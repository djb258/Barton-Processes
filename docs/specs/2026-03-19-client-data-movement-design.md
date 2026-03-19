# Client Data Movement Processes — Design Spec

## Governing Engine

| Field | Value |
|-------|-------|
| Sovereign | imo-creator-v2 |
| Doctrine | Tier 0 (TIER0_DOCTRINE.md) |
| Blueprint Repo | djb258/client (client-subhive) |
| Execution Repo | djb258/Barton-Processes |
| Process Range | 800-series |
| Runtime | Cloudflare Workers |

---

## Architecture

### Data Hierarchy

```
CL (Company Lifecycle — sovereign ID)
├── Outreach ID (sub-hub)
├── Sales ID (sub-hub)
└── Client ID (sub-hub) ← THIS SPEC
    ├── S1 Hub — client identity (SPINE)
    ├── S2 Plan — benefits, rates, renewal quotes
    ├── S3 Employee — enrollment, person, elections
    ├── S4 Vendor — vendor identity, ID translation, invoices
    └── S5 Service — service tickets
```

The CL sovereign ID is the spine that threads the entire company lifecycle. A company may arrive through outreach → sales → conversion, or directly via manual assignment. Either way, the input to the client domain is always **one CL sovereign ID**.

### Infrastructure Layers

| Layer | Technology | Role |
|-------|-----------|------|
| Working | CF D1 | All active operations — staging, validation, canonical working copy |
| Config | CF KV | Vendor blueprints, schedule config, feature flags |
| Compute | CF Workers | All processing logic |
| Vault | Neon PostgreSQL (via Hyperdrive) | Long-term canonical storage — promote when certified |
| Secrets | Doppler | All runtime configuration |

**CF does the work. Neon is the vault.**

D1 mirrors the `clnt` schema structure for working operations. Same 16 tables, same 5 spokes. D1 is SQLite-based — types simplify (UUID → TEXT, TIMESTAMPTZ → TEXT, NUMERIC → REAL). The column registry in the client blueprint remains the source of truth for structure.

---

## Process Definitions

### 800 — Client Mint

| Field | Value |
|-------|-------|
| ID | PROC-CLIENT-MINT |
| Trigger | Manual — human provides CL sovereign ID |
| Runtime | CF Worker |
| Frequency | As needed |

**Two-Question Intake:**
- What triggers this? Dave (or operator) provides a CL sovereign ID.
- How do we get it? Read company identity from Neon vault (CL schema).

**IMO:**

| Layer | What Happens |
|-------|-------------|
| **Ingress** | Receive CL sovereign ID. Read company identity from Neon (legal_name, fein, domicile_state, effective_date, source). No logic — dumb read. |
| **Middle** | Mint new client_id (UUID). Populate `clnt.client` in D1 from sovereign data. Link back to CL sovereign ID. Set status='active', version=1. Write to D1 working tables. |
| **Egress** | Promote certified client record to Neon vault (`clnt.client`). Return new client_id. |

**Error Handling:** Failures write to `clnt.client_error` in D1. Sovereign ID not found → error, halt. Duplicate client for same sovereign → error, halt.

---

### 810 — Client Data Intake

| Field | Value |
|-------|-------|
| ID | PROC-CLIENT-DATA-INTAKE |
| Trigger | Manual CSV upload or API POST |
| Runtime | CF Worker |
| Frequency | Annual (plans/renewal), ongoing (enrollment changes) |

**Two-Question Intake:**
- What triggers this? Operator uploads CSV or external system POSTs data.
- How do we get it? HTTP endpoint on CF Worker accepts payload.

**IMO:**

| Layer | What Happens |
|-------|-------------|
| **Ingress** | Receive CSV/API payload. Zod schema validation at boundary — reject malformed data immediately. Payload includes spoke identifier (S2-plan, S3-employee, S4-vendor, S5-service). No logic — validation only. |
| **Middle** | Write to D1 staging tables (enrollment_intake batch header + intake_record per row). Validate business rules against spoke-specific constraints. Promote validated records to D1 canonical working tables. Route by spoke: S2 → plan, plan_quote. S3 → person, election. S4 → vendor, external_identity_map, invoice. S5 → service_request. Errors to spoke-specific *_error tables. |
| **Egress** | Promote certified canonical records from D1 to Neon vault. Return intake summary (records processed, errors, promotions). |

**Spoke Routing:**

| Spoke | Staging Tables | Canonical Tables | Error Table |
|-------|---------------|-----------------|-------------|
| S2 Plan | intake_record | plan, plan_quote | plan_error |
| S3 Employee | enrollment_intake, intake_record | person, election | employee_error |
| S4 Vendor | intake_record | vendor, external_identity_map, invoice | vendor_error |
| S5 Service | intake_record | service_request | service_error |

**Pattern:** Same worker handles initial load and incremental updates. The payload tells it which spoke and whether it's a full load or delta. Idempotent — re-uploading the same data produces the same result.

**Error Handling:** Per-spoke error tables in D1. Errors are insert-only, no updates, no deletes. Errors feed the Circle — operator reviews, corrects source data, re-uploads.

---

### 820 — Vendor Export

| Field | Value |
|-------|-------|
| ID | PROC-VENDOR-EXPORT |
| Trigger | Cron scheduled |
| Runtime | CF Worker |
| Frequency | Daily (TPA/PBM), weekly (carriers) |

**Two-Question Intake:**
- What triggers this? Cron schedule fires.
- How do we get it? Read D1 canonical working tables.

**IMO:**

| Layer | What Happens |
|-------|-------------|
| **Ingress** | Read canonical working tables from D1 (person, election, plan, vendor, external_identity_map). Filter by client_id and export schedule. No logic — dumb read. |
| **Middle** | Apply vendor blueprint mapping (KV: guardian_life.mapping.json, mutual_of_omaha.mapping.json, etc.). Transform internal UUIDs to external IDs via external_identity_map. Generate vendor-formatted output. |
| **Egress** | Ship export file to destination. Log export record. Return export summary. |

**Schedule Config (KV):**

| Vendor Type | Frequency | Blueprint |
|-------------|-----------|-----------|
| TPA | Daily | Vendor-specific mapping |
| PBM | Daily | Vendor-specific mapping |
| Carriers (Guardian, MoO, etc.) | Weekly | guardian_life.mapping.json, mutual_of_omaha.mapping.json |

**Error Handling:** Export failures write to `vendor_error` in D1. Malformed mapping → error, halt. Missing external ID mapping → error, skip record, continue.

---

## Data Flow

```
                    CL Sovereign (Neon vault)
                           |
                    [800 Client Mint]
                           |
                           v
                    D1: clnt.client (working)
                           |
              +------------+------------+
              |            |            |
       [810 Intake]   [810 Intake]  [810 Intake]
       CSV/API         CSV/API       CSV/API
              |            |            |
              v            v            v
        D1 staging    D1 staging    D1 staging
              |            |            |
              v            v            v
     D1 canonical   D1 canonical  D1 canonical
     (person,       (plan,        (vendor,
      election)      plan_quote)   invoice)
              |            |            |
              +------------+------------+
                           |
                    [promote to vault]
                           |
                           v
                    Neon: clnt.* (vault)

              +------------+------------+
              |            |            |
       [820 Export]  [820 Export]  [820 Export]
       Daily TPA     Weekly GDL    Weekly MoO
              |            |            |
              v            v            v
         Export files to vendors
```

---

## CQRS Compliance

| Constant | Verified |
|----------|----------|
| One CANONICAL + one ERROR per sub-hub | Yes — 5 spokes, 5 canonical, 5 error tables |
| Data enters from leaves only | Yes — staging tables (D1) are the entry point |
| CANONICAL is read-only from consumer perspective | Yes — 820 reads, never writes to canonical |
| INSERT-only at leaf level | Yes — intake_record is immutable after insert |
| Promotion path IS the gate mechanism | Yes — staging → validate → canonical → vault |

---

## Tier 0 Gate Validation

| Gate | Validator | Result |
|------|-----------|--------|
| Gate 1 — Tier 0 | IMO: each process has clear I/M/O with all logic in Middle | PASS |
| Gate 1 — Tier 0 | CTB: processes in factory/ silo, client sub-hub off CL sovereign | PASS |
| Gate 1 — Tier 0 | Circle: errors feed back to operator, corrections re-enter at leaf | PASS |
| Gate 2 — CTB Position | factory/800-*, factory/810-*, factory/820-* in Barton-Processes | PASS |
| Gate 3 — CQRS Write Path | Leaves (staging) → promote → canonical → vault. No direct writes. | PASS |

---

## Blueprint Source Reference

All structural definitions come from the client blueprint repo (djb258/client):

| Artifact | Path | Purpose |
|----------|------|---------|
| Column Registry | src/data/db/registry/clnt_column_registry.yml | SINGLE SOURCE OF TRUTH for schema |
| OSAM | doctrine/OSAM.md | Query routing contract |
| PRD | docs/prd/PRD.md | Hub definition + transformation statement |
| Vendor Blueprints | db/vendor_blueprints/*.mapping.json | Vendor field mappings |
| Domain Spec | doctrine/REPO_DOMAIN_SPEC.md | Domain bindings + lane definitions |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-19 |
| Status | DRAFT — awaiting human approval |
| Authority | imo-creator-v2 (Sovereign) |
| Governing Engine | law/doctrine/TIER0_DOCTRINE.md |
| CTB Position | docs/specs/ (leaf — documentation silo) |

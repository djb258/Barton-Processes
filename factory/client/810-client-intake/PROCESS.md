# PROCESS: CLIENT DATA INTAKE
## Receives client benefits data via HTTP, validates with Zod, stages to immutable audit trail, promotes to canonical tables, and vaults to Neon
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-810 |
| Name | Client Data Intake |
| Business Silo | svg-agency |
| Sub-Hub | client |
| CTB Position | factory/client/810-client-intake |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed |
| BAR Reference | BAR-38, BAR-178 |
| Deployed URL | https://client-intake-810.svg-outreach.workers.dev |
| Cron | none (HTTP-triggered) |
| Runtime | CF Worker |

---

## 2. WHY THIS EXISTS

Without this process, client benefits data has no way into the system. Plans, employees, elections, vendors, invoices, and service requests all enter through this single gate. Every record is validated at the boundary, staged immutably for audit, promoted to canonical working tables, and vaulted to Neon for permanent storage.

Process 820 (Vendor Export) and Process 830 (Client Portal) both starve without canonical data in D1. No intake, no downstream operations.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** — HTTP POST to /intake from operator upload or external system
2. **"How do we get it?"** — JSON payload: `{ client_id, table, data[] }`

### Input
- JSON payload via `POST /intake`
- Required fields: `client_id` (must exist in D1 client table via Process 800), `table` (spoke routing key), `data[]` (array of records)
- Table field routes to spoke: plan, plan_quote, person, election, vendor, external_identity_map, invoice, service_request

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | HTTP POST body | Parse JSON, verify client_id exists in D1 `client` table | Verified payload or 404 | D1 SELECT |
| 2 | `{ table, data[] }` | Zod schema validation per table type — rejects malformed data at boundary | `{ valid[], errors[] }` | Zod (validate.ts) |
| 3 | valid records | INSERT into `intake_record` (immutable) + create `enrollment_intake` batch header | batch_id, staged count | D1 INSERT (stage.ts) |
| 4 | intake_record rows for batch | Parse raw_payload, INSERT into canonical table (plan, person, vendor, etc.), mark intake_record.promoted_at | promoted count, errors | D1 INSERT + UPDATE (promote.ts) |
| 5 | Promotion errors (if any) | Write to spoke-specific error table (plan_error, employee_error, vendor_error, service_error) | Error record with source_id tracing back to intake_record | D1 INSERT |

All five steps execute in a single HTTP request — Validate, Stage, Promote in one pass.

### Output
- 201: `{ validated, validation_errors, batch_id, promoted, promote_errors }`
- 422: All records failed validation (zero promoted)
- Canonical tables populated in D1 with `vaulted_at = NULL` (pending vault promotion)
- intake_record contains immutable audit trail of every record received

### Circle (Bedrock S5)
Vault promotion (`POST /vault`) pushes certified D1 records to Neon `clnt.*` schema, stamps `vaulted_at` on D1 rows. Error table review via `GET /errors/:client_id` closes the feedback loop — unresolved errors block downstream processes.

---

## 4. WHAT IT GRABS OFF THE WALL

### Blueprint Reference

| Field | Value |
|-------|-------|
| Blueprint | client |
| OSAM Section | doctrine/OSAM.md (v3.0.0 LOCKED) |
| Snap-On Toolbox | law/SNAP_ON_TOOLBOX.yaml |

### Snap-On Toolbox Tools

| Sub-Hub # | Tool | What It Does Here |
|-----------|------|-------------------|
| 11-structured-data | Cloudflare D1 | All 16 tables: canonical, error, staging, reference |
| 06-api-layer | Hono | REST endpoints: /intake, /vault, /status, /errors/:client_id, /health |

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| client-intake-810 | D1 | (not created — TODO) | READ/WRITE | All 16 tables: 5 spoke canonical + 5 error + intake_record + enrollment_intake + client |
| Neon PostgreSQL | NEON_URL (secret) | — | WRITE | Vault target — `clnt.*` schema (plan, person, election, vendor, invoice, etc.) |

### Tools & Integrations (Snap-On Toolbox references — see law/SNAP_ON_TOOLBOX.yaml for vendor details)

| Item | Snap-On Sub-Hub | Cost Tier | Credentials | What It Does |
|------|----------------|-----------|-------------|-------------|
| Cloudflare D1 | 11-structured-data | Free | D1 binding | All 16 working tables |
| Hono (CF Worker) | 06-api-layer | Free | none | REST endpoint routing |
| Zod | (validation library) | Free | none | Schema validation at boundary — 8 schemas for 8 table types |
| @neondatabase/serverless | (vault vendor) | Free | NEON_URL | Vault promotion — D1 canonical rows to Neon clnt.* |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| NEON_URL | imo-creator | dev | vault.ts — Neon serverless driver for vault promotion |

**Tool Priority:** All free. D1 for working data, Neon for vault only. No external APIs, no proxy, no per-call cost.

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `client` | Client identity — must exist before intake | `client_id` |
| `intake_record` | Immutable audit trail — raw_payload, promoted_at | `enrollment_intake_id`, `client_id` |
| `enrollment_intake` | Batch header — status tracking | `enrollment_intake_id` |
| All canonical tables (plan, person, etc.) | Unvaulted records for vault promotion | `vaulted_at IS NULL` |
| All error tables | Open errors per client per spoke | `client_id`, `status = 'open'` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `enrollment_intake` | Batch header (pending → staged → completed) | Step 3, Step 4 |
| `intake_record` | Immutable raw payload + promoted_at timestamp | Step 3 (INSERT), Step 4 (UPDATE promoted_at) |
| `plan`, `plan_quote` | Canonical plan records | Step 4 (S2 promote) |
| `person`, `election` | Canonical employee records | Step 4 (S3 promote) |
| `vendor`, `external_identity_map`, `invoice` | Canonical vendor records | Step 4 (S4 promote) |
| `service_request` | Canonical service records | Step 4 (S5 promote) |
| `plan_error`, `employee_error`, `vendor_error`, `service_error`, `client_error` | Promotion failures with error_code + source traceability | Step 5 |
| Neon `clnt.*` tables | Vault copies of canonical records | POST /vault |

### Join Chain

```
client.client_id
  → enrollment_intake.client_id  (batch headers)
    → intake_record.enrollment_intake_id  (immutable audit trail)
  → plan.client_id  (S2 canonical)
    → plan_quote.client_id  (S2 quotes)
  → person.client_id  (S3 canonical)
    → election.person_id → person.person_id  (S3 person↔election)
    → election.plan_id → plan.plan_id  (S3 election↔plan)
  → vendor.client_id  (S4 canonical)
    → external_identity_map.vendor_id → vendor.vendor_id  (S4 identity mapping)
    → invoice.vendor_id → vendor.vendor_id  (S4 billing)
  → service_request.client_id  (S5 canonical)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Accept intake without client_id in D1 client table | Client must exist via Process 800 first |
| UPDATE or DELETE intake_record | INSERT-only — immutable audit trail |
| Write to Neon outside /vault endpoint | Vault promotion is the only Neon write path |
| Skip Zod validation | Rejected data never enters staging |
| Direct INSERT to canonical tables bypassing intake_record | Every record must have an audit trail |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| What records are pending promotion? | `intake_record` | `promoted_at IS NULL` |
| What batches are in progress? | `enrollment_intake` | `status` |
| How many open errors for a client? | `*_error` tables | `client_id + status = 'open'` |
| What records haven't been vaulted? | canonical tables | `vaulted_at IS NULL` |
| What plans does a client have? | `plan` | `client_id` |
| Who is enrolled in a plan? | `election` | `plan_id` + JOIN `person` |

---

## 6. CONSTANTS & VARIABLES (Bedrock S2)

### Constants (structure — never changes)
- Single-pass pipeline: Validate → Stage → Promote (one HTTP request)
- intake_record is INSERT-only, immutable audit trail
- Zod validates at boundary — rejected data never enters staging
- 5 spokes: S1 Hub (client), S2 Plan, S3 Employee, S4 Vendor, S5 Service
- 8 table types route through `table` field in payload
- Each spoke has CANONICAL + ERROR table pair (CQRS)
- All canonical tables have `vaulted_at` for vault promotion tracking
- client_id is the universal join key across all tables
- Vault writes to Neon `clnt.*` schema with ON CONFLICT DO NOTHING
- Error tables trace back to source via `source_id` → `intake_record_id`

### Variables (fill — changes every run)
- Which client_id is submitting data
- Which table type the payload targets
- Number of records in the data[] array
- Validation pass/fail ratio per batch
- Promotion error count
- Number of unvaulted records awaiting vault promotion

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| client_id not found in D1 client table | REJECT 404 — client must exist via Process 800 |
| table field not in SPOKE_SCHEMAS map | REJECT 422 — unknown table type, all records fail validation |
| 100% validation failure on a batch | RETURN 422 — nothing staged, nothing promoted |
| D1 database_id not configured | HALT — cannot deploy, `wrangler d1 create` required |
| NEON_URL secret not set | HALT — vault promotion will fail |
| No auth on endpoints | BUILD BLOCKER — must add auth before OPERATE |
| Promotion errors exceed 50% of batch | LOG WARNING — investigate data quality |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 800 (Client Mint) | Client must exist in D1 `client` table | PENDING |
| D1 database creation | `wrangler d1 create client-intake-810` — database_id in wrangler.toml | PENDING |
| NEON_URL secret | Doppler → wrangler secret put | PENDING |
| Auth mechanism | Bearer token, API key, or CF Access — not yet implemented | PENDING |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 820 (Vendor Export) | Canonical vendor, invoice, external_identity_map records in D1 |
| Process 830 (Client Portal) | Canonical plan, person, election records in D1 |

---

## 9. SMOKE TEST

```
1. GET /health → expected: { process: 'PROC-CLIENT-DATA-INTAKE', number: 810, status: 'ok' }
2. POST /intake { client_id: '<valid>', table: 'plan', data: [{ benefit_type: 'medical' }] } → expected: 201, validated=1, promoted=1
3. POST /intake { client_id: '<invalid>', table: 'plan', data: [{}] } → expected: 404
4. POST /intake { client_id: '<valid>', table: 'plan', data: [{}] } → expected: 422 (benefit_type required)
5. GET /status → expected: intake_records.staged=0 (all promoted), intake_records.promoted>0
6. GET /errors/<client_id> → expected: { open_errors: { client_error: 0, plan_error: 0, ... } }
7. POST /vault → expected: { tables: { plan: 1, ... }, errors: 0 }
8. SELECT COUNT(*) FROM intake_record → expected: >0 (immutable, never deleted)
9. SELECT COUNT(*) FROM plan WHERE vaulted_at IS NOT NULL → expected: matches vault count
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** Do all 16 D1 tables exist? Does the client record exist?
2. **Flow:** Does data flow from HTTP → Zod → intake_record → canonical table → Neon?
3. **Change:** Did Zod reject invalid data? Did promotion write correct columns? Did vault stamp vaulted_at?

If any fails → that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock S6).

---

## 10. ANALYTICS

_What gets measured. All values BASELINE until first production run._

### Metrics

| Metric | Type | Baseline | First Run | Notes |
|--------|------|----------|-----------|-------|
| Intake batches processed | count | BASELINE | — | Total enrollment_intake batch headers created |
| Records validated | count | BASELINE | — | Total records passing Zod validation |
| Validation rejection rate | % | BASELINE | — | Failed records / total records submitted |
| Records promoted | count | BASELINE | — | Records successfully written to canonical tables |
| Records vaulted | count | BASELINE | — | Records promoted to Neon clnt.* via POST /vault |
| Per-spoke counts (plan) | count | BASELINE | — | Records promoted to plan table |
| Per-spoke counts (person) | count | BASELINE | — | Records promoted to person table |
| Per-spoke counts (election) | count | BASELINE | — | Records promoted to election table |
| Per-spoke counts (vendor) | count | BASELINE | — | Records promoted to vendor table |
| Per-spoke counts (service) | count | BASELINE | — | Records promoted to service_request table |

### Tool Scorecard

| Tool | Expected | Actual | Status |
|------|----------|--------|--------|
| D1 (client-intake-810) | Available | BASELINE | — |
| Neon (clnt.* vault) | Available | BASELINE | — |
| Zod validation | Passing | BASELINE | — |
| Hono endpoints | Responding | BASELINE | — |

### Sigma Tracking

| Run Date | Metric | Value | Sigma Direction | Notes |
|----------|--------|-------|----------------|-------|
| — | — | — | — | _No runs yet_ |

### ORBT Gate Rule

- **Sigma tightening** = real constant. Lock it.
- **Sigma flat** = phantom constant. Investigate.
- **Sigma expanding** = broken prior constant. Back-propagate and fix.
- **Strike 3 on same metric** = Troubleshoot/Train, not another repair.

---

## 11. LOGBOOK

_No entries yet. Process is in BUILD state._

---

## 12. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | D1 database_id empty in wrangler.toml | Not yet created | Run `wrangler d1 create client-intake-810` and update wrangler.toml | 0 |
| 2 | 2026-03-29 | No auth on any endpoint | BUILD state — not yet implemented | Add Bearer token or CF Access before OPERATE | 0 |

---

## 13. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-19 | Initial scaffold — index.ts, validate.ts, stage.ts, promote.ts, vault.ts, D1 migration | none |
| 2026-03-29 | PROCESS.md written from template v2.0.0 | none |

---

## ENDPOINTS

| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/health` | GET | Health check — process ID, number, status |
| `/status` | GET | Summary — staged vs promoted intake_records, batch statuses |
| `/intake` | POST | `{ client_id, table, data[] }` → Validate → Stage → Promote (single pass) |
| `/vault` | POST | Push all unvaulted canonical records to Neon `clnt.*` |
| `/errors/:client_id` | GET | Open error counts per spoke error table |

---

## SPOKE ROUTING

| Table Value | Spoke | Canonical Table | Error Table |
|-------------|-------|----------------|-------------|
| `plan` | S2 Plan | `plan` | `plan_error` |
| `plan_quote` | S2 Plan | `plan_quote` | `plan_error` |
| `person` | S3 Employee | `person` | `employee_error` |
| `election` | S3 Employee | `election` | `employee_error` |
| `vendor` | S4 Vendor | `vendor` | `vendor_error` |
| `external_identity_map` | S4 Vendor | `external_identity_map` | `vendor_error` |
| `invoice` | S4 Vendor | `invoice` | `vendor_error` |
| `service_request` | S5 Service | `service_request` | `service_error` |

---

## D1 TABLE INVENTORY (16 tables)

| # | Table | Spoke | Type | PK |
|---|-------|-------|------|----|
| 1 | `client` | S1 Hub | Reference | `client_id` |
| 2 | `client_error` | S1 Hub | Error | `client_error_id` |
| 3 | `plan` | S2 Plan | Canonical | `plan_id` |
| 4 | `plan_quote` | S2 Plan | Canonical | `plan_quote_id` |
| 5 | `plan_error` | S2 Plan | Error | `plan_error_id` |
| 6 | `person` | S3 Employee | Canonical | `person_id` |
| 7 | `election` | S3 Employee | Canonical | `election_id` |
| 8 | `employee_error` | S3 Employee | Error | `employee_error_id` |
| 9 | `enrollment_intake` | S3 Employee | Staging | `enrollment_intake_id` |
| 10 | `intake_record` | S3 Employee | Staging (immutable) | `intake_record_id` |
| 11 | `vendor` | S4 Vendor | Canonical | `vendor_id` |
| 12 | `external_identity_map` | S4 Vendor | Canonical | `external_identity_id` |
| 13 | `invoice` | S4 Vendor | Canonical | `invoice_id` |
| 14 | `vendor_error` | S4 Vendor | Error | `vendor_error_id` |
| 15 | `service_request` | S5 Service | Canonical | `service_request_id` |
| 16 | `service_error` | S5 Service | Error | `service_error_id` |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.1.0 |
| Template Version | 3.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | — |
| Data Flow | — |

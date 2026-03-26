# CLAUDE.md — Process 810: Client Data Intake

## Governing Doctrine

**Before any work on this process, read and follow:**

1. `law/doctrine/FOUNDATIONAL_BEDROCK.md` — The engine (Three Primitives, C\&V, IMO, CTB, Circle, Troubleshooting Loop, Tier 0, Aviation Model)
2. `bedrock/math-01-engine.md` — P(x;θ) decision equation (FROZEN)
3. `bedrock/math-02-adapter-template.md` — Domain adapter interface

**Pre-flight (every session):**
- Two-Question Intake: "What triggers this?" and "How do we get it?"
- C\&V Test: Can you name it? Format it? → constant. The value filling it → variable.
- Four-Element Validation: IMO + CTB + Circle simultaneously
- Three Primitives: Thing (exists?), Flow (reaches?), Change (transforms correctly?)
- Determinism first. LLM is tail arbitration only.
- If something broke → Troubleshooting Loop (Bedrock §6). Do not patch. Do not guess.

---


## What This Process Does

Receives client benefits data (plans, employees, elections, vendors, invoices, service requests) via HTTP endpoint, validates with Zod schemas at the boundary, stages to immutable intake records, promotes to canonical D1 tables, and vaults certified records to Neon. One worker handles all 5 spokes via payload routing. This is the primary data ingestion point for the entire client management system.

## How It Works

Single-pass pipeline: Validate → Stage → Promote → Vault.

1. **Receive payload** via POST `/intake` — `{ client_id, table, data[] }`.
2. **Verify client exists** in D1 (must be minted by 800 first).
3. **Validate** every record against Zod schema for the target table. Rejected records never enter staging.
4. **Stage** valid records — create `enrollment_intake` batch header, write each record to `intake_record` (INSERT-only, immutable). Raw payload preserved as JSON.
5. **Promote** — move validated data from intake_record to canonical spoke tables (plan, person, election, vendor, etc.).
6. **Vault** (separate step) — POST `/vault` pushes all unvaulted canonical records to Neon.

## API Endpoints

| Method | Path | What |
|--------|------|------|
| GET | `/health` | Health check |
| GET | `/status` | Intake summary (staged vs promoted counts, batch statuses) |
| POST | `/intake` | `{ client_id, table, data[] }` — validate, stage, promote |
| POST | `/vault` | Push unvaulted canonical records to Neon |
| GET | `/errors/:client_id` | Open error counts per spoke error table |

## Spoke Routing

The `table` field in the intake payload determines which spoke processes the data:

| Spoke | Tables | What |
|-------|--------|------|
| S2 Plan | `plan`, `plan_quote` | Benefits plan definitions, carrier quotes |
| S3 Employee | `person`, `election`, `enrollment_intake`, `intake_record` | Employee identity, coverage elections |
| S4 Vendor | `vendor`, `external_identity_map`, `invoice` | Vendor records, ID translations, billing |
| S5 Service | `service_request` | Support tickets |

## Validation Schemas (Zod)

Each spoke has strict Zod schemas enforced at the boundary:

- **plan:** benefit_type (required), carrier_id, effective_date, rates (ee/es/ec/fam + employer variants)
- **plan_quote:** benefit_type + carrier_id (required), effective_year, rates, status enum
- **person:** first_name + last_name (required), ssn_hash, status
- **election:** person_id + plan_id (UUID required), coverage_tier (EE/ES/EC/FAM), effective_date
- **vendor:** vendor_name (required), vendor_type
- **external_identity_map:** entity_type (person/plan), internal_id + vendor_id (UUID), external_id_value
- **invoice:** vendor_id (UUID), invoice_number, amount, invoice_date, status enum
- **service_request:** category (required), status

## Databases

**D1 workspace:** `client-intake-810` (16 tables across 5 spokes)

| Spoke | Canonical Table | Error Table |
|-------|----------------|-------------|
| S1 Hub | `client` (read ref from 800) | `client_error` |
| S2 Plan | `plan`, `plan_quote` | `plan_error` |
| S3 Employee | `person`, `election`, `enrollment_intake`, `intake_record` | `employee_error` |
| S4 Vendor | `vendor`, `external_identity_map`, `invoice` | `vendor_error` |
| S5 Service | `service_request` | `service_error` |

All canonical tables have `vaulted_at` column for vault promotion tracking.
`intake_record` is INSERT-only — immutable audit trail of raw payloads.

**Neon vault:** Destination for certified records (via `/vault` endpoint).

## Key Joins

- Client verification: `client.client_id` = intake payload client_id
- Election links: `election.person_id` → `person.person_id`, `election.plan_id` → `plan.plan_id`
- Vendor identity: `external_identity_map.internal_id` → person_id or plan_id, `external_identity_map.vendor_id` → `vendor.vendor_id`
- Invoice tracking: `invoice.vendor_id` → `vendor.vendor_id`
- Intake audit: `intake_record.enrollment_intake_id` → `enrollment_intake.enrollment_intake_id`

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | 800 Client Mint | Client must exist in D1 before intake |
| Downstream | 820 Vendor Export | Reads canonical tables for export generation |
| Downstream | 830 Client Portal | Reads canonical tables for portal rendering |

## Worker Config

- **Name:** `client-intake-810`
- **URL:** client-intake-810.svg-outreach.workers.dev
- **Trigger:** HTTP POST (manual or API integration)
- **D1:** `client-intake-810`
- **Secrets:** `NEON_URL` (via wrangler secret)
- **Secrets provider:** Doppler

## Known Issues

| Issue | Resolution |
|-------|------------|
| D1 database_id not set in wrangler.toml | Run `wrangler d1 create client-intake-810` and update |
| promote.ts and vault.ts exist but promotion logic may be incomplete | Verify promote flow writes to all canonical spoke tables |
| No authentication on endpoints | Needs CF Access or bearer token gate before production |
| Shared D1 with 830 Client Portal | 830 wrangler.toml points to client-intake-810 D1 — slug column added via migration |

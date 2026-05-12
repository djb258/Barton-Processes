# DOCTRINE - Process 810 Client Data Intake
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-810-01 | All incoming data must be validated by Zod at the HTTP boundary before any write operation. | heir.yaml acceptance_criteria[0]; PROCESS.md §6 Constants | §8 stop — skip Zod → REJECT all |
| D-810-02 | Rejected data (Zod validation failures) must never enter staging tables or canonical tables. | heir.yaml acceptance_criteria[1]; PROCESS.md §5 Forbidden Paths | §8 stop — failed records stay in validation_errors only |
| D-810-03 | The intake_record table is INSERT-only and immutable; no UPDATE or DELETE is permitted except stamping the promoted_at timestamp. | heir.yaml acceptance_criteria[2]; PROCESS.md §6 Constants; CLAUDE.md | §8 stop — any DELETE/UPDATE attempt halts |
| D-810-04 | Promotion must validate business rules (client exists, schema conforms) before writing to canonical spoke tables. | heir.yaml acceptance_criteria[3]; PROCESS.md §3 IMO Middle Step 4 | §8 stop — canonical write without prior validation is forbidden |
| D-810-05 | All promotion failures must be written to the spoke-specific error table with error_code and source_id tracing back to intake_record_id. | heir.yaml acceptance_criteria[4]; PROCESS.md §5 WRITE Access | §9b gauge — open error count per spoke must be queryable |
| D-810-06 | The same worker must handle both initial load and incremental update operations via spoke routing on the `spoke` field (discriminated union: contact/employee/vendor/compliance/interaction). | PROCESS-UT.md v3.0.0 §4 IMO; src/validate.ts | pre-flight — separate workers per spoke is a violation; `table` field routing is deprecated as of 2026-05-12 |
| D-810-07 | ~~DEPRECATED 2026-05-12~~ — Neon vault path removed. Single-tier D1 model adopted. POST /vault returns 410 Gone. No Neon writes at any layer of bp.810. | PROCESS-UT.md v3.0.0 §4 IMO; src/vault.ts no-op stub | D-810-07 is retired; any attempt to resurrect /vault → Neon write is a doctrine violation |
| D-810-08 | A client record must exist in the `clients` table (minted by bp.800) before any intake is accepted; intake without a valid client_id returns 404 immediately. bp.810 never writes to `clients`. | PROCESS-UT.md v3.0.0 §6 Constants; src/index.ts pre-exist gate | §8 stop — 404 on client_id lookup |
| D-810-09 | ~~DEPRECATED 2026-05-12~~ — D1 binding is resolved. wrangler.toml binds to `svg-d1-client` (id: `5443887b-ba8a-4da5-9f54-6a9c2cfb1244`). This was a BUILD BLOCKER; blocker cleared on 2026-05-12 deployment. | PROCESS-UT.md v3.0.0 §9b; wrangler.toml | No longer a gate — worker is deployed and OPERATE |
| D-810-10 | Auth is deferred per sovereign override (2026-05-12). Worker is OPERATE without endpoint auth; access is restricted at the network/binding layer (service-to-service only). Auth implementation is a REPAIR task, not a BUILD BLOCKER for OPERATE state. | PROCESS-UT.md v3.0.0 §7; Dave Barton override 2026-05-12 | §8 advisory — open REPAIR item; does not block current OPERATE state |

## Cross-references
- UT §7 Constants & Variables references rules D-810-01 through D-810-08 by ID
- UT §8 Stop Conditions cites D-810-08 (client not found), D-810-01/02 (Zod violations)
- §9b Live Verification gauges measure D-810-01 (validation pass rate), D-810-03 (staging row count), D-810-05 (open error counts per spoke)
- D-810-07 (Neon vault) and D-810-09 (empty database_id) are DEPRECATED — removed from active gate list; retained for audit trail only
- D-810-10 (auth) is REPAIR-deferred per sovereign override 2026-05-12

## Flat Spoke Model Adoption — 2026-05-12
- Normalized schema (intake_record, enrollment_intake, plan, plan_quote, person, election, vendor, external_identity_map, invoice, service_request) **permanently discarded**
- Neon vault path permanently removed; `/vault` → 410 Gone
- `table` field routing replaced by `spoke` discriminated union (contact/employee/vendor/compliance/interaction)
- Worker deployed OPERATE: https://client-intake-810.svg-outreach.workers.dev (Version: af52f605-3261-4b4e-a95e-ccf564926876)
- Canonical D1: `svg-d1-client` (5443887b-ba8a-4da5-9f54-6a9c2cfb1244)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-29 |
| Last Modified | 2026-05-12 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |
| Rule Count | 10 (D-810-01 through D-810-10; D-810-07 and D-810-09 deprecated 2026-05-12) |

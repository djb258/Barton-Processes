# DOCTRINE - Process 810 Client Data Intake
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-810-01 | All incoming data must be validated by Zod at the HTTP boundary before any write operation. | heir.yaml acceptance_criteria[0]; PROCESS.md §6 Constants | §8 stop — skip Zod → REJECT all |
| D-810-02 | Rejected data (Zod validation failures) must never enter staging tables or canonical tables. | heir.yaml acceptance_criteria[1]; PROCESS.md §5 Forbidden Paths | §8 stop — failed records stay in validation_errors only |
| D-810-03 | The intake_record table is INSERT-only and immutable; no UPDATE or DELETE is permitted except stamping the promoted_at timestamp. | heir.yaml acceptance_criteria[2]; PROCESS.md §6 Constants; CLAUDE.md | §8 stop — any DELETE/UPDATE attempt halts |
| D-810-04 | Promotion must validate business rules (client exists, schema conforms) before writing to canonical spoke tables. | heir.yaml acceptance_criteria[3]; PROCESS.md §3 IMO Middle Step 4 | §8 stop — canonical write without prior validation is forbidden |
| D-810-05 | All promotion failures must be written to the spoke-specific error table with error_code and source_id tracing back to intake_record_id. | heir.yaml acceptance_criteria[4]; PROCESS.md §5 WRITE Access | §9b gauge — open error count per spoke must be queryable |
| D-810-06 | The same worker must handle both initial load and incremental update operations via spoke routing on the table field. | heir.yaml acceptance_criteria[5]; CLAUDE.md spoke routing | pre-flight — separate workers for load vs update is a violation |
| D-810-07 | Vault promotion must push certified canonical records to Neon clnt.* schema exclusively via POST /vault; no other code path may write to Neon. | heir.yaml acceptance_criteria[6]; PROCESS.md §5 Forbidden Paths | §8 stop — any Neon write outside /vault endpoint halts |
| D-810-08 | A client record must exist in the D1 client table (minted by Process 800) before any intake is accepted; intake without a valid client_id returns 404 immediately. | PROCESS.md §7 Stop Conditions; CLAUDE.md Known Issues | §8 stop — 404 on client_id lookup |
| D-810-09 | The D1 database_id for client-intake-810 must be populated in wrangler.toml before deployment; deployment with an empty database_id is a BUILD BLOCKER. | PROCESS.md §12 Known Issues FP-810-01; wrangler.toml | pre-flight — deployment gate; cannot move to OPERATE until resolved |
| D-810-10 | Authentication must be implemented on all endpoints before the process transitions from BUILD to OPERATE state; no endpoint may be publicly accessible without auth. | PROCESS.md §7 Stop Conditions; PROCESS.md §12 Known Issues FP-810-02; CLAUDE.md | §8 stop — BUILD BLOCKER; ORBT gate from BUILD → OPERATE blocked |

## Cross-references
- UT §7 Constants & Variables references rules D-810-01 through D-810-08 by ID
- UT §8 Stop Conditions cites D-810-08 (client not found), D-810-09 (database_id empty), D-810-10 (no auth), D-810-01/02 (Zod violations), D-810-07 (Neon write path violation)
- §9b Live Verification gauges measure D-810-01 (validation pass rate), D-810-03 (intake_record count), D-810-05 (open error counts), D-810-07 (vaulted_at stamping)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-29 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |
| Rule Count | 10 (D-810-01 through D-810-10) |

# DOCTRINE — 820-vendor-export

> Process-locked rules for PROC-820. Numbered rules are cited by ID in PROCESS-UT.md §7 and §8.
> Source attribution is required per column. Gate column states enforcement mechanism.
> Rules are monotonically numbered. No gaps.

---

## Locked Rules

| Rule ID | Rule | Source | Gate |
|---------|------|--------|------|
| D-820-01 | Process 820 reads from the bp.810 canonical client tables in `svg-d1-client` (`clients`, `client_contacts`, `client_employees`, `client_vendors`, `client_compliance`, `client_employee_vendor_ids` — flat-spoke model) and never writes to those tables. | `heir.yaml` acceptance_criteria[0]; `PROCESS-UT.md` §5 Forbidden Paths; `src/index.ts` + `src/export.ts` (read-only SELECTs) | §8 stop condition — any write attempt to bp.810 client tables halts export run |
| D-820-02 | Every record's vendor external identifier must resolve via `client_employee_vendor_ids` (`employee_id → vendor_employee_id` where `status='active'`) before inclusion in output; missing mapping logs error code `MISSING_EXTERNAL_ID` to `export_error` and skips that record. (`client_employee_vendor_ids` is the live translation table; the formerly speculative `external_identity_map` name does not exist.) | `heir.yaml` acceptance_criteria[4]; `PROCESS-UT.md` §8; `src/export.ts` idMap build | §9b gauge: MISSING_EXTERNAL_ID error count per run; §8 stop: skip record on miss |
| D-820-03 | Vendor blueprint field mapping is loaded from KV `EGRESS_KV` at key `blueprint:{vendor_id}` for every export run; blueprint is never hardcoded in application code. | `heir.yaml` acceptance_criteria[1]; `src/blueprints.ts` `loadBlueprint()` | §9b gauge: KV GET latency; pre-flight: KV binding must be populated (RP-820-DEPLOY) before OPERATE |
| D-820-04 | Every completed export run must write a row to `export_log` (in `svg-d1-client`) with `record_count`, `status`, and `exported_at` before the run is considered successful. (Also written for `no_data` runs.) | `heir.yaml` acceptance_criteria[3]; `PROCESS-UT.md` §5 Write Access; `src/export.ts` `logExport()` | §9b gauge: export_log row count after run; §8 stop: missing log entry = incomplete run |
| D-820-05 | `BLUEPRINT_NOT_FOUND` halts export for that vendor only; the error is written to `export_error`, and execution continues with the next vendor in the run list. | `PROCESS-UT.md` §8 Stop Conditions; `_archived-fragments/CLAUDE.md` Known Issues; `src/export.ts` (early return on null blueprint) | §8 stop: vendor-scoped halt, not process-global halt; §9b gauge: error table count |
| D-820-06 | TPA and PBM vendors export on the daily cron (`0 5 * * *`); carrier vendors (guardian_life, mutual_of_omaha) export weekly on the day defined by `WEEKLY_DAY` env var (default: 1 = Monday). | `heir.yaml` acceptance_criteria[5]; `wrangler.toml` `[vars]`; `src/index.ts` `scheduled()` | §9b gauge: schedule_log last_run_at per vendor; pre-flight: DAILY_VENDORS + WEEKLY_VENDORS env vars must be set |
| D-820-07 | Process 820 must not run against an empty or partially-populated canonical client D1; bp.810 (Client Intake) must be in ORBT state OPERATE with `clients` / `client_employees` / `client_vendors` populated before 820 is promoted to OPERATE. | `PROCESS-UT.md` §3 Dependencies; `heir.yaml` | §8 stop: missing canonical client tables halts all export runs; pre-flight: verify bp.810 ORBT state |
| D-820-08 | The export pipeline step order is fixed: (1) determine vendors for run type → (2) get active clients from `clients` → (3) load blueprint from `EGRESS_KV` → (4) read `client_employees` LEFT JOIN `client_vendors` → (5) resolve `client_employee_vendor_ids` → (6) apply field_mappings → (7) serialize output (CSV or JSON) → (8) log to `export_log`. Steps may not be reordered or skipped. | `PROCESS-UT.md` §4 IMO Middle table; `src/export.ts` `generateExport()` + `src/index.ts` `scheduled()` | §9b gauge: verify step sequence via export_log.status; §8 stop: blueprint load failure stops step 3 |
| D-820-09 | `VendorBlueprint` schema is fixed at six fields: `vendor_id` (string), `vendor_name` (string), `file_format` ('csv'\|'json'), `delimiter` (string), `field_mappings` (Record<string,string>), `include_header` (boolean). No additional fields may be added without a schema change BAR. | `_archived-fragments/CLAUDE.md` VendorBlueprint interface; `src/blueprints.ts` | pre-flight: schema validation on KV load; external: blueprint schema changes require BAR |
| D-820-10 | Error codes are fixed at two values: `BLUEPRINT_NOT_FOUND` and `MISSING_EXTERNAL_ID`. No other error codes may be used or introduced without a DOCTRINE amendment (new rule + BAR). | `_archived-fragments/CLAUDE.md` Error Codes; `PROCESS-UT.md` §8; `src/export.ts` | §8 stop: unrecognized error code = process violation; external: code changes require rule amendment |
| D-820-11 | The D1 binding `D1` must point to `svg-d1-client` (`database_id 5443887b-ba8a-4da5-9f54-6a9c2cfb1244`) — the single shared client D1 that holds both bp.810 canonical client tables and bp.820 audit tables (`export_log`, `export_error`, `export_schedule`). Binding to any other D1 is a violation. | `wrangler.toml` `[[d1_databases]]`; `repair-bp-820.md` (BAR-377 live inventory); `PROCESS-MAP-810-client-intake.yaml` (canonical D1 declaration) | §8 stop: wrong `D1` binding halts run; pre-flight: verify `database_id` in wrangler.toml before deploy |

---

## Source Index

| Source | Priority | Used For |
|--------|----------|----------|
| `heir.yaml` `acceptance_criteria[]` | 1 (highest) | D-820-01, D-820-02, D-820-03, D-820-04, D-820-06, D-820-07 |
| `PROCESS-UT.md` §4 IMO, §5 Data Schema, §8 Stop Conditions | 5 | D-820-01, D-820-02, D-820-04, D-820-05, D-820-07, D-820-08, D-820-10 |
| `src/index.ts`, `src/export.ts`, `src/blueprints.ts` | code reference | D-820-01, D-820-02, D-820-03, D-820-04, D-820-05, D-820-06, D-820-08, D-820-09, D-820-10 |
| `wrangler.toml` | config reference | D-820-06, D-820-11 |
| `repair-bp-820.md` / `audit-bp-820.md` (BAR-377) | live-inventory reference | D-820-11 (svg-d1-client + EGRESS_KV ids); flat-spoke schema confirmation for D-820-01/02/08 |
| `_archived-fragments/CLAUDE.md` (superseded) | historical reference | D-820-05, D-820-09, D-820-10 |

---

## Document Control

| Field | Value |
|-------|-------|
| Process | 820-vendor-export |
| Process ID | PROC-820 |
| Rule count | 11 (D-820-01 through D-820-11) |
| Created | 2026-04-29 |
| Last Modified | 2026-05-12 |
| UT Version | 2.7.0 |
| Status | REPAIR — flat-spoke aligned; not auditor-certified (RP-820-DEPLOY pending) |
| Amendment | 2026-05-12 (BAR-bp820): rules re-pointed to live flat-spoke schema (`clients`/`client_employees`/`client_vendors`/`client_employee_vendor_ids`); removed speculative `external_identity_map` / `person`/`election`/`plan`; added D-820-11 (canonical D1 binding `svg-d1-client`); source attributions updated (PROCESS.md/CLAUDE.md → archived; PROCESS-UT.md + src/ + BAR-377 docs cited). |

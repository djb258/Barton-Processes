# DOCTRINE — 820-vendor-export

> Process-locked rules for PROC-820. Numbered rules are cited by ID in PROCESS-UT.md §7 and §8.
> Source attribution is required per column. Gate column states enforcement mechanism.
> Rules are monotonically numbered. No gaps.

---

## Locked Rules

| Rule ID | Rule | Source | Gate |
|---------|------|--------|------|
| D-820-01 | Process 820 reads from D1 canonical tables (person, election, plan, vendor, external_identity_map) owned by 810 and never writes to those tables. | `heir.yaml` acceptance_criteria[0]; `PROCESS.md` §OSAM Forbidden Paths | §8 stop condition — any write attempt to 810 tables halts export run |
| D-820-02 | Every record's external identifier must resolve via `external_identity_map` before inclusion in output; missing mapping logs error code `MISSING_EXTERNAL_ID` to `export_error` and skips that record. | `heir.yaml` acceptance_criteria[4]; `PROCESS.md` §Stop Conditions | §9b gauge: MISSING_EXTERNAL_ID error count per run; §8 stop: skip record on miss |
| D-820-03 | Vendor blueprint field mapping is loaded from KV at key `blueprint:{vendor_id}` for every export run; blueprint is never hardcoded in application code. | `heir.yaml` acceptance_criteria[1]; `src/blueprints.ts` `loadBlueprint()` | §9b gauge: KV GET latency; pre-flight: KV binding must be populated before OPERATE |
| D-820-04 | Every completed export run must write a row to `export_log` with `record_count`, `status`, and `exported_at` before the run is considered successful. | `heir.yaml` acceptance_criteria[3]; `PROCESS.md` §OSAM Write Tables | §9b gauge: export_log row count after run; §8 stop: missing log entry = incomplete run |
| D-820-05 | `BLUEPRINT_NOT_FOUND` halts export for that vendor only; the error is written to `export_error`, and execution continues with the next vendor in the run list. | `PROCESS.md` §Stop Conditions; `CLAUDE.md` Known Issues | §8 stop: vendor-scoped halt, not process-global halt; §9b gauge: error table count |
| D-820-06 | TPA and PBM vendors export on the daily cron (`0 5 * * *`); carrier vendors (guardian_life, mutual_of_omaha) export weekly on the day defined by `WEEKLY_DAY` env var (default: 1 = Monday). | `heir.yaml` acceptance_criteria[5]; `CLAUDE.md` Export Schedule; `wrangler.toml` vars | §9b gauge: schedule_log last_run_at per vendor; pre-flight: DAILY_VENDORS + WEEKLY_VENDORS env vars must be set |
| D-820-07 | Process 820 must not run against an empty or partially-populated canonical D1; 810 (Client Intake) must be in ORBT state OPERATE with person, election, and plan tables populated before 820 is promoted to OPERATE. | `PROCESS.md` §Dependencies; `heir.yaml` depends_on | §8 stop: missing 810 canonical tables halts all export runs; pre-flight: verify 810 ORBT state |
| D-820-08 | The export pipeline step order is fixed: (1) determine vendors for run type → (2) get active clients → (3) load blueprint from KV → (4) read person+election+plan JOIN → (5) resolve external_identity_map → (6) apply field_mappings → (7) serialize output (CSV or JSON) → (8) log to export_log. Steps may not be reordered or skipped. | `PROCESS.md` §IMO Middle table; `src/export.ts` `generateExport()` | §9b gauge: verify step sequence via export_log.status; §8 stop: blueprint load failure stops step 3 |
| D-820-09 | `VendorBlueprint` schema is fixed at six fields: `vendor_id` (string), `vendor_name` (string), `file_format` ('csv'\|'json'), `delimiter` (string), `field_mappings` (Record<string,string>), `include_header` (boolean). No additional fields may be added without a schema change BAR. | `CLAUDE.md` VendorBlueprint interface; `src/blueprints.ts` | pre-flight: schema validation on KV load; external: blueprint schema changes require BAR |
| D-820-10 | Error codes are fixed at two values: `BLUEPRINT_NOT_FOUND` and `MISSING_EXTERNAL_ID`. No other error codes may be used or introduced without a DOCTRINE amendment (new rule + BAR). | `CLAUDE.md` Error Codes; `PROCESS.md` §Stop Conditions | §8 stop: unrecognized error code = process violation; external: code changes require rule amendment |

---

## Source Index

| Source | Priority | Used For |
|--------|----------|----------|
| `heir.yaml` `acceptance_criteria[]` | 1 (highest) | D-820-01, D-820-02, D-820-03, D-820-04, D-820-05, D-820-06, D-820-07 |
| `PROCESS.md` §OSAM, §Stop Conditions, §IMO | 5 | D-820-01, D-820-02, D-820-05, D-820-07, D-820-08 |
| `CLAUDE.md` governance rules | 6 | D-820-05, D-820-06, D-820-09, D-820-10 |
| `src/blueprints.ts`, `src/export.ts` | code reference | D-820-03, D-820-08, D-820-09 |
| `wrangler.toml` | config reference | D-820-06 |

---

## Document Control

| Field | Value |
|-------|-------|
| Process | 820-vendor-export |
| Process ID | PROC-820 |
| Rule count | 10 (D-820-01 through D-820-10) |
| Created | 2026-04-29 |
| UT Version | 2.7.0 |
| Status | BUILD — not auditor-certified |

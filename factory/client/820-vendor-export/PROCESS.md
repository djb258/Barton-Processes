# PROCESS: Vendor Export
## Generates data export files for insurance vendors (TPAs, PBMs, carriers) from canonical client data
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-820 |
| Name | Vendor Export |
| Business Silo | svg-agency |
| Sub-Hub | client |
| CTB Position | factory/client/820-vendor-export |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed |
| BAR Reference | BAR-38, BAR-178 |
| Deployed URL | vendor-export-820.svg-outreach.workers.dev |
| Cron | `0 5 * * *` (daily at 5 AM UTC) |
| Runtime | CF Worker |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Insurance vendors (TPAs, PBMs, carriers) require client data in their own proprietary formats on defined schedules. Without this process, export files must be hand-assembled from raw tables — error-prone, unscalable, and guaranteed to miss deadlines. This is the terminal egress point for all client data that leaves the SVG system toward external vendor platforms.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** — Cron schedule (daily 5 AM UTC) or manual HTTP POST to `/export`
2. **"How do we get it?"** — Reads D1 canonical tables from 810's database; vendor blueprints from KV

### Input
- Cron trigger fires daily at 5 AM UTC
- Manual trigger via `POST /export { client_id, vendor_id }`
- Env vars determine which vendors run: `DAILY_VENDORS=TPA,PBM`, `WEEKLY_VENDORS=guardian_life,mutual_of_omaha`, `WEEKLY_DAY=1` (Monday)
- Canonical data from 810's D1: `person`, `election`, `plan`, `vendor`, `external_identity_map`
- Vendor blueprint JSON from KV at key `blueprint:{vendor_id}`

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Cron trigger + env vars | Determine scheduled vendors — daily vendors every day, weekly vendors only on WEEKLY_DAY (Monday) | List of vendor_ids to export | CF Worker cron handler |
| 2 | Vendor list | Get active clients from D1 | List of client_ids per vendor | D1 query (810 canonical) |
| 3 | vendor_id | Load vendor blueprint from KV (`blueprint:{vendor_id}`) | VendorBlueprint (field_mappings, file_format, delimiter) | KV GET |
| 4 | client_id + vendor_id | Read canonical data — JOIN person + election + plan, filtered by client_id + active status | Raw record set | D1 query (810 canonical) |
| 5 | Raw records + vendor_id | Translate internal UUIDs to vendor external IDs via `external_identity_map` | Records with vendor-specific IDs. Missing mapping = MISSING_EXTERNAL_ID error, record skipped | D1 query (810 canonical) |
| 6 | Translated records + blueprint | Apply field mapping — transform internal columns to vendor columns per blueprint spec | Mapped record set | In-memory transform |
| 7 | Mapped records + blueprint | Generate output file — CSV or JSON per blueprint file_format and delimiter | Formatted export file | In-memory serialization |
| 8 | Export result | Log export to `export_log` table; log errors to `export_error` table | Audit trail | D1 WRITE (vendor-export-820) |

### Output
- Formatted export files (CSV or JSON) per vendor blueprint specification
- Export log entries in `export_log` table
- Error entries in `export_error` table for skipped records
- **Currently terminal** — output files are generated but not yet shipped (no R2, email, or SFTP delivery mechanism built)

### Circle (Bedrock S5)
- Every export run writes to `export_log` with record_count, status, and timestamp
- Errors write to `export_error` with error_code and error_message
- `export_schedule` tracks last_run_at and next_run_at per vendor
- `/status` endpoint exposes recent exports + error count for operational visibility
- `/log/:client_id` provides per-client export history for audit trail

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches._

### Blueprint Reference

| Field | Value |
|-------|-------|
| Blueprint | client |
| OSAM Section | doctrine/OSAM.md |
| Snap-On Toolbox | law/SNAP_ON_TOOLBOX.yaml |

### Snap-On Toolbox Tools

| Sub-Hub # | Tool | What It Does Here |
|-----------|------|-------------------|
| 11-structured-data | Cloudflare D1 | All data reads (810 canonical) + audit writes (export_log, export_error) |
| 20-cache-layer | Cloudflare Workers KV | Vendor blueprint JSON storage (blueprint:{vendor_id}) |
| 15-scheduling | CF Cron Triggers | Daily cron at 5 AM UTC triggers export runs |

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| vendor-export-820 | D1 | TODO: not created | WRITE | export_log, export_error, export_schedule |
| 810 canonical (client-intake-810) | D1 | TODO: shared binding | READ ONLY | person, election, plan, vendor, external_identity_map |

### Tools & Integrations (Snap-On Toolbox references — see law/SNAP_ON_TOOLBOX.yaml for vendor details)

| Item | Snap-On Sub-Hub | Cost Tier | Credentials | What It Does |
|------|----------------|-----------|-------------|-------------|
| Cloudflare D1 | 11-structured-data | Free | D1 binding | All data reads (810 canonical) and audit writes |
| Cloudflare Workers KV | 20-cache-layer | Free | KV binding | Vendor blueprint JSON storage |
| CF Cron Triggers | 15-scheduling | Free | none | Daily 5 AM UTC export trigger |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| none yet | — | — | — |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 — all canonical data reads
2. Free KV lookups — vendor blueprint retrieval
3. No paid integrations required for this process

---

## 5. OSAM — Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins._

### READ Access (from 810's D1)

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| person | Employee/dependent records — name, DOB, SSN, status | person_id, client_id |
| election | Benefit election records — plan selections, effective dates | person_id, plan_id |
| plan | Plan definitions — carrier, plan type, coverage levels | plan_id |
| vendor | Vendor registry — vendor_id, vendor_name, vendor_type | vendor_id |
| external_identity_map | UUID-to-vendor-ID translation — internal_id to external_id per vendor | internal_id, vendor_id |

### WRITE Access (to vendor-export-820 D1)

| Table | What It Writes | When |
|-------|---------------|------|
| export_log | export_id, client_id, vendor_id, blueprint_id, record_count, file_format, status, exported_at | Step 8 — after every export run |
| export_error | error_id, client_id, vendor_id, export_id, error_code, error_message, created_at | Step 5/8 — when MISSING_EXTERNAL_ID or BLUEPRINT_NOT_FOUND |
| export_schedule | schedule_id, vendor_id, frequency, last_run_at, next_run_at, status | Step 1 — updated after determining scheduled vendors |

### Join Chain

```
person.person_id
  -> election (person_id, 1:many — elections per person)
    -> plan (plan_id, many:1 — plan definition)
person.person_id
  -> external_identity_map (internal_id = person_id, filtered by vendor_id)
vendor.vendor_id
  -> KV blueprint:{vendor_id} (blueprint lookup)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| WRITE to 810's canonical tables | 820 is read-only consumer of 810's data — CQRS write path violation |
| Direct writes to export_log without running the export | Audit trail must reflect actual export execution |
| Skipping external_identity_map lookup | Every vendor requires their own ID format — internal UUIDs are meaningless to vendors |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| What exports ran for this client? | export_log | client_id |
| What errors occurred for this vendor? | export_error | vendor_id, error_code |
| When does this vendor next export? | export_schedule | vendor_id, next_run_at |
| What is this person's vendor ID? | external_identity_map | internal_id + vendor_id -> external_id |
| What format does this vendor need? | KV | blueprint:{vendor_id} -> file_format, delimiter |

---

## 6. CONSTANTS & VARIABLES (Bedrock S2)

### Constants (structure — never changes)

- **Export pipeline steps are fixed:** determine vendors -> get clients -> load blueprint -> read data -> translate IDs -> map fields -> generate output -> log
- **Vendor blueprint schema is fixed:** field_mappings, file_format, delimiter, include_header, vendor_id, vendor_name
- **Error codes are fixed:** BLUEPRINT_NOT_FOUND, MISSING_EXTERNAL_ID
- **D1 table schemas are fixed:** export_log, export_error, export_schedule (column names and types)
- **KV key pattern is fixed:** `blueprint:{vendor_id}`
- **API endpoint paths are fixed:** GET /health, GET /status, POST /export, GET /log/:client_id
- **Schedule structure is fixed:** daily vendors vs weekly vendors, WEEKLY_DAY config
- **820 is read-only against 810 data** — never writes upstream

### Variables (fill — changes every run)

- Which vendors are scheduled for this run (daily vs weekly day match)
- Which clients are active for each vendor
- How many records per client per vendor
- Which records fail external ID translation (MISSING_EXTERNAL_ID count)
- Content of the generated export files
- Vendor blueprint field mappings (different per vendor, updatable in KV)
- Specific external IDs in external_identity_map

---

## 7. STOP CONDITIONS

_When to halt. Not optional._

| Condition | Action |
|-----------|--------|
| Can't answer two-question intake | HALT — process isn't defined |
| Vendor blueprint not found in KV (BLUEPRINT_NOT_FOUND) | HALT for that vendor — log error, skip to next vendor |
| 810 canonical D1 unreachable | HALT — no source data, nothing to export |
| All records for a client fail external ID lookup | HALT for that client/vendor pair — log bulk error, do not generate empty file |
| KV namespace not bound | HALT — no blueprint source |
| 5 consecutive D1 query failures | HALT — check D1 state |
| Strike 3 on same failure | Troubleshoot/Train -> produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| 810 Client Intake | Canonical tables: person, election, plan, vendor, external_identity_map | PENDING — 810 must be OPERATE with populated data |
| KV vendor blueprints | Vendor blueprint JSON mappings loaded into KV | PENDING — KV namespace not created |
| D1 vendor-export-820 | Local audit tables: export_log, export_error, export_schedule | PENDING — D1 not created |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| None | Terminal process — generates files for external vendor systems (TPAs, PBMs, carriers) |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output._

```
1. GET /health -> expected: { "status": "ok", "process": "820", "name": "vendor-export-820" }
2. GET /status -> expected: { "recent_exports": [], "available_blueprints": [...], "error_count": 0 }
3. Load test blueprint into KV: blueprint:test_vendor -> expected: KV write success
4. POST /export { "client_id": "test-001", "vendor_id": "test_vendor" } -> expected: export generated, export_log entry created
5. GET /log/test-001 -> expected: 1 export log entry with status "success" and record_count > 0
6. POST /export { "client_id": "test-001", "vendor_id": "nonexistent" } -> expected: BLUEPRINT_NOT_FOUND error in export_error table
7. Verify MISSING_EXTERNAL_ID handling: insert person with no external_identity_map entry, run export -> expected: error logged, record skipped, remaining records exported
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** D1 tables exist (vendor-export-820 + 810 canonical)? KV namespace exists? Blueprints loaded?
2. **Flow:** Cron fires -> worker runs -> reads 810 D1 -> reads KV blueprint -> generates output -> writes export_log?
3. **Change:** Internal UUIDs correctly translated to vendor external IDs? Field mappings applied correctly? CSV/JSON formatted per blueprint spec?

If any fails -> that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock S6).

---

## 10. ANALYTICS

_What gets measured. All values BASELINE until first production run._

### Metrics

| Metric | Type | Baseline | First Run | Notes |
|--------|------|----------|-----------|-------|
| Exports generated | count | BASELINE | — | Total export runs completed (per vendor per client) |
| Records per export | count | BASELINE | — | Average records in each generated export file |
| Missing external ID rate | % | BASELINE | — | MISSING_EXTERNAL_ID errors / total records attempted |
| Blueprint load failures | count | BASELINE | — | BLUEPRINT_NOT_FOUND errors from KV |
| File size | KB | BASELINE | — | Average export file size |
| Export latency | ms | BASELINE | — | Average time from trigger to export_log write |

### Tool Scorecard

| Tool | Expected | Actual | Status |
|------|----------|--------|--------|
| D1 (vendor-export-820) | Available | BASELINE | — |
| D1 (810 canonical) | Available | BASELINE | — |
| KV (blueprints) | Available | BASELINE | — |
| CF Cron | Firing | BASELINE | — |

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

_Append-only. Read first, write last. No exceptions. (Bedrock S8)_

### 2026-03-29 — Process documentation created

**ORBT:** BUILD
**Trigger:** Manual — documentation authoring
**Records processed:** 0
**Errors:** 0
**Tools used:** None (documentation only)
**Result:** PROCESS.md created from template. All infrastructure TODO: D1 not created, KV not created, no delivery mechanism.
**Learnings:** 820 is terminal egress — no downstream consumers. Delivery mechanism (R2/email/SFTP) is the biggest open question.
**ORBT after:** BUILD

---

## 12. KNOWN ISSUES & STRIKE TRACKING

_The error history. Append-only — never delete a resolved issue._

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | D1 database_id not set in wrangler.toml | Not yet created | Run `wrangler d1 create vendor-export-820` | 0 |
| 2 | 2026-03-29 | KV namespace id not set in wrangler.toml | Not yet created | Run `wrangler kv namespace create vendor-export-820` | 0 |
| 3 | 2026-03-29 | Export output not shipped anywhere | No delivery mechanism built | TODO: R2, email, or SFTP delivery | 0 |
| 4 | 2026-03-29 | Shared D1 access with 810 not formalized | Cross-database binding undefined | Needs shared D1 binding or cross-database query pattern | 0 |
| 5 | 2026-03-29 | No authentication on endpoints | Not yet implemented | Needs CF Access or bearer token gate | 0 |

**Strike 3 -> Troubleshoot/Train -> Airworthiness Directive.**
AD goes to ALL processes, not just this one. Update the template, not just this file.

---

## 13. SESSION LOG

_Every session that touches this process. Links to imo-brain for detail._

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | PROCESS.md created from PROCESS_TEMPLATE v2.0.0 | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.1.0 |
| Template Version | 3.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | factory/svg-agency/STRUCTURE_MANIFEST.yaml |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

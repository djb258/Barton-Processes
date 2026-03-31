# CLAUDE.md — Process 820: Vendor Export

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

Generates data export files for insurance vendors (TPAs, PBMs, carriers) from canonical client data. Reads D1 canonical tables, applies vendor-specific blueprint mappings from KV, translates internal UUIDs to vendor external IDs, and produces formatted output files. Daily exports for TPA/PBM, weekly for carriers.

## How It Works

Cron-triggered daily + manual HTTP trigger. For each scheduled vendor, for each active client, generate an export.

1. **Determine scheduled vendors** — daily vendors run every day (TPA, PBM), weekly vendors run on configured day (Monday default: Guardian Life, Mutual of Omaha).
2. **Get active clients** from D1.
3. **Load vendor blueprint** from KV — defines field mappings (internal column → vendor column), file format, delimiter, header inclusion.
4. **Read canonical data** — JOIN person + election + plan for the client.
5. **Translate IDs** — lookup `external_identity_map` to convert internal UUIDs to vendor-specific external IDs. Missing mapping = error (record skipped).
6. **Apply field mapping** — transform internal columns to vendor columns per blueprint.
7. **Generate output** — CSV or JSON per blueprint spec.
8. **Log export** to `export_log` table.

## API Endpoints

| Method | Path | What |
|--------|------|------|
| GET | `/health` | Health check |
| GET | `/status` | Recent exports + available blueprints + error count |
| POST | `/export` | `{ client_id, vendor_id }` — manual export trigger |
| GET | `/log/:client_id` | Export history for a client |

## Vendor Blueprint System

Blueprints stored in KV as JSON at key `blueprint:{vendor_id}`:

```typescript
interface VendorBlueprint {
  vendor_id: string;
  vendor_name: string;
  file_format: 'csv' | 'json';
  delimiter: string;            // typically ','
  field_mappings: Record<string, string>;  // internal_column → vendor_column
  include_header: boolean;
}
```

Source files: `db/vendor_blueprints/*.mapping.json` in client repo.

## Export Schedule

| Frequency | Vendors | Config |
|-----------|---------|--------|
| Daily | TPA, PBM | `DAILY_VENDORS` env var |
| Weekly (Monday) | Guardian Life, Mutual of Omaha | `WEEKLY_VENDORS` env var, `WEEKLY_DAY=1` |

## Databases

**D1 workspace:** `vendor-export-820`
- `export_log` — export_id (PK), client_id, vendor_id, blueprint_id, record_count, file_format, status, exported_at
- `export_error` — error_id (PK), client_id, vendor_id, export_id, error_code, error_message, created_at
- `export_schedule` — schedule_id (PK), vendor_id, frequency, last_run_at, next_run_at, status

**D1 read (from 810):** Reads canonical tables — `person`, `election`, `plan`, `vendor`, `external_identity_map`

**KV namespace:** `vendor-export-820` — Vendor blueprint JSON mappings

## Key Joins

- Export data: `person` JOIN `election` ON person_id JOIN `plan` ON plan_id, filtered by client_id + active status
- ID translation: `external_identity_map.internal_id` = person_id, filtered by vendor_id + active status
- Blueprint lookup: KV key `blueprint:{vendor_id}`

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | 810 Client Intake | Canonical tables (person, election, plan, vendor, external_identity_map) |
| Downstream | None | Terminal — generates files for external vendor systems |

## Worker Config

- **Name:** `vendor-export-820`
- **URL:** vendor-export-820.svg-outreach.workers.dev
- **Cron:** `0 5 * * *` (daily at 5 AM UTC)
- **D1:** `vendor-export-820`
- **KV:** `vendor-export-820`
- **Env vars:** `DAILY_VENDORS=TPA,PBM`, `WEEKLY_VENDORS=guardian_life,mutual_of_omaha`, `WEEKLY_DAY=1`
- **Secrets provider:** Doppler

## Error Codes

| Code | Meaning |
|------|---------|
| BLUEPRINT_NOT_FOUND | No KV blueprint for the requested vendor_id |
| MISSING_EXTERNAL_ID | Person has no external ID mapping for this vendor — record skipped |

## Known Issues

| Issue | Resolution |
|-------|------------|
| D1 database_id and KV id not set in wrangler.toml | Run `wrangler d1 create` and `wrangler kv namespace create` |
| Export output not shipped anywhere yet | TODO comment: need R2, email, or SFTP delivery mechanism |
| Shared D1 access with 810 not formalized | Currently reads from 810's D1 or requires shared database binding |
| No authentication on endpoints | Needs CF Access or bearer token gate |

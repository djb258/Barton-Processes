# D1 Audit Report

Date: 2026-05-03
BAR: BAR-379
Process: PROC-060-D1-AUDIT
Mode: read-only Cloudflare D1 introspection
Auditor: Codex

## Verdict

P=1 for first live introspection sweep.

P=0 for full schema-drift certification.

Reason: all six active D1 databases were reachable through `npx wrangler d1 execute --remote`; object counts and representative row counts were captured with `changed_db: false`. Full GREEN still requires table-by-table schema comparison against `D1_DATA_DICTIONARY.md`, stale-table analysis, orphan ownership mapping, and hot-query index checks.

## Scope

Active D1 databases inspected:

| Database | Purpose |
|----------|---------|
| `svg-d1-spine` | Company Lifecycle, LCS, sales/client spine |
| `svg-d1-outreach-ops` | Outreach, people, DOL, enrichment, LCS outreach working set |
| `imo-d1-global` | Global shared references |
| `svg-d1-storage` | Storage / real-estate public datasets |
| `lbb` | Library Barton Brain / logbook |
| `mission-control` | Mission Control, BAR context, alerts, briefings |

## Object Counts

| Database | Tables | Indexes | Views | D1 size after query |
|----------|--------|---------|-------|---------------------|
| `svg-d1-spine` | 55 | 77 | 0 | 70,078,464 bytes |
| `svg-d1-outreach-ops` | 69 | 83 | 17 | 995,667,968 bytes |
| `imo-d1-global` | 2 | 1 | 0 | 4,882,432 bytes |
| `svg-d1-storage` | 101 | 22 | 0 | 50,835,456 bytes |
| `lbb` | 5 | 14 | 0 | 1,560,576 bytes |
| `mission-control` | 48 | 128 | 0 | 2,011,136 bytes |

## Representative Row Counts

### `svg-d1-spine`

| Table | Rows |
|-------|------|
| `cl_company_identity` | 32,702 |
| `lcs_event` | 12,803 |
| `lcs_signal_queue` | 4,506 |
| `lcs_err0` | 651 |

### `svg-d1-outreach-ops`

| Table | Rows |
|-------|------|
| `slot_workbench` | 101,559 |
| `people_people_master` | 57,667 |
| `outreach_company_target` | 32,702 |
| `dol_form_5500` | 14,252 |
| `lcs_message_ledger` | 0 |

### `mission-control`

| Table | Rows |
|-------|------|
| `mc_alerts` | 254 |
| `mc_bar_context` | 0 |
| `mc_briefings` | 4 |
| `mc_builds` | 0 |
| `dyno_run` | 0 |

### `lbb`

| Table | Rows |
|-------|------|
| `lbb_records` | 562 |
| `lbb_logbook` | 181 |
| `lbb_subjects` | 23 |
| `lbb_records_error` | 38 |

## Evidence Commands

Commands were read-only and returned `changed_db: false`.

```bash
npx wrangler d1 execute <db> --remote --json --command "SELECT 'tables' AS metric, COUNT(*) AS value FROM sqlite_master WHERE type='table' UNION ALL SELECT 'indexes', COUNT(*) FROM sqlite_master WHERE type='index' UNION ALL SELECT 'views', COUNT(*) FROM sqlite_master WHERE type='view';"
npx wrangler d1 execute <db> --remote --json --command "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
```

## Findings

| ID | Severity | Finding | Route |
|----|----------|---------|-------|
| BAR379-F1 | YELLOW | `svg-d1-outreach-ops` is the largest active D1 at 995,667,968 bytes and should get priority for schema drift and stale table checks. | BAR-379 Stage 2 |
| BAR379-F2 | YELLOW | `svg-d1-storage` has 101 tables but only 22 indexes, so hot-query index health needs a dedicated pass before performance certification. | BAR-379 Stage 3 |
| BAR379-F3 | YELLOW | `lcs_message_ledger` in `svg-d1-outreach-ops` has 0 rows while `svg-d1-spine.lcs_event` has 12,803 rows; this may be expected split-brain staging, but it must be reconciled with OSAM/LCS source-of-truth. | BAR-375 / BAR-379 join |
| BAR379-F4 | YELLOW | `mission-control.mc_bar_context`, `mc_builds`, and `dyno_run` currently have 0 rows. This may be normal for current usage, but BAR cleanup needs either producers wired or tables marked inactive. | Mission Control follow-up |

## Next Pass

1. Generate table-by-table schema fingerprints for all six D1s.
2. Diff live schemas against `D1_DATA_DICTIONARY.md`.
3. Map table ownership using `cron_registry.yaml`, OSAM, and the 16 UT-local process YAMLs.
4. Run stale-table checks where timestamp columns exist.
5. Run `EXPLAIN QUERY PLAN` on hot queries for `svg-d1-outreach-ops`, `svg-d1-storage`, and LCS tables.

## Closeout

This report does not mutate D1, does not recommend drops, and does not promote any database to drift-clean. It only certifies that the first live introspection sweep ran successfully and produced a grounded baseline for the deeper BAR-379 audit cycle.

---

## Stage 2 Schema Fingerprint Sweep

Date: 2026-05-04
Mode: read-only Cloudflare D1 introspection
Result: `changed_db: false` on all six databases

This pass captured live object fingerprints from `sqlite_master` using:

```bash
npx wrangler d1 execute <db> --remote --json --command "SELECT type, COUNT(*) AS count FROM sqlite_master WHERE type IN ('table','index','view') AND name NOT LIKE 'sqlite_%' GROUP BY type ORDER BY type;"
npx wrangler d1 execute <db> --remote --json --command "SELECT name, type, COALESCE(sql,'') AS sql FROM sqlite_master WHERE type IN ('table','index','view') AND name NOT LIKE 'sqlite_%' ORDER BY type, name;"
```

### Live Object Counts

| Database | User tables | User indexes | Views | Size after query | Dictionary claimed tables | Drift signal |
|----------|-------------|--------------|-------|------------------|---------------------------|--------------|
| `svg-d1-spine` | 54 | 30 | 0 | 70,078,464 bytes | 38 | +16 tables vs dictionary |
| `svg-d1-outreach-ops` | 68 | 34 | 17 | 995,667,968 bytes | 33 | +35 tables vs dictionary |
| `imo-d1-global` | 2 | 0 | 0 | 4,882,432 bytes | 1 | +1 table vs dictionary |
| `svg-d1-storage` | 100 | 3 | 0 | 50,835,456 bytes | 92 | +8 tables vs dictionary |
| `lbb` | 5 | 10 | 0 | 1,572,864 bytes | 4 | +1 table vs dictionary |
| `mission-control` | 52 | 91 | 0 | 2,080,768 bytes | variable | dictionary needs concrete baseline |

### Stage 2 Findings

| ID | Severity | Finding | Evidence | Required BAR Route |
|----|----------|---------|----------|--------------------|
| BAR379-F5 | ORANGE | `D1_DATA_DICTIONARY.md` is materially stale for the two outreach-critical databases. | `svg-d1-spine` live 54 user tables vs 38 claimed; `svg-d1-outreach-ops` live 68 user tables vs 33 claimed. | Refresh dictionary from live schema fingerprints; do not hand-edit counts. |
| BAR379-F6 | ORANGE | `svg-d1-storage` has 100 user tables but only 3 user-defined indexes in the live `sqlite_master` count. | Stage 2 query returned `table=100`, `index=3`. | Dedicated index-health pass with `EXPLAIN QUERY PLAN` before performance certification. |
| BAR379-F7 | YELLOW | `mission-control` now needs a concrete dictionary baseline. | Live count is 52 user tables after BAR-381 squawks migration. | Add mission-control section to dictionary instead of leaving table count variable. |
| BAR379-F8 | YELLOW | `imo-d1-global` and `lbb` both drifted above dictionary inventory. | `imo-d1-global` live 2 vs claimed 1; `lbb` live 5 vs claimed 4. | Include both in dictionary refresh. |

### Certification Status

P=1 for live schema fingerprint capture.

P=0 for BAR-379 full acceptance. The dictionary is stale, stale-table timestamps are not yet table-by-table complete, orphan ownership is not mapped, and hot-query index plans are not yet attached.

### Next Pass

1. Generate a machine-readable schema fingerprint artifact per database.
2. Refresh `D1_DATA_DICTIONARY.md` from live fingerprints after sovereign sign-off.
3. Add per-table stale timestamp checks for tables containing `updated_at`, `created_at`, `attempted_at`, `processed_at`, or domain-specific write timestamps.
4. Run index-health checks on `svg-d1-outreach-ops`, `svg-d1-storage`, `svg-d1-spine.lcs_*`, and Mission Control hot routes.

# BAR-377 Live Refresh - bp.010

Date: 2026-05-04
Process: bp.010 SEED D1
Mode: corrected Cloudflare token, remote D1 read-only checks

## Token Correction

Initial Stage 2 evidence was blocked because Wrangler used the wrong token path. The successful refresh used:

```text
CLOUDFLARE_API_TOKEN = GLOBAL_CLOUDFLARE_API_TOKEN
```

## Remote D1 Counts

| Gauge | Expected From PROCESS-UT | Live Count | Status |
|-------|--------------------------|------------|--------|
| `svg-d1-spine.cl_company_identity` | 32,702 | 32,702 | PASS |
| `outreach_company_target` | 32,702 | 32,702 | PASS |
| `outreach_outreach` | 32,702 | 32,702 | PASS |
| `outreach_blog` | 32,702 | 32,702 | PASS |
| `outreach_dol` | 32,702 in UT table; DOL gap is structural elsewhere | 27,464 | REVIEW |
| `people_company_slot` | 98,106 | 98,106 | PASS |
| `people_people_master` | 58,857 | 57,667 | FAIL |
| `coverage_service_agent` | 3 | 3 | PASS |
| `coverage_service_agent_coverage` | 3 | 3 | PASS |
| `outreach_column_registry` | 79 | 78 | FAIL |

Additional People slot split:

- Filled slots: 57,776
- Empty slots: 40,330

## Queries That Hit D1 Limits

The all-in-one count query failed with `too many terms in compound SELECT`.

The orphan-slot anti-join exceeded D1 CPU time limit. It should be rerun with an indexed or paginated query before full OPERATE recertification.

## Verdict

P=0 for full bp.010 certification.

Core SEED D1 company/spine counts are healthy, but People and column-registry baselines drift from the UT. The process remains usable, but not cleanly recertified until the People baseline and column registry discrepancy are explained or repaired.

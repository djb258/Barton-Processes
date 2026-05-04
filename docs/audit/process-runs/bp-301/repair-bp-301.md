# BAR-377 Repair Record - bp.301

Date: 2026-05-04
Process: bp.301 Page Parser
Role Path: Planner classification -> local Mechanic repair -> Auditor pending

## Repair Summary

bp.301 had the same local D1 execution defect family found in adjacent outreach scripts:

- `WRANGLER_CWD` defaulted to an old non-existent `Documents/imo-creator-v2-20260317/workers/lcs-hub` path.
- The active script imported `curl_cffi` but the process had no local requirements file.
- Python subprocess called bare `npx`, which is not reliable from Python `CreateProcess` on Windows.
- Multi-line SQL needed newline normalization before `wrangler d1 execute --command`.

## Files Changed

- `factory/outreach/301-page-parser/src/page-parser.py`
- `factory/outreach/301-page-parser/requirements.txt`

## Verification

| Check | Result |
|-------|--------|
| `python -m py_compile factory/outreach/301-page-parser/src/page-parser.py` | PASS |
| Dry run: `python factory/outreach/301-page-parser/src/page-parser.py --limit 1 --dry-run` under Doppler/Cloudflare token | PASS - loaded 1 live D1 company, fetched 1 page, found 13 people, completed without D1 writes |

## Remaining Certification Risks

- Dry-run emitted `[WARN] Title Classifier not available`; extraction still ran, but classifier wiring remains a parser-quality risk.
- Only `page-parser.py` was repaired as the active workflow target; older helper scripts still contain stale local paths and need separate cleanup if they remain operational.
- Production writes and scheduled rollout remain outside this certification.

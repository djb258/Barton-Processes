# BAR-377 Repair Record - bp.300

Date: 2026-05-04
Process: bp.300 Blog Worker
Role Path: Planner classification -> local Mechanic repair -> Auditor pending

## Repair Summary

bp.300 had the same local D1 execution defect family found in downstream outreach scripts:

- `WRANGLER_CWD` defaulted to an old non-existent `Documents/imo-creator-v2-20260317/workers/lcs-hub` path.
- The active script imported `curl_cffi` but the process had no local requirements file.
- Python subprocess called bare `npx`, which is not reliable from Python `CreateProcess` on Windows.
- Multi-line SQL needed newline normalization before `wrangler d1 execute --command`.
- The active script lacked a safe dry-run mode for D1 writes, preventing controlled verification.

## Files Changed

- `factory/outreach/300-blog-worker/src/blog-recon.py`
- `factory/outreach/300-blog-worker/requirements.txt`

## Verification

| Check | Result |
|-------|--------|
| `python -m py_compile factory/outreach/300-blog-worker/src/blog-recon.py` | PASS |
| Dry run: `python factory/outreach/300-blog-worker/src/blog-recon.py --phase 1 --limit 1 --dry-run` under Doppler/Cloudflare token | PASS - loaded 1 live D1 record and completed without D1 writes |

## Remaining Certification Risks

- Only `blog-recon.py` was repaired as the active workflow target; older helper scripts still contain stale local paths and need separate cleanup if they remain operational.
- The tested run was phase 1 dry-run only; production writes and monthly cron rollout remain outside this certification.
- Full process promotion still depends on scheduled run evidence and downstream `bp.301` consumption.

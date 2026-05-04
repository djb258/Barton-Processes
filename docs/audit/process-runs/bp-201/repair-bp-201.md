# BAR-377 Repair Record - bp.201

Date: 2026-05-04
Process: bp.201 Email Discovery
Role Path: Planner classification -> local Mechanic repair -> Auditor pending

## Repair Summary

bp.201 had four local execution defects:

- `WRANGLER_CWD` defaulted to an old non-existent `Documents/imo-creator-v2-20260317/workers/lcs-hub` path.
- The Python dependency `curl_cffi` was imported but not declared in a process-local requirements file.
- Python subprocess could not launch bare `npx` on Windows because PowerShell resolves `npx.ps1`, not an executable accepted by `CreateProcess`.
- Multi-line SQL passed to `wrangler d1 execute --command` was rejected by Wrangler on Windows, causing the script to falsely report no live slots.

## Files Changed

- `factory/outreach/201-email-discovery/src/find-email.py`
- `factory/outreach/201-email-discovery/requirements.txt`

## Verification

| Check | Result |
|-------|--------|
| `python -m py_compile factory/outreach/201-email-discovery/src/find-email.py` | PASS |
| `pip install -r factory/outreach/201-email-discovery/requirements.txt` | PASS |
| Dry run: `python factory/outreach/201-email-discovery/src/find-email.py --limit 1 --gate a --dry-run` under Doppler/Cloudflare token | PASS - loaded 1 live slot and completed without D1 writes |
| Remote D1 backlog count | PASS - `slot_workbench WHERE has_name=1 AND has_email=0` = `10545` |
| Remote D1 filled count | PASS - `slot_workbench WHERE has_email=1` = `64581` |

## Remaining Certification Risks

- The tested run was dry-run only; no production write was performed.
- Gate A missed the sampled record because no email pattern/hunter candidate existed for that slot.
- Full throughput still requires scheduled execution or an explicit controlled live run for Gate B/Gate C.

# BAR-377 Repair Record - bp.202

Date: 2026-05-04
Process: bp.202 LinkedIn Discovery
Role Path: Planner classification -> local Mechanic repair -> Auditor pending

## Repair Summary

bp.202 had three local execution defects:

- `WRANGLER_CWD` defaulted to an old non-existent `Documents/imo-creator-v2-20260317/workers/lcs-hub` path.
- The Python dependency `curl_cffi` was imported but not declared in a process-local requirements file.
- Python subprocess could not launch bare `npx` on Windows because PowerShell resolves `npx.ps1`, not an executable accepted by `CreateProcess`.

The D1 subprocess path was also hardened to use UTF-8 replacement decoding and normalized SQL newlines so bp.202 stays aligned with the bp.201 D1 access pattern.

## Files Changed

- `factory/outreach/202-linkedin-discovery/src/find-linkedin.py`
- `factory/outreach/202-linkedin-discovery/requirements.txt`

## Verification

| Check | Result |
|-------|--------|
| `python -m py_compile factory/outreach/202-linkedin-discovery/src/find-linkedin.py` | PASS |
| `pip install -r factory/outreach/201-email-discovery/requirements.txt` | PASS - installed shared `curl_cffi` dependency used by bp.202 |
| Dry run: `python factory/outreach/202-linkedin-discovery/src/find-linkedin.py --limit 1 --dry-run` under Doppler/Cloudflare token | PASS - loaded 1 live slot, found LinkedIn URL, dry-ran D1 update |
| Remote D1 backlog count | PASS - `slot_workbench WHERE has_name=1 AND has_linkedin=0` = `19237` |
| Remote D1 filled count | PASS - `slot_workbench WHERE has_linkedin=1` = `55593` |

## Remaining Certification Risks

- The tested run was dry-run only; no production write was performed.
- Full throughput still requires scheduled execution or an explicit controlled live run.
- Gate C used live external search/proxy behavior, so large runs need rate/captcha monitoring.

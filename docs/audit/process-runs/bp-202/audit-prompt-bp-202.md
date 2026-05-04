ROLE: AUDITOR
TASK: Audit the bp.202 LinkedIn Discovery repair. Return `VERDICT: P=1` only if the local repair is certified for BAR-377 repair scope. Return `VERDICT: P=0` with cited reasons if any blocker remains.

READ:
- factory/outreach/202-linkedin-discovery/src/find-linkedin.py
- factory/outreach/202-linkedin-discovery/requirements.txt
- docs/audit/process-runs/bp-202/repair-bp-202.md
- docs/audit/process-runs/bp-202/diff-bp-202.md

SCOPE:
- Read-only audit. Do not modify files.

ACCEPTANCE:
- The script must default Wrangler execution to the current Barton-Processes repo, not a stale local path.
- Python dependencies needed by the script must be declared locally.
- The D1 subprocess command must be executable from Python on Windows.
- SQL/Unicode subprocess handling must be robust enough for dry-run D1 execution.
- Repair evidence must distinguish local execution repair from remaining live/scheduled production rollout.

CONSTRAINTS:
- Auditor does not fix findings.
- Cite only files named in READ.

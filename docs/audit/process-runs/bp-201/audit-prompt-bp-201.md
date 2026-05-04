ROLE: AUDITOR
TASK: Audit the bp.201 Email Discovery repair. Return `VERDICT: P=1` only if the local repair is certified for BAR-377 repair scope. Return `VERDICT: P=0` with cited reasons if any blocker remains.

READ:
- factory/outreach/201-email-discovery/src/find-email.py
- factory/outreach/201-email-discovery/requirements.txt
- docs/audit/process-runs/bp-201/repair-bp-201.md
- docs/audit/process-runs/bp-201/diff-bp-201.md

SCOPE:
- Read-only audit. Do not modify files.

ACCEPTANCE:
- The script must default Wrangler execution to the current Barton-Processes repo, not a stale local path.
- Python dependencies needed by the script must be declared locally.
- The D1 subprocess command must be executable from Python on Windows.
- Multi-line SQL must not cause Wrangler to reject the command.
- Repair evidence must distinguish local execution repair from remaining live/scheduled production rollout.

CONSTRAINTS:
- Auditor does not fix findings.
- Cite only files named in READ.

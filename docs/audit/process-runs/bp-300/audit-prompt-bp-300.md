ROLE: AUDITOR
TASK: Audit the bp.300 Blog Worker local repair. Return `VERDICT: P=1` only if the local repair is certified for BAR-377 repair scope. Return `VERDICT: P=0` with cited reasons if any blocker remains.

READ:
- factory/outreach/300-blog-worker/src/blog-recon.py
- factory/outreach/300-blog-worker/requirements.txt
- docs/audit/process-runs/bp-300/repair-bp-300.md
- docs/audit/process-runs/bp-300/diff-bp-300.md

SCOPE:
- Read-only audit. Do not modify files.

ACCEPTANCE:
- The active script must default Wrangler execution to the current Barton-Processes repo, not a stale local path.
- Python dependencies needed by the active script must be declared locally.
- The D1 subprocess command must be executable from Python on Windows.
- Multi-line SQL must not cause Wrangler to reject the command.
- There must be a safe dry-run path for local verification without production D1 writes.
- Repair evidence must distinguish local active-script repair from older helper cleanup and scheduled production rollout.

CONSTRAINTS:
- Auditor does not fix findings.
- Cite only files named in READ.

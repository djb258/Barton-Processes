ROLE: AUDITOR
TASK: Audit the bp.301 Page Parser local repair. Return `VERDICT: P=1` only if the local repair is certified for BAR-377 repair scope. Return `VERDICT: P=0` with cited reasons if any blocker remains.

READ:
- factory/outreach/301-page-parser/src/page-parser.py
- factory/outreach/301-page-parser/requirements.txt
- docs/audit/process-runs/bp-301/repair-bp-301.md
- docs/audit/process-runs/bp-301/diff-bp-301.md

SCOPE:
- Read-only audit. Do not modify files.

ACCEPTANCE:
- The active script must default Wrangler execution to the current Barton-Processes repo, not a stale local path.
- Python dependencies needed by the active script must be declared locally.
- The D1 subprocess command must be executable from Python on Windows.
- SQL/Unicode subprocess handling must be robust enough for dry-run D1 execution.
- Repair evidence must distinguish local active-script repair from older helper cleanup, parser-quality risks, and scheduled production rollout.

CONSTRAINTS:
- Auditor does not fix findings.
- Cite only files named in READ.

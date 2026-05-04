ROLE: AUDITOR
TASK: Audit the bp.200 People Worker repair. Return `VERDICT: P=1` only if the local repair is certified for BAR-377 repair scope. Return `VERDICT: P=0` with cited reasons if any blocker remains.

READ:
- factory/outreach/200-people-worker/package.json
- factory/outreach/200-people-worker/tsconfig.json
- factory/outreach/200-people-worker/src-v2/types.ts
- factory/outreach/200-people-worker/wrangler.toml
- factory/outreach/200-people-worker/src-v2/index.ts
- docs/audit/process-runs/bp-200/repair-bp-200.md
- docs/audit/process-runs/bp-200/diff-bp-200.md

SCOPE:
- Read-only audit. Do not modify files.

ACCEPTANCE:
- Package scripts must point to the active Wrangler config.
- TypeScript config must include the active Worker source.
- PassResult must represent the metrics returned by the active source.
- Repair evidence must distinguish local verification repair from the remaining live fill-rate gap.

CONSTRAINTS:
- Auditor does not fix findings.
- Cite only files named in READ.

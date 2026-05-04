# Planner Diff - bp.700 Campaign Engine

Date: 2026-05-04
BAR: BAR-377
Stage: 3 - PLANNER DIFF
Mode: inventory + live-state comparison

## Verdict

Route: **BLOCKED/BUILD**

This is a Planner diff, not a Mechanic dispatch and not a Codex certification.

## Inputs Compared

| Artifact | Path | Status |
|----------|------|--------|
| Inventory | docs/audit/process-runs/bp-700/inventory-bp-700.md | PRESENT |
| Live State | docs/audit/process-runs/bp-700/live-state-bp-700.md | PRESENT |
| Fleet Index | Barton-Processes/INDEX.md | PRESENT |
| Execution Order | Barton-Processes/EXECUTION_ORDER.md | PRESENT |
| Cron Registry | actory/governance/050-cron-registry/cron_registry.yaml | PRESENT |

## Delta

| Field | Inventory / Source | Live / Evidence | Delta |
|-------|--------------------|-----------------|-------|
| ORBT | BUILD | BUILD | Route follows ORBT and runtime evidence |
| Route | n/a | BLOCKED/BUILD | Planner classification |
| Rationale | n/a | Depends on bp.600 in execution order; proposed weekday cron; must feed bp.100. | Determines next dispatch |

## Required Next Step

Resolve bp.600 dependency or approve override, then build campaign cron/evidence.

## Dispatch Guardrails

- Full Four-Brain path required for executable repair/build/audit work.
- Use PROC-070 endpoint sequence when dispatching: Planner -> Foreman -> Mechanic -> Auditor -> Emit.
- Every role transition requires LBB Step N evidence.
- Do not certify from this diff alone.

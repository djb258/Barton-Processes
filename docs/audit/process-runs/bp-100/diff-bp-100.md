# Planner Diff - bp.100 LCS Pipeline

Date: 2026-05-04
BAR: BAR-377
Stage: 3 - PLANNER DIFF
Mode: inventory + live-state comparison

## Verdict

Route: **REPAIR -> BLOCKED_SOURCE_DRIFT**

This is a Planner diff, not a Mechanic dispatch and not a Codex certification.

## Inputs Compared

| Artifact | Path | Status |
|----------|------|--------|
| Inventory | docs/audit/process-runs/bp-100/inventory-bp-100.md | PRESENT |
| Live State | docs/audit/process-runs/bp-100/live-state-bp-100.md | PRESENT |
| Fleet Index | Barton-Processes/INDEX.md | PRESENT |
| Execution Order | Barton-Processes/EXECUTION_ORDER.md | PRESENT |
| Cron Registry | actory/governance/050-cron-registry/cron_registry.yaml | PRESENT |

## Delta

| Field | Inventory / Source | Live / Evidence | Delta |
|-------|--------------------|-----------------|-------|
| ORBT | REPAIR | REPAIR | Route follows ORBT and runtime evidence |
| Route | n/a | REPAIR -> BLOCKED_SOURCE_DRIFT | Planner classification updated after live/source comparison |
| Rationale | n/a | Live `lcs-hub` is v2 and processing; Barton-Processes local source is stale and would deploy a different D1-only worker. | Determines next dispatch |

## Required Next Step

Planner must decide whether `barton-outreach-core/hubs/lcs-send` is canonical source, then either sync Barton-Processes or mark Barton-Processes bp.100 as documentation-only. Do not deploy stale Barton-Processes source.

## Dispatch Guardrails

- Full Four-Brain path required for executable repair/build/audit work.
- Use PROC-070 endpoint sequence when dispatching: Planner -> Foreman -> Mechanic -> Auditor -> Emit.
- Every role transition requires LBB Step N evidence.
- Do not certify from this diff alone.

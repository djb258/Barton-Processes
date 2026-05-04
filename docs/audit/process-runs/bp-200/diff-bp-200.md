# Planner Diff - bp.200 People Worker

Date: 2026-05-04
BAR: BAR-377
Stage: 3 - PLANNER DIFF
Mode: inventory + live-state comparison

## Verdict

Route: **REPAIR -> AUDIT_READY**

This is a Planner diff, not a Mechanic dispatch and not a Codex certification.

## Inputs Compared

| Artifact | Path | Status |
|----------|------|--------|
| Inventory | docs/audit/process-runs/bp-200/inventory-bp-200.md | PRESENT |
| Live State | docs/audit/process-runs/bp-200/live-state-bp-200.md | PRESENT |
| Fleet Index | Barton-Processes/INDEX.md | PRESENT |
| Execution Order | Barton-Processes/EXECUTION_ORDER.md | PRESENT |
| Cron Registry | actory/governance/050-cron-registry/cron_registry.yaml | PRESENT |

## Delta

| Field | Inventory / Source | Live / Evidence | Delta |
|-------|--------------------|-----------------|-------|
| ORBT | REPAIR | REPAIR | Route follows ORBT and runtime evidence |
| Route | n/a | REPAIR -> AUDIT_READY | Planner classification updated after local repair |
| Rationale | n/a | Local verification path repaired; live health shows 98,106 slots, 57,667 people, and 40,330 empty slots. Staging is empty, so remaining gap is operational/enrichment route work. | Determines next dispatch |

## Required Next Step

Run Codex audit on local repair. Then execute/fix enrichment routes needed to reduce the 40,330 empty-slot gap.

## Dispatch Guardrails

- Full Four-Brain path required for executable repair/build/audit work.
- Use PROC-070 endpoint sequence when dispatching: Planner -> Foreman -> Mechanic -> Auditor -> Emit.
- Every role transition requires LBB Step N evidence.
- Do not certify from this diff alone.

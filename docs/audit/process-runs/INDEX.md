# BAR-377 Process Run Index

Date: 2026-05-04
BAR: BAR-377
Scope: 16 Barton process Four-Brain audit rollout
Stage: Fleet tracker

## Purpose

This index tracks the BAR-377 evidence set for all 16 Barton processes. It does not replace the process UTs and does not move YAMLs out of their process folders. It only points to per-process run artifacts under docs/audit/process-runs/bp-NNN/.

## Fleet Status

| Process | Name | ORBT From INDEX | Depends On | Inventory | Live State | Planner Diff | Audit |
|---------|------|-----------------|------------|-----------|------------|--------------|-------|
| bp.010 | SEED D1 | OPERATE | none | [DONE](bp-010/inventory-bp-010.md) | [DONE](bp-010/live-state-bp-010.md) | [DONE](bp-010/diff-bp-010.md) | [P=0](bp-010/audit-bp-010.md) |
| bp.100 | LCS Pipeline | REPAIR | 700 | [DONE](bp-100/inventory-bp-100.md) | [DONE](bp-100/live-state-bp-100.md) | [P=0 source drift](bp-100/source-drift-bp-100.md) | TODO |
| bp.200 | People Worker | REPAIR | 010 | [DONE](bp-200/inventory-bp-200.md) | [DONE](bp-200/live-state-bp-200.md) | [REPAIRED](bp-200/repair-bp-200.md) | [P=1 repair](bp-200/audit-bp-200.md) |
| bp.201 | Email Discovery | BUILD | 200 | [DONE](bp-201/inventory-bp-201.md) | [DONE](bp-201/live-state-bp-201.md) | [REPAIRED](bp-201/repair-bp-201.md) | [P=1 repair](bp-201/audit-bp-201.md) |
| bp.202 | LinkedIn Discovery | BUILD | 200 | [DONE](bp-202/inventory-bp-202.md) | [DONE](bp-202/live-state-bp-202.md) | [REPAIRED](bp-202/repair-bp-202.md) | [P=1 repair](bp-202/audit-bp-202.md) |
| bp.300 | Blog Worker | BUILD | 010 | [DONE](bp-300/inventory-bp-300.md) | [DONE](bp-300/live-state-bp-300.md) | [REPAIRED](bp-300/repair-bp-300.md) | [P=1 repair](bp-300/audit-bp-300.md) |
| bp.301 | Page Parser | BUILD | 300 | [DONE](bp-301/inventory-bp-301.md) | [DONE](bp-301/live-state-bp-301.md) | [REPAIRED](bp-301/repair-bp-301.md) | [P=1 repair](bp-301/audit-bp-301.md) |
| bp.400 | DOL Views | OPERATE | 010 | [DONE](bp-400/inventory-bp-400.md) | [REFRESHED](bp-400/live-refresh-bp-400.md) | [DONE](bp-400/diff-bp-400.md) | [P=1 D1 refresh](bp-400/audit-bp-400.md) |
| bp.500 | Talent Flow | BUILD | 200 | [DONE](bp-500/inventory-bp-500.md) | [DONE](bp-500/live-state-bp-500.md) | [DONE](bp-500/diff-bp-500.md) | TODO |
| bp.600 | BIT Scoring | TROUBLESHOOT_TRAIN | 200, 300, 400, 500 | [DONE](bp-600/inventory-bp-600.md) | [DONE](bp-600/live-state-bp-600.md) | [DONE](bp-600/diff-bp-600.md) | TODO |
| bp.700 | Campaign Engine | BUILD | 600 | [DONE](bp-700/inventory-bp-700.md) | [DONE](bp-700/live-state-bp-700.md) | [DONE](bp-700/diff-bp-700.md) | TODO |
| bp.800 | Client Mint | BUILD | 100 | [DONE](bp-800/inventory-bp-800.md) | [DONE](bp-800/live-state-bp-800.md) | [DONE](bp-800/diff-bp-800.md) | TODO |
| bp.810 | Client Intake | BUILD | 800 | [DONE](bp-810/inventory-bp-810.md) | [DONE](bp-810/live-state-bp-810.md) | [DONE](bp-810/diff-bp-810.md) | TODO |
| bp.820 | Vendor Export | BUILD | 810 | [DONE](bp-820/inventory-bp-820.md) | [DONE](bp-820/live-state-bp-820.md) | [REPAIRED](bp-820/repair-bp-820.md) | [P=1 repair](bp-820/audit-bp-820.md) |
| bp.830 | Client Portal | BUILD | 810 | [DONE](bp-830/inventory-bp-830.md) | [DONE](bp-830/live-state-bp-830.md) | [DONE](bp-830/diff-bp-830.md) | TODO |
| bp.900 | Sales Portal | BUILD | 100 | [DONE](bp-900/inventory-bp-900.md) | [DONE](bp-900/live-state-bp-900.md) | [DONE](bp-900/diff-bp-900.md) | TODO |

## Current Completion

| Artifact Type | Complete | Required | Status |
|---------------|----------|----------|--------|
| Stage 1 inventory | 16 | 16 | DONE |
| Stage 2 live-state | 16 | 16 | DONE |
| Stage 3 Planner diff | 16 | 16 | DONE |
| Stage 5 audit | 8 | 16 | IN_PROGRESS |

## Stage 3 Routing Summary

| Route | Processes |
|-------|-----------|
| No-op audit candidates | bp.010, bp.400 |
| Repair | none |
| Blocked source drift | bp.100 |
| Repaired and audit-certified | bp.200, bp.201, bp.202, bp.300, bp.301, bp.820 |
| Build / repair-build | bp.830 |
| Blocked by upstream dependency | bp.500, bp.700, bp.800, bp.810, bp.900 |
| Blocked decision | bp.600 |

## Stage 5 Audit Summary

| Process | Verdict | Reason |
|---------|---------|--------|
| bp.010 | P=0 | Token issue resolved, but refreshed D1 evidence shows People baseline drift and column-registry discrepancy. |
| bp.400 | P=1 D1 refresh | Token issue resolved; D1 DOL runtime tables confirmed non-zero and aligned to BAR-379/D1 dictionary surface. |
| bp.200 | P=1 repair | Local verification repair certified; fill-rate gap remains operational/enrichment work. |
| bp.201 | P=1 repair | Local execution repair certified; live backlog remains for controlled/scheduled processing. |
| bp.202 | P=1 repair | Local execution repair certified; live backlog remains for controlled/scheduled processing. |
| bp.300 | P=1 repair | Local active-script repair certified; older helper cleanup and scheduled rollout remain separate. |
| bp.301 | P=1 repair | Local active-script repair certified; Title Classifier wiring and scheduled rollout remain separate. |
| bp.820 | P=1 repair | Wrangler/D1/KV/schema repair certified; OPERATE promotion still requires live export run and blueprint confirmation. |

## Stage 2 Caveat

Stage 2 initially used the 2026-05-03 BAR-379 D1 live baseline plus 2026-05-04 source cron registry evidence. The first 2026-05-04 refresh attempt failed with Cloudflare API auth error 10000 because the wrong token variable was used. Later checks succeeded by mapping `GLOBAL_CLOUDFLARE_API_TOKEN` to `CLOUDFLARE_API_TOKEN`.

## Next Knockout

Stage 5 audit was run for no-op candidates bp.010 and bp.400 before the token correction; bp.400 is now refreshed to P=1 and bp.010 remains P=0 due real live drift. bp.200, bp.201, bp.202, bp.300, bp.301, and bp.820 local repairs are now audit-certified. Next knockout is bp.500 or bp.830 triage, while bp.100 remains blocked by source drift and bp.600 remains a decision blocker.

## Controls

- Process YAMLs stay in each process UT folder.
- This index only references artifacts; it does not create loose workflow YAMLs.
- A process is not green until live state and Codex audit are present.

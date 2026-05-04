# Inventory - bp.600 BIT Scoring

Date: 2026-05-04
BAR: BAR-377
Stage: 1 - INVENTORY
Mode: read-only source inventory

## Verdict

Stage 1 inventory generated. This is not a live-state audit and does not certify OPERATE.

## Identity

| Field | Value |
|-------|-------|
| Dewey | bp.600 |
| Process Number | 600 |
| Process Name | BIT Scoring |
| Silo | outreach |
| Folder | $(System.Collections.Hashtable.folder)/ |
| ORBT From INDEX | TROUBLESHOOT_TRAIN |
| Deployable | No |
| Mission Control Page | Watch Tower |
| Depends On | 200, 300, 400, 500 |

## Source Artifacts

| Artifact | Path | Status | Notes |
|----------|------|--------|-------|
| PROCESS-UT | $(System.Collections.Hashtable.folder)/PROCESS-UT.md | FOUND | UT section markers observed: 14; checklist: present |
| Workflow YAML | $(System.Collections.Hashtable.folder)/workflow.yaml | FOUND | Workflow name: $workflowName |
| Plan Book | imo-creator-v2/docs/plans/PLAN-BP-600-BIT-SCORING.md | FOUND | $planTitle |
| INDEX row | Barton-Processes/INDEX.md | FOUND | Source for ORBT, deployable, MC page |
| Execution order row | Barton-Processes/EXECUTION_ORDER.md | FOUND | Source for dependency order |

## Stage 1 Findings

| ID | Severity | Finding | Route |
|----|----------|---------|-------|
| INV-600-01 | INFO | Source inventory exists for bp.600; live runtime state not checked in Stage 1. | Stage 2 live-state audit |
| INV-600-02 | INFO | workflow.yaml present. | Stage 2 live-state audit |
| INV-600-03 | INFO | Per-process Plan Book present. | Use for BAR-377 dispatch |
| INV-600-04 | RED | ORBT is TROUBLESHOOT_TRAIN, so this process cannot be treated as green without repair/audit. | Planner routes repair BAR |

## Required Next Artifact

- live-state-bp-600.md - Stage 2 live introspection.
- diff-bp-600.md - Stage 3 Planner diff after live evidence.
- udit-bp-600.md - Stage 5 Codex audit after repair or no-op verification.

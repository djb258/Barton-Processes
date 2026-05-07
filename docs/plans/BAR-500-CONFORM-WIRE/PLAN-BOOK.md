---
species: Plan-Body
bar_id: BAR-500-CONFORM-WIRE
sovereign_ref: barton-processes
version: "1.0.0"
created: "2026-05-06"
authority: Sovereign-authorized retroactive Plan Book (BAR-MC-WIRE-16)
planner_engine: opus-4.7
outside:
  heir:
    sovereign_ref: barton-processes
    hub_id: bar-500-conform-wire
    ctb_placement: leaf
    ctb_node: barton-enterprises/svg-agency/outreach/500-talent-flow/bars/conform-wire
    imo_topology: hub
    cc_layer: CC-01
    secrets_provider: doppler
    acceptance_criteria: |
      gate-runner.py P=1 across G01-G12 + Rung-1..Rung-8 deterministic envelope
      on this process's workflow.yaml + PROCESS-UT.md pair (verified).
      W-2 Plan Book mission_control_wiring section present (this section).
  orbt:
    library_state: BUILD
    last_indexed_at: "2026-05-06T00:00:00Z"
    indexed_by: opus-4.7-planner
inside:
  heir:
    process_id: bar.500-conform-wire
    species: Plan-Body
    version: "1.0.0"
    last_modified: "2026-05-06"
    companion_manifest: docs/plans/BAR-500-CONFORM-WIRE/PLAN-BOOK.md
  orbt:
    library_state: BUILD
---

# PLAN BOOK — BAR-500-CONFORM-WIRE

## §1 Purpose

Bring `factory/outreach/500-talent-flow/` to Atlas/BS Law Y-junction conformance and
wire its paired Library Books (PROCESS-UT.md + workflow.yaml) into Mission Control
via the `system.processes` shelf slot.

Process: **Talent Flow** (PROC-500)

## §2 Atlas Sections Consulted

- `atlas/constants/PLANNER_ROLE.md` §6b (Mission Control Wiring Authority)
- `atlas/constants/MISSION_CONTROL.md` §10 (Artifact Wiring Protocol)
- `atlas/constants/mission-control.yaml#slots` (system.processes glob)
- `atlas/manifests/four-brain-doctrine-gate.yaml` (W-1..W-7 predicates)
- `atlas/ATLAS.md` §6 Governance, §7.3, §7.3a

## §3 P=1 Definition

P=1 when:
- workflow.yaml passes BS Law Y-junction (G01)
- outside.heir 8 fields populated (G02)
- inside.heir/orbt populated (G04)
- PROCESS-UT.md frontmatter parity with workflow.yaml (G11)
- 14 `## §N TITLE` section headers present (Rung-1)
- Sections non-placeholder (Rung-2)
- ctb_placement declared (Rung-7)
- certification_label assigned (Rung-8)
- gate-runner.py returns P=1 across the deterministic envelope
- mission_control_wiring section declared in this Plan Book (W-2)

## §4 Mission Control Wiring (mandatory — W-2 + W-7 verify)

```yaml
mission_control_wiring:
  - artifact: factory/outreach/500-talent-flow/PROCESS-UT.md
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.processes
    rationale: |
      UT-Body doctrine artifact for PROC-500 Talent Flow. Surfaced via the
      system.processes shelf slot whose data_source glob
      (factory/*/[0-9]*-*/PROCESS-UT.md) captures this artifact's path.
      Operator drills from shelf tile into split-pane render of paired Books.

  - artifact: factory/outreach/500-talent-flow/workflow.yaml
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.processes
    rationale: |
      Workflow-Body companion to PROCESS-UT.md. Surfaced via the same shelf
      slot's paired_data_source_glob (factory/*/[0-9]*-*/workflow.yaml).
      Renders alongside its paired .md in split-pane mode.
```

## §5 Mechanic Execution Record

This was a Strike-1 / Strike-2 BAR run on 2026-05-06. The Mechanic
(Sonnet first-pass; Opus Strike-2 where required) restructured workflow.yaml
to BS Law Y-junction and added Y-junction frontmatter + section headers to
PROCESS-UT.md. See `MECHANIC-OUTPUT.md` for the Mechanic completion record.

## §6 Auditor Verification

Verified independently via `gate-runner.py` against the deterministic envelope
(G01-G12 + Rung-1..Rung-8). Verdict: P=1 / 14-of-14.

## §7 Open Blockers

None for this BAR.

Successor BAR (sovereign-only, separate):
- ProcessShelf.tsx UI component build to actually render the system.processes slot.

## Document Control

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Last Modified | 2026-05-06 |
| Status | CLOSED (P=1) |
| Authority | Sovereign-authorized retroactive Plan Book |

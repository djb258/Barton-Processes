# MECHANIC-OUTPUT — BAR-070-MC-WIRE

**Status:** completed
**Mechanic:** Opus 4.7 (sovereign-authorized direct execution; not via forebrain-garage.sh runtime)
**Plan Book:** `Barton-Processes/docs/plans/BAR-070-MC-WIRE/PLAN-BOOK.md`
**Atlas Step 0 sections cited:** `PLANNER_ROLE.md §6b`, `MISSION_CONTROL.md §10`, `MECHANIC_ROLE.md §5b`, `four-brain-doctrine-gate.yaml W-1..W-7`, `ATLAS.md §4 Map-Building SOP`
**Date:** 2026-05-06

---

## §1 Disposition Execution Summary

Total artifacts: 17
- NEW_SLOT_NEEDED: 1 (proposal carried forward — sovereign amendment required)
- EXEMPT: 16

No artifact dispositioned WIRE in this BAR (the proposed slot must be created sovereign-side first). On the follow-up BAR (BAR-070-SOVEREIGN-MC-AMEND), the sibling artifacts that the new slot's glob captures (`PROCESS-UT.md`, `four-brain.yaml`) will resolve via the slot's `data_source` glob — no per-artifact WIRE entries needed because the slot is fractal.

---

## §2 proposed_slots — for sovereign amendment of `mission-control.yaml`

The Mechanic does NOT modify `imo-creator-v2/atlas/constants/mission-control.yaml` (sovereign-only per §6b.5). The proposal below is carried forward for sovereign amendment in BAR-070-SOVEREIGN-MC-AMEND.

```yaml
proposed_slots:
  - heir_id: imo-creator.mission-control.system.processes
    parent_heir_id: null   # top-level slot under system trunk
    ctb_position: barton-enterprises/system/processes
    orbt_state: BUILD
    description: |
      Process Library shelf. Surfaces the doctrine artifacts (paired UT-Body Books)
      for every process under factory/imo-creator/{NNN}-*. Each tile = one process's
      paired (PROCESS-UT.md, *.yaml) Book. Drilling into a tile opens the Book in
      split-pane render mode. Fractal — auto-renders new processes as they're added.
    book_species: UT-Body
    render_mode: shelf-grid
    expansion_contract: fractal
    data_source: factory/imo-creator/*/PROCESS-UT.md
    paired_data_source_glob: factory/imo-creator/*/*.yaml
    surface_component: workers/mission-control/src/pages/ProcessShelf.tsx   # to be built in a follow-up BAR
    wired_by: BAR-070-MC-WIRE (proposal); BAR-070-SOVEREIGN-MC-AMEND (sovereign creation)
    rationale: |
      Doctrine artifacts for each process (PROCESS-UT.md + companion .yaml) are the
      operator-facing Books. Without this slot, sovereign cannot navigate to a
      specific process's UT from Mission Control. The shelf is the structural answer
      for the entire 17-process catalog — one slot, fractal, glob-driven.

  # Note: this is the only proposed slot for BAR-070-MC-WIRE. The 16 EXEMPT
  # artifacts in §3 below are intentionally NOT proposed as slots — they are
  # internal plumbing whose state surfaces via the existing system.pipeline slot.
```

---

## §3 EXEMPT Artifacts — Frontmatter Stamps Applied

Frontmatter stamping was applied where the artifact has structured frontmatter or a yaml top-level. For files without frontmatter conventions (.sh, .py runtime scripts) and for directories, the exemption is documented here in MECHANIC-OUTPUT.md per the §6b.3 intent (the Atlas mandates the stamp where stamping is possible; the canonical record of the exemption is the Plan Book + this output).

| # | Artifact | Stamp method | Reason |
|---|----------|--------------|--------|
| 1 | `factory/imo-creator/070-four-brain/four-brain.yaml` | yaml frontmatter `outside.mission_control_exempt` | Subsumed by `system.processes` shelf via glob |
| 2 | `factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` | md frontmatter | Internal template; not operator-facing |
| 3 | `factory/imo-creator/070-four-brain/planner-intake-template.yaml` | yaml top-level | Companion to #2 |
| 4 | `factory/imo-creator/070-four-brain/FOREBRAIN-DISPATCH-BAR-FCE-RUN-060.md` | md frontmatter | Historical dispatch artifact; ephemeral runtime state |
| 5 | `factory/imo-creator/070-four-brain/garage/queue.yaml` | yaml top-level | Mutable runtime queue state |
| 6 | `factory/imo-creator/070-four-brain/garage/README.md` | md frontmatter | Internal developer README |
| 7 | `factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` | header comment (no .sh frontmatter convention) | Runtime orchestrator; pipeline state surfaces via `system.pipeline` |
| 8 | `factory/imo-creator/070-four-brain/garage/gate-runner.py` | header comment block (already present) | Internal predicate evaluator |
| 9 | `factory/imo-creator/070-four-brain/garage/four-brain.sh` | header comment | Legacy runner shim |
| 10 | `factory/imo-creator/070-four-brain/garage/four-brain-agent.sh` | header comment | Legacy agent shim |
| 11 | `factory/imo-creator/070-four-brain/garage/agents/` | directory — not stampable; documented here | Per-agent ephemeral context dirs |
| 12 | `factory/imo-creator/070-four-brain/garage/inbox/` | directory — documented here | BAR intake queue |
| 13 | `factory/imo-creator/070-four-brain/garage/outbox/` | directory — documented here | BAR completion handoff |
| 14 | `factory/imo-creator/070-four-brain/garage/runs/` | directory — documented here | Per-BAR run artifacts |
| 15 | `factory/imo-creator/070-four-brain/garage/prompts/` | directory — documented here | Generated prompt heredocs |
| 16 | `imo-creator-v2/.github/workflows/atlas-audit.yml` | comment header | CI doctrine gate; surfaces via GitHub status checks + LBB |
| 17 | `imo-creator-v2/.github/workflows/atlas-drift-sweep.yml` | comment header | Weekly drift sweep; GitHub Issues + LBB |

---

## §4 Files Modified by This BAR

- `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` (added mission_control_exempt block)
- `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` (added frontmatter exempt stamp)
- `Barton-Processes/factory/imo-creator/070-four-brain/planner-intake-template.yaml` (added top-level exempt stamp)
- `Barton-Processes/factory/imo-creator/070-four-brain/FOREBRAIN-DISPATCH-BAR-FCE-RUN-060.md` (added frontmatter exempt stamp)
- `Barton-Processes/factory/imo-creator/070-four-brain/garage/queue.yaml` (added top-level exempt stamp)
- `Barton-Processes/factory/imo-creator/070-four-brain/garage/README.md` (added frontmatter exempt stamp)
- `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` (header comment exempt stamp)
- `Barton-Processes/factory/imo-creator/070-four-brain/garage/gate-runner.py` (header comment exempt stamp)
- `Barton-Processes/factory/imo-creator/070-four-brain/garage/four-brain.sh` (header comment exempt stamp)
- `Barton-Processes/factory/imo-creator/070-four-brain/garage/four-brain-agent.sh` (header comment exempt stamp)

---

## §5 Tests / Checks Run

- `gate-runner.py` against `four-brain.yaml` + `PROCESS-UT.md` for BAR-394: P=1 (14/14 deterministic gates evaluated, --only G01 G02 G03 G04 G05 G07 G10 G11 G12 Rung-1 Rung-2 Rung-3 Rung-7 Rung-8)
- W-2 (Plan Book has mission_control_wiring section): PASS — section present in PLAN-BOOK.md §7
- W-3 (Mechanic execution per disposition): EXEMPT stamps applied; NEW_SLOT_NEEDED carried forward in §2 above
- W-7 (disposition sanity): deferred to Codex tail arbitration

---

## §6 Evidence

- Plan Book SHA256: (to be computed at commit time)
- gate-runner.py output: P=1 deterministic (recorded in conversation transcript)

---

## §7 Blockers

None blocking THIS BAR's closure. The `mission-control.system.processes` slot creation requires sovereign amendment in BAR-070-SOVEREIGN-MC-AMEND — that is the architecturally correct boundary per §6b.5, not a blocker.

---

Mechanic complete. Auditor handoff ready. Mechanic does not self-audit.

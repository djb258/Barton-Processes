---
species: Plan-Body
bar_id: BAR-070-MC-WIRE
sovereign_ref: imo-creator
version: "1.0.0"
created: "2026-05-06"
authority: Sovereign-authorized direct dispatch (no template intake required)
planner_engine: opus-4.7
outside:
  heir:
    sovereign_ref: imo-creator
    hub_id: bar-070-mc-wire
    ctb_placement: leaf
    ctb_node: barton-enterprises/imo-creator/processes/four-brain/bars/070-mc-wire
    imo_topology: hub
    cc_layer: CC-01
    secrets_provider: doppler
    acceptance_criteria: |
      mission_control_wiring section covers every 070 artifact; each disposition
      defensible per W-7; Mechanic executes deterministically; Auditor (gate-runner.py
      + Codex W-7) returns P=1.
  orbt:
    library_state: BUILD
    last_indexed_at: "2026-05-06T00:00:00Z"
    indexed_by: opus-4.7-planner
inside:
  heir:
    process_id: bar.070-mc-wire
    species: Plan-Body
    version: "1.0.0"
    last_modified: "2026-05-06"
    companion_manifest: Barton-Processes/docs/plans/BAR-070-MC-WIRE/PLAN-BOOK.md
  orbt:
    library_state: BUILD
---

# PLAN BOOK — BAR-070-MC-WIRE

## §1 Purpose

Wire all 070 Four-Brain artifacts into Mission Control per Atlas §10 Artifact Wiring Protocol + PLANNER_ROLE.md §6b. Establish the wiring template for the next 16 processes.

## §2 Atlas Sections Consulted

- `atlas/constants/PLANNER_ROLE.md` §6b (Mission Control Wiring Authority)
- `atlas/constants/MISSION_CONTROL.md` §10 (Artifact Wiring Protocol)
- `atlas/constants/mission-control.yaml#slots` (existing slot registry)
- `atlas/constants/UI_STYLE_GUIDE.md` (render mode catalog)
- `atlas/manifests/four-brain-doctrine-gate.yaml` (W-1..W-7 predicates the Auditor will run)
- `atlas/ATLAS.md` §1 Legend, §4 Map-Building SOP, §6 Governance, §7.3, §7.3a

## §3 Source-of-Truth Split

| Concern | Authoritative location |
|---|---|
| Slot registry | `imo-creator-v2/atlas/constants/mission-control.yaml#slots` |
| Render mode catalog | `imo-creator-v2/atlas/constants/UI_STYLE_GUIDE.md` |
| Process doctrine artifacts | `Barton-Processes/factory/imo-creator/{NNN}-*/` |
| Runtime state | `mission-control-api` D1 + `mc-proxy` worker |
| LBB rows for wiring transitions | `lbb.records` worker (subject_id `processes` for execution rows) |

## §4 P=1 Definition

P=1 when ALL of the following hold simultaneously:
- Every 070 artifact listed in §7 has a disposition assigned (no defaults, no silence — W-2)
- Every disposition is defensible against the W-7 sanity check (no EXEMPT stamps a sovereign would dispute)
- Mechanic executes per disposition: WIRE updates target slot's data_source; EXEMPT stamps frontmatter; NEW_SLOT_NEEDED emits proposal in MECHANIC-OUTPUT.md (no auto-create)
- `gate-runner.py` returns PASS for G01-G12 + W-1..W-6 + Rung-1..Rung-8 against this BAR's outputs
- Codex returns PASS on W-7 (disposition sanity)
- LBB has rows tagged `mission-control-wiring` / `mission-control-exempt` / `mission-control-new-slot-needed` for each artifact (W-5)

## §5 Stop Conditions

- Foreman dispatch missing from Mechanic input → STOP (Mechanic emits PLAN_BOOK_INCOMPLETE)
- Mechanic attempts to add new slot to mission-control.yaml → STOP (sovereign-only per §6b.5)
- Auditor returns FAIL → Strike-1 → repair → re-audit
- Strike-3 same root cause → Troubleshoot/Train

## §6 Mechanic Dispatch Requirements

### Allowed write scope

| Path | What Mechanic may do |
|---|---|
| `Barton-Processes/factory/imo-creator/070-four-brain/**` | Stamp `mission_control_exempt: true` + `mission_control_exempt_reason: <text>` in EXEMPT artifact frontmatter |
| `<run_dir>/MECHANIC-OUTPUT.md` | Emit `proposed_slots:` block listing the NEW_SLOT_NEEDED proposal verbatim |
| LBB row writes via `scripts/lbb-log.sh` | Emit one row per artifact with appropriate tag |

### Forbidden paths

| Path | Why |
|---|---|
| `imo-creator-v2/atlas/constants/mission-control.yaml` | Sovereign-only amendment (§6b.5) |
| `imo-creator-v2/atlas/constants/MISSION_CONTROL.md` | Sovereign-only |
| Any of the 17 sovereign-locked constants | Per Atlas §7 |

## §7 Mission Control Wiring (mandatory — W-2 + W-7 verify)

```yaml
mission_control_wiring:

  # ============================================================
  # NEW SLOT — process catalog (the structural answer for all 17 processes)
  # ============================================================
  - artifact: factory/imo-creator/070-four-brain/PROCESS-UT.md
    disposition: NEW_SLOT_NEEDED
    proposed_slot:
      heir_id: imo-creator.mission-control.system.processes
      ctb_position: barton-enterprises/system/processes
      render_mode: shelf-grid
      data_source: factory/imo-creator/*/PROCESS-UT.md
      expansion_contract: fractal
      book_species: UT-Body
      description: |
        Process Library shelf — surfaces all process doctrine artifacts (PROCESS-UT.md
        Books) across factory/imo-creator/*. Drilling into a tile opens the paired
        UT-Body view via book_renderer.modes.split-pane (.md left, .yaml right).
        Fractal — child slots auto-render as each new process is added (PROC-070,
        PROC-080, PROC-090, ...).
    rationale: |
      The first artifact dispositioned because it justifies the slot. The other 070
      doctrine artifacts (four-brain.yaml + planner-intake template pair) are subsumed
      by this slot's glob via the paired-artifacts.yaml registry — the shelf renders
      paired Books together. EXEMPT-as-subsumed used for siblings.

  # Doctrine companions to PROCESS-UT.md — subsumed by the proposed shelf slot
  - artifact: factory/imo-creator/070-four-brain/four-brain.yaml
    disposition: EXEMPT
    rationale: |
      Subsumed by imo-creator.mission-control.system.processes — the shelf renders
      paired Books (.md + .yaml) together via paired-artifacts.yaml registry. No
      separate slot needed.

  - artifact: factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md
    disposition: EXEMPT
    rationale: |
      Internal template artifact — defines the intake YAML format used by the
      Four-Brain pipeline. Not operator-facing content; the runtime pipeline
      observer (system.pipeline slot) shows intake state.

  - artifact: factory/imo-creator/070-four-brain/planner-intake-template.yaml
    disposition: EXEMPT
    rationale: |
      Companion to PLANNER-INTAKE-TEMPLATE.md; same exemption.

  - artifact: factory/imo-creator/070-four-brain/FOREBRAIN-DISPATCH-BAR-FCE-RUN-060.md
    disposition: EXEMPT
    rationale: |
      Historical dispatch artifact for a prior BAR (FCE-RUN-060). Stale runtime
      state, not doctrine. No operator value in surfacing this.

  # ============================================================
  # RUNTIME PLUMBING — pipeline observability handled by system.pipeline slot
  # ============================================================
  - artifact: factory/imo-creator/070-four-brain/garage/forebrain-garage.sh
    disposition: EXEMPT
    rationale: |
      Internal runtime orchestrator (956 lines bash). Executes the Four-Brain
      pipeline. Operator visibility into pipeline state is provided by the existing
      imo-creator.mission-control.system.pipeline slot. The script itself is plumbing.

  - artifact: factory/imo-creator/070-four-brain/garage/gate-runner.py
    disposition: EXEMPT
    rationale: |
      Deterministic gate evaluator. Outputs flow into Auditor verdicts which surface
      via system.pipeline. The runner itself is internal predicate evaluation; not
      operator-visible.

  - artifact: factory/imo-creator/070-four-brain/garage/four-brain.sh
    disposition: EXEMPT
    rationale: |
      Legacy runner shim; superseded by forebrain-garage.sh. Plumbing.

  - artifact: factory/imo-creator/070-four-brain/garage/four-brain-agent.sh
    disposition: EXEMPT
    rationale: |
      Legacy agent dispatch shim; superseded. Plumbing.

  - artifact: factory/imo-creator/070-four-brain/garage/queue.yaml
    disposition: EXEMPT
    rationale: |
      Runtime queue state for in-flight BARs. Surfaced via system.pipeline slot's
      flow render. The file itself is mutable runtime state, not a Library Book.

  - artifact: factory/imo-creator/070-four-brain/garage/README.md
    disposition: EXEMPT
    rationale: |
      Internal developer README for the garage. Not operator-facing.

  - artifact: factory/imo-creator/070-four-brain/garage/agents/
    disposition: EXEMPT
    rationale: |
      Agent role working directories (planner/foreman/mechanic/auditor). Per-agent
      ephemeral context state — not Library artifacts. Pipeline observability
      already covered by system.pipeline slot.

  - artifact: factory/imo-creator/070-four-brain/garage/inbox/
    disposition: EXEMPT
    rationale: |
      BAR intake queue. Ephemeral runtime state. Surfaced via system.pipeline.

  - artifact: factory/imo-creator/070-four-brain/garage/outbox/
    disposition: EXEMPT
    rationale: |
      BAR completion handoff queue. Ephemeral runtime state.

  - artifact: factory/imo-creator/070-four-brain/garage/runs/
    disposition: EXEMPT
    rationale: |
      Per-BAR run artifacts. Ephemeral; pipeline state surfaced via system.pipeline.

  - artifact: factory/imo-creator/070-four-brain/garage/prompts/
    disposition: EXEMPT
    rationale: |
      Generated prompt heredocs per BAR. Ephemeral; not Library content.

  # ============================================================
  # CI WORKFLOWS — verdict surface is GitHub status checks + LBB rows
  # ============================================================
  - artifact: imo-creator-v2/.github/workflows/atlas-audit.yml
    disposition: EXEMPT
    rationale: |
      CI doctrine gate runner. Verdicts surface via GitHub PR status checks (BLOCK on
      P=0, no override per Atlas G10) and LBB rows tagged with the audit BAR ID. No
      Mission Control slot needed; the Library shelf renders LBB audit rows.

  - artifact: imo-creator-v2/.github/workflows/atlas-drift-sweep.yml
    disposition: EXEMPT
    rationale: |
      Weekly drift-sweep cron. Output flows to GitHub Issues + LBB rows. No MC slot needed.
```

## §8 Auditor Packet Requirements

The Auditor invokes:

```bash
python Barton-Processes/factory/imo-creator/070-four-brain/garage/gate-runner.py \
  --bar-id BAR-070-MC-WIRE \
  --audited-yaml Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml \
  --audited-md Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md \
  --output-format json \
  --deterministic-only
```

Then evaluates W-7 (disposition sanity) for each entry in §7 above. Verdict is PASS only if:
- Runner verdict = PASS on G01-G12 + W-1..W-6 + Rung-1..Rung-8
- W-7 = PASS for every artifact disposition

## §9 LBB Row Schema for This BAR

Each Mechanic transition writes one row per artifact with:
- `subject_id`: `processes`
- `bar_id`: `BAR-070-MC-WIRE`
- `tags`: `mission-control-wiring` / `mission-control-exempt` / `mission-control-new-slot-needed` (per disposition)
- `notes`: artifact path (so W-5 can verify per-artifact coverage)

## §10 Open Blockers

None for dispatch. The NEW_SLOT_NEEDED proposal will be carried forward in MECHANIC-OUTPUT.md for sovereign amendment in a follow-up sovereign-only BAR (per §6b.5).

## §11 Successor BARs

After this BAR closes:

1. **BAR-070-SOVEREIGN-MC-AMEND** (sovereign-only) — Sovereign amends `imo-creator-v2/atlas/constants/mission-control.yaml` to add the proposed `system.processes` slot. Sovereign also decides on the still-halted `system.pipeline` slot's CN-2 binding (Option A: routes in mission-control-api; Option B: D1 in mc-proxy).

2. **BAR-08X-MC-WIRE through BAR-XXX-MC-WIRE** (one per process) — Same template as this Plan Book applied to processes 080, 090, ... up to the full 17-process catalog. Each BAR carries the same disposition pattern (NEW_SLOT_NEEDED for the first artifact if no slot exists, EXEMPT for plumbing, WIRE for content slots).

## Document Control

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Last Modified | 2026-05-06 |
| Status | DISPATCHED |
| Authority | Sovereign-authorized direct dispatch |
| Planner | Opus 4.7 (this conversation) |
| Successor sovereign-BAR | BAR-070-SOVEREIGN-MC-AMEND |

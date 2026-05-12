---
species: Plan-Body
bar_id: BAR-FCE-PLANNER-GATE
sovereign_ref: imo-creator
version: "1.0.0"
created: "2026-05-08"
authority: Operator intake (Dave Barton sovereign) → Planner (Opus 4.7, collaborative)
planner_engine: opus-4.7
paired_md: PLAN-BOOK.md
mission_control_exempt: true
mission_control_exempt_reason: >
  Plan Book is a Four-Brain governance artifact, not a Library artifact.
  MC wiring instructions are carried inside §7 and executed by the Mechanic
  against individual target files. The Plan Book itself is exempt from
  indexing in Mission Control per BAR-070-MC-WIRE Plan Book §7.
outside:
  heir:
    sovereign_ref: imo-creator
    hub_id: bar-fce-planner-gate
    ctb_placement: leaf
    ctb_node: barton-enterprises/imo-creator/processes/four-brain/bars/fce-planner-gate
    imo_topology: hub
    cc_layer: CC-01
    services: cloudflare-d1,cloudflare-r2
    secrets_provider: doppler
    acceptance_criteria: |
      Planner gate validates every FCE intake against substrate-awareness checklist
      BEFORE engine inbox; PASS auto-bundles validated Plan Book to engine inbox;
      FAIL returns structured operator_fixes; sovereign_id threads I+M+O end-to-end
      through R2 workbench and D1 vault; D1 row queryable by sovereign_id returns
      validated intake + workbench pointer + final Book + audit cert in one row;
      Mission Control surfaces Planner queue + verdicts + bundle state; engine
      internals (us.py / up.py / K=C / DMJ) untouched (Coca-Cola seal); Auditor
      returns P=1 across G01-G12 + W-1..W-7.
  orbt:
    library_state: BUILD
    last_indexed_at: "2026-05-08T00:00:00Z"
    indexed_by: opus-4.7-planner
inside:
  heir:
    process_id: bar.fce-planner-gate
    species: Plan-Body
    version: "1.0.0"
    last_modified: "2026-05-08"
    companion_manifest: Barton-Processes/docs/plans/BAR-FCE-PLANNER-GATE/PLAN-BOOK.md
    aviation_model: four-brain
    determinism_gate: enforced
  orbt:
    library_state: BUILD
    runtime_state: BUILD
    strikes: 0
---

# PLAN BOOK — BAR-FCE-PLANNER-GATE

## §1 Purpose

Stand up an FCE Intake Planner gate as the first stop before the engine, positioned as a Four-Brain Planner specialization (tactical scope, Sonnet model). Close the Circle by threading one `sovereign_id` through I (validated intake) + M (R2 workbench evidence) + O (assembled Book + audit cert), so every D1 row carries its triggering input alongside its output and sigma is trackable across cycles for the first time.

**This BAR ships steps 6–8** of `PLANNER_GATE_BUILD_SPEC.yaml` v1.1.0 (steps 1–5 already built in-session: planner.py skeleton, queue infrastructure, dispatch_fce.py v1.1.0 sovereign_id mint, prompt hardening, FCE_DESCRIPTION_GUIDANCE.md mirrored). Engine internals stay sealed — wrapper layer only.

---

## §2 Atlas Sections Consulted

- `imo-creator-v2/atlas/constants/KEY.md` (vocabulary)
- `imo-creator-v2/atlas/ATLAS.md` §1 Legend, §4 Map-Building SOP, §4.5 Repair SOP, §6 Governance, §7.3, §7.3a
- `imo-creator-v2/atlas/constants/BS_LAW.md` v1.3.0 (Y-junction syntactic separation; outside.heir/orbt vs inside.heir/orbt as syntactically distinct top-level constructs)
- `imo-creator-v2/atlas/constants/BOOK_LAW.md` v1.5.0 (eleven body species; Plan-Body shape; Workflow-Body / Schema-Body / Code-Body / Config-Body manifestation specs)
- `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` #16 (role locks; determinism-first gate; strike system)
- `imo-creator-v2/atlas/constants/PLANNER_ROLE.md` §1, §4, §4.5, §6, §6b, §7.3, §7.3a (Mission Control Wiring Authority — W-2 + W-7 are Planner-accountability)
- `imo-creator-v2/atlas/constants/MISSION_CONTROL.md` §10 (artifact wiring protocol; three dispositions)
- `imo-creator-v2/atlas/constants/mission-control.yaml#slots` (slot registry — pickled WIRE targets verified)
- `imo-creator-v2/atlas/constants/UI_STYLE_GUIDE.md` (render-mode catalog for NEW_SLOT_NEEDED proposals)
- `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml` v1.2.0 (G01-G12 + W-1..W-7 predicates the Auditor will run)
- `imo-creator-v2/atlas/manifests/paired-artifacts.yaml` (paired Book registry)
- `Barton-Processes/factory/imo-creator/060-run-dyno/PLANNER_GATE_BUILD_SPEC.yaml` v1.1.0 (build steps + acceptance criteria)
- `Barton-Processes/factory/imo-creator/060-run-dyno/FCE_DESCRIPTION_GUIDANCE.md` (substrate-awareness rules the Planner enforces)
- `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` + `four-brain.yaml` (process doctrine)

---

## §3 Source-of-Truth Split

Preserved from intake. No relocations.

| Concern | Authoritative location |
|---|---|
| Atlas constants (locked, sovereign-only) | `imo-creator-v2/atlas/constants/` (17 locked) |
| Doctrine gate predicates | `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml` |
| FCE description rules | `Barton-Processes/factory/imo-creator/060-run-dyno/FCE_DESCRIPTION_GUIDANCE.md` (mirrored to dyno-engine) |
| Build spec | `Barton-Processes/factory/imo-creator/060-run-dyno/PLANNER_GATE_BUILD_SPEC.yaml` (mirrored to dyno-engine) |
| Engine internals (SEALED) | `dyno-engine/` private repo — `us.py`, `up.py`, `run_kc_audit.py`, `dyno_engine.py` |
| Wrapper layer (editable) | `imo-creator-v2/atlas/dyno/` — `dispatch_fce.py`, `run_fce.py`, `planner/` |
| Planner queue (operator drop) | `imo-creator-v2/atlas/dyno/planner/planner-queue/{processing,done,failed}/` |
| Engine inbox (sovereign_id mint) | `imo-creator-v2/atlas/dyno/inbox/{processing,done,failed}/` |
| R2 workbench evidence (M) | R2 bucket keyed by `sovereign_id` |
| D1 IMO bundles (O) | `mission-control-api` D1 — table to extend with intake column(s) |
| Mission Control slot registry | `imo-creator-v2/atlas/constants/mission-control.yaml#slots` (sovereign-only amendment) |
| LBB rows | `lbb.records` worker (subject_id `four-brain-gate-audit` for role transitions; subject_id `processes` for execution) |
| Process docs | `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` (UT-Body) + `four-brain.yaml` (Workflow-Body) |
| Plan Book (this artifact) | `Barton-Processes/docs/plans/BAR-FCE-PLANNER-GATE/PLAN-BOOK.md` |

**Connector / run binding (preserved):** Operator → `planner-queue/processing/` → `planner.py` (Sonnet 4.6) → on PASS → `inbox/processing/` → `dispatch_fce.py` (mints sovereign_id) → engine run → `dispatch_fce.py` bundles intake + workbench pointer + final Book + cert into D1 row keyed by `sovereign_id`. Mission Control reads via existing `mc-proxy`/`mission-control-api` data sources.

---

## §4 P=1 Definition (Stop Conditions)

P=1 when ALL of the following hold simultaneously, measured deterministically:

1. **Planner gate operational.** Operator drops intake → `planner.py` returns verdict in <2 min → on PASS the validated Plan Book is auto-bundled into engine inbox; on FAIL a structured failure report with non-empty `operator_fixes` is returned. Mechanical checks (deterministic) gate the LLM check; Sonnet only fires if mechanical passes (determinism-first).
2. **Role-lock enforced.** Once a Plan Book lands in `inbox/processing/`, `planner.py` has no write path back to it (filesystem permission or runtime guard, mechanic chooses).
3. **sovereign_id threading.** `dispatch_fce.py` mints `sovereign_id` at engine inbox claim and bundles the validated intake YAML alongside it; the same `sovereign_id` keys the R2 workbench dir and the D1 row.
4. **D1 IMO bundle column(s) live.** Schema migration applied; query `SELECT * FROM bundles WHERE sovereign_id = ?` returns intake YAML + R2 workbench pointer + final Book + audit cert in one row.
5. **Mission Control wired.** Planner queue + verdicts + bundle state surface via `mission_control_wiring` dispositions executed by Mechanic (per §7) — either WIRE to existing slots, or NEW_SLOT_NEEDED proposals carried in `MECHANIC-OUTPUT.md` (no skeleton auto-edit).
6. **LBB rows present.** Exactly four rows for this BAR (Planner verdict, Foreman dispatch, Mechanic edit, Auditor certify), schema valid per `lbb_row_schema` §8, `atlas_sections_consulted` non-empty on each, `gate_verdicts` JSON populated on the Auditor row only.
7. **Engine internals untouched.** Diff against `dyno-engine/` shows zero edits to `us.py`, `up.py`, `run_kc_audit.py`, `dyno_engine.py`. Coca-Cola seal preserved.
8. **Doctrine gate passes.** `gate-runner.py` returns PASS on all 19 gates: G01-G12 (Y-junction + LBB schema + CI/drift) and W-1..W-7 (Mission Control wiring including W-2 Plan Book section presence and W-7 disposition sanity).
9. **BS Law fires once at end of pipeline.** Assembled bundle (intake + workbench evidence + final Book + cert) carries the outside.heir/orbt + inside.heir/orbt Y-junction as syntactically distinct top-level constructs. Mid-pipeline engine outputs (us.json, kc-audit.json, etc.) remain plain stamped JSON — NOT BS-Law-compliant Books — per intake constraint O4.

**Stop conditions (halt + escalate):**

- Operator intake YAML missing required fields (`domain_string`, `p1_definition`, `family`, inside/outside HEIR) → Planner returns FAIL with `operator_fixes`; do NOT proceed.
- Mechanic detects ambiguous or missing disposition for any artifact in §7 → halt with `PLAN_BOOK_INCOMPLETE` strike → return to Planner for correction.
- Mechanic attempts to add/modify slots in `mission-control.yaml` without sovereign amendment → halt (W-6 violation; sovereign-only).
- Mechanic attempts to edit any file under `dyno-engine/` → halt (Coca-Cola seal violation).
- Auditor returns FAIL → Strike-1 → Mechanic repair → re-audit. Strike-2 → escalate to Opus mechanic. Strike-3 → Troubleshoot/Train, NOT another repair (PLANNER_ROLE.md §7); Plan Book itself is suspect.

---

## §5 Mechanic Dispatch Requirements

### §5.1 Literal work orders (in order)

**WO-1 — Extend `dispatch_fce.py` to bundle validated intake (Step 7 of build spec)**

- Path: `imo-creator-v2/atlas/dyno/dispatch_fce.py` (modify)
- Required behavior:
  - On engine inbox claim, after minting `sovereign_id`, copy the validated intake YAML from `inbox/processing/<file>.yaml` into the R2 workbench dir at key `<sovereign_id>/00-intake.yaml`.
  - Persist `sovereign_id ↔ intake_path` association in the workbench manifest (`<sovereign_id>/manifest.json`).
  - At end of run, when assembling the D1 bundle row, include `intake_yaml` (full validated YAML body) and `workbench_pointer` (R2 path) alongside existing `final_book` and `audit_cert` columns.
- Forbidden: any edit to `us.py`, `up.py`, `run_kc_audit.py`, `dyno_engine.py`, or any file inside `dyno-engine/`.

**WO-2 — D1 schema migration for IMO bundle (Step 8 of build spec)**

- Path: `imo-creator-v2/migrations/<NNN>-fce-imo-bundle.sql` (new file; numbering = next sequential)
- Required behavior: add columns to the existing FCE bundle table:
  - `intake_yaml TEXT NOT NULL` (full validated intake body)
  - `workbench_pointer TEXT NOT NULL` (R2 path keyed by sovereign_id)
  - `intake_validated_at TEXT NOT NULL` (ISO 8601 UTC)
  - `planner_verdict TEXT NOT NULL CHECK (planner_verdict IN ('PASS','FAIL'))`
- Backfill: existing rows pre-Planner-gate get `planner_verdict='PASS'` with `intake_yaml='<legacy: pre-planner-gate>'` and `workbench_pointer=NULL`.
- Mechanic confirms migration applies cleanly to staging D1 before declaring done.

**WO-3 — Mission Control wiring execution (Step 6 of build spec)**

- Per `MISSION_CONTROL.md` §10 + this Plan Book §7. For each artifact in §7:
  - WIRE → update target slot's `data_source` field in `mission-control.yaml` if Mechanic has authority (see W-6: Mechanic does NOT auto-amend skeleton; if a `data_source` change requires skeleton amendment, emit proposal in MECHANIC-OUTPUT.md instead).
  - EXEMPT → stamp `mission_control_exempt: true` + `mission_control_exempt_reason` in artifact frontmatter (only if artifact has frontmatter; otherwise carry as note).
  - NEW_SLOT_NEEDED → emit `proposed_slots:` block in `MECHANIC-OUTPUT.md` with full HEIR ID + CTB position + render mode + data source contract. **Mechanic does NOT add slots to `mission-control.yaml` — sovereign amendment only.**

**WO-4 — LBB row emission**

- Mechanic writes one LBB row at completion of WO-1 + WO-2 + WO-3 with:
  - `role: mechanic`, `bar_id: BAR-FCE-PLANNER-GATE`
  - `atlas_sections_consulted: "§4.5,§6,§7.3,§7.3a"` minimum
  - `evidence_hash`: SHA256 of `MECHANIC-OUTPUT.md`
  - `tags`: `[mission-control-wiring, mission-control-exempt, mission-control-new-slot-needed]` as applicable
- Foreman, Planner, Auditor each write their own LBB row per `four-brain-doctrine-gate.yaml` lbb section (4 rows total per G08).

**WO-5 — Process doc updates**

- Update `Barton-Processes/factory/imo-creator/060-run-dyno/run-dyno.yaml` to reflect Planner gate as Step 0 (operator → planner-queue) BEFORE engine inbox claim. Workflow-Body shape per Book Law v1.3.0 (outside/inside Y-junction as distinct top-level maps).
- Update `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` §3/§4 to reference the FCE specialization Planner under tactical altitude.

### §5.2 Allowed write scope (whitelist)

| Path | Reason |
|---|---|
| `imo-creator-v2/atlas/dyno/dispatch_fce.py` | WO-1 |
| `imo-creator-v2/atlas/dyno/planner/**` | residual cleanup if step-1/2 build needs touch-up |
| `imo-creator-v2/atlas/dyno/run_fce.py` | wrapper-layer touch-ups only if WO-1 requires |
| `imo-creator-v2/migrations/<NNN>-fce-imo-bundle.sql` | WO-2 (new file) |
| `Barton-Processes/factory/imo-creator/060-run-dyno/run-dyno.yaml` | WO-5 |
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` | WO-5 |
| `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` | WO-5 if needed for Y-junction parity |
| `Barton-Processes/docs/plans/BAR-FCE-PLANNER-GATE/MECHANIC-OUTPUT.md` | WO-3 NEW_SLOT_NEEDED proposals + run summary |
| LBB ingestion via `scripts/lbb-log.sh` | WO-4 |

### §5.3 Forbidden paths (hard block)

| Path | Reason |
|---|---|
| `dyno-engine/**` (entire repo) | Coca-Cola seal — engine internals sealed |
| `imo-creator-v2/atlas/constants/**` | 17 locked constants — sovereign-only amendment via `pending-atlas-updates/` |
| `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml` | sovereign-locked; Mechanic instance refactors only via separate sovereign-signed BAR |
| `imo-creator-v2/atlas/constants/mission-control.yaml` (slot registry) | W-6 — Mechanic NEVER adds/removes/renames slots; data_source updates only if §7 disposition explicitly says WIRE; otherwise NEW_SLOT_NEEDED proposal in MECHANIC-OUTPUT.md |

### §5.4 Determinism-first gate

The Planner gate's mechanical checks (field separation, no Connection-as-4th-primitive, substantive length, em-dash format) MUST execute first and short-circuit on any failure. Sonnet judgment calls (Things named, Flows named, Changes named, no solutions pre-loaded) fire ONLY if mechanical checks pass. LLM is the tail; never the spine. This Plan Book REJECTS any Mechanic implementation that places the Sonnet call before the mechanical block.

---

## §6 Auditor Packet Requirements

Auditor (Codex, distinct engine from Mechanic Sonnet/Opus per Aviation Model) runs against this BAR:

### §6.1 Gates that apply (all 19)

**G01–G12 (Doctrine):**
- G01 Y-junction syntactic separation (this Plan Book frontmatter; run-dyno.yaml; four-brain.yaml; PROCESS-UT.md frontmatter)
- G02 outside.heir 8 fields non-null
- G03 outside.orbt library_state in enum
- G04 inside.heir + inside.orbt present and populated
- G05 lbb_row_schema 12 mandatory fields present in any new LBB-consuming code
- G06 atlas_sections_consulted non-empty on all 4 LBB rows
- G07 gate spec source-of-truth (CI workflow references `four-brain-doctrine-gate.yaml`, no inline predicates)
- G08 LBB row count = 4 per BAR (Planner, Foreman, Mechanic, Auditor)
- G09 LBB row schema valid across all 4 rows
- G10 CI gate active (`atlas-audit.yml` triggers on PR)
- G11 parity sha256 match (paired .md/.yaml frontmatter — applies to run-dyno.yaml + run-dyno.md if paired; PROCESS-UT.md + four-brain.yaml)
- G12 drift sweep active

**W-1 to W-7 (Mission Control Wiring):**
- W-1 every produced/modified artifact has a HEIR ID
- W-2 [PLANNER STRIKE TARGET] this Plan Book contains a `mission_control_wiring` section listing every produced/modified artifact with disposition (WIRE | EXEMPT | NEW_SLOT_NEEDED) — see §7
- W-3 Mechanic executed declared disposition exactly (no judgment calls)
- W-4 paired-artifacts.yaml updated for any new paired Books
- W-5 LBB row tagged `mission-control-wiring` / `mission-control-exempt` / `mission-control-new-slot-needed` per artifact
- W-6 [MECHANIC STRIKE TARGET] Mechanic did NOT modify mission-control.yaml or MISSION_CONTROL.md without sovereign amendment
- W-7 [PLANNER STRIKE TARGET] disposition sanity check — Auditor evaluates each disposition in §7 for defensibility

### §6.2 Audit packet contents (Mechanic delivers; Auditor reads)

- This Plan Book (`PLAN-BOOK.md` + frontmatter Y-junction)
- `MECHANIC-OUTPUT.md` (run summary + `proposed_slots:` block + diff list of all touched files)
- Diff/patch listing for WO-1, WO-2, WO-5 (with engine-internals exclusion proof)
- Migration apply log (WO-2 staging D1 confirmation)
- LBB rows for this BAR (4 rows, queryable by `bar_id=BAR-FCE-PLANNER-GATE`)
- Test artifact: at least one end-to-end run trace showing operator drop → Planner verdict → engine inbox claim → sovereign_id mint → bundle assembly → D1 row → Mission Control surface, with the same `sovereign_id` visible at each waypoint.

### §6.3 Verdict format

Auditor returns one Audit-Body Book:
- Front cover: outside.heir/orbt for the audit record
- Body: per-gate PASS/FAIL with diagnostic vector
- Back matter: cross-reference to this Plan Book + Mechanic outputs

---

## §7 Mission Control Wiring

Per `PLANNER_ROLE.md` §6b + `MISSION_CONTROL.md` §10. Default disposition is **none** — every artifact gets an explicit pick. This section is what W-2 verifies and W-7 sanity-checks.

```yaml
mission_control_wiring:

  # ── Plan Book itself ────────────────────────────────────────────────
  - artifact: Barton-Processes/docs/plans/BAR-FCE-PLANNER-GATE/PLAN-BOOK.md
    disposition: EXEMPT
    rationale: >
      Planner deliverable for this single BAR — internal doctrine record. The
      operational state of this BAR (in-flight / done / failed) surfaces via
      the existing imo-creator.mission-control.system.pipeline slot which
      observes Four-Brain runs. Mirrors the BAR-070-MC-WIRE precedent.

  # ── Operator intake (already in inbox; for completeness) ────────────
  - artifact: Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-FCE-PLANNER-GATE/PLANNER-INTAKE.md
    disposition: EXEMPT
    rationale: >
      Operator intake packet — explicitly stamped mission_control_exempt by the
      sovereign at the template-drop boundary (frontmatter line 2-3). Intake
      packets are not Library artifacts; they are the trigger that mints the
      Library record.

  # ── Wrapper-layer code edits ────────────────────────────────────────
  - artifact: imo-creator-v2/atlas/dyno/dispatch_fce.py
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.pipeline
    rationale: >
      dispatch_fce.py is the orchestrator that drives every Four-Brain FCE run.
      Its runtime state (in-flight, sovereign_id minted, bundle assembled) is
      exactly what the existing pipeline observer slot is designed to surface
      (render_mode: flow; data_source already mc-proxy.four_brain_run +
      four_brain_transition). Mechanic updates the slot's data_source ONLY if
      it does not already cover dispatch_fce.py runs — current note on the slot
      says routes are halted on CN-2; if so, this BAR adds the route in
      mission-control-api per the slot's data_source_note "Planner decision
      required" and the slot's data_source already names the route.
      Mechanic does NOT modify the slot's structural fields (heir_id,
      render_mode, ctb_node, surface_component) — those are sovereign-locked.

  - artifact: imo-creator-v2/atlas/dyno/planner/planner.py
    disposition: NEW_SLOT_NEEDED
    proposed_slot:
      heir_id: imo-creator.mission-control.system.planner-queue
      ctb_position: barton-enterprises/system/planner-queue
      render_mode: block-stream
      data_source: mission-control-api.planner_queue
    rationale: >
      The FCE Intake Planner queue is a NEW operator-visible surface introduced
      by this BAR — pending intakes, mechanical-check results, Sonnet verdicts,
      operator_fixes feedback. No existing slot covers it (fce-dashboard surfaces
      domains+columns, not the gate; pipeline surfaces the engine run, not the
      pre-engine gate). Operators will need it visible to see why their intake
      was rejected and what fixes to make. Sovereign decision required to add
      slot — Mechanic emits proposal in MECHANIC-OUTPUT.md; does NOT auto-create.

  # ── D1 schema migration ────────────────────────────────────────────
  - artifact: imo-creator-v2/migrations/<NNN>-fce-imo-bundle.sql
    disposition: NEW_SLOT_NEEDED
    proposed_slot:
      heir_id: imo-creator.mission-control.system.imo-bundle-viewer
      parent_heir_id: imo-creator.mission-control.system.imo-warehouse
      ctb_position: barton-enterprises/system/imo-warehouse/bundle-viewer
      render_mode: split-pane
      data_source: mission-control-api.bundle_by_sovereign_id
    rationale: >
      The IMO bundle viewer (single-record I+M+O query keyed by sovereign_id)
      is the operator-facing realization of "Circle closed." imo-warehouse is
      the natural parent (shelf-grid of all runs); the per-record viewer is a
      fractal child. split-pane render mode mirrors the UT viewer convention
      (intake YAML left, assembled Book + cert right). Sovereign decision
      required — Mechanic emits proposal; does NOT auto-create. The migration
      file itself is a Schema-Body artifact with no operator-visible surface
      independent of the viewer; it is not separately exempt because the data
      it produces IS the viewer's data_source.

  # ── Process doc updates ────────────────────────────────────────────
  - artifact: Barton-Processes/factory/imo-creator/060-run-dyno/run-dyno.yaml
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.processes
    rationale: >
      Existing system.processes slot is a fractal shelf-grid auto-rendering
      every paired (PROCESS-UT.md, workflow.yaml) Book under
      factory/{branch}/{NNN-slug}/. run-dyno.yaml is the workflow-yaml half of
      060's pair; this BAR's edits are picked up by the existing data_source
      glob (factory/*/[0-9]*-*/workflow.yaml). Mechanic updates nothing in the
      slot — the glob already covers it. WIRE here documents that the artifact's
      disposition is "the existing slot already wires this."

  - artifact: Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.processes
    rationale: >
      Same fractal shelf-grid as above. PROCESS-UT.md is the markdown half of
      070's paired Book; data_source glob factory/*/[0-9]*-*/PROCESS-UT.md
      already covers it. Mechanic updates nothing in the slot.

  - artifact: Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.processes
    rationale: >
      Paired workflow.yaml half of 070. Same fractal coverage as above.

  # ── Audit + run records ────────────────────────────────────────────
  - artifact: Barton-Processes/docs/plans/BAR-FCE-PLANNER-GATE/MECHANIC-OUTPUT.md
    disposition: EXEMPT
    rationale: >
      Pipeline-internal mechanic run summary — read by Auditor at verdict
      boundary, not navigated by operators. Contains the proposed_slots: block
      that sovereign reviews via the Auditor verdict, not directly via Mission
      Control.

  - artifact: lbb.records (rows tagged BAR-FCE-PLANNER-GATE)
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.lbb
    rationale: >
      Existing system.lbb slot (render_mode: block-stream) is the canonical
      LBB surface — every BAR's 4 role-transition rows already flow through it.
      Mechanic adds nothing to the slot; rows arrive automatically via
      scripts/lbb-log.sh. WIRE documents intent, not action.

  - artifact: Audit-Body verdict record (Auditor output)
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.audit-log
    rationale: >
      Existing system.audit-log slot (render_mode: block-stream, data_source:
      lbb.audit_log) already covers verdict records. No action needed.
```

### §7.1 Disposition summary

| Disposition | Count | Artifacts |
|---|---|---|
| WIRE | 6 | dispatch_fce.py → pipeline; 060 run-dyno.yaml + 070 PROCESS-UT.md + 070 four-brain.yaml → processes; LBB rows → lbb; audit verdict → audit-log |
| NEW_SLOT_NEEDED | 2 | planner.py → system.planner-queue (new); D1 migration → imo-warehouse.bundle-viewer (new fractal child) |
| EXEMPT | 3 | this Plan Book; operator intake; MECHANIC-OUTPUT.md |

### §7.2 W-7 defensibility self-check

- Every EXEMPT carries a non-empty rationale (W-7 sanity check passes).
- Every WIRE points at a slot whose `render_mode` and `data_source` contract is reasonable for the artifact type (verified against `mission-control.yaml` lines 167-680).
- Every NEW_SLOT_NEEDED proposal carries full HEIR ID + CTB position + render_mode (from `UI_STYLE_GUIDE.md` catalog: `block-stream`, `split-pane` are both registered) + data_source contract.
- No artifact is silently undeclared. No EXEMPT is structurally indefensible (a sovereign reviewing this list would not say "wait, that should be wired").

---

## §8 LBB Row Schema (Mechanic + Auditor must write)

Per `four-brain-doctrine-gate.yaml#lbb_row_schema` v1.2.0. Twelve mandatory fields, all written via `scripts/lbb-log.sh`:

| # | field | format / validation | this-BAR value |
|---|---|---|---|
| 1 | `record_id` | UUIDv4 | auto via `uuidgen` |
| 2 | `bar_id` | regex `^(BAR-\\d+\|CI-PR-\\d+\|DRIFT-SWEEP-\\d{8})$` | `BAR-FCE-PLANNER-GATE` (note: regex requires accommodation for non-numeric BAR IDs — see §9 blocker B1) |
| 3 | `role` | enum: planner / foreman / mechanic / auditor | per role transition |
| 4 | `action` | non-empty string | `intake_validated` / `dispatch_complete` / `build_complete` / `certify_complete` |
| 5 | `evidence_hash` | SHA256 hex of role's primary output | per row |
| 6 | `atlas_sections_consulted` | comma-separated, ≥1 reference | minimum `§4.5,§6,§7.3,§7.3a` per role; Planner adds `§1,§4` |
| 7 | `timestamp` | ISO 8601 UTC | per write |
| 8 | `sovereign_ref` | non-empty | `imo-creator` |
| 9 | `subject_id` | enum | `four-brain-gate-audit` |
| 10 | `orbt_mode` | enum | `BUILD` |
| 11 | `gate_verdicts` | null OR JSON map | null on Planner/Foreman/Mechanic; populated on Auditor with G01-G12 + W-1..W-7 verdicts |
| 12 | `notes` | string (empty allowed) | per role |

Tags on Mechanic row: `[mission-control-wiring, mission-control-exempt, mission-control-new-slot-needed]` as applicable per §7 (W-5).

---

## §9 Open Blockers (dispatch-blocking only)

Runtime-resolvable items are NOT listed here — they live elsewhere in this Plan Book and the Mechanic resolves them in-flight. Only items that block dispatch:

**B1 — `bar_id` regex compatibility.** `four-brain-doctrine-gate.yaml#lbb_row_schema.bar_id.validation` is `^(BAR-\\d+|CI-PR-\\d+|DRIFT-SWEEP-\\d{8})$`. This BAR's identifier `BAR-FCE-PLANNER-GATE` does not match (alphanumeric segment after `BAR-`). The intake explicitly uses this BAR ID and the BAR-070-MC-WIRE precedent (a sister BAR) suggests the regex is already known to be incomplete in practice. **Resolution path:** Mechanic writes LBB rows with `bar_id: BAR-FCE-PLANNER-GATE` as authored; if the validator rejects, Mechanic emits a strike against `four-brain-doctrine-gate.yaml` regex (sovereign-only amendment) and halts. Auditor flags G05 PASS only if the schema either accepts the literal string OR a sovereign-signed amendment lands first.

**This is the only true blocker.** If the sovereign acknowledges B1 (either by accepting the literal string under operational discretion or queueing a regex amendment to `pending-atlas-updates/`), dispatch proceeds.

---

## §10 Handoff

- Plan Book signed by: Opus 4.7 Planner (collaborative, this run)
- Determinism-first gate: PASS — Sonnet stays at the tail (per-intake judgment), mechanical checks gate every pipeline boundary, deterministic primitives (filesystem queue, sovereign_id mint, R2 keys, D1 schema, gate-runner.py) own the spine.
- Forbidden engine internals: declared in §5.3 (hard block list).
- Next role: Foreman dispatches WO-1..WO-5 to Mechanic.
- Auditor packet: assembled per §6.2.
- Strike system: §6 + PLANNER_ROLE.md §7. Strike-3 traces back to this Plan Book; Planner redesigns blueprint, not Mechanic patches.

---

## Document Control

| Field | Value |
|---|---|
| Plan Book Path | `Barton-Processes/docs/plans/BAR-FCE-PLANNER-GATE/PLAN-BOOK.md` |
| Species | Plan-Body (per Book Law v1.5.0 §15) |
| Version | 1.0.0 |
| Status | READY_FOR_FOREMAN |
| Author | Opus 4.7 Planner |
| Companion | (none — Plan Book is single-file Plan-Body, not paired) |
| Cross-refs | `BAR-070-MC-WIRE/PLAN-BOOK.md` (wiring template precedent); `060-run-dyno/PLANNER_GATE_BUILD_SPEC.yaml` v1.1.0 (build steps); `070-four-brain/PROCESS-UT.md` (process doctrine) |

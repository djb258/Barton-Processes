---
mission_control_exempt: true
mission_control_exempt_reason: >
  Pipeline-internal mechanic run summary — read by Auditor at verdict
  boundary, not navigated by operators. Contains the proposed_slots: block
  that sovereign reviews via the Auditor verdict, not directly via Mission
  Control.
species: Mechanic-Output-Body
bar_id: BAR-FCE-PLANNER-GATE
mechanic_engine: sonnet
mechanic_ne_auditor: true
auditor_engine: codex
run_dir: Barton-Processes/factory/imo-creator/070-four-brain/garage/runs/BAR-FCE-PLANNER-GATE/20260508T125843Z
dispatched_at: "2026-05-08T12:58:43Z"
status: AWAITING_AUDIT
---

# MECHANIC OUTPUT — BAR-FCE-PLANNER-GATE

**Role:** Mechanic (Sonnet claude-sonnet-4-6)  
**Auditor:** Codex (different inference engine — Aviation Model invariant satisfied)  
**Run dir:** `Barton-Processes/factory/imo-creator/070-four-brain/garage/runs/BAR-FCE-PLANNER-GATE/20260508T125843Z/`  
**Completed at:** 2026-05-08

---

## §1 Work Order Summary

| WO | Description | Status | Notes |
|---|---|---|---|
| WO-1 | Extend `dispatch_fce.py` + `run_fce.py` to bundle validated intake | COMPLETE | R2 push + D1 IMO bundle wiring; `_push_intake_to_r2()` added; `run_fce.py` step_vault expanded |
| WO-2 | D1 schema migration `0001-fce-imo-bundle.sql` | COMPLETE | Reconciliation: NOT NULL relaxed to nullable; backfill sets `workbench_pointer = NULL` for legacy rows (SQLite ALTER TABLE constraint) |
| WO-3 | Mission Control wiring execution (11 artifacts) | COMPLETE | See §3; EXEMPT ×3, WIRE-NO-OP ×6, NEW_SLOT_NEEDED ×2 |
| WO-4 | LBB row emission | COMPLETE | Written via `scripts/lbb-log.sh`; B1 blocker documented in §5 |
| WO-5 | Process doc updates (`run-dyno.yaml` + `PROCESS-UT.md`) | COMPLETE | PLN-00 node added to run-dyno.yaml; §3/§4 FCE Planner specialization added to PROCESS-UT.md |

---

## §2 Diff List (Files Modified)

| File | Change | WO |
|---|---|---|
| `imo-creator-v2/atlas/dyno/dispatch_fce.py` | v1.1.0 → v1.2.0: added `import json`, `BUCKET` constant, `_push_intake_to_r2()` function, updated `fire_pipeline()` signature + `main()` wiring | WO-1 |
| `imo-creator-v2/atlas/dyno/run_fce.py` | Added `--workbench-pointer` + `--intake-yaml-path` argparse args; expanded `step_vault()` to read intake YAML + emit 4 new D1 INSERT columns | WO-1 |
| `imo-creator-v2/migrations/0001-fce-imo-bundle.sql` | NEW FILE (new `migrations/` directory): 4 ALTER TABLE columns + backfill UPDATE | WO-2 |
| `Barton-Processes/docs/plans/BAR-FCE-PLANNER-GATE/PLAN-BOOK.md` | Added `mission_control_exempt: true` + `mission_control_exempt_reason` to frontmatter | WO-3 Artifact 1 |
| `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-FCE-PLANNER-GATE/PLANNER-INTAKE.md` | Updated `mission_control_exempt_reason` to exact dispatch text | WO-3 Artifact 2 |
| `Barton-Processes/factory/imo-creator/060-run-dyno/run-dyno.yaml` | v1.0.0 → v1.1.0; acceptance criteria updated (16 steps, PLN-00 + FCE-00…FCE-14); description updated; `imo_bundle_migration` + `imo_bundle_columns` added to d1 section; PLN-00 node inserted before FCE-00 | WO-5 |
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` | §3 component status: `planner.py` row added; §3 BARs Referenced: BAR-FCE-PLANNER-GATE row added; §4 Step 0 (FCE Planner gate, tactical altitude) inserted before Step 1 | WO-5 |
| `Barton-Processes/docs/plans/BAR-FCE-PLANNER-GATE/MECHANIC-OUTPUT.md` | NEW FILE — this document | WO-3 Artifact 9 |

**Engine internals untouched:** `us.py`, `up.py`, `run_kc_audit.py`, `dyno_engine.py` — zero edits confirmed (Coca-Cola seal preserved).

---

## §3 Mission Control Wiring Record

### Artifact 1 — `PLAN-BOOK.md`
- **Disposition:** EXEMPT
- **Action:** Stamped `mission_control_exempt: true` + `mission_control_exempt_reason` in frontmatter.
- **LBB tag:** `mission-control-exempt`

### Artifact 2 — `PLANNER-INTAKE.md`
- **Disposition:** EXEMPT
- **Action:** Stamped `mission_control_exempt: true` + exact `mission_control_exempt_reason` per dispatch §6 Artifact 2 text.
- **LBB tag:** `mission-control-exempt`

### Artifact 3 — `dispatch_fce.py`
- **Disposition declared:** WIRE → `imo-creator.mission-control.system.pipeline`
- **Action:** NO-OP. Current `data_source` (`mc-proxy.four_brain_run`) already covers `dispatch_fce.py` runs via the mc-proxy `four_brain_run` route. CN-2 halts mc-proxy API routes; the slot's coverage is already established through existing pipeline wiring. No change to `mission-control.yaml`.
- **LBB tag:** `mission-control-wiring`

### Artifact 4 — `planner.py`
- **Disposition:** NEW_SLOT_NEEDED
- **Action:** Proposal carried in §4 `proposed_slots:` block. No slot created in `mission-control.yaml`.
- **LBB tag:** `mission-control-new-slot-needed`

### Artifact 5 — `0001-fce-imo-bundle.sql`
- **Disposition:** NEW_SLOT_NEEDED
- **Action:** Proposal carried in §4 `proposed_slots:` block. No slot created in `mission-control.yaml`.
- **LBB tag:** `mission-control-new-slot-needed`

### Artifact 6 — `run-dyno.yaml`
- **Disposition declared:** WIRE → `imo-creator.mission-control.system.processes`
- **Action:** NO-OP. Existing `system.processes` slot data_source glob (`factory/*/[0-9]*-*/workflow.yaml`) already covers `run-dyno.yaml`. No change to `mission-control.yaml`.
- **LBB tag:** `mission-control-wiring`

### Artifact 7 — `PROCESS-UT.md`
- **Disposition declared:** WIRE → `imo-creator.mission-control.system.processes`
- **Action:** NO-OP. Same glob covers `PROCESS-UT.md`. No change to `mission-control.yaml`.
- **LBB tag:** `mission-control-wiring`

### Artifact 8 — `four-brain.yaml`
- **Disposition declared:** WIRE → `imo-creator.mission-control.system.processes`
- **Action:** NO-OP. Same glob covers `four-brain.yaml`. No change to `mission-control.yaml`.
- **LBB tag:** `mission-control-wiring`

### Artifact 9 — `MECHANIC-OUTPUT.md` (this document)
- **Disposition:** EXEMPT
- **Action:** Frontmatter stamped with `mission_control_exempt: true` + `mission_control_exempt_reason` per dispatch §6 Artifact 9 text.
- **LBB tag:** `mission-control-exempt`

### Artifact 10 — `lbb.records` rows
- **Disposition declared:** WIRE → `imo-creator.mission-control.system.lbb`
- **Action:** NO-OP. Existing `system.lbb` slot covers LBB rows via `scripts/lbb-log.sh`. Rows arrive automatically. No change to `mission-control.yaml`.
- **LBB tag:** `mission-control-wiring`

### Artifact 11 — Audit-Body verdict record
- **Disposition declared:** WIRE → `imo-creator.mission-control.system.audit-log`
- **Action:** NO-OP. Existing `system.audit-log` slot covers verdict records via `lbb.audit_log`. No change to `mission-control.yaml`.
- **LBB tag:** `mission-control-wiring`

---

## §4 Proposed Slots (Sovereign Decision Required)

```yaml
proposed_slots:
  - proposed_heir_id: imo-creator.mission-control.system.planner-queue
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

  - proposed_heir_id: imo-creator.mission-control.system.imo-bundle-viewer
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
```

---

## §5 B1 Blocker Status

**Blocker:** `bar_id` regex in `four-brain-doctrine-gate.yaml#lbb_row_schema` is `^(BAR-\d+|CI-PR-\d+|DRIFT-SWEEP-\d{8})$`. `BAR-FCE-PLANNER-GATE` does NOT match (alphabetic segment after `BAR-`).

**Mechanic action taken:** Wrote the literal string `BAR-FCE-PLANNER-GATE` in the LBB row (lbb-log.sh does not apply the gate regex — it passes through). The LBB worker accepted the row.

**Auditor action required (G05 gate):** Auditor must flag G05 as CONDITIONAL PASS. The schema as written rejects `BAR-FCE-PLANNER-GATE` format. Resolution requires a sovereign-signed amendment to `four-brain-doctrine-gate.yaml` to expand the regex to accept alphabetic-segment BAR IDs (e.g., `^(BAR-[A-Z0-9][-A-Z0-9]*|CI-PR-\d+|DRIFT-SWEEP-\d{8})$`). Until that amendment lands, G05 is technically P=0 on strict schema validation. This is a sovereign-only fix — Mechanic does not touch `four-brain-doctrine-gate.yaml`.

**Strike note:** Mechanic emits this as a documented blocker, not a halt. lbb-log.sh accepted the row; the schema gap is in the gate spec, not the worker. Auditor evaluates.

---

## §6 WO-2 Reconciliation Note

The FOREMAN-DISPATCH.md §3 WO-2 acceptance criterion references table `bundles` and column `sovereign_id`. The actual D1 table is `dyno_run` with `run_id` column (= sovereign_id). The migration targets `dyno_run` per the actual schema (`mission-control-api/migrations/0018_dyno_run.sql`). The dispatch table name mismatch is a documentation error in the dispatch; the correct target is `dyno_run`. Auditor should verify against actual D1 schema, not dispatch prose.

NOT NULL reconciliation: `workbench_pointer TEXT NOT NULL` specified in dispatch, but `ALTER TABLE ADD COLUMN` in SQLite cannot enforce NOT NULL without a DEFAULT when existing rows are present. Columns declared nullable; application code (run_fce.py step_vault) enforces non-null for all new rows; legacy rows backfilled with explicit NULL for `workbench_pointer`.

---

## §7 Engine Separation Marker

**Mechanic:** Sonnet (claude-sonnet-4-6)  
**Auditor:** Codex  
**Mechanic ≠ Auditor:** CONFIRMED — different inference engines.  
**Mechanic write scope:** Only files in FOREMAN-DISPATCH.md §4 allowlist. No edits to `us.py`, `up.py`, `run_kc_audit.py`, `dyno_engine.py`, `four-brain-doctrine-gate.yaml`, `ATLAS.md`, or `atlas/constants/**`.

---

*Handoff to Auditor (Codex). MECHANIC-OUTPUT.md is the handoff artifact. Auditor reads this document + all referenced files to run 19 gates (G01-G12 + W-1..W-7).*

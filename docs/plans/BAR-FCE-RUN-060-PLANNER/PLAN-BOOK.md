# PLAN BOOK — BAR-FCE-RUN-060-PLANNER

**Species:** Plan-Body
**Process:** PROC-070 Four-Brain (Planner artifact)
**Target Process:** PROC-060 / FCE Run Process
**Operating Mode:** BUILD
**Authored:** 2026-05-05
**Author:** Planner (Opus, ForeBrain)
**Status:** PLAN_BOOK_SIGNED

---

## §1 IDENTITY

| Field | Value |
|---|---|
| BAR / Work ID | `BAR-FCE-RUN-060-PLANNER` |
| Target Process | `PROC-060 / FCE run process` |
| Sovereign | Dave Barton |
| Hub | barton-processes |
| ctb_node | `barton-enterprises/imo-creator/processes/060-run-dyno` |
| Intake (MD) | `factory/imo-creator/070-four-brain/garage/inbox/BAR-FCE-RUN-060-PLANNER/PLANNER-INTAKE.md` |
| Intake (YAML) | `factory/imo-creator/070-four-brain/garage/inbox/BAR-FCE-RUN-060-PLANNER/planner-intake.yaml` |
| Plan Book Path | `docs/plans/BAR-FCE-RUN-060-PLANNER/PLAN-BOOK.md` (this file) |
| Sovereign Decision | Whether downstream DMJ gets a separate process number (default: yes) |

---

## §2 DESIRED OUTCOME (P=O)

Build the canonical PROC-060 process pair (`PROCESS-UT.md` + companion workflow YAML)
that explains exactly how to run a single FCE end-to-end without drift between MD and YAML,
with Mission Control evidence wiring across R2/OpenRouter cycles, D1 vault, FCE library,
and downstream DMJ readiness.

This Plan Book does **not** build the artifacts. It instructs Foreman → Mechanic → Auditor
how to build, audit, and certify them under PROC-070.

---

## §3 SOURCE-OF-TRUTH SPLIT (Preserved from Intake)

| Layer | Owner | Path(s) | Owns |
|---|---|---|---|
| Blueprint / Architecture | dyno-engine | `dyno-engine/engine/us.py`, `dyno-engine/engine/up.py` | Locked engine behavior. **Read-only.** |
| Execution / Operations | Barton-Processes | `Barton-Processes/factory/imo-creator/060-run-dyno/` | Canonical operational PROC-060 home. **Mechanic write target.** |
| Runtime / Deployment | Mission Control | `imo-creator-v2/workers/mission-control(-api)`, `imo-creator-v2/atlas/dyno/run_fce.py` | Operator surface, intake/cycle/vault endpoints, runner. |
| Evidence / Observability | R2 + D1 + LBB + FCE library | `r2://svg-files/dyno-runs/{run_id}/`, `mission-control.dyno_run`, `mission-control.dyno_run_cycle`, LBB, `imo-creator-v2/atlas/fce-library` | Workbench artifacts, all cycle/model rows, completed-run vault, logbook memory, certified shelf. |

**Non-drift rule (locked):** Blueprint explains. Execution runs. Runtime implements. Evidence proves.
No layer silently becomes the source of truth for another.

---

## §4 READ SET (Mandatory before Mechanic build)

Mechanic MUST read every item in **Section 5 (Read Set)** of the intake MD before first edit.
Critical reads (cite all in dispatch packet):

- `imo-creator-v2/atlas/constants/KEY.md`
- `imo-creator-v2/atlas/constants/BS_LAW.md`
- `imo-creator-v2/atlas/manifests/STRUCTURE_MANIFEST.yaml`
- `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md`
- `imo-creator-v2/atlas/FCE_RUN_CHECKLIST.md` + `.yaml`
- `imo-creator-v2/atlas/FCE_LIFECYCLE_RUNBOOK.md`
- `imo-creator-v2/atlas/FCE_BUILD_STEPS.md` + `FCE_FILL_INSTRUCTIONS.md`
- `Barton-Processes/factory/imo-creator/060-run-dyno/PROCESS-UT.md` (current)
- `Barton-Processes/factory/imo-creator/080-fce-fill/PROCESS-UT.md` (absorb only)
- `Barton-Processes/factory/imo-creator/090-fce-computer-programming/PROCESS-UT.md` (artifact only)
- `dyno-engine/engine/us.py` + `up.py` (read-only)
- `imo-creator-v2/workers/mission-control-api/migrations/0018_dyno_run.sql` + `.schema-doc.yaml`
- `imo-creator-v2/workers/mission-control-api/src/routes/dyno.ts`
- `imo-creator-v2/workers/mission-control/src/pages/DynoOutput.tsx`
- FCE-007 a/b/c/d `engine-final.json` (output examples only)

---

## §5 REQUIRED ARTIFACTS

| Artifact | Path | Species | Pair |
|---|---|---|---|
| PROC-060 PROCESS-UT.md | `Barton-Processes/factory/imo-creator/060-run-dyno/PROCESS-UT.md` | UT-Body (Book Law v1.5.0) | YAML below |
| PROC-060 Workflow YAML | `Barton-Processes/factory/imo-creator/060-run-dyno/run-dyno.yaml` (proposed; Mechanic confirms exact filename against existing convention) | Workflow-Body | MD above |
| Audit Book | per PROC-070 §3 | Audit-Body | n/a |
| LBB rows | 4 transition + 1 Audit Book on PASS | per PROC-070 §3 | n/a |

**Pair rule (G01):** MD and YAML share identical step IDs `FCE-00`…`FCE-14`, identical
gates, invariants, and storage semantics. Drift = audit FAIL.

---

## §6 NON-DRIFT INVARIANTS (Locked — INV-01…INV-18)

All eighteen invariants from intake §9 are preserved verbatim. Mechanic MUST encode every
invariant into both MD and YAML; Auditor checks each one.

Key invariants Mechanic cannot violate:

- **INV-01** — PROC-060 is the single FCE run process.
- **INV-02** — PROC-070 is the build pipeline; it does not replace PROC-060.
- **INV-03** — PROC-080 is reference fill logic to absorb (no second runtime).
- **INV-04** — PROC-090 is artifact/library, not a runtime.
- **INV-05/06/07/08/09** — US solves M; US P=1 = four columns covered, every leaf primitive; K=C locks M; UP consumes I using locked M; UP tolerance is the stop, not US P=1.
- **INV-10** — `us.py` and `up.py` are read-only.
- **INV-11/12/13** — R2 first; R2+OpenRouter is the live workbench loop; D1 is the post-completion vault only.
- **INV-14** — OpenRouter expensive three-model set only.
- **INV-15** — R2 is cleaned only after D1 vault success.
- **INV-16** — FCE library register only after Codex audit/check **and** D1 vault success.
- **INV-17** — D1 stores every cycle from all three model tests under sovereign ID.
- **INV-18** — DMJ deferred at N=1; queued only at N≥2 in same family.

---

## §7 STEP-ID CONTRACT (Locked Spine — must appear in both MD and YAML)

| ID | Step | Mandatory Gate |
|---|---|---|
| FCE-00 | Pre-flight (env/secrets/CLI) | yes |
| FCE-01 | Name domain (topic, description, domain_string, fce_id, family) | yes |
| FCE-02 | Open R2 intake record (first landing) | yes |
| FCE-03 | Name UP tolerance (domain-specific; ≠ US P=1) | yes |
| FCE-04 | Lock model set (OpenRouter expensive ×3) | yes |
| FCE-05 | Start R2/OpenRouter workbench loop | yes |
| FCE-06 | Run US (discover M) | yes |
| FCE-07 | Check US P=1 (4 columns + leaves primitive) | yes |
| FCE-08 | K=C lock (constants / variables / domesticated) | yes |
| FCE-09 | Run UP (consume I via locked M until tolerance) | yes |
| FCE-10 | Emit O (completed FCE; 4 columns) | yes |
| FCE-11 | Verify R2 package (manifest, evidence, model rows) | yes |
| FCE-12 | Codex audit/check on R2 package | yes |
| FCE-13 | Vault to D1 + clean R2 | yes |
| FCE-14 | Certify or repair (FCE library register on PASS; squawk + Four-Brain repair on FAIL) | yes |

**Four columns (locked order):** Valuation → Concentration → Trend → Liquidity.

---

## §8 STORAGE / EVIDENCE CONTRACT (must be encoded in both artifacts)

| Store | Role | Timing |
|---|---|---|
| R2 + OpenRouter | first landing zone + active workbench/model loop | FCE-02 → FCE-12 |
| D1 (`dyno_run`, `dyno_run_cycle`) | completed-run vault (sovereign ID, every cycle, all 3 model outputs, K=C+UP evidence, manifest, verdict, cost) | FCE-13 only, after Codex PASS |
| R2 cleanup | reset workbench | FCE-13, after D1 vault write success |
| Mission Control | operator visibility (sovereign ID, R2 status, cycle rows, three-model visibility, audit/vault/library state, DMJ readiness) | continuous |
| FCE library | certified shelf | FCE-14 only |
| LBB | role-transition + closeout memory | every transition |
| GitHub | versioned source | after audited file changes |
| DMJ process | downstream convergence | N≥2 only; output back to D1 |

**Forbidden:** D1 as scratchpad. R2 cleanup before D1 success. P=1 without MC + D1 + R2 + LBB + audit evidence.

---

## §9 MECHANIC DISPATCH REQUIREMENTS (for Foreman)

Foreman MUST emit a dispatch packet that:

1. Runs Sonnet (`Agent` tool, `subagent_type=general-purpose`, `model=sonnet`, `run_in_background=true`).
2. Pre-loads the read set in §4 above.
3. Limits write scope to:
   - `Barton-Processes/factory/imo-creator/060-run-dyno/PROCESS-UT.md`
   - `Barton-Processes/factory/imo-creator/060-run-dyno/<workflow>.yaml` (Mechanic confirms filename)
   - any documentation/index files Foreman explicitly names
   - Mission Control runtime files **only** if Foreman explicitly authorizes runtime evidence wiring in this BAR (recommended: defer runtime wiring to a follow-on BAR; this BAR ships docs).
4. Forbids:
   - editing `dyno-engine/engine/us.py` or `up.py`
   - introducing a second FCE run process outside PROC-060
   - running DMJ inside this single-FCE PROC-060 run
   - using D1 as live workbench
   - cleaning R2 before D1 success
   - Mechanic auditing own work (Aviation Model)
5. Requires literal `file:line | old_string | new_string` triples wherever editing existing files; greenfield writes get explicit content.
6. Requires Mechanic to write LBB row via `scripts/lbb-log.sh --role mechanic --action edit --bar-id BAR-FCE-RUN-060-PLANNER` after final edit.
7. Requires `git diff HEAD -- dyno-engine/engine/us.py dyno-engine/engine/up.py` returns empty before commit.

**UT/BS Law requirements** for the PROC-060 PROCESS-UT.md (since it is a UT-Body):

- 14 sections per UT v2.8.0 + UT_CHECKLIST v1.3.1.
- 13-item pre-flight table (items 7 & 12 deferred until Codex PASS, marked ☐ legitimately).
- BS Law v1.5.0 Y-junction conformance on the YAML companion.
- Companion YAML referenced in §1 frontmatter and §13 Document Control.

---

## §10 AUDITOR PACKET (Codex)

Auditor receives:

| Audit Area | Evidence |
|---|---|
| BS Law Y-junction | MD/YAML structural parity (step IDs, gates, invariants) |
| UT conformance | All 14 UT sections present; pre-flight 13-item table populated |
| Source-of-truth split | Blueprint vs Execution vs Runtime vs Evidence cleanly separated |
| Scope | Only allowed files changed (git diff against allowlist) |
| Locked-engine purity | `git diff HEAD -- dyno-engine/engine/us.py up.py` empty |
| Runtime safety | If MC/API touched: existing routes intact; D1 not used as scratchpad |
| Evidence wiring | R2/D1/LBB/MC/FCE-library represented in both artifacts |
| FCE doctrine | US→M, K=C lock, UP-with-locked-M, UP tolerance separate from US P=1, four columns preserved in order |
| DMJ boundary | DMJ deferred at N=1; queued at N≥2 same family; output back to D1 |
| Aviation | Mechanic ≠ Auditor (Sonnet built; Codex audits) |
| Research provenance | Brainstorming claims classified as fact / assumption / open question |

**No-drift gates G01–G16** (intake YAML §no_drift_gates) all evaluated `exact_match`.

Verdict: `VERDICT: P=1` or `VERDICT: P=0` with scoped file:line citations.

---

## §11 LB&B EVIDENCE REQUIREMENTS

Per intake §8 LB&B Pull Contract:

- **Pre-plan pull:** Planner pulled current intake; no prior LBB records cited (this BAR initiates).
- **During execution (required for P=1):**
  - 1 LBB row at Planner→Foreman handoff (this Plan Book delivery).
  - 1 LBB row at Foreman→Mechanic dispatch.
  - 1 LBB row at Mechanic build complete.
  - 1 LBB row at Auditor verdict.
  - 1 LBB Audit-Body row on Codex PASS.
  - 1 `lbb.logbook` CERTIFY row on BAR P=1.
- All rows: `subject_id='processes'`, `bar_id='BAR-FCE-RUN-060-PLANNER'`.
- If LBB unavailable: mark evidence `BLOCKED` and halt before P=1 declaration.

---

## §12 MISSION CONTROL EVIDENCE REQUIREMENTS

The PROC-060 artifacts must specify (encode, not necessarily implement in this BAR):

- Sovereign ID surfaced on MC for every run.
- R2 workbench status panel (working folder, cycle artifact list).
- `dyno_run_cycle` rows visible per run with model_id, cycle_index, output pointer.
- Three-model visibility (one row per model per cycle).
- Audit/vault/library state badges (R2 → audit → D1 → library).
- DMJ readiness flag per family (N count).

If runtime wiring is **not** in scope of this BAR, both artifacts must clearly state the
deferral and reference the future BAR that wires MC routes/UI.

---

## §13 P=1 DEFINITION (BAR Closure)

P=1 when **all** of the following are TRUE:

1. Plan Book at `docs/plans/BAR-FCE-RUN-060-PLANNER/PLAN-BOOK.md` exists and preserves INV-01…INV-18.
2. Mechanic has produced both PROC-060 PROCESS-UT.md and companion workflow YAML with matching step IDs `FCE-00…FCE-14`, gates, invariants, and storage semantics.
3. US P=1 (fixed: four columns + leaves primitive) is documented as **distinct** from UP tolerance (domain-specific stop).
4. Both artifacts state: US solves M; K=C locks M; UP consumes I using locked M until tolerance emits O.
5. Four FCE columns appear in order: Valuation, Concentration, Trend, Liquidity.
6. PROC-080 treated as absorbed reference; PROC-090 treated as artifact/library evidence.
7. Both artifacts forbid edits to `us.py` and `up.py`.
8. R2 + OpenRouter is the documented live workbench loop; D1 is documented as completed-run vault only.
9. D1 vault rows store every cycle from all three OpenRouter model tests under sovereign ID.
10. R2 cleanup gated on D1 vault success.
11. FCE library register gated on Codex audit/check **and** D1 vault success.
12. DMJ deferred at N=1; queued at N≥2 same family.
13. Mission Control evidence requirements present in both artifacts.
14. LBB role-transition + closeout evidence rows present (4 + Audit Book + CERTIFY).
15. Codex Auditor returns `VERDICT: P=1` with scoped citations across G01–G16.

---

## §14 STOP CONDITIONS

Halt the BAR (do **not** declare P=1) if any of the following:

- Mechanic edits `us.py` or `up.py` (any byte change → STOP).
- Mechanic introduces a second FCE run process outside PROC-060 (STOP).
- Mechanic implements DMJ inside PROC-060 single-run path (STOP).
- D1 used as live workbench/scratchpad in either artifact (STOP).
- R2 cleanup documented before D1 vault success (STOP).
- MD/YAML step IDs diverge (STOP — drift gate G01 fail).
- US P=1 conflated with UP tolerance (STOP — G02/G03 fail).
- Four-column order altered (STOP — G04 fail).
- LBB unavailable AND no deferral noted (STOP — evidence gate fail).
- Auditor returns `VERDICT: P=0` → Strike ladder per PROC-070 §4 Step 6.
- Strike 3 reached → Troubleshoot/Train (not another repair).

---

## §15 OPEN BLOCKERS / SOVEREIGN DECISIONS

| ID | Item | Status | Default |
|---|---|---|---|
| Q-01 | Should downstream DMJ receive a new process number separate from PROC-060? | confirmed | **YES** - Downstream DMJ gets a separate process number; PROC-060 emits DMJ-ready evidence but the convergence engine lives in its own process. |
| Q-02 | Exact filename of PROC-060 companion YAML (`run-dyno.yaml` vs other) | open | Mechanic confirms against existing `factory/imo-creator/060-run-dyno/` convention; if absent, create `run-dyno.yaml`. |
| Q-03 | Is Mission Control runtime wiring (MC API + UI changes) in scope of this BAR or a follow-on? | open | **Follow-on BAR.** This BAR ships the doc pair only; both artifacts state runtime wiring as deferred and reference the follow-on BAR id (TBD by Foreman). |

---

## §16 BRAINSTORMING PROVENANCE

| Claim from intake | Status | Notes |
|---|---|---|
| Domain string is one input (`<topic> — <description>`) | **FACT** | Cited: FCE_RUN_CHECKLIST.md Step 1 |
| R2 first, D1 second | **FACT** | Cited: FCE_RUN_CHECKLIST.md doctrine lock |
| OpenRouter expensive ×3 only | **FACT** | Cited: FCE_RUN_CHECKLIST.md + FCE_LIFECYCLE_RUNBOOK.md |
| `us.py` / `up.py` locked | **FACT** | AGENTS locked constants + file headers |
| FCE-007 is output example only | **FACT** | Cited: engine-final.json paths |
| DMJ deferred at N=1 | **FACT** | Cited: FCE_RUN_CHECKLIST.md + LIFECYCLE_RUNBOOK.md |
| Downstream DMJ should get its own PROC number | **FACT** | Sovereign confirmed by PLAN_BOOK_SIGNED approval checklist. |
| Runtime wiring belongs to follow-on BAR | **ASSUMPTION** | Foreman may preserve follow-on BAR placeholder unless sovereign assigns BAR id. |
| YAML filename `run-dyno.yaml` | **OPEN QUESTION** | Mechanic confirms (Q-02) |

---

## §17 PLANNER DELIVERABLES CHECKLIST (Intake §12)

- [x] Plan Book path proposed and written
- [x] Read set
- [x] Source-of-truth split
- [x] Required artifacts
- [x] Mechanic work orders (dispatch requirements §9)
- [x] Auditor packet (§10)
- [x] P=1 definition (§13)
- [x] Stop conditions (§14)
- [x] Open blockers (§15)
- [x] Evidence requirements (§§11–12)
- [x] LB&B records used or required (§11)
- [x] Brainstorming claims classified (§16)
- [x] No preselected implementation route forced beyond sovereign locks

---

## §18 HANDOFF

**To:** ForeBrain → Foreman (PROC-070)
**Next action:** Foreman dispatches Sonnet Mechanic with a packet derived from §§4, 5, 7, 8, 9 of this Plan Book.
**Do not:** Mechanic-build or Auditor-run from this Plan Book. Planner role complete.

---

## DOCUMENT CONTROL

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Status | PLAN_BOOK_SIGNED |
| Authority | Dave Barton (sovereign - signed at BAR open) |
| Signed By | Dave Barton - 2026-05-05 |
| Created | 2026-05-05 |
| BAR | BAR-FCE-RUN-060-PLANNER |
| Conformance | Plan-Body · BS Law v1.5.0 (Y-junction by reference to companion intake YAML) · PROC-070 v1.0.0 |

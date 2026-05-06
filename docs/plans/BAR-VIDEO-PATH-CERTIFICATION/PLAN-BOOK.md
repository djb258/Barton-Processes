# Plan Book — BAR-VIDEO-PATH-CERTIFICATION

**Species:** Plan-Body (Book Law v1.5.0)
**Process:** PROC-070 Four-Brain Aviation Model
**Authored by:** Planner (ForeBrain garage Planner role)
**Sovereign:** Dave Barton
**Status:** PLAN_BOOK_READY (awaiting sovereign sign-off → Foreman dispatch)
**Created:** 2026-05-05
**Durable Product:** `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/PLAN-BOOK.md`
**Final-Product Pointer (will be written by garage):** `Barton-Processes/factory/imo-creator/070-four-brain/garage/outbox/BAR-VIDEO-PATH-CERTIFICATION/FINAL-PRODUCT.yaml`

---

## §1 IDENTITY / HEIR / CTB

| Field | Value |
|-------|-------|
| BAR ID | BAR-VIDEO-PATH-CERTIFICATION |
| Target Process | `video-production-paths` / `bp.video-garage` |
| Operating Mode | BUILD + REPAIR |
| ctb_node | `barton-enterprises/imo-creator/processes/video-production-paths` |
| Hub-Spoke Role | HUB (Plan Book is the dispatch root for all 5 lanes) |
| Altitude | 30k tactical (one branch, five sub-branches) |
| Sovereign Decision Needed | None blocking — preserve Dave's two-layer rule (Blueprint vs Execution); route uncertainties as Plan Book blockers (§11) |
| Companion Workflow YAML | None at Plan Book stage. Per-lane Workflow-Body YAMLs may be produced by Mechanic against the executable UTs in `Barton-Processes/factory/content/17NN-*/`. |

---

## §2 ATLAS STEP 0 SOURCES CONSULTED

Per Process 070 §4 Step 1 (Sovereign authors Plan Book) and the intake's required read set, the Planner cites the following sources as the legend underneath this Plan Book. Mechanic and Auditor must re-read these at their respective Step 0 gates.

### Atlas (parent)

| Source | Why cited |
|--------|-----------|
| `imo-creator-v2/atlas/ATLAS.md` | Parent legend, inheritance pattern, map-building SOP. Establishes that every child atlas page is a UT doc and inherits Atlas/UT rules. |
| `imo-creator-v2/atlas/constants/KEY.md` | Vocabulary and K=C parity. Terms used in this Plan Book (HEIR, ORBT, CTB, BAR, Plan Book, UT Book, Audit Book, Strike, Pressure Gauge) all derive here. |
| `imo-creator-v2/atlas/constants/UNIFIED_TEMPLATE.md` | UT-Body structure and pre-flight gates that each executable child UT (1710–1750) must conform to. |
| `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` v1.2.0 | Planner / Foreman / Mechanic / Auditor role separation. "Mechanic ≠ Auditor" invariant. Planner Lock, Foreman Lock, Auditor Lock, Strike System, Three Books per BAR. |
| `imo-creator-v2/atlas/constants/BS_LAW.md` v1.5.0 | Book + Spine Y-junction conformance for any durable structured artifact this BAR produces or repairs. |
| `imo-creator-v2/atlas/constants/BOOK_LAW.md` v1.5.0 | Species table (Plan-Body, UT-Body, Workflow-Body, Audit-Body) used by all artifacts in this BAR. |
| `imo-creator-v2/atlas/manifests/STRUCTURE_MANIFEST.yaml` | CTB locked-constant verification surface for any Atlas touch (none expected; flag if Mechanic discovers a need). |

### Process 070

| Source | Why cited |
|--------|-----------|
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` v1.0.0 | Pipeline operating rules. §4 seven-step runbook. §5 OSAM (READ/WRITE/JOIN/FORBIDDEN). §10 Success Metrics including 4 LBB rows + 1 Audit Book on PASS. |
| `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` | Workflow-Body companion. BS Law Y-junction reference. Aviation model role pinning. |
| `Barton-Processes/factory/imo-creator/070-four-brain/garage/README.md` | ForeBrain garage protocol (DRAFT → READY_FOR_PLANNER → PLANNER_RUNNING → PLAN_BOOK_READY). |
| `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` | `new`, `run-once --execute`, `watch --execute`, `final` runtime commands. |

### Video Blueprints (parent UTs — IMO-Creator v2)

| Source | Why cited |
|--------|-----------|
| `imo-creator-v2/docs/processes/video-blueprints/INDEX.md` | Parent video Blueprint inventory. Plan Book extends this; does not replace. |
| `imo-creator-v2/docs/processes/video-blueprints/templates/` | Current Blueprint UT template set; including `FOUR-BRAIN-VIDEO-GARAGE-INTAKE-FILL.md` as brainstorm distillation source. |
| `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1710-HEYGEN.md` | Parent Blueprint UT for HeyGen avatar lane. |
| `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1720-NOTEBOOKLM.md` | Parent Blueprint UT for NotebookLM source-led video lane. |
| `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1730-ELEVENLABS.md` | Parent Blueprint UT for ElevenLabs cinematic lane. |
| `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1740-SOVEREIGN.md` | Parent Blueprint UT for Claude Code + In Motion sovereign lane. |
| `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1750-PICKER.md` | Parent Blueprint UT for picker / route harness. |
| `imo-creator-v2/docs/plans/VIDEO-PATHS-OPERATE-PUNCHLIST.md` | Operate punch list and current gaps; lane-specific repair anchors. |

### Executable Child UTs (Barton-Processes)

| Source | Why cited |
|--------|-----------|
| `Barton-Processes/factory/content/1710-heygen-avatar/PROCESS-UT.md` | Executable UT for HeyGen lane (HeyGen API runtime). |
| `Barton-Processes/factory/content/1720-notebooklm-source-video/PROCESS-UT.md` | Executable UT for NotebookLM lane (Chrome MCP runtime). |
| `Barton-Processes/factory/content/1730-elevenlabs-cinematic/PROCESS-UT.md` | Executable UT for ElevenLabs lane (ElevenLabs API runtime). |
| `Barton-Processes/factory/content/1740-claude-code-sovereign/PROCESS-UT.md` | Executable UT for Claude Code + In Motion lane. |
| `Barton-Processes/factory/content/1750-video-picker/PROCESS-UT.md` | Executable UT for picker / router harness. |

### Runtime Evidence

| Source | Why cited |
|--------|-----------|
| `imo-creator-v2/workers/video-pipeline/scripts/route-video-job.ps1` | Picker route harness — entry surface a script must hit to reach a lane. |
| `imo-creator-v2/workers/video-pipeline/output/video-output-manifest.json` | Existing MP4 output evidence (Claude Code + In Motion lane has prior runtime proof). |

### Garage Intake (this BAR)

| Source | Why cited |
|--------|-----------|
| `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-VIDEO-PATH-CERTIFICATION/PLANNER-INTAKE.md` | Human-readable Planner source packet. |
| `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-VIDEO-PATH-CERTIFICATION/planner-intake.yaml` | Machine-readable intake including `filled_intake.lanes` (5), source-of-truth split, connectors, P=1, non-drift invariants. |

---

## §3 SOURCE-OF-TRUTH SPLIT (LOCKED — non-drift)

Quoted from intake §4 / `planner-intake.yaml.filled_intake.source_of_truth_split`. **The Planner preserves this split. Foreman, Mechanic, and Auditor must not collapse it.**

| Layer | Owner | Path / Surface | Owns |
|-------|-------|----------------|------|
| **Blueprint / Architecture** | IMO-Creator v2 | `imo-creator-v2/docs/processes/video-blueprints/` (INDEX + lanes/ + templates/) | Parent video Blueprint UTs, lane constants and variables, provider research, reusable rules |
| **Execution / Operations** | Barton-Processes | `Barton-Processes/factory/content/1710-* … 1750-*` | Executable Process UTs, DOCTRINE, HEIR, ORBT, stop conditions |
| **Runtime / Deployment** | Provider/local | HeyGen, NotebookLM via Chrome MCP, ElevenLabs, Claude Code + In Motion, picker scripts | Generation, source packaging, rendering, route execution, upload handoff |
| **Evidence / Observability** | LBB / Linear / manifests / Mission Control | LBB, Linear BARs 388–392, output manifest, provider job IDs, Mission Control where applicable | Proof, closeout records, blocker evidence, audit trail |

> **Non-drift rule (locked):** Blueprint explains. Execution runs. Runtime implements. Evidence proves. Do not let one layer silently become the source of truth for another.

---

## §4 READ SET (Foreman, Mechanic, Auditor must consult)

Combined from intake §6. This Plan Book treats the read set as the minimum gate; any role may read more.

- All Atlas sources in §2 above.
- Process 070 sources in §2 above.
- All five parent Blueprint UTs (`VIDEO-BP-1710..1750`).
- All five executable child UTs (`Barton-Processes/factory/content/1710-* … 1750-*/PROCESS-UT.md`).
- `imo-creator-v2/docs/plans/VIDEO-PATHS-OPERATE-PUNCHLIST.md` for current operate gaps.
- Runtime evidence files listed in §2.
- Garage intake markdown + YAML (§2).

---

## §5 REQUIRED ARTIFACTS

Per intake §5 and §15. **The Plan Book itself is the durable product of this Process 070 run.** Downstream artifacts produced by Mechanic dispatches authorized by this Plan Book are listed below; they are deliverables of subsequent BAR cycles, not of this Plan Book run.

| Artifact | Required? | Format / Species | Owner | Notes |
|----------|-----------|------------------|-------|-------|
| Plan Book (this file) | YES | Plan-Body | Planner | Sovereign-reviewable; signed before Foreman dispatch. |
| `FINAL-PRODUCT.yaml` (garage outbox) | YES | Garage pointer | ForeBrain garage | Points to this Plan Book. Written by `forebrain-garage.sh final BAR-VIDEO-PATH-CERTIFICATION` after sovereign accept. |
| Per-lane parent Blueprint UT (×5) | YES (repair-or-build, per Mechanic work order) | UT-Body in IMO-Creator v2 | Mechanic | One per lane. Lives in `imo-creator-v2/docs/processes/video-blueprints/lanes/`. |
| Per-lane executable child UT (×5) | YES (repair-or-build, per Mechanic work order) | UT-Body in Barton-Processes | Mechanic | One per lane. Lives in `Barton-Processes/factory/content/17NN-*/PROCESS-UT.md`. |
| Per-lane companion YAML (×5, conditional) | CONDITIONAL | Workflow-Body | Mechanic | Required iff the executable child UT has a machine-readable workflow surface; MD/YAML must not drift. |
| Lane Audit Book (×5) | YES on PASS | Audit-Body | Auditor | One per lane on Codex PASS. |
| LBB transition rows | YES | LBB record | All four roles | 4 transition rows per BAR per lane (planner / foreman / mechanic / auditor). |
| Mission Control evidence | CONDITIONAL | D1 row + dashboard link | Mechanic / Auditor | Required when a lane is operational. Block/defer note acceptable until lane reaches OPERATE. |

---

## §6 FOREMAN DISPATCH REQUIREMENTS — All Five Lanes

Foreman reads this Plan Book + Atlas §2 + intake (§2) and emits **literal `file:line | old_string | new_string` triples** as Mechanic dispatch packets (Process 070 §4 Step 3). Foreman produces no Library artifact. Sonnet is dispatched with `run_in_background=true`. Mechanic ≠ Auditor (Codex audits).

For each lane, Foreman emits **two work orders** — one per source-of-truth layer that owns documentation:

1. **Blueprint UT work order** → IMO-Creator v2 (`imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-17NN-*.md`)
2. **Executable child UT work order** → Barton-Processes (`Barton-Processes/factory/content/17NN-*/PROCESS-UT.md`)

Foreman additionally emits:

3. **Picker route binding work order** (lane 1750) covering `imo-creator-v2/workers/video-pipeline/scripts/route-video-job.ps1` so a script entering the system reaches the correct lane.
4. **Smoke-test work order** per lane: minimal end-to-end run that exercises the runtime surface and emits one piece of provider evidence (job ID, manifest row, or explicit blocker).

### §6.1 Lane: `heygen_avatar` (1710)

| Field | Value |
|-------|-------|
| Blueprint UT (parent) | `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1710-HEYGEN.md` |
| Executable child UT | `Barton-Processes/factory/content/1710-heygen-avatar/PROCESS-UT.md` |
| Runtime surface | HeyGen API |
| Required connector | HeyGen (Doppler `HEYGEN_API_KEY`) |
| Foreman dispatch hint | Repair both UTs to UT v2.8.0 + UT_CHECKLIST v1.3.1 conformance; preserve lane constants from parent Blueprint; do not duplicate provider research into the executable UT (it lives in the Blueprint). |
| Smoke-test goal | One avatar generation job ID OR explicit blocker note citing missing key/quota. |
| Evidence expected | avatar_ids, voice_ids, generation_job_id (or blocked note). |

### §6.2 Lane: `notebooklm_source_video` (1720)

| Field | Value |
|-------|-------|
| Blueprint UT | `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1720-NOTEBOOKLM.md` |
| Executable child UT | `Barton-Processes/factory/content/1720-notebooklm-source-video/PROCESS-UT.md` |
| Runtime surface | NotebookLM via Chrome MCP |
| Required connector | Chrome MCP browser session |
| Foreman dispatch hint | Document the source packaging contract (what enters NotebookLM, what exits as a video) in the Blueprint; document the operator runbook (browser session, export path) in the executable UT. |
| Smoke-test goal | One source notebook + export path screenshot OR explicit blocker citing browser session absence. |
| Evidence expected | source_notebook reference, export_path (or blocked note). |

### §6.3 Lane: `elevenlabs_cinematic` (1730)

| Field | Value |
|-------|-------|
| Blueprint UT | `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1730-ELEVENLABS.md` |
| Executable child UT | `Barton-Processes/factory/content/1730-elevenlabs-cinematic/PROCESS-UT.md` |
| Runtime surface | ElevenLabs API |
| Required connector | ElevenLabs (Doppler `ELEVENLABS_API_KEY`) |
| Foreman dispatch hint | Cover both cinematic voice and image-to-video paths in the Blueprint as lane variables; child UT pins the operating contract for an entering script. |
| Smoke-test goal | One generation job ID OR blocker. |
| Evidence expected | voice_ids, generation_job_id (or blocked note). |

### §6.4 Lane: `claude_code_sovereign` (1740)

| Field | Value |
|-------|-------|
| Blueprint UT | `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1740-SOVEREIGN.md` |
| Executable child UT | `Barton-Processes/factory/content/1740-claude-code-sovereign/PROCESS-UT.md` |
| Runtime surface | Claude Code + In Motion |
| Required connector | Local toolchain (Claude Code session, In Motion installed) |
| Foreman dispatch hint | Cite existing MP4 output evidence (`workers/video-pipeline/output/video-output-manifest.json`) as runtime proof; lane is the only one with prior live evidence — Mechanic should leverage that to set the OPERATE bar for the other four. |
| Smoke-test goal | One additional MP4 manifest row OR explicit blocker. |
| Evidence expected | manifest row, MP4 path. |

### §6.5 Lane: `video_picker` (1750)

| Field | Value |
|-------|-------|
| Blueprint UT | `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-1750-PICKER.md` |
| Executable child UT | `Barton-Processes/factory/content/1750-video-picker/PROCESS-UT.md` |
| Runtime binding | `imo-creator-v2/workers/video-pipeline/scripts/route-video-job.ps1` |
| Required connector | Local PowerShell + access to the four upstream lane runtimes |
| Foreman dispatch hint | This lane is the **entry seam** described by INV-05. The Blueprint defines the routing contract (script-in → lane-out); the executable UT defines the operator runbook for invoking the picker; the route harness implements it. The three must not drift. |
| Smoke-test goal | One end-to-end pick with a synthetic script that resolves to one of the four upstream lanes (or explicit blocker if none of the four can satisfy the smoke run). |
| Evidence expected | route decision log, downstream lane evidence, output manifest row OR blocker. |

### §6.6 Lane parallelism / dependency note (Foreman uses)

- Lanes 1710, 1720, 1730 are **independent** and may be dispatched in parallel.
- Lane 1740 is **independent** and has prior runtime evidence; its smoke test is the lowest-risk and should be dispatched first to set the OPERATE bar.
- Lane 1750 (picker) **depends** on at least one upstream lane being smoke-test green; Foreman dispatches 1750 last unless explicitly told otherwise by the sovereign.

---

## §7 MECHANIC WORK ORDERS

Per Process 070 §4 Step 4. Each work order obeys these scope and method rules. **The Planner does not over-prescribe Mechanic implementation details beyond the scope and evidence boundaries below.** Mechanic owns the route inside scope.

### §7.1 Allowed write scope (locked by intake §16)

- `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/` (Plan Book and Plan Book artifacts only)
- The two specific UT paths (Blueprint + executable child) named in the per-lane table for the lane the work order targets
- The picker route harness file for the 1750 work order only: `imo-creator-v2/workers/video-pipeline/scripts/route-video-job.ps1`
- Companion Workflow-Body YAMLs paired to a touched UT (BS Law Y-junction conformance — MD/YAML must not drift)

### §7.2 Forbidden (locked)

- Locked Atlas constants (the 16/17 read-only set; only `atlas/ATLAS.md` is amendable, and only with sovereign pre-authorization — NOT in scope for this BAR).
- Secrets or credential values in any artifact (use connector references).
- Unscoped executable process rewrites (work orders are per-lane, not cross-lane).
- Combining Mechanic and Auditor roles. Mechanic ≠ Auditor.
- Collapsing Blueprint and Execution homes into one repo.

### §7.3 Per work-order requirements

Every Mechanic work order must:

1. Cite the Plan Book (this file) and Process 070 §4 Step 4 as authority.
2. Read the Atlas + Process 070 + the per-lane sources before first edit (Step 0 read).
3. Repair or build the targeted UT to **UT v2.8.0 + UT_CHECKLIST v1.3.1** conformance: 14 sections, 13-item pre-flight, 16 stable anchors as required by `Barton-Processes/CLAUDE.md` §"PROCESS INDEX".
4. Preserve the source-of-truth split (§3). If a fact wants to live in two layers, choose the canonical layer and reference it from the other.
5. Conform any companion YAML to BS Law Y-junction (`outside:` and `inside:` distinct top-level maps).
6. Produce one LBB row via `scripts/lbb-log.sh --role mechanic --action edit --bar-id BAR-VIDEO-PATH-CERTIFICATION` after final edit (Process 070 §4 Step 4).
7. Verify `git diff HEAD -- <16 read-only constant paths>` returns empty before commit.
8. Emit a smoke-test result for the lane (per §6 lane table) OR an explicit blocker entry referencing §11 of this Plan Book.

### §7.4 Mechanic non-prescription clause

The Planner **does not** specify file:line dispatch triples in this Plan Book. Foreman emits literal triples per Process 070 §4 Step 3 once the sovereign signs the Plan Book. The Planner only locks the scope, evidence, and conformance gates above.

---

## §8 AUDITOR PACKET REQUIREMENTS

Per Process 070 §4 Step 5 and intake §17. Codex audits each lane work order independently; verdict is per-lane, not per-BAR aggregate.

### §8.1 Audit areas (every lane)

| Audit area | Evidence required |
|------------|-------------------|
| BS Law | MD/YAML structure conformant; outside/inside Y-junction on any companion YAML; no drift between paired MD and YAML. |
| UT conformance | All required UT v2.8.0 sections + UT_CHECKLIST v1.3.1 13-item pre-flight present in both Blueprint UT and executable child UT. |
| Source-of-truth split | Blueprint vs Execution vs Runtime vs Evidence — no layer silently absorbs another (§3). |
| Scope | Only allowed files changed (§7.1). Forbidden paths untouched (§7.2). `git diff HEAD` against the 16 locked constants returns empty. |
| Runtime safety | Smoke test produced provider evidence OR an explicit blocker entry with justification. No silent skip. |
| Evidence surfaces | LBB transition rows present for the four roles. Mission Control row or explicit defer note. Linear BAR(s) updated where reachable. |
| Connector evidence | Each connector named in §10 either produced expected evidence (§6 lane table) or has an explicit blocker entry (§11). |
| Research provenance | Brainstorming claims separated into facts (§13.A) vs assumptions (§13.B). Promotions are cited. |
| Aviation | Mechanic ≠ Auditor confirmed at every transition. Foreman did not flip the verdict. |
| K=C parity (§10b of PROC-070) | Parsed-value match where Codex computes equivalence (lesson BAR-397). Byte identity not required. |

### §8.2 Verdict format

- `VERDICT: P=1` with scoped file citations and Audit Book at `lbb.records` (`subject_id='processes'`, `species='Audit-Body'`) plus `lbb.logbook` CERTIFY row, **or**
- `VERDICT: P=0` with scoped file citations + squawk row in `mission-control.squawks` with `process_id='four-brain'`, `subject_id='processes'`. Strike count increments. Strike ladder applies (Process 070 §4 Step 6).

### §8.3 Strike ladder (Process 070 §4 Step 6)

- Strike 1 → Sonnet repair + Codex re-audit. Foreman re-dispatches.
- Strike 2 → Escalate to Opus 4.7 mechanic. Codex re-audits.
- Strike 3 → Troubleshoot/Train. No fourth repair without structural diagnosis. Airworthiness Directive if fleet-wide.

---

## §9 P=1 DEFINITION (LOCKED)

Quoted and adopted verbatim from intake §18 / `planner-intake.yaml.filled_intake.p1_definition`. **Do not leave P=1 implied.**

This Plan Book reaches P=1 when:

1. Plan Book exists at `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/PLAN-BOOK.md`.
2. Plan Book cites the Atlas, KEY, UT, Four-Brain, garage intake, video Blueprint index, and executable child UTs (§2 of this Plan Book satisfies this).
3. Plan Book defines Foreman dispatch requirements for all five video lanes (§6 satisfies this).
4. Plan Book preserves the source-of-truth split: Blueprint explains, Execution runs, Runtime implements, Evidence proves (§3 satisfies this; non-drift invariants in §12 reinforce).
5. Plan Book defines Mechanic work orders (§7), Auditor packet requirements (§8), smoke tests (§6 per lane), evidence surfaces (§10), and stop conditions (§11).
6. Plan Book names any blocked connector, credential, browser session, provider gate, or Linear/LBB gap instead of hiding it (§11).
7. ForeBrain garage writes `FINAL-PRODUCT.yaml` pointing to the durable Plan Book.

> **Aggregate BAR P=1** (downstream of this Plan Book): each of the five lanes reaches Codex `VERDICT: P=1` with Audit Book + CERTIFY row; the picker (1750) routes a script to a smoke-test-green lane end-to-end; Mission Control surfaces the lane as OPERATE-eligible OR records explicit blocker per §11.

---

## §10 EVIDENCE / CONNECTOR REQUIREMENTS

### §10.1 Evidence surfaces (per intake §14 storage/evidence contract)

| Store | Role | Required when |
|-------|-----|----------------|
| LBB | Compliance logbook + durable memory | Every role transition + closeout. 4 LBB rows per BAR per lane minimum (Process 070 §10a). |
| Mission Control | Operator visibility | Lane is operational. Block/defer note acceptable while lane is BUILD. |
| GitHub | Versioned source | Any audited file change. Branch + commit/PR cited in Audit Book. |
| Linear | BAR tracker | Pull current status of BAR-388…392 if reachable; record as block/defer note otherwise. |
| Provider runtimes | Job evidence | Per §6 lane evidence column. |
| R2 / D1 | Workbench / vault | Only if the lane uses staged data cycles; not required by default for documentation BARs. |

### §10.2 Connectors used / blocked status (intake §10)

| Connector | Status (Plan Book stage) | Action required by Mechanic / Auditor |
|-----------|---------------------------|----------------------------------------|
| Atlas (local repo) | USED | Cite exact paths and sections (done in §2). |
| Process 070 garage | USED | Garage moved BAR to `PLANNER_RUNNING`; will write `FINAL-PRODUCT.yaml` after sovereign accept. |
| LBB | NOT YET QUERIED at Plan Book stage — DEFERRED | Mechanic must query LBB for prior records on BARs 388–392 + search terms (intake §9) before first edit. If LBB unreachable, record block note in §11 of this Plan Book at audit time. |
| Linear / BAR tracker | NOT YET QUERIED at Plan Book stage — DEFERRED | Mechanic must pull BARs 388–392 status snapshots before first edit, or block-note in §11. |
| GitHub | USED on artifact write | Standard CLI / connector. |
| Mission Control | NOT YET QUERIED — CONDITIONAL | Required when a lane operationally runs. Defer note acceptable until then. |
| HeyGen (Doppler `HEYGEN_API_KEY`) | UNVERIFIED at Plan Book stage | Mechanic confirms key reachable before lane 1710 smoke test or block-notes. |
| ElevenLabs (Doppler `ELEVENLABS_API_KEY`) | UNVERIFIED at Plan Book stage | Mechanic confirms key reachable before lane 1730 smoke test or block-notes. |
| Chrome MCP / NotebookLM | UNVERIFIED at Plan Book stage | Mechanic confirms session before lane 1720 smoke test or block-notes. |
| Cloudflare R2 / D1 | NOT IN SCOPE for documentation BAR | Required only if upload/stream lane added later. |

> **Connector rule (locked from intake):** No connector access = explicit blocker/defer note, not silent omission.

---

## §11 STOP CONDITIONS / OPEN BLOCKERS

### §11.1 Stop conditions (locked)

The Plan Book's authorized work halts immediately if any of the following triggers fires. Mechanic must record the trigger in LBB and surface to Foreman.

| ID | Stop trigger | Action |
|----|--------------|--------|
| STOP-01 | Locked Atlas constant modification attempted (any of the 16 read-only constants). | Halt. `git revert`. No further dispatch. |
| STOP-02 | Foreman attempts to flip an Auditor verdict. | Halt. Record squawk. Sovereign notified. |
| STOP-03 | Mechanic attempts to audit own work. | Halt. Aviation Model violation. |
| STOP-04 | Strike 3 reached on the same lane work order. | Halt. Convert to Troubleshoot/Train. No fourth repair. |
| STOP-05 | Source-of-truth split collapse detected (Blueprint and executable UT becoming the same content). | Halt. Repair to restore split. |
| STOP-06 | Secret value committed to any artifact in scope. | Halt. Rotate secret. `git revert`. Squawk. |
| STOP-07 | `forebrain-garage.sh final` fails to write `FINAL-PRODUCT.yaml`. | Halt. Investigate garage state before declaring P=1. |
| STOP-08 | Plan Book and intake YAML drift on `lanes`, `source_of_truth_split`, or `p1_definition`. | Halt. Reconcile via §13. |

### §11.2 Open blockers (Plan Book stage)

| ID | Blocker | Owner | Resolution path |
|----|---------|-------|------------------|
| BLOCK-01 | Five parent Blueprint UT files (`VIDEO-BP-17NN-*.md`) and five executable child UTs in `Barton-Processes/factory/content/17NN-*/` are referenced by the intake; their existence and conformance have **not** been verified by the Planner at this stage (Planner is sources-only per role). | Mechanic at Step 0 read | Mechanic verifies presence + conformance before first edit. If a file is missing, the lane work order shifts from REPAIR to BUILD; record in LBB. |
| BLOCK-02 | LBB connectivity from this session was not exercised by the Planner. | Mechanic | Query LBB once; if unreachable, defer-note. |
| BLOCK-03 | Linear BAR-388…392 status snapshots not pulled at Plan Book stage. | Mechanic | Pull at Step 0 read or defer-note. |
| BLOCK-04 | Provider connectors (HeyGen, ElevenLabs, Chrome MCP) reachability unknown at Plan Book stage. | Mechanic per lane | Reachability check during smoke-test prep; explicit block note if down. |
| BLOCK-05 | Mission Control dashboard URL is TBD per Process 070 §3. | Foreman / Sovereign | Acceptable until lanes reach OPERATE; defer-note until then. |

> Intake §19 explicitly listed **no** intake-blocking questions. Runtime/provider gaps are recorded here, not as intake blockers.

---

## §12 NON-DRIFT INVARIANTS (LOCKED)

Adopted from intake §12 + common invariants. **Locked. Do not modify.**

| ID | Invariant |
|----|-----------|
| INV-01 | IMO-Creator v2 holds parent video Blueprint UTs and reusable documentation. |
| INV-02 | Barton-Processes holds executable video Process UTs. |
| INV-03 | Process 070 garage is the start surface for Planner work. |
| INV-04 | `FINAL-PRODUCT.yaml` is the pickup ticket for the durable Plan Book. |
| INV-05 | A script must be able to enter the system and route to the correct video lane after Foreman dispatches and Mechanic builds. |
| INV-COMMON-01 | The Planner owns the plan; the intake owns only desired outcome and constraints. |
| INV-COMMON-02 | Foreman dispatches; Mechanic builds; Auditor certifies. |
| INV-COMMON-03 | Mechanic cannot audit its own work. |
| INV-COMMON-04 | BS Law applies to every durable structured artifact. |
| INV-COMMON-05 | Blueprint, execution, runtime, and evidence layers must not drift. |

---

## §13 RESEARCH PROVENANCE

Per intake §8 fact-handling rule: brainstorming is input, not certification.

### §13.A Brainstorming claims promoted to FACTS (cited)

| Claim | Citation |
|-------|----------|
| IMO-Creator v2 Blueprint is a UT and Barton-Processes holds executable UTs (Dave's two-layer rule). | `imo-creator-v2/atlas/ATLAS.md`; `Barton-Processes/CLAUDE.md` "Identity" section: "Blueprint repos = brain. This repo = muscle." |
| Process 070 is Planner → Foreman → Mechanic → Auditor. | `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` §1 + §4. |
| ForeBrain garage starts at `garage/inbox/BAR-{id}` and final pickup is `FINAL-PRODUCT.yaml`. | `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` (commands `new`, `run-once --execute`, `final`). |
| Existing Claude Code + In Motion MP4 evidence exists. | `imo-creator-v2/workers/video-pipeline/output/video-output-manifest.json` (intake §7). |
| Five video lanes are the scope: heygen_avatar, notebooklm_source_video, elevenlabs_cinematic, claude_code_sovereign, video_picker. | `planner-intake.yaml.filled_intake.lanes` (5 entries). |

### §13.B Brainstorming claims left as ASSUMPTIONS (Mechanic to verify)

| Assumption | Verification path |
|-----------|-------------------|
| All five parent Blueprint UTs at `imo-creator-v2/docs/processes/video-blueprints/lanes/VIDEO-BP-17NN-*.md` exist and are UT-conformant. | Mechanic Step 0 read; build if missing. |
| All five executable child UTs at `Barton-Processes/factory/content/17NN-*/PROCESS-UT.md` exist and are UT-conformant. | Mechanic Step 0 read; build/repair as discovered. |
| HeyGen / ElevenLabs / Chrome MCP credentials are reachable. | Connector reachability check pre-smoke-test. |
| `route-video-job.ps1` is the canonical picker entry point and accepts a script payload that resolves to one of the four lanes. | Mechanic reads file; confirms input contract or repairs to it. |
| Linear BARs 388–392 are the in-flight tracker IDs for the lane work. | Mechanic pulls Linear; reconciles or block-notes. |

---

## §14 LB&B PULL CONTRACT (intake §9 — unchanged)

| Field | Fill |
|-------|------|
| Work IDs / BAR IDs | BAR-VIDEO-PATH-CERTIFICATION, BAR-388, BAR-389, BAR-390, BAR-391, BAR-392, PROC-070, 1710, 1720, 1730, 1740, 1750 |
| Search terms | video paths, HeyGen, NotebookLM, ElevenLabs, Claude Code, In Motion, picker, Fish voice, cinematic video, video garage |
| Time window | since 2026-05-01 |
| Required records | Planner notes, Foreman dispatches, Mechanic outputs, Auditor verdicts, closeout logs |
| Evidence needed for P=1 | Per-role transition rows for each lane work order; Audit Book + CERTIFY row on PASS |

> If LB&B is unavailable at Mechanic / Auditor time, the role must mark evidence blocked or deferred (§11 BLOCK-02) — never silently skip.

---

## §15 PROCESS 070 START / HANDOFF PATH

Per intake §11 and `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh`.

| Step | Status | Owner | Output |
|------|--------|-------|--------|
| 1. `forebrain-garage.sh new BAR-VIDEO-PATH-CERTIFICATION` | DONE | Operator | BAR intake folder |
| 2. Fill `PLANNER-INTAKE.md` | DONE | Operator | Human-readable packet |
| 3. Fill `planner-intake.yaml`, set `garage_status: READY_FOR_PLANNER` | DONE | Operator | Machine-readable ready signal |
| 4. `forebrain-garage.sh run-once --execute` | DONE | ForeBrain garage | Planner claimed (`PLANNER_RUNNING`) |
| 5. Planner writes `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/PLAN-BOOK.md` | **DONE — this file** | Planner | Plan Book (this document) |
| 6. Garage writes `outbox/BAR-VIDEO-PATH-CERTIFICATION/FINAL-PRODUCT.yaml` | PENDING | ForeBrain garage | `FINAL-PRODUCT.yaml` pointer |
| 7. Sovereign approves or corrects this Plan Book | PENDING | Dave Barton | Signed Plan Book |
| 8. Foreman dispatches Mechanic work orders from §6 / §7 | PENDING | Foreman | Scoped work packets |
| 9. Mechanic builds; Auditor audits; LB&B logs each transition | PENDING | Mechanic / Auditor | P=1 or P=0 + evidence per lane |

> Do not call this BAR complete until step 6 fires (`FINAL-PRODUCT.yaml` exists).

---

## §16 PLANNER DELIVERABLES INDEX (intake §15)

| Deliverable | Section in this Plan Book |
|-------------|----------------------------|
| Plan Book path | Header + §1 |
| Read set | §4 + §2 |
| Source-of-truth split | §3 |
| Required artifacts | §5 |
| Mechanic work orders | §6 + §7 |
| Auditor packet | §8 |
| P=1 definition | §9 |
| Stop conditions | §11.1 |
| Open blockers | §11.2 |
| Evidence requirements | §10 |
| LB&B records used or required | §10.2 + §14 |
| Connectors used or blocked | §10.2 |
| 070 start / handoff path | §15 |
| Brainstorming claims promoted to facts | §13.A |
| Brainstorming claims left as assumptions | §13.B |
| Non-drift invariants | §12 |

---

## §17 DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Created | 2026-05-05 |
| Last Modified | 2026-05-05 |
| Status | PLAN_BOOK_READY |
| Authority | Dave Barton (sovereign) |
| Authored By | Process 070 Planner (ForeBrain garage role) |
| Conformance | Plan-Body species (Book Law v1.5.0); Atlas inheritance; Process 070 PROCESS-UT v1.0.0; intake YAML v1.0.0 |
| Signed By | ☐ (sovereign signs at Process 070 §15 step 7) |
| BAR | BAR-VIDEO-PATH-CERTIFICATION |
| Garage Final Product Pointer | `Barton-Processes/factory/imo-creator/070-four-brain/garage/outbox/BAR-VIDEO-PATH-CERTIFICATION/FINAL-PRODUCT.yaml` (to be written by `forebrain-garage.sh final`) |

# PLAN BOOK — BAR-PLANNER-INTAKE-REFINE (v2)

**Species:** Plan-Body
**Process:** PROC-070 Four-Brain (Planner artifact)
**Target Process:** PROC-070 / Four-Brain Aviation Model — Planner Intake Template Replacement (thin client-brief shape) + downstream UT sync + Planner-config artifact in imo-creator-v2
**Operating Mode:** BUILD (sub-mode: maintenance — delta against existing v1.0.0 template)
**Authored:** 2026-05-06
**Author:** Planner (Opus 4.7, ForeBrain)
**Status:** PLAN_BOOK_SIGNED (auto-advance per G-19; no sovereign mid-pipeline gate)
**Supersedes:** Plan Book v1 (same path); old run dir `garage/runs/BAR-PLANNER-INTAKE-REFINE/20260506T132146Z/` preserved as audit history.

---

## §1 IDENTITY

| Field | Value |
|---|---|
| BAR / Work ID | `BAR-PLANNER-INTAKE-REFINE` |
| Target Process | PROC-070 / Four-Brain — Planner Intake Template replacement + downstream sync + Planner-config |
| Sovereign | Dave Barton |
| Hub | barton-processes |
| ctb_node | `barton-enterprises/imo-creator/processes/four-brain` |
| Intake (MD) | `factory/imo-creator/070-four-brain/garage/inbox/BAR-PLANNER-INTAKE-REFINE/PLANNER-INTAKE.md` (REVISED 2026-05-06) |
| Intake (YAML) | `factory/imo-creator/070-four-brain/garage/inbox/BAR-PLANNER-INTAKE-REFINE/planner-intake.yaml` |
| Conversation Source (canonical, gaps + drift vectors) | LBB record `090520d7-ff64-4b6e-9e14-5e8928b24db7` |
| Conversation Source (G-19 lock) | LBB record `1f19c519-f402-421f-bb5c-8eeaa7f7d9e9` |
| Conversation Source (historical, reference-only) | LBB record `54214381-4d34-4717-8284-6407c483d21a` |
| Plan Book Path | `docs/plans/BAR-PLANNER-INTAKE-REFINE/PLAN-BOOK.md` (this file) |
| Aviation Roles | Planner: Opus 4.7 · Foreman: Opus 4.7 · Mechanic: Sonnet · Auditor: Codex (Mechanic ≠ Auditor) |
| Self-Modification Flag | YES (`target_is_four_brain = true`) — rollback + skeleton-integrity audit gates apply |

---

## §2 DESIRED OUTCOME (P=O)

**Replace** `PLANNER-INTAKE-TEMPLATE.md` and its paired YAML with a thin, client-brief-shaped template (4 mandatory + 1 conditional follow-up + 6 optional fields, plain-language only). Sync four downstream artifacts. Implement the G-19 auto-advance pipeline. All edits stay inside locked skeletons (Atlas C&V Test).

**Five artifacts updated lock-step:**

1. `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` — replaced with the thin shape (~30–50 lines; questions in order WHERE FROM → WHAT → WHERE TO → TYPE [+ conditional Q4A]; plain language only). Version bump `1.0.0 → 2.0.0` (breaking shape change).
2. `Barton-Processes/factory/imo-creator/070-four-brain/planner-intake-template.yaml` — paired YAML, BS Law Y-junction conformant, version-matched.
3. `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` — variable fill within 14-section + 13-item UT_CHECKLIST skeleton; reflect new template version; §14 Maintenance Logbook row appended; remove Q-01..Q-04 references (moot under v2 design).
4. `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` — lock-step with PROCESS-UT.md.
5. `imo-creator-v2/atlas/constants/PLANNER_ROLE.md` — **NEW Planner-config artifact** declaring read-set wiring (CTB, Atlas altitude scale, paired-artifacts, STRUCTURE_MANIFEST, CLAUDE.md locked constants, LBB) so Planner pulls all maps without the human declaring them in a brief.

The Plan Book itself does **not** build these artifacts. It tells Foreman exactly what Mechanic must build and what Auditor must certify. The 14-section UT skeleton, 13-item UT_CHECKLIST, BS Law Y-junction, and Book Law species declarations are CONSTANTS. Only variable fill is in scope.

---

## §3 SOURCE-OF-TRUTH SPLIT (Preserved from Intake)

| Layer | Home |
|---|---|
| Blueprint architecture | `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` v1.2.0 |
| Execution operations | `Barton-Processes/factory/imo-creator/070-four-brain/` |
| Runtime deployment | `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` |
| Evidence / observability | LBB (records `090520d7…`, `1f19c519…`) + mission-control D1 (`four_brain_run`, `four_brain_transition`) |
| Planner config (NEW) | `imo-creator-v2/atlas/constants/PLANNER_ROLE.md` |

Children conform to parents. No layer crosses; no locked-constant edits.

---

## §4 ATLAS STEP 0 — SOURCES CONSULTED

Per Atlas pre-flight for the Planner role.

| # | Source | Section / Claim |
|---|---|---|
| 1 | `imo-creator-v2/atlas/constants/KEY.md` | Vocabulary (BAR, Plan Book, UT Book, Audit Book, HEIR, ORBT, Y-junction). |
| 2 | `imo-creator-v2/atlas/constants/BS_LAW.md` v1.5.0 | Universal Y-junction requirement on every durable structured artifact. |
| 3 | `imo-creator-v2/atlas/constants/BOOK_LAW.md` v1.5.0 | Workflow-Body / UT-Body / Plan-Body / Audit-Body species declarations. |
| 4 | `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` v1.2.0 | Pipeline doctrine: Planner→Foreman→Mechanic→Auditor; Mechanic ≠ Auditor; Two-Mode Dispatch (Build / Fix / Maintenance with cadence cron); Pressure Gauge; Strike system; Maintenance findings do **not** accumulate strikes. |
| 5 | `imo-creator-v2/atlas/manifests/STRUCTURE_MANIFEST.yaml` | Repo structure invariants for Mechanic write paths. |
| 6 | `imo-creator-v2/atlas/manifests/paired-artifacts.yaml` | Registry for paired `.md`/`.yaml` lock-step. Foreman verifies row 9 before dispatch. |
| 7 | `imo-creator-v2/atlas/ATLAS.md` §1.2.3 | Altitude scale 50K/40K/30K/10K/5K; sovereign at 50K. |
| 8 | `imo-creator-v2/atlas/ATLAS.md` §6 + §7.3a | Governance + paired-artifact registry row 9. |
| 9 | `imo-creator-v2/CLAUDE.md` §"Seventeen Constants" + §"Sovereign-Lock Protocol" | Locked-constants list (off-limits to Mechanic). |
| 10 | `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` | Current PROC-070 UT-Body baseline (v1.0.0). |
| 11 | `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` | Current Workflow-Body baseline (v1.0.0). |
| 12 | `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` v1.0.0 | Template baseline being replaced. |
| 13 | `Barton-Processes/factory/imo-creator/070-four-brain/planner-intake-template.yaml` v1.0.0 | Paired YAML baseline. |
| 14 | LBB record `090520d7-ff64-4b6e-9e14-5e8928b24db7` | Canonical conversation summary; gaps G-01..G-18; 9 drift vectors; invariants; P=1. |
| 15 | LBB record `1f19c519-f402-421f-bb5c-8eeaa7f7d9e9` | G-19 lock — no inter-stage sovereign gates. |
| 16 | LBB record `54214381-4d34-4717-8284-6407c483d21a` | Historical first ingest; reference only. |
| 17 | `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml` | Gate spec source of truth (Auditor primary read). |
| 18 | `imo-creator-v2/atlas/constants/UT_CHECKLIST.md` v1.3.1 | 13-item UT pre-flight checklist (constant). |

---

## §5 SCOPE — IN AND OUT

**IN SCOPE (Mechanic write set):**

- Replace `PLANNER-INTAKE-TEMPLATE.md` content (template-shape change permitted; this BAR's variable fill is the template body itself, since Plan-Body / Workflow-Body skeletons are the protected constants, not the template instance shape).
- Replace `planner-intake-template.yaml` content lock-step.
- Variable fill within `PROCESS-UT.md` (no skeleton restructuring; §14 row appended).
- Variable fill within `four-brain.yaml` lock-step.
- Create `imo-creator-v2/atlas/constants/PLANNER_ROLE.md` (new Planner-config artifact — non-locked; sovereign confirms placement).
- Refactor `forebrain-garage.sh` to implement G-19 auto-advance: remove `REVIEW_PLAN_BOOK` / `REVIEW_DIFF` sovereign-gating statuses; advance `PLAN_BOOK_READY → FOREMAN_DISPATCHED → MECHANIC_RUNNING → AUDIT_RUNNING → CERTIFIED` on stage exit code 0; failure routes to Strike system.
- Implement G-15 (`pinned_atlas_version`, `pinned_gate_spec_version` in Plan-Body species).
- Implement G-16 (`plan_book_ttl_hours` field + Foreman re-validation hook).
- Implement G-17 (file-level concurrency check at Foreman dispatch — overlapping `allowed_write_scope` blocked or queued; `bar_locks` D1 table or file-based tracker).
- Implement G-18 (every gate in `four-brain-doctrine-gate.yaml` carries a deterministic predicate; LLM-tail gates marked `requires_llm_tail=true` with deterministic fallback test).

**OUT OF SCOPE (do not touch):**

- The 17 locked constants under `imo-creator-v2/atlas/constants/` (sovereign-only amendment).
- `imo-creator-v2/atlas/ATLAS.md` (sovereign-only via pending-atlas-updates queue, not this BAR).
- Other process intake templates under `Barton-Processes/factory/*/`.
- CLI runner / D1 migration (BAR-FOUR-BRAIN-CLI).
- Skeleton restructuring of any UT (sections, ordering, required UT_CHECKLIST items, paired-artifact Y-junction, Book Law species declarations).
- imo-creator four-brain UT path update (per intake §"NOTE ON Q-01/02/03/04" — dropped from this BAR; PLANNER_ROLE.md replaces it as the imo-creator-v2-side artifact).

---

## §6 NEW TEMPLATE SHAPE (Locked Design from 2026-05-06 Sovereign Session)

### 6a Question Order (TYPE asked LAST + conditional follow-up)

```
Q1. WHERE FROM    — where is the information coming from
Q2. WHAT          — what do you want done with it
Q3. WHERE TO      — where does the information go
Q4. TYPE          — [1=Build · 2=Fix · 3=Maintenance]
   if Q4=1 (Build):       Q4A. MAINTENANCE CADENCE — A/B/C/D-check schedule
   if Q4=2 (Fix):         Q4A. SQUAWK / SYMPTOM     — what triggered this fix
   if Q4=3 (Maintenance): Q4A. CHECK LEVEL          — A-check / B-check / C-check / D-check / AD
```

Mandatory: 4 base + 1 conditional follow-up = 5 total.

### 6b Aviation Analogy (locks TYPE taxonomy)

- **Build** → factory floor; new construction; cadence declared at birth so the garage knows when to inspect.
- **Fix** → garage repair bay; reactive, squawk-driven; symptom captured for traceability.
- **Maintenance** → garage scheduled-tune-up bay; A/B/C/D-checks per FAA-style schedule.

### 6c Edge-Case Routing (default until proven wrong)

- Refactor → Build (new shape, even if file exists).
- Research → Build (output is a new findings doc).
- Delete → Fix (squawk = "this is dead weight").
- A 4th type is only added if default routing produces wrong audit behavior on >3 consecutive BARs.

### 6d Pipeline Behavior Driven by TYPE

| TYPE | Strike accumulates? | Audit mode | Cron-eligible? |
|---|---|---|---|
| Build | yes | full conformance | no — sovereign or LLM dispatch |
| Fix | yes | delta + regression | no — squawk-driven |
| Maintenance | **no** (per FOUR_BRAIN_AVIATION v1.1.0+) | delta + drift sweep | yes — A/B/C/D-check cron |

Single Process 070 stays. TYPE is metadata on the BAR; downstream stages read it and tune audit packet, strike accounting, cron eligibility.

### 6e Optional Helpers (cap = 6, sovereign sign-off to add new)

`WHY` · `WHO FOR` · `DEADLINE` · `CONSTRAINTS` · `EXISTING` · `REFERENCE` — all client-vocabulary, no engineering terms.

### 6f Planner-Side Auto-Wiring (no human burden)

Planner pulls automatically; human never declares:

- CTB tree → `imo-creator-v2/atlas/constants/BARTON_ENTERPRISES_CTB.md`
- Altitude scale → `imo-creator-v2/atlas/ATLAS.md` §1.2.3
- Existing paired artifacts → `imo-creator-v2/atlas/manifests/paired-artifacts.yaml`
- Repo structure → `imo-creator-v2/atlas/manifests/STRUCTURE_MANIFEST.yaml`
- Locked constants → `imo-creator-v2/CLAUDE.md`
- Prior art / decisions → LBB (subjects: `system`, `processes`)

Pointers live in `PLANNER_ROLE.md`, **not** in the template.

### 6g Quality Bail-Out

If a brief is sub-actionable (vacuous fills like "from my brain / make it nice / repo"), Planner asks ONE targeted question to fill the specific gap before producing a Plan Book. Asking is the exception, not the default.

### 6h G-19 Doctrine Lock

Sovereign touchpoints exist at exactly two boundaries: **template-drop** (input) and **Auditor verdict** (output). NO sovereign approval gates between Planner / Foreman / Mechanic / Auditor. Pipeline auto-advances on stage success. Mission Control surfaces transitions as observation only. Garage statuses `REVIEW_PLAN_BOOK`, `REVIEW_DIFF` (and any sovereign-gating equivalents) are removed and replaced with auto-advance transitions.

---

## §7 MECHANIC WORK ORDERS (Foreman-ready, file-level)

Foreman dispatches Sonnet with literal `file:line | old | new` triples. Below is the Plan-Book-level work breakdown; Foreman expands to literal pairs at dispatch time.

### WO-1 — Replace PLANNER-INTAKE-TEMPLATE.md

- **Path:** `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md`
- **Edit mode:** full body replace (template-instance shape is variable per Atlas C&V Test; Plan-Body species skeleton is the constant).
- **Required body:** the §6 design — questions in order, plain language, conditional Q4A, 6 optional helpers, quality bail-out note, G-19 reference. ~30–50 lines.
- **Version:** `1.0.0 → 2.0.0` (breaking shape).
- **Header pinning:** `pinned_atlas_version: v2.2.6` · `pinned_gate_spec_version: <current four-brain-doctrine-gate.yaml version>` · `plan_book_ttl_hours: <human-set, default 168>`.

### WO-2 — Replace planner-intake-template.yaml

- **Path:** `Barton-Processes/factory/imo-creator/070-four-brain/planner-intake-template.yaml`
- **Edit mode:** full body replace, lock-step with WO-1.
- **Required:** BS Law Y-junction (`outside:` + `inside:` distinct top-level constructs), Book Law species `Plan-Body-Template`, `version: "2.0.0"`, `paired_md: PLANNER-INTAKE-TEMPLATE.md`, fields mirroring §6 questions (q1_where_from, q2_what, q3_where_to, q4_type, q4a_conditional with `oneOf` schema), optional helpers schema, G-15/G-16 fields, planner_auto_wiring read-set pointers.

### WO-3 — PROCESS-UT.md variable fill

- **Path:** `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md`
- **Edit mode:** variable fill within 14-section + 13-item UT_CHECKLIST skeleton — NO restructuring.
- **Edits:**
  - §1 IDENTITY: bump version `1.0.0 → 1.1.0`, update `Last Modified` to `2026-05-06`.
  - §2 PRD: add reference to thin-template v2.0.0; remove any Q-01..Q-04 mentions.
  - §4 MIDDLE: add note that the Planner Intake Template is now thin (4+1 mandatory, 6 optional) and Planner auto-wires read-set per `imo-creator-v2/atlas/constants/PLANNER_ROLE.md`.
  - §5 OSAM READ: add `PLANNER_ROLE.md` to Planner read list.
  - §10b Tolerances: note Maintenance findings do NOT accumulate Strikes (per FOUR_BRAIN_AVIATION v1.1.0+).
  - §13 DOCUMENT CONTROL: bump version, last-modified.
  - §14 MAINTENANCE LOGBOOK: append row for BAR-PLANNER-INTAKE-REFINE — `2026-05-06 | 1.1.0 | BAR-PLANNER-INTAKE-REFINE | Sonnet Mechanic | UPDATE — Reflect Planner Intake Template v2.0.0 (thin shape); add PLANNER_ROLE.md to OSAM READ; G-15/G-16/G-17/G-18/G-19 doctrine pinned; Q-01..Q-04 retired.`

### WO-4 — four-brain.yaml lock-step

- **Path:** `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml`
- **Edit mode:** variable fill, lock-step with WO-3.
- **Edits:** bump `version: "1.0.0" → "1.1.0"`, `last_modified: "2026-05-06"`, `inherits.aviation_model` unchanged (still v1.2.0); add `planner_role_artifact: imo-creator-v2/atlas/constants/PLANNER_ROLE.md` reference under `inside.heir`; add G-15/G-16/G-17/G-18/G-19 pinned-version + ttl + concurrency + deterministic-gate fields under `inside.runtime` block; preserve BS Law Y-junction.

### WO-5 — Create PLANNER_ROLE.md (NEW)

- **Path:** `imo-creator-v2/atlas/constants/PLANNER_ROLE.md`
- **Edit mode:** new file (non-locked artifact; sovereign confirms placement at first review — Planner has flagged `imo-creator-v2/atlas/constants/` as the right home).
- **Required content:** Planner-role manual; declares read-set pointers (CTB, altitude scale, paired-artifacts, STRUCTURE_MANIFEST, CLAUDE.md locked constants, LBB subjects) so Planner pulls all maps automatically; documents the quality bail-out rule; documents the Planner→Foreman handoff contract (Plan Book delivered to `docs/plans/<BAR>/PLAN-BOOK.md`); references `FOUR_BRAIN_AVIATION.md` v1.2.0 as parent.
- **Skeleton:** UT-Body or Workflow-Body species (Mechanic chooses UT-Body since this is a role manual; sovereign confirms at audit). BS Law Y-junction with paired YAML if Mechanic creates one (Mechanic decides at build time; Auditor checks pair-or-not consistency).

### WO-6 — forebrain-garage.sh G-19 refactor

- **Path:** `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh`
- **Edit mode:** functional refactor.
- **Edits:** remove sovereign-gating statuses (`REVIEW_PLAN_BOOK`, `REVIEW_DIFF`, etc.); implement auto-advance on stage exit code 0; failure exit codes route through Strike system; surface transitions to Mission Control as observation only (no approve/reject); add G-17 file-level concurrency check (compare candidate BAR `allowed_write_scope` against `bar_locks` table — block or queue overlapping); add G-16 Plan-Book-TTL re-validation hook before Foreman dispatch.

### WO-7 — four-brain-doctrine-gate.yaml deterministic predicates

- **Path:** `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml`
- **Edit mode:** variable fill — add deterministic predicate (regex / hash / file-existence / git-diff / JSON-schema) to every gate; LLM-tail-judgment gates carry `requires_llm_tail: true` plus a deterministic fallback test.
- **Note:** This file is under `imo-creator-v2/atlas/manifests/` — sovereign confirms it is NOT in the locked-constants list before Mechanic edits. If sovereign flags it as locked, Mechanic halts and routes to pending-atlas-updates queue.

### WO-8 — Optional: bar_locks tracking surface

- **Path:** Mechanic chooses (`Barton-Processes/factory/imo-creator/070-four-brain/garage/bar_locks.yaml` or D1 migration deferred to BAR-FOUR-BRAIN-CLI).
- **Edit mode:** new artifact OR documented deferral.
- **Acceptance:** if file-based, schema = `{ bar_id, allowed_write_scope[], claimed_at, released_at }`. If deferred to D1 BAR, document in PROCESS-UT.md §11 OUT OF SCOPE.

---

## §8 AUDITOR PACKET

Codex (different inference engine than Sonnet) audits all artifacts against the gate spec + BAR-specific gates below. Verdict format: `VERDICT: P=1` (PASS) or `VERDICT: P=0` (FAIL). Mechanic ≠ Auditor invariant verified at every transition.

### 8a Standard Gates (G01–G10 from four-brain-doctrine-gate.yaml)

Apply per `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml`. All 10 must PASS.

### 8b BAR-Specific Gates

| Gate | Predicate | Method |
|---|---|---|
| BAR-G-A | PLANNER-INTAKE-TEMPLATE.md is at version 2.0.0 and contains Q1..Q4 in correct order with conditional Q4A. | regex + structural parse |
| BAR-G-B | planner-intake-template.yaml lock-step: same version, BS Law Y-junction conformant, Plan-Body-Template species declared. | YAML parse + schema check |
| BAR-G-C | PROCESS-UT.md skeleton integrity: 14 sections present in canonical order, 13-item UT_CHECKLIST present, paired companion YAML reference present. | structural diff vs. v1.0.0 skeleton baseline |
| BAR-G-D | four-brain.yaml lock-step: version match, BS Law Y-junction preserved. | YAML parse |
| BAR-G-E | PLANNER_ROLE.md exists at `imo-creator-v2/atlas/constants/PLANNER_ROLE.md`, declares Planner read-set wiring, cites FOUR_BRAIN_AVIATION.md v1.2.0 as parent. | file-existence + content regex |
| BAR-G-F | No locked constant modified. `git diff HEAD -- <17 locked-constant paths>` returns empty. | git diff |
| BAR-G-G | No other process intake template under `Barton-Processes/factory/*/` modified. | git diff path filter |
| BAR-G-H | G-15 fields present (`pinned_atlas_version`, `pinned_gate_spec_version`) in template and Plan-Body species. | YAML parse |
| BAR-G-I | G-16 field present (`plan_book_ttl_hours`) and Foreman re-validation hook implemented in forebrain-garage.sh. | YAML parse + grep on hook function |
| BAR-G-J | G-17 concurrency check active in forebrain-garage.sh; `bar_locks` surface present (file or documented deferral). | grep + artifact existence |
| BAR-G-K | G-18: every gate in four-brain-doctrine-gate.yaml has deterministic predicate; LLM-tail gates flagged. | YAML parse |
| BAR-G-L | G-19: forebrain-garage.sh contains NO `REVIEW_PLAN_BOOK` / `REVIEW_DIFF` sovereign-gating statuses; auto-advance transitions present. | grep |
| BAR-G-M | Aviation Model role separation: Mechanic transition rows in LBB show model=sonnet; Auditor row shows model=codex. | LBB query |
| BAR-G-N | Q-01..Q-04 references removed from PROCESS-UT.md. | grep |
| BAR-G-O | Brainstorming-claim provenance: every accepted gap (G-01..G-19) has a citation in this Plan Book §10; rejected/deferred ones documented as assumptions in §11. | manual + cross-ref |
| BAR-G-P | Skeleton integrity on PROCESS-UT.md verified against UT v2.8.0 + UT_CHECKLIST v1.3.1. | structural validator |

### 8c Evidence Required for PASS

- LBB record `090520d7-ff64-4b6e-9e14-5e8928b24db7` cited in this Plan Book ✅ (cited §1, §4).
- LBB record `1f19c519-f402-421f-bb5c-8eeaa7f7d9e9` cited (G-19 lock) ✅ (cited §1, §4, §6h).
- 4 LBB transition rows minimum (planner / foreman / mechanic / auditor) for this BAR.
- Audit Book row in `lbb.records` on Codex PASS.
- CERTIFY row in `lbb.logbook` on BAR P=1.
- `FINAL-PRODUCT.yaml` written to `garage/outbox/BAR-PLANNER-INTAKE-REFINE/` pointing to all 5+ refined artifacts.

### 8d Connector Evidence

- LBB: read of canonical record + 4 transition writes + Audit Book write + CERTIFY write.
- GitHub: branch + commit + pushed SHA on each modified file.
- Atlas: cited file paths and section anchors (§4 above).
- Mission Control: `four_brain_run` row + transition rows OR explicit "deferred-pending-BAR-FOUR-BRAIN-CLI" note in audit packet.

---

## §9 P=1 DEFINITION (Scoped to this BAR)

P=1 only when **every** condition below is true:

1. `PLANNER-INTAKE-TEMPLATE.md` v2.0.0 deployed; thin shape (Q1..Q4 + conditional Q4A + 6 optional helpers) present; plain language only; G-15/G-16 header pins present.
2. `planner-intake-template.yaml` v2.0.0 deployed; BS Law Y-junction conformant; lock-step with markdown.
3. `PROCESS-UT.md` v1.1.0 deployed; 14-section + 13-item UT_CHECKLIST skeleton intact; §14 logbook row appended; Q-01..Q-04 references removed.
4. `four-brain.yaml` v1.1.0 deployed; lock-step with PROCESS-UT; BS Law Y-junction preserved.
5. `imo-creator-v2/atlas/constants/PLANNER_ROLE.md` exists and declares Planner read-set wiring.
6. `forebrain-garage.sh` refactored — G-19 auto-advance live; G-16 TTL hook live; G-17 concurrency check live.
7. `four-brain-doctrine-gate.yaml` — every gate has a deterministic predicate (G-18 lock).
8. `bar_locks` tracking surface present OR deferral to BAR-FOUR-BRAIN-CLI documented.
9. Codex VERDICT: P=1 on standard G01–G10 + BAR-G-A through BAR-G-P.
10. Skeleton invariants verified on every modified UT.
11. Sovereign reviews and signs the locked TEMPLATE version (not intermediate Plan/Audit Books).
12. ≥4 LBB transition rows (planner/foreman/mechanic/auditor).
13. CERTIFY row in `lbb.logbook` for this BAR.
14. `FINAL-PRODUCT.yaml` at `garage/outbox/BAR-PLANNER-INTAKE-REFINE/` listing all refined artifact paths + commit SHAs.

---

## §10 BRAINSTORMING CLAIMS PROMOTED TO FACTS (Sovereign-Accepted)

Per intake §"WHAT" — sovereign-locked at session 2026-05-06.

| ID | Fact | Source |
|---|---|---|
| F-01 | Template uses TYPE-asked-LAST + conditional follow-up question order. | LBB `090520d7…` §8; intake §"WHAT" |
| F-02 | TYPE taxonomy = {Build, Fix, Maintenance}; aviation analogy locks meanings. | Same |
| F-03 | Edge-case routing defaults: Refactor→Build, Research→Build, Delete→Fix. | Same |
| F-04 | Maintenance findings do NOT accumulate Strikes (per FOUR_BRAIN_AVIATION v1.1.0+). | FOUR_BRAIN_AVIATION.md v1.2.0 §Two-Mode Dispatch |
| F-05 | 6-optional-helper cap; sovereign sign-off to add new optionals. | Intake §"WHAT" |
| F-06 | Plain-language only on every human-facing field. | Intake §"WHAT" + CONSTRAINTS |
| F-07 | Quality bail-out rule: ONE targeted clarification on vacuous briefs. | Intake §"WHAT" |
| F-08 | G-15: pinned_atlas_version + pinned_gate_spec_version required in Plan-Body. | Intake §"WHAT" + LBB `090520d7…` §8 |
| F-09 | G-16: plan_book_ttl_hours required; Foreman re-validation hook on stale Plan Books. | Same |
| F-10 | G-17: file-level concurrency check at Foreman dispatch on overlapping write scope. | Same |
| F-11 | G-18: every gate has a deterministic predicate; LLM-tail gates flagged. | Same |
| F-12 | G-19: NO inter-stage sovereign gates; only template-drop and Auditor verdict are sovereign touchpoints; Mission Control surfaces transitions as observation only. | LBB `1f19c519…`; intake §"WHAT" |
| F-13 | Planner auto-wires read-set; pointers in PLANNER_ROLE.md, not in template. | Intake §"WHAT" + §"WHERE TO" #5 |
| F-14 | Q-01..Q-04 from prior plan are moot under v2 design (intake §"NOTE ON Q-01/02/03/04"). | Intake §"NOTE" |
| F-15 | imo-creator four-brain UT path update is dropped from this BAR; PLANNER_ROLE.md replaces it as the imo-creator-v2-side artifact. | Intake §"NOTE ON Q-03" |

---

## §11 BRAINSTORMING CLAIMS LEFT AS ASSUMPTIONS

| ID | Assumption | Reasoning |
|---|---|---|
| A-01 | `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml` is non-locked and editable by Mechanic. | Per intake §"OPTIONAL HELPERS / CONSTRAINTS" only the 17 constants under `atlas/constants/` are off-limits; `atlas/manifests/` should be editable, but Mechanic confirms via `git ls-files` against the locked-constants list before first edit. If sovereign flags as locked, Mechanic halts and routes to pending-atlas-updates queue. |
| A-02 | `bar_locks` can be file-based (yaml) for this BAR; D1 migration deferred to BAR-FOUR-BRAIN-CLI. | Aligns with §11 OUT OF SCOPE in PROCESS-UT.md (CLI runner deferred). Documented deferral acceptable per BAR-G-J. |
| A-03 | Mission Control connector evidence is conditional — "deferred-pending-BAR-FOUR-BRAIN-CLI" is acceptable on PASS if D1 migration not live. | Per `connector_run_binding.mission_control.required: conditional` in intake YAML. |
| A-04 | Default `plan_book_ttl_hours = 168` (7 days) is reasonable; sovereign overrides at template-drop. | Sovereign convention; subject to first real-use feedback. |
| A-05 | PLANNER_ROLE.md placement at `imo-creator-v2/atlas/constants/PLANNER_ROLE.md` is the right home (non-locked Planner-config artifact). | Intake §"WHERE TO" #5 specifies this path. Sovereign confirms at audit; if rejected, Mechanic halts and routes to a sovereign clarification ticket. |

---

## §12 STOP CONDITIONS

Mechanic STOPS and routes to Strike system / sovereign clarification if any of the following:

1. Any locked constant under `imo-creator-v2/atlas/constants/` (the 17) shows up in the dispatch packet write set → halt; route to pending-atlas-updates queue.
2. `git diff HEAD -- <17 locked-constant paths>` is non-empty after a Mechanic edit → halt; revert; Strike 1.
3. Skeleton restructuring detected in PROCESS-UT.md (section reorder, section removal, UT_CHECKLIST item removal, Y-junction violation) → halt; revert; Strike 1.
4. Paired `.md`/`.yaml` version drift after Mechanic edits → halt; re-sync; if persistent, Strike 1.
5. Sovereign rejects PLANNER_ROLE.md placement at audit → halt; route to sovereign clarification ticket; do NOT advance to CERTIFY.
6. Codex returns `VERDICT: P=0` on any standard or BAR-specific gate → Strike count++; Strike ladder applies (Strike 1: Sonnet repair + Codex re-audit; Strike 2: Opus 4.7 mechanic; Strike 3: Troubleshoot/Train).
7. `four-brain-doctrine-gate.yaml` is flagged locked by sovereign → halt WO-7; route to pending-atlas-updates queue; remaining WOs proceed if independent.
8. Plan Book TTL exceeded before Foreman dispatch → Foreman halts; Planner re-validates and re-signs (G-16 hook).
9. File-level write-scope conflict detected at Foreman dispatch (overlapping `allowed_write_scope` with another in-flight BAR) → block or queue (G-17).
10. LBB connector unavailable → Mechanic cannot write transition rows → halt; resolve credential (Doppler `LBB_API_KEY`) before resuming.

---

## §13 MECHANIC DISPATCH REQUIREMENTS (for Foreman)

Foreman MUST:

1. Verify Plan Book TTL not exceeded (G-16).
2. Verify no overlapping `allowed_write_scope` against `bar_locks` (G-17).
3. Verify paired-artifacts.yaml row 9 exists (Atlas registry).
4. Read Atlas pinned-versions from this Plan Book §1 / §4 / §6 — pass to Mechanic as env / context.
5. Emit dispatch packets as **literal `file:line | old_string | new_string` triples** (no "find pattern X" rules; per memory `feedback_work_packet_literal_pairs.md`).
6. Dispatch Sonnet with `run_in_background=true` (per memory `feedback_run_sonnet_in_background.md`).
7. Stamp HEIR `mechanic` model field = `sonnet` on transition row.
8. Auto-advance status `PLAN_BOOK_READY → FOREMAN_DISPATCHED → MECHANIC_RUNNING` (no sovereign gate; G-19).
9. On Mechanic exit code 0 → auto-advance to `AUDIT_RUNNING` and dispatch Codex.
10. Foreman produces NO Library artifact — routing only.
11. Foreman NEVER flips Auditor verdict (per FOUR_BRAIN_AVIATION.md v1.2.0 §"Foreman Lock").

---

## §14 LBB / MISSION CONTROL EVIDENCE REQUIREMENTS

### 14a LBB (required)

- READ: canonical record `090520d7-ff64-4b6e-9e14-5e8928b24db7`; G-19 record `1f19c519-f402-421f-bb5c-8eeaa7f7d9e9`.
- WRITE: 4 transition rows minimum — planner / foreman / mechanic / auditor — for this BAR.
- WRITE: 1 Audit Book row to `lbb.records` on Codex PASS (`subject_id='processes'`, `species='Audit-Body'`).
- WRITE: 1 CERTIFY row to `lbb.logbook` on BAR P=1.
- Credential: Doppler `LBB_API_KEY` (imo-creator → dev).

### 14b Mission Control (conditional)

- WRITE: `four_brain_run` row (run metadata, state, verdict).
- WRITE: `four_brain_transition` rows (one per role transition).
- WRITE: `squawks` rows on FAIL (process_id='four-brain', subject_id='processes').
- DEFERRAL: if D1 migration not live, audit packet documents "deferred-pending-BAR-FOUR-BRAIN-CLI" — acceptable per BAR-G-J + intake `connector_run_binding.mission_control.required: conditional`.

### 14c GitHub (required)

- Branch + commit per modified file; pushed SHA recorded in audit packet.

---

## §15 OPEN BLOCKERS

None blocking Planner→Foreman handoff. The following are flagged for Mechanic / sovereign attention but do not gate dispatch:

| ID | Flag | Owner | Action |
|---|---|---|---|
| B-01 | Confirm `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml` is non-locked. | Mechanic at WO-7 first-edit | If locked, halt WO-7; route to pending-atlas-updates queue; remaining WOs proceed. |
| B-02 | Sovereign confirms `PLANNER_ROLE.md` placement at `imo-creator-v2/atlas/constants/`. | Sovereign at audit | If rejected, Mechanic re-locates per sovereign instruction; Plan Book updates path; re-audit. |
| B-03 | Sovereign confirms `bar_locks` may be file-based for this BAR (vs. requiring D1 migration now). | Sovereign at audit | Documented deferral acceptable per A-02. |
| B-04 | Sovereign sets `plan_book_ttl_hours` default if 168 is wrong. | Sovereign at audit | Mechanic adjusts header pin if instructed. |

---

## §16 PROCESS-070 START / HANDOFF PATH

```
Sovereign drops PLANNER-INTAKE.md (REVISED) → garage/inbox/BAR-PLANNER-INTAKE-REFINE/
  ↓
Planner (Opus 4.7, ForeBrain) reads intake + Atlas Step 0 sources + LBB canonical + G-19 record
  ↓
Planner produces THIS Plan Book at docs/plans/BAR-PLANNER-INTAKE-REFINE/PLAN-BOOK.md
  ↓
Status auto-advances PLAN_BOOK_READY → FOREMAN_DISPATCHED (per G-19)
  ↓
Foreman reads Plan Book §7 + §13; emits literal dispatch packets to Sonnet (background)
  ↓
Status auto-advances → MECHANIC_RUNNING
  ↓
Sonnet executes WO-1..WO-8; writes LBB transition rows; commits to GitHub
  ↓
Status auto-advances → AUDIT_RUNNING (on Mechanic exit 0)
  ↓
Codex reads four-brain-doctrine-gate.yaml + Plan Book §8; runs G01-G10 + BAR-G-A..P
  ↓
PASS → Audit Book → lbb.records + CERTIFY → lbb.logbook + FINAL-PRODUCT.yaml → outbox/
  ↓
Sovereign reads Auditor verdict (output boundary touchpoint)
  ↓
BAR closes
```

On FAIL: Strike system runs per FOUR_BRAIN_AVIATION.md v1.2.0 §"STRIKE SYSTEM". Mission Control surfaces transitions as observation only (no approve/reject buttons between Planner and Auditor).

---

## §17 CONNECTORS USED / BLOCKED

| Connector | Status | Use |
|---|---|---|
| LBB | required, available | Read canonical/G-19 records; write 4 transitions + Audit Book + CERTIFY |
| GitHub | required, available | Read/write 5+ refined artifacts in repos Barton-Processes + imo-creator-v2 |
| Atlas | required, available | Local repo path `imo-creator-v2/atlas/`; cite §1.2.3, §6, §7.3a + constants + manifests |
| Mission Control | conditional | Write run + transition rows if D1 migration live; otherwise deferred per A-03 |
| Linear | optional | Link to ticket if one exists |
| R2 / D1 data cycle | not applicable | Doctrine refinement; no data-cycle |

No connectors currently blocked.

---

## §18 LBB RECORDS USED / REQUIRED

**Used (read by Planner):**

- `090520d7-ff64-4b6e-9e14-5e8928b24db7` — canonical conversation summary (G-01..G-18, drift vectors, P=1).
- `1f19c519-f402-421f-bb5c-8eeaa7f7d9e9` — G-19 doctrine lock.
- `54214381-4d34-4717-8284-6407c483d21a` — historical first ingest (reference only).

**Required (writes during pipeline):**

- planner_transition_row (this stage; Planner writes at exit).
- foreman_transition_row.
- mechanic_transition_row.
- auditor_transition_row.
- audit_book_row (`lbb.records`, on PASS).
- CERTIFY row (`lbb.logbook`, on BAR P=1).

---

## §19 NON-DRIFT INVARIANTS

Carried forward from intake `non_drift_invariants`:

- Planner OWNS the route — this Plan Book specifies the route; the intake specified destination.
- Mechanic ≠ Auditor (Sonnet builds, Codex audits).
- BS Law Y-junction conformance on every refined `.md`/`.yaml` pair.
- v1.0.0 baseline preserved as audit history; v2.0.0 is a breaking shape change but downstream parsers should be backward-compatible where possible.
- No locked constants modified (the 17 in `imo-creator-v2/atlas/constants/`).
- Sovereign decides each gap — Planner does NOT autonomously accept/reject. Per F-01..F-15, sovereign already locked at session 2026-05-06.
- LBB record `090520d7…` is canonical; file copy in inbox is convenience only.
- The Planner owns the plan; intake owns desired outcome and constraints.
- Foreman dispatches; Mechanic builds; Auditor certifies.
- Mechanic cannot audit its own work.
- BS Law applies to every durable structured artifact.
- Blueprint, execution, runtime, and evidence layers must not drift.

---

## §20 DOCUMENT CONTROL

| Field | Value |
|---|---|
| Plan Book Version | 2.0.0 |
| Authored | 2026-05-06 |
| Author | Planner (Opus 4.7, ForeBrain) |
| Status | PLAN_BOOK_SIGNED (auto-advance per G-19) |
| BAR | BAR-PLANNER-INTAKE-REFINE |
| Conformance | Plan-Body species (Book Law v1.5.0) · BS Law v1.5.0 · UT_CHECKLIST v1.3.1 (referenced for downstream UT edits) · FOUR_BRAIN_AVIATION.md v1.2.0 |
| Pinned Atlas Version | v2.2.6 |
| Pinned Gate Spec | `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml` (current) |
| Plan Book TTL | 168 hours (default; sovereign-overridable) |
| Supersedes | Plan Book v1 (same path) |
| Next Stage | FOREMAN_DISPATCHED (auto-advance) |

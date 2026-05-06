# PROCESS-UT — Four-Brain Aviation Model (PROC-070)

**UT-Body species per Book Law (`atlas/constants/BOOK_LAW.md` v1.5.0)**
**Y-junction conformant per BS Law (`atlas/constants/BS_LAW.md` v1.5.0)**
**UT v2.8.0 + UT_CHECKLIST v1.3.1 conformant**
**Companion YAML: `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml`**

---

## UT Pre-Flight Checklist (per `atlas/constants/UT_CHECKLIST.md` v1.3.1)

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §2 |
| 2 | OSAM — READ / WRITE / Process Composition / Join Chain / Forbidden / Query Routing | ☑ | §5 |
| 3 | Component Status — every dep 🟢 / 🟡 / 🔴 with 1-line state | ☑ | §3 |
| 4 | Owner — human who fixes this at 2 AM | ☑ | §1 |
| 5 | Live Dashboard — URL or explicit "N/A" | ☑ | §3 (Mission Control — URL TBD) |
| 6 | Kill Switch — exact command to stop the process | ☑ | §8 |
| 7 | Logbook — last audit verdict + date (after certification only) | ☐ | §12 (legitimately deferred until Codex PASS) |
| 8 | FCEs Attached — which FCE runs structurally back this doc | ☑ | §3 (none for pipeline process itself) |
| 9 | BARs Referenced — every BAR this doc touches, with status | ☑ | §3 |
| 10 | LBB Subjects Fed — which LBB subject(s) this doc's session logs go to | ☑ | §3 (`processes`) |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | ☑ | §1b |
| 12 | Live Verification — every numeric count, cron, URL, command, BAR status grounded | ☐ | §9b (deferred until first run + Codex PASS) |
| 13 | ctb_node — declared path on Barton Enterprises CTB trunk | ☑ | §1 |

---

## §1 IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-070 |
| Name | Four-Brain Aviation Model — Callable Library Process |
| Species | UT-Body (Book Law v1.5.0) |
| Version | 1.3.0 |
| Status | BUILD |
| Created | 2026-05-04 |
| Last Modified | 2026-05-06 |
| Authority | Dave Barton (sovereign) |
| Owner | Dave Barton (fixes at 2 AM) |
| ctb_node | `barton-enterprises/imo-creator/processes/four-brain` |
| BAR Reference | BAR-PROC-070 |
| Companion YAML | `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` |
| services | mission-control D1 (four_brain_run, four_brain_transition, squawks), LBB worker (lbb.records, lbb.logbook), scripts/lbb-log.sh, Sonnet (Agent tool, model=sonnet), Codex (codex-dop exec), Opus 4.7 (Agent tool, model=opus, escalation only) |
| acceptance_criteria | D-070-01: All 19 gates PASS (P=1 on each — G01-G12 + W-1..W-7). D-070-02: No-op BAR run produces exactly 4 LBB rows + 1 Audit Book on PASS. D-070-03: Atlas registry row 9 present in both paired-artifacts.yaml AND atlas/ATLAS.md §7.3a. D-070-04: No locked constants modified except atlas/ATLAS.md (verified by git diff HEAD). D-070-05: BS Law Y-junction conformant on the YAML companion. D-070-06: Mechanic != Auditor confirmed at every transition. |
| Governing Constant | `atlas/constants/FOUR_BRAIN_AVIATION.md` v1.3.0 |
| Aviation Roles | Planner: Opus 4.7 · Foreman: Opus 4.7 · Mechanic: Sonnet · Auditor: Codex |
| Aviation Rule | Mechanic ≠ Auditor (different inference engines — Aviation Model invariant) |
| ORBT | BUILD (no completed BAR run yet; STATUS → OPERATE after 3-run minimum + Codex CERTIFY + sovereign sign-off) |
| Library ORBT State | BUILD |

---

## §1b GEOMETRY

| Field | Value |
|-------|-------|
| CTB Position | Branch — `barton-enterprises/imo-creator/processes/four-brain` |
| Hub-Spoke Role | HUB (this Process IS the orchestration engine for every BAR run) |
| Altitude | 10k operational |
| Sovereign | Dave Barton (trunk — `barton-enterprises`) |
| Parent Branch | `barton-enterprises/imo-creator/processes` |

```
CTB VIEW (50k → 5k)
─────────────────────────────────────────────
Trunk: barton-enterprises
  └─ Branch: imo-creator
       └─ Branch: processes
            └─ Leaf: four-brain (PROC-070) ← YOU ARE HERE

TRACE-BACK (this doc is derived from, does not modify)
─────────────────────────────────────────────
atlas/constants/FOUR_BRAIN_AVIATION.md v1.3.0 (16th locked constant)
  ↓ cites
atlas/manifests/four-brain-doctrine-gate.yaml (gate spec)
  ↓ implements
PROC-070 (this process pair)
  ↓ invoked by
Every BAR dispatched via the Four-Brain pipeline

HUB-SPOKE WIRING
─────────────────────────────────────────────
[Sovereign Plan Book] ──► [PROC-070 HUB] ──► [Sonnet Mechanic]
                                  │           ──► [Codex Auditor]
                                  │           ──► [LBB Worker]
                                  │           ──► [mission-control D1]
                             [Foreman routes — no Library artifact produced]
```

---

## §2 PRD

**WHAT.** A Library-shelved, callable Process pair that encodes the Four-Brain Aviation Model (Planner → Foreman → Mechanic → Auditor) as a repeatable pipeline. Every BAR in every domain runs through this Process; the pipeline is the spine.

**WHY.** Prior to PROC-070, the Four-Brain pipeline was ad-hoc per-BAR ritual — no canonical YAML runtime contract, no D1 telemetry, no standardized LBB logging, no paired Library artifact. PROC-070 converts the pipeline from doctrine into an operable, auditable, Library-indexed Process with defined inputs, outputs, telemetry, and gates.

**WHO.** Foreman (operator — dispatches mechanics). Mechanic (Sonnet — executes build). Auditor (Codex — issues PASS/FAIL). Sovereign Dave Barton (signs Plan Books and final close).

**SCOPE.** Pipeline contract (nodes, gates, strike ladder). D1 telemetry schema (`four_brain_run` + `four_brain_transition`). LBB logging per role transition. Audit gates G01-G12 + Mission Control wiring gates W-1..W-7 (19 total). Atlas registry row 9.

**OUT OF SCOPE.** CLI runner (BAR-FOUR-BRAIN-CLI). Tune-up workflow YAMLs (future BARs). Non-imo-creator domain adaptations.

**SUCCESS METRIC.** A no-op Four-Brain BAR run produces exactly 4 LBB transition rows + 1 Audit Book row on Codex PASS. All 19 audit gates (G01-G12 + W-1..W-7) return P=1.

---

## §3 RESOURCES / COMPONENT STATUS / DEPENDENCIES

### Component Status

| Component | Status | State |
|-----------|--------|-------|
| `FOUR_BRAIN_AVIATION.md` v1.3.0 | 🟢 | Locked (16th constant). Source of pipeline doctrine. |
| `four-brain-doctrine-gate.yaml` | 🟢 | GATED. Gate spec + LBB row schema source of truth. |
| `atlas/manifests/paired-artifacts.yaml` row 9 | 🟢 | Appended in this BAR. |
| `atlas/ATLAS.md` §7.3a row 9 | 🟢 | Appended in this BAR (v2.2.6). |
| `mission-control` D1 binding | 🟡 | `D1_MISSION_CONTROL` exists; new tables `four_brain_run` + `four_brain_transition` require migration (BAR-FOUR-BRAIN-CLI). |
| LBB Worker | 🟢 | `https://lbb.svg-outreach.workers.dev` live. Auth via `LBB_API_KEY` (Doppler). |
| `scripts/lbb-log.sh` | 🟡 | Referenced; existence confirmed if present in repo. Mechanic verifies at dispatch time. |
| Sonnet (Agent tool) | 🟢 | Default mechanic model. `run_in_background=true`. |
| Codex (`codex-dop exec`) | 🟢 | Default auditor. Different inference engine than Sonnet. |
| Opus 4.7 | 🟢 | Reserved for Strike-2 escalation only. |

### BARs Referenced

| BAR | Status | Notes |
|-----|--------|-------|
| BAR-PROC-070 | OPEN (this BAR) | Creates this process pair |
| BAR-FOUR-BRAIN-CLI | FUTURE | CLI runner + D1 migration (not this BAR) |
| BAR-LOCK-01 | FUTURE | Hash manifest refresh after Atlas amendments |

### LBB Subjects Fed

| Subject | Usage |
|---------|-------|
| `processes` | All LBB rows written by four-brain pipeline runs land here |

### FCEs Attached

None for the pipeline orchestration process itself. FCEs run inside individual BARs when the mechanic's Plan Book specifies a Dyno run.

### Live Dashboard

Mission Control — URL TBD (BAR-FOUR-BRAIN-CLI creates dashboard routes). N/A until CLI runner exists.

---

## §3f VOCABULARY

| Term | Definition | Source |
|------|-----------|--------|
| BAR | Barton Action Request — a work order dispatched through the Four-Brain pipeline | `atlas/constants/KEY.md` |
| Plan Book | Plan-Body species artifact authored by Planner; sovereign-signed before dispatch | `FOUR_BRAIN_AVIATION.md` v1.3.0 |
| UT Book | UT-Body species artifact built by Mechanic (this file is a UT Book) | Book Law v1.5.0 |
| Audit Book | Audit-Body species artifact produced by Auditor on PASS verdict | `FOUR_BRAIN_AVIATION.md` v1.3.0 |
| Strike | Auditor FAIL verdict that does NOT close the BAR; triggers repair → re-audit | `FOUR_BRAIN_AVIATION.md` v1.3.0 §STRIKE SYSTEM |
| Tune-up | Scheduled Four-Brain invocation (A/B/C/D-check + AD cadences); NOT a BAR per se | `FOUR_BRAIN_AVIATION.md` v1.3.0 §Two-Mode Dispatch |
| Pressure Gauge | 4-signal composite health indicator (cron firing / LBB log presence / D1 anchor freshness / active errors) | `FOUR_BRAIN_AVIATION.md` v1.3.0 §Pressure Gauge |
| HEIR | 8-field canonical identity stamp for every Library artifact | `atlas/constants/KEY.md` §HEIR |
| ORBT | Operate / Repair / Build / Troubleshoot_Train — 4-state lifecycle | `atlas/constants/KEY.md` §ORBT |
| Y-junction | BS Law conformance point where Book structure + Spine content merge | `atlas/constants/BS_LAW.md` v1.5.0 |
| Determinism-first | Architectural gate: LLM is tail arbitration only, never the spine | `FOUR_BRAIN_AVIATION.md` v1.3.0 + CLAUDE.md |

Inherits parent vocabulary from `atlas/constants/KEY.md` (10th locked constant).

---

## §4 MIDDLE — OPERATOR SEQUENCE

Seven-step canonical runbook. Each step cites Atlas source.

### Step 1 — Sovereign Authors Plan Book

Sovereign (Dave Barton) authors a signed Plan Book at `docs/plans/BAR-{id}.plan.md` (Plan-Body species). Plan Book must pass BS Law Y-junction before Foreman can dispatch. Plan Book contains: HEIR identity, design decisions (each Atlas-cited), D1 schema, gate spec, and open questions resolved before signing.

*Atlas source: `FOUR_BRAIN_AVIATION.md` v1.3.0 §"THREE BOOKS PER BAR" + §X (Atlas pre-flight step 0 for Planner).*

### Step 2 — Sovereign Signs Plan Book

Sovereign reviews Plan Book acceptance criteria and signs. Signing = pre-authorizing the Mechanic override for locked constants (only `atlas/ATLAS.md` is eligible). No BAR may proceed past Foreman without sovereign signature.

*Atlas source: `FOUR_BRAIN_AVIATION.md` v1.3.0 §"Planner Lock" + Plan §8 sovereign-lock considerations.*

### Step 3 — Foreman Dispatches

Foreman reads `atlas/ATLAS.md` §6 (governance) + `atlas/manifests/paired-artifacts.yaml` (inventory). Foreman emits Mechanic dispatch packets as **literal `file:line | old_string | new_string` triples** (no "find pattern X" rules). Foreman dispatches Sonnet with `run_in_background=true`. Foreman produces **no Library artifact** — routing only.

*Atlas source: `FOUR_BRAIN_AVIATION.md` v1.3.0 §"Foreman Lock" + memory `feedback_work_packet_literal_pairs.md` + `feedback_run_sonnet_in_background.md`.*

### Step 4 — Mechanic Builds + LBB-Logs

Mechanic (Sonnet) executes the dispatch packet. Before first edit: reads Atlas §4.5 (repair) or §4 (build), the Plan Book, and spoke frontmatter. After final edit: writes one LBB row via `scripts/lbb-log.sh --role mechanic --action edit --bar-id BAR-{id}`. Verifies `git diff HEAD -- <16 read-only constant paths>` returns empty before commit.

*Atlas source: `FOUR_BRAIN_AVIATION.md` v1.3.0 §X (step 0) + §Y (step N).*

### Step 5 — Codex Audits

Auditor (Codex, different inference engine than Sonnet) loads `atlas/manifests/four-brain-doctrine-gate.yaml` as gate spec source of truth + BAR-specific gates from the Plan Book §7. Walks all 19 gates (G01-G12 + W-1..W-7). Auditor self-verdict is PASS or FAIL — Foreman NEVER flips. On PASS, Codex writes one LBB row + Audit Book. On FAIL, Codex writes squawk; Strike count increments.

*Atlas source: `FOUR_BRAIN_AVIATION.md` v1.3.0 §"Auditor Lock" + Aviation Model "mechanic ≠ inspector" + memory `feedback_codex_certifies_not_operator.md`.*

### Step 6 — Strike Ladder (if FAIL)

- **Strike 1:** Sonnet repair + Codex re-audit. Foreman re-dispatches.
- **Strike 2:** Escalate to Opus 4.7 mechanic. Codex re-audits.
- **Strike 3:** Troubleshoot/Train — structural investigation, not another repair. Airworthiness Directive if fleet-wide.

*Atlas source: `FOUR_BRAIN_AVIATION.md` v1.3.0 §"STRIKE SYSTEM".*

### Step 7 — BAR Closes on PASS

Codex signs CERTIFY verdict. Audit Book shelved to LBB (`subject_id='processes'`, `species='Audit-Body'`). CERTIFY row written to `lbb.logbook`. `four_brain_run.verdict='PASS'`. BAR closes. Foreman notifies sovereign.

*Atlas source: `FOUR_BRAIN_AVIATION.md` v1.3.0 §"THREE BOOKS PER BAR" + four-brain-doctrine-gate.yaml G08.*

---

## §5 OSAM

### READ

| Source | What |
|--------|------|
| `atlas/constants/FOUR_BRAIN_AVIATION.md` v1.3.0 | Pipeline doctrine (locked). Planner reads §X; Mechanic reads §4/§4.5; Auditor reads gate spec. |
| `atlas/manifests/four-brain-doctrine-gate.yaml` | Gate spec + LBB row schema source of truth. Auditor's primary read. |
| `atlas/manifests/paired-artifacts.yaml` | Registry — Foreman verifies row 9 exists before dispatching. |
| `docs/plans/BAR-*.plan.md` | Sovereign-signed Plan Book for the active BAR. |
| `scripts/lbb-log.sh` | Shell script used by all roles for LBB step-N writes. |

### WRITE

| Target | What | Who writes |
|--------|------|------------|
| `mission-control.four_brain_run` | One row per BAR run (run metadata, state, verdict) | CLI runner (future) |
| `mission-control.four_brain_transition` | One row per role transition | CLI runner (future) |
| `mission-control.squawks` | Errors keyed `process_id='four-brain'` + `subject_id='processes'` | Auditor on FAIL |
| `lbb.records` | 4 transition rows per BAR (planner/foreman/mechanic/auditor) via lbb-log.sh | Each role at Step N |
| `lbb.records` | Terminal Audit Book row on Codex PASS | Auditor |
| `lbb.logbook` | CERTIFY row on BAR P=1 | Auditor |

### PROCESS COMPOSITION

```
Planner (Plan Book) → Foreman (dispatch) → Mechanic (build + LBB-log)
    → Auditor (audit + LBB-log) → [PASS → Audit Book → LBB] | [FAIL → squawk → Strike ladder]
```

### JOIN CHAIN

```
Sovereign Plan Book (docs/plans/BAR-X.plan.md)
  → Foreman dispatch (literal pairs)
  → Sonnet builds + lbb-log.sh writes 1 row per role transition
  → Codex audit run (gate spec: four-brain-doctrine-gate.yaml)
  → 19 gates evaluated (G01-G12 + W-1..W-7)
  → PASS: Audit Book → lbb.records + lbb.logbook CERTIFY + four_brain_run.verdict='PASS'
  → FAIL: squawks row + Strike count++; Strike ladder applies
```

### FORBIDDEN

| Action | Why forbidden |
|--------|--------------|
| LLM on the spine of any gate evaluation | `determinism_gate: ai_on_spine_forbidden` — `FOUR_BRAIN_AVIATION.md` v1.3.0 |
| Mechanic self-audits | Aviation Model violation — mechanic ≠ inspector |
| Foreman flips Auditor verdicts | `FOUR_BRAIN_AVIATION.md` v1.3.0 §"Foreman Lock" |
| Skip Atlas step 0 read for any role | `FOUR_BRAIN_AVIATION.md` v1.3.0 §X |
| Skip LBB step N write before any transition | `FOUR_BRAIN_AVIATION.md` v1.3.0 §Y |
| Modify 16 of 17 locked constants | CLAUDE.md §"Seventeen Constants" + G09 |

### QUERY ROUTING

| Question | Where to query |
|----------|----------------|
| How many BAR runs completed? | `SELECT COUNT(*) FROM four_brain_run WHERE verdict='PASS'` |
| What's the current strike count? | `SELECT strikes FROM four_brain_run WHERE run_id=?` |
| Which LBB rows belong to a BAR? | `SELECT * FROM lbb_records WHERE bar_id=? AND subject_id='processes'` |
| What gate verdicts did the last run produce? | `SELECT gate_verdicts FROM four_brain_transition WHERE run_id=? AND role='auditor'` |
| What Atlas sections did the mechanic consult? | `SELECT atlas_sections_consulted FROM four_brain_transition WHERE run_id=? AND role='mechanic'` |
| Are there unresolved squawks? | `SELECT * FROM squawks WHERE process_id='four-brain' AND resolved_at IS NULL` |

---

## §6 INPUTS

| Input | Format | Source |
|-------|--------|--------|
| Sovereign-signed Plan Book | `docs/plans/BAR-{id}.plan.md` (Plan-Body species, BS Law Y-junction conformant) | Planner authors; sovereign signs |
| Foreman context | Env variables (HUMAN_LOCKED_AMEND_AUTH if Atlas touched), repo state, branch | Foreman loads from current env |
| Atlas version pin | `atlas/ATLAS.md` version string read at Foreman step 0 | Foreman cites in dispatch packet |

---

## §7 OUTPUTS

| Output | Species | Destination |
|--------|---------|-------------|
| UT Book(s) at HEIR-B | UT-Body | Mechanic creates at prescribed paths |
| Audit Book at HEIR-C | Audit-Body | Auditor writes on PASS; shelved to LBB |
| D1 telemetry rows | Structured rows | `mission-control.four_brain_run` + `four_brain_transition` |
| LBB transition records | `lbb.records` rows | 4 rows per BAR (one per role) via lbb-log.sh |
| LBB Audit Book record | `lbb.records` row | Auditor on PASS; `subject_id='processes'`, `species='Audit-Body'` |
| CERTIFY row | `lbb.logbook` row | Auditor on BAR P=1 |
| Squawk(s) | `mission-control.squawks` row | Auditor on FAIL |

---

## §8 KILL SWITCH

| Level | Command / Action |
|-------|-----------------|
| Abort a BAR mid-flight | `git revert HEAD` on the BAR commit; abort via Foreman halt (no further dispatch packets) |
| Disable this process for a run | `D1: UPDATE four_brain_run SET runtime_state='DISABLED' WHERE run_id=?` (manual — CLI runner does not exist yet) |
| Emergency — revert all mechanic edits | `git diff HEAD~1 HEAD -- <mechanic-touched files>` then `git revert HEAD` |
| Strike 3 stop | Declare Troubleshoot/Train; do NOT dispatch a 4th repair without structural diagnosis |

---

## §9 OBSERVABILITY

### D1 Query Patterns

```sql
-- Active runs
SELECT run_id, bar_id, runtime_state, strikes FROM four_brain_run
WHERE verdict IS NULL ORDER BY started_at DESC;

-- Gate verdicts for a specific run
SELECT gate_verdicts FROM four_brain_transition
WHERE run_id = ? AND role = 'auditor';

-- Transition history for a run
SELECT role, action, atlas_sections_consulted, timestamp
FROM four_brain_transition WHERE run_id = ? ORDER BY timestamp;

-- Unresolved squawks
SELECT * FROM squawks WHERE process_id = 'four-brain' AND resolved_at IS NULL;
```

### LBB Query Patterns

```bash
# All LBB rows for a BAR
curl -s -X POST "https://lbb.svg-outreach.workers.dev/query" \
  -H "Authorization: Bearer $LBB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"BAR-{id}","subject_id":"processes"}'

# Count rows per BAR (gate G08 predicate: must be exactly 4)
SELECT COUNT(*) FROM lbb_records WHERE bar_id='BAR-{id}' AND subject_id='processes';
```

### Pressure Gauge (4 Signals → GREEN / YELLOW / RED)

| Signal | Source | GREEN | YELLOW | RED |
|--------|--------|-------|--------|-----|
| 1. cron_firing | cron_registry.yaml | N/A (event-driven) | — | — |
| 2. lbb_log_presence | `lbb_records WHERE bar_id=? AND subject_id='processes'` | COUNT == 4 | COUNT < 4 | COUNT == 0 |
| 3. d1_anchor_freshness | `four_brain_run.last_completed_at` | Fresh per active BAR | Stale | NULL after expected completion |
| 4. active_errors | `squawks WHERE process_id='four-brain' AND resolved_at IS NULL` | COUNT == 0 | COUNT > 0 | Any unresolved Strike-3 |

**Composition rule:** ALL 4 GREEN → OPERATE gauge. Any 1 YELLOW → drift watch. Signal 4 RED → auto-RED.
*Per `FOUR_BRAIN_AVIATION.md` v1.3.0 §"Pressure Gauge — the Operational Read".*

---

## §9b LIVE VERIFICATION

Deferred until first completed BAR run + Codex CERTIFY. At that time, append:
- Actual `four_brain_run` row count
- LBB row count (must be 4)
- Gate verdict table (G01-G10 all PASS)
- D1 `last_completed_at` value

---

## §10 SUCCESS METRICS

### §10a Targets

| Target | Metric |
|--------|--------|
| P=1 on all 19 gates | G01-G12 + W-1..W-7 all PASS on Codex audit |
| LBB row count per BAR | Exactly 4 rows (planner / foreman / mechanic / auditor) + 1 Audit Book on PASS |
| Atlas registry | Row 9 in both `paired-artifacts.yaml` AND `atlas/ATLAS.md` §7.3a |
| Locked constant purity | `git diff HEAD -- <16 constant paths>` returns empty |

### §10b Tolerances

All gates: `exact_match` (binary P=1 / P=0 per gate). No partial credit. No provisional pass.

Gate G06 (K=C parity): `parsed_value_match` — Codex compares parsed values, not byte identity (lesson BAR-397).

### §10c Derivation

Each gate maps to an Atlas-cited predicate per the Plan Book §7. Gate failure impact is BLOCK for all 19 gates.

---

## §11 OUT OF SCOPE

- CLI runner for this process (`bp.070-four-brain.run`) — BAR-FOUR-BRAIN-CLI
- Tune-up workflow YAMLs (A/B/C/D-check + AD cadences) — future BARs after Codex PASS on base process pair
- Adapting this process for non-imo-creator domains
- D1 migration (`migrations/0019_four_brain_run.sql`) — BAR-FOUR-BRAIN-CLI

---

## §12 LOGBOOK / BIRTH CERTIFICATE

☐ **Not certified.** No CERTIFY verdict from Codex yet. Logbook row will be appended here on Codex PASS.

*Per Book Law v1.5.0 §"Back Matter" — logbook section is append-only after certification. No pre-certification entries.*

---

## §13 DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Version | 1.3.0 |
| Last Modified | 2026-05-06 |
| Status | BUILD |
| Authority | Dave Barton (sovereign) |
| Created | 2026-05-04 |
| BAR | BAR-PROC-070 |
| Signed By | ☐ (sovereign signs at BAR close after Codex CERTIFY) |
| Conformance | UT v2.8.0 · UT_CHECKLIST v1.3.1 · Book Law v1.5.0 · BS Law v1.5.0 |

---

## §14 MAINTENANCE LOGBOOK

| Date | Version | BAR | Actor | Action |
|------|---------|-----|-------|--------|
| 2026-05-04 | 1.0.0 | BAR-PROC-070 | Sonnet Mechanic | CREATE — Initial UT-Body build. 14 sections, 13-item checklist. Companion YAML: `four-brain.yaml`. Paired artifact row 9 registered in `atlas/manifests/paired-artifacts.yaml` + `atlas/ATLAS.md` §7.3a (v2.2.6). |
| 2026-05-06 | 1.3.0 | REPAIR-AUDIT | Sonnet Mechanic | REPAIR — Runtime audit findings F-012/F-013/F-014 applied. All `FOUR_BRAIN_AVIATION.md v1.2.0` refs bumped to v1.3.0. Gate count updated from 10 (G01-G10) to 19 (G01-G12 + W-1..W-7) in all §2/§5/§9b/§10a sections. Mojibake encoding normalization. acceptance_criteria D-070-01 updated to 19 gates. |

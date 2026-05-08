# PROCESS-UT — Run Dyno (End-to-End FCE Operator Runbook)
**UT-Body species per Book Law (atlas/constants/BOOK_LAW.md v1.5.0)**
**Y-junction conformant per BS Law (atlas/constants/BS_LAW.md v1.5.0)**
**UT v2.8.0 + UT_CHECKLIST v1.3.1 conformant**
**Companion YAML: Barton-Processes/factory/imo-creator/060-run-dyno/run-dyno.yaml**

---

## UT Pre-Flight Checklist (per `atlas/constants/UT_CHECKLIST.md` v1.3.1)

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §2 |
| 2 | OSAM — READ / WRITE / Process Composition / Join Chain / Forbidden / Query Routing | ☑ | §5 |
| 3 | Component Status — every dep 🟢 / 🟡 / 🔴 with 1-line state | ☑ | §3 |
| 4 | Owner — human who fixes this at 2 AM | ☑ | §1 |
| 5 | Live Dashboard — URL or explicit "N/A" | ☑ | §3 (N/A until MC wiring BAR TBD) |
| 6 | Kill Switch — exact command to stop the process | ☑ | §8 |
| 7 | Logbook — last audit verdict + date (after certification only) | ☐ | §12 (legitimately deferred — Codex PASS not yet issued) |
| 8 | FCEs Attached — which FCE runs structurally back this doc | ☑ | §3 (none — this IS the FCE runner process) |
| 9 | BARs Referenced — every BAR this doc touches, with status | ☑ | §3 |
| 10 | LBB Subjects Fed — which LBB subject(s) this doc's session logs go to | ☑ | §3 (`processes`) |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | ☑ | §1b |
| 12 | Live Verification — every numeric count, cron, URL, command, BAR status grounded | ☐ | §9b (legitimately deferred — first FCE run not yet complete) |
| 13 | ctb_node — declared path on Barton Enterprises CTB trunk | ☑ | §1 |

---

## §1 IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-060 |
| Name | Run Dyno — FCE End-to-End Operator Runbook |
| Species | UT-Body (Book Law v1.5.0) |
| Version | 1.1.1 |
| Status | BUILD |
| Created | 2026-05-05 |
| Last Modified | 2026-05-08 |
| Authority | Dave Barton (sovereign) |
| Owner | Dave Barton (fixes at 2 AM) |
| ctb_node | `barton-enterprises/imo-creator/processes/060-run-dyno` |
| BAR Reference | BAR-FCE-RUN-060-PLANNER |
| Companion YAML | `Barton-Processes/factory/imo-creator/060-run-dyno/run-dyno.yaml` |
| services | fce-run, r2-workbench, openrouter-model-loop, d1-vault, lbb-memory, fce-library |
| acceptance_criteria | PROC-060 P=1: Both artifacts (PROCESS-UT.md v1.1.0 + run-dyno.yaml v1.1.0) pass Codex G01-G16 audit. All 16 FCE steps PLN-00 + FCE-00...FCE-14 present and identical in both. All 21 invariants encoded. us.py + up.py untouched. D1 vault-only confirmed. R2 workbench-only confirmed. |
| Locked Constants Used | FCE.md (#3), us.py (#7), up.py (#8), UT_CHECKLIST.md (#11), FOUR_BRAIN_AVIATION.md (#16), BS_LAW.md (#17) |
| ORBT | BUILD |

---

## §1b GEOMETRY

| Field | Value |
|-------|-------|
| CTB Position | Leaf — `barton-enterprises/imo-creator/processes/060-run-dyno` |
| Hub-Spoke Role | HUB (this process orchestrates the FCE run loop; OpenRouter models are spokes) |
| Altitude | 5k–10k operational |
| Sovereign | Dave Barton (trunk — `barton-enterprises`) |
| Parent Branch | `barton-enterprises/imo-creator` |
| Sibling Processes | PROC-080 FCE-Fill (reference fill logic — absorbed, not a second runtime), PROC-090 FCE-Computer-Programming (artifact/library evidence only) |
| IMO Role | Middle — consumes domain + P=1 (I), runs US+UP loop (M), produces locked M + evidence artifacts (O) |

```
CTB VIEW (50k → 5k)
─────────────────────────────────────────────
Trunk: barton-enterprises
  └─ Branch: imo-creator
       └─ Branch: processes
            └─ Leaf: 060-run-dyno (PROC-060) ← YOU ARE HERE

HUB-SPOKE WIRING
─────────────────────────────────────────────
[Operator declares domain + P=1]
        │
        ▼
[PROC-060 HUB: run_fce.py orchestrator]
        │
        ├──► [us.py — discover M] (read-only spoke)
        │         └──► [OpenRouter model 1] (expensive tier, parallel spoke)
        │         └──► [OpenRouter model 2] (expensive tier, parallel spoke)
        │         └──► [OpenRouter model 3] (expensive tier, parallel spoke)
        │
        ├──► [K=C lock — engine-final-locked.json]
        │
        ├──► [up.py — consume I via locked M] (read-only spoke)
        │         └──► [OpenRouter model 1] (expensive tier, parallel spoke)
        │         └──► [OpenRouter model 2] (expensive tier, parallel spoke)
        │         └──► [OpenRouter model 3] (expensive tier, parallel spoke)
        │
        ├──► [R2 workbench — artifacts] (FCE-02 through FCE-12 only)
        │
        ├──► [Codex Auditor — PASS / FAIL verdict] (different engine; Aviation Model)
        │
        └──► [D1 vault — dyno_run + dyno_run_cycle] (FCE-13 ONLY, after Codex PASS)
```

---

## §2 PRD

### What

PROC-060 is the canonical mechanical runner for any FCE domain. It takes a domain string and a P=1 definition, runs the US discovery loop until all four FCE columns (Valuation → Concentration → Trend → Liquidity) reach primitive leaf, locks K=C-certified constants into M, runs the UP solve loop until UP tolerance is satisfied, synthesizes FCE output, stores artifacts in R2, vaults the completed run to D1, and logs to LBB. One process covers any domain in any family.

### Why

Without a canonical run process, every FCE operator invents their own loop. The constants drift. The evidence chain breaks. D1 becomes a junk drawer. With PROC-060, the loop is the constant — the domain is the only variable.

### Who

- **Operator:** Dave Barton (fires the CLI, declares domain + P=1, sets UP tolerance, reviews Codex output)
- **Mechanic (build-time):** Sonnet (builds this doc + companion YAML; does not self-audit)
- **Auditor (certification):** Codex (different inference engine — cannot be same model as Mechanic; Aviation Model invariant)
- **Spokes (runtime):** Three OpenRouter models (expensive tier only) — independent parallel candidates per cycle

### Scope

- Single domain FCE run: US discover → K=C lock → UP solve → FCE output synthesis → R2 push → D1 vault → LBB log
- Every step from FCE-00 (pre-flight) through FCE-14 (certify + library register)
- R2 as live workbench during run (FCE-02 through FCE-12)
- D1 as completed-run vault (FCE-13 only, after Codex PASS)
- Covers all four FCE columns in locked order: Valuation → Concentration → Trend → Liquidity

### Out of Scope

- DMJ (Define·Map·Join) across multiple FCE runs — deferred at N=1; queued at N≥2 same family (separate process number, confirmed in Plan Book §15 Q-01)
- Mission Control wiring — deferred to follow-on BAR (Plan Book §15 Q-03)
- Domain-specific content authoring — PROC-080 FCE-Fill (absorbed reference only; not a second runtime)
- Family-level aggregation or cross-FCE comparison

### Success Metric

P=1 when:
1. US P=1 achieved: all four FCE columns (Valuation → Concentration → Trend → Liquidity) have primitive leaves; Three Primitives satisfied at leaf level
2. K=C lock written to `engine-final-locked.json` in R2 (2/3 majority minimum)
3. UP P=1 achieved: UP tolerance satisfied per operator declaration; three reference programs fully decomposed to recipe steps, zero remainder, zero external concepts
4. All run artifacts in R2 under `r2://svg-files/dyno-runs/{sovereign_id}/`
5. D1 `dyno_run` row inserted with `status = 'completed'` and `verdict` set (FCE-13, after Codex PASS)
6. D1 `dyno_run_cycle` rows: one per model per cycle from all three OpenRouter model tests, stored under sovereign ID
7. LBB CERTIFY row written under subject `processes`
8. Codex PASS verdict issued

---

## §3 RESOURCES

### Component Status

| Component | Type | Status | State |
|-----------|------|--------|-------|
| `atlas/dyno/us.py` | engine | 🟢 | Locked constant #7 — Universal Structure discovery; **sealed, zero bytes written** |
| `atlas/dyno/up.py` | engine | 🟢 | Locked constant #8 — Universal Process; **sealed, zero bytes written** |
| `atlas/dyno/dyno_engine.py` | runner | 🟢 | Mechanical runner — calls us.py + up.py; gated, not locked |
| `atlas/dyno/run_fce.py` | orchestrator | 🟢 | Full-pipeline orchestrator (FCE-00 → FCE-14); gated |
| OpenRouter API | external service | 🟢 | Three expensive-tier models per cycle; OPENROUTER_API_KEY via Doppler |
| Cloudflare R2 (`svg-files`) | storage | 🟢 | **Live workbench ONLY** during run (FCE-02 through FCE-12); bucket `svg-files`, binding `R2_SVG_FILES`, path `r2://svg-files/dyno-runs/{sovereign_id}/` |
| D1 (`mission-control`) | database | 🟢 | **Completed-run vault ONLY**; name `mission-control`, id `9f01c45a-a7f8-4173-83ac-afa666e86609`, binding `MC_DB`; tables `dyno_run` (20 cols) + `dyno_run_cycle`; migrations `0018_dyno_run.sql` + `0024_fce_imo_bundle.sql` |
| LBB API | logging | 🟢 | Role-transition + CERTIFY rows; subject `processes` |
| Doppler (`imo-creator/dev`) | secrets | 🟢 | OPENROUTER_API_KEY, CLOUDFLARE_API_TOKEN, LBB_API_KEY |
| Mission Control UI | dashboard | 🟢 | `workers/mission-control/src/pages/RunDyno.tsx` — queue view + intake form (BUILD) |
| Mission Control API | api | 🟢 | `workers/mission-control-api/src/routes/proc060.ts` — 6 routes (BUILD) |

### BARs Referenced

| BAR ID | Subject | Status |
|--------|---------|--------|
| BAR-FCE-RUN-060-PLANNER | This process — Plan Book | PLAN_BOOK_SIGNED |
| BAR-345 | D1 dyno_run schema base (migration 0018) | CLOSED |
| BAR-393 | Fire-and-forget wrapper (dyno-run-fce.yaml) | CLOSED |

### LBB Subjects Fed

| Subject | When | Role |
|---------|------|------|
| `processes` | Every role transition (planner → foreman → mechanic → auditor) | All roles |
| `processes` | At FCE-14 CERTIFY on Codex PASS | Auditor |

### FCEs Attached

None — PROC-060 IS the FCE runner. FCE runs produced by this process are stored in D1 and catalogued in `atlas/manifests/fce-registry.yaml`.

### Live Dashboard

Mission Control surfaces PROC-060 runs via `workers/mission-control/src/pages/RunDyno.tsx` (queue view + intake form). API routes in `workers/mission-control-api/src/routes/proc060.ts`.

Surfaces:
- Sovereign ID per run
- R2 workbench status panel (working folder, cycle artifact list)
- `dyno_run_cycle` rows per model per cycle (three-model visibility)
- Audit/vault/library state badges: R2 → audit → D1 → library
- DMJ readiness flag per family (N count)

---

## §3a CONCRETE WIRING

### D1 Database

| Field | Value |
|-------|-------|
| database_name | `mission-control` |
| database_id | `9f01c45a-a7f8-4173-83ac-afa666e86609` |
| binding | `MC_DB` |
| wrangler.toml | `workers/mission-control-api/wrangler.toml` |

#### Table: `dyno_run` — 20 columns total

16 original columns (migration `0018_dyno_run.sql`):
`run_id`, `domain`, `p1_definition`, `intent_mode`, `phases`, `status`, `verdict`,
`r_x`, `ut_doc`, `diagnostic`, `cycle_count`, `models_used`, `cost_usd`,
`r2_artifact_path`, `health_report`, `created_at`, `completed_at`

4 IMO bundle columns (migration `0024_fce_imo_bundle.sql`):
`intake_yaml`, `workbench_pointer`, `intake_validated_at`, `planner_verdict`

#### Table: `dyno_run_cycle` — 10 columns

`cycle_id`, `run_id` (FK → dyno_run), `phase`, `model`, `prompt_hash`,
`response_hash`, `tokens_in`, `tokens_out`, `cost_usd`, `duration_ms`, `created_at`

#### Migrations (applied order)

| File | Contents |
|------|----------|
| `workers/mission-control-api/migrations/0018_dyno_run.sql` | CREATE dyno_run + dyno_run_cycle + indexes (BAR-345 base — 16 columns) |
| `workers/mission-control-api/migrations/0024_fce_imo_bundle.sql` | ALTER dyno_run: +4 IMO bundle columns + backfill |

### R2 Bucket

| Field | Value |
|-------|-------|
| bucket_name | `svg-files` |
| binding | `R2_SVG_FILES` |
| path pattern | `r2://svg-files/dyno-runs/{sovereign_id}/` |
| workbench window | FCE-02 through FCE-12 |
| cleanup gate | D1 INSERT confirmed (INV-10) |
| fallback | R2 stays intact if D1 fails |

### Mission Control API Endpoints (proc060.ts)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/proc-060/queue` | Planner queue — 4 buckets (incoming / processing / done / failed) |
| GET | `/api/proc-060/runs` | List dyno_run rows with intake metadata; `limit` param |
| GET | `/api/proc-060/run/:id` | Full run detail — phases, cycles, intake_yaml, workbench_pointer |
| POST | `/api/proc-060/intake` | Submit new FCE intake; creates dyno_run row in `pending` state |
| POST | `/api/proc-060/retry/:id` | Re-submit failed run; new dyno_run row with same intake_yaml |
| POST | `/api/proc-060/cancel/:id` | Cancel pending/running run; sets status=`cancelled` |

### Mission Control UI

| File | Role |
|------|------|
| `workers/mission-control/src/pages/RunDyno.tsx` | Run Dyno page — queue view + intake form |
| `workers/mission-control/src/components/Shell.tsx` | Route registered here |
| `workers/mission-control/src/navigation.ts` | Nav node added (heirId: `proc-060`) |

### Planner + Dispatcher (local Python)

| File | Role |
|------|------|
| `imo-creator-v2/atlas/dyno/planner/planner.py` | Planner: polls D1 for pending rows, runs BS Law lens, queues to intake |
| `imo-creator-v2/atlas/dyno/planner/planner-queue/incoming/` | Drop zone for new FCE intake YAMLs |
| `imo-creator-v2/atlas/dyno/planner/planner-queue/processing/` | In-flight planner validation |
| `imo-creator-v2/atlas/dyno/planner/planner-queue/done/` | Passed validation — moved to inbox |
| `imo-creator-v2/atlas/dyno/planner/planner-queue/failed/` | Failed validation — structured failure report |
| `imo-creator-v2/atlas/dyno/dispatch_fce.py` v1.2.0 | Dispatcher: fires Dyno engine with domain + P=1 from intake_yaml |
| `imo-creator-v2/atlas/dyno/inbox/` | Inbox queue — validated YAMLs land here before engine claim |

---

## §3f VOCABULARY

Inherits: `imo-creator-v2/atlas/constants/KEY.md` v1.0.3 (full vocabulary — Thing, Flow, Change, C&V, IMO, CTB, Circle, HEIR, ORBT, US, UP, DMJ, FCE, P=1, K=C, Sigma, Back-Prop).

FCE-specific terms:

| Term | Definition |
|------|------------|
| US | Universal Structure — discovers the constant set (M) for any domain. Produces invariant set at primitive leaf. **US P=1 is a distinct gate from UP tolerance.** |
| UP | Universal Process — consumes remaining I using locked M. UP tolerance is domain-specific, human-declared. **NOT the same as US P=1.** |
| K=C Lock | Bridge step: constants certified by US output are locked into M; variables remain in I; domesticated variables removed. AFTER US P=1; BEFORE UP runs. |
| US P=1 | All four FCE columns (Valuation → Concentration → Trend → Liquidity) have primitive leaves AND Three Primitives satisfied at leaf level. Structure fully decomposed. |
| UP Tolerance | Human-declared stop condition for UP solve phase. Domain-specific. **NOT the same as US P=1.** |
| FCE | Failure Classification Engine — four columns in locked order: **Valuation** (Thing — is it priced right?) → **Concentration** (Flow — where is the herd?) → **Trend** (Change — is the change sustainable?) → **Liquidity** (Connection — can the system execute?). Gate outputs: GO / MONITOR / NO-GO / UNCLASSIFIABLE. |
| R2 | Cloudflare R2 object storage. **Live workbench ONLY** during active run (FCE-02 through FCE-12). NOT the vault. Cleaned ONLY after D1 INSERT confirmed. |
| D1 | Cloudflare D1 SQLite database. **Completed-run vault ONLY**. Receives one `dyno_run` INSERT at FCE-13, ONLY after Codex PASS. NOT a scratchpad. |
| sovereign_id | UUID assigned to a completed FCE run. Primary key for R2 path and D1 row. |
| DMJ | Define · Map · Join. **Deferred at N=1** (single run). Queued at N≥2 same family. Gets its own separate process number. |
| Expensive tier | OpenRouter model tier — locked for all FCE runs. No cheap-tier rotation. Three models per cycle. |
| PROC-080 | FCE-Fill — reference fill logic. Absorbed; NOT a second runtime. |
| PROC-090 | FCE-Computer-Programming — artifact/library evidence only. NOT a runtime. |

---

## §4 MIDDLE — OPERATOR SEQUENCE

### FCE Operator Steps (FCE-00 through FCE-14)

| Step | ID | Action | Owner | Inputs | Outputs | Guard Rails |
|------|----|--------|-------|--------|---------|-------------|
| PLN-00 | PLN-00 | Planner gate — substrate-awareness validation of FCE intake YAML | Operator + planner.py (Sonnet, tactical scope) | Filled FCE intake YAML; FCE_DESCRIPTION_GUIDANCE 7-item checklist | PASS: validated intake → engine inbox; FAIL: structured failure report → operator | Determinism-first (mechanical checks before LLM); role-lock per FOUR_BRAIN_AVIATION; engine internals never touched |
| 0 | FCE-00 | Pre-flight — verify env, secrets, CLI, input shape | Operator | Shell session | Four env vars confirmed; domain string written; P=1 written | STOP if any env var missing; STOP if domain string malformed (no em-dash); STOP if P=1 undefined |
| 1 | FCE-01 | Name domain — declare topic, description, domain_string, fce_id, family | Operator | Domain knowledge; `atlas/manifests/fce-registry.yaml` (uniqueness check) | Locked input manifest (domain_string, fce_id, family) | STOP if fce-id not unique in registry; domain string = `"<topic> — <description>"` using em-dash separator; never two CLI args |
| 2 | FCE-02 | Open R2 intake record — first landing; R2 workbench path created | `run_fce.py` | Locked inputs from FCE-01; `sovereign_id` passed via `--sovereign-id <uuid>` (minted by inbox dispatcher at intake claim per INV-19) | R2 path `r2://svg-files/dyno-runs/{sovereign_id}/` initialized | R2 = live workbench; **DO NOT write to D1 yet**; sovereign_id is the durable run identity — minted at dispatcher claim, not here (INV-19) |
| 3 | FCE-03 | Name UP tolerance — operator declares domain-specific UP stop condition | Operator | Domain knowledge; P=1 definition | UP tolerance declared (written, not inferred) | UP tolerance is domain-specific and human-declared; **NOT the same as US P=1**; must be declared explicitly before US loop starts |
| 4 | FCE-04 | Lock model set — confirm exactly three OpenRouter expensive-tier models | Operator / `run_fce.py` | OpenRouter API; Doppler OPENROUTER_API_KEY | Three model IDs confirmed; logged to R2 manifest | Expensive models only; **no cheap-tier rotation**; exactly three per cycle |
| 5 | FCE-05 | Start R2/OpenRouter workbench loop — fire three models in parallel for US discovery | `run_fce.py` | Locked inputs + model set | `runs/discover-{slug}/` artifacts in R2; US raw outputs per model | R2 = live workbench during all loop iterations; D1 write forbidden here; sigma tracking begins |
| 6 | FCE-06 | Run US (discover M) — apply C&V, classify constants vs variables per cycle; back-propagate | `run_fce.py` + models | US raw outputs from FCE-05 | Classification per candidate: 3/3 locked / 2/3 high-confidence / 1/3 investigate | 2/3 majority = locked; do NOT chase 3/3 unanimity; back-propagate on every new lock; sigma: tightening = real, flat = phantom, expanding = broken upstream |
| 7 | FCE-07 | Check US P=1 — verify all four FCE columns have primitive leaves | `run_fce.py` + Operator | US classified candidates from FCE-06 | `kc-audit*.json` with MATCH / MISMATCH / SPLIT per candidate; US P=1 GO/STOP | US P=1 = all four columns (Valuation → Concentration → Trend → Liquidity) at primitive with Three Primitives at leaf; **US P=1 is a distinct gate from UP tolerance**; STOP if any column missing leaves |
| 8 | FCE-08 | K=C lock — resolve mismatches; lock constants into M; remove domesticated | `apply_kc_corrections_and_refire.py` + Operator | `kc-audit*.json` from FCE-07 | `engine-final-locked.json` (locked M) | K=C lock AFTER US P=1; BEFORE UP runs (INV-05); constants → M; variables → remain in I; domesticated → removed; re-run US if MISMATCH found |
| 9 | FCE-09 | Run UP (consume I via locked M until UP tolerance satisfied) | `dyno_engine.py solve` + models | Locked M from FCE-08; P=1 definition; UP tolerance from FCE-03 | `runs/solve-{slug}/engine-final.json`; UP P=1 confirmation | UP tolerance governs stop; **NOT US P=1**; UP does NOT self-certify; HALT for TS rather than guess; three models per cycle (expensive tier) |
| 10 | FCE-10 | Emit O — synthesize FCE output; produce four-column result (Valuation → Concentration → Trend → Liquidity) | `run_recipe_synthesis.py` + `run_recipe_synthesis_bs_law.py` | UP P=1 output from FCE-09 | Three raw `.md` recipes (human-readable); three BS Law `.yaml` recipes (Y-junction compliant) | BS Law Y-junction required on all YAML outputs; `outside:` and `inside:` must be syntactically distinct top-level keys; no merged arms |
| 11 | FCE-11 | Verify R2 package — inspect manifest, evidence, model rows | Operator | All run artifacts in R2 | Operator GO / STOP; manifest verified | Human gate; cannot be skipped or delegated to LLM; confirm all artifacts present before Codex dispatch |
| 12 | FCE-12 | Codex audit/check on R2 package — dispatch complete run to auditor | Operator | R2 artifacts + run evidence | Codex verdict (PASS / FAIL / DEFER) | Auditor MUST be different inference engine than the three run models and different from Mechanic; no self-auditing; Aviation Model invariant preserved |
| 13 | FCE-13 | Vault to D1 + clean R2 — INSERT dyno_run + dyno_run_cycle rows; THEN clean R2 | `run_fce.py` | Codex PASS verdict from FCE-12; run data (costs, cycles, models, sovereign_id) | `dyno_run` row (status=completed, verdict set); `dyno_run_cycle` rows (one per model per cycle — three per cycle) | D1 INSERT ONLY on Codex PASS; D1 is NOT a scratchpad; **R2 cleanup ONLY after D1 INSERT confirmed**; one `dyno_run` row per FCE run; three `dyno_run_cycle` rows per cycle; every cycle from all three OpenRouter model tests stored under sovereign ID |
| 14 | FCE-14 | Certify or repair — write LBB CERTIFY row on PASS; squawk + Four-Brain repair on FAIL | Operator | D1 INSERT confirmed + Codex PASS (or FAIL) | PASS: LBB CERTIFY row; `atlas/manifests/fce-registry.yaml` append hint; FCE registered in library. FAIL: squawk filed; Four-Brain repair initiated (separate BAR) | **FCE library registration only after BOTH Codex PASS AND D1 INSERT confirmed**; LBB CERTIFY row is append-only; registry append is manual (operator-owned); **DMJ deferred at N=1** (if N≥2 same family: queue DMJ rebuild under separate process number per Q-01); MC wiring deferred per Q-03 |

### Key Sequencing Constraints

- **R2 = live workbench (FCE-02 → FCE-12).** D1 write is FCE-13 only, after Codex PASS.
- **D1 INSERT only on Codex PASS.** D1 is the vault, not the scratchpad.
- **R2 cleanup only after D1 INSERT confirmed.** If D1 fails, R2 stays intact (only fallback).
- **US P=1 ≠ UP tolerance.** Two separate gates. US P=1 gates the K=C lock (FCE-07). UP tolerance governs the UP solve completion (FCE-09).
- **K=C lock (after US P=1, before UP runs).** Constants → M. Variables → stay in I. Domesticated → removed.
- **FCE library registration only after BOTH Codex PASS and D1 INSERT succeed.**
- **DMJ boundary at FCE-14.** DMJ does NOT appear inside the single-run path. Deferred at N=1. Queued at N≥2 same family. Separate process number.
- **Four columns in locked order throughout:** Valuation → Concentration → Trend → Liquidity.

---

## §5 OSAM

### READ

| Source | What | When |
|--------|------|------|
| `atlas/dyno/us.py` | US engine (sealed — zero bytes written) | FCE-06 — called by `dyno_engine.py discover` |
| `atlas/dyno/up.py` | UP engine (sealed — zero bytes written) | FCE-09 — called by `dyno_engine.py solve` |
| `atlas/dyno/dyno_engine.py` | Runner | FCE-05, FCE-06, FCE-09 |
| `atlas/dyno/run_fce.py` | Full orchestrator | All FCE steps |
| `atlas/manifests/fce-registry.yaml` | FCE registry | FCE-01 (uniqueness check) + FCE-14 (append hint) |
| OpenRouter API | Model responses (expensive tier × 3) | FCE-05, FCE-06, FCE-09, FCE-10 |
| Cloudflare R2 | Artifact reads + writes (workbench only) | FCE-02 through FCE-12 |
| D1 `mission-control` | `dyno_run` + `dyno_run_cycle` | FCE-13 (write only, after Codex PASS) |
| LBB API | Role-transition + CERTIFY rows | All role transitions + FCE-14 |

### WRITE

| Destination | What | When | Guard |
|-------------|------|------|-------|
| R2 `r2://svg-files/dyno-runs/{sovereign_id}/` | All run artifacts (US outputs, K=C audit, UP outputs, six recipes) | FCE-02 through FCE-12 (workbench) | R2 is workbench only; cleaned ONLY after D1 INSERT confirmed (INV-10) |
| D1 `dyno_run` | One completed-run row per FCE run | FCE-13 ONLY | Codex PASS required; no provisional inserts; NOT a scratchpad (INV-09) |
| D1 `dyno_run_cycle` | Three rows per cycle (one per model) — all models, all cycles | FCE-13 ONLY | Co-inserted with `dyno_run`; every cycle from all three OpenRouter model tests stored under sovereign ID |
| LBB | Role-transition rows + CERTIFY row | Every role transition + FCE-14 CERTIFY | Append-only; subject = `processes` |
| `atlas/manifests/fce-registry.yaml` | FCE entry append hint | FCE-14 manual (PASS path only) | Operator-owned; auditor does not touch registry |

### Process Composition

```
run_fce.py (HUB orchestrator)
  ├── FCE-02: R2 intake record (first landing)
  ├── FCE-05/06: dyno_engine.py discover → calls us.py (READ-ONLY)
  │     └── three OpenRouter models (expensive tier, parallel spokes)
  ├── FCE-07: K=C audit (run_kc_audit.py)
  ├── FCE-08: K=C corrections + refire (apply_kc_corrections_and_refire.py)
  ├── FCE-09: dyno_engine.py solve → calls up.py (READ-ONLY)
  │     └── three OpenRouter models (expensive tier, parallel spokes)
  ├── FCE-10: recipe synthesis (run_recipe_synthesis.py + run_recipe_synthesis_bs_law.py)
  ├── FCE-11/12: R2 artifact review + Codex audit dispatch
  └── FCE-13: D1 INSERT — ONLY on Codex PASS; R2 cleanup ONLY after D1 confirmed
```

Hub = `run_fce.py` (all logic). Spokes = OpenRouter models (dumb transport). Boundary = R2 artifacts (workbench) + D1 rows (vault).

### Join Chain

```
domain string + P=1 + UP tolerance
  → R2 intake record (FCE-02)
  → US discover loop (FCE-05/06: us.py via dyno_engine.py, × 3 models)
  → US P=1 check (FCE-07: all four columns at primitive)
  → K=C lock (FCE-08: engine-final-locked.json)
  → UP solve loop (FCE-09: up.py via dyno_engine.py, × 3 models, until UP tolerance)
  → FCE output synthesis (FCE-10: 3 raw .md + 3 BS Law .yaml)
  → R2 package verification (FCE-11: human gate)
  → Codex audit (FCE-12: PASS / FAIL / DEFER)
  → D1 vault (FCE-13: dyno_run + dyno_run_cycle INSERT, after PASS only)
  → R2 cleanup (FCE-13: ONLY after D1 INSERT confirmed)
  → LBB CERTIFY + fce-registry.yaml append hint (FCE-14, PASS path)
```

### Forbidden

| Forbidden Action | Reason | INV |
|-----------------|--------|-----|
| Write to `atlas/dyno/us.py` | Locked constant #7 — sealed. Zero bytes. | Atlas locked-constants doctrine |
| Write to `atlas/dyno/up.py` | Locked constant #8 — sealed. Zero bytes. | Atlas locked-constants doctrine |
| Write to D1 before Codex PASS | D1 is vault, not scratchpad. No provisional inserts. | INV-09 |
| Describe D1 as workbench or scratchpad | D1 is vault-only. Workbench is R2. | INV-09 |
| Clean R2 before D1 INSERT confirmed | R2 is the only fallback if D1 fails. | INV-10 |
| Self-auditing (Mechanic = Auditor) | Aviation model — mechanic cannot be inspector. Different engines required. | INV-13 |
| DMJ inside single-run path (FCE-00 through FCE-14) | DMJ deferred at N=1. Runs only at N≥2 same family. Separate process number. | INV-18 |
| Cheap-tier OpenRouter models | Expensive tier only — locked. Three per cycle. | INV-03 |
| Conflating US P=1 with UP tolerance | Two separate gates. US P=1 gates K=C lock. UP tolerance gates UP solve completion. | INV-04, INV-07 |
| FCE library registration before Codex PASS + D1 | Library must contain only certified runs with vault evidence. | INV-16 |
| Alter four-column order | Locked order: Valuation → Concentration → Trend → Liquidity. | INV-04 |
| Treat PROC-080 as a second runtime | PROC-080 is reference fill logic — absorbed, not a second FCE run process. | INV-01 |

### Query Routing

| Query | Route |
|-------|-------|
| "Show all FCE runs" | D1 `dyno_run` table — query by domain, status, verdict |
| "Show cycles for run X" | D1 `dyno_run_cycle` table — filter by run_id |
| "Get raw artifacts for run X" | R2 path `r2://svg-files/dyno-runs/{sovereign_id}/` |
| "What FCEs are registered?" | `atlas/manifests/fce-registry.yaml` |
| "Show in Mission Control" | `workers/mission-control/src/pages/RunDyno.tsx` — queue view + run list via `/api/proc-060/runs` |

---

## §5a NON-DRIFT INVARIANTS (INV-01…INV-21)

These 21 invariants must hold at every step. Violation = STOP condition.

| ID | Invariant | Enforced At |
|----|-----------|-------------|
| INV-01 | PROC-060 is the single FCE run process. No second FCE run process outside PROC-060 may exist. PROC-080 is reference fill logic (absorbed). PROC-090 is artifact/library evidence only. | All steps |
| INV-02 | Domain string format is `"<topic> — <description>"` using em-dash separator — single string, topic + description joined. Never two CLI args. | FCE-00, FCE-01 |
| INV-03 | Exactly three OpenRouter models (expensive tier only) run per cycle. No cheap-tier rotation. | FCE-04, FCE-05, FCE-09 |
| INV-04 | US P=1 = all four FCE columns (Valuation → Concentration → Trend → Liquidity) have primitive leaves AND Three Primitives satisfied at leaf level. **This is a distinct gate from UP tolerance.** US P=1 must not be conflated with UP tolerance under any circumstance. | FCE-07 |
| INV-05 | K=C lock happens AFTER US P=1 and BEFORE UP runs. No UP call before K=C lock. | FCE-08, FCE-09 |
| INV-06 | K=C consensus threshold: 2/3 majority = locked. Do NOT chase 3/3 unanimity. | FCE-06, FCE-07 |
| INV-07 | UP tolerance is domain-specific and human-declared. UP does not self-certify. HALT for TS rather than guess. **UP tolerance is NOT the same as US P=1.** | FCE-03, FCE-09 |
| INV-08 | P=1 definition is declared before the run fires. Never inferred mid-run. | FCE-01 |
| INV-09 | D1 INSERT (`dyno_run` + `dyno_run_cycle`) occurs ONLY at FCE-13, ONLY after Codex PASS. No provisional D1 writes. D1 is the completed-run vault — NOT a scratchpad, NOT a workbench. | FCE-13 |
| INV-10 | R2 cleanup occurs ONLY after D1 INSERT is confirmed. If D1 fails, R2 stays intact (only fallback). | FCE-13 |
| INV-11 | R2 + OpenRouter is the live workbench during the active model loop (FCE-02 through FCE-12). D1 receives data only at FCE-13 after Codex PASS. | FCE-02 through FCE-12 |
| INV-12 | BS Law Y-junction: every YAML recipe artifact and companion YAML must have `outside:` and `inside:` as syntactically distinct top-level keys. No merged arms. No same-name siblings. | FCE-10 |
| INV-13 | Auditor (Codex) must be a different inference engine than the three run models and different from the Mechanic. No self-auditing under any circumstance. Aviation Model invariant. | FCE-12 |
| INV-14 | Sigma tracking required across cycles: tightening = real constant (lock it), flat = phantom (investigate), expanding = broken upstream (go back). | FCE-06, FCE-09 |
| INV-15 | Back-propagation required on every new constant: new lock triggers revalidation of ALL prior constants with updated θ'. | FCE-06, FCE-08 |
| INV-16 | FCE library registration occurs ONLY after BOTH Codex PASS AND D1 INSERT are confirmed. Not before. Both conditions required simultaneously. | FCE-14 |
| INV-17 | LBB row is written at every role transition (planner, foreman, mechanic, auditor) and at FCE-14 CERTIFY on Codex PASS. Append-only. Subject = `processes`. | All transitions + FCE-14 |
| INV-18 | DMJ does NOT appear inside the single-run path (FCE-00 through FCE-14). DMJ is deferred at N=1. DMJ is queued and runs only at N≥2 same family. DMJ gets its own separate process number (confirmed Plan Book §15 Q-01). DMJ output returns to D1. | FCE-14 |
| INV-19 | sovereign_id (UUIDv4) is minted by the inbox dispatcher at the moment the work-packet YAML is claimed from `inbox/` to `inbox/processing/`. This is the FIRST action of the run. The dispatcher passes sovereign_id to `run_fce.py` via `--sovereign-id <uuid>`. All cycle artifacts, phase verdicts, R2 paths, D1 row keys, and LBB records derive from this single sovereign_id. The engine's internal run_id is sealed bookkeeping and is NOT used as the durable identifier. | Dispatcher claim (mint), FCE-02 (R2 init), every PHASE_VERDICT.json, FCE-13 (D1 insert), FCE-14 (LBB record) |
| INV-20 | Each FCE phase produces a self-contained artifact set in its own folder under `runs/{sovereign_id}/fce-NN-<name>/` plus a `PHASE_VERDICT.json` readable independently of any other phase. Codex audits each phase by reading only that phase's folder. No phase may write artifacts outside its own folder. | FCE-05, FCE-07, FCE-08, FCE-09, FCE-10, FCE-13, FCE-14 |
| INV-21 | A `RUN_VERDICT.json` is written at `runs/{sovereign_id}/` and updated after each phase completes. It is the single source of truth for "which phases of this run passed, which failed, which are pending." | Every phase completion |

---

## §6 INPUTS

### Required Inputs

| Input | Format | Source | Guard |
|-------|--------|--------|-------|
| `domain_string` | String — `"<topic> — <description>"` with em-dash separator | Operator declaration (FCE-01) | Malformed domain string → STOP at FCE-00 |
| `p1_definition` | String — explicit stop condition for UP solve | Operator declaration (FCE-01) | Undefined P=1 → STOP at FCE-01 |
| `fce_id` | Slug string (e.g., `sql`, `schemas`) | Operator declaration (FCE-01) | Must be unique in `atlas/manifests/fce-registry.yaml` |
| `family` | String (e.g., `programming`) | Operator declaration (FCE-01) | Governs DMJ queue logic at N≥2 |
| `up_tolerance` | Human-declared stop condition for UP phase | Operator declaration (FCE-03) | Cannot be inferred; must be explicit; **NOT the same as US P=1** |

### Environment Inputs (pre-flight, FCE-00)

| Variable | Source | Purpose |
|----------|--------|---------|
| `OPENROUTER_API_KEY` | Doppler: `imo-creator / dev` | OpenRouter model calls |
| `CLOUDFLARE_API_TOKEN` | Doppler: `imo-creator / dev` | R2 push + D1 write |
| `LBB_API_KEY` | Doppler: `imo-creator / dev` | LBB row writes |
| `PYTHONUTF8=1` | Shell export | UTF-8 safety for all Python I/O |

---

## §7 OUTPUTS

### Evidence Artifacts (stored in R2 `r2://svg-files/dyno-runs/{sovereign_id}/`)

| Artifact | Format | Produced At |
|----------|--------|-------------|
| R2 intake manifest | JSON — run metadata, inputs | FCE-02 |
| `runs/discover-{slug}/engine-final.json` | JSON — raw US candidates per model | FCE-05/FCE-06 |
| `kc-audit*.json` | JSON — K=C audit results per candidate (MATCH / MISMATCH / SPLIT) | FCE-07 |
| `engine-final-locked.json` (locked M) | JSON — K=C-certified constants locked into M | FCE-08 |
| `runs/solve-{slug}/engine-final.json` | JSON — UP P=1 confirmation per model | FCE-09 |
| Three raw `.md` recipes | Markdown — FCE recipe output, human-readable | FCE-10 |
| Three BS Law `.yaml` recipes | YAML — BS Law Y-junction compliant, `outside:`/`inside:` syntactically distinct | FCE-10 |
| Codex audit report | Markdown | FCE-12 |

### D1 Records (vault — FCE-13 only, after Codex PASS)

| Table | Row Count | Key Fields |
|-------|-----------|------------|
| `dyno_run` | One per FCE run | run_id (UUID / sovereign_id), domain, p1_definition, status='completed', verdict, r2_artifact_path, cost_usd, cycle_count, models_used, completed_at |
| `dyno_run_cycle` | Three per cycle (one per model) — all cycles | cycle_id, run_id, phase, model, prompt_hash, response_hash, tokens_in, tokens_out, cost_usd, duration_ms |

Schema source: `workers/mission-control-api/migrations/0018_dyno_run.sql` (16 cols) + `workers/mission-control-api/migrations/0024_fce_imo_bundle.sql` (4 IMO bundle cols)

### LBB Records

| Record Type | Subject | Written At |
|-------------|---------|------------|
| Role-transition row (role=mechanic, action=edit) | `processes` | Build time |
| CERTIFY row | `processes` | FCE-14 on Codex PASS |

### Storage / Evidence Contract Summary

| Store | Role | Timing |
|-------|------|--------|
| R2 + OpenRouter | Live workbench + active model loop | FCE-02 → FCE-12 |
| D1 (`dyno_run`, `dyno_run_cycle`) | Completed-run vault | FCE-13 only, after Codex PASS |
| R2 cleanup | Reset workbench | FCE-13, after D1 vault write success |
| Mission Control | Operator visibility — RunDyno.tsx + proc060.ts (BUILD) | Continuous |
| FCE library | Certified shelf | FCE-14 only (PASS path) |
| LBB | Role-transition + closeout memory | Every transition |
| GitHub | Versioned source | After audited file changes |
| DMJ process | Downstream convergence | N≥2 only; output back to D1 |

---

## §8 KILL SWITCH

**To stop any active FCE run immediately:**

```bash
# Kill the orchestrator process
kill $(pgrep -f run_fce.py)

# Or kill the dyno_engine process
kill $(pgrep -f dyno_engine.py)
```

**R2 state:** Artifacts written before kill are retained in R2. R2 cleanup requires explicit manual operator action (do NOT clean until D1 INSERT confirmed).

**D1 state:** If killed before FCE-13, D1 has no record of the run — this is correct. D1 only receives writes on Codex PASS at FCE-13.

**Recovery:** Restart from FCE-00 with the same domain string. R2 artifacts from the interrupted run are available for inspection under the run's R2 path if the push had started.

---

## §9 OBSERVABILITY

### Signals to Watch

| Signal | Source | What to Watch |
|--------|--------|---------------|
| US cycle convergence | `dyno_engine.py discover` stdout | Sigma tightening across cycles = real constants being locked |
| K=C audit pass rate | `kc-audit*.json` | MISMATCH count decreasing = progress; flat = phantom constant |
| UP cycle convergence | `dyno_engine.py solve` stdout | Coverage increasing, remainder decreasing; UP tolerance governs stop |
| R2 push status | `push_run_to_r2.py` stdout | Confirm all artifacts uploaded before FCE-11 |
| D1 INSERT status | `run_fce.py` log | `status = 'completed'` in `dyno_run` row after FCE-13 |
| LBB write status | LBB API response | HTTP 2xx = success |
| Total cost | `dyno_run.cost_usd` | Sum of all model calls for the run |
| Wall time | `completed_at - created_at` | Expected 15–40 minutes per FCE |

### D1 Query Patterns

```sql
-- All FCE runs
SELECT run_id, domain, status, verdict, cost_usd, completed_at FROM dyno_run ORDER BY completed_at DESC;

-- Cycles for a specific run
SELECT cycle_id, phase, model, tokens_in, tokens_out, cost_usd FROM dyno_run_cycle WHERE run_id = ? ORDER BY cycle_id;

-- Runs by family (DMJ readiness check)
SELECT domain, status, verdict, completed_at FROM dyno_run WHERE domain LIKE '%<family>%' ORDER BY completed_at;
```

### LBB Query Patterns

```bash
# Check LBB rows for this BAR
scripts/lbb-log.sh --query --subject-id processes --bar-id BAR-FCE-RUN-060-PLANNER
```

### Pressure Gauge (Stop Conditions)

| Condition | Action |
|-----------|--------|
| Any env var missing at FCE-00 | STOP — fix before firing |
| Domain string malformed (no em-dash separator) | STOP — correct format |
| P=1 undefined | STOP — declare before firing |
| fce-id not unique in registry | STOP — choose unique slug |
| US cycles hit max without all four columns at primitive | STOP — diagnose domain decomposition |
| R2 push fails | STOP — do not proceed to Codex or D1 |
| Codex FAIL verdict | STOP — diagnose, fix, re-run from FCE-00; strike ladder per PROC-070 §4 Step 6 |
| D1 INSERT fails | STOP — do not clean R2; preserve artifacts |
| us.py or up.py modified | STOP — locked constants; revert immediately; Airworthiness Directive candidate |

---

## §9b LIVE VERIFICATION

☐ **Legitimately deferred** — first FCE run not yet complete. Live verification requires at least one completed run (Codex PASS + D1 INSERT confirmed) to ground all counts, timing estimates, and command outputs against real observations.

When the first run completes, verify:
- [ ] `dyno_run` row count in D1 = 1
- [ ] `dyno_run_cycle` row count = (cycles × 3) per run
- [ ] R2 path `r2://svg-files/dyno-runs/{sovereign_id}/` contains all expected artifacts
- [ ] LBB CERTIFY row appears in subject `processes`
- [ ] Total wall time logged in `completed_at - created_at`
- [ ] `atlas/manifests/fce-registry.yaml` has the new entry

---

## §10 SUCCESS METRICS

### §10a Targets

| Metric | Target |
|--------|--------|
| US cycles to convergence | 1–3 cycles |
| K=C MATCH rate (round 1) | ≥ 7/10 candidates |
| UP cycles to P=1 | 1–3 cycles |
| Wall time per FCE run | 15–30 minutes |
| D1 INSERT latency | < 30 seconds |
| R2 push latency | 5–8 minutes |

### §10b Tolerances

| Metric | Tolerance | Notes |
|--------|-----------|-------|
| US cycles | ≤ 5 | Domain complexity drives this; > 5 = investigate domain string |
| K=C MATCH rate | ≥ 5/10 | Below 5/10 round 1 → re-examine domain string |
| UP cycles | ≤ 5 | Better K=C lock = fewer UP cycles |
| Wall time | ≤ 45 minutes | > 45 min → investigate model latency or domain decomposition |
| Total cost per run | TBD | Grounded after first live run |
| D1 INSERT latency | < 60 seconds | Cloudflare D1 write SLA |
| R2 push latency | < 15 minutes | Based on FCE_LIFECYCLE_RUNBOOK.md step 5 estimate |

### §10c Derivation

- US cycle targets derived from FCE Computer Programming (7/10 round 1 observed).
- UP cycle targets derived from locked M quality correlation with US cycle count.
- Wall time targets derived from FCE_LIFECYCLE_RUNBOOK.md orchestrator step timing table.
- Cost targets deferred until first live run produces actual OpenRouter billing data.

---

## §11 OUT OF SCOPE

| Item | Reason | Owner When It Lands |
|------|--------|---------------------|
| DMJ across multiple FCE runs | Deferred at N=1; separate process number confirmed (Plan Book §15 Q-01) | Dave Barton / follow-on BAR |
| Mission Control wiring | Wired — see §3a. RunDyno.tsx + proc060.ts live. MC surfaces: run list with domain/verdict/status, cycle detail drill-down, cost totals, R2 artifact links, three-model visibility, DMJ readiness flag. | Dave Barton |
| Domain-specific fill instructions | Handled by PROC-080 FCE-Fill (absorbed reference only; not a second runtime) | PROC-080 |
| Family-level aggregation | Post-DMJ concern; out of PROC-060 scope | DMJ process (TBD number) |
| Cross-FCE comparison / analytics | Post-DMJ + MC wiring concern | Follow-on processes |
| PROC-070 Four-Brain pipeline | PROC-070 is the build pipeline; it does not replace PROC-060 | PROC-070 |

---

## §12 LOGBOOK / BIRTH CERTIFICATE

☐ **Not yet certified.** This section is populated by the Auditor (Codex) on first PASS verdict.

| Field | Value |
|-------|-------|
| First PASS verdict | ☐ pending |
| Auditor | Codex (different inference engine from Mechanic — Aviation Model) |
| Audit date | ☐ pending |
| Audit BAR | BAR-FCE-RUN-060-PLANNER |
| LBB CERTIFY row | ☐ pending |

---

## §13 DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Template | UT v2.8.0 |
| Checklist | UT_CHECKLIST v1.3.1 |
| Book Law | v1.5.0 |
| BS Law | v1.5.0 |
| Four-Brain Aviation | v1.2.0 |
| Atlas | v2.3.0 |
| Created | 2026-05-05 |
| Last Modified | 2026-05-08 |
| Version | 1.1.1 |
| Status | BUILD |
| BAR | BAR-FCE-RUN-060-PLANNER |
| Companion YAML | `Barton-Processes/factory/imo-creator/060-run-dyno/run-dyno.yaml` |
| Built By | Sonnet (Mechanic role — PROC-070 Four-Brain Aviation Model) |
| Certified By | ☐ Codex (pending) |

---

## §14 MAINTENANCE LOGBOOK

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-05-05 | 1.0.0 | Initial creation — full UT-Body v1.0.0 per UT v2.8.0 + UT_CHECKLIST v1.3.1. FCE-00 through FCE-14 operator sequence per BAR-FCE-RUN-060-PLANNER Plan Book §7 locked step spine. All 18 invariants `INV-01…INV-18` encoded. BS Law v1.5.0 Y-junction conformant. Companion YAML: run-dyno.yaml. | Sonnet (Mechanic — BAR-FCE-RUN-060-PLANNER) |
| 2026-05-08 | 1.1.0 | Absorb `AMENDMENT-PHASE-BARRIERS-AND-SOVEREIGN-ID.md`. Add PLN-00 (Planner gate) at step 0. Add INV-19 (sovereign_id at intake), INV-20 (phase barriers), INV-21 (run verdict rollup). Bump Atlas pin v2.2.7 → v2.3.0. Lock-stepped with run-dyno.yaml v1.1.0. | Sonnet (Mechanic — BAR-PROC-060-V1-1-0-PHASE-BARRIERS) |
| 2026-05-08 | 1.1.1 | Documentation update — concrete wiring captured in §3a (D1 db id 9f01c45a, binding MC_DB; R2 bucket svg-files, binding R2_SVG_FILES; migrations 0018+0024; MC API proc060.ts; MC UI RunDyno.tsx; Planner + Dispatcher paths). No doctrine changes. Pairs with imo-creator-v2 commit a7403355. | Sonnet (Mechanic) |

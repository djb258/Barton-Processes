> **STATUS: ABSORBED 2026-05-08** — Content folded into PROCESS-UT.md v1.1.0 (§4, §5a INV-19/20/21, §13, §14) and run-dyno.yaml v1.1.0 (FCE-02 update, INV-19/20/21 appended). This file retained for historical traceability per the Logbook Historical Phrases protocol. Do not edit further. See `pending-atlas-updates/BAR-PROC-060-V1-1-0-PHASE-BARRIERS.yaml` for the absorbing BAR.

# AMENDMENT — Phase Barriers + Sovereign-ID-At-Start

**Status:** PENDING (proposed amendment to PROC-060 v1.0.0 → v1.1.0)
**Authority:** Dave Barton (sovereign)
**Date proposed:** 2026-05-07
**Companion:** Mirror of this doc lives at `dyno-engine/AMENDMENT-PHASE-BARRIERS-AND-SOVEREIGN-ID.md` (private repo) — lock-stepped per BS Law.
**Affects:** `PROCESS-UT.md` §4, §5a, §7  +  `run-dyno.yaml` invariants list, FCE-02 node, FCE-13 node

---

## Why

Two structural defects in the v1.0.0 implementation:

1. **No sovereign_id at the start of the run.** Per FCE-02 doctrine ("R2 path `r2://svg-files/dyno-runs/{sovereign_id}/` initialized"), sovereign_id should mint at the **first step**. In the v1.0.0 wrapper (`atlas/dyno/run_fce.py`), sovereign_id mints at FCE-13 (R2 push, end of run). Cycles produced by US discover and UP solve are not stamped with sovereign_id — they have engine-assigned 8-char `run_id`s that don't connect across phases. Validated 2026-05-07: live FCE run for tier-count had US `run_id=7bd90439`, UP `run_id=d836bce6`, no shared sovereign stamp.

2. **No phase barriers between tests.** US, K=C, and UP all dump artifacts into one flat `discover-{slug}/` folder + one flat `solve-{slug}/` folder. The K=C audit produces a `kc-audit.json` file sitting next to US cycle files. There is no visible boundary saying "US ended here, K=C started there, here is K=C's verdict on its own." The auditor cannot read one phase's output without seeing the others. Operator cannot inspect K=C in isolation. Aviation Model is partially violated — Codex sees bundled artifacts, not separable phase artifacts.

## What changes

### Sovereign_id at intake (the very first step)

- The **inbox dispatcher** mints `sovereign_id = uuid.uuid4()` at the moment the work-packet YAML is claimed from `inbox/` to `inbox/processing/`. This is the FIRST action after the operator's drop. Sovereign_id is the run's durable identity from the moment the run is born — not the moment it ends.
- The dispatcher passes sovereign_id to `run_fce.py` as `--sovereign-id <uuid>`.
- `run_fce.py` uses sovereign_id as the root for all phase folders: `atlas/dyno/runs/{sovereign_id}/fce-NN-<name>/`.
- All downstream subprocesses (engine discover, engine solve, K=C audit, recipe synthesis, R2 push, D1 insert, LBB ingest) receive `--output-dir` rooted at `atlas/dyno/runs/{sovereign_id}/<phase-folder>/`.
- The dispatcher records sovereign_id in the work-packet YAML metadata before claim, so failed/done copies retain the trace.
- `dyno_engine.py` keeps minting its internal short `run_id` for in-engine bookkeeping (engine stays sealed). The wrapper-controlled folder structure, verdict files, R2 paths, D1 inserts, and LBB records all key off `sovereign_id`.

### Phase folder layout

Replace the flat `discover-{slug}/` + `solve-{slug}/` layout with:

```
atlas/dyno/runs/{sovereign_id}/
  fce-05-us-discover/      cycles + engine-final.json + PHASE_VERDICT.json
  fce-07-kc-audit/         kc-audit.json + PHASE_VERDICT.json
  fce-08-kc-lock/          engine-final-locked.json + PHASE_VERDICT.json
  fce-09-up-solve/         cycles + engine-final.json + PHASE_VERDICT.json
  fce-10-recipes/          raw-*.md + bs-law-*.yaml + PHASE_VERDICT.json
  fce-13-vault/            PHASE_VERDICT.json
  fce-14-certify/          PHASE_VERDICT.json
  RUN_VERDICT.json         top-level rollup of all PHASE_VERDICTs
```

Each phase folder is **self-contained**. Codex audit on the K=C step reads only `fce-07-kc-audit/`. Operator inspecting UP solve reads only `fce-09-up-solve/`. No cross-phase leakage.

### PHASE_VERDICT.json schema

Every phase emits one verdict file. Minimum fields:

```json
{
  "sovereign_id": "<uuid>",
  "phase_id": "fce-NN-<name>",
  "status": "PASS | FAIL | PENDING",
  "started_at": "<ISO-8601>",
  "completed_at": "<ISO-8601 | null>",
  "summary": { "...phase-specific fields..." },
  "artifacts": ["filename1", "filename2", "..."],
  "next_phase": "fce-NN-<name> | null"
}
```

Per-phase `summary` shapes:
- `fce-05-us-discover` — `{ p_status, m_size, i_size, total_cycles, sigma_final_direction, total_cost }`
- `fce-07-kc-audit` — `{ MATCH, MISMATCH, SPLIT, INSUFFICIENT, total }`
- `fce-08-kc-lock` — `{ locked_count, demoted_count, domesticated_count }`
- `fce-09-up-solve` — `{ up_tolerance_reached, total_cycles, remainder_count, total_cost }`
- `fce-10-recipes` — `{ raw_count, bs_law_count, y_junction_pass }`
- `fce-13-vault` — `{ d1_run_id, d1_cycle_rows_inserted, r2_cleaned }`
- `fce-14-certify` — `{ codex_verdict, lbb_record_id, registry_appended }`

### RUN_VERDICT.json schema

Top-level rollup at `runs/{sovereign_id}/RUN_VERDICT.json`:

```json
{
  "sovereign_id": "<uuid>",
  "fce_id": "<slug>",
  "family": "<family>",
  "domain": "<full em-dash domain string>",
  "p1_definition": "<full p1>",
  "started_at": "<ISO-8601>",
  "completed_at": "<ISO-8601 | null>",
  "phases": {
    "fce-05-us-discover": "PASS | FAIL | PENDING",
    "fce-07-kc-audit": "...",
    "fce-08-kc-lock": "...",
    "fce-09-up-solve": "...",
    "fce-10-recipes": "...",
    "fce-13-vault": "...",
    "fce-14-certify": "..."
  },
  "overall_status": "PASS | FAIL | IN_PROGRESS"
}
```

## New invariants

Insert into `run-dyno.yaml` invariants list and `PROCESS-UT.md` §5a:

**INV-19 — Sovereign-ID-At-Intake**
> sovereign_id (UUIDv4) is minted by the inbox dispatcher at the moment the work-packet YAML is claimed from `inbox/` to `inbox/processing/`. This is the FIRST action of the run. The dispatcher passes sovereign_id to `run_fce.py` via `--sovereign-id <uuid>`. All cycle artifacts, phase verdicts, R2 paths, D1 row keys, and LBB records derive from this single sovereign_id. The engine's internal run_id is sealed bookkeeping and is NOT used as the durable identifier.
> *Enforced at:* dispatcher claim (mint), FCE-02 (R2 init), every PHASE_VERDICT.json, FCE-13 (D1 insert), FCE-14 (LBB record).

**INV-20 — Phase Barriers**
> Each FCE phase produces a self-contained artifact set in its own folder under `runs/{sovereign_id}/fce-NN-<name>/` plus a `PHASE_VERDICT.json` readable independently of any other phase. Codex audits each phase by reading only that phase's folder. No phase may write artifacts outside its own folder.
> *Enforced at:* FCE-05, FCE-07, FCE-08, FCE-09, FCE-10, FCE-13, FCE-14.

**INV-21 — Run Verdict Rollup**
> A `RUN_VERDICT.json` is written at `runs/{sovereign_id}/` and updated after each phase completes. It is the single source of truth for "which phases of this run passed, which failed, which are pending."
> *Enforced at:* every phase completion.

## Implementation scope

- **Wrapper-only.** All changes land in `atlas/dyno/run_fce.py` and (optionally) helper scripts. Engine (`dyno_engine.py`, `us.py`, `up.py`) stays sealed — engine still receives `--output-dir` and writes cycles into whatever path the wrapper passes.
- **No engine changes required.** The phase folders are created by the wrapper before invoking the engine subprocess; the engine just writes into the directory it's given.
- **Backward-compat note:** Existing `runs/discover-*/` and `runs/solve-*/` from past runs stay where they are. The new layout applies to runs minted after this amendment is implemented.

## Verification plan

After implementation, fire one FCE through the inbox dispatcher. Confirm:
1. `runs/{sovereign_id}/` exists with the seven phase folders.
2. Each phase folder contains its expected artifacts + PHASE_VERDICT.json.
3. PHASE_VERDICT.json files all carry the same sovereign_id.
4. RUN_VERDICT.json at the run root rolls up all phase statuses.
5. D1 `dyno_run` row keyed by sovereign_id.
6. D1 `dyno_run_cycle` rows all carry sovereign_id as foreign key.
7. R2 path `r2://svg-files/dyno-runs/{sovereign_id}/` mirrors the local layout.

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Sovereign (proposer) | Dave Barton | 2026-05-07 | proposed |
| Mechanic (implementer) | TBD (Sonnet) | TBD | pending |
| Auditor (certifier) | Codex | TBD | pending |

## Document control

| Field | Value |
|-------|-------|
| Version | 1.0.0 (this amendment) |
| Status | PROPOSED |
| Created | 2026-05-07 |
| Last Modified | 2026-05-07 |
| Mirror | `dyno-engine/AMENDMENT-PHASE-BARRIERS-AND-SOVEREIGN-ID.md` |
| Affects | PROC-060 → v1.1.0 (PROCESS-UT.md + run-dyno.yaml lock-stepped) |

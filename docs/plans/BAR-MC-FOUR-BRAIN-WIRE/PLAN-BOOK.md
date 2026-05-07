---
title: "Plan Book — BAR-MC-FOUR-BRAIN-WIRE"
species: Plan-Body
bar_id: BAR-MC-FOUR-BRAIN-WIRE
process_id: PROC-070
version: 0.1.0
status: SIGNED_PENDING_DISPATCH
created: 2026-05-06
authored_by: Planner (Opus 4.7 collaborative + sovereign)
sovereign_signed: pending
ut_schema: UT_v2.8.0
book_law: v1.5.0
bs_law: v1.5.0
companion_yaml: null  # Plan-Body species ships single-file per Book Law #15

# ── BS LAW Y-JUNCTION ──────────────────────────────────────────────────────
outside:
  heir:
    sovereign_ref: imo-creator
    hub_id: bar-mc-four-brain-wire-plan
    ctb_placement: barton-enterprises/imo-creator/garage/plans/bar-mc-four-brain-wire
    imo_topology: leaf
    cc_layer: CC-01
    services:
      - atlas/constants/MISSION_CONTROL.md
      - atlas/constants/mission-control.yaml
      - atlas/constants/FOUR_BRAIN_AVIATION.md
      - atlas/manifests/four-brain-doctrine-gate.yaml
      - atlas/constants/PLANNER_ROLE.md
      - atlas/constants/UI_STYLE_GUIDE.md
    secrets_provider: doppler
    acceptance_criteria: |
      P=1 conditions enumerated in §3 of body.
  orbt:
    library_state: BUILD
    last_indexed_at: "2026-05-06T00:00:00Z"
    indexed_by: planner-opus-4-7

inside:
  heir:
    artifact_role: plan-book
    bar_id: BAR-MC-FOUR-BRAIN-WIRE
    process_id: PROC-070
    species: Plan-Body
    determinism_gate_passed: true
    aviation_model:
      planner: opus-4-7
      foreman: sonnet
      mechanic: sonnet
      auditor: codex
      rule: mechanic != auditor
  orbt:
    runtime_state: BUILD
    promotion_gate: codex CERTIFY → BAR closes
---

# Plan Book — BAR-MC-FOUR-BRAIN-WIRE

**Wire the Four-Brain pipeline into Mission Control as a live, observation-only `flow` renderer over the existing `imo-creator.mission-control.system.pipeline` slot. G-19 compliant — no mid-pipeline approval gates.**

---

## §1 Atlas Sections Consulted

| Source | Section | Read for |
|---|---|---|
| `atlas/constants/KEY.md` | full | vocabulary (HEIR, ORBT, BAR, BS Law, Book Law, paired-artifact) |
| `atlas/ATLAS.md` | §1 Legend, §4 Map-Building SOP, §4.5 Repair SOP, §6 Governance, §7.3, §7.3a | build SOP, governance, paired-artifact registry |
| `atlas/constants/BS_LAW.md` | v1.5.0 | Y-junction syntactic separation of `outside`/`inside` (this Plan Book conforms in frontmatter) |
| `atlas/constants/BOOK_LAW.md` | v1.5.0, species table, Plan-Body shape | this Plan Book's species + shape |
| `atlas/constants/FOUR_BRAIN_AVIATION.md` | v1.3.0 — Planner Lock, Three Books per BAR, determinism-first gate, Strike System | role locks + determinism gate |
| `atlas/constants/PLANNER_ROLE.md` | v1.1.0 §6b Mission Control Wiring Authority | I am the architect; I declare disposition per artifact |
| `atlas/constants/MISSION_CONTROL.md` | v0.2.0 §2 Geometry, §4.5 System Spokes, §10 Artifact Wiring Protocol | Pipeline Observer slot already exists; G-19 forbids mid-pipeline gates |
| `atlas/constants/mission-control.yaml` | `slots[heir_id=imo-creator.mission-control.system.pipeline]` + `artifact_wiring_protocol` | target slot already declares `render_mode: flow` and `data_source: [mc-proxy.four_brain_run, mc-proxy.four_brain_transition]` |
| `atlas/constants/UI_STYLE_GUIDE.md` | §5.13 `flow` render mode | render contract for the Pipeline Observer view |
| `atlas/manifests/four-brain-doctrine-gate.yaml` | v1.2.0 G01–G12 + W-1..W-7 | gates the Auditor will run against this Plan Book and the Mechanic's output |
| `atlas/manifests/paired-artifacts.yaml` | full | paired-artifact registry; nothing in this BAR is a paired Book at amend time |
| `factory/imo-creator/070-four-brain/PROCESS-UT.md` | full + §11 Out-of-Scope | confirms `four_brain_run` + `four_brain_transition` D1 tables not yet migrated; confirms CLI runner deferred to BAR-FOUR-BRAIN-CLI |

---

## §2 Source-of-Truth Split (preserved from intake)

| Concern | Source of truth | Notes |
|---|---|---|
| Mission Control skeleton (slots + render modes) | `imo-creator-v2/atlas/constants/mission-control.yaml` (sovereign-locked) | Mechanic MUST NOT modify (W-6). Pipeline slot already exists with correct `data_source` and `render_mode: flow` — nothing to amend. |
| Pipeline doctrine | `atlas/constants/FOUR_BRAIN_AVIATION.md` v1.3.0 | Read-only; not touched by this BAR. |
| Audit gates | `atlas/manifests/four-brain-doctrine-gate.yaml` v1.2.0 | Auditor reads; this BAR does not amend. |
| LBB row schema | same file, `lbb_row_schema` block | All four roles in this BAR write LBB rows conforming to this schema. |
| Pipeline runtime telemetry | `mission-control.four_brain_run` + `mission-control.four_brain_transition` D1 tables (TO BE CREATED in this BAR via migration `0019_four_brain_run.sql`) | Tables don't exist yet; Mechanic creates them. Once created, `lbb-log.sh` extension writes one transition row per role transition; the existing pipeline runtime starts populating telemetry on the next BAR run. |
| Mission Control runtime fetch | `mc-proxy` worker (read-only) | Mechanic adds two routes that surface the two D1 tables. Existing mc-proxy worker is the home for these endpoints — slot's `data_source: [mc-proxy.four_brain_run, mc-proxy.four_brain_transition]` already expects this naming. |
| Pipeline Observer view | `mission-control` worker, route reachable from sidebar System Spokes → Pipeline Observer | Implements `render_mode: flow` using the universal Book renderer per `UI_STYLE_GUIDE.md` §5.13. |

**Determinism-first gate:** Every required path is deterministic. D1 SQL migration, REST GET handlers, polling cron, lbb-log.sh shell calls. No LLM on the spine. `flow` render is a pure function of D1 rows. **PASS — proceed.**

---

## §3 P=1 Definition (explicit conditions)

A no-op end-to-end run achieves P=1 when ALL of the following hold:

1. **Migration applied.** D1 migration `0019_four_brain_run.sql` exists in `imo-creator-v2/migrations/`, has been applied to the `mission-control` D1 binding, and the two tables (`four_brain_run`, `four_brain_transition`) exist with the column set declared in §6.
2. **mc-proxy endpoints live.** Two read-only routes exist in the `mc-proxy` worker: `GET /four-brain-run` and `GET /four-brain-transition` (response shape per §6). Each returns `200` with `[]` when no rows exist (graceful empty state — no 404 / no 500).
3. **Pipeline Observer view live.** Mission Control worker exposes the Pipeline Observer route (sidebar entry under System Spokes; HEIR `imo-creator.mission-control.system.pipeline`). View consumes both mc-proxy endpoints, renders `flow` render mode per `UI_STYLE_GUIDE.md` §5.13, shows four lanes (Planner → Foreman → Mechanic → Auditor) with status per stage.
4. **Stage diff drawer.** Clicking any stage opens a read-only diff drawer showing that role's LBB row + Atlas sections consulted + (if Mechanic) `git diff` summary. Observation only — no buttons that mutate state.
5. **Stale-data poll wired.** A-check weekly cron exists (script + cron registry entry). Poll asserts: for every `four_brain_run` with `verdict IS NULL` and `started_at` older than 7 days, emit a squawk to `mission-control.squawks`. Stale runs surface in the Master Error Table slot.
6. **lbb-log.sh dual-write.** `scripts/lbb-log.sh` is extended so that calling it ALSO inserts one row into `four_brain_transition` (deterministic shim — no LLM). The two writes are atomic from the script's perspective: either both succeed or the script exits non-zero. (LBB row remains the system of record; `four_brain_transition` is a Mission-Control-side projection.)
7. **G-19 invariant.** No artifact this BAR ships introduces an approval button, a "wait for sovereign" gate, or any UI control that pauses the pipeline. Auditor explicitly checks the diff for the strings `approve`, `reject`, `gate`, `pause`, `confirm` in any user-facing surface and rejects on hit (exception list: `approve_at` columns / read-only display labels).
8. **All 19 doctrine gates PASS.** G01–G12 + W-1..W-7 from `four-brain-doctrine-gate.yaml` v1.2.0 return P=1.
9. **Exactly 4 LBB rows for this BAR run.** `SELECT COUNT(*) FROM lbb_records WHERE bar_id='BAR-MC-FOUR-BRAIN-WIRE' AND subject_id='processes' == 4` (per G08).
10. **Sovereign-locked files unchanged.** `git diff HEAD -- atlas/constants/MISSION_CONTROL.md atlas/constants/mission-control.yaml atlas/constants/FOUR_BRAIN_AVIATION.md atlas/manifests/four-brain-doctrine-gate.yaml` returns empty. (W-6 + locked-constant invariant.)

---

## §4 Stop Conditions

The Mechanic halts (and emits a strike against the named role) on any of:

| Condition | Strike target | Reason |
|---|---|---|
| Plan Book disposition missing for any artifact created | Planner | `PLAN_BOOK_INCOMPLETE` per MISSION_CONTROL.md §10.2 |
| Attempt to modify `atlas/constants/mission-control.yaml` or `atlas/constants/MISSION_CONTROL.md` | Mechanic | W-6 violation |
| Attempt to add a UI control that pauses / approves / rejects mid-pipeline | Mechanic | G-19 violation |
| Determinism-first violation (LLM on a required path of pipeline rendering) | Mechanic | Determinism gate; redesign required |
| D1 migration fails to apply against staging binding | Mechanic | Halt and emit migration error squawk; do NOT silently retry against prod |
| `lbb-log.sh` extension breaks an existing call site | Mechanic | Backward-compat invariant: existing four-role lbb-log.sh contract must continue to work for any non-Four-Brain caller |
| Pipeline Observer view exceeds 200ms p50 render budget on a 100-run dataset | Mechanic | Performance regression on the operator-visible surface |
| Strike count for this BAR reaches 3 | (none — escalation) | Troubleshoot/Train, not another repair (per FOUR_BRAIN_AVIATION.md §STRIKE SYSTEM) |

---

## §5 Mechanic Dispatch Requirements

### §5.1 Allowed write scope (literal paths)

```
imo-creator-v2/migrations/0019_four_brain_run.sql                    # NEW
imo-creator-v2/workers/mc-proxy/src/routes/four-brain-run.ts         # NEW (or .js)
imo-creator-v2/workers/mc-proxy/src/routes/four-brain-transition.ts  # NEW
imo-creator-v2/workers/mc-proxy/src/index.ts                          # AMEND — register the two new routes
imo-creator-v2/workers/mc-proxy/wrangler.toml                         # AMEND — confirm D1 binding name
imo-creator-v2/workers/mission-control/src/routes/pipeline-observer.tsx        # NEW (or framework equivalent)
imo-creator-v2/workers/mission-control/src/components/flow-renderer.tsx        # NEW
imo-creator-v2/workers/mission-control/src/components/stage-diff-drawer.tsx    # NEW
imo-creator-v2/workers/mission-control/src/sidebar.config.ts                   # AMEND — add Pipeline Observer entry under System Spokes
scripts/four-brain-stale-data-poll.sh                                          # NEW (A-check)
scripts/lbb-log.sh                                                             # AMEND — add dual-write to four_brain_transition
imo-creator-v2/cron/cron_registry.yaml                                         # AMEND — register A-check weekly cron
factory/imo-creator/070-four-brain/garage/inbox/BAR-MC-FOUR-BRAIN-WIRE/MECHANIC-OUTPUT.md   # NEW — Mechanic's own output
```

If the Mechanic discovers a different on-disk worker layout than the assumptions above (e.g. `pipeline-observer/` vs `pipeline-observer.tsx`, framework variant), the Mechanic adapts the **filename within the same directory and same purpose** without expanding scope. Path drift outside these directories = stop and ask.

### §5.2 Forbidden paths (Mechanic must NOT touch)

```
atlas/constants/MISSION_CONTROL.md                  # sovereign-locked skeleton
atlas/constants/mission-control.yaml                # sovereign-locked skeleton (W-6)
atlas/constants/FOUR_BRAIN_AVIATION.md              # 16th locked constant
atlas/manifests/four-brain-doctrine-gate.yaml       # gate spec — sovereign + Codex amend only
atlas/manifests/paired-artifacts.yaml               # nothing in this BAR is a paired Book
atlas/constants/PLANNER_ROLE.md                     # already amended in BAR-MISSION-CONTROL-WIRING
atlas/constants/MECHANIC_ROLE.md                    # same
atlas/constants/AUDITOR_ROLE.md                     # same
atlas/constants/UI_STYLE_GUIDE.md                   # render-mode catalog locked
factory/imo-creator/070-four-brain/PROCESS-UT.md    # PROC-070 doctrine — out of scope for this BAR
```

### §5.3 Literal work orders (Foreman dispatches as `file:line | old_string | new_string` triples)

Per `feedback_work_packet_literal_pairs.md` doctrine, Foreman emits literal pairs only — no "find pattern X" rules. The Mechanic receives:

1. **D1 migration** — full file content from §6 below; commit as new file at the literal path.
2. **mc-proxy route registration** — Foreman cuts a triple inserting two `import` + two `app.get(...)` lines into `imo-creator-v2/workers/mc-proxy/src/index.ts`. Exact triple emitted at dispatch time once Foreman reads current index.ts.
3. **Sidebar config amendment** — single literal triple inserting one entry into the System Spokes array in `sidebar.config.ts`. Exact triple emitted at dispatch.
4. **lbb-log.sh extension** — Foreman emits the literal patch adding the dual-write block guarded by `[[ -n "$BAR_ID" ]]` (no-op for non-BAR callers).
5. **cron_registry.yaml entry** — Foreman emits the literal triple appending the A-check weekly entry: `cron: "0 14 * * 1"  # Mondays 14:00 UTC, after the existing drift-sweep`.
6. **Per-artifact LBB log call** — Mechanic invokes `scripts/lbb-log.sh --role mechanic --action build_complete --bar-id BAR-MC-FOUR-BRAIN-WIRE --subject processes --atlas-sections "§1,§4,§4.5,§6,§7.3,§7.3a"` after final commit, before handoff to Auditor.

### §5.4 Run conditions

- Sonnet via Agent tool, `run_in_background=true` (per `feedback_run_sonnet_in_background.md`).
- Mechanic reads Atlas §4 (build) before first edit.
- Mechanic reads this Plan Book §3 P=1 conditions before first edit.
- Mechanic reads spoke frontmatter on every file it modifies.
- After all edits: `git diff HEAD -- <forbidden paths from §5.2>` MUST return empty before commit. If non-empty → revert and emit strike.

---

## §6 D1 Schema (canonical for Mechanic + Auditor)

Migration `imo-creator-v2/migrations/0019_four_brain_run.sql` creates exactly these tables:

```sql
-- Per-BAR pipeline run
CREATE TABLE IF NOT EXISTS four_brain_run (
  run_id            TEXT PRIMARY KEY,            -- UUIDv4
  bar_id            TEXT NOT NULL,
  process_id        TEXT NOT NULL DEFAULT 'four-brain',
  runtime_state     TEXT NOT NULL,               -- BUILD|OPERATE|REPAIR|TROUBLESHOOT_TRAIN|DISABLED
  verdict           TEXT,                        -- PASS|FAIL|NULL (open)
  strikes           INTEGER NOT NULL DEFAULT 0,
  started_at        TEXT NOT NULL,               -- ISO8601 UTC
  last_completed_at TEXT,
  created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE INDEX IF NOT EXISTS ix_four_brain_run_bar_id ON four_brain_run(bar_id);
CREATE INDEX IF NOT EXISTS ix_four_brain_run_started_at ON four_brain_run(started_at);

-- Per-role transition within a run
CREATE TABLE IF NOT EXISTS four_brain_transition (
  transition_id              TEXT PRIMARY KEY,   -- UUIDv4
  run_id                     TEXT NOT NULL,
  bar_id                     TEXT NOT NULL,
  role                       TEXT NOT NULL,      -- planner|foreman|mechanic|auditor
  action                     TEXT NOT NULL,      -- e.g. plan_complete, dispatch_complete, build_complete, audit_complete
  atlas_sections_consulted   TEXT NOT NULL,      -- comma-separated
  evidence_hash              TEXT,               -- 64-hex SHA256 (nullable for foreman/planner)
  gate_verdicts              TEXT,               -- JSON; non-null only on auditor row
  notes                      TEXT NOT NULL DEFAULT '',
  timestamp                  TEXT NOT NULL,      -- ISO8601 UTC
  FOREIGN KEY (run_id) REFERENCES four_brain_run(run_id)
);
CREATE INDEX IF NOT EXISTS ix_four_brain_transition_run_id ON four_brain_transition(run_id);
CREATE INDEX IF NOT EXISTS ix_four_brain_transition_bar_id ON four_brain_transition(bar_id);
```

mc-proxy endpoints return:
- `GET /four-brain-run?bar_id=...&limit=50` → `{ rows: four_brain_run[] }`
- `GET /four-brain-transition?run_id=...` → `{ rows: four_brain_transition[] }` (sorted by `timestamp` ASC)

Both endpoints: read-only, no auth beyond the existing mc-proxy auth, return `[]` when empty, never 404 on a syntactically valid query.

---

## §7 Auditor Packet Requirements

Auditor (Codex, different inference engine than Sonnet) walks all gates from `atlas/manifests/four-brain-doctrine-gate.yaml` v1.2.0:

### §7.1 Gates that apply

| Gate | What Auditor verifies for this BAR |
|---|---|
| G01 | This Plan Book's frontmatter Y-junction parses (outside + inside as distinct top-level constructs, both with nested heir + orbt) |
| G02 | `outside.heir` 8-field completeness on this Plan Book |
| G03 | `outside.orbt.library_state` ∈ enum |
| G04 | `inside.heir` + `inside.orbt` populated |
| G05 | `lbb_row_schema` referenced (this BAR uses the canonical schema; no local override) |
| G06 | All 4 LBB rows for this BAR carry non-empty `atlas_sections_consulted` |
| G07 | Auditor uses `four-brain-doctrine-gate.yaml` as gate spec source (no inline predicates) |
| G08 | `COUNT(lbb_records WHERE bar_id='BAR-MC-FOUR-BRAIN-WIRE') == 4` |
| G09 | All 4 LBB rows pass schema validation (12 fields each, regex/enum) |
| G10 | CI gate active and unmodified by this BAR |
| G11 | Parity SHA256 — N/A (this Plan Book has no companion .yaml; Plan-Body is single-file) — Auditor records `gate=G11 verdict=N/A reason=plan-body-single-file` |
| G12 | Drift sweep workflow unchanged |
| **W-1** | Every produced/modified artifact has a HEIR ID (or for non-spine code files, a frontmatter stub identifying its repo + path; Auditor accepts the convention used by sibling worker code) |
| **W-2** | Plan Book §8 below contains the `mission_control_wiring` section listing every produced/modified artifact with disposition |
| **W-3** | For the WIRE artifact: target slot's `data_source` references the `mc-proxy.four_brain_run` + `mc-proxy.four_brain_transition` paths the Mechanic actually built. (Already true in locked skeleton.) |
| **W-4** | No paired Books in this BAR — `paired-artifacts.yaml` unchanged. Auditor records N/A. |
| **W-5** | LBB transition row tagged `mission-control-wiring` exists for the WIRE artifact (Mechanic emits at execution) |
| **W-6** | `git diff HEAD -- atlas/constants/MISSION_CONTROL.md atlas/constants/mission-control.yaml` returns empty |
| **W-7** | Disposition sanity — Auditor reads §8 below and asks "would the sovereign reasonably want this artifact surfaced?" for each EXEMPT |

### §7.2 BAR-specific predicates Auditor adds

In addition to the doctrine gates, Auditor verifies:

| Predicate | Source |
|---|---|
| `0019_four_brain_run.sql` is idempotent (`CREATE TABLE IF NOT EXISTS`) | §6 |
| Pipeline Observer route returns 200 when D1 is empty | §3.2 |
| Stage diff drawer contains zero strings matching `/\b(approve|reject|pause|confirm)\b/i` outside of read-only display labels and column names | §3.7 |
| `scripts/lbb-log.sh` non-BAR call sites still pass their own existing tests (Mechanic preserves backward compat) | §4 stop condition |
| Cron entry uses `0 14 * * 1` (Monday 14:00 UTC) | §5.3 |

### §7.3 Verdict format

Per `four-brain-doctrine-gate.yaml#emit_verdict`. Auditor produces an Audit Book at `factory/imo-creator/070-four-brain/garage/inbox/BAR-MC-FOUR-BRAIN-WIRE/AUDIT-BOOK.md` (Audit-Body species, BS Law conformant). On PASS, Auditor writes one CERTIFY row to `lbb.logbook` and one final LBB row to `lbb.records`.

---

## §8 Mission Control Wiring

Per MISSION_CONTROL.md §10 + PLANNER_ROLE.md §6b. Default disposition is **none** — every artifact gets an explicit call.

```yaml
mission_control_wiring:
  # ── 1. The Pipeline Observer view itself — the operator-visible artifact
  - artifact: imo-creator-v2/workers/mission-control/src/routes/pipeline-observer.tsx
    disposition: WIRE
    target_slot_heir_id: imo-creator.mission-control.system.pipeline
    rationale: |
      Slot already exists in the locked skeleton with render_mode: flow and
      data_source: [mc-proxy.four_brain_run, mc-proxy.four_brain_transition].
      This Mechanic build fulfills that contract; no skeleton edit needed.
      The WIRE disposition is the explicit declaration that this artifact
      satisfies the slot's existing data_source contract.

  - artifact: imo-creator-v2/workers/mission-control/src/components/flow-renderer.tsx
    disposition: EXEMPT
    rationale: |
      Internal renderer primitive consumed by pipeline-observer.tsx (and any
      future flow-mode slot). No standalone operator surface; addressed via
      its parent slot.

  - artifact: imo-creator-v2/workers/mission-control/src/components/stage-diff-drawer.tsx
    disposition: EXEMPT
    rationale: |
      Internal drawer component opened from inside the pipeline-observer view.
      Not a standalone slot — it is fill within an existing slot.

  - artifact: imo-creator-v2/workers/mission-control/src/sidebar.config.ts
    disposition: EXEMPT
    rationale: |
      Sidebar config file. The sidebar slot itself
      (imo-creator.mission-control.shell.sidebar) is wired in the locked
      skeleton; this file is its fill, not a slot.

  # ── 2. Backend / infra fulfilling the slot's data_source contract
  - artifact: imo-creator-v2/migrations/0019_four_brain_run.sql
    disposition: EXEMPT
    rationale: |
      Pure D1 schema migration. Consumed by mc-proxy endpoints; no
      operator-visible surface. Defensible exempt — sovereign navigates the
      data through the Pipeline Observer slot, not through the migration file.

  - artifact: imo-creator-v2/workers/mc-proxy/src/routes/four-brain-run.ts
    disposition: EXEMPT
    rationale: |
      Read-only HTTP route on mc-proxy worker. The slot's data_source
      'mc-proxy.four_brain_run' already declares this dependency; the route
      is fill, not a slot.

  - artifact: imo-creator-v2/workers/mc-proxy/src/routes/four-brain-transition.ts
    disposition: EXEMPT
    rationale: same as four-brain-run.ts

  - artifact: imo-creator-v2/workers/mc-proxy/src/index.ts
    disposition: EXEMPT
    rationale: Worker entry; tooling-only.

  - artifact: imo-creator-v2/workers/mc-proxy/wrangler.toml
    disposition: EXEMPT
    rationale: Cloudflare worker config; never operator-navigated.

  # ── 3. Cron / instrumentation
  - artifact: scripts/four-brain-stale-data-poll.sh
    disposition: EXEMPT
    rationale: |
      A-check weekly cron script. Its outputs land in mission-control.squawks
      and surface via the existing Master Error Table slot
      (imo-creator.mission-control.system.errors). The script itself has no
      operator-visible state.

  - artifact: scripts/lbb-log.sh
    disposition: EXEMPT
    rationale: |
      Existing instrumentation script; this BAR amends it for dual-write into
      four_brain_transition. Not a standalone slot — its outputs reach
      Mission Control via the Pipeline Observer slot's data_source.

  - artifact: imo-creator-v2/cron/cron_registry.yaml
    disposition: EXEMPT
    rationale: |
      Cron registry config. Operator-visible cron health surfaces via the
      Pressure Gauge signal (already wired); the registry file is fill.

  # ── 4. This Plan Book itself
  - artifact: docs/plans/BAR-MC-FOUR-BRAIN-WIRE/PLAN-BOOK.md
    disposition: NEW_SLOT_NEEDED
    proposed_slot:
      heir_id: imo-creator.mission-control.system.plans
      ctb_position: barton-enterprises/system/plans
      render_mode: block-stream
      data_source: docs/plans/**/PLAN-BOOK.md
    rationale: |
      No existing slot covers Plan Books. Per MISSION_CONTROL.md §10.1
      (which uses this exact example), the correct disposition is
      NEW_SLOT_NEEDED. Sovereign reads at Auditor verdict and either fires
      a follow-up sovereign BAR to amend the skeleton, or accepts the
      unwired state with an exemption. Mechanic does NOT auto-create the
      slot (W-6); Mechanic carries the proposal forward in
      MECHANIC-OUTPUT.md per §10.2.

  # ── 5. Mechanic's own output (created by Mechanic at end of build)
  - artifact: factory/imo-creator/070-four-brain/garage/inbox/BAR-MC-FOUR-BRAIN-WIRE/MECHANIC-OUTPUT.md
    disposition: EXEMPT
    rationale: |
      Garage-internal Mechanic handoff document for this BAR; ephemeral
      across the Garage inbox, not a Library-shelved artifact.

  # ── 6. Auditor's own output (created by Auditor on verdict)
  - artifact: factory/imo-creator/070-four-brain/garage/inbox/BAR-MC-FOUR-BRAIN-WIRE/AUDIT-BOOK.md
    disposition: EXEMPT
    rationale: |
      Audit-Body species artifact for this BAR. Audit Books shelve into LBB
      under subject_id='processes' on PASS — the LBB Browser slot
      (imo-creator.mission-control.system.lbb) already surfaces all LBB
      records, so Audit Books are reachable through the LBB slot's existing
      fractal expansion. No standalone slot needed.
```

---

## §9 LBB Row Schema Fields (Mechanic + Auditor MUST write)

Per `four-brain-doctrine-gate.yaml#lbb_row_schema` v1.2.0. Each of the 4 roles (Planner, Foreman, Mechanic, Auditor) writes exactly one row to `lbb_records` for this BAR. Every row carries:

| Field | Source / Value for this BAR |
|---|---|
| `record_id` | `uuidgen` (UUIDv4) |
| `bar_id` | `BAR-MC-FOUR-BRAIN-WIRE` |
| `role` | `planner` / `foreman` / `mechanic` / `auditor` |
| `action` | `plan_complete` / `dispatch_complete` / `build_complete` / `audit_complete` |
| `evidence_hash` | SHA256 of role's primary artifact (Plan Book / dispatch packet / git tree / Audit Book) |
| `atlas_sections_consulted` | Planner: §1,§4,§4.5,§6,§7.3,§7.3a · Foreman: paired-artifacts.yaml + this Plan Book · Mechanic: §4,§4.5 + this Plan Book + UI_STYLE_GUIDE §5.13 · Auditor: four-brain-doctrine-gate.yaml v1.2.0 |
| `timestamp` | ISO8601 UTC at write time |
| `sovereign_ref` | `imo-creator` |
| `subject_id` | `processes` |
| `orbt_mode` | `BUILD` |
| `gate_verdicts` | NULL for planner/foreman/mechanic; JSON map of G01-G12 + W-1..W-7 verdicts for auditor |
| `notes` | Mechanic appends `mission-control-wiring` tag for the Pipeline Observer artifact (W-5); Auditor appends final-verdict summary string |

In addition, per §3.6, `lbb-log.sh` dual-writes one row per role transition into `four_brain_transition` (Mission-Control-side projection, NOT a substitute for the LBB row).

---

## §10 Open Blockers (TRUE blockers only — runtime-resolvable items omitted)

**None.** All §3 P=1 conditions are achievable with the §5.1 allowed write scope. The known runtime concerns below are NOT blockers — they're handled in the build:

- *D1 tables don't exist yet* → Mechanic creates via migration `0019_four_brain_run.sql` in §5.1. Resolved at build.
- *No live BAR runs yet to populate telemetry* → Endpoints return `[]`; view shows empty state gracefully. First real population happens on the next BAR that calls the extended `lbb-log.sh`. Resolved at first downstream run.
- *PROC-070 §11 says CLI runner is out-of-scope* → Confirmed; this BAR does not require the CLI runner. Pipeline runtime instruments via `lbb-log.sh` extension instead. Compatible with future BAR-FOUR-BRAIN-CLI which can replace the shim.
- *Pipeline Observer view will show empty until a real Four-Brain BAR runs through with the extended lbb-log.sh* → Acceptable empty state; intake explicitly accepts observation-only and the A-check stale-data poll will surface absence as a squawk.

---

## §11 Document Control

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Created | 2026-05-06 |
| Last Modified | 2026-05-06 |
| Status | SIGNED_PENDING_DISPATCH (sovereign signs at Foreman handoff) |
| Authority | Planner (Opus 4.7 collaborative) — sovereign signs to dispatch |
| Determinism Gate | PASS — no LLM on the spine of any required path |
| BS Law Y-junction | Conformant (frontmatter `outside` + `inside` as distinct top-level constructs with nested heir + orbt) |
| Book Law Species | Plan-Body (single-file, 11-block shape) |
| Mechanic Engine | Sonnet (Agent tool, run_in_background=true) |
| Auditor Engine | Codex (codex-dop exec) — different engine than Mechanic (Aviation Model invariant) |
| Strike Ladder | Strike 1: Sonnet repair · Strike 2: Opus 4.7 mechanic · Strike 3: Troubleshoot/Train (NOT another repair) |

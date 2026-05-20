# PROCESS-UT — Process 2310 Kiddos Sports-Performance
# Status: BUILD | Medium: database | Business: personal (Kiddos App)
# Process number 2310 is TENTATIVE — sovereign-assigned via pending-atlas-updates/BAR-KIDDOS-SPORTS-PERFORMANCE.yaml

## UT Pre-Flight Checklist (per `atlas/constants/UT_CHECKLIST.md` v1.3.1)

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §1 |
| 2 | OSAM — READ / WRITE / Process Composition / Join Chain / Forbidden / Query Routing | ☑ | §5, §6 |
| 3 | Component Status — every dep 🟢 / 🟡 / 🔴 with 1-line state | ☑ | §3 |
| 4 | Owner — human who fixes this at 2 AM | ☑ | §2 (Dave Barton) |
| 5 | Live Dashboard — URL or explicit "N/A" | ☑ | §3 — N/A (BUILD; first dashboard wires after first kid populated) |
| 6 | Kill Switch — exact command to stop the process | ☑ | §8 |
| 7 | Logbook — last audit verdict + date (after certification only) | ☐ | §12 — N/A during BUILD |
| 8 | FCEs Attached — which FCE runs structurally back this doc | ☑ | §3c |
| 9 | BARs Referenced — every BAR this doc touches, with status | ☑ | §3d |
| 10 | LBB Subjects Fed — which LBB subject(s) this doc's session logs go to | ☑ | §3e |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | ☑ | §1b |
| 12 | Live Verification — counts/crons/URLs/BAR statuses grounded against the system | ☐ | §9b — N/A in BUILD; verified at first apply |
| 13 | ctb_node — declared path on the Barton Enterprises CTB trunk | ☑ | §1 — `barton-enterprises/personal/kiddos/sports/performance` |

---

## §1 PRD

### Identity (HEIR — 8 fields)

| Field | Value |
|-------|-------|
| sovereign_ref | imo-creator |
| hub_id | kiddos-sports-performance |
| ctb_placement | barton-enterprises/personal/kiddos/sports/performance |
| imo_topology | middle |
| cc_layer | CC-03 |
| services | Cloudflare D1 (`kiddos` db `5a57021b-1a6f-48ea-83a0-2e730d0fe674`); Airtable (canonical `measurement` front — pending) |
| secrets_provider | Doppler → `imo-creator/dev` (CF_FULL_API_TOKEN, GLOBAL_CLOUDFLARE_ACCOUNT_ID); Airtable PAT TBD |
| acceptance_criteria | `v_recruiting_gate` + `v_composite_score` + `v_prescription` return sane values for one seeded child on one sport; CQRS error pairs reject malformed input; every column registered in §7 with description/format/unique-id |
| species | UT-Body (database medium) |

### §1b Geometry

| Field | Value |
|-------|-------|
| ctb_node | `barton-enterprises/personal/kiddos/sports/performance` |
| altitude | 10K (leaf-cluster; one sub-engine inside the Sports silo of the Kiddos App) |
| hub_spoke_role | HUB — the Sports-Performance hub. Spokes: per-sport adapters (wrestling/volleyball/softball), each kid's `sport_participation` row, the measurement/result stores. Rim: data-in (Airtable + future MatBoss/sensor feeds) + data-out (the recruiting score, gate, leverage, prescription views) |
| parent_silo | Kiddos App (Personal branch); child sovereign is `children.id` (NOT a new athlete identity — doctrine) |

### What

A measurement-driven recruiting + training engine for Tyler, Mallory, and any future Barton child across any sport they play. Stores tested athletic metrics and competition outcomes long-format (one engine, sport = data — wrestling/volleyball/softball already seeded; sport #4 is a data insert, never a migration), normalizes them against published division/position thresholds, computes composite recruiting scores (0–100), identifies the highest-leverage weakness per athlete (FCE-shaped: weight × gap-to-elite × trainability), and prescribes targeted training with projected score gain. Multi-kid, multi-sport, hierarchical composites (wrestling 40/30/20/10), input-stream-agnostic (future generalization to one canonical `measurement` table absorbs nutrition + recovery + sleep + supplements + bodyweight without migration — pending sovereign confirm).

### Why

Replaces eye-test / generic-conditioning with measurable, comparable, sortable, trendable, recruitable data. Every workout becomes targeted optimization against a specific weak high-weight metric; every retest closes the loop and tightens the system's own correlation hypotheses from data (sigma tightens with use). The actual analytics leverage in wrestling specifically — where nobody systematically tracks grip endurance, re-attack speed, live-go degradation, scramble efficiency — is the gap this fills first.

### Who

Operator: Dave Barton (sovereign). Subjects: Tyler (wrestling — seeded), Mallory (volleyball + softball — pending participation rows), any future child. Consumers: parent dashboard (Mission Control / Kiddos portal — pending), college-recruiting packets (graduation outputs).

### Scope

In: athletic-metric long store + recruiting-model reference + composite scoring + gate + leverage + prescription + competition results (event + stat) + CQRS error pairs for every canonical that accepts external input. Three sports seeded (wrestling/volleyball/softball). Schema catalog (§7) — every column AI + human ready.

Out of scope (this UT): the Airtable canonical-front design (separate BAR); the 001 kiddos foundation (`children`/`parents`/`family_links` — port from `archive/v1/migrations/001_d1_foundation.sql`, prerequisite); the Workout/Nutrition/Recovery input streams (pending sovereign A/B decision on generalized `measurement` table vs per-category tables); the parent dashboard UI; the live MatBoss / Rapsodo / Blast / HitTrax / Vertec sensor feeds (defined as `metric_test.source` enum, integration deferred).

### Success metric

`v_recruiting_gate` returns correct ABOVE/AT/BELOW for ≥1 seeded child × ≥1 sport against published thresholds; `v_composite_score` returns 0–100 for the same; `v_prescription` returns at least one (weak_metric → exercise → projected_gain) row; CQRS error tables reject ≥1 deliberately malformed insert without losing the payload.

---

## §2 OWNER

Dave Barton (sovereign). 2 AM fix: doctrine via this UT; data via Airtable (once wired); D1 via `wrangler d1 execute --remote --database=kiddos --file=...`. No service binding to other workers yet.

---

## §3 COMPONENT STATUS

### Dependencies

| Dependency | Type | What It Provides | Status |
|-----------|------|-----------------|--------|
| `children` / `parents` / `family_links` (kiddos foundation) | upstream table | child sovereign; sport_participation FKs `children.id` | 🟡 **prerequisite missing** — exists only in `kiddo-app-skeleton/archive/v1/migrations/001_d1_foundation.sql`; must be ported to v2 as `001_kiddos_foundation.sql` and applied BEFORE this migration |
| Cloudflare D1 — `kiddos` db | substrate | persistent store for engine + spine + error pairs | 🟢 exists (uuid `5a57021b-1a6f-48ea-83a0-2e730d0fe674`, 0 tables, empty) |
| `CF_FULL_API_TOKEN` (Doppler `imo-creator/dev`) | secret | wrangler d1 auth | 🟢 verified active (token-verify 200, scope sufficient for d1 list / execute) |
| Airtable canonical `measurement` base | substrate | operator-facing data entry (pending) | 🔴 not yet designed |
| MatBoss / Rapsodo / Blast / HitTrax / Vertec | external feeds | sensor-source measurements | 🔴 integration deferred |
| `atlas/constants/BARTON_ENTERPRISES_CTB.md` (#12 locked) | doctrine | CTB trunk this attaches to | 🟢 |
| `atlas/DATABASE_FILL_INSTRUCTIONS.md` | doctrine | this UT's parent fill spec | 🟢 |

### §3c FCEs Attached

| FCE | Why it backs this | Status |
|-----|-------------------|--------|
| Sports-Performance Intelligence (parent FCE, future) | Valuation = weight × gap-to-elite per metric · Concentration = where the weight is (composite weights) · Trend = retest deltas · Liquidity = `correlation_strength` (can training move it). Allocates scarce training time to highest-leverage metric. | DEFERRED — runs after enough longitudinal data exists to compute real correlation strengths (current values are in-house hypotheses) |

### §3d BARs Referenced

| BAR | Status | Why |
|-----|--------|-----|
| `BAR-436` (Two-layer cockpit + sealed engines) | Backlog | This UT is a concrete fill of the two-layer architecture — Kiddos App (operating cockpit) calling a sub-engine (this) |
| `BAR-KIDDOS-SPORTS-PERFORMANCE` (pending-atlas-updates) | PENDING-SOVEREIGN | Proposes process number 2310 + CTB layer-registry additions |
| `BAR-433` (Obsidian Windows) | Done | Vault setup that made `_inbox/` Atlas-attached the inbox surface |

### §3e LBB Subjects Fed

| Subject | What lands there |
|---------|------------------|
| `system` | Session logs on this UT (build/repair/audit transitions) |
| `processes` | Per-run transitions when the system processes a kid's measurement batch / generates a prescription |

---

## §4 IMO

### Input

- **Measurements** — combine tests (`metric_test` long store): exit velocity, vertical jump, deadlift/BW, pop time, etc. Per (child, sport_participation, metric, test_date, value, source).
- **Competition results** — events (`competition_event`) + per-event/per-match stats (`competition_stat`): placements (Fargo/state/dual), takedown%, win%, ride time, batting avg, hitting%, etc.
- **Reference model** (kid-independent, seeded once per sport): metrics + division/position thresholds + composite weights + training correlations + exercises.
- **Triggers**: a coach/parent/Dave enters a new measurement OR a competition result lands (manual or feed).

### Middle

For each measurement insert: validate against `recruiting_metric.canonical_unit`/range → CANONICAL or CQRS error pair. The views then continuously compute:
1. **Gate** — latest value per (participation, metric) vs threshold band for (sport, position, division) → ABOVE / AT / BELOW. Phase-1 recruiting cut, deterministic.
2. **Composite score** — `Σ(normalized_metric × weight) × 100` (0–100), normalize = `(actual−baseline)/(elite−baseline)` direction-aware (lower-better flips), clamped 0..1. Hierarchical composites (wrestling parent + 4 nested layer-models) resolve in app layer (SQLite views can't recurse — documented honestly).
3. **Leverage / weakness** — `weight × (1 − normalized_score)` per metric. High weight + low score = the metric where training gains the most score. FCE valuation.
4. **Prescription** — weak metrics joined to `training_correlation` → exercise + projected score gain = `leverage × correlation_strength × 100`. NULL correlation strengths use a hypothesis-0.5 placeholder; every retest cycle replaces hypothesis with measured truth (the loop discovers its own correlations).

### Output

- **Phase-1 gate verdicts** per athlete (which divisions they currently qualify for, per metric).
- **Recruiting score 0–100** per (athlete, composite_model) — multiple lenses per kid (e.g., volleyball: AVCA-VPI-published-style + position-weighted-hypothesis).
- **Targeted training prescription**, ranked by projected score gain.
- **Trend over time** per metric per athlete (`v_metric_trend`).
- **CQRS error queue** (`v_open_errors`) — rejected payloads awaiting fix-and-promote.

### Circle

`Test → Score → Weakness ID → Prescription → Retest → Score Δ` — every retest tightens the system's correlation hypotheses against measured score deltas. Sigma tightens with data accumulation.

---

## §5 CONTRACT (CQRS, sovereign silo, join chain to spine)

### READ access

| Source | What |
|--------|------|
| `children` (foundation) | child sovereign for sport_participation FK |
| `sport`, `recruiting_metric`, `recruiting_threshold`, `composite_model`, `composite_component`, `exercise`, `training_correlation` | per-sport reference model (built once per sport; kid-independent) |
| `sport_participation`, `metric_test`, `competition_event`, `competition_stat` | kid-owned spine (long stores) |
| views | derived only — never stored as truth |

### WRITE access

| Target | What | When |
|--------|------|------|
| canonical tables | new measurement / event / stat / participation rows | data entry (Airtable, feed, manual) — VIA validation layer; bad rows go to error pairs |
| `*_error` pairs | rejected payloads + reason + raw_payload | on validation failure |
| seed tables | per-sport reference fill | once per sport, sovereign-curated |

### Spine key

`children.id` (the kiddos sovereign). `sport_participation_id` chains to it; everything else chains through `sport_participation_id`.

### Join chain to spine

```
children.id
  └─ sport_participation.child_id
       ├─ metric_test.participation_id
       ├─ competition_event.participation_id
       │     └─ competition_stat.event_id
       └─ competition_stat.participation_id
```

### Forbidden paths

| Action | Why |
|--------|-----|
| Direct INSERT into canonical tables bypassing validation | Violates CQRS — data must enter from leaves through the validator |
| Skipping CQRS error pair | Every canonical needs its error sibling; silent drops are doctrine violations |
| Cross-silo joins (e.g., kiddos → SVG outreach) | Sovereign silo rule — Personal silo is bounded |
| Creating a parallel athlete identity | Child = sovereign via `children.id`; an athlete is never its own identity, only a sport_participation row off a child |
| Per-sport wide tables / per-input-category tables | Wide is brittle; long absorbs new sports + new input streams as data, not migration |

### CQRS pairs

| Canonical | Error |
|-----------|-------|
| `sport_participation` | `sport_participation_error` |
| `metric_test` | `metric_test_error` |
| `competition_event` | `competition_event_error` |
| `competition_stat` | `competition_stat_error` |

---

## §6 JOIN CONTRACT (the FK graph)

```
                 children.id (foundation — 001 prereq)
                       │
                       ▼
        ┌──────  sport_participation  ──────┐
        │            (sport_id ─► sport)    │
        ▼                                    ▼
   metric_test ──► recruiting_metric    competition_event ──► competition_stat
        │              │                     │                       │
        │              ▼                     │                       ▼
        │     recruiting_threshold           │              (production stats; long)
        │              ▲                     │
        ▼              │                     ▼
   v_metric_normalized ┘            (event_weight × placement → competition_layer, app-resolved)
        │
        ▼
   v_composite_score ── reads composite_model + composite_component (which may nest)
        │
        ▼
   v_metric_leverage ──► v_prescription ──► training_correlation ──► exercise
```

---

## §7 SCHEMA — column catalog (every column, AI + human ready)

Each row: a unique catalog ID (`table.column`), human/AI description, semantic format (beyond DDL type), data type, PK/FK marker. This is the single source of truth for what every column means; the SQL DDL is its execution form.

### ENGINE tables (constant — kid-independent reference, built once per sport)

| catalog_id | description | format | type | role |
|---|---|---|---|---|
| `sport.sport_id` | Sport slug, primary key | lowercase slug (`wrestling`\|`volleyball`\|`softball`) | TEXT | PK |
| `sport.name` | Display name | Title Case | TEXT | |
| `sport.created_at` | Row created | ISO datetime UTC | TEXT | |
| `recruiting_metric.metric_id` | Metric slug, PK | lowercase prefixed slug (`sb_exit_velocity`, `wr_grip_endurance`) | TEXT | PK |
| `recruiting_metric.sport_id` | Which sport this metric belongs to | sport slug | TEXT | FK→sport |
| `recruiting_metric.position` | Position restriction (NULL = applies to all) | sport-specific slug (`OF`, `catcher`, `middle_blocker`, `setter`, `libero`, `pitcher`, `position_player`) | TEXT | |
| `recruiting_metric.metric_name` | Display name | Sentence case | TEXT | |
| `recruiting_metric.canonical_unit` | Storage unit for all values | enum: `in`\|`sec`\|`mph`\|`lb`\|`ms`\|`ratio`\|`rpm`\|`pct`\|`bpm`\|`count`\|`score` | TEXT | |
| `recruiting_metric.direction` | Which way is better | enum: `higher_better`\|`lower_better` | TEXT | |
| `recruiting_metric.source_type` | How the value originates | enum: `combine`\|`production`\|`sensor`\|`composite` | TEXT | |
| `recruiting_metric.measurement_method` | Instrument/protocol | free text (e.g., `Radar/HitTrax/Rapsodo`, `Vertec`, `Timing gates`, `Dynamometer`) | TEXT | |
| `recruiting_metric.why_it_matters` | Recruiting rationale | one-liner sentence | TEXT | |
| `recruiting_metric.created_at` | Row created | ISO datetime UTC | TEXT | |
| `recruiting_threshold.threshold_id` | Threshold row PK | slug (`t_sb_ev_d1`) | TEXT | PK |
| `recruiting_threshold.metric_id` | Which metric this threshold is for | metric slug | TEXT | FK→recruiting_metric |
| `recruiting_threshold.position` | Position override (NULL = inherit) | position slug | TEXT | |
| `recruiting_threshold.division` | Recruiting division | enum: `D1`\|`D2`\|`D3`\|`developmental` | TEXT | |
| `recruiting_threshold.band_low` | BASELINE — minimum to qualify (canonical unit) | REAL in metric's canonical unit; for lower_better this is the slowest-still-qualifying | REAL | |
| `recruiting_threshold.band_high` | ELITE anchor (canonical unit) | REAL in metric's canonical unit; for lower_better this is the elite/fast end | REAL | |
| `recruiting_threshold.band_display` | Human-readable band | string (`"9'10\"–10'4\"+"`, `"1.7–1.9 sec"`) | TEXT | |
| `recruiting_threshold.citation` | Source attribution | free text (`NCSA-class`, `AVCA-VPI`, `HYPO: tune`) | TEXT | |
| `recruiting_threshold.created_at` | Row created | ISO datetime UTC | TEXT | |
| `composite_model.model_id` | Composite model slug, PK | slug (`sb_of_index`, `wr_projection`, `vb_vpi_official`) | TEXT | PK |
| `composite_model.sport_id` | Which sport | sport slug | TEXT | FK→sport |
| `composite_model.position` | Position (NULL = all) | position slug | TEXT | |
| `composite_model.name` | Display name | Title Case | TEXT | |
| `composite_model.source` | Where the formula came from | enum: `published`\|`hypothesis`\|`discovered` | TEXT | |
| `composite_model.normalize` | Pre-weighting normalization method | enum: `none`\|`minmax_baseline_elite`\|`percentile` | TEXT | |
| `composite_model.score_vs_division` | Which division's band to normalize against | enum: `D1`\|`D2`\|`D3`\|`developmental` | TEXT | |
| `composite_model.citation` | Source attribution | free text | TEXT | |
| `composite_model.notes` | Caveats / blockers | free text (e.g., `norms_required: percentile-of-one undefined`) | TEXT | |
| `composite_model.created_at` | Row created | ISO datetime UTC | TEXT | |
| `composite_component.component_id` | PK | slug | TEXT | PK |
| `composite_component.model_id` | Parent composite | model slug | TEXT | FK→composite_model |
| `composite_component.metric_id` | Component is a raw metric (XOR with nested_model_id) | metric slug \| NULL | TEXT | FK→recruiting_metric |
| `composite_component.nested_model_id` | Component is a nested composite (Blast→SRI, wr layers) | model slug \| NULL | TEXT | FK→composite_model |
| `composite_component.weight` | Weight in the parent composite | REAL 0..1; weights within a model SHOULD sum to 1.0 | REAL | |
| `composite_component.created_at` | Row created | ISO datetime UTC | TEXT | |
| `exercise.exercise_id` | Exercise slug, PK | slug (`ex_rot_medball`, `ex_hang_protocol`) | TEXT | PK |
| `exercise.name` | Display name | Sentence case | TEXT | |
| `exercise.category` | Training category | enum: `plyometric`\|`olympic_lift`\|`rotational`\|`reactive`\|`grip_endurance`\|`work_capacity`\|`acceptance`\|`acceleration`\|`arm_speed` (extensible) | TEXT | |
| `exercise.created_at` | Row created | ISO datetime UTC | TEXT | |
| `training_correlation.correlation_id` | PK | slug (`tc_sb_ev_mb`) | TEXT | PK |
| `training_correlation.sport_id` | Sport | sport slug | TEXT | FK→sport |
| `training_correlation.metric_id` | Metric the exercise correlates to | metric slug | TEXT | FK→recruiting_metric |
| `training_correlation.physical_driver` | Why the exercise moves the metric | free text (`Rotational force`, `Forearm endurance`) | TEXT | |
| `training_correlation.exercise_id` | Exercise that moves it | exercise slug | TEXT | FK→exercise |
| `training_correlation.correlation_strength` | 0..1 strength (NULL = unvalidated hypothesis) | REAL 0..1 \| NULL | REAL | |
| `training_correlation.source` | Provenance | enum-ish (`JSCR-study`, `in-house-hypothesis`, `discovered`) | TEXT | |
| `training_correlation.created_at` | Row created | ISO datetime UTC | TEXT | |

### SPINE tables (variable — kid-owned; child sovereign)

| catalog_id | description | format | type | role |
|---|---|---|---|---|
| `sport_participation.participation_id` | PK; the "kid in a sport for a season" row | UUIDv4 lowercase \| slug | TEXT | PK |
| `sport_participation.child_id` | Sovereign join | FK to `children.id` (foundation) | TEXT | FK→children |
| `sport_participation.sport_id` | Sport | sport slug | TEXT | FK→sport |
| `sport_participation.position` | Position in the sport | position slug | TEXT | |
| `sport_participation.season_year` | Calendar year of the season | INTEGER YYYY | INTEGER | |
| `sport_participation.declared_bracket` | Wrestling weight class label (NULL otherwise) | free text (e.g., `132`, `144`) | TEXT | |
| `sport_participation.club_team` | Club/team affiliation | free text | TEXT | |
| `sport_participation.status` | ORBT-ish lifecycle | enum: `ACTIVE`\|`INACTIVE`\|`RETIRED` | TEXT | |
| `sport_participation.created_at` | Row created | ISO datetime UTC | TEXT | |
| `sport_participation.updated_at` | Row last updated | ISO datetime UTC | TEXT | |
| `metric_test.metric_test_id` | PK | UUIDv4 lowercase | TEXT | PK |
| `metric_test.participation_id` | Which participation this measurement belongs to | FK | TEXT | FK→sport_participation |
| `metric_test.metric_id` | Which metric was measured | metric slug | TEXT | FK→recruiting_metric |
| `metric_test.test_date` | Date of measurement | ISO date `YYYY-MM-DD` | TEXT | |
| `metric_test.value` | Measured value in metric's canonical unit | REAL; unit MUST match `recruiting_metric.canonical_unit` | REAL | |
| `metric_test.source` | Where the measurement came from | enum: `Rapsodo`\|`Blast`\|`HitTrax`\|`MatBoss`\|`Vertec`\|`showcase`\|`manual` (extensible) | TEXT | |
| `metric_test.created_at` | Row created | ISO datetime UTC | TEXT | |
| `competition_event.event_id` | PK | UUIDv4 lowercase | TEXT | PK |
| `competition_event.participation_id` | Which participation | FK | TEXT | FK→sport_participation |
| `competition_event.event_date` | Date of event | ISO date `YYYY-MM-DD` | TEXT | |
| `competition_event.event_type` | Kind of event | enum: `tournament`\|`dual`\|`match`\|`game` | TEXT | |
| `competition_event.placement` | Finish position (NULL if N/A) | INTEGER (1=champion) | INTEGER | |
| `competition_event.bracket_size` | Field size (for placement normalization) | INTEGER | INTEGER | |
| `competition_event.event_tier` | Strength-of-competition tier (Layer-3 normalization) | enum: `fargo`\|`super32`\|`national`\|`state`\|`regional`\|`dual`\|`scrimmage` | TEXT | |
| `competition_event.event_weight` | Multiplier applied to outcomes (Fargo high, scrimmage low) | REAL ≥0; defaults 1.0; suggested fargo 2.0 / super32 1.9 / national 1.7 / state 1.4 / regional 1.1 / dual 1.0 / scrimmage 0.5 | REAL | |
| `competition_event.source` | Provenance | enum-ish (`MatBoss`\|`manual`\|`showcase`) | TEXT | |
| `competition_event.created_at` | Row created | ISO datetime UTC | TEXT | |
| `competition_stat.stat_id` | PK | UUIDv4 lowercase | TEXT | PK |
| `competition_stat.event_id` | Linked event (NULL if season-level aggregate) | FK \| NULL | TEXT | FK→competition_event |
| `competition_stat.participation_id` | Which participation | FK | TEXT | FK→sport_participation |
| `competition_stat.stat_name` | Stat key | snake_case slug (`takedown_pct`, `win_pct`, `bonus_pct`, `ride_time_sec`, `batting_avg`, `hitting_pct`, `serve_receive_pct`) | TEXT | |
| `competition_stat.stat_value` | Numeric value | REAL | REAL | |
| `competition_stat.source` | Provenance | enum-ish | TEXT | |
| `competition_stat.created_at` | Row created | ISO datetime UTC | TEXT | |

### ERROR pairs (CQRS — same columns as canonical + error metadata)

Each error table mirrors its canonical's columns (all nullable — the row may be malformed) and adds the standard error metadata block. The error metadata block is identical across all four error tables:

| catalog_id (per error table) | description | format | type |
|---|---|---|---|
| `*_error.error_id` | PK | UUIDv4 lowercase | TEXT |
| `*_error.error_reason` | Human-readable failure | sentence | TEXT |
| `*_error.error_code` | Machine code | enum per canonical (e.g., `FK_PARTICIPATION`, `UNKNOWN_METRIC`, `UNIT_MISMATCH`, `OUT_OF_RANGE`, `BAD_DATE`, `DUPLICATE`, `FK_CHILD_MISSING`, `BAD_SPORT`, `VALIDATION`, `BAD_TIER`, `MISSING_PLACEMENT`, `UNKNOWN_STAT`, `FK_EVENT`) | TEXT |
| `*_error.raw_payload` | The original payload that failed | JSON string | TEXT |
| `*_error.ingest_source` | Where it came from | enum-ish (`airtable`\|`manual`\|`matboss`\|...) | TEXT |
| `*_error.received_at` | When the error was logged | ISO datetime UTC | TEXT |
| `*_error.retry_count` | Number of fix-attempts | INTEGER ≥0 | INTEGER |
| `*_error.resolved` | 0 open / 1 fixed-and-promoted | 0\|1 | INTEGER |
| `*_error.resolved_at` | When resolved | ISO datetime UTC \| NULL | TEXT |
| `*_error.resolution_note` | What was fixed | free text | TEXT |

The canonical-column-mirror portion of each error table reproduces the canonical's columns nullable (so the fix-and-promote path is `UPDATE ... SET resolved=1 ... INSERT INTO canonical SELECT canonical_cols FROM error WHERE error_id=?`).

### DERIVED views

| view | reads | returns |
|---|---|---|
| `v_recruiting_gate` | latest `metric_test` × `recruiting_threshold` | (participation_id, child_id, sport_id, position, division, metric, measured_value, band_display, gate_status ∈ ABOVE\|AT\|BELOW) |
| `v_metric_trend` | `metric_test` | (participation, metric, test_date, value, source) ordered |
| `v_metric_normalized` | latest `metric_test` × `composite_model`/`component`/`recruiting_metric`/`recruiting_threshold` | (participation, model, metric, weight, metric_score 0..1) — base for the loop views |
| `v_composite_score` | `v_metric_normalized` | (participation, model, recruiting_score 0..100) |
| `v_metric_leverage` | `v_metric_normalized` | (participation, model, metric, weight, metric_score, score_gap, leverage = weight × (1−score)) |
| `v_prescription` | `v_metric_leverage` × `training_correlation` × `exercise` | (participation, weak_metric, exercise, projected_score_gain) ranked DESC |
| `v_open_errors` | UNION of `*_error` where resolved=0 | (canonical, error_id, error_reason, error_code, ingest_source, received_at, retry_count) |

---

## §8 INGEST CHECKLIST / KILL SWITCH

### Apply order (D1 — `kiddos` database, `5a57021b-1a6f-48ea-83a0-2e730d0fe674`)

```bash
# Prerequisite (BLOCKS this migration — write it first):
#   001_kiddos_foundation.sql   (port from kiddo-app-skeleton/archive/v1/migrations/001_d1_foundation.sql)

export CLOUDFLARE_API_TOKEN=$(doppler secrets get CF_FULL_API_TOKEN --plain -p imo-creator -c dev)
export CLOUDFLARE_ACCOUNT_ID=$(doppler secrets get GLOBAL_CLOUDFLARE_ACCOUNT_ID --plain -p imo-creator -c dev)

# 1. Foundation (children/parents/family_links)
npx wrangler d1 execute kiddos --remote --file=kiddo-app-skeleton/migrations/001_kiddos_foundation.sql

# 2. Sports-Performance engine + error pairs
npx wrangler d1 execute kiddos --remote --file=kiddo-app-skeleton/migrations/002_sports_performance_schema.sql

# 3. Per-sport seeds (build per sport — one file each)
npx wrangler d1 execute kiddos --remote --file=kiddo-app-skeleton/migrations/seed_softball.sql
npx wrangler d1 execute kiddos --remote --file=kiddo-app-skeleton/migrations/seed_wrestling.sql
npx wrangler d1 execute kiddos --remote --file=kiddo-app-skeleton/migrations/seed_volleyball.sql   # not yet written
```

### Kill switch

This is a schema, not a running worker. "Kill" = drop the database OR drop the tables. No live cron, no live route, no live consumer wired yet.

```bash
# Hard kill (destroys data):
npx wrangler d1 execute kiddos --remote --command="DROP TABLE IF EXISTS sport_participation_error; DROP TABLE IF EXISTS metric_test_error; DROP TABLE IF EXISTS competition_event_error; DROP TABLE IF EXISTS competition_stat_error; DROP VIEW IF EXISTS v_open_errors; DROP VIEW IF EXISTS v_prescription; DROP VIEW IF EXISTS v_metric_leverage; DROP VIEW IF EXISTS v_composite_score; DROP VIEW IF EXISTS v_metric_normalized; DROP VIEW IF EXISTS v_metric_trend; DROP VIEW IF EXISTS v_recruiting_gate; DROP TABLE IF EXISTS competition_stat; DROP TABLE IF EXISTS competition_event; DROP TABLE IF EXISTS metric_test; DROP TABLE IF EXISTS sport_participation; DROP TABLE IF EXISTS training_correlation; DROP TABLE IF EXISTS exercise; DROP TABLE IF EXISTS composite_component; DROP TABLE IF EXISTS composite_model; DROP TABLE IF EXISTS recruiting_threshold; DROP TABLE IF EXISTS recruiting_metric; DROP TABLE IF EXISTS sport;"
```

---

## §9 PERMISSIONS / LIVE VERIFICATION

Cloudflare API token scope verified active 2026-05-19 (Bearer `CF_FULL_API_TOKEN`, account `a1dd98c6...`). D1 `kiddos` exists, 0 tables, empty (uuid `5a57021b-1a6f-48ea-83a0-2e730d0fe674`).

### §9b Live Verification (BUILD — N/A until first apply)

Owed at apply time:
- `wrangler d1 execute kiddos --remote --command "SELECT name FROM sqlite_master WHERE type='table';"` returns the 15 expected tables.
- `INSERT` of one deliberately-malformed `metric_test` payload lands in `metric_test_error`, not in `metric_test`.
- `INSERT` of one `sport_participation(child_id=person-tyler, sport_id=wrestling, …)` + one valid `metric_test` row → `v_recruiting_gate` returns 1+ rows; `v_composite_score` returns a 0–100 value; `v_prescription` returns ≥1 row.

---

## §10 ERROR HANDLING (CQRS pairs — doctrinal)

Every canonical that accepts external input has a paired `*_error` table. Bad rows never silently drop — they land in the pair with `error_reason`, `error_code`, `raw_payload`, `ingest_source`, `received_at`, `retry_count`, `resolved` flag. The fix-and-promote workflow is one `UPDATE … SET resolved=1, resolved_at=…` + `INSERT INTO canonical SELECT canonical_cols FROM error WHERE error_id=…`. The `v_open_errors` triage view surfaces all unresolved errors across all four pairs, newest first.

The validator (Airtable side, or a CF Worker once wired) is where rows are routed canonical-vs-error. This UT defines the contract; the validator is a separate execution component (deferred — write it when Airtable lands or when the first non-manual feed needs ingestion).

---

## §11 FCE

This sub-engine IS the foundation for an FCE called **Sports-Performance Intelligence** (per `atlas/constants/FCE.md` pattern: Valuation / Concentration / Trend / Liquidity). Deferred until enough longitudinal data accumulates to compute real correlation strengths — current values are in-house hypotheses (or NULL). The closed loop (test → score → weakness → prescribe → retest) generates the input that lets the FCE actually rank metrics by `weight × gap × trainability`.

---

## §12 LBB (logbook — after first certification only)

N/A during BUILD. First entry lands when the schema is applied + first kid is seeded + the three core views return sane values.

---

## §13 BARS REFERENCED

| BAR | Status | Why |
|-----|--------|-----|
| `BAR-436` (Two-layer cockpit) | Backlog | This UT is a concrete fill of the two-layer architecture |
| `BAR-KIDDOS-SPORTS-PERFORMANCE` (pending-atlas-updates) | PENDING-SOVEREIGN | Proposes process number 2310 + CTB layer-registry additions |
| `BAR-433` (Obsidian Windows) | Done | Vault setup |

---

## §14 DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Created | 2026-05-19 |
| Last Modified | 2026-05-19 |
| Version | 0.1.0 |
| Status | BUILD |
| Authority | inherited — imo-creator (sovereign) |
| Process Number | 2310 (TENTATIVE — sovereign-confirm via `pending-atlas-updates/BAR-KIDDOS-SPORTS-PERFORMANCE.yaml`) |
| Template Version | UT v2.8.0 (database medium per `atlas/DATABASE_FILL_INSTRUCTIONS.md`) |
| Parent | `atlas/DATABASE_FILL_INSTRUCTIONS.md` + `atlas/constants/HOW_TO_BUILD_ANYTHING.md` |
| Children (execution) | `kiddo-app-skeleton/migrations/002_sports_performance_schema.sql`, `seed_softball.sql`, `seed_wrestling.sql`, `seed_volleyball.sql` (TODO), `001_kiddos_foundation.sql` (prereq, TODO — port from `archive/v1`) |
| Companions | `heir.yaml`, `orbt.yaml` |
| BAR | (Atlas attach via `pending-atlas-updates/BAR-KIDDOS-SPORTS-PERFORMANCE.yaml`) |

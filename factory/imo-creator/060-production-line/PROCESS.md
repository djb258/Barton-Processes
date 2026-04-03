# PROCESS: Production Line Engine
## Dependency-aware process orchestrator — builds, runs, traces, and certifies goals across the system
### Status: OPERATE
### Business: imo-creator

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-060 |
| Name | Production Line Engine |
| Business Silo | imo-creator |
| CTB Position | factory/imo-creator/060-production-line |
| ORBT | OPERATE |
| Strikes | 0 |
| Last Deployed | 2026-04-02 |
| BAR Reference | BAR-195, BAR-196, BAR-187 |
| Deployed URL | TBD (CF Worker + Durable Objects) |
| Cron | none (goal-triggered) |
| Runtime | CF Worker (Hono) + Durable Objects (OrchestratorAgent + LineAgent) |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Without this, processes run ad-hoc with no dependency tracking, no execution trace, no auditor certification, no sigma tracking, and no fleet-wide failure detection. This is Tier 0 as a runtime engine — IMO is the goal flow, CTB is the dependency graph, Circle is the sigma tracking, Aviation Model is the auditor certification. The doctrine is not a document. It is running code that enforces itself.

With the mathematical engine integrated, every station's pass/fail is computed by `P(x;θ) = 1 if max_i[C_i(x)/k_i] ≤ 1 else 0`. The diagnostic vector `r(x)` tells the mechanic exactly what broke and by how much. Certification is not opinion — it is bounded variance across consecutive runs.

### 060's Two Jobs

060 is not just for building production line processes. It runs on ANYTHING that needs structure defined — processes, data sections, web pages, page keys, mappings, new domains.

**060 does two things. Always. In this order:**

**Job 1: BUILD THE KEY.** Run the mathematical equation against raw data. C&V on every element. Can you name it? Can you define its format? Give each element a description, unique ID, and format. The equation converges (sigma tightens) until every element is identified or domesticated. The KEY is the output — the complete structure definition of that data source.

**Job 2: MAP THE KEY.** Once the key exists, connect it to the target structure. Column A on the source → column B in our structure. This is a lookup table. Trivial once the key is built.

**060 does NOT map. 060 DEFINES.** It defines the key. Once defined, the mapping writes itself.

The constant extractor agent (`factory/agents/constant-extractor/`) IS the tool that executes Job 1. Point it at any data source — a database table, a web page, a platform page, a DOL filing — and it runs 060 to produce the key. The agent understands 060. 060 is its operating instructions.

### Three Steps — Every Section, Every Source, Every Domain

1. **DEFINE** — Run C&V on every element. Description, unique ID, format. Build the key. This is 060 with the equation. Can't skip to step 2 without this.

2. **MAP** — Connect the key to our structure. This column → that column. Trivial once step 1 is done. Can't do this without the key.

3. **JOIN** — Find the path to the spine. How does this section connect to the outreach_id? (EIN, domain, URL, direct ID.) Without this, structured data floats in space. Can't do this without the map.

**Define. Map. Join. In order. Can't skip. The order is the constant.**

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)

1. **"What triggers this?"** — A goal submitted via POST /goals (manual, cron, inbox, agent), or a business need requiring a new process (BAR ticket).
2. **"How do we get it?"** — Two phases: BUILD creates the process, RUN executes it through the production line.

### Input

- **Phase 1 (BUILD):** BAR ticket + business requirement
- **Phase 2 (RUN):** Goal submission (line, workpiece_id, source)

### Middle

This process has two phases. Each phase is fully documented with mathematical engine integration, worked examples, and altitude breakdowns in its own reference document.

#### Phase 1: BUILD — How Processes Get Created

The altitude descent from 50K (production line station) to 5K (code + certification). Eight steps, each its own IMO with comparators C_i, tolerances k_i, and decision function P(x;θ).

| Step | Altitude | What Happens | Output |
|------|----------|-------------|--------|
| 1 | 50K | Add station to production line (lines.ts) | Station in dependency graph |
| 2 | 40K | Create process directory + 3 required files (PROCESS.md, heir.yaml, CLAUDE.md) | Documented process |
| 3 | 30K | Define internal steps, run Tier 0 on each (C&V + comparators + tolerances) | Steps with IMO defined |
| 4 | 20K | Complex/broken steps get own 14-section PROCESS.md | Step-level documentation |
| 5 | 10K | Identify tools from Snap-On Toolbox, enforce well-drinks-first | Tool configuration |
| 6 | 5K | Write code implementing the documented spec | Working code |
| 7 | 5K | Smoke test + establish analytics baseline (r(x) first run) | Execution trace + baseline |
| 8 | 5K | Auditor certification (P(x;θ) = 1 for 3 runs, var(r_i) ≤ σ_max) | Certified or rejected |

**Full detail with mathematical engine, worked examples, and comparator definitions:** `HOW_TO_BUILD_A_PROCESS.md` in this directory.

#### Phase 2: RUN — How Goals Flow Through the Line

The runtime flow from goal submission to auditor certification. Seven steps with dependency-aware execution, failure handling, and sigma tracking.

| Step | What Happens | Output |
|------|-------------|--------|
| 1 | Orchestrator validates line, creates goal + steps in D1 (ORBT = BUILD) | goal_id |
| 2 | Line agent checks dependencies, finds ready stations | Ready station list |
| 3 | Adapter calls station (HTTP/CLI/SQL/Manual), computes P(x;θ) | AdapterResponse + r(x) |
| 4 | Write execution trace, update step status, record sigma | Trace entry |
| 5a | Success → recheck for newly unblocked stations | Next ready or complete |
| 5b | Failure → fleet failure registry, ORBT → REPAIR, halt | Failure with strike tracking |
| 6 | All stations done → awaiting certification | Complete, not certified |
| 7 | Auditor certifies: P(x;θ) = 1 all stations + global gate + bounded variance | OPERATE + birth certificate |

**Full detail with mathematical engine, worked examples, API reference, and comparator computations:** `HOW_TO_RUN_A_PROCESS.md` in this directory.

#### Mathematical Engine (Both Phases)

Every step in both phases is governed by the Tier 0 Mathematical Principle:

```
PRE-GATE:    ∑_i |C_i(x)| > ε                    (non-nullity)
DECISION:    P(x;θ) = 1  if  max_i[C_i(x)/k_i] ≤ 1  else 0
DIAGNOSTIC:  r(x) = [C_1(x)/k_1, ..., C_n(x)/k_n]
STABILITY:   ∀t ∈ [1..N]: P(f^t(x);θ) = 1  AND  var(r_i) ≤ σ_max
GLOBAL GATE: ACCEPT(x_new) = P(x_new;θ') = 1  AND  ∀x ∈ L: P(x;θ') = 1
DOMESTICATE: max(r(x)) ≤ α  AND  var(r_i) ≤ σ_max  →  stop decomposing
```

### Output

- **Phase 1:** A certified process operating on the production line
- **Phase 2:** A certified goal with execution trace, logbook birth certificate, and sigma data

### Circle (Bedrock §5)

- Sigma tracking feeds back to process documentation — tightening = stable, expanding = upstream broke
- Fleet failures feed back to process repair — same station+error pattern accumulates strikes
- Strike 3 produces an Airworthiness Directive — fix goes fleet-wide
- Certified output becomes the workpiece for downstream goals
- The tolerance lifecycle IS the circle: Phase 1 (guess) → Phase 2 (failures tighten) → Phase 3 (data stops proving wrong = lock)

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| production-line D1 | D1_PRODUCTION | TBD | READ/WRITE | Goals, steps, trace, logbook, fleet failures, sigma |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| OrchestratorAgent | Durable Object | Free | none | Routes goals to line agents |
| LineAgent | Durable Object | Free | none | Walks dependency graph, calls adapters |
| HTTP Adapter | Tool | Free | per-station | Calls CF Worker stations |
| CLI Adapter | Tool | Free | per-station | Calls Python/Node scripts |
| SQL Adapter | Tool | Free | per-station | Runs D1 queries |
| Manual Adapter | Tool | Free | none | Marks station as not-callable |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PRODUCTION_API_KEY | imo-creator | dev | Auth for all /goals endpoints |

### Doctrine (from parent repo imo-creator-v2)

| Document | Path | What It Provides |
|----------|------|-----------------|
| Foundational Bedrock | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md | The synthesis (§1-8) |
| Mathematical Principle | imo-creator-v2/law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md | The math (P(x;θ), tolerances) |
| Adapter Template | imo-creator-v2/law/doctrine/TIER0_ADAPTER_TEMPLATE.md | Domain adapter blueprint |
| Snap-On Toolbox | imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml | Tool registry |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 — always first
2. Free external fetches — second
3. Cheap integrations — third
4. Top shelf — only when free/cheap exhausted

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| production_goals | Goal state, ORBT, workpiece | goal_id |
| production_steps | Step status, results, errors | goal_id → step_id |
| execution_trace | Append-only build journal | goal_id |
| production_sigma | Per-station metrics over time | station_id |
| fleet_failures | Open failure patterns | station_id + error_code |
| production_logbook | Certified entries only | goal_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| production_goals | Create + update ORBT + certify | Goal lifecycle |
| production_steps | Status updates, results, errors | Each station execution |
| execution_trace | Trace entries (append-only) | Every step |
| production_sigma | Metric values per run | After each station success |
| fleet_failures | Upsert failure patterns | On station failure |
| production_logbook | Birth certificate + entries | On certification only |

### Join Chain

```
production_goals.goal_id (SPINE)
  → production_steps.goal_id (steps per goal)
  → execution_trace.goal_id (trace per goal)
  → production_logbook.goal_id (logbook per goal)
  → production_sigma.station_id (sigma per station across goals)
  → fleet_failures.station_id (failures per station across goals)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Write to logbook during BUILD | Logbook only after auditor certification (Aviation §8) |
| Builder certifying own work | Auditor must be different engine (Aviation §8) |
| Delete trace entries | Append-only (§11) |
| Edit logbook entries | Immutable (§12) |
| Skip dependency check | Dependency graph IS the CTB |
| Modify engine to accommodate domain | Domain adapter resolves conflicts, engine never changes |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)

- The decision equation: `P(x;θ) = 1 if max_i[C_i(x)/k_i] ≤ 1 else 0`
- The diagnostic vector: `r(x) = [C_1(x)/k_1, ..., C_n(x)/k_n]`
- The adapter contract: AdapterRequest → AdapterResponse (types.ts)
- ORBT state machine: BUILD → OPERATE → REPAIR → TROUBLESHOOT_TRAIN
- Dependency graph per line (lines.ts)
- Auditor ≠ builder (different engine required)
- Trace is append-only, logbook is append-only
- Logbook only after certification
- Tolerance floor: k_i ≥ ε_k (no singularities)
- Non-nullity gate: ∑|C_i(x)| > ε (reject zero-signal)
- Stability: P must hold across N consecutive goals with var(r_i) ≤ σ_max
- The altitude model (50K → 5K) for BUILD phase
- The 14-section template (PROCESS_TEMPLATE v4.0.0)
- Canonical silo paths (4 roots from STRUCTURE_MANIFEST)
- Required files per process: PROCESS.md, heir.yaml, CLAUDE.md

### Variables (fill — changes every run)

- Which goal, which workpiece, which line
- Which stations succeed/fail per goal
- ORBT state per goal
- Tolerance thresholds k_i (discovered through operation)
- Diagnostic vector values r(x) per run
- Sigma values per station
- Fleet failure strike counts
- Which steps need 20K detail (determined by failures)

### Tolerance Lifecycle

| Phase | What Happens | When It Ends |
|-------|-------------|-------------|
| Phase 1 | Educated guess — tolerances intentionally wide | System begins operating |
| Phase 2 | Failure-driven tightening — r(x) identifies which C_i broke | k_i stops moving (convergence) |
| Phase 3 | Stabilization — lock tolerance, data stopped proving it wrong | Reopened only if new failure |

---

## 7. STOP CONDITIONS

| Condition | Action | Mathematical Basis |
|-----------|--------|-------------------|
| Can't answer two-question intake | HALT — process isn't defined | No input defined |
| Unknown line in goal submission | 400 error — invalid station | Station ∉ dependency graph |
| Station adapter fails | ORBT → REPAIR, halt line | C_i(x)/k_i > 1 |
| Strike 3 on same station+error | ORBT → TROUBLESHOOT_TRAIN | No feasible θ' exists |
| Steps still incomplete at certification | Reject certification | P(x;θ) undefined |
| Builder attempts self-certification | Reject — different engine required | Aviation §8 |
| Sigma variance expanding | Investigate — upstream misclassification | var(r_i) > σ_max |
| Skipped altitude during BUILD | HALT — descent order violated | CTB integrity |
| Budget cap reached on top shelf tool | HALT — do not proceed | Cost comparator exceeded |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Foundational Bedrock | The synthesis (§1-8) | DONE — LOCKED |
| Mathematical Principle | The math (P(x;θ), tolerances) | DONE — LOCKED |
| Process Template v4.0.0 | 14-section format | DONE — LOCKED |
| Structure Manifest | Required files, canonical paths | DONE |
| Logbook Schema | Logbook rules | DONE |
| D1 Schema | production tables migrated | DONE |
| Processes defined as stations | At least one line with stations | DONE (outreach line) |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Every process in the system | Station definition + dependency routing |
| Auditor | Execution trace to review |
| Mission Control | Goal status, sigma data |
| LBB | Session learnings from certified goals |

---

## 9. SMOKE TEST

```
1. GET /health → status ok, goals count, open errors
2. POST /goals {line: "outreach", workpiece_id: "test-001"} → 201 + goal_id
3. GET /goals/:id → goal with steps created per dependency graph
4. Verify: 010-seed step = pending, all others = blocked (dependencies)
5. Verify: station execution respects dependency order
6. Simulate failure on one station → ORBT = REPAIR, fleet failure recorded
7. POST /goals/:id/resume → failed step retries
8. POST /goals/:id/certify {auditor: "test-auditor"} → ORBT = OPERATE + logbook entry
9. GET /sigma/010-seed → sigma data recorded
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do all D1 tables exist? Do all Durable Objects instantiate?
2. **Flow:** Does a goal flow from orchestrator → line agent → adapters → trace?
3. **Change:** Does ORBT transition correctly? Does sigma record? Does logbook write on certification?

---

## 10. ANALYTICS — The Dyno Sheet (Bedrock §2 + §5 + Mathematical Principle)

_Each metric IS a comparator C_i. Each tolerance IS k_i. P(x;θ) IS the gate._

### Process Metrics

| Metric (C_i) | Unit | Grounding | Initial k_i | Phase |
|---------------|------|-----------|-------------|-------|
| Goal completion rate | % | Change | k ≥ 90% | 1 |
| Avg station duration | ms | Flow | k ≤ 300,000 | 1 |
| Goal cost | cents | Thing | k ≤ 10000 | 1 |
| Certification pass rate (first attempt) | % | Change | k ≥ 80% | 1 |
| Fleet failure count (open) | count | Thing | k ≤ 5 | 1 |
| Sigma trend (expanding stations) | count | Change | k = 0 | 1 |

### Decision Function

```
P(x;θ) = 1  if  max_i[C_i(x)/k_i] ≤ 1  for all metrics above
         0  otherwise

BUILD → OPERATE gate:  P(x;θ) = 1 for 3 consecutive goals
                       AND var(r_i(x)) ≤ σ_max for all i
```

### Sigma Tracking

| Metric | Run 1 | Run 2 | Run 3 | var(r_i) | Trend | Action |
|--------|-------|-------|-------|----------|-------|--------|
| Goal completion | BASELINE | — | — | — | — | — |
| Station duration | BASELINE | — | — | — | — | — |
| Cost per goal | BASELINE | — | — | — | — | — |

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | P(x;θ) = 1 for 3 consecutive runs + var(r_i) ≤ σ_max + auditor sign-off |
| OPERATE | REPAIR | Any C_i(x)/k_i > 1 |
| REPAIR | OPERATE | Fix applied + P(x;θ) = 1 + auditor verification |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | No feasible θ' — restructure invariants → AD |

---

## 11. EXECUTION TRACE (During BUILD)

Built into the engine — `src/lib/trace.ts` writes to `execution_trace` table. Every step produces a trace entry with: trace_id, run_id, goal_id, step_id, station_id, target, actual, delta, status, error_code, error_message, tools_used, duration_ms, cost_cents, r_i (comparator ratio), P_step (decision), signed_by, timestamp.

### Rules
- Append-only. No edits. No deletions.
- Every step gets a trace entry. No step executes without logging.
- Auditor reviews the trace to decide certification.
- Trace persists after certification as evidence.

---

## 12. LOGBOOK (After Certification Only)

Built into the engine — POST /certify writes to `production_logbook` table.

### Birth Certificate (first entry per goal)

| Field | Value |
|-------|-------|
| heir_ref | Goal HEIR (goal_id, line, workpiece_id) |
| orbt_entered | BUILD |
| orbt_exited | OPERATE |
| action | "Goal certified — all stations complete" |
| authority | "Bedrock §8 — auditor certification" |
| gates_passed | { imo: true, ctb: true, circle: true, P: 1, var_r: bounded } |
| signed_by | Auditor agent (different engine than builder) |

### Rules (from logbook_schema.yaml)
1. No logbook until certified
2. First entry is always the birth certificate
3. Append-only. Immutable.
4. Builder CANNOT be the auditor

---

## 13. FLEET FAILURE REGISTRY & STRIKE TRACKING

Built into the engine — `src/lib/fleet-failures.ts` writes to `fleet_failures` table.

### Failure Pattern Registry

| Pattern ID | Station | Error Code | Occurrences | Strike Count | Status |
|-----------|---------|-----------|-------------|-------------|--------|
| (populated at runtime) | | | | | |

### Strike Rules
- **Strike 1:** C_i(x)/k_i > 1. Repair at source. Log it.
- **Strike 2:** Same comparator violation. Was root cause found?
- **Strike 3:** No feasible θ'. Constraint collision. Troubleshoot/Train → AD.

---

## 14. SESSION LOG

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| 2026-04-02 | Dave built production line engine (BAR-195/196). Lines.ts, agents, adapters, D1 schema. | none |
| 2026-04-02 | HOW_TO_BUILD + HOW_TO_RUN written as 14-section docs with math | none |
| 2026-04-02 | PROCESS.md created merging both phases + heir.yaml + CLAUDE.md | d4d48096 |

---

## Reference Documents

The two phases are fully detailed in companion documents in this directory:

| Document | Phase | Lines | What It Contains |
|----------|-------|------:|-----------------|
| `HOW_TO_BUILD_A_PROCESS.md` | Phase 1: BUILD | 807 | Altitude descent, worked example with comparators, descent checklist, tolerance lifecycle |
| `HOW_TO_RUN_A_PROCESS.md` | Phase 2: RUN | 983 | Runtime flow, worked example with P(x;θ) computation, API reference, failure handling |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-02 |
| Last Modified | 2026-04-02 |
| Version | 1.0.0 |
| Template Version | 4.0.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md (parent repo) |
| Mathematical Engine | imo-creator-v2/law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md (parent repo) |
| Logbook Schema | Barton-Processes/law/logbook_schema.yaml |
| OSAM Authority | D1 schema: migrations/0001_production.sql |

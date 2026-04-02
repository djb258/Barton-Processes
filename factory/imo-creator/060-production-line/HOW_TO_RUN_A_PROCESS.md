# PROCESS: Run a Process Goal
## How a goal flows through the production line at runtime -- the pilot's operating handbook.
### Status: OPERATE
### Business: imo-creator

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-060-RUN |
| Name | Run a Process Goal |
| Business Silo | imo-creator |
| CTB Position | factory/imo-creator/060-production-line |
| ORBT | OPERATE |
| Strikes | 0 |
| Last Deployed | 2026-04-01 |
| BAR Reference | BAR-195, BAR-196 |
| Deployed URL | TBD (production-line CF Worker) |
| Cron | manual / inbox / agent / cron (all four sources supported) |
| Runtime | CF Worker (Hono + Durable Objects) |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Without this, nobody knows how to submit a goal, monitor execution, handle failures, or get certification. Every process in the factory produces work through goals -- this is the runtime contract that turns a goal submission into a certified, logbooked outcome. Downstream, every silo (outreach, conversion, IMO internal) starves without a clear execution path from "I have a workpiece" to "the auditor signed off."

---

## 3. IMO -- What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** -- A goal submitted via `POST /goals` (manual, cron, inbox, or agent source).
2. **"How do we get it?"** -- The production line engine routes the goal through stations defined in `lines.ts`, executed by Durable Object agents.

### Input

A goal submission containing:
- `line` (required) -- which production line to run (outreach, conversion, cl, imo)
- `workpiece_id` (required) -- the entity being processed (e.g., company domain)
- `workpiece_name` (optional) -- human-readable label
- `source` (optional, default: "manual") -- one of: inbox, cron, manual, agent
- `inbox_task_id` (optional) -- links to upstream inbox task if source is inbox

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | `POST /goals` with line + workpiece_id | Orchestrator validates line exists (from `lines.ts`), creates goal in D1 with HEIR identity stamp, creates all steps from line definition with dependency graph | goal_id + production_steps rows (pending/blocked) | OrchestratorAgent (Durable Object) |
| 2 | Goal with steps in D1 | Line agent queries all steps, finds stations whose `depends_on` are all `done` | Ready station list | LineAgent (Durable Object) |
| 3 | Ready station | Adapter calls the station based on `adapter_type` -- HTTP fetch to CF Worker, CLI exec of Python script, SQL query on D1, or Manual (marks not-callable) | AdapterResponse: `{ success, station_id, result, error, metrics }` | Adapter (http / cli / sql / manual) |
| 3b | AdapterResponse | **Compute station gate P(x;theta).** Extract comparators from metrics: `C_duration(x) = duration_ms`, `C_cost(x) = cost_cents`, `C_error(x) = error_rate`. Compute `r(x) = [C_i(x)/k_i]` for each. Station passes if `max_i[C_i(x)/k_i] <= 1`. Store `r(x)` vector in execution_trace and production_sigma. | P(x;theta) = 1 (pass) or 0 (fail) + diagnostic vector r(x) | Station Gate (computed inline) |
| 4 | AdapterResponse + r(x) | Write execution trace entry (S11) to `execution_trace` table -- append-only, every step logged. **r(x) vector stored as diagnostic payload.** | Trace entry row with status, duration, cost, tools_used, r(x) | `trace.ts` |
| 5 | Success response (P=1) | Record sigma metric (each comparator ratio), mark step `done`, store result JSON, recheck for newly unblocked stations. **Variance check: `var(r_i(x))` over sliding window must be <= sigma_max.** | Next ready stations or all-complete signal | LineAgent |
| 5b | Failure response (P=0) | Record fleet failure via `fleet-failures.ts` -- **identify WHICH comparator broke: `C_i(x)/k_i > 1` tells the mechanic the exact violation and magnitude.** Upsert on station_id + error_code. Update goal ORBT to REPAIR (or TROUBLESHOOT_TRAIN on strike 3), halt execution. | Failure with r(x) diagnostic + strike tracking, goal halted | `fleet-failures.ts` + `orbt.ts` |
| 6 | All callable stations done | Goal marked `completed_at`, trace entry written: "All callable stations complete. Awaiting auditor certification." Builder does NOT flip to OPERATE. | Goal in BUILD state, awaiting auditor | LineAgent |
| 7 | `POST /goals/:id/certify` with auditor field | **Global gate fires.** Auditor verifies: (a) P(x;theta) = 1 for ALL stations in this goal, (b) back-propagation check: new goal's tolerances don't break any prior certified goal (`forall x in L: P(x;theta') = 1`), (c) execution trace reviewed. Flips ORBT BUILD -> OPERATE, writes birth certificate to `production_logbook`. | OPERATE + logbook entry | Certify endpoint (index.ts) |

### Output

- Certified goal with ORBT = OPERATE
- Complete execution trace (append-only evidence chain) **with r(x) diagnostic vectors per station**
- Birth certificate in `production_logbook`
- Sigma data per station (comparator ratios per run, variance tracked)
- Fleet failure records if any station failed **with comparator violation detail**

### Worked Example -- A Goal Flowing Through the Line

An enrichment line with 5 stations. A company workpiece enters. Here is what the production line does at runtime:

```
POST /goals { line: "enrichment", workpiece_id: "company-batch-001" }
|
v
ORCHESTRATOR (hub)
|  Validates line exists
|  Creates goal in D1 (ORBT = BUILD)
|  Creates 5 steps from line definition
|  Routes to Line Agent
|
v
LINE AGENT (spoke)
|
|  +-- Check dependencies ------------------------------------------+
|  |  Station: SEED (depends_on: [])         -> READY               |
|  |  Station: ENRICH (depends_on: [SEED])   -> BLOCKED             |
|  |  Station: PEOPLE (depends_on: [ENRICH]) -> BLOCKED             |
|  |  Station: EMAIL (depends_on: [PEOPLE])  -> BLOCKED             |
|  |  Station: COMPILE (depends_on: [EMAIL]) -> BLOCKED             |
|  +----------------------------------------------------------------+
|
|  Execute SEED (adapter: http -> calls CF Worker)
|  |-- AdapterResponse received
|  |   Compute P(x;theta):
|  |     C_duration(x) = 1200ms, k_duration = 5000ms -> ratio = 0.24
|  |     C_cost(x) = 0 cents, k_cost = 100 cents     -> ratio = 0.00
|  |     r(x) = [0.24, 0.00]
|  |     max(r(x)) = 0.24 <= 1 -> P(x;theta) = 1 (PASS)
|  |-- r(x) stored in execution_trace + production_sigma
|  |-- Step = done. Recheck: ENRICH now READY (SEED done)
|  |
|  Execute ENRICH (adapter: cli -> calls Python script)
|  |   Inside the process: organize -> validate -> execute -> write
|  |   The line agent doesn't see internals -- just waits for result
|  |-- AdapterResponse received
|  |   Compute P(x;theta):
|  |     C_duration(x) = 8500ms, k_duration = 15000ms -> ratio = 0.57
|  |     C_cost(x) = 12 cents, k_cost = 50 cents      -> ratio = 0.24
|  |     C_error(x) = 0.02, k_error = 0.10            -> ratio = 0.20
|  |     r(x) = [0.57, 0.24, 0.20]
|  |     max(r(x)) = 0.57 <= 1 -> P(x;theta) = 1 (PASS)
|  |-- r(x) stored. Sigma variance check: var([0.57, prev...]) <= sigma_max
|  |-- Step = done. Recheck: PEOPLE now READY
|  |
|  Execute PEOPLE (adapter: cli)
|  |   CONDITIONAL: reads workbench, skips slots already filled
|  |   (Domesticated variable check: max(r(x)) <= alpha -> skip station)
|  |-- Success -> trace, sigma, step = done
|  |   Recheck: EMAIL now READY (PEOPLE done)
|  |
|  Execute EMAIL (adapter: cli, conditional: only if has_name AND no email)
|  |-- FAILURE -> error_code: CAPTCHA_THRESHOLD
|  |   |
|  |   Compute P(x;theta):
|  |     C_duration(x) = 45000ms, k_duration = 30000ms -> ratio = 1.50
|  |     C_error(x) = 1.0, k_error = 0.10             -> ratio = 10.0
|  |     r(x) = [1.50, ..., 10.0]
|  |     max(r(x)) = 10.0 > 1 -> P(x;theta) = 0 (FAIL)
|  |   |
|  |   Diagnostic: C_error/k_error = 10.0 -- error rate 10x tolerance
|  |   Diagnostic: C_duration/k_duration = 1.50 -- 50% over time budget
|  |   |
|  |   v
|  |   Fleet failure recorded: station=EMAIL, code=CAPTCHA_THRESHOLD
|  |   r(x) vector stored -- mechanic sees WHICH comparator broke and by HOW MUCH
|  |   Strike count: 1 (first occurrence)
|  |   Goal ORBT -> REPAIR
|  |   Line agent HALTS
|  |   |
|  |   v
|  |   Human reviews r(x): error_rate ratio = 10.0 (the problem)
|  |   REPAIR = tolerance recalibration: adjust proxy config (not k_i -- fix the source)
|  |   If source fix insufficient, recalibrate k_error within feasibility constraints
|  |   POST /goals/:id/resume
|  |   |
|  |   v
|  |   EMAIL retried -> Success this time
|  |   New r(x) = [0.80, 0.15, 0.05] -- all ratios <= 1
|  |   Recheck: COMPILE now READY
|  |
|  Execute COMPILE (adapter: http -> calls CF Worker)
|  |-- Success -> all stations done
|  |
|  v
|  ALL STATIONS COMPLETE
|  Goal marked: completed_at = now
|  Status: awaiting_certification
|
v
POST /goals/:id/certify { auditor: "auditor-agent" }
|  GLOBAL GATE fires:
|  (a) P(x;theta) = 1 for ALL 5 stations (verified from execution_trace r(x) vectors)
|  (b) Back-propagation: forall x in L (prior certified goals): P(x;theta') = 1
|      New goal's tolerance set doesn't break any previously certified goal
|  (c) Sigma stability: var(r_i(x)) <= sigma_max across recent runs
|  |
|  All gates pass -> ORBT -> OPERATE
|  Birth certificate written to production_logbook
|
v
GOAL CERTIFIED
|  Workbench updated with enriched data
|  r(x) history available for trend analysis (sigma tracking)
|  Ready for next goal on the line
```

**Key pattern:** The line agent walks the dependency graph mechanically. It doesn't know what happens inside each station -- it calls the adapter and reads the response. The AdapterResponse metrics ARE the comparator values C_i(x). The tolerance thresholds k_i are defined per station in the analytics config. `P(x;theta) = 1 if max_i[C_i(x)/k_i] <= 1` -- that's the station gate. Success -> next station. Failure -> the r(x) vector tells the mechanic WHICH comparator broke and by HOW MUCH. All stations done -> global gate at certification: P=1 for all stations AND back-propagation clean. The auditor is always a different engine than the builder.

### Circle (Bedrock S5)

- **Sigma tracking** feeds back to process analytics -- `var(r_i(x))` tightening = station stabilizing (real constant), flat = phantom (something isn't learning), expanding = broken (something upstream changed).
- **Fleet failures** feed back to process repair -- the r(x) vector identifies the specific comparator violation, not just "it failed." Same station+error_code pattern accumulates strikes.
- **Strike 3** produces an Airworthiness Directive (AD) -- the tolerance system itself needs restructuring (constraint collision per Mathematical Principle). Fix goes fleet-wide, not just the failing goal.
- **Logbook entries** feed back to LBB ingest -- session learnings persist for next run.
- **Certified output** becomes the workpiece for downstream goals (e.g., outreach goal produces enriched company data that feeds the next campaign).

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches. A mechanic reads this and knows exactly what to set up before the process can run._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| production-line D1 | D1_PRODUCTION | (see wrangler.toml) | READ + WRITE | production_goals, production_steps, execution_trace, fleet_failures, production_logbook, production_sigma |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| OrchestratorAgent | Durable Object | Free | none | Routes goals to correct line agent. Hub -- does NOT run stations. |
| LineAgent | Durable Object | Free | none | Executes stations per dependency graph. One per line. |
| HTTP Adapter | CF Worker fetch | Free | none (station auth handled by station) | Calls CF Worker stations (seed, LCS compile, campaign) |
| CLI Adapter | Python exec | Free | none | Calls Python scripts (blog-recon, find-person, find-email, find-linkedin, talent-flow) |
| SQL Adapter | D1 query | Free | none | Runs SQL queries (DOL views) |
| Manual Adapter | Marker | Free | none | Marks stations as not-callable -- does not halt the line |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PRODUCTION_API_KEY | imo-creator | dev | Auth middleware -- all endpoints except /health and /agents/* |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 -- always first
2. Free external fetches (CF Worker fetch, no proxy) -- second
3. Cheap integrations (Composio routes) -- third
4. Top shelf (per-call APIs, proxy services) -- only when free/cheap exhausted

---

## 5. OSAM -- Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins. What's forbidden._

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| production_goals | Goal identity, ORBT state, line, workpiece, timestamps | goal_id |
| production_steps | Step status, adapter info, results, errors, dependencies | goal_id (FK) |
| execution_trace | Append-only build journal -- what happened, when, how long, what cost, **r(x) diagnostic vectors** | goal_id (FK) |
| fleet_failures | Open squawk sheet -- station + error_code patterns, strike counts, **comparator violation detail** | station_id + error_code |
| production_logbook | Certified records -- birth certificates, maintenance entries | goal_id (FK) |
| production_sigma | Per-station metrics across runs -- **comparator ratios r(x), variance history** | station_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| production_goals | INSERT new goal (Step 1), UPDATE orbt_mode (Step 5b, 7), UPDATE completed_at (Step 6), UPDATE certified_by/certified_at (Step 7) | Steps 1, 5b, 6, 7 |
| production_steps | INSERT all steps (Step 1), UPDATE status/result/error/duration (Steps 3-5b), UPDATE on resume (retry) | Steps 1, 3, 4, 5, 5b |
| execution_trace | INSERT trace entries -- every step, every status change, **every r(x) vector** (append-only) | Steps 1, 3b, 4, 6 |
| fleet_failures | UPSERT on station_id + error_code -- increment occurrences, strike_count, append goal_id, **store violating comparator ratios** | Step 5b |
| production_logbook | INSERT birth certificate (certification only) | Step 7 |
| production_sigma | INSERT metric per completed station -- **comparator ratio per C_i, not just raw value** | Step 5 |

### Join Chain

```
production_goals.goal_id                    (spine)
  -> production_steps.goal_id               (1:many -- all stations for this goal)
  -> execution_trace.goal_id                (1:many -- all trace entries + r(x) vectors for this goal)
  -> production_logbook.goal_id             (1:many -- certification + maintenance records)
  -> fleet_failures.station_id              (many:many via station_id -- cross-goal pattern)
       -> production_sigma.station_id       (1:many -- comparator ratios per station across goals)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Writing to production_logbook during BUILD | Logbook only after auditor certification (Bedrock S8) |
| Builder certifying own work | Auditor must be different engine than builder (Bedrock S8) |
| Deleting execution_trace entries | Trace is append-only, immutable (S11) |
| Editing production_logbook entries | Logbook is append-only, immutable (S12) |
| Deleting fleet_failures records | Failures resolve, never delete -- status changes to resolved/ad_issued |
| Direct ORBT -> OPERATE without /certify | Only the certify endpoint can transition BUILD -> OPERATE |
| Setting k_i below tolerance floor (epsilon_k) | Creates numerical singularity -- any non-zero C_i(x) produces infinite ratio (Mathematical Principle) |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| What goals are running on the outreach line? | production_goals | line = 'outreach', orbt_mode |
| Which station failed for goal X? | production_steps | goal_id + status = 'failed' |
| How long did station 300-recon take last 20 runs? | production_sigma | station_id = '300-recon', metric = 'duration_ms' |
| What fleet failures are open? | fleet_failures | status = 'open' |
| Has this goal been certified? | production_goals | certified_by IS NOT NULL |
| What did the auditor write? | production_logbook | goal_id + visit_path = 'CERTIFICATION' |
| Which comparator broke on station X? | execution_trace | station_id = X, status = 'failed' -> parse r(x) for max ratio |
| Is station X stabilizing or degrading? | production_sigma | station_id = X -> compute var(r_i(x)) over last N runs |

---

## 6. CONSTANTS & VARIABLES (Bedrock S2 + Mathematical Principle)

### Constants (structure -- never changes)

_What is fixed regardless of what data flows through. If this changes, you're redesigning, not operating._

- **Adapter contract:** `AdapterRequest -> AdapterResponse` -- every station, regardless of type, conforms to the same input/output interface
- **ORBT state machine:** BUILD -> OPERATE -> REPAIR -> TROUBLESHOOT_TRAIN -- the only valid transitions, enforced by code
- **Dependency graph per line:** Defined in `lines.ts` -- 010-seed before 300-recon, 300-recon before 200-people, etc. The graph is the constant, which stations execute is the variable.
- **Auditor != builder:** The certify endpoint requires an `auditor` field. The line agent that built the goal cannot self-certify.
- **Trace is append-only:** execution_trace is INSERT-only. No UPDATE, no DELETE. Immutable evidence.
- **Logbook only after certification:** production_logbook receives its first entry (birth certificate) only when /certify succeeds.
- **Four adapter types:** http, cli, sql, manual -- the adapter_type enum is locked. Adding a fifth is a redesign.
- **Four source types:** inbox, cron, manual, agent -- the source enum is locked.
- **HEIR stamp at goal creation:** Every goal gets sovereign_ref, hub_id, cc_layer, ctb_placement at INSERT.
- **Fleet failure keyed by station_id + error_code:** Same pattern across goals accumulates strikes, not per-goal counting.
- **The decision equation:** `P(x;theta) = 1 if max_i[C_i(x)/k_i] <= 1 else 0` -- this is the ONLY gate function. No secondary evaluation. No override. No qualitative assessment.
- **The diagnostic vector:** `r(x) = [C_1(x)/k_1, C_2(x)/k_2, ..., C_n(x)/k_n]` -- always computed, always stored. P(x) for the gate, r(x) for the mechanic.
- **Global gate (back-propagation):** `ACCEPT(x_new) = P(x_new;theta') = 1 AND forall x in L: P(x;theta') = 1` -- adding a new certified goal triggers revalidation of ALL prior constants.
- **Tolerance floor:** `k_i >= epsilon_k` for all i -- prevents calibration from driving k_i toward zero (numerical singularity).
- **Non-nullity gate:** `sum_i |C_i(x)| > epsilon` -- reject zero-signal inputs before evaluating P(x;theta).

### Station Comparators

_Each station's AdapterResponse maps directly to comparator functions C_i(x). The tolerance thresholds k_i are defined per station in the analytics config (Section 10). Together they compute the station gate._

| Comparator | Source in AdapterResponse | Axiom Grounding | What It Measures |
|-----------|--------------------------|-----------------|-----------------|
| C_duration(x) | `metrics.duration_ms` | Flow | Did the flow complete in time? |
| C_cost(x) | `metrics.cost_cents` | Change | Did the transformation stay within cost budget? |
| C_error(x) | `error_rate` (derived: failures / attempts) | Change | Did the change happen correctly? |
| C_success(x) | `success` (boolean -> 0/1) | Thing | Did the output thing exist? |

**Decision per station:**

```
P(x;theta) = 1   if   max_i [ C_i(x) / k_i ] <= 1
P(x;theta) = 0   otherwise
```

**Diagnostic vector stored per step:**

```
r(x) = [ C_duration(x)/k_duration,  C_cost(x)/k_cost,  C_error(x)/k_error ]
```

Stored in `execution_trace` for each step. The mechanic reads r(x) to know exactly which comparator broke and by how much -- not just "it failed."

**Stability requirement -- P must hold across N consecutive goals:**

A single passing run is provisional. The station is only stable when:

```
forall t in [1..N]:  P(f^t(x); theta) = 1
AND  var(r_i(x)) over [t-w..t] <= sigma_max   for all i
```

Where w = sliding window size, sigma_max = max permitted variance per comparator. A station that passes but oscillates (high variance in r(x)) is NOT stable -- it's a domesticated variable at best, a phantom constant at worst.

**Tolerance lifecycle (per station):**

| Phase | When | What Happens | k_i State |
|-------|------|-------------|-----------|
| Phase 1: Initial Set | First deploy | k_i set intentionally wide based on domain expertise. They will be wrong. This is correct. | Wide, educated guess |
| Phase 2: Calibration | After failures surface | r(x) identifies which C_i(x)/k_i broke and by how much. Tighten k_i at observed failure boundary (never below epsilon_k). Check feasibility: does tightening break prior stations? | Tightening, failure-driven |
| Phase 3: Stabilization | k_i stops moving | Variance bounded, ratios converging. Lock tolerance. Not because declared correct -- because data stopped proving it wrong. | Locked (conditionally) |

**Reopening rule:** New failure modes can move a previously stable k_i. If movement resumes, return to Phase 2. Locks are conditional on continued stability.

### Variables (fill -- changes every run)

_The values that fill the constants. Different every execution._

- Which goal (goal_id -- UUID per submission)
- Which workpiece (workpiece_id -- the company or entity being processed)
- Which stations succeed vs. fail (step status per run)
- ORBT state per goal (transitions through the state machine)
- Sigma values (comparator ratios r(x) per station per run)
- Which line is run (outreach, conversion, cl, imo)
- Prior outputs passed to downstream stations (result JSON from completed deps)
- Tolerance values k_i (adapter-defined, calibrated through operation -- the variable that the tolerance lifecycle fills)
- Comparator values C_i(x) (the raw measurements from each AdapterResponse)

### Domesticated Variables in Routing

_The conditional logic between stations (read workbench, check NULLs) is a domesticated variable check._

A slot's readiness tier is computed as: `max(r(x)) <= alpha` where alpha is the domestication threshold (defined per adapter, 0 < alpha < 1). If the remaining variables can't change the outcome (all comparator ratios are far below 1 with bounded variance), the station can be skipped. This is the mathematical basis for conditional stations like PEOPLE ("skip slots already filled") and EMAIL ("only if has_name AND no email").

**Domestication requires bounded variance** -- a variable with low amplitude but high noise is not domesticated, it is unstable.

---

## 7. STOP CONDITIONS

_When to halt. Not optional. From Troubleshooting Loop (Bedrock S6), Aviation Model (Bedrock S8), and Mathematical Principle._

| Condition | Action | Mathematical Basis |
|-----------|--------|-------------------|
| Unknown line submitted | 400 error: `Unknown line: {name}. Available: outreach, conversion, cl, imo` | Pre-gate: input doesn't map to any adapter |
| Missing line or workpiece_id | 400 error: `line and workpiece_id are required` | Non-nullity: `sum_i |C_i(x)| <= epsilon` -- no signal to evaluate |
| Station adapter fails (non-NOT_CALLABLE) | ORBT -> REPAIR, halt goal execution, record fleet failure | P(x;theta) = 0: at least one `C_i(x)/k_i > 1` |
| Strike 3 on same station + error_code pattern | ORBT -> TROUBLESHOOT_TRAIN, halt -- produce Airworthiness Directive | Constraint collision: no theta' exists that satisfies all constraints. The invariant set requires restructuring, not tighter tolerances. |
| Attempt to certify from non-BUILD state | 400 error: `Cannot certify from {orbt_mode}` | ORBT state machine constant violated |
| Steps still incomplete at certification | 400 error: `{count} steps still incomplete` | Global gate cannot fire: not all P(x;theta) computed |
| Attempt to resume from non-REPAIR state | 400 error: `Cannot resume from {orbt_mode} -- must be REPAIR` | ORBT state machine constant violated |
| No auditor field on /certify | 400 error: `auditor field is required` | Builder != auditor constant violated |
| Unauthorized request (missing/bad API key) | 401 error: `Unauthorized` | Pre-gate: identity check |
| Sigma variance expanding on station | Warning: station degrading, investigate upstream | `var(r_i(x)) > sigma_max` -- stability integrity constraint violated |
| Tolerance hitting floor (k_i approaching epsilon_k) | STOP calibration: singularity risk | Tolerance floor: `k_i >= epsilon_k` -- cannot tighten further |
| Feasibility region collapsed | STOP: constraint collision between stations | `vol(Theta)^(1/n) < delta` -- tolerances are knife-edge, restructure invariants |

### Comparator Violation Diagnostics

When a station fails, the mechanic does NOT chase "it failed." The r(x) vector provides precision:

```
r(x) = [C_duration/k_duration, C_cost/k_cost, C_error/k_error]
      = [0.80,                  0.15,           10.0          ]
                                                 ^^^^
                                                 THIS is the problem.
                                                 C_error/k_error = 10.0
                                                 Error rate is 10x tolerance.
```

**The diagnostic workflow:**
1. Read r(x) from execution_trace for the failed step
2. Identify `max_i[C_i(x)/k_i]` -- that's the primary violation
3. Check magnitude: ratio of 1.1 = barely over, ratio of 10.0 = catastrophic
4. Check history: is this comparator's variance tightening (converging toward fix) or expanding (upstream broke)?
5. Fix at source: adjust the thing that produces C_i(x), not the tolerance k_i. Tolerance recalibration is the fallback when the source can't be fixed, within feasibility constraints.
6. If sigma expanding after fix -> the fix didn't work. Back to step 1.

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Production line CF Worker deployed | Hono app + Durable Objects (OrchestratorAgent, LineAgent) | DONE |
| D1 schema migrated (0001_production.sql) | 6 tables: goals, steps, trace, failures, logbook, sigma | DONE |
| Line definitions in lines.ts | 4 lines (outreach, conversion, cl, imo) with station graphs | DONE |
| Station processes built and deployed | Each station (010-seed, 300-recon, 200-people, etc.) must be reachable by its adapter | MIXED (see each station's ORBT) |
| PRODUCTION_API_KEY in Doppler | Auth for all non-health endpoints | DONE |
| Adapter modules (http, cli, sql, manual) | Each adapter type must have its implementation in src/adapters/ | DONE |
| HEIR stamp utility (lib/heir.ts) | Stamps goal identity at creation | DONE |
| Fleet failure utility (lib/fleet-failures.ts) | Records and escalates station failures | DONE |
| Trace utility (lib/trace.ts) | Writes execution trace entries | DONE |
| Tolerance config per station | k_i values for each comparator per station (Phase 1 initial set) | TBD -- define in analytics config |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Auditor (human or agent) | Execution trace with r(x) vectors to review before certification |
| LBB (Library Barton Brain) | Session learnings ingested after certification |
| Next goal on same workpiece | Prior outputs from certified goal inform next run |
| Dashboard (imo-dashboard) | Goal status, sigma trends (comparator ratio variance), fleet failures for display |
| Airworthiness Directive process | Fleet failure at strike 3 (constraint collision) triggers AD authoring |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output. Not prose -- run these._

```
1. GET /health
   -> expected: { status: "ok", goals: <number>, open_fleet_failures: <number>, timestamp: <ISO-8601> }

2. POST /goals with body: { "line": "outreach", "workpiece_id": "test-company.com", "workpiece_name": "Test Company", "source": "manual" }
   -> expected: 201 + { goal_id: "<uuid>" }

3. GET /goals/<goal_id>
   -> expected: goal with steps array (9 stations for outreach line), trace entries, empty logbook
   -> verify: steps have correct depends_on relationships

4. Verify dependency execution order:
   -> 010-seed runs first (depends_on: [])
   -> 300-recon and 400-dol run after 010-seed (depends_on: ["010-seed"])
   -> 200-people runs after 300-recon (depends_on: ["300-recon"])
   -> 100-lcs runs after 200-people, 201-email, 202-linkedin, 400-dol, 500-talent

5. Simulate station failure:
   -> verify: goal orbt_mode = "REPAIR"
   -> verify: fleet_failures has new/updated entry for station + error_code
   -> verify: execution_trace has failed entry WITH r(x) vector showing which C_i/k_i > 1
   -> verify: the violating comparator ratio identifies the break (not just "status: failed")

6. POST /goals/<goal_id>/resume
   -> expected: { status: "resumed", goal_id: "<uuid>" }
   -> verify: failed steps reset to "pending", orbt_mode back to "BUILD"

7. POST /goals/<goal_id>/certify with body: { "auditor": "smoke-test-auditor" }
   -> expected: { status: "certified", goal_id: "<uuid>", orbt_mode: "OPERATE", certified_by: "smoke-test-auditor" }
   -> verify: production_logbook has birth certificate entry with gates_passed, checklist_type = "build"
   -> verify: global gate checked -- all station P(x;theta) = 1

8. GET /errors
   -> expected: array of open fleet failures (may be empty if smoke test station succeeded)
   -> verify: each failure includes comparator violation detail (which C_i/k_i exceeded 1)

9. GET /sigma/010-seed
   -> expected: sigma entries with metric = "duration_ms", ascending run_number
   -> verify: after 3+ runs, can compute var(r_i(x)) to determine trend (tightening/flat/expanding)
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** Did every component exist where it should? (Worker deployed, D1 migrated, agents registered, adapters present)
2. **Flow:** Did the data reach every step? (Goal -> orchestrator -> line agent -> adapter -> trace)
3. **Change:** Did the transformation happen correctly? (Steps transitioned through statuses, ORBT moved through state machine, logbook written at certification)

If any fails -> that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock S6).

---

## 10. ANALYTICS -- The Dyno Sheet (Bedrock S2 + S5 + Mathematical Principle)

_The BUILD->OPERATE gate. No analytics passing tolerance = stays on the dyno._

_This section MUST be defined BEFORE build starts. No analytics spec -> no build authorization (BAR-187)._

_Every metric below IS a comparator C_i with a defined tolerance k_i. The production_sigma table IS the r(x) history. OPERATE status = P(x;theta) = 1 for 3+ consecutive goals with bounded variance._

### Process Metrics (Comparators + Tolerances)

_Each metric is a comparator function C_i(x). Each tolerance is k_i. The ratio C_i(x)/k_i is what gets tracked in production_sigma._

| Metric (C_i) | Unit | k_i (Tolerance) | Phase 1 (Deploy) | Phase 2 (Calibrate) | Phase 3 (Stable) | Axiom |
|--------------|------|-----------------|-------------------|---------------------|-------------------|-------|
| Goals submitted per line per day | count | k_submit = BASELINE +/- 50% | Wide: accept anything | Tighten from observed distribution | Lock when var <= sigma_max | Flow |
| Goals completed (certified) per day | count | k_complete = BASELINE +/- 50% | Wide | Tighten | Lock | Change |
| Goals failed per day | count | k_fail = < 20% of submitted | Wide | Tighten from failure patterns | Lock | Change |
| Avg duration per station | ms | k_duration = BASELINE +/- 30% | Wide: 5-30s depending on station | Tighten per station from r(x) history | Lock per station | Flow |
| Cost per goal (sum of step costs) | cents | k_cost = BASELINE +/- 25% | Wide: 0-100 cents | Tighten from actual spend | Lock | Change |
| Certification pass rate | % | k_cert = > 80% | Wide: > 50% | Tighten toward > 90% | Lock at > 90% | Change |
| Fleet failure count (open) | count | k_fleet = < 5 | Wide: < 10 | Tighten to < 3 | Lock at < 3 | Thing |
| Sigma trend per station | trend | sigma_max = per station | Wide | Calibrate per comparator | Lock when variance stabilized | All three |

**OPERATE gate (the global decision):**

```
OPERATE = P(x;theta) = 1
  for ALL metrics above
  for 3+ consecutive goals
  AND var(r_i(x)) <= sigma_max for each metric
  AND auditor sign-off
```

### Tool Scorecard (per Snap-On sub-hub vendor)

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| HTTP Adapter | CF Worker fetch | BASELINE | $0 | BASELINE | BASELINE | first run |
| CLI Adapter | Python exec | BASELINE | $0 | BASELINE | BASELINE | first run |
| SQL Adapter | D1 query | BASELINE | $0 | BASELINE | BASELINE | first run |
| Manual Adapter | N/A | N/A | $0 | N/A | N/A | N/A |

### Sigma Tracking (Bedrock S2 + Mathematical Principle)

_The production_sigma table IS the r(x) history. After 3+ runs, compute `var(r_i(x))` over a sliding window to determine trend._

**How sigma is computed (from the Mathematical Principle):**

```
For each station, for each run:
  r(x) = [ C_duration(x)/k_duration, C_cost(x)/k_cost, C_error(x)/k_error ]

Over sliding window of last w runs:
  var(r_i(x)) = variance of the i-th ratio across the window

Trend determination:
  var(r_i) decreasing over windows -> TIGHTENING (real constant)
  var(r_i) constant over windows   -> FLAT (phantom constant)
  var(r_i) increasing over windows -> EXPANDING (broken prior constant)

Hard cap:
  var(r_i(x)) <= sigma_max for all i, or stability check fails
```

| Metric | Run 1 r(x) | Run 2 r(x) | Run 3 r(x) | var(r_i) | Trend | Action |
|--------|-----------|-----------|-----------|----------|-------|--------|
| 010-seed duration ratio | -- | -- | -- | -- | -- | awaiting data |
| 300-recon duration ratio | -- | -- | -- | -- | -- | awaiting data |
| 200-people duration ratio | -- | -- | -- | -- | -- | awaiting data |
| 100-lcs duration ratio | -- | -- | -- | -- | -- | awaiting data |

_Tightening var = real constant, process is stabilizing. Flat var = phantom, something isn't learning. Expanding var = broken, something upstream changed. This is NOT subjective -- var(r_i(x)) is a number. Compute it._

### ORBT Gate Rule

| From | To | Gate | Mathematical Condition |
|------|-----|------|----------------------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs + **auditor sign-off** | `forall t in [1..3]: P(f^t(x);theta) = 1 AND var(r_i(x)) <= sigma_max` |
| OPERATE | REPAIR | Any metric outside tolerance | `exists i: C_i(x)/k_i > 1` -> P(x;theta) = 0 |
| REPAIR | OPERATE | Fix applied + metric back within tolerance + **auditor verification** | P(x;theta) = 1 again + r(x) shows tightening + auditor confirms |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same failure pattern 3 times at fleet level -> AD | Constraint collision: no feasible theta' exists. Restructure invariant set. |

_The builder cannot certify its own work. The auditor MUST be a different engine than the builder. (Bedrock S8)_

---

## 11. EXECUTION TRACE (During BUILD)

_Append-only record of what happened during build/execution. This is NOT the logbook -- the logbook is created only after auditor certification. This is the build journal that the auditor reviews._

_Built into the engine -- every step writes a trace entry automatically via `writeTraceEntry()` in `lib/trace.ts`._

### Entry Format (per step, per run)

| Field | Description | Format | Required |
|-------|-------------|--------|----------|
| trace_id | Unique entry identifier | UUID (auto-generated) | Yes |
| run_id | Which execution run this belongs to | UUID (one per goal submission or resume) | Yes |
| goal_id | Which goal this trace belongs to | UUID (FK to production_goals) | Yes |
| step_id | Which step was executed | UUID (FK to production_steps) or null for goal-level events | If step-level |
| station_id | Which station was called | Station ID string (e.g., "010-seed") | If step-level |
| step_description | What was attempted | Text -- human-readable | Yes |
| target | Expected outcome | Text -- measurable | If available |
| actual | What happened | Text -- measurable | If available |
| delta | Target vs actual | Number or text -- the gap | If available |
| status | Step outcome | done / failed / skipped / not-callable | Yes |
| error_code | If failed -- machine-readable error type | Text or null | If failed |
| error_message | If failed -- human-readable description | Text or null | If failed |
| tools_used | Which tools/adapters were called | JSON array | Yes (default []) |
| duration_ms | How long this step took | Integer (milliseconds) | If step-level |
| cost_cents | Cost of this step | Integer (cents, default 0) | Yes |
| signed_by | Who/what produced this entry | Agent name (e.g., "outreach-agent") | Yes |
| timestamp | When this happened | ISO-8601 (auto-generated) | Yes |

### Run Summary (per execution run)

Derived from querying execution_trace by run_id:

| Field | Description |
|-------|-------------|
| run_id | UUID for this execution run |
| trigger | What started this run (source field on goal: cron / manual / inbox / agent) |
| orbt_at_start | ORBT state when run began (BUILD on first run, BUILD on resume) |
| steps_total | Count of production_steps for this goal |
| steps_completed | Count where status = 'done' |
| steps_failed | Count where status = 'failed' |
| total_duration_ms | Sum of duration_ms from trace entries for this run_id |
| total_cost_cents | Sum of cost_cents from trace entries for this run_id |
| errors | Count + summary of failed entries |
| learnings | What was new -- feeds to LBB |

### Rules

- **Append-only.** No edits. No deletions. Immutable.
- **Every step gets a trace entry.** No step executes without logging. The `executeStep()` method calls `writeTraceEntry()` after every adapter call.
- **Trace exists during BUILD.** This is NOT the certified logbook.
- **Auditor reviews the trace** to decide certification.
- **Trace persists after certification** -- it becomes evidence inside the logbook's birth certificate.

---

## 12. LOGBOOK (After Certification Only)

_The aircraft's legal identity. Created ONLY when the auditor certifies the process (BUILD -> OPERATE). (Bedrock S8, logbook_schema.yaml)_

**No logbook during BUILD.** The execution trace (S11) is the build journal. The logbook is born when the auditor signs off.

Written by the `POST /goals/:id/certify` endpoint. The line agent that ran the goal does NOT write to this table.

### Rules (from logbook_schema.yaml)

1. No logbook until aircraft is certified (auditor sign-off on BUILD)
2. First entry is always the **birth certificate** (certification record)
3. Append-only. No edits. No deletions. Immutable.
4. Every entry must have all required fields. Incomplete entries rejected.
5. Mechanic must log what they READ before starting (context_loaded)
6. Auditor reviews logbook entries, not source code.
7. The builder CANNOT be the auditor. Different engine required.

### Birth Certificate (first entry -- created by auditor at certification)

| Field | Value |
|-------|-------|
| entry_id | UUID (auto-generated) |
| goal_id | FK to the certified goal |
| heir_ref | JSON: `{ goal_id, line, workpiece_id }` |
| orbt_entered | BUILD |
| orbt_exited | OPERATE |
| visit_path | CERTIFICATION |
| action | "Goal certified -- all stations complete. Auditor: {auditor}" |
| authority | "Bedrock S8 -- auditor certification" |
| gates_passed | `{"imo":true,"ctb":true,"circle":true}` |
| checklist_type | build |
| signed_by | Auditor agent name (from request body) |
| signed_at | Certification timestamp (auto-generated) |
| notes | Optional auditor notes |

### Subsequent Entries (during OPERATE, REPAIR, TROUBLESHOOT/TRAIN)

| Field | Description | Required |
|-------|-------------|----------|
| heir_ref | HEIR reference -- goal_id, line, workpiece_id | Yes |
| orbt_entered | ORBT mode when work started | Yes |
| orbt_exited | ORBT mode when work completed | Yes |
| context_loaded | What was read before work began (heir, orbt, logbook, tier0) | Yes |
| error_ref | Error table reference (null for maintenance) | If repair |
| visit_path | CERTIFICATION / MAINTENANCE / ERROR | Yes |
| strike_count | Recurrence count for this error pattern | Yes |
| action | What the mechanic did | Yes |
| authority | Which Bedrock section authorized this | Yes |
| gates_passed | { imo: bool, ctb: bool, circle: bool } | Yes |
| checklist_type | build / operate / repair / troubleshoot_train | Yes |
| signed_by | Who did the work | Yes |
| signed_at | Immutable timestamp | Yes |

---

## 13. FLEET FAILURE REGISTRY & STRIKE TRACKING

_Strike tracking at FLEET level, not per-goal. The same failure pattern appearing across multiple goals/runs triggers escalation. (Bedrock S6, S8, Mathematical Principle)_

Built into the engine via `lib/fleet-failures.ts`. The `recordFleetFailure()` function handles upsert logic: if the station_id + error_code combination already exists, it increments occurrences and strike_count and appends the goal_id. If strike_count reaches 3, it returns `escalated: true` and the line agent sets ORBT to TROUBLESHOOT_TRAIN.

**Mathematical basis:** A fleet failure IS a comparator violation -- `C_i(x)/k_i > 1` on a specific station+error pattern. The r(x) vector in the execution trace tells the mechanic exactly which comparator exceeded tolerance and by how much. Strike count = how many times this comparator pattern exceeded tolerance across goals. Strike 3 = the tolerance system itself needs restructuring (constraint collision -- no feasible theta' exists).

### Failure Pattern Registry

| Pattern ID | Station | Error Code | First Seen | Occurrences | Goals Affected | Strike Count | Status | Violating Comparator | Ratio |
|-----------|---------|-----------|-----------|-------------|---------------|-------------|--------|---------------------|-------|
| (auto-generated) | station_id | error_code | first_seen | count | JSON array of goal_ids | 0-3 | open / resolved / ad_issued | Which C_i/k_i > 1 | How much > 1 |

Queryable via: `GET /errors` -- returns all open fleet failures sorted by strike_count DESC.

### Strike Rules (Mathematical Interpretation)

- **Strike 1:** REPAIR. The r(x) vector tells you which C_i/k_i > 1. Fix the source that produces C_i(x). If unfixable, recalibrate k_i within feasibility constraints (`theta' in Theta`). Log it. Goal goes to ORBT = REPAIR.
- **Strike 2:** REPAIR with scrutiny. Was root cause actually found? Check: did var(r_i(x)) tighten after the Strike 1 fix? If not, the fix was cosmetic. Goal goes to ORBT = REPAIR.
- **Strike 3:** **STOP.** Constraint collision. No feasible theta' satisfies all constraints simultaneously. The problem isn't a broken part -- it's a broken invariant set. Troubleshoot/Train. Restructure the tolerance definitions, not just the values. Goal goes to ORBT = TROUBLESHOOT_TRAIN. Produce Airworthiness Directive.

### Airworthiness Directive (Strike 3 output)

_When strike 3 fires, the fix goes to ALL processes, not just the one that failed. This updates the template, not just one file._

| Field | Value |
|-------|-------|
| AD Number | AD-[YYYY]-[NNN] |
| Failure Pattern | pattern_id -- station_id + error_code |
| Comparator Violation | Which C_i/k_i exceeded tolerance, magnitude of violation |
| Root Cause | From Troubleshooting Loop S6 -- constraint collision analysis |
| Fix Applied | What changed (invariant restructure, not just k_i adjustment) |
| Scope | ALL processes / specific silo / specific station |
| Template Updated | Yes / No -- if Yes, what section |
| Issued By | Mechanic + auditor sign-off |
| Issued At | Timestamp |

**AD issuance requires:**
1. Root cause identified (Troubleshooting Loop S6 complete)
2. Constraint collision confirmed -- no feasible theta' exists with current invariant set
3. Fix tested on the failing process -- new invariant set produces P(x;theta) = 1
4. Fix verified by auditor (different engine) -- back-propagation clean
5. Template updated if the fix is structural
6. All affected processes notified/updated

---

## MATHEMATICAL ENGINE REFERENCE

_Quick reference for the Tier 0 Mathematical Principle as applied to production line runtime. Full specification: `law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md`._

### The Decision Equation

```
P(x; theta) = 1   if   max_i [ C_i(x) / k_i ] <= 1
P(x; theta) = 0   otherwise
```

This is the ONLY gate function. No secondary evaluation. No override.

### The Diagnostic Vector

```
r(x) = [ C_1(x)/k_1,  C_2(x)/k_2,  ...,  C_n(x)/k_n ]
```

P(x) is the gate decision (scalar, binary). r(x) is the diagnostic output (vector, continuous). Both computed. Both retained.

### Pre-Gate Checks

```
Non-nullity:   sum_i |C_i(x)| > epsilon       (reject zero-signal inputs)
Tolerance floor: k_i >= epsilon_k  for all i   (prevent singularity)
```

### Stability

```
forall t in [1..N]:  P(f^t(x); theta) = 1
AND  var(r_i(x)) over [t-w..t] <= sigma_max   for all i
```

### Global Gate (Certification = Back-Propagation)

```
ACCEPT(x_new) = P(x_new; theta') = 1
                AND  forall x in L: P(x; theta') = 1
```

Adding a new certified goal triggers revalidation of ALL prior certified goals.

### Feasibility

```
theta' in Theta  where  Theta = { theta: forall x in L, r(x;theta) <= 1, k_i >= epsilon_k }
AND  vol(Theta)^(1/n) >= delta
```

If feasible region exists but is knife-edge -> constraint collision. Restructure invariants.

### Domestication

```
max(r(x)) <= alpha  AND  var(r_i(x)) <= sigma_max  ->  stop decomposing
```

The remaining variables can't change the outcome.

### Convergence (Sigma)

| var(r_i) Behavior | Meaning | Action |
|-------------------|---------|--------|
| Decreasing | Real constant. Converging. | Lock. |
| Constant | Phantom constant. Not converging. | Investigate. |
| Increasing | Broken prior constant. Upstream misclassification. | Reclassify. Re-run gate. |

---

## API REFERENCE

All endpoints require `Authorization: Bearer <PRODUCTION_API_KEY>` except where noted.

### POST /goals
Submit a new goal to the production line.

**Request:**
```json
{
  "line": "outreach",
  "workpiece_id": "example-company.com",
  "workpiece_name": "Example Company",
  "source": "manual",
  "inbox_task_id": null
}
```

**Response (201):**
```json
{ "goal_id": "uuid" }
```

**Errors:** 400 (missing fields, unknown line), 401 (unauthorized)

---

### GET /goals
List goals with optional filters.

**Query params:** `line`, `orbt_mode`, `limit` (default 50)

**Response:**
```json
{ "goals": [ { ...goal_row }, ... ] }
```

---

### GET /goals/:goal_id
Goal detail with steps, trace, and logbook.

**Response:**
```json
{
  "goal": { ...goal_row },
  "steps": [ { ...step_row }, ... ],
  "trace": [ { ...trace_row }, ... ],
  "logbook": [ { ...logbook_row }, ... ]
}
```

**Errors:** 404 (not found)

---

### POST /goals/:goal_id/request-certification
Builder signals that all callable stations are complete. Does NOT certify -- just confirms readiness.

**Response:**
```json
{ "status": "awaiting_certification", "goal_id": "uuid", "message": "Auditor must review execution trace and call /certify" }
```

**Errors:** 400 (not in BUILD state), 404

---

### POST /goals/:goal_id/certify
Auditor certifies the goal. Requires a different engine than the builder. **This is the global gate.**

**Request:**
```json
{
  "auditor": "auditor-agent-name",
  "notes": "Optional review notes"
}
```

**Response:**
```json
{ "status": "certified", "goal_id": "uuid", "orbt_mode": "OPERATE", "certified_by": "auditor-agent-name" }
```

**Errors:** 400 (missing auditor, not in BUILD state, steps incomplete, back-propagation failure), 404

---

### POST /goals/:goal_id/resume
Resume a goal after repair. Resets failed steps to pending, sets ORBT back to BUILD.

**Response:**
```json
{ "status": "resumed", "goal_id": "uuid" }
```

**Errors:** 400 (not in REPAIR state), 404

---

### GET /errors
Open fleet failures (squawk sheet). **Includes comparator violation detail.**

**Response:**
```json
{ "errors": [ { ...fleet_failure_row, "violating_comparator": "C_error/k_error", "ratio": 10.0 }, ... ] }
```

Sorted by strike_count DESC, created_at DESC.

---

### GET /sigma/:station_id
Sigma tracking per station. Last 20 runs. **Returns comparator ratios r(x), not just raw values.**

**Response:**
```json
{ "sigma": [ { ...sigma_row, "ratio": 0.57, "variance": 0.003 }, ... ] }
```

---

### GET /health
No auth required. System status.

**Response:**
```json
{ "status": "ok", "goals": 42, "open_fleet_failures": 1, "timestamp": "2026-04-01T00:00:00.000Z" }
```

---

## 14. SESSION LOG

_Every session that touches this process. Links to LBB for detail._

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| 2026-04-01 | Initial HOW_TO_RUN_A_PROCESS.md written from production line source code | none |
| 2026-04-01 | v2.0.0 rewrite: Mathematical engine integrated -- P(x;theta), r(x), sigma variance, tolerance lifecycle, comparator-based diagnostics, global gate at certification | TBD |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-01 |
| Last Modified | 2026-04-01 |
| Version | 2.0.0 |
| Template Version | 4.0.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md |
| Mathematical Engine | imo-creator-v2/law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md |
| Logbook Schema | law/logbook_schema.yaml |
| OSAM Authority | factory/imo-creator/060-production-line (self-contained) |
| Data Flow | factory/imo-creator/060-production-line/src/ (index.ts -> orchestrator.ts -> line-agent.ts -> adapters/) |

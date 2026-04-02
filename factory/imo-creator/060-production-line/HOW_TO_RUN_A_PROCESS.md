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
| 4 | AdapterResponse | Write execution trace entry (S11) to `execution_trace` table -- append-only, every step logged | Trace entry row with status, duration, cost, tools_used | `trace.ts` |
| 5 | Success response | Record sigma metric (duration_ms), mark step `done`, store result JSON, recheck for newly unblocked stations | Next ready stations or all-complete signal | LineAgent |
| 5b | Failure response | Record fleet failure via `fleet-failures.ts` (upsert on station_id + error_code), update goal ORBT to REPAIR (or TROUBLESHOOT_TRAIN on strike 3), halt execution | Failure with strike tracking, goal halted | `fleet-failures.ts` + `orbt.ts` |
| 6 | All callable stations done | Goal marked `completed_at`, trace entry written: "All callable stations complete. Awaiting auditor certification." Builder does NOT flip to OPERATE. | Goal in BUILD state, awaiting auditor | LineAgent |
| 7 | `POST /goals/:id/certify` with auditor field | Auditor (different engine than builder) reviews execution trace, verifies all callable steps done, flips ORBT BUILD -> OPERATE, writes birth certificate to `production_logbook` | OPERATE + logbook entry | Certify endpoint (index.ts) |

### Output

- Certified goal with ORBT = OPERATE
- Complete execution trace (append-only evidence chain)
- Birth certificate in `production_logbook`
- Sigma data per station (duration_ms per run)
- Fleet failure records if any station failed

### Worked Example — A Goal Flowing Through the Line

An enrichment line with 5 stations. A company workpiece enters. Here is what the production line does at runtime:

```
POST /goals { line: "enrichment", workpiece_id: "company-batch-001" }
│
▼
ORCHESTRATOR (hub)
│  Validates line exists
│  Creates goal in D1 (ORBT = BUILD)
│  Creates 5 steps from line definition
│  Routes to Line Agent
│
▼
LINE AGENT (spoke)
│
│  ┌─ Check dependencies ─────────────────────────────────────┐
│  │  Station: SEED (depends_on: [])         → READY          │
│  │  Station: ENRICH (depends_on: [SEED])   → BLOCKED        │
│  │  Station: PEOPLE (depends_on: [ENRICH]) → BLOCKED        │
│  │  Station: EMAIL (depends_on: [PEOPLE])  → BLOCKED        │
│  │  Station: COMPILE (depends_on: [EMAIL]) → BLOCKED        │
│  └───────────────────────────────────────────────────────────┘
│
│  Execute SEED (adapter: http → calls CF Worker)
│  ├── Success → trace entry, sigma recorded, step = done
│  │   Recheck: ENRICH now READY (SEED done)
│  │
│  Execute ENRICH (adapter: cli → calls Python script)
│  │   Inside the process: organize → validate → execute → write
│  │   The line agent doesn't see internals — just waits for result
│  ├── Success → trace, sigma, step = done
│  │   Recheck: PEOPLE now READY (ENRICH done)
│  │
│  Execute PEOPLE (adapter: cli)
│  │   CONDITIONAL: reads workbench, skips slots already filled
│  ├── Success → trace, sigma, step = done
│  │   Recheck: EMAIL now READY (PEOPLE done)
│  │
│  Execute EMAIL (adapter: cli, conditional: only if has_name AND no email)
│  ├── FAILURE → error_code: CAPTCHA_THRESHOLD
│  │   │
│  │   ▼
│  │   Fleet failure recorded: station=EMAIL, code=CAPTCHA_THRESHOLD
│  │   Strike count: 1 (first occurrence)
│  │   Goal ORBT → REPAIR
│  │   Line agent HALTS
│  │   │
│  │   ▼
│  │   Human reviews, fixes proxy config
│  │   POST /goals/:id/resume
│  │   │
│  │   ▼
│  │   EMAIL retried → Success this time
│  │   Recheck: COMPILE now READY
│  │
│  Execute COMPILE (adapter: http → calls CF Worker)
│  ├── Success → all stations done
│  │
│  ▼
│  ALL STATIONS COMPLETE
│  Goal marked: completed_at = now
│  Status: awaiting_certification
│
▼
POST /goals/:id/certify { auditor: "auditor-agent" }
│  Auditor reviews execution trace
│  Confirms all steps done
│  ORBT → OPERATE
│  Birth certificate written to production_logbook
│
▼
GOAL CERTIFIED
│  Workbench updated with enriched data
│  Sigma data available for trend analysis
│  Ready for next goal on the line
```

**Key pattern:** The line agent walks the dependency graph mechanically. It doesn't know what happens inside each station — it calls the adapter and reads the response. Success → next station. Failure → halt + fleet failure + ORBT to REPAIR. All stations done → awaiting certification. The auditor is always a different engine than the builder.

### Circle (Bedrock S5)

- **Sigma tracking** feeds back to process analytics -- tightening sigma = station stabilizing, expanding = upstream broke.
- **Fleet failures** feed back to process repair -- same station+error_code pattern accumulates strikes.
- **Strike 3** produces an Airworthiness Directive (AD) -- fix goes fleet-wide, not just the failing goal.
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
| execution_trace | Append-only build journal -- what happened, when, how long, what cost | goal_id (FK) |
| fleet_failures | Open squawk sheet -- station + error_code patterns, strike counts | station_id + error_code |
| production_logbook | Certified records -- birth certificates, maintenance entries | goal_id (FK) |
| production_sigma | Per-station metrics across runs -- duration_ms, cost_cents, rates | station_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| production_goals | INSERT new goal (Step 1), UPDATE orbt_mode (Step 5b, 7), UPDATE completed_at (Step 6), UPDATE certified_by/certified_at (Step 7) | Steps 1, 5b, 6, 7 |
| production_steps | INSERT all steps (Step 1), UPDATE status/result/error/duration (Steps 3-5b), UPDATE on resume (retry) | Steps 1, 3, 4, 5, 5b |
| execution_trace | INSERT trace entries -- every step, every status change (append-only) | Steps 1, 4, 6 |
| fleet_failures | UPSERT on station_id + error_code -- increment occurrences, strike_count, append goal_id | Step 5b |
| production_logbook | INSERT birth certificate (certification only) | Step 7 |
| production_sigma | INSERT metric per completed station | Step 5 |

### Join Chain

```
production_goals.goal_id                    (spine)
  -> production_steps.goal_id               (1:many -- all stations for this goal)
  -> execution_trace.goal_id                (1:many -- all trace entries for this goal)
  -> production_logbook.goal_id             (1:many -- certification + maintenance records)
  -> fleet_failures.station_id              (many:many via station_id -- cross-goal pattern)
       -> production_sigma.station_id       (1:many -- metrics per station across goals)
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

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| What goals are running on the outreach line? | production_goals | line = 'outreach', orbt_mode |
| Which station failed for goal X? | production_steps | goal_id + status = 'failed' |
| How long did station 300-recon take last 20 runs? | production_sigma | station_id = '300-recon', metric = 'duration_ms' |
| What fleet failures are open? | fleet_failures | status = 'open' |
| Has this goal been certified? | production_goals | certified_by IS NOT NULL |
| What did the auditor write? | production_logbook | goal_id + visit_path = 'CERTIFICATION' |

---

## 6. CONSTANTS & VARIABLES (Bedrock S2)

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

### Variables (fill -- changes every run)

_The values that fill the constants. Different every execution._

- Which goal (goal_id -- UUID per submission)
- Which workpiece (workpiece_id -- the company or entity being processed)
- Which stations succeed vs. fail (step status per run)
- ORBT state per goal (transitions through the state machine)
- Sigma values (duration_ms, cost_cents per station per run)
- Which line is run (outreach, conversion, cl, imo)
- Prior outputs passed to downstream stations (result JSON from completed deps)

---

## 7. STOP CONDITIONS

_When to halt. Not optional. From Troubleshooting Loop (Bedrock S6) and Aviation Model (Bedrock S8)._

| Condition | Action |
|-----------|--------|
| Unknown line submitted | 400 error: `Unknown line: {name}. Available: outreach, conversion, cl, imo` |
| Missing line or workpiece_id | 400 error: `line and workpiece_id are required` |
| Station adapter fails (non-NOT_CALLABLE) | ORBT -> REPAIR, halt goal execution, record fleet failure |
| Strike 3 on same station + error_code pattern | ORBT -> TROUBLESHOOT_TRAIN, halt -- produce Airworthiness Directive |
| Attempt to certify from non-BUILD state | 400 error: `Cannot certify from {orbt_mode}` |
| Steps still incomplete at certification | 400 error: `{count} steps still incomplete` |
| Attempt to resume from non-REPAIR state | 400 error: `Cannot resume from {orbt_mode} -- must be REPAIR` |
| No auditor field on /certify | 400 error: `auditor field is required` |
| Unauthorized request (missing/bad API key) | 401 error: `Unauthorized` |

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

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Auditor (human or agent) | Execution trace to review before certification |
| LBB (Library Barton Brain) | Session learnings ingested after certification |
| Next goal on same workpiece | Prior outputs from certified goal inform next run |
| Dashboard (imo-dashboard) | Goal status, sigma trends, fleet failures for display |
| Airworthiness Directive process | Fleet failure at strike 3 triggers AD authoring |

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
   -> verify: execution_trace has failed entry

6. POST /goals/<goal_id>/resume
   -> expected: { status: "resumed", goal_id: "<uuid>" }
   -> verify: failed steps reset to "pending", orbt_mode back to "BUILD"

7. POST /goals/<goal_id>/certify with body: { "auditor": "smoke-test-auditor" }
   -> expected: { status: "certified", goal_id: "<uuid>", orbt_mode: "OPERATE", certified_by: "smoke-test-auditor" }
   -> verify: production_logbook has birth certificate entry with gates_passed, checklist_type = "build"

8. GET /errors
   -> expected: array of open fleet failures (may be empty if smoke test station succeeded)

9. GET /sigma/010-seed
   -> expected: sigma entries with metric = "duration_ms", ascending run_number
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** Did every component exist where it should? (Worker deployed, D1 migrated, agents registered, adapters present)
2. **Flow:** Did the data reach every step? (Goal -> orchestrator -> line agent -> adapter -> trace)
3. **Change:** Did the transformation happen correctly? (Steps transitioned through statuses, ORBT moved through state machine, logbook written at certification)

If any fails -> that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock S6).

---

## 10. ANALYTICS -- The Dyno Sheet (Bedrock S2 + S5)

_The BUILD->OPERATE gate. No analytics passing tolerance = stays on the dyno._

_This section MUST be defined BEFORE build starts. No analytics spec -> no build authorization (BAR-187)._

### Process Metrics

| Metric | Unit | First Run = Baseline | Target (after baseline) | Tolerance |
|--------|------|---------------------|------------------------|-----------|
| Goals submitted per line per day | count | BASELINE | set after first run | +/- 50% |
| Goals completed (certified) per day | count | BASELINE | set after first run | +/- 50% |
| Goals failed per day | count | BASELINE | set after first run | < 20% of submitted |
| Avg duration per station | ms | BASELINE | set after first run | +/- 30% |
| Cost per goal (sum of step costs) | cents | BASELINE | set after first run | +/- 25% |
| Certification pass rate | % | BASELINE | > 90% | > 80% |
| Fleet failure count (open) | count | BASELINE | < 3 open at any time | < 5 |
| Sigma trend per station (duration_ms) | trend | BASELINE | TIGHTENING | not EXPANDING |

### Tool Scorecard (per Snap-On sub-hub vendor)

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| HTTP Adapter | CF Worker fetch | BASELINE | $0 | BASELINE | BASELINE | first run |
| CLI Adapter | Python exec | BASELINE | $0 | BASELINE | BASELINE | first run |
| SQL Adapter | D1 query | BASELINE | $0 | BASELINE | BASELINE | first run |
| Manual Adapter | N/A | N/A | $0 | N/A | N/A | N/A |

### Sigma Tracking (Bedrock S2)

_After 3+ runs, track whether each metric is tightening, flat, or expanding._

| Metric | Run 1 | Run 2 | Run 3 | Trend | Action |
|--------|-------|-------|-------|-------|--------|
| 010-seed duration_ms | -- | -- | -- | -- | awaiting data |
| 300-recon duration_ms | -- | -- | -- | -- | awaiting data |
| 200-people duration_ms | -- | -- | -- | -- | awaiting data |
| 100-lcs duration_ms | -- | -- | -- | -- | awaiting data |

_Tightening = real constant, process is stabilizing. Flat = phantom, something isn't learning. Expanding = broken, something upstream changed._

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs + **auditor sign-off** |
| OPERATE | REPAIR | Any metric outside tolerance |
| REPAIR | OPERATE | Fix applied + metric back within tolerance + **auditor verification** |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same failure pattern 3 times at fleet level -> AD |

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

_Strike tracking at FLEET level, not per-goal. The same failure pattern appearing across multiple goals/runs triggers escalation. (Bedrock S6, S8)_

Built into the engine via `lib/fleet-failures.ts`. The `recordFleetFailure()` function handles upsert logic: if the station_id + error_code combination already exists, it increments occurrences and strike_count and appends the goal_id. If strike_count reaches 3, it returns `escalated: true` and the line agent sets ORBT to TROUBLESHOOT_TRAIN.

### Failure Pattern Registry

| Pattern ID | Station | Error Code | First Seen | Occurrences | Goals Affected | Strike Count | Status |
|-----------|---------|-----------|-----------|-------------|---------------|-------------|--------|
| (auto-generated) | station_id | error_code | first_seen | count | JSON array of goal_ids | 0-3 | open / resolved / ad_issued |

Queryable via: `GET /errors` -- returns all open fleet failures sorted by strike_count DESC.

### Strike Rules

- **Strike 1:** Repair. Fix at source. Log it. Goal goes to ORBT = REPAIR.
- **Strike 2:** Repair with scrutiny. Was root cause actually found? Goal goes to ORBT = REPAIR.
- **Strike 3:** **STOP.** Troubleshoot/Train. The problem isn't a broken part -- it's a broken understanding. Goal goes to ORBT = TROUBLESHOOT_TRAIN. Produce Airworthiness Directive.

### Airworthiness Directive (Strike 3 output)

_When strike 3 fires, the fix goes to ALL processes, not just the one that failed. This updates the template, not just one file._

| Field | Value |
|-------|-------|
| AD Number | AD-[YYYY]-[NNN] |
| Failure Pattern | pattern_id -- station_id + error_code |
| Root Cause | From Troubleshooting Loop S6 |
| Fix Applied | What changed |
| Scope | ALL processes / specific silo / specific station |
| Template Updated | Yes / No -- if Yes, what section |
| Issued By | Mechanic + auditor sign-off |
| Issued At | Timestamp |

**AD issuance requires:**
1. Root cause identified (Troubleshooting Loop S6 complete)
2. Fix tested on the failing process
3. Fix verified by auditor (different engine)
4. Template updated if the fix is structural
5. All affected processes notified/updated

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
Auditor certifies the goal. Requires a different engine than the builder.

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

**Errors:** 400 (missing auditor, not in BUILD state, steps incomplete), 404

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
Open fleet failures (squawk sheet).

**Response:**
```json
{ "errors": [ { ...fleet_failure_row }, ... ] }
```

Sorted by strike_count DESC, created_at DESC.

---

### GET /sigma/:station_id
Sigma tracking per station. Last 20 runs.

**Response:**
```json
{ "sigma": [ { ...sigma_row }, ... ] }
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

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-01 |
| Last Modified | 2026-04-01 |
| Version | 1.0.0 |
| Template Version | 4.0.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md |
| Logbook Schema | law/logbook_schema.yaml |
| OSAM Authority | factory/imo-creator/060-production-line (self-contained) |
| Data Flow | factory/imo-creator/060-production-line/src/ (index.ts -> orchestrator.ts -> line-agent.ts -> adapters/) |

# PROCESS: Build a Process
## The meta-process — how every process in the system gets built, altitude by altitude, template at every level
### Status: OPERATE
### Business: imo-creator

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-060-BUILD |
| Name | Build a Process |
| Business Silo | imo-creator |
| CTB Position | factory/imo-creator/060-production-line |
| ORBT | OPERATE |
| Strikes | 0 |
| Last Deployed | 2026-04-02 |
| BAR Reference | BAR-195, BAR-196, BAR-187 |
| Deployed URL | not deployed (meta-process, executed by mechanics) |
| Cron | none |
| Runtime | Manual (human + AI agent) |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Without this, processes get built ad-hoc with inconsistent structure. Some have 14 sections, some have 3. Some skip altitudes, some jump straight to code. This ensures every process follows the same altitude descent and template, producing documentation that any mechanic (human or AI) can read, operate, and audit. Every downstream process in the system depends on this meta-process having been run correctly at build time.

---

## 3. IMO --- What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock SS7)

1. **"What triggers this?"** --- A business need: BAR ticket, new capability needed, or a gap identified in the production line.
2. **"How do we get it?"** --- Descend through altitudes (50K to 5K) applying the PROCESS_TEMPLATE v4.0.0 at each level.

### Input

A BAR ticket + business requirement defining what the new process must accomplish. The ticket identifies the business silo, the upstream/downstream dependencies, and the outcome needed.

### Middle

Each step is its own IMO. Each step maps to an altitude in the descent model.

| Step | Altitude | Input | What Happens | Output | Tool Used |
|------|----------|-------|-------------|--------|-----------|
| 1 | 50K | BAR ticket | **Production Line Station.** Open `factory/imo-creator/060-production-line/src/lines.ts`. Add a station entry to the correct line (outreach, conversion, cl, imo) with station ID, dependency graph, adapter type, adapter target, runtime, and ORBT=BUILD. | Station in dependency graph | Production Line Engine |
| 2 | 40K | Station definition | **Process Directory.** Create process directory at canonical silo path. Create 3 required files: PROCESS.md (14 sections from template v4.0.0), heir.yaml (8 fields), CLAUDE.md (agent operating instructions with pre-flight). | Documented process skeleton | PROCESS_TEMPLATE v4.0.0 |
| 3 | 30K | PROCESS.md Middle table | **Step Definitions.** Define internal steps in the Middle table. Each step is its own IMO. Run Tier 0 on every step --- C&V three questions minimum: (1) Can you NAME it? (2) Can you define its FORMAT? (3) Is it the VALUE filling a position? If a step passes cleanly and has never broken, it stays a row. If complex, broken, or sigma not tightening --- descend to 20K. | Steps with IMO defined | Foundational Bedrock |
| 4 | 20K | Steps needing detail | **Step Detail.** Complex or broken steps get their own full 14-section PROCESS.md at `factory/{silo}/{NNN-process}/steps/{step-name}/PROCESS.md`. The parent Middle table points to this document instead of describing the step inline. Parent does not reach into child internals --- CTB rule. | Step-level documentation | PROCESS_TEMPLATE v4.0.0 |
| 5 | 10K | Step tool needs | **Tool Configuration.** Identify tools from Snap-On Toolbox (`imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml`). Enforce well-drinks-first priority: (1) Free data in D1, (2) Free external fetches, (3) Cheap integrations, (4) Top shelf only when free/cheap exhausted. Tools belong to the toolbox, not to any process. | Tool configuration per step | SNAP_ON_TOOLBOX.yaml |
| 6 | 5K | All documentation | **Code.** Write code that implements the documented spec. Code reads from where OSAM says, writes to where OSAM says, uses the tools from SS4, halts on SS7 stop conditions, traces per SS11, produces metrics per SS10. The code is the LAST thing written. | Working code | Language runtime |
| 7 | 5K | Working code | **Smoke Test + Analytics.** Execute smoke test (SS9). Verify Three Primitives: Thing (components exist), Flow (data reaches each step), Change (transformations correct). Establish analytics baseline (SS10) --- defined BEFORE build, measured during first run. | Execution trace + baseline metrics | Production Line Engine |
| 8 | 5K | Execution trace | **Auditor Certification.** Submit execution trace for auditor review. Builder cannot certify own work --- different engine required. Auditor reviews trace, validates all 14 sections present, confirms gates passed (IMO + CTB + Circle). Certify or reject. | Certified process or rejection | Auditor agent |

#### Station Entry Format (Step 1 Detail)

```typescript
{
  id: 'NNN-name',
  name: 'Human Name',
  process_id: 'PROC-NNN',
  phase: 'seed|enrichment|compile',
  depends_on: ['upstream-station-id'],
  adapter_type: 'http|cli|sql|manual',
  adapter_target: 'URL or command',
  runtime: 'CF Worker|Python|Node',
  orbt: 'BUILD'
}
```

#### 40K Required Files (Step 2 Detail)

| Section | What You Define | Bedrock Element |
|---------|----------------|-----------------|
| 1. Identity | What is this thing | HEIR --- the VIN |
| 2. Why This Exists | What breaks without it | The business case |
| 3. IMO | What comes in, what happens, what goes out | IMO SS3 --- the engine |
| 4. What It Grabs Off The Wall | Tools, databases, secrets | Snap-On Toolbox |
| 5. OSAM | Tables read, written, forbidden | Data plumbing |
| 6. Constants & Variables | What's locked, what's fill | C&V SS2 --- the test |
| 7. Stop Conditions | When to halt | Troubleshooting SS6 |
| 8. Dependencies | Upstream and downstream | CTB position |
| 9. Smoke Test | Executable verification | Three Primitives SS1 |
| 10. Analytics | Metrics, targets, sigma | Dyno sheet --- BAR-187 |
| 11. Execution Trace | Append-only build journal | Aviation SS8 |
| 12. Logbook | After certification only | Aviation SS8 |
| 13. Fleet Failures | Strike tracking | Troubleshooting SS6 |
| 14. Session Log | History | LBB |

#### Canonical Silo Paths (Step 2 Detail)

- `factory/imo-creator/{NNN-name}/` --- shared global infrastructure
- `factory/outreach/{NNN-name}/` --- SVG insurance outreach (processes 010-900)
- `factory/real-estate/{NNN-name}/` --- real estate processes
- `factory/personal/{NNN-name}/` --- personal ops

These paths are locked in `law/STRUCTURE_MANIFEST.yaml`. No other root paths are allowed.

#### Between Processes (Step 1 Detail)

Only conditional logic lives between processes on the production line. Read the workbench, check the NULLs, route to the next station. Bedrock does NOT live here. It lives inside the process.

### Output

A certified process operating on the production line: station registered in lines.ts, 3 required files created, all 14 sections documented, code implementing the documented spec, smoke test passing, analytics baselined, and auditor certification complete.

### Worked Example — The Pattern in Action

A process that searches for company data and enriches records. Here is what it looks like when built correctly at each altitude:

```
PRODUCTION LINE (50K)
│
├── Station: Company Enrichment ──depends_on──▶ Station: SEED
│   adapter: cli
│   orbt: OPERATE
│
│   PROCESS INTERNALS (30K — Middle table, each step is its own IMO)
│   │
│   │  Step 1: SEARCHER
│   │  I: Workbench rows (company constants)
│   │  M: Search external source with natural language query
│   │  O: Raw results per company (JSONL)
│   │  C&V: Query pattern = constant. Results = variable.
│   │
│   │  Step 2: ORGANIZER
│   │  I: Raw results
│   │  M: Sort each entry — is this a person name, company name, or garbage?
│   │     Apply C&V three questions to every entry.
│   │  O: Organized piles (has title | has name only | has LinkedIn | garbage)
│   │  C&V: The three questions = constant. The sort result = variable.
│   │
│   │  Step 3: CLASSIFIER
│   │  I: Pile 1 (entries with extractable titles)
│   │  M: Match title to role bucket using taxonomy + fuzzy scoring
│   │  O: Classified candidates with confidence scores
│   │  C&V: Taxonomy = constant. Confidence score = variable.
│   │  Tool: Title Classifier (Snap-On Toolbox)
│   │
│   │  Step 4: MATCHER
│   │  I: Pile 2 (entries with LinkedIn URLs)
│   │  M: Parse slug, match to person name
│   │  O: LinkedIn → person mappings
│   │  C&V: Slug format = constant. Match result = variable.
│   │
│   │  Step 5: WRITER
│   │  I: Validated candidates from steps 3 + 4
│   │  M: Write to workbench with source tracking + timestamp
│   │  O: Updated workbench rows
│   │  C&V: Column names = constant. Values written = variable.
│   │
│   └── PROCESS COMPLETE → updates workbench → returns to production line
│
├── CONDITIONAL LOGIC (between stations — NOT Bedrock, just workbench state)
│   │
│   │  Read workbench for each slot:
│   │    FULL          → skip all remaining stations
│   │    REACHABLE     → skip person search, go to email/LinkedIn stations
│   │    NAME_ONLY     → skip person search, go to email + LinkedIn stations
│   │    PATTERN_READY → go to person search (name needed to apply pattern)
│   │    EMPTY         → go to person search
│   │
├── Station: Person Search ──depends_on──▶ Station: Company Enrichment
│   (same internal pattern: organize → validate → execute → write)
│
├── Station: Email Discovery ──depends_on──▶ Station: Person Search
│   (conditional: only runs if has_name = 1 AND has_email = 0)
│
├── Station: LinkedIn Discovery ──depends_on──▶ Station: Person Search
│   (conditional: only runs if has_name = 1 AND has_linkedin = 0)
│
└── Station: Pipeline Compiler ──depends_on──▶ Email + LinkedIn
    (all enrichment complete → compile outreach message)
```

**Key pattern:** Bedrock lives INSIDE each process (the steps). Between processes, only conditional logic — read the workbench, check what's NULL, route to the next station. The intelligence is in the data, not in the routing.

### Circle (Bedrock SS5)

Sigma tracking from runtime feeds back to process documentation. Metrics that expand indicate something upstream changed or was misclassified. Strike 3 on the same build failure pattern produces an Airworthiness Directive that updates the PROCESS_TEMPLATE itself --- the meta-process improves the meta-process.

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches. A mechanic reads this and knows exactly what to set up before the process can run._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| N/A | N/A | N/A | N/A | This is a documentation/build meta-process --- no direct database access |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| PROCESS_TEMPLATE v4.0.0 | Document | Free | none | The 14-section template applied at 40K and 20K |
| FOUNDATIONAL_BEDROCK.md | Document | Free | none | The engine --- SS1-8: Three Primitives, C&V, IMO, CTB, Circle, Troubleshooting, Tier 0, Aviation |
| SNAP_ON_TOOLBOX.yaml | Document | Free | none | The 27 tool sub-hubs and vendor registry --- consulted at 10K |
| STRUCTURE_MANIFEST.yaml | Document | Free | none | The CTB file structure --- canonical silo paths, required files |
| logbook_schema.yaml | Document | Free | none | Logbook entry format for post-certification |
| Production Line Engine | Code | Free | none | lines.ts station registry and dependency graph |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| N/A | N/A | N/A | No secrets required for the build meta-process |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 --- always first
2. Free external fetches (CF Worker fetch, no proxy) --- second
3. Cheap integrations (Composio routes) --- third
4. Top shelf (per-call APIs, proxy services) --- only when free/cheap exhausted

---

## 5. OSAM --- Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins. What's forbidden._

### READ Access

| Path | What It Provides | Join Key |
|------|-----------------|----------|
| `Barton-Processes/law/PROCESS_TEMPLATE.md` | 14-section template structure | N/A |
| `imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md` | Engine (SS1-8) | N/A |
| `imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml` | 27 tool sub-hubs, vendor registry | Tool # |
| `Barton-Processes/law/STRUCTURE_MANIFEST.yaml` | Canonical silo paths, required files | N/A |
| `Barton-Processes/law/logbook_schema.yaml` | Logbook entry format | N/A |

### WRITE Access

| Path | What It Writes | When |
|------|---------------|------|
| `factory/imo-creator/060-production-line/src/lines.ts` | New station entry | Step 1 (50K) |
| `factory/{canonical-silo}/{NNN-name}/PROCESS.md` | 14-section process documentation | Step 2 (40K) |
| `factory/{canonical-silo}/{NNN-name}/heir.yaml` | HEIR identity (8 fields) | Step 2 (40K) |
| `factory/{canonical-silo}/{NNN-name}/CLAUDE.md` | Agent operating instructions | Step 2 (40K) |
| `factory/{silo}/{NNN-name}/steps/{step}/PROCESS.md` | Step-level detail documentation | Step 4 (20K) |
| `factory/{silo}/{NNN-name}/src/` | Implementation code | Step 6 (5K) |

### Forbidden Paths

| Action | Why |
|--------|-----|
| Creating processes outside canonical silo paths | Violates STRUCTURE_MANIFEST.yaml --- only factory/imo-creator, factory/outreach, factory/real-estate, factory/personal are allowed |
| Skipping altitudes (e.g., writing code at 5K before documenting at 30K) | Violates the altitude descent model --- the constant of this process |
| Builder certifying own work | Violates Aviation Model SS8 --- builder and auditor must be different engines |
| Modifying the 4 locked files | No LLM may modify FOUNDATIONAL_BEDROCK.md, FCE.md, SKILL.md, or STRUCTURE_MANIFEST.yaml |
| Writing logbook entries before certification | Violates Aviation Model --- logbook is born at auditor sign-off, not before |

### What Lives Where

| Altitude | What | Lives At |
|----------|------|----------|
| 50K | Production line | `factory/imo-creator/060-production-line/src/lines.ts` |
| 50K | Line engine | `factory/imo-creator/060-production-line/` |
| 40K | Process docs | `factory/{canonical-silo}/{NNN-name}/PROCESS.md` |
| 30K | Step definitions | Section 3 Middle table in PROCESS.md |
| 20K | Step detail | `factory/{silo}/{NNN-name}/steps/{step}/PROCESS.md` |
| 10K | Tool config | Section 4 + `imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml` |
| 5K | Code | `factory/{silo}/{NNN-name}/src/` |
| ALL | Template | `Barton-Processes/law/PROCESS_TEMPLATE.md` v4.0.0 |
| ALL | Engine | `imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md` |
| ALL | Toolbox | `imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml` |
| ALL | Logbook schema | `Barton-Processes/law/logbook_schema.yaml` |

---

## 6. CONSTANTS & VARIABLES (Bedrock SS2)

### Constants (structure --- never changes)

_What is fixed regardless of what data flows through. If this changes, you're redesigning, not operating._

- **The altitude model (50K to 5K)** --- the descent order is the constant. Six altitudes, always in order, never skipped.
- **The template (14 sections)** --- every process gets all 14 sections from PROCESS_TEMPLATE v4.0.0.
- **The Foundational Bedrock (C&V + IMO + CTB + Circle)** --- applied simultaneously at every gate, not sequentially.
- **The descent order** --- never skip an altitude. You never build at 5K before documenting at 30K.
- **Auditor separation** --- builder cannot certify own work. Different engine required.
- **Canonical silo paths** --- factory/imo-creator, factory/outreach, factory/real-estate, factory/personal. Locked in STRUCTURE_MANIFEST.yaml.
- **Required files (3)** --- every process directory must have PROCESS.md, heir.yaml, CLAUDE.md.
- **Well-drinks-first tool priority** --- free before cheap before top shelf.
- **Station entry constants** --- station ID (never changes), dependency graph (which stations must complete first), adapter type (how the production line calls this process).
- **Between-process logic** --- only conditional routing. Read workbench, check NULLs, route. Bedrock lives inside the process, not between them.

### Variables (fill --- changes every run)

_The values that fill the constants. Different every execution._

- **Which process is being built** --- the specific BAR ticket and business need
- **Which business silo it belongs to** --- outreach, imo-creator, real-estate, personal
- **Which tools it needs** --- selected from Snap-On Toolbox at 10K based on the process's requirements
- **How many internal steps** --- some processes have 3, some have 12
- **Which steps need 20K detail** --- only steps that are complex, broken, or where sigma isn't tightening
- **ORBT state** --- BUILD until certification, then OPERATE
- **Which workpiece is being processed** --- the data flowing through at runtime

---

## 7. STOP CONDITIONS

_When to halt. Not optional. From Troubleshooting Loop (Bedrock SS6) and Aviation Model (Bedrock SS8)._

| Condition | Action |
|-----------|--------|
| Can't answer two-question intake ("What triggers this?" + "How do we get it?") | HALT --- process isn't defined, ask Dave |
| No BAR ticket | HALT --- no authorization to build |
| Skipped an altitude | HALT --- go back and fill the gap |
| Builder attempting self-certification | HALT --- assign different engine as auditor |
| C&V three questions can't be answered for a step | HALT --- step isn't ready for the Middle table |
| Canonical silo path doesn't exist in STRUCTURE_MANIFEST.yaml | HALT --- invalid placement |
| Strike 3 on same build failure pattern | Troubleshoot/Train --- produce Airworthiness Directive that updates the template |
| Sigma expanding on a step during build | HALT --- something upstream was misclassified. Re-run that gate. |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| BAR ticket | Authorization and requirement definition | DONE (per-invocation) |
| FOUNDATIONAL_BEDROCK.md | The engine --- SS1-8 | DONE (locked, immutable) |
| PROCESS_TEMPLATE v4.0.0 | The 14-section template | DONE (locked at v4.0.0) |
| STRUCTURE_MANIFEST.yaml | Canonical silo paths, required files | DONE (locked) |
| SNAP_ON_TOOLBOX.yaml | 27 tool sub-hubs, vendor registry | DONE (gated) |
| logbook_schema.yaml | Logbook entry format | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Production Line Engine | Station definition in lines.ts with dependencies |
| All processes built using this meta-process | The certified PROCESS.md, heir.yaml, CLAUDE.md |
| Auditor agent | Execution trace from SS11 to review for certification |
| LBB | Session learnings ingested after build |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output. Not prose --- run these._

```
1. Process directory exists at canonical silo path
   → expected: factory/{silo}/{NNN-name}/ exists

2. PROCESS.md has all 14 sections
   → expected: grep for "## 1. IDENTITY" through "## 14. SESSION LOG" — all 14 present

3. heir.yaml has 8 fields
   → expected: sovereign_ref, hub_id, sub_hub, component, version, created_at, orbt, cc_layer all present

4. CLAUDE.md exists with pre-flight
   → expected: file exists, contains "Bedrock Pre-Flight" or equivalent gate checklist

5. Station added to lines.ts with dependencies
   → expected: station ID matches PROC-NNN, depends_on array populated, orbt = 'BUILD'

6. Tier 0 run on every internal step (C&V three questions minimum)
   → expected: every Middle table row can answer: NAME it? FORMAT it? VALUE filling a position?

7. Code implements documented spec (5K matches 30K-40K documentation)
   → expected: OSAM read/write paths match code, tools match Section 4, stop conditions implemented

8. Auditor can review execution trace
   → expected: Section 11 populated with append-only entries, all steps traced
```

**Three Primitives Check (Bedrock SS1):**
1. **Thing:** Did every component exist where it should? (directory, files, station entry)
2. **Flow:** Did the data reach every step? (BAR ticket to station to docs to code to trace)
3. **Change:** Did the transformation happen correctly? (business need became certified process)

If any fails --- that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock SS6).

### The Descent Checklist

Before building ANY process, walk this checklist:

```
[ ] 50K — Station added to production line (lines.ts)
[ ] 50K — Dependencies defined (what must complete first)
[ ] 40K — PROCESS.md created (14 sections, template v4.0.0)
[ ] 40K — heir.yaml + CLAUDE.md created (required per STRUCTURE_MANIFEST.yaml)
[ ] 30K — Middle table defined (each step is its own IMO)
[ ] 30K — Tier 0 run on every step (C&V three questions minimum)
[ ] 20K — Complex/broken steps get their own PROCESS.md
[ ] 10K — Tools identified from Snap-On Toolbox
[ ] 10K — Tool priority enforced (well drinks first)
[ ] 5K  — Code written (implements the documentation)
[ ] 5K  — Smoke test passes (section 9)
[ ] 5K  — Analytics defined BEFORE build (BAR-187)
[ ] ALL — Execution trace recorded (section 11)
[ ] ALL — Submit for auditor certification (builder ≠ auditor)
```

---

## 10. ANALYTICS --- The Dyno Sheet (Bedrock SS2 + SS5)

_The BUILD to OPERATE gate. No analytics passing tolerance = stays on the dyno. This section MUST be defined BEFORE build starts. No analytics spec = no build authorization (BAR-187)._

### Process Metrics

_Define BEFORE build starts. These are the instruments on the dyno. Each metric is a constant (named, formatted). The value each run is the variable._

| Metric | Unit | First Run = Baseline | Target (after baseline) | Tolerance |
|--------|------|---------------------|------------------------|-----------|
| Time from BAR to certified process | hours | BASELINE | set after first run | +/- 25% |
| Number of altitudes documented | count (max 6) | BASELINE | 6/6 | must be 6/6 |
| Audit pass rate on first submission | % | BASELINE | set after first run | > 80% |
| Strike count during build | count | BASELINE | 0 | <= 1 |
| 14-section completeness | count (max 14) | BASELINE | 14/14 | must be 14/14 |
| Required files created | count (max 3) | BASELINE | 3/3 | must be 3/3 |

### Sigma Tracking (Bedrock SS2)

_After 3+ builds, track whether each metric is tightening, flat, or expanding._

| Metric | Build 1 | Build 2 | Build 3 | Trend | Action |
|--------|---------|---------|---------|-------|--------|
| Time from BAR to certified | | | | | |
| Audit pass rate | | | | | |
| Strike count | | | | | |

_Tightening = real constant, the build process is stabilizing. Flat = phantom, something isn't learning. Expanding = broken, something upstream changed._

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs + **auditor sign-off** |
| OPERATE | REPAIR | Any metric outside tolerance |
| REPAIR | OPERATE | Fix applied + metric back within tolerance + **auditor verification** |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same failure pattern 3 times at fleet level --- AD issued |

_The builder cannot certify its own work. The auditor MUST be a different engine than the builder. (Bedrock SS8)_

---

## 11. EXECUTION TRACE (During BUILD)

_Append-only record of what happened during build/execution. This is NOT the logbook --- the logbook is created only after auditor certification. This is the build journal that the auditor reviews._

_Every run, every step, every result gets traced here. The auditor reads this to decide: certify or reject._

### Entry Format (per step, per run)

| Field | Description | Format | Required |
|-------|-------------|--------|----------|
| trace_id | Unique entry identifier | UUID | Yes |
| run_id | Which execution run this belongs to | UUID (one per goal/batch) | Yes |
| step | What was attempted | Station ID or action name | Yes |
| target | Expected outcome (defined in SS10 metrics) | Text --- measurable | Yes |
| actual | What happened | Text --- measurable | Yes |
| delta | Target vs actual | Number or text --- the gap | Yes |
| status | Step outcome | done / failed / skipped | Yes |
| error_code | If failed --- machine-readable error type | Text or null | If failed |
| error_message | If failed --- human-readable description | Text or null | If failed |
| tools_used | Which Snap-On sub-hub tools were called | JSON array of tool numbers | Yes |
| duration_ms | How long this step took | Integer (milliseconds) | Yes |
| cost_cents | Cost of this step | Integer (cents) | Yes |
| timestamp | When this happened | ISO-8601 | Yes |
| signed_by | Who/what produced this entry | Agent name or "manual" | Yes |

### Run Summary (per execution run)

| Field | Description |
|-------|-------------|
| run_id | UUID for this execution run |
| trigger | What started this run (BAR ticket / manual) |
| orbt_at_start | ORBT state when run began |
| steps_total | How many steps planned |
| steps_completed | How many passed |
| steps_failed | How many failed |
| total_duration_ms | Wall clock time for full run |
| total_cost_cents | Sum of all step costs |
| errors | Count + summary of failures |
| learnings | What was new --- feeds to LBB |

### Rules

- **Append-only.** No edits. No deletions. Immutable.
- **Every step gets a trace entry.** No step executes without logging.
- **Trace exists during BUILD.** This is NOT the certified logbook.
- **Auditor reviews the trace** to decide certification.
- **Trace persists after certification** --- it becomes evidence inside the logbook's birth certificate.

---

## 12. LOGBOOK (After Certification Only)

_The aircraft's legal identity. Created ONLY when the auditor certifies the process (BUILD to OPERATE). (Bedrock SS8, logbook_schema.yaml)_

**No logbook during BUILD.** The execution trace (SS11) is the build journal. The logbook is born when the auditor signs off.

### Rules (from logbook_schema.yaml)

1. No logbook until aircraft is certified (auditor sign-off on BUILD)
2. First entry is always the **birth certificate** (certification record)
3. Append-only. No edits. No deletions. Immutable.
4. Every entry must have all required fields. Incomplete entries rejected.
5. Mechanic must log what they READ before starting (context_loaded)
6. Auditor reviews logbook entries, not source code.
7. The builder CANNOT be the auditor. Different engine required.

### Birth Certificate (first entry --- created by auditor at certification)

| Field | Value |
|-------|-------|
| heir_ref | Full HEIR record for the built process |
| orbt_entered | BUILD |
| orbt_exited | OPERATE |
| action | "Process certified --- airworthiness confirmed" |
| authority | "Auditor certification per Tier 0 gate stack" |
| gates_passed | { imo: true, ctb: true, circle: true } |
| checklist_type | build_checklist |
| checklist_items | Full descent checklist with all items PASS |
| execution_trace_ref | Link to SS11 trace (evidence the auditor reviewed) |
| signed_by | Auditor agent (MUST be different engine than builder) |
| signed_at | Certification timestamp |

### Subsequent Entries (during OPERATE, REPAIR, TROUBLESHOOT/TRAIN)

| Field | Description | Required |
|-------|-------------|----------|
| heir_ref | HEIR reference --- hub_id, sub_hub, component | Yes |
| orbt_entered | ORBT mode when work started | Yes |
| orbt_exited | ORBT mode when work completed | Yes |
| context_loaded | What was read before work began (heir, orbt, logbook, tier0) | Yes |
| error_ref | Error table reference (null for maintenance) | If repair |
| visit_path | MAINTENANCE or ERROR | Yes |
| strike_count | Recurrence count for this error pattern | Yes |
| action | What the mechanic did | Yes |
| authority | Which Bedrock section authorized this | Yes |
| gates_passed | { imo: bool, ctb: bool, circle: bool } | Yes |
| checklist_type | operate / repair / troubleshoot_train | Yes |
| signed_by | Who did the work | Yes |
| signed_at | Immutable timestamp | Yes |

---

## 13. FLEET FAILURE REGISTRY & STRIKE TRACKING

_Strike tracking at FLEET level, not per-goal. The same failure pattern appearing across multiple process builds triggers escalation. (Bedrock SS6, SS8)_

### Failure Pattern Registry

| Pattern ID | Station | Error Code | First Seen | Occurrences | Processes Affected | Strike Count | Status |
|-----------|---------|-----------|-----------|-------------|-------------------|-------------|--------|
| FP-001 | 40K-docs | missing-heir-yaml | | 0 | | 0 | OPEN |
| FP-002 | 40K-docs | wrong-silo-path | | 0 | | 0 | OPEN |
| FP-003 | 30K-steps | missing-cv-test | | 0 | | 0 | OPEN |
| FP-004 | 50K-station | missing-dependency | | 0 | | 0 | OPEN |
| FP-005 | 5K-code | code-before-docs | | 0 | | 0 | OPEN |

### Strike Rules

- **Strike 1:** Repair. Fix at source. Log it.
- **Strike 2:** Repair with scrutiny. Was root cause actually found?
- **Strike 3:** **STOP.** Troubleshoot/Train. The problem isn't a broken part --- it's a broken understanding. Produce AD that updates the PROCESS_TEMPLATE itself.

### Airworthiness Directive (Strike 3 output)

_When strike 3 fires, the fix goes to ALL processes, not just the one that failed. This updates the template, not just one file._

| Field | Value |
|-------|-------|
| AD Number | AD-[YYYY]-[NNN] |
| Failure Pattern | FP-[NNN] --- [description] |
| Root Cause | [from Troubleshooting Loop SS6] |
| Fix Applied | [what changed] |
| Scope | ALL processes / [specific silo] / [specific station] |
| Template Updated | Yes / No --- if Yes, what section |
| Issued By | [mechanic + auditor sign-off] |
| Issued At | [timestamp] |

**AD issuance requires:**
1. Root cause identified (Troubleshooting Loop SS6 complete)
2. Fix tested on the failing process
3. Fix verified by auditor (different engine)
4. Template updated if the fix is structural
5. All affected processes notified/updated

---

## 14. SESSION LOG

_Every session that touches this process. Links to LBB for detail._

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| 2026-04-02 | v1.0.0 --- initial HOW_TO_BUILD_A_PROCESS.md created with altitude model | none |
| 2026-04-01 | v2.0.0 --- rewritten as proper 14-section PROCESS.md from PROCESS_TEMPLATE v4.0.0 | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-02 |
| Last Modified | 2026-04-01 |
| Version | 2.0.0 |
| Template Version | 4.0.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md (parent repo) |
| Logbook Schema | Barton-Processes/law/logbook_schema.yaml |
| OSAM Authority | Section 5 of this document (self-contained meta-process) |
| Data Flow | N/A --- meta-process, no runtime data flow |
| Authority | Dave Barton --- the architect |

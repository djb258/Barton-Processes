# PROCESS: Build a Process
## The meta-process --- how every process in the system gets built, altitude by altitude, template at every level
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

With the mathematical engine integrated, every constant identified during the build now carries a comparator function and tolerance threshold --- not just a name and format. The BUILD-to-OPERATE gate is no longer "it seems to work" --- it is P(x;theta) = 1 for 3 consecutive runs, computed from the diagnostic vector. The math removes opinion from certification.

---

## 3. IMO --- What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock SS7)

1. **"What triggers this?"** --- A business need: BAR ticket, new capability needed, or a gap identified in the production line.
2. **"How do we get it?"** --- Descend through altitudes (50K to 5K) applying the PROCESS_TEMPLATE v4.0.0 at each level.

### Input

A BAR ticket + business requirement defining what the new process must accomplish. The ticket identifies the business silo, the upstream/downstream dependencies, and the outcome needed.

### Middle

Each step is its own IMO. Each step maps to an altitude in the descent model.

**Mathematical layer per step:** Every step in the Middle table now includes three additional elements drawn from the Tier 0 Mathematical Principle:

1. **Comparators C_i** --- What measurable structural rules must this step's output satisfy? Each C_i must be grounded in a primitive (Thing, Flow, or Change) and satisfy all four comparator properties: measurable, deterministic, representation-invariant, temporally complete.
2. **Initial tolerances k_i** --- What are the tolerance thresholds for each comparator? These start as educated guesses (Phase 1) and calibrate from failures (Phase 2). Never below the tolerance floor epsilon_k.
3. **Decision function P(x;theta)** --- What must be true for this step to pass? P(x;theta) = 1 if max_i[C_i(x)/k_i] <= 1, else 0. No secondary evaluation. No override.

| Step | Altitude | Input | What Happens | Output | Tool Used |
|------|----------|-------|-------------|--------|-----------|
| 1 | 50K | BAR ticket | **Production Line Station.** Open `factory/imo-creator/060-production-line/src/lines.ts`. Add a station entry to the correct line (outreach, conversion, cl, imo) with station ID, dependency graph, adapter type, adapter target, runtime, and ORBT=BUILD. | Station in dependency graph | Production Line Engine |
| 2 | 40K | Station definition | **Process Directory.** Create process directory at canonical silo path. Create 3 required files: PROCESS.md (14 sections from template v4.0.0), heir.yaml (8 fields), CLAUDE.md (agent operating instructions with pre-flight). | Documented process skeleton | PROCESS_TEMPLATE v4.0.0 |
| 3 | 30K | PROCESS.md Middle table | **Step Definitions with Comparators.** Define internal steps in the Middle table. Each step is its own IMO. Run Tier 0 on every step --- this now means: (a) C&V three questions minimum: (1) Can you NAME it? (2) Can you define its FORMAT? (3) Is it the VALUE filling a position? AND (b) Define comparator functions C_i for each constant identified, (c) Set initial tolerance thresholds k_i (educated guesses --- Phase 1), (d) Verify all four comparator properties (measurable, deterministic, representation-invariant, temporally complete). If a step passes cleanly and has never broken, it stays a row. If complex, broken, or sigma not tightening --- descend to 20K. | Steps with IMO + comparators defined | Foundational Bedrock + Mathematical Principle |
| 4 | 20K | Steps needing detail | **Step Detail.** Complex or broken steps get their own full 14-section PROCESS.md at `factory/{silo}/{NNN-process}/steps/{step-name}/PROCESS.md`. The parent Middle table points to this document instead of describing the step inline. Parent does not reach into child internals --- CTB rule. | Step-level documentation | PROCESS_TEMPLATE v4.0.0 |
| 5 | 10K | Step tool needs | **Tool Configuration.** Identify tools from Snap-On Toolbox (`imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml`). Enforce well-drinks-first priority: (1) Free data in D1, (2) Free external fetches, (3) Cheap integrations, (4) Top shelf only when free/cheap exhausted. Tools belong to the toolbox, not to any process. | Tool configuration per step | SNAP_ON_TOOLBOX.yaml |
| 6 | 5K | All documentation | **Code.** Write code that implements the documented spec. Code reads from where OSAM says, writes to where OSAM says, uses the tools from SS4, halts on SS7 stop conditions, traces per SS11, produces metrics per SS10. The code is the LAST thing written. | Working code | Language runtime |
| 7 | 5K | Working code | **Smoke Test + Analytics.** Execute smoke test (SS9). Verify Three Primitives: Thing (components exist), Flow (data reaches each step), Change (transformations correct). Establish analytics baseline (SS10) --- compute the diagnostic vector r(x) for the first run. Each metric IS a comparator C_i with tolerance k_i. The decision function P(x;theta) must equal 1 for 3 consecutive runs to pass the BUILD-to-OPERATE gate. | Execution trace + diagnostic vector + baseline metrics | Production Line Engine |
| 8 | 5K | Execution trace | **Auditor Certification.** Submit execution trace for auditor review. Builder cannot certify own work --- different engine required. Auditor reviews trace, validates all 14 sections present, confirms gates passed (IMO + CTB + Circle), verifies P(x;theta) = 1 for 3 consecutive runs with var(r_i(x)) <= sigma_max. Certify or reject. | Certified process or rejection | Auditor agent |

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
| 6. Constants & Variables | What's locked, what's fill, comparators + tolerances | C&V SS2 + Mathematical Principle |
| 7. Stop Conditions | When to halt | Troubleshooting SS6 |
| 8. Dependencies | Upstream and downstream | CTB position |
| 9. Smoke Test | Executable verification | Three Primitives SS1 |
| 10. Analytics | Metrics as comparators, tolerances, decision function | Dyno sheet --- Mathematical Principle |
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

A certified process operating on the production line: station registered in lines.ts, 3 required files created, all 14 sections documented, code implementing the documented spec, smoke test passing, analytics baselined with comparators and tolerances defined, diagnostic vector r(x) computed, P(x;theta) = 1 for 3 consecutive runs, and auditor certification complete.

### Worked Example --- The Pattern in Action

A process that searches for company data and enriches records. Here is what it looks like when built correctly at each altitude, now showing where the mathematical engine lives:

```
PRODUCTION LINE (50K)
|
+-- Station: Company Enrichment --depends_on--> Station: SEED
|   adapter: cli
|   orbt: OPERATE
|
|   PROCESS INTERNALS (30K -- Middle table, each step is its own IMO)
|   |
|   |  Step 1: SEARCHER
|   |  I: Workbench rows (company constants)
|   |  M: Search external source with natural language query
|   |  O: Raw results per company (JSONL)
|   |  C&V: Query pattern = constant. Results = variable.
|   |  C_i: C_1 = results_returned_count (Thing), C_2 = query_latency_ms (Flow)
|   |  k_i: k_1 = 50 (max results), k_2 = 5000 (max ms)
|   |  P(x;theta): max(C_1/k_1, C_2/k_2) <= 1 --> pass
|   |
|   |  Step 2: ORGANIZER
|   |  I: Raw results
|   |  M: Sort each entry -- is this a person name, company name, or garbage?
|   |     Apply C&V three questions to every entry.
|   |  O: Organized piles (has title | has name only | has LinkedIn | garbage)
|   |  C&V: The three questions = constant. The sort result = variable.
|   |  C_i: C_1 = garbage_rate (Change), C_2 = unclassified_rate (Change)
|   |  k_i: k_1 = 0.30 (max 30% garbage), k_2 = 0.05 (max 5% unclassified)
|   |  P(x;theta): max(C_1/k_1, C_2/k_2) <= 1 --> pass
|   |
|   |  Step 3: CLASSIFIER
|   |  I: Pile 1 (entries with extractable titles)
|   |  M: Match title to role bucket using taxonomy + fuzzy scoring
|   |  O: Classified candidates with confidence scores
|   |  C&V: Taxonomy = constant. Confidence score = variable.
|   |  C_i: C_1 = low_confidence_rate (Change), C_2 = misclassification_rate (Change)
|   |  k_i: k_1 = 0.20, k_2 = 0.05
|   |  P(x;theta): max(C_1/k_1, C_2/k_2) <= 1 --> pass
|   |  Tool: Title Classifier (Snap-On Toolbox)
|   |
|   |  Step 4: MATCHER
|   |  I: Pile 2 (entries with LinkedIn URLs)
|   |  M: Parse slug, match to person name
|   |  O: LinkedIn --> person mappings
|   |  C&V: Slug format = constant. Match result = variable.
|   |  C_i: C_1 = match_failure_rate (Change)
|   |  k_i: k_1 = 0.10 (max 10% failures)
|   |  P(x;theta): C_1/k_1 <= 1 --> pass
|   |
|   |  Step 5: WRITER
|   |  I: Validated candidates from steps 3 + 4
|   |  M: Write to workbench with source tracking + timestamp
|   |  O: Updated workbench rows
|   |  C&V: Column names = constant. Values written = variable.
|   |  C_i: C_1 = write_failure_count (Thing), C_2 = orphan_row_count (Thing)
|   |  k_i: k_1 = 0, k_2 = 0 (zero tolerance -- writes must succeed)
|   |  P(x;theta): max(C_1/k_1, C_2/k_2) <= 1 --> pass
|   |  Note: k_i = 0 violates tolerance floor. In practice, set k_i = epsilon_k
|   |        (e.g., 0.001) so the math doesn't produce singularities.
|   |
|   +-- PROCESS COMPLETE --> updates workbench --> returns to production line
|   |
|   |  PROCESS-LEVEL DIAGNOSTIC VECTOR:
|   |  r(x) = [C_1(x)/k_1, C_2(x)/k_2, ..., C_n(x)/k_n] across all steps
|   |  P(x;theta) = 1 if max(r(x)) <= 1 -- the process passes
|   |  Stability: P must hold for 3 consecutive runs with var(r_i) <= sigma_max
|   |  Domestication: max(r(x)) <= alpha AND var(r_i) <= sigma_max --> stop decomposing
|   |
+-- CONDITIONAL LOGIC (between stations -- NOT Bedrock, just workbench state)
|   |
|   |  Read workbench for each slot:
|   |    FULL          --> skip all remaining stations
|   |    REACHABLE     --> skip person search, go to email/LinkedIn stations
|   |    NAME_ONLY     --> skip person search, go to email + LinkedIn stations
|   |    PATTERN_READY --> go to person search (name needed to apply pattern)
|   |    EMPTY         --> go to person search
|   |
+-- Station: Person Search --depends_on--> Station: Company Enrichment
|   (same internal pattern: organize --> validate --> execute --> write)
|
+-- Station: Email Discovery --depends_on--> Station: Person Search
|   (conditional: only runs if has_name = 1 AND has_email = 0)
|
+-- Station: LinkedIn Discovery --depends_on--> Station: Person Search
|   (conditional: only runs if has_name = 1 AND has_linkedin = 0)
|
+-- Station: Pipeline Compiler --depends_on--> Email + LinkedIn
    (all enrichment complete --> compile outreach message)
```

**Key pattern:** Bedrock lives INSIDE each process (the steps). Between processes, only conditional logic --- read the workbench, check what's NULL, route to the next station. The intelligence is in the data, not in the routing. The mathematical engine (P, r, k) lives at the step level and aggregates to the process level.

### Circle (Bedrock SS5)

Sigma tracking from runtime feeds back to process documentation. The diagnostic vector r(x) computed each run identifies which comparators are tightening (real constant), flat (phantom), or expanding (broken upstream). Strike 3 on the same build failure pattern produces an Airworthiness Directive that updates the PROCESS_TEMPLATE itself --- the meta-process improves the meta-process. Tolerances recalibrate through the three-phase lifecycle: Phase 1 educated guess, Phase 2 failure-driven tightening, Phase 3 stabilization/domestication.

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
| TIER0_MATHEMATICAL_PRINCIPLE.md | Document | Free | none | The math --- decision equation P(x;theta), diagnostic vector r(x), stability, global gate, feasibility, tolerance lifecycle, bolt pattern |
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
| `imo-creator-v2/law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md` | Decision equation, diagnostic vector, tolerance lifecycle, bolt pattern | N/A |
| `imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml` | 27 tool sub-hubs, vendor registry | Tool # |
| `Barton-Processes/law/STRUCTURE_MANIFEST.yaml` | Canonical silo paths, required files | N/A |
| `Barton-Processes/law/logbook_schema.yaml` | Logbook entry format | N/A |

### WRITE Access

| Path | What It Writes | When |
|------|---------------|------|
| `factory/imo-creator/060-production-line/src/lines.ts` | New station entry | Step 1 (50K) |
| `factory/{canonical-silo}/{NNN-name}/PROCESS.md` | 14-section process documentation with comparators + tolerances | Step 2 (40K) |
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
| Declaring tolerances without comparator properties | Violates Mathematical Principle --- every k_i requires a valid C_i satisfying all four properties |

### What Lives Where

| Altitude | What | Lives At |
|----------|------|----------|
| 50K | Production line | `factory/imo-creator/060-production-line/src/lines.ts` |
| 50K | Line engine | `factory/imo-creator/060-production-line/` |
| 40K | Process docs | `factory/{canonical-silo}/{NNN-name}/PROCESS.md` |
| 30K | Step definitions + comparators | Section 3 Middle table in PROCESS.md |
| 20K | Step detail | `factory/{silo}/{NNN-name}/steps/{step}/PROCESS.md` |
| 10K | Tool config | Section 4 + `imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml` |
| 5K | Code | `factory/{silo}/{NNN-name}/src/` |
| ALL | Template | `Barton-Processes/law/PROCESS_TEMPLATE.md` v4.0.0 |
| ALL | Engine | `imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md` |
| ALL | Math | `imo-creator-v2/law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md` |
| ALL | Toolbox | `imo-creator-v2/law/SNAP_ON_TOOLBOX.yaml` |
| ALL | Logbook schema | `Barton-Processes/law/logbook_schema.yaml` |

---

## 6. CONSTANTS & VARIABLES (Bedrock SS2 + Mathematical Principle)

### Mathematical Definitions

_From TIER0_MATHEMATICAL_PRINCIPLE.md. These definitions apply to every constant and variable identified in this section and in every process built using this meta-process._

```
COMPARATOR
  C_i(x) -> R        a function that measures one structural rule
  Must satisfy ALL FOUR properties:
    1. Measurable     -- produces a numeric value from observable data
    2. Deterministic  -- same input always produces same output
    3. Representation-invariant -- result independent of encoding/format
    4. Temporally complete -- declares measurement support (continuous or Nyquist-compliant sampling)
  Must be grounded in exactly one primitive: Thing, Flow, or Change

TOLERANCE
  k_i in R+           the maximum acceptable deviation for comparator C_i
  k_i >= epsilon_k    tolerance floor -- prevents singularity (division by near-zero)
  Discovered through operation, not declared by fiat (3-phase lifecycle)

DECISION FUNCTION
  P(x;theta) = 1  if  max_i [ C_i(x) / k_i ] <= 1  else 0
  This is the ONLY decision function. No override. No qualitative assessment.

DIAGNOSTIC VECTOR
  r(x) = [ C_1(x)/k_1,  C_2(x)/k_2,  ...,  C_n(x)/k_n ]
  P(x) is the gate (binary). r(x) is for the mechanic (continuous).

STABILITY
  forall t in [1..N]:  P(f^t(x); theta) = 1
  AND  var(r_i(x)) over [t-w..t] <= sigma_max  for all i

DOMESTICATION (when to stop decomposing)
  max(r(x)) <= alpha  AND  var(r_i(x)) <= sigma_max  -->  stop
  Not "it seems tight enough." The math says stop.

GLOBAL GATE (back-propagation)
  ACCEPT(x_new) = P(x_new; theta') = 1
                  AND  forall x in L:  P(x; theta') = 1
  Adding a new constant triggers revalidation of ALL prior constants.
```

### Tolerance Lifecycle

_How tolerances get set during the build. You do not know the right thresholds upfront._

| Phase | Name | What Happens | When It Ends |
|-------|------|-------------|-------------|
| 1 | **Educated Guess** | Domain expert sets initial k_i values. Intentionally wide. They will be wrong. This is correct. The purpose is a starting position so the system can begin operation. | System begins operation. |
| 2 | **Calibration** | Stability loop runs. Failures surface. Diagnostic vector r(x) identifies which C_i(x)/k_i broke and by how much. Tighten k_i at the observed failure boundary (but never below epsilon_k). Check feasible region. Adjust bolt pattern if unexpected coupling appears. | k_i stops moving between cycles (convergence), OR oscillation detected (limit cycle), OR max iterations M_max reached. |
| 3 | **Stabilization** | When k_i stops moving, lock it. Not because it was declared correct --- because the data stopped proving it wrong. | Locked. Reopening only if new failure mode moves a previously stable k_i. |

### Bolt Pattern (Tolerance Setting Sequence)

_Tolerances are not set simultaneously. Each affects the others. The sequence matters._

1. Start with the most structurally independent tolerance --- the one least coupled to others.
2. Lock it.
3. Move to the next.
4. After each lock, verify all prior locks still hold (this IS the global gate / back-propagation applied to tolerances themselves).
5. If sigma expands on a prior constant after adding a new tolerance, the sequence is wrong. Back up and re-sequence.
6. If the coupling graph contains cycles, solve the cyclic block simultaneously, then resume sequential locking.

### Constants (structure --- never changes)

_What is fixed regardless of what data flows through. If this changes, you're redesigning, not operating. Each constant below now has an implicit comparator --- the question "did this hold?" is answered by C_i(x)/k_i <= 1, not by opinion._

| Constant | Comparator C_i | Primitive | Initial k_i | Notes |
|----------|---------------|-----------|-------------|-------|
| The altitude model (50K to 5K) | C_1 = altitudes_skipped_count | Flow | 0 + epsilon_k | Six altitudes, always in order, never skipped |
| The template (14 sections) | C_2 = sections_missing_count | Thing | 0 + epsilon_k | Every process gets all 14 sections from PROCESS_TEMPLATE v4.0.0 |
| The Foundational Bedrock (C&V + IMO + CTB + Circle) | C_3 = validators_skipped_count | Flow | 0 + epsilon_k | Applied simultaneously at every gate, not sequentially |
| The descent order | C_4 = out_of_order_steps_count | Flow | 0 + epsilon_k | Never skip an altitude. Never build at 5K before documenting at 30K |
| Auditor separation | C_5 = self_certification_count | Change | 0 + epsilon_k | Builder cannot certify own work. Different engine required |
| Canonical silo paths | C_6 = invalid_path_count | Thing | 0 + epsilon_k | factory/imo-creator, factory/outreach, factory/real-estate, factory/personal. Locked in STRUCTURE_MANIFEST.yaml |
| Required files (3) | C_7 = missing_files_count | Thing | 0 + epsilon_k | PROCESS.md, heir.yaml, CLAUDE.md per directory |
| Well-drinks-first tool priority | C_8 = priority_violations_count | Flow | 0 + epsilon_k | Free before cheap before top shelf |
| Station entry constants | C_9 = missing_station_fields_count | Thing | 0 + epsilon_k | Station ID, dependency graph, adapter type never change |
| Between-process logic | C_10 = bedrock_in_routing_count | Change | 0 + epsilon_k | Only conditional routing between stations. Bedrock lives inside the process |

_Note: Many of these constants have tolerances at epsilon_k (near-zero). That is correct --- they are structural invariants where ANY violation is a failure. The tolerance floor prevents mathematical singularity while preserving zero-tolerance semantics._

### Variables (fill --- changes every run)

_The values that fill the constants. Different every execution._

- **Which process is being built** --- the specific BAR ticket and business need
- **Which business silo it belongs to** --- outreach, imo-creator, real-estate, personal
- **Which tools it needs** --- selected from Snap-On Toolbox at 10K based on the process's requirements
- **How many internal steps** --- some processes have 3, some have 12
- **Which steps need 20K detail** --- only steps that are complex, broken, or where sigma isn't tightening
- **ORBT state** --- BUILD until certification, then OPERATE
- **Which workpiece is being processed** --- the data flowing through at runtime
- **Tolerance values k_i** --- Phase 1 guesses, refined in Phase 2, locked in Phase 3
- **Diagnostic vector r(x)** --- computed each run, different values every execution
- **Comparator outputs C_i(x)** --- the measured values at each step

---

## 7. STOP CONDITIONS

_When to halt. Not optional. From Troubleshooting Loop (Bedrock SS6), Aviation Model (Bedrock SS8), and Mathematical Principle._

| Condition | Action |
|-----------|--------|
| Can't answer two-question intake ("What triggers this?" + "How do we get it?") | HALT --- process isn't defined, ask Dave |
| No BAR ticket | HALT --- no authorization to build |
| Skipped an altitude | HALT --- go back and fill the gap |
| Builder attempting self-certification | HALT --- assign different engine as auditor |
| C&V three questions can't be answered for a step | HALT --- step isn't ready for the Middle table |
| Comparator C_i fails any of the four properties (not measurable, not deterministic, not representation-invariant, not temporally complete) | HALT --- comparator is invalid, redefine before proceeding |
| Non-nullity check fails: sum of abs(C_i(x)) <= epsilon | HALT --- candidate produces no measurable signal, cannot classify |
| Canonical silo path doesn't exist in STRUCTURE_MANIFEST.yaml | HALT --- invalid placement |
| Strike 3 on same build failure pattern | Troubleshoot/Train --- produce Airworthiness Directive that updates the template |
| Sigma expanding on a step during build: var(r_i(x)) increasing | HALT --- something upstream was misclassified. Re-run that gate. |
| Constraint collision: no theta' exists satisfying all locked constants | HALT --- invariant set requires restructuring. This is a Troubleshooting Loop trigger, not a tolerance adjustment. |
| Feasible region too narrow: vol(Theta)^(1/n) < delta | HALT --- system is fragile. The invariant set requires restructuring, not tighter tolerances. |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| BAR ticket | Authorization and requirement definition | DONE (per-invocation) |
| FOUNDATIONAL_BEDROCK.md | The engine --- SS1-8 | DONE (locked, immutable) |
| TIER0_MATHEMATICAL_PRINCIPLE.md | The math --- P(x;theta), r(x), tolerance lifecycle, bolt pattern | DONE (locked, immutable) |
| PROCESS_TEMPLATE v4.0.0 | The 14-section template | DONE (locked at v4.0.0) |
| STRUCTURE_MANIFEST.yaml | Canonical silo paths, required files | DONE (locked) |
| SNAP_ON_TOOLBOX.yaml | 27 tool sub-hubs, vendor registry | DONE (gated) |
| logbook_schema.yaml | Logbook entry format | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Production Line Engine | Station definition in lines.ts with dependencies |
| All processes built using this meta-process | The certified PROCESS.md (with comparators + tolerances), heir.yaml, CLAUDE.md |
| Auditor agent | Execution trace from SS11 + diagnostic vector r(x) to review for certification |
| LBB | Session learnings ingested after build |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output. Not prose --- run these._

```
1. Process directory exists at canonical silo path
   -> expected: factory/{silo}/{NNN-name}/ exists

2. PROCESS.md has all 14 sections
   -> expected: grep for "## 1. IDENTITY" through "## 14. SESSION LOG" -- all 14 present

3. heir.yaml has 8 fields
   -> expected: sovereign_ref, hub_id, sub_hub, component, version, created_at, orbt, cc_layer all present

4. CLAUDE.md exists with pre-flight
   -> expected: file exists, contains "Bedrock Pre-Flight" or equivalent gate checklist

5. Station added to lines.ts with dependencies
   -> expected: station ID matches PROC-NNN, depends_on array populated, orbt = 'BUILD'

6. Tier 0 run on every internal step (C&V three questions + comparators)
   -> expected: every Middle table row can answer: NAME it? FORMAT it? VALUE filling a position?
   -> expected: every constant has C_i defined with all four properties verified
   -> expected: every C_i has initial k_i set (Phase 1 educated guess)
   -> expected: every C_i grounded in exactly one primitive (Thing, Flow, or Change)

7. Code implements documented spec (5K matches 30K-40K documentation)
   -> expected: OSAM read/write paths match code, tools match Section 4, stop conditions implemented

8. Auditor can review execution trace + diagnostic vector
   -> expected: Section 11 populated with append-only entries, all steps traced
   -> expected: r(x) computed for each run, P(x;theta) evaluated
   -> expected: P(x;theta) = 1 for 3 consecutive runs with var(r_i(x)) <= sigma_max

9. Non-nullity gate passes
   -> expected: sum of abs(C_i(x)) > epsilon for the candidate process
```

**Three Primitives Check (Bedrock SS1):**
1. **Thing:** Did every component exist where it should? (directory, files, station entry)
2. **Flow:** Did the data reach every step? (BAR ticket to station to docs to code to trace)
3. **Change:** Did the transformation happen correctly? (business need became certified process)

If any fails --- that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock SS6).

### The Descent Checklist

Before building ANY process, walk this checklist:

```
[ ] 50K -- Station added to production line (lines.ts)
[ ] 50K -- Dependencies defined (what must complete first)
[ ] 40K -- PROCESS.md created (14 sections, template v4.0.0)
[ ] 40K -- heir.yaml + CLAUDE.md created (required per STRUCTURE_MANIFEST.yaml)
[ ] 30K -- Middle table defined (each step is its own IMO)
[ ] 30K -- Tier 0 run on every step (C&V three questions minimum)
[ ] 30K -- Comparators C_i defined for every constant (all four properties verified)
[ ] 30K -- Initial tolerances k_i set (Phase 1 educated guesses)
[ ] 30K -- Comparators grounded in primitives (Thing, Flow, or Change)
[ ] 30K -- Bolt pattern sequence declared (most independent first)
[ ] 20K -- Complex/broken steps get their own PROCESS.md
[ ] 10K -- Tools identified from Snap-On Toolbox
[ ] 10K -- Tool priority enforced (well drinks first)
[ ] 5K  -- Code written (implements the documentation)
[ ] 5K  -- Smoke test passes (section 9)
[ ] 5K  -- Analytics defined BEFORE build (BAR-187)
[ ] 5K  -- Diagnostic vector r(x) computed for first run
[ ] 5K  -- P(x;theta) = 1 for 3 consecutive runs
[ ] 5K  -- var(r_i(x)) <= sigma_max for all comparators
[ ] ALL -- Execution trace recorded (section 11)
[ ] ALL -- Submit for auditor certification (builder != auditor)
```

---

## 10. ANALYTICS --- The Dyno Sheet (Bedrock SS2 + SS5 + Mathematical Principle)

_The BUILD to OPERATE gate. No analytics passing tolerance = stays on the dyno. This section MUST be defined BEFORE build starts. No analytics spec = no build authorization (BAR-187)._

_With the mathematical engine, the dyno sheet IS the adapter. Each metric is a comparator C_i. Each tolerance is k_i. The BUILD-to-OPERATE gate is the decision function: P(x;theta) = 1 if max_i[C_i(x)/k_i] <= 1, else 0. Sigma tracking is var(r_i(x)) over a sliding window. This is not metaphor --- this is the computation._

### Process Metrics (Each Metric = a Comparator C_i)

_Define BEFORE build starts. These are the instruments on the dyno. Each metric is a comparator function (named, formatted, grounded in a primitive). The value each run is the variable. The tolerance is k_i. The decision function P(x;theta) aggregates all of them._

| Metric (= C_i) | Primitive | Unit | First Run = Baseline | Target k_i (after baseline) | Phase |
|----------------|-----------|------|---------------------|---------------------------|-------|
| Time from BAR to certified process | Flow | hours | BASELINE | set after first run, +/- 25% | Phase 1 |
| Number of altitudes documented | Thing | count (max 6) | BASELINE | k = 6 (must be 6/6) | Phase 1 |
| Audit pass rate on first submission | Change | % | BASELINE | set after first run, > 80% | Phase 1 |
| Strike count during build | Change | count | BASELINE | k = 1 (tolerance <= 1) | Phase 1 |
| 14-section completeness | Thing | count (max 14) | BASELINE | k = 14 (must be 14/14) | Phase 1 |
| Required files created | Thing | count (max 3) | BASELINE | k = 3 (must be 3/3) | Phase 1 |
| Comparators defined per step | Thing | count | BASELINE | set after first run | Phase 1 |
| Comparator property violations | Change | count | BASELINE | k = 0 + epsilon_k | Phase 1 |

_All Phase 1 tolerances are educated guesses. They will be wrong. Phase 2 calibrates from failures. Phase 3 locks when k_i stops moving._

### Decision Function (The BUILD-to-OPERATE Gate)

```
For each metric C_i with tolerance k_i:
  r_i(x) = C_i(x) / k_i          (the ratio -- how close to the limit)

Diagnostic vector:
  r(x) = [r_1, r_2, ..., r_n]    (all ratios, all runs)

Gate decision:
  P(x;theta) = 1  if  max(r(x)) <= 1  else 0

BUILD -> OPERATE requires:
  P(x;theta) = 1 for 3 consecutive runs
  AND var(r_i(x)) <= sigma_max for all i over those runs

If P = 0:  which C_i broke? r(x) tells you. Fix at source.
If var expanding:  sigma is broken. Something upstream changed.
```

### Sigma Tracking (Bedrock SS2 + var(r_i(x)) <= sigma_max)

_After 3+ builds, track whether each metric is tightening, flat, or expanding. This is now the variance of the diagnostic vector over a sliding window._

| Metric (C_i) | Run 1 r_i | Run 2 r_i | Run 3 r_i | var(r_i) | Trend | Action |
|--------------|-----------|-----------|-----------|----------|-------|--------|
| Time from BAR to certified | | | | | | |
| Audit pass rate | | | | | | |
| Strike count | | | | | | |

_Tightening (var decreasing) = real constant, the build process is stabilizing. Flat (var near-zero but not converging) = phantom, something isn't learning. Expanding (var increasing) = broken, something upstream changed or was misclassified._

### Domestication Check

_When to stop decomposing a metric further:_

```
max(r(x)) <= alpha  AND  var(r_i(x)) <= sigma_max  -->  DOMESTICATED

alpha = domestication threshold (defined per adapter, 0 < alpha < 1)
sigma_max = maximum permitted variance per comparator

If domesticated: the variable's range is irrelevant to the outcome.
Stop decomposing. The math says stop.

If NOT domesticated: either max(r(x)) > alpha (too close to threshold)
or var(r_i) > sigma_max (too unstable). Keep decomposing.
```

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | P(x;theta) = 1 for 3 consecutive runs AND var(r_i(x)) <= sigma_max for all i AND **auditor sign-off** |
| OPERATE | REPAIR | Any C_i(x)/k_i > 1 (any metric outside tolerance) |
| REPAIR | OPERATE | Fix applied + P(x;theta) = 1 + var(r_i) back within sigma_max + **auditor verification** |
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
| r_i | Diagnostic ratio for this step: C_i(x)/k_i | Float | Yes |
| P_step | Step decision: 1 if max(r_i) <= 1 else 0 | 0 or 1 | Yes |
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
| r_vector | Full diagnostic vector r(x) = [r_1, ..., r_n] for this run |
| P_run | Decision function: 1 if max(r_vector) <= 1 else 0 |
| var_r | Variance of each r_i over sliding window [t-w..t] |
| total_duration_ms | Wall clock time for full run |
| total_cost_cents | Sum of all step costs |
| errors | Count + summary of failures |
| learnings | What was new --- feeds to LBB |

### Rules

- **Append-only.** No edits. No deletions. Immutable.
- **Every step gets a trace entry.** No step executes without logging.
- **Every trace entry includes r_i and P_step.** The math is logged, not just the outcome.
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
| authority | "Auditor certification per Tier 0 gate stack + Mathematical Principle" |
| gates_passed | { imo: true, ctb: true, circle: true, P_decision: 1 } |
| r_vector_final | Diagnostic vector from final certification run |
| var_r_final | Variance of each r_i at certification |
| consecutive_passes | Number of consecutive P(x;theta) = 1 runs (must be >= 3) |
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
| r_vector | Diagnostic vector at time of entry | Yes |
| P_decision | Decision function result at time of entry | Yes |
| action | What the mechanic did | Yes |
| authority | Which Bedrock section authorized this | Yes |
| gates_passed | { imo: bool, ctb: bool, circle: bool, P_decision: 0 or 1 } | Yes |
| checklist_type | operate / repair / troubleshoot_train | Yes |
| signed_by | Who did the work | Yes |
| signed_at | Immutable timestamp | Yes |

---

## 13. FLEET FAILURE REGISTRY & STRIKE TRACKING

_Strike tracking at FLEET level, not per-goal. The same failure pattern appearing across multiple process builds triggers escalation. (Bedrock SS6, SS8)_

### Failure Pattern Registry

| Pattern ID | Station | Error Code | C_i that broke | r_i at failure | First Seen | Occurrences | Processes Affected | Strike Count | Status |
|-----------|---------|-----------|---------------|---------------|-----------|-------------|-------------------|-------------|--------|
| FP-001 | 40K-docs | missing-heir-yaml | C_7 (missing_files) | r_7 > 1 | | 0 | | 0 | OPEN |
| FP-002 | 40K-docs | wrong-silo-path | C_6 (invalid_path) | r_6 > 1 | | 0 | | 0 | OPEN |
| FP-003 | 30K-steps | missing-cv-test | C_3 (validators_skipped) | r_3 > 1 | | 0 | | 0 | OPEN |
| FP-004 | 50K-station | missing-dependency | C_9 (missing_station_fields) | r_9 > 1 | | 0 | | 0 | OPEN |
| FP-005 | 5K-code | code-before-docs | C_4 (out_of_order) | r_4 > 1 | | 0 | | 0 | OPEN |
| FP-006 | 30K-steps | invalid-comparator | C_i missing property | N/A | | 0 | | 0 | OPEN |
| FP-007 | 5K-analytics | tolerance-singularity | k_i < epsilon_k | r_i = infinity | | 0 | | 0 | OPEN |

### Strike Rules

- **Strike 1:** Repair. Fix at source. Log it. Record r(x) at failure.
- **Strike 2:** Repair with scrutiny. Was root cause actually found? Check if the same C_i keeps breaking.
- **Strike 3:** **STOP.** Troubleshoot/Train. The problem isn't a broken part --- it's a broken understanding. Produce AD that updates the PROCESS_TEMPLATE itself. If the same C_i breaks 3 times, the comparator or tolerance may need restructuring, not just tightening.

### Airworthiness Directive (Strike 3 output)

_When strike 3 fires, the fix goes to ALL processes, not just the one that failed. This updates the template, not just one file._

| Field | Value |
|-------|-------|
| AD Number | AD-[YYYY]-[NNN] |
| Failure Pattern | FP-[NNN] --- [description] |
| C_i that failed | Which comparator broke |
| r_i at failure | The diagnostic ratio at failure |
| Root Cause | [from Troubleshooting Loop SS6] |
| Fix Applied | [what changed --- comparator redefined? tolerance restructured? bolt pattern resequenced?] |
| Scope | ALL processes / [specific silo] / [specific station] |
| Template Updated | Yes / No --- if Yes, what section |
| Issued By | [mechanic + auditor sign-off] |
| Issued At | [timestamp] |

**AD issuance requires:**
1. Root cause identified (Troubleshooting Loop SS6 complete)
2. Fix tested on the failing process (P(x;theta) = 1 after fix)
3. Fix verified by auditor (different engine)
4. Template updated if the fix is structural
5. All affected processes notified/updated
6. Global gate re-run: all prior locked constants still hold under new theta'

---

## 14. SESSION LOG

_Every session that touches this process. Links to LBB for detail._

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| 2026-04-02 | v1.0.0 --- initial HOW_TO_BUILD_A_PROCESS.md created with altitude model | none |
| 2026-04-01 | v2.0.0 --- rewritten as proper 14-section PROCESS.md from PROCESS_TEMPLATE v4.0.0 | none |
| 2026-04-01 | v3.0.0 --- mathematical engine integrated from TIER0_MATHEMATICAL_PRINCIPLE.md. Comparators, tolerances, decision function, diagnostic vector, stability, domestication, bolt pattern, tolerance lifecycle woven into all sections. | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-02 |
| Last Modified | 2026-04-01 |
| Version | 3.0.0 |
| Template Version | 4.0.0 |
| Mathematical Engine | imo-creator-v2/law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md v3.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md (parent repo) |
| Logbook Schema | Barton-Processes/law/logbook_schema.yaml |
| OSAM Authority | Section 5 of this document (self-contained meta-process) |
| Data Flow | N/A --- meta-process, no runtime data flow |
| Authority | Dave Barton --- the architect |

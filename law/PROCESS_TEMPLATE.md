# PROCESS: [NAME]
## [One sentence — what this process does and why it matters]
### Status: [BUILD | OPERATE | REPAIR | TROUBLESHOOT/TRAIN]
### Business: [imo-creator | svg-agency | real-estate | personal]

---

# IDENTITY (Thing — what this process IS)

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-[NNN] |
| Name | [human-readable name] |
| Business Silo | [which business this serves] |
| CTB Position | [where on the tree — e.g., factory/svg-agency/200-people-worker] |
| ORBT | [BUILD / OPERATE / REPAIR / TROUBLESHOOT_TRAIN] |
| Strikes | [0 / 1 / 2 / 3] |
| Last Deployed | [date] |
| BAR Reference | BAR-[NNN] |
| Deployed URL | [URL or "not deployed"] |
| Cron | [schedule or "manual" or "none"] |
| Runtime | [CF Worker / Python / Node] |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

[2-3 sentences. Not how it works — why it matters. What downstream process starves without its output.]

---

## 3. RESOURCES

_Every tool, database, integration, API, secret, agent, and dependency this process touches. A mechanic reads this and knows exactly what to set up before the process can run._

_Merges "What It Grabs Off The Wall" + "Dependencies" — both answer the same question: what must exist before this runs._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| [D1 name] | [env var] | [database ID] | [READ / WRITE / READ ONLY] | [what tables, what data] |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| [tool name] | [Tool / API / MCP / Composio] | [Free / Cheap / Top Shelf] | [Doppler key name or "none"] | [what it does in this process] |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| [secret name] | [project] | [config] | [which step uses it] |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 — always first
2. Free external fetches (CF Worker fetch, no proxy) — second
3. Cheap integrations (Composio routes) — third
4. Top shelf (per-call APIs, proxy services) — only when free/cheap exhausted

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| [process / data source / service] | [what it provides] | [DONE / PENDING / BLOCKED] |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| [process / service] | [what data it reads from this process's output] |

---

# CONTRACT (Flow — what flows through this process)

## 4. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — [cron / webhook / manual / upstream process output]
2. **"How do we get it?"** — [which data source, which API, which table]

### Input
[What triggers the process. What data it needs. Where that data comes from.]

### Middle
[What it does — step by step. Each step is its own IMO.]

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | [trigger] | [transformation] | [result] | [tool/API/query] |
| 2 | [step 1 output] | [transformation] | [result] | [tool/API/query] |
| N | [step N-1 output] | [transformation] | [final result] | [tool/API/query] |

### Output
[What comes out. Where it goes. What downstream process consumes it.]

### Circle (Bedrock §5)
[How output feeds back to input. Logbook entry, LBB ingest, ORBT update, metrics that inform next run.]

---

## 5. OSAM — Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins. What's forbidden._

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| [table name] | [what data, what columns] | [join key to spine] |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| [table name] | [what changes] | [which step] |

### Join Chain

```
[spine table].outreach_id
  → [table 1] (join key, relationship)
  → [table 2] (join key, relationship)
       → [table 3] (join key, relationship)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| [what this process must NEVER do] | [which rule it violates] |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| [business question] | [which table answers it] | [which column] |

---

## 6. DMJ — Define, Map, Join (law/doctrine/DMJ.md)

_Three steps. In order. Can't skip. Each step is its own sub-layer with a distinct table format._

### 6a. DEFINE (Build the Key)

_Run C&V on every data element this process touches. Each element gets a description, unique ID, and format. The mathematical equation validates: P(x;θ) = 1 if max_i[C_i(x)/k_i] ≤ 1. Elements that survive are constants. Elements that don't are variables. Unidentified elements are stored as unidentified — not discarded._

| Element | ID | Format | Description | Constant or Variable |
|---------|-----|--------|-------------|---------------------|
| [element] | [unique ID] | [format] | [description] | [C / V] |

### 6b. MAP (Connect Key to Structure)

_Once every element is defined, map each one to the target structure. Source column → target column. Cannot execute without 6a complete._

| Source (this process) | Target (our structure) | Transform |
|----------------------|----------------------|-----------|
| [source element ID] | [target column] | [direct / classify / parse] |

### 6c. JOIN (Path to Spine)

_How does this process's data connect to the spine? What is the join key? Direct, indirect, or fuzzy? Cannot execute without 6b complete._

| Join Path | Type | Description |
|-----------|------|-------------|
| [source field] → [spine field] | [direct / indirect / fuzzy] | [how the join works] |

_If no join path exists, back-propagate to 6a — the key is missing a field. The Circle closes._

---

## 7. CONSTANTS & VARIABLES (Bedrock §2)

_Summary of what 6a (Define) produced. The constants and variables identified by running the equation._

### Constants (structure — never changes)

_What is fixed regardless of what data flows through. If this changes, you're redesigning, not operating._

- [constant 1]
- [constant 2]
- [constant 3]

### Variables (fill — changes every run)

_The values that fill the constants. Different every execution._

- [variable 1]
- [variable 2]
- [variable 3]

---

## 8. STOP CONDITIONS (Bedrock §6)

_When to halt. Not optional. From Troubleshooting Loop (Bedrock §6) and Aviation Model (Bedrock §8)._

| Condition | Action |
|-----------|--------|
| Can't answer two-question intake | HALT — process isn't defined |
| OSAM question can't be routed | HALT — semantic gap, ask human |
| Tool returns 5 consecutive errors | HALT — check tool state |
| Budget cap reached on Top Shelf tool | HALT — do not proceed |
| Data quality below threshold | HALT — flag for human review |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

# GOVERNANCE (Change — how this process is controlled)

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output. Not prose — run these._

```
1. [Action — e.g., GET /health] → expected: [result]
2. [Action — e.g., query D1 table] → expected: [count or value]
3. [Action — e.g., POST /pass/0] → expected: [records processed]
4. [Action — e.g., verify join] → expected: [match rate]
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Did every component exist where it should?
2. **Flow:** Did the data reach every step?
3. **Change:** Did the transformation happen correctly?

If any fails → that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock §6).

---

## 10. ANALYTICS — The Dyno Sheet (Bedrock §2 + §5)

_The BUILD→OPERATE gate. Three distinct sub-layers that the Grid Reader parses independently._

### 10a. Process Metrics

_Define BEFORE build starts. These are the instruments on the dyno. Each metric is a constant (named, formatted). The value each run is the variable._

| Metric | Unit | First Run = Baseline | Target (after baseline) | Tolerance |
|--------|------|---------------------|------------------------|-----------|
| [metric name] | [count / % / $/unit / ms] | BASELINE | [set after first run] | [acceptable range] |

### 10b. Sigma Tracking (Bedrock §2)

_After 3+ runs, track whether each metric is tightening, flat, or expanding._

| Metric | Run 1 | Run 2 | Run 3 | Trend | Action |
|--------|-------|-------|-------|-------|--------|
| [metric] | [value] | [value] | [value] | TIGHTENING / FLAT / EXPANDING | [none / investigate / reclassify] |

_Tightening = real constant, process is stabilizing. Flat = phantom, something isn't learning. Expanding = broken, something upstream changed._

### 10c. ORBT Gate Rules

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs + **auditor sign-off** |
| OPERATE | REPAIR | Any metric outside tolerance |
| REPAIR | OPERATE | Fix applied + metric back within tolerance + **auditor verification** |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same failure pattern 3 times at fleet level → AD |

_The builder cannot certify its own work. The auditor MUST be a different engine than the builder. (Bedrock §8)_

---

## 11. EXECUTION TRACE (During BUILD)

_Append-only record of what happened during build/execution. This is NOT the logbook — the logbook is created only after auditor certification. This is the build journal that the auditor reviews._

### Entry Format (per step, per run)

| Field | Description | Format | Required |
|-------|-------------|--------|----------|
| trace_id | Unique entry identifier | UUID | Yes |
| run_id | Which execution run this belongs to | UUID (one per goal/batch) | Yes |
| step | What was attempted | Station ID or action name | Yes |
| target | Expected outcome (defined in §10a metrics) | Text — measurable | Yes |
| actual | What happened | Text — measurable | Yes |
| delta | Target vs actual | Number or text — the gap | Yes |
| status | Step outcome | done / failed / skipped | Yes |
| error_code | If failed — machine-readable error type | Text or null | If failed |
| error_message | If failed — human-readable description | Text or null | If failed |
| tools_used | Which Snap-On sub-hub tools were called | JSON array of tool numbers | Yes |
| duration_ms | How long this step took | Integer (milliseconds) | Yes |
| cost_cents | Cost of this step | Integer (cents) | Yes |
| timestamp | When this happened | ISO-8601 | Yes |
| signed_by | Who/what produced this entry | Agent name or "manual" | Yes |

### Run Summary (per execution run)

| Field | Description |
|-------|-------------|
| run_id | UUID for this execution run |
| trigger | What started this run (cron / manual / inbox / upstream) |
| orbt_at_start | ORBT state when run began |
| steps_total | How many steps planned |
| steps_completed | How many passed |
| steps_failed | How many failed |
| total_duration_ms | Wall clock time for full run |
| total_cost_cents | Sum of all step costs |
| errors | Count + summary of failures |
| learnings | What was new — feeds to LBB |

### Rules

- **Append-only.** No edits. No deletions. Immutable.
- **Every step gets a trace entry.** No step executes without logging.
- **Trace exists during BUILD.** This is NOT the certified logbook.
- **Auditor reviews the trace** to decide certification.
- **Trace persists after certification** — it becomes evidence inside the logbook's birth certificate.

---

## 12. LOGBOOK (After Certification Only)

_The aircraft's legal identity. Created ONLY when the auditor certifies the process (BUILD → OPERATE). (Bedrock §8)_

**No logbook during BUILD.** The execution trace (§11) is the build journal. The logbook is born when the auditor signs off.

### Birth Certificate (first entry — created by auditor at certification)

| Field | Value |
|-------|-------|
| heir_ref | Full HEIR record for this process |
| orbt_entered | BUILD |
| orbt_exited | OPERATE |
| action | "Process certified — airworthiness confirmed" |
| authority | "Auditor certification per Tier 0 gate stack" |
| gates_passed | { imo: true, ctb: true, circle: true } |
| checklist_type | build_checklist |
| checklist_items | Full build checklist with all items PASS |
| execution_trace_ref | Link to §11 trace (evidence the auditor reviewed) |
| signed_by | Auditor agent (MUST be different engine than builder) |
| signed_at | Certification timestamp |

### Subsequent Entries (during OPERATE, REPAIR, TROUBLESHOOT/TRAIN)

| Field | Description | Required |
|-------|-------------|----------|
| heir_ref | HEIR reference — hub_id, sub_hub, component | Yes |
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

_Strike tracking at FLEET level, not per-goal. The same failure pattern appearing across multiple goals/runs triggers escalation. (Bedrock §6, §8)_

### Failure Pattern Registry

| Pattern ID | Station | Error Code | First Seen | Occurrences | Goals Affected | Strike Count | Status |
|-----------|---------|-----------|-----------|-------------|---------------|-------------|--------|
| FP-[NNN] | [station_id] | [error_code] | [date] | [count] | [list of goal_ids] | [0-3] | OPEN / RESOLVED / AD_ISSUED |

### Strike Rules

- **Strike 1:** Repair. Fix at source. Log it.
- **Strike 2:** Repair with scrutiny. Was root cause actually found?
- **Strike 3:** **STOP.** Troubleshoot/Train. The problem isn't a broken part — it's a broken understanding.

### Airworthiness Directive (Strike 3 output)

| Field | Value |
|-------|-------|
| AD Number | AD-[YYYY]-[NNN] |
| Failure Pattern | FP-[NNN] — [description] |
| Root Cause | [from Troubleshooting Loop §6] |
| Fix Applied | [what changed] |
| Scope | ALL processes / [specific silo] / [specific station] |
| Template Updated | Yes / No — if Yes, what section |
| Issued By | [mechanic + auditor sign-off] |
| Issued At | [timestamp] |

---

## 14. SESSION LOG

_Every session that touches this process. Links to LBB for detail._

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| [date] | [summary] | [record_id or "none"] |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | [date] |
| Last Modified | [date] |
| Version | [semver] |
| Template Version | 6.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md + law/doctrine/DMJ.md |
| US Validated | [date of US run that validated this template] |

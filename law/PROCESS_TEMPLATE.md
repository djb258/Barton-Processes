# PROCESS: [NAME]
## [One sentence — what this process does and why it matters]
### Status: [BUILD | OPERATE | REPAIR | TROUBLESHOOT/TRAIN]
### Business: [imo-creator | svg-agency | real-estate | personal]

---

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

## 3. IMO — What Comes In, What Happens, What Comes Out

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
[How output feeds back to input. Logbook entry, imo-brain ingest, ORBT update, metrics that inform next run.]

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches. A mechanic reads this and knows exactly what to set up before the process can run._

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

---

## 5. OSAM — Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins. What's forbidden. From the hub OSAM (barton-outreach-core/doctrine/OSAM.md)._

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

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)

_What is fixed regardless of what data flows through. If this changes, you're redesigning, not operating._

- [constant 1 — e.g., slot types are CEO, CFO, HR]
- [constant 2 — e.g., outreach_id is the universal join key]
- [constant 3 — e.g., well drinks before top shelf]

### Variables (fill — changes every run)

_The values that fill the constants. Different every execution._

- [variable 1 — e.g., which companies get processed]
- [variable 2 — e.g., how many slots get filled]
- [variable 3 — e.g., what data comes back from search]

---

## 7. STOP CONDITIONS

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

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| [process / data source / service] | [what it provides] | [DONE / PENDING / BLOCKED] |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| [process / service] | [what data it reads from this process's output] |

---

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

## 10. LOGBOOK

_Append-only. Read first, write last. No exceptions. (Bedrock §8)_

### [DATE] — [Run summary]

**ORBT:** [state at time of run]
**Trigger:** [what started this run]
**Records processed:** [count]
**Errors:** [count and summary]
**Tools used:** [which wall items were called]
**Result:** [what changed — slots filled, records updated, signals emitted]
**Learnings:** [anything new — feeds to imo-brain]
**ORBT after:** [same or changed?]

---

## 11. KNOWN ISSUES & STRIKE TRACKING

_The error history. Append-only — never delete a resolved issue._

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | [date] | [what broke] | [why] | [how fixed] | [0-3] |

**Strike 3 → Troubleshoot/Train → Airworthiness Directive.**
AD goes to ALL processes, not just this one. Update the template, not just this file.

---

## 12. SESSION LOG

_Every session that touches this process. Links to imo-brain for detail._

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| [date] | [summary] | [source_path or "none"] |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | [date] |
| Last Modified | [date] |
| Version | [semver] |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | [path to hub OSAM] |
| Data Flow | [path to DATA_FLOW.md] |

# UP — The Ultimate Process
## Six agents. One flow. Any data. Any domain.
### Status: BUILD
### Authority: Bedrock Foundation + DMJ + 060

---

## CTB — The Tree

```
UP (TRUNK)
│
├── Orchestrator Agent (BRANCH)
│   └── Checklist execution (LEAF)
│   └── Footprint read (LEAF)
│   └── Dispatch decision (LEAF)
│   └── Documentation (LEAF)
│
├── D Agent — Define (BRANCH)
│   └── C&V on every element (LEAF)
│   └── Equation: P(x;θ) (LEAF)
│   └── Key output (LEAF)
│   └── Sigma tracking (LEAF)
│
├── M Agent — Map (BRANCH)
│   └── Read key (LEAF)
│   └── Connect to target structure (LEAF)
│   └── Mapping table output (LEAF)
│
├── J Agent — Join (BRANCH)
│   └── Read map (LEAF)
│   └── ERD analysis (LEAF)
│   └── Join path resolution (LEAF)
│   └── Back-propagation to D if gap found (LEAF)
│
├── QC Agent — Quality Control (BRANCH)
│   └── Run P(x;θ) on evidence (LEAF)
│   └── Ones and zeros per element (LEAF)
│   └── Diagnostic vector (LEAF)
│   └── Scorecard output (LEAF)
│
├── TS — Troubleshooting / Human Gate (BRANCH)
│   └── Read QC scorecard (LEAF)
│   └── Run 11-step troubleshooting on failures (LEAF)
│   └── Set tolerance for this run (LEAF)
│   └── Approve or send back for rework (LEAF)
│
└── Auditor Agent — FAA (BRANCH)
    └── Read Bedrock checklist — all 11 steps (LEAF)
    └── Verify evidence behind every checkbox (LEAF)
    └── HEIR + ORBT check (LEAF)
    └── Certify or reject (LEAF)
```

**Trunk:** UP is the process. Everything falls underneath it.
**Branches:** Six agents. Each has a defined role.
**Leaves:** The specific tasks each agent executes.

---

## What Lives Inside UP

| Component | What It Is | Where It Lives |
|-----------|-----------|---------------|
| 060 | How to define structure | factory/imo-creator/060-production-line/ |
| DMJ | Define, Map, Join — the three steps | law/doctrine/DMJ.md (LOCKED) |
| Process Template v5.0.0 | 15-section documentation | law/PROCESS_TEMPLATE.md |
| Bedrock Foundation | The equation, the physics | law/doctrine/FOUNDATIONAL_BEDROCK.md (LOCKED) |
| Mathematical Principle | The computable equation | law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md (LOCKED) |

UP doesn't replace these. UP contains them. You don't run 060 separately or DMJ separately. You run UP. UP runs all of them in the right order.

---

## IMO — The Flow

### Two-Question Intake
1. **"What triggers UP?"** — Raw data exists that needs structuring. A section, a subsection, a page, a data source, a new domain.
2. **"How do we get it?"** — The Orchestrator reads the checklist, dispatches to D, M, J, QC, Auditor. In order. No skipping.

### Input
- Raw data from any source (database table, web page, platform page, DOL filing, anything)
- The target structure (what we want the data mapped into)
- The spine ID (what everything joins to)

### Middle — Six Agents in Sequence

```
RAW DATA
    │
    ▼
ORCHESTRATOR
    │  Read checklist (060 + Bedrock)
    │  Read footprint (what's done, what's not)
    │  Document recommendation (WHY this work is needed)
    │  Dispatch to D
    │
    ▼
D AGENT (Define)
    │  Input: raw data elements
    │  Run C&V on EVERY element
    │  Run equation: P(x;θ) = 1 if max_i[C_i(x)/k_i] ≤ 1
    │  Give each element: description, unique ID, format
    │  Identified → bucket (KB-01 through KB-07)
    │  Unidentified → stored as KB-99 (NOT discarded)
    │  Output: THE KEY — complete structure definition
    │  Evidence: every element listed with classification
    │
    ▼
M AGENT (Map)
    │  Input: the key from D
    │  Read target structure
    │  Connect: source element → target column
    │  Output: MAPPING TABLE
    │  Evidence: every source→target connection listed
    │
    ▼
J AGENT (Join)
    │  Input: the map from M
    │  Read full ERD
    │  Find path to spine (direct, indirect, fuzzy)
    │  Test: does the join resolve?
    │  If gap found → back-propagate to D (via Orchestrator)
    │  Output: JOIN PATH — how this data connects
    │  Evidence: join tested, company match verified (1 or 0)
    │
    ▼
QC AGENT (Quality Control)
    │  Input: D output + M output + J output
    │  Run P(x;θ) on the COMPLETE chain
    │  Every element: 1 (pass) or 0 (fail)
    │  Diagnostic vector: which step failed, by how much
    │  Output: SCORECARD — ones and zeros
    │  Evidence: the actual numbers, not self-reported
    │
    ▼
TS — TROUBLESHOOTING (Human in the Loop)
    │  THE HUMAN GATE. Not optional. Not skippable.
    │  Input: QC scorecard — the ones and zeros
    │  Human reads the scorecard
    │  Human runs 11-step troubleshooting loop on failures (Bedrock §6)
    │  Human identifies root causes (why did these fail?)
    │  Human decides the fix path (retry? alternate source? accept?)
    │  Human sets the tolerance for THIS run (what's acceptable?)
    │  Human approves for certification OR sends back for rework
    │  Output: human-approved tolerance + fix decisions
    │  If rework needed → routes back to Orchestrator
    │
    ▼
AUDITOR (FAA)
    │  Input: all evidence from D, M, J, QC + human-approved tolerance from TS
    │  Read Bedrock checklist — all 11 troubleshooting steps
    │  Verify: every checkbox has EVIDENCE behind it
    │  Verify: measurements meet HUMAN-SET tolerance (not self-set)
    │  Verify: HEIR stamped, ORBT set
    │  Verify: 15-section template complete
    │  DIFFERENT ENGINE than D, M, J, QC
    │  Output: CERTIFIED or REJECTED
    │  If rejected: diagnostic says what's missing
    │
    ▼
STRUCTURED, MAPPED, JOINED, CERTIFIED DATA
```

### Output
- Structured data with every element defined (description, ID, format)
- Mapping table connecting source to target
- Join path connecting data to spine
- Quality scorecard (ones and zeros)
- Auditor certification (or rejection with diagnostic)
- Complete 15-section documentation
- HEIR identity stamped
- ORBT state tracked

### Circle
QC scorecard feeds back to Orchestrator. If zeros exist, Orchestrator dispatches back to the appropriate agent. If Auditor rejects, Orchestrator reads the diagnostic and routes the fix. Sigma tracks across runs — tightening means the system is converging, flat means something isn't learning, expanding means something upstream broke.

---

## The Rules

1. **UP runs on EVERYTHING.** Every section. Every subsection. No exceptions. Simple or complex doesn't matter.
2. **Full 15-section template.** Every time. No abbreviated versions.
3. **Order is the constant.** Orchestrator → D → M → J → QC → TS (Human) → Auditor. Can't skip. Can't reorder.
4. **Evidence, not claims.** Every checkbox requires proof. The numbers. The key. The map. The join path. Not "I did it."
5. **Auditor is a different engine.** The builder cannot certify its own work.
6. **Nothing gets discarded.** Unidentified elements stored as KB-99. Today's unidentified is tomorrow's identified.
7. **Back-propagation is allowed.** J can send back to D via Orchestrator. The Circle closes.
8. **HEIR and ORBT are automatic.** The Auditor verifies they exist. If missing, reject.
9. **Every element gets three properties.** Description, Unique ID, Format. No exceptions. For LLMs and humans alike. Missing any one = not defined. The Auditor rejects anything without all three.
10. **All evidence must be reproducible.** Every QC scorecard includes the ACTUAL QUERIES that produced the numbers — not just the results. Any human can run the same query independently and get the same number. If they can't reproduce it, the evidence is invalid. LLMs can and do fabricate results. The query IS the proof. No query, no evidence. No evidence, no certification.
11. **LLMs lie.** This is a known risk, not a theoretical one. An LLM can generate perfect-looking scorecards with fabricated numbers. The guard rail is reproducibility — the human runs the query, gets the same number, or the scorecard is rejected. TS exists specifically because the human must verify, not trust.
12. **Auditor cannot certify without Dave's sign-off.** TS produces a tolerance decision signed by Dave. The Auditor checks for Dave's sign-off as a mandatory field. No sign-off = no certification. No exceptions. No "the human approved" — specifically Dave Barton. This is the ultimate guard rail. The system does not self-certify under any circumstances.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-03 |
| Version | 1.0.0 |
| Status | BUILD |
| Authority | Bedrock Foundation + DMJ |
| Location | factory/imo-creator/UP/ |
| BAR Reference | BAR-198 |

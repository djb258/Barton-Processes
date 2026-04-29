> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# PROCESS: BIT Scoring
## Composite scoring system (0-100 per company) combining sub-hub data points. RETIRED — replaced by direct data completeness checks in the LCS compiler.
### Status: RETIRED
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-600 |
| Name | BIT Scoring |
| Business Silo | svg-agency |
| CTB Position | factory/svg-agency/600-bit-scoring |
| ORBT | RETIRED |
| Strikes | N/A |
| Last Deployed | N/A — retired before production deployment |
| BAR Reference | N/A |
| Deployed URL | not deployed |
| Cron | none |
| Runtime | CF Worker (was planned) |

---

## 2. WHY THIS EXISTS

BIT Scoring was designed to produce a single composite score (0-100) per company by aggregating data points from multiple sub-hubs (people, blogs, enrichment). The score would indicate "readiness" for outreach — how much intelligence we had on a given company.

**Why it was retired (2026-03-25):** The score was a variable masquerading as a constant. A composite number hides which inputs changed. The individual data points are more useful than a single number that obscures signal. The LCS compiler's intelligence tier logic now performs direct data completeness checks against the actual fields, which is deterministic and transparent. No downstream process was starved by the removal.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

**RETIRED — this section documents what was planned, not what runs.**

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** — Was planned to run after enrichment passes completed
2. **"How do we get it?"** — Would aggregate columns across D1 sub-hub tables

### Input
Sub-hub data: people slots filled, blog data, enrichment fields, company metadata.

### Middle
Would have weighted and summed data completeness across sub-hubs into a single 0-100 score per company.

### Output
A composite score written to `outreach_bit_scores` (D1). **This table is deprecated. Do not reference.**

### Circle (Bedrock S5)
No feedback loop was established. The score was consumed downstream but never fed back to improve input quality — another sign it was a variable, not a constant.

---

## 4. WHAT IT GRABS OFF THE WALL

**RETIRED — no active dependencies.**

All tools and integrations have been decommissioned for this process.

---

## 5. OSAM — Where the Data Lives

**RETIRED — no active data paths.**

The `outreach_bit_scores` table in D1 is **deprecated**. Do not read from it, do not write to it, do not join against it.

The LCS compiler (Process 100) now handles intelligence tier classification directly by checking field completeness in the source tables.

---

## 6. CONSTANTS & VARIABLES (Bedrock S2)

### The Lesson (why this was retired)

The BIT score itself was the problem. It appeared to be a constant (a named, formatted thing — "BIT score, 0-100, per company"). But it failed the C&V test at the variable level:

- **IMO:** The score changed based on which sub-hub data was present — it was reactive, not fixed.
- **CTB:** At the trunk level, "how ready is this company?" is valid. At the leaf level, the composite number collapsed distinct signals into noise.
- **Circle:** The score never fed back to improve input quality. Dead-end output.

**Conclusion:** The individual data points (people slots filled, blog found, enrichment fields populated) are the real constants of structure. The composite score was an unnecessary abstraction layer — a variable pretending to add value by hiding specifics.

---

## 7. STOP CONDITIONS

Process is permanently stopped. ORBT: RETIRED.

---

## 8. DEPENDENCIES

### Upstream
None active. Former dependencies on sub-hub enrichment processes are now served directly by the LCS compiler (Process 100).

### Downstream
None. The LCS compiler replaced all downstream consumption of BIT scores with direct field-level completeness checks.

---

## 9. SMOKE TEST

No smoke test. Process is retired.

---

## 10. LOGBOOK

### 2026-03-25 — Process retired

**ORBT:** RETIRED
**Trigger:** Architecture review during LCS compiler v2 build
**Records processed:** 0
**Errors:** N/A
**Tools used:** None
**Result:** Process retired. Composite scoring replaced by direct data completeness checks in LCS compiler intelligence tier logic.
**Learnings:** A composite score is a variable masquerading as a constant. Individual data points are more useful than an aggregate that hides which inputs changed. Ingest to imo-brain.
**ORBT after:** RETIRED (permanent)

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-25 | Composite score hides signal | Score was a variable masquerading as a constant — aggregation destroyed useful granularity | Retired process. Replaced with direct field-level checks in LCS compiler. | N/A — retired, not repaired |

---

## 12. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-25 | Process retired during LCS compiler v2 architecture review | none |
| 2026-03-29 | PROCESS.md written to document retirement rationale | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | N/A — retired |
| Data Flow | N/A — retired |

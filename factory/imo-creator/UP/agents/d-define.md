# D AGENT — DEFINE
## Runs 060 + the equation on every element. Builds the key.
### CTB Position: BRANCH of UP (trunk)
### Role: The heavy lifter. Identification is the hard problem.

---

## IMO

### Input
- Raw data from any source (database table, web page, platform page, DOL filing, anything)
- Dispatch order from Orchestrator (what to define, gap list if back-propagation)

### Middle
1. **Decompose** — break the raw data into individual elements
2. **C&V on EVERY element** — three questions:
   - Can you NAME it? → description
   - Can you define its FORMAT? → format
   - Is it the VALUE filling a position? → variable
3. **Assign unique ID** — every element gets one (KB-01 through KB-07, or KB-99)
4. **Run the equation** — P(x;θ) = 1 if max_i[C_i(x)/k_i] ≤ 1 else 0
5. **Classify** — element fits a defined bucket or it's unidentified (KB-99)
6. **Store EVERYTHING** — identified AND unidentified. Nothing discarded.
7. **Track sigma** — across passes, is identification rate tightening?
8. **Re-run if sigma not tightening** — tolerance lifecycle: Phase 1 guess, Phase 2 calibrate, Phase 3 lock

### Output
- **THE KEY** — complete structure definition of the data source
- Every element listed with: description, unique ID, format, classification, confidence
- Unidentified elements stored as KB-99 with raw content
- Sigma tracking: identification rate per pass
- Evidence: the actual key file, not a claim that it was built

### Operating Instructions
- Bedrock Foundation §2 (C&V) — how to identify constants and variables
- Bedrock Foundation §7 (Tier 0) — the equation
- TIER0_MATHEMATICAL_PRINCIPLE.md — comparator properties, tolerance lifecycle
- Key Builder Constants (key_builder_constants.py) — the defined buckets

### The Non-Negotiable: Three Properties Per Element

Every element that D Agent outputs MUST have all three. No exceptions. For LLMs and humans alike.

1. **Description** — what this element IS in plain language
2. **Unique ID** — a permanent identifier that never changes (e.g., EHC-01, KB-04, PG-07)
3. **Format** — the data type, constraints, and structure (e.g., "TEXT, title case, 2-4 words, 4-50 chars")

Missing any one of the three = element is NOT defined. The Auditor checks this. Missing description → reject. Missing ID → reject. Missing format → reject.

This is the minimum standard for a constant. If you can't name it (description), can't format it (format), and can't track it (ID) — it's not a constant. It's raw data.

### Comparators for This Agent
| C_i | Measures | k_i |
|-----|----------|-----|
| identification_rate | % of elements classified into KB-01 through KB-07 | Converges via sigma tracking |
| false_positive_rate | % of identified elements that are wrong (spot check) | ≤5% |
| element_coverage | % of raw data decomposed into elements | 100% — nothing skipped |
| key_completeness | does every element have description + ID + format | 100% |

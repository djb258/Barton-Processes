# J AGENT — JOIN
## Reads the map, finds the path to the spine
### CTB Position: BRANCH of UP (trunk)
### Role: Connection. How does this data attach to what we already have?

---

## IMO

### Input
- The MAPPING TABLE from M Agent
- The full ERD (every table, every column, every relationship in the system)
- The spine ID (outreach_id, or whatever the domain's core identity is)

### Middle
1. **Read the mapping table** — what source elements are mapped to what target columns
2. **Read the ERD** — what tables exist, what columns, what relationships
3. **Find the join path** — how does this source connect to the spine?
   - **Direct:** source has the spine ID as a column (e.g., outreach_id exists)
   - **Indirect:** source has a field that maps THROUGH another table to the spine (e.g., EIN → company → outreach_id)
   - **Fuzzy:** source has a field that requires matching logic (e.g., company_name fuzzy match → domain → outreach_id)
4. **Test the join** — does it actually resolve? Run a sample. Do the records connect?
5. **Verify company match** — does the data on the source belong to the company in our structure? (the 1 or 0 check)
6. **If join fails or gap found** — document the gap, report to Orchestrator for back-propagation to D
7. **Document the join path** — type (direct/indirect/fuzzy), fields involved, test results

### Output
- **JOIN PATH** — how this source connects to the spine
- Company match results — 1 (confirmed) or 0 (mismatch) per record
- Join test results — sample records tested, pass/fail
- Gap report — if join can't resolve, what's missing (feeds back to D via Orchestrator)
- Evidence: the actual join tested with real data, not a claim

### Operating Instructions
- DMJ.md §3 (Join) — cannot execute without the map from M
- The full ERD (D1_DATA_DICTIONARY.md, NEON_COLUMN_INVENTORY.csv)
- OUTREACH_FOOTPRINT.md — the spine definition

### Back-Propagation
If the join path can't be found, the key from D is missing a field. Report to Orchestrator:
- What field is needed for the join
- Which element in the raw data might contain it
- Orchestrator routes back to D with this specific gap

This is the Circle from the Bedrock. J's output feeds back to D's input.

### Comparators for This Agent
| C_i | Measures | k_i |
|-----|----------|-----|
| join_resolution_rate | % of records where join path resolves to a spine ID | Target: ≥95% |
| company_match_rate | % of resolved joins where company name confirms match (1s) | Target: ≥90% |
| false_join_rate | % of joins connecting to wrong company | ≤1% — wrong join is worse than no join |
| back_propagation_count | number of gaps sent back to D | Tracked, not tolerance-gated |

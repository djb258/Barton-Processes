# M AGENT — MAP
## Reads the key, connects to target structure
### CTB Position: BRANCH of UP (trunk)
### Role: Wiring. Trivial once D is complete.

---

## IMO

### Input
- The KEY from D Agent (every element with description, ID, format)
- The target structure (what we want the data mapped into)

### Middle
1. **Read the key** — every element D identified
2. **Read the target structure** — the columns we need to fill
3. **For each identified element** — does it map to a target column?
   - Yes → record: source element ID → target column
   - No → element stays in key but has no map target (might be useful later)
4. **For each target column** — is there a source element mapped to it?
   - Yes → mapping complete for this column
   - No → gap. Document it. The data doesn't exist in this source for this column.
5. **Document the mapping table** — every connection, every gap

### Output
- **MAPPING TABLE** — source element → target column for every match
- Gap list — target columns with no source element
- Coverage metric — % of target columns that have a mapped source
- Evidence: the actual mapping table, not a claim

### Operating Instructions
- DMJ.md §2 (Map) — cannot execute without the key from D
- The target structure definition (e.g., slot_workbench columns, DATA_SOURCE_REGISTRY.md)

### Comparators for This Agent
| C_i | Measures | k_i |
|-----|----------|-----|
| mapping_coverage | % of target columns with a mapped source element | Varies by source — not all sources fill all columns |
| mapping_accuracy | % of mappings that connect correct source to correct target | 100% — wrong mapping is worse than no mapping |
| gap_documentation | every unmapped target column documented with reason | 100% |

# DOCTRINE — 600 BIT Scoring
# Per-process locked rules for PROC-BIT / Process 600
# Numbered D-600-XX. Monotonic. No gaps.
# Source attribution: heir.yaml (H), PRD.md (P), OSAM.md (O), MANIFEST.md (M), PROCESS.md (PR), CLAUDE.md (C)
# Gate: §8 stop / §9b gauge / pre-flight / external

> **STATUS: TROUBLESHOOT_TRAIN (RETIRED 2026-03-25)**
> These rules are preserved for audit and institutional memory. No active runtime exists. The outreach_bit_scores table is deprecated.

---

## Rule Table

| ID | Rule | Source | Gate |
|----|------|--------|------|
| D-600-01 | BIT scoring MUST run AFTER all upstream workers (Processes 200, 300, 400, 500) complete their enrichment passes for a given run window. | H: `acceptance_criteria[0]` "Runs AFTER all dumb workers complete"; H: `depends_on: [200, 300, 400, 500]`; O: anti-pattern "Run BIT before all sub-hubs complete" | §8 stop: if upstream not complete, BIT run is halted |
| D-600-02 | Authorization bands are fixed at 6 levels (0-5). The band structure — IDs, score ranges, names, and action labels — is invariant and may not be modified at runtime. | H: `bands` array (6 entries, ranges 0-9 through 80+); M: IMO section; P: R3 | §9b gauge: band count must equal 6 |
| D-600-03 | Outreach action rules are fixed per band: Band 0 = no outreach; Band 1 = internal flag only; Band 2 = 1 educational/60 days; Band 3 = persona-specific 3 max; Band 4 = phone warm 5 max; Band 5 = direct contact meeting request. These limits may not be exceeded. | H: `bands[*].action` values; M: bands table | §8 stop: action exceeding band limit triggers gate violation |
| D-600-04 | Within a scoring window, a company's BIT score may only increase or hold — it may not decrease due to noise. Score decreases require a full recalculation with updated signals, not a partial adjustment. | M: "Score can only increase within a scoring window" invariant | pre-flight: validate score delta direction before write |
| D-600-05 | Signal categories are fixed at exactly three: Structural Pressure (DOL — slow velocity, highest trust), Decision Surface (People — medium velocity, high trust), Narrative Volatility (Blog/News — fast velocity, lowest trust). No new categories may be added without a full architecture review. | H: `signal_sources` keys; O: signal weights table with category column | §8 stop: unclassified signal category halts scoring |
| D-600-06 | BIT reads from sub-hub source tables only. BIT NEVER writes to sub-hub source tables (outreach_company_target, outreach_dol, people_company_slot, outreach_blog). BIT's only write target is outreach_bit_scores (deprecated). | O: READ tables list; O: anti-pattern "Write directly to source tables"; P: non-requirements | §8 stop: any write to source table is a fatal violation |
| D-600-07 | Signal weights MUST be config-driven, not hardcoded constants in business logic. The 12 signal weights defined in heir.yaml are the canonical configuration source. Hardcoding weights in application code is forbidden. | O: anti-pattern "Hardcode signal weights"; O: signal weights table; PR: C&V analysis §6 (weights are variables, not constants) | pre-flight: config-driven weight loading verified before build |
| D-600-08 | BIT scores ONLY companies in the active agent territory. Scoring companies outside the territory boundary is forbidden regardless of data availability. | O: anti-pattern "Score companies outside agent territory"; P: non-requirements | §8 stop: out-of-territory company triggers skip, not score |
| D-600-09 | Component scores (people_score, dol_score, blog_score, talent_flow_score) MUST be stored alongside the composite score in every output record. Composite-only storage is forbidden — it destroys signal traceability. | P: R4 "Component scores stored separately for auditability"; O: outreach_bit_scores CANONICAL columns | §9b gauge: output row must contain all 4 component score columns |
| D-600-10 | outreach_id is the single join key across all outreach D1 tables. Cross-database joins are forbidden. Multi-hop joins must chain through outreach_id only. | O: ERD FK chain (outreach_company_target → outreach_dol, people_company_slot, outreach_blog → outreach_bit_scores, all via outreach_id); O: anti-pattern "Cross-database joins" | §8 stop: join on non-outreach_id key is a schema violation |
| D-600-11 | Gate 8 in the LCS pipeline (Process 100) is the sole authorized consumer of BIT score output. No other process may read directly from outreach_bit_scores for decision logic without an explicit architecture change logged in LBB. | H: `feeds: [100]`; P: R5 "Gate 8 integration" | external: LCS compiler change required to add any new consumer |
| D-600-12 | outreach_bit_scores D1 table is DEPRECATED effective 2026-03-25. Do not read from it, write to it, or join against it in any current or future process. The LCS compiler (Process 100) now performs intelligence tier classification via direct field-completeness checks against source tables. | C: "outreach_bit_scores table in D1 is deprecated. Do not reference."; PR: §5 OSAM "RETIRED — no active data paths" | §8 stop (permanent): any reference to outreach_bit_scores in new code is a doctrine violation |

---

## Rule Count: 12 (D-600-01 through D-600-12)

---

## Source Attribution Index

| Source File | Rules Derived |
|-------------|--------------|
| `heir.yaml` (acceptance_criteria, signal_sources, bands, feeds) | D-600-01, D-600-02, D-600-03, D-600-05, D-600-07, D-600-11 |
| `PRD.md` (R3, R4, R5, non-requirements) | D-600-02, D-600-03, D-600-08, D-600-09, D-600-11 |
| `OSAM.md` (READ/WRITE tables, anti-patterns, signal weights, FK chain) | D-600-01, D-600-05, D-600-06, D-600-07, D-600-08, D-600-09, D-600-10 |
| `MANIFEST.md` (IMO, bands, invariants) | D-600-02, D-600-03, D-600-04 |
| `PROCESS.md` (C&V analysis, retirement logbook) | D-600-07 |
| `CLAUDE.md` (retirement notice, deprecated table) | D-600-12 |

---

## Document Control

| Field | Value |
|-------|-------|
| Process | 600-bit-scoring |
| Process ID | PROC-BIT |
| ORBT | TROUBLESHOOT_TRAIN (RETIRED) |
| Rule Count | 12 |
| Created | 2026-04-29 |
| Template Version | UT v2.7.0 |
| Authority | imo-creator-v2 (sovereign ref) |

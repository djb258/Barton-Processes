# DOCTRINE — SVG D1 SEED (PROC-010)
## Locked Rules | Process 010 | D-010-XX Series

> **Source Attribution Key**
> - `[PROCESS]` = `PROCESS.md` (operational rules, forbidden paths, stop conditions)
> - `[AUDIT]` = `SEED_AUDIT.md` (audit gates, locked constants, fill rate baselines)
> - `[DESIGN]` = `SEED_V2_DESIGN.md` (design invariants, constants vs variables, phase architecture)
> - `[CTB]` = `MASTER_DATA_CTB.md` (column ownership rules, documentation gates)

---

| Rule ID | Rule | Source | Gate |
|---------|------|--------|------|
| D-010-01 | SEED direction is strictly Neon → D1; writes to Neon from D1 are forbidden at all times. | [PROCESS] §4 Forbidden Paths | §8 STOP CONDITION — halt immediately if reverse write attempted |
| D-010-02 | All D1 bulk writes MUST use `D1.batch()` with a maximum of ~100 statements per batch; single-row INSERT loops are forbidden. | [PROCESS] §4 Operational Rules | §9b gauge: D1 batch write error rate ≤ 10% |
| D-010-03 | All D1 INSERT statements MUST use `INSERT OR REPLACE` pattern for idempotency; bare INSERT is forbidden. | [PROCESS] §4 Operational Rules | Pre-flight item 7; §8 STOP if bare INSERT detected |
| D-010-04 | The coverage filter (Haversine ZIP gate via `coverage.v_service_agent_coverage_zips`) MUST be applied before every SEED run; seeding without the filter is forbidden. | [PROCESS] §3 IMO, §4 Gate 0 | Pre-flight item 5; §8 STOP if filter skipped |
| D-010-05 | The locked constant is 32,702 DISTINCT companies after coverage filter (`DISTINCT ON outreach_id`); any post-SEED count deviation greater than 20% from this baseline triggers a HALT. | [AUDIT] §1 The Gate | §9b gauge: company count = 32,702 ± 20% or HALT |
| D-010-06 | Join integrity audit (outreach_id spine) MUST return ≥ 95% coverage across all sub-hub tables before SEED is certified; below 95% triggers a HALT. | [PROCESS] §9 Smoke Tests | §8 STOP CONDITION — join integrity < 95% |
| D-010-07 | D1 write error rate MUST remain ≤ 10% per SEED run; rate above 10% triggers an immediate HALT and ORBT transitions to REPAIR. | [PROCESS] §9 Stop Conditions | §8 STOP CONDITION — error rate > 10% |
| D-010-08 | A column inventory snapshot (from `NEON_COLUMN_INVENTORY.csv` or equivalent) MUST be taken and reviewed before any SEED run; undocumented columns block the SEED for the affected table until documented. | [CTB] §1 Documentation Rate, [PROCESS] §5 Data Schema | Pre-flight item 6; §8 block gate |
| D-010-09 | SEED constants (sovereign ID, CT fields, EIN, ZIP, employee count, carrier, broker, renewal) are built once for the whole national universe and are free; SEED variables (people slots, email, LinkedIn) are filled only when an agent activates a geography — never pre-filled for the full universe. | [DESIGN] §Constants vs Variables | §2 Scope; §7 CONSTANTS & VARIABLES |
| D-010-10 | Materialized views `seed_views.v_agent_blog` and `seed_views.v_agent_fill_rates` MUST be refreshed after any data change in Neon before a SEED run reads from them. | [AUDIT] §Neon SEED Views | §9b gauge: materialized view refresh timestamp within 24h of run |
| D-010-11 | The `outreach_id` is the universal spine join key across all D1 sub-hub tables; cross-sub-hub queries that do not join via `outreach_id` are forbidden. | [PROCESS] §4 Forbidden Paths, §5 Data Schema | §9b gauge: 0 orphan slots (person_id not in people_master) |
| D-010-12 | All Neon queries during SEED run MUST route through Hyperdrive binding `HD_NEON`; direct Neon TCP connections from within D1 workers are forbidden. | [PROCESS] §3 Resources | Pre-flight item 4; §8 STOP if HD_NEON binding missing |

---

## Rule Count: 12

## Enforcement Cross-Reference

| Rule | §8 Stop | §9b Gauge | Pre-Flight | External |
|------|---------|-----------|------------|----------|
| D-010-01 | YES — halt | — | — | — |
| D-010-02 | — | batch error rate ≤ 10% | — | — |
| D-010-03 | YES — halt | — | Item 7 | — |
| D-010-04 | YES — halt | — | Item 5 | — |
| D-010-05 | YES — halt | count = 32,702 ± 20% | — | — |
| D-010-06 | YES — halt | join integrity ≥ 95% | — | — |
| D-010-07 | YES — halt | write error rate ≤ 10% | — | ORBT REPAIR trigger |
| D-010-08 | block gate | — | Item 6 | Column registry audit |
| D-010-09 | — | — | — | Design invariant (SEED v2) |
| D-010-10 | — | mat. view refresh < 24h | — | — |
| D-010-11 | — | 0 orphan slots | — | — |
| D-010-12 | YES — halt | — | Item 4 | — |

---

## Document Control

| Field | Value |
|-------|-------|
| Process ID | PROC-010 |
| Rule Series | D-010-01 through D-010-12 |
| Created | 2026-04-29 |
| Created By | Sonnet Runner (Wave 1 consolidation) |
| Source Files | PROCESS.md, SEED_AUDIT.md, SEED_V2_DESIGN.md, MASTER_DATA_CTB.md |
| UT Version | v2.7.0 |
| Authority | Foundational Bedrock — CC-04 leaf |

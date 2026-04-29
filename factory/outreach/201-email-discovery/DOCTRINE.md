> **ARCHIVED HEADER: Not archived — this is a NEW file written during UT v2.7.0 consolidation 2026-04-29.**

# DOCTRINE — 201 Email Discovery
<!-- Process: PROC-201 | Silo: svg-agency | Template: DOCTRINE v1.0.0 -->

Per-process locked rules. Each rule is a single declarative sentence. Numbered monotonically, no gaps. Source attribution and gate enforcement required on every rule.

**Rule ID format:** D-201-XX  
**Gate column values:** §8 stop / §9b gauge / pre-flight / external

---

## Rule Table

| Rule ID | Declarative Rule | Source | Gate |
|---------|-----------------|--------|------|
| D-201-01 | `person_email_verified` MUST track the Million Verifier (MV) verdict and MUST NOT be set to 1 based on the mere existence of a pattern guess or gate hit — this is the root cause of FP-201-01. | `heir.yaml` acceptance_criteria item 1; `PROCESS.md` §7 Stop Conditions (bounce rate trigger) | §8 stop — if `person_email_verified=1` rows exceed bounce threshold without MV confirmation, halt and REPAIR |
| D-201-02 | The process MUST only execute on slots where `has_name=1 AND has_email=0`; slots with `has_email=1` are out-of-scope and MUST be skipped without write. | `PROCESS.md` §5 Forbidden Paths ("Never write to a slot that already has_email=1") | §8 stop — write to occupied slot = immediate halt |
| D-201-03 | Pattern guesses generated in Gate A MUST NOT be written to the `person_email` field until a gate hit is confirmed (Gate B promote OR Gate C score ≥ 30); this is the CQRS gate for email discovery. | `heir.yaml` acceptance_criteria; assignment brief (2026-04-29) | §8 stop — any unconfirmed guess in `person_email` is a doctrine violation |
| D-201-04 | Gate execution order MUST be A → B → C; no gate may be skipped, reversed, or run in parallel — Gate B only runs if Gate A produced a candidate, Gate C only runs if Gate B did not promote. | `PROCESS.md` §3 Gate Order constant; `CLAUDE.md` Gate Chain definition | §8 stop — out-of-order gate execution halts the run |
| D-201-05 | A write to `person_email` MUST atomically set `has_email=1` in the same UPDATE statement; split writes (email written, flag set separately) are forbidden. | `PROCESS.md` §5 Forbidden Paths ("must be atomic"); `DATA_FLOW.md` write path SQL | §8 stop — non-atomic write = data integrity violation |
| D-201-06 | The 12-entry email pattern format map is a locked constant; no pattern may be added, removed, or reordered without a BAR (Build Action Request) and updated PROCESS-UT.md §7. | `PROCESS.md` §6 Constants (12 patterns enumerated); `find-email.py` `generate_from_pattern()` | pre-flight — verify pattern count == 12 before each run |
| D-201-07 | Gate B promotion threshold is `hunter_confidence ≥ 80`; this floor MUST NOT be lowered without a BAR and re-audit of bounce rate impact. | `heir.yaml` acceptance_criteria; `PROCESS.md` §3 Gate B definition | §9b gauge — `hunter_confidence` distribution monitored; floor compliance verified per run |
| D-201-08 | Gate C query template is `"{first} {last} {company} email contact"` and the acceptance score floor is ≥ 30 (domain match +100, first name in local +30, last name in local +30, first initial +5); score floor MUST NOT be lowered without a BAR. | `PROCESS.md` §3 Gate C definition; `find-email.py` scoring logic | §9b gauge — Gate C hit rate and score distribution monitored |
| D-201-09 | A JSONL audit trail file MUST be written per run; no run may execute without a designated output file path and the file MUST capture per-slot gate decisions (hit/miss/skip) and final write outcome. | `PROCESS.md` §6 Constants (output_file constant); `CLAUDE.md` operational notes | pre-flight — verify output path is set and writable before first slot processed |

---

## Rule Count: 9

## Source Files (pre-consolidation)

All source files archived to `_archived-fragments/` on 2026-04-29 during UT v2.7.0 standardization.

| File | Rules Extracted |
|------|----------------|
| `CLAUDE.md` | D-201-04 (gate chain) |
| `PROCESS.md` | D-201-02, D-201-04, D-201-05, D-201-06, D-201-07, D-201-08, D-201-09 |
| `heir.yaml` (acceptance_criteria) | D-201-01, D-201-03, D-201-07 |
| `DATA_FLOW.md` | D-201-05 (write path SQL) |
| Assignment brief 2026-04-29 | D-201-01 (FP-201-01 root cause), D-201-03 (CQRS gate) |

---

## Enforcement Cross-Reference

| §8 Stop Conditions | Rules | Halt Trigger |
|-------------------|-------|-------------|
| Bounce rate > 5% | D-201-01 | MV not tracking verdicts → false positives → bounces |
| Non-atomic write detected | D-201-05 | has_email=1 set without person_email in same UPDATE |
| Write to occupied slot | D-201-02 | has_email already 1 |
| Out-of-order gate | D-201-04 | Gate B or C ran without prerequisite |
| Unconfirmed guess in person_email | D-201-03 | CQRS gate violation |

| §9b Live Gauges | Rules | What to Measure |
|----------------|-------|----------------|
| Verified email count | D-201-01 | `SELECT COUNT(*) FROM slot_workbench WHERE person_email_verified=1` |
| Hunter confidence floor | D-201-07 | `SELECT MIN(hunter_confidence) FROM slot_workbench WHERE hunter_confidence > 0` |
| Gate C score distribution | D-201-08 | Review run JSONL for score histogram |
| JSONL file written | D-201-09 | `ls -la output/run_*.jsonl` — file must exist after every run |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-29 |
| Version | 1.0.0 |
| Template | DOCTRINE v1.0.0 |
| Process | PROC-201 |
| Governing UT | `PROCESS-UT.md` (sibling) |
| Status | LOCKED (human amendment only after BAR) |

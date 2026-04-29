# DOCTRINE — PROC-301 Page Parser
<!-- DOCTRINE v1.0.0 | Process: 301-page-parser | Generated: 2026-04-29 | UT v2.7.0 -->

## Authority

These rules are locked operational constants for PROC-301. Each rule is a declarative sentence derived from `heir.yaml` acceptance criteria, `PROCESS.md` operational rules, `CLAUDE.md` per-process governance, and `src/key_builder_constants.py` invariants. All rules are numbered monotonically. No gaps.

§7 of `PROCESS-UT.md` cites these rules by ID. §8 of `PROCESS-UT.md` cites rule violations that halt execution.

---

## Rule Table

| Rule ID | Rule (declarative sentence) | Source | Gate / Enforcement |
|---------|----------------------------|--------|-------------------|
| D-301-01 | One fetch is performed per company (one `about_url`) — not per slot, not per field, not per position. | CLAUDE.md §Boundaries, PROCESS.md §7 | §8 stop condition; pre-flight check |
| D-301-02 | The 7-step pipeline sequence is fixed and immutable: FETCHER → DECOMPOSER → KEY BUILDER → QUALITY GATE → ORGANIZER → SLOT FILLER → RECALC; no step may be skipped or reordered. | PROCESS.md §5 Middle table | §8 stop condition; pre-flight check |
| D-301-03 | `key_builder_constants.py` (BUCKETS KB-01..KB-07+KB-99, POSITIONS set, NAME_REJECT_WORDS, GENERIC_EMAIL_PREFIXES, regex patterns) are locked structural constants — no runtime modification, no process-level override. | src/key_builder_constants.py header comment | §9b gauge; pre-flight check; external audit |
| D-301-04 | Every element that does not fit a defined bucket (KB-01..KB-07) is classified as KB-99 (unidentified) and stored — never silently discarded. | src/key_builder_constants.py BUCKETS["unidentified"] | §9b gauge (unidentified_element_stored_rate); pre-flight check |
| D-301-05 | This process does not write to `readiness_tier` — `readiness_tier` is owned exclusively by `recalc_tier.py` (PROC-TBV). | CLAUDE.md §Forbidden, PROCESS.md §8 | §8 stop condition; pre-flight check |
| D-301-06 | This process does not write `person_email` to any slot — email discovery is owned exclusively by PROC-201. | CLAUDE.md §Forbidden, PROCESS.md §8 | §8 stop condition; pre-flight check |
| D-301-07 | This process does not issue Startpage search queries — Startpage is forbidden for page parsing. | CLAUDE.md §Forbidden | §8 stop condition; pre-flight check |
| D-301-08 | This process does not scrape LinkedIn directly — LinkedIn scraping is out of scope for this process. | CLAUDE.md §Forbidden | §8 stop condition; pre-flight check |
| D-301-09 | `about_url` (from `slot_workbench`) is the only source URL for this process — no URL discovery, no link-following, no supplemental URL generation within this process. | CLAUDE.md §Boundaries, PROCESS.md §4 | §8 stop condition; pre-flight check |
| D-301-10 | The URL classification taxonomy is fixed at exactly 10 mutually exclusive categories: `linkedin_profile`, `company_page`, `linkedin_company`, `directory`, `job_site`, `government`, `academic`, `social`, `pdf`, `noise` — no category may be added, removed, or merged at runtime. | src/classify-urls.py `classify_url()` function | §9b gauge; pre-flight check; external audit |
| D-301-11 | Direct fetch via `curl_cffi` is always attempted first; DataImpulse residential proxy is invoked only on direct fetch failure or `403`/`429` response — never as the primary channel. | PROCESS.md §7 FETCHER step, CLAUDE.md §Tools | §9b gauge (proxy_escalation_rate); pre-flight check |
| D-301-12 | All classified elements — both identified (KB-01..KB-07) and unidentified (KB-99) — are stored to `slot_workbench` per page; no silent drops on successful parse. | PROCESS.md §7 SLOT FILLER step | §9b gauge; §8 stop condition on write_failure_count > ε |
| D-301-13 | Execution halts and the process reports a STOP condition when `fetch_failure_rate` exceeds 30% over any 50-company window — this indicates a systemic fetch problem requiring operator intervention. | PROCESS.md §8 Stop Conditions, heir.yaml acceptance_criteria | §8 stop condition; §9b gauge C_1 (k=0.20 warn, 0.30 halt) |
| D-301-14 | Execution halts when no person names are found on 10 or more consecutive pages — this indicates a parser failure, not a data absence pattern. | PROCESS.md §8 Stop Conditions | §8 stop condition; §9b gauge C_3 |
| D-301-15 | Execution halts when D1 write error count exceeds 1% of attempted writes — data integrity is non-negotiable and write failures must not be silently swallowed. | PROCESS.md §8 Stop Conditions, heir.yaml acceptance_criteria | §8 stop condition; §9b gauge C_6 (k=ε) |

---

## Source Attribution Legend

| Source Tag | File | Description |
|-----------|------|-------------|
| `CLAUDE.md §Boundaries` | `_archived-fragments/CLAUDE.md` | Per-process CLAUDE.md boundaries section |
| `CLAUDE.md §Forbidden` | `_archived-fragments/CLAUDE.md` | Per-process CLAUDE.md forbidden operations |
| `CLAUDE.md §Tools` | `_archived-fragments/CLAUDE.md` | Per-process CLAUDE.md tool list |
| `PROCESS.md §4` | `_archived-fragments/PROCESS.md` | Section 4 (Constants & Variables) of original PROCESS.md |
| `PROCESS.md §5` | `_archived-fragments/PROCESS.md` | Section 5 (Middle) of original PROCESS.md |
| `PROCESS.md §7` | `_archived-fragments/PROCESS.md` | Section 7 (Constants & Variables / pipeline) of original PROCESS.md |
| `PROCESS.md §8` | `_archived-fragments/PROCESS.md` | Section 8 (Stop Conditions) of original PROCESS.md |
| `heir.yaml acceptance_criteria` | `heir.yaml` | V2 HEIR acceptance criteria array |
| `src/key_builder_constants.py` | `src/key_builder_constants.py` | Snap-On Tool — bucket definitions, POSITIONS, classification logic |
| `src/classify-urls.py` | `src/classify-urls.py` | URL classifier — 10-category taxonomy |

---

## Rule Count Summary

- Total rules: **15** (D-301-01 through D-301-15)
- Boundary rules (what this process does/does not do): D-301-01, D-301-05, D-301-06, D-301-07, D-301-08, D-301-09
- Structural constants (locked tools/schemas): D-301-03, D-301-04, D-301-10
- Pipeline invariants (sequence, method): D-301-02, D-301-11, D-301-12
- Stop conditions (halt triggers): D-301-13, D-301-14, D-301-15

---

## Document Control

| Field | Value |
|-------|-------|
| Process | PROC-301 page-parser |
| Version | 1.0.0 |
| Created | 2026-04-29 |
| Template | DOCTRINE v1 per STAGE-1-CODEX-MECHANIC-OUTPUT.md §3 |
| Status | BUILD — pending Codex audit (Stage 3) |
| Amend via | Human + gate enforcement only — no LLM rule additions post-audit |

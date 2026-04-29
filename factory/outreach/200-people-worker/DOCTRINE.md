# DOCTRINE — Process 200 People Worker
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-200-01 | A company must have at least one reachable slot (verified email OR LinkedIn URL) before it can enter the LCS pipeline. | heir.yaml `acceptance_criteria[0]`, `reachability_gate.rule` | §8 stop |
| D-200-02 | Well-drinks tools (MXLookup, SMTPCheck, LinkedInCheck — TOOL-001/002/003) must be exhausted before any top-shelf tool (Hunter, Apollo, MillionVerifier) is invoked. | heir.yaml `acceptance_criteria[1]`, `tool_priority` | §8 stop |
| D-200-03 | Every data point written to D1 must be tagged with `source_tool` and a timestamp; untagged records are invalid. | heir.yaml `acceptance_criteria[2]`, `schema_approach` | §9b gauge |
| D-200-04 | A monthly snapshot diff must be performed slot-by-slot, comparing current month to previous month, to produce the binary movement flag. | heir.yaml `acceptance_criteria[3]`, `movement_detection` | §9b gauge |
| D-200-05 | Movement detection output must be binary: 0 (no change) or 1 (movement detected); no probabilistic or AI-derived movement scoring is permitted. | heir.yaml `acceptance_criteria[4]`, `movement_detection.ai_required = false` | §8 stop |
| D-200-06 | DOL-linked companies must be prioritized for enrichment in the order: (1) DOL + movement + empty slots, (2) DOL + no movement + empty slots, (3) non-DOL companies. | heir.yaml `acceptance_criteria[5]`, `enrichment_priority` | pre-flight |
| D-200-07 | All errors must be written to the master error table in D1; no silent failure or log-only error handling is permitted. | heir.yaml `acceptance_criteria[6]`, `services` | §8 stop |
| D-200-08 | The wide schema rule must be followed: all available data points are collected per slot; the decision about which fields matter is deferred to Monte Carlo analysis. | heir.yaml `acceptance_criteria[7]`, `schema_approach` | pre-flight |
| D-200-09 | Only three slot types are permitted: CEO, CFO, HR — in that priority order; no other slot types may be created or filled. | heir.yaml `slots.types`, `slots.priority` | §8 stop |
| D-200-10 | The worker must never query Neon directly during the WORK phase; all WORK-phase reads and writes go to D1 (D1_OUTREACH or D1_SPINE); Neon is accessed only during SEED and PUSH phases. | PRD.md R7 "non-requirements", CLAUDE.md governance | §8 stop |
| D-200-11 | During Pass 2 (Startpage search via DataImpulse proxy), the proxy must be invoked with sticky session POST form and a 3–8 second randomized delay between fetches; direct unauthenticated Startpage requests are forbidden. | OSAM.md forbidden paths, CLAUDE.md Pass 2 | §8 stop |
| D-200-12 | `person_email_verified = 1` must only be set when MillionVerifier has returned a confirmed valid result (MV_PASS); setting this flag without a passing MV result is a Strike-class violation (FP-200-01). | PROCESS.md §13 failure registry, FP-200-01 | §9b gauge |
| D-200-13 | Source trust hierarchy must be respected: DOL_LINKED > Hunter > Clay; when data conflicts between sources, the higher-trust source wins. | heir.yaml `source_trust` | pre-flight |
| D-200-14 | D1_SPINE (svg-d1-spine, 641a9a1e) is read-only; no writes, updates, or deletes may be issued against D1_SPINE tables; canonical company identity data is consumed, never mutated. | OSAM.md `query_routing`, forbidden paths | §8 stop |
| D-200-15 | The slot-fill target is ≥60% of eligible slots filled with at least one reachable contact method per monthly cycle; falling below this threshold triggers a REPAIR review. | PRD.md definition of done, R1 | §9b gauge |
| D-200-16 | Pass 0 (staging promotion from `intake_people_staging`) must run before any external fetch pass; promoting staged data costs $0 and must not be skipped. | CLAUDE.md Pass 0, PROCESS.md gate chain | pre-flight |

## Cross-references
- UT §7 Constants & Variables references these rules by ID (D-200-01 through D-200-16)
- UT §8 Stop Conditions cites the violations that halt (D-200-01, D-200-02, D-200-05, D-200-07, D-200-09, D-200-10, D-200-11, D-200-12, D-200-14)
- §9b Live Verification gauges measure compliance for D-200-03 (source_tool coverage), D-200-04 (snapshot diff count), D-200-12 (FP-200-01 spurious flag count), D-200-15 (slot fill rate)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-29 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |

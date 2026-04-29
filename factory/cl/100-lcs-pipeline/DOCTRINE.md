# DOCTRINE - Process 100 LCS Pipeline
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-100-01 | SID construction must gate on `has_verified_email = 1` in `slot_workbench`; the legacy column `person_email_verified` must never be used as the email verification gate. | extracted from heir.yaml (acceptance_criteria[0]) + special context (quarantine-356-2026-04-28) + OSAM.md (anti-patterns) | §8 stop |
| D-100-02 | Every Mailgun send must include `Reply-To: dave@svg.agency` in the message headers. | extracted from CLAUDE.md (domain rotation section) | §8 stop |
| D-100-03 | The pipeline must execute in three sequential stages only: CID → SID → MID; each stage must append a row to `lcs_event` before proceeding to the next stage. | extracted from heir.yaml (acceptance_criteria[1,2]) + PRD.md (R8) | §8 stop |
| D-100-04 | All pipeline configuration must be read from D1 registry tables (`lcs_domain_rotation`, `lcs_signal_types`, `lcs_outreach_templates`); no configuration values may be hardcoded in worker source. | extracted from PRD.md (R9) + OSAM.md (anti-patterns: "Hardcode from/reply-to addresses") | §8 stop |
| D-100-05 | Domain selection must use least-recently-used (LRU) ordering from `lcs_domain_rotation` where `sent_today < daily_cap AND is_paused = 0`; the rotation pool is capped at 14 domains. | extracted from CLAUDE.md (domain rotation section) + special context | §9b gauge |
| D-100-06 | Slot priority for recipient selection must follow CFO → CEO → HR Contact order; only the first matching slot per company may be promoted to SID. | extracted from PROCESS.md (constants: slot_priority) + PRD.md (R3) | pre-flight |
| D-100-07 | Only intelligence tiers 2–5 (section_count 2–5) are eligible for SID construction; tier 1 (section_count < 2) must remain in the staging queue. | extracted from PROCESS.md (constants: intelligence_tier) + OUTREACH_FOOTPRINT.md (tier table) | pre-flight |
| D-100-08 | The ORBT 3-strike protocol for failed MIDs must follow AUTO_RETRY → ALT_CHANNEL → HUMAN_ESCALATION; Strike 3 on the same failure pattern triggers TROUBLESHOOT_TRAIN and an Airworthiness Directive. | extracted from heir.yaml (acceptance_criteria[3]) + PRD.md (R6) + MANIFEST.md (ORBT 3-strike protocol) | §8 stop |
| D-100-09 | Every `communication_id` must conform to the format `LCS-{PHASE}-{DATE}-{ULID}` and must be bidirectionally traceable via the `/trace/{id}` endpoint. | extracted from MANIFEST.md (ID format table) + heir.yaml (acceptance_criteria[1]) | pre-flight |
| D-100-10 | If a domain's bounce rate exceeds 2% within any 24-hour window, the domain must be automatically paused by setting `is_paused = 1` in `lcs_domain_rotation`; no sends may occur on a paused domain. | extracted from special context (quarantine-356-2026-04-28 root cause) | §9b gauge |
| D-100-11 | All pipeline processing operations must execute against D1 only; Neon PostgreSQL is the vault (SEED_WORK_PUSH pattern); no direct Neon queries are permitted during pipeline execution. | extracted from heir.yaml (acceptance_criteria[4]) + OSAM.md (anti-patterns: "Query Neon during pipeline processing") | §8 stop |
| D-100-12 | The LCS pipeline must never write to the outreach D1 database (`outreach_hub`); all outreach D1 data is read-only from LCS pipeline context. | extracted from OSAM.md (cross-database write rule) + PRD.md (R10 non-requirements) | §8 stop |

## Cross-references
- UT §7 Constants & Variables references these rules by ID (D-100-01 through D-100-12)
- UT §8 Stop Conditions cites D-100-01, D-100-02, D-100-03, D-100-04, D-100-08, D-100-11, D-100-12 as halt triggers
- UT §9b Live Verification gauges measure D-100-05 (domain rotation) and D-100-10 (bounce rate) compliance

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-29 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes - only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |

# DOCTRINE — Process 280 Problem Source Discovery
## Locked rules. Auditor enforces. Violations break AI classification accuracy or reply integrity.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-280-01 | CLASSES enum is the canonical classification taxonomy for all incoming messages. Every inbound email classified by the inbox-agent MUST resolve to one of the defined CLASSES values. Unknown or unmapped classifications are forbidden — they route to a default bucket, never silently discarded. | inbox-agent.ts CLASSES enum | §5 stop — unclassified messages drop out of the pipeline |
| D-280-02 | DRAFT_RULES is the locked set of reply-drafting rules. Every AI-drafted reply MUST comply with all active DRAFT_RULES. Rules are constants — they do not vary per message or per campaign. Additions require a BAR. | inbox-agent.ts DRAFT_RULES | §5 stop — rule drift produces off-brand or non-compliant AI replies |
| D-280-03 | OpenRouter claude-sonnet-4-5 is the sole LLM used for classification and reply drafting. Model substitution requires a BAR. The model is invoked via OpenRouter API — direct Anthropic API calls are forbidden on this route. | inbox-agent.ts (OpenRouter client) | §5 stop — model substitution changes classification behavior without a reviewed gate |
| D-280-04 | problem_source_chain is the canonical chain-of-thought prompt sequence for problem source discovery. Every classification run MUST execute the full chain. Partial chain execution (skipping steps) is a doctrine violation. | inbox-agent.ts problem_source_chain | §5 stop — partial chain produces unreliable source attribution |
| D-280-05 | The inbox-agent operates in AI auto-reply mode. Drafted replies are written to a staging table before sending. No reply may be sent directly from the classification pipeline without passing through the staging gate. | inbox-agent.ts auto-reply architecture | §9 stop — direct send bypasses human review gate on AI-authored content |
| D-280-06 | Migration 0019 defines the canonical schema for problem_source_chain records. All writes to the problem source discovery tables MUST conform to migration 0019. Schema drift outside a BAR is a violation. | migration 0019 (inbox-agent) | §7 stop — schema drift breaks JOIN with campaign engine downstream |
| D-280-07 | The inbox-agent's D1 database is the canonical store for all classified messages and problem source records. KV cache may be used for session-level deduplication only. No KV write may create a canonical record — D1 is always the source of truth. | inbox-agent.ts (D1 binding) | §5 stop — KV canonical records are unversioned and unauditable |
| D-280-08 | Classification output (CLASSES value + confidence) must be stored alongside the original message_id. Every classification record must be traceable back to a source message. Orphan classifications (no message_id) are forbidden. | inbox-agent.ts classification schema | §6 stop — orphan classifications poison problem source attribution |
| D-280-09 | The inbox-agent is a read-write process on D1 but is READ-ONLY with respect to the outreach contact record (people table). It may read contact data to enrich classifications but may never write to the people table directly. Contact mutations require routing through the people-worker (Process 200). | inbox-agent.ts + Process 200 DOCTRINE | §9 stop — direct contact mutations bypass the people-worker governance gate |
| D-280-10 | Problem source discovery output feeds the campaign engine (Process 700). The JOIN key between problem source records and campaign records is the sovereign_company_id. Every problem source record MUST carry sovereign_company_id as a non-nullable field. | inbox-agent.ts + Process 700 architecture | §6 stop — missing sovereign_company_id breaks the campaign engine JOIN |

## Cross-references
- UT §5 CONTRACT references D-280-01 (CLASSES enum), D-280-02 (DRAFT_RULES), D-280-04 (problem_source_chain)
- UT §4 IMO references D-280-03 (OpenRouter), D-280-05 (staging gate)
- UT §6 JOIN CONTRACT references D-280-08 (message_id traceability), D-280-10 (sovereign_company_id)
- UT §7 SCHEMA references D-280-06 (migration 0019)
- UT §9 PERMISSIONS references D-280-05 (staging gate), D-280-09 (people table read-only)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| BAR | BAR-315 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 |
| Rule Count | 10 (D-280-01 through D-280-10) |

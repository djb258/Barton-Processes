# DOCTRINE - Process 700 Campaign Engine
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-700-01 | Every MID must be tagged with path_type, channel, movement_signal, and sequence_position before delivery — untagged MIDs are untraceable and must be blocked. | heir.yaml acceptance_criteria + PROCESS.md §5 Forbidden Paths | §8 stop |
| D-700-02 | Campaign model selection is binary: any movement signal detected in any of the three slots (CEO/CFO/HR) triggers MOVEMENT_DETECTED (3-5 touches over 2 weeks); zero movement across all slots triggers NO_MOVEMENT (1 touch monthly). | heir.yaml campaign_models + PROCESS.md §3 Middle Step 1 | §9b gauge |
| D-700-03 | The sequencer reads MIDs from Process 100 (LCS Pipeline) — it does not generate new message identifiers; every MID must trace back to a CID compiled by Process 100. | heir.yaml depends_on + PROCESS.md §8 Upstream Dependencies | §8 stop |
| D-700-04 | No MID is delivered to a recipient on the suppression list — the campaign engine must check suppression status before routing to Composio; delivery to a suppressed contact is a CQRS write violation. | PROCESS.md §5 Forbidden Paths + CLAUDE.md Acceptance Criteria | §8 stop |
| D-700-05 | The campaign engine does not run until Process 100 (LCS Pipeline) has completed its CID compilation for the current cycle — cadence depends on Process 100 completion. | heir.yaml depends_on: [100] + PROCESS.md §8 Upstream | pre-flight |
| D-700-06 | No-movement cadence is exactly 1 touch per month per company; movement cadence is 3-5 touches spaced every 2-3 days over approximately 2 weeks — cadence deviations are a zero-tolerance violation. | heir.yaml campaign_models + PROCESS.md §6 Constants | §9b gauge |
| D-700-07 | Every MID must contain a CTA link (schedule a meeting) — messages without a CTA link must not be sent. | heir.yaml acceptance_criteria + CLAUDE.md Acceptance Criteria | §8 stop |
| D-700-08 | Errors (bounces, failed deliveries) must write to the master error table in D1 — errors may not be silently dropped. | heir.yaml acceptance_criteria + PROCESS.md §5 WRITE Access | §9b gauge |
| D-700-09 | Movement campaigns require a specific movement signal type (JOINED, LEFT, REPLACED, TITLE_CHANGED, EMAIL_CHANGED) — no movement signal means generic monthly only; a movement model cannot be triggered without the signal. | PROCESS.md §5 Forbidden Paths + CLAUDE.md MID Tagging | §8 stop |
| D-700-10 | Composio is the only routing layer to Mailgun and HeyReach — direct API calls to Mailgun or HeyReach that bypass Composio are forbidden. | PROCESS.md §4 Snap-On Toolbox + CLAUDE.md Tools | pre-flight |

## Cross-references
- UT §7 Constants & Variables references these rules by ID
- UT §8 Stop Conditions cites the violations that halt
- §9b Live Verification gauges measure compliance where measurable

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-28 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes - only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |

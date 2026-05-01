# DOCTRINE — Process 280 LCS Delivery Hub
## Locked rules. Auditor enforces. Violations break email delivery state or campaign queue integrity.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-LCS280-01 | SenderDomain is the canonical shape for all sending domain records. Required fields: domain, status, daily_limit, sent_today, warmup_phase. Backend must return this shape from the /lcs/delivery-status endpoint. Shape drift outside a BAR breaks the LCSDelivery.tsx render contract. | LCSDelivery.tsx SenderDomain interface | §5 stop — shape drift breaks the delivery status dashboard |
| D-LCS280-02 | FireDailyRun is the canonical shape for daily send run records. Required fields: run_id, fired_at, total_sent, total_failed, domains_used. Every daily run MUST produce a FireDailyRun record. Runs without records are governance violations. | LCSDelivery.tsx FireDailyRun interface | §5 stop — missing run records break the audit trail and delivery metrics |
| D-LCS280-03 | CampaignQueueItem is the canonical shape for queued campaign sends. Required fields: queue_id, campaign_id, contact_id, scheduled_at, status (enum: pending / sent / failed / skipped). Queue items with missing status are rejected at the write gate. | LCSDelivery.tsx CampaignQueueItem interface | §5 stop — statusless queue items make campaign delivery unauditable |
| D-LCS280-04 | The /lcs/delivery-status endpoint is the sole data source for LCSDelivery.tsx. It MUST return SenderDomain[] + FireDailyRun[] in a single response. LCSDelivery.tsx may not call additional endpoints to complete its render — it is a single-fetch component. | LCSDelivery.tsx fetch architecture | §5 stop — multi-fetch renders create partial-state UI on any single endpoint failure |
| D-LCS280-05 | daily_limit and sent_today on SenderDomain drive the warmup throttle. The scheduler MUST enforce daily_limit — no domain may send more emails than daily_limit in a 24-hour window. Exceeding daily_limit is a deliverability violation. | SenderDomain.daily_limit + scheduler | §5 stop — overlimit sends trigger spam filters and damage domain reputation |
| D-LCS280-06 | warmup_phase on SenderDomain is an enum: cold / warming / warm / paused. A domain in paused warmup_phase MUST NOT receive scheduled sends. The scheduler enforces this filter before queue processing. | SenderDomain.warmup_phase | §5 stop — sending on a paused domain collapses its deliverability score |
| D-LCS280-07 | CampaignQueueItem.status transitions are one-directional: pending → sent OR pending → failed OR pending → skipped. No status may revert. A sent item cannot be re-queued. Reversions require a new queue item, not a status update on an existing one. | CampaignQueueItem.status enum | §6 stop — status reversions corrupt campaign send history |
| D-LCS280-08 | The lcs-hub is a write-only process with respect to contact records. It may READ contact data (contact_id, email address) for queue population but may never WRITE to the contacts table. Contact mutations route through the people-worker (Process 200). | LCS delivery architecture | §9 stop — direct contact writes from the delivery hub bypass people-worker governance |
| D-LCS280-09 | FireDailyRun.domains_used is an array of domain strings representing which SenderDomains fired in that run. It must be populated at run completion — an empty domains_used array on a completed run with total_sent > 0 is a violation. | FireDailyRun interface | §5 stop — missing domains_used makes per-domain deliverability attribution impossible |
| D-LCS280-10 | The LCS Delivery Hub is scoped to SVG Agency outreach (BRANCH 1 — SVG Agency Hub: Outreach). It must not send on behalf of other entities (Briar Valley, Personal). Cross-entity sends are a sovereign-silo violation. | law/BARTON_ENTERPRISES_CTB.md Sovereign Silos rule | §9 stop — cross-entity sending exposes non-SVG domains to SVG Agency deliverability risk |

## Cross-references
- UT §5 CONTRACT references D-LCS280-01 (SenderDomain), D-LCS280-02 (FireDailyRun), D-LCS280-03 (CampaignQueueItem), D-LCS280-05 (daily_limit), D-LCS280-06 (warmup_phase)
- UT §4 IMO references D-LCS280-04 (/lcs/delivery-status single fetch), D-LCS280-07 (status transitions)
- UT §6 JOIN CONTRACT references D-LCS280-03 (queue_id → campaign_id → contact_id chain)
- UT §9 PERMISSIONS references D-LCS280-08 (contacts read-only), D-LCS280-10 (entity scope)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| BAR | BAR-357 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 |
| Rule Count | 10 (D-LCS280-01 through D-LCS280-10) |

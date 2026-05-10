-- ═══════════════════════════════════════════════════════════════
-- Migration 002 — Add sender_domain to mid table
-- ═══════════════════════════════════════════════════════════════
-- Required by RIM-GATE / THROUGHPUT-CONTROL template
-- (imo-creator-v2/atlas/templates/rim-gate/throughput-control/UT.md §7).
-- Per-domain bounce/complaint stats are computed from mid filtered by
-- sender_domain. Single column add — no new tables (sovereign rule).
-- ═══════════════════════════════════════════════════════════════

ALTER TABLE mid ADD COLUMN sender_domain TEXT;

CREATE INDEX IF NOT EXISTS idx_mid_sender_domain ON mid(sender_domain);
CREATE INDEX IF NOT EXISTS idx_mid_sender_domain_sent ON mid(sender_domain, delivery_status, sent_at);

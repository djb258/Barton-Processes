-- ═══════════════════════════════════════════════════════════════
-- Process 820 — D1 Export Tracking Tables
-- ═══════════════════════════════════════════════════════════════
-- Reads canonical from 810's D1 (shared or API).
-- This D1 tracks export history and errors.
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS export_log (
  export_id       TEXT PRIMARY KEY,
  client_id       TEXT NOT NULL,
  vendor_id       TEXT NOT NULL,
  blueprint_id    TEXT NOT NULL,
  record_count    INTEGER NOT NULL DEFAULT 0,
  file_format     TEXT NOT NULL DEFAULT 'csv',
  status          TEXT NOT NULL DEFAULT 'completed',
  exported_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_export_log_client ON export_log(client_id);
CREATE INDEX IF NOT EXISTS idx_export_log_vendor ON export_log(vendor_id);
CREATE INDEX IF NOT EXISTS idx_export_log_date ON export_log(exported_at);

CREATE TABLE IF NOT EXISTS export_error (
  error_id        TEXT PRIMARY KEY,
  client_id       TEXT NOT NULL,
  vendor_id       TEXT,
  export_id       TEXT,
  error_code      TEXT NOT NULL,
  error_message   TEXT NOT NULL,
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_export_error_client ON export_error(client_id);

CREATE TABLE IF NOT EXISTS export_schedule (
  schedule_id     TEXT PRIMARY KEY,
  vendor_id       TEXT NOT NULL,
  frequency       TEXT NOT NULL,
  last_run_at     TEXT,
  next_run_at     TEXT,
  status          TEXT NOT NULL DEFAULT 'active'
);

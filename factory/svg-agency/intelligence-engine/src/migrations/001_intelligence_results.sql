-- ═══════════════════════════════════════════════════════════════
-- Intelligence Engine — D1 Schema
-- Migration 001: Core tables for results and queue state
-- ═══════════════════════════════════════════════════════════════

-- ── Intelligence Results ─────────────────────────────────────
-- Every fetch result lands here. One row per job execution.
-- This is the primary output table read by BIT scoring and dashboards.

CREATE TABLE IF NOT EXISTS intelligence_results (
  job_id             TEXT PRIMARY KEY,
  job_type           TEXT NOT NULL,
  company_unique_id  TEXT NOT NULL,
  person_id          TEXT,

  -- Signal classification
  signal_type        TEXT NOT NULL,
  signal_score       INTEGER NOT NULL DEFAULT 0,

  -- Raw search output
  raw_snippet        TEXT NOT NULL DEFAULT '',

  -- Parsed structured data (JSON)
  parsed_data        TEXT NOT NULL DEFAULT '{}',

  -- Keywords that matched from templates
  keyword_matches    TEXT NOT NULL DEFAULT '[]',

  -- Movement detection (linkedin_profile jobs only)
  movement_detected  INTEGER,    -- 0 or 1
  movement_type      TEXT,       -- COMPANY_CHANGE, TITLE_CHANGE, NO_CHANGE, PARSE_INCOMPLETE

  -- Fetch metadata
  search_engine      TEXT NOT NULL DEFAULT 'startpage',
  http_status        INTEGER NOT NULL DEFAULT 0,
  duration_ms        INTEGER NOT NULL DEFAULT 0,
  fetched_at         TEXT NOT NULL,
  error              TEXT
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_ir_company
  ON intelligence_results (company_unique_id);

CREATE INDEX IF NOT EXISTS idx_ir_person
  ON intelligence_results (person_id)
  WHERE person_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ir_type
  ON intelligence_results (job_type);

CREATE INDEX IF NOT EXISTS idx_ir_signal_score
  ON intelligence_results (signal_score DESC)
  WHERE error IS NULL;

CREATE INDEX IF NOT EXISTS idx_ir_movement
  ON intelligence_results (movement_detected)
  WHERE movement_detected = 1;

CREATE INDEX IF NOT EXISTS idx_ir_fetched
  ON intelligence_results (fetched_at DESC);

-- ── Job Queue State ──────────────────────────────────────────
-- Tracks what has been queued and processed each month.
-- Prevents re-queuing the same entity+type within a cycle.

CREATE TABLE IF NOT EXISTS job_queue_state (
  entity_id    TEXT NOT NULL,        -- person_id or company_unique_id
  job_type     TEXT NOT NULL,
  month_key    TEXT NOT NULL,        -- e.g., '2026-03'
  status       TEXT NOT NULL DEFAULT 'queued',  -- queued, completed, failed
  queued_at    TEXT,
  completed_at TEXT,

  PRIMARY KEY (entity_id, job_type, month_key)
);

CREATE INDEX IF NOT EXISTS idx_jqs_month_status
  ON job_queue_state (month_key, status);

-- ── Batch Progress ───────────────────────────────────────────
-- Records each production run for observability.

CREATE TABLE IF NOT EXISTS batch_progress (
  batch_id    TEXT PRIMARY KEY,
  month_key   TEXT NOT NULL,
  total_jobs  INTEGER NOT NULL,
  by_type     TEXT NOT NULL DEFAULT '{}',  -- JSON: {"linkedin_profile": 10, "glassdoor_sentiment": 5}
  produced_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bp_month
  ON batch_progress (month_key, produced_at DESC);

-- ── Monitor List ─────────────────────────────────────────────
-- Companies with explicit monitoring configuration.
-- Populated by upstream processes (people-worker, campaign-engine).

CREATE TABLE IF NOT EXISTS monitor_list (
  company_unique_id  TEXT PRIMARY KEY,
  company_name       TEXT NOT NULL,
  domain             TEXT,
  state              TEXT,
  agent_name         TEXT NOT NULL,
  monitor_types      TEXT NOT NULL DEFAULT 'glassdoor_sentiment,company_news',
  active             INTEGER NOT NULL DEFAULT 1,
  added_at           TEXT NOT NULL DEFAULT (datetime('now')),
  notes              TEXT
);

CREATE INDEX IF NOT EXISTS idx_ml_active
  ON monitor_list (active)
  WHERE active = 1;

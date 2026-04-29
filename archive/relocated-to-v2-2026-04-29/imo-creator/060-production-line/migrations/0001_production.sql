-- ═══════════════════════════════════════════════════════════════════════════════
-- PRODUCTION LINE ENGINE — D1 Schema (SQLite)
-- ═══════════════════════════════════════════════════════════════════════════════
-- Authority: imo-creator (CC-01)
-- Engine: Foundational Bedrock
-- Template: PROCESS_TEMPLATE v4.0.0
-- Pattern: execution_trace (§11) + logbook after certification (§12) + fleet_failures (§13)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ PRODUCTION GOALS — CANONICAL                                               │
-- │ Each goal is an aircraft. HEIR identity + ORBT state.                      │
-- │ certified_by is NULL until auditor certifies (different engine than builder)│
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS production_goals (
  goal_id           TEXT PRIMARY KEY,
  sovereign_ref     TEXT NOT NULL DEFAULT 'imo-creator',
  hub_id            TEXT NOT NULL DEFAULT 'production-line',
  cc_layer          TEXT NOT NULL DEFAULT 'CC-03',
  line              TEXT NOT NULL,
  phase             TEXT,
  workpiece_id      TEXT NOT NULL,
  workpiece_name    TEXT,
  ctb_placement     TEXT NOT NULL DEFAULT 'leaf',
  orbt_mode         TEXT NOT NULL DEFAULT 'BUILD' CHECK (orbt_mode IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  certified_by      TEXT,
  certified_at      TEXT,
  strike_count      INTEGER NOT NULL DEFAULT 0,
  source            TEXT NOT NULL DEFAULT 'manual' CHECK (source IN ('inbox','cron','manual','agent')),
  inbox_task_id     TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),
  started_at        TEXT,
  completed_at      TEXT,
  updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_goals_line ON production_goals(line);
CREATE INDEX IF NOT EXISTS idx_goals_orbt ON production_goals(orbt_mode);
CREATE INDEX IF NOT EXISTS idx_goals_workpiece ON production_goals(workpiece_id);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ PRODUCTION STEPS — One row per station per goal                            │
-- │ depends_on = JSON array of station_ids that must complete first            │
-- │ adapter_type determines how the station is called                          │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS production_steps (
  step_id           TEXT PRIMARY KEY,
  goal_id           TEXT NOT NULL REFERENCES production_goals(goal_id),
  station_id        TEXT NOT NULL,
  sequence          INTEGER NOT NULL,
  depends_on        TEXT NOT NULL DEFAULT '[]',
  adapter_type      TEXT NOT NULL CHECK (adapter_type IN ('http','cli','sql','manual')),
  adapter_target    TEXT NOT NULL,
  conditional       INTEGER NOT NULL DEFAULT 0,
  condition_desc    TEXT,
  status            TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','blocked','running','done','failed','skipped','not-callable')),
  result            TEXT,
  error_code        TEXT,
  error_message     TEXT,
  retryable         INTEGER DEFAULT 0,
  retry_count       INTEGER NOT NULL DEFAULT 0,
  duration_ms       INTEGER,
  cost_cents        INTEGER DEFAULT 0,
  tools_used        TEXT DEFAULT '[]',
  transport         TEXT,
  started_at        TEXT,
  completed_at      TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_steps_goal ON production_steps(goal_id);
CREATE INDEX IF NOT EXISTS idx_steps_status ON production_steps(status);
CREATE INDEX IF NOT EXISTS idx_steps_station ON production_steps(station_id);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ EXECUTION TRACE — §11 Append-only build journal (NOT the logbook)          │
-- │ Written during BUILD. Auditor reviews this to decide certification.        │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS execution_trace (
  trace_id          TEXT PRIMARY KEY,
  run_id            TEXT NOT NULL,
  goal_id           TEXT NOT NULL REFERENCES production_goals(goal_id),
  step_id           TEXT,
  station_id        TEXT,
  step_description  TEXT NOT NULL,
  target            TEXT,
  actual            TEXT,
  delta             TEXT,
  status            TEXT NOT NULL CHECK (status IN ('done','failed','skipped','not-callable')),
  error_code        TEXT,
  error_message     TEXT,
  tools_used        TEXT DEFAULT '[]',
  duration_ms       INTEGER,
  cost_cents        INTEGER DEFAULT 0,
  signed_by         TEXT NOT NULL,
  timestamp         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_trace_goal ON execution_trace(goal_id);
CREATE INDEX IF NOT EXISTS idx_trace_run ON execution_trace(run_id);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ FLEET FAILURES — §13 Fleet-level strike tracking                           │
-- │ Keyed by station + error_code pattern. Strike 3 = AD.                     │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS fleet_failures (
  pattern_id        TEXT PRIMARY KEY,
  station_id        TEXT NOT NULL,
  error_code        TEXT NOT NULL,
  error_pattern     TEXT NOT NULL,
  first_seen        TEXT NOT NULL DEFAULT (datetime('now')),
  occurrences       INTEGER NOT NULL DEFAULT 1,
  goals_affected    TEXT NOT NULL DEFAULT '[]',
  strike_count      INTEGER NOT NULL DEFAULT 1,
  status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','resolved','ad_issued')),
  ad_number         TEXT,
  resolved_by       TEXT,
  resolved_at       TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_fleet_station_code ON fleet_failures(station_id, error_code);
CREATE INDEX IF NOT EXISTS idx_fleet_status ON fleet_failures(status);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ PRODUCTION LOGBOOK — §12 ONLY after auditor certification                  │
-- │ First entry = birth certificate. Builder CANNOT write here.               │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS production_logbook (
  entry_id          TEXT PRIMARY KEY,
  goal_id           TEXT NOT NULL REFERENCES production_goals(goal_id),
  heir_ref          TEXT NOT NULL,
  orbt_entered      TEXT NOT NULL CHECK (orbt_entered IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  orbt_exited       TEXT NOT NULL CHECK (orbt_exited IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  context_loaded    TEXT,
  visit_path        TEXT NOT NULL CHECK (visit_path IN ('CERTIFICATION','MAINTENANCE','ERROR')),
  error_ref         TEXT,
  strike_count      INTEGER DEFAULT 0,
  action            TEXT NOT NULL,
  authority         TEXT NOT NULL,
  gates_passed      TEXT,
  checklist_type    TEXT NOT NULL CHECK (checklist_type IN ('build','operate','repair','troubleshoot_train')),
  signed_by         TEXT NOT NULL,
  signed_at         TEXT NOT NULL DEFAULT (datetime('now')),
  notes             TEXT
);

CREATE INDEX IF NOT EXISTS idx_logbook_goal ON production_logbook(goal_id);
CREATE INDEX IF NOT EXISTS idx_logbook_signed ON production_logbook(signed_at);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ PRODUCTION SIGMA — Analytics / Dyno Sheet                                  │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS production_sigma (
  sigma_id          TEXT PRIMARY KEY,
  station_id        TEXT NOT NULL,
  line              TEXT NOT NULL,
  metric            TEXT NOT NULL CHECK (metric IN ('duration_ms','cost_cents','success_rate','error_rate')),
  value             REAL NOT NULL,
  run_number        INTEGER NOT NULL,
  recorded_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sigma_station ON production_sigma(station_id);
CREATE INDEX IF NOT EXISTS idx_sigma_metric ON production_sigma(metric);

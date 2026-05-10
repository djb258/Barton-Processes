-- Dyno Run Tracking (BAR-345)
-- D1: mission-control

CREATE TABLE IF NOT EXISTS dyno_run (
  run_id TEXT PRIMARY KEY,
  domain TEXT NOT NULL,
  p1_definition TEXT NOT NULL,
  intent_mode TEXT NOT NULL,
  phases TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  verdict TEXT,
  r_x TEXT,
  ut_doc TEXT,
  diagnostic TEXT,
  cycle_count INTEGER DEFAULT 0,
  models_used TEXT,
  cost_usd REAL DEFAULT 0,
  r2_artifact_path TEXT,
  health_report TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  completed_at TEXT
);

CREATE TABLE IF NOT EXISTS dyno_run_cycle (
  cycle_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES dyno_run(run_id),
  phase TEXT NOT NULL,
  model TEXT NOT NULL,
  prompt_hash TEXT,
  response_hash TEXT,
  tokens_in INTEGER,
  tokens_out INTEGER,
  cost_usd REAL,
  duration_ms INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_dyno_run_domain ON dyno_run(domain);
CREATE INDEX IF NOT EXISTS idx_dyno_run_status ON dyno_run(status);
CREATE INDEX IF NOT EXISTS idx_dyno_run_cycle_run ON dyno_run_cycle(run_id);

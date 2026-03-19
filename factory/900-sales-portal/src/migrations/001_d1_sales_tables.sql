-- ═══════════════════════════════════════════════════════════════
-- Process 900 — D1 Sales Working Tables
-- ═══════════════════════════════════════════════════════════════
-- D1 = working layer. Neon = vault.
-- Spine + 4 sub-hubs (1 per meeting) + outreach snapshot for Meeting 1.
-- ═══════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────
-- SPINE — Sales State (phase router)
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sales_state (
  sales_id            TEXT PRIMARY KEY,
  sovereign_id        TEXT NOT NULL,
  legal_name          TEXT NOT NULL,
  domicile_state      TEXT,
  current_phase       TEXT NOT NULL DEFAULT 'factfinder',
  slug                TEXT UNIQUE,
  agent_name          TEXT,
  source              TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_sales_state_sovereign ON sales_state(sovereign_id);
CREATE INDEX IF NOT EXISTS idx_sales_state_slug ON sales_state(slug);
CREATE INDEX IF NOT EXISTS idx_sales_state_phase ON sales_state(current_phase);

-- ─────────────────────────────────────────────────────────────
-- OUTREACH SNAPSHOT — Seeded from outreach 5 sub-hubs for Meeting 1
-- Read-only after seed. Gives the Fact Finder form its pre-populated data.
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS outreach_snapshot (
  snapshot_id         TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,
  sovereign_id        TEXT NOT NULL,

  -- From company_target
  company_name        TEXT,
  postal_code         TEXT,
  city                TEXT,
  state               TEXT,
  industry            TEXT,
  employees           INTEGER,
  company_domain      TEXT,

  -- From DOL
  ein                 TEXT,
  filing_present      INTEGER DEFAULT 0,
  funding_type        TEXT,
  broker_or_advisor   TEXT,
  carrier             TEXT,
  renewal_month       INTEGER,

  -- From people/slots
  ceo_name            TEXT,
  ceo_title           TEXT,
  ceo_email           TEXT,
  ceo_linkedin        TEXT,
  cfr_name            TEXT,
  cfr_title           TEXT,
  cfr_email           TEXT,
  cfr_linkedin        TEXT,
  hr_name             TEXT,
  hr_title            TEXT,
  hr_email            TEXT,
  hr_linkedin         TEXT,

  -- From blog
  blog_url            TEXT,
  blog_context        TEXT,

  -- From BIT
  bit_score           REAL,
  bit_tier            TEXT,
  signal_count        INTEGER,

  seeded_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_outreach_snapshot_sales ON outreach_snapshot(sales_id);

-- ─────────────────────────────────────────────────────────────
-- MEETING 1: FACT FINDER — Form data (read-write)
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sales_factfinder (
  factfinder_id       TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,

  -- Company info (validated/corrected from outreach snapshot)
  legal_name          TEXT,
  domicile_state      TEXT,
  ein                 TEXT,
  employee_count      INTEGER,
  industry            TEXT,

  -- Current benefits situation
  current_carrier     TEXT,
  current_broker      TEXT,
  renewal_date        TEXT,
  funding_type        TEXT,
  annual_premium      REAL,
  stop_loss_carrier   TEXT,
  stop_loss_deductible REAL,

  -- Pain points / notes
  pain_points         TEXT,
  decision_timeline   TEXT,
  decision_makers     TEXT,
  notes               TEXT,

  -- Meeting metadata
  meeting_date        TEXT,
  meeting_status      TEXT NOT NULL DEFAULT 'scheduled',
  completed_at        TEXT,

  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_factfinder_sales ON sales_factfinder(sales_id);

CREATE TABLE IF NOT EXISTS sales_factfinder_errors (
  error_id            TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,
  source_entity       TEXT NOT NULL,
  source_id           TEXT,
  error_code          TEXT NOT NULL,
  error_message       TEXT NOT NULL,
  severity            TEXT NOT NULL DEFAULT 'error',
  status              TEXT NOT NULL DEFAULT 'open',
  context             TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────────────────────────
-- MEETING 2: INSURANCE EDUCATION — Slide deck + Monte Carlo
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sales_insurance (
  insurance_id        TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,

  -- Monte Carlo results (populated by future simulation engine)
  monte_carlo_run_id  TEXT,
  projected_claims    REAL,
  confidence_low      REAL,
  confidence_high     REAL,
  recommended_funding TEXT,
  simulation_date     TEXT,

  -- Presentation metadata
  slides_presented    TEXT,  -- JSON array of slide IDs shown
  meeting_date        TEXT,
  meeting_status      TEXT NOT NULL DEFAULT 'scheduled',
  completed_at        TEXT,
  notes               TEXT,

  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_insurance_sales ON sales_insurance(sales_id);

CREATE TABLE IF NOT EXISTS sales_insurance_errors (
  error_id            TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,
  source_entity       TEXT NOT NULL,
  source_id           TEXT,
  error_code          TEXT NOT NULL,
  error_message       TEXT NOT NULL,
  severity            TEXT NOT NULL DEFAULT 'error',
  status              TEXT NOT NULL DEFAULT 'open',
  context             TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────────────────────────
-- MEETING 3: SYSTEMS EDUCATION — Slide deck
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sales_systems (
  systems_id          TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,

  -- Presentation metadata
  slides_presented    TEXT,  -- JSON array of slide IDs shown
  meeting_date        TEXT,
  meeting_status      TEXT NOT NULL DEFAULT 'scheduled',
  completed_at        TEXT,
  notes               TEXT,

  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_systems_sales ON sales_systems(sales_id);

CREATE TABLE IF NOT EXISTS sales_systems_errors (
  error_id            TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,
  source_entity       TEXT NOT NULL,
  source_id           TEXT,
  error_code          TEXT NOT NULL,
  error_message       TEXT NOT NULL,
  severity            TEXT NOT NULL DEFAULT 'error',
  status              TEXT NOT NULL DEFAULT 'open',
  context             TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────────────────────────
-- MEETING 4: FINANCIALS — Quote presentation
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sales_quotes (
  quote_id            TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,
  benefit_type        TEXT NOT NULL,
  carrier             TEXT NOT NULL,
  rate_ee             REAL,
  rate_es             REAL,
  rate_ec             REAL,
  rate_fam            REAL,
  annual_cost         REAL,
  source              TEXT,
  received_date       TEXT,
  status              TEXT NOT NULL DEFAULT 'received',
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_quotes_sales ON sales_quotes(sales_id);
CREATE INDEX IF NOT EXISTS idx_quotes_benefit ON sales_quotes(benefit_type);

CREATE TABLE IF NOT EXISTS sales_quotes_errors (
  error_id            TEXT PRIMARY KEY,
  sales_id            TEXT NOT NULL,
  source_entity       TEXT NOT NULL,
  source_id           TEXT,
  error_code          TEXT NOT NULL,
  error_message       TEXT NOT NULL,
  severity            TEXT NOT NULL DEFAULT 'error',
  status              TEXT NOT NULL DEFAULT 'open',
  context             TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ═══════════════════════════════════════════════════════════════
-- Process 200 — D1 Edge Workspace
-- ═══════════════════════════════════════════════════════════════
-- D1 = active companies we're working on.
-- Neon = the vault (everything, including inactive).
-- If we're not working a company, it stays in Neon.
-- Monthly SEED pulls active territory into D1.
-- Monthly PUSH sends confirmed results back to Neon.
--
-- COLUMN NAMES MATCH PRODUCTION NEON (verified 2026-03-19)
-- ═══════════════════════════════════════════════════════════════

-- ┌─────────────────────────────────────────────────────────────┐
-- │ COMPANY DOSSIER — Territory companies + all sub-hub data    │
-- │ Seeded from Neon on Day 1. Read-only during the month.     │
-- │                                                             │
-- │ Seed query path (CONSTANT — do not change):                │
-- │   coverage.service_agent (3 agents)                         │
-- │   → coverage.service_agent_coverage (3 active territories) │
-- │   → coverage.v_service_agent_coverage_zips (zips in radius)│
-- │   → outreach.company_target (companies in those zips)      │
-- │   → JOIN each sub-hub on company_unique_id or outreach_id  │
-- │                                                             │
-- │ Key views in Neon:                                          │
-- │   people.v_territory_companies                              │
-- │   people.v_territory_slots                                  │
-- │   people.v_territory_people                                 │
-- │   people.v_linkedin_monitor_list                            │
-- │   people.v_territory_summary                                │
-- └─────────────────────────────────────────────────────────────┘

-- Companies: from outreach.company_target + cl.company_identity
-- JOIN: company_target.company_unique_id = company_identity.company_unique_id::text
CREATE TABLE IF NOT EXISTS companies (
  company_unique_id   TEXT PRIMARY KEY,
  outreach_id         TEXT NOT NULL,
  agent_name          TEXT NOT NULL,
  agent_number        TEXT,

  -- From company_target
  postal_code         TEXT,
  city                TEXT,
  state               TEXT,
  industry            TEXT,
  employees           INTEGER,
  outreach_status     TEXT,
  source              TEXT,

  -- From company_identity
  canonical_name      TEXT,
  company_domain      TEXT,
  identity_status     TEXT,
  normalized_domain   TEXT,
  sovereign_company_id TEXT,

  seeded_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_companies_agent ON companies(agent_name);
CREATE INDEX IF NOT EXISTS idx_companies_state ON companies(state);
CREATE INDEX IF NOT EXISTS idx_companies_outreach ON companies(outreach_id);

-- Slots: from people.company_slot
-- JOIN: company_slot.company_unique_id = companies.company_unique_id
CREATE TABLE IF NOT EXISTS slots (
  slot_id             TEXT PRIMARY KEY,
  outreach_id         TEXT,
  company_unique_id   TEXT NOT NULL,
  slot_type           TEXT NOT NULL,  -- CEO, CFO, HR
  person_unique_id    TEXT,
  is_filled           INTEGER NOT NULL DEFAULT 0,
  filled_at           TEXT,
  confidence_score    REAL,
  source_system       TEXT
);

CREATE INDEX IF NOT EXISTS idx_slots_company ON slots(company_unique_id);
CREATE INDEX IF NOT EXISTS idx_slots_filled ON slots(is_filled);
CREATE INDEX IF NOT EXISTS idx_slots_person ON slots(person_unique_id);

-- People: from people.people_master
-- JOIN: people_master.unique_id = company_slot.person_unique_id
-- NOTE: Join to company is THROUGH slots, not direct company_unique_id
CREATE TABLE IF NOT EXISTS people (
  unique_id             TEXT PRIMARY KEY,
  company_unique_id     TEXT,
  company_slot_unique_id TEXT,
  full_name             TEXT,
  first_name            TEXT,
  last_name             TEXT,
  title                 TEXT,
  seniority             TEXT,
  department            TEXT,
  email                 TEXT,
  email_verified        INTEGER DEFAULT 0,
  email_verification_source TEXT,
  linkedin_url          TEXT,
  twitter_url           TEXT,
  source_system         TEXT,
  outreach_ready        INTEGER DEFAULT 0,
  is_decision_maker     INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_people_company ON people(company_unique_id);
CREATE INDEX IF NOT EXISTS idx_people_linkedin ON people(linkedin_url) WHERE linkedin_url IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_people_slot ON people(company_slot_unique_id);

-- Outreach: from outreach.outreach
-- JOIN: outreach.outreach_id = companies.outreach_id
CREATE TABLE IF NOT EXISTS outreach_status (
  outreach_id         TEXT PRIMARY KEY,
  sovereign_id        TEXT,
  domain              TEXT,
  ein                 TEXT,
  has_appointment     INTEGER DEFAULT 0
);

-- DOL: from outreach.dol
-- JOIN: dol.outreach_id = companies.outreach_id
CREATE TABLE IF NOT EXISTS dol (
  dol_id              TEXT PRIMARY KEY,
  outreach_id         TEXT NOT NULL,
  ein                 TEXT,
  filing_present      INTEGER DEFAULT 0,
  funding_type        TEXT,
  broker_or_advisor   TEXT,
  carrier             TEXT,
  renewal_month       INTEGER,
  outreach_start_month INTEGER
);

CREATE INDEX IF NOT EXISTS idx_dol_outreach ON dol(outreach_id);
CREATE INDEX IF NOT EXISTS idx_dol_ein ON dol(ein);

-- Blog: from outreach.blog
-- JOIN: blog.outreach_id = companies.outreach_id
CREATE TABLE IF NOT EXISTS blog (
  blog_id             TEXT PRIMARY KEY,
  outreach_id         TEXT NOT NULL,
  source_url          TEXT,
  about_url           TEXT,
  news_url            TEXT,
  source_type         TEXT,
  extraction_method   TEXT,
  context_summary     TEXT,
  last_extracted_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_blog_outreach ON blog(outreach_id);

-- BIT Scores: from outreach.bit_scores
-- JOIN: bit_scores.outreach_id = companies.outreach_id
CREATE TABLE IF NOT EXISTS bit_scores (
  outreach_id         TEXT PRIMARY KEY,
  score               REAL,
  score_tier          TEXT,
  signal_count        INTEGER,
  people_score        REAL,
  dol_score           REAL,
  blog_score          REAL,
  talent_flow_score   REAL,
  last_signal_at      TEXT,
  last_scored_at      TEXT
);

-- ┌─────────────────────────────────────────────────────────────┐
-- │ MONITOR LIST — LinkedIn URLs to check this month            │
-- │ Derived from people + slots (has linkedin_url + in a slot) │
-- │                                                             │
-- │ Join path: slots (is_filled=1) → people (has linkedin_url) │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS monitor_list (
  person_id           TEXT PRIMARY KEY,
  company_unique_id   TEXT NOT NULL,
  full_name           TEXT,
  linkedin_url        TEXT NOT NULL,
  slot_type           TEXT NOT NULL,
  agent_name          TEXT NOT NULL,
  agent_number        TEXT,
  seeded_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_monitor_agent ON monitor_list(agent_name);

-- ┌─────────────────────────────────────────────────────────────┐
-- │ BASELINE — Previous month's title+company for movement diff │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS baseline (
  person_id           TEXT PRIMARY KEY,
  parsed_title        TEXT,
  parsed_company      TEXT,
  raw_title_tag       TEXT,
  run_month           TEXT NOT NULL
);

-- ┌─────────────────────────────────────────────────────────────┐
-- │ SNAPSHOTS — This month's LinkedIn fetch results             │
-- │ One row per person per month. Movement: 0 or 1.            │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS snapshots (
  snapshot_id         TEXT PRIMARY KEY,
  person_id           TEXT NOT NULL,
  company_unique_id   TEXT NOT NULL,
  run_month           TEXT NOT NULL,

  -- From <title> tag
  linkedin_url        TEXT NOT NULL,
  raw_title_tag       TEXT,
  parsed_name         TEXT,
  parsed_title        TEXT,
  parsed_company      TEXT,

  -- From JSON-LD
  headline            TEXT,
  location            TEXT,
  last_post_date      TEXT,
  profile_photo_url   TEXT,

  -- Movement detection
  movement_detected   INTEGER NOT NULL DEFAULT 0,
  movement_type       TEXT NOT NULL DEFAULT 'NONE',

  -- Fetch metadata
  fetched_at          TEXT NOT NULL DEFAULT (datetime('now')),
  source_tool         TEXT NOT NULL DEFAULT 'cf_fetch',
  origin_domain       TEXT,
  fetch_duration_ms   INTEGER,
  http_status         INTEGER,

  UNIQUE(person_id, run_month)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_month ON snapshots(run_month);
CREATE INDEX IF NOT EXISTS idx_snapshots_movement ON snapshots(movement_detected) WHERE movement_detected = 1;
CREATE INDEX IF NOT EXISTS idx_snapshots_person ON snapshots(person_id);

-- ┌─────────────────────────────────────────────────────────────┐
-- │ BATCH PROGRESS — Tracks monthly processing state            │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS batch_progress (
  run_month           TEXT PRIMARY KEY,
  total_profiles      INTEGER NOT NULL DEFAULT 0,
  checked             INTEGER NOT NULL DEFAULT 0,
  movements           INTEGER NOT NULL DEFAULT 0,
  errors              INTEGER NOT NULL DEFAULT 0,
  started_at          TEXT,
  last_batch_at       TEXT,
  completed_at        TEXT,
  pushed_to_vault     INTEGER NOT NULL DEFAULT 0
);

-- ┌─────────────────────────────────────────────────────────────┐
-- │ ERRORS — Local error log                                    │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS errors (
  error_id            TEXT PRIMARY KEY,
  person_id           TEXT,
  linkedin_url        TEXT,
  error_code          TEXT NOT NULL,
  error_message       TEXT NOT NULL,
  run_month           TEXT NOT NULL,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_errors_month ON errors(run_month);
CREATE INDEX IF NOT EXISTS idx_errors_code ON errors(error_code);

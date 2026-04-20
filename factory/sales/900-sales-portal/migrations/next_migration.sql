-- Sales Sub-Hub — Migration: Column gaps + missing tables
-- Database: svg-d1-sales (95835f64-db7f-43d4-b211-899b11a17c96)
-- Date: 2026-04-16
-- Author: Audit (claude-code), Review: Dave Barton
-- Status: PENDING DAVE REVIEW — do not execute until approved
--
-- This migration:
--   1. Adds sales_state_errors (missing CQRS error table for spine)
--   2. Adds sales_videos (gate video send/watch tracking)
--   3. Adds sales_monte_carlo (Gate 2 simulation output)
--   4. Adds columns to sales_factfinder (Gate 1 "bring the bill" data)
--   5. Adds columns to sales_insurance (Gate 2 strategy context)
--   6. Adds columns to sales_systems (Gate 3 vendor selections + implementation)
--   7. Adds columns to sales_quotes (Gate 4 full quote detail)
--   8. Adds columns to sales_state (pipeline reporting / gate timestamps)
--
-- SAFE: All new tables use CREATE TABLE IF NOT EXISTS.
--       All column additions use ALTER TABLE ... ADD COLUMN (SQLite supports this).
--       No existing columns are modified or dropped.
--       No existing data is touched.

-- ============================================================
-- 1. MISSING TABLE: sales_state_errors
--    CQRS: error table for the sales_state spine.
--    Captures failed phase transitions, sovereign_id resolution
--    failures, close attempt rejections.
-- ============================================================

CREATE TABLE IF NOT EXISTS sales_state_errors (
  error_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  sales_id      TEXT,
  error_code    TEXT NOT NULL,
  payload       TEXT,   -- JSON: what was attempted
  process_id    TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- 2. MISSING TABLE: sales_videos
--    Tracks which gate video was sent to which contact,
--    when it was sent, and watch status (if tracking available).
--    One row per video send event.
-- ============================================================

CREATE TABLE IF NOT EXISTS sales_videos (
  video_id        TEXT PRIMARY KEY,
  sovereign_ref   TEXT NOT NULL DEFAULT 'imo-creator',
  hub_id          TEXT NOT NULL DEFAULT 'DB-SALES',
  cc_layer        TEXT NOT NULL DEFAULT 'CC-03',
  ctb_placement   TEXT NOT NULL DEFAULT 'leaf',

  sales_id        TEXT NOT NULL REFERENCES sales_state(sales_id),
  contact_id      TEXT REFERENCES sales_contacts(contact_id),

  -- Which gate video
  gate_number     INTEGER NOT NULL CHECK (gate_number IN (0, 1, 2, 3, 4)),
    -- 0 = C-00 intro/filter, 1 = Gate 1 factfinder, 2 = Gate 2 Monte Carlo,
    -- 3 = Gate 3 service demo, 4 = Gate 4 quote/dare
  video_type      TEXT NOT NULL CHECK (video_type IN ('gate', 'explainer', 'vendor', 'training')),
  video_id_ref    TEXT,   -- reference ID in the video pipeline (e.g. C-01, C-02)
  video_url       TEXT,   -- URL where the video lives (R2, InVideo, etc.)

  -- Send tracking
  sent_at         TEXT,   -- when it was sent to the contact
  sent_via        TEXT,   -- 'email', 'linkedin', 'sms', 'in_meeting'
  send_message_id TEXT,   -- email message_id or outreach thread reference

  -- Watch tracking (if available from delivery platform)
  watched         INTEGER NOT NULL DEFAULT 0,  -- 0 = not watched, 1 = watched
  watched_at      TEXT,
  watch_duration_seconds INTEGER,  -- how long they watched (if available)
  watch_pct       REAL,            -- % of video watched (if available)

  -- Outcome
  response_received INTEGER NOT NULL DEFAULT 0,  -- did they respond after watching?
  response_type     TEXT,  -- 'meeting_booked', 'replied', 'no_response', 'declined'
  meeting_booked_at TEXT,  -- if they booked a meeting

  orbt_mode       TEXT NOT NULL DEFAULT 'BUILD' CHECK (orbt_mode IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  strike_count    INTEGER NOT NULL DEFAULT 0,

  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- 3. MISSING TABLE: sales_monte_carlo
--    Gate 2 primary deliverable.
--    The two-path simulation showing current fully-insured
--    trajectory vs proposed self-insured trajectory.
--    Separate table because it is complex structured output
--    that must be versioned and audited.
-- ============================================================

CREATE TABLE IF NOT EXISTS sales_monte_carlo (
  mc_id           TEXT PRIMARY KEY,
  sovereign_ref   TEXT NOT NULL DEFAULT 'imo-creator',
  hub_id          TEXT NOT NULL DEFAULT 'DB-SALES',
  cc_layer        TEXT NOT NULL DEFAULT 'CC-03',
  ctb_placement   TEXT NOT NULL DEFAULT 'leaf',

  sales_id        TEXT NOT NULL REFERENCES sales_state(sales_id),
  version         INTEGER NOT NULL DEFAULT 1,  -- simulation version (may be re-run)
  is_current      INTEGER NOT NULL DEFAULT 1,  -- only one current per sales_id

  -- Inputs (what was fed into the simulation)
  employee_count          INTEGER,
  current_annual_premium  REAL,
  trend_rate_pct          REAL,    -- assumed medical trend (e.g. 8.5%)
  claims_profile          TEXT,    -- 'average', 'favorable', 'unfavorable' or Dave's assessment
  stop_loss_attachment_specific  REAL,   -- per-person stop loss attachment point ($)
  stop_loss_attachment_aggregate REAL,   -- aggregate attachment point ($)
  projection_years        INTEGER DEFAULT 5,

  -- Outputs — Path A (stay fully insured, compound off higher base)
  path_a_year1    REAL,
  path_a_year2    REAL,
  path_a_year3    REAL,
  path_a_year4    REAL,
  path_a_year5    REAL,
  path_a_5yr_total REAL,

  -- Outputs — Path B (self insured, compound off lower base)
  path_b_year1    REAL,
  path_b_year2    REAL,
  path_b_year3    REAL,
  path_b_year4    REAL,
  path_b_year5    REAL,
  path_b_5yr_total REAL,

  -- Summary
  projected_savings_year1 REAL,   -- Path A - Path B, Year 1
  projected_savings_5yr   REAL,   -- Path A - Path B, cumulative 5 years
  break_even_month        INTEGER, -- when Path B becomes cheaper than Path A on a monthly basis

  -- Full simulation output (JSON blob for anything not in structured columns)
  simulation_json TEXT,

  -- System
  run_by          TEXT,   -- 'dave_manual', 'monte_carlo_worker', 'pending'
  run_at          TEXT,

  orbt_mode       TEXT NOT NULL DEFAULT 'BUILD' CHECK (orbt_mode IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  strike_count    INTEGER NOT NULL DEFAULT 0,

  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sales_monte_carlo_errors (
  error_id    INTEGER PRIMARY KEY AUTOINCREMENT,
  sales_id    TEXT,
  mc_id       TEXT,
  error_code  TEXT NOT NULL,
  payload     TEXT,
  process_id  TEXT,
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- 4. COLUMN GAPS: sales_factfinder
--    Gate 1 = "Bring the bill, I'll bring the math."
--    The bill data is the entire point of Gate 1.
--    None of it is in the current table.
-- ============================================================

-- Current carrier (who they're insured with now)
ALTER TABLE sales_factfinder ADD COLUMN current_carrier TEXT;

-- Current funding type (fully insured / level funded / self insured)
ALTER TABLE sales_factfinder ADD COLUMN current_plan_type TEXT
  CHECK (current_plan_type IN ('fully_insured', 'level_funded', 'self_insured', 'unknown') OR current_plan_type IS NULL);

-- The bill — monthly and annual
ALTER TABLE sales_factfinder ADD COLUMN current_monthly_premium REAL;
ALTER TABLE sales_factfinder ADD COLUMN current_annual_premium  REAL;

-- Tier enrollment counts (how many employees in each coverage tier)
ALTER TABLE sales_factfinder ADD COLUMN tier_count_ee            INTEGER;  -- employee only
ALTER TABLE sales_factfinder ADD COLUMN tier_count_ee_spouse     INTEGER;  -- employee + spouse
ALTER TABLE sales_factfinder ADD COLUMN tier_count_ee_child      INTEGER;  -- employee + child(ren)
ALTER TABLE sales_factfinder ADD COLUMN tier_count_family        INTEGER;  -- family

-- Tier monthly costs (employer + employee combined PEPM)
ALTER TABLE sales_factfinder ADD COLUMN tier_cost_ee             REAL;
ALTER TABLE sales_factfinder ADD COLUMN tier_cost_ee_spouse      REAL;
ALTER TABLE sales_factfinder ADD COLUMN tier_cost_ee_child       REAL;
ALTER TABLE sales_factfinder ADD COLUMN tier_cost_family         REAL;

-- Employer contribution percentage
ALTER TABLE sales_factfinder ADD COLUMN employer_contribution_pct REAL;

-- Exact renewal date (not just month)
ALTER TABLE sales_factfinder ADD COLUMN renewal_date TEXT;  -- ISO date

-- Company context for underwriting
ALTER TABLE sales_factfinder ADD COLUMN sic_code TEXT;
ALTER TABLE sales_factfinder ADD COLUMN state    TEXT;

-- The actual bill document
ALTER TABLE sales_factfinder ADD COLUMN bill_document_url TEXT;  -- R2 or Drive URL

-- Dave's notes from the meeting
ALTER TABLE sales_factfinder ADD COLUMN notes TEXT;

-- ============================================================
-- 5. COLUMN GAPS: sales_insurance
--    Gate 2 = strategy + landscape context.
--    The Monte Carlo lives in sales_monte_carlo.
--    This table captures the qualitative strategy decision.
-- ============================================================

-- Landscape flags (inform waterfall eligibility)
ALTER TABLE sales_insurance ADD COLUMN hospital_waterfall_applicable INTEGER DEFAULT 0;
  -- 1 = nonprofit hospital accessible (501R is in play)
ALTER TABLE sales_insurance ADD COLUMN drug_waterfall_applicable     INTEGER DEFAULT 0;
  -- 1 = high-dollar specialty drug exposure detected or expected

-- Vendor candidates identified at Gate 2 (before Gate 3 final selections)
ALTER TABLE sales_insurance ADD COLUMN tpa_candidates  TEXT;  -- JSON array
ALTER TABLE sales_insurance ADD COLUMN pbm_candidates  TEXT;  -- JSON array

-- Stop loss tier
ALTER TABLE sales_insurance ADD COLUMN stop_loss_tier TEXT;
  -- e.g. 'standard_50k', 'laser_100k', 'aggregate_only'

-- When Gate 2 happened
ALTER TABLE sales_insurance ADD COLUMN gate2_meeting_date TEXT;

-- Dave's reasoning for the strategy chosen
ALTER TABLE sales_insurance ADD COLUMN strategy_rationale TEXT;

ALTER TABLE sales_insurance ADD COLUMN notes TEXT;

-- ============================================================
-- 6. COLUMN GAPS: sales_systems
--    Gate 3 = vendor ecosystem + implementation plan.
--    Current table captures payroll/admin/compliance but
--    misses the actual vendor selections and timelines.
-- ============================================================

-- Vendor selections (proposed — these become final at close)
ALTER TABLE sales_systems ADD COLUMN tpa_selected               TEXT;
ALTER TABLE sales_systems ADD COLUMN pbm_selected               TEXT;
ALTER TABLE sales_systems ADD COLUMN ppo_network_selected       TEXT
  CHECK (ppo_network_selected IN ('first_health', 'healthsmart', 'other', NULL) OR ppo_network_selected IS NULL);
  -- Per CTB: only First Health or HealthSmart; PHCS and MultiPlan explicitly retired
ALTER TABLE sales_systems ADD COLUMN um_precert_vendor          TEXT;
ALTER TABLE sales_systems ADD COLUMN specialty_drug_flag_vendor TEXT;
ALTER TABLE sales_systems ADD COLUMN stop_loss_carrier          TEXT;

-- Client's existing HR and benefit admin platforms (affects enrollment integration)
ALTER TABLE sales_systems ADD COLUMN hr_platform           TEXT;
ALTER TABLE sales_systems ADD COLUMN benefit_admin_platform TEXT;

-- Implementation timeline
ALTER TABLE sales_systems ADD COLUMN year1_implementation_start TEXT;  -- target ISO date
ALTER TABLE sales_systems ADD COLUMN year2_implementation_start TEXT;  -- target ISO date
ALTER TABLE sales_systems ADD COLUMN enrollment_method          TEXT;
  -- 'census_copy' = Year 1 (take existing, copy over, no disruption)
  -- 'full_open_enrollment' = Year 2

-- Which dashboards were shown in the Gate 3 demo
ALTER TABLE sales_systems ADD COLUMN dashboards_shown TEXT;
  -- JSON array: ["hr", "cfo", "underwriting", "renewal", "service_advisor"]

ALTER TABLE sales_systems ADD COLUMN gate3_meeting_date TEXT;

ALTER TABLE sales_systems ADD COLUMN notes TEXT;

-- ============================================================
-- 7. COLUMN GAPS: sales_quotes
--    Gate 4 = specific numbers + the dare.
--    Current table: quote_version, total_cost, approved_flag.
--    Missing everything Dave would actually bring to the meeting.
-- ============================================================

-- Structured quote details
ALTER TABLE sales_quotes ADD COLUMN stop_loss_quote_json     TEXT;
  -- JSON: carrier, specific_attachment, aggregate_attachment, monthly_premium, annual_premium
ALTER TABLE sales_quotes ADD COLUMN ancillary_quote_json     TEXT;
  -- JSON: dental, vision, life, std, ltd, eap — each with vendor + monthly_pepm
ALTER TABLE sales_quotes ADD COLUMN fixed_side_pepm_total    REAL;
  -- Total of all fixed-side vendor PEPMs rolled up
ALTER TABLE sales_quotes ADD COLUMN variable_side_monthly_estimate REAL;
  -- Estimated monthly claims cost (from Monte Carlo most likely path)

-- Savings presentation
ALTER TABLE sales_quotes ADD COLUMN projected_annual_savings  REAL;
  -- vs their current_annual_premium in sales_factfinder
ALTER TABLE sales_quotes ADD COLUMN projected_year1_cost      REAL;
ALTER TABLE sales_quotes ADD COLUMN commission_equivalent_saved REAL;
  -- The commission that's baked into their current premium — the transparency argument

-- Gate 4 meeting details
ALTER TABLE sales_quotes ADD COLUMN quote_presented_at TEXT;
ALTER TABLE sales_quotes ADD COLUMN decision_deadline   TEXT;  -- their renewal pressure date
ALTER TABLE sales_quotes ADD COLUMN gate4_meeting_date  TEXT;

-- Competitive positioning
ALTER TABLE sales_quotes ADD COLUMN competitive_notes TEXT;
  -- "Take it to every broker" — notes on what the competitive responses were

-- Close outcome
ALTER TABLE sales_quotes ADD COLUMN loss_reason TEXT;
  -- If closed_lost: why (price, competition, timing, no decision-maker, other)

ALTER TABLE sales_quotes ADD COLUMN notes TEXT;

-- ============================================================
-- 8. COLUMN GAPS: sales_state
--    Spine additions for pipeline reporting.
--    Gate completion timestamps let you calculate
--    days-per-gate without joining interactions.
-- ============================================================

-- Context at deal-open (denormalized from factfinder/outreach for fast pipeline views)
ALTER TABLE sales_state ADD COLUMN current_carrier    TEXT;
  -- Carrier they're leaving — denormalized from factfinder when Gate 1 completes
ALTER TABLE sales_state ADD COLUMN dol_employee_count INTEGER;
  -- Employee count from DOL data at deal-open (may differ from factfinder actual count)

-- Gate completion timestamps (sigma tracking — how long each gate takes)
ALTER TABLE sales_state ADD COLUMN gate1_completed_at TEXT;
ALTER TABLE sales_state ADD COLUMN gate2_completed_at TEXT;
ALTER TABLE sales_state ADD COLUMN gate3_completed_at TEXT;
ALTER TABLE sales_state ADD COLUMN gate4_completed_at TEXT;
ALTER TABLE sales_state ADD COLUMN closed_at          TEXT;

-- ═══════════════════════════════════════════════════════════════
-- Process 200 — LinkedIn Snapshots Table
-- ═══════════════════════════════════════════════════════════════
-- Stores monthly snapshots of LinkedIn profile data for movement detection.
-- Phase 1: title + company comparison. 0 or 1 per person per month.
-- CQRS: This is the CANONICAL table. Errors go to D1 master error table.
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS people.linkedin_snapshots (
  snapshot_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  person_id         TEXT NOT NULL,
  company_unique_id TEXT NOT NULL,
  run_month         DATE NOT NULL,  -- YYYY-MM-01 format

  -- Phase 1: from <title> tag
  linkedin_url      TEXT NOT NULL,
  raw_title_tag     TEXT,
  parsed_name       TEXT,
  parsed_title      TEXT,
  parsed_company    TEXT,

  -- Phase 1 bonus: from JSON-LD
  headline          TEXT,
  location          TEXT,
  last_post_date    TIMESTAMPTZ,
  profile_photo_url TEXT,

  -- Movement detection output
  movement_detected BOOLEAN NOT NULL DEFAULT false,
  movement_type     TEXT NOT NULL DEFAULT 'NONE',  -- NONE, TITLE_CHANGED, COMPANY_CHANGED, BOTH_CHANGED

  -- Metadata
  fetched_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  source_tool       TEXT NOT NULL DEFAULT 'cf_fetch',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- One snapshot per person per month
  CONSTRAINT uq_linkedin_snapshot_person_month UNIQUE (person_id, run_month)
);

-- Query patterns
CREATE INDEX IF NOT EXISTS idx_linkedin_snapshots_person ON people.linkedin_snapshots(person_id);
CREATE INDEX IF NOT EXISTS idx_linkedin_snapshots_month ON people.linkedin_snapshots(run_month);
CREATE INDEX IF NOT EXISTS idx_linkedin_snapshots_movement ON people.linkedin_snapshots(movement_detected) WHERE movement_detected = true;
CREATE INDEX IF NOT EXISTS idx_linkedin_snapshots_company ON people.linkedin_snapshots(company_unique_id);

-- Movement detection view: current month vs previous month
CREATE OR REPLACE VIEW people.v_linkedin_movement AS
SELECT
  curr.person_id,
  curr.company_unique_id,
  curr.parsed_name,
  curr.parsed_title as current_title,
  prev.parsed_title as previous_title,
  curr.parsed_company as current_company,
  prev.parsed_company as previous_company,
  curr.movement_detected,
  curr.movement_type,
  curr.last_post_date,
  curr.run_month as current_month,
  prev.run_month as previous_month
FROM people.linkedin_snapshots curr
LEFT JOIN people.linkedin_snapshots prev
  ON prev.person_id = curr.person_id
  AND prev.run_month = (
    SELECT MAX(run_month)
    FROM people.linkedin_snapshots
    WHERE person_id = curr.person_id
    AND run_month < curr.run_month
  )
WHERE curr.run_month = (
  SELECT MAX(run_month) FROM people.linkedin_snapshots
);

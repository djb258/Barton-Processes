-- ═══════════════════════════════════════════════════════════════
-- Process 200 — Neon Vault Table (Canonical)
-- ═══════════════════════════════════════════════════════════════
-- Receives confirmed monthly results from D1 at end of month.
-- INSERT-only. This is what downstream processes read.
-- CQRS: D1 = command (working), Neon = query (canonical).
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS people.linkedin_snapshots (
  snapshot_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  person_id         TEXT NOT NULL,
  company_unique_id TEXT NOT NULL,
  run_month         DATE NOT NULL,

  -- From <title> tag
  linkedin_url      TEXT NOT NULL,
  raw_title_tag     TEXT,
  parsed_name       TEXT,
  parsed_title      TEXT,
  parsed_company    TEXT,

  -- From JSON-LD
  headline          TEXT,
  location          TEXT,
  last_post_date    TIMESTAMPTZ,
  profile_photo_url TEXT,

  -- Movement detection
  movement_detected BOOLEAN NOT NULL DEFAULT false,
  movement_type     TEXT NOT NULL DEFAULT 'NONE',

  -- Metadata
  fetched_at        TIMESTAMPTZ NOT NULL,
  source_tool       TEXT NOT NULL DEFAULT 'cf_fetch',
  pushed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- One snapshot per person per month
  CONSTRAINT uq_linkedin_snapshot_person_month UNIQUE (person_id, run_month)
);

CREATE INDEX IF NOT EXISTS idx_linkedin_snapshots_person ON people.linkedin_snapshots(person_id);
CREATE INDEX IF NOT EXISTS idx_linkedin_snapshots_month ON people.linkedin_snapshots(run_month);
CREATE INDEX IF NOT EXISTS idx_linkedin_snapshots_movement ON people.linkedin_snapshots(movement_detected) WHERE movement_detected = true;
CREATE INDEX IF NOT EXISTS idx_linkedin_snapshots_company ON people.linkedin_snapshots(company_unique_id);

-- Movement view: what downstream processes consume
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

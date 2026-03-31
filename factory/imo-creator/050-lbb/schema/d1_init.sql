-- ═══════════════════════════════════════════════════════════════════════════════
-- LBB (Library Barton Brain) — D1 Schema (SQLite)
-- ═══════════════════════════════════════════════════════════════════════════════
-- Authority: imo-creator (CC-01 Sovereign)
-- Engine: Foundational Bedrock (law/doctrine/FOUNDATIONAL_BEDROCK.md)
-- Template: fleet/brain-template/ v1.0.0
-- Pattern: CQRS — 1 CANONICAL + 1 ERROR per sub-hub
-- Identity: HEIR (8 fields per record) + ORBT (4 states)
-- Hierarchy: CTB — subject (trunk) → subtopic (branch) → record (leaf)
-- Vault: Neon (lbb) via Hyperdrive. D1 is working surface.
-- ═══════════════════════════════════════════════════════════════════════════════

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ SUBJECTS — The CTB hierarchy (Dewey Decimal)                               │
-- │ Self-referencing tree. Trunk → Branch → Leaf.                              │
-- │ Records hang from these as leaves.                                         │
-- │                                                                             │
-- │ subject_id   TEXT PK    — UUID. Permanent identity for this subject node.   │
-- │ parent_id    TEXT FK    — Parent subject. NULL = root/trunk subject.         │
-- │ name         TEXT       — Slug-style name (e.g. insurance-informatics).     │
-- │ description  TEXT       — What this subject covers. AI classification key.  │
-- │ ctb_level    TEXT       — Position: trunk, branch, or leaf.                 │
-- │ sort_order   INTEGER    — Display ordering among siblings.                  │
-- │ created_at   TEXT       — ISO-8601 timestamp.                               │
-- │ updated_at   TEXT       — ISO-8601 timestamp.                               │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS lbb_subjects (
  subject_id      TEXT PRIMARY KEY,
  parent_id       TEXT REFERENCES lbb_subjects(subject_id),
  name            TEXT NOT NULL,
  description     TEXT,
  ctb_level       TEXT NOT NULL CHECK (ctb_level IN ('trunk','branch','leaf')),
  sort_order      INTEGER NOT NULL DEFAULT 0,
  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_lbb_subjects_parent ON lbb_subjects(parent_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_lbb_subjects_name_parent ON lbb_subjects(name, parent_id);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ RECORDS — CANONICAL                                                        │
-- │ Every record is a leaf on the CTB. HEIR identity + ORBT state.             │
-- │ One record = one finding/fact/article from one source.                     │
-- │                                                                             │
-- │ record_id      TEXT PK    — UUID. Permanent HEIR identity. Never changes.   │
-- │ sovereign_ref  TEXT       — HEIR. Which hangar owns this. imo-creator.      │
-- │ hub_id         TEXT       — HEIR. Aircraft identifier. lbb.                 │
-- │ cc_layer       TEXT       — HEIR. Authority level. CC-03 (context).         │
-- │ subject_id     TEXT FK    — Where this record sits on the CTB hierarchy.    │
-- │ ctb_placement  TEXT       — HEIR. Always leaf for individual records.       │
-- │ title          TEXT       — Human-readable title of this finding.           │
-- │ content        TEXT       — Full content. The actual data.                  │
-- │ summary        TEXT       — AI-generated or human summary.                  │
-- │ content_hash   TEXT UQ    — SHA-256 of content. Dedup key.                  │
-- │ content_format TEXT       — Format: text, markdown, html, transcript.       │
-- │ source_url     TEXT       — Origin URL or file path.                        │
-- │ source_type    TEXT       — Source class: web, pdf, video, podcast, etc.    │
-- │ source_name    TEXT       — Human-readable source name.                     │
-- │ fetched_by     TEXT       — Which UT sub-hub or method fetched this.        │
-- │ orbt_mode      TEXT       — Lifecycle: BUILD, OPERATE, REPAIR, T/T.        │
-- │ strike_count   INTEGER    — Error recurrence. 3 = TROUBLESHOOT_TRAIN.      │
-- │ tags           TEXT       — JSON array of freeform tags.                    │
-- │ found_at       TEXT       — When content was discovered/fetched.            │
-- │ reviewed_at    TEXT       — When human promoted to OPERATE. NULL = pending. │
-- │ created_at     TEXT       — ISO-8601 timestamp.                             │
-- │ updated_at     TEXT       — ISO-8601 timestamp.                             │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS lbb_records (
  -- IDENTITY (HEIR)
  record_id         TEXT PRIMARY KEY,
  sovereign_ref     TEXT NOT NULL DEFAULT 'imo-creator',
  hub_id            TEXT NOT NULL DEFAULT 'lbb',
  cc_layer          TEXT NOT NULL DEFAULT 'CC-03',

  -- CTB CLASSIFICATION
  subject_id        TEXT NOT NULL REFERENCES lbb_subjects(subject_id),
  ctb_placement     TEXT NOT NULL DEFAULT 'leaf',

  -- CONTENT
  title             TEXT NOT NULL,
  content           TEXT NOT NULL,
  summary           TEXT,
  content_hash      TEXT NOT NULL,
  content_format    TEXT NOT NULL DEFAULT 'text' CHECK (content_format IN ('text','markdown','html','transcript')),

  -- SOURCE
  source_url        TEXT,
  source_type       TEXT NOT NULL DEFAULT 'web' CHECK (source_type IN ('web','pdf','video','podcast','document','manual','search')),
  source_name       TEXT,
  fetched_by        TEXT,

  -- ORBT STATE
  orbt_mode         TEXT NOT NULL DEFAULT 'BUILD' CHECK (orbt_mode IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  strike_count      INTEGER NOT NULL DEFAULT 0,

  -- TAGS (JSON array)
  tags              TEXT NOT NULL DEFAULT '[]',

  -- TIMESTAMPS
  found_at          TEXT NOT NULL DEFAULT (datetime('now')),
  reviewed_at       TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_lbb_records_subject ON lbb_records(subject_id);
CREATE INDEX IF NOT EXISTS idx_lbb_records_orbt ON lbb_records(orbt_mode);
CREATE INDEX IF NOT EXISTS idx_lbb_records_source_type ON lbb_records(source_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_lbb_records_content_hash ON lbb_records(content_hash);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ RECORDS ERROR — CQRS Error Table                                           │
-- │ Failed ingestions, parse errors, validation failures. Append-only.         │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS lbb_records_error (
  error_id          TEXT PRIMARY KEY,
  record_id         TEXT,
  error_code        TEXT NOT NULL,
  error_message     TEXT NOT NULL,
  source_url        TEXT,
  payload_snapshot  TEXT,
  sub_hub           TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_lbb_error_code ON lbb_records_error(error_code);
CREATE INDEX IF NOT EXISTS idx_lbb_error_record ON lbb_records_error(record_id);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ LOGBOOK — Append-Only Change History                                       │
-- │ Aviation model: read first, write last. Immutable entries.                │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS lbb_logbook (
  entry_id          TEXT PRIMARY KEY,
  record_id         TEXT NOT NULL REFERENCES lbb_records(record_id),
  orbt_entered      TEXT NOT NULL CHECK (orbt_entered IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  orbt_exited       TEXT NOT NULL CHECK (orbt_exited IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  action            TEXT NOT NULL,
  signed_by         TEXT NOT NULL,
  signed_at         TEXT NOT NULL DEFAULT (datetime('now')),
  notes             TEXT
);

CREATE INDEX IF NOT EXISTS idx_lbb_logbook_record ON lbb_logbook(record_id);
CREATE INDEX IF NOT EXISTS idx_lbb_logbook_signed_at ON lbb_logbook(signed_at);

-- ═══════════════════════════════════════════════════════════════════════════════
-- SEED: 5 TRUNK SUBJECTS
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT OR IGNORE INTO lbb_subjects (subject_id, parent_id, name, description, ctb_level, sort_order)
VALUES
  ('trunk-system', NULL, 'system', 'System knowledge — doctrine, architecture, infrastructure, decisions. What imo-brain holds today.', 'trunk', 1),
  ('trunk-outreach', NULL, 'outreach', 'Outreach intelligence — company data patterns, enrichment learnings, tool performance, process analytics.', 'trunk', 2),
  ('trunk-sales', NULL, 'sales', 'Sales IP — Barton voice, DISC framework, meeting sequences, objection handling, Monte Carlo. The 25-year moat.', 'trunk', 3),
  ('trunk-client', NULL, 'client', 'Client service knowledge — intake patterns, vendor mappings, portal usage, benefits administration.', 'trunk', 4),
  ('trunk-research', NULL, 'research', 'Competitive intelligence — marketplace findings, vendor evaluations, tool benchmarks, industry trends.', 'trunk', 5);

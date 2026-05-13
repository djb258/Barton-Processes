-- Migration: 0001_client_tickets
-- Created: 2026-05-13
-- Purpose: Add client_tickets + client_tickets_error tables; add slug + branding columns to clients
-- Worker: bp.830 client-portal-830
-- DB: svg-d1-client (5443887b-ba8a-4da5-9f54-6a9c2cfb1244)

-- ── 1. Add slug + branding columns to clients ────────────────────────────────
ALTER TABLE clients ADD COLUMN slug TEXT;
ALTER TABLE clients ADD COLUMN label_override TEXT;
ALTER TABLE clients ADD COLUMN logo_url TEXT;
ALTER TABLE clients ADD COLUMN color_primary TEXT DEFAULT '#1a365d';
ALTER TABLE clients ADD COLUMN color_accent TEXT DEFAULT '#3182ce';

CREATE UNIQUE INDEX IF NOT EXISTS idx_clients_slug
  ON clients(slug) WHERE slug IS NOT NULL;

-- ── 2. client_tickets (canonical) ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS client_tickets (
  ticket_id         TEXT PRIMARY KEY,
  sovereign_ref     TEXT NOT NULL DEFAULT 'imo-creator',
  hub_id            TEXT NOT NULL DEFAULT 'DB-CLIENT',
  cc_layer          TEXT NOT NULL DEFAULT 'CC-03',
  ctb_placement     TEXT NOT NULL DEFAULT 'leaf',

  -- DOMAIN
  client_id         TEXT NOT NULL REFERENCES clients(client_id),
  full_name         TEXT NOT NULL,
  email             TEXT NOT NULL,
  category          TEXT NOT NULL CHECK (category IN ('benefits','payroll','onboarding','offboarding','compliance','general')),
  subject           TEXT NOT NULL,
  description       TEXT NOT NULL,
  priority          TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('low','normal','high','urgent')),
  status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','in_progress','waiting','resolved','closed')),

  -- ORBT STATE
  orbt_mode         TEXT NOT NULL DEFAULT 'OPERATE' CHECK (orbt_mode IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
  strike_count      INTEGER NOT NULL DEFAULT 0,

  -- TIMESTAMPS
  resolved_at       TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ── 3. client_tickets_error (CQRS error table) ──────────────────────────────
CREATE TABLE IF NOT EXISTS client_tickets_error (
  ticket_error_id   TEXT PRIMARY KEY,
  client_id         TEXT NOT NULL,
  source_entity     TEXT NOT NULL DEFAULT 'client_tickets',
  source_id         TEXT,
  error_code        TEXT NOT NULL,
  error_message     TEXT NOT NULL,
  severity          TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning','error','critical')),
  status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','resolved','suppressed')),
  context           TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

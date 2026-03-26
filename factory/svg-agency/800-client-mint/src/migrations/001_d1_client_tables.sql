-- ═══════════════════════════════════════════════════════════════
-- Process 800 — D1 Working Tables (Client Identity)
-- ═══════════════════════════════════════════════════════════════
-- D1 = working layer. Neon = vault.
-- S1 Hub: client (SPINE) + client_error
-- sovereign_id links back to CL company lifecycle.
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS client (
  client_id           TEXT PRIMARY KEY,
  sovereign_id        TEXT NOT NULL,
  legal_name          TEXT NOT NULL,
  fein                TEXT,
  domicile_state      TEXT,
  effective_date      TEXT,
  status              TEXT NOT NULL DEFAULT 'active',
  source              TEXT,
  version             INTEGER NOT NULL DEFAULT 1,
  domain              TEXT,
  label_override      TEXT,
  logo_url            TEXT,
  color_primary       TEXT,
  color_accent        TEXT,
  feature_flags       TEXT NOT NULL DEFAULT '{}',
  dashboard_blocks    TEXT NOT NULL DEFAULT '[]',
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_client_sovereign ON client(sovereign_id);
CREATE INDEX IF NOT EXISTS idx_client_status ON client(status);
CREATE INDEX IF NOT EXISTS idx_client_vaulted ON client(vaulted_at);

CREATE TABLE IF NOT EXISTS client_error (
  client_error_id     TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  source_entity       TEXT NOT NULL,
  source_id           TEXT,
  error_code          TEXT NOT NULL,
  error_message       TEXT NOT NULL,
  severity            TEXT NOT NULL DEFAULT 'error',
  status              TEXT NOT NULL DEFAULT 'open',
  context             TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_client_error_client ON client_error(client_id);
CREATE INDEX IF NOT EXISTS idx_client_error_status ON client_error(status);

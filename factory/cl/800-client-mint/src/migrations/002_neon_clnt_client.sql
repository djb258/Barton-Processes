-- ═══════════════════════════════════════════════════════════════
-- Process 800 — Neon Vault Tables (clnt schema — S1 Hub)
-- ═══════════════════════════════════════════════════════════════
-- Run once during initial setup.
-- Matches client blueprint column registry exactly.
-- ═══════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS clnt;

-- S1 Hub: CANONICAL — Sovereign client identity
CREATE TABLE IF NOT EXISTS clnt.client (
  client_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sovereign_id        TEXT NOT NULL,
  legal_name          TEXT NOT NULL,
  fein                TEXT,
  domicile_state      TEXT,
  effective_date      DATE,
  status              TEXT NOT NULL DEFAULT 'active',
  source              TEXT,
  version             INT NOT NULL DEFAULT 1,
  domain              TEXT,
  label_override      TEXT,
  logo_url            TEXT,
  color_primary       TEXT,
  color_accent        TEXT,
  feature_flags       JSONB NOT NULL DEFAULT '{}',
  dashboard_blocks    JSONB NOT NULL DEFAULT '[]',
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_clnt_client_sovereign ON clnt.client(sovereign_id);

-- S1 Hub: ERROR
CREATE TABLE IF NOT EXISTS clnt.client_error (
  client_error_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id           UUID NOT NULL REFERENCES clnt.client(client_id),
  source_entity       TEXT NOT NULL,
  source_id           UUID,
  error_code          TEXT NOT NULL,
  error_message       TEXT NOT NULL,
  severity            TEXT NOT NULL DEFAULT 'error'
                      CHECK (severity IN ('warning', 'error', 'critical')),
  status              TEXT NOT NULL DEFAULT 'open'
                      CHECK (status IN ('open', 'resolved', 'dismissed')),
  context             JSONB,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clnt_client_error_client ON clnt.client_error(client_id);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION clnt.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_client_updated_at
  BEFORE UPDATE ON clnt.client
  FOR EACH ROW EXECUTE FUNCTION clnt.update_updated_at();

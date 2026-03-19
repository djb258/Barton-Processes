-- ═══════════════════════════════════════════════════════════════
-- Process 810 — D1 Working Tables (All 16 clnt tables)
-- ═══════════════════════════════════════════════════════════════
-- D1 = working layer. Neon = vault.
-- All 5 spokes mirrored for working operations.
-- Types simplified for SQLite (UUID→TEXT, TIMESTAMPTZ→TEXT, etc.)
-- ═══════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────
-- S1: HUB — Client Identity (read reference from 800)
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS client (
  client_id           TEXT PRIMARY KEY,
  sovereign_id        TEXT NOT NULL,
  legal_name          TEXT NOT NULL,
  status              TEXT NOT NULL DEFAULT 'active',
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

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

-- ─────────────────────────────────────────────────────────────
-- S2: PLAN — Benefits & Quote Intake
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS plan (
  plan_id             TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  benefit_type        TEXT NOT NULL,
  carrier_id          TEXT,
  effective_date      TEXT,
  status              TEXT NOT NULL DEFAULT 'active',
  version             INTEGER NOT NULL DEFAULT 1,
  rate_ee             REAL,
  rate_es             REAL,
  rate_ec             REAL,
  rate_fam            REAL,
  employer_rate_ee    REAL,
  employer_rate_es    REAL,
  employer_rate_ec    REAL,
  employer_rate_fam   REAL,
  source_quote_id     TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_plan_client ON plan(client_id);
CREATE INDEX IF NOT EXISTS idx_plan_vaulted ON plan(vaulted_at);

CREATE TABLE IF NOT EXISTS plan_error (
  plan_error_id       TEXT PRIMARY KEY,
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

CREATE INDEX IF NOT EXISTS idx_plan_error_client ON plan_error(client_id);

CREATE TABLE IF NOT EXISTS plan_quote (
  plan_quote_id       TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  benefit_type        TEXT NOT NULL,
  carrier_id          TEXT NOT NULL,
  effective_year      INTEGER NOT NULL,
  rate_ee             REAL,
  rate_es             REAL,
  rate_ec             REAL,
  rate_fam            REAL,
  source              TEXT,
  received_date       TEXT,
  status              TEXT NOT NULL DEFAULT 'received',
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_plan_quote_client ON plan_quote(client_id);

-- ─────────────────────────────────────────────────────────────
-- S3: EMPLOYEE — Enrollment & Identity
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS person (
  person_id           TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  first_name          TEXT NOT NULL,
  last_name           TEXT NOT NULL,
  ssn_hash            TEXT,
  status              TEXT NOT NULL DEFAULT 'active',
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_person_client ON person(client_id);
CREATE INDEX IF NOT EXISTS idx_person_vaulted ON person(vaulted_at);

CREATE TABLE IF NOT EXISTS employee_error (
  employee_error_id   TEXT PRIMARY KEY,
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

CREATE INDEX IF NOT EXISTS idx_employee_error_client ON employee_error(client_id);

CREATE TABLE IF NOT EXISTS election (
  election_id         TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  person_id           TEXT NOT NULL,
  plan_id             TEXT NOT NULL,
  coverage_tier       TEXT NOT NULL,
  effective_date      TEXT NOT NULL,
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_election_client ON election(client_id);
CREATE INDEX IF NOT EXISTS idx_election_person ON election(person_id);
CREATE INDEX IF NOT EXISTS idx_election_plan ON election(plan_id);

CREATE TABLE IF NOT EXISTS enrollment_intake (
  enrollment_intake_id TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  upload_date         TEXT NOT NULL DEFAULT (datetime('now')),
  status              TEXT NOT NULL DEFAULT 'pending',
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_enrollment_intake_client ON enrollment_intake(client_id);

CREATE TABLE IF NOT EXISTS intake_record (
  intake_record_id    TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  enrollment_intake_id TEXT NOT NULL,
  spoke               TEXT NOT NULL,
  raw_payload         TEXT NOT NULL,
  promoted_at         TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_intake_record_client ON intake_record(client_id);
CREATE INDEX IF NOT EXISTS idx_intake_record_batch ON intake_record(enrollment_intake_id);
CREATE INDEX IF NOT EXISTS idx_intake_record_promoted ON intake_record(promoted_at);

-- ─────────────────────────────────────────────────────────────
-- S4: VENDOR — Vendor Identity & Billing
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS vendor (
  vendor_id           TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  vendor_name         TEXT NOT NULL,
  vendor_type         TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_vendor_client ON vendor(client_id);

CREATE TABLE IF NOT EXISTS vendor_error (
  vendor_error_id     TEXT PRIMARY KEY,
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

CREATE INDEX IF NOT EXISTS idx_vendor_error_client ON vendor_error(client_id);

CREATE TABLE IF NOT EXISTS external_identity_map (
  external_identity_id TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  entity_type         TEXT NOT NULL,
  internal_id         TEXT NOT NULL,
  vendor_id           TEXT NOT NULL,
  external_id_value   TEXT NOT NULL,
  effective_date      TEXT,
  status              TEXT NOT NULL DEFAULT 'active',
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_eim_client ON external_identity_map(client_id);
CREATE INDEX IF NOT EXISTS idx_eim_vendor ON external_identity_map(vendor_id);

CREATE TABLE IF NOT EXISTS invoice (
  invoice_id          TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  vendor_id           TEXT NOT NULL,
  invoice_number      TEXT NOT NULL,
  amount              REAL NOT NULL,
  invoice_date        TEXT NOT NULL,
  due_date            TEXT,
  status              TEXT NOT NULL DEFAULT 'received',
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_invoice_client ON invoice(client_id);
CREATE INDEX IF NOT EXISTS idx_invoice_vendor ON invoice(vendor_id);

-- ─────────────────────────────────────────────────────────────
-- S5: SERVICE — Ticket Tracking
-- ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS service_request (
  service_request_id  TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  category            TEXT NOT NULL,
  status              TEXT NOT NULL DEFAULT 'open',
  opened_at           TEXT NOT NULL DEFAULT (datetime('now')),
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_service_request_client ON service_request(client_id);

CREATE TABLE IF NOT EXISTS service_error (
  service_error_id    TEXT PRIMARY KEY,
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

CREATE INDEX IF NOT EXISTS idx_service_error_client ON service_error(client_id);

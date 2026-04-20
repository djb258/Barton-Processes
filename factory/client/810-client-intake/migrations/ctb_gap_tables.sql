-- ============================================================
-- CTB Gap Tables Migration
-- Target: client-hub D1 (ID: 3ba426ee) — sections 1-4
-- Target: svg-d1-client D1 (ID: 5443887b) — section 5
-- Source: INSURANCE-INFORMATICS-CTB.md + CLIENT-SUB-HUB.md audit
-- Audit file: factory/client/TABLES-AUDIT.md
-- Date: 2026-04-16
-- Author: audit run by Claude Sonnet 4.6
-- Status: REVIEW REQUIRED — Dave must approve before applying
--
-- APPLY ORDER:
--   1. Sections 1-4 against client-hub D1
--   2. Section 5 against svg-d1-client D1
--   3. Dave decides DB consolidation before running section 6 (pending)
-- ============================================================


-- ============================================================
-- SECTION 1: CTB GAP TABLES — HIGH PRIORITY (client-hub D1)
-- The 10/85 workflow cannot function without these tables.
-- Every table follows CQRS: canonical + _error pair.
-- ============================================================

-- 1a. claims_case
-- One row per orchestrator-managed high-dollar case.
-- Spine of the 10% workflow. Triggered by PBM file feed flag or UM pre-cert.
-- FK to client + person in client-hub D1.
CREATE TABLE IF NOT EXISTS claims_case (
    case_id           TEXT PRIMARY KEY,
    client_id         TEXT NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
    person_id         TEXT NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,

    -- Classification
    trigger_type      TEXT NOT NULL CHECK (trigger_type IN ('drug_flag', 'hospital_precert')),
    case_status       TEXT NOT NULL DEFAULT 'intake' CHECK (case_status IN (
                          'intake', 'routed', 'vendor_active', 'babysitter',
                          'vendor_complete', 'service_rep_followup', 'closed'
                      )),

    -- Intake data
    trigger_date      TEXT NOT NULL,
    trigger_source    TEXT,          -- PBM file feed, UM vendor name, etc.
    trigger_detail    TEXT,          -- Drug name, procedure code, hospital name, etc.
    intake_notes      TEXT,          -- Orchestrator intake notes from employee call

    -- Routing
    waterfall_type    TEXT CHECK (waterfall_type IN ('hospital', 'drug')),
    routed_vendor_id  TEXT REFERENCES vendor(vendor_id) ON DELETE SET NULL,
    routed_at         TEXT,

    -- Babysitter mode
    babysitter_active INTEGER NOT NULL DEFAULT 0,
    last_vendor_check TEXT,          -- Timestamp of last orchestrator vendor check
    vendor_stall_flag INTEGER NOT NULL DEFAULT 0,

    -- Outcome
    resolved_at       TEXT,
    outcome_notes     TEXT,
    savings_amount    REAL,          -- Dollar savings achieved (vs original bill)

    -- ORBT
    orbt_mode         TEXT NOT NULL DEFAULT 'BUILD' CHECK (orbt_mode IN ('BUILD','OPERATE','REPAIR','TROUBLESHOOT_TRAIN')),
    strike_count      INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS claims_case_error (
    case_error_id     TEXT PRIMARY KEY,
    case_id           TEXT,          -- NULL if case creation itself failed
    client_id         TEXT NOT NULL,
    error_code        TEXT NOT NULL,
    error_message     TEXT NOT NULL,
    severity          TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context           TEXT,          -- JSON snapshot of the failing payload
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);


-- 1b. waterfall_status
-- Tracks which step of the hospital or drug waterfall a case is at.
-- Each case gets one active waterfall_status row per waterfall_type.
-- Step advances as vendor attempts each tier (e.g. PPO → RBP → 501R).
CREATE TABLE IF NOT EXISTS waterfall_status (
    waterfall_id      TEXT PRIMARY KEY,
    case_id           TEXT NOT NULL REFERENCES claims_case(case_id) ON DELETE CASCADE,
    client_id         TEXT NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
    waterfall_type    TEXT NOT NULL CHECK (waterfall_type IN ('hospital', 'drug')),

    -- Current position
    -- Hospital steps: ppo_network | rbp | nonprofit_501r
    -- Drug steps: map_pap | international_pharmacy | 340b
    current_step      TEXT NOT NULL,
    step_status       TEXT NOT NULL DEFAULT 'pending' CHECK (step_status IN (
                          'pending', 'in_progress', 'approved', 'denied', 'bypassed'
                      )),
    step_started_at   TEXT,
    step_completed_at TEXT,

    -- Prior steps (denormalized for fast dashboard reads)
    step_history      TEXT NOT NULL DEFAULT '[]',   -- JSON array of {step, status, outcome, date}

    -- Financials at this waterfall position
    bill_amount_at_step   REAL,      -- What the bill was when this step started
    savings_at_step       REAL,      -- Savings achieved at this step

    -- Timestamps
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS waterfall_status_error (
    waterfall_error_id TEXT PRIMARY KEY,
    waterfall_id       TEXT,
    case_id            TEXT NOT NULL,
    client_id          TEXT NOT NULL,
    error_code         TEXT NOT NULL,
    error_message      TEXT NOT NULL,
    severity           TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status             TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context            TEXT,
    created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);


-- 1c. bill_audit
-- Hospital bill audit — line-item comparison against Medicare rates.
-- Runs BEFORE the waterfall per CTB 10K: "STEP 1: BILL AUDIT (before anything else)"
-- One bill_audit row per hospital case (case_id). N bill_audit_line rows per audit.
CREATE TABLE IF NOT EXISTS bill_audit (
    audit_id          TEXT PRIMARY KEY,
    case_id           TEXT NOT NULL REFERENCES claims_case(case_id) ON DELETE CASCADE,
    client_id         TEXT NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,

    -- Hospital/provider info
    provider_name     TEXT,
    provider_npi      TEXT,
    facility_type     TEXT,          -- hospital, outpatient, ASC, etc.
    service_date      TEXT,

    -- Bill summary
    gross_billed      REAL NOT NULL,  -- What the hospital billed
    medicare_baseline REAL,           -- What Medicare would pay for same services
    audit_reduction   REAL,           -- Dollars saved from audit alone
    audit_reduction_pct REAL,         -- Percentage reduction

    -- Audit verdict
    audit_status      TEXT NOT NULL DEFAULT 'pending' CHECK (audit_status IN (
                          'pending', 'in_review', 'complete', 'disputed'
                      )),
    findings_summary  TEXT,           -- Free-text summary of what was caught
    auditor_vendor_id TEXT REFERENCES vendor(vendor_id) ON DELETE SET NULL,
    completed_at      TEXT,

    -- Timestamps
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Individual line items within a bill audit
CREATE TABLE IF NOT EXISTS bill_audit_line (
    line_id           TEXT PRIMARY KEY,
    audit_id          TEXT NOT NULL REFERENCES bill_audit(audit_id) ON DELETE CASCADE,

    -- Line detail
    billing_code      TEXT NOT NULL,  -- CPT, DRG, revenue code
    code_type         TEXT,           -- CPT, DRG, ICD10, REVENUE
    description       TEXT,
    units             REAL NOT NULL DEFAULT 1,

    -- Amounts
    billed_amount     REAL NOT NULL,
    medicare_amount   REAL,
    delta             REAL,           -- billed_amount - medicare_amount

    -- Finding
    finding_type      TEXT CHECK (finding_type IN (
                          'overbilling', 'duplicate', 'inflated', 'not_rendered',
                          'wrong_code', 'acceptable', NULL
                      )),
    finding_notes     TEXT,

    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bill_audit_error (
    audit_error_id    TEXT PRIMARY KEY,
    audit_id          TEXT,
    case_id           TEXT NOT NULL,
    client_id         TEXT NOT NULL,
    error_code        TEXT NOT NULL,
    error_message     TEXT NOT NULL,
    severity          TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context           TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);


-- 1d. orchestrator_handoff
-- Records the formal handoff when orchestrator transfers case to service rep
-- at the end of vendor execution. Closes the orchestrator's babysitter loop
-- and opens the service rep's "close the loop" phase.
-- Per CTB 10K: PHASE 2 — Service Rep closes after vendor is done.
CREATE TABLE IF NOT EXISTS orchestrator_handoff (
    handoff_id        TEXT PRIMARY KEY,
    case_id           TEXT NOT NULL REFERENCES claims_case(case_id) ON DELETE CASCADE,
    client_id         TEXT NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,

    -- Parties
    -- service_request_id links to the employee-facing ticket if one was opened
    service_request_id TEXT REFERENCES service_request(service_request_id) ON DELETE SET NULL,

    -- Handoff state
    handoff_status    TEXT NOT NULL DEFAULT 'pending' CHECK (handoff_status IN (
                          'pending', 'accepted', 'rep_contacted_employee',
                          'employee_satisfied', 'employee_escalated', 'closed'
                      )),
    handoff_notes     TEXT,          -- Orchestrator notes passed to service rep

    -- Outcome measurement
    process_worked    INTEGER,       -- 1=yes, 0=no, NULL=not yet assessed
    outcome_notes     TEXT,          -- What broke if process didn't work
    sigma_signal      TEXT CHECK (sigma_signal IN ('tightening', 'flat', 'expanding', NULL)),

    -- Timestamps
    handed_off_at     TEXT NOT NULL DEFAULT (datetime('now')),
    accepted_at       TEXT,
    closed_at         TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orchestrator_handoff_error (
    handoff_error_id  TEXT PRIMARY KEY,
    handoff_id        TEXT,
    case_id           TEXT NOT NULL,
    client_id         TEXT NOT NULL,
    error_code        TEXT NOT NULL,
    error_message     TEXT NOT NULL,
    severity          TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context           TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- SECTION 2: CTB GAP TABLES — MEDIUM PRIORITY (client-hub D1)
-- Dashboard config, HR comms, vendor contacts
-- ============================================================

-- 2a. hr_comms
-- Tracks HR-branded communications sent to employees per case.
-- Per CTB 10K: "HR-branded comm via Trello → preps employee"
-- Dave writes these; they go out branded as the client's HR department.
CREATE TABLE IF NOT EXISTS hr_comms (
    comm_id           TEXT PRIMARY KEY,
    case_id           TEXT REFERENCES claims_case(case_id) ON DELETE CASCADE,
    client_id         TEXT NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
    person_id         TEXT REFERENCES person(person_id) ON DELETE SET NULL,

    -- Communication detail
    comm_type         TEXT NOT NULL CHECK (comm_type IN (
                          'case_intro', 'intake_request', 'status_update',
                          'vendor_routing', 'resolution', 'follow_up'
                      )),
    channel           TEXT NOT NULL CHECK (channel IN ('email', 'sms', 'trello', 'mail', 'phone')),
    subject           TEXT,
    body_snippet      TEXT,          -- First 500 chars for audit trail
    branded_as        TEXT,          -- The HR sender name (e.g. "Acme Corp HR")
    source_trello_id  TEXT,          -- Trello card/board ID if sent via Trello

    -- Delivery
    sent_at           TEXT NOT NULL DEFAULT (datetime('now')),
    delivered         INTEGER NOT NULL DEFAULT 0,
    delivery_confirmed_at TEXT,

    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS hr_comms_error (
    comm_error_id     TEXT PRIMARY KEY,
    comm_id           TEXT,
    case_id           TEXT,
    client_id         TEXT NOT NULL,
    error_code        TEXT NOT NULL,
    error_message     TEXT NOT NULL,
    severity          TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context           TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);


-- 2b. vendor_contact
-- Two contacts per vendor: account_manager and customer_service.
-- Per CTB 5K: "Every vendor, two contacts. No exceptions."
-- Account manager = escalations / orchestrator babysitter contact
-- Customer service = routine 90/15 ticket routing target
CREATE TABLE IF NOT EXISTS vendor_contact (
    contact_id        TEXT PRIMARY KEY,
    vendor_id         TEXT NOT NULL REFERENCES vendor(vendor_id) ON DELETE CASCADE,
    client_id         TEXT NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,

    -- Contact classification (exactly two per vendor per CTB)
    contact_role      TEXT NOT NULL CHECK (contact_role IN ('account_manager', 'customer_service')),

    -- Contact details
    full_name         TEXT,
    email             TEXT,
    phone             TEXT,
    phone_ext         TEXT,
    title             TEXT,

    -- Routing flags
    is_escalation_contact  INTEGER NOT NULL DEFAULT 0,  -- Account manager escalation target
    is_ticket_route_target INTEGER NOT NULL DEFAULT 0,  -- Customer service ticket route target
    notes             TEXT,

    -- Status
    status            TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    effective_date    TEXT,
    end_date          TEXT,

    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now')),

    -- Enforce two-contact pattern: one account_manager + one customer_service per vendor per client
    UNIQUE (vendor_id, client_id, contact_role)
);

CREATE TABLE IF NOT EXISTS vendor_contact_error (
    contact_error_id  TEXT PRIMARY KEY,
    contact_id        TEXT,
    vendor_id         TEXT NOT NULL,
    client_id         TEXT NOT NULL,
    error_code        TEXT NOT NULL,
    error_message     TEXT NOT NULL,
    severity          TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context           TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);


-- 2c. dashboard_config
-- Per-client dashboard block configuration.
-- Per CTB 5K: five dashboards per client. This table controls which blocks
-- each dashboard shows, ordering, and any client-specific overrides.
CREATE TABLE IF NOT EXISTS dashboard_config (
    config_id         TEXT PRIMARY KEY,
    client_id         TEXT NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,

    -- Which dashboard this config applies to
    dashboard_type    TEXT NOT NULL CHECK (dashboard_type IN (
                          'hr', 'cfo', 'underwriting', 'renewal', 'service_advisor'
                      )),

    -- Block configuration (JSON array of block definitions)
    -- Each block: {block_id, block_type, title, query, display_order, visible}
    blocks            TEXT NOT NULL DEFAULT '[]',

    -- Feature flags for this dashboard
    show_savings_banner  INTEGER NOT NULL DEFAULT 1,
    show_waterfall_status INTEGER NOT NULL DEFAULT 1,
    show_case_tracker    INTEGER NOT NULL DEFAULT 1,

    -- Branding overrides (inherits from client.color_primary if NULL)
    color_primary     TEXT,
    color_accent      TEXT,
    logo_url_override TEXT,

    -- Status
    status            TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'draft')),
    version           INTEGER NOT NULL DEFAULT 1,

    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now')),

    -- One config per dashboard type per client
    UNIQUE (client_id, dashboard_type)
);

CREATE TABLE IF NOT EXISTS dashboard_config_error (
    config_error_id   TEXT PRIMARY KEY,
    config_id         TEXT,
    client_id         TEXT NOT NULL,
    error_code        TEXT NOT NULL,
    error_message     TEXT NOT NULL,
    severity          TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context           TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- SECTION 3: MISSING CQRS ERROR TABLES — client-hub D1
-- Existing canonical tables that are missing their _error pair.
-- ============================================================

CREATE TABLE IF NOT EXISTS plan_quote_error (
    plan_quote_error_id TEXT PRIMARY KEY,
    client_id           TEXT NOT NULL,
    source_entity       TEXT NOT NULL,
    source_id           TEXT,
    error_code          TEXT NOT NULL,
    error_message       TEXT NOT NULL,
    severity            TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status              TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context             TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS election_error (
    election_error_id   TEXT PRIMARY KEY,
    client_id           TEXT NOT NULL,
    source_entity       TEXT NOT NULL,
    source_id           TEXT,
    error_code          TEXT NOT NULL,
    error_message       TEXT NOT NULL,
    severity            TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status              TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context             TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS enrollment_intake_error (
    enrollment_intake_error_id TEXT PRIMARY KEY,
    client_id                  TEXT NOT NULL,
    source_entity              TEXT NOT NULL,
    source_id                  TEXT,
    error_code                 TEXT NOT NULL,
    error_message              TEXT NOT NULL,
    severity                   TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status                     TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context                    TEXT,
    created_at                 TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS intake_record_error (
    intake_record_error_id TEXT PRIMARY KEY,
    client_id              TEXT NOT NULL,
    source_entity          TEXT NOT NULL,
    source_id              TEXT,
    error_code             TEXT NOT NULL,
    error_message          TEXT NOT NULL,
    severity               TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status                 TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context                TEXT,
    created_at             TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS external_identity_map_error (
    ext_id_error_id TEXT PRIMARY KEY,
    client_id       TEXT NOT NULL,
    source_entity   TEXT NOT NULL,
    source_id       TEXT,
    error_code      TEXT NOT NULL,
    error_message   TEXT NOT NULL,
    severity        TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status          TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context         TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS invoice_error (
    invoice_error_id TEXT PRIMARY KEY,
    client_id        TEXT NOT NULL,
    source_entity    TEXT NOT NULL,
    source_id        TEXT,
    error_code       TEXT NOT NULL,
    error_message    TEXT NOT NULL,
    severity         TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status           TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context          TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- SECTION 4: SCHEMA COLUMN ADDITIONS — client-hub D1
-- Existing tables missing columns required by CTB.
-- SQLite requires one ALTER TABLE ADD COLUMN statement per column.
-- ============================================================

-- vendor table: add group_number and integration_type
-- (currently only has vendor_name + vendor_type)
ALTER TABLE vendor ADD COLUMN group_number TEXT;
ALTER TABLE vendor ADD COLUMN integration_type TEXT CHECK (integration_type IN ('api', 'sftp', 'portal', 'manual', NULL));

-- service_request table: add priority, linked case, and resolution fields
ALTER TABLE service_request ADD COLUMN priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent'));
ALTER TABLE service_request ADD COLUMN linked_case_id TEXT REFERENCES claims_case(case_id) ON DELETE SET NULL;
ALTER TABLE service_request ADD COLUMN resolution_notes TEXT;
ALTER TABLE service_request ADD COLUMN resolved_at TEXT;
ALTER TABLE service_request ADD COLUMN assigned_vendor_type TEXT;  -- Which vendor type this ticket routes to

-- person table: add date_of_birth and zip_code for 10/85 intake pre-population
-- per CTB 10K enrollment: "data already partially in DB from enrollment"
ALTER TABLE person ADD COLUMN date_of_birth TEXT;
ALTER TABLE person ADD COLUMN zip_code TEXT;
ALTER TABLE person ADD COLUMN gender TEXT;
ALTER TABLE person ADD COLUMN phone TEXT;
ALTER TABLE person ADD COLUMN email TEXT;


-- ============================================================
-- SECTION 5: MISSING CQRS ERROR TABLES — svg-d1-client D1
-- Apply this section against svg-d1-client D1, not client-hub.
-- ============================================================

CREATE TABLE IF NOT EXISTS client_employees_error (
    employee_error_id TEXT PRIMARY KEY,
    client_id         TEXT NOT NULL,
    source_entity     TEXT NOT NULL,
    source_id         TEXT,
    error_code        TEXT NOT NULL,
    error_message     TEXT NOT NULL,
    severity          TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status            TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context           TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS client_contacts_error (
    contact_error_id TEXT PRIMARY KEY,
    client_id        TEXT NOT NULL,
    source_entity    TEXT NOT NULL,
    source_id        TEXT,
    error_code       TEXT NOT NULL,
    error_message    TEXT NOT NULL,
    severity         TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status           TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context          TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS client_vendors_error (
    vendor_error_id TEXT PRIMARY KEY,
    client_id       TEXT NOT NULL,
    source_entity   TEXT NOT NULL,
    source_id       TEXT,
    error_code      TEXT NOT NULL,
    error_message   TEXT NOT NULL,
    severity        TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status          TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context         TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS client_compliance_error (
    compliance_error_id TEXT PRIMARY KEY,
    client_id           TEXT NOT NULL,
    source_entity       TEXT NOT NULL,
    source_id           TEXT,
    error_code          TEXT NOT NULL,
    error_message       TEXT NOT NULL,
    severity            TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status              TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context             TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS client_interactions_error (
    interaction_error_id TEXT PRIMARY KEY,
    client_id            TEXT NOT NULL,
    source_entity        TEXT NOT NULL,
    source_id            TEXT,
    error_code           TEXT NOT NULL,
    error_message        TEXT NOT NULL,
    severity             TEXT NOT NULL DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical')),
    status               TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'suppressed')),
    context              TEXT,
    created_at           TEXT NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- END OF MIGRATION
-- Total new tables added to client-hub D1:
--   Section 1 (CTB gaps, HIGH): 10 tables
--     claims_case, claims_case_error
--     waterfall_status, waterfall_status_error
--     bill_audit, bill_audit_line, bill_audit_error
--     orchestrator_handoff, orchestrator_handoff_error
--   Section 2 (CTB gaps, MEDIUM): 6 tables
--     hr_comms, hr_comms_error
--     vendor_contact, vendor_contact_error
--     dashboard_config, dashboard_config_error
--   Section 3 (CQRS gaps, existing tables): 6 error tables
--     plan_quote_error, election_error, enrollment_intake_error,
--     intake_record_error, external_identity_map_error, invoice_error
--   Section 4 (column additions): 7 columns across 3 tables
--     vendor: group_number, integration_type
--     service_request: priority, linked_case_id, resolution_notes, resolved_at, assigned_vendor_type
--     person: date_of_birth, zip_code, gender, phone, email
-- Total new tables added to svg-d1-client D1:
--   Section 5 (CQRS gaps): 5 error tables
--     client_employees_error, client_contacts_error, client_vendors_error,
--     client_compliance_error, client_interactions_error
-- ============================================================

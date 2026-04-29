# Client Sub-Hub — Tables Audit
## Both D1 databases audited against the Insurance Informatics CTB
### Audit Date: 2026-04-16
### Authority: Dave Barton
### Status: REVIEW REQUIRED — migrations written, not yet applied

---

## SECTION 1 — DATABASE INVENTORY

### client-hub D1 (ID: 3ba426ee) — Operational domain tables
| Table | CQRS Pair | Schema Status | Notes |
|-------|-----------|--------------|-------|
| client | client_error | PRESENT | Has dashboard_blocks, feature_flags, label_override, logo_url — complete |
| plan | plan_error | PRESENT | Has full tier rates (ee/es/ec/fam) for both employee and employer — complete |
| plan_quote | (none — no error table) | PRESENT, GAP | Missing plan_quote_error table |
| person | employee_error | PRESENT, MISMATCH | Canonical table is `person` but error table is `employee_error` — naming inconsistency |
| election | (none — no error table) | PRESENT, GAP | Missing election_error table |
| enrollment_intake | (none — no error table) | PRESENT, GAP | Missing enrollment_intake_error table |
| intake_record | (none — no error table) | PRESENT, GAP | Missing intake_record_error table |
| vendor | vendor_error | PRESENT | Schema is thin (vendor_name, vendor_type only) — no group_number, no integration_type |
| external_identity_map | (none — no error table) | PRESENT, GAP | Missing external_identity_map_error table |
| invoice | (none — no error table) | PRESENT, GAP | Missing invoice_error table |
| service_request | service_error | PRESENT, MISMATCH | Canonical table is `service_request` but error table is `service_error` — naming inconsistency |

### svg-d1-client D1 (ID: 5443887b) — CRM / compliance layer tables
| Table | CQRS Pair | Schema Status | Notes |
|-------|-----------|--------------|-------|
| clients | clients_error | PRESENT | Full HEIR fields, lifecycle, ORBT — complete |
| client_employees | (none — no error table) | PRESENT, GAP | Missing client_employees_error table |
| client_contacts | (none — no error table) | PRESENT, GAP | Missing client_contacts_error table |
| client_vendors | (none — no error table) | PRESENT, GAP | Missing client_vendors_error table |
| client_compliance | (none — no error table) | PRESENT, GAP | Missing client_compliance_error table |
| client_interactions | (none — no error table) | PRESENT, GAP | Missing client_interactions_error table |
| client_entity_relationships | (none) | PRESENT | No CQRS error table — this is a join table, may be acceptable |
| client_employee_vendor_ids | (none) | PRESENT | No CQRS error table — mapping table, acceptable |
| client_audit_lineage | (none) | PRESENT | Append-only by doctrine — no error table needed |
| client_staging_intake | (none) | PRESENT | Staging table — acceptable |

---

## SECTION 2 — CTB GAP ANALYSIS

Tables required by the Insurance Informatics CTB that do not exist in either database.

### MISSING — HIGH PRIORITY (10/85 workflow cannot operate without these)

| Table | Database Target | CTB Source | What It Tracks |
|-------|----------------|------------|----------------|
| claims_case | client-hub | CTB 10K — 10/85 Team, The Flow | One orchestrator-managed case per high-dollar event (drug flag or hospital pre-cert trigger). The spine of the 10% workflow. |
| claims_case_error | client-hub | CQRS pair for claims_case | CQRS error table |
| waterfall_status | client-hub | CTB 10K — Hospital Claim Flow, Drug Waterfall | Which step of the hospital waterfall (PPO/RBP/501R) or drug waterfall (MAP/PAP / international / 340B) the case is currently at |
| waterfall_status_error | client-hub | CQRS pair | CQRS error table |
| bill_audit | client-hub | CTB 10K — Hospital Claim Flow Step 1 | Line-item audit of hospital bill against Medicare rates. Tracks gross charge, Medicare rate, delta, and audit verdict per line |
| bill_audit_error | client-hub | CQRS pair | CQRS error table |
| orchestrator_handoff | client-hub | CTB 10K — 10/85 Team, SERVICE 10/85 FLOW | Handoff record when orchestrator routes a case to a service rep after the vendor process completes |
| orchestrator_handoff_error | client-hub | CQRS pair | CQRS error table |

### MISSING — MEDIUM PRIORITY (dashboards and comms layer)

| Table | Database Target | CTB Source | What It Tracks |
|-------|----------------|------------|----------------|
| hr_comms | client-hub | CTB 10K — 10/85 Flow (Trello-branded comms) | HR-branded communications sent to employee per case (what was sent, when, which case it tied to) |
| hr_comms_error | client-hub | CQRS pair | CQRS error table |
| vendor_contact | client-hub | CTB 5K — Vendor Contacts (Two contacts per vendor) | Account manager + customer service contact per vendor. The "Twos Pattern" for vendor relationships |
| vendor_contact_error | client-hub | CQRS pair | CQRS error table |
| dashboard_config | client-hub | CTB 5K — Dashboards (per-client block config) | Per-client dashboard block configuration (which blocks show, what data they pull, ordering) |
| dashboard_config_error | client-hub | CQRS pair | CQRS error table |

### SCHEMA GAPS IN EXISTING TABLES

| Table | Database | Gap | Recommendation |
|-------|----------|-----|----------------|
| vendor (client-hub) | client-hub | Missing group_number, integration_type (API/SFTP/Portal/Manual), account_manager_contact_id | Add columns via ALTER TABLE migration or replace with vendor_contact table reference |
| service_request (client-hub) | client-hub | Missing priority field, linked_case_id (to tie a ticket to a claims_case), resolution_notes | Add columns via migration |
| person (client-hub) | client-hub | Missing date_of_birth, zip_code (needed for 10/85 intake pre-population per CTB enrollment section) | Add columns via migration |

---

## SECTION 3 — DATABASE OVERLAP / DUPLICATION ANALYSIS

Two databases are doing overlapping work. This needs a consolidation decision before BAR-82 proceeds.

### Duplicate Concepts

| Concept | client-hub Table | svg-d1-client Table | Verdict |
|---------|-----------------|--------------------|---------| 
| Company / Client identity | `client` | `clients` | OVERLAP — client-hub `client` is the operational record (branding, feature flags). svg-d1-client `clients` is the CRM record (lifecycle, ORBT, sovereign_id). Different enough to keep both but need explicit FK or shared client_id contract |
| Employee record | `person` | `client_employees` | OVERLAP — `person` is the Golden Record for enrollment/elections. `client_employees` is the CRM/HR record (hire date, employment status). Both are needed but `person.person_id` and `client_employees.employee_id` are separate UUIDs for the same human. This breaks the join chain — they need a cross-reference or shared ID |
| Vendor | `vendor` | `client_vendors` | OVERLAP — nearly identical schemas. `client_vendors` has more fields (group_number, integration_type). Recommendation: consolidate to client-hub `vendor` table with added columns, and drop `client_vendors` from svg-d1-client |

### Consolidation Recommendation

**Decision required from Dave before BAR-82 can proceed.**

Three options:
1. **client-hub is canonical** — svg-d1-client tables are supplementary CRM layer only. `person.person_id` becomes the shared identity key; `client_employees.employee_id` is deprecated, column added to `client_employees` as `person_id FK`. `vendor` table in client-hub absorbs `client_vendors` columns.
2. **svg-d1-client is canonical** — client-hub worker is bound to svg-d1-client as primary DB, client-hub D1 becomes the fast operational cache. More complex.
3. **Keep both, explicit cross-reference** — Add `svg_client_employee_id` to `person` table in client-hub pointing to `client_employees.employee_id` in svg-d1-client. Explicit join contract. More joins, but zero destructive migration needed.

**Current recommendation: Option 1.** client-hub is already deployed, already bound to the worker, already has the enrollment pipeline writing to it. svg-d1-client is not bound to any worker yet. Promoting client-hub as canonical is the lower-risk path.

---

## SECTION 4 — CQRS COMPLIANCE SUMMARY

Every canonical table must have a corresponding `_error` table per the CQRS pattern in FOUNDATIONAL_BEDROCK.md.

### client-hub — Missing error tables for existing canonical tables

| Canonical Table | Missing Error Table |
|----------------|-------------------|
| plan_quote | plan_quote_error |
| election | election_error |
| enrollment_intake | enrollment_intake_error |
| intake_record | intake_record_error |
| external_identity_map | external_identity_map_error |
| invoice | invoice_error |

### svg-d1-client — Missing error tables for existing canonical tables

| Canonical Table | Missing Error Table |
|----------------|-------------------|
| client_employees | client_employees_error |
| client_contacts | client_contacts_error |
| client_vendors | client_vendors_error |
| client_compliance | client_compliance_error |
| client_interactions | client_interactions_error |

### Naming inconsistencies in client-hub (should be fixed)

| Canonical Table | Existing Error Table | Expected Error Table Name |
|----------------|---------------------|--------------------------|
| person | employee_error | person_error |
| service_request | service_error | service_request_error |

---

## SECTION 5 — MIGRATION PLAN

All missing tables and schema fixes are written to:
`factory/client/810-client-intake/migrations/ctb_gap_tables.sql`

**Order of operations:**
1. Apply ctb_gap_tables.sql to client-hub D1 — adds CTB gap tables + missing CQRS error tables
2. Apply ctb_gap_tables.sql CQRS section to svg-d1-client D1 — adds missing error tables for that DB
3. Dave decides on DB consolidation (Section 3 above) — then a second migration handles person/employee and vendor deduplication
4. Bind svg-d1-client to client-hub worker (wrangler.toml update)
5. BAR-82 can proceed

**DO NOT APPLY until Dave reviews and signs off.**

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-16 |
| Auditor | Claude Sonnet 4.6 |
| Databases Audited | client-hub (3ba426ee), svg-d1-client (5443887b) |
| CTB Source | fleet/content/INSURANCE-INFORMATICS-CTB.md |
| Hub Doc | fleet/docs/CLIENT-SUB-HUB.md |
| Migration File | factory/client/810-client-intake/migrations/ctb_gap_tables.sql |
| Status | REVIEW REQUIRED |

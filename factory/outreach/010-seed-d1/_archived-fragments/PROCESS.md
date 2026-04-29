> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# PROCESS: SVG D1 SEED
## Copies the company footprint from Neon vault into D1 workspace for every company inside an agent's coverage zone
### Status: OPERATE
### Sub-Hub: outreach
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-010 |
| Name | SVG D1 SEED |
| Sub-Hub | outreach |
| Business Silo | svg-agency |
| CTB Position | factory/outreach/010-seed-d1 |
| Blueprint Repo | barton-outreach-core |
| Blueprint Section | doctrine/OSAM.md — outreach schema, join paths, CQRS write rules |
| ORBT | OPERATE |
| Strikes | 0 |
| Last Deployed | 2026-04-01 |
| BAR Reference | BAR-52 |
| Deployed URL | https://lcs-hub.svg-outreach.workers.dev (SEED endpoints) |
| Cron | Manual (run before any SVG process operates) |
| Runtime | CF Worker (lcs-hub) via Hyperdrive to Neon |

---

## 2. WHY THIS EXISTS

Without this process, D1 is empty. Every SVG process (100 LCS Pipeline, 200 People Worker, 300 Blog Worker — all of them) reads from D1. If the SEED didn't run, nothing downstream works.

The agent + ZIP + radius is the gate that controls the entire flow. No agent assignment, no SEED, no downstream processes. Nothing gets a footprint, nothing gets pulled to D1, nothing gets worked on unless it falls inside an agent's coverage zone.

**THIS IS THE ONLY PROCESS THAT READS FROM NEON.** Every other SVG process reads exclusively from D1. The lifecycle is SEED (Neon → D1) → WORK (D1 only) → PUSH (D1 → Neon). Only Process 010 does the SEED.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Manual. Run before any SVG process operates. Re-run when Neon data changes (new companies, new agents, new coverage zones).
2. **"How do we get it?"** — Hyperdrive connection to Neon PostgreSQL vault.

### Input
- Agent name + anchor ZIP code + 100-mile radius
- Currently 3 agents: Dave Allan (26739 WV), Jeff Mussolino (21742 MD), David Vang (28461 NC)
- The agent defines the geography, not company ownership. Companies in overlapping zones get multiple agents in `service_agents` column (e.g., SA-001,SA-002). Distribution: 29,775 single-agent + 2,927 dual-agent = 32,702.

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Agent anchor ZIP + 100mi radius | Haversine expansion against `reference.us_zip_codes` (41,553 ZIPs with lat/lon) | All ZIP codes within 100mi of each agent's anchor | `coverage.v_service_agent_coverage_zips` (Neon view) |
| 2 | Qualifying ZIPs | Match against `outreach.company_target.postal_code` to get outreach_ids | 32,702 outreach_ids that passed Gate 0 | Neon SQL JOIN |
| 3 | Qualifying outreach_ids | Tie back to sovereign_id via `cl.company_identity` | outreach_id ↔ sovereign_id link confirmed | Neon SQL JOIN |
| 4 | Qualifying outreach_ids | Copy CT sub-hub — city, state, postal_code, industry, employees, email_method + agent assignment | `outreach_company_target` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 5 | Qualifying outreach_ids | Copy DOL sub-hub — filing_present, ein, carrier, renewal_month + full filing detail (form_5500, schedule_a, schedule_c, schedule_other) | `outreach_dol` + `dol_form_5500` + `dol_schedule_*` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 6 | Qualifying outreach_ids | Copy Blog sub-hub — about_url, source_url, sitemap structure. First pass maps everything. After that, quick update for changes only. | `outreach_blog` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 7 | Qualifying outreach_ids | Copy People sub-hub — 3 slots per company (CEO, CFO, HR), always 3, filled or empty. Each filled slot ties to a person record with verified email + LinkedIn URL. | `people_company_slot` + `people_people_master` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 8 | Coverage reference | Copy coverage tables for local reference | `coverage_service_agent` + `coverage_service_agent_coverage` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 9 | Qualifying outreach_ids | Copy Hunter contacts — verified emails, LinkedIn URLs, phone numbers, confidence scores. 175K rows of gold from Hunter.io enrichment. | `enrichment_hunter_contact` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 10 | Qualifying outreach_ids | Copy Hunter email patterns — one pattern per domain (e.g., {first}.{last}@domain). Only domains with known patterns (15,537). | `enrichment_hunter_company` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 11 | Qualifying outreach_ids | Copy Vendor people — enriched contacts from vendor pipeline with mapped_slot_type. Overlaps Hunter but includes slot mapping + backfill metadata. | `vendor_people` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 12 | Qualifying outreach_ids | Copy Vendor CT — enriched company data with email patterns, company phone, description, LinkedIn. | `vendor_ct` in D1 | Hyperdrive → D1 INSERT OR REPLACE |

### Output
- D1 fully populated with the complete footprint for every company inside an agent's coverage zone
- Footprint per company = CT + DOL + Blog + People (3 slots with person records) + Hunter contacts + Hunter email patterns + Vendor people + Vendor CT
- All hanging off one outreach_id (the spine)
- If a new sub-hub appears (e.g., workers comp), it goes into Neon first, then the SEED pulls it to D1. The pattern is the constant. The sub-hubs are the variable.

### Circle (Bedrock §5)
After SEED completes, run the post-SEED audit (section 9) to verify all joins. If join integrity drops below 99%, re-run the failing step. Log results to LBB.

### Source of Truth — Neon SEED Views

**SEED reads from `seed_views` schema in Neon (Marketing DB).** These views are read-only lenses scoped to the 32,702 agent-assigned companies. The SEED is a dumb copy — no filtering logic in the SEED code. The views ARE the gate.

| Neon View | D1 Target | Rows | Logic |
|-----------|-----------|------|-------|
| `seed_views.v_agent_companies` | `outreach_company_target` | 32,702 | The gate — ZIP coverage |
| `seed_views.v_agent_cl_identity` | `cl_company_identity` (spine) | 32,702 | 1:1 sovereign IDs |
| `seed_views.v_agent_outreach` | `outreach_outreach` | 32,702 | 1:1 outreach status |
| `seed_views.v_agent_blog` | `outreach_blog` | 32,702 | `vendor.blog` + `outreach.blog` merged, materialized |
| `seed_views.v_agent_dol` | `outreach_dol` | 32,702 | LEFT JOIN — empty row if no filing |
| `seed_views.v_agent_slots` | `people_company_slot` | 98,106 | 32,702 × 3 (CEO, CFO, HR) |
| `seed_views.v_agent_people` | `people_people_master` | 58,857 | Only people referenced by filled slots |
| `seed_views.v_agent_hunter_contacts` | `enrichment_hunter_contact` | 175,632 | Hunter.io verified emails + people |
| `seed_views.v_agent_hunter_patterns` | `enrichment_hunter_company` | 15,537 | Email patterns per domain (e.g., {first}.{last}) |
| `seed_views.v_agent_vendor_people` | `vendor_people` | 175,632 | Vendor-enriched contacts with slot mapping |
| `seed_views.v_agent_vendor_ct` | `vendor_ct` | 18,683 | Vendor-enriched company data + email patterns |
| `seed_views.v_agent_fill_rates` | _(reference only)_ | 32,702 | Completeness scorecard |

**The chain:** Agent anchor ZIP + radius → `coverage.v_service_agent_coverage_zips` → qualifying ZIPs → `outreach.company_target.postal_code` → 32,702 companies. The agent defines the geography. The geography defines the universe. Agent assignment to a specific company is a downstream variable.

**Locked constant: 32,702.** Every D1 table must have exactly 32,702 rows (or 98,106 for slots). If D1 counts don't match, the SEED is dirty. See `SEED_AUDIT.md` for full trace.

**Materialized views** (`v_agent_blog`, `v_agent_fill_rates`) need refreshing after data changes:
```sql
REFRESH MATERIALIZED VIEW seed_views.v_agent_blog;
REFRESH MATERIALIZED VIEW seed_views.v_agent_fill_rates;
```

**Neon Database:** Marketing DB (`OUTREACH_DATABASE_URL` in Doppler)

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | WRITE | All outreach sub-hub tables (target for SEED) |
| svg-d1-spine | D1 | 641a9a1e | WRITE | cl_company_identity (32,702 sovereign records — 1:1 scoped by seed_views) |
| Neon PostgreSQL | HD_NEON (Hyperdrive) | — | READ | Source vault — all schemas (cl, outreach, people, dol, coverage, reference) |

### Snap-On Toolbox Sub-Hubs (law/SNAP_ON_TOOLBOX.yaml)

| Tool # | Sub-Hub | Recommended Vendor | What It Does In This Process |
|--------|---------|-------------------|------------------------------|
| 11 | structured-data | Cloudflare D1 | D1 outreach writes (all sub-hub tables) |
| 16 | fetcher | Hyperdrive to Neon | Reads vault data for SEED transfer |
| 06 | api-layer | Hono | Hosts /seed/* HTTP endpoints on lcs-hub worker |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| NEON_URL | imo-creator | dev | Hyperdrive binding (configured in wrangler.toml, not runtime) |

### Blueprint References

| Blueprint | Repo | Path | What It Defines |
|-----------|------|------|-----------------|
| Outreach OSAM | barton-outreach-core | doctrine/OSAM.md v1.1.2 | Full Neon schema, join paths, CQRS rules |
| CL OSAM | company-lifecycle-cl | doctrine/OSAM.md v1.0.0 | CL spine identity, sovereign_company_id |
| Snap-On Toolbox | imo-creator | law/SNAP_ON_TOOLBOX.yaml v4.0.0 | 26 tool sub-hubs, vendors (swappable), banned list |
| D1 Data Dictionary | Barton-Processes | D1_DATA_DICTIONARY.md v1.0.0 | AI-ready column reference for D1 workspace |

---

## 5. OSAM + ERD — Where the Data Lives (AI-Ready Column Reference)

### D1 Target: svg-d1-outreach-ops (73a285b8)
### Row counts as of 2026-04-01

---

### outreach_outreach — Spine table (32,702 rows)
The universal join key for all sub-hubs. Every company in D1 has one row here.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| outreach_id | TEXT | PK, NOT NULL | Universal join key — every sub-hub table joins on this |
| sovereign_id | TEXT | NOT NULL | Maps back to cl.company_identity.company_unique_id |
| domain | TEXT | | Company website domain (e.g., acmecorp.com) |
| ein | TEXT | | Employer Identification Number from DOL filings |
| has_appointment | INTEGER | | Whether company has an existing broker appointment |
| created_at | TEXT | NOT NULL | Record creation timestamp |
| updated_at | TEXT | NOT NULL | Last modification timestamp |

---

### outreach_company_target — CT sub-hub (32,702 rows)
Company targeting data — geo, industry, employees, agent assignment. One row per company. Agent assignment via `service_agents` (comma-separated, e.g., SA-001,SA-002) and `agent_count`.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| target_id | TEXT | PK, NOT NULL | Unique target record identifier |
| company_unique_id | TEXT | | Maps to cl.company_identity.company_unique_id |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| city | TEXT | | Company city |
| state | TEXT | | Company state (2-letter code) |
| postal_code | TEXT | | Company ZIP code — used for Gate 0 coverage filter |
| country | TEXT | | Country code |
| industry | TEXT | | Industry classification |
| employees | INTEGER | | Employee headcount |
| email_method | TEXT | | How we deliver email (direct, catchall, etc.) |
| method_type | TEXT | | Email method classification |
| confidence_score | REAL | | Confidence in email delivery method (0.0–1.0) |
| is_catchall | INTEGER | | Whether domain accepts any email address |
| outreach_status | TEXT | NOT NULL | Current outreach state (queued, active, paused) |
| execution_status | TEXT | | Execution pipeline state |
| imo_completed_at | TEXT | | When IMO processing completed |
| bit_score_snapshot | INTEGER | | DEPRECATED — BIT scoring retired 2026-03-25 |
| data_year | INTEGER | | Year of the targeting data |
| postal_code_source | TEXT | | Where the ZIP code came from |
| postal_code_updated_at | TEXT | | When ZIP was last verified |
| first_targeted_at | TEXT | | When company first entered targeting |
| last_targeted_at | TEXT | | When company was last targeted |
| sequence_count | INTEGER | NOT NULL | Number of outreach sequences sent |
| active_sequence_id | TEXT | | Currently active sequence |
| source | TEXT | | Data source for this record |
| service_agents | TEXT | | Comma-separated agent numbers (e.g., SA-001,SA-002) — agents define geography, companies in overlapping zones get multiple |
| agent_count | INTEGER | | Number of agents covering this company (1 or 2) |
| created_at | TEXT | NOT NULL | Record creation timestamp |
| updated_at | TEXT | NOT NULL | Last modification timestamp |

---

### outreach_dol — DOL sub-hub (27,464 rows)
DOL filing summary per company. One row per outreach_id. Only companies with filings (not all 32,702).

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| dol_id | TEXT | NOT NULL | Unique DOL record identifier |
| outreach_id | TEXT | NOT NULL | FK → outreach_outreach.outreach_id |
| ein | TEXT | | Employer Identification Number |
| filing_present | INTEGER | | Whether company has DOL filings (0/1) |
| funding_type | TEXT | | Plan funding type (fully insured, self-funded, etc.) |
| broker_or_advisor | TEXT | | Current broker or advisor name |
| carrier | TEXT | | Current insurance carrier name |
| renewal_month | INTEGER | | Plan renewal month (1-12) |
| outreach_start_month | INTEGER | | When outreach should begin relative to renewal |
| url_enrichment_data | TEXT | | JSON blob of URL-based enrichment |
| created_at | TEXT | | Record creation timestamp |
| updated_at | TEXT | | Last modification timestamp |

---

### outreach_blog — Blog sub-hub (32,702 rows)
Web presence data per company. 1:1 with company target (clean). Now uses `vendor.blog` (290K crawl data) merged with `outreach.blog`. URL mapping is the constant, content state is the variable.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| blog_id | TEXT | NOT NULL | Unique blog record identifier |
| outreach_id | TEXT | NOT NULL | FK → outreach_outreach.outreach_id |
| about_url | TEXT | | Company about/team page URL (mapped by Process 300) |
| source_url | TEXT | | Primary source URL for web content |
| news_url | TEXT | | Company news/blog URL |
| context_summary | TEXT | | Extracted content: people names/titles (JSON) or movement data |
| source_type | TEXT | | Source classification |
| source_type_enum | TEXT | | Enumerated source type |
| extraction_method | TEXT | | How content was extracted (direct_fetch, proxy, manual) |
| last_extracted_at | TEXT | | When content was last extracted |
| context_timestamp | TEXT | | Timestamp of the extracted content |
| created_at | TEXT | | Record creation timestamp |
| updated_at | TEXT | | Last modification timestamp |

---

### outreach_people — DEPRECATED (no longer used)
Legacy table from pre-slot model. Replaced by people_company_slot + people_people_master.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| person_id | TEXT | NOT NULL | Unique person identifier |
| target_id | TEXT | NOT NULL | FK → outreach_company_target.target_id |
| company_unique_id | TEXT | NOT NULL | FK → cl.company_identity.company_unique_id |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| slot_type | TEXT | | Role slot (CEO, CFO, HR) |
| email | TEXT | NOT NULL | Contact email address |
| email_verified | INTEGER | NOT NULL | Whether email is verified (0/1) |
| email_verified_at | TEXT | | When email was verified |
| contact_status | TEXT | NOT NULL | Current contact state (active, bounced, opted_out) |
| lifecycle_state | TEXT | NOT NULL | Contact lifecycle state |
| funnel_membership | TEXT | NOT NULL | Which funnel this contact is in |
| email_open_count | INTEGER | NOT NULL | Total email opens tracked |
| email_click_count | INTEGER | NOT NULL | Total email clicks tracked |
| email_reply_count | INTEGER | NOT NULL | Total email replies tracked |
| current_bit_score | INTEGER | NOT NULL | DEPRECATED — BIT scoring retired |
| last_event_ts | TEXT | | Last engagement event timestamp |
| last_state_change_ts | TEXT | | Last state transition timestamp |
| source | TEXT | | Data source for this contact |
| created_at | TEXT | NOT NULL | Record creation timestamp |
| updated_at | TEXT | NOT NULL | Last modification timestamp |

---

### people_company_slot — CEO/CFO/HR slots (98,106 rows)
Three slots per company: CEO, CFO, HR (32,702 x 3). Slot is the constant, person filling it is the variable.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| slot_id | TEXT | PK, NOT NULL | Unique slot identifier |
| outreach_id | TEXT | NOT NULL | FK → outreach_outreach.outreach_id |
| company_unique_id | TEXT | NOT NULL | FK → cl.company_identity.company_unique_id |
| slot_type | TEXT | NOT NULL | Role type: CEO, CFO, or HR |
| person_unique_id | TEXT | | FK → people_people_master.unique_id (NULL if empty) |
| is_filled | INTEGER | | Whether slot has a person (0/1) |
| filled_at | TEXT | | When the slot was filled |
| confidence_score | REAL | | Confidence in the person-slot match (0.0–1.0) |
| source_system | TEXT | | Which system filled this slot (staging, blog, proxy, manual) |
| slot_phone | TEXT | | Direct phone number for this slot |
| slot_phone_source | TEXT | | Where the phone number came from |
| slot_phone_updated_at | TEXT | | When phone was last verified |
| created_at | TEXT | | Record creation timestamp |
| updated_at | TEXT | | Last modification timestamp |

---

### people_people_master — Person records (58,857 rows)
Individual contact records. Only people referenced by filled slots. Contains verified email + LinkedIn for outreach.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| unique_id | TEXT | PK, NOT NULL | Unique person identifier — FK from people_company_slot.person_unique_id |
| company_unique_id | TEXT | NOT NULL | FK → cl.company_identity.company_unique_id |
| company_slot_unique_id | TEXT | NOT NULL | FK → people_company_slot.slot_id |
| first_name | TEXT | NOT NULL | Person's first name |
| last_name | TEXT | NOT NULL | Person's last name |
| full_name | TEXT | | Computed: first_name + last_name |
| title | TEXT | | Job title (CEO, CFO, HR Director, etc.) |
| seniority | TEXT | | Seniority level (C-suite, VP, Director, Manager) |
| department | TEXT | | Department (Executive, Finance, HR, Operations) |
| email | TEXT | | Verified email address |
| email_verified | INTEGER | | Whether email is verified (0/1) |
| email_verification_source | TEXT | | Which service verified the email |
| email_verified_at | TEXT | | When email was verified |
| validation_status | TEXT | | Current validation state |
| last_verified_at | TEXT | NOT NULL | Last verification timestamp |
| work_phone_e164 | TEXT | | Work phone in E.164 format |
| personal_phone_e164 | TEXT | | Personal phone in E.164 format |
| linkedin_url | TEXT | | LinkedIn profile URL |
| twitter_url | TEXT | | Twitter/X profile URL |
| facebook_url | TEXT | | Facebook profile URL |
| bio | TEXT | | Professional bio |
| skills | TEXT | | Skills list (JSON) |
| education | TEXT | | Education history (JSON) |
| certifications | TEXT | | Professional certifications (JSON) |
| source_system | TEXT | NOT NULL | Which system created this record (staging, blog, proxy) |
| source_record_id | TEXT | | Original record ID from source system |
| promoted_from_intake_at | TEXT | NOT NULL | When promoted from intake_people_staging |
| promotion_audit_log_id | INTEGER | | Audit trail ID for promotion |
| is_decision_maker | INTEGER | | Whether this person is a benefits decision maker (0/1) |
| outreach_ready | INTEGER | | Whether person has verified contact method (0/1) |
| outreach_ready_at | TEXT | | When person became outreach-ready |
| message_key_scheduled | TEXT | | Scheduled message key for next outreach |
| last_enrichment_attempt | TEXT | | When enrichment was last attempted |
| created_at | TEXT | | Record creation timestamp |
| updated_at | TEXT | | Last modification timestamp |

---

### dol_form_5500 — Federal DOL filings (14,252 rows)
Form 5500 filings from EBSA. Uploaded once a year. Read-only reference.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| ack_id | TEXT | PK | EBSA acknowledgment ID — unique per filing |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| sponsor_dfe_ein | TEXT | NOT NULL | Employer EIN on the filing |
| sponsor_dfe_name | TEXT | | Legal company name from filing |
| plan_name | TEXT | | Benefits plan name |
| plan_number | TEXT | | Plan number |
| plan_eff_date | TEXT | | Plan effective date |
| form_year | TEXT | | Filing year |
| form_tax_prd | TEXT | | Tax period |
| spons_dfe_mail_us_city | TEXT | | Sponsor mailing city |
| spons_dfe_mail_us_state | TEXT | | Sponsor mailing state |
| spons_dfe_mail_us_zip | TEXT | | Sponsor mailing ZIP |
| tot_active_partcp_cnt | INTEGER | | Total active participants |
| tot_partcp_boy_cnt | INTEGER | | Total participants beginning of year |
| admin_name | TEXT | | Plan administrator name |
| admin_ein | TEXT | | Plan administrator EIN |
| type_plan_entity_cd | TEXT | | Plan entity type code |
| sch_a_attached_ind | TEXT | | Whether Schedule A is attached (Y/N) |
| num_sch_a_attached_cnt | INTEGER | | Number of Schedule A attachments |
| filing_status | TEXT | | Filing status |
| date_received | TEXT | | Date EBSA received the filing |
| funding_arrangement | TEXT | | Funding arrangement code |
| benefit_arrangement | TEXT | | Benefit arrangement code |
| all_data | TEXT | | Full filing as JSON blob |
| seeded_at | TEXT | NOT NULL | When this row was seeded to D1 |

---

### dol_schedule_a — Broker/insurance detail (9,538 rows)
Schedule A from Form 5500. Insurance broker commissions and fees.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INT | | Auto-increment row ID |
| ack_id | TEXT | | FK → dol_form_5500.ack_id |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| sponsor_dfe_ein | TEXT | | Employer EIN |
| form_year | TEXT | | Filing year |
| row_order | INT | | Row position within the filing |
| ins_broker_name | TEXT | | Insurance broker name |
| ins_broker_us_city | TEXT | | Broker city |
| ins_broker_us_state | TEXT | | Broker state |
| ins_broker_us_zip | TEXT | | Broker ZIP |
| ins_broker_comm_pd_amt | REAL | | Broker commissions paid ($) |
| ins_broker_fees_pd_amt | REAL | | Broker fees paid ($) |
| ins_broker_code | TEXT | | Broker type code |
| all_data | TEXT | | Full schedule as JSON blob |
| seeded_at | TEXT | | When seeded to D1 |

---

### dol_schedule_c — Service provider detail (18,246 rows)
Schedule C from Form 5500. Service provider compensation.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INT | | Auto-increment row ID |
| ack_id | TEXT | | FK → dol_form_5500.ack_id |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| sponsor_dfe_ein | TEXT | | Employer EIN |
| form_year | TEXT | | Filing year |
| row_order | INT | | Row position within the filing |
| provider_name | TEXT | | Service provider name |
| provider_ein | TEXT | | Service provider EIN |
| provider_us_city | TEXT | | Provider city |
| provider_us_state | TEXT | | Provider state |
| provider_srvc_codes | TEXT | | Service type codes |
| provider_relation | TEXT | | Relationship to plan |
| provider_direct_comp_amt | REAL | | Direct compensation amount ($) |
| provider_indirect_comp_amt | REAL | | Indirect compensation amount ($) |
| all_data | TEXT | | Full schedule as JSON blob |
| seeded_at | TEXT | | When seeded to D1 |

---

### dol_schedule_other — Other schedules (67,164 rows)
All other DOL schedules stored as JSON.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INT | | Auto-increment row ID |
| ack_id | TEXT | | FK → dol_form_5500.ack_id |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| sponsor_dfe_ein | TEXT | | Employer EIN |
| schedule_type | TEXT | | Which schedule (H, I, R, etc.) |
| form_year | TEXT | | Filing year |
| row_order | INT | | Row position |
| all_data | TEXT | | Full schedule as JSON blob |
| seeded_at | TEXT | | When seeded to D1 |

---

### coverage_service_agent — Service agents (3 rows)
The 3 active agents. Gate 0 anchors.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| service_agent_id | TEXT | | Unique agent identifier |
| agent_name | TEXT | | Full name (Dave Allan, Jeff Mussolino, David Vang) |
| agent_number | TEXT | | Agent code (SA-001, SA-002, SA-003) |
| first_name | TEXT | | First name |
| last_name | TEXT | | Last name |
| status | TEXT | | Active or inactive |
| created_at | TEXT | | Record creation timestamp |

---

### coverage_service_agent_coverage — Coverage zones (3 rows)
Each agent's coverage definition — anchor ZIP + radius. Active only.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| coverage_id | TEXT | | Unique coverage record identifier |
| service_agent_id | TEXT | | FK → coverage_service_agent.service_agent_id |
| anchor_zip | TEXT | | Center ZIP code for coverage area |
| radius_miles | REAL | | Coverage radius in miles (100) |
| status | TEXT | | Active or retired |
| created_by | TEXT | | Who created this coverage zone |
| created_at | TEXT | | Record creation timestamp |
| retired_at | TEXT | | When coverage was retired (NULL if active) |
| retired_by | TEXT | | Who retired this coverage zone |
| notes | TEXT | | Free-text notes |

---

### intake_people_staging — Pre-scraped contacts (24,727 rows)
Contacts already scraped and title-mapped, waiting to be promoted to people_people_master by Process 200.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INTEGER | PK | Auto-increment row ID |
| source_url_id | TEXT | | URL the contact was scraped from |
| company_unique_id | TEXT | NOT NULL | FK → cl.company_identity.company_unique_id |
| raw_name | TEXT | | Original scraped name |
| first_name | TEXT | | Parsed first name |
| last_name | TEXT | | Parsed last name |
| raw_title | TEXT | | Original scraped title |
| normalized_title | TEXT | | Cleaned/standardized title |
| mapped_slot_type | TEXT | | Which slot this maps to (CEO, CFO, HR) |
| linkedin_url | TEXT | | LinkedIn profile URL |
| email | TEXT | | Email address |
| confidence_score | REAL | | Confidence in the name/title extraction (0.0–1.0) |
| status | TEXT | | Processing state (pending, promoted, rejected) |
| created_at | TEXT | | Record creation timestamp |
| processed_at | TEXT | | When processed by Process 200 |

---

### enrichment_hunter_contact — Hunter.io verified contacts (175,632 rows)
Verified emails and people data from Hunter.io enrichment. The gold mine — 179K+ verified emails already in the database before any Startpage search.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INTEGER | PK | Hunter record ID |
| outreach_id | TEXT | NOT NULL | FK → outreach_outreach.outreach_id |
| company_unique_id | TEXT | | FK → cl.company_identity.company_unique_id |
| domain | TEXT | NOT NULL | Company domain |
| first_name | TEXT | | Contact first name |
| last_name | TEXT | | Contact last name |
| full_name | TEXT | | Computed full name |
| email | TEXT | | Verified email address |
| email_type | TEXT | | Personal vs generic |
| email_verified | INTEGER | | Hunter verification status (0/1) |
| confidence_score | INTEGER | | Hunter email confidence (0-100) |
| job_title | TEXT | | Job title from Hunter |
| title_normalized | TEXT | | Cleaned/standardized title |
| seniority_level | TEXT | | C-suite, VP, Director, Manager |
| department | TEXT | | Raw department |
| department_normalized | TEXT | | Normalized department |
| linkedin_url | TEXT | | LinkedIn profile URL |
| phone_number | TEXT | | Phone number if available |
| num_sources | INTEGER | | Number of sources confirming this email |
| is_decision_maker | INTEGER | | Whether contact is a decision maker (0/1) |
| outreach_priority | INTEGER | | Computed outreach priority |
| data_quality_score | REAL | | Composite data completeness score |
| source | TEXT | | Data source system |
| source_file | TEXT | | Original source file |
| created_at | TEXT | | Record creation timestamp |

---

### enrichment_hunter_company — Hunter.io email patterns (15,537 rows)
One row per company domain with a known email pattern. Use pattern + person name to generate email addresses for Process 201.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INTEGER | PK | Hunter company record ID |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| company_unique_id | TEXT | | FK → cl.company_identity.company_unique_id |
| domain | TEXT | NOT NULL | Company domain — primary identifier |
| organization | TEXT | | Company name from Hunter |
| email_pattern | TEXT | | Email pattern (e.g., {first}.{last}, {f}{last}) |
| industry | TEXT | | Industry from Hunter |
| industry_normalized | TEXT | | Cleaned industry category |
| company_type | TEXT | | Company ownership type |
| headcount | TEXT | | Employee count range string |
| headcount_min | INTEGER | | Min employee count |
| headcount_max | INTEGER | | Max employee count |
| country | TEXT | | Country code |
| state | TEXT | | State/province |
| city | TEXT | | City |
| postal_code | TEXT | | ZIP code |
| street | TEXT | | Street address |
| location_full | TEXT | | Full address string |
| data_quality_score | REAL | | Composite data completeness score |
| source | TEXT | | Data source system |
| enriched_at | TEXT | | When Hunter data was fetched |
| created_at | TEXT | | Record creation timestamp |
| updated_at | TEXT | | Last update timestamp |

---

### vendor_people — Vendor-enriched contacts (175,632 rows)
Enriched contacts from the vendor pipeline. Overlaps Hunter data but includes `mapped_slot_type` for direct slot matching and `backfill_source` for provenance.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| vendor_row_id | INTEGER | PK | Vendor pipeline row ID |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| company_unique_id | TEXT | | FK → cl.company_identity.company_unique_id |
| domain | TEXT | | Company domain |
| first_name | TEXT | | Contact first name |
| last_name | TEXT | | Contact last name |
| full_name | TEXT | | Computed full name |
| email | TEXT | | Email address |
| email_type | TEXT | | Personal vs generic |
| email_verified | INTEGER | | Verification status (0/1) |
| confidence_score | REAL | | Confidence in email accuracy |
| job_title | TEXT | | Job title from source |
| title_normalized | TEXT | | Cleaned/standardized title |
| seniority_level | TEXT | | C-suite, VP, Director, Manager |
| department | TEXT | | Raw department |
| department_normalized | TEXT | | Normalized department |
| mapped_slot_type | TEXT | | Which slot this maps to (CEO, CFO, HR) |
| linkedin_url | TEXT | | LinkedIn profile URL |
| phone_number | TEXT | | Phone number |
| work_phone | TEXT | | Work phone |
| personal_phone | TEXT | | Personal phone |
| num_sources | INTEGER | | Number of confirming sources |
| is_decision_maker | INTEGER | | Decision maker flag (0/1) |
| company_name | TEXT | | Company name |
| city | TEXT | | Contact city |
| state | TEXT | | Contact state |
| country | TEXT | | Contact country |
| source_system | TEXT | | Which system provided this data |
| backfill_source | TEXT | | Backfill provenance |
| enriched_by | TEXT | | Which enrichment service |
| data_quality_score | REAL | | Composite completeness score |
| source_table | TEXT | | Original Neon table |
| created_at | TEXT | | Record creation timestamp |
| updated_at | TEXT | | Last update timestamp |

---

### vendor_ct — Vendor-enriched company data (18,683 rows)
Company-level enrichment from vendors. Key value: email patterns with confidence scores, company phone, LinkedIn URL, descriptions.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| vendor_row_id | INTEGER | PK | Vendor pipeline row ID |
| outreach_id | TEXT | | FK → outreach_outreach.outreach_id |
| company_unique_id | TEXT | | FK → cl.company_identity.company_unique_id |
| domain | TEXT | | Company domain |
| company_name | TEXT | | Company name |
| email_pattern | TEXT | | Email pattern (e.g., {first}.{last}) |
| email_pattern_confidence | INTEGER | | Pattern confidence (0-100) |
| email_pattern_source | TEXT | | Where pattern came from |
| email_pattern_verified_at | TEXT | | When pattern was verified |
| company_phone | TEXT | | Main company phone |
| company_type | TEXT | | Company type |
| employee_count | INTEGER | | Employee headcount |
| industry | TEXT | | Industry classification |
| industry_normalized | TEXT | | Normalized industry |
| description | TEXT | | Company description |
| city | TEXT | | Company city |
| state | TEXT | | Company state |
| country | TEXT | | Country |
| postal_code | TEXT | | ZIP code |
| linkedin_url | TEXT | | Company LinkedIn URL |
| facebook_url | TEXT | | Company Facebook URL |
| twitter_url | TEXT | | Company Twitter/X URL |
| ein | TEXT | | Employer Identification Number |
| duns | TEXT | | DUNS number |
| source_system | TEXT | | Data source system |
| enriched_by | TEXT | | Which enrichment service |
| data_quality_score | REAL | | Composite completeness score |
| enriched_at | TEXT | | When enrichment occurred |
| source_table | TEXT | | Original Neon table |
| created_at | TEXT | | Record creation timestamp |
| updated_at | TEXT | | Last update timestamp |

---

### Join Chain

```
coverage_service_agent.service_agent_id
  → coverage_service_agent_coverage.service_agent_id (agent → coverage zones)
    → reference.us_zip_codes [Neon view: haversine expansion]
      → outreach_company_target.postal_code (GATE 0 — is this company in range?)
        → outreach_outreach.outreach_id (SPINE — universal join key)
          → cl.company_identity.outreach_id (tie back to sovereign_id)
          → outreach_company_target.outreach_id (CT sub-hub)
          → outreach_dol.outreach_id (DOL sub-hub)
            → dol_form_5500.outreach_id (filing detail)
              → dol_schedule_a.ack_id
              → dol_schedule_c.ack_id
              → dol_schedule_other.ack_id
          → outreach_blog.outreach_id (Blog sub-hub)
          → outreach_people.outreach_id (People contacts — DEPRECATED)
          → enrichment_hunter_contact.outreach_id (Hunter verified emails)
          → enrichment_hunter_company.outreach_id (Hunter email patterns)
          → vendor_people.outreach_id (Vendor-enriched contacts)
          → vendor_ct.outreach_id (Vendor-enriched company data)
          → people_company_slot.outreach_id (3 per company: CEO, CFO, HR)
            → people_people_master.unique_id (via person_unique_id)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Query Neon during WORK phase | SEED only. After SEED, all reads from D1. |
| Write to Neon | Neon is vault. SEED is Neon→D1, never D1→Neon (that's PUSH). |
| Skip the coverage filter | Every company in D1 must be inside an agent's coverage zone. |
| Direct cross-sub-hub joins in D1 | Route through outreach_id (the spine). |
| INSERT without OR REPLACE | SEED is idempotent. Re-running must not create duplicates. |

### Query Routing

| Question | Source | Table | Column |
|----------|--------|-------|--------|
| Which agents exist? | D1 outreach | coverage_service_agent | agent_name, status |
| Which ZIPs does an agent cover? | Neon only (view) | coverage.v_service_agent_coverage_zips | zip |
| Is this company in an agent's zone? | D1 outreach | outreach_company_target | service_agents IS NOT NULL |
| How many companies per agent? | D1 outreach | outreach_company_target | GROUP BY service_agents |
| What's the slot fill rate? | D1 outreach | people_company_slot | WHERE is_filled = 1 |
| What DOL filings does a company have? | D1 outreach | dol_form_5500 | WHERE outreach_id = ? |
| Does this company have a team page? | D1 outreach | outreach_blog | about_url IS NOT NULL |
| What verified emails exist for a company? | D1 outreach | enrichment_hunter_contact | WHERE outreach_id = ? AND email_verified = 1 |
| What's the email pattern for a domain? | D1 outreach | enrichment_hunter_company | WHERE domain = ? |
| What vendor-enriched contacts exist? | D1 outreach | vendor_people | WHERE outreach_id = ? |
| What vendor email pattern + confidence? | D1 outreach | vendor_ct | WHERE outreach_id = ? |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)
- Agent + anchor ZIP + radius = the gate. Everything flows from this.
- 3 slot types per company: CEO, CFO, HR
- outreach_id is the universal join key across all sub-hubs
- Footprint per company = CT + DOL + Blog + People (sub-hubs are extensible)
- D1 table names: Neon schema.table → D1 schema_table (underscore flattening)
- INSERT OR REPLACE for idempotent SEED
- D1.batch() for bulk writes (max ~100 statements per batch)
- DOL data uploaded once a year from EBSA — read-only reference until next upload
- Blog first pass maps everything, after that quick update for changes only

### Variables (fill — changes every run)
- Number of companies passing Gate 0 (~32K currently, changes if agents/coverage change)
- Slot fill rates (depends on Neon people data quality)
- Number of DOL filings (grows with each yearly upload)
- Total rows per table (changes with each SEED run)
- Which sub-hubs exist (CT, DOL, Blog, People today — workers comp or others tomorrow)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Hyperdrive connection fails | HALT — check Neon credentials, Hyperdrive binding |
| D1 write returns error on >10% of batch | HALT — check D1 size limits, table schema |
| Post-SEED join audit shows <95% match | HALT — re-run failing step, investigate data gap |
| Agent coverage returns 0 ZIPs | HALT — check coverage.service_agent_coverage table |
| Company count drops >20% from prior SEED | HALT — something changed in Neon, investigate before overwriting |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Neon PostgreSQL vault | All source data — CL, outreach, people, DOL, coverage | DONE |
| Hyperdrive binding on lcs-hub | HD_NEON configured in wrangler.toml | DONE |
| coverage.v_service_agent_coverage_zips | Neon view (haversine) — must exist for Gate 0 filter | DONE |
| reference.us_zip_codes | 41,553 ZIP codes with lat/lon for haversine | DONE |
| Active service agents | Must exist in coverage.service_agent with status='active' | DONE |
| DOL data | Yearly bulk load from EBSA website into Neon | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 100 (LCS Pipeline) | ALL of the above — compiles CID from full footprint |
| Process 200 (People Worker) | Filled slots, people records, company target, blog about_urls, hunter contacts (pre-fill), vendor people (mapped_slot_type) |
| Process 201 (Email Discovery) | Hunter email patterns, vendor CT email patterns — try pattern first before searching |
| Process 300 (Blog Worker) | Blog records, company target, domains |
| Process 400 (DOL Views) | DOL filing detail (form_5500, schedules) |
| Process 500 (Talent Flow) | People records with LinkedIn URLs |
| ALL SVG processes | If SEED didn't run, nothing works |

---

## 9. SMOKE TEST

```
1. GET lcs-hub.svg-outreach.workers.dev/health → expected: status ok
2. POST /seed/clean?table=company_target&limit=5000&offset=0 → expected: seeded > 0, errors = 0 (tables: all, company_target, outreach, cl_identity, blog, dol, slots, people, hunter_contacts, hunter_patterns, vendor_people, vendor_ct)
3. wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_outreach" → expected: 32,702
4. wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_company_target WHERE service_agents IS NOT NULL" → expected: 32,702
5. wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM people_company_slot" → expected: 98,106
6. Join integrity: SELECT COUNT(*) FROM people_company_slot cs JOIN people_people_master pm ON cs.person_unique_id = pm.unique_id WHERE cs.is_filled = 1 → expected: 100% (0 orphans)
7. Slot fill rates: SELECT slot_type, ROUND(SUM(CASE WHEN is_filled=1 THEN 1.0 ELSE 0 END)/COUNT(*)*100,1) as pct FROM people_company_slot GROUP BY slot_type → expected: CEO ~63.4%, CFO ~58.5%, HR ~58.4%
8. Hunter contacts: SELECT COUNT(*) FROM enrichment_hunter_contact → expected: 175,632
9. Hunter patterns: SELECT COUNT(*) FROM enrichment_hunter_company → expected: 15,537
10. Vendor people: SELECT COUNT(*) FROM vendor_people → expected: 175,632
11. Vendor CT: SELECT COUNT(*) FROM vendor_ct → expected: 18,683
12. Hunter join: SELECT COUNT(DISTINCT hc.outreach_id) FROM enrichment_hunter_contact hc JOIN outreach_outreach oo ON hc.outreach_id = oo.outreach_id → expected: matches outreach coverage
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do all D1 tables exist with data? (CT, DOL, Blog, People, Coverage)
2. **Flow:** Does outreach_id join correctly from spine through every sub-hub table?
3. **Change:** Did the SEED copy Neon data to D1 correctly (schema.table → schema_table)?

---

## 10. ANALYTICS — The Dyno Sheet (Bedrock §2 + §5)

### Process Metrics

| Metric | Unit | Baseline (2026-04-01) | Target | Tolerance |
|--------|------|----------------------|--------|-----------|
| Companies seeded | count | 32,702 | 32,702 | ±5% (drop >20% = HALT) |
| CT rows | count | 32,702 | = companies | 100% match |
| DOL summary rows | count | 27,464 | ≥ companies with filing | correct (not all have filings) |
| Blog rows | count | 32,702 | = companies (1:1 clean) | 100% match |
| Slot rows | count | 98,106 | 32,702 × 3 | 100% match |
| People master rows | count | 58,857 | filled slots only | ±10% |
| CEO fill rate | % | 63.4% | ≥63.4% | must not drop |
| CFO fill rate | % | 58.5% | ≥58.5% | must not drop |
| HR fill rate | % | 58.4% | ≥58.4% | must not drop |
| Slot→person join integrity | % | 100% (0 orphans) | 100% | <99% = HALT |
| Agent assignment coverage | % | 100% (32,702/32,702) | 100% | <99% = HALT |
| Hunter contact rows | count | 175,632 | all with email for coverage companies | must match Neon |
| Hunter pattern rows | count | 15,537 | all domains with known pattern | must match Neon |
| Vendor people rows | count | 175,632 | all vendor-enriched contacts | must match Neon |
| Vendor CT rows | count | 18,683 | all vendor-enriched companies | must match Neon |
| SEED errors | count | 0 | 0 | >10% of batch = HALT |
| DOL filing detail rows | count | 14,252 | stable | ±10% |

### Tool Scorecard

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| 16-fetcher | Hyperdrive to Neon | 100% | $0 (free) | 0% | ~2s/batch | 2026-03-26 |
| 11-structured-data | CF D1 batch writes | 100% | $0 (free) | 0% | ~100ms/batch | 2026-03-26 |

### Sigma Tracking

| Metric | Run 1 (2026-03-25) | Run 2 (2026-03-26) | Run 3 (2026-04-01) | Trend | Action |
|--------|-------------------|-------------------|-------------------|-------|--------|
| Slot→person join | 5.2% (broken) | 99.7% (fixed) | 100% (0 orphans) | TIGHTENING | Locked |
| Companies seeded | 32,704 | 32,704 | 32,702 | TIGHTENING | Correct — seed_views scoped |
| CEO fill | — | 54.7% | 63.4% | TIGHTENING | vendor.blog data merged |
| CFO fill | — | 50.2% | 58.5% | TIGHTENING | vendor.blog data merged |
| HR fill | — | 43.2% | 58.4% | TIGHTENING | vendor.blog data merged |

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs |
| OPERATE | REPAIR | Any metric outside tolerance |
| REPAIR | OPERATE | Fix applied + metric back within tolerance |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same metric fails 3 times → AD |

---

## 11. LOGBOOK

### 2026-04-01 — Hunter + Vendor SEED expansion

**ORBT:** OPERATE
**Trigger:** Audit revealed 4 Neon sub-hubs NOT in D1 — Hunter contacts (175K verified emails), Hunter patterns (15K email patterns), Vendor people (175K contacts), Vendor CT (18K company records)
**Records processed:** 175,632 + 15,537 + 175,632 + 18,683 = 385,484 new rows
**Errors:** 0
**Tools used:** Hyperdrive (HD_NEON), D1.batch(), seed_views (Neon), `/seed/clean` endpoint, psql for Neon view creation
**Result:**
- Fix #1: Created `seed_views.v_agent_hunter_patterns` in Neon — previous attempt failed on non-existent `num_sources` column in enrichment.hunter_company (correct column: `email_pattern`)
- Created D1 migration 003_hunter_vendor_tables.sql — 4 new tables with indexes
- Added 4 new table handlers to `seedClean()` in seed.ts: hunter_contacts, hunter_patterns, vendor_people, vendor_ct
- All 4 tables seeded and verified: counts match Neon exactly
- D1 now has 15 data tables (up from 11) covering ALL known sub-hubs in Neon
**Learnings:**
- Observe before you build — we had 179K verified emails sitting in Neon that were never brought to D1
- Email patterns from Hunter (15,537 domains) + vendor (18,683 domains) = Gate 0 for Process 201 (email discovery). Try pattern first, only search if no pattern exists.
- vendor_people has `mapped_slot_type` — can directly fill slots without title parsing
**ORBT after:** OPERATE

### 2026-04-01 — Clean SEED audit

**ORBT:** OPERATE
**Trigger:** Manual — full audit of D1 vs Neon after seed_views created
**Records processed:** 32,702 companies, 98,106 slots, 58,857 people, 27,464 DOL, 32,702 blog
**Errors:** 0 after fixes
**Tools used:** Hyperdrive (HD_NEON), D1.batch(), seed_views (Neon), `/seed/clean` endpoint
**Result:**
- Fix #1: 53 orphan slots (CTB-path IDs from intake_promotion/wv_hr_pipeline) — deleted in Neon, clean in D1
- Fix #2: D1 had full Neon universe (117K CL identity, 358K slots) — fixed with seed_views scoping to 32,702
- Fix #3: Blog was using `outreach.blog` only, now uses `vendor.blog` (290K crawl data) merged via materialized view
- Fill rates jumped: CEO 54.7% → 63.4%, CFO 50.2% → 58.5%, HR 43.2% → 58.4%
- Slot→person join integrity: 100% (0 orphans after fix)
- Agent model updated: agents define geography, companies can have multiple agents (29,775 single + 2,927 dual)
**Learnings:**
- seed_views are the gate — SEED code is a dumb copy, no filtering logic
- Materialized views need REFRESH after data changes (v_agent_blog, v_agent_fill_rates)
- Old outreach_people table deprecated — slot+people_master model is the standard
**ORBT after:** OPERATE

### 2026-03-26 — Full SEED + fixes

**ORBT:** BUILD → OPERATE
**Trigger:** Manual — D1 was incomplete, slot→person 94.8% orphan rate
**Records processed:** 358K slots, 160K people, 171K DOL, 32K companies
**Errors:** 0 across all batches
**Tools used:** Hyperdrive (HD_NEON), D1.batch(), wrangler CLI for verification
**Result:**
- Fix #1: people_people_master re-SEED (19K records, 99.7% match)
- Fix #2: missing slots created (54K, 100% coverage)
- Fix #3: agent assignment added to outreach_company_target (32,702 assigned)
- Fix #4: D1 title matching (2,510 filled)
- Fix #5: full Neon slot+people SEED (69 batches, 342K slots, ~175K people)
**Learnings:**
- Neon slots already have correct fill states — just copy table by table
- D1.batch() required for bulk operations (CF Worker subrequest limits, max ~100 per batch)
- Coverage zone join is expensive — skip it by using outreach_ids already in D1
- INSERT OR REPLACE makes SEED idempotent — safe to re-run
**ORBT after:** OPERATE

### 2026-03-25 — Initial D1 SEED (partial)

**ORBT:** BUILD
**Trigger:** Manual — building D1 workspace
**Records processed:** 32K companies, 43K slots, 32K people, 171K DOL
**Errors:** Slot→person orphan rate 94.8% (SEED brought wrong subset of people)
**Result:** D1 populated but incomplete. Led to 2026-03-26 fixes.
**ORBT after:** BUILD (incomplete)

---

## 12. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-25 | 94.8% orphan on slot→person join | SEED brought slots but not matching people records | Re-SEED people_master for all referenced person_unique_ids | 1 |
| 2 | 2026-03-25 | 18,301 companies had no slots | Original SEED only brought slots for companies that had them in Neon | Create CEO/CFO/HR slots for all companies, then re-SEED from Neon | 1 |
| 3 | 2026-03-25 | No agent assignment on companies | Coverage filter applied during SEED but result not stored | Added service_agent_id/name/number columns to outreach_company_target | 1 |
| 4 | 2026-03-26 | CF Worker subrequest limit on bulk writes | Individual INSERT statements instead of D1.batch() | Use D1.batch() with max ~100 statements per batch | 1 |
| 5 | 2026-03-26 | Coverage zone join too slow for full people SEED | Query joined against haversine view for 182K people rows | Skip coverage join — use outreach_ids already in D1 to filter | 1 |
| 6 | 2026-04-01 | 53 orphan slots in Neon (CTB-path IDs from intake_promotion/wv_hr_pipeline) | Old pipeline created slots with non-standard IDs | Deleted orphan rows in Neon; clean SEED to D1 | 1 |
| 7 | 2026-04-01 | D1 had full Neon universe (117K CL identity, 358K slots) instead of agent-scoped | No seed_views — SEED pulled everything | Created seed_views in Neon, re-SEED with scoped views | 1 |
| 8 | 2026-04-01 | Blog was using outreach.blog only (49K), missing vendor.blog crawl data (290K) | SEED only joined outreach.blog, not vendor.blog | Created materialized view v_agent_blog merging both sources | 1 |

---

## 13. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-04-01 | Clean SEED audit — seed_views, orphan fix, blog merge, row count correction | none (LBB) |
| 2026-03-25 | D1 schema introspection, SEED gap analysis | schema/d1-outreach-ops-full-schema-2026-03-25 |
| 2026-03-25 | Architectural corrections documented | session/2026-03-25-process-200-corrections |
| 2026-03-26 | Full SEED fixes (people, slots, agents) | ops/2026-03-26-seed-fix-complete |
| 2026-03-26 | Data flow diagram documented | decisions/2026-03-26-data-flow-neon-to-d1 |
| 2026-03-26 | Full Neon slot+people SEED complete | ops/2026-03-26-full-neon-seed-complete |
| 2026-03-29 | Process doc v2 rewritten from Dave's walkthrough | none |
| 2026-03-30 | AI-ready column inventory added from live D1 | none |

---

## SEED ENDPOINTS (on lcs-hub worker)

| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/seed/clean?table={name}&limit=5000&offset=0` | POST | Clean SEED from Neon seed_views — table by table (company_target, outreach, cl_identity, blog, dol, slots, people) |
| `/seed/full-people?limit=5000&offset=0` | POST | Pull slots + people from Neon, paginated (legacy) |
| `/seed/fix-slots?limit=3000` | POST | Create missing CEO/CFO/HR slots (D1 only) |
| `/seed/fix-agents` | POST | Assign agents to companies via coverage view |
| `/seed/fix-people` | POST | Pull missing people_master records from Neon |
| `/seed/fix-match?limit=1000` | POST | Match existing D1 people to empty slots by title |
| `/seed/batch?limit=100&offset=0` | POST | Original DOL-focused batch SEED |
| `/seed/dol-to-d1/{ein}` | POST | SEED DOL for one EIN |
| `/seed/global-zips` | POST | SEED ZIP codes to imo-d1-global |

---

## HOW TO RE-RUN THE FULL SEED

```bash
# Clean SEED from Neon seed_views — table by table
# Each table reads from its corresponding seed_views view (the gate)
for TABLE in company_target outreach cl_identity blog dol slots people; do
  for OFFSET in $(seq 0 5000 100000); do
    RESULT=$(curl -s -X POST "https://lcs-hub.svg-outreach.workers.dev/seed/clean?table=$TABLE&limit=5000&offset=$OFFSET")
    echo "$TABLE offset=$OFFSET: $RESULT"
    # Stop when seeded=0
  done
done

# Post-SEED audit — verify counts match seed_views
wrangler d1 execute svg-d1-outreach-ops --remote --command "
  SELECT 'outreach_outreach' as tbl, COUNT(*) as rows FROM outreach_outreach
  UNION ALL SELECT 'outreach_company_target', COUNT(*) FROM outreach_company_target
  UNION ALL SELECT 'people_company_slot', COUNT(*) FROM people_company_slot
  UNION ALL SELECT 'people_people_master', COUNT(*) FROM people_people_master
  UNION ALL SELECT 'outreach_blog', COUNT(*) FROM outreach_blog
  UNION ALL SELECT 'outreach_dol', COUNT(*) FROM outreach_dol"

# Expected: outreach_outreach=32702, company_target=32702, slots=98106, people=58857, blog=32702, dol=27464

# Slot fill rates
wrangler d1 execute svg-d1-outreach-ops --remote --command "
  SELECT slot_type,
    COUNT(*) as total,
    SUM(CASE WHEN is_filled=1 THEN 1 ELSE 0 END) as filled,
    ROUND(SUM(CASE WHEN is_filled=1 THEN 1.0 ELSE 0 END)/COUNT(*)*100,1) as pct
  FROM people_company_slot
  GROUP BY slot_type ORDER BY slot_type"
# Expected: CEO 63.4%, CFO 58.5%, HR 58.4%
```

---

## SERVICE AGENTS (Gate 0)

Agents define geography, not company ownership. Companies in overlapping coverage zones get multiple agents in the `service_agents` column. Agent count distribution: **29,775 single-agent + 2,927 dual-agent = 32,702 total**.

| Agent | Number | Anchor ZIP | Radius | Region |
|-------|--------|-----------|--------|--------|
| Dave Allan | SA-001 | 26739 | 100mi | WV |
| Jeff Mussolino | SA-002 | 21742 | 100mi | MD |
| David Vang | SA-003 | 28461 | 100mi | NC |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-04-01 |
| Version | 4.0.0 |
| Template Version | 3.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| Blueprint Repo | barton-outreach-core |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md v1.1.2 |
| Data Flow | factory/outreach/DATA_FLOW.md |

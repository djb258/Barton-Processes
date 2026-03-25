# D1 Schema Reference — Process 200: People Worker
# Source: Live D1 introspection via wrangler CLI
# Date: 2026-03-25
# Authority: Actual deployed D1 databases (not docs, not guesses)

---

## D1: svg-d1-outreach-ops (73a285b8) — PRIMARY WORKSPACE

### outreach_company_target (32,704 rows)
The targeting record per company. Has city/state/industry/employees but NO company name.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| target_id | TEXT | NOT NULL | PK |
| company_unique_id | TEXT | yes | |
| outreach_status | TEXT | NOT NULL | |
| bit_score_snapshot | INTEGER | yes | |
| first_targeted_at | TEXT | yes | |
| last_targeted_at | TEXT | yes | |
| sequence_count | INTEGER | NOT NULL | |
| active_sequence_id | TEXT | yes | |
| source | TEXT | yes | |
| created_at | TEXT | NOT NULL | |
| updated_at | TEXT | NOT NULL | |
| outreach_id | TEXT | yes | |
| email_method | TEXT | yes | |
| method_type | TEXT | yes | |
| confidence_score | REAL | yes | |
| execution_status | TEXT | yes | |
| imo_completed_at | TEXT | yes | |
| is_catchall | INTEGER | yes | |
| industry | TEXT | yes | |
| employees | INTEGER | yes | |
| country | TEXT | yes | |
| state | TEXT | yes | |
| city | TEXT | yes | |
| postal_code | TEXT | yes | |
| data_year | INTEGER | yes | |
| postal_code_source | TEXT | yes | |
| postal_code_updated_at | TEXT | yes | |

**Key columns for Process 200:** `outreach_id` (join key), `city`, `state`, `postal_code`, `email_method`, `industry`, `employees`

---

### outreach_outreach (32,704 rows)
The spine record. Has domain and EIN.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| outreach_id | TEXT | NOT NULL | PK |
| sovereign_id | TEXT | NOT NULL | |
| created_at | TEXT | NOT NULL | |
| updated_at | TEXT | NOT NULL | |
| domain | TEXT | yes | |
| ein | TEXT | yes | |
| has_appointment | INTEGER | yes | |

**Key columns for Process 200:** `outreach_id` (join key), `domain` (company website), `ein`, `sovereign_id` (links to CL)

---

### people_company_slot (43,209 rows)
CEO/CFO/HR slots per company. The core working table for Process 200.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| slot_id | TEXT | NOT NULL | PK |
| outreach_id | TEXT | NOT NULL | |
| company_unique_id | TEXT | NOT NULL | |
| slot_type | TEXT | NOT NULL | |
| person_unique_id | TEXT | yes | |
| is_filled | INTEGER | yes | |
| filled_at | TEXT | yes | |
| confidence_score | REAL | yes | |
| source_system | TEXT | yes | |
| created_at | TEXT | yes | |
| updated_at | TEXT | yes | |
| slot_phone | TEXT | yes | |
| slot_phone_source | TEXT | yes | |
| slot_phone_updated_at | TEXT | yes | |

**Key columns for Process 200:** `slot_id`, `outreach_id`, `slot_type`, `person_unique_id`, `is_filled`, `source_system`
**Join:** `person_unique_id` → `people_people_master.unique_id`

---

### people_people_master (32,106 rows)
Full contact records. Names, emails, LinkedIn URLs, verification status.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| unique_id | TEXT | NOT NULL | PK |
| company_unique_id | TEXT | NOT NULL | |
| company_slot_unique_id | TEXT | NOT NULL | |
| first_name | TEXT | NOT NULL | |
| last_name | TEXT | NOT NULL | |
| full_name | TEXT | yes | |
| title | TEXT | yes | |
| seniority | TEXT | yes | |
| department | TEXT | yes | |
| email | TEXT | yes | |
| work_phone_e164 | TEXT | yes | |
| personal_phone_e164 | TEXT | yes | |
| linkedin_url | TEXT | yes | |
| twitter_url | TEXT | yes | |
| facebook_url | TEXT | yes | |
| bio | TEXT | yes | |
| skills | TEXT | yes | |
| education | TEXT | yes | |
| certifications | TEXT | yes | |
| source_system | TEXT | NOT NULL | |
| source_record_id | TEXT | yes | |
| promoted_from_intake_at | TEXT | NOT NULL | |
| promotion_audit_log_id | INTEGER | yes | |
| created_at | TEXT | yes | |
| updated_at | TEXT | yes | |
| email_verified | INTEGER | yes | |
| message_key_scheduled | TEXT | yes | |
| email_verification_source | TEXT | yes | |
| email_verified_at | TEXT | yes | |
| validation_status | TEXT | yes | |
| last_verified_at | TEXT | NOT NULL | |
| last_enrichment_attempt | TEXT | yes | |
| is_decision_maker | INTEGER | yes | |
| outreach_ready | INTEGER | yes | |
| outreach_ready_at | TEXT | yes | |

**Key columns for Process 200:** `unique_id` (PK), `linkedin_url` (for movement checks), `first_name`, `last_name`, `full_name`, `title`, `email`, `email_verified`, `outreach_ready`, `last_enrichment_attempt`, `source_system`

---

### outreach_people (109,443 rows)
Delivery contacts with engagement tracking. Has email + verification but NO names/titles.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| person_id | TEXT | NOT NULL | |
| target_id | TEXT | NOT NULL | |
| company_unique_id | TEXT | NOT NULL | |
| slot_type | TEXT | yes | |
| email | TEXT | NOT NULL | |
| email_verified | INTEGER | NOT NULL | |
| email_verified_at | TEXT | yes | |
| contact_status | TEXT | NOT NULL | |
| lifecycle_state | TEXT | NOT NULL | |
| funnel_membership | TEXT | NOT NULL | |
| email_open_count | INTEGER | NOT NULL | |
| email_click_count | INTEGER | NOT NULL | |
| email_reply_count | INTEGER | NOT NULL | |
| current_bit_score | INTEGER | NOT NULL | |
| last_event_ts | TEXT | yes | |
| last_state_change_ts | TEXT | yes | |
| source | TEXT | yes | |
| created_at | TEXT | NOT NULL | |
| updated_at | TEXT | NOT NULL | |
| outreach_id | TEXT | yes | |

**Key columns for Process 200:** `outreach_id`, `email`, `email_verified`, `slot_type`, `contact_status`

---

### outreach_blog (49,062 rows)
Web content intelligence. Has source URLs and about pages.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| blog_id | TEXT | NOT NULL | |
| outreach_id | TEXT | NOT NULL | |
| context_summary | TEXT | yes | |
| source_type | TEXT | yes | |
| source_url | TEXT | yes | |
| context_timestamp | TEXT | yes | |
| created_at | TEXT | yes | |
| source_type_enum | TEXT | yes | |
| about_url | TEXT | yes | |
| news_url | TEXT | yes | |
| extraction_method | TEXT | yes | |
| last_extracted_at | TEXT | yes | |
| updated_at | TEXT | yes | |

**Key columns for Process 200:** `outreach_id`, `source_url` (company website pages), `about_url` (team/about pages often list executives)

---

### outreach_dol (36,247 rows)
DOL filing summary. Carrier, broker, renewal timing.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| dol_id | TEXT | NOT NULL | |
| outreach_id | TEXT | NOT NULL | |
| ein | TEXT | yes | |
| filing_present | INTEGER | yes | |
| funding_type | TEXT | yes | |
| broker_or_advisor | TEXT | yes | |
| carrier | TEXT | yes | |
| created_at | TEXT | yes | |
| updated_at | TEXT | yes | |
| url_enrichment_data | TEXT | yes | |
| renewal_month | INTEGER | yes | |
| outreach_start_month | INTEGER | yes | |

**Key columns for Process 200:** `outreach_id`, `filing_present` (DOL-linked = higher trust), `ein`

---

### dol_form_5500 (14,252 rows)
Full DOL filings. Has sponsor name (= company legal name), city, state from federal records.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| ack_id | TEXT | | PK |
| outreach_id | TEXT | yes | |
| sponsor_dfe_ein | TEXT | NOT NULL | |
| sponsor_dfe_name | TEXT | yes | |
| plan_name | TEXT | yes | |
| plan_number | TEXT | yes | |
| plan_eff_date | TEXT | yes | |
| form_year | TEXT | yes | |
| form_tax_prd | TEXT | yes | |
| spons_dfe_mail_us_city | TEXT | yes | |
| spons_dfe_mail_us_state | TEXT | yes | |
| spons_dfe_mail_us_zip | TEXT | yes | |
| tot_active_partcp_cnt | INTEGER | yes | |
| tot_partcp_boy_cnt | INTEGER | yes | |
| admin_name | TEXT | yes | |
| admin_ein | TEXT | yes | |
| type_plan_entity_cd | TEXT | yes | |
| sch_a_attached_ind | TEXT | yes | |
| num_sch_a_attached_cnt | INTEGER | yes | |
| filing_status | TEXT | yes | |
| date_received | TEXT | yes | |
| funding_arrangement | TEXT | yes | |
| benefit_arrangement | TEXT | yes | |
| all_data | TEXT | yes | |
| seeded_at | TEXT | NOT NULL | |

**Key columns for Process 200:** `sponsor_dfe_name` (legal company name from federal filing), `outreach_id`, `spons_dfe_mail_us_city`, `spons_dfe_mail_us_state`

---

### outreach_appointments (487 rows)
Past appointments. Has company name and contact details.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| appointment_id | TEXT | NOT NULL | |
| outreach_id | TEXT | yes | |
| domain | TEXT | yes | |
| prospect_keycode_id | INTEGER | yes | |
| appt_number | TEXT | yes | |
| appt_date | TEXT | yes | |
| contact_first_name | TEXT | yes | |
| contact_last_name | TEXT | yes | |
| contact_title | TEXT | yes | |
| contact_email | TEXT | yes | |
| contact_phone | TEXT | yes | |
| company_name | TEXT | NOT NULL | |
| address_1 | TEXT | yes | |
| address_2 | TEXT | yes | |
| city | TEXT | yes | |
| state | TEXT | yes | |
| zip | TEXT | yes | |
| county | TEXT | yes | |
| notes | TEXT | yes | |
| source_file | TEXT | yes | |
| created_at | TEXT | yes | |
| updated_at | TEXT | yes | |

---

### people_title_slot_mapping (43 rows)
Title pattern → slot type mapping. Deterministic slot assignment.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| id | INTEGER | | PK |
| title_pattern | TEXT | NOT NULL | |
| slot_type | TEXT | NOT NULL | |
| priority | INTEGER | yes | |
| created_at | TEXT | yes | |

---

### intake_people_staging (24,727 rows)
Staging table for people discovered via web scraping. Has LinkedIn URLs and names.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| id | INTEGER | | PK |
| source_url_id | TEXT | yes | |
| company_unique_id | TEXT | NOT NULL | |
| raw_name | TEXT | yes | |
| first_name | TEXT | yes | |
| last_name | TEXT | yes | |
| raw_title | TEXT | yes | |
| normalized_title | TEXT | yes | |
| mapped_slot_type | TEXT | yes | |
| linkedin_url | TEXT | yes | |
| email | TEXT | yes | |
| confidence_score | REAL | yes | |
| status | TEXT | yes | |
| created_at | TEXT | yes | |
| processed_at | TEXT | yes | |

**Key columns for Process 200:** This IS the staging table for enrichment results. 24,727 records already staged.

---

### coverage_service_agent (9 rows)
Service agents and their identities.

| Column | Type | Nullable |
|--------|------|----------|
| service_agent_id | TEXT | yes |
| agent_name | TEXT | yes |
| status | TEXT | yes |
| created_at | TEXT | yes |
| agent_number | TEXT | yes |
| first_name | TEXT | yes |
| last_name | TEXT | yes |

---

### coverage_service_agent_coverage (21 rows)
Agent territory zones (zip + radius).

| Column | Type | Nullable |
|--------|------|----------|
| coverage_id | TEXT | yes |
| service_agent_id | TEXT | yes |
| anchor_zip | TEXT | yes |
| radius_miles | REAL | yes |
| status | TEXT | yes |
| created_by | TEXT | yes |
| created_at | TEXT | yes |
| retired_at | TEXT | yes |
| retired_by | TEXT | yes |
| notes | TEXT | yes |

---

## D1: svg-d1-spine (641a9a1e) — READ ONLY (company name)

### cl_company_identity (117,154 rows)
Sovereign company records. The ONLY place with `canonical_name`.

| Column | Type | Nullable | PK |
|--------|------|----------|-----|
| company_unique_id | TEXT | NOT NULL | PK |
| company_name | TEXT | NOT NULL | |
| company_domain | TEXT | yes | |
| linkedin_company_url | TEXT | yes | |
| source_system | TEXT | NOT NULL | |
| created_at | TEXT | NOT NULL | |
| company_fingerprint | TEXT | yes | |
| lifecycle_run_id | TEXT | yes | |
| existence_verified | INTEGER | yes | |
| verification_run_id | TEXT | yes | |
| verified_at | TEXT | yes | |
| domain_status_code | INTEGER | yes | |
| name_match_score | INTEGER | yes | |
| state_match_result | TEXT | yes | |
| canonical_name | TEXT | yes | |
| state_verified | TEXT | yes | |
| employee_count_band | TEXT | yes | |
| identity_pass | INTEGER | yes | |
| identity_status | TEXT | yes | |
| last_pass_at | TEXT | yes | |
| eligibility_status | TEXT | yes | |
| exclusion_reason | TEXT | yes | |
| entity_role | TEXT | yes | |
| sovereign_company_id | TEXT | yes | |
| final_outcome | TEXT | yes | |
| final_reason | TEXT | yes | |
| outreach_id | TEXT | yes | |
| sales_process_id | TEXT | yes | |
| client_id | TEXT | yes | |
| outreach_attached_at | TEXT | yes | |
| sales_opened_at | TEXT | yes | |
| client_promoted_at | TEXT | yes | |
| normalized_domain | TEXT | yes | |
| updated_at | TEXT | yes | |
| state_code | TEXT | yes | |
| lcs_id | TEXT | yes | |
| lcs_attached_at | TEXT | yes | |

**Key columns for Process 200:** `canonical_name` (company name for search), `company_domain`, `linkedin_company_url`, `outreach_id` (join key)

---

## JOIN MAP — How Process 200 Connects the Data

```
cl_company_identity.outreach_id
  ├→ outreach_company_target.outreach_id  (city, state, industry, employees, email_method)
  ├→ outreach_outreach.outreach_id        (domain, ein)
  ├→ people_company_slot.outreach_id      (slot_type, is_filled, person_unique_id)
  │     └→ people_people_master.unique_id (first_name, last_name, title, email, linkedin_url)
  ├→ outreach_blog.outreach_id            (source_url, about_url — team pages)
  ├→ outreach_dol.outreach_id             (filing_present, ein — trust signal)
  ├→ dol_form_5500.outreach_id            (sponsor_dfe_name — legal company name)
  ├→ outreach_people.outreach_id          (email, email_verified — delivery contacts)
  └→ intake_people_staging.company_unique_id (linkedin_url, names — already discovered)
```

---

## WHAT PROCESS 200 ALREADY HAS TO WORK WITH

For any company with `outreach_id`:

| Data Point | Source Table | Column |
|------------|------------|--------|
| Company name | cl_company_identity (spine) | canonical_name |
| Company name (legal/DOL) | dol_form_5500 | sponsor_dfe_name |
| Company domain | outreach_outreach | domain |
| Company LinkedIn | cl_company_identity (spine) | linkedin_company_url |
| City / State / Zip | outreach_company_target | city, state, postal_code |
| Industry | outreach_company_target | industry |
| Employee count | outreach_company_target | employees |
| Email pattern | outreach_company_target | email_method |
| EIN | outreach_outreach | ein |
| About page URL | outreach_blog | about_url |
| Team page / news URL | outreach_blog | news_url, source_url |
| CEO/CFO/HR slot status | people_company_slot | slot_type, is_filled |
| Existing contact details | people_people_master | linkedin_url, email, title |
| Already-discovered people | intake_people_staging | linkedin_url, first_name, last_name, raw_title |
| DOL trust signal | outreach_dol | filing_present |
| Title → slot mapping | people_title_slot_mapping | title_pattern → slot_type |

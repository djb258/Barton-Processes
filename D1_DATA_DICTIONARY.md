# Barton-Processes — D1 Data Dictionary

> **AUTO-GENERATED** by `imo-creator-v2/doc-engine/generators/d1-introspect.py`
> — last scan: `2026-05-12T15:52:10Z` (UTC).
>
> **Replaces** the hand-built dictionary (authority: "Live D1 introspection 2026-03-31",
> 527 lines, stale + partial). This file is now the single canonical source.
> Do not hand-edit the table/column facts; re-run the scanner.
> Human annotations (what a table is FOR, which column is the canonical source-of-record
> for a concept) go in the `<!-- TODO(human) -->` blocks and are tracked as schema squawks.
>
> **Scope:** Cloudflare D1 only (`svg-d1-spine`, `svg-d1-outreach-ops`).
> Neon Postgres is explicitly out of scope (it is the vault).
> `imo-brain` + `imo-d1-global`: TODO — see script DATABASES dict.
> BigQuery: not yet scanned — see **BAR-434**.
>
> **Schema questions → start here. Never spelunk `sqlite_master` by hand.**

**122 tables** across 2 databases · 23 owning processes/areas · 0 unclaimed.

## Master index — table → owning process

| Table | DB | Owner | Rows | Cols |
|---|---|---|--:|--:|
| `_cf_KV` | svg-d1-outreach-ops | <cloudflare internal> | ? | 0 |
| `_cf_KV` | svg-d1-spine | <cloudflare internal> | ? | 0 |
| `catalog_columns` | svg-d1-outreach-ops | <governance: schema catalog — BAR-434> | 725 | 27 |
| `catalog_schemas` | svg-d1-outreach-ops | <governance: schema catalog — BAR-434> | 6 | 8 |
| `catalog_tables` | svg-d1-outreach-ops | <governance: schema catalog — BAR-434> | 31 | 15 |
| `cl_cl_err_existence` | svg-d1-spine | 100-lcs-pipeline | 9328 | 18 |
| `cl_company_identity` | svg-d1-spine | 100-lcs-pipeline | 32702 | 46 |
| `cl_company_identity_bridge` | svg-d1-spine | 100-lcs-pipeline | 74641 | 7 |
| `cl_company_identity_excluded` | svg-d1-spine | 100-lcs-pipeline | 5327 | 33 |
| `cl_movement_code_registry` | svg-d1-spine | 100-lcs-pipeline | 15 | 5 |
| `client_grid` | svg-d1-spine | 830-client-portal | 0 | 15 |
| `clnt_client` | svg-d1-spine | 810-client-intake | 0 | 17 |
| `coverage_service_agent` | svg-d1-outreach-ops | 010-seed-d1 | 3 | 7 |
| `coverage_service_agent` | svg-d1-spine | 010-seed-d1 | 3 | 7 |
| `coverage_service_agent_coverage` | svg-d1-outreach-ops | 010-seed-d1 | 3 | 10 |
| `coverage_service_agent_coverage` | svg-d1-spine | 010-seed-d1 | 0 | 10 |
| `ctb_audit_log` | svg-d1-spine | <governance> | 0 | 11 |
| `ctb_batch_audit_log` | svg-d1-spine | <governance> | 0 | 6 |
| `ctb_promotion_paths` | svg-d1-spine | <governance> | 0 | 11 |
| `ctb_raw_batch_registry` | svg-d1-spine | <governance> | 0 | 11 |
| `ctb_table_registry` | svg-d1-outreach-ops | <governance> | 675 | 10 |
| `ctb_table_registry` | svg-d1-spine | <governance> | 0 | 10 |
| `ctb_vendor_bridges` | svg-d1-spine | <governance> | 0 | 12 |
| `ctb_violation_log` | svg-d1-spine | <governance> | 0 | 10 |
| `doctrine_doctrine_key` | svg-d1-spine | <imo-creator-v2: doctrine> | 335 | 8 |
| `doctrine_doctrine_library` | svg-d1-spine | <imo-creator-v2: doctrine> | 668 | 16 |
| `doctrine_doctrine_library_error` | svg-d1-spine | <imo-creator-v2: doctrine> | 0 | 6 |
| `dol_column_metadata` | svg-d1-outreach-ops | <governance> | 2678 | 14 |
| `dol_form_5500` | svg-d1-outreach-ops | 010-seed-d1 | 14252 | 25 |
| `dol_schedule_a` | svg-d1-outreach-ops | 010-seed-d1 | 9538 | 15 |
| `dol_schedule_c` | svg-d1-outreach-ops | 010-seed-d1 | 18246 | 16 |
| `dol_schedule_other` | svg-d1-outreach-ops | 010-seed-d1 | 67164 | 9 |
| `dyno_cycles` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 311 | 19 |
| `dyno_dmj` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 12 |
| `dyno_dmj_error` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 9 |
| `dyno_kc` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 12 |
| `dyno_kc_error` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 9 |
| `dyno_runs` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 89 | 21 |
| `dyno_up` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 15 |
| `dyno_up_error` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 9 |
| `dyno_us` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 13 |
| `dyno_us_error` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 9 |
| `dyno_variables` | svg-d1-outreach-ops | <imo-creator-v2: run-dyno> | 0 | 16 |
| `engine_cells` | svg-d1-outreach-ops | <imo-creator-v2: engine> | 8449 | 39 |
| `engine_cells_error` | svg-d1-outreach-ops | <imo-creator-v2: engine> | 0 | 10 |
| `engine_runs` | svg-d1-outreach-ops | <imo-creator-v2: engine> | 17 | 34 |
| `engine_runs_error` | svg-d1-outreach-ops | <imo-creator-v2: engine> | 0 | 16 |
| `enrichment_column_registry` | svg-d1-outreach-ops | <governance> | 53 | 14 |
| `enrichment_hunter_company` | svg-d1-outreach-ops | 201-email-discovery | 15537 | 23 |
| `enrichment_hunter_contact` | svg-d1-outreach-ops | 201-email-discovery | 175632 | 25 |
| `error_log` | svg-d1-spine | <governance: error spine> | 0 | 11 |
| `escalation` | svg-d1-spine | <governance: error spine> | 0 | 27 |
| `field_monitor_check_log` | svg-d1-spine | <imo-creator-v2: field monitor> | 1 | 9 |
| `field_monitor_error_log` | svg-d1-spine | <imo-creator-v2: field monitor> | 1 | 7 |
| `field_monitor_field_state` | svg-d1-spine | <imo-creator-v2: field monitor> | 0 | 11 |
| `field_monitor_rate_state` | svg-d1-spine | <imo-creator-v2: field monitor> | 0 | 8 |
| `field_monitor_url_registry` | svg-d1-spine | <imo-creator-v2: field monitor> | 1 | 7 |
| `intake_people_staging` | svg-d1-outreach-ops | 200-people-worker | 0 | 15 |
| `lcs_adapter_registry` | svg-d1-spine | 100-lcs-pipeline | 3 | 15 |
| `lcs_cid` | svg-d1-spine | 100-lcs-pipeline | 3677 | 14 |
| `lcs_contact_channel_state` | svg-d1-outreach-ops | 100-lcs-pipeline | 0 | 10 |
| `lcs_contact_channel_state` | svg-d1-spine | 100-lcs-pipeline | 1456 | 10 |
| `lcs_contact_engagement_score` | svg-d1-outreach-ops | 100-lcs-pipeline | 0 | 12 |
| `lcs_contact_engagement_score` | svg-d1-spine | 100-lcs-pipeline | 1110 | 12 |
| `lcs_contact_sequence_state` | svg-d1-outreach-ops | 100-lcs-pipeline | 0 | 11 |
| `lcs_contact_sequence_state` | svg-d1-spine | 100-lcs-pipeline | 0 | 11 |
| `lcs_domain_rotation` | svg-d1-spine | 100-lcs-pipeline | 14 | 11 |
| `lcs_email_signature` | svg-d1-outreach-ops | 100-lcs-pipeline | 1 | 13 |
| `lcs_email_signature` | svg-d1-spine | 100-lcs-pipeline | 1 | 13 |
| `lcs_engagement_rules` | svg-d1-outreach-ops | 100-lcs-pipeline | 6 | 9 |
| `lcs_engagement_rules` | svg-d1-spine | 100-lcs-pipeline | 6 | 9 |
| `lcs_err0` | svg-d1-spine | 100-lcs-pipeline | 651 | 13 |
| `lcs_event` | svg-d1-spine | 100-lcs-pipeline | 12803 | 21 |
| `lcs_frame_registry` | svg-d1-outreach-ops | 100-lcs-pipeline | 8 | 16 |
| `lcs_frame_registry` | svg-d1-spine | 100-lcs-pipeline | 14 | 24 |
| `lcs_m_registry` | svg-d1-outreach-ops | 100-lcs-pipeline | 37 | 17 |
| `lcs_m_registry` | svg-d1-spine | 100-lcs-pipeline | 37 | 17 |
| `lcs_message_error` | svg-d1-outreach-ops | 100-lcs-pipeline | 0 | 8 |
| `lcs_message_ledger` | svg-d1-outreach-ops | 100-lcs-pipeline | 0 | 18 |
| `lcs_mid_sequence_state` | svg-d1-spine | 100-lcs-pipeline | 3404 | 15 |
| `lcs_sender_profile_registry` | svg-d1-outreach-ops | 100-lcs-pipeline | 0 | 10 |
| `lcs_sequence_def` | svg-d1-outreach-ops | 100-lcs-pipeline | 5 | 8 |
| `lcs_sequence_def` | svg-d1-spine | 100-lcs-pipeline | 5 | 8 |
| `lcs_sid_output` | svg-d1-spine | 100-lcs-pipeline | 3617 | 14 |
| `lcs_signal_queue` | svg-d1-spine | 100-lcs-pipeline | 4506 | 15 |
| `lcs_signal_registry` | svg-d1-spine | 100-lcs-pipeline | 9 | 13 |
| `lcs_suppression` | svg-d1-spine | 100-lcs-pipeline | 261 | 4 |
| `lcs_voice_library` | svg-d1-outreach-ops | 100-lcs-pipeline | 4 | 11 |
| `lcs_voice_library` | svg-d1-spine | 100-lcs-pipeline | 4 | 11 |
| `master_error` | svg-d1-spine | <governance: error spine> | 0 | 26 |
| `outreach_appointments` | svg-d1-outreach-ops | 500-talent-flow | 487 | 22 |
| `outreach_bit_scores` | svg-d1-outreach-ops | 600-bit-scoring | 7002 | 12 |
| `outreach_blog` | svg-d1-outreach-ops | 300-blog-worker | 32702 | 13 |
| `outreach_blog_ingress_control` | svg-d1-outreach-ops | 300-blog-worker | 1 | 14 |
| `outreach_column_registry` | svg-d1-outreach-ops | <governance> | 78 | 14 |
| `outreach_company_hub_status` | svg-d1-outreach-ops | 010-seed-d1 | 15308 | 8 |
| `outreach_company_target` | svg-d1-outreach-ops | 010-seed-d1 | 32702 | 32 |
| `outreach_ctx_context` | svg-d1-outreach-ops | 700-campaign-engine | 0 | 4 |
| `outreach_dol` | svg-d1-outreach-ops | 010-seed-d1 | 27464 | 12 |
| `outreach_hub_registry` | svg-d1-outreach-ops | <governance> | 6 | 12 |
| `outreach_outreach` | svg-d1-outreach-ops | 010-seed-d1 | 32702 | 7 |
| `outreach_people` | svg-d1-outreach-ops | 200-people-worker | 0 | 20 |
| `outreach_signal_output` | svg-d1-outreach-ops | 010-seed-d1 | 0 | 12 |
| `page_raw_html` | svg-d1-outreach-ops | 301-page-parser | 22928 | 8 |
| `people_company_slot` | svg-d1-outreach-ops | 200-people-worker | 98106 | 14 |
| `people_people_master` | svg-d1-outreach-ops | 200-people-worker | 57667 | 36 |
| `people_slot_ingress_control` | svg-d1-outreach-ops | 200-people-worker | 1 | 9 |
| `people_title_slot_mapping` | svg-d1-outreach-ops | 200-people-worker | 43 | 5 |
| `platform_registry` | svg-d1-outreach-ops | <governance> | 58125 | 10 |
| `sales_appointments_already_had` | svg-d1-spine | 900-sales-portal | 0 | 12 |
| `sales_grid` | svg-d1-spine | 900-sales-portal | 0 | 17 |
| `sales_sales_state` | svg-d1-spine | 900-sales-portal | 0 | 9 |
| `sales_sales_state_error` | svg-d1-spine | 900-sales-portal | 0 | 10 |
| `slot_workbench` | svg-d1-outreach-ops | 200-people-worker | 101559 | 100 |
| `sovereign_companies` | svg-d1-spine | <governance: sovereign registry> | 0 | 11 |
| `sub_hub_registry` | svg-d1-outreach-ops | <governance> | 12 | 4 |
| `up_runs` | svg-d1-outreach-ops | <imo-creator-v2: UP> | 0 | 16 |
| `up_stages` | svg-d1-outreach-ops | <imo-creator-v2: UP> | 0 | 15 |
| `vendor_ct` | svg-d1-outreach-ops | 201-email-discovery | 18683 | 31 |
| `vendor_people` | svg-d1-outreach-ops | 201-email-discovery | 175632 | 34 |
| `work_order_items` | svg-d1-spine | <governance: work orders> | 0 | 11 |
| `work_orders` | svg-d1-spine | <governance: work orders> | 0 | 8 |

## 010-seed-d1

### `coverage_service_agent`

- **DB:** `svg-d1-spine`  ·  **Rows:** 3  ·  **Columns:** 7
- **Primary key:** `service_agent_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `service_agent_id` | TEXT | ✓ | ✓ |  |
| `agent_name` | TEXT |  | ✓ |  |
| `status` | TEXT |  | ✓ | `'active'` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `agent_number` | TEXT |  | ✓ |  |
| `first_name` | TEXT |  |  |  |
| `last_name` | TEXT |  |  |  |

### `coverage_service_agent`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 3  ·  **Columns:** 7

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `service_agent_id` | TEXT |  |  |  |
| `agent_name` | TEXT |  |  |  |
| `status` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `agent_number` | TEXT |  |  |  |
| `first_name` | TEXT |  |  |  |
| `last_name` | TEXT |  |  |  |

### `coverage_service_agent_coverage`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 10
- **Primary key:** `coverage_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `coverage_id` | TEXT | ✓ | ✓ |  |
| `service_agent_id` | TEXT |  | ✓ |  |
| `anchor_zip` | TEXT |  | ✓ |  |
| `radius_miles` | REAL |  | ✓ |  |
| `status` | TEXT |  | ✓ | `'active'` |
| `created_by` | TEXT |  | ✓ |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `retired_at` | TEXT |  |  |  |
| `retired_by` | TEXT |  |  |  |
| `notes` | TEXT |  |  |  |

### `coverage_service_agent_coverage`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 3  ·  **Columns:** 10

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `coverage_id` | TEXT |  |  |  |
| `service_agent_id` | TEXT |  |  |  |
| `anchor_zip` | TEXT |  |  |  |
| `radius_miles` | REAL |  |  |  |
| `status` | TEXT |  |  |  |
| `created_by` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `retired_at` | TEXT |  |  |  |
| `retired_by` | TEXT |  |  |  |
| `notes` | TEXT |  |  |  |

### `dol_form_5500`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 14252  ·  **Columns:** 25
- **Primary key:** `ack_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `ack_id` | TEXT | ✓ |  |  |
| `outreach_id` | TEXT |  |  |  |
| `sponsor_dfe_ein` | TEXT |  | ✓ |  |
| `sponsor_dfe_name` | TEXT |  |  |  |
| `plan_name` | TEXT |  |  |  |
| `plan_number` | TEXT |  |  |  |
| `plan_eff_date` | TEXT |  |  |  |
| `form_year` | TEXT |  |  |  |
| `form_tax_prd` | TEXT |  |  |  |
| `spons_dfe_mail_us_city` | TEXT |  |  |  |
| `spons_dfe_mail_us_state` | TEXT |  |  |  |
| `spons_dfe_mail_us_zip` | TEXT |  |  |  |
| `tot_active_partcp_cnt` | INTEGER |  |  |  |
| `tot_partcp_boy_cnt` | INTEGER |  |  |  |
| `admin_name` | TEXT |  |  |  |
| `admin_ein` | TEXT |  |  |  |
| `type_plan_entity_cd` | TEXT |  |  |  |
| `sch_a_attached_ind` | TEXT |  |  |  |
| `num_sch_a_attached_cnt` | INTEGER |  |  |  |
| `filing_status` | TEXT |  |  |  |
| `date_received` | TEXT |  |  |  |
| `funding_arrangement` | TEXT |  |  |  |
| `benefit_arrangement` | TEXT |  |  |  |
| `all_data` | TEXT |  |  |  |
| `seeded_at` | TEXT |  | ✓ | `datetime('now')` |

### `dol_schedule_a`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 9538  ·  **Columns:** 15

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INT |  |  |  |
| `ack_id` | TEXT |  |  |  |
| `outreach_id` | TEXT |  |  |  |
| `sponsor_dfe_ein` | TEXT |  |  |  |
| `form_year` | TEXT |  |  |  |
| `row_order` | INT |  |  |  |
| `ins_broker_name` | TEXT |  |  |  |
| `ins_broker_us_city` | TEXT |  |  |  |
| `ins_broker_us_state` | TEXT |  |  |  |
| `ins_broker_us_zip` | TEXT |  |  |  |
| `ins_broker_comm_pd_amt` | REAL |  |  |  |
| `ins_broker_fees_pd_amt` | REAL |  |  |  |
| `ins_broker_code` | TEXT |  |  |  |
| `all_data` | TEXT |  |  |  |
| `seeded_at` | TEXT |  |  |  |

### `dol_schedule_c`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 18246  ·  **Columns:** 16

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INT |  |  |  |
| `ack_id` | TEXT |  |  |  |
| `outreach_id` | TEXT |  |  |  |
| `sponsor_dfe_ein` | TEXT |  |  |  |
| `form_year` | TEXT |  |  |  |
| `row_order` | INT |  |  |  |
| `provider_name` | TEXT |  |  |  |
| `provider_ein` | TEXT |  |  |  |
| `provider_us_city` | TEXT |  |  |  |
| `provider_us_state` | TEXT |  |  |  |
| `provider_srvc_codes` | TEXT |  |  |  |
| `provider_relation` | TEXT |  |  |  |
| `provider_direct_comp_amt` | REAL |  |  |  |
| `provider_indirect_comp_amt` | REAL |  |  |  |
| `all_data` | TEXT |  |  |  |
| `seeded_at` | TEXT |  |  |  |

### `dol_schedule_other`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 67164  ·  **Columns:** 9

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INT |  |  |  |
| `ack_id` | TEXT |  |  |  |
| `outreach_id` | TEXT |  |  |  |
| `sponsor_dfe_ein` | TEXT |  |  |  |
| `schedule_type` | TEXT |  |  |  |
| `form_year` | TEXT |  |  |  |
| `row_order` | INT |  |  |  |
| `all_data` | TEXT |  |  |  |
| `seeded_at` | TEXT |  |  |  |

### `outreach_company_hub_status`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 15308  ·  **Columns:** 8
- **Primary key:** `company_unique_id`, `hub_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `company_unique_id` | TEXT | ✓ | ✓ |  |
| `hub_id` | TEXT | ✓ | ✓ |  |
| `status` | TEXT |  | ✓ |  |
| `status_reason` | TEXT |  |  |  |
| `metric_value` | REAL |  |  |  |
| `last_processed_at` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `outreach_company_target`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 32702  ·  **Columns:** 32
- **Primary key:** `target_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `target_id` | TEXT | ✓ | ✓ |  |
| `company_unique_id` | TEXT |  |  |  |
| `outreach_status` | TEXT |  | ✓ | `'queued'` |
| `bit_score_snapshot` | INTEGER |  |  |  |
| `first_targeted_at` | TEXT |  |  |  |
| `last_targeted_at` | TEXT |  |  |  |
| `sequence_count` | INTEGER |  | ✓ | `0` |
| `active_sequence_id` | TEXT |  |  |  |
| `source` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |
| `outreach_id` | TEXT |  |  |  |
| `email_method` | TEXT |  |  |  |
| `method_type` | TEXT |  |  |  |
| `confidence_score` | REAL |  |  |  |
| `execution_status` | TEXT |  |  | `'pending'` |
| `imo_completed_at` | TEXT |  |  |  |
| `is_catchall` | INTEGER |  |  | `0` |
| `industry` | TEXT |  |  |  |
| `employees` | INTEGER |  |  |  |
| `country` | TEXT |  |  |  |
| `state` | TEXT |  |  |  |
| `city` | TEXT |  |  |  |
| `postal_code` | TEXT |  |  |  |
| `data_year` | INTEGER |  |  |  |
| `postal_code_source` | TEXT |  |  |  |
| `postal_code_updated_at` | TEXT |  |  |  |
| `service_agent_id` | TEXT |  |  |  |
| `service_agent_name` | TEXT |  |  |  |
| `service_agent_number` | TEXT |  |  |  |
| `service_agents` | TEXT |  |  |  |
| `agent_count` | INTEGER |  |  | `0` |

### `outreach_dol`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 27464  ·  **Columns:** 12

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `dol_id` | TEXT |  | ✓ |  |
| `outreach_id` | TEXT |  | ✓ |  |
| `ein` | TEXT |  |  |  |
| `filing_present` | INTEGER |  |  |  |
| `funding_type` | TEXT |  |  |  |
| `broker_or_advisor` | TEXT |  |  |  |
| `carrier` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `updated_at` | TEXT |  |  |  |
| `url_enrichment_data` | TEXT |  |  |  |
| `renewal_month` | INTEGER |  |  |  |
| `outreach_start_month` | INTEGER |  |  |  |

### `outreach_outreach`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 32702  ·  **Columns:** 7
- **Primary key:** `outreach_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `outreach_id` | TEXT | ✓ | ✓ |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |
| `domain` | TEXT |  |  |  |
| `ein` | TEXT |  |  |  |
| `has_appointment` | INTEGER |  |  | `0` |

### `outreach_signal_output`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 12
- **Primary key:** `signal_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `signal_id` | TEXT | ✓ | ✓ |  |
| `outreach_id` | TEXT |  | ✓ |  |
| `signal_code` | TEXT |  | ✓ |  |
| `signal_name` | TEXT |  | ✓ |  |
| `signal_source` | TEXT |  | ✓ |  |
| `signal_value` | TEXT |  | ✓ | `'{}'` |
| `magnitude` | INTEGER |  | ✓ | `0` |
| `detected_at` | TEXT |  | ✓ | `datetime('now')` |
| `expires_at` | TEXT |  | ✓ |  |
| `correlation_id` | TEXT |  | ✓ |  |
| `run_month` | TEXT |  | ✓ |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

## 100-lcs-pipeline

### `cl_cl_err_existence`

- **DB:** `svg-d1-spine`  ·  **Rows:** 9328  ·  **Columns:** 18
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ | ✓ |  |
| `company_unique_id` | TEXT |  | ✓ |  |
| `company_name` | TEXT |  |  |  |
| `company_domain` | TEXT |  |  |  |
| `linkedin_company_url` | TEXT |  |  |  |
| `reason_code` | TEXT |  | ✓ |  |
| `domain_status_code` | INTEGER |  |  |  |
| `domain_redirect_chain` | TEXT |  |  |  |
| `domain_final_url` | TEXT |  |  |  |
| `domain_error` | TEXT |  |  |  |
| `extracted_name` | TEXT |  |  |  |
| `name_match_score` | INTEGER |  |  |  |
| `extracted_state` | TEXT |  |  |  |
| `state_match_result` | TEXT |  |  |  |
| `evidence` | TEXT |  |  |  |
| `verification_run_id` | TEXT |  | ✓ |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `error_type` | TEXT |  |  |  |

### `cl_company_identity`

- **DB:** `svg-d1-spine`  ·  **Rows:** 32702  ·  **Columns:** 46
- **Primary key:** `company_unique_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `company_unique_id` | TEXT | ✓ | ✓ |  |
| `company_name` | TEXT |  | ✓ |  |
| `company_domain` | TEXT |  |  |  |
| `linkedin_company_url` | TEXT |  |  |  |
| `source_system` | TEXT |  | ✓ |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `company_fingerprint` | TEXT |  |  |  |
| `lifecycle_run_id` | TEXT |  |  |  |
| `existence_verified` | INTEGER |  |  | `0` |
| `verification_run_id` | TEXT |  |  |  |
| `verified_at` | TEXT |  |  |  |
| `domain_status_code` | INTEGER |  |  |  |
| `name_match_score` | INTEGER |  |  |  |
| `state_match_result` | TEXT |  |  |  |
| `canonical_name` | TEXT |  |  |  |
| `state_verified` | TEXT |  |  |  |
| `employee_count_band` | TEXT |  |  |  |
| `identity_pass` | INTEGER |  |  | `0` |
| `identity_status` | TEXT |  |  | `'PENDING'` |
| `last_pass_at` | TEXT |  |  |  |
| `eligibility_status` | TEXT |  |  |  |
| `exclusion_reason` | TEXT |  |  |  |
| `entity_role` | TEXT |  |  |  |
| `sovereign_company_id` | TEXT |  |  |  |
| `final_outcome` | TEXT |  |  |  |
| `final_reason` | TEXT |  |  |  |
| `outreach_id` | TEXT |  |  |  |
| `sales_process_id` | TEXT |  |  |  |
| `client_id` | TEXT |  |  |  |
| `outreach_attached_at` | TEXT |  |  |  |
| `sales_opened_at` | TEXT |  |  |  |
| `client_promoted_at` | TEXT |  |  |  |
| `normalized_domain` | TEXT |  |  |  |
| `updated_at` | TEXT |  |  |  |
| `state_code` | TEXT |  |  |  |
| `lcs_id` | TEXT |  |  |  |
| `lcs_attached_at` | TEXT |  |  |  |
| `address_line_1` | TEXT |  |  |  |
| `address_line_2` | TEXT |  |  |  |
| `city` | TEXT |  |  |  |
| `zip_code` | TEXT |  |  |  |
| `address_normalized` | TEXT |  |  |  |
| `address_verified` | INTEGER |  |  | `0` |
| `address_verified_at` | TEXT |  |  |  |
| `address_source` | TEXT |  |  |  |
| `address_batch_id` | TEXT |  |  |  |

### `cl_company_identity_bridge`

- **DB:** `svg-d1-spine`  ·  **Rows:** 74641  ·  **Columns:** 7
- **Primary key:** `bridge_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `bridge_id` | TEXT | ✓ | ✓ |  |
| `source_company_id` | TEXT |  | ✓ |  |
| `company_sov_id` | TEXT |  | ✓ |  |
| `source_system` | TEXT |  | ✓ |  |
| `minted_at` | TEXT |  | ✓ | `datetime('now')` |
| `minted_by` | TEXT |  | ✓ | `'cl_bootstrap'` |
| `lifecycle_run_id` | TEXT |  |  |  |

### `cl_company_identity_excluded`

- **DB:** `svg-d1-spine`  ·  **Rows:** 5327  ·  **Columns:** 33
- **Primary key:** `company_unique_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `company_unique_id` | TEXT | ✓ | ✓ |  |
| `company_name` | TEXT |  | ✓ |  |
| `company_domain` | TEXT |  |  |  |
| `linkedin_company_url` | TEXT |  |  |  |
| `source_system` | TEXT |  | ✓ |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `company_fingerprint` | TEXT |  |  |  |
| `lifecycle_run_id` | TEXT |  |  |  |
| `existence_verified` | INTEGER |  |  | `0` |
| `verification_run_id` | TEXT |  |  |  |
| `verified_at` | TEXT |  |  |  |
| `domain_status_code` | INTEGER |  |  |  |
| `name_match_score` | INTEGER |  |  |  |
| `state_match_result` | TEXT |  |  |  |
| `canonical_name` | TEXT |  |  |  |
| `state_verified` | TEXT |  |  |  |
| `employee_count_band` | TEXT |  |  |  |
| `identity_pass` | INTEGER |  |  | `0` |
| `identity_status` | TEXT |  |  | `'PENDING'` |
| `last_pass_at` | TEXT |  |  |  |
| `eligibility_status` | TEXT |  |  |  |
| `exclusion_reason` | TEXT |  |  |  |
| `entity_role` | TEXT |  |  |  |
| `sovereign_company_id` | TEXT |  |  |  |
| `final_outcome` | TEXT |  |  |  |
| `final_reason` | TEXT |  |  |  |
| `outreach_id` | TEXT |  |  |  |
| `sales_process_id` | TEXT |  |  |  |
| `client_id` | TEXT |  |  |  |
| `outreach_attached_at` | TEXT |  |  |  |
| `sales_opened_at` | TEXT |  |  |  |
| `client_promoted_at` | TEXT |  |  |  |
| `normalized_domain` | TEXT |  |  |  |

### `cl_movement_code_registry`

- **DB:** `svg-d1-spine`  ·  **Rows:** 15  ·  **Columns:** 5
- **Primary key:** `subhub`, `code`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `subhub` | TEXT | ✓ | ✓ |  |
| `code` | INTEGER | ✓ | ✓ |  |
| `description` | TEXT |  | ✓ |  |
| `active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_adapter_registry`

- **DB:** `svg-d1-spine`  ·  **Rows:** 3  ·  **Columns:** 15
- **Primary key:** `adapter_type`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `adapter_type` | TEXT | ✓ | ✓ |  |
| `adapter_name` | TEXT |  | ✓ |  |
| `channel` | TEXT |  | ✓ |  |
| `direction` | TEXT |  | ✓ | `'outbound'` |
| `description` | TEXT |  |  |  |
| `domain_rotation_config` | TEXT |  |  |  |
| `health_status` | TEXT |  | ✓ | `'HEALTHY'` |
| `daily_cap` | INTEGER |  |  |  |
| `sent_today` | INTEGER |  | ✓ | `0` |
| `bounce_rate_24h` | REAL |  |  | `0` |
| `complaint_rate_24h` | REAL |  |  | `0` |
| `auto_pause_rules` | TEXT |  |  |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_cid`

- **DB:** `svg-d1-spine`  ·  **Rows:** 3677  ·  **Columns:** 14
- **Primary key:** `communication_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `communication_id` | TEXT | ✓ | ✓ |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `entity_type` | TEXT |  | ✓ |  |
| `entity_id` | TEXT |  | ✓ |  |
| `signal_set_hash` | TEXT |  | ✓ |  |
| `signal_queue_id` | TEXT |  |  |  |
| `frame_id` | TEXT |  | ✓ |  |
| `lifecycle_phase` | TEXT |  | ✓ |  |
| `lane` | TEXT |  | ✓ |  |
| `agent_number` | TEXT |  | ✓ |  |
| `intelligence_tier` | INTEGER |  |  |  |
| `compilation_status` | TEXT |  | ✓ |  |
| `compilation_reason` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_contact_channel_state`

- **DB:** `svg-d1-spine`  ·  **Rows:** 1456  ·  **Columns:** 10
- **Primary key:** `contact_email`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `contact_email` | TEXT | ✓ |  |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `primary_channel` | TEXT |  | ✓ | `'MG'` |
| `channel_state` | TEXT |  | ✓ | `'email_active'` |
| `email_status` | TEXT |  | ✓ | `'active'` |
| `linkedin_status` | TEXT |  | ✓ | `'not_started'` |
| `last_channel_switch_at` | TEXT |  |  |  |
| `switch_reason` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_contact_channel_state`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 10
- **Primary key:** `contact_email`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `contact_email` | TEXT | ✓ |  |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `primary_channel` | TEXT |  | ✓ | `'MG'` |
| `channel_state` | TEXT |  | ✓ | `'email_active'` |
| `email_status` | TEXT |  | ✓ | `'active'` |
| `linkedin_status` | TEXT |  | ✓ | `'not_started'` |
| `last_channel_switch_at` | TEXT |  |  |  |
| `switch_reason` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_contact_engagement_score`

- **DB:** `svg-d1-spine`  ·  **Rows:** 1110  ·  **Columns:** 12
- **Primary key:** `contact_email`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `contact_email` | TEXT | ✓ |  |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `email_score` | REAL |  | ✓ | `0` |
| `linkedin_score` | REAL |  | ✓ | `0` |
| `web_score` | REAL |  | ✓ | `0` |
| `composite_score` | REAL |  | ✓ | `0` |
| `total_events` | INTEGER |  | ✓ | `0` |
| `last_event_type` | TEXT |  |  |  |
| `last_event_at` | TEXT |  |  |  |
| `is_hot_lead` | INTEGER |  | ✓ | `0` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_contact_engagement_score`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 12
- **Primary key:** `contact_email`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `contact_email` | TEXT | ✓ |  |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `email_score` | REAL |  | ✓ | `0` |
| `linkedin_score` | REAL |  | ✓ | `0` |
| `web_score` | REAL |  | ✓ | `0` |
| `composite_score` | REAL |  | ✓ | `0` |
| `total_events` | INTEGER |  | ✓ | `0` |
| `last_event_type` | TEXT |  |  |  |
| `last_event_at` | TEXT |  |  |  |
| `is_hot_lead` | INTEGER |  | ✓ | `0` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_contact_sequence_state`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | TEXT | ✓ |  |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `contact_email` | TEXT |  | ✓ |  |
| `sequence_id` | TEXT |  | ✓ |  |
| `current_step` | INTEGER |  | ✓ | `1` |
| `status` | TEXT |  | ✓ | `'active'` |
| `last_step_at` | TEXT |  |  |  |
| `next_step_after` | TEXT |  |  |  |
| `last_engagement` | TEXT |  |  | `NULL` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_contact_sequence_state`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | TEXT | ✓ |  |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `contact_email` | TEXT |  | ✓ |  |
| `sequence_id` | TEXT |  | ✓ |  |
| `current_step` | INTEGER |  | ✓ | `1` |
| `status` | TEXT |  | ✓ | `'active'` |
| `last_step_at` | TEXT |  |  |  |
| `next_step_after` | TEXT |  |  |  |
| `last_engagement` | TEXT |  |  | `NULL` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_domain_rotation`

- **DB:** `svg-d1-spine`  ·  **Rows:** 14  ·  **Columns:** 11
- **Primary key:** `domain`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `domain` | TEXT | ✓ |  |  |
| `sent_today` | INTEGER |  | ✓ | `0` |
| `daily_cap` | INTEGER |  | ✓ | `20` |
| `warmup_week` | INTEGER |  | ✓ | `1` |
| `last_sent_at` | TEXT |  |  |  |
| `total_sent` | INTEGER |  | ✓ | `0` |
| `bounce_count_24h` | INTEGER |  | ✓ | `0` |
| `is_paused` | INTEGER |  | ✓ | `0` |
| `pause_reason` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_email_signature`

- **DB:** `svg-d1-spine`  ·  **Rows:** 1  ·  **Columns:** 13
- **Primary key:** `sig_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sig_id` | TEXT | ✓ |  |  |
| `agent_number` | TEXT |  | ✓ |  |
| `name` | TEXT |  | ✓ |  |
| `title` | TEXT |  | ✓ |  |
| `company` | TEXT |  | ✓ |  |
| `phone` | TEXT |  |  |  |
| `website` | TEXT |  |  |  |
| `linkedin_url` | TEXT |  |  |  |
| `booking_link` | TEXT |  |  |  |
| `tagline` | TEXT |  |  |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_email_signature`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 1  ·  **Columns:** 13
- **Primary key:** `sig_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sig_id` | TEXT | ✓ |  |  |
| `agent_number` | TEXT |  | ✓ |  |
| `name` | TEXT |  | ✓ |  |
| `title` | TEXT |  | ✓ |  |
| `company` | TEXT |  | ✓ |  |
| `phone` | TEXT |  |  |  |
| `website` | TEXT |  |  |  |
| `linkedin_url` | TEXT |  |  |  |
| `booking_link` | TEXT |  |  |  |
| `tagline` | TEXT |  |  |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_engagement_rules`

- **DB:** `svg-d1-spine`  ·  **Rows:** 6  ·  **Columns:** 9
- **Primary key:** `rule_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `rule_id` | TEXT | ✓ |  |  |
| `trigger_event` | TEXT |  | ✓ |  |
| `action` | TEXT |  | ✓ |  |
| `delay_hours` | INTEGER |  | ✓ | `0` |
| `followup_frame_id` | TEXT |  |  |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |
| `signal_priority` | INTEGER |  | ✓ | `8` |

### `lcs_engagement_rules`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 6  ·  **Columns:** 9
- **Primary key:** `rule_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `rule_id` | TEXT | ✓ |  |  |
| `trigger_event` | TEXT |  | ✓ |  |
| `action` | TEXT |  | ✓ |  |
| `delay_hours` | INTEGER |  | ✓ | `0` |
| `followup_frame_id` | TEXT |  |  |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |
| `signal_priority` | INTEGER |  | ✓ | `8` |

### `lcs_err0`

- **DB:** `svg-d1-spine`  ·  **Rows:** 651  ·  **Columns:** 13
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ | ✓ |  |
| `message_run_id` | TEXT |  | ✓ |  |
| `communication_id` | TEXT |  |  |  |
| `sovereign_company_id` | TEXT |  |  |  |
| `failure_type` | TEXT |  | ✓ |  |
| `failure_message` | TEXT |  | ✓ |  |
| `lifecycle_phase` | TEXT |  |  |  |
| `adapter_type` | TEXT |  |  |  |
| `orbt_strike_number` | INTEGER |  |  |  |
| `orbt_action_taken` | TEXT |  |  |  |
| `orbt_alt_channel_eligible` | INTEGER |  |  |  |
| `orbt_alt_channel_reason` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_event`

- **DB:** `svg-d1-spine`  ·  **Rows:** 12803  ·  **Columns:** 21
- **Primary key:** `communication_id`, `created_at`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `communication_id` | TEXT | ✓ | ✓ |  |
| `message_run_id` | TEXT |  | ✓ |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `entity_type` | TEXT |  | ✓ |  |
| `entity_id` | TEXT |  | ✓ |  |
| `signal_set_hash` | TEXT |  | ✓ |  |
| `frame_id` | TEXT |  | ✓ |  |
| `adapter_type` | TEXT |  | ✓ |  |
| `channel` | TEXT |  | ✓ |  |
| `delivery_status` | TEXT |  | ✓ |  |
| `lifecycle_phase` | TEXT |  | ✓ |  |
| `event_type` | TEXT |  | ✓ |  |
| `lane` | TEXT |  | ✓ |  |
| `agent_number` | TEXT |  | ✓ |  |
| `step_number` | INTEGER |  | ✓ |  |
| `step_name` | TEXT |  | ✓ |  |
| `payload` | TEXT |  |  |  |
| `adapter_response` | TEXT |  |  |  |
| `intelligence_tier` | INTEGER |  |  |  |
| `sender_identity` | TEXT |  |  |  |
| `created_at` | TEXT | ✓ | ✓ | `datetime('now')` |

### `lcs_frame_registry`

- **DB:** `svg-d1-spine`  ·  **Rows:** 14  ·  **Columns:** 24
- **Primary key:** `frame_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `frame_id` | TEXT | ✓ | ✓ |  |
| `frame_name` | TEXT |  | ✓ |  |
| `lifecycle_phase` | TEXT |  | ✓ |  |
| `frame_type` | TEXT |  | ✓ |  |
| `tier` | INTEGER |  | ✓ |  |
| `required_fields` | TEXT |  | ✓ | `'[]'` |
| `fallback_frame` | TEXT |  |  |  |
| `channel` | TEXT |  |  |  |
| `step_in_sequence` | INTEGER |  |  |  |
| `description` | TEXT |  |  |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |
| `cid_compilation_rule` | TEXT |  |  |  |
| `sid_template_id` | TEXT |  |  |  |
| `mid_sequence_type` | TEXT |  |  |  |
| `mid_delay_hours` | INTEGER |  |  |  |
| `mid_max_attempts` | INTEGER |  |  | `3` |
| `sequence_id` | TEXT |  |  | `'SEQ-COLD-EMAIL-V1'` |
| `target_role` | TEXT |  |  | `'ALL'` |
| `voice_id` | TEXT |  |  | `'VCE-BARTON-ALL'` |
| `subject_line_template` | TEXT |  |  |  |
| `body_template` | TEXT |  |  |  |
| `notes` | TEXT |  |  |  |

### `lcs_frame_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 8  ·  **Columns:** 16
- **Primary key:** `frame_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `frame_id` | TEXT | ✓ |  |  |
| `frame_name` | TEXT |  | ✓ |  |
| `lifecycle_phase` | TEXT |  | ✓ | `'OUTREACH'` |
| `frame_type` | TEXT |  | ✓ | `'cold_email'` |
| `tier` | INTEGER |  | ✓ | `5` |
| `channel` | TEXT |  | ✓ | `'MG'` |
| `step_in_sequence` | INTEGER |  |  | `1` |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |
| `sequence_id` | TEXT |  |  | `'SEQ-COLD-EMAIL-V1'` |
| `target_role` | TEXT |  |  | `'ALL'` |
| `voice_id` | TEXT |  |  | `'VCE-BARTON-ALL'` |
| `subject_line_template` | TEXT |  |  |  |
| `body_template` | TEXT |  |  |  |
| `notes` | TEXT |  |  |  |

### `lcs_m_registry`

- **DB:** `svg-d1-spine`  ·  **Rows:** 37  ·  **Columns:** 17
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | TEXT | ✓ |  |  |
| `name` | TEXT |  | ✓ |  |
| `abbreviation` | TEXT |  |  | `NULL` |
| `description` | TEXT |  | ✓ |  |
| `category` | TEXT |  | ✓ |  |
| `primitive` | TEXT |  | ✓ |  |
| `ctb_placement` | TEXT |  | ✓ | `'Leaf'` |
| `imo_topology` | TEXT |  |  | `NULL` |
| `format` | TEXT |  |  | `NULL` |
| `current_value` | TEXT |  |  | `NULL` |
| `source` | TEXT |  |  | `NULL` |
| `source_detail` | TEXT |  |  | `NULL` |
| `status` | TEXT |  | ✓ | `'active'` |
| `locked` | INTEGER |  | ✓ | `1` |
| `last_verified` | TEXT |  |  | `NULL` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_m_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 37  ·  **Columns:** 17
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | TEXT | ✓ |  |  |
| `name` | TEXT |  | ✓ |  |
| `abbreviation` | TEXT |  |  | `NULL` |
| `description` | TEXT |  | ✓ |  |
| `category` | TEXT |  | ✓ |  |
| `primitive` | TEXT |  | ✓ |  |
| `ctb_placement` | TEXT |  | ✓ | `'Leaf'` |
| `imo_topology` | TEXT |  |  | `NULL` |
| `format` | TEXT |  |  | `NULL` |
| `current_value` | TEXT |  |  | `NULL` |
| `source` | TEXT |  |  | `NULL` |
| `source_detail` | TEXT |  |  | `NULL` |
| `status` | TEXT |  | ✓ | `'active'` |
| `locked` | INTEGER |  | ✓ | `1` |
| `last_verified` | TEXT |  |  | `NULL` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_message_error`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 8
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ | ✓ |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `lcs_id` | TEXT |  |  |  |
| `source_stage` | TEXT |  | ✓ |  |
| `cid` | TEXT |  |  |  |
| `error_code` | TEXT |  | ✓ |  |
| `payload` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_message_ledger`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 18
- **Primary key:** `mid`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `mid` | TEXT | ✓ | ✓ |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `lcs_id` | TEXT |  | ✓ |  |
| `source_stage` | TEXT |  | ✓ |  |
| `source_cid_table` | TEXT |  | ✓ |  |
| `cid` | TEXT |  | ✓ |  |
| `channel` | TEXT |  | ✓ |  |
| `provider` | TEXT |  | ✓ |  |
| `sender_profile_id` | TEXT |  | ✓ |  |
| `payload_hash` | TEXT |  | ✓ |  |
| `status` | TEXT |  | ✓ |  |
| `provider_message_id` | TEXT |  |  |  |
| `attempt_number` | INTEGER |  | ✓ | `1` |
| `ready_at` | TEXT |  |  |  |
| `sent_at` | TEXT |  |  |  |
| `last_error_at` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_mid_sequence_state`

- **DB:** `svg-d1-spine`  ·  **Rows:** 3404  ·  **Columns:** 15
- **Primary key:** `mid_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `mid_id` | TEXT | ✓ | ✓ |  |
| `message_run_id` | TEXT |  | ✓ |  |
| `communication_id` | TEXT |  | ✓ |  |
| `adapter_type` | TEXT |  | ✓ |  |
| `channel` | TEXT |  | ✓ |  |
| `sequence_position` | INTEGER |  | ✓ |  |
| `attempt_number` | INTEGER |  | ✓ | `1` |
| `gate_verdict` | TEXT |  | ✓ |  |
| `gate_reason` | TEXT |  |  |  |
| `throttle_status` | TEXT |  |  |  |
| `delivery_status` | TEXT |  | ✓ | `'PENDING'` |
| `scheduled_at` | TEXT |  |  |  |
| `attempted_at` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `recipient_email` | TEXT |  |  |  |

### `lcs_sender_profile_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 10
- **Primary key:** `sender_profile_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sender_profile_id` | TEXT | ✓ | ✓ |  |
| `stage` | TEXT |  | ✓ |  |
| `channel` | TEXT |  | ✓ |  |
| `provider` | TEXT |  | ✓ |  |
| `from_address` | TEXT |  |  |  |
| `reply_to_address` | TEXT |  |  |  |
| `display_name` | TEXT |  |  |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_sequence_def`

- **DB:** `svg-d1-spine`  ·  **Rows:** 5  ·  **Columns:** 8
- **Primary key:** `sequence_id`, `step_number`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sequence_id` | TEXT | ✓ | ✓ |  |
| `step_number` | INTEGER | ✓ | ✓ |  |
| `frame_id` | TEXT |  | ✓ |  |
| `channel` | TEXT |  | ✓ | `'MG'` |
| `delay_hours` | INTEGER |  | ✓ | `0` |
| `condition` | TEXT |  |  | `NULL` |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_sequence_def`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 5  ·  **Columns:** 8
- **Primary key:** `sequence_id`, `step_number`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sequence_id` | TEXT | ✓ | ✓ |  |
| `step_number` | INTEGER | ✓ | ✓ |  |
| `frame_id` | TEXT |  | ✓ |  |
| `channel` | TEXT |  | ✓ | `'MG'` |
| `delay_hours` | INTEGER |  | ✓ | `0` |
| `condition` | TEXT |  |  | `NULL` |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_sid_output`

- **DB:** `svg-d1-spine`  ·  **Rows:** 3617  ·  **Columns:** 14
- **Primary key:** `sid_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sid_id` | TEXT | ✓ | ✓ |  |
| `communication_id` | TEXT |  | ✓ |  |
| `frame_id` | TEXT |  | ✓ |  |
| `template_id` | TEXT |  |  |  |
| `subject_line` | TEXT |  |  |  |
| `body_plain` | TEXT |  |  |  |
| `body_html` | TEXT |  |  |  |
| `sender_identity` | TEXT |  |  |  |
| `sender_email` | TEXT |  |  |  |
| `recipient_email` | TEXT |  |  |  |
| `recipient_name` | TEXT |  |  |  |
| `construction_status` | TEXT |  | ✓ |  |
| `construction_reason` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_signal_queue`

- **DB:** `svg-d1-spine`  ·  **Rows:** 4506  ·  **Columns:** 15
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | TEXT | ✓ | ✓ |  |
| `signal_set_hash` | TEXT |  | ✓ |  |
| `signal_category` | TEXT |  | ✓ |  |
| `sovereign_company_id` | TEXT |  | ✓ |  |
| `lifecycle_phase` | TEXT |  | ✓ |  |
| `preferred_channel` | TEXT |  |  |  |
| `preferred_lane` | TEXT |  |  |  |
| `agent_number` | TEXT |  |  |  |
| `signal_data` | TEXT |  | ✓ | `'{}'` |
| `source_hub` | TEXT |  | ✓ |  |
| `source_signal_id` | TEXT |  |  |  |
| `status` | TEXT |  | ✓ | `'PENDING'` |
| `priority` | INTEGER |  | ✓ | `0` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `processed_at` | TEXT |  |  |  |

### `lcs_signal_registry`

- **DB:** `svg-d1-spine`  ·  **Rows:** 9  ·  **Columns:** 13
- **Primary key:** `signal_set_hash`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `signal_set_hash` | TEXT | ✓ | ✓ |  |
| `signal_name` | TEXT |  | ✓ |  |
| `lifecycle_phase` | TEXT |  | ✓ |  |
| `signal_category` | TEXT |  | ✓ |  |
| `description` | TEXT |  |  |  |
| `data_fetched_at` | TEXT |  |  |  |
| `data_expires_at` | TEXT |  |  |  |
| `freshness_window` | TEXT |  | ✓ | `'30 days'` |
| `signal_validity_score` | REAL |  |  |  |
| `validity_threshold` | REAL |  | ✓ | `0.50` |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_suppression`

- **DB:** `svg-d1-spine`  ·  **Rows:** 261  ·  **Columns:** 4
- **Primary key:** `email`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `email` | TEXT | ✓ |  |  |
| `reason` | TEXT |  | ✓ |  |
| `source_mid_id` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ |  |

### `lcs_voice_library`

- **DB:** `svg-d1-spine`  ·  **Rows:** 4  ·  **Columns:** 11
- **Primary key:** `voice_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `voice_id` | TEXT | ✓ |  |  |
| `voice_name` | TEXT |  | ✓ |  |
| `target_role` | TEXT |  | ✓ |  |
| `tone` | TEXT |  | ✓ |  |
| `style_rules` | TEXT |  | ✓ |  |
| `forbidden_phrases` | TEXT |  | ✓ |  |
| `opening_patterns` | TEXT |  | ✓ |  |
| `closing_patterns` | TEXT |  | ✓ |  |
| `proof_points` | TEXT |  | ✓ |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `lcs_voice_library`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 4  ·  **Columns:** 11
- **Primary key:** `voice_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `voice_id` | TEXT | ✓ |  |  |
| `voice_name` | TEXT |  | ✓ |  |
| `target_role` | TEXT |  | ✓ |  |
| `tone` | TEXT |  | ✓ |  |
| `style_rules` | TEXT |  | ✓ |  |
| `forbidden_phrases` | TEXT |  | ✓ |  |
| `opening_patterns` | TEXT |  | ✓ |  |
| `closing_patterns` | TEXT |  | ✓ |  |
| `proof_points` | TEXT |  | ✓ |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

## 200-people-worker

### `intake_people_staging`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 15
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ |  |  |
| `source_url_id` | TEXT |  |  |  |
| `company_unique_id` | TEXT |  | ✓ |  |
| `raw_name` | TEXT |  |  |  |
| `first_name` | TEXT |  |  |  |
| `last_name` | TEXT |  |  |  |
| `raw_title` | TEXT |  |  |  |
| `normalized_title` | TEXT |  |  |  |
| `mapped_slot_type` | TEXT |  |  |  |
| `linkedin_url` | TEXT |  |  |  |
| `email` | TEXT |  |  |  |
| `confidence_score` | REAL |  |  |  |
| `status` | TEXT |  |  | `'pending'` |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `processed_at` | TEXT |  |  |  |

### `outreach_people`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 20

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `person_id` | TEXT |  | ✓ |  |
| `target_id` | TEXT |  | ✓ |  |
| `company_unique_id` | TEXT |  | ✓ |  |
| `slot_type` | TEXT |  |  |  |
| `email` | TEXT |  | ✓ |  |
| `email_verified` | INTEGER |  | ✓ |  |
| `email_verified_at` | TEXT |  |  |  |
| `contact_status` | TEXT |  | ✓ |  |
| `lifecycle_state` | TEXT |  | ✓ |  |
| `funnel_membership` | TEXT |  | ✓ |  |
| `email_open_count` | INTEGER |  | ✓ |  |
| `email_click_count` | INTEGER |  | ✓ |  |
| `email_reply_count` | INTEGER |  | ✓ |  |
| `current_bit_score` | INTEGER |  | ✓ |  |
| `last_event_ts` | TEXT |  |  |  |
| `last_state_change_ts` | TEXT |  |  |  |
| `source` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ |  |
| `updated_at` | TEXT |  | ✓ |  |
| `outreach_id` | TEXT |  |  |  |

### `people_company_slot`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 98106  ·  **Columns:** 14
- **Primary key:** `slot_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `slot_id` | TEXT | ✓ | ✓ |  |
| `outreach_id` | TEXT |  | ✓ |  |
| `company_unique_id` | TEXT |  | ✓ |  |
| `slot_type` | TEXT |  | ✓ |  |
| `person_unique_id` | TEXT |  |  |  |
| `is_filled` | INTEGER |  |  | `0` |
| `filled_at` | TEXT |  |  |  |
| `confidence_score` | REAL |  |  |  |
| `source_system` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |
| `slot_phone` | TEXT |  |  |  |
| `slot_phone_source` | TEXT |  |  |  |
| `slot_phone_updated_at` | TEXT |  |  |  |

### `people_people_master`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 57667  ·  **Columns:** 36
- **Primary key:** `unique_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `unique_id` | TEXT | ✓ | ✓ |  |
| `company_unique_id` | TEXT |  | ✓ |  |
| `company_slot_unique_id` | TEXT |  | ✓ |  |
| `first_name` | TEXT |  | ✓ |  |
| `last_name` | TEXT |  | ✓ |  |
| `full_name` | TEXT |  |  |  |
| `title` | TEXT |  |  |  |
| `seniority` | TEXT |  |  |  |
| `department` | TEXT |  |  |  |
| `email` | TEXT |  |  |  |
| `work_phone_e164` | TEXT |  |  |  |
| `personal_phone_e164` | TEXT |  |  |  |
| `linkedin_url` | TEXT |  |  |  |
| `twitter_url` | TEXT |  |  |  |
| `facebook_url` | TEXT |  |  |  |
| `bio` | TEXT |  |  |  |
| `skills` | TEXT |  |  |  |
| `education` | TEXT |  |  |  |
| `certifications` | TEXT |  |  |  |
| `source_system` | TEXT |  | ✓ |  |
| `source_record_id` | TEXT |  |  |  |
| `promoted_from_intake_at` | TEXT |  | ✓ | `datetime('now')` |
| `promotion_audit_log_id` | INTEGER |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |
| `email_verified` | INTEGER |  |  | `0` |
| `message_key_scheduled` | TEXT |  |  |  |
| `email_verification_source` | TEXT |  |  |  |
| `email_verified_at` | TEXT |  |  |  |
| `validation_status` | TEXT |  |  |  |
| `last_verified_at` | TEXT |  | ✓ | `datetime('now')` |
| `last_enrichment_attempt` | TEXT |  |  |  |
| `is_decision_maker` | INTEGER |  |  | `0` |
| `outreach_ready` | INTEGER |  |  | `0` |
| `outreach_ready_at` | TEXT |  |  |  |
| `source_url` | TEXT |  |  |  |

### `people_slot_ingress_control`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 1  ·  **Columns:** 9
- **Primary key:** `switch_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `switch_id` | TEXT | ✓ | ✓ |  |
| `switch_name` | TEXT |  | ✓ |  |
| `is_enabled` | INTEGER |  | ✓ | `0` |
| `description` | TEXT |  |  |  |
| `enabled_by` | TEXT |  |  |  |
| `enabled_at` | TEXT |  |  |  |
| `disabled_by` | TEXT |  |  |  |
| `disabled_at` | TEXT |  |  | `datetime('now')` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `people_title_slot_mapping`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 43  ·  **Columns:** 5
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ |  |  |
| `title_pattern` | TEXT |  | ✓ |  |
| `slot_type` | TEXT |  | ✓ |  |
| `priority` | INTEGER |  |  | `50` |
| `created_at` | TEXT |  |  | `datetime('now')` |

### `slot_workbench`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 101559  ·  **Columns:** 100
- **Primary key:** `slot_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `slot_id` | TEXT | ✓ |  |  |
| `outreach_id` | TEXT |  | ✓ |  |
| `company_unique_id` | TEXT |  |  |  |
| `slot_type` | TEXT |  | ✓ |  |
| `is_filled` | INTEGER |  |  | `0` |
| `person_unique_id` | TEXT |  |  |  |
| `city` | TEXT |  |  |  |
| `state` | TEXT |  |  |  |
| `postal_code` | TEXT |  |  |  |
| `industry` | TEXT |  |  |  |
| `employees` | INTEGER |  |  |  |
| `service_agents` | TEXT |  |  |  |
| `agent_count` | INTEGER |  |  |  |
| `company_name` | TEXT |  |  |  |
| `company_domain` | TEXT |  |  |  |
| `canonical_name` | TEXT |  |  |  |
| `domain` | TEXT |  |  |  |
| `ein` | TEXT |  |  |  |
| `has_appointment` | INTEGER |  |  | `0` |
| `filing_present` | INTEGER |  |  |  |
| `funding_type` | TEXT |  |  |  |
| `carrier` | TEXT |  |  |  |
| `broker_or_advisor` | TEXT |  |  |  |
| `renewal_month` | INTEGER |  |  |  |
| `about_url` | TEXT |  |  |  |
| `blog_source_url` | TEXT |  |  |  |
| `hunter_email_pattern` | TEXT |  |  |  |
| `vendor_email_pattern` | TEXT |  |  |  |
| `company_phone` | TEXT |  |  |  |
| `person_first_name` | TEXT |  |  |  |
| `person_last_name` | TEXT |  |  |  |
| `person_full_name` | TEXT |  |  |  |
| `person_email` | TEXT |  |  |  |
| `person_email_verified` | INTEGER |  |  |  |
| `person_linkedin` | TEXT |  |  |  |
| `person_source` | TEXT |  |  |  |
| `hunter_contact_id` | INTEGER |  |  |  |
| `hunter_first_name` | TEXT |  |  |  |
| `hunter_last_name` | TEXT |  |  |  |
| `hunter_email` | TEXT |  |  |  |
| `hunter_confidence` | INTEGER |  |  |  |
| `hunter_linkedin` | TEXT |  |  |  |
| `hunter_phone` | TEXT |  |  |  |
| `hunter_title` | TEXT |  |  |  |
| `has_name` | INTEGER |  |  | `0` |
| `has_email` | INTEGER |  |  | `0` |
| `has_verified_email` | INTEGER |  |  | `0` |
| `has_linkedin` | INTEGER |  |  | `0` |
| `has_hunter_candidate` | INTEGER |  |  | `0` |
| `has_email_pattern` | INTEGER |  |  | `0` |
| `readiness_tier` | TEXT |  | ✓ |  |
| `last_recon_at` | TEXT |  |  |  |
| `person_found_at` | TEXT |  |  |  |
| `email_found_at` | TEXT |  |  |  |
| `linkedin_found_at` | TEXT |  |  |  |
| `email_verified_at` | TEXT |  |  |  |
| `recon_linkedin_people` | TEXT |  |  |  |
| `recon_linkedin_company` | TEXT |  |  |  |
| `recon_emails` | TEXT |  |  |  |
| `recon_name_titles` | TEXT |  |  |  |
| `recon_result_urls` | TEXT |  |  |  |
| `recon_snippets` | TEXT |  |  |  |
| `recon_result_count` | INTEGER |  |  |  |
| `recon_organized_people` | TEXT |  |  | `NULL` |
| `recon_organized_linkedin` | TEXT |  |  | `NULL` |
| `recon_organized_garbage` | TEXT |  |  | `NULL` |
| `recon_platform_urls` | TEXT |  |  | `NULL` |
| `sp_baseline_at` | TEXT |  |  |  |
| `sp_changed_at` | TEXT |  |  |  |
| `people_baseline_at` | TEXT |  |  |  |
| `people_changed_at` | TEXT |  |  |  |
| `dol_baseline_at` | TEXT |  |  |  |
| `dol_changed_at` | TEXT |  |  |  |
| `ct_baseline_at` | TEXT |  |  |  |
| `ct_changed_at` | TEXT |  |  |  |
| `people_checked` | INTEGER |  |  | `0` |
| `people_changed` | INTEGER |  |  | `0` |
| `sp_checked` | INTEGER |  |  | `0` |
| `sp_changed` | INTEGER |  |  | `0` |
| `name_last_checked_at` | TEXT |  |  |  |
| `name_changed` | INTEGER |  |  | `0` |
| `email_last_checked_at` | TEXT |  |  |  |
| `email_changed` | INTEGER |  |  | `0` |
| `verified_last_checked_at` | TEXT |  |  |  |
| `verified_changed` | INTEGER |  |  | `0` |
| `linkedin_last_checked_at` | TEXT |  |  |  |
| `linkedin_changed` | INTEGER |  |  | `0` |
| `sp_has_glassdoor` | INTEGER |  |  | `0` |
| `sp_glassdoor_url` | TEXT |  |  |  |
| `sp_glassdoor_last_checked_at` | TEXT |  |  |  |
| `sp_glassdoor_changed` | INTEGER |  |  | `0` |
| `sp_has_indeed` | INTEGER |  |  | `0` |
| `sp_indeed_url` | TEXT |  |  |  |
| `sp_indeed_last_checked_at` | TEXT |  |  |  |
| `sp_indeed_changed` | INTEGER |  |  | `0` |
| `sp_has_facebook` | INTEGER |  |  | `0` |
| `sp_facebook_url` | TEXT |  |  |  |
| `sp_facebook_last_checked_at` | TEXT |  |  |  |
| `sp_facebook_changed` | INTEGER |  |  | `0` |
| `sp_has_twitter` | INTEGER |  |  | `0` |

## 201-email-discovery

### `enrichment_hunter_company`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 15537  ·  **Columns:** 23
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ |  |  |
| `outreach_id` | TEXT |  |  |  |
| `company_unique_id` | TEXT |  |  |  |
| `domain` | TEXT |  | ✓ |  |
| `organization` | TEXT |  |  |  |
| `email_pattern` | TEXT |  |  |  |
| `industry` | TEXT |  |  |  |
| `industry_normalized` | TEXT |  |  |  |
| `company_type` | TEXT |  |  |  |
| `headcount` | TEXT |  |  |  |
| `headcount_min` | INTEGER |  |  |  |
| `headcount_max` | INTEGER |  |  |  |
| `country` | TEXT |  |  |  |
| `state` | TEXT |  |  |  |
| `city` | TEXT |  |  |  |
| `postal_code` | TEXT |  |  |  |
| `street` | TEXT |  |  |  |
| `location_full` | TEXT |  |  |  |
| `data_quality_score` | REAL |  |  |  |
| `source` | TEXT |  |  |  |
| `enriched_at` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `updated_at` | TEXT |  |  |  |

### `enrichment_hunter_contact`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 175632  ·  **Columns:** 25
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ |  |  |
| `outreach_id` | TEXT |  | ✓ |  |
| `company_unique_id` | TEXT |  |  |  |
| `domain` | TEXT |  | ✓ |  |
| `first_name` | TEXT |  |  |  |
| `last_name` | TEXT |  |  |  |
| `full_name` | TEXT |  |  |  |
| `email` | TEXT |  |  |  |
| `email_type` | TEXT |  |  |  |
| `email_verified` | INTEGER |  |  | `0` |
| `confidence_score` | INTEGER |  |  |  |
| `job_title` | TEXT |  |  |  |
| `title_normalized` | TEXT |  |  |  |
| `seniority_level` | TEXT |  |  |  |
| `department` | TEXT |  |  |  |
| `department_normalized` | TEXT |  |  |  |
| `linkedin_url` | TEXT |  |  |  |
| `phone_number` | TEXT |  |  |  |
| `num_sources` | INTEGER |  |  |  |
| `is_decision_maker` | INTEGER |  |  | `0` |
| `outreach_priority` | INTEGER |  |  |  |
| `data_quality_score` | REAL |  |  |  |
| `source` | TEXT |  |  |  |
| `source_file` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |

### `vendor_ct`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 18683  ·  **Columns:** 31
- **Primary key:** `vendor_row_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `vendor_row_id` | INTEGER | ✓ |  |  |
| `outreach_id` | TEXT |  |  |  |
| `company_unique_id` | TEXT |  |  |  |
| `domain` | TEXT |  |  |  |
| `company_name` | TEXT |  |  |  |
| `email_pattern` | TEXT |  |  |  |
| `email_pattern_confidence` | INTEGER |  |  |  |
| `email_pattern_source` | TEXT |  |  |  |
| `email_pattern_verified_at` | TEXT |  |  |  |
| `company_phone` | TEXT |  |  |  |
| `company_type` | TEXT |  |  |  |
| `employee_count` | INTEGER |  |  |  |
| `industry` | TEXT |  |  |  |
| `industry_normalized` | TEXT |  |  |  |
| `description` | TEXT |  |  |  |
| `city` | TEXT |  |  |  |
| `state` | TEXT |  |  |  |
| `country` | TEXT |  |  |  |
| `postal_code` | TEXT |  |  |  |
| `linkedin_url` | TEXT |  |  |  |
| `facebook_url` | TEXT |  |  |  |
| `twitter_url` | TEXT |  |  |  |
| `ein` | TEXT |  |  |  |
| `duns` | TEXT |  |  |  |
| `source_system` | TEXT |  |  |  |
| `enriched_by` | TEXT |  |  |  |
| `data_quality_score` | REAL |  |  |  |
| `enriched_at` | TEXT |  |  |  |
| `source_table` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `updated_at` | TEXT |  |  |  |

### `vendor_people`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 175632  ·  **Columns:** 34
- **Primary key:** `vendor_row_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `vendor_row_id` | INTEGER | ✓ |  |  |
| `outreach_id` | TEXT |  |  |  |
| `company_unique_id` | TEXT |  |  |  |
| `domain` | TEXT |  |  |  |
| `first_name` | TEXT |  |  |  |
| `last_name` | TEXT |  |  |  |
| `full_name` | TEXT |  |  |  |
| `email` | TEXT |  |  |  |
| `email_type` | TEXT |  |  |  |
| `email_verified` | INTEGER |  |  | `0` |
| `confidence_score` | REAL |  |  |  |
| `job_title` | TEXT |  |  |  |
| `title_normalized` | TEXT |  |  |  |
| `seniority_level` | TEXT |  |  |  |
| `department` | TEXT |  |  |  |
| `department_normalized` | TEXT |  |  |  |
| `mapped_slot_type` | TEXT |  |  |  |
| `linkedin_url` | TEXT |  |  |  |
| `phone_number` | TEXT |  |  |  |
| `work_phone` | TEXT |  |  |  |
| `personal_phone` | TEXT |  |  |  |
| `num_sources` | INTEGER |  |  |  |
| `is_decision_maker` | INTEGER |  |  | `0` |
| `company_name` | TEXT |  |  |  |
| `city` | TEXT |  |  |  |
| `state` | TEXT |  |  |  |
| `country` | TEXT |  |  |  |
| `source_system` | TEXT |  |  |  |
| `backfill_source` | TEXT |  |  |  |
| `enriched_by` | TEXT |  |  |  |
| `data_quality_score` | REAL |  |  |  |
| `source_table` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `updated_at` | TEXT |  |  |  |

## 300-blog-worker

### `outreach_blog`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 32702  ·  **Columns:** 13

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `blog_id` | TEXT |  | ✓ |  |
| `outreach_id` | TEXT |  | ✓ |  |
| `context_summary` | TEXT |  |  |  |
| `source_type` | TEXT |  |  |  |
| `source_url` | TEXT |  |  |  |
| `context_timestamp` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `source_type_enum` | TEXT |  |  |  |
| `about_url` | TEXT |  |  |  |
| `news_url` | TEXT |  |  |  |
| `extraction_method` | TEXT |  |  |  |
| `last_extracted_at` | TEXT |  |  |  |
| `updated_at` | TEXT |  |  |  |

### `outreach_blog_ingress_control`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 1  ·  **Columns:** 14
- **Primary key:** `control_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `control_id` | TEXT | ✓ | ✓ |  |
| `enabled` | INTEGER |  | ✓ | `0` |
| `enabled_at` | TEXT |  |  |  |
| `enabled_by` | TEXT |  |  |  |
| `disabled_at` | TEXT |  |  |  |
| `disabled_by` | TEXT |  |  |  |
| `max_urls_per_hour` | INTEGER |  |  | `100` |
| `max_urls_per_company` | INTEGER |  |  | `10` |
| `url_ttl_days` | INTEGER |  |  | `30` |
| `content_ttl_days` | INTEGER |  |  | `7` |
| `notes` | TEXT |  |  |  |
| `singleton_key` | INTEGER |  |  | `1` |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

## 301-page-parser

### `page_raw_html`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 22928  ·  **Columns:** 8
- **Primary key:** `outreach_id`, `page_url`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `outreach_id` | TEXT | ✓ | ✓ |  |
| `page_url` | TEXT | ✓ | ✓ |  |
| `source` | TEXT |  | ✓ | `'about_url'` |
| `fetch_status` | INTEGER |  |  |  |
| `html_length` | INTEGER |  |  | `0` |
| `raw_html` | TEXT |  |  |  |
| `fetched_at` | TEXT |  | ✓ | `datetime('now')` |
| `key_built` | INTEGER |  | ✓ | `0` |

## 500-talent-flow

### `outreach_appointments`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 487  ·  **Columns:** 22

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `appointment_id` | TEXT |  | ✓ |  |
| `outreach_id` | TEXT |  |  |  |
| `domain` | TEXT |  |  |  |
| `prospect_keycode_id` | INTEGER |  |  |  |
| `appt_number` | TEXT |  |  |  |
| `appt_date` | TEXT |  |  |  |
| `contact_first_name` | TEXT |  |  |  |
| `contact_last_name` | TEXT |  |  |  |
| `contact_title` | TEXT |  |  |  |
| `contact_email` | TEXT |  |  |  |
| `contact_phone` | TEXT |  |  |  |
| `company_name` | TEXT |  | ✓ |  |
| `address_1` | TEXT |  |  |  |
| `address_2` | TEXT |  |  |  |
| `city` | TEXT |  |  |  |
| `state` | TEXT |  |  |  |
| `zip` | TEXT |  |  |  |
| `county` | TEXT |  |  |  |
| `notes` | TEXT |  |  |  |
| `source_file` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `updated_at` | TEXT |  |  |  |

## 600-bit-scoring

### `outreach_bit_scores`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 7002  ·  **Columns:** 12

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `outreach_id` | TEXT |  | ✓ |  |
| `score` | REAL |  | ✓ |  |
| `score_tier` | TEXT |  | ✓ |  |
| `signal_count` | INTEGER |  | ✓ |  |
| `people_score` | REAL |  | ✓ |  |
| `dol_score` | REAL |  | ✓ |  |
| `blog_score` | REAL |  | ✓ |  |
| `talent_flow_score` | REAL |  | ✓ |  |
| `last_signal_at` | TEXT |  |  |  |
| `last_scored_at` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ |  |
| `updated_at` | TEXT |  | ✓ |  |

## 700-campaign-engine

### `outreach_ctx_context`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 4
- **Primary key:** `outreach_context_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `outreach_context_id` | TEXT | ✓ | ✓ |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `status` | TEXT |  | ✓ |  |
| `notes` | TEXT |  |  |  |

## 810-client-intake

### `clnt_client`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 17
- **Primary key:** `client_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `client_id` | TEXT | ✓ | ✓ |  |
| `legal_name` | TEXT |  | ✓ |  |
| `fein` | TEXT |  |  |  |
| `domicile_state` | TEXT |  |  |  |
| `effective_date` | TEXT |  |  |  |
| `status` | TEXT |  | ✓ | `'active'` |
| `source` | TEXT |  |  |  |
| `version` | INTEGER |  | ✓ | `1` |
| `domain` | TEXT |  |  |  |
| `label_override` | TEXT |  |  |  |
| `logo_url` | TEXT |  |  |  |
| `color_primary` | TEXT |  |  |  |
| `color_accent` | TEXT |  |  |  |
| `feature_flags` | TEXT |  | ✓ | `'{}'` |
| `dashboard_blocks` | TEXT |  | ✓ | `'[]'` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

## 830-client-portal

### `client_grid`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 15
- **Primary key:** `client_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `client_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `p300_doc_1` | INTEGER |  |  | `0` |
| `p300_doc_1_date` | TEXT |  |  |  |
| `p301_doc_2` | INTEGER |  |  | `0` |
| `p301_doc_2_date` | TEXT |  |  |  |
| `p302_doc_3` | INTEGER |  |  | `0` |
| `p302_doc_3_date` | TEXT |  |  |  |
| `p303_doc_4` | INTEGER |  |  | `0` |
| `p303_doc_4_date` | TEXT |  |  |  |
| `p304_doc_5` | INTEGER |  |  | `0` |
| `p304_doc_5_date` | TEXT |  |  |  |
| `orbt_state` | TEXT |  |  | `'OPERATE'` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

## 900-sales-portal

### `sales_appointments_already_had`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 12
- **Primary key:** `appointment_uid`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `appointment_uid` | TEXT | ✓ | ✓ |  |
| `company_id` | TEXT |  |  |  |
| `people_id` | TEXT |  |  |  |
| `outreach_id` | TEXT |  |  |  |
| `meeting_date` | TEXT |  | ✓ |  |
| `meeting_type` | TEXT |  | ✓ |  |
| `meeting_outcome` | TEXT |  | ✓ |  |
| `stalled_reason` | TEXT |  |  |  |
| `source` | TEXT |  | ✓ |  |
| `source_record_id` | TEXT |  |  |  |
| `metadata` | TEXT |  |  | `'{}'` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `sales_grid`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 17
- **Primary key:** `sales_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sales_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `p200_meeting_1` | INTEGER |  |  | `0` |
| `p200_meeting_1_date` | TEXT |  |  |  |
| `p200_meeting_1_notes` | TEXT |  |  |  |
| `p201_meeting_2` | INTEGER |  |  | `0` |
| `p201_meeting_2_date` | TEXT |  |  |  |
| `p201_meeting_2_notes` | TEXT |  |  |  |
| `p202_meeting_3` | INTEGER |  |  | `0` |
| `p202_meeting_3_date` | TEXT |  |  |  |
| `p202_meeting_3_notes` | TEXT |  |  |  |
| `p203_meeting_4` | INTEGER |  |  | `0` |
| `p203_meeting_4_date` | TEXT |  |  |  |
| `p203_meeting_4_notes` | TEXT |  |  |  |
| `orbt_state` | TEXT |  |  | `'OPERATE'` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `sales_sales_state`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 9
- **Primary key:** `sales_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sales_id` | TEXT | ✓ | ✓ |  |
| `legal_name` | TEXT |  | ✓ |  |
| `domicile_state` | TEXT |  |  |  |
| `current_phase` | TEXT |  | ✓ | `'factfinder'` |
| `status` | TEXT |  | ✓ | `'active'` |
| `source` | TEXT |  |  |  |
| `version` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `sales_sales_state_error`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 10
- **Primary key:** `sales_state_error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sales_state_error_id` | TEXT | ✓ | ✓ |  |
| `sales_id` | TEXT |  |  |  |
| `source_entity` | TEXT |  | ✓ |  |
| `source_id` | TEXT |  |  |  |
| `error_code` | TEXT |  | ✓ |  |
| `error_message` | TEXT |  | ✓ |  |
| `severity` | TEXT |  | ✓ | `'error'` |
| `status` | TEXT |  | ✓ | `'open'` |
| `context` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

## <cloudflare internal>

### `_cf_KV`

- **DB:** `svg-d1-spine`  ·  **Rows:** ?  ·  **Columns:** 0

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|

### `_cf_KV`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** ?  ·  **Columns:** 0

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|

## <governance: error spine>

### `error_log`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ |  |  |
| `work_order_id` | TEXT |  | ✓ |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `branch` | TEXT |  | ✓ |  |
| `process_id` | TEXT |  | ✓ |  |
| `process_name` | TEXT |  |  |  |
| `error_type` | TEXT |  |  |  |
| `strike_count` | INTEGER |  |  | `1` |
| `resolution` | TEXT |  |  |  |
| `resolved_at` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |

### `escalation`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 27
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | TEXT | ✓ |  | `lower(hex(randomblob(16)))` |
| `master_error_id` | TEXT |  | ✓ |  |
| `hub_id` | TEXT |  | ✓ |  |
| `sub_hub` | TEXT |  |  |  |
| `component` | TEXT |  |  |  |
| `process_id` | TEXT |  |  |  |
| `sovereign_company_id` | TEXT |  |  |  |
| `communication_id` | TEXT |  |  |  |
| `strike_count` | INTEGER |  | ✓ | `3` |
| `error_type` | TEXT |  | ✓ |  |
| `error_pattern` | TEXT |  |  |  |
| `first_occurrence` | TEXT |  |  |  |
| `last_occurrence` | TEXT |  |  |  |
| `root_cause` | TEXT |  |  |  |
| `troubleshoot_notes` | TEXT |  |  |  |
| `fix_applied` | TEXT |  |  |  |
| `sop_updated` | INTEGER |  |  | `0` |
| `sop_reference` | TEXT |  |  |  |
| `fleet_directive` | INTEGER |  |  | `0` |
| `fleet_directive_desc` | TEXT |  |  |  |
| `status` | TEXT |  | ✓ | `'OPEN'` |
| `priority` | TEXT |  |  | `'HIGH'` |
| `auditor_approved` | INTEGER |  |  |  |
| `auditor_notes` | TEXT |  |  |  |
| `escalated_at` | TEXT |  |  | `datetime('now')` |
| `resolved_at` | TEXT |  |  |  |
| `signed_off_at` | TEXT |  |  |  |

### `master_error`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 26
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | TEXT | ✓ |  | `lower(hex(randomblob(16)))` |
| `hub_id` | TEXT |  | ✓ |  |
| `sub_hub` | TEXT |  |  |  |
| `component` | TEXT |  |  |  |
| `process_id` | TEXT |  |  |  |
| `process_number` | TEXT |  |  |  |
| `sovereign_company_id` | TEXT |  |  |  |
| `communication_id` | TEXT |  |  |  |
| `message_run_id` | TEXT |  |  |  |
| `signal_queue_id` | TEXT |  |  |  |
| `error_type` | TEXT |  | ✓ |  |
| `error_severity` | TEXT |  | ✓ | `'ERROR'` |
| `error_message` | TEXT |  | ✓ |  |
| `error_context` | TEXT |  |  |  |
| `orbt_mode` | TEXT |  | ✓ | `'REPAIR'` |
| `strike_number` | INTEGER |  |  | `1` |
| `orbt_action_taken` | TEXT |  |  |  |
| `tier0_gate` | TEXT |  |  |  |
| `tier0_validator` | TEXT |  |  |  |
| `resolved` | INTEGER |  |  | `0` |
| `resolved_at` | TEXT |  |  |  |
| `resolved_by` | TEXT |  |  |  |
| `resolution_notes` | TEXT |  |  |  |
| `source_worker` | TEXT |  |  |  |
| `environment` | TEXT |  |  | `'production'` |
| `created_at` | TEXT |  |  | `datetime('now')` |

## <governance: schema catalog — BAR-434>

### `catalog_columns`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 725  ·  **Columns:** 27
- **Primary key:** `column_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `column_id` | TEXT | ✓ | ✓ |  |
| `table_id` | TEXT |  | ✓ |  |
| `column_name` | TEXT |  | ✓ |  |
| `ordinal_position` | INTEGER |  |  |  |
| `data_type` | TEXT |  | ✓ |  |
| `max_length` | INTEGER |  |  |  |
| `is_nullable` | INTEGER |  |  | `1` |
| `default_value` | TEXT |  |  |  |
| `description` | TEXT |  | ✓ |  |
| `business_name` | TEXT |  |  |  |
| `business_definition` | TEXT |  |  |  |
| `format_pattern` | TEXT |  |  |  |
| `format_example` | TEXT |  |  |  |
| `valid_values` | TEXT |  |  |  |
| `validation_rule` | TEXT |  |  |  |
| `is_primary_key` | INTEGER |  |  | `0` |
| `is_foreign_key` | INTEGER |  |  | `0` |
| `references_column` | TEXT |  |  |  |
| `pii_classification` | TEXT |  |  |  |
| `data_sensitivity` | TEXT |  |  |  |
| `source_system` | TEXT |  |  |  |
| `source_field` | TEXT |  |  |  |
| `transformation_logic` | TEXT |  |  |  |
| `tags` | TEXT |  |  |  |
| `synonyms` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `catalog_schemas`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 6  ·  **Columns:** 8
- **Primary key:** `schema_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `schema_id` | TEXT | ✓ | ✓ |  |
| `schema_name` | TEXT |  | ✓ |  |
| `schema_type` | TEXT |  | ✓ |  |
| `description` | TEXT |  | ✓ |  |
| `parent_schema` | TEXT |  |  |  |
| `owner` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `catalog_tables`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 31  ·  **Columns:** 15
- **Primary key:** `table_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `table_id` | TEXT | ✓ | ✓ |  |
| `schema_id` | TEXT |  | ✓ |  |
| `table_name` | TEXT |  | ✓ |  |
| `table_type` | TEXT |  | ✓ |  |
| `description` | TEXT |  | ✓ |  |
| `business_purpose` | TEXT |  |  |  |
| `primary_key` | TEXT |  |  |  |
| `foreign_keys` | TEXT |  |  |  |
| `row_count_approx` | INTEGER |  |  |  |
| `data_source` | TEXT |  |  |  |
| `refresh_frequency` | TEXT |  |  |  |
| `owner` | TEXT |  |  |  |
| `tags` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

## <governance: sovereign registry>

### `sovereign_companies`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `sovereign_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `sovereign_id` | TEXT | ✓ |  |  |
| `company_name` | TEXT |  | ✓ |  |
| `ein` | TEXT |  |  |  |
| `state` | TEXT |  |  |  |
| `employee_count` | INTEGER |  |  |  |
| `industry` | TEXT |  |  |  |
| `source` | TEXT |  |  |  |
| `entry_point` | TEXT |  |  |  |
| `orbt_state` | TEXT |  |  | `'OPERATE'` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

## <governance: work orders>

### `work_order_items`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `item_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `item_id` | TEXT | ✓ |  |  |
| `work_order_id` | TEXT |  | ✓ |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `branch` | TEXT |  | ✓ |  |
| `process_id` | TEXT |  | ✓ |  |
| `process_name` | TEXT |  |  |  |
| `status` | TEXT |  |  | `'PENDING'` |
| `completed_at` | TEXT |  |  |  |
| `notes` | TEXT |  |  |  |
| `is_carry_forward` | INTEGER |  |  | `0` |
| `error_log_ref` | TEXT |  |  |  |

### `work_orders`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 8
- **Primary key:** `work_order_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `work_order_id` | TEXT | ✓ |  |  |
| `generated_at` | TEXT |  | ✓ | `datetime('now')` |
| `closed_at` | TEXT |  |  |  |
| `status` | TEXT |  |  | `'OPEN'` |
| `total_items` | INTEGER |  |  | `0` |
| `completed_items` | INTEGER |  |  | `0` |
| `failed_items` | INTEGER |  |  | `0` |
| `cycle` | TEXT |  | ✓ |  |

## <governance>

### `ctb_audit_log`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ | ✓ |  |
| `event_type` | TEXT |  | ✓ |  |
| `table_schema` | TEXT |  |  |  |
| `table_name` | TEXT |  |  |  |
| `operation` | TEXT |  |  |  |
| `process_id` | TEXT |  |  |  |
| `hub_id` | TEXT |  |  |  |
| `subhub_id` | TEXT |  |  |  |
| `details` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `created_by` | TEXT |  | ✓ |  |

### `ctb_batch_audit_log`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 6
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ | ✓ |  |
| `batch_id` | TEXT |  | ✓ |  |
| `old_status` | TEXT |  |  |  |
| `new_status` | TEXT |  | ✓ |  |
| `changed_by` | TEXT |  | ✓ |  |
| `changed_at` | TEXT |  | ✓ | `datetime('now')` |

### `ctb_promotion_paths`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ | ✓ |  |
| `source_schema` | TEXT |  | ✓ | `'public'` |
| `source_table` | TEXT |  | ✓ |  |
| `target_schema` | TEXT |  | ✓ | `'public'` |
| `target_table` | TEXT |  | ✓ |  |
| `hub_id` | TEXT |  | ✓ |  |
| `subhub_id` | TEXT |  | ✓ |  |
| `description` | TEXT |  |  |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `created_by` | TEXT |  | ✓ |  |

### `ctb_raw_batch_registry`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `batch_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `batch_id` | TEXT | ✓ | ✓ |  |
| `bridge_id` | TEXT |  | ✓ |  |
| `vendor_source` | TEXT |  | ✓ |  |
| `bridge_version` | TEXT |  | ✓ |  |
| `target_schema` | TEXT |  | ✓ | `'public'` |
| `target_table` | TEXT |  | ✓ |  |
| `row_count` | INTEGER |  | ✓ | `0` |
| `supersedes_batch_id` | TEXT |  |  |  |
| `status` | TEXT |  | ✓ | `'ACTIVE'` |
| `ingested_at` | TEXT |  | ✓ | `datetime('now')` |
| `ingested_by` | TEXT |  | ✓ |  |

### `ctb_table_registry`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 10
- **Primary key:** `registry_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `registry_id` | INTEGER | ✓ |  |  |
| `table_schema` | TEXT |  | ✓ |  |
| `table_name` | TEXT |  | ✓ |  |
| `leaf_type` | TEXT |  | ✓ |  |
| `ctb_path` | TEXT |  |  |  |
| `parent_table` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `registered_by` | TEXT |  |  | `'ctb_phase3'` |
| `is_frozen` | INTEGER |  |  | `0` |
| `notes` | TEXT |  |  |  |

### `ctb_table_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 675  ·  **Columns:** 10

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `registry_id` | INTEGER |  | ✓ |  |
| `table_schema` | TEXT |  | ✓ |  |
| `table_name` | TEXT |  | ✓ |  |
| `leaf_type` | TEXT |  | ✓ |  |
| `ctb_path` | TEXT |  |  |  |
| `parent_table` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |
| `registered_by` | TEXT |  |  |  |
| `is_frozen` | INTEGER |  |  |  |
| `notes` | TEXT |  |  |  |

### `ctb_vendor_bridges`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 12
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ | ✓ |  |
| `bridge_id` | TEXT |  | ✓ |  |
| `vendor_source` | TEXT |  | ✓ |  |
| `bridge_version` | TEXT |  | ✓ |  |
| `target_schema` | TEXT |  | ✓ | `'public'` |
| `target_table` | TEXT |  | ✓ |  |
| `hub_id` | TEXT |  | ✓ |  |
| `subhub_id` | TEXT |  | ✓ |  |
| `is_active` | INTEGER |  | ✓ | `1` |
| `description` | TEXT |  |  |  |
| `registered_at` | TEXT |  | ✓ | `datetime('now')` |
| `registered_by` | TEXT |  | ✓ |  |

### `ctb_violation_log`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 10
- **Primary key:** `violation_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `violation_id` | INTEGER | ✓ |  |  |
| `violation_type` | TEXT |  | ✓ |  |
| `table_schema` | TEXT |  |  |  |
| `table_name` | TEXT |  |  |  |
| `column_name` | TEXT |  |  |  |
| `violation_message` | TEXT |  | ✓ |  |
| `severity` | TEXT |  |  | `'WARNING'` |
| `detected_at` | TEXT |  |  | `datetime('now')` |
| `resolved_at` | TEXT |  |  |  |
| `resolution_note` | TEXT |  |  |  |

### `dol_column_metadata`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 2678  ·  **Columns:** 14

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER |  | ✓ |  |
| `table_name` | TEXT |  | ✓ |  |
| `column_name` | TEXT |  | ✓ |  |
| `column_id` | TEXT |  | ✓ |  |
| `description` | TEXT |  | ✓ |  |
| `category` | TEXT |  |  |  |
| `data_type` | TEXT |  | ✓ |  |
| `format_pattern` | TEXT |  |  |  |
| `max_length` | INTEGER |  |  |  |
| `search_keywords` | TEXT |  |  |  |
| `is_pii` | INTEGER |  |  |  |
| `is_searchable` | INTEGER |  |  |  |
| `example_values` | TEXT |  |  |  |
| `created_at` | TEXT |  |  |  |

### `enrichment_column_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 53  ·  **Columns:** 14
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ |  |  |
| `table_name` | TEXT |  | ✓ |  |
| `column_name` | TEXT |  | ✓ |  |
| `column_id` | TEXT |  | ✓ |  |
| `data_type` | TEXT |  | ✓ |  |
| `format_pattern` | TEXT |  |  |  |
| `description` | TEXT |  | ✓ |  |
| `example_value` | TEXT |  |  |  |
| `is_required` | INTEGER |  |  | `0` |
| `is_pii` | INTEGER |  |  | `0` |
| `ai_usage_hint` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `primitive` | TEXT |  |  | `NULL` |
| `cv` | TEXT |  |  | `NULL` |

### `outreach_column_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 78  ·  **Columns:** 14
- **Primary key:** `registry_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `registry_id` | INTEGER | ✓ |  |  |
| `schema_name` | TEXT |  | ✓ |  |
| `table_name` | TEXT |  | ✓ |  |
| `column_name` | TEXT |  | ✓ |  |
| `column_unique_id` | TEXT |  | ✓ |  |
| `column_description` | TEXT |  | ✓ |  |
| `column_format` | TEXT |  | ✓ |  |
| `is_nullable` | INTEGER |  | ✓ |  |
| `default_value` | TEXT |  |  |  |
| `fk_reference` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |
| `primitive` | TEXT |  |  | `NULL` |
| `cv` | TEXT |  |  | `NULL` |

### `outreach_hub_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 6  ·  **Columns:** 12
- **Primary key:** `hub_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `hub_id` | TEXT | ✓ | ✓ |  |
| `hub_name` | TEXT |  | ✓ |  |
| `doctrine_id` | TEXT |  | ✓ |  |
| `classification` | TEXT |  | ✓ |  |
| `gates_completion` | INTEGER |  | ✓ | `0` |
| `waterfall_order` | INTEGER |  | ✓ |  |
| `core_metric` | TEXT |  | ✓ |  |
| `metric_healthy_threshold` | REAL |  |  |  |
| `metric_critical_threshold` | REAL |  |  |  |
| `description` | TEXT |  |  |  |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `platform_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 58125  ·  **Columns:** 10
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | INTEGER | ✓ |  |  |
| `outreach_id` | TEXT |  | ✓ |  |
| `platform` | TEXT |  | ✓ |  |
| `has_it` | INTEGER |  |  | `0` |
| `url` | TEXT |  |  |  |
| `last_checked_at` | TEXT |  |  |  |
| `changed` | INTEGER |  |  | `0` |
| `data` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `sub_hub_registry`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 12  ·  **Columns:** 4
- **Primary key:** `old_table`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `old_table` | TEXT | ✓ | ✓ |  |
| `new_view` | TEXT |  | ✓ |  |
| `sub_hub` | TEXT |  | ✓ |  |
| `description` | TEXT |  |  |  |

## <imo-creator-v2: UP>

### `up_runs`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 16
- **Primary key:** `run_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `run_id` | TEXT | ✓ |  |  |
| `subject_id` | TEXT |  | ✓ |  |
| `us_run_dir` | TEXT |  | ✓ |  |
| `operator_intent` | TEXT |  |  |  |
| `p1_definition` | TEXT |  |  |  |
| `stages_completed` | INTEGER |  |  | `0` |
| `overall_p` | INTEGER |  |  | `0` |
| `status` | TEXT |  |  | `'running'` |
| `r2_artifact_path` | TEXT |  |  |  |
| `total_cost_usd` | REAL |  |  | `0` |
| `started_at` | TEXT |  | ✓ |  |
| `completed_at` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |
| `side` | TEXT |  |  | `'UP'` |
| `us_run_id` | TEXT |  |  |  |

### `up_stages`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 15
- **Primary key:** `stage_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `stage_id` | TEXT | ✓ |  |  |
| `run_id` | TEXT |  | ✓ |  |
| `stage_number` | INTEGER |  | ✓ |  |
| `stage_name` | TEXT |  | ✓ |  |
| `model_used` | TEXT |  |  |  |
| `artifact_name` | TEXT |  |  |  |
| `artifact_json` | TEXT |  |  |  |
| `p` | INTEGER |  |  | `0` |
| `status` | TEXT |  |  |  |
| `tokens_in` | INTEGER |  |  | `0` |
| `tokens_out` | INTEGER |  |  | `0` |
| `cost_usd` | REAL |  |  | `0` |
| `r2_artifact_path` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `side` | TEXT |  |  | `'UP'` |

## <imo-creator-v2: doctrine>

### `doctrine_doctrine_key`

- **DB:** `svg-d1-spine`  ·  **Rows:** 335  ·  **Columns:** 8
- **Primary key:** `key_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `key_id` | INTEGER | ✓ | ✓ |  |
| `domain` | TEXT |  | ✓ |  |
| `major_section` | INTEGER |  | ✓ |  |
| `minor_section` | INTEGER |  | ✓ |  |
| `section_title` | TEXT |  | ✓ |  |
| `audience` | TEXT |  | ✓ |  |
| `chunk_count` | INTEGER |  | ✓ |  |
| `first_doctrine_id` | TEXT |  | ✓ |  |

### `doctrine_doctrine_library`

- **DB:** `svg-d1-spine`  ·  **Rows:** 668  ·  **Columns:** 16
- **Primary key:** `id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `id` | TEXT | ✓ | ✓ |  |
| `doctrine_id` | TEXT |  | ✓ |  |
| `domain` | TEXT |  | ✓ |  |
| `audience` | TEXT |  | ✓ |  |
| `major_section` | INTEGER |  | ✓ |  |
| `minor_section` | INTEGER |  | ✓ |  |
| `chunk_sequence` | INTEGER |  | ✓ |  |
| `section_title` | TEXT |  |  |  |
| `content` | TEXT |  | ✓ |  |
| `token_count` | INTEGER |  | ✓ |  |
| `embedding` | TEXT |  | ✓ |  |
| `source_file` | TEXT |  | ✓ |  |
| `status` | TEXT |  | ✓ | `'ACTIVE'` |
| `version` | TEXT |  | ✓ | `'1.0.0'` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `doctrine_doctrine_library_error`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 6
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | INTEGER | ✓ | ✓ |  |
| `failed_at` | TEXT |  | ✓ | `datetime('now')` |
| `operation` | TEXT |  | ✓ |  |
| `error_code` | TEXT |  |  |  |
| `error_message` | TEXT |  |  |  |
| `offending_payload` | TEXT |  |  |  |

## <imo-creator-v2: engine>

### `engine_cells`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 8449  ·  **Columns:** 39
- **Primary key:** `cell_id`, `run_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `cell_id` | TEXT | ✓ | ✓ |  |
| `run_id` | TEXT | ✓ | ✓ |  |
| `name` | TEXT |  | ✓ |  |
| `depth` | INTEGER |  |  | `0` |
| `parent_id` | TEXT |  |  |  |
| `primitive` | TEXT |  |  |  |
| `heir_sovereign_ref` | TEXT |  |  |  |
| `heir_hub_id` | TEXT |  |  |  |
| `heir_ctb_placement` | TEXT |  |  |  |
| `heir_imo_topology` | TEXT |  |  |  |
| `why_it_matters` | TEXT |  |  |  |
| `trigger_desc` | TEXT |  |  |  |
| `input_desc` | TEXT |  |  |  |
| `middle_desc` | TEXT |  |  |  |
| `output_desc` | TEXT |  |  |  |
| `structural_cv` | TEXT |  |  | `'unidentified'` |
| `content_cv` | TEXT |  |  | `'unidentified'` |
| `constants_json` | TEXT |  |  |  |
| `variables_json` | TEXT |  |  |  |
| `at_primitive` | INTEGER |  |  | `0` |
| `domesticated` | INTEGER |  |  | `0` |
| `p` | INTEGER |  |  |  |
| `ratio` | REAL |  |  |  |
| `c_value` | REAL |  |  |  |
| `k_tolerance` | REAL |  |  |  |
| `comparator` | TEXT |  |  |  |
| `version` | INTEGER |  |  | `0` |
| `pass_evaluated` | INTEGER |  |  |  |
| `model_used` | TEXT |  |  |  |
| `cost_usd` | REAL |  |  | `0` |
| `dirty` | INTEGER |  |  | `1` |
| `phase` | TEXT |  |  | `'US'` |
| `locked_at_pass` | INTEGER |  |  |  |
| `sections_filled` | INTEGER |  |  | `0` |
| `template_json` | TEXT |  |  |  |
| `dependencies_json` | TEXT |  |  |  |
| `dependents_json` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `engine_cells_error`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 10
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ |  |  |
| `cell_id` | TEXT |  | ✓ |  |
| `run_id` | TEXT |  | ✓ |  |
| `heir_ref` | TEXT |  |  |  |
| `error_type` | TEXT |  | ✓ |  |
| `error_message` | TEXT |  |  |  |
| `prior_value` | TEXT |  |  |  |
| `new_value` | TEXT |  |  |  |
| `pass_number` | INTEGER |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |

### `engine_runs`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 17  ·  **Columns:** 34
- **Primary key:** `run_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `run_id` | TEXT | ✓ |  |  |
| `domain` | TEXT |  | ✓ |  |
| `phase` | TEXT |  | ✓ | `'US'` |
| `ctb_placement` | TEXT |  |  | `'leaf'` |
| `orbt` | TEXT |  |  | `'BUILD'` |
| `strikes` | INTEGER |  |  | `0` |
| `heir_sovereign_ref` | TEXT |  |  | `'imo-creator'` |
| `heir_hub_id` | TEXT |  |  |  |
| `heir_ctb_placement` | TEXT |  |  | `'leaf'` |
| `heir_imo_topology` | TEXT |  |  | `'middle'` |
| `heir_cc_layer` | TEXT |  |  | `'CC-03'` |
| `heir_services` | TEXT |  |  | `'ray,openrouter,d1,r2'` |
| `heir_secrets_provider` | TEXT |  |  | `'doppler'` |
| `heir_acceptance_criteria` | TEXT |  |  |  |
| `p1_definition` | TEXT |  |  |  |
| `input_constants` | TEXT |  |  |  |
| `total_locked` | INTEGER |  |  | `0` |
| `total_variables` | INTEGER |  |  | `0` |
| `total_domesticated` | INTEGER |  |  | `0` |
| `max_passes` | INTEGER |  |  | `20` |
| `overall_p` | INTEGER |  |  | `0` |
| `sigma_direction` | TEXT |  |  |  |
| `total_passes` | INTEGER |  |  | `0` |
| `total_cells` | INTEGER |  |  | `0` |
| `total_evaluations` | INTEGER |  |  | `0` |
| `total_cost_usd` | REAL |  |  | `0` |
| `model_used` | TEXT |  |  |  |
| `started_at` | TEXT |  |  |  |
| `completed_at` | TEXT |  |  |  |
| `status` | TEXT |  |  | `'running'` |
| `r2_artifact_path` | TEXT |  |  |  |
| `graph_snapshot` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `engine_runs_error`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 16
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ |  |  |
| `run_id` | TEXT |  | ✓ |  |
| `heir_ref` | TEXT |  |  |  |
| `orbt_at_error` | TEXT |  |  | `'BUILD'` |
| `error_type` | TEXT |  | ✓ |  |
| `error_message` | TEXT |  |  |  |
| `stage` | TEXT |  |  |  |
| `pass_number` | INTEGER |  |  |  |
| `gap_type` | TEXT |  |  |  |
| `fault_domain` | TEXT |  |  |  |
| `root_cause` | TEXT |  |  |  |
| `why_not_caught_earlier` | TEXT |  |  |  |
| `prevention_control` | TEXT |  |  |  |
| `certification_impact` | TEXT |  |  |  |
| `strike_count` | INTEGER |  |  | `0` |
| `created_at` | TEXT |  |  | `datetime('now')` |

## <imo-creator-v2: field monitor>

### `field_monitor_check_log`

- **DB:** `svg-d1-spine`  ·  **Rows:** 1  ·  **Columns:** 9
- **Primary key:** `log_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `log_id` | TEXT | ✓ | ✓ |  |
| `url_id` | TEXT |  | ✓ |  |
| `field_name` | TEXT |  | ✓ |  |
| `checked_at` | TEXT |  | ✓ | `datetime('now')` |
| `old_value` | TEXT |  |  |  |
| `new_value` | TEXT |  |  |  |
| `changed` | INTEGER |  | ✓ | `0` |
| `fetch_duration_ms` | INTEGER |  | ✓ | `0` |
| `parse_duration_ms` | INTEGER |  | ✓ | `0` |

### `field_monitor_error_log`

- **DB:** `svg-d1-spine`  ·  **Rows:** 1  ·  **Columns:** 7
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ | ✓ |  |
| `url_id` | TEXT |  | ✓ |  |
| `field_name` | TEXT |  |  |  |
| `error_type` | TEXT |  | ✓ |  |
| `error_message` | TEXT |  | ✓ |  |
| `occurred_at` | TEXT |  | ✓ | `datetime('now')` |
| `resolved_at` | TEXT |  |  |  |

### `field_monitor_field_state`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 11
- **Primary key:** `field_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `field_id` | TEXT | ✓ | ✓ |  |
| `url_id` | TEXT |  | ✓ |  |
| `field_name` | TEXT |  | ✓ |  |
| `current_value` | TEXT |  |  |  |
| `previous_value` | TEXT |  |  |  |
| `last_checked_at` | TEXT |  |  |  |
| `last_changed_at` | TEXT |  |  |  |
| `status` | TEXT |  | ✓ | `'ACTIVE'` |
| `promotion_status` | TEXT |  | ✓ | `'DRAFT'` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `field_monitor_rate_state`

- **DB:** `svg-d1-spine`  ·  **Rows:** 0  ·  **Columns:** 8
- **Primary key:** `rate_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `rate_id` | TEXT | ✓ | ✓ |  |
| `domain` | TEXT |  | ✓ |  |
| `window_start` | TEXT |  | ✓ |  |
| `window_end` | TEXT |  | ✓ |  |
| `request_count` | INTEGER |  | ✓ | `0` |
| `max_requests` | INTEGER |  | ✓ | `60` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

### `field_monitor_url_registry`

- **DB:** `svg-d1-spine`  ·  **Rows:** 1  ·  **Columns:** 7
- **Primary key:** `url_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `url_id` | TEXT | ✓ | ✓ |  |
| `domain` | TEXT |  | ✓ |  |
| `path` | TEXT |  | ✓ |  |
| `check_interval_minutes` | INTEGER |  | ✓ | `60` |
| `is_active` | INTEGER |  | ✓ | `1` |
| `created_at` | TEXT |  | ✓ | `datetime('now')` |
| `updated_at` | TEXT |  | ✓ | `datetime('now')` |

## <imo-creator-v2: run-dyno>

### `dyno_cycles`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 311  ·  **Columns:** 19
- **Primary key:** `cycle_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `cycle_id` | TEXT | ✓ |  |  |
| `run_id` | TEXT |  | ✓ |  |
| `cycle_number` | INTEGER |  | ✓ |  |
| `model_used` | TEXT |  | ✓ |  |
| `prompt_hash` | TEXT |  |  |  |
| `variables_found` | INTEGER |  |  | `0` |
| `variables_locked` | INTEGER |  |  | `0` |
| `variables_domesticated` | INTEGER |  |  | `0` |
| `still_blocking` | INTEGER |  |  | `0` |
| `sigma_direction` | TEXT |  |  |  |
| `back_prop_conflicts` | INTEGER |  |  | `0` |
| `back_prop_broken` | TEXT |  |  |  |
| `response_summary` | TEXT |  |  |  |
| `r2_receipt_path` | TEXT |  |  |  |
| `tokens_in` | INTEGER |  |  | `0` |
| `tokens_out` | INTEGER |  |  | `0` |
| `cost_usd` | REAL |  |  | `0` |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `side` | TEXT |  |  | `'US'` |

### `dyno_dmj`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 12
- **Primary key:** `dmj_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `dmj_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `kc_id` | TEXT |  | ✓ |  |
| `domain` | TEXT |  |  |  |
| `fce_id` | TEXT |  |  |  |
| `total_entries` | INTEGER |  |  |  |
| `schema_version` | TEXT |  |  | `'1.0.0'` |
| `entries_json` | TEXT |  |  |  |
| `r2_path` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `status` | TEXT |  |  | `'complete'` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `dyno_dmj_error`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 9
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `dmj_id` | TEXT |  |  |  |
| `error_code` | TEXT |  | ✓ |  |
| `error_message` | TEXT |  | ✓ |  |
| `severity` | TEXT |  |  | `'error'` |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `failed_at` | TEXT |  |  |  |
| `status` | TEXT |  |  | `'failed'` |

### `dyno_kc`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 12
- **Primary key:** `kc_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `kc_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `us_id` | TEXT |  | ✓ |  |
| `total_constants` | INTEGER |  |  |  |
| `match_count` | INTEGER |  |  |  |
| `mismatch_count` | INTEGER |  |  |  |
| `split_count` | INTEGER |  |  |  |
| `corrections_json` | TEXT |  |  |  |
| `r2_path` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `status` | TEXT |  |  | `'complete'` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `dyno_kc_error`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 9
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `kc_id` | TEXT |  |  |  |
| `error_code` | TEXT |  | ✓ |  |
| `error_message` | TEXT |  | ✓ |  |
| `severity` | TEXT |  |  | `'error'` |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `failed_at` | TEXT |  |  |  |
| `status` | TEXT |  |  | `'failed'` |

### `dyno_runs`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 89  ·  **Columns:** 21
- **Primary key:** `run_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `run_id` | TEXT | ✓ |  |  |
| `domain` | TEXT |  | ✓ |  |
| `process_number` | TEXT |  |  |  |
| `m_constants` | TEXT |  | ✓ |  |
| `p1_definition` | TEXT |  | ✓ |  |
| `total_cycles` | INTEGER |  |  | `0` |
| `sigma_direction` | TEXT |  |  |  |
| `p_status` | INTEGER |  |  | `0` |
| `variables_discovered` | INTEGER |  |  | `0` |
| `variables_locked` | INTEGER |  |  | `0` |
| `variables_domesticated` | INTEGER |  |  | `0` |
| `back_prop_conflicts` | INTEGER |  |  | `0` |
| `build_sequence` | TEXT |  |  |  |
| `r2_artifact_path` | TEXT |  |  |  |
| `status` | TEXT |  |  | `'running'` |
| `started_at` | TEXT |  | ✓ |  |
| `completed_at` | TEXT |  |  |  |
| `total_cost_usd` | REAL |  |  | `0` |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |
| `side` | TEXT |  |  | `'US'` |

### `dyno_up`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 15
- **Primary key:** `up_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `up_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `dmj_id` | TEXT |  | ✓ |  |
| `problem` | TEXT |  |  |  |
| `tolerance` | TEXT |  |  |  |
| `p_status` | TEXT |  | ✓ |  |
| `total_cycles` | INTEGER |  |  |  |
| `constants_in_m` | INTEGER |  |  |  |
| `variables_consumed` | INTEGER |  |  |  |
| `variables_remaining_json` | TEXT |  |  |  |
| `sigma_direction` | TEXT |  |  |  |
| `r2_path` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `status` | TEXT |  |  | `'complete'` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `dyno_up_error`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 9
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `up_id` | TEXT |  |  |  |
| `error_code` | TEXT |  | ✓ |  |
| `error_message` | TEXT |  | ✓ |  |
| `severity` | TEXT |  |  | `'error'` |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `failed_at` | TEXT |  |  |  |
| `status` | TEXT |  |  | `'failed'` |

### `dyno_us`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 13
- **Primary key:** `us_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `us_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `domain` | TEXT |  | ✓ |  |
| `p_status` | TEXT |  | ✓ |  |
| `total_cycles` | INTEGER |  |  |  |
| `constants_locked` | INTEGER |  |  |  |
| `variables_remaining` | INTEGER |  |  |  |
| `constants_json` | TEXT |  |  |  |
| `sigma_direction` | TEXT |  |  |  |
| `r2_path` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `status` | TEXT |  |  | `'complete'` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

### `dyno_us_error`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 9
- **Primary key:** `error_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `error_id` | TEXT | ✓ |  |  |
| `sovereign_id` | TEXT |  | ✓ |  |
| `us_id` | TEXT |  |  |  |
| `error_code` | TEXT |  | ✓ |  |
| `error_message` | TEXT |  | ✓ |  |
| `severity` | TEXT |  |  | `'error'` |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `failed_at` | TEXT |  |  |  |
| `status` | TEXT |  |  | `'failed'` |

### `dyno_variables`

- **DB:** `svg-d1-outreach-ops`  ·  **Rows:** 0  ·  **Columns:** 16
- **Primary key:** `variable_id`

<!-- TODO(human): business_purpose — what is this table FOR? what's it the canonical source of record for? which columns are authoritative vs. duplicates of another table's column? -->

| Column | Type | PK | Not-null | Default |
|---|---|:--:|:--:|---|
| `variable_id` | TEXT | ✓ |  |  |
| `run_id` | TEXT |  | ✓ |  |
| `cycle_discovered` | INTEGER |  | ✓ |  |
| `name` | TEXT |  | ✓ |  |
| `primitive` | TEXT |  |  |  |
| `cv` | TEXT |  |  |  |
| `blocking` | INTEGER |  |  | `1` |
| `description` | TEXT |  |  |  |
| `current_state` | TEXT |  |  |  |
| `required_state` | TEXT |  |  |  |
| `solution` | TEXT |  |  |  |
| `depends_on` | TEXT |  |  |  |
| `cycle_resolved` | INTEGER |  |  |  |
| `resolution` | TEXT |  |  |  |
| `created_at` | TEXT |  |  | `datetime('now')` |
| `updated_at` | TEXT |  |  | `datetime('now')` |

---
_Generated 2026-05-12T15:52:10Z · `imo-creator-v2/doc-engine/generators/d1-introspect.py` · BAR-434 · next: Neon + BigQuery scan, D1 `catalog_*` overwrite, daily cron, per-process `PROCESS-MAP.yaml`._

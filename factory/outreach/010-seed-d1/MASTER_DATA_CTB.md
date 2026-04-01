# MASTER DATA CTB — Every Column in Neon
## Trunk: Neon Vault (Marketing DB) | 4,959 columns across 296 tables
### Built from: barton-outreach-core/column_registry_complete.yml + CL/column_registry.yml + Neon inventory
### Documentation: 78% complete (3,867 documented, 1,092 remaining)

---

## BRANCH: archive (archived tables — 1456 columns)
_Archived tables not listed individually. See NEON_COLUMN_INVENTORY.csv for details._

## BRANCH: catalog (6 tables, 87 columns, 57% documented)

### LEAF: catalog.columns (27 columns, 27 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| business_definition | text | YES | catalog.columns.business_definition | Business Definition |
| business_name | character varyi | YES | catalog.columns.business_name | Business Name |
| column_id | character varyi | NO | catalog.columns.column_id | Column Id |
| column_name | character varyi | NO | catalog.columns.column_name | Column Name |
| created_at | timestamp witho | YES | catalog.columns.created_at | When this record was created |
| data_sensitivity | character varyi | YES | catalog.columns.data_sensitivity | Data Sensitivity |
| data_type | character varyi | NO | catalog.columns.data_type | Data Type |
| default_value | text | YES | catalog.columns.default_value | Default Value |
| description | text | NO | catalog.columns.description | Description |
| format_example | character varyi | YES | catalog.columns.format_example | Format Example |
| format_pattern | character varyi | YES | catalog.columns.format_pattern | Format Pattern |
| is_foreign_key | boolean | YES | catalog.columns.is_foreign_key | Whether this record foreign key |
| is_nullable | boolean | YES | catalog.columns.is_nullable | Whether this record nullable |
| is_primary_key | boolean | YES | catalog.columns.is_primary_key | Whether this record primary key |
| max_length | integer | YES | catalog.columns.max_length | Max Length |
| ordinal_position | integer | YES | catalog.columns.ordinal_position | Ordinal Position |
| pii_classification | character varyi | YES | catalog.columns.pii_classification | Pii Classification |
| references_column | character varyi | YES | catalog.columns.references_column | References Column |
| source_field | character varyi | YES | catalog.columns.source_field | Source Field |
| source_system | character varyi | YES | catalog.columns.source_system | System that originated this record |
| synonyms | ARRAY | YES | catalog.columns.synonyms | Synonyms |
| table_id | character varyi | NO | catalog.columns.table_id | Table Id |
| tags | ARRAY | YES | catalog.columns.tags | Tags |
| transformation_logic | text | YES | catalog.columns.transformation_logic | Transformation Logic |
| updated_at | timestamp witho | YES | catalog.columns.updated_at | When this record was last updated |
| valid_values | ARRAY | YES | catalog.columns.valid_values | Valid Values |
| validation_rule | text | YES | catalog.columns.validation_rule | Validation Rule |

### LEAF: catalog.schemas (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp witho | YES | catalog.schemas.created_at | When this record was created |
| description | text | NO | catalog.schemas.description | Description |
| owner | character varyi | YES | catalog.schemas.owner | Owner |
| parent_schema | character varyi | YES | catalog.schemas.parent_schema | Parent Schema |
| schema_id | character varyi | NO | catalog.schemas.schema_id | Schema Id |
| schema_name | character varyi | NO | catalog.schemas.schema_name | Schema Name |
| schema_type | character varyi | NO | catalog.schemas.schema_type | Schema Type |
| updated_at | timestamp witho | YES | catalog.schemas.updated_at | When this record was last updated |

### LEAF: catalog.tables (15 columns, 15 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| business_purpose | text | YES | catalog.tables.business_purpose | Business Purpose |
| created_at | timestamp witho | YES | catalog.tables.created_at | When this record was created |
| data_source | character varyi | YES | catalog.tables.data_source | Data Source |
| description | text | NO | catalog.tables.description | Description |
| foreign_keys | jsonb | YES | catalog.tables.foreign_keys | Foreign Keys |
| owner | character varyi | YES | catalog.tables.owner | Owner |
| primary_key | character varyi | YES | catalog.tables.primary_key | Primary Key |
| refresh_frequency | character varyi | YES | catalog.tables.refresh_frequency | Refresh Frequency |
| row_count_approx | integer | YES | catalog.tables.row_count_approx | Row Count Approx |
| schema_id | character varyi | NO | catalog.tables.schema_id | Schema Id |
| table_id | character varyi | NO | catalog.tables.table_id | Table Id |
| table_name | character varyi | NO | catalog.tables.table_name | Table Name |
| table_type | character varyi | NO | catalog.tables.table_type | Table Type |
| tags | ARRAY | YES | catalog.tables.tags | Tags |
| updated_at | timestamp witho | YES | catalog.tables.updated_at | When this record was last updated |

### LEAF: catalog.v_ai_reference (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| business_name | character varyi | YES | catalog.v_ai_reference.business_name | _undocumented_ |
| column_id | character varyi | YES | catalog.v_ai_reference.column_id | _undocumented_ |
| column_name | character varyi | YES | catalog.v_ai_reference.column_name | _undocumented_ |
| description | text | YES | catalog.v_ai_reference.description | _undocumented_ |
| format_example | character varyi | YES | catalog.v_ai_reference.format_example | _undocumented_ |
| full_type | text | YES | catalog.v_ai_reference.full_type | _undocumented_ |
| key_info | text | YES | catalog.v_ai_reference.key_info | _undocumented_ |
| tags | text | YES | catalog.v_ai_reference.tags | _undocumented_ |

### LEAF: catalog.v_schema_summary (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| column_count | bigint | YES | catalog.v_schema_summary.column_count | _undocumented_ |
| description | text | YES | catalog.v_schema_summary.description | _undocumented_ |
| schema_id | character varyi | YES | catalog.v_schema_summary.schema_id | _undocumented_ |
| schema_name | character varyi | YES | catalog.v_schema_summary.schema_name | _undocumented_ |
| schema_type | character varyi | YES | catalog.v_schema_summary.schema_type | _undocumented_ |
| table_count | bigint | YES | catalog.v_schema_summary.table_count | _undocumented_ |
| total_rows | bigint | YES | catalog.v_schema_summary.total_rows | _undocumented_ |

### LEAF: catalog.v_searchable_columns (22 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| business_definition | text | YES | catalog.v_searchable_columns.business_definition | _undocumented_ |
| business_name | character varyi | YES | catalog.v_searchable_columns.business_name | _undocumented_ |
| column_id | character varyi | YES | catalog.v_searchable_columns.column_id | _undocumented_ |
| column_name | character varyi | YES | catalog.v_searchable_columns.column_name | _undocumented_ |
| data_type | character varyi | YES | catalog.v_searchable_columns.data_type | _undocumented_ |
| description | text | YES | catalog.v_searchable_columns.description | _undocumented_ |
| format_example | character varyi | YES | catalog.v_searchable_columns.format_example | _undocumented_ |
| format_pattern | character varyi | YES | catalog.v_searchable_columns.format_pattern | _undocumented_ |
| is_foreign_key | boolean | YES | catalog.v_searchable_columns.is_foreign_key | _undocumented_ |
| is_nullable | boolean | YES | catalog.v_searchable_columns.is_nullable | _undocumented_ |
| is_primary_key | boolean | YES | catalog.v_searchable_columns.is_primary_key | _undocumented_ |
| max_length | integer | YES | catalog.v_searchable_columns.max_length | _undocumented_ |
| ordinal_position | integer | YES | catalog.v_searchable_columns.ordinal_position | _undocumented_ |
| references_column | character varyi | YES | catalog.v_searchable_columns.references_column | _undocumented_ |
| schema_name | character varyi | YES | catalog.v_searchable_columns.schema_name | _undocumented_ |
| schema_type | character varyi | YES | catalog.v_searchable_columns.schema_type | _undocumented_ |
| source_system | character varyi | YES | catalog.v_searchable_columns.source_system | _undocumented_ |
| synonyms | ARRAY | YES | catalog.v_searchable_columns.synonyms | _undocumented_ |
| table_id | character varyi | YES | catalog.v_searchable_columns.table_id | _undocumented_ |
| table_name | character varyi | YES | catalog.v_searchable_columns.table_name | _undocumented_ |
| table_type | character varyi | YES | catalog.v_searchable_columns.table_type | _undocumented_ |
| tags | ARRAY | YES | catalog.v_searchable_columns.tags | _undocumented_ |

---

## BRANCH: cl (15 tables, 227 columns, 81% documented)

### LEAF: cl.cl_err_existence (18 columns, 18 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_domain | text | YES | cl.cl_err_existence.company_domain | Company Domain |
| company_name | text | YES | cl.cl_err_existence.company_name | Company legal or common name |
| company_unique_id | uuid | NO | cl.cl_err_existence.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | YES | cl.cl_err_existence.created_at | When this record was created |
| domain_error | text | YES | cl.cl_err_existence.domain_error | Domain Error |
| domain_final_url | text | YES | cl.cl_err_existence.domain_final_url | Domain Final URL |
| domain_redirect_chain | ARRAY | YES | cl.cl_err_existence.domain_redirect_chain | Domain Redirect Chain |
| domain_status_code | integer | YES | cl.cl_err_existence.domain_status_code | Domain Status Code |
| error_id | uuid | NO | cl.cl_err_existence.error_id | Primary key for this error record |
| error_type | character varyi | YES | cl.cl_err_existence.error_type | Discriminator column classifying the error type |
| evidence | jsonb | YES | cl.cl_err_existence.evidence | Evidence |
| extracted_name | text | YES | cl.cl_err_existence.extracted_name | Extracted Name |
| extracted_state | text | YES | cl.cl_err_existence.extracted_state | Extracted State |
| linkedin_company_url | text | YES | cl.cl_err_existence.linkedin_company_url | LinkedIn company page URL |
| name_match_score | integer | YES | cl.cl_err_existence.name_match_score | Name Match score |
| reason_code | text | NO | cl.cl_err_existence.reason_code | Reason Code |
| state_match_result | text | YES | cl.cl_err_existence.state_match_result | State Match Result |
| verification_run_id | text | NO | cl.cl_err_existence.verification_run_id | Run identifier for verification batch |

### LEAF: cl.cl_errors_archive (19 columns, 19 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | cl.cl_errors_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | cl.cl_errors_archive.archived_at | When this record was archived |
| company_unique_id | uuid | YES | cl.cl_errors_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | YES | cl.cl_errors_archive.created_at | When this record was created |
| error_id | uuid | NO | cl.cl_errors_archive.error_id | Primary key for this error record |
| error_type | character varyi | NO | cl.cl_errors_archive.error_type | Discriminator column classifying the error type |
| expires_at | timestamp with  | YES | cl.cl_errors_archive.expires_at | When this record expires |
| failure_reason_code | text | NO | cl.cl_errors_archive.failure_reason_code | Failure Reason Code |
| final_outcome | text | YES | cl.cl_errors_archive.final_outcome | Final outcome after processing |
| final_reason | text | YES | cl.cl_errors_archive.final_reason | Reason for final outcome |
| inputs_snapshot | jsonb | YES | cl.cl_errors_archive.inputs_snapshot | Inputs Snapshot |
| lifecycle_run_id | text | NO | cl.cl_errors_archive.lifecycle_run_id | Run identifier for lifecycle batch |
| pass_name | text | NO | cl.cl_errors_archive.pass_name | Pass Name |
| resolved_at | timestamp with  | YES | cl.cl_errors_archive.resolved_at | When this error/issue was resolved |
| retry_after | timestamp with  | YES | cl.cl_errors_archive.retry_after | Earliest time to retry |
| retry_ceiling | integer | YES | cl.cl_errors_archive.retry_ceiling | Maximum number of retries allowed |
| retry_count | integer | YES | cl.cl_errors_archive.retry_count | Number of retry attempts so far |
| tool_tier | integer | YES | cl.cl_errors_archive.tool_tier | Tool Tier |
| tool_used | text | YES | cl.cl_errors_archive.tool_used | Tool Used |

### LEAF: cl.company_domains_archive (9 columns, 9 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | cl.company_domains_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | cl.company_domains_archive.archived_at | When this record was archived |
| checked_at | timestamp with  | YES | cl.company_domains_archive.checked_at | When this record was last checked/verified |
| company_unique_id | uuid | NO | cl.company_domains_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| domain | text | NO | cl.company_domains_archive.domain | Company website domain (lowercase, no protocol) |
| domain_health | text | YES | cl.company_domains_archive.domain_health | Domain Health |
| domain_id | uuid | NO | cl.company_domains_archive.domain_id | Primary key for this domain record |
| domain_name_confidence | integer | YES | cl.company_domains_archive.domain_name_confidence | Domain Name Confidence |
| mx_present | boolean | YES | cl.company_domains_archive.mx_present | MX record status |

### LEAF: cl.company_identity (37 columns, 37 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| canonical_name | text | YES | cl.company_identity.canonical_name | Canonical Name |
| client_id | uuid | YES | cl.company_identity.client_id | Client Id |
| client_promoted_at | timestamp with  | YES | cl.company_identity.client_promoted_at | Timestamp for client promoted event |
| company_domain | text | YES | cl.company_identity.company_domain | Company Domain |
| company_fingerprint | text | YES | cl.company_identity.company_fingerprint | Company Fingerprint |
| company_name | text | NO | cl.company_identity.company_name | Company legal or common name |
| company_unique_id | uuid | NO | cl.company_identity.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | NO | cl.company_identity.created_at | When this record was created |
| domain_status_code | integer | YES | cl.company_identity.domain_status_code | Domain Status Code |
| eligibility_status | text | YES | cl.company_identity.eligibility_status | Eligibility Status |
| employee_count_band | text | YES | cl.company_identity.employee_count_band | Employee Count Band |
| entity_role | text | YES | cl.company_identity.entity_role | Entity Role |
| exclusion_reason | text | YES | cl.company_identity.exclusion_reason | Exclusion Reason |
| existence_verified | boolean | YES | cl.company_identity.existence_verified | Existence Verified |
| final_outcome | text | YES | cl.company_identity.final_outcome | Final outcome after processing |
| final_reason | text | YES | cl.company_identity.final_reason | Reason for final outcome |
| identity_pass | integer | YES | cl.company_identity.identity_pass | Identity Pass |
| identity_status | text | YES | cl.company_identity.identity_status | Identity Status |
| last_pass_at | timestamp with  | YES | cl.company_identity.last_pass_at | Timestamp for last pass event |
| lcs_attached_at | timestamp with  | YES | cl.company_identity.lcs_attached_at | Timestamp when lcs_id was attached, auto-set on first write |
| lcs_id | uuid | YES | cl.company_identity.lcs_id | Write-once pointer to LCS record, set when company enters lifecycle communicatio |
| lifecycle_run_id | text | YES | cl.company_identity.lifecycle_run_id | Run identifier for lifecycle batch |
| linkedin_company_url | text | YES | cl.company_identity.linkedin_company_url | LinkedIn company page URL |
| name_match_score | integer | YES | cl.company_identity.name_match_score | Name Match score |
| normalized_domain | text | YES | cl.company_identity.normalized_domain | Normalized Domain |
| outreach_attached_at | timestamp with  | YES | cl.company_identity.outreach_attached_at | Timestamp for outreachtached event |
| outreach_id | uuid | YES | cl.company_identity.outreach_id | FK to outreach.outreach spine table (universal join key) |
| sales_opened_at | timestamp with  | YES | cl.company_identity.sales_opened_at | Timestamp for sales opened event |
| sales_process_id | uuid | YES | cl.company_identity.sales_process_id | Sales Process Id |
| source_system | text | NO | cl.company_identity.source_system | System that originated this record |
| sovereign_company_id | uuid | YES | cl.company_identity.sovereign_company_id | FK to cl.company_identity (sovereign company identifier) |
| state_code | character | YES | cl.company_identity.state_code | US state code (2-letter) |
| state_match_result | text | YES | cl.company_identity.state_match_result | State Match Result |
| state_verified | text | YES | cl.company_identity.state_verified | State Verified |
| updated_at | timestamp with  | YES | cl.company_identity.updated_at | When this record was last updated |
| verification_run_id | text | YES | cl.company_identity.verification_run_id | Run identifier for verification batch |
| verified_at | timestamp with  | YES | cl.company_identity.verified_at | When verification was completed |

### LEAF: cl.company_identity_archive (28 columns, 28 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | cl.company_identity_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | cl.company_identity_archive.archived_at | When this record was archived |
| canonical_name | text | YES | cl.company_identity_archive.canonical_name | Canonical Name |
| company_domain | text | YES | cl.company_identity_archive.company_domain | Company Domain |
| company_fingerprint | text | YES | cl.company_identity_archive.company_fingerprint | Company Fingerprint |
| company_name | text | NO | cl.company_identity_archive.company_name | Company legal or common name |
| company_unique_id | uuid | NO | cl.company_identity_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | NO | cl.company_identity_archive.created_at | When this record was created |
| domain_status_code | integer | YES | cl.company_identity_archive.domain_status_code | Domain Status Code |
| eligibility_status | text | YES | cl.company_identity_archive.eligibility_status | Eligibility Status |
| employee_count_band | text | YES | cl.company_identity_archive.employee_count_band | Employee Count Band |
| entity_role | text | YES | cl.company_identity_archive.entity_role | Entity Role |
| exclusion_reason | text | YES | cl.company_identity_archive.exclusion_reason | Exclusion Reason |
| existence_verified | boolean | YES | cl.company_identity_archive.existence_verified | Existence Verified |
| final_outcome | text | YES | cl.company_identity_archive.final_outcome | Final outcome after processing |
| final_reason | text | YES | cl.company_identity_archive.final_reason | Reason for final outcome |
| identity_pass | integer | YES | cl.company_identity_archive.identity_pass | Identity Pass |
| identity_status | text | YES | cl.company_identity_archive.identity_status | Identity Status |
| last_pass_at | timestamp with  | YES | cl.company_identity_archive.last_pass_at | Timestamp for last pass event |
| lifecycle_run_id | text | YES | cl.company_identity_archive.lifecycle_run_id | Run identifier for lifecycle batch |
| linkedin_company_url | text | YES | cl.company_identity_archive.linkedin_company_url | LinkedIn company page URL |
| name_match_score | integer | YES | cl.company_identity_archive.name_match_score | Name Match score |
| source_system | text | NO | cl.company_identity_archive.source_system | System that originated this record |
| sovereign_company_id | uuid | YES | cl.company_identity_archive.sovereign_company_id | FK to cl.company_identity (sovereign company identifier) |
| state_match_result | text | YES | cl.company_identity_archive.state_match_result | State Match Result |
| state_verified | text | YES | cl.company_identity_archive.state_verified | State Verified |
| verification_run_id | text | YES | cl.company_identity_archive.verification_run_id | Run identifier for verification batch |
| verified_at | timestamp with  | YES | cl.company_identity_archive.verified_at | When verification was completed |

### LEAF: cl.company_identity_bridge (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| bridge_id | uuid | NO | cl.company_identity_bridge.bridge_id | Bridge Id |
| company_sov_id | uuid | NO | cl.company_identity_bridge.company_sov_id | Company Sov Id |
| lifecycle_run_id | text | YES | cl.company_identity_bridge.lifecycle_run_id | Run identifier for lifecycle batch |
| minted_at | timestamp with  | NO | cl.company_identity_bridge.minted_at | Timestamp for minted event |
| minted_by | text | NO | cl.company_identity_bridge.minted_by | Minted By |
| source_company_id | text | NO | cl.company_identity_bridge.source_company_id | Source Company Id |
| source_system | text | NO | cl.company_identity_bridge.source_system | System that originated this record |

### LEAF: cl.company_identity_excluded (33 columns, 33 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| canonical_name | text | YES | cl.company_identity_excluded.canonical_name | Canonical Name |
| client_id | uuid | YES | cl.company_identity_excluded.client_id | Client Id |
| client_promoted_at | timestamp with  | YES | cl.company_identity_excluded.client_promoted_at | Timestamp for client promoted event |
| company_domain | text | YES | cl.company_identity_excluded.company_domain | Company Domain |
| company_fingerprint | text | YES | cl.company_identity_excluded.company_fingerprint | Company Fingerprint |
| company_name | text | NO | cl.company_identity_excluded.company_name | Company legal or common name |
| company_unique_id | uuid | NO | cl.company_identity_excluded.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | NO | cl.company_identity_excluded.created_at | When this record was created |
| domain_status_code | integer | YES | cl.company_identity_excluded.domain_status_code | Domain Status Code |
| eligibility_status | text | YES | cl.company_identity_excluded.eligibility_status | Eligibility Status |
| employee_count_band | text | YES | cl.company_identity_excluded.employee_count_band | Employee Count Band |
| entity_role | text | YES | cl.company_identity_excluded.entity_role | Entity Role |
| exclusion_reason | text | YES | cl.company_identity_excluded.exclusion_reason | Exclusion Reason |
| existence_verified | boolean | YES | cl.company_identity_excluded.existence_verified | Existence Verified |
| final_outcome | text | YES | cl.company_identity_excluded.final_outcome | Final outcome after processing |
| final_reason | text | YES | cl.company_identity_excluded.final_reason | Reason for final outcome |
| identity_pass | integer | YES | cl.company_identity_excluded.identity_pass | Identity Pass |
| identity_status | text | YES | cl.company_identity_excluded.identity_status | Identity Status |
| last_pass_at | timestamp with  | YES | cl.company_identity_excluded.last_pass_at | Timestamp for last pass event |
| lifecycle_run_id | text | YES | cl.company_identity_excluded.lifecycle_run_id | Run identifier for lifecycle batch |
| linkedin_company_url | text | YES | cl.company_identity_excluded.linkedin_company_url | LinkedIn company page URL |
| name_match_score | integer | YES | cl.company_identity_excluded.name_match_score | Name Match score |
| normalized_domain | text | YES | cl.company_identity_excluded.normalized_domain | Normalized Domain |
| outreach_attached_at | timestamp with  | YES | cl.company_identity_excluded.outreach_attached_at | Timestamp for outreachtached event |
| outreach_id | uuid | YES | cl.company_identity_excluded.outreach_id | FK to outreach.outreach spine table (universal join key) |
| sales_opened_at | timestamp with  | YES | cl.company_identity_excluded.sales_opened_at | Timestamp for sales opened event |
| sales_process_id | uuid | YES | cl.company_identity_excluded.sales_process_id | Sales Process Id |
| source_system | text | NO | cl.company_identity_excluded.source_system | System that originated this record |
| sovereign_company_id | uuid | YES | cl.company_identity_excluded.sovereign_company_id | FK to cl.company_identity (sovereign company identifier) |
| state_match_result | text | YES | cl.company_identity_excluded.state_match_result | State Match Result |
| state_verified | text | YES | cl.company_identity_excluded.state_verified | State Verified |
| verification_run_id | text | YES | cl.company_identity_excluded.verification_run_id | Run identifier for verification batch |
| verified_at | timestamp with  | YES | cl.company_identity_excluded.verified_at | When verification was completed |

### LEAF: cl.company_names_archive (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | cl.company_names_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | cl.company_names_archive.archived_at | When this record was archived |
| company_unique_id | uuid | NO | cl.company_names_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | YES | cl.company_names_archive.created_at | When this record was created |
| name_id | uuid | NO | cl.company_names_archive.name_id | Name Id |
| name_type | text | NO | cl.company_names_archive.name_type | Name Type |
| name_value | text | NO | cl.company_names_archive.name_value | Name Value |

### LEAF: cl.domain_hierarchy_archive (10 columns, 10 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | cl.domain_hierarchy_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | cl.domain_hierarchy_archive.archived_at | When this record was archived |
| child_company_id | uuid | YES | cl.domain_hierarchy_archive.child_company_id | Child Company Id |
| confidence_score | integer | YES | cl.domain_hierarchy_archive.confidence_score | Confidence score (0-100) |
| created_at | timestamp with  | YES | cl.domain_hierarchy_archive.created_at | When this record was created |
| domain | text | NO | cl.domain_hierarchy_archive.domain | Company website domain (lowercase, no protocol) |
| hierarchy_id | uuid | NO | cl.domain_hierarchy_archive.hierarchy_id | Hierarchy Id |
| parent_company_id | uuid | YES | cl.domain_hierarchy_archive.parent_company_id | Parent Company Id |
| relationship_type | text | NO | cl.domain_hierarchy_archive.relationship_type | Relationship Type |
| resolution_method | text | YES | cl.domain_hierarchy_archive.resolution_method | Resolution Method |

### LEAF: cl.identity_confidence_archive (6 columns, 6 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | cl.identity_confidence_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | cl.identity_confidence_archive.archived_at | When this record was archived |
| company_unique_id | uuid | NO | cl.identity_confidence_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| computed_at | timestamp with  | YES | cl.identity_confidence_archive.computed_at | Timestamp for computed event |
| confidence_bucket | text | NO | cl.identity_confidence_archive.confidence_bucket | Confidence Bucket |
| confidence_score | integer | NO | cl.identity_confidence_archive.confidence_score | Confidence score (0-100) |

### LEAF: cl.movement_code_registry (5 columns, 5 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| active | boolean | NO | cl.movement_code_registry.active | Active |
| code | integer | NO | cl.movement_code_registry.code | Code |
| created_at | timestamp with  | NO | cl.movement_code_registry.created_at | When this record was created |
| description | text | NO | cl.movement_code_registry.description | Description |
| subhub | character varyi | NO | cl.movement_code_registry.subhub | Subhub |

### LEAF: cl.sovereign_mint_backup_20260218 (4 columns, 4 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_name | text | YES | cl.sovereign_mint_backup_20260218.company_name | Company legal or common name |
| company_unique_id | uuid | YES | cl.sovereign_mint_backup_20260218.company_unique_i | FK to cl.company_identity or Barton company ID |
| old_sovereign_id | uuid | YES | cl.sovereign_mint_backup_20260218.old_sovereign_id | Old Sovereign Id |
| source_system | text | YES | cl.sovereign_mint_backup_20260218.source_system | System that originated this record |

### LEAF: cl.v_company_identity_eligible (25 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| canonical_name | text | YES | cl.v_company_identity_eligible.canonical_name | _undocumented_ |
| company_domain | text | YES | cl.v_company_identity_eligible.company_domain | _undocumented_ |
| company_fingerprint | text | YES | cl.v_company_identity_eligible.company_fingerprint | _undocumented_ |
| company_name | text | YES | cl.v_company_identity_eligible.company_name | _undocumented_ |
| company_unique_id | uuid | YES | cl.v_company_identity_eligible.company_unique_id | _undocumented_ |
| created_at | timestamp with  | YES | cl.v_company_identity_eligible.created_at | _undocumented_ |
| domain_status_code | integer | YES | cl.v_company_identity_eligible.domain_status_code | _undocumented_ |
| domain_verified | boolean | YES | cl.v_company_identity_eligible.domain_verified | _undocumented_ |
| eligibility_reason | text | YES | cl.v_company_identity_eligible.eligibility_reason | _undocumented_ |
| eligible_for_outreach | boolean | YES | cl.v_company_identity_eligible.eligible_for_outrea | _undocumented_ |
| employee_count_band | text | YES | cl.v_company_identity_eligible.employee_count_band | _undocumented_ |
| existence_verified | boolean | YES | cl.v_company_identity_eligible.existence_verified | _undocumented_ |
| identity_pass | integer | YES | cl.v_company_identity_eligible.identity_pass | _undocumented_ |
| identity_status | text | YES | cl.v_company_identity_eligible.identity_status | _undocumented_ |
| last_pass_at | timestamp with  | YES | cl.v_company_identity_eligible.last_pass_at | _undocumented_ |
| lifecycle_run_id | text | YES | cl.v_company_identity_eligible.lifecycle_run_id | _undocumented_ |
| linkedin_company_url | text | YES | cl.v_company_identity_eligible.linkedin_company_ur | _undocumented_ |
| name_coherent | boolean | YES | cl.v_company_identity_eligible.name_coherent | _undocumented_ |
| name_match_score | integer | YES | cl.v_company_identity_eligible.name_match_score | _undocumented_ |
| source_system | text | YES | cl.v_company_identity_eligible.source_system | _undocumented_ |
| state_coherent | boolean | YES | cl.v_company_identity_eligible.state_coherent | _undocumented_ |
| state_match_result | text | YES | cl.v_company_identity_eligible.state_match_result | _undocumented_ |
| state_verified | text | YES | cl.v_company_identity_eligible.state_verified | _undocumented_ |
| verification_run_id | text | YES | cl.v_company_identity_eligible.verification_run_id | _undocumented_ |
| verified_at | timestamp with  | YES | cl.v_company_identity_eligible.verified_at | _undocumented_ |

### LEAF: cl.v_company_lifecycle_status (14 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| client_id | uuid | YES | cl.v_company_lifecycle_status.client_id | _undocumented_ |
| client_promoted_at | timestamp with  | YES | cl.v_company_lifecycle_status.client_promoted_at | _undocumented_ |
| company_domain | text | YES | cl.v_company_lifecycle_status.company_domain | _undocumented_ |
| company_name | text | YES | cl.v_company_lifecycle_status.company_name | _undocumented_ |
| company_unique_id | uuid | YES | cl.v_company_lifecycle_status.company_unique_id | _undocumented_ |
| has_outreach | boolean | YES | cl.v_company_lifecycle_status.has_outreach | _undocumented_ |
| has_sales | boolean | YES | cl.v_company_lifecycle_status.has_sales | _undocumented_ |
| is_client | boolean | YES | cl.v_company_lifecycle_status.is_client | _undocumented_ |
| lifecycle_stage | text | YES | cl.v_company_lifecycle_status.lifecycle_stage | _undocumented_ |
| outreach_attached_at | timestamp with  | YES | cl.v_company_lifecycle_status.outreach_attached_at | _undocumented_ |
| outreach_id | uuid | YES | cl.v_company_lifecycle_status.outreach_id | _undocumented_ |
| sales_opened_at | timestamp with  | YES | cl.v_company_lifecycle_status.sales_opened_at | _undocumented_ |
| sales_process_id | uuid | YES | cl.v_company_lifecycle_status.sales_process_id | _undocumented_ |
| sovereign_company_id | uuid | YES | cl.v_company_lifecycle_status.sovereign_company_id | _undocumented_ |

### LEAF: cl.v_identity_gate_summary (5 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| fail_count | bigint | YES | cl.v_identity_gate_summary.fail_count | _undocumented_ |
| pass_count | bigint | YES | cl.v_identity_gate_summary.pass_count | _undocumented_ |
| pass_pct | numeric | YES | cl.v_identity_gate_summary.pass_pct | _undocumented_ |
| pending_count | bigint | YES | cl.v_identity_gate_summary.pending_count | _undocumented_ |
| total_companies | bigint | YES | cl.v_identity_gate_summary.total_companies | _undocumented_ |

---

## BRANCH: clnt (1 tables, 17 columns, 0% documented)

### LEAF: clnt.client (17 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| client_id | uuid | NO | clnt.client.client_id | _undocumented_ |
| color_accent | text | YES | clnt.client.color_accent | _undocumented_ |
| color_primary | text | YES | clnt.client.color_primary | _undocumented_ |
| created_at | timestamp with  | NO | clnt.client.created_at | _undocumented_ |
| dashboard_blocks | jsonb | NO | clnt.client.dashboard_blocks | _undocumented_ |
| domain | text | YES | clnt.client.domain | _undocumented_ |
| domicile_state | text | YES | clnt.client.domicile_state | _undocumented_ |
| effective_date | date | YES | clnt.client.effective_date | _undocumented_ |
| feature_flags | jsonb | NO | clnt.client.feature_flags | _undocumented_ |
| fein | text | YES | clnt.client.fein | _undocumented_ |
| label_override | text | YES | clnt.client.label_override | _undocumented_ |
| legal_name | text | NO | clnt.client.legal_name | _undocumented_ |
| logo_url | text | YES | clnt.client.logo_url | _undocumented_ |
| source | text | YES | clnt.client.source | _undocumented_ |
| status | text | NO | clnt.client.status | _undocumented_ |
| updated_at | timestamp with  | NO | clnt.client.updated_at | _undocumented_ |
| version | integer | NO | clnt.client.version | _undocumented_ |

---

## BRANCH: company (5 tables, 39 columns, 0% documented)

### LEAF: company.next_company_urls_30d (4 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_id | bigint | YES | company.next_company_urls_30d.company_id | _undocumented_ |
| last_checked_at | timestamp with  | YES | company.next_company_urls_30d.last_checked_at | _undocumented_ |
| url | text | YES | company.next_company_urls_30d.url | _undocumented_ |
| url_type | text | YES | company.next_company_urls_30d.url_type | _undocumented_ |

### LEAF: company.vw_anchor_staleness (9 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_id | bigint | YES | company.vw_anchor_staleness.company_id | _undocumented_ |
| company_name | text | YES | company.vw_anchor_staleness.company_name | _undocumented_ |
| linkedin_status | text | YES | company.vw_anchor_staleness.linkedin_status | _undocumented_ |
| linkedin_url | text | YES | company.vw_anchor_staleness.linkedin_url | _undocumented_ |
| news_status | text | YES | company.vw_anchor_staleness.news_status | _undocumented_ |
| news_url | text | YES | company.vw_anchor_staleness.news_url | _undocumented_ |
| overall_status | text | YES | company.vw_anchor_staleness.overall_status | _undocumented_ |
| website_status | text | YES | company.vw_anchor_staleness.website_status | _undocumented_ |
| website_url | text | YES | company.vw_anchor_staleness.website_url | _undocumented_ |

### LEAF: company.vw_company_slots (15 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_id | bigint | YES | company.vw_company_slots.company_id | _undocumented_ |
| company_name | text | YES | company.vw_company_slots.company_name | _undocumented_ |
| company_slot_id | bigint | YES | company.vw_company_slots.company_slot_id | _undocumented_ |
| contact_id | bigint | YES | company.vw_company_slots.contact_id | _undocumented_ |
| email | text | YES | company.vw_company_slots.email | _undocumented_ |
| email_checked_at | timestamp with  | YES | company.vw_company_slots.email_checked_at | _undocumented_ |
| email_status | text | YES | company.vw_company_slots.email_status | _undocumented_ |
| full_name | text | YES | company.vw_company_slots.full_name | _undocumented_ |
| linkedin_url | text | YES | company.vw_company_slots.linkedin_url | _undocumented_ |
| news_url | text | YES | company.vw_company_slots.news_url | _undocumented_ |
| phone | text | YES | company.vw_company_slots.phone | _undocumented_ |
| profile_source_url | text | YES | company.vw_company_slots.profile_source_url | _undocumented_ |
| role_code | text | YES | company.vw_company_slots.role_code | _undocumented_ |
| title | text | YES | company.vw_company_slots.title | _undocumented_ |
| website_url | text | YES | company.vw_company_slots.website_url | _undocumented_ |

### LEAF: company.vw_due_renewals_ready (5 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| campaign_window_start | date | YES | company.vw_due_renewals_ready.campaign_window_star | _undocumented_ |
| company_id | bigint | YES | company.vw_due_renewals_ready.company_id | _undocumented_ |
| company_name | text | YES | company.vw_due_renewals_ready.company_name | _undocumented_ |
| has_green_contact | boolean | YES | company.vw_due_renewals_ready.has_green_contact | _undocumented_ |
| next_renewal_date | date | YES | company.vw_due_renewals_ready.next_renewal_date | _undocumented_ |

### LEAF: company.vw_next_renewal (6 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| campaign_window_start | date | YES | company.vw_next_renewal.campaign_window_start | _undocumented_ |
| company_id | bigint | YES | company.vw_next_renewal.company_id | _undocumented_ |
| company_name | text | YES | company.vw_next_renewal.company_name | _undocumented_ |
| next_renewal_date | date | YES | company.vw_next_renewal.next_renewal_date | _undocumented_ |
| notice_days | integer | YES | company.vw_next_renewal.notice_days | _undocumented_ |
| renewal_month | smallint | YES | company.vw_next_renewal.renewal_month | _undocumented_ |

---

## BRANCH: coverage (3 tables, 24 columns, 71% documented)

### LEAF: coverage.service_agent (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_name | text | NO | coverage.service_agent.agent_name | Service agent display name |
| agent_number | text | NO | coverage.service_agent.agent_number | Service agent identifier (SA-NNN format) |
| created_at | timestamp with  | NO | coverage.service_agent.created_at | When this record was created |
| first_name | text | YES | coverage.service_agent.first_name | Person first name |
| last_name | text | YES | coverage.service_agent.last_name | Person last name |
| service_agent_id | uuid | NO | coverage.service_agent.service_agent_id | FK to coverage.service_agent |
| status | text | NO | coverage.service_agent.status | Current status of this record |

### LEAF: coverage.service_agent_coverage (10 columns, 10 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| anchor_zip | text | NO | coverage.service_agent_coverage.anchor_zip | Center ZIP code for this market radius |
| coverage_id | uuid | NO | coverage.service_agent_coverage.coverage_id | FK to coverage.service_agent_coverage |
| created_at | timestamp with  | NO | coverage.service_agent_coverage.created_at | When this record was created |
| created_by | text | NO | coverage.service_agent_coverage.created_by | Created By |
| notes | text | YES | coverage.service_agent_coverage.notes | Human-readable notes |
| radius_miles | numeric | NO | coverage.service_agent_coverage.radius_miles | Radius in miles from anchor ZIP |
| retired_at | timestamp with  | YES | coverage.service_agent_coverage.retired_at | Timestamp for retired event |
| retired_by | text | YES | coverage.service_agent_coverage.retired_by | Retired By |
| service_agent_id | uuid | NO | coverage.service_agent_coverage.service_agent_id | FK to coverage.service_agent |
| status | text | NO | coverage.service_agent_coverage.status | Current status of this record |

### LEAF: coverage.v_service_agent_coverage_zips (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| city | text | YES | coverage.v_service_agent_coverage_zips.city | _undocumented_ |
| coverage_id | uuid | YES | coverage.v_service_agent_coverage_zips.coverage_id | _undocumented_ |
| distance_miles | numeric | YES | coverage.v_service_agent_coverage_zips.distance_mi | _undocumented_ |
| population | integer | YES | coverage.v_service_agent_coverage_zips.population | _undocumented_ |
| service_agent_id | uuid | YES | coverage.v_service_agent_coverage_zips.service_age | _undocumented_ |
| state_id | text | YES | coverage.v_service_agent_coverage_zips.state_id | _undocumented_ |
| zip | text | YES | coverage.v_service_agent_coverage_zips.zip | _undocumented_ |

---

## BRANCH: ctb (7 tables, 71 columns, 10% documented)

### LEAF: ctb.audit_log (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | ctb.audit_log.created_at | _undocumented_ |
| created_by | text | NO | ctb.audit_log.created_by | _undocumented_ |
| details | jsonb | YES | ctb.audit_log.details | _undocumented_ |
| event_type | text | NO | ctb.audit_log.event_type | _undocumented_ |
| hub_id | text | YES | ctb.audit_log.hub_id | _undocumented_ |
| id | bigint | NO | ctb.audit_log.id | _undocumented_ |
| operation | text | YES | ctb.audit_log.operation | _undocumented_ |
| process_id | text | YES | ctb.audit_log.process_id | _undocumented_ |
| subhub_id | text | YES | ctb.audit_log.subhub_id | _undocumented_ |
| table_name | text | YES | ctb.audit_log.table_name | _undocumented_ |
| table_schema | text | YES | ctb.audit_log.table_schema | _undocumented_ |

### LEAF: ctb.batch_audit_log (6 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| batch_id | uuid | NO | ctb.batch_audit_log.batch_id | _undocumented_ |
| changed_at | timestamp with  | NO | ctb.batch_audit_log.changed_at | _undocumented_ |
| changed_by | text | NO | ctb.batch_audit_log.changed_by | _undocumented_ |
| id | bigint | NO | ctb.batch_audit_log.id | _undocumented_ |
| new_status | text | NO | ctb.batch_audit_log.new_status | _undocumented_ |
| old_status | text | YES | ctb.batch_audit_log.old_status | _undocumented_ |

### LEAF: ctb.promotion_paths (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | ctb.promotion_paths.created_at | _undocumented_ |
| created_by | text | NO | ctb.promotion_paths.created_by | _undocumented_ |
| description | text | YES | ctb.promotion_paths.description | _undocumented_ |
| hub_id | text | NO | ctb.promotion_paths.hub_id | _undocumented_ |
| id | bigint | NO | ctb.promotion_paths.id | _undocumented_ |
| is_active | boolean | NO | ctb.promotion_paths.is_active | _undocumented_ |
| source_schema | text | NO | ctb.promotion_paths.source_schema | _undocumented_ |
| source_table | text | NO | ctb.promotion_paths.source_table | _undocumented_ |
| subhub_id | text | NO | ctb.promotion_paths.subhub_id | _undocumented_ |
| target_schema | text | NO | ctb.promotion_paths.target_schema | _undocumented_ |
| target_table | text | NO | ctb.promotion_paths.target_table | _undocumented_ |

### LEAF: ctb.raw_batch_registry (11 columns, 3 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| batch_id | uuid | NO | ctb.raw_batch_registry.batch_id | Matches ingestion_batch_id on RAW table rows |
| bridge_id | text | NO | ctb.raw_batch_registry.bridge_id | _undocumented_ |
| bridge_version | text | NO | ctb.raw_batch_registry.bridge_version | _undocumented_ |
| ingested_at | timestamp with  | NO | ctb.raw_batch_registry.ingested_at | _undocumented_ |
| ingested_by | text | NO | ctb.raw_batch_registry.ingested_by | _undocumented_ |
| row_count | integer | NO | ctb.raw_batch_registry.row_count | _undocumented_ |
| status | text | NO | ctb.raw_batch_registry.status | ACTIVE (current), SUPERSEDED (replaced by newer batch), FAILED (ingestion error) |
| supersedes_batch_id | uuid | YES | ctb.raw_batch_registry.supersedes_batch_id | Previous batch this one replaces (corrections flow through supersede) |
| target_schema | text | NO | ctb.raw_batch_registry.target_schema | _undocumented_ |
| target_table | text | NO | ctb.raw_batch_registry.target_table | _undocumented_ |
| vendor_source | text | NO | ctb.raw_batch_registry.vendor_source | _undocumented_ |

### LEAF: ctb.table_registry (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | YES | ctb.table_registry.created_at | _undocumented_ |
| ctb_path | character varyi | YES | ctb.table_registry.ctb_path | _undocumented_ |
| is_frozen | boolean | YES | ctb.table_registry.is_frozen | _undocumented_ |
| leaf_type | character varyi | NO | ctb.table_registry.leaf_type | _undocumented_ |
| notes | text | YES | ctb.table_registry.notes | _undocumented_ |
| parent_table | character varyi | YES | ctb.table_registry.parent_table | _undocumented_ |
| registered_by | character varyi | YES | ctb.table_registry.registered_by | _undocumented_ |
| registry_id | integer | NO | ctb.table_registry.registry_id | _undocumented_ |
| table_name | character varyi | NO | ctb.table_registry.table_name | _undocumented_ |
| table_schema | character varyi | NO | ctb.table_registry.table_schema | _undocumented_ |

### LEAF: ctb.vendor_bridges (12 columns, 4 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| bridge_id | text | NO | ctb.vendor_bridges.bridge_id | Unique bridge identifier (e.g., stripe-invoices-v2) |
| bridge_version | text | NO | ctb.vendor_bridges.bridge_version | Semantic version of the bridge logic |
| description | text | YES | ctb.vendor_bridges.description | _undocumented_ |
| hub_id | text | NO | ctb.vendor_bridges.hub_id | _undocumented_ |
| id | bigint | NO | ctb.vendor_bridges.id | _undocumented_ |
| is_active | boolean | NO | ctb.vendor_bridges.is_active | _undocumented_ |
| registered_at | timestamp with  | NO | ctb.vendor_bridges.registered_at | _undocumented_ |
| registered_by | text | NO | ctb.vendor_bridges.registered_by | _undocumented_ |
| subhub_id | text | NO | ctb.vendor_bridges.subhub_id | _undocumented_ |
| target_schema | text | NO | ctb.vendor_bridges.target_schema | _undocumented_ |
| target_table | text | NO | ctb.vendor_bridges.target_table | RAW table this bridge writes to |
| vendor_source | text | NO | ctb.vendor_bridges.vendor_source | External system name (e.g., stripe, hubspot, manual_csv) |

### LEAF: ctb.violation_log (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| column_name | character varyi | YES | ctb.violation_log.column_name | _undocumented_ |
| detected_at | timestamp with  | YES | ctb.violation_log.detected_at | _undocumented_ |
| resolution_note | text | YES | ctb.violation_log.resolution_note | _undocumented_ |
| resolved_at | timestamp with  | YES | ctb.violation_log.resolved_at | _undocumented_ |
| severity | character varyi | YES | ctb.violation_log.severity | _undocumented_ |
| table_name | character varyi | YES | ctb.violation_log.table_name | _undocumented_ |
| table_schema | character varyi | YES | ctb.violation_log.table_schema | _undocumented_ |
| violation_id | integer | NO | ctb.violation_log.violation_id | _undocumented_ |
| violation_message | text | NO | ctb.violation_log.violation_message | _undocumented_ |
| violation_type | character varyi | NO | ctb.violation_log.violation_type | _undocumented_ |

---

## BRANCH: dol (36 tables, 1171 columns, 96% documented)

### LEAF: dol.column_metadata (14 columns, 14 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| category | character varyi | YES | dol.column_metadata.category | Category |
| column_id | character varyi | NO | dol.column_metadata.column_id | Column Id |
| column_name | character varyi | NO | dol.column_metadata.column_name | Column Name |
| created_at | timestamp witho | YES | dol.column_metadata.created_at | When this record was created |
| data_type | character varyi | NO | dol.column_metadata.data_type | Data Type |
| description | text | NO | dol.column_metadata.description | Description |
| example_values | ARRAY | YES | dol.column_metadata.example_values | Example Values |
| format_pattern | character varyi | YES | dol.column_metadata.format_pattern | Format Pattern |
| id | integer | NO | dol.column_metadata.id | Id |
| is_pii | boolean | YES | dol.column_metadata.is_pii | Whether this record pii |
| is_searchable | boolean | YES | dol.column_metadata.is_searchable | Whether this record searchable |
| max_length | integer | YES | dol.column_metadata.max_length | Max Length |
| search_keywords | ARRAY | YES | dol.column_metadata.search_keywords | Search Keywords |
| table_name | character varyi | NO | dol.column_metadata.table_name | Table Name |

### LEAF: dol.ein_urls (9 columns, 9 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| city | text | YES | dol.ein_urls.city | City name |
| company_name | text | NO | dol.ein_urls.company_name | Company legal or common name |
| discovered_at | timestamp witho | YES | dol.ein_urls.discovered_at | Timestamp for discovered event |
| discovery_method | text | YES | dol.ein_urls.discovery_method | Discovery Method |
| domain | text | YES | dol.ein_urls.domain | Company website domain (lowercase, no protocol) |
| ein | character varyi | NO | dol.ein_urls.ein | Employer Identification Number (9-digit, no dashes) |
| normalized_domain | text | YES | dol.ein_urls.normalized_domain | Normalized Domain |
| state | character varyi | YES | dol.ein_urls.state | US state code (2-letter) |
| url | text | YES | dol.ein_urls.url | Url |

### LEAF: dol.form_5500 (147 columns, 147 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.form_5500.ack_id | DOL acknowledgment ID for the filing | ID: DOL_F5500_ACK_ID | Format: Up to 255  |
| admin_address_same_spon_ind | character varyi | YES | dol.form_5500.admin_address_same_spon_ind | Plan Administrator address same spon (indicator flag) | ID: DOL_F5500_ADMIN_ADDR |
| admin_care_of_name | character varyi | YES | dol.form_5500.admin_care_of_name | Plan Administrator care of (name) | ID: DOL_F5500_ADMIN_CARE_OF_NAME | Format: U |
| admin_ein | character varyi | YES | dol.form_5500.admin_ein | Plan Administrator ein | ID: DOL_F5500_ADMIN_EIN | Format: 9 digits (XX-XXXXXXX) |
| admin_foreign_address1 | character varyi | YES | dol.form_5500.admin_foreign_address1 | Plan Administrator foreign address1 | ID: DOL_F5500_ADMIN_FOREIGN_ADDRESS1 | For |
| admin_foreign_address2 | character varyi | YES | dol.form_5500.admin_foreign_address2 | Plan Administrator foreign address2 | ID: DOL_F5500_ADMIN_FOREIGN_ADDRESS2 | For |
| admin_foreign_city | character varyi | YES | dol.form_5500.admin_foreign_city | Plan Administrator foreign city | ID: DOL_F5500_ADMIN_FOREIGN_CITY | Format: Up  |
| admin_foreign_cntry | character varyi | YES | dol.form_5500.admin_foreign_cntry | Plan Administrator foreign cntry | ID: DOL_F5500_ADMIN_FOREIGN_CNTRY | Format: D |
| admin_foreign_postal_cd | character varyi | YES | dol.form_5500.admin_foreign_postal_cd | Plan Administrator foreign postal cd | ID: DOL_F5500_ADMIN_FOREIGN_POSTAL_CD | F |
| admin_foreign_prov_state | character varyi | YES | dol.form_5500.admin_foreign_prov_state | Plan Administrator foreign province state | ID: DOL_F5500_ADMIN_FOREIGN_PROV_STA |
| admin_manual_signed_date | character varyi | YES | dol.form_5500.admin_manual_signed_date | Plan Administrator manual signed (date) | ID: DOL_F5500_ADMIN_MANUAL_SIGNED_DATE |
| admin_manual_signed_name | character varyi | YES | dol.form_5500.admin_manual_signed_name | Plan Administrator manual signed (name) | ID: DOL_F5500_ADMIN_MANUAL_SIGNED_NAME |
| admin_name | character varyi | YES | dol.form_5500.admin_name | Plan Administrator name | ID: DOL_F5500_ADMIN_NAME | Format: Up to 255 character |
| admin_name_same_spon_ind | character varyi | YES | dol.form_5500.admin_name_same_spon_ind | Plan Administrator name same spon (indicator flag) | ID: DOL_F5500_ADMIN_NAME_SA |
| admin_phone_num | character varyi | YES | dol.form_5500.admin_phone_num | Plan Administrator phone (number/identifier) | ID: DOL_F5500_ADMIN_PHONE_NUM | F |
| admin_phone_num_foreign | character varyi | YES | dol.form_5500.admin_phone_num_foreign | Plan Administrator phone number foreign | ID: DOL_F5500_ADMIN_PHONE_NUM_FOREIGN  |
| admin_signed_date | character varyi | YES | dol.form_5500.admin_signed_date | Plan Administrator signed (date) | ID: DOL_F5500_ADMIN_SIGNED_DATE | Format: YYY |
| admin_signed_name | character varyi | YES | dol.form_5500.admin_signed_name | Plan Administrator signed (name) | ID: DOL_F5500_ADMIN_SIGNED_NAME | Format: Up  |
| admin_us_address1 | character varyi | YES | dol.form_5500.admin_us_address1 | Plan Administrator us address1 | ID: DOL_F5500_ADMIN_US_ADDRESS1 | Format: Up to |
| admin_us_address2 | character varyi | YES | dol.form_5500.admin_us_address2 | Plan Administrator us address2 | ID: DOL_F5500_ADMIN_US_ADDRESS2 | Format: Up to |
| admin_us_city | character varyi | YES | dol.form_5500.admin_us_city | Plan Administrator us city | ID: DOL_F5500_ADMIN_US_CITY | Format: Up to 100 cha |
| admin_us_state | character varyi | YES | dol.form_5500.admin_us_state | Plan Administrator us state | ID: DOL_F5500_ADMIN_US_STATE | Format: Up to 10 ch |
| admin_us_zip | character varyi | YES | dol.form_5500.admin_us_zip | Plan Administrator us (ZIP code) | ID: DOL_F5500_ADMIN_US_ZIP | Format: 5 or 9 d |
| adopted_plan_perm_sec_act | character varyi | YES | dol.form_5500.adopted_plan_perm_sec_act | Adopted plan perm sec act | ID: DOL_F5500_ADOPTED_PLAN_PERM_SEC_ACT | Format: Up |
| amended_ind | character varyi | YES | dol.form_5500.amended_ind | Amended (indicator flag) | ID: DOL_F5500_AMENDED_IND | Format: Y/N/X or 1/0 |
| benef_rcvg_bnft_cnt | numeric | YES | dol.form_5500.benef_rcvg_bnft_cnt | Benef receiving bnft (count/number) | ID: DOL_F5500_BENEF_RCVG_BNFT_CNT | Format |
| benefit_gen_asset_ind | character varyi | YES | dol.form_5500.benefit_gen_asset_ind | Benefit gen asset (indicator flag) | ID: DOL_F5500_BENEFIT_GEN_ASSET_IND | Forma |
| benefit_insurance_ind | character varyi | YES | dol.form_5500.benefit_insurance_ind | Benefit insurance (indicator flag) | ID: DOL_F5500_BENEFIT_INSURANCE_IND | Forma |
| benefit_sec412_ind | character varyi | YES | dol.form_5500.benefit_sec412_ind | Benefit sec412 (indicator flag) | ID: DOL_F5500_BENEFIT_SEC412_IND | Format: Y/N |
| benefit_trust_ind | character varyi | YES | dol.form_5500.benefit_trust_ind | Benefit trust (indicator flag) | ID: DOL_F5500_BENEFIT_TRUST_IND | Format: Y/N/X |
| business_code | character varyi | YES | dol.form_5500.business_code | Business (code value) | ID: DOL_F5500_BUSINESS_CODE | Format: Up to 50 character |
| collective_bargain_ind | character varyi | YES | dol.form_5500.collective_bargain_ind | Collective bargain (indicator flag) | ID: DOL_F5500_COLLECTIVE_BARGAIN_IND | For |
| company_unique_id | text | YES | dol.form_5500.company_unique_id | Company unique id | ID: DOL_F5500_COMPANY_UNIQUE_ID | Format: Variable length te |
| compliance_m1_filing_req_ind | character varyi | YES | dol.form_5500.compliance_m1_filing_req_ind | Compliance m1 filing req (indicator flag) | ID: DOL_F5500_COMPLIANCE_M1_FILING_R |
| contrib_emplrs_cnt | numeric | YES | dol.form_5500.contrib_emplrs_cnt | Contrib emplrs (count/number) | ID: DOL_F5500_CONTRIB_EMPLRS_CNT | Format: Whole |
| created_at | timestamp with  | NO | dol.form_5500.created_at | Record creation timestamp | ID: DOL_F5500_CREATED_AT | Format: YYYY-MM-DD HH:MM: |
| date_received | character varyi | YES | dol.form_5500.date_received | Date filing was received by DOL | ID: DOL_F5500_DATE_RECEIVED | Format: Up to 30 |
| dfe_manual_signed_date | character varyi | YES | dol.form_5500.dfe_manual_signed_date | Direct Filing Entity manual signed (date) | ID: DOL_F5500_DFE_MANUAL_SIGNED_DATE |
| dfe_manual_signed_name | character varyi | YES | dol.form_5500.dfe_manual_signed_name | Direct Filing Entity manual signed (name) | ID: DOL_F5500_DFE_MANUAL_SIGNED_NAME |
| dfe_signed_date | character varyi | YES | dol.form_5500.dfe_signed_date | Direct Filing Entity signed (date) | ID: DOL_F5500_DFE_SIGNED_DATE | Format: YYY |
| dfe_signed_name | character varyi | YES | dol.form_5500.dfe_signed_name | Direct Filing Entity signed (name) | ID: DOL_F5500_DFE_SIGNED_NAME | Format: Up  |
| dfvc_program_ind | character varyi | YES | dol.form_5500.dfvc_program_ind | Dfvc program (indicator flag) | ID: DOL_F5500_DFVC_PROGRAM_IND | Format: Y/N/X o |
| ext_automatic_ind | character varyi | YES | dol.form_5500.ext_automatic_ind | Ext automatic (indicator flag) | ID: DOL_F5500_EXT_AUTOMATIC_IND | Format: Y/N/X |
| ext_special_ind | character varyi | YES | dol.form_5500.ext_special_ind | Ext special (indicator flag) | ID: DOL_F5500_EXT_SPECIAL_IND | Format: Y/N/X or  |
| ext_special_text | text | YES | dol.form_5500.ext_special_text | Ext special (text description) | ID: DOL_F5500_EXT_SPECIAL_TEXT | Format: Variab |
| f5558_application_filed_ind | character varyi | YES | dol.form_5500.f5558_application_filed_ind | F5558 application filed (indicator flag) | ID: DOL_F5500_F5558_APPLICATION_FILED |
| filing_id | uuid | NO | dol.form_5500.filing_id | Unique filing identifier (UUID) | ID: DOL_F5500_FILING_ID | Format: xxxxxxxx-xxx |
| filing_status | character varyi | YES | dol.form_5500.filing_status | Filing status | ID: DOL_F5500_FILING_STATUS | Format: Up to 50 characters |
| final_filing_ind | character varyi | YES | dol.form_5500.final_filing_ind | Final filing (indicator flag) | ID: DOL_F5500_FINAL_FILING_IND | Format: Y/N/X o |
| form_plan_year_begin_date | character varyi | YES | dol.form_5500.form_plan_year_begin_date | Form plan year begin (date) | ID: DOL_F5500_FORM_PLAN_YEAR_BEGIN_DATE | Format:  |
| form_tax_prd | character varyi | YES | dol.form_5500.form_tax_prd | Form tax prd | ID: DOL_F5500_FORM_TAX_PRD | Format: Up to 255 characters |
| form_year | character varyi | YES | dol.form_5500.form_year | Tax/plan year for this filing | ID: DOL_F5500_FORM_YEAR | Format: Up to 10 chara |
| funding_gen_asset_ind | character varyi | YES | dol.form_5500.funding_gen_asset_ind | Funding gen asset (indicator flag) | ID: DOL_F5500_FUNDING_GEN_ASSET_IND | Forma |
| funding_insurance_ind | character varyi | YES | dol.form_5500.funding_insurance_ind | Funding insurance (indicator flag) | ID: DOL_F5500_FUNDING_INSURANCE_IND | Forma |
| funding_sec412_ind | character varyi | YES | dol.form_5500.funding_sec412_ind | Funding sec412 (indicator flag) | ID: DOL_F5500_FUNDING_SEC412_IND | Format: Y/N |
| funding_trust_ind | character varyi | YES | dol.form_5500.funding_trust_ind | Funding trust (indicator flag) | ID: DOL_F5500_FUNDING_TRUST_IND | Format: Y/N/X |
| initial_filing_ind | character varyi | YES | dol.form_5500.initial_filing_ind | Initial filing (indicator flag) | ID: DOL_F5500_INITIAL_FILING_IND | Format: Y/N |
| last_rpt_plan_name | character varyi | YES | dol.form_5500.last_rpt_plan_name | Last rpt plan (name) | ID: DOL_F5500_LAST_RPT_PLAN_NAME | Format: Up to 255 char |
| last_rpt_plan_num | character varyi | YES | dol.form_5500.last_rpt_plan_num | Last rpt plan (number/identifier) | ID: DOL_F5500_LAST_RPT_PLAN_NUM | Format: Up |
| last_rpt_spons_ein | character varyi | YES | dol.form_5500.last_rpt_spons_ein | Last rpt spons (Employer Identification Number) | ID: DOL_F5500_LAST_RPT_SPONS_E |
| last_rpt_spons_name | character varyi | YES | dol.form_5500.last_rpt_spons_name | Last rpt spons (name) | ID: DOL_F5500_LAST_RPT_SPONS_NAME | Format: Up to 255 ch |
| m1_receipt_confirmation_code | character varyi | YES | dol.form_5500.m1_receipt_confirmation_code | M1 receipt confirmation (code value) | ID: DOL_F5500_M1_RECEIPT_CONFIRMATION_COD |
| num_sch_a_attached_cnt | integer | YES | dol.form_5500.num_sch_a_attached_cnt | Num sch a attached (count/number) | ID: DOL_F5500_NUM_SCH_A_ATTACHED_CNT | Forma |
| num_sch_dcg_attached_cnt | numeric | YES | dol.form_5500.num_sch_dcg_attached_cnt | Num sch dcg attached (count/number) | ID: DOL_F5500_NUM_SCH_DCG_ATTACHED_CNT | F |
| partcp_account_bal_cnt | numeric | YES | dol.form_5500.partcp_account_bal_cnt | Participants with account balances | ID: DOL_F5500_PARTCP_ACCOUNT_BAL_CNT | Form |
| partcp_account_bal_cnt_boy | numeric | YES | dol.form_5500.partcp_account_bal_cnt_boy | Partcp account balance cnt boy | ID: DOL_F5500_PARTCP_ACCOUNT_BAL_CNT_BOY | Form |
| plan_eff_date | character varyi | YES | dol.form_5500.plan_eff_date | Plan effective date | ID: DOL_F5500_PLAN_EFF_DATE | Format: YYYY-MM-DD |
| plan_name | character varyi | YES | dol.form_5500.plan_name | Official name of the benefit plan | ID: DOL_F5500_PLAN_NAME | Format: Up to 500  |
| plan_number | character varyi | YES | dol.form_5500.plan_number | Plan number | ID: DOL_F5500_PLAN_NUMBER | Format: Up to 20 characters |
| preparer_firm_name | character varyi | YES | dol.form_5500.preparer_firm_name | Form Preparer firm (name) | ID: DOL_F5500_PREPARER_FIRM_NAME | Format: Up to 255 |
| preparer_foreign_address1 | character varyi | YES | dol.form_5500.preparer_foreign_address1 | Form Preparer foreign address1 | ID: DOL_F5500_PREPARER_FOREIGN_ADDRESS1 | Forma |
| preparer_foreign_address2 | character varyi | YES | dol.form_5500.preparer_foreign_address2 | Form Preparer foreign address2 | ID: DOL_F5500_PREPARER_FOREIGN_ADDRESS2 | Forma |
| preparer_foreign_city | character varyi | YES | dol.form_5500.preparer_foreign_city | Form Preparer foreign city | ID: DOL_F5500_PREPARER_FOREIGN_CITY | Format: Up to |
| preparer_foreign_cntry | character varyi | YES | dol.form_5500.preparer_foreign_cntry | Form Preparer foreign cntry | ID: DOL_F5500_PREPARER_FOREIGN_CNTRY | Format: Dec |
| preparer_foreign_postal_cd | character varyi | YES | dol.form_5500.preparer_foreign_postal_cd | Form Preparer foreign postal cd | ID: DOL_F5500_PREPARER_FOREIGN_POSTAL_CD | For |
| preparer_foreign_prov_state | character varyi | YES | dol.form_5500.preparer_foreign_prov_state | Form Preparer foreign province state | ID: DOL_F5500_PREPARER_FOREIGN_PROV_STATE |
| preparer_name | character varyi | YES | dol.form_5500.preparer_name | Form Preparer name | ID: DOL_F5500_PREPARER_NAME | Format: Up to 255 characters |
| preparer_phone_num | character varyi | YES | dol.form_5500.preparer_phone_num | Form Preparer phone (number/identifier) | ID: DOL_F5500_PREPARER_PHONE_NUM | For |
| preparer_phone_num_foreign | character varyi | YES | dol.form_5500.preparer_phone_num_foreign | Form Preparer phone number foreign | ID: DOL_F5500_PREPARER_PHONE_NUM_FOREIGN |  |
| preparer_us_address1 | character varyi | YES | dol.form_5500.preparer_us_address1 | Form Preparer us address1 | ID: DOL_F5500_PREPARER_US_ADDRESS1 | Format: Up to 2 |
| preparer_us_address2 | character varyi | YES | dol.form_5500.preparer_us_address2 | Form Preparer us address2 | ID: DOL_F5500_PREPARER_US_ADDRESS2 | Format: Up to 2 |
| preparer_us_city | character varyi | YES | dol.form_5500.preparer_us_city | Form Preparer us city | ID: DOL_F5500_PREPARER_US_CITY | Format: Up to 100 chara |
| preparer_us_state | character varyi | YES | dol.form_5500.preparer_us_state | Form Preparer us state | ID: DOL_F5500_PREPARER_US_STATE | Format: Up to 10 char |
| preparer_us_zip | character varyi | YES | dol.form_5500.preparer_us_zip | Form Preparer us (ZIP code) | ID: DOL_F5500_PREPARER_US_ZIP | Format: 5 or 9 dig |
| rtd_sep_partcp_fut_cnt | numeric | YES | dol.form_5500.rtd_sep_partcp_fut_cnt | Rtd separated participant fut (count/number) | ID: DOL_F5500_RTD_SEP_PARTCP_FUT_ |
| rtd_sep_partcp_rcvg_cnt | numeric | YES | dol.form_5500.rtd_sep_partcp_rcvg_cnt | Retired/separated participants receiving benefits | ID: DOL_F5500_RTD_SEP_PARTCP |
| sch_a_attached_ind | character varyi | YES | dol.form_5500.sch_a_attached_ind | Schedule A attached (indicator flag) | ID: DOL_F5500_SCH_A_ATTACHED_IND | Format |
| sch_c_attached_ind | character varyi | YES | dol.form_5500.sch_c_attached_ind | Sch c attached (indicator flag) | ID: DOL_F5500_SCH_C_ATTACHED_IND | Format: Y/N |
| sch_d_attached_ind | character varyi | YES | dol.form_5500.sch_d_attached_ind | Sch d attached (indicator flag) | ID: DOL_F5500_SCH_D_ATTACHED_IND | Format: Y/N |
| sch_dcg_attached_ind | character varyi | YES | dol.form_5500.sch_dcg_attached_ind | Sch dcg attached (indicator flag) | ID: DOL_F5500_SCH_DCG_ATTACHED_IND | Format: |
| sch_g_attached_ind | character varyi | YES | dol.form_5500.sch_g_attached_ind | Sch g attached (indicator flag) | ID: DOL_F5500_SCH_G_ATTACHED_IND | Format: Y/N |
| sch_h_attached_ind | character varyi | YES | dol.form_5500.sch_h_attached_ind | Sch h attached (indicator flag) | ID: DOL_F5500_SCH_H_ATTACHED_IND | Format: Y/N |
| sch_i_attached_ind | character varyi | YES | dol.form_5500.sch_i_attached_ind | Sch i attached (indicator flag) | ID: DOL_F5500_SCH_I_ATTACHED_IND | Format: Y/N |
| sch_mb_attached_ind | character varyi | YES | dol.form_5500.sch_mb_attached_ind | Sch mb attached (indicator flag) | ID: DOL_F5500_SCH_MB_ATTACHED_IND | Format: Y |
| sch_mep_attached_ind | character varyi | YES | dol.form_5500.sch_mep_attached_ind | Sch mep attached (indicator flag) | ID: DOL_F5500_SCH_MEP_ATTACHED_IND | Format: |
| sch_r_attached_ind | character varyi | YES | dol.form_5500.sch_r_attached_ind | Sch r attached (indicator flag) | ID: DOL_F5500_SCH_R_ATTACHED_IND | Format: Y/N |
| sch_sb_attached_ind | character varyi | YES | dol.form_5500.sch_sb_attached_ind | Sch sb attached (indicator flag) | ID: DOL_F5500_SCH_SB_ATTACHED_IND | Format: Y |
| sep_partcp_partl_vstd_cnt | numeric | YES | dol.form_5500.sep_partcp_partl_vstd_cnt | Sep participant partl vstd (count/number) | ID: DOL_F5500_SEP_PARTCP_PARTL_VSTD_ |
| short_plan_yr_ind | character varyi | YES | dol.form_5500.short_plan_yr_ind | Short plan yr (indicator flag) | ID: DOL_F5500_SHORT_PLAN_YR_IND | Format: Y/N/X |
| spons_dfe_care_of_name | character varyi | YES | dol.form_5500.spons_dfe_care_of_name | Plan Sponsor dfe care of (name) | ID: DOL_F5500_SPONS_DFE_CARE_OF_NAME | Format: |
| spons_dfe_dba_name | character varyi | YES | dol.form_5500.spons_dfe_dba_name | Plan Sponsor dfe dba (name) | ID: DOL_F5500_SPONS_DFE_DBA_NAME | Format: Up to 5 |
| spons_dfe_ein | character varyi | YES | dol.form_5500.spons_dfe_ein | Plan Sponsor dfe (Employer Identification Number) | ID: DOL_F5500_SPONS_DFE_EIN  |
| spons_dfe_loc_foreign_address1 | character varyi | YES | dol.form_5500.spons_dfe_loc_foreign_address1 | Plan Sponsor dfe location foreign address1 | ID: DOL_F5500_SPONS_DFE_LOC_FOREIGN |
| spons_dfe_loc_foreign_address2 | character varyi | YES | dol.form_5500.spons_dfe_loc_foreign_address2 | Plan Sponsor dfe location foreign address2 | ID: DOL_F5500_SPONS_DFE_LOC_FOREIGN |
| spons_dfe_loc_foreign_city | character varyi | YES | dol.form_5500.spons_dfe_loc_foreign_city | Plan Sponsor dfe location foreign city | ID: DOL_F5500_SPONS_DFE_LOC_FOREIGN_CIT |
| spons_dfe_loc_foreign_cntry | character varyi | YES | dol.form_5500.spons_dfe_loc_foreign_cntry | Plan Sponsor dfe location foreign cntry | ID: DOL_F5500_SPONS_DFE_LOC_FOREIGN_CN |
| spons_dfe_loc_forgn_postal_cd | character varyi | YES | dol.form_5500.spons_dfe_loc_forgn_postal_cd | Plan Sponsor dfe location forgn postal cd | ID: DOL_F5500_SPONS_DFE_LOC_FORGN_PO |
| spons_dfe_loc_forgn_prov_st | character varyi | YES | dol.form_5500.spons_dfe_loc_forgn_prov_st | Plan Sponsor dfe location forgn province st | ID: DOL_F5500_SPONS_DFE_LOC_FORGN_ |
| spons_dfe_loc_us_address1 | character varyi | YES | dol.form_5500.spons_dfe_loc_us_address1 | Plan Sponsor dfe location us address1 | ID: DOL_F5500_SPONS_DFE_LOC_US_ADDRESS1  |
| spons_dfe_loc_us_address2 | character varyi | YES | dol.form_5500.spons_dfe_loc_us_address2 | Plan Sponsor dfe location us address2 | ID: DOL_F5500_SPONS_DFE_LOC_US_ADDRESS2  |
| spons_dfe_loc_us_city | character varyi | YES | dol.form_5500.spons_dfe_loc_us_city | Plan Sponsor dfe location us city | ID: DOL_F5500_SPONS_DFE_LOC_US_CITY | Format |
| spons_dfe_loc_us_state | character varyi | YES | dol.form_5500.spons_dfe_loc_us_state | Plan Sponsor dfe location us state | ID: DOL_F5500_SPONS_DFE_LOC_US_STATE | Form |
| spons_dfe_loc_us_zip | character varyi | YES | dol.form_5500.spons_dfe_loc_us_zip | Plan Sponsor dfe location us (ZIP code) | ID: DOL_F5500_SPONS_DFE_LOC_US_ZIP | F |
| spons_dfe_mail_foreign_addr1 | character varyi | YES | dol.form_5500.spons_dfe_mail_foreign_addr1 | Plan Sponsor dfe mail foreign addr1 | ID: DOL_F5500_SPONS_DFE_MAIL_FOREIGN_ADDR1 |
| spons_dfe_mail_foreign_addr2 | character varyi | YES | dol.form_5500.spons_dfe_mail_foreign_addr2 | Plan Sponsor dfe mail foreign addr2 | ID: DOL_F5500_SPONS_DFE_MAIL_FOREIGN_ADDR2 |
| spons_dfe_mail_foreign_city | character varyi | YES | dol.form_5500.spons_dfe_mail_foreign_city | Plan Sponsor dfe mail foreign city | ID: DOL_F5500_SPONS_DFE_MAIL_FOREIGN_CITY | |
| spons_dfe_mail_foreign_cntry | character varyi | YES | dol.form_5500.spons_dfe_mail_foreign_cntry | Plan Sponsor dfe mail foreign cntry | ID: DOL_F5500_SPONS_DFE_MAIL_FOREIGN_CNTRY |
| spons_dfe_mail_forgn_postal_cd | character varyi | YES | dol.form_5500.spons_dfe_mail_forgn_postal_cd | Plan Sponsor dfe mail forgn postal cd | ID: DOL_F5500_SPONS_DFE_MAIL_FORGN_POSTA |
| spons_dfe_mail_forgn_prov_st | character varyi | YES | dol.form_5500.spons_dfe_mail_forgn_prov_st | Plan Sponsor dfe mail forgn province st | ID: DOL_F5500_SPONS_DFE_MAIL_FORGN_PRO |
| spons_dfe_mail_us_address1 | character varyi | YES | dol.form_5500.spons_dfe_mail_us_address1 | Sponsor mailing address line 1 | ID: DOL_F5500_SPONS_DFE_MAIL_US_ADDRESS1 | Form |
| spons_dfe_mail_us_address2 | character varyi | YES | dol.form_5500.spons_dfe_mail_us_address2 | Sponsor mailing address line 2 | ID: DOL_F5500_SPONS_DFE_MAIL_US_ADDRESS2 | Form |
| spons_dfe_mail_us_city | character varyi | YES | dol.form_5500.spons_dfe_mail_us_city | Sponsor mailing city | ID: DOL_F5500_SPONS_DFE_MAIL_US_CITY | Format: Up to 100  |
| spons_dfe_mail_us_state | character varyi | YES | dol.form_5500.spons_dfe_mail_us_state | Sponsor mailing state (2-letter) | ID: DOL_F5500_SPONS_DFE_MAIL_US_STATE | Forma |
| spons_dfe_mail_us_zip | character varyi | YES | dol.form_5500.spons_dfe_mail_us_zip | Sponsor mailing ZIP code | ID: DOL_F5500_SPONS_DFE_MAIL_US_ZIP | Format: 5 or 9  |
| spons_dfe_phone_num | character varyi | YES | dol.form_5500.spons_dfe_phone_num | Sponsor phone number | ID: DOL_F5500_SPONS_DFE_PHONE_NUM | Format: Up to 30 char |
| spons_dfe_phone_num_foreign | character varyi | YES | dol.form_5500.spons_dfe_phone_num_foreign | Plan Sponsor dfe phone number foreign | ID: DOL_F5500_SPONS_DFE_PHONE_NUM_FOREIG |
| spons_dfe_pn | character varyi | YES | dol.form_5500.spons_dfe_pn | Plan Sponsor dfe pn | ID: DOL_F5500_SPONS_DFE_PN | Format: Up to 255 characters |
| spons_manual_signed_date | character varyi | YES | dol.form_5500.spons_manual_signed_date | Plan Sponsor manual signed (date) | ID: DOL_F5500_SPONS_MANUAL_SIGNED_DATE | For |
| spons_manual_signed_name | character varyi | YES | dol.form_5500.spons_manual_signed_name | Plan Sponsor manual signed (name) | ID: DOL_F5500_SPONS_MANUAL_SIGNED_NAME | For |
| spons_signed_date | character varyi | YES | dol.form_5500.spons_signed_date | Plan Sponsor signed (date) | ID: DOL_F5500_SPONS_SIGNED_DATE | Format: YYYY-MM-D |
| spons_signed_name | character varyi | YES | dol.form_5500.spons_signed_name | Plan Sponsor signed (name) | ID: DOL_F5500_SPONS_SIGNED_NAME | Format: Up to 255 |
| sponsor_dfe_ein | character varyi | NO | dol.form_5500.sponsor_dfe_ein | Employer Identification Number of sponsor | ID: DOL_F5500_SPONSOR_DFE_EIN | Form |
| sponsor_dfe_name | character varyi | NO | dol.form_5500.sponsor_dfe_name | Legal name of the plan sponsor or DFE | ID: DOL_F5500_SPONSOR_DFE_NAME | Format: |
| subj_m1_filing_req_ind | character varyi | YES | dol.form_5500.subj_m1_filing_req_ind | Subj m1 filing req (indicator flag) | ID: DOL_F5500_SUBJ_M1_FILING_REQ_IND | For |
| subtl_act_rtd_sep_cnt | numeric | YES | dol.form_5500.subtl_act_rtd_sep_cnt | Subtl act retired sep (count/number) | ID: DOL_F5500_SUBTL_ACT_RTD_SEP_CNT | For |
| tot_act_partcp_boy_cnt | numeric | YES | dol.form_5500.tot_act_partcp_boy_cnt | Tot act participant boy (count/number) | ID: DOL_F5500_TOT_ACT_PARTCP_BOY_CNT |  |
| tot_act_rtd_sep_benef_cnt | numeric | YES | dol.form_5500.tot_act_rtd_sep_benef_cnt | Tot act retired separated benef (count/number) | ID: DOL_F5500_TOT_ACT_RTD_SEP_B |
| tot_active_partcp_cnt | integer | YES | dol.form_5500.tot_active_partcp_cnt | Total active participants | ID: DOL_F5500_TOT_ACTIVE_PARTCP_CNT | Format: Whole  |
| tot_partcp_boy_cnt | integer | YES | dol.form_5500.tot_partcp_boy_cnt | Total participants at beginning of year | ID: DOL_F5500_TOT_PARTCP_BOY_CNT | For |
| type_dfe_plan_entity_cd | character varyi | YES | dol.form_5500.type_dfe_plan_entity_cd | Type of DFE plan entity code | ID: DOL_F5500_TYPE_DFE_PLAN_ENTITY_CD | Format: U |
| type_pension_bnft_code | character varyi | YES | dol.form_5500.type_pension_bnft_code | Type pension bnft (code value) | ID: DOL_F5500_TYPE_PENSION_BNFT_CODE | Format:  |
| type_plan_entity_cd | character varyi | YES | dol.form_5500.type_plan_entity_cd | Type of plan entity code | ID: DOL_F5500_TYPE_PLAN_ENTITY_CD | Format: Up to 255 |
| type_welfare_bnft_code | character varyi | YES | dol.form_5500.type_welfare_bnft_code | Type welfare bnft (code value) | ID: DOL_F5500_TYPE_WELFARE_BNFT_CODE | Format:  |
| updated_at | timestamp with  | NO | dol.form_5500.updated_at | Record last update timestamp | ID: DOL_F5500_UPDATED_AT | Format: YYYY-MM-DD HH: |
| valid_admin_signature | character varyi | YES | dol.form_5500.valid_admin_signature | Valid administrative signature | ID: DOL_F5500_VALID_ADMIN_SIGNATURE | Format: U |
| valid_dfe_signature | character varyi | YES | dol.form_5500.valid_dfe_signature | Valid Direct Filing Entity signature | ID: DOL_F5500_VALID_DFE_SIGNATURE | Forma |
| valid_sponsor_signature | character varyi | YES | dol.form_5500.valid_sponsor_signature | Valid sponsor signature | ID: DOL_F5500_VALID_SPONSOR_SIGNATURE | Format: Up to  |

### LEAF: dol.form_5500_icp_filtered (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| filter_id | integer | NO | dol.form_5500_icp_filtered.filter_id | Filter Id |
| normalized_name | text | YES | dol.form_5500_icp_filtered.normalized_name | Normalized Name |
| spons_dfe_mail_us_city | character varyi | YES | dol.form_5500_icp_filtered.spons_dfe_mail_us_city | Spons Dfe Mail Us City |
| spons_dfe_mail_us_state | character varyi | YES | dol.form_5500_icp_filtered.spons_dfe_mail_us_state | Spons Dfe Mail Us State |
| sponsor_dfe_ein | character varyi | YES | dol.form_5500_icp_filtered.sponsor_dfe_ein | Sponsor Dfe Ein |
| sponsor_dfe_name | character varyi | YES | dol.form_5500_icp_filtered.sponsor_dfe_name | Sponsor Dfe Name |
| tot_active_partcp_cnt | integer | YES | dol.form_5500_icp_filtered.tot_active_partcp_cnt | Tot Active Partcp Cnt |

### LEAF: dol.form_5500_sf (196 columns, 196 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | YES | dol.form_5500_sf.ack_id | DOL acknowledgment ID for the filing | ID: DOL_F5500SF_ACK_ID | Format: Up to 25 |
| collectively_bargained | character varyi | YES | dol.form_5500_sf.collectively_bargained | Collectively bargained | ID: DOL_F5500SF_COLLECTIVELY_BARGAINED | Format: Up to  |
| company_unique_id | text | YES | dol.form_5500_sf.company_unique_id | Company unique id | ID: DOL_F5500SF_COMPANY_UNIQUE_ID | Format: Variable length  |
| created_at | timestamp with  | YES | dol.form_5500_sf.created_at | Record creation timestamp | ID: DOL_F5500SF_CREATED_AT | Format: YYYY-MM-DD HH:M |
| date_received | character varyi | YES | dol.form_5500_sf.date_received | Date filing was received by DOL | ID: DOL_F5500SF_DATE_RECEIVED | Format: Up to  |
| filing_id | uuid | NO | dol.form_5500_sf.filing_id | Unique filing identifier (UUID) | ID: DOL_F5500SF_FILING_ID | Format: xxxxxxxx-x |
| filing_status | character varyi | YES | dol.form_5500_sf.filing_status | Filing status | ID: DOL_F5500SF_FILING_STATUS | Format: Up to 255 characters |
| form_year | character varyi | YES | dol.form_5500_sf.form_year | Tax/plan year for this filing | ID: DOL_F5500SF_FORM_YEAR | Format: Up to 10 cha |
| sf_401k_current_year_adp_ind | character varyi | YES | dol.form_5500_sf.sf_401k_current_year_adp_ind | Short Form (5500-SF) 401k current year adp (indicator flag) | ID: DOL_F5500SF_SF |
| sf_401k_current_year_adp_test_ind | character varyi | YES | dol.form_5500_sf.sf_401k_current_year_adp_test_ind | Short Form (5500-SF) 401k current year adp test (indicator flag) | ID: DOL_F5500 |
| sf_401k_design_based_safe_harbor_ind | character varyi | YES | dol.form_5500_sf.sf_401k_design_based_safe_harbor_ | Short Form (5500-SF) 401k design based safe harbor (indicator flag) | ID: DOL_F5 |
| sf_401k_design_based_safe_ind | character varyi | YES | dol.form_5500_sf.sf_401k_design_based_safe_ind | Short Form (5500-SF) 401k design based safe (indicator flag) | ID: DOL_F5500SF_S |
| sf_401k_na_ind | character varyi | YES | dol.form_5500_sf.sf_401k_na_ind | Short Form (5500-SF) 401k na (indicator flag) | ID: DOL_F5500SF_SF_401K_NA_IND | |
| sf_401k_plan_ind | character varyi | YES | dol.form_5500_sf.sf_401k_plan_ind | Short Form (5500-SF) 401k plan (indicator flag) | ID: DOL_F5500SF_SF_401K_PLAN_I |
| sf_401k_prior_year_adp_ind | character varyi | YES | dol.form_5500_sf.sf_401k_prior_year_adp_ind | Short Form (5500-SF) 401k prior year adp (indicator flag) | ID: DOL_F5500SF_SF_4 |
| sf_401k_prior_year_adp_test_ind | character varyi | YES | dol.form_5500_sf.sf_401k_prior_year_adp_test_ind | Short Form (5500-SF) 401k prior year adp test (indicator flag) | ID: DOL_F5500SF |
| sf_401k_satisfy_rqmts_ind | character varyi | YES | dol.form_5500_sf.sf_401k_satisfy_rqmts_ind | Short Form (5500-SF) 401k satisfy rqmts (indicator flag) | ID: DOL_F5500SF_SF_40 |
| sf_5558_application_filed_ind | character varyi | YES | dol.form_5500_sf.sf_5558_application_filed_ind | Short Form (5500-SF) 5558 application filed (indicator flag) | ID: DOL_F5500SF_S |
| sf_admin_addrss_same_spon_ind | character varyi | YES | dol.form_5500_sf.sf_admin_addrss_same_spon_ind | Plan Administrator (SF) addrss same spon (indicator flag) | ID: DOL_F5500SF_SF_A |
| sf_admin_care_of_name | character varyi | YES | dol.form_5500_sf.sf_admin_care_of_name | Plan Administrator (SF) care of (name) | ID: DOL_F5500SF_SF_ADMIN_CARE_OF_NAME | |
| sf_admin_ein | character varyi | YES | dol.form_5500_sf.sf_admin_ein | Plan Administrator (SF) ein | ID: DOL_F5500SF_SF_ADMIN_EIN | Format: 9 digits (X |
| sf_admin_foreign_address1 | character varyi | YES | dol.form_5500_sf.sf_admin_foreign_address1 | Plan Administrator (SF) foreign address1 | ID: DOL_F5500SF_SF_ADMIN_FOREIGN_ADDR |
| sf_admin_foreign_address2 | character varyi | YES | dol.form_5500_sf.sf_admin_foreign_address2 | Plan Administrator (SF) foreign address2 | ID: DOL_F5500SF_SF_ADMIN_FOREIGN_ADDR |
| sf_admin_foreign_city | character varyi | YES | dol.form_5500_sf.sf_admin_foreign_city | Plan Administrator (SF) foreign city | ID: DOL_F5500SF_SF_ADMIN_FOREIGN_CITY | F |
| sf_admin_foreign_cntry | character varyi | YES | dol.form_5500_sf.sf_admin_foreign_cntry | Plan Administrator (SF) foreign cntry | ID: DOL_F5500SF_SF_ADMIN_FOREIGN_CNTRY | |
| sf_admin_foreign_postal_cd | character varyi | YES | dol.form_5500_sf.sf_admin_foreign_postal_cd | Plan Administrator (SF) foreign postal cd | ID: DOL_F5500SF_SF_ADMIN_FOREIGN_POS |
| sf_admin_foreign_prov_state | character varyi | YES | dol.form_5500_sf.sf_admin_foreign_prov_state | Plan Administrator (SF) foreign province state | ID: DOL_F5500SF_SF_ADMIN_FOREIG |
| sf_admin_manual_sign_date | character varyi | YES | dol.form_5500_sf.sf_admin_manual_sign_date | Plan Administrator (SF) manual sign (date) | ID: DOL_F5500SF_SF_ADMIN_MANUAL_SIG |
| sf_admin_manual_signed_name | character varyi | YES | dol.form_5500_sf.sf_admin_manual_signed_name | Plan Administrator (SF) manual signed (name) | ID: DOL_F5500SF_SF_ADMIN_MANUAL_S |
| sf_admin_name | character varyi | YES | dol.form_5500_sf.sf_admin_name | Plan Administrator (SF) name | ID: DOL_F5500SF_SF_ADMIN_NAME | Format: Up to 255 |
| sf_admin_name_same_spon_ind | character varyi | YES | dol.form_5500_sf.sf_admin_name_same_spon_ind | Plan Administrator (SF) name same spon (indicator flag) | ID: DOL_F5500SF_SF_ADM |
| sf_admin_phone_num | character varyi | YES | dol.form_5500_sf.sf_admin_phone_num | Plan Administrator (SF) phone (number/identifier) | ID: DOL_F5500SF_SF_ADMIN_PHO |
| sf_admin_phone_num_foreign | character varyi | YES | dol.form_5500_sf.sf_admin_phone_num_foreign | Plan Administrator (SF) phone number foreign | ID: DOL_F5500SF_SF_ADMIN_PHONE_NU |
| sf_admin_signed_date | character varyi | YES | dol.form_5500_sf.sf_admin_signed_date | Plan Administrator (SF) signed (date) | ID: DOL_F5500SF_SF_ADMIN_SIGNED_DATE | F |
| sf_admin_signed_name | character varyi | YES | dol.form_5500_sf.sf_admin_signed_name | Plan Administrator (SF) signed (name) | ID: DOL_F5500SF_SF_ADMIN_SIGNED_NAME | F |
| sf_admin_srvc_providers_amt | numeric | YES | dol.form_5500_sf.sf_admin_srvc_providers_amt | Plan Administrator (SF) srvc providers (amount in dollars) | ID: DOL_F5500SF_SF_ |
| sf_admin_us_address1 | character varyi | YES | dol.form_5500_sf.sf_admin_us_address1 | Plan Administrator (SF) us address1 | ID: DOL_F5500SF_SF_ADMIN_US_ADDRESS1 | For |
| sf_admin_us_address2 | character varyi | YES | dol.form_5500_sf.sf_admin_us_address2 | Plan Administrator (SF) us address2 | ID: DOL_F5500SF_SF_ADMIN_US_ADDRESS2 | For |
| sf_admin_us_city | character varyi | YES | dol.form_5500_sf.sf_admin_us_city | Plan Administrator (SF) us city | ID: DOL_F5500SF_SF_ADMIN_US_CITY | Format: Up  |
| sf_admin_us_state | character varyi | YES | dol.form_5500_sf.sf_admin_us_state | Plan Administrator (SF) us state | ID: DOL_F5500SF_SF_ADMIN_US_STATE | Format: U |
| sf_admin_us_zip | character varyi | YES | dol.form_5500_sf.sf_admin_us_zip | Plan Administrator (SF) us (ZIP code) | ID: DOL_F5500SF_SF_ADMIN_US_ZIP | Format |
| sf_adopted_plan_perm_sec_act | character varyi | YES | dol.form_5500_sf.sf_adopted_plan_perm_sec_act | Short Form (5500-SF) adopted plan perm sec act | ID: DOL_F5500SF_SF_ADOPTED_PLAN |
| sf_adp_acp_test_ind | character varyi | YES | dol.form_5500_sf.sf_adp_acp_test_ind | Short Form (5500-SF) adp acp test (indicator flag) | ID: DOL_F5500SF_SF_ADP_ACP_ |
| sf_all_plan_ast_distrib_ind | character varyi | YES | dol.form_5500_sf.sf_all_plan_ast_distrib_ind | Short Form (5500-SF) all plan ast distrib (indicator flag) | ID: DOL_F5500SF_SF_ |
| sf_amended_ind | character varyi | YES | dol.form_5500_sf.sf_amended_ind | Short Form (5500-SF) amended (indicator flag) | ID: DOL_F5500SF_SF_AMENDED_IND | |
| sf_broker_fees_paid_amt | numeric | YES | dol.form_5500_sf.sf_broker_fees_paid_amt | Short Form (5500-SF) broker fees paid (amount in dollars) | ID: DOL_F5500SF_SF_B |
| sf_broker_fees_paid_ind | character varyi | YES | dol.form_5500_sf.sf_broker_fees_paid_ind | Short Form (5500-SF) broker fees paid (indicator flag) | ID: DOL_F5500SF_SF_BROK |
| sf_business_code | character varyi | YES | dol.form_5500_sf.sf_business_code | Short Form (5500-SF) business (code value) | ID: DOL_F5500SF_SF_BUSINESS_CODE |  |
| sf_comply_blackout_notice_ind | character varyi | YES | dol.form_5500_sf.sf_comply_blackout_notice_ind | Short Form (5500-SF) comply blackout notice (indicator flag) | ID: DOL_F5500SF_S |
| sf_corrective_deemed_distr_amt | numeric | YES | dol.form_5500_sf.sf_corrective_deemed_distr_amt | Short Form (5500-SF) corrective deemed distr (amount in dollars) | ID: DOL_F5500 |
| sf_covered_pbgc_insurance_ind | character varyi | YES | dol.form_5500_sf.sf_covered_pbgc_insurance_ind | Short Form (5500-SF) covered pbgc insurance (indicator flag) | ID: DOL_F5500SF_S |
| sf_db_plan_funding_reqd_ind | character varyi | YES | dol.form_5500_sf.sf_db_plan_funding_reqd_ind | Short Form (5500-SF) db plan funding reqd (indicator flag) | ID: DOL_F5500SF_SF_ |
| sf_dc_plan_funding_reqd_ind | character varyi | YES | dol.form_5500_sf.sf_dc_plan_funding_reqd_ind | Short Form (5500-SF) dc plan funding reqd (indicator flag) | ID: DOL_F5500SF_SF_ |
| sf_dfvc_program_ind | character varyi | YES | dol.form_5500_sf.sf_dfvc_program_ind | Short Form (5500-SF) dfvc program (indicator flag) | ID: DOL_F5500SF_SF_DFVC_PRO |
| sf_distrib_made_employe_62_ind | character varyi | YES | dol.form_5500_sf.sf_distrib_made_employe_62_ind | Short Form (5500-SF) distrib made employe 62 (indicator flag) | ID: DOL_F5500SF_ |
| sf_eligible_assets_ind | character varyi | YES | dol.form_5500_sf.sf_eligible_assets_ind | Short Form (5500-SF) eligible assets (indicator flag) | ID: DOL_F5500SF_SF_ELIGI |
| sf_emplr_contrib_income_amt | numeric | YES | dol.form_5500_sf.sf_emplr_contrib_income_amt | Short Form (5500-SF) emplr contribution income (amount in dollars) | ID: DOL_F55 |
| sf_emplr_contrib_paid_amt | numeric | YES | dol.form_5500_sf.sf_emplr_contrib_paid_amt | Short Form (5500-SF) emplr contribution paid (amount in dollars) | ID: DOL_F5500 |
| sf_ext_automatic_ind | character varyi | YES | dol.form_5500_sf.sf_ext_automatic_ind | Short Form (5500-SF) ext automatic (indicator flag) | ID: DOL_F5500SF_SF_EXT_AUT |
| sf_ext_special_ind | character varyi | YES | dol.form_5500_sf.sf_ext_special_ind | Short Form (5500-SF) ext special (indicator flag) | ID: DOL_F5500SF_SF_EXT_SPECI |
| sf_ext_special_text | text | YES | dol.form_5500_sf.sf_ext_special_text | Short Form (5500-SF) ext special (text description) | ID: DOL_F5500SF_SF_EXT_SPE |
| sf_fail_provide_benef_due_amt | numeric | YES | dol.form_5500_sf.sf_fail_provide_benef_due_amt | Short Form (5500-SF) fail provide benef due (amount in dollars) | ID: DOL_F5500S |
| sf_fail_provide_benef_due_ind | character varyi | YES | dol.form_5500_sf.sf_fail_provide_benef_due_ind | Short Form (5500-SF) fail provide benef due (indicator flag) | ID: DOL_F5500SF_S |
| sf_fail_transmit_contrib_amt | numeric | YES | dol.form_5500_sf.sf_fail_transmit_contrib_amt | Short Form (5500-SF) fail transmit contrib (amount in dollars) | ID: DOL_F5500SF |
| sf_fail_transmit_contrib_ind | character varyi | YES | dol.form_5500_sf.sf_fail_transmit_contrib_ind | Short Form (5500-SF) fail transmit contrib (indicator flag) | ID: DOL_F5500SF_SF |
| sf_fav_determ_ltr_date | character varyi | YES | dol.form_5500_sf.sf_fav_determ_ltr_date | Short Form (5500-SF) fav determination ltr (date) | ID: DOL_F5500SF_SF_FAV_DETER |
| sf_fdcry_trus_cus_phon_numfore | character varyi | YES | dol.form_5500_sf.sf_fdcry_trus_cus_phon_numfore | Short Form (5500-SF) fdcry trus cus phon numfore | ID: DOL_F5500SF_SF_FDCRY_TRUS |
| sf_fdcry_trust_ein | character varyi | YES | dol.form_5500_sf.sf_fdcry_trust_ein | Short Form (5500-SF) fdcry trust (Employer Identification Number) | ID: DOL_F550 |
| sf_fdcry_trust_name | character varyi | YES | dol.form_5500_sf.sf_fdcry_trust_name | Short Form (5500-SF) fdcry trust (name) | ID: DOL_F5500SF_SF_FDCRY_TRUST_NAME |  |
| sf_fdcry_truste_cust_name | character varyi | YES | dol.form_5500_sf.sf_fdcry_truste_cust_name | Short Form (5500-SF) fdcry truste cust (name) | ID: DOL_F5500SF_SF_FDCRY_TRUSTE_ |
| sf_fdcry_truste_cust_phone_num | character varyi | YES | dol.form_5500_sf.sf_fdcry_truste_cust_phone_num | Short Form (5500-SF) fdcry truste cust phone (number/identifier) | ID: DOL_F5500 |
| sf_final_filing_ind | character varyi | YES | dol.form_5500_sf.sf_final_filing_ind | Short Form (5500-SF) final filing (indicator flag) | ID: DOL_F5500SF_SF_FINAL_FI |
| sf_funding_deadline_ind | character varyi | YES | dol.form_5500_sf.sf_funding_deadline_ind | Short Form (5500-SF) funding deadline (indicator flag) | ID: DOL_F5500SF_SF_FUND |
| sf_funding_deficiency_amt | numeric | YES | dol.form_5500_sf.sf_funding_deficiency_amt | Short Form (5500-SF) funding deficiency (amount in dollars) | ID: DOL_F5500SF_SF |
| sf_in_service_distrib_amt | numeric | YES | dol.form_5500_sf.sf_in_service_distrib_amt | Short Form (5500-SF) in service distrib (amount in dollars) | ID: DOL_F5500SF_SF |
| sf_in_service_distrib_ind | character varyi | YES | dol.form_5500_sf.sf_in_service_distrib_ind | Short Form (5500-SF) in service distrib (indicator flag) | ID: DOL_F5500SF_SF_IN |
| sf_initial_filing_ind | character varyi | YES | dol.form_5500_sf.sf_initial_filing_ind | Short Form (5500-SF) initial filing (indicator flag) | ID: DOL_F5500SF_SF_INITIA |
| sf_iqpa_waiver_ind | character varyi | YES | dol.form_5500_sf.sf_iqpa_waiver_ind | Short Form (5500-SF) iqpa waiver (indicator flag) | ID: DOL_F5500SF_SF_IQPA_WAIV |
| sf_last_opin_advi_date | character varyi | YES | dol.form_5500_sf.sf_last_opin_advi_date | Short Form (5500-SF) last opinion advi (date) | ID: DOL_F5500SF_SF_LAST_OPIN_ADV |
| sf_last_opin_advi_serial_num | character varyi | YES | dol.form_5500_sf.sf_last_opin_advi_serial_num | Short Form (5500-SF) last opinion advisory serial (number/identifier) | ID: DOL_ |
| sf_last_plan_amendment_date | character varyi | YES | dol.form_5500_sf.sf_last_plan_amendment_date | Short Form (5500-SF) last plan amendment (date) | ID: DOL_F5500SF_SF_LAST_PLAN_A |
| sf_last_rpt_plan_name | character varyi | YES | dol.form_5500_sf.sf_last_rpt_plan_name | Short Form (5500-SF) last rpt plan (name) | ID: DOL_F5500SF_SF_LAST_RPT_PLAN_NAM |
| sf_last_rpt_plan_num | character varyi | YES | dol.form_5500_sf.sf_last_rpt_plan_num | Short Form (5500-SF) last rpt plan (number/identifier) | ID: DOL_F5500SF_SF_LAST |
| sf_last_rpt_spons_ein | character varyi | YES | dol.form_5500_sf.sf_last_rpt_spons_ein | Short Form (5500-SF) last rpt spons (Employer Identification Number) | ID: DOL_F |
| sf_last_rpt_spons_name | character varyi | YES | dol.form_5500_sf.sf_last_rpt_spons_name | Short Form (5500-SF) last rpt spons (name) | ID: DOL_F5500SF_SF_LAST_RPT_SPONS_N |
| sf_loss_discv_dur_year_amt | numeric | YES | dol.form_5500_sf.sf_loss_discv_dur_year_amt | Short Form (5500-SF) loss discv dur year (amount in dollars) | ID: DOL_F5500SF_S |
| sf_loss_discv_dur_year_ind | character varyi | YES | dol.form_5500_sf.sf_loss_discv_dur_year_ind | Short Form (5500-SF) loss discv dur year (indicator flag) | ID: DOL_F5500SF_SF_L |
| sf_min_req_distrib_ind | character varyi | YES | dol.form_5500_sf.sf_min_req_distrib_ind | Short Form (5500-SF) min req distrib (indicator flag) | ID: DOL_F5500SF_SF_MIN_R |
| sf_mthd_avg_bnft_test_ind | character varyi | YES | dol.form_5500_sf.sf_mthd_avg_bnft_test_ind | Short Form (5500-SF) mthd avg benefit test (indicator flag) | ID: DOL_F5500SF_SF |
| sf_mthd_na_ind | character varyi | YES | dol.form_5500_sf.sf_mthd_na_ind | Short Form (5500-SF) mthd na (indicator flag) | ID: DOL_F5500SF_SF_MTHD_NA_IND | |
| sf_mthd_ratio_prcnt_test_ind | character varyi | YES | dol.form_5500_sf.sf_mthd_ratio_prcnt_test_ind | Short Form (5500-SF) mthd ratio prcnt test (indicator flag) | ID: DOL_F5500SF_SF |
| sf_mthd_used_satisfy_rqmts_ind | character varyi | YES | dol.form_5500_sf.sf_mthd_used_satisfy_rqmts_ind | Short Form (5500-SF) mthd used satisfy rqmts (indicator flag) | ID: DOL_F5500SF_ |
| sf_net_assets_boy_amt | numeric | YES | dol.form_5500_sf.sf_net_assets_boy_amt | Short Form (5500-SF) net assets boy (amount in dollars) | ID: DOL_F5500SF_SF_NET |
| sf_net_assets_eoy_amt | numeric | YES | dol.form_5500_sf.sf_net_assets_eoy_amt | Short Form (5500-SF) net assets eoy (amount in dollars) | ID: DOL_F5500SF_SF_NET |
| sf_net_income_amt | numeric | YES | dol.form_5500_sf.sf_net_income_amt | Short Form (5500-SF) net income (amount in dollars) | ID: DOL_F5500SF_SF_NET_INC |
| sf_opin_letter_date | character varyi | YES | dol.form_5500_sf.sf_opin_letter_date | Short Form (5500-SF) opin letter (date) | ID: DOL_F5500SF_SF_OPIN_LETTER_DATE |  |
| sf_opin_letter_serial_num | character varyi | YES | dol.form_5500_sf.sf_opin_letter_serial_num | Short Form (5500-SF) opin letter serial (number/identifier) | ID: DOL_F5500SF_SF |
| sf_oth_contrib_rcvd_amt | numeric | YES | dol.form_5500_sf.sf_oth_contrib_rcvd_amt | Short Form (5500-SF) oth contribution rcvd (amount in dollars) | ID: DOL_F5500SF |
| sf_oth_expenses_amt | numeric | YES | dol.form_5500_sf.sf_oth_expenses_amt | Short Form (5500-SF) oth expenses (amount in dollars) | ID: DOL_F5500SF_SF_OTH_E |
| sf_other_income_amt | numeric | YES | dol.form_5500_sf.sf_other_income_amt | Short Form (5500-SF) other income (amount in dollars) | ID: DOL_F5500SF_SF_OTHER |
| sf_partcp_account_bal_cnt | numeric | YES | dol.form_5500_sf.sf_partcp_account_bal_cnt | Short Form (5500-SF) partcp account bal (count/number) | ID: DOL_F5500SF_SF_PART |
| sf_partcp_account_bal_cnt_boy | character varyi | YES | dol.form_5500_sf.sf_partcp_account_bal_cnt_boy | Short Form (5500-SF) partcp account balance cnt boy | ID: DOL_F5500SF_SF_PARTCP_ |
| sf_partcp_loans_eoy_amt | numeric | YES | dol.form_5500_sf.sf_partcp_loans_eoy_amt | Short Form (5500-SF) partcp loans eoy (amount in dollars) | ID: DOL_F5500SF_SF_P |
| sf_partcp_loans_ind | character varyi | YES | dol.form_5500_sf.sf_partcp_loans_ind | Short Form (5500-SF) partcp loans (indicator flag) | ID: DOL_F5500SF_SF_PARTCP_L |
| sf_particip_contrib_income_amt | numeric | YES | dol.form_5500_sf.sf_particip_contrib_income_amt | Short Form (5500-SF) particip contribution income (amount in dollars) | ID: DOL_ |
| sf_party_in_int_not_rptd_amt | numeric | YES | dol.form_5500_sf.sf_party_in_int_not_rptd_amt | Short Form (5500-SF) party in int not rptd (amount in dollars) | ID: DOL_F5500SF |
| sf_party_in_int_not_rptd_ind | character varyi | YES | dol.form_5500_sf.sf_party_in_int_not_rptd_ind | Short Form (5500-SF) party in int not rptd (indicator flag) | ID: DOL_F5500SF_SF |
| sf_pbgc_notified_cd | character varyi | YES | dol.form_5500_sf.sf_pbgc_notified_cd | Short Form (5500-SF) pbgc notified cd | ID: DOL_F5500SF_SF_PBGC_NOTIFIED_CD | Fo |
| sf_pbgc_notified_explan_text | text | YES | dol.form_5500_sf.sf_pbgc_notified_explan_text | Short Form (5500-SF) pbgc notified explan (text description) | ID: DOL_F5500SF_S |
| sf_plan_blackout_period_ind | character varyi | YES | dol.form_5500_sf.sf_plan_blackout_period_ind | Short Form (5500-SF) plan blackout period (indicator flag) | ID: DOL_F5500SF_SF_ |
| sf_plan_eff_date | character varyi | YES | dol.form_5500_sf.sf_plan_eff_date | Short Form (5500-SF) plan eff (date) | ID: DOL_F5500SF_SF_PLAN_EFF_DATE | Format |
| sf_plan_entity_cd | character varyi | YES | dol.form_5500_sf.sf_plan_entity_cd | Short Form (5500-SF) plan entity cd | ID: DOL_F5500SF_SF_PLAN_ENTITY_CD | Format |
| sf_plan_ins_fdlty_bond_amt | numeric | YES | dol.form_5500_sf.sf_plan_ins_fdlty_bond_amt | Short Form (5500-SF) plan ins fdlty bond (amount in dollars) | ID: DOL_F5500SF_S |
| sf_plan_ins_fdlty_bond_ind | character varyi | YES | dol.form_5500_sf.sf_plan_ins_fdlty_bond_ind | Short Form (5500-SF) plan ins fdlty bond (indicator flag) | ID: DOL_F5500SF_SF_P |
| sf_plan_maintain_us_terri_ind | character varyi | YES | dol.form_5500_sf.sf_plan_maintain_us_terri_ind | Short Form (5500-SF) plan maintain us terri (indicator flag) | ID: DOL_F5500SF_S |
| sf_plan_name | character varyi | YES | dol.form_5500_sf.sf_plan_name | Short Form (5500-SF) plan (name) | ID: DOL_F5500SF_SF_PLAN_NAME | Format: Up to  |
| sf_plan_num | character varyi | YES | dol.form_5500_sf.sf_plan_num | Short Form (5500-SF) plan (number/identifier) | ID: DOL_F5500SF_SF_PLAN_NUM | Fo |
| sf_plan_satisfy_tests_ind | character varyi | YES | dol.form_5500_sf.sf_plan_satisfy_tests_ind | Short Form (5500-SF) plan satisfy tests (indicator flag) | ID: DOL_F5500SF_SF_PL |
| sf_plan_timely_amended_ind | character varyi | YES | dol.form_5500_sf.sf_plan_timely_amended_ind | Short Form (5500-SF) plan timely amended (indicator flag) | ID: DOL_F5500SF_SF_P |
| sf_plan_year_begin_date | character varyi | YES | dol.form_5500_sf.sf_plan_year_begin_date | Short Form (5500-SF) plan year begin (date) | ID: DOL_F5500SF_SF_PLAN_YEAR_BEGIN |
| sf_premium_filing_confirm_no | character varyi | YES | dol.form_5500_sf.sf_premium_filing_confirm_no | Short Form (5500-SF) premium filing confirm no | ID: DOL_F5500SF_SF_PREMIUM_FILI |
| sf_preparer_firm_name | character varyi | YES | dol.form_5500_sf.sf_preparer_firm_name | Short Form (5500-SF) preparer firm (name) | ID: DOL_F5500SF_SF_PREPARER_FIRM_NAM |
| sf_preparer_foreign_address1 | character varyi | YES | dol.form_5500_sf.sf_preparer_foreign_address1 | Short Form (5500-SF) preparer foreign address1 | ID: DOL_F5500SF_SF_PREPARER_FOR |
| sf_preparer_foreign_address2 | character varyi | YES | dol.form_5500_sf.sf_preparer_foreign_address2 | Short Form (5500-SF) preparer foreign address2 | ID: DOL_F5500SF_SF_PREPARER_FOR |
| sf_preparer_foreign_city | character varyi | YES | dol.form_5500_sf.sf_preparer_foreign_city | Short Form (5500-SF) preparer foreign city | ID: DOL_F5500SF_SF_PREPARER_FOREIGN |
| sf_preparer_foreign_cntry | character varyi | YES | dol.form_5500_sf.sf_preparer_foreign_cntry | Short Form (5500-SF) preparer foreign cntry | ID: DOL_F5500SF_SF_PREPARER_FOREIG |
| sf_preparer_foreign_postal_cd | character varyi | YES | dol.form_5500_sf.sf_preparer_foreign_postal_cd | Short Form (5500-SF) preparer foreign postal cd | ID: DOL_F5500SF_SF_PREPARER_FO |
| sf_preparer_foreign_prov_state | character varyi | YES | dol.form_5500_sf.sf_preparer_foreign_prov_state | Short Form (5500-SF) preparer foreign province state | ID: DOL_F5500SF_SF_PREPAR |
| sf_preparer_name | character varyi | YES | dol.form_5500_sf.sf_preparer_name | Short Form (5500-SF) preparer (name) | ID: DOL_F5500SF_SF_PREPARER_NAME | Format |
| sf_preparer_phone_num | character varyi | YES | dol.form_5500_sf.sf_preparer_phone_num | Short Form (5500-SF) preparer phone (number/identifier) | ID: DOL_F5500SF_SF_PRE |
| sf_preparer_phone_num_foreign | character varyi | YES | dol.form_5500_sf.sf_preparer_phone_num_foreign | Short Form (5500-SF) preparer phone number foreign | ID: DOL_F5500SF_SF_PREPARER |
| sf_preparer_us_address1 | character varyi | YES | dol.form_5500_sf.sf_preparer_us_address1 | Short Form (5500-SF) preparer us address1 | ID: DOL_F5500SF_SF_PREPARER_US_ADDRE |
| sf_preparer_us_address2 | character varyi | YES | dol.form_5500_sf.sf_preparer_us_address2 | Short Form (5500-SF) preparer us address2 | ID: DOL_F5500SF_SF_PREPARER_US_ADDRE |
| sf_preparer_us_city | character varyi | YES | dol.form_5500_sf.sf_preparer_us_city | Short Form (5500-SF) preparer us city | ID: DOL_F5500SF_SF_PREPARER_US_CITY | Fo |
| sf_preparer_us_state | character varyi | YES | dol.form_5500_sf.sf_preparer_us_state | Short Form (5500-SF) preparer us state | ID: DOL_F5500SF_SF_PREPARER_US_STATE |  |
| sf_preparer_us_zip | character varyi | YES | dol.form_5500_sf.sf_preparer_us_zip | Short Form (5500-SF) preparer us (ZIP code) | ID: DOL_F5500SF_SF_PREPARER_US_ZIP |
| sf_res_term_plan_adpt_amt | numeric | YES | dol.form_5500_sf.sf_res_term_plan_adpt_amt | Short Form (5500-SF) res term plan adpt (amount in dollars) | ID: DOL_F5500SF_SF |
| sf_res_term_plan_adpt_ind | character varyi | YES | dol.form_5500_sf.sf_res_term_plan_adpt_ind | Short Form (5500-SF) res term plan adpt (indicator flag) | ID: DOL_F5500SF_SF_RE |
| sf_ruling_letter_grant_date | character varyi | YES | dol.form_5500_sf.sf_ruling_letter_grant_date | Short Form (5500-SF) ruling letter grant (date) | ID: DOL_F5500SF_SF_RULING_LETT |
| sf_sec_412_req_contrib_amt | numeric | YES | dol.form_5500_sf.sf_sec_412_req_contrib_amt | Short Form (5500-SF) sec 412 req contrib (amount in dollars) | ID: DOL_F5500SF_S |
| sf_sep_partcp_partl_vstd_cnt | numeric | YES | dol.form_5500_sf.sf_sep_partcp_partl_vstd_cnt | Short Form (5500-SF) sep participant partl vstd (count/number) | ID: DOL_F5500SF |
| sf_short_plan_yr_ind | character varyi | YES | dol.form_5500_sf.sf_short_plan_yr_ind | Short Form (5500-SF) short plan yr (indicator flag) | ID: DOL_F5500SF_SF_SHORT_P |
| sf_spons_care_of_name | character varyi | YES | dol.form_5500_sf.sf_spons_care_of_name | Plan Sponsor (SF) care of (name) | ID: DOL_F5500SF_SF_SPONS_CARE_OF_NAME | Forma |
| sf_spons_ein | character varyi | YES | dol.form_5500_sf.sf_spons_ein | Plan Sponsor (SF) ein | ID: DOL_F5500SF_SF_SPONS_EIN | Format: 9 digits (XX-XXXX |
| sf_spons_foreign_address1 | character varyi | YES | dol.form_5500_sf.sf_spons_foreign_address1 | Plan Sponsor (SF) foreign address1 | ID: DOL_F5500SF_SF_SPONS_FOREIGN_ADDRESS1 | |
| sf_spons_foreign_address2 | character varyi | YES | dol.form_5500_sf.sf_spons_foreign_address2 | Plan Sponsor (SF) foreign address2 | ID: DOL_F5500SF_SF_SPONS_FOREIGN_ADDRESS2 | |
| sf_spons_foreign_city | character varyi | YES | dol.form_5500_sf.sf_spons_foreign_city | Plan Sponsor (SF) foreign city | ID: DOL_F5500SF_SF_SPONS_FOREIGN_CITY | Format: |
| sf_spons_foreign_cntry | character varyi | YES | dol.form_5500_sf.sf_spons_foreign_cntry | Plan Sponsor (SF) foreign cntry | ID: DOL_F5500SF_SF_SPONS_FOREIGN_CNTRY | Forma |
| sf_spons_foreign_postal_cd | character varyi | YES | dol.form_5500_sf.sf_spons_foreign_postal_cd | Plan Sponsor (SF) foreign postal cd | ID: DOL_F5500SF_SF_SPONS_FOREIGN_POSTAL_CD |
| sf_spons_foreign_prov_state | character varyi | YES | dol.form_5500_sf.sf_spons_foreign_prov_state | Plan Sponsor (SF) foreign province state | ID: DOL_F5500SF_SF_SPONS_FOREIGN_PROV |
| sf_spons_loc_foreign_address1 | character varyi | YES | dol.form_5500_sf.sf_spons_loc_foreign_address1 | Plan Sponsor (SF) loc foreign address1 | ID: DOL_F5500SF_SF_SPONS_LOC_FOREIGN_AD |
| sf_spons_loc_foreign_address2 | character varyi | YES | dol.form_5500_sf.sf_spons_loc_foreign_address2 | Plan Sponsor (SF) loc foreign address2 | ID: DOL_F5500SF_SF_SPONS_LOC_FOREIGN_AD |
| sf_spons_loc_foreign_city | character varyi | YES | dol.form_5500_sf.sf_spons_loc_foreign_city | Plan Sponsor (SF) loc foreign city | ID: DOL_F5500SF_SF_SPONS_LOC_FOREIGN_CITY | |
| sf_spons_loc_foreign_cntry | character varyi | YES | dol.form_5500_sf.sf_spons_loc_foreign_cntry | Plan Sponsor (SF) loc foreign cntry | ID: DOL_F5500SF_SF_SPONS_LOC_FOREIGN_CNTRY |
| sf_spons_loc_foreign_postal_cd | character varyi | YES | dol.form_5500_sf.sf_spons_loc_foreign_postal_cd | Plan Sponsor (SF) loc foreign postal cd | ID: DOL_F5500SF_SF_SPONS_LOC_FOREIGN_P |
| sf_spons_loc_foreign_prov_stat | character varyi | YES | dol.form_5500_sf.sf_spons_loc_foreign_prov_stat | Plan Sponsor (SF) loc foreign province stat | ID: DOL_F5500SF_SF_SPONS_LOC_FOREI |
| sf_spons_loc_us_address1 | character varyi | YES | dol.form_5500_sf.sf_spons_loc_us_address1 | Plan Sponsor (SF) loc us address1 | ID: DOL_F5500SF_SF_SPONS_LOC_US_ADDRESS1 | F |
| sf_spons_loc_us_address2 | character varyi | YES | dol.form_5500_sf.sf_spons_loc_us_address2 | Plan Sponsor (SF) loc us address2 | ID: DOL_F5500SF_SF_SPONS_LOC_US_ADDRESS2 | F |
| sf_spons_loc_us_city | character varyi | YES | dol.form_5500_sf.sf_spons_loc_us_city | Plan Sponsor (SF) loc us city | ID: DOL_F5500SF_SF_SPONS_LOC_US_CITY | Format: U |
| sf_spons_loc_us_state | character varyi | YES | dol.form_5500_sf.sf_spons_loc_us_state | Plan Sponsor (SF) loc us state | ID: DOL_F5500SF_SF_SPONS_LOC_US_STATE | Format: |
| sf_spons_loc_us_zip | character varyi | YES | dol.form_5500_sf.sf_spons_loc_us_zip | Plan Sponsor (SF) loc us (ZIP code) | ID: DOL_F5500SF_SF_SPONS_LOC_US_ZIP | Form |
| sf_spons_manual_signed_date | character varyi | YES | dol.form_5500_sf.sf_spons_manual_signed_date | Plan Sponsor (SF) manual signed (date) | ID: DOL_F5500SF_SF_SPONS_MANUAL_SIGNED_ |
| sf_spons_manual_signed_name | character varyi | YES | dol.form_5500_sf.sf_spons_manual_signed_name | Plan Sponsor (SF) manual signed (name) | ID: DOL_F5500SF_SF_SPONS_MANUAL_SIGNED_ |
| sf_spons_phone_num | character varyi | YES | dol.form_5500_sf.sf_spons_phone_num | Plan Sponsor (SF) phone (number/identifier) | ID: DOL_F5500SF_SF_SPONS_PHONE_NUM |
| sf_spons_phone_num_foreign | character varyi | YES | dol.form_5500_sf.sf_spons_phone_num_foreign | Plan Sponsor (SF) phone number foreign | ID: DOL_F5500SF_SF_SPONS_PHONE_NUM_FORE |
| sf_spons_signed_date | character varyi | YES | dol.form_5500_sf.sf_spons_signed_date | Plan Sponsor (SF) signed (date) | ID: DOL_F5500SF_SF_SPONS_SIGNED_DATE | Format: |
| sf_spons_signed_name | character varyi | YES | dol.form_5500_sf.sf_spons_signed_name | Plan Sponsor (SF) signed (name) | ID: DOL_F5500SF_SF_SPONS_SIGNED_NAME | Format: |
| sf_spons_us_address1 | character varyi | YES | dol.form_5500_sf.sf_spons_us_address1 | Plan Sponsor (SF) us address1 | ID: DOL_F5500SF_SF_SPONS_US_ADDRESS1 | Format: U |
| sf_spons_us_address2 | character varyi | YES | dol.form_5500_sf.sf_spons_us_address2 | Plan Sponsor (SF) us address2 | ID: DOL_F5500SF_SF_SPONS_US_ADDRESS2 | Format: U |
| sf_spons_us_city | character varyi | YES | dol.form_5500_sf.sf_spons_us_city | Plan Sponsor (SF) us city | ID: DOL_F5500SF_SF_SPONS_US_CITY | Format: Up to 255 |
| sf_spons_us_state | character varyi | YES | dol.form_5500_sf.sf_spons_us_state | Plan Sponsor (SF) us state | ID: DOL_F5500SF_SF_SPONS_US_STATE | Format: Up to 2 |
| sf_spons_us_zip | character varyi | YES | dol.form_5500_sf.sf_spons_us_zip | Plan Sponsor (SF) us (ZIP code) | ID: DOL_F5500SF_SF_SPONS_US_ZIP | Format: 5 or |
| sf_sponsor_dfe_dba_name | character varyi | YES | dol.form_5500_sf.sf_sponsor_dfe_dba_name | Plan Sponsor (SF) dfe dba (name) | ID: DOL_F5500SF_SF_SPONSOR_DFE_DBA_NAME | For |
| sf_sponsor_name | character varyi | YES | dol.form_5500_sf.sf_sponsor_name | Plan Sponsor (SF) name | ID: DOL_F5500SF_SF_SPONSOR_NAME | Format: Up to 255 cha |
| sf_tax_code | character varyi | YES | dol.form_5500_sf.sf_tax_code | Short Form (5500-SF) tax (code value) | ID: DOL_F5500SF_SF_TAX_CODE | Format: Up |
| sf_tax_prd | character varyi | YES | dol.form_5500_sf.sf_tax_prd | Short Form (5500-SF) tax prd | ID: DOL_F5500SF_SF_TAX_PRD | Format: Up to 255 ch |
| sf_tot_act_partcp_boy_cnt | numeric | YES | dol.form_5500_sf.sf_tot_act_partcp_boy_cnt | Short Form (5500-SF) tot act participant boy (count/number) | ID: DOL_F5500SF_SF |
| sf_tot_act_partcp_eoy_cnt | numeric | YES | dol.form_5500_sf.sf_tot_act_partcp_eoy_cnt | Short Form (5500-SF) tot act participant eoy (count/number) | ID: DOL_F5500SF_SF |
| sf_tot_act_rtd_sep_benef_cnt | numeric | YES | dol.form_5500_sf.sf_tot_act_rtd_sep_benef_cnt | Short Form (5500-SF) tot act retired separated benef (count/number) | ID: DOL_F5 |
| sf_tot_assets_boy_amt | numeric | YES | dol.form_5500_sf.sf_tot_assets_boy_amt | Short Form (5500-SF) tot assets boy (amount in dollars) | ID: DOL_F5500SF_SF_TOT |
| sf_tot_assets_eoy_amt | numeric | YES | dol.form_5500_sf.sf_tot_assets_eoy_amt | Short Form (5500-SF) tot assets eoy (amount in dollars) | ID: DOL_F5500SF_SF_TOT |
| sf_tot_distrib_bnft_amt | numeric | YES | dol.form_5500_sf.sf_tot_distrib_bnft_amt | Short Form (5500-SF) tot distrib bnft (amount in dollars) | ID: DOL_F5500SF_SF_T |
| sf_tot_expenses_amt | numeric | YES | dol.form_5500_sf.sf_tot_expenses_amt | Short Form (5500-SF) tot expenses (amount in dollars) | ID: DOL_F5500SF_SF_TOT_E |
| sf_tot_income_amt | numeric | YES | dol.form_5500_sf.sf_tot_income_amt | Short Form (5500-SF) tot income (amount in dollars) | ID: DOL_F5500SF_SF_TOT_INC |
| sf_tot_liabilities_boy_amt | numeric | YES | dol.form_5500_sf.sf_tot_liabilities_boy_amt | Short Form (5500-SF) tot liabilities boy (amount in dollars) | ID: DOL_F5500SF_S |
| sf_tot_liabilities_eoy_amt | numeric | YES | dol.form_5500_sf.sf_tot_liabilities_eoy_amt | Short Form (5500-SF) tot liabilities eoy (amount in dollars) | ID: DOL_F5500SF_S |
| sf_tot_partcp_boy_cnt | numeric | YES | dol.form_5500_sf.sf_tot_partcp_boy_cnt | Short Form (5500-SF) tot participant boy (count/number) | ID: DOL_F5500SF_SF_TOT |
| sf_tot_plan_transfers_amt | numeric | YES | dol.form_5500_sf.sf_tot_plan_transfers_amt | Short Form (5500-SF) tot plan transfers (amount in dollars) | ID: DOL_F5500SF_SF |
| sf_trus_inc_unrel_tax_inc_amt | numeric | YES | dol.form_5500_sf.sf_trus_inc_unrel_tax_inc_amt | Short Form (5500-SF) trus inc unrel tax inc (amount in dollars) | ID: DOL_F5500S |
| sf_trus_inc_unrel_tax_inc_ind | character varyi | YES | dol.form_5500_sf.sf_trus_inc_unrel_tax_inc_ind | Short Form (5500-SF) trus inc unrel tax inc (indicator flag) | ID: DOL_F5500SF_S |
| sf_type_pension_bnft_code | character varyi | YES | dol.form_5500_sf.sf_type_pension_bnft_code | Short Form (5500-SF) type pension bnft (code value) | ID: DOL_F5500SF_SF_TYPE_PE |
| sf_type_welfare_bnft_code | character varyi | YES | dol.form_5500_sf.sf_type_welfare_bnft_code | Short Form (5500-SF) type welfare bnft (code value) | ID: DOL_F5500SF_SF_TYPE_WE |
| sf_unp_min_cont_cur_yrtot_amt | numeric | YES | dol.form_5500_sf.sf_unp_min_cont_cur_yrtot_amt | Short Form (5500-SF) unp min cont cur yrtot (amount in dollars) | ID: DOL_F5500S |
| updated_at | timestamp with  | YES | dol.form_5500_sf.updated_at | Record last update timestamp | ID: DOL_F5500SF_UPDATED_AT | Format: YYYY-MM-DD H |
| valid_admin_signature | character varyi | YES | dol.form_5500_sf.valid_admin_signature | Valid administrative signature | ID: DOL_F5500SF_VALID_ADMIN_SIGNATURE | Format: |
| valid_sponsor_signature | character varyi | YES | dol.form_5500_sf.valid_sponsor_signature | Valid sponsor signature | ID: DOL_F5500SF_VALID_SPONSOR_SIGNATURE | Format: Up t |

### LEAF: dol.form_5500_sf_part7 (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.form_5500_sf_part7.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.form_5500_sf_part7.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.form_5500_sf_part7.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.form_5500_sf_part7.id | Auto-increment surrogate primary key |
| row_order | integer | YES | dol.form_5500_sf_part7.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |
| sf_plan_transfer_ein | character varyi | YES | dol.form_5500_sf_part7.sf_plan_transfer_ein | EIN (Employer Identification Number) of the receiving plan |
| sf_plan_transfer_name | character varyi | YES | dol.form_5500_sf_part7.sf_plan_transfer_name | Name of the plan to which assets were transferred |
| sf_plan_transfer_pn | character varyi | YES | dol.form_5500_sf_part7.sf_plan_transfer_pn | Plan number of the receiving plan |

### LEAF: dol.renewal_calendar (13 columns, 13 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| carrier_name | character varyi | YES | dol.renewal_calendar.carrier_name | Carrier Name |
| company_unique_id | text | NO | dol.renewal_calendar.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | NO | dol.renewal_calendar.created_at | When this record was created |
| days_until_renewal | integer | YES | dol.renewal_calendar.days_until_renewal | Days Until Renewal |
| filing_id | uuid | YES | dol.renewal_calendar.filing_id | Filing Id |
| is_upcoming | boolean | NO | dol.renewal_calendar.is_upcoming | Whether this record upcoming |
| plan_name | character varyi | YES | dol.renewal_calendar.plan_name | Plan Name |
| renewal_date | date | YES | dol.renewal_calendar.renewal_date | Renewal Date |
| renewal_id | uuid | NO | dol.renewal_calendar.renewal_id | Renewal Id |
| renewal_month | integer | YES | dol.renewal_calendar.renewal_month | Plan year begin month (1-12) |
| renewal_year | integer | YES | dol.renewal_calendar.renewal_year | Renewal Year |
| schedule_id | uuid | YES | dol.renewal_calendar.schedule_id | Schedule Id |
| updated_at | timestamp with  | NO | dol.renewal_calendar.updated_at | When this record was last updated |

### LEAF: dol.schedule_a (98 columns, 98 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | YES | dol.schedule_a.ack_id | DOL acknowledgment ID for the filing | ID: DOL_SCHA_ACK_ID | Format: Up to 255 c |
| alloc_contracts_group_ind | character varyi | YES | dol.schedule_a.alloc_contracts_group_ind | Allocated Contract contracts group (indicator flag) | ID: DOL_SCHA_ALLOC_CONTRAC |
| alloc_contracts_indiv_ind | character varyi | YES | dol.schedule_a.alloc_contracts_indiv_ind | Allocated Contract contracts indiv (indicator flag) | ID: DOL_SCHA_ALLOC_CONTRAC |
| alloc_contracts_other_ind | character varyi | YES | dol.schedule_a.alloc_contracts_other_ind | Allocated Contract contracts other (indicator flag) | ID: DOL_SCHA_ALLOC_CONTRAC |
| alloc_contracts_other_text | text | YES | dol.schedule_a.alloc_contracts_other_text | Allocated Contract contracts other (text description) | ID: DOL_SCHA_ALLOC_CONTR |
| company_unique_id | text | YES | dol.schedule_a.company_unique_id | Company unique id | ID: DOL_SCHA_COMPANY_UNIQUE_ID | Format: Variable length tex |
| created_at | timestamp with  | YES | dol.schedule_a.created_at | Record creation timestamp | ID: DOL_SCHA_CREATED_AT | Format: YYYY-MM-DD HH:MM:S |
| filing_id | uuid | YES | dol.schedule_a.filing_id | Unique filing identifier (UUID) | ID: DOL_SCHA_FILING_ID | Format: xxxxxxxx-xxxx |
| form_id | character varyi | YES | dol.schedule_a.form_id | Form type identifier | ID: DOL_SCHA_FORM_ID | Format: Up to 255 characters |
| form_year | character varyi | YES | dol.schedule_a.form_year | Tax/plan year for this filing | ID: DOL_SCHA_FORM_YEAR | Format: Up to 10 charac |
| ins_broker_comm_tot_amt | numeric | YES | dol.schedule_a.ins_broker_comm_tot_amt | Total broker commissions paid | ID: DOL_SCHA_INS_BROKER_COMM_TOT_AMT | Format: D |
| ins_broker_fees_tot_amt | numeric | YES | dol.schedule_a.ins_broker_fees_tot_amt | Total broker fees paid | ID: DOL_SCHA_INS_BROKER_FEES_TOT_AMT | Format: Decimal  |
| ins_carrier_ein | character varyi | YES | dol.schedule_a.ins_carrier_ein | Insurance carrier EIN | ID: DOL_SCHA_INS_CARRIER_EIN | Format: 9 digits (XX-XXXX |
| ins_carrier_naic_code | character varyi | YES | dol.schedule_a.ins_carrier_naic_code | Insurance carrier NAIC code (5 digits) | ID: DOL_SCHA_INS_CARRIER_NAIC_CODE | Fo |
| ins_carrier_name | character varyi | YES | dol.schedule_a.ins_carrier_name | Name of insurance carrier | ID: DOL_SCHA_INS_CARRIER_NAME | Format: Up to 255 ch |
| ins_contract_num | character varyi | YES | dol.schedule_a.ins_contract_num | Insurance contract/policy number | ID: DOL_SCHA_INS_CONTRACT_NUM | Format: Up to |
| ins_fail_provide_info_ind | character varyi | YES | dol.schedule_a.ins_fail_provide_info_ind | Insurance fail provide info (indicator flag) | ID: DOL_SCHA_INS_FAIL_PROVIDE_INF |
| ins_fail_provide_info_text | text | YES | dol.schedule_a.ins_fail_provide_info_text | Insurance fail provide info (text description) | ID: DOL_SCHA_INS_FAIL_PROVIDE_I |
| ins_policy_from_date | character varyi | YES | dol.schedule_a.ins_policy_from_date | Policy effective start date | ID: DOL_SCHA_INS_POLICY_FROM_DATE | Format: YYYY-M |
| ins_policy_to_date | character varyi | YES | dol.schedule_a.ins_policy_to_date | Policy effective end date | ID: DOL_SCHA_INS_POLICY_TO_DATE | Format: YYYY-MM-DD |
| ins_prsn_covered_eoy_cnt | numeric | YES | dol.schedule_a.ins_prsn_covered_eoy_cnt | Persons covered at end of year | ID: DOL_SCHA_INS_PRSN_COVERED_EOY_CNT | Format: |
| pens_distr_bnft_term_pln_ind | character varyi | YES | dol.schedule_a.pens_distr_bnft_term_pln_ind | Pens distr benefit term pln (indicator flag) | ID: DOL_SCHA_PENS_DISTR_BNFT_TERM |
| pension_admin_chrg_amt | numeric | YES | dol.schedule_a.pension_admin_chrg_amt | Pension administrative charges | ID: DOL_SCHA_PENSION_ADMIN_CHRG_AMT | Format: D |
| pension_basis_rates_text | text | YES | dol.schedule_a.pension_basis_rates_text | Pension basis rates (text description) | ID: DOL_SCHA_PENSION_BASIS_RATES_TEXT | |
| pension_bnfts_dsbrsd_amt | numeric | YES | dol.schedule_a.pension_bnfts_dsbrsd_amt | Pension benefits disbursed | ID: DOL_SCHA_PENSION_BNFTS_DSBRSD_AMT | Format: Dec |
| pension_contract_cost_amt | numeric | YES | dol.schedule_a.pension_contract_cost_amt | Pension contract cost | ID: DOL_SCHA_PENSION_CONTRACT_COST_AMT | Format: Decimal |
| pension_contrib_dep_amt | numeric | YES | dol.schedule_a.pension_contrib_dep_amt | Pension contributions deposited | ID: DOL_SCHA_PENSION_CONTRIB_DEP_AMT | Format: |
| pension_cost_text | text | YES | dol.schedule_a.pension_cost_text | Pension cost (text description) | ID: DOL_SCHA_PENSION_COST_TEXT | Format: Varia |
| pension_divnd_cr_dep_amt | numeric | YES | dol.schedule_a.pension_divnd_cr_dep_amt | Pension dividend credits deposited | ID: DOL_SCHA_PENSION_DIVND_CR_DEP_AMT | For |
| pension_end_prev_bal_amt | numeric | YES | dol.schedule_a.pension_end_prev_bal_amt | Pension end previous bal (amount in dollars) | ID: DOL_SCHA_PENSION_END_PREV_BAL |
| pension_eoy_bal_amt | numeric | YES | dol.schedule_a.pension_eoy_bal_amt | Pension end of year balance | ID: DOL_SCHA_PENSION_EOY_BAL_AMT | Format: Decimal |
| pension_eoy_gen_acct_amt | numeric | YES | dol.schedule_a.pension_eoy_gen_acct_amt | Pension general account value at EOY | ID: DOL_SCHA_PENSION_EOY_GEN_ACCT_AMT | F |
| pension_eoy_sep_acct_amt | numeric | YES | dol.schedule_a.pension_eoy_sep_acct_amt | Pension separate account value at EOY | ID: DOL_SCHA_PENSION_EOY_SEP_ACCT_AMT |  |
| pension_int_cr_dur_yr_amt | numeric | YES | dol.schedule_a.pension_int_cr_dur_yr_amt | Pension interest credits during year | ID: DOL_SCHA_PENSION_INT_CR_DUR_YR_AMT |  |
| pension_oth_ded_amt | numeric | YES | dol.schedule_a.pension_oth_ded_amt | Pension oth ded (amount in dollars) | ID: DOL_SCHA_PENSION_OTH_DED_AMT | Format: |
| pension_oth_ded_text | text | YES | dol.schedule_a.pension_oth_ded_text | Pension oth ded (text description) | ID: DOL_SCHA_PENSION_OTH_DED_TEXT | Format: |
| pension_other_amt | numeric | YES | dol.schedule_a.pension_other_amt | Pension other (amount in dollars) | ID: DOL_SCHA_PENSION_OTHER_AMT | Format: Dec |
| pension_other_text | text | YES | dol.schedule_a.pension_other_text | Pension other (text description) | ID: DOL_SCHA_PENSION_OTHER_TEXT | Format: Var |
| pension_prem_paid_tot_amt | numeric | YES | dol.schedule_a.pension_prem_paid_tot_amt | Total pension premiums paid | ID: DOL_SCHA_PENSION_PREM_PAID_TOT_AMT | Format: D |
| pension_tot_additions_amt | numeric | YES | dol.schedule_a.pension_tot_additions_amt | Pension tot additions (amount in dollars) | ID: DOL_SCHA_PENSION_TOT_ADDITIONS_A |
| pension_tot_bal_addn_amt | numeric | YES | dol.schedule_a.pension_tot_bal_addn_amt | Pension tot balance addn (amount in dollars) | ID: DOL_SCHA_PENSION_TOT_BAL_ADDN |
| pension_tot_ded_amt | numeric | YES | dol.schedule_a.pension_tot_ded_amt | Pension tot ded (amount in dollars) | ID: DOL_SCHA_PENSION_TOT_DED_AMT | Format: |
| pension_transfer_from_amt | numeric | YES | dol.schedule_a.pension_transfer_from_amt | Pension transfer from (amount in dollars) | ID: DOL_SCHA_PENSION_TRANSFER_FROM_A |
| pension_transfer_to_amt | numeric | YES | dol.schedule_a.pension_transfer_to_amt | Pension transfer to (amount in dollars) | ID: DOL_SCHA_PENSION_TRANSFER_TO_AMT | |
| pension_unpaid_premium_amt | numeric | YES | dol.schedule_a.pension_unpaid_premium_amt | Unpaid pension premiums | ID: DOL_SCHA_PENSION_UNPAID_PREMIUM_AMT | Format: Deci |
| sch_a_ein | character varyi | YES | dol.schedule_a.sch_a_ein | Schedule A ein | ID: DOL_SCHA_SCH_A_EIN | Format: 9 digits (XX-XXXXXXX) |
| sch_a_plan_num | character varyi | YES | dol.schedule_a.sch_a_plan_num | Schedule A plan (number/identifier) | ID: DOL_SCHA_SCH_A_PLAN_NUM | Format: Up t |
| sch_a_plan_year_begin_date | character varyi | YES | dol.schedule_a.sch_a_plan_year_begin_date | Schedule A plan year begin (date) | ID: DOL_SCHA_SCH_A_PLAN_YEAR_BEGIN_DATE | Fo |
| sch_a_plan_year_end_date | character varyi | YES | dol.schedule_a.sch_a_plan_year_end_date | Schedule A plan year end (date) | ID: DOL_SCHA_SCH_A_PLAN_YEAR_END_DATE | Format |
| schedule_id | uuid | NO | dol.schedule_a.schedule_id | Schedule id | ID: DOL_SCHA_SCHEDULE_ID | Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxx |
| sponsor_name | character varyi | YES | dol.schedule_a.sponsor_name | Sponsor name (derived from Form 5500 for Schedule A) | ID: DOL_SCHA_SPONSOR_NAME |
| sponsor_state | character varyi | YES | dol.schedule_a.sponsor_state | Sponsor state (derived from Form 5500 for Schedule A) | ID: DOL_SCHA_SPONSOR_STA |
| unal_contrac_imm_part_guar_ind | character varyi | YES | dol.schedule_a.unal_contrac_imm_part_guar_ind | Unallocated Contract contrac imm part guar (indicator flag) | ID: DOL_SCHA_UNAL_ |
| unal_contracts_guar_invest_ind | character varyi | YES | dol.schedule_a.unal_contracts_guar_invest_ind | Unallocated Contract contracts guar invest (indicator flag) | ID: DOL_SCHA_UNAL_ |
| unalloc_contracts_dep_adm_ind | character varyi | YES | dol.schedule_a.unalloc_contracts_dep_adm_ind | Unallocated Contract contracts dep adm (indicator flag) | ID: DOL_SCHA_UNALLOC_C |
| unalloc_contracts_other_ind | character varyi | YES | dol.schedule_a.unalloc_contracts_other_ind | Unallocated Contract contracts other (indicator flag) | ID: DOL_SCHA_UNALLOC_CON |
| unalloc_contracts_other_text | text | YES | dol.schedule_a.unalloc_contracts_other_text | Unallocated Contract contracts other (text description) | ID: DOL_SCHA_UNALLOC_C |
| updated_at | timestamp with  | YES | dol.schedule_a.updated_at | Record last update timestamp | ID: DOL_SCHA_UPDATED_AT | Format: YYYY-MM-DD HH:M |
| wlfr_acquis_cost_amt | numeric | YES | dol.schedule_a.wlfr_acquis_cost_amt | Welfare Benefit acquis cost (amount in dollars) | ID: DOL_SCHA_WLFR_ACQUIS_COST_ |
| wlfr_acquis_cost_text | text | YES | dol.schedule_a.wlfr_acquis_cost_text | Welfare Benefit acquis cost (text description) | ID: DOL_SCHA_WLFR_ACQUIS_COST_T |
| wlfr_bnft_dental_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_dental_ind | Plan provides dental benefits | ID: DOL_SCHA_WLFR_BNFT_DENTAL_IND | Format: Y/N/ |
| wlfr_bnft_drug_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_drug_ind | Plan provides prescription drug benefits | ID: DOL_SCHA_WLFR_BNFT_DRUG_IND | For |
| wlfr_bnft_health_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_health_ind | Plan provides health benefits | ID: DOL_SCHA_WLFR_BNFT_HEALTH_IND | Format: Y/N/ |
| wlfr_bnft_hmo_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_hmo_ind | Plan uses HMO arrangement | ID: DOL_SCHA_WLFR_BNFT_HMO_IND | Format: Y/N/X or 1/ |
| wlfr_bnft_indemnity_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_indemnity_ind | Plan uses indemnity arrangement | ID: DOL_SCHA_WLFR_BNFT_INDEMNITY_IND | Format: |
| wlfr_bnft_life_insur_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_life_insur_ind | Plan provides life insurance | ID: DOL_SCHA_WLFR_BNFT_LIFE_INSUR_IND | Format: Y |
| wlfr_bnft_long_term_disab_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_long_term_disab_ind | Plan provides long-term disability | ID: DOL_SCHA_WLFR_BNFT_LONG_TERM_DISAB_IND  |
| wlfr_bnft_other_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_other_ind | Plan provides other welfare benefits | ID: DOL_SCHA_WLFR_BNFT_OTHER_IND | Format |
| wlfr_bnft_ppo_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_ppo_ind | Plan uses PPO arrangement | ID: DOL_SCHA_WLFR_BNFT_PPO_IND | Format: Y/N/X or 1/ |
| wlfr_bnft_stop_loss_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_stop_loss_ind | Plan has stop-loss coverage | ID: DOL_SCHA_WLFR_BNFT_STOP_LOSS_IND | Format: Y/N |
| wlfr_bnft_temp_disab_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_temp_disab_ind | Plan provides temporary disability | ID: DOL_SCHA_WLFR_BNFT_TEMP_DISAB_IND | For |
| wlfr_bnft_unemp_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_unemp_ind | Plan provides unemployment benefits | ID: DOL_SCHA_WLFR_BNFT_UNEMP_IND | Format: |
| wlfr_bnft_vision_ind | character varyi | YES | dol.schedule_a.wlfr_bnft_vision_ind | Plan provides vision benefits | ID: DOL_SCHA_WLFR_BNFT_VISION_IND | Format: Y/N/ |
| wlfr_claims_chrgd_amt | numeric | YES | dol.schedule_a.wlfr_claims_chrgd_amt | Welfare Benefit claims chrgd (amount in dollars) | ID: DOL_SCHA_WLFR_CLAIMS_CHRG |
| wlfr_claims_paid_amt | numeric | YES | dol.schedule_a.wlfr_claims_paid_amt | Welfare Benefit claims paid (amount in dollars) | ID: DOL_SCHA_WLFR_CLAIMS_PAID_ |
| wlfr_claims_reserve_amt | numeric | YES | dol.schedule_a.wlfr_claims_reserve_amt | Welfare Benefit claims reserve (amount in dollars) | ID: DOL_SCHA_WLFR_CLAIMS_RE |
| wlfr_divnds_due_amt | numeric | YES | dol.schedule_a.wlfr_divnds_due_amt | Welfare Benefit divnds due (amount in dollars) | ID: DOL_SCHA_WLFR_DIVNDS_DUE_AM |
| wlfr_held_bnfts_amt | numeric | YES | dol.schedule_a.wlfr_held_bnfts_amt | Welfare Benefit held bnfts (amount in dollars) | ID: DOL_SCHA_WLFR_HELD_BNFTS_AM |
| wlfr_incr_reserve_amt | numeric | YES | dol.schedule_a.wlfr_incr_reserve_amt | Welfare Benefit incr reserve (amount in dollars) | ID: DOL_SCHA_WLFR_INCR_RESERV |
| wlfr_incurred_claim_amt | numeric | YES | dol.schedule_a.wlfr_incurred_claim_amt | Welfare Benefit incurred claim (amount in dollars) | ID: DOL_SCHA_WLFR_INCURRED_ |
| wlfr_oth_reserve_amt | numeric | YES | dol.schedule_a.wlfr_oth_reserve_amt | Welfare Benefit oth reserve (amount in dollars) | ID: DOL_SCHA_WLFR_OTH_RESERVE_ |
| wlfr_premium_rcvd_amt | numeric | YES | dol.schedule_a.wlfr_premium_rcvd_amt | Welfare Benefit premium rcvd (amount in dollars) | ID: DOL_SCHA_WLFR_PREMIUM_RCV |
| wlfr_refund_amt | numeric | YES | dol.schedule_a.wlfr_refund_amt | Welfare Benefit refund (amount in dollars) | ID: DOL_SCHA_WLFR_REFUND_AMT | Form |
| wlfr_refund_cash_ind | character varyi | YES | dol.schedule_a.wlfr_refund_cash_ind | Welfare Benefit refund cash (indicator flag) | ID: DOL_SCHA_WLFR_REFUND_CASH_IND |
| wlfr_refund_credit_ind | character varyi | YES | dol.schedule_a.wlfr_refund_credit_ind | Welfare Benefit refund credit (indicator flag) | ID: DOL_SCHA_WLFR_REFUND_CREDIT |
| wlfr_reserve_amt | numeric | YES | dol.schedule_a.wlfr_reserve_amt | Welfare Benefit reserve (amount in dollars) | ID: DOL_SCHA_WLFR_RESERVE_AMT | Fo |
| wlfr_ret_admin_amt | numeric | YES | dol.schedule_a.wlfr_ret_admin_amt | Welfare Benefit ret admin (amount in dollars) | ID: DOL_SCHA_WLFR_RET_ADMIN_AMT  |
| wlfr_ret_charges_amt | numeric | YES | dol.schedule_a.wlfr_ret_charges_amt | Welfare Benefit ret charges (amount in dollars) | ID: DOL_SCHA_WLFR_RET_CHARGES_ |
| wlfr_ret_commissions_amt | numeric | YES | dol.schedule_a.wlfr_ret_commissions_amt | Welfare Benefit ret commissions (amount in dollars) | ID: DOL_SCHA_WLFR_RET_COMM |
| wlfr_ret_oth_chrgs_amt | numeric | YES | dol.schedule_a.wlfr_ret_oth_chrgs_amt | Welfare Benefit ret other chrgs (amount in dollars) | ID: DOL_SCHA_WLFR_RET_OTH_ |
| wlfr_ret_oth_cost_amt | numeric | YES | dol.schedule_a.wlfr_ret_oth_cost_amt | Welfare Benefit ret other cost (amount in dollars) | ID: DOL_SCHA_WLFR_RET_OTH_C |
| wlfr_ret_oth_expense_amt | numeric | YES | dol.schedule_a.wlfr_ret_oth_expense_amt | Welfare Benefit ret other expense (amount in dollars) | ID: DOL_SCHA_WLFR_RET_OT |
| wlfr_ret_taxes_amt | numeric | YES | dol.schedule_a.wlfr_ret_taxes_amt | Welfare Benefit ret taxes (amount in dollars) | ID: DOL_SCHA_WLFR_RET_TAXES_AMT  |
| wlfr_ret_tot_amt | numeric | YES | dol.schedule_a.wlfr_ret_tot_amt | Welfare Benefit ret tot (amount in dollars) | ID: DOL_SCHA_WLFR_RET_TOT_AMT | Fo |
| wlfr_tot_charges_paid_amt | numeric | YES | dol.schedule_a.wlfr_tot_charges_paid_amt | Welfare Benefit tot charges paid (amount in dollars) | ID: DOL_SCHA_WLFR_TOT_CHA |
| wlfr_tot_earned_prem_amt | numeric | YES | dol.schedule_a.wlfr_tot_earned_prem_amt | Welfare Benefit tot earned prem (amount in dollars) | ID: DOL_SCHA_WLFR_TOT_EARN |
| wlfr_type_bnft_oth_text | text | YES | dol.schedule_a.wlfr_type_bnft_oth_text | Welfare Benefit type benefit oth (text description) | ID: DOL_SCHA_WLFR_TYPE_BNF |
| wlfr_unpaid_due_amt | numeric | YES | dol.schedule_a.wlfr_unpaid_due_amt | Welfare Benefit unpaid due (amount in dollars) | ID: DOL_SCHA_WLFR_UNPAID_DUE_AM |

### LEAF: dol.schedule_a_part1 (22 columns, 22 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_a_part1.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_a_part1.created_at | Timestamp when this row was loaded into the database |
| form_id | character varyi | YES | dol.schedule_a_part1.form_id | DOL internal form identifier |
| form_year | character varyi | YES | dol.schedule_a_part1.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_a_part1.id | Auto-increment surrogate primary key |
| ins_broker_code | character varyi | YES | dol.schedule_a_part1.ins_broker_code | Broker classification code (type of broker/agent) |
| ins_broker_comm_pd_amt | numeric | YES | dol.schedule_a_part1.ins_broker_comm_pd_amt | Total commissions paid to broker (USD) |
| ins_broker_fees_pd_amt | numeric | YES | dol.schedule_a_part1.ins_broker_fees_pd_amt | Total fees paid to broker (USD) |
| ins_broker_fees_pd_text | text | YES | dol.schedule_a_part1.ins_broker_fees_pd_text | Description/explanation of fees paid to broker |
| ins_broker_foreign_address1 | character varyi | YES | dol.schedule_a_part1.ins_broker_foreign_address1 | Broker foreign address line 1 |
| ins_broker_foreign_address2 | character varyi | YES | dol.schedule_a_part1.ins_broker_foreign_address2 | Broker foreign address line 2 |
| ins_broker_foreign_city | character varyi | YES | dol.schedule_a_part1.ins_broker_foreign_city | Broker foreign city |
| ins_broker_foreign_cntry | character varyi | YES | dol.schedule_a_part1.ins_broker_foreign_cntry | Broker foreign country |
| ins_broker_foreign_postal_cd | character varyi | YES | dol.schedule_a_part1.ins_broker_foreign_postal_cd | Broker foreign postal code |
| ins_broker_foreign_prov_state | character varyi | YES | dol.schedule_a_part1.ins_broker_foreign_prov_state | Broker foreign province/state |
| ins_broker_name | character varyi | YES | dol.schedule_a_part1.ins_broker_name | Name of insurance broker or agent |
| ins_broker_us_address1 | character varyi | YES | dol.schedule_a_part1.ins_broker_us_address1 | Broker US mailing address line 1 |
| ins_broker_us_address2 | character varyi | YES | dol.schedule_a_part1.ins_broker_us_address2 | Broker US mailing address line 2 |
| ins_broker_us_city | character varyi | YES | dol.schedule_a_part1.ins_broker_us_city | Broker US city |
| ins_broker_us_state | character varyi | YES | dol.schedule_a_part1.ins_broker_us_state | Broker US state code (2-letter) |
| ins_broker_us_zip | character varyi | YES | dol.schedule_a_part1.ins_broker_us_zip | Broker US ZIP code |
| row_order | integer | YES | dol.schedule_a_part1.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_c (5 columns, 5 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_c.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c.id | Auto-increment surrogate primary key |
| provider_exclude_ind | character varyi | YES | dol.schedule_c.provider_exclude_ind | Indicator (Yes/No) — whether certain service providers are excluded from Part 1  |

### LEAF: dol.schedule_c_part1_item1 (18 columns, 18 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c_part1_item1.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_c_part1_item1.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c_part1_item1.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c_part1_item1.id | Auto-increment surrogate primary key |
| prov_eligible_foreign_address1 | character varyi | YES | dol.schedule_c_part1_item1.prov_eligible_foreign_a | Provider foreign address line 1 |
| prov_eligible_foreign_address2 | character varyi | YES | dol.schedule_c_part1_item1.prov_eligible_foreign_a | Provider foreign address line 2 |
| prov_eligible_foreign_city | character varyi | YES | dol.schedule_c_part1_item1.prov_eligible_foreign_c | Provider foreign city |
| prov_eligible_foreign_cntry | character varyi | YES | dol.schedule_c_part1_item1.prov_eligible_foreign_c | Provider foreign country |
| prov_eligible_foreign_post_cd | character varyi | YES | dol.schedule_c_part1_item1.prov_eligible_foreign_p | Provider foreign postal code |
| prov_eligible_foreign_prov_st | character varyi | YES | dol.schedule_c_part1_item1.prov_eligible_foreign_p | Provider foreign province/state |
| provider_eligible_ein | character varyi | YES | dol.schedule_c_part1_item1.provider_eligible_ein | EIN of the eligible indirect compensation provider |
| provider_eligible_name | character varyi | YES | dol.schedule_c_part1_item1.provider_eligible_name | Name of service provider receiving eligible indirect compensation |
| provider_eligible_us_address1 | character varyi | YES | dol.schedule_c_part1_item1.provider_eligible_us_ad | Provider US address line 1 |
| provider_eligible_us_address2 | character varyi | YES | dol.schedule_c_part1_item1.provider_eligible_us_ad | Provider US address line 2 |
| provider_eligible_us_city | character varyi | YES | dol.schedule_c_part1_item1.provider_eligible_us_ci | Provider US city |
| provider_eligible_us_state | character varyi | YES | dol.schedule_c_part1_item1.provider_eligible_us_st | Provider US state code (2-letter) |
| provider_eligible_us_zip | character varyi | YES | dol.schedule_c_part1_item1.provider_eligible_us_zi | Provider US ZIP code |
| row_order | integer | YES | dol.schedule_c_part1_item1.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_c_part1_item2 (25 columns, 25 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c_part1_item2.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_c_part1_item2.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c_part1_item2.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c_part1_item2.id | Auto-increment surrogate primary key |
| prov_other_elig_ind_comp_ind | character varyi | YES | dol.schedule_c_part1_item2.prov_other_elig_ind_com | Indicator (Yes/No) — eligible indirect compensation received |
| prov_other_foreign_address1 | character varyi | YES | dol.schedule_c_part1_item2.prov_other_foreign_addr | Provider foreign address line 1 |
| prov_other_foreign_address2 | character varyi | YES | dol.schedule_c_part1_item2.prov_other_foreign_addr | Provider foreign address line 2 |
| prov_other_foreign_city | character varyi | YES | dol.schedule_c_part1_item2.prov_other_foreign_city | Provider foreign city |
| prov_other_foreign_cntry | character varyi | YES | dol.schedule_c_part1_item2.prov_other_foreign_cntr | Provider foreign country |
| prov_other_foreign_postal_cd | character varyi | YES | dol.schedule_c_part1_item2.prov_other_foreign_post | Provider foreign postal code |
| prov_other_foreign_prov_state | character varyi | YES | dol.schedule_c_part1_item2.prov_other_foreign_prov | Provider foreign province/state |
| prov_other_indirect_comp_ind | character varyi | YES | dol.schedule_c_part1_item2.prov_other_indirect_com | Indicator (Yes/No) — did provider receive indirect compensation |
| prov_other_tot_ind_comp_amt | numeric | YES | dol.schedule_c_part1_item2.prov_other_tot_ind_comp | Total indirect compensation amount (USD) |
| provider_other_amt_formula_ind | character varyi | YES | dol.schedule_c_part1_item2.provider_other_amt_form | Indicator (Yes/No) — compensation based on formula rather than fixed amount |
| provider_other_direct_comp_amt | numeric | YES | dol.schedule_c_part1_item2.provider_other_direct_c | Direct compensation paid to provider (USD) |
| provider_other_ein | character varyi | YES | dol.schedule_c_part1_item2.provider_other_ein | EIN of the service provider |
| provider_other_name | character varyi | YES | dol.schedule_c_part1_item2.provider_other_name | Name of service provider receiving $5,000+ in compensation |
| provider_other_relation | character varyi | YES | dol.schedule_c_part1_item2.provider_other_relation | Relationship to plan (e.g., party-in-interest) |
| provider_other_srvc_codes | character varyi | YES | dol.schedule_c_part1_item2.provider_other_srvc_cod | Concatenated service type codes for this provider |
| provider_other_us_address1 | character varyi | YES | dol.schedule_c_part1_item2.provider_other_us_addre | Provider US address line 1 |
| provider_other_us_address2 | character varyi | YES | dol.schedule_c_part1_item2.provider_other_us_addre | Provider US address line 2 |
| provider_other_us_city | character varyi | YES | dol.schedule_c_part1_item2.provider_other_us_city | Provider US city |
| provider_other_us_state | character varyi | YES | dol.schedule_c_part1_item2.provider_other_us_state | Provider US state code (2-letter) |
| provider_other_us_zip | character varyi | YES | dol.schedule_c_part1_item2.provider_other_us_zip | Provider US ZIP code |
| row_order | integer | YES | dol.schedule_c_part1_item2.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_c_part1_item2_codes (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c_part1_item2_codes.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| code_order | integer | YES | dol.schedule_c_part1_item2_codes.code_order | Sequence number of the service code within a given row_order — preserves code or |
| created_at | timestamp with  | NO | dol.schedule_c_part1_item2_codes.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c_part1_item2_codes.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c_part1_item2_codes.id | Auto-increment surrogate primary key |
| row_order | integer | YES | dol.schedule_c_part1_item2_codes.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |
| service_code | character varyi | YES | dol.schedule_c_part1_item2_codes.service_code | DOL service type classification code identifying the category of service provide |

### LEAF: dol.schedule_c_part1_item3 (22 columns, 22 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c_part1_item3.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_c_part1_item3.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c_part1_item3.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c_part1_item3.id | Auto-increment surrogate primary key |
| prov_payor_foreign_address1 | character varyi | YES | dol.schedule_c_part1_item3.prov_payor_foreign_addr | Payor foreign address line 1 |
| prov_payor_foreign_address2 | character varyi | YES | dol.schedule_c_part1_item3.prov_payor_foreign_addr | Payor foreign address line 2 |
| prov_payor_foreign_city | character varyi | YES | dol.schedule_c_part1_item3.prov_payor_foreign_city | Payor foreign city |
| prov_payor_foreign_cntry | character varyi | YES | dol.schedule_c_part1_item3.prov_payor_foreign_cntr | Payor foreign country |
| prov_payor_foreign_postal_cd | character varyi | YES | dol.schedule_c_part1_item3.prov_payor_foreign_post | Payor foreign postal code |
| prov_payor_foreign_prov_state | character varyi | YES | dol.schedule_c_part1_item3.prov_payor_foreign_prov | Payor foreign province/state |
| provider_comp_explain_text | text | YES | dol.schedule_c_part1_item3.provider_comp_explain_t | Free-text explanation of the indirect compensation arrangement |
| provider_indirect_comp_amt | numeric | YES | dol.schedule_c_part1_item3.provider_indirect_comp_ | Amount of indirect compensation received (USD) |
| provider_indirect_name | character varyi | YES | dol.schedule_c_part1_item3.provider_indirect_name | Name of service provider receiving indirect compensation |
| provider_indirect_srvc_codes | character varyi | YES | dol.schedule_c_part1_item3.provider_indirect_srvc_ | Concatenated service type codes |
| provider_payor_ein | character varyi | YES | dol.schedule_c_part1_item3.provider_payor_ein | EIN of the payor |
| provider_payor_name | character varyi | YES | dol.schedule_c_part1_item3.provider_payor_name | Name of the entity that paid the indirect compensation |
| provider_payor_us_address1 | character varyi | YES | dol.schedule_c_part1_item3.provider_payor_us_addre | Payor US address line 1 |
| provider_payor_us_address2 | character varyi | YES | dol.schedule_c_part1_item3.provider_payor_us_addre | Payor US address line 2 |
| provider_payor_us_city | character varyi | YES | dol.schedule_c_part1_item3.provider_payor_us_city | Payor US city |
| provider_payor_us_state | character varyi | YES | dol.schedule_c_part1_item3.provider_payor_us_state | Payor US state code (2-letter) |
| provider_payor_us_zip | character varyi | YES | dol.schedule_c_part1_item3.provider_payor_us_zip | Payor US ZIP code |
| row_order | integer | YES | dol.schedule_c_part1_item3.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_c_part1_item3_codes (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c_part1_item3_codes.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| code_order | integer | YES | dol.schedule_c_part1_item3_codes.code_order | Sequence number of the service code within a given row_order — preserves code or |
| created_at | timestamp with  | NO | dol.schedule_c_part1_item3_codes.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c_part1_item3_codes.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c_part1_item3_codes.id | Auto-increment surrogate primary key |
| row_order | integer | YES | dol.schedule_c_part1_item3_codes.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |
| service_code | character varyi | YES | dol.schedule_c_part1_item3_codes.service_code | DOL service type classification code identifying the category of service provide |

### LEAF: dol.schedule_c_part2 (20 columns, 20 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c_part2.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_c_part2.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c_part2.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c_part2.id | Auto-increment surrogate primary key |
| provider_fail_ein | character varyi | YES | dol.schedule_c_part2.provider_fail_ein | EIN of the non-disclosing provider |
| provider_fail_foreign_address1 | character varyi | YES | dol.schedule_c_part2.provider_fail_foreign_address | Provider foreign address line 1 |
| provider_fail_foreign_address2 | character varyi | YES | dol.schedule_c_part2.provider_fail_foreign_address | Provider foreign address line 2 |
| provider_fail_foreign_city | character varyi | YES | dol.schedule_c_part2.provider_fail_foreign_city | Provider foreign city |
| provider_fail_foreign_cntry | character varyi | YES | dol.schedule_c_part2.provider_fail_foreign_cntry | Provider foreign country |
| provider_fail_foreign_prov_st | character varyi | YES | dol.schedule_c_part2.provider_fail_foreign_prov_st | Provider foreign province/state |
| provider_fail_forgn_postal_cd | character varyi | YES | dol.schedule_c_part2.provider_fail_forgn_postal_cd | Provider foreign postal code |
| provider_fail_info_text | text | YES | dol.schedule_c_part2.provider_fail_info_text | Free-text explanation of the provider's failure to disclose |
| provider_fail_name | character varyi | YES | dol.schedule_c_part2.provider_fail_name | Name of provider who failed/refused to disclose compensation |
| provider_fail_srvc_code | character varyi | YES | dol.schedule_c_part2.provider_fail_srvc_code | Service type code(s) for the non-disclosing provider |
| provider_fail_us_address1 | character varyi | YES | dol.schedule_c_part2.provider_fail_us_address1 | Provider US address line 1 |
| provider_fail_us_address2 | character varyi | YES | dol.schedule_c_part2.provider_fail_us_address2 | Provider US address line 2 |
| provider_fail_us_city | character varyi | YES | dol.schedule_c_part2.provider_fail_us_city | Provider US city |
| provider_fail_us_state | character varyi | YES | dol.schedule_c_part2.provider_fail_us_state | Provider US state code (2-letter) |
| provider_fail_us_zip | character varyi | YES | dol.schedule_c_part2.provider_fail_us_zip | Provider US ZIP code |
| row_order | integer | YES | dol.schedule_c_part2.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_c_part2_codes (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c_part2_codes.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| code_order | integer | YES | dol.schedule_c_part2_codes.code_order | Sequence number of the service code within a given row_order — preserves code or |
| created_at | timestamp with  | NO | dol.schedule_c_part2_codes.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c_part2_codes.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c_part2_codes.id | Auto-increment surrogate primary key |
| row_order | integer | YES | dol.schedule_c_part2_codes.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |
| service_code | character varyi | YES | dol.schedule_c_part2_codes.service_code | DOL service type classification code identifying the category of service provide |

### LEAF: dol.schedule_c_part3 (22 columns, 22 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_c_part3.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_c_part3.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_c_part3.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_c_part3.id | Auto-increment surrogate primary key |
| provider_term_ein | character varyi | YES | dol.schedule_c_part3.provider_term_ein | EIN of the terminated provider |
| provider_term_foreign_address1 | character varyi | YES | dol.schedule_c_part3.provider_term_foreign_address | Provider foreign address line 1 |
| provider_term_foreign_address2 | character varyi | YES | dol.schedule_c_part3.provider_term_foreign_address | Provider foreign address line 2 |
| provider_term_foreign_city | character varyi | YES | dol.schedule_c_part3.provider_term_foreign_city | Provider foreign city |
| provider_term_foreign_cntry | character varyi | YES | dol.schedule_c_part3.provider_term_foreign_cntry | Provider foreign country |
| provider_term_foreign_prov_st | character varyi | YES | dol.schedule_c_part3.provider_term_foreign_prov_st | Provider foreign province/state |
| provider_term_forgn_postal_cd | character varyi | YES | dol.schedule_c_part3.provider_term_forgn_postal_cd | Provider foreign postal code |
| provider_term_name | character varyi | YES | dol.schedule_c_part3.provider_term_name | Name of the terminated service provider |
| provider_term_phone_num | character varyi | YES | dol.schedule_c_part3.provider_term_phone_num | US phone number of the terminated provider |
| provider_term_phone_num_foreig | character varyi | YES | dol.schedule_c_part3.provider_term_phone_num_forei | Foreign phone number of the terminated provider |
| provider_term_position | character varyi | YES | dol.schedule_c_part3.provider_term_position | Position/role held by the terminated provider |
| provider_term_text | text | YES | dol.schedule_c_part3.provider_term_text | Free-text explanation of the termination |
| provider_term_us_address1 | character varyi | YES | dol.schedule_c_part3.provider_term_us_address1 | Provider US address line 1 |
| provider_term_us_address2 | character varyi | YES | dol.schedule_c_part3.provider_term_us_address2 | Provider US address line 2 |
| provider_term_us_city | character varyi | YES | dol.schedule_c_part3.provider_term_us_city | Provider US city |
| provider_term_us_state | character varyi | YES | dol.schedule_c_part3.provider_term_us_state | Provider US state code (2-letter) |
| provider_term_us_zip | character varyi | YES | dol.schedule_c_part3.provider_term_us_zip | Provider US ZIP code |
| row_order | integer | YES | dol.schedule_c_part3.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_d (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_d.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_d.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_d.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_d.id | Auto-increment surrogate primary key |
| sch_d_ein | character varyi | YES | dol.schedule_d.sch_d_ein | EIN of the DFE sponsor |
| sch_d_plan_year_begin_date | character varyi | YES | dol.schedule_d.sch_d_plan_year_begin_date | First day of the DFE plan year (YYYY-MM-DD) |
| sch_d_pn | character varyi | YES | dol.schedule_d.sch_d_pn | Plan number of the DFE |
| sch_d_tax_prd | character varyi | YES | dol.schedule_d.sch_d_tax_prd | Tax period end date of the DFE filing |

### LEAF: dol.schedule_d_part1 (11 columns, 11 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_d_part1.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_d_part1.created_at | Timestamp when this row was loaded into the database |
| dfe_p1_entity_code | character varyi | YES | dol.schedule_d_part1.dfe_p1_entity_code | Entity type code of the participating plan |
| dfe_p1_entity_name | character varyi | YES | dol.schedule_d_part1.dfe_p1_entity_name | Name of the participating plan/entity |
| dfe_p1_plan_ein | character varyi | YES | dol.schedule_d_part1.dfe_p1_plan_ein | EIN of the participating plan |
| dfe_p1_plan_int_eoy_amt | numeric | YES | dol.schedule_d_part1.dfe_p1_plan_int_eoy_amt | End-of-year interest/value amount for this plan in the DFE (USD) |
| dfe_p1_plan_pn | character varyi | YES | dol.schedule_d_part1.dfe_p1_plan_pn | Plan number of the participating plan |
| dfe_p1_spons_name | character varyi | YES | dol.schedule_d_part1.dfe_p1_spons_name | Name of the participating plan's sponsor |
| form_year | character varyi | YES | dol.schedule_d_part1.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_d_part1.id | Auto-increment surrogate primary key |
| row_order | integer | YES | dol.schedule_d_part1.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_d_part2 (9 columns, 9 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_d_part2.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_d_part2.created_at | Timestamp when this row was loaded into the database |
| dfe_p2_plan_ein | character varyi | YES | dol.schedule_d_part2.dfe_p2_plan_ein | EIN of the DFE |
| dfe_p2_plan_name | character varyi | YES | dol.schedule_d_part2.dfe_p2_plan_name | Name of the DFE in which this plan participates |
| dfe_p2_plan_pn | character varyi | YES | dol.schedule_d_part2.dfe_p2_plan_pn | Plan number of the DFE |
| dfe_p2_plan_spons_name | character varyi | YES | dol.schedule_d_part2.dfe_p2_plan_spons_name | Name of the DFE sponsor |
| form_year | character varyi | YES | dol.schedule_d_part2.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_d_part2.id | Auto-increment surrogate primary key |
| row_order | integer | YES | dol.schedule_d_part2.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_dcg (121 columns, 121 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_dcg.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_dcg.created_at | Timestamp when this row was loaded into the database |
| dcg_401k_current_year_adp_test_ind | character varyi | YES | dol.schedule_dcg.dcg_401k_current_year_adp_test_in | Indicator — 401(k) uses current year ADP test |
| dcg_401k_design_based_safe_harbor_ind | character varyi | YES | dol.schedule_dcg.dcg_401k_design_based_safe_harbor | Indicator — 401(k) uses design-based safe harbor |
| dcg_401k_na_ind | character varyi | YES | dol.schedule_dcg.dcg_401k_na_ind | Indicator — 401(k) testing not applicable |
| dcg_401k_prior_year_adp_test_ind | character varyi | YES | dol.schedule_dcg.dcg_401k_prior_year_adp_test_ind | Indicator — 401(k) uses prior year ADP test |
| dcg_accountant_firm_ein | character varyi | YES | dol.schedule_dcg.dcg_accountant_firm_ein | EIN of the accounting firm |
| dcg_accountant_firm_name | character varyi | YES | dol.schedule_dcg.dcg_accountant_firm_name | Name of the accounting firm |
| dcg_acct_performed_ltd_audit_103_12d_ind | character varyi | YES | dol.schedule_dcg.dcg_acct_performed_ltd_audit_103_ | Indicator — accountant performed limited-scope audit per DOL Reg 2520.103-12(d) |
| dcg_acct_performed_ltd_audit_103_8_ind | character varyi | YES | dol.schedule_dcg.dcg_acct_performed_ltd_audit_103_ | Indicator — accountant performed limited-scope audit per ERISA Sec 103(a)(3)(C)  |
| dcg_acct_performed_not_ltd_audit_ind | character varyi | YES | dol.schedule_dcg.dcg_acct_performed_not_ltd_audit_ | Indicator — accountant performed full (non-limited-scope) audit |
| dcg_acctnt_opinion_type_cd | character varyi | YES | dol.schedule_dcg.dcg_acctnt_opinion_type_cd | Accountant opinion type code (1=Unqualified, 2=Qualified, 3=Disclaimer, 4=Advers |
| dcg_admin_ein | character varyi | YES | dol.schedule_dcg.dcg_admin_ein | Administrator EIN |
| dcg_admin_foreign_address1 | character varyi | YES | dol.schedule_dcg.dcg_admin_foreign_address1 | Administrator foreign address line 1 |
| dcg_admin_foreign_address2 | character varyi | YES | dol.schedule_dcg.dcg_admin_foreign_address2 | Administrator foreign address line 2 |
| dcg_admin_foreign_city | character varyi | YES | dol.schedule_dcg.dcg_admin_foreign_city | Administrator foreign city |
| dcg_admin_foreign_cntry | character varyi | YES | dol.schedule_dcg.dcg_admin_foreign_cntry | Administrator foreign country |
| dcg_admin_foreign_postal_cd | character varyi | YES | dol.schedule_dcg.dcg_admin_foreign_postal_cd | Administrator foreign postal code |
| dcg_admin_foreign_prov_state | character varyi | YES | dol.schedule_dcg.dcg_admin_foreign_prov_state | Administrator foreign province/state |
| dcg_admin_name | character varyi | YES | dol.schedule_dcg.dcg_admin_name | Plan administrator name |
| dcg_admin_phone_num | character varyi | YES | dol.schedule_dcg.dcg_admin_phone_num | Administrator US phone number |
| dcg_admin_phone_num_foreign | character varyi | YES | dol.schedule_dcg.dcg_admin_phone_num_foreign | Administrator foreign phone number |
| dcg_admin_srvc_providers_amt | numeric | YES | dol.schedule_dcg.dcg_admin_srvc_providers_amt | Payments to administrative service providers (USD) |
| dcg_admin_us_address1 | character varyi | YES | dol.schedule_dcg.dcg_admin_us_address1 | Administrator US address line 1 |
| dcg_admin_us_address2 | character varyi | YES | dol.schedule_dcg.dcg_admin_us_address2 | Administrator US address line 2 |
| dcg_admin_us_city | character varyi | YES | dol.schedule_dcg.dcg_admin_us_city | Administrator US city |
| dcg_admin_us_state | character varyi | YES | dol.schedule_dcg.dcg_admin_us_state | Administrator US state code |
| dcg_admin_us_zip | character varyi | YES | dol.schedule_dcg.dcg_admin_us_zip | Administrator US ZIP code |
| dcg_amended_ind | character varyi | YES | dol.schedule_dcg.dcg_amended_ind | Indicator — this is an amended filing |
| dcg_business_code | character varyi | YES | dol.schedule_dcg.dcg_business_code | NAICS business code of the sponsor |
| dcg_corrective_distrib_amt | numeric | YES | dol.schedule_dcg.dcg_corrective_distrib_amt | Corrective distributions (USD) |
| dcg_dc_plan_funding_reqd_ind | character varyi | YES | dol.schedule_dcg.dcg_dc_plan_funding_reqd_ind | Indicator — defined contribution plan funding required |
| dcg_deemed_distrib_partcp_lns_amt | numeric | YES | dol.schedule_dcg.dcg_deemed_distrib_partcp_lns_amt | Deemed distributions from participant loans (USD) |
| dcg_emplr_contrib_income_amt | numeric | YES | dol.schedule_dcg.dcg_emplr_contrib_income_amt | Employer contributions received (USD) |
| dcg_fail_provide_benefit_due_amt | numeric | YES | dol.schedule_dcg.dcg_fail_provide_benefit_due_amt | Amount of benefits not provided when due (USD) |
| dcg_fail_provide_benefit_due_ind | character varyi | YES | dol.schedule_dcg.dcg_fail_provide_benefit_due_ind | Indicator — plan failed to provide benefits when due |
| dcg_fail_transmit_contrib_amt | numeric | YES | dol.schedule_dcg.dcg_fail_transmit_contrib_amt | Amount of late-transmitted contributions (USD) |
| dcg_fail_transmit_contrib_ind | character varyi | YES | dol.schedule_dcg.dcg_fail_transmit_contrib_ind | Indicator — employer failed to timely transmit participant contributions |
| dcg_fidelity_bond_amt | numeric | YES | dol.schedule_dcg.dcg_fidelity_bond_amt | Fidelity bond coverage amount (USD) |
| dcg_fidelity_bond_ind | character varyi | YES | dol.schedule_dcg.dcg_fidelity_bond_ind | Indicator — plan covered by fidelity bond |
| dcg_final_ind | character varyi | YES | dol.schedule_dcg.dcg_final_ind | Indicator — this is the final filing for this DFE |
| dcg_initial_filing_ind | character varyi | YES | dol.schedule_dcg.dcg_initial_filing_ind | Indicator — initial filing for this DFE |
| dcg_iqpa_attached_ind | character varyi | YES | dol.schedule_dcg.dcg_iqpa_attached_ind | Indicator — Independent Qualified Public Accountant (IQPA) report attached |
| dcg_last_rpt_plan_name | character varyi | YES | dol.schedule_dcg.dcg_last_rpt_plan_name | Plan name from the last reported filing |
| dcg_last_rpt_plan_num | character varyi | YES | dol.schedule_dcg.dcg_last_rpt_plan_num | Plan number from the last reported filing |
| dcg_last_rpt_spons_ein | character varyi | YES | dol.schedule_dcg.dcg_last_rpt_spons_ein | Sponsor EIN from the last reported filing |
| dcg_last_rpt_spons_name | character varyi | YES | dol.schedule_dcg.dcg_last_rpt_spons_name | Sponsor name from the last reported filing |
| dcg_loss_discv_dur_year_amt | numeric | YES | dol.schedule_dcg.dcg_loss_discv_dur_year_amt | Amount of losses discovered (USD) |
| dcg_loss_discv_dur_year_ind | character varyi | YES | dol.schedule_dcg.dcg_loss_discv_dur_year_ind | Indicator — losses discovered during year due to fraud/dishonesty |
| dcg_net_assets_boy_amt | numeric | YES | dol.schedule_dcg.dcg_net_assets_boy_amt | Net assets at beginning of year (USD) |
| dcg_net_assets_eoy_amt | numeric | YES | dol.schedule_dcg.dcg_net_assets_eoy_amt | Net assets at end of year (USD) |
| dcg_net_income_amt | numeric | YES | dol.schedule_dcg.dcg_net_income_amt | Net income/loss (USD) |
| dcg_non_cash_contrib_amt | numeric | YES | dol.schedule_dcg.dcg_non_cash_contrib_amt | Non-cash contributions (USD) |
| dcg_opin_letter_date | character varyi | YES | dol.schedule_dcg.dcg_opin_letter_date | Date of IRS opinion/advisory letter |
| dcg_opin_letter_serial_num | character varyi | YES | dol.schedule_dcg.dcg_opin_letter_serial_num | IRS opinion/advisory letter serial number |
| dcg_oth_contrib_rcvd_amt | numeric | YES | dol.schedule_dcg.dcg_oth_contrib_rcvd_amt | Other contributions received (USD) |
| dcg_oth_expenses_amt | numeric | YES | dol.schedule_dcg.dcg_oth_expenses_amt | Other expenses (USD) |
| dcg_other_income_amt | numeric | YES | dol.schedule_dcg.dcg_other_income_amt | Other income (USD) |
| dcg_partcp_account_bal_boy_cnt | numeric | YES | dol.schedule_dcg.dcg_partcp_account_bal_boy_cnt | Participants with account balances at beginning of year |
| dcg_partcp_account_bal_eoy_cnt | numeric | YES | dol.schedule_dcg.dcg_partcp_account_bal_eoy_cnt | Participants with account balances at end of year |
| dcg_partcp_loans_boy_amt | numeric | YES | dol.schedule_dcg.dcg_partcp_loans_boy_amt | Participant loans at beginning of year (USD) |
| dcg_partcp_loans_eoy_amt | numeric | YES | dol.schedule_dcg.dcg_partcp_loans_eoy_amt | Participant loans at end of year (USD) |
| dcg_participant_contrib_income_amt | numeric | YES | dol.schedule_dcg.dcg_participant_contrib_income_am | Participant contributions received (USD) |
| dcg_party_in_int_not_rptd_amt | numeric | YES | dol.schedule_dcg.dcg_party_in_int_not_rptd_amt | Amount of unreported party-in-interest transactions (USD) |
| dcg_party_in_int_not_rptd_ind | character varyi | YES | dol.schedule_dcg.dcg_party_in_int_not_rptd_ind | Indicator — party-in-interest transactions not reported on Schedule G |
| dcg_plan_eff_date | character varyi | YES | dol.schedule_dcg.dcg_plan_eff_date | Effective date of the plan |
| dcg_plan_name | character varyi | YES | dol.schedule_dcg.dcg_plan_name | Plan name as reported on the filing |
| dcg_plan_num | character varyi | YES | dol.schedule_dcg.dcg_plan_num | Plan number as reported on the filing |
| dcg_plan_satisfy_tests_ind | character varyi | YES | dol.schedule_dcg.dcg_plan_satisfy_tests_ind | Indicator — plan satisfied coverage/nondiscrimination tests |
| dcg_plan_type | character varyi | YES | dol.schedule_dcg.dcg_plan_type | Type of plan (e.g., Master Trust, PSA, 103-12 IE, GIA) |
| dcg_sep_partcp_partl_vstd_cnt | numeric | YES | dol.schedule_dcg.dcg_sep_partcp_partl_vstd_cnt | Separated participants with partially vested benefits |
| dcg_spons_care_of_name | character varyi | YES | dol.schedule_dcg.dcg_spons_care_of_name | Sponsor care-of name |
| dcg_spons_dba_name | character varyi | YES | dol.schedule_dcg.dcg_spons_dba_name | Sponsor DBA (doing business as) name |
| dcg_spons_ein | character varyi | YES | dol.schedule_dcg.dcg_spons_ein | EIN of the plan sponsor |
| dcg_spons_foreign_address1 | character varyi | YES | dol.schedule_dcg.dcg_spons_foreign_address1 | Sponsor foreign address line 1 |
| dcg_spons_foreign_address2 | character varyi | YES | dol.schedule_dcg.dcg_spons_foreign_address2 | Sponsor foreign address line 2 |
| dcg_spons_foreign_city | character varyi | YES | dol.schedule_dcg.dcg_spons_foreign_city | Sponsor foreign city |
| dcg_spons_foreign_cntry | character varyi | YES | dol.schedule_dcg.dcg_spons_foreign_cntry | Sponsor foreign country |
| dcg_spons_foreign_postal_cd | character varyi | YES | dol.schedule_dcg.dcg_spons_foreign_postal_cd | Sponsor foreign postal code |
| dcg_spons_foreign_prov_state | character varyi | YES | dol.schedule_dcg.dcg_spons_foreign_prov_state | Sponsor foreign province/state |
| dcg_spons_loc_foreign_address1 | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_foreign_address1 | Sponsor location foreign address line 1 |
| dcg_spons_loc_foreign_address2 | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_foreign_address2 | Sponsor location foreign address line 2 |
| dcg_spons_loc_foreign_city | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_foreign_city | Sponsor location foreign city |
| dcg_spons_loc_foreign_cntry | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_foreign_cntry | Sponsor location foreign country |
| dcg_spons_loc_foreign_postal_cd | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_foreign_postal_cd | Sponsor location foreign postal code |
| dcg_spons_loc_foreign_prov_state | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_foreign_prov_state | Sponsor location foreign province/state |
| dcg_spons_loc_us_address1 | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_us_address1 | Sponsor location (physical) US address line 1 |
| dcg_spons_loc_us_address2 | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_us_address2 | Sponsor location US address line 2 |
| dcg_spons_loc_us_city | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_us_city | Sponsor location US city |
| dcg_spons_loc_us_state | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_us_state | Sponsor location US state code |
| dcg_spons_loc_us_zip | character varyi | YES | dol.schedule_dcg.dcg_spons_loc_us_zip | Sponsor location US ZIP code |
| dcg_spons_phone_num | character varyi | YES | dol.schedule_dcg.dcg_spons_phone_num | Sponsor US phone number |
| dcg_spons_phone_num_foreign | character varyi | YES | dol.schedule_dcg.dcg_spons_phone_num_foreign | Sponsor foreign phone number |
| dcg_spons_us_address1 | character varyi | YES | dol.schedule_dcg.dcg_spons_us_address1 | Sponsor US mailing address line 1 |
| dcg_spons_us_address2 | character varyi | YES | dol.schedule_dcg.dcg_spons_us_address2 | Sponsor US mailing address line 2 |
| dcg_spons_us_city | character varyi | YES | dol.schedule_dcg.dcg_spons_us_city | Sponsor US city |
| dcg_spons_us_state | character varyi | YES | dol.schedule_dcg.dcg_spons_us_state | Sponsor US state code (2-letter) |
| dcg_spons_us_zip | character varyi | YES | dol.schedule_dcg.dcg_spons_us_zip | Sponsor US ZIP code |
| dcg_sponsor_name | character varyi | YES | dol.schedule_dcg.dcg_sponsor_name | Sponsor name as reported |
| dcg_tot_act_partcp_boy_cnt | numeric | YES | dol.schedule_dcg.dcg_tot_act_partcp_boy_cnt | Total active participants at beginning of year |
| dcg_tot_act_partcp_eoy_cnt | numeric | YES | dol.schedule_dcg.dcg_tot_act_partcp_eoy_cnt | Total active participants at end of year |
| dcg_tot_act_rtd_sep_benef_cnt | numeric | YES | dol.schedule_dcg.dcg_tot_act_rtd_sep_benef_cnt | Total active, retired, separated beneficiaries count |
| dcg_tot_assets_boy_amt | numeric | YES | dol.schedule_dcg.dcg_tot_assets_boy_amt | Total assets at beginning of year (USD) |
| dcg_tot_assets_eoy_amt | numeric | YES | dol.schedule_dcg.dcg_tot_assets_eoy_amt | Total assets at end of year (USD) |
| dcg_tot_bnft_amt | numeric | YES | dol.schedule_dcg.dcg_tot_bnft_amt | Total benefits paid (USD) |
| dcg_tot_contrib_amt | numeric | YES | dol.schedule_dcg.dcg_tot_contrib_amt | Total contributions (USD) |
| dcg_tot_expenses_amt | numeric | YES | dol.schedule_dcg.dcg_tot_expenses_amt | Total expenses (USD) |
| dcg_tot_income_amt | numeric | YES | dol.schedule_dcg.dcg_tot_income_amt | Total income (USD) |
| dcg_tot_liabilities_boy_amt | numeric | YES | dol.schedule_dcg.dcg_tot_liabilities_boy_amt | Total liabilities at beginning of year (USD) |
| dcg_tot_liabilities_eoy_amt | numeric | YES | dol.schedule_dcg.dcg_tot_liabilities_eoy_amt | Total liabilities at end of year (USD) |
| dcg_tot_partcp_boy_cnt | numeric | YES | dol.schedule_dcg.dcg_tot_partcp_boy_cnt | Total participants at beginning of year |
| dcg_tot_transfers_from_amt | numeric | YES | dol.schedule_dcg.dcg_tot_transfers_from_amt | Total transfers from other plans (USD) |
| dcg_tot_transfers_to_amt | numeric | YES | dol.schedule_dcg.dcg_tot_transfers_to_amt | Total transfers to other plans (USD) |
| dcg_type_pension_bnft_code | character varyi | YES | dol.schedule_dcg.dcg_type_pension_bnft_code | Type of pension benefit code |
| form_id | character varyi | YES | dol.schedule_dcg.form_id | DOL internal form identifier |
| form_year | character varyi | YES | dol.schedule_dcg.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_dcg.id | Auto-increment surrogate primary key |
| sch_dcg_ein | character varyi | YES | dol.schedule_dcg.sch_dcg_ein | EIN of the DFE sponsor |
| sch_dcg_name | character varyi | YES | dol.schedule_dcg.sch_dcg_name | Name of the Direct Filing Entity |
| sch_dcg_plan_num | character varyi | YES | dol.schedule_dcg.sch_dcg_plan_num | Plan number of the DFE |
| sch_dcg_sponsor_name | character varyi | YES | dol.schedule_dcg.sch_dcg_sponsor_name | Sponsor name of the DFE |

### LEAF: dol.schedule_g (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_g.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_g.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_g.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_g.id | Auto-increment surrogate primary key |
| sch_g_ein | character varyi | YES | dol.schedule_g.sch_g_ein | EIN of the plan sponsor |
| sch_g_plan_year_begin_date | character varyi | YES | dol.schedule_g.sch_g_plan_year_begin_date | First day of the plan year (YYYY-MM-DD) |
| sch_g_pn | character varyi | YES | dol.schedule_g.sch_g_pn | Plan number |
| sch_g_tax_prd | character varyi | YES | dol.schedule_g.sch_g_tax_prd | Tax period end date |

### LEAF: dol.schedule_g_part1 (25 columns, 25 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_g_part1.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_g_part1.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_g_part1.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_g_part1.id | Auto-increment surrogate primary key |
| lns_default_description_text | text | YES | dol.schedule_g_part1.lns_default_description_text | Description of the defaulted loan terms |
| lns_default_int_overdue_amt | numeric | YES | dol.schedule_g_part1.lns_default_int_overdue_amt | Overdue interest amount (USD) |
| lns_default_int_rcvd_amt | numeric | YES | dol.schedule_g_part1.lns_default_int_rcvd_amt | Interest payments received (USD) |
| lns_default_obligor_name | character varyi | YES | dol.schedule_g_part1.lns_default_obligor_name | Name of the loan obligor in default |
| lns_default_obligor_us_addr1 | character varyi | YES | dol.schedule_g_part1.lns_default_obligor_us_addr1 | Obligor US address line 1 |
| lns_default_obligor_us_addr2 | character varyi | YES | dol.schedule_g_part1.lns_default_obligor_us_addr2 | Obligor US address line 2 |
| lns_default_obligor_us_city | character varyi | YES | dol.schedule_g_part1.lns_default_obligor_us_city | Obligor US city |
| lns_default_obligor_us_state | character varyi | YES | dol.schedule_g_part1.lns_default_obligor_us_state | Obligor US state code |
| lns_default_obligor_us_zip | character varyi | YES | dol.schedule_g_part1.lns_default_obligor_us_zip | Obligor US ZIP code |
| lns_default_original_amt | numeric | YES | dol.schedule_g_part1.lns_default_original_amt | Original loan amount (USD) |
| lns_default_pii_ind | character varyi | YES | dol.schedule_g_part1.lns_default_pii_ind | Indicator — party-in-interest involvement in the defaulted loan |
| lns_default_prcpl_overdue_amt | numeric | YES | dol.schedule_g_part1.lns_default_prcpl_overdue_amt | Overdue principal amount (USD) |
| lns_default_prncpl_rcvd_amt | numeric | YES | dol.schedule_g_part1.lns_default_prncpl_rcvd_amt | Principal payments received (USD) |
| lns_default_unpaid_bal_amt | numeric | YES | dol.schedule_g_part1.lns_default_unpaid_bal_amt | Unpaid balance (USD) |
| lns_dft_obligor_foreign_addr1 | character varyi | YES | dol.schedule_g_part1.lns_dft_obligor_foreign_addr1 | Obligor foreign address line 1 |
| lns_dft_obligor_foreign_addr2 | character varyi | YES | dol.schedule_g_part1.lns_dft_obligor_foreign_addr2 | Obligor foreign address line 2 |
| lns_dft_obligor_foreign_city | character varyi | YES | dol.schedule_g_part1.lns_dft_obligor_foreign_city | Obligor foreign city |
| lns_dft_obligor_forgn_country | character varyi | YES | dol.schedule_g_part1.lns_dft_obligor_forgn_country | Obligor foreign country |
| lns_dft_obligor_forgn_post_cd | character varyi | YES | dol.schedule_g_part1.lns_dft_obligor_forgn_post_cd | Obligor foreign postal code |
| lns_dft_obligor_forgn_prov_st | character varyi | YES | dol.schedule_g_part1.lns_dft_obligor_forgn_prov_st | Obligor foreign province/state |
| row_order | integer | YES | dol.schedule_g_part1.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_g_part2 (15 columns, 15 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_g_part2.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_g_part2.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_g_part2.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_g_part2.id | Auto-increment surrogate primary key |
| leases_default_arrears_amt | numeric | YES | dol.schedule_g_part2.leases_default_arrears_amt | Amount in arrears (USD) |
| leases_default_cost_amt | numeric | YES | dol.schedule_g_part2.leases_default_cost_amt | Original cost of the leased property (USD) |
| leases_default_curr_value_amt | numeric | YES | dol.schedule_g_part2.leases_default_curr_value_amt | Current value of the leased property (USD) |
| leases_default_expense_pd_amt | numeric | YES | dol.schedule_g_part2.leases_default_expense_pd_amt | Expenses paid by plan related to the lease (USD) |
| leases_default_lessor_name | character varyi | YES | dol.schedule_g_part2.leases_default_lessor_name | Name of the lessor in default |
| leases_default_net_rcpt_amt | numeric | YES | dol.schedule_g_part2.leases_default_net_rcpt_amt | Net rental receipts (USD) |
| leases_default_pii_ind | character varyi | YES | dol.schedule_g_part2.leases_default_pii_ind | Indicator — party-in-interest involvement in the defaulted lease |
| leases_default_relation_text | text | YES | dol.schedule_g_part2.leases_default_relation_text | Relationship of lessor to the plan |
| leases_default_rentl_rcpt_amt | numeric | YES | dol.schedule_g_part2.leases_default_rentl_rcpt_amt | Gross rental receipts (USD) |
| leases_default_terms_text | text | YES | dol.schedule_g_part2.leases_default_terms_text | Description of the lease terms |
| row_order | integer | YES | dol.schedule_g_part2.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_g_part3 (15 columns, 15 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_g_part3.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_g_part3.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_g_part3.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_g_part3.id | Auto-increment surrogate primary key |
| non_exempt_cost_ast_amt | numeric | YES | dol.schedule_g_part3.non_exempt_cost_ast_amt | Cost of asset (USD) |
| non_exempt_curr_value_ast_amt | numeric | YES | dol.schedule_g_part3.non_exempt_curr_value_ast_amt | Current value of asset (USD) |
| non_exempt_expense_incr_amt | numeric | YES | dol.schedule_g_part3.non_exempt_expense_incr_amt | Expenses incurred (USD) |
| non_exempt_gain_loss_amt | numeric | YES | dol.schedule_g_part3.non_exempt_gain_loss_amt | Net gain or loss on the transaction (USD) |
| non_exempt_ls_rntl_amt | numeric | YES | dol.schedule_g_part3.non_exempt_ls_rntl_amt | Lease/rental amount (USD) |
| non_exempt_party_name | character varyi | YES | dol.schedule_g_part3.non_exempt_party_name | Name of the party involved in the nonexempt transaction |
| non_exempt_pur_price_amt | numeric | YES | dol.schedule_g_part3.non_exempt_pur_price_amt | Purchase price (USD) |
| non_exempt_relation_text | text | YES | dol.schedule_g_part3.non_exempt_relation_text | Relationship of the party to the plan |
| non_exempt_sell_price_amt | numeric | YES | dol.schedule_g_part3.non_exempt_sell_price_amt | Selling price (USD) |
| non_exempt_terms_text | text | YES | dol.schedule_g_part3.non_exempt_terms_text | Description of the transaction terms |
| row_order | integer | YES | dol.schedule_g_part3.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_h (169 columns, 169 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| accountant_firm_ein | character varyi | YES | dol.schedule_h.accountant_firm_ein | EIN of the accounting firm |
| accountant_firm_name | character varyi | YES | dol.schedule_h.accountant_firm_name | Name of the accounting firm |
| acct_opin_not_on_file_ind | character varyi | YES | dol.schedule_h.acct_opin_not_on_file_ind | Indicator — accountant opinion not on file |
| acct_perf_ltd_audit_103_12_ind | character varyi | YES | dol.schedule_h.acct_perf_ltd_audit_103_12_ind | Indicator — accountant performed limited-scope audit per DOL Reg 2520.103-12(d) |
| acct_perf_ltd_audit_103_8_ind | character varyi | YES | dol.schedule_h.acct_perf_ltd_audit_103_8_ind | Indicator — accountant performed limited-scope audit per DOL Reg 2520.103-8 |
| acct_perf_not_ltd_audit_ind | character varyi | YES | dol.schedule_h.acct_perf_not_ltd_audit_ind | Indicator — accountant performed full (non-limited-scope) audit |
| acct_performed_ltd_audit_ind | character varyi | YES | dol.schedule_h.acct_performed_ltd_audit_ind | Indicator — accountant performed a limited-scope audit |
| acctnt_opinion_type_cd | character varyi | YES | dol.schedule_h.acctnt_opinion_type_cd | Accountant opinion type code (1=Unqualified, 2=Qualified, 3=Disclaimer, 4=Advers |
| ack_id | character varyi | NO | dol.schedule_h.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| acquis_indbt_boy_amt | numeric | YES | dol.schedule_h.acquis_indbt_boy_amt | Acquisition indebtedness — BOY (USD) |
| acquis_indbt_eoy_amt | numeric | YES | dol.schedule_h.acquis_indbt_eoy_amt | Acquisition indebtedness — EOY (USD) |
| actuarial_fees_amt | numeric | YES | dol.schedule_h.actuarial_fees_amt | Actuarial fees (USD) |
| aggregate_costs_amt | numeric | YES | dol.schedule_h.aggregate_costs_amt | Aggregate costs of sold/exchanged assets (USD) |
| aggregate_proceeds_amt | numeric | YES | dol.schedule_h.aggregate_proceeds_amt | Aggregate proceeds from sale/exchange of assets (USD) |
| all_plan_ast_distrib_ind | character varyi | YES | dol.schedule_h.all_plan_ast_distrib_ind | Indicator — all plan assets distributed to participants |
| asset_undeterm_val_amt | numeric | YES | dol.schedule_h.asset_undeterm_val_amt | Amount of assets with undetermined value (USD) |
| asset_undeterm_val_ind | character varyi | YES | dol.schedule_h.asset_undeterm_val_ind | Indicator — plan assets include investments with undetermined value |
| ast_held_invst_ind | character varyi | YES | dol.schedule_h.ast_held_invst_ind | Indicator — plan held assets for investment |
| bldgs_used_boy_amt | numeric | YES | dol.schedule_h.bldgs_used_boy_amt | Buildings and other property used in plan operation — BOY (USD) |
| bldgs_used_eoy_amt | numeric | YES | dol.schedule_h.bldgs_used_eoy_amt | Buildings and other property used in plan operation — EOY (USD) |
| bnfts_payable_boy_amt | numeric | YES | dol.schedule_h.bnfts_payable_boy_amt | Benefit claims payable — BOY (USD) |
| bnfts_payable_eoy_amt | numeric | YES | dol.schedule_h.bnfts_payable_eoy_amt | Benefit claims payable — EOY (USD) |
| common_stock_boy_amt | numeric | YES | dol.schedule_h.common_stock_boy_amt | Common stock — BOY (USD) |
| common_stock_eoy_amt | numeric | YES | dol.schedule_h.common_stock_eoy_amt | Common stock — EOY (USD) |
| comply_blackout_notice_ind | character varyi | YES | dol.schedule_h.comply_blackout_notice_ind | Indicator — plan complied with blackout notice requirements |
| contract_admin_fees_amt | numeric | YES | dol.schedule_h.contract_admin_fees_amt | Contract administrator fees (USD) |
| corp_debt_other_boy_amt | numeric | YES | dol.schedule_h.corp_debt_other_boy_amt | Corporate debt instruments (other) — BOY (USD) |
| corp_debt_other_eoy_amt | numeric | YES | dol.schedule_h.corp_debt_other_eoy_amt | Corporate debt instruments (other) — EOY (USD) |
| corp_debt_preferred_boy_amt | numeric | YES | dol.schedule_h.corp_debt_preferred_boy_amt | Corporate debt instruments (preferred) — BOY (USD) |
| corp_debt_preferred_eoy_amt | numeric | YES | dol.schedule_h.corp_debt_preferred_eoy_amt | Corporate debt instruments (preferred) — EOY (USD) |
| covered_pbgc_insurance_ind | character varyi | YES | dol.schedule_h.covered_pbgc_insurance_ind | Indicator — plan covered by PBGC insurance |
| created_at | timestamp with  | NO | dol.schedule_h.created_at | Timestamp when this row was loaded into the database |
| distrib_drt_partcp_amt | numeric | YES | dol.schedule_h.distrib_drt_partcp_amt | Distributions directly to participants/beneficiaries (USD) |
| distrib_made_employee_62_ind | character varyi | YES | dol.schedule_h.distrib_made_employee_62_ind | Indicator — distributions made to employees under age 62 who separated |
| divnd_common_stock_amt | numeric | YES | dol.schedule_h.divnd_common_stock_amt | Dividends from common stock (USD) |
| divnd_pref_stock_amt | numeric | YES | dol.schedule_h.divnd_pref_stock_amt | Dividends from preferred stock (USD) |
| emplr_contrib_boy_amt | numeric | YES | dol.schedule_h.emplr_contrib_boy_amt | Employer contributions receivable — BOY (USD) |
| emplr_contrib_eoy_amt | numeric | YES | dol.schedule_h.emplr_contrib_eoy_amt | Employer contributions receivable — EOY (USD) |
| emplr_contrib_income_amt | numeric | YES | dol.schedule_h.emplr_contrib_income_amt | Employer contributions received (USD) |
| emplr_prop_boy_amt | numeric | YES | dol.schedule_h.emplr_prop_boy_amt | Employer real property — BOY (USD) |
| emplr_prop_eoy_amt | numeric | YES | dol.schedule_h.emplr_prop_eoy_amt | Employer real property — EOY (USD) |
| emplr_sec_boy_amt | numeric | YES | dol.schedule_h.emplr_sec_boy_amt | Employer securities — BOY (USD) |
| emplr_sec_eoy_amt | numeric | YES | dol.schedule_h.emplr_sec_eoy_amt | Employer securities — EOY (USD) |
| fail_provide_benefit_due_amt | numeric | YES | dol.schedule_h.fail_provide_benefit_due_amt | Amount of benefits not provided when due (USD) |
| fail_provide_benefit_due_ind | character varyi | YES | dol.schedule_h.fail_provide_benefit_due_ind | Indicator — plan failed to provide benefits when due |
| fail_transmit_contrib_amt | numeric | YES | dol.schedule_h.fail_transmit_contrib_amt | Amount of late-transmitted contributions (USD) |
| fail_transmit_contrib_ind | character varyi | YES | dol.schedule_h.fail_transmit_contrib_ind | Indicator — employer failed to timely transmit participant contributions |
| fdcry_trust_cust_phon_nu_fore | character varyi | YES | dol.schedule_h.fdcry_trust_cust_phon_nu_fore | Trustee/custodian foreign phone number |
| fdcry_trust_cust_phon_num | character varyi | YES | dol.schedule_h.fdcry_trust_cust_phon_num | Trustee/custodian US phone number |
| fdcry_trust_ein | character varyi | YES | dol.schedule_h.fdcry_trust_ein | EIN of the fiduciary trust |
| fdcry_trust_name | character varyi | YES | dol.schedule_h.fdcry_trust_name | Name of the fiduciary trust |
| fdcry_trustee_cust_name | character varyi | YES | dol.schedule_h.fdcry_trustee_cust_name | Name of the fiduciary trustee/custodian |
| five_prcnt_trans_ind | character varyi | YES | dol.schedule_h.five_prcnt_trans_ind | Indicator — single transaction exceeded 5% of plan assets |
| form_year | character varyi | YES | dol.schedule_h.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| gain_loss_103_12_invst_amt | numeric | YES | dol.schedule_h.gain_loss_103_12_invst_amt | Net investment gain/loss from 103-12 investment entities (USD) |
| gain_loss_com_trust_amt | numeric | YES | dol.schedule_h.gain_loss_com_trust_amt | Net investment gain/loss from common/collective trusts (USD) |
| gain_loss_master_tr_amt | numeric | YES | dol.schedule_h.gain_loss_master_tr_amt | Net investment gain/loss from master trusts (USD) |
| gain_loss_pool_sep_amt | numeric | YES | dol.schedule_h.gain_loss_pool_sep_amt | Net investment gain/loss from pooled separate accounts (USD) |
| gain_loss_reg_invst_amt | numeric | YES | dol.schedule_h.gain_loss_reg_invst_amt | Net investment gain/loss from registered investment companies (USD) |
| govt_sec_boy_amt | numeric | YES | dol.schedule_h.govt_sec_boy_amt | US government securities — BOY (USD) |
| govt_sec_eoy_amt | numeric | YES | dol.schedule_h.govt_sec_eoy_amt | US government securities — EOY (USD) |
| id | bigint | NO | dol.schedule_h.id | Auto-increment surrogate primary key |
| in_service_distrib_amt | numeric | YES | dol.schedule_h.in_service_distrib_amt | Total in-service distributions (USD) |
| in_service_distrib_ind | character varyi | YES | dol.schedule_h.in_service_distrib_ind | Indicator — in-service distributions made |
| ins_carrier_bnfts_amt | numeric | YES | dol.schedule_h.ins_carrier_bnfts_amt | Benefits paid via insurance carriers (USD) |
| ins_co_gen_acct_boy_amt | numeric | YES | dol.schedule_h.ins_co_gen_acct_boy_amt | Value of funds in insurance company general accounts — BOY (USD) |
| ins_co_gen_acct_eoy_amt | numeric | YES | dol.schedule_h.ins_co_gen_acct_eoy_amt | Value of funds in insurance company general accounts — EOY (USD) |
| int_103_12_invst_boy_amt | numeric | YES | dol.schedule_h.int_103_12_invst_boy_amt | Value of interest in 103-12 investment entities — BOY (USD) |
| int_103_12_invst_eoy_amt | numeric | YES | dol.schedule_h.int_103_12_invst_eoy_amt | Value of interest in 103-12 investment entities — EOY (USD) |
| int_bear_cash_amt | numeric | YES | dol.schedule_h.int_bear_cash_amt | Interest on interest-bearing cash (USD) |
| int_bear_cash_boy_amt | numeric | YES | dol.schedule_h.int_bear_cash_boy_amt | Interest-bearing cash — BOY (USD) |
| int_bear_cash_eoy_amt | numeric | YES | dol.schedule_h.int_bear_cash_eoy_amt | Interest-bearing cash — EOY (USD) |
| int_common_tr_boy_amt | numeric | YES | dol.schedule_h.int_common_tr_boy_amt | Value of interest in common/collective trusts — BOY (USD) |
| int_common_tr_eoy_amt | numeric | YES | dol.schedule_h.int_common_tr_eoy_amt | Value of interest in common/collective trusts — EOY (USD) |
| int_master_tr_boy_amt | numeric | YES | dol.schedule_h.int_master_tr_boy_amt | Value of interest in master trust — BOY (USD) |
| int_master_tr_eoy_amt | numeric | YES | dol.schedule_h.int_master_tr_eoy_amt | Value of interest in master trust — EOY (USD) |
| int_on_corp_debt_amt | numeric | YES | dol.schedule_h.int_on_corp_debt_amt | Interest on corporate debt instruments (USD) |
| int_on_govt_sec_amt | numeric | YES | dol.schedule_h.int_on_govt_sec_amt | Interest on government securities (USD) |
| int_on_oth_invst_amt | numeric | YES | dol.schedule_h.int_on_oth_invst_amt | Interest on other investments (USD) |
| int_on_oth_loans_amt | numeric | YES | dol.schedule_h.int_on_oth_loans_amt | Interest on other loans (USD) |
| int_on_partcp_loans_amt | numeric | YES | dol.schedule_h.int_on_partcp_loans_amt | Interest on participant loans (USD) |
| int_pool_sep_acct_boy_amt | numeric | YES | dol.schedule_h.int_pool_sep_acct_boy_amt | Value of interest in pooled separate accounts — BOY (USD) |
| int_pool_sep_acct_eoy_amt | numeric | YES | dol.schedule_h.int_pool_sep_acct_eoy_amt | Value of interest in pooled separate accounts — EOY (USD) |
| int_reg_invst_co_boy_amt | numeric | YES | dol.schedule_h.int_reg_invst_co_boy_amt | Value of interest in registered investment companies — BOY (USD) |
| int_reg_invst_co_eoy_amt | numeric | YES | dol.schedule_h.int_reg_invst_co_eoy_amt | Value of interest in registered investment companies — EOY (USD) |
| invst_mgmt_fees_amt | numeric | YES | dol.schedule_h.invst_mgmt_fees_amt | Investment management fees (USD) |
| iqpa_audit_fees_amt | numeric | YES | dol.schedule_h.iqpa_audit_fees_amt | IQPA audit fees (USD) |
| joint_venture_boy_amt | numeric | YES | dol.schedule_h.joint_venture_boy_amt | Partnership/joint venture interests — BOY (USD) |
| joint_venture_eoy_amt | numeric | YES | dol.schedule_h.joint_venture_eoy_amt | Partnership/joint venture interests — EOY (USD) |
| leases_in_default_amt | numeric | YES | dol.schedule_h.leases_in_default_amt | Amount of leases in default (USD) |
| leases_in_default_ind | character varyi | YES | dol.schedule_h.leases_in_default_ind | Indicator — plan has leases in default or uncollectible |
| legal_fees_amt | numeric | YES | dol.schedule_h.legal_fees_amt | Legal fees (USD) |
| loans_in_default_amt | numeric | YES | dol.schedule_h.loans_in_default_amt | Amount of loans in default (USD) |
| loans_in_default_ind | character varyi | YES | dol.schedule_h.loans_in_default_ind | Indicator — plan has loans in default or uncollectible |
| loss_discv_dur_year_amt | numeric | YES | dol.schedule_h.loss_discv_dur_year_amt | Amount of losses discovered (USD) |
| loss_discv_dur_year_ind | character varyi | YES | dol.schedule_h.loss_discv_dur_year_ind | Indicator — losses discovered during year from fraud/dishonesty |
| net_assets_boy_amt | numeric | YES | dol.schedule_h.net_assets_boy_amt | Net assets — beginning of year (USD) |
| net_assets_eoy_amt | numeric | YES | dol.schedule_h.net_assets_eoy_amt | Net assets — end of year (USD) |
| net_income_amt | numeric | YES | dol.schedule_h.net_income_amt | Net income/loss (USD) |
| non_cash_contrib_amt | numeric | YES | dol.schedule_h.non_cash_contrib_amt | Total non-cash contributions (USD) |
| non_cash_contrib_bs_amt | numeric | YES | dol.schedule_h.non_cash_contrib_bs_amt | Non-cash contributions included in total (USD) |
| non_cash_contrib_ind | character varyi | YES | dol.schedule_h.non_cash_contrib_ind | Indicator — plan received non-cash contributions |
| non_int_bear_cash_boy_amt | numeric | YES | dol.schedule_h.non_int_bear_cash_boy_amt | Non-interest-bearing cash — beginning of year (USD) |
| non_int_bear_cash_eoy_amt | numeric | YES | dol.schedule_h.non_int_bear_cash_eoy_amt | Non-interest-bearing cash — end of year (USD) |
| oprtng_payable_boy_amt | numeric | YES | dol.schedule_h.oprtng_payable_boy_amt | Operating payables — BOY (USD) |
| oprtng_payable_eoy_amt | numeric | YES | dol.schedule_h.oprtng_payable_eoy_amt | Operating payables — EOY (USD) |
| oth_bnft_payment_amt | numeric | YES | dol.schedule_h.oth_bnft_payment_amt | Other benefit payments (USD) |
| oth_contrib_rcvd_amt | numeric | YES | dol.schedule_h.oth_contrib_rcvd_amt | Other contributions received (USD) |
| oth_invst_boy_amt | numeric | YES | dol.schedule_h.oth_invst_boy_amt | Other investments — BOY (USD) |
| oth_invst_eoy_amt | numeric | YES | dol.schedule_h.oth_invst_eoy_amt | Other investments — EOY (USD) |
| oth_recordkeeping_fees_amt | numeric | YES | dol.schedule_h.oth_recordkeeping_fees_amt | Other recordkeeping fees (USD) |
| other_admin_fees_amt | numeric | YES | dol.schedule_h.other_admin_fees_amt | Other administrative fees (USD) |
| other_income_amt | numeric | YES | dol.schedule_h.other_income_amt | Other income (USD) |
| other_liab_boy_amt | numeric | YES | dol.schedule_h.other_liab_boy_amt | Other liabilities — BOY (USD) |
| other_liab_eoy_amt | numeric | YES | dol.schedule_h.other_liab_eoy_amt | Other liabilities — EOY (USD) |
| other_loans_boy_amt | numeric | YES | dol.schedule_h.other_loans_boy_amt | Loans (other than to participants) — BOY (USD) |
| other_loans_eoy_amt | numeric | YES | dol.schedule_h.other_loans_eoy_amt | Loans (other than to participants) — EOY (USD) |
| other_receivables_boy_amt | numeric | YES | dol.schedule_h.other_receivables_boy_amt | Other receivables — BOY (USD) |
| other_receivables_eoy_amt | numeric | YES | dol.schedule_h.other_receivables_eoy_amt | Other receivables — EOY (USD) |
| other_trustee_fees_expenses_amt | numeric | YES | dol.schedule_h.other_trustee_fees_expenses_amt | Other trustee fees and expenses (USD) |
| partcp_contrib_boy_amt | numeric | YES | dol.schedule_h.partcp_contrib_boy_amt | Participant contributions receivable — BOY (USD) |
| partcp_contrib_eoy_amt | numeric | YES | dol.schedule_h.partcp_contrib_eoy_amt | Participant contributions receivable — EOY (USD) |
| partcp_loans_boy_amt | numeric | YES | dol.schedule_h.partcp_loans_boy_amt | Participant loans — BOY (USD) |
| partcp_loans_eoy_amt | numeric | YES | dol.schedule_h.partcp_loans_eoy_amt | Participant loans — EOY (USD) |
| participant_contrib_amt | numeric | YES | dol.schedule_h.participant_contrib_amt | Participant contributions received (USD) |
| party_in_int_not_rptd_amt | numeric | YES | dol.schedule_h.party_in_int_not_rptd_amt | Amount of unreported party-in-interest transactions (USD) |
| party_in_int_not_rptd_ind | character varyi | YES | dol.schedule_h.party_in_int_not_rptd_ind | Indicator — party-in-interest transactions not reported on Sch G |
| plan_blackout_period_ind | character varyi | YES | dol.schedule_h.plan_blackout_period_ind | Indicator — plan had a blackout period |
| plan_ins_fdlty_bond_amt | numeric | YES | dol.schedule_h.plan_ins_fdlty_bond_amt | Fidelity bond coverage amount (USD) |
| plan_ins_fdlty_bond_ind | character varyi | YES | dol.schedule_h.plan_ins_fdlty_bond_ind | Indicator — plan covered by fidelity bond |
| pref_stock_boy_amt | numeric | YES | dol.schedule_h.pref_stock_boy_amt | Preferred stock — BOY (USD) |
| pref_stock_eoy_amt | numeric | YES | dol.schedule_h.pref_stock_eoy_amt | Preferred stock — EOY (USD) |
| premium_filing_confirm_number | character varyi | YES | dol.schedule_h.premium_filing_confirm_number | PBGC premium filing confirmation number |
| professional_fees_amt | numeric | YES | dol.schedule_h.professional_fees_amt | Professional fees (legal, accounting) (USD) |
| real_estate_boy_amt | numeric | YES | dol.schedule_h.real_estate_boy_amt | Real estate (other than employer property) — BOY (USD) |
| real_estate_eoy_amt | numeric | YES | dol.schedule_h.real_estate_eoy_amt | Real estate (other than employer property) — EOY (USD) |
| registered_invst_amt | numeric | YES | dol.schedule_h.registered_invst_amt | Dividends from registered investment companies (USD) |
| res_term_plan_adpt_amt | numeric | YES | dol.schedule_h.res_term_plan_adpt_amt | Amount of plan assets at time of termination resolution (USD) |
| res_term_plan_adpt_ind | character varyi | YES | dol.schedule_h.res_term_plan_adpt_ind | Indicator — resolution to terminate plan adopted |
| salaries_allowances_amt | numeric | YES | dol.schedule_h.salaries_allowances_amt | Salaries and allowances — administrative expenses (USD) |
| sch_h_ein | character varyi | YES | dol.schedule_h.sch_h_ein | EIN of the plan sponsor |
| sch_h_plan_year_begin_date | character varyi | YES | dol.schedule_h.sch_h_plan_year_begin_date | First day of the plan year (YYYY-MM-DD) |
| sch_h_pn | character varyi | YES | dol.schedule_h.sch_h_pn | Plan number |
| sch_h_tax_prd | character varyi | YES | dol.schedule_h.sch_h_tax_prd | Tax period end date |
| tot_admin_expenses_amt | numeric | YES | dol.schedule_h.tot_admin_expenses_amt | Total administrative expenses (USD) |
| tot_assets_boy_amt | numeric | YES | dol.schedule_h.tot_assets_boy_amt | Total assets — beginning of year (USD) |
| tot_assets_eoy_amt | numeric | YES | dol.schedule_h.tot_assets_eoy_amt | Total assets — end of year (USD) |
| tot_contrib_amt | numeric | YES | dol.schedule_h.tot_contrib_amt | Total contributions (USD) |
| tot_corrective_distrib_amt | numeric | YES | dol.schedule_h.tot_corrective_distrib_amt | Corrective distributions (USD) |
| tot_deemed_distr_part_lns_amt | numeric | YES | dol.schedule_h.tot_deemed_distr_part_lns_amt | Deemed distributions from participant loans (USD) |
| tot_distrib_bnft_amt | numeric | YES | dol.schedule_h.tot_distrib_bnft_amt | Total benefit distributions (USD) |
| tot_expenses_amt | numeric | YES | dol.schedule_h.tot_expenses_amt | Total expenses (USD) |
| tot_gain_loss_sale_ast_amt | numeric | YES | dol.schedule_h.tot_gain_loss_sale_ast_amt | Net gain/loss on sale of assets (USD) |
| tot_income_amt | numeric | YES | dol.schedule_h.tot_income_amt | Total income (USD) |
| tot_int_expense_amt | numeric | YES | dol.schedule_h.tot_int_expense_amt | Total interest expense (USD) |
| tot_liabilities_boy_amt | numeric | YES | dol.schedule_h.tot_liabilities_boy_amt | Total liabilities — BOY (USD) |
| tot_liabilities_eoy_amt | numeric | YES | dol.schedule_h.tot_liabilities_eoy_amt | Total liabilities — EOY (USD) |
| tot_transfers_from_amt | numeric | YES | dol.schedule_h.tot_transfers_from_amt | Total transfers from other plans (USD) |
| tot_transfers_to_amt | numeric | YES | dol.schedule_h.tot_transfers_to_amt | Total transfers to other plans (USD) |
| tot_unrealzd_apprctn_amt | numeric | YES | dol.schedule_h.tot_unrealzd_apprctn_amt | Total unrealized appreciation/depreciation (USD) |
| total_dividends_amt | numeric | YES | dol.schedule_h.total_dividends_amt | Total dividend income (USD) |
| total_interest_amt | numeric | YES | dol.schedule_h.total_interest_amt | Total interest income (USD) |
| total_rents_amt | numeric | YES | dol.schedule_h.total_rents_amt | Total rents (USD) |
| trust_incur_unrel_tax_inc_amt | numeric | YES | dol.schedule_h.trust_incur_unrel_tax_inc_amt | Amount of unrelated business taxable income (USD) |
| trust_incur_unrel_tax_inc_ind | character varyi | YES | dol.schedule_h.trust_incur_unrel_tax_inc_ind | Indicator — trust incurred unrelated business taxable income |
| trustee_custodial_fees_amt | numeric | YES | dol.schedule_h.trustee_custodial_fees_amt | Trustee/custodial fees (USD) |
| unrealzd_apprctn_oth_amt | numeric | YES | dol.schedule_h.unrealzd_apprctn_oth_amt | Unrealized appreciation/depreciation — other (USD) |
| unrealzd_apprctn_re_amt | numeric | YES | dol.schedule_h.unrealzd_apprctn_re_amt | Unrealized appreciation/depreciation — real estate (USD) |
| valuation_appraisal_fees_amt | numeric | YES | dol.schedule_h.valuation_appraisal_fees_amt | Valuation/appraisal fees (USD) |

### LEAF: dol.schedule_h_part1 (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_h_part1.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_h_part1.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_h_part1.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_h_part1.id | Auto-increment surrogate primary key |
| plan_transfer_ein | character varyi | YES | dol.schedule_h_part1.plan_transfer_ein | EIN of the receiving plan |
| plan_transfer_name | character varyi | YES | dol.schedule_h_part1.plan_transfer_name | Name of the plan to which assets were transferred |
| plan_transfer_pn | character varyi | YES | dol.schedule_h_part1.plan_transfer_pn | Plan number of the receiving plan |
| row_order | integer | YES | dol.schedule_h_part1.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |

### LEAF: dol.schedule_i (80 columns, 80 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_i.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_i.created_at | Timestamp when this row was loaded into the database |
| distrib_made_employee_62_ind | character varyi | YES | dol.schedule_i.distrib_made_employee_62_ind | Indicator — distributions made to employees under age 62 who separated |
| fdcry_trust_cust_phon_nu_fore | character varyi | YES | dol.schedule_i.fdcry_trust_cust_phon_nu_fore | Trustee/custodian foreign phone number |
| fdcry_trust_cust_phone_num | character varyi | YES | dol.schedule_i.fdcry_trust_cust_phone_num | Trustee/custodian US phone number |
| fdcry_trust_ein | character varyi | YES | dol.schedule_i.fdcry_trust_ein | EIN of the fiduciary trust |
| fdcry_trust_name | character varyi | YES | dol.schedule_i.fdcry_trust_name | Name of the fiduciary trust |
| fdcry_trustee_cust_name | character varyi | YES | dol.schedule_i.fdcry_trustee_cust_name | Name of the fiduciary trustee/custodian |
| form_year | character varyi | YES | dol.schedule_i.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_i.id | Auto-increment surrogate primary key |
| in_service_distrib_amt | numeric | YES | dol.schedule_i.in_service_distrib_amt | Total in-service distributions (USD) |
| in_service_distrib_ind | character varyi | YES | dol.schedule_i.in_service_distrib_ind | Indicator — in-service distributions made |
| premium_filing_confirm_number | character varyi | YES | dol.schedule_i.premium_filing_confirm_number | PBGC premium filing confirmation number |
| sch_i_ein | character varyi | YES | dol.schedule_i.sch_i_ein | EIN of the plan sponsor |
| sch_i_plan_num | character varyi | YES | dol.schedule_i.sch_i_plan_num | Plan number |
| sch_i_plan_year_begin_date | character varyi | YES | dol.schedule_i.sch_i_plan_year_begin_date | First day of the plan year (YYYY-MM-DD) |
| sch_i_tax_prd | character varyi | YES | dol.schedule_i.sch_i_tax_prd | Tax period end date |
| sm_comply_blackout_notice_ind | character varyi | YES | dol.schedule_i.sm_comply_blackout_notice_ind | Indicator — complied with blackout notice requirements |
| sm_fail_provide_benef_due_amt | numeric | YES | dol.schedule_i.sm_fail_provide_benef_due_amt | Amount of benefits not provided when due (USD) |
| sm_fail_provide_benef_due_ind | character varyi | YES | dol.schedule_i.sm_fail_provide_benef_due_ind | Indicator — failed to provide benefits when due |
| sm_party_in_int_not_rptd_amt | numeric | YES | dol.schedule_i.sm_party_in_int_not_rptd_amt | Amount of unreported party-in-interest transactions (USD) |
| sm_party_in_int_not_rptd_ind | character varyi | YES | dol.schedule_i.sm_party_in_int_not_rptd_ind | Indicator — party-in-interest transactions not reported |
| sm_waiv_annual_iqpa_report_ind | character varyi | YES | dol.schedule_i.sm_waiv_annual_iqpa_report_ind | Indicator — annual IQPA report waived |
| small_20_prcnt_sngl_invst_amt | numeric | YES | dol.schedule_i.small_20_prcnt_sngl_invst_amt | Amount of single investment exceeding 20% (USD) |
| small_20_prcnt_sngl_invst_ind | character varyi | YES | dol.schedule_i.small_20_prcnt_sngl_invst_ind | Indicator — single investment exceeded 20% of plan assets |
| small_admin_srvc_providers_amt | numeric | YES | dol.schedule_i.small_admin_srvc_providers_amt | Payments to administrative service providers (USD) |
| small_all_plan_ast_distrib_ind | character varyi | YES | dol.schedule_i.small_all_plan_ast_distrib_ind | Indicator — all plan assets distributed |
| small_asset_undeterm_val_amt | numeric | YES | dol.schedule_i.small_asset_undeterm_val_amt | Amount of assets with undetermined value (USD) |
| small_asset_undeterm_val_ind | character varyi | YES | dol.schedule_i.small_asset_undeterm_val_ind | Indicator — assets with undetermined value |
| small_corrective_distrib_amt | numeric | YES | dol.schedule_i.small_corrective_distrib_amt | Corrective distributions (USD) |
| small_covered_pbgc_ins_ind | character varyi | YES | dol.schedule_i.small_covered_pbgc_ins_ind | Indicator — plan covered by PBGC insurance |
| small_deem_dstrb_partcp_ln_amt | numeric | YES | dol.schedule_i.small_deem_dstrb_partcp_ln_amt | Deemed distributions from participant loans (USD) |
| small_emplr_contrib_income_amt | numeric | YES | dol.schedule_i.small_emplr_contrib_income_amt | Employer contributions received (USD) |
| small_emplr_prop_eoy_amt | numeric | YES | dol.schedule_i.small_emplr_prop_eoy_amt | Employer real property at EOY (USD) |
| small_emplr_prop_eoy_ind | character varyi | YES | dol.schedule_i.small_emplr_prop_eoy_ind | Indicator — plan held employer real property at EOY |
| small_emplr_sec_eoy_amt | numeric | YES | dol.schedule_i.small_emplr_sec_eoy_amt | Employer securities at EOY (USD) |
| small_emplr_sec_eoy_ind | character varyi | YES | dol.schedule_i.small_emplr_sec_eoy_ind | Indicator — plan held employer securities at EOY |
| small_fail_transm_contrib_amt | numeric | YES | dol.schedule_i.small_fail_transm_contrib_amt | Amount of late-transmitted contributions (USD) |
| small_fail_transm_contrib_ind | character varyi | YES | dol.schedule_i.small_fail_transm_contrib_ind | Indicator — employer failed to timely transmit participant contributions |
| small_inv_real_estate_eoy_amt | numeric | YES | dol.schedule_i.small_inv_real_estate_eoy_amt | Real estate investments at EOY (USD) |
| small_inv_real_estate_eoy_ind | character varyi | YES | dol.schedule_i.small_inv_real_estate_eoy_ind | Indicator — plan invested in real estate at EOY |
| small_joint_venture_eoy_amt | numeric | YES | dol.schedule_i.small_joint_venture_eoy_amt | Joint venture investments at EOY (USD) |
| small_joint_venture_eoy_ind | character varyi | YES | dol.schedule_i.small_joint_venture_eoy_ind | Indicator — plan invested in joint ventures at EOY |
| small_leases_in_default_amt | numeric | YES | dol.schedule_i.small_leases_in_default_amt | Amount of leases in default (USD) |
| small_leases_in_default_ind | character varyi | YES | dol.schedule_i.small_leases_in_default_ind | Indicator — plan has leases in default |
| small_loans_in_default_amt | numeric | YES | dol.schedule_i.small_loans_in_default_amt | Amount of loans in default (USD) |
| small_loans_in_default_ind | character varyi | YES | dol.schedule_i.small_loans_in_default_ind | Indicator — plan has loans in default |
| small_loss_discv_dur_year_amt | numeric | YES | dol.schedule_i.small_loss_discv_dur_year_amt | Amount of losses discovered (USD) |
| small_loss_discv_dur_year_ind | character varyi | YES | dol.schedule_i.small_loss_discv_dur_year_ind | Indicator — losses discovered from fraud/dishonesty |
| small_mortg_partcp_eoy_amt | numeric | YES | dol.schedule_i.small_mortg_partcp_eoy_amt | Participant mortgages at EOY (USD) |
| small_mortg_partcp_eoy_ind | character varyi | YES | dol.schedule_i.small_mortg_partcp_eoy_ind | Indicator — plan held participant mortgages at EOY |
| small_net_assets_boy_amt | numeric | YES | dol.schedule_i.small_net_assets_boy_amt | Net assets — beginning of year (USD) |
| small_net_assets_eoy_amt | numeric | YES | dol.schedule_i.small_net_assets_eoy_amt | Net assets — end of year (USD) |
| small_net_income_amt | numeric | YES | dol.schedule_i.small_net_income_amt | Net income/loss (USD) |
| small_non_cash_contrib_amt | numeric | YES | dol.schedule_i.small_non_cash_contrib_amt | Total non-cash contributions (USD) |
| small_non_cash_contrib_bs_amt | numeric | YES | dol.schedule_i.small_non_cash_contrib_bs_amt | Non-cash contributions included in total (USD) |
| small_non_cash_contrib_ind | character varyi | YES | dol.schedule_i.small_non_cash_contrib_ind | Indicator — plan received non-cash contributions |
| small_oth_contrib_rcvd_amt | numeric | YES | dol.schedule_i.small_oth_contrib_rcvd_amt | Other contributions received (USD) |
| small_oth_expenses_amt | numeric | YES | dol.schedule_i.small_oth_expenses_amt | Other expenses (USD) |
| small_oth_lns_partcp_eoy_amt | numeric | YES | dol.schedule_i.small_oth_lns_partcp_eoy_amt | Other participant loans at EOY (USD) |
| small_oth_lns_partcp_eoy_ind | character varyi | YES | dol.schedule_i.small_oth_lns_partcp_eoy_ind | Indicator — plan held other participant loans at EOY |
| small_other_income_amt | numeric | YES | dol.schedule_i.small_other_income_amt | Other income (USD) |
| small_participant_contrib_amt | numeric | YES | dol.schedule_i.small_participant_contrib_amt | Participant contributions received (USD) |
| small_personal_prop_eoy_amt | numeric | YES | dol.schedule_i.small_personal_prop_eoy_amt | Tangible personal property at EOY (USD) |
| small_personal_prop_eoy_ind | character varyi | YES | dol.schedule_i.small_personal_prop_eoy_ind | Indicator — plan held tangible personal property at EOY |
| small_plan_blackout_period_ind | character varyi | YES | dol.schedule_i.small_plan_blackout_period_ind | Indicator — plan had a blackout period |
| small_plan_ins_fdlty_bond_amt | numeric | YES | dol.schedule_i.small_plan_ins_fdlty_bond_amt | Fidelity bond coverage amount (USD) |
| small_plan_ins_fdlty_bond_ind | character varyi | YES | dol.schedule_i.small_plan_ins_fdlty_bond_ind | Indicator — plan covered by fidelity bond |
| small_res_term_plan_adpt_amt | numeric | YES | dol.schedule_i.small_res_term_plan_adpt_amt | Amount of plan assets at time of termination resolution (USD) |
| small_res_term_plan_adpt_ind | character varyi | YES | dol.schedule_i.small_res_term_plan_adpt_ind | Indicator — resolution to terminate plan adopted |
| small_tot_assets_boy_amt | numeric | YES | dol.schedule_i.small_tot_assets_boy_amt | Total assets — beginning of year (USD) |
| small_tot_assets_eoy_amt | numeric | YES | dol.schedule_i.small_tot_assets_eoy_amt | Total assets — end of year (USD) |
| small_tot_distrib_bnft_amt | numeric | YES | dol.schedule_i.small_tot_distrib_bnft_amt | Total benefit distributions (USD) |
| small_tot_expenses_amt | numeric | YES | dol.schedule_i.small_tot_expenses_amt | Total expenses (USD) |
| small_tot_income_amt | numeric | YES | dol.schedule_i.small_tot_income_amt | Total income (USD) |
| small_tot_liabilities_boy_amt | numeric | YES | dol.schedule_i.small_tot_liabilities_boy_amt | Total liabilities — beginning of year (USD) |
| small_tot_liabilities_eoy_amt | numeric | YES | dol.schedule_i.small_tot_liabilities_eoy_amt | Total liabilities — end of year (USD) |
| small_tot_plan_transfers_amt | numeric | YES | dol.schedule_i.small_tot_plan_transfers_amt | Total plan transfers (USD) |
| trust_incur_unrel_tax_inc_amt | numeric | YES | dol.schedule_i.trust_incur_unrel_tax_inc_amt | Amount of unrelated business taxable income (USD) |
| trust_incur_unrel_tax_inc_ind | character varyi | YES | dol.schedule_i.trust_incur_unrel_tax_inc_ind | Indicator — trust incurred unrelated business taxable income |

### LEAF: dol.schedule_i_part1 (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ack_id | character varyi | NO | dol.schedule_i_part1.ack_id | DOL acknowledgment ID — unique filing identifier. Foreign key to dol.form_5500.a |
| created_at | timestamp with  | NO | dol.schedule_i_part1.created_at | Timestamp when this row was loaded into the database |
| form_year | character varyi | YES | dol.schedule_i_part1.form_year | Filing year (2023, 2024, 2025, etc.) — partition key for cross-year queries |
| id | bigint | NO | dol.schedule_i_part1.id | Auto-increment surrogate primary key |
| row_order | integer | YES | dol.schedule_i_part1.row_order | Sequence number within a single filing — preserves original CSV row ordering whe |
| small_plan_transfer_ein | character varyi | YES | dol.schedule_i_part1.small_plan_transfer_ein | EIN of the receiving plan |
| small_plan_transfer_name | character varyi | YES | dol.schedule_i_part1.small_plan_transfer_name | Name of the plan to which assets were transferred |
| small_plan_transfer_pn | character varyi | YES | dol.schedule_i_part1.small_plan_transfer_pn | Plan number of the receiving plan |

### LEAF: dol.v_dol_broker_changes (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| broker_changed | boolean | YES | dol.v_dol_broker_changes.broker_changed | _undocumented_ |
| company_name | character varyi | YES | dol.v_dol_broker_changes.company_name | _undocumented_ |
| company_unique_id | text | YES | dol.v_dol_broker_changes.company_unique_id | _undocumented_ |
| current_broker | character varyi | YES | dol.v_dol_broker_changes.current_broker | _undocumented_ |
| current_year | character varyi | YES | dol.v_dol_broker_changes.current_year | _undocumented_ |
| ein | character varyi | YES | dol.v_dol_broker_changes.ein | _undocumented_ |
| prior_broker | character varyi | YES | dol.v_dol_broker_changes.prior_broker | _undocumented_ |
| prior_year | character varyi | YES | dol.v_dol_broker_changes.prior_year | _undocumented_ |

### LEAF: dol.v_dol_carrier_changes (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| carrier_changed | boolean | YES | dol.v_dol_carrier_changes.carrier_changed | _undocumented_ |
| company_name | character varyi | YES | dol.v_dol_carrier_changes.company_name | _undocumented_ |
| company_unique_id | text | YES | dol.v_dol_carrier_changes.company_unique_id | _undocumented_ |
| current_carrier | character varyi | YES | dol.v_dol_carrier_changes.current_carrier | _undocumented_ |
| current_year | character varyi | YES | dol.v_dol_carrier_changes.current_year | _undocumented_ |
| ein | character varyi | YES | dol.v_dol_carrier_changes.ein | _undocumented_ |
| prior_carrier | character varyi | YES | dol.v_dol_carrier_changes.prior_carrier | _undocumented_ |
| prior_year | character varyi | YES | dol.v_dol_carrier_changes.prior_year | _undocumented_ |

### LEAF: dol.v_dol_filing_status (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | YES | dol.v_dol_filing_status.company_unique_id | _undocumented_ |
| ein | character varyi | YES | dol.v_dol_filing_status.ein | _undocumented_ |
| has_filing | boolean | YES | dol.v_dol_filing_status.has_filing | _undocumented_ |
| latest_form_year | text | YES | dol.v_dol_filing_status.latest_form_year | _undocumented_ |
| latest_participants | integer | YES | dol.v_dol_filing_status.latest_participants | _undocumented_ |
| plan_count | bigint | YES | dol.v_dol_filing_status.plan_count | _undocumented_ |
| state | text | YES | dol.v_dol_filing_status.state | _undocumented_ |

### LEAF: dol.v_dol_market_comparison (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| avg_pepm_broker_cost | numeric | YES | dol.v_dol_market_comparison.avg_pepm_broker_cost | _undocumented_ |
| carrier_name | character varyi | YES | dol.v_dol_market_comparison.carrier_name | _undocumented_ |
| filing_count | bigint | YES | dol.v_dol_market_comparison.filing_count | _undocumented_ |
| form_year | character varyi | YES | dol.v_dol_market_comparison.form_year | _undocumented_ |
| median_pepm_broker_cost | numeric | YES | dol.v_dol_market_comparison.median_pepm_broker_cos | _undocumented_ |
| size_band | text | YES | dol.v_dol_market_comparison.size_band | _undocumented_ |
| state | character varyi | YES | dol.v_dol_market_comparison.state | _undocumented_ |

### LEAF: dol.v_dol_premium_pressure (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_name | character varyi | YES | dol.v_dol_premium_pressure.company_name | _undocumented_ |
| company_unique_id | text | YES | dol.v_dol_premium_pressure.company_unique_id | _undocumented_ |
| current_participants | integer | YES | dol.v_dol_premium_pressure.current_participants | _undocumented_ |
| current_year | character varyi | YES | dol.v_dol_premium_pressure.current_year | _undocumented_ |
| ein | character varyi | YES | dol.v_dol_premium_pressure.ein | _undocumented_ |
| pct_change | numeric | YES | dol.v_dol_premium_pressure.pct_change | _undocumented_ |
| prior_participants | integer | YES | dol.v_dol_premium_pressure.prior_participants | _undocumented_ |
| prior_year | character varyi | YES | dol.v_dol_premium_pressure.prior_year | _undocumented_ |
| significant_decrease | boolean | YES | dol.v_dol_premium_pressure.significant_decrease | _undocumented_ |
| significant_increase | boolean | YES | dol.v_dol_premium_pressure.significant_increase | _undocumented_ |

### LEAF: dol.v_dol_renewal_window (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_name | character varyi | YES | dol.v_dol_renewal_window.company_name | _undocumented_ |
| company_unique_id | text | YES | dol.v_dol_renewal_window.company_unique_id | _undocumented_ |
| days_to_renewal | integer | YES | dol.v_dol_renewal_window.days_to_renewal | _undocumented_ |
| ein | character varyi | YES | dol.v_dol_renewal_window.ein | _undocumented_ |
| next_renewal_date | date | YES | dol.v_dol_renewal_window.next_renewal_date | _undocumented_ |
| plan_year_begin | date | YES | dol.v_dol_renewal_window.plan_year_begin | _undocumented_ |
| renewal_approaching | boolean | YES | dol.v_dol_renewal_window.renewal_approaching | _undocumented_ |

---

## BRANCH: enrichment (7 tables, 134 columns, 72% documented)

### LEAF: enrichment.column_registry (12 columns, 12 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ai_usage_hint | text | YES | enrichment.column_registry.ai_usage_hint | Ai Usage Hint |
| column_id | character varyi | NO | enrichment.column_registry.column_id | Column Id |
| column_name | character varyi | NO | enrichment.column_registry.column_name | Column Name |
| created_at | timestamp witho | YES | enrichment.column_registry.created_at | When this record was created |
| data_type | character varyi | NO | enrichment.column_registry.data_type | Data Type |
| description | text | NO | enrichment.column_registry.description | Description |
| example_value | text | YES | enrichment.column_registry.example_value | Example Value |
| format_pattern | character varyi | YES | enrichment.column_registry.format_pattern | Format Pattern |
| id | integer | NO | enrichment.column_registry.id | Id |
| is_pii | boolean | YES | enrichment.column_registry.is_pii | Whether this record pii |
| is_required | boolean | YES | enrichment.column_registry.is_required | Whether this record required |
| table_name | character varyi | NO | enrichment.column_registry.table_name | Table Name |

### LEAF: enrichment.hunter_company (26 columns, 26 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| city | character varyi | YES | HC_CITY | City name |
| company_embedding | USER-DEFINED | YES | HC_EMBEDDING | Semantic embedding for similarity search |
| company_type | character varyi | YES | HC_COMPANY_TYPE | Company ownership type |
| company_unique_id | character varyi | YES | HC_CT_ID | Link to company_target.company_unique_id |
| country | character varyi | YES | HC_COUNTRY | Two-letter country code |
| created_at | timestamp witho | YES | HC_CREATED_TS | Record creation timestamp |
| data_quality_score | numeric | YES | HC_QUALITY | Composite data completeness score |
| domain | character varyi | NO | HC_DOMAIN | Company website domain - primary identifier |
| email_pattern | character varyi | YES | HC_EMAIL_PATTERN | Email pattern for generating addresses |
| enriched_at | timestamp witho | YES | HC_ENRICHED_TS | When Hunter data was fetched |
| headcount | character varyi | YES | HC_HEADCOUNT_RAW | Employee count range as string |
| headcount_max | integer | YES | HC_HEADCOUNT_MAX | Maximum employee count from range |
| headcount_min | integer | YES | HC_HEADCOUNT_MIN | Minimum employee count from range |
| id | integer | NO | HC_ID | Primary key, auto-generated sequential ID |
| industry | character varyi | YES | HC_INDUSTRY | Industry classification from Hunter |
| industry_normalized | character varyi | YES | HC_INDUSTRY_NORM | Cleaned/mapped industry category |
| location_full | text | YES | HC_LOCATION_FULL | Full address string for display |
| organization | character varyi | YES | HC_ORG_NAME | Legal or common company name from Hunter |
| outreach_id | uuid | YES | HC_OUTREACH_ID | Link to outreach.outreach.outreach_id |
| postal_code | character varyi | YES | HC_POSTAL | ZIP or postal code |
| source | character varyi | YES | HC_SOURCE | Data source system |
| source_file | character varyi | YES | enrichment.hunter_company.source_file | Source File |
| state | character varyi | YES | HC_STATE | State/province/region |
| street | character varyi | YES | HC_STREET | Street address line |
| tags | ARRAY | YES | HC_TAGS | Custom classification tags |
| updated_at | timestamp witho | YES | HC_UPDATED_TS | Last update timestamp |

### LEAF: enrichment.hunter_contact (59 columns, 59 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | character varyi | YES | HCT_CT_ID | Link to company_target.company_unique_id |
| confidence_score | integer | YES | HCT_CONFIDENCE | Hunter email confidence score |
| contact_embedding | USER-DEFINED | YES | HCT_EMBEDDING | Semantic embedding for similarity search |
| created_at | timestamp witho | YES | HCT_CREATED_TS | Record creation timestamp |
| data_quality_score | numeric | YES | HCT_QUALITY | Composite data completeness score |
| department | character varyi | YES | HCT_DEPT_RAW | Department from Hunter |
| department_normalized | character varyi | YES | HCT_DEPT_NORM | Normalized department |
| domain | character varyi | NO | HCT_DOMAIN | Company domain this contact belongs to |
| email | character varyi | YES | HCT_EMAIL | Verified email address from Hunter |
| email_type | character varyi | YES | HCT_EMAIL_TYPE | Whether email is personal or generic |
| email_verified | boolean | YES | HCT_EMAIL_VERIFIED | Hunter verification status |
| first_name | character varyi | YES | HCT_FIRST_NAME | Contact first name |
| full_name | character varyi | YES | HCT_FULL_NAME | Combined full name |
| id | integer | NO | HCT_ID | Primary key, auto-generated sequential ID |
| is_decision_maker | boolean | YES | HCT_IS_DM | Whether contact is a decision maker |
| job_title | character varyi | YES | HCT_TITLE_RAW | Job title from Hunter |
| last_name | character varyi | YES | HCT_LAST_NAME | Contact last name |
| linkedin_url | character varyi | YES | HCT_LINKEDIN | LinkedIn profile URL |
| num_sources | integer | YES | HCT_NUM_SOURCES | Number of sources confirming this email |
| outreach_id | uuid | YES | HCT_OUTREACH_ID | Link to outreach.outreach.outreach_id |
| outreach_priority | integer | YES | HCT_PRIORITY | Computed outreach priority |
| phone_number | character varyi | YES | HCT_PHONE | Phone number if available |
| position_raw | character varyi | YES | HCT_POSITION_RAW | Full position description from source |
| seniority_level | character varyi | YES | HCT_SENIORITY | Seniority classification |
| source | character varyi | YES | HCT_SOURCE | Data source system |
| source_1 | text | YES | enrichment.hunter_contact.source_1 | Source 1 |
| source_10 | text | YES | enrichment.hunter_contact.source_10 | Source 10 |
| source_11 | text | YES | enrichment.hunter_contact.source_11 | Source 11 |
| source_12 | text | YES | enrichment.hunter_contact.source_12 | Source 12 |
| source_13 | text | YES | enrichment.hunter_contact.source_13 | Source 13 |
| source_14 | text | YES | enrichment.hunter_contact.source_14 | Source 14 |
| source_15 | text | YES | enrichment.hunter_contact.source_15 | Source 15 |
| source_16 | text | YES | enrichment.hunter_contact.source_16 | Source 16 |
| source_17 | text | YES | enrichment.hunter_contact.source_17 | Source 17 |
| source_18 | text | YES | enrichment.hunter_contact.source_18 | Source 18 |
| source_19 | text | YES | enrichment.hunter_contact.source_19 | Source 19 |
| source_2 | text | YES | enrichment.hunter_contact.source_2 | Source 2 |
| source_20 | text | YES | enrichment.hunter_contact.source_20 | Source 20 |
| source_21 | text | YES | enrichment.hunter_contact.source_21 | Source 21 |
| source_22 | text | YES | enrichment.hunter_contact.source_22 | Source 22 |
| source_23 | text | YES | enrichment.hunter_contact.source_23 | Source 23 |
| source_24 | text | YES | enrichment.hunter_contact.source_24 | Source 24 |
| source_25 | text | YES | enrichment.hunter_contact.source_25 | Source 25 |
| source_26 | text | YES | enrichment.hunter_contact.source_26 | Source 26 |
| source_27 | text | YES | enrichment.hunter_contact.source_27 | Source 27 |
| source_28 | text | YES | enrichment.hunter_contact.source_28 | Source 28 |
| source_29 | text | YES | enrichment.hunter_contact.source_29 | Source 29 |
| source_3 | text | YES | enrichment.hunter_contact.source_3 | Source 3 |
| source_30 | text | YES | enrichment.hunter_contact.source_30 | Source 30 |
| source_4 | text | YES | enrichment.hunter_contact.source_4 | Source 4 |
| source_5 | text | YES | enrichment.hunter_contact.source_5 | Source 5 |
| source_6 | text | YES | enrichment.hunter_contact.source_6 | Source 6 |
| source_7 | text | YES | enrichment.hunter_contact.source_7 | Source 7 |
| source_8 | text | YES | enrichment.hunter_contact.source_8 | Source 8 |
| source_9 | text | YES | enrichment.hunter_contact.source_9 | Source 9 |
| source_file | character varyi | YES | enrichment.hunter_contact.source_file | Source File |
| tags | ARRAY | YES | HCT_TAGS | Custom classification tags |
| title_normalized | character varyi | YES | HCT_TITLE_NORM | Normalized job title |
| twitter_handle | character varyi | YES | HCT_TWITTER | Twitter/X handle |

### LEAF: enrichment.v_column_metadata (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| ai_usage_hint | text | YES | enrichment.v_column_metadata.ai_usage_hint | _undocumented_ |
| column_id | character varyi | YES | enrichment.v_column_metadata.column_id | _undocumented_ |
| column_name | character varyi | YES | enrichment.v_column_metadata.column_name | _undocumented_ |
| data_type | character varyi | YES | enrichment.v_column_metadata.data_type | _undocumented_ |
| description | text | YES | enrichment.v_column_metadata.description | _undocumented_ |
| example_value | text | YES | enrichment.v_column_metadata.example_value | _undocumented_ |
| field_status | text | YES | enrichment.v_column_metadata.field_status | _undocumented_ |
| format_pattern | character varyi | YES | enrichment.v_column_metadata.format_pattern | _undocumented_ |
| is_pii | boolean | YES | enrichment.v_column_metadata.is_pii | _undocumented_ |
| is_required | boolean | YES | enrichment.v_column_metadata.is_required | _undocumented_ |
| table_name | character varyi | YES | enrichment.v_column_metadata.table_name | _undocumented_ |

### LEAF: enrichment.v_hunter_company_sources (5 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| domain | character varyi | YES | enrichment.v_hunter_company_sources.domain | _undocumented_ |
| organization | character varyi | YES | enrichment.v_hunter_company_sources.organization | _undocumented_ |
| outreach_id | uuid | YES | enrichment.v_hunter_company_sources.outreach_id | _undocumented_ |
| source_type | text | YES | enrichment.v_hunter_company_sources.source_type | _undocumented_ |
| source_url | text | YES | enrichment.v_hunter_company_sources.source_url | _undocumented_ |

### LEAF: enrichment.v_hunter_contact_sources (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| contact_id | integer | YES | enrichment.v_hunter_contact_sources.contact_id | _undocumented_ |
| domain | character varyi | YES | enrichment.v_hunter_contact_sources.domain | _undocumented_ |
| email | character varyi | YES | enrichment.v_hunter_contact_sources.email | _undocumented_ |
| first_name | character varyi | YES | enrichment.v_hunter_contact_sources.first_name | _undocumented_ |
| job_title | character varyi | YES | enrichment.v_hunter_contact_sources.job_title | _undocumented_ |
| last_name | character varyi | YES | enrichment.v_hunter_contact_sources.last_name | _undocumented_ |
| linkedin_url | character varyi | YES | enrichment.v_hunter_contact_sources.linkedin_url | _undocumented_ |
| outreach_id | uuid | YES | enrichment.v_hunter_contact_sources.outreach_id | _undocumented_ |
| source_order | integer | YES | enrichment.v_hunter_contact_sources.source_order | _undocumented_ |
| source_url | text | YES | enrichment.v_hunter_contact_sources.source_url | _undocumented_ |

### LEAF: enrichment.v_hunter_sources_by_type (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| contact_id | integer | YES | enrichment.v_hunter_sources_by_type.contact_id | _undocumented_ |
| domain | character varyi | YES | enrichment.v_hunter_sources_by_type.domain | _undocumented_ |
| email | character varyi | YES | enrichment.v_hunter_sources_by_type.email | _undocumented_ |
| first_name | character varyi | YES | enrichment.v_hunter_sources_by_type.first_name | _undocumented_ |
| job_title | character varyi | YES | enrichment.v_hunter_sources_by_type.job_title | _undocumented_ |
| last_name | character varyi | YES | enrichment.v_hunter_sources_by_type.last_name | _undocumented_ |
| linkedin_url | character varyi | YES | enrichment.v_hunter_sources_by_type.linkedin_url | _undocumented_ |
| outreach_id | uuid | YES | enrichment.v_hunter_sources_by_type.outreach_id | _undocumented_ |
| source_order | integer | YES | enrichment.v_hunter_sources_by_type.source_order | _undocumented_ |
| source_type | text | YES | enrichment.v_hunter_sources_by_type.source_type | _undocumented_ |
| source_url | text | YES | enrichment.v_hunter_sources_by_type.source_url | _undocumented_ |

---

## BRANCH: field_monitor (5 tables, 42 columns, 0% documented)

### LEAF: field_monitor.check_log (9 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| changed | boolean | NO | field_monitor.check_log.changed | _undocumented_ |
| checked_at | timestamp with  | NO | field_monitor.check_log.checked_at | _undocumented_ |
| fetch_duration_ms | integer | NO | field_monitor.check_log.fetch_duration_ms | _undocumented_ |
| field_name | text | NO | field_monitor.check_log.field_name | _undocumented_ |
| log_id | uuid | NO | field_monitor.check_log.log_id | _undocumented_ |
| new_value | text | YES | field_monitor.check_log.new_value | _undocumented_ |
| old_value | text | YES | field_monitor.check_log.old_value | _undocumented_ |
| parse_duration_ms | integer | NO | field_monitor.check_log.parse_duration_ms | _undocumented_ |
| url_id | uuid | NO | field_monitor.check_log.url_id | _undocumented_ |

### LEAF: field_monitor.error_log (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| error_id | uuid | NO | field_monitor.error_log.error_id | _undocumented_ |
| error_message | text | NO | field_monitor.error_log.error_message | _undocumented_ |
| error_type | text | NO | field_monitor.error_log.error_type | _undocumented_ |
| field_name | text | YES | field_monitor.error_log.field_name | _undocumented_ |
| occurred_at | timestamp with  | NO | field_monitor.error_log.occurred_at | _undocumented_ |
| resolved_at | timestamp with  | YES | field_monitor.error_log.resolved_at | _undocumented_ |
| url_id | uuid | NO | field_monitor.error_log.url_id | _undocumented_ |

### LEAF: field_monitor.field_state (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | field_monitor.field_state.created_at | _undocumented_ |
| current_value | text | YES | field_monitor.field_state.current_value | _undocumented_ |
| field_id | uuid | NO | field_monitor.field_state.field_id | _undocumented_ |
| field_name | text | NO | field_monitor.field_state.field_name | _undocumented_ |
| last_changed_at | timestamp with  | YES | field_monitor.field_state.last_changed_at | _undocumented_ |
| last_checked_at | timestamp with  | YES | field_monitor.field_state.last_checked_at | _undocumented_ |
| previous_value | text | YES | field_monitor.field_state.previous_value | _undocumented_ |
| promotion_status | text | NO | field_monitor.field_state.promotion_status | _undocumented_ |
| status | text | NO | field_monitor.field_state.status | _undocumented_ |
| updated_at | timestamp with  | NO | field_monitor.field_state.updated_at | _undocumented_ |
| url_id | uuid | NO | field_monitor.field_state.url_id | _undocumented_ |

### LEAF: field_monitor.rate_state (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | field_monitor.rate_state.created_at | _undocumented_ |
| domain | text | NO | field_monitor.rate_state.domain | _undocumented_ |
| max_requests | integer | NO | field_monitor.rate_state.max_requests | _undocumented_ |
| rate_id | uuid | NO | field_monitor.rate_state.rate_id | _undocumented_ |
| request_count | integer | NO | field_monitor.rate_state.request_count | _undocumented_ |
| updated_at | timestamp with  | NO | field_monitor.rate_state.updated_at | _undocumented_ |
| window_end | timestamp with  | NO | field_monitor.rate_state.window_end | _undocumented_ |
| window_start | timestamp with  | NO | field_monitor.rate_state.window_start | _undocumented_ |

### LEAF: field_monitor.url_registry (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| check_interval_minutes | integer | NO | field_monitor.url_registry.check_interval_minutes | _undocumented_ |
| created_at | timestamp with  | NO | field_monitor.url_registry.created_at | _undocumented_ |
| domain | text | NO | field_monitor.url_registry.domain | _undocumented_ |
| is_active | boolean | NO | field_monitor.url_registry.is_active | _undocumented_ |
| path | text | NO | field_monitor.url_registry.path | _undocumented_ |
| updated_at | timestamp with  | NO | field_monitor.url_registry.updated_at | _undocumented_ |
| url_id | uuid | NO | field_monitor.url_registry.url_id | _undocumented_ |

---

## BRANCH: intake (5 tables, 115 columns, 100% documented)

### LEAF: intake.company_raw_intake (35 columns, 35 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| apollo_id | character varyi | YES | intake.company_raw_intake.apollo_id | Apollo Id |
| b2_file_path | text | YES | intake.company_raw_intake.b2_file_path | B2 File Path |
| b2_uploaded_at | timestamp witho | YES | intake.company_raw_intake.b2_uploaded_at | Timestamp for b2 uploaded event |
| chronic_bad | boolean | YES | intake.company_raw_intake.chronic_bad | Chronic Bad |
| company | text | NO | intake.company_raw_intake.company | Company |
| company_address | text | YES | intake.company_raw_intake.company_address | Address |
| company_city | text | YES | intake.company_raw_intake.company_city | Company City |
| company_country | text | YES | intake.company_raw_intake.company_country | Company Country |
| company_linkedin_url | text | YES | intake.company_raw_intake.company_linkedin_url | Company Linkedin URL |
| company_name_for_emails | text | YES | intake.company_raw_intake.company_name_for_emails | Company Name For Emails |
| company_phone | text | YES | intake.company_raw_intake.company_phone | Company Phone |
| company_postal_code | text | YES | intake.company_raw_intake.company_postal_code | Company Postal Code |
| company_state | text | YES | intake.company_raw_intake.company_state | Company State |
| company_street | text | YES | intake.company_raw_intake.company_street | Company Street |
| created_at | timestamp with  | YES | intake.company_raw_intake.created_at | When this record was created |
| enriched_by | character varyi | YES | intake.company_raw_intake.enriched_by | Enriched By |
| enrichment_attempt | integer | YES | intake.company_raw_intake.enrichment_attempt | Enrichment Attempt |
| facebook_url | text | YES | intake.company_raw_intake.facebook_url | Facebook URL |
| founded_year | integer | YES | intake.company_raw_intake.founded_year | Founded Year |
| garage_bay | character varyi | YES | intake.company_raw_intake.garage_bay | Garage Bay |
| id | bigint | NO | intake.company_raw_intake.id | Id |
| import_batch_id | text | YES | intake.company_raw_intake.import_batch_id | Import Batch Id |
| industry | text | YES | intake.company_raw_intake.industry | Industry |
| last_enriched_at | timestamp witho | YES | intake.company_raw_intake.last_enriched_at | Timestamp for last enriched event |
| last_hash | character varyi | YES | intake.company_raw_intake.last_hash | Last Hash |
| num_employees | integer | YES | intake.company_raw_intake.num_employees | Num Employees |
| sic_codes | text | YES | intake.company_raw_intake.sic_codes | Sic Codes |
| state_abbrev | text | YES | intake.company_raw_intake.state_abbrev | State Abbrev |
| twitter_url | text | YES | intake.company_raw_intake.twitter_url | Twitter URL |
| validated | boolean | YES | intake.company_raw_intake.validated | Validated |
| validated_at | timestamp with  | YES | intake.company_raw_intake.validated_at | Timestamp for validated event |
| validated_by | text | YES | intake.company_raw_intake.validated_by | Validated By |
| validation_notes | text | YES | intake.company_raw_intake.validation_notes | Validation Notes |
| validation_reasons | text | YES | intake.company_raw_intake.validation_reasons | Validation Reasons |
| website | text | YES | intake.company_raw_intake.website | Website |

### LEAF: intake.company_raw_wv (12 columns, 12 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| address | text | YES | intake.company_raw_wv.address | Mailing address |
| city | text | YES | intake.company_raw_wv.city | City name |
| company_name | text | YES | intake.company_raw_wv.company_name | Company legal or common name |
| company_unique_id | text | NO | intake.company_raw_wv.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp witho | YES | intake.company_raw_wv.created_at | When this record was created |
| domain | text | YES | intake.company_raw_wv.domain | Company website domain (lowercase, no protocol) |
| employee_count | integer | YES | intake.company_raw_wv.employee_count | Count of employee |
| industry | text | YES | intake.company_raw_wv.industry | Industry |
| phone | text | YES | intake.company_raw_wv.phone | Phone number (E.164 format preferred) |
| state | text | YES | intake.company_raw_wv.state | US state code (2-letter) |
| website | text | YES | intake.company_raw_wv.website | Website |
| zip | text | YES | intake.company_raw_wv.zip | ZIP/postal code (5-digit) |

### LEAF: intake.people_raw_intake (40 columns, 40 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| b2_file_path | text | YES | intake.people_raw_intake.b2_file_path | B2 File Path |
| b2_uploaded_at | timestamp witho | YES | intake.people_raw_intake.b2_uploaded_at | Timestamp for b2 uploaded event |
| backfill_source | character varyi | YES | intake.people_raw_intake.backfill_source | Backfill Source |
| bio | text | YES | intake.people_raw_intake.bio | Bio |
| certifications | text | YES | intake.people_raw_intake.certifications | Certifications |
| chronic_bad | boolean | YES | intake.people_raw_intake.chronic_bad | Chronic Bad |
| city | character varyi | YES | intake.people_raw_intake.city | City name |
| company_name | character varyi | YES | intake.people_raw_intake.company_name | Company legal or common name |
| company_unique_id | character varyi | YES | intake.people_raw_intake.company_unique_id | FK to cl.company_identity or Barton company ID |
| country | character varyi | YES | intake.people_raw_intake.country | Country name or code |
| created_at | timestamp witho | YES | intake.people_raw_intake.created_at | When this record was created |
| department | character varyi | YES | intake.people_raw_intake.department | Department |
| education | text | YES | intake.people_raw_intake.education | Education |
| email | character varyi | YES | intake.people_raw_intake.email | Email address |
| enriched_by | character varyi | YES | intake.people_raw_intake.enriched_by | Enriched By |
| enrichment_attempt | integer | YES | intake.people_raw_intake.enrichment_attempt | Enrichment Attempt |
| facebook_url | text | YES | intake.people_raw_intake.facebook_url | Facebook URL |
| first_name | character varyi | YES | intake.people_raw_intake.first_name | Person first name |
| full_name | character varyi | YES | intake.people_raw_intake.full_name | Full Name |
| id | integer | NO | intake.people_raw_intake.id | Id |
| import_batch_id | character varyi | YES | intake.people_raw_intake.import_batch_id | Import Batch Id |
| last_enriched_at | timestamp witho | YES | intake.people_raw_intake.last_enriched_at | Timestamp for last enriched event |
| last_name | character varyi | YES | intake.people_raw_intake.last_name | Person last name |
| linkedin_url | text | YES | intake.people_raw_intake.linkedin_url | LinkedIn profile URL |
| personal_phone | character varyi | YES | intake.people_raw_intake.personal_phone | Personal Phone |
| seniority | character varyi | YES | intake.people_raw_intake.seniority | Seniority |
| skills | ARRAY | YES | intake.people_raw_intake.skills | Skills |
| slot_type | character varyi | YES | intake.people_raw_intake.slot_type | Executive role type (CEO, CFO, HR, CTO, CMO, COO) |
| source_record_id | character varyi | YES | intake.people_raw_intake.source_record_id | Source Record Id |
| source_system | character varyi | YES | intake.people_raw_intake.source_system | System that originated this record |
| state | character varyi | YES | intake.people_raw_intake.state | US state code (2-letter) |
| state_abbrev | character varyi | YES | intake.people_raw_intake.state_abbrev | State Abbrev |
| title | character varyi | YES | intake.people_raw_intake.title | Job title or position |
| twitter_url | text | YES | intake.people_raw_intake.twitter_url | Twitter URL |
| updated_at | timestamp witho | YES | intake.people_raw_intake.updated_at | When this record was last updated |
| validated | boolean | YES | intake.people_raw_intake.validated | Validated |
| validated_at | timestamp witho | YES | intake.people_raw_intake.validated_at | Timestamp for validated event |
| validated_by | character varyi | YES | intake.people_raw_intake.validated_by | Validated By |
| validation_notes | text | YES | intake.people_raw_intake.validation_notes | Validation Notes |
| work_phone | character varyi | YES | intake.people_raw_intake.work_phone | Work Phone |

### LEAF: intake.people_raw_wv (13 columns, 13 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| city | text | YES | intake.people_raw_wv.city | City name |
| company_name | text | YES | intake.people_raw_wv.company_name | Company legal or common name |
| company_unique_id | text | YES | intake.people_raw_wv.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp witho | YES | intake.people_raw_wv.created_at | When this record was created |
| email | text | YES | intake.people_raw_wv.email | Email address |
| first_name | text | YES | intake.people_raw_wv.first_name | Person first name |
| full_name | text | YES | intake.people_raw_wv.full_name | Full Name |
| last_name | text | YES | intake.people_raw_wv.last_name | Person last name |
| linkedin_url | text | YES | intake.people_raw_wv.linkedin_url | LinkedIn profile URL |
| phone | text | YES | intake.people_raw_wv.phone | Phone number (E.164 format preferred) |
| state | text | YES | intake.people_raw_wv.state | US state code (2-letter) |
| title | text | YES | intake.people_raw_wv.title | Job title or position |
| unique_id | text | NO | intake.people_raw_wv.unique_id | Primary identifier for this record (Barton ID format) |

### LEAF: intake.people_staging (15 columns, 15 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | NO | intake.people_staging.company_unique_id | FK to cl.company_identity or Barton company ID |
| confidence_score | numeric | YES | intake.people_staging.confidence_score | Confidence score (0-100) |
| created_at | timestamp witho | YES | intake.people_staging.created_at | When this record was created |
| email | character varyi | YES | intake.people_staging.email | Email address |
| first_name | character varyi | YES | intake.people_staging.first_name | Person first name |
| id | integer | NO | intake.people_staging.id | Id |
| last_name | character varyi | YES | intake.people_staging.last_name | Person last name |
| linkedin_url | character varyi | YES | intake.people_staging.linkedin_url | LinkedIn profile URL |
| mapped_slot_type | character varyi | YES | intake.people_staging.mapped_slot_type | Mapped Slot Type |
| normalized_title | character varyi | YES | intake.people_staging.normalized_title | Normalized Title |
| processed_at | timestamp witho | YES | intake.people_staging.processed_at | Timestamp for processed event |
| raw_name | text | YES | intake.people_staging.raw_name | Raw Name |
| raw_title | text | YES | intake.people_staging.raw_title | Raw Title |
| source_url_id | uuid | YES | intake.people_staging.source_url_id | Source Url Id |
| status | character varyi | YES | intake.people_staging.status | Current status of this record |

---

## BRANCH: lcs (3 tables, 36 columns, 0% documented)

### LEAF: lcs.message_error (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| cid | text | YES | lcs.message_error.cid | _undocumented_ |
| created_at | timestamp with  | NO | lcs.message_error.created_at | _undocumented_ |
| error_code | text | NO | lcs.message_error.error_code | _undocumented_ |
| error_id | uuid | NO | lcs.message_error.error_id | _undocumented_ |
| lcs_id | uuid | YES | lcs.message_error.lcs_id | _undocumented_ |
| payload | jsonb | YES | lcs.message_error.payload | _undocumented_ |
| source_stage | text | NO | lcs.message_error.source_stage | _undocumented_ |
| sovereign_id | uuid | NO | lcs.message_error.sovereign_id | _undocumented_ |

### LEAF: lcs.message_ledger (18 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| attempt_number | integer | NO | lcs.message_ledger.attempt_number | _undocumented_ |
| channel | text | NO | lcs.message_ledger.channel | _undocumented_ |
| cid | text | NO | lcs.message_ledger.cid | _undocumented_ |
| created_at | timestamp with  | NO | lcs.message_ledger.created_at | _undocumented_ |
| last_error_at | timestamp with  | YES | lcs.message_ledger.last_error_at | _undocumented_ |
| lcs_id | uuid | NO | lcs.message_ledger.lcs_id | _undocumented_ |
| mid | uuid | NO | lcs.message_ledger.mid | _undocumented_ |
| payload_hash | text | NO | lcs.message_ledger.payload_hash | _undocumented_ |
| provider | text | NO | lcs.message_ledger.provider | _undocumented_ |
| provider_message_id | text | YES | lcs.message_ledger.provider_message_id | _undocumented_ |
| ready_at | timestamp with  | YES | lcs.message_ledger.ready_at | _undocumented_ |
| sender_profile_id | uuid | NO | lcs.message_ledger.sender_profile_id | _undocumented_ |
| sent_at | timestamp with  | YES | lcs.message_ledger.sent_at | _undocumented_ |
| source_cid_table | text | NO | lcs.message_ledger.source_cid_table | _undocumented_ |
| source_stage | text | NO | lcs.message_ledger.source_stage | _undocumented_ |
| sovereign_id | uuid | NO | lcs.message_ledger.sovereign_id | _undocumented_ |
| status | text | NO | lcs.message_ledger.status | _undocumented_ |
| updated_at | timestamp with  | NO | lcs.message_ledger.updated_at | _undocumented_ |

### LEAF: lcs.sender_profile_registry (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| channel | text | NO | lcs.sender_profile_registry.channel | _undocumented_ |
| created_at | timestamp with  | NO | lcs.sender_profile_registry.created_at | _undocumented_ |
| display_name | text | YES | lcs.sender_profile_registry.display_name | _undocumented_ |
| from_address | text | YES | lcs.sender_profile_registry.from_address | _undocumented_ |
| is_active | boolean | NO | lcs.sender_profile_registry.is_active | _undocumented_ |
| provider | text | NO | lcs.sender_profile_registry.provider | _undocumented_ |
| reply_to_address | text | YES | lcs.sender_profile_registry.reply_to_address | _undocumented_ |
| sender_profile_id | uuid | NO | lcs.sender_profile_registry.sender_profile_id | _undocumented_ |
| stage | text | NO | lcs.sender_profile_registry.stage | _undocumented_ |
| updated_at | timestamp with  | NO | lcs.sender_profile_registry.updated_at | _undocumented_ |

---

## BRANCH: marketing (6 tables, 33 columns, 0% documented)

### LEAF: marketing.marketing_ceo (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_id | uuid | YES | marketing.marketing_ceo.company_id | _undocumented_ |
| created_at | timestamp witho | YES | marketing.marketing_ceo.created_at | _undocumented_ |
| email | text | YES | marketing.marketing_ceo.email | _undocumented_ |
| external_id | text | YES | marketing.marketing_ceo.external_id | _undocumented_ |
| full_name | text | YES | marketing.marketing_ceo.full_name | _undocumented_ |
| id | uuid | YES | marketing.marketing_ceo.id | _undocumented_ |
| persona_type | text | YES | marketing.marketing_ceo.persona_type | _undocumented_ |
| title | text | YES | marketing.marketing_ceo.title | _undocumented_ |

### LEAF: marketing.marketing_cfo (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_id | uuid | YES | marketing.marketing_cfo.company_id | _undocumented_ |
| created_at | timestamp witho | YES | marketing.marketing_cfo.created_at | _undocumented_ |
| email | text | YES | marketing.marketing_cfo.email | _undocumented_ |
| external_id | text | YES | marketing.marketing_cfo.external_id | _undocumented_ |
| full_name | text | YES | marketing.marketing_cfo.full_name | _undocumented_ |
| id | uuid | YES | marketing.marketing_cfo.id | _undocumented_ |
| persona_type | text | YES | marketing.marketing_cfo.persona_type | _undocumented_ |
| title | text | YES | marketing.marketing_cfo.title | _undocumented_ |

### LEAF: marketing.marketing_hr (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_id | uuid | YES | marketing.marketing_hr.company_id | _undocumented_ |
| created_at | timestamp witho | YES | marketing.marketing_hr.created_at | _undocumented_ |
| email | text | YES | marketing.marketing_hr.email | _undocumented_ |
| external_id | text | YES | marketing.marketing_hr.external_id | _undocumented_ |
| full_name | text | YES | marketing.marketing_hr.full_name | _undocumented_ |
| id | uuid | YES | marketing.marketing_hr.id | _undocumented_ |
| persona_type | text | YES | marketing.marketing_hr.persona_type | _undocumented_ |
| title | text | YES | marketing.marketing_hr.title | _undocumented_ |

### LEAF: marketing.vw_health_crawl_staleness (3 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| companies_never_checked | bigint | YES | marketing.vw_health_crawl_staleness.companies_neve | _undocumented_ |
| companies_stale_30d | bigint | YES | marketing.vw_health_crawl_staleness.companies_stal | _undocumented_ |
| companies_total | bigint | YES | marketing.vw_health_crawl_staleness.companies_tota | _undocumented_ |

### LEAF: marketing.vw_health_profile_staleness (3 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| contacts_never_checked | bigint | YES | marketing.vw_health_profile_staleness.contacts_nev | _undocumented_ |
| contacts_stale_30d | bigint | YES | marketing.vw_health_profile_staleness.contacts_sta | _undocumented_ |
| contacts_total | bigint | YES | marketing.vw_health_profile_staleness.contacts_tot | _undocumented_ |

### LEAF: marketing.vw_queue_sizes (3 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| due_company_urls | bigint | YES | marketing.vw_queue_sizes.due_company_urls | _undocumented_ |
| due_email_rechecks | bigint | YES | marketing.vw_queue_sizes.due_email_rechecks | _undocumented_ |
| due_profile_urls | bigint | YES | marketing.vw_queue_sizes.due_profile_urls | _undocumented_ |

---

## BRANCH: outreach (38 tables, 576 columns, 85% documented)

### LEAF: outreach.appointments (22 columns, 22 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| address_1 | character varyi | YES | outreach.appointments.address_1 | Address 1 |
| address_2 | character varyi | YES | outreach.appointments.address_2 | Address 2 |
| appointment_id | uuid | NO | outreach.appointments.appointment_id | Appointment Id |
| appt_date | date | YES | outreach.appointments.appt_date | Appt Date |
| appt_number | character varyi | YES | outreach.appointments.appt_number | Appt Number |
| city | character varyi | YES | outreach.appointments.city | City name |
| company_name | character varyi | NO | outreach.appointments.company_name | Company legal or common name |
| contact_email | character varyi | YES | outreach.appointments.contact_email | Contact Email |
| contact_first_name | character varyi | YES | outreach.appointments.contact_first_name | Contact First Name |
| contact_last_name | character varyi | YES | outreach.appointments.contact_last_name | Contact Last Name |
| contact_phone | character varyi | YES | outreach.appointments.contact_phone | Contact Phone |
| contact_title | character varyi | YES | outreach.appointments.contact_title | Contact Title |
| county | character varyi | YES | outreach.appointments.county | County |
| created_at | timestamp with  | YES | outreach.appointments.created_at | When this record was created |
| domain | character varyi | YES | outreach.appointments.domain | Company website domain (lowercase, no protocol) |
| notes | text | YES | outreach.appointments.notes | Human-readable notes |
| outreach_id | uuid | YES | outreach.appointments.outreach_id | FK to outreach.outreach spine table (universal join key) |
| prospect_keycode_id | bigint | YES | outreach.appointments.prospect_keycode_id | Prospect Keycode Id |
| source_file | character varyi | YES | outreach.appointments.source_file | Source File |
| state | character varyi | YES | outreach.appointments.state | US state code (2-letter) |
| updated_at | timestamp with  | YES | outreach.appointments.updated_at | When this record was last updated |
| zip | character varyi | YES | outreach.appointments.zip | ZIP/postal code (5-digit) |

### LEAF: outreach.bit_errors (13 columns, 13 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| blocking_reason | text | NO | outreach.bit_errors.blocking_reason | Blocking Reason |
| correlation_id | uuid | YES | outreach.bit_errors.correlation_id | UUID linking related operations across tables |
| created_at | timestamp with  | NO | outreach.bit_errors.created_at | When the error was recorded |
| error_id | uuid | NO | outreach.bit_errors.error_id | Primary key for error record |
| error_type | character varyi | YES | outreach.bit_errors.error_type | Discriminator column — classifies the scoring error |
| failure_code | character varyi | NO | outreach.bit_errors.failure_code | Failure Code |
| outreach_id | uuid | YES | outreach.bit_errors.outreach_id | FK to spine (nullable — error may occur before entity exists) |
| pipeline_stage | character varyi | NO | outreach.bit_errors.pipeline_stage | Pipeline Stage |
| process_id | uuid | YES | outreach.bit_errors.process_id | Process Id |
| raw_input | jsonb | YES | outreach.bit_errors.raw_input | Raw Input |
| retry_allowed | boolean | NO | outreach.bit_errors.retry_allowed | Retry Allowed |
| severity | character varyi | NO | outreach.bit_errors.severity | Severity |
| stack_trace | text | YES | outreach.bit_errors.stack_trace | Stack Trace |

### LEAF: outreach.bit_scores (12 columns, 12 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| blog_score | numeric | NO | outreach.bit_scores.blog_score | Blog score |
| created_at | timestamp with  | NO | outreach.bit_scores.created_at | When this record was created |
| dol_score | numeric | NO | outreach.bit_scores.dol_score | Dol score |
| last_scored_at | timestamp with  | YES | outreach.bit_scores.last_scored_at | Timestamp for last scored event |
| last_signal_at | timestamp with  | YES | outreach.bit_scores.last_signal_at | Timestamp for last signal event |
| outreach_id | uuid | NO | outreach.bit_scores.outreach_id | FK to outreach.outreach spine table |
| people_score | numeric | NO | outreach.bit_scores.people_score | People score |
| score | numeric | NO | outreach.bit_scores.score | Score |
| score_tier | character varyi | NO | outreach.bit_scores.score_tier | Score Tier |
| signal_count | integer | NO | outreach.bit_scores.signal_count | Count of signal |
| talent_flow_score | numeric | NO | outreach.bit_scores.talent_flow_score | Talent Flow score |
| updated_at | timestamp with  | NO | outreach.bit_scores.updated_at | When this record was last updated |

### LEAF: outreach.bit_scores_archive (14 columns, 14 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | outreach.bit_scores_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | outreach.bit_scores_archive.archived_at | When this record was archived |
| blog_score | numeric | NO | outreach.bit_scores_archive.blog_score | Blog score |
| created_at | timestamp with  | NO | outreach.bit_scores_archive.created_at | When this record was created |
| dol_score | numeric | NO | outreach.bit_scores_archive.dol_score | Dol score |
| last_scored_at | timestamp with  | YES | outreach.bit_scores_archive.last_scored_at | Timestamp for last scored event |
| last_signal_at | timestamp with  | YES | outreach.bit_scores_archive.last_signal_at | Timestamp for last signal event |
| outreach_id | uuid | NO | outreach.bit_scores_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| people_score | numeric | NO | outreach.bit_scores_archive.people_score | People score |
| score | numeric | NO | outreach.bit_scores_archive.score | Score |
| score_tier | character varyi | NO | outreach.bit_scores_archive.score_tier | Score Tier |
| signal_count | integer | NO | outreach.bit_scores_archive.signal_count | Count of signal |
| talent_flow_score | numeric | NO | outreach.bit_scores_archive.talent_flow_score | Talent Flow score |
| updated_at | timestamp with  | NO | outreach.bit_scores_archive.updated_at | When this record was last updated |

### LEAF: outreach.blog (13 columns, 13 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| about_url | text | YES | outreach.blog.about_url | Company About Us page URL |
| blog_id | uuid | NO | outreach.blog.blog_id | Primary key for this blog record |
| context_summary | text | YES | outreach.blog.context_summary | Summary of blog/content context |
| context_timestamp | timestamp with  | YES | outreach.blog.context_timestamp | Context Timestamp |
| created_at | timestamp with  | YES | outreach.blog.created_at | When this record was created |
| extraction_method | text | YES | outreach.blog.extraction_method | Method used to extract content (sitemap, crawl, etc.) |
| last_extracted_at | timestamp with  | YES | outreach.blog.last_extracted_at | When data was last extracted/scraped |
| news_url | text | YES | outreach.blog.news_url | Company news/press page URL |
| outreach_id | uuid | NO | outreach.blog.outreach_id | FK to outreach.outreach spine table |
| source_type | text | YES | outreach.blog.source_type | Source Type |
| source_type_enum | USER-DEFINED | YES | outreach.blog.source_type_enum | Source Type Enum |
| source_url | text | YES | outreach.blog.source_url | URL of the content source |
| updated_at | timestamp with  | YES | outreach.blog.updated_at | When this record was last updated |

### LEAF: outreach.blog_archive (10 columns, 10 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | outreach.blog_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | outreach.blog_archive.archived_at | When this record was archived |
| blog_id | uuid | NO | outreach.blog_archive.blog_id | Primary key for this blog record |
| context_summary | text | YES | outreach.blog_archive.context_summary | Summary of blog/content context |
| context_timestamp | timestamp with  | YES | outreach.blog_archive.context_timestamp | Context Timestamp |
| created_at | timestamp with  | YES | outreach.blog_archive.created_at | When this record was created |
| outreach_id | uuid | NO | outreach.blog_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| source_type | text | YES | outreach.blog_archive.source_type | Source Type |
| source_type_enum | USER-DEFINED | YES | outreach.blog_archive.source_type_enum | Source Type Enum |
| source_url | text | YES | outreach.blog_archive.source_url | URL of the content source |

### LEAF: outreach.blog_errors (15 columns, 15 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| blocking_reason | text | NO | outreach.blog_errors.blocking_reason | Blocking Reason |
| created_at | timestamp with  | NO | outreach.blog_errors.created_at | When the error was recorded |
| error_id | uuid | NO | outreach.blog_errors.error_id | Primary key for error record |
| error_type | character varyi | NO | outreach.blog_errors.error_type | Discriminator column — classifies the blog error (e.g., BLOG_MISSING) |
| failure_code | character varyi | NO | outreach.blog_errors.failure_code | Failure Code |
| outreach_id | uuid | NO | outreach.blog_errors.outreach_id | FK to spine (nullable — error may occur before entity exists) |
| pipeline_stage | character varyi | NO | outreach.blog_errors.pipeline_stage | Pipeline Stage |
| process_id | uuid | YES | outreach.blog_errors.process_id | Process Id |
| raw_input | jsonb | YES | outreach.blog_errors.raw_input | Raw Input |
| requeue_attempts | integer | YES | outreach.blog_errors.requeue_attempts | Requeue Attempts |
| resolution_note | text | YES | outreach.blog_errors.resolution_note | Resolution Note |
| resolved_at | timestamp with  | YES | outreach.blog_errors.resolved_at | When this error/issue was resolved |
| retry_allowed | boolean | NO | outreach.blog_errors.retry_allowed | Retry Allowed |
| severity | character varyi | NO | outreach.blog_errors.severity | Severity |
| stack_trace | text | YES | outreach.blog_errors.stack_trace | Stack Trace |

### LEAF: outreach.blog_ingress_control (14 columns, 14 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| content_ttl_days | integer | YES | outreach.blog_ingress_control.content_ttl_days | Content Ttl Days |
| control_id | uuid | NO | outreach.blog_ingress_control.control_id | Control Id |
| created_at | timestamp with  | YES | outreach.blog_ingress_control.created_at | When this record was created |
| disabled_at | timestamp with  | YES | outreach.blog_ingress_control.disabled_at | Timestamp for disabled event |
| disabled_by | text | YES | outreach.blog_ingress_control.disabled_by | Disabled By |
| enabled | boolean | NO | outreach.blog_ingress_control.enabled | Enabled |
| enabled_at | timestamp with  | YES | outreach.blog_ingress_control.enabled_at | Timestamp for enabled event |
| enabled_by | text | YES | outreach.blog_ingress_control.enabled_by | Enabled By |
| max_urls_per_company | integer | YES | outreach.blog_ingress_control.max_urls_per_company | Max Urls Per Company |
| max_urls_per_hour | integer | YES | outreach.blog_ingress_control.max_urls_per_hour | Max Urls Per Hour |
| notes | text | YES | outreach.blog_ingress_control.notes | Human-readable notes |
| singleton_key | integer | YES | outreach.blog_ingress_control.singleton_key | Singleton Key |
| updated_at | timestamp with  | YES | outreach.blog_ingress_control.updated_at | When this record was last updated |
| url_ttl_days | integer | YES | outreach.blog_ingress_control.url_ttl_days | Url Ttl Days |

### LEAF: outreach.column_registry (12 columns, 12 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| column_description | text | NO | outreach.column_registry.column_description | Column Description |
| column_format | character varyi | NO | outreach.column_registry.column_format | Column Format |
| column_name | character varyi | NO | outreach.column_registry.column_name | Column Name |
| column_unique_id | character varyi | NO | outreach.column_registry.column_unique_id | Column Unique Id |
| created_at | timestamp with  | YES | outreach.column_registry.created_at | When this record was created |
| default_value | text | YES | outreach.column_registry.default_value | Default Value |
| fk_reference | text | YES | outreach.column_registry.fk_reference | Fk Reference |
| is_nullable | boolean | NO | outreach.column_registry.is_nullable | Whether this record nullable |
| registry_id | integer | NO | outreach.column_registry.registry_id | Registry Id |
| schema_name | character varyi | NO | outreach.column_registry.schema_name | Schema Name |
| table_name | character varyi | NO | outreach.column_registry.table_name | Table Name |
| updated_at | timestamp with  | YES | outreach.column_registry.updated_at | When this record was last updated |

### LEAF: outreach.company_hub_status (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | NO | outreach.company_hub_status.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | NO | outreach.company_hub_status.created_at | When this record was created |
| hub_id | character varyi | NO | outreach.company_hub_status.hub_id | Hub Id |
| last_processed_at | timestamp with  | YES | outreach.company_hub_status.last_processed_at | Timestamp for last processed event |
| metric_value | numeric | YES | outreach.company_hub_status.metric_value | Metric Value |
| status | USER-DEFINED | NO | outreach.company_hub_status.status | Current status of this record |
| status_reason | text | YES | outreach.company_hub_status.status_reason | Status Reason |
| updated_at | timestamp with  | NO | outreach.company_hub_status.updated_at | When this record was last updated |

### LEAF: outreach.company_target (27 columns, 27 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| active_sequence_id | text | YES | outreach.company_target.active_sequence_id | Current sequence ID |
| bit_score_snapshot | integer | YES | outreach.company_target.bit_score_snapshot | Cached BIT score at targeting (0-100) |
| city | character varyi | YES | outreach.company_target.city | City name |
| company_unique_id | text | YES | outreach.company_target.company_unique_id | FK to cl.company_identity - parent hub identity |
| confidence_score | numeric | YES | outreach.company_target.confidence_score | Confidence score (0-100) |
| country | character varyi | YES | outreach.company_target.country | Country name or code |
| created_at | timestamp with  | NO | outreach.company_target.created_at | Creation timestamp |
| data_year | integer | YES | outreach.company_target.data_year | Data Year |
| email_method | character varyi | YES | outreach.company_target.email_method | Email Method |
| employees | integer | YES | outreach.company_target.employees | Employees |
| execution_status | character varyi | YES | outreach.company_target.execution_status | Execution Status |
| first_targeted_at | timestamp with  | YES | outreach.company_target.first_targeted_at | First targeting timestamp |
| imo_completed_at | timestamp with  | YES | outreach.company_target.imo_completed_at | Timestamp for imo completed event |
| industry | character varyi | YES | outreach.company_target.industry | Industry |
| is_catchall | boolean | YES | outreach.company_target.is_catchall | Whether this record catchall |
| last_targeted_at | timestamp with  | YES | outreach.company_target.last_targeted_at | Most recent outreach timestamp |
| method_type | character varyi | YES | outreach.company_target.method_type | Method Type |
| outreach_id | uuid | YES | outreach.company_target.outreach_id | FK to outreach.outreach spine table |
| outreach_status | text | NO | outreach.company_target.outreach_status | Current outreach status |
| postal_code | character varyi | YES | outreach.company_target.postal_code | ZIP/postal code (5-digit) |
| postal_code_source | text | YES | outreach.company_target.postal_code_source | Postal Code Source |
| postal_code_updated_at | timestamp with  | YES | outreach.company_target.postal_code_updated_at | Timestamp for postal code updated event |
| sequence_count | integer | NO | outreach.company_target.sequence_count | Number of sequences completed |
| source | text | YES | outreach.company_target.source | Record origin |
| state | character varyi | YES | outreach.company_target.state | US state code (2-letter) |
| target_id | uuid | NO | outreach.company_target.target_id | UUID primary key for outreach company target record |
| updated_at | timestamp with  | NO | outreach.company_target.updated_at | Last update timestamp |

### LEAF: outreach.company_target_archive (20 columns, 20 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| active_sequence_id | text | YES | outreach.company_target_archive.active_sequence_id | Active Sequence Id |
| archive_reason | text | YES | outreach.company_target_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | outreach.company_target_archive.archived_at | When this record was archived |
| bit_score_snapshot | integer | YES | outreach.company_target_archive.bit_score_snapshot | Bit Score Snapshot |
| company_unique_id | text | YES | outreach.company_target_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| confidence_score | numeric | YES | outreach.company_target_archive.confidence_score | Confidence score (0-100) |
| created_at | timestamp with  | NO | outreach.company_target_archive.created_at | When this record was created |
| email_method | character varyi | YES | outreach.company_target_archive.email_method | Email Method |
| execution_status | character varyi | YES | outreach.company_target_archive.execution_status | Execution Status |
| first_targeted_at | timestamp with  | YES | outreach.company_target_archive.first_targeted_at | Timestamp for first targeted event |
| imo_completed_at | timestamp with  | YES | outreach.company_target_archive.imo_completed_at | Timestamp for imo completed event |
| is_catchall | boolean | YES | outreach.company_target_archive.is_catchall | Whether this record catchall |
| last_targeted_at | timestamp with  | YES | outreach.company_target_archive.last_targeted_at | Timestamp for last targeted event |
| method_type | character varyi | YES | outreach.company_target_archive.method_type | Method Type |
| outreach_id | uuid | YES | outreach.company_target_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| outreach_status | text | NO | outreach.company_target_archive.outreach_status | Outreach Status |
| sequence_count | integer | NO | outreach.company_target_archive.sequence_count | Count of sequence |
| source | text | YES | outreach.company_target_archive.source | Data source identifier |
| target_id | uuid | NO | outreach.company_target_archive.target_id | Primary key for this target record |
| updated_at | timestamp with  | NO | outreach.company_target_archive.updated_at | When this record was last updated |

### LEAF: outreach.company_target_errors (28 columns, 28 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archived_at | timestamp with  | YES | outreach.company_target_errors.archived_at | When this record was archived |
| blocking_reason | text | NO | outreach.company_target_errors.blocking_reason | Blocking Reason |
| created_at | timestamp with  | NO | outreach.company_target_errors.created_at | When the error was recorded |
| disposition | USER-DEFINED | YES | outreach.company_target_errors.disposition | Disposition |
| error_id | uuid | NO | outreach.company_target_errors.error_id | Primary key for error record |
| error_type | character varyi | YES | outreach.company_target_errors.error_type | Discriminator column — classifies the error |
| escalated_at | timestamp with  | YES | outreach.company_target_errors.escalated_at | Timestamp for escalated event |
| escalation_level | integer | YES | outreach.company_target_errors.escalation_level | Escalation Level |
| failure_code | character varyi | NO | outreach.company_target_errors.failure_code | Failure Code |
| imo_stage | character varyi | YES | outreach.company_target_errors.imo_stage | Imo Stage |
| last_retry_at | timestamp with  | YES | outreach.company_target_errors.last_retry_at | Timestamp for last retry event |
| max_retries | integer | YES | outreach.company_target_errors.max_retries | Max Retries |
| next_retry_at | timestamp with  | YES | outreach.company_target_errors.next_retry_at | Timestamp for next retry event |
| outreach_id | uuid | NO | outreach.company_target_errors.outreach_id | FK to spine (nullable — error may occur before entity exists) |
| park_reason | text | YES | outreach.company_target_errors.park_reason | Park Reason |
| parked_at | timestamp with  | YES | outreach.company_target_errors.parked_at | Timestamp for parked event |
| parked_by | text | YES | outreach.company_target_errors.parked_by | Parked By |
| pipeline_stage | character varyi | NO | outreach.company_target_errors.pipeline_stage | Pipeline Stage |
| raw_input | jsonb | YES | outreach.company_target_errors.raw_input | Raw Input |
| requeue_attempts | integer | YES | outreach.company_target_errors.requeue_attempts | Requeue Attempts |
| resolution_note | text | YES | outreach.company_target_errors.resolution_note | Resolution Note |
| resolved_at | timestamp with  | YES | outreach.company_target_errors.resolved_at | When this error/issue was resolved |
| retry_allowed | boolean | NO | outreach.company_target_errors.retry_allowed | Retry Allowed |
| retry_count | integer | YES | outreach.company_target_errors.retry_count | Number of retry attempts so far |
| retry_exhausted | boolean | YES | outreach.company_target_errors.retry_exhausted | Retry Exhausted |
| severity | character varyi | NO | outreach.company_target_errors.severity | Severity |
| stack_trace | text | YES | outreach.company_target_errors.stack_trace | Stack Trace |
| ttl_tier | USER-DEFINED | YES | outreach.company_target_errors.ttl_tier | Ttl Tier |

### LEAF: outreach.company_target_errors_archive (30 columns, 30 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | outreach.company_target_errors_archive.archive_rea | Reason this record was archived |
| archived_at | timestamp with  | NO | outreach.company_target_errors_archive.archived_at | When this record was archived |
| archived_by | text | YES | outreach.company_target_errors_archive.archived_by | Archived By |
| blocking_reason | text | YES | outreach.company_target_errors_archive.blocking_re | Blocking Reason |
| created_at | timestamp with  | YES | outreach.company_target_errors_archive.created_at | When this record was created |
| disposition | USER-DEFINED | YES | outreach.company_target_errors_archive.disposition | Disposition |
| error_id | uuid | NO | outreach.company_target_errors_archive.error_id | Primary key for this error record |
| error_type | character varyi | YES | outreach.company_target_errors_archive.error_type | Discriminator column classifying the error type |
| escalated_at | timestamp with  | YES | outreach.company_target_errors_archive.escalated_a | Timestamp for escalated event |
| escalation_level | integer | YES | outreach.company_target_errors_archive.escalation_ | Escalation Level |
| failure_code | character varyi | YES | outreach.company_target_errors_archive.failure_cod | Failure Code |
| final_disposition | USER-DEFINED | YES | outreach.company_target_errors_archive.final_dispo | Final Disposition |
| imo_stage | character varyi | YES | outreach.company_target_errors_archive.imo_stage | Imo Stage |
| last_retry_at | timestamp with  | YES | outreach.company_target_errors_archive.last_retry_ | Timestamp for last retry event |
| max_retries | integer | YES | outreach.company_target_errors_archive.max_retries | Max Retries |
| outreach_id | uuid | YES | outreach.company_target_errors_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| park_reason | text | YES | outreach.company_target_errors_archive.park_reason | Park Reason |
| parked_at | timestamp with  | YES | outreach.company_target_errors_archive.parked_at | Timestamp for parked event |
| parked_by | text | YES | outreach.company_target_errors_archive.parked_by | Parked By |
| pipeline_stage | character varyi | YES | outreach.company_target_errors_archive.pipeline_st | Pipeline Stage |
| raw_input | jsonb | YES | outreach.company_target_errors_archive.raw_input | Raw Input |
| resolution_note | text | YES | outreach.company_target_errors_archive.resolution_ | Resolution Note |
| resolved_at | timestamp with  | YES | outreach.company_target_errors_archive.resolved_at | When this error/issue was resolved |
| retention_expires_at | timestamp with  | YES | outreach.company_target_errors_archive.retention_e | Timestamp for retention expires event |
| retry_allowed | boolean | YES | outreach.company_target_errors_archive.retry_allow | Retry Allowed |
| retry_count | integer | YES | outreach.company_target_errors_archive.retry_count | Number of retry attempts so far |
| retry_exhausted | boolean | YES | outreach.company_target_errors_archive.retry_exhau | Retry Exhausted |
| severity | character varyi | YES | outreach.company_target_errors_archive.severity | Severity |
| stack_trace | text | YES | outreach.company_target_errors_archive.stack_trace | Stack Trace |
| ttl_tier | USER-DEFINED | YES | outreach.company_target_errors_archive.ttl_tier | Ttl Tier |

### LEAF: outreach.company_target_orphaned_archive (29 columns, 29 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| active_sequence_id | text | YES | outreach.company_target_orphaned_archive.active_se | Active Sequence Id |
| archive_reason | text | YES | outreach.company_target_orphaned_archive.archive_r | Reason this record was archived |
| archived_at | timestamp with  | NO | outreach.company_target_orphaned_archive.archived_ | When this record was archived |
| bit_score_snapshot | integer | YES | outreach.company_target_orphaned_archive.bit_score | Bit Score Snapshot |
| city | character varyi | YES | outreach.company_target_orphaned_archive.city | City name |
| company_unique_id | text | YES | outreach.company_target_orphaned_archive.company_u | FK to cl.company_identity or Barton company ID |
| confidence_score | numeric | YES | outreach.company_target_orphaned_archive.confidenc | Confidence score (0-100) |
| country | character varyi | YES | outreach.company_target_orphaned_archive.country | Country name or code |
| created_at | timestamp with  | YES | outreach.company_target_orphaned_archive.created_a | When this record was created |
| data_year | integer | YES | outreach.company_target_orphaned_archive.data_year | Data Year |
| domain | character varyi | YES | outreach.company_target_orphaned_archive.domain | Company website domain (lowercase, no protocol) |
| email_method | character varyi | YES | outreach.company_target_orphaned_archive.email_met | Email Method |
| employees | integer | YES | outreach.company_target_orphaned_archive.employees | Employees |
| execution_status | character varyi | YES | outreach.company_target_orphaned_archive.execution | Execution Status |
| first_targeted_at | timestamp with  | YES | outreach.company_target_orphaned_archive.first_tar | Timestamp for first targeted event |
| imo_completed_at | timestamp with  | YES | outreach.company_target_orphaned_archive.imo_compl | Timestamp for imo completed event |
| industry | character varyi | YES | outreach.company_target_orphaned_archive.industry | Industry |
| is_catchall | boolean | YES | outreach.company_target_orphaned_archive.is_catcha | Whether this record catchall |
| last_targeted_at | timestamp with  | YES | outreach.company_target_orphaned_archive.last_targ | Timestamp for last targeted event |
| method_type | character varyi | YES | outreach.company_target_orphaned_archive.method_ty | Method Type |
| outreach_id | uuid | YES | outreach.company_target_orphaned_archive.outreach_ | FK to outreach.outreach spine table (universal join key) |
| outreach_status | text | YES | outreach.company_target_orphaned_archive.outreach_ | Outreach Status |
| postal_code | character varyi | YES | outreach.company_target_orphaned_archive.postal_co | ZIP/postal code (5-digit) |
| sequence_count | integer | YES | outreach.company_target_orphaned_archive.sequence_ | Count of sequence |
| source | text | YES | outreach.company_target_orphaned_archive.source | Data source identifier |
| sovereign_id | uuid | YES | outreach.company_target_orphaned_archive.sovereign | FK to cl.company_identity (sovereign company identifier) |
| state | character varyi | YES | outreach.company_target_orphaned_archive.state | US state code (2-letter) |
| target_id | uuid | NO | outreach.company_target_orphaned_archive.target_id | Primary key for this target record |
| updated_at | timestamp with  | YES | outreach.company_target_orphaned_archive.updated_a | When this record was last updated |

### LEAF: outreach.ctb_audit_log (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| audit_id | integer | NO | outreach.ctb_audit_log.audit_id | Audit Id |
| ctb_merged_at | timestamp with  | YES | outreach.ctb_audit_log.ctb_merged_at | Timestamp for ctb merged event |
| log_data | jsonb | NO | outreach.ctb_audit_log.log_data | Log Data |
| original_created_at | timestamp with  | YES | outreach.ctb_audit_log.original_created_at | Timestamp for original created event |
| original_id | text | YES | outreach.ctb_audit_log.original_id | Original Id |
| source_hub | character varyi | NO | outreach.ctb_audit_log.source_hub | Source Hub |
| source_table | character varyi | NO | outreach.ctb_audit_log.source_table | Source Table |

### LEAF: outreach.dol (12 columns, 12 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| broker_or_advisor | text | YES | outreach.dol.broker_or_advisor | Broker/advisor name from Schedule C code 28 |
| carrier | text | YES | outreach.dol.carrier | Insurance carrier name from Schedule A |
| created_at | timestamp with  | YES | outreach.dol.created_at | When this record was created |
| dol_id | uuid | NO | outreach.dol.dol_id | Dol Id |
| ein | text | YES | outreach.dol.ein | Employer Identification Number (9-digit, no dashes) |
| filing_present | boolean | YES | outreach.dol.filing_present | Whether a Form 5500 filing exists for this EIN |
| funding_type | text | YES | outreach.dol.funding_type | Benefit funding classification (pension_only, fully_insured, self_funded) |
| outreach_id | uuid | NO | outreach.dol.outreach_id | FK to outreach.outreach spine table |
| outreach_start_month | integer | YES | outreach.dol.outreach_start_month | 5 months before renewal month (1-12) — when to begin outreach |
| renewal_month | integer | YES | outreach.dol.renewal_month | Plan year begin month (1-12) |
| updated_at | timestamp with  | YES | outreach.dol.updated_at | When this record was last updated |
| url_enrichment_data | jsonb | YES | outreach.dol.url_enrichment_data | Url Enrichment Data |

### LEAF: outreach.dol_archive (11 columns, 11 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | outreach.dol_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | outreach.dol_archive.archived_at | When this record was archived |
| broker_or_advisor | text | YES | outreach.dol_archive.broker_or_advisor | Broker/advisor name from Schedule C code 28 |
| carrier | text | YES | outreach.dol_archive.carrier | Insurance carrier name from Schedule A |
| created_at | timestamp with  | YES | outreach.dol_archive.created_at | When this record was created |
| dol_id | uuid | NO | outreach.dol_archive.dol_id | Dol Id |
| ein | text | YES | outreach.dol_archive.ein | Employer Identification Number (9-digit, no dashes) |
| filing_present | boolean | YES | outreach.dol_archive.filing_present | Whether a Form 5500 filing exists for this EIN |
| funding_type | text | YES | outreach.dol_archive.funding_type | Benefit funding classification (pension_only, fully_insured, self_funded) |
| outreach_id | uuid | NO | outreach.dol_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| updated_at | timestamp with  | YES | outreach.dol_archive.updated_at | When this record was last updated |

### LEAF: outreach.dol_errors (27 columns, 27 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archived_at | timestamp with  | YES | outreach.dol_errors.archived_at | When this record was archived |
| blocking_reason | text | NO | outreach.dol_errors.blocking_reason | Blocking Reason |
| created_at | timestamp with  | NO | outreach.dol_errors.created_at | When the error was recorded |
| disposition | USER-DEFINED | YES | outreach.dol_errors.disposition | Disposition |
| error_id | uuid | NO | outreach.dol_errors.error_id | Primary key for error record |
| error_type | character varyi | NO | outreach.dol_errors.error_type | Discriminator column — classifies the DOL error |
| escalated_at | timestamp with  | YES | outreach.dol_errors.escalated_at | Timestamp for escalated event |
| escalation_level | integer | YES | outreach.dol_errors.escalation_level | Escalation Level |
| failure_code | character varyi | NO | outreach.dol_errors.failure_code | Failure Code |
| last_retry_at | timestamp with  | YES | outreach.dol_errors.last_retry_at | Timestamp for last retry event |
| max_retries | integer | YES | outreach.dol_errors.max_retries | Max Retries |
| next_retry_at | timestamp with  | YES | outreach.dol_errors.next_retry_at | Timestamp for next retry event |
| outreach_id | uuid | NO | outreach.dol_errors.outreach_id | FK to spine (nullable — error may occur before entity exists) |
| park_reason | text | YES | outreach.dol_errors.park_reason | Park Reason |
| parked_at | timestamp with  | YES | outreach.dol_errors.parked_at | Timestamp for parked event |
| parked_by | text | YES | outreach.dol_errors.parked_by | Parked By |
| pipeline_stage | character varyi | NO | outreach.dol_errors.pipeline_stage | Pipeline Stage |
| raw_input | jsonb | YES | outreach.dol_errors.raw_input | Raw Input |
| requeue_attempts | integer | YES | outreach.dol_errors.requeue_attempts | Requeue Attempts |
| resolution_note | text | YES | outreach.dol_errors.resolution_note | Resolution Note |
| resolved_at | timestamp with  | YES | outreach.dol_errors.resolved_at | When this error/issue was resolved |
| retry_allowed | boolean | NO | outreach.dol_errors.retry_allowed | Retry Allowed |
| retry_count | integer | YES | outreach.dol_errors.retry_count | Number of retry attempts so far |
| retry_exhausted | boolean | YES | outreach.dol_errors.retry_exhausted | Retry Exhausted |
| severity | character varyi | NO | outreach.dol_errors.severity | Severity |
| stack_trace | text | YES | outreach.dol_errors.stack_trace | Stack Trace |
| ttl_tier | USER-DEFINED | YES | outreach.dol_errors.ttl_tier | Ttl Tier |

### LEAF: outreach.dol_errors_archive (29 columns, 29 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | outreach.dol_errors_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | NO | outreach.dol_errors_archive.archived_at | When this record was archived |
| archived_by | text | YES | outreach.dol_errors_archive.archived_by | Archived By |
| blocking_reason | text | YES | outreach.dol_errors_archive.blocking_reason | Blocking Reason |
| created_at | timestamp with  | YES | outreach.dol_errors_archive.created_at | When this record was created |
| disposition | USER-DEFINED | YES | outreach.dol_errors_archive.disposition | Disposition |
| error_id | uuid | NO | outreach.dol_errors_archive.error_id | Primary key for this error record |
| error_type | character varyi | YES | outreach.dol_errors_archive.error_type | Discriminator column classifying the error type |
| escalated_at | timestamp with  | YES | outreach.dol_errors_archive.escalated_at | Timestamp for escalated event |
| escalation_level | integer | YES | outreach.dol_errors_archive.escalation_level | Escalation Level |
| failure_code | character varyi | YES | outreach.dol_errors_archive.failure_code | Failure Code |
| final_disposition | USER-DEFINED | YES | outreach.dol_errors_archive.final_disposition | Final Disposition |
| last_retry_at | timestamp with  | YES | outreach.dol_errors_archive.last_retry_at | Timestamp for last retry event |
| max_retries | integer | YES | outreach.dol_errors_archive.max_retries | Max Retries |
| outreach_id | uuid | YES | outreach.dol_errors_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| park_reason | text | YES | outreach.dol_errors_archive.park_reason | Park Reason |
| parked_at | timestamp with  | YES | outreach.dol_errors_archive.parked_at | Timestamp for parked event |
| parked_by | text | YES | outreach.dol_errors_archive.parked_by | Parked By |
| pipeline_stage | character varyi | YES | outreach.dol_errors_archive.pipeline_stage | Pipeline Stage |
| raw_input | jsonb | YES | outreach.dol_errors_archive.raw_input | Raw Input |
| resolution_note | text | YES | outreach.dol_errors_archive.resolution_note | Resolution Note |
| resolved_at | timestamp with  | YES | outreach.dol_errors_archive.resolved_at | When this error/issue was resolved |
| retention_expires_at | timestamp with  | YES | outreach.dol_errors_archive.retention_expires_at | Timestamp for retention expires event |
| retry_allowed | boolean | YES | outreach.dol_errors_archive.retry_allowed | Retry Allowed |
| retry_count | integer | YES | outreach.dol_errors_archive.retry_count | Number of retry attempts so far |
| retry_exhausted | boolean | YES | outreach.dol_errors_archive.retry_exhausted | Retry Exhausted |
| severity | character varyi | YES | outreach.dol_errors_archive.severity | Severity |
| stack_trace | text | YES | outreach.dol_errors_archive.stack_trace | Stack Trace |
| ttl_tier | USER-DEFINED | YES | outreach.dol_errors_archive.ttl_tier | Ttl Tier |

### LEAF: outreach.hub_registry (12 columns, 12 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| classification | character varyi | NO | outreach.hub_registry.classification | Classification |
| core_metric | character varyi | NO | outreach.hub_registry.core_metric | Core Metric |
| created_at | timestamp with  | NO | outreach.hub_registry.created_at | When this record was created |
| description | text | YES | outreach.hub_registry.description | Description |
| doctrine_id | character varyi | NO | outreach.hub_registry.doctrine_id | Doctrine Id |
| gates_completion | boolean | NO | outreach.hub_registry.gates_completion | Gates Completion |
| hub_id | character varyi | NO | outreach.hub_registry.hub_id | Hub Id |
| hub_name | character varyi | NO | outreach.hub_registry.hub_name | Hub Name |
| metric_critical_threshold | numeric | YES | outreach.hub_registry.metric_critical_threshold | Metric Critical Threshold |
| metric_healthy_threshold | numeric | YES | outreach.hub_registry.metric_healthy_threshold | Metric Healthy Threshold |
| updated_at | timestamp with  | NO | outreach.hub_registry.updated_at | When this record was last updated |
| waterfall_order | integer | NO | outreach.hub_registry.waterfall_order | Waterfall Order |

### LEAF: outreach.outreach (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | outreach.outreach.created_at | When the outreach record was created |
| domain | character varyi | YES | outreach.outreach.domain | Company website domain (lowercase, no protocol) |
| ein | character varyi | YES | outreach.outreach.ein | Employer Identification Number (9-digit, no dashes) |
| has_appointment | boolean | YES | outreach.outreach.has_appointment | Whether this record appointment |
| outreach_id | uuid | NO | outreach.outreach.outreach_id | Universal join key — minted here, propagated to all sub-hub tables |
| sovereign_id | uuid | NO | outreach.outreach.sovereign_id | FK to cl.company_identity (sovereign company identifier) |
| updated_at | timestamp with  | NO | outreach.outreach.updated_at | When the outreach record was last updated |

### LEAF: outreach.outreach_archive (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | outreach.outreach_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | outreach.outreach_archive.archived_at | When this record was archived |
| created_at | timestamp with  | NO | outreach.outreach_archive.created_at | When this record was created |
| domain | character varyi | YES | outreach.outreach_archive.domain | Company website domain (lowercase, no protocol) |
| outreach_id | uuid | NO | outreach.outreach_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| sovereign_id | uuid | NO | outreach.outreach_archive.sovereign_id | FK to cl.company_identity (sovereign company identifier) |
| updated_at | timestamp with  | NO | outreach.outreach_archive.updated_at | When this record was last updated |

### LEAF: outreach.outreach_excluded (10 columns, 10 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| cl_status | text | YES | outreach.outreach_excluded.cl_status | Cl Status |
| company_name | text | YES | outreach.outreach_excluded.company_name | Company legal or common name |
| created_at | timestamp with  | YES | outreach.outreach_excluded.created_at | When this record was created |
| domain | text | YES | outreach.outreach_excluded.domain | Company website domain (lowercase, no protocol) |
| excluded_at | timestamp with  | YES | outreach.outreach_excluded.excluded_at | Timestamp for excluded event |
| excluded_by | text | YES | outreach.outreach_excluded.excluded_by | Excluded By |
| exclusion_reason | text | YES | outreach.outreach_excluded.exclusion_reason | Exclusion Reason |
| outreach_id | uuid | NO | outreach.outreach_excluded.outreach_id | FK to outreach.outreach spine table (universal join key) |
| sovereign_id | uuid | YES | outreach.outreach_excluded.sovereign_id | FK to cl.company_identity (sovereign company identifier) |
| updated_at | timestamp with  | YES | outreach.outreach_excluded.updated_at | When this record was last updated |

### LEAF: outreach.outreach_legacy_quarantine (5 columns, 5 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| original_created_at | timestamp with  | YES | outreach.outreach_legacy_quarantine.original_creat | Timestamp for original created event |
| outreach_id | uuid | NO | outreach.outreach_legacy_quarantine.outreach_id | FK to outreach.outreach spine table (universal join key) |
| quarantine_reason | text | NO | outreach.outreach_legacy_quarantine.quarantine_rea | Quarantine Reason |
| quarantined_at | timestamp with  | YES | outreach.outreach_legacy_quarantine.quarantined_at | Timestamp for quarantined event |
| sovereign_id | uuid | YES | outreach.outreach_legacy_quarantine.sovereign_id | FK to cl.company_identity (sovereign company identifier) |

### LEAF: outreach.outreach_orphan_archive (7 columns, 7 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | character varyi | YES | outreach.outreach_orphan_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | outreach.outreach_orphan_archive.archived_at | When this record was archived |
| created_at | timestamp with  | NO | outreach.outreach_orphan_archive.created_at | When this record was created |
| domain | character varyi | YES | outreach.outreach_orphan_archive.domain | Company website domain (lowercase, no protocol) |
| outreach_id | uuid | NO | outreach.outreach_orphan_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| sovereign_id | uuid | NO | outreach.outreach_orphan_archive.sovereign_id | FK to cl.company_identity (sovereign company identifier) |
| updated_at | timestamp with  | NO | outreach.outreach_orphan_archive.updated_at | When this record was last updated |

### LEAF: outreach.people (20 columns, 20 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | NO | outreach.people.company_unique_id | Denormalized FK to cl.company_identity |
| contact_status | text | NO | outreach.people.contact_status | Contact status |
| created_at | timestamp with  | NO | outreach.people.created_at | Creation timestamp |
| current_bit_score | integer | NO | outreach.people.current_bit_score | Current BIT score (0-100) |
| email | text | NO | outreach.people.email | Primary email address |
| email_click_count | integer | NO | outreach.people.email_click_count | Email click count |
| email_open_count | integer | NO | outreach.people.email_open_count | Email open count |
| email_reply_count | integer | NO | outreach.people.email_reply_count | Email reply count |
| email_verified | boolean | NO | outreach.people.email_verified | Email verification status |
| email_verified_at | timestamp with  | YES | outreach.people.email_verified_at | Verification timestamp |
| funnel_membership | USER-DEFINED | NO | outreach.people.funnel_membership | Funnel position |
| last_event_ts | timestamp with  | YES | outreach.people.last_event_ts | Last event timestamp |
| last_state_change_ts | timestamp with  | YES | outreach.people.last_state_change_ts | Last state change timestamp |
| lifecycle_state | USER-DEFINED | NO | outreach.people.lifecycle_state | Lifecycle stage |
| outreach_id | uuid | YES | outreach.people.outreach_id | FK to outreach.outreach spine table (universal join key) |
| person_id | uuid | NO | outreach.people.person_id | UUID primary key for person record |
| slot_type | text | YES | outreach.people.slot_type | Executive slot: CHRO, HR, Benefits, CFO, CEO |
| source | text | YES | outreach.people.source | Record origin |
| target_id | uuid | NO | outreach.people.target_id | FK to outreach.company_target |
| updated_at | timestamp with  | NO | outreach.people.updated_at | Last update timestamp |

### LEAF: outreach.people_archive (22 columns, 22 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | outreach.people_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | outreach.people_archive.archived_at | When this record was archived |
| company_unique_id | text | NO | outreach.people_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| contact_status | text | NO | outreach.people_archive.contact_status | Contact Status |
| created_at | timestamp with  | NO | outreach.people_archive.created_at | When this record was created |
| current_bit_score | integer | NO | outreach.people_archive.current_bit_score | Current Bit score |
| email | text | NO | outreach.people_archive.email | Email address |
| email_click_count | integer | NO | outreach.people_archive.email_click_count | Count of email click |
| email_open_count | integer | NO | outreach.people_archive.email_open_count | Count of email open |
| email_reply_count | integer | NO | outreach.people_archive.email_reply_count | Count of email reply |
| email_verified | boolean | NO | outreach.people_archive.email_verified | Whether email was verified via Million Verifier |
| email_verified_at | timestamp with  | YES | outreach.people_archive.email_verified_at | Timestamp for email verified event |
| funnel_membership | USER-DEFINED | NO | outreach.people_archive.funnel_membership | Funnel Membership |
| last_event_ts | timestamp with  | YES | outreach.people_archive.last_event_ts | Last Event Ts |
| last_state_change_ts | timestamp with  | YES | outreach.people_archive.last_state_change_ts | Last State Change Ts |
| lifecycle_state | USER-DEFINED | NO | outreach.people_archive.lifecycle_state | Lifecycle State |
| outreach_id | uuid | YES | outreach.people_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| person_id | uuid | NO | outreach.people_archive.person_id | Person Id |
| slot_type | text | YES | outreach.people_archive.slot_type | Executive role type (CEO, CFO, HR, CTO, CMO, COO) |
| source | text | YES | outreach.people_archive.source | Data source identifier |
| target_id | uuid | NO | outreach.people_archive.target_id | Primary key for this target record |
| updated_at | timestamp with  | NO | outreach.people_archive.updated_at | When this record was last updated |

### LEAF: outreach.signal_output (12 columns, 5 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| correlation_id | uuid | NO | outreach.signal_output.correlation_id | _undocumented_ |
| created_at | timestamp with  | NO | outreach.signal_output.created_at | _undocumented_ |
| detected_at | timestamp with  | NO | outreach.signal_output.detected_at | _undocumented_ |
| expires_at | timestamp with  | NO | outreach.signal_output.expires_at | Signal expiry. DOL signals: 365d. People signals: 90d. Blog signals: 60d. Expire |
| magnitude | integer | NO | outreach.signal_output.magnitude | Signal strength 0-100. Used for prioritization. D-04 Renewal Proximity = 80 (cur |
| outreach_id | uuid | NO | outreach.signal_output.outreach_id | _undocumented_ |
| run_month | date | NO | outreach.signal_output.run_month | First day of the month this worker run covers (e.g. 2026-03-01). Used as the ded |
| signal_code | character varyi | NO | outreach.signal_output.signal_code | Structured signal identifier: D-01..D-07 (DOL), P-01..P-05 (People), B-01..B-06  |
| signal_id | uuid | NO | outreach.signal_output.signal_id | _undocumented_ |
| signal_name | text | NO | outreach.signal_output.signal_name | _undocumented_ |
| signal_source | character varyi | NO | outreach.signal_output.signal_source | _undocumented_ |
| signal_value | jsonb | NO | outreach.signal_output.signal_value | JSONB evidence payload. Contents vary by signal_code. Always include at minimum: |

### LEAF: outreach.url_discovery_failures (20 columns, 20 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archived_at | timestamp with  | YES | outreach.url_discovery_failures.archived_at | When this record was archived |
| company_unique_id | text | NO | outreach.url_discovery_failures.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | YES | outreach.url_discovery_failures.created_at | When this record was created |
| disposition | USER-DEFINED | YES | outreach.url_discovery_failures.disposition | Disposition |
| escalated_at | timestamp with  | YES | outreach.url_discovery_failures.escalated_at | Timestamp for escalated event |
| escalation_level | integer | YES | outreach.url_discovery_failures.escalation_level | Escalation Level |
| failure_id | uuid | NO | outreach.url_discovery_failures.failure_id | Failure Id |
| failure_reason | character varyi | NO | outreach.url_discovery_failures.failure_reason | Failure Reason |
| last_attempt_at | timestamp with  | YES | outreach.url_discovery_failures.last_attempt_at | Timestamp for lasttempt event |
| last_retry_at | timestamp with  | YES | outreach.url_discovery_failures.last_retry_at | Timestamp for last retry event |
| max_retries | integer | YES | outreach.url_discovery_failures.max_retries | Max Retries |
| next_retry_at | timestamp with  | YES | outreach.url_discovery_failures.next_retry_at | Timestamp for next retry event |
| park_reason | text | YES | outreach.url_discovery_failures.park_reason | Park Reason |
| parked_at | timestamp with  | YES | outreach.url_discovery_failures.parked_at | Timestamp for parked event |
| parked_by | text | YES | outreach.url_discovery_failures.parked_by | Parked By |
| resolved_at | timestamp with  | YES | outreach.url_discovery_failures.resolved_at | When this error/issue was resolved |
| retry_count | integer | YES | outreach.url_discovery_failures.retry_count | Number of retry attempts so far |
| retry_exhausted | boolean | YES | outreach.url_discovery_failures.retry_exhausted | Retry Exhausted |
| ttl_tier | USER-DEFINED | YES | outreach.url_discovery_failures.ttl_tier | Ttl Tier |
| website_url | text | YES | outreach.url_discovery_failures.website_url | Company website URL |

### LEAF: outreach.url_discovery_failures_archive (21 columns, 21 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | outreach.url_discovery_failures_archive.archive_re | Reason this record was archived |
| archived_at | timestamp with  | NO | outreach.url_discovery_failures_archive.archived_a | When this record was archived |
| archived_by | text | YES | outreach.url_discovery_failures_archive.archived_b | Archived By |
| company_unique_id | text | YES | outreach.url_discovery_failures_archive.company_un | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | YES | outreach.url_discovery_failures_archive.created_at | When this record was created |
| disposition | USER-DEFINED | YES | outreach.url_discovery_failures_archive.dispositio | Disposition |
| escalated_at | timestamp with  | YES | outreach.url_discovery_failures_archive.escalated_ | Timestamp for escalated event |
| escalation_level | integer | YES | outreach.url_discovery_failures_archive.escalation | Escalation Level |
| failure_id | uuid | NO | outreach.url_discovery_failures_archive.failure_id | Failure Id |
| failure_reason | character varyi | YES | outreach.url_discovery_failures_archive.failure_re | Failure Reason |
| final_disposition | USER-DEFINED | YES | outreach.url_discovery_failures_archive.final_disp | Final Disposition |
| last_retry_at | timestamp with  | YES | outreach.url_discovery_failures_archive.last_retry | Timestamp for last retry event |
| max_retries | integer | YES | outreach.url_discovery_failures_archive.max_retrie | Max Retries |
| park_reason | text | YES | outreach.url_discovery_failures_archive.park_reaso | Park Reason |
| parked_at | timestamp with  | YES | outreach.url_discovery_failures_archive.parked_at | Timestamp for parked event |
| parked_by | text | YES | outreach.url_discovery_failures_archive.parked_by | Parked By |
| retention_expires_at | timestamp with  | YES | outreach.url_discovery_failures_archive.retention_ | Timestamp for retention expires event |
| retry_count | integer | YES | outreach.url_discovery_failures_archive.retry_coun | Number of retry attempts so far |
| retry_exhausted | boolean | YES | outreach.url_discovery_failures_archive.retry_exha | Retry Exhausted |
| ttl_tier | USER-DEFINED | YES | outreach.url_discovery_failures_archive.ttl_tier | Ttl Tier |
| website_url | text | YES | outreach.url_discovery_failures_archive.website_ur | Company website URL |

### LEAF: outreach.v_bit_hot_companies (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| blog_score | numeric | YES | outreach.v_bit_hot_companies.blog_score | _undocumented_ |
| dol_score | numeric | YES | outreach.v_bit_hot_companies.dol_score | _undocumented_ |
| domain | character varyi | YES | outreach.v_bit_hot_companies.domain | _undocumented_ |
| last_scored_at | timestamp with  | YES | outreach.v_bit_hot_companies.last_scored_at | _undocumented_ |
| last_signal_at | timestamp with  | YES | outreach.v_bit_hot_companies.last_signal_at | _undocumented_ |
| outreach_id | uuid | YES | outreach.v_bit_hot_companies.outreach_id | _undocumented_ |
| people_score | numeric | YES | outreach.v_bit_hot_companies.people_score | _undocumented_ |
| score | numeric | YES | outreach.v_bit_hot_companies.score | _undocumented_ |
| score_tier | character varyi | YES | outreach.v_bit_hot_companies.score_tier | _undocumented_ |
| signal_count | integer | YES | outreach.v_bit_hot_companies.signal_count | _undocumented_ |
| talent_flow_score | numeric | YES | outreach.v_bit_hot_companies.talent_flow_score | _undocumented_ |

### LEAF: outreach.v_bit_tier_distribution (5 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| avg_score | numeric | YES | outreach.v_bit_tier_distribution.avg_score | _undocumented_ |
| avg_signals | numeric | YES | outreach.v_bit_tier_distribution.avg_signals | _undocumented_ |
| company_count | bigint | YES | outreach.v_bit_tier_distribution.company_count | _undocumented_ |
| max_score | numeric | YES | outreach.v_bit_tier_distribution.max_score | _undocumented_ |
| score_tier | character varyi | YES | outreach.v_bit_tier_distribution.score_tier | _undocumented_ |

### LEAF: outreach.v_context_current (21 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| blog_signal_count | bigint | YES | outreach.v_context_current.blog_signal_count | _undocumented_ |
| ct_completed_at | timestamp with  | YES | outreach.v_context_current.ct_completed_at | _undocumented_ |
| ct_confidence | numeric | YES | outreach.v_context_current.ct_confidence | _undocumented_ |
| ct_email_method | character varyi | YES | outreach.v_context_current.ct_email_method | _undocumented_ |
| ct_is_catchall | boolean | YES | outreach.v_context_current.ct_is_catchall | _undocumented_ |
| ct_method_type | character varyi | YES | outreach.v_context_current.ct_method_type | _undocumented_ |
| ct_status | character varyi | YES | outreach.v_context_current.ct_status | _undocumented_ |
| dol_assets | text | YES | outreach.v_context_current.dol_assets | _undocumented_ |
| dol_created_at | timestamp with  | YES | outreach.v_context_current.dol_created_at | _undocumented_ |
| dol_ein | text | YES | outreach.v_context_current.dol_ein | _undocumented_ |
| dol_filing_year | text | YES | outreach.v_context_current.dol_filing_year | _undocumented_ |
| dol_participants | text | YES | outreach.v_context_current.dol_participants | _undocumented_ |
| domain | character varyi | YES | outreach.v_context_current.domain | _undocumented_ |
| last_activity_at | timestamp with  | YES | outreach.v_context_current.last_activity_at | _undocumented_ |
| outreach_id | uuid | YES | outreach.v_context_current.outreach_id | _undocumented_ |
| people_count | bigint | YES | outreach.v_context_current.people_count | _undocumented_ |
| people_verified_count | bigint | YES | outreach.v_context_current.people_verified_count | _undocumented_ |
| sovereign_id | uuid | YES | outreach.v_context_current.sovereign_id | _undocumented_ |
| spine_created_at | timestamp with  | YES | outreach.v_context_current.spine_created_at | _undocumented_ |
| spine_updated_at | timestamp with  | YES | outreach.v_context_current.spine_updated_at | _undocumented_ |
| waterfall_state | text | YES | outreach.v_context_current.waterfall_state | _undocumented_ |

### LEAF: outreach.v_ct_zip_repair_candidates (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| confidence_score | bigint | YES | outreach.v_ct_zip_repair_candidates.confidence_sco | _undocumented_ |
| dol_city | character varyi | YES | outreach.v_ct_zip_repair_candidates.dol_city | _undocumented_ |
| dol_state | character varyi | YES | outreach.v_ct_zip_repair_candidates.dol_state | _undocumented_ |
| evidence_summary | text | YES | outreach.v_ct_zip_repair_candidates.evidence_summa | _undocumented_ |
| first_year_seen | text | YES | outreach.v_ct_zip_repair_candidates.first_year_see | _undocumented_ |
| last_year_seen | text | YES | outreach.v_ct_zip_repair_candidates.last_year_seen | _undocumented_ |
| occurrence_count | bigint | YES | outreach.v_ct_zip_repair_candidates.occurrence_cou | _undocumented_ |
| outreach_id | uuid | YES | outreach.v_ct_zip_repair_candidates.outreach_id | _undocumented_ |
| proposed_postal_code | text | YES | outreach.v_ct_zip_repair_candidates.proposed_posta | _undocumented_ |
| years_seen | bigint | YES | outreach.v_ct_zip_repair_candidates.years_seen | _undocumented_ |

### LEAF: outreach.v_dol_zip_evidence (9 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| dol_city | character varyi | YES | outreach.v_dol_zip_evidence.dol_city | _undocumented_ |
| dol_state | character varyi | YES | outreach.v_dol_zip_evidence.dol_state | _undocumented_ |
| first_year_seen | text | YES | outreach.v_dol_zip_evidence.first_year_seen | _undocumented_ |
| last_year_seen | text | YES | outreach.v_dol_zip_evidence.last_year_seen | _undocumented_ |
| occurrence_count | bigint | YES | outreach.v_dol_zip_evidence.occurrence_count | _undocumented_ |
| outreach_id | uuid | YES | outreach.v_dol_zip_evidence.outreach_id | _undocumented_ |
| source_count | bigint | YES | outreach.v_dol_zip_evidence.source_count | _undocumented_ |
| years_seen | bigint | YES | outreach.v_dol_zip_evidence.years_seen | _undocumented_ |
| zip_candidate | text | YES | outreach.v_dol_zip_evidence.zip_candidate | _undocumented_ |

### LEAF: outreach.vw_marketing_eligibility (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| bit_gate_status | text | YES | outreach.vw_marketing_eligibility.bit_gate_status | _undocumented_ |
| bit_score | integer | YES | outreach.vw_marketing_eligibility.bit_score | _undocumented_ |
| company_target_status | USER-DEFINED | YES | outreach.vw_marketing_eligibility.company_target_s | _undocumented_ |
| company_unique_id | text | YES | outreach.vw_marketing_eligibility.company_unique_i | _undocumented_ |
| dol_status | USER-DEFINED | YES | outreach.vw_marketing_eligibility.dol_status | _undocumented_ |
| marketing_tier | integer | YES | outreach.vw_marketing_eligibility.marketing_tier | _undocumented_ |
| next_tier_requirement | text | YES | outreach.vw_marketing_eligibility.next_tier_requir | _undocumented_ |
| overall_status | text | YES | outreach.vw_marketing_eligibility.overall_status | _undocumented_ |
| people_status | USER-DEFINED | YES | outreach.vw_marketing_eligibility.people_status | _undocumented_ |
| talent_flow_status | USER-DEFINED | YES | outreach.vw_marketing_eligibility.talent_flow_stat | _undocumented_ |
| tier_explanation | text | YES | outreach.vw_marketing_eligibility.tier_explanation | _undocumented_ |

### LEAF: outreach.vw_sovereign_completion (13 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| bit_gate_status | text | YES | outreach.vw_sovereign_completion.bit_gate_status | _undocumented_ |
| bit_score | integer | YES | outreach.vw_sovereign_completion.bit_score | _undocumented_ |
| blocked_count | bigint | YES | outreach.vw_sovereign_completion.blocked_count | _undocumented_ |
| company_target_status | USER-DEFINED | YES | outreach.vw_sovereign_completion.company_target_st | _undocumented_ |
| company_unique_id | text | YES | outreach.vw_sovereign_completion.company_unique_id | _undocumented_ |
| dol_status | USER-DEFINED | YES | outreach.vw_sovereign_completion.dol_status | _undocumented_ |
| fail_count | bigint | YES | outreach.vw_sovereign_completion.fail_count | _undocumented_ |
| in_progress_count | bigint | YES | outreach.vw_sovereign_completion.in_progress_count | _undocumented_ |
| overall_status | text | YES | outreach.vw_sovereign_completion.overall_status | _undocumented_ |
| pass_count | bigint | YES | outreach.vw_sovereign_completion.pass_count | _undocumented_ |
| people_status | USER-DEFINED | YES | outreach.vw_sovereign_completion.people_status | _undocumented_ |
| talent_flow_status | USER-DEFINED | YES | outreach.vw_sovereign_completion.talent_flow_statu | _undocumented_ |
| total_required_hubs | bigint | YES | outreach.vw_sovereign_completion.total_required_hu | _undocumented_ |

---

## BRANCH: outreach_ctx (1 tables, 4 columns, 100% documented)

### LEAF: outreach_ctx.context (4 columns, 4 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | outreach_ctx.context.created_at | When this record was created |
| notes | text | YES | outreach_ctx.context.notes | Human-readable notes |
| outreach_context_id | text | NO | outreach_ctx.context.outreach_context_id | Outreach Context Id |
| status | text | NO | outreach_ctx.context.status | Current status of this record |

---

## BRANCH: partners (1 tables, 13 columns, 100% documented)

### LEAF: partners.fractional_cfo_master (13 columns, 13 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | partners.fractional_cfo_master.created_at | When this record was created |
| email | text | YES | partners.fractional_cfo_master.email | Email address |
| firm_name | text | NO | partners.fractional_cfo_master.firm_name | Firm Name |
| fractional_cfo_id | uuid | NO | partners.fractional_cfo_master.fractional_cfo_id | Fractional Cfo Id |
| geography | text | YES | partners.fractional_cfo_master.geography | Geography |
| linkedin_url | text | YES | partners.fractional_cfo_master.linkedin_url | LinkedIn profile URL |
| metadata | jsonb | YES | partners.fractional_cfo_master.metadata | Metadata |
| niche_focus | text | YES | partners.fractional_cfo_master.niche_focus | Niche Focus |
| primary_contact_name | text | NO | partners.fractional_cfo_master.primary_contact_nam | Primary Contact Name |
| source | text | NO | partners.fractional_cfo_master.source | Data source identifier |
| source_detail | text | YES | partners.fractional_cfo_master.source_detail | Source Detail |
| status | USER-DEFINED | NO | partners.fractional_cfo_master.status | Current status of this record |
| updated_at | timestamp with  | NO | partners.fractional_cfo_master.updated_at | When this record was last updated |

---

## BRANCH: people (25 tables, 364 columns, 54% documented)

### LEAF: people.company_slot (14 columns, 14 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | NO | people.company_slot.company_unique_id | FK to cl.company_identity or Barton company ID |
| confidence_score | numeric | YES | people.company_slot.confidence_score | Confidence score (0-100) |
| created_at | timestamp with  | YES | people.company_slot.created_at | When this record was created |
| filled_at | timestamp with  | YES | people.company_slot.filled_at | When this slot was filled with a person |
| is_filled | boolean | YES | people.company_slot.is_filled | Whether this slot has an assigned person (TRUE = people record linked) |
| outreach_id | uuid | NO | people.company_slot.outreach_id | FK to outreach.outreach spine table |
| person_unique_id | text | YES | people.company_slot.person_unique_id | FK to people.people_master.unique_id (Barton ID format 04.04.02.YY.NNNNNN.NNN) |
| slot_id | uuid | NO | people.company_slot.slot_id | Primary key for the slot record |
| slot_phone | text | YES | people.company_slot.slot_phone | Phone number stored on the slot |
| slot_phone_source | text | YES | people.company_slot.slot_phone_source | Source of the slot phone number |
| slot_phone_updated_at | timestamp with  | YES | people.company_slot.slot_phone_updated_at | Timestamp for slot phone updated event |
| slot_type | text | NO | people.company_slot.slot_type | Executive role type (CEO, CFO, HR, CTO, CMO, COO) |
| source_system | text | YES | people.company_slot.source_system | System that originated this record |
| updated_at | timestamp with  | YES | people.company_slot.updated_at | When this record was last updated |

### LEAF: people.company_slot_archive (13 columns, 13 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | people.company_slot_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | YES | people.company_slot_archive.archived_at | When this record was archived |
| company_unique_id | text | NO | people.company_slot_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| confidence_score | numeric | YES | people.company_slot_archive.confidence_score | Confidence score (0-100) |
| created_at | timestamp with  | YES | people.company_slot_archive.created_at | When this record was created |
| filled_at | timestamp with  | YES | people.company_slot_archive.filled_at | When this slot was filled with a person |
| is_filled | boolean | YES | people.company_slot_archive.is_filled | Whether this slot has an assigned person |
| outreach_id | uuid | NO | people.company_slot_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| person_unique_id | text | YES | people.company_slot_archive.person_unique_id | FK to people.people_master.unique_id (Barton person ID) |
| slot_id | uuid | NO | people.company_slot_archive.slot_id | Primary key for this company slot record |
| slot_type | text | NO | people.company_slot_archive.slot_type | Executive role type (CEO, CFO, HR, CTO, CMO, COO) |
| source_system | text | YES | people.company_slot_archive.source_system | System that originated this record |
| updated_at | timestamp with  | YES | people.company_slot_archive.updated_at | When this record was last updated |

### LEAF: people.contact_enhanced_view (40 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| calendly_url | text | YES | people.contact_enhanced_view.calendly_url | _undocumented_ |
| company_unique_id | text | YES | people.contact_enhanced_view.company_unique_id | _undocumented_ |
| computed_full_name | text | YES | people.contact_enhanced_view.computed_full_name | _undocumented_ |
| contact_availability | text | YES | people.contact_enhanced_view.contact_availability | _undocumented_ |
| contact_id | bigint | YES | people.contact_enhanced_view.contact_id | _undocumented_ |
| contact_owner | text | YES | people.contact_enhanced_view.contact_owner | _undocumented_ |
| created_at | timestamp with  | YES | people.contact_enhanced_view.created_at | _undocumented_ |
| department | text | YES | people.contact_enhanced_view.department | _undocumented_ |
| do_not_contact | boolean | YES | people.contact_enhanced_view.do_not_contact | _undocumented_ |
| email | text | YES | people.contact_enhanced_view.email | _undocumented_ |
| email_last_verified_at | timestamp with  | YES | people.contact_enhanced_view.email_last_verified_a | _undocumented_ |
| email_status | text | YES | people.contact_enhanced_view.email_status | _undocumented_ |
| facebook_url | text | YES | people.contact_enhanced_view.facebook_url | _undocumented_ |
| first_name | text | YES | people.contact_enhanced_view.first_name | _undocumented_ |
| full_name | text | YES | people.contact_enhanced_view.full_name | _undocumented_ |
| github_url | text | YES | people.contact_enhanced_view.github_url | _undocumented_ |
| has_phone | boolean | YES | people.contact_enhanced_view.has_phone | _undocumented_ |
| has_profile_source | boolean | YES | people.contact_enhanced_view.has_profile_source | _undocumented_ |
| has_social_media | boolean | YES | people.contact_enhanced_view.has_social_media | _undocumented_ |
| instagram_url | text | YES | people.contact_enhanced_view.instagram_url | _undocumented_ |
| last_name | text | YES | people.contact_enhanced_view.last_name | _undocumented_ |
| last_profile_checked_at | timestamp with  | YES | people.contact_enhanced_view.last_profile_checked_ | _undocumented_ |
| linkedin_url | text | YES | people.contact_enhanced_view.linkedin_url | _undocumented_ |
| mobile_phone_e164 | text | YES | people.contact_enhanced_view.mobile_phone_e164 | _undocumented_ |
| personal_website_url | text | YES | people.contact_enhanced_view.personal_website_url | _undocumented_ |
| phone | text | YES | people.contact_enhanced_view.phone | _undocumented_ |
| profile_source_url | text | YES | people.contact_enhanced_view.profile_source_url | _undocumented_ |
| seniority | text | YES | people.contact_enhanced_view.seniority | _undocumented_ |
| slot_unique_id | text | YES | people.contact_enhanced_view.slot_unique_id | _undocumented_ |
| source_record_id | text | YES | people.contact_enhanced_view.source_record_id | _undocumented_ |
| source_system | text | YES | people.contact_enhanced_view.source_system | _undocumented_ |
| telegram_handle | text | YES | people.contact_enhanced_view.telegram_handle | _undocumented_ |
| threads_url | text | YES | people.contact_enhanced_view.threads_url | _undocumented_ |
| tiktok_url | text | YES | people.contact_enhanced_view.tiktok_url | _undocumented_ |
| title | text | YES | people.contact_enhanced_view.title | _undocumented_ |
| updated_at | timestamp with  | YES | people.contact_enhanced_view.updated_at | _undocumented_ |
| whatsapp_handle | text | YES | people.contact_enhanced_view.whatsapp_handle | _undocumented_ |
| work_phone_e164 | text | YES | people.contact_enhanced_view.work_phone_e164 | _undocumented_ |
| x_url | text | YES | people.contact_enhanced_view.x_url | _undocumented_ |
| youtube_url | text | YES | people.contact_enhanced_view.youtube_url | _undocumented_ |

### LEAF: people.due_email_recheck_30d (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| contact_id | bigint | YES | people.due_email_recheck_30d.contact_id | _undocumented_ |
| email | text | YES | people.due_email_recheck_30d.email | _undocumented_ |
| email_checked_at | timestamp with  | YES | people.due_email_recheck_30d.email_checked_at | _undocumented_ |
| email_status | text | YES | people.due_email_recheck_30d.email_status | _undocumented_ |
| full_name | text | YES | people.due_email_recheck_30d.full_name | _undocumented_ |
| last_checked_at | timestamp with  | YES | people.due_email_recheck_30d.last_checked_at | _undocumented_ |
| title | text | YES | people.due_email_recheck_30d.title | _undocumented_ |

### LEAF: people.linkedin_snapshots (18 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | NO | people.linkedin_snapshots.company_unique_id | _undocumented_ |
| fetched_at | timestamp with  | NO | people.linkedin_snapshots.fetched_at | _undocumented_ |
| headline | text | YES | people.linkedin_snapshots.headline | _undocumented_ |
| last_post_date | timestamp with  | YES | people.linkedin_snapshots.last_post_date | _undocumented_ |
| linkedin_url | text | NO | people.linkedin_snapshots.linkedin_url | _undocumented_ |
| location | text | YES | people.linkedin_snapshots.location | _undocumented_ |
| movement_detected | boolean | NO | people.linkedin_snapshots.movement_detected | _undocumented_ |
| movement_type | text | NO | people.linkedin_snapshots.movement_type | _undocumented_ |
| parsed_company | text | YES | people.linkedin_snapshots.parsed_company | _undocumented_ |
| parsed_name | text | YES | people.linkedin_snapshots.parsed_name | _undocumented_ |
| parsed_title | text | YES | people.linkedin_snapshots.parsed_title | _undocumented_ |
| person_id | text | NO | people.linkedin_snapshots.person_id | _undocumented_ |
| profile_photo_url | text | YES | people.linkedin_snapshots.profile_photo_url | _undocumented_ |
| pushed_at | timestamp with  | NO | people.linkedin_snapshots.pushed_at | _undocumented_ |
| raw_title_tag | text | YES | people.linkedin_snapshots.raw_title_tag | _undocumented_ |
| run_month | date | NO | people.linkedin_snapshots.run_month | _undocumented_ |
| snapshot_id | uuid | NO | people.linkedin_snapshots.snapshot_id | _undocumented_ |
| source_tool | text | NO | people.linkedin_snapshots.source_tool | _undocumented_ |

### LEAF: people.next_profile_urls_30d (3 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| contact_id | bigint | YES | people.next_profile_urls_30d.contact_id | _undocumented_ |
| last_checked_at | timestamp with  | YES | people.next_profile_urls_30d.last_checked_at | _undocumented_ |
| url | text | YES | people.next_profile_urls_30d.url | _undocumented_ |

### LEAF: people.people_errors (28 columns, 28 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archived_at | timestamp with  | YES | people.people_errors.archived_at | When this record was archived |
| created_at | timestamp with  | NO | people.people_errors.created_at | When the error was recorded |
| disposition | USER-DEFINED | YES | people.people_errors.disposition | Disposition |
| error_code | text | NO | people.people_errors.error_code | Error Code |
| error_id | uuid | NO | people.people_errors.error_id | Primary key for error record |
| error_message | text | NO | people.people_errors.error_message | Human-readable error description |
| error_stage | text | NO | people.people_errors.error_stage | Pipeline stage where error occurred (slot_creation, slot_fill, etc.) |
| error_type | text | NO | people.people_errors.error_type | Discriminator column (validation, ambiguity, conflict, missing_data, stale_data, |
| escalated_at | timestamp with  | YES | people.people_errors.escalated_at | Timestamp for escalated event |
| escalation_level | integer | YES | people.people_errors.escalation_level | Escalation Level |
| last_retry_at | timestamp with  | YES | people.people_errors.last_retry_at | Timestamp for last retry event |
| last_updated_at | timestamp with  | NO | people.people_errors.last_updated_at | Timestamp for last updated event |
| max_retries | integer | YES | people.people_errors.max_retries | Max Retries |
| next_retry_at | timestamp with  | YES | people.people_errors.next_retry_at | Timestamp for next retry event |
| outreach_id | uuid | NO | people.people_errors.outreach_id | FK to spine (nullable — error may occur before entity exists) |
| park_reason | text | YES | people.people_errors.park_reason | Park Reason |
| parked_at | timestamp with  | YES | people.people_errors.parked_at | Timestamp for parked event |
| parked_by | text | YES | people.people_errors.parked_by | Parked By |
| person_id | uuid | YES | people.people_errors.person_id | Person Id |
| raw_payload | jsonb | NO | people.people_errors.raw_payload | Raw Payload |
| retry_after | timestamp with  | YES | people.people_errors.retry_after | Earliest time to retry |
| retry_count | integer | YES | people.people_errors.retry_count | Number of retry attempts so far |
| retry_exhausted | boolean | YES | people.people_errors.retry_exhausted | Retry Exhausted |
| retry_strategy | text | NO | people.people_errors.retry_strategy | How to handle retry (manual_fix, auto_retry, discard) |
| slot_id | uuid | YES | people.people_errors.slot_id | Primary key for this company slot record |
| source_hints_used | jsonb | YES | people.people_errors.source_hints_used | Source Hints Used |
| status | text | NO | people.people_errors.status | Current status of this record |
| ttl_tier | USER-DEFINED | YES | people.people_errors.ttl_tier | Ttl Tier |

### LEAF: people.people_errors_archive (30 columns, 30 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | people.people_errors_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp with  | NO | people.people_errors_archive.archived_at | When this record was archived |
| archived_by | text | YES | people.people_errors_archive.archived_by | Archived By |
| created_at | timestamp with  | YES | people.people_errors_archive.created_at | When this record was created |
| disposition | USER-DEFINED | YES | people.people_errors_archive.disposition | Disposition |
| error_code | character varyi | YES | people.people_errors_archive.error_code | Error Code |
| error_id | uuid | NO | people.people_errors_archive.error_id | Primary key for this error record |
| error_message | text | YES | people.people_errors_archive.error_message | Human-readable error description |
| error_stage | character varyi | YES | people.people_errors_archive.error_stage | Pipeline stage where error occurred |
| error_type | character varyi | YES | people.people_errors_archive.error_type | Discriminator column classifying the error type |
| escalated_at | timestamp with  | YES | people.people_errors_archive.escalated_at | Timestamp for escalated event |
| escalation_level | integer | YES | people.people_errors_archive.escalation_level | Escalation Level |
| final_disposition | USER-DEFINED | YES | people.people_errors_archive.final_disposition | Final Disposition |
| last_retry_at | timestamp with  | YES | people.people_errors_archive.last_retry_at | Timestamp for last retry event |
| last_updated_at | timestamp with  | YES | people.people_errors_archive.last_updated_at | Timestamp for last updated event |
| max_retries | integer | YES | people.people_errors_archive.max_retries | Max Retries |
| outreach_id | uuid | YES | people.people_errors_archive.outreach_id | FK to outreach.outreach spine table (universal join key) |
| park_reason | text | YES | people.people_errors_archive.park_reason | Park Reason |
| parked_at | timestamp with  | YES | people.people_errors_archive.parked_at | Timestamp for parked event |
| parked_by | text | YES | people.people_errors_archive.parked_by | Parked By |
| person_id | uuid | YES | people.people_errors_archive.person_id | Person Id |
| raw_payload | jsonb | YES | people.people_errors_archive.raw_payload | Raw Payload |
| retention_expires_at | timestamp with  | YES | people.people_errors_archive.retention_expires_at | Timestamp for retention expires event |
| retry_count | integer | YES | people.people_errors_archive.retry_count | Number of retry attempts so far |
| retry_exhausted | boolean | YES | people.people_errors_archive.retry_exhausted | Retry Exhausted |
| retry_strategy | character varyi | YES | people.people_errors_archive.retry_strategy | How to handle retry (manual_fix, auto_retry, discard) |
| slot_id | uuid | YES | people.people_errors_archive.slot_id | Primary key for this company slot record |
| source_hints_used | jsonb | YES | people.people_errors_archive.source_hints_used | Source Hints Used |
| status | character varyi | YES | people.people_errors_archive.status | Current status of this record |
| ttl_tier | USER-DEFINED | YES | people.people_errors_archive.ttl_tier | Ttl Tier |

### LEAF: people.people_master (35 columns, 35 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| bio | text | YES | people.people_master.bio | Bio |
| certifications | ARRAY | YES | people.people_master.certifications | Certifications |
| company_slot_unique_id | text | NO | people.people_master.company_slot_unique_id | FK to people.company_slot.slot_id |
| company_unique_id | text | NO | people.people_master.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp with  | YES | people.people_master.created_at | When this record was created |
| department | text | YES | people.people_master.department | Department |
| education | text | YES | people.people_master.education | Education |
| email | text | YES | people.people_master.email | Person email address |
| email_verification_source | text | YES | people.people_master.email_verification_source | Email Verification Source |
| email_verified | boolean | YES | people.people_master.email_verified | Whether email was checked via Million Verifier (TRUE = checked) |
| email_verified_at | timestamp with  | YES | people.people_master.email_verified_at | Timestamp for email verified event |
| facebook_url | text | YES | people.people_master.facebook_url | Facebook URL |
| first_name | text | NO | people.people_master.first_name | Person first name from Hunter, Clay, or manual enrichment |
| full_name | text | YES | people.people_master.full_name | Full Name |
| is_decision_maker | boolean | YES | people.people_master.is_decision_maker | Whether this record decision maker |
| last_enrichment_attempt | timestamp witho | YES | people.people_master.last_enrichment_attempt | Last Enrichment Attempt |
| last_name | text | NO | people.people_master.last_name | Person last name from Hunter, Clay, or manual enrichment |
| last_verified_at | timestamp witho | NO | people.people_master.last_verified_at | Timestamp for last verified event |
| linkedin_url | text | YES | people.people_master.linkedin_url | Person LinkedIn profile URL |
| message_key_scheduled | text | YES | people.people_master.message_key_scheduled | Message Key Scheduled |
| outreach_ready | boolean | YES | people.people_master.outreach_ready | Whether email is safe to send outreach (TRUE = VALID verified) |
| outreach_ready_at | timestamp with  | YES | people.people_master.outreach_ready_at | Timestamp for outreach ready event |
| personal_phone_e164 | text | YES | people.people_master.personal_phone_e164 | Personal Phone E164 |
| promoted_from_intake_at | timestamp with  | NO | people.people_master.promoted_from_intake_at | Timestamp for promoted from intake event |
| promotion_audit_log_id | integer | YES | people.people_master.promotion_audit_log_id | Promotion Audit Log Id |
| seniority | text | YES | people.people_master.seniority | Seniority |
| skills | ARRAY | YES | people.people_master.skills | Skills |
| source_record_id | text | YES | people.people_master.source_record_id | Source Record Id |
| source_system | text | NO | people.people_master.source_system | System that originated this record |
| title | text | YES | people.people_master.title | Job title or position |
| twitter_url | text | YES | people.people_master.twitter_url | Twitter URL |
| unique_id | text | NO | people.people_master.unique_id | Barton person identifier (04.04.02.YY.NNNNNN.NNN format, immutable) |
| updated_at | timestamp with  | YES | people.people_master.updated_at | When this record was last updated |
| validation_status | character varyi | YES | people.people_master.validation_status | Validation Status |
| work_phone_e164 | text | YES | people.people_master.work_phone_e164 | Phone number (E.164 format preferred) |

### LEAF: people.people_master_archive (35 columns, 35 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| archive_reason | text | YES | people.people_master_archive.archive_reason | Reason this record was archived |
| archived_at | timestamp witho | NO | people.people_master_archive.archived_at | When this record was archived |
| bio | text | YES | people.people_master_archive.bio | Bio |
| certifications | ARRAY | YES | people.people_master_archive.certifications | Certifications |
| company_slot_unique_id | text | YES | people.people_master_archive.company_slot_unique_i | FK to people.company_slot.slot_id |
| company_unique_id | text | YES | people.people_master_archive.company_unique_id | FK to cl.company_identity or Barton company ID |
| created_at | timestamp witho | YES | people.people_master_archive.created_at | When this record was created |
| department | text | YES | people.people_master_archive.department | Department |
| education | text | YES | people.people_master_archive.education | Education |
| email | text | YES | people.people_master_archive.email | Email address |
| email_verification_source | text | YES | people.people_master_archive.email_verification_so | Email Verification Source |
| email_verified | boolean | YES | people.people_master_archive.email_verified | Whether email was verified via Million Verifier |
| email_verified_at | timestamp witho | YES | people.people_master_archive.email_verified_at | Timestamp for email verified event |
| facebook_url | text | YES | people.people_master_archive.facebook_url | Facebook URL |
| first_name | text | YES | people.people_master_archive.first_name | Person first name |
| full_name | text | YES | people.people_master_archive.full_name | Full Name |
| is_decision_maker | boolean | YES | people.people_master_archive.is_decision_maker | Whether this record decision maker |
| last_enrichment_attempt | timestamp witho | YES | people.people_master_archive.last_enrichment_attem | Last Enrichment Attempt |
| last_name | text | YES | people.people_master_archive.last_name | Person last name |
| last_verified_at | timestamp witho | YES | people.people_master_archive.last_verified_at | Timestamp for last verified event |
| linkedin_url | text | YES | people.people_master_archive.linkedin_url | LinkedIn profile URL |
| message_key_scheduled | text | YES | people.people_master_archive.message_key_scheduled | Message Key Scheduled |
| personal_phone_e164 | text | YES | people.people_master_archive.personal_phone_e164 | Personal Phone E164 |
| promoted_from_intake_at | timestamp witho | YES | people.people_master_archive.promoted_from_intake_ | Timestamp for promoted from intake event |
| promotion_audit_log_id | integer | YES | people.people_master_archive.promotion_audit_log_i | Promotion Audit Log Id |
| seniority | text | YES | people.people_master_archive.seniority | Seniority |
| skills | ARRAY | YES | people.people_master_archive.skills | Skills |
| source_record_id | text | YES | people.people_master_archive.source_record_id | Source Record Id |
| source_system | text | YES | people.people_master_archive.source_system | System that originated this record |
| title | text | YES | people.people_master_archive.title | Job title or position |
| twitter_url | text | YES | people.people_master_archive.twitter_url | Twitter URL |
| unique_id | text | YES | people.people_master_archive.unique_id | Primary identifier for this record (Barton ID format) |
| updated_at | timestamp witho | YES | people.people_master_archive.updated_at | When this record was last updated |
| validation_status | character varyi | YES | people.people_master_archive.validation_status | Validation Status |
| work_phone_e164 | text | YES | people.people_master_archive.work_phone_e164 | Phone number (E.164 format preferred) |

### LEAF: people.slot_assignment_history (15 columns, 15 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_slot_unique_id | text | NO | people.slot_assignment_history.company_slot_unique | FK to people.company_slot.slot_id |
| company_unique_id | text | NO | people.slot_assignment_history.company_unique_id | FK to cl.company_identity or Barton company ID |
| confidence_score | numeric | YES | people.slot_assignment_history.confidence_score | Confidence score (0-100) |
| created_at | timestamp with  | NO | people.slot_assignment_history.created_at | When this record was created |
| displaced_by_person_id | text | YES | people.slot_assignment_history.displaced_by_person | Displaced By Person Id |
| displacement_reason | text | YES | people.slot_assignment_history.displacement_reason | Displacement Reason |
| event_metadata | jsonb | NO | people.slot_assignment_history.event_metadata | Event Metadata |
| event_ts | timestamp with  | NO | people.slot_assignment_history.event_ts | Event Ts |
| event_type | text | NO | people.slot_assignment_history.event_type | Type of audit/system event |
| history_id | bigint | NO | people.slot_assignment_history.history_id | History Id |
| original_filled_at | timestamp with  | YES | people.slot_assignment_history.original_filled_at | Timestamp for original filled event |
| person_unique_id | text | YES | people.slot_assignment_history.person_unique_id | FK to people.people_master.unique_id (Barton person ID) |
| slot_type | text | NO | people.slot_assignment_history.slot_type | Executive role type (CEO, CFO, HR, CTO, CMO, COO) |
| source_system | text | NO | people.slot_assignment_history.source_system | System that originated this record |
| tenure_days | integer | YES | people.slot_assignment_history.tenure_days | Tenure Days |

### LEAF: people.slot_ingress_control (9 columns, 9 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | people.slot_ingress_control.created_at | When this record was created |
| description | text | YES | people.slot_ingress_control.description | Description |
| disabled_at | timestamp with  | YES | people.slot_ingress_control.disabled_at | Timestamp for disabled event |
| disabled_by | character varyi | YES | people.slot_ingress_control.disabled_by | Disabled By |
| enabled_at | timestamp with  | YES | people.slot_ingress_control.enabled_at | Timestamp for enabled event |
| enabled_by | character varyi | YES | people.slot_ingress_control.enabled_by | Enabled By |
| is_enabled | boolean | NO | people.slot_ingress_control.is_enabled | Whether this record enabled |
| switch_id | uuid | NO | people.slot_ingress_control.switch_id | Switch Id |
| switch_name | character varyi | NO | people.slot_ingress_control.switch_name | Switch Name |

### LEAF: people.slot_orphan_snapshot_r0_002 (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_slot_unique_id | text | NO | people.slot_orphan_snapshot_r0_002.company_slot_un | FK to people.company_slot.slot_id |
| company_unique_id | text | NO | people.slot_orphan_snapshot_r0_002.company_unique_ | FK to cl.company_identity or Barton company ID |
| derivation_status | text | YES | people.slot_orphan_snapshot_r0_002.derivation_stat | Derivation Status |
| derived_outreach_id | uuid | YES | people.slot_orphan_snapshot_r0_002.derived_outreac | Derived Outreach Id |
| original_outreach_id | uuid | YES | people.slot_orphan_snapshot_r0_002.original_outrea | Original Outreach Id |
| slot_type | text | NO | people.slot_orphan_snapshot_r0_002.slot_type | Executive role type (CEO, CFO, HR, CTO, CMO, COO) |
| snapshot_at | timestamp with  | YES | people.slot_orphan_snapshot_r0_002.snapshot_at | Timestamp for snapshot event |
| snapshot_id | integer | NO | people.slot_orphan_snapshot_r0_002.snapshot_id | Snapshot Id |

### LEAF: people.slot_quarantine_r0_002 (6 columns, 6 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_slot_unique_id | text | NO | people.slot_quarantine_r0_002.company_slot_unique_ | FK to people.company_slot.slot_id |
| company_unique_id | text | NO | people.slot_quarantine_r0_002.company_unique_id | FK to cl.company_identity or Barton company ID |
| quarantine_id | integer | NO | people.slot_quarantine_r0_002.quarantine_id | Quarantine Id |
| quarantine_reason | text | NO | people.slot_quarantine_r0_002.quarantine_reason | Quarantine Reason |
| quarantined_at | timestamp with  | YES | people.slot_quarantine_r0_002.quarantined_at | Timestamp for quarantined event |
| slot_type | text | NO | people.slot_quarantine_r0_002.slot_type | Executive role type (CEO, CFO, HR, CTO, CMO, COO) |

### LEAF: people.title_slot_mapping (5 columns, 5 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp witho | YES | people.title_slot_mapping.created_at | When this record was created |
| id | integer | NO | people.title_slot_mapping.id | Id |
| priority | integer | YES | people.title_slot_mapping.priority | Priority |
| slot_type | character varyi | NO | people.title_slot_mapping.slot_type | Executive role type (CEO, CFO, HR, CTO, CMO, COO) |
| title_pattern | character varyi | NO | people.title_slot_mapping.title_pattern | Title Pattern |

### LEAF: people.v_linkedin_monitor_list (9 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_name | text | YES | people.v_linkedin_monitor_list.agent_name | _undocumented_ |
| agent_number | text | YES | people.v_linkedin_monitor_list.agent_number | _undocumented_ |
| company_unique_id | text | YES | people.v_linkedin_monitor_list.company_unique_id | _undocumented_ |
| full_name | text | YES | people.v_linkedin_monitor_list.full_name | _undocumented_ |
| linkedin_url | text | YES | people.v_linkedin_monitor_list.linkedin_url | _undocumented_ |
| outreach_id | uuid | YES | people.v_linkedin_monitor_list.outreach_id | _undocumented_ |
| person_id | text | YES | people.v_linkedin_monitor_list.person_id | _undocumented_ |
| slot_type | text | YES | people.v_linkedin_monitor_list.slot_type | _undocumented_ |
| title | text | YES | people.v_linkedin_monitor_list.title | _undocumented_ |

### LEAF: people.v_linkedin_movement (12 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | YES | people.v_linkedin_movement.company_unique_id | _undocumented_ |
| current_company | text | YES | people.v_linkedin_movement.current_company | _undocumented_ |
| current_month | date | YES | people.v_linkedin_movement.current_month | _undocumented_ |
| current_title | text | YES | people.v_linkedin_movement.current_title | _undocumented_ |
| last_post_date | timestamp with  | YES | people.v_linkedin_movement.last_post_date | _undocumented_ |
| movement_detected | boolean | YES | people.v_linkedin_movement.movement_detected | _undocumented_ |
| movement_type | text | YES | people.v_linkedin_movement.movement_type | _undocumented_ |
| parsed_name | text | YES | people.v_linkedin_movement.parsed_name | _undocumented_ |
| person_id | text | YES | people.v_linkedin_movement.person_id | _undocumented_ |
| previous_company | text | YES | people.v_linkedin_movement.previous_company | _undocumented_ |
| previous_month | date | YES | people.v_linkedin_movement.previous_month | _undocumented_ |
| previous_title | text | YES | people.v_linkedin_movement.previous_title | _undocumented_ |

### LEAF: people.v_slot_tenure_summary (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | YES | people.v_slot_tenure_summary.company_unique_id | _undocumented_ |
| confidence_score | numeric | YES | people.v_slot_tenure_summary.confidence_score | _undocumented_ |
| displaced_by_person_id | text | YES | people.v_slot_tenure_summary.displaced_by_person_i | _undocumented_ |
| displacement_reason | text | YES | people.v_slot_tenure_summary.displacement_reason | _undocumented_ |
| event_timestamp | timestamp with  | YES | people.v_slot_tenure_summary.event_timestamp | _undocumented_ |
| event_type | text | YES | people.v_slot_tenure_summary.event_type | _undocumented_ |
| original_filled_at | timestamp with  | YES | people.v_slot_tenure_summary.original_filled_at | _undocumented_ |
| person_unique_id | text | YES | people.v_slot_tenure_summary.person_unique_id | _undocumented_ |
| slot_type | text | YES | people.v_slot_tenure_summary.slot_type | _undocumented_ |
| source_system | text | YES | people.v_slot_tenure_summary.source_system | _undocumented_ |
| tenure_days | integer | YES | people.v_slot_tenure_summary.tenure_days | _undocumented_ |

### LEAF: people.v_staging_summary (4 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| avg_confidence | numeric | YES | people.v_staging_summary.avg_confidence | _undocumented_ |
| count | bigint | YES | people.v_staging_summary.count | _undocumented_ |
| mapped_slot_type | character varyi | YES | people.v_staging_summary.mapped_slot_type | _undocumented_ |
| status | character varyi | YES | people.v_staging_summary.status | _undocumented_ |

### LEAF: people.v_territory_companies (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_name | text | YES | people.v_territory_companies.agent_name | _undocumented_ |
| agent_number | text | YES | people.v_territory_companies.agent_number | _undocumented_ |
| city | character varyi | YES | people.v_territory_companies.city | _undocumented_ |
| company_unique_id | text | YES | people.v_territory_companies.company_unique_id | _undocumented_ |
| employees | integer | YES | people.v_territory_companies.employees | _undocumented_ |
| industry | character varyi | YES | people.v_territory_companies.industry | _undocumented_ |
| outreach_id | uuid | YES | people.v_territory_companies.outreach_id | _undocumented_ |
| postal_code | character varyi | YES | people.v_territory_companies.postal_code | _undocumented_ |
| service_agent_id | uuid | YES | people.v_territory_companies.service_agent_id | _undocumented_ |
| state | character varyi | YES | people.v_territory_companies.state | _undocumented_ |

### LEAF: people.v_territory_people (16 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_name | text | YES | people.v_territory_people.agent_name | _undocumented_ |
| agent_number | text | YES | people.v_territory_people.agent_number | _undocumented_ |
| company_unique_id | text | YES | people.v_territory_people.company_unique_id | _undocumented_ |
| email | text | YES | people.v_territory_people.email | _undocumented_ |
| email_verified | boolean | YES | people.v_territory_people.email_verified | _undocumented_ |
| full_name | text | YES | people.v_territory_people.full_name | _undocumented_ |
| is_decision_maker | boolean | YES | people.v_territory_people.is_decision_maker | _undocumented_ |
| linkedin_url | text | YES | people.v_territory_people.linkedin_url | _undocumented_ |
| outreach_id | uuid | YES | people.v_territory_people.outreach_id | _undocumented_ |
| outreach_ready | boolean | YES | people.v_territory_people.outreach_ready | _undocumented_ |
| person_id | text | YES | people.v_territory_people.person_id | _undocumented_ |
| service_agent_id | uuid | YES | people.v_territory_people.service_agent_id | _undocumented_ |
| slot_id | uuid | YES | people.v_territory_people.slot_id | _undocumented_ |
| slot_type | text | YES | people.v_territory_people.slot_type | _undocumented_ |
| source_system | text | YES | people.v_territory_people.source_system | _undocumented_ |
| title | text | YES | people.v_territory_people.title | _undocumented_ |

### LEAF: people.v_territory_slots (12 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_name | text | YES | people.v_territory_slots.agent_name | _undocumented_ |
| agent_number | text | YES | people.v_territory_slots.agent_number | _undocumented_ |
| company_unique_id | text | YES | people.v_territory_slots.company_unique_id | _undocumented_ |
| confidence_score | numeric | YES | people.v_territory_slots.confidence_score | _undocumented_ |
| filled_at | timestamp with  | YES | people.v_territory_slots.filled_at | _undocumented_ |
| is_filled | boolean | YES | people.v_territory_slots.is_filled | _undocumented_ |
| outreach_id | uuid | YES | people.v_territory_slots.outreach_id | _undocumented_ |
| person_unique_id | text | YES | people.v_territory_slots.person_unique_id | _undocumented_ |
| service_agent_id | uuid | YES | people.v_territory_slots.service_agent_id | _undocumented_ |
| slot_id | uuid | YES | people.v_territory_slots.slot_id | _undocumented_ |
| slot_type | text | YES | people.v_territory_slots.slot_type | _undocumented_ |
| source_system | text | YES | people.v_territory_slots.source_system | _undocumented_ |

### LEAF: people.v_territory_summary (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_name | text | YES | people.v_territory_summary.agent_name | _undocumented_ |
| agent_number | text | YES | people.v_territory_summary.agent_number | _undocumented_ |
| companies_with_slots | bigint | YES | people.v_territory_summary.companies_with_slots | _undocumented_ |
| empty_or_missing_slots | bigint | YES | people.v_territory_summary.empty_or_missing_slots | _undocumented_ |
| filled_slots | bigint | YES | people.v_territory_summary.filled_slots | _undocumented_ |
| total_companies | bigint | YES | people.v_territory_summary.total_companies | _undocumented_ |
| total_slot_positions | bigint | YES | people.v_territory_summary.total_slot_positions | _undocumented_ |

### LEAF: people.vw_profile_monitoring (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| assignment_status | text | YES | people.vw_profile_monitoring.assignment_status | _undocumented_ |
| contact_id | bigint | YES | people.vw_profile_monitoring.contact_id | _undocumented_ |
| email | text | YES | people.vw_profile_monitoring.email | _undocumented_ |
| email_checked_at | timestamp with  | YES | people.vw_profile_monitoring.email_checked_at | _undocumented_ |
| email_status | text | YES | people.vw_profile_monitoring.email_status | _undocumented_ |
| email_verification_status | text | YES | people.vw_profile_monitoring.email_verification_st | _undocumented_ |
| full_name | text | YES | people.vw_profile_monitoring.full_name | _undocumented_ |
| last_profile_checked_at | timestamp with  | YES | people.vw_profile_monitoring.last_profile_checked_ | _undocumented_ |
| profile_source_url | text | YES | people.vw_profile_monitoring.profile_source_url | _undocumented_ |
| profile_status | text | YES | people.vw_profile_monitoring.profile_status | _undocumented_ |

### LEAF: people.vw_profile_staleness (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| contact_id | bigint | YES | people.vw_profile_staleness.contact_id | _undocumented_ |
| email | text | YES | people.vw_profile_staleness.email | _undocumented_ |
| email_source_url | text | YES | people.vw_profile_staleness.email_source_url | _undocumented_ |
| email_status | text | YES | people.vw_profile_staleness.email_status | _undocumented_ |
| full_name | text | YES | people.vw_profile_staleness.full_name | _undocumented_ |
| profile_source_url | text | YES | people.vw_profile_staleness.profile_source_url | _undocumented_ |
| profile_status | text | YES | people.vw_profile_staleness.profile_status | _undocumented_ |

---

## BRANCH: public (6 tables, 35 columns, 83% documented)

### LEAF: public.due_email_recheck_30d (2 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| contact_id | bigint | YES | public.due_email_recheck_30d.contact_id | _undocumented_ |
| email | text | YES | public.due_email_recheck_30d.email | _undocumented_ |

### LEAF: public.garage_runs (14 columns, 14 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| bay_a_count | integer | YES | public.garage_runs.bay_a_count | Count of records with missing fields (sent to Bay A agents) |
| bay_b_count | integer | YES | public.garage_runs.bay_b_count | Count of records with contradictions (sent to Bay B agents) |
| chronic_bad_count | integer | YES | public.garage_runs.chronic_bad_count | Count of records with 2+ failed enrichment attempts |
| created_at | timestamp witho | YES | public.garage_runs.created_at | Timestamp when this record was created. |
| promoted_count | integer | YES | public.garage_runs.promoted_count | Count of promoted. |
| record_type | character varyi | YES | public.garage_runs.record_type | Classification type for record. |
| run_completed_at | timestamp witho | YES | public.garage_runs.run_completed_at | Timestamp when run completed occurred. |
| run_id | integer | NO | public.garage_runs.run_id | ID of the pipeline run that processed this record. |
| run_mode | character varyi | YES | public.garage_runs.run_mode | Run mode. May be NULL. |
| run_started_at | timestamp witho | NO | public.garage_runs.run_started_at | Timestamp when run started occurred. |
| run_status | character varyi | NO | public.garage_runs.run_status | Status of run. |
| snapshot_version | character varyi | NO | public.garage_runs.snapshot_version | Timestamp-based snapshot identifier (YYYYMMDDHHMMSS) |
| total_records_processed | integer | YES | public.garage_runs.total_records_processed | Total records processed. May be NULL. |
| updated_at | timestamp witho | YES | public.garage_runs.updated_at | Timestamp of last modification to this record. |

### LEAF: public.migration_log (6 columns, 6 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| details | text | YES | public.migration_log.details | Event or error details. |
| executed_at | timestamp witho | YES | public.migration_log.executed_at | Timestamp when executed occurred. |
| id | integer | NO | public.migration_log.id | Id. |
| migration_name | character varyi | YES | public.migration_log.migration_name | Name of migration. |
| status | character varyi | YES | public.migration_log.status | Current status of this record. |
| step | character varyi | YES | public.migration_log.step | Step. May be NULL. |

### LEAF: public.next_company_urls_30d (2 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_id | bigint | YES | public.next_company_urls_30d.company_id | _undocumented_ |
| website_url | text | YES | public.next_company_urls_30d.website_url | _undocumented_ |

### LEAF: public.next_profile_urls_30d (2 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| contact_id | bigint | YES | public.next_profile_urls_30d.contact_id | _undocumented_ |
| email | text | YES | public.next_profile_urls_30d.email | _undocumented_ |

### LEAF: public.shq_validation_log (9 columns, 9 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| executed_at | timestamp with  | YES | public.shq_validation_log.executed_at | Timestamp when executed occurred. |
| executed_by | text | YES | public.shq_validation_log.executed_by | Executed by. May be NULL. |
| failed_records | integer | YES | public.shq_validation_log.failed_records | Failed records. May be NULL. |
| notes | text | YES | public.shq_validation_log.notes | Free text notes. |
| passed_records | integer | YES | public.shq_validation_log.passed_records | Passed records. May be NULL. |
| source_table | text | NO | public.shq_validation_log.source_table | Source data field: source_table. |
| target_table | text | NO | public.shq_validation_log.target_table | Target table. |
| total_records | integer | YES | public.shq_validation_log.total_records | Total records. May be NULL. |
| validation_run_id | text | NO | public.shq_validation_log.validation_run_id | Identifier for validation run. |

---

## BRANCH: ref (2 tables, 13 columns, 100% documented)

### LEAF: ref.county_fips (8 columns, 8 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| county_code | character | NO | ref.county_fips.county_code | County Code |
| county_fips | character | NO | ref.county_fips.county_fips | County Fips |
| county_name | text | NO | ref.county_fips.county_name | County Name |
| created_at | timestamp witho | YES | ref.county_fips.created_at | When this record was created |
| source | text | YES | ref.county_fips.source | Data source identifier |
| source_year | integer | NO | ref.county_fips.source_year | Source Year |
| state_fips | character | NO | ref.county_fips.state_fips | State Fips |
| state_name | text | NO | ref.county_fips.state_name | State Name |

### LEAF: ref.zip_county_map (5 columns, 5 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| county_fips | character | NO | ref.zip_county_map.county_fips | County Fips |
| created_at | timestamp witho | YES | ref.zip_county_map.created_at | When this record was created |
| is_primary | boolean | YES | ref.zip_county_map.is_primary | Whether this record primary |
| source | text | YES | ref.zip_county_map.source | Data source identifier |
| zip | character | NO | ref.zip_county_map.zip | ZIP/postal code (5-digit) |

---

## BRANCH: reference (1 tables, 39 columns, 100% documented)

### LEAF: reference.us_zip_codes (39 columns, 39 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| age_median | numeric | YES | reference.us_zip_codes.age_median | Age Median |
| city | text | YES | reference.us_zip_codes.city | City name |
| county_fips | text | YES | reference.us_zip_codes.county_fips | County Fips |
| county_fips_all | text | YES | reference.us_zip_codes.county_fips_all | County Fips All |
| county_name | text | YES | reference.us_zip_codes.county_name | County Name |
| county_names_all | text | YES | reference.us_zip_codes.county_names_all | County Names All |
| county_weights | jsonb | YES | reference.us_zip_codes.county_weights | County Weights |
| created_at | timestamp with  | YES | reference.us_zip_codes.created_at | When this record was created |
| density | numeric | YES | reference.us_zip_codes.density | Density |
| education_college_or_above | numeric | YES | reference.us_zip_codes.education_college_or_above | Education College Or Above |
| family_size | numeric | YES | reference.us_zip_codes.family_size | Family Size |
| female | numeric | YES | reference.us_zip_codes.female | Female |
| home_ownership | numeric | YES | reference.us_zip_codes.home_ownership | Home Ownership |
| home_value | integer | YES | reference.us_zip_codes.home_value | Home Value |
| imprecise | boolean | YES | reference.us_zip_codes.imprecise | Imprecise |
| income_household_median | integer | YES | reference.us_zip_codes.income_household_median | Income Household Median |
| income_household_six_figure | numeric | YES | reference.us_zip_codes.income_household_six_figure | Income Household Six Figure |
| labor_force_participation | numeric | YES | reference.us_zip_codes.labor_force_participation | Labor Force Participation |
| lat | numeric | YES | reference.us_zip_codes.lat | Lat |
| lng | numeric | YES | reference.us_zip_codes.lng | Lng |
| male | numeric | YES | reference.us_zip_codes.male | Male |
| married | numeric | YES | reference.us_zip_codes.married | Married |
| military | boolean | YES | reference.us_zip_codes.military | Military |
| parent_zcta | text | YES | reference.us_zip_codes.parent_zcta | Parent Zcta |
| population | integer | YES | reference.us_zip_codes.population | Population |
| race_asian | numeric | YES | reference.us_zip_codes.race_asian | Race Asian |
| race_black | numeric | YES | reference.us_zip_codes.race_black | Race Black |
| race_multiple | numeric | YES | reference.us_zip_codes.race_multiple | Race Multiple |
| race_native | numeric | YES | reference.us_zip_codes.race_native | Race Native |
| race_other | numeric | YES | reference.us_zip_codes.race_other | Race Other |
| race_pacific | numeric | YES | reference.us_zip_codes.race_pacific | Race Pacific |
| race_white | numeric | YES | reference.us_zip_codes.race_white | Race White |
| rent_median | integer | YES | reference.us_zip_codes.rent_median | Rent Median |
| state_id | text | YES | reference.us_zip_codes.state_id | US state code (2-letter) |
| state_name | text | YES | reference.us_zip_codes.state_name | State Name |
| timezone | text | YES | reference.us_zip_codes.timezone | Timezone |
| unemployment_rate | numeric | YES | reference.us_zip_codes.unemployment_rate | Unemployment Rate |
| zcta | boolean | YES | reference.us_zip_codes.zcta | Zcta |
| zip | text | NO | reference.us_zip_codes.zip | ZIP/postal code (5-digit) |

---

## BRANCH: sales (3 tables, 31 columns, 39% documented)

### LEAF: sales.appointments_already_had (12 columns, 12 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| appointment_uid | text | NO | sales.appointments_already_had.appointment_uid | Appointment Uid |
| company_id | uuid | YES | sales.appointments_already_had.company_id | Company Id |
| created_at | timestamp with  | NO | sales.appointments_already_had.created_at | When this record was created |
| meeting_date | date | NO | sales.appointments_already_had.meeting_date | Meeting Date |
| meeting_outcome | USER-DEFINED | NO | sales.appointments_already_had.meeting_outcome | Meeting Outcome |
| meeting_type | USER-DEFINED | NO | sales.appointments_already_had.meeting_type | Meeting Type |
| metadata | jsonb | YES | sales.appointments_already_had.metadata | Metadata |
| outreach_id | uuid | YES | sales.appointments_already_had.outreach_id | FK to outreach.outreach spine table (universal join key) |
| people_id | uuid | YES | sales.appointments_already_had.people_id | People Id |
| source | USER-DEFINED | NO | sales.appointments_already_had.source | Data source identifier |
| source_record_id | text | YES | sales.appointments_already_had.source_record_id | Source Record Id |
| stalled_reason | text | YES | sales.appointments_already_had.stalled_reason | Stalled Reason |

### LEAF: sales.sales_state (9 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | NO | sales.sales_state.created_at | _undocumented_ |
| current_phase | text | NO | sales.sales_state.current_phase | _undocumented_ |
| domicile_state | text | YES | sales.sales_state.domicile_state | _undocumented_ |
| legal_name | text | NO | sales.sales_state.legal_name | _undocumented_ |
| sales_id | uuid | NO | sales.sales_state.sales_id | _undocumented_ |
| source | text | YES | sales.sales_state.source | _undocumented_ |
| status | text | NO | sales.sales_state.status | _undocumented_ |
| updated_at | timestamp with  | NO | sales.sales_state.updated_at | _undocumented_ |
| version | integer | NO | sales.sales_state.version | _undocumented_ |

### LEAF: sales.sales_state_error (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| context | jsonb | YES | sales.sales_state_error.context | _undocumented_ |
| created_at | timestamp with  | NO | sales.sales_state_error.created_at | _undocumented_ |
| error_code | text | NO | sales.sales_state_error.error_code | _undocumented_ |
| error_message | text | NO | sales.sales_state_error.error_message | _undocumented_ |
| sales_id | uuid | YES | sales.sales_state_error.sales_id | _undocumented_ |
| sales_state_error_id | uuid | NO | sales.sales_state_error.sales_state_error_id | _undocumented_ |
| severity | text | NO | sales.sales_state_error.severity | _undocumented_ |
| source_entity | text | NO | sales.sales_state_error.source_entity | _undocumented_ |
| source_id | uuid | YES | sales.sales_state_error.source_id | _undocumented_ |
| status | text | NO | sales.sales_state_error.status | _undocumented_ |

---

## BRANCH: seed_views (6 tables, 109 columns, 0% documented)

### LEAF: seed_views.v_agent_cl_identity (37 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| canonical_name | text | YES | seed_views.v_agent_cl_identity.canonical_name | _undocumented_ |
| client_id | uuid | YES | seed_views.v_agent_cl_identity.client_id | _undocumented_ |
| client_promoted_at | timestamp with  | YES | seed_views.v_agent_cl_identity.client_promoted_at | _undocumented_ |
| company_domain | text | YES | seed_views.v_agent_cl_identity.company_domain | _undocumented_ |
| company_fingerprint | text | YES | seed_views.v_agent_cl_identity.company_fingerprint | _undocumented_ |
| company_name | text | YES | seed_views.v_agent_cl_identity.company_name | _undocumented_ |
| company_unique_id | uuid | YES | seed_views.v_agent_cl_identity.company_unique_id | _undocumented_ |
| created_at | timestamp with  | YES | seed_views.v_agent_cl_identity.created_at | _undocumented_ |
| domain_status_code | integer | YES | seed_views.v_agent_cl_identity.domain_status_code | _undocumented_ |
| eligibility_status | text | YES | seed_views.v_agent_cl_identity.eligibility_status | _undocumented_ |
| employee_count_band | text | YES | seed_views.v_agent_cl_identity.employee_count_band | _undocumented_ |
| entity_role | text | YES | seed_views.v_agent_cl_identity.entity_role | _undocumented_ |
| exclusion_reason | text | YES | seed_views.v_agent_cl_identity.exclusion_reason | _undocumented_ |
| existence_verified | boolean | YES | seed_views.v_agent_cl_identity.existence_verified | _undocumented_ |
| final_outcome | text | YES | seed_views.v_agent_cl_identity.final_outcome | _undocumented_ |
| final_reason | text | YES | seed_views.v_agent_cl_identity.final_reason | _undocumented_ |
| identity_pass | integer | YES | seed_views.v_agent_cl_identity.identity_pass | _undocumented_ |
| identity_status | text | YES | seed_views.v_agent_cl_identity.identity_status | _undocumented_ |
| last_pass_at | timestamp with  | YES | seed_views.v_agent_cl_identity.last_pass_at | _undocumented_ |
| lcs_attached_at | timestamp with  | YES | seed_views.v_agent_cl_identity.lcs_attached_at | _undocumented_ |
| lcs_id | uuid | YES | seed_views.v_agent_cl_identity.lcs_id | _undocumented_ |
| lifecycle_run_id | text | YES | seed_views.v_agent_cl_identity.lifecycle_run_id | _undocumented_ |
| linkedin_company_url | text | YES | seed_views.v_agent_cl_identity.linkedin_company_ur | _undocumented_ |
| name_match_score | integer | YES | seed_views.v_agent_cl_identity.name_match_score | _undocumented_ |
| normalized_domain | text | YES | seed_views.v_agent_cl_identity.normalized_domain | _undocumented_ |
| outreach_attached_at | timestamp with  | YES | seed_views.v_agent_cl_identity.outreach_attached_a | _undocumented_ |
| outreach_id | uuid | YES | seed_views.v_agent_cl_identity.outreach_id | _undocumented_ |
| sales_opened_at | timestamp with  | YES | seed_views.v_agent_cl_identity.sales_opened_at | _undocumented_ |
| sales_process_id | uuid | YES | seed_views.v_agent_cl_identity.sales_process_id | _undocumented_ |
| source_system | text | YES | seed_views.v_agent_cl_identity.source_system | _undocumented_ |
| sovereign_company_id | uuid | YES | seed_views.v_agent_cl_identity.sovereign_company_i | _undocumented_ |
| state_code | character | YES | seed_views.v_agent_cl_identity.state_code | _undocumented_ |
| state_match_result | text | YES | seed_views.v_agent_cl_identity.state_match_result | _undocumented_ |
| state_verified | text | YES | seed_views.v_agent_cl_identity.state_verified | _undocumented_ |
| updated_at | timestamp with  | YES | seed_views.v_agent_cl_identity.updated_at | _undocumented_ |
| verification_run_id | text | YES | seed_views.v_agent_cl_identity.verification_run_id | _undocumented_ |
| verified_at | timestamp with  | YES | seed_views.v_agent_cl_identity.verified_at | _undocumented_ |

### LEAF: seed_views.v_agent_companies (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| city | character varyi | YES | seed_views.v_agent_companies.city | _undocumented_ |
| company_unique_id | text | YES | seed_views.v_agent_companies.company_unique_id | _undocumented_ |
| email_method | character varyi | YES | seed_views.v_agent_companies.email_method | _undocumented_ |
| employees | integer | YES | seed_views.v_agent_companies.employees | _undocumented_ |
| industry | character varyi | YES | seed_views.v_agent_companies.industry | _undocumented_ |
| outreach_id | uuid | YES | seed_views.v_agent_companies.outreach_id | _undocumented_ |
| postal_code | character varyi | YES | seed_views.v_agent_companies.postal_code | _undocumented_ |
| state | character varyi | YES | seed_views.v_agent_companies.state | _undocumented_ |

### LEAF: seed_views.v_agent_dol (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| broker_or_advisor | text | YES | seed_views.v_agent_dol.broker_or_advisor | _undocumented_ |
| carrier | text | YES | seed_views.v_agent_dol.carrier | _undocumented_ |
| created_at | timestamp with  | YES | seed_views.v_agent_dol.created_at | _undocumented_ |
| dol_id | uuid | YES | seed_views.v_agent_dol.dol_id | _undocumented_ |
| ein | text | YES | seed_views.v_agent_dol.ein | _undocumented_ |
| filing_present | boolean | YES | seed_views.v_agent_dol.filing_present | _undocumented_ |
| funding_type | text | YES | seed_views.v_agent_dol.funding_type | _undocumented_ |
| outreach_id | uuid | YES | seed_views.v_agent_dol.outreach_id | _undocumented_ |
| outreach_start_month | integer | YES | seed_views.v_agent_dol.outreach_start_month | _undocumented_ |
| renewal_month | integer | YES | seed_views.v_agent_dol.renewal_month | _undocumented_ |
| updated_at | timestamp with  | YES | seed_views.v_agent_dol.updated_at | _undocumented_ |

### LEAF: seed_views.v_agent_outreach (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp with  | YES | seed_views.v_agent_outreach.created_at | _undocumented_ |
| domain | character varyi | YES | seed_views.v_agent_outreach.domain | _undocumented_ |
| ein | character varyi | YES | seed_views.v_agent_outreach.ein | _undocumented_ |
| has_appointment | boolean | YES | seed_views.v_agent_outreach.has_appointment | _undocumented_ |
| outreach_id | uuid | YES | seed_views.v_agent_outreach.outreach_id | _undocumented_ |
| sovereign_id | uuid | YES | seed_views.v_agent_outreach.sovereign_id | _undocumented_ |
| updated_at | timestamp with  | YES | seed_views.v_agent_outreach.updated_at | _undocumented_ |

### LEAF: seed_views.v_agent_people (35 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| bio | text | YES | seed_views.v_agent_people.bio | _undocumented_ |
| certifications | ARRAY | YES | seed_views.v_agent_people.certifications | _undocumented_ |
| company_slot_unique_id | text | YES | seed_views.v_agent_people.company_slot_unique_id | _undocumented_ |
| company_unique_id | text | YES | seed_views.v_agent_people.company_unique_id | _undocumented_ |
| created_at | timestamp with  | YES | seed_views.v_agent_people.created_at | _undocumented_ |
| department | text | YES | seed_views.v_agent_people.department | _undocumented_ |
| education | text | YES | seed_views.v_agent_people.education | _undocumented_ |
| email | text | YES | seed_views.v_agent_people.email | _undocumented_ |
| email_verification_source | text | YES | seed_views.v_agent_people.email_verification_sourc | _undocumented_ |
| email_verified | boolean | YES | seed_views.v_agent_people.email_verified | _undocumented_ |
| email_verified_at | timestamp with  | YES | seed_views.v_agent_people.email_verified_at | _undocumented_ |
| facebook_url | text | YES | seed_views.v_agent_people.facebook_url | _undocumented_ |
| first_name | text | YES | seed_views.v_agent_people.first_name | _undocumented_ |
| full_name | text | YES | seed_views.v_agent_people.full_name | _undocumented_ |
| is_decision_maker | boolean | YES | seed_views.v_agent_people.is_decision_maker | _undocumented_ |
| last_enrichment_attempt | timestamp witho | YES | seed_views.v_agent_people.last_enrichment_attempt | _undocumented_ |
| last_name | text | YES | seed_views.v_agent_people.last_name | _undocumented_ |
| last_verified_at | timestamp witho | YES | seed_views.v_agent_people.last_verified_at | _undocumented_ |
| linkedin_url | text | YES | seed_views.v_agent_people.linkedin_url | _undocumented_ |
| message_key_scheduled | text | YES | seed_views.v_agent_people.message_key_scheduled | _undocumented_ |
| outreach_ready | boolean | YES | seed_views.v_agent_people.outreach_ready | _undocumented_ |
| outreach_ready_at | timestamp with  | YES | seed_views.v_agent_people.outreach_ready_at | _undocumented_ |
| personal_phone_e164 | text | YES | seed_views.v_agent_people.personal_phone_e164 | _undocumented_ |
| promoted_from_intake_at | timestamp with  | YES | seed_views.v_agent_people.promoted_from_intake_at | _undocumented_ |
| promotion_audit_log_id | integer | YES | seed_views.v_agent_people.promotion_audit_log_id | _undocumented_ |
| seniority | text | YES | seed_views.v_agent_people.seniority | _undocumented_ |
| skills | ARRAY | YES | seed_views.v_agent_people.skills | _undocumented_ |
| source_record_id | text | YES | seed_views.v_agent_people.source_record_id | _undocumented_ |
| source_system | text | YES | seed_views.v_agent_people.source_system | _undocumented_ |
| title | text | YES | seed_views.v_agent_people.title | _undocumented_ |
| twitter_url | text | YES | seed_views.v_agent_people.twitter_url | _undocumented_ |
| unique_id | text | YES | seed_views.v_agent_people.unique_id | _undocumented_ |
| updated_at | timestamp with  | YES | seed_views.v_agent_people.updated_at | _undocumented_ |
| validation_status | character varyi | YES | seed_views.v_agent_people.validation_status | _undocumented_ |
| work_phone_e164 | text | YES | seed_views.v_agent_people.work_phone_e164 | _undocumented_ |

### LEAF: seed_views.v_agent_slots (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | YES | seed_views.v_agent_slots.company_unique_id | _undocumented_ |
| confidence_score | numeric | YES | seed_views.v_agent_slots.confidence_score | _undocumented_ |
| created_at | timestamp with  | YES | seed_views.v_agent_slots.created_at | _undocumented_ |
| filled_at | timestamp with  | YES | seed_views.v_agent_slots.filled_at | _undocumented_ |
| is_filled | boolean | YES | seed_views.v_agent_slots.is_filled | _undocumented_ |
| outreach_id | uuid | YES | seed_views.v_agent_slots.outreach_id | _undocumented_ |
| person_unique_id | text | YES | seed_views.v_agent_slots.person_unique_id | _undocumented_ |
| slot_id | text | YES | seed_views.v_agent_slots.slot_id | _undocumented_ |
| slot_type | text | YES | seed_views.v_agent_slots.slot_type | _undocumented_ |
| source_system | text | YES | seed_views.v_agent_slots.source_system | _undocumented_ |
| updated_at | timestamp with  | YES | seed_views.v_agent_slots.updated_at | _undocumented_ |

---

## BRANCH: shq (10 tables, 71 columns, 30% documented)

### LEAF: shq.audit_log (5 columns, 5 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| created_at | timestamp witho | YES | shq.audit_log.created_at | When this record was created |
| details | jsonb | YES | shq.audit_log.details | Event details (JSON) |
| event_source | character varyi | NO | shq.audit_log.event_source | System or process that generated this event |
| event_type | character varyi | NO | shq.audit_log.event_type | Type of audit/system event |
| id | integer | NO | shq.audit_log.id | Id |

### LEAF: shq.error_master (16 columns, 16 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_id | character varyi | NO | shq.error_master.agent_id | Agent Id |
| air_event_id | character varyi | YES | shq.error_master.air_event_id | Air Event Id |
| archived_at | timestamp with  | YES | shq.error_master.archived_at | When this record was archived |
| company_unique_id | character varyi | YES | shq.error_master.company_unique_id | FK to cl.company_identity or Barton company ID |
| context | jsonb | YES | shq.error_master.context | Context |
| created_at | timestamp with  | NO | shq.error_master.created_at | When this record was created |
| disposition | USER-DEFINED | YES | shq.error_master.disposition | Disposition |
| error_id | uuid | NO | shq.error_master.error_id | Primary key for this error record |
| error_type | character varyi | NO | shq.error_master.error_type | Discriminator column classifying the error type |
| message | text | NO | shq.error_master.message | Message |
| outreach_context_id | character varyi | YES | shq.error_master.outreach_context_id | Outreach Context Id |
| process_id | character varyi | NO | shq.error_master.process_id | Process Id |
| resolution_type | character varyi | YES | shq.error_master.resolution_type | Resolution Type |
| resolved_at | timestamp with  | YES | shq.error_master.resolved_at | When this error/issue was resolved |
| severity | character varyi | NO | shq.error_master.severity | Severity |
| ttl_tier | USER-DEFINED | YES | shq.error_master.ttl_tier | Ttl Tier |

### LEAF: shq.v_dol_enrichment_queue (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | character varyi | YES | shq.v_dol_enrichment_queue.company_unique_id | _undocumented_ |
| context | jsonb | YES | shq.v_dol_enrichment_queue.context | _undocumented_ |
| created_at | timestamp with  | YES | shq.v_dol_enrichment_queue.created_at | _undocumented_ |
| error_id | uuid | YES | shq.v_dol_enrichment_queue.error_id | _undocumented_ |
| error_type | character varyi | YES | shq.v_dol_enrichment_queue.error_type | _undocumented_ |
| hours_pending | numeric | YES | shq.v_dol_enrichment_queue.hours_pending | _undocumented_ |
| message | text | YES | shq.v_dol_enrichment_queue.message | _undocumented_ |
| outreach_context_id | character varyi | YES | shq.v_dol_enrichment_queue.outreach_context_id | _undocumented_ |

### LEAF: shq.v_error_summary_24h (7 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_id | character varyi | YES | shq.v_error_summary_24h.agent_id | _undocumented_ |
| earliest | timestamp with  | YES | shq.v_error_summary_24h.earliest | _undocumented_ |
| error_count | bigint | YES | shq.v_error_summary_24h.error_count | _undocumented_ |
| error_type | character varyi | YES | shq.v_error_summary_24h.error_type | _undocumented_ |
| latest | timestamp with  | YES | shq.v_error_summary_24h.latest | _undocumented_ |
| process_id | character varyi | YES | shq.v_error_summary_24h.process_id | _undocumented_ |
| unresolved_count | bigint | YES | shq.v_error_summary_24h.unresolved_count | _undocumented_ |

### LEAF: shq.vw_blocking_errors_by_outreach (3 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| blocking_tables | ARRAY | YES | shq.vw_blocking_errors_by_outreach.blocking_tables | _undocumented_ |
| outreach_id | uuid | YES | shq.vw_blocking_errors_by_outreach.outreach_id | _undocumented_ |
| total_blocking_errors | numeric | YES | shq.vw_blocking_errors_by_outreach.total_blocking_ | _undocumented_ |

### LEAF: shq.vw_error_governance_summary (8 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| disposition | USER-DEFINED | YES | shq.vw_error_governance_summary.disposition | _undocumented_ |
| error_count | bigint | YES | shq.vw_error_governance_summary.error_count | _undocumented_ |
| error_table | text | YES | shq.vw_error_governance_summary.error_table | _undocumented_ |
| escalation_level | integer | YES | shq.vw_error_governance_summary.escalation_level | _undocumented_ |
| newest_error | timestamp with  | YES | shq.vw_error_governance_summary.newest_error | _undocumented_ |
| oldest_error | timestamp with  | YES | shq.vw_error_governance_summary.oldest_error | _undocumented_ |
| ttl_expired_count | bigint | YES | shq.vw_error_governance_summary.ttl_expired_count | _undocumented_ |
| ttl_tier | USER-DEFINED | YES | shq.vw_error_governance_summary.ttl_tier | _undocumented_ |

### LEAF: shq.vw_error_resolution_rate (5 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| resolution_rate_pct | numeric | YES | shq.vw_error_resolution_rate.resolution_rate_pct | _undocumented_ |
| resolved_errors | bigint | YES | shq.vw_error_resolution_rate.resolved_errors | _undocumented_ |
| source_table | character varyi | YES | shq.vw_error_resolution_rate.source_table | _undocumented_ |
| total_errors | bigint | YES | shq.vw_error_resolution_rate.total_errors | _undocumented_ |
| unresolved_errors | bigint | YES | shq.vw_error_resolution_rate.unresolved_errors | _undocumented_ |

### LEAF: shq.vw_promotion_readiness (11 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| bit_done | boolean | YES | shq.vw_promotion_readiness.bit_done | _undocumented_ |
| blog_done | boolean | YES | shq.vw_promotion_readiness.blog_done | _undocumented_ |
| can_promote_to_outreach | boolean | YES | shq.vw_promotion_readiness.can_promote_to_outreach | _undocumented_ |
| company_target_done | boolean | YES | shq.vw_promotion_readiness.company_target_done | _undocumented_ |
| dol_done | boolean | YES | shq.vw_promotion_readiness.dol_done | _undocumented_ |
| has_ct_blocking_errors | boolean | YES | shq.vw_promotion_readiness.has_ct_blocking_errors | _undocumented_ |
| has_dol_blocking_errors | boolean | YES | shq.vw_promotion_readiness.has_dol_blocking_errors | _undocumented_ |
| has_people_blocking_errors | boolean | YES | shq.vw_promotion_readiness.has_people_blocking_err | _undocumented_ |
| outreach_id | uuid | YES | shq.vw_promotion_readiness.outreach_id | _undocumented_ |
| people_done | boolean | YES | shq.vw_promotion_readiness.people_done | _undocumented_ |
| readiness_tier | text | YES | shq.vw_promotion_readiness.readiness_tier | _undocumented_ |

### LEAF: shq.vw_promotion_readiness_summary (3 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| count | bigint | YES | shq.vw_promotion_readiness_summary.count | _undocumented_ |
| percentage | numeric | YES | shq.vw_promotion_readiness_summary.percentage | _undocumented_ |
| readiness_tier | text | YES | shq.vw_promotion_readiness_summary.readiness_tier | _undocumented_ |

### LEAF: shq.vw_unresolved_errors_by_source (5 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| agent_id | character varyi | YES | shq.vw_unresolved_errors_by_source.agent_id | _undocumented_ |
| error_count | bigint | YES | shq.vw_unresolved_errors_by_source.error_count | _undocumented_ |
| newest_error | timestamp with  | YES | shq.vw_unresolved_errors_by_source.newest_error | _undocumented_ |
| oldest_error | timestamp with  | YES | shq.vw_unresolved_errors_by_source.oldest_error | _undocumented_ |
| source_table | character varyi | YES | shq.vw_unresolved_errors_by_source.source_table | _undocumented_ |

---

## BRANCH: vendor (8 tables, 252 columns, 0% documented)

### LEAF: vendor.blog (29 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| company_unique_id | text | YES | vendor.blog.company_unique_id | _undocumented_ |
| content_checksum | text | YES | vendor.blog.content_checksum | _undocumented_ |
| discovered_at | timestamp with  | YES | vendor.blog.discovered_at | _undocumented_ |
| discovered_from | text | YES | vendor.blog.discovered_from | _undocumented_ |
| domain | text | YES | vendor.blog.domain | _undocumented_ |
| domain_reachable | boolean | YES | vendor.blog.domain_reachable | _undocumented_ |
| extracted_at | timestamp with  | YES | vendor.blog.extracted_at | _undocumented_ |
| extraction_error | text | YES | vendor.blog.extraction_error | _undocumented_ |
| extraction_status | text | YES | vendor.blog.extraction_status | _undocumented_ |
| has_sitemap | boolean | YES | vendor.blog.has_sitemap | _undocumented_ |
| http_status | smallint | YES | vendor.blog.http_status | _undocumented_ |
| is_accessible | boolean | YES | vendor.blog.is_accessible | _undocumented_ |
| last_checked_at | timestamp with  | YES | vendor.blog.last_checked_at | _undocumented_ |
| last_content_change_at | timestamp with  | YES | vendor.blog.last_content_change_at | _undocumented_ |
| migrated_at | timestamp with  | NO | vendor.blog.migrated_at | _undocumented_ |
| original_created_at | timestamp with  | YES | vendor.blog.original_created_at | _undocumented_ |
| original_updated_at | timestamp with  | YES | vendor.blog.original_updated_at | _undocumented_ |
| outreach_id | uuid | YES | vendor.blog.outreach_id | _undocumented_ |
| page_title | text | YES | vendor.blog.page_title | _undocumented_ |
| people_extracted | integer | YES | vendor.blog.people_extracted | _undocumented_ |
| reachable_checked_at | timestamp with  | YES | vendor.blog.reachable_checked_at | _undocumented_ |
| requires_paid_enrichment | boolean | YES | vendor.blog.requires_paid_enrichment | _undocumented_ |
| sitemap_source | text | YES | vendor.blog.sitemap_source | _undocumented_ |
| sitemap_url | text | YES | vendor.blog.sitemap_url | _undocumented_ |
| source_row_id | text | YES | vendor.blog.source_row_id | _undocumented_ |
| source_table | text | NO | vendor.blog.source_table | _undocumented_ |
| source_type | text | YES | vendor.blog.source_type | _undocumented_ |
| source_url | text | YES | vendor.blog.source_url | _undocumented_ |
| vendor_row_id | bigint | NO | vendor.blog.vendor_row_id | _undocumented_ |

### LEAF: vendor.blog_claude (9 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| domain | text | YES | vendor.blog_claude.domain | _undocumented_ |
| enrichment_type | text | YES | vendor.blog_claude.enrichment_type | _undocumented_ |
| migrated_at | timestamp with  | NO | vendor.blog_claude.migrated_at | _undocumented_ |
| original_created_at | timestamp with  | YES | vendor.blog_claude.original_created_at | _undocumented_ |
| outreach_id | uuid | YES | vendor.blog_claude.outreach_id | _undocumented_ |
| payload | jsonb | YES | vendor.blog_claude.payload | _undocumented_ |
| source_row_id | text | YES | vendor.blog_claude.source_row_id | _undocumented_ |
| source_table | text | NO | vendor.blog_claude.source_table | _undocumented_ |
| vendor_row_id | bigint | NO | vendor.blog_claude.vendor_row_id | _undocumented_ |

### LEAF: vendor.ct (64 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| address_full | text | YES | vendor.ct.address_full | _undocumented_ |
| apollo_id | text | YES | vendor.ct.apollo_id | _undocumented_ |
| b2_file_path | text | YES | vendor.ct.b2_file_path | _undocumented_ |
| b2_uploaded_at | timestamp witho | YES | vendor.ct.b2_uploaded_at | _undocumented_ |
| cage_code | text | YES | vendor.ct.cage_code | _undocumented_ |
| chronic_bad | boolean | YES | vendor.ct.chronic_bad | _undocumented_ |
| city | text | YES | vendor.ct.city | _undocumented_ |
| company_name | text | YES | vendor.ct.company_name | _undocumented_ |
| company_name_for_emails | text | YES | vendor.ct.company_name_for_emails | _undocumented_ |
| company_phone | text | YES | vendor.ct.company_phone | _undocumented_ |
| company_type | text | YES | vendor.ct.company_type | _undocumented_ |
| company_unique_id | text | YES | vendor.ct.company_unique_id | _undocumented_ |
| country | text | YES | vendor.ct.country | _undocumented_ |
| data_quality_score | numeric | YES | vendor.ct.data_quality_score | _undocumented_ |
| description | text | YES | vendor.ct.description | _undocumented_ |
| domain | text | YES | vendor.ct.domain | _undocumented_ |
| duns | text | YES | vendor.ct.duns | _undocumented_ |
| ein | text | YES | vendor.ct.ein | _undocumented_ |
| email_pattern | text | YES | vendor.ct.email_pattern | _undocumented_ |
| email_pattern_confidence | integer | YES | vendor.ct.email_pattern_confidence | _undocumented_ |
| email_pattern_source | text | YES | vendor.ct.email_pattern_source | _undocumented_ |
| email_pattern_verified_at | timestamp witho | YES | vendor.ct.email_pattern_verified_at | _undocumented_ |
| employee_count | integer | YES | vendor.ct.employee_count | _undocumented_ |
| enriched_at | timestamp witho | YES | vendor.ct.enriched_at | _undocumented_ |
| enriched_by | text | YES | vendor.ct.enriched_by | _undocumented_ |
| enrichment_attempt | integer | YES | vendor.ct.enrichment_attempt | _undocumented_ |
| facebook_url | text | YES | vendor.ct.facebook_url | _undocumented_ |
| founded_year | integer | YES | vendor.ct.founded_year | _undocumented_ |
| garage_bay | text | YES | vendor.ct.garage_bay | _undocumented_ |
| headcount_max | integer | YES | vendor.ct.headcount_max | _undocumented_ |
| headcount_min | integer | YES | vendor.ct.headcount_min | _undocumented_ |
| headcount_raw | text | YES | vendor.ct.headcount_raw | _undocumented_ |
| import_batch_id | text | YES | vendor.ct.import_batch_id | _undocumented_ |
| industry | text | YES | vendor.ct.industry | _undocumented_ |
| industry_normalized | text | YES | vendor.ct.industry_normalized | _undocumented_ |
| keywords | ARRAY | YES | vendor.ct.keywords | _undocumented_ |
| last_enriched_at | timestamp witho | YES | vendor.ct.last_enriched_at | _undocumented_ |
| last_hash | text | YES | vendor.ct.last_hash | _undocumented_ |
| linkedin_url | text | YES | vendor.ct.linkedin_url | _undocumented_ |
| migrated_at | timestamp with  | NO | vendor.ct.migrated_at | _undocumented_ |
| original_created_at | timestamp with  | YES | vendor.ct.original_created_at | _undocumented_ |
| original_updated_at | timestamp with  | YES | vendor.ct.original_updated_at | _undocumented_ |
| outreach_id | uuid | YES | vendor.ct.outreach_id | _undocumented_ |
| postal_code | text | YES | vendor.ct.postal_code | _undocumented_ |
| promoted_from_intake_at | timestamp with  | YES | vendor.ct.promoted_from_intake_at | _undocumented_ |
| promotion_audit_log_id | integer | YES | vendor.ct.promotion_audit_log_id | _undocumented_ |
| sic_codes | text | YES | vendor.ct.sic_codes | _undocumented_ |
| source_file | text | YES | vendor.ct.source_file | _undocumented_ |
| source_record_id | text | YES | vendor.ct.source_record_id | _undocumented_ |
| source_row_id | text | YES | vendor.ct.source_row_id | _undocumented_ |
| source_system | text | YES | vendor.ct.source_system | _undocumented_ |
| source_table | text | NO | vendor.ct.source_table | _undocumented_ |
| state | text | YES | vendor.ct.state | _undocumented_ |
| state_abbrev | text | YES | vendor.ct.state_abbrev | _undocumented_ |
| street | text | YES | vendor.ct.street | _undocumented_ |
| tags | ARRAY | YES | vendor.ct.tags | _undocumented_ |
| twitter_url | text | YES | vendor.ct.twitter_url | _undocumented_ |
| validated | boolean | YES | vendor.ct.validated | _undocumented_ |
| validated_at | timestamp with  | YES | vendor.ct.validated_at | _undocumented_ |
| validated_by | text | YES | vendor.ct.validated_by | _undocumented_ |
| validation_notes | text | YES | vendor.ct.validation_notes | _undocumented_ |
| validation_reasons | text | YES | vendor.ct.validation_reasons | _undocumented_ |
| vendor_row_id | bigint | NO | vendor.ct.vendor_row_id | _undocumented_ |
| website_url | text | YES | vendor.ct.website_url | _undocumented_ |

### LEAF: vendor.ct_claude (28 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| checked_at | timestamp with  | YES | vendor.ct_claude.checked_at | _undocumented_ |
| child_company_id | uuid | YES | vendor.ct_claude.child_company_id | _undocumented_ |
| company_unique_id | uuid | YES | vendor.ct_claude.company_unique_id | _undocumented_ |
| computed_at | timestamp with  | YES | vendor.ct_claude.computed_at | _undocumented_ |
| confidence_bucket | text | YES | vendor.ct_claude.confidence_bucket | _undocumented_ |
| confidence_score | integer | YES | vendor.ct_claude.confidence_score | _undocumented_ |
| domain | text | YES | vendor.ct_claude.domain | _undocumented_ |
| domain_health | text | YES | vendor.ct_claude.domain_health | _undocumented_ |
| domain_name_confidence | integer | YES | vendor.ct_claude.domain_name_confidence | _undocumented_ |
| ingestion_run_id | text | YES | vendor.ct_claude.ingestion_run_id | _undocumented_ |
| migrated_at | timestamp with  | NO | vendor.ct_claude.migrated_at | _undocumented_ |
| mx_present | boolean | YES | vendor.ct_claude.mx_present | _undocumented_ |
| name_type | text | YES | vendor.ct_claude.name_type | _undocumented_ |
| name_value | text | YES | vendor.ct_claude.name_value | _undocumented_ |
| original_created_at | timestamp with  | YES | vendor.ct_claude.original_created_at | _undocumented_ |
| parent_company_id | uuid | YES | vendor.ct_claude.parent_company_id | _undocumented_ |
| raw_payload | jsonb | YES | vendor.ct_claude.raw_payload | _undocumented_ |
| relationship_type | text | YES | vendor.ct_claude.relationship_type | _undocumented_ |
| resolution_method | text | YES | vendor.ct_claude.resolution_method | _undocumented_ |
| source_record_id | text | YES | vendor.ct_claude.source_record_id | _undocumented_ |
| source_row_id | text | YES | vendor.ct_claude.source_row_id | _undocumented_ |
| source_system | text | YES | vendor.ct_claude.source_system | _undocumented_ |
| source_table | text | NO | vendor.ct_claude.source_table | _undocumented_ |
| state_code | character | YES | vendor.ct_claude.state_code | _undocumented_ |
| vendor_row_id | bigint | NO | vendor.ct_claude.vendor_row_id | _undocumented_ |
| verification_error | text | YES | vendor.ct_claude.verification_error | _undocumented_ |
| verification_status | text | YES | vendor.ct_claude.verification_status | _undocumented_ |
| verified_at | timestamp with  | YES | vendor.ct_claude.verified_at | _undocumented_ |

### LEAF: vendor.dol_claude (18 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| city | text | YES | vendor.dol_claude.city | _undocumented_ |
| confidence | text | YES | vendor.dol_claude.confidence | _undocumented_ |
| dba_name | text | YES | vendor.dol_claude.dba_name | _undocumented_ |
| ein | text | YES | vendor.dol_claude.ein | _undocumented_ |
| enriched_url | text | YES | vendor.dol_claude.enriched_url | _undocumented_ |
| legal_name | text | YES | vendor.dol_claude.legal_name | _undocumented_ |
| match_status | text | YES | vendor.dol_claude.match_status | _undocumented_ |
| matched_company_unique_id | text | YES | vendor.dol_claude.matched_company_unique_id | _undocumented_ |
| migrated_at | timestamp with  | NO | vendor.dol_claude.migrated_at | _undocumented_ |
| original_created_at | timestamp with  | YES | vendor.dol_claude.original_created_at | _undocumented_ |
| participants | integer | YES | vendor.dol_claude.participants | _undocumented_ |
| payload | jsonb | YES | vendor.dol_claude.payload | _undocumented_ |
| search_query | text | YES | vendor.dol_claude.search_query | _undocumented_ |
| source_row_id | text | YES | vendor.dol_claude.source_row_id | _undocumented_ |
| source_table | text | NO | vendor.dol_claude.source_table | _undocumented_ |
| state | text | YES | vendor.dol_claude.state | _undocumented_ |
| vendor_row_id | bigint | NO | vendor.dol_claude.vendor_row_id | _undocumented_ |
| zip | text | YES | vendor.dol_claude.zip | _undocumented_ |

### LEAF: vendor.lane_claude (10 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| domain | text | YES | vendor.lane_claude.domain | _undocumented_ |
| enrichment_type | text | YES | vendor.lane_claude.enrichment_type | _undocumented_ |
| lane | text | YES | vendor.lane_claude.lane | _undocumented_ |
| migrated_at | timestamp with  | NO | vendor.lane_claude.migrated_at | _undocumented_ |
| original_created_at | timestamp with  | YES | vendor.lane_claude.original_created_at | _undocumented_ |
| outreach_id | uuid | YES | vendor.lane_claude.outreach_id | _undocumented_ |
| payload | jsonb | YES | vendor.lane_claude.payload | _undocumented_ |
| source_row_id | text | YES | vendor.lane_claude.source_row_id | _undocumented_ |
| source_table | text | NO | vendor.lane_claude.source_table | _undocumented_ |
| vendor_row_id | bigint | NO | vendor.lane_claude.vendor_row_id | _undocumented_ |

### LEAF: vendor.people (65 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| b2_file_path | text | YES | vendor.people.b2_file_path | _undocumented_ |
| b2_uploaded_at | timestamp witho | YES | vendor.people.b2_uploaded_at | _undocumented_ |
| backfill_source | text | YES | vendor.people.backfill_source | _undocumented_ |
| bio | text | YES | vendor.people.bio | _undocumented_ |
| certifications | text | YES | vendor.people.certifications | _undocumented_ |
| chronic_bad | boolean | YES | vendor.people.chronic_bad | _undocumented_ |
| city | text | YES | vendor.people.city | _undocumented_ |
| company_name | text | YES | vendor.people.company_name | _undocumented_ |
| company_unique_id | text | YES | vendor.people.company_unique_id | _undocumented_ |
| confidence_score | numeric | YES | vendor.people.confidence_score | _undocumented_ |
| country | text | YES | vendor.people.country | _undocumented_ |
| data_quality_score | numeric | YES | vendor.people.data_quality_score | _undocumented_ |
| department | text | YES | vendor.people.department | _undocumented_ |
| department_normalized | text | YES | vendor.people.department_normalized | _undocumented_ |
| domain | text | YES | vendor.people.domain | _undocumented_ |
| education | text | YES | vendor.people.education | _undocumented_ |
| email | text | YES | vendor.people.email | _undocumented_ |
| email_type | text | YES | vendor.people.email_type | _undocumented_ |
| email_verified | boolean | YES | vendor.people.email_verified | _undocumented_ |
| enriched_by | text | YES | vendor.people.enriched_by | _undocumented_ |
| enrichment_attempt | integer | YES | vendor.people.enrichment_attempt | _undocumented_ |
| facebook_url | text | YES | vendor.people.facebook_url | _undocumented_ |
| first_name | text | YES | vendor.people.first_name | _undocumented_ |
| full_name | text | YES | vendor.people.full_name | _undocumented_ |
| hunter_sources | ARRAY | YES | vendor.people.hunter_sources | _undocumented_ |
| import_batch_id | text | YES | vendor.people.import_batch_id | _undocumented_ |
| is_decision_maker | boolean | YES | vendor.people.is_decision_maker | _undocumented_ |
| job_title | text | YES | vendor.people.job_title | _undocumented_ |
| last_enriched_at | timestamp witho | YES | vendor.people.last_enriched_at | _undocumented_ |
| last_name | text | YES | vendor.people.last_name | _undocumented_ |
| linkedin_url | text | YES | vendor.people.linkedin_url | _undocumented_ |
| mapped_slot_type | text | YES | vendor.people.mapped_slot_type | _undocumented_ |
| migrated_at | timestamp with  | NO | vendor.people.migrated_at | _undocumented_ |
| num_sources | integer | YES | vendor.people.num_sources | _undocumented_ |
| original_created_at | timestamp with  | YES | vendor.people.original_created_at | _undocumented_ |
| original_updated_at | timestamp with  | YES | vendor.people.original_updated_at | _undocumented_ |
| outreach_id | uuid | YES | vendor.people.outreach_id | _undocumented_ |
| outreach_priority | integer | YES | vendor.people.outreach_priority | _undocumented_ |
| personal_phone | text | YES | vendor.people.personal_phone | _undocumented_ |
| phone_number | text | YES | vendor.people.phone_number | _undocumented_ |
| position_raw | text | YES | vendor.people.position_raw | _undocumented_ |
| processed_at | timestamp witho | YES | vendor.people.processed_at | _undocumented_ |
| raw_name | text | YES | vendor.people.raw_name | _undocumented_ |
| seniority_level | text | YES | vendor.people.seniority_level | _undocumented_ |
| skills | ARRAY | YES | vendor.people.skills | _undocumented_ |
| slot_type | text | YES | vendor.people.slot_type | _undocumented_ |
| source_file | text | YES | vendor.people.source_file | _undocumented_ |
| source_record_id | text | YES | vendor.people.source_record_id | _undocumented_ |
| source_row_id | text | YES | vendor.people.source_row_id | _undocumented_ |
| source_system | text | YES | vendor.people.source_system | _undocumented_ |
| source_table | text | NO | vendor.people.source_table | _undocumented_ |
| source_url_id | uuid | YES | vendor.people.source_url_id | _undocumented_ |
| state | text | YES | vendor.people.state | _undocumented_ |
| state_abbrev | text | YES | vendor.people.state_abbrev | _undocumented_ |
| status | text | YES | vendor.people.status | _undocumented_ |
| tags | ARRAY | YES | vendor.people.tags | _undocumented_ |
| title_normalized | text | YES | vendor.people.title_normalized | _undocumented_ |
| twitter_handle | text | YES | vendor.people.twitter_handle | _undocumented_ |
| twitter_url | text | YES | vendor.people.twitter_url | _undocumented_ |
| validated | boolean | YES | vendor.people.validated | _undocumented_ |
| validated_at | timestamp witho | YES | vendor.people.validated_at | _undocumented_ |
| validated_by | text | YES | vendor.people.validated_by | _undocumented_ |
| validation_notes | text | YES | vendor.people.validation_notes | _undocumented_ |
| vendor_row_id | bigint | NO | vendor.people.vendor_row_id | _undocumented_ |
| work_phone | text | YES | vendor.people.work_phone | _undocumented_ |

### LEAF: vendor.people_claude (29 columns, 0 documented)

| Column | Type | Nullable | Unique ID | Description |
|--------|------|----------|-----------|-------------|
| assigned_to | text | YES | vendor.people_claude.assigned_to | _undocumented_ |
| attempt_count | integer | YES | vendor.people_claude.attempt_count | _undocumented_ |
| company_name | text | YES | vendor.people_claude.company_name | _undocumented_ |
| company_slot_unique_id | text | YES | vendor.people_claude.company_slot_unique_id | _undocumented_ |
| company_unique_id | text | YES | vendor.people_claude.company_unique_id | _undocumented_ |
| empty_slots | ARRAY | YES | vendor.people_claude.empty_slots | _undocumented_ |
| error_details | jsonb | YES | vendor.people_claude.error_details | _undocumented_ |
| existing_email | text | YES | vendor.people_claude.existing_email | _undocumented_ |
| failure_reason | text | YES | vendor.people_claude.failure_reason | _undocumented_ |
| issue_type | text | YES | vendor.people_claude.issue_type | _undocumented_ |
| last_touched_at | timestamp witho | YES | vendor.people_claude.last_touched_at | _undocumented_ |
| migrated_at | timestamp with  | NO | vendor.people_claude.migrated_at | _undocumented_ |
| notes | text | YES | vendor.people_claude.notes | _undocumented_ |
| original_created_at | timestamp witho | YES | vendor.people_claude.original_created_at | _undocumented_ |
| priority | integer | YES | vendor.people_claude.priority | _undocumented_ |
| processed_at | timestamp witho | YES | vendor.people_claude.processed_at | _undocumented_ |
| processed_via | text | YES | vendor.people_claude.processed_via | _undocumented_ |
| queued_at | timestamp witho | YES | vendor.people_claude.queued_at | _undocumented_ |
| resolved_at | timestamp witho | YES | vendor.people_claude.resolved_at | _undocumented_ |
| resolved_contact_id | text | YES | vendor.people_claude.resolved_contact_id | _undocumented_ |
| slot_type | text | YES | vendor.people_claude.slot_type | _undocumented_ |
| source_row_id | text | YES | vendor.people_claude.source_row_id | _undocumented_ |
| source_table | text | NO | vendor.people_claude.source_table | _undocumented_ |
| source_url | text | YES | vendor.people_claude.source_url | _undocumented_ |
| source_url_id | uuid | YES | vendor.people_claude.source_url_id | _undocumented_ |
| status | text | YES | vendor.people_claude.status | _undocumented_ |
| touched_by | text | YES | vendor.people_claude.touched_by | _undocumented_ |
| url_type | text | YES | vendor.people_claude.url_type | _undocumented_ |
| vendor_row_id | bigint | NO | vendor.people_claude.vendor_row_id | _undocumented_ |

---

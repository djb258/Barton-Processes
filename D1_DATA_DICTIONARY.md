# D1 Data Dictionary — AI-Ready Column Reference
## Every D1 database, every table, every column — with unique ID, type, format, and description
### Authority: Live D1 introspection (2026-03-31)
### Status: OPERATE — this is the master reference for all process documentation

---

## Database Inventory

| # | D1 Database | Binding | Database ID | Tables | Purpose |
|---|-------------|---------|-------------|--------|---------|
| 1 | svg-d1-spine | D1_SPINE / D1 | 641a9a1e | 38 | CL identity, LCS pipeline, errors, escalation, doctrine, coverage, sales state |
| 2 | svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | 33 | Outreach footprint — CT, DOL, Blog, People, Slots, Staging |
| 3 | svg-d1-sovereign | D1_SOVEREIGN | — | 81 | Legacy sovereign hub (pre-v2 architecture) |
| 4 | imo-d1-global | D1_GLOBAL | — | 1 | Reference data — US ZIP codes |
| 5 | svg-d1-storage | D1_STORAGE | — | 92 | Storage/real estate investment analysis |
| 6 | svg-d1-research | D1_RESEARCH | — | 4 | Doctrine library (duplicate of spine subset) |
| 7 | imo-brain | D1_IMO_BRAIN | 77adcbfe | 15 | System knowledge (documents, chunks, glossary, decisions, relationships) |
| 8 | svg-brain | D1_SVG_BRAIN | a2e09d86 | 15 | Insurance domain knowledge (same schema as imo-brain) |
| 9 | layer0 | D1_LAYER0 | — | 6 | Constant extraction engine (empty — not yet used) |
| 10 | lcs | D1_LCS | — | 9 | Legacy LCS tables (empty — migrated to spine) |
| 11 | phone | D1_PHONE | — | 3 | Phone system (call log, phone map) |
| 12 | people-worker-200 | D1_PEOPLE | — | 12 | Legacy people worker (v1 — deprecated, use outreach) |

### Active Databases for SVG Processes

Only 4 databases matter for SVG Agency processes:

| Database | Used By | Role |
|----------|---------|------|
| **svg-d1-spine** | Process 100 (LCS), Process 800 (Client Mint) | Pipeline state, CL identity, errors, escalation |
| **svg-d1-outreach-ops** | Process 010, 200, 300, 400, 500, 700 | Company footprint — the workspace |
| **imo-d1-global** | Process 010 (SEED) | Reference ZIP codes for coverage filter |
| **imo-brain** | All processes (logging) | System knowledge store |

---

# DATABASE 1: svg-d1-spine (641a9a1e)
## 38 tables — CL identity, LCS pipeline, errors, escalation, doctrine

---

### cl_company_identity — Sovereign company records (117,154 rows)
The ONE table that owns company identity. Every other table references this via company_unique_id or outreach_id.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| company_unique_id | TEXT | PK, NOT NULL | UUID v4 | Sovereign company identifier — the VIN. Never changes. |
| company_name | TEXT | NOT NULL | Free text | Original company name from source system |
| canonical_name | TEXT | | Free text | Cleaned/standardized company name (authoritative for display) |
| company_domain | TEXT | | domain.com | Company website domain (no protocol) |
| normalized_domain | TEXT | | domain.com | Domain after normalization (lowercase, www stripped) |
| linkedin_company_url | TEXT | | URL | LinkedIn company page URL |
| source_system | TEXT | NOT NULL | Enum | Where this company came from (dol, web_scrape, manual, etc.) |
| state_code | TEXT | | 2-letter | US state code (WV, MD, NC, etc.) |
| employee_count_band | TEXT | | Range | Employee count band (1-50, 51-200, 201-500, etc.) |
| existence_verified | INTEGER | | 0/1 | Whether company existence has been verified |
| verification_run_id | TEXT | | UUID | Which verification batch checked this company |
| verified_at | TEXT | | ISO 8601 | When existence was verified |
| domain_status_code | INTEGER | | HTTP code | HTTP status code from domain check (200, 404, etc.) |
| name_match_score | INTEGER | | 0-100 | How closely name matches across sources |
| state_match_result | TEXT | | Enum | State verification result (MATCH, MISMATCH, UNKNOWN) |
| state_verified | TEXT | | State code | Verified state from domain/DOL cross-reference |
| identity_pass | INTEGER | | 0/1 | Whether company passed the identity gate |
| identity_status | TEXT | | Enum | Identity verification status (PASSED, FAILED, PENDING) |
| last_pass_at | TEXT | | ISO 8601 | When company last passed identity verification |
| eligibility_status | TEXT | | Enum | Whether company is eligible for outreach (ELIGIBLE, EXCLUDED) |
| exclusion_reason | TEXT | | Free text | Why company was excluded (if applicable) |
| entity_role | TEXT | | Enum | Role in hierarchy (PARENT, SUBSIDIARY, STANDALONE) |
| sovereign_company_id | TEXT | | UUID | Self-referencing — same as company_unique_id for standalone |
| final_outcome | TEXT | | Enum | Final lifecycle outcome (OUTREACH, SALES, CLIENT, EXCLUDED) |
| final_reason | TEXT | | Free text | Reason for final outcome |
| outreach_id | TEXT | | UUID | Write-once pointer to outreach.outreach_outreach.outreach_id |
| sales_process_id | TEXT | | UUID | Write-once pointer to sales pipeline |
| client_id | TEXT | | UUID | Write-once pointer to client record |
| outreach_attached_at | TEXT | | ISO 8601 | When company was attached to outreach |
| sales_opened_at | TEXT | | ISO 8601 | When sales process opened |
| client_promoted_at | TEXT | | ISO 8601 | When company became a client |
| lcs_id | TEXT | | UUID | LCS communication chain identifier |
| lcs_attached_at | TEXT | | ISO 8601 | When attached to LCS pipeline |
| company_fingerprint | TEXT | | Hash | Dedup fingerprint (name + domain + state) |
| lifecycle_run_id | TEXT | | UUID | Which lifecycle processing batch |
| created_at | TEXT | NOT NULL | ISO 8601 | Record creation timestamp |
| updated_at | TEXT | | ISO 8601 | Last modification timestamp |

---

### lcs_signal_queue — Pipeline signal ingress (rows vary)
Signals from upstream worker spokes enter here. Each signal triggers CID compilation.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| id | TEXT | PK, NOT NULL | UUID | Unique signal identifier |
| signal_set_hash | TEXT | NOT NULL | Hash | Links to lcs_signal_registry — defines signal type |
| signal_category | TEXT | NOT NULL | Enum | Signal category (DOL, PEOPLE, BLOG, TALENT, MANUAL) |
| sovereign_company_id | TEXT | NOT NULL | UUID | Which company this signal is about |
| lifecycle_phase | TEXT | NOT NULL | Enum | Pipeline phase (OUTREACH, SALES, CLIENT) |
| preferred_channel | TEXT | | Enum | Preferred delivery channel (MG, HR, SH) |
| preferred_lane | TEXT | | Enum | Delivery lane preference |
| agent_number | TEXT | | SA-NNN | Which service agent owns this company |
| signal_data | TEXT | NOT NULL | JSON | Signal payload (varies by signal type) |
| source_hub | TEXT | NOT NULL | Enum | Which worker spoke emitted this signal |
| source_signal_id | TEXT | | UUID | Original signal ID from source system |
| status | TEXT | NOT NULL | Enum | Processing state (PENDING, PROCESSING, COMPILED, FAILED) |
| priority | INTEGER | NOT NULL | 1-5 | Priority level (1=highest) |
| created_at | TEXT | NOT NULL | ISO 8601 | When signal was received |
| processed_at | TEXT | | ISO 8601 | When signal was processed |

---

### lcs_cid — Compiled Intelligence Dossier (rows vary)
The compiled company intelligence package. One per signal processed.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| communication_id | TEXT | PK, NOT NULL | LCS-{PHASE}-{DATE}-{ULID} | Unique communication chain identifier |
| sovereign_company_id | TEXT | NOT NULL | UUID | Which company |
| entity_type | TEXT | NOT NULL | Enum | Entity type (COMPANY, CONTACT) |
| entity_id | TEXT | NOT NULL | UUID | Entity identifier (outreach_id for companies) |
| signal_set_hash | TEXT | NOT NULL | Hash | Which signal type triggered this CID |
| signal_queue_id | TEXT | | UUID | FK → lcs_signal_queue.id |
| frame_id | TEXT | NOT NULL | UUID | FK → lcs_frame_registry.frame_id (selected message frame) |
| lifecycle_phase | TEXT | NOT NULL | Enum | Pipeline phase |
| lane | TEXT | NOT NULL | Enum | Delivery lane |
| agent_number | TEXT | NOT NULL | SA-NNN | Service agent |
| intelligence_tier | INTEGER | | 2-5 | Data completeness tier (2=best, 5=minimal) |
| compilation_status | TEXT | NOT NULL | Enum | COMPILED, FAILED, SKIPPED |
| compilation_reason | TEXT | | Free text | Why compilation failed or was skipped |
| created_at | TEXT | NOT NULL | ISO 8601 | When compiled |

---

### lcs_sid_output — Constructed message (rows vary)
The personalized message built from CID + frame template.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| sid_id | TEXT | PK, NOT NULL | SID-{COMM_ID} | Unique message document identifier |
| communication_id | TEXT | NOT NULL | LCS-... | FK → lcs_cid.communication_id |
| frame_id | TEXT | NOT NULL | UUID | Which frame template was used |
| template_id | TEXT | | UUID | Specific template variant |
| subject_line | TEXT | | Free text | Email subject line |
| body_plain | TEXT | | Free text | Plain text message body |
| body_html | TEXT | | HTML | HTML message body |
| sender_identity | TEXT | | Free text | Sender display name |
| sender_email | TEXT | | Email | Sender email (dave@{domain}) |
| recipient_email | TEXT | | Email | Recipient email address |
| recipient_name | TEXT | | Free text | Recipient display name |
| construction_status | TEXT | NOT NULL | Enum | CONSTRUCTED, FAILED |
| construction_reason | TEXT | | Free text | Why construction failed |
| created_at | TEXT | NOT NULL | ISO 8601 | When constructed |

---

### lcs_mid_sequence_state — Delivery state (rows vary)
Tracks each delivery attempt. One MID per send attempt.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| mid_id | TEXT | PK, NOT NULL | UUID | Unique delivery record identifier |
| message_run_id | TEXT | NOT NULL | RUN-{COMM_ID}-{CHANNEL}-{ATTEMPT} | Unique run identifier |
| communication_id | TEXT | NOT NULL | LCS-... | FK → lcs_cid.communication_id |
| adapter_type | TEXT | NOT NULL | Enum | MG (Mailgun), HR (HeyReach), SH (SVG Brain) |
| channel | TEXT | NOT NULL | Enum | EMAIL, LINKEDIN |
| sequence_position | INTEGER | NOT NULL | 1-5 | Position in multi-touch sequence |
| attempt_number | INTEGER | NOT NULL | 1-3 | Retry attempt number |
| gate_verdict | TEXT | NOT NULL | Enum | GO, NO_GO (pre-send gate check) |
| gate_reason | TEXT | | Free text | Why gate blocked send |
| throttle_status | TEXT | | Enum | Throttle state (OK, THROTTLED, CAPPED) |
| delivery_status | TEXT | NOT NULL | Enum | PENDING, SENT, DELIVERED, OPENED, CLICKED, BOUNCED, FAILED |
| scheduled_at | TEXT | | ISO 8601 | When scheduled for send |
| attempted_at | TEXT | | ISO 8601 | When send was attempted |
| created_at | TEXT | NOT NULL | ISO 8601 | Record creation timestamp |

---

### lcs_event — Canonical event trail (rows vary)
Append-only audit log. Every pipeline action is recorded here. CANONICAL table.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| communication_id | TEXT | PK, NOT NULL | LCS-... | Communication chain identifier |
| created_at | TEXT | PK, NOT NULL | ISO 8601 | Event timestamp (composite PK with communication_id) |
| message_run_id | TEXT | NOT NULL | RUN-... | Run identifier |
| sovereign_company_id | TEXT | NOT NULL | UUID | Company identifier |
| entity_type | TEXT | NOT NULL | Enum | COMPANY or CONTACT |
| entity_id | TEXT | NOT NULL | UUID | Entity identifier |
| signal_set_hash | TEXT | NOT NULL | Hash | Signal type |
| frame_id | TEXT | NOT NULL | UUID | Message frame |
| adapter_type | TEXT | NOT NULL | Enum | Delivery adapter |
| channel | TEXT | NOT NULL | Enum | Delivery channel |
| delivery_status | TEXT | NOT NULL | Enum | Current delivery status |
| lifecycle_phase | TEXT | NOT NULL | Enum | Pipeline phase |
| event_type | TEXT | NOT NULL | Enum | What happened (COMPILED, CONSTRUCTED, SENT, DELIVERED, etc.) |
| lane | TEXT | NOT NULL | Enum | Delivery lane |
| agent_number | TEXT | NOT NULL | SA-NNN | Service agent |
| step_number | INTEGER | NOT NULL | 1-N | Step in pipeline sequence |
| step_name | TEXT | NOT NULL | Enum | Step name (CID, SID, MID, WEBHOOK) |
| payload | TEXT | | JSON | Event payload |
| adapter_response | TEXT | | JSON | Raw response from delivery adapter |
| intelligence_tier | INTEGER | | 2-5 | Intelligence tier at time of event |
| sender_identity | TEXT | | Free text | Sender display name |

---

### lcs_err0 — Pipeline error drain (rows vary)
Error table for LCS pipeline. ORBT strike tracking.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| error_id | TEXT | PK, NOT NULL | ERR-{ULID} | Unique error identifier |
| message_run_id | TEXT | NOT NULL | RUN-... | Which run failed |
| communication_id | TEXT | | LCS-... | Which communication chain |
| sovereign_company_id | TEXT | | UUID | Which company |
| failure_type | TEXT | NOT NULL | Enum | COMPANY_NOT_FOUND, NO_RECIPIENT, DELIVERY_FAILED, etc. |
| failure_message | TEXT | NOT NULL | Free text | Human-readable error description |
| lifecycle_phase | TEXT | | Enum | Pipeline phase at time of failure |
| adapter_type | TEXT | | Enum | Which adapter failed |
| orbt_strike_number | INTEGER | | 1-3 | Current strike count for this failure pattern |
| orbt_action_taken | TEXT | | Enum | AUTO_RETRY, ALT_CHANNEL, HUMAN_ESCALATION |
| orbt_alt_channel_eligible | INTEGER | | 0/1 | Whether alternate channel is available |
| orbt_alt_channel_reason | TEXT | | Free text | Why alt channel was/wasn't used |
| created_at | TEXT | NOT NULL | ISO 8601 | When error occurred |

---

### lcs_signal_registry — Signal type definitions (9 rows)
Config table. Defines all valid signal types. Extensible via INSERT.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| signal_set_hash | TEXT | PK, NOT NULL | Hash | Unique signal type identifier |
| signal_name | TEXT | NOT NULL | Free text | Human-readable signal name |
| lifecycle_phase | TEXT | NOT NULL | Enum | Which phase this signal applies to |
| signal_category | TEXT | NOT NULL | Enum | Category (DOL, PEOPLE, BLOG, TALENT) |
| description | TEXT | | Free text | What this signal means |
| freshness_window | TEXT | NOT NULL | Duration | How long signal is valid (e.g., 90d) |
| signal_validity_score | REAL | | 0.0-1.0 | Current validity score |
| validity_threshold | REAL | NOT NULL | 0.0-1.0 | Minimum score to be actionable |
| is_active | INTEGER | NOT NULL | 0/1 | Whether signal type is active |
| data_fetched_at | TEXT | | ISO 8601 | When signal data was last refreshed |
| data_expires_at | TEXT | | ISO 8601 | When signal data expires |
| created_at | TEXT | NOT NULL | ISO 8601 | Record creation timestamp |
| updated_at | TEXT | NOT NULL | ISO 8601 | Last modification timestamp |

---

### lcs_frame_registry — Message frame templates (11 rows)
Config table. Defines message templates per tier/channel. Extensible via INSERT.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| frame_id | TEXT | PK, NOT NULL | UUID | Unique frame identifier |
| frame_name | TEXT | NOT NULL | Free text | Frame name (OUT-HAMMER-01, OUT-GENERAL-V1, etc.) |
| lifecycle_phase | TEXT | NOT NULL | Enum | Which phase |
| frame_type | TEXT | NOT NULL | Enum | Frame type (OUTREACH, FOLLOWUP, NURTURE) |
| tier | INTEGER | NOT NULL | 2-5 | Intelligence tier this frame is designed for |
| required_fields | TEXT | NOT NULL | JSON array | Which CID fields must be present to use this frame |
| fallback_frame | TEXT | | UUID | Frame to use if this one can't be applied |
| channel | TEXT | | Enum | MG, HR, or NULL (any) |
| step_in_sequence | INTEGER | | 1-5 | Position in multi-touch sequence |
| description | TEXT | | Free text | What this frame does |
| cid_compilation_rule | TEXT | | JSON | Rules for CID compilation with this frame |
| sid_template_id | TEXT | | UUID | SID template to use |
| mid_sequence_type | TEXT | | Enum | Sequence type (SINGLE, MULTI) |
| mid_delay_hours | INTEGER | | Hours | Delay between sequence steps |
| mid_max_attempts | INTEGER | | 1-3 | Max delivery attempts |
| is_active | INTEGER | NOT NULL | 0/1 | Whether frame is active |
| created_at | TEXT | NOT NULL | ISO 8601 | Record creation timestamp |
| updated_at | TEXT | NOT NULL | ISO 8601 | Last modification timestamp |

---

### lcs_adapter_registry — Delivery adapter config (3 rows)
Config table. Defines delivery channels and their limits.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| adapter_type | TEXT | PK, NOT NULL | Enum | MG (Mailgun), HR (HeyReach), SH (SVG Brain) |
| adapter_name | TEXT | NOT NULL | Free text | Human-readable name |
| channel | TEXT | NOT NULL | Enum | EMAIL, LINKEDIN, AI |
| direction | TEXT | NOT NULL | Enum | OUTBOUND |
| description | TEXT | | Free text | What this adapter does |
| domain_rotation_config | TEXT | | JSON | Domain rotation settings (MG only) |
| health_status | TEXT | NOT NULL | Enum | HEALTHY, DEGRADED, DOWN |
| daily_cap | INTEGER | | Count | Maximum sends per day |
| sent_today | INTEGER | NOT NULL | Count | Sends today (resets at 07:00 UTC) |
| bounce_rate_24h | REAL | | 0.0-1.0 | 24-hour bounce rate |
| complaint_rate_24h | REAL | | 0.0-1.0 | 24-hour complaint rate |
| auto_pause_rules | TEXT | | JSON | Rules for auto-pausing (bounce threshold, etc.) |
| is_active | INTEGER | NOT NULL | 0/1 | Whether adapter is active |
| created_at | TEXT | NOT NULL | ISO 8601 | Record creation timestamp |
| updated_at | TEXT | NOT NULL | ISO 8601 | Last modification timestamp |

---

### lcs_domain_rotation — Mailgun sending domains (14 rows)
Tracks 14 sending domains with warmup, daily caps, and bounce monitoring.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| domain | TEXT | PK | domain.com | Sending domain (e.g., svgwv.com, svgagencymail.com) |
| sent_today | INTEGER | NOT NULL | Count | Emails sent today (resets 07:00 UTC) |
| daily_cap | INTEGER | NOT NULL | Count | Maximum sends per day for this domain |
| warmup_week | INTEGER | NOT NULL | 1-N | Current warmup week (affects daily cap) |
| last_sent_at | TEXT | | ISO 8601 | When last email was sent from this domain |
| total_sent | INTEGER | NOT NULL | Count | Lifetime total emails sent |
| bounce_count_24h | INTEGER | NOT NULL | Count | Bounces in last 24 hours |
| is_paused | INTEGER | NOT NULL | 0/1 | Whether domain is paused |
| pause_reason | TEXT | | Free text | Why domain was paused |
| created_at | TEXT | NOT NULL | ISO 8601 | Record creation timestamp |
| updated_at | TEXT | NOT NULL | ISO 8601 | Last modification timestamp |

---

### master_error — Global error table (rows vary)
All errors across all processes land here. HEIR/ORBT tracking.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| id | TEXT | PK | UUID | Unique error identifier |
| hub_id | TEXT | NOT NULL | Enum | Which hub (outreach, cl, client, sales) |
| sub_hub | TEXT | | Enum | Which sub-hub within the hub |
| component | TEXT | | Free text | Which component failed |
| process_id | TEXT | | PROC-NNN | Which process |
| process_number | TEXT | | NNN | Process number |
| sovereign_company_id | TEXT | | UUID | Which company (if applicable) |
| communication_id | TEXT | | LCS-... | Which communication chain |
| message_run_id | TEXT | | RUN-... | Which run |
| signal_queue_id | TEXT | | UUID | Which signal |
| error_type | TEXT | NOT NULL | Enum | Error classification |
| error_severity | TEXT | NOT NULL | Enum | CRITICAL, HIGH, MEDIUM, LOW |
| error_message | TEXT | NOT NULL | Free text | Human-readable error description |
| error_context | TEXT | | JSON | Additional context |
| orbt_mode | TEXT | NOT NULL | Enum | OPERATE, REPAIR, BUILD, TROUBLESHOOT_TRAIN |
| strike_number | INTEGER | | 1-3 | Current strike count |
| orbt_action_taken | TEXT | | Enum | AUTO_RETRY, ALT_CHANNEL, HUMAN_ESCALATION |
| tier0_gate | TEXT | | Enum | Which Tier 0 gate failed |
| tier0_validator | TEXT | | Enum | Which validator (IMO, CTB, Circle) |
| resolved | INTEGER | | 0/1 | Whether resolved |
| resolved_at | TEXT | | ISO 8601 | When resolved |
| resolved_by | TEXT | | Free text | Who/what resolved it |
| resolution_notes | TEXT | | Free text | How it was resolved |
| source_worker | TEXT | | Free text | Which CF Worker |
| environment | TEXT | | Enum | PRODUCTION, STAGING, DEV |
| created_at | TEXT | | ISO 8601 | When error occurred |

---

### escalation — Strike 3 escalation records (rows vary)
When master_error hits Strike 3, an escalation record is created for human diagnosis.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| id | TEXT | PK | UUID | Unique escalation identifier |
| master_error_id | TEXT | NOT NULL | UUID | FK → master_error.id |
| hub_id | TEXT | NOT NULL | Enum | Which hub |
| sub_hub | TEXT | | Enum | Which sub-hub |
| component | TEXT | | Free text | Which component |
| process_id | TEXT | | PROC-NNN | Which process |
| sovereign_company_id | TEXT | | UUID | Which company |
| communication_id | TEXT | | LCS-... | Which communication chain |
| strike_count | INTEGER | NOT NULL | 3 | Always 3 at escalation |
| error_type | TEXT | NOT NULL | Enum | Error classification |
| error_pattern | TEXT | | Free text | Pattern description |
| first_occurrence | TEXT | | ISO 8601 | When first strike happened |
| last_occurrence | TEXT | | ISO 8601 | When third strike happened |
| root_cause | TEXT | | Free text | Root cause analysis |
| troubleshoot_notes | TEXT | | Free text | Troubleshooting notes |
| fix_applied | TEXT | | Free text | What fix was applied |
| sop_updated | INTEGER | | 0/1 | Whether SOP was updated |
| sop_reference | TEXT | | Path | Path to updated SOP |
| fleet_directive | INTEGER | | 0/1 | Whether fleet-wide Airworthiness Directive issued |
| fleet_directive_desc | TEXT | | Free text | AD description |
| status | TEXT | NOT NULL | Enum | OPEN, IN_PROGRESS, RESOLVED, CLOSED |
| priority | TEXT | | Enum | CRITICAL, HIGH, MEDIUM, LOW |
| auditor_approved | INTEGER | | 0/1 | Whether auditor approved the fix |
| auditor_notes | TEXT | | Free text | Auditor feedback |
| escalated_at | TEXT | | ISO 8601 | When escalated |
| resolved_at | TEXT | | ISO 8601 | When resolved |
| signed_off_at | TEXT | | ISO 8601 | When auditor signed off |

---

### sales_sales_state — Sales pipeline state (rows vary)
Tracks each prospect through the 4-meeting sales cycle.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| sales_id | TEXT | PK | UUID | Unique sales process identifier |
| legal_name | TEXT | | Free text | Company legal name |
| domicile_state | TEXT | | 2-letter | Company state |
| current_phase | TEXT | | Enum | factfinder, insurance, systems, financials, closed |
| status | TEXT | | Enum | ACTIVE, PAUSED, WON, LOST |
| source | TEXT | | Enum | How prospect entered sales (LCS, REFERRAL, MANUAL) |
| version | INTEGER | | 1-N | Record version |
| created_at | TEXT | | ISO 8601 | When sales process started |
| updated_at | TEXT | | ISO 8601 | Last update |

---

# DATABASE 2: svg-d1-outreach-ops (73a285b8)
## 33 tables — Company footprint for outreach

_Full column reference for all outreach tables is documented in Process 010 PROCESS.md section 5. Tables include:_

| Table | Rows | Sub-Hub | Description |
|-------|------|---------|-------------|
| outreach_outreach | 32,704 | Spine | Universal join key — outreach_id |
| outreach_company_target | 32,704 | CT | Company targeting — geo, industry, employees, agent |
| outreach_dol | 36,247 | DOL | DOL filing summary |
| outreach_blog | 49,062 | Blog | Web presence — about_url, source_url, movement |
| outreach_people | 109,443 | People | Delivery contacts with engagement tracking |
| people_company_slot | 358,308 | People | CEO/CFO/HR slots (3 per company) |
| people_people_master | 160,423 | People | Person records — name, email, LinkedIn |
| dol_form_5500 | 14,252 | DOL | Federal filings detail |
| dol_schedule_a | 9,538 | DOL | Broker/insurance detail |
| dol_schedule_c | 18,246 | DOL | Service provider detail |
| dol_schedule_other | 67,164 | DOL | Other schedules (JSON) |
| coverage_service_agent | 9 | Coverage | Service agent definitions |
| coverage_service_agent_coverage | 21 | Coverage | Agent coverage zones |
| intake_people_staging | 24,727 | Staging | Pre-scraped contacts awaiting promotion |
| people_title_slot_mapping | — | Config | Title → slot type mapping |
| outreach_bit_scores | — | DEPRECATED | BIT scoring retired 2026-03-25 |

_See `factory/outreach/010-seed-d1/PROCESS.md` section 5 for full AI-ready column reference for every table above._

---

# DATABASE 3: imo-d1-global
## 1 table — Reference data

### us_zip_codes — US ZIP code reference (41,553 rows)
Static reference table. All US ZIP codes with lat/lon for haversine calculations.

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| zip | TEXT | PK | 5-digit | US ZIP code |
| city | TEXT | | Free text | Primary city name |
| state_code | TEXT | | 2-letter | US state code |
| state_name | TEXT | | Free text | Full state name |
| county | TEXT | | Free text | County name |
| latitude | REAL | | Decimal degrees | Latitude for haversine |
| longitude | REAL | | Decimal degrees | Longitude for haversine |
| timezone | TEXT | | IANA timezone | Timezone identifier |
| population | INTEGER | | Count | Population estimate |
| seeded_at | TEXT | NOT NULL | ISO 8601 | When seeded from Neon |

---

# DATABASE 4: imo-brain (77adcbfe)
## 15 tables — System knowledge store

### documents — Ingested knowledge documents (62 rows)

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| document_id | TEXT | PK | UUID | Unique document identifier |
| domain | TEXT | | Enum | Knowledge domain (system, tier0, doctrine, operations, etc.) |
| source_path | TEXT | | Path | Where the document came from |
| title | TEXT | | Free text | Document title |
| content_hash | TEXT | | SHA-256 | Hash for dedup |
| doc_version | TEXT | | Semver | Document version |
| ingested_at | TEXT | | ISO 8601 | When ingested |
| updated_at | TEXT | | ISO 8601 | Last update |

### chunks — Document chunks for vector search

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| chunk_id | TEXT | PK | UUID | Unique chunk identifier |
| document_id | TEXT | | UUID | FK → documents.document_id |
| chunk_index | INTEGER | | 0-N | Position within document |
| content | TEXT | | Free text | Chunk content |
| token_count | INTEGER | | Count | Token count for this chunk |
| created_at | TEXT | | ISO 8601 | When created |

### glossary — Term definitions

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| term_id | TEXT | PK | UUID | Unique term identifier |
| term | TEXT | | Free text | The term being defined |
| definition | TEXT | | Free text | Term definition |
| domain | TEXT | | Enum | Knowledge domain |
| source_document_id | TEXT | | UUID | FK → documents.document_id |
| created_at | TEXT | | ISO 8601 | When created |
| updated_at | TEXT | | ISO 8601 | Last update |

### decisions — ADR/decision records

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| decision_id | TEXT | PK | UUID | Unique decision identifier |
| adr_number | TEXT | | ADR-NNN | Architecture Decision Record number |
| title | TEXT | | Free text | Decision title |
| status | TEXT | | Enum | accepted, superseded, deprecated |
| domain | TEXT | | Enum | Knowledge domain |
| summary | TEXT | | Free text | Decision summary |
| source_document_id | TEXT | | UUID | FK → documents.document_id |
| decided_at | TEXT | | ISO 8601 | When decision was made |
| created_at | TEXT | | ISO 8601 | When recorded |
| updated_at | TEXT | | ISO 8601 | Last update |

### relationships — Entity relationships (graph)

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| relationship_id | TEXT | PK | UUID | Unique relationship identifier |
| source_type | TEXT | | Enum | Source entity type (document, term, decision) |
| source_id | TEXT | | UUID | Source entity ID |
| target_type | TEXT | | Enum | Target entity type |
| target_id | TEXT | | UUID | Target entity ID |
| relation | TEXT | | Enum | Relationship type (REFERENCES, DEPENDS_ON, SUPERSEDES) |
| weight | REAL | | 0.0-1.0 | Relationship strength |
| created_at | TEXT | | ISO 8601 | When created |

_Error tables (documents_error, glossary_error, decisions_error, relationships_error) mirror their canonical counterparts with additional error_message and error_context columns._

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-31 |
| Last Modified | 2026-03-31 |
| Version | 1.0.0 |
| Source | Live D1 introspection via claude-sandbox + wrangler CLI |
| Authority | barton-outreach-core/doctrine/OSAM.md, FOUNDATIONAL_BEDROCK.md §4 (CQRS) |
| Location | Barton-Processes/D1_DATA_DICTIONARY.md |

# ERD — Process 200: People Worker v2
## Entity Relationship Diagram — D1 Tables, Columns, FK Chain

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — svg-agency/200-people-worker |
| **OSAM Authority** | barton-outreach-core/doctrine/OSAM.md v1.1.2 |
| **Data Flow** | factory/svg-agency/DATA_FLOW.md |
| **Schema Source** | Live D1 introspection (2026-03-26) |
| **Last Updated** | 2026-03-26 |

---

## D1 Bindings

| Binding | Database | ID | Access |
|---------|----------|-----|--------|
| `D1_OUTREACH` | svg-d1-outreach-ops | 73a285b8 | READ/WRITE |
| `D1_SPINE` | svg-d1-spine | 641a9a1e | READ ONLY (company name) |

---

## Entity Relationship Diagram

```
D1_OUTREACH (svg-d1-outreach-ops)
═══════════════════════════════════

outreach_outreach (32,704 — spine, universal join key)
┌─────────────────────────────────┐
│ outreach_id          TEXT PK    │──────────────────┐
│ sovereign_id         TEXT       │                  │
│ domain               TEXT       │                  │
│ ein                  TEXT       │                  │
│ created_at           TEXT       │                  │
│ updated_at           TEXT       │                  │
└─────────────────────────────────┘                  │
                                                     │
outreach_company_target (32,704 — targeting)          │
┌─────────────────────────────────┐                  │
│ target_id            TEXT PK    │                  │
│ outreach_id          TEXT FK────│──────────────────┤
│ company_unique_id    TEXT       │                  │
│ city                 TEXT       │                  │
│ state                TEXT       │                  │
│ postal_code          TEXT       │                  │
│ industry             TEXT       │                  │
│ employees            INTEGER    │                  │
│ email_method         TEXT       │                  │
│ service_agent_id     TEXT       │ ← NEW (SEED fix) │
│ service_agent_name   TEXT       │ ← NEW            │
│ service_agent_number TEXT       │ ← NEW            │
│ ...                             │                  │
└─────────────────────────────────┘                  │
                                                     │
people_company_slot (98,112 — CEO/CFO/HR slots)      │
┌─────────────────────────────────┐                  │
│ slot_id              TEXT PK    │                  │
│ outreach_id          TEXT FK────│──────────────────┤
│ company_unique_id    TEXT       │                  │
│ slot_type            TEXT       │  (CEO, CFO, HR)  │
│ person_unique_id     TEXT FK────│──┐               │
│ is_filled            INTEGER    │  │               │
│ filled_at            TEXT       │  │               │
│ confidence_score     REAL       │  │               │
│ source_system        TEXT       │  │               │
│ slot_phone           TEXT       │  │               │
│ slot_phone_source    TEXT       │  │               │
│ created_at           TEXT       │  │               │
│ updated_at           TEXT       │  │               │
└─────────────────────────────────┘  │               │
                                      │               │
people_people_master (51,582)         │               │
┌─────────────────────────────────┐  │               │
│ unique_id            TEXT PK────│──┘               │
│ company_unique_id    TEXT       │                   │
│ company_slot_unique_id TEXT     │                   │
│ first_name           TEXT       │                   │
│ last_name            TEXT       │                   │
│ full_name            TEXT       │                   │
│ title                TEXT       │                   │
│ seniority            TEXT       │                   │
│ department           TEXT       │                   │
│ email                TEXT       │                   │
│ work_phone_e164      TEXT       │                   │
│ linkedin_url         TEXT       │                   │
│ email_verified       INTEGER    │                   │
│ outreach_ready       INTEGER    │                   │
│ source_system        TEXT       │                   │
│ last_enrichment_attempt TEXT    │                   │
│ ...                             │                   │
└─────────────────────────────────┘                   │
                                                      │
outreach_blog (49,062 — web content)                  │
┌─────────────────────────────────┐                   │
│ blog_id              TEXT       │                   │
│ outreach_id          TEXT FK────│───────────────────┤
│ source_url           TEXT       │                   │
│ about_url            TEXT       │ ← team/about pages│
│ news_url             TEXT       │                   │
│ context_summary      TEXT       │                   │
│ extraction_method    TEXT       │                   │
│ last_extracted_at    TEXT       │                   │
└─────────────────────────────────┘                   │
                                                      │
outreach_dol (36,247 — DOL summary)                   │
┌─────────────────────────────────┐                   │
│ dol_id               TEXT       │                   │
│ outreach_id          TEXT FK────│───────────────────┤
│ ein                  TEXT       │                   │
│ filing_present       INTEGER    │                   │
│ carrier              TEXT       │                   │
│ broker_or_advisor    TEXT       │                   │
│ renewal_month        INTEGER    │                   │
└─────────────────────────────────┘                   │
                                                      │
dol_form_5500 (14,252 — federal filings)              │
┌─────────────────────────────────┐                   │
│ ack_id               TEXT PK    │                   │
│ outreach_id          TEXT FK────│───────────────────┘
│ sponsor_dfe_name     TEXT       │ ← legal company name
│ spons_dfe_mail_us_city TEXT     │
│ spons_dfe_mail_us_state TEXT    │
│ sponsor_dfe_ein      TEXT       │
│ tot_active_partcp_cnt INTEGER   │
│ form_year            TEXT       │
│ ...                             │
└─────────────────────────────────┘

intake_people_staging (24,727 — pending promotion)
┌─────────────────────────────────┐
│ id                   INTEGER PK │
│ company_unique_id    TEXT       │
│ raw_name             TEXT       │
│ first_name           TEXT       │
│ last_name            TEXT       │
│ raw_title            TEXT       │
│ normalized_title     TEXT       │
│ mapped_slot_type     TEXT       │
│ linkedin_url         TEXT       │
│ email                TEXT       │
│ confidence_score     REAL       │
│ status               TEXT       │ (pending/promoted)
└─────────────────────────────────┘

people_title_slot_mapping (43 — deterministic)
┌─────────────────────────────────┐
│ id                   INTEGER PK │
│ title_pattern        TEXT       │
│ slot_type            TEXT       │
│ priority             INTEGER    │
└─────────────────────────────────┘


D1_SPINE (svg-d1-spine) — READ ONLY
═══════════════════════════════════

cl_company_identity (117,154 — sovereign records)
┌─────────────────────────────────┐
│ company_unique_id    TEXT PK    │
│ canonical_name       TEXT       │ ← company name for search
│ company_domain       TEXT       │
│ linkedin_company_url TEXT       │
│ state_code           TEXT       │
│ outreach_id          TEXT       │ ← join to outreach D1
│ ...                             │
└─────────────────────────────────┘
```

---

## FK Chain

```
cl_company_identity.outreach_id → outreach_outreach.outreach_id (spine → outreach)
outreach_outreach.outreach_id   → outreach_company_target.outreach_id (1:1)
outreach_outreach.outreach_id   → people_company_slot.outreach_id (1:N, 3 per company)
people_company_slot.person_unique_id → people_people_master.unique_id (N:1)
outreach_outreach.outreach_id   → outreach_blog.outreach_id (1:1)
outreach_outreach.outreach_id   → outreach_dol.outreach_id (1:1)
outreach_outreach.outreach_id   → dol_form_5500.outreach_id (1:N)
intake_people_staging.company_unique_id → outreach_company_target.company_unique_id
```

---

## Process 200 Access Pattern

| Operation | Table | Access | Purpose |
|-----------|-------|--------|---------|
| READ | `people_company_slot` | D1_OUTREACH | Find empty/filled slots |
| READ | `people_people_master` | D1_OUTREACH | Current contact details for movement check |
| READ | `outreach_company_target` | D1_OUTREACH | City, state, agent assignment |
| READ | `outreach_blog` | D1_OUTREACH | About/team page URLs |
| READ | `outreach_dol` | D1_OUTREACH | Filing present (trust signal) |
| READ | `dol_form_5500` | D1_OUTREACH | Legal company name |
| READ | `intake_people_staging` | D1_OUTREACH | Pre-discovered people to promote |
| READ | `people_title_slot_mapping` | D1_OUTREACH | Title → slot type |
| READ | `cl_company_identity` | D1_SPINE | Company name for search queries |
| WRITE | `people_people_master` | D1_OUTREACH | Create/update contact records |
| WRITE | `people_company_slot` | D1_OUTREACH | Fill slots, update confidence |
| WRITE | `intake_people_staging` | D1_OUTREACH | Mark as promoted |

---

## Data Counts (post-SEED fix, 2026-03-26)

| Table | Rows | Notes |
|-------|------|-------|
| outreach_company_target | 32,704 | 100% agent-assigned |
| people_company_slot | 98,112 | 3 per company, 100% coverage |
| people_people_master | 51,582 | 99.7% slot→person match |
| outreach_blog | 49,062 | About URLs available |
| outreach_dol | 36,247 | DOL trust signal |
| dol_form_5500 | 14,252 | Legal company names |
| intake_people_staging | 24,727 | Pending promotion |
| people_title_slot_mapping | 43 | Deterministic patterns |
| cl_company_identity | 117,154 | Company names (spine) |

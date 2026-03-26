# SVG Agency — Data Flow & Plumbing
# Authority: barton-outreach-core/doctrine/OSAM.md (v1.1.2, LOCKED)
# Verified: 2026-03-26 (pressure tested against live D1)

---

## The Plumbing (Constants — this does not change)

### Layer 1: CL Hub (Sovereign — Neon)

```
cl.company_identity (117,154 companies)
├── company_unique_id (PK, sovereign ID)
├── company_name, company_domain, linkedin_company_url
├── state_code
├── eligibility_status, final_outcome
├── outreach_id ←── write-once pointer to Outreach
├── sales_process_id ←── write-once pointer to Sales
└── client_id ←── write-once pointer to Client
```

**CL mints the sovereign ID. Outreach receives it. CL is read-only to all downstream.**

### Layer 2: Outreach Hub (Spine — Neon)

```
outreach.outreach (spine table — universal join key: outreach_id)
├── outreach_id (PK, minted here)
├── sovereign_id → cl.company_identity.company_unique_id
├── domain (company website)
├── ein (EIN from DOL)
│
├──→ outreach.company_target (1:1)
│    ├── outreach_id, company_unique_id
│    ├── city, state, postal_code, country
│    ├── industry, employees
│    ├── email_method, method_type, confidence_score
│    └── outreach_status, execution_status
│
├──→ outreach.dol (1:1)
│    ├── outreach_id, ein
│    ├── filing_present, funding_type
│    ├── carrier, broker_or_advisor
│    └── renewal_month, outreach_start_month
│
├──→ outreach.blog (1:1)
│    ├── outreach_id
│    ├── context_summary, source_url
│    ├── about_url, news_url
│    └── extraction_method, last_extracted_at
│
├──→ outreach.people (1:N — delivery contacts)
│    ├── outreach_id, person_id
│    ├── slot_type, email, email_verified
│    ├── lifecycle_state, funnel_membership
│    └── email_open_count, email_click_count, email_reply_count
│
├──→ people.company_slot (1:N — 3 slots per company: CEO, CFO, HR)
│    ├── outreach_id, slot_id (PK)
│    ├── slot_type, person_unique_id
│    ├── is_filled, filled_at
│    └── source_system, confidence_score
│         │
│         └──→ people.people_master (N:1 via person_unique_id → unique_id)
│              ├── unique_id (PK), company_unique_id
│              ├── first_name, last_name, full_name, title
│              ├── email, linkedin_url
│              ├── email_verified, outreach_ready
│              └── source_system, last_enrichment_attempt
│
├──→ outreach.bit_scores (1:1)
│    ├── outreach_id
│    ├── score, score_tier
│    └── people_score, dol_score, blog_score, talent_flow_score
│
└──→ dol.form_5500 (1:N via outreach_id, also via ein)
     ├── ack_id (PK), outreach_id, sponsor_dfe_ein
     ├── sponsor_dfe_name (legal company name from federal filing)
     ├── spons_dfe_mail_us_city, spons_dfe_mail_us_state
     ├── tot_active_partcp_cnt, tot_partcp_boy_cnt
     └── form_year, filing_status, date_received
          │
          ├──→ dol.schedule_a (1:N via ack_id — broker/insurance)
          ├──→ dol.schedule_c (1:N via ack_id — service providers)
          └──→ dol.schedule_other (1:N via ack_id — all other schedules)
```

### Layer 3: Coverage (Gate 0 — Neon)

```
coverage.service_agent (3 active agents)
├── Dave Allan (SA-001) — anchor 26739 (WV), 100mi
├── Jeff Mussolino (SA-002) — anchor 21742 (MD), 100mi
└── David Vang (SA-003) — anchor 28461 (NC), 100mi

coverage.service_agent_coverage (intent: anchor_zip + radius_miles)
    │
    └──→ coverage.v_service_agent_coverage_zips (VIEW — NOT a table)
         Haversine against reference.us_zip_codes (41,551 ZIPs)
         Expands each agent's intent into all ZIP codes within radius
```

**Gate 0 filter (runs in Neon during SEED):**
```
outreach.company_target.postal_code
  JOIN coverage.v_service_agent_coverage_zips ON postal_code = zip
  → ~28K companies pass Gate 0
```

### Layer 4: SEED (Neon → D1)

```
NEON (vault, 117K companies)
    │
    ├── Gate 0: coverage filter (~28K pass)
    │
    └── SEED: pull full footprint for passing companies
         │
         ▼
D1: svg-d1-outreach-ops (workspace)
    ├── outreach_outreach          32,704 rows
    ├── outreach_company_target    32,704 rows
    ├── outreach_dol               36,247 rows
    ├── outreach_blog              49,062 rows
    ├── outreach_people           109,443 rows
    ├── outreach_bit_scores         7,002 rows
    ├── people_company_slot        43,209 rows
    ├── people_people_master       32,106 rows
    ├── dol_form_5500              14,252 rows
    ├── dol_schedule_a             17,890 rows  (was 9,538 pre-full-SEED)
    ├── dol_schedule_c             33,810 rows  (was 18,246 pre-full-SEED)
    ├── dol_schedule_other        105,088 rows
    ├── intake_people_staging      24,727 rows  (web-scraped, pending promotion)
    ├── people_title_slot_mapping      43 rows  (title → slot deterministic mapping)
    ├── coverage_service_agent          9 rows  (reference)
    └── coverage_service_agent_coverage 21 rows (reference)
```

**Once in D1, Gate 0 is already applied. Every company is agent-assigned. No re-filtering.**

### Layer 5: D1 (workspace — processes operate here)

```
SEED → WORK → PUSH

SEED: Neon vault → D1 workspace (already done)
WORK: Processes read D1, fetch external data, write results to D1
PUSH: End of cycle, promote verified results D1 → Neon vault
```

**Rules:**
- No Neon queries during WORK phase
- All process reads from D1
- All process writes to D1
- PUSH promotes verified data back to Neon vault

---

## Join Keys (verified against live D1)

| From | To | Join Key | Verified |
|------|----|----------|----------|
| `outreach_outreach` | `outreach_company_target` | `outreach_id` | PASS (32,704:32,704) |
| `outreach_outreach` | `outreach_dol` | `outreach_id` | PASS (36,247 matched) |
| `outreach_outreach` | `outreach_blog` | `outreach_id` | PASS (49,062 matched) |
| `outreach_outreach` | `outreach_people` | `outreach_id` | PASS (18,647 companies) |
| `outreach_outreach` | `people_company_slot` | `outreach_id` | PASS (14,403 companies) |
| `outreach_outreach` | `outreach_bit_scores` | `outreach_id` | PASS (7,002 matched) |
| `people_company_slot` | `people_people_master` | `person_unique_id` → `unique_id` | **FAIL** (5.2% match rate) |
| `dol_form_5500` | `outreach_dol` | `outreach_id` | PASS (4,698 companies) |
| `outreach_outreach` | `cl_company_identity` | `sovereign_id` → `company_unique_id` | PASS (spine D1 read-only) |

### OSAM Join Key Correction Needed
OSAM declares `people_id` for slot→person and people→master joins.
**Actual key:** `person_unique_id` → `unique_id`. Needs ADR correction.

---

## Known Data Gaps (as of 2026-03-26)

| Gap | Impact | Fix |
|-----|--------|-----|
| 94.8% orphan on slot→person join | Process 200 can't look up contact details for most filled slots | Re-SEED people_people_master for all referenced person_unique_ids |
| 18K companies have no slots | ~56% of companies in D1 have no CEO/CFO/HR slots | Process 200 can't fill slots that don't exist — need slot creation SEED |
| outreach_people.outreach_id partially null | Only 18,647 of 32,704 companies have delivery contacts linked | Legacy data — outreach_id wasn't always populated |
| 5 OSAM views not in D1 | Marketing eligibility, sovereign completion, manual overrides, ICP filtered, form_5500_sf | Views are Neon-only (materialized views can't be SEEDed) |

---

## Forbidden Paths (from OSAM)

| From | To | Why |
|------|----|-----|
| Any outreach table | Any outreach table (direct cross-sub-hub) | Must route through spine (outreach_outreach) |
| Any table | cl.* (WRITE) | CL is authority — READ only |
| Any table | hunter_company / hunter_contact | SOURCE tables — not query surfaces |
| outreach.* | sales.* or client.* | Cross-hub isolation |

---

## Process Access Patterns

Each SVG process declares which tables it reads and writes.
All reads/writes are to D1 outreach unless noted.

| Process | Reads | Writes |
|---------|-------|--------|
| 100 LCS Pipeline | outreach_company_target, outreach_dol, people_company_slot, people_people_master, outreach_blog | lcs_signal_queue, lcs_cid, lcs_sid, lcs_mid, lcs_event, lcs_err0 (spine D1) |
| 200 People Worker | people_company_slot, people_people_master, outreach_company_target, outreach_blog, intake_people_staging, people_title_slot_mapping, cl_company_identity (spine, read-only) | people_people_master, people_company_slot |
| 300 Blog Worker | outreach_blog, outreach_company_target | outreach_blog |
| 400 DOL Views | dol_form_5500, dol_schedule_a, dol_schedule_c, dol_schedule_other | Read-only (views in Neon) |
| 500 Talent Flow | people_people_master (linkedin_url), people_company_slot | people_people_master (movement signals) |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-26 |
| Authority | barton-outreach-core/doctrine/OSAM.md v1.1.2 |
| Verified Against | Live D1 via wrangler CLI |
| Status | ACTIVE |
| Change Protocol | Update this doc when SEED changes or tables are added |

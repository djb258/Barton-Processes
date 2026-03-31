# OSAM — Process 200: People Worker
# Semantic Access Map — subset of hub OSAM
# Authority: barton-outreach-core/doctrine/OSAM.md v1.1.2
# Created: 2026-03-26

---

## What This Process Accesses

Process 200 fills CEO/CFO/HR slots and detects movement.
It reads from multiple sub-hubs but writes ONLY to the people tables.

---

## READ Access

### D1_OUTREACH (svg-d1-outreach-ops)

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `people_company_slot` | Empty/filled slots, slot_type, person_unique_id | `outreach_id` |
| `people_people_master` | Contact details (name, email, LinkedIn) | `unique_id` ← slot.person_unique_id |
| `outreach_company_target` | City, state, industry, employees, agent assignment | `outreach_id` |
| `outreach_blog` | about_url for team page scraping | `outreach_id` |
| `outreach_dol` | filing_present (DOL trust signal) | `outreach_id` |
| `dol_form_5500` | sponsor_dfe_name (legal company name) | `outreach_id` |
| `intake_people_staging` | Pre-discovered people to promote | `company_unique_id` |
| `people_title_slot_mapping` | Title pattern → slot type (deterministic) | n/a (lookup) |

### D1_SPINE (svg-d1-spine) — READ ONLY

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `cl_company_identity` | canonical_name, company_domain, linkedin_company_url | `outreach_id` |

---

## WRITE Access (these tables ONLY)

| Table | What It Writes | When |
|-------|---------------|------|
| `people_people_master` | INSERT new contacts, UPDATE existing | Pass 0, 1, 2 |
| `people_company_slot` | UPDATE is_filled, person_unique_id, filled_at | Pass 0, 1, 2 |
| `intake_people_staging` | UPDATE status = 'promoted' | Pass 0 only |

---

## Forbidden Paths

| Action | Why |
|--------|-----|
| WRITE to cl_company_identity | CL is authority — read only |
| WRITE to outreach_company_target | Targeting data — not this process |
| WRITE to outreach_blog | Blog worker (300) owns this |
| WRITE to outreach_dol | DOL views (400) owns this |
| WRITE to D1_SPINE | Spine is read-only for all outreach processes |
| Query Neon | Vault only — SEED phase, not WORK |
| Cross sub-hub join without spine | Route through outreach_outreach.outreach_id |

---

## Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Which slots need filling? | `people_company_slot` | `WHERE is_filled = 0` |
| What's the person's name? | `people_people_master` | `first_name`, `last_name` |
| What's the company name? | `cl_company_identity` (spine) | `canonical_name` |
| What's the company name? (DOL) | `dol_form_5500` | `sponsor_dfe_name` |
| Where is the company? | `outreach_company_target` | `city`, `state` |
| Does company have a team page? | `outreach_blog` | `about_url` |
| Is this DOL-linked? | `outreach_dol` | `filing_present` |
| Which agent owns this? | `outreach_company_target` | `service_agent_name` |
| What slot for this title? | `people_title_slot_mapping` | `title_pattern → slot_type` |
| Pre-discovered people? | `intake_people_staging` | `WHERE status = 'pending'` |

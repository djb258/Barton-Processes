> **ARCHIVED 2026-04-29** — Consolidated into PROCESS-UT.md and DOCTRINE.md during UT v2.7.0 standardization. See sibling files at folder root.

# OSAM → D1 Mapping — Outreach Hub
# Source: barton-outreach-core/doctrine/OSAM.md (v1.1.2, LOCKED)
# Verified Against: Live D1 via wrangler introspection (2026-03-26)
# Authority: OSAM is the contract. This maps Neon names to D1 names.

---

## Table Name Mapping (Neon → D1)

Neon uses schema-qualified names. D1 flattens schema prefix with underscore.

| OSAM (Neon) | D1 (svg-d1-outreach-ops) | Rows | Status |
|-------------|--------------------------|------|--------|
| `outreach.outreach` | `outreach_outreach` | 32,704 | LOADED |
| `outreach.company_target` | `outreach_company_target` | 32,704 | LOADED |
| `outreach.dol` | `outreach_dol` | 36,247 | LOADED |
| `outreach.people` | `outreach_people` | 109,443 | LOADED |
| `outreach.blog` | `outreach_blog` | 49,062 | LOADED |
| `outreach.bit_scores` | `outreach_bit_scores` | 7,002 | LOADED |
| `people.company_slot` | `people_company_slot` | 43,209 | LOADED |
| `people.people_master` | `people_people_master` | 32,106 | LOADED |
| `dol.form_5500` | `dol_form_5500` | 14,252 | LOADED |
| `dol.schedule_a_part1` | `dol_schedule_a` | 17,890 | LOADED |
| `dol.schedule_c_part1_item2` | `dol_schedule_c` | 33,810 | LOADED |
| `dol.schedule_*` (others) | `dol_schedule_other` | 105,088 | LOADED |
| `cl.company_identity` | `cl_company_identity` (SPINE D1) | 117,154 | LOADED |

### Additional D1 Tables (not in OSAM)

| D1 Table | Rows | Purpose |
|----------|------|---------|
| `intake_people_staging` | 24,727 | Staging for web-scraped people (has linkedin_url, names, titles) |
| `people_title_slot_mapping` | 43 | Title pattern → slot type deterministic mapping |
| `coverage_service_agent` | 9 | Service agents (3 active) |
| `coverage_service_agent_coverage` | 21 | Agent territory zones (zip + radius) |
| `outreach_appointments` | 487 | Historical appointments |
| `outreach_signal_output` | 0 | Signal output (empty) |
| `outreach_company_hub_status` | varies | Hub completion status per company |
| `lcs_message_ledger` | varies | LCS message tracking |
| `lcs_message_error` | varies | LCS message errors |
| `lcs_sender_profile_registry` | varies | Sender profiles |

---

## Join Path Verification (Pressure Tested 2026-03-26)

### PASS — All records match

| # | Join Path | Join Key | OSAM Direction | Result |
|---|-----------|----------|---------------|--------|
| 1 | `outreach_outreach` → `outreach_company_target` | `outreach_id` | 1:1 | **PASS** — 32,704 : 32,704 (100% match) |
| 2 | `outreach_outreach` → `outreach_dol` | `outreach_id` | 1:1 | **PASS** — 36,247 DOL records, all matched to spine |
| 3 | `outreach_outreach` → `outreach_blog` | `outreach_id` | 1:1 | **PASS** — 49,062 blog records, all matched to spine |
| 7 | `outreach_outreach` → `outreach_bit_scores` | `outreach_id` | 1:1 | **PASS** — 7,002 scores, all matched to spine |

### PASS WITH NOTES — Partial coverage (by design)

| # | Join Path | Join Key | Result | Notes |
|---|-----------|----------|--------|-------|
| 4 | `outreach_outreach` → `outreach_people` | `outreach_id` | **PASS** — 18,647 of 32,704 companies have delivery contacts | 109,443 total people records. Not all companies have outreach_id populated (legacy data). |
| 5 | `outreach_outreach` → `people_company_slot` | `outreach_id` | **PASS** — 14,403 companies have slots | 43,209 slots across 14,403 companies (3 slots per company). ~18K companies have no slots yet. |
| 8 | `dol_form_5500` → `outreach_dol` | `outreach_id` | **PASS** — 4,698 companies have detailed DOL filings | 14,252 filings across 4,698 companies (multiple years). |

### FAIL — Critical data gap

| # | Join Path | Join Key | Result | Impact |
|---|-----------|----------|--------|--------|
| 6 | `people_company_slot` → `people_people_master` | `person_unique_id` → `unique_id` | **FAIL** — 20,649 filled slots but only 1,072 match (5.2%) | **19,577 filled slots point to person records that DON'T EXIST in D1.** The people_master SEED only brought 32,106 records but the slot table references ~20K person IDs that aren't in the D1 copy. |

---

## OSAM Join Key Correction

The OSAM declares these joins:

```
| people.company_slot | people.people_master | people_id | N:1 |
| outreach.people     | people.people_master | people_id | N:1 |
```

**Actual join key in D1 (and Neon):**
- `people_company_slot.person_unique_id` → `people_people_master.unique_id`
- NOT `people_id`

The OSAM uses `people_id` but the actual column is `person_unique_id` on the slot table and `unique_id` on people_master. This should be corrected in the OSAM via ADR.

---

## Critical Finding: 94.8% Orphan Rate on Slot → Person Join

**20,649 slots are marked `is_filled = 1`**
**Only 1,072 have a matching `people_people_master` record in D1**
**19,577 slots (94.8%) point to person IDs that exist in Neon but were NOT seeded to D1**

### Root Cause
The `people_people_master` SEED brought 32,106 records from Neon. But the 20,649 filled slots reference `person_unique_id` values that are spread across the full Neon `people.people_master` table (182,842 rows in Neon). The D1 SEED didn't filter by agent-assigned companies — it brought a subset.

### Impact
- Process 200 cannot look up contact details (name, email, LinkedIn URL) for 94.8% of filled slots
- The LCS pipeline's compiler-v2 would fail to find recipients for most companies
- Movement detection has no baseline data for these people

### Fix Required
Re-SEED `people_people_master` from Neon filtered to match all `person_unique_id` values referenced by filled slots in `people_company_slot`. This is a SEED operation, not a Process 200 code fix.

---

## Service Agent Territories (Gate 0)

| Agent | Number | Anchor Zip | Radius | Region |
|-------|--------|-----------|--------|--------|
| Dave Allan | SA-001 | 26739 | 100mi | WV |
| Jeff Mussolino | SA-002 | 21742 | 100mi | MD |
| David Vang | SA-003 | 28461 | 100mi | NC |

Only companies within these territories are in the outreach D1. ~28K of 117K total companies.

---

## CL Authority (Read-Only from Spine D1)

Per OSAM: "CL is authority; only READ permitted"

| Question | Table | D1 Location | Join Key |
|----------|-------|-------------|----------|
| Company name | `cl_company_identity` | svg-d1-spine | `outreach_id` or `company_unique_id` |
| Company domain | `cl_company_identity` | svg-d1-spine | `outreach_id` |
| LinkedIn company URL | `cl_company_identity` | svg-d1-spine | `outreach_id` |
| State code | `cl_company_identity` | svg-d1-spine | `outreach_id` |
| Eligibility status | `cl_company_identity` | svg-d1-spine | `outreach_id` |

Process 200 binds `D1_SPINE` read-only for this data.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-26 |
| Source OSAM | barton-outreach-core/doctrine/OSAM.md v1.1.2 |
| Verified Against | Live D1 via wrangler CLI |
| Pressure Test | 10 join paths tested, 1 FAIL (slot→person orphan) |
| Status | ACTIVE — pending people_master re-SEED |

# PROCESS: People Slot Filler
## Finds the person who holds each slot (CEO, CFO, HR) at a company — name and title only
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-200 |
| Name | People Slot Filler |
| Business Silo | svg-agency |
| CTB Position | factory/outreach/200-people-worker |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | 2026-03-26 (v1 — needs rebuild for v2 scope) |
| BAR Reference | BAR-52 |
| Deployed URL | people-worker-200.svg-outreach.workers.dev |
| Cron | Daily `0 6 * * *` (6am UTC) |
| Runtime | CF Worker (daily cron, batched) |

---

## 2. WHY THIS EXISTS

A slot without a person is an empty chair. You can't email an empty chair. You can't send a LinkedIn message to an empty chair. This process finds WHO sits in the CEO, CFO, and HR chairs at each company.

That's ALL it does — find the person's name and title. Email discovery is Process 201. LinkedIn discovery is Process 202. This process identifies the human. The other processes find how to reach them.

After 200 fills a slot, the orchestrator conditionally calls:
- 201 (email) — if the person has no verified email
- 202 (LinkedIn) — if the person has no LinkedIn URL

Some sources return name + email + LinkedIn together. When that happens, write all of it — don't call 201/202 for data you already have.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Daily cron. Runs after Process 300 (Blog) has mapped web presence.
2. **"How do we get it?"** — Three passes, escalating cost. Free data first.

### Input
- Empty slots from `people_company_slot` where `is_filled = 0`
- Blog data from Process 300 (`outreach_blog.context_summary` — extracted names/titles)
- Staging data in D1 (`intake_people_staging` — pre-scraped records)
- Company names from `cl_company_identity.canonical_name`

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| **Pass 0 — Staging (FREE)** | | | | |
| 1 | `intake_people_staging` records | Match staged names/titles to empty slots via `people_title_slot_mapping`. Create person record. Fill slot. | Slots filled from existing staged data | D1 queries (free) |
| **Pass 1 — Blog Data (FREE)** | | | | |
| 2 | Process 300 output (`context_summary` JSON) | Parse extracted names/titles. Match to empty slots by title → slot type. Create person record. Fill slot. | Slots filled from blog extraction | D1 queries (free) |
| 3 | Companies with `about_url` but no extraction | Fetch about page directly, extract names/titles with HTML parser. Match to slots. | Slots filled from direct fetch | CF Workers fetch (free) |
| **Pass 2 — Search (CHEAP)** | | | | |
| 4 | Remaining empty slots | Build Startpage query for the slot type + company. Parse results for name + title. Fill slot. | Slots filled from search | Startpage + DataImpulse proxy |

### Output
- Person record in `people_people_master` with name + title
- Slot updated: `is_filled = 1`, `person_unique_id` set, `source_system` recorded
- If the source also provides email or LinkedIn, write those too (skip 201/202 for that person)

### Circle (Bedrock §5)
After each run, check fill rates by slot type. If fill rate doesn't improve after 3 runs, investigate — parser may need tuning, blog data may be stale, or search queries may need refinement.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | Slots, people master, staging, blog, company target |
| svg-d1-spine | D1 | 641a9a1e | READ | cl_company_identity (canonical_name for search) |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_USER | imo-creator | dev | Pass 2 — DataImpulse proxy |
| PROXY_PASS | imo-creator | dev | Pass 2 — DataImpulse proxy |

**Tool Priority (Well Drinks First):**
1. Staging data (free, already in D1) — Pass 0
2. Blog data from Process 300 (free) — Pass 1
3. Direct fetch of about pages (free) — Pass 1
4. Startpage search via proxy (cheap) — Pass 2

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `people_company_slot` | Empty slots (is_filled = 0) | `outreach_id` |
| `intake_people_staging` | Pre-scraped names/titles | `company_unique_id` |
| `outreach_blog` | Extracted names/titles from about pages | `outreach_id` |
| `outreach_company_target` | City, state for search context | `outreach_id` |
| `cl_company_identity` (spine) | Canonical name for search queries | `outreach_id` |
| `people_title_slot_mapping` | Title → slot type mapping rules | `title_pattern` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `people_people_master` | New person record (name, title, and any email/LinkedIn if source provides it) | All passes |
| `people_company_slot` | is_filled=1, person_unique_id, source_system | All passes |
| `intake_people_staging` | status='promoted' on consumed records | Pass 0 |

### Forbidden Paths

| Action | Why |
|--------|-----|
| Skip Pass 0 and 1 to go to paid search | Free before cheap. Always. |
| Fill a slot without a name | A name is the minimum. No name = not filled. |
| Run before Process 300 | 300 feeds free data to 200. Always run 300 first. |
| Call 201/202 from inside this process | Orchestrator handles that. 200 just fills the slot. |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants
- 3 slot types per company: CEO, CFO, HR
- Pass order: staging (free) → blog data (free) → search (cheap). Never skip.
- A slot is "filled" when it has a person_unique_id pointing to a record with at least a name.
- 300 runs before 200. Always.
- Title-to-slot mapping via `people_title_slot_mapping` table
- The slot is the constant. Who fills it is the variable.

### Variables
- Which slots are empty (changes as passes fill them)
- How many staging records remain to promote
- How many about pages have extractable names
- Hit rate per pass (tracked in logbook)
- Which source provided the best data

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Pass 0 staging exhausted | Normal — move to Pass 1 |
| Pass 1 blog data exhausted | Normal — move to Pass 2 |
| Pass 2 proxy errors > 20% of batch | HALT — check DataImpulse credentials |
| Fill rate doesn't improve after 3 runs | INVESTIGATE — parser, data quality, or query issue |
| Strike 3 on same failure | Troubleshoot/Train → Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream

| Dependency | What | Status |
|-----------|------|--------|
| Process 010 (SEED) | Companies, slots, staging data in D1 | DONE |
| Process 300 (Blog) | Extracted names/titles from about pages | BUILD — running |
| intake_people_staging | Pre-scraped records | In D1 |

### Downstream

| Consumer | What It Needs |
|----------|--------------|
| Process 201 (Email Discovery) | Person with name but no verified email |
| Process 202 (LinkedIn Discovery) | Person with name but no LinkedIn URL |
| Process 100 (LCS Pipeline) | Filled slots with reachable contacts |
| Process 500 (Talent Flow) | Filled slots for movement detection |

---

## 9. SMOKE TEST

```
1. GET people-worker-200.svg-outreach.workers.dev/health → status ok, empty_slots > 0
2. POST /pass/0?limit=100 → expected: slots_filled > 0 from staging data
3. POST /pass/1?limit=50 → expected: slots_filled from blog data
4. Check fill rates: SELECT slot_type, SUM(CASE WHEN is_filled=1 THEN 1 ELSE 0 END) as filled, COUNT(*) as total FROM people_company_slot GROUP BY slot_type
5. Check person quality: SELECT COUNT(*) FROM people_people_master WHERE full_name IS NOT NULL AND length(full_name) > 3
```

**Three Primitives Check:**
1. **Thing:** Do empty slots exist? Does staging/blog data exist?
2. **Flow:** Does staging data reach the slot? Does blog data reach the slot?
3. **Change:** Is the slot updated to is_filled=1 with a valid person_unique_id?

---

## 10. LOGBOOK

_No runs on v2 scope. Prior runs logged in v1 logbook below._

### 2026-03-26 — v1 SEED fixes (slot infrastructure)

**ORBT:** BUILD
**Trigger:** Manual
**Result:** 98,112 slots created, people seeded from Neon. Fill rates: CEO ~60%, CFO ~55%, HR ~35%.
**ORBT after:** BUILD

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-04-01 | 53 orphan slots (CTB-path IDs) | intake_promotion/wv_hr_pipeline used non-UUID IDs | Fixed in Neon — reset to is_filled=false | 1 |
| 2 | 2026-04-01 | D1 had 358K slots (full universe) | SEED pulled from all Neon, not agent-scoped | Clean re-SEED from seed_views — 98,106 slots | 1 |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-04-01 |
| Version | 2.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |

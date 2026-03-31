# PROCESS: People Slot Filler
## Fills CEO/CFO/HR slots with verified email and LinkedIn — if we can't reach a human, the company is dead
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-200 |
| Name | People Slot Filler |
| Business Silo | svg-agency |
| Sub-Hub | outreach |
| CTB Position | factory/outreach/200-people-worker |
| Blueprint Repo | barton-outreach-core |
| Blueprint Section | doctrine/OSAM.md — people intelligence sub-hub (04.04.02) |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | 2026-03-26 (v1 — needs rebuild for v2 pass structure) |
| BAR Reference | BAR-52 |
| Deployed URL | people-worker-200.svg-outreach.workers.dev |
| Cron | Daily `0 6 * * *` (6am UTC) |
| Runtime | CF Worker (daily cron, batched) |

---

## 2. WHY THIS EXISTS

This is the gate. If a company doesn't have at least one reachable person (verified email or LinkedIn URL), it's a dead record — can't enter LCS, can't be outreached, can't become a client. Doesn't matter how much blog data or DOL filings we have.

Every company has 3 slots: CEO, CFO, HR. The SEED (010) copies them from Neon — some filled, most empty. Process 200 fills the empty ones and detects when filled ones change.

**300 (Blog) runs before 200.** Blog maps team pages and extracts names. 200 consumes that free data first, then escalates to paid tools only for what's still empty.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Daily cron. Runs after Process 300 (Blog) has mapped web presence.
2. **"How do we get it?"** — Three passes, each escalating cost. Free → cheap → top shelf.

### Input
- ~32K companies in D1 with 3 slots each (CEO, CFO, HR) — 98,112 total slots
- Blog data from Process 300 (team page URLs, names/titles already extracted)
- Staging data already in D1 (`intake_people_staging` — 24,727 records)
- Company names from spine (`cl_company_identity.canonical_name`)
- City + state from `outreach_company_target`

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| **Pass 1 — FREE** | | | | |
| 1a | `intake_people_staging` (24,727 records) | Match names/titles to slot types via `people_title_slot_mapping`. Create people_master record. Update slot to is_filled=1. | Slots filled from existing staged data | D1 queries (free) |
| 1b | Team page data from Process 300 (names, titles extracted from about_urls) | Match extracted names/titles to empty slots. Create people_master record. Update slot. | Slots filled from blog reconnaissance | D1 queries (free) |
| **Pass 2 — CHEAP** | | | | |
| 2 | Empty slots remaining after Pass 1 | Build Startpage query: `site:linkedin.com/in/ "CEO" "Acme Corp" "Hagerstown" "MD"`. Route through DataImpulse residential proxy. Parse LinkedIn title tag: "Name - Title at Company". Create people_master record, fill slot. | Slots filled from LinkedIn search index | Startpage + DataImpulse proxy (~$1-2/month) |
| **Pass 3 — TOP SHELF** | | | | |
| 3 | Empty slots remaining after Pass 2 | Query Brave Search API: same pattern as Pass 2 but different search engine. Backup source. | Slots filled from Brave index | Brave Search API ($3-5/1K queries) |

If all three passes can't fill a slot, it stays empty. No unlimited retries. Move on.

### Output
- Filled slots with person record: name, title, verified email, LinkedIn URL
- Each company gets a reachability status:

| Status | Meaning | Channel |
|--------|---------|---------|
| UNREACHABLE | No slots filled or no contact method | Blocked — cannot enter LCS |
| EMAIL_ONLY | Verified email, no LinkedIn | Mailgun path |
| LINKEDIN_ONLY | LinkedIn URL, no email | HeyReach path |
| FULL | Both channels available | Best position |

- A company needs at least 1 reachable slot to enter Process 100 (LCS Pipeline)

### Circle (Bedrock §5)
Monthly movement detection: for filled slots with LinkedIn URLs, re-fetch and compare to stored values. Binary: changed or didn't. Signals: TITLE_CHANGED, COMPANY_CHANGED, BOTH_CHANGED. Movement signals feed Process 500 (Talent Flow) and Process 100 (LCS Pipeline).

---

## 4. WHAT IT GRABS OFF THE WALL

### Snap-On Toolbox Sub-Hub References

| Sub-Hub ID | Tool | What It Does | Recommended Vendor |
|------------|------|-------------|-------------------|
| 11-structured-data | D1 read/write | Read/write to svg-d1-outreach-ops, read-only to svg-d1-spine | CF D1 (native) |
| 16-fetcher | CF Workers fetch | Fetch about pages from Process 300 output | CF Workers fetch |
| 18-proxy-router | Residential proxy for search queries | Route Startpage queries through residential IPs | DataImpulse |
| 05-fallback-scraping | Backup search for hard-to-reach slots | Brave Search API when Startpage/proxy can't find results | Brave Search API |
| 15-scheduling | Daily cron trigger | 6am UTC daily execution | CF Workers cron |

Reference: `law/SNAP_ON_TOOLBOX.yaml` for vendor details, cost tiers, and banned list.

### Blueprint Reference

| Blueprint | Repo | Path | What It Defines |
|-----------|------|------|----------------|
| Outreach OSAM | barton-outreach-core | doctrine/OSAM.md | Schema, join paths, CQRS rules |
| Snap-On Toolbox | imo-creator | law/SNAP_ON_TOOLBOX.yaml | Tool sub-hubs, vendors, banned list |
| D1 Data Dictionary | Barton-Processes | D1_DATA_DICTIONARY.md | AI-ready column reference |

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | Slots, people, blog data, staging, company target |
| svg-d1-spine | D1_SPINE | 641a9a1e | READ ONLY | cl_company_identity.canonical_name for search queries |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_GATEWAY_URL | imo-creator | dev | Pass 2 — DataImpulse gateway |
| PROXY_API_KEY | imo-creator | dev | Pass 2 — DataImpulse auth |
| BRAVE_API_KEY | imo-creator | dev | Pass 3 — Brave Search API |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 (staging + blog from 300) — always first
2. Startpage via DataImpulse ($1-2/month) — second
3. Brave Search API ($3-5/1K queries) — only when free and cheap exhausted

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `people_company_slot` | 3 slots per company (CEO/CFO/HR), is_filled, person_unique_id | `outreach_id` |
| `people_people_master` | Existing person records — name, email, LinkedIn | `unique_id` |
| `intake_people_staging` | 24,727 pre-scraped records with names, titles, slot mappings | `outreach_id` |
| `outreach_blog` | about_url, team page data from Process 300 | `outreach_id` |
| `outreach_company_target` | city, state for search queries | `outreach_id` |
| `cl_company_identity` (spine) | canonical_name for search queries | `outreach_id` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `people_people_master` | New person records (name, title, email, LinkedIn URL) | All passes |
| `people_company_slot` | is_filled=1, person_unique_id, filled_at, source_system | All passes |
| `intake_people_staging` | status='promoted' on consumed records | Pass 1a |

### Join Chain

```
outreach_outreach.outreach_id (SPINE)
  → people_company_slot.outreach_id (1:N — 3 per company: CEO, CFO, HR)
    → people_people_master.unique_id (via person_unique_id — name, email, LinkedIn)
  → intake_people_staging.outreach_id (pre-scraped data to promote)
  → outreach_blog.outreach_id (team page data from Process 300)
  → outreach_company_target.outreach_id (city, state for search context)
  → cl_company_identity.outreach_id (canonical_name for search queries — spine D1)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Query Neon | D1 only during WORK phase. SEED already pulled the data. |
| Skip Pass 1 and go to paid tools | Free before cheap. Always. |
| Retry indefinitely on empty slots | Three passes. If all three fail, the slot stays empty. Move on. |
| Run Pass 3 without exhausting Pass 2 | Cost escalation is sequential, not parallel. |
| Fill slots without verified email OR LinkedIn | A slot without a contact method is not filled — it's just a name. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Which slots are empty? | `people_company_slot` | `is_filled = 0` |
| What's the company name for search? | `cl_company_identity` (spine) | `canonical_name` |
| What city/state for search context? | `outreach_company_target` | `city`, `state` |
| Is there staging data to promote? | `intake_people_staging` | `status != 'promoted'` |
| Did Process 300 find a team page? | `outreach_blog` | `about_url IS NOT NULL` |
| Is this company reachable? | `people_company_slot` + `people_people_master` | `is_filled=1` + email or linkedin_url present |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)
- 3 slot types per company: CEO, CFO, HR
- outreach_id is the universal join key
- Pass order: free → cheap → top shelf. Never skip.
- A slot needs verified email OR LinkedIn URL to count as filled
- Reachability gate: at least 1 reachable slot to enter LCS
- 300 runs before 200. Always.
- Batch size: 100 profiles per cron invocation
- Jitter: 30-120 seconds between proxy fetches (Box-Muller)

### Variables (fill — changes every run)
- Which slots are empty (changes as passes fill them)
- How many staging records remain to promote
- How many team pages Process 300 found
- Hit rate per pass (Startpage ~95%, Brave TBD)
- Fill rate per slot type (CEO ~60%, CFO ~55%, HR ~35% as of last SEED)
- Total reachable companies (determines LCS pipeline volume)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Pass 1 staging data exhausted | Normal — move to Pass 1b (blog data) |
| Pass 1b blog data exhausted | Normal — move to Pass 2 (Startpage) |
| Pass 2 proxy errors >20% of batch | HALT — check DataImpulse credentials, IP pool |
| Pass 3 Brave API errors >10% of batch | HALT — check API key, rate limits |
| Brave monthly budget cap reached | HALT — do not exceed. Wait for next month. |
| Slot fill rate drops below prior month | Investigate — something changed in the data |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 010 (SEED) | Companies, slots, people, blog data in D1 | DONE |
| Process 300 (Blog) | Team page URLs, names/titles extracted | BUILD |
| intake_people_staging | 24,727 pre-scraped records | DONE |
| DataImpulse proxy | Residential proxy for Startpage | CONFIGURED |
| Brave Search API | Backup search source | PENDING — needs API key in Doppler |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 100 (LCS Pipeline) | Filled slots with reachable contacts — determines which companies enter LCS |
| Process 500 (Talent Flow) | Movement signals from monthly detection cycle |
| Process 700 (Campaign Engine) | Reachability status determines Mailgun vs HeyReach channel |

---

## 9. SMOKE TEST

```
1. GET people-worker-200.svg-outreach.workers.dev/health → expected: status ok
2. Count empty slots: SELECT COUNT(*) FROM people_company_slot WHERE is_filled = 0 → expected: > 0
3. Count staging records: SELECT COUNT(*) FROM intake_people_staging WHERE status != 'promoted' → expected: > 0
4. Run Pass 1a: promote 100 staging records → expected: slots_filled > 0, errors = 0
5. Run Pass 2: query Startpage for 10 companies → expected: LinkedIn profiles found for >50%
6. Slot fill rate after run: SELECT slot_type, ROUND(SUM(CASE WHEN is_filled=1 THEN 1.0 ELSE 0 END)/COUNT(*)*100,1) as pct FROM people_company_slot GROUP BY slot_type → expected: improvement over prior
7. Reachability: SELECT COUNT(*) FROM people_company_slot cs JOIN people_people_master pm ON cs.person_unique_id = pm.unique_id WHERE cs.is_filled = 1 AND (pm.email IS NOT NULL OR pm.linkedin_url IS NOT NULL) → expected: > 0
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do the empty slots exist in D1? Do the staging records exist? Does the proxy work?
2. **Flow:** Does staging data reach the slot? Does the search query reach Startpage? Does the result reach D1?
3. **Change:** Is the slot updated to is_filled=1? Is the person record created with email/LinkedIn?

---

## 10. ANALYTICS — The Dyno Sheet (Bedrock §2 + §5)

### Process Metrics

| Metric | Unit | Baseline (2026-03-30) | Target | Tolerance |
|--------|------|----------------------|--------|-----------|
| Total slots | count | 358,308 | ~3x companies | stable |
| CEO fill rate | % | 54.7% | IMPROVE | must not drop below baseline |
| CFO fill rate | % | 50.2% | IMPROVE | must not drop below baseline |
| HR fill rate | % | 43.2% | IMPROVE | must not drop below baseline |
| Staging records available | count | 24,727 | decreases as promoted | track promotion rate |
| Pass 1 (free) hit rate | % | BASELINE | set after first run | — |
| Pass 2 (Startpage) hit rate | % | BASELINE | set after first run | — |
| Pass 3 (Brave) hit rate | % | BASELINE | set after first run | — |
| Cost per filled slot (Pass 2) | $/slot | BASELINE | set after first run | budget cap |
| Cost per filled slot (Pass 3) | $/slot | BASELINE | set after first run | budget cap |
| Reachable companies (≥1 slot with email or LinkedIn) | count | BASELINE | IMPROVE | track growth |
| Slot→person join integrity | % | 99.7% | ≥99% | <95% = HALT |

### Tool Scorecard

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| 11-structured-data | CF D1 | 100% | $0 | 0% | ~1ms | baseline |
| 16-fetcher | CF Workers fetch | BASELINE | $0 | BASELINE | BASELINE | pending |
| 18-proxy-router | DataImpulse | 0% (Startpage CAPTCHA) | $1/GB | 100% | N/A | 2026-03-30 |
| 05-fallback-scraping | Brave Search API | BASELINE | $0.004/query | BASELINE | BASELINE | pending |

Note: DataImpulse/Startpage is currently blocked (CAPTCHA). Vendor scorecard reflects this — justification for evaluating Brave as replacement.

### Sigma Tracking — set after 3+ runs

### ORBT Gate Rule

| Current ORBT | Sigma Trend | Action |
|-------------|-------------|--------|
| BUILD | N/A | Establish baselines |
| OPERATE | Tightening | No action — system healthy |
| OPERATE | Flat | Investigate — phantom constant? |
| OPERATE | Expanding | HALT — broken constant upstream |
| REPAIR | Any | Fix at source, re-baseline |

---

## 11. LOGBOOK

### 2026-03-26 — SEED fixes (slot infrastructure)

**ORBT:** BUILD
**Trigger:** Manual — slots and people needed for Process 200 to operate
**Records processed:** 98,112 slots created, 51,582 people records seeded
**Errors:** 0
**Tools used:** Hyperdrive (HD_NEON), D1.batch()
**Result:** All companies have 3 slots. Fill rates: CEO ~60%, CFO ~55%, HR ~35%
**Learnings:** Slot infrastructure is solid. Now need to fill the empty ones.
**ORBT after:** BUILD (worker not yet rebuilt for v2 pass structure)

### 2026-03-19 — v1 build + deploy

**ORBT:** BUILD
**Trigger:** Manual — initial build
**Records processed:** 35K companies seeded to standalone D1
**Errors:** Google CAPTCHA blocks, Bing APIs retired
**Tools used:** DataImpulse proxy, Startpage
**Result:** Proved SearchEngineProxy pattern (87-95% LinkedIn hit rate). Standalone D1 later scrapped.
**Learnings:** Startpage through DataImpulse is the right stack. Google and Bing are dead ends.
**ORBT after:** BUILD

---

## 12. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-19 | Google blocks with CAPTCHAs through proxy | Google anti-bot | Switched to Startpage — 95% hit rate | 1 |
| 2 | 2026-03-19 | Bing APIs retired Aug 2025 | Microsoft sunset | Removed Bing, Startpage exclusively | 1 |
| 3 | 2026-03-25 | Old standalone D1 went stale | Duplicating outreach data in separate D1 | Scrapped standalone D1, rewired to svg-d1-outreach-ops | 1 |
| 4 | 2026-03-25 | 94.8% slot→person orphan rate | SEED brought slots but not matching people | Re-SEED from Neon (fixed in Process 010) | 1 |

---

## 13. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-19 | v1 build + deploy, proved proxy pattern | processes/Session 2026-03-19 — Full Build Progress Report |
| 2026-03-24 | Manifest written, dashboard wired | session/2026-03-24-full-session-final |
| 2026-03-26 | Rewired to svg-d1-outreach-ops, SEED fixes | ops/2026-03-26-seed-fix-complete |
| 2026-03-29 | Process doc rewritten from Dave's walkthrough — v2 pass structure | none |
| 2026-03-29 | Rewrite: CTB position, sub-hub, blueprint refs, Snap-On Toolbox sub-hub references (BAR-52) | none |

---

## ENRICHMENT PRIORITY

| Priority | Criteria | Why |
|----------|----------|-----|
| 1st | DOL-linked + empty slots | Federal filing proves company viability |
| 2nd | Has about_url + empty slots (from Process 300) | Free team page data |
| 3rd | Non-DOL + empty slots | Lower confidence, verify first |
| 4th | Filled slots (movement check) | Monthly refresh |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 2.1.0 |
| Template Version | 3.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md v1.1.2 |
| Data Flow | factory/outreach/DATA_FLOW.md |

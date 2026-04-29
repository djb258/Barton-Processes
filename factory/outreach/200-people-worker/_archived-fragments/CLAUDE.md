> **ARCHIVED 2026-04-29** — Consolidated into PROCESS-UT.md and DOCTRINE.md during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — Process 200: People Worker v2

## Governing Doctrine

**Before any work on this process, read and follow:**

1. `law/doctrine/FOUNDATIONAL_BEDROCK.md` — The engine (Three Primitives, C&V, IMO, CTB, Circle, Troubleshooting Loop, Tier 0, Aviation Model)
2. `factory/svg-agency/DATA_FLOW.md` — The plumbing (Neon → D1 SEED pipeline, all join paths)
3. `factory/svg-agency/200-people-worker/ERD.md` — The tables (actual D1 schema, pressure tested)
4. `factory/svg-agency/200-people-worker/D1_SCHEMA.md` — Full column reference

**Pre-flight (every session):**
- Two-Question Intake: "What triggers this?" and "How do we get it?"
- C&V Test: Can you name it? Format it? → constant. The value filling it → variable.
- Four-Element Validation: IMO + CTB + Circle simultaneously
- Three Primitives: Thing (exists?), Flow (reaches?), Change (transforms correctly?)
- Determinism first. LLM is tail arbitration only.
- If something broke → Troubleshooting Loop (Bedrock §6). Do not patch. Do not guess.

---

## What This Process Does

Fills CEO/CFO/HR slots for 32,704 agent-assigned companies. Detects movement (person changed title, left company). Operates directly on svg-d1-outreach-ops. No standalone D1.

## Architecture

**D1 Bindings:**
- `D1_OUTREACH` (svg-d1-outreach-ops) — all reads and writes
- `D1_SPINE` (svg-d1-spine) — read-only for `cl_company_identity.canonical_name`

**No Neon queries during WORK phase.** Neon is vault only. SEED → WORK → PUSH.

**Gate 0 already applied:** Every company in D1 is agent-assigned. No coverage filtering needed.

---

## How It Works — Four Passes (Well Drinks First)

### Pass 0: Promote Staging (FREE — data already in D1)
- Read `intake_people_staging` (24,727 records with names, titles, slot mappings)
- Match to `people_title_slot_mapping` for deterministic slot assignment
- Create `people_people_master` record
- Update `people_company_slot` to `is_filled = 1`
- Mark staging record as `status = 'promoted'`
- **Cost: $0. Use ALL of this before any external calls.**

### Pass 1: Scrape About/Team Pages (CHEAP — CF fetch, no proxy)
- Read `outreach_blog.about_url` for companies with empty slots
- Fetch team/about pages via CF Worker fetch (no proxy needed — public pages)
- Parse executive names and titles
- Match titles to slot types via `people_title_slot_mapping`
- Create/update records in D1
- **Cost: Free (CF Worker fetch). Rate limit: 100 pages/cron invocation.**

### Pass 2: Search-Engine-as-Proxy — UT Snap-On Tool (TOP SHELF)
- For remaining empty slots after Pass 0 + 1
- Get company name from `cl_company_identity.canonical_name` (D1_SPINE)
- Get city + state from `outreach_company_target` (D1_OUTREACH)
- Build Startpage query: `site:linkedin.com/in/ "CEO" "Acme Corp" "Hagerstown" "MD"`
- Route through DataImpulse residential proxy
- Parse LinkedIn `<title>` tag: `"Name - Title at Company | LinkedIn"`
- Create `people_people_master` record, fill slot
- **Cost: $1-2/month for 20K profiles.**
- **Three-tier fallback:**
  1. Startpage through DataImpulse (95% hit rate)
  2. Brave Search API ($3-5/1K queries) — backup
  3. LinkedIn direct (15% rate) — last resort

### Pass 3: Movement Detection (MONTHLY)
- For filled slots with `linkedin_url`
- Fetch LinkedIn profile via same proxy stack
- Compare title + company to stored values
- Binary movement: 0 (no change) or 1 (movement)
- Signal types: TITLE_CHANGED, COMPANY_CHANGED, BOTH_CHANGED
- Update records in D1 outreach
- **Trigger: Monthly, after Pass 0-2 complete.**

---

## The Snap-On Tool: Search-Engine-as-Proxy

LinkedIn blocks direct fetches (HTTP 999). Query search engines that already indexed the data.

**Stack:**
- **Startpage** — Google results, anonymized, no CAPTCHA
- **DataImpulse** — residential proxy, $1/GB, 90M+ rotating IPs
- **CF Worker fetch** — no curl_cffi needed (Workers have clean TLS)
- **Box-Muller jitter** — organic timing between requests (30-120s)

**Credentials:** Doppler imo-creator project:
- `PROXY_GATEWAY_URL` — DataImpulse HTTP gateway
- `PROXY_API_KEY` — DataImpulse auth

**Reusable for ANY indexed platform:**
- LinkedIn profiles → title + company movement
- LinkedIn company pages → employee count, industry
- Glassdoor → benefits sentiment
- Company career pages → open positions

---

## Enrichment Priority

| Priority | Criteria | Why |
|----------|----------|-----|
| 1st | DOL-linked + empty slots | Federal filing proves viability |
| 2nd | Has about_url + empty slots | Free team page scraping |
| 3rd | Non-DOL + empty slots | Lower confidence, verify first |
| 4th | Filled slots (movement check) | Monthly refresh |

---

## Slot Constants

- **Types:** CEO, CFO, HR (fixed — these three, always)
- **Priority:** CEO → CFO → HR
- **Minimum for LCS:** 1 reachable slot
- **Total slots:** 98,112 (32,704 companies × 3)

---

## Reachability Gate

Must pass BEFORE company enters LCS pipeline:

| Status | Meaning | Channel |
|--------|---------|---------|
| UNREACHABLE | No slots filled or no contact method | Blocked — cannot enter LCS |
| EMAIL_ONLY | Verified email, no LinkedIn | Mailgun path |
| LINKEDIN_ONLY | LinkedIn URL, no email | HeyReach path |
| FULL | Both channels available | Best position |

---

## Data Sources & Trust

| Source | Trust | Why |
|--------|-------|-----|
| intake_people_staging | HIGH | Already web-scraped and title-mapped |
| DOL filings (sponsor_dfe_name) | HIGHEST | Federal filing, legal company name |
| outreach_blog.about_url | MEDIUM | Public page, may be outdated |
| Startpage/LinkedIn search | MEDIUM | Indexed data, point-in-time |
| Hunter-sourced | MEDIUM | Domain exists, unverified |

---

## Dependencies

### Upstream
| Dependency | What | Status |
|-----------|------|--------|
| D1 outreach (SEED) | Company data, slots, people, blog, DOL | DONE (SEED fixes applied 2026-03-26) |
| D1 spine (CL) | Company name for search queries | DONE |
| DataImpulse proxy | Residential proxy for Startpage | CONFIGURED |

### Downstream
| Consumer | What |
|----------|------|
| Process 500 (Talent Flow) | Movement signals (0/1 per slot) |
| Process 100 (LCS Pipeline) | Recipient slots for SID construction |
| Outreach D1 | people_company_slot + people_people_master updates |

---

## Worker Config

- **URL:** people-worker-200.svg-outreach.workers.dev (TBD — needs deploy)
- **Cron:** `0 6 * * *` (daily 6am UTC)
- **Batch size:** 100 profiles per cron (configurable)
- **Delay:** 30-120 seconds between proxy fetches (Box-Muller jitter)

---

## Key Joins (verified 2026-03-26)

| From | To | Join Key | Match Rate |
|------|----|----------|------------|
| outreach_outreach | outreach_company_target | outreach_id | 100% |
| outreach_outreach | people_company_slot | outreach_id | 100% |
| people_company_slot | people_people_master | person_unique_id → unique_id | 99.7% |
| outreach_outreach | outreach_blog | outreach_id | 100% |
| outreach_outreach | outreach_dol | outreach_id | 100% |
| cl_company_identity | outreach_outreach | outreach_id | read-only |

---

## Known Issues

| Issue | Resolution |
|-------|------------|
| Google blocks with CAPTCHAs through proxy | Use Startpage via DataImpulse — 95% hit rate |
| Bing APIs retired Aug 2025 | Removed Bing, Startpage exclusively |
| BIT scoring retired 2026-03-25 | Removed all BIT references |
| Old standalone D1 (people-worker-200) | SCRAPPED — rewired to svg-d1-outreach-ops |
| 94.8% slot→person orphan rate | FIXED (re-SEED 2026-03-26) — now 99.7% |
| 18,301 companies had no slots | FIXED (SEED 2026-03-26) — now 100% coverage |
| No agent assignment on companies | FIXED (SEED 2026-03-26) — 32,702 assigned |

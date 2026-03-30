# PROCESS: Blog Monitor
## Detects content movement on company websites — maps the URL structure (constant), tracks 0/1 change (variable), classifies signals only on the 1s
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-300 |
| Name | Blog Monitor |
| Business Silo | svg-agency |
| CTB Position | factory/svg-agency/300-blog-worker |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | — |
| BAR Reference | BAR-52 |
| Deployed URL | local Python script (blog-monitor-v2.py) |
| Cron | Monthly (manual, future: CF Worker cron) |
| Runtime | Python 3 + curl_cffi + DataImpulse proxy |

---

## 2. WHY THIS EXISTS

Two jobs. First: detect which companies have active web presence so Process 200 (People) has free data to work with before spending on paid tools. Second: detect content movement (funding, acquisition, leadership change) that feeds LCS signals (Process 100).

The URL mapping is the constant — where to look on each site. The 0/1 is the variable — did it change since last check. First pass is expensive (mapping). Every pass after that is cheap (just checking dates against the map).

**300 runs before 200. Always.**

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Monthly. Run before Process 200. Re-run when new companies are SEEDed.
2. **"How do we get it?"** — Startpage via DataImpulse residential proxy. Reads company list from D1 (NOT Neon).

### Input
- ~32,598 companies in D1 with domains from `outreach_outreach.domain`
- 49,062 blog records in `outreach_blog` (13,186 already have about_url)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| **Phase 1 — Movement detection (0/1)** | | | | |
| 1 | All companies with domain | Query Startpage: `site:{domain}` — check search result snippets for freshness indicators (dates, "ago", "today", "this week") | Binary: 0 (no change) or 1 (fresh content detected) | Startpage + DataImpulse proxy |
| 2 | Phase 1 results | Write 0/1 + last_checked + reason back to `outreach_blog.context_summary` in D1 | URL mapping updated with movement status and timestamp | D1 via wrangler |
| **Phase 2 — Signal classification (only on 1s)** | | | | |
| 3 | Companies where Phase 1 = 1 | Run 6 targeted Startpage queries with signal-specific keywords per mover | Signal type: FUNDING_EVENT, ACQUISITION, LEADERSHIP_CHANGE, EXPANSION, RESTRUCTURING, GENERAL_NEWS | Startpage + DataImpulse proxy |
| 4 | Phase 2 results | Write detected signals back to `outreach_blog.context_summary` in D1 | Classified movement signals stored | D1 via wrangler |

**Detection is deterministic.** No AI. Keyword matching against search index snippets. The search engine already did the crawling — we're reading its index, not downloading pages.

### Output
- `outreach_blog.context_summary` updated with: movement (0/1), last_checked, reason, signals (if any)
- JSONL backup files in `src/output/` (blog-indicators-YYYY-MM.jsonl, blog-signals-YYYY-MM.jsonl)
- Movement signals feed Process 100 (LCS Pipeline) and inform Process 200 (People) which companies are active

### Circle (Bedrock §5)
The URL mapping is the constant — `site:{domain}` is the query pattern. The 0/1 is the variable. Each run compares freshness against what was stored. First pass is expensive (every company). After that, only re-check companies that were 1 last time, or on a monthly full sweep. If a domain goes dead (NOT_INDEXED), flag it, don't drop it.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | outreach_blog (about_url, source_url), outreach_outreach (domain) |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| Startpage | Search engine | Free | None (routed through proxy) | Google results anonymized, no CAPTCHA — the search tool |
| DataImpulse | Residential proxy | Cheap (~$1/month) | PROXY_USER, PROXY_PASS (env vars) | 90M+ rotating residential IPs, routes Startpage queries |
| curl_cffi | Python library | Free | None | Chrome TLS fingerprint — looks like a real browser |
| wrangler CLI | CF tool | Free | OAuth (logged in) | Reads company list from D1, writes results back to D1 |

### Secrets (env vars, from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_USER | imo-creator | dev | DataImpulse username |
| PROXY_PASS | imo-creator | dev | DataImpulse password |

**Tool Priority:** Startpage via DataImpulse is the only external tool. No AI. No page downloads. We're reading the search index, not crawling sites.

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `outreach_outreach` | company domain (the input for `site:domain` query) | `outreach_id` |
| `outreach_blog` | existing about_url, source_url, prior movement status | `outreach_id` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `outreach_blog.context_summary` | movement (0/1), last_checked, reason, signals (JSON) | Phase 1 + Phase 2 |

### Join Chain

```
outreach_outreach.outreach_id (SPINE)
  → outreach_outreach.domain (company website — the query input)
  → outreach_blog.outreach_id (1:1 — stores movement results)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Query Neon | D1 only. SEED already pulled the data. |
| Download full pages | We read the search index, not the sites. Map the constant, track the variable. |
| Classify companies with movement=0 | Phase 2 only fires on 1s. Don't waste proxy bandwidth. |
| Run without proxy | Startpage will block direct requests at scale. Always use DataImpulse. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| What's the company domain? | `outreach_outreach` | `domain` |
| Has content changed? | `outreach_blog` | `context_summary → $.movement` (0/1) |
| When was it last checked? | `outreach_blog` | `context_summary → $.last_checked` |
| What type of change? | `outreach_blog` | `context_summary → $.signals` |
| Does this company have a team page? | `outreach_blog` | `about_url` |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)
- Detection is binary: 0 (no change) or 1 (change detected)
- Query pattern: `site:{domain}` — the domain is the constant, the search results are the variable
- 6 signal types: FUNDING_EVENT, ACQUISITION, LEADERSHIP_CHANGE, EXPANSION, RESTRUCTURING, GENERAL_NEWS
- Signal detection is deterministic (keyword matching). No AI.
- Phase 2 only fires on 1s. Never classify a 0.
- URL mapping is the constant. The 0/1 movement flag is the variable.
- First pass maps everything (expensive). After that, just check dates (cheap).
- Box-Muller jitter between requests (mean 5s, std 2s, min 2.5s)

### Variables (fill — changes every run)
- Which companies show content movement (0/1)
- What signal type gets classified on movers
- Last-checked timestamp per company
- Number of companies indexed vs NOT_INDEXED

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| CF Worker fetch fails on >50% of known about_urls | HALT — check if sites are blocking, adjust headers |
| DataImpulse proxy returns >20% errors | HALT — check proxy credentials, IP pool |
| Signal classification produces >3 UNCLASSIFIABLE per batch | HALT — review LLM prompt, check content quality |
| Budget cap on proxy bandwidth | HALT — do not exceed monthly allocation |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 010 (SEED) | Companies + blog data in D1 | DONE |
| outreach_blog populated | 49,062 records with about_url/source_url | DONE |
| DataImpulse proxy | Residential proxy for Startpage | CONFIGURED |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 200 (People) | Team page URLs, names/titles found on about pages — free data for slot filling |
| Process 100 (LCS Pipeline) | Content movement signals (FUNDING_EVENT, LEADERSHIP_CHANGE, etc.) |

---

## 9. SMOKE TEST

```
1. python3 src/blog-monitor-v2.py --phase 1 --limit 10 → expected: loads 10 companies from D1, produces 0/1 per company
2. cat src/output/blog-indicators-YYYY-MM.jsonl | head -3 → expected: JSON lines with movement, reason, fetched_at
3. wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT context_summary FROM outreach_blog WHERE context_summary LIKE '%movement%' LIMIT 3" → expected: JSON with movement 0/1
4. python3 src/blog-monitor-v2.py --phase 2 → expected: classifies only companies with movement=1
5. cat src/output/blog-signals-YYYY-MM.jsonl → expected: signal types with evidence
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do the company domains exist in D1? Does the proxy connect?
2. **Flow:** Does the Startpage query return results? Does the 0/1 get written back to D1?
3. **Change:** Is freshness detection correct (are the 1s real movement)? Are signals classified accurately?

---

## 10. LOGBOOK

_No runs yet on v2. Process in BUILD state._

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | v1 read from Neon via psql | Should read from D1 (SEED already pulled data) | v2 rewired to D1 via wrangler CLI | 1 |
| 2 | 2026-03-29 | v1 output to local JSONL only | Results not persisted to D1 | v2 writes 0/1 + signals back to outreach_blog.context_summary | 1 |
| 3 | 2026-03-29 | Startpage HTML parsing is regex-based | If Startpage changes markup, extraction breaks | Monitor and update regex patterns | 0 |
| 4 | 2026-03-29 | Not yet a CF Worker | Python script with curl_cffi | Future: convert to CF Worker (curl_cffi proxy stack works well, keep for now) | 0 |

---

## 12. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | Process doc written from Dave's walkthrough | none |
| 2026-03-29 | v2 script: rewired to D1, added D1 writeback, kept proxy stack | none |

---

## SIGNAL TYPES (for content movement detection)

| Signal | Keywords | Weight |
|--------|----------|--------|
| FUNDING_EVENT | funding, raised, series A/B, investment, venture, capital | 15 |
| ACQUISITION | acquisition, acquired, merger, buyout, takeover | 12 |
| LEADERSHIP_CHANGE | new CEO, new CFO, appointed, promoted, executive | 10 |
| EXPANSION | expansion, new office, new location, hiring spree, headcount | 8 |
| RESTRUCTURING | restructuring, layoff, reorganization, downsizing | 7 |
| GENERAL_NEWS | announcement, press release, news, update, launch | 5 |

---

## HOW TO RUN

```bash
# Set proxy credentials
export PROXY_USER="your-dataimpulse-user"
export PROXY_PASS="your-dataimpulse-pass"

# Phase 1: Movement detection (0/1) — test with 10 companies
python3 src/blog-monitor-v2.py --phase 1 --limit 10

# Phase 1: Full run (all ~32K companies, ~5s between requests = ~44 hours)
python3 src/blog-monitor-v2.py --phase 1

# Phase 1: Resume interrupted run
python3 src/blog-monitor-v2.py --phase 1 --resume

# Phase 2: Classify movers (only runs on 1s from Phase 1)
python3 src/blog-monitor-v2.py --phase 2

# Both phases
python3 src/blog-monitor-v2.py

# Adjust delay (default mean 5s)
python3 src/blog-monitor-v2.py --phase 1 --delay 3.0
```

**Runtime estimate:** ~720 companies/hour at 5s mean delay. 32K companies = ~44 hours for Phase 1. Run in background with `--resume` for interruption safety.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md v1.1.2 |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

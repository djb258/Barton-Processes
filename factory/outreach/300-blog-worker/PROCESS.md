# PROCESS: Blog Recon
## Fetches public about/team pages to extract names and titles — free data for Process 200 before spending on paid tools
### Status: BUILD
### Sub-Hub: outreach
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-300 |
| Name | Blog Recon |
| Sub-Hub | outreach |
| Business Silo | svg-agency |
| CTB Position | factory/outreach/300-blog-worker |
| Blueprint Repo | barton-outreach-core |
| Blueprint Section | doctrine/OSAM.md — blog content sub-hub (04.04.05) |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | — |
| BAR Reference | BAR-52 |
| Deployed URL | local Python script (blog-recon.py) |
| Cron | Monthly (manual, future: CF Worker cron) |
| Runtime | Python 3 (v3: blog-recon.py) |

---

## 2. WHY THIS EXISTS

Two jobs. First: fetch public about/team pages and extract names + titles so Process 200 (People) has free data before spending on paid tools. Second: detect content movement (funding, acquisition, leadership change) that feeds LCS signals (Process 100).

The URL mapping is the constant — where to look on each site. The 0/1 is the variable — did it change since last check. First pass is expensive (mapping). Every pass after that is cheap (just checking dates against the map).

**300 runs before 200. Always.**

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Monthly. Run before Process 200. Re-run when new companies are SEEDed.
2. **"How do we get it?"** — Direct CF Workers fetch of public about/team pages. No proxy needed. No search engine. Reads company list from D1 (NOT Neon).

### Input
- ~32,598 companies in D1 with domains from `outreach_outreach.domain`
- 49,062 blog records in `outreach_blog` (13,199 already have about_url)
- 4,608 existing `context_summary` records (truncated at 4K chars — needs re-fetch)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| **Phase 1 — Parse existing context_summary** | | | | |
| 1 | 4,608 records with context_summary | Parse existing context_summary JSON. These were truncated at 4K chars in prior runs — extract what's usable, flag what needs re-fetch. | Usable name/title extractions + re-fetch queue | D1 read (11-structured-data) |
| **Phase 2 — Fetch known about_urls** | | | | |
| 2 | 13,199 companies with known about_url | Fetch each about_url directly via CF Workers fetch (16-fetcher). No proxy. No search engine. Direct HTTP GET to public pages. | Raw HTML from about/team pages | CF Workers fetch (16-fetcher) |
| 3 | Raw HTML from step 2 | Parse HTML to extract names and titles. Target roles: CEO, CFO, HR Director, Benefits Manager. | Structured name/title pairs per company | HTML parser (17-parser-registry) |
| 4 | Extracted name/title pairs | Write results to `outreach_blog.context_summary` in D1 | Blog data updated with extracted people | D1 write (11-structured-data) |
| **Phase 3 — Discover about_urls for remaining companies** | | | | |
| 5 | ~19K companies with domain but no about_url | Try common paths: `/about`, `/about-us`, `/team`, `/our-team`, `/leadership`, `/about/team`, `/people` | Discovered about_url (first path that returns 200 + relevant content) | CF Workers fetch (16-fetcher) |
| 6 | Discovered about_urls from step 5 | Fetch and parse same as Phase 2 (steps 2-4) | Names/titles extracted + about_url stored | 16-fetcher + 17-parser-registry |
| 7 | All Phase 2 + Phase 3 results | Write about_url + extracted names/titles + movement flags back to D1 | `outreach_blog` fully updated | D1 write (11-structured-data) |

**Detection is deterministic.** No AI. HTML parsing for names/titles.

**Phase 2 uses direct fetch** — no proxy, no search engine. 16-fetcher is the PRIMARY tool for known about_urls.

**Phase 3 has two paths:**
- **Path A (direct):** Try common paths (`/about`, `/about-us`, `/team`, etc.) via direct fetch. Free. No proxy.
- **Path B (Startpage discovery):** For companies where Path A fails, use Startpage search via DataImpulse proxy to discover the about_url. Query: `site:{domain} about OR team OR leadership`. Proven working (2026-03-31).

**Startpage configuration (DataImpulse — proven 2026-03-31):**
- Host: `gw.dataimpulse.com`
- Port: `10000` (sticky session — NOT rotating port 823)
- Username: `{user}__cr.us` (US country targeting)
- Method: POST form (`q={query}`)
- Delay: 3s between queries
- Session: sticky (same IP for entire batch)
- All 5 test queries passed. CAPTCHA issue resolved.

### Output
- `outreach_blog.context_summary` updated with: extracted names, titles, movement (0/1), last_checked
- `outreach_blog.about_url` populated for newly discovered team pages
- JSONL backup files in `src/output/` (blog-recon-YYYY-MM.jsonl)
- Extracted names/titles feed Process 200 (People) as free Pass 1 data
- Movement signals feed Process 100 (LCS Pipeline)

### Circle (Bedrock §5)
The URL mapping is the constant — the about_url per company. The 0/1 is the variable. Each run compares content against what was stored. First pass is expensive (every company). After that, only re-check companies that were 1 last time, or on a monthly full sweep. If a domain goes dead (NOT_INDEXED), flag it, don't drop it.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | outreach_blog (about_url, source_url, context_summary), outreach_outreach (domain) |

### Snap-On Toolbox Sub-Hubs (law/SNAP_ON_TOOLBOX.yaml)

| Tool # | Sub-Hub | Recommended Vendor | What It Does In This Process |
|--------|---------|-------------------|------------------------------|
| 11 | structured-data | Cloudflare D1 (svg-d1-outreach-ops) | D1 read/write — reads company list, writes extracted names/titles/about_urls |
| 16 | fetcher | CF Workers fetch | PRIMARY tool — direct fetch of public about/team pages. No proxy, no search engine. |
| 17 | parser-registry | CF Workers | HTML → names/titles extraction for CEO/CFO/HR/Benefits |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_USER | imo-creator | dev | DataImpulse proxy username (Phase 3 Path B — Startpage discovery) |
| PROXY_PASS | imo-creator | dev | DataImpulse proxy password |

### Blueprint References

| Blueprint | Repo | Path | What It Defines |
|-----------|------|------|-----------------|
| Outreach OSAM | barton-outreach-core | doctrine/OSAM.md v1.1.2 — blog content sub-hub (04.04.05) | Blog table schema, join paths, CQRS rules |
| Snap-On Toolbox | imo-creator | law/SNAP_ON_TOOLBOX.yaml v4.0.0 | 26 tool sub-hubs, vendors (swappable), banned list |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 (existing context_summary) — always first
2. CF Workers fetch (direct, no proxy) — second. This is the workhorse.
3. No paid tools needed. 300 is entirely free.

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `outreach_outreach` | company domain (the input for direct fetch) | `outreach_id` |
| `outreach_blog` | existing about_url, source_url, prior context_summary | `outreach_id` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `outreach_blog.context_summary` | extracted names/titles, movement (0/1), last_checked (JSON) | Phase 1 + Phase 2 + Phase 3 |
| `outreach_blog.about_url` | newly discovered team page URLs | Phase 3 |

### Join Chain

```
outreach_outreach.outreach_id (SPINE)
  → outreach_outreach.domain (company website — the fetch target)
  → outreach_blog.outreach_id (1:1 — stores recon results)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Query Neon | D1 only. SEED already pulled the data. |
| Use search engines for Phase 2 (known about_urls) | Direct fetch via 16-fetcher. No intermediary. No proxy needed for known URLs. |
| Use proxy for Phase 2 about page fetches | These are public pages with known URLs. Direct fetch is sufficient and free. |
| Use Startpage without DataImpulse sticky session | CAPTCHA blocked on rotating proxy. MUST use port 10000+ (sticky) + `__cr.us` (US country) + POST form. See Startpage fix (2026-03-31). |
| Run 200 before 300 | 300 feeds free data to 200. Always run 300 first. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| What's the company domain? | `outreach_outreach` | `domain` |
| Does this company have a team page? | `outreach_blog` | `about_url` |
| What names/titles were extracted? | `outreach_blog` | `context_summary → $.names` |
| When was it last checked? | `outreach_blog` | `context_summary → $.last_checked` |
| Has content changed? | `outreach_blog` | `context_summary → $.movement` (0/1) |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)
- Detection is binary: 0 (no change) or 1 (change detected)
- Fetch method: direct CF Workers fetch (16-fetcher) to public about/team pages
- Target roles: CEO, CFO, HR Director, Benefits Manager
- URL discovery paths: `/about`, `/about-us`, `/team`, `/our-team`, `/leadership`, `/about/team`, `/people`
- HTML parsing is deterministic. No AI.
- Phase order: existing context_summary first (Phase 1), known about_urls second (Phase 2), discovery third (Phase 3)
- URL mapping is the constant. The 0/1 movement flag is the variable.

### Variables (fill — changes every run)
- Which companies have discoverable about pages
- What names/titles get extracted per company
- Last-checked timestamp per company
- Number of companies with about_url vs without

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| CF Worker fetch fails on >50% of known about_urls | HALT — check if sites are blocking, adjust headers |
| Discovery phase (Phase 3) returning >90% 404s | HALT — check common path list, may need expansion |
| HTML parser extracting 0 names on >80% of fetched pages | HALT — review parser patterns, check content structure |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 010 (SEED) | Companies + blog data in D1 | DONE |
| outreach_blog populated | 49,062 records with about_url/source_url | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 200 (People) | Team page URLs, names/titles found on about pages — free data for slot filling (Pass 1b) |
| Process 100 (LCS Pipeline) | Content movement signals (FUNDING_EVENT, LEADERSHIP_CHANGE, etc.) |

---

## 9. SMOKE TEST

```
1. python3 src/blog-recon.py --phase 1 --limit 10 → expected: parses 10 existing context_summary records, extracts usable names/titles
2. python3 src/blog-recon.py --phase 2 --limit 10 → expected: fetches 10 known about_urls directly, extracts names/titles
3. python3 src/blog-recon.py --phase 3 --limit 10 → expected: tries common paths for 10 companies without about_url, discovers pages
4. cat src/output/blog-recon-YYYY-MM.jsonl | head -3 → expected: JSON lines with names, titles, about_url, fetched_at
5. wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT context_summary FROM outreach_blog WHERE context_summary LIKE '%names%' LIMIT 3" → expected: JSON with extracted names/titles
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do the company domains exist in D1? Do the about_urls resolve?
2. **Flow:** Does the fetch return HTML? Does the parser extract names? Do results get written to D1?
3. **Change:** Are the extracted names real (CEO/CFO/HR)? Does Process 200 consume the output?

---

## 10. ANALYTICS — The Dyno Sheet (Bedrock §2 + §5)

### Process Metrics

Fill with ACTUAL BASELINE DATA from Phase 2 run (2026-03-30):

| Metric | Unit | Baseline (2026-03-30) | Target | Tolerance |
|--------|------|----------------------|--------|-----------|
| Companies with domain | count | 32,598 | stable | ±5% |
| Existing about_urls | count | 13,199 | IMPROVE (discover more) | must not drop |
| Phase 2: pages fetched | count | 5,200 (of 13,199) | 13,199 (all) | run to completion |
| Phase 2: pages OK (200 status) | count | ~4,800 (est) | ≥90% of fetched | <80% = investigate |
| Phase 2: people extracted | count | 811 | IMPROVE (tune parser) | track per run |
| Phase 2: hit rate (people/pages) | % | 15.6% | IMPROVE | track trend |
| Phase 3: about_urls discovered | count | BASELINE | set after first run | — |
| Phase 3: path hit rate | % | BASELINE | set after first run | — |
| Phase 3: homepage fallback rate | % | BASELINE | set after first run | — |
| Parser accuracy (valid names vs false positives) | % | ~70% (est from manual review) | IMPROVE | tune regex patterns |
| context_summary truncation | chars | 4,000 (truncated in SEED) | needs re-fetch | known issue |

### Tool Scorecard

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| 16-fetcher | CF Workers fetch (direct) | ~92% (4,800/5,200) | $0 | ~8% (timeouts, 403s) | ~0.5s/page | 2026-03-30 |
| 17-parser-registry | Python regex (blog-recon.py) | 15.6% (811/5,200) | $0 | 0% (no crashes) | <1ms/parse | 2026-03-30 |
| 18-proxy-router | DataImpulse + Startpage (sticky session) | 100% (5/5 test) | $1/GB | 0% | ~3s/query | 2026-03-31 |

Note: 18-proxy-router/Startpage was dead (0% on 2026-03-30 with rotating proxy). **Fixed 2026-03-31:** sticky session (port 10000+) + US country (`__cr.us`) + POST form. All 5 test queries passed. Now available for Phase 3 Path B (about_url discovery via search).

### Sigma Tracking — Phase 2 was first run. Need 2 more runs for trend.

### ORBT Gate Rule

| Metric Trend | ORBT Action |
|-------------|-------------|
| Sigma tightening (metrics improving run-over-run) | OPERATE — process is healthy |
| Sigma flat (no improvement after 3 runs) | REPAIR — tune parser, expand paths, check headers |
| Sigma expanding (metrics degrading) | TROUBLESHOOT — trace the circle, find first break |

---

## 11. LOGBOOK

_No runs yet on v3. Process in BUILD state._

---

## 12. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | v1 read from Neon via psql | Should read from D1 (SEED already pulled data) | v2 rewired to D1 via wrangler CLI | 1 |
| 2 | 2026-03-29 | v1 output to local JSONL only | Results not persisted to D1 | v2 writes 0/1 + signals back to outreach_blog.context_summary | 1 |
| 3 | 2026-03-29 | Startpage HTML parsing is regex-based | If Startpage changes markup, extraction breaks | v3 removes Startpage dependency — direct fetch via 16-fetcher | 1 |
| 4 | 2026-03-29 | Not yet a CF Worker | Python script with curl_cffi | Future: convert to CF Worker (keep Python for now) | 0 |
| 5 | 2026-03-29 | Startpage CAPTCHA blocks at scale | Anti-bot detection on search engine | v3 eliminates search engine entirely — direct fetch to public pages | 1 |
| 6 | 2026-03-29 | context_summary truncated at 4K chars | 4,608 records have incomplete data | Phase 1 re-parses and flags for re-fetch | 0 |

---

## 13. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | Process doc written from Dave's walkthrough | none |
| 2026-03-29 | v2 script: rewired to D1, added D1 writeback, kept proxy stack | none |
| 2026-03-29 | v3 rewrite: eliminated Startpage/proxy dependency, switched to direct fetch (16-fetcher) | none |

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
# Phase 1: Parse existing context_summary (4,608 records)
python3 src/blog-recon.py --phase 1 --limit 10

# Phase 2: Fetch known about_urls directly (13,199 companies)
python3 src/blog-recon.py --phase 2 --limit 10

# Phase 2: Full run
python3 src/blog-recon.py --phase 2

# Phase 3: Discover about_urls for ~19K companies
python3 src/blog-recon.py --phase 3 --limit 10

# All phases
python3 src/blog-recon.py

# Resume interrupted run
python3 src/blog-recon.py --resume
```

**Runtime estimate:** Direct fetch is faster than proxy-routed search. ~2-3s per company with jitter. 13K known about_urls = ~8-10 hours for Phase 2. 19K discovery = ~12-16 hours for Phase 3. Run in background with `--resume` for interruption safety.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-31 |
| Version | 3.1.0 |
| Template Version | 3.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md v1.1.2 — blog content sub-hub (04.04.05) |
| Data Flow | factory/outreach/DATA_FLOW.md |

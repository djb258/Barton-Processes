# PROCESS: Blog Reconnaissance
## Maps company web presence — about pages, team pages, sitemaps — so downstream processes have free data before calling paid tools
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-300 |
| Name | Blog Reconnaissance |
| Business Silo | svg-agency |
| CTB Position | factory/svg-agency/300-blog-worker |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | — |
| BAR Reference | — |
| Deployed URL | not deployed (currently Python script, future CF Worker) |
| Cron | Monthly (future: CF Worker cron) |
| Runtime | Python 3 script → future CF Worker |

---

## 2. WHY THIS EXISTS

Process 200 (People) needs to fill CEO/CFO/HR slots. The cheapest way to find people is from the company's own website — team pages, about pages, leadership pages. If 300 doesn't run first, 200 has to go straight to paid tools for every single slot.

300 is also the content movement detector. If a company publishes new content (funding, acquisition, leadership change), that signal feeds LCS (Process 100). But the primary value right now is giving 200 free data to work with before it spends money.

**300 runs before 200. Always.**

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Monthly. Run before Process 200. Re-run when new companies are SEEDed.
2. **"How do we get it?"** — CF Worker fetch for public pages. Startpage via DataImpulse proxy for search index freshness.

### Input
- ~32K companies in D1 with domains from `outreach_blog` (49,062 blog records, 13,186 with about_url)
- Company domains from `outreach_outreach.domain`

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Companies with `about_url` in `outreach_blog` | Fetch about/team pages via CF Worker fetch (free, public pages) | Page content — names, titles, team structure mapped | CF Worker fetch |
| 2 | Companies with domain but no `about_url` | Query Startpage via DataImpulse: `site:{domain} about team leadership` to find team page URLs | Discovered about_url / team_url stored to `outreach_blog` | Startpage + DataImpulse proxy |
| 3 | All companies with domain | Query Startpage: `site:{domain}` — check search index for freshness indicators (dates, "today", "this week") | Binary: 0 (stale) or 1 (fresh content) | Startpage + DataImpulse proxy |
| 4 | Companies where Step 3 = 1 (movement detected) | Targeted queries with signal keywords (funding, acquisition, leadership change, expansion, restructuring) | Signal classification: FUNDING_EVENT, ACQUISITION, LEADERSHIP_CHANGE, EXPANSION, RESTRUCTURING, GENERAL_NEWS | Startpage + DataImpulse proxy + LLM as tail for classification |

### Output
- `outreach_blog` updated with about_url, team_url, sitemap structure for every company where found
- Names and titles extracted from team pages (stored for Process 200 to consume)
- Content movement signals (0/1) with classification for movers
- Movement signals fed to LCS Pipeline (Process 100) signal queue

### Circle (Bedrock §5)
First pass maps everything — builds the structure (which companies have team pages, what's the URL pattern). After that, monthly runs only check for changes. The structure is the constant, the content is the variable. If a team page URL goes dead, flag it, don't assume.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | outreach_blog (about_url, source_url), outreach_outreach (domain) |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| CF Worker fetch | Native | Free | None | Fetch public about/team pages |
| Startpage | Search engine | Free | None (routed through proxy) | Google results anonymized, no CAPTCHA |
| DataImpulse | Residential proxy | Cheap (~$1/month) | PROXY_GATEWAY_URL, PROXY_API_KEY (Doppler) | Routes Startpage queries through residential IPs |
| LLM (Workers AI) | AI classification | Free (CF Workers AI) | Auto binding | Signal classification on movement=1 companies ONLY. Tail, not spine. |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_GATEWAY_URL | imo-creator | dev | DataImpulse gateway for Startpage queries |
| PROXY_API_KEY | imo-creator | dev | DataImpulse auth |

**Tool Priority (Well Drinks First):**
1. CF Worker fetch for public pages — always first, free
2. Startpage via DataImpulse — for discovery and freshness detection, cheap
3. LLM classification — only on companies with detected movement, free via Workers AI

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `outreach_blog` | about_url, source_url, news_url, context_summary | `outreach_id` |
| `outreach_outreach` | company domain | `outreach_id` |
| `outreach_company_target` | city, state (for context) | `outreach_id` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `outreach_blog` | Updated about_url, team_url, sitemap data, last_checked, movement flag | Steps 1-3 |
| Signal queue (future) | Content movement signals with classification | Step 4 |

### Join Chain

```
outreach_outreach.outreach_id (SPINE)
  → outreach_blog.outreach_id (1:1 — web presence data)
  → outreach_outreach.domain (company website)
  → outreach_company_target.outreach_id (city/state for context)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Query Neon | D1 only during WORK phase. SEED already pulled the data. |
| Fetch every page on a company site | Map the structure, don't download the content. Constants, not variables. |
| Run LLM on companies with movement=0 | AI is tail. Only fires on detected changes. Deterministic detection first. |
| Skip CF Worker fetch and go straight to proxy | Free before cheap. Always. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Does this company have a team page? | `outreach_blog` | `about_url` |
| What's the company domain? | `outreach_outreach` | `domain` |
| Has content changed since last check? | `outreach_blog` | movement flag (0/1) |
| What type of change? | Signal queue | signal_type |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)
- Detection is binary: 0 (no change) or 1 (change detected)
- 6 signal types: FUNDING_EVENT, ACQUISITION, LEADERSHIP_CHANGE, EXPANSION, RESTRUCTURING, GENERAL_NEWS
- AI is tail only — classification on 1s, detection is deterministic
- Free before cheap. CF Worker fetch before proxy.
- First pass maps everything. After that, quick update for changes only.
- URL structure is the constant. Page content is the variable.

### Variables (fill — changes every run)
- Which companies have discoverable team pages
- Which companies show content movement
- What signal type gets classified
- How many about_urls get discovered (13,186 today, grows with each run)

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
1. Count companies with domains: SELECT COUNT(*) FROM outreach_outreach WHERE domain IS NOT NULL → expected: ~32K
2. Count existing about_urls: SELECT COUNT(*) FROM outreach_blog WHERE about_url IS NOT NULL → expected: ~13,186
3. Fetch one about_url via CF Worker fetch → expected: 200 OK, HTML content
4. Query Startpage via proxy for one company domain → expected: search results returned
5. After first run: SELECT COUNT(*) FROM outreach_blog WHERE about_url IS NOT NULL → expected: > 13,186 (new discoveries)
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do the company domains exist in D1? Do the about_urls resolve?
2. **Flow:** Does CF Worker fetch reach the pages? Does the proxy route to Startpage?
3. **Change:** Are names/titles extracted correctly? Are movement signals classified accurately?

---

## 10. LOGBOOK

_No runs yet. Process in BUILD state._

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | Not yet a CF Worker | Currently Python script with psql calls | Convert to CF Worker with D1 bindings | 0 |
| 2 | 2026-03-29 | Output is local JSONL, not D1 | Signals not flowing to LCS signal_queue | Wire output to D1 tables | 0 |
| 3 | 2026-03-29 | Startpage HTML parsing is brittle | Regex-based extraction | Build resilient parser with fallback patterns | 0 |

---

## 12. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | Process doc written from Dave's walkthrough | none |

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

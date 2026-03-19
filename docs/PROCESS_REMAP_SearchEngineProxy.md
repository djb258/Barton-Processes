# Process Remap — SearchEngineProxy Changes Everything

**Date:** 2026-03-19
**Trigger:** Discovery that Startpage + DataImpulse ($1/GB) provides 95% coverage
of LinkedIn profile metadata through search engine indexing. Same architecture as
Apify's all-in-one scraper. Universal pattern applies to ALL external data sources.

---

## Before vs After

| Process | Before (Direct Fetch) | After (SearchEngineProxy) |
|---------|----------------------|--------------------------|
| **200 People** | Direct LinkedIn fetch → 15% success, HTTP 999 | Startpage query → **95% success**, $1/month |
| **300 Blog** | Fetch 290K blog URLs directly | Startpage `site:company.com` → indexed content changes |
| **400 DOL Views** | SQL views only (unchanged) | **Unchanged** — static federal data |
| **500 Talent Flow** | Blocked by 200's failure | **Unblocked** — 200 now works at 95% |
| **100 LCS** | Depends on all sub-hubs | All sub-hubs now viable |
| **700 Campaign** | Depends on 100 | Downstream unblocked |
| **Slot Filling** | Hunter $500+/month, Apollo $$ | Startpage search → find people FREE |
| **BIT Signals** | Only from sub-hub workers | New: Glassdoor sentiment, Indeed hiring, Reddit pain |

---

## New Data Sources (All via SearchEngineProxy)

### Tier 1: Feeds existing processes directly

| Query Pattern | Data Returned | Feeds Process | Cost |
|--------------|---------------|---------------|------|
| `"{name}" linkedin` | Name - Title at Company | 200 (movement detection) | $0.00005/query |
| `site:linkedin.com/company/{name}` | Employee count, industry, specialties | 200 (company enrichment) | $0.00005/query |
| `site:indeed.com "{company}" "benefits"` | Job postings for buyer persona | BIT signal → 100 | $0.00005/query |
| `site:glassdoor.com "{company}"` | Benefits satisfaction, HR complaints | BIT signal → 100 | $0.00005/query |
| `"{company}" "open enrollment"` | Enrollment cycle timing | 700 (campaign timing) | $0.00005/query |

### Tier 2: New intelligence for CID dossier

| Query Pattern | Data Returned | CID Layer |
|--------------|---------------|-----------|
| `"{company}" "RFP" "benefits"` | Active buying signal | Intent |
| `site:sec.gov "{company}"` | M&A, ownership changes | Financial |
| `site:{company}.com/careers "benefits"` | Hiring for buyer persona | Personnel |
| `"{company}" site:reddit.com "benefits"` | Employee pain signals | Behavioral |
| `site:linkedin.com/company/{competitor}` | Competitor employee movement | Competitive |

---

## Revised Process Architecture

### Process 200 — People Worker (DEPLOYED)
**Status:** Live. CF Worker deployed. D1 seeded. Startpage drip-fetch ready.

**Phase 1: Movement Detection** (monthly)
- Input: 20K LinkedIn URLs from monitor_list
- Method: Startpage query `"{name}" linkedin` → parse snippet
- Output: Title + company diff against stored baseline → 0 or 1
- Cost: ~1GB proxy bandwidth = $1/month
- Hit rate: 95% proven

**Phase 2: Slot Filling** (NEW — enabled by SearchEngineProxy)
- Input: 26K companies with empty slots
- Method: Startpage query `"{company}" "HR" OR "CFO" OR "CEO" site:linkedin.com`
- Output: Candidate names + titles for empty slots
- Cost: ~1GB proxy bandwidth = $1/month
- **This replaces Hunter/Apollo for discovery. Verification still uses well drinks (MX, SMTP).**

### Process 300 — Blog Worker
**Status:** Not started. Remap needed.

**Before:** Fetch 290K blog URLs, parse HTML, detect content changes.
**After:** Two-phase with SearchEngineProxy:

**Phase 1: Key Indicator** (monthly)
- Query: `site:{company_domain}` → check last indexed date in search results
- If Google recently re-indexed → content changed (1). Stale index → no change (0).
- Cost: ~1GB = $1/month for 290K checks

**Phase 2: Content Classification** (only on 1s)
- Query: `site:{company_domain} "funding" OR "acquisition" OR "expansion" OR "hiring"`
- Parse snippets for signal classification
- OR: Fetch page directly via DataImpulse datacenter proxy ($0.50/GB) for full content

### Process 500 — Talent Flow
**Status:** Now viable. Depends on 200 which works.

**Same as before:** Read People snapshots month-over-month, detect executive movement.
200's search-engine-based movement detection feeds 500 directly. No changes to 500's
architecture — it reads the diff output, not the fetch mechanism.

### Process 100 — LCS Pipeline
**Status:** Blocked on upstream processes.

**CID Compilation gains new layers:**
- Financial layer: DOL views (400, unchanged) + SEC via SearchEngineProxy
- Personnel layer: People (200, now working) + hiring signals via SearchEngineProxy
- Behavioral layer: Blog (300, remapped) + Glassdoor/Reddit via SearchEngineProxy
- Movement layer: Talent Flow (500, now viable)
- Intent layer: BIT scoring (folded into CID) + RFP/enrollment signals via SearchEngineProxy
- Reachability layer: SocialSweep (future) or SearchEngineProxy competitor analysis

### Process 700 — Campaign Engine
**Status:** Blocked on 100.

**Campaign timing signals from SearchEngineProxy:**
- `"{company}" "open enrollment"` → time outreach to enrollment window
- `"{company}" "benefits review"` → time outreach to review cycle
- `"{company}" "broker change"` via DOL views → time outreach to transition

---

## Revised Build Order

| Priority | Process | What Changed | Effort |
|----------|---------|-------------|--------|
| **1** | 200 People (Phase 1) | **DONE** — deployed, Startpage drip-fetch coded | Test at scale |
| **2** | 200 People (Phase 2) | **NEW** — slot filling via SearchEngineProxy | Medium — new parser |
| **3** | 300 Blog | **REMAPPED** — SearchEngineProxy replaces direct fetch | Medium — new approach |
| **4** | 500 Talent Flow | **UNBLOCKED** — reads from 200's output | Low — port v1 dumb_worker |
| **5** | 400 DOL Views | **UNCHANGED** — pure SQL | Low — 6 CREATE VIEW |
| **6** | 100 LCS Pipeline | **ENRICHED** — new CID layers from SearchEngineProxy | High — most complex |
| **7** | 700 Campaign | **ENRICHED** — timing signals from SearchEngineProxy | Medium |

---

## Monthly Execution (Revised)

```
Days 1-4:   Process 200 Phase 1 — Startpage drip-fetch (20K profiles, $1)
Days 1-4:   Process 200 Phase 2 — Slot filling search (26K companies, $1)
Days 1-4:   Process 300 — Blog key indicator check (290K domains, $1)
Day 5:      Process 500 — Talent Flow reads 200's output (minutes, $0)
Day 5:      Process 400 — DOL views always available ($0)
Day 6:      Process 100 — CID compilation with all layers
Day 7+:     Process 700 — Campaign sequencing from CID output
```

**Total monthly cost: ~$3-5 in DataImpulse proxy bandwidth.**
Replaces: Hunter ($500+), Apollo ($$$), Apify ($60), Netrows (€299).

---

## The Constant

The SearchEngineProxy (TOOL-019) + DataImpulse (TOOL-020) is the **trunk**.
Every query pattern is a **leaf parser**. The infrastructure never changes.
Only the query string and the parser change per use case.

This is Tier 0 applied to web intelligence:
- **Constant:** The fetch infrastructure (proxy + TLS impersonation + search engine)
- **Variable:** The query string and the parser for each data source
- **Gate:** Search engine result found? If yes → parse. If no → try next engine.

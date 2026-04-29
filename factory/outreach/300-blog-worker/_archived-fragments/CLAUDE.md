> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — Process 300: Blog Worker

## Governing Doctrine

**Before any work on this process, read and follow:**

1. `law/doctrine/FOUNDATIONAL_BEDROCK.md` — The engine (Three Primitives, C\&V, IMO, CTB, Circle, Troubleshooting Loop, Tier 0, Aviation Model)
2. `bedrock/math-01-engine.md` — P(x;θ) decision equation (FROZEN)
3. `bedrock/math-02-adapter-template.md` — Domain adapter interface

**Pre-flight (every session):**
- Two-Question Intake: "What triggers this?" and "How do we get it?"
- C\&V Test: Can you name it? Format it? → constant. The value filling it → variable.
- Four-Element Validation: IMO + CTB + Circle simultaneously
- Three Primitives: Thing (exists?), Flow (reaches?), Change (transforms correctly?)
- Determinism first. LLM is tail arbitration only.
- If something broke → Troubleshooting Loop (Bedrock §6). Do not patch. Do not guess.

---


## What This Process Does

Monthly content movement detector. Scans company websites via search engine proxy to detect fresh content (Phase 1), then classifies what changed into 6 signal types (Phase 2). AI is used ONLY for classification on companies where movement=1. Feeds signals to LCS Pipeline (100).

## How It Works

Two-phase monthly cycle: INDICATOR -> CLASSIFY

1. **Phase 1 -- Key Indicator Check:** For each company with a known domain, query Startpage via proxy for `site:{domain}`. Check search result snippets for freshness indicators (dates, "ago", "today", "this week"). Binary output: 0 (stale/not indexed) or 1 (fresh content detected).
2. **Phase 2 -- Signal Classification (only on 1s):** For each company where Phase 1 returned movement=1, run targeted Startpage queries with signal-specific keywords. Classify into 6 signal types. AI classification is the TAIL, not the spine -- it reads content and tags the signal type. The detection itself is deterministic.

**No sitemap XML parsing in current implementation.** Detection uses search engine index freshness as the proxy for content changes. This is cheaper and more reliable than fetching/parsing sitemaps directly.

## Signal Types

| Signal | Keywords (search terms) | Weight |
|--------|------------------------|--------|
| FUNDING_EVENT | funding, raised, series A/B, investment, venture, capital | 15 |
| ACQUISITION | acquisition, acquired, merger, buyout, takeover | 12 |
| LEADERSHIP_CHANGE | new CEO, new CFO, appointed, promoted, executive | 10 |
| EXPANSION | expansion, new office, new location, hiring spree, headcount | 8 |
| RESTRUCTURING | restructuring, layoff, reorganization, downsizing | 7 |
| GENERAL_NEWS | announcement, press release, news, update, launch | 5 |

## The Snap-On Tool: Search-Engine-as-Proxy

Same infrastructure as Process 200 (People Worker). LinkedIn blocks direct fetches. Company blogs often block scrapers. The solution is to query search engines that already indexed the data.

**Stack:**
- **Startpage** -- Google results, anonymized, no CAPTCHA
- **DataImpulse** -- residential proxy, $1/GB, 90M+ rotating IPs
- **curl_cffi** -- Chrome TLS fingerprint (looks like a real browser)
- **Box-Muller jitter** -- organic timing between requests (mean 5s, std 2s, min 2.5s)

**Credentials:** Doppler imo-creator project (PROXY_USER, PROXY_PASS, PROXY_HOST, PROXY_PORT)

**Fallback tools (not yet wired):**
- Firecrawl via Composio -- for JS-heavy pages that Startpage can't index
- ScraperAPI via Composio -- for anti-bot bypass

## Data Sources

| Source | What | How |
|--------|------|-----|
| Neon vault (people.v_territory_companies + cl.company_identity) | Company list with domains | `psql` query at startup -- gets company_unique_id, canonical_name, company_domain |
| Startpage via DataImpulse proxy | Search index freshness | `site:{domain}` query, parse `<h2>` titles and `<p class="w-gl__description">` snippets |

## Output

Phase 1 and Phase 2 write JSONL files to `src/output/`:

| File | Content |
|------|---------|
| `blog-indicators-YYYY-MM.jsonl` | One line per company: movement (0/1), reason, result_count, top_result |
| `blog-signals-YYYY-MM.jsonl` | One line per company with movement=1: detected signals with evidence |

## Usage

```bash
python3 src/blog-monitor.py                  # Full run (Phase 1 + Phase 2)
python3 src/blog-monitor.py --phase 1        # Phase 1 only (key indicator)
python3 src/blog-monitor.py --phase 2        # Phase 2 only (classify movers)
python3 src/blog-monitor.py --limit 100      # Test with 100 companies
python3 src/blog-monitor.py --resume         # Resume interrupted Phase 1
python3 src/blog-monitor.py --delay 8.0      # Override mean delay (seconds)
```

## Databases

**Neon vault (read only at startup):**
- `people.v_territory_companies` -- company list with agent assignments
- `cl.company_identity` -- canonical name and domain
- Join: `ci.company_unique_id::text = tc.company_unique_id`

**No D1 workspace yet.** Current implementation reads from Neon at startup and writes to local JSONL files. Future: seed company domains into D1, write results to D1, emit signals to LCS signal_queue.

## Key Joins

- Company list: `cl.company_identity.company_unique_id` -> `people.v_territory_companies.company_unique_id`
- Domain filter: `ci.company_domain IS NOT NULL AND ci.company_domain != ''`
- Phase 1 to Phase 2: `blog-indicators-YYYY-MM.jsonl` filtered where `movement=1` feeds Phase 2 input

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | None | Independent -- reads from CT + company_identity |
| Downstream | 100 LCS Pipeline | Content movement signals for CID compilation |

## Worker Config

- **Runtime:** Python 3 script (not yet a CF Worker)
- **Schedule:** Monthly manual run (future: CF Worker with monthly cron)
- **Proxy:** DataImpulse residential via PROXY_USER/PROXY_PASS
- **Rate:** ~720/hour with default 5s mean delay
- **Cost:** <$1/month for proxy bandwidth

## Known Issues

| Issue | Resolution |
|-------|------------|
| Not yet a CF Worker | Currently a Python script with psql subprocess calls. Future: convert to CF Worker with D1. |
| Output is local JSONL, not D1 | Signals not yet flowing to LCS signal_queue automatically. Manual handoff. |
| Startpage HTML parsing is brittle | Regex-based. If Startpage changes markup, titles/snippets extraction breaks. |
| No dedup between months | Resume flag handles within-month interruption but doesn't dedup across months. |
| DB_URL hardcoded as fallback | Production: set DATABASE_URL env var. Default fallback has credentials inline. |
| Phase 2 queries per signal type | 6 searches per company with movement=1. At scale, this is 6x the proxy cost of Phase 1. |
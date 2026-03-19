# Process 200 — People Worker Architecture

**Process ID:** PROC-PEOPLE | **Number:** 200 | **Status:** BUILD
**Governing Engine:** Tier 0 Doctrine (law/doctrine/TIER0_DOCTRINE.md)

---

## Architecture: D1 Edge Workspace + Neon Vault

D1 is the workspace. Neon is the vault. The worker operates at the edge during the month and pushes confirmed results to the vault at end of month.

```
NEON (Vault — canonical)
  │
  │  Day 1: SEED (pull territory dossier down to edge)
  ▼
D1 (Edge Workspace — working tables)
  │
  │  Days 1-28: FETCH + DETECT (LinkedIn profiles, movement 0/1)
  │
  │  Day 28+: PUSH (confirmed results back to vault)
  ▼
NEON (Vault — updated with monthly snapshots)
  │
  ▼
Downstream: Process 500 (Talent Flow), 100 (LCS), 700 (Campaign)
```

---

## Monthly Lifecycle

### Phase 1: SEED (Day 1)

Pull the full territory dossier from Neon into D1. This gives the worker everything it needs at the edge for the entire month.

**What gets seeded:**

| D1 Table | Neon Source | Rows | Purpose |
|----------|------------|------|---------|
| `companies` | `people.v_territory_companies` + `cl.company_identity` | ~35K | Territory companies with identity |
| `slots` | `people.company_slot` (for territory companies) | ~47K | All slot positions (filled + empty) |
| `people` | `people.people_master` (for territory companies) | ~35K | People filling slots |
| `blog` | `outreach.blog` (for territory companies) | ~33K | Blog data per company |
| `dol` | `outreach.dol` (for territory companies) | ~30K | DOL filing linkage |
| `bit_scores` | `outreach.bit_scores` (for territory companies) | ~4K | Current BIT scores |
| `outreach_status` | `outreach.outreach` (for territory companies) | ~36K | Outreach state |
| `baseline` | Previous month's `snapshots` (D1 or Neon) | ~20K | Previous title+company for diff |

**Total: ~255K rows seeded from Neon to D1.**

**Seed query path:**
```
coverage.service_agent (3 agents)
  → coverage.service_agent_coverage (3 active territories)
  → coverage.v_service_agent_coverage_zips (zip codes within 100mi radius)
  → outreach.company_target (companies in those zips)
  → JOIN each sub-hub table on company_unique_id or outreach_id
```

**Key views (created in Neon):**
- `people.v_territory_companies` — all companies under active agent coverage
- `people.v_territory_slots` — all slot positions for territory companies
- `people.v_territory_people` — filled slots with person details
- `people.v_linkedin_monitor_list` — people with LinkedIn URLs (the fetch list)
- `people.v_territory_summary` — dashboard rollup per agent

### Phase 2: FETCH + DETECT (Days 1-28)

Daily cron processes a batch of LinkedIn profiles.

**Batch flow:**
1. Read next unchecked profiles from `d1.monitor_list` (people with LinkedIn URLs)
2. Fetch each LinkedIn URL via UT Sub-Hub 16 (Distributed Fetcher)
3. Parse `<title>` tag → extract `parsed_title` + `parsed_company`
4. Compare to `d1.baseline` → movement: 0 or 1
5. Write snapshot to `d1.snapshots`
6. Update `d1.batch_progress`

**Movement detection:**
- `parsed_title` changed → `TITLE_CHANGED`
- `parsed_company` changed → `COMPANY_CHANGED`
- Both changed → `BOTH_CHANGED`
- Neither changed → `NONE` (0)

**Batch sizing:**
- ~20K profiles ÷ 28 days = ~715/day
- At BATCH_SIZE=100 and ~1min per profile (with delays) = ~100 profiles per cron run
- 7 cron runs per day covers 700 profiles → month completes in ~28 days

### Phase 3: PUSH (Day 28+)

Push confirmed monthly snapshots from D1 to Neon vault.

**What gets pushed:**
- `d1.snapshots` → `neon.people.linkedin_snapshots` (INSERT only, ON CONFLICT DO NOTHING)
- Movement results become the canonical record in Neon
- Downstream processes read from Neon, never from D1

---

## Intelligence Gathering: Search Engine as Proxy

**Key discovery (2026-03-19):** LinkedIn blocks direct profile fetches (HTTP 999) from
automated clients regardless of TLS fingerprint, proxy rotation, or timing. Even
residential IPs with Chrome-impersonated TLS get blocked after ~10-15 requests.

**The solution:** Don't scrape LinkedIn. Query search engines that already indexed LinkedIn.
This is the same architecture Apify's "all-in-one" LinkedIn scraper uses — they confirmed
it publicly: HTTP-only with Impit, residential proxy rotation, multi-source search fallback.

**How it works:**
- Startpage anonymizes Google search results → returns LinkedIn metadata in `<h2>` tags
- Search: `{person_name} linkedin` → returns "Name - Title at Company | LinkedIn"
- Routed through DataImpulse residential proxy ($1/GB)
- curl_cffi with Chrome TLS fingerprint impersonation
- Box-Muller distributed jitter for organic timing (not metronomic)
- **Proven: 95% hit rate on test batch (2026-03-19)**

**Three-tier search fallback (same as Apify):**
1. **Startpage** (primary) — Google results anonymized, clean HTML, $0 + proxy bandwidth
2. **Brave Search API** (fallback) — independent index, $3-5/1K queries, structured JSON
3. **LinkedIn direct** (last resort) — via DataImpulse proxy, ~15% success rate

**Cost: ~$1-2/month** for 20K profiles through DataImpulse proxy bandwidth.

**Tools (documented in Snap-On Toolbox):**

| Tool | Role | Cost |
|------|------|------|
| DataImpulse residential proxy | IP diversity (90M+ IPs) | $1/GB pay-as-you-go |
| curl_cffi (Python) | Chrome TLS fingerprint impersonation | Free (MIT) |
| Startpage | Google results without Google's anti-bot | Free |
| Brave Search API | Independent index fallback | $3-5/1K (if needed) |

**Fetch behavior:**
- Box-Muller jitter: mean 5s, std 2s, floor 2.5s (organic timing)
- DataImpulse rotating residential IPs (new IP per request)
- Chrome TLS fingerprint via curl_cffi impersonate="chrome"
- Session persistence for cookie accumulation
- Resume support (JSONL append, skip already-fetched)
- ~20K profiles in ~3-4 hours at default pace

---

## LinkedIn Profile Parsing

**Phase 1 indicator:** The `<title>` tag.

LinkedIn `<title>` format: `{Name} - {Title} at {Company} | LinkedIn`

**Fields extracted from one GET:**

| Field | Source | Phase |
|-------|--------|-------|
| `parsed_name` | `<title>` tag | 1 |
| `parsed_title` | `<title>` tag | 1 (movement check) |
| `parsed_company` | `<title>` tag | 1 (movement check) |
| `headline` | og:description | 1 (stored) |
| `location` | JSON-LD addressLocality | 1 (stored) |
| `last_post_date` | JSON-LD article datePublished | 1 (freshness indicator) |
| `profile_photo_url` | JSON-LD image | 1 (stored) |

**Movement detection uses only `parsed_title` + `parsed_company`.** Everything else is captured for the wide schema (Monte Carlo decides what matters later).

---

## Database Schema

### D1 (Edge Workspace)

**Working tables (seeded monthly from Neon):**
- `companies` — territory companies with identity data
- `slots` — all slot positions (filled + empty)
- `people` — people filling slots (with LinkedIn URLs)
- `blog` — blog data per company
- `dol` — DOL filing linkage
- `bit_scores` — current BIT scores
- `outreach_status` — outreach state per company

**Process tables (owned by the worker):**
- `monitor_list` — LinkedIn URLs to check this month
- `baseline` — previous month's title+company for diff
- `snapshots` — this month's fetch results + movement detection
- `batch_progress` — tracking (total, checked, movements, errors, pushed)
- `errors` — local error log

### Neon (Vault — Canonical)

- `people.linkedin_snapshots` — monthly snapshots pushed from D1 (INSERT-only)
- `people.v_linkedin_movement` — movement detection view for downstream consumption

### Migration files

| File | Target | Purpose |
|------|--------|---------|
| `001_d1_working_tables.sql` | D1 | Working tables + process tables |
| `002_neon_vault_table.sql` | Neon | Canonical snapshots + movement view |

---

## Cost

| Component | Cost |
|-----------|------|
| CF Worker (cron + HTTP) | $0 (free tier: 100K req/day) |
| D1 database | $0 (free tier: 5M reads/day, 100K writes/day, 5GB storage) |
| LinkedIn fetches (via domain rotation) | $0 (CF fetch, no third-party scraping) |
| Neon (vault reads/writes) | Existing plan (no incremental cost) |
| **Total** | **$0/month** |

---

## Data Volumes

| Metric | Count |
|--------|-------|
| Territory companies | 35,629 |
| Total slot positions | 47,091 |
| Filled slots | 22,812 |
| People with LinkedIn URLs | ~20,063 |
| D1 seed rows (total) | ~255K |
| LinkedIn fetches per month | ~20K |
| Fetches per domain per day | ~50 |

---

## Agents (Territory)

| Agent | Number | Anchor | Radius | Companies |
|-------|--------|--------|--------|-----------|
| Dave Allan | SA-001 | 26739 (WV) | 100mi | 6,872 |
| Jeff Mussolino | SA-002 | 21742 (MD) | 100mi | 25,420 |
| David Vang | SA-003 | 28461 (NC) | 100mi | 3,337 |

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| GET | `/status` | Current month progress |
| POST | `/seed` | Manual trigger: seed from Neon |
| POST | `/run-batch` | Manual trigger: process next batch |
| POST | `/push` | Manual trigger: push to Neon vault |

---

## File Structure

```
factory/200-people-worker/
├── heir.yaml                          # Process HEIR definition
├── ARCHITECTURE.md                    # This file
├── wrangler.toml                      # CF Worker config (D1 + secrets)
├── package.json                       # Dependencies
├── tsconfig.json                      # TypeScript config
└── src/
    ├── index.ts                       # CF Worker entry — lifecycle phases
    ├── linkedin-parser.ts             # Parse <title> tag + JSON-LD
    ├── ut/
    │   └── fetcher.ts                 # UT Sub-Hub 16 — distributed fetcher
    └── migrations/
        ├── 001_d1_working_tables.sql  # D1 schema (edge workspace)
        └── 002_neon_vault_table.sql   # Neon schema (canonical vault)
```

---

## Replication Pattern (For Other Processes)

This D1-edge + Neon-vault pattern is reusable for any monthly process:

1. **Define territory scope** — which companies, via coverage views
2. **Create Neon views** — query path from agents → zips → companies → sub-hubs
3. **Create D1 working tables** — mirror the relevant sub-hub data at the edge
4. **Monthly SEED** — pull from Neon views into D1 (Day 1)
5. **Daily FETCH** — process batches using D1 data (Days 1-28)
6. **Monthly PUSH** — confirmed results from D1 back to Neon (Day 28+)

Process 300 (Blog Worker) follows the same pattern with different sub-hub data and different fetch targets (blog URLs instead of LinkedIn profiles).

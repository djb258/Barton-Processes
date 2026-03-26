# CLAUDE.md — Process 200: People Worker

## Governing Doctrine

**Before any work on this process, read and follow:**

1. `law/doctrine/FOUNDATIONAL_BEDROCK.md` — The engine (Three Primitives, C&V, IMO, CTB, Circle, Troubleshooting Loop, Tier 0, Aviation Model)
2. `bedrock/math-01-engine.md` — P(x;θ) decision equation (FROZEN)
3. `bedrock/math-02-adapter-template.md` — Domain adapter interface

**Pre-flight (every session):**
- Two-Question Intake: "What triggers this?" and "How do we get it?"
- C&V Test: Can you name it? Format it? → constant. The value filling it → variable.
- Four-Element Validation: IMO + CTB + Circle simultaneously
- Three Primitives: Thing (exists?), Flow (reaches?), Change (transforms correctly?)
- Determinism first. LLM is tail arbitration only.
- If something broke → Troubleshooting Loop (Bedrock §6). Do not patch. Do not guess.

---

## What This Process Does

Fills CEO/CFO/HR slots for 27,868 agent-assigned companies. Detects movement (person changed title, left, arrived). Feeds signals to Talent Flow (500) and LCS Pipeline (100). Without filled slots, nothing downstream works.

## How It Works

Monthly cycle: SEED → FETCH → DETECT → PUSH

1. **SEED** (Day 1): Pull territory from Neon vault → D1 workspace. ~255K rows.
2. **FETCH** (Days 1-28): Daily batch of 100 LinkedIn profiles via proxy. Parse `<title>` tag for name + title + company. 30-120 second random delay between fetches.
3. **DETECT** (per batch): Compare snapshot to baseline. Binary movement per slot: 0 or 1. Signals: JOINED, LEFT, REPLACED, TITLE_CHANGED, EMAIL_CHANGED.
4. **PUSH** (Day 28+): Promote verified results from D1 → Neon vault.

## The Snap-On Tool: Search-Engine-as-Proxy

LinkedIn blocks direct fetches (HTTP 999). The solution is to query search engines that already indexed the data.

**Stack:**
- **Startpage** — Google results, anonymized, no CAPTCHA
- **DataImpulse** — residential proxy, $1/GB, 90M+ rotating IPs
- **curl_cffi** — Chrome TLS fingerprint (looks like a real browser)
- **Box-Muller jitter** — organic timing between requests

**Three-tier fallback:**
1. Startpage through DataImpulse (free + proxy) — **95% hit rate**
2. Brave Search API ($3-5/1K queries) — backup
3. LinkedIn direct (15% rate) — last resort

**Cost:** $1-2/month for 20K profiles.

**Credentials:** Doppler imo-creator project (PROXY_USER, PROXY_PASS, PROXY_HOST, PROXY_PORT)

**This same proxy infrastructure is reusable for ANY indexed platform:**
- LinkedIn profiles → title + company movement
- LinkedIn company pages → employee count, industry
- Glassdoor → benefits sentiment
- Indeed → hiring signals
- Company career pages → open positions
- SEC/OpenCorporates → M&A activity

## Tool Priority (Well Drinks First)

| Tier | Tools | Cost | When |
|------|-------|------|------|
| Well Drinks | MXLookup, SMTPCheck, LinkedInCheck (CF fetch) | Free | Always first |
| House Pours | Composio (routes to integrations) | Cheap | After well drinks |
| Top Shelf | Hunter, Apollo, MillionVerifier | Per-call | Only when well drinks exhausted |

**Rule:** Never pour top shelf before well drinks are empty.

## Data Sources & Trust Levels

| Source | Trust | Why |
|--------|-------|-----|
| DOL-linked companies | HIGHEST | Federal filing proves viability, has benefits plan |
| Hunter-sourced | MEDIUM | Domain exists, unverified against federal records |
| Clay-sourced | MEDIUM | Scraped data, unverified |

## Enrichment Priority

1. DOL-linked + movement + empty slots → FIRST (verified, hot, needs people)
2. DOL-linked + no movement + empty slots → SECOND (verified, needs people)
3. Non-DOL companies → THIRD (verify viability before spending)

## Slot Constants

- **Types:** CEO, CFO, HR (fixed — these three, always)
- **Priority:** CEO → CFO → HR
- **Minimum for LCS:** 1 reachable slot

## Reachability Gate

Must pass BEFORE company enters LCS pipeline:

| Status | Meaning | Channel |
|--------|---------|---------|
| UNREACHABLE | No slots filled or no contact method | Blocked — cannot enter LCS |
| EMAIL_ONLY | Verified email, no LinkedIn | Mailgun path |
| LINKEDIN_ONLY | LinkedIn URL, no email | HeyReach path |
| FULL | Both channels available | Best position |

## Databases

**D1 workspace:** `people-worker-200` (4fa3b760)
- `companies` — 35K territory companies
- `slots` — 47K slot positions (CEO/CFO/HR per company)
- `people` — contact details (name, email, LinkedIn, phone)
- `monitor_list` — ~20K LinkedIn profiles to check
- `baseline` — previous month snapshot for diff
- `snapshots` — current month fetch results
- `batch_progress` — tracking current batch position
- `errors` — error drain per fetch attempt

**Neon vault:** Source for SEED, destination for PUSH. Never queried during FETCH.

## Movement Detection

- **Type:** Deterministic (no AI)
- **Method:** Slot-by-slot snapshot diff, month over month
- **Output:** 0 (no change) or 1 (movement)
- **Signals:** JOINED, LEFT, REPLACED, TITLE_CHANGED, EMAIL_CHANGED

## Key Joins

- Territory filter: `outreach.company_target.zip` → `coverage.v_service_agent_coverage_zips.zip`
- People slots: `people.company_slot.outreach_id` → `people.people_master.unique_id`
- LinkedIn parse: `<title>` tag → regex split → `"Name - Title at Company | LinkedIn"`

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | Neon vault | Company data + previous people records |
| Upstream | Coverage zones | 3 agents × radius → territory filter |
| Downstream | 500 Talent Flow | Movement signals (0/1 per slot) |
| Downstream | 100 LCS Pipeline | Recipient slots for SID construction |

## Worker Config

- **URL:** people-worker-200.svg-outreach.workers.dev
- **Cron:** `0 6 * * *` (daily 6am UTC)
- **Batch size:** 100 profiles per cron
- **Delay:** 30-120 seconds between fetches (randomized)
- **Proxy:** DataImpulse residential via `PROXY_URL`

## Known Issues

| Issue | Resolution |
|-------|------------|
| Google blocks with CAPTCHAs through proxy | Use Startpage via DataImpulse — 95% hit rate |
| Bing APIs retired Aug 2025 | Removed Bing, Startpage exclusively |
| BIT scoring retired 2026-03-25 | Remove `bit_scores` table references |

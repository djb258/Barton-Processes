> **ARCHIVED 2026-04-29** — Consolidated into PROCESS-UT.md and DOCTRINE.md during UT v2.7.0 standardization. See sibling files at folder root.

# AUDIT REPORT — Process 200: People Worker
# Date: 2026-03-25
# Auditor: Claude Opus 4.6 (1M context)
# Builder: Claude (prior sessions) + Dave Barton
# Status: IN PROGRESS — gate by gate

---

## VERDICT: PENDING (audit in progress)

---

## GATE 1: THREE PRIMITIVES (Bedrock §1)

### 1.1 THING — Does every component exist where it should?

| Component | Exists? | Evidence |
|-----------|---------|----------|
| CF Worker deployed | YES | `people-worker-200.svg-outreach.workers.dev/health` returns `{"process":"PROC-PEOPLE","number":200,"status":"ok"}` |
| D1 database | YES | `people-worker-200` (4fa3b760) — 13 tables |
| Cron schedule | YES | `0 6 * * *` (daily 6am UTC) in wrangler.toml |
| heir.yaml | YES | 94 lines, PROC-PEOPLE, process 200 |
| CLAUDE.md | YES | 152 lines, Bedrock reference included |
| MANIFEST.md | YES | 164 lines, 11-block format |
| OSAM.md | YES | Exists |
| ERD.md | YES | Exists |
| PRD.md | YES | Exists |
| Proxy endpoint | YES | `linkedin-proxy.insuranceinformatic.agency` returns HTTP 200 |
| Doppler secrets | PARTIAL | `barton-outreach-core/prd` has only default Doppler vars. Process-specific secrets (NEON_URL, PROXY_SECRET) set via `wrangler secret put`, not Doppler project. |

**FINDING 1.1-A:** `bit_scores` table exists in D1 but BIT scoring is retired (2026-03-25). Table should be dropped.

| Field | Value |
|-------|-------|
| **Squawk** | Retired table `bit_scores` still exists in D1 |
| **Root Cause** | BIT scoring retired but D1 table not cleaned up |
| **Fix Required** | `DROP TABLE IF EXISTS bit_scores;` on people-worker-200 D1 |
| **Fix Verified** | NOT YET |
| **Strike** | 0 (first occurrence) |

**FINDING 1.1-B:** Secrets not in Doppler — set via `wrangler secret put` instead.

| Field | Value |
|-------|-------|
| **Squawk** | NEON_URL and PROXY_SECRET set as wrangler secrets, not managed in Doppler |
| **Root Cause** | Process was built before Doppler integration was standardized |
| **Fix Required** | Move NEON_URL and PROXY_SECRET to Doppler project `barton-outreach-core`. Update wrangler.toml to reference Doppler. |
| **Fix Verified** | NOT YET |
| **Strike** | 0 (first occurrence) |

### 1.2 FLOW — Does the data reach every component?

| Data Path | Works? | Evidence |
|-----------|--------|----------|
| D1 companies seeded | YES | 32,702 rows |
| D1 slots seeded | YES | 43,203 rows |
| D1 people seeded | YES | 20,487 rows |
| D1 monitor_list populated | YES | 18,038 LinkedIn profiles |
| D1 baseline populated | **NO** | 0 rows — never populated |
| Proxy routes to correct destination | **NO** | Routes to CF Tunnel → LinkedIn direct. Should route to Startpage via DataImpulse. |
| Snapshots written from fetches | PARTIAL | 4 of 800 (0.5% success rate) |

**FINDING 1.2-A:** Baseline table has 0 rows — movement detection has no comparison point.

| Field | Value |
|-------|-------|
| **Squawk** | `baseline` table is empty. `seedBaseline()` was never successfully executed or Day 1 SEED didn't trigger. |
| **Root Cause** | The cron only seeds on `day === 1` (first of month). If the worker was deployed mid-month (March 19), the SEED phase was skipped. Baseline requires previous month's snapshots — but only 4 snapshots exist, so baseline would be near-empty anyway. |
| **Fix Required** | 1. Fix the fetcher first (Finding 1.3-A). 2. Run a manual SEED via `POST /seed`. 3. After one month of successful fetches, baseline will populate from snapshots. |
| **Fix Verified** | NOT YET — blocked by Finding 1.3-A |
| **Strike** | 0 (first occurrence) |
| **Dependency** | Blocked by FINDING 1.3-A (fetcher fix) |

**FINDING 1.2-B:** Proxy routes to wrong destination.

| Field | Value |
|-------|-------|
| **Squawk** | `fetcher.ts` sends requests to `linkedin-proxy.insuranceinformatic.agency` (CF Tunnel) which hits LinkedIn directly → HTTP 999 |
| **Root Cause** | Fetcher was built with CF Tunnel architecture. The SearchEngineProxy discovery (Startpage via DataImpulse, 95% hit rate) happened AFTER the fetcher was coded. Code was never updated. |
| **Fix Required** | Rewrite `fetcher.ts` to use Startpage query through DataImpulse residential proxy. See Gate 7 for full specification. |
| **Fix Verified** | NOT YET |
| **Strike** | 0 (first occurrence) |
| **Dependency** | This is the ROOT CAUSE of Finding 1.3-A |

### 1.3 CHANGE — Does the transformation happen correctly?

| Transformation | Works? | Evidence |
|----------------|--------|----------|
| LinkedIn fetch succeeds | **NO** | 4 successes / 800 attempts = 0.5% success rate |
| Profile parsing works | UNKNOWN | Only 4 profiles fetched — too small to evaluate parser quality |
| Movement detection works | **NO** | Compares against `people` table instead of `baseline` table (code bug). Baseline is empty anyway. |
| Snapshot writes | PARTIAL | 4 rows written to `snapshots`. Schema and write logic work. Volume is the problem. |
| Error logging | YES | 710 errors logged with error_code and error_message. Errors are queryable. |

**FINDING 1.3-A (CRITICAL):** Fetcher produces 98.5% error rate — process cannot operate.

| Field | Value |
|-------|-------|
| **Squawk** | 800 profiles checked, 710 errors, 4 successes. Process is non-functional. |
| **Root Cause** | `fetcher.ts` routes through CF Tunnel → LinkedIn direct. LinkedIn returns HTTP 999 (bot block). CF Tunnel returns error 1033 (tunnel misconfigured or down). |
| **Error Breakdown** | HTTP 999: 309 (LinkedIn bot block). Error 1033: 309 (CF Tunnel failure). Error 502: 91 (proxy gateway error). HTTP 404: 1 (invalid profile URL). |
| **Fix Required** | Rewrite `fetcher.ts`: (1) Query Startpage with `site:linkedin.com/in/ "{name}"` search. (2) Route through DataImpulse residential proxy ($1/GB). (3) Parse search results for LinkedIn profile snippet. (4) Implement three-tier fallback: Startpage → Brave Search API → LinkedIn direct. |
| **Fix Verified** | NOT YET |
| **Strike** | 0 (first occurrence — root cause identified, not a repeat failure) |
| **Blocks** | Everything downstream — no valid snapshots means no movement detection, no signals, no pipeline input |

**FINDING 1.3-B:** Movement detection compares against wrong table.

| Field | Value |
|-------|-------|
| **Squawk** | `index.ts` lines 109-114 query `people` + `companies` tables for stored title/company. Should query `baseline` table. |
| **Root Cause** | Code was written to compare against current people records instead of the monthly snapshot baseline. The `baseline` table exists and is seeded by `seedBaseline()` but `processBatch()` never reads it. |
| **Fix Required** | Replace the `stored` query at `index.ts` lines 109-114 with: `SELECT parsed_title as stored_title, parsed_company as stored_company FROM baseline WHERE person_id = ?` |
| **Fix Verified** | NOT YET |
| **Strike** | 0 (first occurrence) |

---

**FINDING 1.3-C (CRITICAL): 74% of companies have ZERO filled slots — unreachable.**

| Field | Value |
|-------|-------|
| **Squawk** | 24,232 of 32,702 companies (74%) have zero filled slots. Only 8,470 companies (26%) have at least one person in a slot. Only 6,681 (20%) have a verified email. The pipeline has no one to send to for three-quarters of the territory. |
| **Data** | Total people: 20,487. Have email: 19,953 (97%). Verified email: 13,643 (67%). Have LinkedIn: 18,038 (88%). Have BOTH: 17,666 (86%). Have NEITHER: 162 (<1%). |
| **Slot Fill Rates** | CEO: 7,931 filled (55%). CFO: 6,357 filled (44%). HR: 6,361 filled (44%). |
| **Verified Email by Slot** | CEO: 4,167. CFO: 4,798. HR: 4,755. Total: 13,720 verified emails across all slots. |
| **Root Cause** | The People Worker's enrichment cycle hasn't run successfully. 98.5% fetch error rate (Finding 1.3-A) means slots can't be filled from LinkedIn. The 8,470 filled slots are from the original Clay/Hunter import — no new enrichment has occurred. |
| **Fix Required** | 1. Fix fetcher (Finding 1.3-A). 2. Run enrichment against the 24,232 dark companies — LinkedIn search for CEO/CFO/HR by company name. 3. Verify emails via well-drinks-first cascade (MX lookup → SMTP check → MillionVerifier if needed). |
| **Fix Verified** | NOT YET |
| **Strike** | 0 (first occurrence — enrichment never ran successfully) |
| **Impact** | Pipeline capacity: max 6,681 companies with verified email. At 280 emails/day (14 domains × 20/day warmup), that's 24 days to reach all currently reachable companies once. But 74% of the territory is invisible. |

---

### GATE 1 VERDICT: FAIL

| Check | Result |
|-------|--------|
| 1.1 THING | **PASS with findings** (all components exist, 2 cleanup items) |
| 1.2 FLOW | **FAIL** (baseline empty, proxy routes to wrong destination) |
| 1.3 CHANGE | **FAIL** (98.5% error rate, wrong comparison table) |

### ARCHITECTURAL FINDING (supersedes individual fix items above)

**FINDING 1.X-ARCH (CRITICAL): Process 200 has a standalone D1 that duplicates outreach data. Scrap and rewire.**

| Field | Value |
|-------|-------|
| **Squawk** | Process 200 maintains its own D1 database (`people-worker-200`, 4fa3b760) with 13 tables duplicating data that already exists in `svg-d1-outreach-ops`. The standalone D1 has 20,487 people; the outreach D1 has 32,106. The standalone D1 went stale immediately. This is a sovereign silo violation — Process 200 created a branch-level copy instead of operating on the trunk data. |
| **Root Cause** | Process 200 was designed as a self-contained worker with its own SEED→WORK→PUSH lifecycle. The correct architecture is: outreach D1 owns all data. Process 200 is an enrichment worker that READS and UPDATES existing outreach tables. No new tables. No standalone D1. |
| **What Already Exists in svg-d1-outreach-ops** | `outreach_company_target` (32,704), `people_company_slot` (43,209), `people_people_master` (32,106), `outreach_people` (109,443), `outreach_dol` (36,247), `outreach_blog` (49,062), `dol_form_5500` (14,252), `dol_schedule_a` (9,538), `dol_schedule_c` (18,246), `dol_schedule_other` (67,164) |
| **What Process 200 Should Do** | 1. READ from `svg-d1-outreach-ops` — companies, slots, people (data is already there). 2. FETCH via UT sub-hubs (Startpage/DataImpulse) — LinkedIn profiles for slot enrichment. 3. UPDATE `svg-d1-outreach-ops` — fill empty slots, update titles/emails in existing `people_people_master` and `people_company_slot` rows. 4. WRITE movement signals to `svg-d1-spine` → `lcs_signal_queue`. |
| **What Process 200 Should NOT Do** | No standalone D1. No SEED from Neon. No duplicate tables. No `people-worker-200` database. |
| **Fix Required** | Full rewire: (1) Delete `people-worker-200` D1. (2) Rewrite `wrangler.toml` to bind `svg-d1-outreach-ops` and `svg-d1-spine`. (3) Rewrite worker to read/update existing outreach tables. (4) Rewrite fetcher to use Startpage/DataImpulse. (5) Write movement signals to spine `lcs_signal_queue`. |
| **Fix Verified** | NOT YET |
| **Strike** | 0 |
| **Impact** | All prior individual findings (1.1-A through 1.3-C) are resolved by this architectural fix. The standalone D1, the incomplete SEED, the stale data, the wrong baseline comparison — all go away when Process 200 operates on the real outreach data. |

### FIX PRIORITY ORDER (REVISED)

| Priority | Finding | What | Blocks |
|----------|---------|------|--------|
| 1 | 1.X-ARCH | Rewire Process 200 to operate on svg-d1-outreach-ops (no standalone D1) | Everything |
| 2 | 1.3-A | Rewrite fetcher.ts (Startpage/DataImpulse via UT sub-hubs) | Enrichment |
| 3 | 1.3-C | Run enrichment against 24,232 dark companies | Reachability |
| 4 | 1.3-B | Movement detection (compare current vs prior snapshot in outreach tables) | Signals |

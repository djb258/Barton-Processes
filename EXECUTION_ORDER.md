# EXECUTION ORDER — SVG Agency Processes
## The sequence is a constant. You cannot run a process before its upstream is complete.
### Authority: FOUNDATIONAL_BEDROCK.md §4 (CTB — children conform to parent)

---

## The Outcome — Fully Enriched Company Record (The Setpoint)

Every company in the pipeline should have ALL dimensions filled. 100% is the setpoint — the constant we measure against. The actual fill rate is the variable. The delta is the build list.

| Dimension | Target (Setpoint) | Current (2026-03-31) | Gap |
|-----------|-------------------|---------------------|-----|
| SEED (companies in D1) | ~32K | 32,704 | Done (OPERATE) |
| Blog (about_url mapped) | 32K (100%) | 13,199 (40%) | 19,505 companies without about_url |
| People (3 slots filled w/ email + LinkedIn) | 98,112 slots (100%) | ~54% CEO, ~50% CFO, ~43% HR | ~50K empty slots |
| DOL (linked to filing) | 32K (100%) | 36,247 records | Coverage % against 32K TBD |
| Talent Flow (movement signals) | Running monthly | Not running | 0% — needs Process 200 first |

**Realistically, 100% is not achievable.** Not every company has a public about page. Not every CEO has a LinkedIn. But 100% is the domesticated variable — the setpoint that sigma tracks against. The gap tells you where to improve.

**The Circle:** Once messages go out (Process 100 → MID delivery), response data feeds back through the pipeline. 10-3-1 becomes the measurable outcome: 10 contacted → 3 respond → 1 becomes client. Monte Carlo simulation models the full system with real distributions and shows which dimension has the most leverage — not A/B testing, statistical convergence.

---

## The Rule

**A process cannot run until every process it depends on has completed and passed its analytics baseline.** This is not a suggestion. If the upstream data isn't there, the downstream process produces garbage.

---

## Execution Phases

### Phase 1: SEED (Neon → D1)

| Order | Process | Name | Depends On | What It Produces |
|-------|---------|------|-----------|-----------------|
| 1 | 010 | SVG D1 SEED | Neon vault populated | D1 workspace with full company footprint (CT, DOL, Blog, People, Coverage) |

**Gate:** D1 audit passes — row counts, join integrity, agent assignment. If SEED fails, NOTHING runs.

---

### Phase 2: DATA ENRICHMENT (fill the footprint)

| Order | Process | Name | Depends On | What It Produces |
|-------|---------|------|-----------|-----------------|
| 2 | 300 | Blog Monitor | 010 SEED complete | Web presence mapped — about_urls discovered, names/titles extracted, movement detected (0/1) |
| 3 | 200 | People Slot Filler | 010 SEED + **300 Blog complete** | CEO/CFO/HR slots filled with verified email + LinkedIn. Reachability status per company. |
| 4 | 400 | DOL Views | 010 SEED complete | DOL signals: renewal windows, premium pressure, carrier/broker changes. Independent of 200/300. |
| 5 | 500 | Talent Flow | **200 People complete** (needs LinkedIn snapshots) | Executive movement signals (TF-01 joined, TF-02 left) |

**300 MUST complete before 200.** 200 consumes 300's extracted people data as its free first pass. Without 300, 200 goes straight to paid tools.

**200 MUST complete before 500.** 500 compares LinkedIn snapshots month-over-month. No snapshots = no movement detection.

**400 is independent.** Runs after SEED, doesn't depend on 200 or 300. Can run in parallel with Phase 2.

---

### Phase 3: COMPILE + DELIVER (the engine)

| Order | Process | Name | Depends On | What It Produces |
|-------|---------|------|-----------|-----------------|
| 6 | 100 | LCS Pipeline | **ALL of Phase 2 complete** (200, 300, 400, 500) | CID → SID (via LBB for content) → MID. Compiled intelligence + personalized message + delivery. Domain warmup IS the campaign — ramp from 20/domain/day on shared Mailgun IPs. |
| 7 | 700 | Campaign Engine | **100 LCS complete** (needs CID targets) | Sequenced outreach: no movement = 1/month, movement = 3-5 over 2 weeks |

**100 is the last outreach process.** It compiles everything upstream into the message. If any upstream data is missing, the CID is thin, the SID is generic, the MID is weak.

**700 runs after 100.** It sequences the deliveries that 100 compiled.

---

### Phase 4: CONVERSION (prospect → client)

| Order | Process | Name | Depends On | What It Produces |
|-------|---------|------|-----------|-----------------|
| 8 | 900 | Sales Portal | Prospect responds to outreach (from 100/700) | 4-meeting sales cycle: Fact Finder → Insurance → Systems → Financials |
| 9 | 800 | Client Mint | Sales closes (900 phase = closed) | Sovereign ID → client_id. Prospect becomes client. |
| 10 | 810 | Client Intake | **800 Client Mint complete** | Benefits data ingested: plans, employees, elections, vendors |
| 11 | 820 | Vendor Export | **810 Intake complete** | Export files generated for TPAs, PBMs, carriers |
| 12 | 830 | Client Portal | **810 Intake complete** | Client-facing portal with 5 audience pages |

---

## Dependency Graph

```
010 SEED
  │
  ├──→ 300 Blog ──→ 200 People ──→ 500 Talent Flow ──┐
  │                                                     │
  ├──→ 400 DOL (parallel) ────────────────────────────┤
  │                                                     │
  │                                    ALL Phase 2 ────┘
  │                                         │
  │                                         ▼
  │                                    100 LCS Pipeline
  │                                         │
  │                                         ▼
  │                                    700 Campaign Engine
  │                                         │
  │                                    (prospect responds)
  │                                         │
  │                                         ▼
  │                                    900 Sales Portal
  │                                         │
  │                                    (sale closes)
  │                                         │
  │                                         ▼
  │                                    800 Client Mint
  │                                         │
  │                                         ▼
  │                                    810 Client Intake
  │                                         │
  │                                    ┌────┴────┐
  │                                    ▼         ▼
  │                               820 Export  830 Portal
```

---

## First Run Sequence (getting baselines)

For the initial baseline run, execute in this exact order. Do not skip ahead.

| Step | Process | Action | Baseline Metrics | Status (2026-03-31) |
|------|---------|--------|-----------------|---------------------|
| 1 | 010 SEED | Verify (already OPERATE) | Row counts, join integrity, fill rates | DONE — 32,704 companies, 3 agents, all sub-hubs verified |
| 2 | 300 Blog | Run Phase 2 (re-fetch about_urls) + Phase 3 (discover 19K without about_url using Startpage) | Pages fetched, hit rate, about_urls discovered | PARTIAL — Phase 2 ran (5,200 pages, 811 people, 15.6% hit). Phase 3 not run. Startpage fix proven (sticky session + US country + POST form). |
| 3 | 200 People | Run Pass 1 (staging + blog data from 300) | Slots filled from free data, hit rate | NOT STARTED — needs 300 output |
| 4 | 400 DOL | Query views against D1 | Signal counts per type | DONE — 171K rows seeded, 6 views queryable |
| 5 | 200 People | Run Pass 2 (Startpage search via DataImpulse sticky session) | Hit rate, cost per slot | NOT STARTED — Startpage fix proven but not wired into 200 |
| 6 | 500 Talent Flow | Run first month comparison | Movements detected, signal counts | NOT STARTED — needs 200 LinkedIn snapshots |
| 7 | 100 LCS | Run compiler on test batch, query LBB for SID content | Compilation rate, tier distribution, gate pass rate | READY — compiler-v2 deployed, needs upstream data |
| 8 | 100 LCS | Deliver test MID via Mailgun (shared IPs, 20/domain/day warmup ramp) | Delivery rate, bounce rate, domain reputation | READY — 14 domains verified, 0 emails sent, warmup starts with real outreach |

**After step 8, all outreach baselines are set. Go shopping with vendor-scout (27) for any dimension below target.**

### Domain Warmup Note

No separate warmup process (PROC-750 eliminated). Mailgun shared IPs are already warm. Domain reputation builds by sending real outreach at controlled volume. The warmup IS the campaign. Ramp: 20→40→80→150→250/domain/day over 5 weeks. See PROC-100 for full ramp table.

### Key Technical Discoveries (2026-03-31)

- **Startpage fix:** DataImpulse sticky session (port 10000+) + US country targeting (`__cr.us` in username) + POST form submission + 3s delay. All 5 test queries passed. This unblocks Process 300 Phase 3 and Process 200 Pass 2.
- **LBB replaces SVG Brain:** SID construction queries LBB (Library Barton Brain) for Barton voice, messaging frameworks, and company-specific intel. One library, Dewey Decimal classification.
- **10-3-1 + Monte Carlo:** Once messages flow, response data feeds back through the pipeline. Statistical convergence, not A/B testing.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-31 |
| Last Modified | 2026-03-31 |
| Version | 2.0.0 |
| Authority | FOUNDATIONAL_BEDROCK.md §4 (CTB) + §8 (Aviation — logbook first) |
| Location | Barton-Processes/EXECUTION_ORDER.md |

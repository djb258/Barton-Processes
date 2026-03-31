# EXECUTION ORDER — SVG Agency Processes
## The sequence is a constant. You cannot run a process before its upstream is complete.
### Authority: FOUNDATIONAL_BEDROCK.md §4 (CTB — children conform to parent)

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
| 6 | 100 | LCS Pipeline | **ALL of Phase 2 complete** (200, 300, 400, 500) | CID → SID (via SVG Brain) → MID. Compiled intelligence + personalized message + delivery. |
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

| Step | Process | Action | Baseline Metrics |
|------|---------|--------|-----------------|
| 1 | 010 SEED | Verify (already OPERATE) | Row counts, join integrity, fill rates |
| 2 | 300 Blog | Run Phase 2 (fetch about_urls) + Phase 3 (discover) | Pages fetched, hit rate, about_urls discovered |
| 3 | 200 People | Run Pass 0 (staging) + Pass 1 (blog data) | Slots filled, hit rate per pass, cost |
| 4 | 400 DOL | Query views against D1 | Signal counts per type |
| 5 | 200 People | Run Pass 2 (search — if needed) | Hit rate, cost per slot |
| 6 | 500 Talent Flow | Run first month comparison | Movements detected, signal counts |
| 7 | 100 LCS | Run compiler on test batch | Compilation rate, tier distribution, gate pass rate |
| 8 | 100 LCS | Deliver test MID | Delivery rate, bounce rate |

**After step 8, all outreach baselines are set. Go shopping with vendor-scout (27).**

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-31 |
| Last Modified | 2026-03-31 |
| Version | 1.0.0 |
| Authority | FOUNDATIONAL_BEDROCK.md §4 (CTB) + §8 (Aviation — logbook first) |
| Location | Barton-Processes/EXECUTION_ORDER.md |

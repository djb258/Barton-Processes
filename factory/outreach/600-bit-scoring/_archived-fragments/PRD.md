> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# PRD — Process 600: BIT Scoring
## Product Requirements — What It Does, What "Done" Looks Like

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped requirements |
| **Last Updated** | 2026-03-24 |

---

## Purpose

Buyer Intent Tracker. Aggregates signals from ALL dumb worker sub-hubs (DOL, People, Blog, Talent Flow) into a single composite score per company. Pure computation — no external tools, no AI. Reads everything, decides nothing. The score tells the LCS pipeline HOW to prioritize outreach.

---

## Two-Question Intake

1. **"What triggers this?"** — Monthly cron, runs AFTER all dumb workers complete their cycle. Reads their output, doesn't generate its own.
2. **"How do we get it?"** — Sum weighted signals per company from outreach D1 tables. Classify into band (0-5). Write to `outreach_bit_scores`.

---

## Requirements

### R1: Signal Aggregation
- Read DOL signals: filing_present, broker_change, renewal_approaching, premium_increase
- Read People signals: slots_filled, email_verified
- Read Blog signals: funding, acquisition, expansion, leadership_change
- Read Talent Flow signals: executive_joined, executive_left
- **Acceptance:** All signal sources read for every company in territory

### R2: Weighted Scoring
- Each signal has a defined weight (see OSAM.md signal weights table)
- Three categories: Structural Pressure (DOL), Decision Surface (People), Narrative Volatility (Blog)
- Composite = sum of all weighted signals
- **Acceptance:** Score matches manual calculation for test companies

### R3: Band Classification
- Band 0 (0-9): SILENT — no outreach
- Band 1 (10-24): WATCH — internal flag
- Band 2 (25-39): EXPLORATORY — 1 educational/60 days
- Band 3 (40-59): TARGETED — persona-specific, 3 max
- Band 4 (60-79): ENGAGED — phone warm, 5 max
- Band 5 (80+): DIRECT — direct contact, meeting request
- **Acceptance:** Every scored company assigned correct band

### R4: Component Scores
- Store individual component scores: people_score, dol_score, blog_score, talent_flow_score
- These tell you WHERE the signal is coming from, not just the total
- **Acceptance:** Component scores sum to composite score

### R5: Gate 8 Integration
- LCS pipeline Gate 8 reads BIT score for qualification
- Band 0-1 companies do NOT enter the pipeline
- Band 2+ companies proceed to CID compilation
- **Acceptance:** Gate 8 correctly reads and evaluates BIT score

### R6: Execution Order
- Runs AFTER: Process 200 (People), 300 (Blog), 400 (DOL), 500 (Talent Flow)
- Runs BEFORE: Process 100 (LCS Pipeline)
- **Acceptance:** No stale data — all inputs from current cycle

---

## Non-Requirements

- AI-based scoring (pure computation only)
- Real-time scoring (monthly batch is sufficient)
- External API calls (reads D1 only)
- Scoring companies outside agent territory

---

## Definition of Done

All 6 requirements pass. Every company in territory has a current BIT score and band. Gate 8 correctly reads scores. Component breakdown available for analysis.

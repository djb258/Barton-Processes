> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# PROCESS-600: BIT Scoring
# Status: EXTRACTED (BLD)
# Last Updated: 2026-03-24

---

## IDENTITY (HEIR)

| Field | Value |
|-------|-------|
| Process ID | PROC-BIT |
| Number | 600 |
| Name | BIT Scoring (Buyer Intent Tracker) |
| Blueprint | barton-outreach-core (company-target sub-hub) |
| Runtime | Cloudflare Workers (monthly cron — runs AFTER all dumb workers) |
| Deployed URL | Not yet deployed |
| ORBT | BLD |
| Strikes | 0 |

---

## IMO

**Input:** Signals from all dumb worker sub-hubs: DOL (400), People (200), Blog (300), Talent Flow (500). Each signal has a type and magnitude. BIT runs AFTER all workers complete their monthly cycle.

**Middle:**
1. Read all signals for each company from D1
2. Weight each signal by category:
   - Structural Pressure (DOL): FORM_5500 +5, BROKER_CHANGE +7, RENEWAL_APPROACHING +5, PREMIUM_INCREASE +5
   - Decision Surface (People): SLOT_FILLED +10, EMAIL_VERIFIED +3, EXEC_JOINED +10, EXEC_LEFT -5
   - Narrative Volatility (Blog): FUNDING_EVENT +15, ACQUISITION +12, EXPANSION +8, LEADERSHIP_CHANGE +10
3. Sum weighted scores per company
4. Classify into band (0-5)

**Output:** Composite score and band per company in `outreach_bit_scores`. Gate 8 in the LCS pipeline reads this score.

**Circle:** Each cycle's scores compared to prior. Sigma tracking: tightening = real signal, flat = noise, expanding = model needs recalibration.

---

## DATABASES

### Reads from: Outreach D1 (svg-d1-outreach-ops)

| Table | What | Join Key |
|-------|------|----------|
| outreach_company_target | Company list | outreach_id |
| outreach_dol | DOL signals | outreach_id |
| people_company_slot | People slot state | outreach_id |
| outreach_blog | Blog signals | outreach_id |

### Writes to: Outreach D1 (svg-d1-outreach-ops)

| Table | Role | Key Columns |
|-------|------|-------------|
| outreach_bit_scores | CANONICAL | outreach_id, score, score_tier, signal_count, component scores |

---

## BANDS

| Band | Score | Name | Action |
|------|-------|------|--------|
| 0 | 0-9 | SILENT | No outreach |
| 1 | 10-24 | WATCH | Internal flag only |
| 2 | 25-39 | EXPLORATORY | 1 educational / 60 days |
| 3 | 40-59 | TARGETED | Persona-specific, 3 max |
| 4 | 60-79 | ENGAGED | Phone warm, 5 max |
| 5 | 80+ | DIRECT | Direct contact, meeting request |

---

## DEPENDENCIES

### Upstream
| Dependency | What | Status |
|-----------|------|--------|
| Process 200 (People) | Slot fill data | DEPLOYED |
| Process 300 (Blog) | Blog signals | EXTRACTED |
| Process 400 (DOL) | DOL filing data | EXTRACTED |
| Process 500 (Talent Flow) | Movement signals | EXTRACTED |

### Downstream
| Consumer | What |
|----------|------|
| Process 100 (LCS Pipeline) | Gate 8 reads BIT score for qualification |
| Dashboard | Displays BIT score per company |

---

## CURRENT STATE (as of 2026-03-24)

| Metric | Value |
|--------|-------|
| Companies scored | 13,000 (from prior Python run) |
| Bands distributed | 6 bands (0-5) |
| Data in outreach D1 | 12 columns per score record |
| CF Worker | Not yet deployed — scoring currently runs via Python scripts |

---

## KNOWN ISSUES

| Date | Issue | Resolution | Strikes |
|------|-------|------------|---------|
| None | — | — | — |

---

## SMOKE TEST

1. Pick a company with known DOL + People data
2. Calculate expected score manually (sum weighted signals)
3. Run BIT scoring for that company
4. Verify score matches manual calculation
5. Verify band assignment is correct
6. Check that outreach_bit_scores row was written

---

## NEXT STEPS

| What | BAR | Status |
|------|-----|--------|
| Port Python scoring to CF Worker | — | TODO |
| Deploy as monthly cron (runs after People Worker) | — | TODO |
| Wire into LCS Gate 8 | BAR-131 | DONE (gate reads from D1) |

---

## FILES

```
Barton-Processes/factory/600-bit-scoring/
├── heir.yaml      # Identity
├── MANIFEST.md    # This file
└── src/           # Scoring logic (extracted from barton-outreach-core)
```

---

## SESSION LOG

| Date | Session | What Was Done | Brain Chunks |
|------|---------|---------------|-------------|
| 2026-03-24 | Manifest written | Documentation created from heir.yaml + brain knowledge | `session/2026-03-24-full-session-final` |

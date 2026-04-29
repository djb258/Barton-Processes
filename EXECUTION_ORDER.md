# EXECUTION ORDER — Generated from law/process-registry.yaml
# DO NOT EDIT BY HAND. To regenerate: `python scripts/render-execution-order.py > EXECUTION_ORDER.md`
# Last regenerated: 2026-04-29
# TODO: automate this via scripts/render-execution-order.py when registry depends_on fields are populated

---

## Overview

The sequence is a constant. A process cannot run until every upstream dependency has completed and passed its analytics baseline. This is not a suggestion — if upstream data is absent, downstream produces garbage.

**Setpoint**: Fully enriched company record — all 5 dimensions filled (SEED, People, DOL, Blog, Talent).

---

## Phase 1 — Foundation (SEED + Schema)

| # | Process | Folder | ORBT | Depends On |
|---|---------|--------|------|------------|
| 010 | SEED D1 | factory/outreach/010-seed-d1/ | OPERATE | none |

**Gate**: D1 company table populated. ~32K+ records present. Until this passes, nothing else can run.

---

## Phase 2 — Enrichment (People, DOL, Blog, Signals)

| # | Process | Folder | ORBT | Depends On |
|---|---------|--------|------|------------|
| 200 | People Worker | factory/outreach/200-people-worker/ | REPAIR | 010 |
| 201 | Email Discovery | factory/outreach/201-email-discovery/ | BUILD | 200 |
| 202 | LinkedIn Discovery | factory/outreach/202-linkedin-discovery/ | BUILD | 200 |
| 300 | Blog Worker | factory/outreach/300-blog-worker/ | BUILD | 010 |
| 301 | Page Parser | factory/outreach/301-page-parser/ | BUILD | 300 |
| 400 | DOL Views | factory/outreach/400-dol-views/ | OPERATE | 010 |
| 500 | Talent Flow | factory/outreach/500-talent-flow/ | BUILD | 200 |

**Gate**: 3 contact slots filled per company (CEO, CFO, HR) with email + LinkedIn where findable. DOL linked. Blog about_url mapped.

---

## Phase 3 — Compile + Score

| # | Process | Folder | ORBT | Depends On |
|---|---------|--------|------|------------|
| 600 | BIT Scoring | factory/outreach/600-bit-scoring/ | TROUBLESHOOT_TRAIN | 200, 300, 400, 500 |

**Gate**: Every company has a BIT authorization band (0-5). Scoring model stable (sigma tightening).

---

## Phase 4 — Deliver + Convert

| # | Process | Folder | ORBT | Depends On |
|---|---------|--------|------|------------|
| 700 | Campaign Engine | factory/outreach/700-campaign-engine/ | BUILD | 600 |
| 100 | LCS Pipeline | factory/cl/100-lcs-pipeline/ | REPAIR | 700 |

**Gate**: Messages sent. Webhook feedback closes the circle. 10-3-1 measurable.

---

## Phase 5 — Client + Sales (parallel track, not upstream of outreach)

| # | Process | Folder | ORBT | Depends On |
|---|---------|--------|------|------------|
| 800 | Client Mint | factory/cl/800-client-mint/ | BUILD | 100 (sovereign ID) |
| 810 | Client Intake | factory/client/810-client-intake/ | BUILD | 800 |
| 820 | Vendor Export | factory/client/820-vendor-export/ | BUILD | 810 |
| 830 | Client Portal | factory/client/830-client-portal/ | BUILD | 810 |
| 900 | Sales Portal | factory/sales/900-sales-portal/ | BUILD | 100 (outreach data) |

---

## The Circle

Once messages go out (Campaign Engine → LCS delivery), response data feeds back through the pipeline. 10-3-1 becomes measurable: 10 contacted → 3 respond → 1 becomes client. Monte Carlo simulation models the full system. BIT band is the lever — not A/B testing, statistical convergence.

---

## Current Gaps (2026-04-29)

| Dimension | Setpoint | Gap |
|-----------|----------|-----|
| SEED | ~32K companies | Operational (OPERATE) |
| People (3 slots) | 98K+ slots at 100% | ~50% fill rate — 200 REPAIR |
| DOL (linked to filing) | 32K at 100% | Operational (OPERATE) |
| Blog (about_url mapped) | 32K at 100% | ~40% — 300 BUILD |
| Talent Flow (movement signals) | Monthly | 500 BUILD — needs 200 first |
| BIT Scoring | Model stable | 600 TROUBLESHOOT_TRAIN |
| Campaign/LCS | Running | 700/100 BUILD/REPAIR |

---

## Document Control

| Field | Value |
|-------|-------|
| Last Modified | 2026-04-29 (Stage 2.5 CTB Cleanup) |
| Generated from | law/process-registry.yaml v2.0.0 |
| Authority | imo-creator-v2 (Inherited) |

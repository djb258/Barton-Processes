# CLAUDE.md — Process 400: DOL Views

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

Query library against the DOL (Department of Labor) filing schema in Neon. Six read-only SQL views that detect actionable changes in employee benefits filings: renewal proximity, premium pressure, carrier instability, broker churn. NOT a worker. NOT a cron job. Just SQL views and a reference for how to query them.

## How It Works

No pipeline. No fetch cycle. DOL data is annual (Form 5500 filings from EBSA). The data is static between annual imports. These views answer: "given the filings we have, which companies show movement?"

1. **Annual import:** EBSA Form 5500 bulk download, loaded into Neon `dol` schema. Manual process (not automated).
2. **Views query existing data:** Six views defined in `src/001_dol_views.sql`. Each view computes a different signal by comparing filing years.
3. **DOL detail now in D1:** As of 2026-03-25, 171,040 rows seeded into D1 across 4 tables (`dol_form_5500`, `dol_schedule_a`, `dol_schedule_c`, `dol_schedule_other`) covering 27,868 companies. LCS Pipeline (100) reads from D1, not Neon.

## The 6 Views

### View 1: Filing Status (Gate 3)
**`dol.v_dol_filing_status`** -- Binary: does this company have DOL filings?
- Groups by EIN, returns latest_form_year, participant count, plan count, state
- Gate 3 pass = `has_filing = TRUE`

### View 2: Renewal Window (Gate 4)
**`dol.v_dol_renewal_window`** -- Companies approaching plan renewal within 90 days
- Takes latest filing per EIN, projects `form_plan_year_begin_date + 1 year` as next renewal
- `renewal_approaching = TRUE` when within 90 days of today
- `days_to_renewal` for prioritization

### View 3: Premium Pressure (Gate 5)
**`dol.v_dol_premium_pressure`** -- YoY participant count changes
- Compares consecutive filing years per EIN
- `significant_decrease = TRUE` when participants dropped >10%
- `significant_increase = TRUE` when participants grew >10%
- `pct_change` column for ranking

### View 4: Market Comparison (PEPM Benchmarking)
**`dol.v_dol_market_comparison`** -- Per-Employee-Per-Month broker cost by state/carrier/size
- Joins `form_5500` to `schedule_a` on `ack_id`
- Size bands: SMALL (<50), MID (50-199), LARGE (200-999), JUMBO (1000+)
- `avg_pepm_broker_cost` and `median_pepm_broker_cost` for competitive analysis
- Used to tell a prospect "you're paying X, the market pays Y"

### View 5: Carrier Changes
**`dol.v_dol_carrier_changes`** -- Carrier instability signal
- Compares primary carrier (by covered lives) YoY per EIN
- `carrier_changed = TRUE` when carrier name differs between consecutive years
- Join path: `schedule_a.ack_id` -> `form_5500.ack_id`

### View 6: Broker Changes
**`dol.v_dol_broker_changes`** -- Broker churn signal
- Compares primary broker name YoY per EIN
- `broker_changed = TRUE` when broker name differs between consecutive years
- Join path: `schedule_a_part1.ack_id` -> `schedule_a.ack_id` -> `form_5500.ack_id`

## Signal Types

| Signal | Source View | Meaning |
|--------|-----------|---------|
| RENEWAL_APPROACHING | v_dol_renewal_window | Plan renewal within 90 days -- decision maker is shopping |
| PREMIUM_INCREASE | v_dol_premium_pressure | Participants grew >10% -- costs rising |
| CARRIER_CHANGE | v_dol_carrier_changes | Carrier switched YoY -- company is actively shopping |
| BROKER_CHANGE | v_dol_broker_changes | Broker switched YoY -- relationship instability |
| PLAN_CHANGE | v_dol_premium_pressure | Participant count shifted significantly |
| OVERPAYING | v_dol_market_comparison | PEPM above median for state/size band |

## Databases

**Neon vault (dol schema) -- source of truth:**

| Table | Row Count | Key Columns |
|-------|-----------|-------------|
| `dol.form_5500` | 432K+ | ack_id (PK), sponsor_dfe_ein, form_year, tot_active_partcp_cnt, form_plan_year_begin_date, sponsor_dfe_name, spons_dfe_mail_us_state |
| `dol.form_5500_sf` | 1.5M+ | Short-form filings (small plans) |
| `dol.schedule_a` | 625K+ | ack_id (FK), sch_a_ein, ins_carrier_name, ins_prsn_covered_eoy_cnt, ins_broker_comm_tot_amt, ins_broker_fees_tot_amt |
| `dol.schedule_a_part1` | varies | ack_id (FK), ins_broker_name, row_order |
| `dol.schedule_c` | varies | Service provider compensation data |

**D1 workspace (seeded from Neon as of 2026-03-25):**

| Table | Rows | Purpose |
|-------|------|---------|
| `dol_form_5500` | 14,252 | Filing data for territory companies only |
| `dol_schedule_a` | 17,890 | Broker/insurance details |
| `dol_schedule_c` | 33,810 | Service provider records |
| `dol_schedule_other` | 105,088 | Other schedule data (JSON) |

## Key Joins

- EIN is the universal DOL join key: `form_5500.sponsor_dfe_ein` = `schedule_a.sch_a_ein`
- Filing to schedule: `form_5500.ack_id` = `schedule_a.ack_id` (1:many -- one filing, multiple insurance arrangements)
- Schedule A to Part 1: `schedule_a.ack_id` = `schedule_a_part1.ack_id` AND `schedule_a.form_id` = `schedule_a_part1.form_id`
- DOL to company target: `outreach_company_target.outreach_id` -> `outreach_dol.outreach_id` (in D1 outreach)
- DOL detail to territory: `dol_form_5500.company_unique_id` links back to territory

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | None | Independent -- annual EBSA data import (manual) |
| Downstream | 100 LCS Pipeline | DOL intelligence for CID compilation (tier 2-3) |

## Tools Required

None. Direct SQL queries against Neon or D1. No external APIs, no proxy, no workers.

## Usage

```bash
# Apply views to Neon
psql $DATABASE_URL -f src/001_dol_views.sql

# Query examples
psql $DATABASE_URL -c "SELECT * FROM dol.v_dol_renewal_window WHERE renewal_approaching = true LIMIT 10"
psql $DATABASE_URL -c "SELECT * FROM dol.v_dol_carrier_changes WHERE carrier_changed = true LIMIT 10"
psql $DATABASE_URL -c "SELECT * FROM dol.v_dol_market_comparison WHERE state = 'WV' AND form_year = '2023'"
```

## Known Issues

| Issue | Resolution |
|-------|------------|
| Views run against Neon, but LCS reads D1 | DOL detail seeded to D1 as of 2026-03-25 (171K rows). Views still useful for ad-hoc analysis in Neon. |
| EIN matching is imperfect | Some EINs in form_5500 don't match schedule_a EINs. Use `ack_id` join for filing-level accuracy. |
| Annual data only | DOL filings lag 6-18 months. Renewal window calculations use projected dates, not confirmed. |
| PEPM calculation depends on schedule_a completeness | Not all filings have broker commission data. NULL values filtered out. |
| company_unique_id linkage | Not all DOL records have company_unique_id populated. EIN-to-company matching was done during initial load. |
| form_year is TEXT in some contexts | Cast to INT when comparing consecutive years: `curr.form_year::INT = prev.form_year::INT + 1` |

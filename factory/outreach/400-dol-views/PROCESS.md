# PROCESS: DOL Views
## SQL view library against DOL filing data — 6 read-only views that detect renewal proximity, premium pressure, carrier instability, and broker churn from annual Form 5500 filings
### Status: OPERATE
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-400 |
| Name | DOL Views |
| Business Silo | svg-agency |
| Sub-Hub | outreach |
| CTB Position | factory/outreach/400-dol-views |
| ORBT | OPERATE |
| Strikes | 0 |
| Last Deployed | 2026-03-25 (D1 seed of 171,040 rows) |
| BAR Reference | BAR-49 |
| Deployed URL | not deployed (SQL views — no worker) |
| Cron | none |
| Runtime | SQL views (not a worker) |

---

## 2. WHY THIS EXISTS

DOL Form 5500 filings are the only public dataset that shows what a company spends on employee benefits, which carrier they use, and which broker manages it. This process turns that raw filing data into 6 actionable views that detect movement: renewal windows, premium pressure, carrier switches, and broker churn. Without it, the LCS Pipeline (Process 100) has no DOL intelligence for CID compilation at tiers 2-3 — you'd be reaching out blind to companies that may not even have a benefits plan.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Nothing triggers it. Views exist and are queryable on demand. Underlying data refreshes once per year via manual EBSA bulk import.
2. **"How do we get it?"** — Annual EBSA Form 5500 bulk download, loaded into Neon `dol` schema. As of 2026-03-25, 171,040 rows seeded to D1 across 4 tables for LCS runtime access.

### Input
- DOL Form 5500 annual filings from EBSA (Department of Labor)
- Manual bulk download, loaded into Neon `dol` schema
- Seeded to D1 for runtime use by downstream processes

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | EBSA bulk CSV | **Annual Import** — download Form 5500 bulk data from EBSA website, load into Neon `dol` schema tables | Neon tables populated | psql / manual load |
| 2 | Neon `dol` tables | **View Creation** — apply `src/001_dol_views.sql` to create 6 read-only views | 6 queryable views in Neon | psql -f |
| 3 | Neon `dol` tables | **D1 Seed** — Process 010 copies DOL data to D1 for runtime access | 4 D1 tables (171,040 rows) | Process 010 SEED |
| 4 | Any query | **On-demand read** — downstream processes or ad-hoc queries hit views/tables | Signal data (boolean + numeric) | SQL SELECT |

### Output
- 6 boolean/numeric signals per EIN: filing status, renewal proximity, premium pressure, market comparison, carrier change, broker change
- Consumed by Process 100 LCS Pipeline for CID intelligence tiers 2-3
- Available for ad-hoc analysis directly in Neon

### Circle (Bedrock §5)
Annual cycle: EBSA publishes filings (lag 6-18 months) → manual import to Neon → SEED to D1 → views queryable → LCS uses signals for outreach → outreach results inform next year's targeting priorities. The data itself is static between annual imports — no feedback loop within a single cycle.

---

## 4. WHAT IT GRABS OFF THE WALL

### Blueprint Reference

| Field | Value |
|-------|-------|
| Blueprint | barton-outreach-core |
| OSAM Section | doctrine/OSAM.md -- DOL filings sub-hub (04.04.03) |
| Snap-On Toolbox | law/SNAP_ON_TOOLBOX.yaml |

### Snap-On Toolbox Tools

| Sub-Hub # | Tool | What It Does Here |
|-----------|------|-------------------|
| 11-structured-data | Cloudflare D1 | SQL views and D1 runtime tables — all reads, no external tools |

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| Neon (dol schema) | DATABASE_URL | Hyperdrive | READ ONLY | Source of truth — full DOL filing history, 6 SQL views |
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ ONLY | D1 runtime copy — 4 DOL tables (171K rows) for LCS |

### Tools & Integrations (Snap-On Toolbox references — see law/SNAP_ON_TOOLBOX.yaml for vendor details)

| Item | Snap-On Sub-Hub | Cost Tier | Credentials | What It Does |
|------|----------------|-----------|-------------|-------------|
| Cloudflare D1 | 11-structured-data | Free | D1 binding | Runtime copy of DOL data for LCS queries |
| psql (ad-hoc) | 11-structured-data | Free | DATABASE_URL (Doppler) | Apply views, run ad-hoc queries against Neon |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| DATABASE_URL | imo-creator | dev | Neon connection for view creation and ad-hoc queries |

**Tool Priority (Well Drinks First):**
1. D1 tables (free, already seeded) — runtime queries
2. Neon views (free, direct SQL) — ad-hoc analysis and view definitions
3. No external APIs required — this is pure SQL

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `dol_form_5500` (D1) | Filing data — EIN, form year, participant count, plan year begin date, state | `sponsor_dfe_ein` (EIN) |
| `dol_schedule_a` (D1) | Insurance arrangements — carrier name, covered lives, broker commissions | `ack_id` → `form_5500.ack_id` |
| `dol_schedule_c` (D1) | Service provider compensation data | `ack_id` → `form_5500.ack_id` |
| `dol_schedule_other` (D1) | Other schedule data (JSON) | `ack_id` → `form_5500.ack_id` |
| `dol.form_5500` (Neon) | Full DOL filing history (432K+ rows) | `sponsor_dfe_ein` (EIN) |
| `dol.schedule_a` (Neon) | Full insurance schedule (625K+ rows) | `ack_id` → `form_5500.ack_id` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| None | This process is read-only | Never — views are SELECT only |

### Join Chain

```
dol_form_5500.sponsor_dfe_ein (EIN — universal DOL join key)
  → dol_schedule_a.ack_id = dol_form_5500.ack_id (1:many — one filing, multiple insurance arrangements)
  → dol_schedule_a_part1.ack_id = dol_schedule_a.ack_id (broker detail)
  → dol_schedule_c.ack_id = dol_form_5500.ack_id (service provider compensation)
outreach_company_target.outreach_id → outreach_dol.outreach_id (D1 outreach — links DOL to company target)
dol_form_5500.company_unique_id → territory linkage
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Write to any DOL table from a view or downstream process | DOL data is source-of-truth from EBSA. INSERT only during annual import. |
| Query Neon at LCS runtime | D1 has the seeded copy. Neon is vault only. |
| Automate the EBSA import | Manual process — data quality review required before load. |
| Join on EIN alone across schedules | Use `ack_id` for filing-level accuracy. EIN matching is imperfect across tables. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Does this company have DOL filings? | `dol_form_5500` | `sponsor_dfe_ein` (existence check) |
| When is their plan renewal? | `dol_form_5500` | `form_plan_year_begin_date` + 1 year projection |
| Did participant count change YoY? | `dol_form_5500` | `tot_active_partcp_cnt` (compare consecutive `form_year`) |
| What do they pay per employee per month? | `dol_schedule_a` | `ins_broker_comm_tot_amt` + `ins_broker_fees_tot_amt` / `ins_prsn_covered_eoy_cnt` / 12 |
| Did they switch carriers? | `dol_schedule_a` | `ins_carrier_name` (compare consecutive years, same EIN) |
| Did they switch brokers? | `dol_schedule_a_part1` | `ins_broker_name` (compare consecutive years, same EIN) |
| What state are they in? | `dol_form_5500` | `spons_dfe_mail_us_state` |
| What size band? | `dol_form_5500` | `tot_active_partcp_cnt` → SMALL (<50), MID (50-199), LARGE (200-999), JUMBO (1000+) |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants
- 6 views: Filing Status, Renewal Window, Premium Pressure, Market Comparison, Carrier Changes, Broker Changes
- 6 signal types: RENEWAL_APPROACHING, PREMIUM_INCREASE, CARRIER_CHANGE, BROKER_CHANGE, PLAN_CHANGE, OVERPAYING
- EIN is the universal DOL join key
- `ack_id` is the filing-level join key (form to schedules)
- Size bands: SMALL (<50), MID (50-199), LARGE (200-999), JUMBO (1000+)
- Renewal window threshold: 90 days
- Significant change threshold: 10% YoY participant delta
- Data source: EBSA Form 5500 annual bulk download
- 4 D1 tables: `dol_form_5500`, `dol_schedule_a`, `dol_schedule_c`, `dol_schedule_other`
- Detection method: deterministic (compare filing years — no AI required)

### Variables
- Which filing year is "current" (depends on EBSA publication lag — typically 6-18 months)
- How many rows are seeded to D1 (171,040 as of 2026-03-25 across 27,868 companies)
- Which companies have complete schedule_a data (not all filings include broker commissions)
- Which EINs successfully match to `company_unique_id` in the territory
- Actual renewal dates (projected from `form_plan_year_begin_date`, not confirmed)
- PEPM benchmarks per state/size band (shift annually as new filings arrive)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| EBSA bulk download format changes | HALT — review schema mapping before import |
| D1 seed row count drops vs. prior year | HALT — investigate missing data before overwriting |
| EIN-to-company match rate drops below 80% | HALT — review matching logic |
| View returns zero rows for a known-populated state | HALT — schema or join broke |
| `form_year` data type inconsistency (TEXT vs INT) | HALT — cast explicitly, do not assume |
| Annual import not completed by Q2 | FLAG — data is stale, signals may be outdated |
| Strike 3 on same failure | Troubleshoot/Train — produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| EBSA Form 5500 bulk data | Annual filing download from DOL website | DONE (loaded to Neon) |
| Process 010 (SEED) | Copies DOL data from Neon to D1 for runtime | DONE (171,040 rows as of 2026-03-25) |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 100 (LCS Pipeline) | DOL intelligence for CID compilation at tiers 2-3 — filing status, renewal signals, premium pressure |
| Ad-hoc analysis | Direct Neon view queries for benchmarking and competitive intel |

---

## 9. SMOKE TEST

```
1. psql $DATABASE_URL -c "SELECT COUNT(*) FROM dol.form_5500" → expected: 432K+ rows
2. psql $DATABASE_URL -c "SELECT COUNT(*) FROM dol.v_dol_filing_status" → expected: >0 rows (companies with filings)
3. psql $DATABASE_URL -c "SELECT * FROM dol.v_dol_renewal_window WHERE renewal_approaching = true LIMIT 5" → expected: rows with days_to_renewal <= 90
4. psql $DATABASE_URL -c "SELECT * FROM dol.v_dol_carrier_changes WHERE carrier_changed = true LIMIT 5" → expected: rows with prev/curr carrier names differing
5. psql $DATABASE_URL -c "SELECT * FROM dol.v_dol_broker_changes WHERE broker_changed = true LIMIT 5" → expected: rows with prev/curr broker names differing
6. psql $DATABASE_URL -c "SELECT * FROM dol.v_dol_premium_pressure WHERE significant_increase = true LIMIT 5" → expected: rows with pct_change > 10%
7. psql $DATABASE_URL -c "SELECT * FROM dol.v_dol_market_comparison WHERE state = 'WV' LIMIT 5" → expected: PEPM data for WV companies
8. D1 check: SELECT COUNT(*) FROM dol_form_5500 → expected: ~14,252 rows
9. D1 check: SELECT COUNT(*) FROM dol_schedule_a → expected: ~17,890 rows
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do the 4 D1 tables exist with data? Do the 6 Neon views exist?
2. **Flow:** Can a query reach each view and return rows? Does D1 data match Neon source?
3. **Change:** Do the views correctly compute boolean signals (renewal_approaching, carrier_changed, etc.)?

If any fails — that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock §6).

---

## 10. LOGBOOK

### 2026-03-25 — D1 seed complete

**ORBT:** BUILD → OPERATE
**Trigger:** Process 010 SEED run
**Records processed:** 171,040 rows across 4 tables (27,868 companies)
**Errors:** 0
**Tools used:** Process 010 SEED, D1
**Result:** DOL data now in D1 for LCS runtime access. Views remain in Neon for ad-hoc analysis.
**Learnings:** EIN matching to company_unique_id is partial — not all DOL records link to territory companies.
**ORBT after:** OPERATE

### 2026-03-19 — Views created in Neon

**ORBT:** BUILD
**Trigger:** Manual — initial view creation
**Records processed:** 6 views created against existing Neon DOL tables
**Errors:** 0
**Tools used:** psql, src/001_dol_views.sql
**Result:** All 6 views queryable. Filing status, renewal window, premium pressure, market comparison, carrier changes, broker changes.
**ORBT after:** BUILD (pending D1 seed)

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-19 | EIN matching is imperfect across tables | Some EINs in form_5500 don't match schedule_a EINs | Use `ack_id` join for filing-level accuracy, EIN for company-level | 0 |
| 2 | 2026-03-25 | Not all DOL records have company_unique_id | EIN-to-company matching done during initial load, partial coverage | Accept partial — improve matching in future SEED runs | 0 |
| 3 | 2026-03-25 | form_year is TEXT in some contexts | Neon schema inconsistency | Cast to INT when comparing consecutive years | 0 |
| 4 | 2026-03-25 | PEPM calculation depends on schedule_a completeness | Not all filings have broker commission data | NULL values filtered out in view — known data gap | 0 |
| 5 | 2026-03-25 | Annual data lag | DOL filings lag 6-18 months behind real-time | Accepted limitation — renewal projections are estimates, not confirmed | 0 |

---

## 12. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-19 | 6 SQL views created in Neon against DOL schema | none |
| 2026-03-25 | 171,040 rows seeded to D1 across 4 tables via Process 010 | session/2026-03-25 |
| 2026-03-29 | PROCESS.md written from template v2.0.0 | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.1.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

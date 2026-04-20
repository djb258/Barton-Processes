# Sales Sub-Hub — Tables Audit
## svg-d1-sales (D1 database ID: 95835f64-db7f-43d4-b211-899b11a17c96)
### Date: 2026-04-16
### Authority: Dave Barton
### Status: AUDIT COMPLETE — migration required

---

## Audit Method

- **Schema source:** `SELECT name, sql FROM sqlite_master WHERE type='table'` run live against svg-d1-sales
- **Requirements source:** `fleet/docs/SALES-SUB-HUB.md` + `fleet/content/INSURANCE-INFORMATICS-CTB.md`
- **Process being audited:** Four-gate sales process (Gate 1: Factfinder → Gate 2: Insurance/Monte Carlo → Gate 3: Service Demo → Gate 4: Numbers/Quote)

---

## What Exists — 11 Tables

| Table | Type | Columns (excluding timestamps) | Assessment |
|-------|------|-------------------------------|------------|
| `sales_state` | Canonical (spine) | sales_id, sovereign_ref, hub_id, cc_layer, ctb_placement, company_name, company_domain, sovereign_id, outreach_id, current_phase, status, source, bit_score, orbt_mode, strike_count | THIN — missing `current_carrier`, `current_broker`, `dol_employee_count`; no error table for the spine |
| `sales_factfinder` | Canonical (Gate 1) | sales_id, employer_name, employee_count, renewal_month, prior_broker | SEVERELY THIN — Gate 1 is "bring the bill" — the bill data (tiers, costs, funding type, monthly premium) is entirely absent |
| `sales_factfinder_errors` | Error (Gate 1) | error_id, sales_id, error_code, payload, process_id | OK |
| `sales_insurance` | Canonical (Gate 2) | sales_id, funding_model, strategy_selected | SEVERELY THIN — Monte Carlo output, cost projections, savings estimates, hospital/drug landscape flags are all absent |
| `sales_insurance_errors` | Error (Gate 2) | error_id, sales_id, error_code, payload, process_id | OK |
| `sales_systems` | Canonical (Gate 3) | sales_id, payroll_system, admin_model, compliance_owner | THIN — TPA/PBM/PPO network selections, HR platform, benefit admin platform, implementation dates are absent |
| `sales_systems_errors` | Error (Gate 3) | error_id, sales_id, error_code, payload, process_id | OK |
| `sales_quotes` | Canonical (Gate 4) | sales_id, quote_version, total_cost, approved_flag | SEVERELY THIN — stop loss quote, ancillary quote, competitive notes, presented_at timestamp are absent |
| `sales_quotes_errors` | Error (Gate 4) | error_id, sales_id, error_code, payload, process_id | OK |
| `sales_contacts` | Canonical (contacts) | contact_id, sales_id, full_name, email, email_secondary, phone, role, title, is_decision_maker, orbt_mode, strike_count | ADEQUATE — covers the need |
| `sales_interactions` | Canonical (log) | interaction_id, sales_id, contact_id, interaction_type, subject, body_snippet, source_message_id, source_thread_id, direction, meeting_number, outcome, orbt_mode, strike_count, occurred_at | ADEQUATE — covers the need |

---

## Gap Analysis

### Gap 1 — MISSING TABLE: `sales_state_errors`

**Why it's a gap:** CQRS pattern requires one canonical + one error table per sub-hub. `sales_state` is the spine; if a phase transition fails (e.g., advancing to `closed_won` without `approved_flag=1`), there is currently nowhere to log it. All other canonical tables have error tables. This one is missing.

**Classification:** Structural — CQRS violation. Not a column gap, a missing table.

---

### Gap 2 — MISSING TABLE: `sales_videos`

**Why it's a gap:** The CTB explicitly maps four gate videos (C-01 through C-04) to the sales process. Dave's original audit question specifically asked: "video tracking — which gate video was sent, watched?" The process sends a personalized video before each gate meeting. There is no table tracking: which video was sent, to which contact, when, whether it was watched (if tracking is available), and which gate it belongs to. Without this, there is no way to know if a stalled deal is waiting on a video being watched or a meeting being booked.

**Classification:** Missing table — required by the four-gate video-driven process.

---

### Gap 3 — MISSING TABLE: `sales_monte_carlo`

**Why it's a gap:** Gate 2 is explicitly "Education + Monte Carlo (Your Numbers)." The Monte Carlo simulation is complex structured output — two diverging paths (current fully-insured vs proposed self-insured), year-by-year projections, assumptions (trend rate, claims profile, stop loss attachment), and the resulting savings estimate. Cramming this into `sales_insurance.strategy_selected` (TEXT) is not viable and breaks the CQRS pattern. The simulation output needs its own table so it can be versioned, re-run, and audited. It is also the primary deliverable that gates Gate 2 → Gate 3 advancement.

**Classification:** Missing table — Gate 2 cannot be considered complete without it.

---

### Gap 4 — COLUMN GAPS: `sales_factfinder`

**Why it's a gap:** Gate 1 is "Bring the bill, I'll bring the math." The entire gate is about extracting the client's current insurance bill and context. The current table captures 4 columns (employer name, employee count, renewal month, prior broker) but misses the bill data entirely. Without the bill data, Gate 2 math cannot run.

**Missing columns:**
- `current_carrier` TEXT — who they're insured with now
- `current_plan_type` TEXT — fully insured / level funded / self insured (their current state)
- `current_monthly_premium` REAL — what they pay per month now (the bill)
- `current_annual_premium` REAL — annualized (derived, but useful to store explicitly)
- `employee_tier_count_ee` INTEGER — single employees enrolled
- `employee_tier_count_ee_spouse` INTEGER — employee + spouse
- `employee_tier_count_ee_child` INTEGER — employee + child(ren)
- `employee_tier_count_family` INTEGER — family tier
- `tier_cost_ee` REAL — monthly premium for single
- `tier_cost_ee_spouse` REAL — monthly premium for EE+SP
- `tier_cost_ee_child` REAL — monthly premium for EE+CH
- `tier_cost_family` REAL — monthly premium for family
- `employer_contribution_pct` REAL — what % the employer pays (vs employee)
- `renewal_date` TEXT — exact renewal date (not just month)
- `sic_code` TEXT — industry classification; affects stop loss underwriting
- `state` TEXT — state of domicile; affects regulatory requirements and network availability
- `bill_document_url` TEXT — link to the actual bill they brought (R2 or Drive URL)
- `notes` TEXT — Dave's freeform notes from the meeting

---

### Gap 5 — COLUMN GAPS: `sales_insurance`

**Why it's a gap:** Gate 2 outputs the insurance strategy selection AND the Monte Carlo results. Even with a separate `sales_monte_carlo` table for the simulation output, `sales_insurance` needs to capture the landscape facts that informed the strategy.

**Missing columns:**
- `hospital_waterfall_applicable` INTEGER DEFAULT 0 — can they use PPO→RBP→501R? (nonprofit hospital present?)
- `drug_waterfall_applicable` INTEGER DEFAULT 0 — high-dollar specialty drug exposure present?
- `stop_loss_tier` TEXT — specific/aggregate attachment point tier selected
- `tpa_candidates` TEXT — JSON array of TPA options Dave identified
- `pbm_candidates` TEXT — JSON array of PBM options
- `gate2_meeting_date` TEXT — when Gate 2 actually happened
- `strategy_rationale` TEXT — Dave's reasoning for the selected strategy
- `notes` TEXT — freeform

---

### Gap 6 — COLUMN GAPS: `sales_systems`

**Why it's a gap:** Gate 3 shows the client "what life looks like" — dashboards, implementation, the vendor ecosystem. The current table captures payroll, admin model, compliance owner but misses the vendor selections and implementation timeline which are the actual outputs of this gate.

**Missing columns:**
- `tpa_selected` TEXT — which TPA is being proposed
- `pbm_selected` TEXT — which PBM
- `ppo_network_selected` TEXT CHECK IN ('first_health', 'healthsmart', 'other') — per CTB, only two valid options
- `um_precert_vendor` TEXT — the UM vendor selected
- `specialty_drug_flag_vendor` TEXT — the drug monitoring vendor
- `stop_loss_carrier` TEXT — who is writing the stop loss
- `hr_platform` TEXT — their HR system (affects enrollment integration)
- `benefit_admin_platform` TEXT — their benefit admin (affects enrollment feed)
- `year1_implementation_start` TEXT — target date
- `year2_implementation_start` TEXT — target date
- `enrollment_method` TEXT — how Year 1 census enrollment will be handled
- `dashboards_shown` TEXT — JSON array of which dashboards were demoed (hr, cfo, underwriting, renewal, service_advisor)
- `gate3_meeting_date` TEXT
- `notes` TEXT

---

### Gap 7 — COLUMN GAPS: `sales_quotes`

**Why it's a gap:** Gate 4 is "The Dare" — specific numbers, competitive positioning, stop loss quotes, ancillary quotes. The current table has quote version, total cost, and approved flag. That is the barest skeleton.

**Missing columns:**
- `stop_loss_quote_json` TEXT — JSON blob of stop loss carrier quote details (specific/aggregate attachment, premium)
- `ancillary_quote_json` TEXT — JSON blob of ancillary coverage quotes (dental, vision, life, STD, LTD, EAP)
- `fixed_side_pepm_total` REAL — total PEPM across all fixed-side vendors
- `variable_side_monthly_estimate` REAL — estimated variable/claims cost
- `projected_annual_savings` REAL — vs their current premium
- `projected_year1_cost` REAL — Year 1 total
- `competitive_notes` TEXT — "Take it to every broker" — notes on competitive positioning
- `commission_equivalent_saved` REAL — the commission number that's baked into their current premium (the transparency point)
- `quote_presented_at` TEXT — when the quote was presented
- `decision_deadline` TEXT — when they need to decide (renewal pressure)
- `loss_reason` TEXT — if closed_lost, why
- `gate4_meeting_date` TEXT
- `notes` TEXT

---

### Gap 8 — COLUMN GAPS: `sales_state`

**Minor gaps.** The spine is mostly fine but missing a few columns that support downstream operations.

**Missing columns:**
- `current_carrier` TEXT — denormalized from factfinder for fast lookups (which carrier they're leaving)
- `dol_employee_count` INTEGER — count from DOL data at the time the deal was opened (outreach silo source; may differ from factfinder count)
- `gate1_completed_at` TEXT — timestamp when Gate 1 was marked complete
- `gate2_completed_at` TEXT
- `gate3_completed_at` TEXT
- `gate4_completed_at` TEXT
- `closed_at` TEXT — when the deal closed (won or lost)

---

## Summary Table

| Item | Type | Severity | Tables Affected |
|------|------|----------|-----------------|
| Missing `sales_state_errors` | Missing table | HIGH — CQRS violation | — |
| Missing `sales_videos` | Missing table | HIGH — core process asset tracking | — |
| Missing `sales_monte_carlo` | Missing table | HIGH — Gate 2 primary deliverable | — |
| `sales_factfinder` column gaps | Column additions | HIGH — Gate 1 is "the bill"; can't run Gate 2 without it | sales_factfinder |
| `sales_insurance` column gaps | Column additions | MEDIUM — strategy context and landscape flags | sales_insurance |
| `sales_systems` column gaps | Column additions | MEDIUM — vendor selections and implementation dates | sales_systems |
| `sales_quotes` column gaps | Column additions | HIGH — Gate 4 needs actual quote detail | sales_quotes |
| `sales_state` column gaps | Column additions | LOW — nice-to-have for pipeline reporting | sales_state |

---

## Migration File

See: `migrations/next_migration.sql`

---

## Document Control

| Field | Value |
|-------|-------|
| Audited | 2026-04-16 |
| Auditor | claude-code (Claude Sonnet 4.6) |
| Schema Source | Live D1 query — svg-d1-sales |
| Requirements Source | fleet/docs/SALES-SUB-HUB.md + fleet/content/INSURANCE-INFORMATICS-CTB.md |
| Status | AUDIT COMPLETE — migration written, pending Dave review |
| Migration | migrations/next_migration.sql |

-- ═══════════════════════════════════════════════════════════════
-- Process 400 — DOL Views
-- ═══════════════════════════════════════════════════════════════
-- 6 read-only views against existing DOL filing data in Neon.
-- Pure egress. No workers. No external tools. Just SQL.
-- Data: 432K form_5500 + 1.5M form_5500_sf + 625K schedule_a
-- ═══════════════════════════════════════════════════════════════

-- ┌─────────────────────────────────────────────────────────────┐
-- │ VIEW 1: Filing Status (Gate 3)                              │
-- │ Binary: does this company have DOL filings?                 │
-- └─────────────────────────────────────────────────────────────┘

CREATE OR REPLACE VIEW dol.v_dol_filing_status AS
SELECT
  f.sponsor_dfe_ein AS ein,
  f.company_unique_id,
  TRUE AS has_filing,
  MAX(f.form_year) AS latest_form_year,
  MAX(f.tot_active_partcp_cnt) AS latest_participants,
  COUNT(DISTINCT f.plan_name) AS plan_count,
  MAX(f.spons_dfe_mail_us_state) AS state
FROM dol.form_5500 f
WHERE f.sponsor_dfe_ein IS NOT NULL
  AND f.sponsor_dfe_ein != ''
GROUP BY f.sponsor_dfe_ein, f.company_unique_id;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ VIEW 2: Renewal Window (Gate 4)                             │
-- │ Companies approaching plan renewal within 90 days.          │
-- └─────────────────────────────────────────────────────────────┘

CREATE OR REPLACE VIEW dol.v_dol_renewal_window AS
WITH latest_filing AS (
  SELECT
    sponsor_dfe_ein,
    company_unique_id,
    form_plan_year_begin_date,
    form_year,
    sponsor_dfe_name,
    ROW_NUMBER() OVER (PARTITION BY sponsor_dfe_ein ORDER BY form_year DESC, form_plan_year_begin_date DESC) AS rn
  FROM dol.form_5500
  WHERE form_plan_year_begin_date IS NOT NULL
    AND sponsor_dfe_ein IS NOT NULL
)
SELECT
  lf.sponsor_dfe_ein AS ein,
  lf.company_unique_id,
  lf.sponsor_dfe_name AS company_name,
  lf.form_plan_year_begin_date AS plan_year_begin,
  (lf.form_plan_year_begin_date + INTERVAL '1 year') AS next_renewal_date,
  EXTRACT(DAY FROM (lf.form_plan_year_begin_date + INTERVAL '1 year') - CURRENT_DATE)::INT AS days_to_renewal,
  CASE
    WHEN (lf.form_plan_year_begin_date + INTERVAL '1 year') - CURRENT_DATE <= 90
     AND (lf.form_plan_year_begin_date + INTERVAL '1 year') >= CURRENT_DATE
    THEN TRUE
    ELSE FALSE
  END AS renewal_approaching
FROM latest_filing lf
WHERE lf.rn = 1;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ VIEW 3: Premium Pressure (Gate 5)                           │
-- │ YoY cost/participant change detection.                      │
-- └─────────────────────────────────────────────────────────────┘

CREATE OR REPLACE VIEW dol.v_dol_premium_pressure AS
WITH yearly AS (
  SELECT
    sponsor_dfe_ein,
    company_unique_id,
    form_year,
    sponsor_dfe_name,
    tot_active_partcp_cnt,
    ROW_NUMBER() OVER (PARTITION BY sponsor_dfe_ein, form_year ORDER BY ack_id DESC) AS rn
  FROM dol.form_5500
  WHERE sponsor_dfe_ein IS NOT NULL
    AND tot_active_partcp_cnt IS NOT NULL
    AND tot_active_partcp_cnt > 0
)
SELECT
  curr.sponsor_dfe_ein AS ein,
  curr.company_unique_id,
  curr.sponsor_dfe_name AS company_name,
  prev.form_year AS prior_year,
  curr.form_year AS current_year,
  prev.tot_active_partcp_cnt AS prior_participants,
  curr.tot_active_partcp_cnt AS current_participants,
  ROUND(
    ((curr.tot_active_partcp_cnt - prev.tot_active_partcp_cnt)::NUMERIC
     / NULLIF(prev.tot_active_partcp_cnt, 0)) * 100, 1
  ) AS pct_change,
  CASE
    WHEN curr.tot_active_partcp_cnt < prev.tot_active_partcp_cnt * 0.9 THEN TRUE
    ELSE FALSE
  END AS significant_decrease,
  CASE
    WHEN curr.tot_active_partcp_cnt > prev.tot_active_partcp_cnt * 1.1 THEN TRUE
    ELSE FALSE
  END AS significant_increase
FROM yearly curr
JOIN yearly prev
  ON curr.sponsor_dfe_ein = prev.sponsor_dfe_ein
  AND curr.form_year::INT = prev.form_year::INT + 1
  AND curr.rn = 1
  AND prev.rn = 1;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ VIEW 4: Market Comparison (PEPM Benchmarking)               │
-- │ Per-Employee-Per-Month cost by state and plan size.         │
-- └─────────────────────────────────────────────────────────────┘

CREATE OR REPLACE VIEW dol.v_dol_market_comparison AS
SELECT
  f.spons_dfe_mail_us_state AS state,
  sa.ins_carrier_name AS carrier_name,
  CASE
    WHEN f.tot_active_partcp_cnt < 50 THEN 'SMALL (< 50)'
    WHEN f.tot_active_partcp_cnt < 200 THEN 'MID (50-199)'
    WHEN f.tot_active_partcp_cnt < 1000 THEN 'LARGE (200-999)'
    ELSE 'JUMBO (1000+)'
  END AS size_band,
  COUNT(*) AS filing_count,
  ROUND(AVG(
    (COALESCE(sa.ins_broker_comm_tot_amt, 0) + COALESCE(sa.ins_broker_fees_tot_amt, 0))
    / NULLIF(sa.ins_prsn_covered_eoy_cnt, 0) / 12
  )::NUMERIC, 2) AS avg_pepm_broker_cost,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    (COALESCE(sa.ins_broker_comm_tot_amt, 0) + COALESCE(sa.ins_broker_fees_tot_amt, 0))
    / NULLIF(sa.ins_prsn_covered_eoy_cnt, 0) / 12
  )::NUMERIC, 2) AS median_pepm_broker_cost,
  f.form_year
FROM dol.form_5500 f
JOIN dol.schedule_a sa ON sa.ack_id = f.ack_id
WHERE f.spons_dfe_mail_us_state IS NOT NULL
  AND sa.ins_prsn_covered_eoy_cnt > 0
  AND f.tot_active_partcp_cnt > 0
GROUP BY f.spons_dfe_mail_us_state, sa.ins_carrier_name,
  CASE
    WHEN f.tot_active_partcp_cnt < 50 THEN 'SMALL (< 50)'
    WHEN f.tot_active_partcp_cnt < 200 THEN 'MID (50-199)'
    WHEN f.tot_active_partcp_cnt < 1000 THEN 'LARGE (200-999)'
    ELSE 'JUMBO (1000+)'
  END,
  f.form_year;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ VIEW 5: Carrier Changes                                     │
-- │ Detect carrier instability — company switched carriers YoY. │
-- └─────────────────────────────────────────────────────────────┘

CREATE OR REPLACE VIEW dol.v_dol_carrier_changes AS
WITH carrier_by_year AS (
  SELECT
    sa.sch_a_ein AS ein,
    f.company_unique_id,
    f.sponsor_dfe_name AS company_name,
    f.form_year,
    sa.ins_carrier_name,
    ROW_NUMBER() OVER (PARTITION BY sa.sch_a_ein, f.form_year ORDER BY sa.ins_prsn_covered_eoy_cnt DESC NULLS LAST) AS rn
  FROM dol.schedule_a sa
  JOIN dol.form_5500 f ON f.ack_id = sa.ack_id
  WHERE sa.sch_a_ein IS NOT NULL
    AND sa.ins_carrier_name IS NOT NULL
    AND sa.ins_carrier_name != ''
)
SELECT
  curr.ein,
  curr.company_unique_id,
  curr.company_name,
  prev.form_year AS prior_year,
  curr.form_year AS current_year,
  prev.ins_carrier_name AS prior_carrier,
  curr.ins_carrier_name AS current_carrier,
  CASE
    WHEN UPPER(TRIM(curr.ins_carrier_name)) != UPPER(TRIM(prev.ins_carrier_name)) THEN TRUE
    ELSE FALSE
  END AS carrier_changed
FROM carrier_by_year curr
JOIN carrier_by_year prev
  ON curr.ein = prev.ein
  AND curr.form_year::INT = prev.form_year::INT + 1
  AND curr.rn = 1
  AND prev.rn = 1;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ VIEW 6: Broker Changes                                      │
-- │ Detect broker churn — company switched brokers YoY.         │
-- └─────────────────────────────────────────────────────────────┘

CREATE OR REPLACE VIEW dol.v_dol_broker_changes AS
WITH broker_by_year AS (
  SELECT
    sa.sch_a_ein AS ein,
    f.company_unique_id,
    f.sponsor_dfe_name AS company_name,
    f.form_year,
    sap.ins_broker_name,
    ROW_NUMBER() OVER (PARTITION BY sa.sch_a_ein, f.form_year ORDER BY sap.row_order) AS rn
  FROM dol.schedule_a_part1 sap
  JOIN dol.schedule_a sa ON sa.ack_id = sap.ack_id AND sa.form_id = sap.form_id
  JOIN dol.form_5500 f ON f.ack_id = sa.ack_id
  WHERE sa.sch_a_ein IS NOT NULL
    AND sap.ins_broker_name IS NOT NULL
    AND sap.ins_broker_name != ''
)
SELECT
  curr.ein,
  curr.company_unique_id,
  curr.company_name,
  prev.form_year AS prior_year,
  curr.form_year AS current_year,
  prev.ins_broker_name AS prior_broker,
  curr.ins_broker_name AS current_broker,
  CASE
    WHEN UPPER(TRIM(curr.ins_broker_name)) != UPPER(TRIM(prev.ins_broker_name)) THEN TRUE
    ELSE FALSE
  END AS broker_changed
FROM broker_by_year curr
JOIN broker_by_year prev
  ON curr.ein = prev.ein
  AND curr.form_year::INT = prev.form_year::INT + 1
  AND curr.rn = 1
  AND prev.rn = 1;

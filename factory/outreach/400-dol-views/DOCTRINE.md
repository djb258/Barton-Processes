# DOCTRINE — Process 400 DOL Views
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-400-01 | All six views are read-only; no INSERT, UPDATE, or DELETE operation may touch any table in the `dol` schema during this process. | `src/001_dol_views.sql` (VIEW-only DDL), PROCESS.md §OSAM Forbidden Paths | §8 stop |
| D-400-02 | The EIN (Employer Identification Number) is the universal join key between the CT contact table and DOL filing tables; no join may use any other field as a substitute when EIN is available. | CLAUDE.md §Key Joins, PROCESS.md §DMJ Join | §8 stop |
| D-400-03 | The `ack_id` is the filing-level join key between `form_5500` and `schedule_a`; every view that accesses schedule data must join on `ack_id`, never on EIN alone. | CLAUDE.md §Key Joins, `src/001_dol_views.sql` v_dol_market_comparison | §8 stop |
| D-400-04 | All views must be defined under the `dol` schema (prefix `dol.v_dol_*`); no view may be created in the public schema or under any other schema prefix. | `src/001_dol_views.sql` schema declarations | §9b gauge |
| D-400-05 | Renewal window is defined as `form_plan_year_begin_date + INTERVAL '1 year'`; a company is flagged `renewal_approaching = TRUE` when `days_to_renewal <= 90`. | `src/001_dol_views.sql` v_dol_renewal_window CTE | §8 stop |
| D-400-06 | Premium pressure thresholds are: significant decrease = total_contributions_curr < 0.9 × total_contributions_prev; significant increase = total_contributions_curr > 1.1 × total_contributions_prev; no other multipliers may be used. | `src/001_dol_views.sql` v_dol_premium_pressure | §8 stop |
| D-400-07 | Carrier and broker change detection must use UPPER(TRIM()) normalization on both the current and prior year values before comparison; raw string equality without normalization is a logic error. | `src/001_dol_views.sql` v_dol_carrier_changes, v_dol_broker_changes | §8 stop |
| D-400-08 | YoY comparisons must select the single dominant carrier per EIN per year using ROW_NUMBER() OVER (PARTITION BY ein ORDER BY covered_lives DESC NULLS LAST); multi-row carrier records must be deduplicated this way before joining. | `src/001_dol_views.sql` v_dol_carrier_changes CTE carrier_by_year | §8 stop |
| D-400-09 | The `form_year` column is stored as TEXT in the source table; any arithmetic comparison across form years must cast to INT using `form_year::INT`; implicit cast or string comparison is forbidden. | CLAUDE.md §Known Issues (form_year TEXT vs INT), PROCESS.md §Known Issues | §9b gauge |
| D-400-10 | Gate 3 (filing status), Gate 4 (renewal window), and Gate 5 (premium pressure) in the downstream LCS process (PROC-100) depend exclusively on these views; no LCS gate logic may query the raw `form_5500` table directly when a DOL view already covers the signal. | heir.yaml `feeds: [600, 100]`, PROCESS.md §Dependencies | pre-flight |

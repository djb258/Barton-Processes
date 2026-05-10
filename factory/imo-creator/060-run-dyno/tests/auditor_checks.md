# Dyno Engine — Auditor Checks
## 11 structural tests run by Codex after every engine run
## These are CONSTANTS — same tests regardless of domain

---

| # | Check | What It Verifies | Pass Condition |
|---|-------|-----------------|----------------|
| 1 | Primitive validity | Every layer maps to exactly one primitive | primitive ∈ {Thing, Flow, Change} |
| 2 | C&V classification | Every layer has classification | cv ∈ {constant, variable, unidentified} |
| 3 | Minimum US runs | At least 3 US runs before UP handoff | completed_runs >= 3 |
| 4 | Back-propagation | New constants checked against all priors | θ' used, not stale θ |
| 5 | Sigma tracking | Direction computed across runs | sigma ∈ {tightening, flat, expanding} |
| 6 | Human tolerances | Tolerances set by human before UP | set_by = 'human' |
| 7 | R2 artifacts | Raw files pushed to R2 workbench | r2_artifact_path exists and files readable |
| 8 | D1 metadata | Rows written to dyno_runs/up_runs/up_stages | SELECT by run_id returns rows |
| 9 | LBB sequence | Read before work, write after | read_timestamp < work_timestamp < write_timestamp |
| 10 | Binary P | Equation produces 0 or 1 | p_result ∈ {0, 1} |
| 11 | Diagnostic vector | r(x) populated on P=0 | failed_comparators array non-empty when P=0 |

## How To Run

Codex receives the run_id after engine completes. It:
1. Pulls artifacts from R2 (dyno-runs/{side}/{slug}/{run_id}/)
2. Queries D1 for metadata rows
3. Runs each check above
4. Produces health report JSON: { checks: [{id, pass, detail}], all_pass: bool }
5. Writes health report to R2 + D1 (health_report column on dyno_run)

## Verdict

- all_pass = true → engine run VALID
- any check fails → engine run FLAGGED, detail shows which check failed
- Flagged runs are NOT discarded — they're marked for review

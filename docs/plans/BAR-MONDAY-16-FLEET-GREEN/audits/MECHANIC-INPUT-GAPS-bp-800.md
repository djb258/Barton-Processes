# MECHANIC-INPUT-GAPS — bp.800 Client Mint
**BAR:** BAR-MONDAY-16-FLEET-GREEN
**Audited:** 2026-05-08
**Auditor:** Sonnet (read-only baseline)
**Process path:** `factory/cl/800-client-mint/`

## Gate Scorecard

| Gate | ID | Result | Detail |
|------|----|--------|--------|
| UT template ≥v2.7.0 | G01 | PASS | |
| UT_CHECKLIST as TABLE | G02 | PASS | |
| 8 HEIR fields in outside.heir | G03 | FAIL | Multiple fields absent: `services`, `ctb_node`, `subject_id`, `acceptance_criteria`; `ctb_placement` is full path string instead of atomic value |
| Valid 4-state ORBT | G04 | PASS | |
| ctb_node anchored on barton-enterprises/... | G05 | PASS | |
| §9b ≥1 real value (no TBD/TBV-only) | G06 | FAIL | All 7 §9b rows are TBV — no live verification performed |
| Kill switch present | G07 | PASS | |
| §14 columns = date/version/author/action/scope | G08 | FAIL | §14 uses Date / What Was Done / LBB Record (systemic wrong columns) |
| workflow.yaml outside/inside distinct top-level maps | G09 | PASS | |
| workflow.yaml all 11 blocks top-level | G10 | PASS | |
| SHA256 parity | G11 | NEEDS_VERIFY | Cannot verify without script execution |
| paired-artifacts.yaml presence | G12 | PASS | Pre-confirmed |

## Gaps for Mechanic

### GAP-800-01 — G03: HEIR fields missing/malformed in outside.heir (MOST CRITICAL IN FLEET)
- **Fault (a):** `ctb_placement` contains a full path string instead of atomic value
- **Fault (b):** `ctb_node` field absent
- **Fault (c):** `subject_id` field absent
- **Fault (d):** `acceptance_criteria` field absent
- **Fault (e):** `services` field absent
- **Fix (a):** Set `ctb_placement: leaf`
- **Fix (b):** Add `ctb_node: barton-enterprises/svg-agency/cl/800-client-mint`
- **Fix (c):** Add `subject_id: svg-client-proc`
- **Fix (d):** Add `acceptance_criteria: "UT-local Workflow-Body; client mint gates green"`
- **Fix (e):** Add `services: [client-mint, cloudflare-d1, lbb, mission-control]` (verify against wrangler.toml)
- **Scope:** PROCESS-UT.md outside.heir block — highest G03 gap count in fleet

### GAP-800-02 — G06: §9b all-TBV
- **Fault:** All 7 §9b live verification rows have TBV in the Value column — no live verification performed
- **Fix:** Mechanic must run the verification commands or document the actual observed values; replace TBV with real observed values or explicit "NOT DEPLOYED" status
- **Scope:** PROCESS-UT.md §9b — all 7 TBV rows

### GAP-800-03 — G08: §14 SESSION LOG wrong columns
- **Fault:** §14 columns are Date / What Was Done / LBB Record — non-conformant
- **Fix:** Replace §14 header with `| Date | Version | Author | Action | Scope |` and reformat all existing rows
- **Scope:** PROCESS-UT.md §14

## Unchanged (no mechanic action needed)
G01, G02, G04, G05, G07, G09, G10, G12 — all PASS, no touch.

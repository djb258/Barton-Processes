# MECHANIC-INPUT-GAPS — bp.100 LCS Pipeline
**BAR:** BAR-MONDAY-16-FLEET-GREEN
**Audited:** 2026-05-08
**Auditor:** Sonnet (read-only baseline)
**Process path:** `factory/cl/100-lcs-pipeline/`

## Gate Scorecard

| Gate | ID | Result | Detail |
|------|----|--------|--------|
| UT template ≥v2.7.0 | G01 | PASS | |
| UT_CHECKLIST as TABLE | G02 | PASS | |
| 8 HEIR fields in outside.heir | G03 | PASS | |
| Valid 4-state ORBT | G04 | PASS | REPAIR — valid 4-state value |
| ctb_node anchored on barton-enterprises/... | G05 | PASS | |
| §9b ≥1 real value (no TBD/TBV-only) | G06 | PASS | |
| Kill switch present | G07 | PASS | |
| §14 columns = date/version/author/action/scope | G08 | FAIL | §14 uses Date / What Was Done / LBB Record (systemic wrong columns) |
| workflow.yaml outside/inside distinct top-level maps | G09 | PASS | |
| workflow.yaml all 11 blocks top-level | G10 | FAIL | CRITICAL: workflow content nested under `inside.orbt.workflow:` instead of as top-level blocks |
| SHA256 parity | G11 | NEEDS_VERIFY | Cannot verify without script execution |
| paired-artifacts.yaml presence | G12 | PASS | Pre-confirmed |

## Gaps for Mechanic

### GAP-100-01 — G10: workflow.yaml structure CRITICAL
- **Fault:** The workflow content (description, inputs, schedule, data, nodes, gates, lbb) is nested under `inside: → orbt: → workflow:` instead of being declared as syntactically independent top-level blocks
- **Fix:** Restructure workflow.yaml so that `description:`, `schedule:`, `data:`, `nodes:`, `gates:`, and `lbb:` are top-level keys alongside `outside:` and `inside:`. The `inside:` block should contain only `heir:` and `orbt:` (without `workflow:` nesting).
- **Scope:** workflow.yaml full restructure — highest priority gap in this process
- **Reference:** BS Law Y-junction; Book Law v1.4.0 Workflow-Body 11-block spec

### GAP-100-02 — G08: §14 SESSION LOG wrong columns
- **Fault:** §14 columns are Date / What Was Done / LBB Record — non-conformant
- **Fix:** Replace §14 header with `| Date | Version | Author | Action | Scope |` and reformat all existing rows
- **Scope:** PROCESS-UT.md §14

## Unchanged (no mechanic action needed)
G01, G02, G03, G04, G05, G06, G07, G09, G12 — all PASS, no touch.

# MECHANIC-INPUT-GAPS — bp.010 Seed D1
**BAR:** BAR-MONDAY-16-FLEET-GREEN
**Audited:** 2026-05-08
**Auditor:** Sonnet (read-only baseline)
**Process path:** `factory/outreach/010-seed-d1/`

## Gate Scorecard

| Gate | ID | Result | Detail |
|------|----|--------|--------|
| UT template ≥v2.7.0 | G01 | PASS | |
| UT_CHECKLIST as TABLE | G02 | FAIL | §2 uses bullet checkboxes, not TABLE format |
| 8 HEIR fields in outside.heir | G03 | FAIL | `services` field absent from PROCESS-UT.md outside.heir frontmatter |
| Valid 4-state ORBT | G04 | PASS | |
| ctb_node anchored on barton-enterprises/... | G05 | PASS | |
| §9b ≥1 real value (no TBD/TBV-only) | G06 | PASS | 12 D1 gauge rows with real values present |
| Kill switch present | G07 | PASS | |
| §14 columns = date/version/author/action/scope | G08 | FAIL | §14 uses Date / What Was Done / LBB Record (systemic wrong columns) |
| workflow.yaml outside/inside distinct top-level maps | G09 | PASS | |
| workflow.yaml all 11 blocks top-level | G10 | PASS | |
| SHA256 parity | G11 | NEEDS_VERIFY | Cannot verify without script execution |
| paired-artifacts.yaml presence | G12 | PASS | Pre-confirmed |

## Gaps for Mechanic

### GAP-010-01 — G02: UT_CHECKLIST format wrong
- **Fault:** §2 checklist rendered as bullet checkboxes instead of pipe-delimited TABLE
- **Fix:** Convert §2 checklist to TABLE with columns: Item | Requirement | Status
- **Scope:** PROCESS-UT.md §2 only

### GAP-010-02 — G03: `services` missing from outside.heir
- **Fault:** `services` field absent from the outside.heir frontmatter block in PROCESS-UT.md
- **Fix:** Add `services: [seed-d1, cloudflare-d1, lbb, mission-control]` (verify against wrangler.toml) to outside.heir
- **Scope:** PROCESS-UT.md outside.heir block

### GAP-010-03 — G08: §14 SESSION LOG wrong columns
- **Fault:** §14 columns are Date / What Was Done / LBB Record — non-conformant
- **Fix:** Replace §14 header with `| Date | Version | Author | Action | Scope |` and reformat all existing rows
- **Scope:** PROCESS-UT.md §14

## Unchanged (no mechanic action needed)
G01, G04, G05, G06, G07, G09, G10, G12 — all PASS, no touch.

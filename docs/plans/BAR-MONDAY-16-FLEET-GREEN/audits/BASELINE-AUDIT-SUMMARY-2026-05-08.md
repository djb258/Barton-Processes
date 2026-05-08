# BASELINE AUDIT SUMMARY — BAR-MONDAY-16-FLEET-GREEN
**Date:** 2026-05-08
**Auditor:** Sonnet (read-only baseline sweep)
**Scope:** 16 production processes — Barton-Processes fleet
**Target:** Atlas v2.3.0 conformance by 2026-05-11

---

## Complete Gate Matrix

| Process | G01 | G02 | G03 | G04 | G05 | G06 | G07 | G08 | G09 | G10 | G11 | G12 | FAILs |
|---------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-------|
| bp.010 | P | **F** | **F** | P | P | P | P | **F** | P | P | NV | P | 3 |
| bp.100 | P | P | P | P | P | P | P | **F** | P | **F** | NV | P | 2 |
| bp.200 | P | P | **F** | P | P | P | P | **F** | P | P | NV | P | 2 |
| bp.201 | P | P | **F** | P | P | **F** | P | **F** | P | P | NV | P | 3 |
| bp.202 | P | P | P | P | P | P | P | **F** | P | P | NV | P | 1 |
| bp.300 | P | P | **F** | P | P | P | P | **F** | P | P | NV | P | 2 |
| bp.301 | P | P | P | P | P | **F** | P | **F** | P | P | NV | P | 2 |
| bp.400 | P | P | **F** | P | P | P | P | **F** | P | P | NV | P | 2 |
| bp.500 | P | P | **F** | P | P | **F** | P | **F** | P | P | NV | P | 3 |
| bp.600 | P | P | **F** | P | P | **F** | P | **F** | P | P | NV | P | 3 |
| bp.700 | P | P | **F** | P | P | **F** | P | **F** | P | P | NV | P | 3 |
| bp.800 | P | P | **F** | P | P | **F** | P | **F** | P | P | NV | P | 3 |
| bp.810 | P | P | **F** | P | P | **F** | P | **F** | P | P | NV | P | 3 |
| bp.820 | P | P | P | P | P | P | P | **F** | P | P | NV | P | 1 |
| bp.830 | P | P | **F** | P | P | **F** | P | **F** | P | P | NV | P | 3 |
| bp.900 | P | P | P | P | P | **F** | P | **F** | P | P | NV | P | 2 |

**P** = PASS | **F** = FAIL | **NV** = NEEDS_VERIFY (G11 SHA256, requires script execution)

---

## Gate Failure Counts

| Gate | Failures | Type |
|------|----------|------|
| G01 — UT template ≥v2.7.0 | 0/16 | — |
| G02 — UT_CHECKLIST as TABLE | 1/16 | bp.010 only |
| G03 — 8 HEIR fields in outside.heir | 11/16 | Systemic — `services` missing in most; bp.800 worst (5 fields missing) |
| G04 — Valid 4-state ORBT | 0/16 | — |
| G05 — ctb_node anchored barton-enterprises/... | 0/16 | — |
| G06 — §9b ≥1 real value | 9/16 | Systemic — all-TBV §9b is the most common substantive gap |
| G07 — Kill switch present | 0/16 | — |
| G08 — §14 correct columns | 16/16 | **100% FAIL — fully systemic across entire fleet** |
| G09 — workflow.yaml outside/inside distinct | 0/16 | — |
| G10 — workflow.yaml all blocks top-level | 1/16 | bp.100 only — CRITICAL structural defect |
| G11 — SHA256 parity | 0/16 verified | NEEDS_VERIFY — script required |
| G12 — paired-artifacts.yaml presence | 0/16 | Pre-confirmed PASS all 16 |

---

## Systemic Findings (Fleet-Wide)

### SYSTEMIC-01 — G08: §14 SESSION LOG wrong columns (16/16)
**Every process in the fleet uses:** `| Date | What Was Done | LBB Record |`
**Required format:** `| Date | Version | Author | Action | Scope |`
**Recommendation:** Single mechanic dispatch with a literal find-replace template applied to all 16 files simultaneously. This is a pure format change — no content decisions required.

### SYSTEMIC-02 — G03: `services` absent from outside.heir (11/16)
Processes affected: bp.010, bp.200, bp.300, bp.400, bp.500, bp.600, bp.700, bp.800, bp.810, bp.830 + bp.800 (additional fields missing).
**Recommendation:** Each process needs its services list verified against wrangler.toml, then added to outside.heir. Cannot batch-template because service names differ per process.

### SYSTEMIC-03 — G06: §9b all-TBV (9/16)
Processes affected: bp.201 (5/6 TBV), bp.301 (7/7), bp.500 (all), bp.600 (4/5), bp.700 (8/8), bp.800 (7/7), bp.810 (7/7), bp.830 (8/8), bp.900 (6/7).
**Recommendation:** This requires live verification runs — cannot be resolved by doc editing alone. Mechanic must execute verification commands OR mark rows "NOT DEPLOYED" with explicit date.

---

## Isolated Findings (Process-Specific)

### ISOLATED-01 — G10: bp.100 workflow.yaml CRITICAL structural defect
workflow content nested under `inside.orbt.workflow:` instead of declared as top-level blocks. This violates BS Law Y-junction and Book Law Workflow-Body spec. Requires full workflow.yaml restructure.

### ISOLATED-02 — G02: bp.010 checklist format
§2 uses bullet checkboxes instead of TABLE format. One-process fix.

### ISOLATED-03 — G03: bp.800 missing 5 HEIR fields
bp.800 is the worst G03 offender: `services`, `ctb_node`, `subject_id`, `acceptance_criteria`, and malformed `ctb_placement`. All 5 require separate fixes.

### ISOLATED-04 — G03: bp.201 HEIR malformation
`ctb_placement` contains full path string; `ctb_node` absent.

---

## Clean Processes (Fewest Gaps)

| Process | Gap Count | Only Gap |
|---------|-----------|---------|
| bp.202 | 1 | G08 only |
| bp.820 | 1 | G08 only |
| bp.100 | 2 | G08 + G10 (CRITICAL) |
| bp.200 | 2 | G08 + G03 |
| bp.300 | 2 | G08 + G03 |
| bp.400 | 2 | G08 + G03 |
| bp.301 | 2 | G08 + G06 |
| bp.900 | 2 | G08 + G06 |

---

## Recommended Dispatch Order

1. **G08 batch** — Single Sonnet dispatch, all 16 §14 headers replaced. Pure format, no content decisions. Fastest path to 16/16 G08 PASS.
2. **G10 bp.100** — workflow.yaml restructure. One file, high severity. Sonnet dispatch.
3. **G03 services adds** — 11 processes, each needs wrangler.toml verification. Separate dispatch per process or grouped by wrangler access.
4. **G06 §9b verification** — Requires runtime access. Separate from doc-only fixes. Mechanic runs commands; records real values.
5. **G02 bp.010** — §2 checklist table conversion. Low effort, one file.
6. **G11 SHA256** — Script must be run after all doc edits are committed.

---

## Certification Status

**Pre-certification verdict: BLOCKED — 16/16 processes fail at least 1 gate.**
No process may be certified until G08 is resolved at minimum.
bp.202 and bp.820 are promotion-ready after G08 fix only.

---

*Audit performed 2026-05-08. Auditor: Sonnet (read-only). No mechanic edits made during this audit.*
*16 gap-delta files written to: `docs/plans/BAR-MONDAY-16-FLEET-GREEN/audits/`*

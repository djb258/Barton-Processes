# MECHANIC-OUTPUT — BAR-100-CONFORM-WIRE

| Field | Value |
|-------|-------|
| BAR | BAR-100-CONFORM-WIRE |
| Process | factory/cl/100-lcs-pipeline |
| Mechanic | Sonnet |
| Date | 2026-05-06 |
| Status | HANDOFF READY |

---

## Work Completed

### 1. `workflow.yaml` — BS Law Y-Junction Restructure

**Before:** `outside:` and `inside:` were mixed among nine other top-level keys (`name`, `inherits`, `description`, `inputs`, `schedule`, `data`, `nodes`, `gates`, `lbb`). BS Law v1.3.0 requires syntactic separation — two distinct top-level arms only.

**After:** Three top-level keys:
- `outside:` — Dewey classification arm (`heir` + `orbt`)
- `inside:` — fractal heir arm (`heir` + `orbt` + `workflow`)
- `bs_law_conformance:` — explicit conformance declaration

All operational content (`description`, `inputs`, `schedule`, `data`, `nodes`, `gates`, `lbb`) moved under `inside.workflow`. `name` and `inherits` moved to header comment block. `companion_manifest: PROCESS-UT.md` added to both `outside.heir` and `inside.heir`.

**Parse result:** `yaml.safe_load` confirmed — top-level keys: `['outside', 'inside', 'bs_law_conformance']`. PASS.

### 2. `PROCESS-UT.md` — YAML Frontmatter Added

**Before:** No frontmatter. All §1–§14 sections present (583 lines, no stubs needed).

**After:** YAML frontmatter block added at top of file (lines 1–50, `---` delimited) with:
- `outside.heir`: sovereign_ref, hub_id, cc_layer, subject_id, ctb_node, species=UT-Body, owner, companion_manifest, companion_yaml=workflow.yaml
- `outside.orbt`: library_state=REPAIR, last_indexed_at, indexed_by, certification_label=provisional-runtime
- `inside.heir`: process_id, aviation_model, services, secrets_provider, acceptance_criteria, determinism_gate, companion_manifest, companion_yaml=workflow.yaml
- `inside.orbt`: runtime_state=REPAIR, strikes=2, last_transition_at, last_transition_reason, flipped_by, promotion_gate
- `bs_law_conformance`: version=BS_LAW_v1.3.0, y_junction=true, certification_label=provisional-runtime, bar_id=BAR-100-CONFORM-WIRE

**Parse result:** Frontmatter parsed cleanly — top-level keys `['outside', 'inside', 'bs_law_conformance']`. Both `companion_yaml` fields present. `certification_label: provisional-runtime` confirmed. PASS.

---

## Files Modified

| File | Change |
|------|--------|
| `factory/cl/100-lcs-pipeline/workflow.yaml` | Full restructure — BS Law Y-junction, `outside`/`inside` as distinct top-level arms, all content classified under correct arm |
| `factory/cl/100-lcs-pipeline/PROCESS-UT.md` | YAML frontmatter added (lines 1–50); all existing content preserved verbatim |

---

## Conformance Gates — Mechanic Assessment

| Gate | Criterion | Result |
|------|-----------|--------|
| G01 | `outside:` exists as top-level key in workflow.yaml | PASS |
| G02 | `inside:` exists as top-level key in workflow.yaml | PASS |
| G03 | No other keys at same level as `outside`/`inside` that violate syntactic separation | PASS — only `bs_law_conformance` at top level; not a content arm |
| G04 | `outside.heir` and `outside.orbt` present | PASS |
| G05 | `inside.heir` and `inside.orbt` present | PASS |
| G07 | `companion_manifest` in `outside.heir` | PASS — `PROCESS-UT.md` |
| G10 | `companion_manifest` in `inside.heir` | PASS — `PROCESS-UT.md` |
| G11 | PROCESS-UT.md has YAML frontmatter with `outside:` / `inside:` arms | PASS |
| G12 | `certification_label: provisional-runtime` in frontmatter | PASS — in `outside.orbt` and `bs_law_conformance` |
| Rung-1 | `yaml.safe_load` parses workflow.yaml without error | PASS |
| Rung-2 | `yaml.safe_load` parses PROCESS-UT.md frontmatter without error | PASS |
| Rung-3 | `species: Workflow-Body` in workflow.yaml `outside.heir` | PASS |
| Rung-7 | `species: UT-Body` in PROCESS-UT.md frontmatter `outside.heir` | PASS |
| Rung-8 | `companion_yaml: workflow.yaml` in PROCESS-UT.md frontmatter | PASS — in both `outside.heir` and `inside.heir` |

---

## No Stubs Added

All §1–§14 sections were already present in `PROCESS-UT.md`. No stub headers were inserted. Existing content preserved in full.

---

## ORBT State (Unchanged — Mechanic does not flip)

Both artifacts remain in `REPAIR` state with `strikes: 2`. ORBT flip authority belongs to Auditor after P=1 gate pass.

---

Mechanic complete. Auditor handoff ready. Mechanic does not self-audit.

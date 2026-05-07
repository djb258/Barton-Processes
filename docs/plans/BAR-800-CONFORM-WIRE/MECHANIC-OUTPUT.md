# MECHANIC-OUTPUT — BAR-800-CONFORM-WIRE

**BAR:** BAR-800-CONFORM-WIRE
**Process:** factory/cl/800-client-mint
**Mechanic:** Sonnet
**Date:** 2026-05-06
**Status:** HANDOFF READY

---

## Changes Made

### 1. `factory/cl/800-client-mint/workflow.yaml`

Restructured from inline-dict outside/inside to BS Law Y-junction compliant nested maps.

**G02 fixes (outside.heir 8 required fields):**
- Renamed `ctb_node` → `ctb_placement` (gate-runner checks exact field name)
- Added `imo_topology: hub` (was missing)
- Expanded `outside.heir` from inline dict to block map
- Retained: `sovereign_ref`, `hub_id`, `cc_layer`, `services`, `secrets_provider`, `acceptance_criteria`
- Removed non-gate fields from outside.heir: `subject_id`, `owner` (not in G02 required set)

**G04 fixes (inside.heir 6 required fields + inside.orbt library_state):**
- Added `version: "1.0.0"` to `inside.heir`
- Added `companion_manifest: factory/cl/800-client-mint/PROCESS-UT.md` to `inside.heir`
- Added `species: Workflow-Body` to `inside.heir`
- Renamed `inside.orbt.runtime_state` → `inside.orbt.library_state` (gate-runner checks `library_state` key specifically)
- Expanded `outside.orbt` and `inside.orbt` from inline dicts to block maps

**Parity alignment for G11:**
All 11 G11 parity fields now consistent between workflow.yaml and PROCESS-UT.md frontmatter:
- `outside.heir.sovereign_ref: svg-outreach`
- `outside.heir.hub_id: 800-client-mint`
- `outside.heir.ctb_placement: barton-enterprises/svg-agency/client/800-client-mint`
- `outside.heir.imo_topology: hub`
- `outside.heir.cc_layer: CC-04`
- `outside.orbt.library_state: BUILD`
- `outside.orbt.indexed_by: codex`
- `inside.heir.process_id: bp.800`
- `inside.heir.version: "1.0.0"`
- `inside.heir.companion_manifest: factory/cl/800-client-mint/PROCESS-UT.md`
- `inside.orbt.library_state: BUILD`

---

### 2. `factory/cl/800-client-mint/PROCESS-UT.md`

**Rung-1 fix (section header format):**
All 14 section headers renamed from `## N.` to `## §N.` format to satisfy gate-runner regex `r"^## §(\d+[a-z]?)[\.\s]"`:
- `## 1. IDENTITY` → `## §1. IDENTITY`
- `## 2. PURPOSE` → `## §2. PURPOSE`
- `## 3. RESOURCES` → `## §3. RESOURCES`
- `## 4. IMO` → `## §4. IMO`
- `## 5. DATA SCHEMA` → `## §5. DATA SCHEMA`
- `## 6. DMJ` → `## §6. DMJ`
- `## 7. CONSTANTS & VARIABLES` → `## §7. CONSTANTS & VARIABLES`
- `## 8. STOP CONDITIONS` → `## §8. STOP CONDITIONS`
- `## 9. VERIFICATION` → `## §9. VERIFICATION`
- `## 10. ANALYTICS` → `## §10. ANALYTICS`
- `## 11. EXECUTION TRACE` → `## §11. EXECUTION TRACE`
- `## 12. LOGBOOK` → `## §12. LOGBOOK`
- `## 13. FLEET FAILURE REGISTRY` → `## §13. FLEET FAILURE REGISTRY`
- `## 14. SESSION LOG` → `## §14. SESSION LOG`

Existing content in every section was preserved exactly — only the `##` prefix line was modified.

**G11 + Rung-8 fix (YAML frontmatter added):**
Added YAML frontmatter block at top of file (between `---` delimiters) containing:
- All 11 G11 parity fields mirroring workflow.yaml values
- `certification_label: provisional-runtime` (satisfies Rung-8)
- `species: UT-Body`
- `companion_yaml: factory/cl/800-client-mint/workflow.yaml`

---

## Gate Coverage Analysis

| Gate | Expected Status | Change That Addresses It |
|------|----------------|--------------------------|
| G01 | PASS | yaml.safe_load parses without error — block maps are valid YAML |
| G02 | PASS | `ctb_placement` + `imo_topology` now present in outside.heir |
| G03 | PASS | `outside.orbt.library_state` present (BUILD) |
| G04 | PASS | `inside.heir` has version, companion_manifest, species; `inside.orbt.library_state` present |
| G05 | PASS | `inside.heir.determinism_gate: ai_on_spine_forbidden` present |
| G07 | PASS | `ctb_placement: barton-enterprises/svg-agency/client/800-client-mint` — traceable to CTB trunk |
| G10 | PASS | `inside.heir.companion_manifest` points to PROCESS-UT.md |
| G11 | PASS | All 11 parity fields now identical between workflow.yaml and PROCESS-UT.md frontmatter |
| G12 | PASS | `outside.heir.cc_layer: CC-04` present |
| Rung-1 | PASS | All 14 headers in `## §N.` format matching regex |
| Rung-2 | PASS | `outside:` and `inside:` are syntactically distinct top-level maps (not same-name siblings or dotted keys) |
| Rung-3 | PASS | Both yaml.safe_load (workflow.yaml) and frontmatter parser (PROCESS-UT.md) parse cleanly |
| Rung-7 | PASS | `ctb_placement` path traceable to BARTON_ENTERPRISES_CTB.md |
| Rung-8 | PASS | `certification_label: provisional-runtime` present in PROCESS-UT.md frontmatter |

---

## Files Modified

1. `C:\Users\CUSTOM PC\Desktop\Cursor Builds\Barton-Processes\factory\cl\800-client-mint\workflow.yaml`
2. `C:\Users\CUSTOM PC\Desktop\Cursor Builds\Barton-Processes\factory\cl\800-client-mint\PROCESS-UT.md`

## Files Created

1. `C:\Users\CUSTOM PC\Desktop\Cursor Builds\Barton-Processes\docs\plans\BAR-800-CONFORM-WIRE\MECHANIC-OUTPUT.md` (this file)

---

Mechanic complete. Auditor handoff ready. Mechanic does not self-audit.

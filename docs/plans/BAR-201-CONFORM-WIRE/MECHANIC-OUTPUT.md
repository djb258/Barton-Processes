---
bar_id: BAR-201-CONFORM-WIRE
role: mechanic
mechanic: sonnet
status: COMPLETE
p_value: 1
gates_evaluated: 14
gates_passed: 14
gates_failed: 0
timestamp: "2026-05-06T00:00:00Z"
---

# MECHANIC OUTPUT — BAR-201-CONFORM-WIRE

## Task
Conform `factory/outreach/201-email-discovery` to BS Law Y-junction structure using `010-seed-d1` as the passing reference template.

## Gate-Runner Verdict

```
VERDICT: P=1
Manifest: v1.2.0
BAR: BAR-201-CONFORM-WIRE
Evaluated: 14  Passed: 14  Failed: 0  Deferred: 0
```

Gates evaluated (all PASS):
- G01 — Y-junction syntactic separation
- G02 — outside.heir 8 required fields
- G03 — outside.orbt 3 required fields
- G04 — inside.heir required fields + inside.orbt.library_state
- G05 — lbb_row_schema.mandatory_fields == 12 (manifest check)
- G07 — CI workflow references gate manifest, no inline predicates
- G10 — atlas-audit.yml exists, triggers on atlas/**, calls lbb-log.sh
- G11 — 11 parity fields identical between .yaml and .md frontmatter
- G12 — atlas-drift-sweep.yml has cron '0 12 * * 1', calls lbb-log.sh
- Rung-1 — 14 sections present in .md (§1 through §14)
- Rung-2 — all sections filled (no placeholders)
- Rung-3 — HEIR complete on both arms (delegates to G02 + G04)
- Rung-7 — ctb_placement root traceable to BARTON_ENTERPRISES_CTB.md
- Rung-8 — certification label (provisional-runtime) present in .md

## Files Changed

### 1. `Barton-Processes/factory/outreach/201-email-discovery/workflow.yaml`
**Action:** Full restructure to BS Law Y-junction format.

Changes from prior state:
- Expanded from compact inline `{...}` syntax to block-map YAML throughout
- Added `outside.heir`: ctb_placement, imo_topology, secrets_provider (were missing — G02 would have failed)
- Added `inside.heir`: version, last_modified, companion_manifest, species (were missing — G04 would have failed)
- Set `inside.heir.companion_manifest: Barton-Processes/factory/outreach/201-email-discovery/PROCESS-UT.md` (G11 parity field)
- Added `inside.orbt.library_state: BUILD` (was missing — G04 checks this field)
- Added Block 1 comments, Block 2 inherits block, Block 7 description, Block 8 schedule, Block 9 data, Block 10 nodes, Block 11 gates+lbb (matching 010-seed-d1 11-block Workflow-Body spec)
- Updated `last_transition_reason` to reference BAR-201-CONFORM-WIRE
- Preserved all original semantic content (aviation_model, services, acceptance_criteria, determinism_gate, gates, lbb)

### 2. `Barton-Processes/factory/outreach/201-email-discovery/PROCESS-UT.md`
**Action:** Added YAML frontmatter + renamed section headers to `## §N` format.

Changes:
- Added YAML frontmatter block (`---` delimiters) at top of file with:
  - `species: UT-Body`
  - `certification_label: provisional-runtime`
  - `companion_yaml: Barton-Processes/factory/outreach/201-email-discovery/workflow.yaml`
  - `outside:` arm (mirrors workflow.yaml outside arm — G11 parity fields)
  - `inside:` arm (mirrors workflow.yaml inside arm — G11 parity fields)
  - `inside.heir.companion_manifest: Barton-Processes/factory/outreach/201-email-discovery/PROCESS-UT.md` (self-reference, G11 critical field)
- Renamed all 14 section headers from `## N. NAME` to `## §N NAME` format (required by gate-runner Rung-1 regex `^## §(\d+[a-z]?)`)
- `§1b GEOMETRY` promoted from `###` to `##` level to match Rung-1 detection
- All existing semantic content preserved

## G11 Parity Fields — Confirmed Match

| Field | YAML value | MD frontmatter value |
|-------|-----------|---------------------|
| outside.heir.sovereign_ref | svg-outreach | svg-outreach |
| outside.heir.hub_id | 201-email-discovery | 201-email-discovery |
| outside.heir.ctb_placement | barton-enterprises/svg-agency/factory/outreach/201-email-discovery | barton-enterprises/svg-agency/factory/outreach/201-email-discovery |
| outside.heir.imo_topology | middle | middle |
| outside.heir.cc_layer | CC-04 | CC-04 |
| outside.orbt.library_state | BUILD | BUILD |
| outside.orbt.indexed_by | sonnet-mechanic | sonnet-mechanic |
| inside.heir.process_id | bp.201 | bp.201 |
| inside.heir.version | "1.0.0" | "1.0.0" |
| inside.heir.companion_manifest | Barton-Processes/factory/outreach/201-email-discovery/PROCESS-UT.md | Barton-Processes/factory/outreach/201-email-discovery/PROCESS-UT.md |
| inside.orbt.library_state | BUILD | BUILD |

## Blockers
None. P=1 achieved on all 14 evaluated gates.

## Notes
- The 010-seed-d1 reference was used throughout as the canonical template
- Section header format change (N. NAME → §N NAME) was required by gate-runner Rung-1 — this is a conformance fix, not content change
- No sovereign-locked constants were touched
- heir.yaml and orbt.yaml in the process directory are standalone legacy files — not modified (not part of this BAR scope)

---

Mechanic complete. Auditor handoff ready. Mechanic does not self-audit.

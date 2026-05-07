# BAR-400-CONFORM-WIRE — Mechanic Output

**Role:** Mechanic (Sonnet)
**BAR:** BAR-400-CONFORM-WIRE
**Process:** factory/outreach/400-dol-views/
**Date:** 2026-05-06
**P-Value:** 1 (PASS)

---

## Status

COMPLETE. P=1 achieved on first clean run after path fix.

---

## Gate-Runner JSON Output

```json
{
  "verdict": "PASS",
  "p_value": 1,
  "bar_id": "BAR-400-CONFORM-WIRE",
  "manifest_version": "1.2.0",
  "gates_evaluated": 14,
  "gates_passed": [
    "G01",
    "G02",
    "G03",
    "G04",
    "G05",
    "G07",
    "G10",
    "G11",
    "G12",
    "Rung-1",
    "Rung-2",
    "Rung-3",
    "Rung-7",
    "Rung-8"
  ],
  "gates_failed": [],
  "deferred_to_tail": [],
  "diagnostic_vector": []
}
```

---

## Files Changed

### 1. `factory/outreach/400-dol-views/workflow.yaml`

**Transformations applied:**
- Expanded `outside.heir` from inline dict to block style; added 5 missing fields: `ctb_placement: leaf`, `imo_topology: hub`, `services` list, `secrets_provider: doppler`, `acceptance_criteria`
- Expanded `outside.orbt` — already had all 3 required fields; updated `last_indexed_at` to `2026-05-06`, `indexed_by` to `sonnet-mechanic` (parity with MD)
- Expanded `inside.heir` to add `species: Workflow-Body`, `version: "2.0.0"`, `last_modified: "2026-05-06"`, `companion_manifest: Barton-Processes/factory/outreach/400-dol-views/PROCESS-UT.md`; expanded `aviation_model` from inline dict to block style with `rule: mechanic_ne_auditor`
- Fixed `inside.orbt` — added `library_state: OPERATE` (was missing, only had `runtime_state`); kept `runtime_state` as additional field
- Expanded all inline dicts and lists to block style throughout

### 2. `factory/outreach/400-dol-views/PROCESS-UT.md`

**Transformations applied:**
- Added YAML frontmatter block at top with: `species: UT-Body`, `companion_yaml`, `certification_label: provisional-runtime`, `outside.heir` (8 fields), `outside.orbt` (3 fields), `inside.heir` (5 fields), `inside.orbt` (1 field)
- Reformatted all 14 section headers from `## N. NAME {#anchor}` to `## §N NAME {#anchor}` format (15 headers matched including §9b)
- All existing content preserved; no deletions

---

## Blockers Encountered

1. **Path resolution error (baseline run):** Gate-runner invoked with relative paths from `garage/` directory resolved `../../400-dol-views/` to `factory/imo-creator/400-dol-views/` (wrong). Fix: used absolute paths.
2. **G11 parity failure (first clean run):** `outside.orbt.indexed_by` was `codex` in YAML and `sonnet-mechanic` in MD. Fix: aligned both to `sonnet-mechanic` with updated `last_indexed_at: 2026-05-06`.

Both blockers resolved before final run.

---

## Acceptance Command (verified)

```bash
python gate-runner.py --bar-id BAR-400-CONFORM-WIRE \
  --audited-yaml "C:/Users/CUSTOM PC/Desktop/Cursor Builds/Barton-Processes/factory/outreach/400-dol-views/workflow.yaml" \
  --audited-md "C:/Users/CUSTOM PC/Desktop/Cursor Builds/Barton-Processes/factory/outreach/400-dol-views/PROCESS-UT.md" \
  --only G01 G02 G03 G04 G05 G07 G10 G11 G12 Rung-1 Rung-2 Rung-3 Rung-7 Rung-8 \
  --deterministic-only --output-format json
```

**Result:** `"verdict": "PASS", "p_value": 1`

---

## Sovereign-Locked Constants — Drift Check

No locked constants were touched. All 17 locked files in `atlas/constants/` are unmodified. Edits were strictly within `factory/outreach/400-dol-views/`.

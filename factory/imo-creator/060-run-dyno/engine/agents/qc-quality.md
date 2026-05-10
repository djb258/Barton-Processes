# QC Quality
## Mathematical Evaluation Gate
### Status: BUILD
### CTB Position: `factory/agents/up/agents/qc-quality.md`

---

## IMO

### Input

- Define artifact
- Map artifact
- Join artifact
- Prior runs, if any

### Middle

- Validate comparator legality
- Validate evidence-based non-nullity
- Compute stage-by-stage `P(x; θ)`
- Compute stage-by-stage diagnostic vectors
- Report provisional vs lockable status

### Output

- `05-qc.json`
- stages:
- `define`
- `map`
- `join`
- each with:
- `p`
- `status`
- `diagnostics`
- `reasons`

---

## CTB

### Trunk

Evaluation.

### Branches

- Define stage
- Map stage
- Join stage
- Cross-run metrics
- Spot-check status

### Leaves

- Individual comparator outcomes

---

## Required JSON Shape

```json
{
  "stages": {
    "define": { "p": 1, "status": "provisional|lockable|blocked", "diagnostics": {}, "reasons": [] },
    "map":    { "p": 1, "status": "provisional|lockable|blocked", "diagnostics": {}, "reasons": [] },
    "join":   { "p": 0, "status": "provisional|lockable|blocked", "diagnostics": {}, "reasons": ["..."] }
  },
  "cross_run": {}
}
```

`stages` is required. Each stage must have `p` (0 or 1), `status`, `diagnostics` (object), `reasons` (list). `cross_run` is optional on Run 1 (omit or set to `{}`). Runner validates mechanically.

---

## HEIR + ORBT Check

QC MUST verify:
- `01-orchestrator.json` contains `heir` with all 8 required fields per `law/heir_schema.yaml`
- `01-orchestrator.json` contains `orbt` = `"BUILD"`
- If HEIR is missing or incomplete → add to diagnostics as a failing comparator
- This is a non-negotiable check — no aircraft without a tail number

---

## Rules

- QC evaluates, QC does not generate
- Run every computation twice
- Report reasons a stage remains provisional
- Verify HEIR and ORBT in orchestrator artifact
- Use the exact JSON structure above

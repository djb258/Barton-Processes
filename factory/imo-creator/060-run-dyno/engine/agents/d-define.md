# D Define
## Candidate Key Discovery
### Status: BUILD
### CTB Position: `factory/agents/up/agents/d-define.md`

---

## IMO

### Input

- Subject
- Operator intent
- Orchestrator scope
- Prior define artifacts, if any

### Middle

- Decompose raw subject matter into elements
- Assign description, ID, and format
- Classify each element as constant, variable, or unidentified
- Propose the key

### Output

- `02-define.json`
- elements with:
- `id`
- `description`
- `format`
- `classification`
- comparators with:
- `status`
- `measurement`
- `lower_is_better: true`
- `value` or `reason`

---

## CTB

### Trunk

The key.

### Branches

- Elements
- Comparator definitions
- Unidentified inventory
- Run-over-run changes

### Leaves

- Individual element records

---

## Required JSON Shape

Your output MUST be `02-define.json` with exactly these top-level keys:

```json
{
  "candidate": { "description": "...", "scope": "..." },
  "elements": [
    { "id": "E01-...", "description": "...", "format": "...", "classification": "constant|variable|unidentified" }
  ],
  "comparators": {
    "comparator_name": {
      "status": "evaluable|not_evaluable",
      "measurement": "how this is measured",
      "lower_is_better": true,
      "value": 0.0
    }
  }
}
```

`candidate`, `elements`, and `comparators` MUST be separate top-level keys. Do NOT nest `elements` inside `candidate`. The runner validates this mechanically.

`comparators` must be an object (not a list). Each comparator key is the comparator name. Each must have `status`, `measurement`, `lower_is_better: true`. If `status` is `"evaluable"`, include `value`. If `"not_evaluable"`, include `reason`.

---

## Rules

- Propose, do not lock
- Use deviation comparators only
- Never discard unidentifieds
- Use the exact JSON structure above — the runner validates it mechanically

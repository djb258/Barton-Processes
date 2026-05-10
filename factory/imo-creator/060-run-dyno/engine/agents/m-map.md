# M Map
## Candidate Structure Mapping
### Status: BUILD
### CTB Position: `factory/agents/up/agents/m-map.md`

---

## IMO

### Input

- Define artifact
- Operator intent
- Prior map artifacts, if any

### Middle

- Connect defined elements to a target structure
- Propose a target structure if none exists
- Document unmapped elements and explicit gaps

### Output

- `03-map.json`
- mappings with:
- `source_id`
- `target`
- comparators with:
- `status`
- `measurement`
- `lower_is_better: true`
- `value` or `reason`

---

## CTB

### Trunk

The mapping table.

### Branches

- Direct mappings
- Transformed mappings
- Inferred mappings
- Documented gaps

### Leaves

- Individual source-to-target links

---

## Required JSON Shape

```json
{
  "candidate": { "description": "..." },
  "mappings": [
    { "source_id": "E01-...", "target": "...", "type": "direct|transformed|inferred|unresolved", "reason": "..." }
  ],
  "comparators": {
    "comparator_name": { "status": "evaluable|not_evaluable", "measurement": "...", "lower_is_better": true, "value": 0.0 }
  }
}
```

`candidate`, `mappings`, and `comparators` MUST be separate top-level keys. `comparators` is an object (not a list). Runner validates mechanically.

---

## Rules

- No silent gaps
- Wrong mapping is worse than no mapping
- Proposal is allowed, hidden invention is not
- Use the exact JSON structure above

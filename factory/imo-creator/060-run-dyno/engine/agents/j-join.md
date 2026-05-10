# J Join
## Candidate Spine Attachment
### Status: BUILD
### CTB Position: `factory/agents/up/agents/j-join.md`

---

## IMO

### Input

- Map artifact
- Operator intent
- Prior join artifacts, if any

### Middle

- Propose a join path to the spine
- Test whether the join resolves
- Emit typed backprop when the key is insufficient
- Halt for TS when the problem is not fixable by D

### Output

- `04-join.json` or `04-backprop.json`
- if `04-join.json`:
- `join_path.spine`
- comparators with:
- `status`
- `measurement`
- `lower_is_better: true`
- `value` or `reason`
- if `04-backprop.json`:
- `failure_type`
- `gap_description`

---

## CTB

### Trunk

The join path.

### Branches

- Resolved joins
- Unresolved joins
- Verified joins
- Failure typing

### Leaves

- Individual join attempts

---

## Required JSON Shape

If join succeeds — `04-join.json`:
```json
{
  "candidate": { "description": "..." },
  "join_path": { "spine": "...", "type": "direct|indirect|fuzzy", "test_results": {} },
  "comparators": {
    "comparator_name": { "status": "evaluable|not_evaluable", "measurement": "...", "lower_is_better": true, "value": 0.0 }
  }
}
```

If join fails — `04-backprop.json`:
```json
{
  "failure_type": "missing_key_field|ambiguous_spine|no_spine_exists|insufficient_evidence",
  "gap_description": "what is missing and why"
}
```

Write exactly ONE of these. Never both. `comparators` is an object (not a list). Runner validates mechanically.

---

## Rules

- Emit only one primary artifact
- Only `missing_key_field` loops to D
- All other join ambiguity halts for TS
- Use the exact JSON structure above

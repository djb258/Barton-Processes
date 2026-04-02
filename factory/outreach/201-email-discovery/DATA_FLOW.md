# DATA_FLOW.md — Process 201: Find Email

## Read Path
```
slot_workbench (D1 svg-d1-outreach-ops)
  WHERE has_name = 1 AND has_email = 0
  SELECT: slot_id, person_first_name, person_last_name, company_domain,
          domain, email_pattern, hunter_email, hunter_confidence,
          has_name, has_linkedin, readiness_tier
```

## Gate Chain
```
slot_workbench ──READ──> Gate A (pattern generate)
                         │ HIT ──> write
                         │ MISS ──v
                         Gate B (hunter promote, confidence >= 80)
                         │ HIT ──> write
                         │ MISS ──v
                         Gate C (Startpage search + parse)
                         │ HIT ──> write
                         │ MISS ──> log MISS, no write
```

## Write Path
```
UPDATE slot_workbench
  SET person_email      = {discovered_email}
      has_email         = 1
      email_found_at    = {UTC timestamp}
      readiness_tier    = {recalculated: FULL | REACHABLE | PATTERN_READY | EMPTY}
  WHERE slot_id = {slot_id}
```

## Readiness Tier Recalculation
| has_name | has_email | has_linkedin | Tier          |
|----------|-----------|--------------|---------------|
| 1        | 1         | 1            | FULL          |
| 1        | 1         | 0            | REACHABLE     |
| 1        | 0         | 1            | REACHABLE     |
| 1        | 0         | 0            | PATTERN_READY |
| 0        | *         | *            | EMPTY         |

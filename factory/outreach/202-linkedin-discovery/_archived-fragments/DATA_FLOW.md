> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# DATA_FLOW.md — Process 202: Find LinkedIn

## Read Path
```
slot_workbench (D1 svg-d1-outreach-ops)
  WHERE has_name = 1 AND has_linkedin = 0
  SELECT: slot_id, person_first_name, person_last_name, company_name,
          city, domain, company_domain, recon_linkedin_people,
          hunter_linkedin, has_name, has_email, has_linkedin,
          readiness_tier
```

## Gate Chain
```
slot_workbench ──READ──> Gate A (recon_linkedin_people name match)
                         │ HIT ──> write
                         │ MISS ──v
                         Gate B (hunter_linkedin promote)
                         │ HIT ──> write
                         │ MISS ──v
                         Gate C (Startpage search "{first} {last} {company} linkedin")
                         │ HIT ──> write
                         │ MISS ──> log MISS, no write
```

## Write Path
```
UPDATE slot_workbench
  SET person_linkedin   = {discovered_url}
      has_linkedin      = 1
      linkedin_found_at = {UTC timestamp}
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

# PROCESS: Email Discovery
## Finds a verified business email for a person given their name and company domain
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-201 |
| Name | Email Discovery |
| Business Silo | svg-agency |
| CTB Position | factory/outreach/201-email-discovery |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | — |
| BAR Reference | BAR-191 |
| Deployed URL | not deployed |
| Cron | Called conditionally by Process 200 orchestrator |
| Runtime | CF Worker |

---

## 2. WHY THIS EXISTS

Without a verified email, you can't reach the person through Mailgun. A name in a slot without a verified email is half a contact. This process turns a name + company domain into a deliverable email address, verified through Million Verifier before it's written.

Called conditionally — only runs when Process 200 has filled a slot but the person has no verified email. If another process (201 or 202) already found the email, this is skipped. No wasted spend.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Process 200 fills a slot. Orchestrator checks: does this person have email_verified = 1? No → call 201.
2. **"How do we get it?"** — Pattern derivation (free), then Prospeo API ($0.01), then Apollo API (backup). Million Verifier gates every result.

### Input
- Person name (first_name, last_name from people_people_master)
- Company domain (from outreach_outreach.domain)
- Company name (from cl_company_identity.canonical_name)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Name + domain | **Pattern derivation** — generate likely email patterns (first.last@, flast@, firstlast@, first@). ~60% of companies use first.last@domain. | 3-5 candidate emails | String formatting (free) |
| 2 | Candidate emails | **Verify candidates** — hit Million Verifier on each pattern. First one that verifies = done. | Verified email or all fail | Million Verifier API |
| 3 | Name + domain (if step 2 failed) | **Prospeo domain search** — search their 300M+ database. 98% accuracy. | Email + confidence | Prospeo API ($0.01/email) |
| 4 | Prospeo result | **Verify** — Million Verifier on Prospeo result. | Verified email or fail | Million Verifier API |
| 5 | Name + domain (if step 4 failed) | **Apollo lookup** — larger database, backup. 32-38% bounce rate on their "verified," so we verify externally. | Email + confidence | Apollo API |
| 6 | Apollo result | **Verify** — Million Verifier. No exceptions. | Verified email or fail | Million Verifier API |

If all steps fail, the person record stays without email. Slot remains at EMAIL_ONLY = 0. Process 202 can still find LinkedIn for alternate channel.

### Output
- `people_people_master.email` = verified email address
- `people_people_master.email_verified` = 1
- `people_people_master.email_verification_source` = which step found it (pattern, prospeo, apollo)
- `people_people_master.email_verified_at` = timestamp

### Circle (Bedrock §5)
Email bounce from Mailgun webhook → updates email_verified = 0 → triggers re-run of 201 on next cycle. Strike tracking: 3 bounces on same email → mark contact as bad, re-discover.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | People master (write email), outreach_outreach (read domain) |
| svg-d1-spine | D1 | 641a9a1e | READ | cl_company_identity (canonical_name) |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| OUTREACH_PROSPEO_API_KEY | imo-creator | dev | Step 3 — Prospeo domain search |
| OUTREACH_APOLLO_API_KEY | imo-creator | dev | Step 5 — Apollo backup |
| OUTREACH_MILLIONVERIFIER_API_KEY | imo-creator | dev | Steps 2, 4, 6 — verification gate |

**Tool Priority (Well Drinks First):**
1. Pattern derivation — free, try first
2. Prospeo — $0.01/email, best accuracy
3. Apollo — backup, needs external verification
4. Million Verifier — gate on ALL sources, no exceptions

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `people_people_master` | Person name (first_name, last_name) | `unique_id` |
| `outreach_outreach` | Company domain | `outreach_id` |
| `cl_company_identity` (spine) | Canonical company name | `outreach_id` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `people_people_master` | email, email_verified, email_verification_source, email_verified_at | On successful verification |

### Forbidden Paths

| Action | Why |
|--------|-----|
| Write an unverified email | Million Verifier gate. No exceptions. |
| Skip pattern derivation and go straight to paid | Well drinks first. Free before cheap. |
| Call this process if email_verified = 1 | Conditional — orchestrator checks first. |
| Retry indefinitely on a failed email | 3 sources. If all fail, move on. |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants
- Million Verifier is the gate. Every email gets verified regardless of source.
- Pass order: pattern (free) → Prospeo ($0.01) → Apollo (backup). Never skip.
- Email patterns to try: first.last@, flast@, firstlast@, first@, last.first@
- A bounce from Mailgun webhook invalidates the verification — triggers re-discovery.

### Variables
- Which pattern works for a given company domain
- Whether Prospeo or Apollo has the email
- Hit rate per source (tracked in logbook)
- Cost per verified email (tracked in analytics)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Million Verifier API returns error on 5 consecutive calls | HALT — check API key |
| Prospeo returns 429 (rate limited) | PAUSE — back off, retry after cooldown |
| Apollo budget cap reached | STOP Apollo, continue with pattern + Prospeo only |
| Bounce rate on verified emails > 5% | HALT — Million Verifier may be returning false positives. Investigate. |
| Strike 3 on same failure | Troubleshoot/Train → Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream

| Dependency | What | Status |
|-----------|------|--------|
| Process 200 | Filled slot with person name | Required |
| outreach_outreach.domain | Company domain | From SEED |
| cl_company_identity.canonical_name | Company name | From SEED |

### Downstream

| Consumer | What It Needs |
|----------|--------------|
| Process 100 (LCS Pipeline) | Verified email for MID delivery via Mailgun |
| Process 700 (Campaign Engine) | Reachability status: EMAIL_ONLY or FULL |

---

## 9. SMOKE TEST

```
1. Pick a person with name + domain but no email → run pattern derivation → expected: candidate emails generated
2. Run Million Verifier on candidates → expected: one verifies or all fail
3. If all fail, run Prospeo → expected: email returned
4. Verify Prospeo result → expected: email_verified = 1, written to people_people_master
5. Check: SELECT email, email_verified, email_verification_source FROM people_people_master WHERE unique_id = ? → expected: email present, verified = 1
```

**Three Primitives Check:**
1. **Thing:** Does the person record exist? Does the domain exist?
2. **Flow:** Does the name + domain reach the pattern generator? Does the candidate reach Million Verifier?
3. **Change:** Is the verified email written to the person record?

---

## 10. LOGBOOK

_No runs yet. Process in BUILD state._

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-01 |
| Last Modified | 2026-04-01 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |

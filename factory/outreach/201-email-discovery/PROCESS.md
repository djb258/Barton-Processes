# PROCESS: Find Email
## Fills person_email on slots that have a name but no email address
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-201 |
| Name | Find Email |
| Business Silo | outreach |
| CTB Position | factory/outreach/201-email-discovery (LEAF) |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | -- |
| BAR Reference | BAR-52, BAR-191 |
| Deployed URL | Local script (not deployed as worker) |
| Cron | Manual / called after Process 200 |
| Runtime | Python 3.x + curl_cffi + wrangler D1 subprocess |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Without a verified email, we cannot send outreach through Mailgun. A name in a slot without an email is half a contact. Process 200 fills the name. Process 201 fills the email. Until this process runs, the slot stays at readiness_tier T3 (name only) and cannot enter the LCS pipeline.

Three gates, cheapest first: pattern generation is free and deterministic, Hunter promotion is free (data already paid for), Startpage search is free (proxy cost only). **Current cost: proxy only (~$0 for Gate A/B, proxy cost for Gate C).** Million Verifier integration is PLANNED as a future Gate D -- not yet implemented. When MV is added, verification will cost $0.003/email with 111,167 credits available, bringing total cost to ~$103 for full run.

---

## 3. IMO -- What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** -- A slot in slot_workbench where has_name = 1 AND has_email = 0
2. **"How do we get it?"** -- Three gates: (A) generate from email pattern + name + domain, (B) promote hunter_email if confidence >= 80, (C) search Startpage with natural language query

### Input
- Slot with person_first_name, person_last_name populated (has_name = 1)
- Company constants: domain, company_name, canonical_name, city, state
- Hunter data: hunter_email_pattern, vendor_email_pattern, hunter_email, hunter_confidence

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| Gate A: Pattern Generate | hunter_email_pattern + name + domain | Apply pattern template to name parts, produce email deterministically. 12 patterns handled: {first}.{last}, {f}{last}, {first}, {last}, {first}{last}, {f}.{last}, {first}_{last}, {f}_{last}, {last}.{first}, {last}{f}, {first}.{f_last}, {f_first}.{last} | Generated email or skip | String formatting (free) |
| Gate B: Hunter Promote | hunter_email + hunter_confidence | If hunter_email exists AND confidence >= 80, promote directly. Data already paid for at SEED time. | Promoted email or skip | Hunter data lookup (free) |
| Gate C: Startpage Search | first + last + company_name + city/state | Query "{first} {last} {company_name} email contact". For common names add city/state. Parse all emails from results. Score by domain match + name match. | Best-scoring email or miss | Startpage + curl_cffi + DataImpulse proxy (free) |
| Gate D: Verify (PLANNED) | Candidate email from A/B/C | **NOT YET IMPLEMENTED.** Million Verifier API check -- risky/invalid rejected, valid/catch-all accepted. Currently emails are stored unverified. Verification is a manual step or future gate. | Verified email or reject | Million Verifier ($0.003/check) -- PLANNED |

**Gate order is the constant.** A before B before C. Stop on first hit. Cheapest and most deterministic first.

### Output
- `slot_workbench.person_email` = found email address
- `slot_workbench.has_email` = 1
- `slot_workbench.person_source` = gate identifier (pattern_generate, hunter_promote, startpage_201)
- `slot_workbench.readiness_tier` = recalculated (T3 -> T2 or T1)
- JSONL output file per run with full audit trail

### Circle (Bedrock S5)
Email found -> slot updated -> readiness_tier promoted -> enters LCS pipeline -> Mailgun sends -> bounce webhook -> person_email_verified = 0 -> re-enter 201 on next cycle. Bounce feedback closes the circle.

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches. A mechanic reads this and knows exactly what to set up before the process can run._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | slot_workbench (read slots, write person_email) |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| String formatting | Built-in | Free | none | Gate A -- pattern generation (deterministic) |
| Hunter data (pre-loaded) | D1 lookup | Free | none | Gate B -- confidence-based promotion |
| Startpage + curl_cffi | API + library | Free (proxy cost) | PROXY_USER, PROXY_PASS | Gate C -- natural language email search |
| DataImpulse proxy | Proxy | Free (bundled) | PROXY_USER, PROXY_PASS | Residential proxy for Gate C requests |
| Million Verifier | API | Top Shelf ($0.003/check) | MV_API_KEY | **PLANNED -- not yet integrated.** Email verification -- 111,167 credits remaining |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_USER | imo-creator | dev | Gate C -- DataImpulse proxy |
| PROXY_PASS | imo-creator | dev | Gate C -- DataImpulse proxy |
| MV_API_KEY | imo-creator | dev | Million Verifier verification (PLANNED -- not yet used) |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 -- Gate A (pattern generate, deterministic) and Gate B (Hunter promote, data exists)
2. Free external fetches with proxy -- Gate C (Startpage search via DataImpulse)
3. Top shelf per-call API -- Million Verifier ($0.003/check, only after A/B/C produce a candidate) -- **PLANNED, not yet integrated**

---

## 5. OSAM -- Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins. What's forbidden. From the hub OSAM._

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| slot_workbench.slot_id | Primary key for the slot | slot_id |
| slot_workbench.outreach_id | Company identifier | outreach_id |
| slot_workbench.slot_type | CEO, CFO, HR | slot_id |
| slot_workbench.person_first_name | Input to pattern generation (V -- fill) | slot_id |
| slot_workbench.person_last_name | Input to pattern generation (V -- fill) | slot_id |
| slot_workbench.domain | Email domain (C -- per company) | outreach_id |
| slot_workbench.company_name | Search query component (C -- per company) | outreach_id |
| slot_workbench.canonical_name | Search query component (C -- per company) | outreach_id |
| slot_workbench.city | Location disambiguation (C -- per company) | outreach_id |
| slot_workbench.state | Location disambiguation (C -- per company) | outreach_id |
| slot_workbench.hunter_email_pattern | Email pattern template e.g. "{first}.{last}" (C -- per domain) | outreach_id |
| slot_workbench.vendor_email_pattern | Alternate pattern source (C -- per domain) | outreach_id |
| slot_workbench.hunter_email | Pre-discovered email candidate (V -- fill) | slot_id |
| slot_workbench.hunter_confidence | Confidence score 0-100 (V -- fill) | slot_id |
| slot_workbench.has_name | Gate condition: must be 1 (C -- flag) | slot_id |
| slot_workbench.has_email | Gate condition: must be 0 (C -- flag) | slot_id |
| slot_workbench.has_linkedin | Used for readiness_tier calc (C -- flag) | slot_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| slot_workbench.person_email | Found email address (V -- fill) | On gate hit |
| slot_workbench.has_email | Set to 1 (C -- flag) | On gate hit |
| slot_workbench.person_source | Gate identifier string (V -- fill) | On gate hit |
| slot_workbench.readiness_tier | Recalculated tier (C -- derived) | After write |

### Join Chain

```
slot_workbench.outreach_id
  -> slot_workbench (self-join on outreach_id for company-level constants)
  -> slot_workbench.slot_id (individual slot for person-level variables)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Skip Gate A and go to Gate B/C | Gate order is the constant. Deterministic first. |
| Write person_email without updating has_email | Inconsistent state breaks downstream queries |
| Run on slots where has_name = 0 | No name = nothing to generate from |
| Overwrite an existing person_email | If has_email = 1, this slot is not in the query set |
| Write directly to Neon vault | Neon is vault only. All working data on CF D1. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Which slots need emails? | slot_workbench | has_name = 1 AND has_email = 0 |
| What email pattern does this company use? | slot_workbench | hunter_email_pattern, vendor_email_pattern |
| How confident is the Hunter email? | slot_workbench | hunter_confidence |
| What gate found the email? | slot_workbench | person_source |
| Is this slot ready for LCS? | slot_workbench | readiness_tier |

---

## 6. CONSTANTS & VARIABLES (Bedrock S2)

### Constants (structure -- never changes)

_What is fixed regardless of what data flows through. If this changes, you're redesigning, not operating._

- **Gate order: A -> B -> C** -- IMO: cheapest/deterministic first regardless of input. CTB: applies at every altitude. Circle: wrong order wastes money on re-runs.
- **12 email pattern formats** -- {first}.{last}, {f}{last}, {first}, {last}, {first}{last}, {f}.{last}, {first}_{last}, {f}_{last}, {last}.{first}, {last}{f}, {first}.{f_last}, {f_first}.{last}. Named, formatted, validated.
- **Gate A threshold: has_email_pattern = 1** -- IMO: pattern exists or it doesn't. CTB: same rule for all slots. Circle: no feedback changes this.
- **Gate B threshold: hunter_confidence >= 80** -- IMO: confidence is the filter regardless of slot. CTB: same threshold everywhere. Circle: threshold validated against bounce rates.
- **Startpage query pattern: "{first} {last} {company_name} email contact"** -- IMO: natural language avoids CAPTCHA. CTB: same pattern all slots. Circle: query format doesn't change with results.
- **Common name disambiguation: add city/state** -- IMO: reduces false matches. CTB: same rule for all common names. Circle: still holds after feedback.
- **Readiness tier calculation: T1/T2/T3/T4** -- IMO: tier depends on filled fields only. CTB: same formula everywhere. Circle: correct tier after re-run.
- **JSONL audit trail per run** -- IMO: every run produces a log. CTB: same format at all levels. Circle: enables post-run analysis.
- **Script name: find-email.py** -- Named, formatted, locked.

### Variables (fill -- changes every run)

_The values that fill the constants. Different every execution._

- **person_first_name, person_last_name** -- The name parts fed into pattern generation. Different per slot.
- **person_email** -- The email address itself. Changes per person per company.
- **hunter_confidence value** -- 0-100 integer, compared against constant threshold.
- **Which gate hits first** -- Depends on available data per slot.
- **Startpage search results** -- Different HTML per query.
- **Email scoring result** -- Depends on domain match + name match.
- **MV credits remaining** -- 111,167 at start, decreasing per check (applies after MV integration -- currently unused).

---

## 7. STOP CONDITIONS

_When to halt. Not optional. From Troubleshooting Loop (Bedrock S6) and Aviation Model (Bedrock S8)._

| Condition | Action |
|-----------|--------|
| CAPTCHA rate > 10% of Gate C queries | HALT Gate C -- rotate proxy, increase delay |
| Million Verifier credits < 1,000 | HALT MV integration -- alert for credit purchase (applies after MV integration) |
| Bounce rate on 201-generated emails > 5% | HALT -- investigate gate logic, tighten confidence thresholds |
| D1 write failures > 5 consecutive | HALT -- check wrangler auth, D1 availability |
| Missing PROXY_USER/PROXY_PASS | Gate C skipped automatically (A+B still run) |
| Can't answer two-question intake | HALT -- process isn't defined |
| OSAM question can't be routed | HALT -- semantic gap, ask human |
| Strike 3 on same failure | Troubleshoot/Train -> produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 010 (SEED) | Populates slot_workbench with company constants, hunter data | DONE |
| Process 300 (Blog Recon) | Enriches company data, may find emails via recon | DONE (optional enrichment) |
| Process 200 (Find Person) | Fills person_first_name, person_last_name (has_name = 1) | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| LCS Pipeline | person_email + has_email = 1 for MID delivery via Mailgun |
| Process 700 (Campaign Engine) | readiness_tier T2+ to enter campaign |
| Million Verifier (PLANNED -- Gate D) | person_email to verify, will write person_email_verified when integrated |
| Process 202 (LinkedIn Discovery) | Runs in parallel -- if 201 misses, 202 may still find LinkedIn |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output. Not prose -- run these._

```
1. Select 5 slots with has_name=1, has_email=0, has_email_pattern=1
   -> Run Gate A only (--gate a --limit 5)
   -> Expected: pattern-generated emails in output JSONL, D1 updated

2. Select 5 slots with hunter_email IS NOT NULL AND hunter_confidence >= 80
   -> Run Gate B only (--gate b --limit 5)
   -> Expected: hunter emails promoted, D1 updated

3. Select 5 slots that miss Gate A and B
   -> Run all gates (--gate all --limit 5)
   -> Expected: Gate C fires, Startpage queried, email parsed or miss logged

4. Run --dry-run on 10 slots
   -> Expected: output JSONL written, zero D1 writes

5. Verify D1 state:
   SELECT slot_id, person_email, has_email, person_source, readiness_tier
   FROM slot_workbench WHERE person_source LIKE 'pattern_generate%' LIMIT 5
   -> Expected: person_email populated, has_email = 1, readiness_tier = T2 or T1
   -> NOTE: person_email_verified will be NULL -- MV is not yet integrated

6. Resume test:
   -> Run --limit 5, stop, run --limit 10 --resume
   -> Expected: first 5 skipped, next 5 processed

NOTE: No MV verification step in smoke test -- emails are stored unverified.
MV smoke test will be added when Gate D is implemented.
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** Does the slot exist in slot_workbench? Does it have has_name = 1?
2. **Flow:** Does the name + domain reach the gate chain? Does the result reach D1?
3. **Change:** Is person_email written? Is has_email flipped to 1? Is readiness_tier recalculated?

If any fails -> that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock S6).

---

## 10. ANALYTICS -- The Dyno Sheet (Bedrock S2 + S5)

_The BUILD->OPERATE gate. No analytics passing tolerance = stays on the dyno. You don't flip to OPERATE by saying "it seems to work." The numbers say it works, or they don't._

_This section MUST be defined BEFORE build starts. No analytics spec -> no build authorization (BAR-187)._

_This is also the vendor scorecard. When you want to swap a vendor in the Snap-On Toolbox, pull the scorecard for the current one and say: beat these numbers._

### Process Metrics

_Define BEFORE build starts. These are the instruments on the dyno. Each metric is a constant (named, formatted). The value each run is the variable._

| Metric | Unit | First Run = Baseline | Target (after baseline) | Tolerance |
|--------|------|---------------------|------------------------|-----------|
| Gate A hit rate | % | BASELINE | > 40% | +/- 5% |
| Gate B hit rate | % | BASELINE | > 15% | +/- 3% |
| Gate C hit rate | % | BASELINE | fill remainder | n/a |
| Overall email fill rate | % | BASELINE | > 80% | +/- 5% |
| Gate C CAPTCHA rate | % | BASELINE | < 5% | max 10% |
| D1 write success rate | % | BASELINE | > 99% | min 95% |
| Bounce rate on generated emails | % | BASELINE | < 5% (after MV integration) | max 8% |
| Cost per email found (current) | $/email | BASELINE | ~$0.00 (proxy only) | n/a |
| Cost per email found (after MV) | $/email | BASELINE | ~$0.003 (MV dominated) | max $0.005 |
| Total run cost (current) | $ | BASELINE | ~$0 (proxy bundled) | n/a |
| Total run cost (after MV) | $ | BASELINE | ~$103 (full corpus) | +/- 20% |

### Tool Scorecard (per Snap-On sub-hub vendor)

_Track per vendor so you can benchmark swaps. Tool is constant, vendor is variable, scorecard measures the variable._

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| -- | Million Verifier (PLANNED) | BASELINE | $0.003/email | BASELINE | BASELINE | pre-build -- not yet integrated |
| -- | Startpage (via DataImpulse) | BASELINE | $0.00 (proxy bundled) | BASELINE | BASELINE | pre-build |
| -- | Pattern Generate (built-in) | BASELINE | $0.00 | 0% | <1ms | pre-build |
| -- | Hunter (pre-loaded D1) | BASELINE | $0.00 | 0% | <1ms | pre-build |

### Sigma Tracking (Bedrock S2)

_After 3+ runs, track whether each metric is tightening, flat, or expanding._

| Metric | Run 1 | Run 2 | Run 3 | Trend | Action |
|--------|-------|-------|-------|-------|--------|
| Gate A hit rate | -- | -- | -- | -- | -- |
| Gate B hit rate | -- | -- | -- | -- | -- |
| Overall fill rate | -- | -- | -- | -- | -- |
| Bounce rate | -- | -- | -- | -- | -- |
| CAPTCHA rate | -- | -- | -- | -- | -- |

_Tightening = real constant, process is stabilizing. Flat = phantom, something isn't learning. Expanding = broken, something upstream changed._

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs + **auditor sign-off** |
| OPERATE | REPAIR | Any metric outside tolerance |
| REPAIR | OPERATE | Fix applied + metric back within tolerance + **auditor verification** |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same failure pattern 3 times at fleet level -> AD |

_The builder cannot certify its own work. The auditor MUST be a different engine than the builder. (Bedrock S8)_

---

## 11. EXECUTION TRACE (During BUILD)

_Append-only record of what happened during build/execution. This is NOT the logbook -- the logbook is created only after auditor certification. This is the build journal that the auditor reviews._

_Every run, every step, every result gets traced here. The auditor reads this to decide: certify or reject._

### Entry Format (per step, per run)

| Field | Description | Format | Required |
|-------|-------------|--------|----------|
| trace_id | Unique entry identifier | UUID | Yes |
| run_id | Which execution run this belongs to | UUID (one per goal/batch) | Yes |
| step | What was attempted | Station ID or action name | Yes |
| target | Expected outcome (defined in S10 metrics) | Text -- measurable | Yes |
| actual | What happened | Text -- measurable | Yes |
| delta | Target vs actual | Number or text -- the gap | Yes |
| status | Step outcome | done / failed / skipped | Yes |
| error_code | If failed -- machine-readable error type | Text or null | If failed |
| error_message | If failed -- human-readable description | Text or null | If failed |
| tools_used | Which Snap-On sub-hub tools were called | JSON array of tool numbers | Yes |
| duration_ms | How long this step took | Integer (milliseconds) | Yes |
| cost_cents | Cost of this step | Integer (cents) | Yes |
| timestamp | When this happened | ISO-8601 | Yes |
| signed_by | Who/what produced this entry | Agent name or "manual" | Yes |

### Run Summary (per execution run)

| Field | Description |
|-------|-------------|
| run_id | UUID for this execution run |
| trigger | What started this run (cron / manual / inbox / upstream) |
| orbt_at_start | ORBT state when run began |
| steps_total | How many steps planned |
| steps_completed | How many passed |
| steps_failed | How many failed |
| total_duration_ms | Wall clock time for full run |
| total_cost_cents | Sum of all step costs |
| errors | Count + summary of failures |
| learnings | What was new -- feeds to LBB |

### Rules

- **Append-only.** No edits. No deletions. Immutable.
- **Every step gets a trace entry.** No step executes without logging.
- **Trace exists during BUILD.** This is NOT the certified logbook.
- **Auditor reviews the trace** to decide certification.
- **Trace persists after certification** -- it becomes evidence inside the logbook's birth certificate.

---

## 12. LOGBOOK (After Certification Only)

_The aircraft's legal identity. Created ONLY when the auditor certifies the process (BUILD -> OPERATE). (Bedrock S8, logbook_schema.yaml)_

**No logbook during BUILD.** The execution trace (S11) is the build journal. The logbook is born when the auditor signs off.

### Rules (from logbook_schema.yaml)

1. No logbook until aircraft is certified (auditor sign-off on BUILD)
2. First entry is always the **birth certificate** (certification record)
3. Append-only. No edits. No deletions. Immutable.
4. Every entry must have all required fields. Incomplete entries rejected.
5. Mechanic must log what they READ before starting (context_loaded)
6. Auditor reviews logbook entries, not source code.
7. The builder CANNOT be the auditor. Different engine required.

### Birth Certificate (first entry -- created by auditor at certification)

| Field | Value |
|-------|-------|
| heir_ref | Full HEIR record for this process |
| orbt_entered | BUILD |
| orbt_exited | OPERATE |
| action | "Process certified -- airworthiness confirmed" |
| authority | "Auditor certification per Tier 0 gate stack" |
| gates_passed | { imo: true, ctb: true, circle: true } |
| checklist_type | build_checklist |
| checklist_items | Full build checklist with all items PASS |
| execution_trace_ref | Link to S11 trace (evidence the auditor reviewed) |
| signed_by | Auditor agent (MUST be different engine than builder) |
| signed_at | Certification timestamp |

### Subsequent Entries (during OPERATE, REPAIR, TROUBLESHOOT/TRAIN)

| Field | Description | Required |
|-------|-------------|----------|
| heir_ref | HEIR reference -- hub_id, sub_hub, component | Yes |
| orbt_entered | ORBT mode when work started | Yes |
| orbt_exited | ORBT mode when work completed | Yes |
| context_loaded | What was read before work began (heir, orbt, logbook, tier0) | Yes |
| error_ref | Error table reference (null for maintenance) | If repair |
| visit_path | MAINTENANCE or ERROR | Yes |
| strike_count | Recurrence count for this error pattern | Yes |
| action | What the mechanic did | Yes |
| authority | Which Bedrock section authorized this | Yes |
| gates_passed | { imo: bool, ctb: bool, circle: bool } | Yes |
| checklist_type | operate / repair / troubleshoot_train | Yes |
| signed_by | Who did the work | Yes |
| signed_at | Immutable timestamp | Yes |

---

## 13. FLEET FAILURE REGISTRY & STRIKE TRACKING

_Strike tracking at FLEET level, not per-goal. The same failure pattern appearing across multiple goals/runs triggers escalation. (Bedrock S6, S8)_

### Failure Pattern Registry

| Pattern ID | Station | Error Code | First Seen | Occurrences | Goals Affected | Strike Count | Status |
|-----------|---------|-----------|-----------|-------------|---------------|-------------|--------|
| -- | -- | -- | -- | -- | -- | -- | -- |

### Strike Rules

- **Strike 1:** Repair. Fix at source. Log it.
- **Strike 2:** Repair with scrutiny. Was root cause actually found?
- **Strike 3:** **STOP.** Troubleshoot/Train. The problem isn't a broken part -- it's a broken understanding.

### Airworthiness Directive (Strike 3 output)

_When strike 3 fires, the fix goes to ALL processes, not just the one that failed. This updates the template, not just one file._

| Field | Value |
|-------|-------|
| AD Number | AD-[YYYY]-[NNN] |
| Failure Pattern | FP-[NNN] -- [description] |
| Root Cause | [from Troubleshooting Loop S6] |
| Fix Applied | [what changed] |
| Scope | ALL processes / [specific silo] / [specific station] |
| Template Updated | Yes / No -- if Yes, what section |
| Issued By | [mechanic + auditor sign-off] |
| Issued At | [timestamp] |

**AD issuance requires:**
1. Root cause identified (Troubleshooting Loop S6 complete)
2. Fix tested on the failing process
3. Fix verified by auditor (different engine)
4. Template updated if the fix is structural
5. All affected processes notified/updated

---

## 14. SESSION LOG

_Every session that touches this process. Links to LBB for detail._

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| 2026-04-02 | Initial PROCESS.md created (v2.0.0 format) | none |
| 2026-04-01 | Rewritten to PROCESS_TEMPLATE v4.0.0 -- all 14 sections | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-02 |
| Last Modified | 2026-04-01 |
| Version | 3.0.0 |
| Template Version | 4.0.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md (parent repo — Barton-Processes inherits) |
| Logbook Schema | law/logbook_schema.yaml |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md |
| Data Flow | factory/outreach/201-email-discovery/DATA_FLOW.md |

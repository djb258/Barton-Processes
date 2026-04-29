> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# PROCESS: Find LinkedIn
## Fills person_linkedin on slots that have a name but no LinkedIn URL
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-202 |
| Name | Find LinkedIn |
| Business Silo | svg-agency |
| CTB Position | factory/outreach/202-linkedin-discovery (LEAF) |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | -- |
| BAR Reference | BAR-52, BAR-192 |
| Deployed URL | not deployed (local script) |
| Cron | Manual or called by orchestrator |
| Runtime | Python 3 + curl_cffi (local) |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

LinkedIn URL enables two things: (1) profile-based personalization in the LCS pipeline -- the LinkedIn profile is the richest public source of what someone actually does, and (2) HeyReach as a delivery channel when email bounces or doesn't exist. Without LinkedIn, you lose both the personalization angle and the backup channel.

The LinkedIn URL is person-scoped, not company-scoped. If the person changes companies, the URL still works. This is a write-once asset with long shelf life. Cost: approximately $0.90 total for all remaining slots. Gate A and B are free (matching existing data), Gate C is proxy-only.

---

## 3. IMO -- What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** -- A slot in slot_workbench where has_name = 1 AND has_linkedin = 0.
2. **"How do we get it?"** -- Three gates: (A) match person name against recon_linkedin_people from Process 300, (B) promote hunter_linkedin, (C) search Startpage.

### Input
- person_first_name, person_last_name (from Process 200 -- VARIABLE, the names we're matching)
- company_name (CONSTANT -- disambiguates common names)
- city, state (CONSTANT -- LinkedIn profiles list location, used for disambiguation)
- domain (CONSTANT -- but EXCLUDED from query: returns website results, not LinkedIn)
- recon_linkedin_people (VARIABLE -- JSON array of LinkedIn /in/ URLs found by Process 300)
- hunter_linkedin (VARIABLE -- Hunter may have found it during Process 200)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 (Gate A) | recon_linkedin_people + person name | Parse each URL slug (e.g. "john-smith-12345" -> first=John, last=Smith). Strip trailing hex/numeric IDs, split on hyphens, drop single-char parts. Compare to person_first_name + person_last_name, case-insensitive. | Matched LinkedIn URL or nothing | String parsing (FREE) |
| 2 (Gate B) | hunter_linkedin | If not null and matches linkedin.com/in/ pattern, promote it. | LinkedIn URL or nothing | Column read (FREE) |
| 3 (Gate C) | first + last + company + "linkedin" | POST to startpage.com/do/dsearch via DataImpulse proxy. Query: "{first} {last} {company} linkedin" (natural language, zero CAPTCHA). Extract /in/ URLs from HTML. Score by slug-to-name similarity. Require last-name match minimum. | Best-match LinkedIn URL or nothing | DataImpulse proxy (~$0.001/query) |

Gate priority: A -> B -> C. First hit wins. Gate C only fires if A and B miss.

### Output
- `slot_workbench.person_linkedin` = LinkedIn profile URL (cleaned, no query params)
- `slot_workbench.has_linkedin` = 1
- `slot_workbench.linkedin_found_at` = UTC timestamp
- `slot_workbench.readiness_tier` = recalculated (FULL if email+linkedin, REACHABLE if either, PATTERN_READY if name only, EMPTY if nothing)

### Circle (Bedrock S5)
LinkedIn found -> slot updated -> used by LCS for personalization and HeyReach delivery. If person changes companies, LinkedIn URL still valid (it's their profile, not the company's). Process 500 (Talent Flow) checks monthly for movement detection. Dead profile -> flag for re-discovery. Logbook entry captures hit rates per gate per run, feeding next-run tuning.

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches. A mechanic reads this and knows exactly what to set up before the process can run._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | slot_workbench (read slots, write LinkedIn) |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| Startpage Search | API (POST form) | Cheap | none (public) | Search engine query via proxy |
| DataImpulse Proxy | Proxy | Cheap | PROXY_USER, PROXY_PASS | Residential proxy for Startpage requests |
| curl_cffi | Tool | Free | none | Chrome131 impersonation for TLS fingerprint |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_USER | imo-creator | dev | DataImpulse proxy auth (Gate C) |
| PROXY_PASS | imo-creator | dev | DataImpulse proxy auth (Gate C) |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 (Gate A: recon_linkedin_people match) -- always first
2. Free column promotion (Gate B: hunter_linkedin) -- second
3. Cheap proxy search (Gate C: Startpage via DataImpulse) -- only when free exhausted

### Proxy Configuration (constant -- proven 2026-03-31)
- Host: gw.dataimpulse.com
- Port: 10000 (sticky session -- NOT 823 rotating)
- Username format: {PROXY_USER}__cr.us (US country targeting)
- Method: POST form to startpage.com/do/dsearch
- Impersonation: chrome131 via curl_cffi
- Delay: 3 seconds minimum between queries
- Port rotation: every 50 queries
- Cost: ~$1/GB (~$0.90 for all remaining slots)

---

## 5. OSAM -- Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins. What's forbidden. From the hub OSAM._

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| slot_workbench | slot_id, outreach_id, company_name, city, state, domain, person_first_name, person_last_name, recon_linkedin_people, hunter_linkedin, has_name, has_email, has_linkedin, readiness_tier | slot_id (PK), outreach_id (FK) |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| slot_workbench | person_linkedin, has_linkedin (=1), linkedin_found_at (UTC), readiness_tier (recalculated) | On successful LinkedIn discovery |

### Join Chain

```
slot_workbench.outreach_id
  -> (company-level data via outreach_id FK)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Direct write to Neon vault | Neon is vault only -- all working data on D1 (SEED->WORK->PUSH lifecycle) |
| Include domain in Startpage query | Returns website results, not LinkedIn profiles -- proven constant |
| Scrape LinkedIn directly | TOS violation -- search index only |
| Write to any table other than slot_workbench | This process is scoped to slot_workbench only |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Does this person have a LinkedIn? | slot_workbench | has_linkedin |
| What is the LinkedIn URL? | slot_workbench | person_linkedin |
| When was it found? | slot_workbench | linkedin_found_at |
| What tier is this slot? | slot_workbench | readiness_tier |
| How many slots still need LinkedIn? | slot_workbench | WHERE has_name=1 AND has_linkedin=0 |

---


---

## DMJ — Define, Map, Join (law/doctrine/DMJ.md)

_Three steps. In order. Can't skip._

### Define (Build the Key)

| Element | ID | Format | Description | C or V |
|---------|-----|--------|-------------|--------|
| linkedin_url | LD-01 | TEXT, URL (linkedin.com/in/slug) | LinkedIn profile URL for a person | V |
| profile_name | LD-02 | TEXT, title case, First Last | Name from LinkedIn profile slug | V |
| outreach_id | LD-03 | TEXT, UUID | Join key to slot_workbench | C |
| slot_type | LD-04 | TEXT, enum: CEO/CFO/HR | Which slot this LinkedIn resolves to | C |

### Map (Connect Key to Structure)

| Source | Target | Transform |
|--------|--------|-----------|
| LD-01 linkedin_url | person_linkedin | Direct |
| LD-02 profile_name | person_first_name + person_last_name | Split on space |

### Join (Path to Spine)

| Join Path | Type | Description |
|-----------|------|-------------|
| slot_workbench.outreach_id | direct | outreach_id on workbench row |

## 6. CONSTANTS & VARIABLES (Bedrock S2 + Mathematical Principle)

### Mathematical Definitions

```
DECISION:     P(x;θ) = 1  if  max_i [ C_i(x) / k_i ] ≤ 1  else 0
DIAGNOSTIC:   r(x) = [ C_1(x)/k_1, ..., C_n(x)/k_n ]
STABILITY:    ∀ t ∈ [1..N]: P(f^t(x);θ) = 1 AND var(r_i) ≤ σ_max
```

### Step-Level Comparators and Tolerances

**Gate A -- Slug Match (recon_organized_linkedin from 300 Organizer):**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_1 | slug_miss_rate | Change | % of slots where no slug matches person name | 0.60 (≤60% -- many slugs won't match) | 1 |

**Gate B -- Hunter Promote:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_2 | hunter_miss_rate | Change | % of slots where hunter_linkedin is NULL | 0.80 (≤80% -- Hunter coverage sparse for LinkedIn) | 1 |

**Gate C -- Startpage Search:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_3 | search_miss_rate | Change | % of searches returning no LinkedIn URL | 0.40 (≤40% -- LinkedIn results are common on Startpage) | 1 |
| C_4 | captcha_rate | Change | % of searches hitting CAPTCHA | 0.05 (≤5%) | 1 |

**Writer:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_5 | write_failure_count | Thing | D1 write failures | ε_k | 1 |
| C_6 | total_fill_rate (inverted: 1-rate) | Change | % of input slots that got a LinkedIn URL | 0.10 (≥90% fill across all gates) | 1 |

**Process-Level:** `P_202(x;θ) = 1 if max_i[C_i(x)/k_i] ≤ 1 for i ∈ {1..6}`

### Conditional Logic (Workbench State Routing)

Process 202 only runs on slots where name exists but LinkedIn is missing:

```sql
SELECT * FROM slot_workbench
WHERE has_name = 1 AND has_linkedin = 0
ORDER BY outreach_id
```

Runs in parallel with Process 201 (email). Both depend on Process 200 completing first.

### Constants (structure -- never changes)

| Constant | Comparator | Primitive | k_i |
|----------|-----------|-----------|-----|
| Gate order: A → B → C | gate_skip_count | Flow | ε_k |
| LinkedIn URL pattern: linkedin.com/in/{slug} | url_format_violation_count | Thing | ε_k |
| Slug-to-name parsing rules | parsing_deviation_count | Change | ε_k |
| Query format: "{first} {last} {company} linkedin" | query_deviation_count | Thing | ε_k |
| Proxy config: port 10000, sticky, __cr.us, chrome131 | config_deviation_count | Flow | ε_k |
| Do not include domain in query | domain_in_query_count | Change | ε_k |
| Do not scrape LinkedIn directly | direct_scrape_count | Change | ε_k |
| Gate A reads recon_organized_linkedin (not raw recon) | raw_read_count | Flow | ε_k |

### Variables (fill -- changes every run)

- Which LinkedIn profile matches (guarded by scoring)
- person_first_name, person_last_name (from Process 200)
- recon_organized_linkedin content (from 300 Organizer — sorted slugs)
- hunter_linkedin content (may be null)
- Hit rate per gate, CAPTCHA rate, cost per run
- readiness_tier after recalculation (FULL / REACHABLE / PATTERN_READY / EMPTY)
- Tolerance values k_i (calibrated through operation)

---

## 7. STOP CONDITIONS

_When to halt. Not optional. From Troubleshooting Loop (Bedrock S6) and Aviation Model (Bedrock S8)._

| Condition | Action |
|-----------|--------|
| Can't answer two-question intake | HALT -- process isn't defined |
| CAPTCHA rate exceeds 10% of queries | HALT -- proxy config may need updating |
| 3 consecutive CAPTCHAs from Startpage | HALT Gate C -- investigate proxy immediately |
| DataImpulse returns 5 consecutive connection errors | HALT -- check proxy credentials in Doppler |
| Gate C hit rate drops below 30% over 100 queries | INVESTIGATE -- query format or proxy issue |
| Budget cap reached on proxy | HALT -- do not proceed |
| All slots processed (has_linkedin = 0 count = 0) | DONE -- process complete |
| Strike 3 on same failure pattern | Troubleshoot/Train -> produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 010 (SEED) | Slots exist in slot_workbench with company_name, city, state | OPERATE |
| Process 300 (Blog Recon) | recon_linkedin_people populated on slots | OPERATE |
| Process 200 (People Worker) | person_first_name, person_last_name filled, hunter_linkedin populated | OPERATE |
| DataImpulse proxy | Residential proxy for Startpage (Doppler creds) | Configured |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| LCS Pipeline | person_linkedin for profile-based personalization |
| HeyReach | LinkedIn URL for connection request delivery |
| Process 500 (Talent Flow) | LinkedIn URL for monthly movement detection |
| Process 700 (Campaign Engine) | Reachability: FULL (email+linkedin) or REACHABLE (one channel) |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output. Not prose -- run these._

```
1. Query slot_workbench: SELECT COUNT(*) FROM slot_workbench WHERE has_name = 1 AND has_linkedin = 0
   -> Expected: >0 slots to process

2. Pick one slot with recon_linkedin_people populated
   -> Run Gate A: parse slug (/in/john-smith-12345 -> first=John, last=Smith), compare names
   -> Expected: match found if person is in the recon list

3. Pick one slot with hunter_linkedin not null
   -> Run Gate B: validate URL pattern (linkedin.com/in/)
   -> Expected: promoted if valid linkedin.com/in/ URL

4. Pick one slot needing Gate C
   -> Build query: "{first} {last} {company} linkedin"
   -> POST to Startpage via proxy
   -> Expected: HTTP 200, HTML with results (not CAPTCHA)
   -> Parse: at least one linkedin.com/in/ URL
   -> Score: slug name matches person name

5. Dry-run: python3 find-linkedin.py --limit 5 --dry-run
   -> Expected: gates fire, no D1 writes, output logged to JSONL

6. Live run: python3 find-linkedin.py --limit 5
   -> Expected: D1 writes succeed, has_linkedin=1, readiness_tier updated
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** Does the slot exist? Does the proxy respond? Does recon data exist?
2. **Flow:** Does the query reach Startpage? Do results come back? Does the URL get written to D1?
3. **Change:** Is person_linkedin populated? Is has_linkedin = 1? Is readiness_tier updated?

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
| Gate A hit rate (recon match) | % | BASELINE | >40% | 30-50% |
| Gate B hit rate (hunter) | % | BASELINE | >20% | 10-30% |
| Gate C hit rate (Startpage) | % | BASELINE | >80% | 70-90% |
| Overall hit rate | % | BASELINE | >90% | 85-95% |
| Cost per LinkedIn found | $/unit | BASELINE | <$0.01 | $0.00-$0.02 |
| CAPTCHAs per 100 queries | count | BASELINE | <2 | 0-5 |
| Latency per Gate C query | ms | BASELINE | <5000 | 2000-8000 |

### Tool Scorecard (per Snap-On sub-hub vendor)

_Track per vendor so you can benchmark swaps. Tool is constant, vendor is variable, scorecard measures the variable._

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| -- | DataImpulse (proxy) | BASELINE | ~$0.001/query | BASELINE | BASELINE | first run pending |
| -- | Startpage (search) | BASELINE | FREE (via proxy) | BASELINE | BASELINE | first run pending |

### Sigma Tracking (Bedrock S2)

_After 3+ runs, track whether each metric is tightening, flat, or expanding._

| Metric | Run 1 | Run 2 | Run 3 | Trend | Action |
|--------|-------|-------|-------|-------|--------|
| Gate A hit rate | -- | -- | -- | -- | -- |
| Gate B hit rate | -- | -- | -- | -- | -- |
| Gate C hit rate | -- | -- | -- | -- | -- |
| Overall hit rate | -- | -- | -- | -- | -- |
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
| _empty -- no failures yet_ | | | | | | | |

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
| 2026-04-01 | Process doc created (v2.0.0, old format) | none |
| 2026-04-01 | Rewritten to PROCESS_TEMPLATE v4.0.0 (14 sections) | none |
| 2026-04-02 | Math engine added: 6 comparators, P(x;θ), conditional logic SQL. Gate A reads recon_organized_linkedin. | 5db86e97 |
| 2026-04-02 | Gate A+B ran all 10,786 slots: 941 Gate A (slug match) + 124 Gate B (Hunter promote) = 1,065 LinkedIn URLs filled. 999 slots → FULL, 66 → REACHABLE. | 5db86e97 |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-01 |
| Last Modified | 2026-04-02 |
| Version | 5.0.0 |
| Template Version | 4.0.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md (parent repo — Barton-Processes inherits) |
| Logbook Schema | law/logbook_schema.yaml |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md |
| Data Flow | factory/outreach/202-linkedin-discovery/DATA_FLOW.md |

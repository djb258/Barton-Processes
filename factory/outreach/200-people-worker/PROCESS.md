# PROCESS: Find Person
## Fills empty slots in slot_workbench with a person's name and title via three-gate chain
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-200 |
| Name | Find Person |
| Business Silo | svg-agency |
| CTB Position | factory/outreach/200-people-worker (LEAF) |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed (v3 — local Python script) |
| BAR Reference | BAR-52 |
| Deployed URL | not deployed |
| Cron | Manual (batched, after Process 300 completes) |
| Runtime | Python script (local or container) |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Without names, we can't send personalized outreach. Every downstream process — email discovery (201), LinkedIn discovery (202), campaign engine (700) — requires a human name in the slot. This process fills the `person_first_name` and `person_last_name` variables on empty slots using the cheapest source available first: free recon data, then free Hunter data, then cheap Startpage search.

A slot without a name is dead inventory. This process converts dead inventory into actionable contacts.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — A slot in `slot_workbench` where `has_name = 0` and `readiness_tier IN ('EMPTY', 'PATTERN_READY', 'HUNTER_READY')`
2. **"How do we get it?"** — Three gates checked in order: (A) `recon_name_titles` from Process 300, (B) Hunter candidate data already in the slot, (C) Startpage natural language search via DataImpulse proxy

### Input

| Source | What It Provides | Cost |
|--------|-----------------|------|
| `slot_workbench` (D1) | Empty slots with all company constants + recon data + hunter data | FREE |

Trigger SQL:
```sql
SELECT * FROM slot_workbench
WHERE has_name = 0 AND readiness_tier IN ('EMPTY','PATTERN_READY','HUNTER_READY')
ORDER BY outreach_id
```

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 — Gate A: Recon | `recon_organized_people` JSON (from 300 Organizer) | Parse organized entries — already sorted by C&V gate, already classified by Title Classifier. Match `bucket` to `slot_type`. | Person name + title filled. Source = `recon_300`. | wrangler d1 (FREE) |
| 2 — Gate B: Hunter | `hunter_first_name`, `hunter_last_name`, `hunter_title` | Check if Hunter has a candidate for this slot type. Validate title matches slot via same pattern table. | Person name promoted from Hunter. Source = `hunter`. | wrangler d1 (FREE) |
| 3 — Gate C: Startpage | `company_name`, `city`, `state`, `slot_type`, `employees` | Build natural language query. POST to Startpage via DataImpulse proxy. Parse results for names near LinkedIn URLs and title keywords. | Person name + optional LinkedIn URL. Source = `startpage_v3`. | curl_cffi + DataImpulse proxy (CHEAP) |

Gate chain stops at first success. Free before cheap. Always.

**Boundary note:** Process 200 fills NAME + TITLE only. Email discovery (including pattern-based generation) is Process 201's responsibility. Even if an email pattern exists, 200 does not write `person_email`.

### Output

| Field Written | Value | When |
|--------------|-------|------|
| `person_first_name` | Extracted first name | Any gate success |
| `person_last_name` | Extracted last name | Any gate success |
| `person_full_name` | Full name | Any gate success |
| `has_name` | 1 | Any gate success |
| `person_found_at` | ISO timestamp | Any gate success |
| `person_source` | `recon_300` / `hunter` / `startpage_v3` | Any gate success |
| `readiness_tier` | `NAME_ONLY` | Any gate success |
| `person_linkedin` | LinkedIn URL | If found in search results |
| `has_linkedin` | 1 | If LinkedIn found |
| `linkedin_found_at` | ISO timestamp | If LinkedIn found |

**Process 200 outputs name + title only -- email discovery is Process 201's responsibility.**

### Circle (Bedrock §5)
Person found -> slot updated -> workbench refreshed -> Process 201/202 sees the name and uses it for email/LinkedIn discovery -> Campaign engine (700) sends outreach -> Response feeds back to slot status. If person leaves company, slot cleared, process re-runs on the empty slot.

Fill rate tracked per gate (A/B/C) after each run. If fill rate plateaus for 3 consecutive runs, investigate: recon data stale, Hunter data exhausted, or search queries need refinement.

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches. A mechanic reads this and knows exactly what to set up before the process can run._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | `slot_workbench` — empty slots, recon data, hunter data, all company constants |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| Startpage | Tool | Cheap (proxy cost only) | None (public) | Natural language search for person names |
| DataImpulse | API | Cheap | PROXY_USER, PROXY_PASS | Residential proxy for Startpage queries |
| curl_cffi | Tool | Free | None | Browser impersonation (chrome131) to avoid CAPTCHA |
| wrangler d1 | Tool | Free | Cloudflare auth | D1 read/write via subprocess |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_USER | imo-creator | dev | Gate C — DataImpulse proxy |
| PROXY_PASS | imo-creator | dev | Gate C — DataImpulse proxy |

**Tool Priority (Well Drinks First):**
1. Gate A: Recon data from Process 300 (FREE — already in D1)
2. Gate B: Hunter candidate data (FREE — already in D1)
3. Gate C: Startpage search via proxy (CHEAP — only when free gates exhausted)

---

## 5. OSAM — Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins. What's forbidden. From the hub OSAM (barton-outreach-core/doctrine/OSAM.md)._

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `slot_workbench` | All company constants, recon data, hunter data, readiness state | `outreach_id` |

**Column Detail:**

| Column | Type | C&V | What It Provides |
|--------|------|-----|-----------------|
| `slot_id` | TEXT PK | CONSTANT | Unique slot identifier |
| `outreach_id` | TEXT | CONSTANT | Company join key |
| `company_unique_id` | TEXT | CONSTANT | Company UUID |
| `slot_type` | TEXT | CONSTANT | CEO / CFO / HR |
| `company_name` | TEXT | CONSTANT | Company name for search query |
| `city` | TEXT | CONSTANT | City for search context |
| `state` | TEXT | CONSTANT | State for search context |
| `domain` | TEXT | CONSTANT | Company domain |
| `company_domain` | TEXT | CONSTANT | Alternate domain field |
| `employees` | INTEGER | CONSTANT | Employee count (determines query variation) |
| `recon_name_titles` | TEXT (JSON) | VARIABLE | Raw name-title pairs from Process 300 (use recon_organized_people instead) |
| `recon_organized_people` | TEXT (JSON) | VARIABLE | Organized + classified entries from 300 Organizer — Gate A reads THIS |
| `recon_linkedin_people` | TEXT (JSON) | VARIABLE | LinkedIn URLs from Process 300 |
| `hunter_first_name` | TEXT | VARIABLE | Hunter.io candidate first name |
| `hunter_last_name` | TEXT | VARIABLE | Hunter.io candidate last name |
| `hunter_title` | TEXT | VARIABLE | Hunter.io candidate title |
| `hunter_email` | TEXT | VARIABLE | Hunter.io candidate email |
| `hunter_linkedin` | TEXT | VARIABLE | Hunter.io candidate LinkedIn |
| `hunter_email_pattern` | TEXT | CONSTANT | Email pattern from Hunter (structure) — READ only, not used to generate email (that's 201) |
| `vendor_email_pattern` | TEXT | CONSTANT | Email pattern from vendor data (structure) — READ only, not used to generate email (that's 201) |
| `readiness_tier` | TEXT | VARIABLE | Current slot readiness state |
| `has_name` | INTEGER | VARIABLE | 0 = empty, 1 = filled |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `slot_workbench` | `person_first_name`, `person_last_name`, `person_full_name`, `has_name`, `person_found_at`, `person_source`, `readiness_tier` | Any gate success |
| `slot_workbench` | `person_linkedin`, `has_linkedin`, `linkedin_found_at` | If LinkedIn found |

### Join Chain

```
slot_workbench.outreach_id
  → (self-contained — all reads and writes target this single table)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Skip Gate A/B to go straight to Startpage | Free before cheap. Always. Gate chain order is a CONSTANT. |
| Fill a slot without both first AND last name | A name requires two parts minimum. No first+last = not filled. |
| Run before Process 300 | 300 feeds `recon_name_titles` to Gate A. Run 300 first. |
| Write to Neon from this process | Neon is vault. D1 is workspace. SEED->WORK->PUSH lifecycle. |
| Call Process 201/202 from inside this script | Orchestrator handles downstream. 200 fills names only. |
| Write `person_email`, `has_email`, or `email_found_at` | **That is Process 201's job.** Process 200 fills name only. Email pattern is READ context, not a trigger to generate email. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| How many slots still need names? | `slot_workbench` | `has_name = 0` |
| Which slots are ready for email discovery? | `slot_workbench` | `has_name = 1 AND has_email = 0` |
| What was the source of a person fill? | `slot_workbench` | `person_source` |
| How many slots reached NAME_ONLY? | `slot_workbench` | `readiness_tier = 'NAME_ONLY'` |
| Which companies have small-company override? | `slot_workbench` | `employees < 25` |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2 + Mathematical Principle)

### Mathematical Definitions

```
DECISION:     P(x;θ) = 1  if  max_i [ C_i(x) / k_i ] ≤ 1  else 0
DIAGNOSTIC:   r(x) = [ C_1(x)/k_1, ..., C_n(x)/k_n ]
STABILITY:    ∀ t ∈ [1..N]: P(f^t(x);θ) = 1 AND var(r_i) ≤ σ_max
DOMESTICATE:  max(r(x)) ≤ α AND var(r_i) ≤ σ_max → stop decomposing
```

### Step-Level Comparators and Tolerances

**Gate A — Recon Parse (reads recon_organized_people from 300 Organizer):**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_1 | parse_match_rate (inverted: 1-rate) | Change | % of organized entries matching this slot_type | 0.50 (≥50% should match at least one slot) | 1 |

**Gate B — Hunter Promote:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_2 | promote_rate (inverted: 1-rate) | Change | % of hunter candidates successfully promoted | 0.85 (≥15% promotion rate) | 1 |

**Gate C — Startpage Search:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_3 | search_miss_rate | Change | % of searches returning no usable name | 0.60 (≤60% miss rate) | 1 |
| C_4 | captcha_rate | Change | % of searches hitting CAPTCHA | 0.05 (≤5%) | 1 |

**Writer:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_5 | write_failure_count | Thing | D1 write failures | ε_k | 1 |
| C_6 | total_fill_rate (inverted: 1-rate) | Change | % of input slots that got a name | 0.30 (≥70% fill across all gates) | 1 |

**Process-Level:** `P_200(x;θ) = 1 if max_i[C_i(x)/k_i] ≤ 1 for i ∈ {1..6}`

### Conditional Logic (Workbench State Routing)

Process 200 only runs on slots where the workbench says name is missing:

```sql
SELECT * FROM slot_workbench
WHERE has_name = 0 AND readiness_tier IN ('EMPTY', 'PATTERN_READY', 'HUNTER_READY')
ORDER BY outreach_id
```

After 200 fills names, downstream routing:
- `has_name = 1 AND has_email = 0` → Process 201 (email)
- `has_name = 1 AND has_linkedin = 0` → Process 202 (LinkedIn)
- 201 and 202 run in parallel.

### Constants (structure — never changes)

| Constant | Comparator | Primitive | k_i |
|----------|-----------|-----------|-----|
| 3 slot types: CEO, CFO, HR | slot_type_violation_count | Thing | ε_k |
| Gate chain order: A → B → C | gate_skip_count | Flow | ε_k |
| Title matching patterns (from Classifier taxonomy) | pattern_deviation_count | Thing | ε_k |
| slot_workbench as source of truth | non_workbench_read_count | Thing | ε_k |
| Gate A reads recon_organized_people (not raw recon_name_titles) | raw_read_count | Flow | ε_k |
| Employee threshold: <25 = "owner" query | threshold_deviation_count | Change | ε_k |
| 200 fills NAME only — never email (that's 201) | email_write_count | Change | ε_k |

### Variables (fill — changes every run)

- recon_organized_people entries (from 300 Organizer — different per company)
- hunter candidate data (may or may not exist per slot)
- person_first_name, person_last_name (THE fill — empty until gate succeeds)
- readiness_tier (200 sets NAME_ONLY; 201 sets REACHABLE)
- Search results from Startpage (Gate C only)
- CAPTCHA rate, fill rate per gate, cost per run
- Tolerance values k_i (calibrated through operation)

---

## 7. STOP CONDITIONS

_When to halt. Not optional. From Troubleshooting Loop (Bedrock §6) and Aviation Model (Bedrock §8)._

| Condition | Action |
|-----------|--------|
| CAPTCHA > 10% of Gate C searches | HALT — rotate proxy port, check DataImpulse credentials, wait and retry |
| Errors > 5% of total processed | HALT — check D1 connectivity, wrangler auth |
| No proxy credentials for Gate C | Skip Gate C, fill only from A/B |
| Fill rate plateaus for 3 consecutive runs | INVESTIGATE — recon data stale, Hunter exhausted, query patterns need refinement |
| All slots have has_name = 1 | DONE — nothing to process |
| Strike 3 on same failure | Troubleshoot/Train -> Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 010 (SEED) | Companies, slots, hunter data in D1 `slot_workbench` | DONE |
| Process 300 (Blog/Recon) | `recon_name_titles` and `recon_linkedin_people` populated in `slot_workbench` | DONE (store-names-v2 ran) |
| DataImpulse proxy | Residential proxy for Startpage queries | ACTIVE (Doppler creds) |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 201 (Email Discovery) | Slot with `has_name = 1` but `has_email = 0` |
| Process 202 (LinkedIn Discovery) | Slot with `has_name = 1` but `has_linkedin = 0` |
| Process 700 (Campaign Engine) | Slot with `readiness_tier = REACHABLE` |
| Process 500 (Talent Flow) | Filled slots for movement detection |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output. Not prose — run these._

```
1. python3 find-person-v3.py --limit 10 --dry-run
   -> Expected: 10 slots loaded, gate chain runs, DRY-RUN printed for each UPDATE, no D1 writes

2. python3 find-person-v3.py --limit 10
   -> Expected: slots filled, output JSONL created, D1 writes > 0

3. Verify Gate A fills:
   SELECT COUNT(*) FROM slot_workbench WHERE person_source = 'recon_300' AND has_name = 1
   -> Expected: > 0 if recon_name_titles data exists

4. Verify readiness tier changed:
   SELECT readiness_tier, COUNT(*) FROM slot_workbench WHERE has_name = 1 GROUP BY readiness_tier
   -> Expected: NAME_ONLY rows exist (Process 200 only sets NAME_ONLY — REACHABLE is 201's job)

5. Verify no orphan data:
   SELECT COUNT(*) FROM slot_workbench WHERE has_name = 1 AND person_first_name IS NULL
   -> Expected: 0

6. Check CAPTCHA rate in output JSONL:
   grep -c '"captcha"' output/find-person-v3-*.jsonl
   -> Expected: < 10% of total lines
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do empty slots exist in slot_workbench? Does recon_name_titles data exist?
2. **Flow:** Does the gate chain reach the slot? Does the UPDATE execute?
3. **Change:** Is has_name set to 1? Is readiness_tier updated? Is person_source recorded?

If any fails -> that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock §6).

---

## 10. ANALYTICS — The Dyno Sheet (Bedrock §2 + §5)

_The BUILD->OPERATE gate. No analytics passing tolerance = stays on the dyno. You don't flip to OPERATE by saying "it seems to work." The numbers say it works, or they don't._

_This section MUST be defined BEFORE build starts. No analytics spec -> no build authorization (BAR-187)._

_This is also the vendor scorecard. When you want to swap a vendor in the Snap-On Toolbox, pull the scorecard for the current one and say: beat these numbers._

### Process Metrics

_Define BEFORE build starts. These are the instruments on the dyno. Each metric is a constant (named, formatted). The value each run is the variable._

| Metric | Unit | First Run = Baseline | Target (after baseline) | Tolerance |
|--------|------|---------------------|------------------------|-----------|
| Gate A fill rate | % | BASELINE | [set after first run] | [set after baseline] |
| Gate B fill rate | % | BASELINE | [set after first run] | [set after baseline] |
| Gate C fill rate | % | BASELINE | [set after first run] | [set after baseline] |
| Overall hit rate | % | BASELINE | [set after first run] | [set after baseline] |
| CAPTCHA rate | % | BASELINE | < 10% | > 10% = HALT |
| LinkedIn capture rate | % | BASELINE | [set after first run] | [set after baseline] |
| Cost per fill (Gate C) | $/slot | BASELINE | [set after first run] | [set after baseline] |

### Tool Scorecard (per Snap-On sub-hub vendor)

_Track per vendor so you can benchmark swaps. Tool is constant, vendor is variable, scorecard measures the variable._

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| — | DataImpulse (proxy) | — | — | — | — | No runs yet |
| — | Startpage (search) | — | — | — | — | No runs yet |

### Sigma Tracking (Bedrock §2)

_After 3+ runs, track whether each metric is tightening, flat, or expanding._

| Metric | Run 1 | Run 2 | Run 3 | Trend | Action |
|--------|-------|-------|-------|-------|--------|
| Gate A fill rate | — | — | — | — | — |
| Gate B fill rate | — | — | — | — | — |
| Gate C fill rate | — | — | — | — | — |
| Overall hit rate | — | — | — | — | — |
| CAPTCHA rate | — | — | — | — | — |

_Tightening = real constant, process is stabilizing. Flat = phantom, something isn't learning. Expanding = broken, something upstream changed._

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs + **auditor sign-off** |
| OPERATE | REPAIR | Any metric outside tolerance |
| REPAIR | OPERATE | Fix applied + metric back within tolerance + **auditor verification** |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same failure pattern 3 times at fleet level -> AD |

_The builder cannot certify its own work. The auditor MUST be a different engine than the builder. (Bedrock §8)_

---

## 11. EXECUTION TRACE (During BUILD)

_Append-only record of what happened during build/execution. This is NOT the logbook — the logbook is created only after auditor certification. This is the build journal that the auditor reviews._

_Every run, every step, every result gets traced here. The auditor reads this to decide: certify or reject._

### Entry Format (per step, per run)

| Field | Description | Format | Required |
|-------|-------------|--------|----------|
| trace_id | Unique entry identifier | UUID | Yes |
| run_id | Which execution run this belongs to | UUID (one per goal/batch) | Yes |
| step | What was attempted | Station ID or action name | Yes |
| target | Expected outcome (defined in §10 metrics) | Text — measurable | Yes |
| actual | What happened | Text — measurable | Yes |
| delta | Target vs actual | Number or text — the gap | Yes |
| status | Step outcome | done / failed / skipped | Yes |
| error_code | If failed — machine-readable error type | Text or null | If failed |
| error_message | If failed — human-readable description | Text or null | If failed |
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
| learnings | What was new — feeds to LBB |

### Rules

- **Append-only.** No edits. No deletions. Immutable.
- **Every step gets a trace entry.** No step executes without logging.
- **Trace exists during BUILD.** This is NOT the certified logbook.
- **Auditor reviews the trace** to decide certification.
- **Trace persists after certification** — it becomes evidence inside the logbook's birth certificate.

---

## 12. LOGBOOK (After Certification Only)

_The aircraft's legal identity. Created ONLY when the auditor certifies the process (BUILD -> OPERATE). (Bedrock §8, logbook_schema.yaml)_

**No logbook during BUILD.** The execution trace (§11) is the build journal. The logbook is born when the auditor signs off.

### Rules (from logbook_schema.yaml)

1. No logbook until aircraft is certified (auditor sign-off on BUILD)
2. First entry is always the **birth certificate** (certification record)
3. Append-only. No edits. No deletions. Immutable.
4. Every entry must have all required fields. Incomplete entries rejected.
5. Mechanic must log what they READ before starting (context_loaded)
6. Auditor reviews logbook entries, not source code.
7. The builder CANNOT be the auditor. Different engine required.

### Birth Certificate (first entry — created by auditor at certification)

| Field | Value |
|-------|-------|
| heir_ref | Full HEIR record for this process |
| orbt_entered | BUILD |
| orbt_exited | OPERATE |
| action | "Process certified — airworthiness confirmed" |
| authority | "Auditor certification per Tier 0 gate stack" |
| gates_passed | { imo: true, ctb: true, circle: true } |
| checklist_type | build_checklist |
| checklist_items | Full build checklist with all items PASS |
| execution_trace_ref | Link to §11 trace (evidence the auditor reviewed) |
| signed_by | Auditor agent (MUST be different engine than builder) |
| signed_at | Certification timestamp |

### Subsequent Entries (during OPERATE, REPAIR, TROUBLESHOOT/TRAIN)

| Field | Description | Required |
|-------|-------------|----------|
| heir_ref | HEIR reference — hub_id, sub_hub, component | Yes |
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

_Strike tracking at FLEET level, not per-goal. The same failure pattern appearing across multiple goals/runs triggers escalation. (Bedrock §6, §8)_

### Failure Pattern Registry

| Pattern ID | Station | Error Code | First Seen | Occurrences | Goals Affected | Strike Count | Status |
|-----------|---------|-----------|-----------|-------------|---------------|-------------|--------|
| FP-001 | find-person-v3 | SCHEMA_MISMATCH | 2026-04-01 | 1 | v1 rewrite | 0 | RESOLVED |

_v1 used old schema (people_company_slot, people_people_master). Schema migrated to slot_workbench. Rewrote as v3 against slot_workbench._

### Strike Rules

- **Strike 1:** Repair. Fix at source. Log it.
- **Strike 2:** Repair with scrutiny. Was root cause actually found?
- **Strike 3:** **STOP.** Troubleshoot/Train. The problem isn't a broken part — it's a broken understanding.

### Airworthiness Directive (Strike 3 output)

_When strike 3 fires, the fix goes to ALL processes, not just the one that failed. This updates the template, not just one file._

| Field | Value |
|-------|-------|
| AD Number | AD-[YYYY]-[NNN] |
| Failure Pattern | FP-[NNN] — [description] |
| Root Cause | [from Troubleshooting Loop §6] |
| Fix Applied | [what changed] |
| Scope | ALL processes / [specific silo] / [specific station] |
| Template Updated | Yes / No — if Yes, what section |
| Issued By | [mechanic + auditor sign-off] |
| Issued At | [timestamp] |

**AD issuance requires:**
1. Root cause identified (Troubleshooting Loop §6 complete)
2. Fix tested on the failing process
3. Fix verified by auditor (different engine)
4. Template updated if the fix is structural
5. All affected processes notified/updated

---

## 14. SESSION LOG

_Every session that touches this process. Links to LBB for detail._

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| 2026-03-29 | Initial PROCESS.md created (v1 format) | none |
| 2026-04-01 | Full rewrite to v3 against slot_workbench, C&V audit, gate chain documented | none |
| 2026-04-01 | Rewritten to PROCESS_TEMPLATE v4.0.0 (14 sections) | none |
| 2026-04-02 | Math engine added: 6 comparators (C_i/k_i per gate), P(x;θ), conditional logic SQL, Gate A updated to read recon_organized_people | a65dd7b1 |
| 2026-04-02 | Funnel built (5 layers). L1 CEO promote: 5,057. L2 bucket match: 2. L3 Hunter: 129. L4 slug derive: 2,021. Total free fills: 7,209. | 5db86e97 |
| 2026-04-02 | find-person-v3.py Gate A updated to read recon_organized_people, Pass 3 REJECT promotion for small CEO slots, employees param added | 5db86e97 |
| 2026-04-02 | Hunter broad match: 55 fills. DOL 5500 signer match: 1,979 fills (1,000 CFO + 963 HR). Management page scraper test: 30 fills from 100 companies. | 5db86e97 |
| 2026-04-02 | DATA GAP FOUND: 29K empty slots with 95% data available. 69K about_urls never scraped. 175K Hunter contacts barely matched. 7.5K recon_emails unused. 140K DOL signers never SEEDed. BAR-197 created. | 54f035e9 |
| 2026-04-02 | Branch 1 database joins running: Hunter seniority→slot mapping + recon_emails→person_email + vendor_people. All structured sources, zero cost. | 54f035e9 |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-04-02 |
| Version | 5.0.0 |
| Template Version | 4.0.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md (parent repo — Barton-Processes inherits) |
| Logbook Schema | law/logbook_schema.yaml |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md |
| Data Flow | factory/outreach/200-people-worker/DATA_FLOW.md |

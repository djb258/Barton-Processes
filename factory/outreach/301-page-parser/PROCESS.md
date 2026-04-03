# PROCESS: Management Page Parser
## Fetches leadership/team pages discovered by Process 300, parses ALL names + titles, fills CEO/CFO/HR slots — one page, three fills
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-301 |
| Name | Management Page Parser |
| Business Silo | svg-agency |
| CTB Position | factory/outreach/301-page-parser (LEAF) |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed |
| BAR Reference | BAR-197 |
| Deployed URL | local Python script |
| Cron | Manual / after Process 300 completes |
| Runtime | Python 3 + curl_cffi |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Process 300 discovered 69,174 leadership page URLs. It stored the address but never opened the door. Those pages list the CEO, CFO, HR director by name and title. Without this process, we're searching Startpage for names that are already published on the company's own website.

One page fetch fills up to 3 slots. That's 3x the fill rate per fetch compared to Process 200 (which searches for one person at a time). This process sits between 300 (discovery) and 200 (fallback search). What 301 fills, 200 doesn't need to search for.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — A company in slot_workbench where `about_url IS NOT NULL`.
2. **"How do we get it?"** — Fetch the about_url page. Break it into pieces. Identify each piece. Build a key for that page. Quality gate rejects bad data. Organizer maps identified pieces into our structured table. Unidentified pieces stored as "unidentified" — nothing gets thrown away.

### Input
- `slot_workbench.about_url` — the page URL (discovered by Process 300)
- `slot_workbench.company_name` — for validation
- `slot_workbench.outreach_id` — company key
- One fetch per company. Extract EVERYTHING, not just CEO/CFO/HR.

### Middle

Each step is its own IMO with comparators C_i, tolerances k_i, and decision function P(x;θ).

| Step | Name | Input | What Happens | Output | Tool Used |
|------|------|-------|-------------|--------|-----------|
| 1 | **FETCHER** | about_url per company | Fetch the page via curl_cffi. Try direct first, DataImpulse proxy as fallback. One fetch per company. Store raw HTML. | Raw HTML content + fetch_status | curl_cffi + DataImpulse proxy |
| 2 | **DECOMPOSER** | Raw HTML | Break the page into individual pieces. Every text block, heading, link, image caption, list item, table cell — each becomes a separate element with its position in the DOM. Strip scripts/styles but preserve ALL content. Nothing gets thrown away. | List of elements: [{position, tag_type, text_content, href, parent_context}] | HTML parsing |
| 3 | **KEY BUILDER** | Decomposed elements | Identify each element. What IS this piece? Apply classification rules: person name pattern? Title keyword? Email format? Phone format? LinkedIn URL? Company description? Navigation? Unknown? Each element gets a classification. Unidentified elements are classified AS "unidentified" — they are NOT discarded. | Page key: [{position, tag_type, text_content, classification, confidence}] | Pattern matching + Title Classifier |
| 4 | **QUALITY GATE** | Page key (all elements) | Validate identified elements. Is the "person name" actually a person? (C&V three questions.) Is the "title" actually a job title? Cross-check: does the company name on the page match our company_name? Bad identifications get reclassified as "unidentified" — still stored, just not promoted. | Validated key: same structure, classifications confirmed or downgraded | C&V rules |
| 5 | **ORGANIZER** | Validated key | Read the key. Map identified elements into our defined output columns. person_name → PG-01. person_title → PG-02. Email → PG-04. LinkedIn → PG-03. Unidentified elements → stored in unidentified column. Every element on the page gets stored — identified OR unidentified. | Structured records in page_contacts table | Column mapping |
| 6 | **SLOT FILLER** | Structured page_contacts records | Query page_contacts for this company. Match classified titles to slot_types (CEO/CFO/HR). Fill workbench slots from the structured table. This is just a VIEW — the page_contacts table is the source of truth. | Workbench slots updated | D1 write |
| 7 | **RECALC** | All written slot_ids | Run recalc_tier on all slots touched. | Tiers updated from actual state | recalc_tier.py |

### The Key Concept

Every page has its own format. The format is the variable. But once you identify what each piece IS on that page, you've built a key for that page. The key maps that page's format to our format. Store the key — next time you visit the page, the key already exists. No re-identification needed.

**What gets stored:**
- Identified elements → mapped to output columns (PG-01 through PG-10)
- Unidentified elements → stored as "unidentified" with raw text content
- The key itself → stored per page URL for reuse

**Nothing gets thrown away. Today's unidentified is tomorrow's identified when a better tool arrives.**

#### Step-Level Comparators and Tolerances

**Step 1 — FETCHER:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_1 | fetch_failure_rate | Flow | % of URLs returning error/timeout/404 | 0.20 (≤20% failure) | 1 |
| C_2 | fetch_latency_p95 | Flow | 95th percentile fetch time in ms | 15000 (≤15s) | 1 |

**Step 2 — PARSER:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_3 | no_names_rate | Change | % of successfully fetched pages yielding zero names | 0.40 (≤40% — some about pages don't list people) | 1 |
| C_4 | names_per_page_avg | Thing | Average names extracted per page | 0.33 (inverted: k_4 = 1/target, pass if avg ≥ 3 names/page) | 1 |

**Step 3 — CLASSIFIER:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_5 | reject_rate | Change | % of parsed names classified as REJECT (no title match) | 0.50 (≤50% — many names won't have matching titles) | 1 |

**Step 4 — WRITER:**

| C_i | Name | Primitive | Measures | Initial k_i | Phase |
|-----|------|-----------|----------|-------------|-------|
| C_6 | write_failure_count | Thing | D1 write failures | ε_k | 1 |
| C_7 | slots_filled_per_company_avg | Change | Average slots filled per company processed | 0.67 (inverted: pass if avg ≥ 1.5 fills/company) | 1 |

**Process-Level:**
```
P_301(x;θ) = 1  if  max_i[C_i(x)/k_i] ≤ 1  for i ∈ {1..7}
r(x) = [C_1/k_1, ..., C_7/k_7]   (diagnostic vector)
```

### Output
- `slot_workbench.person_first_name` + `person_last_name` filled for matched slots
- `slot_workbench.person_source` = 'page_parser_301'
- `slot_workbench.person_linkedin` if LinkedIn URL found on page
- Readiness tiers recalculated by recalc_tier
- JSONL output file with full parse audit trail

### Circle (Bedrock §5)
Slots filled by 301 reduce the workload for Process 200. Sigma tracking on fetch_failure_rate and no_names_rate identifies pages that need different parsing strategies. If no_names_rate > 40% for 3 runs, investigate: are these really leadership pages? Should about_url classification be tighter in Process 300?

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | slot_workbench (read about_url + company, write person data) |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| curl_cffi | Library | Free | None | Chrome131 impersonation for page fetches |
| DataImpulse | Proxy | Cheap ($1/GB) | PROXY_USER, PROXY_PASS | Residential proxy for page fetches |
| Title Classifier | Snap-On Tool | Free | None | Classify parsed titles → CEO/CFO/HR bucket |
| recalc_tier.py | Script | Free | None | Recalculate tiers after writes |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_USER | imo-creator | dev | DataImpulse proxy |
| PROXY_PASS | imo-creator | dev | DataImpulse proxy |

**Tool Priority (Well Drinks First):**
1. Direct page fetch without proxy — try first, many company pages don't block
2. DataImpulse proxy — fallback if direct fetch fails or returns CAPTCHA

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| slot_workbench | about_url, company_name, slot_type, has_name, outreach_id | outreach_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| slot_workbench | person_first_name, person_last_name, person_full_name, person_source, has_name, person_found_at | Step 4 — on classified match |
| slot_workbench | person_linkedin, has_linkedin, linkedin_found_at | Step 4 — if LinkedIn found on page |

### Forbidden Paths

| Action | Why |
|--------|-----|
| Set readiness_tier | Tier is computed by recalc_tier, not by this process |
| Write person_email | That's Process 201's job |
| Search Startpage | That's Process 300 (discovery) and 200 Gate C (fallback) |
| Scrape LinkedIn directly | ToS violation — only parse /in/ URLs found on company pages |
| Fetch pages not in about_url | This process reads the URL from the workbench, doesn't discover new ones |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2 + Mathematical Principle)

### Mathematical Definitions

```
DECISION:     P(x;θ) = 1  if  max_i [ C_i(x) / k_i ] ≤ 1  else 0
DIAGNOSTIC:   r(x) = [ C_1(x)/k_1, ..., C_n(x)/k_n ]
STABILITY:    ∀ t ∈ [1..N]: P(f^t(x);θ) = 1 AND var(r_i) ≤ σ_max
```

### Constants (structure — never changes)

| Constant | Comparator | Primitive | k_i |
|----------|-----------|-----------|-----|
| One fetch per company (not per slot) | multi_fetch_count | Flow | ε_k |
| 4-step process: Fetch → Parse → Classify → Write | step_skip_count | Flow | ε_k |
| Title Classifier maps title → slot_type | classification_deviation | Change | ε_k |
| about_url is the input — no new URL discovery | url_discovery_count | Thing | ε_k |
| Does not set readiness_tier | tier_set_count | Change | ε_k |
| Does not write person_email | email_write_count | Change | ε_k |
| Try direct fetch before proxy | proxy_first_count | Flow | ε_k |

### Variables (fill — changes every run)
- Which companies have empty slots + about_url (changes as other processes fill)
- Page HTML content (different every company)
- How many names parsed per page
- Which names match which slot types
- Fetch success/failure per URL
- Tolerance values k_i (calibrated through operation)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Fetch failure rate > 30% | HALT — check proxy, check URL quality |
| No names found on 10 consecutive pages | HALT — parser may need updating for new HTML patterns |
| D1 write errors > 1% | HALT — check connectivity |
| All about_url companies have has_name = 1 | DONE — nothing to process |
| Strike 3 on same failure | Troubleshoot/Train → AD |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 300 (Recon) | about_url populated in slot_workbench | OPERATE |
| Process 010 (SEED) | Companies + slots in D1 | OPERATE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 200 (Find Person) | Slots NOT filled by 301 — 200 handles the remainder |
| Process 201 (Find Email) | person_first_name + person_last_name (for email pattern generation) |
| Process 202 (Find LinkedIn) | person_first_name + person_last_name (for LinkedIn slug matching) |

---

## 9. SMOKE TEST

```
1. python3 src/page-parser.py --limit 10 → expected: 10 companies fetched, names parsed
2. Check output JSONL: names + titles extracted per page
3. SELECT person_source, COUNT(*) FROM slot_workbench WHERE person_source = 'page_parser_301' → expected: > 0
4. Verify recalc_tier ran: no misclassified tiers on touched slots
```

**Three Primitives Check:**
1. **Thing:** Do the about_url pages exist? Do they return HTML?
2. **Flow:** Does the HTML reach the parser? Do parsed names reach the writer? Do writes reach D1?
3. **Change:** Are names correctly extracted? Are titles correctly classified to slot types?

---

## 10. ANALYTICS — The Dyno Sheet (Bedrock §2 + §5 + Mathematical Principle)

### Process Metrics (as Comparators)

| Metric | C_i | Primitive | Unit | Baseline | k_i (tolerance) | Phase |
|--------|-----|-----------|------|----------|-----------------|-------|
| Fetch failure rate | C_1 | Flow | % | TBD | 0.20 (≤20%) | 1 |
| Fetch latency p95 | C_2 | Flow | ms | TBD | 15000 (≤15s) | 1 |
| No names found rate | C_3 | Change | % | TBD | 0.40 (≤40%) | 1 |
| Names per page avg | C_4 | Thing | count | TBD | ≥3 | 1 |
| Reject rate | C_5 | Change | % | TBD | 0.50 (≤50%) | 1 |
| Write failures | C_6 | Thing | count | TBD | ε_k | 1 |
| Slots filled per company | C_7 | Change | avg | TBD | ≥1.5 | 1 |

### Sigma Tracking

| Metric | Run 1 | Run 2 | Run 3 | Trend | Action |
|--------|-------|-------|-------|-------|--------|
| Fetch failure rate | — | — | — | BASELINE | — |
| No names rate | — | — | — | BASELINE | — |
| Slots/company | — | — | — | BASELINE | — |

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs + auditor sign-off |
| OPERATE | REPAIR | Any metric outside tolerance |
| REPAIR | OPERATE | Fix applied + metric back within tolerance + auditor verification |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same failure pattern 3 times → AD |

---

## 11. EXECUTION TRACE (During BUILD)

_Append-only record. Auditor reads this to certify or reject._

(No runs yet — BUILD state)

---

## 12. LOGBOOK (After Certification Only)

_Created ONLY when the auditor certifies BUILD → OPERATE._

(Not yet certified)

---

## 13. FLEET FAILURE REGISTRY & STRIKE TRACKING

| Pattern ID | Station | Error Code | First Seen | Occurrences | Strike Count | Status |
|-----------|---------|-----------|-----------|-------------|-------------|--------|
| (none yet) | | | | | | |

---

## 14. SESSION LOG

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| 2026-04-03 | PROC-301 created via 060 altitude descent. Station added to lines.ts between 300-recon and 200-people. 14-section PROCESS.md, heir.yaml, CLAUDE.md created. 7 comparators defined. | 54f035e9 |
| 2026-04-03 | Key Builder approach designed: decompose page → identify each element into defined buckets (KB-01 through KB-07, KB-99 unidentified) → quality gate → organize → store ALL. Unidentified stored, not discarded. Key reusable for Talent Flow monthly checks. | pending |
| 2026-04-03 | Key Builder constants defined: key_builder_constants.py — 7 buckets, ~60 position constants, strict name rules (reject navigation/company words). Snap-On Tool — reusable by any page-parsing process. | pending |
| 2026-04-03 | First run: 100 pages. 89 fetched, 84 with people (94%), 4,841 people found. Identification rate 39% — rules too loose, "Edit Profile" and "Leadership Team" passing as person names. Tighter guard rails built. Re-run needed. | pending |
| 2026-04-03 | KEY INSIGHT (Dave): Each page gets its own key. The key maps that page's format to our format. Store the key per URL — reusable. One-time cost to build, free to query forever. Talent Flow checks = fetch page + apply key + diff values. | pending |
| 2026-04-03 | KEY INSIGHT (Dave): Key Builder IS a Snap-On Tool. If current rules don't identify enough, use sub-hub 27 (Vendor Scout) to find a better driver. Then re-run Bedrock on unidentified pile. Funnel pattern — each pass tightens. | pending |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-03 |
| Last Modified | 2026-04-03 |
| Version | 1.0.0 |
| Template Version | 4.0.0 |
| Governing Engine | imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md |
| Logbook Schema | law/logbook_schema.yaml |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md |

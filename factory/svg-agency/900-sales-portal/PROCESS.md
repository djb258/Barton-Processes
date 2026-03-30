# PROCESS: Sales Portal
## Prospect-facing sales cycle portal — 4 meetings from Fact Finder through Financials, driven by outreach intelligence.
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-900 |
| Name | Sales Portal |
| Business Silo | svg-agency |
| CTB Position | factory/svg-agency/900-sales-portal |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed |
| BAR Reference | none |
| Deployed URL | sales-portal-900.svg-outreach.workers.dev (production: app.svgagency.com/sales/) |
| Cron | none |
| Runtime | CF Worker |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Without the Sales Portal, the entire outreach pipeline has no conversion surface. Processes 010-800 generate intelligence, contacts, content signals, and BIT scores, but none of that converts to revenue without a structured sales cycle. This process is the terminal output of the outreach engine — it renders the intelligence as a branded, prospect-specific experience across 4 meetings that walk a prospect from Fact Finder through quotes to close.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** — User navigates to app.svgagency.com/sales/:slug/:meeting
2. **"How do we get it?"** — Resolve slug to sales_id from D1 sales_state, query meeting-specific D1 table, render HTML

### Input
- HTTP request: `GET /sales/:slug/:meeting` (page render) or `POST /sales/:slug/meeting1/save` (form submission)
- Slug resolves to `sales_id` via `sales_state.slug` index
- Meeting 1 pre-populates from `outreach_snapshot` (seeded from 5 outreach sub-hubs via `sovereign_id`)
- Meetings 2-4 read from their respective D1 tables (`sales_insurance`, `sales_systems`, `sales_quotes`)

### Middle
| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | HTTP request with `:slug` and `:meeting` | Parse path segments, validate meeting name | Slug + meeting identifier | CF Worker router |
| 2 | Slug | Query `sales_state` by slug | Sales context (sales_id, sovereign_id, current_phase, legal_name) | D1 query |
| 3a (Meeting 1 GET) | sales_id | Query `outreach_snapshot` + `sales_factfinder` | Pre-populated form HTML (read-write) | D1 query |
| 3b (Meeting 1 POST) | sales_id + form body | Validate and INSERT/UPDATE `sales_factfinder` | Success/error JSON | D1 write |
| 3c (Meeting 2 GET) | sales_id | Query `sales_insurance` (Monte Carlo results — future) | Read-only presentation HTML | D1 query |
| 3d (Meeting 3 GET) | sales_id | Query `sales_systems` | Read-only presentation HTML | D1 query |
| 3e (Meeting 4 GET) | sales_id | Query `sales_quotes` by benefit_type + carrier | Read-only financials HTML | D1 query |
| 4 | Body HTML from step 3 | Wrap in branded layout template | Full HTML page | renderPage() |

### Output
- HTML pages served to browser — no downstream process consumes this output
- Meeting 1 form data persisted to `sales_factfinder` in D1
- Phase progression tracked in `sales_state.current_phase`: factfinder -> insurance -> systems -> financials -> closed

### Circle (Bedrock S5)
- Meeting 1 form submission writes to `sales_factfinder` which becomes the input for Meeting 2 (insurance education uses validated company data)
- Phase progression in `sales_state` gates which meetings are accessible
- Error tables capture validation failures per meeting — feeds back into ORBT state assessment
- Terminal process: no downstream consumers. The circle closes at revenue conversion (closed phase).

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches._

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| sales-portal-900 (D1) | D1 | TODO: not created | READ/WRITE | sales_state, outreach_snapshot, sales_factfinder, sales_insurance, sales_systems, sales_quotes + error tables |
| Neon (outreach vault) | NEON_URL | production | READ ONLY | Outreach sub-hub data for snapshot seeding (company_target, dol, people, blog, bit_scores) |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| Cloudflare Workers | Runtime | Free | none | Serves HTTP, executes routing + rendering |
| Cloudflare D1 | Database | Free | D1 binding | Working tables for all sales data |
| Neon PostgreSQL | Database | Cheap | NEON_URL (Doppler) | Read-only source for outreach snapshot seeding |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| NEON_URL | sales-portal-900 | production | Outreach snapshot seeding (future — reads 5 sub-hubs) |

**Tool Priority (Well Drinks First):**
1. Free data already in D1 (sales working tables) — all meeting rendering
2. Free external fetches (CF Worker fetch) — not currently used
3. Cheap integrations (Neon read) — outreach snapshot seeding only
4. Top shelf — none required

---

## 5. OSAM — Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins._

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| sales_state | Spine: sales_id, sovereign_id, slug, current_phase, legal_name | sales_state.slug (resolve), sales_state.sales_id (join) |
| outreach_snapshot | Meeting 1 pre-population: company profile, DOL, contacts, blog, BIT | outreach_snapshot.sales_id |
| sales_factfinder | Meeting 1 saved form data, Meeting 2 input | sales_factfinder.sales_id |
| sales_insurance | Meeting 2 Monte Carlo results + presentation metadata | sales_insurance.sales_id |
| sales_systems | Meeting 3 systems education presentation metadata | sales_systems.sales_id |
| sales_quotes | Meeting 4 quotes by benefit_type + carrier with rates | sales_quotes.sales_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| sales_factfinder | Validated form data from Meeting 1 | POST /sales/:slug/meeting1/save |
| sales_state | Phase progression (current_phase update) | After meeting completion |
| sales_factfinder_errors | Validation failures on Meeting 1 form | POST with invalid data |
| sales_insurance_errors | Meeting 2 rendering errors | GET meeting2 failures |
| sales_systems_errors | Meeting 3 rendering errors | GET meeting3 failures |
| sales_quotes_errors | Meeting 4 rendering errors | GET meeting4 failures |

### Join Chain

```
sales_state.sales_id (SPINE)
  -> outreach_snapshot.sales_id (1:1, seeded from outreach)
  -> sales_factfinder.sales_id (1:1, Meeting 1 form data)
  -> sales_insurance.sales_id (1:1, Meeting 2 Monte Carlo)
  -> sales_systems.sales_id (1:1, Meeting 3 systems)
  -> sales_quotes.sales_id (1:N, Meeting 4 quotes by benefit_type)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Write to outreach_snapshot after initial seed | Read-only after seed — outreach data is a frozen point-in-time snapshot |
| Direct write to Neon from this worker | Neon is vault only. D1 is the working layer. SEED->WORK->PUSH lifecycle. |
| Skip phase progression (jump from meeting1 to meeting4) | Phase gates enforce sales cycle sequence |
| Modify outreach sub-hub data | This process is a consumer, not an owner. Sovereign silo boundary. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| What phase is this prospect in? | sales_state | current_phase |
| What's the prospect's company profile? | outreach_snapshot | company_name, industry, employees, state |
| What did the fact finder capture? | sales_factfinder | all columns |
| What are the Monte Carlo projections? | sales_insurance | projected_claims, confidence_low, confidence_high |
| What quotes exist for this prospect? | sales_quotes | benefit_type, carrier, rate_ee/es/ec/fam, annual_cost |
| What's the prospect's renewal month? | outreach_snapshot | renewal_month |
| Who are the decision makers? | outreach_snapshot | ceo_name, cfr_name, hr_name |

---

## 6. CONSTANTS & VARIABLES (Bedrock S2)

### Constants (structure -- never changes)

_What is fixed regardless of what data flows through._

- **4 meetings** = 4 phases of the sales cycle: Fact Finder, Insurance Education, Systems Education, Financials
- **Meeting 1 is read-write; Meetings 2-4 are read-only** — only the Fact Finder accepts user input
- **Phase sequence**: factfinder -> insurance -> systems -> financials -> closed — no skipping, no reordering
- **sales_id is the spine join key** for all meeting sub-hub tables
- **sovereign_id links back to outreach** — the bridge between sales silo and outreach silo
- **outreach_snapshot is frozen after seed** — point-in-time copy, never updated from outreach
- **1 CANONICAL + 1 ERROR table per sub-hub** — CQRS pattern on every meeting table
- **URL structure**: /sales/:slug/:meeting — slug resolves to sales_id, meeting selects the page
- **D1 is working layer, Neon is vault** — no direct Neon writes from this worker

### Variables (fill -- changes every run)

_The values that fill the constants. Different every execution._

- Which prospect (slug) is being viewed
- Which meeting page is requested
- What data populates the outreach_snapshot for this prospect
- What form values the user enters in Meeting 1
- What Monte Carlo simulation results appear in Meeting 2 (future)
- What quotes by benefit_type + carrier appear in Meeting 4
- Current phase of the sales cycle for this prospect

---

## 7. STOP CONDITIONS

_When to halt. Not optional._

| Condition | Action |
|-----------|--------|
| Can't answer two-question intake | HALT -- process isn't defined |
| Slug does not resolve to a sales_id | Return 404 -- prospect not found |
| sales_state.current_phase doesn't match requested meeting | Gate check -- deny access to future meetings |
| outreach_snapshot is empty for Meeting 1 | HALT -- snapshot seeding not yet implemented, cannot pre-populate |
| Meeting 1 POST fails validation | Write to sales_factfinder_errors, return 400 |
| D1 query returns unexpected error | Log to error table, return 500 |
| Monte Carlo engine not available (Meeting 2) | Show placeholder -- future dependency, not yet built |
| Strike 3 on same failure | Troubleshoot/Train -> produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| D1 database (sales-portal-900) | Working tables for all sales data | PENDING -- not created |
| Process 200 (People Worker) | Contacts (CEO/CFO/HR) for outreach_snapshot | DONE |
| Outreach sub-hubs (Neon) | company_target, dol, people, blog, bit_scores data | DONE (data exists) |
| Snapshot seeding mechanism | Copies 5 sub-hub data into outreach_snapshot by sovereign_id | PENDING -- not built |
| Monte Carlo simulation engine | Produces projections for Meeting 2 | PENDING -- not built |
| Auth / access control | Restrict portal access to authorized users | PENDING -- no auth |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| None | Terminal process -- renders HTML to browser. No downstream data consumers. |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output._

```
1. GET /health -> expected: {"process":"PROC-SALES-PORTAL","number":900,"status":"ok"}
2. GET / -> expected: 200 with route documentation text
3. GET /sales/nonexistent/meeting1 -> expected: 404 "Prospect not found"
4. GET /sales/valid-slug/meeting1 -> expected: 200 HTML with pre-populated Fact Finder form
5. POST /sales/valid-slug/meeting1/save with valid JSON body -> expected: 200 {"success":true}
6. POST /sales/valid-slug/meeting1/save with invalid body -> expected: 400 with error
7. GET /sales/valid-slug/meeting2 -> expected: 200 HTML (Insurance Education page)
8. GET /sales/valid-slug/meeting3 -> expected: 200 HTML (Systems Education page)
9. GET /sales/valid-slug/meeting4 -> expected: 200 HTML (Financials with quotes)
10. Query D1: SELECT current_phase FROM sales_state WHERE slug = 'valid-slug' -> expected: phase value
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** D1 database exists? All 6 canonical + 4 error tables exist? Worker deployed?
2. **Flow:** Slug resolves to sales_id? outreach_snapshot seeded? Form data writes to sales_factfinder?
3. **Change:** Phase progresses correctly? Form validation catches bad data? HTML renders with correct prospect data?

If any fails -> that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock S6).

---

## 10. LOGBOOK

_Append-only. Read first, write last. No exceptions. (Bedrock S8)_

### 2026-03-29 -- Process documentation created

**ORBT:** BUILD
**Trigger:** Documentation creation for Process 900
**Records processed:** 0
**Errors:** 0
**Tools used:** None -- documentation only
**Result:** PROCESS.md created. D1 schema defined (001_d1_sales_tables.sql). Worker code scaffolded (index.ts, 4 page renderers, resolver, layout template). No deployment yet.
**Learnings:** BIT scoring (Process 600) is retired -- bit_score/bit_tier columns in outreach_snapshot exist but source is deprecated. Snapshot seeding mechanism is the critical missing piece before this process can operate.
**ORBT after:** BUILD

---

## 11. KNOWN ISSUES & STRIKE TRACKING

_The error history. Append-only -- never delete a resolved issue._

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | D1 database not created | BUILD phase -- wrangler d1 create not yet run | Run `wrangler d1 create sales-portal-900`, update database_id in wrangler.toml | 0 |
| 2 | 2026-03-29 | Snapshot seeding not implemented | No mechanism to copy 5 outreach sub-hubs into outreach_snapshot | Build seeding endpoint or cron that queries Neon by sovereign_id and INSERTs to D1 | 0 |
| 3 | 2026-03-29 | Monte Carlo engine not built | Future dependency -- Meeting 2 has no simulation data | Build Monte Carlo simulation engine (separate process) | 0 |
| 4 | 2026-03-29 | No auth / access control | BUILD phase -- portal is open to anyone with the URL | Implement auth before OPERATE (token, session, or edge auth) | 0 |
| 5 | 2026-03-29 | BIT scoring retired | Process 600 deprecated -- bit_score columns orphaned | Columns remain in schema but will not be populated. Remove or repurpose when snapshot seeding is built. | 0 |

**Strike 3 -> Troubleshoot/Train -> Airworthiness Directive.**
AD goes to ALL processes, not just this one. Update the template, not just this file.

---

## 12. SESSION LOG

_Every session that touches this process. Links to imo-brain for detail._

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | PROCESS.md created from template v2.0.0. Documented full IMO, OSAM, C&V, dependencies, smoke test. | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | factory/svg-agency/DATA_FLOW.md |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

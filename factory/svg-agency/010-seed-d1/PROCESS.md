# PROCESS: SVG D1 SEED
## Copies the company footprint from Neon vault into D1 workspace for every company inside an agent's coverage zone
### Status: OPERATE
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-010 |
| Name | SVG D1 SEED |
| Business Silo | svg-agency |
| CTB Position | factory/svg-agency/010-seed-d1 |
| ORBT | OPERATE |
| Strikes | 0 |
| Last Deployed | 2026-03-26 |
| BAR Reference | BAR-52 |
| Deployed URL | https://lcs-hub.svg-outreach.workers.dev (SEED endpoints) |
| Cron | Manual (run before any SVG process operates) |
| Runtime | CF Worker (lcs-hub) via Hyperdrive to Neon |

---

## 2. WHY THIS EXISTS

Without this process, D1 is empty. Every SVG process (100 LCS Pipeline, 200 People Worker, 300 Blog Worker — all of them) reads from D1. If the SEED didn't run, nothing downstream works.

The agent + ZIP + radius is the gate that controls the entire flow. No agent assignment, no SEED, no downstream processes. Nothing gets a footprint, nothing gets pulled to D1, nothing gets worked on unless it falls inside an agent's coverage zone.

**THIS IS THE ONLY PROCESS THAT READS FROM NEON.** Every other SVG process reads exclusively from D1. The lifecycle is SEED (Neon → D1) → WORK (D1 only) → PUSH (D1 → Neon). Only Process 010 does the SEED.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Manual. Run before any SVG process operates. Re-run when Neon data changes (new companies, new agents, new coverage zones).
2. **"How do we get it?"** — Hyperdrive connection to Neon PostgreSQL vault.

### Input
- Agent name + anchor ZIP code + 100-mile radius
- Currently 3 agents: Dave Allan (26739 WV), Jeff Mussolino (21742 MD), David Vang (28461 NC)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Agent anchor ZIP + 100mi radius | Haversine expansion against `reference.us_zip_codes` (41,553 ZIPs with lat/lon) | All ZIP codes within 100mi of each agent's anchor | `coverage.v_service_agent_coverage_zips` (Neon view) |
| 2 | Qualifying ZIPs | Match against `outreach.company_target.postal_code` to get outreach_ids | ~32K outreach_ids that passed Gate 0 | Neon SQL JOIN |
| 3 | Qualifying outreach_ids | Tie back to sovereign_id via `cl.company_identity` | outreach_id ↔ sovereign_id link confirmed | Neon SQL JOIN |
| 4 | Qualifying outreach_ids | Copy CT sub-hub — city, state, postal_code, industry, employees, email_method + agent assignment | `outreach_company_target` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 5 | Qualifying outreach_ids | Copy DOL sub-hub — filing_present, ein, carrier, renewal_month + full filing detail (form_5500, schedule_a, schedule_c, schedule_other) | `outreach_dol` + `dol_form_5500` + `dol_schedule_*` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 6 | Qualifying outreach_ids | Copy Blog sub-hub — about_url, source_url, sitemap structure. First pass maps everything. After that, quick update for changes only. | `outreach_blog` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 7 | Qualifying outreach_ids | Copy People sub-hub — 3 slots per company (CEO, CFO, HR), always 3, filled or empty. Each filled slot ties to a person record with verified email + LinkedIn URL. | `people_company_slot` + `people_people_master` in D1 | Hyperdrive → D1 INSERT OR REPLACE |
| 8 | Coverage reference | Copy coverage tables for local reference | `coverage_service_agent` + `coverage_service_agent_coverage` in D1 | Hyperdrive → D1 INSERT OR REPLACE |

### Output
- D1 fully populated with the complete footprint for every company inside an agent's coverage zone
- Footprint per company = CT + DOL + Blog + People (3 slots with person records)
- All hanging off one outreach_id (the spine)
- If a new sub-hub appears (e.g., workers comp), it goes into Neon first, then the SEED pulls it to D1. The pattern is the constant. The sub-hubs are the variable.

### Circle (Bedrock §5)
After SEED completes, run the post-SEED audit (section 9) to verify all joins. If join integrity drops below 99%, re-run the failing step. Log results to imo-brain.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | WRITE | All outreach sub-hub tables (target for SEED) |
| svg-d1-spine | D1 | 641a9a1e | WRITE | cl_company_identity (117K sovereign records) |
| Neon PostgreSQL | HD_NEON (Hyperdrive) | — | READ | Source vault — all schemas (cl, outreach, people, dol, coverage, reference) |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| Hyperdrive | CF Binding | Free | Auto (wrangler.toml) | Connection pooling to Neon — fast reads from vault |
| wrangler CLI | Tool | Free | OAuth (logged in) | D1 queries for verification |
| lcs-hub worker | CF Worker | Free | Deployed | Hosts all /seed/* endpoints |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| NEON_URL | imo-creator | dev | Hyperdrive binding (configured in wrangler.toml, not runtime) |

**Tool Priority:** This is a SEED process — it only uses Hyperdrive to Neon. No external APIs. No proxy. No cost beyond compute.

---

## 5. OSAM — Where the Data Lives

### READ Access (Neon vault — source)

| Schema.Table | What It Provides | Join Key |
|-------------|-----------------|----------|
| `reference.us_zip_codes` | 41,553 US ZIP codes with lat/lon | `zip` (used by haversine view) |
| `coverage.service_agent` | 3 agents — name, number, status | `service_agent_id` |
| `coverage.service_agent_coverage` | Intent — anchor_zip + radius_miles | `service_agent_id` |
| `coverage.v_service_agent_coverage_zips` | VIEW — all ZIPs within each agent's radius | `zip` |
| `cl.company_identity` | Sovereign identity — company_unique_id, outreach_id | `company_unique_id` / `outreach_id` |
| `outreach.company_target` | Targeting — city, state, postal_code, email_method | `outreach_id` |
| `outreach.dol` | DOL summary — filing_present, carrier, renewal | `outreach_id` |
| `outreach.blog` | Web content — about_url, source_url | `outreach_id` |
| `outreach.people` | Delivery contacts — email, verified, lifecycle | `outreach_id` |
| `people.company_slot` | Slots — CEO/CFO/HR, is_filled, person_unique_id | `outreach_id` |
| `people.people_master` | Contacts — name, title, verified email, LinkedIn URL | `unique_id` ← slot.person_unique_id |
| `dol.form_5500` | Federal filings — all years, all fields | `sponsor_dfe_ein`, `ack_id` |
| `dol.schedule_a_part1` | Broker/insurance detail | `ack_id` |
| `dol.schedule_c_part1_item2` | Service provider detail | `ack_id` |
| `dol.schedule_*` (others) | All other schedules as JSON | `ack_id` |

### WRITE Access (D1 outreach — target)

| D1 Table | Neon Source | Sub-Hub | When |
|----------|-----------|---------|------|
| `outreach_company_target` | `outreach.company_target` + agent assignment | CT | Step 4 |
| `outreach_dol` | `outreach.dol` | DOL | Step 5 |
| `dol_form_5500` | `dol.form_5500` | DOL | Step 5 |
| `dol_schedule_a` | `dol.schedule_a_part1` | DOL | Step 5 |
| `dol_schedule_c` | `dol.schedule_c_part1_item2` | DOL | Step 5 |
| `dol_schedule_other` | `dol.schedule_*` | DOL | Step 5 |
| `outreach_blog` | `outreach.blog` | Blog | Step 6 |
| `people_company_slot` | `people.company_slot` | People | Step 7 |
| `people_people_master` | `people.people_master` | People | Step 7 |
| `coverage_service_agent` | `coverage.service_agent` | Coverage | Step 8 |
| `coverage_service_agent_coverage` | `coverage.service_agent_coverage` | Coverage | Step 8 |

### Join Chain

```
coverage.service_agent.service_agent_id
  → coverage.v_service_agent_coverage_zips.zip  (haversine expansion)
    → outreach.company_target.postal_code  (GATE 0 — is this company in range?)
      → outreach.outreach.outreach_id  (SPINE — universal join key)
        → cl.company_identity.outreach_id  (tie back to sovereign_id)
        → outreach.company_target  (CT sub-hub)
        → outreach.dol  (DOL sub-hub)
          → dol.form_5500.sponsor_dfe_ein  (filing detail)
            → dol.schedule_a.ack_id
            → dol.schedule_c.ack_id
            → dol.schedule_other.ack_id
        → outreach.blog  (Blog sub-hub)
        → people.company_slot.outreach_id  (3 per company: CEO, CFO, HR)
          → people.people_master.unique_id  (via person_unique_id — verified email + LinkedIn)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Query Neon during WORK phase | SEED only. After SEED, all reads from D1. |
| Write to Neon | Neon is vault. SEED is Neon→D1, never D1→Neon (that's PUSH). |
| Skip the coverage filter | Every company in D1 must be inside an agent's coverage zone. No unfiltered data. |
| Direct cross-sub-hub joins in D1 | Route through outreach_id (the spine) |
| INSERT without OR REPLACE | SEED is idempotent. Re-running must not create duplicates. |

### Query Routing

| Question | Source | Table |
|----------|--------|-------|
| Which agents exist? | D1 outreach | `coverage_service_agent` |
| Which ZIPs does an agent cover? | Neon only (view) | `coverage.v_service_agent_coverage_zips` |
| Is this company in an agent's zone? | D1 outreach | `outreach_company_target.service_agent_name IS NOT NULL` |
| How many companies per agent? | D1 outreach | `outreach_company_target GROUP BY service_agent_name` |
| What's the slot fill rate? | D1 outreach | `people_company_slot WHERE is_filled = 1` |
| What DOL filings does a company have? | D1 outreach | `dol_form_5500 WHERE outreach_id = ?` |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)
- Agent + anchor ZIP + radius = the gate. Everything flows from this.
- 3 slot types per company: CEO, CFO, HR
- outreach_id is the universal join key across all sub-hubs
- Footprint per company = CT + DOL + Blog + People (sub-hubs are extensible)
- D1 table names: Neon schema.table → D1 schema_table (underscore flattening)
- INSERT OR REPLACE for idempotent SEED
- D1.batch() for bulk writes (max ~100 statements per batch)
- DOL data uploaded once a year from EBSA — read-only reference until next upload
- Blog first pass maps everything, after that quick update for changes only

### Variables (fill — changes every run)
- Number of companies passing Gate 0 (~32K currently, changes if agents/coverage change)
- Slot fill rates (depends on Neon people data quality)
- Number of DOL filings (grows with each yearly upload)
- Total rows per table (changes with each SEED run)
- Which sub-hubs exist (CT, DOL, Blog, People today — workers comp or others tomorrow)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Hyperdrive connection fails | HALT — check Neon credentials, Hyperdrive binding |
| D1 write returns error on >10% of batch | HALT — check D1 size limits, table schema |
| Post-SEED join audit shows <95% match | HALT — re-run failing step, investigate data gap |
| Agent coverage returns 0 ZIPs | HALT — check coverage.service_agent_coverage table |
| Company count drops >20% from prior SEED | HALT — something changed in Neon, investigate before overwriting |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Neon PostgreSQL vault | All source data — CL, outreach, people, DOL, coverage | DONE |
| Hyperdrive binding on lcs-hub | HD_NEON configured in wrangler.toml | DONE |
| coverage.v_service_agent_coverage_zips | Neon view (haversine) — must exist for Gate 0 filter | DONE |
| reference.us_zip_codes | 41,553 ZIP codes with lat/lon for haversine | DONE |
| Active service agents | Must exist in coverage.service_agent with status='active' | DONE |
| DOL data | Yearly bulk load from EBSA website into Neon | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 100 (LCS Pipeline) | ALL of the above — compiles CID from full footprint |
| Process 200 (People Worker) | Filled slots, people records, company target, blog about_urls |
| Process 300 (Blog Worker) | Blog records, company target |
| Process 400 (DOL Views) | DOL filing detail (form_5500, schedules) |
| Process 500 (Talent Flow) | People records with LinkedIn URLs |
| ALL SVG processes | If SEED didn't run, nothing works |

---

## 9. SMOKE TEST

```
1. GET lcs-hub.svg-outreach.workers.dev/health → expected: status ok
2. POST /seed/full-people?limit=1000&offset=0 → expected: slots > 0, people > 0, errors = 0
3. wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_company_target" → expected: ~32,704
4. wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_company_target WHERE service_agent_name IS NOT NULL" → expected: ~32,702
5. wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM people_company_slot" → expected: >90,000
6. Join integrity: SELECT COUNT(*) FROM people_company_slot cs JOIN people_people_master pm ON cs.person_unique_id = pm.unique_id WHERE cs.is_filled = 1 → expected: >99% of filled slots match
7. Slot fill rates: SELECT slot_type, ROUND(SUM(CASE WHEN is_filled=1 THEN 1.0 ELSE 0 END)/COUNT(*)*100,1) as pct FROM people_company_slot GROUP BY slot_type → expected: CEO ~60%, CFO ~55%, HR ~35%+
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do all D1 tables exist with data? (CT, DOL, Blog, People, Coverage)
2. **Flow:** Does outreach_id join correctly from spine through every sub-hub table?
3. **Change:** Did the SEED copy Neon data to D1 correctly (schema.table → schema_table)?

---

## 10. LOGBOOK

### 2026-03-26 — Full SEED + fixes

**ORBT:** BUILD → OPERATE
**Trigger:** Manual — D1 was incomplete, slot→person 94.8% orphan rate
**Records processed:** 358K slots, 160K people, 171K DOL, 32K companies
**Errors:** 0 across all batches
**Tools used:** Hyperdrive (HD_NEON), D1.batch(), wrangler CLI for verification
**Result:**
- Fix #1: people_people_master re-SEED (19K records, 99.7% match)
- Fix #2: missing slots created (54K, 100% coverage)
- Fix #3: agent assignment added to outreach_company_target (32,702 assigned)
- Fix #4: D1 title matching (2,510 filled)
- Fix #5: full Neon slot+people SEED (69 batches, 342K slots, ~175K people)
**Learnings:**
- Neon slots already have correct fill states — just copy table by table
- D1.batch() required for bulk operations (CF Worker subrequest limits, max ~100 per batch)
- Coverage zone join is expensive — skip it by using outreach_ids already in D1
- INSERT OR REPLACE makes SEED idempotent — safe to re-run
**ORBT after:** OPERATE

### 2026-03-25 — Initial D1 SEED (partial)

**ORBT:** BUILD
**Trigger:** Manual — building D1 workspace
**Records processed:** 32K companies, 43K slots, 32K people, 171K DOL
**Errors:** Slot→person orphan rate 94.8% (SEED brought wrong subset of people)
**Result:** D1 populated but incomplete. Led to 2026-03-26 fixes.
**ORBT after:** BUILD (incomplete)

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-25 | 94.8% orphan on slot→person join | SEED brought slots but not matching people records | Re-SEED people_master for all referenced person_unique_ids | 1 |
| 2 | 2026-03-25 | 18,301 companies had no slots | Original SEED only brought slots for companies that had them in Neon | Create CEO/CFO/HR slots for all companies, then re-SEED from Neon | 1 |
| 3 | 2026-03-25 | No agent assignment on companies | Coverage filter applied during SEED but result not stored | Added service_agent_id/name/number columns to outreach_company_target | 1 |
| 4 | 2026-03-26 | CF Worker subrequest limit on bulk writes | Individual INSERT statements instead of D1.batch() | Use D1.batch() with max ~100 statements per batch | 1 |
| 5 | 2026-03-26 | Coverage zone join too slow for full people SEED | Query joined against haversine view for 182K people rows | Skip coverage join — use outreach_ids already in D1 to filter | 1 |

---

## 12. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-25 | D1 schema introspection, SEED gap analysis | schema/d1-outreach-ops-full-schema-2026-03-25 |
| 2026-03-25 | Architectural corrections documented | session/2026-03-25-process-200-corrections |
| 2026-03-26 | Full SEED fixes (people, slots, agents) | ops/2026-03-26-seed-fix-complete |
| 2026-03-26 | Data flow diagram documented | decisions/2026-03-26-data-flow-neon-to-d1 |
| 2026-03-26 | Full Neon slot+people SEED complete | ops/2026-03-26-full-neon-seed-complete |
| 2026-03-29 | Process doc rewritten from Dave's walkthrough | none |

---

## SEED ENDPOINTS (on lcs-hub worker)

| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/seed/full-people?limit=5000&offset=0` | POST | Pull slots + people from Neon, paginated |
| `/seed/fix-slots?limit=3000` | POST | Create missing CEO/CFO/HR slots (D1 only) |
| `/seed/fix-agents` | POST | Assign agents to companies via coverage view |
| `/seed/fix-people` | POST | Pull missing people_master records from Neon |
| `/seed/fix-match?limit=1000` | POST | Match existing D1 people to empty slots by title |
| `/seed/batch?limit=100&offset=0` | POST | Original DOL-focused batch SEED |
| `/seed/dol-to-d1/{ein}` | POST | SEED DOL for one EIN |
| `/seed/global-zips` | POST | SEED ZIP codes to imo-d1-global |

---

## HOW TO RE-RUN THE FULL SEED

```bash
# 1. Pull all slots + people from Neon (paginated, run until has_more=false)
for OFFSET in $(seq 0 5000 350000); do
  curl -s -X POST "https://lcs-hub.svg-outreach.workers.dev/seed/full-people?limit=5000&offset=$OFFSET"
  # Stop when slots_updated=0
done

# 2. Assign agents (if not already done or if coverage changed)
curl -s -X POST "https://lcs-hub.svg-outreach.workers.dev/seed/fix-agents"

# 3. Run post-SEED audit
wrangler d1 execute svg-d1-outreach-ops --remote --command "
  SELECT slot_type,
    COUNT(*) as total,
    SUM(CASE WHEN is_filled=1 THEN 1 ELSE 0 END) as filled,
    ROUND(SUM(CASE WHEN is_filled=1 THEN 1.0 ELSE 0 END)/COUNT(*)*100,1) as pct
  FROM people_company_slot
  GROUP BY slot_type ORDER BY slot_type"
```

---

## SERVICE AGENTS (Gate 0)

| Agent | Number | Anchor ZIP | Radius | Region | Companies |
|-------|--------|-----------|--------|--------|-----------|
| Dave Allan | SA-001 | 26739 | 100mi | WV | 6,872 |
| Jeff Mussolino | SA-002 | 21742 | 100mi | MD | 22,493 |
| David Vang | SA-003 | 28461 | 100mi | NC | 3,337 |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 2.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md v1.1.2 |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

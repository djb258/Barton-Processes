---
species: UT-Body
companion_yaml: Barton-Processes/factory/outreach/010-seed-d1/workflow.yaml
certification_label: provisional-runtime
outside:
  heir:
    sovereign_ref: svg-outreach
    hub_id: 010-seed-d1
    ctb_placement: leaf
    ctb_node: barton-enterprises/svg-agency/outreach-intelligence/010-seed-d1
    imo_topology: hub
    cc_layer: CC-04
    secrets_provider: doppler
    acceptance_criteria: "UT-local Workflow-Body; 10 BAR-377 gates green; verify-only OPERATE"
  orbt:
    library_state: BUILD
    last_indexed_at: "2026-05-06T00:00:00Z"
    indexed_by: sonnet-mechanic
inside:
  heir:
    process_id: bp.010
    species: UT-Body
    version: "1.0.0"
    last_modified: "2026-05-06"
    companion_manifest: Barton-Processes/factory/outreach/010-seed-d1/PROCESS-UT.md
  orbt:
    library_state: BUILD
---

# PROCESS-UT — SVG D1 SEED
## Unified Template v2.7.0 | PROC-010 | UT Consolidation 2026-04-29

> **Governance:** Rules enforced by `DOCTRINE.md` (D-010-01 through D-010-12).
> **Authority:** `law/doctrine/FOUNDATIONAL_BEDROCK.md`, `law/UNIFIED_TEMPLATE.md`
> **CTB:** `law/BARTON_ENTERPRISES_CTB.md` → SVG Agency → Outreach → SEED D1

---

## PRE-FLIGHT CHECKLIST (13 Items — UT v2.7.0)

- [ ] 1. Process ID declared and matches heir.yaml `hub_id`
- [ ] 2. HEIR all 8 fields populated (no blanks)
- [ ] 3. ORBT state declared and matches orbt.yaml
- [ ] 4. Hyperdrive binding `HD_NEON` confirmed active in lcs-hub
- [ ] 5. Coverage filter `v_service_agent_coverage_zips` confirmed available in Neon
- [ ] 6. Column inventory snapshot current (NEON_COLUMN_INVENTORY.csv or equivalent < 7 days old)
- [ ] 7. All INSERT statements confirmed as `INSERT OR REPLACE` (no bare INSERT)
- [ ] 8. D1.batch() confirmed for all bulk write paths
- [ ] 9. Materialized views `v_agent_blog` and `v_agent_fill_rates` refreshed
- [ ] 10. Target D1 databases confirmed: svg-d1-outreach-ops (73a285b8) and svg-d1-spine (641a9a1e)
- [ ] 11. Neon seed_views schema confirmed available (8 views)
- [ ] 12. SEED run has defined table scope and offset range (not open-ended)
- [ ] 13. Stop condition thresholds reviewed: >10% D1 write error = HALT, <95% join integrity = HALT, >20% company count drop = HALT

---

## §1 IDENTITY {#sec-1-identity}

| Field | Value |
|-------|-------|
| Process ID | PROC-010 |
| Name | SVG D1 SEED |
| Short Name | SEED |
| Organization | SVG Agency |
| Owner | Dave Barton |
| CTB Placement | leaf |
| IMO Topology | spoke |
| CC Layer | CC-04 |
| ORBT State | OPERATE |
| Strikes | 0 |
| BAR Reference | BAR-52 |
| Related BARs | BAR-190 (SEED v2 national spine design) |
| Version | v1.0.0-consolidated |
| Created | 2026-03-25 |
| Last Modified | 2026-04-29 |
| Governance | See `DOCTRINE.md` at folder root |

### HEIR

| Field | Value |
|-------|-------|
| sovereign_ref | imo-creator-v2 |
| hub_id | 010-seed-d1 |
| ctb_placement | leaf |
| imo_topology | spoke |
| cc_layer | CC-04 |
| services | lcs-hub, svg-d1-outreach-ops, svg-d1-spine, neon-postgresql |
| secrets_provider | doppler |
| acceptance_criteria | See heir.yaml at folder root |

---

## §1b GEOMETRY {#sec-1b-geometry}

**CTB Position:** SVG Agency → Outreach Intelligence → SEED D1 (leaf)

**Role in Hub-Spoke:** SEED is a spoke process. It reads from the Neon vault (hub) and writes to D1 workspace databases. SEED does not generate data — it copies and scopes. All SEED logic lives in Neon `seed_views` schema (read-only lenses). The SEED Worker is dumb transport.

**Altitude:** 10k ft operational. SEED executes a defined table copy per run cycle. Strategy (which tables, what scope) is set at 30k (process design). The operator fires SEED at 10k and reads counts.

**Sovereign Silo:** SEED owns two D1 databases (outreach-ops, spine). It reads one Neon database (Marketing DB via Hyperdrive). No cross-silo writes.

---

## §2 PURPOSE {#sec-2-purpose}

### What This Process Does

SEED copies agent-scoped company records from the Neon PostgreSQL vault into Cloudflare D1 workspace databases, making them available for low-latency edge processing by downstream workers (LCS, Process 100; Email Discovery, Process 201; LinkedIn Discovery, Process 202; Blog Worker, Process 300).

### Why It Exists

Neon is the vault — authoritative, high-fidelity, expensive to query at edge latency. D1 is the workspace — fast, cheap, edge-native, but dumb. SEED bridges the gap. It applies the agent coverage filter (Gate 0: ZIP + radius → qualifying companies) and pours only the relevant subset into D1. Downstream workers never touch Neon during live outreach runs.

### SEED v1 vs SEED v2

**SEED v1 (current — OPERATE):** Agent ZIP + radius → qualifying ZIPs → 32,702 companies from Neon → pour all 9 sub-hubs into D1. One agent scope, pre-defined.

**SEED v2 (planned — BAR-190):** Three-phase national architecture:
- Phase 1: Rough-in 2.4M DOL companies with sovereign ID + CT + domain (free, national, run once)
- Phase 2: State completion via Clay/Hunter for non-filers (cheap, per state, on market open)
- Phase 3: Agent activation → SEED to D1 → fill slots → outreach (costs money, per agent)

SEED v1 mixes constants and variables. SEED v2 separates them: constants built once for the whole country, variables filled only when activated.

### Downstream Consumers

| Consumer | Process | What It Reads |
|----------|---------|---------------|
| LCS Pipeline | PROC-100 | All D1 sub-hubs via outreach_id spine |
| Email Discovery | PROC-201 | people_company_slot, people_people_master |
| LinkedIn Discovery | PROC-202 | people_company_slot, people_people_master |
| Blog Worker | PROC-300 | outreach_blog, outreach_outreach |
| DOL Views | PROC-400 | outreach_dol |

---

## §3 RESOURCES {#sec-3-resources}

### Databases

| Database | Binding | ID | Access | Role |
|----------|---------|-----|--------|------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8-... | WRITE | Primary workspace D1 |
| svg-d1-spine | D1 | 641a9a1e-... | WRITE | CL identity spine D1 |
| Neon Marketing DB | HD_NEON | ep-ancient-waterfall | READ | Source vault via Hyperdrive |

### Secrets

| Secret | Provider | Scope | Used For |
|--------|----------|-------|----------|
| NEON_URL | Doppler | imo-creator/dev | Direct Neon connection (non-Hyperdrive path) |

### Runtime

| Component | Value |
|-----------|-------|
| Compute | Cloudflare Workers (via lcs-hub) |
| SEED Endpoint | `https://lcs-hub.svg-outreach.workers.dev/seed/clean?table={name}&limit=5000&offset=0` |
| Method | POST |
| Auth | Internal binding (no public auth) |
| Wrangler | None — PROC-010 is NOT a deployable process; it runs as an endpoint on lcs-hub |

### Tool Sub-Hubs

| Sub-Hub | Number | Role |
|---------|--------|------|
| Neon PostgreSQL | 11 | Source vault |
| Cloudflare D1 | 16 | Workspace databases |
| Cloudflare Workers | 06 | Compute runtime (lcs-hub) |

---

## §4 IMO {#sec-4-imo}

### Input

**Trigger:** Manual POST or automated scheduler to `/seed/clean?table={name}&limit=5000&offset=0`

**Initial Condition:** Neon `seed_views` schema contains 8 agent-scoped views pre-built with coverage filter applied. D1 databases may contain stale data from prior runs.

**Dual Input:**
- Crossing Input: HTTP POST request with table name + limit + offset parameters
- Initial Condition: Neon vault data state at time of run

### Middle (12-Step Processing)

| Step | Action | Gate |
|------|--------|------|
| 1 | Receive POST — extract `table`, `limit`, `offset` params | D-010-04 (coverage filter already in view) |
| 2 | Validate table name against allowed list | Reject unknown table names |
| 3 | Open Hyperdrive connection to Neon (`HD_NEON`) | D-010-12 (must use HD_NEON) |
| 4 | SELECT from corresponding `seed_views.v_agent_{table}` with LIMIT/OFFSET | D-010-01 (read-only from Neon) |
| 5 | Transform Neon row format to D1 column format | Schema mapping per table |
| 6 | Build D1.batch() statement array (max ~100 per batch) | D-010-02 (batch required) |
| 7 | Execute INSERT OR REPLACE batch against target D1 table | D-010-03 (OR REPLACE required) |
| 8 | Capture write error count from D1 response | D-010-07 (>10% = HALT) |
| 9 | Return JSON response: `{inserted, errors, table, offset}` | Caller reads counts |
| 10 | Caller increments offset by limit, fires next POST | Repeat until view exhausted |
| 11 | Post-run: caller verifies D1 row counts match Neon view counts | D-010-06 (join integrity ≥ 95%) |
| 12 | Post-run: log sigma (3 consecutive runs, compare counts) | §10 Analytics |

### Output

**Emitted Output:** JSON response per POST with inserted count, error count, table name, offset.

**Retained Output:** D1 tables populated with agent-scoped Neon data. Coverage: 32,702 companies × 9 sub-hubs.

---

## §5 DATA SCHEMA {#sec-5-data-schema}

### D1 Tables — svg-d1-outreach-ops (D1_OUTREACH)

| Table | Rows (post-clean SEED) | Key Columns | Join |
|-------|----------------------|-------------|------|
| outreach_company_target | 32,702 | outreach_id (PK), postal_code, state_code | spine |
| outreach_outreach | 32,702 | outreach_id (PK), campaign_status | spine |
| outreach_blog | 32,702 | outreach_id (FK), domain, about_url, reachable | outreach_id |
| outreach_dol | 32,702 | outreach_id (FK), ein, carrier, broker, renewal_month | outreach_id |
| people_company_slot | 98,106 | slot_id (PK), outreach_id (FK), slot_type, is_filled | outreach_id |
| people_people_master | 58,857 | person_unique_id (PK), name, email, linkedin_url | slot → outreach_id |
| coverage_service_agent | 3 | agent_id, agent_number, anchor_zip | — |
| coverage_service_agent_coverage | 3 active | agent_id (FK), zip_code, radius_miles | agent_id |
| outreach_column_registry | 79 | column_name, table_name, documented | metadata |

### D1 Tables — svg-d1-spine (D1)

| Table | Rows | Key Columns | Join |
|-------|------|-------------|------|
| cl_company_identity | 32,702 | outreach_id (PK), company_name, ein, zip | spine |

### Neon Source Views (seed_views schema)

| View | Type | Rows | Source |
|------|------|------|--------|
| v_agent_companies | VIEW | 32,702 | Gate — DISTINCT ON outreach_id from coverage JOIN |
| v_agent_cl_identity | VIEW | 32,702 | cl.company_identity |
| v_agent_outreach | VIEW | 32,702 | outreach.outreach |
| v_agent_blog | MATERIALIZED | 32,702 | vendor.blog + outreach.blog |
| v_agent_dol | VIEW | 32,702 | outreach.dol |
| v_agent_slots | VIEW | 98,106 | CROSS JOIN gate × (CEO, CFO, HR) |
| v_agent_people | VIEW | 58,857 | people referenced by filled slots |
| v_agent_fill_rates | MATERIALIZED | 32,702 | Completeness scorecard |

### Join Chain

```
coverage.v_service_agent_coverage_zips (ZIP gate)
  → outreach.company_target.postal_code
  → DISTINCT ON outreach_id → 32,702 companies
    → cl_company_identity (1:1)
    → outreach_outreach (1:1)
    → outreach_blog (1:1, LEFT JOIN)
    → outreach_dol (1:1, LEFT JOIN)
    → people_company_slot (1:3, CEO/CFO/HR)
      → people_people_master (via person_unique_id)
```

### Forbidden Paths (D-010-01, D-010-04, D-010-11)

- Write to Neon from D1 Worker
- Query Neon during live outreach runs (not during SEED)
- Skip coverage filter → pour full universe into D1
- Cross-sub-hub join without outreach_id
- INSERT without OR REPLACE
- Single-row INSERT loops (must use D1.batch())

---

## §6 DMJ {#sec-6-dmj}

### DEFINE

| Element | Type | Format | Classification |
|---------|------|--------|----------------|
| outreach_id | constant | UUID string | spine join key |
| agent_number | constant | SA-NNN format | coverage scope |
| anchor_zip | constant | 5-digit string | geographic center |
| radius_miles | constant | integer | coverage boundary |
| slot_type | constant | enum: CEO/CFO/HR | people classification |
| company_name | variable | string | fill per company |
| domain | variable | string or null | fill per company |
| email | variable | string or null | fill per person |
| linkedin_url | variable | string or null | fill per person |
| campaign_status | variable | enum | fill per outreach cycle |
| is_filled | variable | boolean | fill after slot discovery |

### MAP

| Source (Neon) | Target (D1) |
|---------------|-------------|
| seed_views.v_agent_cl_identity | cl_company_identity |
| seed_views.v_agent_outreach | outreach_outreach |
| seed_views.v_agent_companies | outreach_company_target |
| seed_views.v_agent_blog | outreach_blog |
| seed_views.v_agent_dol | outreach_dol |
| seed_views.v_agent_slots | people_company_slot |
| seed_views.v_agent_people | people_people_master |

### JOIN

Spine: `outreach_id` (UUID). Every D1 table attaches to this key. All sub-hub tables JOIN through outreach_id. No cross-sub-hub query skips this key (D-010-11).

---

## §7 CONSTANTS & VARIABLES {#sec-7-constants-variables}

### Constants (Locked — D-010-XX enforces)

| Constant | Value | Doctrine Rule |
|----------|-------|---------------|
| SEED direction | Neon → D1 only | D-010-01 |
| Batch write method | D1.batch() | D-010-02 |
| INSERT pattern | INSERT OR REPLACE | D-010-03 |
| Coverage gate | Haversine ZIP filter | D-010-04 |
| Company count baseline | 32,702 | D-010-05 |
| Join integrity threshold | ≥ 95% | D-010-06 |
| Write error threshold | ≤ 10% | D-010-07 |
| Column documentation gate | snapshot required | D-010-08 |
| Constants vs variables split | Phase 1 free / Phase 3 costs | D-010-09 |
| Materialized view refresh | required before run | D-010-10 |
| Spine key | outreach_id | D-010-11 |
| Neon connection method | HD_NEON binding | D-010-12 |

### Variables (Per Run)

| Variable | Format | Range |
|----------|--------|-------|
| target_table | string (table name) | allowed list |
| limit | integer | 1 – 5000 |
| offset | integer | 0 – (view max rows) |
| run_timestamp | ISO 8601 | current time |
| inserted_count | integer | 0 – limit |
| error_count | integer | 0 – limit |

---

## §8 STOP CONDITIONS {#sec-8-stop-conditions}

| Condition | Threshold | Doctrine Rule | Action |
|-----------|-----------|---------------|--------|
| Reverse write to Neon detected | Any | D-010-01 | HALT immediately — ORBT → REPAIR |
| D1 write error rate | > 10% per run | D-010-07 | HALT — ORBT → REPAIR |
| Join integrity audit | < 95% coverage | D-010-06 | HALT — do not certify SEED |
| Company count deviation | > 20% from 32,702 | D-010-05 | HALT — investigate coverage filter |
| Coverage filter skipped | Any | D-010-04 | Block SEED run — require filter confirmation |
| HD_NEON binding missing | Any | D-010-12 | Block SEED run — binding required |
| Undocumented columns blocking table | Any affected table | D-010-08 | Block that table's SEED until documented |
| Strike 3 on same failure | 3 identical failures | Aviation Model | Troubleshoot/Train — no more repair cycles |

### Kill Switch

```bash
# Stop all active SEED runs — revoke lcs-hub endpoint access (requires CF dashboard)
# Emergency: disable the /seed/clean route in lcs-hub wrangler.toml and redeploy
# Verification: curl -X POST https://lcs-hub.svg-outreach.workers.dev/seed/clean?table=outreach&limit=1
# Expected: 403 or 404 if disabled
```

---

## §9 VERIFICATION + THREE PRIMITIVES {#sec-9-verification}

### Three Primitives Check

| Primitive | Check | Pass Condition |
|-----------|-------|----------------|
| THING | Does outreach_id exist for every company in D1? | 0 NULL outreach_ids in outreach_company_target |
| FLOW | Does each Neon view row reach its D1 target table? | D1 row count = Neon view row count per table |
| CHANGE | Does INSERT OR REPLACE correctly update changed rows? | Re-run produces same counts (idempotent) |

---

## §9b LIVE VERIFICATION {#sec-9b-live-verification}

All commands use Wrangler D1 execute against remote databases.

| # | Gauge | Verification Command | Expected Value |
|---|-------|----------------------|----------------|
| 1 | company_target count | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_company_target"` | 32,702 |
| 2 | outreach count | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_outreach"` | 32,702 |
| 3 | blog count | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_blog"` | 32,702 |
| 4 | dol count | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_dol"` | 32,702 |
| 5 | slots count | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM people_company_slot"` | 98,106 |
| 6 | people count | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM people_people_master"` | 58,857 |
| 7 | spine count | `wrangler d1 execute svg-d1-spine --remote --command "SELECT COUNT(*) FROM cl_company_identity"` | 32,702 |
| 8 | agents count | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM coverage_service_agent"` | 3 |
| 9 | active zones | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM coverage_service_agent_coverage"` | 3 |
| 10 | orphan slots | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM people_company_slot WHERE is_filled=1 AND person_unique_id NOT IN (SELECT person_unique_id FROM people_people_master)"` | 0 |
| 11 | column registry | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(*) FROM outreach_column_registry"` | 79 |
| 12 | join integrity | `wrangler d1 execute svg-d1-outreach-ops --remote --command "SELECT COUNT(DISTINCT ct.outreach_id) FROM outreach_company_target ct JOIN outreach_outreach o ON ct.outreach_id=o.outreach_id JOIN people_company_slot s ON ct.outreach_id=s.outreach_id"` | TBV (expect ≥ 31,066 for 95%) |

---

## §10 ANALYTICS {#sec-10-analytics}

### Metrics Table (Baseline 2026-04-01)

| Metric | Value | Source | Threshold |
|--------|-------|--------|-----------|
| Total companies in scope | 32,702 | SEED_AUDIT.md | locked constant |
| Dave Allan companies | 6,872 | SEED_AUDIT.md | — |
| Jeff Mussolino companies | 22,493 | SEED_AUDIT.md | — |
| David Vang companies | 3,337 | SEED_AUDIT.md | — |
| Dual-agent companies | 2,927 | SEED_AUDIT.md | — |
| CL identity fill rate | 100% | SEED_AUDIT.md | 100% required |
| Blog domain reachable | 52.7% (17,248/32,702) | SEED_AUDIT.md | TBV |
| Blog about_url found | 34.7% (11,356/32,702) | SEED_AUDIT.md | TBV |
| Blog content extracted | 11.9% (3,876/32,702) | SEED_AUDIT.md | TBV |
| DOL filing present | 78.5% (25,656/32,702) | SEED_AUDIT.md | TBV |
| People slots filled | 60.1% (58,966/98,106) | SEED_AUDIT.md | improving via PROC-201 |
| People with email | 59.3% (58,184/98,106) | SEED_AUDIT.md | improving via PROC-201 |
| People with LinkedIn | 48.8% (47,858/98,106) | SEED_AUDIT.md | improving via PROC-202 |
| Total people in Neon | 183,397 | SEED_AUDIT.md | 58,857 needed |
| People outside scope | 124,540 | SEED_AUDIT.md | never touch D1 |
| Column registry documented | 79 of TBV | PROCESS.md | 100% required before new table |
| Neon columns documented | 3,867 / 4,959 (78%) | MASTER_DATA_CTB.md | 100% target |

### Sigma Tracking

| Metric | Direction | Status |
|--------|-----------|--------|
| Company count per run | Flat at 32,702 | Locked constant — any deviation = investigate |
| Blog fill rate | Tightening (active work) | PROC-300 running |
| People slot fill | Tightening (active work) | PROC-201/202 running |
| DOL filing coverage | Flat at 78.5% | Gap = companies without DOL filings (structural) |
| Email verification rate | Tightening | Million Verifier pending integration |

### ORBT Gate Rules

| State | Condition |
|-------|-----------|
| OPERATE | SEED completes, counts match, error rate ≤ 10%, join integrity ≥ 95% |
| REPAIR | Write error rate > 10% OR join integrity < 95% OR count deviation > 20% |
| BUILD | New table or schema change requires SEED rebuild |
| TROUBLESHOOT_TRAIN | Strike 3 on same failure — root cause investigation before next run |

---

## §11 EXECUTION TRACE {#sec-11-execution-trace}

### Full Re-Run Script

```bash
# Fire SEED for all 7 primary tables with offset pagination
for TABLE in company_target outreach cl_identity blog dol slots people; do
  for OFFSET in $(seq 0 5000 100000); do
    RESULT=$(curl -s -X POST \
      "https://lcs-hub.svg-outreach.workers.dev/seed/clean?table=$TABLE&limit=5000&offset=$OFFSET")
    echo "$TABLE offset=$OFFSET: $RESULT"
    # Check for errors in response
    ERROR_COUNT=$(echo $RESULT | jq -r '.errors // 0')
    INSERTED_COUNT=$(echo $RESULT | jq -r '.inserted // 0')
    if [ "$INSERTED_COUNT" -eq "0" ] && [ "$OFFSET" -gt "0" ]; then
      echo "Table $TABLE exhausted at offset $OFFSET"
      break
    fi
  done
done
```

### Table Execution Order

Run in this sequence to satisfy foreign key dependencies:

1. `company_target` — spine reference (no FK)
2. `cl_identity` — spine reference (no FK)
3. `outreach` — references company_target
4. `blog` — references outreach
5. `dol` — references outreach
6. `slots` — references outreach (creates 3× rows per company)
7. `people` — references slots

---

## §12 LOGBOOK {#sec-12-logbook}

| Date | Entry | Author |
|------|-------|--------|
| 2026-03-25 | SEED v1 built and deployed. lcs-hub `/seed/clean` endpoint live. First full pour: 32,702 companies across 9 sub-hubs. Counts verified. ORBT: BUILD → OPERATE. | Dave Barton |
| 2026-03-28 | Discovered D1 dirty state: cl_company_identity had 117,154 rows (full Neon universe instead of agent-scoped 32,702). outreach_blog had 49,062 rows with duplicates. coverage_service_agent had 9 rows (triple duplicated). Added re-SEED plan. ORBT: OPERATE → REPAIR. | Dave Barton |
| 2026-03-30 | SEED_AUDIT.md created. Traced full agent → ZIP → coverage → company chain. Locked 32,702 as constant. Documented 8 Neon seed_views. Fill rate scorecard established. 53 orphan slots fixed (CTB-path person IDs from Jan 2026 intake_promotion pipeline reset to is_filled=false). | Dave Barton |
| 2026-04-01 | Clean SEED completed. All D1 tables wiped and re-seeded from Neon views. Final counts verified: 32,702 companies, 98,106 slots, 58,857 people. Coverage tables cleaned: 3 agents, 3 active zones. ORBT: REPAIR → OPERATE. | Dave Barton |

---

## §13 FLEET FAILURE REGISTRY {#sec-13-fleet-failure-registry}

| # | Failure | Date | Strike | Root Cause | AD Reference |
|---|---------|------|--------|------------|--------------|
| 1 | cl_company_identity bloat (117,154 rows instead of 32,702) | 2026-03-28 | 1 | SEED poured full Neon universe without agent scope filter — coverage filter not applied to cl_identity view | Fixed 2026-04-01: re-seeded with v_agent_cl_identity |
| 2 | outreach_blog duplicates (49,062 rows) | 2026-03-28 | 1 | SEED sourced from outreach.blog only, not vendor.blog JOIN — duplicate rows from multiple SEED runs without truncate | Fixed 2026-04-01: re-seeded from v_agent_blog (vendor.blog + outreach.blog combined) |
| 3 | coverage_service_agent triplication (9 rows instead of 3) | 2026-03-28 | 1 | SEED run fired 3× without truncate — INSERT without OR REPLACE created duplicate agent rows | Fixed 2026-04-01: table truncated, 3 clean rows inserted |
| 4 | people_company_slot bloat (358,308 rows instead of 98,106) | 2026-03-28 | 1 | SEED poured full people universe instead of agent-scoped slots | Fixed 2026-04-01: re-seeded from v_agent_slots |
| 5 | 53 orphan slots (is_filled=true, person_unique_id not in people_master) | 2026-03-30 | — | CTB-path IDs from Jan 2026 intake_promotion/wv_hr_pipeline never migrated to UUID format | Fixed 2026-04-01: reset to is_filled=false in Neon |
| 6 | outreach_company_target 2 orphans (no agent) | 2026-03-28 | — | Unknown — 2 rows exist without agent assignment | TBV — investigate coverage join |
| 7 | DOL gap: 7,046 companies without filing | Baseline 2026-04-01 | — | Structural: companies with no DOL 5500 filing in Neon — not a SEED failure | Monitor — gap is real, not a bug |
| 8 | Blog content extraction low (11.9%) | Baseline 2026-04-01 | — | PROC-300 blog worker has not yet run full extraction pass | Active work — PROC-300 running |

---

## §14 SESSION LOG {#sec-14-session-log}

| Date | Session | Action | Output |
|------|---------|--------|--------|
| 2026-04-29 | Wave 1 UT Consolidation | Sonnet Runner consolidated 7 fragments (PROCESS.md, MASTER_DATA_CTB.md, SEED_AUDIT.md, SEED_V2_DESIGN.md, NEON_COLUMN_INVENTORY.csv, MASTER_COLUMN_REGISTRY.json, UNDOCUMENTED_COLUMNS.json) into UT v2.7.0 locked folder shape | PROCESS-UT.md, DOCTRINE.md, heir.yaml, orbt.yaml written; _archived-fragments/ created |

---

## Document Control

| Field | Value |
|-------|-------|
| Process ID | PROC-010 |
| UT Version | v2.7.0 |
| Created | 2026-04-29 |
| Consolidated By | Sonnet Runner (Wave 1) |
| Source Fragments | 7 files → _archived-fragments/ |
| Gates G21-G30 | Self-check — pending Codex Auditor Stage 3 |
| DOCTRINE Reference | DOCTRINE.md at folder root |
| HEIR Reference | heir.yaml at folder root |
| ORBT Reference | orbt.yaml at folder root |

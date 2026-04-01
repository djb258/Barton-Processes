# SEED AUDIT — 2026-04-01
## Traced from agent → ZIP → radius → companies → all sub-hubs
### Locked constant: 32,702 companies

---

## The Gate

3 agents define the geography. The geography defines the universe. Agent assignment to a specific company is a downstream variable.

| Agent | Number | Anchor ZIP | Radius | Companies |
|-------|--------|-----------|--------|-----------|
| Dave Allan | SA-001 | 26739 (WV) | 100mi | 6,872 |
| Jeff Mussolino | SA-002 | 21742 (MD) | 100mi | 22,493 |
| David Vang | SA-003 | 28461 (NC) | 100mi | 3,337 |

**Note:** Per-agent sum = 35,629 because 2,927 companies fall in overlapping zones (WV/MD border). DISTINCT ON outreach_id collapses to **32,702**. That is the locked constant.

**Chain:** Agent anchor ZIP + radius → `coverage.v_service_agent_coverage_zips` (Haversine) → qualifying ZIPs → `outreach.company_target.postal_code` → 32,702 companies

---

## Neon SEED Views (`seed_views` schema)

All views are read-only lenses on existing Neon data. No data was modified.

| View | Type | Rows | Logic |
|------|------|------|-------|
| `v_agent_companies` | VIEW | 32,702 | The gate — `DISTINCT ON outreach_id` from coverage JOIN |
| `v_agent_cl_identity` | VIEW | 32,702 | `DISTINCT ON outreach_id` from `cl.company_identity` |
| `v_agent_outreach` | VIEW | 32,702 | 1:1 from `outreach.outreach` |
| `v_agent_blog` | MATERIALIZED | 32,702 | LEFT JOIN from gate to `vendor.blog` + `outreach.blog`, deduped |
| `v_agent_dol` | VIEW | 32,702 | LEFT JOIN from gate to `outreach.dol`, deduped. Empty row if no filing. |
| `v_agent_slots` | VIEW | 98,106 | CROSS JOIN gate × (CEO, CFO, HR), LEFT JOIN to `people.company_slot` |
| `v_agent_people` | VIEW | 58,857 | People referenced by filled slots only |
| `v_agent_fill_rates` | MATERIALIZED | 32,702 | Completeness scorecard per company |

**Every table is 32,702 rows (1:1 per company) except:**
- Slots: 98,106 (32,702 × 3)
- People: 58,857 (follows filled slots — the variable)

**Materialized views** need `REFRESH MATERIALIZED VIEW seed_views.v_agent_blog;` and `REFRESH MATERIALIZED VIEW seed_views.v_agent_fill_rates;` after data changes.

---

## Fill Rate Scorecard (Baseline 2026-04-01)

| Dimension | Have | Need | Gap | Fill Rate |
|-----------|------|------|-----|-----------|
| CL Identity | 32,702 | 32,702 | 0 | **100%** |
| Blog record exists | 29,715 | 32,702 | 2,987 | **90.9%** |
| Blog domain reachable | 17,248 | 29,715 | 12,467 (10,023 not checked + 2,444 down) | **52.7%** |
| Blog about_url found | 11,356 | 32,702 | 21,346 | **34.7%** |
| Blog content extracted | 3,876 | 32,702 | 28,826 | **11.9%** |
| DOL filing present | 25,656 | 32,702 | 7,046 | **78.5%** |
| People slots filled | 58,966 | 98,106 | **39,140** | **60.1%** |
| People with email | 58,184 | 98,106 | 39,922 | **59.3%** |
| People with LinkedIn | 47,858 | 98,106 | 50,248 | **48.8%** |

### Blog Domain Status (29,715 with records)

| Status | Count | Meaning |
|--------|-------|---------|
| Reachable (true) | 17,248 | Confirmed reachable |
| Not checked (NULL) | 10,023 | Unknown — need to check |
| Unreachable (false) | 2,444 | Domain was down when checked |

### Slots Integrity

| Check | Result |
|-------|--------|
| Every filled slot has person_unique_id | YES — 0 orphans |
| Every person_unique_id exists in people_master | YES — 58,857 match |
| People with name | 58,857 (100%) |
| People with email | 58,237 (99.0%) |
| People with LinkedIn | 47,911 (81.4%) |
| People with both | 47,454 (80.6%) |
| People with neither | 163 (0.3%) |
| People used in multiple slots | 104 (minor) |
| Orphan slots (person_id not in people_master) | 0 — **FIXED 2026-04-01** (53 slots had CTB-path IDs from intake_promotion/wv_hr_pipeline Jan 2026 that never migrated to UUID format. Reset to is_filled=false in Neon.) |

### People Bloat

| Where | Count |
|-------|-------|
| Total people in Neon | 183,397 |
| People we need (in 32,702 slots) | 58,857 |
| People outside our universe | 124,540 (67.9%) |

The SEED view (`v_agent_people`) pulls only the 58,857. The 124,540 stay in Neon, never touch D1.

---

## D1 Current State (DIRTY — needs re-SEED)

| D1 Table | Current Rows | Should Be | Problem |
|----------|-------------|-----------|---------|
| `outreach_company_target` | 32,704 | 32,702 | 2 orphans (no agent) |
| `outreach_outreach` | 32,704 | 32,702 | Same 2 orphans |
| `cl_company_identity` (spine) | 117,154 | 32,702 | Full Neon universe — 84,452 extra |
| `outreach_blog` | 49,062 | 32,702 | Duplicates + wrong source table |
| `outreach_dol` | 36,247 | 32,702 | Duplicates (384) + gap is real |
| `people_company_slot` | 358,308 | 98,106 | Full universe — 260,202 extra |
| `people_people_master` | 160,423 | 58,857 | Full universe — 101,566 extra |
| `coverage_service_agent` | 9 | 3 | Triple duplicated |
| `coverage_service_agent_coverage` | 21 | 3 active | Duplicated + retired test zones |

### Re-SEED Plan

1. Delete all rows from dirty D1 tables
2. Clean coverage tables (3 agents, 3 active zones)
3. Pour each Neon view into corresponding D1 table
4. Verify counts match exactly
5. Blog view comes from `vendor.blog` (290K crawl data) + `outreach.blog` (about_urls), not just `outreach.blog`

---

## Work Queue (what the processes need to fill)

| Priority | Task | Count | Process |
|----------|------|-------|---------|
| 1 | Check 10,023 unchecked blog domains | 10,023 | 300 — hit domain, get true/false |
| 2 | Find about_urls on reachable domains | ~5,892 | 300 Phase 3/3B |
| 3 | Extract content from pages with about_urls | 7,480 | 300 Phase 2 |
| 4 | Fill 39,087 empty people slots | 39,087 | 200 (Pass 0 → 1 → 2) |
| 5 | Get blog records for 2,987 missing companies | 2,987 | 300 — need domains first |
| 6 | Re-check 2,444 unreachable domains | 2,444 | 300 — may have come back up |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-01 |
| Authority | Foundational Bedrock — Tier 0 |
| Locked Constant | 32,702 companies |
| Neon Schema | seed_views (8 views) |
| Neon Database | Marketing DB (ep-ancient-waterfall) |

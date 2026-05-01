# PROCESS-UT — 180 Sitemap Publisher
# UT Checklist v1.2.0 | BAR-322 | Governance Backfill 2026-04-30

## UT Pre-Flight Checklist

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §2 PURPOSE |
| 2 | OSAM — READ / WRITE / Process Composition / Join Chain / Forbidden / Routing | ☑ | §6 JOIN CONTRACT + §9 PERMISSIONS |
| 3 | Component Status — every dependency has 🟢 / 🟡 / 🔴 with 1-line state | ☑ | §3 RESOURCES |
| 4 | Owner — human who fixes this at 2 AM | ☑ | §1 IDENTITY |
| 5 | Live Dashboard | ☑ | §3b RESOURCES |
| 6 | Kill Switch — exact command to stop the process | ☑ | §8 INGEST CHECKLIST |
| 7 | Logbook — last audit verdict + date (after certification only) | ☑ | §12 LOGBOOK |
| 8 | FCEs Attached — which FCE runs structurally back this doc | ☑ | §3c FCEs |
| 9 | BARs Referenced — every BAR this doc touches, with status | ☑ | §3d BARs |
| 10 | LBB Subjects Fed — which LBB subject(s) this doc's session logs go to | ☑ | §3e LBB Subjects |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | ☑ | §1b GEOMETRY |
| 12 | Live Verification — every numeric count, cron, URL, command, BAR status grounded | ☑ | §9 PERMISSIONS |
| 13 | ctb_node — declared path on Barton Enterprises CTB trunk | ☑ | §1 IDENTITY |

---

# IDENTITY

## §1 Identity

| Field | Value |
|-------|-------|
| process_id | SITEMAP-PUBLISHER |
| process_number | 180 |
| name | Sitemap Publisher — insuranceinformatics.com URL Registry |
| blueprint_owner | svg-agency |
| runtime | mission-control-api CF Worker (Hono) |
| hub_id | SITEMAP-PUBLISHER-180 |
| sovereign_ref | imo-creator |
| ctb_node | barton-enterprises/insurance-informatics/svg-agency |
| cc_layer | CC-03 |
| imo_topology | middle |
| BAR | BAR-322 |
| owner | Dave Barton |

## §1b Geometry

```
Consumer (MapEngine / XML generator / SEO crawler)
         │
         ▼  GET /sitemap
         ▼  GET /sitemap/:site
mission-control-api (Hono router)  ←── Hub
         │
    ┌────┴──────────────────────┐
    ▼                           ▼
INSURANCE_INFORMATICS_ENTRIES  slugToTitle()
(static array — canonical       pathDepth()
 source of truth)               parentPath()
                                (helper functions)
```

**Hub-Spoke role:** sitemap.ts Hono routes are the hub. Static INSURANCE_INFORMATICS_ENTRIES array is the canonical data source. Helper functions are pure transforms (no side effects). Consumers are spokes — they call the endpoint and render the result.

**Altitude:** Leaf (10K — operational execution). Single-purpose data service returning URL inventory.

---

# CONTRACT

## §2 Purpose

| Field | Value |
|-------|-------|
| WHAT | A Hono route handler on mission-control-api that exposes insuranceinformatics.com URL inventory as a JSON API |
| WHY | MapEngine, XML sitemap generators, and SEO crawlers need a single authoritative source of site URL structure with metadata (depth, parent, priority, changefreq) |
| WHO | Internal consumers: MapEngine (BAR-323), sitemap XML generator; external: SEO crawlers via generated sitemap.xml |
| SCOPE | insuranceinformatics.com sitemap data only; GET /sitemap + GET /sitemap/:site routes on mission-control-api |
| OUT-OF-SCOPE | Write operations; multi-domain sitemaps; dynamic D1-backed sitemap generation |
| SUCCESS METRIC | GET /sitemap returns all entries; GET /sitemap/:site filters correctly; SitemapEntry shape is complete and valid |

## §3 Resources

### §3a Component Status Grid

| Component | Status | State |
|-----------|--------|-------|
| mission-control-api CF Worker | 🟢 | Live — hosts GET /sitemap routes |
| INSURANCE_INFORMATICS_ENTRIES static array | 🟢 | Live — canonical URL registry in sitemap.ts |
| slugToTitle() / pathDepth() / parentPath() | 🟢 | Live — pure helper functions, no dependencies |

### §3b Live Dashboard
Mission Control → Sitemap tab (rendered by MapEngine, BAR-323). GET /sitemap response is the data source.

### §3c FCEs
| FCE | Attachment |
|-----|-----------|
| SVG Agency SEO FCE | Sitemap publisher is the data layer for SEO crawl optimization |

### §3d BARs
| BAR | Description | Status |
|-----|-------------|--------|
| BAR-322 | Sitemap publisher — Hono routes + static entries + helper functions | CLOSED |
| BAR-323 | MapEngine — consumes this endpoint for visualization | CLOSED |

### §3e LBB Subjects
- `svg-sales` — primary (site structure supports sales surface)
- `system` — secondary (infrastructure/routing layer)

## §4 IMO

**Two-Question Intake:**
- What triggers this? A consumer requests the insuranceinformatics.com URL inventory
- How do we get it? HTTP GET to /sitemap (all) or /sitemap/:site (filtered) on mission-control-api

**Input:**
- Crossing: HTTP GET request with optional :site path parameter
- Initial Condition: INSURANCE_INFORMATICS_ENTRIES array compiled into mission-control-api bundle

**Middle:**
1. Route matches GET /sitemap or GET /sitemap/:site
2. If :site present, filter entries where entry.site === site param
3. Return JSON array of SitemapEntry objects
4. If :site unknown → return empty array (200, not 404)

**Output:**
- Emitted: JSON array of SitemapEntry objects to caller
- Retained: none — stateless handler, no D1 writes

**Circle:**
- MapEngine consumes output → renders sitemap visualization → operator verifies URLs → updates static entries if needed → redeploy → next GET /sitemap reflects update

## §5 Contract

### SitemapEntry canonical shape

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| site | TEXT | yes | Site slug identifier (e.g., insuranceinformatics) |
| site_label | TEXT | yes | Human-readable site name |
| path | TEXT | yes | Relative URL path (e.g., /about) |
| title | TEXT | yes | Page title (display string) |
| url | TEXT | yes | Fully qualified canonical URL (https://) |
| parent | TEXT | yes | Parent path (one level up); empty string for root |
| depth | INTEGER | yes | Path depth (number of segments) |
| priority | FLOAT | yes | XML sitemap priority 0.0–1.0 |
| changefreq | TEXT | yes | XML sitemap changefreq enum |
| last_modified | TEXT | yes | ISO 8601 date (YYYY-MM-DD) |

### changefreq valid values
`always` | `hourly` | `daily` | `weekly` | `monthly` | `yearly` | `never`

## §6 Join Contract

**Universal join key:** site slug → SitemapEntry array

**Join chain:**
```
GET /sitemap/:site
  → filter INSURANCE_INFORMATICS_ENTRIES WHERE site === :site
  → return SitemapEntry[]
  → consumer joins on path for page-level metadata
```

**Forbidden paths:**
- Write operations via these routes
- Dynamic D1 reads mixed with static entries without declared join contract
- Returning 404 for unknown site slugs (must return empty array)

**Query routing:**
- All reads: GET /sitemap (all) or GET /sitemap/:site (filtered)
- No other read pattern sanctioned

## §7 Integration

| Source | Target | Transform |
|--------|--------|-----------|
| :site path param | filter condition | direct string match on entry.site |
| INSURANCE_INFORMATICS_ENTRIES | response body | JSON serialization |
| path string | depth | pathDepth() — count of '/' segments |
| path string | parent | parentPath() — path minus last segment |
| path slug | title | slugToTitle() — hyphen→space, title-case |

## §8 Ingest Checklist

**Adding a new page to the sitemap:**
1. Add SitemapEntry object to INSURANCE_INFORMATICS_ENTRIES in sitemap.ts
2. Verify required fields: site, site_label, path, title, url, parent, depth, priority, changefreq, last_modified
3. Confirm url is fully qualified (https://) and path is relative (/)
4. Confirm priority is 0.0–1.0 and changefreq is a valid enum value
5. Confirm last_modified reflects actual content date (not today's date)
6. Deploy mission-control-api
7. GET /sitemap — confirm new entry appears
8. GET /sitemap/insuranceinformatics — confirm entry appears in filtered result

**Stop conditions:**
- Missing required field → entry is incomplete; fix before deploy
- priority out of range → XML sitemap validation will fail
- changefreq not in enum → XML sitemap validation will fail
- url is relative → XML sitemap validation will fail

**Kill switch:**
- Remove entry from INSURANCE_INFORMATICS_ENTRIES → redeploy → entry disappears from all consumers
- To disable the entire endpoint: remove /sitemap routes from mission-control-api router → redeploy (requires BAR)

## §9 Permissions

| Operation | Path | Auth | Notes |
|-----------|------|------|-------|
| READ all sitemap entries | GET /sitemap | none | Public read |
| READ site-filtered entries | GET /sitemap/:site | none | Public read; unknown site → empty array |
| WRITE sitemap data | n/a | n/a — code deploy only | Static entries; no runtime write path |

**Three Primitives Check:**
- Thing: INSURANCE_INFORMATICS_ENTRIES array exists in mission-control-api bundle ✓
- Flow: HTTP GET → Hono router → filter → JSON response ✓
- Change: No runtime state change — stateless read; data changes via code deploy only ✓

**Live Verification Log:**
- GET /sitemap → 200 JSON array: verified BAR-322 close
- GET /sitemap/insuranceinformatics → filtered subset: verified BAR-322 close

## §10 Analytics

**Metrics:**
| Metric | Source | Tolerance |
|--------|--------|-----------|
| Entry count | GET /sitemap array length | matches INSURANCE_INFORMATICS_ENTRIES count |
| Filter accuracy | GET /sitemap/:site count / total | all entries for site returned |
| Response latency | mission-control-api p95 | < 100ms (static data, no D1) |

**Sigma Tracking:**
- Tightening: entry count stable; filter returns correct subset; latency < 100ms
- Flat: entry count not growing despite new pages — static array not updated
- Expanding: latency rising — check mission-control-api bundle size or routing overhead

**ORBT Gate Rules:**
| State | Condition |
|-------|-----------|
| OPERATE | Entry count matches deployed array; filter correct; no squawks |
| REPAIR | Missing entries OR incorrect filter OR schema drift |
| TROUBLESHOOT_TRAIN | Strike 3 on same failure class |

## §11 Execution Trace

| Date | Action | Operator | Result |
|------|--------|----------|--------|
| 2026-04-30 | BAR-322 shipped — GET /sitemap + GET /sitemap/:site + INSURANCE_INFORMATICS_ENTRIES | Dave Barton | PASS — routes live on mission-control-api |
| 2026-04-30 | UT manual backfill (governance) | Claude Code | UT doc written; OPERATE state confirmed |

## §12 Logbook

_After certification only. No entries until auditor certifies._

## §13 Fleet Failure Registry

_No fleet failures recorded._

## §14 Maintenance Logbook

| Date | Action | Operator | Notes |
|------|--------|----------|-------|
| 2026-04-30 | RETROFIT | Claude Code | UT manual backfill for BAR-322; governance only; no code changes |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| Version | 1.0.0 |
| BAR | BAR-322 |
| Status | OPERATE |
| Author | Claude Code (governance backfill) |
| Authority | Dave Barton |
| Template | UNIFIED_TEMPLATE.md v2.0 — 14 sections, 3 clusters |
| UT Checklist | v1.2.0 — 13 items, all addressed |

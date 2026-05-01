# PROCESS-UT — 181 Sitemap Visualization (MapEngine)
# UT Checklist v1.2.0 | BAR-323 | Governance Backfill 2026-04-30

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
| process_id | SITEMAP-VISUALIZATION |
| process_number | 181 |
| name | Sitemap Visualization — MapEngine CTB Map (Mission Control) |
| blueprint_owner | svg-agency |
| runtime | Mission Control CF Pages (React component) |
| hub_id | SITEMAP-VISUALIZATION-181 |
| sovereign_ref | imo-creator |
| ctb_node | barton-enterprises/insurance-informatics/svg-agency |
| cc_layer | CC-02 |
| imo_topology | middle |
| BAR | BAR-323 |
| owner | Dave Barton |

## §1b Geometry

```
Mission Control operator (CF Access gated)
         │
         ▼
MapEngine.tsx  ←── Hub (all rendering logic)
         │
    ┌────┴──────────────────────────────┐
    ▼                                   ▼
GET /map/layers                    GET /sitemap
GET /map/points                    (Process 180 spoke)
[mission-control-api]
         │
    ┌────┴──────┐
    ▼           ▼
MapLayer[]   MapPoint[]
(CTB layers) (geographic dots)
         │
         ▼
ViewportStats (count, avgPriceSqft,
               avgOccupancy, avgSaturation)
```

**Hub-Spoke role:** MapEngine is the hub. All three API calls are spokes (dumb transport). Component owns all layer selection, color assignment, viewport debouncing, and stats rendering logic.

**Altitude:** CC-02 leaf (Mission Control branch). Operational execution — renders the CTB map for operator navigation.

---

# CONTRACT

## §2 Purpose

| Field | Value |
|-------|-------|
| WHAT | A React page within Mission Control that renders the Barton Enterprises CTB as an interactive geographic map, consuming layer data from mission-control-api and site structure from Process 180 |
| WHY | Operators need a visual representation of the CTB tree to understand geographic data distribution, layer relationships, and site structure across all Barton Enterprises branches |
| WHO | Dave Barton (sole authorized operator via CF Access Zero Trust gate) |
| SCOPE | Mission Control Map page only; read-only visualization of map layers + sitemap tree; CF Access gated |
| OUT-OF-SCOPE | Public access; write operations on map or sitemap data; non-Mission Control surfaces |
| SUCCESS METRIC | Map layers render with correct CATEGORY_COLORS; viewport stats display correctly; sitemap tree reflects Process 180 data; all API calls authenticated |

## §3 Resources

### §3a Component Status Grid

| Component | Status | State |
|-----------|--------|-------|
| Mission Control CF Pages | 🟢 | Live — hosts MapEngine.tsx under CF Access |
| mission-control-api GET /map/layers | 🟢 | Live — returns MapLayer[] |
| mission-control-api GET /map/points | 🟢 | Live — returns MapPoint[] (max 2000, viewport-filtered) |
| mission-control-api GET /sitemap | 🟢 | Live — returns SitemapEntry[] (Process 180 data) |
| Cloudflare Access (Zero Trust) | 🟢 | Live — Dave-only, one-time PIN, 24hr session |

### §3b Live Dashboard
MapEngine IS the dashboard. Mission Control → Map page. No secondary dashboard.

### §3c FCEs
| FCE | Attachment |
|-----|-----------|
| Barton Enterprises CTB FCE | MapEngine renders the CTB as its primary output — structural identity |
| SVG Agency FCE | Layer data includes SVG Agency geographic signals |

### §3d BARs
| BAR | Description | Status |
|-----|-------------|--------|
| BAR-323 | MapEngine — CTB map visualization component + API integration | CLOSED |
| BAR-322 | Sitemap Publisher — peer process, supplies GET /sitemap data | CLOSED |
| BAR-329 | MapEngine renders Barton Enterprises CTB (referenced in CTB trunk doc) | CLOSED |

### §3e LBB Subjects
- `system` — primary (CTB visualization, infrastructure)
- `svg-sales` — secondary (geographic signals layer data)

## §4 IMO

**Two-Question Intake:**
- What triggers this? An authorized Mission Control operator opens the Map page
- How do we get it? MapEngine fetches layer registry + viewport points from mission-control-api; sitemap from Process 180 endpoint; all on mount and viewport change

**Input:**
- Crossing: Operator viewport interaction (pan, zoom), layer toggle events
- Initial Condition: MC_API_URL + MC_API_KEY available as Vite env vars at build time

**Middle:**
1. On mount: fetch GET /map/layers → populate layer panel
2. On mount + viewport change (debounced 500ms): fetch GET /map/points for active layers
3. On mount: fetch GET /sitemap → populate sitemap tree panel
4. Apply CATEGORY_COLORS to each MapPoint by category field
5. Enforce MAX_POINTS (2000) — truncate if exceeded
6. Compute ViewportStats from returned points
7. Render CTB nodes from MapLayer.ctb_node — null ctb_node → orphan warning

**Output:**
- Emitted: none (read-only visualization)
- Retained: React state (layers, points, viewportStats, sitemapEntries) — ephemeral

**Circle:**
- Operator sees map → identifies orphan layer → files BAR to add ctb_node → deploy → next map load shows node attached

## §5 Contract

### MapLayer canonical shape

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| layer_id | TEXT | yes | Unique layer identifier |
| name | TEXT | yes | Display name |
| category | TEXT | yes | Category key (drives CATEGORY_COLORS) |
| branch | TEXT | yes | CTB branch |
| parent_hub | TEXT | no | Parent hub identifier |
| ctb_node | TEXT | no | CTB attachment path; null = orphan |
| architecture_doc | TEXT | no | Link to architecture doc |
| d1_database | TEXT | yes | D1 database name |
| d1_table | TEXT | yes | D1 table name |
| lat_col | TEXT | no | Latitude column name |
| lon_col | TEXT | no | Longitude column name |
| zip_col | TEXT | no | ZIP code column name |
| color_col | TEXT | no | Color data column name |
| color_scale | TEXT | no | Color scale identifier |
| label_col | TEXT | no | Label column name |
| tooltip_cols | TEXT | no | JSON array of tooltip column names |
| marker_color | TEXT | no | Override marker color |
| icon | TEXT | yes | Icon identifier |
| is_active | INTEGER | yes | 1 = active, 0 = inactive |
| is_default_visible | INTEGER | yes | 1 = visible by default |
| sort_order | INTEGER | yes | Render order |
| description | TEXT | no | Layer description |
| filter_sql | TEXT | no | Optional SQL filter clause |

### ViewportStats canonical shape

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| count | INTEGER | no | Point count in viewport |
| avgPriceSqft | FLOAT | yes | Average price per sqft (storage layers) |
| avgOccupancy | FLOAT | yes | Average occupancy % (storage layers) |
| avgSaturation | FLOAT | yes | Average market saturation % |

### CATEGORY_COLORS palette

| Category | Color |
|----------|-------|
| storage | #6366f1 (indigo) |
| insurance | #f59e0b (amber) |
| signals | #10b981 (emerald) |
| deals | #ef4444 (red) |
| sales-stack | #fdba74 (light orange) |
| sales-gates | #f97316 (orange) |
| sales-status | #fb923c (deep orange) |
| svg-outreach | #3b82f6 (blue) |
| svg-sales | #f97316 (orange) |
| svg-client | #22c55e (green) |
| svg-service | #a855f7 (purple) |
| default | #818cf8 (light indigo) |

## §6 Join Contract

**Universal join key:** MapLayer.ctb_node → Barton Enterprises CTB node path

**Join chain:**
```
GET /map/layers → MapLayer[]
  → MapLayer.ctb_node → CTB node attachment
  → MapLayer.d1_database + d1_table → GET /map/points (viewport query)
  → MapPoint[] → CATEGORY_COLORS[category] → dot render

GET /sitemap → SitemapEntry[] (Process 180)
  → SitemapEntry.path → tree node
  → SitemapEntry.depth → indentation level
  → SitemapEntry.parent → parent link
```

**Forbidden paths:**
- Direct D1 reads from MapEngine frontend (no Wrangler bindings on CF Pages)
- Unauthenticated API calls (MC_API_KEY required)
- Rendering more than MAX_POINTS (2000) simultaneously
- Viewport fetches with debounce < DEBOUNCE_MS (500ms)

**Query routing:**
- Layer registry: GET /map/layers (mission-control-api)
- Geographic points: GET /map/points (mission-control-api, viewport-scoped)
- Sitemap tree: GET /sitemap (mission-control-api → Process 180)

## §7 Integration

| Source | Target | Transform |
|--------|--------|-----------|
| MapLayer.category | dot color | CATEGORY_COLORS[category] ?? CATEGORY_COLORS.default |
| MapPoint[] | viewport render | truncate at MAX_POINTS |
| viewport events | fetch trigger | debounce at DEBOUNCE_MS (500ms) |
| ViewportStats.avgPriceSqft (null) | UI display | "N/A" (not "0") |
| MapLayer.ctb_node (null) | UI indicator | orphan warning badge |
| SitemapEntry.depth | tree indentation | depth * indent-unit |
| SitemapEntry.parent | tree hierarchy | parent path → child nesting |

## §8 Ingest Checklist

**Adding a new map layer:**
1. Insert MapLayer row into mission-control D1 with all required fields
2. Set ctb_node to valid Barton Enterprises CTB path (not null if known)
3. Confirm category matches a CATEGORY_COLORS key (or accept default)
4. Confirm is_active = 1 and is_default_visible as intended
5. Open Mission Control Map page → confirm layer appears in layer panel
6. Toggle layer → confirm points render with correct color
7. Confirm ViewportStats display (N/A for null metrics, not zero)

**Stop conditions:**
- Layer appears with default color → category key missing from CATEGORY_COLORS; add to palette via DOCTRINE amendment + code change + BAR
- ctb_node null → layer renders as orphan; file BAR to add ctb_node
- > 2000 points in viewport → MAX_POINTS truncation fires; confirm truncation is visible to operator

**Kill switch:**
- Set MapLayer.is_active = 0 in mission-control D1 → layer disappears from map on next load
- To disable MapEngine entirely: remove Map page route from Mission Control Shell.tsx → redeploy (requires BAR)

## §9 Permissions

| Operation | Path | Auth | Notes |
|-----------|------|------|-------|
| READ layer registry | GET /map/layers | MC_API_KEY (Bearer) | Mission Control CF Access also required |
| READ geographic points | GET /map/points | MC_API_KEY (Bearer) | Viewport-scoped, max 2000 points |
| READ sitemap tree | GET /sitemap | MC_API_KEY (Bearer) | Process 180 data passthrough |
| WRITE any data | n/a | n/a — out of scope | Map is read-only; mutations require separate BAR |

**Three Primitives Check:**
- Thing: MapEngine.tsx component exists in Mission Control CF Pages bundle ✓
- Flow: operator viewport → debounced fetch → mission-control-api → D1 → MapPoint[] → CATEGORY_COLORS → render ✓
- Change: Layer toggle → is_default_visible state change → re-fetch → updated dot set rendered ✓

**Live Verification Log:**
- GET /map/layers → 200 MapLayer[]: verified BAR-323 close
- GET /map/points → 200 MapPoint[] (≤ 2000): verified BAR-323 close
- CATEGORY_COLORS palette rendering: verified BAR-323 close
- CF Access gate (Dave-only): verified via Mission Control CLAUDE.md

## §10 Analytics

**Metrics:**
| Metric | Source | Tolerance |
|--------|--------|-----------|
| Active layer count | GET /map/layers is_active=1 count | matches deployed layer rows |
| Point render count | GET /map/points array length | ≤ MAX_POINTS (2000) |
| Orphan layer count | MapLayer WHERE ctb_node IS NULL | 0 target; > 0 triggers governance review |
| Fetch debounce compliance | DEBOUNCE_MS | ≥ 500ms always |

**Sigma Tracking:**
- Tightening: orphan count → 0; all layers have ctb_node; point renders within MAX_POINTS
- Flat: orphan count stable (no BAR filed to resolve) — governance drift
- Expanding: fetch errors rising — check mission-control-api availability or MC_API_KEY expiry

**ORBT Gate Rules:**
| State | Condition |
|-------|-----------|
| OPERATE | Layers render; points load; sitemap tree displays; no squawks |
| REPAIR | API fetch failures OR orphan layers with no filed BAR OR stats showing zero instead of N/A |
| TROUBLESHOOT_TRAIN | Strike 3 on same failure class |

## §11 Execution Trace

| Date | Action | Operator | Result |
|------|--------|----------|--------|
| 2026-04-30 | BAR-323 shipped — MapEngine.tsx live on Mission Control, CTB map rendering | Dave Barton | PASS — map page operational |
| 2026-04-30 | UT manual backfill (governance) | Claude Code | UT doc written; OPERATE state confirmed |

## §12 Logbook

_After certification only. No entries until auditor certifies._

## §13 Fleet Failure Registry

_No fleet failures recorded._

## §14 Maintenance Logbook

| Date | Action | Operator | Notes |
|------|--------|----------|-------|
| 2026-04-30 | RETROFIT | Claude Code | UT manual backfill for BAR-323; governance only; no code changes |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| Version | 1.0.0 |
| BAR | BAR-323 |
| Status | OPERATE |
| Author | Claude Code (governance backfill) |
| Authority | Dave Barton |
| Template | UNIFIED_TEMPLATE.md v2.0 — 14 sections, 3 clusters |
| UT Checklist | v1.2.0 — 13 items, all addressed |

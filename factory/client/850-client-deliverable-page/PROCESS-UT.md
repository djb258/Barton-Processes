# PROCESS-UT — 850 Client Deliverable Page
# UT Checklist v1.2.0 | BAR-82 | Governance Backfill 2026-04-30

## UT Pre-Flight Checklist

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §2 PURPOSE |
| 2 | OSAM — READ / WRITE / Process Composition / Join Chain / Forbidden / Routing | ☑ | §6 JOIN CONTRACT + §9 PERMISSIONS |
| 3 | Component Status — every dependency has 🟢 / 🟡 / 🔴 with 1-line state | ☑ | §3 RESOURCES |
| 4 | Owner — human who fixes this at 2 AM | ☑ | §1 IDENTITY |
| 5 | Live Dashboard | ☑ | §3 RESOURCES |
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
| process_id | CLIENT-DELIVERABLE-PAGE |
| process_number | 850 |
| name | Client Deliverable Page — Public-Facing Client Hub |
| blueprint_owner | client |
| runtime | CF Pages (React) + mission-control-api CF Worker |
| hub_id | CLIENT-DELIVERABLE-PAGE-850 |
| sovereign_ref | imo-creator |
| ctb_node | barton-enterprises/insurance-informatics/svg-agency/client |
| cc_layer | CC-03 |
| imo_topology | middle |
| BAR | BAR-82 |
| owner | Dave Barton |

## §1b Geometry

```
CF Pages (insuranceinformatics.com)
         │
         ▼
ClientDeliverablePage.tsx  ←── Hub (all rendering logic)
         │
    ┌────┴────────────────────┐
    ▼                         ▼
GET /public/clients/         POST /page-event
slug/:slug                   (lcs-hub beacon)
[mission-control-api]        [lcs-hub]
    │
    ▼
D1_CLIENT (svg-d1-client)
clients CANONICAL table
```

**Hub-Spoke role:** ClientDeliverablePage is the hub. Both API calls are spokes (dumb transport). Component owns all rendering logic; spokes own zero logic.

**Altitude:** Leaf (10K — operational execution). Single-purpose UI component delivering one client view per slug.

---

# CONTRACT

## §2 Purpose

| Field | Value |
|-------|-------|
| WHAT | A public React component that renders a client-specific deliverable dashboard on insuranceinformatics.com, fetched by slug |
| WHY | Clients need a live, branded view of their benefit vendors, service requests, and invoicing status without requiring an authenticated portal |
| WHO | Active insurance clients of SVG Agency; accessed via private slug URL shared by the agency |
| SCOPE | insuranceinformatics.com /clients/:slug route; read-only client data display; LCS event beacon |
| OUT-OF-SCOPE | Client data mutation; authentication flows beyond slug-as-soft-token; non-insuranceinformatics.com domains |
| SUCCESS METRIC | Page renders client data within 1s of slug navigation; LCS beacon fires on every load; error state displays for unknown slugs |

## §3 Resources

### §3a Component Status Grid

| Component | Status | State |
|-----------|--------|-------|
| CF Pages (insuranceinformatics.com) | 🟢 | Live — serves ClientDeliverablePage.tsx at /clients/:slug |
| mission-control-api GET /public/clients/slug/:slug | 🟢 | Live — returns ClientData shape from D1_CLIENT |
| lcs-hub POST /page-event | 🟢 | Live — receives beacon on page load |
| D1_CLIENT (svg-d1-client) | 🟢 | Live — clients CANONICAL table |

### §3b Live Dashboard
Mission Control → Client Hub tab. Slug-based page events visible in LCS delivery dashboard.

### §3c FCEs
| FCE | Attachment |
|-----|-----------|
| Client Hub FCE | Primary — this process IS the client-facing output of the Client Hub |
| LCS FCE | Page-event beacon feeds LCS lifecycle tracking |

### §3d BARs
| BAR | Description | Status |
|-----|-------------|--------|
| BAR-82 | Client Deliverable Page — public slug endpoint + React component + LCS beacon | CLOSED |

### §3e LBB Subjects
- `svg-client` — primary (client deliverable surface)
- `svg-sales` — secondary (feeds from active client records)

## §4 IMO

**Two-Question Intake:**
- What triggers this? A client navigates to their slug URL on insuranceinformatics.com
- How do we get it? Component fetches GET /public/clients/slug/:slug on mount; slug comes from the URL path parameter

**Input:**
- Crossing: slug URL parameter (from browser navigation)
- Initial Condition: React component mounted on CF Pages with CLIENT_HUB_BASE and LCS_HUB_URL constants

**Middle:**
1. Fetch GET /public/clients/slug/:slug from mission-control-api
2. On success: set data state, fire LCS beacon via sendPageEvent()
3. On failure: set error state
4. Render one of three states: loading skeleton → data view or error view

**Output:**
- Emitted: LCS page-event beacon (POST to lcs-hub)
- Retained: React state (data, loading, error) — ephemeral, discarded on unmount

**Circle:**
- LCS beacon feeds back into LCS delivery hub metrics
- Error states surface to Mission Control squawk log
- Sigma tightening: slug navigation success rate + beacon fire rate tracked in LCS

## §5 Contract

### Canonical ClientData shape

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| client_id | TEXT | yes | Unique client identifier (join key) |
| company_name | TEXT | yes | Display name for header |
| employee_count | INTEGER | yes | Displayed in stats row |
| vendors | ARRAY | yes | List of benefit vendors; each has vendor_id, vendor_name, vendor_type |
| open_service_requests | INTEGER | yes | Count; > 0 triggers red accent |
| pending_invoice_count | INTEGER | yes | Count; > 0 triggers orange accent |
| branding_color | TEXT | no | Hex color for accent; defaults to #1a56db |

### LCS beacon payload

| Field | Value |
|-------|-------|
| sovereign_company_id | slug.toUpperCase() |
| communication_id | `CLIENT-${slug.toUpperCase()}` |
| event_type | page_loaded |
| lifecycle_phase | CLIENT_DELIVERABLE |
| page_step | deliverable_view |
| signal_set_hash | `CLIENT-${slug.toUpperCase()}` |
| payload | { slug, company_name } |

## §6 Join Contract

**Universal join key:** slug → sovereign_company_id (uppercase) → client_id

**Join chain:**
```
URL slug
  → GET /public/clients/slug/:slug (mission-control-api)
  → D1_CLIENT.clients WHERE slug = :slug
  → client_id (sovereign join key for all downstream records)
  → vendors[], service_requests, invoices joined on client_id
```

**Forbidden paths:**
- Direct D1 reads from the frontend (no Wrangler bindings on CF Pages)
- Authenticated write operations on the public route
- Slug derivation that produces sequential or predictable values

**Query routing:**
- All reads: mission-control-api GET /public/clients/slug/:slug
- All events: lcs-hub POST /page-event

## §7 Integration

| Source Field | Target Field | Transform |
|-------------|-------------|-----------|
| URL :slug param | fetch URL path | encodeURIComponent() |
| ClientData.company_name | header display | direct render |
| ClientData.branding_color | CSS accent | null → #1a56db default |
| ClientData.open_service_requests | stat card accent | > 0 → #e3342f |
| ClientData.pending_invoice_count | stat card accent | > 0 → #f6993f |
| slug | LCS sovereign_company_id | .toUpperCase() |
| ClientData.company_name | LCS payload.company_name | direct |

## §8 Ingest Checklist

**Pre-flight (before deploying a new client slug):**
1. Confirm client record exists in D1_CLIENT.clients with a valid slug field
2. Confirm slug is non-sequential and non-guessable
3. Confirm ClientData fields are populated (company_name, employee_count, vendors, open_service_requests, pending_invoice_count)
4. Navigate to /clients/:slug — confirm data state renders (not error state)
5. Confirm LCS beacon fires (check lcs-hub logs for page_loaded event)

**Stop conditions:**
- Slug returns 404 from mission-control-api → ErrorState renders (correct behavior)
- ClientData shape missing required fields → rendering gaps; fix backend response
- LCS beacon not firing → check lcs-hub availability; check sendPageEvent() payload shape

**Kill Switch:**
- To disable a client page: remove or invalidate the slug in D1_CLIENT.clients
- To disable all public client reads: add auth gate to GET /public/clients/slug/:slug in mission-control-api (requires BAR)
- There is no CF Pages route-level kill without a deploy; use mission-control-api auth gate as the fast kill

## §9 Permissions

| Operation | Path | Auth | Notes |
|-----------|------|------|-------|
| READ client data | GET /public/clients/slug/:slug | none — slug-as-soft-token | Non-guessable slug is the access control |
| EMIT LCS beacon | POST /page-event (lcs-hub) | none — event logging only | No sensitive data in payload |
| WRITE client data | mission-control-api authenticated write paths | Bearer token | Out of scope for this component |

**Three Primitives Check:**
- Thing: ClientDeliverablePage component exists at /clients/:slug route ✓
- Flow: slug → mission-control-api → D1_CLIENT → ClientData → React state ✓
- Change: React state transitions (loading → data | error) trigger correct render ✓

**Live Verification Log:**
- GET /public/clients/slug/:slug → 200 with ClientData shape: verified BAR-82 close
- POST /page-event beacon fires on data load: verified BAR-82 close

## §10 Analytics

**Metrics:**
| Metric | Source | Tolerance |
|--------|--------|-----------|
| Slug navigation success rate | LCS page-event count / slug navigations | > 95% |
| Beacon fire rate | LCS page_loaded events / successful data loads | 100% |
| Error state rate | ErrorState renders / total slug navigations | < 5% |

**Sigma Tracking:**
- Tightening: LCS beacon fire rate approaching 100%; error state rate approaching 0%
- Flat: beacon rate stable but not improving — check navigator.sendBeacon() fallback
- Expanding: error rate rising — check mission-control-api availability or D1_CLIENT schema

**ORBT Gate Rules:**
| State | Condition |
|-------|-----------|
| OPERATE | Error rate < 5%, beacon rate > 95%, no squawks open |
| REPAIR | Error rate > 5% OR beacon not firing OR missing slug records |
| TROUBLESHOOT_TRAIN | Strike 3 on same failure class |

## §11 Execution Trace

| Date | Action | Operator | Result |
|------|--------|----------|--------|
| 2026-04-30 | BAR-82 shipped — ClientDeliverablePage.tsx + GET /public/clients/slug/:slug + LCS beacon | Dave Barton | PASS — component live on insuranceinformatics.com |
| 2026-04-30 | UT manual backfill (governance) | Claude Code | UT doc written; OPERATE state confirmed |

## §12 Logbook

_After certification only. No entries until auditor certifies._

## §13 Fleet Failure Registry

_No fleet failures recorded._

## §14 Maintenance Logbook

| Date | Action | Operator | Notes |
|------|--------|----------|-------|
| 2026-04-30 | RETROFIT | Claude Code | UT manual backfill for BAR-82; governance only; no code changes |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| Version | 1.0.0 |
| BAR | BAR-82 |
| Status | OPERATE |
| Author | Claude Code (governance backfill) |
| Authority | Dave Barton |
| Template | UNIFIED_TEMPLATE.md v2.0 — 14 sections, 3 clusters |
| UT Checklist | v1.2.0 — 13 items, all addressed |

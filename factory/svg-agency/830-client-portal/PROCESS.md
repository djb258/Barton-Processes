# PROCESS: CLIENT PORTAL
## Renders audience-specific HTML pages for each client, branded per client record, served at app.svgagency.com/:slug/:page
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-830 |
| Name | Client Portal |
| Business Silo | svg-agency |
| CTB Position | factory/svg-agency/830-client-portal |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed |
| BAR Reference | — |
| Deployed URL | https://client-portal-830.svg-outreach.workers.dev (production: app.svgagency.com) |
| Cron | none — HTTP-triggered |
| Runtime | CF Worker |

---

## 2. WHY THIS EXISTS

Without this process, there is no client-facing view of the data SVG Agency collects and manages. Every upstream process (800 Client Mint, 810 Client Intake) builds the canonical client record, but none of them present it to the audience that needs to act on it — the client's CEO, HR team, underwriter, or the internal service agent.

This is the terminal egress point for the svg-agency client data pipeline. It converts rows in D1 into branded HTML that five distinct audiences can read (and in one case, write to). If this doesn't work, clients have no self-service visibility and every question becomes a phone call.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** — User navigates to app.svgagency.com/:slug/:page (HTTP GET). Agent page also accepts HTTP POST for ticket status updates.
2. **"How do we get it?"** — Resolve slug to client_id from shared D1 (client-intake-810 database), query page-specific tables, render server-side HTML.

### Input
- HTTP request with URL path containing two segments: slug (client identifier) and page (audience view)
- Slug resolves to a `ClientContext` from the `client` table in D1 (shared with 810)
- ClientContext provides: client_id, slug, legal_name, label_override, logo_url, color_primary, color_accent, status

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | HTTP request URL | Parse path into slug + page segments. Validate page is one of 5 known values. | slug, page strings | CF Worker router |
| 2 | slug | Query `client` table WHERE slug = ?. Return ClientContext or null. | ClientContext (branding + client_id) or 404 | D1 query |
| 3 | page + client_id | Route to page-specific renderer (renewal, ceo, hr, underwriting, agent) | Raw HTML body for that audience | Page renderer function |
| 4 | HTML body + ClientContext | Wrap body in layout template with client branding (logo, colors, nav) | Full HTML document | layout.ts renderPage() |
| 5 | Full HTML | Return Response with Content-Type text/html | HTTP 200 response | CF Worker |
| 5a | POST /:slug/agent/ticket/:id/status | Validate status transition, update ticket record in D1 | JSON success/error response | D1 write |

### Output
- HTML page rendered with client branding, served to the requesting browser
- For agent POST: JSON response confirming ticket status update
- No downstream data consumers — this is terminal

### Circle (Bedrock S5)
No automated feedback loop. The circle closes through human observation: the audience reads the page, identifies issues (wrong data, missing info), and reports back through the agent page's service request system or direct communication. Agent page ticket updates feed back into 810's canonical data.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| client-intake-810 | D1 | (same as 810 — not yet set in wrangler.toml) | READ + ticket WRITE | client table (slug resolution, branding), plan, plan_quote, person, election, census, service_request |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| CF Worker | Runtime | Free | none | Serves HTTP requests, renders HTML |
| D1 | Database | Free | Binding (wrangler.toml) | All reads and ticket writes |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| (none) | — | — | — |

No secrets required. This process reads from a shared D1 binding and renders HTML. No external API calls.

**Tool Priority (Well Drinks First):**
1. D1 (free, already bound) — only data source needed

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| client | Slug resolution, branding (label_override, logo_url, color_primary, color_accent), legal_name, status | client.slug (resolution), client.client_id (all pages) |
| plan | Plan details for renewal page | client_id |
| plan_quote | Quote/rate data for renewal and underwriting pages | client_id |
| person | People records for HR page | client_id |
| election | Benefit elections for HR page | client_id |
| service_request | Ticket data for agent page | client_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| service_request | Ticket status updates (status column) | POST /:slug/agent/ticket/:id/status |

### Join Chain

```
client.slug (URL resolution)
  → client.client_id
    → plan (client_id — renewal page)
    → plan_quote (client_id — renewal, underwriting pages)
    → person (client_id — HR page)
    → election (client_id — HR page)
    → service_request (client_id — agent page)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Write to any table except service_request.status | 830 is a read layer. Only agent ticket updates are allowed. |
| Direct write to client table | Client records are owned by 800 Client Mint and 810 Client Intake |
| Cross-client data access | Each slug resolves to exactly one client_id. No page may query data outside that client_id. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| What client does this slug belong to? | client | slug → client_id |
| What is the client's display name? | client | label_override, legal_name |
| What branding to apply? | client | logo_url, color_primary, color_accent |
| What plans does this client have? | plan | client_id |
| What are the current rates? | plan_quote | client_id |
| Who is enrolled? | person, election | client_id |
| What service tickets exist? | service_request | client_id |

---

## 6. CONSTANTS & VARIABLES (Bedrock S2)

### Constants (structure — never changes)

- **5 pages, 5 audiences:** renewal (client), ceo (CEO), hr (HR), underwriting (underwriter), agent (internal). Fixed set.
- **Slug-based routing:** URL pattern is always /:slug/:page. Two segments, no exceptions.
- **Display name rule:** label_override || legal_name. Branding fallback: #1a365d primary, #3182ce accent.
- **Read-only default:** All pages are read-only. Only agent page has a write path (ticket status).
- **Server-side HTML:** No SPA framework. CF Worker renders full HTML documents.
- **Shared D1 with 810:** Single database binding. 830 adds the slug column; all other schema owned by 810.
- **ClientContext shape:** client_id, slug, legal_name, label_override, logo_url, color_primary, color_accent, status.

### Variables (fill — changes every run)

- Which slug is requested (determines which client)
- Which page is requested (determines which renderer)
- Client branding values (logo_url, colors — different per client)
- Page data (plans, people, tickets — different per client, changes over time)
- Ticket status value on POST (the new status being set)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Slug not found in D1 | Return 404 — do not guess or fall back |
| Page segment not in known set (renewal, ceo, hr, underwriting, agent) | Return 404 with valid page list |
| POST to non-agent path | Return 404 — only agent page accepts writes |
| POST body missing status field | Return 400 — status required |
| Invalid status transition on ticket update | Return 400 — reject with reason |
| D1 query failure | Return 500 — log error, do not render partial page |
| D1 database_id not configured in wrangler.toml | HALT — cannot deploy until binding is set to 810's D1 ID |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| 800 Client Mint | Client record must exist in D1 `client` table with slug assigned | DONE (process exists; slug assignment is manual) |
| 810 Client Intake | Canonical data — plans, people, elections, vendors, service requests | DONE (process exists; data populates shared D1) |
| D1 migration 001_add_slug.sql | slug column + unique index on client table | PENDING (migration written, needs execution) |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| (none) | Terminal process — renders HTML to browser. No downstream data consumers. |

---

## 9. SMOKE TEST

```
1. GET /health → expected: {"process":"PROC-CLIENT-PORTAL","number":830,"status":"ok"}
2. GET / → expected: 200 with route listing text
3. GET /nonexistent-slug/renewal → expected: 404 "Client not found"
4. GET /valid-slug/bogus-page → expected: 404 with valid page list
5. GET /valid-slug/renewal → expected: 200 HTML with client branding in header
6. GET /valid-slug/ceo → expected: 200 HTML with CEO-specific data
7. GET /valid-slug/hr → expected: 200 HTML with people/election data
8. GET /valid-slug/underwriting → expected: 200 HTML with census data
9. GET /valid-slug/agent → expected: 200 HTML with service request table
10. POST /valid-slug/agent/ticket/123/status {"status":"resolved"} → expected: 200 JSON success
11. POST /valid-slug/agent/ticket/123/status {} → expected: 400 "status required"
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** Does the client record exist with slug, branding columns, and status?
2. **Flow:** Does the slug resolve to client_id, and does client_id reach the page renderer with correct data?
3. **Change:** Does the layout template correctly inject branding (logo, colors, display name) and does each page render the right data for its audience?

If any fails — that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock S6).

---

## 10. LOGBOOK

_No entries yet. Process is in BUILD state._

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | D1 database_id blank in wrangler.toml | 830 shares 810's D1 but ID not copied to config | Copy 810's D1 database_id into 830's wrangler.toml | 0 |
| 2 | 2026-03-29 | No authentication per audience | No auth layer built yet — any visitor can access any page if they know the slug | Needs CF Access rules or token-based auth per audience role | 0 |
| 3 | 2026-03-29 | Slug generation not automated | Slugs must be manually set on client records | Needs slug auto-generation in 800 Client Mint or 810 Client Intake | 0 |
| 4 | 2026-03-29 | No branding asset storage | logo_url column exists but no R2 bucket or CDN for client logos | Needs R2 bucket or external CDN integration | 0 |

---

## 12. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | Initial PROCESS.md created. Documented IMO, OSAM, C&V, dependencies, known issues. BUILD state. | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | factory/svg-agency/830-client-portal (local — no hub OSAM yet) |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

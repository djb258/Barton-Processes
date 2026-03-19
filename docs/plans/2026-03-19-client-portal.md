# Client Portal (830) Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CF Worker serving 5 client-facing pages (renewal, CEO, HR, underwriting, service agent) with path-based routing, shared D1, and client branding.

**Architecture:** Single CF Worker at `app.svgagency.com/:slug/:page`. Resolves slug to client_id from D1 (shared with 810). Server-side HTML rendering with client branding. All pages read-only except service agent (ticket status updates). Each page is a self-contained module in `src/pages/`.

**Tech Stack:** Cloudflare Workers, D1 (shared with 810), TypeScript, server-side HTML

**Spec:** `docs/specs/2026-03-19-client-portal-design.md`

---

## File Structure

```
factory/830-client-portal/
├── heir.yaml                    # Process identity
├── wrangler.toml                # CF Worker config (shared D1 binding)
├── package.json                 # Dependencies
├── tsconfig.json                # TypeScript config
└── src/
    ├── index.ts                 # CF Worker entry — route resolution
    ├── resolve.ts               # Slug → client_id + branding lookup
    ├── templates/
    │   └── layout.ts            # Shared HTML shell with branding injection
    ├── pages/
    │   ├── renewal.ts           # Renewal: plans + quotes + rate comparison
    │   ├── ceo.ts               # CEO: cost overview + headcount + tickets
    │   ├── hr.ts                # HR: roster + elections + enrollment + tickets
    │   ├── underwriting.ts      # Underwriting: census + coverage + tier distribution
    │   └── agent.ts             # Service agent: tickets + status updates (read-write)
    └── migrations/
        └── 001_add_slug.sql     # Add slug column to client table
```

---

## Task 1: Scaffold + Slug Migration

**Files:**
- Create: `factory/830-client-portal/heir.yaml`
- Create: `factory/830-client-portal/wrangler.toml`
- Create: `factory/830-client-portal/package.json`
- Create: `factory/830-client-portal/tsconfig.json`
- Create: `factory/830-client-portal/src/migrations/001_add_slug.sql`

- [ ] **Step 1: Create heir.yaml**

```yaml
# HEIR — 830 Client Portal
process_id: "PROC-CLIENT-PORTAL"
process_number: "830"
name: "Client Portal"
blueprint_owner: "client"
runtime: "cloudflare-workers"
status: "build"
sovereign_ref: "imo-creator-v2"
governing_engine: "law/doctrine/TIER0_DOCTRINE.md"
ctb_placement: "leaf"
cc_layer: "CC-04"
imo_topology: "egress"

services:
  - "CF Worker (HTTP)"
  - "D1 (shared with 810 — read + ticket writes)"
secrets_provider: "doppler"

two_question_intake:
  what_triggers: "User navigates to app.svgagency.com/:slug/:page"
  how_do_we_get_it: "Resolve slug to client_id from D1, query page data, render HTML"

pages:
  - {route: "/:slug/renewal", audience: "Client", access: "read-only"}
  - {route: "/:slug/ceo", audience: "Client CEO", access: "read-only"}
  - {route: "/:slug/hr", audience: "Client HR", access: "read-only"}
  - {route: "/:slug/underwriting", audience: "Stop-loss underwriter", access: "read-only"}
  - {route: "/:slug/agent", audience: "Internal (Dave's team)", access: "read-write"}

acceptance_criteria:
  - "Slug resolves to client_id from shared D1"
  - "Unknown slug returns 404"
  - "Each page renders with client branding (logo, colors)"
  - "All pages read-only except agent (ticket status updates)"
  - "Agent validates status transitions before writing"
  - "Server-side HTML — no SPA framework"

depends_on: [810]
feeds: []
```

- [ ] **Step 2: Create wrangler.toml**

```toml
name = "client-portal-830"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[[d1_databases]]
binding = "D1"
database_name = "client-intake-810"
database_id = ""  # Same D1 as 810

[vars]
# No secrets needed — reads from shared D1
```

- [ ] **Step 3: Create package.json**

```json
{
  "name": "client-portal-830",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "d1:add-slug": "wrangler d1 execute client-intake-810 --file=src/migrations/001_add_slug.sql"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20241218.0",
    "typescript": "^5.7.0",
    "wrangler": "^4.0.0"
  }
}
```

- [ ] **Step 4: Create tsconfig.json** (same as 800/810/820)

- [ ] **Step 5: Create slug migration**

```sql
-- 830 — Add slug column to client table (shared D1 with 810)
ALTER TABLE client ADD COLUMN slug TEXT UNIQUE;
CREATE INDEX IF NOT EXISTS idx_client_slug ON client(slug);
```

- [ ] **Step 6: Commit**

```bash
git add factory/830-client-portal/
git commit -m "feat: scaffold 830-client-portal — heir, wrangler, slug migration"
```

---

## Task 2: Resolve + Layout

**Files:**
- Create: `factory/830-client-portal/src/resolve.ts`
- Create: `factory/830-client-portal/src/templates/layout.ts`

- [ ] **Step 1: Create resolve.ts — slug lookup + branding**

Exports:
- `interface ClientContext { client_id, legal_name, slug, logo_url, color_primary, color_accent, label_override }`
- `async function resolveClient(d1, slug): Promise<ClientContext | null>`

Queries D1 `client` table by slug. Returns null if not found.

- [ ] **Step 2: Create layout.ts — shared HTML template**

Exports:
- `function renderPage(client: ClientContext, pageTitle: string, bodyHtml: string): string`

Returns complete HTML document with:
- `<!DOCTYPE html>` + viewport meta
- Client branding: logo in header, primary/accent colors as CSS variables
- Navigation: links to all 5 pages for this client (using slug)
- Page title in header
- Body content slot
- Minimal CSS — clean, professional, no framework

- [ ] **Step 3: Commit**

```bash
git add factory/830-client-portal/src/resolve.ts factory/830-client-portal/src/templates/layout.ts
git commit -m "feat: 830 resolve + layout — slug lookup, branded HTML shell"
```

---

## Task 3: Renewal Page

**Files:**
- Create: `factory/830-client-portal/src/pages/renewal.ts`

- [ ] **Step 1: Create renewal.ts**

Exports:
- `async function renderRenewal(d1: D1Database, clientId: string): Promise<string>`

Queries:
- `SELECT * FROM plan WHERE client_id = ? AND status = 'active' ORDER BY benefit_type`
- `SELECT * FROM plan_quote WHERE client_id = ? ORDER BY benefit_type, effective_year DESC, carrier_id`

Renders:
- Current plans table: benefit_type, carrier_id, rate_ee/es/ec/fam, employer contributions, effective_date
- Renewal quotes table: grouped by benefit_type, showing carrier, year, quoted rates
- Rate delta column: `quote.rate_ee - plan.rate_ee` for each tier (computed inline, color-coded: green=decrease, red=increase)

Returns HTML string (body content only — layout.ts wraps it).

- [ ] **Step 2: Commit**

```bash
git add factory/830-client-portal/src/pages/renewal.ts
git commit -m "feat: 830 renewal page — plans, quotes, rate comparison"
```

---

## Task 4: CEO Dashboard

**Files:**
- Create: `factory/830-client-portal/src/pages/ceo.ts`

- [ ] **Step 1: Create ceo.ts**

Exports:
- `async function renderCeo(d1: D1Database, clientId: string): Promise<string>`

Queries:
- `SELECT * FROM client WHERE client_id = ?` — identity
- `SELECT benefit_type, COUNT(*) as plan_count FROM plan WHERE client_id = ? AND status = 'active' GROUP BY benefit_type`
- `SELECT COUNT(*) as headcount FROM person WHERE client_id = ? AND status = 'active'`
- `SELECT status, COUNT(*) as cnt FROM service_request WHERE client_id = ? GROUP BY status`

Renders:
- Company header (name, effective_date, status)
- Benefits summary cards (plan count by type)
- Headcount number
- Service ticket summary (open/in_progress/resolved counts)

- [ ] **Step 2: Commit**

```bash
git add factory/830-client-portal/src/pages/ceo.ts
git commit -m "feat: 830 CEO dashboard — cost overview, headcount, tickets"
```

---

## Task 5: HR Portal

**Files:**
- Create: `factory/830-client-portal/src/pages/hr.ts`

- [ ] **Step 1: Create hr.ts**

Exports:
- `async function renderHr(d1: D1Database, clientId: string): Promise<string>`

Queries:
- `SELECT * FROM person WHERE client_id = ? ORDER BY last_name, first_name`
- `SELECT e.*, p.benefit_type, p.carrier_id FROM election e JOIN plan p ON e.plan_id = p.plan_id WHERE e.client_id = ?`
- `SELECT * FROM enrollment_intake WHERE client_id = ? ORDER BY upload_date DESC LIMIT 10`
- `SELECT * FROM service_request WHERE client_id = ? AND status IN ('open','in_progress') ORDER BY opened_at DESC`

Renders:
- Employee roster table (name, status, elected plans with coverage tier)
- Recent enrollment batches (date, status, record count)
- Open service tickets list

- [ ] **Step 2: Commit**

```bash
git add factory/830-client-portal/src/pages/hr.ts
git commit -m "feat: 830 HR portal — roster, elections, enrollment, tickets"
```

---

## Task 6: Underwriting Page

**Files:**
- Create: `factory/830-client-portal/src/pages/underwriting.ts`

- [ ] **Step 1: Create underwriting.ts**

Exports:
- `async function renderUnderwriting(d1: D1Database, clientId: string): Promise<string>`

Queries:
- `SELECT COUNT(*) as total, SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) as active FROM person WHERE client_id = ?`
- `SELECT coverage_tier, COUNT(*) as cnt FROM election e JOIN plan p ON e.plan_id = p.plan_id WHERE e.client_id = ? GROUP BY coverage_tier`
- `SELECT benefit_type, COUNT(*) as enrolled FROM election e JOIN plan p ON e.plan_id = p.plan_id WHERE e.client_id = ? GROUP BY benefit_type`
- `SELECT * FROM plan WHERE client_id = ? AND status = 'active'`

Renders:
- Census summary (total employees, active, terminated)
- Tier distribution table (EE/ES/EC/FAM counts and percentages)
- Enrollment by benefit type (medical, dental, vision, life — counts)
- Current plan details (carrier, rates, effective dates)

- [ ] **Step 2: Commit**

```bash
git add factory/830-client-portal/src/pages/underwriting.ts
git commit -m "feat: 830 underwriting — census, tier distribution, coverage"
```

---

## Task 7: Service Agent Dashboard (Read-Write)

**Files:**
- Create: `factory/830-client-portal/src/pages/agent.ts`

- [ ] **Step 1: Create agent.ts**

Exports:
- `async function renderAgent(d1: D1Database, clientId: string): Promise<string>`
- `async function updateTicketStatus(d1: D1Database, ticketId: string, newStatus: string): Promise<{ success: boolean; error?: string }>`

Queries (read):
- `SELECT * FROM service_request WHERE client_id = ? ORDER BY CASE status WHEN 'open' THEN 1 WHEN 'in_progress' THEN 2 WHEN 'resolved' THEN 3 ELSE 4 END, opened_at DESC`
- `SELECT * FROM service_error WHERE client_id = ? ORDER BY created_at DESC LIMIT 20`

Write (updateTicketStatus):
- Validate status transition: open → in_progress → resolved → closed (forward only)
- `UPDATE service_request SET status = ?, updated_at = datetime('now') WHERE service_request_id = ? AND client_id = ?`
- Invalid transition → return error

Renders:
- Tickets table with status badges (color-coded)
- Action button per ticket (next valid status transition)
- Ticket counts by status
- Recent errors panel
- Minimal JS: button click → fetch POST → reload page

- [ ] **Step 2: Commit**

```bash
git add factory/830-client-portal/src/pages/agent.ts
git commit -m "feat: 830 service agent — ticket dashboard with status updates"
```

---

## Task 8: Worker Entry Point (Router)

**Files:**
- Create: `factory/830-client-portal/src/index.ts`

- [ ] **Step 1: Create index.ts — route resolver**

```
GET  /health                         → health check
GET  /:slug/:page                    → resolve slug → render page
POST /:slug/agent/ticket/:id/status  → update ticket status
```

Flow:
1. Parse URL path
2. `/health` → return JSON
3. Extract slug and page from path
4. `resolveClient(d1, slug)` → 404 if null
5. Switch on page name:
   - `renewal` → `renderRenewal(d1, clientId)`
   - `ceo` → `renderCeo(d1, clientId)`
   - `hr` → `renderHr(d1, clientId)`
   - `underwriting` → `renderUnderwriting(d1, clientId)`
   - `agent` → `renderAgent(d1, clientId)`
   - default → 404
6. Wrap in `renderPage(client, pageTitle, bodyHtml)`
7. Return HTML response with `Content-Type: text/html`

POST handler for ticket updates:
1. Extract slug, ticket ID from path
2. Resolve client (verify slug)
3. Parse body `{ status }`
4. Call `updateTicketStatus(d1, ticketId, status)`
5. Return JSON result

- [ ] **Step 2: Commit**

```bash
git add factory/830-client-portal/src/index.ts
git commit -m "feat: 830 index.ts — route resolver, page dispatch, ticket POST"
```

---

## Task 9: Update Registry

**Files:**
- Modify: `law/process-registry.yaml`
- Modify: `law/heir.yaml`
- Modify: `law/orbt.yaml`

- [ ] **Step 1: Add 830 to process-registry.yaml**

- [ ] **Step 2: Add 830 to heir.yaml processes list**

- [ ] **Step 3: Update orbt.yaml with note**

- [ ] **Step 4: Commit**

```bash
git add law/process-registry.yaml law/heir.yaml law/orbt.yaml
git commit -m "ops: register 830-client-portal in registry + HEIR/ORBT"
```

---

## Task 10: Log to imo-brain

- [ ] **Step 1: POST session record to imo-brain**

Log: 830 client portal built, 5 pages, shared D1 with 810, SSR HTML, client branding, service agent read-write for tickets.

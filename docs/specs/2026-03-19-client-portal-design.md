# Client Portal (830) — Design Spec

## Governing Engine

| Field | Value |
|-------|-------|
| Sovereign | imo-creator-v2 |
| Doctrine | Tier 0 (TIER0_DOCTRINE.md) |
| Blueprint Repo | djb258/client (client-subhive) |
| Execution Repo | djb258/Barton-Processes |
| Process Number | 830 |
| Runtime | Cloudflare Workers |

---

## Architecture

Single CF Worker serving client-facing pages at `app.svgagency.com/:client-slug/:page`. Path-based routing. All pages read from D1 (working layer). One exception: the service agent page can update ticket status.

### URL Pattern

```
app.svgagency.com/:slug/renewal        → Renewal page
app.svgagency.com/:slug/ceo            → CEO dashboard
app.svgagency.com/:slug/hr             → HR portal
app.svgagency.com/:slug/underwriting   → Underwriting census
app.svgagency.com/:slug/agent          → Service agent dashboard
```

### Resolution Flow

1. Worker receives request
2. Extract `slug` from URL path
3. Query D1: `SELECT client_id, legal_name, logo_url, color_primary, color_accent FROM client WHERE slug = ?`
4. Unknown slug → 404
5. Extract `page` from URL path
6. Unknown page → 404
7. Query D1 for page-specific data using client_id
8. Render HTML with client branding
9. Return response

---

## Pages

### Renewal

| Field | Value |
|-------|-------|
| Route | `/:slug/renewal` |
| Audience | Client (CEO/HR), broker |
| Access | Read-only |

**Data (D1 queries):**
- `plan` WHERE client_id — current active plans with rates (EE/ES/EC/FAM, employer contributions)
- `plan_quote` WHERE client_id — renewal quotes by benefit type, carrier, year
- Rate comparison: current plan rates vs quote rates (computed in Worker, not stored)

**View:**
- Current plans table (benefit type, carrier, rates by tier)
- Renewal quotes table (side-by-side rate comparisons)
- Rate delta (increase/decrease per tier)
- Renewal timeline (effective dates)

---

### CEO Dashboard

| Field | Value |
|-------|-------|
| Route | `/:slug/ceo` |
| Audience | Client CEO |
| Access | Read-only |

**Data (D1 queries):**
- `client` WHERE client_id — company identity, branding
- `plan` WHERE client_id — plan summary (count by benefit type, total cost estimate)
- `person` WHERE client_id — headcount (active employees)
- `service_request` WHERE client_id — open ticket count

**View:**
- Company header (name, logo, branding)
- Benefits at a glance (plan count, types, total monthly cost estimate)
- Headcount summary
- Open service tickets (count only, no detail)

---

### HR Portal

| Field | Value |
|-------|-------|
| Route | `/:slug/hr` |
| Audience | Client HR |
| Access | Read-only |

**Data (D1 queries):**
- `person` WHERE client_id — employee roster (name, status)
- `election` JOIN plan WHERE client_id — elections with plan details and coverage tier
- `enrollment_intake` WHERE client_id — recent intake batch status
- `service_request` WHERE client_id — open tickets

**View:**
- Employee roster table (name, status, elected plans, coverage tier)
- Enrollment status (recent batches — pending/completed/failed)
- Open service tickets list

---

### Underwriting

| Field | Value |
|-------|-------|
| Route | `/:slug/underwriting` |
| Audience | Stop-loss carrier underwriter |
| Access | Read-only |

**Data (D1 queries):**
- `person` WHERE client_id — census (headcount, active/terminated breakdown)
- `election` JOIN plan WHERE client_id — enrollment by benefit type and coverage tier
- `plan` WHERE client_id — current coverage details and rates

**View:**
- Census summary (total employees, active count, dependent count via election tiers)
- Enrollment by benefit type (medical, dental, vision, life — counts per tier)
- Current plan details (carrier, rates, effective dates)
- Demographics rollup (tier distribution: EE/ES/EC/FAM percentages)

---

### Service Agent Dashboard

| Field | Value |
|-------|-------|
| Route | `/:slug/agent` |
| Audience | Dave's team (internal) |
| Access | **Read-write** — ticket status updates |

**Data (D1 queries):**
- `service_request` WHERE client_id — all tickets with status, category, opened_at
- `service_error` WHERE client_id — recent errors

**Write operations:**
- `POST /:slug/agent/ticket/:id/status` — body: `{ status }` → update service_request.status
- Valid transitions: open → in_progress → resolved → closed
- Worker validates transition before writing
- Invalid transition → 400 error

**View:**
- Open tickets table (category, status, age)
- Action buttons per ticket (advance status)
- Recent errors panel
- Ticket counts by status (open, in_progress, resolved, closed)

---

## Slug Management

Add `slug` column to D1 client table (TEXT, UNIQUE, NOT NULL). Set during 800 mint or manually updated.

**Slug rules:**
- URL-safe: lowercase, alphanumeric, hyphens only
- Unique across all clients
- Human-readable (e.g., `acme-corp`, `johnson-mfg`)
- Derived from legal_name by default (slugified), can be overridden

**Migration:** Add to 800's D1 schema:
```sql
ALTER TABLE client ADD COLUMN slug TEXT UNIQUE;
CREATE INDEX IF NOT EXISTS idx_client_slug ON client(slug);
```

---

## Client Branding

Each page renders with client-specific branding pulled from `client` table:

| Field | Usage |
|-------|-------|
| `legal_name` | Page header |
| `logo_url` | Header logo |
| `color_primary` | Header background, accent elements |
| `color_accent` | Buttons, links |
| `label_override` | Display name (if different from legal_name) |

Branding is read from D1 on every request (cached in Worker memory for the request lifecycle). No separate KV needed — it's already in the client record.

---

## Shared D1

830 binds to the same D1 database as 810 (client-intake-810). Read-only access for all pages except service agent ticket updates.

**Why shared D1:**
- Data is always current (no sync lag)
- No duplication
- Read-only pages have zero conflict risk
- Service agent writes are controlled (single column updates via Worker validation)

**wrangler.toml binding:**
```toml
[[d1_databases]]
binding = "D1"
database_name = "client-intake-810"
database_id = ""  # Same D1 as 810
```

---

## Rendering

Server-side HTML. No SPA framework. Each page is a TypeScript function that:

1. Queries D1 for page-specific data
2. Applies client branding
3. Returns complete HTML response

**Why SSR, not SPA:**
- Zero client-side JS needed for read-only pages (except agent dashboard)
- Faster initial load
- Simpler — no build step, no hydration, no client-side state
- CF Worker edge rendering is fast
- Agent dashboard gets minimal JS for ticket status buttons (fetch POST)

---

## Auth (Deferred)

No auth for now. Pages are accessible by URL. Auth will be added later.

**Future plan (not built now):**
- CF Access for internal pages (agent)
- Magic links or email OTP for external pages (renewal, ceo, hr, underwriting)
- Role-based: slug + page determines what's visible

---

## Two-Question Intake

- **What triggers this?** User navigates to `app.svgagency.com/:slug/:page`
- **How do we get it?** Resolve slug → client_id from D1, query page-specific data, render HTML

---

## Tier 0 Gate Validation

| Gate | Validator | Result |
|------|-----------|--------|
| Gate 1 — IMO | Ingress: HTTP request with slug+page. Middle: resolve client, query data, render. Egress: HTML response. | PASS |
| Gate 1 — CTB | Process in factory/ silo. Portal is egress view of client sub-hub data. | PASS |
| Gate 1 — Circle | Service agent writes feed back to service_request table → visible on HR page → circle closes. | PASS |
| Gate 2 — CTB Position | factory/830-client-portal/ in Barton-Processes | PASS |
| Gate 3 — CQRS | Read-only for 4 pages. Agent write is a controlled status update on service_request (existing canonical table). | PASS |

---

## Data Flow

```
810 D1 (canonical working tables — all 16 clnt tables)
       |
       | read-only (except service_request status updates)
       v
830 CF Worker (client-portal-830)
       |
       | 1. resolve slug → client_id
       | 2. query D1 by client_id + page type
       | 3. apply client branding
       | 4. render server-side HTML
       |
       v
Browser: app.svgagency.com/acme-corp/renewal
```

---

## File Structure

```
factory/830-client-portal/
├── heir.yaml
├── wrangler.toml
├── package.json
├── tsconfig.json
└── src/
    ├── index.ts              # CF Worker entry — route resolution
    ├── resolve.ts            # Slug → client_id lookup + branding
    ├── pages/
    │   ├── renewal.ts        # Renewal page data + HTML
    │   ├── ceo.ts            # CEO dashboard data + HTML
    │   ├── hr.ts             # HR portal data + HTML
    │   ├── underwriting.ts   # Underwriting census data + HTML
    │   └── agent.ts          # Service agent dashboard + ticket writes
    └── templates/
        └── layout.ts         # Shared HTML layout with branding
```

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-19 |
| Status | DRAFT — awaiting human approval |
| Authority | imo-creator-v2 (Sovereign) |
| Governing Engine | law/doctrine/TIER0_DOCTRINE.md |
| CTB Position | docs/specs/ (leaf — documentation silo) |

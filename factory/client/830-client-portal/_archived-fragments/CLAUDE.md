> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — Process 830: Client Portal

## Status: SKELETON (2026-04-22)

This Pages project is a visual skeleton. All routes + screens render with mock data.
No backend wiring yet. See README.md for the WIRE-HERE punch list.

Governing UT: `Barton-Processes/factory/client/UT_PROCESSES.md` v1.2.0 (CERTIFIED)
Blueprint: `client/docs/UT_BLUEPRINT.md` v1.2.0 (CERTIFIED)

---

## Governing Doctrine

**Before any work on this process, read and follow:**

1. `law/doctrine/FOUNDATIONAL_BEDROCK.md` — The engine (Three Primitives, C\&V, IMO, CTB, Circle, Troubleshooting Loop, Tier 0, Aviation Model)
2. `bedrock/math-01-engine.md` — P(x;θ) decision equation (FROZEN)
3. `bedrock/math-02-adapter-template.md` — Domain adapter interface

**Pre-flight (every session):**
- Two-Question Intake: "What triggers this?" and "How do we get it?"
- C\&V Test: Can you name it? Format it? → constant. The value filling it → variable.
- Four-Element Validation: IMO + CTB + Circle simultaneously
- Three Primitives: Thing (exists?), Flow (reaches?), Change (transforms correctly?)
- Determinism first. LLM is tail arbitration only.
- If something broke → Troubleshooting Loop (Bedrock §6). Do not patch. Do not guess.

---


## What This Process Does

Client-facing web portal served at `app.svgagency.com/:slug/:page`. Resolves URL slugs to client records, renders 5 audience-specific pages with client branding (logo, colors), all server-side HTML. Four pages are read-only; the agent page supports ticket status updates. Shared D1 with 810 Client Intake.

## How It Works

Path-based routing on a single CF Worker. No SPA framework — server-side HTML rendering.

1. **Resolve slug** — query D1 `client` table WHERE slug = :slug. Returns ClientContext with client_id, legal_name, branding (label_override, logo_url, color_primary, color_accent).
2. **Route to page renderer** — switch on page segment (renewal, ceo, hr, underwriting, agent).
3. **Render HTML** — each page function queries D1 for page-specific data, returns HTML body. Layout template wraps with client branding.
4. **Agent page write path** — POST `/:slug/agent/ticket/:id/status` validates status transition and updates ticket.

## Pages

| Route | Page | Audience | Access |
|-------|------|----------|--------|
| `/:slug/renewal` | Renewal | Client (general) | Read-only |
| `/:slug/ceo` | CEO Dashboard | Client CEO | Read-only |
| `/:slug/hr` | HR Portal | Client HR | Read-only |
| `/:slug/underwriting` | Underwriting | Stop-loss underwriter | Read-only |
| `/:slug/agent` | Service Dashboard | Internal (Dave's team) | Read-write |

## API Endpoints

| Method | Path | What |
|--------|------|------|
| GET | `/health` | Health check |
| GET | `/:slug/:page` | Render page for client |
| POST | `/:slug/agent/ticket/:id/status` | Update ticket status (agent only) |

## Slug Resolution

```typescript
interface ClientContext {
  client_id: string;
  slug: string;
  legal_name: string;
  label_override: string | null;  // Display name override
  logo_url: string | null;
  color_primary: string | null;
  color_accent: string | null;
  status: string;
}
```

Display name: `label_override || legal_name`. Unknown slug returns 404.

## Databases

**D1 workspace:** `client-intake-810` (SHARED with 810 — same D1 binding)
- Reads: `client` (with slug column added by 830 migration), plus all 810 canonical tables for page data
- Writes: Ticket status updates via agent page only

The slug column was added to the shared `client` table via `001_add_slug.sql` migration:
```sql
ALTER TABLE client ADD COLUMN slug TEXT UNIQUE;
```

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | 800 Client Mint | Client record must exist |
| Upstream | 810 Client Intake | Canonical data (plans, people, elections, vendors, service requests) |
| Downstream | None | Terminal — renders HTML for browser consumption |

## Worker Config

- **Name:** `client-portal-830`
- **URL:** client-portal-830.svg-outreach.workers.dev (production: app.svgagency.com)
- **Trigger:** HTTP GET/POST
- **D1:** Binds to `client-intake-810` D1 (shared)
- **Secrets:** None — reads from shared D1 only
- **Secrets provider:** Doppler

## Key Joins

- Slug resolution: `client.slug` = URL slug segment
- Renewal page: queries plan, plan_quote data for client_id
- HR page: queries person, election data for client_id
- Underwriting page: queries census/enrollment data for client_id
- Agent page: queries service_request for client_id
- Branding: client.logo_url, color_primary, color_accent applied to layout template

## Known Issues

| Issue | Resolution |
|-------|------------|
| D1 database_id not set in wrangler.toml | Uses 810's D1 — needs the same database_id |
| No authentication per page audience | Needs CF Access rules or token-based auth per audience role |
| Slug generation not automated | Slugs must be manually set on client records |
| No client branding assets (logos) storage | logo_url column exists but no R2 bucket or CDN for assets |

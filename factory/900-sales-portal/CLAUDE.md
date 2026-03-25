# CLAUDE.md — Process 900: Sales Portal

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

Sales process portal served at `app.svgagency.com/sales/:slug/:meeting`. Four meetings map to four phases of the sales cycle. Meeting 1 (Fact Finder) is a read-write form pre-populated from outreach intelligence. Meetings 2-4 are read-only presentation pages. Each prospect gets a unique slug. Server-side HTML, no SPA.

## How It Works

Path-based routing. Slug resolves to a sales_state record. Each meeting corresponds to a sales phase.

1. **Resolve slug** — query D1 `sales_state` WHERE slug = :slug. Returns SalesContext with sales_id, sovereign_id, legal_name, current_phase, agent_name.
2. **Route to meeting renderer** — switch on meeting segment (meeting1-4).
3. **Meeting 1 (Fact Finder):**
   - Read `outreach_snapshot` for pre-populated intelligence (company profile, DOL filings, contacts from CEO/CFO/HR slots, BIT score, blog signals).
   - Read existing `sales_factfinder` if previously saved.
   - Render form with outreach data as defaults, existing data as overrides.
   - POST `/sales/:slug/meeting1/save` — upserts to `sales_factfinder`, advances phase to 'insurance' if status='completed'.
4. **Meetings 2-4:** Read-only presentation pages from their respective tables.

## Pages

| Route | Meeting | Name | Access | Data Source |
|-------|---------|------|--------|-------------|
| `/sales/:slug/meeting1` | Meeting 1 | Fact Finder | Read-write | outreach_snapshot + sales_factfinder |
| `/sales/:slug/meeting2` | Meeting 2 | Insurance Education | Read-only | sales_insurance (Monte Carlo results future) |
| `/sales/:slug/meeting3` | Meeting 3 | Systems Education | Read-only | sales_systems |
| `/sales/:slug/meeting4` | Meeting 4 | Financials | Read-only | sales_quotes |

## API Endpoints

| Method | Path | What |
|--------|------|------|
| GET | `/health` | Health check |
| GET | `/sales/:slug/:meeting` | Render meeting page |
| POST | `/sales/:slug/meeting1/save` | Save fact finder form data |

## Outreach Snapshot (Meeting 1 Seed)

The `outreach_snapshot` table is seeded from 5 outreach sub-hubs via the sovereign_id. Read-only after seed.

| Source Sub-Hub | Fields |
|----------------|--------|
| company_target | company_name, postal_code, city, state, industry, employees, company_domain |
| DOL | ein, filing_present, funding_type, broker_or_advisor, carrier, renewal_month |
| People/Slots | ceo/cfr/hr name, title, email, linkedin |
| Blog | blog_url, blog_context |
| BIT | bit_score, bit_tier, signal_count |

## Sales Phase Progression

`sales_state.current_phase` tracks where the prospect is:

```
factfinder → insurance → systems → financials → closed
```

Meeting 1 completion advances phase from 'factfinder' to 'insurance'.

## Databases

**D1 workspace:** `sales-portal-900`

| Table | Purpose | Access |
|-------|---------|--------|
| `sales_state` | Spine — sales_id, sovereign_id, legal_name, current_phase, slug, agent_name | Read + phase updates |
| `outreach_snapshot` | Seeded from outreach 5 sub-hubs (read-only after seed) | Read |
| `sales_factfinder` | Meeting 1 form data — company info, current benefits, discovery notes | Read-write (upsert) |
| `sales_factfinder_errors` | Meeting 1 error drain | Write |
| `sales_insurance` | Meeting 2 — Monte Carlo results + presentation metadata | Read (future write from simulation engine) |
| `sales_insurance_errors` | Meeting 2 error drain | Write |
| `sales_systems` | Meeting 3 — presentation metadata | Read |
| `sales_systems_errors` | Meeting 3 error drain | Write |
| `sales_quotes` | Meeting 4 — quotes by benefit_type + carrier with rates | Read |
| `sales_quotes_errors` | Meeting 4 error drain | Write |

**Neon vault:** Read access for outreach data seeding (Meeting 1). `NEON_URL` secret.

## Key Joins

- Slug resolution: `sales_state.slug` = URL slug segment
- Outreach seed: `outreach_snapshot.sales_id` = `sales_state.sales_id`
- Fact finder: `sales_factfinder.sales_id` = `sales_state.sales_id`
- Quotes: `sales_quotes.sales_id` = `sales_state.sales_id`, grouped by benefit_type
- Sovereign link: `sales_state.sovereign_id` → `outreach.company_target.company_unique_id` (Neon)

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | 200 People Worker | CEO/CFO/HR contact data in outreach snapshot |
| Upstream | 600 BIT Scoring | BIT score + tier in outreach snapshot |
| Upstream | Outreach sub-hubs (Neon) | Company profile, DOL filings, blog signals |
| Downstream | None | Terminal — renders HTML for browser consumption |

## Worker Config

- **Name:** `sales-portal-900`
- **URL:** sales-portal-900.svg-outreach.workers.dev (production: app.svgagency.com/sales/)
- **Trigger:** HTTP GET/POST
- **D1:** `sales-portal-900`
- **Secrets:** `NEON_URL` (via wrangler secret, for outreach data reads)
- **Secrets provider:** Doppler

## Known Issues

| Issue | Resolution |
|-------|------------|
| D1 database_id not set in wrangler.toml | Run `wrangler d1 create sales-portal-900` and update |
| BIT scoring retired 2026-03-25 | Remove bit_scores references from outreach_snapshot and Meeting 1 display |
| Monte Carlo results placeholder in Meeting 2 | sales_insurance.monte_carlo_run_id not populated — simulation engine not built |
| Outreach snapshot seeding mechanism not implemented | Need a seed endpoint or cron to pull from Neon outreach tables into D1 |
| No authentication on endpoints | Needs CF Access or bearer token gate — prospect URLs are currently public |
| Fact finder upsert uses DELETE + INSERT | Could race if two users save simultaneously — consider proper upsert |

> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — Process 800: Client Mint

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

Converts a company from the outreach pipeline into a formal client record. Receives a CL sovereign ID (from company lifecycle), reads the company identity from Neon vault, mints a new client_id in D1 working tables, and promotes certified clients back to Neon. This is the boundary crossing from "prospect we're outreaching" to "client we're servicing."

## How It Works

Manual trigger only. No cron. Human provides a sovereign ID, the system does the rest.

1. **Receive sovereign_id** via POST to `/mint`.
2. **Duplicate check** — if sovereign_id already minted in D1, halt with DUPLICATE_SOVEREIGN error.
3. **Read sovereign identity** from Neon CL schema (`cl.company_identity`) — canonical_name, EIN, state, domain, source.
4. **Mint client_id** — `crypto.randomUUID()` — insert into D1 `client` table with status='active', version=1.
5. **Vault promotion** (separate step) — POST `/vault` pushes all unvaulted D1 clients to Neon `clnt.client` table, marks `vaulted_at` in D1.

## API Endpoints

| Method | Path | What |
|--------|------|------|
| GET | `/health` | Health check |
| GET | `/status` | Client counts (total, vaulted, unvaulted, open errors) |
| POST | `/mint` | `{ sovereign_id }` — mint new client from CL sovereign |
| POST | `/vault` | Promote all unvaulted clients to Neon |
| GET | `/client/:id` | Lookup client by client_id |

## Databases

**D1 workspace:** `client-mint-800`
- `client` — Spine table. client_id (PK), sovereign_id, legal_name, fein, domicile_state, effective_date, status, source, version, domain, label_override, logo_url, color_primary, color_accent, feature_flags (JSON), dashboard_blocks (JSON), created_at, updated_at, vaulted_at.
- `client_error` — Error drain. client_error_id (PK), client_id, source_entity, source_id, error_code, error_message, severity, status, context, created_at.

**Neon vault:**
- Read: `cl.company_identity` — sovereign company data (source for mint)
- Write: `clnt.client` — certified client identity (vault target)
- Write: `clnt.client_error` — vault-level error tracking

## Key Joins

- Sovereign lookup: `cl.company_identity.company_unique_id` = sovereign_id input
- Vault promotion: D1 `client.client_id` → Neon `clnt.client.client_id`
- Downstream link: `client.sovereign_id` traces back to CL company lifecycle

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | CL company lifecycle (Neon vault) | Sovereign company identity |
| Downstream | 810 Client Intake | Client record exists before intake can begin |

## Worker Config

- **Name:** `client-mint-800`
- **URL:** client-mint-800.svg-outreach.workers.dev
- **Trigger:** Manual HTTP POST only
- **D1:** `client-mint-800`
- **Secrets:** `NEON_URL` (via wrangler secret)
- **Secrets provider:** Doppler

## Error Codes

| Code | Meaning |
|------|---------|
| DUPLICATE_SOVEREIGN | sovereign_id already minted as a client |
| SOVEREIGN_NOT_FOUND | sovereign_id not found in CL vault |
| VAULT_FAILED | Neon write failed during vault promotion |

## Known Issues

| Issue | Resolution |
|-------|------------|
| D1 database_id not set in wrangler.toml | Run `wrangler d1 create client-mint-800` and update |
| No authentication on endpoints | Needs CF Access or bearer token gate before production |
| No slug generation at mint time | Slug added by 830 migration — consider generating at mint |

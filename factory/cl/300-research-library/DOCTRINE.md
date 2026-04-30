# DOCTRINE — 300 Research Library

**Process ID:** PROC-300-RESEARCH-LIBRARY
**BAR:** BAR-370
**CTB Node:** barton-enterprises/governance/research-library
**Engine:** K=C — auth pattern locked as BE-wide constant

---

## What It Does

The Research Library is a multi-source research router. It accepts a query + source list, routes to configured providers (Firecrawl, Supadata, Perplexity via Composio), deduplicates by SHA-256 content hash, and stores canonical results in D1.

## Auth Doctrine (K=C Lock)

Auth pattern is a Barton Enterprises constant — not a per-worker variable. All authenticated workers use `MC_API_KEY`. No per-worker keys.

- `MC_API_KEY` → set via Doppler (imo-creator → dev)
- Header: `Authorization: Bearer <key>` OR `X-API-Key: <key>`
- `/health` is always open (no auth)
- `RESEARCH_API_KEY` was doctrine drift — removed in BAR-370

## Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | None | Health + table check |
| POST | /research | MC_API_KEY | Run research job |
| GET | /research/records | MC_API_KEY | Query canonical records |
| GET | /research/records/:id | MC_API_KEY | Get single record |
| GET | /research/subjects | MC_API_KEY | CTB subject hierarchy |
| POST | /research/subjects | MC_API_KEY | Create subject |
| POST | /research/ingest | MC_API_KEY | Manual leaf ingest |
| GET | /research/errors | MC_API_KEY | CQRS error table |

## CQRS

- `research_records` — canonical table (leaf writes only, promotes upward)
- `research_records_error` — error table (CQRS error path)

## Sub-Hubs Wired

16-fetcher, 17-parser, 19-orchestrator, 20-cache, 21-dedup, 24-transformer

## Composio Status

Provider wiring (Firecrawl / Supadata / Perplexity) pending API keys in Doppler. POST /research returns `pending_composio` status until wired.

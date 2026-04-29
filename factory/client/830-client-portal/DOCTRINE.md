# DOCTRINE.md — Process 830: Client Portal

> **UT v2.7.0 — Locked rules for process 830-client-portal. Source-attributed. Gate-enforced.**

---

## Rule Registry

| Rule ID | Rule | Source | Gate |
|---------|------|--------|------|
| D-830-01 | The portal exposes exactly five audience pages — renewal, ceo, hr, underwriting, and agent — and no others may be added without a BAR. | `heir.yaml` acceptance_criteria[0]; `PROCESS.md` §OSAM; `CLAUDE.md` Pages table | Pre-flight item 11 (process scope); §8 STOP if unknown page slug is requested |
| D-830-02 | URL routing is path-based `/:slug/:page`; the slug segment resolves the client and the page segment selects the renderer; no other routing scheme is permitted. | `PROCESS.md` §IMO Flow; `CLAUDE.md` How It Works; `src/index.ts` fetch handler | §9b gauge: route smoke test returns 200 for all 5 pages; §8 STOP on unknown page |
| D-830-03 | Each slug resolves to exactly one `client_id`; cross-client access via slug manipulation is forbidden; an unknown or ambiguous slug returns 404 immediately. | `PROCESS.md` §OSAM Forbidden Paths; `src/resolve.ts` resolveClient(); `CLAUDE.md` Slug Resolution | §8 STOP: cross-client data visible = halt and rollback |
| D-830-04 | The display name is `label_override \|\| legal_name`; color_primary defaults to `#1a365d` and color_accent defaults to `#3182ce` when the client record has null branding fields. | `PROCESS.md` §C&V CONSTANTS; `src/resolve.ts` displayName(); `CLAUDE.md` Slug Resolution | §9b gauge: branding fallback renders correctly in layout template |
| D-830-05 | All five pages render read-only server-side HTML by default; no client-side state mutations are permitted outside the explicitly gated agent write path. | `PROCESS.md` §OSAM READ Operations; `CLAUDE.md` Pages table (Access column); `heir.yaml` acceptance_criteria | Pre-flight item 9 (render path); §8 STOP if write attempted on read-only page |
| D-830-06 | The agent page exposes one and only one write path: `POST /:slug/agent/ticket/:id/status`; the request body must contain a `status` field; the status transition must be validated before the D1 write executes; all other POST targets on the agent page are forbidden. | `PROCESS.md` §OSAM WRITE Operations; `CLAUDE.md` API Endpoints; `src/index.ts` POST handler | §9b gauge: ticket status update smoke test; §8 STOP if POST body missing status field or transition invalid |
| D-830-07 | Process 830 may write only to `service_request.status`; no other column in any table is a valid write target for this process. | `PROCESS.md` §OSAM WRITE Operations; `CLAUDE.md` Databases; `heir.yaml` acceptance_criteria[3] | §8 STOP: any write to a column other than service_request.status is a doctrine violation |
| D-830-08 | The `client` table is owned by processes 800 and 810; process 830 must not write to it except for the one-time migration that adds the `slug` column (`001_add_slug.sql`); that migration is idempotent and does not re-run after initial deployment. | `PROCESS.md` §OSAM Forbidden Paths; `CLAUDE.md` Databases; `src/migrations/001_add_slug.sql` | Pre-flight item 12 (schema ownership); §8 STOP if 830 worker attempts INSERT/UPDATE on client table |
| D-830-09 | All HTML is rendered server-side inside the Cloudflare Worker; no SPA framework, no client-side routing, and no JavaScript bundler output is served as the primary rendering mechanism. | `PROCESS.md` §C&V CONSTANTS; `CLAUDE.md` How It Works; `src/templates/layout.ts` layout wrapper | §9b gauge: HTML response contains full page markup, not a shell with a JS bundle reference |
| D-830-10 | Process 830 binds to the shared `client-intake-810` D1 database; it does not own a separate D1 instance; the slug column added by `001_add_slug.sql` is the only schema extension 830 contributes to that database. | `PROCESS.md` §IMO Flow; `CLAUDE.md` Databases; `heir.yaml` services[]; `wrangler.toml` D1 binding | Pre-flight item 7 (dependencies); §9b gauge: D1 binding resolves to client-intake-810 |
| D-830-11 | The `ClientContext` shape is fixed at 8 fields — `client_id`, `slug`, `legal_name`, `label_override`, `logo_url`, `color_primary`, `color_accent`, `status` — and may not be extended or reduced without a BAR updating both `resolve.ts` and this doctrine. | `PROCESS.md` §C&V CONSTANTS; `src/resolve.ts` ClientContext interface; `CLAUDE.md` Slug Resolution | §9b gauge: resolveClient() returns all 8 fields or null; §8 STOP if shape mismatch at runtime |
| D-830-12 | Process 830 is triggered by the completion of a client intake in process 810; 830 is terminal (egress) and has no downstream process it feeds; it must not initiate outbound calls to any other process. | `heir.yaml` depends_on=[810] feeds=[]; `PROCESS.md` §IMO Input; `CLAUDE.md` Dependencies table | Pre-flight item 6 (trigger source); §8 STOP if 830 makes outbound write calls to upstream processes |

---

## Source File Index

| File | Rules Sourced |
|------|--------------|
| `heir.yaml` acceptance_criteria | D-830-01, D-830-07, D-830-10, D-830-12 |
| `PROCESS.md` §OSAM | D-830-01, D-830-02, D-830-03, D-830-05, D-830-06, D-830-07, D-830-08, D-830-09 |
| `PROCESS.md` §C&V CONSTANTS | D-830-04, D-830-09, D-830-11 |
| `PROCESS.md` §IMO Flow | D-830-02, D-830-10, D-830-12 |
| `CLAUDE.md` | D-830-01, D-830-02, D-830-03, D-830-05, D-830-06, D-830-08, D-830-10, D-830-12 |
| `src/resolve.ts` | D-830-03, D-830-04, D-830-11 |
| `src/index.ts` | D-830-02, D-830-06 |
| `src/migrations/001_add_slug.sql` | D-830-08 |
| `wrangler.toml` | D-830-10 |

---

## Document Control

| Field | Value |
|-------|-------|
| Process | 830-client-portal |
| Rule count | 12 (D-830-01 through D-830-12) |
| UT version | v2.7.0 |
| Created | 2026-04-29 |
| Status | LOCKED per UT consolidation |
| Authority | Auditor gate G22 |

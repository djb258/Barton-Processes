# DOCTRINE.md — Process 830: Client Portal

> **UT v2.8.0 — Locked rules for process 830-client-portal. Source-attributed. Gate-enforced.**

---

## Rule Registry

| Rule ID | Rule | Source | Gate |
|---------|------|--------|------|
| D-830-01 | The portal exposes exactly six audience pages — renewal, ceo, hr, underwriting, employee, and agent — and no others may be added without a BAR. | `heir.yaml` acceptance_criteria[0]; `PROCESS-UT.md` §2 PURPOSE; `src/index.ts` route dispatch | Pre-flight item 11 (process scope); §8 STOP if unknown page slug is requested |
| D-830-02 | URL routing is path-based `/:slug/:page`; the slug segment resolves the client and the page segment selects the renderer; no other routing scheme is permitted. | `PROCESS-UT.md` §IMO Flow; `CLAUDE.md` How It Works; `src/index.ts` fetch handler | §9b gauge: route smoke test returns 200 for all 6 pages; §8 STOP on unknown page |
| D-830-03 | Each slug resolves to exactly one `client_id`; cross-client access via slug manipulation is forbidden; an unknown or ambiguous slug returns 404 immediately. | `PROCESS-UT.md` §OSAM Forbidden Paths; `src/resolve.ts` resolveClient(); `CLAUDE.md` Slug Resolution | §8 STOP: cross-client data visible = halt and rollback |
| D-830-04 | The display name is `clients.company_name`; color_primary defaults to `#1a365d` and color_accent defaults to `#3182ce` when the client record has null branding fields. | `PROCESS-UT.md` §C&V CONSTANTS; `src/resolve.ts` resolveClient(); `CLAUDE.md` Slug Resolution | §9b gauge: branding fallback renders correctly in layout template |
| D-830-05 | All six pages render server-side HTML; four pages (renewal, ceo, hr, underwriting) are strictly read-only; the employee page exposes one INSERT write path (ticket submission); the agent page exposes one UPDATE write path (ticket status); no client-side state mutations are permitted outside these two explicitly gated write paths. | `PROCESS-UT.md` §OSAM READ Operations; `CLAUDE.md` Pages table (Access column); `heir.yaml` acceptance_criteria | Pre-flight item 9 (render path); §8 STOP if write attempted on read-only page |
| D-830-06 | Process 830 exposes exactly two write paths: (1) employee page `POST /:slug/employee/ticket` — request body must contain `full_name`, `email`, `category`, `subject`, `description`; category must be one of `benefits`, `payroll`, `onboarding`, `offboarding`, `compliance`, `general`; on success responds 303 redirect; (2) agent page `POST /:slug/agent/ticket/:id/status` — request body must contain a `status` field; status must be one of `open`, `in_progress`, `waiting`, `resolved`, `closed`; on success responds JSON `{"success":true}`; all other POST targets are forbidden. | `PROCESS-UT.md` §OSAM WRITE Operations; `CLAUDE.md` API Endpoints; `src/index.ts` POST handler; `src/pages/employee.ts`; `src/pages/agent.ts` | §9b gauge: both write-path smoke tests pass; §8 STOP if POST body missing required fields or values invalid |
| D-830-07 | Process 830 may write only to `client_tickets` (INSERT on employee ticket submit) and `client_tickets.status` + `client_tickets.updated_at` + `client_tickets.resolved_at` (UPDATE on agent status change); error rows are written to `client_tickets_error`; no other column in any other table is a valid write target for this process. | `PROCESS-UT.md` §OSAM WRITE Operations; `CLAUDE.md` Databases; `heir.yaml` acceptance_criteria[3] | §8 STOP: any write outside client_tickets / client_tickets_error is a doctrine violation |
| D-830-08 | The `clients` table is owned by processes 800 and 810; process 830 must not write to it under any circumstance; the `slug` column on `clients` was pre-existing in `svg-d1-client` and is consumed read-only by 830 for slug → client_id resolution. | `PROCESS-UT.md` §OSAM Forbidden Paths; `CLAUDE.md` Databases; `src/resolve.ts` resolveClient() | Pre-flight item 12 (schema ownership); §8 STOP if 830 worker attempts INSERT/UPDATE on clients table |
| D-830-09 | All HTML is rendered server-side inside the Cloudflare Worker; no SPA framework, no client-side routing, and no JavaScript bundler output is served as the primary rendering mechanism. | `PROCESS-UT.md` §C&V CONSTANTS; `CLAUDE.md` How It Works; `src/templates/layout.ts` layout wrapper | §9b gauge: HTML response contains full page markup, not a shell with a JS bundle reference |
| D-830-10 | Process 830 binds to the shared `svg-d1-client` D1 database (ID: 5443887b-ba8a-4da5-9f54-6a9c2cfb1244); it does not own a separate D1 instance; the only schema objects 830 contributes to that database are `client_tickets` and `client_tickets_error` (created by migration `0001_client_tickets.sql`). | `PROCESS-UT.md` §IMO Flow; `CLAUDE.md` Databases; `heir.yaml` services[]; `wrangler.toml` D1 binding | Pre-flight item 7 (dependencies); §9b gauge: D1 binding resolves to svg-d1-client |
| D-830-11 | The `ClientContext` shape is fixed at 8 fields — `client_id`, `slug`, `company_name`, `logo_url`, `color_primary`, `color_accent`, `lifecycle_stage`, `employee_count` — and may not be extended or reduced without a BAR updating both `resolve.ts` and this doctrine. | `PROCESS-UT.md` §C&V CONSTANTS; `src/resolve.ts` ClientContext interface; `CLAUDE.md` Slug Resolution | §9b gauge: resolveClient() returns all 8 fields or null; §8 STOP if shape mismatch at runtime |
| D-830-12 | Process 830 is triggered by the completion of a client intake in process 810; 830 is terminal (egress) and has no downstream process it feeds; it must not initiate outbound calls to any other process. | `heir.yaml` depends_on=[810] feeds=[]; `PROCESS-UT.md` §IMO Input; `CLAUDE.md` Dependencies table | Pre-flight item 6 (trigger source); §8 STOP if 830 makes outbound write calls to upstream processes |

---

## Source File Index

| File | Rules Sourced |
|------|--------------|
| `heir.yaml` acceptance_criteria | D-830-01, D-830-07, D-830-10, D-830-12 |
| `PROCESS-UT.md` §OSAM | D-830-01, D-830-02, D-830-03, D-830-05, D-830-06, D-830-07, D-830-08, D-830-09 |
| `PROCESS-UT.md` §C&V CONSTANTS | D-830-04, D-830-09, D-830-11 |
| `PROCESS-UT.md` §IMO Flow | D-830-02, D-830-10, D-830-12 |
| `CLAUDE.md` | D-830-01, D-830-02, D-830-03, D-830-05, D-830-06, D-830-08, D-830-10, D-830-12 |
| `src/resolve.ts` | D-830-03, D-830-04, D-830-08, D-830-11 |
| `src/index.ts` | D-830-02, D-830-06 |
| `src/pages/employee.ts` | D-830-06, D-830-07 |
| `src/pages/agent.ts` | D-830-06, D-830-07 |
| `src/migrations/0001_client_tickets.sql` | D-830-10 |
| `wrangler.toml` | D-830-10 |

---

## Document Control

| Field | Value |
|-------|-------|
| Process | 830-client-portal |
| Rule count | 12 (D-830-01 through D-830-12) |
| UT version | v2.8.0 |
| Created | 2026-04-29 |
| Last Modified | 2026-05-13 |
| Status | LOCKED per UT consolidation — updated to OPERATE state 2026-05-13 |
| Authority | Auditor gate G22 |

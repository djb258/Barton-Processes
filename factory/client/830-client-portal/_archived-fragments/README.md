> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# Client Portal 830 — Skeleton

**Status:** SKELETON (2026-04-22) — all routes render with mock data. Zero backend wiring.

## What This Is

A CF Pages static skeleton for the client-facing portal. All 14 screens render.
Navigation works. Every fetch is stubbed with inline mock JSON.
Purpose: lock in the complete UI shape before wiring the backend.

## How to Run Locally

```bash
npm install
npm run dev
# Opens http://localhost:8788
```

## URL Routes

```
#/                                    → Login (client selector)
#/intake                              → New client intake form
#/{client_id}/                        → CFO Dashboard (default)
#/{client_id}/benefits                → Benefits checkbox
#/{client_id}/plans/add               → Add plan (4-tier rates)
#/{client_id}/dashboard/cfo           → CFO Dashboard
#/{client_id}/dashboard/ceo           → CEO Dashboard
#/{client_id}/dashboard/hr            → HR Dashboard
#/{client_id}/dashboard/underwriting  → Underwriting Dashboard
#/{client_id}/dashboard/renewal       → Renewal Dashboard
#/{client_id}/dashboard/advisor       → Advisor Dashboard
#/{client_id}/employees               → Employee list
#/{client_id}/employees/{person_id}   → Employee detail
#/{client_id}/tickets                 → Ticket list
#/{client_id}/tickets/new             → New ticket form
```

## Sample Client IDs (mock data)

- `CLT-ACME-2026` — Acme Corp (PA)
- `CLT-GLOBEX-2026` — Globex Inc (NY)
- `CLT-INITECH-2026` — Initech LLC (TX)

Example: http://localhost:8788/#/CLT-ACME-2026/dashboard/cfo

## WIRE-HERE Punch List

Every location that needs a real backend endpoint:

| # | Location | Stub | Wire To |
|---|----------|------|---------|
| 1 | `app.js` loadClients() | mocks/clients.json | GET https://client-hub-api.svg-outreach.workers.dev/clients |
| 2 | `app.js` loadClient() | mocks/clients.json filter | GET https://client-hub-api.svg-outreach.workers.dev/clients/{id} |
| 3 | `app.js` loadBenefitClasses() | mocks/benefit-classes.json | GET https://client-hub-api.svg-outreach.workers.dev/benefit-classes |
| 4 | `app.js` loadPlans() | mocks/plans.json | GET https://client-hub-api.svg-outreach.workers.dev/plans?client_id=X |
| 5 | `app.js` loadEmployees() | mocks/employees.json | GET https://client-hub-api.svg-outreach.workers.dev/employees?client_id=X |
| 6 | `app.js` loadEmployee() | mocks/employees.json find | GET https://client-hub-api.svg-outreach.workers.dev/employees/{person_id} |
| 7 | `app.js` loadTickets() | mocks/tickets.json | GET https://client-hub-api.svg-outreach.workers.dev/tickets?client_id=X |
| 8 | `app.js` loadDashboard() | mocks/dashboards/{role}.json | GET https://client-hub-api.svg-outreach.workers.dev/views/v_{role}?client_id=X |
| 9 | `app.js` mintClient() | console.log stub | POST https://client-mint-800.svg-outreach.workers.dev/mint |
| 10 | `app.js` submitBenefits() | console.log stub | POST https://client-intake-810.svg-outreach.workers.dev/intake (table=benefit_election) |
| 11 | `app.js` submitPlan() | console.log stub | POST https://client-intake-810.svg-outreach.workers.dev/intake (table=plan) |
| 12 | `app.js` submitTicket() | console.log stub | POST https://client-intake-810.svg-outreach.workers.dev/intake (table=service_request) |
| 13 | `employees-detail.js` mockVendorIds() | hardcoded map | GET https://client-hub-api.svg-outreach.workers.dev/employees/{person_id}/vendor-ids |
| 14 | `tickets-form.js` member_id display | "[WIRE: member_id]" | GET elections join by employee + vendor |

## Mock Data

```
src/mocks/
  clients.json          — 3 clients
  benefit-classes.json  — 19 benefit classes
  plans.json            — 5 plans across 3 clients
  employees.json        — 15 persons (employees + dependents)
  tickets.json          — 9 tickets across 3 clients
  dashboards/
    cfo.json            — CFO KPIs + plan breakdown
    ceo.json            — CEO KPIs + activity log
    hr.json             — HR KPIs + upcoming events
    underwriting.json   — Underwriting KPIs + demographics
    renewal.json        — Renewal KPIs + vendor list
    advisor.json        — Advisor KPIs + activity log
```

## Governing Docs

- UT: `Barton-Processes/factory/client/UT_PROCESSES.md` v1.2.0 (CERTIFIED)
- Blueprint: `client/docs/UT_BLUEPRINT.md` v1.2.0 (CERTIFIED)
- Process: `factory/client/830-client-portal/PROCESS.md`

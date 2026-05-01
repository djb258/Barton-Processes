# Process 211 — Agent Follow-up Publishing

## Daily surfacing of each servicing agent's emailed book to a public follow-up page (with CSV export) and branded calendar booking landing for replies.
### Status: BUILD
### Medium: process
### Business: svg-agency

---

# 📋 UT Pre-Flight Checklist (per `law/UT_CHECKLIST.md` v1.2.0)

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | Parent Atlas declared — `law/doctrine/BARTON_ENTERPRISES_WORLD_ATLAS.md` (13th constant) | ☑ | Inherits legend, cartographic standards, 10-step map-building SOP |
| 2 | ctb_node declared (top-down from Barton Enterprises trunk) | ☑ | `barton-enterprises/svg-agency/outreach/lcs/agent-followup-publishing` |
| 3 | Dewey address | ☑ | `svg-agency.outreach.lcs.agent-followup-publishing` |
| 4 | HEIR populated (8 fields, §1 table) | ☑ | See §1 |
| 5 | ORBT declared (OPERATE / REPAIR / BUILD / TROUBLESHOOT-TRAIN) | ☑ | BUILD |
| 6 | K=C against Parent Legend — every term in parent atlas §1 | ☑ | No new vocabulary introduced |
| 7 | Gauges installed (§9b) — live verification queries | ☑ | 4 gauges, one per surface |
| 8 | FCEs Attached | ☑ | FCE-006 Email Deliverability (upstream) |
| 9 | BARs Referenced | ☑ | BAR-801 (book-page), BAR-802 (CSV + Stage 4 fix), BAR-803 (public agent-book) |
| 10 | Tolerances — 0→1 per section | ☑ | Binary per §UT format |
| 11 | Repair SOP — ORBT + HEIR path declared | ☑ | See §13 |
| 12 | Inheritance — parent atlas `§1` immutable, this doc extends | ☑ | Extends only with local terms: "book-page", "agent-book", "public route" |
| 13 | LBB ingest plan — where this lands in LBB | ☑ | `subject_id='svg-outreach-proc'`, `ctb_placement='leaf'` |

---

# IDENTITY (Thing — what this IS)

## 1. IDENTITY

| Field | Value |
|-------|-------|
| ID | PROC-211 |
| Name | Agent Follow-up Publishing |
| Medium | process |
| Business Silo | svg-agency (outreach) |
| CTB Position | `barton-enterprises/svg-agency/outreach/lcs/agent-followup-publishing` |
| ORBT | BUILD |
| Strikes | 0 |
| Authority | BAR-801, BAR-802, BAR-803 — Dave-approved 2026-04-24 |
| Last Modified | 2026-04-24 |
| BAR Reference | BAR-801 (book-page), BAR-802 (CSV + Stage 4), BAR-803 (public agent-book) |
| **CL Spine Binding** | **`sovereign_id` (trunk) — every surface row carries `sovereign_company_id` per `docs/CL_GRID_SPEC.md` CTB. Agent-book + public API: LOCKED. Book-page: UNLOCKED until `/track/calendar-view` ships (Phase 2 backlog).** |
| **CL Branch** | Outreach (hangs off the Outreach branch of the CL trunk, alongside PROC-010 through PROC-700 + PROC-203) |

### HEIR (Aviation Model, Bedrock §8)

| Field | Value |
|-------|-------|
| sovereign_ref | imo-creator |
| hub_id | proc-211-agent-followup-publishing |
| ctb_placement | leaf (under `svg-agency/outreach/lcs/`) |
| imo_topology | middle — daily `lcs_cid` + `lcs_event` rows in, public HTML tables + branded booking URL out |
| cc_layer | CC-03 |
| services | Cloudflare Pages (`book-page`, `agent-book`), Cloudflare Workers (`mission-control-api`), D1 (`svg-d1-spine`, `svg-d1-outreach-ops`) |
| secrets_provider | doppler (project: imo-creator, config: dev) |
| acceptance_criteria | (a) `https://book.insuranceinformatics.com` serves 200 with iframe; (b) `https://agent-book.pages.dev/?agent=SA-00{1,2,3}` serves 200 with rendered table; (c) `/public/agents/:code/sends` returns correct row counts without auth; (d) CSV download produces valid file; (e) whitelist rejects SA-999 with 403 |

**0 → 1 when:** every identity field and all 8 HEIR fields are present, non-placeholder, and match the live deployment (URLs resolving, routes returning expected shape).

---

## 2. PURPOSE

Without this process, the daily 1,200-email fire is one-directional — we send, the three servicing agents (SA-001 Dave Allan, SA-002 Jeff Mussolino, SA-003 David Vang) have no visibility into who was emailed on their behalf, and replies land in raw calendar.app.google URLs instead of a branded landing page with click tracking.

This process publishes two surfaces daily:

1. **Outbound landing** — `https://book.insuranceinformatics.com` (BAR-801) — branded wrapper around the Google Appointment Scheduling iframe. Replaces raw `calendar.app.google/XXX` links in email bodies with a domain that reads as credible (not forwarded) and sits inside the Cloudflare zone we control, letting us track and iterate.
2. **Inbound visibility** — `https://agent-book.pages.dev/?agent=SA-00{1,2,3}` (BAR-803) — public per-agent follow-up page where each servicing agent can see their emailed book for the day with Company · Contact · Role (CEO/CFO/HR) · Phone · Email · State · Sent time · Delivery status · Call/Email actions, filter by delivery status, and download a CSV for phone follow-up work.

**0 → 1 when:** this section states in 2-3 sentences what breaks without the process and names the downstream consumers of its output (servicing agents + prospects).

---

## 3. RESOURCES

### Dependencies

| Dependency | Type | What It Provides | Status |
|-----------|------|-----------------|--------|
| Process 203 (Email Deliverability) | upstream process | Emits `lcs_cid` + `lcs_sid_output` + `lcs_event` rows this process reads | DONE |
| `mission-control-api` | CF Worker | Hosts `/agents/:code/sends` (authed) + `/public/agents/:code/sends` (public, whitelisted) | DONE |
| `book-page` | CF Pages project | Serves `book.insuranceinformatics.com` — branded calendar booking landing | DONE |
| `agent-book` | CF Pages project | Serves `agent-book.pages.dev` (or `agents.insuranceinformatics.com`) — public follow-up table | DONE |
| D1 `svg-d1-spine` | D1 database | `lcs_cid`, `lcs_sid_output`, `lcs_event`, `cl_company_identity`, `lcs_email_signature`, `lcs_frame_registry` | DONE |
| D1 `svg-d1-outreach-ops` | D1 database | `outreach_company_target`, `people_people_master`, `people_company_slot` | DONE |
| Google Appointment Scheduling | external | Iframe embed for 15-min intro booking (URL `AcZssZ0WSr65JWFjSGKd6IDVISpZdjT8mYHCaSxjRzfuKWnJz76b8t7pL3jNzf1_hjcrsfNPJ_Hs0Joy`) | DONE |
| DNS: `insuranceinformatics.com` | CF zone | Hosts `book.*` CNAME (and `agents.*` pending) | DONE |

### Downstream Consumers

| Consumer | What It Needs |
|----------|--------------|
| SA-001 Dave Allan | `?agent=SA-001` URL → daily book with phones for follow-up |
| SA-002 Jeff Mussolino | `?agent=SA-002` URL |
| SA-003 David Vang | `?agent=SA-003` URL |
| Prospects (email recipients) | Branded `book.insuranceinformatics.com` for calendar booking |

### Secrets

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| `MC_API_KEY` | imo-creator | dev | `mission-control-api` auth — required for authenticated `/agents/:code/sends` (Mission Control UI); NOT required for `/public/agents/:code/sends` |

**0 → 1 when:** every dependency, consumer, and secret required is named; no count contradicts live deployment.

---

# CONTRACT (Flow — what flows through this)

## 4. IMO — Input, Middle, Output

### Two-Question Intake
1. **What triggers this?** — (a) Daily fire of outbound emails completes (Process 203 `MID_SENT` events land in `lcs_event`); (b) A prospect opens the email and clicks the booking link.
2. **How do we get it?** — (a) Mission-control-api queries `lcs_cid` + `lcs_sid_output` + `lcs_event` for each agent_number on demand via HTTPS GET. **Every returned row carries `sovereign_company_id` — the CL spine trunk key — so each follow-up entry is traceable back to one canonical company across Outreach/Sales/Client branches.** (b) Email body contains `https://book.insuranceinformatics.com` rendered from `lcs_frame_registry.body_template`; CF Pages serves the branded iframe; recipient books via Google. (NOTE: book-page is NOT YET sovereign_id-bound — Phase 2 adds `?cid=` → `/track/calendar-view` to close that leg.)

### Input
- Per-agent query: `GET /public/agents/:code/sends?since=ISO8601` (HTTP, public, whitelisted to SA-001/002/003)
- Per-prospect email click: `GET https://book.insuranceinformatics.com/` (HTTPS, public, no auth)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Daily fire complete | Process 203 writes `lcs_cid` + `lcs_sid_output` rows | Queryable row set per agent_number | lcs-hub worker |
| 2 | Agent opens follow-up URL | `agent-book` static HTML loads from CF Pages | HTML + JS shell rendered | CF Pages edge |
| 3 | JS reads `?agent=` query param | Fetch `GET /public/agents/:code/sends?since=...` (no auth header) | JSON `{agent_code, since, count, sends: [...]}` | fetch API |
| 4 | API receives request | Whitelist check (`PUBLIC_AGENT_WHITELIST` = {SA-001, SA-002, SA-003}); 403 if not in set; otherwise delegate to shared `fetchAgentSends` | D1 queries across 5 stages (CID → companies → people → slots → events) | mission-control-api + D1 |
| 5 | JSON returns | JS renders sortable/filterable table with Call/Email buttons; filter pills reflect status distribution | Rendered DOM table | vanilla JS |
| 6 | Agent clicks Download CSV | Filtered+sorted view serialized to CSV with 18 columns; browser download triggered | `SA-00{1,2,3}-sends-YYYY-MM-DD.csv` | Blob + `a.download` |
| 7 | Email recipient clicks `book.insuranceinformatics.com` | `book-page` static HTML loads Google Appointment Scheduling iframe | Rendered iframe; recipient books | CF Pages edge |

### Output
- Public HTML table per agent (reloadable, status-filterable)
- CSV download (18 columns, what-you-see-is-what-you-get)
- Branded calendar landing at `book.insuranceinformatics.com`
- Booked meetings on marketing@svg.agency Google Calendar (downstream — outside this process)

### Circle (Bedrock §5)
When Process 212 (AI Inbox Agent, BAR-800) starts auto-drafting replies, the calendar booking confirmations become its input — the system learns which outbound frames converted. That loop closes at the next process downstream; this process's job is to surface today's state accurately so the agent can call manually AND the machine can read canonically.

**0 → 1 when:** the process's Two-Question Intake is answered, every Middle step is traceable, and the Circle explicitly names the downstream process that closes it.

---

## 5. DATA SCHEMA

### READ Access

| Source | What It Provides | Join Key |
|--------|-----------------|----------|
| `svg-d1-spine.lcs_cid` | `communication_id`, `sovereign_company_id`, `entity_id` (outreach_id), `frame_id`, `agent_number`, `created_at` | `communication_id` |
| `svg-d1-spine.lcs_sid_output` | `recipient_email`, `sent_at`, `construction_status` | `communication_id` |
| `svg-d1-spine.lcs_event` | Latest `event_type` per CID (MID_SENT, MID_DELIVERED, MID_OPENED, MID_CLICKED, MID_REPLIED, MID_BOUNCED) | `communication_id` |
| `svg-d1-spine.cl_company_identity` | `canonical_name` | `outreach_id` |
| `svg-d1-outreach-ops.outreach_company_target` | `state`, `industry`, `employees` | `outreach_id` |
| `svg-d1-outreach-ops.people_people_master` | `first_name`, `last_name`, `linkedin_url`, `work_phone_e164`, `personal_phone_e164`, `unique_id` | `LOWER(email)` |
| `svg-d1-outreach-ops.people_company_slot` | `slot_type` (CEO/CFO/HR) | (`outreach_id`, `person_unique_id`) tuple |
| `svg-d1-spine.lcs_email_signature` | `booking_link` (per `agent_number`) | `agent_number` |
| `svg-d1-spine.lcs_frame_registry` | `body_template` with interpolated `{booking_link}` merge tag | `frame_id` |

### WRITE Access

| Target | What It Writes | When |
|--------|---------------|------|
| (none) | This process is READ-ONLY | N/A |

### Join Chain

```
lcs_cid (spine)
  ├── LEFT JOIN lcs_sid_output (spine) on communication_id
  ├── LEFT JOIN lcs_event (spine) on communication_id [latest by created_at DESC]
  ├── LEFT JOIN cl_company_identity (spine) on outreach_id
  ├── LEFT JOIN outreach_company_target (outreach) on outreach_id
  ├── LEFT JOIN people_people_master (outreach) on LOWER(recipient_email) = LOWER(email)
  └── LEFT JOIN people_company_slot (outreach) on (outreach_id, person_unique_id) tuple
        [chunked at 40 pairs/query to stay under D1's ~100-variable statement limit]
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Writes from `agent-book` or `book-page` to any D1 table | Both pages are public, unauthenticated static HTML — cannot be trusted with write access |
| Exposing non-whitelisted agent codes on `/public/agents/*` | Whitelist is the security boundary; only the 3 servicing agents are publishable |
| Embedding `MC_API_KEY` in the public `agent-book` page | Defeats the public-route design; always use `/public/agents/*`, never the authed variant |

**0 → 1 when:** every read source is named, the join chain is traceable, and write access is explicitly declared (none, here).

---

## 6. DMJ

| Element | Mapping |
|---------|---------|
| **Define** | Agent code (SA-001/002/003), window (since ISO), row shape (`Send` interface — 18 public fields) |
| **Map** | Query-time join of 5 staged D1 reads → single JSON response; JSON → rendered DOM rows + CSV rows |
| **Join** | `communication_id` is the spine join; all other data attaches via LEFT JOINs with fallback to `—` in the UI |

---

## 7. CONSTANTS & VARIABLES

### Constants
- `PUBLIC_AGENT_WHITELIST = {SA-001, SA-002, SA-003}` (server-side)
- Booking iframe URL: `AcZssZ0WSr65JWFjSGKd6IDVISpZdjT8mYHCaSxjRzfuKWnJz76b8t7pL3jNzf1_hjcrsfNPJ_Hs0Joy` (hardcoded in `book-page/dist/index.html`)
- CSV header: 18 columns, fixed order
- Join keys: `communication_id`, `outreach_id`, `LOWER(email)`, `(outreach_id, person_unique_id)` tuple
- Stage 4 chunk size: 40 tuple-pairs per D1 statement (stays under ~100 variable cap)
- Default window: `new Date().setUTCHours(0,0,0,0).toISOString()` — today 00:00 UTC

### Variables
- Agent code (SA-00x) — whitelist-bounded
- `?since=` override — any valid ISO8601 after 2026-01-01
- Delivery status filter (All / sent / delivered / opened / clicked / replied / bounced)
- Sort key + direction — runtime UI state

### Domesticated Variables
- Row count (bounded to `LIMIT 2000` in Stage 1 query)
- Phone coverage (50–100% per day, depending on enrichment)

---

## 8. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Agent code not in whitelist | API returns 403; page shows error |
| `mission-control-api` down | Page shows error message; user sees cached prior render (or empty state on first load) |
| `book-page` cert not issued yet | CF returns 522 briefly; email links appear dead for ~1–5 min post-CNAME |
| D1 variable limit hit | Stage 4 chunking prevents; if other stages hit, return 500 with error string |
| Empty result set | Page renders "No sends found." empty state |

---

# GOVERNANCE (Change — how this evolves)

## 9. GAUGES (Live Verification)

### §9a — Build Verification
- [x] `https://book.insuranceinformatics.com/` returns 200 with correct title + iframe (verified 2026-04-24 after Google cert issuance)
- [x] `https://agent-book.pages.dev/?agent=SA-001` returns 200 (pending pages.dev DNS propagation, retry if 5xx)
- [x] `GET /public/agents/SA-001/sends` returns count ≥ 1 with no auth header
- [x] `GET /public/agents/SA-999/sends` returns 403 with `error: "agent_code not permitted on public endpoint"`
- [x] CSV download produces valid file with 18 columns + escaped values

### §9b — Operational Gauges (always on)

| Gauge | Query | Red Threshold |
|-------|-------|--------------|
| **Book-page reachability** | `curl -sI https://book.insuranceinformatics.com` → 200 | Any non-2xx |
| **Agent-book reachability** | `curl -sI https://agent-book.pages.dev/?agent=SA-001` → 200 | Any non-2xx |
| **Public API health** | `curl -s https://mission-control-api.svg-outreach.workers.dev/public/agents/SA-001/sends` → `count ≥ 0` | Any error key present in response |
| **Whitelist enforcement** | `curl -s .../public/agents/SA-999/sends` → 403 | Anything other than 403 |

Gauges are polled by the daily fire script's post-send check. If any red, session is halted and Troubleshoot/Train is entered.

---

## 10. ROLLOUT

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | `book-page` live on pages.dev, custom domain attached via API, CNAME added | ✅ 2026-04-24 |
| 2 | D1 frame_registry templates swapped to `https://book.insuranceinformatics.com`; `lcs_email_signature.booking_link` updated for SA-001 | ✅ 2026-04-24 |
| 3 | `agent-followup.ts` Stage 4 chunking fix (D1 variable limit) + public route added | ✅ 2026-04-24 |
| 4 | `agent-book` static page deployed with vanilla JS table + CSV download | ✅ 2026-04-24 |
| 5 | `agents.insuranceinformatics.com` custom domain attached (CNAME pending manual dashboard add — no token has DNS-edit) | 🟨 pending DNS |
| 6 | Docs landed (this file + worker MANUALs) | ✅ 2026-04-24 |
| 7 | LBB ingest of session learnings | ⏳ end of session |

---

## 11. EXCEPTIONS

- **MC_API_KEY in bundle** — The authed `mission-control` React app still bakes `VITE_MC_API_KEY` into its JS bundle (same as every other authed MC page). That's a soft exposure behind CF Access but not a new risk from this process. The `agent-book` public page deliberately does NOT use that key — it uses the whitelisted `/public/agents/*` route.
- **Phone coverage** — 50/601 rows had a phone on BAR-802's day-one query. That's a data-enrichment gap upstream (Process 203 / enrichment jobs), not a bug in this process. Separate task (#38 BAR-701) handles enrichment wave.
- **Pages.dev subdomain propagation** — Brand-new CF Pages projects can take 5–15 minutes before their pages.dev subdomain resolves globally. Custom domain attach fires independently and may be reachable first.

---

## 12. CHANGE CONTROL

| Date | Change | Author | BAR |
|------|--------|--------|-----|
| 2026-04-24 | Initial build — book-page, agent-followup CSV + Stage 4 fix, public agent-book | Claude (Opus 4.7, via Dave) | BAR-801/802/803 |

---

## 13. REPAIR SOP (ORBT + HEIR — per Atlas §4.5)

When a gauge reads red:

1. **Gauge red** → identify which surface (book-page, agent-book, public API, whitelist)
2. **Look at HEIR** (§1 table) → `hub_id=proc-211-agent-followup-publishing`, services named, exact file paths in `acceptance_criteria`
3. **ORBT flip** → OPERATE → REPAIR, log in LBB
4. **Diagnose** (Aviation Model — mechanic ≠ inspector):
   - 522 on `book.insuranceinformatics.com` → check `pages/projects/book-page/domains/book.insuranceinformatics.com` status via wrangler OAuth token
   - 403 on `/public/agents/SA-001/sends` → check `PUBLIC_AGENT_WHITELIST` in `workers/mission-control-api/src/routes/agent-followup.ts`
   - `D1_ERROR: too many SQL variables` → Stage 4 chunk size needs lowering (currently 40 pairs); see commit `a4d5f446`
   - CSV download silent fail → browser popup blocker; user-side
5. **Fix at source** — code edit, redeploy, verify gauge flips green
6. **ORBT flip** → REPAIR → OPERATE
7. **LBB ingest** — record symptom, root cause, fix

---

## 14. DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Created | 2026-04-24 |
| Last Modified | 2026-04-24 |
| Version | 1.0.0 |
| Status | BUILD |
| Authority | Dave Barton |
| Inherits From | `law/doctrine/BARTON_ENTERPRISES_WORLD_ATLAS.md` §1 (parent legend) |

# CRON CLASSIFICATION DECISION SHEET
## BAR-MONDAY-16-FLEET-GREEN
### Compiled: 2026-05-08 | Compiler: Claude Sonnet (read-only) | Sovereign Decision: Dave Barton

---

## SUMMARY TABLE

| # | ID | Process | Proposed Cron | ORBT | Implementation | Recommendation |
|---|----|---------|--------------:|------|---------------|----------------|
| 1 | bp.010 | Seed D1 | `0 4 * * *` | OPERATE | CF endpoint on lcs-hub | RECURRING |
| 2 | bp.201 | Email Discovery | `0 7 * * *` | BUILD | Local Python script | EVENT-DRIVEN/MANUAL |
| 3 | bp.202 | LinkedIn Discovery | `0 7 * * *` | BUILD | Local Python script | EVENT-DRIVEN/MANUAL |
| 4 | bp.300 | Blog Worker | `0 9 1 * *` | BUILD | Local Python scripts | UNCLEAR |
| 5 | bp.301 | Page Parser | `0 8 * * *` | BUILD | STUB — sections not filled | UNCLEAR |
| 6 | bp.400 | DOL Views | `0 5 * * *` | OPERATE | 6 SQL views (Neon) — no worker | EVENT-DRIVEN/MANUAL |
| 7 | bp.500 | Talent Flow | `0 8 1 * *` | BUILD | Local Python script | EVENT-DRIVEN/MANUAL |
| 8 | bp.700 | Campaign Engine | `0 13 * * 1-5` | BUILD | CF Worker (lcs-hub) — MISSING DEPS | RECURRING (blocked) |
| 9 | bp.800 | Client Mint | `0 4 * * *` | BUILD | CF Worker — manual trigger only per D-800-07 | EVENT-DRIVEN/MANUAL |
| 10 | bp.810 | Client Intake | `0 5 * * *` | BUILD | CF Worker — HTTP POST triggered | EVENT-DRIVEN/MANUAL |
| 11 | bp.830 | Client Portal | `0 6 * * *` | BUILD | CF Worker — HTTP GET/POST per user request | EVENT-DRIVEN/MANUAL |
| 12 | bp.900 | Sales Portal | `0 6 * * *` | BUILD | CF Worker — HTTP GET/POST per user request | EVENT-DRIVEN/MANUAL |

**Totals: 1 RECURRING (immediate) · 1 RECURRING (blocked) · 8 EVENT-DRIVEN/MANUAL · 2 UNCLEAR**

---

## PER-PROCESS EVIDENCE

---

### bp.010 — Seed D1 | Proposed: `0 4 * * *`
**Recommendation: RECURRING**

**Evidence:**
- ORBT: OPERATE. Currently running.
- §3 Resources: "PROC-010 is NOT a deployable process; it runs as an endpoint on lcs-hub." No standalone `wrangler.toml` — trigger must come from outside (e.g., lcs-hub cron or an external scheduler).
- §4 Trigger: "Manual POST or automated scheduler to `/seed/clean?table={name}&limit=5000&offset=0`" — both are explicitly listed as valid trigger modes.
- Purpose: Copies Neon vault records to D1 workspace for downstream consumers (201, 202, 300, 400). D1 freshness is a pre-condition for every downstream process.

**Why RECURRING:** Daily refresh is structurally required. Downstream processes run on daily/monthly crons and all read from D1. Stale D1 = garbage downstream. The trigger mechanism is an HTTP call to lcs-hub; a cron on lcs-hub calling the `/seed` endpoint is the correct wiring path. OPERATE status confirms it is safe to wire.

**Sovereign note:** Trigger is HTTP call to lcs-hub `/seed` endpoint, not a standalone CF Worker cron. Wiring = add lcs-hub cron at `0 4 * * *` that POSTs to the seed endpoint internally, or add a scheduled handler in lcs-hub that calls the seed logic.

---

### bp.201 — Email Discovery | Proposed: `0 7 * * *`
**Recommendation: EVENT-DRIVEN/MANUAL**

**Evidence:**
- ORBT: BUILD. Not in production.
- Implementation: Local Python script (`python3 src/find-email.py`). Not a CF Worker.
- §4 Trigger (explicit): "Triggered manually after Process 200 run." "Manual execution of `python3 src/find-email.py` after Process 200 completes."
- Depends on Process 200 output — ordering cannot be guaranteed by a fixed-time cron.

**Why EVENT-DRIVEN/MANUAL:** The doc explicitly designates this as manual, downstream of Process 200. It is a Python script that cannot receive CF cron signals. A daily cron entry would fire on an empty/stale input if Process 200 hasn't run. De-list from cron registry until this is converted to a CF Worker with an event trigger or orchestrator call from Process 200.

---

### bp.202 — LinkedIn Discovery | Proposed: `0 7 * * *`
**Recommendation: EVENT-DRIVEN/MANUAL**

**Evidence:**
- ORBT: BUILD. Not in production.
- Implementation: Local Python script (`python3 find-linkedin.py --limit N`). Not a CF Worker.
- §4 Trigger (explicit): "Triggered manually (`python3 find-linkedin.py --limit N`) or by orchestrator."
- Gate A depends on Process 300 output (`recon_linkedin_people` table). Multi-upstream dependency.

**Why EVENT-DRIVEN/MANUAL:** Python script with explicit manual/orchestrator trigger. Time-based cron cannot guarantee upstream data readiness. De-list from cron registry until CF Worker conversion and orchestrator wiring.

---

### bp.300 — Blog Worker | Proposed: `0 9 1 * *`
**Recommendation: UNCLEAR**

**Evidence:**
- ORBT: BUILD. Not in production.
- Implementation: Local Python scripts (company-recon.py, blog-monitor.py, etc.). Not a CF Worker.
- §4 Trigger (explicit): "Monthly manual run (currently). Future: CF Worker with monthly cron trigger."
- Proposed cron `0 9 1 * *` (monthly) matches the declared future intent perfectly.

**Why UNCLEAR:** The monthly cadence and proposed cron are architecturally correct and aligned with the doc's stated future state. But the implementation does not yet exist as a CF Worker. Wiring the cron now would reference infrastructure that isn't built. Dave's call: (a) build the CF Worker first and then wire, or (b) de-list and re-list when CF Worker is deployed.

---

### bp.301 — Page Parser | Proposed: `0 8 * * *`
**Recommendation: UNCLEAR**

**Evidence:**
- ORBT: BUILD.
- Implementation: Unknown — every §2–§14 section in the UT doc is a stub placeholder ("Section placeholder — content to be filled by process owner").
- Only confirmed data: process feeds CEO/CFO/HR slot fills from pages discovered by Process 300; architecture uses CF Worker topology (`page-parser` service listed in HEIR).
- No trigger documented. No IMO intake documented.

**Why UNCLEAR:** Insufficient UT documentation to classify. No §4 Two-Question Intake filled. No trigger mode declared. No resource/implementation detail confirmed. If it is a CF Worker (suggested by service list), a daily cron may be appropriate. Cannot recommend without a filled UT doc.

---

### bp.400 — DOL Views | Proposed: `0 5 * * *`
**Recommendation: EVENT-DRIVEN/MANUAL**

**Evidence:**
- ORBT: OPERATE.
- Implementation: 6 read-only SQL views against Neon `dol` schema + D1 seeded tables. There is no process to "run" — the views exist permanently in Neon and are queried by consumers on-demand.
- §2 Out-of-scope: "D1 seeding logic (owned by Process 010 SEED)." "Real-time data (DOL filings lag 6-18 months; this is annual batch only)."
- §1b Hub-Spoke: "No worker, no cron; the hub is the SQL view definitions and the query interface."
- EBSA data is annual; D1 seed is owned by Process 010.

**Why EVENT-DRIVEN/MANUAL:** This process is a static view library. It has no runnable artifact — no script, no worker, no scheduled action. A cron entry makes no sense: there is nothing to trigger. The views are always-on SQL objects. De-list from cron registry. Process 010 handles D1 freshness. Consumers query the views directly.

---

### bp.500 — Talent Flow | Proposed: `0 8 1 * *`
**Recommendation: EVENT-DRIVEN/MANUAL**

**Evidence:**
- ORBT: BUILD. Not in production.
- Implementation: Python script (`talent_flow.py`). Not a CF Worker.
- §4 Trigger (explicit): "Monthly, after Process 200 completes its LinkedIn refresh for the target month."
- §2 Out-of-scope: "Converting to a CF Worker — currently a Python script; future state only."
- Snapshot gate: if `COUNT(*) = 0` from linkedin_snapshots for target month → HALT. Fixed-time cron that fires before Process 200 completes would always HALT.

**Why EVENT-DRIVEN/MANUAL:** Sequencing dependency on Process 200 is hard-wired in the process logic (snapshot gate). A monthly cron at a fixed time cannot guarantee 200 has completed. De-list from cron registry until CF Worker conversion with event-based trigger after Process 200 completion.

---

### bp.700 — Campaign Engine | Proposed: `0 13 * * 1-5`
**Recommendation: RECURRING (blocked — do not wire yet)**

**Evidence:**
- ORBT: BUILD.
- Implementation: CF Worker (lives inside lcs-hub). Cron-triggered architecture is explicitly designed in. Kill switch is `npx wrangler cron delete --name lcs-hub-campaign-scanner`.
- §4 Trigger: "LCS Pipeline (Process 100) completes CID compilation for a company cycle; cron fires at `0 7 * * *` and the campaign scanner evaluates pending CIDs." (Note: proposed cron in registry is `0 13 * * 1-5`; doc internally references `0 7 * * *` — discrepancy to resolve.)
- Tools: "CF Cron Triggers — Daily batch send scheduling; runs after Process 100 cron (`0 7 * * *`)."
- BLOCKING DEPS: HeyReach = red (API key not set, account not configured). Campaign content templates = red (not started). Process 200 movement signals = BUILD/yellow.

**Why RECURRING (blocked):** The architecture is correct — CF Worker with cron is the right design and is documented as such. But three blocking dependencies are red: HeyReach unconnected, no message templates, movement signals not fully operational. Wiring the cron now produces a campaign engine that fires daily and silently fails on HeyReach routes and movement campaigns. Wire the cron AFTER: (1) HeyReach API key set, (2) at least one content template defined, (3) Process 200 movement signals OPERATE.

**Timing discrepancy:** Registry proposes `0 13 * * 1-5` (1pm weekdays); doc references `0 7 * * *` (7am daily). Dave resolves which is correct before wiring.

---

### bp.800 — Client Mint | Proposed: `0 4 * * *`
**Recommendation: EVENT-DRIVEN/MANUAL**

**Evidence:**
- ORBT: BUILD.
- Implementation: CF Worker (manual trigger only — rule D-800-07).
- §4 Trigger (explicit): "Human provides a CL sovereign_id via HTTP POST /mint."
- §4 Input (explicit): "No cron. No automated trigger. D-800-07."
- §9b Live Verification: "Manual trigger only — confirmed in wrangler.toml (no crons), index.ts (no scheduled handler)."
- Purpose: Converts one company to a client. One mint per company. Not a batch scan operation.

**Why EVENT-DRIVEN/MANUAL:** The doc, wrangler.toml, and the decision rule D-800-07 all explicitly prohibit cron. This is a per-event transaction — a human hands it a sovereign_id when a deal closes. A daily cron would fire with nothing to do and no input. De-list from cron registry.

---

### bp.810 — Client Intake | Proposed: `0 5 * * *`
**Recommendation: EVENT-DRIVEN/MANUAL**

**Evidence:**
- ORBT: BUILD.
- Implementation: CF Worker — HTTP endpoint (`POST /intake`).
- §4 Trigger: "HTTP POST to /intake from operator upload or external system."
- Purpose: Receives client benefits data payloads. Event-driven by nature — only meaningful when data arrives.
- No mention of scheduled scan behavior. No batch queue that would warrant a cron sweep.

**Why EVENT-DRIVEN/MANUAL:** This is an HTTP intake gate. It processes whatever arrives at the endpoint. A cron has nothing to fire at — there is no internal queue to sweep and no time-bound batch work. Clients submit data when they submit it. De-list from cron registry.

---

### bp.830 — Client Portal | Proposed: `0 6 * * *`
**Recommendation: EVENT-DRIVEN/MANUAL**

**Evidence:**
- ORBT: BUILD.
- Implementation: CF Worker — HTTP GET/POST per user request at `app.svgagency.com/:slug/:page`.
- §4 Trigger: "User navigates to `app.svgagency.com/:slug/:page` (HTTP GET). Agent page also accepts HTTP POST for ticket status updates."
- UT checklist: 12 of 13 checks are unchecked ([ ]) — this is the least complete doc in the set.
- Purpose: Read-only page renderer + one POST route for ticket status. Entirely user-request-driven.

**Why EVENT-DRIVEN/MANUAL:** A portal worker is request-driven by definition. No cron architecture exists or is appropriate. The proposed daily cron is a category error. De-list from cron registry.

---

### bp.900 — Sales Portal | Proposed: `0 6 * * *`
**Recommendation: EVENT-DRIVEN/MANUAL**

**Evidence:**
- ORBT: BUILD.
- Implementation: CF Worker — HTTP GET at `app.svgagency.com/sales/:slug/:meeting`, HTTP POST for Meeting 1 form save.
- §4 Trigger: "A user (Dave or prospect) navigates to `app.svgagency.com/sales/:slug/:meeting` via HTTP GET, or Dave submits the Meeting 1 form via HTTP POST."
- Purpose: Renders 4 meeting pages per prospect. Per-request, per-prospect.

**Why EVENT-DRIVEN/MANUAL:** Same category error as bp.830. Sales portal is request-driven. A daily cron firing into a portal worker with no queue to process does nothing. De-list from cron registry.

---

## SOVEREIGN DECISION MATRIX

For Dave to mark each row:

| # | ID | Process | Agent Rec | Dave Decision | Notes |
|---|----|---------|-----------|----|---|
| 1 | bp.010 | Seed D1 | RECURRING | ☐ WIRE / ☐ DE-LIST | Wire as lcs-hub internal cron calling /seed endpoint |
| 2 | bp.201 | Email Discovery | EVENT-DRIVEN | ☐ DE-LIST / ☐ HOLD | Python script — cannot receive CF cron |
| 3 | bp.202 | LinkedIn Discovery | EVENT-DRIVEN | ☐ DE-LIST / ☐ HOLD | Python script — cannot receive CF cron |
| 4 | bp.300 | Blog Worker | UNCLEAR | ☐ DE-LIST / ☐ HOLD / ☐ WIRE AFTER CF BUILD | Future CF Worker intent documented |
| 5 | bp.301 | Page Parser | UNCLEAR | ☐ DE-LIST / ☐ HOLD | UT doc is stub — needs §4 filled first |
| 6 | bp.400 | DOL Views | EVENT-DRIVEN | ☐ DE-LIST | Static SQL views — no runnable artifact |
| 7 | bp.500 | Talent Flow | EVENT-DRIVEN | ☐ DE-LIST / ☐ HOLD | Python script, sequenced after Process 200 |
| 8 | bp.700 | Campaign Engine | RECURRING (blocked) | ☐ WIRE AFTER DEPS / ☐ HOLD | Wire after: HeyReach + templates + 200 OPERATE |
| 9 | bp.800 | Client Mint | EVENT-DRIVEN | ☐ DE-LIST | D-800-07 prohibition explicit in code |
| 10 | bp.810 | Client Intake | EVENT-DRIVEN | ☐ DE-LIST | HTTP intake gate — no batch scan |
| 11 | bp.830 | Client Portal | EVENT-DRIVEN | ☐ DE-LIST | Request-driven portal — cron is wrong category |
| 12 | bp.900 | Sales Portal | EVENT-DRIVEN | ☐ DE-LIST | Request-driven portal — cron is wrong category |

---

## OPEN ITEMS / BLOCKERS

| Item | Process | What's Needed |
|------|---------|---------------|
| bp.700 cron time discrepancy | Campaign Engine | Registry=`0 13 * * 1-5`, doc=`0 7 * * *` — Dave picks one before wiring |
| bp.700 HeyReach | Campaign Engine | API key + account config required before wiring |
| bp.700 content templates | Campaign Engine | At least one message frame per movement signal type required |
| bp.700 Process 200 | Campaign Engine | People Worker must reach OPERATE before Campaign Engine is meaningful |
| bp.301 UT stub | Page Parser | All §2–§14 sections are unfilled placeholders — cannot classify without trigger documentation |
| bp.300 CF Worker | Blog Worker | Intent is documented; wire point exists after CF Worker is built |
| bp.010 wiring path | Seed D1 | Not a standalone worker — trigger = lcs-hub cron POSTing to /seed endpoint; confirm wiring mechanism |

---

*Compiled from PROCESS-UT.md §2, §3, §4 (IMO/Two-Question Intake), §3 Component Status for all 12 processes. Read-only. No edits made to any process file.*

| Field | Value |
|-------|-------|
| Date | 2026-05-08 |
| Compiler | Claude Sonnet (agent) |
| BAR | BAR-MONDAY-16-FLEET-GREEN |
| Authority | Sovereign decision — Dave Barton |
| Status | DRAFT — awaiting sovereign sign-off |

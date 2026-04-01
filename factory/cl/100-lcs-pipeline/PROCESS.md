# PROCESS: LCS Pipeline
## Three-stage compiler — CID (gather intel) → SID (build message) → MID (deliver it) — converts raw signals into delivered outreach
### Status: OPERATE
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-100 |
| Name | LCS Pipeline |
| Business Silo | svg-agency |
| Sub-Hub | cl (Company Lifecycle) |
| CTB Position | factory/cl/100-lcs-pipeline |
| Blueprint Repo | company-lifecycle-cl |
| Blueprint Section | doctrine/OSAM.md — SUBHUB-CL-LCS (lcs.event, lcs.err0, registries) |
| ORBT | OPERATE |
| Strikes | 0 |
| Last Deployed | 2026-03-24 (v2 — compiler-v2.ts) |
| BAR Reference | BAR-37, BAR-48, BAR-51, BAR-152 |
| Deployed URL | https://lcs-hub.svg-outreach.workers.dev |
| Cron | `0 7 * * *` (daily 7am UTC — scan pending signals + reset domain counters) |
| Runtime | CF Worker (cron + HTTP + queue consumer) |

---

## 2. WHY THIS EXISTS

This is the outreach machine. Every upstream process (200 People, 300 Blog, 400 DOL, 500 Talent Flow) feeds signals into a queue. This process compiles those signals into personalized messages and delivers them. Without it, all the data collection is pointless — you have a dossier on 32K companies but nobody gets contacted.

The compiler is config-driven. Signal types, message frames, and delivery adapters are all registry tables. Adding a new signal or message template is a database INSERT, not a code change.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Signals arrive in `lcs_signal_queue` from upstream worker spokes. Daily cron scans for pending. Queue consumer processes in real-time.
2. **"How do we get it?"** — D1 spine (signal queue) + D1 outreach (company data). Neon is vault only.

### Input
- Signals from upstream processes: sovereign_company_id, signal_set_hash, priority
- Company footprint from D1 outreach (CT, DOL, People, Blog)
- Company identity from D1 spine (cl_company_identity)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Signal in queue | **CID Compilation** — read company data from D1 outreach. Determine intelligence tier (2-5) by data completeness. Select message frame from registry. Run 9-gate qualification. | `lcs_cid` record | D1 queries |
| 2 | CID record | **SID Construction** — read CID + frame template. Get recipient from people slots (CFO → CEO → HR priority). Build personalized subject/body. | `lcs_sid_output` record | D1 queries |
| 3 | SID record | **MID Delivery** — pick sending domain from 14-domain rotation (LRU, daily cap). Deliver via Mailgun (email) or HeyReach (LinkedIn). | `lcs_mid_sequence_state` record + delivered message | Mailgun API / HeyReach API |
| 4 | Webhook callback | **Feedback** — Mailgun/HeyReach webhooks update delivery status. Bounces trigger ORBT strikes. Strike 3 = human escalation. | Updated MID state + lcs_event record | Webhook receiver |

### Output
- Delivered email or LinkedIn message to target recipient
- Full audit trail: signal → CID → SID → MID → event (traceable via `/trace/{id}`)
- Delivery status: SENT, DELIVERED, OPENED, CLICKED, BOUNCED, FAILED

### Circle (Bedrock §5)
Webhook responses feed back → update MID state → bounces trigger ORBT strikes → strike 3 = human escalation. Each delivery cycle makes the next one smarter (intelligence tier adjusts, frame selection improves).

---

## 4. WHAT IT GRABS OFF THE WALL

### Snap-On Toolbox Sub-Hub References

> Reference: `law/SNAP_ON_TOOLBOX.yaml`

| Sub-Hub | What This Process Uses |
|---------|----------------------|
| 11-structured-data | D1 spine read/write + D1 outreach read-only |
| 13-error-queue | CF Queues (lcs-pipeline + lcs-dlq) |
| 15-scheduling | Daily cron 7am UTC (scan pending signals + reset domain counters) |
| 22-webhook-gateway | Mailgun/HeyReach webhook receiver |
| 06-api-layer | Hono HTTP endpoints (/health, /status, /signal, /signals, /company/{id}, /trace/{id}, /run, /webhook/*) |

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-spine | D1 | 641a9a1e | READ/WRITE | Signal queue, CID, SID, MID, event log, error drain, registries, domain rotation |
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ ONLY | Company target, DOL, people slots, people master |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| MAILGUN_API_KEY | imo-creator | dev | MID delivery via Mailgun |
| HEYREACH_API_KEY | imo-creator | dev | MID delivery via HeyReach |

---

## 5. OSAM — Where the Data Lives

### Blueprint Reference

| Blueprint | Repo | Path | What It Defines |
|-----------|------|------|----------------|
| CL OSAM | company-lifecycle-cl | doctrine/OSAM.md | CL spine, LCS tables, join paths |
| Outreach OSAM | barton-outreach-core | doctrine/OSAM.md | Outreach footprint (read-only by LCS) |
| Snap-On Toolbox | imo-creator | law/SNAP_ON_TOOLBOX.yaml | Tool sub-hubs, vendors |
| D1 Data Dictionary | Barton-Processes | D1_DATA_DICTIONARY.md | AI-ready column reference |

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `lcs_signal_queue` | Incoming signals from upstream | `signal_queue_id` |
| `lcs_signal_registry` | 9 signal type definitions | `signal_set_hash` |
| `lcs_frame_registry` | 11 message frame templates | `frame_id` |
| `lcs_adapter_registry` | 3 delivery adapters (MG/HR/SH) | `adapter_type` |
| `lcs_domain_rotation` | 14 Mailgun sending domains | `domain_id` |
| `outreach_company_target` | Company data (CT sub-hub) | `company_unique_id` |
| `outreach_dol` | DOL filings | `outreach_id` |
| `people_company_slot` | CEO/CFO/HR slots | `outreach_id` |
| `people_people_master` | Contact details (email, LinkedIn) | `person_unique_id` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `lcs_cid` | Compiled Intelligence Dossier | Step 1 |
| `lcs_sid_output` | Constructed message | Step 2 |
| `lcs_mid_sequence_state` | Delivery state | Step 3 |
| `lcs_event` | Append-only audit trail (CANONICAL) | Every step |
| `lcs_err0` | Error drain with ORBT strikes (ERROR) | On failure |

### Join Chain

```
lcs_signal_queue.signal_set_hash → lcs_signal_registry.signal_set_hash
lcs_signal_queue.sovereign_company_id → outreach_company_target.company_unique_id
  → outreach_dol.outreach_id
  → people_company_slot.outreach_id → people_people_master.unique_id
lcs_cid.frame_id → lcs_frame_registry.frame_id
lcs_mid_sequence_state.adapter_type → lcs_adapter_registry.adapter_type
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Query Neon during pipeline ops | D1 only. SEED already pulled the data. |
| Hardcode signal types or frames | Config-driven. Registry INSERT only. |
| Skip the 9-gate qualification | Every company must pass gates before SID construction. |
| Send without checking daily domain cap | Domain rotation enforces warmup limits. |

### Domain Warmup / Ramp Strategy

**The warmup IS the campaign.** No separate warmup process needed. Mailgun shared IPs are already warm. Domain reputation builds by sending real outreach at controlled volume.

| Week | Daily Cap/Domain | Total/Day (14 domains) | Cumulative |
|------|-----------------|----------------------|------------|
| 1 | 20 | 280 | 1,960 |
| 2 | 40 | 560 | 5,880 |
| 3 | 80 | 1,120 | 13,720 |
| 4 | 150 | 2,100 | 28,420 |
| 5+ | 250 | 3,500 | Full volume |

**Ramp rules (enforced by `lcs_domain_rotation` table):**
- `warmup_week` increments weekly via cron (every Monday 07:00 UTC)
- `daily_cap` doubles each week until target
- `sent_today` resets daily at 07:00 UTC
- If `bounce_count_24h` > 5% of `sent_today` → pause domain, flag for review
- If any domain paused → redistribute load to remaining domains
- Strike 3 on same domain → remove from rotation, investigate

**Why shared IPs, not dedicated:**
- Shared IPs are already warm (Mailgun's sender pool)
- Dedicated IPs cost extra and need weeks of IP warming on top of domain warming
- For our volume (280-3,500/day), shared IPs are correct
- Revisit when volume exceeds 10K/day

**LBB Integration (SID Content):**
The SID construction step queries LBB for context-enriched content before building the personalized message. The flow:
1. CID compiled (intelligence tier determined from company footprint)
2. **SID queries LBB** — subject: svg-sales (Barton voice, DISC, messaging frameworks) + svg-outreach (company-specific intel)
3. LBB returns relevant knowledge records matching the signal type + company profile
4. SID constructs message using: frame template (registry) + LBB content + CID intelligence
5. Result: a message that sounds like Dave, informed by what we actually know

This replaces the old "SVG Brain" reference. LBB IS the brain. One library, Dewey Decimal.

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants
- Three-stage compiler: CID → SID → MID. Always sequential.
- 9 signal types in registry (extensible via INSERT)
- 11 message frames in registry (extensible via INSERT)
- 3 delivery adapters: Mailgun, HeyReach, SVG Brain (extensible via INSERT)
- 14 Mailgun sending domains with rotation
- Slot priority: CFO → CEO → HR
- Intelligence tiers: 2 (best data) through 5 (minimal data)
- ORBT 3-strike protocol: AUTO_RETRY → ALT_CHANNEL → HUMAN_ESCALATION
- ID format: `LCS-{PHASE}-{DATE}-{ULID}`

### Variables
- Which signals are pending in queue
- Which companies qualify through gates
- Which intelligence tier each company lands on
- Which domain gets selected for send (LRU rotation)
- Delivery status per message (SENT → DELIVERED → OPENED → CLICKED or BOUNCED)
- Daily sent counts per domain (resets at 07:00 UTC)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Signal has no sovereign_company_id | REJECT — write to lcs_err0 |
| Company not found in D1 outreach | REJECT — COMPANY_NOT_FOUND error |
| No filled slot with reachable contact | REJECT — NO_RECIPIENT error |
| All domains at daily cap | HALT — wait for next day reset |
| Mailgun API returns 5xx on 3 consecutive sends | HALT — check API key, domain health |
| Strike 3 on delivery | HUMAN_ESCALATION — system gives up |
| Queue DLQ accumulating | Investigate — signals failing repeatedly |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 010 (SEED) | D1 outreach populated | DONE |
| Process 200 (People) | CEO/CFO/HR slots filled | BUILD |
| Process 300 (Blog) | Content signals | BUILD |
| Process 400 (DOL) | DOL filing data | DONE |
| Process 500 (Talent Flow) | Movement signals | BUILD |
| Signal registry | 9 signal types defined | DONE |
| Frame registry | 11 message frames defined | DONE |
| Adapter registry | 3 adapters configured | DONE |
| Domain rotation | 14 Mailgun domains verified | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Dashboard / Mission Control | lcs_event + lcs_err0 for pipeline stats |
| Vault Sync (weekly) | D1 spine tables → Neon vault |

---

## 9. SMOKE TEST

```
1. GET lcs-hub.svg-outreach.workers.dev/health → expected: status ok, companies > 0
2. GET /status → check for pending signals
3. POST /signal with test sovereign_company_id → expected: signal queued
4. POST /run with signal_queue_id → expected: CID compiled, SID constructed, MID attempted
5. GET /trace/{communication_id} → expected: full chain (CID + SID + MID + events)
6. Check lcs_event for audit trail entries
7. Check lcs_err0 for any errors — should be 0 on success
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Does the signal exist in the queue? Does the company exist in D1?
2. **Flow:** Does the signal reach CID? Does CID reach SID? Does SID reach MID?
3. **Change:** Is the message compiled correctly? Is it delivered?

---

## 10. ANALYTICS

_What gets measured. All values BASELINE until first production run._

### Metrics

| Metric | Type | Baseline | First Run | Notes |
|--------|------|----------|-----------|-------|
| Signals processed | count | BASELINE | — | Total signals dequeued from lcs_signal_queue |
| CIDs compiled | count | BASELINE | — | Successful CID records created |
| SIDs constructed | count | BASELINE | — | Successful SID records created |
| MIDs delivered | count | BASELINE | — | Messages successfully sent |
| Delivery rate | % | BASELINE | — | MIDs delivered / MIDs attempted |
| Bounce rate | % | BASELINE | — | BOUNCED / total MIDs |
| Compilation success rate | % | BASELINE | — | CIDs compiled / signals processed |
| Intelligence tier distribution | % per tier | BASELINE | — | Breakdown: tier 2 / 3 / 4 / 5 |
| Domain rotation utilization | sent/cap | BASELINE | — | Messages sent per domain vs daily cap |
| Webhook response rate | % | BASELINE | — | Webhooks received / MIDs sent |

### Tool Scorecard

| Tool | Expected | Actual | Status |
|------|----------|--------|--------|
| D1 spine | Available | BASELINE | — |
| D1 outreach | Available | BASELINE | — |
| Mailgun API | 200 OK | BASELINE | — |
| HeyReach API | 200 OK | BASELINE | — |
| CF Queue | Processing | BASELINE | — |

### Sigma Tracking

| Run Date | Metric | Value | Sigma Direction | Notes |
|----------|--------|-------|----------------|-------|
| — | — | — | — | _No runs yet_ |

### ORBT Gate Rule

- **Sigma tightening** = real constant. Lock it.
- **Sigma flat** = phantom constant. Investigate.
- **Sigma expanding** = broken prior constant. Back-propagate and fix.
- **Strike 3 on same metric** = Troubleshoot/Train, not another repair.

---

## 11. LOGBOOK

### 2026-03-24 — v2 deployed

**ORBT:** BUILD → OPERATE
**Trigger:** Manual deployment
**Records processed:** Smoke test — 2 CIDs compiled
**Errors:** 0
**Tools used:** compiler-v2.ts, D1 spine + outreach
**Result:** Pipeline functional. Config-driven. 9 signals, 11 frames, 3 adapters, 14 domains registered.
**ORBT after:** OPERATE

### 2026-03-23 — v1 smoke test

**ORBT:** BUILD
**Trigger:** Local smoke test
**Result:** Pipeline works but fetchCompanyData was querying Neon. Fixed to D1.
**ORBT after:** BUILD

---

## 12. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-23 | fetchCompanyData querying Neon | Original code used Hyperdrive | Rewired to D1 outreach | 1 |
| 2 | 2026-03-23 | max_batch_timeout exceeded CF limit | Set to 300, CF limit is 60 | Set to 60 | 1 |
| 3 | 2026-03-24 | Compiler v1 created duplicate D1 tables | v1 didn't use existing spine/outreach | v2 reads existing D1 | 1 |
| 4 | 2026-03-29 | Mailgun webhook URL not configured | Dashboard setup incomplete | TODO — point Mailgun dashboard to /webhook/mailgun | 0 |
| 5 | 2026-03-29 | HeyReach webhook URL not configured | Dashboard setup incomplete | TODO — point HeyReach to /webhook/heyreach | 0 |

---

## 13. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-23 | v1 smoke test, compiler architecture defined | decisions/2026-03-23 |
| 2026-03-24 | v2 build + deploy, process extracted | session/2026-03-24-full-session-final |
| 2026-03-30 | PROCESS.md written from template | none |
| 2026-03-29 | PROCESS.md rewrite — CTB position, sub-hub, blueprint, Snap-On Toolbox refs, blueprint reference table | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-30 |
| Last Modified | 2026-03-29 |
| Version | 2.0.0 |
| Template Version | 3.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | company-lifecycle-cl/doctrine/OSAM.md — SUBHUB-CL-LCS |
| Data Flow | factory/cl/DATA_FLOW.md |

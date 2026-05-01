# PROCESS-UT — Process 280 LCS Delivery Hub
# BAR-357 | Governance backfill — code shipped, UT doc written post-deploy

---

## UT Pre-Flight Checklist (per `law/UT_CHECKLIST.md` v1.2.0)

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §1 PRD |
| 2 | OSAM — READ / WRITE / Join Chain / Forbidden Paths / Query Routing | ☑ | §6 JOIN CONTRACT + §9 PERMISSIONS |
| 3 | Component Status — every dependency has 🟢 / 🟡 / 🔴 with 1-line state | ☑ | §3 COMPONENT STATUS |
| 4 | Owner — human who fixes this at 2 AM | ☑ | §2 OWNER |
| 5 | Live Dashboard — URL or explicit "N/A" | ☑ | §2 OWNER |
| 6 | Kill Switch — exact command to stop the process | ☑ | §8 INGEST CHECKLIST |
| 7 | Logbook — last audit verdict + date (after certification only) | ☑ | §14 DOCUMENT CONTROL |
| 8 | FCEs Attached — which FCE runs structurally back this doc | ☑ | §11 FCE |
| 9 | BARs Referenced — every BAR this doc touches, with status | ☑ | §13 BARS REFERENCED |
| 10 | LBB Subjects Fed — which LBB subject(s) this doc's session logs go to | ☑ | §12 LBB |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | ☑ | §4 IMO |
| 12 | Live Verification — every numeric count, cron, URL, command, BAR status grounded | ☑ | §3 COMPONENT STATUS |
| 13 | ctb_node — declared path on Barton Enterprises CTB trunk | ☑ | heir.yaml + §4 IMO |

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 1 — IDENTITY
     ════════════════════════════════════════════════════════════ -->

## §1 PRD

**What:** The LCS Delivery Hub is the email send scheduler and delivery status dashboard for SVG Agency outreach campaigns. It processes CampaignQueueItem records, enforces per-domain daily send limits and warmup phase rules, dispatches emails via Mailgun, records FireDailyRun audit logs, and surfaces delivery status via a Mission Control dashboard (LCSDelivery.tsx).

**Why:** SVG Agency runs email outreach at scale across multiple sending domains in varying warmup phases. Without governed delivery scheduling, domains exceed daily limits, warmup phases are violated, and campaign send history is unauditable. The LCS Delivery Hub enforces the throttle, maintains the audit trail, and gives Dave a single dashboard view of delivery health.

**Who:** Dave Barton (operator). SVG Agency outreach team (dashboard consumers). Campaign engine Process 700 (upstream queue producer).

**Scope:** lcs-hub CF Worker (scheduler + /lcs/delivery-status endpoint). Mission Control LCSDelivery.tsx (React dashboard component, CF Access gated). D1 tables: sender_domains, campaign_queue, fire_daily_runs. Mailgun integration for actual send dispatch.

**Out of scope:** Email content generation (Campaign Engine, Process 700). Contact record mutations (people-worker, Process 200). Cross-entity sends (SVG Agency only). Reply tracking / inbox classification (Process 280 inbox-agent).

**Success metric:** Every daily run produces a FireDailyRun record with domains_used populated. No domain exceeds daily_limit. Paused domains receive zero sends. LCSDelivery.tsx renders current SenderDomain[] + FireDailyRun[] from a single /lcs/delivery-status fetch.

---

## §2 OWNER

**Owner:** Dave Barton — dbarton@svg.agency
**Fixes at 2 AM:** Dave Barton
**Live Dashboard:** Mission Control LCSDelivery.tsx (CF Access gated — Dave only)
**On-call escalation:** N/A

---

## §3 COMPONENT STATUS

| Component | Status | State |
|-----------|--------|-------|
| lcs-hub CF Worker (scheduler) | 🟢 | Deployed — daily cron firing, queue processing active |
| /lcs/delivery-status endpoint | 🟢 | Returns SenderDomain[] + FireDailyRun[] |
| Mission Control LCSDelivery.tsx | 🟢 | Rendering delivery dashboard in Mission Control |
| D1 sender_domains table | 🟢 | Canonical SenderDomain registry |
| D1 campaign_queue table | 🟢 | CampaignQueueItem records — pending/sent/failed/skipped |
| D1 fire_daily_runs table | 🟢 | Append-only FireDailyRun audit log |
| Mailgun integration | 🟢 | Bound to SenderDomain records — dispatching sends |
| Process 200 (people-worker) | 🟢 | Contact data source — read-only from lcs-hub |
| Process 700 (campaign-engine) | 🟢 | Upstream queue producer — supplies CampaignQueueItem records |

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 2 — CONTRACT
     ════════════════════════════════════════════════════════════ -->

## §4 IMO

**CTB node:** `barton-enterprises → BRANCH 1: Insurance Informatics → SVG Agency → Hub: Outreach`
**Hub-Spoke role:** Hub (lcs-hub is the Middle — all scheduling + dispatch + logging logic)
**Altitude:** leaf (10K ft — operational)
**IMO topology:** middle

```
INPUT                          MIDDLE (lcs-hub)                        OUTPUT
────────────────────────────   ─────────────────────────────────────   ────────────────────────
Cron trigger (daily send)   →  Read campaign_queue (status=pending)  → Mailgun send dispatch
  OR                            Filter by SenderDomain.warmup_phase     (per CampaignQueueItem)
GET /lcs/delivery-status        Enforce SenderDomain.daily_limit      → D1 write: queue item
  (Mission Control fetch)       Dispatch via Mailgun                     status update
                                Write FireDailyRun record             → D1 write: FireDailyRun
                                Return SenderDomain[] + FireDailyRun[]→ JSON response
                                  on /lcs/delivery-status               (LCSDelivery.tsx)
```

**Hub-Spoke geometry:**
- Hub: lcs-hub CF Worker (all logic)
- Spoke 1: D1 (canonical — sender_domains, campaign_queue, fire_daily_runs)
- Spoke 2: Mailgun (external send — dumb transport)
- Spoke 3: Process 200 people-worker (contact enrichment — read-only)
- Rim: Mission Control LCSDelivery.tsx (read-only view of /lcs/delivery-status)

**Three Primitives check:**
- Thing: SenderDomain record exists with warmup_phase ≠ paused before any send dispatches
- Flow: CampaignQueueItem (status=pending) flows from D1 → scheduler → Mailgun dispatch
- Change: Mailgun send → queue item status update (pending→sent/failed) → FireDailyRun write (ordered)

---

## §5 CONTRACT

### SenderDomain Shape

| Field | Type | Description |
|-------|------|-------------|
| domain | string | Sending domain (e.g., svg.agency) |
| status | enum: active \| inactive \| suspended | Domain operational status |
| daily_limit | integer | Max emails per 24-hour window |
| sent_today | integer | Emails sent in current 24-hour window |
| warmup_phase | enum: cold \| warming \| warm \| paused | Current warmup phase |

### FireDailyRun Shape

| Field | Type | Description |
|-------|------|-------------|
| run_id | string (UUID) | Canonical run ID |
| fired_at | ISO 8601 datetime | Run execution timestamp |
| total_sent | integer | Total emails successfully dispatched |
| total_failed | integer | Total emails that failed dispatch |
| domains_used | string[] | Array of domains that sent in this run (non-empty if total_sent > 0) |

### CampaignQueueItem Shape

| Field | Type | Description |
|-------|------|-------------|
| queue_id | string (UUID) | Canonical queue item ID |
| campaign_id | string | References campaign record |
| contact_id | string | References contact record (read-only — no writes to contacts) |
| scheduled_at | ISO 8601 datetime | Scheduled send time |
| status | enum: pending \| sent \| failed \| skipped | One-directional status transition |

### /lcs/delivery-status Response Shape

```json
{
  "sender_domains": [SenderDomain, ...],
  "recent_runs": [FireDailyRun, ...]
}
```

Single fetch — LCSDelivery.tsx receives both arrays in one response. No second fetch required.

---

## §6 JOIN CONTRACT

**Primary join chain:**
```
campaign_queue (status=pending)
  → CampaignQueueItem.contact_id
    → Process 200 people-worker (READ — email address lookup)
      → Mailgun dispatch (SenderDomain selected by warmup_phase + daily_limit)
        → campaign_queue status update (pending → sent/failed/skipped)
        → fire_daily_runs INSERT (domains_used populated)
```

**Dashboard fetch chain:**
```
GET /lcs/delivery-status
  → sender_domains table READ (all SenderDomain records)
  → fire_daily_runs table READ (recent runs, ordered by fired_at DESC)
  → JSON response → LCSDelivery.tsx render
```

**READ path:** scheduler → D1 campaign_queue (pending filter) → people-worker contact READ → Mailgun
**WRITE path:** post-send → D1 campaign_queue status update → D1 fire_daily_runs INSERT
**FORBIDDEN:** Direct contacts table writes from lcs-hub. Cross-entity sends. Status reversions on queue items.

---

## §7 SCHEMA

```sql
-- sender_domains
CREATE TABLE sender_domains (
  domain TEXT PRIMARY KEY,
  status TEXT NOT NULL CHECK(status IN ('active','inactive','suspended')),
  daily_limit INTEGER NOT NULL,
  sent_today INTEGER NOT NULL DEFAULT 0,
  warmup_phase TEXT NOT NULL CHECK(warmup_phase IN ('cold','warming','warm','paused')),
  updated_at TEXT NOT NULL
);

-- campaign_queue
CREATE TABLE campaign_queue (
  queue_id TEXT PRIMARY KEY,
  campaign_id TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  scheduled_at TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('pending','sent','failed','skipped')),
  domain_used TEXT REFERENCES sender_domains(domain),
  processed_at TEXT
);

CREATE INDEX idx_campaign_queue_status ON campaign_queue(status);
CREATE INDEX idx_campaign_queue_scheduled_at ON campaign_queue(scheduled_at);

-- fire_daily_runs (append-only)
CREATE TABLE fire_daily_runs (
  run_id TEXT PRIMARY KEY,
  fired_at TEXT NOT NULL,
  total_sent INTEGER NOT NULL DEFAULT 0,
  total_failed INTEGER NOT NULL DEFAULT 0,
  domains_used TEXT NOT NULL  -- JSON array of domain strings
);

CREATE INDEX idx_fire_daily_runs_fired_at ON fire_daily_runs(fired_at DESC);
```

---

## §8 INGEST CHECKLIST

**Adding a new sending domain:**
1. INSERT into sender_domains with warmup_phase = 'cold', daily_limit = (start conservative)
2. Verify Mailgun domain verification complete before setting status = 'active'
3. Progress warmup_phase cold → warming → warm as daily limits increase (BAR not required for phase changes — operational)

**Pausing a domain (kill switch — single domain):**
```sql
UPDATE sender_domains SET warmup_phase = 'paused', updated_at = datetime('now')
WHERE domain = '{domain}';
-- Scheduler will skip this domain on next run
```

**Kill switch — halt all outbound sends:**
```sql
UPDATE sender_domains SET warmup_phase = 'paused', updated_at = datetime('now');
```

**Kill switch — undeploy lcs-hub entirely:**
```bash
cd workers/lcs-hub
npx wrangler delete lcs-hub --force
```

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 3 — GOVERNANCE
     ════════════════════════════════════════════════════════════ -->

## §9 PERMISSIONS

**READ (/lcs/delivery-status):**
- Requires: MC_API_KEY Bearer + Cloudflare Access (Mission Control gate — Dave only)
- Who: LCSDelivery.tsx via Mission Control (authenticated)
- Forbidden: Public access to delivery status

**WRITE (campaign_queue status, fire_daily_runs):**
- Requires: Completed/failed send dispatch (scheduler-automated)
- Who: lcs-hub CF Worker scheduler only
- Forbidden: External HTTP writes to campaign_queue or fire_daily_runs

**READ (contacts — enrichment only):**
- Requires: Internal service call to Process 200 people-worker
- Who: lcs-hub scheduler (contact_id → email address lookup)
- Forbidden: Direct D1 reads on contacts table from lcs-hub; any write to contacts table

**FORBIDDEN PATHS:**
- Direct contacts table writes (D-LCS280-08)
- Cross-entity sends — SVG Agency only (D-LCS280-10)
- CampaignQueueItem status reversions (D-LCS280-07)
- Sends to paused warmup_phase domains (D-LCS280-06)
- Sends exceeding daily_limit (D-LCS280-05)
- FireDailyRun with empty domains_used when total_sent > 0 (D-LCS280-09)

**Three Primitives enforcement:**
- Thing: SenderDomain record must exist with warmup_phase ≠ paused before dispatch
- Flow: CampaignQueueItem must flow from pending state through scheduler before Mailgun call
- Change: Mailgun dispatch must complete before queue item status update and FireDailyRun write

---

## §10 ERROR HANDLING

| Scenario | Handler | Response |
|----------|---------|----------|
| Mailgun dispatch failure | lcs-hub error handler | Update queue item status = 'failed'; increment total_failed in FireDailyRun |
| Domain daily_limit reached mid-run | Scheduler throttle check | Skip remaining queue items for that domain; mark skipped; continue on other domains |
| warmup_phase = paused detected at run start | Scheduler domain filter | Exclude domain from run entirely; do not attempt sends |
| /lcs/delivery-status D1 read failure | Endpoint error handler | Return 500 with error message; LCSDelivery.tsx displays error state |
| FireDailyRun write failure | Post-run error handler | Log to CF Worker console; retry once; alert via Mission Control error surface |

---

## §11 FCE

**FCE attachment:** `barton-enterprises → BRANCH 1: Insurance Informatics → SVG Agency → Hub: Outreach`
**FCE runs:** Outreach FCE — LCS delivery metrics feed domain health signals into outreach concentration analysis
**Columns active:** Concentration (which domains carry highest send volume?), Trend (warmup phase progression — is deliverability improving?), Liquidity/Plumbing (daily_limit headroom — can the system execute the campaign volume?)

---

## §12 LBB

**LBB subject:** `svg-outreach` (outreach intelligence — delivery infrastructure)
**Secondary subject:** `svg-outreach-proc` (process-specific outreach learnings)
**Session log target:** Ingest BAR-357 completion record after batch closes
**Record template:** HEIR stamp + ORBT state (OPERATE) + acceptance criteria status

---

## §13 BARS REFERENCED

| BAR | Description | Status |
|-----|-------------|--------|
| BAR-357 | LCS Delivery Hub — lcs-hub CF Worker + LCSDelivery.tsx + SenderDomain/FireDailyRun/CampaignQueueItem interfaces | CLOSED (code shipped) |

---

## §14 DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| BAR | BAR-357 |
| Version | 1.0.0 |
| Status | OPERATE (governance backfill — code shipped pre-UT) |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Template | law/UNIFIED_TEMPLATE.md v2.0 |
| UT Checklist | law/UT_CHECKLIST.md v1.2.0 — 13 items, all addressed |
| Audit verdict | Pending batch audit (BAR-167 through BAR-48) |
| ctb_node | barton-enterprises → BRANCH 1: Insurance Informatics → SVG Agency → Hub: Outreach |

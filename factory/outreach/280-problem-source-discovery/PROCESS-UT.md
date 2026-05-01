# PROCESS-UT — Process 280 Problem Source Discovery
# BAR-315 | Governance backfill — code shipped, UT doc written post-deploy

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

**What:** Problem Source Discovery is the AI-powered inbox classification and auto-reply process for SVG Agency outreach. Inbound emails are classified against a locked CLASSES enum using a problem_source_chain prompt sequence, and AI-drafted replies are staged for review before sending.

**Why:** SVG Agency receives inbound responses across dozens of outreach campaigns. Manual triage is not scalable. Problem Source Discovery identifies what problem the prospect is signaling (the "problem source") so the campaign engine can route follow-up correctly. It also generates on-brand draft replies using locked DRAFT_RULES, eliminating blank-page friction for the human reviewer.

**Who:** SVG Agency outreach operators (human reviewers of staged replies). Dave Barton (process owner). Campaign engine (downstream consumer of classification output).

**Scope:** inbox-agent CF Worker — email classification via CLASSES enum + problem_source_chain, AI reply drafting via DRAFT_RULES + OpenRouter claude-sonnet-4-5, D1 canonical storage, staging table for draft replies, KV session deduplication.

**Out of scope:** Sending replies (staging gate only — human send action is out of scope for this process). Contact record mutations (read-only on people table — mutations route through Process 200). Campaign execution (Process 700).

**Success metric:** Every inbound message classified to a CLASSES value, classification record stored with message_id + sovereign_company_id, draft reply staged with DRAFT_RULES applied, no direct send from pipeline.

---

## §2 OWNER

**Owner:** Dave Barton — dbarton@svg.agency
**Fixes at 2 AM:** Dave Barton
**Live Dashboard:** Mission Control outreach dashboard (classification metrics view)
**On-call escalation:** N/A

---

## §3 COMPONENT STATUS

| Component | Status | State |
|-----------|--------|-------|
| inbox-agent CF Worker (Hono) | 🟢 | Deployed — email classification + reply drafting active |
| OpenRouter claude-sonnet-4-5 | 🟢 | Model live — classification + draft generation running |
| D1 canonical database | 🟢 | Stores classified messages + problem source records (migration 0019) |
| KV namespace | 🟢 | Session-level dedup only — not canonical |
| Staging table (D1) | 🟢 | AI-drafted replies land here before send gate |
| Process 200 (people-worker) | 🟢 | Contact data source — read-only from inbox-agent |
| Process 700 (campaign-engine) | 🟢 | Downstream consumer of problem source output |

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 2 — CONTRACT
     ════════════════════════════════════════════════════════════ -->

## §4 IMO

**CTB node:** `barton-enterprises → BRANCH 1: Insurance Informatics → SVG Agency → Hub: Outreach`
**Hub-Spoke role:** Hub (inbox-agent is the Middle — all classification + drafting logic lives here)
**Altitude:** leaf (10K ft — operational)
**IMO topology:** middle

```
INPUT                        MIDDLE (inbox-agent)                   OUTPUT
──────────────────────────   ──────────────────────────────────     ───────────────────────
Inbound email payload     →  Hono router                        →   D1 write: classified
  (webhook or poll)           CLASSES enum classification             message record
  + message_id                problem_source_chain (full)         →  D1 write: problem
  + sender context            OpenRouter claude-sonnet-4-5            source record
                              DRAFT_RULES applied                 →  D1 write: staged
                              Staging gate (no direct send)           draft reply
                              people table READ (enrichment)      →  KV: session dedup
                              sovereign_company_id lookup             (derived, not canon)
```

**Hub-Spoke geometry:**
- Hub: inbox-agent CF Worker (all logic)
- Spoke 1: D1 database (canonical writes — classified messages, problem source, staging)
- Spoke 2: KV namespace (session dedup — derived)
- Spoke 3: OpenRouter API (external LLM — dumb transport, no logic)
- Spoke 4: Process 200 people-worker (contact enrichment — read-only spoke)

**Three Primitives check:**
- Thing: inbound email exists with message_id before classification can run
- Flow: problem_source_chain executes in full before classification output is written to D1
- Change: classification → staged draft → human send action (ordered, staging gate enforced)

---

## §5 CONTRACT

### CLASSES Enum (Classification Taxonomy)

The CLASSES enum is a locked constant. Every inbound message resolves to exactly one value. Current values documented at time of BAR-315 ship — additions require a BAR.

| Class | Description |
|-------|-------------|
| INTERESTED | Prospect signals active interest in SVG Agency services |
| NOT_INTERESTED | Prospect explicitly declines or opts out |
| REFERRAL | Prospect refers to another contact |
| QUESTION | Prospect asks a clarifying question |
| OUT_OF_OFFICE | Auto-reply or OOO response |
| BOUNCED | Hard or soft bounce — invalid address |
| UNSUBSCRIBE | Explicit unsubscribe request |
| OTHER | Does not match any defined class (routes to default bucket) |

### problem_source_chain (Prompt Sequence)

The problem_source_chain is a locked chain-of-thought sequence. Every step executes in order. Steps are constants — values (prospect context) are variables.

| Step | Purpose |
|------|---------|
| 1. Context extraction | Extract sender identity, company, role from email |
| 2. Problem signal identification | Identify the problem the prospect is signaling |
| 3. Source attribution | Attribute the problem to a source category |
| 4. Classification | Map to CLASSES enum value |
| 5. Confidence scoring | Assign confidence (0.0–1.0) to classification |

### DRAFT_RULES (Reply Drafting Constants)

DRAFT_RULES are applied to every AI-drafted reply without exception. Rules are locked — additions require a BAR.

| Rule | Constraint |
|------|-----------|
| Tone | Professional, direct, Barton voice (no filler phrases) |
| Length | Max 3 paragraphs for standard replies |
| CTA | One clear call-to-action per reply |
| No fabrication | Draft may not invent facts not in the original email or contact record |
| Brand compliance | Must comply with SVG Agency messaging guidelines |

### Classification Record Shape

| Field | Type | Description |
|-------|------|-------------|
| record_id | string (UUID) | Canonical ID |
| message_id | string | Source email message ID (non-nullable) |
| sovereign_company_id | string | Company join key (non-nullable) |
| classification | CLASSES enum | Resolved classification value |
| confidence | float (0.0–1.0) | Chain-of-thought confidence score |
| problem_source | string | Attributed problem source category |
| classified_at | ISO 8601 datetime | Classification timestamp |

---

## §6 JOIN CONTRACT

**Primary join chain:**
```
Inbound email (message_id)
  → inbox-agent classification
    → classification_records (message_id FK)
    → problem_source_records (message_id FK + sovereign_company_id FK)
      → Process 700 campaign engine (sovereign_company_id JOIN key)
```

**Contact enrichment (read-only):**
```
sender email / domain
  → Process 200 people-worker (READ — people table)
    → person_id + sovereign_company_id lookup
      → enriches classification record (sovereign_company_id populated)
```

**READ path:** inbound email → CLASSES classification → D1 classification record
**WRITE path:** classified message → D1 write → staged draft → D1 staging table
**FORBIDDEN:** Direct people table writes. Partial problem_source_chain execution. Direct reply send from pipeline.

---

## §7 SCHEMA

### Migration 0019 Tables

```sql
-- classified_messages (canonical)
CREATE TABLE classified_messages (
  record_id TEXT PRIMARY KEY,
  message_id TEXT NOT NULL UNIQUE,
  sovereign_company_id TEXT NOT NULL,
  classification TEXT NOT NULL,   -- CLASSES enum value
  confidence REAL NOT NULL,
  problem_source TEXT,
  classified_at TEXT NOT NULL
);

-- staged_replies (draft gate)
CREATE TABLE staged_replies (
  reply_id TEXT PRIMARY KEY,
  message_id TEXT NOT NULL REFERENCES classified_messages(message_id),
  draft_body TEXT NOT NULL,
  draft_rules_version TEXT NOT NULL,
  model_used TEXT NOT NULL,       -- 'openrouter/claude-sonnet-4-5'
  staged_at TEXT NOT NULL,
  sent_at TEXT,                   -- NULL until human sends
  sent_by TEXT                    -- human actor who triggered send
);
```

---

## §8 INGEST CHECKLIST

**Adding a new CLASSES value:**
1. Add value to CLASSES enum in inbox-agent.ts
2. Update §5 CONTRACT table in this UT doc
3. Verify problem_source_chain step 4 maps the new class correctly
4. BAR required (D-280-01)

**Adding a new DRAFT_RULE:**
1. Add rule to DRAFT_RULES in inbox-agent.ts
2. Update §5 CONTRACT DRAFT_RULES table
3. BAR required (D-280-02)

**Kill switch — disable inbox-agent entirely:**
```bash
cd workers/inbox-agent
npx wrangler delete inbox-agent --force
```

**Kill switch — disable AI auto-reply (keep classification running):**
```typescript
// Set DRAFT_ENABLED = false in inbox-agent.ts environment config
// Redeploy: npx wrangler deploy
// Classification continues; no drafts written to staging table
```

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 3 — GOVERNANCE
     ════════════════════════════════════════════════════════════ -->

## §9 PERMISSIONS

**READ (contact enrichment):**
- Requires: Internal service call (inbox-agent → people-worker)
- Who: inbox-agent only (no external reads on people table)
- Forbidden: Direct D1 reads on people table from inbox-agent — must route through Process 200

**WRITE (classification records, staged replies):**
- Requires: Inbound email payload with valid message_id
- Who: inbox-agent CF Worker (automated pipeline)
- Gate: Staging table is mandatory — no reply may bypass staging

**EMIT (OpenRouter API calls):**
- Requires: OPENROUTER_API_KEY (Doppler secret)
- Who: inbox-agent only
- Model: claude-sonnet-4-5 via OpenRouter exclusively (no direct Anthropic API)

**FORBIDDEN PATHS:**
- Direct people table writes from inbox-agent (D-280-09)
- Partial problem_source_chain execution (D-280-04)
- Direct reply send from classification pipeline (D-280-05)
- Model substitution without BAR (D-280-03)
- Classification records without message_id (D-280-08)
- Problem source records without sovereign_company_id (D-280-10)

**Three Primitives enforcement:**
- Thing: message_id must exist before classification record can be written
- Flow: full problem_source_chain must complete before OpenRouter returns classification
- Change: classification → staging write (ordered; no staging bypass)

---

## §10 ERROR HANDLING

| Scenario | Handler | Response |
|----------|---------|----------|
| OpenRouter API failure | inbox-agent retry logic | Retry 3x; if still failing, write to error table with message_id + timestamp |
| CLASSES enum miss (unknown value) | Classification fallback | Route to OTHER class; log for review |
| sovereign_company_id not found | Classification record | Write record with sovereign_company_id = NULL; flag for manual enrichment |
| D1 write failure | inbox-agent error handler | Log to error table; do not retry silently |
| Partial chain execution detected | Chain validator | Abort; log chain step failure; do not write partial classification |

---

## §11 FCE

**FCE attachment:** `barton-enterprises → BRANCH 1: Insurance Informatics → SVG Agency → Hub: Outreach`
**FCE runs:** Outreach FCE — problem source discovery output feeds prospect classification for campaign targeting
**Columns active:** Concentration (where are inbound signals clustering?), Trend (is the problem source pattern shifting?), Valuation (which problem sources convert at highest rate?)

---

## §12 LBB

**LBB subject:** `svg-outreach` (outreach intelligence)
**Secondary subject:** `svg-outreach-proc` (process-specific outreach learnings)
**Session log target:** Ingest BAR-315 completion record after batch closes
**Record template:** HEIR stamp + ORBT state (OPERATE) + CLASSES enum snapshot + acceptance criteria status

---

## §13 BARS REFERENCED

| BAR | Description | Status |
|-----|-------------|--------|
| BAR-315 | Problem Source Discovery — inbox-agent AI auto-reply + CLASSES classification | CLOSED (code shipped) |

---

## §14 DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| BAR | BAR-315 |
| Version | 1.0.0 |
| Status | OPERATE (governance backfill — code shipped pre-UT) |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Template | law/UNIFIED_TEMPLATE.md v2.0 |
| UT Checklist | law/UT_CHECKLIST.md v1.2.0 — 13 items, all addressed |
| Audit verdict | Pending batch audit (BAR-167 through BAR-48) |
| ctb_node | barton-enterprises → BRANCH 1: Insurance Informatics → SVG Agency → Hub: Outreach |

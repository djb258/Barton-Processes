# PROCESS: Campaign Engine
## Sequences outreach messages (MIDs) based on movement detection — no movement = stay visible, movement = get the meeting
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-700 |
| Name | Campaign Engine |
| Business Silo | svg-agency |
| CTB Position | factory/svg-agency/700-campaign-engine |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed |
| BAR Reference | — |
| Deployed URL | not deployed |
| Cron | none (triggered by LCS pipeline CID output) |
| Runtime | CF Worker (future) |

---

## 2. WHY THIS EXISTS

This is the terminal execution layer. Every upstream process — SEED, People, Blog, DOL, Talent Flow, LCS Pipeline — exists to produce one thing: a reason to contact a human. Process 700 delivers that contact. Without it, the entire pipeline is a dossier factory with no output.

The campaign engine decides HOW to contact based on movement signals. No movement means the company is quiet — stay visible with a monthly generic touch. Movement detected means something changed (title, company, role) — escalate to 3-5 targeted touches over 2 weeks to get the meeting while the signal is hot.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — LCS Pipeline (100) compiles a CID for a company. The CID contains the target, the signal, and the message frame. Campaign Engine sequences the delivery.
2. **"How do we get it?"** — CID targets from D1 spine (`lcs_cid`). Movement signals from D1 outreach (people slots). Delivery via Composio routing to Mailgun (email) or HeyReach (LinkedIn).

### Input
- CID records from Process 100 (LCS Pipeline) — company target, signal type, intelligence tier, message frame
- Movement signals from Process 200 (People Worker) — binary per slot: moved (1) or static (0)
- Reachability status per company — EMAIL_ONLY, LINKEDIN_ONLY, or FULL (determines channel)
- Recipient contact info from `people_people_master` — verified email, LinkedIn URL

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | CID record from LCS pipeline | **Evaluate movement status** — check all 3 slots (CEO/CFO/HR) for movement signals. Binary: any slot moved = movement detected. | Campaign model selection: NO_MOVEMENT or MOVEMENT_DETECTED | D1 query |
| 2 | Campaign model + CID | **Build sequence** — NO_MOVEMENT: 1 generic introduction MID. MOVEMENT_DETECTED: 3-5 MIDs spaced every 2-3 days over ~2 weeks, frame matched to signal type. | Sequence plan: MID count, cadence, frame per position | D1 query (campaign registry) |
| 3 | Sequence plan + recipient | **Tag each MID** — stamp path_type (WARM/COLD), channel (MG/HR), movement_signal, sequence_position (e.g., "2 of 5"). | Tagged MID records in campaign queue | D1 write |
| 4 | Tagged MID | **Route to channel** — EMAIL_ONLY or FULL → Composio → Mailgun. LINKEDIN_ONLY → Composio → HeyReach. CTA link in every message. | Delivered message + delivery status | Composio → Mailgun API / HeyReach API |
| 5 | Delivery webhook callback | **Record outcome** — update MID state (SENT, DELIVERED, OPENED, CLICKED, BOUNCED, FAILED). Bounces write to error table. | Updated MID state + event log entry | Webhook receiver |

### Output
- Delivered outreach messages (email via Mailgun, LinkedIn via HeyReach)
- Full MID audit trail: CID → sequence plan → tagged MID → delivery status → webhook event
- Every MID tagged with path_type + channel + movement_signal + sequence_position

### Circle (Bedrock §5)
Webhook callbacks from Mailgun/HeyReach feed delivery status back to Process 100 (LCS Pipeline). Bounces and failures update the company's reachability status. Repeated bounces on a contact trigger ORBT strikes on the person record. Delivery metrics (open rate, click rate per frame type) inform frame selection in future CID compilations.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-spine | D1 | 641a9a1e | READ/WRITE | CID records, campaign queue, MID sequence state, event log, campaign registry tables |
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ ONLY | People slots (movement signals), people master (email, LinkedIn), company target |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| Composio | MCP / API | Cheap | COMPOSIO_API_KEY (Doppler) | Routes MIDs to Mailgun or HeyReach based on channel tag |
| Mailgun | API | Cheap | MAILGUN_API_KEY (Doppler) | Email delivery — uses LCS pipeline's 14-domain rotation |
| HeyReach | API | Cheap | HEYREACH_API_KEY (Doppler) | LinkedIn outreach delivery |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| COMPOSIO_API_KEY | imo-creator | dev | Step 4 — MID routing |
| MAILGUN_API_KEY | imo-creator | dev | Step 4 — email delivery |
| HEYREACH_API_KEY | imo-creator | dev | Step 4 — LinkedIn delivery |

**Tool Priority (Well Drinks First):**
1. D1 queries for campaign model evaluation and sequence building — always free
2. Composio routing to Mailgun (email) — cheap, primary channel
3. Composio routing to HeyReach (LinkedIn) — cheap, secondary channel

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `lcs_cid` (spine) | CID records — company target, signal type, intelligence tier, message frame | `sovereign_company_id` |
| `people_company_slot` | Movement signals per slot (CEO/CFO/HR), reachability | `outreach_id` |
| `people_people_master` | Recipient contact info — email, LinkedIn URL | `unique_id` via slot's `person_unique_id` |
| `outreach_company_target` | Company metadata for message personalization | `outreach_id` |
| Campaign registry tables (spine) | Campaign models, frame templates, sequence configurations | config lookup |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| Campaign queue (spine) | Tagged MID records: sequence plan, path_type, channel, movement_signal, sequence_position | Step 3 |
| `lcs_mid_sequence_state` (spine) | Delivery status per MID: SENT, DELIVERED, OPENED, CLICKED, BOUNCED, FAILED | Steps 4-5 |
| `lcs_event` (spine) | Webhook event log — delivery callbacks | Step 5 |
| Error table (spine) | Failed deliveries, bounces | Step 5 |

### Join Chain

```
lcs_cid.sovereign_company_id (CID from pipeline)
  → outreach_company_target.company_unique_id (company metadata)
  → people_company_slot.outreach_id (3 slots — movement signals)
    → people_people_master.unique_id (via person_unique_id — email, LinkedIn)
  → campaign_queue.cid_id (tagged MIDs for delivery)
    → lcs_mid_sequence_state.mid_id (delivery status)
      → lcs_event.mid_id (webhook callbacks)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Deliver without a CID | Every MID traces back to a CID. No CID = no delivery. |
| Skip tagging | Every MID must have path_type + channel + movement_signal + sequence_position. Untagged MIDs are untraceable. |
| Send to UNREACHABLE contacts | No verified email AND no LinkedIn URL = blocked. Do not attempt delivery. |
| Query Neon directly | D1 only during WORK phase. LCS pipeline already compiled the CID from D1 data. |
| Override domain rotation | Sending domains are managed by LCS pipeline (100). Campaign engine uses the assigned domain. |
| Send movement campaign without movement signal | Movement model requires a specific signal type. No signal = generic monthly only. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Which companies have pending CIDs? | `lcs_cid` | `status = 'pending'` |
| Does this company have movement? | `people_company_slot` | movement signal columns |
| What channel for this recipient? | `people_people_master` | `email IS NOT NULL` → MG, `linkedin_url IS NOT NULL` → HR |
| Where is this MID in the sequence? | Campaign queue | `sequence_position` |
| What happened after delivery? | `lcs_mid_sequence_state` | `delivery_status` |
| Did the webhook come back? | `lcs_event` | `event_type`, `received_at` |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)

- Two campaign models: NO_MOVEMENT (1 touch/month) and MOVEMENT_DETECTED (3-5 touches/2 weeks)
- Every MID tagged with 4 fields: path_type, channel, movement_signal, sequence_position
- Two delivery channels: Mailgun (email) and HeyReach (LinkedIn)
- Channel selection is deterministic: has email → MG, LinkedIn only → HR, both → MG primary
- Every MID must trace back to a CID. No orphan messages.
- CTA link required in every outreach message
- Movement cadence: every 2-3 days over ~2 weeks
- No-movement cadence: 1 per month
- Webhook feedback loop: delivery status feeds back to LCS pipeline
- Errors write to master error table in D1

### Variables (fill — changes every run)

- Which companies have pending CIDs (changes as pipeline runs)
- Which companies have movement signals (changes as People Worker detects changes)
- How many MIDs in queue (depends on signal volume)
- Delivery success rate per channel (Mailgun vs HeyReach)
- Open/click rates per frame type (informs future frame selection)
- Which sending domain gets assigned (LCS pipeline rotation)
- Sequence position per company (advances with each delivery)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Can't answer two-question intake | HALT — process isn't defined |
| No CID records in queue | Normal — nothing to deliver. Wait for next pipeline run. |
| Recipient has no email AND no LinkedIn | SKIP — mark as UNREACHABLE, do not attempt delivery |
| Composio routing errors > 5 consecutive | HALT — check Composio credentials and connection |
| Mailgun delivery errors > 20% of batch | HALT — check API key, domain status, sending limits |
| HeyReach delivery errors > 20% of batch | HALT — check API key, LinkedIn account status |
| Daily sending cap reached (per domain) | Normal — queue remaining MIDs for next day |
| Webhook callbacks not arriving > 24 hours | Investigate — Composio webhook config or endpoint down |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 100 (LCS Pipeline) | CID targets — which companies to campaign, with signal type and message frame | OPERATE |
| Process 200 (People Worker) | Movement signals per slot — determines campaign model selection | BUILD |
| Process 010 (SEED) | Company and people data in D1 | DONE |
| Composio integration | MID routing to Mailgun/HeyReach | CONFIGURED |
| Mailgun sending domains | 14 verified domains for email delivery | DONE (managed by 100) |
| HeyReach account | LinkedIn outreach delivery | PENDING |
| Campaign content templates | Message frames per movement signal type | NOT STARTED |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| None — terminal | Webhooks feed delivery status back to Process 100 (LCS Pipeline) |

---

## 9. SMOKE TEST

```
1. Verify CID exists: SELECT COUNT(*) FROM lcs_cid WHERE status = 'pending' → expected: > 0
2. Movement check: SELECT outreach_id, movement_signal FROM people_company_slot WHERE movement_signal IS NOT NULL LIMIT 5 → expected: rows with signal data
3. Tag a test MID: INSERT into campaign queue with path_type=COLD, channel=MG, movement_signal=NONE, sequence_position='1 of 1' → expected: row created
4. Route test MID via Composio to Mailgun sandbox → expected: 200 response, message queued
5. Receive webhook callback → expected: delivery status updated in lcs_mid_sequence_state
6. Trace full chain: CID → campaign queue → MID state → event log → expected: all records linked
7. Verify tagging: SELECT * FROM campaign_queue WHERE path_type IS NULL OR channel IS NULL → expected: 0 rows (no untagged MIDs)
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Does the CID exist in D1? Does the recipient have a contact method? Does the Composio route work?
2. **Flow:** Does the CID reach the campaign model selector? Does the tagged MID reach Composio? Does the webhook reach back?
3. **Change:** Is the MID correctly tagged? Is the message delivered? Is the delivery status recorded?

If any fails → that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock §6).

---

## 10. LOGBOOK

### 2026-03-29 — Process documentation created

**ORBT:** BUILD
**Trigger:** Manual — documenting process contract before implementation
**Records processed:** 0 (no source code yet)
**Errors:** 0
**Tools used:** None
**Result:** PROCESS.md written from heir.yaml contract and CLAUDE.md specifications. Campaign models, MID tagging, delivery routing, and feedback loop documented.
**Learnings:** Campaign content templates are the critical blocker. Can't build sequences without frame content per movement signal type.
**ORBT after:** BUILD

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | No source code — src/ directory empty | Process in BUILD, heir.yaml defines contract only | Build worker after campaign content templates defined | 0 |
| 2 | 2026-03-29 | Campaign content templates not defined | No content library per movement signal type | Define frames: JOINED, LEFT, REPLACED, TITLE_CHANGED, EMAIL_CHANGED, NONE | 0 |
| 3 | 2026-03-29 | Webhook feedback loop to LCS not built | Composio webhook → 100 pipeline status update not implemented | Build as part of campaign worker implementation | 0 |
| 4 | 2026-03-29 | HeyReach integration not configured | No API key, no account setup | Set up HeyReach account, add credentials to Doppler | 0 |

---

## 12. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | Process doc written from heir.yaml + CLAUDE.md contract. Template v2.0.0 format. | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

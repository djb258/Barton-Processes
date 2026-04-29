> **ARCHIVED 2026-04-29** — Consolidated into PROCESS-UT.md and DOCTRINE.md during UT v2.7.0 standardization. See sibling files at folder root.

# PRD — Process 200: People Worker
## Product Requirements — What It Does, What "Done" Looks Like

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped requirements |
| **BAR(s)** | BAR-52 (data refresh) |
| **Last Updated** | 2026-03-24 |

---

## Purpose

Monthly dumb worker that fills CEO/CFO/HR slots for every company in the territory. Uses LinkedIn head-only checks via residential proxy to detect personnel changes. Without filled slots, nothing downstream works — this is the gateway to the entire pipeline.

---

## Two-Question Intake

1. **"What triggers this?"** — Daily cron at 6am UTC. Runs through the month in batches of 100 profiles per day.
2. **"How do we get it?"** — LinkedIn head-only checks via SearchEngineProxy (Startpage through DataImpulse residential IP). Well drinks first (free tools), top shelf last (Hunter, Apollo).

---

## Requirements

### R1: Territory Seed
- Pull agent-assigned companies from Neon → D1 `companies` table
- Filter by coverage zones (3 agents × anchor_zip × radius_miles)
- **Acceptance:** D1 companies count matches territory view count

### R2: Slot Assignment
- Three slots per company: CEO, CFO, HR
- Priority: CEO → CFO → HR
- Minimum 1 reachable slot before company enters LCS pipeline
- **Acceptance:** Every company has 3 slot records in `slots` table

### R3: LinkedIn Monitoring
- Build monitor list of LinkedIn profile URLs from slots
- Daily batch of 100 profiles via proxy
- 30-120 second random delay between fetches
- **Acceptance:** monitor_list populated, batch_progress tracks daily runs

### R4: Tool Priority
- Well drinks first (MXLookup, SMTPCheck, LinkedInCheck — free via CF fetch)
- House pours second (Composio)
- Top shelf last (Hunter, Apollo, MillionVerifier — only when free tools fail)
- **Acceptance:** source_tool tagged on every data point

### R5: Movement Detection
- Monthly snapshot diff: compare baseline to current
- Binary output per slot: 0 (no change) or 1 (movement)
- Signal types: JOINED, LEFT, REPLACED, TITLE_CHANGED, EMAIL_CHANGED
- Deterministic — zero AI required
- **Acceptance:** Movement signals written for every slot that changed

### R6: Reachability Gate
- UNREACHABLE: No slots filled or no contact method → cannot enter LCS
- EMAIL_ONLY: Verified email → Mailgun path
- LINKEDIN_ONLY: LinkedIn URL → HeyReach path
- FULL: Both channels → best position
- **Acceptance:** Every company has a reachability status

### R7: Push to Vault
- End of month: promote verified results from D1 → Neon
- Also sync to outreach D1 (svg-d1-outreach-ops) for LCS pipeline access
- **Acceptance:** Neon vault updated, outreach D1 people tables current

### R8: Error Handling
- Every failed fetch logged to `errors` table
- Track error rate per batch
- If error rate > 50% → pause and alert
- **Acceptance:** Errors logged with context, batch pauses on high error rate

---

## Non-Requirements

- AI-based name matching (deterministic only)
- Real-time slot updates (monthly cycle is sufficient)
- Direct Neon queries during fetch cycle (D1 workspace only)

---

## Definition of Done

All 8 requirements pass acceptance criteria. Full monthly cycle: SEED → FETCH (28 days) → DETECT movements → PUSH to vault. At least 60% slot fill rate maintained.

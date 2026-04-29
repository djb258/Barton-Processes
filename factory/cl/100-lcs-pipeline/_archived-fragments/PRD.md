> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# PRD — Process 100: LCS Pipeline
## Product Requirements — What It Does, What "Done" Looks Like

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped requirements |
| **Input** | Business need: closed-loop outreach pipeline |
| **Middle** | Define what triggers, what processes, what outputs, what "done" means |
| **Output** | Acceptance criteria — testable, binary |
| **Circle** | If acceptance criteria aren't met, the process isn't certified |
| **BAR(s)** | BAR-152, BAR-131, BAR-132, BAR-37, BAR-48 |
| **Last Updated** | 2026-03-24 |

---

## Purpose

Closed-loop intelligence pipeline: qualify companies through 8 gates, compile intelligence dossier (CID), construct targeted message (SID) from frame registry, deliver via Mailgun or HeyReach (MID), receive webhook feedback, update delivery state, accumulate intelligence. The footprint never shrinks. Each cycle is smarter than the last.

---

## Two-Question Intake

1. **"What triggers this?"** — A signal arrives in `lcs_signal_queue` from a dumb worker spoke (DOL, People, Blog, Talent Flow). The cron job scans for pending signals daily at 7am UTC.

2. **"How do we get it?"** — The compiler reads company data from outreach D1, processes through the 9-gate stack, selects a message frame from the registry, builds the message, and delivers via the appropriate adapter.

---

## Requirements

### R1: Signal Ingestion
- Signals from any worker spoke arrive via `POST /signal` or `POST /signals`
- Each signal has sovereign_company_id, signal_set_hash, and priority
- Signal links to registry definition for validation
- **Acceptance:** Signal appears in lcs_signal_queue with status 'pending'

### R2: CID Compilation
- Compiler reads company data from outreach D1 (CT, DOL, People, BIT)
- Intelligence tier determined by data completeness (tier 2 = high, tier 5 = generic)
- Frame selected from registry based on tier
- 8-gate qualification evaluates each company
- **Acceptance:** CID row written to lcs_cid with compilation_status COMPILED or FAILED

### R3: SID Construction
- Reads CID + frame template from registry
- Gets recipient from people slots (CFO → CEO → HR priority)
- Builds personalized subject line and message body
- **Acceptance:** SID row written to lcs_sid_output with construction_status CONSTRUCTED or FAILED

### R4: MID Delivery
- Reads SID + adapter from registry
- Checks daily cap (adapter_registry.sent_today vs daily_cap)
- Delivers via Mailgun (email) or HeyReach (LinkedIn)
- Passes tracing variables (communication_id, message_run_id) for webhook correlation
- **Acceptance:** MID row written to lcs_mid_sequence_state with delivery_status SENT

### R5: Webhook Processing
- Mailgun webhooks arrive at `/webhook/mailgun`
- HeyReach webhooks arrive at `/webhook/heyreach`
- Extract message_run_id from custom variables
- Update MID delivery_status (DELIVERED, OPENED, CLICKED, BOUNCED)
- **Acceptance:** MID delivery_status updated correctly based on webhook event

### R6: ORBT 3-Strike Protocol
- Strike 1: AUTO_RETRY — same channel
- Strike 2: ALT_CHANNEL — try alternate if eligible
- Strike 3: HUMAN_ESCALATION — system gives up
- Strikes tracked in lcs_err0.orbt_strike_number
- **Acceptance:** Strike count increments correctly. Strike 3 escalates.

### R7: Bidirectional Trace
- Given any communication_id: return CID + all SIDs + all MIDs + all events + all errors
- Given any sovereign_company_id: return all events for that company
- **Acceptance:** `/trace/{id}` returns complete chain in both directions

### R8: Append-Only Event Log
- Every pipeline action writes to lcs_event (the CET)
- Events are append-only — never updated, never deleted
- Event types: CID_COMPILED, CID_FAILED, SID_CONSTRUCTED, SID_FAILED, MID_SENT, MID_DELIVERED, MID_OPENED, MID_CLICKED, MID_BOUNCED, MID_FAILED
- **Acceptance:** lcs_event has a row for every pipeline action

### R9: Config-Driven
- Signal types from lcs_signal_registry (not hardcoded)
- Message frames from lcs_frame_registry (not hardcoded)
- Adapter routing from lcs_adapter_registry (not hardcoded)
- Adding a new signal type, frame, or adapter requires only a registry INSERT — no code change
- **Acceptance:** New registry entry → compiler uses it without redeployment

### R10: Data Isolation
- LCS pipeline reads from outreach D1 but NEVER writes to it
- All writes go to spine D1 only
- Neon is vault — never queried during pipeline operations
- **Acceptance:** Zero write operations to outreach D1 or Neon during pipeline run

---

## Non-Requirements (Out of Scope)

- AI narrative synthesis (BAR-132 — separate, adds Claude API as tail)
- Monte Carlo simulation (BAR-133 — separate, adds probability layer)
- Content library taxonomy (BAR-48 — separate, enriches SID templates)
- Data refresh (BAR-52 — separate, maintains outreach D1 freshness)
- Dashboard rendering (separate — reads lcs_event/lcs_err0)

---

## Definition of Done

All 10 requirements above pass acceptance criteria. Smoke test (BAR-37) executes end-to-end: signal → CID → SID → MID → email in inbox → webhook updates MID status → trace returns full chain.

> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — Process 100: LCS Pipeline

## Governing Doctrine

**Before any work on this process, read and follow:**

1. `law/doctrine/FOUNDATIONAL_BEDROCK.md` — The engine (Three Primitives, C\&V, IMO, CTB, Circle, Troubleshooting Loop, Tier 0, Aviation Model)
2. `bedrock/math-01-engine.md` — P(x;θ) decision equation (FROZEN)
3. `bedrock/math-02-adapter-template.md` — Domain adapter interface

**Pre-flight (every session):**
- Two-Question Intake: "What triggers this?" and "How do we get it?"
- C\&V Test: Can you name it? Format it? → constant. The value filling it → variable.
- Four-Element Validation: IMO + CTB + Circle simultaneously
- Three Primitives: Thing (exists?), Flow (reaches?), Change (transforms correctly?)
- Determinism first. LLM is tail arbitration only.
- If something broke → Troubleshooting Loop (Bedrock §6). Do not patch. Do not guess.

---


## What This Process Does

Three-stage compiler that converts raw signals into delivered messages. CID (Compiled Intelligence Dossier) gathers all company data. SID (Signal Document) constructs the personalized message. MID (Message Delivery Record) sends it and tracks the response. Full circle: webhooks feed delivery status back into the CID, making every cycle smarter than the last.

## How It Works

Signal arrives in queue. Compiler runs CID -> SID -> MID sequentially.

1. **Signal Ingestion:** Dumb worker spokes (200-People, 300-Blog, 400-DOL, 500-Talent) emit signals to `lcs_signal_queue` via `POST /signal` or `POST /signals`. Each signal has `sovereign_company_id`, `signal_set_hash` (links to registry), and `priority`.
2. **CID Compilation:** Reads company data from D1 outreach tables (CT, DOL, People). Determines intelligence tier (2-5) by data completeness. Selects message frame from `lcs_frame_registry`. Evaluates 9-gate qualification stack. Writes `lcs_cid`.
3. **SID Construction:** Reads CID + frame template. Gets recipient from people slots (CFO -> CEO -> HR priority). Builds personalized subject/body. Writes `lcs_sid_output`.
4. **MID Delivery:** Reads SID + picks sending domain from rotation. Checks daily cap. Delivers via Mailgun (email) or HeyReach (LinkedIn). Writes `lcs_mid_sequence_state`.
5. **Webhook Feedback:** Mailgun/HeyReach webhooks arrive at `/webhook/mailgun` and `/webhook/heyreach`. Update MID delivery_status. Bounces trigger ORBT strikes. Strike 3 = human escalation.

## Intelligence Tier System

| Tier | Data Completeness | Frame Selection | Message Quality |
|------|------------------|-----------------|-----------------|
| 2 | DOL + high score + renewal signal | OUT-HAMMER-01 (DOL intro) | High -- references specific financial data |
| 3 | DOL present OR 2+ slots filled | OUT-HAMMER-01 through steps | Medium -- references company context |
| 4 | Basic company data | OUT-HAMMER-01-LITE | Standard template |
| 5 | Minimal data | OUT-GENERAL-V1 | Generic outreach |

## Domain Rotation (14 Mailgun Domains)

The MID stage does NOT use a single Mailgun domain. It rotates across 14 verified sending domains tracked in `lcs_domain_rotation` table in spine D1.

- **Selection:** Round-robin by LRU (`last_sent_at ASC`), filtered by `is_paused = 0` and `sent_today < daily_cap`.
- **From address:** `dave@{domain}` for each send.
- **Daily reset:** Cron at 07:00 UTC resets `sent_today` and `bounce_count_24h` to 0.
- **Tracking:** Each send increments `sent_today` and `total_sent`. Bounces increment `bounce_count_24h`.
- **Warmup:** Each domain has a `warmup_week` field. During warmup, daily caps are conservative (20/domain/day in week 1).

## Config-Driven Architecture

Nothing is hardcoded. Three registry tables control all behavior:

| Registry | What It Controls | Key Columns |
|----------|-----------------|-------------|
| `lcs_signal_registry` | Signal types (9 defined) | signal_set_hash, signal_name, signal_category |
| `lcs_frame_registry` | Message frames (11 defined) | frame_id, frame_name, tier, channel, step_in_sequence |
| `lcs_adapter_registry` | Delivery adapters (3: MG, HR, SH) | adapter_type, channel, daily_cap, sent_today, health_status |

Adding a new signal type, frame, or adapter requires only a registry INSERT -- no code change, no redeployment.

## Databases

**Spine D1 (svg-d1-spine) -- Binding: `D1` -- Read + Write**

| Table | Role | Purpose |
|-------|------|---------|
| `lcs_signal_queue` | Supporting | Ingress from dumb workers |
| `lcs_cid` | Supporting | Compiled Intelligence Dossier |
| `lcs_sid_output` | Supporting | Constructed message document |
| `lcs_mid_sequence_state` | Supporting | Delivery state tracker |
| `lcs_event` | CANONICAL | Append-only audit trail (CET) |
| `lcs_err0` | ERROR | Error drain with ORBT strikes |
| `lcs_signal_registry` | Config | 9 signal type definitions |
| `lcs_frame_registry` | Config | 11 message frame templates |
| `lcs_adapter_registry` | Config | 3 delivery adapter configs |
| `lcs_domain_rotation` | Config | 14 Mailgun sending domain states |

**Outreach D1 (svg-d1-outreach-ops) -- Binding: `D1_OUTREACH` -- Read Only**

| Table | Purpose | Join Key |
|-------|---------|----------|
| `outreach_company_target` | 32K+ territory companies | sovereign_company_id = company_unique_id |
| `outreach_dol` | DOL summary records | outreach_id |
| `people_company_slot` | CEO/CFO/HR slots per company | outreach_id |
| `people_people_master` | Contact details (email, LinkedIn) | person_unique_id |

**Neon vault:** Source for SEED, destination for PUSH. NEVER queried during pipeline operations.

## ID Format

| ID | Format | Example | Minted By |
|----|--------|---------|-----------|
| communication_id | `LCS-{PHASE}-{DATE}-{ULID}` | `LCS-OUTREACH-20260324-a1b2c3d4e5f6` | compileCid() |
| message_run_id | `RUN-{COMM_ID}-{CHANNEL}-{ATTEMPT}` | `RUN-LCS-OUTREACH-20260324-a1b2-MG-01` | deliverMid() |
| sid_id | `SID-{COMM_ID}` | `SID-LCS-OUTREACH-20260324-a1b2c3d4e5f6` | constructSid() |
| error_id | `ERR-{ULID}` | `ERR-a1b2c3d4e5f6` | logErr0() |

**Bidirectional trace:** `/trace/{id}` returns the full chain given any ID.

## Key Joins

- Territory filter: `outreach_company_target.company_unique_id` = `lcs_cid.sovereign_company_id`
- People slots: `people_company_slot.outreach_id` -> `people_people_master.person_unique_id`
- Slot priority: CFO -> CEO -> HR (first filled slot with reachable contact wins)
- Signal to registry: `lcs_signal_queue.signal_set_hash` -> `lcs_signal_registry.signal_set_hash`
- CID to frame: `lcs_cid.frame_id` -> `lcs_frame_registry.frame_id`
- MID to adapter: `lcs_mid_sequence_state.adapter_type` -> `lcs_adapter_registry.adapter_type`
- Full chain: `signal_queue` -> `lcs_cid` (via signal_queue_id) -> `lcs_sid_output` (via communication_id) -> `lcs_mid_sequence_state` (via communication_id)

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check -- signal/CID/company counts |
| GET | `/status` | Pipeline stats by status across all stages + domain rotation |
| POST | `/signal` | Ingest single signal |
| POST | `/signals` | Ingest batch signals |
| GET | `/company/{id}` | Company detail -- all CIDs, SIDs, MIDs, events, errors |
| GET | `/trace/{id}` | Bidirectional ID lookup |
| POST | `/webhook/mailgun` | Mailgun delivery webhook receiver |
| POST | `/webhook/heyreach` | HeyReach delivery webhook receiver |
| POST | `/run` | Manual pipeline trigger -- bypasses queue for smoke test |

## ORBT 3-Strike Protocol

| Strike | Action | Description |
|--------|--------|-------------|
| 1 | AUTO_RETRY | Same channel, automatic retry |
| 2 | ALT_CHANNEL | Try alternate delivery channel if eligible |
| 3 | HUMAN_ESCALATION | Route to human -- system gives up |

Strikes tracked in `lcs_err0.orbt_strike_number`. Strike 3 logged to `lcs_event`.

## Worker Config

- **URL:** https://lcs-hub.svg-outreach.workers.dev
- **Cron:** `0 7 * * *` (daily 7am UTC -- scan for pending signals + reset domain counters)
- **Queue:** `lcs-pipeline` (producer + consumer), `lcs-dlq` (dead letter)
- **Batch:** max_batch_size=5, max_retries=3, max_batch_timeout=60
- **Secrets:** MAILGUN_API_KEY, HEYREACH_API_KEY, SVG_BRAIN_API_KEY, IMO_BRAIN_API_KEY, COMPOSIO_API_KEY, NEON_URL (all in Doppler)

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | 200 People Worker | Fills CEO/CFO/HR slots -- without people, SID cannot build |
| Upstream | 300 Blog Worker | Emits content movement signals |
| Upstream | 400 DOL Views | DOL filing data for intelligence tier and renewal signals |
| Upstream | 500 Talent Flow | Executive movement signals |
| Downstream | Dashboard | Reads lcs_event + lcs_err0 for pipeline stats |
| Downstream | Neon vault | Batch PUSH of delivery results |

## Files

```
factory/100-lcs-pipeline/
+-- heir.yaml           # Identity (HEIR)
+-- MANIFEST.md         # Full process manual
+-- OSAM.md             # Semantic access map -- WHERE to query
+-- ERD.md              # Entity relationships -- tables, columns, FK chain
+-- PRD.md              # Product requirements -- acceptance criteria
+-- CLAUDE.md           # This file -- agent operating instructions
+-- package.json
+-- wrangler.toml       # CF Worker config (D1 bindings, queue, cron, secrets)
+-- src/
    +-- index.ts        # Entry point -- cron, queue consumer, HTTP API
    +-- compiler-v2.ts  # The compiler -- CID -> SID -> MID (blueprint-native)
    +-- compiler.ts     # v1 (deprecated)
    +-- gates.ts        # 9-gate qualification stack
    +-- types.ts        # Type definitions
    +-- utils.ts        # v1 utilities (deprecated)
    +-- spokes/
    |   +-- delivery.ts     # v1 adapters (deprecated)
    |   +-- signal-intake.ts
    +-- migrations/
        +-- 001_lcs_tables.sql
```

**Source of truth for compiler logic:** `/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub/src/compiler-v2.ts`

## Known Issues

| Issue | Resolution |
|-------|------------|
| fetchCompanyData() was querying Neon directly | Fixed -- reads from D1. Neon is vault only. |
| max_batch_timeout exceeded CF limit (300 > 60) | Fixed -- set to 60 |
| Compiler v1 created duplicate D1 tables | Fixed -- v2 reads existing spine/outreach D1 |
| Hyperdrive binding in wrangler.toml | Removed -- Neon is vault only during ops |
| BIT scoring references | BIT scoring retired 2026-03-25 -- do not reference `outreach_bit_scores` |
| Mailgun webhook URL not yet configured | TODO -- point Mailgun dashboard to /webhook/mailgun |
| HeyReach webhook URL not yet configured | TODO -- point HeyReach to /webhook/heyreach |
| Daily adapter sent_today reset | Handled by cron at 07:00 UTC via domain_rotation table |

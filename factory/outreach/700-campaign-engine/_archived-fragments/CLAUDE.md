> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — Process 700: Campaign Engine

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

Sequences outreach messages (MIDs) based on movement detection from People Worker (200). No movement = 1 touch monthly (stay visible). Movement detected = 3-5 touches over 2 weeks (get the meeting). This is the terminal execution layer of the LCS pipeline — it delivers the actual messages to prospects.

## How It Works

Runs after LCS pipeline (100) compiles CIDs (Campaign Instruction Documents). The campaign engine reads CID targets, determines which campaign model to apply, tags each MID, and routes to the appropriate delivery channel.

1. **Receive CID targets** from LCS pipeline (100) — companies with assigned SIDs + movement signals.
2. **Evaluate movement status** per company — binary: movement (1) or no movement (0).
3. **Select campaign model:**
   - No movement → 1 generic introduction per month (stay visible)
   - Movement detected → 3-5 movement-specific touches over ~2 weeks (get the meeting)
4. **Tag each MID** with path_type + channel + movement_signal + sequence_position.
5. **Route to delivery channel** via Composio → Mailgun (email) or HeyReach (LinkedIn).

## Campaign Models

| Model | Touches | Cadence | Frame | Goal |
|-------|---------|---------|-------|------|
| No Movement | 1 | Monthly | Generic introduction | Stay visible |
| Movement Detected | 3-5 | Every 2-3 days over ~2 weeks | Movement-specific (based on signal type) | Get the meeting |

## MID Tagging

Every outreach message is tagged with:

- **path_type:** WARM or COLD (for A/B tracking)
- **channel:** MG (Mailgun) or HR (HeyReach)
- **movement_signal:** Which signal triggered this campaign (JOINED, LEFT, REPLACED, TITLE_CHANGED, EMAIL_CHANGED)
- **sequence_position:** 1 of 5, 2 of 5, etc.

## Tools

| Tier | Tool | Cost | When |
|------|------|------|------|
| Snap-On | Composio (TOOL-007) | Cheap | Routes MIDs to Mailgun/HeyReach |

## Databases

**Neon vault** (via Hyperdrive):
- Read: CID targets, movement signals, company + people data
- Write: Campaign delivery status

**D1 workspace** (working tables):
- Campaign queue, MID tracking, delivery status
- Error table for failed deliveries

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | 100 LCS Pipeline | CID targets — which companies to campaign |
| Upstream | 200 People Worker | Movement signals (0/1 per slot) |
| Downstream | None | Terminal — delivers MIDs. Webhooks feed back to 100. |

## Worker Config

- **Runtime:** Cloudflare Workers
- **Trigger:** After LCS pipeline compiles CIDs
- **Secrets:** Doppler (Composio API keys, Mailgun credentials, HeyReach credentials)

## Key Joins

- CID targets: `lcs.campaign_instruction.sovereign_id` → `outreach.company_target.company_unique_id`
- People slots: `people.company_slot.outreach_id` → movement signal lookup
- Delivery routing: MID channel tag → Composio route → Mailgun API or HeyReach API

## Acceptance Criteria

- Tags every MID with path_type + channel + movement_signal
- Sequences movement campaigns over 2 weeks
- Monthly generic for non-movement companies
- CTA link in every MID (schedule a meeting)
- Errors write to master error table (D1)

## Known Issues

| Issue | Resolution |
|-------|------------|
| Status: BUILD — no source code yet | `src/` directory exists but is empty. Heir.yaml defines the contract. |
| Campaign content templates not defined | Need content library per movement signal type |
| Webhook feedback loop from delivery to LCS not built | Composio webhook → 100 pipeline status update |

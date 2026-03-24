# PROCESS-100: LCS Pipeline
# Status: DEPLOYED (OPR)
# Last Updated: 2026-03-24

---

## IDENTITY (HEIR)

| Field | Value |
|-------|-------|
| Process ID | PROC-LCS |
| Number | 100 |
| Name | LCS Pipeline |
| Blueprint | company-lifecycle-cl (SUBHUB-CL-LCS) |
| Runtime | Cloudflare Workers (cron + HTTP + queue consumer) |
| Deployed URL | https://lcs-hub.svg-outreach.workers.dev |
| Cron | `0 7 * * *` (daily 7am UTC — scan for pending signals) |
| Queue | lcs-pipeline (consumer + producer) + lcs-dlq (dead letter) |
| Version | v2 (compiler-v2.ts — blueprint-native) |
| ORBT | OPR |
| Strikes | 0 |

---

## IMO

**Input:** Signals arrive in `lcs_signal_queue` from dumb worker spokes (DOL, People, Blog, Talent Flow). Each signal has a `sovereign_company_id`, `signal_set_hash` (links to registry definition), and `priority`.

**Middle:** Three-stage compiler runs on each signal:
1. **CID Compilation** — Reads company data from outreach D1 (CT, DOL, People, BIT). Determines intelligence tier (2-5). Selects message frame from registry. Writes `lcs_cid`.
2. **SID Construction** — Reads CID + frame template. Gets recipient from people slots (CFO → CEO → HR priority). Builds personalized message. Writes `lcs_sid_output`.
3. **MID Delivery** — Reads SID + adapter from registry. Checks daily cap. Delivers via Mailgun (email) or HeyReach (LinkedIn). Writes `lcs_mid_sequence_state`.

**Output:** Email or LinkedIn message delivered to target recipient. Delivery status tracked. Webhook updates MID state on response (delivered/opened/clicked/bounced).

**Circle:** Webhook responses feed back → update MID state → bounces trigger ORBT strikes → strike 3 = human escalation. Delivery results accumulate on D1 → eventually PUSH to Neon vault in batch.

---

## DATABASES

### Spine D1 (svg-d1-spine) — Binding: `D1`

| Table | Role | Key Columns |
|-------|------|-------------|
| `lcs_signal_queue` | Supporting | id, sovereign_company_id, signal_set_hash, status, priority |
| `lcs_cid` | Supporting | communication_id, sovereign_company_id, entity_id, frame_id, intelligence_tier, compilation_status |
| `lcs_sid_output` | Supporting | sid_id, communication_id, subject_line, body_plain, recipient_email, construction_status |
| `lcs_mid_sequence_state` | Supporting | mid_id, message_run_id, communication_id, delivery_status, gate_verdict |
| `lcs_event` | CANONICAL | communication_id, message_run_id, event_type, delivery_status — append-only CET |
| `lcs_err0` | ERROR | error_id, failure_type, orbt_strike_number, orbt_action_taken |
| `lcs_signal_registry` | Config | signal_set_hash, signal_name, signal_category — 9 signal types defined |
| `lcs_frame_registry` | Config | frame_id, frame_name, tier, channel, step_in_sequence — 11 frames defined |
| `lcs_adapter_registry` | Config | adapter_type, channel, daily_cap, sent_today, health_status — 3 adapters (MG/HR/SH) |

### Outreach D1 (svg-d1-outreach-ops) — Binding: `D1_OUTREACH`

| Table | Role | Key Columns | Join Key |
|-------|------|-------------|----------|
| `outreach_company_target` | Read | company_unique_id, outreach_id, state, employees, agent_name | sovereign_company_id = company_unique_id |
| `outreach_dol` | Read | outreach_id, ein, filing_present, renewal_month, carrier | outreach_id |
| `people_company_slot` | Read | outreach_id, slot_type, is_filled, person_unique_id | outreach_id |
| `people_people_master` | Read | person_unique_id, email, first_name, last_name, linkedin_url | person_unique_id |
| `outreach_bit_scores` | Read | outreach_id, score, score_tier | outreach_id |

### Data Flow

```
OUTREACH D1 (read-only)          SPINE D1 (read-write)
┌─────────────────────┐          ┌──────────────────────────┐
│ company_target       │──read──→│ lcs_signal_queue          │
│ outreach_dol         │          │ lcs_cid                  │
│ people_company_slot  │          │ lcs_sid_output           │
│ people_people_master │          │ lcs_mid_sequence_state   │
│ outreach_bit_scores  │          │ lcs_event (CANONICAL)    │
└─────────────────────┘          │ lcs_err0 (ERROR)         │
                                  └──────────────────────────┘
                                            │
                                            ▼
                                  Mailgun / HeyReach (delivery)
                                            │
                                            ▼
                                  Webhook → D1 (status update)
```

---

## ID FORMAT

| ID | Format | Example | Minted By |
|----|--------|---------|-----------|
| communication_id | `LCS-{PHASE}-{DATE}-{ULID}` | `LCS-OUTREACH-20260324-a1b2c3d4e5f6` | compileCid() |
| message_run_id | `RUN-{COMM_ID}-{CHANNEL}-{ATTEMPT}` | `RUN-LCS-OUTREACH-20260324-a1b2-MG-01` | deliverMid() |
| sid_id | `SID-{COMM_ID}` | `SID-LCS-OUTREACH-20260324-a1b2c3d4e5f6` | constructSid() |
| error_id | `ERR-{ULID}` | `ERR-a1b2c3d4e5f6` | logErr0() |

**Bidirectional trace:** Given any ID, `/trace/{id}` returns the full chain. `LCS-` prefix returns CID + all SIDs + all MIDs + all events + all errors.

---

## DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Outreach D1 seeded | 32,704 companies in outreach_company_target | DONE |
| DOL data | 27,464 DOL records | DONE |
| People data | 43,203 slots, 20,487 contacts | DONE |
| BIT scores | Scoring operational | DONE |
| Signal registry | 9 signal types defined | DONE |
| Frame registry | 11 message frames defined | DONE |
| Adapter registry | 3 adapters (MG/HR/SH) | DONE |
| Secrets | MAILGUN_API_KEY, HEYREACH_API_KEY, SVG_BRAIN_API_KEY, IMO_BRAIN_API_KEY, COMPOSIO_API_KEY, NEON_URL | SET |

### Downstream (consumes this process's output)

| Consumer | What |
|----------|------|
| Dashboard | Reads lcs_event + lcs_err0 for pipeline stats |
| BAR-132 | AI synthesis reads CID for narrative generation |
| BAR-133 | Monte Carlo reads CID + delivery results for probability simulation |
| PUSH to Neon | Batch promotes delivery results to vault |

---

## ENDPOINTS

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check — signal/CID/company counts |
| GET | `/status` | Pipeline stats by status across all stages |
| POST | `/signal` | Ingest single signal |
| POST | `/signals` | Ingest batch signals |
| GET | `/company/{id}` | Company detail — all CIDs, SIDs, MIDs, events, errors |
| GET | `/trace/{id}` | Bidirectional ID lookup |
| POST | `/webhook/mailgun` | Mailgun delivery webhook receiver |
| POST | `/webhook/heyreach` | HeyReach delivery webhook receiver |
| POST | `/run` | Manual pipeline trigger — bypasses queue for smoke test |

---

## INTELLIGENCE TIER SYSTEM

| Tier | Data Completeness | Frame Selection | Message Quality |
|------|------------------|-----------------|-----------------|
| 2 | DOL + BIT > 80 + renewal signal | OUT-HAMMER-01 (DOL intro) | High — references specific financial data |
| 3 | DOL present OR BIT > 60 OR 2+ slots | OUT-HAMMER-01 through steps | Medium — references company context |
| 4 | Basic company data | OUT-HAMMER-01-LITE | Standard template |
| 5 | Minimal data | OUT-GENERAL-V1 | Generic outreach |

---

## ORBT 3-STRIKE PROTOCOL

| Strike | Action | Description |
|--------|--------|-------------|
| 1 | AUTO_RETRY | Same channel, automatic retry |
| 2 | ALT_CHANNEL | Try alternate delivery channel if eligible |
| 3 | HUMAN_ESCALATION | Route to human — system gives up |

Strikes tracked in `lcs_err0.orbt_strike_number`. Strike 3 logged as event type in `lcs_event`.

---

## CURRENT STATE (as of 2026-03-24)

| Metric | Value |
|--------|-------|
| Companies in outreach D1 | 32,704 |
| Signals in queue | 3 (pending) |
| CIDs compiled | 2 |
| Adapters healthy | 3/3 (MG, HR, SH) |
| Mailgun daily cap | 1,500 |
| HeyReach daily cap | 100 |
| Last deployment | 2026-03-24 (v2 — compiler-v2.ts) |
| Process extracted to | Barton-Processes/factory/100-lcs-pipeline/ |

---

## KNOWN ISSUES

| Date | Issue | Resolution |
|------|-------|------------|
| 2026-03-23 | fetchCompanyData() was querying Neon directly | Fixed — reads from D1 company table. Neon is vault only. |
| 2026-03-23 | max_batch_timeout exceeded CF limit (300 > 60) | Fixed — set to 60 |
| 2026-03-24 | Compiler v1 created duplicate D1 tables | Fixed — v2 reads existing spine/outreach D1 databases |
| 2026-03-24 | Hyperdrive binding in wrangler.toml | Removed — Neon is vault only, never queried during ops |

---

## SMOKE TEST

1. **Verify health:** `GET https://lcs-hub.svg-outreach.workers.dev/health` → should show companies > 0
2. **Check signals:** `GET /status` → check for pending signals in queue
3. **Pick a signal:** Use an existing pending signal ID from spine D1, or insert one via `POST /signal`
4. **Run pipeline:** `POST /run` with `{"signal_queue_id": "{id}"}` — runs CID → SID → MID directly
5. **Verify CID:** Response should show `communication_id` with status COMPILED
6. **Verify SID:** Response should show `sid_id` with construction_status CONSTRUCTED
7. **Verify MID:** Response should show delivery status SENT or FAILED
8. **Check email:** If SENT via MG, email should arrive at recipient's inbox
9. **Trace:** `GET /trace/{communication_id}` — should show full chain (CID + SID + MID + events)
10. **Check errors:** If anything failed, check `GET /status` for error counts

---

## NEXT STEPS

| What | BAR | Status |
|------|-----|--------|
| Execute smoke test with real company | BAR-37 | Ready — execute |
| Wire Claude API for tier 1-2 narrative | BAR-132 | In Progress — deterministic path works |
| Wire Monte Carlo probability per company | BAR-133 | TODO — layer0-engine exists |
| Classify 600pg content library for SID templates | BAR-48 | TODO — content in svg-brain |
| Set up Mailgun webhook URL in Mailgun dashboard | — | TODO — point to /webhook/mailgun |
| Set up HeyReach webhook URL | — | TODO — point to /webhook/heyreach |
| Build PUSH script (D1 → Neon batch) | — | TODO — scheduled promote |
| Reset adapter sent_today count daily | — | TODO — cron or at start of daily run |

---

## FILES

```
Barton-Processes/factory/100-lcs-pipeline/
├── heir.yaml           # Identity (HEIR)
├── MANIFEST.md         # This file — the process manual
├── package.json        # Dependencies
├── wrangler.toml       # CF Worker config (D1 bindings, queue, cron, secrets)
└── src/
    ├── index.ts        # Entry point — cron producer, queue consumer, HTTP API
    ├── compiler-v2.ts  # The compiler — CID → SID → MID (blueprint-native)
    ├── compiler.ts     # v1 (deprecated — kept for reference)
    ├── gates.ts        # 9-gate qualification stack
    ├── types.ts        # Type definitions (Env, Signal, CID, SID, MID, etc.)
    ├── utils.ts        # v1 utilities (deprecated)
    ├── spokes/
    │   ├── delivery.ts     # v1 Mailgun + HeyReach adapters (deprecated)
    │   └── signal-intake.ts # Signal ingestion
    └── migrations/
        └── 001_lcs_tables.sql  # D1 schema (reference — tables live in spine)
```

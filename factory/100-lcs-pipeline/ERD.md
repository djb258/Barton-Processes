# ERD — Process 100: LCS Pipeline
## Entity Relationship Diagram — Tables, Columns, FK Chain

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped entity relationships |
| **Input** | The LCS pipeline needs to know how tables connect |
| **Middle** | Map every entity, every column, every foreign key |
| **Output** | Complete relationship map — no blind joins |
| **Circle** | If a JOIN fails, the ERD is wrong — update it |
| **Blueprint ERD** | company-lifecycle-cl → LCS sub-hub schema contracts in `src/sys/lcs/contracts/` |
| **Last Updated** | 2026-03-24 |

---

## Entity Relationship Diagram

```
OUTREACH D1 (svg-d1-outreach-ops) — READ ONLY
═══════════════════════════════════════════════

outreach_company_target            outreach_dol
┌─────────────────────┐            ┌──────────────────┐
│ company_unique_id PK│──(1:1)───→│ outreach_id FK    │
│ outreach_id    UK   │            │ dol_id PK         │
│ canonical_name      │            │ ein               │
│ state               │            │ filing_present    │
│ postal_code         │            │ funding_type      │
│ employees           │            │ renewal_month     │
│ agent_name          │            │ carrier           │
│ agent_number        │            │ broker_or_advisor │
│ email_method        │            └──────────────────┘
│ outreach_status     │
└────────┬────────────┘            outreach_bit_scores
         │                         ┌──────────────────┐
         │──(1:1)────────────────→│ outreach_id FK    │
         │                         │ score             │
         │                         │ score_tier        │
         │                         │ signal_count      │
         │                         └──────────────────┘
         │
         │  people_company_slot         people_people_master
         │  ┌───────────────────┐       ┌───────────────────┐
         └─→│ outreach_id FK    │       │ person_unique_id PK│
            │ slot_id PK        │──────→│ first_name         │
            │ slot_type         │       │ last_name          │
            │ person_unique_id FK│      │ email              │
            │ is_filled         │       │ linkedin_url       │
            │ confidence_score  │       └───────────────────┘
            └───────────────────┘


SPINE D1 (svg-d1-spine) — READ + WRITE
═══════════════════════════════════════

lcs_signal_registry (CONFIG)        lcs_frame_registry (CONFIG)
┌─────────────────────┐             ┌──────────────────────┐
│ signal_set_hash PK  │             │ frame_id PK          │
│ signal_name         │             │ frame_name           │
│ lifecycle_phase     │             │ lifecycle_phase      │
│ signal_category     │             │ tier                 │
│ is_active           │             │ channel              │
└─────────┬───────────┘             │ step_in_sequence     │
          │                         │ cid_compilation_rule │
          │                         │ sid_template_id      │
          │                         │ mid_sequence_type    │
          │                         │ mid_delay_hours      │
          │                         │ mid_max_attempts     │
          │                         │ is_active            │
          │                         └──────────┬───────────┘
          │                                    │
          ▼                                    ▼
lcs_signal_queue                    lcs_cid
┌─────────────────────┐             ┌──────────────────────┐
│ id PK               │            │ communication_id PK  │
│ signal_set_hash FK──│────────────│ sovereign_company_id │
│ sovereign_company_id│            │ entity_id            │
│ lifecycle_phase     │            │ signal_set_hash FK───│──→ signal_registry
│ source_hub          │            │ signal_queue_id FK───│──→ signal_queue
│ status              │            │ frame_id FK──────────│──→ frame_registry
│ priority            │            │ lifecycle_phase      │
│ created_at          │            │ lane                 │
│ processed_at        │            │ agent_number         │
└─────────────────────┘            │ intelligence_tier    │
                                    │ compilation_status   │
                                    │ compilation_reason   │
                                    └──────────┬───────────┘
                                               │
                          ┌────────────────────┤
                          │                    │
                          ▼                    ▼
lcs_sid_output                      lcs_mid_sequence_state
┌─────────────────────┐             ┌──────────────────────┐
│ sid_id PK           │             │ mid_id PK            │
│ communication_id FK─│─────────────│ message_run_id       │
│ frame_id FK         │             │ communication_id FK  │
│ subject_line        │             │ adapter_type FK──────│──→ adapter_registry
│ body_plain          │             │ channel              │
│ body_html           │             │ sequence_position    │
│ sender_identity     │             │ attempt_number       │
│ sender_email        │             │ gate_verdict         │
│ recipient_email     │             │ gate_reason          │
│ recipient_name      │             │ delivery_status      │
│ construction_status │             │ scheduled_at         │
│ construction_reason │             │ attempted_at         │
└─────────────────────┘             └──────────────────────┘

                                    lcs_adapter_registry (CONFIG)
                                    ┌──────────────────────┐
                                    │ adapter_type PK      │
                                    │ adapter_name         │
                                    │ channel              │
                                    │ daily_cap            │
                                    │ sent_today           │
                                    │ health_status        │
                                    │ bounce_rate_24h      │
                                    │ is_active            │
                                    └──────────────────────┘

lcs_event (CANONICAL — append-only CET)
┌────────────────────────────────────┐
│ communication_id FK                │
│ message_run_id                     │
│ sovereign_company_id               │
│ entity_type, entity_id             │
│ signal_set_hash FK                 │
│ frame_id FK                        │
│ adapter_type FK                    │
│ channel                            │
│ delivery_status                    │
│ lifecycle_phase                    │
│ event_type                         │
│ lane                               │
│ agent_number                       │
│ step_number, step_name             │
│ intelligence_tier                  │
│ created_at                         │
└────────────────────────────────────┘

lcs_err0 (ERROR — the drain)
┌────────────────────────────────────┐
│ error_id PK                        │
│ message_run_id                     │
│ communication_id FK                │
│ sovereign_company_id               │
│ failure_type                       │
│ failure_message                    │
│ lifecycle_phase                    │
│ adapter_type FK                    │
│ orbt_strike_number                 │
│ orbt_action_taken                  │
│ created_at                         │
└────────────────────────────────────┘
```

---

## FK Chain (Bidirectional Trace)

```
Forward:  signal_queue → lcs_cid → lcs_sid_output → lcs_mid_sequence_state
          (signal_queue_id)  (communication_id)  (communication_id)

Reverse:  lcs_mid_sequence_state → lcs_sid_output → lcs_cid → signal_queue
          (communication_id)      (communication_id) (signal_queue_id)

Cross-DB: lcs_cid.sovereign_company_id → outreach_company_target.company_unique_id
          lcs_cid.entity_id → outreach_company_target.outreach_id
```

---

## CQRS Compliance

| Sub-Hub | CANONICAL | ERROR | Supporting |
|---------|-----------|-------|-----------|
| LCS | lcs_event | lcs_err0 | lcs_signal_queue, lcs_cid, lcs_sid_output, lcs_mid_sequence_state |
| LCS Config | — | — | lcs_signal_registry, lcs_frame_registry, lcs_adapter_registry |

Data enters from leaves (signal_queue). Promotes through gates (CID → SID → MID). Events append to CANONICAL (lcs_event). Failures drain to ERROR (lcs_err0). No direct writes to CANONICAL except append.

---

## Column Details

### Status Values

| Table | Column | Values |
|-------|--------|--------|
| lcs_signal_queue | status | pending, processed, failed |
| lcs_cid | compilation_status | COMPILED, FAILED, BLOCKED |
| lcs_sid_output | construction_status | CONSTRUCTED, FAILED |
| lcs_mid_sequence_state | delivery_status | SCHEDULED, SENT, DELIVERED, OPENED, CLICKED, BOUNCED, FAILED |
| lcs_mid_sequence_state | gate_verdict | PASS, FAIL, THROTTLED |
| lcs_adapter_registry | health_status | HEALTHY, DEGRADED, DOWN |

### ORBT Strike Values

| Column | Values |
|--------|--------|
| orbt_strike_number | 1, 2, 3+ |
| orbt_action_taken | AUTO_RETRY, ALT_CHANNEL, HUMAN_ESCALATION |

# ERD — Process 200: People Worker
## Entity Relationship Diagram — Tables, Columns, FK Chain

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped entity relationships |
| **Blueprint ERD** | barton-outreach-core → People Intelligence sub-hub |
| **Last Updated** | 2026-03-24 |

---

## Entity Relationship Diagram

```
D1 (people-worker-200)
═══════════════════════

companies (territory — seeded from Neon)
┌──────────────────────────┐
│ company_unique_id PK     │
│ outreach_id UK           │──────────────────────┐
│ canonical_name           │                      │
│ agent_name               │                      │
│ agent_number             │                      │
│ state                    │                      │
│ postal_code              │                      │
│ industry                 │                      │
│ employees                │                      │
│ company_domain           │                      │
│ sovereign_company_id     │                      │
│ seeded_at                │                      │
└──────────────────────────┘                      │
                                                   │
slots (CEO/CFO/HR per company)                    │
┌──────────────────────────┐                      │
│ outreach_id FK───────────│──────────────────────┘
│ slot_type                │  (CEO, CFO, HR)
│ person_unique_id FK──────│──┐
│ is_filled                │  │
│ confidence_score         │  │
└──────────────────────────┘  │
                               │
people (contact details)       │
┌──────────────────────────┐  │
│ person_unique_id PK──────│──┘
│ email                    │
│ linkedin_url             │
│ first_name               │
│ last_name                │
│ title                    │
└──────────────────────────┘

monitor_list (LinkedIn profiles to check)
┌──────────────────────────┐
│ outreach_id FK           │
│ linkedin_url             │
│ status                   │  (pending, fetched, failed, skipped)
│ last_checked_at          │
└──────────────────────────┘

baseline (previous month snapshot)
┌──────────────────────────┐
│ outreach_id FK           │
│ slot_type                │
│ person_unique_id         │
│ snapshot_date            │
└──────────────────────────┘

snapshots (current month results)
┌──────────────────────────┐
│ outreach_id FK           │
│ slot_type                │
│ person_unique_id         │
│ fetched_at               │
│ raw_data                 │
└──────────────────────────┘

dol (DOL filing snapshot — read only)
┌──────────────────────────┐
│ outreach_id FK           │
│ ein                      │
│ filing_present           │
│ renewal_month            │
└──────────────────────────┘

bit_scores (composite — read only)
┌──────────────────────────┐
│ outreach_id FK           │
│ score                    │
│ score_tier               │
└──────────────────────────┘

batch_progress (tracking)
┌──────────────────────────┐
│ batch_id                 │
│ processed_count          │
│ total_count              │
│ started_at               │
└──────────────────────────┘

errors (drain)
┌──────────────────────────┐
│ outreach_id              │
│ error_type               │
│ error_message            │
│ created_at               │
└──────────────────────────┘
```

---

## FK Chain

```
companies.outreach_id → slots.outreach_id → people.person_unique_id
companies.outreach_id → monitor_list.outreach_id
companies.outreach_id → dol.outreach_id
companies.outreach_id → bit_scores.outreach_id
companies.outreach_id → baseline.outreach_id
companies.outreach_id → snapshots.outreach_id
```

---

## Movement Detection (Snapshot Diff)

```
baseline (month N-1)     snapshots (month N)
┌──────────────┐         ┌──────────────┐
│ slot: CEO    │         │ slot: CEO    │
│ person: A    │ ──diff──│ person: B    │ → REPLACED (signal)
│              │         │              │
│ slot: CFO    │         │ slot: CFO    │
│ person: C    │ ──diff──│ person: C    │ → NO CHANGE (0)
│              │         │              │
│ slot: HR     │         │ slot: HR     │
│ person: null │ ──diff──│ person: D    │ → JOINED (signal)
└──────────────┘         └──────────────┘
```

Output: Binary per slot (0 = no change, 1 = movement). Signal type: JOINED, LEFT, REPLACED, TITLE_CHANGED, EMAIL_CHANGED.

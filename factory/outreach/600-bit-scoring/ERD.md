# ERD — Process 600: BIT Scoring
## Entity Relationship Diagram — Tables, Columns, FK Chain

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped entity relationships |
| **Blueprint ERD** | barton-outreach-core → BIT sub-hub |
| **Last Updated** | 2026-03-24 |

---

## Entity Relationship Diagram

```
OUTREACH D1 (svg-d1-outreach-ops)
══════════════════════════════════

outreach_company_target (spine — read only)
┌──────────────────────────┐
│ outreach_id PK           │────────────────────────────┐
│ company_unique_id        │                            │
│ state                    │                            │
│ employees                │                            │
│ industry                 │                            │
└──────────────────────────┘                            │
                                                         │
        ┌─────────────────┬──────────────────┐          │
        │                 │                  │          │
        ▼                 ▼                  ▼          │
outreach_dol         people_company_slot  outreach_blog  │
┌────────────────┐   ┌────────────────┐  ┌────────────┐│
│ outreach_id FK │   │ outreach_id FK │  │outreach_id ││
│ filing_present │   │ slot_type      │  │signal_type  ││
│ renewal_month  │   │ is_filled      │  │created_at   ││
│ carrier        │   │ person_uid FK  │  └────────────┘│
│ broker         │   └────────────────┘                 │
└────────────────┘                                      │
        │                 │                  │          │
        │   SIGNALS       │   SIGNALS        │ SIGNALS  │
        ▼                 ▼                  ▼          │
┌──────────────────────────────────────────────────────┐│
│              BIT SCORING ENGINE                       ││
│  SUM(weighted signals per category)                  ││
│  → Structural Pressure (DOL)                         ││
│  → Decision Surface (People)                         ││
│  → Narrative Volatility (Blog)                       ││
│  = Composite Score → Band (0-5)                      ││
└──────────────────────────────────────────────────────┘│
        │                                               │
        ▼                                               │
outreach_bit_scores (CANONICAL — write)                 │
┌──────────────────────────┐                            │
│ outreach_id FK───────────│────────────────────────────┘
│ score                    │
│ score_tier               │  (SILENT/WATCH/EXPLORATORY/
│ signal_count             │   TARGETED/ENGAGED/DIRECT)
│ people_score             │
│ dol_score                │
│ blog_score               │
│ talent_flow_score        │
│ last_signal_at           │
│ last_scored_at           │
│ created_at               │
│ updated_at               │
└──────────────────────────┘
```

---

## FK Chain

```
outreach_company_target.outreach_id
  → outreach_dol.outreach_id (DOL signals)
  → people_company_slot.outreach_id (People signals)
  → outreach_blog.outreach_id (Blog signals)
  → outreach_bit_scores.outreach_id (composite output)
```

All joins on `outreach_id`. Single key. No cross-database joins.

---

## Band Classification

| Band | Score Range | Name | Tier |
|------|------------|------|------|
| 0 | 0-9 | SILENT | 5 |
| 1 | 10-24 | WATCH | 5 |
| 2 | 25-39 | EXPLORATORY | 4 |
| 3 | 40-59 | TARGETED | 3 |
| 4 | 60-79 | ENGAGED | 3 |
| 5 | 80+ | DIRECT | 2 |

Band maps to intelligence tier in the LCS compiler — higher band = lower tier number = more personalized outreach.

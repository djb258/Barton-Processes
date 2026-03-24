# OSAM — Process 600: BIT Scoring
## Semantic Access Map — WHERE to Query, HOW to Join

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped access map |
| **Blueprint OSAM** | barton-outreach-core → `docs/OSAM.md` |
| **Last Updated** | 2026-03-24 |

---

## Rule

**BEFORE RUNNING ANY DATA QUERY, READ THIS FILE.**

---

## Database

BIT Scoring reads from the outreach D1 (svg-d1-outreach-ops). It is pure computation — reads signals from all sub-hubs, aggregates into a composite score, writes back to the same database.

| Database | ID | Purpose | Access |
|----------|----|---------|--------|
| svg-d1-outreach-ops | `73a285b8-770a-4370-abbe-ce9607be0b34` | Outreach sub-hubs | Read + Write |

---

## Tables

### Reads From

| Table | What | Join Key |
|-------|------|----------|
| `outreach_company_target` | Company list (which companies to score) | outreach_id |
| `outreach_dol` | DOL signals (FORM_5500, BROKER_CHANGE, RENEWAL, PREMIUM) | outreach_id |
| `people_company_slot` | People signals (SLOT_FILLED, EMAIL_VERIFIED) | outreach_id |
| `outreach_blog` | Blog signals (FUNDING, ACQUISITION, EXPANSION) | outreach_id |

### Writes To

| Table | Role | Key Columns |
|-------|------|-------------|
| `outreach_bit_scores` | CANONICAL | outreach_id, score, score_tier, signal_count, people_score, dol_score, blog_score, talent_flow_score |

---

## Query Patterns

### "Score a single company"
```sql
-- Get all signal components for one company
SELECT
  ct.outreach_id,
  d.filing_present, d.renewal_month, d.carrier,
  (SELECT COUNT(*) FROM people_company_slot WHERE outreach_id = ct.outreach_id AND is_filled = 1) as slots_filled,
  (SELECT COUNT(*) FROM outreach_blog WHERE outreach_id = ct.outreach_id) as blog_signals
FROM outreach_company_target ct
LEFT JOIN outreach_dol d ON ct.outreach_id = d.outreach_id
WHERE ct.outreach_id = ?
```

### "Get current scores"
```sql
SELECT outreach_id, score, score_tier, signal_count FROM outreach_bit_scores ORDER BY score DESC
```

### "Band distribution"
```sql
SELECT score_tier, COUNT(*) as cnt FROM outreach_bit_scores GROUP BY score_tier ORDER BY score_tier
```

### "Companies in band 4+ (hot targets)"
```sql
SELECT b.outreach_id, b.score, b.score_tier, ct.state, ct.employees
FROM outreach_bit_scores b
JOIN outreach_company_target ct ON b.outreach_id = ct.outreach_id
WHERE b.score >= 60
ORDER BY b.score DESC
```

---

## Signal Weights

| Category | Signal | Weight | Source Process |
|----------|--------|--------|---------------|
| Structural Pressure | FORM_5500_FILED | +5 | 400 DOL |
| Structural Pressure | BROKER_CHANGE | +7 | 400 DOL |
| Structural Pressure | RENEWAL_APPROACHING | +5 | 400 DOL |
| Structural Pressure | PREMIUM_INCREASE | +5 | 400 DOL |
| Decision Surface | SLOT_FILLED | +10 | 200 People |
| Decision Surface | EMAIL_VERIFIED | +3 | 200 People |
| Decision Surface | EXECUTIVE_JOINED | +10 | 500 Talent Flow |
| Decision Surface | EXECUTIVE_LEFT | -5 | 500 Talent Flow |
| Narrative Volatility | FUNDING_EVENT | +15 | 300 Blog |
| Narrative Volatility | ACQUISITION | +12 | 300 Blog |
| Narrative Volatility | EXPANSION | +8 | 300 Blog |
| Narrative Volatility | LEADERSHIP_CHANGE | +10 | 300 Blog |

---

## Anti-Patterns

| Wrong | Right | Why |
|-------|-------|-----|
| Run BIT before dumb workers complete | Run AFTER all workers finish monthly cycle | BIT aggregates their output |
| Hardcode weights | Read from config (future: lcs_signal_registry) | Weights are variables, not constants |
| Score ALL 96K companies | Score only agent-assigned territory | Focus resources |

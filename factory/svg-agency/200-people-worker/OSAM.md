# OSAM — Process 200: People Worker
## Semantic Access Map — WHERE to Query, HOW to Join

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped access map |
| **Input** | A query need within the People Worker |
| **Middle** | Look up the table, join key, and database in this file |
| **Output** | Correct query against the correct database |
| **Circle** | If your query returns unexpected results, the OSAM is wrong — update it |
| **Blueprint OSAM** | barton-outreach-core → `docs/OSAM.md` |
| **Last Updated** | 2026-03-24 |

---

## Rule

**BEFORE RUNNING ANY DATA QUERY, READ THIS FILE.**

---

## Database

| Binding | Database | ID | Purpose | Access |
|---------|----------|----|---------|--------|
| `D1` | people-worker-200 | `4fa3b760-d8c9-4f94-8291-e0f85fc2a3a4` | Working database — territory dossier | Read + Write |

Neon is vault. D1 is workspace. SEED → WORK → PUSH lifecycle.

---

## Tables

| Table | Role | Row Count | Key Columns |
|-------|------|-----------|-------------|
| `companies` | Territory companies | 32,702 | company_unique_id, outreach_id, canonical_name, agent_name, state |
| `slots` | CEO/CFO/HR slot state | 43,203 | outreach_id, slot_type, person_unique_id, is_filled |
| `people` | Contact details | 20,487 | person_unique_id, email, linkedin_url, first_name, last_name |
| `dol` | DOL snapshot | 27,464 | outreach_id, ein, filing_present, renewal_month |
| `blog` | Blog signals | — | outreach_id, signal_type |
| `bit_scores` | BIT composite | — | outreach_id, score, score_tier |
| `monitor_list` | LinkedIn profiles to check | ~20,000 | outreach_id, linkedin_url, status |
| `baseline` | Previous month snapshot | — | slot state for diff |
| `snapshots` | Current month results | — | fetched profile data |
| `batch_progress` | Batch tracking | — | batch_id, processed_count |
| `outreach_status` | Company outreach state | — | outreach_id, status |
| `errors` | Error drain | — | error details |

---

## Join Keys

| Key | Where It Lives | What It Joins |
|-----|---------------|---------------|
| `company_unique_id` | companies | Company identity (= sovereign_company_id) |
| `outreach_id` | companies, slots, dol, blog, bit_scores, monitor_list | ALL sub-hub data to company |
| `person_unique_id` | slots → people | Slot to contact details |

---

## Query Patterns

### "What companies are in the territory?"
```sql
SELECT * FROM companies WHERE agent_name IS NOT NULL
```

### "What slots are filled for a company?"
```sql
SELECT * FROM slots WHERE outreach_id = ? AND is_filled = 1
```

### "Get contact details for a slot"
```sql
SELECT s.slot_type, p.first_name, p.last_name, p.email, p.linkedin_url
FROM slots s
JOIN people p ON s.person_unique_id = p.person_unique_id
WHERE s.outreach_id = ? AND s.is_filled = 1
```

### "What's the monitor list status?"
```sql
SELECT status, COUNT(*) FROM monitor_list GROUP BY status
```

### "Batch progress"
```sql
SELECT * FROM batch_progress ORDER BY rowid DESC LIMIT 1
```

### "Errors for today"
```sql
SELECT * FROM errors WHERE created_at > date('now') ORDER BY created_at DESC
```

---

## Anti-Patterns

| Wrong | Right | Why |
|-------|-------|-----|
| Query Neon during fetch cycle | Query D1 only | SEED→WORK→PUSH. Neon is vault. |
| Join companies to slots via company_unique_id | Join via outreach_id | outreach_id is the universal join key |
| Fetch LinkedIn without delay | 30-120 second random delay | Rate limiting / detection avoidance |
| Use Hunter/Apollo before free tools | Well drinks first, top shelf last | Tool priority doctrine |

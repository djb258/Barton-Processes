# OSAM — Process 100: LCS Pipeline
## Semantic Access Map — WHERE to Query, HOW to Join

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped access map |
| **Input** | A query need within the LCS pipeline |
| **Middle** | Look up the table, join key, and database in this file |
| **Output** | Correct query against the correct database |
| **Circle** | If your query returns unexpected results, the OSAM is wrong — update it |
| **Blueprint OSAM** | company-lifecycle-cl → `doctrine/OSAM.md` (full repo scope) |
| **Last Updated** | 2026-03-24 |

---

## Rule

**BEFORE RUNNING ANY DATA QUERY, READ THIS FILE.**

If your question isn't in this OSAM, STOP and ask. Do not guess tables or join keys.

---

## Databases

| Binding | Database | Purpose | Access |
|---------|----------|---------|--------|
| `D1` | svg-d1-spine | LCS tables — signals, CID, SID, MID, events, errors, registries | Read + Write |
| `D1_OUTREACH` | svg-d1-outreach-ops | Company data — CT, DOL, People, BIT | Read Only |

**Cross-database rule:** The LCS pipeline READS from outreach but NEVER WRITES to it. Outreach data is owned by its respective dumb worker processes (006 DOL, 007 People, etc.). LCS writes ONLY to spine.

---

## Universal Join Keys

| Key | Where It Lives | What It Joins |
|-----|---------------|---------------|
| `sovereign_company_id` | Spine: lcs_cid, lcs_signal_queue, lcs_event, lcs_err0 | Everything to a company |
| `company_unique_id` | Outreach: outreach_company_target | Same as sovereign_company_id — the CL identity |
| `outreach_id` | Outreach: ALL outreach tables | CT to DOL, CT to People, CT to BIT |
| `communication_id` | Spine: lcs_cid, lcs_sid_output, lcs_mid_sequence_state, lcs_event | CID to all downstream stages |
| `signal_set_hash` | Spine: lcs_signal_queue, lcs_signal_registry, lcs_cid | Signal to its registry definition |
| `frame_id` | Spine: lcs_cid, lcs_frame_registry, lcs_sid_output | CID to its message frame template |
| `person_unique_id` | Outreach: people_company_slot → people_people_master | Slot to contact details |

---

## Query Patterns

### "What company is this?"
```sql
-- Outreach D1
SELECT * FROM outreach_company_target WHERE company_unique_id = ?
```

### "What DOL data does this company have?"
```sql
-- Outreach D1 — join on outreach_id
SELECT d.* FROM outreach_dol d
JOIN outreach_company_target ct ON d.outreach_id = ct.outreach_id
WHERE ct.company_unique_id = ?
```

### "Who are the contacts at this company?"
```sql
-- Outreach D1 — slot + person join
SELECT cs.slot_type, pm.first_name, pm.last_name, pm.email, pm.linkedin_url
FROM people_company_slot cs
LEFT JOIN people_people_master pm ON cs.person_unique_id = pm.person_unique_id
WHERE cs.outreach_id = ? AND cs.is_filled = 1
ORDER BY CASE cs.slot_type WHEN 'CFO' THEN 1 WHEN 'CEO' THEN 2 WHEN 'HR' THEN 3 ELSE 4 END
```

### "What's the BIT score?"
```sql
-- Outreach D1
SELECT score, score_tier, signal_count FROM outreach_bit_scores WHERE outreach_id = ?
```

### "What signals are pending?"
```sql
-- Spine D1
SELECT * FROM lcs_signal_queue WHERE status = 'pending' ORDER BY priority DESC
```

### "What happened with this communication?"
```sql
-- Spine D1 — trace full chain by communication_id
SELECT * FROM lcs_cid WHERE communication_id = ?;
SELECT * FROM lcs_sid_output WHERE communication_id = ?;
SELECT * FROM lcs_mid_sequence_state WHERE communication_id = ?;
SELECT * FROM lcs_event WHERE communication_id = ? ORDER BY created_at;
SELECT * FROM lcs_err0 WHERE communication_id = ?;
```

### "What signal types exist?"
```sql
-- Spine D1 — config table
SELECT signal_set_hash, signal_name, signal_category FROM lcs_signal_registry WHERE is_active = 1
```

### "What message frames are available?"
```sql
-- Spine D1 — config table
SELECT frame_id, frame_name, tier, channel, step_in_sequence FROM lcs_frame_registry WHERE is_active = 1
```

### "What's the adapter health?"
```sql
-- Spine D1 — config table
SELECT adapter_type, daily_cap, sent_today, health_status FROM lcs_adapter_registry
```

### "What errors exist for a company?"
```sql
-- Spine D1
SELECT * FROM lcs_err0 WHERE sovereign_company_id = ? ORDER BY created_at DESC
```

### "Pipeline stats"
```sql
-- Spine D1
SELECT status, COUNT(*) FROM lcs_signal_queue GROUP BY status;
SELECT compilation_status, COUNT(*) FROM lcs_cid GROUP BY compilation_status;
SELECT construction_status, COUNT(*) FROM lcs_sid_output GROUP BY construction_status;
SELECT delivery_status, COUNT(*) FROM lcs_mid_sequence_state GROUP BY delivery_status;
SELECT failure_type, COUNT(*) FROM lcs_err0 GROUP BY failure_type;
```

---

## Anti-Patterns

| Wrong | Right | Why |
|-------|-------|-----|
| Query Neon during pipeline processing | Query D1 only | Neon is vault. D1 is workspace. SEED→WORK→PUSH. |
| Join outreach tables via `company_domain` | Join via `outreach_id` | outreach_id is the universal join key |
| Write to outreach D1 from LCS pipeline | Write to spine D1 only | LCS doesn't own outreach data |
| Query `lcs_cid` by `cid_id` | Query by `communication_id` | v2 uses communication_id as the primary key concept |
| Hardcode signal types | Read from lcs_signal_registry | Config-driven, not hardcoded |
| Hardcode message templates | Read from lcs_frame_registry | Frame registry IS the template engine |

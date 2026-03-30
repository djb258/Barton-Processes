# PROCESS: Talent Flow
## Movement detection engine for executive slot changes — if we can't see who moved, we're selling blind
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-500 |
| Name | Talent Flow |
| Business Silo | svg-agency |
| CTB Position | factory/svg-agency/500-talent-flow |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed (Python script, not a CF Worker yet) |
| BAR Reference | BAR-50 |
| Deployed URL | not deployed |
| Cron | Monthly (manual — runs AFTER Process 200 completes) |
| Runtime | Python 3 script with psql subprocess |

---

## 2. WHY THIS EXISTS

A filled slot today doesn't mean a filled slot tomorrow. CEOs leave, CFOs get promoted, HR directors change companies. If Process 200 fills the slots but nobody watches for changes, we're outreaching to ghosts — wrong name, wrong title, wrong company.

Talent Flow is the monthly sensor. It reads Process 200's LinkedIn snapshots, compares them to stored people data, and emits deterministic signals when an executive joins or leaves. Those signals feed Process 100 (LCS Pipeline) so CIDs reflect reality, not stale data.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Monthly, after Process 200 completes its LinkedIn refresh for the target month.
2. **"How do we get it?"** — Pure database diff against Neon tables. No external APIs, no proxy, no AI.

### Input
- Process 200's LinkedIn snapshots for the target month (`people.linkedin_snapshots`)
- Stored person records as baseline (`people.people_master`)
- Executive slot assignments (`people.company_slot` — CEO, CFO, HR only)
- Territory filter (`people.v_territory_companies`)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | run_month parameter | Gate check: verify Process 200 has snapshots for target month. If count=0, FAIL and exit. | Go/no-go | psql query against Neon |
| 2 | Snapshots + people_master + company_slot + v_territory_companies | Movement detection: join snapshots to stored data, filter to executive slots (CEO/CFO/HR) in territory companies, filter to `movement_detected = true` | List of executive movements with movement_type | psql query against Neon |
| 3 | Movement list | Signal classification: COMPANY_CHANGED or BOTH_CHANGED = TF-02 EXECUTIVE_LEFT. TITLE_CHANGED = TF-01 EXECUTIVE_JOINED. | Classified signals with magnitude and expiry | Python logic (deterministic) |
| 4 | Classified signals | Write signals to `outreach.signal_output` with dedup on (outreach_id, signal_code, run_month) | Signal records in Neon | psql INSERT against Neon |

### Output
- Signals written to `outreach.signal_output` in Neon:

| Column | Value |
|--------|-------|
| outreach_id | From company_slot join |
| signal_code | TF-01 or TF-02 |
| signal_name | Description (truncated to 50 chars) |
| signal_source | 'talent_flow' |
| signal_value | movement_type (COMPANY_CHANGED, TITLE_CHANGED, BOTH_CHANGED) |
| magnitude | 10 (joined) or 8 (left) |
| expires_at | run_date + 90 days |
| run_month | First day of run month |

- Dedup: `ON CONFLICT (outreach_id, signal_code, run_month) DO NOTHING` — one signal per company per type per month.

### Circle (Bedrock §5)
Signals feed Process 100 (LCS Pipeline) which compiles CIDs. Movement signals adjust outreach priority — a company with a freshly joined CEO is a higher-value target than one with a stable roster. Signal expiry (90 days) ensures stale movements don't persist. Next month's run produces a fresh diff, closing the loop.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| Neon (Marketing DB) | DATABASE_URL env var | — | READ/WRITE | All people tables + signal_output |

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| psql | CLI | Free | DATABASE_URL | Executes SQL against Neon via subprocess |
| Python 3 | Runtime | Free | None | Script execution, argument parsing, signal classification |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| DATABASE_URL | imo-creator | dev | psql subprocess — Neon connection string |

**Tool Priority (Well Drinks First):**
1. Pure database diff — $0. No external APIs, no proxy, no paid tools.

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `people.linkedin_snapshots` | Monthly LinkedIn profile snapshots from Process 200 | person_id, company_unique_id, run_month |
| `people.people_master` | Stored contact records (baseline for diff) | unique_id = person_id |
| `people.company_slot` | CEO/CFO/HR slot assignments, is_filled, outreach_id | person_unique_id |
| `people.v_territory_companies` | Territory filter (agent assignments) | company_unique_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `outreach.signal_output` | TF-01 and TF-02 signals with magnitude, expiry, movement_type | Step 4 — after classification |

### Join Chain

```
people.linkedin_snapshots.person_id (run_month = target)
  → people.people_master.unique_id (baseline title/company for diff)
  → people.company_slot.person_unique_id (slot_type filter: CEO, CFO, HR)
    → people.company_slot.outreach_id (provides outreach_id for signal_output)
  → people.v_territory_companies.company_unique_id (territory filter)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Call external APIs | This is a pure database diff. No LinkedIn API, no proxy, no scraping. |
| Run without Process 200 completing first | Snapshots are the input. No snapshots = no diff. Gate check enforces this. |
| Write to D1 | Currently writes to Neon only. Known violation of SEED-WORK-PUSH. |
| Use AI for signal classification | Classification is deterministic: movement_type maps directly to signal code. No LLM. |
| Overwrite existing signals | Dedup via ON CONFLICT DO NOTHING. One signal per company per type per month. |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Did Process 200 run this month? | `people.linkedin_snapshots` | `run_month = target_month`, COUNT(*) |
| Who moved? | `people.linkedin_snapshots` | `movement_detected = true` |
| What kind of movement? | `people.linkedin_snapshots` | `movement_type` |
| Is this an executive slot? | `people.company_slot` | `slot_type IN ('CEO', 'CFO', 'HR')` |
| What company does the signal attach to? | `people.company_slot` | `outreach_id` |
| Is this company in territory? | `people.v_territory_companies` | `company_unique_id` |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)
- Signal types: TF-01 EXECUTIVE_JOINED (magnitude 10, 90 day expiry), TF-02 EXECUTIVE_LEFT (magnitude 8, 90 day expiry)
- Executive slot filter: CEO, CFO, HR only
- Classification rules: COMPANY_CHANGED or BOTH_CHANGED = TF-02. TITLE_CHANGED = TF-01.
- Dependency gate: Process 200 must have snapshots for target month. Zero snapshots = hard stop.
- Dedup key: (outreach_id, signal_code, run_month) — one signal per company per type per month
- Signal source: 'talent_flow' (constant string in all signal records)
- No AI, no external APIs, no proxy. Pure database diff.

### Variables (fill — changes every run)
- Which month is being processed (run_month parameter)
- How many snapshots Process 200 produced
- How many executive movements detected
- Split between TF-01 (joined) and TF-02 (left) signals
- Which companies and people are affected
- Whether run is dry-run or live

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Can't answer two-question intake | HALT — process isn't defined |
| Process 200 snapshots for target month = 0 | HALT — dependency not met. Exit with error. |
| DATABASE_URL not set and no fallback | HALT — can't connect to Neon |
| psql not available on system | HALT — runtime dependency missing |
| movement_type not in (COMPANY_CHANGED, TITLE_CHANGED, BOTH_CHANGED) | Signal silently skipped — known gap, no crash |
| Signal write fails | HALT — check Neon connectivity and signal_output schema |
| Strike 3 on same failure | Troubleshoot/Train → produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| Process 200 (People Worker) | MUST complete monthly LinkedIn refresh. Snapshots in `people.linkedin_snapshots` for target month. | BUILD |
| Neon (Marketing DB) | All people tables, signal_output table | DONE |
| psql CLI | Installed on execution machine | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| Process 100 (LCS Pipeline) | Executive movement signals from `outreach.signal_output` — adjusts CID priority |

---

## 9. SMOKE TEST

```
1. python3 src/talent-flow.py --dry-run → expected: gate check passes, movements listed, no writes
2. psql query: SELECT COUNT(*) FROM people.linkedin_snapshots WHERE run_month = '2026-03-01' → expected: > 0
3. psql query: SELECT COUNT(*) FROM people.linkedin_snapshots ls JOIN people.company_slot cs ON cs.person_unique_id = ls.person_id WHERE ls.movement_detected = true AND cs.slot_type IN ('CEO','CFO','HR') → expected: >= 0 (may be 0 if no movements)
4. python3 src/talent-flow.py --month 2026-03 → expected: signals written, summary printed
5. psql query: SELECT signal_code, COUNT(*) FROM outreach.signal_output WHERE signal_source = 'talent_flow' GROUP BY signal_code → expected: TF-01 and/or TF-02 counts match script summary
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do the snapshots exist for the target month? Does the signal_output table exist? Are executive slots populated?
2. **Flow:** Does the snapshot data join correctly to people_master and company_slot? Does the territory filter apply? Do signals reach signal_output?
3. **Change:** Is the movement_type correctly classified to TF-01 or TF-02? Does the dedup prevent duplicates? Does magnitude match the signal definition?

If any fails → that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock §6).

---

## 10. LOGBOOK

_No runs logged yet. Process is in BUILD state._

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | Not yet a CF Worker | Built as Python script with psql subprocess for rapid prototyping | Future: convert to CF Worker with Hyperdrive | 0 |
| 2 | 2026-03-29 | Writes directly to Neon | Violates SEED-WORK-PUSH pattern — should write to D1 first, then PUSH | Future: rewire to D1 workspace | 0 |
| 3 | 2026-03-29 | DATABASE_URL hardcoded as fallback | Credentials inline in source code | Set DATABASE_URL env var in production; remove fallback | 0 |
| 4 | 2026-03-29 | Only 2 of 4 planned signals | TF-03 (DISPLACE) and TF-04 (CASCADE) not implemented | BAR-50 scope — cascade discovery with Clay.com | 0 |
| 5 | 2026-03-29 | Cascade discovery not wired | Clay.com integration for unknown company lookup planned but not built | BAR-50 scope | 0 |
| 6 | 2026-03-29 | ICP gate not enforced | 50-5000 employees + 6 states filter for cascade targets not coded | BAR-50 scope | 0 |
| 7 | 2026-03-29 | Unknown movement_type silently skipped | No handling for movement types outside the three known values | Add logging or error table write for unknown types | 0 |
| 8 | 2026-03-29 | Dependency check is simple count | Checks if ANY snapshots exist, not whether Process 200 fully completed | Future: check Process 200 completion flag or expected count | 0 |

---

## 12. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | PROCESS.md written from CLAUDE.md + source code + heir.yaml | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | barton-outreach-core/doctrine/OSAM.md |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

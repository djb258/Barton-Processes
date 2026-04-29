> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — Process 500: Talent Flow

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

Movement detection engine for executive-level slot changes. Reads Process 200's LinkedIn snapshots month-over-month and detects when a CEO, CFO, or HR contact has joined, left, or changed roles. Pure database diff -- no AI, no external APIs, no proxy. Feeds signals to LCS Pipeline (100).

## How It Works

Monthly sensor. Runs AFTER Process 200 completes its monthly LinkedIn refresh.

1. **Gate Check:** Verify Process 200 has snapshots for the target month in `people.linkedin_snapshots`. If count=0, FAIL with dependency not met.
2. **Movement Detection:** Compare current month snapshots to stored people data. Join `linkedin_snapshots` to `people_master` and `company_slot`. Filter to executive slots (CEO, CFO, HR) in territory companies.
3. **Signal Classification:** Deterministic classification based on `movement_type`:
   - `COMPANY_CHANGED` -> TF-02 EXECUTIVE_LEFT (person moved to different company)
   - `TITLE_CHANGED` -> TF-01 EXECUTIVE_JOINED (role change at same company)
   - `BOTH_CHANGED` -> TF-02 EXECUTIVE_LEFT (both title and company changed)
4. **Signal Output:** Write signals to `outreach.signal_output` in Neon with outreach_id, signal code, magnitude, and expiry.

## Signal Types

| Code | Signal | Meaning | Magnitude | Expiry |
|------|--------|---------|-----------|--------|
| TF-01 | EXECUTIVE_JOINED | New person in slot or role change | 10 | 90 days |
| TF-02 | EXECUTIVE_LEFT | Slot vacated or person changed company | 8 | 90 days |

**Note:** The heir.yaml references 4 signals (TF-01 VACATE, TF-02 ASSIGN, TF-03 DISPLACE, TF-04 CASCADE), but the current implementation uses only TF-01 and TF-02. TF-03 (DISPLACE) and TF-04 (CASCADE) are planned for the cascade discovery feature.

## Cascade Discovery (Planned -- Not Yet Implemented)

When an executive LEAVES a company (TF-02), the question becomes: "where did they go?" If they went to an unknown company:

- **TF-03 DISPLACE:** The executive displaced someone at the new company
- **TF-04 CASCADE:** The displacement triggers a chain reaction

**ICP Gate:** Only pursue cascade discovery if the new company meets ICP criteria:
- 50-5,000 employees
- Located in one of 6 target states

**Tool:** Clay.com for discovering unknown companies from LinkedIn company name matches.

This is BAR-50 scope and not yet wired.

## Data Sources

| Source | What | Join Key |
|--------|------|----------|
| `people.linkedin_snapshots` | Monthly LinkedIn profile snapshots from Process 200 | person_id, company_unique_id, run_month |
| `people.people_master` | Stored contact records (baseline) | unique_id = person_id |
| `people.company_slot` | CEO/CFO/HR slot assignments | person_unique_id, is_filled |
| `people.v_territory_companies` | Territory filter (agent assignments) | company_unique_id |

## Output

Signals written to `outreach.signal_output` in Neon:

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

**Dedup:** `ON CONFLICT (outreach_id, signal_code, run_month) DO NOTHING` -- one signal per company per type per month.

## Usage

```bash
python3 src/talent-flow.py                    # Run for current month
python3 src/talent-flow.py --month 2026-03    # Specific month
python3 src/talent-flow.py --dry-run          # Preview without writing signals
```

## Databases

**Neon vault (read + write):**
- **Read:** `people.linkedin_snapshots`, `people.people_master`, `people.company_slot`, `people.v_territory_companies`
- **Write:** `outreach.signal_output`

**No D1 workspace.** Current implementation queries Neon directly via `psql` subprocess. Future: may convert to CF Worker reading from D1 after Process 200 seeds snapshots there.

## Key Joins

- Snapshot to person: `linkedin_snapshots.person_id` = `people_master.unique_id`
- Person to slot: `company_slot.person_unique_id` = `linkedin_snapshots.person_id` AND `company_slot.is_filled = true`
- Slot filter: `company_slot.slot_type IN ('CEO', 'CFO', 'HR')`
- Territory filter: `v_territory_companies.company_unique_id` = `linkedin_snapshots.company_unique_id`
- Signal output join: `company_slot.outreach_id` provides the outreach_id for signal_output

## Dependencies

| Direction | Process | What |
|-----------|---------|------|
| Upstream | 200 People Worker | MUST complete monthly LinkedIn refresh first. If no snapshots for run_month, Talent Flow exits with error. |
| Downstream | 100 LCS Pipeline | Executive movement signals feed CID compilation |

## Worker Config

- **Runtime:** Python 3 script (not yet a CF Worker)
- **Schedule:** Monthly, runs AFTER Process 200 completes
- **External APIs:** None (pure database diff)
- **Proxy:** None needed
- **Cost:** $0 (database queries only)

## Known Issues

| Issue | Resolution |
|-------|------------|
| Not yet a CF Worker | Currently a Python script with psql subprocess calls. Future: convert to CF Worker. |
| Writes directly to Neon | Violates SEED-WORK-PUSH pattern. Should write to D1 first, then PUSH. |
| DB_URL hardcoded as fallback | Production: set DATABASE_URL env var. Default fallback has credentials inline. |
| Only 2 of 4 planned signals implemented | TF-01 and TF-02 work. TF-03 (DISPLACE) and TF-04 (CASCADE) are BAR-50 scope. |
| Cascade discovery not wired | Clay.com integration for unknown company lookup is planned but not implemented. |
| ICP gate not enforced | 50-5000 employees + 6 states filter for cascade targets is not yet coded. |
| No movement_type handling for edge cases | If movement_type is not COMPANY_CHANGED, TITLE_CHANGED, or BOTH_CHANGED, signal is silently skipped. |
| Dependency check is simple count | Checks if ANY snapshots exist for run_month, not whether Process 200 fully completed. |

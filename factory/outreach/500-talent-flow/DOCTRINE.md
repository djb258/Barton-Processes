# DOCTRINE — Process 500: Talent Flow

> **Locked rules for Process 500 — Talent Flow**
> Every rule is numbered monotonically. No gaps. Source attribution required on every rule.
> Gate column states enforcement mechanism. No rule may be deleted — REPAIR or RETIRE only.

---

## Pre-Flight

Before executing any rule enforcement, confirm:
- `PROCESS-UT.md` is present at folder root
- `heir.yaml` carries all 8 HEIR fields
- Process 200 snapshot gate (D-500-01) checked before any further steps

---

## Rules

| Rule ID | Statement | Source | Gate |
|---------|-----------|--------|------|
| D-500-01 | Process 200 must have completed its monthly LinkedIn snapshot refresh for the target run_month before Process 500 may execute; if `COUNT(*) FROM people.linkedin_snapshots WHERE run_month = '{run_date}'` returns 0, the process MUST halt with a non-zero exit code and no signals may be written. | `CLAUDE.md` (dependencies section), `PROCESS.md` (§STOP CONDITIONS — "Process 200 has not run for the target month"), `heir.yaml` (acceptance_criteria[0]: "Process 200 must complete first"), `src/talent-flow.py` (lines 96-109: explicit count check and sys.exit(1)) | §8 STOP CONDITION — enforced at runtime gate before any downstream processing |
| D-500-02 | Signal types are locked to exactly two codes: TF-01 (EXECUTIVE_JOINED, magnitude 10, expiry 90 days) and TF-02 (EXECUTIVE_LEFT, magnitude 8, expiry 90 days); no new signal codes may be added without a BAR and corresponding DOCTRINE amendment. | `CLAUDE.md` (signal types table: TF-01/TF-02), `src/talent-flow.py` (SIGNALS dict, lines 31-44) | §9b GAUGE — tracked via signal_code count in outreach.signal_output; changes blocked until BAR-50 (TF-03/TF-04 planned scope) |
| D-500-03 | Signal classification is fully deterministic: COMPANY_CHANGED movement_type → TF-02 (EXECUTIVE_LEFT); TITLE_CHANGED movement_type → TF-01 (EXECUTIVE_JOINED); BOTH_CHANGED movement_type → TF-02 (EXECUTIVE_LEFT); any other movement_type → no signal written. No LLM, no probabilistic scoring, no heuristics may be substituted for this classification table. | `PROCESS.md` (IMO Middle table: Step 3 — Classify movement), `src/talent-flow.py` (lines 148-161: if/elif/elif classification block) | Pre-flight gate + §8 STOP CONDITION if classification logic deviates; auditor verifies determinism in Stage 3 |
| D-500-04 | No AI, no machine learning, no external intelligence API, and no proxy service may be used for movement detection or signal classification; Process 500 is a pure database diff operation reading data written by Process 200. | `CLAUDE.md` (process description: "No external tools. No API calls. No proxy. Pure database diff."), `PROCESS.md` (§CONSTANTS: "sensor_only = true") | §8 STOP CONDITION — any code path invoking external inference is a doctrine violation; enforced at audit |
| D-500-05 | Each signal write to `outreach.signal_output` uses the composite dedup key `(outreach_id, signal_code, run_month)` with `ON CONFLICT DO NOTHING`; re-running Process 500 for the same month is idempotent and must not produce duplicate signals. | `CLAUDE.md` (known issues: dedup behavior documented), `PROCESS.md` (§OSAM WRITE path), `src/talent-flow.py` (lines 162-183: INSERT with ON CONFLICT clause) | §9b GAUGE — verified by querying duplicate count post-run; pre-flight enforces ON CONFLICT presence before any deployment |
| D-500-06 | Process 500 reads exclusively from Neon PostgreSQL (`people.linkedin_snapshots`, `people.people_master`, `people.company_slot`, `people.v_territory_companies`) and writes exclusively to `outreach.signal_output`; no HTTP requests, no file I/O beyond the script itself, no additional databases, and no Cloudflare D1 writes are permitted. | `CLAUDE.md` (data sources table, output table), `PROCESS.md` (§OSAM: READ list, WRITE list, forbidden paths) | §8 STOP CONDITION if any foreign write path detected; auditor verifies no import of http/requests/urllib in src/ |
| D-500-07 | The executive slot filter is locked to exactly three slot_type values: CEO, CFO, HR; movement events for any other slot_type are excluded from signal generation and must not be written to `outreach.signal_output`. | `PROCESS.md` (§CONSTANTS: slot_types = [CEO, CFO, HR]), `src/talent-flow.py` (line 131: `cs.slot_type IN ('CEO', 'CFO', 'HR')`) | §9b GAUGE — slot distribution in output verified by auditor; filter change requires BAR + DOCTRINE amendment |
| D-500-08 | The `--dry-run` flag must produce all console output (movement detection rows, summary counts) without writing any records to `outreach.signal_output`; dry-run behavior is a required operational safety gate and must not be removed or bypassed in any future refactor. | `CLAUDE.md` (usage section: `--dry-run` flag documented), `src/talent-flow.py` (lines 163, 185: `if not dry_run` guards) | §9b GAUGE — dry-run verified by confirming zero new rows in outreach.signal_output after `--dry-run` execution |

---

## Amendment Protocol

1. A BAR must be opened to propose any rule change.
2. The Codex Mechanic amends the rule text and updates the source attribution column.
3. The Codex Auditor verifies the amended rule passes G21-G30 before the BAR is closed.
4. Rule IDs are never recycled. Retired rules are marked `[RETIRED BAR-NNN]` in the Statement column.
5. `PROCESS-UT.md` §7 must be updated to cite any new rule IDs within the same BAR.

---

## Document Control

| Field | Value |
|-------|-------|
| Process | 500 — Talent Flow |
| Rule Count | 8 (D-500-01 through D-500-08) |
| Template Version | V2 (from STAGE-1-CODEX-MECHANIC-OUTPUT.md §3) |
| Created | 2026-04-29 |
| Status | BUILD |
| Authority | Codex Runner (Stage 2) — subject to Auditor verification (Stage 3) |

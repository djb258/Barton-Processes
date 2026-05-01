# DOCTRINE — Process 100 Claude Code Routines
## Locked rules. Auditor enforces. Violations break autonomous agent scheduling or run integrity.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-DA100-01 | The routines table is the canonical registry of all autonomous Claude Code agent configurations. Every scheduled agent run MUST originate from a routines record. Ad-hoc agent invocations that bypass the routines table are forbidden in the production scheduling system. | routines.ts routines table | §5 stop — unregistered runs are unauditable and ungoverned |
| D-DA100-02 | The routine_runs table is the append-only audit log for every agent execution. Every routine invocation MUST produce a routine_runs record — whether it succeeds, fails, or is skipped. Runs without a routine_runs record are governance violations. | routines.ts routine_runs table | §5 stop — missing run records break the audit trail |
| D-DA100-03 | MC_DB is the sole database binding for the Claude Code Routines process. All reads and writes to routines and routine_runs MUST use the MC_DB D1 binding. No alternative database connections (direct D1 IDs, Neon, KV) are permitted for routine state. | routines.ts MC_DB binding | §5 stop — alternative bindings create split state between Mission Control and the scheduler |
| D-DA100-04 | Migration 0020 defines the canonical schema for routines and routine_runs tables. All writes MUST conform to migration 0020. Schema changes outside a BAR are violations. | migration 0020 (dave-agent) | §7 stop — schema drift breaks Mission Control dashboard queries |
| D-DA100-05 | A routine record MUST declare: name, schedule (cron expression), agent_prompt, enabled (boolean), and max_runtime_seconds. Routines missing any of these five fields are rejected at the write gate. | routines.ts routines schema | §5 stop — incomplete routine configs produce unpredictable agent behavior |
| D-DA100-06 | The enabled field is the kill switch for individual routines. Setting enabled = false stops scheduling of that routine without deleting the record. Routine records are never deleted — they are disabled. This preserves the audit trail. | routines.ts enabled field | §8 stop — deleting routine records destroys scheduling history |
| D-DA100-07 | max_runtime_seconds is a hard ceiling for each routine. The scheduler MUST enforce this ceiling. A routine_runs record with status = 'timeout' is written when the ceiling is hit. The agent process is terminated. No silent overruns. | routines.ts max_runtime_seconds | §5 stop — uncapped agent runs can exhaust CF Worker CPU limits and block other routines |
| D-DA100-08 | routine_runs records MUST carry: routine_id (FK), started_at, completed_at (or null if in-flight), status (enum: running / completed / failed / timeout / skipped), and output_summary. Records missing status are rejected. | routines.ts routine_runs schema | §5 stop — statusless run records are unauditable |
| D-DA100-09 | The Claude Code agent invoked by a routine operates with the permissions of the imo-creator Doppler environment. It may not self-modify the routines table or routine_runs table during an active run. Writes to routines/routine_runs are post-run only, not mid-run. | routines.ts agent invocation model | §9 stop — mid-run self-modification corrupts in-flight state |
| D-DA100-10 | The routines scheduler is scoped to Mission Control (MC_DB binding, dave-agent silo). It must not schedule or invoke agents on behalf of other silos (svg-agency, outreach, personal) without explicit routing through those silos' own governance. Cross-silo scheduling is a sovereign-silo violation. | law/BARTON_ENTERPRISES_CTB.md Sovereign Silos rule | §9 stop — cross-silo scheduling bypasses each silo's own ORBT governance |

## Cross-references
- UT §5 CONTRACT references D-DA100-01 (routines table), D-DA100-02 (routine_runs table), D-DA100-05 (required fields), D-DA100-08 (run record fields)
- UT §4 IMO references D-DA100-03 (MC_DB binding), D-DA100-07 (max_runtime enforcement)
- UT §6 JOIN CONTRACT references D-DA100-02 (routine_id FK in routine_runs)
- UT §7 SCHEMA references D-DA100-04 (migration 0020)
- UT §9 PERMISSIONS references D-DA100-06 (enabled kill switch), D-DA100-09 (no mid-run self-modification), D-DA100-10 (silo scope)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| BAR | BAR-331 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 |
| Rule Count | 10 (D-DA100-01 through D-DA100-10) |

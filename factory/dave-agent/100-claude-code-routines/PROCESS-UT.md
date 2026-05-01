# PROCESS-UT — Process 100 Claude Code Routines (dave-agent)
# BAR-331 | Governance backfill — code shipped, UT doc written post-deploy

---

## UT Pre-Flight Checklist (per `law/UT_CHECKLIST.md` v1.2.0)

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §1 PRD |
| 2 | OSAM — READ / WRITE / Join Chain / Forbidden Paths / Query Routing | ☑ | §6 JOIN CONTRACT + §9 PERMISSIONS |
| 3 | Component Status — every dependency has 🟢 / 🟡 / 🔴 with 1-line state | ☑ | §3 COMPONENT STATUS |
| 4 | Owner — human who fixes this at 2 AM | ☑ | §2 OWNER |
| 5 | Live Dashboard — URL or explicit "N/A" | ☑ | §2 OWNER |
| 6 | Kill Switch — exact command to stop the process | ☑ | §8 INGEST CHECKLIST |
| 7 | Logbook — last audit verdict + date (after certification only) | ☑ | §14 DOCUMENT CONTROL |
| 8 | FCEs Attached — which FCE runs structurally back this doc | ☑ | §11 FCE |
| 9 | BARs Referenced — every BAR this doc touches, with status | ☑ | §13 BARS REFERENCED |
| 10 | LBB Subjects Fed — which LBB subject(s) this doc's session logs go to | ☑ | §12 LBB |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | ☑ | §4 IMO |
| 12 | Live Verification — every numeric count, cron, URL, command, BAR status grounded | ☑ | §3 COMPONENT STATUS |
| 13 | ctb_node — declared path on Barton Enterprises CTB trunk | ☑ | heir.yaml + §4 IMO |

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 1 — IDENTITY
     ════════════════════════════════════════════════════════════ -->

## §1 PRD

**What:** Claude Code Routines is the autonomous agent scheduling system for Dave's Mission Control. It maintains a registry of scheduled Claude Code agent configurations (routines table) and an append-only audit log of every execution (routine_runs table), all stored in MC_DB D1.

**Why:** Dave runs recurring autonomous Claude Code agent tasks (LBB ingests, process audits, outreach enrichment checks, etc.). Without a governed scheduler, these run ad-hoc with no audit trail, no kill switches, and no visibility in Mission Control. Routines provides the governance layer: every agent run is registered, auditable, and controllable from the dashboard.

**Who:** Dave Barton (sole operator — dave-agent silo). Mission Control dashboard (consumer of routine_runs state).

**Scope:** mission-control-api CF Worker (routines.ts) — routines registry + scheduler + routine_runs logging. MC_DB D1 binding (migration 0020). Claude Code agent invocation per enabled routine on cron schedule.

**Out of scope:** Agent logic itself (each routine's agent_prompt governs the agent's actions — out of scope for this process doc). Cross-silo scheduling (SVG Agency, outreach, personal routines route through their own governance). Routine output storage beyond output_summary string.

**Success metric:** Every scheduled agent run produces a routine_runs record with status + output_summary. enabled = false halts a routine without data loss. max_runtime_seconds ceiling enforced on every run.

---

## §2 OWNER

**Owner:** Dave Barton — dbarton@svg.agency
**Fixes at 2 AM:** Dave Barton
**Live Dashboard:** Mission Control Routines page (schedule status, run history via routine_runs)
**On-call escalation:** N/A (single-operator system)

---

## §3 COMPONENT STATUS

| Component | Status | State |
|-----------|--------|-------|
| mission-control-api CF Worker (routines.ts) | 🟢 | Deployed — scheduler reading routines table on cron |
| MC_DB D1 (routines table) | 🟢 | Canonical routine registry (migration 0020) |
| MC_DB D1 (routine_runs table) | 🟢 | Append-only audit log — every run recorded |
| Claude Code agent (per-routine) | 🟢 | Invoked on schedule per enabled routine |
| Doppler imo-creator dev | 🟢 | Supplies CLAUDE_CODE_OAUTH_TOKEN + MC_DB binding |

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 2 — CONTRACT
     ════════════════════════════════════════════════════════════ -->

## §4 IMO

**CTB node:** `barton-enterprises → dave-agent silo → Mission Control → Claude Code Routines`
**Hub-Spoke role:** Hub (routines scheduler is the Middle — all scheduling + logging logic here)
**Altitude:** leaf (10K ft — operational)
**IMO topology:** middle

```
INPUT                        MIDDLE (routines.ts)                    OUTPUT
──────────────────────────   ──────────────────────────────────      ────────────────────────
Cron trigger              →  Read enabled routines from MC_DB    →   Claude Code agent
  (CF Worker scheduled        Validate routine fields (5 required)     invocation (per routine)
   trigger)                   Enforce max_runtime_seconds          →  routine_runs write
                              Invoke Claude Code agent                  (status + output_summary)
                              Capture output_summary              →  Mission Control dashboard
                              Write routine_runs record               (run history, status)
```

**Hub-Spoke geometry:**
- Hub: routines.ts scheduler (all logic)
- Spoke 1: MC_DB D1 (canonical state — routines + routine_runs)
- Spoke 2: Claude Code agent (external invocation — dumb execution, no scheduling logic)
- Rim: Mission Control dashboard (read-only view of routine_runs)

**Three Primitives check:**
- Thing: routines record exists with enabled = true before scheduler invokes agent
- Flow: cron trigger flows from CF Worker scheduled trigger → routines.ts → agent invocation
- Change: agent execution → output_summary captured → routine_runs record written (ordered, no skip)

---

## §5 CONTRACT

### routines Table (Registry)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| routine_id | string (UUID) | yes | Canonical ID |
| name | string | yes | Human-readable routine name |
| schedule | string (cron) | yes | Cron expression (e.g., `0 9 * * *`) |
| agent_prompt | string | yes | Full prompt sent to Claude Code agent |
| enabled | boolean | yes | Kill switch — false halts scheduling |
| max_runtime_seconds | integer | yes | Hard ceiling for agent execution |
| created_at | ISO 8601 datetime | yes | Record creation |
| updated_at | ISO 8601 datetime | yes | Last modification |

### routine_runs Table (Audit Log)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| run_id | string (UUID) | yes | Canonical ID |
| routine_id | string (UUID FK) | yes | References routines.routine_id |
| started_at | ISO 8601 datetime | yes | Invocation timestamp |
| completed_at | ISO 8601 datetime | no | Null if in-flight or timed out |
| status | enum | yes | running / completed / failed / timeout / skipped |
| output_summary | string | yes | Agent output summary (truncated if needed) |

### Status Enum

| Value | Description |
|-------|-------------|
| running | Agent currently executing |
| completed | Agent finished within max_runtime_seconds |
| failed | Agent returned error or exception |
| timeout | max_runtime_seconds ceiling hit; agent terminated |
| skipped | Routine was eligible but skipped (e.g., prior run still in-flight) |

---

## §6 JOIN CONTRACT

**Primary join chain:**
```
CF Worker cron trigger
  → routines table (enabled = true filter)
    → routine invocation (routine_id carried)
      → routine_runs table (routine_id FK)
        → Mission Control dashboard (routine_id JOIN for history display)
```

**READ path:** cron trigger → MC_DB routines query (enabled = true) → agent invocation
**WRITE path:** agent completes/fails/times out → MC_DB routine_runs INSERT
**FORBIDDEN:** Agent writing to routines or routine_runs mid-run. Cross-silo routine registration. Routine record deletion.

---

## §7 SCHEMA

### Migration 0020

```sql
-- routines (registry)
CREATE TABLE routines (
  routine_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  schedule TEXT NOT NULL,          -- cron expression
  agent_prompt TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,  -- 1=true, 0=false
  max_runtime_seconds INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- routine_runs (append-only audit log)
CREATE TABLE routine_runs (
  run_id TEXT PRIMARY KEY,
  routine_id TEXT NOT NULL REFERENCES routines(routine_id),
  started_at TEXT NOT NULL,
  completed_at TEXT,               -- NULL if in-flight
  status TEXT NOT NULL CHECK(status IN ('running','completed','failed','timeout','skipped')),
  output_summary TEXT NOT NULL,
  FOREIGN KEY (routine_id) REFERENCES routines(routine_id)
);

CREATE INDEX idx_routine_runs_routine_id ON routine_runs(routine_id);
CREATE INDEX idx_routine_runs_started_at ON routine_runs(started_at DESC);
```

---

## §8 INGEST CHECKLIST

**Adding a new routine:**
1. INSERT into routines table with all 5 required fields
2. Set enabled = true when ready to schedule
3. Verify max_runtime_seconds is set conservatively (start low)
4. Confirm agent_prompt is tested before enabling on schedule

**Disabling a routine (kill switch):**
```sql
-- Disable without deleting (preserves audit trail)
UPDATE routines SET enabled = 0, updated_at = datetime('now')
WHERE routine_id = '{routine_id}';
```

**Kill switch — disable all routines:**
```sql
UPDATE routines SET enabled = 0, updated_at = datetime('now');
```

**Kill switch — undeploy scheduler entirely:**
```bash
cd workers/mission-control-api
npx wrangler delete mission-control-api --force
# Note: this kills all mission-control-api routes, not just routines
# Prefer disabling individual routines over full undeploy
```

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 3 — GOVERNANCE
     ════════════════════════════════════════════════════════════ -->

## §9 PERMISSIONS

**READ (routines registry):**
- Requires: Internal CF Worker scheduled trigger (no external auth on scheduler reads)
- Who: routines.ts scheduler only
- Forbidden: External HTTP reads on routines table

**WRITE (routine_runs):**
- Requires: Completed/failed/timed-out agent run
- Who: routines.ts scheduler (post-run write only)
- Forbidden: Agent writing to routine_runs mid-run (D-DA100-09)

**WRITE (routines registry):**
- Requires: Manual SQL or Mission Control admin action (Dave only)
- Who: Dave Barton
- Forbidden: Agent self-modifying its own routine record

**FORBIDDEN PATHS:**
- Routine record deletion (D-DA100-06 — disable only, never delete)
- Agent writing to routines or routine_runs during execution (D-DA100-09)
- Cross-silo scheduling without target silo governance routing (D-DA100-10)
- Alternative DB bindings (non-MC_DB) for routine state (D-DA100-03)
- Routines missing any of the 5 required fields (D-DA100-05)

**Three Primitives enforcement:**
- Thing: routine record must exist with enabled = true before invocation
- Flow: cron trigger must reach routines.ts scheduler before agent is invoked
- Change: agent completion must produce routine_runs record before next run is eligible

---

## §10 ERROR HANDLING

| Scenario | Handler | Response |
|----------|---------|----------|
| Agent exceeds max_runtime_seconds | Scheduler timeout handler | Terminate agent; write routine_runs with status = 'timeout' |
| Agent throws exception | Scheduler error catch | Write routine_runs with status = 'failed' + error in output_summary |
| Prior run still in-flight at cron fire | Scheduler overlap check | Write routine_runs with status = 'skipped'; do not double-invoke |
| MC_DB write failure on routine_runs | Scheduler error handler | Log to CF Worker console; retry once; if still failing, alert via Mission Control error surface |
| Routine missing required field | Scheduler validation | Skip invocation; write skipped run record with validation error in output_summary |

---

## §11 FCE

**FCE attachment:** `barton-enterprises → dave-agent silo → Mission Control`
**FCE runs:** N/A for current scope (internal scheduling governance — no competitive resource allocation FCE applicable)
**Future FCE candidates:** Routine efficiency analysis (runtime trends, failure rate by routine type)

---

## §12 LBB

**LBB subject:** `system` (infrastructure — CF Worker + D1 scheduling pattern)
**Secondary subject:** `processes` (cross-cutting process knowledge — autonomous agent governance)
**Session log target:** Ingest BAR-331 completion record after batch closes
**Record template:** HEIR stamp + ORBT state (OPERATE) + acceptance criteria status

---

## §13 BARS REFERENCED

| BAR | Description | Status |
|-----|-------------|--------|
| BAR-331 | Claude Code Routines — autonomous agent scheduler + routines/routine_runs tables (migration 0020) | CLOSED (code shipped) |

---

## §14 DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| BAR | BAR-331 |
| Version | 1.0.0 |
| Status | OPERATE (governance backfill — code shipped pre-UT) |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Template | law/UNIFIED_TEMPLATE.md v2.0 |
| UT Checklist | law/UT_CHECKLIST.md v1.2.0 — 13 items, all addressed |
| Audit verdict | Pending batch audit (BAR-167 through BAR-48) |
| ctb_node | barton-enterprises → dave-agent silo → Mission Control → Claude Code Routines |

# Production Line — Bedrock Design Document

**BAR-196** | Designed with Foundational Bedrock

---

## Bedrock Pre-Flight

### Two-Question Intake (S7)
1. **What triggers this?** -- Dave defines a goal ("Prepare Acme Corp for sales"). System decomposes into steps and runs them.
2. **How do we get it?** -- CF Agents (Durable Objects) as runtime. D1 for working data. Visual UI in Mission Control.

### C&V Test (S2)

#### Constants (structure -- never changes)

| Constant | Format | Why It's Fixed |
|----------|--------|---------------|
| Process catalog | Array of {id, name, silo, worker_url} | Processes are registered, not discovered |
| Chain definitions | Ordered array of process IDs per silo | Sequence is the constant, results are variable |
| Agent roles | One Durable Object class per silo | Silo boundary is structural |
| Hub-spoke geometry | Hub orchestrates, spokes execute, no sideways | Bedrock S4 |
| IMO per step | Input/Middle/Output at every level | Bedrock S3 |
| Step states | pending/running/done/failed/skipped | Finite state machine |
| Data hierarchy | DO SQLite -> D1 -> Hyperdrive -> Neon | Three-tier, locked |

#### Variables (fill -- changes every run)

| Variable | What Changes |
|----------|-------------|
| Goal target | Which company, which prospect |
| Step results | Output from each CF Worker call |
| Timing | How long each step took |
| Errors | What failed, why |
| Cost | API calls, compute time |
| Position | Where in the chain we are right now |

### IMO (S3)

#### System-level IMO
- **Input**: Goal definition (company, silo, chain to run)
- **Middle**: Orchestrator decomposes goal -> assigns to line agent -> line agent runs steps in sequence -> each step calls CF Worker -> collects results
- **Output**: Goal completion status + all step results + timing + errors

#### Per-step IMO
- **Input**: Prior step output (or goal payload for first step)
- **Middle**: HTTP fetch to CF Worker endpoint -> wait for response -> validate result
- **Output**: Success payload for next step, OR error that halts the chain

### CTB (S4)

```
50K: Production Line System (the concept)
  40K: Orchestrator Agent (hub -- all decisions)
    30K: Line Agents (one per silo -- chain coordination)
      10K: Steps (individual CF Worker calls)
        5K: Step results (data payloads)
```

### Circle (S5)

- Goal completes -> results feed back to goal status
- Failed steps -> error logged -> strike count incremented
- Strike 3 on same step -> Troubleshoot/Train (Bedrock S6)
- Chain timing tracked -> sigma tightening = optimization working

### Three Primitives (S1)

- **Thing**: Does the agent exist? Does the CF Worker endpoint exist? Does D1 have the data?
- **Flow**: Does the goal reach the orchestrator? Does the orchestrator reach the line agent? Does the line agent reach the CF Worker?
- **Change**: Does the CF Worker produce the expected output? Does the step state transition correctly? Does the goal status update?

---

## Structural Comparison: Paperclip Patterns -> CF Agents Implementation

| Paperclip (57 tables) | CF Agents (our design) | Storage |
|---|---|---|
| companies | Business silos (SVG, RE, Personal) | Config constant |
| agents | Line Agent classes (one DO per silo) | Durable Object |
| agent_runtime_state | Agent SQLite -- step position, status | DO SQLite |
| goals | Goals table -- what to accomplish | D1 |
| issues | Steps table -- each process in chain | D1 |
| heartbeat_runs | CF Agent alarms -- scheduled execution | DO alarms |
| heartbeat_run_events | Step execution log | DO SQLite |
| budget_policies | Cost limits per agent | DO SQLite |
| cost_events | Cost per step | DO SQLite |
| approvals | Human gate before critical steps | D1 |
| activity_log | Agent event log | DO SQLite |
| projects | Process chains (outreach, sales, etc.) | Config constant |

Tables we skip: auth, invites, memberships, logos, plugins, documents, labels, workspaces (single operator, not needed).

---

## Agent Classes

### OrchestratorAgent (Hub)
- Receives goals
- Decomposes into silo chains
- Dispatches to line agents via RPC
- Tracks overall goal status
- Reports to Mission Control UI via WebSocket

### LineAgent (Spoke -- one per silo)
- Receives chain to execute
- Runs steps in sequence
- Calls CF Workers via fetch
- Reports step status back to orchestrator
- Persists chain state in SQLite
- Handles retries and failure

### Step Execution
- Not a separate agent -- a function within LineAgent
- fetch(worker_url) -> validate response -> update state -> next step or halt

---

## D1 Schema (Working Data)

### goals
| Column | Type | Purpose |
|--------|------|---------|
| goal_id | TEXT PK | UUID |
| company_name | TEXT | Target company |
| sovereign_id | TEXT | Links to CL spine |
| silo | TEXT | Which silo (outreach, sales, client, cl) |
| chain | TEXT | JSON array of process IDs |
| status | TEXT | pending/running/done/failed |
| created_at | TEXT | Timestamp |
| completed_at | TEXT | Timestamp |

### steps
| Column | Type | Purpose |
|--------|------|---------|
| step_id | TEXT PK | UUID |
| goal_id | TEXT FK | Parent goal |
| process_id | TEXT | e.g., "010-seed-d1" |
| sequence | INTEGER | Order in chain |
| status | TEXT | pending/running/done/failed/skipped |
| input_payload | TEXT | JSON -- what was passed in |
| output_payload | TEXT | JSON -- what came back |
| error_message | TEXT | If failed |
| started_at | TEXT | Timestamp |
| completed_at | TEXT | Timestamp |
| duration_ms | INTEGER | How long |
| cost_usd | REAL | If applicable |

### steps_error
| Column | Type | Purpose |
|--------|------|---------|
| error_id | TEXT PK | UUID |
| step_id | TEXT FK | Which step |
| error_code | TEXT | Categorized |
| error_message | TEXT | Detail |
| strike_count | INTEGER | How many times this has failed |
| created_at | TEXT | Timestamp |

---

## Visual UI Specification

### Production Line Page (Mission Control)

Layout: Horizontal pipeline per silo, vertically stacked.

```
+-------------------------------------------------------------------+
| GOAL: Prepare Acme Corp for Sales          [RUNNING] [3/17 done]  |
+-------------------------------------------------------------------+
|                                                                   |
| OUTREACH ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  |
|   [Seed]-->[People]-->[Email]-->[LinkedIn]-->[Blog]-->            |
|    done     done      running   pending     pending               |
|                                                                   |
| SALES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  |
|   [Portal]-->[Presentation]                                       |
|    pending    pending                                             |
|                                                                   |
| CLIENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  |
|   [Intake]-->[Export]-->[Portal]                                   |
|    pending    pending    pending                                  |
+-------------------------------------------------------------------+
| AGENTS: Orchestrator [active] | Outreach [running] | Sales [idle] |
| COST: $0.12 | DURATION: 4m 32s | STRIKES: 0                      |
+-------------------------------------------------------------------+
```

Each node is clickable -> shows logs, input/output, timing, errors.
Real-time updates via WebSocket from Durable Objects.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-02 |
| Version | 1.0.0 |
| BAR | BAR-196 |
| Status | BUILD |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |

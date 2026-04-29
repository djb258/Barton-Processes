# Production Line — CF Agents Orchestration

**BAR-196** | Status: BUILD | Priority: Urgent

## What This Is

The foreman layer for Barton-Processes. Uses Cloudflare Agents SDK (Durable Objects) to orchestrate 17+ processes across 5 silos in a visible production line.

## Architecture

```
HUB: Orchestrator Agent (Durable Object)
  |
  +-- SPOKE: Outreach Line Agent
  |     010 -> 200 -> 201 -> 202 -> 300 -> 400 -> 500 -> 600 -> 700
  |
  +-- SPOKE: Sales Line Agent
  |     900 -> BAR-194 presentation
  |
  +-- SPOKE: Client Line Agent
  |     810 -> 820 -> 830
  |
  +-- SPOKE: CL Line Agent
  |     100 -> 800
  |
  +-- SPOKE: IMO-Creator Line Agent
        000 -> 050
```

Hub = all logic, all decisions. Spokes = chain coordination. Leaves = CF Worker calls.

## Data Hierarchy

- **Durable Object SQLite** = agent state (step position, errors, timing, cost)
- **D1** = working data (process inputs/outputs)
- **Hyperdrive -> Neon** = vault (certified results)

## Design Authority

- Foundational Bedrock (law/doctrine/FOUNDATIONAL_BEDROCK.md)
- Hub-Spoke geometry (Bedrock S4)
- IMO per step (Bedrock S3)
- Circle feedback (Bedrock S5)
- Strike 3 rule (Bedrock S6)

## Reference Repos

| Repo | Purpose |
|------|---------|
| djb258/agents | CF Agents SDK (fork of cloudflare/agents) |
| djb258/agents-starter | Starter template |
| djb258/paperclip | Structural patterns reference (NOT runtime) |

## Visual UI

Production line view in Mission Control. Real-time via WebSocket.
Green = done. Yellow = running. Red = failed. Gray = pending.

# Barton-Processes

**The muscle.** Every executable process across the Barton fleet lives here.

## Taxonomy

| Repo Type | Role | Contains | Workers |
|-----------|------|----------|---------|
| Blueprint repos (CL, outreach, sales, client, storage) | Brain | Static schemas, doctrine, definitions | ZERO |
| **barton-processes** (this repo) | **Muscle** | **Every executable process** | **ALL** |

## Structure

Processes live under `factory/` in numbered directories:

```
factory/
├── 001-neon-db-agent/        # CL: DB scripts + CLI agent
├── 002-cl-pipeline/          # CL: Pipeline orchestrator
├── 003-lcs-runtime/          # CL: Cron, matview, signal bridge
├── 004-lcs-delivery/         # CL: Delivery pipeline + adapters
├── 005-lcs-gates/            # CL: Capacity, freshness, suppression
├── 006-dol-refresh/          # Outreach: DOL filing enrichment
├── 007-people-intel/         # Outreach: Contact slot filling
├── 008-blog-monitor/         # Outreach: Blog signal detection
├── 009-talent-flow/          # Outreach: Executive movement
├── 010-outreach-execution/   # Outreach: Execution workers
├── 011-outreach-scripts/     # Outreach: Utility scripts
├── 012-field-monitor/        # Garage: 4 CF Workers
├── 013-client-ai-services/   # Client: MCP server, sidecar, agents
├── 014-client-ui-api/        # Client: API endpoints
├── 015-sales-meeting-service/ # Sales: Meeting service
└── 016-bit-scoring/          # Outreach: BIT signal aggregation
```

## Governance

- **Parent**: imo-creator (Sovereign)
- **Identity**: `law/heir.yaml`
- **Mode**: `law/orbt.yaml`
- **Registry**: `law/process-registry.yaml`
- **Dependencies**: `law/ingress-manifest.yaml`

## BAR

BAR-136 — Build barton-processes repo

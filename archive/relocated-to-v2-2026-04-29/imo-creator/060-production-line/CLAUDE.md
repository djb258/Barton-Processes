# CLAUDE.md --- Process 060: Production Line Engine

## Identity
- **Process:** PROC-060 (Production Line Engine)
- **Business:** imo-creator
- **CTB Position:** factory/imo-creator/060-production-line
- **ORBT:** OPERATE
- **D1 Database:** production-line D1
- **Runtime:** CF Worker + Durable Objects

## Pre-Flight
1. Read PROCESS.md in this directory
2. Read imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md (parent repo)
3. Read imo-creator-v2/law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md (parent repo)
4. Check D1 schema is migrated (migrations/0001_production.sql)
5. Verify line definitions in src/lines.ts match deployed processes

## Two Phases
- **Phase 1: BUILD** --- How processes get created. Altitude descent 50K->5K. See HOW_TO_BUILD_A_PROCESS.md
- **Phase 2: RUN** --- How goals flow through the line. See HOW_TO_RUN_A_PROCESS.md

## Key Architecture
- OrchestratorAgent (hub) routes goals to LineAgent (spokes)
- LineAgent walks dependency graph, calls adapters (HTTP/CLI/SQL/Manual)
- Every step traced (S11). Fleet failures tracked (S13). Sigma per station.
- Builder CANNOT certify own work. Auditor = different engine.
- P(x;theta) = 1 if max_i[C_i(x)/k_i] <= 1 --- the decision function, not opinion.

## API Endpoints
- POST /goals --- submit goal
- GET /goals/:id --- goal + steps + trace + logbook
- POST /goals/:id/certify --- auditor certifies (requires auditor field)
- POST /goals/:id/resume --- resume after repair
- GET /errors --- open fleet failures
- GET /sigma/:station_id --- sigma tracking

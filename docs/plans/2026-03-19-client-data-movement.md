# Client Data Movement Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build three CF Workers (800, 810, 820) that handle client data minting, intake, and vendor export in Barton-Processes.

**Architecture:** CF Workers with D1 edge workspace and Neon vault. Data enters D1 (working layer), gets validated and promoted within D1, then certified records vault to Neon. Vendor exports read from D1. Follows the same SEED/WORK/PUSH pattern established by Process 200.

**Tech Stack:** Cloudflare Workers, D1, KV, Neon PostgreSQL (@neondatabase/serverless), TypeScript, Zod

**Spec:** `docs/specs/2026-03-19-client-data-movement-design.md`

**Blueprint Source:** `djb258/client` — column registry at `src/data/db/registry/clnt_column_registry.yml`

---

## File Structure

### Process 800 — Client Mint

```
factory/800-client-mint/
├── heir.yaml
├── wrangler.toml
├── package.json
├── tsconfig.json
└── src/
    ├── index.ts                         # CF Worker entry — HTTP only (manual trigger)
    ├── mint.ts                          # Read CL sovereign → mint client_id → write D1
    ├── vault.ts                         # Promote certified client to Neon vault
    └── migrations/
        ├── 001_d1_client_tables.sql     # D1 working tables (client + client_error)
        └── 002_neon_clnt_client.sql     # Neon vault table (clnt.client)
```

### Process 810 — Client Data Intake

```
factory/810-client-intake/
├── heir.yaml
├── wrangler.toml
├── package.json
├── tsconfig.json
└── src/
    ├── index.ts                         # CF Worker entry — HTTP endpoint for CSV/API
    ├── validate.ts                      # Zod schemas per spoke (S2-S5)
    ├── stage.ts                         # Write validated data to D1 staging tables
    ├── promote.ts                       # Promote staging → D1 canonical working tables
    ├── vault.ts                         # Push certified records to Neon vault
    └── migrations/
        ├── 001_d1_intake_tables.sql     # D1 staging + canonical working tables (all 16)
        └── 002_neon_clnt_all.sql        # Neon vault tables (full clnt schema)
```

### Process 820 — Vendor Export

```
factory/820-vendor-export/
├── heir.yaml
├── wrangler.toml
├── package.json
├── tsconfig.json
└── src/
    ├── index.ts                         # CF Worker entry — cron + HTTP
    ├── export.ts                        # Read D1 canonical → apply blueprint → generate file
    ├── blueprints.ts                    # Load vendor mappings from KV
    └── migrations/
        └── 001_d1_export_tables.sql     # D1 export log + error tracking
```

---

## Task 1: Process 800 — Client Mint (Scaffold + D1 Schema)

**Files:**
- Create: `factory/800-client-mint/heir.yaml`
- Create: `factory/800-client-mint/wrangler.toml`
- Create: `factory/800-client-mint/package.json`
- Create: `factory/800-client-mint/tsconfig.json`
- Create: `factory/800-client-mint/src/migrations/001_d1_client_tables.sql`

- [ ] **Step 1: Create heir.yaml**

```yaml
# HEIR — 800 Client Mint
process_id: "PROC-CLIENT-MINT"
process_number: "800"
name: "Client Mint"
blueprint_owner: "client"
runtime: "cloudflare-workers"
status: "build"
sovereign_ref: "imo-creator-v2"
governing_engine: "law/doctrine/TIER0_DOCTRINE.md"
ctb_placement: "leaf"
cc_layer: "CC-04"
imo_topology: "middle"

services:
  - "CF Worker (manual trigger)"
  - "Neon via Hyperdrive"
  - "D1 (working tables)"
secrets_provider: "doppler"

two_question_intake:
  what_triggers: "Human provides CL sovereign ID"
  how_do_we_get_it: "Read company identity from Neon vault (CL schema)"

acceptance_criteria:
  - "Receives CL sovereign ID, mints new client_id in D1"
  - "Populates clnt.client from CL sovereign data"
  - "Links client_id back to CL sovereign ID"
  - "Promotes certified client to Neon vault"
  - "Errors write to clnt.client_error in D1"
  - "Duplicate sovereign ID detection halts with error"

depends_on: []  # Independent — reads from CL sovereign in Neon
feeds: [810]    # Client Data Intake needs a client_id to attach data to
```

- [ ] **Step 2: Create wrangler.toml**

```toml
name = "client-mint-800"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[[d1_databases]]
binding = "D1"
database_name = "client-mint-800"
database_id = ""  # TODO: wrangler d1 create client-mint-800

[vars]
# NEON_URL set via wrangler secret put
```

- [ ] **Step 3: Create package.json**

```json
{
  "name": "client-mint-800",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "d1:create": "wrangler d1 create client-mint-800",
    "d1:migrate": "wrangler d1 execute client-mint-800 --file=src/migrations/001_d1_client_tables.sql",
    "neon:migrate": "psql $DATABASE_URL -f src/migrations/002_neon_clnt_client.sql"
  },
  "dependencies": {
    "@neondatabase/serverless": "^0.10.0"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20241218.0",
    "typescript": "^5.7.0",
    "wrangler": "^4.0.0"
  }
}
```

- [ ] **Step 4: Create tsconfig.json** (same as 200-people-worker)

- [ ] **Step 5: Create D1 migration — `001_d1_client_tables.sql`**

D1 mirrors the clnt schema for S1 Hub. Types simplified for SQLite.

```sql
-- Process 800 — D1 Working Tables
-- D1 = working layer. Neon = vault.
-- Client identity + error tracking.

CREATE TABLE IF NOT EXISTS client (
  client_id           TEXT PRIMARY KEY,
  sovereign_id        TEXT NOT NULL,
  legal_name          TEXT NOT NULL,
  fein                TEXT,
  domicile_state      TEXT,
  effective_date      TEXT,
  status              TEXT NOT NULL DEFAULT 'active',
  source              TEXT,
  version             INTEGER NOT NULL DEFAULT 1,
  domain              TEXT,
  label_override      TEXT,
  logo_url            TEXT,
  color_primary       TEXT,
  color_accent        TEXT,
  feature_flags       TEXT NOT NULL DEFAULT '{}',
  dashboard_blocks    TEXT NOT NULL DEFAULT '[]',
  created_at          TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
  vaulted_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_client_sovereign ON client(sovereign_id);
CREATE INDEX IF NOT EXISTS idx_client_status ON client(status);

CREATE TABLE IF NOT EXISTS client_error (
  client_error_id     TEXT PRIMARY KEY,
  client_id           TEXT NOT NULL,
  source_entity       TEXT NOT NULL,
  source_id           TEXT,
  error_code          TEXT NOT NULL,
  error_message       TEXT NOT NULL,
  severity            TEXT NOT NULL DEFAULT 'error',
  status              TEXT NOT NULL DEFAULT 'open',
  context             TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_client_error_client ON client_error(client_id);
CREATE INDEX IF NOT EXISTS idx_client_error_status ON client_error(status);
```

- [ ] **Step 6: Commit scaffold**

```bash
git add factory/800-client-mint/
git commit -m "feat: scaffold 800-client-mint — heir, wrangler, D1 schema"
```

---

## Task 2: Process 800 — Client Mint (Worker Code)

**Files:**
- Create: `factory/800-client-mint/src/index.ts`
- Create: `factory/800-client-mint/src/mint.ts`
- Create: `factory/800-client-mint/src/vault.ts`
- Create: `factory/800-client-mint/src/migrations/002_neon_clnt_client.sql`

- [ ] **Step 1: Create mint.ts — read CL sovereign, mint client_id**

Core logic: receive sovereign_id → query Neon CL schema for company identity → generate client_id UUID → write to D1 client table → return new client_id.

Checks: duplicate sovereign_id in D1 → halt with error. Missing sovereign in Neon → halt with error.

- [ ] **Step 2: Create vault.ts — promote D1 client to Neon**

Read from D1 where vaulted_at IS NULL → INSERT into Neon clnt.client via Hyperdrive → update D1 vaulted_at timestamp.

- [ ] **Step 3: Create index.ts — CF Worker entry**

HTTP endpoints:
- `GET /health` — health check
- `GET /status` — list clients in D1, vaulted/unvaulted counts
- `POST /mint` — body: `{ sovereign_id: string }` → mint new client
- `POST /vault` — promote all unvaulted clients to Neon
- `GET /client/:id` — lookup client by client_id

- [ ] **Step 4: Create Neon migration — `002_neon_clnt_client.sql`**

Creates `clnt.client` in Neon vault matching the blueprint column registry. This only runs once during initial setup.

- [ ] **Step 5: Commit worker code**

```bash
git add factory/800-client-mint/src/
git commit -m "feat: 800-client-mint worker — mint, vault, HTTP endpoints"
```

---

## Task 3: Process 810 — Client Data Intake (Scaffold + D1 Schema)

**Files:**
- Create: `factory/810-client-intake/heir.yaml`
- Create: `factory/810-client-intake/wrangler.toml`
- Create: `factory/810-client-intake/package.json`
- Create: `factory/810-client-intake/tsconfig.json`
- Create: `factory/810-client-intake/src/migrations/001_d1_intake_tables.sql`

- [ ] **Step 1: Create heir.yaml**

Same pattern as 800. Process ID: PROC-CLIENT-DATA-INTAKE. Trigger: CSV upload or API POST. Feeds: 820 (vendor export needs canonical data).

- [ ] **Step 2: Create wrangler.toml, package.json, tsconfig.json**

Same pattern as 800. D1 database: `client-intake-810`. Add `zod` as dependency.

- [ ] **Step 3: Create D1 migration — `001_d1_intake_tables.sql`**

All 16 tables from the client blueprint column registry, adapted for D1/SQLite types. Organized by spoke:
- S1 Hub: client (read from 800), client_error
- S2 Plan: plan, plan_error, plan_quote
- S3 Employee: person, employee_error, election, enrollment_intake, intake_record
- S4 Vendor: vendor, vendor_error, external_identity_map, invoice
- S5 Service: service_request, service_error

Plus staging tables for intake processing.

- [ ] **Step 4: Commit scaffold**

```bash
git add factory/810-client-intake/
git commit -m "feat: scaffold 810-client-intake — heir, wrangler, D1 schema (16 tables)"
```

---

## Task 4: Process 810 — Client Data Intake (Worker Code)

**Files:**
- Create: `factory/810-client-intake/src/index.ts`
- Create: `factory/810-client-intake/src/validate.ts`
- Create: `factory/810-client-intake/src/stage.ts`
- Create: `factory/810-client-intake/src/promote.ts`
- Create: `factory/810-client-intake/src/vault.ts`
- Create: `factory/810-client-intake/src/migrations/002_neon_clnt_all.sql`

- [ ] **Step 1: Create validate.ts — Zod schemas per spoke**

One Zod schema per spoke's intake format. Derived from the column registry. Validates at boundary — rejects malformed data before staging.

- [ ] **Step 2: Create stage.ts — write validated data to D1 staging**

Write to enrollment_intake (batch header) + intake_record (individual rows). INSERT-only on intake_record (immutable).

- [ ] **Step 3: Create promote.ts — promote staging to D1 canonical**

Read from staging → validate business rules → INSERT/UPSERT to canonical working tables in D1. Route by spoke identifier in payload.

- [ ] **Step 4: Create vault.ts — push certified records to Neon**

Same pattern as 800. Read D1 canonical where vaulted_at IS NULL → INSERT into Neon clnt.* → update vaulted_at.

- [ ] **Step 5: Create index.ts — CF Worker entry**

HTTP endpoints:
- `GET /health` — health check
- `GET /status` — intake summary (staged/promoted/vaulted counts per spoke)
- `POST /intake` — body: `{ client_id, spoke, data[] }` → validate → stage → promote
- `POST /vault` — promote all unvaulted records to Neon
- `GET /errors/:client_id` — error summary per spoke

- [ ] **Step 6: Create Neon migration — `002_neon_clnt_all.sql`**

Full clnt schema in Neon (all 16 tables). Run once during setup. Matches blueprint column registry exactly.

- [ ] **Step 7: Commit worker code**

```bash
git add factory/810-client-intake/src/
git commit -m "feat: 810-client-intake worker — validate, stage, promote, vault"
```

---

## Task 5: Process 820 — Vendor Export (Full Build)

**Files:**
- Create: `factory/820-vendor-export/heir.yaml`
- Create: `factory/820-vendor-export/wrangler.toml`
- Create: `factory/820-vendor-export/package.json`
- Create: `factory/820-vendor-export/tsconfig.json`
- Create: `factory/820-vendor-export/src/index.ts`
- Create: `factory/820-vendor-export/src/export.ts`
- Create: `factory/820-vendor-export/src/blueprints.ts`
- Create: `factory/820-vendor-export/src/migrations/001_d1_export_tables.sql`

- [ ] **Step 1: Create heir.yaml, wrangler.toml, package.json, tsconfig.json**

Cron-triggered. D1 database: `vendor-export-820`. KV namespace for vendor blueprints. Cron: daily for TPA/PBM, weekly for carriers.

- [ ] **Step 2: Create D1 migration — export log + errors**

```sql
CREATE TABLE IF NOT EXISTS export_log (
  export_id       TEXT PRIMARY KEY,
  client_id       TEXT NOT NULL,
  vendor_id       TEXT NOT NULL,
  blueprint_id    TEXT NOT NULL,
  record_count    INTEGER NOT NULL,
  status          TEXT NOT NULL DEFAULT 'completed',
  exported_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS export_error (
  error_id        TEXT PRIMARY KEY,
  client_id       TEXT NOT NULL,
  vendor_id       TEXT,
  error_code      TEXT NOT NULL,
  error_message   TEXT NOT NULL,
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- [ ] **Step 3: Create blueprints.ts — load vendor mappings from KV**

Read vendor blueprint JSON from KV. Maps internal column names to vendor-specific field names. Blueprints sourced from client repo `db/vendor_blueprints/*.mapping.json`.

- [ ] **Step 4: Create export.ts — generate vendor file**

Read D1 canonical (person, election, plan, vendor, external_identity_map) → apply blueprint mapping → translate internal UUIDs to external IDs via external_identity_map → generate output records.

- [ ] **Step 5: Create index.ts — CF Worker entry**

Cron handler + HTTP:
- `scheduled()` — run daily/weekly exports based on schedule config
- `GET /health` — health check
- `GET /status` — export log summary
- `POST /export` — body: `{ client_id, vendor_id }` → manual export trigger
- `GET /log/:client_id` — export history

- [ ] **Step 6: Commit**

```bash
git add factory/820-vendor-export/
git commit -m "feat: 820-vendor-export — blueprint mapping, cron export, KV config"
```

---

## Task 6: Update Registry + Ingress Manifest

**Files:**
- Modify: `law/process-registry.yaml`
- Modify: `law/ingress-manifest.yaml`

- [ ] **Step 1: Add 800, 810, 820 to process-registry.yaml**

```yaml
  # ── client (800-820) ──────────────────────────────────────────

  - number: "800"
    id: "PROC-CLIENT-MINT"
    name: "Client Mint"
    source_repo: "client"
    runtime: "cloudflare-workers"
    status: "build"
    description: "Receives CL sovereign ID → mints client_id → populates clnt.client → vaults to Neon"

  - number: "810"
    id: "PROC-CLIENT-DATA-INTAKE"
    name: "Client Data Intake"
    source_repo: "client"
    runtime: "cloudflare-workers"
    status: "build"
    description: "CSV/API intake → Zod validate → D1 staging → promote to canonical → vault to Neon"

  - number: "820"
    id: "PROC-VENDOR-EXPORT"
    name: "Vendor Export"
    source_repo: "client"
    runtime: "cloudflare-workers"
    status: "build"
    description: "Cron — reads D1 canonical → applies vendor blueprint → generates export files"
```

- [ ] **Step 2: Update ingress-manifest.yaml**

Add clnt schema dependency for 800-820. Add CL schema read dependency for 800.

- [ ] **Step 3: Commit**

```bash
git add law/process-registry.yaml law/ingress-manifest.yaml
git commit -m "ops: register 800-820 client processes in registry + manifest"
```

---

## Task 7: Update law/heir.yaml + law/orbt.yaml

**Files:**
- Modify: `law/heir.yaml`
- Modify: `law/orbt.yaml`

- [ ] **Step 1: Add 800-820 to heir.yaml processes list**

- [ ] **Step 2: Update orbt.yaml — note client processes added**

- [ ] **Step 3: Commit**

```bash
git add law/heir.yaml law/orbt.yaml
git commit -m "ops: update HEIR/ORBT with 800-820 client processes"
```

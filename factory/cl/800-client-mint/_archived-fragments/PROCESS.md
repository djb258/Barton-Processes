> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# PROCESS: Client Mint
## Converts a company from the outreach pipeline into a formal client record — the birth certificate for every client relationship.
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

_What is this thing? The constants that never change regardless of when you read this._

| Field | Value |
|-------|-------|
| Process ID | PROC-800 |
| Name | Client Mint |
| Business Silo | svg-agency |
| Sub-Hub | cl |
| CTB Position | factory/cl/800-client-mint |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | not deployed |
| BAR Reference | BAR-38, BAR-87, BAR-178 |
| Deployed URL | https://client-mint-800.svg-outreach.workers.dev |
| Cron | manual |
| Runtime | CF Worker |

---

## 2. WHY THIS EXISTS

_What breaks without it. What business outcome it serves. If you can't answer this, the process shouldn't exist._

Without Client Mint, there is no formal client record. A company sitting in the CL outreach pipeline is a lead, not a client. This process is the gate that converts a qualified company into a minted client with its own identity (client_id), which every downstream process (810 Client Intake, portal, billing) requires to function. No mint, no client. No client, no revenue.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock S7)
1. **"What triggers this?"** — Manual POST /mint with a CL sovereign_id
2. **"How do we get it?"** — Human provides sovereign_id; company identity read from Neon vault (cl.company_identity)

### Input
- CL sovereign_id (provided in POST body)
- Company identity record from Neon vault (cl.company_identity table)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | POST /mint {sovereign_id} | Validate sovereign_id is present and well-formed | Validated sovereign_id or 400 error | CF Worker validation |
| 2 | sovereign_id | Check D1 client table for duplicate sovereign_id | Pass (no duplicate) or DUPLICATE_SOVEREIGN error | D1 query |
| 3 | sovereign_id | Read company identity from Neon vault (cl.company_identity) | Company identity record or SOVEREIGN_NOT_FOUND error | Neon via NEON_URL |
| 4 | Company identity record | Mint new client_id, write client record to D1 client table | client_id + client record in D1 | D1 insert |
| 5 | client_id + client record | Return minted client record to caller | JSON response with client_id | CF Worker response |

### Output
- Minted client record in D1 (client table) with unique client_id linked to CL sovereign_id
- On promotion: certified client written to Neon vault (clnt.client)
- Errors written to D1 client_error table (and Neon clnt.client_error on vault promotion)
- Downstream: 810 Client Intake reads client_id to begin intake workflow

### Circle (Bedrock S5)
- Minted client_id feeds downstream to 810 Client Intake
- Errors (DUPLICATE_SOVEREIGN, SOVEREIGN_NOT_FOUND, VAULT_FAILED) write to client_error table, surfaced via GET /status
- Vault promotion (POST /vault) closes the loop by persisting certified clients back to Neon, making them permanent
- GET /client/:id provides read-back verification that the mint succeeded

---

## 4. WHAT IT GRABS OFF THE WALL

_Every tool, database, integration, API, secret, and agent this process touches._

### Blueprint Reference

| Field | Value |
|-------|-------|
| Blueprint | company-lifecycle-cl |
| OSAM Section | doctrine/OSAM.md + client/doctrine/OSAM.md (crosses boundary) |
| Snap-On Toolbox | law/SNAP_ON_TOOLBOX.yaml |

### Snap-On Toolbox Tools

| Sub-Hub # | Tool | What It Does Here |
|-----------|------|-------------------|
| 11-structured-data | Cloudflare D1 | Working client table + client_error table |
| 06-api-layer | Hono | REST endpoints: /mint, /vault, /client/:id, /health, /status |

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| client-mint-800 (D1) | D1 | TBD (not created yet) | READ / WRITE | client table (minted records), client_error table (error log) |
| Neon PostgreSQL | NEON_URL | vault | READ | cl.company_identity — source company data |
| Neon PostgreSQL | NEON_URL | vault | WRITE | clnt.client + clnt.client_error — promoted certified clients |

### Tools & Integrations (Snap-On Toolbox references — see law/SNAP_ON_TOOLBOX.yaml for vendor details)

| Item | Snap-On Sub-Hub | Cost Tier | Credentials | What It Does |
|------|----------------|-----------|-------------|-------------|
| Cloudflare D1 | 11-structured-data | Free | D1 binding | Working data for minted clients + error table |
| Hono (CF Worker) | 06-api-layer | Free | none | REST endpoint routing |
| Neon PostgreSQL | (vault vendor) | Cheap | NEON_URL | Vault reads (cl.company_identity) and promotion writes (clnt.*) |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| NEON_URL | svg-outreach | production | Steps 3 (read CL identity), vault promotion (write clnt) |

**Tool Priority (Well Drinks First):**
1. D1 for all working data (free) — client table, client_error table
2. Neon reads for source company identity (cheap — vault only)
3. Neon writes for promotion only (cheap — certified clients only)

---

## 5. OSAM — Where the Data Lives

_The plumbing. Which tables this process reads, writes, joins._

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| cl.company_identity (Neon) | Company name, domain, metadata from outreach pipeline | sovereign_id |
| D1: client | Previously minted client records (duplicate check) | sovereign_id |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| D1: client | New minted client record (client_id, sovereign_id, company data) | Step 4 — mint |
| D1: client_error | Error records (code, sovereign_id, message, timestamp) | On any failure |
| clnt.client (Neon) | Certified client record | POST /vault promotion |
| clnt.client_error (Neon) | Promoted error records | POST /vault promotion |

### Join Chain

```
cl.company_identity.sovereign_id
  → D1: client (sovereign_id, 1:1 after mint)
  → clnt.client (sovereign_id, 1:1 after promotion)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Direct write to Neon cl.* tables | CL schema is READ ONLY for this process — never write upstream |
| Mint without duplicate check | Would create orphan client_ids — violates data integrity |
| Auto-promotion without explicit POST /vault | Vault writes must be deliberate — CQRS write path |
| Skip error table on failure | No log = fix doesn't exist (Aviation Model) |

### Query Routing

| Question | Table | Column |
|----------|-------|--------|
| Does this company already have a client_id? | D1: client | sovereign_id |
| What company data feeds the mint? | cl.company_identity (Neon) | sovereign_id |
| What errors occurred during minting? | D1: client_error | error_code |
| Is this client promoted to vault? | clnt.client (Neon) | sovereign_id |

---

## 6. CONSTANTS & VARIABLES (Bedrock S2)

### Constants (structure — never changes)

_What is fixed regardless of what data flows through._

- sovereign_id is the universal link between CL pipeline and minted client
- client_id is generated at mint time — one per sovereign_id, never reused
- D1 is working data; Neon is vault (SEED-WORK-PUSH lifecycle)
- CQRS: client table (canonical) + client_error table (error) per workspace
- Error codes are fixed: DUPLICATE_SOVEREIGN, SOVEREIGN_NOT_FOUND, VAULT_FAILED
- Endpoints are fixed: GET /health, GET /status, POST /mint, POST /vault, GET /client/:id
- Manual trigger only — no cron, no automated runs

### Variables (fill — changes every run)

_The values that fill the constants. Different every execution._

- Which sovereign_id is being minted
- What company data comes back from cl.company_identity
- Whether the sovereign_id already exists (duplicate check result)
- The generated client_id value
- Error messages and timestamps

---

## 7. STOP CONDITIONS

_When to halt. Not optional._

| Condition | Action |
|-----------|--------|
| sovereign_id missing or malformed in POST body | HALT — return 400, do not query anything |
| DUPLICATE_SOVEREIGN — client already exists for this sovereign_id | HALT — return error with existing client_id |
| SOVEREIGN_NOT_FOUND — cl.company_identity has no record | HALT — return error, cannot mint without source data |
| VAULT_FAILED — Neon write fails during promotion | HALT — client stays in D1, log error, do not retry automatically |
| Neon connection failure on read | HALT — cannot verify source, do not mint blind |
| D1 write failure | HALT — log to error table if possible, return 500 |
| Strike 3 on same failure | Troubleshoot/Train — produce Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| CL company lifecycle (Neon vault) | cl.company_identity with sovereign_id records | DONE |
| Neon vault access | NEON_URL secret in Doppler | DONE |
| D1 database: client-mint-800 | Working tables for client + client_error | PENDING — database_id not set |
| Auth on endpoints | Authentication layer for POST /mint, POST /vault | PENDING — no auth configured |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| 810 Client Intake | client_id must exist in D1 client table before intake can begin |

---

## 9. SMOKE TEST

_Executable verification. Numbered steps with expected output._

```
1. GET /health → expected: { "status": "ok" }
2. POST /mint { "sovereign_id": "test-123" } → expected: 200 with minted client_id (or SOVEREIGN_NOT_FOUND if test ID doesn't exist in Neon)
3. POST /mint { "sovereign_id": "test-123" } (repeat) → expected: DUPLICATE_SOVEREIGN error
4. GET /client/:id (using client_id from step 2) → expected: full client record
5. GET /status → expected: summary of minted clients and errors
6. POST /vault { "client_id": "<from step 2>" } → expected: 200, client promoted to Neon clnt.client
```

**Three Primitives Check (Bedrock S1):**
1. **Thing:** D1 database exists? Neon cl.company_identity table accessible? Worker deployed?
2. **Flow:** sovereign_id reaches Neon query? Company data reaches D1 insert? Errors reach client_error?
3. **Change:** Company identity correctly transformed into client record? client_id generated and linked?

If any fails — that's the break. Don't guess. Run the Troubleshooting Loop (Bedrock S6).

---

## 10. ANALYTICS

_What gets measured. All values BASELINE until first production run._

### Metrics

| Metric | Type | Baseline | First Run | Notes |
|--------|------|----------|-----------|-------|
| Clients minted | count | BASELINE | — | Successful POST /mint completions |
| Duplicate rejections | count | BASELINE | — | DUPLICATE_SOVEREIGN errors |
| Sovereign lookups | count | BASELINE | — | Neon cl.company_identity reads |
| Vault promotions | count | BASELINE | — | Successful POST /vault completions |
| Error rate | % | BASELINE | — | Total errors / total mint attempts |
| Mint latency | ms | BASELINE | — | Average time from POST /mint to response |

### Tool Scorecard

| Tool | Expected | Actual | Status |
|------|----------|--------|--------|
| D1 (client-mint-800) | Available | BASELINE | — |
| Neon (cl.company_identity) | Available | BASELINE | — |
| Neon (clnt.* vault) | Available | BASELINE | — |
| Hono endpoints | Responding | BASELINE | — |

### Sigma Tracking

| Run Date | Metric | Value | Sigma Direction | Notes |
|----------|--------|-------|----------------|-------|
| — | — | — | — | _No runs yet_ |

### ORBT Gate Rule

- **Sigma tightening** = real constant. Lock it.
- **Sigma flat** = phantom constant. Investigate.
- **Sigma expanding** = broken prior constant. Back-propagate and fix.
- **Strike 3 on same metric** = Troubleshoot/Train, not another repair.

---

## 11. LOGBOOK

_Append-only. Read first, write last. No exceptions. (Bedrock S8)_

### 2026-03-29 — Process documentation created

**ORBT:** BUILD
**Trigger:** Documentation pass
**Records processed:** 0
**Errors:** 0
**Tools used:** none
**Result:** PROCESS.md created from template v2.0.0. D1 database not yet created. No auth on endpoints. Worker not deployed.
**Learnings:** Upstream CL sovereign data confirmed available in Neon vault.
**ORBT after:** BUILD

---

## 12. KNOWN ISSUES & STRIKE TRACKING

_The error history. Append-only — never delete a resolved issue._

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-29 | D1 database_id not set in wrangler.toml | Not yet created | Run: wrangler d1 create client-mint-800, update wrangler.toml | 0 |
| 2 | 2026-03-29 | No auth on endpoints | BUILD phase — auth not implemented | Implement auth middleware before OPERATE | 0 |

**Strike 3 — Troubleshoot/Train — Airworthiness Directive.**
AD goes to ALL processes, not just this one. Update the template, not just this file.

---

## 13. SESSION LOG

_Every session that touches this process. Links to imo-brain for detail._

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-29 | PROCESS.md created from PROCESS_TEMPLATE v2.0.0 | none |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-29 |
| Last Modified | 2026-03-29 |
| Version | 1.1.0 |
| Template Version | 3.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | factory/svg-agency/DATA_FLOW.md |
| Data Flow | factory/svg-agency/DATA_FLOW.md |

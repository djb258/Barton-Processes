# PROCESS-UT — Process 100 Kiddos Working Surface
# BAR-167 | Governance backfill — code shipped, UT doc written post-deploy

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

**What:** The Kiddos Working Surface is the family tracker API and UI for the Barton family. It provides a centralized working surface for academic, sports, and health data across four family members (Dave, Risa, Tyler, Mallory).

**Why:** Family data is scattered across Google Workspace, school portals, sports apps, and health trackers. The Kiddos Working Surface consolidates it under a single sovereign person_id per family member, enabling correlation analysis (sports ↔ health over time, academic trends) that no single external tool provides.

**Who:** Dave Barton (operator, sovereign). Risa Barton (parent operator). Tyler and Mallory Barton (subjects — child records).

**Scope:** kiddos-api CF Worker (Hono) + Kiddos CF Pages (React). Covers /auth/* (Google OAuth), /children/:id (academic, sports, health, correlation), /family/link, /google/* (Drive, Calendar, Gmail). D1 working layer + KV cache + Neon vault archival.

**Out of scope:** SVG Agency data (BRANCH 1), Real Estate data (BRANCH 2), any non-Barton family member records.

**Success metric:** Parent authenticates via Google OAuth, retrieves child records from D1, Google service integrations return scoped data without cross-family token leakage, health data inaccessible without valid Bearer token.

---

## §2 OWNER

**Owner:** Dave Barton — dbarton@svg.agency
**Fixes at 2 AM:** Dave Barton
**Live Dashboard:** N/A (personal app — no Mission Control integration; Kiddos CF Pages is the runtime surface)
**On-call escalation:** N/A (single-owner personal system)

---

## §3 COMPONENT STATUS

| Component | Status | State |
|-----------|--------|-------|
| kiddos-api CF Worker (Hono) | 🟢 | Deployed, routing /auth, /children, /family, /google |
| D1 working database | 🟢 | Canonical store for person, academic, sports, health records |
| KV cache namespace | 🟢 | Derived read cache — populated from D1 |
| Neon vault (Hyperdrive) | 🟢 | Archival layer — receives D1 promotes |
| Google OAuth integration | 🟢 | Parent authentication — Drive/Calendar/Gmail scopes |
| Kiddos CF Pages (React) | 🟢 | Family dashboard UI — consumes kiddos-api |

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 2 — CONTRACT
     ════════════════════════════════════════════════════════════ -->

## §4 IMO

**CTB node:** `barton-enterprises → BRANCH 3: Personal → Kiddos App`
**Hub-Spoke role:** Hub (kiddos-api is the Middle — all logic lives here)
**Altitude:** leaf (10K ft — operational)
**IMO topology:** middle

```
INPUT                    MIDDLE (kiddos-api)              OUTPUT
─────────────────────    ──────────────────────────────   ──────────────────────
Parent HTTP request   →  Hono router                  →  JSON response (child
  + Bearer JWT            auth.ts (OAuth exchange)         records, family data,
  + Google OAuth           routes-children.ts               Google integrations)
  callback                 routes-family.ts             →  D1 write (canonical)
                           routes-google.ts             →  KV populate (cache)
                           db.ts (D1 queries)           →  Neon archive (vault)
                           google.ts (token exchange)
```

**Hub-Spoke geometry:**
- Hub: kiddos-api CF Worker (all processing)
- Spoke 1: D1 database (dumb transport — no logic in D1 itself)
- Spoke 2: KV namespace (dumb cache — no logic)
- Spoke 3: Neon vault (dumb archive)
- Spoke 4: Google OAuth / API (external service — token exchange only)
- Rim: Kiddos CF Pages (read-only view — consumes kiddos-api responses)

**Three Primitives check:**
- Thing: person_id exists in D1 before any child record can be written
- Flow: Bearer JWT flows from OAuth exchange → every authenticated route handler
- Change: D1 write → KV populate → Neon archive (ordered, no skip)

---

## §5 CONTRACT

### person_id (Sovereign Join Key)

| Field | Type | Description |
|-------|------|-------------|
| person_id | string (UUID) | Sovereign identity for every family member |
| name | string | Full name |
| role | enum: parent \| child | Family role |
| google_sub | string | Google OAuth subject identifier (parents only) |
| created_at | ISO 8601 datetime | Record creation timestamp |

All child tables (academic, sports, health, correlation) carry `person_id` as a non-nullable foreign key. Records without person_id are rejected at the D1 write layer.

### Bearer JWT (Auth Token Shape)

| Field | Type | Description |
|-------|------|-------------|
| sub | string | Google OAuth subject (person_id lookup key) |
| email | string | Parent's Google email |
| iat | number | Issued at (Unix epoch) |
| exp | number | Expiration (Unix epoch) |

### Google Service Token (per-parent scoped)

| Field | Type | Description |
|-------|------|-------------|
| access_token | string | Google OAuth access token |
| scope | string | Granted scopes (Drive, Calendar, Gmail) |
| person_id | string | Must match authenticated parent's person_id |

---

## §6 JOIN CONTRACT

**Primary join chain:**
```
Google OAuth (google_sub)
  → person_id lookup in D1 (persons table)
    → academic_records (person_id FK)
    → sports_records (person_id FK)
    → health_records (person_id FK)
    → correlation_surface (derived — joins sports + health on person_id + date)
```

**Family link join:**
```
Parent person_id (authenticated)
  → family_links table (parent_id + child_id)
    → validates parent owns the child_id before write
```

**READ path:** HTTP request → Bearer JWT validation → person_id resolution → D1 query → KV cache check → response
**WRITE path:** HTTP request → Bearer JWT validation → person_id ownership check → D1 write → KV invalidate → Neon archive
**FORBIDDEN:** Direct KV writes from route handlers. Cross-family person_id access. Non-OAuth auth paths.

---

## §7 SCHEMA

### Core Tables (D1)

```sql
-- persons (sovereign)
CREATE TABLE persons (
  person_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('parent', 'child')),
  google_sub TEXT,         -- parents only
  created_at TEXT NOT NULL
);

-- academic_records
CREATE TABLE academic_records (
  record_id TEXT PRIMARY KEY,
  person_id TEXT NOT NULL REFERENCES persons(person_id),
  subject TEXT NOT NULL,
  grade TEXT,
  term TEXT,
  recorded_at TEXT NOT NULL
);

-- sports_records
CREATE TABLE sports_records (
  record_id TEXT PRIMARY KEY,
  person_id TEXT NOT NULL REFERENCES persons(person_id),
  sport TEXT NOT NULL,
  event TEXT,
  result TEXT,
  recorded_at TEXT NOT NULL
);

-- health_records (highest sensitivity tier)
CREATE TABLE health_records (
  record_id TEXT PRIMARY KEY,
  person_id TEXT NOT NULL REFERENCES persons(person_id),
  metric TEXT NOT NULL,
  value TEXT NOT NULL,
  unit TEXT,
  recorded_at TEXT NOT NULL
);

-- family_links
CREATE TABLE family_links (
  link_id TEXT PRIMARY KEY,
  parent_id TEXT NOT NULL REFERENCES persons(person_id),
  child_id TEXT NOT NULL REFERENCES persons(person_id),
  created_at TEXT NOT NULL
);
```

---

## §8 INGEST CHECKLIST

**Adding a new data type (e.g., finance records):**
1. Add table to D1 schema with `person_id` FK (non-nullable)
2. Add route handler to routes-children.ts
3. Confirm Bearer JWT required on route
4. Update heir.yaml acceptance_criteria
5. Update DOCTRINE.md if new sensitivity rules apply

**Kill switch — disable kiddos-api entirely:**
```bash
# Option 1: Undeploy the worker
cd kiddo-app-skeleton/workers/kiddos-api
npx wrangler delete kiddos-api --force

# Option 2: Remove routes (partial disable)
# Remove route handler from index.ts, redeploy
npx wrangler deploy
```

**Kill switch — revoke a parent's access:**
```sql
-- Invalidate google_sub so OAuth lookup fails
UPDATE persons SET google_sub = NULL WHERE person_id = '{person_id}';
-- Also invalidate any active KV session tokens (manual KV delete)
```

---

<!-- ════════════════════════════════════════════════════════════
     CLUSTER 3 — GOVERNANCE
     ════════════════════════════════════════════════════════════ -->

## §9 PERMISSIONS

**READ (child records, family data):**
- Requires: Valid parent Bearer JWT (Google OAuth issued)
- Who: Authenticated parents only
- Exception: N/A — no public read paths on Kiddos API

**WRITE (records, family links):**
- Requires: Valid parent Bearer JWT + person_id ownership validation
- Who: Authenticated parent who owns the target child_id
- Exception: N/A

**EMIT (Google service integrations):**
- Requires: Authenticated parent's own Google OAuth token (scoped to that parent's google_sub)
- Who: Authenticated parent
- Forbidden: Token sharing, token substitution, using one parent's token for another parent's routes

**FORBIDDEN PATHS:**
- Direct D1 writes without Bearer JWT
- Direct KV writes from route handlers (cache is populated only, never written directly)
- /children/:id with unknown person_id → 404 (not empty array)
- Any route exposing SVG Agency (BRANCH 1) or Real Estate (BRANCH 2) data
- Health data (/children/:id/health) without valid Bearer token

**Three Primitives enforcement:**
- Thing: person_id must exist in D1 before any child record write
- Flow: Bearer JWT must transit from OAuth exchange to every authenticated route
- Change: D1 write must precede KV populate; KV populate must precede Neon archive

---

## §10 ERROR HANDLING

| Scenario | Handler | Response |
|----------|---------|----------|
| Unknown person_id on /children/:id | routes-children.ts | 404 Not Found |
| Invalid/expired Bearer JWT | auth.ts middleware | 401 Unauthorized |
| Parent lacks ownership of child_id | routes-family.ts | 403 Forbidden |
| Google OAuth token mismatch | routes-google.ts | 403 Forbidden |
| D1 write failure | db.ts | 500 Internal Server Error + log to error table |
| KV populate failure | Non-fatal | Log warning; D1 remains canonical; next read repopulates |

---

## §11 FCE

**FCE attachment:** BRANCH 3 Personal — Kiddos App node on Barton Enterprises CTB
**FCE runs:** N/A for current scope (personal family tracker — no competitive resource allocation FCE applicable)
**Future FCE candidates:** Health trend analysis (sports ↔ academic correlation), academic performance benchmarking

---

## §12 LBB

**LBB subject:** `processes` (cross-cutting process knowledge)
**Secondary subject:** `system` (infrastructure — CF Worker + D1 + KV + Neon pattern)
**Session log target:** Ingest BAR-167 completion record to LBB after batch closes
**Record template:** HEIR stamp + ORBT state (OPERATE) + acceptance criteria status

---

## §13 BARS REFERENCED

| BAR | Description | Status |
|-----|-------------|--------|
| BAR-167 | Kiddos Working Surface — kiddos-api CF Worker scaffold | CLOSED (code shipped) |

---

## §14 DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| BAR | BAR-167 |
| Version | 1.0.0 |
| Status | OPERATE (governance backfill — code shipped pre-UT) |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Template | law/UNIFIED_TEMPLATE.md v2.0 |
| UT Checklist | law/UT_CHECKLIST.md v1.2.0 — 13 items, all addressed |
| Audit verdict | Pending batch audit (BAR-167 through BAR-48) |
| ctb_node | barton-enterprises → BRANCH 3: Personal → Kiddos App |

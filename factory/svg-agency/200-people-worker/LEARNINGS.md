# Learnings — Process 200: People Worker

## IMO of This Document
- **Input:** Session outcomes — what worked, what broke, what surprised.
- **Middle:** Classify each learning as constant (repeatable pattern) or variable (one-time fix). Validate against C&V test.
- **Output:** Rules that compound. Next session starts smarter than this one ended.

## CTB of This Document
- **Trunk:** Process 200's accumulated operational intelligence.
- **Branch 1:** Locked patterns — validated constants that hold across sessions.
- **Branch 2:** Corrections — mistakes made, root cause, rule added. Strike 3 → escalate to Airworthiness Directive.
- **Branch 3:** Discoveries — new patterns found, pending validation.
- **Leaf:** Individual entries (append-only, newest first).

---

## Locked Patterns (Constants)

_Patterns validated across 2+ sessions. C&V test passed: can name it, can format it, holds under IMO + CTB + Circle._

| # | Pattern | Discovered | Sessions Validated |
|---|---------|------------|-------------------|
| 1 | OSAM is the plumbing contract — read it BEFORE touching code | 2026-03-26 | 1 (pending 2nd validation) |
| 2 | ERDs must come from live D1 introspection, never from docs or assumptions | 2026-03-26 | 1 (pending 2nd validation) |
| 3 | SEED→WORK→PUSH — never query Neon during WORK phase | 2026-03-25 | 2 (validated across sessions) |
| 4 | Well drinks first — free data (staging, about pages) before top shelf (proxy) | 2026-03-26 | 1 (pending 2nd validation) |
| 5 | CF Workers cannot use HTTP CONNECT proxies — need alternate compute for proxy fetches | 2026-03-26 | 1 (pending 2nd validation) |

---

## Corrections (Strike Tracking)

_Mistakes made → root cause → rule added. Track strikes per error class._

| # | Error | Root Cause | Rule Added | Strikes | Date |
|---|-------|-----------|------------|---------|------|
| 1 | Standalone D1 duplicated outreach data (stale on arrival) | Process designed as self-contained worker instead of operating on shared outreach D1 | No standalone D1. Read/write svg-d1-outreach-ops directly. | 1 | 2026-03-25 |
| 2 | 94.8% orphan rate on slot→person join | SEED brought slots but not matching people records | Re-SEED must verify ALL join targets exist. Pressure test after every SEED. | 1 | 2026-03-25 |
| 3 | Guessed column names instead of checking live D1 | Relied on docs/assumptions instead of running `wrangler d1 execute PRAGMA table_info` | Always introspect live D1 before writing queries. | 1 | 2026-03-25 |
| 4 | OSAM says `people_id` but actual join key is `person_unique_id → unique_id` | OSAM written with wrong column name | Needs ADR to correct in barton-outreach-core/doctrine/OSAM.md | 1 | 2026-03-26 |
| 5 | Attempted to query Neon during WORK phase for company name | Forgot SEED→WORK→PUSH rule | Company name comes from cl_company_identity in D1_SPINE (read-only). Never hit Neon. | 1 | 2026-03-25 |
| 6 | CF Worker hit subrequest limit during bulk D1 writes | Individual INSERT statements instead of D1.batch() | Always use D1.batch() for bulk operations (max ~100 statements per batch) | 1 | 2026-03-26 |

**Strike 3 escalation**: If any error reaches 3 strikes, stop repairing. Escalate to Troubleshoot/Train. Produce an Airworthiness Directive (fleet-wide fix) — update the agent's SKILL.md, not just this file.

---

## Discoveries (Pending Validation)

_New patterns observed but not yet validated. Need 2+ sessions to confirm._

| # | Observation | Session | Needs Validation |
|---|-------------|---------|-----------------|
| 1 | intake_people_staging has 24K records but 0 with LinkedIn/email — titles only. Limited value for slot filling. | 2026-03-26 | Confirm in next pass — may need different staging data |
| 2 | About page scraping (Pass 1) finds 0 executives — HTML parsing too simple | 2026-03-26 | Need structured extraction or AI tail for parsing |
| 3 | DataImpulse proxy needs external compute (Python, not CF Worker) for LinkedIn searches | 2026-03-26 | Build Python fetch script that writes to D1 via worker API |

---

## Session Log (Append-Only)

### 2026-03-26 — Full rewrite and SEED fixes

**What worked:**
- D1 introspection via wrangler CLI gave actual schemas (no more guessing)
- D1.batch() solved subrequest limits for bulk writes
- Three SEED fixes: people master 99.7%, slots 100%, agents 32,702 assigned
- Four-pass architecture (well drinks first) is clean

**What broke:**
- CF Workers can't route through DataImpulse HTTP proxy (cf.resolveOverride doesn't work)
- About page parsing regex too simple — 0% fill rate on Pass 1
- Staging data has no LinkedIn URLs or emails — titles only

**Rule added:**
- Proxy fetches need external compute layer, not CF Workers
- Always verify D1 schema via live introspection before coding
- Pressure test ALL joins after every SEED operation

**Ingest to imo-brain?** [x] Yes — 6 documents ingested (83 chunks total)

### 2026-03-25 — Audit and architectural findings

**What worked:**
- PROCESS_AUDIT_TEMPLATE.md (8-gate pre-flight) caught all issues
- Standalone D1 correctly identified as architectural violation

**What broke:**
- Standalone D1 had 98.5% fetch error rate (wrong proxy, stale data)
- ERD and docs all referenced tables that don't exist in outreach D1

**Rule added:**
- No standalone D1 for any process — operate on shared outreach D1
- Read the OSAM before touching ANY process code

**Ingest to imo-brain?** [x] Yes — schema + corrections documents

---

## Three Primitives Check (Per Entry)

Before logging any learning, verify:
1. **Thing:** Does the pattern/correction exist as a nameable structure?
2. **Flow:** Does it apply when data moves through the agent?
3. **Change:** Does it affect transformation outcomes?

If any fails → it's noise, not a learning. Don't log it.

---

## Document Control

| Field | Value |
|-------|-------|
| Agent | Process 200: People Worker |
| Created | 2026-03-26 |
| Last Modified | 2026-03-26 |
| Entries | 2 |
| Locked Patterns | 5 (3 pending 2nd validation) |
| Active Corrections | 6 |

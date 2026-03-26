# PROCESS DOCUMENTATION STANDARD
## Every Process Gets the Same Structure

| Field | Value |
|-------|-------|
| **Status** | ACTIVE — standard for all processes across all business silos |
| **Authority** | PROCESS_MANIFEST_TEMPLATE.md (LOCKED) + Foundational Bedrock |
| **Created** | 2026-03-26 |

---

## The Rule

Every process in `factory/{business-silo}/{NNN}-{name}/` MUST have the full documentation chain. The same structure applies to SVG Agency, Real Estate, Personal, and IMO-Creator processes.

No documentation chain → process is not certified → cannot move to OPR.

---

## Required Files (in read order)

```
factory/{business-silo}/{NNN}-{name}/
├── CLAUDE.md           ← Agent operating instructions
├── MANIFEST.md         ← Logbook (state, issues, session log)
├── OSAM.md             ← Semantic access map (which tables, which joins)
├── ERD.md              ← Entity relationships (actual D1 columns, verified)
├── PRD.md              ← Product requirements (acceptance criteria)
├── heir.yaml           ← Identity (HEIR 8 fields)
├── LEARNINGS.md        ← Agent logbook (locked patterns, corrections, discoveries)
├── D1_SCHEMA.md        ← Full column-level schema from live D1 introspection (when applicable)
├── OSAM_D1_MAPPING.md  ← Neon→D1 table mapping with pressure test results (when applicable)
├── src-v2/             ← Current executable code
└── wrangler-v2.toml    ← CF Worker config (when applicable)
```

**Read order (every session, before touching code):**
1. CLAUDE.md — what this process does, how it works, what tools it uses
2. MANIFEST.md — current state, known issues, session history
3. OSAM.md — which tables it reads, writes, joins, and what's forbidden
4. ERD.md — actual table schemas from live D1
5. PRD.md — acceptance criteria
6. heir.yaml — process identity

**Read first. Write last. No exceptions.**

---

## CLAUDE.md Standard Format

Every process CLAUDE.md MUST contain these sections:

```markdown
# CLAUDE.md — Process {NNN}: {Name}

## Governing Doctrine
- Links to Bedrock, DATA_FLOW.md, ERD.md, D1_SCHEMA.md
- Pre-flight checklist (two-question intake, C&V test, etc.)

## What This Process Does
- 2-3 sentences. What it does, not how.

## Architecture
- D1 bindings (which databases, read vs write)
- NEON rules (vault only, no queries during WORK)
- Gate 0 status (already applied or not)

## How It Works
- Numbered passes/phases with tool priority (well drinks first)
- For each pass: what it reads, what it does, what it writes, what it costs

## The Snap-On Tool
- If the process uses a UT tool, document it here
- Stack, credentials, cost, hit rate, fallback tiers

## Enrichment Priority
- Ranked list: which data sources to use first and why

## Key Joins (verified)
- Table of join paths with match rates from live verification

## Dependencies
- Upstream: what must exist before this process runs
- Downstream: what consumes this process's output

## Worker Config
- URL, cron, batch size, delay settings

## Known Issues
- Table of issues with resolution and strike count
```

---

## ERD.md Standard Format

Every ERD MUST be based on **live D1 introspection**, not documentation or assumptions.

```markdown
# ERD — Process {NNN}: {Name}

| Field | Value |
|-------|-------|
| CTB Position | LEAF — {silo}/{process} |
| OSAM Authority | {path to hub OSAM} |
| Schema Source | Live D1 introspection ({date}) |

## D1 Bindings
- Table of bindings with access level (READ/WRITE/READ ONLY)

## Entity Relationship Diagram
- ASCII box diagram showing actual tables with actual columns
- PK/FK markers
- Row counts from live D1

## FK Chain
- Complete join path from spine through all tables

## Process Access Pattern
- Table of: operation, table, access level, purpose

## Data Counts
- Row counts from live D1 with date verified
```

**Rule: Run `wrangler d1 execute` to get actual schemas. Never copy from old docs.**

---

## OSAM.md Standard Format (Process-Level)

A process OSAM is a SUBSET of the hub OSAM. It declares what THIS process accesses.

```markdown
# OSAM — Process {NNN}: {Name}

## READ Access
- D1_OUTREACH tables with what they provide and join keys
- D1_SPINE tables (if applicable, read-only)

## WRITE Access
- Only tables this process modifies

## Forbidden Paths
- What this process must NEVER do

## Query Routing
- Question → Table → Column mapping
```

---

## LEARNINGS.md Standard Format

From `factory/LEARNINGS_TEMPLATE.md`:

```markdown
# Learnings — {Process Name}

## Locked Patterns (Constants)
- Patterns validated across 2+ sessions

## Corrections (Strike Tracking)
- Mistakes → root cause → rule added. Strike 3 → Airworthiness Directive.

## Discoveries (Pending Validation)
- New patterns, need 2+ sessions to confirm

## Session Log (Append-Only)
- One entry per session. What worked, what broke, rule added.
```

---

## Verification Before Certification

Before a process moves from BLD → OPR:

| Gate | Check |
|------|-------|
| 1 | All required files exist |
| 2 | ERD matches live D1 schema (introspected, not assumed) |
| 3 | OSAM references valid join paths (pressure tested) |
| 4 | CLAUDE.md references correct D1 bindings |
| 5 | Code compiles and deploys (`wrangler deploy --dry-run`) |
| 6 | Health endpoint returns valid data |
| 7 | At least one pass produces results |
| 8 | Session logged in MANIFEST.md and LEARNINGS.md |

Audit template: `law/PROCESS_AUDIT_TEMPLATE.md`

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-26 |
| Authority | PROCESS_MANIFEST_TEMPLATE.md (LOCKED) |
| Applies To | All processes in all business silos |
| Change Protocol | Gate-based (Tier 0 validation) |

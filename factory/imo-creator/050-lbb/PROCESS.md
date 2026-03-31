# PROCESS: LBB (Library Barton Brain)
## One library, Dewey Decimal classification — all knowledge under one roof, categorized by subject hierarchy
### Status: BUILD
### Sub-Hub: imo-creator
### Business: all (serves every sub-hub)

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-050 |
| Name | LBB — Library Barton Brain |
| Sub-Hub | imo-creator (serves all sub-hubs) |
| Business Silo | all — system, outreach, sales, client, research |
| CTB Position | factory/imo-creator/050-lbb |
| Blueprint Repo | imo-creator |
| Blueprint Section | fleet/brain-template/ v1.0.0 — airframe spec |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | 2026-03-31 (D1 created, schema applied, 5 trunks seeded) |
| BAR Reference | — |
| Deployed URL | TBD (CF Worker) |
| Cron | none (ingestion is event-driven or manual) |
| Runtime | CF Worker (Hono) + D1 + Neon (via Hyperdrive) |
| D1 Database | lbb |
| D1 Database ID | 1f8f12ab-9048-4ebc-9f0d-ed06b6c3c243 |

---

## 2. WHY THIS EXISTS

Every process produces knowledge. Session learnings, tool performance, architectural decisions, vendor evaluations, sales IP, client patterns. Right now that knowledge is scattered across imo-brain (62 docs, flat), svg-brain (590 docs, flat), and human memory.

LBB is one library. Dewey Decimal subjects hierarchy. Five trunks: system, outreach, sales, client, research. Every piece of knowledge gets classified on the tree. Query at any altitude — trunk for everything in a domain, leaf for one specific finding.

Without LBB, every new session starts from scratch. The logbook exists but it's not queryable by domain. The brain exists but it's a junk drawer. LBB puts the card catalog on the library.

**Migration path:** imo-brain (62 docs) → parse into 5 trunks by domain tag. svg-brain (32 surviving docs after gap analysis) → all under outreach/sales trunks.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Session learnings, process analytics, vendor evaluations, research findings, manual ingestion. Any process that produces knowledge feeds LBB.
2. **"How do we get it?"** — POST /ingest with content + subject classification. Or migration from existing brains.

### Input
- Session learnings from any process
- Vendor scorecard results from analytics
- Research findings from vendor-scout (sub-hub 27)
- Manual knowledge ingestion (documents, articles, decisions)
- Migration: imo-brain (62 docs) + svg-brain (32 surviving docs)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Raw content + metadata | Classify into subject hierarchy (trunk → branch → leaf). Auto-create leaf subjects if needed. | Subject assignment | 09-llm-router (classification) or manual |
| 2 | Classified content | SHA-256 hash for dedup. If duplicate, skip. | Dedup check | 21-dedup-engine |
| 3 | Unique content | Stamp HEIR identity. Set ORBT to BUILD. Insert into lbb_records. | Record created | 11-structured-data (D1) |
| 4 | New record | Write logbook entry (BUILD, action: "ingested", signed_by). | Logbook updated | 11-structured-data (D1) |
| 5 | Query request | Search by subject, tags, source_type, orbt_mode. Return matching records. | Query results | 11-structured-data (D1) |

### Output
- Classified, deduplicated knowledge records with HEIR identity and ORBT lifecycle
- Queryable at any CTB altitude (trunk → branch → leaf)
- Append-only logbook for every record change

### Circle (Bedrock §5)
Every process run should end with: "What did we learn? Ingest it to LBB." The logbook entry closes the loop. Records in BUILD get human review → OPERATE. Records that prove wrong → REPAIR. Strike 3 → TROUBLESHOOT/TRAIN with fleet-wide AD.

---

## 4. WHAT IT GRABS OFF THE WALL

### Snap-On Toolbox Sub-Hubs (law/SNAP_ON_TOOLBOX.yaml)

| Tool # | Sub-Hub | Recommended Vendor | What It Does In This Process |
|--------|---------|-------------------|------------------------------|
| 11 | structured-data | Cloudflare D1 | All reads and writes (4 tables) |
| 21 | dedup-engine | D1 + Workers | SHA-256 content hash for dedup |
| 09 | llm-router | Workers AI | Subject classification (tail only — deterministic rules first) |
| 06 | api-layer | Hono | HTTP endpoints for ingest, query, lookup |

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| lbb | D1_LBB | 1f8f12ab-9048-4ebc-9f0d-ed06b6c3c243 | READ/WRITE | 4 tables: subjects, records, records_error, logbook |
| Neon (lbb) | HD_LBB (Hyperdrive) | TBD | WRITE (vault) | Permanent storage. D1 syncs weekly via vault-sync. |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| LBB_API_KEY | imo-creator | dev | API authentication |

### Blueprint References

| Blueprint | Repo | Path | What It Defines |
|-----------|------|------|-----------------|
| Brain Template | imo-creator | fleet/brain-template/ v1.0.0 | Airframe: 4 tables, HEIR, ORBT, subjects hierarchy |
| Snap-On Toolbox | imo-creator | law/SNAP_ON_TOOLBOX.yaml v4.0.0 | Tool sub-hubs, vendors |
| D1 Data Dictionary | Barton-Processes | D1_DATA_DICTIONARY.md | AI-ready column reference |

---

## 5. OSAM — Where the Data Lives (AI-Ready Column Reference)

### D1: lbb (1f8f12ab-9048-4ebc-9f0d-ed06b6c3c243)

---

### lbb_subjects — Dewey Decimal hierarchy (5 trunk rows seeded)

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| subject_id | TEXT | PK | UUID | Permanent identity for this subject node |
| parent_id | TEXT | FK → lbb_subjects | UUID or NULL | Parent subject. NULL = root/trunk |
| name | TEXT | NOT NULL, UNIQUE per parent | slug-style | Subject name (e.g., insurance-informatics) |
| description | TEXT | | Free text | What this subject covers. AI classification key. |
| ctb_level | TEXT | NOT NULL, CHECK | trunk/branch/leaf | Position on the CTB |
| sort_order | INTEGER | NOT NULL, DEFAULT 0 | Integer | Display ordering among siblings |
| created_at | TEXT | NOT NULL | ISO 8601 | Record creation timestamp |
| updated_at | TEXT | NOT NULL | ISO 8601 | Last modification timestamp |

**Seeded trunks:**

| subject_id | name | description |
|-----------|------|-------------|
| trunk-system | system | Doctrine, architecture, infrastructure, decisions |
| trunk-outreach | outreach | Company data patterns, enrichment learnings, tool performance |
| trunk-sales | sales | Barton voice, DISC, meeting sequences, objection handling — the 25-year moat |
| trunk-client | client | Intake patterns, vendor mappings, portal usage |
| trunk-research | research | Marketplace findings, vendor evaluations, tool benchmarks |

---

### lbb_records — CANONICAL (library cards)

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| record_id | TEXT | PK | UUID | Permanent HEIR identity. Never changes. |
| sovereign_ref | TEXT | NOT NULL, DEFAULT 'imo-creator' | Enum | Which hangar owns this |
| hub_id | TEXT | NOT NULL, DEFAULT 'lbb' | Enum | Aircraft identifier |
| cc_layer | TEXT | NOT NULL, DEFAULT 'CC-03' | Enum | Authority level (context) |
| subject_id | TEXT | NOT NULL, FK → lbb_subjects | UUID | CTB position — which subject this record belongs to |
| ctb_placement | TEXT | NOT NULL, DEFAULT 'leaf' | Enum | Always leaf for individual records |
| title | TEXT | NOT NULL | Free text | Human-readable title |
| content | TEXT | NOT NULL | Free text | Full content — the actual knowledge |
| summary | TEXT | | Free text | Condensed version (AI or human) |
| content_hash | TEXT | NOT NULL, UNIQUE | SHA-256 | Dedup key — prevents duplicate content |
| content_format | TEXT | NOT NULL, DEFAULT 'text' | text/markdown/html/transcript | Content format |
| source_url | TEXT | | URL | Origin URL or file path |
| source_type | TEXT | NOT NULL, DEFAULT 'web' | web/pdf/video/podcast/document/manual/search | Source classification |
| source_name | TEXT | | Free text | Human-readable source name |
| fetched_by | TEXT | | Free text | Which UT sub-hub or method fetched this |
| orbt_mode | TEXT | NOT NULL, DEFAULT 'BUILD' | BUILD/OPERATE/REPAIR/TROUBLESHOOT_TRAIN | Lifecycle state |
| strike_count | INTEGER | NOT NULL, DEFAULT 0 | 0-3 | Error recurrence. 3 = escalate. |
| tags | TEXT | NOT NULL, DEFAULT '[]' | JSON array | Freeform tags for filtering |
| found_at | TEXT | NOT NULL | ISO 8601 | When discovered/fetched |
| reviewed_at | TEXT | | ISO 8601 | When promoted to OPERATE. NULL = pending. |
| created_at | TEXT | NOT NULL | ISO 8601 | Record creation timestamp |
| updated_at | TEXT | NOT NULL | ISO 8601 | Last modification timestamp |

---

### lbb_records_error — CQRS Error Table

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| error_id | TEXT | PK | UUID | Unique error identifier |
| record_id | TEXT | | UUID or NULL | FK → lbb_records. NULL if never persisted. |
| error_code | TEXT | NOT NULL | Enum | FETCH_FAILED, PARSE_ERROR, DEDUP_COLLISION, CLASSIFICATION_FAILED |
| error_message | TEXT | NOT NULL | Free text | Human-readable error description |
| source_url | TEXT | | URL | URL/source that failed. Preserved for retry. |
| payload_snapshot | TEXT | | JSON | Raw payload at failure. For debugging. |
| sub_hub | TEXT | | Enum | Which UT sub-hub generated this error |
| created_at | TEXT | NOT NULL | ISO 8601 | When error occurred |

---

### lbb_logbook — Append-Only Change History

| Column | Type | Constraint | Format | Description |
|--------|------|-----------|--------|-------------|
| entry_id | TEXT | PK | UUID | Unique logbook entry |
| record_id | TEXT | NOT NULL, FK → lbb_records | UUID | Which record this documents |
| orbt_entered | TEXT | NOT NULL, CHECK | BUILD/OPERATE/REPAIR/TROUBLESHOOT_TRAIN | ORBT state when work started |
| orbt_exited | TEXT | NOT NULL, CHECK | BUILD/OPERATE/REPAIR/TROUBLESHOOT_TRAIN | ORBT state when work completed |
| action | TEXT | NOT NULL | Free text | What was done. Plain English. |
| signed_by | TEXT | NOT NULL | Free text | Who performed the work |
| signed_at | TEXT | NOT NULL | ISO 8601 | Signature timestamp. Immutable. |
| notes | TEXT | | Free text | Optional context or reasoning |

---

### Join Chain

```
lbb_subjects.subject_id (Dewey Decimal tree — self-referencing via parent_id)
  → lbb_records.subject_id (1:N — records hang from subjects as leaves)
    → lbb_records_error.record_id (1:N — errors per record)
    → lbb_logbook.record_id (1:N — logbook entries per record)
```

### Forbidden Paths

| Action | Why |
|--------|-----|
| Modify a logbook entry | Append-only. Aviation model. |
| Delete a record | Records are never deleted. ORBT to REPAIR or TROUBLESHOOT_TRAIN. |
| Insert without content_hash | Dedup is mandatory. No hash = no insert. |
| Insert with duplicate content_hash | Dedup collision → records_error. |
| Create subject without ctb_level | Every subject must declare its position. |
| Skip HEIR fields | Every record gets all 8 HEIR fields at creation. |

### Query Routing

| Question | Query Pattern |
|----------|--------------|
| Everything about outreach | `WHERE subject_id IN (SELECT subject_id FROM lbb_subjects WHERE parent_id = 'trunk-outreach' OR subject_id = 'trunk-outreach')` |
| All vendor evaluations | `WHERE subject_id IN (... research/vendor-evaluations leaf)` |
| All records in BUILD (need review) | `WHERE orbt_mode = 'BUILD'` |
| Records by source type | `WHERE source_type = 'web'` or `'pdf'` etc. |
| Dedup check before insert | `WHERE content_hash = ?` |
| Record history | `SELECT * FROM lbb_logbook WHERE record_id = ? ORDER BY signed_at` |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants
- 4 tables: subjects, records, records_error, logbook. No more, no less.
- 5 trunk subjects: system, outreach, sales, client, research
- HEIR identity: 8 fields stamped at birth. Never changes.
- ORBT lifecycle: BUILD → OPERATE → REPAIR → TROUBLESHOOT/TRAIN
- Content dedup via SHA-256 hash
- Logbook is append-only. No edits. No deletes.
- Records are never deleted. State changes via ORBT.
- Subjects hierarchy is self-referencing (Dewey Decimal). Any depth.

### Variables
- Which records exist (grows with each ingestion)
- Which subjects exist below trunk level (branches and leaves created as needed)
- ORBT state per record (changes with review/corrections)
- Content of each record (the knowledge itself)
- Tags per record (freeform classification)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Content hash collision | HALT — duplicate content. Log to records_error. |
| Subject classification fails | HALT — can't determine where this belongs. Human review. |
| Content is empty or <10 chars | REJECT — not knowledge, just noise. |
| Source URL unreachable | Log to records_error. Don't create record. |
| Strike 3 on same record | TROUBLESHOOT/TRAIN → Airworthiness Directive. |

---

## 8. DEPENDENCIES

### Upstream (feeds knowledge into LBB)

| Source | What | How |
|--------|------|-----|
| All processes (010-900) | Session learnings, analytics, decisions | POST /ingest after each run |
| Vendor-scout (sub-hub 27) | Marketplace findings, vendor evaluations | POST /ingest with research subject |
| imo-brain migration | 62 existing docs | Batch ingest, classify into 5 trunks |
| svg-brain migration | 32 surviving docs (gap analysis) | Batch ingest under outreach/sales trunks |

### Downstream (queries LBB for knowledge)

| Consumer | What It Needs |
|----------|--------------|
| All processes | Prior learnings before starting work (read the logbook) |
| 100 LCS Pipeline | SVG Brain content for SID construction |
| Vendor-scout (27) | Prior evaluations to avoid re-testing |
| Claude Code sessions | Context from prior sessions |

---

## 9. SMOKE TEST

```
1. wrangler d1 execute lbb --remote --command "SELECT COUNT(*) FROM lbb_subjects" → expected: 5 trunks
2. wrangler d1 execute lbb --remote --command "SELECT name, ctb_level FROM lbb_subjects" → expected: 5 trunks listed
3. POST /ingest with test record → expected: record created, HEIR stamped, ORBT=BUILD
4. POST /ingest with same content → expected: REJECTED (duplicate hash)
5. GET /query?subject=trunk-system → expected: returns test record
6. Check logbook: SELECT * FROM lbb_logbook → expected: 1 entry for test record
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Do the 4 tables exist? Are the 5 trunks seeded?
2. **Flow:** Does content reach the record table? Does the logbook get written?
3. **Change:** Is HEIR stamped? Is content hashed? Is dedup working?

---

## 10. ANALYTICS — The Dyno Sheet (Bedrock §2 + §5)

### Process Metrics

| Metric | Unit | Baseline | Target | Tolerance |
|--------|------|----------|--------|-----------|
| Total records | count | 0 (new) | grows | track growth rate |
| Records by trunk | count per trunk | BASELINE | balanced across domains | no trunk > 80% of total |
| Records in BUILD (unreviewed) | count | BASELINE | decreasing | review backlog should shrink |
| Records in OPERATE (usable) | count | BASELINE | increasing | knowledge should be validated |
| Dedup collision rate | % | BASELINE | low (<5%) | high rate = ingesting duplicates |
| Classification accuracy | % | BASELINE (manual review) | >90% | records in wrong subject |
| Logbook entries per record | ratio | 1 (at ingest) | grows with lifecycle | no record without logbook |
| Migration: imo-brain docs ingested | count | 0 of 62 | 62 | complete |
| Migration: svg-brain docs ingested | count | 0 of 32 | 32 | complete |

### Tool Scorecard

| Tool # | Vendor | Hit Rate | Cost/Unit | Error Rate | Latency | Period |
|--------|--------|----------|-----------|------------|---------|--------|
| 11-structured-data | CF D1 | BASELINE | $0 | BASELINE | BASELINE | pending |
| 09-llm-router | Workers AI | BASELINE | $0 | BASELINE | BASELINE | pending |

### Sigma Tracking — set after 3+ ingestion runs

### ORBT Gate Rule

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All metrics within tolerance for 3 consecutive runs |
| OPERATE | REPAIR | Any metric outside tolerance |
| REPAIR | OPERATE | Fix applied + metric back within tolerance |
| Any (Strike 3) | TROUBLESHOOT/TRAIN | Same metric fails 3 times → AD |

---

## 11. LOGBOOK

### 2026-03-31 — D1 created, schema applied, 5 trunks seeded

**ORBT:** BUILD
**Trigger:** Manual — Dave's brainstorm on unified brain

| Step | Target | Actual | Delta |
|------|--------|--------|-------|
| Create D1 | lbb database exists | Created (1f8f12ab) | 0 |
| Apply schema | 4 tables | 4 tables created | 0 |
| Seed trunks | 5 trunk subjects | 5 seeded (system, outreach, sales, client, research) | 0 |

**Tools used:** 11-structured-data (CF D1 via wrangler CLI)
**Errors:** 0
**Learnings:** One library beats five databases. Dewey Decimal subjects hierarchy handles domain separation.
**ORBT after:** BUILD

---

## 12. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-03-31 | No CF Worker deployed yet | Schema only, no API | Build Hono worker with /ingest, /query, /lookup | 0 |
| 2 | 2026-03-31 | No Neon vault yet | D1 only | Create Neon database + Hyperdrive binding | 0 |
| 3 | 2026-03-31 | imo-brain migration pending | 62 docs need classification | Batch ingest with domain tag → trunk mapping | 0 |
| 4 | 2026-03-31 | svg-brain migration pending | 32 surviving docs need classification | Map per gap analysis (sales voice → sales, ops → outreach) | 0 |

---

## 13. SESSION LOG

| Date | What Was Done | imo-brain Document |
|------|---------------|-------------------|
| 2026-03-31 | LBB concept, D1 created, schema applied, 5 trunks seeded, PROCESS.md written | pending |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-31 |
| Last Modified | 2026-03-31 |
| Version | 1.0.0 |
| Template Version | 3.0.0 |
| Brain Template | fleet/brain-template/ v1.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | this document (self-contained — LBB is its own OSAM) |

# WORK ORDER: Outreach Line — Internal Step Definitions
## Define the internal steps for every process on the outreach production line
### Created: 2026-04-02
### Authority: PROC-060 Production Line Engine + HOW_TO_BUILD_A_PROCESS.md

---

## The Goal

Every process on the outreach line gets its internal steps defined using the template. Each step is its own IMO with comparators, tolerances, and decision function. The production line connects them with conditional logic from the workbench.

When this work order is complete, the entire outreach pipeline is documented at every altitude — from the production line trunk down to the individual step leaves.

---

## Pipeline Diagram — Full Outreach Line

```
══════════════════════════════════════════════════════════════════════════
PRODUCTION LINE: OUTREACH (trunk)
══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ STATION: 010-SEED (PROC-010)                                        │
│ Status: OPERATE | Adapter: HTTP (lcs-hub.svg-outreach.workers.dev)  │
│ Depends on: nothing (first station)                                  │
│                                                                      │
│ INTERNAL STEPS:                                                      │
│ ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐           │
│ │ Step 1  │───▶│ Step 2  │───▶│ Step 3  │───▶│ Step 4  │           │
│ │ QUERY   │    │ TRANSFER│    │ WRITE   │    │ VERIFY  │           │
│ │         │    │         │    │         │    │         │           │
│ │ Read    │    │ Neon →  │    │ D1      │    │ Count   │           │
│ │ Neon    │    │ Hyper-  │    │ INSERT  │    │ match + │           │
│ │ seed_   │    │ drive   │    │ OR      │    │ join    │           │
│ │ views   │    │ batch   │    │ REPLACE │    │ audit   │           │
│ └─────────┘    └─────────┘    └─────────┘    └─────────┘           │
│                                                                      │
│ C_i: row_count_match, join_integrity, table_coverage                │
│ k_i: 100% match, 99% joins, all tables present                     │
│                                                                      │
│ OUTPUT: D1 fully populated (32,702 companies, 97,983 slots)         │
│         + slot_workbench materialized view refreshed                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STATION: 300-RECON (PROC-300)                                        │
│ Status: OPERATE | Adapter: CLI (company-recon.py)                    │
│ Depends on: 010-seed                                                 │
│                                                                      │
│ INTERNAL STEPS:                                                      │
│ ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ │ Step 1  │───▶│ Step 2  │───▶│ Step 3  │───▶│ Step 4  │───▶│ Step 5  │
│ │SEARCHER │    │ORGANIZER│    │CLASSIFR │    │MATCHER  │    │ WRITER  │
│ │         │    │         │    │         │    │         │    │         │
│ │ Read    │    │ C&V 3   │    │ Title   │    │LinkedIn │    │ Write   │
│ │ work-   │    │ questions│   │ Classifr│    │ slug →  │    │ to D1   │
│ │ bench,  │    │ on each │    │ (Snap-  │    │ name    │    │ work-   │
│ │ search  │    │ entry:  │    │ On Tool)│    │ match   │    │ bench + │
│ │ Start-  │    │ person? │    │ RapidFuz│    │         │    │ time-   │
│ │ page    │    │ company?│    │ 3-tier  │    │         │    │ stamp   │
│ │         │    │ garbage?│    │         │    │         │    │         │
│ └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
│                                                                      │
│ C_i: capture_rate, captcha_rate, classify_accuracy, match_rate      │
│ k_i: ≥95%, ≤5%, ≥80%, ≥40%                                         │
│                                                                      │
│ OUTPUT: Workbench updated with about_url, LinkedIn, names, emails    │
│         + last_recon_at timestamped                                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  CONDITIONAL LOGIC   │
                    │  (workbench state)   │
                    │                      │
                    │  FULL → skip all     │
                    │  REACHABLE → 201/202 │
                    │  NAME_ONLY → 201+202 │
                    │  PATTERN_READY → 200 │
                    │  EMPTY → 200         │
                    │  HUNTER_READY → 200  │
                    └──────┬───────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STATION: 200-PEOPLE (PROC-200)                                       │
│ Status: BUILD | Adapter: CLI (find-person-v3.py)                     │
│ Depends on: 300-recon                                                │
│                                                                      │
│ INTERNAL STEPS:                                                      │
│ ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐           │
│ │ Step 1  │───▶│ Step 2  │───▶│ Step 3  │───▶│ Step 4  │           │
│ │GATE A   │    │GATE B   │    │GATE C   │    │ WRITER  │           │
│ │         │    │         │    │         │    │         │           │
│ │ Parse   │    │ Promote │    │ Search  │    │ Write   │           │
│ │ recon_  │    │ Hunter  │    │ Start-  │    │ name to │           │
│ │ name_   │    │ candid- │    │ page    │    │ work-   │           │
│ │ titles  │    │ ate     │    │ natural │    │ bench   │           │
│ │ (FREE)  │    │ (FREE)  │    │ language│    │ NAME_   │           │
│ │         │    │         │    │ (proxy) │    │ ONLY    │           │
│ └─────────┘    └─────────┘    └─────────┘    └─────────┘           │
│                                                                      │
│ Gate chain: A stops if match found. B stops if match. C = fallback. │
│ C_i: gate_a_hit_rate, gate_b_hit_rate, total_fill_rate, captcha    │
│ k_i: ≥50%, ≥15%, ≥70%, ≤5%                                         │
│                                                                      │
│ OUTPUT: person_first_name + person_last_name filled                  │
│         has_name = 1, person_found_at timestamped                    │
│         readiness_tier = NAME_ONLY (NOT REACHABLE — email is 201)   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
┌─────────────────────────────────┐  ┌─────────────────────────────────┐
│ STATION: 201-EMAIL (PROC-201)   │  │ STATION: 202-LINKEDIN (PROC-202)│
│ Status: BUILD                    │  │ Status: BUILD                    │
│ Adapter: CLI (find-email.py)     │  │ Adapter: CLI (find-linkedin.py)  │
│ Depends on: 200-people           │  │ Depends on: 200-people           │
│ Conditional: has_name=1,         │  │ Conditional: has_name=1,         │
│              has_email=0         │  │              has_linkedin=0      │
│                                  │  │                                  │
│ INTERNAL STEPS:                  │  │ INTERNAL STEPS:                  │
│ ┌───────┐ ┌───────┐ ┌───────┐   │  │ ┌───────┐ ┌───────┐ ┌───────┐  │
│ │GATE A │▶│GATE B │▶│GATE C │   │  │ │GATE A │▶│GATE B │▶│GATE C │  │
│ │       │ │       │ │       │   │  │ │       │ │       │ │       │  │
│ │Pattern│ │Hunter │ │Start- │   │  │ │Slug   │ │Hunter │ │Start- │  │
│ │genera-│ │promote│ │page   │   │  │ │match  │ │promote│ │page   │  │
│ │te from│ │email  │ │search │   │  │ │recon_ │ │linked-│ │search │  │
│ │{first}│ │if     │ │+ MV   │   │  │ │linked-│ │in_url │ │{name} │  │
│ │.{last}│ │conf≥80│ │verify │   │  │ │in_    │ │       │ │{co}   │  │
│ │@domain│ │       │ │$0.003 │   │  │ │people │ │       │ │linked-│  │
│ │(FREE) │ │(FREE) │ │(PAID) │   │  │ │(FREE) │ │(FREE) │ │in     │  │
│ └───────┘ └───────┘ └───────┘   │  │ └───────┘ └───────┘ └───────┘  │
│                                  │  │                                  │
│ + Step 4: WRITER                 │  │ + Step 4: WRITER                 │
│ + Step 5: MV VERIFY (PLANNED)    │  │                                  │
│                                  │  │ C_i: slug_match_rate,            │
│ C_i: pattern_hit, hunter_hit,   │  │      hunter_hit, total_fill,     │
│      total_fill, mv_verify_rate  │  │      captcha_rate                │
│ k_i: ≥40%, ≥15%, ≥80%, ≥90%     │  │ k_i: ≥40%, ≥20%, ≥90%, ≤5%     │
│                                  │  │                                  │
│ OUTPUT: person_email filled      │  │ OUTPUT: person_linkedin filled   │
│         has_email = 1            │  │         has_linkedin = 1         │
│         email_found_at stamped   │  │         linkedin_found_at stamped│
└──────────────┬───────────────────┘  └──────────────┬─────────────────┘
               │                                     │
               └──────────────┬──────────────────────┘
                              │
                              ▼
               ┌──────────────────────────┐
               │  WORKBENCH STATE CHECK   │
               │                          │
               │  Slot has name + email   │
               │  + LinkedIn = FULL       │
               │                          │
               │  FULL slots → ready for  │
               │  LCS Pipeline (100)      │
               └──────────┬───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STATION: 100-LCS (PROC-100)                                         │
│ Status: OPERATE | Adapter: HTTP (lcs-hub.svg-outreach.workers.dev)  │
│ Depends on: 200-people, 201-email, 202-linkedin, 400-dol, 500-flow │
│                                                                      │
│ Compiles CID → SID → MID from workbench constants                   │
│ Every constant in the workbench feeds the message                    │
│ The more constants filled, the more personalized the outreach        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STATION: 700-CAMPAIGN (PROC-700)                                     │
│ Status: BUILD | Adapter: HTTP (lcs-hub)                              │
│ Depends on: 100-lcs                                                  │
│                                                                      │
│ Sends the compiled messages via Mailgun (14 domains, rotation)       │
│ Tracks opens, clicks, replies, bounces                               │
│ Bounce → updates person_email_verified = 0 → re-enters 201          │
│ Reply → enters sales pipeline (900)                                  │
└─────────────────────────────────────────────────────────────────────┘

══════════════════════════════════════════════════════════════════════════
THE CIRCLE CLOSES:
  700 sends → bounce/reply webhook → updates workbench
  → stale data triggers 300 re-run (--stale 90)
  → 200/201/202 fill what changed
  → 100 recompiles → 700 re-sends
══════════════════════════════════════════════════════════════════════════
```

---

## Work Order — Execution Sequence

Each task follows HOW_TO_BUILD_A_PROCESS.md: descend through altitudes, template at every level, Tier 0 on every step.

### Task 1: Process 010 — SEED Internal Steps

| Step | Name | IMO | Key Comparators |
|------|------|-----|----------------|
| 1 | Query Neon | Read seed_views via Hyperdrive | C: view_exists, row_count |
| 2 | Transfer | Batch read from Neon, prepare for D1 | C: batch_size, transfer_time |
| 3 | Write D1 | INSERT OR REPLACE into D1 tables | C: rows_written, error_count |
| 4 | Build Workbench | REFRESH materialized view → SEED workbench | C: workbench_row_count |
| 5 | Verify | Count match + join audit | C: count_match, join_integrity |

**Deliverables:**
- [ ] Update PROCESS.md with internal steps in Middle table
- [ ] Define comparators C_i and initial tolerances k_i per step
- [ ] Verify comparator properties (measurable, deterministic, representation-invariant, temporally complete)
- [ ] Update analytics (§10) with step-level metrics

---

### Task 2: Process 300 — Company Recon Internal Steps

| Step | Name | IMO | Key Comparators |
|------|------|-----|----------------|
| 1 | Searcher | Read workbench, search Startpage | C: capture_rate, captcha_rate, query_rate |
| 2 | Organizer | C&V three questions on each raw entry | C: person_count, company_count, garbage_count |
| 3 | Classifier | Title → CEO/CFO/HR via RapidFuzz tool | C: classify_accuracy, reject_rate, confidence_distribution |
| 4 | Matcher | LinkedIn slug → person name match | C: match_rate, false_positive_rate |
| 5 | Writer | Validated data → workbench + timestamps | C: rows_updated, error_count |

**Deliverables:**
- [ ] Update PROCESS.md with internal steps in Middle table
- [ ] Build the Organizer (C&V gate on raw recon data — the missing piece)
- [ ] Wire Title Classifier as Snap-On tool
- [ ] Define comparators and tolerances per step
- [ ] Purge 1,275 free_extraction garbage from workbench
- [ ] Update analytics with step-level metrics

---

### Task 3: Process 200 — Find Person Internal Steps

| Step | Name | IMO | Key Comparators |
|------|------|-----|----------------|
| 1 | Gate A: Recon Parse | Parse recon_name_titles, match title to slot | C: parse_match_rate |
| 2 | Gate B: Hunter Promote | Promote hunter candidate to slot | C: promote_count |
| 3 | Gate C: Startpage Search | Natural language search, extract names | C: search_hit_rate, captcha_rate |
| 4 | Writer | Name → workbench, readiness = NAME_ONLY | C: slots_filled, error_count |

**Deliverables:**
- [ ] Update PROCESS.md with internal steps
- [ ] Gate A needs the Organizer output (Pile 1 = has title) — depends on Task 2
- [ ] Define comparators and tolerances per gate
- [ ] Update analytics

---

### Task 4: Process 201 — Find Email Internal Steps

| Step | Name | IMO | Key Comparators |
|------|------|-----|----------------|
| 1 | Gate A: Pattern Generate | Apply email_pattern + name + domain | C: pattern_available_rate, generation_count |
| 2 | Gate B: Hunter Promote | Promote hunter_email if confidence ≥ 80 | C: promote_count, confidence_threshold |
| 3 | Gate C: Startpage Search | Search for email in results | C: search_hit_rate, captcha_rate |
| 4 | Writer | Email → workbench, readiness = REACHABLE | C: slots_filled |
| 5 | MV Verify (PLANNED) | Million Verifier SMTP confirmation | C: verify_rate, deliverable_rate, cost |

**Deliverables:**
- [ ] Update PROCESS.md with internal steps
- [ ] Define comparators and tolerances per gate
- [ ] Million Verifier integration (when ready)
- [ ] Update analytics

---

### Task 5: Process 202 — Find LinkedIn Internal Steps

| Step | Name | IMO | Key Comparators |
|------|------|-----|----------------|
| 1 | Gate A: Slug Match | Match recon_linkedin_people slugs to person name | C: slug_match_rate |
| 2 | Gate B: Hunter Promote | Promote hunter_linkedin | C: promote_count |
| 3 | Gate C: Startpage Search | Search "{name} {company} linkedin" | C: search_hit_rate, captcha_rate |
| 4 | Writer | LinkedIn URL → workbench, update readiness | C: slots_filled |

**Deliverables:**
- [ ] Update PROCESS.md with internal steps
- [ ] Define comparators and tolerances per gate
- [ ] Update analytics

---

## Pre-Requisites (before starting tasks)

- [x] PROC-060 PROCESS.md passes C_structure audit
- [x] HOW_TO_BUILD_A_PROCESS.md with math integrated
- [x] HOW_TO_RUN_A_PROCESS.md with math integrated
- [x] Mathematical Principle locked in doctrine
- [x] All process scripts built (company-recon.py, find-person-v3.py, find-email.py, find-linkedin.py)
- [x] Title Classifier built (Snap-On tool)
- [x] Workbench loaded with 300 recon data
- [ ] Purge 1,275 free_extraction garbage from workbench
- [ ] Deploy production line engine to CF

---

## Execution Rules

1. **Do Tasks 1-5 in order.** Each builds on the prior.
2. **Follow HOW_TO_BUILD** — descend through altitudes, don't skip.
3. **Tier 0 on every step** — C&V three questions + comparators + tolerances.
4. **Don't write code** — the code exists. This is documentation + wiring.
5. **Submit for audit** after each task — run C_structure at minimum.
6. **The diagram above is the 50K view.** Each task descends to 30K-5K.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-02 |
| Governing Process | PROC-060 (Production Line Engine) |
| Governing Docs | HOW_TO_BUILD_A_PROCESS.md, PROCESS_TEMPLATE v4.0.0 |
| Mathematical Engine | imo-creator-v2/law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md |

---
mission_control_exempt: true
mission_control_exempt_reason: Internal template artifact — defines intake YAML format used by the Four-Brain pipeline. Not operator-facing content. Per BAR-070-MC-WIRE Plan Book §7.
---

# Planner Intake Template

**Process 070 Four-Brain — Operator → Planner source packet**
**Status:** TEMPLATE | **Version:** 2.0.0 | **Last Modified:** 2026-05-06
**Paired YAML:** `planner-intake-template.yaml`

---

## Purpose

Operator drops the work in plain language. Planner translates into structured doctrine, reads Atlas, builds the Plan Book.

**Operator answers the questions. The Planner does the rest.**

If a question can be answered later, leave it blank — the Planner will ask.

---

## BAR Identifier

| Field | Fill |
| --- | --- |
| BAR ID | `BAR-___` |
| Submitted by | `[name]` |
| Submitted at | `[ISO timestamp or blank]` |

---

## Mandatory — IMO + Type

Four questions. Plain language. No jargon.

### Q1. WHERE FROM

> Where is the information / signal / trigger coming from?

```text
[Where does this start? A repo, a worker, a doc, a process, a customer, an event, a schedule, a person.]
```

### Q2. WHAT

> What do you want done with it?

```text
[Describe the work in business terms. What should happen between input and output.]
```

### Q3. WHERE TO

> Where does the result go?

```text
[Final destination. A repo, a doc, a database, a dashboard, an email, a person, a process, the Library.]
```

### Q4. TYPE

> Pick one. This drives the conditional follow-up.

```text
[ ] 1 — Build (new construction; factory)
[ ] 2 — Fix (something broken; garage repair)
[ ] 3 — Maintenance (scheduled tune-up; garage maintenance)
```

#### Q4A — Conditional follow-up (answer ONLY the one that matches Q4)

**If Q4 = 1 (Build):**

```text
Maintenance cadence after build:
[ ] A-check (weekly)
[ ] B-check (monthly)
[ ] C-check (quarterly)
[ ] D-check (yearly)
[ ] None / not applicable
```

**If Q4 = 2 (Fix):**

```text
Squawk / symptom (what is broken; what did you observe):
[Describe the failure. Error message, missing data, wrong output, regression — whatever the symptom is.]
```

**If Q4 = 3 (Maintenance):**

```text
Check level:
[ ] A-check (weekly)
[ ] B-check (monthly)
[ ] C-check (quarterly)
[ ] D-check (yearly)
[ ] AD (event-driven airworthiness directive)
```

---

## Optional — Helpful If You Have It

These are not required. The Planner will fill them in from Atlas + memory if blank.

| # | Field | Hint |
| --- | --- | --- |
| O1 | **Why** | Why does this matter? Driver, deadline, constraint, business context. |
| O2 | **Who for** | Who consumes the output? Sovereign, customer, system, downstream process. |
| O3 | **Deadline** | Date / event / "no rush". |
| O4 | **Constraints** | Locked files, no-touch zones, sovereign-only decisions, security boundaries. |
| O5 | **Existing** | Anything already in flight, already documented, already failed — point to it. |
| O6 | **Reference** | Files, BAR IDs, LBB rows, Linear issues, screenshots, voice notes. |

```text
O1. Why:
[blank or fill]

O2. Who for:
[blank or fill]

O3. Deadline:
[blank or fill]

O4. Constraints:
[blank or fill]

O5. Existing:
[blank or fill]

O6. Reference:
[blank or fill]
```

---

## Garage Intake Status

Operator sets `garage_status` in the paired YAML, not here. The MD is for human reading; the YAML is the trigger.

| Status | Meaning |
| --- | --- |
| `DRAFT` | Parked. Not ready. |
| `READY_FOR_PLANNER` | In the bay with a work order on the windshield. Planner picks it up. |
| `PLANNER_RUNNING` | Planner has claimed it. |
| `PLAN_BOOK_SIGNED` | Plan Book produced and sovereign-signed. Foreman can dispatch. |
| `FOREMAN_RUNNING` | Foreman is producing the dispatch. |
| `FOREMAN_DISPATCHED` | Foreman dispatch written; Mechanic not yet started. |
| `MECHANIC_RUNNING` | Mechanic is executing work orders. |
| `MECHANIC_DONE` | Mechanic output written; Auditor not yet started. |
| `AUDITOR_RUNNING` | Auditor is inspecting. |
| `REVIEW_PLAN_BOOK` | Awaiting sovereign review of Plan Book. |
| `REVIEW_FOREMAN_DISPATCH` | Awaiting sovereign review of Foreman dispatch. |
| `REVIEW_MECHANIC_OUTPUT` | Awaiting sovereign review of Mechanic output. |
| `REVIEW_AUDIT_VERDICT` | Awaiting sovereign review of Audit verdict. |
| `BLOCKED` | Question back to operator (Planner can't proceed). |
| `CLOSED` | BAR finished. |
| `TROUBLESHOOT_TRAIN` | Strike-3 reached. Pipeline halted; structural review required (not another repair). |

---

## What the Planner Does Next (not the operator's problem)

The Planner reads this packet, then:

1. Reads Atlas (KEY, BS Law, Structure Manifest, Four-Brain doctrine, repo CTB)
2. Looks up the CTB position for the answers above
3. Inventories existing assets (Library Books, workers, scripts, FCEs, schemas) before designing
4. Climbs the priority ladder: existing automation > new automation > new code > AI (last resort)
5. Asks back questions as a `BLOCKED` status if anything mandatory is unclear
6. Writes the Plan Book
7. Hands off to Foreman

**Operator does not need to fill in CTB position, source-of-truth split, read set, connector binding, P=1 condition, audit packet, or any other doctrine field. The Planner owns those.**

---

## Edge-Case Routing (for Planner reference, not operator decision)

| Operator says... | Planner classifies as... |
| --- | --- |
| "Refactor X" | Build (new structure) |
| "Research Y" | Build (new artifact) |
| "Delete Z" | Fix (removing a defect) |
| "Audit / review" | Maintenance (C-check or AD) |
| "Investigate" | Fix (diagnostic before repair) |

---

## Parity Zone (BS Law v1.5.0)

Paired artifact: `planner-intake-template.yaml`. Fields that must stay synchronized between this file and the YAML companion:

| MD Field | YAML Field | Sync Rule |
| --- | --- | --- |
| Version (header + §Document Control) | `version` + `document_control.version` | Bump together |
| Last Modified (header + §Document Control) | `last_modified` + `document_control.last_modified` | Update together |
| Status (header + §Document Control) | `status` + `document_control.status` | Match always |
| Garage status table | `garage_status.enum` | Every status in MD table must appear in YAML enum |
| Planner responsibility order | `planner_responsibilities.discipline_order` | Steps must match |
| Changelog | `document_control.changelog` | Major entries mirrored |
| Authority | `document_control.authority` | Identical prose |

**Enforcement:** Codex G06 (`parsed_value_match`) verifies parity on every audit. Drift = BLOCK.

---

## Document Control

| Field | Value |
| --- | --- |
| Version | 2.0.0 |
| Last Modified | 2026-05-06 |
| Status | TEMPLATE |
| Authority | Sovereign-locked. Mechanic refactors instances; doctrine changes require sovereign sign-off. |
| Changelog | v2.0.0 (2026-05-06): Replaced 19-section verbose template with thin operator IMO+Type form. Doctrine fill is the Planner's job, not the operator's. |

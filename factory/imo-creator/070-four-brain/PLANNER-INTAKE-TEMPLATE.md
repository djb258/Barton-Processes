# Planner Intake Template
## Process 070 Four-Brain Planner Source Packet
### Status: TEMPLATE
### Medium: planner-intake
### Business: universal

---

## 1. Purpose

This template tells the Planner what outcome is wanted, what sources must be read, what constraints are locked, and what P=1 means.

It does not tell the Planner how to plan. The Planner owns the route. This packet only defines the destination, boundaries, evidence, and non-drift invariants.

Use this template for any BAR or process run that enters Process 070.

Paired YAML: `planner-intake-template.yaml`

---

## 2. Planner Request

| Field | Fill |
| --- | --- |
| BAR / Work ID | `BAR-___` |
| Target Process | `PROC-___ / bp.___ / name` |
| Desired Outcome | What we want completed, in business terms. |
| Operating Mode | BUILD / REPAIR / OPERATE / TROUBLESHOOT_TRAIN |
| Due / Timing | Today / this week / no deadline / specific date |
| Sovereign Decision Needed | yes/no + what decision |

Planner request:

```text
Run Process 070 for [target process / BAR].

Desired outcome:
[State what we want done. Do not prescribe how the Planner should do it.]
```

---

## 3. Garage Intake Status

This is the handoff switch. Any agent may fill the packet, but the Planner should only pick it up when status is `READY_FOR_PLANNER`.

| Field | Fill |
| --- | --- |
| garage_status | DRAFT / READY_FOR_PLANNER / PLANNER_RUNNING / PLAN_BOOK_READY / FOREMAN_DISPATCHED / CLOSED / BLOCKED |
| intake_path | `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-{id}/PLANNER-INTAKE.md` |
| intake_yaml_path | `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-{id}/planner-intake.yaml` |
| requested_by | Human / agent name |
| ready_at | ISO-8601 timestamp or blank |
| planner_claimed_by | Planner agent / blank |
| planner_claimed_at | ISO-8601 timestamp or blank |
| next_artifact | `Barton-Processes/docs/plans/BAR-{id}/PLAN-BOOK.md` |

Garage rule:

```text
DRAFT means parked but not ready.
READY_FOR_PLANNER means the car is in the garage bay with a work order on the windshield.
PLANNER_RUNNING means the Planner has claimed it.
PLAN_BOOK_READY means the Planner produced the Plan Book and the Foreman can dispatch.
```

---

## 4. Source-Of-Truth Split

| Layer | Owner | Repo / Folder | What It Owns |
| --- | --- | --- | --- |
| Blueprint / Architecture | `[repo/folder]` | `[path]` | What the system is and how it should work |
| Execution / Operations | `[repo/folder]` | `[path]` | How data moves and work gets done |
| Runtime / Deployment | `[repo/folder/service]` | `[path/url]` | Deployed implementation or live surface |
| Evidence / Observability | `[service]` | `[path/url/table]` | LBB, Mission Control, D1, R2, logs |

Non-drift rule:

```text
Blueprint explains. Execution runs. Runtime implements. Evidence proves.
Do not let one layer silently become the source of truth for another.
```

---

## 5. Required Format

| Artifact | Required? | Format |
| --- | --- | --- |
| Plan Book | yes | Plan-Body |
| UT | if durable process/doc | UT-Body |
| Companion YAML | if paired artifact | Workflow-Body / Config-Body / Data-Body as appropriate |
| BS Law | yes | Book + Spine together |
| Atlas references | yes | KEY, BS Law, Structure Manifest, Four-Brain doctrine where applicable |
| LBB / MC evidence | if operational | Required before P=1 |

Required paired-artifact rule:

```text
When the output is durable process documentation, produce or repair both MD and YAML if the process has a machine-readable workflow.
The MD and YAML must not drift.
```

---

## 6. Read Set

Planner must inspect these before planning:

| Source | Why Planner Reads It |
| --- | --- |
| `[path]` | `[purpose]` |
| `[path]` | `[purpose]` |
| `[path]` | `[purpose]` |

Always consider:

| Source | Why |
| --- | --- |
| `imo-creator-v2/atlas/constants/KEY.md` | Vocabulary |
| `imo-creator-v2/atlas/constants/BS_LAW.md` | Book + Spine conformance |
| `imo-creator-v2/atlas/manifests/STRUCTURE_MANIFEST.yaml` | CTB / locked constants |
| `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` | Planner / Foreman / Mechanic / Auditor separation |
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` | Process 070 operating rules |
| `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` | Process 070 workflow body |

---

## 7. Documentation Anchors

Use this section to give the Planner evidence that already exists.

| Claim / Constraint | Existing Documentation Anchor |
| --- | --- |
| `[claim]` | `[file/path/section]` |
| `[claim]` | `[file/path/section]` |

Example:

| Claim / Constraint | Existing Documentation Anchor |
| --- | --- |
| R2 is the active workbench before D1 vaulting | `Barton-Processes/docs/plans/BAR-FCE-RUN-060-PLANNER/FCE-RUN-PLANNER-INTAKE.md` |
| Process 070 is Planner -> Foreman -> Mechanic -> Auditor | `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` |

---

## 8. Research / Brainstorming Packet

Use this section when the work starts as rough thinking, voice notes, chat notes, whiteboard notes, or partial operator context.

The Planner may use this information, but it must separate facts from assumptions before dispatching work.

| Input Type | Location / Record | How Planner Should Use It |
| --- | --- | --- |
| Brainstorm notes | `[path / chat / note]` | Extract candidate goals, questions, and constraints. |
| Voice / meeting summary | `[path / transcript / summary]` | Convert into structured desired outcome and open questions. |
| Existing BAR notes | `[Linear/BAR/LBB link]` | Pull prior decisions, blockers, and acceptance criteria. |
| Operator observations | `[notes]` | Treat as clues until verified against source docs or runtime evidence. |

Fact handling rule:

```text
Brainstorming is input, not certification.
The Planner can use it to form the plan, but P=1 requires cited documentation, runtime evidence, or sovereign confirmation.
```

---

## 9. LB&B Pull Contract

Use this section to tell the Planner where to pull prior memory and compliance context.

| LB&B Field | Fill |
| --- | --- |
| Work IDs / BAR IDs | `BAR-___`, `PROC-___`, run IDs, trace IDs |
| Search Terms | Process names, customer/system names, domains, table names |
| Time Window | Today / this week / since date / all history |
| Required Records | Planner notes, Foreman dispatches, Mechanic outputs, Auditor verdicts, closeout logs |
| Evidence Needed For P=1 | Which LB&B rows must exist before closeout |

LB&B rule:

```text
Before planning, pull relevant LB&B records when they exist.
During execution, every role transition and closeout must be logged to LB&B when the process is operational or compliance-relevant.
If LB&B is unavailable, Planner must mark evidence as blocked or deferred; it cannot silently skip the logbook.
```

---

## 10. Connector / Run Binding

Use this section to define what connectors, services, or repo surfaces 070 may use for this BAR.

| Connector | Required? | Purpose | Credential / Access Source | Evidence Expected |
| --- | --- | --- | --- | --- |
| LB&B | if compliance-relevant | Pull prior memory; write role transitions and closeout | Doppler `LBB_API_KEY` or approved connector | Query results, transition rows, Audit Book / CERTIFY row |
| Linear / BAR tracker | if BAR exists there | Pull current status, comments, checklist, owner, blockers | Linear connector or exported BAR notes | BAR URL / ID and status snapshot |
| GitHub | if repo changes | Read/write versioned process docs and code | GitHub CLI / connector | Branch, commit, PR or pushed SHA |
| Atlas | yes | Resolve constants, structure, BS Law, Four-Brain doctrine | Local repo path | Exact file paths / sections cited |
| Mission Control | if operational | Surface run state, telemetry, dashboard visibility | D1 / worker / MC connector | Run row, dashboard link, or blocked note |
| R2 / D1 | if data-cycle process | Stage artifacts in R2; vault accepted records in D1 | Cloudflare/Doppler bindings | Object keys, D1 rows, or blocked note |

Connector rule:

```text
The template should name the connector and the job it performs.
The Planner decides how to use the connector inside the route.
No connector access = explicit blocker/defer note, not silent omission.
```

---

## 11. 070 Start Contract

Use this section after the template is filled out.

| Step | Artifact / Action | Owner | Output |
| --- | --- | --- | --- |
| 1 | Run `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh new BAR-{id}` | Operator / Planner intake | BAR intake folder |
| 2 | Fill `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-{id}/PLANNER-INTAKE.md` | Operator / Planner intake | Human-readable Planner source packet |
| 3 | Fill `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-{id}/planner-intake.yaml` and set `garage_status: READY_FOR_PLANNER` | Operator / Planner intake | Machine-readable ready signal |
| 4 | Run `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh run-once --execute` or watcher mode | ForeBrain garage | Planner execution |
| 5 | Planner writes `Barton-Processes/docs/plans/BAR-{id}/PLAN-BOOK.md` | Planner | Sovereign-reviewable Plan Book |
| 6 | Garage writes `Barton-Processes/factory/imo-creator/070-four-brain/garage/outbox/BAR-{id}/FINAL-PRODUCT.yaml` | ForeBrain garage | Final product pointer |
| 7 | Sovereign approves or corrects the Plan Book | Sovereign | Signed / accepted Plan Book |
| 8 | Foreman dispatches Mechanic work orders from the Plan Book | Foreman | Scoped work packets |
| 9 | Mechanic builds; Auditor audits; LB&B logs each transition | Mechanic / Auditor | P=1 or P=0 with evidence |

Runtime commands:

```text
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh new BAR-123
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh run-once --execute
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh watch --execute --interval 3
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh final BAR-123
```

Do not call the BAR complete until `FINAL-PRODUCT.yaml` exists and points to the durable product, usually `docs/plans/BAR-{id}/PLAN-BOOK.md`.

---

## 12. Non-Drift Invariants

These are locked facts the Planner must preserve.

| ID | Invariant |
| --- | --- |
| INV-01 | `[locked fact]` |
| INV-02 | `[locked fact]` |
| INV-03 | `[locked fact]` |

Common invariants:

| ID | Invariant |
| --- | --- |
| INV-COMMON-01 | The Planner owns the plan; the intake owns only desired outcome and constraints. |
| INV-COMMON-02 | Foreman dispatches; Mechanic builds; Auditor certifies. |
| INV-COMMON-03 | Mechanic cannot audit its own work. |
| INV-COMMON-04 | BS Law applies to every durable structured artifact. |
| INV-COMMON-05 | Blueprint, execution, runtime, and evidence layers must not drift. |

---

## 13. Input Contract

The operator must provide or explicitly defer:

| Input | Required? | Rule |
| --- | --- | --- |
| Target process | yes | Process number and name |
| Desired outcome | yes | Business outcome, not implementation route |
| Blueprint home | if applicable | Where architecture docs live |
| Execution home | if applicable | Where operational process docs live |
| Runtime surface | if applicable | Worker/API/cron/db/service |
| Evidence target | if applicable | LBB, Mission Control, D1, R2, logs |
| Brainstorming packet | if available | Notes, voice summary, chat summary, whiteboard, partial ideas |
| LB&B search contract | if available | Work IDs, BAR IDs, search terms, trace IDs, time window |
| Connector/run binding | if applicable | Which connectors 070 may use and what each must prove |
| Protected constraints | if applicable | Domains, secrets, locked files, human-only decisions |
| P=1 definition | yes | What done means |

---

## 14. Storage / Evidence Contract

Fill only what applies.

| Store | Role | Timing |
| --- | --- | --- |
| R2 | Workbench / staging / cycle artifacts | Before final vaulting if the process uses cycles/backprop |
| D1 | Registry / vault / indexed system of record | After acceptance criteria are met |
| LBB | Compliance logbook and durable memory | At role transitions and closeout |
| Mission Control | Operator visibility | During run and closeout |
| GitHub | Versioned source | After audited file changes |

Rules:

```text
Do not use D1 as scratchpad when R2/workbench cycle is required.
Do not call P=1 without required evidence surfaces.
Do not clean the workbench until the accepted package is vaulted or otherwise preserved.
```

---

## 15. Planner Deliverables

Planner should return:

| Deliverable | Required |
| --- | --- |
| Plan Book path / proposed path | yes |
| Read set | yes |
| Source-of-truth split | yes |
| Required artifacts | yes |
| Mechanic work orders | yes |
| Auditor packet | yes |
| P=1 definition | yes |
| Stop conditions | yes |
| Open blockers | yes |
| Evidence requirements | yes |
| LB&B records used or required | if applicable |
| Connectors used or blocked | if applicable |
| 070 start/handoff path | yes |
| Brainstorming claims promoted to facts | if applicable |
| Brainstorming claims left as assumptions | if applicable |

Planner must not be forced into a preselected implementation route unless the sovereign explicitly locks it.

---

## 16. Mechanic Dispatch Hints

This section is optional. Use it only to clarify scope boundaries, not to plan for the Planner.

```text
Allowed write scope:
- [path]
- [path]

Forbidden:
- [path/action]
- [path/action]
```

---

## 17. Auditor Packet Requirements

Auditor should receive:

| Audit Area | Evidence |
| --- | --- |
| BS Law | MD/YAML structure, outside/inside separation where applicable |
| UT conformance | All required UT sections if UT artifact |
| Source-of-truth split | Blueprint vs execution vs runtime vs evidence |
| Scope | Only allowed files changed |
| Runtime safety | If operational |
| Evidence | LBB / Mission Control / D1 / R2 as applicable |
| Connector evidence | Which connectors were used, blocked, or deferred |
| Research provenance | Brainstorming claims resolved into facts, assumptions, or open questions |
| Aviation | Mechanic != Auditor |

Auditor verdict must be:

```text
VERDICT: P=1
```

or

```text
VERDICT: P=0
```

with scoped file citations.

---

## 18. P=1 Definition

P=1 when:

1. `[condition]`
2. `[condition]`
3. `[condition]`
4. Auditor certifies.

Do not leave P=1 implied. The Planner needs an explicit done condition.

---

## 19. Open Questions

Only list questions that block planning.

| Question | Why It Blocks |
| --- | --- |
| `[question]` | `[reason]` |

If a question does not block planning, leave it out and let the Planner handle it.

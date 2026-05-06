# Planner Intake: BAR-VIDEO-PATH-CERTIFICATION
## Process 070 Four-Brain Planner Source Packet
### Status: READY_FOR_PLANNER
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
| BAR / Work ID | `BAR-VIDEO-PATH-CERTIFICATION` |
| Target Process | `video-production-paths / bp.video-garage` |
| Desired Outcome | Produce a Plan Book that tells Foreman how to build, repair, smoke-test, and audit the video production lanes so a script can enter and a video build can start through the correct path. |
| Operating Mode | BUILD / REPAIR |
| Due / Timing | current build cycle |
| Sovereign Decision Needed | no blocking decision; preserve Dave's two-layer rule and route uncertainties as Planner blockers |

Planner request:

```text
Run Process 070 for `BAR-VIDEO-PATH-CERTIFICATION`.

Desired outcome:
Create the Plan Book for the video production path system. The Plan Book must let Foreman dispatch scoped Mechanic and Auditor work for the parent Blueprint UTs in IMO-Creator v2 and the executable child Process UTs in Barton-Processes.

The Planner must preserve this source-of-truth split:

Blueprint explains. Execution runs. Runtime implements. Evidence proves.

The Planner should cover five lanes:

1. `heygen_avatar`
2. `notebooklm_source_video`
3. `elevenlabs_cinematic`
4. `claude_code_sovereign`
5. `video_picker`
```

---

## 3. Garage Intake Status

This is the handoff switch. Any agent may fill the packet, but the Planner should only pick it up when status is `READY_FOR_PLANNER`.

| Field | Fill |
| --- | --- |
| garage_status | READY_FOR_PLANNER |
| intake_path | `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-VIDEO-PATH-CERTIFICATION/PLANNER-INTAKE.md` |
| intake_yaml_path | `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-VIDEO-PATH-CERTIFICATION/planner-intake.yaml` |
| requested_by | Dave Barton / Codex operator fill |
| ready_at | `2026-05-05T00:00:00Z` |
| planner_claimed_by | blank |
| planner_claimed_at | blank |
| next_artifact | `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/PLAN-BOOK.md` |

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
| Blueprint / Architecture | IMO-Creator v2 | `imo-creator-v2/docs/processes/video-blueprints/` | Parent video Blueprint UTs, lane constants and variables, provider research, reusable rules |
| Execution / Operations | Barton-Processes | `Barton-Processes/factory/content/1710-*` through `1750-*` | Executable Process UTs, DOCTRINE, HEIR, ORBT, stop conditions |
| Runtime / Deployment | Provider/local tools | HeyGen, NotebookLM via Chrome MCP, ElevenLabs, Claude Code + In Motion, local picker scripts | Actual generation, source packaging, rendering, routing, upload handoff |
| Evidence / Observability | LBB / Linear / manifests / Mission Control | Linear BARs, LBB records, output manifest, provider job IDs, `workers/video-pipeline/output/video-output-manifest.json` | Proof, closeout records, blocker evidence, audit trail |

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
| `imo-creator-v2/atlas/ATLAS.md` | Parent legend, inheritance pattern, map-building SOP |
| `imo-creator-v2/atlas/constants/KEY.md` | Vocabulary and K=C |
| `imo-creator-v2/atlas/constants/UNIFIED_TEMPLATE.md` | UT structure and pre-flight gates |
| `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` | Planner / Foreman / Mechanic / Auditor separation |
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` | Process 070 operating rules |
| `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` | Machine-readable Four-Brain workflow |
| `imo-creator-v2/docs/processes/video-blueprints/INDEX.md` | Parent video blueprint inventory |
| `imo-creator-v2/docs/processes/video-blueprints/templates/` | Current video template set |
| `imo-creator-v2/docs/processes/video-blueprints/lanes/` | Lane-specific Blueprint UT drafts |
| `imo-creator-v2/docs/plans/VIDEO-PATHS-OPERATE-PUNCHLIST.md` | Operate punch list and current gaps |
| `imo-creator-v2/workers/video-pipeline/scripts/route-video-job.ps1` | Picker route harness |
| `imo-creator-v2/workers/video-pipeline/output/video-output-manifest.json` | Existing MP4 output evidence |
| `Barton-Processes/factory/content/1710-heygen-avatar/PROCESS-UT.md` | HeyGen executable child UT |
| `Barton-Processes/factory/content/1720-notebooklm-source-video/PROCESS-UT.md` | NotebookLM executable child UT |
| `Barton-Processes/factory/content/1730-elevenlabs-cinematic/PROCESS-UT.md` | ElevenLabs executable child UT |
| `Barton-Processes/factory/content/1740-claude-code-sovereign/PROCESS-UT.md` | Claude Code sovereign executable child UT |
| `Barton-Processes/factory/content/1750-video-picker/PROCESS-UT.md` | Picker executable child UT |

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
| Atlas is a reference/legend; child artifacts inherit and extend | `imo-creator-v2/atlas/ATLAS.md` |
| Every child atlas page is a UT doc and should follow the Atlas/UT rules | `imo-creator-v2/atlas/ATLAS.md`; `imo-creator-v2/atlas/constants/UNIFIED_TEMPLATE.md` |
| Process 070 is Planner -> Foreman -> Mechanic -> Auditor | `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md`; `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` |
| ForeBrain garage starts from `garage/inbox/BAR-{id}` and final pickup is `FINAL-PRODUCT.yaml` | `Barton-Processes/factory/imo-creator/070-four-brain/garage/README.md`; `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` |
| IMO-Creator v2 owns parent video Blueprint UTs | `imo-creator-v2/docs/processes/video-blueprints/INDEX.md` |
| Barton-Processes owns executable Process UTs | `Barton-Processes/factory/content/1710-heygen-avatar/PROCESS-UT.md`; `1720`; `1730`; `1740`; `1750` |
| Existing Claude Code + In Motion MP4 evidence exists | `imo-creator-v2/workers/video-pipeline/output/video-output-manifest.json` |

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
| Brainstorm notes | Current Dave/Codex chat context plus `imo-creator-v2/docs/processes/video-blueprints/templates/FOUR-BRAIN-VIDEO-GARAGE-INTAKE-FILL.md` | Extract the desired command flow and video path operating model. |
| Existing BAR notes | Linear BARs 388-392 where available; `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/VIDEO-PATH-PLANNER-INTAKE.md` | Pull prior lane status, blockers, and acceptance criteria. |
| Operator observations | Dave's correction that IMO-Creator v2 Blueprint is a UT and Barton-Processes holds executable UTs | Treat as sovereign constraint unless contradicted by locked Atlas doctrine. |
| Runtime evidence | HeyGen API access check, picker harness, MP4 output manifest | Promote to facts only when cited to files or command evidence. |

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
| Work IDs / BAR IDs | `BAR-VIDEO-PATH-CERTIFICATION`, `BAR-388`, `BAR-389`, `BAR-390`, `BAR-391`, `BAR-392`, `PROC-070`, `1710`, `1720`, `1730`, `1740`, `1750` |
| Search Terms | video paths, HeyGen, NotebookLM, ElevenLabs, Claude Code, In Motion, picker, Fish voice, cinematic video, video garage |
| Time Window | since 2026-05-01 |
| Required Records | Planner notes, Foreman dispatches, Mechanic outputs, Auditor verdicts, closeout logs |
| Evidence Needed For P=1 | LB&B role-transition rows if available; otherwise explicit blocked/deferred evidence note in Plan Book |

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
| LB&B | yes if reachable | Pull prior memory; write role transitions and closeout | Doppler `LBB_API_KEY` or approved connector | Query results, transition rows, Audit Book / CERTIFY row; explicit blocker if unavailable |
| Linear / BAR tracker | yes if reachable | Pull current status, comments, checklist, owner, blockers for BARs 388-392 | Linear connector or exported BAR notes | BAR URL / ID and status snapshot; explicit blocker if unavailable |
| GitHub | if repo changes | Read/write versioned process docs and code | GitHub CLI / connector | Branch, commit, PR or pushed SHA |
| Atlas | yes | Resolve constants, structure, BS Law, Four-Brain doctrine | Local repo path | Exact file paths / sections cited |
| Mission Control | if operational | Surface run state, telemetry, dashboard visibility | D1 / worker / MC connector | Run row, dashboard link, or blocked note |
| R2 / D1 | if artifact staging or vaulting is in scope | Stage artifacts in R2; vault accepted records in D1 | Cloudflare/Doppler bindings | Object keys, D1 rows, or blocked note |
| HeyGen | lane-specific | Avatar/video generation lane | Doppler `HEYGEN_API_KEY` | Avatar IDs, voice IDs, job IDs, output URL or blocked note |
| ElevenLabs | lane-specific | Cinematic voice/audio/image-video lane | Doppler `ELEVENLABS_API_KEY` | Voice IDs, generation job IDs, output URL or blocked note |
| Chrome MCP / NotebookLM | lane-specific | Source-led NotebookLM video lane | Chrome MCP browser session | Notebook/source evidence, export path, screenshot or blocked note |

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
| INV-01 | IMO-Creator v2 holds parent video Blueprint UTs and reusable documentation. |
| INV-02 | Barton-Processes holds executable video Process UTs. |
| INV-03 | Process 070 garage is the start surface for Planner work. |
| INV-04 | `FINAL-PRODUCT.yaml` is the pickup ticket for the durable Plan Book. |
| INV-05 | A script should be able to enter the system and route to the correct video lane after Foreman dispatches and Mechanic builds. |

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
| Target process | yes | `video-production-paths / bp.video-garage` |
| Desired outcome | yes | Plan Book for Foreman dispatch of all video production path templates and UT repairs |
| Blueprint home | yes | `imo-creator-v2/docs/processes/video-blueprints/` |
| Execution home | yes | `Barton-Processes/factory/content/1710-*` through `1750-*` |
| Runtime surface | yes | HeyGen, NotebookLM via Chrome MCP, ElevenLabs, Claude Code + In Motion, picker harness |
| Evidence target | yes | LBB, Linear, provider job IDs, output manifest, Mission Control where applicable |
| Brainstorming packet | yes | Dave/Codex conversation distilled in the current intake and template docs |
| LB&B search contract | yes | BARs 388-392, video-path search terms, since 2026-05-01 |
| Connector/run binding | yes | See section 10 |
| Protected constraints | yes | Do not modify locked Atlas constants; do not collapse Blueprint and Execution homes; do not expose secrets |
| P=1 definition | yes | See section 18 |

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

Plan Book target:

```text
Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/PLAN-BOOK.md
```

---

## 16. Mechanic Dispatch Hints

This section is optional. Use it only to clarify scope boundaries, not to plan for the Planner.

```text
Allowed write scope:
- `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/PLAN-BOOK.md`
- `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/`
- Foreman dispatch packet paths selected by the Planner

Forbidden:
- locked Atlas constants
- secrets or credential values
- unscoped executable process rewrites
- combining Mechanic and Auditor roles
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

1. Plan Book exists at `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/PLAN-BOOK.md`.
2. Plan Book cites the Atlas, KEY, UT, Four-Brain, garage intake, video Blueprint index, and executable child UTs.
3. Plan Book defines Foreman dispatch requirements for all five video lanes.
4. Plan Book preserves the source-of-truth split: Blueprint explains, Execution runs, Runtime implements, Evidence proves.
5. Plan Book defines Mechanic work orders, Auditor packet requirements, smoke tests, evidence surfaces, and stop conditions.
6. Plan Book names any blocked connector, credential, browser session, provider gate, or Linear/LBB gap instead of hiding it.
7. ForeBrain garage writes `FINAL-PRODUCT.yaml` pointing to the durable Plan Book.

Do not leave P=1 implied. The Planner needs an explicit done condition.

---

## 19. Open Questions

Only list questions that block planning.

| Question | Why It Blocks |
| --- | --- |
| none at intake time | Planner should mark runtime/provider gaps as Plan Book blockers, not intake blockers. |

If a question does not block planning, leave it out and let the Planner handle it.

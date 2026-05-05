# Video Path Planner Intake
## Process 070 Four-Brain source packet for video blueprint + executable UT certification
### Status: DRAFT
### Medium: planner-intake
### Business: imo-creator / barton-enterprises

---

## 1. Purpose

This packet tells the Planner what outcome is wanted for the video production paths: convert the current video work into a clean two-layer UT system.

The Planner owns the plan. This packet only defines the destination, source-of-truth split, read set, non-drift invariants, evidence requirements, and P=1 definition.

Paired YAML: `video-path-planner-intake.yaml`

---

## 2. Planner Request

| Field | Fill |
| --- | --- |
| BAR / Work ID | BAR-388, BAR-389, BAR-390, BAR-391, BAR-392, BAR-VIDEO-PATH-CERTIFICATION |
| Target Process | PROC-1710, PROC-1720, PROC-1730, PROC-1740, PROC-1750, PROC-1800 |
| Desired Outcome | Produce a Four-Brain plan that turns the video path system into linked Blueprint UTs in IMO-Creator v2 and executable Process UTs in Barton-Processes, then promotes each path toward OPERATE with audit and smoke evidence. |
| Operating Mode | BUILD -> OPERATE |
| Due / Timing | This week |
| Sovereign Decision Needed | yes: decide whether PROC-1740 sovereign lane may certify with provider-assisted Claude/InVideo/NotebookLM evidence + manifest, or requires a fully local deterministic renderer. |

Planner request:

```text
Run Process 070 for video path certification.

Desired outcome:
Build a clean two-layer UT system for video production:

1. IMO-Creator v2 owns the parent Blueprint UT / V-layer documentation for each reusable video process.
2. Barton-Processes owns the child executable Process UTs that run, track ORBT, hold gates, and certify.

The Planner should produce a Plan Book, mechanic work orders, auditor packets, smoke-test sequence, and P=1 definition for promoting the video paths to OPERATE.
```

---

## 3. Source-Of-Truth Split

| Layer | Owner | Repo / Folder | What It Owns |
| --- | --- | --- | --- |
| Blueprint / Architecture | IMO-Creator v2 | `imo-creator-v2/docs/processes`, `workers/video-pipeline`, `fleet/content/videos`, `docs/plans` | Parent Blueprint UT / V-layer docs, provider research, constants/variables, routing contracts, examples, scripts, reusable tooling |
| Execution / Operations | Barton-Processes | `Barton-Processes/factory/content/1710-1750`, `1800-cf-stream-upload` | Child executable Process UTs, DOCTRINE, HEIR, ORBT, stop conditions, runtime gates |
| Runtime / Deployment | provider + local surfaces | HeyGen, NotebookLM Chrome MCP, ElevenLabs, local scripts, CF Stream/R2/YouTube | Actual render/generate/upload surfaces |
| Evidence / Observability | LBB, Mission Control, Linear, manifests | LBB `processes`, Linear BAR-388..392, `video-output-manifest.json`, smoke-test records | Role transitions, audit verdicts, artifact manifests, provider job IDs, output paths |

Non-drift rule:

```text
Blueprint explains. Execution runs. Runtime implements. Evidence proves.
IMO-Creator v2 Blueprint UTs are parent UTs.
Barton-Processes Process UTs are executable child UTs.
Do not let runtime/provider behavior silently rewrite the blueprint.
Do not let executable UT changes drift from the parent blueprint.
```

---

## 4. Required Format

| Artifact | Required? | Format |
| --- | --- | --- |
| Plan Book | yes | Plan-Body |
| Blueprint UTs | yes | UT-Body / process-reference in IMO-Creator v2 |
| Executable UTs | yes | PROCESS-UT.md + DOCTRINE.md + heir.yaml + orbt.yaml in Barton-Processes |
| Companion YAML | yes where the artifact is paired or machine-readable | Workflow-Body / Config-Body |
| BS Law | yes | Book + Spine together |
| Atlas references | yes | KEY, BS Law, Structure Manifest, Four-Brain doctrine, child UT guide |
| LBB / MC evidence | yes for OPERATE | Required before P=1 |

Required paired-artifact rule:

```text
The IMO-Creator v2 blueprint and Barton-Processes executable UT must be linked.
If either side changes a contract, the other side must be checked for drift before promotion.
```

---

## 5. Read Set

Planner must inspect these before planning:

| Source | Why Planner Reads It |
| --- | --- |
| `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` | This packet's parent template |
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` | Process 070 operating rules |
| `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` | Process 070 workflow body |
| `imo-creator-v2/docs/processes/VIDEO-GARAGE-TOOLKIT.md` | Current video blueprint/toolkit reference; must be treated as blueprint UT layer, not notes |
| `imo-creator-v2/docs/plans/VIDEO-PATHS-OPERATE-PUNCHLIST.md` | Current path readiness and blockers |
| `imo-creator-v2/docs/plans/BAR-VIDEO-LANE-UTS.plan.md` | Lane plan, C&V extraction, and source mapping |
| `imo-creator-v2/docs/plans/PLAN-MASTER-VIDEO.md` | Master video binding doc |
| `imo-creator-v2/workers/video-pipeline/MANUAL.md` | Trunk-level video generation ratchet |
| `imo-creator-v2/workers/video-pipeline/scripts/route-video-job.ps1` | Current picker harness proof |
| `imo-creator-v2/workers/video-pipeline/scripts/write-video-output-manifest.ps1` | Manifest generator proof |
| `imo-creator-v2/workers/video-pipeline/output/video-output-manifest.json` | Historical MP4 artifact evidence for PROC-1740 |
| `imo-creator-v2/fleet/content/videos/VIDEO-MARKETING-CV-RESEARCH.md` | Four path constant/variable research |
| `imo-creator-v2/fleet/content/videos/HEYGEN-CINEMATIC-VIDEO-RESEARCH.md` | HeyGen cinematic requirements |
| `imo-creator-v2/fleet/content/videos/JULIA-MCCOY-AVATAR-WORKFLOW.md` | HeyGen/ElevenLabs/avatar workflow research |
| `imo-creator-v2/fleet/content/videos/PRODUCTION-STANDARDS-FRAMEWORK.md` | Cross-domain production standards |
| `Barton-Processes/factory/content/1710-heygen-avatar/PROCESS-UT.md` | HeyGen executable UT |
| `Barton-Processes/factory/content/1720-notebooklm-source-video/PROCESS-UT.md` | NotebookLM executable UT |
| `Barton-Processes/factory/content/1730-elevenlabs-cinematic/PROCESS-UT.md` | ElevenLabs executable UT |
| `Barton-Processes/factory/content/1740-claude-code-sovereign/PROCESS-UT.md` | Claude Code / InVideo / sovereign executable UT |
| `Barton-Processes/factory/content/1750-video-picker/PROCESS-UT.md` | Picker executable UT |
| `Barton-Processes/factory/content/1800-cf-stream-upload/PROCESS-UT.md` | Downstream upload handoff |

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

## 6. Documentation Anchors

| Claim / Constraint | Existing Documentation Anchor |
| --- | --- |
| IMO-Creator v2 owns the blueprint / V-layer docs | `imo-creator-v2/docs/processes/VIDEO-GARAGE-TOOLKIT.md` |
| Barton-Processes owns executable process UTs | `Barton-Processes/factory/content/1710-1750/*/PROCESS-UT.md` |
| Process 070 is Planner -> Foreman -> Mechanic -> Auditor | `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` |
| Video path picker has local proof | `imo-creator-v2/workers/video-pipeline/scripts/route-video-job.ps1` and examples |
| PROC-1740 has historical MP4 proof | `imo-creator-v2/workers/video-pipeline/output/video-output-manifest.json` |
| HeyGen API credentials/avatar/voice were verified without printing secrets | `Barton-Processes/factory/content/1710-heygen-avatar/PROCESS-UT.md` live verification log |
| NotebookLM must be Chrome MCP/browser-driven, not fake public API | `Barton-Processes/factory/content/1720-notebooklm-source-video/PROCESS-UT.md` |
| ElevenLabs is a model-picker lane, not only voice | `Barton-Processes/factory/content/1730-elevenlabs-cinematic/PROCESS-UT.md` |
| Picker must route exactly one lane or return REPAIR/HALT | `Barton-Processes/factory/content/1750-video-picker/PROCESS-UT.md` |

---

## 7. Research / Brainstorming Packet

| Input Type | Location / Record | How Planner Should Use It |
| --- | --- | --- |
| Brainstorm notes | Current Codex/user session context | Extract the two-type build rule and parent/child UT relationship |
| Existing BAR notes | Linear BAR-388, BAR-389, BAR-390, BAR-391, BAR-392 | Pull current status, blockers, comments, and acceptance criteria |
| Operator observations | Dave: IMO-Creator v2 Blueprint is also a UT | Treat as sovereign clarification; encode as non-drift invariant |
| Operator observations | Dave: video tools are cross-domain garage tools | Treat as blueprint placement rule |
| Runtime evidence | `video-output-manifest.json` | Treat as historical proof for PROC-1740, not full OPERATE certification |

Fact handling rule:

```text
Brainstorming is input, not certification.
Sovereign clarifications become constraints.
P=1 still requires cited documentation, runtime evidence, or sovereign confirmation.
```

---

## 8. LB&B Pull Contract

| LB&B Field | Fill |
| --- | --- |
| Work IDs / BAR IDs | BAR-388, BAR-389, BAR-390, BAR-391, BAR-392, BAR-396, BAR-VIDEO-PATH-CERTIFICATION |
| Search Terms | video path, video picker, HeyGen, NotebookLM, ElevenLabs, Claude Code sovereign, InVideo, PROC-1710, PROC-1720, PROC-1730, PROC-1740, PROC-1750 |
| Time Window | since 2026-05-04 |
| Required Records | Planner notes, Foreman dispatches, Mechanic outputs, Auditor verdicts, closeout logs |
| Evidence Needed For P=1 | role transition logs, audit verdicts, smoke-test evidence, artifact/output records |

LB&B rule:

```text
Before planning, pull relevant LB&B records when they exist.
During execution, every role transition and closeout must be logged to LB&B when operational or compliance-relevant.
If LB&B is unavailable, Planner must mark evidence as blocked or deferred.
```

---

## 9. Non-Drift Invariants

| ID | Invariant |
| --- | --- |
| INV-01 | IMO-Creator v2 Blueprint is a UT, not scratch documentation. |
| INV-02 | IMO-Creator v2 owns parent Blueprint UT / V-layer documentation for reusable video capabilities. |
| INV-03 | Barton-Processes owns child executable Process UTs for running the video processes. |
| INV-04 | Blueprint explains. Execution runs. Runtime implements. Evidence proves. |
| INV-05 | Process 070 orchestrates Planner -> Foreman -> Mechanic -> Auditor; it is not the physical home of the video UTs. |
| INV-06 | Mechanic cannot audit its own work. |
| INV-07 | The video system is cross-domain and must not be hardcoded to one branch. |
| INV-08 | PROC-1750 is the front door for script/source intake and must route exactly one lane or return REPAIR/HALT. |
| INV-09 | Provider-specific implementation details cannot silently rewrite the blueprint. |
| INV-10 | No secrets may be printed or stored in process docs. |
| INV-11 | OPERATE requires smoke proof and evidence, not just filled docs. |
| INV-12 | PROC-1740 must explicitly resolve whether "sovereign" allows provider-assisted renders with manifests or requires a fully local deterministic renderer. |

Common invariants:

| ID | Invariant |
| --- | --- |
| INV-COMMON-01 | The Planner owns the plan; the intake owns only desired outcome and constraints. |
| INV-COMMON-02 | Foreman dispatches; Mechanic builds; Auditor certifies. |
| INV-COMMON-03 | Mechanic cannot audit its own work. |
| INV-COMMON-04 | BS Law applies to every durable structured artifact. |
| INV-COMMON-05 | Blueprint, execution, runtime, and evidence layers must not drift. |

---

## 10. Input Contract

The operator has provided or explicitly deferred:

| Input | Required? | Rule |
| --- | --- | --- |
| Target process | yes | PROC-1710, PROC-1720, PROC-1730, PROC-1740, PROC-1750, PROC-1800 |
| Desired outcome | yes | Create linked parent Blueprint UTs and child executable UTs; promote paths toward OPERATE |
| Blueprint home | yes | `imo-creator-v2/docs/processes`, `workers/video-pipeline`, `fleet/content/videos`, `docs/plans` |
| Execution home | yes | `Barton-Processes/factory/content/1710-1750`, `1800-cf-stream-upload` |
| Runtime surface | yes | HeyGen, NotebookLM Chrome MCP, ElevenLabs, local scripts, CF Stream/R2/YouTube |
| Evidence target | yes | LBB, Linear, manifests, provider job IDs/output paths |
| Brainstorming packet | yes | Current Codex/user session and existing video docs |
| LB&B search contract | yes | See section 8 |
| Protected constraints | yes | No secrets printed; no locked constant modification; mechanic != auditor |
| P=1 definition | yes | See section 15 |

---

## 11. Storage / Evidence Contract

| Store | Role | Timing |
| --- | --- | --- |
| R2 / CF Stream | Storage/output surface for MP4 artifacts | After output verification |
| D1 / Mission Control | Registry / operator visibility if wired | Before final OPERATE if required by plan |
| LBB | Compliance logbook and durable memory | At role transitions and closeout |
| Linear | BAR status and operator-facing issue state | During run and closeout |
| GitHub / local git | Versioned source | After audited file changes |
| Provider dashboards | Runtime status | During smoke tests |

Rules:

```text
Do not call P=1 without required evidence surfaces.
Do not treat a provider dashboard as the only durable evidence.
Every successful video output needs artifact metadata, path/ID, and handoff evidence.
```

---

## 12. Planner Deliverables

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
| LB&B records used or required | yes |
| Blueprint UT creation/repair work orders | yes |
| Executable UT repair work orders | yes |
| Smoke-test sequence | yes |
| Brainstorming claims promoted to facts | yes |
| Brainstorming claims left as assumptions | yes |

Planner must not be forced into a preselected implementation route unless the sovereign explicitly locks it.

---

## 13. Mechanic Dispatch Hints

Allowed write scope:

- `imo-creator-v2/docs/processes/`
- `imo-creator-v2/docs/plans/`
- `imo-creator-v2/workers/video-pipeline/`
- `imo-creator-v2/fleet/content/videos/`
- `Barton-Processes/factory/content/1710-1750/`
- `Barton-Processes/factory/content/1800-cf-stream-upload/`
- `Barton-Processes/docs/plans/BAR-VIDEO-PATH-CERTIFICATION/`

Forbidden:

- Printing or committing secrets.
- Moving executable process UTs into PROC-070.
- Treating IMO-Creator v2 blueprint docs as non-UT scratch notes.
- Letting a mechanic certify its own work.
- Marking any path OPERATE without smoke proof.

---

## 14. Auditor Packet Requirements

Auditor should receive:

| Audit Area | Evidence |
| --- | --- |
| BS Law | MD/YAML structure and parent/child UT relationship |
| UT conformance | Blueprint UTs and executable UTs have required sections/anchors where applicable |
| Source-of-truth split | Blueprint vs execution vs runtime vs evidence |
| Scope | Only allowed files changed |
| Runtime safety | No secrets printed; provider smoke tests bounded |
| Evidence | LBB / Linear / manifest / provider job IDs / output paths |
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

## 15. P=1 Definition

P=1 when:

1. IMO-Creator v2 contains parent Blueprint UT documentation for the reusable video capability and each lane or a clearly indexed lane section.
2. Barton-Processes contains executable child UTs for PROC-1710, PROC-1720, PROC-1730, PROC-1740, PROC-1750, and PROC-1800 as needed.
3. Each executable UT links back to the relevant IMO-Creator v2 blueprint source.
4. Each blueprint source links forward to the executable Barton-Processes UT.
5. PROC-1750 picker can route clear script/source packets and reject ambiguous packets.
6. Each lane has a defined smoke test and evidence requirement.
7. No secrets are printed or stored.
8. Linear BAR-388 through BAR-392 are updated with current state.
9. LBB evidence is logged or explicitly marked blocked/deferred by Planner.
10. Auditor certifies.

Do not leave P=1 implied. The Planner needs explicit done conditions.

---

## 16. Open Questions

Only questions that block planning:

| Question | Why It Blocks |
| --- | --- |
| Does PROC-1740 "sovereign" mean provider-assisted Claude/InVideo/NotebookLM flow with manifest is sufficient, or must it mean fully local deterministic rendering? | Determines whether PROC-1740 can move to audit now or needs a renderer build work order. |
| Should the first official intake surface be CLI (`route-video-job.ps1`) or Mission Control UI/API? | Determines what evidence is required before PROC-1750 can be marked OPERATE. |
| Are Blueprint UTs per lane separate files, or one parent Video Blueprint UT with lane sections? | Determines the exact IMO-Creator v2 artifact shape. |

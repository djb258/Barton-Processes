# FCE Run Planner Intake
## Process 070 Planner Source Packet for PROC-060 FCE Run
### Status: READY-FOR-PLANNER
### Medium: planner-intake
### Business: imo-creator

---

## 1. Purpose

This packet tells the Process 070 Planner what outcome is wanted for the canonical FCE run process.

The Planner owns the plan. This intake owns the destination, boundaries, evidence, non-drift invariants, and P=1 definition.

Desired durable output from the full Four-Brain cycle:

- `PROCESS-UT.md` under the canonical PROC-060 FCE run home
- companion workflow YAML under the same PROC-060 process home
- Mission Control visibility for the IMO trail, R2/OpenRouter workbench loop, D1 vault, FCE library status, and downstream DMJ readiness

The MD and YAML must not drift.

Paired YAML: `fce-run-planner-intake.yaml`

---

## 2. Planner Request

| Field | Fill |
| --- | --- |
| BAR / Work ID | `BAR-FCE-RUN-060-PLANNER` |
| Target Process | `PROC-060 / FCE run process` |
| Desired Outcome | Produce the plan for one canonical process that runs an FCE from named domain intake through US, K=C, UP, Codex audit, D1 vaulting, R2 cleanup, FCE library registration, and downstream DMJ readiness. |
| Operating Mode | BUILD |
| Due / Timing | No fixed deadline; ready for Planner intake now. |
| Sovereign Decision Needed | Yes: whether downstream DMJ gets its own process number. Default recommendation is yes. |

Planner request:

```text
Run Process 070 for PROC-060 FCE run.

Desired outcome:
Build a Plan Book for the canonical PROC-060 FCE run process pair. The plan must specify the durable PROCESS-UT.md and companion workflow YAML that explain exactly how to run an FCE without drift.
```

---

## 3. Source-Of-Truth Split

| Layer | Owner | Repo / Folder | What It Owns |
| --- | --- | --- | --- |
| Blueprint / Architecture | Dyno engine blueprint | `dyno-engine/engine/us.py`, `dyno-engine/engine/up.py` | Locked blueprint engine behavior. `us.py` solves M; `up.py` consumes I using locked M. |
| Execution / Operations | Barton processes | `Barton-Processes/factory/imo-creator/060-run-dyno/` | Canonical operational process home for running FCEs. |
| Runtime / Deployment | Mission Control / MC API / runner | `imo-creator-v2/workers/mission-control`, `imo-creator-v2/workers/mission-control-api`, `imo-creator-v2/atlas/dyno/run_fce.py` | Operator surface, intake, cycle/vault endpoints, and runner execution. |
| Evidence / Observability | R2, D1, LBB, FCE library | `r2://svg-files/dyno-runs/{run_id}/`, `mission-control.dyno_run`, `mission-control.dyno_run_cycle`, LBB, `imo-creator-v2/atlas/fce-library` | Workbench artifacts, every cycle from all three model tests, completed-run vault, logbook memory, certified library shelf. |

Non-drift rule:

```text
Blueprint explains. Execution runs. Runtime implements. Evidence proves.
Do not let one layer silently become the source of truth for another.
```

---

## 4. Required Format

| Artifact | Required? | Format |
| --- | --- | --- |
| Plan Book | yes | Plan-Body |
| PROC-060 process doc | yes | UT-Body |
| Companion YAML | yes | Workflow-Body |
| BS Law | yes | Book + Spine together |
| Atlas references | yes | KEY, BS Law, Structure Manifest, Four-Brain doctrine, FCE doctrine |
| LBB / MC evidence | yes | Required before P=1 |

Required paired-artifact rule:

```text
The final PROC-060 process must produce or repair both MD and YAML.
The MD and YAML must share the same step IDs, gates, invariants, and storage semantics.
```

---

## 5. Read Set

Planner must inspect these before planning:

| Source | Why Planner Reads It |
| --- | --- |
| `imo-creator-v2/atlas/constants/KEY.md` | Vocabulary and engine terms. |
| `imo-creator-v2/atlas/constants/BS_LAW.md` | Book + Spine conformance. |
| `imo-creator-v2/atlas/manifests/STRUCTURE_MANIFEST.yaml` | CTB / locked structure. |
| `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` | Planner / Foreman / Mechanic / Auditor separation. |
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` | Process 070 operating rules. |
| `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` | Process 070 workflow body. |
| `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` | Parent intake template this packet instantiates. |
| `imo-creator-v2/atlas/FCE_RUN_CHECKLIST.md` | Current operator checklist for FCE runs. |
| `imo-creator-v2/atlas/FCE_RUN_CHECKLIST.yaml` | Agent-readable checklist mirror. |
| `imo-creator-v2/atlas/FCE_LIFECYCLE_RUNBOOK.md` | Full lifecycle and storage sequence. |
| `imo-creator-v2/atlas/FCE_BUILD_STEPS.md` | US loop, K=C, UP, four-column doctrine. |
| `imo-creator-v2/atlas/FCE_FILL_INSTRUCTIONS.md` | Four-column fill doctrine and output gates. |
| `Barton-Processes/factory/imo-creator/060-run-dyno/PROCESS-UT.md` | Current PROC-060 operator process home. |
| `Barton-Processes/factory/imo-creator/080-fce-fill/PROCESS-UT.md` | Reference-only fill logic to absorb into PROC-060. |
| `Barton-Processes/factory/imo-creator/090-fce-computer-programming/PROCESS-UT.md` | FCE artifact/library example, not runtime process. |
| `dyno-engine/engine/us.py` | Locked US blueprint; read-only. |
| `dyno-engine/engine/up.py` | Locked UP blueprint; read-only. |
| `imo-creator-v2/workers/mission-control-api/migrations/0018_dyno_run.sql` | D1 vault/cycle schema. |
| `imo-creator-v2/workers/mission-control-api/migrations/0018_dyno_run.schema-doc.yaml` | AI-readable D1 vault/cycle contract. |
| `imo-creator-v2/workers/mission-control-api/src/routes/dyno.ts` | Mission Control API runtime wiring. |
| `imo-creator-v2/workers/mission-control/src/pages/DynoOutput.tsx` | Mission Control operator visibility. |
| `imo-creator-v2/factory/agents/up/runs/discover-fce-007a-valuation-technical-seo-health-/engine-final.json` | FCE-007 Valuation output example. |
| `imo-creator-v2/factory/agents/up/runs/discover-fce-007b-concentration-traffic-concentra/engine-final.json` | FCE-007 Concentration output example. |
| `imo-creator-v2/factory/agents/up/runs/discover-fce-007c-trend-domain-authority-growth-t/engine-final.json` | FCE-007 Trend output example. |
| `imo-creator-v2/factory/agents/up/runs/discover-fce-007d-liquidity-conversion-plumbing-f/engine-final.json` | FCE-007 Liquidity output example. |

---

## 6. Documentation Anchors

| Claim / Constraint | Existing Documentation Anchor |
| --- | --- |
| Domain string is topic + description as one input | `imo-creator-v2/atlas/FCE_RUN_CHECKLIST.md` Step 1 and `FCE_LIFECYCLE_RUNBOOK.md` fire command. |
| R2 is first and D1 is second | `imo-creator-v2/atlas/FCE_RUN_CHECKLIST.md` doctrine lock: R2 first, D1 second. |
| R2 holds artifacts during cycles; D1 takes post-completion index/vault | `imo-creator-v2/atlas/FCE_LIFECYCLE_RUNBOOK.md` doctrine lock. |
| D1 stores parent run metadata and per-cycle rows | `imo-creator-v2/workers/mission-control-api/migrations/0018_dyno_run.sql`. |
| Full cycle artifacts live in R2; D1 cycle rows index every cycle/model | `imo-creator-v2/workers/mission-control-api/migrations/0018_dyno_run.schema-doc.yaml`. |
| DMJ is deferred at N=1 and queued when N >= 2 in the same family | `imo-creator-v2/atlas/FCE_RUN_CHECKLIST.md` and `FCE_LIFECYCLE_RUNBOOK.md`. |
| OpenRouter uses expensive models only | `imo-creator-v2/atlas/FCE_RUN_CHECKLIST.md` and `FCE_LIFECYCLE_RUNBOOK.md`. |
| `us.py` and `up.py` are locked engine files | AGENTS locked constants and `dyno-engine/engine/us.py`, `dyno-engine/engine/up.py`. |
| FCE-007 is output evidence, not process definition | `imo-creator-v2/factory/agents/up/runs/discover-fce-007{a,b,c,d}-*/engine-final.json`. |

---

## 7. Research / Brainstorming Packet

| Input Type | Location / Record | How Planner Should Use It |
| --- | --- | --- |
| Operator observations | Current Codex thread | Treat as confirmed only where backed by source docs or explicit sovereign correction. |
| Current planner packet | `Barton-Processes/docs/plans/BAR-FCE-RUN-060-PLANNER/FCE-RUN-PLANNER-INTAKE.md` | Use as the source packet, not final process output. |
| Current YAML mirror | `Barton-Processes/docs/plans/BAR-FCE-RUN-060-PLANNER/fce-run-planner-intake.yaml` | Use as agent-readable mirror of this packet. |
| Mission Control source changes | `imo-creator-v2/workers/mission-control-api/src/routes/dyno.ts`, `imo-creator-v2/workers/mission-control/src/pages/DynoOutput.tsx` | Treat as runtime evidence target and current wiring state. |

Fact handling rule:

```text
Brainstorming is input, not certification.
The Planner can use it to form the plan, but P=1 requires cited documentation, runtime evidence, or sovereign confirmation.
```

---

## 8. LB&B Pull Contract

| LB&B Field | Fill |
| --- | --- |
| Work IDs / BAR IDs | `BAR-FCE-RUN-060-PLANNER`, `PROC-060`, `PROC-070`, `PROC-080`, `PROC-090`, FCE-007 run IDs |
| Search Terms | FCE, Dyno, US, UP, K=C, R2 first, D1 vault, OpenRouter expensive, DMJ, FCE library, Mission Control |
| Time Window | Since 2026-05-01, plus all records tied to FCE Computer Programming and FCE-007 |
| Required Records | Planner notes, Foreman dispatches, Mechanic outputs, Auditor verdicts, D1/R2 vault doctrine records, closeout logs |
| Evidence Needed For P=1 | LB&B records proving Planner dispatch, Foreman dispatch, Mechanic build, Auditor verdict, and final closeout |

LB&B rule:

```text
Before planning, pull relevant LB&B records when they exist.
During execution, every role transition and closeout must be logged to LB&B.
If LB&B is unavailable, Planner must mark evidence as blocked or deferred.
```

---

## 9. Non-Drift Invariants

| ID | Invariant |
| --- | --- |
| INV-01 | PROC-060 is the one process that runs an FCE. |
| INV-02 | PROC-070 is the Four-Brain build pipeline: Planner -> Foreman -> Mechanic -> Auditor. It does not replace PROC-060. |
| INV-03 | PROC-080 content is reference/fill logic to absorb into PROC-060. It must not remain a second FCE run process. |
| INV-04 | PROC-090 is an FCE artifact/library entry. It is not a process for running FCEs. |
| INV-05 | US solves for M: the domain structure/constants. |
| INV-06 | US P=1 is fixed: all four FCE columns are covered and every leaf is decomposed to primitive. |
| INV-07 | K=C locks M after US discovery. |
| INV-08 | UP works through I using locked M. |
| INV-09 | UP tolerance tells the process when to stop and emit O. |
| INV-10 | `us.py` and `up.py` are locked/read-only. No plan may ask a Mechanic to edit them. |
| INV-11 | Initial domain + description intake goes to R2 first; D1 does not precede the R2 workbench. |
| INV-12 | R2 and OpenRouter are the active workbench loop for cycle artifacts, model outputs, corrections, consensus, and back-propagation. |
| INV-13 | D1 is the completed-run vault. Nothing moves from R2 into D1 until the run is done and checked. |
| INV-14 | All FCE runs use OpenRouter with the expensive three-model set. No cheap-tier rotation. |
| INV-15 | R2 is cleaned/reset for the next FCE only after the completed package has been vaulted into D1. |
| INV-16 | The FCE library receives the artifact only after Codex audit/check and D1 vault success. |
| INV-17 | D1 vault stores every cycle from all three OpenRouter model tests under the sovereign ID. |
| INV-18 | DMJ does not run inside a single-FCE PROC-060 run. DMJ is deferred until multiple locked FCEs exist in the same family. |

---

## 10. Input Contract

The operator must provide or explicitly defer:

| Input | Required? | Rule |
| --- | --- | --- |
| Target process | yes | `PROC-060 / FCE run process` |
| Desired outcome | yes | Canonical MD/YAML process pair plus MC evidence wiring. |
| Blueprint home | yes | `dyno-engine/engine/us.py`, `dyno-engine/engine/up.py` |
| Execution home | yes | `Barton-Processes/factory/imo-creator/060-run-dyno/` |
| Runtime surface | yes | Mission Control, MC API, FCE runner |
| Evidence target | yes | R2, D1, LBB, MC, FCE library |
| Brainstorming packet | yes | This thread and this intake packet |
| LB&B search contract | yes | See section 8 |
| Protected constraints | yes | No edits to `us.py` or `up.py`; no cheap model tier; no D1 scratchpad; no DMJ at N=1. |
| P=1 definition | yes | See section 15 |

FCE run input values:

| Input | Rule |
| --- | --- |
| topic | Short FCE name, for example `SQL`. |
| description | Full scope sentence. |
| domain_string | One string: `"<topic> — <description in detail>"`. |
| fce_id | Unique slug, checked against the FCE registry. |
| family | Family name for downstream DMJ grouping. |
| up_tolerance | Domain-specific stop/proof condition for UP; this is not US P=1. |
| model_set | OpenRouter expensive three-model set. |

---

## 11. Storage / Evidence Contract

| Store | Role | Timing |
| --- | --- | --- |
| R2 + OpenRouter | First landing zone and active workbench/model loop | Active during intake, US, K=C, model comparison, back-prop, corrections, UP, recipe synthesis, and Codex audit/check. |
| D1 | Completed-run vault of record | Receives the completed/audited package from R2 only after Codex check passes; stores sovereign ID, every cycle, all three model-test outputs, final O, and artifact manifest. |
| R2 cleanup | Workbench reset | Happens only after successful D1 vault write. |
| Mission Control | Operator visibility | Shows sovereign ID, R2 workbench status, cycle rows, three-model visibility, audit/vault/library state, and DMJ readiness. |
| FCE library | Certified artifact shelf | Receives the FCE only after Codex audit/check and D1 vault success. |
| DMJ process | Downstream convergence analysis | Runs only after multiple locked FCEs exist in the same family; output goes back into D1 as family-level convergence evidence. |
| LBB | Compliance logbook and durable memory | At role transitions, audit, vault, library registration, and closeout. |
| GitHub | Versioned source | After audited file changes. |

Rules:

```text
Do not use D1 as scratchpad.
Do not clean R2 until the completed package is vaulted into D1.
Do not call P=1 without MC, D1, R2, LBB, and audit evidence.
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
| Brainstorming claims promoted to facts | yes |
| Brainstorming claims left as assumptions | yes |

Planner must not be forced into a preselected implementation route unless the sovereign explicitly locks it.

---

## 13. Mechanic Dispatch Hints

Allowed write scope for future Mechanic work orders:

- `Barton-Processes/factory/imo-creator/060-run-dyno/PROCESS-UT.md`
- companion PROC-060 workflow YAML selected by Planner
- MC runtime files if Planner includes runtime evidence wiring
- documentation/index files explicitly named by Foreman

Forbidden:

- editing `dyno-engine/engine/us.py`
- editing `dyno-engine/engine/up.py`
- introducing a second FCE run process outside PROC-060
- running DMJ inside a single-FCE PROC-060 run
- using D1 as the live workbench/scratchpad
- cleaning R2 before D1 vault success
- allowing Mechanic to audit its own work

---

## 14. Auditor Packet Requirements

Auditor should receive:

| Audit Area | Evidence |
| --- | --- |
| BS Law | MD/YAML structure and paired artifact parity. |
| UT conformance | All required UT sections if UT artifact is built. |
| Source-of-truth split | Blueprint vs execution vs runtime vs evidence. |
| Scope | Only allowed files changed. |
| Runtime safety | MC/API changes do not break existing routes; D1 is vault, not scratchpad. |
| Evidence | R2/D1/LBB/MC/FCE library requirements are represented. |
| FCE doctrine | US solves M; K=C locks M; UP consumes I using locked M until tolerance; four columns preserved. |
| DMJ boundary | DMJ deferred at N=1 and queued only when N >= 2 locked FCEs exist in the same family. |
| Research provenance | Brainstorming claims resolved into facts, assumptions, or open questions. |
| Aviation | Mechanic != Auditor. |

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

1. Planner returns a Plan Book for PROC-060 that preserves all non-drift invariants in this packet.
2. Planner specifies a durable PROC-060 `PROCESS-UT.md` and companion workflow YAML with matching step IDs and gates.
3. The planned process separates US P=1 from UP tolerance.
4. The planned process states that US solves M, K=C locks M, and UP consumes I using locked M until tolerance emits O.
5. The planned process preserves the four FCE columns exactly: Valuation, Concentration, Trend, Liquidity.
6. The planned process treats PROC-080 as absorbed reference material and PROC-090 as artifact/library evidence.
7. The planned process forbids edits to `us.py` and `up.py`.
8. The planned process uses R2 + OpenRouter as the live workbench loop and D1 only as the completed-run vault.
9. The planned process stores every cycle from all three OpenRouter model tests in D1 under the sovereign ID during vaulting.
10. The planned process cleans R2 only after D1 vault success.
11. The planned process registers the FCE into the library only after Codex audit/check and D1 vault success.
12. The planned process defers DMJ for N=1 and only queues DMJ when multiple locked FCEs exist in the same family.
13. Mission Control visibility is included in the evidence requirements.
14. LB&B role transition and closeout evidence is required.
15. Auditor certifies.

---

## 16. Open Questions

| Question | Why It Blocks |
| --- | --- |
| Should downstream DMJ receive a new process number separate from PROC-060? | It affects where the Planner routes convergence work after multiple FCEs are locked. Default recommendation: yes. |

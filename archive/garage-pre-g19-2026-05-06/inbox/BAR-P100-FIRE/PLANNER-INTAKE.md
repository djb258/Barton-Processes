# Planner Intake: BAR-P100-FIRE
## Process 070 Garage Packet For Process 100 Email Firing

## 1. Planner Request

| Field | Fill |
| --- | --- |
| BAR / Work ID | `BAR-P100-FIRE` |
| Target Process | `PROC-100 / bp.100 / LCS Pipeline` |
| Desired Outcome | Produce a Plan Book that gets Process 100 ready to fire daily outbound emails with evidence, domain safety, servicing-agent limits, and Mission Control visibility. |
| Operating Mode | REPAIR / OPERATE |
| Due / Timing | Today |
| Sovereign Decision Needed | Only if Planner finds a domain, volume, or compliance constraint that blocks daily firing. |

Planner request:

```text
Run Process 070 for BAR-P100-FIRE.

Desired outcome:
Create the Plan Book for repairing and operating Process 100 so it can start firing daily emails through the LCS pipeline. Do not prescribe implementation details beyond source-of-truth constraints. Give Foreman enough to dispatch Mechanic and Auditor without guessing.
```

## 2. Garage Intake Status

| Field | Fill |
| --- | --- |
| garage_status | READY_FOR_PLANNER |
| intake_path | `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-P100-FIRE/PLANNER-INTAKE.md` |
| intake_yaml_path | `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-P100-FIRE/planner-intake.yaml` |
| requested_by | Dave Barton / Codex intake |
| ready_at | 2026-05-05T00:00:00Z |
| planner_claimed_by | blank |
| planner_claimed_at | blank |
| next_artifact | `Barton-Processes/docs/plans/BAR-P100-FIRE/PLAN-BOOK.md` |

## 3. Source-Of-Truth Split

| Layer | Owner | Repo / Folder | What It Owns |
| --- | --- | --- | --- |
| Blueprint / Architecture | Company Lifecycle | `company-lifecycle-cl/docs/lcs/` | LCS blueprint, CTB explanation, and architecture context. |
| Execution / Operations | Barton-Processes | `Barton-Processes/factory/cl/100-lcs-pipeline/` | Actual Process 100 movement, cron, worker, D1, delivery, and operational docs. |
| Runtime / Deployment | Cloudflare / Worker | `Barton-Processes/factory/cl/100-lcs-pipeline/wrangler.toml`, `src/**` | Worker routes, scheduled run, queue handling, bindings, delivery path. |
| Evidence / Observability | LB&B, Mission Control, D1, R2, Mailgun/Cloudflare checks | Paths/tables/endpoints discovered by Planner | Proof that the process can run, fire safely, and be observed. |

Non-drift rule:

```text
Company Lifecycle explains LCS. Barton-Processes runs Process 100. Mission Control shows state. LB&B records compliance. Do not make Company Lifecycle the execution surface.
```

## 4. Required Format

| Artifact | Required? | Format |
| --- | --- | --- |
| Plan Book | yes | Plan-Body |
| Mechanic dispatch packet | yes | Scoped Foreman work order |
| Auditor packet | yes | P=1/P=0 verdict packet |
| UT repair targets | if Planner requires | UT-Body |
| Companion YAML repair targets | if Planner requires | Workflow-Body / Config-Body |
| BS Law | yes | Book + Spine together |
| LBB / MC evidence | yes | Required before final P=1 |

## 5. Read Set

Planner must inspect these before planning:

| Source | Why Planner Reads It |
| --- | --- |
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` | Process 070 roles and gates. |
| `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` | Process 070 workflow contract. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/PROCESS-UT.md` | Existing Process 100 UT. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/wrangler.toml` | Runtime bindings, cron, worker name, vars. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/src/index.ts` | Scheduled, queue, fetch, and manual run behavior. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/src/compiler.ts` | CID/SID/MID compile flow. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/src/spokes/delivery.ts` | Delivery/mail path. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/src/spokes/signal-intake.ts` | Signal intake path. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/src/migrations/001_lcs_tables.sql` | D1 tables used by Process 100. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/PROCESS-100-STEP-BY-STEP.md` | Current walkthrough. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/PROCESS-100-STEP-BY-STEP.yaml` | Machine-readable walkthrough. |
| `Barton-Processes/factory/cl/100-lcs-pipeline/DOMAIN-MAINTENANCE.md` | Domain rotation and protected-domain notes. |
| `Barton-Processes/docs/plans/BAR-P100-FIRE.plan.md` | Existing rough Plan Book context. |
| `company-lifecycle-cl/docs/lcs/LCS-BLUEPRINT-UT.md` | LCS blueprint source. |
| `company-lifecycle-cl/docs/lcs/LCS-BLUEPRINT.yaml` | Paired blueprint YAML. |

Always consider Atlas / BS Law references where available in `imo-creator-v2/atlas`.

## 6. Documentation Anchors

| Claim / Constraint | Existing Documentation Anchor |
| --- | --- |
| Barton-Processes is the execution surface for Process 100. | `Barton-Processes/factory/cl/100-lcs-pipeline/` |
| Company Lifecycle is the LCS blueprint home. | `company-lifecycle-cl/docs/lcs/LCS-BLUEPRINT-UT.md` |
| Process 070 is Planner -> Foreman -> Mechanic -> Auditor. | `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` |
| Process 100 must expose operator visibility through Mission Control/map layer. | Prior sovereign instruction; Planner must locate or request MC evidence path. |
| R2-first / D1-second applies where cycle/backprop artifacts exist. | Existing FCE planner intake precedent; Planner decides applicability to Process 100. |

## 7. Research / Brainstorming Packet

| Input Type | Location / Record | How Planner Should Use It |
| --- | --- | --- |
| Chat / sovereign notes | This intake and prior session notes | Extract desired outcome and constraints; verify against docs/runtime. |
| Existing Process 100 docs | `factory/cl/100-lcs-pipeline/*.md`, `*.yaml` | Use as current working documentation. |
| Existing LCS blueprint docs | `company-lifecycle-cl/docs/lcs/*` | Use as architecture source, not runtime source. |

Fact handling rule:

```text
Brainstorming is input, not certification. Planner may use it to form the plan, but P=1 requires cited documentation, runtime evidence, or sovereign confirmation.
```

## 8. LB&B Pull Contract

| LB&B Field | Fill |
| --- | --- |
| Work IDs / BAR IDs | `BAR-P100-FIRE`, `PROC-100`, `LCS`, `Process 100` |
| Search Terms | `process 100`, `LCS`, `daily email`, `servicing agent`, `Mailgun`, `Cloudflare domains`, `Mission Control` |
| Time Window | Current session plus recent Process 100 work |
| Required Records | Planner notes, Foreman dispatches, Mechanic outputs, Auditor verdicts, closeout logs if available |
| Evidence Needed For P=1 | Role transitions, audit result, runtime proof, MC visibility proof, delivery/domain safety proof |

## 9. Connector / Run Binding

| Connector | Required? | Purpose | Credential / Access Source | Evidence Expected |
| --- | --- | --- | --- | --- |
| LB&B | yes if available | Pull prior memory and write role transitions | `LBB_API_KEY` / approved connector | Query results and transition rows |
| GitHub | yes | Versioned source and final push | GH CLI / connector | Commit SHA / pushed branch |
| Atlas | yes | BS Law, constants, Four-Brain doctrine | Local repo path | Cited files/sections |
| Mission Control | yes | Operator map/layer visibility for Process 100 | Worker/D1/MC connector | Run status or blocker |
| Cloudflare | yes | Domain, D1, R2, worker checks | Doppler Cloudflare bindings | Zone/domain/D1/R2 evidence |
| Mailgun | yes | Delivery/domain readiness | Doppler or approved connector | Domain and sending proof |

## 10. Non-Drift Invariants

| ID | Invariant |
| --- | --- |
| INV-01 | Barton-Processes owns Process 100 execution. |
| INV-02 | Company Lifecycle owns LCS blueprint and architecture. |
| INV-03 | Planner writes the Plan Book; Mechanic builds; Auditor certifies. |
| INV-04 | Mechanic cannot audit its own work. |
| INV-05 | Protected domains `svg.agency` and `svgwv.com` must not be burned for cold outreach. |
| INV-06 | Process 100 daily firing must respect servicing-agent constraints and radius targeting. |
| INV-07 | Process 100 depends on signals from outreach sub-hubs including people, social platform/blog, and DOL/static data where applicable. |
| INV-08 | Mission Control must show operator visibility, ideally as IMO/map layer: input, middle, output. |
| INV-09 | Do not call P=1 without runtime/evidence surfaces. |

## 11. Planner Deliverables

Planner should return:

| Deliverable | Required |
| --- | --- |
| Plan Book path | yes |
| Read set | yes |
| Source-of-truth split | yes |
| Required Mechanic work orders | yes |
| Auditor packet | yes |
| P=1 definition | yes |
| Stop conditions | yes |
| Open blockers | yes |
| Connector evidence needed | yes |
| LB&B records used or required | yes |
| 070 handoff path | yes |

## 12. P=1 Definition

P=1 when:

1. Planner produces a Plan Book at `Barton-Processes/docs/plans/BAR-P100-FIRE/PLAN-BOOK.md`.
2. The Plan Book gives Foreman enough to dispatch Mechanic and Auditor work without guessing.
3. Daily firing path, servicing-agent filter, domain safety, delivery path, MC visibility, LBB logging, D1/R2 evidence, and protected-domain constraints are explicit.
4. Open blockers are either resolved or elevated as sovereign decisions.

## 13. Open Questions

| Question | Why It Blocks |
| --- | --- |
| Which exact runtime evidence proves Process 100 has fired successfully today? | Needed for final operational P=1, but not needed for Planner to begin. |

# BAR-P100-FIRE Plan Book
## Process 070 Four-Brain Dispatch: Get Process 100 Ready To Fire Emails

### Status

| Field | Value |
| --- | --- |
| BAR | BAR-P100-FIRE |
| Process invoked | PROC-070 Four-Brain Aviation Model |
| Target process | PROC-100 / bp.100 / LCS Pipeline |
| Source of truth | `Barton-Processes/factory/cl/100-lcs-pipeline/` |
| Requested outcome | Start firing outbound emails from Process 100 through a controlled, auditable path |
| ORBT | REPAIR -> controlled fire -> audit -> OPERATE candidate |
| Created | 2026-05-05 |
| Planner input owner | Codex |
| Sovereign | Dave Barton |

### BS Law Conformance

This Plan Book is a durable process artifact. It must be read as both Book and Spine under BS Law.

| BS Law Arm | This Plan Carries |
| --- | --- |
| Book Law structure | BAR identity, purpose, reads, scope, work orders, gates, evidence, stop conditions, role separation. |
| Spine content | HEIR, ORBT, CTB position, IMO, DMJ, constants/variables, execution trace, P=1 definition. |

Outside-Dewey stream:

| Field | Value |
| --- | --- |
| species | Plan-Body |
| sovereign_ref | company-lifecycle |
| hub_id | outreach |
| ctb_placement | barton-enterprises/company-lifecycle/outreach/process-100 |
| imo_topology | middle |
| cc_layer | CC-02 |
| orbt | REPAIR |

Inside-Fractal stream:

| Field | Value |
| --- | --- |
| process_id | BAR-P100-FIRE |
| target_process | bp.100 |
| four_brain_process | bp.070-four-brain |
| planner | Four-Brain Planner |
| foreman | Sonnet |
| mechanic | Sonnet |
| auditor | Codex |
| aviation_rule | mechanic != auditor |

## 1. What I Want The Planner To Do

Planner: use Process 070 to produce the exact repair/fire plan that gets Process 100 sending emails safely today.

The goal is not to re-document Process 100 again. The goal is to move from consolidated documentation to a controlled fire:

1. Read the Barton Process 100 folder as the operational source of truth.
2. Confirm the runtime path from `wrangler.toml`, `src/index.ts`, `src/compiler.ts`, and `src/spokes/delivery.ts`.
3. Confirm the email fire cannot use protected domains `svg.agency` or `svgwv.com`.
4. Confirm the domain rotation and Mailgun path are safe enough for a capped repair fire.
5. Identify exactly how pending signals are created or selected.
6. Identify the minimum code/config/doc repairs needed before the first fire.
7. Dispatch Sonnet as mechanic only for those repairs.
8. Dispatch Codex as auditor after the mechanic finishes.
9. Require LBB and Mission Control evidence for the fire.
10. Stop if any hard gate fails.

Planner should not chase deleted or external repos as source of truth. External systems are runtime surfaces only when referenced by `Barton-Processes`.

## 2. Read Set

Planner must read these files first:

| File | Purpose |
| --- | --- |
| `factory/imo-creator/070-four-brain/PROCESS-UT.md` | Process 070 orchestration rules |
| `factory/imo-creator/070-four-brain/four-brain.yaml` | Four-Brain workflow body |
| `factory/cl/100-lcs-pipeline/PROCESS-UT.md` | Process 100 UT |
| `factory/cl/100-lcs-pipeline/PROCESS-100-STEP-BY-STEP.md` | Human step-by-step runbook |
| `factory/cl/100-lcs-pipeline/PROCESS-100-STEP-BY-STEP.yaml` | Machine-readable step-by-step runbook |
| `factory/cl/100-lcs-pipeline/daily-email-run.yaml` | Existing daily fire contract |
| `factory/cl/100-lcs-pipeline/workflow.yaml` | Existing Workflow-Body |
| `factory/cl/100-lcs-pipeline/DOMAIN-MAINTENANCE.md` | Domain maintenance and protected-domain gate |
| `factory/cl/100-lcs-pipeline/wrangler.toml` | Runtime reference |
| `factory/cl/100-lcs-pipeline/src/index.ts` | Worker schedule, endpoints, queue |
| `factory/cl/100-lcs-pipeline/src/compiler.ts` | CID/SID/MID compiler |
| `factory/cl/100-lcs-pipeline/src/gates.ts` | Gate stack |
| `factory/cl/100-lcs-pipeline/src/spokes/delivery.ts` | Mailgun/HeyReach delivery |
| `factory/cl/100-lcs-pipeline/src/spokes/signal-intake.ts` | Signal intake |

Atlas/law references:

| File | Purpose |
| --- | --- |
| `../imo-creator-v2/atlas/constants/KEY.md` | Vocabulary |
| `../imo-creator-v2/atlas/constants/BS_LAW.md` | BS Law conformance |
| `../imo-creator-v2/atlas/manifests/STRUCTURE_MANIFEST.yaml` | CTB and locked constants |

## 3. Scope

Allowed write scope:

| Path | Allowed work |
| --- | --- |
| `factory/cl/100-lcs-pipeline/PROCESS-100-STEP-BY-STEP.md` | Tighten runbook if the runtime path or gates are wrong |
| `factory/cl/100-lcs-pipeline/PROCESS-100-STEP-BY-STEP.yaml` | Tighten machine runbook if the runtime path or gates are wrong |
| `factory/cl/100-lcs-pipeline/DOMAIN-MAINTENANCE.md` | Tighten domain classification and rotation gate |
| `factory/cl/100-lcs-pipeline/daily-email-run.yaml` | Align fire contract with current runtime |
| `factory/cl/100-lcs-pipeline/workflow.yaml` | Align 070 workflow gates if needed |
| `factory/cl/100-lcs-pipeline/src/**` | Only if required to make the controlled fire safe and auditable |

Forbidden:

| Path/Action | Reason |
| --- | --- |
| Treat `cf-lcs-hub` as source of truth | Repo was deleted locally and should not govern Process 100 |
| Add protected domains to rotation | `svg.agency` and `svgwv.com` are main domains |
| Send unrestricted emails | Process 100 is still REPAIR |
| Fire without pending-signal explanation | Empty queue was the last known runtime blocker |
| Fire without LBB and Mission Control evidence | Compliance/logging requirement |
| Mechanic audits own work | Aviation Model violation |

## 4. IMO

Input:

| Input | Source |
| --- | --- |
| Process 100 docs and YAML | `factory/cl/100-lcs-pipeline/` |
| Runtime config | `wrangler.toml` |
| Runtime code | `src/index.ts`, `src/compiler.ts`, `src/spokes/*` |
| Domains | Cloudflare + Mailgun + `lcs_domain_rotation` |
| Candidates/signals | `signal_queue` / `lcs_signal_queue`, depending on current runtime schema |
| Evidence targets | LBB + Mission Control |

Middle:

1. Planner resolves the current Process 100 execution spine.
2. Foreman dispatches exact mechanic work orders.
3. Mechanic repairs only what blocks a safe controlled fire.
4. Auditor checks gates against docs, YAML, runtime, and evidence.
5. If P=1, operator can run capped email fire.

Output:

| Output | Destination |
| --- | --- |
| Repair/fire work orders | Sonnet mechanic |
| Audit packet | Codex auditor |
| Controlled fire runbook | Process 100 folder |
| LBB closeout requirement | LBB |
| Mission Control evidence requirement | Mission Control |

## 5. Planner Deliverables

Planner must return:

1. `P100-FIRE-READINESS` verdict: `READY_FOR_CONTROLLED_FIRE`, `REPAIR_FIRST`, or `BLOCKED`.
2. Exact runtime path: worker, D1 binding, queue, endpoints, cron, source files.
3. Exact signal source: how pending rows get created or selected.
4. Exact safe fire path: endpoint/cron/manual command, cap size, and rollback/stop condition.
5. Mechanic work orders, each with read set, write scope, acceptance criteria.
6. Auditor packet, including files and live evidence to inspect.
7. LBB/Mission Control closeout schema for this fire.
8. Open questions that truly block firing today.

## 6. Mechanic Work Order Template

Foreman should dispatch mechanics with this format:

```text
ROLE: MECHANIC
BAR: BAR-P100-FIRE
TASK: [specific repair]
READ:
  - factory/cl/100-lcs-pipeline/PROCESS-100-STEP-BY-STEP.md
  - factory/cl/100-lcs-pipeline/PROCESS-100-STEP-BY-STEP.yaml
  - factory/cl/100-lcs-pipeline/wrangler.toml
  - factory/cl/100-lcs-pipeline/src/[specific file]
SCOPE:
  - factory/cl/100-lcs-pipeline/[specific file(s)]
ACCEPTANCE:
  - Controlled fire gate is safer or more observable.
  - No protected domain can be selected.
  - No unrestricted fire path is introduced.
  - LBB and Mission Control evidence remain required.
CONSTRAINTS:
  - Do not use cf-lcs-hub as source of truth.
  - Do not audit your own work.
  - Do not modify unrelated files.
```

## 7. Auditor Packet

Codex auditor should inspect:

| Gate | Evidence |
| --- | --- |
| BS Law | MD/YAML carry Book + Spine, YAML has outside/inside separation |
| Source of truth | Runtime/process home is `Barton-Processes/factory/cl/100-lcs-pipeline/` |
| Domain safety | `svg.agency` and `svgwv.com` excluded |
| Signal readiness | Pending signal source documented and tested |
| Email safety | Verified recipient, suppression, voice, Reply-To, CAN-SPAM gates |
| Runtime safety | Cap size and stop conditions present |
| Evidence | LBB and Mission Control closeout required |
| Aviation | Mechanic did not audit own work |

Auditor verdict must be:

```text
VERDICT: P=1
```

or

```text
VERDICT: P=0
```

with file citations to the scoped files.

## 8. P=1 Definition

P=1 when all are true:

1. Planner identifies a safe controlled fire path.
2. Any required mechanic repairs are complete.
3. Auditor certifies the repair/fire packet.
4. Process 100 has a known source for pending signals.
5. Active domains are safe and protected domains are excluded.
6. Batch size is capped for REPAIR mode.
7. LBB and Mission Control closeout are required and wired.
8. Operator can fire emails without guessing.

## 9. Stop Conditions

Stop immediately if:

| Stop | Why |
| --- | --- |
| No pending signal creation path | Sender will not fire |
| Protected domain can be selected | Main-domain burn risk |
| Verified-email gate is missing | Bounce/reputation risk |
| LBB/MC evidence is not available | Compliance gap |
| Runtime source contradicts Process 100 folder | Source-of-truth drift |
| Mechanic and auditor collapse into same role | Aviation violation |

## 10. Notes To Foreman

Do not overbuild. The target is a controlled, auditable first fire, not full autonomy.

If the planner finds multiple options, choose the smallest safe path:

1. Repair docs/YAML gates.
2. Verify runtime and pending signals.
3. Cap the batch.
4. Fire.
5. Log.
6. Audit.

Full daily autonomy comes after three clean fires.


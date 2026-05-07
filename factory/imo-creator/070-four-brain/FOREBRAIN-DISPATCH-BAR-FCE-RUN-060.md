---
mission_control_exempt: true
mission_control_exempt_reason: Historical dispatch artifact for prior BAR (FCE-RUN-060). Stale runtime state. Per BAR-070-MC-WIRE Plan Book §7.
---

# Forebrain Dispatch: BAR-FCE-RUN-060-PLANNER
## Process 070 Planner Start Packet
### Status: READY
### Medium: dispatch
### Business: imo-creator

---

## Dispatch

Run Process 070 for `BAR-FCE-RUN-060-PLANNER`.

The Planner should read the instantiated intake packet:

- `Barton-Processes/docs/plans/BAR-FCE-RUN-060-PLANNER/FCE-RUN-PLANNER-INTAKE.md`
- `Barton-Processes/docs/plans/BAR-FCE-RUN-060-PLANNER/fce-run-planner-intake.yaml`

The Planner should use the Process 070 template and workflow:

- `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md`
- `Barton-Processes/factory/imo-creator/070-four-brain/planner-intake-template.yaml`
- `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md`
- `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml`

## Desired Outcome

Produce the Plan Book for the canonical PROC-060 FCE run process pair.

The Plan Book must specify the future Mechanic build for:

- PROC-060 `PROCESS-UT.md`
- PROC-060 companion workflow YAML
- Mission Control evidence visibility for the FCE IMO trail
- D1 vault and cycle evidence
- R2 cleanup gate
- FCE library registration gate
- downstream DMJ readiness after multiple locked FCEs exist in the same family

## Non-Drift Locks

- PROC-060 is the only process that runs an FCE.
- PROC-070 plans and dispatches; it does not run FCEs.
- PROC-080 is reference/fill material to absorb into PROC-060.
- PROC-090 is an FCE artifact/library example, not runtime.
- `us.py` and `up.py` are locked read-only blueprint files.
- US solves `M`.
- US P=1 is fixed: all four FCE columns covered and leaves at primitive.
- K=C locks `M`.
- UP consumes `I` using locked `M` until tolerance says stop.
- R2 + OpenRouter is the active workbench loop.
- D1 is the completed-run vault only.
- D1 stores every cycle from all three OpenRouter model tests under the sovereign ID.
- R2 is cleaned only after D1 vault success.
- FCE library registration happens only after Codex audit/check and D1 vault success.
- DMJ is deferred at N=1 and queued only when multiple locked FCEs exist in the same family.

## Planner P=1

Planner P=1 when the Plan Book gives Foreman enough to dispatch Mechanic and Auditor work orders without guessing:

1. Read set is explicit.
2. Source-of-truth split is explicit.
3. PROC-060 target artifacts are explicit.
4. R2/OpenRouter, D1, MC, LBB, FCE library, and DMJ evidence roles are explicit.
5. Locked files and forbidden actions are explicit.
6. Auditor packet requirements are explicit.
7. Open blocker on DMJ process number is either resolved or routed as sovereign decision.

## Start Prompt

```text
ROLE: PLANNER
PROCESS: PROC-070 Four-Brain
BAR: BAR-FCE-RUN-060-PLANNER

READ:
- Barton-Processes/docs/plans/BAR-FCE-RUN-060-PLANNER/FCE-RUN-PLANNER-INTAKE.md
- Barton-Processes/docs/plans/BAR-FCE-RUN-060-PLANNER/fce-run-planner-intake.yaml
- Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md
- Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml
- Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md
- Barton-Processes/factory/imo-creator/070-four-brain/planner-intake-template.yaml

TASK:
Produce the Plan Book for the canonical PROC-060 FCE run process pair.

ACCEPTANCE:
Planner output must satisfy the P=1 definition in the intake packet and preserve every non-drift invariant.

CONSTRAINTS:
Do not build the PROC-060 artifacts directly. Planner plans. Foreman dispatches. Mechanic builds. Auditor certifies.
```

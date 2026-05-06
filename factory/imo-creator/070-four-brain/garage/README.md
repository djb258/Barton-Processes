# Process 070 Garage Intake

## Purpose

This folder is the intake bay for Process 070 Four-Brain work.

Any agent can pull the car into the garage by creating a BAR folder under `inbox/`, filling the Planner Intake packet, and setting `garage_status: READY_FOR_PLANNER` in the paired YAML.

The Planner watches this folder, claims the next ready packet, and turns it into a Plan Book.

## Canonical Paths

| Item | Path |
| --- | --- |
| Intake inbox | `factory/imo-creator/070-four-brain/garage/inbox/` |
| Completion outbox | `factory/imo-creator/070-four-brain/garage/outbox/` |
| One work order | `factory/imo-creator/070-four-brain/garage/inbox/BAR-{id}/` |
| Planner intake MD | `factory/imo-creator/070-four-brain/garage/inbox/BAR-{id}/PLANNER-INTAKE.md` |
| Planner intake YAML | `factory/imo-creator/070-four-brain/garage/inbox/BAR-{id}/planner-intake.yaml` |
| Durable Plan Book output | `docs/plans/BAR-{id}/PLAN-BOOK.md` or `docs/plans/BAR-{id}.plan.md` |
| Final product pointer | `factory/imo-creator/070-four-brain/garage/outbox/BAR-{id}/FINAL-PRODUCT.yaml` |
| Queue manifest | `factory/imo-creator/070-four-brain/garage/queue.yaml` |

## Status Values

| Status | Meaning |
| --- | --- |
| DRAFT | Intake exists but is not ready for Planner. |
| READY_FOR_PLANNER | Intake is complete enough for Planner to claim. |
| PLANNER_RUNNING | Planner has claimed the work order. |
| PLAN_BOOK_READY | Planner produced the Plan Book. |
| FOREMAN_DISPATCHED | Foreman has dispatched Mechanic work packets. |
| REVIEW_FOREMAN_DISPATCH | Human/operator must inspect Foreman dispatch checklist before Mechanic. |
| REVIEW_MECHANIC_OUTPUT | Human/operator must inspect Mechanic output checklist before Auditor. |
| REVIEW_AUDIT_VERDICT | Human/operator must inspect Auditor verdict before close. |
| CLOSED | Auditor certified P=1 and closeout evidence exists. |
| BLOCKED | Missing input, connector, permission, source doc, or sovereign decision. |

## Start Rule

Process 070 starts from the path, not from a vague chat instruction.

```text
If a BAR folder exists under garage/inbox and planner-intake.yaml says
garage_status: READY_FOR_PLANNER, the Planner may claim it.
```

Until `BAR-FOUR-BRAIN-CLI` exists, this is the automation contract:

1. Agent creates the BAR folder under `garage/inbox`.
2. Agent fills `PLANNER-INTAKE.md` and `planner-intake.yaml`.
3. Agent sets `garage_status: READY_FOR_PLANNER`.
4. Planner claims it by changing status to `PLANNER_RUNNING`.
5. Planner writes the Plan Book.
6. Foreman dispatches.
7. Mechanic builds.
8. Auditor certifies or rejects.
9. LB&B and Mission Control evidence close the loop where applicable.
10. Outbox receives `FINAL-PRODUCT.yaml` pointing to the final artifact, evidence, and current status.

## Review Checklists

The `approve` command is not a rubber stamp. Each handoff writes and enforces
a checklist in the BAR run directory:

| Handoff | Approval | Checklist |
| --- | --- | --- |
| Planner -> Foreman | `REVIEW_PLAN_BOOK -> PLAN_BOOK_SIGNED` | `APPROVAL-CHECKLIST-PLAN_BOOK_SIGNED.md` |
| Foreman -> Mechanic | `REVIEW_FOREMAN_DISPATCH -> FOREMAN_DISPATCHED` | `APPROVAL-CHECKLIST-FOREMAN_DISPATCHED.md` |
| Mechanic -> Auditor | `REVIEW_MECHANIC_OUTPUT -> MECHANIC_DONE` | `APPROVAL-CHECKLIST-MECHANIC_DONE.md` |

If any checkbox fails, `approve` exits non-zero and leaves the BAR at the
review status. Fix the source artifact, then rerun `approve`.

## Helper

Use:

```bash
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh new BAR-123
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh ready
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh claim BAR-123
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh run-once --execute
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh final BAR-123
```

## Model Routing

| Role | Default Engine | Rule |
| --- | --- | --- |
| Planner | ForeBrain / Claude Opus | Normal garage pickup only. |
| Foreman / Mechanic | Sonnet | Dispatched after Plan Book. |
| Auditor | Codex | Certifies or rejects; does not build. |
| Gemini | Specialty only | Not part of normal 070 garage pickup; requires explicit specialty BAR. |

# Garage Pre-G-19 Archive (2026-05-06)

Five BAR inbox dirs moved here on 2026-05-06 after the G-19 doctrine refactor
(`forebrain-garage.sh` commit `8a73ffc`) and the Planner Intake Template v2.0.0
rewrite (commit `ec4832a` in this repo).

## Why archived

All five BARs were filed against the **v1.0.0 19-section verbose template**
and ran through the **pre-G-19 pipeline** that had three sovereign approval
gates between roles. Both contracts are obsolete:

- **Template v1.0.0** has been replaced by v2.0.0 (thin operator IMO+Type form
  — 4 mandatory questions plus conditional Q4A plus 6 optional, where the
  Planner translates plain-language operator intent into doctrine).
- **Pipeline pre-G-19** had `REVIEW_PLAN_BOOK` / `REVIEW_FOREMAN_DISPATCH` /
  `REVIEW_MECHANIC_OUTPUT` sovereign-approval statuses between roles. Per
  `atlas/constants/MISSION_CONTROL.md` §10.4, sovereign cannot gate the
  pipeline mid-flight; only template-drop (input) and Auditor verdict
  (output) are sovereign touchpoints. Those three intermediate statuses
  no longer exist in the runtime.

## Status at archive time

| BAR | Last `garage_status` | Why archived |
|-----|---------------------|--------------|
| BAR-FCE-RUN-060-PLANNER | REVIEW_MECHANIC_OUTPUT | Mid-flight in pre-G-19 pipeline; status no longer valid |
| BAR-FOUR-BRAIN-CLI | REVIEW_PLAN_BOOK | Mid-flight in pre-G-19 pipeline; status no longer valid |
| BAR-P100-FIRE | BLOCKED | Failed before G-19 fix |
| BAR-PLANNER-INTAKE-REFINE | BLOCKED | Failed three runs at the pre-G-19 sovereign approval checklist; manually replaced via direct template rewrite |
| BAR-VIDEO-PATH-CERTIFICATION | (incomplete metadata) | Pre-G-19 |

## Output artifacts NOT archived

`docs/plans/<bar-id>/PLAN-BOOK.md` outputs from these BARs remain in place
in `docs/plans/`. Run directories under `garage/runs/<bar-id>/` also remain.
Only the **inbox intake examples** are archived here, because their v1.0.0
format is the pattern-match risk.

## Re-firing one of these

Don't re-fire from this archive. If a BAR's work still matters, file a
fresh BAR through the new v2.0.0 template at the canonical path
`factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md`.

## Authority

Archive performed under sovereign authorization on 2026-05-06.

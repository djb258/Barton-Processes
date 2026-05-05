# LB&B Session Evidence: 2026-05-05 Four-Brain Garage

## Summary

Process 070 Four-Brain garage and related Atlas doctrine were updated to make Foreman delegation explicit, auditable, and non-black-box. The Planner remains the high-cognition role. The Foreman is allowed to run on Sonnet/default routing model only after a signed Plan Book and only as routing-only dispatch. Gemini was removed from the Process 070 garage path entirely.

LB&B record: `175449dd-ab65-4a14-9cff-7a8a33c310af`

LB&B logger install verification record: `080b14db-712d-4fa3-9bff-12c2553b1c69`

## Doctrine Updates

Repo: `C:\Users\CUSTOM PC\Desktop\Cursor Builds\imo-creator-v2`

Commit: `9965abf3 Lock foreman delegation doctrine`

Files:

- `atlas/constants/FOUR_BRAIN_AVIATION.md`
- `atlas/constants/FOREMAN_ROLE.md`
- `atlas/manifests/foreman-role.yaml`
- `atlas/FOUR_BRAIN_ROUTING.md`

Result:

- `FOUR_BRAIN_AVIATION.md` moved to v1.3.0.
- Foreman model delegation gate added.
- Foreman may use Sonnet/default routing model only behind signed Plan Book, Atlas citations, LB&B handoff row, Auditor review, and Opus escalation on ambiguity.
- Atlas feed source clarified: `atlas/constants/*` doctrine feeds the Atlas registry/legend.

## Process 070 Updates

Repo: `C:\Users\CUSTOM PC\Desktop\Cursor Builds\Barton-Processes`

Commits:

- `6409461 Enforce four-brain garage handoff gates`
- `25af705 Restrict process 070 planner cli`
- `1115e23 Remove gemini from process 070 garage`

Files:

- `factory/imo-creator/070-four-brain/garage/forebrain-garage.sh`
- `factory/imo-creator/070-four-brain/garage/queue.yaml`

Result:

- Added full Planner -> Foreman -> Mechanic -> Auditor handoff commands.
- Added review gates: `REVIEW_PLAN_BOOK`, `REVIEW_FOREMAN_DISPATCH`, `REVIEW_MECHANIC_OUTPUT`, `REVIEW_AUDIT_VERDICT`.
- Added signed Plan Book state: `PLAN_BOOK_SIGNED`.
- Foreman dispatch now requires `PLAN_BOOK_SIGNED`.
- LB&B transition logging is enforced by default; `--defer-lbb` is documented as local dry-test only when live logger is unavailable.
- Queue manifest documents the state machine and Foreman delegation gate.
- Gemini references were removed from the Process 070 garage runner and queue manifest.

## Follow-up Cleanup

A post-commit cleanup removed the leftover `--planner-cli` option from the runner so Planner is hard-wired through Claude/Opus in Process 070. This prevents other agents from treating alternate Planner CLIs as supported.

## Verification

- `bash -n factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` passed.
- Search confirmed no remaining `Gemini`, `gemini`, or `specialty` references in the Process 070 garage runner or queue manifest after removal.
- `rg` is currently blocked on this machine with `Access is denied`; PowerShell search was used instead.

## Open Operational Note

`Barton-Processes` now contains `scripts/lbb-log.sh`, matching the Process 070 runner's compact transition flags. The script posts the standard LBB `/ingest` record shape accepted by the live worker. On this Windows/WSL setup, WSL does not inherit Windows environment variables by default; production runs need `LBB_API_KEY` present inside the bash environment, Doppler installed inside bash, or `WSLENV=LBB_API_KEY/u` set by the launching shell.

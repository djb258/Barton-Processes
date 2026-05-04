VERDICT: P=1

Date: 2026-05-04
Process: bp.301 Page Parser
Auditor: nested Codex via `plugins/brain-runners/scripts/invoke-brain.ps1`
Scope: BAR-377 local active-script repair

## Certification

The local BAR-377 repair is certified for the active-script scope.

## Findings

- Wrangler now defaults to the current Barton-Processes repo through `REPO_ROOT = Path(__file__).resolve().parents[4]` and `WRANGLER_CWD` defaulting to that repo root.
- The process-local Python dependency is declared in `factory/outreach/301-page-parser/requirements.txt`.
- Windows subprocess execution is repaired by resolving `npx.cmd` before `npx`.
- Multi-line SQL is normalized before Wrangler calls and subprocess output uses UTF-8 replacement decoding.
- Repair evidence separates active-script repair from parser-quality risks, older helper cleanup, and scheduled production rollout.

## Residual Risk

No blocker remains for the local active-script repair scope. The dry-run still warned that the optional Title Classifier is unavailable; classifier wiring remains a parser-quality risk outside this certification.

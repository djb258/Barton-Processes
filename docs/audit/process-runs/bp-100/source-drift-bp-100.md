# BAR-377 Source Drift Record - bp.100

Date: 2026-05-04
Process: bp.100 LCS Pipeline
Route: REPAIR -> BLOCKED_SOURCE_DRIFT

## Finding

bp.100 is live and processing, but the `Barton-Processes/factory/cl/100-lcs-pipeline` source does not match the deployed `lcs-hub` Worker behavior.

## Live Evidence

Live endpoint: `https://lcs-hub.svg-outreach.workers.dev`

| Check | Result |
|-------|--------|
| `/health` | PASS |
| Worker version | `v2` |
| Spine DB | `svg-d1-spine` |
| Outreach DB | `svg-d1-outreach-ops` |
| Signals | 4,506 |
| CIDs | 3,677 |
| Companies | 32,702 |
| Domain capacity | 1,250 remaining across active domains |

Live `/status` shows:

- Signals: 4,402 processed, 102 failed, 1 completed, 1 suppressed
- CIDs: 3,677 compiled
- SIDs: 3,404 constructed, 213 failed
- MIDs: 1,139 sent, 1,230 delivered, 778 failed, 242 bounced, 15 scheduled

## Local Source Evidence

The local `Barton-Processes/factory/cl/100-lcs-pipeline` worker dry-run passes, but it would deploy a different D1-only Worker:

- Local Wrangler binding: `D1 = lcs-hub`
- Live Worker reports: `svg-d1-spine` and `svg-d1-outreach-ops`
- Local source uses older table names such as `signal_queue`, `cid`, `sid`, and `mid`
- Live `/status` uses v2 LCS tables such as `lcs_signal_queue`, `lcs_cid`, `lcs_sid_output`, and `lcs_mid_sequence_state`

The apparent live source exists in:

- `C:/Users/CUSTOM PC/Desktop/Cursor Builds/barton-outreach-core/hubs/lcs-send`

## Local Repair Applied

Only local verification scaffolding was added:

- `factory/cl/100-lcs-pipeline/package.json` now has `typecheck`
- `factory/cl/100-lcs-pipeline/tsconfig.json` was added

Verification:

- `npm run typecheck` PASS
- `npx wrangler deploy --dry-run` PASS

## Verdict

P=0 for bp.100 repair certification until the canonical source-of-truth decision is made.

Do not deploy `Barton-Processes/factory/cl/100-lcs-pipeline` to `lcs-hub` until it is synchronized with the live v2 source or explicitly retired as documentation-only.

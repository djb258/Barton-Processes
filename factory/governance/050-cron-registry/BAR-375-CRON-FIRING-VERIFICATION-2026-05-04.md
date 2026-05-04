# BAR-375 Cron Firing Verification

Date: 2026-05-04
Auditor: Codex
Scope:
- `imo-creator-v2/workers/**/wrangler.toml`
- `imo-creator-v2/.github/workflows/*.yml`
- `Barton-Processes/factory/**/wrangler.toml`
- `Barton-Processes/factory/**/PROCESS-UT.md`

## Verdict

BAR-375 is not GREEN.

The fleet has deterministic cron definitions for the known active workers, but full acceptance requires recent fire proof and LBB-per-fire proof for every process. That proof is not present for every process in the local evidence set. One RED determinism finding was also found: `mission-control-api` runs a cron path that calls Anthropic through autonomous routines.

## Source Cron Inventory

### imo-creator-v2 workers

| Status | Path | Schedule evidence |
|--------|------|-------------------|
| YELLOW | `workers/briefing/wrangler.toml` | `0 8 * * 1-5`, `0 18 * * 1-5`; cron exists, recent-fire/LBB proof not verified in this pass |
| YELLOW | `workers/doc-library/wrangler.toml` | `0 6 * * *`; cron exists, recent-fire/LBB proof not verified in this pass |
| RED | `workers/mission-control-api/wrangler.toml` | `0 13 * * 1-5`; cron exists, but scheduled path calls `runRoutines`, which calls Anthropic |
| YELLOW | `workers/vault-sync/wrangler.toml` | `0 22 * * 5`; cron exists, recent-fire/LBB proof not verified in this pass |
| RED | `workers/barton-dev-box/wrangler.toml` | no `[triggers]` block |
| RED | `workers/content-fetcher/wrangler.toml` | no `[triggers]` block |
| RED | `workers/dave-agent/wrangler.toml` | no `[triggers]` block |
| RED | `workers/layer0-engine/wrangler.toml` | no `[triggers]` block |
| RED | `workers/lbb/wrangler.toml` | no `[triggers]` block |
| RED | `workers/mc-proxy/wrangler.toml` | no `[triggers]` block |
| RED | `workers/mission-control/wrangler.toml` | no `[triggers]` block |
| RED | `workers/ops-dashboard/wrangler.toml` | no `[triggers]` block |
| RED | `workers/page-parser/wrangler.toml` | no `[triggers]` block |
| RED | `workers/phone-system/wrangler.toml` | no `[triggers]` block |
| RED | `workers/research-library/wrangler.toml` | no `[triggers]` block |

### Barton-Processes workers

| Status | Path | Schedule evidence |
|--------|------|-------------------|
| YELLOW | `factory/cl/100-lcs-pipeline/wrangler.toml` | `0 7 * * *`; cron exists, recent-fire/LBB proof not verified in this pass |
| YELLOW | `factory/client/820-vendor-export/wrangler.toml` | `0 5 * * *`; cron exists, recent-fire/LBB proof not verified in this pass |
| YELLOW | `factory/outreach/200-people-worker/wrangler.toml` | `0 6 * * *`; cron exists, recent-fire/LBB proof not verified in this pass |
| RED | `factory/cl/800-client-mint/wrangler.toml` | no `[triggers]` block |
| RED | `factory/client/810-client-intake/wrangler.toml` | no `[triggers]` block |
| RED | `factory/client/830-client-portal/wrangler.toml` | no `[triggers]` block |
| RED | `factory/sales/900-sales-portal/wrangler.toml` | no `[triggers]` block |

### GitHub Actions

| Status | Path | Schedule evidence |
|--------|------|-------------------|
| YELLOW | `imo-creator-v2/.github/workflows/atlas-drift-sweep.yml` | `0 12 * * 1`; workflow schedule exists and writes LBB per comments/script path, but recent-run proof not verified in this pass |

## AI-On-Spine Finding

Finding: RED.

Evidence:
- `imo-creator-v2/workers/mission-control-api/src/index.ts` scheduled handler falls through to `runRoutines(cron, env)`.
- `imo-creator-v2/workers/mission-control-api/src/cos/routine-runner.ts` calls Anthropic for routine execution.
- `imo-creator-v2/workers/mission-control-api/src/routes/routines.ts` documents the current path as `schedule trigger (I) -> Claude API call (M) -> LBB ingest (O)`.

BAR-375 says any LLM-on-schedule pattern must halt and be redesigned as deterministic cron plus static upstream content-tail. This should become a follow-on repair BAR unless the sovereign explicitly narrows D-050-03 to mean "AI must not decide when cron fires" rather than "no LLM in scheduled handler."

## PROCESS-UT Coverage

This workspace currently has 38 `PROCESS-UT.md` files under `Barton-Processes/factory/**`, more than the BAR's approximate 16-process scope. The cron registry covers the active/proposed recurring subset; it does not yet prove every UT either has a cron, is event-driven, is retired, or is explicitly non-recurring.

## Required Repairs To Reach GREEN

1. Add recent-fire evidence source for each active cron: Cloudflare cron invocation log, GitHub Action run, or LBB row.
2. Add per-fire LBB logging proof for every active cron.
3. Classify every no-trigger worker/process as one of: recurring gap, event-driven non-cron, disabled, retired, or non-recurring.
4. Repair or explicitly reclassify the `mission-control-api` autonomous routines cron because the current scheduled path calls Anthropic.
5. Re-run this audit and update `cron_registry.yaml` only after evidence supports GREEN.

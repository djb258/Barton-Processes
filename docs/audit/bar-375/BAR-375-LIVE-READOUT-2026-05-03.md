# BAR-375 Live Readout

Date: 2026-05-03
Auditor: Codex
Mode: read-only Cloudflare/D1/repo verification.

## Verdict

P=0 for full BAR-375 GREEN.

Reason: source crons and live deployments exist, and D1/LBB are reachable, but full BAR-375 requires proof that every registered cron is firing and logging every fire to LBB. Current evidence proves several live components, but not every scheduled fire interval.

## Cloudflare Access

`npx wrangler whoami` succeeded under `dbarton@svg.agency` with Workers and D1 access. `wrangler` is not globally installed, but local `npx wrangler` works.

## D1 Inventory Evidence

`npx wrangler d1 list` returned active databases including:

| D1 | ID | Purpose |
|----|----|---------|
| `svg-d1-spine` | `641a9a1e-0882-41a7-82af-ea700e7cfbb3` | CL identity and LCS spine |
| `svg-d1-outreach-ops` | `73a285b8-770a-4370-abbe-ce9607be0b34` | Outreach workspace |
| `imo-d1-global` | `5b902b59-5d65-4c7a-be7c-3763c132b585` | Shared reference |
| `svg-d1-storage` | `47417f00-0eab-4258-947a-3959c063c1de` | Storage/real estate |
| `lbb` | `1f8f12ab-9048-4ebc-9f0d-ed06b6c3c243` | Library Barton Brain |
| `mission-control` | `9f01c45a-a7f8-4173-83ac-afa666e86609` | Mission Control |

## LBB Evidence

Remote query confirmed LBB tables:

```text
_cf_KV
lbb_logbook
lbb_records
lbb_records_error
lbb_subjects
```

Recent records exist for `system` and `processes`, including Four-Brain and sovereign amendment entries on 2026-05-03.

## LCS Live Data Evidence

Remote `svg-d1-spine` read:

| Metric | Value |
|--------|-------|
| LCS tables found | 19 |
| Pending `lcs_signal_queue` rows | 0 |
| `lcs_event` rows in last 7 days | 2007 |
| `lcs_frame_registry` rows | 14 |
| `lcs_email_signature` rows | 1 |
| `lcs_domain_rotation` rows | 14 |
| Active domains | 5 |

Recent `lcs_event` event types:

| Event | Count |
|-------|-------|
| `SID_CONSTRUCTED` | 602 |
| `CID_COMPILED` | 602 |
| `MID_SENT` | 392 |
| `MID_DELIVERED` | 338 |
| `MID_BOUNCED` | 64 |
| `MID_FAILED` | 9 |

Remote `svg-d1-outreach-ops` read:

| Metric | Value |
|--------|-------|
| `slot_workbench` rows | 101559 |
| Verified emails | 53435 |

## Cron Source Evidence

| Worker | Source path | Cron |
|--------|-------------|------|
| `lcs-hub` | `cf-lcs-hub/wrangler.toml` | `0 7 * * *` |
| `lcs-hub` | `barton-outreach-core/hubs/lcs-send/wrangler.toml` | `0 7 * * *` |
| `people-worker-200` | `Barton-Processes/factory/outreach/200-people-worker/wrangler.toml` | `0 6 * * *` |
| `vendor-export-820` | `Barton-Processes/factory/client/820-vendor-export/wrangler.toml` | `0 5 * * *` |
| `briefing` | `imo-creator-v2/workers/briefing/wrangler.toml` | `0 8 * * 1-5`, `0 18 * * 1-5` |
| `doc-library` | `imo-creator-v2/workers/doc-library/wrangler.toml` | `0 6 * * *` |
| `vault-sync` | `imo-creator-v2/workers/vault-sync/wrangler.toml` | `0 22 * * 5` |
| `mission-control-api` | `imo-creator-v2/workers/mission-control-api/wrangler.toml` | `0 13 * * 1-5` |

## Deployment Evidence

`npx wrangler deployments list --name <worker> --json` returned live deployments for:

| Worker | Latest deployment observed |
|--------|----------------------------|
| `lcs-hub` | `2026-04-24T14:47:08.792394Z` latest shown in 10-row deployment window |
| `people-worker-200` | `2026-04-01T18:13:47.033869Z` latest shown |
| `mission-control-api` | `2026-04-27T21:03:51.488442Z` latest shown |
| `briefing` | `2026-03-30T15:55:47.418539Z` latest shown |
| `doc-library` | `2026-04-16T19:46:36.426267Z` latest shown |
| `vault-sync` | `2026-03-30T15:00:20.280501Z` latest shown |

`vendor-export-820` deployment check failed because its local `wrangler.toml` has `kv_namespaces[0].id = ""`; this is a config defect to route to BAR-375/Stage 4, not a live D1 failure.

## Findings

| ID | Severity | Finding | Route |
|----|----------|---------|-------|
| BAR375-F1 | RED | `lcs-fire-daily` daily send is still not proven as an active 10am ET cron. The registry only has it as proposed. | Mechanic fix under bp.100 after final source repo decision |
| BAR375-F2 | ORANGE | `lcs-hub` source exists in three places: `cf-lcs-hub`, `barton-outreach-core/hubs/lcs-send`, and Barton process docs. One canonical code source must be selected before source-of-truth registry can be P=1. | Planner decision, then registry repair |
| BAR375-F3 | ORANGE | `vendor-export-820` has a malformed local `wrangler.toml` KV binding with empty `id`, blocking Wrangler deployment introspection from that config path. | Mechanic repair or alternate canonical path |
| BAR375-F4 | YELLOW | LBB has recent `processes` and `system` rows, but per-fire rows for every cron were not yet proven. | Add/query per-process LBB fire logs |
| BAR375-F5 | ORANGE | Company Lifecycle cron doctrine says the LCS pipeline runner should fire every 15 minutes during business hours and the domain reset should fire daily at midnight ET, while current live source evidence shows `lcs-hub` at `0 7 * * *` and the registry proposes a separate `lcs-fire-daily` at `0 14 * * 1-5`. The canonical LCS cadence must be reconciled before BAR-375 can be GREEN. | Planner decision using `company-lifecycle-cl/archive/v1-dirs/doctrine/OSAM.md` and `Company Lifecycle CL/company-lifecycle-cl/docs/ops/CRON_SCHEDULE.md` |

## Next Knockouts

1. Generate BAR-377 Stage 1 inventories for all 16 processes using the source map and UT-local `workflow.yaml` files.
2. Run BAR-379 read-only D1 audit across the 6 active databases and refresh the evidence report.
3. Fix BAR375-F2 by choosing canonical `lcs-hub` source repo.
4. Fix BAR375-F1 by implementing the daily 10am ET `lcs-fire-daily` cron in the chosen canonical LCS source.

# BAR-378 Live Introspection Report

Date: 2026-05-03
Auditor: Codex
Scope: `Barton-Processes` and sibling `imo-creator-v2` wrangler/GitHub schedule files visible from this workspace.

## Summary

| Metric | Count | Notes |
|--------|-------|-------|
| Active cron registry rows | 7 | 3 in `Barton-Processes`, 4 in `imo-creator-v2` |
| Disabled cron registry rows | 1 | COS/Twilio crons in `mission-control-api`, BAR-812/BAR-813 |
| Proposed cron registry rows | 14 | Decision Sheet Section A defaults, pending sovereign sign-off |
| Retired rows | 1 | `bp.600.bit-scoring` |
| GitHub Action schedules found | 0 | `imo-creator-v2/.github/workflows/locked-files-integrity.yml` has push/PR only |

## Active File Evidence

| Registry ID | Source path | Schedule |
|-------------|-------------|----------|
| `bp.100.lcs-pipeline` | `factory/cl/100-lcs-pipeline/wrangler.toml` | `0 7 * * *` |
| `bp.200.people-worker` | `factory/outreach/200-people-worker/wrangler.toml` | `0 6 * * *` |
| `bp.820.vendor-export` | `factory/client/820-vendor-export/wrangler.toml` | `0 5 * * *` |
| `imo-creator.briefing` | `workers/briefing/wrangler.toml` | `0 8 * * 1-5`, `0 18 * * 1-5` |
| `imo-creator.doc-library.sync` | `workers/doc-library/wrangler.toml` | `0 6 * * *` |
| `imo-creator.vault-sync` | `workers/vault-sync/wrangler.toml` | `0 22 * * 5` |
| `imo-creator.mission-control-api.routines` | `workers/mission-control-api/wrangler.toml` | `0 13 * * 1-5` |

## Drift Found

`workers/mission-control-api/wrangler.toml` contains an active BAR-331 autonomous-routines cron. The skeleton registry only recorded the disabled COS/Twilio crons in that file. `cron_registry.yaml` v1.0.1 now records both states separately:

| Row | State |
|-----|-------|
| `imo-creator.mission-control-api.routines` | Active |
| `imo-creator.mission-control-api.cos` | Disabled, BAR-812/BAR-813 |

## CI Gate

Added `.github/workflows/cron-registry-gate.yml` in `Barton-Processes`. The gate fails PRs that touch a `wrangler.toml` file containing `[triggers]` unless `factory/governance/050-cron-registry/cron_registry.yaml` changes in the same diff.

## Blockers

Live Cloudflare invocation proof still belongs to BAR-375. This pass is file-level registry population and CI drift prevention, not `wrangler cron triggers list` evidence.

# Company Lifecycle Autonomy Index

Date: 2026-05-04
Status: BUILD
Purpose: Tie Barton process UTs, workflow YAMLs, ORBT state, and Company Lifecycle/LCS source documents into one operational map.

## Source Documents

Company Lifecycle source of truth:

- `company-lifecycle-cl/docs/doctrine/COMPANY_LIFECYCLE_LOCK.md`
- `company-lifecycle-cl/docs/handoff/DOWNSTREAM_SUB_HUB_HANDOFF.md`
- `company-lifecycle-cl/docs/handoff/OUTREACH_HANDOFF.md`
- `company-lifecycle-cl/docs/doctrine/CL_DOCTRINE.md`
- `company-lifecycle-cl/docs/schema/CL_SCHEMA_INDEX.md`
- `company-lifecycle-cl/docs/prd/PRD-LCS.md`
- `company-lifecycle-cl/docs/INSURANCE-INFORMATICS-CTB.md`

Barton process source of truth:

- `Barton-Processes/INDEX.md`
- `Barton-Processes/EXECUTION_ORDER.md`
- `Barton-Processes/D1_DATA_DICTIONARY.md`
- `Barton-Processes/factory/**/PROCESS-UT.md`
- `Barton-Processes/factory/**/workflow.yaml`
- `Barton-Processes/factory/**/heir.yaml`
- `Barton-Processes/factory/**/orbt.yaml`

Autonomy manifest:

- `Barton-Processes/docs/company_lifecycle_autonomy_manifest.yaml`

## Autonomy Rule

No process is allowed to run just because it has a workflow file.

Autonomous execution requires all of these:

- `PROCESS-UT.md` exists.
- `workflow.yaml` exists or the process is explicitly documentation-only.
- `heir.yaml` exists.
- `orbt.yaml` exists.
- ORBT is `OPERATE`.
- CL/LCS source document is resolved.
- No known RED audit finding blocks the schedule spine.
- Required secrets and bindings are present.

If any condition fails, the process stays `manual_gate`, `repair_required`, `build_required`, or `retired`.

## Company Lifecycle Flow

Company Lifecycle is the identity authority. It mints sovereign company identity, then downstream hubs consume that identity read-only.

Flow:

1. CL intake verifies company identity.
2. Outreach sub-hubs enrich signals around that sovereign company.
3. Campaign Engine selects eligible targets.
4. LCS Pipeline sends daily communications.
5. Client and Sales processes consume downstream state only after the company is bound to the sovereign ID.

## Main Process Map

| Process | Folder | CL/LCS Role | MD | YAML | ORBT | Autonomous State |
|---|---|---|---|---|---|---|
| bp.010 SEED D1 | `factory/outreach/010-seed-d1` | Seeds source D1 data used by outreach | yes | yes | OPERATE | `auto_eligible` |
| bp.100 LCS Pipeline | `factory/cl/100-lcs-pipeline` | Daily LCS delivery and communication fire | yes | yes | REPAIR | `repair_required` |
| bp.200 People Worker | `factory/outreach/200-people-worker` | People hub; produces people signals for bp.100 | yes | yes | REPAIR | `repair_required` |
| bp.201 Email Discovery | `factory/outreach/201-email-discovery` | People sub-hub email discovery | yes | yes | BUILD | `build_required` |
| bp.202 LinkedIn Discovery | `factory/outreach/202-linkedin-discovery` | People sub-hub LinkedIn discovery | yes | yes | BUILD | `build_required` |
| bp.300 Blog Worker | `factory/outreach/300-blog-worker` | Blog/content signal hub for outreach | yes | yes | BUILD | `build_required` |
| bp.301 Page Parser | `factory/outreach/301-page-parser` | Parses site/page content for outreach signals | yes | yes | BUILD | `build_required` |
| bp.400 DOL Views | `factory/outreach/400-dol-views` | DOL static/reference signal hub | yes | yes | OPERATE | `auto_eligible` |
| bp.500 Talent Flow | `factory/outreach/500-talent-flow` | Talent signal hub | yes | yes | BUILD | `build_required` |
| bp.600 BIT Scoring | `factory/outreach/600-bit-scoring` | Retired/replaced scoring path | yes | yes | TROUBLESHOOT_TRAIN | `retired_or_tt` |
| bp.700 Campaign Engine | `factory/outreach/700-campaign-engine` | Chooses outreach campaign candidates for bp.100 | yes | yes | BUILD | `build_required` |
| bp.800 Client Mint | `factory/cl/800-client-mint` | Mints client-side state downstream of CL | yes | yes | BUILD | `build_required` |
| bp.810 Client Intake | `factory/client/810-client-intake` | Client intake downstream of CL identity | yes | yes | BUILD | `build_required` |
| bp.820 Vendor Export | `factory/client/820-vendor-export` | Vendor export downstream of client state | yes | yes | BUILD | `build_required` |
| bp.830 Client Portal | `factory/client/830-client-portal` | Client portal surface | yes | yes | BUILD | `build_required` |
| bp.900 Sales Portal | `factory/sales/900-sales-portal` | Sales portal downstream of CL/sales state | yes | yes | BUILD | `build_required` |

## Outreach Sub-Hub Join

Under Company Lifecycle, Outreach is a peer downstream hub beside Sales and Client. Inside Outreach:

- People: bp.200, bp.201, bp.202.
- Blog / social-platform content: bp.300, bp.301.
- DOL: bp.400.
- Talent: bp.500.
- Campaign orchestration: bp.700.
- LCS delivery: bp.100.

All of these feed signals into bp.100. bp.100 must not be treated as a standalone sender; it depends on upstream sub-hub signals.

## Current Autonomous Run Position

Safe to run automatically now:

- bp.010, subject to existing cron/runner.
- bp.400, subject to existing cron/runner.

Not safe to run all automatically now:

- bp.100 is in REPAIR and BAR-375 found a schedule-spine policy issue in related mission-control cron behavior.
- bp.200 is in REPAIR.
- bp.201, bp.202, bp.300, bp.301, bp.500, bp.700, bp.800, bp.810, bp.820, bp.830, and bp.900 are BUILD.
- bp.600 is TROUBLESHOOT_TRAIN / retirement path.

## Required Next Step Before Fleet Autonomy

Use the manifest as the control plane for Mission Control:

1. MC reads `docs/company_lifecycle_autonomy_manifest.yaml`.
2. MC renders each process with ORBT, source docs, MD/YAML availability, and autonomy state.
3. MC only exposes "run now" for `auto_eligible` rows.
4. Any `repair_required`, `build_required`, or `retired_or_tt` row opens its process UT and BAR context instead of running.


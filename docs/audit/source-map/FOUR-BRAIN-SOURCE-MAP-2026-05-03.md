# Four-Brain Source Map

Date: 2026-05-03
Scope: blueprints, company lifecycle, client, sales, outreach, LBB, D1 doctrine.

## Four-Brain Roles

| Brain | Role | Current source |
|-------|------|----------------|
| Planner | Sequence work, define gates, decide BAR order | `imo-creator-v2/docs/plans/*`, Linear BARs |
| Specialist | Long-context source discovery | `company-lifecycle-cl`, `Barton-Processes`, `client`, `Sales Process`, `barton-outreach-core` |
| Mechanic | Live read checks and scoped fixes | Cloudflare Wrangler, D1, repo source files |
| Auditor | P=1/P=0 against evidence | BAR reports in `docs/audit/` + Linear comments |

## Repo Map

| Domain | Local path | GitHub | Role |
|--------|------------|--------|------|
| Process execution | `C:/Users/CUSTOM PC/Desktop/Cursor Builds/Barton-Processes` | `djb258/Barton-Processes` | Executable 16-process UT/workflow repo |
| Company Lifecycle authority | `C:/Users/CUSTOM PC/Desktop/Cursor Builds/company-lifecycle-cl` and legacy local copy under `Company Lifecycle CL/company-lifecycle-cl` | `djb258/company-lifecycle-cl` | Sovereign CL identity + LCS doctrine |
| Client | `C:/Users/CUSTOM PC/Desktop/Cursor Builds/client` | `djb258/client` | Client hub blueprint and new `hubs/client-hub` worker |
| Sales | `C:/Users/CUSTOM PC/Desktop/Cursor Builds/Sales Process` | `djb258/ctb-sales-navigator` | Sales navigator blueprint |
| Outreach | `C:/Users/CUSTOM PC/Desktop/Cursor Builds/barton-outreach-core` | `djb258/barton-outreach-core` | Outreach hub + current folded LCS/content/agent hubs |
| LCS Worker | `C:/Users/CUSTOM PC/Desktop/Cursor Builds/cf-lcs-hub` | `djb258/cf-lcs-hub` | Dedicated `lcs-hub` worker repo |
| LBB | Cloudflare D1 `lbb` | Cloudflare account | Knowledge/logbook database |
| Dyno vault | `C:/Users/CUSTOM PC/Desktop/Cursor Builds/imo-engine-vault` | `djb258/imo-engine-vault` | Sealed Dyno vault worker |
| Dyno engine | `C:/Users/CUSTOM PC/Desktop/Cursor Builds/dyno-engine` | `djb258/dyno-engine` | Sealed engine infrastructure |

## Canonical Doctrine Files

| Authority | File |
|-----------|------|
| KEY vocabulary | `imo-creator-v2/atlas/constants/KEY.md` |
| CL technical CTB / routing contract | `company-lifecycle-cl/archive/v1-dirs/doctrine/OSAM.md` |
| Insurance Informatics business CTB | `company-lifecycle-cl/content/INSURANCE-INFORMATICS-CTB.md` |
| Four-hub lifecycle | `company-lifecycle-cl/docs/adr/ADR-005-four-hub-architecture.md` |
| CL doctrine lock | `company-lifecycle-cl/docs/doctrine/COMPANY_LIFECYCLE_LOCK.md` |
| CL schema index | `company-lifecycle-cl/docs/schema/CL_SCHEMA_INDEX.md` |
| Sovereign company identity | `company-lifecycle-cl/docs/schema/CL_COMPANY_IDENTITY.md` |
| LCS overview | `company-lifecycle-cl/src/sys/lcs/doctrine/LCS_OVERVIEW.md` |
| LCS backbone | `company-lifecycle-cl/docs/LCS_BACKBONE.md` |
| LCS cron doctrine | `Company Lifecycle CL/company-lifecycle-cl/docs/ops/CRON_SCHEDULE.md` |
| LCS SQL source | `company-lifecycle-cl/neon/migrations/009_lcs_backbone.sql` |
| D1 live dictionary | `Barton-Processes/D1_DATA_DICTIONARY.md` |
| Cron registry | `Barton-Processes/factory/governance/050-cron-registry/cron_registry.yaml` |

## Company Lifecycle CTB Discovery

The technical CTB that explains how Company Lifecycle flows into LCS is `company-lifecycle-cl/archive/v1-dirs/doctrine/OSAM.md`. It is titled "Operational Semantic Access Map", has `Domain: Company Lifecycle`, `Hub: HUB-CL-001`, `Status: ACTIVE`, and declares itself the authoritative query-routing contract for the Company Lifecycle hub.

The OSAM authority chain is:

```text
imo-creator
  -> HUB-CL-001: Company Lifecycle Hub
  -> cl.company_identity
  -> SUBHUB-CL-LCS
  -> lcs.event / lcs.err0 / lcs.signal_queue / lcs registries
```

Critical routing rules from OSAM:

| Rule | Operational impact |
|------|--------------------|
| Universal join key | `sovereign_company_id`, minted only in `cl.company_identity`, propagated into LCS by value |
| LCS event routing | `cl.company_identity -> lcs.event` via `sovereign_company_id` |
| LCS queue routing | `cl.company_identity -> lcs.signal_queue` via `sovereign_company_id` |
| Error routing | `lcs.event -> lcs.err0` via `message_run_id` |
| Forbidden path | `cl.company_candidate` cannot join directly to LCS; candidate must pass verification first |
| Agent rule | Unknown query path means halt; agents may not invent joins at runtime |

The Insurance Informatics CTB at `company-lifecycle-cl/content/INSURANCE-INFORMATICS-CTB.md` is the business/content backbone. It drives downstream content adapters including LCS email, but it is not the technical query-routing source. Use OSAM for BAR routing, D1 audits, and process YAML dependencies. Use the Insurance Informatics CTB for content-frame/source-language lineage.

## Lifecycle Flow

```text
company_candidate intake
  -> identity/admission gate
  -> cl.company_identity.company_unique_id minted
  -> outreach attaches outreach_id
  -> sales attaches sales_process_id
  -> client attaches client_id
  -> LCS reads lifecycle phase and signal context
  -> lcs_signal_queue
  -> CID compile
  -> SID construct
  -> MID deliver through Mailgun / HeyReach / sales handoff
  -> lcs_event + lcs_err0 + LBB feedback
```

## Immediate BAR Routing

| BAR | Can proceed now | Needs |
|-----|-----------------|-------|
| BAR-375 | Yes, live readout started | Full GREEN needs per-worker last-fire evidence where Cloudflare exposes it or LBB emits it |
| BAR-377 | Yes, Stage 1 inventory can be generated from 16 UT/workflow docs | Stage 2 live state per process after BAR-375 evidence |
| BAR-379 | Yes, read-only D1 introspection approved by user | Generate report across 6 active D1 databases |
| BAR-381 | Yes, schema/routing skeleton can be produced | Final Dave-page channel implementation choice |
| BAR-380 | Yes, source mapping can start | Depends on BAR-375 registry and BAR-379 D1 report for live layers |

## Open Source-Control Notes

| Repo | Note |
|------|------|
| `Sales Process` | Current branch has no upstream tracking and dirty local changes; do not pull/commit without branch decision |
| `cursor-blueprint-enforcer` | Remote points to missing `djb258/command-center`; treat as stale until remote is corrected |
| `company-lifecycle-cl` | Fresh clone exists at workspace root; legacy copy under `Company Lifecycle CL` also exists and has local dirty changes |
| `lcs-hub` | Same worker appears in `cf-lcs-hub`, `barton-outreach-core/hubs/lcs-send`, and Barton process docs; canonical code repo needs one source-of-truth decision |

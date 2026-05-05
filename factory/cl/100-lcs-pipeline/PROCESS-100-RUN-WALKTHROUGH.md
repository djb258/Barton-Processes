# Process 100 Run Walkthrough
## LCS Pipeline daily email fire: IMO view, repair path, and today-fire checklist

Status note: this file is retained as historical investigation and repair context. For operational execution, use `PROCESS-100-STEP-BY-STEP.md` and `PROCESS-100-STEP-BY-STEP.yaml` as the Barton-Processes source of truth.

### Status

Current operating state: **REPAIR because of source drift**, not because no sends have happened.

Important correction: Process 100 has already been sending batches through the live `lcs-hub` v2 worker. The stale UT-local worker under `Barton-Processes/factory/cl/100-lcs-pipeline/src` is not the deployed live source. The live send path appears to be `cf-lcs-hub` and mirrored in `barton-outreach-core/hubs/lcs-send`.

The repair problem is now: **align the docs, Mission Control, and canonical repo with the live v2 send path, then patch any remaining hard-stop gaps without breaking a worker that is already sending.**

Second correction: Process 100 does not market to every company in the database. The first limiter is servicing-agent coverage. The system starts with the full company database, then filters to companies assigned to active servicing agents by ZIP-code radius. That coverage gate is Gate 0.

### Source Of Truth

| Item | Path |
|---|---|
| UT | `PROCESS-UT.md` |
| Daily fire contract | `daily-email-run.yaml` |
| Workflow body | `workflow.yaml` |
| ORBT state | `orbt.yaml` |
| Worker code | `src/index.ts`, `src/compiler.ts`, `src/gates.ts`, `src/spokes/delivery.ts` |
| Cloudflare config | `wrangler.toml` |
| Mission Control layer | `imo-creator-v2/workers/mission-control-api/src/routes/map.ts` |

### Live Source Correction

| Source | Role | Current Finding |
|---|---|---|
| `cf-lcs-hub` | Apparent deployed live source for `lcs-hub` v2 | Contains `compiler-v2.ts`, `lcs_*` table names, Mailgun domain rotation, `/run-batch`, webhook handling |
| `barton-outreach-core/hubs/lcs-send` | Mirror/canonical candidate for live v2 source | Same v2 shape as `cf-lcs-hub`; BAR-377 source drift points here as apparent live source |
| `Barton-Processes/factory/cl/100-lcs-pipeline/src` | UT-local older worker | Uses older table names (`signal_queue`, `cid`, `sid`, `mid`) and should not be deployed over live v2 |
| `Barton-Processes/docs/audit/process-runs/bp-100/source-drift-bp-100.md` | Audit evidence | Says bp.100 is live and processing, but local UT source does not match deployed worker behavior |
| `Barton-Processes/docs/audit/bar-375/BAR-375-LIVE-READOUT-2026-05-03.md` | Live D1 readout | Shows live `MID_SENT`, `MID_DELIVERED`, `MID_BOUNCED`, `MID_FAILED` events |

### Servicing Agent Coverage Gate

Process 100's first filter is not DOL, people, or email. It is **servicing-agent assignment**.

The coverage model is:

```text
full company database
  -> company postal_code
    -> coverage.v_service_agent_coverage_zips.zip
      -> coverage.service_agent
        -> service_agent_number: SA-001 / SA-002 / SA-003
          -> marketable company universe for Process 100
```

Local source evidence:

| Evidence | Location |
|---|---|
| Gate 0 is `agent_assignment` and is a hard stop | `cf-lcs-hub/src/gates.ts` |
| Gate 0 is described as "Agent assignment (100mi radius)" | `cf-lcs-hub/src/gates.ts` |
| Build docs list Gate 0 as "Agent in 100mi radius" | `cf-lcs-hub/BUILD.md` |
| `postal_code` joins to `coverage.v_service_agent_coverage_zips.zip` | `cf-lcs-hub/src/migrations/002_column_registry.sql` |
| `service_agent_number` values are `SA-001`, `SA-002`, `SA-003` | `cf-lcs-hub/src/migrations/002_column_registry.sql` |
| Coverage zones are defined by `anchor_zip` and `radius_miles` | `cf-lcs-hub/src/migrations/002_column_registry.sql` |
| Agent assignment seed joins `outreach.company_target` to `coverage.v_service_agent_coverage_zips` and `coverage.service_agent` | `cf-lcs-hub/src/seed.ts` |

The important business rule:

> A company can only enter the Process 100 marketable universe if it has an active servicing agent assignment.

That is how the larger company database gets reduced to the roughly 32,700-company outreach universe referenced in the docs. The audit/doc layer also references 32,702 companies and 98,106 people slots, which equals 32,702 companies times the three role slots: CEO, CFO, HR.

### Purpose

Process 100 turns upstream outreach intelligence into outbound email activity.

In plain terms:

1. It receives signals that say a company is worth contacting.
2. It compiles those signals into a CID.
3. It selects the right person and builds a SID message.
4. It delivers MIDs through Mailgun using domain rotation.
5. It receives webhook feedback.
6. It writes evidence so LBB and Mission Control can show what happened.

### IMO Map

#### Input

Process 100 does not create the raw universe. It consumes prepared upstream data.

| Input | What It Provides | Current Requirement |
|---|---|---|
| `lcs_signal_queue` | Pending company-level signals ready for processing | Rows must be `pending` and not expired |
| `lcs_signal_registry` | Signal definitions and lineage | Needed for traceability |
| Process 200 / 201 / 202 | People, slots, verified emails | Must only use verified recipient email |
| Process 300 | Social platform / blog / content signal layer | Feeds signal strength |
| Process 400 / DOL | Form 5500 and employer benefit signals | Required for qualification |
| Process 700 | Campaign candidate selection | Can seed/shape queue candidates |
| Servicing agents | Geographic marketability filter | Company ZIP must fall inside an active SA coverage radius |
| `slot_workbench` / v2 people source | CEO/CFO/HR slot data | Must include verification gate before send |
| Mailgun domain rotation | Send domain availability | Domain must not be paused and must be under cap |
| Voice source / LBB | Barton voice and approved outbound framing | Message must pass voice rules |

#### Middle - Live v2 Path

The live worker is built around the CID -> SID -> MID compiler in `compiler-v2.ts`.

| Stage | Current Code Path | What Happens |
|---|---|---|
| Scheduled producer | `cf-lcs-hub/src/index.ts` `scheduled()` | Resets/ramps domains, schedules sequence-step signals, finds pending `lcs_signal_queue` rows, queues `compile_cid` jobs |
| Manual batch trigger | `cf-lcs-hub/src/index.ts` `/run-batch` | Processes up to 50 pending signals directly with `runPipeline()` |
| Queue consumer | `cf-lcs-hub/src/index.ts` `queue()` | Runs `compile_cid`, `construct_sid`, `deliver_mid`, and webhook jobs |
| CID compile | `cf-lcs-hub/src/compiler-v2.ts` `compileCid()` | Reads `lcs_signal_queue`, compiles `lcs_cid`, logs `CID_COMPILED` |
| SID construct | `cf-lcs-hub/src/compiler-v2.ts` `constructSid()` | Builds voice-validated outbound copy, writes `lcs_sid_output`, logs `SID_CONSTRUCTED` |
| MID delivery | `cf-lcs-hub/src/compiler-v2.ts` `deliverMid()` | Checks adapter caps, calls Mailgun/HeyReach delivery, writes `lcs_mid_sequence_state`, logs `MID_SENT` or `MID_FAILED` |
| Mailgun send | `cf-lcs-hub/src/compiler-v2.ts` `deliverMailgun()` | Picks sending domain, injects CAN-SPAM footer, normalizes ASCII, sets Reply-To, sends to Mailgun |
| Webhook feedback | `cf-lcs-hub/src/index.ts` `processWebhook()` | Updates `lcs_mid_sequence_state`, logs `MID_DELIVERED`, `MID_OPENED`, `MID_CLICKED`, `MID_BOUNCED`, etc. |

#### Gate Stack

| Gate | Name | Hard Stop | Meaning |
|---:|---|---|---|
| 0 | `agent_assignment` | Yes | Company must be assigned to a servicing agent inside the configured ZIP/radius coverage |
| 1 | `geography` | Yes | Company must be in the allowed state territory |
| 2 | `size` | Yes | Company must be in the target employee range |
| 3 | `dol_filing` | Yes | Company must have a Form 5500/DOL signal |
| 4 | `renewal_window` | No | Renewal timing boosts signal quality |
| 5 | `premium_trend` | No | Premium increase boosts signal quality |
| 6 | `talent_flow` | No | Talent-flow signal boosts signal quality |
| 7 | `blog_signal` | No | Blog/social platform signal boosts signal quality |
| 8 | `composite_signal` | Yes | At least one substantive signal must exist |

#### Output

Process 100 must leave evidence after every run.

| Output | What It Should Prove |
|---|---|
| `cid` / `lcs_cid` | Which company intelligence was compiled |
| `sid` / `lcs_sid_output` | Which message was constructed and why |
| `mid` / `lcs_mid_sequence_state` | Which message was queued/sent/delivered/bounced |
| `lcs_event` | Append-only run timeline |
| `err0` / `lcs_err0` | Failures, bounces, delivery errors, squawks |
| LBB subject `svg-outreach-proc` | Human-readable closeout evidence |
| Mission Control Process 100 map layer | Visual run status and IMO flow |

### Already-Sent Evidence

The live readout from 2026-05-03 proves sends already happened.

| Evidence | Count |
|---|---:|
| `lcs_event` rows in last 7 days | 2,007 |
| `SID_CONSTRUCTED` | 602 |
| `CID_COMPILED` | 602 |
| `MID_SENT` | 392 |
| `MID_DELIVERED` | 338 |
| `MID_BOUNCED` | 64 |
| `MID_FAILED` | 9 |

Coverage evidence in local docs/schema:

| Metric / Structure | Value |
|---|---:|
| Outreach company universe referenced in docs | 32,702 |
| People slots for that universe | 98,106 |
| Slot math | 32,702 companies x 3 slots |
| Servicing agents | SA-001, SA-002, SA-003 |

Live count refresh attempted on 2026-05-05, but the current shell was missing `CLOUDFLARE_API_TOKEN`, so remote D1 queries could not run. The query to run when token context is loaded:

```sql
SELECT service_agent_number, COUNT(*) AS companies
FROM outreach_company_target
WHERE service_agent_number IS NOT NULL
GROUP BY service_agent_number
ORDER BY service_agent_number;
```

And the total universe check:

```sql
SELECT
  COUNT(*) AS total_companies,
  SUM(CASE WHEN service_agent_number IS NOT NULL THEN 1 ELSE 0 END) AS agent_assigned
FROM outreach_company_target;
```

The bp.100 source drift audit also recorded live `/status` totals:

| Live `/status` Metric | Count |
|---|---:|
| Signals processed | 4,402 |
| Signals failed | 102 |
| CIDs compiled | 3,677 |
| SIDs constructed | 3,404 |
| SIDs failed | 213 |
| MIDs sent | 1,139 |
| MIDs delivered | 1,230 |
| MIDs failed | 778 |
| MIDs bounced | 242 |
| MIDs scheduled | 15 |

This means the real question is not "can Process 100 send at all?" It can. The real question is "what gates and telemetry must be repaired so we can safely keep firing and scale volume?"

### Current Runtime Shape

Current deployed config exposes:

| Surface | Purpose |
|---|---|
| Cron `0 7 * * *` | Daily signal compiler producer |
| Queue `lcs-pipeline` | Async processing for CID -> SID -> MID |
| DLQ `lcs-dlq` | Failed jobs after retry |
| `/health` | Read signal/CID counts |
| `/status` | Read pipeline counts |
| `/signal` and `/signals` | Ingest upstream signals |
| `/run` | Manual pipeline trigger for one signal/company path |
| `/run-batch` | Manual batch trigger for pending signals, capped at 50 by live code |
| `/webhook/mailgun` | Mailgun delivery feedback |
| `/webhook/heyreach` | HeyReach feedback |
| `/trace/:id` | Follow a signal/CID/SID/MID chain |

### Why We Are Still In Repair / Source Drift

The current contract says Process 100 cannot run unrestricted while in REPAIR, but the live v2 worker has already been sending. The repair state exists because certification and source-of-truth alignment are not clean.

Known issues before increasing volume:

| Blocker | Why It Matters | Repair Needed |
|---|---|---|
| Canonical source drift | Docs point at stale UT-local worker while live is v2 | Pick canonical repo/path and mark UT-local source documentation-only or sync it |
| Verified-email gate needs live-code audit | Prior bounce issue came from unverified emails | Confirm `has_verified_email = 1` enforcement in v2 CID/SID selection and patch if missing |
| Reply-To mismatch needs decision | v2 compiler uses deliverability config; spoke fallback uses `marketing@svg.agency` | Confirm desired reply-to: `dave@svg.agency` vs `marketing@svg.agency`, then patch all send chokepoints |
| Voice validation exists in v2 | Prevents off-voice copy | Keep `validateOutboundEmailCopy()` in `constructSid()` and audit frame failures |
| CAN-SPAM footer exists in v2 | Compliance requirement | Keep footer injection in `deliverMailgun()` and audit idempotency |
| Domain pause and daily cap exist in v2 | Protects domain reputation | Keep `pickSendingDomain()`, `recordDomainSend()`, adapter cap checks, and scheduled pause/ramp logic |
| LBB and Mission Control closeout not visibly written by fire path | Required evidence for promotion | Write evidence after every manual fire |
| Three clean fires not complete | Promotion gate | Run small controlled fires and audit results |

### Today-Fire Path

This is the safest path if Process 100 must continue firing today.

1. Keep ORBT as `REPAIR`.
2. Do not deploy the stale UT-local worker over live `lcs-hub`.
3. Treat `cf-lcs-hub` / `barton-outreach-core/hubs/lcs-send` as the live source until Dave chooses the canonical repo.
4. Use `/status`, `lcs_mid_sequence_state`, and `lcs_event` to inspect current performance before firing more.
5. Use `/run-batch` only with an explicit cap.
6. Require verified-email-only recipients in the live v2 selection path.
7. Require suppression check.
8. Require the approved Reply-To across every Mailgun chokepoint.
9. Preserve voice/CAN-SPAM checks already in `compiler-v2.ts`.
10. Require Mailgun domain not paused and under cap.
11. Write `lcs_event`, `lcs_err0` if needed, LBB closeout, and Mission Control evidence.
12. Audit the next fire before increasing volume.

### Live Manual Batch Contract

The live worker already exposes a batch trigger:

```json
{
  "endpoint": "POST /run-batch",
  "body": {
    "limit": 20
  }
}
```

Expected response:

```json
{
  "processed": 0,
  "compiled": 0,
  "sent_count": 0,
  "failed": 0
}
```

Recommended repair: add a stricter `/repair-fire` or extend `/run-batch` so the response includes `batch_id`, verified-email skips, voice failures, suppression skips, domain pauses, LBB record id, and Mission Control evidence id.

### Mission Control View

Mission Control should show Process 100 as a process layer, not just a map pin.

The layer should answer:

| Question | MC Display |
|---|---|
| What came in? | Input signals, upstream process states, eligible recipients |
| What coverage is active? | SA-001 / SA-002 / SA-003 company counts, anchor ZIPs, radius miles |
| What is running now? | CID/SID/MID stage counts |
| What went out? | Sent/skipped/failed/bounced counts |
| What stopped the run? | Hard-stop gate and error reason |
| Can we increase volume? | Repair-fire audit result and bounce/complaint window |
| Are domains safe to rotate? | Cloudflare DNS, Mailgun verification, D1 rotation, warmup cap, bounce state |

### Domain Maintenance Gate

Process 100 must treat domain maintenance as a pre-fire gate. The runtime sender already rotates through `lcs_domain_rotation`, but that table is only safe when it is reconciled against Cloudflare DNS and Mailgun verification.

Control document: `factory/cl/100-lcs-pipeline/DOMAIN-MAINTENANCE.md`

Current live health shows 14 domains in the LCS rotation table. If five more domains were moved into Cloudflare, they must be checked against Cloudflare DNS, Mailgun verification, Composio Mailgun connection state if applicable, and domain classification before they contribute to daily capacity.

2026-05-05 reconciliation result:

| Layer | Count | Finding |
|---|---:|---|
| Cloudflare active zones | 18 | All zones active |
| Mailgun active custom domains | 16 | `mg.svg.agency` and `mg.svgwv.com` are verified but protected |
| D1 rotation domains | 14 | Current outreach rotation only |
| Protected main domains | 2 | `svg.agency`, `svgwv.com` must not be burned by cold outreach |
| Cloudflare-only domains | 2 | `medsavings.org`, `weewee.me` are not Mailgun rotation domains |
| Composio connected accounts | 49 | No Mailgun connected account found through v3.1 API |

Stop condition: do not activate a new sending domain until SPF, DKIM, DMARC, Mailgun verification, domain classification, and Mission Control visibility pass. Protected main domains must stay out of `lcs_domain_rotation`.

Current delivery path: live `cf-lcs-hub` sends Mailgun messages directly from `compiler-v2.ts`. Composio is documented as an integration router, but Mailgun is not currently routed through a Composio connected account.

### Promotion Path

Process 100 can move from REPAIR to OPERATE only after:

1. Verified-email gate is deployed and proven.
2. Domain maintenance gate passes for every active sending domain.
3. Three clean controlled fires complete.
4. Bounce rate stays below 2 percent.
5. Voice pass rate is 100 percent.
6. No AI call exists on the scheduled send spine.
7. LBB and Mission Control evidence exists for each fire.
8. Auditor returns P=1 against UT, workflow, daily run YAML, code, and live evidence.

### Questions For Dave

Use this section to correct the run model before we repair code.

| Question | Dave Update |
|---|---|
| Should the first fire be one company, one role path, or a capped batch? | TBD |
| What is the exact max count for today's first controlled fire? | TBD |
| Which recipient roles can fire today: CEO, CFO, HR, or all three? | TBD |
| Is Mailgun the only channel for today, or should HeyReach stay disabled? | TBD |
| Which D1 table is the authoritative verified-email source today? | TBD |
| Are the three active servicing agents exactly SA-001, SA-002, and SA-003? | TBD |
| What are the current anchor ZIPs and radius miles for each servicing agent? | TBD |
| Should Process 100 ever market outside an assigned servicing-agent radius? | Expected: no |
| Should Process 700 seed candidates first, or should Process 100 pull directly from pending signals? | TBD |
| Where should the LBB closeout write: `svg-outreach-proc` only, or another subject too? | TBD |
| What Mission Control surface should show the live fire card: Map layer only, Outreach Ops, or both? | TBD |
| Are we allowed to fire while Process 200 remains REPAIR if recipient rows are verified? | TBD |
| Do we want an explicit `/repair-fire` endpoint, or should `/run` be upgraded with repair-fire gates? | TBD |
| What are the five new Cloudflare domains that should enter domain maintenance? | TBD |
| Should new domains start paused at warmup week 1, or are any already warmed in Mailgun? | TBD |
| Are any Mailgun actions routed through Composio instead of direct Mailgun API calls? | TBD |

### Recommended Repair Order

1. Choose canonical live source: `cf-lcs-hub` or `barton-outreach-core/hubs/lcs-send`.
2. Mark `Barton-Processes/factory/cl/100-lcs-pipeline/src` as stale/documentation-only or sync it to v2.
3. Refresh live SA counts by `service_agent_number` once Wrangler token context is available.
4. Audit Gate 0 in live v2: no servicing-agent assignment means no CID/MID.
5. Audit verified-email enforcement in `compiler-v2.ts`.
6. Patch Reply-To consistently across `compiler-v2.ts` and `spokes/delivery.ts`.
7. Add LBB and Mission Control evidence writes to the live batch path.
8. Add a dry-run mode that validates pending signals without sending.
9. Run domain maintenance against Cloudflare, Mailgun, D1 rotation, LBB, and MC.
10. Run the next capped live batch.
11. Audit `lcs_event`, `lcs_mid_sequence_state`, `lcs_err0`, LBB, and MC.
12. Repeat until three clean fires are complete.

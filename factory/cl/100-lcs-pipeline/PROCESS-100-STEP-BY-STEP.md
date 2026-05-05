# Process 100 Step-By-Step Runbook

## 1. Identity

| Field | Value |
| --- | --- |
| ID | PROC-100-STEP-BY-STEP |
| Name | Process 100 LCS Step-By-Step Runbook |
| Medium | process |
| Business Silo | company lifecycle / outreach |
| CTB Position | barton-enterprises/company-lifecycle/outreach/process-100 |
| ORBT | REPAIR |
| Authority | Atlas + BS Law + Process 100 UT |
| Last Modified | 2026-05-05 |
| Paired YAML | `PROCESS-100-STEP-BY-STEP.yaml` |

### HEIR

| Field | Value |
| --- | --- |
| sovereign_ref | company-lifecycle |
| hub_id | outreach |
| ctb_placement | factory/cl/100-lcs-pipeline |
| imo_topology | middle |
| cc_layer | CC-02 process |
| services | Cloudflare Workers, D1, Mailgun, Composio, LBB, Mission Control |
| secrets_provider | Doppler |
| acceptance_criteria | A human or agent can start at Step 0 and run Process 100 through evidence closeout without guessing where the next artifact lives. |

### BS Law Conformance

This artifact uses BS Law as its conformance contract. It is both a Book and a Spine artifact:

| BS Law Arm | This File Carries |
| --- | --- |
| Book Law structure | Named sections, durable Markdown body, paired YAML, identity, purpose, resources, IMO, DMJ, gates, trace, logbook, failure registry, session log. |
| Three Layers Spine content | HEIR, ORBT, CTB placement, IMO topology, constants/variables, execution trace, audit/promotion path. |

Outside-Dewey stream:

| Field | Value |
| --- | --- |
| species | UT-Body / Process Runbook |
| sovereign_ref | company-lifecycle |
| hub_id | outreach |
| ctb_placement | barton-enterprises/company-lifecycle/outreach/process-100 |
| imo_topology | middle |
| cc_layer | CC-02 |
| orbt | REPAIR |

Inside-Fractal stream:

| Field | Value |
| --- | --- |
| process_id | bp.100 |
| process_number | 100 |
| process_name | LCS Pipeline |
| source_ut | PROCESS-UT.md |
| paired_yaml | PROCESS-100-STEP-BY-STEP.yaml |
| aviation_rule | builder != auditor |
| p_equals_1 | three clean controlled fires with LBB and Mission Control evidence, then auditor P=1 |

## 2. Purpose

This file is the plain-language step-by-step guide for Process 100. It ties the existing Process 100 UT, workflow YAML, daily fire YAML, domain maintenance file, UT-local runtime files, D1 tables, Mailgun domains, Mission Control layer, and LBB evidence into one path.

Without this guide, Process 100 is documented in fragments. With it, the process has one ordered run path: know the law, classify the domains, verify inputs, create signals, compile CID, construct SID, deliver MID, capture feedback, write evidence, and promote only after audit.

## 3. Resources

| Resource | Role |
| --- | --- |
| `atlas/constants/KEY.md` | Vocabulary. Read first. K = C. |
| `atlas/constants/BS_LAW.md` | Artifact conformance. Book and Spine together, always. |
| `atlas/manifests/STRUCTURE_MANIFEST.yaml` | CTB and locked-constant structure. |
| `PROCESS-UT.md` | Process 100 UT body. |
| `daily-email-run.yaml` | Existing executable daily-run contract. |
| `PROCESS-100-STEP-BY-STEP.yaml` | Machine-readable paired runbook for this file. |
| `DOMAIN-MAINTENANCE.md` | Cloudflare, Mailgun, D1 rotation, protected-domain gate. |
| `wrangler.toml` | Barton Process 100 runtime reference: worker, cron, D1, queue, env vars. |
| `src/index.ts` | Worker schedule, `/health`, `/status`, `/signal`, `/signals`, `/run`, webhooks. |
| `src/compiler.ts` | CID/SID/MID compiler. |
| `src/spokes/delivery.ts` | Mailgun/HeyReach delivery spoke. |
| `lcs_domain_rotation` | D1 runtime sending-domain table. |
| LBB | Compliance and operational logbook. |
| Mission Control | Operator visibility and map layer. |

### Runtime Reference

Barton Process 100 keeps its runtime contract in this folder. The runtime reference is not an external repo.

| Runtime Field | Value |
| --- | --- |
| Process home | `Barton-Processes/factory/cl/100-lcs-pipeline/` |
| Worker name | `lcs-hub` |
| Runtime main | `src/index.ts` |
| Compiler | `src/compiler.ts` |
| Delivery spoke | `src/spokes/delivery.ts` |
| Signal intake spoke | `src/spokes/signal-intake.ts` |
| Wrangler config | `wrangler.toml` |
| Cron | `0 7 * * *` |
| D1 binding | `D1` |
| D1 database name | `lcs-hub` |
| Queue | `lcs-pipeline` |
| Manual smoke endpoint | `POST /run` with `sovereign_company_id` |
| Signal intake endpoints | `POST /signal`, `POST /signals` |
| Status endpoints | `GET /health`, `GET /status`, `GET /company/:id`, `GET /trace/:id` |
| Webhooks | `POST /webhook/mailgun`, `POST /webhook/heyreach` |

Deployment or blueprint repos may exist, but they do not define the process. They are implementation surfaces only if this folder points to them.

## 4. IMO

### Input

Process 100 receives:

| Input | Source |
| --- | --- |
| Company universe | `outreach_company_target` |
| Servicing agent coverage | coverage ZIP/radius assignment from active servicing agents |
| People/contact slots | `people_company_slot`, `people_people_master`, `slot_workbench` |
| DOL/plan intelligence | `outreach_dol` |
| Campaign signals | `lcs_signal_queue` |
| Voice/frame rules | `lcs_frame_registry`, `voice-spec.ts` |
| Domain capacity | `lcs_domain_rotation` |
| Secrets | Doppler |

### Middle

Process 100 transforms eligible signals into outbound campaign messages through hard gates:

1. Law and Atlas load.
2. Domain maintenance gate.
3. Servicing-agent coverage gate.
4. Verified-recipient gate.
5. Signal queue selection.
6. CID compile.
7. SID construction.
8. MID delivery.
9. Webhook feedback.
10. Evidence closeout.

### Output

Process 100 emits:

| Output | Destination |
| --- | --- |
| Sent message | Mailgun |
| Delivery record | `lcs_mid_sequence_state` |
| Append-only events | `lcs_event` |
| Failures and skips | `lcs_err0` |
| Batch closeout | LBB |
| Operator view | Mission Control |
| Next-cycle signals | `lcs_signal_queue` |

## 5. Data Schema

Core D1 tables:

| Table | Purpose |
| --- | --- |
| `lcs_signal_queue` | Pending, processed, suppressed, failed signals. |
| `lcs_cid` | Compiled company intelligence dossier. |
| `lcs_sid_output` | Voice-checked campaign/message construction. |
| `lcs_mid_sequence_state` | Message delivery state. |
| `lcs_event` | Append-only event trail. |
| `lcs_err0` | Error and skip drain. |
| `lcs_domain_rotation` | Runtime sender-domain rotation. |
| `outreach_company_target` | Company universe and service-agent assignment. |
| `people_company_slot` | CEO/CFO/HR slots. |
| `people_people_master` | Contact identity and email state. |
| `outreach_dol` | DOL plan intelligence. |

## 6. DMJ

| Define | Map | Join |
| --- | --- | --- |
| Process 100 | LCS daily email fire | `PROCESS-UT.md` + `wrangler.toml` + `src/index.ts` |
| Company | Target employer | `sovereign_company_id` |
| Servicing agent | Area ownership | `service_agent_number` / coverage ZIP |
| Signal | Reason to contact | `lcs_signal_queue.signal_queue_id` |
| CID | Company intelligence | signal + company + DOL + people |
| SID | Sendable campaign | CID + frame + target role + voice gate |
| MID | Delivery record | SID + Mailgun domain + recipient |
| Evidence | Compliance output | LBB + Mission Control |

## 7. Constants & Variables

Constants:

| Constant | Value |
| --- | --- |
| Law gate | Atlas `KEY.md` first, BS Law second |
| Process identity | Process 100 / LCS Pipeline |
| Runtime worker | `lcs-hub` |
| Runtime source | `Barton-Processes/factory/cl/100-lcs-pipeline` |
| Runtime database | `lcs-hub` through D1 binding `D1` |
| Protected domains | `svg.agency`, `svgwv.com` |
| Current rotation domains | 14 outreach Mailgun domains |
| Mailgun path | Delivery spoke from `src/spokes/delivery.ts` |
| Composio Mailgun state | No Mailgun connected account found in Composio v3.1 as of 2026-05-05 |

Variables:

| Variable | Owner |
| --- | --- |
| Daily batch size | Operator / repair policy |
| Eligible pending signals | Upstream processes |
| Servicing agent ZIP/radius coverage | Coverage source |
| Domain pause/unpause state | Domain maintenance process |
| Promotion from REPAIR to OPERATE | Auditor after three clean fires |

## 8. Stop Conditions

| Stop | Why |
| --- | --- |
| Atlas/BS Law not referenced | Artifact is not governed. |
| Protected domain selected for cold outreach | Main domain burn risk. |
| No active sending domains | No delivery capacity. |
| No pending signals | Sender has nothing to process. |
| Company has no servicing-agent coverage | Do not market outside assigned service area. |
| Recipient email is not verified | Bounce/reputation risk. |
| Recipient is suppressed | Compliance stop. |
| Voice spec fails | Message cannot leave. |
| Reply-To is not Dave-controlled | Deliverability/compliance drift. |
| LBB or Mission Control closeout fails | No compliance evidence. |

## 9. Verification

Minimum checks before firing:

```powershell
Invoke-RestMethod "https://lcs-hub.svg-outreach.workers.dev/health"
Invoke-RestMethod "https://lcs-hub.svg-outreach.workers.dev/status"
```

Live findings on 2026-05-05:

| Check | Result |
| --- | --- |
| Cloudflare active zones | 18 |
| Mailgun active custom domains | 16 |
| D1 rotation domains | 14 |
| Active rotation domains | 5 |
| Remaining capacity | 1250 |
| Protected domains excluded | `svg.agency`, `svgwv.com` |
| Composio Mailgun connected accounts | 0 |
| Pending signals | 0 at last `/status` check |

## 10. Analytics

| Metric | P=1 Target |
| --- | --- |
| Domain maintenance gate | Pass |
| Servicing-agent coverage gate | Pass |
| Verified email gate | Pass |
| Voice-spec pass rate | 100 percent |
| Bounce rate | Below 2 percent |
| LBB closeout | Present for every fire |
| Mission Control visibility | Present for every fire |
| Clean controlled fires | 3 consecutive |

## 11. Execution Trace

Step-by-step run path:

| Step | Action | Input | Output | Gate |
| --- | --- | --- | --- | --- |
| 0 | Load Atlas law | `KEY.md`, `BS_LAW.md`, structure manifest | governed context | BS Law |
| 1 | Confirm runtime source | `wrangler.toml` + `src/index.ts` in this folder | Barton runtime selected | no mystery repo |
| 2 | Check domain maintenance | Cloudflare, Mailgun, D1 rotation, Composio | domain health decision | protected domains excluded |
| 3 | Check Process 100 health | `/health`, `/status` | signal/domain/capacity snapshot | worker reachable |
| 4 | Check upstream feeders | Process 200, 201, 202, 300, DOL, Process 700 | candidate readiness | no blind send |
| 5 | Create or select pending signals | `lcs_signal_queue` | eligible signal batch | status = pending |
| 6 | Apply servicing-agent gate | company ZIP + active agent radius | covered companies only | SA assignment required |
| 7 | Apply verified-recipient gate | people/contact tables | verified recipient slots | verified email required |
| 8 | Compile CID | company + DOL + people + signal | `lcs_cid` | event written |
| 9 | Construct SID | CID + frame + voice rules | `lcs_sid_output` | voice pass |
| 10 | Select domain | `lcs_domain_rotation` | next safe Mailgun domain | active, cap available |
| 11 | Deliver MID | SID + recipient + domain | Mailgun send + MID state | Reply-To and CAN-SPAM |
| 12 | Capture webhook | Mailgun webhook | delivered/bounced/failed state | feedback loop |
| 13 | Pause unsafe domains | bounce/failure state | paused domain if needed | reputation gate |
| 14 | Write LBB evidence | events + batch stats | logbook record | compliance exists |
| 15 | Update Mission Control | health + batch result | map/process layer | operator visibility |
| 16 | Audit run | UT + YAML + live evidence | P=0/P=1 verdict | builder != auditor |
| 17 | Promote or repair | audit verdict | OPERATE or repair order | three clean fires |

## 12. Logbook

Every fire must write:

| Field | Required |
| --- | --- |
| batch_id | yes |
| run_started_at | yes |
| run_finished_at | yes |
| selected_count | yes |
| sent_count | yes |
| skipped_count | yes |
| voice_fail_count | yes |
| suppression_skip_count | yes |
| bounce_count | yes |
| paused_domain_count | yes |
| lcs_event_count | yes |
| mission_control_ref | yes |
| signed_by | yes |

## 13. Fleet Failure Registry

| Pattern | Failure | Repair |
| --- | --- | --- |
| Fragmented docs | Operators cannot find the run path | Use this file and paired YAML as the canonical step path |
| Protected-domain burn | Main domains enter cold outreach | Keep `svg.agency` and `svgwv.com` out of rotation |
| Empty queue | Sender is healthy but does nothing | Repair upstream signal feeder |
| No evidence | Emails send without compliance trace | Require LBB and Mission Control closeout |
| Stale source | External repo treated as process authority | Use Barton-Processes Process 100 folder as source of truth |

## 14. Session Log

| Date | Action |
| --- | --- |
| 2026-05-05 | Created paired step-by-step MD/YAML runbook to consolidate Process 100 documentation under Atlas and BS Law. |

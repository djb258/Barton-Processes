# Process 100 Domain Maintenance

## 1. Identity

| Field | Value |
| --- | --- |
| ID | PROC-100-DOMAIN-MAINTENANCE |
| Name | Process 100 Domain Maintenance |
| Medium | process |
| Business Silo | company lifecycle / outreach |
| CTB Position | factory/cl/100-lcs-pipeline/domain-maintenance |
| ORBT | BUILD |
| Authority | Process 100 LCS pipeline + Cloudflare DNS + Mailgun sending domains |
| Last Modified | 2026-05-05 |

### HEIR

| Field | Value |
| --- | --- |
| sovereign_ref | company-lifecycle |
| hub_id | lcs-pipeline |
| ctb_placement | factory/cl/100-lcs-pipeline |
| imo_topology | middle |
| cc_layer | Process 100 |
| services | Cloudflare, Mailgun, LCS Hub, Mission Control |
| secrets_provider | Doppler / Cloudflare CLI auth |
| acceptance_criteria | Every active sending domain is approved for outreach rotation, verified in Cloudflare DNS, verified in Mailgun, present in D1 rotation, and visible in Mission Control |

## 2. Purpose

Process 100 depends on clean sending-domain rotation. Cloudflare can contain new zones before LCS knows they exist. Mailgun can verify a domain before D1 starts rotating it. D1 can rotate a domain after DNS or reputation has failed. This process reconciles all three layers so the sender can run daily without domain drift.

Important: a domain being present in Mailgun is not enough to make it eligible for cold outreach. Main identity domains such as `svg.agency` and `svgwv.com` are protected brand domains. They may be verified in Mailgun for transactional or internal use, but they must not be inserted into `lcs_domain_rotation` unless the operator explicitly reclassifies them as burnable outreach domains.

## 3. Resources

| Resource | Purpose |
| --- | --- |
| Cloudflare zones | Source for owned domains and DNS records |
| Mailgun domains | Source for sending-domain verification and DKIM/SPF requirements |
| Composio Mailgun connection | Possible source for Mailgun action credentials and connected-account state |
| `lcs_domain_rotation` | Runtime rotation table used by the LCS sender |
| `lcs-hub /health` | Public readout of active domain capacity |
| Mission Control map layer | Operator view for domain health and rotation |
| `src/compiler.ts` | CID/SID/MID compiler that calls the delivery spoke |
| `src/spokes/delivery.ts` | Runtime delivery spoke for Mailgun/HeyReach delivery |
| `deliverability.ts` | Warmup caps, bounce threshold, Reply-To policy |

Required live access:

```powershell
npx wrangler whoami
$env:CLOUDFLARE_API_TOKEN
$env:MAILGUN_API_KEY
```

Current blocker observed on 2026-05-05: this shell is not logged into Cloudflare Wrangler, so live zone inventory cannot be queried until Cloudflare auth is restored.

## 4. IMO

### Input

| Input | Source |
| --- | --- |
| Cloudflare zone list | Cloudflare API / Wrangler |
| DNS records per domain | Cloudflare DNS |
| Mailgun verification state | Mailgun API |
| Domain runtime state | D1 `lcs_domain_rotation` |
| Delivery health | LCS events, bounces, failures, sent counts |
| New domain intake | Human/operator list of domains moved to Cloudflare |
| Domain classification | Human/operator decision: outreach rotation, protected identity, transactional, parked |

### Middle

1. Pull all Cloudflare zones that are part of SVG / Insurance Informatics sending infrastructure.
2. For each domain, derive the Mailgun sending host, normally `mg.<domain>`.
3. Verify DNS records: SPF, DKIM, DMARC, MX/return-path, tracking CNAME, and proxy status where Mailgun requires DNS-only.
4. Verify Mailgun domain status and required DNS values.
5. Check Composio for Mailgun connected-account state if mail actions are routed through Composio.
6. Classify each domain before rotation: outreach, protected identity, transactional, or parked.
7. Compare only outreach-approved Mailgun domains to D1 `lcs_domain_rotation`.
8. Insert missing outreach-approved domains as paused or warmup week 1, based on operator approval.
9. Keep protected identity domains out of `lcs_domain_rotation` even if they pass DNS and Mailgun verification.
10. Pause domains with failed DNS, failed Mailgun verification, high bounce rate, or missing webhook coverage.
11. Recompute capacity from active outreach domains and warmup caps.
12. Publish a domain health snapshot to Mission Control.
13. Log the reconciliation result to LBB.

### Output

| Output | Destination |
| --- | --- |
| Domain health report | Mission Control + LBB |
| Updated rotation rows | D1 `lcs_domain_rotation` |
| Pause/unpause actions | D1 `is_paused` |
| DNS repair list | Operator / Cloudflare |
| Capacity readout | Process 100 daily run gate |

## 5. Data Schema

Minimum runtime query:

```sql
SELECT
  domain,
  is_paused,
  warmup_week,
  daily_cap,
  sent_today,
  total_sent,
  bounce_count_24h,
  last_sent_at
FROM lcs_domain_rotation
ORDER BY is_paused ASC, warmup_week ASC, domain ASC;
```

Expected reconciliation record:

```yaml
domain: mg.example.com
root_domain: example.com
cloudflare_zone_status: active
dns:
  spf: pass
  dkim: pass
  dmarc: pass
  mx: pass
  tracking_cname: pass
mailgun:
  verified: true
  receiving_dns: pass
  sending_dns: pass
classification:
  class: outreach | protected_identity | transactional | parked
  rotation_allowed: true
rotation:
  present: true
  is_paused: false
  warmup_week: 1
  daily_cap: 20
  sent_today: 0
decision: active | paused | protected_do_not_rotate | needs_dns_repair | needs_mailgun_repair | missing_from_rotation
```

## 6. DMJ

| Define | Map | Join |
| --- | --- | --- |
| Owned domain | Cloudflare zone | Root domain joins to `mg.<domain>` |
| Sending domain | Mailgun domain | Mailgun FQDN joins to D1 `domain` |
| Protected domain | Operator classification | Protected domains never join to D1 rotation |
| Runtime sender | `lcs_domain_rotation` row | D1 row joins to `pickSendingDomain()` |
| Health gate | DNS + Mailgun + bounce rate | Gate result joins to Mission Control and LBB |

## 7. Constants & Variables

Constants:

| Constant | Value |
| --- | --- |
| Runtime table | `lcs_domain_rotation` |
| LCS health endpoint | `https://lcs-hub.svg-outreach.workers.dev/health` |
| Bounce threshold | `EMAIL_DELIVERABILITY_CONFIG.warmup.bounce_rate_threshold_percent` |
| Runtime selector | `pickSendingDomain()` |
| Daily reset location | LCS scheduled handler |
| Protected identity domains | `svg.agency`, `svgwv.com` |
| Current Mailgun delivery path | Barton Process 100 delivery spoke: `src/spokes/delivery.ts` |

Variables:

| Variable | Owner |
| --- | --- |
| New domains moved into Cloudflare | Operator |
| Initial warmup week | Operator / deliverability policy |
| Daily cap | Warmup policy |
| Pause/unpause decision | Domain maintenance process |
| DNS repair actions | Cloudflare operator |
| Domain classification | Operator |

## 8. Stop Conditions

| Condition | Action |
| --- | --- |
| Cloudflare auth missing | Stop live reconciliation and report auth blocker |
| Mailgun auth missing | Stop verification and report auth blocker |
| Domain missing SPF/DKIM/DMARC | Do not activate in D1 |
| Domain not verified in Mailgun | Do not activate in D1 |
| Domain is classified protected identity | Do not insert into `lcs_domain_rotation` |
| Bounce rate exceeds threshold | Pause domain |
| Domain is in Cloudflare but not in D1 | Report as missing from rotation |
| Domain is in D1 but not verified in Cloudflare/Mailgun | Pause or repair before daily send |

## 9. Verification

Cloudflare session:

```powershell
npx wrangler whoami
```

LCS public health:

```powershell
Invoke-RestMethod "https://lcs-hub.svg-outreach.workers.dev/health"
```

D1 rotation:

```powershell
npx wrangler d1 execute lcs-hub --remote --command "SELECT domain,is_paused,warmup_week,daily_cap,sent_today,total_sent,bounce_count_24h,last_sent_at FROM lcs_domain_rotation ORDER BY is_paused,warmup_week,domain;"
```

Cloudflare zone inventory:

```powershell
$headers = @{ Authorization = "Bearer $env:CLOUDFLARE_API_TOKEN" }
Invoke-RestMethod "https://api.cloudflare.com/client/v4/zones?per_page=100" -Headers $headers
```

DNS spot checks:

```powershell
Resolve-DnsName -Type TXT "mg.example.com"
Resolve-DnsName -Type TXT "_dmarc.example.com"
Resolve-DnsName -Type CNAME "k1._domainkey.mg.example.com"
Resolve-DnsName -Type MX "mg.example.com"
```

## 10. Analytics

| Metric | Target |
| --- | --- |
| Cloudflare zones reconciled | 100% |
| Composio Mailgun accounts checked | 100% |
| Mailgun verified domains in D1 | 100% |
| Active domains with failed DNS | 0 |
| Active domains over bounce threshold | 0 |
| Missing new domains after Cloudflare move | 0 |
| Protected domains in outreach rotation | 0 |
| Daily capacity visible in Mission Control | 100% |

## 11. Execution Trace

Each run records:

| Field | Required |
| --- | --- |
| run_id | yes |
| checked_at | yes |
| cloudflare_zone_count | yes |
| mailgun_domain_count | yes |
| d1_rotation_count | yes |
| active_rotation_count | yes |
| missing_from_d1 | yes |
| failed_dns | yes |
| failed_mailgun | yes |
| paused_for_reputation | yes |
| protected_domains_excluded | yes |
| total_daily_capacity | yes |
| signed_by | yes |

## 12. Logbook

Log only after the reconciliation run completes:

```yaml
action: process_100_domain_maintenance
result: pass | repair_required | blocked
cloudflare_checked: true
mailgun_checked: true
d1_checked: true
mission_control_updated: true
domains_added: []
domains_paused: []
domains_protected: []
domains_repaired: []
```

## 13. Fleet Failure Registry

| Pattern | Failure | Prevention |
| --- | --- | --- |
| Cloudflare-only domain | Domain moved but not added to Mailgun/D1 | Reconciliation flags missing from rotation |
| D1-only domain | Runtime rotates a bad or stale sender | DNS/Mailgun gate pauses the row |
| Protected-domain burn | Main identity domain enters cold outreach rotation | Classification gate blocks insertion |
| Warmup drift | Cap does not match reputation | Scheduled cap check and Mission Control alert |
| Bounce drift | Domain keeps sending after bounces | Auto-pause on threshold breach |
| Visibility drift | Operator cannot see capacity | Mission Control domain layer |

## 14. Session Log

| Date | Action |
| --- | --- |
| 2026-05-05 | Created domain-maintenance process after identifying Cloudflare auth blocker and existing LCS runtime rotation. |
| 2026-05-05 | Reconciled Doppler-backed Cloudflare/Mailgun access. Found 18 active Cloudflare zones, 16 active custom Mailgun domains, 14 D1 rotation domains. Classified `mg.svg.agency` and `mg.svgwv.com` as protected main-domain senders that must stay out of outreach rotation. |
| 2026-05-05 | Checked Composio v3.1 connected accounts through Doppler. Found 49 connected accounts and 0 Mailgun connected accounts. Current LCS Mailgun delivery is direct API, not Composio-routed. |

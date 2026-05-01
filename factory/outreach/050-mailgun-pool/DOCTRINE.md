# DOCTRINE — Mailgun Sender Pool (050)
## Locked rules governing the outreach campaign sender pool.
### Status: REPAIR
### ctb_node: barton-enterprises/insurance-informatics/svg-agency/outreach/mailgun-pool

---

## D-050-01 — Canonical Sender Pool Definition

The sender pool is the set of Mailgun custom domains + SMTP credentials authorized to send outreach campaigns on behalf of SVG Agency / Insurance Informatics. It is maintained in Mailgun under `GLOBAL_MAILGUN_API_KEY` (Doppler: imo-creator/dev).

**Primary domain:** `mg.insuranceinformatics.com` (oldest, highest reputation)
**Secondary domains:** `mg.svg.agency`, `mg.insuranceinformatics.agency`
**Expansion pool (available, not yet credentialed):** all remaining 13 active custom domains

---

## D-050-02 — DNS Requirements Before Any Domain Enters the Pool

A domain MUST have all three sending records in `valid` state before it is considered pool-eligible:

| Record | Type | Required Value |
|--------|------|---------------|
| SPF | TXT | `v=spf1 include:mailgun.org ~all` on the subdomain |
| DKIM | TXT | `k=rsa; p=...` on `{selector}._domainkey.{subdomain}` |
| CNAME | CNAME | `{subdomain}` → `mailgun.org` (tracking) |

MX records (`valid: "unknown"`) do NOT block sending. MX is receive-side only. Do not hold a domain out of the pool on MX status alone.

Verification command:
```bash
curl -s --user "api:$GLOBAL_MAILGUN_API_KEY" \
  "https://api.mailgun.net/v3/domains/{domain}" \
  | grep -o '"record_type":"[^"]*","valid":"[^"]*"'
```

All `sending_dns_records` must show `"valid":"valid"` before the domain is activated.

---

## D-050-03 — SMTP Credential Standard

Every active pool domain MUST have a minimum of 3 SMTP credentials to enable rotation. Credentials follow the naming convention:

- Login: `outreach{N}` (N = 1, 2, 3, ...)
- Password: stored in Doppler or in the Dave-action note — never committed to git
- Endpoint: `smtp.mailgun.org:587` (STARTTLS) or `smtp.mailgun.org:465` (SSL)

Creation command:
```bash
curl -s -X POST --user "api:$GLOBAL_MAILGUN_API_KEY" \
  -F login="outreach1" \
  -F password="{SECURE_PASSWORD}" \
  "https://api.mailgun.net/v3/domains/{domain}/credentials"
```

---

## D-050-04 — Domain Reputation Checks Before Campaign Send

Before sending a new campaign from any domain, verify:
1. Domain `state` == `active` via `GET /v3/domains/{domain}`
2. All sending DNS records `valid` (D-050-02)
3. No recent bounce/complaint spike in Mailgun logs (check Mailgun dashboard → Analytics)
4. Domain has been warmed (do not cold-send high volume from a brand-new domain)

---

## D-050-05 — Sandbox Domain Is NOT for Production

`sandboxc9d5277f17894e6988749752487bafb7.mailgun.org` is Mailgun's test sandbox. It requires authorized recipient whitelisting. Never route production campaign sends to the sandbox domain.

---

## D-050-06 — Secret Hygiene

- API key lives in Doppler: `imo-creator/dev/GLOBAL_MAILGUN_API_KEY`
- SMTP passwords are NOT stored in Doppler today — Dave-action item to add them
- Never commit credentials to git
- Never log credentials in LBB record content

---

## D-050-07 — Expansion Protocol

When adding a new domain to the active pool:
1. Verify DNS (D-050-02)
2. Create minimum 3 SMTP credentials (D-050-03)
3. Update `~/.claude/three-brain-state/mailgun-state-{date}.json`
4. Update the worker config if sender pool is hardcoded (Phase 3 of BAR-365)
5. Run a test send via `POST /v3/{domain}/messages`
6. Log in LBB under `svg-outreach-proc`

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| Version | 1.0.0 |
| BAR | BAR-365 |
| Owner | Dave Barton |
| Authority | Inherited (imo-creator sovereign) |

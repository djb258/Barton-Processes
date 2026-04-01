# PROCESS: LinkedIn Discovery
## Finds a LinkedIn profile URL for a person given their name, company, and location
### Status: BUILD
### Business: svg-agency

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-202 |
| Name | LinkedIn Discovery |
| Business Silo | svg-agency |
| CTB Position | factory/outreach/202-linkedin-discovery |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | — |
| BAR Reference | BAR-192 |
| Deployed URL | not deployed |
| Cron | Called conditionally by Process 200 orchestrator |
| Runtime | CF Worker |

---

## 2. WHY THIS EXISTS

Without a LinkedIn URL, you can't reach the person through HeyReach. LinkedIn is the backup channel when email bounces, and for some contacts it's the only channel. This process turns a name + company + location into a LinkedIn profile URL.

Called conditionally — only runs when Process 200 has filled a slot but the person has no LinkedIn URL. If Process 201 or another source already found LinkedIn (some email tools return both), this is skipped.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Process 200 fills a slot. Orchestrator checks: does this person have linkedin_url? No → call 202.
2. **"How do we get it?"** — Startpage search via DataImpulse residential proxy. Query LinkedIn's search index, parse profile URL from results.

### Input
- Person name (first_name, last_name from people_people_master)
- Company name (from cl_company_identity.canonical_name)
- City + State (from outreach_company_target)
- Slot type (CEO, CFO, HR — provides title context for search)

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Name + company + city + state + slot type | **Build search query** — `site:linkedin.com/in/ "Title" "Company" "City" "State"` | Formatted query string | String formatting (free) |
| 2 | Query | **Startpage search via proxy** — POST form to startpage.com/do/dsearch through DataImpulse sticky session | HTML results page | DataImpulse proxy (18-proxy-router) |
| 3 | HTML results | **Parse LinkedIn URL** — extract first `linkedin.com/in/` URL from results | LinkedIn profile URL | Regex parser (free) |
| 4 | LinkedIn URL | **Parse title tag** — fetch profile page via proxy, extract `<title>Name - Title at Company</title>` | Confirmation: name + title match | DataImpulse proxy |
| 5 | Confirmed URL | **Write to D1** — update people_people_master.linkedin_url | Slot enriched with LinkedIn | D1 write |

If Startpage returns no LinkedIn results, the person stays without LinkedIn. HeyReach channel unavailable for this contact.

### Output
- `people_people_master.linkedin_url` = LinkedIn profile URL
- `people_people_master.last_enrichment_attempt` = timestamp
- Source recorded

### Circle (Bedrock §5)
Process 500 (Talent Flow) uses LinkedIn URLs monthly to detect movement. If a LinkedIn URL goes dead (profile removed), flag for re-discovery on next cycle.

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

| Database | Binding | ID | Access | What It Provides |
|----------|---------|-----|--------|-----------------|
| svg-d1-outreach-ops | D1_OUTREACH | 73a285b8 | READ/WRITE | People master (write LinkedIn), company target (read city/state) |
| svg-d1-spine | D1 | 641a9a1e | READ | cl_company_identity (canonical_name) |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| PROXY_USER | imo-creator | dev | DataImpulse proxy auth |
| PROXY_PASS | imo-creator | dev | DataImpulse proxy auth |

### Proxy Configuration (constant — proven 2026-03-31)
- Host: gw.dataimpulse.com
- Port: 10000 (sticky session — NOT 823 rotating)
- Username format: {PROXY_USER}__cr.us (US country targeting)
- Method: POST form (`q={query}`)
- Delay: 3 seconds minimum between queries
- Cost: ~$1/GB (~$1-2/month at normal volume)

**Tool Priority (Well Drinks First):**
1. Startpage via DataImpulse — cheap, proven, primary method
2. Sub-hub 27 evaluation if hit rate drops — hunt for alternatives

---

## 5. OSAM — Where the Data Lives

### READ Access

| Table | What It Provides | Join Key |
|-------|-----------------|----------|
| `people_people_master` | Person name | `unique_id` |
| `people_company_slot` | Slot type (CEO/CFO/HR) | `person_unique_id` |
| `outreach_company_target` | City, state | `outreach_id` |
| `cl_company_identity` (spine) | Canonical company name | `outreach_id` |

### WRITE Access

| Table | What It Writes | When |
|-------|---------------|------|
| `people_people_master` | linkedin_url, last_enrichment_attempt | On successful discovery |

### Forbidden Paths

| Action | Why |
|--------|-----|
| Use rotating proxy (port 823) | CAPTCHA blocked. Sticky session (10000) only. |
| Use GET instead of POST for Startpage | CAPTCHA blocked. POST form only. |
| Skip the 3-second delay between queries | Proxy stability. Non-negotiable. |
| Call this process if linkedin_url already exists | Conditional — orchestrator checks first. |
| Scrape LinkedIn directly | ToS violation. Search index only. |

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants
- Startpage query format: `site:linkedin.com/in/ "Title" "Company" "City" "State"`
- DataImpulse proxy config: port 10000, sticky session, __cr.us, POST form
- 3-second minimum delay between queries
- LinkedIn title tag format: "Name - Title at Company | LinkedIn"
- Do not scrape LinkedIn directly — search index only

### Variables
- Which LinkedIn profile matches (many people share names)
- Hit rate per search (tracked in logbook)
- Whether Startpage changes their HTML structure (parser may need updating)

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Startpage returns CAPTCHA on 3 consecutive queries | HALT — proxy config may need updating |
| DataImpulse returns 5 consecutive connection errors | HALT — check proxy credentials |
| Hit rate drops below 50% | INVESTIGATE — query format or proxy issue |
| Strike 3 on same failure | Troubleshoot/Train → Airworthiness Directive |

---

## 8. DEPENDENCIES

### Upstream

| Dependency | What | Status |
|-----------|------|--------|
| Process 200 | Filled slot with person name | Required |
| outreach_company_target | City, state for search context | From SEED |
| cl_company_identity | Canonical company name | From SEED |
| DataImpulse proxy | Residential proxy for Startpage | Configured (Doppler) |

### Downstream

| Consumer | What It Needs |
|----------|--------------|
| Process 100 (LCS Pipeline) | LinkedIn URL for MID delivery via HeyReach |
| Process 500 (Talent Flow) | LinkedIn URL for monthly movement detection |
| Process 700 (Campaign Engine) | Reachability status: LINKEDIN_ONLY or FULL |

---

## 9. SMOKE TEST

```
1. Pick a person with name + company + city/state but no LinkedIn → build query → expected: well-formed Startpage query
2. Execute query via proxy → expected: HTTP 200, HTML with results (not CAPTCHA)
3. Parse results → expected: linkedin.com/in/ URL found
4. Fetch LinkedIn title tag via proxy → expected: "Name - Title at Company | LinkedIn"
5. Write to D1 → expected: linkedin_url populated on people_people_master
```

**Three Primitives Check:**
1. **Thing:** Does the person record exist? Does the proxy respond?
2. **Flow:** Does the query reach Startpage? Do results come back? Does the URL get written to D1?
3. **Change:** Is the linkedin_url field populated on the person record?

---

## 10. LOGBOOK

_No runs yet. Process in BUILD state._

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-01 |
| Last Modified | 2026-04-01 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |

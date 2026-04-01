# People Discovery Waterfall — Design Document
## Built from constants. Each process fills one variable. Tested and proven 2026-04-01.
### BAR-52, BAR-191, BAR-192

---

## The Insight

Startpage CAPTCHA detection is based on **query shape**, not content. Natural language queries like "who is the CEO of {company}" look like a human searching. Quoted patterns like `"CEO" "Company Name"` look like automation and get blocked.

By feeding rich context from D1 (company name + city + state + industry), we build queries that are both more accurate AND less likely to trigger CAPTCHA.

---

## The Waterfall

```
SEED (010) → fills company constants in D1
  ↓
Blog (300) → fills about_url, blog data, extracted names
  ↓
D1 View (v_slot_query_builder) → joins ALL constants into one row per slot
  ↓
Process 200 → reads view, checks what's missing, fills what it can
  ↓ slot has no LinkedIn?
Process 202 → "{name} {company} linkedin" → captures LinkedIn URL
  ↓ slot has no verified email?
Process 201 → email pattern + Startpage → Million Verifier confirms
```

Each process uses ALL constants from prior processes. The more that's filled, the richer the query, the better the results.

---

## D1 View: v_slot_query_builder

One view. Every constant in one row per slot. Processes read this, not individual tables.

```sql
SELECT slot_id, slot_type, is_filled, city, state, postal_code,
       industry, employees, domain, ein, about_url, filing_present,
       broker_or_advisor, carrier, renewal_month, funding_type,
       full_name, first_name, last_name, linkedin_url, email, email_verified
FROM v_slot_query_builder
WHERE is_filled = 0  -- only empty slots
```

---

## Process 200 — Find Person

**Input:** Empty slot from v_slot_query_builder with company constants.

**Query pattern (proven — zero CAPTCHA):**
- `who is the CEO of {company_name} in {city} {state}`
- `who is the CFO of {company_name} {city} {state}`
- `{company_name} HR director {city} {state}`

**Captures (raw):** All LinkedIn URLs, all emails, all name patterns, all dates, all leadership page URLs, all snippets. Store everything. Parse later.

**Name extraction (two passes):**
1. LinkedIn slug → name (57% of records). Clean, reliable.
2. Snippet parsing → name (73% of remaining). Needs filtering.
3. Total: 88% name capture rate.

**Recency check:** 69% of results have 2025-2026 dates. Flag records with only pre-2023 dates as stale.

**Conditional handoff:**
- Has name but no LinkedIn? → Send to Process 202
- Has name but no verified email? → Send to Process 201
- Has everything? → Slot filled. Done.

---

## Process 201 — Find Email

**Input:** Slot with name + domain (from 200 or view).

**Method:**
1. Generate 3 patterns: first.last@domain, firstlast@domain, flast@domain
2. Search each on Startpage UNQUOTED (quoted triggers CAPTCHA)
3. Compare result counts — highest count = most likely real
4. Send winner to Million Verifier for SMTP confirmation ($0.003)

**Why Startpage alone isn't enough:** Web presence ≠ deliverable mailbox. Tested 10 emails — Startpage said all 10 existed. Million Verifier said only 1 was actually deliverable. Companies get acquired, domains expire, people leave. The web index is stale.

**Million Verifier is the gate.** Credits available: 111,167. Cost: $0.003 each.

---

## Process 202 — Find LinkedIn

**Input:** Slot with name + company (from 200) but no LinkedIn URL.

**Method:** `{name} {company} linkedin` on Startpage.

**Hit rate:** 82% (18/22 in testing).

---

## Query Patterns — What Works vs What Doesn't

| Pattern | CAPTCHA? | Works? |
|---------|----------|--------|
| `who is the CEO of {company}` | NO | YES — best pattern |
| `{company} CFO {city} {state}` | NO | YES |
| `{company} HR director` | NO | YES |
| `{name} {company} linkedin` | NO | YES |
| `first.last@domain.com` (unquoted) | NO | YES |
| `"CEO" "Company Name"` (quoted) | YES | NO |
| `site:linkedin.com/in/` anything | YES | NO |
| `"linkedin"` as keyword with quotes | YES | NO |
| `"first.last@domain.com"` (quoted email) | YES | NO |

**Rule:** Natural language = safe. Quoted exact match = blocked.

---

## Proxy Configuration

- **Host:** gw.dataimpulse.com
- **Ports:** 10001+ (sticky sessions — rotate every 50 queries)
- **Username:** {user}__cr.us (US country targeting)
- **Method:** POST form to startpage.com/do/dsearch
- **Delay:** 3-5 seconds between queries
- **Port 10000:** BURNED from testing. Start at 10001+.
- **Rotation:** Fresh port = fresh IP. Prevents session burns.

---

## Test Results (2026-04-01)

### Process 200 — Capture (81 records)
- Captured OK: 81 (100%)
- CAPTCHA: 0
- Has LinkedIn URL: 61 (75%)
- Has name+title: 73 (90%)
- Has recent date: 56 (69%)
- Has leadership page: 71 (88%)

### Process 202 — LinkedIn backfill (22 records without LinkedIn)
- Found LinkedIn: 18 (82%)

### Email Pattern Search (10 records)
- All 10 found a winning pattern on Startpage
- first.last@ won 9/10 times
- Million Verifier confirmed 1/10 as deliverable (others: expired domains, no mailbox)

---

## Cost Model

| Item | Cost | Notes |
|------|------|-------|
| Startpage queries (~4/person × 117K) | ~$50 | Proxy bandwidth only |
| Million Verifier (1 check per person) | ~$351 | SMTP verification. 111K credits available. |
| **Total** | **~$401** | vs $1,170 HarvestAPI, vs $293 Bright Data (no email) |

---

## What's Left to Build

1. Rebuild Process 200 to read from v_slot_query_builder
2. Build smart query from all available constants
3. Capture raw, parse later
4. Conditional handoff to 201/202
5. 201 needs Million Verifier integration (API key in Doppler)
6. Name parser needs tuning (filter company names, fix slug parsing)
7. Recency scoring (flag pre-2023 results)

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-01 |
| BAR Reference | BAR-52, BAR-191, BAR-192 |
| Authority | Foundational Bedrock — Tier 0 |

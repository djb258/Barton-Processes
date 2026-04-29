> **ARCHIVED 2026-04-29** — Consolidated into PROCESS-UT.md and DOCTRINE.md during UT v2.7.0 standardization. See sibling files at folder root.

# DATA SOURCE REGISTRY — Slot Fill Sources
## Every source that feeds person data into slot_workbench — C&V defined per column
### Authority: BAR-197 | Governing Engine: Foundational Bedrock §2 (Constants & Variables)

---

## How This Works

Each source has columns. Each column is a constant: named, described, formatted, ID'd.
The VALUE that fills the column is the variable. The Organizer maps source columns → workbench columns.

**Target columns (what we're filling):**
- `person_first_name` — TEXT, the person's first name
- `person_last_name` — TEXT, the person's last name
- `person_email` — TEXT, verified or candidate email address
- `person_linkedin` — TEXT, linkedin.com/in/ profile URL
- `slot_type` — determines WHICH slot gets the fill (CEO, CFO, HR)

---

## SOURCE 1: enrichment_hunter_contact

**Table:** `enrichment_hunter_contact` (D1)
**Rows:** 175,632
**Join to workbench:** `outreach_id`

| Column | ID | Format | Description | Maps To |
|--------|-----|--------|-------------|---------|
| first_name | EHC-01 | TEXT, title case, 1-30 chars | Person's first name from Hunter.io API | `person_first_name` |
| last_name | EHC-02 | TEXT, title case, 1-30 chars | Person's last name from Hunter.io API | `person_last_name` |
| full_name | EHC-03 | TEXT, "{first} {last}", 3-60 chars | Concatenated full name | `person_full_name` |
| email | EHC-04 | TEXT, email format (user@domain.tld) | Email address discovered by Hunter | `person_email` |
| email_type | EHC-05 | TEXT, enum: personal / generic / unknown | Whether email is personal or role-based (info@, admin@) | Filter: skip generic |
| email_verified | EHC-06 | BOOLEAN | Hunter's verification status | `has_verified_email` |
| confidence_score | EHC-07 | INTEGER, 0-100 | Hunter's confidence the email is valid | Gate: ≥80 promote, <80 candidate |
| job_title | EHC-08 | TEXT, free-form, 0-200 chars | Raw job title string from Hunter | Classify → `slot_type` via Title Classifier |
| title_normalized | EHC-09 | TEXT, Hunter-normalized | Hunter's normalized title | Secondary classification input |
| seniority_level | EHC-10 | TEXT, enum: C-Level/Owner / Director / Manager / VP / Individual Contributor / NULL | Hunter's seniority classification | Map → `slot_type`: C-Level→CEO, Finance dept→CFO, HR dept→HR |
| department | EHC-11 | TEXT, enum: Executive / Management / Finance / HR / Sales / IT & Engineering / Operations & logistics / Marketing / Support / NULL | Hunter's department classification | Map → `slot_type` in combination with seniority |
| department_normalized | EHC-12 | TEXT, Hunter-normalized | Hunter's normalized department | Secondary mapping input |
| linkedin_url | EHC-13 | TEXT, URL format: https://linkedin.com/in/{slug} | LinkedIn profile URL | `person_linkedin` |
| phone_number | EHC-14 | TEXT, E.164 or free-form | Phone number | Future: `person_phone` |
| is_decision_maker | EHC-15 | BOOLEAN | Hunter's decision-maker flag | Gate: prioritize in slot fill |
| outreach_priority | EHC-16 | INTEGER | Computed priority score | Sort order for fill |
| data_quality_score | EHC-17 | REAL, 0-1 | Composite quality metric | Gate: minimum threshold |
| num_sources | EHC-18 | INTEGER | Number of data sources confirming this contact | Confidence boost |
| domain | EHC-19 | TEXT | Company domain | Validation: match to workbench domain |

**Slot Type Mapping (seniority + department → slot_type):**

| slot_type | seniority_level | department |
|-----------|----------------|-----------|
| CEO | C-Level/Owner | Executive, Management, Operations & logistics, Sales, NULL |
| CEO | Director | Executive, Management |
| CFO | C-Level/Owner, Director, Manager, VP | Finance |
| HR | C-Level/Owner, Director, Manager, VP | HR |

---

## SOURCE 2: vendor_people

**Table:** `vendor_people` (D1)
**Rows:** 175,632
**Join to workbench:** `outreach_id`

| Column | ID | Format | Description | Maps To |
|--------|-----|--------|-------------|---------|
| first_name | VP-01 | TEXT, title case, 1-30 chars | Person's first name from vendor enrichment | `person_first_name` |
| last_name | VP-02 | TEXT, title case, 1-30 chars | Person's last name | `person_last_name` |
| full_name | VP-03 | TEXT, "{first} {last}" | Full name | `person_full_name` |
| email | VP-04 | TEXT, email format | Email address | `person_email` |
| email_type | VP-05 | TEXT, enum: personal / generic | Email type | Filter: skip generic |
| email_verified | VP-06 | BOOLEAN | Verification status | `has_verified_email` |
| confidence_score | VP-07 | INTEGER, 0-100 | Confidence score | Gate threshold |
| job_title | VP-08 | TEXT, free-form | Raw job title | Classify → `slot_type` |
| title_normalized | VP-09 | TEXT | Normalized title | Secondary input |
| seniority_level | VP-10 | TEXT, same enum as Hunter | Seniority classification | Same mapping as Source 1 |
| department | VP-11 | TEXT, same enum as Hunter | Department classification | Same mapping as Source 1 |
| mapped_slot_type | VP-12 | TEXT, enum: ceo / cfo / hr / NULL | **Pre-mapped slot type** — already classified | DIRECT map to `slot_type` (when not NULL) |
| linkedin_url | VP-13 | TEXT, URL | LinkedIn profile URL | `person_linkedin` |
| phone_number | VP-14 | TEXT | Phone | Future |
| work_phone | VP-15 | TEXT | Work phone | Future |
| personal_phone | VP-16 | TEXT | Personal phone | Future |
| is_decision_maker | VP-17 | BOOLEAN | Decision-maker flag | Gate |
| company_name | VP-18 | TEXT | Company name from vendor | Validation: match workbench |
| city | VP-19 | TEXT | City | Validation |
| state | VP-20 | TEXT | State | Validation |

**Note:** `mapped_slot_type` (VP-12) is the direct path — when populated, skip classification and map straight to slot. When NULL, fall back to seniority+department mapping same as Source 1.

---

## SOURCE 3: enrichment_hunter_company

**Table:** `enrichment_hunter_company` (D1)
**Rows:** 15,537
**Join to workbench:** `outreach_id`

| Column | ID | Format | Description | Maps To |
|--------|-----|--------|-------------|---------|
| email_pattern | HC-01 | TEXT, template format: {first}.{last}, {f}{last}, etc. | Email pattern for the company's domain | `hunter_email_pattern` (already SEEDed) |
| organization | HC-02 | TEXT | Company name per Hunter | Validation |
| headcount | HC-03 | TEXT, range format: "51-200", "201-500" | Employee count range | `employees` backfill |
| industry_normalized | HC-04 | TEXT | Industry classification | `industry` backfill |
| domain | HC-05 | TEXT | Company domain | Join validation |

**Note:** This source fills COMPANY-level data, not person-level. The email_pattern is already SEEDed to workbench. Primary value is employee count backfill for the 16K slots with NULL employees.

---

## SOURCE 4: slot_workbench recon columns (from Process 300)

**Table:** `slot_workbench` — JSON columns populated by Process 300
**Already on workbench** — no join needed

| Column | ID | Format | Description | Maps To |
|--------|-----|--------|-------------|---------|
| recon_name_titles | RC-01 | JSON array: `[{"name": "First Last", "context": "Title at Company - LinkedIn"}]` | Raw name+context pairs extracted from Startpage search snippets | Parse → `person_first_name`, `person_last_name` via Organizer |
| recon_organized_people | RC-02 | JSON array: `[{"name": "...", "context": "...", "classification": "person/person_with_title/garbage", "bucket": "CEO/CFO/HR/REJECT", "confidence": 0-100}]` | Organized + classified entries from Organizer + Title Classifier | Map bucket → `slot_type`, name → `person_first_name`/`person_last_name` |
| recon_organized_linkedin | RC-03 | JSON array: `[{"name": "...", "context": "...", "classification": "linkedin"}]` | LinkedIn-tagged entries sorted by Organizer | Slug parse → `person_first_name`/`person_last_name`, URL → `person_linkedin` |
| recon_organized_garbage | RC-04 | JSON array: `[{"name": "...", "context": "...", "classification": "garbage"}]` | Company names, junk, unclassifiable | Skip — do not fill from this |
| recon_linkedin_people | RC-05 | JSON array: `["https://linkedin.com/in/slug", ...]` | LinkedIn profile URLs found in search results | Match slug to person name → `person_linkedin` |
| recon_linkedin_company | RC-06 | TEXT, URL | Company LinkedIn page URL | Not a person fill — company-level data |
| recon_emails | RC-07 | JSON array: `["email@domain.com", ...]` | Email addresses found in search result snippets | `person_email` (match to domain, prefer company domain match) |
| recon_result_urls | RC-08 | JSON array: `["https://url1.com", "https://url2.com", ...]` | All URLs from search results — NOT FETCHED, just addresses | Source 8 (future: fetch and parse) |
| recon_snippets | RC-09 | TEXT | Raw search result snippet text | NOT PARSED — potential secondary extraction |
| about_url | RC-10 | TEXT, single URL | Leadership/team/about page URL discovered during recon | Source 7 (future: fetch and parse) |

---

## SOURCE 5: slot_workbench hunter columns (from SEED)

**Table:** `slot_workbench` — flat columns SEEDed from Neon
**Already on workbench** — no join needed

| Column | ID | Format | Description | Maps To |
|--------|-----|--------|-------------|---------|
| hunter_first_name | WH-01 | TEXT, title case | Hunter candidate first name matched to this slot | `person_first_name` (if title matches slot_type) |
| hunter_last_name | WH-02 | TEXT, title case | Hunter candidate last name | `person_last_name` |
| hunter_email | WH-03 | TEXT, email format | Hunter candidate email | `person_email` (if confidence ≥ 80) |
| hunter_confidence | WH-04 | INTEGER, 0-100 | Confidence score for hunter_email | Gate: ≥80 promote |
| hunter_linkedin | WH-05 | TEXT, URL | Hunter candidate LinkedIn URL | `person_linkedin` |
| hunter_title | WH-06 | TEXT, free-form | Hunter candidate job title | Classify → match to `slot_type` |
| hunter_phone | WH-07 | TEXT | Hunter candidate phone | Future |
| hunter_contact_id | WH-08 | TEXT, UUID | Reference back to enrichment_hunter_contact row | Join key |
| hunter_email_pattern | WH-09 | TEXT, template: `{first}.{last}` | Email pattern for company domain | Generate email: pattern + person name + domain |
| vendor_email_pattern | WH-10 | TEXT, template | Alternate email pattern from vendor data | Fallback pattern |

---

## SOURCE 6: DOL 5500 Signers (Neon)

**Table:** `dol.form_5500` (Neon PostgreSQL — NOT in D1)
**Rows:** 140,054 with signer names
**Join to workbench:** `sponsor_dfe_ein` → `slot_workbench.ein`

| Column | ID | Format | Description | Maps To |
|--------|-----|--------|-------------|---------|
| spons_signed_name | DOL-01 | TEXT, ALL CAPS, format varies: "FIRST LAST" / "FIRST M. LAST" / "LAST, FIRST" / with suffixes (CPA, DMD, JR, III) | Plan sponsor who signed the 5500 — typically CEO/owner/president | `person_first_name` + `person_last_name` → CEO slot |
| admin_signed_name | DOL-02 | TEXT, ALL CAPS, same format variations as DOL-01 | Plan administrator who signed the 5500 — typically CFO, HR director, or benefits administrator | `person_first_name` + `person_last_name` → CFO or HR slot (only if different from spons_signed_name) |
| sponsor_dfe_ein | DOL-03 | TEXT, 9 digits, no dashes | Employer Identification Number — join key to workbench | Join: `slot_workbench.ein` |
| sponsor_dfe_name | DOL-04 | TEXT, ALL CAPS | Company name on filing | Validation: match to workbench company_name |
| form_year | DOL-05 | INTEGER, 4 digits (e.g., 2023, 2024) | Filing year — use most recent | Sort: DESC, take newest |
| admin_name | DOL-06 | TEXT, ALL CAPS | Plan administrator entity name (usually company name, not person) | Low value for person fill — usually "COMMITTEE" or company name |

**Name Format Variations (DOL-01, DOL-02):**

| Format | Example | Parse Rule |
|--------|---------|-----------|
| FIRST LAST | CHAD ROHRBACH | Split on space: first=parts[0], last=parts[-1] |
| FIRST M. LAST | EFRAIN M. FLORES DE HOSTOS | first=parts[0], last=parts[-1] (skip middle) |
| FIRST MIDDLE LAST | MARIA S. RUIZ ALONSO | first=parts[0], last=" ".join(parts[2:]) for Hispanic names |
| With suffix | MARION C. WACHNICKI, DMD | Strip after comma, then parse |
| ALL CAPS | VINCENZO PADOVANO | Title case: Vincenzo Padovano |
| Same person both fields | spons = admin (80%+ of filings) | Only fill CEO from spons. Only fill CFO/HR from admin when admin ≠ spons. |

---

## SOURCES 7-8: Not Yet Structured

## SOURCE 7: about_url pages (Management/Leadership Pages)

**Input:** `slot_workbench.about_url` — single URL per company (discovered by Process 300)
**Rows:** 69,174 slots have an about_url
**Fetch method:** curl_cffi (chrome131) + DataImpulse proxy
**Output:** Parsed person records — one per person found on page

The INPUT structure (HTML) varies by site — every page has its own format. The format IS the variable.
The OUTPUT structure (what we extract) is the constant. The BUCKETS that classify each element are the constants.

**The process:**
1. Fetch the page
2. Decompose into individual elements (every text block, heading, link, image caption)
3. Key Builder classifies each element into defined buckets — guard rails, not guessing
4. Quality gate validates identified elements (C&V three questions)
5. Store EVERYTHING — identified elements map to output columns, unidentified stored as KB-99
6. Re-run Bedrock on unidentified pile with better tools (funnel pattern — each pass tightens)
7. Key is stored per page URL — reusable for monthly Talent Flow checks (fetch page, apply key, diff values)

**The key is a one-time cost. Build it once, query forever. Monthly checks are just position reads against a known key.**

**Proven:** 100-page test found 4,841 people on 84 of 89 fetched pages (94% hit rate). Identification rules need tightening (39% → target 70%+) via Snap-On sub-hub 27 (Vendor Scout) or LLM tail pass on unidentified pile.

### Key Builder Buckets (guard rails — element must fit a bucket or it's unidentified)

| Bucket | ID | Format | Description |
|--------|-----|--------|-------------|
| company | KB-01 | TEXT, proper case or ALL CAPS, 2-100 chars | Company or organization name — matches the company we're looking for |
| position | KB-02 | TEXT, matches known position constant (CEO, CFO, Director, Owner, etc.) | Job position/role — from a defined set of ~60 position constants |
| title | KB-03 | TEXT, contains a position keyword + qualifiers, 3-120 chars | Full job title string containing a position keyword |
| person_name | KB-04 | TEXT, title case, 2-4 words, first+last capitalized, 4-50 chars, no reject words | A human person's name — strict rules, no navigation text, no company words |
| email | KB-05 | TEXT, user@domain.tld, user is personal (not info/contact/admin/support) | A personal email address |
| linkedin_url | KB-06 | TEXT, https://linkedin.com/in/{slug} | A LinkedIn personal profile URL |
| phone | KB-07 | TEXT, matches phone number pattern | A phone number |
| unidentified | KB-99 | TEXT, any | Element that does not fit any bucket — STORED, NOT DISCARDED |

**If it doesn't fit KB-01 through KB-07, it's KB-99. No guessing. No loose patterns.**

### Output Column Definitions (what we extract from every page)

| Column | ID | Format | Description | Maps To |
|--------|-----|--------|-------------|---------|
| person_name | PG-01 | TEXT, title case, "First Last", 3-60 chars | Person name extracted from page text — found near title keywords, in heading tags, or in structured name/title blocks | `person_first_name` + `person_last_name` (split on first space) |
| person_title | PG-02 | TEXT, free-form, 3-100 chars | Job title extracted from page — found adjacent to name (before, after, or in same block). Raw text, not yet classified. | Classify → `slot_type` via Title Classifier |
| person_linkedin | PG-03 | TEXT, URL format: https://linkedin.com/in/{slug} | LinkedIn profile URL found on the same page, linked from or near the person's name | `person_linkedin` |
| person_email | PG-04 | TEXT, email format (user@domain.tld) | Email address found on the page, matched to company domain | `person_email` |
| person_image_url | PG-05 | TEXT, URL | Headshot/profile photo URL (for future use — not currently mapped to workbench) | Future |
| page_url | PG-06 | TEXT, URL | The about_url that was fetched — provenance | Source tracking |
| page_type | PG-07 | TEXT, enum: team_page / about_page / contact_page / other | Classification of what kind of page this is | Parser strategy selection |
| company_match | PG-08 | BOOLEAN | Whether the page content matches the expected company (guards against redirects/wrong pages) | Validation gate |
| fetch_status | PG-09 | INTEGER, HTTP status code (200, 404, 403, 500, 0=timeout) | Result of the page fetch | C_1 comparator (fetch_failure_rate) |
| parse_method | PG-10 | TEXT, enum: title_keyword / name_comma_title / name_dash_title / linkedin_link / heading_block | Which parsing method extracted this person | Diagnostic — which methods work best |

### Input Patterns Observed (from 10-page sample)

The HTML varies but the name+title data appears in these patterns:

| Pattern ID | Format | Example | Frequency |
|------------|--------|---------|-----------|
| PAT-01 | Title then Name (heading block) | `<h3>Chief Executive Officer</h3><p>Elaine Pulakos</p>` | Common on team pages |
| PAT-02 | Name, Title (inline) | `Gary Hurst, Owner` | Common on about pages |
| PAT-03 | Name - Title (separator) | `John Smith - President` | Common in lists |
| PAT-04 | Name in image/link filename | `Marty-Kearns-Executive-Director-Netcentric.jpg` | Common on CMS sites |
| PAT-05 | Title in meta description | `Meet our CEO Elaine Pulakos` | Common in meta tags |
| PAT-06 | LinkedIn link + nearby name | `<a href="linkedin.com/in/gary-hurst">Gary Hurst</a>` | When LinkedIn links are on page |

**The patterns are the variables. The output columns (PG-01 through PG-10) are the constants.**

---

## SOURCE 8: recon_result_urls (Search Result Pages)

**Input:** `slot_workbench.recon_result_urls` — JSON array of URLs per slot
**Rows:** 93,063 slots have result URLs
**Status:** NOT FETCHED — URLs stored, page content not downloaded

**Process:** Same as Source 7. Classify URL type first (LinkedIn /in/, company page, directory, noise). Fetch the valuable ones. Run the same Key Builder (KB-01 through KB-99) to decompose and identify each element. Same buckets, same quality gate, same output columns. The Key Builder is a Snap-On Tool — it doesn't care whether the URL came from about_url or recon_result_urls.

### URL Type Classification (from 10-company sample)

| Type | Example | Value for Slot Fill |
|------|---------|-------------------|
| LinkedIn /in/ profile | `linkedin.com/in/roger-life-67736131` | HIGH — slug derives name, URL fills linkedin |
| Company about/team page | `oceanlakesservicecorp.com/about/` | HIGH — same as Source 7 |
| LinkedIn /company/ page | `linkedin.com/company/prometric` | LOW — company page, not person |
| ZoomInfo/directory | `zoominfo.com/pic/ocean-lakes` | MEDIUM — may have contacts |
| News/press/PDF | `congress.gov`, `justice.gov`, `.pdf` | LOW — rarely has leadership names |
| Unrelated | `annalsthoracicsurgery.org` | NONE — noise from search |

**Action:** Classify each URL by type. Fetch only HIGH-value types. Apply Source 7 parser (PG-01 through PG-10) to company pages. Apply LinkedIn slug parser (existing) to /in/ URLs.

Output columns for Source 8 = same as Source 7 (PG-01 through PG-10) for company pages, plus existing recon LinkedIn parsing for /in/ URLs. No new columns needed — just classification and routing.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-03 |
| Last Modified | 2026-04-03 |
| BAR Reference | BAR-197 |
| Authority | Foundational Bedrock §2 (C&V) |
| Status | GATED |

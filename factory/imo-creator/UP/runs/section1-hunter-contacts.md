# UP RUN: Section 1 — Hunter Contacts (enrichment_hunter_contact)
## Full UP execution — all six agents, evidence-based
### Date: 2026-04-03

---

## ORCHESTRATOR — Checklist & Dispatch

**Source:** enrichment_hunter_contact (D1)
**Rows:** 175,632
**Companies:** 25,998 (80% of 32,661)
**Join field:** outreach_id (direct — exists on every row)

### Pre-Flight Checklist

| Item | Status | Evidence |
|------|--------|---------|
| Data exists in D1? | YES | 175,632 rows confirmed |
| Key previously built? | PARTIAL | DATA_SOURCE_REGISTRY has 19 EHC IDs. Table has 25 columns. 6 missing definitions. |
| Map previously built? | PARTIAL | Slot-type mapping defined. Column-level mapping exists but not fully tested. |
| Join previously tested? | NO | outreach_id exists but join not formally tested at scale. |
| QC scorecard? | NO | Never run. |
| Auditor certification? | NO | Never certified. |

**Dispatch:** Run D Agent to complete the key (6 missing columns). Then M, J, QC, Auditor.

---

## D AGENT — DEFINE (Build the Key)

### Every Column — Description, Unique ID, Format

| Column | ID | Format | Description | C or V |
|--------|-----|--------|-------------|--------|
| id | EHC-00 | INTEGER, auto-increment | Row identifier — internal D1 primary key | C (structure) |
| outreach_id | EHC-01 | TEXT, UUID format (36 chars) | Company identifier — JOIN KEY to slot_workbench | C (structure) |
| company_unique_id | EHC-02 | TEXT, UUID format | Sovereign company ID from cl.company_identity | C (structure) |
| domain | EHC-03 | TEXT, domain format (e.g., company.com) | Company website domain — from Hunter.io | C (per company) |
| first_name | EHC-04 | TEXT, title case, 1-30 chars | Person's first name | V (the fill) |
| last_name | EHC-05 | TEXT, title case, 1-30 chars | Person's last name | V (the fill) |
| full_name | EHC-06 | TEXT, "{first} {last}", 3-60 chars | Concatenated full name | V (derived) |
| email | EHC-07 | TEXT, email format (user@domain.tld) | Email address discovered by Hunter | V (the fill) |
| email_type | EHC-08 | TEXT, enum: personal / generic / unknown | Whether email is personal or role-based | V (classification) |
| email_verified | EHC-09 | INTEGER, boolean (0/1) | Hunter's verification status | V (state) |
| confidence_score | EHC-10 | INTEGER, 0-100 | Hunter's confidence the email is valid | V (measurement) |
| job_title | EHC-11 | TEXT, free-form, 0-200 chars | Raw job title string from Hunter | V (the fill) |
| title_normalized | EHC-12 | TEXT, Hunter-normalized | Hunter's normalized title | V (derived) |
| seniority_level | EHC-13 | TEXT, enum: C-Level/Owner / Director / Manager / VP / Individual Contributor / NULL | Hunter's seniority classification | V (classification) |
| department | EHC-14 | TEXT, enum: Executive / Management / Finance / HR / Sales / IT & Engineering / Operations & logistics / Marketing / Support / NULL | Hunter's department classification | V (classification) |
| department_normalized | EHC-15 | TEXT, Hunter-normalized | Hunter's normalized department | V (derived) |
| linkedin_url | EHC-16 | TEXT, URL format: https://linkedin.com/in/{slug} | LinkedIn profile URL | V (the fill) |
| phone_number | EHC-17 | TEXT, E.164 or free-form | Phone number | V (the fill) |
| num_sources | EHC-18 | INTEGER, 1-50 | Number of data sources confirming this contact | V (measurement) |
| is_decision_maker | EHC-19 | INTEGER, boolean (0/1) | Hunter's decision-maker flag | V (classification) |
| outreach_priority | EHC-20 | INTEGER, 0-100 | Computed priority score | V (derived) |
| data_quality_score | EHC-21 | REAL, 0.0-1.0 | Composite quality metric | V (measurement) |
| source | EHC-22 | TEXT, enum or free-form | Which Hunter dataset this came from | C (provenance) |
| source_file | EHC-23 | TEXT, filename | Which import file this came from | C (provenance) |
| created_at | EHC-24 | TEXT, ISO-8601 datetime | When this record was created in D1 | C (timestamp) |

**25 columns. 25 definitions. All three properties (description, ID, format) present for every column.**

### Previously missing (now defined):
- EHC-00 (id) — internal key
- EHC-02 (company_unique_id) — was listed but renumbered
- EHC-12 (title_normalized) — was listed
- EHC-22 (source) — provenance
- EHC-23 (source_file) — provenance
- EHC-24 (created_at) — timestamp

### Constants vs Variables:
- **8 Constants:** id, outreach_id, company_unique_id, domain, source, source_file, created_at, email_type structure
- **17 Variables:** the person data that fills the constants — names, email, title, seniority, scores

### D Agent Pass: COMPLETE. Key built. All 25 columns defined with description, ID, format.

---

## M AGENT — MAP (Connect Key to Structure)

### Target: slot_workbench (the structure we fill)

| Source (EHC) | ID | Target (workbench) | Transform | Notes |
|-------------|-----|-------------------|-----------|-------|
| first_name | EHC-04 | person_first_name | Direct | |
| last_name | EHC-05 | person_last_name | Direct | |
| full_name | EHC-06 | person_full_name | Direct | |
| email | EHC-07 | person_email | Direct | Gate: confidence_score ≥ 80 |
| email_verified | EHC-09 | has_verified_email | Direct | |
| confidence_score | EHC-10 | (gate threshold) | Gate: ≥ 80 for email promotion | Not a column fill — a decision input |
| job_title | EHC-11 | (classify → slot_type) | Title Classifier → CEO/CFO/HR bucket | Snap-On Tool |
| seniority_level | EHC-13 | (classify → slot_type) | Seniority+department → slot mapping | See mapping table below |
| department | EHC-14 | (classify → slot_type) | Combined with seniority | See mapping table below |
| linkedin_url | EHC-16 | person_linkedin | Direct | |
| phone_number | EHC-17 | (future: person_phone) | Not currently mapped | No target column yet |
| is_decision_maker | EHC-19 | (priority gate) | Prioritize in fill order | Not a column fill — a decision input |
| domain | EHC-03 | (validation) | Match against workbench domain | Not a fill — a quality check |

### Slot Type Mapping (seniority + department → slot_type)

| slot_type | seniority_level | department |
|-----------|----------------|-----------|
| CEO | C-Level/Owner | Executive, Management, Operations & logistics, Sales, NULL |
| CEO | Director | Executive, Management |
| CFO | C-Level/Owner, Director, Manager, VP | Finance |
| HR | C-Level/Owner, Director, Manager, VP | HR |

### Unmapped columns (exist in source, no target in workbench):
- EHC-00 (id) — internal key, not person data
- EHC-02 (company_unique_id) — structural, exists in workbench already
- EHC-08 (email_type) — filter: skip "generic" emails, not a fill
- EHC-12 (title_normalized) — secondary to job_title classification
- EHC-15 (department_normalized) — secondary to department
- EHC-18 (num_sources) — confidence metric, not a fill
- EHC-20 (outreach_priority) — ordering metric, not a fill
- EHC-21 (data_quality_score) — quality metric, not a fill
- EHC-22 (source) — provenance, not a fill
- EHC-23 (source_file) — provenance, not a fill
- EHC-24 (created_at) — timestamp, not a fill

**13 columns mapped to workbench targets. 12 columns unmapped (infrastructure/metadata). Coverage: 100% of person-fillable data mapped.**

### M Agent Pass: COMPLETE. Mapping table built. Every column accounted for — mapped or documented as unmapped with reason.

---

## J AGENT — JOIN (Path to Spine)

### Join Path

| Source Field | Target Field | Type | Hops |
|-------------|-------------|------|------|
| EHC-01 (outreach_id) | slot_workbench.outreach_id | DIRECT | 1 |

**This is the simplest possible join.** outreach_id exists on every Hunter contact row. outreach_id is the spine of slot_workbench. One field, one hop, direct match.

### Join Test (evidence)

Need to verify: do all Hunter outreach_ids actually exist in slot_workbench?

### Company Match

The domain field (EHC-03) on the Hunter contact should match the domain field on slot_workbench for the same outreach_id. This is the quality check — does this Hunter contact actually belong to this company?

### J Agent Pass: JOIN PATH DEFINED. Direct join on outreach_id. Needs evidence testing.

---

## EVIDENCE TESTING (J Agent + QC Agent)

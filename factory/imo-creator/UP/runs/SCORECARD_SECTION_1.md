# UP SCORECARD — Section 1: Hunter Contacts
## Source: enrichment_hunter_contact (D1)
## Status: BUILD — Awaiting TS (Human Troubleshooting)
## Date: 2026-04-03

---

## What This Section Is

175,632 contact records from Hunter.io across 25,998 companies. Each record has a person's name, email, job title, seniority, department, LinkedIn URL. This is our largest person data source. It should be filling CEO, CFO, and HR slots.

---

## The Numbers

| ID | What We're Measuring | Result | Query |
|----|---------------------|--------|-------|
| S1-01 | Total records | 175,632 | `SELECT COUNT(*) FROM enrichment_hunter_contact` |
| S1-02 | Companies represented | 25,998 of 32,661 (80%) | `SELECT COUNT(DISTINCT outreach_id) FROM enrichment_hunter_contact` |
| S1-03 | Join to workbench | 100% — every outreach_id matches | `SELECT COUNT(DISTINCT CASE WHEN sw.outreach_id IS NOT NULL THEN ehc.outreach_id END) * 100.0 / COUNT(DISTINCT ehc.outreach_id) FROM (SELECT DISTINCT outreach_id FROM enrichment_hunter_contact) ehc LEFT JOIN (SELECT DISTINCT outreach_id FROM slot_workbench) sw ON ehc.outreach_id = sw.outreach_id` |
| S1-04 | Domain match (company verification) | 99.8% — 134 mismatches out of 126,599 | `SELECT SUM(CASE WHEN ehc.domain = sw.domain THEN 1 ELSE 0 END) * 100.0 / COUNT(*) FROM enrichment_hunter_contact ehc JOIN slot_workbench sw ON ehc.outreach_id = sw.outreach_id AND sw.slot_type = 'CEO' WHERE ehc.first_name IS NOT NULL AND ehc.first_name != ''` |
| S1-05 | Records with a person name | 126,599 (72.1%) | `SELECT COUNT(*) FROM enrichment_hunter_contact WHERE first_name IS NOT NULL AND first_name != ''` |
| S1-06 | Records WITHOUT a name | 49,033 (27.9%) | `SELECT COUNT(*) FROM enrichment_hunter_contact WHERE first_name IS NULL OR first_name = ''` |
| S1-07 | Records with email | 175,632 (100%) | `SELECT COUNT(*) FROM enrichment_hunter_contact WHERE email IS NOT NULL AND email != ''` |
| S1-08 | Records with LinkedIn URL | 109,286 (62.2%) | `SELECT COUNT(*) FROM enrichment_hunter_contact WHERE linkedin_url IS NOT NULL AND linkedin_url != ''` |
| S1-09 | Records with job title | 118,239 (67.3%) | `SELECT COUNT(*) FROM enrichment_hunter_contact WHERE job_title IS NOT NULL AND job_title != ''` |
| S1-10 | Records with seniority level | 50,766 (28.9%) | `SELECT COUNT(*) FROM enrichment_hunter_contact WHERE seniority_level IS NOT NULL` |
| S1-11 | Records with department | 50,766 (28.9%) | `SELECT COUNT(*) FROM enrichment_hunter_contact WHERE department IS NOT NULL` |

**All queries ran twice. Both runs returned identical results. Self-verification: PASS.**

---

## What This Means for Slot Filling

### What we CAN fill from this section:

| What | How Many | How |
|------|---------|-----|
| Person names (first + last) | 126,599 records with names | Map to person_first_name + person_last_name |
| Emails | 175,632 records — every record has one | Map to person_email (gate: confidence ≥ 80) |
| LinkedIn URLs | 109,286 records | Map to person_linkedin |
| Phone numbers | Not yet measured | Need to add S1-12 |

### How we match to slot types (CEO, CFO, HR):

| Method | Coverage | How It Works |
|--------|---------|-------------|
| Seniority + Department | 28.9% of records | C-Level/Owner + Finance = CFO. C-Level/Owner + HR = HR. Etc. |
| Job Title (via Title Classifier) | 67.3% of records | Run Title Classifier on job_title → CEO/CFO/HR bucket |
| Both missing | ~25% of records | Have name + email but no way to assign to a slot type |

**The gap:** 28.9% seniority coverage is too low to rely on seniority+department mapping alone. Job title (67.3%) is the better path. But 25% of records have NEITHER — they have a name and email but no role information. Those can't be mapped to a slot type without additional data.

---

## Issues to Troubleshoot

### Issue 1: 134 domain mismatches (0.2%)
- **What:** 134 Hunter contacts where the Hunter domain doesn't match the workbench domain for the same outreach_id
- **Impact:** These contacts might be at the wrong company. If we fill a slot from them, we put the wrong person in.
- **Query to investigate:** `SELECT ehc.outreach_id, ehc.domain as hunter_domain, sw.domain as workbench_domain, ehc.first_name, ehc.last_name FROM enrichment_hunter_contact ehc JOIN slot_workbench sw ON ehc.outreach_id = sw.outreach_id AND sw.slot_type = 'CEO' WHERE ehc.first_name IS NOT NULL AND ehc.first_name != '' AND ehc.domain != sw.domain LIMIT 20`
- **Decision needed:** Accept? Reject? Investigate each one?

### Issue 2: 49,033 records with no name (27.9%)
- **What:** Hunter records that have an email but no first_name or last_name
- **Impact:** Can't fill a person slot without a name. The email is usable but only if we find the name elsewhere.
- **Query to investigate:** `SELECT email, domain, job_title, seniority_level FROM enrichment_hunter_contact WHERE first_name IS NULL OR first_name = '' LIMIT 20`
- **Decision needed:** Are these recoverable? Can we derive names from email patterns? Or are they email-only records with no person data?

### Issue 3: 25% of records have no role information
- **What:** No seniority_level AND no job_title. Can't map to CEO/CFO/HR.
- **Impact:** These records have a name and email but we can't put them in a slot because we don't know which slot they belong to.
- **Query to investigate:** `SELECT first_name, last_name, email, domain FROM enrichment_hunter_contact WHERE first_name IS NOT NULL AND first_name != '' AND (job_title IS NULL OR job_title = '') AND seniority_level IS NULL LIMIT 20`
- **Decision needed:** Skip these? Or cross-reference against other sections (DOL signer name match, management page match) to figure out their role?

---

## Tolerance Decision (for Dave)

| Comparator | Measured | Suggested Tolerance | Your Call |
|-----------|---------|-------------------|-----------|
| Join resolution | 100% | 100% (binary — it resolves or it doesn't) | |
| Domain match | 99.8% | ? (is 0.2% mismatch acceptable?) | |
| Name coverage | 72.1% | ? (what % of records must have names to pass?) | |
| Role classification coverage | 67.3% via title, 28.9% via seniority | ? (what % must be classifiable?) | |
| Email coverage | 100% | 100% (every record has one) | |

**No tolerance has been set. This section cannot be certified until you review these numbers, investigate the issues, and set the tolerance for each comparator.**

---

## Document Control

| Field | Value |
|-------|-------|
| QC Run Date | 2026-04-03 |
| Self-Verification | ALL PASS (both runs match on every query) |
| TS Status | NOT RUN — awaiting Dave's review |
| Auditor Status | NOT RUN — cannot run without TS approval |
| ORBT | BUILD |

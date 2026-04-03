# UP SCORECARD — All 9 Sections
## Status: NO section certified. ALL require TS (human troubleshooting) before Auditor.
### Date: 2026-04-03
### BAR: 198

---

## The Rule

No data moves until certified. No certification without human-approved tolerance.
Every section runs: Orchestrator → D → M → J → QC → TS (Human) → Auditor.

---

## Scorecard

| Section | Source | D (Define) | M (Map) | J (Join) | QC (Scorecard) | TS (Human) | Auditor | Status |
|---------|--------|-----------|---------|----------|---------------|-----------|---------|--------|
| 1 | Hunter Contacts (175K) | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |
| 2 | Vendor People (175K) | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |
| 3 | Hunter Company (15K) | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |
| 4 | Recon Columns (80K) | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |
| 5 | Workbench Hunter | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |
| 6 | DOL 5500 Signers (140K) | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |
| 7 | Management Pages (20,707 fetched) | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |
| 8 | Search Result Pages (classified) | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |
| 9 | Platform Sources (running) | PENDING | PENDING | PENDING | PENDING | NOT RUN | NOT RUN | BUILD |

**0 of 9 sections certified. All in BUILD.**

---

## Per-Section Detail

### Section 1: Hunter Contacts
- **Source:** enrichment_hunter_contact (D1), 175,632 rows, 25 columns
- **D:** Key partially built in DATA_SOURCE_REGISTRY (EHC-01 to EHC-19). Full 25-column key drafted in UP run. NEEDS FORMAL PASS.
- **M:** Slot-type mapping defined (seniority+department → CEO/CFO/HR). NEEDS FORMAL PASS.
- **J:** outreach_id direct join. 100% resolution tested. 99.8% domain match. NEEDS FORMAL PASS.
- **QC:** Scorecard produced. Numbers: 100% join, 99.8% domain, 72.1% name coverage, 28.9% seniority coverage.
- **TS:** NOT RUN. Human has not reviewed scorecard. Tolerance not set. Not approved.
- **Auditor:** NOT RUN. Cannot run without TS approval.

### Section 2: Vendor People
- **Source:** vendor_people (D1), 175,632 rows, 34 columns
- **D:** Key partially built in DATA_SOURCE_REGISTRY (VP-01 to VP-20). 14 columns not yet defined.
- **M:** mapped_slot_type exists (direct path). Full mapping not tested.
- **J:** outreach_id direct join. Not tested at scale.
- **QC:** NOT RUN.
- **TS:** NOT RUN.
- **Auditor:** NOT RUN.

### Section 3: Hunter Company
- **Source:** enrichment_hunter_company (D1), 15,537 rows, 23 columns
- **D:** Key partially built in DATA_SOURCE_REGISTRY (HC-01 to HC-05). 18 columns not yet defined.
- **M:** email_pattern already mapped. headcount → employees backfill defined but not executed.
- **J:** outreach_id direct join. Not tested at scale.
- **QC:** NOT RUN.
- **TS:** NOT RUN.
- **Auditor:** NOT RUN.

### Section 4: Recon Columns
- **Source:** slot_workbench recon_* columns (D1), 80K+ slots
- **D:** Key built in DATA_SOURCE_REGISTRY (RC-01 to RC-10). Organizer ran on 80K slots.
- **M:** Organizer sorts into buckets. Title Classifier maps to slot_type.
- **J:** Already on workbench — outreach_id is the spine. No join needed.
- **QC:** Organizer comparators produced: 47% people, 45% LinkedIn, 8% garbage. P_organizer ratio 1.05 on C_6.
- **TS:** NOT RUN. Human has not reviewed organizer results.
- **Auditor:** NOT RUN.

### Section 5: Workbench Hunter
- **Source:** slot_workbench hunter_* columns (D1), 11,097 companies
- **D:** Key built in DATA_SOURCE_REGISTRY (WH-01 to WH-10).
- **M:** hunter_first_name → person_first_name. hunter_email → person_email (gate: confidence ≥ 80).
- **J:** Already on workbench — no join needed.
- **QC:** NOT RUN as formal UP step.
- **TS:** NOT RUN.
- **Auditor:** NOT RUN.

### Section 6: DOL 5500 Signers
- **Source:** dol.form_5500 (Neon), 140,054 filings with signer names
- **D:** Key built in DATA_SOURCE_REGISTRY (DOL-01 to DOL-06). Name format variations documented.
- **M:** spons_signed_name → CEO slot. admin_signed_name → CFO/HR slot.
- **J:** sponsor_dfe_ein → slot_workbench.ein. INDIRECT join (1 hop through EIN).
- **QC:** Test run: 1,979 fills, 384 unparseable names. Not formally scored.
- **TS:** NOT RUN. Human has not reviewed name parsing failures.
- **Auditor:** NOT RUN.

### Section 7: Management Pages
- **Source:** about_url pages. 20,707 fetched, 1,990 failed (403/404/timeout).
- **D:** Key Builder tested on 100 pages. 39% identification rate. Needs tightening.
- **M:** Output columns defined (PG-01 to PG-10). Not mapped at scale.
- **J:** about_url → outreach_id via workbench. Direct.
- **QC:** Fetch scorecard: 91% success, 9% failure (1,105 forbidden, 438 not found, 375 timeout).
- **TS:** NOT RUN. Human identified the 9% edge cases. Fix path not decided.
- **Auditor:** NOT RUN.

### Section 8: Search Result Pages
- **Source:** recon_result_urls (93K slots). Classified: 97K LinkedIn, 18K company pages, 71K noise.
- **D:** URL classification done. Page content NOT fetched. No key built.
- **M:** Not started. Pending fetch.
- **J:** outreach_id via workbench. Direct.
- **QC:** Classification scorecard exists. Page content not scored (not fetched).
- **TS:** NOT RUN.
- **Auditor:** NOT RUN.

### Section 9: Platform Sources
- **Source:** Platform recon running (24 workers). 10 platforms. Test: 86% coverage on 100 companies.
- **D:** Platform patterns defined (11 URL matchers). Page content NOT fetched. No keys built.
- **M:** Not started. Pending fetch.
- **J:** outreach_id via workbench (platform URL stored on workbench). Direct.
- **QC:** Test scorecard: 86% companies found platforms. Zero CAPTCHA.
- **TS:** NOT RUN.
- **Auditor:** NOT RUN.

---

## Human Tolerance (to be set per section per run)

| Section | Comparator | Human-Set Tolerance | Set By | Date |
|---------|-----------|-------------------|--------|------|
| 1 | Join resolution rate | TBD | Dave | — |
| 1 | Domain match rate | TBD | Dave | — |
| 1 | Name coverage minimum | TBD | Dave | — |
| 2-9 | (all comparators) | TBD | Dave | — |

**No tolerance has been set. No section has been approved. All sections are in BUILD.**

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-03 |
| BAR | 198 |
| Status | ALL SECTIONS BUILD — NONE CERTIFIED |
| Next Step | Run UP on each section, produce QC scorecards, TS with Dave on each one |

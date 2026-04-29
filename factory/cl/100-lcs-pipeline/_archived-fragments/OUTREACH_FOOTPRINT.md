> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# OUTREACH FOOTPRINT — Company Intelligence Architecture
## The CTB for every outreach_id — what we have, what we're missing, what to check
### Authority: Foundational Bedrock §4 (CTB) + §2 (C&V)
### Status: GATED
### BAR Reference: BAR-197

---

## The Structure

Every company (outreach_id) has a footprint. The footprint maps which of the 9 data sections have data for that company. All processes read the footprint first to know what's available, what's missing, and what to do.

```
═══════════════════════════════════════════════════════════════
                    OUTREACH_ID (trunk)
                    The company. One per.
═══════════════════════════════════════════════════════════════
                          │
                    FOOTPRINT MAP
                    Which sections exist for THIS company
                    9 booleans — the instruction set
                          │
         ┌────┬────┬────┬────┬────┬────┬────┬────┬────┐
         │ S1 │ S2 │ S3 │ S4 │ S5 │ S6 │ S7 │ S8 │ S9 │
         └────┴────┴────┴────┴────┴────┴────┴────┴────┘
           │    │    │    │    │    │    │    │    │
         BRANCHES — each section with its own structure
           │    │    │    │    │    │    │    │    │
         LEAVES — individual data elements inside each section
                  (060 defines the steps, comparators, tolerances)
```

---

## The 9 Sections

| # | Section | Source | Structure Status | Location | Key Type |
|---|---------|--------|-----------------|----------|----------|
| 1 | Hunter Contacts | enrichment_hunter_contact (D1) | DEFINED | DATA_SOURCE_REGISTRY.md, EHC-01 through EHC-19 | Database — one schema for all |
| 2 | Vendor People | vendor_people (D1) | DEFINED | DATA_SOURCE_REGISTRY.md, VP-01 through VP-20 | Database — one schema for all |
| 3 | Hunter Company | enrichment_hunter_company (D1) | DEFINED | DATA_SOURCE_REGISTRY.md, HC-01 through HC-05 | Database — one schema for all |
| 4 | Recon Columns | slot_workbench recon_* columns (D1) | DEFINED | DATA_SOURCE_REGISTRY.md, RC-01 through RC-10 | Database — one schema for all |
| 5 | Workbench Hunter | slot_workbench hunter_* columns (D1) | DEFINED | DATA_SOURCE_REGISTRY.md, WH-01 through WH-10 | Database — one schema for all |
| 6 | DOL 5500 Signers | dol.form_5500 (Neon) | DEFINED | DATA_SOURCE_REGISTRY.md, DOL-01 through DOL-06 | Database — one schema for all |
| 7 | Management Pages | about_url → fetch HTML | IN PROGRESS | PROC-301, Key Builder (KB-01 through KB-99) | One key PER PAGE — page format is the variable |
| 8 | Search Result Pages | recon_result_urls → classified | CLASSIFIED | URL classifier output — 18K company pages, 97K LinkedIn slugs | One key per page (company), one key per platform (LinkedIn) |
| 9 | Platform Sources | LinkedIn company, Facebook, Glassdoor, X, Indeed | NEW | Not yet built | One key PER PLATFORM — platform controls the format |

---

## Footprint Map — Per Outreach ID

The footprint is one row per outreach_id. Nine section flags plus metadata.

| Column | Type | Description |
|--------|------|-------------|
| outreach_id | TEXT PK | The company |
| has_section_1 | BOOLEAN | Hunter contacts exist for this company |
| has_section_2 | BOOLEAN | Vendor people exist |
| has_section_3 | BOOLEAN | Hunter company data exists |
| has_section_4 | BOOLEAN | Recon columns populated (300 ran) |
| has_section_5 | BOOLEAN | Workbench hunter columns populated (SEED) |
| has_section_6 | BOOLEAN | DOL 5500 filing exists with signer names |
| has_section_7 | BOOLEAN | Management page fetched and key built |
| has_section_8 | BOOLEAN | Search result pages classified and fetched |
| has_section_9 | BOOLEAN | Platform source pages identified and keyed |
| section_count | INTEGER | Total sections with data (0-9) |
| last_checked_at | TEXT | Last time footprint was evaluated |
| last_updated_at | TEXT | Last time any section got new data |

**section_count IS the intelligence tier.** More sections = richer CID = better message = higher response rate.

---

## Who Reads the Footprint

| Process | What It Reads | Why |
|---------|--------------|-----|
| PROC-100 (LCS Pipeline) | section_count → intelligence tier | Determines CID depth and message frame selection |
| PROC-200 (Find Person) | has_section_4, has_section_5, has_section_1 | Knows which gates have data for this company |
| PROC-201 (Find Email) | has_section_5 (email pattern), has_section_1 (hunter email) | Knows which email sources to try |
| PROC-202 (Find LinkedIn) | has_section_4 (recon LinkedIn), has_section_1 (hunter LinkedIn) | Knows which LinkedIn sources to try |
| PROC-301 (Page Parser) | has_section_7 | Knows if page already fetched and keyed |
| PROC-500 (Talent Flow) | ALL sections | Knows which sections to check for movement per company |
| PROC-700 (Campaign Engine) | section_count | Determines campaign model and personalization depth |

---

## Who Updates the Footprint

| Process | What It Updates | When |
|---------|----------------|------|
| PROC-010 (SEED) | Sections 1, 2, 3, 5 | After SEED from Neon |
| PROC-300 (Recon) | Section 4 | After Startpage search completes |
| PROC-301 (Page Parser) | Section 7 | After page fetched and key built |
| Source 6 script (DOL) | Section 6 | After DOL signer match runs |
| Source 8 script | Section 8 | After URL classification + fetch |
| Source 9 script (future) | Section 9 | After platform pages keyed |
| Talent Flow | last_checked_at | After monthly movement check |

---

## The CID Connection

The CID (Compiled Intelligence Dossier) is NOT a separate build. It's a READ of the footprint.

```
CID for Company X = 
    Section 1 data (if has_section_1) +
    Section 2 data (if has_section_2) +
    ... +
    Section 9 data (if has_section_9)
```

The more sections filled, the richer the CID. The CID compiler (Process 100) reads the footprint map, queries each available section, assembles the dossier. No guessing. No searching. Just reading structured data.

**The sections are the CID. The footprint tells you which sections to read.**

---

## The Talent Flow Connection

Talent Flow (Process 500) reads the footprint to know HOW to check each company:

- Section 7 exists → re-fetch management page, apply stored key, diff values
- Section 9 exists → check platform pages for announcements
- Section 6 exists → check next DOL filing for signer name changes
- Section 1 exists → check Hunter for contact updates

The footprint IS the monitoring plan per company. Different companies get different checks based on what sections they have. A company with 8 sections gets 8 checks. A company with 2 sections gets 2 checks.

---

## Key Architecture

| Sections | Key Type | Build Cost | Reuse |
|----------|----------|-----------|-------|
| 1-6 (database) | Schema — one for all | Already built | Permanent |
| 7 (management pages) | One key PER PAGE | One-time per company | Permanent — re-fetch uses same key |
| 8 (search result pages) | Same as 7 for company pages, same as platform for LinkedIn | One-time | Permanent |
| 9 (platform sources) | One key PER PLATFORM | One-time per platform (Facebook, LinkedIn, Glassdoor, X, Indeed) | Permanent — every company on that platform uses the same key |

**Sections 1-6:** Zero key cost. Already structured.
**Section 7:** One-time cost per company. 69K keys. Worth paying for (LLM, better parser, manual if needed).
**Section 8:** Mostly covered by 7 + platform keys.
**Section 9:** 5 platform keys total. Build once, cover 50K+ URLs.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-03 |
| BAR Reference | BAR-197 |
| Authority | Foundational Bedrock §4 (CTB) + §2 (C&V) |
| Status | GATED |
| Location | factory/cl/100-lcs-pipeline/OUTREACH_FOOTPRINT.md |
| Registry | factory/outreach/200-people-worker/DATA_SOURCE_REGISTRY.md |

# Barton-Processes — INDEX

## Process Index (Dewey card catalog)

| Dewey | # | Process | Silo | Folder | ORBT | Deployable | MC Page |
|-------|---|---------|------|--------|------|-----------|---------|
| bp.010 | 010 | SEED D1 | outreach | [factory/outreach/010-seed-d1/](factory/outreach/010-seed-d1/) | OPERATE | No | Watch Tower |
| bp.100 | 100 | LCS Pipeline | cl | [factory/cl/100-lcs-pipeline/](factory/cl/100-lcs-pipeline/) | REPAIR | Yes | Outreach Ops |
| bp.200 | 200 | People Worker | outreach | [factory/outreach/200-people-worker/](factory/outreach/200-people-worker/) | REPAIR | Yes | Watch Tower |
| bp.201 | 201 | Email Discovery | outreach | [factory/outreach/201-email-discovery/](factory/outreach/201-email-discovery/) | BUILD | No | Watch Tower |
| bp.202 | 202 | LinkedIn Discovery | outreach | [factory/outreach/202-linkedin-discovery/](factory/outreach/202-linkedin-discovery/) | BUILD | No | Watch Tower |
| bp.300 | 300 | Blog Worker | outreach | [factory/outreach/300-blog-worker/](factory/outreach/300-blog-worker/) | BUILD | No | Watch Tower |
| bp.301 | 301 | Page Parser | outreach | [factory/outreach/301-page-parser/](factory/outreach/301-page-parser/) | BUILD | No | Watch Tower |
| bp.400 | 400 | DOL Views | outreach | [factory/outreach/400-dol-views/](factory/outreach/400-dol-views/) | OPERATE | No | Watch Tower |
| bp.500 | 500 | Talent Flow | outreach | [factory/outreach/500-talent-flow/](factory/outreach/500-talent-flow/) | BUILD | No | Watch Tower |
| bp.600 | 600 | BIT Scoring | outreach | [factory/outreach/600-bit-scoring/](factory/outreach/600-bit-scoring/) | TROUBLESHOOT_TRAIN | No | Watch Tower |
| bp.700 | 700 | Campaign Engine | outreach | [factory/outreach/700-campaign-engine/](factory/outreach/700-campaign-engine/) | BUILD | No | Outreach Ops |
| bp.800 | 800 | Client Mint | cl | [factory/cl/800-client-mint/](factory/cl/800-client-mint/) | BUILD | Yes | Watch Tower |
| bp.810 | 810 | Client Intake | client | [factory/client/810-client-intake/](factory/client/810-client-intake/) | BUILD | Yes | Watch Tower |
| bp.820 | 820 | Vendor Export | client | [factory/client/820-vendor-export/](factory/client/820-vendor-export/) | BUILD | Yes | Watch Tower |
| bp.830 | 830 | Client Portal | client | [factory/client/830-client-portal/](factory/client/830-client-portal/) | BUILD | Yes | Watch Tower |
| bp.900 | 900 | Sales Portal | sales | [factory/sales/900-sales-portal/](factory/sales/900-sales-portal/) | BUILD | Yes | Sales Ops |

---

## How to find anything

1. Look up the process by number or title in the table above
2. Click the folder link to open the process directory
3. Open `PROCESS-UT.md` — consolidated UT (14 sections, 13-item pre-flight, 16 stable anchors)
4. Open `DOCTRINE.md` — locked rules for this process
5. `heir.yaml` — HEIR identity (8 fields, stamped at build, never changes)
6. `orbt.yaml` — current ORBT state (OPERATE / REPAIR / BUILD / TROUBLESHOOT_TRAIN)

---

## What's NOT a process

- `archive/` — historical extractions, orphans, relocations (read-only)
- `factory/_stubs/` — silos reserved for future processes (empty)
- `factory/content/` — content production folders (1700-video-ctb, 1800-cf-stream-upload, brand-assets — not data-movement processes)
- Trunk root files (CLAUDE.md, README.md, INDEX.md, etc.) — repo-wide governance

---

## ORBT Legend

| State | Meaning |
|-------|---------|
| OPERATE | Running in production |
| REPAIR | Broken — under active fix |
| BUILD | Being built — not yet deployed |
| TROUBLESHOOT_TRAIN | Strike 3 — root cause investigation |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-29 |
| Authority | imo-creator-v2 (Inherited) |
| Generated from | law/process-registry.yaml v2.0.0 |
| Validator | scripts/validate-ctb.sh |

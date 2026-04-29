# CLAUDE.md — Barton-Processes

## Identity

This is the **process engine** — where data moves. Governed by **imo-creator-v2** (the Garage).

Blueprint repos are the **brain** (schemas, doctrine, definitions — ZERO workers).
This repo is the **muscle** (every executable process across the fleet — 16 numbered, Dewey-classified).

**Hub ID**: barton-processes
**Sovereign Authority**: imo-creator-v2 (CC-01)
**CTB Position**: Branch — child of Barton Enterprises trunk, parent of all process leaves

---

## STARTUP PROTOCOL — Every Session

1. Read this file (CLAUDE.md) — front door
2. Read `INDEX.md` — Dewey card catalog of every process
3. Read `EXECUTION_ORDER.md` — operational dependency graph
4. Read `law/process-registry.yaml` — machine-readable index (v2.0.0)
5. Read `law/heir.yaml` + `law/orbt.yaml` — repo identity + state

---

## PROCESS INDEX (front door)

| # | Process | Folder | ORBT | MC Page |
|---|---------|--------|------|---------|
| 010 | SEED D1 | [factory/outreach/010-seed-d1/](factory/outreach/010-seed-d1/) | OPERATE | Watch Tower |
| 100 | LCS Pipeline | [factory/cl/100-lcs-pipeline/](factory/cl/100-lcs-pipeline/) | REPAIR | Outreach Ops |
| 200 | People Worker | [factory/outreach/200-people-worker/](factory/outreach/200-people-worker/) | REPAIR | Watch Tower |
| 201 | Email Discovery | [factory/outreach/201-email-discovery/](factory/outreach/201-email-discovery/) | BUILD | Watch Tower |
| 202 | LinkedIn Discovery | [factory/outreach/202-linkedin-discovery/](factory/outreach/202-linkedin-discovery/) | BUILD | Watch Tower |
| 300 | Blog Worker | [factory/outreach/300-blog-worker/](factory/outreach/300-blog-worker/) | BUILD | Watch Tower |
| 301 | Page Parser | [factory/outreach/301-page-parser/](factory/outreach/301-page-parser/) | BUILD | Watch Tower |
| 400 | DOL Views | [factory/outreach/400-dol-views/](factory/outreach/400-dol-views/) | OPERATE | Watch Tower |
| 500 | Talent Flow | [factory/outreach/500-talent-flow/](factory/outreach/500-talent-flow/) | BUILD | Watch Tower |
| 600 | BIT Scoring | [factory/outreach/600-bit-scoring/](factory/outreach/600-bit-scoring/) | TROUBLESHOOT_TRAIN | Watch Tower |
| 700 | Campaign Engine | [factory/outreach/700-campaign-engine/](factory/outreach/700-campaign-engine/) | BUILD | Outreach Ops |
| 800 | Client Mint | [factory/cl/800-client-mint/](factory/cl/800-client-mint/) | BUILD | Watch Tower |
| 810 | Client Intake | [factory/client/810-client-intake/](factory/client/810-client-intake/) | BUILD | Watch Tower |
| 820 | Vendor Export | [factory/client/820-vendor-export/](factory/client/820-vendor-export/) | BUILD | Watch Tower |
| 830 | Client Portal | [factory/client/830-client-portal/](factory/client/830-client-portal/) | BUILD | Watch Tower |
| 900 | Sales Portal | [factory/sales/900-sales-portal/](factory/sales/900-sales-portal/) | BUILD | Sales Ops |

For full detail per process: open its `PROCESS-UT.md` (14 sections, 13-item pre-flight, 16 stable anchors).

---

## REPO STRUCTURE (CTB)

```
Barton-Processes/              ← trunk root (governance files only)
├── CLAUDE.md
├── README.md
├── INDEX.md
├── EXECUTION_ORDER.md
├── D1_DATA_DICTIONARY.md
├── .gitignore
│
├── law/                       ← governance layer
│   ├── heir.yaml
│   ├── orbt.yaml
│   ├── process-registry.yaml  ← machine-readable index (v2.0.0)
│   ├── STRUCTURE_MANIFEST.yaml
│   ├── ingress-manifest.yaml
│   ├── logbook_schema.yaml
│   ├── PROCESS_TEMPLATE.md
│   └── PROCESS_AUDIT_TEMPLATE.md
│
├── factory/                   ← process silos
│   ├── cl/                    ← Company Lifecycle
│   │   ├── 100-lcs-pipeline/
│   │   └── 800-client-mint/
│   ├── outreach/              ← SVG Outreach (010, 200-700)
│   │   ├── 010-seed-d1/
│   │   ├── 200-people-worker/
│   │   ├── 201-email-discovery/
│   │   ├── 202-linkedin-discovery/
│   │   ├── 300-blog-worker/
│   │   ├── 301-page-parser/
│   │   ├── 400-dol-views/
│   │   ├── 500-talent-flow/
│   │   ├── 600-bit-scoring/
│   │   └── 700-campaign-engine/
│   ├── client/                ← Client processes (810-830)
│   │   ├── 810-client-intake/
│   │   ├── 820-vendor-export/
│   │   └── 830-client-portal/
│   ├── sales/                 ← Sales (900)
│   │   └── 900-sales-portal/
│   ├── content/               ← Non-process content production
│   │   ├── 1700-video-ctb/
│   │   ├── 1800-cf-stream-upload/
│   │   └── brand-assets/
│   └── _stubs/                ← Reserved silos (no processes yet)
│       ├── personal/
│       ├── real-estate/
│       └── production-line/
│
├── scripts/                   ← Validation + utility scripts
│   └── validate-ctb.sh        ← CTB rule enforcer (R1-R4 + R9)
│
├── archive/                   ← Read-only historical record
│   ├── v1-extractions-2026-04-29.tar.gz
│   ├── v1-extractions-README.md
│   ├── orphans-2026-04-29/
│   └── relocated-to-v2-2026-04-29/
│
├── docs/
└── log/
```

---

## CTB RULES (R1-R9)

See `law/STRUCTURE_MANIFEST.yaml` for machine-readable enforcement.

- **R1** — Trunk root: only allowlisted files + dirs (CLAUDE.md, README.md, INDEX.md, EXECUTION_ORDER.md, D1_DATA_DICTIONARY.md, .gitignore + law/ docs/ scripts/ log/ archive/ factory/)
- **R2** — `law/` only allowlisted governance files; no `law/doctrine/` subtree
- **R3** — `factory/<silo>/` has only numbered subfolders, no loose files
- **R4** — Each `factory/<silo>/<NNN-name>/` has PROCESS-UT.md + DOCTRINE.md + heir.yaml + orbt.yaml + _archived-fragments/ (+ wrangler.toml/src/package.json/etc. for deployable)
- **R5** — Mid-tier orphans go to `archive/orphans-YYYY-MM-DD/`, not floating in factory
- **R6** — Non-numbered content (video, brand) goes in `factory/content/` only
- **R7** — Empty silos live in `factory/_stubs/`; not at silo level
- **R8** — Garage-internal (LBB, UP, adapter-build) lives in `imo-creator-v2/`, not here
- **R9** — **No file lives in this repo without being inside a UT folder OR being repo-wide doctrine.** Process-specific files go inside `factory/<silo>/<NNN-name>/` (PROCESS-UT.md, DOCTRINE.md, heir.yaml, orbt.yaml, src/, _archived-fragments/, etc.). Cross-process docs go in `docs/`. Trunk root + `law/` reserved for repo-wide governance only. **Hard rule, machine-enforced.** See `law/FILE_LOCATION_DOCTRINE.md`.

Run `scripts/validate-ctb.sh` to check R1-R4 + R9 compliance. Exit 0 = clean.

---

## GOVERNANCE

- Children conform to parent (imo-creator-v2). Never the reverse.
- Blueprint repos = brain. This repo = muscle.
- Every process is numbered, Dewey-classified, and registered in `law/process-registry.yaml`.
- Auditor enforces rules. Determinism first.
- ASK > INFER. When uncertain, HALT and ask.
- The 13 locked constants in `imo-creator-v2/CLAUDE.md` are human-only. No LLM touches them.

---

## DOCTRINE LOAD ORDER (inherited from v2)

1. `imo-creator-v2/law/doctrine/KEY.md` — vocabulary first
2. `imo-creator-v2/CLAUDE.md` — architecture
3. `imo-creator-v2/law/doctrine/BARTON_ENTERPRISES_WORLD_ATLAS.md` — the legend
4. `imo-creator-v2/law/doctrine/FOUNDATIONAL_BEDROCK.md` — physics
5. This `CLAUDE.md` — BP-specific governance

---

## DOCUMENT CONTROL

| Field | Value |
|-------|-------|
| Created | 2026-03-14 |
| Last Modified | 2026-04-29 (Stage 2.5 CTB Cleanup) |
| Version | 2.0.0 |
| Status | ACTIVE |
| Authority | imo-creator-v2 (Inherited) |
| Audit | imo-creator-v2/law/doctrine/AUDITS/AUDIT-2026-04-29-barton-processes-ctb.md |

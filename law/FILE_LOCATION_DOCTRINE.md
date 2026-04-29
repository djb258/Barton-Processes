# FILE_LOCATION_DOCTRINE.md
## Hard rule: every file in Barton-Processes must be either repo-wide doctrine OR live inside a UT folder. No exceptions.
### Status: LOCKED (machine-enforced via validate-ctb.sh + STRUCTURE_MANIFEST.yaml)
### Authority: Dave Barton (sovereign)
### Created: 2026-04-29

---

## The rule

**Every file in this repo is one of two kinds:**

### Kind A — Repo-wide doctrine (governs ALL processes)

Lives in one of these locations:

| Location | Contents |
|---|---|
| Trunk root (`/`) | Only the 6 allowlisted files: `CLAUDE.md`, `README.md`, `INDEX.md`, `EXECUTION_ORDER.md`, `D1_DATA_DICTIONARY.md`, `.gitignore` |
| `law/` | Repo governance: heir.yaml, orbt.yaml, process-registry.yaml, STRUCTURE_MANIFEST.yaml, ingress-manifest.yaml, logbook_schema.yaml, PROCESS_TEMPLATE.md, PROCESS_AUDIT_TEMPLATE.md, FILE_LOCATION_DOCTRINE.md |
| `docs/` | Cross-process plans, specs, ADRs (must apply to ≥2 processes; if it applies to one, it goes in that process's folder) |
| `scripts/` | Repo-wide ops scripts (validate-ctb.sh, registry generators, etc.) |
| `log/` | Repo-level logbook entries |
| `archive/` | Historical artifacts (compressed v1-extractions, dated orphan archives, relocated-to-v2 trees) |

### Kind B — Process-specific (governs ONE process)

Lives ONLY inside the relevant `factory/<silo>/<NNN-name>/` folder. Anywhere else is a violation.

| Where it goes | What goes there |
|---|---|
| `PROCESS-UT.md` | All 14 sections of the UT — IDENTITY, PURPOSE, RESOURCES, IMO, DATA SCHEMA, DMJ, CONSTANTS, STOP CONDITIONS, VERIFICATION, ANALYTICS, EXECUTION TRACE, LOGBOOK, FAILURE REGISTRY, SESSION LOG |
| `DOCTRINE.md` | Per-process locked rules (D-NNN-XX) extracted from the UT's content |
| `heir.yaml` | 8-field WHERE coordinate per HEIR_SCHEMA.md |
| `orbt.yaml` | State machine per ORBT_SCHEMA.md |
| `wrangler.toml` / `package.json` / `tsconfig.json` | Deployment config (deployable processes only) |
| `src/` | Runtime code (deployable processes only) |
| `migrations/` | SQL migrations (D1-using processes only) |
| `_archived-fragments/` | Every prior fragment — PRD.md, ERD.md, OSAM.md, MANIFEST.md, AUDIT_REPORT.md, LEARNINGS.md, README.md, DATA_FLOW.md, RESEARCH_NOTES.md, etc. — preserved with archive header |

**Anything process-specific that doesn't fit one of the categories above goes in `_archived-fragments/` of the relevant process.** It does NOT live at the silo level (`factory/<silo>/`), at the trunk root, or at any other location.

---

## What this rule forbids

**No floating files at any of these levels:**

```
Barton-Processes/
├── ❌ NO non-allowlisted files at root   (e.g., RANDOM_NOTES.md, DRAFT.md, todo.txt)
├── factory/
│   ├── ❌ NO files at factory/ level     (e.g., factory/README.md)
│   └── <silo>/
│       ├── ❌ NO files at silo level     (kills client/UT_PROCESSES.md, sales/UT_PROCESS.md, factory/svg-agency/lcs/send-process/PROCESS.md, factory/outreach/tools/title-classifier/*)
│       └── <NNN-name>/   ← UT folder (only valid leaf)
│           ├── ✅ PROCESS-UT.md
│           ├── ✅ DOCTRINE.md
│           ├── ✅ heir.yaml + orbt.yaml + (deployable extras)
│           └── ✅ _archived-fragments/   ← everything process-specific that isn't the canonical 4 + runtime
└── ❌ NO mid-tier orphans (factory/<silo>/<sub-silo>/<process>/ is illegal — max 3 levels)
```

**Specifically forbidden patterns the auditor catches:**

| Pattern | Why forbidden | Where it goes instead |
|---|---|---|
| `factory/<silo>/UT_PROCESSES.md` (or any `.md`) | Silo-level floater | Either `_archived-fragments/` of the most-relevant process OR `archive/silo-level-fragments-YYYY-MM-DD/` if no clear owner |
| `factory/<silo>/<NNN-name>/PRD.md` (or ERD/OSAM/MANIFEST/PROCESS as separate files) | Process-specific fragmented UT | Consolidated into `PROCESS-UT.md` (14 sections); originals to `_archived-fragments/` |
| `factory/<silo>/<NNN-name>/CLAUDE.md` | Per-process CLAUDE.md | Trunk `CLAUDE.md` governs all processes; per-process governance lives in §1 of `PROCESS-UT.md` and `DOCTRINE.md` |
| `factory/<silo>/<NNN-name>/README.md` | Per-process README | Same — content rolls into PROCESS-UT.md §2 PURPOSE; original to `_archived-fragments/` |
| `factory/<silo>/<NNN-name>/AUDIT_REPORT.md` | Audit findings outside the UT | Findings go in PROCESS-UT.md §13 FLEET FAILURE REGISTRY; original to `_archived-fragments/` |
| `factory/<silo>/<NNN-name>/LEARNINGS.md` | Loose lessons doc | Lessons go in DOCTRINE.md as locked rules with source attribution; original to `_archived-fragments/` |
| `factory/<silo>/<NNN-name>/.wrangler/` or `.up-runs/` | Build cache / Dyno artifacts | `.gitignore` it; never commit |
| `factory/017-video-ctb/` (non-numbered branch folder) | Non-numbered at branch level | Move to `factory/content/1700-video-ctb/` (renumbered) OR archive |
| `factory/imo-creator/` (garage-internal) | Garage tools in process repo | Move to v2 (the garage); `archive/relocated-to-v2-YYYY-MM-DD/` if needs preservation |

---

## What this rule allows (the only escape hatch)

**Cross-process docs in `docs/`** — IF they genuinely apply to two or more processes. The test:

> Does this doc describe behavior, schema, or rules that span multiple processes (e.g., "how all outreach processes interact with the spine D1")?

- YES → `docs/<doc-name>.md` is allowed (Kind A repo-wide doctrine)
- NO → it belongs in the most-relevant process folder (Kind B)

If unclear, default to Kind B (process folder). Drift toward repo-wide is the failure mode that produces silo-level floaters; drift toward process-folder is conservative and reversible.

---

## Auditor enforcement (G42, G43, G44)

Three new gates added to the auditor checklist:

| Gate | Check | Pass condition |
|------|-------|----------------|
| G42 | No process-specific files outside UT folders | Every `.md`, `.yaml`, `.json` (excluding allowlisted trunk + law/ + cross-process docs/) lives inside a `factory/<silo>/<NNN-name>/` UT folder |
| G43 | No floating files at silo level | `factory/<silo>/` directories contain ZERO files (only numbered subfolders) — strict enforcement of R3 |
| G44 | Cross-process docs in docs/ have ≥2 process references | Each file in `docs/` either explicitly names ≥2 processes by Dewey number OR is a generic ADR/plan that references repo-wide concerns |

---

## How `validate-ctb.sh` enforces this mechanically

The validator script extends to enforce R3 + R9 (this doctrine):

```bash
# R9: every file under factory/ is inside a UT folder
for f in $(find factory -type f); do
  case "$f" in
    factory/*/[0-9]*-*/PROCESS-UT.md) ;;
    factory/*/[0-9]*-*/DOCTRINE.md) ;;
    factory/*/[0-9]*-*/heir.yaml) ;;
    factory/*/[0-9]*-*/orbt.yaml) ;;
    factory/*/[0-9]*-*/wrangler.toml) ;;
    factory/*/[0-9]*-*/package.json) ;;
    factory/*/[0-9]*-*/tsconfig.json) ;;
    factory/*/[0-9]*-*/package-lock.json) ;;
    factory/*/[0-9]*-*/src/*) ;;
    factory/*/[0-9]*-*/migrations/*) ;;
    factory/*/[0-9]*-*/_archived-fragments/*) ;;
    factory/*/[0-9]*-*/vendor_library/*) ;;  # documented exception per 820
    factory/_stubs/*) ;;                       # _stubs exempt
    factory/content/*) ;;                      # content silo exempt (runner-renumbered)
    *)
      echo "R9 FAIL: $f is outside any UT folder"
      errors=$((errors+1))
      ;;
  esac
done
```

Exit non-zero on any violation. CI gate.

---

## How to migrate an existing process-specific file when it's discovered

If during a session you discover a process-specific file in the wrong location:

1. **Don't delete.** Move to `_archived-fragments/` of the relevant process with archive header.
2. **Roll content** into the appropriate UT section or DOCTRINE rule if it's still relevant.
3. **Log the move** in PROCESS-UT.md §11 EXECUTION TRACE.
4. **Re-run validate-ctb.sh** to confirm clean.

If the file is genuinely cross-process, propose moving it to `docs/` instead — but document which ≥2 processes it spans in the doc's frontmatter.

---

## Reference enforcement

- **`law/STRUCTURE_MANIFEST.yaml`** — declares the rule machine-readably (R9 added)
- **`scripts/validate-ctb.sh`** — checks R9 mechanically; CI gate
- **Codex Auditor** — runs G42, G43, G44 in addition to G1-G38

---

## Why this rule exists

Without it, the repo accretes orphans. Pre-cleanup state had:
- `factory/client/UT_PROCESSES.md` (silo-level floater)
- `factory/client/TABLES-AUDIT.md` (silo-level floater)
- `factory/sales/UT_PROCESS.md` (silo-level floater)
- 13 fragmented docs at root of `factory/outreach/200-people-worker/` (PRD + ERD + OSAM + MANIFEST + PROCESS + CLAUDE + ARCHITECTURE + AUDIT_REPORT + LEARNINGS + WATERFALL_DESIGN + D1_SCHEMA + DATA_SOURCE_REGISTRY + OSAM_D1_MAPPING)
- `factory/svg-agency/lcs/send-process/PROCESS.md` (mid-tier orphan)
- `factory/outreach/tools/title-classifier/*` (non-numbered tooling)
- `factory/imo-creator/*` (garage-internal in process repo)
- `factory/017-video-ctb/`, `factory/018-cf-stream-upload/`, `factory/brand/` (non-numbered branch folders)

All of these became invisible to MC, drifted from doctrine, and made the repo unnavigable. The 2026-04-29 cleanup absorbed them all into either `_archived-fragments/` of the relevant process or dated `archive/` buckets. **This rule prevents recurrence.**

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-29 |
| Status | LOCKED — machine-enforced |
| Authority | Dave Barton (sovereign) |
| Inherits | CTB_RULES.md (R1-R8) extends to add R9 |
| Auditor gates | G42, G43, G44 (added to G1-G38 set) |
| Validator | `scripts/validate-ctb.sh` (R9 check added) |
| Manifest | `law/STRUCTURE_MANIFEST.yaml` v3.1.0 (R9 codified) |

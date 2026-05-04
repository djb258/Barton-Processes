# PROCESS-UT — FCE-Fill Operator Runbook (PROC-080)

**UT-Body species per Book Law (`atlas/constants/BOOK_LAW.md` v1.5.0)**
**Y-junction conformant per BS Law (`atlas/constants/BS_LAW.md` v1.5.0)**
**UT v2.8.0 + UT_CHECKLIST v1.3.1 conformant**

---

## UT Pre-Flight Checklist (per `atlas/constants/UT_CHECKLIST.md` v1.3.1)

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §2 |
| 2 | OSAM — READ / WRITE / Process Composition / Join Chain / Forbidden / Query Routing | ☑ | §5 |
| 3 | Component Status — every dep 🟢 / 🟡 / 🔴 with 1-line state | ☑ | §3 |
| 4 | Owner — human who fixes this at 2 AM | ☑ | §1 |
| 5 | Live Dashboard — URL or explicit "N/A" | ☑ | §3 (N/A — no real-time dashboard for fill spec itself) |
| 6 | Kill Switch — exact command to stop the process | ☑ | §8 |
| 7 | Logbook — last audit verdict + date (after certification only) | ☐ | §12 (legitimately deferred until Codex PASS) |
| 8 | FCEs Attached — which FCE runs structurally back this doc | ☑ | §3 (none — this IS the FCE-fill runbook) |
| 9 | BARs Referenced — every BAR this doc touches, with status | ☑ | §3 |
| 10 | LBB Subjects Fed — which LBB subject(s) this doc's session logs go to | ☑ | §3 (`processes`) |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | ☑ | §1b |
| 12 | Live Verification — every numeric count, cron, URL, command, BAR status grounded | ☐ | §9b (deferred until first FCE run + Codex PASS) |
| 13 | ctb_node — declared path on Barton Enterprises CTB trunk | ☑ | §1 |

---

## §1 IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-080 |
| Name | FCE-Fill Operator Runbook |
| Species | UT-Body (Book Law v1.5.0) |
| Version | 1.0.0 |
| Status | BUILD |
| Created | 2026-05-04 |
| Last Modified | 2026-05-04 |
| Authority | Dave Barton (sovereign) |
| Owner | Dave Barton (fixes at 2 AM) |
| ctb_node | `barton-enterprises/imo-creator/fce-fill` |
| BAR Reference | BAR-PROC-080 |
| Fill Spec | `imo-creator-v2/atlas/FCE_FILL_INSTRUCTIONS.md` (canonical — do not duplicate prose here) |
| Locked Constants Used | FCE.md (#3), UNIFIED_TEMPLATE.md (#6), UT_CHECKLIST.md (#11) |
| D1 Ingestion Rules | `imo-creator-v2/atlas/FCE_DATABASE_RULES.md` |
| Engine | K=C (vocabulary lock per FCE four-columns ceiling) then DMJ (Define/Map/Join into D1 fce table) |
| ORBT | BUILD |

---

## §1b GEOMETRY

| Field | Value |
|-------|-------|
| CTB Position | Leaf — `barton-enterprises/imo-creator/fce-fill` |
| Hub-Spoke Role | SPOKE (this Process calls the FCE engine, which is the hub) |
| Altitude | 10k operational |
| Sovereign | Dave Barton (trunk — `barton-enterprises`) |
| Parent Branch | `barton-enterprises/imo-creator` |

```
CTB VIEW (50k → 5k)
─────────────────────────────────────────────
Trunk: barton-enterprises
  └─ Branch: imo-creator
       └─ Leaf: fce-fill (PROC-080) ← YOU ARE HERE

TRACE-BACK (this doc is derived from, does not modify)
─────────────────────────────────────────────
atlas/constants/FCE.md (#3 locked constant)
  ↓ governs
atlas/FCE_FILL_INSTRUCTIONS.md (canonical fill spec — read-only here)
  ↓ implemented by
PROC-080 (this operator runbook)
  ↓ produces
Conformant FCE Books shelved in the Library

HUB-SPOKE WIRING
─────────────────────────────────────────────
[Operator] ──► [PROC-080 SPOKE] ──► [FCE Engine (US → K=C → DMJ → UP)]
                                           │
                                    [D1 fce table]
                                    [LBB ingestion]
                                    [Codex audit]
```

---

## §2 PRD

**WHAT.** An operator runbook for building conformant FCE Books. This process walks an operator from domain declaration to a Library-shelved, 14-section FCE artifact that passes all fill-rule tolerances and D1 ingestion gates defined in the canonical fill spec.

**WHY.** Without a repeatable operator runbook, FCE builds are ad-hoc — wrong section order, missing columns, fill rule violations not caught until Codex audit. PROC-080 encodes the sequence so that any mechanic can produce a conformant FCE Book in one pass.

**WHO.** Operator / Foreman (dispatches the build). Mechanic / Sonnet (executes the fill). Auditor / Codex (issues PASS/FAIL). Canonical fill spec: `imo-creator-v2/atlas/FCE_FILL_INSTRUCTIONS.md`.

**SCOPE.**
- Domain declaration and scope lock
- Source identification and channel profiling
- Fill sequence: all 14 UNIFIED_TEMPLATE sections per FCE fill rules
- K=C vocabulary lock (four-columns ceiling)
- DMJ into D1 fce table
- Codex audit gate
- LBB session log ingest

**OUT OF SCOPE.**
- FCE engine internals (US/K=C/DMJ/UP runtime) — sealed Coca-Cola, see `atlas/dyno/`
- FCE database schema modifications — see `atlas/FCE_DATABASE_RULES.md`
- Domain FCE content (categories, metrics, constants) — filled per-run by the engine

**SUCCESS METRIC.** A completed FCE build produces: (1) one 14-section FCE Book with all 0→1 tolerances at 1, (2) one D1 `fce` table row with `domain_id = FCE-NNN`, (3) one LBB record in `processes` subject, (4) Codex PASS verdict.

---

## §3 RESOURCES / COMPONENT STATUS / DEPENDENCIES

### Component Status

| Component | Status | State |
|-----------|--------|-------|
| `atlas/constants/FCE.md` (#3) | 🟢 | LOCKED. Four-columns doctrine, gate outputs, adapter model. |
| `atlas/constants/UNIFIED_TEMPLATE.md` (#6) | 🟢 | LOCKED. 14-section skeleton every FCE Book uses. |
| `atlas/constants/UT_CHECKLIST.md` (#11) | 🟢 | LOCKED. 13-item pre-flight checklist. v1.3.1. |
| `atlas/FCE_FILL_INSTRUCTIONS.md` | 🟢 | GATED. Canonical fill spec — DO NOT duplicate prose here. |
| `atlas/FCE_DATABASE_RULES.md` | 🟡 | Reference. D1 ingestion rules for fce table. |
| D1 `fce` table | 🟢 | Canonical store for FCE domains, cells, sources, mappings. |
| D1 `fce_error` table | 🟢 | Error store for failed FCE operations. |
| LBB Worker | 🟢 | `https://lbb.svg-outreach.workers.dev` — session log ingest. |
| Codex (auditor) | 🟢 | Different engine than mechanic. Aviation Model invariant. |

### FCEs Attached

None — this IS the FCE-fill operator runbook. Individual FCE runs (e.g., FCE-001 for a specific domain) will reference this process.

### BARs Referenced

| BAR | Status |
|-----|--------|
| BAR-PROC-080 | OPEN — creation of this runbook |

### LBB Subjects Fed

`processes` (subject_id: `processes`) — session logs from every FCE build go here.

---

## §4 IMO

**Two-Question Intake:**
1. **What triggers this?** — Human declares a domain to evaluate (e.g., "build FCE for self-storage market"). OR monthly cron triggers refresh of an existing FCE.
2. **How do we get it?** — Domain name + business intent from operator. Source data from published content (Supadata, WebSearch, manual).

**Input:**
- Domain declaration (human-provided)
- Business intent (what decision does this FCE enable?)
- Source list seed (operator provides starting sources; engine expands)

**Middle:**

| Step | What Happens | Output | Tool |
|------|-------------|--------|------|
| 1 | Read canonical fill spec | Fill rules loaded | `atlas/FCE_FILL_INSTRUCTIONS.md` |
| 2 | Declare domain, lock FCE-NNN ID | Identity block filled (§1) | Human / Foreman |
| 3 | K=C vocabulary lock | Four-columns ceiling confirmed | K=C engine |
| 4 | Source identification + channel profiling | §3 RESOURCES filled | WebSearch / Supadata |
| 5 | Fill §2 PURPOSE — domain, why, what breaks | §2 filled 0→1 | Mechanic |
| 6 | Fill §4 IMO — two-question intake, 8 middle steps | §4 filled 0→1 | Mechanic |
| 7 | Fill §5 DATA SCHEMA — four columns + altitude model | §5 filled 0→1 | Mechanic |
| 8 | Fill §6 DMJ — define, map, join | §6 filled 0→1 | Mechanic |
| 9 | Fill §7 C&V — universal constants + domain variables | §7 filled 0→1 | Mechanic |
| 10 | Fill §8-§14 — stops, verification, analytics, trace, logbook, fleet, session | Remaining sections 0→1 | Mechanic |
| 11 | DMJ into D1 fce table | D1 row inserted | wrangler D1 execute |
| 12 | LBB session log ingest | LBB record created | LBB Worker |
| 13 | Codex audit | PASS or FAIL with gap classification | Codex (auditor) |

**Output:**
- 14-section FCE Book (Library artifact, BS Law conformant)
- D1 `fce` table row (domain_id = FCE-NNN)
- LBB record (subject: processes)
- Codex PASS verdict (or FAIL with classified gaps)

**Circle:**
Codex PASS → ORBT transitions BUILD → OPERATE. Monthly cron triggers re-pull of sources → US/UP re-run → sigma check → gaps trigger REPAIR cycle → Codex re-audit → sigma tightens or TROUBLESHOOT_TRAIN on Strike 3.

---

## §5 DATA SCHEMA / OSAM

**READ:**
- `atlas/FCE_FILL_INSTRUCTIONS.md` — fill rules for all 14 sections (canonical, never duplicated here)
- `atlas/constants/FCE.md` — four-columns doctrine
- `atlas/constants/UNIFIED_TEMPLATE.md` — 14-section skeleton
- D1 `fce` table — existing FCE registrations (to assign next FCE-NNN)

**WRITE:**
- D1 `fce` table — new FCE-NNN row after Codex PASS
- D1 `fce_error` table — on any failed ingestion
- LBB `lbb_records` — session log (subject: processes)

**Process Composition:**
K=C (vocabulary lock) → DMJ (Define: key all elements → Map: source-to-column → Join: source_id through fce_source_mapping to domain/cell)

**Join Chain:**
`source_id` → `fce_source_mapping` → `fce_domains.domain_id` (FCE-NNN) → `fce_cells.column_id` (1-4)

**Forbidden:**
- Do NOT modify locked constants (#3, #6, #11) during a build
- Do NOT skip the K=C vocabulary lock step — columns are the ceiling, not suggestions
- Do NOT create FCE content in R2 without wiping after (R2 = whiteboard only)
- Do NOT duplicate prose from `FCE_FILL_INSTRUCTIONS.md` into domain FCE Books — cross-reference only

**Query Routing:**
- FCE registration lookup: `SELECT * FROM fce_domains WHERE domain_id = 'FCE-NNN'`
- Next FCE-NNN: `SELECT MAX(domain_id) FROM fce_domains`
- Source mapping: `SELECT * FROM fce_source_mapping WHERE domain_id = 'FCE-NNN'`

---

## §6 DMJ

**DEFINE (K=C vocabulary lock — FCE four-columns ceiling):**

| Element | ID | Format | C or V |
|---------|-----|--------|--------|
| Four columns | COL-1..4 | column_id integer | C (LOCKED — Valuation/Concentration/Trend/Liquidity) |
| Domain | FCE-NNN | text | C (once declared, never reassigned) |
| Fill spec reference | DOC-FCE-FILL | pointer | C (canonical source only) |
| Source list | SRC-NNN | text + URL | C (list structure) / V (per-domain content) |
| Categories (30K) | CAT-NNN | text per column | V → C (after US run locks them) |
| Metrics (10K) | MET-NNN | text per category | V → C (after UP run locks them) |
| Thresholds | THR-NNN | numeric | V (human-set per build) |

**MAP:**

| Source | Target | Transform |
|--------|--------|-----------|
| Domain declaration | `fce_domains.domain_id` | Assign FCE-NNN |
| Fill spec §5 four-columns table | `fce_cells.column_id` | Map 1:1 (COL-1..4) |
| Source URLs | `fce_sources.source_id` | SRC-NNN registration |
| US/UP output (categories, metrics) | `fce_cells.cell_content` | Lock after cross-source comparison |

**JOIN:**

Every domain FCE joins to the spine through:
- `fce_domains.domain_id` (FCE-NNN) — trunk join
- `fce_source_mapping.source_id` → `fce_domains.domain_id` — many-to-many source join
- `fce_cells.column_id` (1-4) — column join (four-columns ceiling is invariant)

---

## §7 CONSTANTS & VARIABLES

**Constants (same for every FCE build run):**
- Fill spec location: `imo-creator-v2/atlas/FCE_FILL_INSTRUCTIONS.md`
- Four columns: Valuation (Thing), Concentration (Flow), Trend (Change), Liquidity (Connection)
- 14-section UNIFIED_TEMPLATE skeleton
- D1 table names: `fce_domains`, `fce_cells`, `fce_sources`, `fce_source_mapping`, `fce_error`, `fce_logbook`
- CQRS: one canonical (fce_domains + fce_cells), one error (fce_error)
- Auditor: Codex (different engine than mechanic — Aviation Model invariant)
- Strike ladder: Strike 1 → repair → re-audit; Strike 2 → Opus mechanic; Strike 3 → TROUBLESHOOT_TRAIN

**Variables (changes per build run):**
- Which domain (FCE-NNN assigned sequentially)
- Which sources (operator seeds, engine expands)
- Categories and metrics (discovered by US/UP engine)
- Domain-specific constants (what survived cross-source comparison)
- Thresholds (human-set per column metric)
- Budget ceiling (human-set per run)

---

## §8 STOP CONDITIONS / KILL SWITCH

**Universal stops (same every FCE build):**

| Condition | Action |
|-----------|--------|
| No domain declared | HALT — ask operator for domain name and business intent |
| No sources identified | HALT — operator must seed at least 1 source to start |
| Fill spec not found at canonical path | HALT — check imo-creator-v2/atlas/FCE_FILL_INSTRUCTIONS.md |
| Any locked constant modified during build | HALT + Strike logged — locked constants are human-only |
| Codex FAIL with unclassified gaps | HALT — classify every gap before re-dispatching |
| Strike 3 on same failure mode | TROUBLESHOOT_TRAIN → Airworthiness Directive (fleet-wide fix) |
| Budget exceeded | HALT — report to operator, do not continue |

**Kill Switch:**
```bash
# Stop an in-flight FCE build (wrangler D1 write):
# 1. Mark the in-flight FCE-NNN as HALT in fce_domains:
npx wrangler d1 execute research-library --remote \
  --command "UPDATE fce_domains SET orbt_state = 'HALT' WHERE domain_id = 'FCE-NNN'"

# 2. Log the halt in LBB:
curl -s -X POST "https://lbb.svg-outreach.workers.dev/ingest" \
  -H "Authorization: Bearer $LBB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"FCE-NNN halted","content":"Kill switch triggered","subject_id":"processes","orbt_mode":"REPAIR"}'
```

---

## §9 VERIFICATION

**Universal checks (same every FCE build):**

```
1. Is fill spec read from canonical path (imo-creator-v2/atlas/FCE_FILL_INSTRUCTIONS.md)? → expected: yes
2. Are all 14 UNIFIED_TEMPLATE sections present in the FCE Book? → expected: yes
3. Are all 4 FCE columns present in §5 DATA SCHEMA? → expected: yes
4. Are all FCE fill rule 0→1 tolerances at 1? → expected: yes
5. Is FCE-NNN unique and registered in D1 fce_domains? → expected: yes
6. Are locked constants (#3, #6, #11) unmodified? → expected: yes (git diff confirms)
7. Is Codex the auditor (different engine than mechanic)? → expected: yes
8. Is LBB session log ingested (subject: processes)? → expected: yes
```

**Three Primitives Check:**
1. **Thing:** Does the FCE Book exist as a Library artifact with valid HEIR and FCE-NNN?
2. **Flow:** Does data flow from domain declaration → fill → D1 → LBB → Codex audit?
3. **Change:** Does domain-specific fill transform correctly into the four-column structure?

**§9b Live Verification:** Deferred — populated after first FCE run + Codex PASS.

---

## §10 ANALYTICS

**10a. Metrics:**

| Metric | Unit | Baseline | Target | Tolerance |
|--------|------|----------|--------|-----------|
| FCE sections filled 0→1 | count/14 | 0 | 14 | = 14 |
| FCE columns present | count/4 | 0 | 4 | = 4 |
| D1 rows inserted | count | 0 | 1 (fce_domains) | >= 1 |
| LBB records created | count | 0 | 1 | = 1 |
| Codex audit result | PASS/FAIL | — | PASS | = PASS |
| Strikes on build | count | 0 | 0 | <= 2 (Strike 3 = TROUBLESHOOT_TRAIN) |

**10b. Sigma Tracking:**

| Metric | Run 1 | Run 2 | Run 3 | Trend | Action |
|--------|-------|-------|-------|-------|--------|
| Sections at 0→1 | — | — | — | PENDING | Establish baseline |
| Codex PASS rate | — | — | — | PENDING | Establish baseline |

**10c. ORBT Gate Rules:**

| From | To | Gate |
|------|-----|------|
| BUILD | OPERATE | All 14 sections at 1, D1 registered, LBB ingested, Codex PASS |
| OPERATE | REPAIR | Any section fill rule breaks, or monthly source refresh finds new constants |
| REPAIR | OPERATE | Fix applied, re-audit PASS, sigma tightening |
| Any (Strike 3) | TROUBLESHOOT_TRAIN | Fleet-wide fix → Airworthiness Directive |

---

## §11 EXECUTION TRACE

**During BUILD:** No traces yet.
**After first run:** Log each build step with operator, mechanic, auditor, and timestamps.

| Field | Format | Required |
|-------|--------|----------|
| trace_id | UUID | Yes |
| proc_id | PROC-080 | Yes |
| fce_id | FCE-NNN | Yes |
| step | DECLARE/K=C/FILL/DMJ/AUDIT/INGEST | Yes |
| mechanic | agent name | Yes |
| auditor | Codex | Yes |
| result | PASS / FAIL / HALT | Yes |
| timestamp | ISO-8601 | Yes |

---

## §12 LOGBOOK

**No logbook during BUILD.** Created when Codex issues PASS verdict on the first complete FCE build run through this process.

Birth certificate will include: PROC-080 HEIR, ORBT transition (BUILD → OPERATE), all 8 verification checks at PASS, Codex auditor signature, date.

**0 → 1 when:** Codex certifies the first FCE Book produced by this runbook. Not before.

---

## §13 FLEET FAILURE REGISTRY

| Pattern ID | Location | Error Code | First Seen | Occurrences | Strike Count | Status |
|-----------|----------|-----------|-----------|-------------|-------------|--------|
| — | — | — | — | — | 0 | — |

Table present. Empty during initial BUILD. Populated on first Strike.

---

## §14 SESSION LOG

| Date | What Was Done | LBB Record |
|------|---------------|-----------|
| 2026-05-04 | PROC-080 created. FCE-fill operator runbook added as slot 080 under imo-creator. Mirrors canonical fill spec in imo-creator-v2/atlas/ without duplicating prose. Two commits: imo-engine-vault (mirror) + Barton-Processes (this runbook). | pending |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-05-04 |
| Last Modified | 2026-05-04 |
| Version | 1.0.0 |
| Template Version | UNIFIED_TEMPLATE.md v1.0.0 |
| Species | UT-Body |
| US Validated | pending |
| Governing Spec | `imo-creator-v2/atlas/FCE_FILL_INSTRUCTIONS.md` |
| Locked Constants | FCE.md (#3), UNIFIED_TEMPLATE.md (#6), UT_CHECKLIST.md (#11) |

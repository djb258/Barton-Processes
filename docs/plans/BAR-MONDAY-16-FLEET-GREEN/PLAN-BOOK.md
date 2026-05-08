---
species: Plan-Body
bar_id: BAR-MONDAY-16-FLEET-GREEN
sovereign_ref: barton-processes
version: "1.0.0"
last_modified: "2026-05-08"
created: "2026-05-08"
authority: Sovereign-authorized 2026-05-08 (Dave Barton, "get it all done")
planner_engine: opus-4.7
foreman_engine: opus-4.7
mechanic_engine: sonnet
auditor_engine: codex
outside:
  heir:
    sovereign_ref: barton-processes
    hub_id: bar-monday-16-fleet-green
    ctb_placement: branch
    ctb_node: barton-enterprises/svg-agency/bars/monday-16-fleet-green
    imo_topology: hub
    cc_layer: CC-01
    services: [opus-4.7, sonnet, codex, lbb, d1-mission-control, cf-workers]
    secrets_provider: doppler
    acceptance_criteria: |
      All 16 production processes pass Codex audit (P=1) against Atlas v2.3.0
      conformance gates: UT v2.8.0 14-section + UT_CHECKLIST v1.3.1 13-item +
      HEIR 8-field + ORBT 4-state + ctb_node on BE trunk + §9b mandatory gauge
      installed + 6D complete + workflow.yaml BS Law v1.3.0 Y-junction +
      v1.5.0 SHA256 parity + paired-artifacts.yaml registration. Cron fleet
      classified per process: recurring (wired in wrangler.toml [triggers])
      OR event-driven/manual (de-listed from cron_registry.yaml + stamped on UT).
      Every OPERATE-eligible process has fire-proof + LBB row per fire. Monday
      AM: live-fire verification confirms cron firing + LBB ingest per fire.
  orbt:
    library_state: BUILD
    last_indexed_at: "2026-05-08T00:00:00Z"
    indexed_by: opus-4.7-planner

inside:
  heir:
    process_id: bar.monday-16-fleet-green
    species: Plan-Body
    version: "1.0.0"
    last_modified: "2026-05-08"
    companion_manifest: docs/plans/BAR-MONDAY-16-FLEET-GREEN/plan-book.yaml
  orbt:
    library_state: BUILD
---

# PLAN BOOK — BAR-MONDAY-16-FLEET-GREEN

## §1 Identity

**BAR:** BAR-MONDAY-16-FLEET-GREEN
**Sovereign:** Dave Barton (authorized 2026-05-08 — "get it all done")
**Planner:** Opus 4.7 (this Plan Book)
**Foreman:** Opus 4.7 (dispatches mechanics, never fixes)
**Mechanics:** Sonnet (per-process work, parallel batches of 4, run_in_background=true)
**Auditor:** Codex (P=1 / P=0 verdict per process; never fixes)

**Scope:** 16 production processes wired to Mission Control `system.processes` shelf (per BAR-MC-WIRE-16, 2026-05-07).

**Target:** Monday 2026-05-11 — every process audited GREEN, paired in `paired-artifacts.yaml`, gauges installed per Atlas §1.6, cron status definitively classified, OPERATE-eligible processes firing on schedule with per-fire LBB rows.

**ctb_node:** `barton-enterprises/svg-agency/bars/monday-16-fleet-green`

## §2 Purpose / PRD

### Why this BAR exists

Atlas was significantly updated to v2.3.0 (2026-05-08, sovereign self-audit). New hard gates apply to every Library artifact:

1. **§1.6 Mandatory Gauge** — every process must install at least one gauge (UT §9b) before BUILD → OPERATE transition. Auditor blocks promotion if §9b is empty.
2. **§1.6 Six Dimensions completeness** — WHO/WHAT/WHEN/WHERE/WHY/HOW must all be answered.
3. **§7.3a Paired Library Artifacts** — every `.md` + `.yaml` pair must be registered in `paired-artifacts.yaml` with SHA256 parity zone enforcement.
4. **BS Law v1.5.0** — universal paired-artifact pattern with parity-zone CI gate.
5. **Determinism-first §1.3.4** — AI never on the spine (locked).

The 16 production processes existed before these gates were locked. The fleet is in a mixed conformance state:
- 0 OPERATE
- 2 REPAIR (bp.100, bp.200)
- 1 BUILD (bp.820)
- 12 PROPOSED (registered in cron registry, no `[triggers]` block in wrangler.toml)
- 1 RETIRED (bp.600)

This BAR brings the entire 16-process fleet into Atlas v2.3.0 conformance and definitive cron classification by Monday.

### Out of scope

- **mc-api.routines AI-on-spine RED finding** — separate BAR (sovereign decision required on whether AI banned only as scheduler, or also from being invoked by cron). Tracked in BAR-375. Does not block this sweep.
- **ProcessShelf.tsx UI render** — separate BAR (BAR-MC-WIRE-16 noted UI is pending).
- **Trunk restructure (real estate / personal finance branches)** — sovereign deferred 2026-05-08.

### Success metric

Codex audit verdict P=1 across all 16 processes by Monday 2026-05-11 09:00 UTC. Live-fire verification confirms cron firing + LBB row per fire on every OPERATE-eligible process.

## §3 Component Status

### The 16 production processes (current state)

| # | Process | Path | UT | YAML | wrangler | triggers | Cron Reg ORBT | Conformance Gap |
|---|---|---|---|---|---|---|---|---|
| 1 | bp.010 seed-d1 | `factory/outreach/010-seed-d1/` | ✓ | ✓ | ✗ | ✗ | PROPOSED | wrangler+triggers OR de-list |
| 2 | bp.100 lcs-pipeline | `factory/cl/100-lcs-pipeline/` | ✓ | ✓ | ✓ | ✓ | REPAIR | gauge install + fire-proof + LBB row |
| 3 | bp.200 people-worker | `factory/outreach/200-people-worker/` | ✓ | ✓ | ✓ | ✓ | REPAIR | gauge install + fire-proof + LBB row |
| 4 | bp.201 email-discovery | `factory/outreach/201-email-discovery/` | ✓ | ✓ | ✗ | ✗ | PROPOSED | wrangler+triggers OR de-list |
| 5 | bp.202 linkedin-discovery | `factory/outreach/202-linkedin-discovery/` | ✓ | ✓ | ✗ | ✗ | PROPOSED | wrangler+triggers OR de-list |
| 6 | bp.300 blog-worker | `factory/outreach/300-blog-worker/` | ✓ | ✓ | ✗ | ✗ | PROPOSED | wrangler+triggers OR de-list |
| 7 | bp.301 page-parser | `factory/outreach/301-page-parser/` | ✓ | ✓ | ✗ | ✗ | PROPOSED | wrangler+triggers OR de-list |
| 8 | bp.400 dol-views | `factory/outreach/400-dol-views/` | ✓ | ✓ | ✗ | ✗ | PROPOSED | wrangler+triggers OR de-list |
| 9 | bp.500 talent-flow | `factory/outreach/500-talent-flow/` | ✓ | ✓ | ✗ | ✗ | PROPOSED | wrangler+triggers OR de-list |
| 10 | bp.600 bit-scoring | `factory/outreach/600-bit-scoring/` | ✓ | ✓ | ✗ | ✗ | RETIRED | RETIRED stamp confirm |
| 11 | bp.700 campaign-engine | `factory/outreach/700-campaign-engine/` | ✓ | ✓ | ✗ | ✗ | PROPOSED | wrangler+triggers OR de-list |
| 12 | bp.800 client-mint | `factory/cl/800-client-mint/` | ✓ | ✓ | ✓ | ✗ | PROPOSED | triggers OR de-list |
| 13 | bp.810 client-intake | `factory/client/810-client-intake/` | ✓ | ✓ | ✓ | ✗ | PROPOSED | triggers OR de-list |
| 14 | bp.820 vendor-export | `factory/client/820-vendor-export/` | ✓ | ✓ | ✓ | ✓ | BUILD | gauge install + fire-proof + LBB row → OPERATE |
| 15 | bp.830 client-portal | `factory/client/830-client-portal/` | ✓ | ✓ | ✓ | ✗ | PROPOSED | triggers OR de-list |
| 16 | bp.900 sales-portal | `factory/sales/900-sales-portal/` | ✓ | ✓ | ✓ | ✗ | PROPOSED | triggers OR de-list |

### Common conformance checks (apply to all 16)

| Check | Doctrine | Verifier |
|---|---|---|
| UT v2.8.0 14 sections present | UNIFIED_TEMPLATE.md | Codex grep §1..§14 |
| UT_CHECKLIST v1.3.1 13-item pre-flight | UT_CHECKLIST.md | Codex grep checklist table |
| HEIR 8 fields populated | Atlas §1.5.2 | Codex YAML parse |
| ORBT 4-state stamped | Sovereign Decision A 2026-05-08 | Codex enum check |
| ctb_node on BE trunk | BARTON_ENTERPRISES_CTB.md | Codex path validation |
| §9b Mandatory Gauge installed | Atlas §1.6 (NEW) | Codex non-empty + typology match |
| 6D complete (WHO/WHAT/WHEN/WHERE/WHY/HOW) | Atlas §1.6 | Codex 6-dimension scan |
| §14 Logbook append-only | Atlas governance | Codex history table check |
| BS Law v1.3.0 Y-junction syntactic separation | BS_LAW.md | Codex YAML AST parse |
| Book Law v1.5.0 Workflow-Body 11 blocks | BOOK_LAW.md | Codex block enumeration |
| BS Law v1.5.0 SHA256 parity zone | BS_LAW.md | `scripts/atlas-pair-verify.sh` |
| Registered in `paired-artifacts.yaml` | Atlas §7.3a | Codex grep artifact_id |

## §4 P=1 Definition

P=1 for this BAR when ALL of the following hold:

1. **Per-process conformance:** all 12 common checks pass for each of the 16 (Codex returns PASS per process).
2. **Cron classification:** every PROPOSED status definitively resolved — either wired (`[triggers]` block + `wrangler deployments list` shows fired) or de-listed from `cron_registry.yaml` (with UT §10 stamp marking event-driven/manual).
3. **Gauge installation:** every process has at least one operational gauge in §9b. CF Worker → health check + cron heartbeat. Worker without cron → health check + invocation log. Pipeline step → throughput. D1 table dependency → row count + freshness.
4. **Paired-artifact registration:** all 16 + master Plan Book registered in `paired-artifacts.yaml` (pairs #12-28). Atlas §7.3a updated via `pending-atlas-updates/` queue (sovereign drains).
5. **Live-fire on OPERATE-eligible:** Monday AM verification — for every process now in OPERATE, `wrangler deployments list` shows recent fire AND LBB has row per fire (matching `cron_registry.yaml` schedule).
6. **bp.600 RETIRED stamped:** UT carries explicit `RETIRED` ORBT, no `[triggers]`, removed from active fleet view.
7. **Master Plan Book + companion YAML conform to BS Law v1.5.0:** SHA256 parity zone matches across this `.md` + `plan-book.yaml`.

P=0 if any check fails. Diagnostic vector r(x) reports which gate(s) failed and per-process severity.

## §5 OSAM (Outside / Surface / Architecture / Movement)

### READ
- `atlas/ATLAS.md` v2.3.0 — every conformance gate sources here
- `atlas/constants/UNIFIED_TEMPLATE.md` v2.8.0 — UT format
- `atlas/constants/UT_CHECKLIST.md` v1.3.1 — 13-item pre-flight
- `atlas/constants/BS_LAW.md` v1.4.0 — Y-junction + parity zone
- `atlas/constants/BOOK_LAW.md` v1.5.0 — Workflow-Body 11 blocks
- `atlas/constants/BARTON_ENTERPRISES_CTB.md` — trunk
- `Barton-Processes/factory/governance/050-cron-registry/cron_registry.yaml` — current cron state
- 16 × `factory/<branch>/<NNN>-*/PROCESS-UT.md` (existing UTs)
- 16 × `factory/<branch>/<NNN>-*/workflow.yaml` (existing YAMLs)

### WRITE
- 16 × PROCESS-UT.md amendments (conformance fixes)
- 16 × workflow.yaml amendments (parity + Y-junction)
- 1 × `imo-creator-v2/atlas/manifests/paired-artifacts.yaml` append (17 entries: master + 16)
- 16 × wrangler.toml `[triggers]` adds OR removes (per Sonnet classification dispatch)
- `Barton-Processes/factory/governance/050-cron-registry/cron_registry.yaml` updates
- N × `imo-creator-v2/pending-atlas-updates/BAR-NNN.yaml` queue entries (Atlas §7.3a + §14 updates)
- LBB ingest rows per audit certification

### Join Chain
`bar-monday-16-fleet-green` → JOIN on `process_id` → 16 individual processes → JOIN on `ctb_node` → BE trunk

### Forbidden Paths
- ❌ Sonnet flips Codex verdict (memory: Auditor decides PASS/FAIL)
- ❌ Foreman fixes code (memory: Foreman never fixes; Codex/Sonnet repair)
- ❌ Direct edit of any locked Atlas constant (sovereign-only — queue via `pending-atlas-updates/`)
- ❌ AI on schedule spine (Atlas §1.3.4 + BAR-375)
- ❌ Foreground mechanic dispatch (memory: Run Sonnet in Background — `run_in_background=true`)

### Query Routing
- Audit verdict → Codex (read-only, JSON output)
- Code fix → Sonnet (parallel batches of 4)
- Atlas amendment → queue in `pending-atlas-updates/` for sovereign drain
- LBB ingest → `scripts/lbb-log.sh` after every certification

### Process Composition
US (discover gaps via Codex baseline) → K=C (verify each gap names a real Atlas check) → DMJ (map gap to fix-target) → UP (Sonnet executes; Codex certifies; LBB logs)

## §6 Dispatch Sequence

### Friday 2026-05-08 (today)

1. **Author master Plan Book + plan-book.yaml** ← THIS WORK ORDER (Opus 4.7)
2. **Append registry entries to `paired-artifacts.yaml`** — master Plan Book + 16 process pairs
3. **Queue `pending-atlas-updates/`** — §7.3a append + §14 logbook entry + ORBT 4-state Atlas drift fix (separate BAR for sovereign)
4. **Commit + push** Plan Book + registry to master (both repos)
5. **Dispatch Codex baseline audit** (read-only, run_in_background=true) — produces `MECHANIC-INPUT-GAPS.md` per process

### Saturday 2026-05-09

6. **Sonnet batch 1** (run_in_background=true): bp.010, bp.100, bp.200, bp.201 — UT/YAML conformance + gauge install
7. **Sonnet batch 2** (parallel with batch 1): bp.202, bp.300, bp.301, bp.400
8. **Codex audits batch 1** as it lands → certify or strike
9. **Sovereign cron classification call** for each PROPOSED — Dave decides recurring vs event-driven (foreman compiles a single decision sheet)
10. **Sonnet batch 3:** bp.500, bp.600 (RETIRED stamp), bp.700, bp.800
11. **Sonnet batch 4:** bp.810, bp.820, bp.830, bp.900

### Sunday 2026-05-10

12. **Codex re-audit** of any Strike-1 repairs from Saturday
13. **Wire `[triggers]` blocks** for processes Dave classified as recurring
14. **De-list from `cron_registry.yaml`** for processes Dave classified as event-driven; UT §10 stamped accordingly
15. **Deploy any new wrangler triggers** — `wrangler deploy` per worker
16. **Final Codex sweep** — all 16 processes → P=1

### Monday 2026-05-11 AM

17. **Live-fire verification** — `wrangler cron triggers list` per active worker; LBB row per fire confirmed; gauges reading green
18. **Promote BUILD/REPAIR → OPERATE** for processes that pass live-fire
19. **LBB ingest final BAR closure** — record_id stamped, ORBT BUILD → OPERATE on this BAR
20. **Sovereign sign-off** — Dave reviews close-state and certifies BAR done

## §7 Dependencies

- **Atlas v2.3.0** locked 2026-05-08 — defines all conformance gates this BAR enforces
- **Cron registry** at `factory/governance/050-cron-registry/cron_registry.yaml` — single source of truth for cron state
- **paired-artifacts.yaml** at `imo-creator-v2/atlas/manifests/paired-artifacts.yaml` — registry append target
- **`scripts/atlas-pair-verify.sh`** — SHA256 parity zone enforcement
- **`.github/workflows/atlas-audit.yml`** — CI gate on parity (blocks merge on FAIL)
- **LBB worker** at `https://lbb.svg-outreach.workers.dev` — every audit certification ingests
- **`scripts/lbb-log.sh`** — bash CLI for LBB ingest

## §8 Risk

| Risk | Mitigation |
|---|---|
| Sovereign classification call delayed (12 PROPOSED need ruling) | Foreman compiles single decision sheet for Dave; one batch reply unblocks all 12 |
| Sonnet rate limit during batches | Batch size 4, parallel; sequential fallback if rate-limited (memory: 16-process conformance pass survived rate-limit on prior sweep via batch staging) |
| Codex Strike-2 on a process | Escalate to Opus 4.7 mechanic per Four-Brain doctrine; do NOT have Sonnet retry without root-cause diagnosis |
| Atlas §1.5.3 ORBT 6-state vs 4-state drift contaminates UTs | Mechanics use 4-state per sovereign call 2026-05-08; Atlas drift queued as separate BAR; UTs reference 4-state with `<!-- atlas-drift: §1.5.3 still says 6 -->` comment |
| paired-artifact parity zone fails CI on bulk register | Append registry entries first as a single commit; verify locally with `scripts/atlas-pair-verify.sh` before push |
| mc-api.routines AI-on-spine RED bleeds into this BAR | Out of scope — explicitly carved out in §2; tracked in BAR-375 |

## §9 Operations / Schedule

This is a one-shot BAR (not recurring). No cron registration. ORBT lifecycle: BUILD → OPERATE (only when all 16 process certifications close + Monday live-fire verifies).

### §9b Live Verification (master Plan Book gauges)

| Gauge | Query | Expected (P=1) | Trigger if RED |
|---|---|---|---|
| Process certification count | `SELECT COUNT(*) FROM lbb_records WHERE source_url='BAR-MONDAY-16-FLEET-GREEN' AND tags LIKE '%CERTIFY%'` | 16 by Monday 09:00 UTC | Foreman re-dispatches missing process to Sonnet |
| Cron firing count (OPERATE only) | `wrangler cron triggers list` per worker | matches `cron_registry.yaml` schedule | REPAIR mode flip; Sonnet diagnoses |
| LBB row-per-fire | `SELECT COUNT(*) FROM lbb_records WHERE subject_id IN (...) AND found_at > now()-interval` | ≥ 1 per scheduled fire interval | Worker scheduler missing LBB ingest call |
| Parity zone CI | `.github/workflows/atlas-audit.yml` PR status | PASS on bulk-register PR | Mechanic retries with corrected SHA256 manifest |

## §10 Operations Block (cron status post-sweep)

Populated per process at completion. Each of the 16 will end up in one of these terminal states:

| Terminal State | What it means |
|---|---|
| OPERATE-recurring | wrangler.toml `[triggers]` set, cron registry has the entry, fire-proof + LBB row confirmed |
| OPERATE-event-driven | No cron, UT §10 stamped "event-driven (HTTP / queue / webhook)", removed from active cron registry |
| BUILD | Worker not yet deployed; UT exists, paired YAML exists, but no live invocation |
| RETIRED | Explicit RETIRED stamp on UT (only bp.600 today) |
| DISABLED | Temporarily off; cite the BAR that disabled it |

## §11 Test Plan

### Per-process audit (Codex)
- Input: `PROCESS-UT.md` + `workflow.yaml` pair
- Expected: P=1 across 12 conformance gates
- On FAIL: gap delta written to `MECHANIC-INPUT-GAPS-bp-NNN.md`

### Bulk parity zone (CI)
- Input: 17 new entries in `paired-artifacts.yaml` (master + 16) + corresponding `.md`/`.yaml` pairs
- Expected: `scripts/atlas-pair-verify.sh` PASS on all 17
- On FAIL: SHA256 mismatch listed; Sonnet repairs parity-zone fields and re-pushes

### Live-fire (Monday AM)
- Input: each OPERATE-eligible worker
- Expected: `wrangler cron triggers list` shows recent fire; LBB row per fire
- On FAIL: REPAIR mode flip; Sonnet diagnoses (missing LBB ingest call vs cron not firing vs misconfigured trigger)

## §12 Vocabulary (legend extension — local terms only)

This BAR introduces no new vocabulary. All terms inherited from Atlas v2.3.0 §1 Legend.

## §13 References

- `atlas/ATLAS.md` v2.3.0
- `atlas/constants/UNIFIED_TEMPLATE.md` v2.8.0
- `atlas/constants/UT_CHECKLIST.md` v1.3.1
- `atlas/constants/BS_LAW.md` v1.4.0
- `atlas/constants/BOOK_LAW.md` v1.5.0
- `atlas/constants/BARTON_ENTERPRISES_CTB.md`
- `atlas/constants/FOUR_BRAIN_AVIATION.md` v1.2.0
- `atlas/manifests/paired-artifacts.yaml` v1.2.0
- `Barton-Processes/factory/governance/050-cron-registry/cron_registry.yaml` v1.0.1-live-index
- BAR-375 (cron firing verification — separate scope, does not block)
- BAR-MC-WIRE-16 (16 processes wired to MC `system.processes` shelf, 2026-05-07)
- LBB record `078abc13-a796-4b38-91c7-b6977a1b8c36` (BAR-MC-WIRE-16 ingest)

## §14 Maintenance Logbook

| Date | Version | Author | Action | Scope |
|---|---|---|---|---|
| 2026-05-08 | v1.0.0 | Opus 4.7 Planner | `CREATE` — initial Plan Book authored under sovereign authorization "get it all done" 2026-05-08. 16 processes scoped, conformance gates enumerated against Atlas v2.3.0, dispatch sequence Friday→Monday committed. mc-api.routines AI-on-spine and ProcessShelf.tsx UI explicitly out of scope. | Full Plan Book initial draft |

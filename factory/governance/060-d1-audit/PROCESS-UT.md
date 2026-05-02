# D1 Audit (Process 060-d1-audit)
## Periodic introspection of the 6 active D1 databases — schema drift, stale tables, orphan tables, index health, row-count baselines. The eyes for the data layer.
### Status: BUILD
### Medium: process
### Business: imo-creator (cross-cutting governance)

---

## §1 Identity

| Field | Value |
|-------|-------|
| Process ID | PROC-060-D1-AUDIT |
| Name | D1 Audit |
| Medium | process |
| Business Silo | imo-creator (cross-cutting governance) |
| CTB Position | barton-enterprises → imo-creator → governance → 060-d1-audit (LEAF) |
| ctb_node | `barton-enterprises/imo-creator/governance/d1-audit` |
| ORBT | BUILD |
| Strikes | 0 |
| Authority | Sovereign (imo-creator-v2) |
| Owner | Dave Barton |
| Last Modified | 2026-05-02 |
| Sister Process | bp.050-cron-registry (governance sibling) |
| Parent Plan | docs/plans/PLAN-MASTER-16-PROCESSES-FIX.md (in imo-creator-v2) |

### §1b Geometry

**CTB:** trunk (Barton Enterprises) → branch (imo-creator) → branch (governance) → leaf (060-d1-audit)
**Hub-Spoke:** **Hub** — runs introspection across all D1s; spokes are the wrangler CLI per database. Rim-in: scheduled trigger. Rim-out: audit reports + drift squawks.
**Altitude:** 30k tactical — the audit sits above per-process D1 reads/writes; below the strategy doctrine.

---

## §2 PRD

**WHAT:** Periodic live introspection of the 6 active D1 databases (svg-d1-spine, svg-d1-outreach-ops, imo-d1-global, svg-d1-storage, lbb, mission-control). For each DB, report: table inventory + row counts + last-write timestamps + schema drift vs `D1_DATA_DICTIONARY.md` + stale tables (no writes in 30 days) + orphan tables (no process consumes) + index health on hot queries.

**WHY:** `D1_DATA_DICTIONARY.md` authority date is 2026-03-31 — drift over 32+ days is plausible. No "last-write timestamp per table" inventory exists today. Without periodic D1 audit, schema drift compounds invisibly, stale tables waste storage, orphan tables create confusion, missing indexes silently degrade performance.

**WHO:**
- **Owner:** Dave Barton (sovereign sign-off on schema migrations / table retirements)
- **Mechanic:** Sonnet (introspection + report generation)
- **Auditor:** Codex (verifies every claim resolves to live D1 + dictionary diff is accurate)

**SCOPE (in):**
1. Per-DB introspection script (deterministic — `wrangler d1 execute` queries)
2. `D1_AUDIT_REPORT.md` — generated artifact, refreshed each fire
3. Drift events → LBB log + mission-control squawk
4. Schema-migration recommendation (does NOT execute — recommends only)
5. Stale-table flagging (does NOT retire — flags for sovereign review)
6. Index health: `EXPLAIN QUERY PLAN` for each process's known queries; flag missing indexes

**SCOPE (out):**
- Modifying any D1 schema directly (audit recommends; sovereign + Mechanic execute via separate BAR)
- Retiring any D1 table (sovereign sign-off required, see 2026-03-31 retirement of 12 DBs as precedent)
- Per-process data quality (handled by per-process audit cycle in PLAN-GAME-PLAN)

**SUCCESS METRIC:**
- Single canonical `D1_AUDIT_REPORT.md` regenerated on every fire
- 0 schema drift after each Mechanic-executed migration
- Codex audit confirms every claim resolves to live D1 introspection
- Stale-table list ≤5 (active fleet stays tight)

---

## §3 Components / Status

| Component | Status | Notes |
|-----------|--------|-------|
| `D1_AUDIT_REPORT.md` | BUILD (skeleton this session) | Lives at `factory/governance/060-d1-audit/D1_AUDIT_REPORT.md` (to be created Monday by Mechanic on first fire) |
| Introspection script | BUILD (commands embedded below) | Runs via `wrangler d1 execute` per DB |
| `D1_DATA_DICTIONARY.md` | OPERATE (parent reference, authority 2026-03-31) | This audit refreshes the dictionary's authority date on each clean fire |
| Mission Control D1 panel | TBD | Wires up post per-process GREEN |
| LBB subject_id `system` | OPERATE | Audit metadata destination |

### §3d BARs Referenced
- BAR-375 (fleet-wide cron firing — sister)
- (D1 Audit init BAR — to file Sunday)

### §3e LBB Subjects Fed
- `system` — audit reports + drift events
- `processes` — per-process schema health (when audit findings are scoped to one process)

---

## §4 IMO

| I — Input | M — Middle | O — Output |
|-----------|------------|------------|
| **Source:** 6 active D1 databases via `wrangler d1 execute` CLI; `D1_DATA_DICTIONARY.md` for diff baseline | **Transformation:** introspect schema (`SELECT name FROM sqlite_master`) + row counts + last-write timestamps + stale flags + orphan flags + index health (EXPLAIN QUERY PLAN) per DB | **Writes:** `D1_AUDIT_REPORT.md` (per-DB section refreshed each fire) + LBB log of drift events + squawks on RED severity |
| **Trigger:** weekly cron (proposed `0 5 * * 0` Sunday 5am UTC) — runs after weekly cron-registry drift check | **Doctrine:** introspection is read-only; audit recommends, never executes schema migrations; stale flags require sovereign sign-off before retirement | **Downstream:** per-process audit cycle (Stage 2 introspection) reuses these queries; sovereign reads report for migration decisions |
| **Boundary:** wrangler authenticated to all 6 DBs; Doppler-stored CF API token healthy | **Stop:** introspection error rate >5% (D1 unreachable); schema drift > 20% (suspect catastrophic change, halt for sovereign) | **Squawk:** drift > 10% → ORANGE; drift > 20% → RED with halt; D1 unreachable → RED |

---

## §5 OSAM

**READ:**
- All 6 active D1 databases (introspection only)
- `D1_DATA_DICTIONARY.md` (baseline reference)
- `cron_registry.yaml` (which processes own which tables)

**WRITE:**
- `factory/governance/060-d1-audit/D1_AUDIT_REPORT.md` (canonical output)
- LBB rows on drift events (subject_id=`system`)
- mission-control squawks on severity ORANGE/RED

**Forbidden:**
- ❌ Modifying any D1 schema directly (recommend, don't execute)
- ❌ Dropping any table (sovereign sign-off required)
- ❌ Re-creating `D1_DATA_DICTIONARY.md` from scratch (refresh-in-place; preserve authority history)

**Query Routing:**
- "What's in DB X?" → live wrangler introspection (the audit's primary function)
- "Has DB X drifted from doctrine?" → diff live vs `D1_DATA_DICTIONARY.md`
- "Which process owns table T?" → cross-reference with `cron_registry.yaml` + per-process Plan Books

---

## §6 Locked Rules (D-060-XX) — see DOCTRINE.md (sibling, to be created)

Quick summary:
- D-060-01: Audit is read-only; introspection MUST NOT modify D1 state
- D-060-02: Schema drift detected → recommend migration BAR; never auto-execute
- D-060-03: Stale tables flagged → require sovereign sign-off before retirement
- D-060-04: Live introspection refreshes `D1_DATA_DICTIONARY.md` authority date on clean fire (no drift)
- D-060-05: Index recommendations include `EXPLAIN QUERY PLAN` evidence per query
- D-060-06: Audit cron is itself registered in `cron_registry.yaml`

---

## §7 Live Introspection (Mechanic dispatch — runs on every fire)

```bash
# Per-DB inventory (one block per DB)
for DB in svg-d1-spine svg-d1-outreach-ops imo-d1-global svg-d1-storage lbb mission-control; do
  echo "=== $DB ==="

  # Table list + row counts
  wrangler d1 execute $DB --command "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
  wrangler d1 execute $DB --command "SELECT name, (SELECT COUNT(*) FROM '|| name ||') AS rows FROM sqlite_master WHERE type='table' ORDER BY name"

  # Last-write timestamp per table (where updated_at exists)
  # Mechanic generates per-table query from schema introspection; pseudocode:
  # for each table T with updated_at column:
  #   wrangler d1 execute $DB --command "SELECT MAX(updated_at) FROM $T"

  # Schema dump
  wrangler d1 execute $DB --command "SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name"
done
```

**Drift detection:**
- Diff each table's live schema vs `D1_DATA_DICTIONARY.md` declared schema
- Flag: column added (drift), column removed (drift), column renamed (drift), column type changed (RED — schema migration evidence)

**Stale detection:**
- Any table with `MAX(updated_at) < now() - 30 days` → STALE
- Any table NOT referenced by any process per `cron_registry.yaml` cross-ref → ORPHAN

**Index health:**
- For each process's hot query (per per-process Plan Book §3 introspection commands):
- `EXPLAIN QUERY PLAN <query>` → check for `SCAN TABLE` instead of `SEARCH TABLE USING INDEX`
- Flag missing indexes per query

---

## §8 Stop Conditions + Kill Switch

**Stop normally:** introspection completes across all 6 DBs; drift count tabulated; report regenerated; LBB log written.

**Hard HALT:**
- Any DB unreachable → RED squawk; do NOT generate partial report (incomplete = misleading)
- Drift > 20% in any DB → RED with halt; suspect catastrophic change; sovereign reviews
- AI-on-spine grep finds an LLM call inside the introspection script → halt (audit must be deterministic)

**Kill switch:** `wrangler triggers unschedule d1-audit-worker` (when worker exists).

---

## §9 Live Verification

**§9a Live Dashboard:** Mission Control / D1 panel (post-wiring)

**§9b Gauges:**
- Active DBs introspected: 6 (baseline)
- Drift count weekly: 0 (acceptable); ≥1 = squawk
- Stale tables count: ≤5 (target)
- Orphan tables count: 0 (target)
- Index recommendations open: trending down

---

## §10 Operations

**Schedule:** `0 5 * * 0` weekly Sunday 5am UTC (proposed — registers in `cron_registry.yaml` once Process 060 exits BUILD).

**Failure mode handling:**
- Drift detected → ORANGE squawk + LBB log + recommend migration BAR
- D1 unreachable → RED squawk + halt audit; sovereign decides retry vs deeper diagnosis
- Stale table flagged → LBB log; sovereign reviews monthly

---

## §11 Doctrine Cross-Reference

- `Barton-Processes/D1_DATA_DICTIONARY.md` (authoritative schema baseline)
- `imo-creator-v2/docs/plans/PLAN-MASTER-16-PROCESSES-FIX.md` (parent — D1 audit shape declared in §6)
- `imo-creator-v2/docs/plans/PLAN-GAME-PLAN.md` (consumer — Stage 2 of per-process audit cycle reuses these queries)

---

## §12 BARs Referenced

- BAR-375 (sister — fleet-wide cron firing)
- (D1 Audit init BAR — to file Sunday)
- Future: per-DB schema-migration BARs (filed by sovereign on drift findings)

---

## §13 Owner Contact

Dave Barton — sovereign authority on schema migrations + table retirements.

---

## §14 Maintenance Logbook

| Date | Author | Action | Reason |
|------|--------|--------|--------|
| 2026-05-02 | Opus 4.7 (Planner) | Stub created | Per game plan §12 deliverable #3. D1 Audit process initialized in Barton-Processes governance silo (sibling of 050-cron-registry). Awaits Mechanic dispatch (Sunday) to run first introspection sweep + populate D1_AUDIT_REPORT.md. |

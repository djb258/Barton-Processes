# Cron Registry (Process 050-cron-registry)
## Single source of truth for every recurring cron across the Barton fleet — CF Worker cron triggers, GitHub Actions schedules, server crontabs. AI is NEVER the scheduler.
### Status: BUILD
### Medium: process
### Business: imo-creator (cross-cutting governance)

---

## UT Pre-Flight Checklist (13 items per law/UT_CHECKLIST.md v1.2.0)

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | [x] | §2 |
| 2 | OSAM — READ / WRITE / Process Composition / Join Chain / Forbidden Paths / Query Routing | [x] | §5 |
| 3 | Component Status — every dep with state | [x] | §3 |
| 4 | Owner — human who fixes this at 2 AM | [x] | §1 — Dave Barton |
| 5 | Live Dashboard — URL or N/A | [x] | §3 — Mission Control / cron panel |
| 6 | Kill Switch | [x] | §8 |
| 7 | Logbook — last audit verdict + date | [ ] | §14 — BUILD, no logbook yet |
| 8 | FCEs Attached | [ ] | §3c — TBV |
| 9 | BARs Referenced | [x] | §3d |
| 10 | LBB Subjects Fed | [x] | §3e — `system`, `processes` |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | [x] | §1b |
| 12 | Live Verification — every numeric count, cron, URL grounded | [ ] | §9b — pending live registry population |
| 13 | ctb_node — declared on Barton Enterprises CTB trunk | [x] | §1 — `barton-enterprises/imo-creator/governance/cron-registry` |

---

## §1 Identity

| Field | Value |
|-------|-------|
| Process ID | PROC-050-CRON-REGISTRY |
| Name | Cron Registry |
| Medium | process |
| Business Silo | imo-creator (cross-cutting governance) |
| CTB Position | barton-enterprises → imo-creator → governance → 050-cron-registry (LEAF) |
| ctb_node | `barton-enterprises/imo-creator/governance/cron-registry` |
| ORBT | BUILD |
| Strikes | 0 |
| Authority | Sovereign (imo-creator-v2) |
| Owner | Dave Barton |
| Last Modified | 2026-05-02 |
| BAR Reference | (BAR-XXX to be filed Sunday — Cron Registry init) |
| Sister BARs | BAR-375 (fleet-wide cron firing verification) |
| Parent Plan | docs/plans/PLAN-MASTER-CRON-AUTOMATION.md (in imo-creator-v2) |

### §1b Geometry

**CTB Position:** trunk (Barton Enterprises) → branch (imo-creator) → branch (governance) → leaf (050-cron-registry)

**Hub-Spoke Role:** **Hub** for cron metadata. Spokes are the actual workers / actions / crontabs that fire. The registry tells you what's supposed to fire when; the spokes do the firing.

**Altitude:** 30k tactical — the registry sits above the leaves (per-process worker configs) but below the strategy doctrine (PLAN-MASTER-CRON-AUTOMATION).

---

## §2 PRD

**WHAT:** Single source of truth for every recurring cron across the Barton fleet. Every CF Worker `[triggers]` block, every GitHub Actions `schedule:`, every server crontab entry has a row in `cron_registry.yaml`. New crons cannot ship without a registry entry. Codex audits the registry against live state weekly.

**WHY:** Today the cron config is scattered across ~30 wrangler.toml files + workflows in various repos. No one document tells you what's running when. As of session 32 audit, 5 active CF Worker crons are running, ~10 wrangler.toml files have NO `[triggers]` block (gaps), and `lcs-fire-daily.sh` has no cron at all. Without a registry, gaps stay invisible and disabled crons re-enable silently.

**WHO:**
- **Owner:** Dave Barton (sovereign sign-off on registry changes)
- **Mechanic:** Sonnet (live introspection + drift fixes)
- **Auditor:** Codex (weekly drift check + AI-on-spine ban verification)

**SCOPE (in):**
1. `cron_registry.yaml` — machine-readable index of every cron
2. This `PROCESS-UT.md` — doctrine + operational rules
3. `DOCTRINE.md` (sibling) — locked rules (D-050-XX series)
4. CI gate — every PR touching a wrangler.toml `[triggers]` block must include a `cron_registry.yaml` diff
5. Weekly drift cron — verifies live state matches registry
6. Failure routing — drift detected → squawk to mission-control

**SCOPE (out):**
- The actual scheduling (CF Worker / GH Action / crontab does that)
- Per-process build/repair (handled by per-process Plan Books + BARs)
- The Dyno engine's internal cron (engine sealed)

**SUCCESS METRIC:** Every cron in the fleet is a row in `cron_registry.yaml`; weekly drift check returns 0 drift; Codex AI-on-spine grep returns 0 hits across all registered crons.

---

## §3 Components / Status

| Component | Status | Notes |
|-----------|--------|-------|
| `cron_registry.yaml` | BUILD (skeleton populated session 32) | Lives at `factory/governance/050-cron-registry/cron_registry.yaml` |
| Mission Control cron panel | TBD | Wires up post per-process GREEN; surfaces registry to UT Viewer |
| `wrangler cron triggers list` | OPERATE (CLI exists) | Mechanic uses for live verification |
| LBB subject_id `processes` | OPERATE | Per-fire log destination |

### §3c FCEs Attached
TBV — likely no FCE (this is governance, not domain analytics).

### §3d BARs Referenced
- BAR-375 (fleet-wide UT-firing-on-cron verification)
- BAR-812 / BAR-813 (mission-control crons disabled — registry tracks)
- (Cron Registry init BAR — to file Sunday)

### §3e LBB Subjects Fed
- `system` (registry doctrine + version bumps)
- `processes` (drift events, cron fire logs roll up here when LBB ingest pattern enforced fleet-wide)

---

## §4 IMO

**Input:** wrangler.toml `[triggers]` blocks across all repos + GH Actions `schedule:` blocks + server crontabs (any).

**Middle:** for each cron, capture metadata (id, process, binding, repo, path, schedule, timezone, purpose, orbt, last_verified, on_failure, is_disabled+reason). Aggregate into `cron_registry.yaml`. Audit weekly.

**Output:** `cron_registry.yaml` (canonical) + drift events to LBB + squawks to mission-control on drift.

### §4 IMO Table

| I — Input | M — Middle | O — Output |
|-----------|------------|------------|
| **Source:** wrangler.toml `[triggers]` blocks + GH Actions schedules + server crontabs across all Barton repos | **Transformation:** scan each source, normalize to registry schema, write entry per cron | **Writes:** `cron_registry.yaml` (canonical YAML) + LBB log of drift events |
| **Trigger:** weekly drift check `0 4 * * 0` (Sunday 4am UTC) + per-PR CI check | **Doctrine:** every cron MUST have a registry row; AI MUST NEVER appear as scheduler; disabled crons MUST cite the BAR that disabled them | **Downstream:** Mission Control cron panel reads YAML for visualization; per-process audits reference registry |
| **Boundary:** every cron has wrangler.toml or .yml or crontab line provable by file path | **Stop:** drift detected (registry says X, live says Y) — squawk; AI-on-spine grep hit — halt the offending cron | **Squawk:** drift event → mission-control with `subject_id=system` + severity ORANGE (degraded) or RED (broken) |

---

## §5 OSAM (READ / WRITE / Forbidden / Routing)

**READ:**
- All wrangler.toml files in `imo-creator-v2/workers/`, `Barton-Processes/factory/`, `barton-outreach-core/workers/` (when they exist)
- GitHub Actions YAML at `.github/workflows/*.yml` in any Barton repo
- Server crontab entries (where any exist — `crontab -l`)

**WRITE:**
- `factory/governance/050-cron-registry/cron_registry.yaml` (this process's only canonical artifact)
- LBB rows on drift events (subject_id=`system`)
- mission-control squawks on drift severity ORANGE/RED

**Forbidden:**
- ❌ Writing to any source wrangler.toml directly (the registry indexes; doesn't author the source)
- ❌ Modifying `[triggers]` blocks during the audit (drift fixes go through per-process BARs)
- ❌ Approving an AI-on-spine cron (any cron whose handler calls an LLM during scheduled execution = doctrine violation)

**Query Routing:**
- "What's scheduled to fire next?" → registry YAML
- "Is this cron firing in reality?" → `wrangler cron triggers list <worker>` + LBB last-fire log
- "Why is this cron disabled?" → registry YAML `is_disabled: true` + `disabled_reason: <BAR-NNN>`

---

## §6 Locked Rules (D-050-XX) → see DOCTRINE.md (sibling file)

Quick summary:
- D-050-01: Every cron in the fleet MUST have a registry entry
- D-050-02: New crons cannot ship without a `cron_registry.yaml` diff in same PR
- D-050-03: AI is NEVER the scheduler; LLM calls inside a scheduled handler = doctrine violation, halt
- D-050-04: Disabled crons MUST cite the BAR that disabled them
- D-050-05: Weekly drift check is itself a registered cron (meta-recursion intentional)
- D-050-06: Registry edits require sovereign sign-off (Dave) — Mechanic proposes, sovereign approves

---

## §7 Pre-Flight (every fire of the weekly drift cron)

- [ ] All source wrangler.toml files reachable
- [ ] All registered workers respond to `wrangler cron triggers list`
- [ ] LBB worker reachable for log writes
- [ ] mission-control reachable for squawk writes

---

## §8 Stop Conditions + Kill Switch

**Stop normally:** weekly drift check completes, registry matches live state, 0 AI-on-spine hits.

**Hard HALT:**
- Drift > 10% (>3 crons out of registry sync) → halt the auto-correct path; sovereign must sign off on resync
- AI-on-spine grep hit → halt the offending cron immediately, escalate, do NOT auto-correct

**Kill switch:** `wrangler triggers unschedule <worker>` (per-cron kill); registry-wide kill = comment out the meta-drift cron.

---

## §9 Live Verification

**§9a Live Dashboard:** Mission Control / cron panel (post-wiring)

**§9b Gauges:**
- Active crons in registry: ≥5 (current baseline session 32)
- Disabled crons in registry: 1 (mission-control-api COS, BAR-812/813)
- Drift count weekly: 0 (acceptable: 0); SLO: ≥1 = squawk
- AI-on-spine hits: 0 (HARD: any > 0 is a halt)

---

## §10 Operations

**Schedule:** `0 4 * * 0` weekly Sunday 4am UTC drift check (proposed — register once Cron Registry process exits BUILD).

**On-call rotation:** N/A (Dave is sole operator currently).

**Failure mode handling:** drift → ORANGE squawk + LBB log; AI-on-spine → RED squawk + immediate halt of offending cron.

---

## §11 Doctrine Cross-Reference

- `law/doctrine/PLAN-MASTER-CRON-AUTOMATION.md` (parent strategy in imo-creator-v2)
- `law/doctrine/PLAN-GAME-PLAN.md` (per-process audit cycle this registry feeds)
- `law/doctrine/FOUNDATIONAL_BEDROCK.md` (cron is the deterministic trigger; AI is tail not spine)

---

## §12 BARs Referenced

- BAR-375 — fleet-wide cron-firing verification (sister)
- BAR-812 / BAR-813 — mission-control COS Twilio crons disabled (registry tracks the disable)
- (BAR-XXX — Cron Registry init, to file Sunday)

---

## §13 Owner Contact

Dave Barton — sole sovereign. Strike-3 escalation = pause for sovereign call (per Decision Sheet E1).

---

## §14 Maintenance Logbook

| Date | Author | Action | Reason |
|------|--------|--------|--------|
| 2026-05-02 | Opus 4.7 (Planner) | Stub created | Per game plan §12 deliverable #2 — Cron Registry process initialized in Barton-Processes governance silo. cron_registry.yaml skeleton committed alongside. Awaits Mechanic dispatch (Sunday) to populate from live wrangler.toml introspection. |

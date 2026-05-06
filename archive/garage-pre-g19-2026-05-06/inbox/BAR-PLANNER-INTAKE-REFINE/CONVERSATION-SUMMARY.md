# Conversation Summary — Planner Intake Template Refinement

**Session:** 2026-05-06 (sovereign Dave Barton + Opus-4-7-foreman)
**Purpose:** Identify gaps in `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` and the paired `planner-intake-template.yaml`, then have Four-Brain refine its own template to incorporate them.

---

## §1 — Architectural framing the conversation locked

These are sovereign-affirmed positions to be reflected in the refined template.

1. **Atlas is HOW stuff is done.** The Atlas (`atlas/ATLAS.md` v2.2.7 + the 17 locked constants) is a static reference for the Planner. Operational work does NOT amend the Atlas.
2. **The leaf template is HOW work flows in.** The Planner intake template is the input contract. Both Atlas and template are constants on the shelf.
3. **Four-Brain is the gate.** Every build, repair, modification, or new system flows through Planner → Foreman → Mechanic → Auditor. By construction, BS Law is enforced on every output because the Planner reads the Atlas first.
4. **The template + model swap is the dominant maintenance lane.** Template amendments + model upgrades cover most ongoing maintenance. Locked-constant amendments + infrastructure changes still happen but go through Four-Brain like everything else (sovereign-led BARs).
5. **All scheduled maintenance flows through Four-Brain.** Squawks (reactive) and tune-ups (scheduled A/B/C/D-checks + AD) are different trigger sources into the same pipeline. Library logs everything.
6. **Self-repair within boundaries.** Four-Brain CAN repair itself via the same leaf template. Three hard ceilings: bootstrap paradox (broken Planner can't process leaves), sovereign-only locked constants, Strike 3 → human Troubleshoot/Train.
7. **The end-state of this BAR is a refined PLANNER-INTAKE-TEMPLATE.md (+ paired yaml) carrying every field the Planner needs.** Once Codex CERTIFY's and sovereign signs, that's the locked template every future BAR fills out. One template. Comprehensive.

---

## §2 — Altitude scale (Atlas §1.2.3 — confirmed, no amendment)

| Altitude | What lives here |
|----------|-----------------|
| 50K Strategic | Whole tree. Sovereign view (Dave's "Office"). Per Atlas: "Dave operates at 50K strategically." |
| 40K Branch | One branch — II / Real Estate / Personal |
| 30K Tactical | Entity or Hub slice within a branch — SVG Agency, Briar Valley Properties, Kiddos |
| 10K Operational | One Hub — Outreach, Sales, Client, FIND, BUILD, OPERATE |
| 5K Execution | One row, field, instance |

**No 60K.** Earlier proposal to add a sovereign altitude was rejected per Atlas conformance. Dave sits AT 50K.

---

## §3 — Roles and overlays (not altitudes, not new template fields)

Already in doctrine. Listed here so the Planner can confirm the refined template doesn't conflate them.

- **CoS** = Hub at the trunk node (not an altitude). Consolidator. Reports up to sovereign. Has its own assistant for email/calendar.
- **Master Error Table** = Pressure Gauge aggregation per Atlas §1.2.5. Cross-cutting overlay.
- **Inbox / Outbox** = Plumbing per Atlas §1.2.5. Already lives in `mission-control-api`. Cross-cutting.
- **Cron / Loop Manager** = Plumbing.
- **FCE** = Dyno output (FCE Book species). Read by Planner. Not a destination.
- **Snap-On Toolbox** = Ratchets per Atlas §1.2.5. Drawer at every altitude.
- **Library** = Eternal record. Holds doctrinal Books + operational Books.

---

## §4 — Trigger sources for leaves (one pipeline, multiple inputs)

Every leaf carries a `trigger` value. Auditor applies the right strike rule per trigger.

| Trigger | Strike tally? | Notes |
|---------|---------------|-------|
| sovereign-issued | yes | Direct order from Dave |
| cos-escalation | yes | CoS judging an anomaly worth Dave's attention |
| reactive-squawk | yes | Pressure gauge red |
| scheduled-tune-up | **no** | Per Four-Brain Aviation v1.1.0 — findings don't accumulate Strikes |
| mechanic-discovered-sub-build | yes | Mechanic uncovers a missing piece during a build |
| cron-fired | varies | Non-tune-up scheduled work |

When `trigger=scheduled-tune-up`, also requires `tune_up_type` ∈ {A-check, B-check, C-check, D-check, AD}.

---

## §5 — Build modes (within Operating Mode = BUILD)

The current template has Operating Mode = BUILD/REPAIR/OPERATE/TROUBLESHOOT_TRAIN. Within BUILD, three sub-modes determine whether the Planner dispatches a Dyno upstream:

| Sub-mode | When | Pipeline upstream |
|----------|------|-------------------|
| discovery | Structure unknown / competitive / "where's the herd vs neglected upside" | Dyno (US→K=C→DMJ→UP) → FCE Book → Planner consumes |
| declared | Structure already known, internal, controlled | Planner reads existing UTs/CTB/Atlas, no Dyno |
| maintenance | Modifying a locked system (delta against existing UT) | No new structure, no discovery |

**Auditor verifies the mode call.** If `declared` is claimed but no UT exists in the Library covering that structure, reject and force `discovery`.

---

## §6 — Mobile Mechanic + Strike rules

Per BAR-334 military hierarchy + Foundational Bedrock §6:

- Mobile Mechanic (Sergeant rank — deterministic CF Worker) watches the master error table.
- Picks up squawks, patches rows deterministically.
- Each row patch = a leaf (lightweight Plan Book / fast-path).
- `root_cause_hash` is the strike key (deterministic — derived from error_type + source_component + failure_signature, NOT row identity).
- Strike counter persists in D1 keyed by `root_cause_hash`.
- Strike 1, 2 = patch row, increment counter.
- **Strike 3 → STOP patching rows. File system-fix leaf with `target=broken-component, is_system_level_fix=true`.** Goes through full Four-Brain pipeline. After CERTIFY, strike counter resets for that hash.

---

## §7 — Universal capture pattern (BS Law applied to operations)

Every event becomes a Book in the Library. Two lifecycle types:

| Type | Examples | Lifecycle |
|------|----------|-----------|
| Doctrinal Books | Atlas, locked constants, UTs, Plans, Audits, repos | Sovereign-amended, versioned, slow-changing |
| Operational Books | Inbound email, outbound email, call, calendar event, squawk, BAR completion, briefing, FCE run | Auto-generated by writers, append-only, time-indexed, high-volume |

Same outside-arm/inside-arm structure for both. Same renderer. Same Library navigation. Different storage tier (hot D1 / warm-cold R2).

---

## §8 — Gaps in the current PLANNER-INTAKE-TEMPLATE.md identified during conversation

The Planner is invited to incorporate or reject each. The Planner OWNS the route — this is input, not prescription.

| # | Gap | Reason |
|---|-----|--------|
| G-01 | `trigger` enum field (source classification) | Currently absent. Auditor needs it to apply strike rules correctly. |
| G-02 | `tune_up_type` enum (conditional on trigger=scheduled-tune-up) | Aviation v1.1.0 defines A/B/C/D-check + AD; intake should capture which. |
| G-03 | `target_is_four_brain` boolean | Self-modification leaves need extra audit gates and rollback plan. |
| G-04 | `counts_toward_strike_tally` boolean | Auditor enforces — sovereign-issued and scheduled-tune-up don't count. |
| G-05 | Build sub-mode field (discovery / declared / maintenance) | Operating Mode=BUILD is broad; sub-mode determines whether Dyno dispatches upstream. |
| G-06 | `mode_justification` text required | Forces explicit reasoning for the mode call so Auditor can verify. |
| G-07 | `simpler_alternative_considered` text required | Forces simplicity gate per Planner Discipline Order. |
| G-08 | `determinism_check` text required | Forces "where could LLM be replaced by deterministic code?" answer per LLM-tail-only rule. |
| G-09 | `rollback_plan` text (conditional on target_is_four_brain=true) | Required for self-modification leaves. |
| G-10 | `is_system_level_fix` boolean | Distinguishes Mobile Mechanic row patches (false) from Strike-3 system fixes (true). |
| G-11 | `root_cause_hash` field for repair leaves | Strike key for Mobile Mechanic patches. |
| G-12 | Maintenance schedule block in Plan Book deliverable for build-mode leaves | Aviation Model: every system gets A/B/C/D-check schedule baked in at build. Sovereign-call whether this is a Plan-Body amendment (Book Law / Four-Brain Aviation) or a Planner deliverable line item. |
| G-13 | `lbb_record_id` field for the conversation context referenced from this BAR | Already partially in the lbb_pull_contract; should be required when the leaf has prior session context. |
| G-14 | Reference to existing FCE Book(s) for the domain when mode=discovery and a prior Dyno run exists | Avoids re-Dyno-ing the same domain redundantly. |
| G-15 | **Atlas + gate-spec version pinning at Plan time** — Plan Book carries `pinned_atlas_version`, `pinned_gate_spec_version` fields. Foreman / Mechanic / Auditor MUST read the pinned versions, not whatever the file is at execution time. | Drift vector #1 + #2: Atlas amended between Plan and Audit causes role drift. Pinning eliminates it. |
| G-16 | **Plan Book freshness TTL** — Plan Book carries `plan_book_ttl_hours` (default 72). Past TTL → Foreman re-validates against current state before dispatching. Aviation analog: stale flight plan must be refiled. | Drift vector #7: time passes between Plan and Mechanic execution; world changes (new squawks, new doctrine, new dependencies). |
| G-17 | **Concurrency rule** — file-level locking at Foreman dispatch. If two BARs claim overlapping `allowed_write_scope`, second one waits or is conflict-flagged. Implemented in `forebrain-garage.sh` plus a new `mission-control.bar_locks` D1 table (or equivalent). | Drift vector #5: two BARs racing on same file produce inconsistent state; second BAR's plan is stale on Mechanic execution. |
| G-18 | **Deterministic gate predicates** — every gate in `four-brain-doctrine-gate.yaml` has a deterministic computation (regex / hash compare / file-existence / JSON schema / `git diff --name-only` against scope list). Where judgment is unavoidable, mark gate as `requires_llm_tail: true` AND require a deterministic fallback test that establishes a floor. | Drift vector #6: Codex hallucinates PASS or FAIL on ambiguous gates. Determinism-first per Atlas means LLM is tail, not spine. |

---

## §8b — Drift Vectors Mapped (rationale for G-15 through G-18)

The Planner validation gate catches semantic drift (roles disagreeing on meaning) — Atlas + KEY ensure roles share vocabulary. What it CANNOT catch is **state-change drift** between roles' reads. Nine vectors identified:

| # | Vector | Already in doctrine? | Lock |
|---|--------|---------------------|------|
| 1 | Atlas version drift between Plan and downstream | partial (PROCESS-UT.md §6 mentions Atlas version pin) | G-15 (mandate it) |
| 2 | Gate-spec version drift | no | G-15 |
| 3 | Mechanic interpretation slop | yes (literal `file:line | old | new` triples per memory) | verify enforcement |
| 4 | Mechanic scope creep | yes (G09 scope gate) | G-18 (make deterministic) |
| 5 | Concurrency on same file | **no** | G-17 |
| 6 | Auditor hallucination | partial (determinism-first doctrine) | G-18 |
| 7 | Plan Book staleness (time) | **no** | G-16 |
| 8 | Template version drift across BARs | yes (version field) | verify usage |
| 9 | Atlas internal drift via sub-doc references | partial (locked constants only) | flag for separate audit |

Vectors 5 and 7 have NO current doctrinal coverage — these are the highest-priority new locks. Vectors 1, 2, 6 have partial coverage that needs hardening.

---

## §9 — Open questions for the Planner to resolve

Only items that block planning. Everything else the Planner handles in its route.

| Q-01 | Should build sub-mode (discovery/declared/maintenance) be a separate field, or expressed as a sub-enum under Operating Mode? Sovereign-call. |
| Q-02 | Should the maintenance schedule for built systems be a Plan-Body amendment (touches Book Law) or just a Planner deliverable line item? The first is sovereign-only via pending-atlas-updates; the second is Plan-internal. |
| Q-03 | Where does the strike counter live operationally — `mission-control.squawks` table augmented, or new `strike_tally` D1 table? Sovereign-call. |
| Q-04 | Are operational Books a new species (Event-Body) or extension of Data-Body? Out-of-scope for this BAR but flagged. |

---

## §10 — Out of scope for this BAR (do NOT include in template refinement)

- The Mobile Mechanic build itself (separate BAR — file when ready)
- The Library Renderer / Mission Control shell build (separate BAR)
- New Book Law species (Event-Body, FCE-Body, Leaf-Body) — sovereign-only constant amendments, NOT this BAR
- Operational writer pipeline implementations (email handler, BAR completion writer, etc.)
- Storage tiering policy (D1 hot / R2 warm-cold thresholds)

---

## §11 — Non-drift invariants for this BAR

- The Planner OWNS the route. This summary specifies destination, boundaries, evidence — not the plan.
- Mechanic ≠ Auditor. Sonnet builds the refined template; Codex audits.
- BS Law Y-junction conformance on both `.md` and `.yaml` outputs of the refined template.
- The current PLANNER-INTAKE-TEMPLATE.md and planner-intake-template.yaml at version 1.0.0 are the baseline. The refined version is a delta against them.
- No locked constants modified. This is a process-level template under `Barton-Processes/`, not under any of the 17 locked constants.

---

## §12 — P=1 definition

This BAR is P=1 when:

1. PLANNER-INTAKE-TEMPLATE.md is updated to incorporate the gaps listed in §8 (Planner may justify rejecting any individual gap with reasoning).
2. The paired `planner-intake-template.yaml` is updated in lock-step with full BS Law Y-junction conformance.
3. Codex audits and signs `VERDICT: P=1` against gates BS Law / UT conformance / scope / aviation role separation / evidence.
4. Sovereign (Dave Barton) reviews and signs the version bump.
5. LBB transition rows recorded for planner / foreman / mechanic / auditor (4 rows minimum) per Four-Brain Aviation v1.2.0.
6. CERTIFY row written to lbb.logbook.

---

## §13 — Document control

| Field | Value |
|-------|-------|
| Created | 2026-05-06 |
| Author | Opus-4-7-foreman (drafted in conversation with sovereign) |
| Source | Real-time conversation 2026-05-06 between sovereign and Opus-4-7-foreman |
| Purpose | LBB-ingestible source artifact for BAR-PLANNER-INTAKE-REFINE |
| Status | Brainstorming packet — to be promoted to facts by Planner where applicable; remaining items stay as assumptions for sovereign confirmation |
| Subject ID for LBB | processes |

# AMENDMENT — Three Altitudes Locked Into the Spine + BS Law

**Status:** PENDING (proposed amendment to the Spine and BS Law)
**Authority:** Dave Barton (sovereign)
**Date proposed:** 2026-05-07
**Affects:**
- The Spine (`atlas/ATLAS.md` → `## Three Layers Spine`, formerly locked constant #14)
- BS Law (`atlas/ATLAS.md` → `## BS Law — Y Junction`, formerly locked constant #17)
**Source artifact:** `atlas/constants/THREE_ALTITUDES.md` v1.0.0 (gated provisional, derived from FCE tier-count run sovereign_id `a23e9997-4191-49ae-aef3-bb7d412eae49`)
**Mirrors:**
- `Barton-Processes/factory/imo-creator/060-run-dyno/AMENDMENT-THREE-ALTITUDES-INTO-SPINE.md`
- `dyno-engine/AMENDMENT-THREE-ALTITUDES-INTO-SPINE.md`

---

## Why

The Spine currently encodes three layers — HEIR+ORBT (universal language), the four engines (US → K=C → DMJ → UP), and the four elements (C&V + IMO + CTB + Circle). CTB carries a cadence altitude axis (50K / 30K / 10K / 5K). It does NOT carry a structural altitude axis.

The FCE tier-count run derived three structural altitudes from the Three Primitives (Foundational Bedrock §1):

| Altitude | Primitive | Question Answered |
|---|---|---|
| **Stratification Layer** | Thing | What exists at this depth? |
| **Information Flow** | Flow | What moves between depths? |
| **State Transition** | Change | What flips at this depth? |

These three are orthogonal to CTB's cadence axis. Every artifact has a cadence (how often the answer changes) AND a structural role (what kind of element it is). Without the structural axis on the Spine, BS Law cannot enforce structural classification at the Y-junction. Every Library Book today carries HEIR (identity) and ORBT (state) but no structural classifier. That gap lets jargon survive — a Book can claim to be a UT-Body without being forced to declare which structural altitude its subject manifests as.

## What changes

### Spine update — Three Altitudes as a structural axis on Layer 3

Layer 3 (validation laws) currently lists C&V + IMO + CTB + Circle. CTB has been a single-axis cadence classifier. After this amendment:

```
Layer 3 — Validation laws
  - C&V (Constants and Variables)
  - IMO (Input → Middle → Output)
  - CTB (Christmas Tree Backbone)
      ├─ cadence axis: 50K / 30K / 10K / 5K (years → events)
      └─ structural axis: Stratification Layer / Information Flow / State Transition (Thing / Flow / Change)
  - Circle (feedback loop)
  - Three Altitudes (THREE_ALTITUDES.md — canonical descriptions)
```

The Three Altitudes appear both as a sub-axis of CTB (since CTB is the natural home for altitude classification) AND as a standalone reference under Layer 3 (since the canonical descriptions in `THREE_ALTITUDES.md` are inherited by every system the Spine touches). This is intentional redundancy — the structural axis is a CTB feature AND a first-class element.

### BS Law update — Y-junction conformance now requires three orthogonal classifiers

Today, every Library Book at the Y-junction must declare:
- **HEIR** identity (8 fields)
- **ORBT** state

After this amendment, every Library Book at the Y-junction must ALSO declare:
- **Structural altitude** — which of the Three Altitudes (Stratification Layer / Information Flow / State Transition) the Book's subject dominantly manifests as, with optional `secondary_altitudes` for subjects that legitimately read as multiple altitudes under different observers (dynamic-altitude case)

The new BS Law block at every Y-junction (in both `outside:` and `inside:` arms):

```yaml
outside:
  heir: { ... }
  orbt: { ... }
  altitude:
    primary: "Stratification Layer | Information Flow | State Transition"
    primary_primitive: "Thing | Flow | Change"
    secondary: []

inside:
  heir: { ... }
  orbt: { ... }
  altitude:
    primary: "..."
    primary_primitive: "..."
    secondary: [...]
```

The `altitude:` block is **descriptive, not K=C-audited**. The author of a Book picks the dominant altitude for the subject (and flags secondary readings if relevant). K=C is NOT required at the per-Book level because not every Book is FCE-derived. K=C remains the gate at the FCE constant-locking moment only — it is not a per-artifact audit requirement.

### New invariants

**INV-22 — Three Altitudes On Spine**
The Spine's Layer 3 includes the Three Altitudes (Stratification Layer / Information Flow / State Transition) as a structural axis on CTB and as a first-class validation element. Canonical descriptions are sourced from `atlas/constants/THREE_ALTITUDES.md`. Every doctrine artifact, process artifact, and library artifact inherits this axis.
*Enforced at:* doctrine read order, Spine references, BS Law audit.

**INV-23 — Y-Junction Altitude Declaration (descriptive)**
Every Library Book artifact crossing the Y-junction declares an `altitude:` block in both `outside:` and `inside:` arms. The block specifies a `primary` altitude (one of Stratification Layer / Information Flow / State Transition), the `primary_primitive` (one of Thing / Flow / Change), and an optional `secondary` list of other valid altitude readings. The declaration is descriptive — the author picks the dominant altitude for the subject. K=C audit is NOT required at this level. Books missing the block fail BS Law audit on **completeness** grounds (the field is required), not on K=C grounds.
*Enforced at:* BS Law audit on every Library Book, every UT, every Plan, every Audit, every Catalog, every Research artifact.

## Implementation scope

- **Doctrine-only.** This amendment changes what the Spine declares and what BS Law audits. It does not require engine changes. The matrix is a **design lens** for building anything new — not an FCE prerequisite.
- **Not everything has an FCE.** The altitude declaration on a Book is descriptive author classification, not K=C-validated. FCE-derived constants get K=C-stamped altitude as part of the FCE flow; non-FCE artifacts (UTs, Plans, Audits, Catalogs, Research, infrastructure docs) just carry author-declared altitude.
- **Backward-compat:** existing Library Books pre-amendment may carry `altitude: null` until re-classified. The field becomes required for new Books.
- **New Books:** must declare `altitude:` from creation; BS Law audit blocks on missing field (completeness check), not on K=C.
- **Codex auditor:** gets a new gate (G17 — altitude block present and valid). G17 added to the existing G01–G16 gate set. G17 checks structural completeness only, not K=C.

## Where the matrix actually pays off

The matrix is a **design lens**, not an audit gate. The leverage shows up in two operational moments:

**1. Building anything new.** When you go to design a system, process, worker, database, anything — the matrix is your structural template. Walk down the cadence axis (50K → 5K) asking "what Things, Flows, Changes belong at this level?" That is the design session. The matrix replaces ad-hoc brainstorming with a 4×3 fill-in.

**2. DMJ across FCEs.** When N≥2 FCEs land in the same family, JOIN needs a canonical join key. Altitude IS the join key. Storage's "Container Occupancy State" and real estate's "Lease Status" are both 5K-cadence State Transitions — they JOIN on the matrix even though their names differ. DMJ becomes mechanical lookup against the 4×3 grid instead of fuzzy text matching across arbitrary names.

## Verification plan

After implementation:
1. Pick one existing Library Book.
2. Add the `altitude:` block to both arms.
3. Run BS Law audit. Confirm pass on completeness (field present, valid value).
4. Pick a second Book missing the block. Confirm audit fails on missing-field check.
5. Use the matrix as the design lens for a new artifact — walk the 4×3 grid filling in Things, Flows, Changes at each cadence. Confirm the resulting artifact has structural completeness without ad-hoc brainstorming.

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Sovereign (proposer) | Dave Barton | 2026-05-07 | proposed |
| Mechanic (implementer) | TBD (Sonnet) | TBD | pending |
| Auditor (certifier) | Codex | TBD | pending |

## Document control

| Field | Value |
|-------|-------|
| Version | 1.1.0 |
| Status | PROPOSED |
| Created | 2026-05-07 |
| Last Modified | 2026-05-07 |
| v1.1.0 change | Removed K=C-justified-altitude requirement (former INV-24). Per-Book altitude declaration is descriptive (author classification), not K=C-audited. K=C remains the gate at FCE constant-locking only. Added §"Where the matrix actually pays off" (design lens + DMJ join key). Added matrix reference (THREE_ALTITUDES.md §5). |
| Source artifact | atlas/constants/THREE_ALTITUDES.md v1.1.0 (matrix locked) |
| Affects | Spine (ATLAS.md §Three Layers Spine), BS Law (ATLAS.md §BS Law — Y Junction) |
| Inherits from | FOUNDATIONAL_BEDROCK §1 (Three Primitives), KEY.md (vocabulary), ALTITUDE_LEGEND.md (cadence axis), THREE_ALTITUDES.md (structural axis + matrix) |
| Mirrors | Barton-Processes/060/AMENDMENT-THREE-ALTITUDES-INTO-SPINE.md, dyno-engine/AMENDMENT-THREE-ALTITUDES-INTO-SPINE.md |

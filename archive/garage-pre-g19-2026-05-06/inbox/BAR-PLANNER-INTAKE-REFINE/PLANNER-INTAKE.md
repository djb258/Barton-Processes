# BAR-PLANNER-INTAKE-REFINE — Sovereign Brief (REVISED 2026-05-06)

**Supersedes:** prior intake (Plan Book v1 superseded; old run dir 20260506T132146Z preserved as audit history).
**Authority:** Sovereign (Dave Barton).
**Pipeline status:** READY_FOR_PLANNER (re-dispatch).

---

## WHERE FROM (INPUT)

The current `PLANNER-INTAKE-TEMPLATE.md` (v1.0.0, 403 lines, 19 sections) and its paired `planner-intake-template.yaml`. Plus the locked architecture from sovereign session 2026-05-06 (this conversation), captured in LBB record `1f19c519-f402-421f-bb5c-8eeaa7f7d9e9` (G-19 doctrine) and the broader sovereign discussion that locked the template-as-leaf model.

---

## WHAT (MIDDLE — what do we want done)

**Replace the 19-section template with a thin, client-brief-shaped template.**

Locked design from sovereign session 2026-05-06 (FINAL — TYPE asked LAST + conditional follow-up):

**Question order (TYPE intentionally last — describe before classifying):**

```
Q1. WHERE FROM    — where is the information coming from
Q2. WHAT          — what do you want done with it
Q3. WHERE TO      — where does the information go
Q4. TYPE          — [1=Build · 2=Fix · 3=Maintenance]
   if Q4=1 (Build):       Q4A. MAINTENANCE CADENCE — A/B/C/D-check schedule
   if Q4=2 (Fix):         Q4A. SQUAWK / SYMPTOM     — what triggered this fix
   if Q4=3 (Maintenance): Q4A. CHECK LEVEL          — A-check / B-check / C-check / D-check / AD
```

**Five mandatory total** (4 base + 1 conditional). Conditional follow-up is determined by Q4's answer.

**Aviation analogy** (locks the TYPE taxonomy):
- **Build** = factory floor — new construction; cadence declared at birth so the garage knows when to inspect
- **Fix** = garage repair bay — reactive, squawk-driven; symptom captured for traceability
- **Maintenance** = garage scheduled-tune-up bay — A/B/C/D-checks per FAA-style schedule

**Edge-case routing (default until proven wrong):**
- Refactor → Build (new shape, even if file exists)
- Research → Build (output is new findings doc)
- Delete → Fix (squawk = "this is dead weight")
- Add 4th type only if default routing produces wrong audit behavior on >3 consecutive BARs

**Pipeline behavior driven by TYPE flag** (no new process, just downstream tuning):

| TYPE | Strike accumulates? | Audit mode | Cron-eligible? |
|---|---|---|---|
| Build | yes | full conformance | no — sovereign or LLM dispatch |
| Fix | yes | delta + regression | no — squawk-driven |
| Maintenance | **no** (per FOUR_BRAIN_AVIATION v1.1.0) | delta + drift sweep | yes — A/B/C/D-check cron |

Single Process 070 stays. TYPE is metadata on the BAR; downstream stages read it and adjust audit packet, strike accounting, and cron eligibility.

**Optional helper fields (6, all client-vocabulary, no engineering):**
- WHY — purpose / use case
- WHO FOR — which org or area (SVG / BVP / Personal / system)
- DEADLINE — when does this need to land
- CONSTRAINTS — must-haves, can't-haves
- EXISTING — related artifacts you already know about
- REFERENCE — linked Linear ticket, prior BAR, doc

**Planner-side wiring (no human burden):**
The Planner pulls ALL of the following automatically — the human never declares them in a brief:
- CTB tree → `atlas/constants/BARTON_ENTERPRISES_CTB.md`
- Altitude scale → `atlas/ATLAS.md` §1.2.3 (50K/40K/30K/10K/5K)
- Existing artifacts → `atlas/manifests/paired-artifacts.yaml`
- Repo structure → `atlas/manifests/STRUCTURE_MANIFEST.yaml`
- Locked-constants list → CLAUDE.md (the 17 + new MISSION_CONTROL + UI_STYLE_GUIDE pending)
- Prior art / decisions → LBB (subjects: system, processes)

These pointers live in the Planner role's manual (`atlas/constants/PLANNER_ROLE.md`), not in the template.

**G-19 doctrine** (LBB `1f19c519-f402-421f-bb5c-8eeaa7f7d9e9`): the only sovereign touchpoints are template-drop (input boundary) and Auditor verdict (output boundary). NO sovereign approval gates between Planner / Foreman / Mechanic / Auditor. Pipeline auto-advances on stage success. Mission Control surfaces stage transitions as observation only. Garage statuses like `REVIEW_PLAN_BOOK` are removed; replaced with auto-advance transitions.

**Quality bail-out:** if a brief is sub-actionable (vacuous fills like "from my brain / make it nice / repo"), the Planner asks ONE targeted question to fill the specific gap before producing a Plan Book. Asking is the exception path, not the default flow.

---

## WHERE TO (OUTPUT)

Five artifacts updated lock-step:

1. `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` — the new thin template (3 mandatory + 6 optional, ~30-50 lines, plain language only)
2. `Barton-Processes/factory/imo-creator/070-four-brain/planner-intake-template.yaml` — paired YAML, BS Law Y-junction, version bump
3. `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` — PROC-070 reflects the new template; Q-01–Q-04 from the old plan retired
4. `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` — paired with PROCESS-UT
5. `imo-creator-v2/atlas/constants/PLANNER_ROLE.md` — Planner config: declares the read-set wiring (CTB, Atlas, paired-artifacts, STRUCTURE_MANIFEST, CLAUDE.md, LBB) so the Planner has all maps without the human having to declare them

All five conform to BS Law v1.5.0 Y-junction, UT_CHECKLIST current version, paired-artifact rule. Skeleton (14 sections + 13-item UT_CHECKLIST + Y-junction) is CONSTANT and unchanged. Variable fill is what updates.

**Acceptance:** Codex audit verdict P=1 across all five artifacts; sovereign signs version bumps.

---

## OPTIONAL HELPERS

- **WHY:** Current template is JIRA-shaped; sovereign drops are friction-heavy. New shape lets sovereign or any LLM drop a brief in seconds. Plus prepares the pipeline for parallel BARs (mechanical concurrency work happens in parallel, separate scope).
- **WHO FOR:** system (PROC-070 doctrine; affects every future BAR in the garage)
- **DEADLINE:** none specified; sovereign reviews when ready
- **CONSTRAINTS:**
  - Locked constants are off-limits (the 17 in CLAUDE.md + pending MISSION_CONTROL + UI_STYLE_GUIDE — all sovereign-only amendment)
  - Plain-language only on every field facing the human; no engineering vocab in template fields
  - No optional-field bloat — cap at 6, sovereign sign-off to add new optionals
  - Must implement quality bail-out (single targeted clarification on vacuous briefs)
  - Must implement G-19 (no inter-stage sovereign gates)
- **EXISTING:**
  - Prior Plan Book v1: `docs/plans/BAR-PLANNER-INTAKE-REFINE/PLAN-BOOK.md` (superseded; will be regenerated by Planner)
  - Old run dir: `garage/runs/BAR-PLANNER-INTAKE-REFINE/20260506T132146Z/` (preserved as audit history)
  - LBB canonical (prior gaps): `090520d7-ff64-4b6e-9e14-5e8928b24db7`
  - LBB G-19: `1f19c519-f402-421f-bb5c-8eeaa7f7d9e9`
- **REFERENCE:** session 2026-05-06 sovereign brainstorming thread — architect-client model locked the design

---

## NOTE ON Q-01 / Q-02 / Q-03 / Q-04 (FROM PRIOR PLAN BOOK)

All four open questions from the prior plan are **moot** under the new locked design:

- **Q-01 (build sub-mode field):** retired — template no longer has 19 sections; sub-mode tracking moves to Plan Book if needed at all
- **Q-02 (downstream DMJ PROC number):** retired — out of scope; this BAR is template-only
- **Q-03 (imo-creator four-brain UT path):** sovereign decision — drop the imo-creator four-brain UT update from this BAR; Mission Control + UI Style Guide already cover the imo-creator-v2 UI surface; PLANNER_ROLE.md is the Planner-config artifact
- **Q-04 (LBB record canonicalization):** answered — `090520d7` is canonical for prior gaps; `1f19c519` is canonical for G-19

Mechanic does NOT need to halt on these. Proceed.

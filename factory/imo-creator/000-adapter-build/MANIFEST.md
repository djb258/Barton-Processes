# PROCESS-000: Domain Adapter Build
# Status: ACTIVE (OPR)
# Last Updated: 2026-03-25

---

## IDENTITY (HEIR)

| Field | Value |
|-------|-------|
| Process ID | PROC-ADAPTER-BUILD |
| Number | 000 |
| Name | Domain Adapter Build Process |
| Blueprint | imo-creator-v2 → `bedrock/ADAPTER_BUILD_PROCESS.md` |
| Runtime | Human + LLM (procedure, not code) |
| Deployed URL | N/A — this is a procedure, not a service |
| ORBT | OPR |
| Strikes | 0 |

---

## IMO

**Input:** A new domain that needs the Tier 0 engine applied. Examples: US Equities sector rotation, SVG insurance pipeline, storage facility acquisition, any future competitive resource allocation domain.

**Middle:** Three-pass cycle executed by human + LLM:

1. **Pass 1 — Math 2 (Define):**
   - Declare the candidate (what is x?)
   - Define comparators (what do you measure? — must trace to Thing/Flow/Change)
   - Set initial tolerances (educated guess — will be wrong)
   - Define transformation (what changes between cycles?)
   - Set operational parameters (N_min, σ_max, α, δ, etc.)
   - Run 20-point validation checklist

2. **Pass 2 — Math 1 (Validate):**
   - Feed real candidates into `P(x; θ) = 1 if max_i[C_i(x)/k_i] ≤ 1`
   - Read diagnostic vector r(x) — which comparators broke and by how much
   - Run stability across N cycles
   - Check global consistency (back-propagation)
   - Read sigma — tightening (real) / flat (phantom) / expanding (broken)

3. **Pass 3 — Math 2 (Tighten):**
   - Fix broken comparators (remove useless, replace unstable)
   - Adjust tolerances at failure boundaries
   - Check coupling — does changing k_i break k_j?
   - Verify feasible region: `vol(Θ)^(1/n) ≥ δ`
   - Re-run 20-point checklist
   - Go back to Pass 2

**Output:** A locked domain adapter stored at `domains/{domain-name}/adapter.md` in Math 2 format. Binary go/no-go classifications that hold across cycles, survive back-propagation, and have healthy sigma.

**Circle:** Every calibration cycle produces diagnostics that feed the next cycle. Tolerances converge. Sigma tightens. Process terminates when remaining variables are domesticated. After deployment, production data feeds back for continuous calibration.

---

## DATABASES

This process does not own tables. It PRODUCES adapters that define what tables the domain's pipeline reads.

The adapters reference:
- `bedrock/math-01-engine.md` — the engine equation (read only, FROZEN)
- `bedrock/math-02-adapter-template.md` — the adapter interface (read only)
- `domains/{domain}/adapter.md` — the output of this process (write)

---

## DEPENDENCIES

### Upstream
| Dependency | What | Status |
|-----------|------|--------|
| Bedrock math docs | Engine (M1) + Adapter Template (M2) | LOCKED |
| Concept docs 1-9 | Three Primitives through FCE | LOCKED |
| Domain knowledge | Subject matter expertise for comparator selection | Per domain |
| Real data | Actual candidates for engine validation | Per domain |

### Downstream
| Consumer | What |
|----------|------|
| Every domain pipeline | The adapter defines what the pipeline measures |
| layer0-engine | Executes P(x;θ) using adapter-defined comparators |
| Monte Carlo simulations | Uses adapter tolerances for probability distributions |
| Dashboard | Displays classifications and sigma tracking |

---

## CURRENT STATE (as of 2026-03-25)

| Metric | Value |
|--------|-------|
| Process defined | YES — bedrock/ADAPTER_BUILD_PROCESS.md |
| Math 1 (Engine) | FROZEN v3.0 |
| Math 2 (Template) | DRAFT v1.2 (Round 1 patches applied, Round 2 in progress) |
| Adapters in Math 2 format | 0 (all 3 existing adapters are in FCE narrative format) |
| Adapters in FCE format | 3 (insurance, equities, storage) |
| Full three-pass cycles completed | 0 |

---

## KNOWN ISSUES

| Date | Issue | Resolution | Strikes |
|------|-------|------------|---------|
| 2026-03-25 | Existing FCE adapters not in Math 2 format | Need conversion — FCE narrative → formal Math 2 template | 0 |
| 2026-03-25 | layer0-engine doesn't execute P(x;θ) v3.0 | Worker exists but predates v3.0 math | 0 |
| 2026-03-25 | No adapter has completed the full three-pass cycle | First candidate: SVG insurance adapter | 0 |

---

## SMOKE TEST

1. Pick a domain (start with SVG insurance — most data available)
2. Execute Pass 1: fill Math 2 template with insurance comparators
   → expected: completed adapter draft with all fields, 20-point checklist passes
3. Execute Pass 2: feed 10 real companies through P(x;θ)
   → expected: classifications match known good/bad companies
4. Read diagnostics: which comparators are near threshold?
   → expected: r(x) vector identifies the decision boundaries
5. Execute Pass 3: tighten tolerances based on diagnostics
   → expected: re-run produces tighter sigma
6. Verify: domesticated variables identified, sigma tightening confirmed
   → expected: process terminates with locked adapter

---

## NEXT STEPS

| What | BAR | Status |
|------|-----|--------|
| Convert SVG insurance adapter from FCE → Math 2 format | — | TODO — first adapter to convert |
| Convert US equities adapter from FCE → Math 2 format | — | TODO — has 10 pending fixes from Round 3 |
| Convert storage adapter from FCE → Math 2 format | — | TODO |
| Update layer0-engine to execute P(x;θ) v3.0 | BAR-133 | TODO |
| Run first full three-pass cycle (insurance) | — | TODO — blocked by Math 2 conversion |
| Tournament validate first completed adapter | — | TODO — after three-pass cycle |

---

## THE THREE-PASS CYCLE (Quick Reference)

```
┌─────────────────────────────────────────────────────────┐
│ PASS 1: Math 2 → DEFINE                                 │
│   What is x? What do you measure? What do you accept?   │
│   → Draft adapter. 20-point checklist.                   │
├─────────────────────────────────────────────────────────┤
│ PASS 2: Math 1 → VALIDATE                               │
│   P(x;θ). Diagnostics r(x). Stability. Global gate.     │
│   → What broke? Where is sigma?                          │
├─────────────────────────────────────────────────────────┤
│ PASS 3: Math 2 → TIGHTEN                                │
│   Fix comparators. Adjust tolerances. Check coupling.    │
│   → Re-run checklist. Go back to Pass 2.                 │
├─────────────────────────────────────────────────────────┤
│ TERMINATE when:                                          │
│   No new constants + back-prop clean + domesticated      │
│   + sigma tightening + feasible region healthy            │
└─────────────────────────────────────────────────────────┘
```

---

## FILES

```
Barton-Processes/factory/000-adapter-build/
├── heir.yaml      # Identity
├── MANIFEST.md    # This file
├── OSAM.md        # Where to find the math docs and existing adapters
├── PRD.md         # Requirements for what a completed adapter looks like
└── (no src/ — this is a procedure, not code)
```

---

## SESSION LOG

| Date | Session | What Was Done | Brain Chunks |
|------|---------|---------------|-------------|
| 2026-03-25 | Process creation | Defined Process 000, heir.yaml + MANIFEST created. Adapter Build Process written in bedrock/. Math docs (M1 v3.0, M2 v1.2) added to bedrock/. | `session/2026-03-24-full-session-final`, `session/2026-03-24-end-of-day` |

**imo-brain documents:**
- `session/2026-03-24-full-session-final` (covers full architecture decisions)
- `session/2026-03-24-end-of-day` (covers BAR status and bedrock updates)

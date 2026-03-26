# PRD — Process 000: Domain Adapter Build
## Product Requirements — What a Completed Adapter Looks Like

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped requirements |
| **Last Updated** | 2026-03-25 |

---

## Purpose

Produce domain adapters that plug into the Tier 0 engine. Each adapter transforms a domain's raw data into comparator functions the engine can evaluate. The adapter IS the domain definition — without it, the engine has nothing to classify.

---

## Two-Question Intake

1. **"What triggers this?"** — A new domain needs Tier 0 classification. Someone says "I want to evaluate [companies / sectors / properties / anything] using the engine."
2. **"How do we get it?"** — Execute the three-pass cycle: Math 2 → Math 1 → Math 2. Use real domain data. Iterate until sigma tightens.

---

## Requirements

### R1: Adapter Identity
- Adapter name, domain, version, author, creation date, phase, locked set size
- **Acceptance:** All identity fields present and valid

### R2: Candidate Definition
- What is x? Where does x come from? How is x represented?
- Must be concrete — not "a thing" but "a company record with outreach_id, state, employee_count, DOL filing data"
- **Acceptance:** Any engineer can look at the candidate definition and know exactly what data to pull

### R3: Comparator Declaration
- Minimum 1 comparator per FCE column (Valuation, Concentration, Trend, Plumbing)
- Every comparator traces to exactly one axiom (Thing, Flow, Change)
- Every comparator satisfies all 4 requirements (measurable, deterministic, representation-invariant, temporally complete)
- Verification evidence: determinism test (3 runs), representation test (2 encodings), non-negativity test (10 samples)
- **Acceptance:** All comparators declared with full fields. Verification tests documented.

### R4: Tolerance Declaration
- Initial k_i for every comparator
- k_i ≥ ε_k (tolerance floor)
- Coupling declared for every k_i (independent? if no, which k_j and directionality)
- Bolt pattern sequence defined
- **Acceptance:** Tolerances declared, coupling documented, sequence justified

### R5: Transformation Declaration
- f(x) defined — what changes between evaluation cycles
- If f(x) = x, static-candidate justification provided
- **Acceptance:** Transformation is concrete, not abstract

### R6: Operational Parameters
- N_min, w, σ_max, α, δ, ε, ε_k, M_max all declared with numeric values
- Coherence rules satisfied (α ≤ 0.95, σ_max below Popoviciu bound, etc.)
- **Acceptance:** All parameters declared and within coherence bounds

### R7: 20-Point Checklist
- Math 2 Section A9 checklist completed
- All 20 checks pass
- **Acceptance:** Checklist signed off with evidence per check

### R8: Engine Validation (Pass 2)
- P(x;θ) computed on minimum 10 real candidates
- Diagnostic vector r(x) produced for each
- Stability verified across N_min cycles
- Global gate checked
- Sigma direction documented (tightening/flat/expanding)
- **Acceptance:** Classification results match domain expert expectations. Sigma tightening.

### R9: Calibration Complete (Pass 3)
- Broken comparators fixed or replaced
- Tolerances adjusted at failure boundaries
- Feasible region conditioned: vol(Θ)^(1/n) ≥ δ
- Re-run produces tighter sigma than prior pass
- **Acceptance:** Sigma tighter than Pass 2. No expanding sigma on any comparator.

### R10: Domestication
- Variables that can't change the outcome identified
- max(r(x)) ≤ α AND var(r_i(x)) ≤ σ_max for domesticated variables
- Analysis stops at domesticated variables — no infinite zooming
- **Acceptance:** Domesticated variables documented. Process terminates.

---

## Non-Requirements

- The adapter does NOT need to be implemented as code for this process to complete
- Tournament validation is recommended but not required for initial lock
- Production deployment is a separate process (wiring the adapter to real pipelines)
- AI/LLM involvement in classifications is out of scope — the engine is deterministic

---

## Definition of Done

All 10 requirements pass. The adapter document is complete in Math 2 format, stored at `domains/{domain-name}/adapter.md`, and produces correct binary classifications on real domain data with tightening sigma. The three-pass cycle has terminated (no new constants + back-propagation clean + domesticated).

---

## Output Artifacts

| Artifact | Location | What |
|----------|----------|------|
| Adapter document | `domains/{domain-name}/adapter.md` | Formal Math 2 adapter — the domain definition |
| Failure registry | `domains/{domain-name}/failure-registry.md` | Domain-specific failure tracking |
| Calibration log | `domains/{domain-name}/calibration/` | Diagnostic vectors and sigma history per pass |
| Tournament results | `domains/{domain-name}/tournament/` | If adversarial validation was run |

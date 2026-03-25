# CLAUDE.md — Process 000: Domain Adapter Build

## Governing Doctrine

**Before any work on this process, read and follow:**

1. `law/doctrine/FOUNDATIONAL_BEDROCK.md` — The engine (Three Primitives, C\&V, IMO, CTB, Circle, Troubleshooting Loop, Tier 0, Aviation Model)
2. `bedrock/math-01-engine.md` — P(x;θ) decision equation (FROZEN)
3. `bedrock/math-02-adapter-template.md` — Domain adapter interface

**Pre-flight (every session):**
- Two-Question Intake: "What triggers this?" and "How do we get it?"
- C\&V Test: Can you name it? Format it? → constant. The value filling it → variable.
- Four-Element Validation: IMO + CTB + Circle simultaneously
- Three Primitives: Thing (exists?), Flow (reaches?), Change (transforms correctly?)
- Determinism first. LLM is tail arbitration only.
- If something broke → Troubleshooting Loop (Bedrock §6). Do not patch. Do not guess.

---


## What This Process Does

The meta-process. Produces all domain adapters that plug into the Tier 0 mathematical engine. Not a pipeline, not a worker, not code. A **procedure** executed by humans + LLMs to define how a domain maps to the engine's comparator functions. Without a completed adapter, the engine has nothing to classify.

## How It Works

Three-pass cycle: Math 2 (Define) → Math 1 (Validate) → Math 2 (Tighten). Repeat until sigma tightens and all variables are domesticated.

1. **Pass 1 — Math 2 (Define):** Declare the candidate (what is x?), define comparators (what do you measure? — must trace to Thing/Flow/Change), set initial tolerances (will be wrong), define transformation (what changes between cycles), set operational parameters (N_min, sigma_max, alpha, delta, etc.), run 20-point validation checklist.
2. **Pass 2 — Math 1 (Validate):** Feed real candidates into `P(x;theta) = 1 if max_i[C_i(x)/k_i] <= 1`. Read diagnostic vector r(x) — which comparators broke and by how much. Run stability across N cycles. Check global consistency (back-propagation). Read sigma — tightening (real) / flat (phantom) / expanding (broken).
3. **Pass 3 — Math 2 (Tighten):** Fix broken comparators (remove useless, replace unstable). Adjust tolerances at failure boundaries. Check coupling — does changing k_i break k_j? Verify feasible region: `vol(Theta)^(1/n) >= delta`. Re-run 20-point checklist. Go back to Pass 2.

**Termination:** No new constants + back-propagation clean + domesticated + sigma tightening + feasible region healthy.

## Key Equations (from Math 1)

```
Decision:     P(x; theta) = 1  if  max_i [ C_i(x) / k_i ] <= 1  else 0
Diagnostics:  r(x) = [ C_1(x)/k_1, ..., C_n(x)/k_n ]
Stability:    forall t in [1..N]: P(f^t(x); theta) = 1
              AND var(r_i(x)) over [t-w..t] <= sigma_max
Global gate:  ACCEPT(x_new) = P(x_new; theta') = 1 AND forall x in L: P(x; theta') = 1
Feasibility:  theta' in Theta where vol(Theta)^(1/n) >= delta
Domesticate:  max(r(x)) <= alpha AND var(r_i(x)) <= sigma_max -> stop
```

## FCE Four Columns to Comparator Mapping

| FCE Column | Primitive | Comparator Type | Question |
|-----------|-----------|-----------------|----------|
| Valuation | Thing | C_val(x) | Is x priced right? |
| Concentration | Flow | C_conc(x) | Where is the herd? |
| Trend | Change | C_trend(x) | Is direction sustainable? |
| Liquidity/Plumbing | Connection | C_plumb(x) | Can the system execute? |

Each FCE column becomes one or more formal comparators in the Math 2 adapter. The column is the concept. The comparator is the measurement.

## Data Sources

This process does NOT own tables. It produces adapters that define what tables downstream pipelines read.

| Source | Location | Purpose |
|--------|----------|---------|
| Engine equation | `bedrock/math-01-engine.md` | P(x;theta) definition — FROZEN |
| Adapter template | `bedrock/math-02-adapter-template.md` | Section A (universal) + Section B (domain-specific) |
| Build procedure | `bedrock/ADAPTER_BUILD_PROCESS.md` | Step-by-step three-pass cycle |
| Concept docs 1-9 | `bedrock/doc-01` through `doc-09` | Three Primitives through FCE |
| FCE | `law/doctrine/FCE.md` | Applied engine — four columns, domain adapters |
| Domain knowledge | Per domain | Real data for engine validation |

## Tools

- **Claude Code / Claude AI** — LLM execution for comparator selection, diagnostic analysis
- **NotebookLM** — Research + content generation for domain knowledge
- **layer0-engine CF Worker** — Monte Carlo validation (when executing P(x;theta))

## Dependencies

| Direction | What | Status |
|-----------|------|--------|
| Upstream | Bedrock math docs (M1 v3.0, M2 v1.2) | LOCKED |
| Upstream | Concept docs 1-9 | LOCKED |
| Upstream | Domain knowledge + real data | Per domain |
| Downstream | Every domain pipeline | Adapter defines what the pipeline measures |
| Downstream | layer0-engine | Executes P(x;theta) using adapter-defined comparators |
| Downstream | Dashboard | Displays classifications and sigma tracking |

## Existing Adapters

| Domain | Location | Format | Math 2 Status |
|--------|----------|--------|---------------|
| SVG Insurance | `domains/svg-insurance/adapter.md` | FCE narrative | Not converted |
| US Equities | `domains/us-equities/adapter.md` | FCE narrative | Not converted (10 fixes pending) |
| Storage | `domains/storage/adapter.md` | FCE narrative | Not converted |

## Output Artifacts

| Artifact | Location |
|----------|----------|
| Adapter document | `domains/{domain-name}/adapter.md` |
| Failure registry | `domains/{domain-name}/failure-registry.md` |
| Calibration log | `domains/{domain-name}/calibration/` |
| Tournament results | `domains/{domain-name}/tournament/` |

## Acceptance Criteria

- Adapter passes Math 2 20-point checklist
- P(x;theta) produces correct classifications on real candidates
- Sigma tightens across calibration cycles
- Feasible region is healthy (not knife-edge)
- Remaining variables are domesticated
- Back-propagation clean — no prior constants broken

## Read Order Before Building Any Adapter

1. `bedrock/ADAPTER_BUILD_PROCESS.md` — the procedure
2. `bedrock/math-02-adapter-template.md` — the template
3. `bedrock/math-01-engine.md` — the engine
4. `bedrock/INDEX.md` — how concepts connect to math
5. `bedrock/doc-01` through `doc-09` — concept proofs
6. `law/doctrine/FCE.md` — applied engine

## Known Issues

| Issue | Resolution |
|-------|------------|
| All 3 existing adapters in FCE narrative format, not Math 2 | Need conversion — FCE narrative to formal Math 2 template |
| layer0-engine doesn't execute P(x;theta) v3.0 | Worker exists but predates v3.0 math |
| No adapter has completed the full three-pass cycle | First candidate: SVG insurance adapter |

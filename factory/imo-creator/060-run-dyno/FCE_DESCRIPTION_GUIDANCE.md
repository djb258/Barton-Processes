# FCE Description Guidance

**Purpose:** What you put in the domain description determines what the engine can do. This file tells you how to write one that the engine can actually use.

**Read this BEFORE filling in any FCE intake YAML.**

---

## What we're trying to do

The engine has one job: **find universal structure, then build on it.**

- **Find universal structure** = reduce your domain to the 3-primitive substrate (Thing / Flow / Change). Every domain in the world reduces here. That reduction is what the engine does — domain language strips away, substrate remains.
- **Build on it** = once the substrate is locked (K=C consensus on the foundation dictionary), assemble the customer-facing deliverable mechanically through us.py → K=C → up.py → Auditor. **DMJ does NOT run inside a single FCE run** — DMJ is a downstream convergence step that fires only when N≥2 K=C-certified FCEs exist in the same family (per `run-dyno.yaml` INV-18). At N=1, DMJ is deferred.

Your description is the input to both moves. **If you give the engine a description that doesn't enable both, the engine fails.**

| If your description is... | Then... |
|---|---|
| **Bad** (vague, jargon-heavy, no structure visible) | Engine can't find universal structure. No foundation locks. Build can't start. |
| **Too narrow** (pre-defines the method / solution / technique) | Engine has nothing to discover. You've stolen its job — done badly, with operator bias instead of substrate decomposition. |
| **Good** (substantive, structural, method open) | Engine finds universal structure. Foundation locks. Build proceeds mechanically. |

Without your good description, **the engine cannot do its job.** Not because it's weak — because you didn't give it what it needs. The rules below exist to keep you in the right zone so the engine can do what only it can do: find the substrate and build from there.

---

## You're providing the VARIABLE — everything else is constant

In `I = M + O` terms:

| Part | Status | What it is |
|---|---|---|
| **M** (engine + doctrine) | **LOCKED — constant** | 17 locked constants. Sealed engine internals (us.py / K=C / up.py / DMJ). Role-locked Planner / Foreman / Mechanic / Auditor. The 3 primitives. The 10-piece stack. **None of these change per build.** |
| **O** (the deliverable) | **Output — derived** | What the engine produces. You don't write it; you receive it. |
| **I** (your description) | **VARIABLE** | The only thing that changes per build. The only thing you actually contribute. |

**Your one job per build: provide a good variable.**

The locked constants — the engine, the doctrine, the role-locked agents — are doing 99% of the work. You're providing the 1% that's actually variable. Get that 1% right, and the 99% runs mechanically.

Get the variable wrong, and the 99% has nothing to operate on.

A **good variable** feeds the locked constants the structural material they need.
A **bad variable** starves them.

**Your description IS the variable. Treat it accordingly. The rest of this document is how to write a good one.**

---

## What you're doing

You're handing the engine a domain to **reduce to substrate primitives** (Thing / Flow / Change). The engine strips your domain language and operates on structure. Your description is the input to that reduction.

A thin or jargon-heavy description gives the engine garbage to work with. A description that surfaces structure cleanly accelerates the whole pipeline.

---

## Scope: the Goldilocks zone

You're providing the **I (input)**. The engine's job is to discover the **M (middle — how primitives decompose, how the system actually works)**. The **O (output)** emerges from M.

**Two failure modes bracket the zone:**

| Scope | Example | What breaks |
|---|---|---|
| **Too broad** | `"Computer programming"` | No structure visible → K=C has nothing to inversion-test → engine can't decompose |
| **Too narrow (defines M)** | `"Build a Python script using regex to parse insurance applications and route to underwriters based on risk threshold"` | Operator pre-baked the solution → engine has nothing to find → just executes operator's bias |
| **Right zone** | Domain with Things / Flows / Changes visible, intent stated separately, method NOT specified | Engine discovers the M |

**Test before submitting:** If your description tells the engine HOW to solve, it's too narrow. If it doesn't expose Things / Flows / Changes, it's too broad. Right zone exposes WHAT is there, leaves HOW to the engine.

---

## What the Planner WON'T do for you

The Planner is a **gate**, not a fixer. Critical to understand:

- ❌ Planner will NOT enumerate primitives for you
- ❌ Planner will NOT decompose your domain for you
- ❌ Planner will NOT suggest improvements to your description
- ❌ Planner will NOT generate a "richer" version of what you wrote
- ✅ Planner WILL return PASS or FAIL with reasons

**Why:** Decomposition is the engine's job. If the Planner did it, the engine would have nothing left to discover. The Planner stays in lane (gate only). The engine stays in lane (decomposition + assembly). Each role is locked.

You own the description quality. If it FAILs, you fix it and re-submit. The Planner won't do your work for you, and neither will the engine downstream — the engine processes what it's given.

**The Planner IS the Four-Brain Planner role, specialized for FCE intake.** Same role-lock contract (cannot touch after dispatch), same gate-not-solver ethos, same governance-lens approach (BS Law applied here as substrate-awareness checklist). Specialized for tactical per-intake scope using Sonnet; the canonical strategic Four-Brain Planner (Opus 4.7) operates one altitude up at the BAR level. See `atlas/constants/FOUR_BRAIN_AVIATION.md` (locked constant #16) and `atlas/FOUR_BRAIN_ROUTING.md` for the canonical role definitions and lock contract.

---

## The five rules

### 1. Lead with structure, not jargon

The engine ultimately wants to see, for any domain:

- What **Things** exist? (entities, components, artifacts that have to be present)
- What **Flows** connect them? (movements, transfers, signals, sequences)
- What **Changes** transform state? (transitions, conversions, outcomes)

Domain vocabulary is fine. Structure must be visible underneath it.

### 2. State the intent SEPARATELY from the domain

The intake has two fields:
- `domain_string` = what's being decomposed
- `p1_definition` = what you want the engine to find

Don't braid them. The domain describes structure. The intent describes the operator's goal.

### 3. Don't pre-define the M (the method/solution)

The engine's whole job is finding the Middle. If your description carries the method/technique/solution, you've stolen the engine's job. The engine has nothing to discover; it just executes your bias.

**Describe what's there, not what should happen, and definitely not how to do it.**

### 4. Don't smuggle "Connection" as a primitive

There are **3 primitives**, not 4. Thing, Flow, Change.

Connection appears only as an FCE output column (Liquidity / Plumbing). It is **not** a substrate primitive.

### 5. Make it substantive

Single-word domains are too thin for K=C consensus. Three expensive models need enough material to inversion-test independently.

If you can't describe the domain in 3-5 sentences with structure visible, you don't understand the domain well enough to feed it to the engine yet.

---

## Pre-flight checklist

Before submitting an FCE intake:

- [ ] **Things named** (what exists in this domain)
- [ ] **Flows named** (what moves between the Things)
- [ ] **Changes named** (what transforms state)
- [ ] **Intent stated separately** in `p1_definition` (not braided into the domain)
- [ ] **No solutions pre-loaded** (description is descriptive, not prescriptive)
- [ ] **No method/technique pre-defined** (you didn't tell the engine HOW to solve)
- [ ] **No "Connection" as a 4th primitive** (3 primitives only)
- [ ] **Substantive** (not a single word; 3-5 sentences with structure visible)

---

## Worked examples

### ❌ Examples that FAIL

#### Too broad
```yaml
domain_string: "Computer programming"
```
**Why it fails:** Single concept, no structure visible. Three expensive K=C models have no Thing / Flow / Change to inversion-test. K=C verdict will be SPLIT or INSUFFICIENT every row.

#### Too narrow — defines M
```yaml
domain_string: "Insurance underwriting — build a Python script using regex to parse PDF applications, classify risk via gradient boosting on prior loss data, and route to underwriters whose specialty matches risk class"
```
**Why it fails:** Method (Python, regex, gradient boosting), solution architecture (script + classifier + router), and outcome (routing rule) are all pre-baked into the description. The engine has no Middle to discover. us.py would output a structure that's 90% reflection of the operator's bias and 10% actual domain decomposition.

#### Solution-loaded
```yaml
domain_string: "How to reduce underwriting processing time by 50% through automation"
```
**Why it fails:** The "how to" framing pre-supposes a solution direction (automation). The "50%" pre-supposes a target. The engine should DISCOVER where time leaks structurally, not be told to find automation opportunities.

#### Jargon-heavy / no structure underneath
```yaml
domain_string: "Optimize the customer journey through omnichannel touchpoints with personalized engagement orchestration leveraging next-best-action AI"
```
**Why it fails:** Every word is jargon. Where are the Things? The Flows? The Changes? K=C consensus can't strip this to substrate because there's no substrate visible. Operator clearly doesn't understand the domain at structural level.

#### Connection-as-primitive
```yaml
domain_string: "Sales process — accounts (Things), pipeline movement (Flow), close events (Change), and account-to-pipeline connections (Connection) drive revenue"
```
**Why it fails:** Connection listed as a 4th primitive. There are 3 primitives. Connections between Things ARE Flows. The operator is doctrinally wrong, and the K=C audit would flag it.

---

### ✅ Examples that PASS

#### Insurance underwriting
```yaml
domain_string: "Insurance underwriting — applicants submit applications containing risk-relevant data, underwriters evaluate applications against policy criteria and prior loss patterns, applications transition between submitted / under-review / approved / declined / conditional states, premiums get calculated based on final risk classification, policies issue or get rejected"
p1_definition: "Identify the structural bottlenecks that drive end-to-end processing time"
```
**Why it works:** Things named (applicants, applications, underwriters, premiums, policies). Flows named (submission, evaluation, calculation, issuance). Changes named (state transitions across submitted → approved/declined/conditional). Method NOT specified. Intent in `p1_definition`, not braided. K=C has plenty of structure to inversion-test.

---

#### Storage container go/no-go
```yaml
domain_string: "Storage container go/no-go decision — applicants submit container specs and lease history, evaluators assess specs against site requirements and historical performance, decisions transition through pending / under-review / GO / NO-GO / CONDITIONAL states, lease terms get calculated from final decision class, contracts issue or applications close"
p1_definition: "Find the structural patterns that distinguish GO outcomes from NO-GO outcomes across past decisions"
```
**Why it works:** Mirrors insurance underwriting structurally — and that's the point. The engine will recognize the structural similarity at K=C, enabling JOIN with insurance domain. Method not specified. Intent separate.

---

#### Real estate leasing
```yaml
domain_string: "Commercial real estate leasing — landlords list available properties with terms, tenants submit applications with use case and creditworthiness, brokers facilitate negotiations between parties, applications transition through interest / submitted / negotiating / leased / declined states, lease contracts execute or applications dissolve"
p1_definition: "Identify what structurally drives application-to-lease conversion across property types"
```
**Why it works:** Three-party structure (landlords, tenants, brokers) makes Things explicit. Flows visible (submission, negotiation, execution). Changes visible (state transitions). Intent named separately. Engine free to discover where conversion friction structurally lives.

---

#### Worker debugging
```yaml
domain_string: "CF Worker debugging — operators deploy workers to Cloudflare endpoints, requests reach workers via routes, workers handle requests by reading config / calling bindings / mutating state / returning responses, error states transition between healthy / degraded / failing / dead, logs and error tables capture state transitions, operators diagnose by reading logs and inspecting bindings"
p1_definition: "Find the structural failure modes that account for >80% of worker outages"
```
**Why it works:** Technical domain reduced to substrate cleanly. Things (workers, requests, bindings, logs). Flows (request routing, binding calls, state mutation). Changes (health state transitions). Method (how to fix) NOT specified.

---

#### Customer onboarding (cross-domain)
```yaml
domain_string: "Customer onboarding for B2B SaaS — prospects submit signup forms with company info, sales reps qualify leads by checking company fit, qualified prospects move to demo where they see product capabilities, demos transition prospects to pilot / declined / nurture states, pilots convert to paid customers or expire, paying customers receive ongoing support"
p1_definition: "Discover the structural pattern in pilots that convert vs pilots that expire"
```
**Why it works:** Multi-stage funnel made structurally visible. Things (prospects, sales reps, demos, pilots, customers). Flows (qualification, demo, pilot conversion). Changes (state transitions across the funnel). Engine can JOIN this to other funnel-shaped domains via shared substrate.

---

## What you'll notice across the good examples

1. **Same structural pattern repeats:** entity submits something → evaluator processes → state transitions → outcome emerges. Different domain fill, identical primitive structure. **That's why the engine is domain-agnostic — and why JOIN works across these domains at the foundation.**

2. **None pre-define the method.** None say "use AI", "build a workflow", "automate via", "optimize with". Method is the engine's job.

3. **Each one's `p1_definition` is a discovery question.** "Identify the structural bottlenecks", "Find the patterns that distinguish", "Discover the structural pattern". The operator wants the engine to find something — they don't pre-say what it'll find.

4. **3-5 sentences each, structure visible underneath domain language.** Substantive but not over-prescriptive. Goldilocks zone.

---

## Why this matters operationally

A single FCE run executes us.py → K=C → up.py → Auditor. **DMJ is a separate downstream step that fires only at N≥2 same family** (see `run-dyno.yaml` INV-18, sovereign-confirmed 2026-05-08). Every stage that does run inside a single FCE depends on the description. Specifically:

- **us.py** decomposes the description into layers. A thin description = thin decomposition. A solution-loaded description = decomposition follows the operator's bias instead of the actual domain structure.
- **K=C** runs 3-model consensus on each constant's description against the inversion test (Thing/Flow/Change). A description that doesn't surface structure forces K=C to guess. A description that pre-defines M doesn't give K=C real constants to test.
- **up.py** consumes variables through the locked structure. A weak structure means weak interior assembly. A pre-baked structure means up.py just renders the operator's bias.
- **Downstream DMJ JOIN** (when it eventually fires at N≥2) matches against the foundation dictionary. Bad foundation = bad joins. JOIN works specifically because every domain shares the same primitive substrate — pre-defining M corrupts that. The description quality at intake determines whether this future DMJ has clean inputs to converge.

Garbage in propagates through every stage. **The intake is where quality is set. The Planner gate exists to prevent garbage from entering.**

---

## Anti-patterns (don't do these)

- Single-word domains
- Solution-loaded descriptions ("how to fix X", "how to reduce Y", "how to optimize Z")
- Method-loaded descriptions ("build a script that", "use ML to", "automate with")
- Connection-as-primitive lists (4 primitives — wrong)
- Mixing intent into domain
- Domains spanning multiple altitudes in one description
- Vague abstractions ("the future of work", "innovation", "transformation")
- Describing what the operator wants to find rather than what's there
- Jargon-heavy descriptions with no structure visible underneath

---

## If the description is right

The engine takes a substantive structural description, strips the domain jargon at K=C, and reduces to the 3-primitive substrate. From there the rest of the 10-piece stack runs mechanically.

Your job: give the engine enough structural material to reduce — and then **get out of its way**.

The engine handles the rest.

---

**Lives in:**
- `dyno-engine/FCE_DESCRIPTION_GUIDANCE.md`
- `Barton-Processes/factory/imo-creator/060-run-dyno/FCE_DESCRIPTION_GUIDANCE.md`

**Companion specs:**
- `dyno-engine/PLANNER_GATE_BUILD_SPEC.yaml` — the Planner agent design that enforces this
- `imo-creator-v2/UNIVERSAL_BUILD_STACK.md` — the full 10-piece architecture

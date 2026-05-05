# FCE Computer Programming

**Status:** K=C-certified-awaiting-join | **Version:** 1.0.0 | **Last Modified:** 2026-05-04
**Sovereign ID:** `a8f6980a-880c-4667-a3dd-e9497fa693cc`
**Family:** programming
**ctb_node:** `barton-enterprises/imo-creator/lucy/fce/computer-programming`

The first FCE in the programming-substrate family. Defines the universal vocabulary for decomposing any program in any language to ten primitive constants.

---

## §1 Identity

| Field | Value |
|-------|-------|
| FCE ID | `computer-programming` |
| Name | FCE Computer Programming |
| Family | programming |
| Sovereign ID | `a8f6980a-880c-4667-a3dd-e9497fa693cc` |
| Version | 1.0.0 |
| Status | K=C-certified-awaiting-join |
| Owner | Dave Barton |
| Companion YAML | `atlas/fce-library/computer-programming/computer-programming.yaml` |

## §2 Domain (the I)

```
computer programming — The systematic act of writing executable instructions for a computer
— building software from scratch using a programming language. Decompose to find the constants
that hold across any program in any language for any purpose.
```

Em-dash separator: short topic + scope-defining description, single string per locked doctrine.

## §3 P=1 Definition (the O)

**Process 1 (US discover):** All leaves at primitive (Thing/Flow/Change). Structure fully decomposed.

**Process 4 (UP solve):** P=1 when three diverse reference programs decomposed to the recipe steps have every construct mapping to exactly one of the 10 primitives, with zero external concepts introduced and zero remainder. Reference programs: Hello World (Python), FizzBuzz (Rust), Bubble Sort (Haskell).

## §4 Locked M — The 10 K=C-Certified Primitives

| # | Constant | Primitive | K=C Verdict |
|---|----------|-----------|-------------|
| 1 | Source Code | Thing | 3/3 MATCH |
| 2 | State Transition | Change | 3/3 corrected from Flow |
| 3 | Compiler | Change | 2/3 majority corrected from Thing |
| 4 | Execution Flow | Flow | 3/3 MATCH |
| 5 | Operand | Thing | 3/3 MATCH |
| 6 | Operator | Thing | 3/3 corrected from Change |
| 7 | Primitive Type | Thing | 3/3 MATCH |
| 8 | Scope | Thing | 3/3 MATCH |
| 9 | Interface | Flow | 2/3 majority MATCH |
| 10 | Encapsulation | Thing | 3/3 corrected from Change |

**Distribution:** 6 Things / 2 Flows / 2 Changes.

## §5 K=C Audit Trail

- **Round 1:** 7 MATCH / 3 MISMATCH / 0 SPLIT (each MISMATCH 3/3 against engine claim)
- **Round 2 (after corrections):** 9 MATCH / 1 MISMATCH (Compiler Thing→Change 2/3 majority)
- **Final M source of truth:** `engine-final-locked-v2.json` (in R2 us-discover/ subdir, also locally in `atlas/dyno/runs/discover-computer-programming--the-systematic-act/`)

## §6 Process Status

| Process | Engine | Status | Notes |
|---------|--------|--------|-------|
| 1 — US Discover | `dyno_engine.py discover` | ✅ COMPLETE | 7 cycles, sigma=no_overlap, vars=0, max ratio 0.70 |
| 2 — K=C Audit | `kc_audit_consensus()` | ✅ COMPLETE | 2 rounds, 9/10 MATCH, Compiler 2/3 majority correction applied |
| 3 — DMJ | (deferred — N=1) | ⏸ DEFERRED | Awaiting next FCE in family. Per locked doctrine: DMJ requires ≥2 K=C-certified FCEs + global rebuild not pairwise |
| 4 — UP Solve | `dyno_engine.py solve` | ✅ COMPLETE | 6 cycles, sigma=no_overlap, vars=0, max ratio 0.67. 3-model recipe consensus P=1 |

## §7 Round-Trip Validation Result

**3/3 expensive-model consensus on P=1.** Every construct in Hello World (Python), FizzBuzz (Rust), and Bubble Sort (Haskell) traces to exactly one of the 10 primitives. Zero remainder, zero external concepts.

| Model | Recipe verdict |
|-------|----------------|
| claude-opus-4-6 | P=1 — diagnostic vector [1,1,1,1,1,1,1,1,1,1] |
| gemini-2.5-pro-preview | P=1 — primitive set necessary AND sufficient |
| gpt-4o | P=1 — comprehensive coverage, all constructs aligned |

## §8 Locations (Persistence Trace)

| Layer | Path |
|-------|------|
| R2 base | `r2://svg-files/dyno-runs/a8f6980a-880c-4667-a3dd-e9497fa693cc/` |
| R2 us-discover | `r2://svg-files/dyno-runs/a8f6980a-880c-4667-a3dd-e9497fa693cc/us-discover/` |
| R2 kc-audit | `r2://svg-files/dyno-runs/a8f6980a-880c-4667-a3dd-e9497fa693cc/kc-audit/` |
| R2 up-solve | `r2://svg-files/dyno-runs/a8f6980a-880c-4667-a3dd-e9497fa693cc/up-solve/` |
| R2 manifest | `r2://svg-files/dyno-runs/a8f6980a-880c-4667-a3dd-e9497fa693cc/manifest.json` |
| D1 row | `mission-control.dyno_run` WHERE `run_id = 'a8f6980a-880c-4667-a3dd-e9497fa693cc'` |
| MD doc (this file) | `atlas/fce-library/computer-programming/computer-programming.md` |
| YAML manifest | `atlas/fce-library/computer-programming/computer-programming.yaml` |
| Mirror — private dyno repo | `djb258/dyno-engine: fce-library/computer-programming/` |
| Mirror — Barton-Processes | `factory/imo-creator/090-fce-computer-programming/` |

## §9 Cost + Cycles

- Total OpenRouter cost: **$1.07** (engine cycles + recipe synthesis + K=C audit)
- Total cycles: **13** (US: 7, UP: 6)
- Models used (this run): 3 expensive (claude-opus-4-6, gemini-2.5-pro-preview, gpt-4o) + 3 cheap (haiku, flash, llama) — cheap-tier was active during cycles 4+ before the expensive-only doctrine lock landed mid-session

## §10 The Universal Program-Writing Recipe

The 10 primitives compose into a 10-step recipe applicable to any program in any language. Each step uses exactly one primitive.

| Step | Decision | Primitive | Rationale |
|------|----------|-----------|-----------|
| 1 | Choose the source file and language target | Source Code (Thing) | Every program begins as a text file containing instructions. |
| 2 | Define the data types needed | Primitive Type (Thing) | Selects the basic types (int, string, bool, char) that represent program information. |
| 3 | Declare operands (variables, literals, constants) | Operand (Thing) | Concrete data values the program will manipulate. |
| 4 | Establish scopes (modules, functions, blocks) | Scope (Thing) | Delineates regions where names are valid; structures the namespace. |
| 5 | Define interfaces (function signatures, module contracts, I/O boundaries) | Interface (Flow) | Contracts specifying how components communicate. |
| 6 | Bundle data and behavior into units (functions, structs, classes, closures) | Encapsulation (Thing) | Groups related data and operations into self-contained units. |
| 7 | Select operators (arithmetic, logical, control, custom) | Operator (Thing) | Specific instructions that act on operands. |
| 8 | Arrange execution flow (sequencing, branching, looping, recursion) | Execution Flow (Flow) | Orders instructions into the sequence the machine follows. |
| 9 | Specify state transitions (assignments, mutations, accumulator updates) | State Transition (Change) | Each point where program state changes. |
| 10 | Translate to executable form (compile/interpret) | Compiler (Change) | Translates source text into runnable instructions. |

Full per-program decomposition tables (Hello World/Python, FizzBuzz/Rust, Bubble Sort/Haskell) are in the companion YAML `round_trip_validation` block.

## §11 What This Unlocks

**Standalone uses (this FCE alone):**
- Code review by primitive trace — every line/construct traces to one of the 10
- Cross-language teaching — same recipe steps, different language fill
- Code-generator alignment — demand LLM-written code cite the primitive per construct
- Library audit fingerprinting via primitive ratio
- Doctrine baseline for future workers/scripts to declare primitive trace

**When joined to family (post-DMJ, requires ≥2 FCEs):**
- Universal computing substrate (after Schemas + APIs + SQL + State + Errors land)
- DMJ master rebuild produces hub-and-spoke geometry (likely CP as hub)
- Universal system decomposition for any software system
- Primitive-trace bug taxonomy
- Cross-system migration as primitive remap

## §12 Audit + Doctrine References

- LBB master index for this FCE: see `atlas/manifests/fce-registry.yaml` § audit_trail
- Comprehensive session record: LBB record `3df7cdd9-fe49-4681-b3d7-541adc5113ac`
- Locked doctrines applied:
  - R2 active workbench / D1 post-completion vault — LBB `3c622b0e`
  - K=C 2/3 majority threshold — LBB `efa2f707`
  - DMJ requires ≥2 FCEs + global rebuild — LBB `872c142d`
  - Expensive-models-only — LBB `465c7faa`
  - up.py modification record — LBB `05d6555e`
- Companion YAML manifest: `atlas/fce-library/computer-programming/computer-programming.yaml`
- Companion runbook: `atlas/FCE_LIFECYCLE_RUNBOOK.md`
- Engine spec: `atlas/manifests/dyno-vault.yaml` + `atlas/DYNO_VAULT_SPEC.md`
- FCE Lifecycle doctrine: `factory/agents/up/FCE_LIFECYCLE.md`

## §13 Document Control

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Last Modified | 2026-05-04 |
| Status | BUILD |
| Authority | dyno-orchestrator-fired (retroactively scaffolded) |
| BAR Reference | FCE Computer Programming test fire 2026-05-04 |
| Parity zone fields (match against companion YAML) | version, last_modified, sovereign_id, n_primitives |

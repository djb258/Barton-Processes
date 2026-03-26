# CLAUDE.md — Process 600: BIT Scoring

## Governing Doctrine

**Before any work on this process, read and follow:**

1. `law/doctrine/FOUNDATIONAL_BEDROCK.md` — The engine (Three Primitives, C&V, IMO, CTB, Circle, Troubleshooting Loop, Tier 0, Aviation Model)
2. `bedrock/math-01-engine.md` — P(x;θ) decision equation (FROZEN)
3. `bedrock/math-02-adapter-template.md` — Domain adapter interface

**Pre-flight (every session):**
- Two-Question Intake: "What triggers this?" and "How do we get it?"
- C&V Test: Can you name it? Format it? → constant. The value filling it → variable.
- Four-Element Validation: IMO + CTB + Circle simultaneously
- Three Primitives: Thing (exists?), Flow (reaches?), Change (transforms correctly?)
- Determinism first. LLM is tail arbitration only.
- If something broke → Troubleshooting Loop (Bedrock §6). Do not patch. Do not guess.

---

## STATUS: RETIRED (2026-03-25)

This process is retired. Do not build, deploy, or reference BIT scoring.

BIT scoring was removed from the compiler (compiler-v2.ts), the simulation engine (simulate.ts), and the process registry. The `outreach_bit_scores` table in D1 is deprecated.

Intelligence tier determination is now based on data completeness (DOL filing presence, people slot fill rate, signal category) without a composite BIT score.

## What It Was

Composite scoring system that combined sub-hub data points into a single 0-100 score per company. Used to prioritize outreach. Replaced by direct data completeness checks in the LCS compiler's intelligence tier logic.

## Why It Was Retired

The score was a variable masquerading as a constant. The individual data points (DOL filing present, slots filled, signal type) are more useful to the compiler than a composite number that hides which inputs changed.

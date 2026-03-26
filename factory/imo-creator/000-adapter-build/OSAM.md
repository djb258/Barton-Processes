# OSAM — Process 000: Domain Adapter Build
## Semantic Access Map — WHERE to Find Everything

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — process-scoped access map |
| **Last Updated** | 2026-03-25 |

---

## Rule

**BEFORE BUILDING ANY ADAPTER, READ THESE FILES IN THIS ORDER.**

---

## Source Documents (Read Order)

| # | File | Location | What It Is |
|---|------|----------|-----------|
| 1 | ADAPTER_BUILD_PROCESS.md | `bedrock/` | The procedure — three-pass cycle (Math 2 → Math 1 → Math 2) |
| 2 | math-02-adapter-template.md | `bedrock/` | The template — Section A (universal) + Section B (domain-specific) |
| 3 | math-01-engine.md | `bedrock/` | The engine — P(x;θ), comparator requirements, stability, global gate |
| 4 | INDEX.md | `bedrock/` | The map — how concepts connect to math |
| 5 | doc-01 through doc-09 | `bedrock/` | The concept proofs — Three Primitives through FCE |
| 6 | FCE.md | `law/doctrine/` | The applied engine — four columns, domain adapter model |

---

## Existing Adapters (Current State)

| Domain | Location | Format | Math 2 Status |
|--------|----------|--------|---------------|
| SVG Insurance | `domains/svg-insurance/adapter.md` | FCE narrative | Not converted |
| US Equities | `domains/us-equities/adapter.md` | FCE narrative | Not converted (10 fixes pending from Round 3) |
| Storage | `domains/storage/adapter.md` | FCE narrative | Not converted |
| IT | `domains/it/` | Rosetta Stone vocabulary | Not applicable (infrastructure, not competitive allocation) |

---

## Where Completed Adapters Go

```
domains/{domain-name}/
├── adapter.md           ← The formal Math 2 adapter (output of this process)
├── failure-registry.md  ← Domain-specific failure tracking
└── tournament/          ← Tournament results if adversarial validation was run
```

---

## Key Equations (from Math 1)

```
Decision:     P(x; θ) = 1  if  max_i [ C_i(x) / k_i ] ≤ 1  else 0
Diagnostics:  r(x) = [ C_1(x)/k_1, ..., C_n(x)/k_n ]
Stability:    ∀ t ∈ [1..N]: P(f^t(x); θ) = 1
              AND var(r_i(x)) over [t-w..t] ≤ σ_max
Global gate:  ACCEPT(x_new) = P(x_new; θ') = 1 AND ∀ x ∈ L: P(x; θ') = 1
Feasibility:  θ' ∈ Θ where vol(Θ)^(1/n) ≥ δ
Domesticate:  max(r(x)) ≤ α AND var(r_i(x)) ≤ σ_max → stop
```

---

## FCE Four Columns → Math 2 Comparator Mapping

| FCE Column | Primitive | Math 2 Comparator Type | Question |
|-----------|-----------|----------------------|----------|
| Valuation | Thing | Is x priced right? | C_val(x) |
| Concentration | Flow | Where is the herd? | C_conc(x) |
| Trend | Change | Is direction sustainable? | C_trend(x) |
| Liquidity/Plumbing | Connection | Can the system execute? | C_plumb(x) |

Each FCE column becomes one or more formal comparators in the Math 2 adapter. The column is the concept. The comparator is the measurement.

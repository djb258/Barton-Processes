# DOCTRINE - Process 300 Blog Worker
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-300-01 | Monthly sitemap scan must be compared to a previous snapshot before any movement signal is emitted. | heir.yaml `acceptance_criteria[0]` | §8 stop |
| D-300-02 | Movement output per company is binary: 0 (no new content) or 1 (movement detected) — no partial values. | heir.yaml `movement_detection.output` | §8 stop |
| D-300-03 | AI classification is invoked ONLY on companies where movement=1; static (0) companies must never trigger AI. | heir.yaml `acceptance_criteria[2]` + CLAUDE.md "AI is used ONLY for classification on companies where movement=1" | §8 stop |
| D-300-04 | Errors must write to the master error table (D1); silent failure is forbidden. | heir.yaml `acceptance_criteria[3]` | §9b gauge |
| D-300-05 | AI is the tail, not the spine — detection itself must be deterministic; AI reads content and tags signal type only. | CLAUDE.md "AI classification is the TAIL, not the spine" | pre-flight |
| D-300-06 | CAPTCHA rate exceeding 10% is a hard halt; the process must stop and investigate proxy configuration. | PROCESS.md §7 Stop Conditions | §8 stop |
| D-300-07 | Error rate exceeding 5% is a hard halt. | PROCESS.md §7 Stop Conditions | §8 stop |
| D-300-08 | Proxy cost exceeding $100 per run is a hard halt — indicates a loop or bandwidth leak. | PROCESS.md §7 Stop Conditions | §8 stop |
| D-300-09 | D1 write failures exceeding 1% are a hard halt; batch must be chunked smaller. | PROCESS.md §7 Stop Conditions | §8 stop |
| D-300-10 | Process 300 must run before Process 200; running 200 before 300 is a forbidden path. | PROCESS.md §5 Forbidden Paths "Run 200 before 300" | pre-flight |
| D-300-11 | Neon vault is read-only at startup; no writes to Neon during the work phase — CQRS rule. | PROCESS.md §5 Forbidden Paths "Write directly to Neon" | §8 stop |
| D-300-12 | DataImpulse proxy must use sticky session ports (11000+) with at minimum a 40-port gap between workers; rotating proxy ports are forbidden. | PROCESS.md §5 Forbidden Paths + §11 Run 1 learnings (FP-301) | §8 stop |
| D-300-13 | Same failure pattern appearing three times triggers Troubleshoot/Train and an Airworthiness Directive; a third patch repair is forbidden. | PROCESS.md §7 Strike Rules | §8 stop |

## Cross-references
- UT §7 Constants & Variables references these rules by ID
- UT §8 Stop Conditions cites the violations that halt
- §9b Live Verification gauges measure compliance where measurable

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-28 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes - only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |

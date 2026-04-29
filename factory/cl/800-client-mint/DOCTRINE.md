# DOCTRINE — Process 800 Client Mint
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-800-01 | A client_id is minted from a CL sovereign_id — the flow is one-way: sovereign → client; no client record may exist without a valid sovereign_id in cl.company_identity. | heir.yaml acceptance_criteria[0] + PROCESS.md §3 Step 2-3 | §8 stop |
| D-800-02 | Duplicate sovereign_id detection is mandatory before any insert — if sovereign_id already exists in D1 client table, halt with DUPLICATE_SOVEREIGN and return the existing client_id. | heir.yaml acceptance_criteria[5] + PROCESS.md §7 | §8 stop |
| D-800-03 | client_id is generated at mint time via crypto.randomUUID() — one per sovereign_id, never reused, never recycled. | PROCESS.md §6 Constants + src/mint.ts | §8 stop |
| D-800-04 | The cl.* Neon schema is READ ONLY for this process — this process never writes upstream to CL tables. | PROCESS.md §5 Forbidden Paths | §8 stop |
| D-800-05 | Vault promotion to Neon clnt.client is a deliberate, separate step — auto-promotion is forbidden; vault writes are triggered only by explicit POST /vault. | PROCESS.md §5 Forbidden Paths + CLAUDE.md Databases | §8 stop |
| D-800-06 | Every failure must write a record to D1 client_error — skipping the error table is forbidden; no log means the fix cannot be traced. | heir.yaml acceptance_criteria[4] + PROCESS.md §5 Write Access | §9b gauge |
| D-800-07 | Process 800 is triggered by manual HTTP POST only — no cron, no automated runs; the trigger is always a human-initiated sovereign_id. | PROCESS.md §1 + CLAUDE.md Worker Config | §8 stop |
| D-800-08 | D1 is the working layer; Neon clnt.* is the vault (canonical) layer — the SEED-WORK-PUSH lifecycle applies; D1 is transient, Neon is permanent. | PROCESS.md §6 Constants + CLAUDE.md Databases | pre-flight |
| D-800-09 | This process triggers process 810 Client Intake — no 810 intake can begin until a client_id exists in the D1 client table. | heir.yaml feeds[810] + PROCESS.md §8 Downstream | §9b gauge |
| D-800-10 | Neon cl.company_identity is the sole source of sovereign company identity — minting without successfully reading the source record is forbidden (SOVEREIGN_NOT_FOUND halts). | PROCESS.md §7 Stop Conditions + src/mint.ts | §8 stop |

## Cross-references
- UT §7 Constants & Variables references these rules by ID
- UT §8 Stop Conditions cites the violations that halt
- §9b Live Verification gauges measure compliance where measurable

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-29 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes - only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |

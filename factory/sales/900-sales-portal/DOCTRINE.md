# DOCTRINE - Process 900 Sales Portal
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-900-01 | The four-meeting sequence is fixed and non-negotiable: Meeting 1 (Fact Finder) → Meeting 2 (Insurance/Monte Carlo) → Meeting 3 (Systems Demo) → Meeting 4 (Financials/Quote); no meeting may be served out of order and no meeting may be skipped. | PROCESS.md §Stop Conditions + CLAUDE.md §Sales phase progression | §8 stop |
| D-900-02 | Meeting 1 is the only read-write gate: it pulls live outreach intelligence from all five Neon sub-hubs (outreach_contacts, outreach_companies, email_discovery, linkedin_discovery, bit_scoring) into the outreach_snapshot table and accepts Fact Finder form submission; all subsequent meetings are read-only presentation layers. | CLAUDE.md §How it works + PROCESS.md §OSAM Write Rules | §8 stop |
| D-900-03 | The Monte Carlo simulation output must be computed and rendered before Meeting 2 may be marked complete; Meeting 3 cannot open until Meeting 2's insurance strategy selection and Monte Carlo result are both written to the D1 canonical tables. | CLAUDE.md §Known Issues (Monte Carlo not yet built) + TABLES-AUDIT.md Gap 3 | §9b gauge |
| D-900-04 | Process 900 close (status = closed_won or closed_lost in sales_state) is the required trigger for Process 800 (Client Mint); no client provisioning may begin until sales_state.status reaches a terminal value. | PROCESS.md §Dependencies + CLAUDE.md §How it works | §8 stop |
| D-900-05 | Sales close (closed_won) must execute a sovereign_id transition: the prospect's sovereign_ref in the outreach silo is promoted to a client sovereign_ref in the client silo; this join is the structural bridge between Process 900 and Process 800/810. | CLAUDE.md §Identity + PROCESS.md §Join Chain | §8 stop |
| D-900-06 | The CQRS pattern is mandatory for every canonical table: each sub-hub must have exactly one canonical table and one error table (e.g., sales_factfinder + sales_factfinder_errors); a canonical table without an error table is a structural violation that blocks the cycle. | PROCESS.md §OSAM + TABLES-AUDIT.md Gap 1 (missing sales_state_errors) | §9b gauge |
| D-900-07 | The worker must not serve any meeting page for a slug that does not have a valid sales_state row in D1; unknown slugs return HTTP 404 and are logged to the appropriate error table. | PROCESS.md §OSAM Forbidden Paths + src/resolve.ts | §8 stop |
| D-900-08 | All data writes flow exclusively from leaf (browser form submission) upward through the worker hub to D1 canonical tables; no direct D1 write is permitted from Neon, from the presentation layer, or from any Meeting 2-4 route. | PROCESS.md §OSAM Write Rules + CLAUDE.md §CTB CQRS | §8 stop |
| D-900-09 | Neon (outreach vault) is a read-only data source for this process; no writes to Neon originate from Process 900, and the NEON_URL secret must be configured as a read-only connection string. | PROCESS.md §Data Sources + wrangler.toml §vars | §9b gauge |
| D-900-10 | The D1 database binding is named `D1` and the database name is `sales-portal-900`; any migration or query that references a different binding name or database name is invalid and must not be executed. | wrangler.toml + PROCESS.md §OSAM | pre-flight |
| D-900-11 | The worker URL pattern for all meeting pages is `/sales/:slug/:meeting` where `:meeting` must be one of `meeting1`, `meeting2`, `meeting3`, or `meeting4`; any other path segment returns HTTP 404 and no HTML is rendered. | CLAUDE.md §What It Does + src/index.ts routing | §8 stop |

## Cross-references
- UT §7 Constants & Variables references these rules by ID (D-900-01 through D-900-11)
- UT §8 Stop Conditions cites D-900-01, D-900-02, D-900-04, D-900-05, D-900-07, D-900-08, D-900-11 as violations that halt
- §9b Live Verification gauges measure compliance for D-900-03 (Monte Carlo render), D-900-06 (CQRS table presence), D-900-09 (Neon read-only)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-29 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner (Dave Barton) amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |

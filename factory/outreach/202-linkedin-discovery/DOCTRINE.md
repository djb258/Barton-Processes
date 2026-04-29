# DOCTRINE — Process 202: LinkedIn Discovery
## Locked rules. Auditor enforces. Violations halt the cycle.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-202-01 | Gates must fire in strict order A → B → C; Gate B only fires if Gate A misses; Gate C only fires if both A and B miss. | heir.yaml `acceptance_criteria[0]` + PROCESS.md §3 Middle | §8 stop |
| D-202-02 | A LinkedIn URL must match the pattern `linkedin.com/in/{slug}` (validated via regex) before any slot write is attempted. | heir.yaml `acceptance_criteria[1]` + PROCESS.md §5 Forbidden Paths + src/find-linkedin.py `LINKEDIN_IN_RE` | §8 stop |
| D-202-03 | The company domain must never be included in the Startpage Gate C query; query format is `"{first} {last} {company} linkedin"` only. | heir.yaml `acceptance_criteria[2]` + PROCESS.md §3 Middle (Gate C) + PROCESS.md §5 Forbidden Paths | §8 stop |
| D-202-04 | LinkedIn profiles must not be scraped directly; only public search index results (Startpage) are permitted. | heir.yaml `acceptance_criteria[3]` + PROCESS.md §5 Forbidden Paths | §8 stop |
| D-202-05 | Gate C must halt immediately if CAPTCHA rate exceeds 10% of queries, or if 3 consecutive CAPTCHAs are detected. | heir.yaml `acceptance_criteria[4]` + PROCESS.md §7 Stop Conditions | §8 stop |
| D-202-06 | The DataImpulse proxy must use port 10000 (sticky session), `__cr.us` country targeting, and `chrome131` TLS impersonation via curl_cffi. | heir.yaml `acceptance_criteria[5]` + PROCESS.md §4 Proxy Configuration + src/find-linkedin.py `get_proxy_url()` | §9b gauge |
| D-202-07 | All writes are scoped exclusively to `slot_workbench`; no writes to Neon vault or any other table are permitted. | heir.yaml `acceptance_criteria[6]` + PROCESS.md §5 Forbidden Paths + DATA_FLOW.md Write Path | §8 stop |
| D-202-08 | Only slots where `has_name = 1 AND has_linkedin = 0` are eligible for processing; no other filter may be substituted. | heir.yaml `acceptance_criteria[7]` + PROCESS.md §3 Two-Question Intake + DATA_FLOW.md Read Path | §8 stop |
| D-202-09 | Proxy port must rotate every 50 queries (PORT_ROTATION_INTERVAL); a minimum 3-second delay (SEARCH_DELAY) must be enforced between Gate C searches. | PROCESS.md §4 Proxy Configuration + src/find-linkedin.py constants block | §9b gauge |
| D-202-10 | Gate A must read from `recon_linkedin_people` (the organized JSON array from Process 300 Organizer), never from raw recon data. | PROCESS.md §6 Constants + CLAUDE.md Gate Chain | pre-flight |

## Cross-references
- UT §7 Constants & Variables references these rules by ID
- UT §8 Stop Conditions cites D-202-01, D-202-02, D-202-03, D-202-04, D-202-05, D-202-07, D-202-08 as halt triggers
- UT §9b Live Verification gauges measure D-202-06 (proxy config), D-202-09 (rate/delay), D-202-08 (eligible slot count)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-29 |
| Authority | inherited from imo-creator-v2 (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |

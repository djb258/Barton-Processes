# DOCTRINE - Process 200 Gmail OAuth
## Locked rules. Auditor enforces. Violations halt Google API access for any Dave Agent identity.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-200-01 | One identity per OAuth token record. Each Dave Agent email address (dave@svg.agency, djb258@gmail.com, dbarton@svg.agency) gets its own row in google_oauth_tokens, keyed by email_addr. No shared token across identities. | PROCESS-UT.md §5 CONTRACT; heir.yaml acceptance_criteria[0] | §8 stop — token overwrite across identities is a silent identity confusion violation |
| D-200-02 | OAuth scope must include all four required scopes: gmail.readonly, gmail.send, gmail.modify, and calendar. Partial-scope tokens are invalid and must be re-authorized before any spoke may use them. | PROCESS-UT.md §5 CONTRACT §5b Scope; heir.yaml acceptance_criteria[1] | §8 stop — partial-scope token cannot serve all downstream consumers; re-auth required |
| D-200-03 | Token refresh is the responsibility of the spoke layer (gmail.ts refreshAccessToken). No route handler may attempt a raw token refresh. The spoke handles expiry transparently. | PROCESS-UT.md §4 IMO; heir.yaml acceptance_criteria[2] | pre-flight — refresh logic in hub or rim layer is an architecture violation |
| D-200-04 | No hardcoded identity. The identity (email_addr) is always provided as a runtime parameter or derived from the stored token's provider row. Never embed a specific email address in route logic. | PROCESS-UT.md §3 RESOURCES; heir.yaml acceptance_criteria[3] | pre-flight — hardcoded email is a constant masquerading as a variable; fails C&V gate |
| D-200-05 | OAuth callback MUST validate the state token returned by Google matches the state issued at /cos/oauth/google/start. Mismatched state = reject with 400. No silent accept. | PROCESS-UT.md §4 IMO Middle; heir.yaml acceptance_criteria[4] | §8 stop — CSRF protection; mismatched state is a security violation; return 400 and log |
| D-200-06 | Tokens are stored in MC_MAIL D1 binding (google_oauth_tokens table). No other storage location is permitted. Workers that need a token must read from MC_MAIL via the spoke, never from KV, env vars, or secrets. | PROCESS-UT.md §5 CONTRACT §5c Storage; heir.yaml acceptance_criteria[5] | §8 stop — out-of-band token storage breaks the single source of truth for credential state |
| D-200-07 | The /cos/oauth/google/whoami endpoint is the canonical post-flow verification command. Dave must run it after every OAuth flow to confirm token validity, email binding, and scope coverage. | PROCESS-UT.md §8 INGEST CHECKLIST Step 5 | pre-flight — skipping whoami verification leaves the token state unconfirmed; BUILD cannot transition to OPERATE |
| D-200-08 | Token records are never hard-deleted. If a token must be revoked, set the row's expiry_at to a past timestamp and mark the ORBT state as REPAIR. Hard deletes break the audit trail. | PROCESS-UT.md §9 PERMISSIONS Write Rules | §8 stop — hard delete of token record destroys audit trail; HALT |

## Cross-references
- UT §5 CONTRACT references D-200-01 (one identity per row), D-200-02 (scope), D-200-06 (storage)
- UT §4 IMO references D-200-03 (refresh in spoke), D-200-05 (state validation)
- UT §8 INGEST CHECKLIST cites D-200-07 (whoami verification)
- UT §9 PERMISSIONS cites D-200-08 (no hard delete)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |
| Rule Count | 8 (D-200-01 through D-200-08) |

# DOCTRINE — Process 100 Kiddos Working Surface
## Locked rules. Auditor enforces. Violations break family data integrity or auth security.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-100-01 | person_id is the sovereign join key for all Kiddos data. Every academic, sports, and health record MUST carry a person_id foreign key. Orphan records (no person_id) are forbidden. | kiddos-api types.ts + db.ts | §5 stop — unkeyed records poison every downstream query |
| D-100-02 | Google OAuth is the sole authentication mechanism for parents. No username/password, no magic link, no API key auth on parent routes. Bearer JWT issued after OAuth exchange is the only valid session token. | kiddos-api auth.ts + /auth/google routes | §9 stop — alternate auth paths bypass parental identity verification |
| D-100-03 | D1 is the working layer for all Kiddos reads/writes. KV cache is derived from D1 and is read-only after population. Neon vault is the archival layer. The write path is D1 → KV populate → Neon archive. No direct KV writes from route handlers. | kiddos-api index.ts (D1 + KV + Neon layers declared) | §5 stop — direct KV writes create cache/DB divergence |
| D-100-04 | All child records (academic, sports, health) are accessed via /children/:id routes. The :id parameter MUST resolve to a known person_id in D1. Unknown :id → 404, not empty array. | kiddos-api routes-children.ts | §6 stop — empty array on unknown child masks identity mismatch |
| D-100-05 | Family link operations (/family/link) require the requesting parent to be authenticated. A parent cannot link to a child record they do not own. The family link validates person_id ownership before writing. | kiddos-api routes-family.ts | §9 stop — cross-family data access is a critical privacy violation |
| D-100-06 | Google service integrations (Drive, Calendar, Gmail) are scoped per authenticated parent. The OAuth token used for /google/* routes MUST match the authenticated parent's person_id. Token substitution or shared tokens are forbidden. | kiddos-api routes-google.ts + google.ts | §9 stop — token mismatch exposes one parent's Google data to another |
| D-100-07 | CORS is configured at the worker level for all routes. The allowed-origins list is a locked constant — additions require a BAR. The default allowed origin is the Kiddos CF Pages domain. | kiddos-api index.ts (CORS middleware declared) | pre-flight — unlocked CORS exposes family data to arbitrary origins |
| D-100-08 | Health and performance data is the highest-sensitivity tier of Kiddos data. Health records must never be included in non-authenticated responses. The /children/:id/health routes require a valid parent Bearer token. | kiddos-api routes-children.ts | §9 stop — health data exposure is a HIPAA-adjacent privacy violation |
| D-100-09 | The correlation surface (sports ↔ health over time) is a derived view — it is computed from canonical academic, sports, and health records. It is read-only. No mutation route may target the correlation surface directly. | Barton Enterprises CTB BRANCH 3 — Kiddos correlation surface node | §9 stop — writing to a derived view corrupts source-of-truth records |
| D-100-10 | The Kiddos API is scoped to BRANCH 3 Personal on the Barton Enterprises CTB. It must never expose routes or data from SVG Agency (BRANCH 1) or Real Estate (BRANCH 2). Cross-branch data access is a sovereign-silo violation. | law/BARTON_ENTERPRISES_CTB.md — Sovereign Silos rule | §9 stop — cross-branch exposure violates CTB isolation doctrine |

## Cross-references
- UT §5 CONTRACT references D-100-01 (person_id sovereign key), D-100-03 (D1/KV/Neon layers)
- UT §4 IMO references D-100-03 (write path sequence)
- UT §6 JOIN CONTRACT references D-100-01 (person_id join), D-100-04 (child :id resolution)
- UT §9 PERMISSIONS references D-100-02 (Google OAuth), D-100-05 (family link auth), D-100-06 (Google token scope), D-100-08 (health data gate)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| BAR | BAR-167 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 |
| Rule Count | 10 (D-100-01 through D-100-10) |

# DOCTRINE — Process 910 Content Artifacts
## Locked rules. Auditor enforces. Violations halt artifact ingest or page rendering.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-910-01 | content_id is the routing key for all artifact lookups. It must match the route slug exactly (no leading slash). Any mismatch returns 404 — no fuzzy matching permitted. | PROCESS-UT.md §6 JOIN CONTRACT | §8 stop — mismatched content_id breaks page routing |
| D-910-02 | slot_type is the enum discriminator. Valid values: video, audio, slides, infographic, report, quiz, flashcards, mindmap, datatable. Any value outside this set is rejected at the ingest gate with HTTP 400. | PROCESS-UT.md §5 CONTRACT; ingest.ts VALID_SLOT_TYPES | §8 stop — invalid slot_type indicates a schema violation |
| D-910-03 | One row per (content_id, slot_type) is enforced by UNIQUE constraint. Ingest uses INSERT … ON CONFLICT DO UPDATE — idempotent. Caller may POST the same slot repeatedly without side effects. | PROCESS-UT.md §5 CONTRACT; 0001_content_artifacts.sql | pre-flight — duplicate slots overwrite, not multiply |
| D-910-04 | payload is a JSON blob whose schema is slot-type-specific. The ingest endpoint does NOT validate payload internals — callers own the shape. Malformed JSON payload causes a parse error at read time, not write time. | PROCESS-UT.md §5 CONTRACT | §8 stop — payload schema is caller's responsibility; doc must reference expected shapes per slot_type |
| D-910-05 | Auth gate is mandatory on every write path. POST /api/artifacts/ingest requires Authorization: Bearer <ARTIFACT_INGEST_TOKEN>. Missing or invalid token returns HTTP 401. No unauthenticated writes permitted. | PROCESS-UT.md §9 PERMISSIONS; ingest.ts auth gate | §8 stop — unauthenticated ingest is a security violation |
| D-910-06 | status field defaults to 'active' on insert and is reset to 'active' on conflict update. To retire an artifact, caller must explicitly PATCH status to 'archived' via a direct D1 admin operation. No delete path exists on the ingest endpoint. | PROCESS-UT.md §8 INGEST CHECKLIST Kill Switch | §8 stop — deletion of artifact rows must be admin-only |
| D-910-07 | The CONTENT_ARTIFACTS D1 binding is the single source of truth for this process. No other store (R2, KV, hardcoded JSON) may be treated as authoritative for content slot configuration. | PROCESS-UT.md §6 JOIN CONTRACT | pre-flight — any system reading artifact config must query CONTENT_ARTIFACTS D1 |
| D-910-08 | content_id values come from the route slug system defined in the CF Pages project. Adding a new content page requires a corresponding ingest call to register its artifact slots before the page goes live. | PROCESS-UT.md §8 INGEST CHECKLIST | pre-flight — unregistered content pages render empty slot UI |
| D-910-09 | GET /api/artifacts/[content_id] is the read path. It returns all active slots for a given content_id. The response is consumed by the ContentPage React component. No other read pattern is sanctioned. | PROCESS-UT.md §6 JOIN CONTRACT | pre-flight — client code must use this endpoint; direct D1 reads from frontend are forbidden |
| D-910-10 | This process is scoped to insuranceinformatics.com content pages only. Extending to other domains requires a separate process doc and a new D1 binding. | PROCESS-UT.md §1 IDENTITY | pre-flight — cross-domain use without a separate doc is a doctrine violation |

## Cross-references
- UT §5 CONTRACT references D-910-02 (slot_type enum), D-910-03 (UNIQUE constraint), D-910-04 (payload ownership)
- UT §8 INGEST CHECKLIST cites D-910-06 (status kill switch), D-910-08 (pre-ingest requirement)
- UT §9 PERMISSIONS cites D-910-05 (auth gate), D-910-07 (D1 as source of truth)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| BAR | BAR-194 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 |
| Rule Count | 10 (D-910-01 through D-910-10) |

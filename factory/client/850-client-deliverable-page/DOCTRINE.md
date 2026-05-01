# DOCTRINE — Process 850 Client Deliverable Page
## Locked rules. Auditor enforces. Violations halt page rendering or data exposure.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-850-01 | slug is the sole access token for the public read path. GET /public/clients/slug/:slug requires no Bearer header. Slug is derived from company_name at record creation and must be non-guessable in practice (search space >> brute-force feasibility for operational data at this sensitivity tier). | ClientDeliverablePage.tsx §AUTH MODEL | pre-flight — slug derivation must remain opaque; sequential or predictable slugs are a security violation |
| D-850-02 | The public read endpoint is GET /public/clients/slug/:slug on mission-control-api. No other endpoint may be called from the ClientDeliverablePage component for client record retrieval. | ClientDeliverablePage.tsx CLIENT_HUB_BASE | §8 stop — direct D1 reads or alternate API routes from the frontend are forbidden |
| D-850-03 | LCS page-event beacon fires on every successful data load via POST to lcs-hub /page-event. The beacon payload must include: sovereign_company_id (slug uppercase), communication_id, event_type='page_loaded', lifecycle_phase='CLIENT_DELIVERABLE', page_step='deliverable_view'. No sensitive PII may be included in the beacon payload. | ClientDeliverablePage.tsx sendPageEvent() | pre-flight — omitting the beacon breaks the LCS feedback loop; adding PII is a data exposure violation |
| D-850-04 | ClientData shape is the canonical contract. Fields: client_id, company_name, employee_count, vendors (array: vendor_id, vendor_name, vendor_type), open_service_requests, pending_invoice_count, branding_color. Backend must not return fields outside this shape on the public route. | ClientDeliverablePage.tsx ClientData type | §5 stop — schema drift between frontend type and backend response breaks rendering |
| D-850-05 | Auth model is public read with slug-as-soft-token (BAR-82, locked 2026-04-30). Upgrade path is documented: Option A = X-API-Key per client, Option B = signed JWT, Option C = session cookie. No upgrade may be implemented without a new BAR and revised DOCTRINE. | ClientDeliverablePage.tsx §AUTH MODEL UPGRADE PATH | pre-flight — silent auth model changes without a BAR violate governance |
| D-850-06 | branding_color is optional. When present it controls header border and stat card accent. When absent the default accent is #1a56db. No other color system may override branding_color at render time. | ClientDeliverablePage.tsx accent logic | pre-flight — hardcoded color overrides break client branding contract |
| D-850-07 | The component renders three states: loading skeleton (aria-busy), error state (role=alert), and data state. All three must be present. Error state must display the slug and error message. No state may be silently swallowed. | ClientDeliverablePage.tsx LoadingSkeleton + ErrorState | §8 stop — missing states cause silent failures invisible to operators |
| D-850-08 | open_service_requests > 0 triggers red accent (#e3342f) on the stat card. pending_invoice_count > 0 triggers orange accent (#f6993f). These threshold-to-color mappings are locked. No other threshold logic may be added without a DOCTRINE amendment. | ClientDeliverablePage.tsx StatCard accent logic | pre-flight — threshold drift silently changes operator alert signals |
| D-850-09 | No state mutation occurs on the client page. The component is read-only. Any action that modifies client data must route through mission-control-api authenticated write paths, not through this public page. | ClientDeliverablePage.tsx §AUTH MODEL — no CSRF needed | §9 stop — write actions on a public no-auth page are a security violation |
| D-850-10 | This process is scoped to the insuranceinformatics.com client deliverable surface only. Extending to other domains or adding client-side mutation requires a separate BAR and updated DOCTRINE. | BAR-82 scope lock | pre-flight — cross-domain use without a separate doc is a doctrine violation |

## Cross-references
- UT §4 IMO references D-850-02 (endpoint), D-850-03 (beacon flow)
- UT §5 CONTRACT references D-850-04 (ClientData shape)
- UT §9 PERMISSIONS references D-850-05 (auth model), D-850-09 (read-only)
- UT §8 INGEST CHECKLIST references D-850-06 (branding_color), D-850-07 (states), D-850-08 (thresholds)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| BAR | BAR-82 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 |
| Rule Count | 10 (D-850-01 through D-850-10) |

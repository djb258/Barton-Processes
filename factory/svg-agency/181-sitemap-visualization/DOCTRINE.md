# DOCTRINE — Process 181 Sitemap Visualization (MapEngine)
## Locked rules. Auditor enforces. Violations break map rendering or CTB visibility.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-181-01 | MapLayer is the canonical shape for all geographic data layers. Required fields: layer_id, name, category, branch, parent_hub, ctb_node, architecture_doc, d1_database, d1_table, lat_col, lon_col, zip_col, color_col, color_scale, label_col, tooltip_cols, marker_color, icon, is_active, is_default_visible, sort_order, description, filter_sql. Backend must return this shape from GET /map/layers. | MapEngine.tsx MapLayer interface | §5 stop — schema drift breaks layer rendering and CTB node lookup |
| D-181-02 | SitemapEntry consumed by MapEngine must match the shape from Process 180 (Sitemap Publisher): site, site_label, path, title, url, parent, depth, priority, changefreq, last_modified. MapEngine is a consumer of Process 180; it must not transform or cache the shape. | MapEngine.tsx SitemapEntry interface | §6 stop — shape divergence between Process 180 and Process 181 breaks the join |
| D-181-03 | CATEGORY_COLORS is the authoritative color palette for map dot rendering. Keys: storage, insurance, signals, deals, sales-stack, sales-gates, sales-status, svg-outreach, svg-sales, svg-client, svg-service, default. No category may be rendered with a color not in this palette without a DOCTRINE amendment. | MapEngine.tsx CATEGORY_COLORS | pre-flight — rogue colors break visual consistency of the CTB map |
| D-181-04 | MAX_POINTS is 2000. The map must never attempt to render more than 2000 points in a single viewport. Point count enforcement is mandatory at the data-fetch layer, not the render layer. | MapEngine.tsx MAX_POINTS constant | §8 stop — exceeding MAX_POINTS causes browser performance degradation |
| D-181-05 | DEBOUNCE_MS is 500ms. All viewport-triggered data fetches must be debounced at 500ms minimum. Reducing DEBOUNCE_MS without a BAR is a doctrine violation. | MapEngine.tsx DEBOUNCE_MS constant | pre-flight — under-debounced fetches flood mission-control-api with requests |
| D-181-06 | ViewportStats shape is canonical: count, avgPriceSqft, avgOccupancy, avgSaturation. All four fields must be present in the response from GET /map/points (nullable for non-applicable layers). Stats panel must display N/A for null fields, not zero or empty. | MapEngine.tsx ViewportStats interface | §5 stop — null→zero masking hides meaningful absence-of-data signals |
| D-181-07 | Mission Control API (MC_API_URL) is the sole data source for MapEngine. Direct D1 reads from the frontend, external API calls, or hardcoded data arrays are forbidden. MC_API_KEY authentication is required on all map API requests. | MapEngine.tsx MC_API_URL + MC_API_KEY | §9 stop — unauthenticated or direct reads bypass the hub |
| D-181-08 | ctb_node field on MapLayer is the CTB attachment point. When present, MapEngine renders the node's position on the Barton Enterprises CTB. MapLayer rows with null ctb_node are rendered as unattached (orphan indicator). Orphan layers must be visible as warnings in the UI, not silently hidden. | MapEngine.tsx MapLayer.ctb_node | pre-flight — hiding orphan layers masks governance violations |
| D-181-09 | The sitemap tree view within MapEngine is a read-only visualization of Process 180 data. No sitemap data may be created, edited, or deleted from the MapEngine interface. Sitemap mutations require a code deploy on Process 180 (BAR). | BAR-323 scope | §9 stop — write actions on a read-only visualization surface are a scope violation |
| D-181-10 | MapEngine is scoped to Mission Control only (CF Pages, Cloudflare Access gated). It must never be exposed as a public endpoint. The MC_API_KEY authentication on all API calls is the runtime enforcement of this scope. | Mission Control CLAUDE.md — CF Access | §9 stop — public exposure of the CTB map violates Zero Trust architecture |

## Cross-references
- UT §5 CONTRACT references D-181-01 (MapLayer), D-181-02 (SitemapEntry), D-181-06 (ViewportStats)
- UT §4 IMO references D-181-04 (MAX_POINTS), D-181-05 (DEBOUNCE_MS)
- UT §6 JOIN CONTRACT references D-181-02 (Process 180 join), D-181-08 (ctb_node attachment)
- UT §9 PERMISSIONS references D-181-07 (MC_API_KEY), D-181-10 (access gate)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| BAR | BAR-323 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 |
| Rule Count | 10 (D-181-01 through D-181-10) |

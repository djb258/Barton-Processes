# DOCTRINE — Process 170 UT Map Viewer
## Locked rules. Auditor enforces. Violations block certification.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-170-01 | Every PROCESS-UT.md is rendered as a map. The 3 cluster banners (IDENTITY / CONTRACT / GOVERNANCE) are top-level toggleable layers. 14 sections are sub-layers. This mapping is a constant — it does not vary per doc. | PROCESS-UT.md §4 IMO; law/UNIFIED_TEMPLATE.md | §8 stop — any component that renders UT sections without cluster grouping is a doctrine violation |
| D-170-02 | The 13-item UT Pre-Flight Checklist renders as a status overlay. Items are red (unchecked) or green (checked). The checklist is NEVER suppressed even when a section is collapsed. | PROCESS-UT.md §7 C&V; law/UT_CHECKLIST.md v1.2.0 | §8 stop — hiding the checklist overlay is a visibility violation |
| D-170-03 | Source docs are PROCESS-UT.md files only. Worker fill instructions, DATABASE docs, or LOCKSMITH docs are NOT rendered by this viewer. The doc picker must filter to **/PROCESS-UT.md paths exclusively. | PROCESS-UT.md §2 PRD Scope | pre-flight — rendering non-UT docs in this viewer is a scope violation |
| D-170-04 | Multi-doc compare mode renders each doc as its own layer set. Diff highlighting is additive — it does NOT hide sections. Side-by-side max: 3 docs. | PROCESS-UT.md §4 IMO Output | §8 stop — compare mode that hides base doc content is a contrast violation |
| D-170-05 | The UTViewer.tsx component is a full rebuild — NOT an extension of the BAR-event-renderer. No BAR fetch logic, no SECTION_EVENT_MAP, no BarStrip, no AddBarModal survives in the new component. | PROCESS-UT.md §8 Stop Conditions; BAR-339 dispatch | §8 stop — importing BAR-related state into the Map Viewer is a scope contamination |
| D-170-06 | The component reads doc content from the MC API /ut-docs endpoint (preferred) or via static import list. It does NOT call the filesystem directly from the CF Pages worker. | PROCESS-UT.md §5 OSAM; workers/mission-control CLAUDE.md | §8 stop — direct filesystem reads from CF Pages runtime violate the Cloudflare execution model |
| D-170-07 | Layer visibility state is local (useState). It is NOT persisted to D1 or LBB during this BUILD phase. Persistence is a Phase 2 enhancement requiring its own BAR. | PROCESS-UT.md §7 C&V; ORBT.yaml | pre-flight — premature persistence wiring is gold-plating; block if it adds D1 schema changes |

## Cross-references
- §4 IMO grounds D-170-01 (cluster=layer mapping)
- §7 C&V grounds D-170-02 (checklist visibility) and D-170-07 (state scope)
- §2 PRD grounds D-170-03 (doc type filter)
- §8 Stop Conditions grounds D-170-05 (BAR contamination) and D-170-06 (filesystem access)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |
| Rule Count | 7 (D-170-01 through D-170-07) |

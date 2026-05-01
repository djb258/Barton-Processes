# UT Map Viewer — Universal Template Doc Renderer
## Renders any PROCESS-UT.md as a layered map. Cluster = layer. Section = sub-layer. Checklist = status overlay.
### Status: BUILD
### Medium: cloudflare-pages
### Business: svg-agency / mission-control

## UT Checklist (Pre-Flight — per law/UT_CHECKLIST.md v1.2.0)

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | [x] | §2 |
| 2 | OSAM — READ / WRITE / Join Chain / Forbidden Paths / Query Routing filled | [x] | §5 |
| 3 | Component Status — every dependency has light with 1-line state | [x] | §3 |
| 4 | Owner — human who fixes this at 2 AM | [x] | §1 |
| 5 | Live Dashboard — URL or explicit "N/A" | [x] | §3 |
| 6 | Kill Switch — exact command to stop the process | [x] | §8 |
| 7 | Logbook — last audit verdict + date (after certification only) | [ ] | §12 — N/A during BUILD |
| 8 | FCEs Attached — which FCE runs structurally back this doc | [x] | §3c |
| 9 | BARs Referenced — every BAR this doc touches, with status | [x] | §3d |
| 10 | LBB Subjects Fed — which LBB subject(s) this doc's session logs go to | [x] | §3e |
| 11 | Geometry — CTB position + Hub-Spoke role + Altitude | [x] | §1b |
| 12 | Live Verification — every numeric count, cron, URL, command, BAR status grounded | [ ] | §9 — pending live typecheck |
| 13 | ctb_node — declared path on Barton Enterprises CTB trunk | [x] | §1 |

---

# IDENTITY

## 1. Identity

| Field | Value |
|-------|-------|
| ID | UT-MAP-VIEWER |
| Name | UT Map Viewer — Universal Template Doc Renderer |
| Medium | cloudflare-pages (React + TypeScript + Vite + Tailwind) |
| Business Silo | svg-agency / mission-control |
| CTB Position | barton-enterprises/svg-agency/mission-control/ut-map-viewer |
| ORBT | BUILD |
| Strikes | 0 |
| Authority | CC-02 (hub — mission-control owns this page) |
| Version | 2.0.0 |
| Last Modified | 2026-04-30 |
| BAR Reference | BAR-339_v2.0.0 |
| Owner | Dave Barton |
| ctb_node | barton-enterprises/svg-agency/mission-control/ut-map-viewer |

### 1b. Geometry

**CTB Position:** Barton Enterprises → SVG Agency → Mission Control → UT Map Viewer (leaf)

**Hub-Spoke Role:** leaf output (this page reads from Barton-Processes filesystem via MC API; it does not write)

**Altitude:** 10k operational (one leaf cluster — single page within Mission Control hub)

```
TRUNK: Barton Enterprises
  BRANCH: SVG Agency
    HUB: Mission Control (CC-02)
      LEAF: UT Map Viewer (CC-02, output spoke)
```

---

# CONTRACT

## 2. Purpose (PRD)

**WHAT:** A React page (UTViewer.tsx) inside Mission Control that loads any PROCESS-UT.md from Barton-Processes and renders it as an interactive layered map. The 3 UT cluster banners become toggleable top-level layers. The 14 sections become sub-layers under their parent cluster. The 13-item UT Pre-Flight Checklist becomes a status overlay (red/green per item). Multi-doc compare mode lets the operator pick 2-3 docs and render them side-by-side.

**WHY:** The prior UTViewer rendered BAR work orders against the UT skeleton — wrong target. The correct architecture uses PROCESS-UT.md as the source. Every Barton Process is already in UT format; making them navigable as a map closes the Circle between the doctrine (Barton-Processes) and the command floor (Mission Control).

**WHO:**
- Dave Barton (operator — reads and compares process docs)
- Mission Control (host — renders the page)
- Barton-Processes (source — provides PROCESS-UT.md files)
- MC API (spoke — optionally serves the doc list and content)

**SCOPE (in):**
- Render any `factory/**/PROCESS-UT.md` as a layered map
- Cluster banner → toggleable layer (IDENTITY / CONTRACT / GOVERNANCE)
- 14 sections → sub-layers under their cluster
- 13-item checklist → status overlay per doc
- Doc picker dropdown listing all available PROCESS-UT.md paths
- Multi-doc compare: pick 2-3 docs, side-by-side or stacked, diff on checklist items

**OUT-OF-SCOPE:**
- Worker fill instructions, DATABASE docs, LOCKSMITH docs — not rendered here (handled by doc-library viewer if one exists)
- BAR work order rendering — removed entirely (was the BAR-339 v1.0.0 error)
- Persisting layer visibility state to D1 — Phase 2 BAR only
- Editing PROCESS-UT.md content from within this viewer

**SUCCESS METRIC:** Operator can load any PROCESS-UT.md, see its 3 clusters as layer toggles, drill into any of 14 sections, and see 13-item checklist status — all in under 2 seconds from doc selection.

## 3. Resources

### 3a. Components

| Component | State | Notes |
|-----------|-------|-------|
| workers/mission-control (CF Pages) | LIVE | Host. React + TypeScript + Vite. |
| workers/mission-control-api (CF Worker) | LIVE | Optional /ut-docs endpoint (Phase 2). Phase 1 uses static doc list. |
| Barton-Processes/factory/ | LIVE | Source of all PROCESS-UT.md files. Read-only from viewer. |
| law/UNIFIED_TEMPLATE.md | LOCKED | Defines the 14-section 3-cluster format this viewer renders. |
| law/UT_CHECKLIST.md v1.2.0 | LOCKED | Defines the 13-item checklist the overlay renders. |

**Live Dashboard:** Mission Control → https://mission-control-21z.pages.dev (CF Access — Dave-only)

### 3b. Dependencies

| Dependency | Version | Status |
|------------|---------|--------|
| React | 18.x | LIVE |
| TypeScript | 5.x | LIVE |
| Tailwind CSS | 3.x | LIVE |
| lucide-react | latest | LIVE |
| Vite | 5.x | LIVE |

### 3c. FCEs Attached

No FCE runs against the UT Map Viewer directly. The viewer IS the output of running K=C on each PROCESS-UT.md — it reads the result of FCE work, it does not perform FCE evaluation.

### 3d. BARs Referenced

| BAR | Title | Status |
|-----|-------|--------|
| BAR-339 v1.0.0 | UTViewer — BAR work order renderer | RETIRED (wrong target, replaced by v2.0.0) |
| BAR-339 v2.0.0 | UT Map Viewer rebuild | ACTIVE (this doc) |

### 3e. LBB Subjects Fed

Session logs → subject_id: `system` (Mission Control architecture)
Secondary → subject_id: `processes` (UT format learnings)

## 4. IMO

**Input:**
- Crossing Input: operator selects a PROCESS-UT.md from the doc picker
- Initial Condition: UTViewer.tsx mounts with empty state (no doc loaded)

**Middle:**
1. Doc picker fires → fetch doc path list from `/ut-docs` endpoint (or static manifest)
2. Operator selects doc → fetch PROCESS-UT.md content
3. Parser extracts: (a) cluster headers, (b) 14 sections with content, (c) 13 checklist items + checkbox states
4. Layer state initializes: all clusters ON, all sections collapsed
5. Operator toggles cluster → section sub-layers show/hide
6. Operator toggles section → content renders inline
7. Checklist overlay: always visible; items green (checked) or red (unchecked)
8. Multi-doc mode: operator picks 2-3 docs → repeat steps 2-7 for each → render side-by-side

**Output:**
- Emitted Output: nothing (read-only viewer, no writes)
- Retained Output: layer toggle state (local useState, not persisted)

**Circle:** Operator reads a PROCESS-UT.md, identifies gaps (red checklist items), opens the doc in Cursor, fixes it, redeploys Barton-Processes. The viewer reflects the updated state on next load. Circle closes.

## 5. OSAM — Data Schema

### READ

| Source | Table/Path | Fields Read | Join |
|--------|-----------|-------------|------|
| MC API /ut-docs | None (filesystem walk) | path, doc_id, title | None |
| PROCESS-UT.md | filesystem | Full markdown text | Parsed client-side |

### WRITE

None. This is a read-only viewer.

### Join Chain

Doc picker list → PROCESS-UT.md content → parsed cluster/section/checklist → React state → rendered map

### Forbidden Paths

- No writes to any D1 table during BUILD phase
- No reads from cl_company_identity, clients, contacts, or any business data table
- No cross-doc joins (each doc renders independently except in compare mode where they sit side-by-side)

### Query Routing

Phase 1: Static doc list hardcoded or loaded from a JSON manifest committed alongside the build.
Phase 2: GET /ut-docs from mission-control-api returns `[{ path, title, doc_id }]` — MC API walks Barton-Processes via a pre-built manifest (CF Workers cannot walk a filesystem at runtime).

## 6. DMJ

**Define:**
- `PROCESS-UT.md` = constant (named + formatted — always 14 sections, 3 clusters, 13-item checklist)
- `cluster` = constant (3 values: IDENTITY, CONTRACT, GOVERNANCE — never changes)
- `section` = constant (14 items, numbered, fixed titles per UNIFIED_TEMPLATE.md)
- `checklist_item` = constant (13 items, fixed per UT_CHECKLIST.md v1.2.0)
- `checkbox_state` = variable (value: checked or unchecked — changes per doc)
- `doc_content` = variable (value: the text inside each section — changes per doc)
- `layer_visibility` = variable (value: on/off — changes per operator interaction)

**Map:**
- cluster banner → layer toggle button (top-level)
- section heading → sub-layer accordion row under its cluster
- checklist item + state → status badge in overlay (green/red)
- doc_content → rendered markdown inside expanded section

**Join:**
- Spine: `law/UNIFIED_TEMPLATE.md` (defines the invariant structure)
- Every PROCESS-UT.md conforms to UNIFIED_TEMPLATE.md
- Viewer reads PROCESS-UT.md → maps to UNIFIED_TEMPLATE.md structure → renders
- No multi-hop join required — the format IS the key

## 7. Constants & Variables

| Element | Classification | Rationale |
|---------|---------------|-----------|
| 3 cluster banners | CONSTANT | Fixed by UNIFIED_TEMPLATE.md — never changes |
| 14 section titles | CONSTANT | Fixed by UNIFIED_TEMPLATE.md — never changes |
| 13 checklist items | CONSTANT | Fixed by UT_CHECKLIST.md v1.2.0 — never changes |
| Cluster-to-section mapping | CONSTANT | IDENTITY=[1-3], CONTRACT=[4-9], GOVERNANCE=[10-14] |
| Doc content (section text) | VARIABLE | Fills per doc |
| Checkbox state per item | VARIABLE | Fills per doc |
| Layer visibility | VARIABLE | Fills per operator interaction |
| Doc list | VARIABLE | Fills per Barton-Processes state |
| Selected doc | VARIABLE | Fills per operator selection |

## 8. Stop Conditions

| Condition | Response |
|-----------|----------|
| Doc fetch fails (network error) | Show error state in viewer — "Could not load doc. Check MC API." Do not crash the page. |
| PROCESS-UT.md does not conform to UNIFIED_TEMPLATE.md (missing sections) | Render available sections; flag missing sections as RED in the map. Do not hide the gap. |
| BAR-related imports detected in UTViewer.tsx | HALT build. Remove before typecheck. D-170-05. |
| Filesystem read attempted from CF Pages runtime | HALT. Use MC API endpoint or static manifest. D-170-06. |
| Non-PROCESS-UT.md file selected | Reject in doc picker. Filter enforced at list-generation level. D-170-03. |

**Kill Switch:** Remove the UT Map Viewer route from `workers/mission-control/src/App.tsx` (or `Shell.tsx`) → redeploy. The page disappears from Mission Control. No data loss (viewer is read-only).

## 9. Verification

**Typecheck:** `cd workers/mission-control && npx tsc --noEmit` — must PASS.

**Manual verification checklist:**
- [ ] 3 cluster layer toggles render (IDENTITY / CONTRACT / GOVERNANCE)
- [ ] Toggling a cluster shows/hides its section sub-layers
- [ ] 14 sections total across 3 clusters (3 + 6 + 5)
- [ ] Checklist overlay renders 13 items
- [ ] Green item = checked `[x]` in source; Red = unchecked `[ ]`
- [ ] Doc picker lists PROCESS-UT.md files
- [ ] Selecting a doc loads and parses it
- [ ] Multi-doc compare: 2 docs side by side
- [ ] No BAR-related code (no `/cos/bars` calls, no BarStrip, no AddBarModal)
- [ ] No TypeScript errors

**Live Verification:** Pending — requires typecheck run after Phase 1 complete.

---

# GOVERNANCE

## 10. Analytics

N/A during BUILD. Phase 2: log doc-view events to `mc_errors` table (or a new `mc_events` table) — BAR TBD.

## 11. Execution Trace

| Date | Actor | Action | Result |
|------|-------|--------|--------|
| 2026-04-30 | claude-code (BAR-339_v2.0.0) | Phase 0 manual created | 4 files written |
| 2026-04-30 | claude-code (BAR-339_v2.0.0) | Phase 1 UTViewer.tsx rewrite | In progress |

## 12. Logbook

N/A — logbook not created until auditor sign-off (BUILD phase). No audit verdict yet.

## 13. Fleet Failure Registry

No failures registered. BAR-339 v1.0.0 failure: wrong target (rendered BAR work orders instead of PROCESS-UT.md docs). Corrected in v2.0.0 via full rebuild.

## 14. Maintenance Logbook

| Date | Change | Author |
|------|--------|--------|
| 2026-04-30 | v2.0.0 — full rebuild dispatched. Phase 0 manual (4 files) complete. UTViewer.tsx replaced. Architecture reframed: UT doc renderer, not BAR renderer. | BAR-339_v2.0.0 / claude-code |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-30 |
| Last Modified | 2026-04-30 |
| Version | 2.0.0 |
| Status | BUILD |
| Authority | CC-02 (mission-control hub) |
| Inherits | law/UNIFIED_TEMPLATE.md + law/UT_CHECKLIST.md v1.2.0 + law/doctrine/FOUNDATIONAL_BEDROCK.md |

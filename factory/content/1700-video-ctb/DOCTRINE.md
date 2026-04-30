# DOCTRINE — Process 1700 Video CTB
## Locked rules. Auditor enforces. Violations block video production and NotebookLM ingest.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-1700-01 | Every video maps to exactly one CTB node (trunk, branch, or leaf). A video without a declared CTB position is an orphan and may not be published. | PROCESS-UT.md §1 IDENTITY; heir.yaml ctb_placement | pre-flight — undeclared CTB node halts video production |
| D-1700-02 | Sources for each video live in that video's `sources/` subfolder only. Cross-pollination of sources between video folders is a sovereignty violation. | PROCESS-UT.md §4 IMO — Input | §8 stop — mixed sources corrupt the NotebookLM notebook |
| D-1700-03 | NotebookLM notebook IDs are constants per video. Once a notebook ID is assigned to a video folder, it is locked. A new video requires a new notebook — never re-use an existing notebook for a different CTB node. | PROCESS-UT.md §4 IMO — Middle; README Notebook ID column | §8 stop — notebook ID reuse corrupts the artifact lineage |
| D-1700-04 | Workflow order is mandatory: (1) Sources added to `sources/` → (2) Sources uploaded to NotebookLM → (3) Artifacts generated → (4) Artifacts downloaded → (5) CF Stream upload (PROC-018) → (6) Deployed to content-pages. Steps cannot be skipped or reordered. | PROCESS-UT.md §4 IMO — Middle; §7 STOP CONDITIONS | §8 stop — out-of-order execution breaks the artifact chain |
| D-1700-05 | Every video artifact that is a video file (.mp4) must be uploaded to CF Stream via PROC-018 before it can be embedded in content-pages. Local file storage on CF Pages is not permitted for video artifacts (65MB+ files). | PROCESS-UT.md §8 DEPENDENCIES upstream; PROC-018 | §8 stop — direct CF Pages hosting of video files exceeds size limits |
| D-1700-06 | Source quality gates: sources must be relevant to the declared CTB node. Generic or off-topic sources are rejected. The more specific and on-point the sources, the better the generated artifact. | PROCESS-UT.md §2 PURPOSE — SUCCESS METRIC | pre-flight — off-topic sources dilute artifact quality |
| D-1700-07 | The README.md is the navigation index only — it is not a governance doc. Governance lives in PROCESS-UT.md. If there is a conflict between README.md and PROCESS-UT.md, PROCESS-UT.md wins. | PROCESS-UT.md authority | pre-flight |

## Cross-references
- UT §4 IMO Middle cites D-1700-04 (workflow order)
- UT §7 STOP CONDITIONS cites D-1700-02 (source isolation), D-1700-03 (notebook ID lock)
- UT §8 DEPENDENCIES cites D-1700-05 (CF Stream requirement)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |
| Rule Count | 7 (D-1700-01 through D-1700-07) |

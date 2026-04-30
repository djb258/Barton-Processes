# 017 — Video CTB

Video content tree for SVG Agency and Barton Enterprises. Each folder is one video. Sources go in the `sources/` subfolder — add documents, notes, scripts, data, anything that should feed into the NotebookLM notebook for that video.

## CTB Structure

```
TRUNK — Barton Enterprises Overview
│   "The Machine" — IMO Creator, three businesses, how it's built
│
└── BRANCH — SVG Agency
    │
    ├── Outreach Overview
    │   How the data pipeline works — DOL filings, enrichment, 10-3-1
    │
    └── Sales (4 client-facing videos)
        │
        ├── 1. Fact Finder
        │   "What to expect, what to bring to our first meeting"
        │
        ├── 2. Insurance Education + Monte Carlo
        │   "Here's what we're going to cover — pricing, funding, simulations"
        │
        ├── 3. Cost Presentation
        │   "Understanding your insurance costs and options"
        │
        └── 4. Service
            "What happens after you become a client"
```

## Folders

| # | Folder | Notebook ID | Audience | Status |
|---|--------|-------------|----------|--------|
| 01 | barton-enterprises-overview | d36ab921-264d-40c1-8574-d3ffbcfef401 | General / LinkedIn | Sources draft |
| 02 | svg-outreach-overview | 8a1014a7-075d-4a1a-928f-256f6866b3bc | General / LinkedIn | Sources draft |
| 03 | svg-sales-factfinder | bfe9f7df-8c09-4d76-8839-4b7fd3c87023 | Client-facing (pre-meeting 1) | Sources draft |
| 04 | svg-sales-insurance-education | 1a5080d4-619b-4ac7-9576-32391bbf31e3 | Client-facing (pre-meeting 2) | Sources draft |
| 05 | svg-sales-cost-presentation | a681c244-7e48-4a64-a6e0-6b2ab045b14d | Client-facing (pre-meeting 3) | Sources draft |
| 06 | svg-sales-service | 44acfde8-467e-494a-8725-ba35076c7a0b | Client-facing (post-sale) | Sources draft |

## Workflow

1. Add source materials to `sources/` in the relevant folder
2. Paste/upload sources into the NotebookLM notebook (IDs above)
3. Generate video + other artifacts in NotebookLM Studio
4. Download artifacts → upload video to CF Stream → deploy to content-pages
5. Full process doc: `imo-creator-v2/factory/agents/notebooklm/references/content-pages-process.md`

## Adding Sources

Drop anything relevant into the `sources/` folder:
- Markdown docs, text files
- PDFs (sales materials, compliance docs, client handouts)
- Scripts or talking points
- Data exports or examples
- Links (save as .md with the URL and description)

Each source file in `sources/` gets pasted into the corresponding NotebookLM notebook. The more quality sources you add, the better the generated video.

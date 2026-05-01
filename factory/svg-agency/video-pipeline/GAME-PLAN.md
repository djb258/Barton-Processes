# Insurance Informatics — Tier 1 Video Game Plan (SVG-Agency Render Queue)
## The 8-block dependency-gated execution sequence for the first 15 Insurance Informatics videos. Blocks unlock in order. E-06 Duck Master goes first.
### Status: BUILD
### Medium: reference
### Business: svg-agency

---

## 📋 UT Checklist (Pre-Flight — per law/UT_CHECKLIST.md v1.2.0)

**Format carve-out:** Reference/spec document per atlas §1.0.6 precedent. Full 14-section UT carried by parent ratchet (`workers/video-pipeline/MANUAL.md` in imo-creator-v2). Items below reflect this doc's specific coverage.

| # | Check | Status | Location |
|---|-------|--------|----------|
| 1 | PRD — what / why / who / scope / out-of-scope / success metric | ☑ | §A |
| 2 | OSAM — partial (no DB writes) | ☑ | §A |
| 3 | Component Status — deps | ☑ | §A |
| 4 | Owner | ☑ | §1 |
| 5 | Live Dashboard — URL | ☑ | §1 |
| 6 | Kill Switch — N/A | ☑ | N/A — game plan has no kill switch |
| 7 | Logbook | ☐ | BUILD state |
| 8 | FCEs Attached | ☑ | N/A |
| 9 | BARs Referenced | ☑ | §1 |
| 10 | LBB Subjects Fed | ☑ | §1 |
| 11 | Geometry | ☑ | §1 |
| 12 | Live Verification | ☐ | BUILD state — no renders completed yet |
| 13 | ctb_node | ☑ | §1 |

---

## §1. IDENTITY

| Field | Value |
|-------|-------|
| ID | insurance-informatics-game-plan |
| Name | Insurance Informatics — Tier 1 Video Game Plan |
| ctb_node | barton-enterprises/svg-agency/video-pipeline/game-plan |
| Trunk Reference | `imo-creator-v2/workers/video-pipeline/MANUAL.md` (sub-hub 30) |
| Trunk Redirect | `imo-creator-v2/fleet/content/videos/GAME-PLAN.md` (pointer only) |
| ORBT | BUILD |
| Owner | Dave Barton |
| Last Modified | 2026-04-30 |
| BAR Reference | BAR-367 |
| Version | 1.1.0 |
| LBB Subject | svg-sales |
| Live Dashboard | https://studio.youtube.com (@InsuranceInformatics) |

---

## §A. PURPOSE

**WHAT:** The dependency-gated execution sequence for the first 15 Insurance Informatics YouTube videos. Organized into 8 blocks. Each block must be rendered and published before the next block unlocks. E-06 Duck Master (the flagship intro video) is Block 1 — it anchors all subsequent content.

**WHY:** Without a dependency-gated sequence, video production becomes random — content without strategic context, no build-up, no compound discovery. With the game plan: every video earns its place in the stack. Early blocks build credibility. Later blocks convert.

**WHO uses it:**
- Dave Barton (operator — executes blocks in order, checks off renders as they complete)
- Claude AI Brain (references this when generating scripts — must know where a video sits in the sequence)

**SCOPE:** Tier 1 videos only — the foundational 15-video stack for the Insurance Informatics channel. Does not cover Gate Series (client-facing) or deep-dive specialty content.

**SUCCESS METRIC:** All 8 blocks rendered and published in dependency order within the Tier 1 production window.

---

## §B. DEPENDENCY RULES

1. Block N+1 does not start until Block N is published (not just rendered — must be live on YouTube)
2. Within a block, videos may render in parallel if their scripts are complete
3. E-06 Duck Master is the anchor — every subsequent video assumes the viewer has seen it or can reference it
4. If a block video fails the re-render policy (Strike 3), the block is paused pending Troubleshoot/Train resolution
5. Script must be complete and Dave-approved before HeyGen render begins — no speculative renders

---

## §C. THE 8-BLOCK EXECUTION SEQUENCE

### Block 1 — The Anchor (render first, unlock all)

| ID | Title | CTB Altitude | Status |
|----|-------|-------------|--------|
| E-06 | Duck Master — Why Your Broker Doesn't Know What You're Paying | 50K | ☐ Pending |

**Block 1 unlock condition:** E-06 live on YouTube. All subsequent blocks reference this video.

---

### Block 2 — The Two Pillars (architecture foundation)

| ID | Title | CTB Altitude | Status |
|----|-------|-------------|--------|
| E-01 | The Two Pillars of Self-Funded Insurance | 50K | ☐ Pending |
| E-02 | Fixed Costs vs. Variable Costs: What Your Plan Actually Costs | 40K | ☐ Pending |

**Block 2 dependency:** Block 1 published.
**Block 2 unlock condition:** Both E-01 and E-02 live.

---

### Block 3 — The Vendor Layer (PEPM economics)

| ID | Title | CTB Altitude | Status |
|----|-------|-------------|--------|
| E-03 | How Your TPA Gets Paid (And Why It Matters) | 30K | ☐ Pending |
| E-04 | The PBM Problem: Why Drug Costs Keep Rising | 30K | ☐ Pending |
| E-07 | Stop-Loss Insurance: What Your Broker Won't Tell You | 30K | ☐ Pending |

**Block 3 dependency:** Block 2 published.
**Block 3 unlock condition:** All 3 Block 3 videos live.

---

### Block 4 — The Pool Split (the actuarial reveal)

| ID | Title | CTB Altitude | Status |
|----|-------|-------------|--------|
| E-08 | 90/15 vs. 10/85: The Number That Explains Your Health Insurance Bill | 20K | ☐ Pending |
| E-09 | Why Treating Every Employee the Same Costs You $400K a Year | 20K | ☐ Pending |

**Block 4 dependency:** Block 3 published.
**Block 4 unlock condition:** Both E-08 and E-09 live.

---

### Block 5 — The Hospital Waterfall

| ID | Title | CTB Altitude | Status |
|----|-------|-------------|--------|
| E-10 | The Hospital Bill Waterfall: Where Your Money Actually Goes | 10K | ☐ Pending |
| E-11 | Reference-Based Pricing: The Strategy Your Hospital Doesn't Want You to Know | 10K | ☐ Pending |

**Block 5 dependency:** Block 4 published.
**Block 5 unlock condition:** Both E-10 and E-11 live.

---

### Block 6 — The Drug Waterfall

| ID | Title | CTB Altitude | Status |
|----|-------|-------------|--------|
| E-12 | The Drug Cost Waterfall: Retail, Negotiated, Rebate, Net | 10K | ☐ Pending |
| E-13 | How PBM Rebates Work (And Who Actually Keeps the Money) | 10K | ☐ Pending |

**Block 6 dependency:** Block 5 published.
**Block 6 unlock condition:** Both E-12 and E-13 live.

---

### Block 7 — The Operating System (the data machine)

| ID | Title | CTB Altitude | Status |
|----|-------|-------------|--------|
| E-14 | The Insurance Informatics Dashboard: Real-Time Claims Data for Employers | 5K | ☐ Pending |
| E-05 | We Already Know Your Health Plan Setup — Here's How | 5K | ☐ Pending |

**Block 7 dependency:** Block 6 published.
**Block 7 unlock condition:** Both E-14 and E-05 live.

---

### Block 8 — The Conversion Close (Gate Series entry point)

| ID | Title | CTB Altitude | Status |
|----|-------|-------------|--------|
| E-15 | Is Self-Funded Right for Your Company? The 3 Questions to Answer First | 50K | ☐ Pending |

**Block 8 dependency:** Block 7 published.
**Block 8 unlock condition:** E-15 live. Tier 1 stack complete.
**Post-Block 8:** Gate Series begins (client-facing content — separate game plan).

---

## §D. VIDEO METADATA TEMPLATE

For each video in the sequence, maintain a render record:

| Field | Value |
|-------|-------|
| Video ID | E-XX |
| Title | Final YouTube title (60 char max) |
| Script Status | Draft / Dave-Approved / Final |
| Render Date | YYYY-MM-DD |
| Render Strikes | 0 / 1 / 2 / 3 |
| YouTube URL | https://youtube.com/watch?v=... |
| Published Date | YYYY-MM-DD |
| Block | 1–8 |

---

## §E. RENDER LOG

| Date | Video ID | Action | Strike Count | Outcome |
|------|----------|--------|-------------|---------|
| — | — | No renders completed yet | — | BUILD state |

---

## §F. MAINTENANCE LOGBOOK

| Date | Actor | Action | Outcome |
|------|-------|--------|---------|
| 2026-04-30 | Sonnet (Mechanic, BAR-367) | Moved from imo-creator-v2 to Barton-Processes. Updated ctb_node. Added cross-references to trunk doc. Version bumped to 1.1.0. Expanded video metadata template and render log sections. | BUILD state. Canonical location is now this file. Trunk has redirect stub. |

---

## §G. VERSION HISTORY

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-04-30 | Initial version (was in imo-creator-v2, moved to Barton-Processes per BAR-367). |
| 1.1.0 | 2026-04-30 | Updated ctb_node to Barton-Processes path. Added video metadata template and render log. Added cross-references. |

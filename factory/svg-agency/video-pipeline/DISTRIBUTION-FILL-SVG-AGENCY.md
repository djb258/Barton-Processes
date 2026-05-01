# Distribution Fill — SVG-Agency (@InsuranceInformatics)
## The SVG-Agency socket fill for the trunk distribution adapter. IL-specific hashtag fills, optional pool, and channel metadata for the @InsuranceInformatics YouTube channel.
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
| 6 | Kill Switch — N/A | ☑ | N/A — distribution fill has no kill switch |
| 7 | Logbook | ☐ | BUILD state |
| 8 | FCEs Attached | ☑ | N/A |
| 9 | BARs Referenced | ☑ | §1 |
| 10 | LBB Subjects Fed | ☑ | §1 |
| 11 | Geometry | ☑ | §1 |
| 12 | Live Verification | ☑ | §E — channel active |
| 13 | ctb_node | ☑ | §1 |

---

## §1. IDENTITY

| Field | Value |
|-------|-------|
| ID | distribution-fill-svg-agency |
| Name | Distribution Fill — SVG-Agency (@InsuranceInformatics) |
| ctb_node | barton-enterprises/svg-agency/video-pipeline/distribution-fill |
| Trunk Pattern Doc | `imo-creator-v2/fleet/content/videos/DISTRIBUTION-ADAPTER.md` |
| Parent Ratchet | `imo-creator-v2/workers/video-pipeline/MANUAL.md` (sub-hub 30) |
| ORBT | BUILD |
| Owner | Dave Barton |
| Last Modified | 2026-04-30 |
| BAR Reference | BAR-367 |
| Version | 1.0.0 |
| LBB Subject | svg-sales |
| Live Dashboard | https://studio.youtube.com (@InsuranceInformatics) |

---

## §A. PURPOSE

**WHAT:** The SVG-Agency socket fill for the trunk 6-element hashtag formula. The trunk adapter (`DISTRIBUTION-ADAPTER.md`) defines the pattern (constant). This file provides the IL-specific values (variable) that fill the pattern for the @InsuranceInformatics channel.

**WHY:** The trunk pattern is domain-agnostic. Without a socket fill, the 6-element formula has no actual hashtags to use. This fill doc is the operational piece — what actually goes into each slot for every SVG-Agency video upload.

**WHO uses it:**
- Dave Barton (operator — fills hashtag slots per video before uploading)
- Claude AI Brain (§C of AI-BRAIN-SPEC.md references this for hashtag generation)
- `DISTRIBUTION-ADAPTER.md` trunk pattern (this file IS the variable referenced by §C)

---

## §A. 6-SLOT FILL TABLE

| Slot | Fill |
|------|------|
| 1 — Branded | `#InsuranceInformatics` |
| 2 — Creator | `#DaveBarton` |
| 3 — Domain | `#SelfFundedInsurance` or `#EmployerHealthcare` or topic-specific (see §B rotation rules) |
| 4 — Problem | Topic-specific (Claude AI Brain selects per video — see INSURANCE-INFORMATICS-AI-BRAIN-SPEC.md §C) |
| 5 — Audience | `#HRLeaders` or `#CFO` or `#SmallBusiness` (Claude AI Brain selects per video) |
| 6 — Trust | Rotate: `#NoCommission` or `#FlatFee` or `#DataDriven` (see §B rotation rules) |

**Slots 1 and 2** are LOCKED. Never swap `#InsuranceInformatics` or `#DaveBarton`.

**Slot 3 rotation rules:**
- Default: `#SelfFundedInsurance` (highest-volume, broadest signal)
- Use `#EmployerHealthcare` when the video targets large employer audiences
- Use topic-specific domain tag when the video covers a specific mechanism (e.g., `#StopLossInsurance` for stop-loss videos)

**Slot 6 rotation rules:**
- `#NoCommission` — lead trust signal. Use when video directly addresses broker conflict or fee structure.
- `#FlatFee` — use when video explains Dave's compensation model.
- `#DataDriven` — use when video focuses on data, dashboards, or analytics.
- Default when uncertain: `#NoCommission`

---

## §B. OPTIONAL HASHTAG POOL (IL-Specific)

Use 1–2 from this pool as extras beyond the 6-element base when the video topic warrants it. Add to the last paragraph of the YouTube description only.

| Hashtag | When to Use |
|---------|-------------|
| `#MonteCarlo` | Videos covering the 90/15 vs 10/85 pool analysis |
| `#StopLoss` | Videos about stop-loss mechanics or attachment points |
| `#TPA` | Videos covering Third Party Administrators |
| `#PBM` | Videos covering Pharmacy Benefit Managers |
| `#501R` | Videos covering hospital charity care waterfall |
| `#ReferenceBasedPricing` | Videos covering RBP hospital pricing strategy |
| `#CaptiveInsurance` | Videos covering captive structure |
| `#HealthcareCosts` | High-search-volume tag — use when generally relevant |
| `#InsuranceBroker` | When video directly addresses broker conflict of interest |
| `#EmployeeBenefits` | Broad audience catch — high search volume, use for reach |
| `#BenefitsStrategy` | When video covers plan design strategy |
| `#HealthcareCostContainment` | When video covers cost-reduction mechanisms |

---

## §C. CHANNEL METADATA

| Field | Value |
|-------|-------|
| Channel | @InsuranceInformatics |
| YouTube Category | Education (Category 27) |
| Channel URL | https://youtube.com/@InsuranceInformatics |
| Target audience | HR Leaders, CFOs, Small Business Owners (50–500 employees) |
| Monetization target | $200K/mo (see JULIA-MCCOY-AVATAR-WORKFLOW.md in imo-creator-v2) |
| Primary content theme | Self-funded insurance, healthcare cost containment, Insurance Informatics CTB architecture |

### Playlist Structure

| Playlist | CTB Altitude | Videos Belong Here |
|----------|-------------|-------------------|
| What Is Insurance Informatics | 50K | Channel introduction, discipline overview |
| The Two Pillars | 40K | Fixed + Variable pillar architecture |
| How It Works | 30K | PEPM vendors, TPA mechanics, PBM mechanics |
| Your Numbers | 20K | 90/15 vs 10/85, Monte Carlo, pool split |
| The Waterfalls | 10K | Hospital + drug waterfall paths |
| The Operating System | 5K | Dashboards, employee tickets, data warehouse |
| Gate Series | Sales | Gate 1–4 meeting prep videos |

---

## §D. CLI UPLOAD REFERENCE

```bash
# SVG-Agency standard hashtag string for CLI uploads
# Replace slots 3-5 with video-specific selections; slots 1, 2, 6 per rotation rules above
TAGS="#InsuranceInformatics,#DaveBarton,#SelfFundedInsurance,#HealthcareCosts,#HRLeaders,#NoCommission"

# Upload via heygen-dop CLI
YT_ID=$(heygen-dop upload-yt ./output/video.mp4 "$TITLE" "$DESCRIPTION" "$TAGS")
echo "YouTube URL: https://youtube.com/watch?v=$YT_ID"
```

---

## §E. COMPONENT STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Channel | ACTIVE | @InsuranceInformatics live |
| 6-slot fill | LOCKED | §A above — do not modify slots 1-2 |
| Optional pool | ACTIVE | §B above — add new tags here as needed |
| Playlist structure | BUILD | Playlists to be created when first videos publish |

---

## §F. MAINTENANCE LOGBOOK

| Date | Actor | Action | Outcome |
|------|-------|--------|---------|
| 2026-04-30 | Sonnet (Mechanic, BAR-367) | Created DISTRIBUTION-FILL-SVG-AGENCY.md v1.0.0. Extracted IL-specific fill from trunk DISTRIBUTION-ADAPTER.md §C and §D. Added optional pool, channel metadata, playlist structure, CLI reference. | BUILD state. Trunk is now domain-agnostic. This file is the SVG-Agency socket variable. |

---

## §G. VERSION HISTORY

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-04-30 | Initial fill doc. Extracted from imo-creator-v2 DISTRIBUTION-ADAPTER.md §C + §D per BAR-367 cross-repo restructure. |

# Production Standards — SVG-Agency (@InsuranceInformatics)
## The SVG-Agency socket fill for the trunk production standards framework. Avatar, voice, branding, platform, and re-render policy for the @InsuranceInformatics YouTube channel.
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
| 3 | Component Status — deps | ☑ | §E |
| 4 | Owner | ☑ | §1 |
| 5 | Live Dashboard — URL | ☑ | §1 |
| 6 | Kill Switch — N/A | ☑ | N/A — production standards have no kill switch |
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
| ID | production-standards-svg-agency |
| Name | Production Standards — SVG-Agency (@InsuranceInformatics) |
| ctb_node | barton-enterprises/svg-agency/video-pipeline/production-standards |
| Trunk Framework Doc | `imo-creator-v2/fleet/content/videos/PRODUCTION-STANDARDS-FRAMEWORK.md` |
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

**WHAT:** The SVG-Agency socket fill for the trunk production standards framework. The trunk framework (`PRODUCTION-STANDARDS-FRAMEWORK.md`) defines the 7 slots every branch must fill. This file contains the locked SVG-Agency values for all 7 slots — Dave's actual avatar IDs, voice IDs, logo specs, platform matrix, and re-render policy.

**WHY:** Production decisions are not per-video decisions. They are constants. Locking them here means every HeyGen render starts from the same baseline — same avatar, same voice, same logo, same specs. Drift is eliminated at the source.

**WHO uses it:**
- Dave Barton (operator — reads this before every render session)
- Claude AI Brain (references production parameters during content generation)
- HeyGen operator (uses avatar IDs and voice IDs directly)

---

## §B. SLOT FILLS (The 7 Locked Production Standards)

### Slot 1 — Primary Voice

| Field | Value |
|-------|-------|
| Voice ID | `6bddf71228964cd59d74d62fc1070fb3` |
| Voice Name | "Fish" (Dave's primary voice) |
| Voice Source | HeyGen-native |
| Fallback Voice | TBD — designate if "Fish" becomes unavailable |

**LOCKED.** Do not use any other voice for SVG-Agency videos without updating this doc and Dave's explicit approval.

---

### Slot 2 — Primary Avatar

| Field | Value |
|-------|-------|
| Avatar ID (default) | `cf8be1f92db345458a24fbbdfc368faa` |
| Avatar Description (default) | Black shirt, dark background |
| Avatar ID (variation) | `f2f245dd75514a78a96feec067f0dd9b` |
| Avatar Description (variation) | Blue shirt |
| Selection Rule | Use default (black shirt) for all standard videos. Use blue shirt variation for content where lighter visual tone is appropriate (e.g., introductory explainers). When uncertain: use default. |

**LOCKED.** Maximum 2 approved avatar variants. Any additional variant requires Dave's explicit approval and a doc update before use.

---

### Slot 3 — Branding / Logo

| Field | Value |
|-------|-------|
| Logo Asset Path | `imo-creator-v2/fleet/content/logos/locked/insurance-informatics-presentation.png` |
| Logo Placement | Every video — position per HeyGen template design (lower-right or opening card) |
| Logo Required | YES — every SVG-Agency video carries the Insurance Informatics logo. No exceptions. |
| Background Asset Path | `imo-creator-v2/fleet/content/logos/locked/heygen-background.png` |

**LOCKED.** Logo is non-negotiable. A render without the Insurance Informatics logo is an automatic Strike 1 defect.

---

### Slot 4 — Platform / Aspect Ratio Matrix

| Platform | Aspect Ratio | Status | Notes |
|----------|-------------|--------|-------|
| YouTube | 16:9 | ACTIVE | Primary distribution platform |
| LinkedIn | 16:9 | ACTIVE | Secondary distribution — same render as YouTube |
| CF Pages Embed | 16:9 | ACTIVE | Content pages embed — same render as YouTube |
| YouTube Shorts | 9:16 | DEFERRED | Not in current production cycle — revisit post-Block 4 |
| Instagram Reels | 9:16 | DEFERRED | Not in current production cycle |

**One render serves YouTube + LinkedIn + CF Pages.** No separate renders for 16:9 platforms. Shorts and Reels are deferred — do not produce until this doc is updated.

---

### Slot 5 — Re-Render Policy (Aviation Model)

Following the trunk framework 3-strike policy with SVG-Agency-specific escalation triggers:

| Strike | Action |
|--------|--------|
| Strike 1 | Repair defect and re-render. Log defect type in §E Render Log. |
| Strike 2 | Escalate to Dave for review before re-render. Root cause required in writing. |
| Strike 3 | Troubleshoot/Train — do not re-render until failure mode is classified and prevention control is added to this doc. Issue Airworthiness Directive if failure mode affects all IL videos. |

**Automatic Strike 2 escalation (regardless of strike count):**
- Wrong avatar ID used (not on approved list above)
- Wrong voice ID used (not "Fish")
- Insurance Informatics logo missing from render
- Video published without correct hashtag formula (slots 1-6 incomplete)

---

### Slot 6 — Render Duration Standards

| Field | Value |
|-------|-------|
| Target video length | 3:00–5:00 (three to five minutes) |
| Maximum video length | 7:00 (hard ceiling — YouTube algorithm penalty above this for educational content) |
| Minimum video length | 2:00 (floor — anything shorter lacks sufficient teaching value) |
| Script word count target | 450–750 words (at Dave's natural speaking pace of ~150 wpm) |

---

### Slot 7 — File Naming Convention

| Field | Value |
|-------|-------|
| Raw render filename | `il-[video-id]-[YYYYMMDD]-raw.mp4` (e.g., `il-e06-20260430-raw.mp4`) |
| Final filename | `il-[video-id]-[YYYYMMDD]-final.mp4` (e.g., `il-e06-20260430-final.mp4`) |
| Archive path | `output/svg-agency/[video-id]/` |

---

## §C. COMPONENT STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Primary voice "Fish" | ACTIVE — LOCKED | Voice ID: `6bddf71228964cd59d74d62fc1070fb3` |
| Default avatar (black shirt) | ACTIVE — LOCKED | Avatar ID: `cf8be1f92db345458a24fbbdfc368faa` |
| Variation avatar (blue shirt) | ACTIVE — LOCKED | Avatar ID: `f2f245dd75514a78a96feec067f0dd9b` |
| Insurance Informatics logo | ACTIVE — LOCKED | Path: `imo-creator-v2/fleet/content/logos/locked/insurance-informatics-presentation.png` |
| YouTube (16:9) | ACTIVE | Primary platform |
| LinkedIn (16:9) | ACTIVE | Same render as YouTube |
| CF Pages Embed (16:9) | ACTIVE | Same render as YouTube |
| YouTube Shorts (9:16) | DEFERRED | Not in current production |
| Instagram Reels (9:16) | DEFERRED | Not in current production |

---

## §D. HEYGEN RENDER QUICK-REFERENCE

Before every HeyGen render session, verify:

```
Avatar ID (default):    cf8be1f92db345458a24fbbdfc368faa  (black shirt)
Avatar ID (variation):  f2f245dd75514a78a96feec067f0dd9b  (blue shirt)
Voice ID ("Fish"):      6bddf71228964cd59d74d62fc1070fb3
Logo:                   insurance-informatics-presentation.png — REQUIRED on every video
Aspect ratio:           16:9 (YouTube / LinkedIn / CF Pages)
Duration target:        3:00–5:00 (450–750 words)
```

---

## §E. RENDER LOG

| Date | Video ID | Avatar Used | Voice Used | Logo Present | Strike Count | Status |
|------|----------|-------------|------------|-------------|-------------|--------|
| — | — | — | — | — | — | No renders yet |

---

## §F. MAINTENANCE LOGBOOK

| Date | Actor | Action | Outcome |
|------|-------|--------|---------|
| 2026-04-30 | Sonnet (Mechanic, BAR-367) | Created PRODUCTION-STANDARDS-SVG-AGENCY.md v1.0.0. Locked all 7 slots with Dave's actual production defaults: voice "Fish" (HeyGen-native), default avatar (black shirt), variation avatar (blue shirt), IL logo (required on every video), platform matrix (YouTube+LinkedIn+CF Pages active; Shorts deferred), 3-strike re-render policy, duration 3-5 min, file naming convention. | BUILD state. All SVG-Agency production constants locked. Ready for first render session. |

---

## §G. VERSION HISTORY

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-04-30 | Initial production standards fill for SVG-Agency. All 7 slots from trunk framework filled with Dave's locked defaults. BAR-367. |

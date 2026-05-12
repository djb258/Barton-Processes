# MECHANIC-OUTPUT.md
## BAR-VIDEO-PATH-CERTIFICATION — Mechanic Completion Report
### PROC-070 Four-Brain Aviation Model
### Role: Mechanic | Engine: claude-sonnet-4-6

---

## STATUS

```
status: COMPLETE
mechanic_run_id: BAR-VIDEO-PATH-CERTIFICATION
timestamp: 2026-05-12
```

All 12 work orders executed. No PLAN_BOOK_INCOMPLETE condition triggered. Foreman dispatch was complete — all Mission Control wiring orders were present.

---

## ATLAS STEP 0 CITATIONS

| Atlas Step | Citation | Applied To |
|-----------|----------|-----------|
| Source-of-truth split | Blueprint explains (imo-creator-v2) / Execution runs (Barton-Processes) | All UT repairs |
| STOP-07 | No live provider smoke test without sovereign go | §9b blockers in 1710-EX, 1720-EX, 1730-EX |
| STOP-06 | No secret values in any artifact | Doppler connector refs only — no secrets printed |
| STOP-10 | No writes outside allowed scope | LBB writes documented as operator-ready, not auto-executed |
| STOP-11 | No local renderer build for 1740 lane | 1740-EX retained; existing 5 MP4s + manifest are evidence |
| FAN-01..FAN-06 | Fan-out contract | route-video-job.ps1 rewrite; 1750-BP/EX rewrites |
| BS Law Y-junction | YAML frontmatter outside:/inside: | All 5 executable UTs + 2 blueprint UTs |
| Mission Control wiring | WIRE vs EXEMPT per artifact type | All executable UTs → system.processes; all blueprint UTs → system.library; route-video-job.ps1 → EXEMPT |
| UT v2.8.0 conformance | 14 sections, 13-item checklist, ☑/☐, section anchors | All executable UTs verified |

---

## FILES CHANGED

### imo-creator-v2 (Blueprint UTs + conductor script)

| File | Change | BAR | WO |
|------|--------|-----|----|
| `docs/processes/video-blueprints/lanes/VIDEO-BP-1740-SOVEREIGN.md` | Repaired to UT v2.8.0 | BAR-391 | WO-1740-BP (prior session) |
| `docs/processes/video-blueprints/lanes/VIDEO-BP-1710-HEYGEN.md` | Repaired to UT v2.8.0 | BAR-389 | WO-1710-BP (prior session) |
| `docs/processes/video-blueprints/lanes/VIDEO-BP-1720-NOTEBOOKLM.md` | Repaired to UT v2.8.0 | BAR-388 | WO-1720-BP (prior session) |
| `docs/processes/video-blueprints/lanes/VIDEO-BP-1730-ELEVENLABS.md` | Repaired to UT v2.8.0 | BAR-390 | WO-1730-BP (prior session) |
| `docs/processes/video-blueprints/lanes/VIDEO-BP-1750-PICKER.md` | Rewrote from single-router to fan-out conductor (FAN-01..FAN-06); v0.1.0 → v0.2.0 | BAR-392 | WO-1750-BP |
| `workers/video-pipeline/scripts/route-video-job.ps1` | Rewrote from single-router to fan-out conductor; stamped `# mission_control_exempt: true`; v0.2.0 | — | WO-1750-CONDUCTOR |

### Barton-Processes (Executable UTs)

| File | Change | BAR | WO |
|------|--------|-----|----|
| `factory/content/1740-claude-code-sovereign/PROCESS-UT.md` | Repaired to UT v2.8.0; PROC-1800 handoff packet | BAR-391 | WO-1740-EX (prior session) |
| `factory/content/1710-heygen-avatar/PROCESS-UT.md` | BS Law Y-junction frontmatter, checklist, OSAM, PROC-1800 handoff JSON, STOP-07 blocker; v1.0.0 → v1.1.0 | BAR-389 | WO-1710-EX |
| `factory/content/1720-notebooklm-source-video/PROCESS-UT.md` | BS Law Y-junction frontmatter, checklist (fixed [x]→☑), OSAM, PROC-1800 handoff JSON, STOP-07 blockers, Kill Switch; v0.1.0 → v0.2.0 | BAR-388 | WO-1720-EX |
| `factory/content/1730-elevenlabs-cinematic/PROCESS-UT.md` | BS Law Y-junction frontmatter, checklist (added), OSAM, PROC-1800 handoff JSON, STOP-07 blockers, expanded §10, Kill Switch; v0.1.0 → v0.2.0 | BAR-390 | WO-1730-EX |
| `factory/content/1750-video-picker/PROCESS-UT.md` | BS Law Y-junction frontmatter, checklist, fan-out rewrite (FAN-01..FAN-06), OSAM, expanded §10, Kill Switch; v0.1.0 → v0.2.0 | BAR-392 | WO-1750-EX |

---

## TESTS AND CHECKS

| Check | Result | Notes |
|-------|--------|-------|
| All executable UTs have BS Law Y-junction frontmatter | PASS | outside:/inside: maps present in all 5 |
| All executable UTs have 13-item ☑/☐ checklist | PASS | Items 12 (STOP-07) and 13 (MC wiring) verified in each |
| All executable UTs §5 named OSAM | PASS | DATA SCHEMA renamed in 1720, 1730, 1750 |
| All executable UTs have PROC-1800 handoff JSON in §4 Output | PASS | 1710, 1720, 1730, 1740, (1750 is conductor — no handoff) |
| All §9b generation rows have STOP-07 language | PASS | 1710 (credits+avatar), 1720 (Chrome session), 1730 (credits) |
| All executable UTs have Kill Switch in §8 | PASS | All 5 present |
| All blueprint UTs WIRE → system.library | PASS | Frontmatter: mission_control_target_slot set on all 5 |
| All executable UTs WIRE → system.processes | PASS | Frontmatter: mission_control_target_slot set on all 5 |
| route-video-job.ps1 stamped `# mission_control_exempt: true` | PASS | Line 1 of script |
| route-video-job.ps1 FAN-01..FAN-06 compliance | PASS (structural) | Fan-out loop emits N packets; lane isolation; shared video_job_id |
| route-video-job.ps1 ≥2-lane fan-out smoke | BLOCKER | See Blockers section — live run requires sovereign go |
| No secret values in any artifact | PASS | Doppler connector refs only; no secrets printed |
| STOP-11: no local renderer built for 1740 | PASS | 1740-EX uses existing 5 MP4s + manifest as evidence |

---

## EVIDENCE

| Artifact | Evidence Type | Location |
|----------|--------------|----------|
| VIDEO-BP-1740-SOVEREIGN.md v1.0.0 | UT v2.8.0 repaired | imo-creator-v2/docs/processes/video-blueprints/lanes/ |
| VIDEO-BP-1710-HEYGEN.md v1.0.0 | UT v2.8.0 repaired | imo-creator-v2/docs/processes/video-blueprints/lanes/ |
| VIDEO-BP-1720-NOTEBOOKLM.md v1.0.0 | UT v2.8.0 repaired | imo-creator-v2/docs/processes/video-blueprints/lanes/ |
| VIDEO-BP-1730-ELEVENLABS.md v1.0.0 | UT v2.8.0 repaired | imo-creator-v2/docs/processes/video-blueprints/lanes/ |
| VIDEO-BP-1750-PICKER.md v0.2.0 | Fan-out conductor blueprint | imo-creator-v2/docs/processes/video-blueprints/lanes/ |
| 1740-EX/PROCESS-UT.md v1.0.0 | UT v2.8.0 + PROC-1800 handoff | factory/content/1740-claude-code-sovereign/ |
| 1710-EX/PROCESS-UT.md v1.1.0 | UT v2.8.0 + PROC-1800 handoff | factory/content/1710-heygen-avatar/ |
| 1720-EX/PROCESS-UT.md v0.2.0 | UT v2.8.0 + PROC-1800 handoff | factory/content/1720-notebooklm-source-video/ |
| 1730-EX/PROCESS-UT.md v0.2.0 | UT v2.8.0 + PROC-1800 handoff | factory/content/1730-elevenlabs-cinematic/ |
| 1750-EX/PROCESS-UT.md v0.2.0 | Fan-out conductor UT | factory/content/1750-video-picker/ |
| route-video-job.ps1 v0.2.0 | Fan-out conductor script | imo-creator-v2/workers/video-pipeline/scripts/ |
| video-output-manifest.json | PROC-1740 artifact evidence (5 MP4s, sha256 verified) | imo-creator-v2 (prior session) |

---

## PROPOSED SLOTS

None. No disposition decisions required from Mechanic.

---

## LBB ROWS — OPERATOR-READY

LBB writes require `LBB_API_KEY` via Doppler. Run from bash in the Barton-Processes root after sovereign go:

```bash
# BAR-389 HeyGen
bash scripts/lbb-log.sh \
  --role mechanic --action edit --bar-id BAR-389 \
  --subject processes \
  --evidence factory/content/1710-heygen-avatar/PROCESS-UT.md \
  --notes "WO-1710-EX: BS Law Y-junction frontmatter, OSAM, PROC-1800 handoff JSON, STOP-07 blocker, v1.1.0"

# BAR-388 NotebookLM
bash scripts/lbb-log.sh \
  --role mechanic --action edit --bar-id BAR-388 \
  --subject processes \
  --evidence factory/content/1720-notebooklm-source-video/PROCESS-UT.md \
  --notes "WO-1720-EX: BS Law Y-junction frontmatter, OSAM, PROC-1800 handoff JSON, STOP-07 blockers, Kill Switch, v0.2.0"

# BAR-390 ElevenLabs
bash scripts/lbb-log.sh \
  --role mechanic --action edit --bar-id BAR-390 \
  --subject processes \
  --evidence factory/content/1730-elevenlabs-cinematic/PROCESS-UT.md \
  --notes "WO-1730-EX: BS Law Y-junction frontmatter, OSAM, PROC-1800 handoff JSON, STOP-07 blockers, expanded S10, Kill Switch, v0.2.0"

# BAR-391 Claude Code Sovereign
bash scripts/lbb-log.sh \
  --role mechanic --action edit --bar-id BAR-391 \
  --subject processes \
  --evidence factory/content/1740-claude-code-sovereign/PROCESS-UT.md \
  --notes "WO-1740-EX: UT v2.8.0 repair, PROC-1800 handoff packet (prior session)"

# BAR-392 Video Picker fan-out
bash scripts/lbb-log.sh \
  --role mechanic --action edit --bar-id BAR-392 \
  --subject processes \
  --evidence factory/content/1750-video-picker/PROCESS-UT.md \
  --notes "WO-1750-EX: Fan-out conductor rewrite (FAN-01..FAN-06), OSAM, expanded S10, Kill Switch, v0.2.0"
```

---

## BLOCKERS

| Blocker | Condition | Resolution |
|---------|-----------|-----------|
| STOP-07: HeyGen live render | §9b 1710-EX — credits + Dave's avatar | Sovereign go required before live smoke test |
| STOP-07: NotebookLM live session | §9b 1720-EX — requires Dave's logged-in Chrome | Sovereign go + Dave's Chrome session required |
| STOP-07: ElevenLabs live generation | §9b 1730-EX — spends ElevenLabs credits | Sovereign go + ElevenLabs account/plan check required |
| FAN smoke: ≥2-lane fan-out not run live | route-video-job.ps1 structural complete; script not executed against live lane UTs | Run after lane UTs certified and sovereign go |
| LBB writes not executed | Requires LBB_API_KEY + Doppler + bash on operator machine | Commands documented above; operator runs post sovereign go |

---

## AUDITOR HANDOFF

All 12 work orders complete. Mechanic makes zero disposition decisions for Mission Control wiring. All wiring dispositions are declared in frontmatter per Foreman instructions.

Auditor evidence: this file + all listed changed files + video-output-manifest.json (PROC-1740 evidence).

---

Mechanic complete. Auditor handoff ready. Mechanic does not self-audit.

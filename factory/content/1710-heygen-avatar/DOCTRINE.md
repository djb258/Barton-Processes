# DOCTRINE — Process 1710 HeyGen Avatar/Cinematic Video
## Locked per-process rules. Auditor enforces. Violations halt render or trigger REPAIR before dispatch.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-1710-01 | Every render must use a verified HeyGen digital twin belonging to Dave Barton. An avatar ID that has not been identity-verified through HeyGen's first-party consent process may not be used. If the avatar cannot be confirmed as Dave's verified twin → HALT. | PROCESS-UT.md §7 Constants, §8 Stop Conditions; JULIA-MCCOY-AVATAR-WORKFLOW.md Cautions | pre-flight — unverified avatar halts all render dispatch |
| D-1710-02 | Every cinematic prompt (for Avatar Shots, Video Agent, AI Video Generator) must contain all four slots: setting/mood, avatar action, camera movement, and audio. A prompt missing one or more slots is structurally incomplete → REPAIR before render. The four slots are the constant; the fills are the variable. | PROCESS-UT.md §4 IMO Middle Step 4, §7 Constants; HEYGEN-CINEMATIC-VIDEO-RESEARCH.md Prompt Formula | §8 stop — incomplete prompt → REPAIR |
| D-1710-03 | B-roll shots generated via Avatar Shots or AI Video Generator default to 4–15 seconds duration. This range is domesticated for B-roll purposes. Full A-roll or full-video generation (Video Agent) declares its own duration per job. | PROCESS-UT.md §7 Constants; JULIA-MCCOY-AVATAR-WORKFLOW.md Setup Steps | render parameter constraint |
| D-1710-04 | Reference media supplied to HeyGen for cinematic style guidance must be brand/product images, product screenshots, or other brand-safe visuals. Real human faces (photos or video frames of any person other than Dave's verified digital twin) are forbidden as reference input for Seedance/cinematic generation. | PROCESS-UT.md §7 Constants, §8 Stop Conditions; HEYGEN-CINEMATIC-VIDEO-RESEARCH.md Cautions | pre-flight — real human face reference → HALT |
| D-1710-05 | Output orientation must be declared per render. Accepted values: `16:9` (YouTube, LinkedIn, CF Pages default), `9:16` (short/vertical), `1:1` (square). No render may dispatch without an explicit orientation declaration. | PROCESS-UT.md §7 Constants; VIDEO-MARKETING-CV-RESEARCH.md heygen_avatar path | render parameter constraint |
| D-1710-06 | Voice provider and voice ID are variable fill, not architecture. No worker, script, or workflow may hardcode a specific voice ID as a structural dependency. The voice slot (provider + id_or_name) is the constant; the voice selected for a specific render is the variable. Phase 1 default: HeyGen-native voice `Fish` (`6bddf71228964cd59d74d62fc1070fb3`). ElevenLabs PVC routing is deferred to Phase 2 per Dave's sovereign decision 2026-04-30. | PROCESS-UT.md §7 Constants, §8 Stop Conditions; JULIA-MCCOY-AVATAR-WORKFLOW.md §C Step 2 | pre-flight — hardcoded voice → REPAIR |
| D-1710-07 | Features that are UI-only in Dave's HeyGen account (Avatar Shots, Video Agent, AI Video Generator, Enhance) must declare an explicit browser automation path (Chrome MCP) before the process step that invokes them. A UI-only step with no declared automation path → HALT. The preferred invocation is API where stable; Chrome MCP is the official fallback for UI-only features. | PROCESS-UT.md §4 IMO Middle, §8 Stop Conditions; BAR-VIDEO-LANE-UTS.plan.md §9 Access/API Matrix | §8 stop — UI-only + no browser path → HALT |
| D-1710-08 | A-roll and B-roll serve structurally distinct purposes. A-roll (direct-to-camera avatar speech) carries the argument and information density. B-roll (cinematic shots, Avatar Shots, AI Video Generator output) carries attention, emotion, and visual memory. Do not substitute B-roll for A-roll content or vice versa. The join structure is: A-roll determines the narrative arc; B-roll is layered over and between A-roll to serve the narrative. | PROCESS-UT.md §7 Constants; HEYGEN-CINEMATIC-VIDEO-RESEARCH.md A-Roll/B-Roll Join | structural join rule — not enforced by code, enforced by review |
| D-1710-09 | `HEYGEN_API_KEY` must be available from Doppler (imo-creator → dev) before any render dispatch. If the key is absent, expired, or cannot be retrieved → HALT. The key must not be stored in plaintext in any script, UT, or committed file. | PROCESS-UT.md §3 Secrets, §8 Stop Conditions | pre-flight — missing API key → HALT |
| D-1710-10 | Every completed render (successful or failed) must produce a LBB record in the `processes` subject containing: job_id, constants_packet (avatar, voice, format), output_url (or error), and timestamp. Missing LBB ingest breaks the Circle and severs traceability. | PROCESS-UT.md §4 IMO Middle Step 9, §5 WRITE Access | post-render requirement — omission = open loop |

## Cross-references
- PROCESS-UT.md §4 IMO Middle cites D-1710-01 (identity gate), D-1710-02 (prompt slots), D-1710-07 (browser path)
- PROCESS-UT.md §7 Constants cites D-1710-01 (avatar IDs), D-1710-03 (B-roll duration), D-1710-06 (voice variable)
- PROCESS-UT.md §8 Stop Conditions cites D-1710-01, D-1710-02, D-1710-04, D-1710-06, D-1710-07, D-1710-09

## Document Control

| Field | Value |
|---|---|
| Created | 2026-05-04 |
| Last Modified | 2026-05-04 |
| Version | 1.0.0 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |
| Rule Count | 10 (D-1710-01 through D-1710-10) |
| BAR | BAR-389 |

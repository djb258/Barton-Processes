# DOCTRINE — PROC-1720 NotebookLM Source Video
## Local locked rules for the Chrome MCP browser automation lane.
### Status: BUILD
### Process: PROC-1720
### BAR: BAR-388

These rules are LOCAL to PROC-1720. They supplement (never contradict) the parent doctrine in `atlas/constants/FOUNDATIONAL_BEDROCK.md` and the Barton Enterprises Atlas. If any rule below conflicts with a locked constant, the locked constant wins.

---

## D-1720-01 — Chrome MCP is the Only Access Surface

NotebookLM has no stable public API for video generation. All notebook creation, source ingestion, and video artifact generation MUST be performed via Chrome DevTools MCP (browser automation). Direct HTTP calls to notebooklm.google.com are FORBIDDEN except as incidental browser-navigation traffic controlled by the MCP session.

**Trigger:** Any attempt to construct a raw HTTP POST or REST call to notebooklm.google.com from code or a worker.
**Action:** HALT immediately. Raise as a stop condition. Log to LBB.

---

## D-1720-02 — No Raw Google Credentials in This Process

Authentication for NotebookLM is provided exclusively through a logged-in Chrome session for Dave's Google account. No OAuth tokens, passwords, session cookies, or Google API keys may be written into this UT, the heir.yaml, the orbt.yaml, any workflow YAML, or any companion script.

If the Chrome session expires mid-run, the run is HALTED (see §8 stop conditions). The operator re-authenticates in the browser; the run is re-dispatched.

**Trigger:** Any file in this process folder containing a Google credential value.
**Action:** Remove immediately. Log the violation to LBB subject `processes`.

---

## D-1720-03 — Source Count Verification is Non-Negotiable

Before triggering video generation, `sources_loaded_count` MUST equal the expected source count from the source_packet. Partial source ingestion produces an artifact that is not traceable to the complete source_packet — this breaks artifact lineage.

**Trigger:** sources_loaded_count < source_packet.count at Step 4.
**Action:** HALT. Do not trigger generation. Log mismatched sources to LBB. Return FAILED status to PROC-1750.

---

## D-1720-04 — Artifact Verification Before Handoff

The handoff file written at Step 9 MUST NOT be written before `artifact_verified = true` (file exists, size > 0). PROC-1800 trusts the handoff file as a signed delivery receipt. Writing it before verification creates a phantom path that PROC-1800 cannot distinguish from a valid path.

**Trigger:** Code or automation attempts to write handoff_file_path before artifact_download_path verification passes.
**Action:** HALT at Step 9 preamble. Log phantom-path attempt to LBB.

---

## D-1720-05 — Every Run Writes an LBB Record

Every run of PROC-1720, whether successful or failed, MUST write a record to the LBB `processes` subject. The record MUST include: source_packet_id, notebook_id, artifact_id (null if failed), run status, and failure step + error_code if applicable.

A run with no LBB record is an invisible run. Invisible runs break the Circle (Bedrock §5) and prevent sigma tracking.

**Trigger:** End of run (Step 10) skipped for any reason.
**Action:** Escalate to Strike 1 immediately. Run is invalid for analytics purposes.

---

## D-1720-06 — notebook_id is Variable, Not Architecture

The `notebook_id` field is a per-source_packet variable. Do NOT hardcode a notebook_id into any workflow, configuration, or downstream system. New source packets may create new notebooks; existing source packets may reuse a prior notebook. The join key is always `source_packet_id -> notebook_id` stored in LBB.

**Trigger:** notebook_id appears as a hardcoded value in any YAML, script, or config.
**Action:** Replace with a runtime lookup from LBB by source_packet_id.

---

## D-1720-07 — This Lane Produces Video Only

PROC-1720 is strictly a video artifact lane. If a source packet requests audio-only (podcast), document summary, or any other artifact type, PROC-1720 MUST return WRONG_LANE to PROC-1750 and stop. It is not this process's job to produce non-video artifacts.

**Trigger:** target_output_type != `video` at Step 1 intake.
**Action:** Return WRONG_LANE to PROC-1750. Do not open or modify any notebook.

---

## Document Control

| Field         | Value       |
|---------------|-------------|
| Created       | 2026-05-04  |
| Last Modified | 2026-05-04  |
| Version       | 0.1.0       |
| Status        | BUILD       |
| BAR           | BAR-388     |
| Authority     | Dave Barton (sovereign for amendments) |

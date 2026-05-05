# DOCTRINE - PROC-1740 Claude Code Sovereign Video

## D-1740-01 - No Template, No Render

Every run must name a repo-owned template_id that resolves to a real template path.

## D-1740-02 - Render Command Is Required

The lane is not operational until it has an exact deterministic render command.

## D-1740-03 - Manifest Is the Receipt

Every successful render must emit an output manifest with video_job_id, script reference, template_id, command, exit code, artifact_path, file size, and timestamp.

## D-1740-04 - Zero-Byte Output Fails

An output file with zero bytes is a failed render even if the command exits 0.

## D-1740-05 - Provider Independence

This lane should not depend on HeyGen, NotebookLM, or ElevenLabs for generation. Downstream storage may use CF/R2 after render.

## Document Control

| Field | Value |
|-------|-------|
| Process | PROC-1740 |
| BAR | BAR-391 |
| Status | BUILD |

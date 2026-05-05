# DOCTRINE - PROC-1730 ElevenLabs Cinematic

## D-1730-01 - Model Is Variable Fill

The architecture is the ElevenLabs cinematic model-picker lane. The selected model is never architecture. Do not hardcode a model as the only path.

## D-1730-02 - Cost Gate Before Generation

Every generation must know the plan/credit impact before dispatch. Unknown cost means REPAIR before generation.

## D-1730-03 - UI-Only Features Require Chrome MCP

If Image & Video functionality is only available in ElevenCreative UI or beta surfaces, the run must use Chrome MCP/browser automation. No undocumented API workaround.

## D-1730-04 - Reference Compatibility Gate

Start frame, end frame, image references, video references, audio references, duration, aspect ratio, and sound policy must be supported by the selected model before generation.

## D-1730-05 - Output Must Be Exportable

No run is complete until the output is downloadable, importable into ElevenCreative, or otherwise handed to a known storage surface.

## D-1730-06 - No Raw Secrets

No ElevenLabs API key or session token may be written to this folder.

## Document Control

| Field | Value |
|-------|-------|
| Process | PROC-1730 |
| BAR | BAR-390 |
| Status | BUILD |

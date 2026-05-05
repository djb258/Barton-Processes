# DOCTRINE - PROC-1750 Video Picker

## D-1750-01 - Exactly One Lane

Every valid intake must resolve to exactly one selected_path_id. Multiple matches require REPAIR. No match requires HALT.

## D-1750-02 - Picker Does Not Generate

The picker emits lane packets only. It must not call HeyGen, NotebookLM, ElevenLabs, render commands, or CF Stream directly.

## D-1750-03 - Lane Packet Must Conform

No lane dispatch is valid unless the packet satisfies the selected lane input contract.

## D-1750-04 - Rationale Required

Every routing decision must include a concise rationale so the Circle can improve future choices.

## Document Control

| Field | Value |
|-------|-------|
| Process | PROC-1750 |
| BAR | BAR-392 |
| Status | BUILD |

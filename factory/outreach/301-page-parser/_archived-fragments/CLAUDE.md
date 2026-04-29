> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — PROC-301 Management Page Parser

## What This Is
Fetches leadership/team/about pages (about_url) discovered by Process 300 and parses names + titles for all 3 slot types (CEO, CFO, HR). One page fetch fills up to 3 slots per company.

## Pre-Flight
1. Read PROCESS.md first — understand the IMO, comparators, stop conditions
2. Query LBB for prior session learnings on this process
3. Check workbench: `SELECT COUNT(*) FROM slot_workbench WHERE about_url IS NOT NULL AND has_name = 0`
4. This process depends on 300-recon completing first (about_url must be populated)

## Boundaries
- Reads: slot_workbench (about_url, company_name, slot_type, has_name)
- Writes: slot_workbench (person_first_name, person_last_name, person_source)
- Does NOT set readiness_tier — that's computed by recalc_tier after writes
- Does NOT write person_email — that's Process 201
- Does NOT search Startpage — that's Process 300 (discovery) and Process 200 Gate C (fallback)

## Tools
- curl_cffi (chrome131 impersonation) — fetch pages
- DataImpulse proxy — residential proxy for page fetches
- Title Classifier (Snap-On Tool) — classify parsed titles to slot_type
- recalc_tier.py — run after all writes to update readiness tiers

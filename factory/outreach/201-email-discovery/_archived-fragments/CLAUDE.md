> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# CLAUDE.md — Process 201: Find Email

## Identity
- **Process:** PROC-201 (Find Email)
- **Business:** svg-agency
- **CTB Position:** factory/outreach/201-email-discovery
- **ORBT:** BUILD
- **Reads from:** slot_workbench (D1 svg-d1-outreach-ops)
- **Writes to:** slot_workbench (person_email, has_email, email_found_at)

## Pre-Flight
1. Read PROCESS.md in this directory
2. Read the slot_workbench schema
3. Check readiness: only process slots where has_name = 1 AND has_email = 0

## Gate Chain
- Gate A: email pattern exists → generate from pattern + name + domain
- Gate B: hunter_email exists with confidence >= 80 → promote
- Gate C: search Startpage → parse emails from results

## Script
- `src/find-email.py` — main execution script
- Args: --limit, --offset, --port-base, --dry-run, --resume, --gate (a|b|c|all)

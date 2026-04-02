# CLAUDE.md — Process 202: Find LinkedIn

## Identity
- **Process:** PROC-202 (Find LinkedIn)
- **Business:** svg-agency
- **CTB Position:** factory/outreach/202-linkedin-discovery
- **ORBT:** BUILD
- **Reads from:** slot_workbench (D1 svg-d1-outreach-ops)
- **Writes to:** slot_workbench (person_linkedin, has_linkedin, linkedin_found_at)

## Pre-Flight
1. Read PROCESS.md in this directory
2. Read the slot_workbench schema
3. Check readiness: only process slots where has_name = 1 AND has_linkedin = 0

## Gate Chain
- Gate A: match person name to recon_linkedin_people slugs → FREE
- Gate B: hunter_linkedin exists → promote
- Gate C: search Startpage "{first} {last} {company} linkedin"

## Script
- `src/find-linkedin.py` — main execution script
- Args: --limit, --offset, --port-base, --dry-run, --resume

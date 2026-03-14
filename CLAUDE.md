# CLAUDE.md — Barton-Processes

## IDENTITY

This is the **process engine** governed by **imo-creator**.

Blueprint repos are the **brain** (static schemas, doctrine, definitions — ZERO workers).
This repo is the **muscle** (every executable process across the fleet).

**Hub ID**: barton-processes
**Hub Name**: Barton Processes
**Domain**: process-engine
**Authority**: Inherited from imo-creator (Sovereign)

---

## CANONICAL REFERENCE

| Template | imo-creator Path | Version |
|----------|------------------|---------|
| Architecture | law/doctrine/ARCHITECTURE.md | 2.1.0 |
| Tools | law/integrations/TOOLS.md | 1.1.0 |
| OSAM | law/semantic/OSAM.md | 1.1.0 |
| PRD | fleet/car-template/docs/PRD_HUB.md | 1.0.0 |
| ADR | fleet/adr-templates/ADR.md | 1.0.0 |
| Checklist | fleet/checklists/HUB_COMPLIANCE.md | 1.0.0 |

---

## STARTUP PROTOCOL

Every session, before any work:

1. Read this file (`CLAUDE.md`) — identity, permissions, rules
2. Read `law/heir.yaml` — process engine identity
3. Read `law/orbt.yaml` — current operational mode
4. Read `law/process-registry.yaml` — master process list

---

## REPO STRUCTURE

```
barton-processes/
├── CLAUDE.md                         # This file
├── README.md                         # Repo overview
├── .gitignore
│
├── law/                              # GOVERNANCE
│   ├── heir.yaml                     # Process engine identity (HEIR)
│   ├── orbt.yaml                     # Operational mode (ORBT)
│   ├── process-registry.yaml         # Master list of all processes
│   ├── ingress-manifest.yaml         # Cross-silo dependencies
│   └── doctrine/                     # Inherited doctrine from Garage
│
├── factory/                          # ALL EXECUTABLE PROCESSES
│   ├── 001-neon-db-agent/            # Each process gets NNN-name/
│   ├── 002-cl-pipeline/              #   └── heir.yaml (process identity)
│   ├── ...                           #   └── src/ (executable code)
│   └── 016-bit-scoring/              #   └── contracts/ (if applicable)
│
├── docs/                             # DOCUMENTATION
│   └── adr/                          # Architecture Decision Records
│
├── log/                              # Process execution receipts
├── scripts/                          # Extraction playbook + utilities
└── archive/                          # Retired processes
```

---

## PROCESS NUMBERING

| Range | Source Repo | Count |
|-------|------------|-------|
| 001-005 | company-lifecycle-cl | 5 |
| 006-011 | barton-outreach-core | 6 |
| 012 | imo-creator (field-monitor snap-on) | 1 |
| 013-014 | client | 2 |
| 015 | sales | 1 |
| 016 | barton-outreach-core (BIT scoring) | 1 |
| 017+ | reserved (barton-storage, future) | — |

---

## GOVERNANCE DIRECTION

| Action | Permitted |
|--------|-----------|
| Read parent doctrine | YES |
| Extract processes from blueprint repos | YES (with playbook) |
| Create new numbered process directories | YES |
| Update process-registry.yaml | YES |
| Modify parent doctrine | **FORBIDDEN** |
| Push changes to parent | **FORBIDDEN** |
| Add executables to blueprint repos | **FORBIDDEN** |
| Submit ADR to parent | YES (change request only) |

---

## WHAT CLAUDE CODE CAN DO IN THIS REPO

| Action | Permitted |
|--------|-----------|
| Read all files | YES |
| Extract processes using playbook | YES |
| Create process directories under factory/ | YES |
| Create process heir.yaml files | YES |
| Update law/process-registry.yaml | YES |
| Update law/ingress-manifest.yaml | YES |
| Report violations | YES |
| Modify parent doctrine files | NO |
| Skip extraction playbook steps | NO |
| Invent structure beyond doctrine | NO |
| Use LLM as primary solution | NO |
| Leave executables in blueprint repos | NO |

---

## EXTRACTION RULES

1. **Use the playbook** — `scripts/extraction-playbook.md` defines every step
2. **Number sequentially** — no gaps in factory/ numbering
3. **One heir.yaml per process** — declares dependencies, runtime, log targets
4. **Update registry after every extraction** — process-registry.yaml must match factory/
5. **Verify zero remaining** — source blueprint must have ZERO executables in extracted paths
6. **Archive, don't delete** — retired code goes to archive/, never vanishes

---

## GOLDEN RULES

1. **This repo conforms to imo-creator. Parent defines, children conform.**
2. **Blueprint repos = brain. This repo = muscle. Never mix.**
3. **Every process is numbered and registered. No exceptions.**
4. **Extraction is repeatable. Follow the playbook.**
5. **Determinism first. LLM as tail only.**
6. **ASK > INFER. When uncertain, HALT.**

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-14 |
| Last Modified | 2026-03-14 |
| Status | ACTIVE |
| Authority | imo-creator (Inherited) |
| BAR | BAR-136 |

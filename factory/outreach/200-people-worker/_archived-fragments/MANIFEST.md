> **ARCHIVED 2026-04-29** — Consolidated into PROCESS-UT.md and DOCTRINE.md during UT v2.7.0 standardization. See sibling files at folder root.

# PROCESS-200: People Worker
# Status: DEPLOYED (OPR)
# Last Updated: 2026-03-24

---

## IDENTITY (HEIR)

| Field | Value |
|-------|-------|
| Process ID | PROC-PEOPLE |
| Number | 200 |
| Name | People Worker |
| Blueprint | barton-outreach-core (04.04.02 People Intelligence) |
| Runtime | Cloudflare Workers (daily cron) |
| Deployed URL | people-worker-200.svg-outreach.workers.dev |
| Cron | `0 6 * * *` (daily 6am UTC) |
| ORBT | OPR |
| Strikes | 0 |
| Last Deployed | 2026-03-19 |

---

## IMO

**Input:** Territory dossier (35,629 companies) seeded from Neon into D1. Company list comes from `outreach.company_target` filtered by agent coverage zones (3 agents × coverage radius).

**Middle:**
1. **SEED** (Day 1): Pull territory from Neon → D1 `companies` table. Build `monitor_list` of LinkedIn profiles to check. Take `baseline` snapshot of current slot state.
2. **FETCH** (Days 1-28): Daily batch of 100 profiles. LinkedIn head-only check via residential proxy (DataImpulse/Startpage). 30-120 second random delay between fetches. Check CEO/CFO/HR slots for each company.
3. **DETECT** (per batch): Compare current snapshot to baseline. Binary movement detection per slot (0 = no change, 1 = movement). Signals: JOINED, LEFT, REPLACED, TITLE_CHANGED, EMAIL_CHANGED.
4. **PUSH** (Day 28+): Promote verified results from D1 → Neon vault.

**Output:** Filled CEO/CFO/HR slots with verified email/LinkedIn. Movement signals fed to Talent Flow (Process 500) and BIT Scoring (Process 600). Reachability status per company (UNREACHABLE, EMAIL_ONLY, LINKEDIN_ONLY, FULL).

**Circle:** Monthly cycle. Each month's snapshot becomes next month's baseline. Movement trends accumulate. Companies that were UNREACHABLE may become reachable as slots fill.

---

## DATABASES

### D1 (people-worker-200) — Binding: `D1`

| Table | Role | Key Columns |
|-------|------|-------------|
| `companies` | Working copy | company_unique_id, outreach_id, canonical_name, agent_name, state |
| `slots` | Slot state | outreach_id, slot_type (CEO/CFO/HR), person_unique_id, is_filled |
| `people` | Contact details | person_unique_id, email, linkedin_url, first_name, last_name |
| `dol` | DOL snapshot | outreach_id, ein, filing_present, renewal_month |
| `blog` | Blog signals | outreach_id, signal_type |
| `bit_scores` | BIT composite | outreach_id, score, score_tier |
| `monitor_list` | LinkedIn profiles to check | outreach_id, linkedin_url, status |
| `baseline` | Previous month snapshot | slot state for diff comparison |
| `snapshots` | Current month results | fetched profile data |
| `batch_progress` | Batch tracking | current batch, processed count |
| `outreach_status` | Company outreach state | queued/active/paused |
| `errors` | Error drain | error details per fetch attempt |

### Data Flow

```
NEON (vault) ─── SEED ──→ D1 (workspace)
                            │
                            ├── monitor_list → proxy → LinkedIn
                            ├── snapshots ← fetch results
                            ├── baseline vs snapshots → movement detection
                            │
D1 (workspace) ── PUSH ──→ NEON (vault)
```

---

## DEPENDENCIES

### Upstream
| Dependency | What | Status |
|-----------|------|--------|
| Neon vault | Company data + previous people records | DONE |
| Agent coverage zones | 3 agents × radius → territory filter | DONE |
| LinkedIn proxy | Residential IP via DataImpulse | DONE |

### Downstream
| Consumer | What |
|----------|------|
| Process 500 (Talent Flow) | Movement signals (0/1 per slot) |
| Process 600 (BIT Scoring) | People score component |
| Process 100 (LCS Pipeline) | Recipient slots for SID construction |
| Outreach D1 (svg-d1-outreach-ops) | people_company_slot + people_people_master |

---

## CURRENT STATE (as of 2026-03-24)

| Metric | Value |
|--------|-------|
| Companies in D1 | 32,702 |
| Slots | 43,203 |
| People (contacts) | 20,487 |
| Monitor list | ~20,000 LinkedIn profiles |
| DOL records | 27,464 |
| D1 size | 70MB |
| Proxy hit rate | 87-95% on LinkedIn |

---

## KNOWN ISSUES

| Date | Issue | Resolution | Strikes |
|------|-------|------------|---------|
| 2026-03-19 | Google blocks with CAPTCHAs through proxy | Switched to Startpage via DataImpulse — 95% hit rate | 0 |
| 2026-03-19 | Bing APIs retired Aug 2025 | Removed Bing, using Startpage exclusively | 0 |

---

## SMOKE TEST

1. `GET people-worker-200.svg-outreach.workers.dev/health` → expected: status ok, company count > 0
2. Check D1: `SELECT COUNT(*) FROM companies` → expected: ~32,700
3. Check D1: `SELECT COUNT(*) FROM monitor_list WHERE status = 'pending'` → expected: > 0
4. Trigger manual batch: `POST /batch` → expected: processes up to BATCH_SIZE profiles
5. Check D1: `SELECT COUNT(*) FROM snapshots` → expected: increased
6. Verify error rate: `SELECT COUNT(*) FROM errors` → expected: low relative to processed

---

## NEXT STEPS

| What | BAR | Status |
|------|-----|--------|
| Full month cycle completion | BAR-52 | In Progress |
| Movement detection integration with LCS signals | — | TODO |
| Push results to Neon vault | — | TODO — needs end-of-month trigger |

---

## FILES

```
Barton-Processes/factory/200-people-worker/
├── heir.yaml          # Identity
├── MANIFEST.md        # This file
├── ARCHITECTURE.md    # Detailed architecture doc
├── package.json       # Dependencies
├── wrangler.toml      # CF Worker config
├── tsconfig.json
├── bulk-update/       # Bulk operations
├── proxy/             # LinkedIn proxy config
└── src/               # Worker source code
    └── index.ts       # Entry point
```

---

## SESSION LOG

| Date | Session | What Was Done | Brain Chunks |
|------|---------|---------------|-------------|
| 2026-03-19 | Full build + deploy | Built CF Worker, seeded 35K companies, proved SearchEngineProxy pattern (87-95% LinkedIn hit rate), deployed | `processes/Session 2026-03-19 — Full Build Progress Report` |
| 2026-03-24 | Manifest written | Documentation chain created | `session/2026-03-24-full-session-final` |

**imo-brain documents:**
- `processes/Session 2026-03-19 — Full Build Progress Report`
- `infrastructure/Search-Engine-as-Proxy Architecture — Universal Intelligence Layer`

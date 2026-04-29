> **ARCHIVED 2026-04-29** — Consolidated into `PROCESS-UT.md` and `DOCTRINE.md` during UT v2.7.0 standardization. See sibling files at folder root.

# SEED v2 — National CL Spine Design
## Build constants free for the whole country. Spend money only when an agent is assigned.
### BAR-190 | Authority: Foundational Bedrock — Tier 0

---

## The Insight

The 2.4M DOL Form 5500 records already in Neon ARE the national company universe. A company doesn't file a 5500 unless it's real, has employees, and has a benefits plan. The filing is proof of existence — the government already verified it.

One DOL record fills TWO sub-hubs for free:
- **DOL sub-hub** — the filing data itself (EIN, carrier, broker, renewal, funding type)
- **CT sub-hub** — company profile extracted from the filing (name, ZIP, city, state, employee count)

A third sub-hub — **Blog** — is one domain lookup away. Free.

The fourth sub-hub — **People** — is the only one that costs money. And you only spend that money when an agent is assigned to a geography.

---

## Constants vs Variables

### Constants (structure — free to build for all companies)

| Constant | Source | Cost |
|----------|--------|------|
| Sovereign ID | Stamped at creation, one per EIN | Free |
| Company name | DOL filing `sponsor_dfe_name` | Free |
| EIN | DOL filing `sponsor_dfe_ein` | Free |
| ZIP code | DOL filing `spons_dfe_mail_us_zip` | Free |
| City | DOL filing `spons_dfe_mail_us_city` | Free |
| State | DOL filing `spons_dfe_mail_us_state` | Free |
| Employee count | DOL filing `tot_active_partcp_cnt` | Free |
| Carrier | DOL Schedule A | Free |
| Broker | DOL Schedule A | Free |
| Renewal month | DOL filing `plan_eff_date` | Free |
| Funding type | DOL filing | Free |
| Domain | One-time lookup (Startpage or direct) | Essentially free |
| About URL | One-time lookup from domain | Essentially free |
| 3 slot types | CEO, CFO, HR — structure exists per company | Free (rows created at activation) |

### Variables (fill — costs money, only when agent assigned)

| Variable | Source | Cost | When |
|----------|--------|------|------|
| Person name per slot | Blog extraction, Startpage, Prospeo, Apollo | Free → cheap | At activation |
| Email per person | Pattern derivation, Prospeo, Apollo | $0.01-0.05/email | At activation |
| Email verification | Million Verifier | Per verification | At activation |
| LinkedIn URL per person | Startpage search | ~$1-2/month proxy | At activation |
| Campaign state | LCS Pipeline output | Free (internal) | At activation |

---

## The Gate — Agent Assignment

An agent defines a geography, not company ownership. Agent has a ZIP. ZIP has a radius. Radius produces qualifying ZIPs. Companies at those ZIPs move from "roughed in" to "active."

```
Rough-In (free, national)
  → All 2.4M+ companies have: sovereign ID, CT, DOL, domain, about URL
  → 3 slot types defined but rows NOT created
  → No money spent

Agent assigns ZIP + radius (the work order)
  → Companies in radius move to "active"
  → Slot rows created (3 per company)
  → Process 200 starts filling slots (costs money)
  → Process 100 LCS compiles and delivers
```

A company can have multiple agents if its ZIP falls in overlapping coverage zones. The `service_agents` column holds comma-separated agent numbers.

---

## Three Phases

### Phase 1: Rough-In (free, national, run once)

**Input:** 2.4M DOL records already in Neon

**What happens:**
1. Dedup by EIN — one sovereign ID per company. Latest filing year provides the current CT data.
2. Extract CT from latest filing (name, EIN, ZIP, city, state, employees, carrier, broker, renewal).
3. Domain lookup — batch Startpage search or direct fetch. One per company. Store in CL.
4. About URL discovery — from domain. Store in CL.

**Output:** National CL spine with every DOL-filing company roughed in. All constants locked. No money spent.

**What this does NOT do:** Create slot rows. Fill people data. Verify emails. Run campaigns. That's finish work.

### Phase 2: State Completion (cheap, per state, run when opening a new market)

**Input:** State name (e.g., "Texas")

**What happens:**
1. Pull non-filing companies (50-5,000 employees) from Clay.com or Hunter.io for that state.
2. Merge into CL. Dedup against existing DOL companies on EIN or domain.
3. New companies get sovereign ID + CT (from Clay/Hunter data).
4. Mark state as "complete" in state tracking table.

**Output:** Full universe for that state — DOL filers + non-filers. State marked complete.

**State tracking table:**

| Column | Description |
|--------|-------------|
| state_code | 2-letter state code |
| dol_companies | Count of DOL-filing companies in this state |
| non_filer_source | Where non-filers came from (Clay, Hunter, etc.) |
| non_filer_count | Count of non-filers added |
| total_companies | DOL + non-filers |
| completed_at | When this state was fully populated |
| status | pending / complete |

### Phase 3: Activation (costs money, per agent ZIP)

**Input:** Agent assigns a ZIP + radius

**What happens:**
1. Coverage view expands ZIP into qualifying ZIPs (Haversine).
2. SEED pulls matching companies from CL into D1 workspace.
3. Create 3 slot rows per company (CEO, CFO, HR).
4. Process 200 starts filling slots — people discovery, email, LinkedIn.
5. Million Verifier gates every email before the slot is marked "filled."
6. Process 100 LCS compiles CID → SID → MID and delivers.

**Output:** Agent-scoped companies in D1 with filled slots, verified contacts, and active campaigns.

---

## What Already Exists

| Asset | Location | Status |
|-------|----------|--------|
| 2.4M DOL records | Neon `dol` schema | In Neon |
| 117K companies (6-8 states) | Neon `cl`, `outreach`, `people` schemas | Processed |
| SEED v1 pipeline | LCS Hub `/seed/clean` endpoint | Working (32,702 companies) |
| Neon `seed_views` schema | 8 views, agent-scoped | Built 2026-04-01 |
| D1 workspace | `svg-d1-outreach-ops` + `svg-d1-spine` | Clean SEED complete |
| Hyperdrive binding | LCS Hub `HD_NEON` | Live |
| Agent model | 3 agents, 3 ZIP+radius zones | Working |
| Column registry | D1 `outreach_column_registry` | 79 columns documented |
| Prospeo API key | Doppler | Not wired |
| Apollo API key | Doppler | Not wired |
| Million Verifier API key | Doppler | Not wired |
| Clay API | Not in Doppler | Needs setup for Phase 2 |

## What Needs Building

| Item | Phase | Effort |
|------|-------|--------|
| Sovereign ID stamping for 2.4M DOL companies | 1 | Neon SQL |
| CT extraction view (latest filing per EIN) | 1 | Neon view |
| State tracking table | 2 | Neon table |
| Batch domain lookup process | 1 | CF Worker or Python script |
| Clay/Hunter integration for non-filers | 2 | Per state |
| SEED v2 endpoint (reads from national CL, scoped by agent ZIP) | 3 | LCS Hub update |
| Email discovery pipeline (BAR-148/189) | 3 | The big build |

---

## How This Changes the Architecture

### Before (SEED v1)
```
Agent → ZIP → radius → 32,702 companies → SEED everything to D1 → fill slots → outreach
```
Problem: Constants and variables mixed. Filling slots for all 32K even if data isn't ready. Can't scale beyond agent-assigned companies.

### After (SEED v2)
```
Phase 1: DOL → 2.4M companies → sovereign ID + CT + domain (FREE, NATIONAL)
Phase 2: State opening → add non-filers from Clay/Hunter (CHEAP, PER STATE)
Phase 3: Agent → ZIP → radius → SEED to D1 → fill slots → outreach (COSTS MONEY, PER AGENT)
```
Constants built once for the whole country. Variables filled only when activated. Tolerance cascade: improve Phase 1 → every Phase 3 activation gets better.

---

## The Rough-In Metaphor

Building a subdivision:
- **Phase 1 (rough-in):** Frame every house, run the plumbing and rough electrical. Every house has a structure. No one lives there yet. Costs almost nothing per house.
- **Phase 2 (state completion):** Survey the lots that weren't in the original plan. Add them to the map.
- **Phase 3 (finish work):** A buyer (agent) picks a house (ZIP radius). NOW you do the finish work — drywall, fixtures, paint (people, email, LinkedIn). You only finish houses that have buyers.

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-01 |
| BAR Reference | BAR-190 |
| Related BARs | BAR-52, BAR-148, BAR-189 |
| Authority | Foundational Bedrock — Tier 0 |
| Location | factory/outreach/010-seed-d1/SEED_V2_DESIGN.md |

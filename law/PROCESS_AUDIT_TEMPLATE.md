# PROCESS AUDIT TEMPLATE — Pre-Flight Inspection Checklist
## The Airworthiness Check Before Any Process Goes Operational
### Status: LOCKED — Every process MUST pass this audit before moving to OPR

| Field | Value |
|-------|-------|
| **CTB Position** | BRANCH — hangs from Barton-Processes (trunk). One audit per process (leaf). |
| **Input** | A process exists in `factory/`. It claims to be ready. |
| **Middle** | Walk through the 8 Bedrock gates + documentation chain + tool chain. PASS/FAIL per item. |
| **Output** | A signed audit report: airworthy (all gates pass) or grounded (specific failures listed with fix requirements). |
| **Circle** | Every audit finding feeds back to the process. Fix → re-audit → verify. Strike 3 on same finding → Troubleshoot/Train, not another repair. |
| **Authority** | Foundational Bedrock (`law/doctrine/FOUNDATIONAL_BEDROCK.md`) |
| **Created** | 2026-03-25 |

---

## The Rule

**No process moves from BLD to OPR without passing this audit. No exceptions.**

The audit is the FAA inspection. The auditor reads the documentation, inspects the code, verifies the tool chain, and signs off. The auditor MUST be a different inference engine than the builder (Bedrock §8 — Auditor Rule).

**Read order before auditing:**
1. Foundational Bedrock (`law/doctrine/FOUNDATIONAL_BEDROCK.md`) — the engine
2. This template — the inspection checklist
3. The process's CLAUDE.md — agent operating instructions
4. The process's MANIFEST.md — the logbook
5. The process's code — the actual implementation

---

## GATE 1: THREE PRIMITIVES (Bedrock §1)
**Governed by: C&V**

Three questions. Every component in the process must answer all three. If any one fails, that's the break.

| Field | Value |
|-------|-------|
| **CTB Position** | TRUNK — the irreducible base of the inspection |
| **Input** | The process claims to work |
| **Middle** | For every component (table, endpoint, worker, service, secret), ask the three questions |
| **Output** | PASS (all three answered YES for every component) or FAIL (specific component + which question failed) |
| **Circle** | A component that fails one of these three IS the root cause. Don't chase downstream. |

### Checklist

| # | Question | What You're Checking | PASS/FAIL |
|---|----------|---------------------|-----------|
| 1.1 | **THING — Does every component exist where it should?** | D1 tables exist. Worker is deployed. Endpoints respond. Secrets are in Doppler. Config files exist. Cron is scheduled. | |
| 1.2 | **FLOW — Does the data reach every component?** | Join keys work. D1 bindings connect. Hyperdrive resolves. Proxy responds. Queue delivers. Webhook receives. | |
| 1.3 | **CHANGE — Does the transformation happen correctly?** | Compilation produces correct output. Movement detection returns 0/1. Signals write to correct table. Errors log correctly. | |

**How to execute:**
- For each component listed in the process's CLAUDE.md and MANIFEST.md, verify Thing/Flow/Change.
- Test Thing: `curl /health`, query D1 for table existence, check Doppler for secrets.
- Test Flow: run a single record through the process. Did the data arrive at each stage?
- Test Change: compare actual output to expected output at each stage.

---

## GATE 2: CONSTANTS & VARIABLES (Bedrock §2)
**Governed by: C&V**

Run the C&V Test against every element of the process. Identify what's fixed (constant) and what varies (variable). Verify constants are locked and variables are guard-railed.

| Field | Value |
|-------|-------|
| **CTB Position** | TRUNK — the classification that everything else depends on |
| **Input** | The process's components, data, configuration, and behavior |
| **Middle** | Apply the three-question C&V Test to every element. Verify sigma. Check for misclassifications. |
| **Output** | Constant manifest for this process: locked constants, classified variables, domesticated variables |
| **Circle** | Back-propagate: does any new constant invalidate a prior one? Sigma tightening → real. Flat → phantom. Expanding → broken. |

### Checklist

| # | Check | What You're Looking For | PASS/FAIL |
|---|-------|------------------------|-----------|
| 2.1 | **Constants identified** | Table names, column names, slot types, signal types, tool IDs, HEIR fields — all nameable, formattable, locked | |
| 2.2 | **Variables identified** | Values that fill constants — row counts, timestamps, person names, scores, states — classified with guard rails | |
| 2.3 | **Domesticated variables identified** | Variables too tight to affect the outcome — stop decomposing here | |
| 2.4 | **No misclassifications** | Nothing treated as constant that actually varies (BIT scores were this). Nothing treated as variable that should be locked. | |
| 2.5 | **Retired references removed** | No references to BIT scoring, deprecated tables, dead endpoints, or retired processes | |
| 2.6 | **Hardcoded values that should be config** | No credentials in source code. No magic numbers without a config constant. | |

**How to execute:**
- Read heir.yaml — are constants declared?
- Grep code for hardcoded strings, credentials, magic numbers.
- Check every table/column reference in code against actual D1 schema.
- Verify no retired system references (BIT, deprecated tables).

---

## GATE 3: IMO (Bedrock §3)
**Governed by: IMO**

The process must have a clear Input → Middle → Output. The two-question intake must be answerable. The IMO must be implemented as documented.

| Field | Value |
|-------|-------|
| **CTB Position** | BRANCH — the process description |
| **Input** | The process's MANIFEST.md Block 2 (IMO section) |
| **Middle** | Verify two-question intake. Verify each IMO stage exists in code. Verify fractal decomposition where needed. |
| **Output** | PASS (IMO documented and implemented correctly) or FAIL (specific stage that's missing or wrong) |
| **Circle** | If the output doesn't match what the IMO section says, the documentation or the code is wrong. Fix whichever is wrong. |

### Checklist

| # | Check | What You're Looking For | PASS/FAIL |
|---|-------|------------------------|-----------|
| 3.1 | **Two-question intake answered** | "What triggers this?" has a concrete answer. "How do we get it?" has a concrete answer. | |
| 3.2 | **Input documented and exists** | What data comes in? From where? The trigger mechanism exists in code (cron, HTTP, queue). | |
| 3.3 | **Middle documented and exists** | Processing steps numbered in MANIFEST. Each step has corresponding code. | |
| 3.4 | **Output documented and exists** | What comes out? Where does it go? The output path exists in code. | |
| 3.5 | **Circle documented and exists** | How does feedback flow back? Webhooks, error paths, sigma tracking — the loop closes. | |
| 3.6 | **Code matches documentation** | Every endpoint in CLAUDE.md exists in code. Every processing step in MANIFEST exists in code. | |

---

## GATE 4: CTB (Bedrock §4)
**Governed by: CTB**

The process must know where it sits on the tree. CQRS must be enforced. Sovereign silos respected. UT sub-hubs called through the hierarchy.

| Field | Value |
|-------|-------|
| **CTB Position** | BRANCH — the hierarchy check |
| **Input** | The process's position in the system |
| **Middle** | Verify CTB placement, CQRS compliance, silo boundaries, UT sub-hub routing |
| **Output** | PASS (process knows its place and respects boundaries) or FAIL (specific violation) |
| **Circle** | A process that violates CTB contaminates everything downstream. Fix at the trunk, not the leaf. |

### Checklist

| # | Check | What You're Looking For | PASS/FAIL |
|---|-------|------------------------|-----------|
| 4.1 | **CTB position declared** | heir.yaml has `ctb_placement` field. Process knows if it's trunk, branch, or leaf. | |
| 4.2 | **CQRS enforced** | 1 CANONICAL table + 1 ERROR table per sub-hub. No direct writes to CANONICAL from outside. INSERT-only at leaf level. | |
| 4.3 | **Sovereign silos respected** | No sideways calls between processes. No direct branch-to-branch communication. Each process connects at one point only. | |
| 4.4 | **UT sub-hubs declared** | heir.yaml lists which UT sub-hubs this process uses (16-fetcher, 18-proxy-router, etc.) | |
| 4.5 | **UT sub-hubs called correctly** | Code calls through declared UT sub-hubs, not bypassing them. Fetcher goes through 16-fetcher, not raw `fetch()`. Proxy goes through 18-proxy-router, not hardcoded URLs. | |
| 4.6 | **SEED → WORK → PUSH lifecycle** | Data enters from Neon (SEED). Processing happens on D1 (WORK). Results promote back (PUSH). No direct Neon reads during WORK phase. | |
| 4.7 | **Database tables match OSAM** | Every table referenced in code appears in OSAM.md. Every join key in code matches OSAM. | |

---

## GATE 5: THE CIRCLE (Bedrock §5)
**Governed by: Circle**

The process must close the feedback loop. Output feeds back to input. Errors are caught and routed. The logbook gets updated.

| Field | Value |
|-------|-------|
| **CTB Position** | BRANCH — the validation mechanism |
| **Input** | The process runs and produces output |
| **Middle** | Verify feedback paths exist, error handling closes the loop, logbook updated |
| **Output** | PASS (circle closes) or FAIL (specific point where the flow stops) |
| **Circle** | If the circle doesn't close, the process can't self-correct. It will drift silently. |

### Checklist

| # | Check | What You're Looking For | PASS/FAIL |
|---|-------|------------------------|-----------|
| 5.1 | **Output feeds back to input** | Webhook responses update state. Error signals trigger re-processing. Monthly snapshots become next month's baseline. | |
| 5.2 | **Error handling writes to error table** | Every `catch` block writes to the ERROR table (CQRS write side). No swallowed errors. No `catch {}` with no action. | |
| 5.3 | **Error table is queryable** | Can you see what's failing and why? Error records have enough detail to diagnose without reading code. | |
| 5.4 | **Process can be stopped mid-run** | Batch progress is tracked. Resume is possible. Interruption doesn't corrupt data. | |
| 5.5 | **Logbook (MANIFEST) is current** | Session log has recent entries. Current state section has recent date. Known issues section reflects reality. | |

---

## GATE 6: TROUBLESHOOTING LOOP (Bedrock §6)
**Governed by: Circle**

The process must have error detection, strike counting, and escalation paths.

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — the repair protocol |
| **Input** | Something broke |
| **Middle** | Verify error detection, strike counting, escalation, and stop conditions |
| **Output** | PASS (errors are caught, counted, and escalated correctly) or FAIL (error handling gaps) |
| **Circle** | Strike 3 → Troubleshoot/Train, not another repair. The audit catches processes that keep repairing without learning. |

### Checklist

| # | Check | What You're Looking For | PASS/FAIL |
|---|-------|------------------------|-----------|
| 6.1 | **Error detection exists** | Every external call (fetch, DB query, API call) has error handling. | |
| 6.2 | **Errors are categorized** | Error codes distinguish between types (FETCH_FAILED, PARSE_FAILED, DB_ERROR, etc.) | |
| 6.3 | **Strike counting implemented** | ORBT strike counter increments on repeated failures. heir.yaml shows current strike count. | |
| 6.4 | **Escalation path exists** | Strike 1 → auto-retry. Strike 2 → alt channel. Strike 3 → human escalation / Troubleshoot/Train. | |
| 6.5 | **Stop conditions defined** | Batch limits exist. Rate limits enforced. Process doesn't run forever on failure. | |
| 6.6 | **Cost controls enforced** | Daily caps on paid tools. Well drinks exhausted before top shelf. No single company can consume unlimited resources. | |

---

## GATE 7: TOOL CHAIN (UT + Snap-On Architecture)
**Governed by: CTB**

The process must call tools correctly through the UT layer. Tool priority must be enforced. Every data point must be tagged with its source tool.

| Field | Value |
|-------|-------|
| **CTB Position** | BRANCH — the tool hierarchy |
| **Input** | The process needs external data (LinkedIn profiles, blog content, DOL filings, etc.) |
| **Middle** | Verify tool calls go through UT sub-hubs, priority cascade is implemented, source tracking works |
| **Output** | PASS (tools called correctly with cost controls) or FAIL (bypassed UT, wrong priority, no tracking) |
| **Circle** | Monte Carlo evaluates tool ROI from source_tool tags. Without tags, you can't measure which tools produce results. |

### Checklist

| # | Check | What You're Looking For | PASS/FAIL |
|---|-------|------------------------|-----------|
| 7.1 | **heir.yaml declares tool_priority** | Well drinks (free), house pours (cheap), top shelf (surgical) — with specific TOOL-IDs | |
| 7.2 | **heir.yaml declares ut_sub_hubs** | Lists which UT sub-hubs this process calls (16-fetcher, 17-parser, 18-proxy-router, etc.) | |
| 7.3 | **Code calls through UT, not around it** | Fetches go through 16-fetcher / 18-proxy-router. Not raw `fetch()` to external URLs. Not hardcoded proxy endpoints. | |
| 7.4 | **Three-tier fallback implemented** | Well drinks tried first. If exhausted → house pours. If exhausted → top shelf. Code enforces this order, not just docs. | |
| 7.5 | **source_tool tagged on every data point** | Every record written includes which tool produced it (e.g., 'startpage', 'brave', 'hunter', 'apollo'). Not hardcoded to a single value. | |
| 7.6 | **Cost controls per tool** | Daily caps on paid APIs. Budget limits per company. Per-batch spending limits. | |
| 7.7 | **Proxy pattern correct** | SearchEngineProxy: Startpage through DataImpulse residential proxy. Not direct LinkedIn/Google. Not CF Tunnel to LinkedIn. | |
| 7.8 | **Credentials from Doppler only** | No hardcoded API keys, proxy passwords, or connection strings. No fallback defaults for credentials. | |

---

## GATE 8: AVIATION MODEL (Bedrock §8)
**Governed by: C&V + Circle**

The process must have a complete identity (HEIR), current state (ORBT), and full documentation chain.

| Field | Value |
|-------|-------|
| **CTB Position** | BRANCH — the operational governance |
| **Input** | The process exists and claims readiness |
| **Middle** | Verify HEIR (8 fields), ORBT (current state), documentation chain (6 files), logbook (session log) |
| **Output** | PASS (fully governed, documented, and state-tracked) or FAIL (missing identity, wrong state, incomplete docs) |
| **Circle** | Read the logbook first. Write it last. If the logbook is stale, the process is ungoverned. |

### HEIR Checklist (8 Fields — All Required)

| # | Field | What It Must Contain | PASS/FAIL |
|---|-------|---------------------|-----------|
| 8.1 | **Process ID** | `PROC-{ID}` format | |
| 8.2 | **Number** | Three-digit process number (e.g., 200) | |
| 8.3 | **Name** | Human-readable name | |
| 8.4 | **Blueprint** | Source repo — the design, not the executable | |
| 8.5 | **Runtime** | CF Worker / Python / SQL / Node | |
| 8.6 | **Deployed URL** | Live URL or "not deployed" | |
| 8.7 | **ORBT** | Current state: OPR / RPR / BLD / T/T | |
| 8.8 | **Strikes** | Current strike count: 0 / 1 / 2 / 3 | |

### ORBT State Verification

| # | Check | What You're Looking For | PASS/FAIL |
|---|-------|------------------------|-----------|
| 8.9 | **ORBT reflects reality** | If code has critical bugs → should be RPR or BLD, not OPR. If process isn't deployed → should be BLD, not OPR. | |
| 8.10 | **ORBT history logged** | orbt.yaml or heir.yaml has state transition history with dates and reasons | |

### Documentation Chain (6 Files — All Required)

| # | File | Purpose | Exists? | Complete? |
|---|------|---------|---------|-----------|
| 8.11 | `CLAUDE.md` | Agent operating instructions + Bedrock reference | | |
| 8.12 | `heir.yaml` | Identity — 8-field HEIR, tool priority, UT sub-hubs | | |
| 8.13 | `MANIFEST.md` | Logbook — 11 blocks per PROCESS_MANIFEST_TEMPLATE | | |
| 8.14 | `OSAM.md` | Semantic access map — WHERE to query, HOW to join | | |
| 8.15 | `ERD.md` | Entity relationships — tables, columns, FK chain | | |
| 8.16 | `PRD.md` | Product requirements — acceptance criteria, definition of done | | |

### Smoke Test

| # | Check | What You're Looking For | PASS/FAIL |
|---|-------|------------------------|-----------|
| 8.17 | **Smoke test defined** | MANIFEST Block 8 has numbered steps with expected results | |
| 8.18 | **Smoke test passes** | Execute the smoke test. Every step produces expected output. | |

---

## AUDIT REPORT FORMAT

After completing all 8 gates, produce the audit report:

```
# AUDIT REPORT — Process {NNN}: {Name}
# Date: {YYYY-MM-DD}
# Auditor: {engine name}
# Builder: {engine that built the process}

## VERDICT: {AIRWORTHY / GROUNDED}

## Gate Results

| Gate | Section | Result | Findings |
|------|---------|--------|----------|
| 1 | Three Primitives | PASS/FAIL | {specific items} |
| 2 | Constants & Variables | PASS/FAIL | {specific items} |
| 3 | IMO | PASS/FAIL | {specific items} |
| 4 | CTB | PASS/FAIL | {specific items} |
| 5 | The Circle | PASS/FAIL | {specific items} |
| 6 | Troubleshooting Loop | PASS/FAIL | {specific items} |
| 7 | Tool Chain | PASS/FAIL | {specific items} |
| 8 | Aviation Model | PASS/FAIL | {specific items} |

## Fix List (if GROUNDED)

| # | Gate | Item | What's Wrong | Fix Required |
|---|------|------|-------------|-------------|
| 1 | {gate} | {item #} | {description} | {specific fix} |

## Signature

Auditor: {name/engine}
Date: {date}
Next audit: {after fixes applied}
```

---

## Enforcement

- Every process MUST pass all 8 gates before moving to OPR.
- A single FAIL on any gate = GROUNDED. Fix the specific items, then re-audit.
- The auditor MUST be a different inference engine than the builder (Bedrock §8).
- Strike 3 on the same audit finding across multiple processes → Airworthiness Directive (fleet-wide fix).
- This template is LOCKED. Changes require human authority.

---

## Three Primitives Meta-Check

Before signing the audit report, the auditor asks:
1. **Thing:** Does every component exist where it should?
2. **Flow:** Does the data reach every component?
3. **Change:** Does the transformation happen correctly?

If any one fails → the audit is incomplete. Go back to the gate where it broke.

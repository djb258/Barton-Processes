# PROCESS MANIFEST — Required Format
## The Aircraft Maintenance Log for Every Process

| Field | Value |
|-------|-------|
| **Status** | LOCKED — every process MUST have a MANIFEST.md following this format |
| **Authority** | Foundational Bedrock (`law/doctrine/FOUNDATIONAL_BEDROCK.md`) |
| **CTB Position** | BRANCH — hangs from Barton-Processes (trunk). One manifest per process (leaf). |
| **Input** | A process exists in `factory/`. It needs a maintenance log. |
| **Middle** | Apply the template below. Every section follows IMO+CTB block format. |
| **Output** | A complete MANIFEST.md that any LLM or human can read cold and know exactly what this process is, where it runs, what it touches, what broke, and what's next. |
| **Circle** | Every session that touches the process reads the manifest FIRST and updates it LAST. Stale manifest = grounded aircraft. |
| **Created** | 2026-03-24 |

---

## The Rule

**No manifest → process is not certified. Cannot move to OPR.**

The `heir.yaml` is the VIN — identity only, stamped at build.
The `MANIFEST.md` is the logbook — everything needed to pick up where you left off.

**Read first. Write last. No exceptions.** (Bedrock §8 — Aviation Model)

---

## Template — Required Sections

Every MANIFEST.md MUST contain these sections in this order. No section may be omitted. Each section is a block following the Bedrock block format.

---

### BLOCK 1: IDENTITY (HEIR)
**Governed by: C&V**

The constants of this process. What is fixed regardless of when you read this.

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — one process, one identity |
| **Input** | The process exists |
| **Middle** | Apply the C&V test: name it, format it, lock it |
| **Output** | 8-field HEIR + runtime details |

**Required fields:**

```
| Field | Value |
|-------|-------|
| Process ID | PROC-{ID} |
| Number | {NNN} |
| Name | {human-readable} |
| Blueprint | {source repo — the design, NOT the executable} |
| Runtime | {CF Worker / Python / Node} |
| Deployed URL | {URL or "not deployed"} |
| Cron | {schedule or "none"} |
| ORBT | {OPR / RPR / BLD / T/T} |
| Strikes | {0/1/2/3} |
| Last Deployed | {date} |
```

---

### BLOCK 2: IMO
**Governed by: IMO**

What this process does. Fractal — each stage decomposes into its own IMO if needed.

| Field | Value |
|-------|-------|
| **CTB Position** | TRUNK of the process — this IS the process |
| **Input** | What triggers it? What data comes in? From where? |
| **Middle** | What processing happens? Numbered steps. |
| **Output** | What comes out? Where does it go? |
| **Circle** | How does feedback flow back? |

**Two-question intake (Bedrock §3):**
1. "What triggers this?" — must be answerable
2. "How do we get it?" — must be answerable

If either can't be answered → STOP. The process isn't defined yet.

---

### BLOCK 3: DATABASES
**Governed by: CTB**

Where this process lives in the data hierarchy. One CANONICAL + one ERROR per sub-hub (Bedrock §4 — CQRS).

| Field | Value |
|-------|-------|
| **CTB Position** | BRANCH — each database is a silo. Tables are leaves. |
| **Input** | Which databases does this process connect to? |
| **Middle** | Map every table: read or write? CANONICAL or ERROR or supporting? What join key? |
| **Output** | Complete data map — no blind spots |
| **Circle** | If a table is missing from this list, the process has an undocumented dependency |

**Required format:**

```
| Database | Table | Role | Read/Write | Join Key |
|----------|-------|------|------------|----------|
```

**Data flow diagram required** — ASCII showing the path from input tables through processing to output tables.

---

### BLOCK 4: ID FORMAT
**Governed by: C&V**

How this process mints and traces identifiers. The chain must be bidirectional (Bedrock §5 — Circle).

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — IDs are the atomic constants |
| **Input** | An event occurs that needs an identity |
| **Middle** | Mint ID in the defined format |
| **Output** | Traceable ID that links forward and backward |
| **Circle** | Given any ID, can you trace the full chain? If not, the format is broken. |

**Required format:**

```
| ID | Format | Example | Minted By |
|----|--------|---------|-----------|
```

---

### BLOCK 5: DEPENDENCIES
**Governed by: CTB**

What's upstream (must exist before this runs) and downstream (consumes this output). Sovereign silos — no direct branch-to-branch communication (Bedrock §4).

| Field | Value |
|-------|-------|
| **CTB Position** | BRANCH — this process sits between upstream and downstream |
| **Input** | What must be true before this process can run? |
| **Middle** | List every upstream dependency with status. List every downstream consumer. |
| **Output** | Complete dependency map |
| **Circle** | If an upstream breaks, this section tells you what to check. If this process breaks, downstream knows it's affected. |

**Required format:**

```
### Upstream
| Dependency | What | Status |
|-----------|------|--------|

### Downstream
| Consumer | What |
|----------|------|
```

---

### BLOCK 6: CURRENT STATE
**Governed by: Circle**

The sigma reading. What's the state right now? Must be dated — stale state is worse than no state (Bedrock §5 — sigma tracking).

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — a snapshot in time |
| **Input** | Query the system |
| **Middle** | Record observable metrics — counts, dates, health |
| **Output** | Dated snapshot |
| **Circle** | If sigma is flat (state hasn't been updated), the process isn't being monitored |

**Required format:**

```
## CURRENT STATE (as of {YYYY-MM-DD})

| Metric | Value |
|--------|-------|
```

---

### BLOCK 7: KNOWN ISSUES
**Governed by: Circle**

The error log. Append-only — never delete a resolved issue (Bedrock §8 — logbook is append-only). If the same issue appears 3 times → strike 3 → Troubleshoot/Train (Bedrock §6).

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — each issue is a single event |
| **Input** | Something broke |
| **Middle** | Record: what broke, how it was fixed, when |
| **Output** | Institutional memory — the process can't lose the same way twice |
| **Circle** | Strike 3 on same pattern → escalate to T/T, not another repair |

**Required format:**

```
| Date | Issue | Resolution | Strikes |
|------|-------|------------|---------|
```

Write "None" if no issues. Do NOT delete the section.

---

### BLOCK 8: SMOKE TEST
**Governed by: IMO**

The verification procedure. Numbered steps with expected output at each step. Must be executable — not prose (Bedrock §6, Step 11 — Verify Loop).

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — a specific test procedure |
| **Input** | The process is deployed and ready to test |
| **Middle** | Execute numbered steps. Observe actual vs expected at each boundary. |
| **Output** | PASS (all steps match expected) or FAIL (identify which step broke) |
| **Circle** | If smoke test fails → run troubleshooting loop (Bedrock §6). Don't guess. |

**Required format:**

```
1. {Action} → expected: {result}
2. {Action} → expected: {result}
...
```

---

### BLOCK 9: NEXT STEPS
**Governed by: CTB**

What remains to be done. Links to BARs. Altitude-ordered — trunk-level work first.

| Field | Value |
|-------|-------|
| **CTB Position** | LEAF — specific action items |
| **Input** | The process exists at its current state |
| **Middle** | Identify what's missing, what's next, what's blocked |
| **Output** | Prioritized list with BAR references |
| **Circle** | As items complete, update this section AND mark the BAR |

**Required format:**

```
| What | BAR | Status |
|------|-----|--------|
```

---

### BLOCK 10: FILES
**Governed by: CTB**

Directory listing. The tree of this process folder.

| Field | Value |
|-------|-------|
| **CTB Position** | The physical file structure mirrors the logical CTB |
| **Input** | The process folder exists |
| **Middle** | List every file with its purpose |
| **Output** | Complete file map |

---

## Enforcement

- `heir.yaml` + `MANIFEST.md` = minimum viable process folder
- No process moves from BLD to OPR without a complete manifest
- The auditor (`factory/agents/agent-auditor/`) checks for manifest presence and completeness
- Any session that modifies a process MUST update the manifest before closing
- Manifest sections map 1:1 to Bedrock elements: C&V (identity, IDs), IMO (process flow), CTB (databases, dependencies, files), Circle (state, issues, smoke test)

---

## Three Primitives Check (Bedrock §1)

Before certifying any manifest, ask:
1. **Thing:** Does every component exist where it should? (tables, files, endpoints)
2. **Flow:** Does the data reach every component? (join keys, bindings, secrets)
3. **Change:** Does the transformation happen correctly? (compilation, delivery, webhook)

If any one fails → that's the break. The manifest told you where to look.

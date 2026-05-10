#!/usr/bin/env python3
"""
Dyno Engine — I = M + O

The Dyno calls us.py and up.py. They are the tools. The Dyno is the machine.

═══════════════════════════════════════════════════════════════
US/UP CONTRACT (law/doctrine/US_UP_CONTRACT.md)
═══════════════════════════════════════════════════════════════

us.py = M (builds the structure)
    I = domain (human provides — ONE input)
    O = all leaves at primitive (CONSTANT — Thing/Flow/Change/Connection)
    M = what us.py discovers (the unknown)
    Two knowns (I, O). One unknown (M). Solve for M.
    Runs until every leaf = primitive. 1 pass or 1000. Engine decides.

up.py = I (consumes the variables)
    M = structure from US (LOCKED — does not change)
    O = tolerance from human (human defines P=1)
    I = variables to consume (the unknown)
    Two knowns (M, O). One unknown (I→0). Consume I through M.
    Runs until I=0. All variables consumed. P=1 within tolerance.

Handoff: US must finish before UP starts. No M = nothing to solve with.
         UP cannot modify M. If gap found → back to US.

═══════════════════════════════════════════════════════════════

Usage:
    # US phase — discover structure. ONE argument: the domain.
    python3 dyno_engine.py discover "B2B meeting setting"
    python3 dyno_engine.py discover "Type 2 Diabetes"
    python3 dyno_engine.py discover "Cancer treatment"
    # P=1 is hardcoded: all leaves at primitive. Not a parameter.
    # Models are LOCKED constants. Not overridable.
    # Number of passes: engine decides. Not a parameter.

    # UP phase — solve using structure. THREE arguments.
    python3 dyno_engine.py solve "Book meetings with CEOs" "≥10 meetings/month" --m path/to/us/output
    python3 dyno_engine.py solve "Manage A1C" "A1C ≤ 5.6" --m path/to/us/output
    # M comes from US (locked). O (tolerance) comes from human.
    # UP consumes I through M until I=0.

    # Status
    python3 dyno_engine.py status path/to/run/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error

# Force UTF-8 output on Windows (cp1252 default breaks Unicode chars in prompts/logs)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════════════
# CONSTANTS — the engine's geometry. Does not change.
# ═══════════════════════════════════════════════════════════════

UP_ROOT = Path(__file__).resolve().parent
REPO_ROOT = UP_ROOT.parents[2]
RUNS_DIR = UP_ROOT / "runs"

# ═══════════════════════════════════════════════════════════════
# LOCKED CONSTANTS — API + Models
# OpenRouter is the API constant. Three models are constants.
# Only change on deprecation or human-approved upgrade
# (maintenance event + logbook entry).
# See: factory/agents/up/docs/US_ENGINE_SPEC.md
# ═══════════════════════════════════════════════════════════════
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"  # LOCKED — the API

# Model deployment by altitude:
#   Passes 1-3: expensive models (trunk + major branches — high consequence)
#   Passes 4+:  cheap models (decompose to primitive — mechanical)
# The cutoff (3) is the only tunable. The rule and the rosters are constants.
# See: factory/agents/up/ARCHITECTURE.md

EXPENSIVE_MODELS = [
    "anthropic/claude-opus-4-6",             # Slot A: top Anthropic — 80.8% SWE-bench, 1M context
    "google/gemini-2.5-pro-preview",         # Slot B: top Google available on OpenRouter
    "openai/gpt-4o",                         # Slot C: top OpenAI — stable OpenRouter resolution (was gpt-5.4, which 404s)
]

CHEAP_MODELS = [
    "google/gemini-2.0-flash-001",           # Slot A: fast, cheap, good structured output
    "anthropic/claude-3.5-haiku",            # Slot B: different architecture, good schema adherence
    "meta-llama/llama-3.3-70b-instruct",     # Slot C: open source, different training, tiebreaker
]

ALTITUDE_CUTOFF = 3  # Passes 1-3 = expensive, 4+ = cheap

# Default (legacy) — used by `run` command for backwards compat
DEFAULT_MODELS = list(CHEAP_MODELS)


# ═══════════════════════════════════════════════════════════════
# STRICT OUTPUT SCHEMA — the 7-field KEY, enforced at the API boundary.
# Output is the locked constant. LLMs are the variable. Any LLM that
# cannot honor this schema is unsuitable and is dropped from the pool.
# Source of truth: law/doctrine/KEY.md (10th locked constant).
# ═══════════════════════════════════════════════════════════════

CANDIDATE_OUTPUT_SCHEMA = {
    # US PROCESS 1 SCHEMA — SKELETON ONLY. Name + primitive. No vocabulary.
    # "Throw shit against the wall" per the locked doctrine (2026-04-19).
    # Vocabulary (abbreviation, description, behavior, context, example) is
    # produced BY Process 2 (K=C Audit) — NOT by US. US goes wide + deep on
    # structure; K=C fills the dictionary. See FCE_LIFECYCLE.md.
    "type": "object",
    "properties": {
        "cycle": {"type": "integer"},
        "domain": {"type": "string"},
        "p1_definition": {"type": "string"},
        "mode": {"type": "string"},
        "candidates_evaluated": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "primitive": {"type": "string", "enum": ["Thing", "Flow", "Change"]},
                },
                "required": ["name", "primitive"]
            }
        },
        "new_locked": {"type": "array", "items": {"type": "string"}},
        "remaining_variables": {"type": "array", "items": {"type": "string"}},
        "sigma": {"type": "string"},
        "p_status": {"type": "string"}
    },
    "required": ["candidates_evaluated"]
}
LBB_URL = os.environ.get("LBB_URL", "https://lbb.svg-outreach.workers.dev")
D1_DB = "svg-d1-outreach-ops"
WRANGLER_CWD = Path(__file__).resolve().parents[3] / "workers" / "lcs-hub"
R2_BUCKET = "svg-files"


# ═══════════════════════════════════════════════════════════════
# M — THE ENGINE DEFINITION
# This is the base M that every run starts with.
# It contains the full definitions — not labels, definitions.
# This is the fire before any wood is added.
# ═══════════════════════════════════════════════════════════════

BASE_M = """
# THE ENGINE (M) — Locked Constants

## Three Primitives (the floor — cannot reduce further)

- THING: Something exists. If it doesn't exist, nothing happens.
- FLOW: Something moves or interacts. No movement = no system.
- CHANGE: Something transforms. No change = no outcome.

Every comparator must trace to exactly one primitive. If it doesn't → reject it.

Diagnostic questions:
1. Did the Thing exist where it should?
2. Did the Flow reach it?
3. Did the Change happen correctly?

## Constants & Variables (C&V)

CONSTANT: Anything with structure. If you can name it or define its format → constant.
VARIABLE: The value that fills a named, formatted position → variable.
DOMESTICATED VARIABLE: Range so tight it can't change the outcome → stop decomposing.

The C&V Test (apply to everything):
1. Can you NAME it? → constant candidate
2. Can you define its FORMAT? → constant candidate
3. Is it the VALUE filling a position? → variable

## The Equation

P(x; θ) = 1  if  max_i [ C_i(x) / k_i ] ≤ 1
P(x; θ) = 0  otherwise

Where:
- x = candidate being evaluated
- C_i(x) = comparator function (measures one aspect, produces a number)
- k_i = tolerance threshold (maximum acceptable value)
- r(x) = diagnostic vector: [C_1(x)/k_1, C_2(x)/k_2, ...]

Operations (in order):
0. Non-nullity: ∑|C_i(x)| > ε — reject zero-signal candidates
1. Decision: compute P(x; θ) — binary
2. Diagnostics: compute r(x) — which broke, by how much
3. Stability: P must hold across N feedback cycles
4. Global gate: adding x_new → revalidate ALL prior constants
5. Feasibility: tolerance set must have room — no knife-edge

## Tier 0 (what moves the equation)

Four elements applied SIMULTANEOUSLY, not sequentially:
1. C&V — separates structure from fill
2. IMO — does it hold regardless of what flows through? (Input → Middle → Output)
3. CTB — does it hold at every altitude? (Trunk → Branch → Leaf)
4. Circle — does it hold after a full feedback cycle?

Survives all four → constant. Lock it.
Fails any one → variable. Classify with guard rails.

## Engine Geometry

Two axes:
- HORIZONTAL = IMO (I → M → O, the flow)
- VERTICAL = C&V + CTB (decompose down, back-propagate up)

The equation measures (static). Tier 0 moves (both axes + Circle).

I = M + O. M grows by consuming I. P=1 when I=0.

## Sigma Tracking

- Tightening → real constant. Lock it.
- Flat → phantom constant. Investigate.
- Expanding → broken prior constant. Reclassify.

## Back-Propagation

Every new constant must be checked against ALL prior constants.
If it breaks a prior → reclassify prior as variable → re-run.

## THE 9 SYMBOLS — Structural Terminology

Use these terms consistently when naming and classifying. Do not invent synonyms.

| Symbol | Category | What It Means |
|--------|----------|---------------|
| Thing | Primitive | Something that EXISTS. Remove it → system breaks. |
| Flow | Primitive | Something that MOVES. No movement → system breaks. |
| Change | Primitive | Something that TRANSFORMS. No transformation → no outcome. |
| Trunk | CTB Position | The ROOT of any tree. Depth 0. Fix trunk → everything below improves. |
| Branch | CTB Position | EVERYTHING BETWEEN trunk and leaf. Has parent above, children below. |
| Leaf | CTB Position | TERMINAL node. No children. Where execution happens. |
| Constant | C&V Class | STRUCTURE. Can you name it + format it? The field, not the fill. |
| Variable | C&V Class | FILL. The value occupying a named, formatted position. |
| Domesticated | C&V Class | A variable whose range can't change the outcome. Stop analyzing. |

When naming candidates:
- Use plain structural names (e.g., "Gateway", "Tool Manifest", "Approval Gate")
- Classify each by primitive (Thing/Flow/Change) AND CTB position (Trunk/Branch/Leaf)
- Every name must be a CONSTANT (nameable + formattable) — not a description of behavior
- If two candidates are the same THING with different names, merge them
- Prefer nouns (Things) and noun phrases (Flows/Changes) over verbs or adjectives
"""


# ═══════════════════════════════════════════════════════════════
# FILLED EXAMPLES — one per primitive.
# Every prompt embeds all three so the LLM sees the full surface
# of how Thing/Flow/Change each fill the 7-column KEY vocabulary.
# Prevents primitive-skewed output.
# ═══════════════════════════════════════════════════════════════

LAYER_FILLED_EXAMPLE_THING = """{
  "name": "Capital",
  "primitive": "Thing",
  "vocabulary": {
    "abbreviation": "CAP",
    "description": "A pool of financial resources that exists prior to any deployment decision.",
    "behavior": "sits as reserve until deployed",
    "context": "start of every investment cycle",
    "example": "$500k in a money-market fund"
  }
}"""

LAYER_FILLED_EXAMPLE_FLOW = """{
  "name": "Capital Deployment",
  "primitive": "Flow",
  "vocabulary": {
    "abbreviation": "DEPLOY",
    "description": "The movement of funds from reserve into an active position.",
    "behavior": "routes approved capital to the target instrument",
    "context": "after an allocation decision passes risk review",
    "example": "wire of $250k to equity brokerage, T+2 settle"
  }
}"""

LAYER_FILLED_EXAMPLE_CHANGE = """{
  "name": "Position Appreciation",
  "primitive": "Change",
  "vocabulary": {
    "abbreviation": "APPREC",
    "description": "The upward transformation of a position's market value over time.",
    "behavior": "increases mark-to-market value of the holding",
    "context": "on every mark-to-market cycle after entry",
    "example": "entered $50, marked $62 after 90 days (24% unrealized)"
  }
}"""

THREE_PRIMITIVE_EXAMPLES_BLOCK = """
US PROCESS 1 — structure + terse vocabulary fill.

Your job (US Process 1):
- Produce one row per structural element with 7 columns filled: name, primitive, and 5 vocab fields (abbreviation, description, behavior, context, example).
- Keep vocab content LIGHT — description is 1-2 sentences; abbreviation/behavior/context/example are short phrases.
- Do NOT validate whether description matches primitive — that's Process 2 (K=C Audit), a separate Dyno sub-run that runs AFTER US P=1.
- Primitive ∈ {Thing, Flow, Change} — exact spelling, exact case, no exceptions.

Three dictionary-entry examples showing the light fill shape:

EXAMPLE 1 (Thing):
""" + LAYER_FILLED_EXAMPLE_THING + """

EXAMPLE 2 (Flow):
""" + LAYER_FILLED_EXAMPLE_FLOW + """

EXAMPLE 3 (Change):
""" + LAYER_FILLED_EXAMPLE_CHANGE + """
"""


# ═══════════════════════════════════════════════════════════════
# ENGINE STATE — what the engine carries through cycles
# ═══════════════════════════════════════════════════════════════

@dataclass
class EngineState:
    """The state of I = M + O at any point in time."""
    # O — the destination (set by human, never changes)
    p1_definition: str

    # M — the engine (only grows)
    locked_constants: list[dict] = field(default_factory=list)
    base_m: str = BASE_M

    # I — the fuel (only shrinks)
    variables: list[dict] = field(default_factory=list)
    domain: str = ""

    # Operational
    run_dir: Path = field(default_factory=lambda: Path("."))
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    models: list[str] = field(default_factory=lambda: list(DEFAULT_MODELS))
    model_tier: str = "auto"  # "expensive", "cheap", or "auto" (altitude-based)
    cycle: int = 0
    # NOT a convergence criterion. The engine runs until P=1. Number of cycles
    # is the VARIABLE. This field is a runaway-loop safety stop only — set very
    # high so it never triggers in normal operation. If it triggers, log and
    # report that sigma failed to converge (not "done").
    max_cycles: int = 10000  # safety stop, not a design cap
    spend_log: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # History — sigma tracking across cycles
    ratio_history: list[dict] = field(default_factory=list)

    # Sigma log — per-cycle direction: tightening / flat / expanding
    # Each entry: {cycle, direction, constants_locked, variables_remaining, timestamp}
    sigma_log: list[dict] = field(default_factory=list)

    # Equation rotation state
    # Rotation triggers when sigma is flat/expanding for rotation_trigger_cycles consecutive cycles.
    # Rotation multiplies k_i tolerances by rotation_multiplier to relax thresholds temporarily.
    # Resets after rotation_max_attempts cycles or when sigma tightens again.
    rotation_active: bool = False
    rotation_multiplier: float = 1.25   # expand k_i by 25% each rotation (human-tunable)
    rotation_trigger_cycles: int = 2    # consecutive flat/expanding cycles before rotating
    rotation_max_attempts: int = 3      # maximum rotation passes before giving up
    rotation_count: int = 0             # how many rotations have been attempted
    stuck_cycle_count: int = 0          # consecutive flat/expanding cycles this run

    # D1 awareness — data context injected into prompts when available
    # Populated by d1_get_context() at engine start.
    d1_context: dict = field(default_factory=dict)

    @property
    def m_size(self) -> int:
        return len(self.locked_constants)

    @property
    def i_size(self) -> int:
        return len(self.variables)

    @property
    def is_done(self) -> bool:
        """P=1 when I=0. All variables either locked or domesticated."""
        return self.i_size == 0 and self.cycle > 0


# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    slug = value.strip().lower()
    for old, new in (("/", "-"), (" ", "-"), ("_", "-")):
        slug = slug.replace(old, new)
    return "".join(ch for ch in slug if ch.isalnum() or ch == "-")[:40] or "run"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Explicit UTF-8 — LLM output contains arrows, em-dashes, unicode; Windows cp1252 crashes silently.
    path.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def extract_json_from_text(text: str) -> str | None:
    """Extract first valid JSON object from LLM response."""
    text = text.strip()
    if text.startswith("{"):
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass
    for pattern in [r"```json\s*\n(.*?)\n```", r"```\s*\n(.*?)\n```", r"(\{.*\})"]:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            candidate = match.group(1).strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                continue
    return None


def d1_execute(sql: str) -> bool:
    """Execute SQL against D1 via wrangler."""
    import subprocess
    try:
        r = subprocess.run(
            ["npx", "wrangler", "d1", "execute", D1_DB,
             "--remote", "--command", sql, "--json"],
            cwd=str(WRANGLER_CWD), capture_output=True, text=True, timeout=30,
        )
        return r.returncode == 0
    except Exception:
        return False


def d1_write_run(state: "EngineState") -> bool:
    """Write or update the run record in D1 dyno_runs."""
    sql_esc = lambda v: "'" + str(v).replace("'", "''") + "'" if v is not None else "NULL"
    m_json = json.dumps([c.get("name", "?") for c in state.locked_constants])
    total_cost = sum(s.get("cost", 0) for s in state.spend_log
                     if isinstance(s.get("cost"), (int, float)))
    sql = (
        f"INSERT OR REPLACE INTO dyno_runs "
        f"(run_id, domain, m_constants, p1_definition, total_cycles, "
        f"sigma_direction, p_status, variables_discovered, variables_locked, "
        f"variables_domesticated, back_prop_conflicts, "
        f"r2_artifact_path, status, started_at, total_cost_usd, updated_at, side) "
        f"VALUES ("
        f"{sql_esc(state.run_id)}, {sql_esc(state.domain)}, "
        f"{sql_esc(m_json)}, {sql_esc(state.p1_definition)}, "
        f"{state.cycle}, {sql_esc(track_sigma(state, []) if len(state.ratio_history) >= 2 else 'insufficient_data')}, "
        f"{1 if state.is_done else 0}, "
        f"{state.m_size + state.i_size}, {state.m_size}, 0, 0, "
        f"{sql_esc(f'dyno-runs/us/{slugify(state.domain)}/{state.run_id}/')}, "
        f"{sql_esc('complete' if state.is_done else 'running')}, "
        f"{sql_esc(now_utc())}, {total_cost}, {sql_esc(now_utc())}, 'US')"
    )
    return d1_execute(sql)


def d1_write_cycle(state: "EngineState", cycle_result: dict, model: str,
                   tokens_in: int, tokens_out: int, cost: float) -> bool:
    """Write a cycle record to D1 dyno_cycles."""
    sql_esc = lambda v: "'" + str(v).replace("'", "''") + "'" if v is not None else "NULL"
    cycle_id = f"{state.run_id}-c{state.cycle:02d}-{slugify(model)}"
    new_locked = cycle_result.get("new_locked", [])
    remaining = cycle_result.get("remaining_variables", [])
    domesticated = cycle_result.get("domesticated", [])
    sigma = cycle_result.get("sigma", "?")
    back_prop = cycle_result.get("back_propagation_issues", [])
    sql = (
        f"INSERT OR REPLACE INTO dyno_cycles "
        f"(cycle_id, run_id, cycle_number, model_used, "
        f"variables_found, variables_locked, variables_domesticated, "
        f"still_blocking, sigma_direction, back_prop_conflicts, back_prop_broken, "
        f"tokens_in, tokens_out, cost_usd) "
        f"VALUES ("
        f"{sql_esc(cycle_id)}, {sql_esc(state.run_id)}, {state.cycle}, {sql_esc(model)}, "
        f"{len(new_locked) + len(remaining) + len(domesticated)}, "
        f"{len(new_locked)}, {len(domesticated)}, {len(remaining)}, "
        f"{sql_esc(sigma)}, {len(back_prop)}, {sql_esc(json.dumps(back_prop))}, "
        f"{tokens_in}, {tokens_out}, {cost})"
    )
    return d1_execute(sql)


def r2_push_artifact(key: str, content: str) -> bool:
    """Push a text artifact to R2."""
    import subprocess, tempfile
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            f.flush()
            r = subprocess.run(
                ["npx", "wrangler", "r2", "object", "put",
                 f"{R2_BUCKET}/{key}", "--file", f.name,
                 "--content-type", "application/json", "--remote"],
                capture_output=True, text=True, timeout=30,
            )
            os.unlink(f.name)
            return r.returncode == 0
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
# D1 AWARENESS — query live data for discovery context
# The Dyno can look at what actually lives in D1 before/during
# discovery. This grounds LLM candidates in real data shape,
# not imagination. Read-only. No writes from here.
# ═══════════════════════════════════════════════════════════════

def d1_query(sql: str, db: str = D1_DB) -> list[dict]:
    """Run a SELECT against D1 and return rows as list of dicts.
    Uses wrangler d1 execute --json output format.
    Returns [] on any failure — awareness is best-effort, never blocking.
    """
    import subprocess
    try:
        r = subprocess.run(
            ["npx", "wrangler", "d1", "execute", db,
             "--remote", "--command", sql, "--json"],
            cwd=str(WRANGLER_CWD), capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            return []
        data = json.loads(r.stdout)
        # wrangler --json returns [{results: [...], ...}]
        if isinstance(data, list) and data:
            return data[0].get("results", [])
        return []
    except Exception:
        return []


def d1_get_context(domain: str | None = None) -> dict:
    """Build a D1 awareness context for the engine.

    Returns a dict with:
        tables: [{name, row_count}] for the 10 most-populated tables
        dyno_prior_runs: prior runs for similar domains (by slug match)
        total_tables: int
        available: bool — False if D1 is unreachable

    This context gets injected into the prompt so LLMs know
    what data structures already exist and can ground their
    candidate generation in real facts.
    """
    context: dict = {"available": False, "tables": [], "dyno_prior_runs": [], "total_tables": 0}

    # 1. What tables exist?
    tables_raw = d1_query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '_cf_%' ORDER BY name;",
        db=D1_DB,
    )
    if not tables_raw:
        return context  # D1 unreachable — silently return empty context

    context["available"] = True
    table_names = [r.get("name", "") for r in tables_raw if r.get("name")]
    context["total_tables"] = len(table_names)

    # 2. Row counts for key tables (sample up to 15 — skip system tables)
    row_counts = []
    sample_tables = [t for t in table_names if not t.startswith("_")][:15]
    for tname in sample_tables:
        rows = d1_query(f"SELECT COUNT(*) as cnt FROM {tname};", db=D1_DB)
        cnt = rows[0].get("cnt", 0) if rows else 0
        row_counts.append({"name": tname, "row_count": cnt})

    # Sort by row count descending — most populated tables first
    row_counts.sort(key=lambda x: x["row_count"], reverse=True)
    context["tables"] = row_counts[:10]  # Top 10 by volume

    # 3. Prior Dyno runs for similar domains
    if domain:
        domain_slug = slugify(domain)[:20]
        prior_runs = d1_query(
            f"SELECT domain, total_cycles, variables_locked, p_status, started_at "
            f"FROM dyno_runs "
            f"WHERE domain LIKE '%{domain_slug}%' "
            f"ORDER BY started_at DESC LIMIT 5;",
            db=D1_DB,
        )
        context["dyno_prior_runs"] = prior_runs

    return context


def format_d1_context_for_prompt(d1_ctx: dict) -> str:
    """Format D1 context as a text block for injection into prompts.
    Empty string if D1 is unavailable — no noise when data is absent.
    """
    if not d1_ctx.get("available"):
        return ""

    lines = ["\n# D1 DATA AWARENESS — Live system context (read-only)"]
    lines.append(f"Total tables in system: {d1_ctx.get('total_tables', 0)}")

    tables = d1_ctx.get("tables", [])
    if tables:
        lines.append("\nTop tables by row count:")
        for t in tables:
            lines.append(f"  - {t['name']}: {t['row_count']:,} rows")

    prior_runs = d1_ctx.get("dyno_prior_runs", [])
    if prior_runs:
        lines.append("\nPrior Dyno runs on similar domains:")
        for r in prior_runs:
            lines.append(
                f"  - {r.get('domain','?')} | cycles={r.get('total_cycles','?')} "
                f"locked={r.get('variables_locked','?')} status={r.get('p_status','?')}"
            )

    lines.append(
        "\nUse this data awareness to ground your candidates in what actually exists. "
        "If a table maps to a structural element you're discovering, note it."
    )
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# EQUATION ROTATION — unstick P=0 cycles
# When sigma is flat or expanding for rotation_trigger_cycles
# consecutive cycles, rotate: multiply all k_i tolerances by
# rotation_multiplier to relax thresholds and see if more
# constants can be locked.
#
# Mechanically: if max_i[C_i(x)/k_i] is stuck just above 1.0,
# expanding k_i by 25% drops the ratios below 1.0 — unlocking
# previously-blocked constants. Human sets the multiplier.
# The engine resets after rotation_max_attempts or tightening sigma.
# ═══════════════════════════════════════════════════════════════

def rotate_tolerances(constants: list[dict], multiplier: float) -> list[dict]:
    """Apply tolerance rotation: multiply all k_i by multiplier.
    Returns a new list — does NOT mutate the original.
    Only affects constants with numeric k_tolerance.
    """
    rotated = []
    for c in constants:
        c_copy = dict(c)
        k = c_copy.get("k_tolerance")
        if k is not None:
            try:
                k_new = float(k) * multiplier
                # Enforce tolerance floor: k_i ≥ ε_k
                k_new = max(k_new, 0.001)
                c_copy["k_tolerance"] = round(k_new, 6)
                c_copy["_rotated"] = True
                c_copy["_rotation_multiplier"] = multiplier
            except (ValueError, TypeError):
                pass
        rotated.append(c_copy)
    return rotated


def check_rotation_needed(state: "EngineState") -> bool:
    """Return True if the engine is stuck and should rotate tolerances.

    Conditions:
    1. We're in MEASUREMENT mode (cycle > 3) — rotation requires numeric values
    2. sigma has been flat/expanding for rotation_trigger_cycles consecutive cycles
    3. We haven't exceeded rotation_max_attempts
    4. There are still variables remaining (I > 0)
    """
    if state.cycle <= 3:
        return False  # Discovery mode — no equation yet, rotation not applicable
    if state.i_size == 0:
        return False  # Already at P=1 — no need to rotate
    if state.rotation_count >= state.rotation_max_attempts:
        return False  # Exceeded max attempts — engine gives up on rotation
    return state.stuck_cycle_count >= state.rotation_trigger_cycles


def get_api_key(name: str) -> str:
    """Get API key from env or Doppler."""
    key = os.environ.get(name, "")
    if not key:
        try:
            import subprocess
            r = subprocess.run(
                ["doppler", "secrets", "get", name, "--plain",
                 "-p", "imo-creator", "-c", "dev"],
                capture_output=True, text=True, timeout=10,
            )
            key = r.stdout.strip()
        except Exception:
            pass
    return key


# ═══════════════════════════════════════════════════════════════
# THE EQUATION — deterministic arithmetic, no LLM needed
# ═══════════════════════════════════════════════════════════════

def compute_ratio(c_value: float, k_tolerance: float) -> float:
    """Compute one comparator ratio: C_i(x) / k_i."""
    if k_tolerance <= 0:
        return float("inf")  # invalid tolerance — always fails
    return c_value / k_tolerance


def compute_p(ratios: list[float]) -> int:
    """P(x;θ) = 1 if max ratio ≤ 1, else 0."""
    if not ratios:
        return 0  # non-nullity: no signal
    return 1 if max(ratios) <= 1.0 else 0


def compute_diagnostic_vector(candidates: list[dict]) -> list[dict]:
    """Compute r(x) for a list of candidates with numeric values.

    Each candidate must have:
        c_value: float  — the measured value (C_i(x))
        k_tolerance: float  — the threshold (k_i)

    COMPARATOR REQUIREMENT (tournament-validated):
        C_i(x) must be ≥ 0. Negative comparator values are invalid because
        negative / positive = negative ratio, which vacuously passes max ≤ 1.
        This was flagged by 4/5 LLMs in the engine tournament.

    Returns candidates enriched with:
        ratio: float
        p: 1 or 0
        gap: how far from tolerance (negative = within, positive = exceeded)
    """
    results = []
    for c in candidates:
        c_val = c.get("c_value")
        k_val = c.get("k_tolerance")
        if c_val is not None and k_val is not None:
            try:
                c_val = float(c_val)
                k_val = float(k_val)

                # Enforce C_i(x) ≥ 0 — negative comparators are invalid
                # Use absolute value: the equation measures magnitude of deviation
                c_val = abs(c_val)

                # Enforce k_i > 0 — tolerance floor prevents singularity
                k_val = max(abs(k_val), 0.001)

                ratio = compute_ratio(c_val, k_val)
                results.append({
                    **c,
                    "c_value_abs": c_val,
                    "k_tolerance_abs": k_val,
                    "ratio": round(ratio, 4),
                    "p": 1 if ratio <= 1.0 else 0,
                    "gap": round(c_val - k_val, 4),
                    "pct_over": round((ratio - 1.0) * 100, 2) if ratio > 1.0 else 0,
                })
            except (ValueError, TypeError):
                results.append({**c, "ratio": None, "p": None, "gap": None, "error": "non-numeric"})
        else:
            results.append({**c, "ratio": None, "p": None, "gap": None, "error": "missing values"})
    return results


def back_propagate(new_constant: dict, locked_set: list[dict]) -> list[str]:
    """Re-run the equation on ALL prior constants after adding new_constant.

    Returns list of prior constant names that broke (ratio now > 1).
    This is Operation 4 from the Math Principle — deterministic arithmetic.

    CRITICAL: Uses θ' (updated tolerance set including new_constant),
    NOT the old θ. Adding a new constant can shift tolerances for
    coupled priors. Tournament-validated fix: 5/5 LLMs flagged the
    old implementation for using stale θ.

    Each locked constant must have c_value and k_tolerance as numbers.
    """
    broken = []
    new_name = new_constant.get("name", "?")
    new_k = new_constant.get("k_tolerance")
    new_c = new_constant.get("c_value")

    # Build θ' — the updated tolerance set including the new constant
    # θ' = θ ∪ {new_constant's tolerances}
    # Any prior constant coupled to the new one gets its tolerance recalculated
    theta_prime = {}
    for prior in locked_set:
        pname = prior.get("name", "?")
        theta_prime[pname] = {
            "c_value": prior.get("c_value"),
            "k_tolerance": prior.get("k_tolerance"),
        }
    theta_prime[new_name] = {"c_value": new_c, "k_tolerance": new_k}

    for prior in locked_set:
        prior_name = prior.get("name", "?")
        if prior_name == new_name:
            continue

        c_val = prior.get("c_value")
        k_val = prior.get("k_tolerance")

        if c_val is None or k_val is None:
            continue

        try:
            c_val = float(c_val)
            k_val = float(k_val)
        except (ValueError, TypeError):
            continue

        # Check coupling: does the new constant affect this prior's tolerance?
        coupled_to = prior.get("coupled_to", [])
        if new_name in coupled_to and new_k is not None:
            # Coupled tolerance — recalculate k under θ'
            # The new constant's presence shifts this prior's effective tolerance
            shift = prior.get("coupling_shift", 0)
            try:
                shift = float(shift)
            except (ValueError, TypeError):
                shift = 0
            k_val_prime = k_val + shift
            # Enforce tolerance floor: k_i ≥ ε_k (prevent singularity)
            k_val_prime = max(k_val_prime, 0.001)
            ratio = compute_ratio(c_val, k_val_prime)
            print(f"      BACK-PROP (coupled): {prior_name} k={k_val}→{k_val_prime} ratio={ratio:.4f}")
        else:
            # Not coupled — re-run with same tolerance under θ'
            ratio = compute_ratio(c_val, k_val)

        if ratio > 1.0:
            broken.append(prior_name)
            print(f"      BACK-PROP: {prior_name} BROKE (ratio={ratio:.4f} > 1)")

    return broken


def solve_for_variable(variable: dict, locked_constants: list[dict], p1_definition: str) -> dict:
    """Algebraic isolation: given knowns (M) and target (O=P=1),
    solve for what this variable needs to be.

    Like algebra: if A + B + C = D and A, C are known, B = D - A - C.

    Returns the variable enriched with:
        required_value: what it needs to be for P=1
        current_gap: how far it is from required
        levers: what other variables influence this one
    """
    c_val = variable.get("c_value")
    k_val = variable.get("k_tolerance")

    result = {**variable}

    if c_val is not None and k_val is not None:
        try:
            c_val = float(c_val)
            k_val = float(k_val)
            ratio = compute_ratio(c_val, k_val)

            # To get P=1, need C_i(x)/k_i ≤ 1, so C_i(x) ≤ k_i
            # Required value = k_i (the tolerance IS the target)
            result["required_value"] = k_val
            result["current_value"] = c_val
            result["current_ratio"] = round(ratio, 4)
            result["gap"] = round(c_val - k_val, 4)
            result["needs_reduction"] = c_val > k_val
            result["pct_change_needed"] = round(((c_val - k_val) / c_val) * 100, 2) if c_val != 0 else 0
        except (ValueError, TypeError):
            result["error"] = "non-numeric values"
    else:
        result["error"] = "missing c_value or k_tolerance"

    # Identify what levers (other variables) influence this one
    result["influenced_by"] = variable.get("influenced_by", [])
    result["influences"] = variable.get("influences", [])

    return result


def track_sigma(state: "EngineState", cycle_ratios: list[dict]) -> str:
    """Track sigma across cycles. Returns tightening/flat/expanding.

    Also updates state.sigma_log (per-cycle record) and
    state.stuck_cycle_count (for equation rotation trigger).

    Sigma semantics:
      tightening — real constant being locked (ratio range narrowing)
      flat       — phantom constant or no new progress
      expanding  — something broke upstream or misclassification
    """
    state.ratio_history.append({
        "cycle": state.cycle,
        "ratios": {r.get("name", "?"): r.get("ratio") for r in cycle_ratios if r.get("ratio") is not None},
        "timestamp": now_utc(),
    })

    if len(state.ratio_history) < 2:
        direction = "insufficient_data"
        # Log it anyway — first cycle is the baseline
        state.sigma_log.append({
            "cycle": state.cycle,
            "direction": direction,
            "constants_locked": state.m_size,
            "variables_remaining": state.i_size,
            "rotation_active": state.rotation_active,
            "rotation_count": state.rotation_count,
            "timestamp": now_utc(),
        })
        return direction

    # Compare last two cycles
    prev = state.ratio_history[-2]["ratios"]
    curr = state.ratio_history[-1]["ratios"]

    # Find common candidates
    common = set(prev.keys()) & set(curr.keys())
    if not common:
        direction = "no_overlap"
        state.sigma_log.append({
            "cycle": state.cycle,
            "direction": direction,
            "constants_locked": state.m_size,
            "variables_remaining": state.i_size,
            "rotation_active": state.rotation_active,
            "rotation_count": state.rotation_count,
            "timestamp": now_utc(),
        })
        return direction

    tightening = 0
    expanding = 0
    flat = 0
    delta_details: list[dict] = []
    for name in common:
        prev_r = prev[name]
        curr_r = curr[name]
        if prev_r is None or curr_r is None:
            continue
        diff = curr_r - prev_r
        if diff < -0.01:
            tightening += 1
            delta_details.append({"name": name, "delta": round(diff, 4), "direction": "tightening"})
        elif diff > 0.01:
            expanding += 1
            delta_details.append({"name": name, "delta": round(diff, 4), "direction": "expanding"})
        else:
            flat += 1
            delta_details.append({"name": name, "delta": round(diff, 4), "direction": "flat"})

    if expanding > tightening:
        direction = "expanding"
    elif tightening > flat:
        direction = "tightening"
    else:
        direction = "flat"

    # Update stuck_cycle_count for rotation trigger
    if direction in ("flat", "expanding"):
        state.stuck_cycle_count += 1
    else:
        state.stuck_cycle_count = 0  # Reset on progress

    # Log the full per-cycle sigma record
    state.sigma_log.append({
        "cycle": state.cycle,
        "direction": direction,
        "constants_locked": state.m_size,
        "variables_remaining": state.i_size,
        "tightening_count": tightening,
        "flat_count": flat,
        "expanding_count": expanding,
        "delta_details": delta_details,
        "stuck_cycle_count": state.stuck_cycle_count,
        "rotation_active": state.rotation_active,
        "rotation_count": state.rotation_count,
        "timestamp": now_utc(),
    })

    return direction


# ═══════════════════════════════════════════════════════════════
# OPENROUTER — the parser (not the intelligence)
# ═══════════════════════════════════════════════════════════════

def classify_description_primitive(description: str, constant_name: str = "?") -> str | None:
    """LEGACY single-model classifier (kept for reference). Prefer kc_audit_consensus.

    Returns None. Direct single-model classification is deprecated — the K=C audit
    now runs as its own 3-model consensus Dyno sub-run, not a single classifier call.
    See kc_audit_consensus() below.
    """
    return None


def kc_audit_consensus(constants: list[dict]) -> dict:
    """K=C audit as its own Dyno sub-run. 3 expensive models independently classify
    every constant's description and consensus determines the verdict per row.

    Dyno-on-Dyno: the audit is its own discovery problem with the same rigor as
    the main run. Aviation Model — the inspector uses the same instrument suite
    as the mechanic but is a different engine per row.

    Input: list of {name, primitive, vocabulary: {description}, ...}
    Output: {
      "verdicts": [{name, claimed_primitive, votes: {model→primitive}, consensus, agreement, verdict}],
      "summary": {match, mismatch, split, total, cost, tokens},
      "timestamp": isoformat
    }

    Each row gets:
      verdict = "MATCH" (consensus == claimed), "MISMATCH" (consensus != claimed),
                "SPLIT" (3 models disagree, no consensus), "INSUFFICIENT" (models errored)
      agreement = "3/3" | "2/3" | "1/1/1" | "partial"

    Batched: each model gets the full list of descriptions in one call, returns all
    classifications. 3 calls total, not 3 × N. Cheap and fast.
    """
    from collections import Counter

    # Build the batched prompt — show the Three Primitives algorithm and ask for
    # one classification per description in a JSON array.
    rows_for_prompt = [
        {
            "id": f"R{i+1}",
            "name": c.get("name", "?"),
            "description": (c.get("vocabulary") or {}).get("description", "") or "",
        }
        for i, c in enumerate(constants)
    ]
    prompt = (
        "You are running the Three Primitives algorithm on a batch of descriptions.\n\n"
        "THE THREE PRIMITIVES (irreducible floor):\n"
        "- Thing: Something that EXISTS. A component, entity, container, structure.\n"
        "  Test: If removed, does the system break because something no longer exists?\n"
        "- Flow: Something that MOVES. A pathway, transfer, sequence, process of movement.\n"
        "  Test: If nothing moved through it, does the system break because transfer stopped?\n"
        "- Change: Something that TRANSFORMS. A state transition, conversion, shift.\n"
        "  Test: If the transformation stopped, does the system break because no outcome occurs?\n\n"
        "TASK: For EVERY row below, apply the inversion test to the description. Which single primitive does it reduce to?\n"
        "Exactly one of Thing|Flow|Change per row. Exact capitalization. No other values.\n\n"
        f"ROWS ({len(rows_for_prompt)}):\n{json.dumps(rows_for_prompt, indent=2)}\n\n"
        "Output ONLY valid JSON:\n"
        '{"classifications": [{"id": "R1", "primitive": "Thing|Flow|Change"}, ...]}'
    )

    # Fire all 3 expensive models in the same batched prompt
    model_results: dict[str, dict] = {}
    total_cost = 0.0
    total_tokens_in = 0
    total_tokens_out = 0
    for model in EXPENSIVE_MODELS:
        model_short = model.split("/")[-1]
        try:
            result = call_openrouter(model, prompt, max_tokens=8000, temperature=0.0)
        except Exception as e:
            print(f"      [K=C audit error {model_short}]: {e}")
            continue
        total_cost += result.get("cost", 0) or 0
        total_tokens_in += result.get("tokens_in", 0) or 0
        total_tokens_out += result.get("tokens_out", 0) or 0
        content = result.get("content", "") or ""
        # Parse the classifications array
        json_str = extract_json_from_text(content)
        if not json_str:
            continue
        try:
            parsed = json.loads(json_str)
            classifications = parsed.get("classifications") or []
            # Build id → primitive map, strict enum match only
            id_to_prim = {}
            for item in classifications:
                row_id = item.get("id")
                prim = item.get("primitive", "")
                if row_id and prim in {"Thing", "Flow", "Change"}:
                    id_to_prim[row_id] = prim
            model_results[model_short] = id_to_prim
        except json.JSONDecodeError:
            continue

    # Build per-row verdicts from the 3 model results
    verdicts = []
    counters = {"MATCH": 0, "MISMATCH": 0, "SPLIT": 0, "INSUFFICIENT": 0}
    for i, c in enumerate(constants):
        row_id = f"R{i+1}"
        claimed = c.get("primitive", "")
        votes = {m: model_results[m].get(row_id) for m in model_results
                 if model_results[m].get(row_id)}
        if not votes:
            verdict = "INSUFFICIENT"
            consensus = None
            agreement = "0"
        else:
            vote_counts = Counter(votes.values())
            top, count = vote_counts.most_common(1)[0]
            if count == 3:
                agreement, consensus = "3/3", top
            elif count == 2:
                agreement, consensus = "2/3", top
            elif len(vote_counts) == 3:  # 1/1/1 disagreement
                agreement, consensus = "1/1/1", None
            elif len(votes) < 3:  # partial returns
                agreement = f"{count}/{len(votes)}"
                consensus = top if count > len(votes) / 2 else None
            else:
                agreement, consensus = "partial", None
            if consensus is None:
                verdict = "SPLIT"
            elif consensus == claimed:
                verdict = "MATCH"
            else:
                verdict = "MISMATCH"
        counters[verdict] += 1
        verdicts.append({
            "name": c.get("name", "?"),
            "claimed_primitive": claimed,
            "votes": votes,
            "consensus": consensus,
            "agreement": agreement,
            "verdict": verdict,
        })

    return {
        "verdicts": verdicts,
        "summary": {
            **counters,
            "total": len(constants),
            "tokens_in": total_tokens_in,
            "tokens_out": total_tokens_out,
            "cost": round(total_cost, 4),
            "models_that_returned": list(model_results.keys()),
        },
        "timestamp": now_utc(),
    }


def call_openrouter(model: str, prompt: str,
                    max_tokens: int = 16000, temperature: float = 0.3,
                    response_schema: dict | None = None) -> dict:
    """Call one model via OpenRouter. Returns {content, tokens_in, tokens_out, cost}.

    When response_schema is provided, the API enforces the schema at the boundary
    via response_format.type=json_schema (strict). Non-conforming models fail loud
    instead of silently drifting — doctrine: output trumps LLM.
    """
    api_key = get_api_key("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("No OPENROUTER_API_KEY found")

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if response_schema is not None:
        # PER-MODEL RESPONSE_FORMAT POLICY (2026-04-18):
        # OpenAI's strict json_schema mode has stricter requirements than Anthropic/Google —
        # every property must be in `required`, every object must have `additionalProperties: false`.
        # Our schema intentionally allows extra fields (tier0_check, cv_test, etc. the LLMs emit
        # beyond the required minimum), which OpenAI 400s on. Fix: for OpenAI models use
        # `json_object` mode (just "return valid JSON") — our in-engine validators + prompt
        # contract catch schema violations post-hoc. Strict schema kept for Anthropic/Google.
        if model.startswith("openai/"):
            payload["response_format"] = {"type": "json_object"}
        else:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "dyno_output",
                    "strict": True,
                    "schema": response_schema,
                },
            }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://imo-creator.svg.agency",
        "X-Title": "Dyno Engine",
    }

    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    content = ""
    if "choices" in data and data["choices"]:
        content = data["choices"][0].get("message", {}).get("content", "")

    usage = data.get("usage", {})
    return {
        "content": content,
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "cost": usage.get("cost", 0),
        "model": model,
    }


# ═══════════════════════════════════════════════════════════════
# PROMPT BUILDER — formats I = M + O as a prompt
# ═══════════════════════════════════════════════════════════════

def build_prompt(state: EngineState) -> str:
    """Build I = M + O as a prompt for the LLM.

    Two modes based on engine phase:
    - DISCOVERY (cycles 1-3): Find what STRUCTURES exist. No numbers.
      "What must exist? What would break if removed?"
    - MEASUREMENT (cycles 4+): Measure the discovered structures.
      Numeric c_value/k_tolerance only AFTER structure is known.
    """

    # M — the engine + all locked constants
    locked_text = ""
    if state.locked_constants:
        locked_items = []
        for c in state.locked_constants:
            desc = c.get('description', '')
            desc_line = f"\n      Description: {desc}" if desc else ""
            locked_items.append(
                f"  - {c['name']} [{c.get('primitive', '?')}] "
                f"(locked cycle {c.get('locked_cycle', '?')}): {c.get('why', '')}{desc_line}"
            )
        locked_text = f"\n\nLOCKED CONSTANTS (already in M — do not re-discover):\n" + "\n".join(locked_items)

    # Variables still in I
    variables_text = ""
    if state.variables:
        var_items = []
        for v in state.variables:
            var_items.append(
                f"  - {v['name']} [{v.get('primitive', '?')}]: {v.get('status', 'unclassified')}"
            )
        variables_text = f"\n\nVARIABLES STILL IN I (decompose these):\n" + "\n".join(var_items)

    # DISCOVERY mode (first 3 cycles) vs MEASUREMENT mode (cycle 4+)
    is_discovery = state.cycle < 3

    if is_discovery:
        task_section = f"""# YOUR TASK — Cycle {state.cycle + 1} (DISCOVERY MODE)

You are discovering the STRUCTURE of this domain. NOT measuring it. NOT inventing numbers.

For this domain, find what MUST EXIST for it to function:

1. STRUCTURAL DISCOVERY using Three Primitives:
   - THING: What must exist? What objects, components, or entities are required?
     Test: If you removed it, does the domain break? YES = structural. NO = optional.
   - FLOW: What must move? What pathways, sequences, or transfers are required?
     Test: If nothing moved through this path, does the domain break? YES = structural.
   - CHANGE: What must transform? What state transitions are required?
     Test: If this transformation stopped, does the domain break? YES = structural.

2. C&V TEST on each discovery:
   - Can you NAME it? (not a number — a structural element)
   - Can you define its FORMAT? (what it contains structurally, not its numeric value)
   - Would it exist in ANY implementation of this domain, regardless of specific numbers?
     YES = constant. NO = variable.

3. DEPTH CHECK:
   - For each structural element, ask: can this be decomposed further?
   - If YES: what are the sub-structures inside it?
   - If NO: you've hit primitive (Thing/Flow/Change at the leaf). Stop.

4. INVERSION TEST (the key):
   - "What would BREAK if you removed this?"
   - If removing it breaks the domain → STRUCTURAL CONSTANT
   - If removing it just changes a number or preference → VARIABLE (skip it)
   - Example: "A sequence of outreach touches exists" = structural (removing it = no outreach)
   - Example: "4-6 touches" = variable (changing the number doesn't break the concept)

DO NOT:
- Invent numeric values (no c_value, no k_tolerance — those come later)
- List best practices or tips
- Include platform-specific details (LinkedIn's 300 char limit is LinkedIn's variable, not structural)
- Include anything that wouldn't hold if you swapped the industry

Output ONLY valid JSON:
{{
  "cycle": {state.cycle + 1},
  "domain": "{state.domain}",
  "p1_definition": "{state.p1_definition}",
  "mode": "discovery",
  "candidates_evaluated": [
    {{
      "name": "<structural element name — not a number>",
      "primitive": "Thing|Flow|Change",
      "cv_test": {{"nameable": true, "formattable": true, "is_fill": false}},
      "format": "<what this structurally contains — not a numeric value>",
      "depth": <0=domain, 1=category, 2=component, 3=primitive>,
      "parent": "<parent element name or null if root>",
      "inversion_test": "<what breaks if you remove this>",
      "holds_across_implementations": true,
      "classification": "locked|variable|domesticated",
      "tier0_check": {{
        "cv": "pass|fail — is it structure not fill?",
        "imo": "pass|fail — does it hold regardless of what flows through?",
        "ctb": "pass|fail — does it hold at 50K and 5K?",
        "circle": "pass|fail — does it hold after a feedback cycle?"
      }},
      "why": "<one line — why this is structural>",
      "vocabulary": {{
        "abbreviation": "<shorthand or ->",
        "description": "<1-2 sentences max — what it IS>",
        "behavior": "<short phrase or clause — what it does>",
        "context": "<short phrase or clause — when you see it>",
        "example": "<short concrete instance — one phrase>"
      }}
    }}
  ],
  "new_locked": ["<structural elements that passed all 4 tests>"],
  "remaining_variables": ["<elements that need deeper decomposition>"],
  "domesticated": ["<elements whose range can't affect the structure>"],
  "sigma": "tightening|flat|expanding",
  "m_size": <total locked structural constants>,
  "i_size": <total elements still being decomposed>,
  "p_status": "P=0 (structure not fully mapped)|P=1 (all structural elements discovered to primitive)"
}}"""
    else:
        task_section = f"""# YOUR TASK — Cycle {state.cycle + 1} (MEASUREMENT MODE)

Structure has been discovered. Now MEASURE the locked structural constants.

For each structural constant already in M, define:
1. C_i(x): what specifically do you measure? (must trace to Thing, Flow, or Change)
2. k_i: what's the tolerance? (maximum acceptable value)
3. r(x) = C_i(x) / k_i
4. If max ratio ≤ 1 → P=1. If any > 1 → P=0.

Also evaluate any remaining variables from I:
- Can they now be measured?
- Are they domesticated (range too tight to affect P)?
- Do they need further decomposition?

Output ONLY valid JSON:
{{
  "cycle": {state.cycle + 1},
  "domain": "{state.domain}",
  "p1_definition": "{state.p1_definition}",
  "mode": "measurement",
  "candidates_evaluated": [
    {{
      "name": "<name>",
      "primitive": "Thing|Flow|Change",
      "cv_test": {{"nameable": true, "formattable": true, "is_fill": false}},
      "comparator": "<what you measure — C_i(x)>",
      "c_value": <NUMERIC current measured value>,
      "k_tolerance": <NUMERIC max acceptable threshold>,
      "ratio": <c_value / k_tolerance>,
      "influenced_by": ["<other candidates that affect this value>"],
      "influences": ["<other candidates this affects>"],
      "p_result": 1,
      "classification": "locked|variable|domesticated",
      "tier0_check": {{
        "cv": "pass — <reason>",
        "imo": "pass — <reason>",
        "ctb": "pass — <reason>",
        "circle": "pass — <reason>"
      }},
      "holds_across_implementations": true,
      "vocabulary": {{
        "abbreviation": "<shorthand or ->",
        "description": "<1-2 sentences max — what it IS>",
        "behavior": "<short phrase or clause — what it does>",
        "context": "<short phrase or clause — when you see it>",
        "example": "<short concrete instance — one phrase>"
      }},
      "back_propagation": "clean|broke <name>",
      "why": "<one line>"
    }}
  ],
  "new_locked": ["<names that moved to M>"],
  "remaining_variables": ["<names still in I>"],
  "domesticated": ["<names removed>"],
  "back_propagation_issues": ["<any prior constants that broke>"],
  "sigma": "tightening|flat|expanding",
  "m_size": <total locked constants>,
  "i_size": <total variables remaining>,
  "p_status": "P=0 (variables remain)|P=1 (I=0, done)"
}}"""

    # D1 awareness context — injected when available
    d1_block = format_d1_context_for_prompt(state.d1_context) if state.d1_context else ""

    # Rotation notice — tell the LLM if we've relaxed tolerances
    rotation_notice = ""
    if state.rotation_active:
        rotation_notice = (
            f"\n# EQUATION ROTATION ACTIVE (rotation #{state.rotation_count})\n"
            f"Sigma was stuck for {state.stuck_cycle_count} cycles. "
            f"Tolerances have been relaxed by {state.rotation_multiplier:.0%} to unlock blocked candidates. "
            f"Focus on any candidates that were borderline (ratio just above 1.0) in prior cycles.\n"
        )

    return f"""{state.base_m}
{THREE_PRIMITIVE_EXAMPLES_BLOCK}
{locked_text}
{d1_block}
{rotation_notice}
# O — THE DESTINATION (set by human, never changes)

P=1 means: {state.p1_definition}

# I — THE FUEL (domain: {state.domain})
{variables_text}

{task_section}
"""


def build_consolidation_prompt(outputs: list[dict], state: EngineState) -> str:
    """Consolidate 3 model outputs into one."""
    runs_text = []
    for output in outputs:
        model = output.get("_model", "unknown")
        candidates = output.get("candidates_evaluated", [])
        new_locked = output.get("new_locked", [])
        remaining = output.get("remaining_variables", [])
        runs_text.append(
            f"=== {model} ===\n"
            f"  Locked: {new_locked}\n"
            f"  Variables: {remaining}\n"
            f"  Candidates: {len(candidates)}\n"
            f"  Sigma: {output.get('sigma', '?')}\n"
        )

    return f"""CONSOLIDATE these {len(outputs)} model runs for cycle {state.cycle + 1}.

Domain: {state.domain}
P=1: {state.p1_definition}

{chr(10).join(runs_text)}

Full outputs:
{json.dumps(outputs, indent=2, default=str)}

Rules:
- 3/3 agree on a classification = LOCKED (constant)
- 2/3 agree = HIGH confidence
- 1/3 unique = INVESTIGATE
- For each candidate, pick the strongest classification that consensus supports
- Check back-propagation across all three outputs

CRITICAL: Preserve ALL structural fields from the source candidates — tier0_check,
holds_across_implementations, inversion_test, cv_test. Do not drop these.

Output ONLY valid JSON:
{{
  "cycle": {state.cycle + 1},
  "domain": "{state.domain}",
  "consolidation_method": "3-model consensus",
  "candidates": [
    {{
      "name": "<name>",
      "primitive": "Thing|Flow|Change",
      "classification": "locked|variable|domesticated",
      "confidence": "locked|high|investigate",
      "found_by": ["<model names>"],
      "comparator": "<what to measure>",
      "c_value": <NUMERIC measured value>,
      "k_tolerance": <NUMERIC threshold>,
      "ratio": <c_value / k_tolerance>,
      "influenced_by": ["<what affects this>"],
      "influences": ["<what this affects>"],
      "why": "<one line>",
      "cv_test": {{"nameable": true, "formattable": true, "is_fill": false}},
      "format": "<what this structurally contains>",
      "depth": <0-3>,
      "parent": "<parent name or null>",
      "inversion_test": "<what breaks if removed>",
      "holds_across_implementations": true,
      "tier0_check": {{
        "cv": "pass — <one-line reason>",
        "imo": "pass — <one-line reason>",
        "ctb": "pass — <one-line reason>",
        "circle": "pass — <one-line reason>"
      }},
      "vocabulary": {{
        "abbreviation": "<shorthand or ->",
        "description": "<1-2 sentences max — what it IS>",
        "behavior": "<short phrase or clause>",
        "context": "<short phrase or clause>",
        "example": "<short concrete instance>"
      }}
    }}
  ],
  "new_locked": ["<names — 3/3 or 2/3 agreed as constant>"],
  "remaining_variables": ["<names — still need decomposition>"],
  "domesticated": ["<names — all agree range can't change P>"],
  "back_propagation_issues": ["<any prior constants broken>"],
  "sigma": "tightening|flat|expanding",
  "m_size": <total locked>,
  "i_size": <total variables remaining>,
  "p_status": "P=0|P=1"
}}"""


# ═══════════════════════════════════════════════════════════════
# PASS-LEVEL AUDIT — whole-cycle coherence check.
# Runs AFTER row-level vocab gate + back-prop + sigma tracking.
# Per US Code Desk doctrine: pass cannot advance until coherent as a set.
# Checks that are scope-level (not per-row):
#   1. No duplicate names in state.locked_constants
#   2. Every primitive in the enum (post-lock sanity — belt-and-suspenders)
#   3. Every coupled_to/influenced_by reference resolves (no orphans)
#   4. No (name, primitive) collision where the same name maps to different primitives
# Returns list of violation dicts: [{name, type, reason, primitive}]
# ═══════════════════════════════════════════════════════════════

def pass_level_audit(state: "EngineState") -> list[dict]:
    """Audit the locked set AFTER a cycle completes. Return violations list (empty = CERTIFIED)."""
    violations: list[dict] = []
    legal_prims = {"Thing", "Flow", "Change"}

    # Map name → list of primitives (collision detection)
    seen_names: dict[str, list[str]] = {}
    locked_name_set: set[str] = set()
    for c in state.locked_constants:
        name = c.get("name")
        prim = c.get("primitive")
        if not name:
            continue
        seen_names.setdefault(name, []).append(prim)
        locked_name_set.add(name)

    # Check 1: duplicate names
    for name, prims in seen_names.items():
        if len(prims) > 1:
            if len(set(prims)) == 1:
                violations.append({
                    "name": name, "type": "duplicate_name",
                    "reason": f"name appears {len(prims)} times with same primitive {prims[0]}",
                    "primitive": prims[0],
                })
            else:
                violations.append({
                    "name": name, "type": "primitive_collision",
                    "reason": f"same name has conflicting primitives: {prims}",
                    "primitive": prims[0],
                })

    # Check 2: primitive in enum (belt-and-suspenders — schema should prevent this)
    for c in state.locked_constants:
        prim = c.get("primitive")
        if prim not in legal_prims:
            violations.append({
                "name": c.get("name", "?"), "type": "bad_primitive",
                "reason": f"primitive {prim!r} not in {sorted(legal_prims)}",
                "primitive": prim,
            })

    # Check 3: reference integrity — coupled_to + influenced_by must resolve
    known_refs = locked_name_set | {v.get("name") for v in state.variables if v.get("name")}
    for c in state.locked_constants:
        for ref_field in ("coupled_to", "influenced_by", "influences"):
            refs = c.get(ref_field, []) or []
            if not isinstance(refs, list):
                continue
            for r in refs:
                if r and r not in known_refs:
                    violations.append({
                        "name": c.get("name", "?"), "type": "orphan_reference",
                        "reason": f"{ref_field} references {r!r} which is not locked or in variables",
                        "primitive": c.get("primitive", "?"),
                    })

    return violations


# ═══════════════════════════════════════════════════════════════
# THE ENGINE LOOP — I = M + O until I=0
# ═══════════════════════════════════════════════════════════════

def run_cycle(state: EngineState) -> dict | None:
    """Run one cycle of I = M + O across 3 models and consolidate."""
    state.cycle += 1

    # Altitude-based tier selection restored (2026-04-19). Doctrine: expensive
    # for first 3 cycles (trunk + first branches — judgment-heavy), cheap after
    # (leaf-level mechanical). model_tier="expensive"/"cheap" forces one tier.
    if state.model_tier == "expensive":
        cycle_models = EXPENSIVE_MODELS
        tier = "EXPENSIVE (forced — 5K precision)"
    elif state.model_tier == "cheap":
        cycle_models = CHEAP_MODELS
        tier = "CHEAP (forced — mechanical)"
    else:
        cycle_models = EXPENSIVE_MODELS if state.cycle <= ALTITUDE_CUTOFF else CHEAP_MODELS
        tier = "EXPENSIVE (5K precision)" if state.cycle <= ALTITUDE_CUTOFF else "CHEAP (50K mechanical)"

    print(f"\n{'='*60}")
    print(f"  CYCLE {state.cycle} | M={state.m_size} constants | I={state.i_size} variables")
    print(f"  Domain: {state.domain}")
    print(f"  P=1: {state.p1_definition[:60]}")
    print(f"  Models: {tier}")
    print(f"{'='*60}")

    prompt = build_prompt(state)

    # Save prompt
    prompt_path = state.run_dir / f"cycle-{state.cycle:02d}-prompt.txt"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding='utf-8')

    # Run 3 models (selected by altitude)
    outputs = []
    for model in cycle_models:
        model_short = model.split("/")[-1]
        print(f"\n  Running {model_short}...")

        try:
            # Expanded vocabulary schema produces large JSON outputs — 32k tokens
            # prevents truncation when many candidates are being evaluated.
            # response_schema enforces the 7-field KEY structure at the API boundary;
            # models that can't honor it fail loud instead of drifting.
            result = call_openrouter(model, prompt, max_tokens=32000,
                                     response_schema=CANDIDATE_OUTPUT_SCHEMA)
        except Exception as e:
            print(f"    ERROR: {e}")
            state.errors.append(f"cycle {state.cycle} {model_short}: {e}")
            continue

        state.spend_log.append({
            "cycle": state.cycle, "model": model,
            "tokens_in": result["tokens_in"], "tokens_out": result["tokens_out"],
            "cost": result["cost"], "timestamp": now_utc(),
        })
        print(f"    tokens: {result['tokens_in']}→{result['tokens_out']} | cost: ${result['cost']:.4f}" if result['cost'] else f"    tokens: {result['tokens_in']}→{result['tokens_out']}")

        # Save raw
        raw_path = state.run_dir / f"cycle-{state.cycle:02d}-{model_short}-raw.txt"
        raw_content = result["content"] or ""
        raw_path.write_text(raw_content, encoding='utf-8')

        if not raw_content:
            print(f"    [WARN] Empty response from {model_short} — skipping")
            continue

        # Parse JSON
        json_str = extract_json_from_text(raw_content)
        if json_str:
            parsed = json.loads(json_str)
            parsed["_model"] = model_short
            write_json(state.run_dir / f"cycle-{state.cycle:02d}-{model_short}.json", parsed)
            outputs.append(parsed)
            print(f"    candidates: {len(parsed.get('candidates_evaluated', parsed.get('candidates', [])))}")
        else:
            print(f"    ERROR: no valid JSON")
            state.errors.append(f"cycle {state.cycle} {model_short}: no JSON")

    if not outputs:
        print(f"\n  ALL MODELS FAILED — cycle {state.cycle}")
        return None

    # Consolidate
    print(f"\n  CONSOLIDATING {len(outputs)} outputs...")
    if len(outputs) == 1:
        consolidated = outputs[0]
        consolidated["consolidation_method"] = "single model"
    else:
        cons_prompt = build_consolidation_prompt(outputs, state)
        try:
            # Consolidation merges outputs from 3 models → must hold full JSON
            cons_result = call_openrouter(state.models[0], cons_prompt, max_tokens=32000)
            state.spend_log.append({
                "cycle": state.cycle, "model": state.models[0],
                "phase": "consolidation",
                "tokens_in": cons_result["tokens_in"],
                "tokens_out": cons_result["tokens_out"],
                "cost": cons_result["cost"], "timestamp": now_utc(),
            })
            json_str = extract_json_from_text(cons_result["content"])
            if json_str:
                consolidated = json.loads(json_str)
            else:
                print(f"    Consolidation failed — using first model output")
                consolidated = outputs[0]
        except Exception as e:
            print(f"    Consolidation error: {e} — using first model output")
            consolidated = outputs[0]

    write_json(state.run_dir / f"cycle-{state.cycle:02d}-consolidated.json", consolidated)

    # ── DETERMINISTIC PHASE: equation + back-propagation + algebra ──
    # The LLM was the parser. Now the math takes over.
    # Discovery mode (cycles 1-3): no equation — lock based on tier0 + consensus
    # Measurement mode (cycles 4+): full equation with c_value/k_tolerance

    is_discovery = state.cycle <= 3
    # NONE-VALIDATION GUARD (2026-04-18): consolidation can return None fields
    # when the LLM output is malformed. None was previously treated as [],
    # causing false P=1 when all fields came back None. Reject None as a
    # consolidation failure — return the cycle without modifying state so the
    # engine retries next cycle instead of celebrating victory.
    raw_new_locked = consolidated.get("new_locked")
    raw_remaining = consolidated.get("remaining_variables")
    raw_domesticated = consolidated.get("domesticated")
    raw_candidates = consolidated.get("candidates", consolidated.get("candidates_evaluated"))
    if raw_new_locked is None or raw_remaining is None or raw_candidates is None:
        print(f"\n  ✗ CONSOLIDATION FAIL — cycle {state.cycle} returned None fields "
              f"(new_locked={raw_new_locked!r}, remaining={raw_remaining!r}, candidates={type(raw_candidates).__name__})")
        print(f"    NOT treating as convergence. Cycle discarded. Engine continues.")
        write_json(
            state.run_dir / f"cycle-{state.cycle:02d}-consolidation-failure.json",
            {"cycle": state.cycle, "raw_consolidated": consolidated,
             "reason": "None-valued fields — malformed LLM output"},
        )
        return consolidated  # return without state mutation — next cycle retries
    new_locked = raw_new_locked
    remaining = raw_remaining
    domesticated = raw_domesticated or []
    candidates = raw_candidates

    if is_discovery:
        # DISCOVERY MODE: no numeric equation — lock based on structural tests
        print(f"\n  STRUCTURAL CHECK — evaluating {len(candidates)} candidates (discovery mode)")
        evaluated = []
        for c in candidates:
            tier0 = c.get("tier0_check", {})
            # LLM returns "pass — <reason>" per prompt schema — match by prefix, not equality
            passed = all(
                (v or "").strip().lower().startswith("pass")
                for v in tier0.values()
            ) if tier0 else False
            inversion = c.get("inversion_test", "")
            holds = c.get("holds_across_implementations", False)
            # In discovery mode: lock if tier0 passes AND it holds across implementations
            is_locked = passed and holds
            evaluated.append({
                **c,
                "p": 1 if is_locked else 0,
                "ratio": 0.0 if is_locked else 1.5,  # synthetic ratio for compatibility
                "c_value": 1 if is_locked else 0,
                "k_tolerance": 1,
            })
            status = "✓ STRUCTURAL" if is_locked else "? NEEDS WORK"
            prim = c.get('primitive') or '?'
            cname = c.get('name') or '?'
            print(f"    {status} [{prim:6s}] {cname}")
            if inversion:
                print(f"             breaks if removed: {str(inversion)[:80]}")
        write_json(state.run_dir / f"cycle-{state.cycle:02d}-equation.json", evaluated)
    else:
        # MEASUREMENT MODE: full equation with numeric values
        print(f"\n  EQUATION — computing r(x) for {len(candidates)} candidates")
        evaluated = compute_diagnostic_vector(candidates)
        write_json(state.run_dir / f"cycle-{state.cycle:02d}-equation.json", evaluated)

    for e in evaluated:
        if e.get("ratio") is not None:
            status = "✓" if e["p"] == 1 else "✗"
            print(f"    {status} {e.get('name', '?'):30s} r={e['ratio']:.4f} "
                  f"(C={e.get('c_value','?')} / k={e.get('k_tolerance','?')})")

    # 2. LOCK constants that passed (P=1) — move to M
    for name in new_locked:
        candidate = next((c for c in evaluated if c.get("name") == name), None)
        if not candidate:
            candidate = next((c for c in candidates if c.get("name") == name), None)
        new_const = {
            "name": name,
            "primitive": candidate.get("primitive", "?") if candidate else "?",
            "comparator": candidate.get("comparator", "") if candidate else "",
            "c_value": candidate.get("c_value") if candidate else None,
            "k_tolerance": candidate.get("k_tolerance") if candidate else None,
            "ratio": candidate.get("ratio") if candidate else None,
            "why": candidate.get("why", "") if candidate else "",
            "locked_cycle": state.cycle,
            "confidence": candidate.get("confidence", "locked") if candidate else "locked",
            "influenced_by": candidate.get("influenced_by", []) if candidate else [],
            "influences": candidate.get("influences", []) if candidate else [],
            "coupled_to": candidate.get("influenced_by", []) if candidate else [],
            "vocabulary": candidate.get("vocabulary", {}) if candidate else {},
        }

        # STRUCTURAL GATE — 7-column output required. Verifies the STRUCTURE is
        # present (all 5 vocab fields non-empty). Does NOT verify the content
        # (whether description matches primitive) — that's Process 2 (K=C Audit).
        # Structure is the constant. Content is the variable. US locks structure.
        vocab = new_const.get("vocabulary") or {}
        required_vocab_fields = ["abbreviation", "description", "behavior", "context", "example"]
        missing_vocab = [f for f in required_vocab_fields if not (vocab.get(f) or "").strip()]
        if missing_vocab:
            print(f"    ✗ STRUCTURAL GATE — {name}: missing vocab fields {missing_vocab} — not locked")
            state.variables.append({
                "name": name, "primitive": new_const.get("primitive", "?"),
                "status": f"missing_vocab_fields: {missing_vocab}",
            })
            continue
        print(f"    ✓ structural gate — 7 columns present")

        # BACK-PROPAGATE — deterministic check against all prior constants
        print(f"\n  BACK-PROP — checking {name} against {len(state.locked_constants)} priors")
        broken = back_propagate(new_const, state.locked_constants)

        if broken:
            print(f"    ⚠ {name} broke {len(broken)} prior constants: {broken}")
            for broken_name in broken:
                state.locked_constants = [c for c in state.locked_constants if c["name"] != broken_name]
                state.variables.append({
                    "name": broken_name, "primitive": "?",
                    "status": f"back-prop broke by {name}",
                })
        else:
            print(f"    ✓ clean — no prior constants broken")

        state.locked_constants.append(new_const)

    # 4. ALGEBRAIC SOLVING — for each remaining variable, compute what it needs to be
    print(f"\n  ALGEBRA — solving for {len(remaining)} variables")
    # US Process 1 — no vocab gate, nothing to preserve. Reset to the cycle's `remaining` list.
    state.variables = []
    for name in remaining:
        candidate = next((c for c in evaluated if c.get("name") == name), None)
        if not candidate:
            candidate = next((c for c in candidates if c.get("name") == name), None)

        if candidate:
            solved = solve_for_variable(candidate, state.locked_constants, state.p1_definition)
            state.variables.append({
                "name": name,
                "primitive": solved.get("primitive", "?"),
                "status": "needs decomposition",
                "current_value": solved.get("current_value"),
                "required_value": solved.get("required_value"),
                "gap": solved.get("gap"),
                "pct_change_needed": solved.get("pct_change_needed"),
                "influenced_by": solved.get("influenced_by", []),
                "influences": solved.get("influences", []),
            })
            if solved.get("gap") is not None:
                print(f"    {name}: current={solved.get('current_value')} "
                      f"required={solved.get('required_value')} "
                      f"gap={solved.get('gap')} ({solved.get('pct_change_needed', 0)}% change needed)")
        else:
            state.variables.append({
                "name": name, "primitive": "?", "status": "needs decomposition",
            })

    # 5. SIGMA TRACKING — deterministic comparison across cycles
    sigma_direction = track_sigma(state, evaluated)

    # Print sigma detail
    sigma_icon = {"tightening": "↘ TIGHTENING", "flat": "→ FLAT", "expanding": "↗ EXPANDING",
                  "insufficient_data": "… BASELINE", "no_overlap": "? NO OVERLAP"}.get(sigma_direction, sigma_direction)
    print(f"\n  SIGMA: {sigma_icon}  "
          f"(stuck_cycles={state.stuck_cycle_count}, rotation_count={state.rotation_count})")

    # Show delta details if available (last sigma log entry)
    if state.sigma_log:
        last_log = state.sigma_log[-1]
        deltas = last_log.get("delta_details", [])
        if deltas:
            # Show the 3 biggest movers
            biggest = sorted(deltas, key=lambda x: abs(x.get("delta", 0)), reverse=True)[:3]
            for d in biggest:
                print(f"    Δ {d['name']}: {d['delta']:+.4f} ({d['direction']})")

    # 6. EQUATION ROTATION — if stuck, relax tolerances for next cycle
    if check_rotation_needed(state):
        state.rotation_count += 1
        state.rotation_active = True
        state.stuck_cycle_count = 0  # Reset counter after rotation
        old_k_values = {c["name"]: c.get("k_tolerance") for c in state.locked_constants if c.get("k_tolerance") is not None}
        state.locked_constants = rotate_tolerances(state.locked_constants, state.rotation_multiplier)
        print(f"\n  EQUATION ROTATION #{state.rotation_count} — sigma stuck, relaxing tolerances "
              f"({state.rotation_multiplier:.0%} expansion)")
        for c in state.locked_constants:
            if c.get("_rotated") and c["name"] in old_k_values:
                print(f"    {c['name']}: k={old_k_values[c['name']]} → {c['k_tolerance']}")
        write_json(state.run_dir / f"cycle-{state.cycle:02d}-rotation.json", {
            "rotation_number": state.rotation_count,
            "multiplier": state.rotation_multiplier,
            "rotated_at_cycle": state.cycle,
            "constants_rotated": [
                {"name": c["name"], "old_k": old_k_values.get(c["name"]), "new_k": c.get("k_tolerance")}
                for c in state.locked_constants if c.get("_rotated") and c["name"] in old_k_values
            ],
        })
    elif state.rotation_active and sigma_direction == "tightening":
        # Sigma tightening again — rotation worked or natural progress resumed
        state.rotation_active = False
        print(f"  ROTATION CLEARED — sigma tightening again")

    # Save sigma log every cycle
    write_json(state.run_dir / "sigma-log.json", state.sigma_log)

    # ── PASS-LEVEL AUDIT — whole-cycle coherence check ──
    # Per the US Code Desk doctrine: the pass cannot advance if any rule of
    # coherence is violated. This is the stage-level audit (different scope
    # than the per-row vocab gate). Failures get pushed back to I so the
    # engine retries next cycle. Strike 3 → Troubleshoot/Train.
    pass_audit_violations = pass_level_audit(state)
    if pass_audit_violations:
        print(f"\n  ✗ PASS AUDIT FAIL — {len(pass_audit_violations)} coherence violation(s)")
        for v in pass_audit_violations:
            print(f"    - [{v['type']}] {v['name']}: {v['reason']}")
        write_json(
            state.run_dir / f"cycle-{state.cycle:02d}-pass-audit-failures.json",
            pass_audit_violations,
        )
        # Kick violating constants back to I — loop will retry next cycle
        bad_names = {v["name"] for v in pass_audit_violations}
        state.locked_constants = [c for c in state.locked_constants if c["name"] not in bad_names]
        for v in pass_audit_violations:
            state.variables.append({
                "name": v["name"],
                "primitive": v.get("primitive", "?"),
                "status": f"pass_audit_fail: {v['type']}",
            })
    else:
        print(f"\n  ✓ PASS AUDIT CERTIFIED — cycle coherent")

    # Print cycle summary
    sigma = consolidated.get("sigma", "?")
    print(f"\n  CYCLE {state.cycle} COMPLETE")
    print(f"    Locked (M):  {state.m_size} constants")
    print(f"    Variables (I): {state.i_size} remaining")
    print(f"    Domesticated:  {len(domesticated)}")
    print(f"    Sigma:         {sigma_direction} (engine) / {sigma} (LLM)")
    print(f"    Rotation:      #{state.rotation_count} active={state.rotation_active}")
    print(f"    P status:      {'P=1 ✓' if state.i_size == 0 else 'P=0 — variables remain'}")

    # ── PERSIST: D1 + R2 ──
    cycle_cost = sum(s.get("cost", 0) for s in state.spend_log
                     if s.get("cycle") == state.cycle and isinstance(s.get("cost"), (int, float)))
    cycle_tokens_in = sum(s.get("tokens_in", 0) for s in state.spend_log if s.get("cycle") == state.cycle)
    cycle_tokens_out = sum(s.get("tokens_out", 0) for s in state.spend_log if s.get("cycle") == state.cycle)

    if d1_write_cycle(state, consolidated, ",".join(m.split("/")[-1] for m in state.models),
                      cycle_tokens_in, cycle_tokens_out, cycle_cost):
        print(f"    D1: cycle {state.cycle} logged")
    else:
        print(f"    D1: cycle write failed")

    if d1_write_run(state):
        print(f"    D1: run updated")

    r2_key = f"dyno-runs/{slugify(state.domain)}/{state.run_id}/cycle-{state.cycle:02d}-consolidated.json"
    if r2_push_artifact(r2_key, json.dumps(consolidated, indent=2, default=str)):
        print(f"    R2: {r2_key}")
    else:
        print(f"    R2: push failed")

    return consolidated


def run_preflight(constraints: list[dict], domain: str, output_dir: Path,
                   model: str = "anthropic/claude-opus-4-6") -> list[dict]:
    """Pre-flight comprehension check: send M to one model, have it echo back
    its understanding of each constant. Human reviews and corrects before the
    real run starts.

    Returns the corrected constraints list (with updated descriptions).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build the preflight prompt
    constraint_block = ""
    for i, c in enumerate(constraints):
        desc = c.get("description", "")
        desc_line = f"\n   Description provided: {desc}" if desc else "\n   No description provided."
        constraint_block += f"\n{i+1}. {c['name']}{desc_line}\n"

    prompt = f"""You are a pre-flight auditor for the Dyno Engine. Before the gap analysis runs,
you must verify that you UNDERSTAND what the human's constraints actually mean.

DOMAIN: {domain}

The human has declared these as their locked constants (M). For EACH one, write back:
1. YOUR UNDERSTANDING — what you think this constant is, in your own words (2-3 sentences)
2. CONFIDENCE — HIGH (you're sure you understand), MEDIUM (you have a reasonable guess), LOW (you're guessing from context)
3. QUESTIONS — anything you'd want to clarify before using this in a gap analysis

Be honest. If something is an acronym or proprietary term you're not sure about, say so.
Don't pretend to understand something you don't.

CONSTANTS TO AUDIT:
{constraint_block}

Output valid JSON:
{{
  "preflight_results": [
    {{
      "name": "<constant name>",
      "my_understanding": "<what you think this means>",
      "confidence": "HIGH|MEDIUM|LOW",
      "questions": ["<any clarifying questions>"],
      "description_adequate": true|false
    }}
  ],
  "total_high": <count>,
  "total_medium": <count>,
  "total_low": <count>,
  "ready_for_gap_analysis": true|false,
  "blocking_issues": ["<any constants that MUST be clarified before proceeding>"]
}}"""

    print(f"\n{'='*60}")
    print(f"  PREFLIGHT — Comprehension Check")
    print(f"  Model: {model.split('/')[-1]}")
    print(f"  Constants: {len(constraints)}")
    print(f"  Domain: {domain[:60]}")
    print(f"{'='*60}")

    # Call the model
    result = call_openrouter(model, prompt, max_tokens=16000, temperature=0.2)
    raw_content = result.get("content", "")

    # Save raw output
    (output_dir / "preflight-raw.txt").write_text(raw_content, encoding='utf-8')

    # Parse
    json_text = extract_json_from_text(raw_content)
    if not json_text:
        print(f"  ERROR: Could not parse preflight response as JSON")
        print(f"  Raw saved to: {output_dir}/preflight-raw.txt")
        return constraints

    preflight = json.loads(json_text)
    write_json(output_dir / "preflight-audit.json", preflight)

    # Display results
    results = preflight.get("preflight_results", [])
    low_confidence = []
    medium_confidence = []

    for r in results:
        conf = r.get("confidence", "LOW")
        name = r.get("name", "?")
        understanding = r.get("my_understanding", "")
        questions = r.get("questions", [])

        if conf == "LOW":
            low_confidence.append(r)
            marker = "❌ LOW"
        elif conf == "MEDIUM":
            medium_confidence.append(r)
            marker = "⚠️  MEDIUM"
        else:
            marker = "✓ HIGH"

        print(f"\n  {marker}: {name}")
        print(f"    Understanding: {understanding[:120]}")
        if questions:
            for q in questions:
                print(f"    ❓ {q}")

    print(f"\n  {'='*60}")
    print(f"  PREFLIGHT SUMMARY")
    print(f"    HIGH confidence:   {preflight.get('total_high', 0)}")
    print(f"    MEDIUM confidence: {preflight.get('total_medium', 0)}")
    print(f"    LOW confidence:    {preflight.get('total_low', 0)}")
    print(f"    Ready: {preflight.get('ready_for_gap_analysis', False)}")

    blocking = preflight.get("blocking_issues", [])
    if blocking:
        print(f"\n  BLOCKING ISSUES:")
        for b in blocking:
            print(f"    🛑 {b}")

    # Interactive correction for LOW and MEDIUM confidence
    needs_correction = low_confidence + medium_confidence
    if needs_correction:
        print(f"\n  {len(needs_correction)} constant(s) need clarification.")
        print(f"  For each, provide a better description or 'ok' to accept the model's understanding.")
        print(f"  Type 'skip' to proceed without corrections.\n")

        for r in needs_correction:
            name = r.get("name", "?")
            understanding = r.get("my_understanding", "")
            print(f"  [{r.get('confidence')}] {name}")
            print(f"    Model thinks: {understanding}")
            try:
                correction = input(f"    Your correction (or 'ok'/'skip'): ").strip()
                if correction.lower() == "skip":
                    print(f"    Skipping remaining corrections")
                    break
                elif correction.lower() != "ok" and correction:
                    # Update the constraint's description
                    for c in constraints:
                        if c["name"] == name:
                            c["description"] = correction
                            print(f"    ✓ Updated: {correction[:80]}...")
                            break
                else:
                    # Accept model's understanding as the description if none exists
                    for c in constraints:
                        if c["name"] == name and not c.get("description", "").strip():
                            c["description"] = understanding
                            print(f"    ✓ Accepted model's understanding as description")
                            break
            except (EOFError, KeyboardInterrupt):
                print(f"\n  Correction interrupted — proceeding with current descriptions")
                break

    # Save corrected constraints
    write_json(output_dir / "constraints-post-preflight.json", constraints)
    print(f"\n  Corrected constraints saved to: {output_dir}/constraints-post-preflight.json")
    print(f"  Cost: ${result.get('cost', 0):.4f}")

    return constraints


def run_engine(state: EngineState) -> None:
    """The main loop: I = M + O until I=0 or max cycles."""
    print(f"\n{'='*60}")
    print(f"  DYNO ENGINE — I = M + O")
    print(f"  Domain: {state.domain}")
    print(f"  P=1: {state.p1_definition[:60]}")
    print(f"  Models: {', '.join(m.split('/')[-1] for m in state.models)}")
    print(f"  Max cycles: {state.max_cycles}")
    print(f"{'='*60}")

    state.run_dir.mkdir(parents=True, exist_ok=True)

    # D1 AWARENESS — load live data context before the run starts
    # Best-effort: if D1 is unreachable, we continue without it
    print(f"\n  D1 AWARENESS — loading data context...")
    state.d1_context = d1_get_context(domain=state.domain)
    if state.d1_context.get("available"):
        tables = state.d1_context.get("tables", [])
        total = state.d1_context.get("total_tables", 0)
        print(f"    D1 online: {total} tables, top tables: "
              f"{', '.join(t['name'] + '(' + str(t['row_count']) + ')' for t in tables[:3])}")
        prior_runs = state.d1_context.get("dyno_prior_runs", [])
        if prior_runs:
            print(f"    Prior runs on similar domains: {len(prior_runs)}")
        write_json(state.run_dir / "d1-context.json", state.d1_context)
    else:
        print(f"    D1 offline or unreachable — proceeding without data context")

    # Save initial state
    write_json(state.run_dir / "engine-start.json", {
        "run_id": state.run_id,
        "domain": state.domain,
        "p1_definition": state.p1_definition,
        "initial_constants": state.locked_constants,
        "initial_variables": state.variables,
        "models": state.models,
        "max_cycles": state.max_cycles,
        "started_at": now_utc(),
    })

    # CONSTRAINT VALIDATION GATE — stop and ask if any constraint lacks a description
    # A constraint without a description is an acronym the models will guess at.
    # Better to stop and ask the human than to let 3 models hallucinate meaning.
    undescribed = [c for c in state.locked_constants
                   if c.get("confidence") == "human" and not c.get("description", "").strip()]
    if undescribed:
        print(f"\n  {'='*60}")
        print(f"  CONSTRAINT GATE — {len(undescribed)} constraint(s) missing descriptions")
        print(f"  The models need to understand what these mean, not just the name.")
        print(f"  {'='*60}")
        for i, c in enumerate(undescribed):
            print(f"\n  [{i+1}] {c['name']}")
            print(f"      What is this? (enter description, or 'skip' to proceed without):")
            try:
                desc = input(f"      > ").strip()
                if desc and desc.lower() != "skip":
                    c["description"] = desc
                    print(f"      ✓ Locked: {desc[:80]}...")
                else:
                    print(f"      ⚠ Skipped — models will infer meaning from context")
            except (EOFError, KeyboardInterrupt):
                print(f"\n  Gate interrupted — proceeding with {len(undescribed)} undescribed constraints")
                break
        # Re-save engine-start with updated descriptions
        write_json(state.run_dir / "engine-start.json", {
            "run_id": state.run_id,
            "domain": state.domain,
            "p1_definition": state.p1_definition,
            "initial_constants": state.locked_constants,
            "initial_variables": state.variables,
            "models": state.models,
            "max_cycles": state.max_cycles,
            "started_at": now_utc(),
        })

    # THE LOOP — runs until P=1. Cycle count is the variable, not a target.
    # max_cycles is a runaway-loop safety stop only; if hit, log as convergence
    # failure (not "done") so the human can investigate.
    while state.cycle < state.max_cycles:
        result = run_cycle(state)

        if result is None:
            print(f"\n  ENGINE STOPPED — cycle failed")
            break

        if state.is_done:
            print(f"\n  {'='*60}")
            print(f"  PROCESS 1 (US) COMPLETE — P=1 — I=0")
            print(f"  M contains {state.m_size} locked constants")
            print(f"  US converged in {state.cycle} cycles")
            print(f"  {'='*60}")
            print(f"\n  K=C (Process 2) is a SEPARATE run. Does not auto-fire.")
            print(f"  To run Process 2 on this M: (invoke separately when ready)")
            break

        # Human gate between cycles
        print(f"\n  HUMAN GATE — Review cycle {state.cycle}")
        print(f"    Continue to cycle {state.cycle + 1}? (engine will auto-continue)")
        print(f"    Ctrl+C to stop and review")

    # Loop exit — distinguish P=1 completion from safety-stop halt
    if not state.is_done:
        print(f"\n  {'='*60}")
        print(f"  SAFETY HALT — loop exited without reaching P=1")
        print(f"  Cycle {state.cycle} of max {state.max_cycles}. Sigma did not converge.")
        print(f"  This is NOT 'done'. P=0. Human must investigate convergence failure.")
        print(f"  {'='*60}")

    # Save final state
    total_cost = sum(s.get("cost", 0) for s in state.spend_log
                     if isinstance(s.get("cost"), (int, float)))

    write_json(state.run_dir / "engine-final.json", {
        "run_id": state.run_id,
        "domain": state.domain,
        "p1_definition": state.p1_definition,
        "final_constants": state.locked_constants,
        "final_variables": state.variables,
        "total_cycles": state.cycle,
        "p_status": "P=1" if state.is_done else "P=0",
        "m_size": state.m_size,
        "i_size": state.i_size,
        "total_cost": total_cost,
        "errors": state.errors,
        "completed_at": now_utc(),
        # Sigma log — full per-cycle history
        "sigma_log": state.sigma_log,
        "sigma_final_direction": state.sigma_log[-1]["direction"] if state.sigma_log else "no_data",
        # Equation rotation summary
        "rotation_count": state.rotation_count,
        "rotation_multiplier": state.rotation_multiplier,
        "rotation_active_at_end": state.rotation_active,
    })

    write_json(state.run_dir / "spend.json", state.spend_log)

    # Final D1 + R2 persist
    d1_write_run(state)
    r2_push_artifact(
        f"dyno-runs/{slugify(state.domain)}/{state.run_id}/engine-final.json",
        json.dumps({
            "run_id": state.run_id, "domain": state.domain,
            "p1_definition": state.p1_definition,
            "final_constants": [c["name"] for c in state.locked_constants],
            "final_variables": [v["name"] for v in state.variables],
            "total_cycles": state.cycle,
            "p_status": "P=1" if state.is_done else "P=0",
            "m_size": state.m_size, "i_size": state.i_size,
            "total_cost": total_cost,
        }, indent=2, default=str),
    )

    # LBB ingest
    lbb_key = get_api_key("LBB_API_KEY")
    if lbb_key:
        try:
            payload = json.dumps({
                "record_id": str(uuid.uuid4()),
                "sovereign_ref": "imo-creator",
                "hub_id": "lbb",
                "cc_layer": "CC-03",
                "subject_id": "processes",
                "ctb_placement": "leaf",
                "title": f"Dyno: {state.domain[:40]} — {state.m_size} constants, {'P=1' if state.is_done else 'P=0'}, {state.cycle} cycles, ${total_cost:.2f}",
                "content": json.dumps({
                    "domain": state.domain,
                    "p1": state.p1_definition,
                    "constants": [c["name"] for c in state.locked_constants],
                    "remaining": [v["name"] for v in state.variables],
                    "cycles": state.cycle,
                    "cost": total_cost,
                }),
                "content_format": "text",  # LBB CHECK constraint: text|markdown|html|transcript
                "source_type": "document",
                "source_name": "dyno-engine",
                "fetched_by": "api",
                "orbt_mode": "BUILD",
                "tags": json.dumps(["dyno", "engine", slugify(state.domain)]),
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{LBB_URL}/ingest", data=payload,
                headers={"Authorization": f"Bearer {lbb_key}", "Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=15)
            print(f"\n  LBB: run logged")
        except Exception as e:
            print(f"\n  LBB ingest failed: {e}")

    print(f"\n  Total cost: ${total_cost:.4f}")
    print(f"  Run dir: {state.run_dir}")


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(description="Dyno Engine — I = M + O")
    sub = parser.add_subparsers(dest="command", required=True)

    # ── DISCOVER (us.py = M) ──
    # I = domain (human provides). O = all leaves at primitive (CONSTANT).
    # Solve for M. ONE argument: the domain name.
    p_discover = sub.add_parser("discover", help="US phase — discover M (structure to primitive)")
    p_discover.add_argument("domain", help="The domain — the ONLY input")
    p_discover.add_argument("--constraints-file", help="JSON file with enriched constraints [{name, description}, ...]", default=None)
    p_discover.add_argument("--max-cycles", type=int, default=10000,
                            help="Runaway-loop safety stop — NOT a target. Engine runs until P=1. "
                                 "The number of cycles is the VARIABLE. Leave unset for normal operation.")
    p_discover.add_argument("--output-dir", help="Run directory", default=None)

    # ── SOLVE (up.py = I) ──
    # M = from US (locked). O = tolerance from human. Consume I until I=0.
    p_solve = sub.add_parser("solve", help="UP phase — consume I through M to reach O")
    p_solve.add_argument("problem", help="What you're trying to do (I)")
    p_solve.add_argument("tolerance", help="P=1 definition — what solved looks like (O)")
    p_solve.add_argument("--m", required=True, help="Path to US output (M) — locked, cannot change")
    p_solve.add_argument("--max-cycles", type=int, default=10000,
                         help="Runaway-loop safety stop — NOT a target. Engine runs until P=1.")
    p_solve.add_argument("--output-dir", help="Run directory", default=None)

    # ── RUN (legacy — both phases, for backwards compatibility) ──
    p_run = sub.add_parser("run", help="Legacy — runs both phases")
    p_run.add_argument("domain", help="The domain")
    p_run.add_argument("p1", help="P=1 definition")
    p_run.add_argument("--constraints", help="Known constants to pre-load into M (semicolon-separated names)", default="")
    p_run.add_argument("--constraints-file", help="JSON file with enriched constraints [{name, description}, ...]", default=None)
    p_run.add_argument("--models", choices=["expensive", "cheap", "auto"], default="auto",
                        help="Model tier: expensive (Opus/Gemini Pro/GPT-5.4), cheap (Flash/Haiku/Llama), auto (altitude-based)")
    p_run.add_argument("--max-cycles", type=int, default=10000,
                       help="Runaway-loop safety stop — NOT a target. Engine runs until P=1.")
    p_run.add_argument("--output-dir", help="Run directory", default=None)

    # ── PREFLIGHT ──
    # Comprehension check: send M to one model, have it echo back its understanding.
    # Human reviews and corrects BEFORE the gap analysis runs.
    p_pre = sub.add_parser("preflight", help="Pre-flight comprehension check on constraints")
    p_pre.add_argument("domain", help="The domain context")
    p_pre.add_argument("--constraints-file", required=True, help="JSON file with constraints [{name, description}, ...]")
    p_pre.add_argument("--model", default="anthropic/claude-opus-4-6",
                       help="Model to use for comprehension check (default: Opus)")
    p_pre.add_argument("--output-dir", help="Where to save preflight results", default=None)

    # ── STATUS ──
    p_status = sub.add_parser("status", help="Check run status")
    p_status.add_argument("run_dir", help="Path to run directory")

    args = parser.parse_args()
    models = list(DEFAULT_MODELS)  # Locked — 3 models, constant, not overridable

    if args.command == "discover":
        # us.py = M. I and O are already set. Solve for M.
        # O is HARDCODED: all leaves at primitive (Thing/Flow/Change/Connection)
        output_dir = Path(args.output_dir) if args.output_dir else (
            RUNS_DIR / f"discover-{slugify(args.domain)}"
        )
        initial_constants = []
        if args.constraints_file:
            cf_path = Path(args.constraints_file)
            cf_data = load_json(cf_path)
            if cf_data and isinstance(cf_data, list):
                for c in cf_data:
                    initial_constants.append({
                        "name": c.get("name", "?"),
                        "description": c.get("description", ""),
                        "primitive": c.get("primitive", "?"),
                        "comparator": c.get("comparator", ""),
                        "tolerance": c.get("tolerance", ""),
                        "why": c.get("why", "human-declared constraint"),
                        "locked_cycle": 0,
                        "confidence": "human",
                    })
                print(f"  Loaded {len(initial_constants)} enriched constraints from {cf_path}")
        state = EngineState(
            p1_definition="All leaves at primitive (Thing/Flow/Change/Connection). Structure fully decomposed. Every branch terminates at exactly one primitive.",
            locked_constants=initial_constants,
            domain=args.domain,
            run_dir=output_dir,
            models=models,
            max_cycles=args.max_cycles,
        )
        run_engine(state)
        return 0 if state.is_done else 1

    elif args.command == "solve":
        # up.py = I. M and O are already set. Consume I until I=0.
        output_dir = Path(args.output_dir) if args.output_dir else (
            RUNS_DIR / f"solve-{slugify(args.problem)}"
        )
        # Load M from US output
        m_path = Path(args.m)
        m_data = load_json(m_path / "engine-final.json") if m_path.is_dir() else load_json(m_path)
        if not m_data:
            print(f"ERROR: Cannot load M from {args.m}")
            print(f"  US must finish before UP starts. No M = nothing to solve with.")
            return 1

        # M is locked — load all constants from US
        initial_constants = m_data.get("final_constants", [])
        if not initial_constants:
            print(f"ERROR: M is empty — US found no constants")
            print(f"  Run 'discover' first to build M.")
            return 1

        state = EngineState(
            p1_definition=args.tolerance,
            locked_constants=initial_constants,
            domain=args.problem,
            run_dir=output_dir,
            models=models,
            max_cycles=args.max_cycles,
        )
        run_engine(state)
        return 0 if state.is_done else 1

    elif args.command == "run":
        # Legacy mode — backwards compatible
        output_dir = Path(args.output_dir) if args.output_dir else (
            RUNS_DIR / f"engine-{slugify(args.domain)}"
        )
        initial_constants = []
        if args.constraints_file:
            cf_path = Path(args.constraints_file)
            cf_data = load_json(cf_path)
            if cf_data and isinstance(cf_data, list):
                for c in cf_data:
                    initial_constants.append({
                        "name": c.get("name", "?"),
                        "description": c.get("description", ""),
                        "primitive": c.get("primitive", "?"),
                        "comparator": c.get("comparator", ""),
                        "tolerance": c.get("tolerance", ""),
                        "why": c.get("why", "human-declared constraint"),
                        "locked_cycle": 0,
                        "confidence": "human",
                    })
                print(f"  Loaded {len(initial_constants)} enriched constraints from {cf_path}")
            else:
                print(f"  WARNING: Could not load constraints from {cf_path}")
        elif args.constraints:
            for i, c in enumerate(args.constraints.split(";")):
                c = c.strip()
                if c:
                    initial_constants.append({
                        "name": c,
                        "primitive": "?",
                        "comparator": "",
                        "tolerance": "",
                        "why": "human-declared constraint",
                        "locked_cycle": 0,
                        "confidence": "human",
                    })
        model_tier = getattr(args, 'models', 'auto') or 'auto'
        state = EngineState(
            p1_definition=args.p1,
            locked_constants=initial_constants,
            domain=args.domain,
            run_dir=output_dir,
            models=models,
            model_tier=model_tier,
            max_cycles=args.max_cycles,
        )
        run_engine(state)
        return 0 if state.is_done else 1

    elif args.command == "preflight":
        cf_path = Path(args.constraints_file)
        cf_data = load_json(cf_path)
        if not cf_data or not isinstance(cf_data, list):
            print(f"  ERROR: Cannot load constraints from {cf_path}")
            return 1
        output_dir = Path(args.output_dir) if args.output_dir else (
            RUNS_DIR / f"preflight-{slugify(args.domain)}"
        )
        corrected = run_preflight(cf_data, args.domain, output_dir, model=args.model)
        write_json(output_dir / "constraints-corrected.json", corrected)
        print(f"\n  Corrected constraints ready at: {output_dir}/constraints-corrected.json")
        print(f"  Use this file with: dyno_engine.py run ... --constraints-file {output_dir}/constraints-corrected.json")
        return 0

    elif args.command == "status":
        final = load_json(Path(args.run_dir) / "engine-final.json")
        if not final:
            start = load_json(Path(args.run_dir) / "engine-start.json")
            if start:
                print(f"  Engine running: {start.get('domain', '?')}")
            else:
                print(f"  No engine found at {args.run_dir}")
            return 1
        print(f"  Domain:    {final.get('domain', '?')}")
        print(f"  P=1:       {final.get('p1_definition', '?')[:60]}")
        print(f"  Status:    {final.get('p_status', '?')}")
        print(f"  Constants: {final.get('m_size', 0)}")
        print(f"  Variables: {final.get('i_size', 0)}")
        print(f"  Cycles:    {final.get('total_cycles', 0)}")
        print(f"  Cost:      ${final.get('total_cost', 0):.4f}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

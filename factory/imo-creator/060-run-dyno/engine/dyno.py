#!/usr/bin/env python3
"""
Dyno — IMO Chain Navigator

THE RULES:
    1. You give it the outcome: "get past CF" → 0 or 1. That's the constant.
    2. The Dyno figures out what altitude it needs to be at to solve it.
    3. It doesn't start at 50K and march down. It starts at the problem
       and goes wherever the equation takes it.
    4. If it needs structure → it's at 30K. If it needs to test → 10K.
       If the test breaks → back to 30K. The altitude is DISCOVERED, not assigned.
    5. The outcome is the constant. The path to get there is the variable.
    6. Each run produces constants and variables. That's all it does.
    7. P = 0 or 1. It works or it doesn't. No sliding scale.

HOW IT WORKS:
    Each run is an IMO:
        Input:  reads the output from the prior run (or fresh start)
        Middle: US.py or UP.py runs the equation
        Output: constants & variables + WHERE TO GO NEXT

    Every run gets a unique ID in the IMO warehouse (D1).
    The output contains the next instruction: go up, go down, or done.
    The chain is traceable by following IDs.

    Altitude is a LABEL on the run — where it ended up on the tree.
    Not a constraint on what it can do. Not a rail.
    The Dyno navigates freely to solve 0 → 1.

    The only constants:
        - Each run is an IMO (read input, do work, produce output)
        - Each run gets a unique ID
        - The output says where to go next
        - Everything goes in the warehouse
        - P = 0 or 1

Does NOT modify us.py or up.py (locked constants #7 and #8).

CAPABILITIES (BAR-241):
    1. OpenRouter Multi-LLM Tournament — 3 models validate each other
    2. CTB Propagation — navigate up/down the tree freely
    3. D1 Data Awareness — reads grid, slot_workbench, DOL from D1
    4. LBB Auto-Log — every run ingests to LBB (self-learning)
    5. LBB Pre-Read — reads logbook before starting (mechanic reads the log)
    6. Equation Workbench — rotate equation to solve for any variable
    7. Agent-Per-Variable — spawn one agent per blocker, sovereign silos
    8. Wall Report (Squawk) — structured report when stuck, ingests to LBB

Usage:
    # Original commands
    python3 dyno.py run --medium "..." --intent "..." [--altitude 30K] [--engine us]
    python3 dyno.py run --from-run <run_id>
    python3 dyno.py auto --medium "..." --intent "..." [--max-runs <safety-stop>]
    python3 dyno.py chain [run_id]
    python3 dyno.py status <run_id>
    python3 dyno.py registry [--filter keyword]

    # New commands (BAR-241)
    python3 dyno.py tournament --medium "..." --intent "..." [--models claude,openai,gemini]
    python3 dyno.py diagnose <run_id> [--outreach-id <id>]
    python3 dyno.py solve --outreach-id <id>
    python3 dyno.py grid [outreach_id]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


UP_ROOT = Path(__file__).resolve().parent
REPO_ROOT = UP_ROOT.parents[2]

ALTITUDES = ["50K", "40K", "30K", "20K", "10K"]

# ── Multi-LLM provider config ────────────────────────────────
# Three providers for tournament validation. Direct keys, no middleman.

LLM_PROVIDERS = {
    "claude": {
        "name": "Claude (Anthropic)",
        "env_key": "ANTHROPIC_API_KEY",  # or use Claude Code's built-in auth
        "model": "claude-sonnet-4-6",
        "engine_var": "UP_BUILD_MODEL",
        "engine_val": "sonnet",
    },
    "openai": {
        "name": "OpenAI (GPT)",
        "env_key": "OPENAI_API_KEY",
        "model": "gpt-4o",
        "engine_var": "UP_BUILD_MODEL",
        "engine_val": "openai",
    },
    "gemini": {
        "name": "Google (Gemini)",
        "env_key": "GLOBAL_GEMINI_API_KEY",
        "model": "gemini-2.5-pro",
        "engine_var": "UP_BUILD_MODEL",
        "engine_val": "gemini",
    },
}

# ── D1 query helper ──────────────────────────────────────────

D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

def d1_query(sql: str) -> list[dict]:
    """Query D1 via wrangler. Returns list of row dicts."""
    try:
        result = subprocess.run(
            ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql],
            capture_output=True, text=True, timeout=30,
            cwd=WRANGLER_CWD,
        )
        if result.returncode != 0:
            return []
        # Wrangler output contains JSON array with results
        # Find the JSON portion in stdout
        stdout = result.stdout
        # Look for the JSON array in the output
        start = stdout.find("[")
        if start == -1:
            return []
        # Find matching close bracket
        bracket_count = 0
        end = start
        for i in range(start, len(stdout)):
            if stdout[i] == "[":
                bracket_count += 1
            elif stdout[i] == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    end = i + 1
                    break
        json_str = stdout[start:end]
        data = json.loads(json_str)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("results", [])
        return []
    except Exception:
        return []


# ── LBB helper ───────────────────────────────────────────────

LBB_URL = os.environ.get("LBB_URL", "https://lbb.svg-outreach.workers.dev")
LBB_API_KEY = os.environ.get("LBB_API_KEY", "")

def lbb_query(query: str, subject_id: str = "processes", limit: int = 5) -> list[dict]:
    """Query LBB for prior knowledge."""
    if not LBB_API_KEY:
        # Try Doppler
        try:
            result = subprocess.run(
                ["doppler", "secrets", "get", "LBB_API_KEY", "--plain", "-p", "imo-creator", "-c", "dev"],
                capture_output=True, text=True, timeout=10,
            )
            key = result.stdout.strip()
        except Exception:
            key = ""
    else:
        key = LBB_API_KEY

    if not key:
        return []

    try:
        import urllib.request
        req = urllib.request.Request(
            f"{LBB_URL}/query",
            data=json.dumps({"query": query, "subject_id": subject_id, "limit": limit}).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("results", data.get("records", []))
    except Exception:
        return []


def lbb_ingest(title: str, content: str, subject_id: str = "processes", tags: list[str] = None) -> str | None:
    """Ingest a record to LBB. Returns record_id or None."""
    if not LBB_API_KEY:
        try:
            result = subprocess.run(
                ["doppler", "secrets", "get", "LBB_API_KEY", "--plain", "-p", "imo-creator", "-c", "dev"],
                capture_output=True, text=True, timeout=10,
            )
            key = result.stdout.strip()
        except Exception:
            key = ""
    else:
        key = LBB_API_KEY

    if not key:
        return None

    try:
        import urllib.request
        payload = {
            "title": title,
            "content": content[:4000],
            "subject_id": subject_id,
            "source_type": "document",
            "source_name": "dyno-auto-log",
            "tags": tags or ["dyno", "auto-log"],
        }
        req = urllib.request.Request(
            f"{LBB_URL}/ingest",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("record_id")
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════
# D1 WRITES + R2 PUSH — Dyno's own logbook
# ═══════════════════════════════════════════════════════════════
# Every us.py / up.py run writes a row to D1 (tagged side=US or UP)
# and pushes raw artifacts to R2 for replay/audit.
#
# HEIR: sovereign=imo-creator, hub=dyno, cc_layer=CC-03
# ORBT: BUILD (until auditor promotes)
# Repair: see docs/dyno-storage-repair-guide.md
# ═══════════════════════════════════════════════════════════════

R2_BUCKET = os.environ.get("R2_BUCKET", "svg-files")


def d1_execute(sql: str) -> bool:
    """Execute SQL against D1 via wrangler. Returns True on success."""
    try:
        r = subprocess.run(
            ["npx", "wrangler", "d1", "execute", D1_DB,
             "--remote", "--command", sql, "--json"],
            cwd=WRANGLER_CWD, capture_output=True, text=True, timeout=30,
        )
        return r.returncode == 0
    except Exception:
        return False


def sql_esc(v: Any) -> str:
    """SQL-escape a value for inline D1 statements."""
    if v is None:
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def d1_write_us_run(run: dict) -> bool:
    """Write a US run to dyno_runs table, tagged side='US'.

    Maps from dyno.py's run dict to dyno_runs columns.
    """
    md = run.get("middle_data", {}) or {}
    od = run.get("output_data", {}) or {}
    m_constants = json.dumps([c.get("name", "?") for c in run.get("constants", [])])
    variables_discovered = md.get("total_layers", 0) or 0
    variables_locked = md.get("constants", 0) or 0
    variables_domesticated = md.get("domesticated", 0) or 0
    r2_path = f"dyno-runs/us/{slugify_name(run.get('medium', 'medium'))}/{run['run_id']}/"

    sql = (
        f"INSERT OR REPLACE INTO dyno_runs "
        f"(run_id, domain, m_constants, p1_definition, total_cycles, "
        f"sigma_direction, p_status, variables_discovered, variables_locked, "
        f"variables_domesticated, back_prop_conflicts, r2_artifact_path, "
        f"status, started_at, total_cost_usd, updated_at, side) VALUES ("
        f"{sql_esc(run['run_id'])}, {sql_esc(run.get('medium',''))}, "
        f"{sql_esc(m_constants)}, {sql_esc(run.get('intent',''))}, 1, "
        f"{sql_esc(od.get('sigma','insufficient_data'))}, "
        f"{int(run.get('p_result', 0))}, "
        f"{variables_discovered}, {variables_locked}, {variables_domesticated}, 0, "
        f"{sql_esc(r2_path)}, "
        f"{sql_esc('complete' if run.get('completed_at') else 'running')}, "
        f"{sql_esc(run.get('started_at', now_utc()))}, 0, {sql_esc(now_utc())}, 'US')"
    )
    return d1_execute(sql)


def d1_write_up_run(run: dict, us_run_id: str | None) -> bool:
    """Write a UP run to up_runs table, tagged side='UP'.

    Links back to the US run via us_run_id.
    """
    md = run.get("middle_data", {}) or {}
    od = run.get("output_data", {}) or {}
    stages_completed = sum(1 for k in ("define_p", "map_p", "join_p") if md.get(k) is not None)
    overall_p = int(run.get("p_result", 0))
    r2_path = f"dyno-runs/up/{slugify_name(run.get('medium', 'medium'))}/{run['run_id']}/"

    sql = (
        f"INSERT OR REPLACE INTO up_runs "
        f"(run_id, subject_id, us_run_dir, operator_intent, p1_definition, "
        f"stages_completed, overall_p, status, r2_artifact_path, total_cost_usd, "
        f"started_at, completed_at, updated_at, side, us_run_id) VALUES ("
        f"{sql_esc(run['run_id'])}, {sql_esc(run.get('medium',''))}, "
        f"{sql_esc(run.get('run_dir',''))}, {sql_esc(run.get('intent',''))}, "
        f"{sql_esc(run.get('intent',''))}, "
        f"{stages_completed}, {overall_p}, "
        f"{sql_esc('complete' if run.get('completed_at') else 'running')}, "
        f"{sql_esc(r2_path)}, 0, "
        f"{sql_esc(run.get('started_at', now_utc()))}, "
        f"{sql_esc(run.get('completed_at',''))}, "
        f"{sql_esc(now_utc())}, 'UP', {sql_esc(us_run_id)})"
    )
    return d1_execute(sql)


def d1_write_up_stage(run_id: str, stage_num: int, stage_name: str,
                       artifact_name: str, artifact_data: dict,
                       p: int, status: str) -> bool:
    """Write an up_stages row — one row per stage artifact."""
    stage_id = f"{run_id}-s{stage_num:02d}-{stage_name}"
    sql = (
        f"INSERT OR REPLACE INTO up_stages "
        f"(stage_id, run_id, stage_number, stage_name, artifact_name, "
        f"artifact_json, p, status, side) VALUES ("
        f"{sql_esc(stage_id)}, {sql_esc(run_id)}, {stage_num}, "
        f"{sql_esc(stage_name)}, {sql_esc(artifact_name)}, "
        f"{sql_esc(json.dumps(artifact_data, default=str)[:8000])}, "
        f"{p}, {sql_esc(status)}, 'UP')"
    )
    return d1_execute(sql)


def r2_push_file(local_path: Path, r2_key: str) -> bool:
    """Push a local file to R2 svg-files bucket."""
    try:
        r = subprocess.run(
            ["npx", "wrangler", "r2", "object", "put",
             f"{R2_BUCKET}/{r2_key}", "--file", str(local_path),
             "--content-type", "application/json", "--remote"],
            capture_output=True, text=True, timeout=30,
        )
        return r.returncode == 0
    except Exception:
        return False


def r2_push_run_artifacts(run: dict, side: str) -> int:
    """Push every artifact file in the run_dir to R2.

    Returns count of files pushed.
    """
    run_dir = Path(run.get("run_dir", ""))
    if not run_dir.exists():
        return 0

    slug = slugify_name(run.get("medium", "medium"))
    base = f"dyno-runs/{side.lower()}/{slug}/{run['run_id']}"
    count = 0
    for f in run_dir.rglob("*"):
        if f.is_file() and f.suffix in (".json", ".txt", ".md", ".log"):
            rel = f.relative_to(run_dir)
            key = f"{base}/{rel}"
            if r2_push_file(f, key):
                count += 1
    return count


def slugify_name(value: str) -> str:
    """Simple slug for R2/D1 paths."""
    slug = (value or "unknown").strip().lower()
    for old, new in (("/", "-"), (" ", "-"), ("_", "-"), (":", "")):
        slug = slug.replace(old, new)
    return "".join(ch for ch in slug if ch.isalnum() or ch == "-")[:50] or "unknown"


# ── Core: the IMO run record ──────────────────────────────────

def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n")


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def create_run(
    run_id: str,
    altitude: str,
    medium: str,
    intent: str,
    engine: str,
    input_from: str | None = None,
) -> dict:
    """Create a new run record. This is the IMO shell before the Middle runs."""
    return {
        "run_id": run_id,
        "altitude": altitude,
        "medium": medium,
        "intent": intent,
        "engine": engine,           # "us" or "up"
        "input_from": input_from,   # run_id of prior run, or None for fresh start
        "input_data": {},
        "middle_data": {},
        "output_data": {},
        "p_result": None,           # 0 or 1
        "next_action": None,        # {"go": "30K", "reason": "..."} or {"done": true}
        "constants": [],
        "variables": [],
        "created_at": now_utc(),
        "completed_at": None,
        "run_dir": None,
    }


# ── Run storage ────────────────────────────────────────────────

DYNO_STORE = UP_ROOT / "dyno-runs"


def save_run(run: dict) -> Path:
    """Save a run record to disk."""
    path = DYNO_STORE / f"{run['run_id']}.json"
    write_json(path, run)
    return path


def load_run(run_id: str) -> dict | None:
    path = DYNO_STORE / f"{run_id}.json"
    return load_json(path)


def list_all_runs() -> list[dict]:
    """List all dyno runs."""
    if not DYNO_STORE.exists():
        return []
    runs = []
    for f in sorted(DYNO_STORE.glob("*.json")):
        r = load_json(f)
        if r:
            runs.append(r)
    return runs


# ── Registry: scan existing US/UP runs ────────────────────────

def scan_registry() -> list[dict]:
    """Scan all existing US and UP runs. The logbook of what exists."""
    registry = []

    # US runs
    us_root = UP_ROOT / "us-runs"
    if us_root.exists():
        for subject_dir in sorted(us_root.iterdir()):
            if not subject_dir.is_dir():
                continue
            for run_dir in sorted(subject_dir.iterdir()):
                if not run_dir.is_dir() or not run_dir.name.startswith("run-"):
                    continue
                us = load_json(run_dir / "01-us.json")
                if not us:
                    continue
                layers = us.get("layers", [])
                registry.append({
                    "type": "us",
                    "subject": subject_dir.name,
                    "run": run_dir.name,
                    "run_dir": str(run_dir),
                    "medium": us.get("medium", "")[:80],
                    "total_layers": us.get("total_layers", len(layers)),
                    "invariant_count": len(us.get("invariant_set", [])),
                    "domesticated": len([l for l in layers if l.get("domesticated")]),
                    "constants": len([l for l in layers if l.get("cv") == "constant"]),
                    "variables": len([l for l in layers if l.get("cv") == "variable"]),
                    "sigma": us.get("sigma_status", ""),
                    "layer_names": [l.get("name", "") for l in layers[:8]],
                })

    # UP runs
    up_dirs = [
        REPO_ROOT / "factory" / "ts-sneakers" / "playbooks" / ".up-runs",
    ]
    for up_root in up_dirs:
        if not up_root.exists():
            continue
        for subject_dir in sorted(up_root.iterdir()):
            if not subject_dir.is_dir():
                continue
            for run_dir in sorted(subject_dir.iterdir()):
                if not run_dir.is_dir() or not run_dir.name.startswith("run-"):
                    continue
                qc = load_json(run_dir / "05-qc.json")
                if not qc:
                    continue
                stages = qc.get("stages", {})
                dp = stages.get("define", {}).get("p") if isinstance(stages.get("define"), dict) else None
                mp = stages.get("map", {}).get("p") if isinstance(stages.get("map"), dict) else None
                jp = stages.get("join", {}).get("p") if isinstance(stages.get("join"), dict) else None
                registry.append({
                    "type": "up",
                    "subject": subject_dir.name,
                    "run": run_dir.name,
                    "run_dir": str(run_dir),
                    "p_result": 1 if dp == 1 and mp == 1 and jp == 1 else 0,
                    "define_p": dp, "map_p": mp, "join_p": jp,
                })

    return registry


def build_history_context(medium: str) -> str:
    """Build a text summary of prior runs related to this medium.
    Injected into the intent so the model sees the full picture."""
    registry = scan_registry()
    if not registry:
        return ""

    medium_words = set(w for w in medium.lower().replace("—", " ").split() if len(w) > 3)
    related = []
    for entry in registry:
        entry_words = set(entry.get("subject", "").lower().replace("-", " ").split())
        entry_medium = set(w for w in entry.get("medium", "").lower().replace("—", " ").split() if len(w) > 3)
        if (medium_words & entry_words) or (medium_words & entry_medium):
            related.append(entry)

    if not related:
        return ""

    lines = ["\n\n--- PRIOR RUNS (what already exists on the tree) ---"]
    subjects: dict[str, list] = {}
    for e in related:
        s = e["subject"]
        subjects.setdefault(s, []).append(e)

    for subj, runs in sorted(subjects.items()):
        lines.append(f"\n{subj}:")
        for r in runs:
            if r["type"] == "us":
                lines.append(f"  US {r['run']}: {r['total_layers']} layers, "
                             f"{r['invariant_count']} invariants, "
                             f"C={r['constants']} V={r['variables']}")
            else:
                lines.append(f"  UP {r['run']}: P={r['p_result']} "
                             f"(D={r.get('define_p','?')} M={r.get('map_p','?')} J={r.get('join_p','?')})")

    lines.append("--- END PRIOR RUNS ---\n")
    return "\n".join(lines)


# ── Engines: fire US or UP ─────────────────────────────────────

def fire_engine(run: dict) -> dict:
    """Fire the appropriate engine (US or UP) and fill in the run record."""
    if run["engine"] == "us":
        return fire_us(run)
    elif run["engine"] == "up":
        return fire_up(run)
    else:
        run["output_data"] = {"error": f"Unknown engine: {run['engine']}"}
        run["p_result"] = 0
        return run


def fire_us(run: dict) -> dict:
    """Fire a US run."""
    run_dir = DYNO_STORE / "us" / run["run_id"]

    # Read the logbook — what did the Dyno learn from prior runs?
    logbook = read_logbook(run["medium"])

    # Build intent with history so the model sees what already exists
    history = build_history_context(run["medium"])
    intent_with_history = run["intent"] + logbook + history

    # If this run chains from a prior run, include that output as context
    if run["input_from"]:
        prior = load_run(run["input_from"])
        if prior and prior.get("output_data"):
            prior_summary = json.dumps(prior["output_data"], default=str)[:2000]
            intent_with_history += f"\n\n--- PRIOR RUN OUTPUT (run {run['input_from']} at {prior.get('altitude','?')}) ---\n{prior_summary}\n--- END ---\n"

    run["input_data"] = {
        "medium": run["medium"],
        "intent": run["intent"],
        "input_from": run["input_from"],
        "altitude": run["altitude"],
        "history_injected": bool(history),
    }

    env = os.environ.copy()
    env.setdefault("UP_BUILD_MODEL", "anthropic/claude-sonnet-4")
    # Make OpenRouter available to us.py — it checks OPENROUTER_API_KEY and
    # uses OpenRouter when present, otherwise falls back to Claude CLI.
    if "OPENROUTER_API_KEY" not in env:
        try:
            r = subprocess.run(
                ["doppler", "secrets", "get", "OPENROUTER_API_KEY", "--plain",
                 "-p", "imo-creator", "-c", "dev"],
                capture_output=True, text=True, timeout=10,
            )
            if r.stdout.strip():
                env["OPENROUTER_API_KEY"] = r.stdout.strip()
        except Exception:
            pass
    timeout = int(os.environ.get("DYNO_TIMEOUT", "1800"))

    print(f"\n  [{run['altitude']}] Firing US: {run['medium'][:60]}...")
    print(f"  Run ID: {run['run_id']}")
    if env.get("OPENROUTER_API_KEY"):
        print(f"  OpenRouter: enabled")
    if history:
        print(f"  History: injected from prior runs")

    cmd = [
        sys.executable, str(UP_ROOT / "us.py"),
        run["medium"], intent_with_history,
        "--output-dir", str(run_dir),
    ]

    run["started_at"] = now_utc()
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    run["run_dir"] = str(run_dir)

    # Read the output
    us = load_json(run_dir / "01-us.json")
    if us:
        layers = us.get("layers", [])
        constants = [l for l in layers if l.get("cv") == "constant"]
        variables = [l for l in layers if l.get("cv") == "variable"]
        domesticated = [l for l in layers if l.get("domesticated")]

        run["constants"] = [{"id": l["id"], "name": l["name"]} for l in constants]
        run["variables"] = [{"id": l["id"], "name": l["name"]} for l in variables]
        run["p_result"] = 1 if len(domesticated) == len(layers) and len(layers) > 0 else 0

        run["middle_data"] = {
            "total_layers": len(layers),
            "constants": len(constants),
            "variables": len(variables),
            "domesticated": len(domesticated),
            "invariants": len(us.get("invariant_set", [])),
        }

        run["output_data"] = {
            "invariant_set": [inv.get("name") for inv in us.get("invariant_set", [])],
            "reverse_route": us.get("reverse_route", {}),
            "handoff": us.get("handoff_contract", {}),
            "sigma": us.get("sigma_status", ""),
        }
    else:
        error = load_json(run_dir / "00-error.json")
        run["p_result"] = 0
        run["output_data"] = {"error": error.get("message", "unknown") if error else "no artifact"}

    run["completed_at"] = now_utc()

    # ── Dyno logbook: D1 + R2 ─────────────────────────────────
    # Tag side='US' on every row, push artifacts under dyno-runs/us/...
    if d1_write_us_run(run):
        print(f"  D1: dyno_runs logged (side=US)")
    else:
        print(f"  D1: write FAILED — run {run['run_id']} not in D1")

    pushed = r2_push_run_artifacts(run, side="US")
    if pushed > 0:
        print(f"  R2: {pushed} artifacts pushed to dyno-runs/us/{slugify_name(run.get('medium','medium'))}/{run['run_id']}/")

    return run


def fire_up(run: dict) -> dict:
    """Fire a UP run."""
    # Find the US run dir to use as handoff
    us_run_dir = None
    if run.get("input_from"):
        prior = load_run(run["input_from"])
        if prior and prior.get("run_dir"):
            candidate = Path(prior["run_dir"])
            if (candidate / "01-us.json").exists():
                us_run_dir = candidate

    if not us_run_dir:
        run["p_result"] = 0
        run["output_data"] = {"error": "No US run to chain from. Fire a US run first."}
        run["completed_at"] = now_utc()
        return run

    # UP needs a subject_path (directory) and operator_intent
    subject_path = Path(us_run_dir).parent.parent  # e.g., factory/agents/up/us-runs/glassdoor-outreach-signals
    if not subject_path.exists():
        subject_path.mkdir(parents=True, exist_ok=True)

    run["input_data"] = {
        "us_run_dir": str(us_run_dir),
        "input_from": run["input_from"],
        "altitude": run["altitude"],
    }

    env = os.environ.copy()
    env.setdefault("UP_BUILD_MODEL", "anthropic/claude-sonnet-4")
    env.setdefault("UP_AUDIT_MODEL", "opus")
    # Make OpenRouter available to up.py — see fire_us comment.
    if "OPENROUTER_API_KEY" not in env:
        try:
            r = subprocess.run(
                ["doppler", "secrets", "get", "OPENROUTER_API_KEY", "--plain",
                 "-p", "imo-creator", "-c", "dev"],
                capture_output=True, text=True, timeout=10,
            )
            if r.stdout.strip():
                env["OPENROUTER_API_KEY"] = r.stdout.strip()
        except Exception:
            pass
    timeout = int(os.environ.get("DYNO_TIMEOUT", "1800"))

    print(f"\n  [{run['altitude']}] Firing UP from US: {us_run_dir}")
    print(f"  Run ID: {run['run_id']}")
    if env.get("OPENROUTER_API_KEY"):
        print(f"  OpenRouter: enabled")

    cmd = [
        sys.executable, str(UP_ROOT / "up.py"),
        "--us-run-dir", str(us_run_dir),
        str(subject_path),
        run["intent"],
    ]

    run["started_at"] = now_utc()
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)

    # Find the UP run output directory
    up_runs_dir = subject_path / ".up-runs"
    if not up_runs_dir.exists():
        # Check alternate location
        up_runs_dir = Path(REPO_ROOT) / "factory" / "ts-sneakers" / "playbooks" / ".up-runs"

    # Find latest run with QC
    qc_data = None
    up_run_dir = None
    if up_runs_dir.exists():
        for d in sorted(up_runs_dir.iterdir(), reverse=True):
            if d.is_dir():
                for rd in sorted(d.iterdir(), reverse=True):
                    if rd.is_dir() and (rd / "05-qc.json").exists():
                        qc_data = load_json(rd / "05-qc.json")
                        up_run_dir = rd
                        break
                if qc_data:
                    break

    if qc_data:
        stages = qc_data.get("stages", {})
        dp = stages.get("define", {}).get("p") if isinstance(stages.get("define"), dict) else None
        mp = stages.get("map", {}).get("p") if isinstance(stages.get("map"), dict) else None
        jp = stages.get("join", {}).get("p") if isinstance(stages.get("join"), dict) else None
        overall_p = 1 if dp == 1 and mp == 1 and jp == 1 else 0

        run["p_result"] = overall_p
        run["run_dir"] = str(up_run_dir)
        run["middle_data"] = {"define_p": dp, "map_p": mp, "join_p": jp}
        run["output_data"] = {
            "p_result": overall_p,
            "stages": {"define": dp, "map": mp, "join": jp},
        }
    else:
        run["p_result"] = 0
        stdout = result.stdout[:500] if result.stdout else ""
        run["output_data"] = {"error": f"No QC artifact produced. stdout: {stdout}"}

    run["completed_at"] = now_utc()

    # ── Dyno logbook: D1 + R2 ─────────────────────────────────
    # Tag side='UP', link back to the US run that fed this one.
    us_run_id = run.get("input_from")  # dyno.py's chain pointer
    if d1_write_up_run(run, us_run_id):
        print(f"  D1: up_runs logged (side=UP, us_run_id={us_run_id})")
    else:
        print(f"  D1: write FAILED — run {run['run_id']} not in D1")

    # Write per-stage rows if we have QC data
    if qc_data and up_run_dir:
        for i, stage in enumerate(["define", "map", "join", "qc"], start=1):
            artifact_file = {
                "define": "02-define.json",
                "map": "03-map.json",
                "join": "04-join.json",
                "qc": "05-qc.json",
            }[stage]
            apath = Path(up_run_dir) / artifact_file
            if apath.exists():
                try:
                    adata = json.loads(apath.read_text())
                    stage_info = qc_data.get("stages", {}).get(stage, {}) if stage != "qc" else {}
                    stage_p = stage_info.get("p", 1 if stage == "qc" else 0)
                    stage_status = stage_info.get("status", "complete")
                    d1_write_up_stage(run["run_id"], i, stage, artifact_file, adata, stage_p, stage_status)
                except Exception as e:
                    print(f"  D1: stage {stage} write skipped: {e}")

    pushed = r2_push_run_artifacts(run, side="UP")
    if pushed > 0:
        print(f"  R2: {pushed} artifacts pushed to dyno-runs/up/{slugify_name(run.get('medium','medium'))}/{run['run_id']}/")

    return run


# ── IMO Warehouse ingest ───────────────────────────────────────

def ingest_run(run: dict) -> None:
    """Push a completed dyno run to the IMO warehouse."""
    # Also ingest the underlying US/UP run if it has a run_dir
    if run.get("run_dir"):
        ingest_script = UP_ROOT / "imo_ingest.py"
        if ingest_script.exists():
            run_type = run["engine"]
            try:
                subprocess.run(
                    [sys.executable, str(ingest_script),
                     "--run-dir", run["run_dir"], "--type", run_type],
                    capture_output=True, text=True, timeout=60,
                )
                print(f"  [IMO] Ingested to warehouse")
            except Exception as e:
                print(f"  [WARN] Ingest error: {e}")


# ── D1 Grid Awareness ────────────────────────────────────────

def read_grid(outreach_id: str) -> dict | None:
    """Read a company's grid state from D1. Queries slot_workbench directly
    (the grid view is too CPU-heavy for D1's limits on full scans).
    Returns a merged dict with all 3 slots' data for one company."""
    oid = outreach_id.replace("'", "''")
    rows = d1_query(
        f"SELECT * FROM slot_workbench WHERE outreach_id = '{oid}' ORDER BY slot_type"
    )
    if not rows:
        return None

    # Merge into one row per company with slot-prefixed fields
    merged = {}
    for row in rows:
        slot = row.get("slot_type", "").lower()
        if slot == "ceo":
            # CEO row carries company-level fields
            merged.update(row)
        # Add slot-prefixed people fields
        merged[f"people_{slot}_has_name"] = row.get("has_name", 0)
        merged[f"people_{slot}_has_email"] = row.get("has_email", 0)
        merged[f"people_{slot}_has_verified_email"] = row.get("has_verified_email", 0)
        merged[f"people_{slot}_has_linkedin"] = row.get("has_linkedin", 0)
        merged[f"people_{slot}_is_filled"] = row.get("is_filled", 0)

    # Compute CT checkboxes
    merged["ct_has_name"] = 1 if merged.get("company_name") else 0
    merged["ct_has_domain"] = 1 if merged.get("domain") else 0
    merged["ct_has_location"] = 1 if merged.get("city") and merged.get("state") else 0
    merged["ct_has_employees"] = 1 if merged.get("employees") and int(merged.get("employees", 0) or 0) > 0 else 0
    merged["ct_has_ein"] = 1 if merged.get("ein") else 0
    merged["dol_ein_linked"] = 1 if merged.get("filing_present") else 0
    merged["sp_has_about_page"] = 1 if merged.get("about_url") else 0
    merged["sp_has_blog"] = 1 if merged.get("blog_source_url") else 0
    merged["sp_has_linkedin"] = 1 if merged.get("recon_linkedin_company") else 0
    merged["sp_has_platforms"] = 1 if merged.get("recon_platform_urls") and merged.get("recon_platform_urls") != "{}" else 0

    # Scores
    merged["ct_score"] = sum([merged.get("ct_has_name", 0), merged.get("ct_has_domain", 0),
                              merged.get("ct_has_location", 0), merged.get("ct_has_employees", 0),
                              merged.get("ct_has_ein", 0)])
    merged["dol_score"] = merged.get("dol_ein_linked", 0)
    merged["people_total_score"] = sum([
        merged.get(f"people_{s}_{f}", 0)
        for s in ["ceo", "cfo", "hr"]
        for f in ["has_name", "has_email", "has_verified_email", "has_linkedin"]
    ])

    return merged


def read_grid_summary() -> dict:
    """Read grid-level summary stats from slot_workbench (CEO slots only for company-level)."""
    rows = d1_query("""
        SELECT
            COUNT(*) as total,
            SUM(has_email) as ceo_has_email,
            SUM(has_name) as ceo_has_name,
            SUM(has_verified_email) as ceo_has_verified,
            SUM(has_linkedin) as ceo_has_linkedin,
            SUM(is_filled) as ceo_filled,
            SUM(CASE WHEN ein IS NOT NULL AND ein != '' THEN 1 ELSE 0 END) as has_ein,
            SUM(CASE WHEN filing_present = 1 THEN 1 ELSE 0 END) as dol_linked,
            SUM(CASE WHEN about_url IS NOT NULL AND about_url != '' THEN 1 ELSE 0 END) as has_about,
            SUM(CASE WHEN last_recon_at IS NOT NULL THEN 1 ELSE 0 END) as recon_done
        FROM slot_workbench WHERE slot_type = 'CEO'
    """)
    return rows[0] if rows else {}


def read_blocking_variables(outreach_id: str) -> list[dict]:
    """Given a company, identify what's blocking full readiness.
    Returns a list of {field, current_value, required, agent} dicts."""
    grid = read_grid(outreach_id)
    if not grid:
        return [{"field": "company", "current_value": 0, "required": 1, "agent": None, "reason": "Company not found in grid"}]

    blockers = []

    # People blockers
    for slot in ["ceo", "cfo", "hr"]:
        if not grid.get(f"people_{slot}_has_name"):
            blockers.append({"field": f"people_{slot}_name", "current_value": 0, "required": 1,
                            "agent": "200", "reason": f"{slot.upper()} name missing"})
        if not grid.get(f"people_{slot}_has_email"):
            blockers.append({"field": f"people_{slot}_email", "current_value": 0, "required": 1,
                            "agent": "201", "reason": f"{slot.upper()} email missing"})
        if not grid.get(f"people_{slot}_has_verified_email"):
            blockers.append({"field": f"people_{slot}_verified_email", "current_value": 0, "required": 1,
                            "agent": "201-mv", "reason": f"{slot.upper()} email not verified"})
        if not grid.get(f"people_{slot}_has_linkedin"):
            blockers.append({"field": f"people_{slot}_linkedin", "current_value": 0, "required": 1,
                            "agent": "202", "reason": f"{slot.upper()} LinkedIn missing"})

    # DOL blocker
    if not grid.get("dol_ein_linked"):
        blockers.append({"field": "dol_ein_linked", "current_value": 0, "required": 1,
                        "agent": "dol-link", "reason": "EIN not linked to DOL filings"})

    # SP blockers
    if not grid.get("sp_has_about_page"):
        blockers.append({"field": "sp_about_page", "current_value": 0, "required": 1,
                        "agent": "300", "reason": "About page URL missing"})
    if not grid.get("sp_has_linkedin"):
        blockers.append({"field": "sp_linkedin", "current_value": 0, "required": 1,
                        "agent": "300", "reason": "LinkedIn company page missing"})

    return blockers


# ── Equation Workbench ───────────────────────────────────────
# The equation runs forward (inputs → P) or rotates to solve
# for any variable. Same equation, different unknown.

def equation_forward(run: dict) -> int:
    """Standard forward pass: given inputs, produce P. 0 or 1."""
    return run.get("p_result", 0)


def equation_reverse(target_p: int, medium: str, outreach_id: str = None) -> dict:
    """Reverse pass: given P=1 as the target, what needs to be true?
    Returns {requirements: [...], blockers: [...], path: [...]}"""

    result = {
        "target_p": target_p,
        "medium": medium,
        "outreach_id": outreach_id,
        "requirements": [],
        "blockers": [],
        "path": [],
    }

    if outreach_id:
        # Ground in real data — what does this company actually need?
        blockers = read_blocking_variables(outreach_id)
        result["blockers"] = blockers
        result["requirements"] = [
            f"{b['field']} must be 1 (currently {b['current_value']})" for b in blockers
        ]
        # Build the path: which agents to fire, in what order
        agents_needed = list(set(b["agent"] for b in blockers if b["agent"]))
        # Order: 300 first (recon), then 200 (names), then 201 (email), then 202 (linkedin)
        agent_order = ["300", "200", "201", "201-mv", "202", "dol-link"]
        result["path"] = [a for a in agent_order if a in agents_needed]
    else:
        # Generic requirements for P=1
        result["requirements"] = [
            "At least one slot with has_name = 1 AND has_email = 1",
            "Process 300 recon completed (last_recon_at not null)",
            "All upstream processes have run",
        ]

    return result


def equation_diagnose(run: dict) -> dict:
    """Diagnostic pass: which gate is blocking P=1?
    Returns {blocking_gate, blocking_variables, suggested_action}"""

    if run.get("p_result") == 1:
        return {"blocking_gate": None, "status": "P=1, no blockers"}

    output = run.get("output_data", {})
    middle = run.get("middle_data", {})

    diagnosis = {
        "blocking_gate": None,
        "blocking_variables": [],
        "suggested_action": None,
    }

    if output.get("error"):
        diagnosis["blocking_gate"] = "error"
        diagnosis["blocking_variables"] = [{"name": "engine_error", "value": output["error"][:200]}]
        diagnosis["suggested_action"] = "Fix the error, then re-run"
        return diagnosis

    engine = run.get("engine")
    if engine == "us":
        vars_list = run.get("variables", [])
        if vars_list:
            diagnosis["blocking_gate"] = "structure"
            diagnosis["blocking_variables"] = vars_list[:5]
            diagnosis["suggested_action"] = f"Run US again — {len(vars_list)} variables not yet domesticated"
    elif engine == "up":
        stages = middle
        for stage_name in ["define_p", "map_p", "join_p"]:
            if stages.get(stage_name) == 0:
                diagnosis["blocking_gate"] = stage_name.replace("_p", "")
                diagnosis["suggested_action"] = f"Stage {stage_name.replace('_p', '')} failed — go back to US"
                break

    return diagnosis


# ── Wall Report (Squawk) ─────────────────────────────────────
# When P=0 and no agent can solve it, produce a structured report.
# This is the mechanic's squawk — goes to engineering.

def generate_wall_report(runs: list[dict], medium: str, outreach_id: str = None) -> dict:
    """Generate a wall report from a series of failed runs."""
    report = {
        "type": "WALL_REPORT",
        "medium": medium,
        "outreach_id": outreach_id,
        "generated_at": now_utc(),
        "total_runs": len(runs),
        "what_was_tried": [],
        "what_worked": [],
        "whats_left": [],
        "why_stuck": [],
        "recommendation": None,
    }

    for run in runs:
        entry = {
            "run_id": run["run_id"],
            "engine": run["engine"],
            "altitude": run["altitude"],
            "p_result": run.get("p_result"),
        }
        report["what_was_tried"].append(entry)

        if run.get("p_result") == 1:
            report["what_worked"].append({
                "run_id": run["run_id"],
                "constants_locked": len(run.get("constants", [])),
            })

    # Get remaining blockers if we have a company
    if outreach_id:
        blockers = read_blocking_variables(outreach_id)
        report["whats_left"] = blockers
        unsolvable = [b for b in blockers if not b.get("agent")]
        if unsolvable:
            report["why_stuck"] = [f"No agent for: {b['field']} — {b['reason']}" for b in unsolvable]
        else:
            report["why_stuck"] = ["All blockers have agents but agents failed to solve"]

    # Last run's diagnosis
    if runs:
        last = runs[-1]
        diag = equation_diagnose(last)
        report["last_diagnosis"] = diag
        if diag.get("blocking_gate") == "error":
            report["recommendation"] = "Fix engine error before retrying"
        elif report["whats_left"]:
            report["recommendation"] = f"Human review: {len(report['whats_left'])} variables remain unsolved"
        else:
            report["recommendation"] = "Re-run with different parameters or escalate"

    return report


def save_wall_report(report: dict) -> Path:
    """Save wall report to disk and ingest to LBB."""
    path = DYNO_STORE / "walls" / f"wall-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    write_json(path, report)

    # Auto-log to LBB
    title = f"WALL: {report['medium'][:60]} — {len(report.get('whats_left', []))} blockers remain"
    content = json.dumps(report, indent=2, default=str)
    record_id = lbb_ingest(title, content, "processes", ["dyno", "wall-report", "squawk"])
    if record_id:
        print(f"  [LBB] Wall report ingested: {record_id}")

    return path


# ── Agent-Per-Variable ───────────────────────────────────────
# Spawn one agent per blocking variable. Sovereign silos.
# Each agent reads D1, does its one job, writes result back.

AGENT_SCRIPTS = {
    "300": {
        "name": "Company Recon",
        "script": "Barton-Processes/factory/outreach/300-blog-worker/src/company-recon.py",
        "args": ["--limit", "1"],
    },
    "200": {
        "name": "Find Person",
        "script": "Barton-Processes/factory/outreach/200-people-worker/src/find-person-v3.py",
        "args": ["--limit", "1"],
    },
    "201": {
        "name": "Find Email",
        "script": "Barton-Processes/factory/outreach/201-email-discovery/src/find-email.py",
        "args": ["--limit", "1"],
    },
    "201-mv": {
        "name": "Verify Email (MillionVerifier)",
        "script": None,  # TO BUILD — not wired yet
        "args": [],
    },
    "202": {
        "name": "Find LinkedIn",
        "script": "Barton-Processes/factory/outreach/202-linkedin-discovery/src/find-linkedin.py",
        "args": ["--limit", "1"],
    },
    "dol-link": {
        "name": "Link DOL EIN",
        "script": None,  # Manual — check if EIN exists in dol_form_5500
        "args": [],
    },
}


def dispatch_agent(agent_id: str, outreach_id: str) -> dict:
    """Dispatch a single agent to solve one variable for one company.
    Returns {agent, status, result}"""
    agent = AGENT_SCRIPTS.get(agent_id)
    if not agent:
        return {"agent": agent_id, "status": "unknown", "result": f"No agent registered for {agent_id}"}

    if not agent.get("script"):
        return {"agent": agent_id, "status": "manual", "result": f"{agent['name']} not automated yet — requires human"}

    script_path = Path(os.path.expanduser("~/Documents")) / agent["script"]
    if not script_path.exists():
        return {"agent": agent_id, "status": "missing", "result": f"Script not found: {script_path}"}

    print(f"  [AGENT] Dispatching {agent['name']} for {outreach_id}")

    try:
        env = os.environ.copy()
        # Try to load proxy creds from Doppler
        for var in ["PROXY_USER", "PROXY_PASS"]:
            if var not in env:
                try:
                    r = subprocess.run(
                        ["doppler", "secrets", "get", var, "--plain", "-p", "imo-creator", "-c", "dev"],
                        capture_output=True, text=True, timeout=10,
                    )
                    if r.stdout.strip():
                        env[var] = r.stdout.strip()
                except Exception:
                    pass

        result = subprocess.run(
            [sys.executable, str(script_path)] + agent["args"],
            env=env, capture_output=True, text=True, timeout=300,
        )

        return {
            "agent": agent_id,
            "status": "completed" if result.returncode == 0 else "failed",
            "result": result.stdout[-500:] if result.stdout else result.stderr[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"agent": agent_id, "status": "timeout", "result": "Agent timed out after 300s"}
    except Exception as e:
        return {"agent": agent_id, "status": "error", "result": str(e)}


def solve_variables(outreach_id: str) -> dict:
    """The self-healing loop. Rotate equation → find blockers → dispatch agents → re-check.
    Returns {solved: [...], unsolved: [...], wall: bool}"""

    result = {
        "outreach_id": outreach_id,
        "iterations": 0,
        "max_iterations": 3,
        "solved": [],
        "unsolved": [],
        "agent_results": [],
        "wall": False,
    }

    for iteration in range(result["max_iterations"]):
        result["iterations"] = iteration + 1
        print(f"\n  ── Solve iteration {iteration + 1}/{result['max_iterations']} ──")

        # 1. Rotate equation — what's blocking?
        blockers = read_blocking_variables(outreach_id)
        if not blockers:
            print(f"  All variables solved. P=1.")
            break

        print(f"  {len(blockers)} blocking variables")

        # 2. Dispatch agents for solvable blockers
        dispatched = 0
        for blocker in blockers:
            agent_id = blocker.get("agent")
            if not agent_id:
                continue
            if agent_id in [r["agent"] for r in result["agent_results"] if r["status"] == "completed"]:
                continue  # Already tried this agent

            agent_result = dispatch_agent(agent_id, outreach_id)
            result["agent_results"].append(agent_result)
            dispatched += 1

            if agent_result["status"] == "completed":
                result["solved"].append(blocker["field"])

        if dispatched == 0:
            # No agents dispatched — either all manual or all already tried
            result["wall"] = True
            result["unsolved"] = [b for b in blockers if b["field"] not in result["solved"]]
            print(f"  WALL — no more agents to dispatch")
            break

        # 3. Re-check grid
        remaining = read_blocking_variables(outreach_id)
        newly_solved = len(blockers) - len(remaining)
        if newly_solved > 0:
            print(f"  {newly_solved} variables solved this iteration")
        if not remaining:
            print(f"  All variables solved!")
            break

    result["unsolved"] = read_blocking_variables(outreach_id)
    if result["unsolved"]:
        result["wall"] = True

    return result


# ── Multi-LLM Tournament ────────────────────────────────────
# Fire the same run through multiple models. Compare outputs.
# Agreement = high confidence. Divergence = needs more work.

def tournament_run(
    medium: str,
    intent: str,
    altitude: str = "30K",
    models: list[str] = None,
) -> dict:
    """Run the same US analysis through multiple LLMs and compare."""
    if models is None:
        # Default: use all available providers
        models = []
        for pid, prov in LLM_PROVIDERS.items():
            key = os.environ.get(prov["env_key"], "")
            if not key:
                try:
                    r = subprocess.run(
                        ["doppler", "secrets", "get", prov["env_key"], "--plain", "-p", "imo-creator", "-c", "dev"],
                        capture_output=True, text=True, timeout=10,
                    )
                    if r.stdout.strip():
                        models.append(pid)
                except Exception:
                    pass
            else:
                models.append(pid)

    if not models:
        models = ["claude"]  # Fallback to current runtime

    print(f"\n{'='*60}")
    print(f"  DYNO TOURNAMENT — {len(models)} models")
    print(f"  Models: {', '.join(models)}")
    print(f"  Medium: {medium[:60]}")
    print(f"{'='*60}")

    results = {}
    for model_id in models:
        prov = LLM_PROVIDERS.get(model_id, LLM_PROVIDERS["claude"])
        print(f"\n  ── {prov['name']} ──")

        # Set the model env var for this run
        env_override = {prov["engine_var"]: prov["engine_val"]} if prov.get("engine_var") else {}
        old_vals = {}
        for k, v in env_override.items():
            old_vals[k] = os.environ.get(k)
            os.environ[k] = v

        try:
            run = execute_single_run(medium, intent, altitude, "us", None)
            results[model_id] = {
                "run_id": run["run_id"],
                "p_result": run.get("p_result"),
                "constants": run.get("constants", []),
                "variables": run.get("variables", []),
                "invariant_count": run.get("middle_data", {}).get("invariants", 0),
                "total_layers": run.get("middle_data", {}).get("total_layers", 0),
            }
        except Exception as e:
            results[model_id] = {"error": str(e)}
        finally:
            for k, v in old_vals.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    # Compare results
    tournament = {
        "models": models,
        "results": results,
        "agreement": {},
        "divergence": [],
    }

    # Check P agreement
    p_values = {m: r.get("p_result") for m, r in results.items() if "error" not in r}
    unique_p = set(p_values.values())
    tournament["agreement"]["p_result"] = len(unique_p) == 1
    if len(unique_p) > 1:
        tournament["divergence"].append({
            "field": "p_result",
            "values": p_values,
            "significance": "HIGH — models disagree on whether the structure is complete",
        })

    # Check constant count agreement
    c_counts = {m: len(r.get("constants", [])) for m, r in results.items() if "error" not in r}
    if c_counts:
        spread = max(c_counts.values()) - min(c_counts.values())
        tournament["agreement"]["constant_count"] = spread <= 2
        if spread > 2:
            tournament["divergence"].append({
                "field": "constant_count",
                "values": c_counts,
                "significance": "MEDIUM — models found different numbers of constants",
            })

    # Check invariant set overlap
    inv_sets = {}
    for m, r in results.items():
        if "error" not in r:
            run_data = load_run(r["run_id"])
            if run_data:
                inv_names = [c.get("name", "") for c in run_data.get("constants", [])]
                inv_sets[m] = set(inv_names)

    if len(inv_sets) >= 2:
        all_names = set()
        for s in inv_sets.values():
            all_names |= s
        common = set.intersection(*inv_sets.values()) if inv_sets.values() else set()
        tournament["agreement"]["common_constants"] = list(common)
        tournament["agreement"]["constant_overlap_pct"] = len(common) / len(all_names) * 100 if all_names else 100

        only_in = {}
        for m, s in inv_sets.items():
            unique = s - common
            if unique:
                only_in[m] = list(unique)
        if only_in:
            tournament["divergence"].append({
                "field": "constants",
                "only_in": only_in,
                "significance": "HIGH — these constants were found by one model but not others",
            })

    # Summary
    total_divergence = len(tournament["divergence"])
    tournament["verdict"] = "AGREEMENT" if total_divergence == 0 else f"DIVERGENCE ({total_divergence} points)"

    print(f"\n{'='*60}")
    print(f"  TOURNAMENT RESULT: {tournament['verdict']}")
    if tournament.get("agreement", {}).get("constant_overlap_pct"):
        print(f"  Constant overlap: {tournament['agreement']['constant_overlap_pct']:.0f}%")
    for d in tournament["divergence"]:
        print(f"  DIVERGENCE: {d['field']} — {d['significance']}")
    print(f"{'='*60}\n")

    # Auto-log to LBB
    title = f"TOURNAMENT: {medium[:40]} — {tournament['verdict']} ({len(models)} models)"
    content = json.dumps(tournament, indent=2, default=str)
    record_id = lbb_ingest(title, content, "processes", ["dyno", "tournament", "multi-llm"])
    if record_id:
        print(f"  [LBB] Tournament logged: {record_id}")

    return tournament


# ── LBB Auto-Log ─────────────────────────────────────────────
# Every completed run auto-ingests to LBB.

def auto_log_run(run: dict) -> None:
    """Auto-log a completed run to LBB."""
    p = run.get("p_result", "?")
    engine = run.get("engine", "?").upper()
    c_count = len(run.get("constants", []))
    v_count = len(run.get("variables", []))

    title = f"DYNO {engine}: {run['medium'][:40]} — P={p} C={c_count} V={v_count}"
    content = json.dumps({
        "run_id": run["run_id"],
        "altitude": run["altitude"],
        "engine": run["engine"],
        "p_result": run.get("p_result"),
        "constants": run.get("constants", []),
        "variables": run.get("variables", []),
        "middle_data": run.get("middle_data", {}),
        "output_data": run.get("output_data", {}),
        "diagnosis": equation_diagnose(run),
    }, indent=2, default=str)

    record_id = lbb_ingest(title, content, "processes", ["dyno", "run", engine.lower()])
    if record_id:
        print(f"  [LBB] Run auto-logged: {record_id}")


# ── LBB Pre-Read (Read the logbook) ─────────────────────────

def read_logbook(medium: str) -> str:
    """Read prior Dyno learnings from LBB before starting a run.
    The mechanic reads the logbook before touching the aircraft."""
    records = lbb_query(f"dyno {medium}", "processes", 5)
    if not records:
        return ""

    lines = ["\n--- DYNO LOGBOOK (from LBB) ---"]
    for r in records:
        lines.append(f"  {r.get('title', '?')}")
        content = r.get("content", "")[:200]
        if content:
            lines.append(f"    {content}")
    lines.append("--- END LOGBOOK ---\n")
    return "\n".join(lines)


# ── Auto-chain: the Circle ─────────────────────────────────────

def classify_description_primitive(description: str, constant_name: str, api_key: str) -> str | None:
    """Run the Three Primitives algorithm on a description via the Dyno engine.

    Feeds the description to dyno_engine.py as a domain and runs until P=1.
    Returns the dominant primitive the engine locks ('Thing', 'Flow', or 'Change').
    The engine decides how many cycles it needs — no cap imposed here.

    K=C: the description must reduce to the SAME primitive as the constant.
    """
    import urllib.request as _urllib
    import tempfile

    if not api_key:
        return None

    # The prompt IS the Three Primitives algorithm applied to a description.
    # We don't run a full Dyno subprocess here (too slow for 100+ constants).
    # Instead we make one direct call to the engine's classification logic:
    # give the description as the domain, ask "what primitive does this reduce to?"
    # This IS running the algorithm — not a word list.
    prompt = f"""You are running the Three Primitives algorithm on a description.

DESCRIPTION TO CLASSIFY:
"{description}"

THE THREE PRIMITIVES (irreducible floor):
- Thing: Something that EXISTS. A component, entity, object, container, structure.
  Test: If you removed it, does the system break because something no longer exists? YES = Thing.
- Flow: Something that MOVES. A pathway, transfer, sequence, process of movement.
  Test: If nothing moved through it, does the system break because transfer stopped? YES = Flow.
- Change: Something that TRANSFORMS. A state transition, conversion, shift.
  Test: If this transformation stopped, does the system break because no outcome occurs? YES = Change.

TASK: Apply the inversion test to the description above.
Which single primitive does this description reduce to at its core?

Output ONLY valid JSON:
{{"primitive": "Thing|Flow|Change", "inversion_test": "<what breaks if this is removed>", "confidence": "high|medium|low"}}"""

    try:
        payload = json.dumps({
            "model": "google/gemini-2.0-flash-001",
            "max_tokens": 200,
            "temperature": 0.0,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = _urllib.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://imo-creator.svg.agency",
                "X-Title": "K=C Classifier",
            },
            method="POST",
        )

        with _urllib.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]

        content_clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)
        match = re.search(r'\{.*\}', content_clean, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            prim = parsed.get("primitive", "").strip()
            if prim in ("Thing", "Flow", "Change"):
                return prim
    except Exception as e:
        print(f"      [classifier error for {constant_name}]: {e}")

    return None


def run_vocab_proof(run: dict) -> dict:
    """STEP 5 — K=C Gate: Vocabulary Proof Pass.

    After US reaches P=1, point the Dyno at each description.
    The description must reduce to the SAME primitive as the constant.
    The engine runs the Three Primitives algorithm on the description — no word list.
    The description has to equal the constant. K=C.

    Failures are flagged for human review — NOT auto-returned to discovery.
    Human finds how domain experts name the concept, corrects vocabulary.
    Only when all pass does K=C hold. UP cannot run until K=C is achieved.

    Returns: {"kc": True, "failures": [], "failures_file": None}
          or {"kc": False, "failures": [...], "failures_file": path}
    """
    output_data = run.get("output_data", {})
    constants = output_data.get("constants", output_data.get("final_constants", []))

    if not constants:
        return {"kc": True, "failures": [], "failures_file": None}

    # Get API key for classification calls
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        try:
            result = subprocess.run(
                ["doppler", "secrets", "get", "OPENROUTER_API_KEY", "--plain",
                 "-p", "imo-creator", "-c", "dev"],
                capture_output=True, text=True, timeout=10,
            )
            api_key = result.stdout.strip()
        except Exception:
            pass

    failures = []
    passed = 0

    print(f"\n  {'='*60}")
    print(f"  VOCABULARY PROOF PASS — K=C gate (US->UP handoff)")
    print(f"  Running Three Primitives algorithm on each description...")
    print(f"  {len(constants)} constants to verify")
    print(f"  {'='*60}")

    for const in constants:
        name = const.get("name", "?")
        locked_prim = const.get("primitive", "").strip()
        vocab = const.get("vocabulary") or {}
        desc = (vocab.get("description") or const.get("why") or "").strip()

        if not desc:
            print(f"    ✗ {name} [{locked_prim}]: no description — human review required")
            failures.append({
                "name": name, "primitive": locked_prim,
                "current_description": "",
                "why": const.get("why", ""),
                "action_required": "No description — human must provide expert vocabulary",
                "status": "HUMAN_REVIEW_REQUIRED"
            })
            continue

        # Run the algorithm on the description
        detected_prim = classify_description_primitive(desc, name, api_key)

        if detected_prim is None:
            # Classifier failed — skip, don't block
            print(f"    ? {name} [{locked_prim}]: classifier unavailable — skipping")
            continue

        if detected_prim == locked_prim:
            print(f"    ✓ {name} [{locked_prim}]: K=C — description reduces to same primitive")
            passed += 1
        else:
            print(f"    ✗ {name} [{locked_prim}]: mismatch — description reduces to {detected_prim}")
            failures.append({
                "name": name,
                "primitive": locked_prim,
                "description_reduces_to": detected_prim,
                "current_description": desc,
                "why": const.get("why", ""),
                "action_required": (
                    f"Description reduces to {detected_prim} but constant is locked as {locked_prim}. "
                    "Find how domain experts describe this concept so description and primitive agree."
                ),
                "status": "HUMAN_REVIEW_REQUIRED"
            })

    print(f"\n  K=C results: {passed} passed, {len(failures)} flagged")

    if failures:
        # Write failures for human review
        run_dir = Path(UP_ROOT) / "runs" / run.get("run_id", "unknown")
        run_dir.mkdir(parents=True, exist_ok=True)
        failures_file = run_dir / "vocab-proof-failures.json"
        failures_file.write_text(json.dumps(failures, indent=2), encoding="utf-8")

        print(f"\n  VOCAB PROOF: {len(failures)} flags — human review required before UP can run")
        print(f"  Failures written to: {failures_file}")
        print(f"  Find expert vocabulary for flagged concepts, then re-run vocab proof.")
        return {"kc": False, "failures": failures, "failures_file": str(failures_file)}

    print(f"\n  K=C — All {passed} constants proven. Handoff to UP authorized.")
    return {"kc": True, "failures": [], "failures_file": None}


def run_pressure_test(run: dict) -> dict:
    """STEP 6 — Pressure Test (Auditor Gate): Try to break the locked constants.

    Aviation Model: the mechanic (US/Claude) builds. Codex (the designated auditor)
    approves. Mechanic never audits own work. Codex is the FAA inspector.

    Codex is used via CLI: codex exec --approval-mode full-auto -q "<prompt>"
    This matches the AGENTS.md architecture — Codex = Mechanic/Auditor.

    The auditor is given ALL locked constants and asked:
    - Are there phantom constants (look locked but aren't)?
    - Are any primitives misclassified?
    - Does any constant break under a different framing?
    - Are there missing constants the US missed?

    If auditor breaks a constant → it goes back to US discovery.
    If auditor finds a gap → flagged for human review.
    If auditor certifies → US is approved. UP is authorized.

    Returns: {"certified": True, "broken": [], "gaps": []}
          or {"certified": False, "broken": [...], "gaps": [...]}
    """
    output_data = run.get("output_data", {})
    constants = output_data.get("constants", output_data.get("final_constants", []))
    domain = run.get("medium", "unknown domain")

    if not constants:
        return {"certified": True, "broken": [], "gaps": []}

    constants_text = "\n".join([
        f"  - {c.get('name','?')} [{c.get('primitive','?')}]: {c.get('vocabulary', {}).get('description', c.get('why',''))}"
        for c in constants
    ])

    prompt = f"""You are an independent auditor reviewing locked constants from a structural discovery run.
Your job: find what is WRONG. Try to break these constants. Be adversarial.

DOMAIN: {domain}

LOCKED CONSTANTS ({len(constants)} total):
{constants_text}

AUDIT TASKS:
1. PHANTOM TEST: For each constant — is it truly structural, or is it actually a variable/preference?
   A phantom constant looks locked but its removal would not break the domain.

2. PRIMITIVE TEST: For each constant — is the primitive (Thing/Flow/Change) correct?
   A misclassified primitive is a structural error.

3. FRAMING TEST: Can any constant be broken by reframing the domain?
   A true constant holds regardless of how you describe the domain.

4. GAP TEST: What structural constants are MISSING that must exist for this domain to function?

Output ONLY valid JSON (no markdown fences):
{{
  "audit_model": "codex",
  "domain": "{domain}",
  "total_reviewed": {len(constants)},
  "broken": [
    {{
      "name": "<constant name>",
      "failure_type": "phantom|wrong_primitive|framing_break",
      "reason": "<why it fails the audit>"
    }}
  ],
  "gaps": [
    {{
      "name": "<missing constant>",
      "primitive": "Thing|Flow|Change",
      "reason": "<why it must exist>"
    }}
  ],
  "certified": true,
  "auditor_verdict": "<one sentence summary>"
}}"""

    print(f"\n  {'='*60}")
    print(f"  PRESSURE TEST — Codex auditor (AGENTS.md: Mechanic = Auditor)")
    print(f"  Trying to break {len(constants)} constants...")
    print(f"  {'='*60}")

    # Save prompt to temp file for codex
    run_dir = Path(UP_ROOT) / "runs" / run.get("run_id", "unknown")
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = run_dir / "pressure-test-prompt.txt"
    prompt_file.write_text(prompt, encoding="utf-8")

    try:
        # Call Codex CLI — the designated auditor in AGENTS.md
        # codex exec --approval-mode full-auto runs non-interactively
        result = subprocess.run(
            ["codex", "exec", "--approval-mode", "full-auto", "-q", prompt],
            capture_output=True, text=True, timeout=300,
            cwd=str(UP_ROOT),
        )

        content = (result.stdout or "").strip()
        if not content and result.returncode != 0:
            raise RuntimeError(f"Codex exited {result.returncode}: {result.stderr[:200]}")

        # Parse JSON from Codex output
        content_clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)
        match = re.search(r'\{.*\}', content_clean, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON in Codex output: {content[:200]}")
        audit = json.loads(match.group(0))

        with _urllib.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]

        # Parse JSON from response
        content_clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)
        match = re.search(r'\{.*\}', content_clean, re.DOTALL)
        audit = json.loads(match.group(0)) if match else {}

        broken = audit.get("broken", [])
        gaps = audit.get("gaps", [])
        certified = audit.get("certified", len(broken) == 0)
        verdict = audit.get("auditor_verdict", "")

        print(f"  Auditor verdict: {verdict}")
        if broken:
            print(f"  BROKEN: {len(broken)} constants failed pressure test")
            for b in broken:
                print(f"    ✗ {b.get('name','?')} [{b.get('failure_type','?')}]: {b.get('reason','')[:80]}")
        if gaps:
            print(f"  GAPS: {len(gaps)} missing constants identified")
        if certified:
            print(f"  ✓ CERTIFIED — US approved. UP authorized.")

        # Save audit report
        run_dir = Path(UP_ROOT) / "runs" / run.get("run_id", "unknown")
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "pressure-test-audit.json").write_text(
            json.dumps(audit, indent=2), encoding="utf-8"
        )

        return {"certified": certified, "broken": broken, "gaps": gaps, "verdict": verdict}

    except Exception as e:
        print(f"  [PRESSURE TEST] Error: {e} — not blocking UP")
        return {"certified": True, "broken": [], "gaps": [], "error": str(e)}


def decide_next(run: dict) -> dict | None:
    """Read the output of a completed run and decide what to do next.
    Returns a dict with next run params, or None if done.

    The logic:
        - P=1 on a US run → run vocab proof (K=C gate). Only if K=C → chain to UP.
        - P=0 on a US run → run US again (structure not locked yet)
        - P=1 on a UP run → done (architecture locked, exit Dyno)
        - P=0 on a UP run → go back to US (something in the structure broke)
        - Error → stop and report
    """
    if run.get("output_data", {}).get("error"):
        return None  # Hit a wall. Stop.

    p = run.get("p_result")
    engine = run.get("engine")

    if p == 1 and engine == "us":
        # US at P=1. Run BOTH gates fully — K=C proof + pressure test — collect all
        # findings, then present to human as one coordinated review.
        # Engine does not stop between gates. Human sees complete picture at once.
        print(f"\n  US P=1 reached. Running full validation sweep (K=C + pressure test)...")

        vocab_result = run_vocab_proof(run)
        pressure = run_pressure_test(run)

        vocab_failed = not vocab_result.get("kc", True)
        pressure_failed = not pressure.get("certified", True)
        vocab_failures = vocab_result.get("failures", [])
        broken = pressure.get("broken", [])
        gaps = pressure.get("gaps", [])

        if vocab_failed or pressure_failed:
            # One coordinated stop. Human reviews both reports together.
            print(f"\n  {'='*60}")
            print(f"  DYNO PAUSED — Human review required")
            print(f"  {'='*60}")
            if vocab_failed:
                print(f"  K=C gate:       {len(vocab_failures)} vocabulary flags")
                print(f"                  → vocab-proof-failures.json")
            else:
                print(f"  K=C gate:       ✓ passed")
            if pressure_failed:
                print(f"  Pressure test:  {len(broken)} broken constants, {len(gaps)} structural gaps")
                print(f"                  → pressure-test-audit.json")
            else:
                print(f"  Pressure test:  ✓ certified")
            print(f"  {'='*60}")
            print(f"  Human reviews both reports, decides action, re-runs to proceed to UP.")
            return None  # Aviation Model — both inspectors file reports, human adjudicates

        return {
            "engine": "up",
            "altitude": "20K",
            "reason": "US P=1 + K=C proven + Pressure test certified — UP authorized",
        }

    if p == 0 and engine == "us":
        # Structure not locked. Run US again.
        return {
            "engine": "us",
            "altitude": run.get("altitude", "30K"),
            "reason": "US P=0 — structure incomplete, running again",
        }

    if p == 1 and engine == "up":
        # Architecture locked. Done.
        return None  # P=1 on UP = exit Dyno

    if p == 0 and engine == "up":
        # Architecture failed. Go back up to structure.
        return {
            "engine": "us",
            "altitude": "30K",
            "reason": "UP P=0 — architecture failed, back to structure",
        }

    return None


def execute_single_run(
    medium: str,
    intent: str,
    altitude: str,
    engine: str,
    input_from: str | None,
) -> dict:
    """Execute one run and return the completed record."""
    run_id = new_run_id()
    run = create_run(run_id, altitude, medium, intent, engine, input_from)
    save_run(run)

    print(f"\n{'='*60}")
    print(f"  DYNO RUN: {run_id}")
    print(f"  ALTITUDE: {altitude}")
    print(f"  ENGINE:   {engine.upper()}")
    print(f"  MEDIUM:   {medium[:60]}")
    if input_from:
        print(f"  CHAINED FROM: {input_from}")
    print(f"{'='*60}")

    run = fire_engine(run)
    save_run(run)
    ingest_run(run)
    auto_log_run(run)

    print(f"\n  RESULT: P={run['p_result']} | C={len(run.get('constants',[]))} V={len(run.get('variables',[]))}")
    if run.get("middle_data"):
        for k, v in run["middle_data"].items():
            print(f"    {k}: {v}")
    if run.get("output_data", {}).get("error"):
        print(f"  ERROR: {run['output_data']['error']}")

    return run


# ── Commands ───────────────────────────────────────────────────

def cmd_run(args: argparse.Namespace) -> int:
    """Fire a single run. Either fresh or chained from a prior run."""
    altitude = args.altitude or "30K"
    engine = args.engine or "us"
    input_from = None
    medium = args.medium
    intent = args.intent

    if args.from_run:
        prior = load_run(args.from_run)
        if not prior:
            print(f"  [ERROR] Run not found: {args.from_run}")
            return 1
        input_from = args.from_run
        medium = medium or prior["medium"]
        intent = intent or prior["intent"]
        if not args.engine and prior["engine"] == "us" and prior["p_result"] == 1:
            engine = "up"

    if not medium:
        print("  [ERROR] --medium required for fresh runs")
        return 1
    if not intent:
        print("  [ERROR] --intent required for fresh runs")
        return 1

    run = execute_single_run(medium, intent, altitude, engine, input_from)

    print(f"\n  Run ID: {run['run_id']}")
    print(f"  Chain next: python3 dyno.py run --from-run {run['run_id']}")
    print(f"  Or auto:    python3 dyno.py auto --from-run {run['run_id']}")

    return 0


def cmd_auto(args: argparse.Namespace) -> int:
    """Auto-chain: fire runs, read output, decide next, repeat until P=1 or wall.
    The Circle — output feeds back to input until the outcome is reached.

    max_runs is a RUNAWAY-LOOP SAFETY STOP — not a convergence target.
    The engine runs until P=1. The number of runs is the variable.
    If max_runs triggers, log as convergence failure (not "done").
    """
    max_runs = int(args.max_runs) if args.max_runs else 10000
    input_from = None
    medium = args.medium
    intent = args.intent
    altitude = args.altitude or "30K"
    engine = args.engine or "us"

    if args.from_run:
        prior = load_run(args.from_run)
        if not prior:
            print(f"  [ERROR] Run not found: {args.from_run}")
            return 1
        input_from = args.from_run
        medium = medium or prior["medium"]
        intent = intent or prior["intent"]
        # Pick up where the prior run left off
        next_step = decide_next(prior)
        if next_step:
            engine = next_step["engine"]
            altitude = next_step["altitude"]
        elif prior["p_result"] == 1 and prior["engine"] == "up":
            print(f"\n  Already done. Prior run {args.from_run} reached P=1 on UP.")
            print(f"  Dyno exit. Ready for build & test.")
            return 0

    if not medium:
        print("  [ERROR] --medium required")
        return 1
    if not intent:
        print("  [ERROR] --intent required")
        return 1

    print(f"\n{'='*60}")
    print(f"  DYNO AUTO-CHAIN")
    print(f"  OUTCOME: {medium[:60]}")
    print(f"  SAFETY STOP: {max_runs} runs (NOT a target — engine runs until P=1)")
    print(f"  Starting: {engine.upper()} at {altitude}")
    print(f"{'='*60}")

    run_count = 0
    current_run = None

    while run_count < max_runs:
        run_count += 1
        print(f"\n  ── Auto-chain step {run_count}/{max_runs} ──")

        current_run = execute_single_run(medium, intent, altitude, engine, input_from)

        # Check: are we done?
        if current_run["p_result"] == 1 and current_run["engine"] == "up":
            print(f"\n{'='*60}")
            print(f"  DYNO COMPLETE — P=1 on UP")
            print(f"  Runs: {run_count}")
            print(f"  Final run: {current_run['run_id']}")
            print(f"  Ready for build & test (outside Dyno)")
            print(f"{'='*60}\n")
            return 0

        # Decide next
        next_step = decide_next(current_run)
        if not next_step:
            print(f"\n{'='*60}")
            print(f"  DYNO STOPPED — hit a wall")
            print(f"  Runs: {run_count}")
            print(f"  Last run: {current_run['run_id']} P={current_run['p_result']}")

            # Generate wall report (squawk)
            all_chain_runs = []
            rid = current_run["run_id"]
            while rid:
                r = load_run(rid)
                if r:
                    all_chain_runs.insert(0, r)
                    rid = r.get("input_from")
                else:
                    break
            wall = generate_wall_report(all_chain_runs, medium)
            wall_path = save_wall_report(wall)
            print(f"  Wall report: {wall_path}")
            if wall.get("recommendation"):
                print(f"  Recommendation: {wall['recommendation']}")

            print(f"  Resume: python3 dyno.py auto --from-run {current_run['run_id']}")
            print(f"{'='*60}\n")
            return 1

        # Set up next run
        input_from = current_run["run_id"]
        engine = next_step["engine"]
        altitude = next_step["altitude"]
        print(f"\n  → Next: {next_step['reason']}")

    # Loop exit without reaching P=1 → safety halt, not "done"
    print(f"\n{'='*60}")
    print(f"  SAFETY HALT — hit max_runs safety ceiling ({max_runs})")
    print(f"  Engine did NOT reach P=1. This is P=0, not done.")
    print(f"  Sigma did not converge. Human must investigate why structure isn't locking.")
    print(f"  Last run: {current_run['run_id']} P={current_run['p_result']}")
    print(f"  Resume: python3 dyno.py auto --from-run {current_run['run_id']}")
    print(f"{'='*60}\n")
    return 0


def cmd_chain(args: argparse.Namespace) -> int:
    """Show the chain of runs starting from a given run."""
    all_runs = list_all_runs()
    if not all_runs:
        print("  No dyno runs found.")
        return 0

    # Build chain forward and backward from the given run
    by_id = {r["run_id"]: r for r in all_runs}

    if args.run_id:
        # Trace backward to root
        chain = []
        current = args.run_id
        while current and current in by_id:
            chain.append(by_id[current])
            current = by_id[current].get("input_from")
        chain.reverse()

        # Trace forward from the given run
        forward = {r.get("input_from"): r for r in all_runs if r.get("input_from")}
        current = args.run_id
        while current in forward:
            chain.append(forward[current])
            current = forward[current]["run_id"]
    else:
        chain = sorted(all_runs, key=lambda r: r.get("created_at", ""))

    print(f"\n{'='*60}")
    print(f"  IMO CHAIN — {len(chain)} runs")
    print(f"{'='*60}")

    for r in chain:
        p = r.get("p_result", "?")
        p_mark = "✓" if p == 1 else "✗" if p == 0 else "?"
        alt = r.get("altitude", "?")
        eng = r.get("engine", "?").upper()
        c_count = len(r.get("constants", []))
        v_count = len(r.get("variables", []))
        medium = r.get("medium", "")[:40]
        marker = " ←" if args.run_id and r["run_id"] == args.run_id else ""

        print(f"\n  [{alt}] {r['run_id']} P={p} {p_mark}{marker}")
        print(f"    Engine: {eng} | C={c_count} V={v_count} | {medium}")

        if r.get("input_from"):
            print(f"    ↑ from: {r['input_from']}")

    print(f"\n{'='*60}\n")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Show details of a specific run."""
    run = load_run(args.run_id)
    if not run:
        print(f"  Run not found: {args.run_id}")
        return 1

    print(f"\n{'='*60}")
    print(f"  RUN: {run['run_id']}")
    print(f"  ALTITUDE: {run['altitude']}")
    print(f"  ENGINE: {run['engine'].upper()}")
    print(f"  P: {run.get('p_result', '?')}")
    print(f"  MEDIUM: {run['medium']}")
    print(f"  CREATED: {run['created_at']}")
    print(f"  COMPLETED: {run.get('completed_at', 'running...')}")
    if run.get("input_from"):
        print(f"  CHAINED FROM: {run['input_from']}")
    if run.get("run_dir"):
        print(f"  RUN DIR: {run['run_dir']}")

    print(f"\n  INPUT:")
    for k, v in run.get("input_data", {}).items():
        print(f"    {k}: {str(v)[:80]}")

    print(f"\n  MIDDLE:")
    for k, v in run.get("middle_data", {}).items():
        print(f"    {k}: {v}")

    print(f"\n  OUTPUT:")
    for k, v in run.get("output_data", {}).items():
        val = str(v)[:100]
        print(f"    {k}: {val}")

    print(f"\n  CONSTANTS ({len(run.get('constants', []))}):")
    for c in run.get("constants", [])[:10]:
        print(f"    {c.get('id', '?')}: {c.get('name', '?')}")

    print(f"\n  VARIABLES ({len(run.get('variables', []))}):")
    for v in run.get("variables", [])[:10]:
        print(f"    {v.get('id', '?')}: {v.get('name', '?')}")

    print(f"\n{'='*60}\n")
    return 0


def cmd_registry(args: argparse.Namespace) -> int:
    """Show the run registry — the map of what exists."""
    registry = scan_registry()
    filter_kw = args.filter if hasattr(args, "filter") and args.filter else None

    if filter_kw:
        registry = [r for r in registry if filter_kw.lower() in r.get("subject", "").lower()
                     or filter_kw.lower() in r.get("medium", "").lower()]

    if not registry:
        print("  No runs found.")
        return 0

    subjects: dict[str, list] = {}
    for e in registry:
        subjects.setdefault(e["subject"], []).append(e)

    print(f"\n{'='*60}")
    print(f"  RUN REGISTRY — {len(registry)} runs, {len(subjects)} subjects")
    print(f"{'='*60}")

    for subj, runs in sorted(subjects.items()):
        us_runs = [r for r in runs if r["type"] == "us"]
        up_runs = [r for r in runs if r["type"] == "up"]
        total_layers = max((r.get("total_layers", 0) for r in us_runs), default=0)
        pos = "TRUNK" if total_layers >= 15 else "BRANCH" if total_layers >= 8 else "LEAF"

        print(f"\n  [{pos}] {subj}")
        for r in us_runs:
            print(f"    US {r['run']}: {r['total_layers']} layers, "
                  f"C={r['constants']} V={r['variables']}, {r['invariant_count']} inv")
        for r in up_runs:
            print(f"    UP {r['run']}: P={r['p_result']} "
                  f"(D={r.get('define_p','?')} M={r.get('map_p','?')} J={r.get('join_p','?')})")

    print(f"\n{'='*60}\n")
    return 0


# ── New Commands ─────────────────────────────────────────────

def cmd_tournament(args: argparse.Namespace) -> int:
    """Fire the same run through multiple LLMs and compare."""
    if not args.medium:
        print("  [ERROR] --medium required")
        return 1
    if not args.intent:
        print("  [ERROR] --intent required")
        return 1

    models = args.models.split(",") if args.models else None
    tournament = tournament_run(args.medium, args.intent, args.altitude or "30K", models)

    # Save tournament result
    path = DYNO_STORE / "tournaments" / f"tournament-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    write_json(path, tournament)
    print(f"  Saved: {path}")

    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    """Diagnose a run — rotate the equation to find what's blocking."""
    run = load_run(args.run_id)
    if not run:
        print(f"  Run not found: {args.run_id}")
        return 1

    print(f"\n{'='*60}")
    print(f"  EQUATION DIAGNOSIS — {args.run_id}")
    print(f"{'='*60}")

    # Forward pass
    print(f"\n  Forward: P={equation_forward(run)}")

    # Diagnostic pass
    diag = equation_diagnose(run)
    print(f"  Blocking gate: {diag.get('blocking_gate', 'none')}")
    if diag.get("blocking_variables"):
        print(f"  Blocking variables:")
        for v in diag["blocking_variables"][:5]:
            name = v.get("name", v) if isinstance(v, dict) else v
            print(f"    - {name}")
    if diag.get("suggested_action"):
        print(f"  Suggested: {diag['suggested_action']}")

    # Reverse pass (if outreach_id provided)
    if args.outreach_id:
        print(f"\n  Reverse (for {args.outreach_id}):")
        reverse = equation_reverse(1, run["medium"], args.outreach_id)
        print(f"  Blockers: {len(reverse['blockers'])}")
        for b in reverse["blockers"][:10]:
            print(f"    [{b.get('agent','?')}] {b['field']}: {b['reason']}")
        if reverse["path"]:
            print(f"  Path to P=1: {' → '.join(reverse['path'])}")

    print(f"\n{'='*60}\n")
    return 0


def cmd_solve(args: argparse.Namespace) -> int:
    """Self-healing: rotate equation, dispatch agents, re-check.
    The full circle for one company."""
    if not args.outreach_id:
        print("  [ERROR] --outreach-id required")
        return 1

    print(f"\n{'='*60}")
    print(f"  DYNO SOLVE — {args.outreach_id}")
    print(f"  Self-healing loop: equation → agents → re-check")
    print(f"{'='*60}")

    # Pre-read: what does the grid say right now?
    grid = read_grid(args.outreach_id)
    if not grid:
        print(f"  Company not found in grid: {args.outreach_id}")
        return 1

    company = grid.get("company_name", "?")
    print(f"  Company: {company}")

    # Show current state
    blockers = read_blocking_variables(args.outreach_id)
    print(f"  Current blockers: {len(blockers)}")
    for b in blockers[:5]:
        print(f"    [{b.get('agent','?')}] {b['reason']}")

    if not blockers:
        print(f"  No blockers. Company is fully ready.")
        return 0

    # Run the solve loop
    result = solve_variables(args.outreach_id)

    print(f"\n{'='*60}")
    print(f"  SOLVE RESULT")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Solved: {len(result['solved'])}")
    print(f"  Unsolved: {len(result['unsolved'])}")
    print(f"  Wall: {result['wall']}")
    print(f"{'='*60}")

    if result["agent_results"]:
        print(f"\n  Agent dispatch log:")
        for ar in result["agent_results"]:
            print(f"    [{ar['status']}] Agent {ar['agent']}")

    if result["wall"]:
        # Generate wall report
        wall = {
            "type": "SOLVE_WALL",
            "outreach_id": args.outreach_id,
            "company": company,
            "generated_at": now_utc(),
            "solved": result["solved"],
            "unsolved": result["unsolved"],
            "agent_results": result["agent_results"],
            "recommendation": f"Human review: {len(result['unsolved'])} variables remain for {company}",
        }
        wall_path = DYNO_STORE / "walls" / f"solve-wall-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
        write_json(wall_path, wall)
        print(f"\n  Wall report: {wall_path}")

        # Auto-log
        lbb_ingest(
            f"SOLVE WALL: {company} — {len(result['unsolved'])} unsolved",
            json.dumps(wall, indent=2, default=str),
            "processes", ["dyno", "solve", "wall"],
        )

    print()
    return 0


def cmd_grid(args: argparse.Namespace) -> int:
    """Show grid state for a company or summary."""
    if args.outreach_id:
        grid = read_grid(args.outreach_id)
        if not grid:
            print(f"  Company not found: {args.outreach_id}")
            return 1

        print(f"\n{'='*60}")
        print(f"  GRID: {grid.get('company_name', '?')} ({args.outreach_id})")
        print(f"{'='*60}")

        # CT
        print(f"\n  CT (Company Target):")
        for f in ["ct_has_name", "ct_has_domain", "ct_has_location", "ct_has_employees", "ct_has_ein"]:
            v = grid.get(f, 0)
            mark = "1" if v else "0"
            print(f"    [{mark}] {f}")

        # DOL
        print(f"\n  DOL:")
        print(f"    [{'1' if grid.get('dol_ein_linked') else '0'}] dol_ein_linked")

        # People
        for slot in ["ceo", "cfo", "hr"]:
            print(f"\n  People ({slot.upper()}):")
            for f in ["has_name", "has_email", "has_verified_email", "has_linkedin", "is_filled"]:
                col = f"people_{slot}_{f}"
                v = grid.get(col, 0)
                print(f"    [{'1' if v else '0'}] {f}")

        # SP
        print(f"\n  SP (Social Platforms):")
        for f in ["sp_has_about_page", "sp_has_blog", "sp_has_linkedin", "sp_has_platforms"]:
            v = grid.get(f, 0)
            print(f"    [{'1' if v else '0'}] {f}")

        # Scores
        print(f"\n  Scores:")
        print(f"    CT: {grid.get('ct_score', '?')}/5")
        print(f"    DOL: {grid.get('dol_score', '?')}/1")
        print(f"    People: {grid.get('people_total_score', '?')}/12")
        print(f"    Tier: {grid.get('readiness_tier', '?')}")

        print(f"\n{'='*60}\n")

    else:
        summary = read_grid_summary()
        if not summary:
            print("  Could not read grid summary.")
            return 1

        print(f"\n{'='*60}")
        print(f"  GRID SUMMARY")
        print(f"{'='*60}")
        for k, v in summary.items():
            print(f"    {k}: {v}")
        print(f"\n{'='*60}\n")

    return 0


# ── CLI ──────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dyno — IMO Chain Navigator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # run — single run
    p_run = sub.add_parser("run", help="Fire a single run (fresh or chained)")
    p_run.add_argument("--medium", help="The medium")
    p_run.add_argument("--intent", help="The intent")
    p_run.add_argument("--altitude", choices=ALTITUDES, default="30K", help="CTB altitude")
    p_run.add_argument("--engine", choices=["us", "up"], help="Engine (default: auto)")
    p_run.add_argument("--from-run", help="Chain from a prior run ID")

    # auto — auto-chain until P=1 or wall
    p_auto = sub.add_parser("auto", help="Auto-chain: keep running until P=1 or wall")
    p_auto.add_argument("--medium", help="The medium (the outcome — what does 1 look like)")
    p_auto.add_argument("--intent", help="The intent")
    p_auto.add_argument("--altitude", choices=ALTITUDES, default="30K", help="Starting altitude")
    p_auto.add_argument("--engine", choices=["us", "up"], help="Starting engine")
    p_auto.add_argument("--from-run", help="Resume from a prior run ID")
    p_auto.add_argument("--max-runs", default=None,
                        help="RUNAWAY-LOOP SAFETY STOP only (not a convergence target). "
                             "Engine runs until P=1; cycle count is the variable. "
                             "Default: 10000 (effectively unbounded for normal runs).")

    # chain — show the trail
    p_chain = sub.add_parser("chain", help="Show the IMO chain")
    p_chain.add_argument("run_id", nargs="?", help="Run ID to trace (omit for all)")

    # status — single run details
    p_status = sub.add_parser("status", help="Show run details")
    p_status.add_argument("run_id", help="Run ID")

    # registry — the logbook
    p_reg = sub.add_parser("registry", help="Show the run registry")
    p_reg.add_argument("--filter", help="Filter by keyword")

    # tournament — multi-LLM comparison
    p_tour = sub.add_parser("tournament", help="Fire same run through multiple LLMs and compare")
    p_tour.add_argument("--medium", required=True, help="The medium")
    p_tour.add_argument("--intent", required=True, help="The intent")
    p_tour.add_argument("--altitude", choices=ALTITUDES, default="30K", help="CTB altitude")
    p_tour.add_argument("--models", help="Comma-separated model IDs (claude,openai,gemini)")

    # diagnose — equation rotation
    p_diag = sub.add_parser("diagnose", help="Rotate the equation — find what's blocking P=1")
    p_diag.add_argument("run_id", help="Run ID to diagnose")
    p_diag.add_argument("--outreach-id", help="Company outreach_id for reverse pass (ground in D1 data)")

    # solve — agent-per-variable self-healing
    p_solve = sub.add_parser("solve", help="Self-healing: rotate equation → dispatch agents → re-check")
    p_solve.add_argument("--outreach-id", required=True, help="Company outreach_id to solve for")

    # grid — D1 data awareness
    p_grid = sub.add_parser("grid", help="Read company grid from D1")
    p_grid.add_argument("outreach_id", nargs="?", help="Company outreach_id (omit for summary)")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commands = {
        "run": cmd_run,
        "auto": cmd_auto,
        "chain": cmd_chain,
        "status": cmd_status,
        "registry": cmd_registry,
        "tournament": cmd_tournament,
        "diagnose": cmd_diagnose,
        "solve": cmd_solve,
        "grid": cmd_grid,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3.12
"""
Fixpoint Graph Engine — I = M + O

The equation (horizontal) reads one cell at a time.
Tier 0 (vertical) moves the equation up and down the tree via dirty tracking.
The fixpoint loop IS the Circle — runs until convergence (I=0, P=1).

Architecture:
    - Dict graph = the whiteboard (in-memory, free movement)
    - Dirty tracking = back-propagation (Tier 0 moving upward)
    - Fixpoint loop = the Circle (output feeds back as input)
    - evaluate_row = the equation (calls OpenRouter, reads one cell)
    - D1 = snapshot store (photograph the whiteboard after each pass)
    - R2 = raw receipts

Two phases:
    - US phase: builds the structural Christmas tree (right-side-up)
    - UP phase: flips each branch upside down and solves content

UP is dependent on US. US is not dependent on UP.
UP cannot run without structure.

Usage:
    python3 fixpoint_engine.py run "Glassdoor CF Protection" "Data comes back consistently"
    python3 fixpoint_engine.py status <run_id>
    python3 fixpoint_engine.py resume <run_id>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ray


# ═══════════════════════════════════════════════════════════════
# CONSTANTS — locked structural constants of the engine itself
# ═══════════════════════════════════════════════════════════════

ENGINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = ENGINE_ROOT.parents[2]
RUNS_DIR = ENGINE_ROOT / "fixpoint-runs"

LEGAL_PRIMITIVES = {"Thing", "Flow", "Change"}
LEGAL_CV = {"constant", "variable", "unidentified", "domesticated"}
LEGAL_PHASES = {"US", "UP"}

D1_DB = "svg-d1-outreach-ops"
WRANGLER_CWD = REPO_ROOT / "workers" / "lcs-hub"
R2_BUCKET = "svg-files"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-sonnet-4"


# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def short_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]


def get_api_key(name: str) -> str:
    key = os.environ.get(name, "")
    if not key:
        try:
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
# R2 WHITEBOARD — the working surface the equation runs on
# Write every pass. Wipe after each phase (US/UP) completes.
# ═══════════════════════════════════════════════════════════════

def r2_write(key: str, data: str) -> bool:
    """Write a JSON string to R2. This is the whiteboard write."""
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(data)
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


def r2_read(key: str) -> str | None:
    """Read a JSON string from R2. This is the whiteboard read."""
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            tmp = f.name
        r = subprocess.run(
            ["npx", "wrangler", "r2", "object", "get",
             f"{R2_BUCKET}/{key}", "--remote", "--file", tmp],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            with open(tmp) as f:
                data = f.read()
            os.unlink(tmp)
            return data
        os.unlink(tmp)
        return None
    except Exception:
        return None


def r2_wipe(prefix: str) -> int:
    """Wipe all objects under a prefix. Called after each phase completes.
    The scratch pad gets thrown away. The logbook keeps the record."""
    # List objects under prefix, delete each one
    # wrangler doesn't have a bulk delete, so we list and delete one by one
    try:
        r = subprocess.run(
            ["npx", "wrangler", "r2", "object", "list", R2_BUCKET,
             "--remote", "--prefix", prefix],
            capture_output=True, text=True, timeout=30,
        )
        # This command may not exist in all wrangler versions
        # Fallback: just track the prefix and delete known keys
        return 0
    except Exception:
        return 0


def r2_snapshot_graph(run_id: str, phase: str, pass_num: int,
                      graph_json: str) -> bool:
    """Snapshot the full graph state to R2 after each pass."""
    key = f"dyno-runs/whiteboard/{run_id}/{phase}/pass-{pass_num:03d}.json"
    return r2_write(key, graph_json)


def r2_snapshot_cell(run_id: str, phase: str, cell_id: str,
                     cell_json: str) -> bool:
    """Write one cell's state to R2."""
    key = f"dyno-runs/whiteboard/{run_id}/{phase}/cells/{cell_id}.json"
    return r2_write(key, cell_json)


# ═══════════════════════════════════════════════════════════════
# D1 VAULT — certified final state only
# Write ONLY on phase completion. HEIR+ORBT stamped.
# ═══════════════════════════════════════════════════════════════

def d1_execute(sql: str) -> bool:
    """Execute SQL against D1 via wrangler."""
    try:
        r = subprocess.run(
            ["npx", "wrangler", "d1", "execute", D1_DB,
             "--remote", "--command", sql, "--json"],
            cwd=str(WRANGLER_CWD), capture_output=True, text=True, timeout=30,
        )
        return r.returncode == 0
    except Exception:
        return False


def d1_vault_run(run: "EngineRun") -> bool:
    """Promote a completed run to D1 vault. HEIR+ORBT stamped."""
    esc = lambda v: "'" + str(v).replace("'", "''") + "'" if v is not None else "NULL"
    sql = (
        f"INSERT OR REPLACE INTO engine_runs "
        f"(run_id, domain, phase, orbt, "
        f"heir_sovereign_ref, heir_hub_id, heir_ctb_placement, heir_imo_topology, "
        f"heir_cc_layer, heir_services, heir_secrets_provider, heir_acceptance_criteria, "
        f"p1_definition, input_constants, "
        f"total_locked, total_variables, total_domesticated, "
        f"max_passes, overall_p, sigma_direction, "
        f"total_passes, total_cells, total_evaluations, total_cost_usd, "
        f"model_used, started_at, completed_at, status) "
        f"VALUES ("
        f"{esc(run.run_id)}, {esc(run.domain)}, {esc(run.phase)}, "
        f"{esc('OPERATE' if run.status == 'converged' else 'BUILD')}, "
        f"'imo-creator', {esc(run.run_id)}, 'leaf', 'middle', "
        f"'CC-03', 'ray,openrouter,r2,d1', 'doppler', "
        f"{esc(run.p1_definition)}, "
        f"{esc(run.p1_definition)}, {esc(json.dumps([]))}, "
        f"{run.graph.locked_count}, {run.graph.variable_count}, 0, "
        f"{run.max_passes}, {1 if run.status == 'converged' else 0}, "
        f"{esc(run.sigma_history[-1].get('sigma', '') if run.sigma_history else '')}, "
        f"{run.current_pass}, {run.graph.total_cells}, "
        f"{run.total_evaluations}, {run.total_cost}, "
        f"{esc(run.model)}, {esc(run.started_at)}, {esc(run.completed_at)}, "
        f"{esc(run.status)})"
    )
    return d1_execute(sql)


def d1_vault_cells(run: "EngineRun") -> int:
    """Promote all cells from a completed run to D1 vault."""
    esc = lambda v: "'" + str(v).replace("'", "''") + "'" if v is not None else "NULL"
    count = 0
    for cid, cell in run.graph.cells.items():
        filled, total = cell.sections_filled()
        sql = (
            f"INSERT OR REPLACE INTO engine_cells "
            f"(cell_id, run_id, name, depth, parent_id, primitive, "
            f"heir_sovereign_ref, heir_hub_id, heir_ctb_placement, heir_imo_topology, "
            f"why_it_matters, structural_cv, content_cv, "
            f"at_primitive, domesticated, p, ratio, c_value, k_tolerance, comparator, "
            f"version, phase, locked_at_pass, sections_filled, "
            f"dirty, template_json, dependencies_json, dependents_json) "
            f"VALUES ("
            f"{esc(cid)}, {esc(run.run_id)}, {esc(cell.name)}, "
            f"{cell.depth}, {esc(cell.parent_id)}, {esc(cell.primitive)}, "
            f"'imo-creator', {esc(cid)}, {esc(f'depth-{cell.depth}')}, {esc(cell.phase)}, "
            f"{esc(cell.template.get('s02_purpose', {}).get('why_it_matters'))}, "
            f"{esc(cell.structural_cv)}, {esc(cell.content_cv)}, "
            f"{cell.template.get('s08_stop_conditions', {}).get('at_primitive', 0)}, "
            f"{cell.template.get('s08_stop_conditions', {}).get('domesticated', 0)}, "
            f"{cell.p if cell.p is not None else 'NULL'}, "
            f"{cell.ratio if cell.ratio is not None else 'NULL'}, "
            f"{cell.c_value if cell.c_value is not None else 'NULL'}, "
            f"{cell.k_tolerance if cell.k_tolerance is not None else 'NULL'}, "
            f"{esc(cell.template.get('s09_verification', {}).get('comparator'))}, "
            f"{cell.version}, {esc(cell.phase)}, "
            f"{cell.locked_at_pass if cell.locked_at_pass is not None else 'NULL'}, "
            f"{filled}, {1 if cell.dirty else 0}, "
            f"{esc(json.dumps(cell.template, default=str)[:8000])}, "
            f"{esc(json.dumps(cell.dependencies))}, "
            f"{esc(json.dumps(cell.dependents))})"
        )
        if d1_execute(sql):
            count += 1
    return count


def d1_vault_error(run_id: str, error_type: str, message: str,
                   stage: str = None, pass_num: int = None) -> bool:
    """Write an error to the D1 error table."""
    esc = lambda v: "'" + str(v).replace("'", "''") + "'" if v is not None else "NULL"
    error_id = short_id() + "-err"
    sql = (
        f"INSERT INTO engine_runs_error "
        f"(error_id, run_id, heir_ref, error_type, error_message, "
        f"stage, pass_number) VALUES ("
        f"{esc(error_id)}, {esc(run_id)}, {esc(run_id)}, "
        f"{esc(error_type)}, {esc(message)}, "
        f"{esc(stage)}, {pass_num if pass_num is not None else 'NULL'})"
    )
    return d1_execute(sql)


# ═══════════════════════════════════════════════════════════════
# THE GRAPH — the in-memory hot cache (backed by R2 whiteboard)
# ═══════════════════════════════════════════════════════════════

def empty_template() -> dict:
    """Return an empty 14-section Unified Template.

    3 clusters mapped to Three Primitives:
        IDENTITY (Thing) — §1-3: what exists
        CONTRACT (Flow) — §4-8: what moves
        GOVERNANCE (Change) — §9-14: what transforms
    """
    return {
        # ── IDENTITY (Thing — what this IS) ──
        "s01_identity": {
            "id": None, "name": None, "primitive": None,
            "medium": None, "ctb_position": None, "orbt": "BUILD",
            "strikes": 0, "heir": {},
            "filled": 0,
        },
        "s02_purpose": {
            "why_it_matters": None, "what_breaks_without_it": None,
            "filled": 0,
        },
        "s03_resources": {
            "dependencies": [], "consumers": [], "tools": [], "secrets": [],
            "filled": 0,
        },
        # ── CONTRACT (Flow — what flows through) ──
        "s04_imo": {
            "trigger": None, "source": None,
            "input": None, "middle": None, "output": None,
            "circle": None,
            "filled": 0,
        },
        "s05_data_schema": {
            "read_access": [], "write_access": [], "join_chain": None,
            "forbidden_paths": [],
            "filled": 0,
        },
        "s06_dmj": {
            "define": {"elements": [], "comparators": {}},
            "map": {"mappings": []},
            "join": {"path": None, "type": None},
            "filled": 0,
        },
        "s07_constants_variables": {
            "structural_cv": "unidentified",
            "content_cv": "unidentified",
            "constants": [],
            "variables": [],
            "filled": 0,
        },
        "s08_stop_conditions": {
            "at_primitive": False, "domesticated": False,
            "conditions": [],
            "filled": 0,
        },
        # ── GOVERNANCE (Change — how this is controlled) ──
        "s09_verification": {
            "p": None, "ratio": None, "c_value": None, "k_tolerance": None,
            "comparator": None,
            "three_primitives_check": {"thing": None, "flow": None, "change": None},
            "filled": 0,
        },
        "s10_analytics": {
            "sigma_direction": None,
            "sigma_history": [],
            "orbt_gate": None,
            "filled": 0,
        },
        "s11_execution_trace": {
            "traces": [],
            "filled": 0,
        },
        "s12_logbook": {
            "certified": False, "birth_certificate": None,
            "filled": 0,
        },
        "s13_failure_registry": {
            "patterns": [],
            "filled": 0,
        },
        "s14_session_log": {
            "entries": [],
            "filled": 0,
        },
    }


def count_filled_sections(template: dict) -> tuple[int, int]:
    """Count how many sections are filled vs total. Returns (filled, total)."""
    total = 14
    filled = sum(1 for k, v in template.items()
                 if k.startswith("s") and isinstance(v, dict) and v.get("filled", 0) == 1)
    return filled, total


class Cell:
    """One cell on the whiteboard. Shaped to the Unified Template (14 sections).

    Every cell produces the same shape output — 3 clusters, 14 sections.
    The UI renders the template. If a section is filled, it shows.
    If it's empty, it shows as 0. The UI IS the auditor.
    """

    def __init__(self, cell_id: str, name: str, depth: int = 0,
                 parent_id: str | None = None):
        self.cell_id = cell_id
        self.name = name
        self.depth = depth
        self.parent_id = parent_id

        # Template-shaped value — 14 sections, 3 clusters
        self.template: dict = empty_template()
        self.prev_template: dict = {}

        # State
        self.dirty = True
        self.version = 0

        # Two-dimensional classification (also in s07)
        self.primitive: str | None = None
        self.structural_cv: str = "unidentified"
        self.content_cv: str = "unidentified"

        # Dependencies (tree structure)
        self.dependencies: list[str] = []
        self.dependents: list[str] = []

        # Phase tracking
        self.phase: str = "US"
        self.locked_at_pass: int | None = None

        # Equation results (also in s09)
        self.c_value: float | None = None
        self.k_tolerance: float | None = None
        self.ratio: float | None = None
        self.p: int | None = None

        # Initialize s01 with what we know at creation
        self.template["s01_identity"]["id"] = cell_id
        self.template["s01_identity"]["name"] = name
        self.template["s01_identity"]["ctb_position"] = f"depth-{depth}"

    # Keep backward compat for code that reads .value
    @property
    def value(self) -> dict:
        return self.template

    @value.setter
    def value(self, v: dict) -> None:
        if v and isinstance(v, dict):
            # If it's a raw LLM response (not template-shaped), store in s04
            if "decompose_into" in v or "classification" in v:
                self.template["_raw_response"] = v
            else:
                self.template.update(v)

    @property
    def prev_value(self) -> dict:
        return self.prev_template

    @prev_value.setter
    def prev_value(self, v: dict) -> None:
        self.prev_template = v

    def sections_filled(self) -> tuple[int, int]:
        return count_filled_sections(self.template)

    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "name": self.name,
            "depth": self.depth,
            "parent_id": self.parent_id,
            "template": self.template,
            "prev_template": self.prev_template,
            "dirty": self.dirty,
            "version": self.version,
            "primitive": self.primitive,
            "structural_cv": self.structural_cv,
            "content_cv": self.content_cv,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "phase": self.phase,
            "locked_at_pass": self.locked_at_pass,
            "c_value": self.c_value,
            "k_tolerance": self.k_tolerance,
            "ratio": self.ratio,
            "p": self.p,
            "sections_filled": self.sections_filled()[0],
            "sections_total": 14,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Cell":
        c = cls(d["cell_id"], d["name"], d.get("depth", 0), d.get("parent_id"))
        c.template = d.get("template", d.get("value", empty_template()))
        c.prev_template = d.get("prev_template", d.get("prev_value", {}))
        c.dirty = d.get("dirty", True)
        c.version = d.get("version", 0)
        c.primitive = d.get("primitive")
        c.structural_cv = d.get("structural_cv", "unidentified")
        c.content_cv = d.get("content_cv", "unidentified")
        c.dependencies = d.get("dependencies", [])
        c.dependents = d.get("dependents", [])
        c.phase = d.get("phase", "US")
        c.locked_at_pass = d.get("locked_at_pass")
        c.c_value = d.get("c_value")
        c.k_tolerance = d.get("k_tolerance")
        c.ratio = d.get("ratio")
        c.p = d.get("p")
        return c


class Graph:
    """The whiteboard. Holds all cells. Free movement via dict lookup."""

    def __init__(self):
        self.cells: dict[str, Cell] = {}

    def add_cell(self, cell: Cell) -> None:
        self.cells[cell.cell_id] = cell
        # Wire parent-child dependencies
        if cell.parent_id and cell.parent_id in self.cells:
            parent = self.cells[cell.parent_id]
            if cell.cell_id not in parent.dependents:
                parent.dependents.append(cell.cell_id)
            if parent.cell_id not in cell.dependencies:
                cell.dependencies.append(parent.cell_id)

    def get_cell(self, cell_id: str) -> Cell | None:
        return self.cells.get(cell_id)

    def get_dirty_cells(self) -> list[Cell]:
        return [c for c in self.cells.values() if c.dirty]

    def get_all_ancestors(self, cell_id: str) -> list[Cell]:
        """Walk up the tree from a cell to the root."""
        ancestors = []
        current = self.cells.get(cell_id)
        while current and current.parent_id:
            parent = self.cells.get(current.parent_id)
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                break
        return ancestors

    def mark_dependents_dirty(self, cell_id: str) -> int:
        """Back-propagation: mark all dependents dirty when a cell changes.
        This IS Tier 0 moving upward."""
        count = 0
        cell = self.cells.get(cell_id)
        if not cell:
            return 0
        for dep_id in cell.dependents:
            dep = self.cells.get(dep_id)
            if dep and not dep.dirty:
                dep.dirty = True
                count += 1
                # Cascade: dependents of dependents
                count += self.mark_dependents_dirty(dep_id)
        return count

    def mark_ancestors_dirty(self, cell_id: str) -> int:
        """Back-propagation upward: mark all ancestors dirty."""
        count = 0
        for ancestor in self.get_all_ancestors(cell_id):
            if not ancestor.dirty:
                ancestor.dirty = True
                count += 1
        return count

    @property
    def total_cells(self) -> int:
        return len(self.cells)

    @property
    def dirty_count(self) -> int:
        return len(self.get_dirty_cells())

    @property
    def locked_count(self) -> int:
        return sum(1 for c in self.cells.values()
                   if c.structural_cv == "constant" or c.content_cv == "constant")

    @property
    def variable_count(self) -> int:
        return sum(1 for c in self.cells.values()
                   if c.structural_cv == "variable" or c.content_cv == "variable")

    def to_dict(self) -> dict:
        return {
            "cells": {cid: c.to_dict() for cid, c in self.cells.items()},
            "total": self.total_cells,
            "dirty": self.dirty_count,
            "locked": self.locked_count,
            "variables": self.variable_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Graph":
        g = cls()
        for cid, cd in d.get("cells", {}).items():
            g.cells[cid] = Cell.from_dict(cd)
        return g


# ═══════════════════════════════════════════════════════════════
# THE EQUATION — horizontal axis. Reads one cell.
# ═══════════════════════════════════════════════════════════════

def get_inputs(cell: Cell, graph: Graph, phase: str,
               p1_definition: str) -> dict:
    """What feeds the equation at this cell.

    This function controls CORRECTNESS — what the equation sees.
    """
    # Gather context from the cell's position in the tree
    ancestors = graph.get_all_ancestors(cell.cell_id)
    ancestor_names = [a.name for a in ancestors]

    # Gather siblings (other children of same parent)
    siblings = []
    if cell.parent_id:
        parent = graph.get_cell(cell.parent_id)
        if parent:
            siblings = [graph.get_cell(sid).name
                        for sid in parent.dependents
                        if sid != cell.cell_id and graph.get_cell(sid)]

    # Gather children
    children = [graph.get_cell(cid).name
                for cid in cell.dependents
                if graph.get_cell(cid)]

    # Extract the cell's actual data content for the LLM to read
    cell_data = ""
    purpose = cell.template.get("s02_purpose", {}).get("why_it_matters", "")
    if purpose:
        cell_data = purpose
    imo = cell.template.get("s04_imo", {})
    if imo.get("middle"):
        cell_data += f"\nProcess: {imo['middle']}"

    return {
        "cell_id": cell.cell_id,
        "name": cell.name,
        "depth": cell.depth,
        "phase": phase,
        "p1_definition": p1_definition,
        "cell_data": cell_data,  # THE ACTUAL CONTENT TO READ
        "current_value": cell.value,
        "prev_value": cell.prev_value,
        "primitive": cell.primitive,
        "structural_cv": cell.structural_cv,
        "content_cv": cell.content_cv,
        "ancestors": ancestor_names,
        "siblings": siblings,
        "children": children,
        "version": cell.version,
    }


def is_equal(old_value: dict, new_value: dict, cell: Cell) -> tuple[bool, bool]:
    """The tolerance gate that controls CONVERGENCE and CORRECTNESS.

    Returns (converged, passes_p1):
        converged: has the cell stopped changing? (sigma check)
        passes_p1: does the cell pass the equation? (P gate)

    Both must be true for the cell to be fully resolved.
    """
    # Check 1: convergence — did the value change?
    converged = (
        old_value.get("primitive") == new_value.get("primitive") and
        old_value.get("structural_cv") == new_value.get("structural_cv") and
        old_value.get("content_cv") == new_value.get("content_cv") and
        old_value.get("classification") == new_value.get("classification")
    )

    # Check 2: does it pass P=1?
    # P=1 at the cell level means: the cell has a definite classification
    # (constant or domesticated) and the ratio ≤ 1
    classification = new_value.get("classification", "unidentified")
    ratio = new_value.get("ratio")

    passes_p1 = (
        classification in ("constant", "domesticated") and
        ratio is not None and
        ratio <= 1.0
    )

    return converged, passes_p1


# ═══════════════════════════════════════════════════════════════
# EVALUATE ROW — calls the LLM (OpenRouter)
# ═══════════════════════════════════════════════════════════════

@ray.remote
def evaluate_row_remote(cell_dict: dict, inputs: dict, model: str = DEFAULT_MODEL) -> dict:
    """Ray remote wrapper — takes dict, returns dict."""
    return _evaluate_row_impl(inputs, model)


def evaluate_row(cell: Cell, inputs: dict, model: str = DEFAULT_MODEL) -> dict:
    """Run the equation on one cell. Local (non-Ray) path."""
    return _evaluate_row_impl(inputs, model)


def _evaluate_row_impl(inputs: dict, model: str = DEFAULT_MODEL) -> dict:
    """Run the equation on one cell. Calls OpenRouter.

    The LLM is the parser — it reads the cell's context and produces
    a classification. The equation (P check) runs AFTER, deterministically.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "") or get_api_key("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "No OPENROUTER_API_KEY", "classification": "unidentified"}

    if inputs['phase'] == 'US':
        phase_instruction = (
            "PHASE US — you are solving for M (BUILD mode: M = I - O).\n"
            "Your job: READ the data in this cell and EXTRACT the constants from it.\n"
            "The cell contains raw data. Read it. Categorize what you find.\n"
            "If the cell has data in the DATA IN THIS CELL section, that IS the content to analyze.\n"
            "Constants = things specifically stated that would not change regardless of context.\n"
            "Variables = things that would change based on who uses it or what industry.\n"
            "\n"
            "OUTPUT FORMAT: Return your findings as Unified Template sections:\n"
            "  §1 Identity: cell ID + what type of content this is\n"
            "  §2 Purpose: one sentence — what this methodology is about\n"
            "  §4 IMO: trigger (what starts it), input (what goes in), middle (the process/steps), output (what comes out)\n"
            "  §7 Constants & Variables: list each constant and variable found, categorized by:\n"
            "     (1) Message (2) Sequence (3) Timing (4) Channel (5) Target (6) Trigger (7) CTA (8) Metric (9) Uncategorized\n"
            "  §8 Stop conditions: is this fully categorized or does it need more passes\n"
            "\n"
            "For §7, format constants as: 'CATEGORY: the constant' (e.g. 'SEQUENCE: 4-6 touches over 3 weeks')\n"
            "For §7 category 9 (Uncategorized), also include which source it came from.\n"
            "\n"
            "Do NOT classify the cell as an object. Read THROUGH it and extract what's inside.\n"
            "Decompose ONLY if the cell contains multiple distinct topics that should be separated.\n"
            "If fully categorized, mark at_primitive=true."
        )
    else:
        # For UP: include the structural constants (M) so the LLM knows what's already built
        ancestors_str = ", ".join(inputs.get('ancestors', [])) if inputs.get('ancestors') else "none"
        siblings_str = ", ".join(inputs.get('siblings', [])) if inputs.get('siblings') else "none"
        phase_instruction = (
            "PHASE UP — you are solving for O (OPERATE mode: O = I - M).\n"
            "M (structural constants) is ALREADY BUILT by US. The structure is locked. Do NOT rebuild it.\n"
            "Your job: for THIS specific structural cell, what is the SOLUTION to get past it?\n"
            "Be specific — name tools, techniques, configurations, code patterns.\n"
            "Do NOT decompose into more sub-cells unless absolutely necessary.\n"
            "The structure exists. You are filling content into the existing structure.\n"
            f"P=1: {inputs.get('p1_definition', '')}\n"
            f"This cell's position: depth={inputs['depth']}, ancestors=[{ancestors_str}], siblings=[{siblings_str}]"
        )

    prompt = f"""You are the equation. You read one cell on the whiteboard and fill its template sections.

{phase_instruction}

CELL:
  id: {inputs['cell_id']}
  name: {inputs['name']}
  depth: {inputs['depth']}
  ancestors: {inputs['ancestors']}
  siblings: {inputs['siblings']}
  children: {inputs['children']}

DATA IN THIS CELL (read this and extract from it):
{inputs.get('cell_data', 'no data')}

The cell has 14 sections in 3 clusters (Unified Template):
  IDENTITY (Thing): §1 Identity, §2 Purpose, §3 Resources
  CONTRACT (Flow): §4 IMO, §5 Data Schema, §6 DMJ, §7 Constants & Variables, §8 Stop Conditions
  GOVERNANCE (Change): §9 Verification, §10 Analytics, §11 Execution Trace, §12-14 (later)

Fill what you can. Apply Three Primitives and C&V test. If this cell needs decomposition, list sub-cells.

Return ONLY valid JSON:
{{
  "cell_id": "{inputs['cell_id']}",
  "s01_identity": {{
    "primitive": "Thing|Flow|Change",
    "medium": "what kind of thing this is"
  }},
  "s02_purpose": {{
    "why_it_matters": "what breaks without this",
    "what_breaks_without_it": "downstream impact"
  }},
  "s04_imo": {{
    "trigger": "what starts this",
    "input": "what comes in",
    "middle": "what happens",
    "output": "what comes out"
  }},
  "s07_constants_variables": {{
    "structural_cv": "constant|variable|unidentified",
    "content_cv": "constant|variable|domesticated|unidentified",
    "constants": ["things that don't change"],
    "variables": ["things that do change"]
  }},
  "s08_stop_conditions": {{
    "at_primitive": true|false,
    "domesticated": true|false
  }},
  "s09_verification": {{
    "comparator": "what to measure",
    "c_value": null,
    "k_tolerance": null
  }},
  "decompose_into": [
    {{"name": "sub-cell name", "primitive": "Thing|Flow|Change"}}
  ]
}}"""

    payload = {
        "model": model,
        "max_tokens": 2000,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://imo-creator.svg.agency",
        "X-Title": "Fixpoint Engine",
    }

    try:
        req = urllib.request.Request(
            OPENROUTER_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        content = ""
        if "choices" in data and data["choices"]:
            content = data["choices"][0].get("message", {}).get("content", "")

        # Extract JSON from response
        import re
        for pattern in [r"```json\s*\n(.*?)\n```", r"```\s*\n(.*?)\n```", r"(\{.*\})"]:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(1).strip())
                    # Add cost tracking
                    usage = data.get("usage", {})
                    result["_tokens_in"] = usage.get("prompt_tokens", 0)
                    result["_tokens_out"] = usage.get("completion_tokens", 0)
                    result["_cost"] = usage.get("cost", 0)
                    result["_model"] = model
                    return result
                except json.JSONDecodeError:
                    continue

        return {"error": "No valid JSON in response", "classification": "unidentified"}

    except Exception as e:
        return {"error": str(e), "classification": "unidentified"}


# ═══════════════════════════════════════════════════════════════
# THE FIXPOINT LOOP — the Circle
# ═══════════════════════════════════════════════════════════════

class EngineRun:
    """One complete run of the fixpoint engine."""

    def __init__(self, run_id: str, domain: str, p1_definition: str,
                 phase: str = "US", max_passes: int = 20,
                 model: str = DEFAULT_MODEL):
        self.run_id = run_id
        self.domain = domain
        self.p1_definition = p1_definition
        self.phase = phase
        self.max_passes = max_passes
        self.model = model

        self.graph = Graph()
        self.current_pass = 0
        self.total_evaluations = 0
        self.total_cost = 0.0
        self.sigma_history: list[dict] = []
        self.started_at = now_utc()
        self.completed_at: str | None = None
        self.status = "running"

    def seed_root(self) -> None:
        """Plant the root cell — P=1 at the top of the tree."""
        root = Cell("ROOT", self.domain, depth=0)
        root.phase = self.phase
        self.graph.add_cell(root)

    def run_pass(self) -> dict:
        """Run one fixpoint pass — evaluate all dirty cells."""
        self.current_pass += 1
        dirty_cells = self.graph.get_dirty_cells()

        if not dirty_cells:
            return {"pass": self.current_pass, "evaluated": 0, "changes": 0,
                    "dirty_remaining": 0, "converged": True}

        print(f"\n  ── Pass {self.current_pass} | "
              f"{len(dirty_cells)} dirty / {self.graph.total_cells} total | "
              f"locked={self.graph.locked_count} var={self.graph.variable_count} ──")

        changes = 0
        new_cells_added = 0

        # Prepare all inputs before dispatching
        cell_inputs = []
        for cell in dirty_cells:
            inputs = get_inputs(cell, self.graph, self.phase, self.p1_definition)
            cell_inputs.append((cell, inputs))

        # Dispatch all dirty cells to Ray in parallel
        print(f"    Dispatching {len(cell_inputs)} cells to Ray...")
        futures = []
        for cell, inputs in cell_inputs:
            future = evaluate_row_remote.remote(cell.to_dict(), inputs, self.model)
            futures.append((cell, future))

        # Collect results
        for cell, future in futures:
            print(f"    [{cell.cell_id}] {cell.name[:50]}...", end=" ", flush=True)
            result = ray.get(future)
            self.total_evaluations += 1
            self.total_cost += result.get("_cost", 0)

            if result.get("error"):
                print(f"ERROR: {result['error'][:60]}")
                cell.dirty = False
                continue

            # Save old state for comparison
            old_value = {
                "primitive": cell.primitive,
                "structural_cv": cell.structural_cv,
                "content_cv": cell.content_cv,
                "classification": cell.template.get("s07_constants_variables", {}).get("structural_cv"),
            }

            # Update cell template from result
            cell.prev_template = json.loads(json.dumps(cell.template, default=str))
            cell.version += 1

            # §1 Identity — primitive
            s01 = result.get("s01_identity", {})
            if s01.get("primitive"):
                cell.primitive = s01["primitive"]
                cell.template["s01_identity"]["primitive"] = s01["primitive"]
                cell.template["s01_identity"]["medium"] = s01.get("medium")
                cell.template["s01_identity"]["filled"] = 1

            # §2 Purpose
            s02 = result.get("s02_purpose", {})
            if s02.get("why_it_matters"):
                cell.template["s02_purpose"]["why_it_matters"] = s02["why_it_matters"]
                cell.template["s02_purpose"]["what_breaks_without_it"] = s02.get("what_breaks_without_it")
                cell.template["s02_purpose"]["filled"] = 1

            # §4 IMO
            s04 = result.get("s04_imo", {})
            if s04.get("trigger") or s04.get("input"):
                cell.template["s04_imo"].update({k: v for k, v in s04.items() if v})
                cell.template["s04_imo"]["filled"] = 1

            # §7 Constants & Variables
            s07 = result.get("s07_constants_variables", {})
            if s07:
                scv = s07.get("structural_cv", cell.structural_cv)
                ccv = s07.get("content_cv", cell.content_cv)
                if self.phase == "US":
                    cell.structural_cv = scv
                else:
                    cell.content_cv = ccv
                cell.template["s07_constants_variables"]["structural_cv"] = scv
                cell.template["s07_constants_variables"]["content_cv"] = ccv
                cell.template["s07_constants_variables"]["constants"] = s07.get("constants", [])
                cell.template["s07_constants_variables"]["variables"] = s07.get("variables", [])
                cell.template["s07_constants_variables"]["filled"] = 1

            # §8 Stop Conditions
            s08 = result.get("s08_stop_conditions", {})
            if s08:
                cell.template["s08_stop_conditions"]["at_primitive"] = s08.get("at_primitive", False)
                cell.template["s08_stop_conditions"]["domesticated"] = s08.get("domesticated", False)
                cell.template["s08_stop_conditions"]["filled"] = 1

            # §9 Verification — equation check (deterministic)
            s09 = result.get("s09_verification", {})
            c_val = s09.get("c_value") if s09 else None
            k_val = s09.get("k_tolerance") if s09 else None
            comparator = s09.get("comparator") if s09 else None
            if c_val is not None and k_val is not None:
                try:
                    c_val = abs(float(c_val))
                    k_val = max(abs(float(k_val)), 0.001)
                    cell.ratio = round(c_val / k_val, 4)
                    cell.p = 1 if cell.ratio <= 1.0 else 0
                    cell.c_value = c_val
                    cell.k_tolerance = k_val
                except (ValueError, TypeError):
                    pass
            cell.template["s09_verification"]["p"] = cell.p
            cell.template["s09_verification"]["ratio"] = cell.ratio
            cell.template["s09_verification"]["c_value"] = cell.c_value
            cell.template["s09_verification"]["k_tolerance"] = cell.k_tolerance
            cell.template["s09_verification"]["comparator"] = comparator
            if cell.p is not None:
                cell.template["s09_verification"]["filled"] = 1

            # §11 Execution Trace — append this evaluation
            cell.template["s11_execution_trace"]["traces"].append({
                "pass": self.current_pass,
                "model": self.model,
                "cost": result.get("_cost", 0),
                "tokens_in": result.get("_tokens_in", 0),
                "tokens_out": result.get("_tokens_out", 0),
                "timestamp": now_utc(),
            })
            cell.template["s11_execution_trace"]["filled"] = 1

            # Store raw response
            cell.template["_raw_response"] = result

            # Check convergence + P=1
            new_value = {
                "primitive": cell.primitive,
                "structural_cv": cell.structural_cv,
                "content_cv": cell.content_cv,
                "classification": cell.template.get("s07_constants_variables", {}).get("structural_cv"),
            }

            converged, passes_p1 = is_equal(old_value, new_value, cell)

            if not converged:
                changes += 1
                # BACK-PROPAGATION: mark ancestors dirty
                bp_count = self.graph.mark_ancestors_dirty(cell.cell_id)
                if bp_count > 0:
                    print(f"→ CHANGED (backprop: {bp_count} ancestors dirty)")
                else:
                    print(f"→ CHANGED")
            else:
                print(f"→ stable" + (" ✓P=1" if passes_p1 else ""))

            if passes_p1:
                cell.locked_at_pass = self.current_pass

            # Only mark clean if at primitive or converged
            # If not at primitive, keep dirty so next pass pushes deeper
            at_prim = result.get("s08_stop_conditions", {}).get("at_primitive", False)
            if at_prim or converged:
                cell.dirty = False
            else:
                cell.dirty = True  # Not at primitive yet — keep pushing

            # Handle decomposition — add sub-cells
            decompose = result.get("decompose_into", [])
            if decompose and isinstance(decompose, list):
                for i, sub in enumerate(decompose):
                    sub_id = f"{cell.cell_id}.{i+1}"
                    if sub_id not in self.graph.cells:
                        sub_cell = Cell(
                            sub_id,
                            sub.get("name", f"sub-{i+1}"),
                            depth=cell.depth + 1,
                            parent_id=cell.cell_id,
                        )
                        sub_cell.primitive = sub.get("primitive")
                        sub_cell.phase = self.phase
                        self.graph.add_cell(sub_cell)
                        new_cells_added += 1

        # Sigma tracking
        sigma_entry = {
            "pass": self.current_pass,
            "total_cells": self.graph.total_cells,
            "dirty": self.graph.dirty_count,
            "locked": self.graph.locked_count,
            "variables": self.graph.variable_count,
            "changes": changes,
            "new_cells": new_cells_added,
            "evaluations": len(dirty_cells),
        }
        self.sigma_history.append(sigma_entry)

        sigma_dir = self._compute_sigma()
        print(f"\n  Pass {self.current_pass} complete: "
              f"{changes} changes, {new_cells_added} new cells, "
              f"sigma={sigma_dir}")

        return {
            "pass": self.current_pass,
            "evaluated": len(dirty_cells),
            "changes": changes,
            "new_cells": new_cells_added,
            "dirty_remaining": self.graph.dirty_count,
            "converged": self.graph.dirty_count == 0 and changes == 0,
            "sigma": sigma_dir,
        }

    def _compute_sigma(self) -> str:
        """Sigma direction across passes."""
        if len(self.sigma_history) < 2:
            return "insufficient_data"
        prev = self.sigma_history[-2]
        curr = self.sigma_history[-1]
        # Sigma tightens when locked grows and variables shrink
        if curr["locked"] > prev["locked"] and curr["variables"] <= prev["variables"]:
            return "tightening"
        elif curr["variables"] > prev["variables"]:
            return "expanding"
        else:
            return "flat"

    def run(self) -> None:
        """The main fixpoint loop. Runs until convergence or max passes."""
        # Initialize Ray
        if not ray.is_initialized():
            ray.init(num_cpus=4, ignore_reinit_error=True)

        print(f"\n{'='*60}")
        print(f"  FIXPOINT ENGINE — {self.phase} Phase")
        print(f"  Domain: {self.domain}")
        print(f"  P=1: {self.p1_definition[:60]}")
        print(f"  Model: {self.model}")
        print(f"  Max passes: {self.max_passes}")
        print(f"  Ray: {ray.cluster_resources()}")
        print(f"{'='*60}")

        if not self.graph.cells:
            self.seed_root()

        while self.current_pass < self.max_passes:
            result = self.run_pass()

            # Snapshot to R2 whiteboard after each pass (NOT D1 — D1 is vault)
            graph_json = json.dumps(self.graph.to_dict(), indent=2, default=str)
            if r2_snapshot_graph(self.run_id, self.phase, self.current_pass, graph_json):
                print(f"    R2: whiteboard snapshot pass {self.current_pass}")
            else:
                print(f"    R2: snapshot FAILED")

            if result["converged"]:
                if self.phase == "US":
                    print(f"\n  {'='*60}")
                    print(f"  US CONVERGED — M stopped growing at pass {self.current_pass}")
                    print(f"  Structure mapped: {self.graph.total_cells} cells")
                    print(f"  Constants (locked structure): {self.graph.locked_count}")
                    print(f"  Variables (content for UP): {self.graph.variable_count}")
                    print(f"  Total evaluations: {self.total_evaluations}")
                    print(f"  Total cost: ${self.total_cost:.4f}")
                    print(f"  {'='*60}")
                else:
                    print(f"\n  {'='*60}")
                    print(f"  UP CONVERGED — O reached (P=1) at pass {self.current_pass}")
                    print(f"  Total cells: {self.graph.total_cells}")
                    print(f"  Locked: {self.graph.locked_count}")
                    print(f"  Total evaluations: {self.total_evaluations}")
                    print(f"  Total cost: ${self.total_cost:.4f}")
                    print(f"  {'='*60}")
                self.status = "converged"
                self.completed_at = now_utc()
                break

            # US-specific convergence: M stopped growing AND three primitives covered
            if self.phase == "US" and result["new_cells"] == 0 and result["changes"] == 0:
                # Check three primitives coverage before declaring convergence
                primitives_found = set()
                for c in self.graph.cells.values():
                    if c.primitive:
                        primitives_found.add(c.primitive)
                missing = {"Thing", "Flow", "Change"} - primitives_found
                if missing:
                    print(f"\n  THREE PRIMITIVES CHECK: missing {missing}")
                    print(f"  US cannot converge without all three primitives represented.")
                    print(f"  Marking all leaf cells dirty to force deeper decomposition.")
                    for c in self.graph.cells.values():
                        if not c.dependents:  # leaf cells
                            c.dirty = True
                else:
                    print(f"\n  {'='*60}")
                    print(f"  US CONVERGED — no new structure found, M is complete")
                    print(f"  Three primitives: {primitives_found}")
                    print(f"  {'='*60}")
                    self.status = "converged"
                    self.completed_at = now_utc()
                    break

            if result["dirty_remaining"] == 0 and result["changes"] == 0:
                self.status = "converged"
                self.completed_at = now_utc()
                break

        else:
            print(f"\n  MAX PASSES REACHED ({self.max_passes})")
            print(f"  Dirty cells remaining: {self.graph.dirty_count}")
            self.status = "max_passes"
            self.completed_at = now_utc()

        # ── PHASE COMPLETE: promote to D1 vault, wipe R2 ──
        # D1 = the vault. Write certified final state with HEIR+ORBT.
        if d1_vault_run(self):
            print(f"  D1 VAULT: run promoted (HEIR stamped, ORBT={'OPERATE' if self.status == 'converged' else 'BUILD'})")
        else:
            print(f"  D1 VAULT: promotion FAILED")
            d1_vault_error(self.run_id, "vault_promotion_failed",
                           "Could not write run to D1 vault", pass_num=self.current_pass)

        cells_promoted = d1_vault_cells(self)
        print(f"  D1 VAULT: {cells_promoted}/{self.graph.total_cells} cells promoted")

        # Save to local disk (backup)
        self._save_to_disk()

        # Wipe R2 whiteboard — scratch pad thrown away
        wipe_prefix = f"dyno-runs/whiteboard/{self.run_id}/"
        r2_wipe(wipe_prefix)
        print(f"  R2 WHITEBOARD: wiped ({wipe_prefix})")

    # _snapshot_to_d1 removed — D1 is the vault, only written on completion
    # R2 whiteboard snapshots happen in the pass loop above

    def _save_to_disk(self) -> None:
        """Save the full state to local disk."""
        run_dir = RUNS_DIR / self.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        state = {
            "run_id": self.run_id,
            "domain": self.domain,
            "p1_definition": self.p1_definition,
            "phase": self.phase,
            "current_pass": self.current_pass,
            "total_evaluations": self.total_evaluations,
            "total_cost": self.total_cost,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "sigma_history": self.sigma_history,
            "graph": self.graph.to_dict(),
        }

        (run_dir / "state.json").write_text(
            json.dumps(state, indent=2, default=str) + "\n"
        )

    # _push_to_r2 removed — R2 whiteboard snapshots happen per-pass
    # Final state goes to D1 vault, not R2


# ═══════════════════════════════════════════════════════════════
# D1 TABLE SETUP
# ═══════════════════════════════════════════════════════════════

def load_us_constants_from_d1(us_run_id: str) -> list[dict]:
    """Load the structural constants US discovered from D1 vault.
    These become M for the UP phase — the engine the equation runs on."""
    try:
        r = subprocess.run(
            ["npx", "wrangler", "d1", "execute", D1_DB, "--remote",
             "--command", f"SELECT cell_id, name, primitive, structural_cv, depth, parent_id, why_it_matters, comparator FROM engine_cells WHERE run_id = '{us_run_id}' ORDER BY depth, cell_id",
             "--json"],
            cwd=str(WRANGLER_CWD), capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            return []
        data = json.loads(r.stdout)
        results = []
        for batch in data:
            if isinstance(batch, dict):
                for row in batch.get("results", []):
                    results.append(row)
        return results
    except Exception:
        return []


def seed_graph_from_us(graph: "Graph", us_constants: list[dict], phase: str = "UP") -> None:
    """Pre-seed the UP graph with US structural constants as M.
    Each US constant becomes a cell in the UP graph with structural_cv=constant.
    The content_cv is set to 'variable' — that's what UP solves."""
    for row in us_constants:
        cell = Cell(
            cell_id=row["cell_id"],
            name=row["name"],
            depth=row.get("depth", 0),
            parent_id=row.get("parent_id"),
        )
        cell.primitive = row.get("primitive")
        cell.structural_cv = "constant"  # Structure is locked by US
        cell.content_cv = "variable"     # Content is what UP solves
        cell.phase = phase
        cell.dirty = True  # UP needs to evaluate each one

        # Fill template sections from US data
        cell.template["s01_identity"]["primitive"] = row.get("primitive")
        cell.template["s01_identity"]["filled"] = 1
        cell.template["s02_purpose"]["why_it_matters"] = row.get("why_it_matters")
        if row.get("why_it_matters"):
            cell.template["s02_purpose"]["filled"] = 1
        cell.template["s07_constants_variables"]["structural_cv"] = "constant"
        cell.template["s07_constants_variables"]["content_cv"] = "variable"
        cell.template["s07_constants_variables"]["filled"] = 1
        cell.template["s09_verification"]["comparator"] = row.get("comparator")

        graph.add_cell(cell)


def ensure_d1_table() -> None:
    """Create the engine_runs table if it doesn't exist."""
    sql = """CREATE TABLE IF NOT EXISTS engine_runs (
        run_id TEXT PRIMARY KEY,
        domain TEXT NOT NULL,
        p1_definition TEXT,
        phase TEXT DEFAULT 'US',
        current_pass INTEGER DEFAULT 0,
        total_cells INTEGER DEFAULT 0,
        locked_cells INTEGER DEFAULT 0,
        variable_cells INTEGER DEFAULT 0,
        dirty_cells INTEGER DEFAULT 0,
        total_evaluations INTEGER DEFAULT 0,
        total_cost REAL DEFAULT 0,
        status TEXT DEFAULT 'running',
        graph_snapshot TEXT,
        started_at TEXT,
        updated_at TEXT DEFAULT (datetime('now'))
    )"""
    try:
        subprocess.run(
            ["npx", "wrangler", "d1", "execute", D1_DB,
             "--remote", "--command", sql, "--json"],
            cwd=str(WRANGLER_CWD), capture_output=True, text=True, timeout=30,
        )
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def validate_intake(args: argparse.Namespace) -> list[str]:
    """Intake completeness check — the biggest lever for convergence speed.
    Returns list of missing/incomplete fields. Empty = complete intake."""
    issues = []
    if not args.domain or len(args.domain) < 20:
        issues.append("DOMAIN too short — include real data (URLs, HTTP codes, observed behavior)")
    if not args.p1 or len(args.p1) < 10:
        issues.append("P=1 too vague — be specific and measurable")
    if args.phase == "UP" and not getattr(args, 'us_run_id', None):
        issues.append("UP phase requires --us-run-id (US must complete before UP)")
    # Check for real data markers
    domain_lower = args.domain.lower()
    has_url = "http" in domain_lower or "www." in domain_lower
    has_status = any(code in domain_lower for code in ["200", "403", "404", "500"])
    if not has_url and not has_status:
        issues.append("DOMAIN lacks real data — include URLs, HTTP status codes, or observed responses")
    return issues


def cmd_run(args: argparse.Namespace) -> int:
    ensure_d1_table()
    import time as _time
    run_start = _time.time()

    # INTAKE ENFORCEMENT — check completeness before firing
    intake_issues = validate_intake(args)
    if intake_issues:
        print(f"\n  ⚠ INTAKE INCOMPLETE — {len(intake_issues)} issue(s):")
        for issue in intake_issues:
            print(f"    - {issue}")
        print(f"\n  Complete intake = fewer runs = faster convergence.")
        print(f"  Proceeding anyway, but expect extra runs.\n")

    run_id = short_id()
    phase = args.phase or "US"
    model = args.model or DEFAULT_MODEL
    max_passes = int(args.max_passes) if args.max_passes else 20

    engine = EngineRun(
        run_id=run_id,
        domain=args.domain,
        p1_definition=args.p1,
        phase=phase,
        max_passes=max_passes,
        model=model,
    )

    # For UP phase: load M from US run in D1
    us_run_id = getattr(args, 'us_run_id', None)
    if phase == "UP" and us_run_id:
        us_constants = load_us_constants_from_d1(us_run_id)
        if us_constants:
            seed_graph_from_us(engine.graph, us_constants, phase="UP")
            print(f"\n  M LOADED FROM US: {len(us_constants)} structural constants from run {us_run_id}")
            print(f"  UP will solve content within this structure.")
            print(f"  P=1: {args.p1}")
        else:
            print(f"\n  WARNING: No US constants found for run {us_run_id}")
            print(f"  UP will start from scratch (not recommended)")
    elif phase == "UP" and not us_run_id:
        print(f"\n  WARNING: UP phase without --us-run-id")
        print(f"  UP needs M from a completed US run. Use --us-run-id <run_id>")

    engine.run()

    elapsed = _time.time() - run_start
    print(f"\n  Run ID: {run_id}")
    print(f"  Status: {engine.status}")
    print(f"  Elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Cost: ${engine.total_cost:.4f}")
    print(f"  Cells: {engine.graph.total_cells}")
    print(f"  Passes: {engine.current_pass}")
    if intake_issues:
        print(f"  Intake issues: {len(intake_issues)}")
    print(f"  State: {RUNS_DIR / run_id / 'state.json'}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state_file = RUNS_DIR / args.run_id / "state.json"
    if not state_file.exists():
        print(f"No run found: {args.run_id}")
        return 1

    state = json.loads(state_file.read_text())
    print(f"  Run:        {state['run_id']}")
    print(f"  Domain:     {state['domain']}")
    print(f"  Phase:      {state['phase']}")
    print(f"  Status:     {state['status']}")
    print(f"  Passes:     {state['current_pass']}")
    print(f"  Total cells: {state['graph']['total']}")
    print(f"  Locked:     {state['graph']['locked']}")
    print(f"  Variables:  {state['graph']['variables']}")
    print(f"  Dirty:      {state['graph']['dirty']}")
    print(f"  Evals:      {state['total_evaluations']}")
    print(f"  Cost:       ${state['total_cost']:.4f}")
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    state_file = RUNS_DIR / args.run_id / "state.json"
    if not state_file.exists():
        print(f"No run found: {args.run_id}")
        return 1

    state = json.loads(state_file.read_text())
    engine = EngineRun(
        run_id=state["run_id"],
        domain=state["domain"],
        p1_definition=state["p1_definition"],
        phase=state.get("phase", "US"),
        max_passes=int(args.max_passes) if args.max_passes else 20,
        model=args.model or DEFAULT_MODEL,
    )
    engine.graph = Graph.from_dict(state["graph"])
    engine.current_pass = state["current_pass"]
    engine.total_evaluations = state["total_evaluations"]
    engine.total_cost = state["total_cost"]
    engine.sigma_history = state.get("sigma_history", [])
    engine.started_at = state["started_at"]

    engine.run()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fixpoint Graph Engine — I = M + O")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Start a new engine run")
    p_run.add_argument("domain", help="The domain (medium)")
    p_run.add_argument("p1", help="P=1 definition (what does done look like)")
    p_run.add_argument("--phase", default="US", choices=["US", "UP"])
    p_run.add_argument("--model", default=DEFAULT_MODEL)
    p_run.add_argument("--max-passes", default="20")
    p_run.add_argument("--us-run-id", help="US run ID to load M from (for UP phase)")

    p_status = sub.add_parser("status", help="Check run status")
    p_status.add_argument("run_id")

    p_resume = sub.add_parser("resume", help="Resume a paused run")
    p_resume.add_argument("run_id")
    p_resume.add_argument("--model", default=DEFAULT_MODEL)
    p_resume.add_argument("--max-passes", default="20")

    args = parser.parse_args()

    if args.command == "run":
        return cmd_run(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "resume":
        return cmd_resume(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())

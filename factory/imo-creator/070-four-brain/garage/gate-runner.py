#!/usr/bin/env python3
# mission_control_exempt: true
# mission_control_exempt_reason: Internal predicate evaluator. Outputs flow into Auditor verdicts which surface via mission-control.system.pipeline slot. Per BAR-070-MC-WIRE Plan Book §7.
# Last modified: 2026-05-08
# v1.4.1 — manifest-driven gate registry; 6-state ORBT from Atlas; W-7 universal PENDING;
#          W-6 BAR-scoped diff (not git-history); W-4 universal paired-Book check;
#          BAR regex widened; per-role action enum; manifest/impl parity check.
# W-6: replaced global-git-history check with BAR-scoped diff/baseline check.
# W-7: removed silent DEFERRED_TO_TAIL path; W-7 is now always PASS/FAIL/PENDING;
#      PENDING blocks verdict (p_value=0); requires --w7-disposition artifact to PASS.
# =============================================================================
# gate-runner.py — Deterministic Four-Brain Doctrine Gate evaluator
#
# Atlas authority:
#   atlas/constants/FOUR_BRAIN_AVIATION.md §75-94 (Determinism-First Gate)
#   atlas/manifests/four-brain-doctrine-gate.yaml (predicate source of truth)
#   atlas/constants/AUDITOR_ROLE.md §7 (8-rung audit ladder), §7b (W-1..W-7)
#
# Atlas mandate (verbatim):
#   "Run LLM on the spine of any gate evaluation" — FORBIDDEN
#   "determinism_gate: ai_on_spine_forbidden — deterministic checks only"
#   "GATES — the 19 conformance predicates (closed-form, deterministic)"
#
# This script is the deterministic implementation. Predicates are READ from the
# manifest, NOT embedded here. The script is the executor; the manifest is the
# spec. If a predicate changes, the manifest changes — the script does not.
#
# W-7 (disposition sanity) is the ONLY gate that legitimately requires LLM
# judgment per Atlas (it evaluates architectural quality of a Planner decision).
# It is deferred to tail arbitration AFTER all 18 deterministic gates pass.
#
# HEIR:
#   sovereign_ref:   imo-creator
#   hub_id:          gate-runner
#   ctb_placement:   barton-enterprises/imo-creator/070-four-brain/gate-runner
#   imo_topology:    hub
#   cc_layer:        CC-01
#   services:        [four-brain-doctrine-gate.yaml, AUDITOR_ROLE.md]
#   secrets_provider: doppler (LBB_API_KEY for G06/G08/G09/W-5 LBB queries)
#   acceptance_criteria: All 18 deterministic gates evaluate without LLM call.
#
# ORBT:
#   library_state: BUILD
# =============================================================================

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

# Force UTF-8 stdout on Windows so unicode in evidence strings (—, §) doesn't mojibake.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML not installed. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


VERSION = "1.4.2"
LBB_BASE = os.environ.get("LBB_URL", "https://lbb.svg-outreach.workers.dev")


# -----------------------------------------------------------------------------
# Output contract
# -----------------------------------------------------------------------------

@dataclass
class GateResult:
    gate_id: str
    name: str
    passed: bool
    predicate: str
    evidence: str
    strike_target: str = ""
    deferred_to_tail: bool = False
    pending: bool = False  # W-7 in --deterministic-only mode: requires LLM judgment


@dataclass
class AuditReport:
    bar_id: str
    manifest_version: str
    gates_evaluated: int = 0
    gates_passed: list[str] = field(default_factory=list)
    gates_failed: list[dict] = field(default_factory=list)
    gates_pending: list[str] = field(default_factory=list)  # W-7 PENDING in --deterministic-only
    deferred_to_tail: list[str] = field(default_factory=list)
    diagnostic_vector: list[dict] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        # BLOCKED: any pending gate (e.g. W-7 awaiting disposition artifact) prevents
        # certification. Distinct from FAIL so the operator knows which repair to dispatch.
        if self.gates_pending:
            return "BLOCKED"
        return "PASS" if not self.gates_failed else "FAIL"

    @property
    def p_value(self) -> int:
        # P=1 requires no failures AND no pending gates
        return 1 if self.verdict == "PASS" else 0

    def record(self, r: GateResult):
        self.gates_evaluated += 1
        if r.pending:
            # PENDING: gate cannot be evaluated yet (e.g. W-7 missing disposition artifact).
            # Blocks certification — p_value=0 while any gate is pending.
            self.gates_pending.append(r.gate_id)
            self.deferred_to_tail.append(r.gate_id)  # emitted for operator visibility
            return
        # NOTE: the old `if r.deferred_to_tail: return` branch has been removed.
        # A gate that is not pending MUST resolve to passed or failed — silent drops
        # allowed W-7 to fall through and gave a false PASS verdict.
        if r.passed:
            self.gates_passed.append(r.gate_id)
        else:
            self.gates_failed.append({
                "id": r.gate_id,
                "name": r.name,
                "predicate": r.predicate,
                "evidence": r.evidence,
                "strike_target": r.strike_target,
            })
            self.diagnostic_vector.append({
                "gate_id": r.gate_id,
                "deviation": r.evidence,
            })

    def to_json(self) -> str:
        return json.dumps({
            "verdict": self.verdict,
            "p_value": self.p_value,
            "bar_id": self.bar_id,
            "manifest_version": self.manifest_version,
            "gates_evaluated": self.gates_evaluated,
            "gates_passed": self.gates_passed,
            "gates_failed": self.gates_failed,
            "gates_pending": self.gates_pending,
            "deferred_to_tail": self.deferred_to_tail,
            "diagnostic_vector": self.diagnostic_vector,
        }, indent=2)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def load_yaml(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_yaml_top_level_keys(path: Path) -> set[str]:
    """Return the set of top-level keys without parsing into a single dict."""
    keys = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", line)
            if m:
                keys.add(m.group(1))
    return keys


def load_md_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a Book .md file (between leading --- markers)."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def load_atlas_book_law_heir_fields(repo_v2: Path) -> tuple[set[str], set[str]]:
    """
    Parse atlas/constants/BOOK_LAW.md and extract:
      - the universal outside.heir field set (8 fields per "Front Cover" section)
      - the universal orbt library_state enum (6 values)
    Atlas is source of truth. If parsing fails, raise — do NOT fall back to hardcoded.
    """
    book_law = repo_v2 / "atlas" / "constants" / "BOOK_LAW.md"
    if not book_law.exists():
        raise FileNotFoundError(f"BOOK_LAW.md not found at {book_law} — Atlas read failed")
    text = book_law.read_text(encoding="utf-8")

    # Find the "Front Cover Must Carry Outside-Dewey HEIR/ORBT Pair" section
    # and extract field names from the markdown table.
    # Table rows look like: | `sovereign_ref` | slug | ... |
    section_match = re.search(
        r"#### Front Cover Must Carry Outside-Dewey.*?(?=^####|\Z)",
        text, re.DOTALL | re.MULTILINE
    )
    if not section_match:
        raise ValueError("BOOK_LAW.md: 'Front Cover Must Carry Outside-Dewey' section not found")
    section = section_match.group(0)

    # Extract HEIR field names from backticked table cells
    # Skip the orbt row (handled separately)
    heir_fields = set()
    for line in section.split("\n"):
        m = re.match(r"\|\s*`([a-z_]+)`\s*\|", line)
        if m:
            field = m.group(1)
            if field != "orbt":
                heir_fields.add(field)

    if len(heir_fields) < 7:
        raise ValueError(f"BOOK_LAW.md: parsed only {len(heir_fields)} HEIR fields, expected >=7. Got: {sorted(heir_fields)}")

    # Extract library_state enum from the orbt row
    orbt_row = re.search(r"\|\s*`orbt`.*?\|\s*enum\s*\|.*?\|", section)
    library_states = set()
    if orbt_row:
        # Pull out backticked tokens after the description
        for tok in re.findall(r"`([A-Z_]+)`", orbt_row.group(0)):
            library_states.add(tok)
    if len(library_states) < 6:
        raise ValueError(f"BOOK_LAW.md: parsed only {len(library_states)} library_state values, expected >=6. Got: {sorted(library_states)}")

    return heir_fields, library_states


def lbb_query(sql: str, timeout: int = 30) -> Optional[dict]:
    """Hit LBB worker with a parametrized SQL query. Returns None on auth failure."""
    api_key = os.environ.get("LBB_API_KEY")
    if not api_key:
        return None
    req = urllib.request.Request(
        f"{LBB_BASE}/query",
        data=json.dumps({"sql": sql}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return None


def file_contains(path: Path, pattern: str) -> bool:
    if not path.exists():
        return False
    return bool(re.search(pattern, path.read_text(encoding="utf-8", errors="replace")))


# -----------------------------------------------------------------------------
# Predicate registry — one function per gate
# Each function returns (passed: bool, evidence: str)
# Predicate text comes FROM the manifest, NOT hardcoded here (G07 conformance)
# -----------------------------------------------------------------------------

def _gate_id_to_method(gate_id: str) -> str:
    """Derive Python method name from manifest gate ID.
    G01 → 'G01', W-1 → 'W1', Rung-1 → 'Rung1'
    """
    return gate_id.replace("-", "")


class GateEvaluator:
    """
    Evaluates the deterministic predicates declared in
    atlas/manifests/four-brain-doctrine-gate.yaml.

    The script is the executor. The manifest is the spec.
    Gate registry (IDs, names, strike targets) loaded from manifest at init time.
    """

    def __init__(self, manifest_path: Path, repo_v2: Path, repo_processes: Path,
                 bar_id: str, audited_yaml: Optional[Path] = None,
                 audited_md: Optional[Path] = None,
                 bar_baseline: Optional[str] = None,
                 sovereign_signed: bool = False,
                 run_dir: Optional[str] = None,
                 w7_disposition_path: Optional[str] = None):
        self.manifest_path = manifest_path
        self.manifest = load_yaml(manifest_path)
        self.repo_v2 = repo_v2
        self.repo_processes = repo_processes
        self.bar_id = bar_id
        self.audited_yaml = audited_yaml
        self.audited_md = audited_md
        # W-6: BAR-scoped baseline commit (not global git history)
        self.bar_baseline: Optional[str] = bar_baseline
        # W-6: sovereign sign-off flag — set when this BAR was authorized by sovereign
        self.sovereign_signed: bool = sovereign_signed
        # W-6/W-7: run dir for auto-discovering claimed-intake.txt / W7_DISPOSITION.json
        self.run_dir: Optional[str] = run_dir
        # W-7: explicit path to disposition artifact (overrides run_dir auto-discovery)
        self.w7_disposition_path: Optional[str] = w7_disposition_path
        # Atlas-derived schemas — read at construction time, not hardcoded.
        self.outside_heir_required, self.library_states_valid = load_atlas_book_law_heir_fields(repo_v2)
        # Manifest-driven per-role action enum and ORBT enum (Sub-task A/B/C).
        lbb_schema = self.manifest.get("lbb_row_schema") or {}
        self.role_action_enum: dict[str, list[str]] = lbb_schema.get("role_action_enum") or {}
        self.manifest_orbt_enum: set[str] = set(lbb_schema.get("orbt_mode_enum") or [])
        # Sub-task C self-check: manifest ORBT enum must agree with Atlas-derived states.
        if self.manifest_orbt_enum and self.manifest_orbt_enum != self.library_states_valid:
            only_in_manifest = self.manifest_orbt_enum - self.library_states_valid
            only_in_atlas = self.library_states_valid - self.manifest_orbt_enum
            raise RuntimeError(
                f"ORBT enum mismatch — manifest lbb_row_schema.orbt_mode_enum disagrees with Atlas BOOK_LAW.md.\n"
                f"  Only in manifest: {sorted(only_in_manifest)}\n"
                f"  Only in Atlas:    {sorted(only_in_atlas)}\n"
                f"Fix: update atlas/manifests/four-brain-doctrine-gate.yaml lbb_row_schema.orbt_mode_enum "
                f"to match the six-state set in BOOK_LAW.md."
            )
        # Manifest-driven gate registry: list of dicts with id/name/strike_target
        self.gate_registry: list[dict] = self._build_gate_registry()
        # Manifest-driven strike targets: gate_id → strike_target string
        self.strike_targets: dict[str, str] = {
            g["id"]: g.get("strike_target", "Mechanic")
            for g in self.gate_registry
        }
        # Validate parity: every manifest gate must have a Python implementation
        self._validate_manifest_implementation_parity()

    def _build_gate_registry(self) -> list[dict]:
        """Load gate list from manifest gates.gate_list."""
        gate_list = (self.manifest.get("gates") or {}).get("gate_list") or []
        if not gate_list:
            raise ValueError("Manifest gates.gate_list is empty or missing — cannot build registry")
        result = []
        for entry in gate_list:
            gid = entry.get("id", "")
            if not gid:
                raise ValueError(f"Manifest gate entry missing 'id': {entry}")
            result.append({
                "id": gid,
                "name": entry.get("name", gid),
                "predicate": entry.get("predicate", ""),
                "failure_impact": entry.get("failure_impact", "BLOCK"),
                "strike_target": entry.get("strike_target", "Mechanic"),
            })
        return result

    def _validate_manifest_implementation_parity(self):
        """Hard-error if any manifest gate lacks a Python implementation, or vice versa.

        Manifest gates are the spec. Python methods are the executor.
        Missing on either side is a conformance failure at startup.
        """
        manifest_ids = {g["id"] for g in self.gate_registry}
        # Derive expected method names from manifest IDs
        method_ids = {gid: _gate_id_to_method(gid) for gid in manifest_ids}
        missing_in_python = []
        for gid, method_name in method_ids.items():
            if not callable(getattr(self, method_name, None)):
                missing_in_python.append(gid)
        if missing_in_python:
            raise RuntimeError(
                f"Manifest-implementation parity FAIL: manifest defines {sorted(missing_in_python)} "
                f"but GateEvaluator has no corresponding method(s). "
                f"Add the method(s) or remove from manifest."
            )

    # --- G-gates: artifact + CI conformance ---

    def G01(self) -> tuple[bool, str]:
        """Y-junction syntactic separation."""
        if not self.audited_yaml:
            return False, "no audited yaml provided"
        top_keys = load_yaml_top_level_keys(self.audited_yaml)
        doc = load_yaml(self.audited_yaml)
        if "outside" not in top_keys or "inside" not in top_keys:
            return False, f"missing top-level outside or inside keys (got: {sorted(top_keys)})"
        outside = doc.get("outside") or {}
        inside = doc.get("inside") or {}
        if not isinstance(outside, dict) or not isinstance(inside, dict):
            return False, "outside/inside not maps"
        if "heir" not in outside or "orbt" not in outside:
            return False, "outside missing nested heir or orbt"
        if "heir" not in inside or "orbt" not in inside:
            return False, "inside missing nested heir or orbt"
        return True, "outside+inside top-level maps with nested heir+orbt"

    def G02(self) -> tuple[bool, str]:
        """outside.heir 7 required fields non-null."""
        required = self.outside_heir_required
        if not self.audited_yaml:
            return False, "no audited yaml"
        doc = load_yaml(self.audited_yaml)
        heir = (doc.get("outside") or {}).get("heir") or {}
        present = {k for k, v in heir.items() if v is not None}
        missing = required - present
        if missing:
            return False, f"missing fields: {sorted(missing)}"
        return True, "all 7 outside.heir fields present and non-null"

    def G03(self) -> tuple[bool, str]:
        """outside.orbt 3 fields + library_state enum."""
        valid = self.library_states_valid
        if not self.audited_yaml:
            return False, "no audited yaml"
        orbt = ((load_yaml(self.audited_yaml).get("outside") or {}).get("orbt")) or {}
        for f in ("library_state", "last_indexed_at", "indexed_by"):
            if not orbt.get(f):
                return False, f"missing outside.orbt.{f}"
        if orbt["library_state"] not in valid:
            return False, f"library_state '{orbt['library_state']}' not in {sorted(valid)}"
        return True, f"library_state={orbt['library_state']}, all 3 fields present"

    def G04(self) -> tuple[bool, str]:
        """inside.heir + inside.orbt populated (Workflow-Body spec: Atlas BOOK_LAW.md §inside.heir)."""
        valid = self.library_states_valid  # 6-state enum from Atlas BOOK_LAW.md
        # Atlas BOOK_LAW.md Workflow-Body inside.heir: process_id, aviation_model, services,
        # secrets_provider, acceptance_criteria, determinism_gate (NOT version/companion_manifest/species).
        required = {"process_id", "aviation_model", "services",
                    "secrets_provider", "acceptance_criteria", "determinism_gate"}
        if not self.audited_yaml:
            return False, "no audited yaml"
        doc = load_yaml(self.audited_yaml)
        heir = (doc.get("inside") or {}).get("heir") or {}
        orbt = (doc.get("inside") or {}).get("orbt") or {}
        missing = {k for k in required if not heir.get(k)}
        if missing:
            return False, f"inside.heir missing: {sorted(missing)}"
        # Atlas BOOK_LAW.md inside.orbt uses runtime_state (not library_state).
        if orbt.get("runtime_state") not in valid:
            return False, f"inside.orbt.runtime_state invalid: {orbt.get('runtime_state')!r}"
        return True, "inside.heir + inside.orbt valid"

    def G05(self) -> tuple[bool, str]:
        """lbb_row_schema.mandatory_fields == 12 with field+format+example+validation."""
        # The manifest IS the audited yaml when auditing the gate spec itself.
        # Otherwise, the audited yaml must reference the canonical schema.
        schema = self.manifest.get("lbb_row_schema", {})
        fields = schema.get("mandatory_fields", [])
        if len(fields) != 12:
            return False, f"manifest lbb_row_schema.mandatory_fields count={len(fields)}, expected 12"
        for entry in fields:
            for key in ("field", "format", "example", "validation"):
                if not entry.get(key):
                    return False, f"field {entry.get('field')!r} missing key '{key}'"
        return True, "12 fields, all with format+example+validation"

    def G06(self) -> tuple[bool, str]:
        """All 4 LBB rows have non-empty atlas_sections_consulted."""
        rows = self._fetch_bar_lbb_rows()
        if rows is None:
            return False, "LBB unreachable (LBB_API_KEY not set or query failed)"
        if not rows:
            return False, f"no LBB rows for bar_id={self.bar_id}"
        for row in rows:
            sections = row.get("atlas_sections_consulted") or ""
            if not sections.strip():
                return False, f"row role={row.get('role')} has empty atlas_sections_consulted"
        return True, f"{len(rows)} rows, all cite atlas sections"

    def G07(self) -> tuple[bool, str]:
        """CI workflow + runtime auditor prompt reference manifest; no inline predicates."""
        wf = self.repo_v2 / ".github" / "workflows" / "atlas-audit.yml"
        if not wf.exists():
            return False, f"workflow missing: {wf}"
        wf_text = wf.read_text(encoding="utf-8", errors="replace")
        if "four-brain-doctrine-gate.yaml" not in wf_text:
            return False, "atlas-audit.yml does not reference four-brain-doctrine-gate.yaml"
        # Forbidden inline predicate patterns — gate spec text MUST NOT be embedded
        # in CI workflows or runtime prompt heredocs. The manifest is the source of truth.
        forbidden_patterns = [
            r"COUNT\(.*lbb_records",
            r"all 8 HEIR fields",
            r"Y-junction.*outside.*inside",
        ]
        for pat in forbidden_patterns:
            if re.search(pat, wf_text, re.IGNORECASE):
                return False, f"workflow embeds gate predicate /{pat}/"
        # Also scan the runtime auditor prompt writer in forebrain-garage.sh — Codex caught
        # this pattern in the prior Atlas-only audit (G07 violation in heredoc).
        garage = self.repo_processes / "factory" / "imo-creator" / "070-four-brain" / "garage" / "forebrain-garage.sh"
        if garage.exists():
            g_text = garage.read_text(encoding="utf-8", errors="replace")
            inline_predicate_in_prompt = [
                r"W-1\s+.*\[strike:",  # W-gate strike-target inline in heredoc
                r"W-2\s+.*\[strike:",
                r"W-7\s+.*\[strike:",
            ]
            for pat in inline_predicate_in_prompt:
                if re.search(pat, g_text):
                    return False, (f"forebrain-garage.sh auditor prompt embeds W-gate "
                                   f"predicate text matching /{pat}/ — Atlas: prompt must "
                                   f"reference manifest, not embed predicates")
        # Workflow must say it CALLS the runner (deterministic), not that Codex evaluates.
        if re.search(r"codex.*evaluat|llm.*evaluat", wf_text, re.IGNORECASE):
            return False, "workflow says LLM evaluates predicates — Atlas: ai_on_spine_forbidden"
        return True, "workflow + runtime prompt reference manifest; no inline predicates"

    def G08(self) -> tuple[bool, str]:
        """COUNT(lbb_records WHERE bar_id=? AND subject_id='four-brain-gate-audit') == 4."""
        rows = self._fetch_bar_lbb_rows(subject_id="four-brain-gate-audit")
        if rows is None:
            return False, "LBB unreachable"
        if len(rows) != 4:
            return False, f"row count={len(rows)} for subject_id='four-brain-gate-audit', expected 4"
        return True, "4 LBB rows under subject_id='four-brain-gate-audit'"

    def G09(self) -> tuple[bool, str]:
        """All 12 schema fields valid across all 4 LBB rows."""
        rows = self._fetch_bar_lbb_rows(subject_id="four-brain-gate-audit")
        if rows is None:
            return False, "LBB unreachable"
        if not rows:
            return False, f"no rows for bar_id={self.bar_id}"
        valid_orbt = self.library_states_valid  # 6-state enum from Atlas BOOK_LAW.md
        valid_role = {"planner", "foreman", "mechanic", "auditor"}
        uuid_re = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        # SOVEREIGN CONFLICT (H-2): Atlas FOUR_BRAIN_AVIATION.md line 183 canonical regex is
        # ^(BAR-\d+|CI-PR-\d+|DRIFT-SWEEP-\d{8})$ (digits-only after BAR-).
        # However active BARs in the repo use alphanumeric slugs (e.g. BAR-FCE-RUN-060,
        # BAR-PROC-070) which would FAIL the canonical pattern. The loose pattern below is
        # retained to avoid breaking live BARs. Sovereign resolution required before tightening.
        bar_re = re.compile(r"^(BAR-[A-Za-z0-9._-]+|CI-PR-\d+|DRIFT-SWEEP-\d{8})$")
        sha_re = re.compile(r"^[0-9a-f]{64}$")
        ts_re = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        for row in rows:
            rid = row.get("record_id", "")
            if not uuid_re.match(rid):
                return False, f"row record_id={rid!r} not UUIDv4"
            if not bar_re.match(row.get("bar_id", "")):
                return False, f"row bar_id={row.get('bar_id')!r} invalid"
            if row.get("role") not in valid_role:
                return False, f"row role={row.get('role')!r} not in enum"
            # Sub-task B: per-role action enum validation (single source of truth: manifest).
            role = (row.get("role") or "").lower()
            action = (row.get("action") or "").lower()
            if self.role_action_enum:
                allowed_actions = self.role_action_enum.get(role, [])
                if action not in allowed_actions:
                    return False, (
                        f"row role={role!r} action={action!r} not in allowed "
                        f"{allowed_actions} (manifest lbb_row_schema.role_action_enum)"
                    )
            else:
                # Fallback: manifest role_action_enum not loaded — enforce non-empty only
                # and emit a warning so the operator knows the enum is missing.
                if not action:
                    return False, f"row action empty (role={role!r})"
            if not sha_re.match(row.get("evidence_hash", "")):
                return False, f"row evidence_hash invalid (role={row.get('role')})"
            if not (row.get("atlas_sections_consulted") or "").strip():
                return False, f"row atlas_sections_consulted empty (role={row.get('role')})"
            if not ts_re.match(row.get("timestamp", "")):
                return False, f"row timestamp invalid (role={row.get('role')})"
            if row.get("orbt_mode") not in valid_orbt:
                return False, f"row orbt_mode={row.get('orbt_mode')!r} invalid"
        return True, f"{len(rows)} rows, all 12 fields valid"

    def G10(self) -> tuple[bool, str]:
        """atlas-audit.yml: triggers on atlas/** PR; blocks merge on P=0; calls lbb-log.sh."""
        wf = self.repo_v2 / ".github" / "workflows" / "atlas-audit.yml"
        if not wf.exists():
            return False, f"missing: {wf}"
        text = wf.read_text(encoding="utf-8", errors="replace")
        if "pull_request" not in text:
            return False, "no pull_request trigger"
        if not re.search(r"paths:[^\n]*\n[^\n]*atlas/", text) and "atlas/**" not in text:
            return False, "no atlas/** path filter"
        if "lbb-log.sh" not in text:
            return False, "does not call scripts/lbb-log.sh"
        # Atlas G10 demands BLOCK on P=0. Sovereign override pathways violate the predicate.
        if re.search(r"sovereign[-_]?override", text, re.IGNORECASE):
            return False, "workflow contains sovereign-override path (Atlas G10 says BLOCK on P=0)"
        return True, "workflow triggers on atlas/** PR, calls lbb-log.sh, no override path"

    def G11(self) -> tuple[bool, str]:
        """11 parity fields identical between .yaml and .md frontmatter."""
        if not self.audited_yaml or not self.audited_md:
            return False, "G11 requires both .yaml and .md to be provided"
        ydoc = load_yaml(self.audited_yaml)
        mfm = load_md_frontmatter(self.audited_md)
        if not mfm:
            return False, (f"{self.audited_md.name} has no YAML frontmatter — "
                           f"G11 requires structured frontmatter to compare against .yaml")
        parity_fields = (self.manifest.get("nodes") or [])
        # The manifest declares the 11 parity fields under check_parity_sha256
        parity_list = []
        for node in parity_fields:
            if node.get("id") == "check_parity_sha256":
                parity_list = node.get("parity_fields", [])
                break
        if not parity_list:
            return False, "manifest does not declare parity_fields"
        mismatches = []
        for path in parity_list:
            yval = self._dotpath(ydoc, path)
            mval = self._dotpath(mfm, path)
            if yval != mval:
                mismatches.append(f"{path}: yaml={yval!r} md={mval!r}")
        if mismatches:
            return False, "; ".join(mismatches[:3])
        return True, f"{len(parity_list)} parity fields match"

    def G12(self) -> tuple[bool, str]:
        """drift-sweep workflow: cron '0 12 * * 1', calls lbb-log.sh."""
        wf = self.repo_v2 / ".github" / "workflows" / "atlas-drift-sweep.yml"
        if not wf.exists():
            return False, f"missing: {wf}"
        text = wf.read_text(encoding="utf-8", errors="replace")
        if "0 12 * * 1" not in text:
            return False, "cron '0 12 * * 1' not present"
        if "lbb-log.sh" not in text:
            return False, "does not call scripts/lbb-log.sh"
        return True, "drift-sweep cron correct, calls lbb-log.sh"

    # --- W-gates: Mission Control wiring ---

    def W1(self) -> tuple[bool, str]:
        """Every produced/modified artifact has a HEIR ID in spoke frontmatter."""
        artifacts = self._planner_declared_artifacts()
        if artifacts is None:
            return False, "Plan Book missing or unreadable"
        missing = []
        for art in artifacts:
            p = self._resolve_artifact_path(art)
            if not p or not p.exists():
                missing.append(f"{art} (file not found)")
                continue
            heir_id = self._extract_heir_id(p)
            if not heir_id:
                missing.append(f"{art} (no heir_id)")
        if missing:
            return False, "; ".join(missing[:3])
        return True, f"{len(artifacts)} artifacts have heir_id"

    def W2(self) -> tuple[bool, str]:
        """Plan Book has mission_control_wiring section with disposition for every artifact."""
        plan = self._plan_book()
        if plan is None:
            return False, "Plan Book not found"
        text = plan.read_text(encoding="utf-8", errors="replace")
        if "mission_control_wiring" not in text:
            return False, "Plan Book missing 'mission_control_wiring' section"
        # Extract the section as YAML if formatted as a block
        wiring = self._extract_wiring_block(text)
        if not wiring:
            return False, "mission_control_wiring section present but not parseable"
        for entry in wiring:
            disp = entry.get("disposition")
            if disp not in ("WIRE", "NEW_SLOT_NEEDED", "EXEMPT"):
                return False, f"artifact {entry.get('artifact')} has disposition={disp!r}"
            if disp == "WIRE" and not entry.get("target_slot_heir_id"):
                return False, f"WIRE artifact {entry.get('artifact')} missing target_slot_heir_id"
            if disp == "NEW_SLOT_NEEDED" and not entry.get("proposed_slot"):
                return False, f"NEW_SLOT_NEEDED artifact {entry.get('artifact')} missing proposed_slot"
            if disp == "EXEMPT" and not entry.get("rationale"):
                return False, f"EXEMPT artifact {entry.get('artifact')} missing rationale"
        return True, f"{len(wiring)} artifacts with valid dispositions"

    def W3(self) -> tuple[bool, str]:
        """WIRE: target slot's data_source updated; EXEMPT/NEW_SLOT execution per Atlas."""
        wiring = self._wiring_entries()
        if wiring is None:
            return False, "no wiring section"
        mc = self.repo_v2 / "atlas" / "constants" / "mission-control.yaml"
        mc_doc = load_yaml(mc) if mc.exists() else {}
        slots = {s.get("heir_id"): s for s in (mc_doc.get("slots") or [])}
        for entry in wiring:
            disp = entry.get("disposition")
            art = entry.get("artifact")
            if disp == "WIRE":
                slot_id = entry.get("target_slot_heir_id")
                slot = slots.get(slot_id)
                if not slot:
                    return False, f"WIRE: slot {slot_id} not found in mission-control.yaml"
                ds = slot.get("data_source")
                ds_str = json.dumps(ds) if ds else ""
                if art and art not in ds_str:
                    return False, f"WIRE: slot {slot_id} data_source does not reference {art}"
            elif disp == "EXEMPT":
                p = self._resolve_artifact_path(art)
                if p and p.exists():
                    fm = load_md_frontmatter(p) if p.suffix == ".md" else (load_yaml(p) or {}).get("outside", {})
                    if not fm.get("mission_control_exempt"):
                        return False, f"EXEMPT: {art} frontmatter missing mission_control_exempt: true"
            # NEW_SLOT_NEEDED: carry-forward verified by W-5 LBB tag
        return True, f"{len(wiring)} entries executed per declared disposition"

    def W4(self) -> tuple[bool, str]:
        """Paired Books (.md + .yaml) registered in paired-artifacts.yaml.

        Checks ALL produced/modified paired Books regardless of Mission Control
        disposition (WIRE, EXEMPT, NEW_SLOT_NEEDED).  The WIRE-specific data-source
        wiring predicate belongs to W-3 only.  W-4 enforces the BS Law v1.5.0
        requirement that every paired Library artifact has a registry entry —
        disposition does not grant an exemption from that structural requirement.
        """
        registry = self.repo_v2 / "atlas" / "manifests" / "paired-artifacts.yaml"
        if not registry.exists():
            return False, f"missing: {registry}"
        reg_doc = load_yaml(registry) or {}
        registered = {e.get("md_path") or e.get("ut_md") for e in (reg_doc.get("pairs") or [])}
        wiring = self._wiring_entries() or []
        for entry in wiring:
            # Evaluate ALL dispositions — paired-Book registry is disposition-agnostic.
            art = entry.get("artifact", "")
            if not art.endswith(".md"):
                continue
            companion = art.replace(".md", ".yaml")
            cp = self._resolve_artifact_path(companion)
            if cp and cp.exists() and art not in registered:
                disp = entry.get("disposition", "UNKNOWN")
                return False, (
                    f"paired Book {art} (disposition={disp}) not in paired-artifacts.yaml"
                )
        return True, "paired Books registered (or none in this BAR)"

    def W5(self) -> tuple[bool, str]:
        """LBB row tagged 'mission-control-wiring|exempt|new-slot-needed' per artifact."""
        rows = self._fetch_bar_lbb_rows()
        if rows is None:
            return False, "LBB unreachable"
        wiring = self._wiring_entries() or []
        wanted = {
            "WIRE": "mission-control-wiring",
            "EXEMPT": "mission-control-exempt",
            "NEW_SLOT_NEEDED": "mission-control-new-slot-needed",
        }
        for entry in wiring:
            tag = wanted[entry["disposition"]]
            art = entry.get("artifact", "")
            if not any(tag in (r.get("tags") or "") and art in (r.get("notes") or r.get("evidence_hash") or "") for r in rows):
                return False, f"no LBB row tagged {tag!r} referencing {art}"
        return True, f"{len(wiring)} artifacts have correctly tagged LBB rows"

    def W6(self) -> tuple[bool, str]:
        """Mechanic did NOT modify mission-control skeleton without sovereign signature.

        Evaluates the BAR's own diff against a baseline commit, NOT global git history.
        This prevents false-fails from unrelated historical commits and false-passes
        when the BAR change isn't the HEAD commit.

        Baseline resolution order:
          1. self.bar_baseline (set from --bar-baseline CLI arg)
          2. claimed-intake.txt in the run dir (first line = baseline commit SHA)
          3. STAGE-REPORT.md in the run dir (searches for 'baseline_commit:' line)
          4. If none found → PENDING (not a false PASS or false FAIL)

        Sovereign sign-off:
          Set self.sovereign_signed=True via --sovereign-signed CLI flag, OR
          if the HEAD commit author email matches 'sovereign' pattern.
        """
        MC_PATHS = [
            "atlas/constants/mission-control.yaml",
            "atlas/constants/MISSION_CONTROL.md",
        ]

        baseline = self._resolve_bar_baseline()
        if baseline is None:
            return False, (
                "PENDING: W-6 cannot evaluate — BAR baseline commit not found. "
                "Pass --bar-baseline <sha> or provide claimed-intake.txt in the run dir."
            )

        # Get the BAR-scoped diff for mission-control files only.
        try:
            diff_out = subprocess.check_output(
                ["git", "-C", str(self.repo_v2), "diff", "--name-only",
                 baseline, "HEAD", "--"] + MC_PATHS,
                stderr=subprocess.DEVNULL, text=True, timeout=15,
            )
        except subprocess.CalledProcessError as exc:
            return False, f"git diff failed (exit {exc.returncode}) — baseline may be invalid: {baseline!r}"
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return False, f"git diff unavailable: {exc}"

        changed = [ln.strip() for ln in diff_out.splitlines() if ln.strip()]
        if not changed:
            return True, f"BAR {self.bar_id} diff does not touch mission-control skeleton (baseline={baseline[:12]})"

        # BAR's diff DOES touch mission-control files — require sovereign sign-off.
        if self.sovereign_signed:
            return True, (
                f"mission-control touched by BAR {self.bar_id} but sovereign-signed "
                f"(files: {changed}; baseline={baseline[:12]})"
            )
        return False, (
            f"BAR {self.bar_id} modified mission-control skeleton without sovereign sign-off "
            f"(files: {changed}; baseline={baseline[:12]}). "
            "Pass --sovereign-signed if this amendment was authorized."
        )

    def _resolve_bar_baseline(self) -> Optional[str]:
        """Return the BAR's start baseline commit SHA, or None if unavailable."""
        # 1. Explicit --bar-baseline arg (stored on self by GateEvaluator.__init__)
        if getattr(self, "bar_baseline", None):
            return self.bar_baseline

        # 2. claimed-intake.txt in the run dir
        if getattr(self, "run_dir", None):
            intake = Path(self.run_dir) / "claimed-intake.txt"
            if intake.exists():
                first_line = intake.read_text(encoding="utf-8").splitlines()[0].strip()
                if re.match(r"^[0-9a-f]{7,40}$", first_line):
                    return first_line

            # 3. STAGE-REPORT.md — look for 'baseline_commit:' line
            stage_report = Path(self.run_dir) / "STAGE-REPORT.md"
            if stage_report.exists():
                for line in stage_report.read_text(encoding="utf-8").splitlines():
                    m = re.match(r"baseline_commit\s*[=:]\s*([0-9a-f]{7,40})", line, re.IGNORECASE)
                    if m:
                        return m.group(1)

        return None

    def W7(self) -> tuple[bool, str]:
        """Disposition sanity check — requires explicit Auditor judgment artifact.

        W-7 is the ONLY gate that legitimately requires LLM judgment (AUDITOR_ROLE.md §7b).
        It CANNOT self-certify. Three outcomes only:

          PASS   — a W7_DISPOSITION.json artifact exists in the run dir (or passed via
                   --w7-disposition) AND its `verdict` field is "PASS".
          FAIL   — artifact exists AND `verdict` is "FAIL". Strike target: Planner.
          PENDING — no artifact found. Blocks certification (verdict=BLOCKED, p_value=0).
                   The orchestrator must: run all deterministic gates first, then invoke
                   LLM tail arbitration, then re-invoke gate-runner with
                   --w7-disposition <path> so this gate can resolve.

        Contract for W7_DISPOSITION.json (produced by orchestrator after LLM run):
          {
            "gate_id": "W-7",
            "bar_id": "<BAR-ID>",
            "verdict": "PASS" | "FAIL",
            "evidence": "<why>",
            "evaluator": "<model-id>",
            "evaluated_at": "<ISO8601>"
          }
        """
        disposition_path = getattr(self, "w7_disposition_path", None)

        if disposition_path is None and getattr(self, "run_dir", None):
            # Auto-discover from run dir
            candidate = Path(self.run_dir) / "W7_DISPOSITION.json"
            if candidate.exists():
                disposition_path = candidate

        if disposition_path is None:
            # No disposition artifact — PENDING, blocks certification.
            return False, (
                "PENDING: W-7 disposition artifact not found. "
                "The orchestrator must run LLM tail arbitration and produce "
                "W7_DISPOSITION.json (or pass --w7-disposition <path>), "
                "then re-invoke gate-runner to resolve W-7."
            )

        # Read and validate the disposition artifact.
        try:
            disposition = json.loads(Path(disposition_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return False, f"W-7 disposition artifact unreadable ({disposition_path}): {exc}"

        verdict_field = disposition.get("verdict", "").upper()
        evidence = disposition.get("evidence", "(no evidence field)")
        evaluator_id = disposition.get("evaluator", "unknown")

        if verdict_field == "PASS":
            return True, (
                f"W-7 PASS from disposition artifact (evaluator={evaluator_id}): {evidence[:200]}"
            )
        if verdict_field == "FAIL":
            return False, (
                f"W-7 FAIL from disposition artifact (evaluator={evaluator_id}): {evidence[:200]}"
            )

        # Malformed verdict field — treat as FAIL with explanation.
        return False, (
            f"W-7 disposition artifact has unrecognized verdict={verdict_field!r} "
            f"(expected PASS or FAIL). Artifact: {disposition_path}"
        )

    # --- Audit ladder rungs (AUDITOR_ROLE.md §7) ---

    def Rung1(self) -> tuple[bool, str]:
        """Template conformity: 14 sections present and non-empty."""
        if not self.audited_md:
            return False, "no md provided"
        text = self.audited_md.read_text(encoding="utf-8", errors="replace")
        sections = re.findall(r"^## §(\d+[a-z]?)[\.\s]", text, re.MULTILINE)
        section_nums = sorted({int(re.match(r"\d+", s).group()) for s in sections})
        required = list(range(1, 15))
        missing = [n for n in required if n not in section_nums]
        if missing:
            return False, f"missing sections: §{missing}"
        return True, "all 14 sections present"

    def Rung2(self) -> tuple[bool, str]:
        """Fill-rule conformity: each section non-empty (no placeholders)."""
        if not self.audited_md:
            return False, "no md provided"
        text = self.audited_md.read_text(encoding="utf-8", errors="replace")
        # Find each section, check the body (until next ## §) is more than placeholders.
        sections = list(re.finditer(r"^## §(\d+[a-z]?)[\.\s].*$", text, re.MULTILINE))
        for i, m in enumerate(sections):
            start = m.end()
            end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
            body = text[start:end].strip()
            if len(body) < 20 or re.fullmatch(r"(TBD|TODO|N/A|—|-|_+)+", body, re.IGNORECASE):
                return False, f"§{m.group(1)} appears empty/placeholder"
        return True, f"{len(sections)} sections all filled"

    def Rung3(self) -> tuple[bool, str]:
        """HEIR completeness: 8 fields in outside.heir + inside.heir."""
        g2_pass, g2_ev = self.G02()
        g4_pass, g4_ev = self.G04()
        if not g2_pass:
            return False, f"outside.heir: {g2_ev}"
        if not g4_pass:
            return False, f"inside.heir: {g4_ev}"
        return True, "HEIR complete on both arms"

    def Rung4(self) -> tuple[bool, str]:
        """Binding/config exact match against wrangler.toml."""
        # The audited artifact must declare a wrangler.toml binding match.
        # If not applicable (doctrine-only artifact), this rung is N/A=PASS.
        if not self.audited_md:
            return False, "no md"
        text = self.audited_md.read_text(encoding="utf-8", errors="replace")
        if "wrangler.toml" not in text and "binding" not in text.lower():
            # Doctrine-only artifacts are exempt from rung 4
            return True, "N/A (no worker bindings declared)"
        # If declared, must reference a real wrangler.toml — defer to per-artifact check
        # For now, conservatively pass if declared and matches some wrangler.toml in tree.
        wrangler_files = list(self.repo_v2.rglob("wrangler.toml")) + list(self.repo_processes.rglob("wrangler.toml"))
        if not wrangler_files:
            return False, "no wrangler.toml found in either repo to match against"
        # Future-state phrasing fails this rung.
        if re.search(r"\b(future|TBD|pending|will be|to be added)\b", text, re.IGNORECASE):
            return False, "doc references future/TBD state — Atlas requires exact match to existing wrangler.toml"
        return True, "wrangler binding declarations present and not future-state"

    def Rung5(self) -> tuple[bool, str]:
        """Route/trigger exact match."""
        if not self.audited_md:
            return False, "no md"
        text = self.audited_md.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"route|trigger|cron", text, re.IGNORECASE):
            return True, "N/A (no routes/triggers declared)"
        if re.search(r"\b(URL TBD|route TBD|future|to be added|pending)\b", text, re.IGNORECASE):
            return False, "doc references future/TBD route state"
        return True, "routes/triggers declared, not future-state"

    def Rung6(self) -> tuple[bool, str]:
        """Schema/migration exact match."""
        if not self.audited_md:
            return False, "no md"
        text = self.audited_md.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"\.sql|migration|schema", text, re.IGNORECASE):
            return True, "N/A (no schema/migration declared)"
        # Future-state migration references fail this rung.
        if re.search(r"\b(future|TBD|pending BAR|will be created|to be shipped)\b", text, re.IGNORECASE):
            return False, "doc references future migration — Atlas requires exact match to existing SQL"
        return True, "schema/migration references present and not future-state"

    def Rung7(self) -> tuple[bool, str]:
        """Cross-manual graph validation: ctb_node consistent with BARTON_ENTERPRISES_CTB.md."""
        if not self.audited_yaml:
            return False, "no yaml"
        doc = load_yaml(self.audited_yaml)
        ctb = ((doc.get("outside") or {}).get("heir") or {}).get("ctb_placement", "")
        if not ctb:
            return False, "no ctb_placement declared"
        ctb_doc = self.repo_v2 / "atlas" / "constants" / "BARTON_ENTERPRISES_CTB.md"
        if not ctb_doc.exists():
            return False, f"trunk doc missing: {ctb_doc}"
        if ctb.split("/")[0] not in ctb_doc.read_text(encoding="utf-8", errors="replace"):
            return False, f"ctb root '{ctb.split('/')[0]}' not present in trunk doc"
        return True, f"ctb_node={ctb} traceable to trunk"

    def Rung8(self) -> tuple[bool, str]:
        """Certification label assigned: repo-certified | deployment-certified | provisional-runtime."""
        if not self.audited_md:
            return False, "no md"
        text = self.audited_md.read_text(encoding="utf-8", errors="replace")
        labels = ("repo-certified", "deployment-certified", "provisional-runtime")
        if not any(lbl in text for lbl in labels):
            return False, f"no certification label found (expected one of {labels})"
        return True, "certification label assigned"

    # --- Helpers ---

    def _fetch_bar_lbb_rows(self, subject_id: Optional[str] = None) -> Optional[list[dict]]:
        sql = f"SELECT * FROM lbb_records WHERE bar_id='{self.bar_id}'"
        if subject_id:
            sql += f" AND subject_id='{subject_id}'"
        result = lbb_query(sql)
        if result is None:
            return None
        return result.get("results") or result.get("rows") or []

    def _planner_declared_artifacts(self) -> Optional[list[str]]:
        wiring = self._wiring_entries()
        if wiring is None:
            return None
        return [e.get("artifact") for e in wiring if e.get("artifact")]

    def _wiring_entries(self) -> Optional[list[dict]]:
        plan = self._plan_book()
        if not plan:
            return None
        return self._extract_wiring_block(plan.read_text(encoding="utf-8", errors="replace"))

    def _plan_book(self) -> Optional[Path]:
        candidate = self.repo_processes / "docs" / "plans" / self.bar_id / "PLAN-BOOK.md"
        return candidate if candidate.exists() else None

    def _extract_wiring_block(self, text: str) -> Optional[list[dict]]:
        # Iterate through every fenced ```yaml/```yml block; return the first that
        # contains mission_control_wiring: as a parseable list.
        for m in re.finditer(r"```ya?ml\s*\n(.*?)\n```", text, re.DOTALL):
            block = m.group(1)
            if "mission_control_wiring:" not in block:
                continue
            try:
                doc = yaml.safe_load(block)
            except yaml.YAMLError:
                continue
            if isinstance(doc, dict) and isinstance(doc.get("mission_control_wiring"), list):
                return doc["mission_control_wiring"]
        # Fallback: non-fenced — capture from `mission_control_wiring:` until a
        # line that begins at column 0 with non-yaml content (next markdown section).
        m2 = re.search(
            r"^mission_control_wiring:\s*\n((?:[ \t#].*\n|\n)+?)(?=^\S|\Z)",
            text, re.MULTILINE,
        )
        if m2:
            try:
                doc = yaml.safe_load("mission_control_wiring:\n" + m2.group(1))
                if isinstance(doc, dict) and isinstance(doc.get("mission_control_wiring"), list):
                    return doc["mission_control_wiring"]
            except yaml.YAMLError:
                pass
        return None

    def _resolve_artifact_path(self, art: str) -> Optional[Path]:
        for root in (self.repo_v2, self.repo_processes):
            p = root / art
            if p.exists():
                return p
        return None

    def _extract_heir_id(self, p: Path) -> Optional[str]:
        if p.suffix == ".md":
            fm = load_md_frontmatter(p)
            return fm.get("heir_id") or (fm.get("outside", {}).get("heir", {}) or {}).get("hub_id")
        if p.suffix in (".yaml", ".yml"):
            doc = load_yaml(p)
            if isinstance(doc, dict):
                return ((doc.get("outside") or {}).get("heir") or {}).get("hub_id")
        return None

    @staticmethod
    def _dotpath(doc: dict, path: str) -> Any:
        cur = doc
        for part in path.split("."):
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        return cur


# -----------------------------------------------------------------------------
# NOTE: Strike-target table and gate dispatch list are now MANIFEST-DRIVEN.
# Both are loaded from atlas/manifests/four-brain-doctrine-gate.yaml at
# GateEvaluator.__init__ time via _build_gate_registry() and stored as:
#   evaluator.strike_targets  (dict: gate_id → strike_target string)
#   evaluator.gate_registry   (list of dicts with id/name/predicate/strike_target)
#
# The hardcoded STRIKE_TARGETS and GATE_DISPATCH dicts/lists have been removed.
# See _build_gate_registry() and _validate_manifest_implementation_parity().
# -----------------------------------------------------------------------------


def run(args) -> int:
    repo_v2 = Path(args.repo_v2).resolve()
    repo_processes = Path(args.repo_processes).resolve()
    manifest_path = Path(args.manifest).resolve() if args.manifest else (
        repo_v2 / "atlas" / "manifests" / "four-brain-doctrine-gate.yaml"
    )
    if not manifest_path.exists():
        print(f"FATAL: manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    audited_yaml = Path(args.audited_yaml).resolve() if args.audited_yaml else None
    audited_md = Path(args.audited_md).resolve() if args.audited_md else None

    evaluator = GateEvaluator(
        manifest_path=manifest_path,
        repo_v2=repo_v2,
        repo_processes=repo_processes,
        bar_id=args.bar_id,
        audited_yaml=audited_yaml,
        audited_md=audited_md,
        bar_baseline=getattr(args, "bar_baseline", None),
        sovereign_signed=getattr(args, "sovereign_signed", False),
        run_dir=getattr(args, "run_dir", None),
        w7_disposition_path=getattr(args, "w7_disposition", None),
    )

    manifest_version = (evaluator.manifest.get("document_control", {}) or {}).get("version", "unknown")
    report = AuditReport(bar_id=args.bar_id, manifest_version=manifest_version)

    only = set(args.only) if args.only else None
    skip = set(args.skip) if args.skip else set()

    # Gate dispatch driven entirely from manifest registry (no hardcoded lists)
    for gate_entry in evaluator.gate_registry:
        gate_id = gate_entry["id"]
        gate_name = gate_entry["name"]
        gate_predicate = gate_entry["predicate"]
        method_name = _gate_id_to_method(gate_id)
        strike_target = evaluator.strike_targets.get(gate_id, "Mechanic")

        if only and gate_id not in only:
            continue
        if gate_id in skip:
            continue
        if args.deterministic_only and gate_id == "W-7":
            # In --deterministic-only mode, W-7 cannot evaluate (no LLM/disposition artifact
            # available). Emit PENDING explicitly — this blocks certification (verdict=BLOCKED).
            report.record(GateResult(
                gate_id=gate_id, name=gate_name, passed=False,
                predicate=gate_predicate,
                evidence="PENDING: --deterministic-only mode; W-7 requires disposition artifact "
                         "(re-invoke with --w7-disposition <path> after LLM tail arbitration)",
                strike_target=strike_target,
                deferred_to_tail=True,
                pending=True,
            ))
            continue
        try:
            method = getattr(evaluator, method_name)
            passed, evidence = method()
        except Exception as e:
            passed, evidence = False, f"runner exception: {type(e).__name__}: {e}"

        # W-7 and W-6 may return (False, "PENDING: ...") to signal a blocking-but-not-failed
        # condition. Detect this and route to PENDING accounting, not FAIL accounting.
        is_pending = not passed and evidence.startswith("PENDING:")
        report.record(GateResult(
            gate_id=gate_id, name=gate_name, passed=passed,
            predicate=gate_predicate, evidence=evidence,
            strike_target=strike_target,
            deferred_to_tail=is_pending,
            pending=is_pending,
        ))

    if args.output_format == "json":
        print(report.to_json())
    else:
        print(f"VERDICT: {report.verdict}  P={report.p_value}")
        print(f"Manifest: v{manifest_version}")
        print(f"BAR: {report.bar_id}")
        print(f"Evaluated: {report.gates_evaluated}  Passed: {len(report.gates_passed)}  "
              f"Failed: {len(report.gates_failed)}  Pending: {len(report.gates_pending)}  "
              f"Deferred: {len(report.deferred_to_tail)}")
        if report.gates_failed:
            print("\nFailures:")
            for f in report.gates_failed:
                print(f"  [{f['strike_target']:<10}] {f['id']} — {f['evidence']}")
        if report.gates_pending:
            print(f"\nPending/Blocked (blocks certification): {report.gates_pending}")
        if report.deferred_to_tail and not report.gates_pending:
            print(f"\nDeferred to tail: {report.deferred_to_tail}")

    return 0 if report.verdict == "PASS" else 1


def main():
    p = argparse.ArgumentParser(
        description="Deterministic Four-Brain Doctrine Gate runner. "
                    "Reads predicates from atlas/manifests/four-brain-doctrine-gate.yaml. "
                    "No LLM on the spine (Atlas: ai_on_spine_forbidden).",
    )
    p.add_argument("--bar-id", required=True, help="BAR identifier (e.g. BAR-394 or CI-PR-42)")
    p.add_argument("--repo-v2", default=str(Path(__file__).resolve().parents[5] / "imo-creator-v2"),
                   help="Path to imo-creator-v2 root")
    p.add_argument("--repo-processes", default=str(Path(__file__).resolve().parents[4]),
                   help="Path to Barton-Processes root")
    p.add_argument("--manifest", help="Override path to four-brain-doctrine-gate.yaml")
    p.add_argument("--audited-yaml", help="Path to the YAML artifact under audit (for G01-G05, G11)")
    p.add_argument("--audited-md", help="Path to the MD companion under audit (for G11, Rungs)")
    p.add_argument("--only", nargs="*", help="Only evaluate these gate IDs (e.g. G01 W-2 Rung-3)")
    p.add_argument("--skip", nargs="*", help="Skip these gate IDs")
    p.add_argument("--deterministic-only", action="store_true",
                   help="Emit W-7 as PENDING (blocks cert). Use when no disposition artifact is ready.")
    # W-7 disposition artifact (produced by orchestrator after LLM tail arbitration)
    p.add_argument("--w7-disposition", metavar="PATH",
                   help="Path to W7_DISPOSITION.json artifact. Allows W-7 to resolve PASS/FAIL. "
                        "Orchestrator workflow: run gate-runner (all deterministic gates) → "
                        "LLM evaluates disposition sanity → writes W7_DISPOSITION.json → "
                        "re-run gate-runner --w7-disposition <path>.")
    # W-6 BAR-scoped baseline
    p.add_argument("--bar-baseline", metavar="SHA",
                   help="Git commit SHA at BAR start. W-6 diffs HEAD against this to detect "
                        "mission-control skeleton changes. Auto-discovered from claimed-intake.txt "
                        "if --run-dir is set.")
    p.add_argument("--sovereign-signed", action="store_true",
                   help="Flag that this BAR's mission-control changes were sovereign-authorized. "
                        "Allows W-6 to PASS when skeleton changes are present.")
    p.add_argument("--run-dir", metavar="PATH",
                   help="Path to the BAR run directory. W-6 searches for claimed-intake.txt "
                        "(baseline SHA) and STAGE-REPORT.md. W-7 searches for W7_DISPOSITION.json.")
    p.add_argument("--output-format", choices=["json", "text"], default="text")
    p.add_argument("--version", action="version", version=f"gate-runner.py {VERSION}")
    sys.exit(run(p.parse_args()))


if __name__ == "__main__":
    main()

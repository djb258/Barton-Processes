#!/usr/bin/env python3
"""
UP runner.

Mechanical control plane for the UP sequence:
Orchestrator -> Define -> Map -> Join -> QC -> STOP -> Auditor

IMO
- Input:
  - A valid US handoff
  - A subject path
  - An operator intent
  - Prior UP runs, if they exist
  - Human-owned TS tolerances before audit
- Middle:
  - Freeze scope
  - Propose key, map, and join candidates
  - Validate artifacts mechanically at every stage
  - Halt for TS instead of self-certifying
  - Require repeated runs before lock
  - Require human-owned tolerances before audit
- Output:
  - Versioned UP run directory
  - Stage JSON artifacts
  - Machine-readable error receipts
  - Audit decision only after the gates are satisfied

CTB
- Trunk:
  - UP is the leaf control plane that structures content using US output
- Branches:
  - Orchestrator
  - Define
  - Map
  - Join
  - QC
  - Auditor
- Leaves:
  - JSON artifacts
  - receipts/
  - ts-tolerances.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
UP_ROOT = Path(__file__).resolve().parent
US_ARTIFACT = "01-us.json"
US_READY_ARTIFACT = "02-us-ready.json"

AGENT_TO_ARTIFACT = {
    "orchestrator": "01-orchestrator.json",
    "d-define": "02-define.json",
    "m-map": "03-map.json",
    "j-join": "04-join.json",  # Or 04-backprop.json
    "qc-quality": "05-qc.json",
    "auditor": "06-audit.json",
}

REQUIRED_FIELDS = {
    "01-orchestrator.json": ["subject", "scope", "boundary", "intent", "heir", "orbt"],
    "02-define.json": ["candidate", "comparators", "elements"],
    "03-map.json": ["candidate", "comparators", "mappings"],
    "04-join.json": ["candidate", "comparators", "join_path"],
    "04-backprop.json": ["failure_type", "gap_description"],
    "05-qc.json": ["stages"],
    "06-audit.json": ["decision", "checklist", "reasons"],
}

HEIR_REQUIRED_FIELDS = [
    "sovereign_ref", "hub_id", "ctb_placement", "imo_topology",
    "cc_layer", "services", "secrets_provider", "acceptance_criteria",
]

LEGAL_ORBT_STATES = {"BUILD", "OPERATE", "REPAIR", "TROUBLESHOOT_TRAIN"}

ARTIFACTS_REQUIRING_CANDIDATE = {
    "02-define.json",
    "03-map.json",
    "04-join.json",
}

ARTIFACTS_REQUIRING_COMPARATORS = {
    "02-define.json",
    "03-map.json",
    "04-join.json",
}

LEGAL_COMPARATOR_STATUSES = {"evaluable", "not_evaluable"}
LEGAL_AUDIT_DECISIONS = {"certify", "reject"}
LEGAL_QC_STATUSES = {"provisional", "lockable", "blocked"}
TS_TOLERANCES_ARTIFACT = "ts-tolerances.json"
MIN_RUNS_FOR_LOCK = 3

READING_LIST = {
    "orchestrator": [
        REPO_ROOT / "law/doctrine/FOUNDATIONAL_BEDROCK.md",
        REPO_ROOT / "law/doctrine/DMJ.md",
        REPO_ROOT / "factory/agents/up/UP.md",
        REPO_ROOT / "factory/agents/up/agents/orchestrator.md",
    ],
    "d-define": [
        REPO_ROOT / "law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md",
        REPO_ROOT / "law/doctrine/FOUNDATIONAL_BEDROCK.md",
        REPO_ROOT / "factory/agents/up/UP.md",
        REPO_ROOT / "factory/agents/up/agents/d-define.md",
    ],
    "m-map": [
        REPO_ROOT / "law/doctrine/DMJ.md",
        REPO_ROOT / "law/doctrine/FOUNDATIONAL_BEDROCK.md",
        REPO_ROOT / "factory/agents/up/UP.md",
        REPO_ROOT / "factory/agents/up/agents/m-map.md",
    ],
    "j-join": [
        REPO_ROOT / "law/doctrine/DMJ.md",
        REPO_ROOT / "law/doctrine/FOUNDATIONAL_BEDROCK.md",
        REPO_ROOT / "factory/agents/up/UP.md",
        REPO_ROOT / "factory/agents/up/agents/j-join.md",
    ],
    "qc-quality": [
        REPO_ROOT / "law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md",
        REPO_ROOT / "law/doctrine/FOUNDATIONAL_BEDROCK.md",
        REPO_ROOT / "factory/agents/up/UP.md",
        REPO_ROOT / "factory/agents/up/agents/qc-quality.md",
    ],
    "auditor": [
        REPO_ROOT / "law/doctrine/FOUNDATIONAL_BEDROCK.md",
        REPO_ROOT / "law/doctrine/DMJ.md",
        REPO_ROOT / "factory/agents/up/UP.md",
        REPO_ROOT / "factory/agents/up/agents/auditor.md",
    ],
}

STAGE_INSTRUCTIONS = {
    "orchestrator": [
        'Write exactly "01-orchestrator.json".',
        "Refuse if subject boundary or operator intent is ambiguous.",
        'If refusing, include: "refused": true and "refused_reason".',
    ],
    "d-define": [
        'Write exactly "02-define.json".',
        "Propose the key. Do not lock anything.",
        "Use deviation comparators only. Lower is better.",
    ],
    "m-map": [
        'Write exactly "03-map.json".',
        "Propose mappings or a target structure if none exists.",
        "Document every unmapped element or gap explicitly.",
    ],
    "j-join": [
        'Write either "04-join.json" or "04-backprop.json", never both.',
        "Only use typed failure_type values for backprop.",
        "If failure is not a missing key field, halt for TS instead of looping.",
    ],
    "qc-quality": [
        'Write exactly "05-qc.json".',
        "QC evaluates. QC does not generate structure.",
        "Record provisional vs lockable status per stage.",
    ],
    "auditor": [
        'Write exactly "06-audit.json".',
        "Auditor certifies or rejects after TS review.",
        "Auditor must evaluate the original subject and the full run evidence.",
    ],
}

JOIN_BACKPROP_FAILURES = {
    "missing_key_field",
    "ambiguous_spine",
    "no_spine_exists",
    "insufficient_evidence",
}


@dataclass
class RunContext:
    subject_path: Path
    run_dir: Path
    operator_intent: str | None = None
    us_run_dir: Path | None = None


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UP runner")
    parser.add_argument("subject_path", nargs="?", help="Path to the subject")
    parser.add_argument("operator_intent", nargs="?", help="What the subject should be brought into")
    parser.add_argument("--us-run-dir", help="US run directory containing 01-us.json and 02-us-ready.json")
    parser.add_argument("--auditor", action="store_true", help="Run auditor only")
    parser.add_argument("--run-dir", help="Existing run directory for --auditor mode")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.auditor:
        if not args.run_dir:
            print("--auditor requires --run-dir", file=sys.stderr)
            return 2
        run_dir = Path(args.run_dir).expanduser().resolve()
        return audit_only(run_dir)

    if not args.subject_path or not args.operator_intent or not args.us_run_dir:
        print("Usage: up.py --us-run-dir /path/to/us-run /path/to/thing \"What do you want this brought into?\"", file=sys.stderr)
        return 2

    subject_path = Path(args.subject_path).expanduser().resolve()
    if not subject_path.exists():
        print(f"Subject path does not exist: {subject_path}", file=sys.stderr)
        return 2
    us_run_dir = Path(args.us_run_dir).expanduser().resolve()
    us_context = validate_us_handoff(us_run_dir)
    if us_context is None:
        return 2

    ensure_model_separation()
    run_dir = create_run_dir(subject_path)
    ctx = RunContext(
        subject_path=subject_path,
        run_dir=run_dir,
        operator_intent=args.operator_intent,
        us_run_dir=us_run_dir,
    )
    save_run_metadata(ctx)
    write_json(run_dir / "us-handoff.json", us_context)

    run_agent("orchestrator", ctx)
    validate_artifact(run_dir, "01-orchestrator.json")

    orch = load_json(run_dir / "01-orchestrator.json")
    if orch.get("refused"):
        print(f"REFUSED: {orch.get('refused_reason', 'unknown reason')}")
        print("Fix the intent or subject boundary, then re-run.")
        return 0

    run_agent("d-define", ctx)
    validate_artifact(run_dir, "02-define.json")

    run_agent("m-map", ctx)
    validate_artifact(run_dir, "03-map.json")

    run_agent("j-join", ctx)
    handle_join_result(ctx)

    run_agent("qc-quality", ctx)
    validate_artifact(run_dir, "05-qc.json")

    print(f"Scorecard: {run_dir / '05-qc.json'}")
    print(f"Human tolerance file required before audit: {run_dir / TS_TOLERANCES_ARTIFACT}")
    print(f"Minimum completed runs before audit: {MIN_RUNS_FOR_LOCK}")
    print(f"When ready: python3 {UP_ROOT / 'up.py'} --auditor --run-dir {run_dir}")
    return 0


def audit_only(run_dir: Path) -> int:
    ensure_model_separation()
    metadata = load_json(run_dir / "run.json")
    subject_path = Path(metadata["subject_path"])
    if not subject_path.exists():
        write_error(run_dir, f"ORIGINAL SUBJECT MISSING FOR AUDIT: {subject_path}", stage="auditor")
        return 1
    completed_runs = count_completed_runs(run_dir)
    if completed_runs < MIN_RUNS_FOR_LOCK:
        write_error(
            run_dir,
            f"INSUFFICIENT RUN HISTORY FOR AUDIT: need {MIN_RUNS_FOR_LOCK} completed runs, found {completed_runs}",
            stage="auditor",
        )
        return 1
    if not validate_ts_tolerances(run_dir):
        return 1
    operator_intent = metadata.get("operator_intent")
    ctx = RunContext(subject_path=subject_path, run_dir=run_dir, operator_intent=operator_intent)
    run_agent("auditor", ctx, model=os.environ.get("UP_AUDIT_MODEL", "auditor"))
    validate_artifact(run_dir, "06-audit.json")
    print(f"Audit decision: {run_dir / '06-audit.json'}")
    return 0


def create_run_dir(subject_path: Path) -> Path:
    anchor_parent = subject_path.parent
    subject_label = subject_path.stem if subject_path.is_file() else subject_path.name
    run_root = anchor_parent / ".up-runs" / subject_label
    run_root.mkdir(parents=True, exist_ok=True)

    existing = sorted(p.name for p in run_root.iterdir() if p.is_dir() and p.name.startswith("run-"))
    next_num = 1
    if existing:
        nums = [int(name.split("-")[1]) for name in existing if name.split("-")[1].isdigit()]
        if nums:
            next_num = max(nums) + 1

    run_dir = run_root / f"run-{next_num:03d}"
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "receipts").mkdir(exist_ok=True)
    return run_dir


def save_run_metadata(ctx: RunContext) -> None:
    write_text(ctx.run_dir / "intent.txt", ctx.operator_intent or "")
    write_text(ctx.run_dir / "subject_path.txt", str(ctx.subject_path))
    write_json(
        ctx.run_dir / "run.json",
        {
            "created_at": now_utc(),
            "subject_path": str(ctx.subject_path),
            "operator_intent": ctx.operator_intent,
            "repo_root": str(REPO_ROOT),
            "run_number": parse_run_number(ctx.run_dir),
            "min_runs_for_lock": MIN_RUNS_FOR_LOCK,
            "us_run_dir": str(ctx.us_run_dir) if ctx.us_run_dir else None,
        },
    )


def run_agent(agent_name: str, ctx: RunContext, model: str | None = None) -> None:
    reading_list = READING_LIST[agent_name]
    missing_refs = [str(path) for path in reading_list if not path.exists()]
    if missing_refs:
        write_error(ctx.run_dir, f"MISSING READING FILES for {agent_name}: {missing_refs}", stage=agent_name)
        sys.exit(1)

    reading_instructions = "\n".join(f"    {i + 1}. Read: {path}" for i, path in enumerate(reading_list))
    stage_instructions = "\n".join(f"    - {line}" for line in STAGE_INSTRUCTIONS[agent_name])
    output_name = AGENT_TO_ARTIFACT[agent_name]
    us_context_path = ctx.run_dir / "us-handoff.json"
    prompt = f"""
You are the {agent_name} agent in the UP (Ultimate Process).

BEFORE YOU DO ANYTHING, read these files in order.
This is how you know what to do:

{reading_instructions}

Then read the original subject at: {ctx.subject_path}
Then read the operator intent and any prior agent outputs in: {ctx.run_dir}
Then read the US handoff at: {us_context_path}

Do your job as defined in your agent spec.
Save your output as JSON to {ctx.run_dir}/

Stage instructions:
{stage_instructions}

Artifact contract:
    - Primary artifact name: {output_name}
"""

    if agent_name in {"d-define", "m-map", "j-join"}:
        prompt += """
    - Include "candidate"
    - Include "comparators"
    - Comparators must be deviation/failure quantities where LOWER is better
    - Do not use success rates in the decision equation
"""
    elif agent_name == "qc-quality":
        prompt += """
    - Include stage-by-stage evaluation
    - Include cross-run metrics only if prior runs exist
"""

    claude_bin = os.environ.get("UP_CLAUDE_BIN", "claude")
    chosen_model = model or os.environ.get("UP_BUILD_MODEL", "builder")
    timeout_seconds = int(os.environ.get("UP_AGENT_TIMEOUT", "600"))
    cmd = [
        claude_bin,
        "--print",
        "--model",
        chosen_model,
        "--allowedTools",
        "Read,Bash,Write,Grep,Glob",
        "-p",
        prompt,
    ]

    receipt_base = ctx.run_dir / "receipts" / f"{agent_name}"
    write_text(receipt_base.with_suffix(".prompt.txt"), prompt)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        write_error(ctx.run_dir, f"AGENT TIMEOUT: {agent_name}", stage=agent_name)
        sys.exit(1)
    except FileNotFoundError:
        write_error(ctx.run_dir, f"AGENT BINARY NOT FOUND: {claude_bin}", stage=agent_name)
        sys.exit(1)

    write_text(receipt_base.with_suffix(".stdout.log"), result.stdout)
    write_text(receipt_base.with_suffix(".stderr.log"), result.stderr)
    write_text(receipt_base.with_suffix(".cmd.txt"), " ".join(cmd))

    if result.returncode != 0:
        write_error(ctx.run_dir, f"AGENT FAILED: {agent_name}, exit={result.returncode}", stage=agent_name)
        sys.exit(1)


def handle_join_result(ctx: RunContext) -> None:
    run_dir = ctx.run_dir
    loop_count = 0
    while not (run_dir / "04-join.json").exists() and loop_count < 3:
        bp_path = run_dir / "04-backprop.json"
        if not bp_path.exists():
            write_error(run_dir, "JOIN FAILED: neither 04-join.json nor 04-backprop.json exists", stage="j-join")
            sys.exit(1)

        validate_artifact(run_dir, "04-backprop.json")
        bp = load_json(bp_path)
        failure_type = bp.get("failure_type")

        if failure_type == "missing_key_field":
            loop_count += 1
            archived = run_dir / f"04-backprop-{loop_count}.json"
            bp_path.rename(archived)

            run_agent("d-define", ctx)
            validate_artifact(run_dir, "02-define.json")
            run_agent("m-map", ctx)
            validate_artifact(run_dir, "03-map.json")
            run_agent("j-join", ctx)
        elif failure_type in {"ambiguous_spine", "no_spine_exists", "insufficient_evidence"}:
            print(f"JOIN HALTED: {failure_type}")
            print(f"Backprop file: {bp_path}")
            print("This is not a Define-stage problem. TS must decide the path.")
            return
        elif failure_type not in JOIN_BACKPROP_FAILURES:
            write_error(run_dir, f"UNKNOWN failure_type in 04-backprop.json: {failure_type}", stage="j-join")
            sys.exit(1)

    if not (run_dir / "04-join.json").exists():
        write_error(run_dir, "JOIN FAILED: max backprop loops exhausted without 04-join.json", stage="j-join")
        sys.exit(1)

    validate_artifact(run_dir, "04-join.json")


def validate_artifact(run_dir: Path, filename: str) -> None:
    path = run_dir / filename
    if not path.exists():
        write_error(run_dir, f"MISSING ARTIFACT: {filename}")
        sys.exit(1)

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        write_error(run_dir, f"INVALID JSON: {filename}")
        sys.exit(1)

    required = REQUIRED_FIELDS.get(filename, [])
    missing = [field for field in required if field not in data]
    if missing:
        write_error(run_dir, f"MISSING FIELDS in {filename}: {missing}")
        sys.exit(1)

    if filename in ARTIFACTS_REQUIRING_CANDIDATE and not data.get("candidate"):
        write_error(run_dir, f"EMPTY CANDIDATE in {filename}")
        sys.exit(1)

    if filename in ARTIFACTS_REQUIRING_COMPARATORS and not data.get("comparators"):
        write_error(run_dir, f"EMPTY COMPARATORS in {filename}")
        sys.exit(1)

    if filename == "04-backprop.json":
        failure_type = data.get("failure_type")
        if failure_type not in JOIN_BACKPROP_FAILURES:
            write_error(run_dir, f"UNKNOWN failure_type in {filename}: {failure_type}")
            sys.exit(1)
        return

    validate_artifact_shape(run_dir, filename, data)


def validate_artifact_shape(run_dir: Path, filename: str, data: dict[str, Any]) -> None:
    if filename == "01-orchestrator.json":
        if not isinstance(data["boundary"], list) or not data["boundary"]:
            fail_validation(run_dir, filename, "boundary must be a non-empty list")
        if data.get("refused") and not data.get("refused_reason"):
            fail_validation(run_dir, filename, "refused orchestrator artifact must include refused_reason")
        # HEIR — 8 required fields (Aviation Model, Bedrock §8)
        heir = data.get("heir")
        if not isinstance(heir, dict):
            fail_validation(run_dir, filename, "heir must be an object")
        heir_missing = [f for f in HEIR_REQUIRED_FIELDS if f not in heir]
        if heir_missing:
            fail_validation(run_dir, filename, f"heir missing required fields: {heir_missing}")
        # ORBT — must be a valid state, starts at BUILD
        orbt = data.get("orbt")
        if orbt not in LEGAL_ORBT_STATES:
            fail_validation(run_dir, filename, f"orbt must be one of {sorted(LEGAL_ORBT_STATES)}, got: {orbt}")
        return

    if filename == "02-define.json":
        require_non_empty_list(run_dir, filename, data, "elements")
        for index, element in enumerate(data["elements"]):
            require_keys(
                run_dir,
                filename,
                element,
                ["id", "description", "format", "classification"],
                prefix=f"elements[{index}]",
            )
        validate_comparators(run_dir, filename, data["comparators"])
        return

    if filename == "03-map.json":
        require_non_empty_list(run_dir, filename, data, "mappings")
        for index, mapping in enumerate(data["mappings"]):
            require_keys(
                run_dir,
                filename,
                mapping,
                ["source_id", "target"],
                prefix=f"mappings[{index}]",
            )
        validate_comparators(run_dir, filename, data["comparators"])
        return

    if filename == "04-join.json":
        if not isinstance(data["join_path"], dict):
            fail_validation(run_dir, filename, "join_path must be an object")
        require_keys(run_dir, filename, data["join_path"], ["spine"], prefix="join_path")
        validate_comparators(run_dir, filename, data["comparators"])
        return

    if filename == "05-qc.json":
        stages = data["stages"]
        if not isinstance(stages, dict):
            fail_validation(run_dir, filename, "stages must be an object")
        for stage_name in ("define", "map", "join"):
            stage_data = stages.get(stage_name)
            if not isinstance(stage_data, dict):
                fail_validation(run_dir, filename, f"stages.{stage_name} must be an object")
            require_keys(
                run_dir,
                filename,
                stage_data,
                ["p", "status", "diagnostics", "reasons"],
                prefix=f"stages.{stage_name}",
            )
            if stage_data["p"] not in (0, 1):
                fail_validation(run_dir, filename, f"stages.{stage_name}.p must be 0 or 1")
            if stage_data["status"] not in LEGAL_QC_STATUSES:
                fail_validation(
                    run_dir,
                    filename,
                    f"stages.{stage_name}.status must be one of {sorted(LEGAL_QC_STATUSES)}",
                )
            if not isinstance(stage_data["diagnostics"], dict):
                fail_validation(run_dir, filename, f"stages.{stage_name}.diagnostics must be an object")
            if not isinstance(stage_data["reasons"], list):
                fail_validation(run_dir, filename, f"stages.{stage_name}.reasons must be a list")
            if stage_data["status"] == "lockable" and count_completed_runs(run_dir) < MIN_RUNS_FOR_LOCK:
                fail_validation(
                    run_dir,
                    filename,
                    f"stages.{stage_name}.status cannot be lockable before {MIN_RUNS_FOR_LOCK} completed runs",
                )
        if "cross_run" in data and not isinstance(data["cross_run"], dict):
            fail_validation(run_dir, filename, "cross_run must be an object when present")
        return

    if filename == "06-audit.json":
        if data["decision"] not in LEGAL_AUDIT_DECISIONS:
            fail_validation(run_dir, filename, f"decision must be one of {sorted(LEGAL_AUDIT_DECISIONS)}")
        if not isinstance(data["checklist"], list) or not data["checklist"]:
            fail_validation(run_dir, filename, "checklist must be a non-empty list")
        if not isinstance(data["reasons"], list) or not data["reasons"]:
            fail_validation(run_dir, filename, "reasons must be a non-empty list")
        return


def validate_comparators(run_dir: Path, filename: str, comparators: Any) -> None:
    if not isinstance(comparators, dict) or not comparators:
        fail_validation(run_dir, filename, "comparators must be a non-empty object")
    for name, comparator in comparators.items():
        if not isinstance(comparator, dict):
            fail_validation(run_dir, filename, f"comparator {name} must be an object")
        require_keys(
            run_dir,
            filename,
            comparator,
            ["status", "measurement", "lower_is_better"],
            prefix=f"comparators.{name}",
        )
        if comparator["status"] not in LEGAL_COMPARATOR_STATUSES:
            fail_validation(
                run_dir,
                filename,
                f"comparators.{name}.status must be one of {sorted(LEGAL_COMPARATOR_STATUSES)}",
            )
        if comparator["lower_is_better"] is not True:
            fail_validation(run_dir, filename, f"comparators.{name}.lower_is_better must be true")
        if not isinstance(comparator["measurement"], str) or not comparator["measurement"].strip():
            fail_validation(run_dir, filename, f"comparators.{name}.measurement must be a non-empty string")
        if comparator["status"] == "evaluable" and "value" not in comparator:
            fail_validation(run_dir, filename, f"comparators.{name}.value is required when status=evaluable")
        if comparator["status"] == "not_evaluable" and "reason" not in comparator:
            fail_validation(run_dir, filename, f"comparators.{name}.reason is required when status=not_evaluable")


def require_non_empty_list(run_dir: Path, filename: str, data: dict[str, Any], field: str) -> None:
    value = data[field]
    if not isinstance(value, list) or not value:
        fail_validation(run_dir, filename, f"{field} must be a non-empty list")


def require_keys(
    run_dir: Path,
    filename: str,
    data: Any,
    keys: list[str],
    *,
    prefix: str = "",
) -> None:
    if not isinstance(data, dict):
        fail_validation(run_dir, filename, f"{prefix or 'object'} must be an object")
    missing = [key for key in keys if key not in data]
    if missing:
        scope = prefix or filename
        fail_validation(run_dir, filename, f"{scope} missing keys: {missing}")


def fail_validation(run_dir: Path, filename: str, message: str) -> None:
    write_error(run_dir, f"INVALID ARTIFACT SHAPE in {filename}: {message}")
    sys.exit(1)


def ensure_model_separation() -> None:
    build_model = os.environ.get("UP_BUILD_MODEL", "builder")
    audit_model = os.environ.get("UP_AUDIT_MODEL", "auditor")
    if build_model == audit_model:
        print("UP_BUILD_MODEL and UP_AUDIT_MODEL must differ", file=sys.stderr)
        sys.exit(2)


def parse_run_number(run_dir: Path) -> int:
    try:
        return int(run_dir.name.split("-")[1])
    except (IndexError, ValueError):
        return 0


def count_completed_runs(run_dir: Path) -> int:
    return sum(1 for candidate in run_dir.parent.glob("run-*") if (candidate / "05-qc.json").exists())


def validate_ts_tolerances(run_dir: Path) -> bool:
    path = run_dir / TS_TOLERANCES_ARTIFACT
    if not path.exists():
        write_error(run_dir, f"MISSING HUMAN TOLERANCE FILE: {TS_TOLERANCES_ARTIFACT}", stage="auditor")
        return False
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        write_error(run_dir, f"INVALID JSON: {TS_TOLERANCES_ARTIFACT}", stage="auditor")
        return False

    required = ["set_by", "approved_at", "stage_tolerances"]
    missing = [field for field in required if field not in data]
    if missing:
        write_error(
            run_dir,
            f"MISSING FIELDS in {TS_TOLERANCES_ARTIFACT}: {missing}",
            stage="auditor",
        )
        return False
    if data["set_by"] != "human":
        write_error(run_dir, f"{TS_TOLERANCES_ARTIFACT} set_by must be 'human'", stage="auditor")
        return False
    if not isinstance(data["stage_tolerances"], dict) or not data["stage_tolerances"]:
        write_error(
            run_dir,
            f"{TS_TOLERANCES_ARTIFACT} stage_tolerances must be a non-empty object",
            stage="auditor",
        )
        return False
    for stage in ("define", "map", "join"):
        if stage not in data["stage_tolerances"]:
            write_error(
                run_dir,
                f"{TS_TOLERANCES_ARTIFACT} missing stage_tolerances.{stage}",
                stage="auditor",
            )
            return False
    return True


def validate_us_handoff(us_run_dir: Path) -> dict[str, Any] | None:
    if not us_run_dir.exists():
        print(f"US run directory does not exist: {us_run_dir}", file=sys.stderr)
        return None
    us_artifact = us_run_dir / US_ARTIFACT
    ready_artifact = us_run_dir / US_READY_ARTIFACT
    if not us_artifact.exists():
        print(f"Missing US artifact: {us_artifact}", file=sys.stderr)
        return None
    if not ready_artifact.exists():
        print(f"Missing US ready artifact: {ready_artifact}", file=sys.stderr)
        return None
    try:
        us_data = json.loads(us_artifact.read_text())
        ready_data = json.loads(ready_artifact.read_text())
    except json.JSONDecodeError as exc:
        print(f"Invalid US handoff JSON: {exc}", file=sys.stderr)
        return None

    required_us = ["medium", "intent", "layers", "invariant_set", "reverse_route", "domestication_depth", "handoff_contract"]
    missing_us = [field for field in required_us if field not in us_data]
    if missing_us:
        print(f"US artifact missing fields: {missing_us}", file=sys.stderr)
        return None
    required_ready = ["source_artifact", "completed_runs", "min_runs_for_handoff", "tolerances_artifact", "set_by", "medium", "intent"]
    missing_ready = [field for field in required_ready if field not in ready_data]
    if missing_ready:
        print(f"US ready artifact missing fields: {missing_ready}", file=sys.stderr)
        return None
    if ready_data["source_artifact"] != US_ARTIFACT:
        print("US ready artifact source_artifact must be 01-us.json", file=sys.stderr)
        return None
    if ready_data["set_by"] != "human":
        print("US ready artifact must be human-owned", file=sys.stderr)
        return None
    if ready_data["medium"] != us_data["medium"] or ready_data["intent"] != us_data["intent"]:
        print("US ready artifact does not match US artifact medium/intent", file=sys.stderr)
        return None
    return {
        "us_run_dir": str(us_run_dir),
        "us_artifact": str(us_artifact),
        "us_ready_artifact": str(ready_artifact),
        "medium": us_data["medium"],
        "intent": us_data["intent"],
        "invariant_set": us_data["invariant_set"],
        "layers": us_data["layers"],
        "reverse_route": us_data["reverse_route"],
        "domestication_depth": us_data["domestication_depth"],
        "handoff_contract": us_data["handoff_contract"],
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value)


def write_error(run_dir: Path, message: str, *, stage: str | None = None) -> None:
    payload = {
        "timestamp": now_utc(),
        "stage": stage,
        "message": message,
    }
    write_json(run_dir / "00-error.json", payload)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
US runner.

Mechanical control plane for Universal Structure discovery.
US runs before UP and produces the invariant set that UP must consume.

IMO
- Input:
  - A medium
  - An operator intent
  - Prior US runs, if they exist
  - Human-owned tolerances before final handoff
- Middle:
  - Discover medium layers using Three Primitives
  - Apply C&V to every layer
  - Validate depth, parentage, and invariant integrity mechanically
  - Keep the run provisional until repeated passes exist
  - Require human-owned tolerances before writing a handoff-ready artifact
- Output:
  - 01-us.json
  - optional 02-us-ready.json
  - Versioned US run directory
  - Machine-readable error receipts

CTB
- Trunk:
  - US is the branch control plane that discovers the medium structure
- Branches:
  - Layer discovery
  - Reverse route
  - Invariant set
  - Handoff contract
- Leaves:
  - 01-us.json
  - 02-us-ready.json
  - ts-us-tolerances.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


UP_ROOT = Path(__file__).resolve().parent
REPO_ROOT = UP_ROOT.parents[2]

US_ARTIFACT = "01-us.json"
US_READY_ARTIFACT = "02-us-ready.json"
US_TOLERANCES_ARTIFACT = "ts-us-tolerances.json"
MIN_RUNS_FOR_HANDOFF = 3
LEGAL_PRIMITIVES = {"Thing", "Flow", "Change"}
LEGAL_LAYER_CV = {"constant", "variable", "unidentified"}

READING_LIST = [
    REPO_ROOT / "law/doctrine/FOUNDATIONAL_BEDROCK.md",
    REPO_ROOT / "law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md",
    REPO_ROOT / "law/doctrine/DMJ.md",
]


@dataclass
class UsContext:
    medium: str
    intent: str
    output_dir: Path
    max_depth: int


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="US runner")
    parser.add_argument("medium", help="The medium to decompose")
    parser.add_argument("intent", help="The operator's intended use of this medium")
    parser.add_argument("--output-dir", help="Directory for the US run", default=None)
    parser.add_argument("--max-depth", type=int, default=10, help="Maximum decomposition depth")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = resolve_output_dir(args.medium, args.output_dir)
    ctx = UsContext(
        medium=args.medium,
        intent=args.intent,
        output_dir=output_dir,
        max_depth=args.max_depth,
    )
    save_run_metadata(ctx)
    return run_us(ctx)


def resolve_output_dir(medium: str, output_dir: str | None) -> Path:
    if output_dir:
        return Path(output_dir).expanduser().resolve()
    slug = slugify(medium)
    run_root = UP_ROOT / "us-runs" / slug
    run_root.mkdir(parents=True, exist_ok=True)
    existing = sorted(p.name for p in run_root.iterdir() if p.is_dir() and p.name.startswith("run-"))
    next_num = 1
    if existing:
        nums = [int(name.split("-")[1]) for name in existing if name.split("-")[1].isdigit()]
        if nums:
            next_num = max(nums) + 1
    return run_root / f"run-{next_num:03d}"


def slugify(value: str) -> str:
    slug = value.strip().lower()
    for old, new in (("/", "-"), (" ", "-"), ("_", "-")):
        slug = slug.replace(old, new)
    return "".join(ch for ch in slug if ch.isalnum() or ch == "-")[:40] or "medium"


def save_run_metadata(ctx: UsContext) -> None:
    ctx.output_dir.mkdir(parents=True, exist_ok=True)
    (ctx.output_dir / "receipts").mkdir(exist_ok=True)
    write_json(
        ctx.output_dir / "run.json",
        {
            "created_at": now_utc(),
            "medium": ctx.medium,
            "intent": ctx.intent,
            "max_depth": ctx.max_depth,
            "repo_root": str(REPO_ROOT),
            "run_number": parse_run_number(ctx.output_dir),
            "min_runs_for_handoff": MIN_RUNS_FOR_HANDOFF,
        },
    )
    (ctx.output_dir / "medium.txt").write_text(ctx.medium + "\n")
    (ctx.output_dir / "intent.txt").write_text(ctx.intent + "\n")


def run_us(ctx: UsContext) -> int:
    missing = [str(path) for path in READING_LIST if not path.exists()]
    if missing:
        write_error(ctx.output_dir, f"MISSING READING FILES: {missing}")
        return 1

    # --- Determine execution mode: OpenRouter (API) or Claude CLI (subprocess) ---
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    use_openrouter = bool(openrouter_key)

    if use_openrouter:
        return run_us_openrouter(ctx, openrouter_key)
    else:
        return run_us_claude_cli(ctx)


def run_us_openrouter(ctx: UsContext, api_key: str) -> int:
    """Run US discovery via OpenRouter API — any model, no subprocess."""
    model = os.environ.get("UP_BUILD_MODEL", "google/gemini-2.5-pro-preview")
    max_tokens = int(os.environ.get("UP_MAX_TOKENS", "8000"))
    daily_budget = float(os.environ.get("UP_DAILY_BUDGET", "5.00"))
    temperature = float(os.environ.get("UP_TEMPERATURE", "0.3"))

    # --- Throttle: check daily spend ---
    spend_log = ctx.output_dir.parent / "openrouter-spend.json"
    daily_spend = check_daily_spend(spend_log)
    if daily_spend >= daily_budget:
        write_error(ctx.output_dir, f"DAILY BUDGET EXCEEDED: ${daily_spend:.2f} >= ${daily_budget:.2f}")
        return 1

    # --- Build self-contained prompt with doctrine content inline ---
    prompt = build_openrouter_prompt(ctx)
    receipt_base = ctx.output_dir / "receipts" / "us"
    receipt_base.with_suffix(".prompt.txt").write_text(prompt)

    system_msg = (
        "You are the US (Universal Structure) discovery agent. "
        "You discover the layers of any medium using Three Primitives (Thing, Flow, Change) "
        "and Constant/Variable classification. Every layer must be grounded in exactly one primitive. "
        "Constants have structure (name + format). Variables are the fill. "
        "Zoom into non-domesticated layers — fractal. Stop at operational tolerance. "
        "Output ONLY valid JSON matching the schema provided. No commentary, no markdown, just JSON."
    )

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    # Add system message — OpenRouter supports both formats
    if "/" in model and "anthropic" in model:
        # Anthropic models use top-level system
        payload["system"] = system_msg
    else:
        # Other models: prepend as system in messages
        payload["messages"].insert(0, {"role": "user", "content": f"[SYSTEM]: {system_msg}"})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://imo-creator.svg.agency",
        "X-Title": "IMO Creator Dyno",
    }

    print(f"US via OpenRouter: model={model} max_tokens={max_tokens}")
    receipt_base.with_suffix(".model.txt").write_text(f"{model}\n")

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        write_error(ctx.output_dir, f"OPENROUTER HTTP {e.code}: {body[:500]}")
        receipt_base.with_suffix(".error.log").write_text(body)
        return 1
    except Exception as e:
        write_error(ctx.output_dir, f"OPENROUTER ERROR: {e}")
        return 1

    # --- Extract response ---
    receipt_base.with_suffix(".response.json").write_text(json.dumps(response_data, indent=2))

    content = ""
    if "choices" in response_data and response_data["choices"]:
        msg = response_data["choices"][0].get("message", {})
        content = msg.get("content", "")
    elif "content" in response_data:
        # Anthropic Messages API format
        for block in response_data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

    receipt_base.with_suffix(".stdout.log").write_text(content)

    # --- Log spend ---
    usage = response_data.get("usage", {})
    cost_entry = {
        "timestamp": now_utc(),
        "model": model,
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "medium": ctx.medium,
    }
    log_spend(spend_log, cost_entry)
    print(f"  tokens: {cost_entry['tokens_in']} in, {cost_entry['tokens_out']} out")

    # --- Extract JSON from response ---
    json_str = extract_json(content)
    if not json_str:
        write_error(ctx.output_dir, "OPENROUTER: no valid JSON found in response")
        return 1

    artifact_path = ctx.output_dir / US_ARTIFACT
    artifact_path.write_text(json_str)

    validate_us_artifact(artifact_path, ctx.max_depth)
    return finish_us_run(ctx)


def run_us_claude_cli(ctx: UsContext) -> int:
    """Original: run US via Claude CLI subprocess."""
    prompt = build_prompt(ctx)
    receipt_base = ctx.output_dir / "receipts" / "us"
    receipt_base.with_suffix(".prompt.txt").write_text(prompt)

    claude_bin = os.environ.get("UP_CLAUDE_BIN", "claude")
    model = os.environ.get("UP_BUILD_MODEL", "builder")
    timeout_seconds = int(os.environ.get("UP_AGENT_TIMEOUT", "600"))
    cmd = [
        claude_bin,
        "--print",
        "--model",
        model,
        "--allowedTools",
        "Read,Bash,Write,Grep,Glob",
        "-p",
        prompt,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        write_error(ctx.output_dir, f"US TIMEOUT: {ctx.medium}")
        return 1
    except FileNotFoundError:
        write_error(ctx.output_dir, f"US BINARY NOT FOUND: {claude_bin}")
        return 1

    receipt_base.with_suffix(".stdout.log").write_text(result.stdout)
    receipt_base.with_suffix(".stderr.log").write_text(result.stderr)
    receipt_base.with_suffix(".cmd.txt").write_text(" ".join(cmd))

    if result.returncode != 0:
        write_error(ctx.output_dir, f"US FAILED: exit={result.returncode}")
        return 1

    validate_us_artifact(ctx.output_dir / US_ARTIFACT, ctx.max_depth)
    return finish_us_run(ctx)


def finish_us_run(ctx: UsContext) -> int:
    """Common finish logic for both OpenRouter and Claude CLI paths."""
    print(f"US artifact: {ctx.output_dir / US_ARTIFACT}")
    completed_runs = count_completed_runs(ctx.output_dir)
    if completed_runs < MIN_RUNS_FOR_HANDOFF:
        print(f"US remains provisional: {completed_runs}/{MIN_RUNS_FOR_HANDOFF} completed runs")
        print(f"No UP handoff until repeated runs stabilize and human tolerances are set")
        return 0
    if not validate_us_tolerances(ctx.output_dir):
        print(f"US remains provisional: missing or invalid {US_TOLERANCES_ARTIFACT}")
        print("No UP handoff until a human sets tolerances")
        return 0

    write_json(
        ctx.output_dir / US_READY_ARTIFACT,
        {
            "ready_at": now_utc(),
            "source_artifact": US_ARTIFACT,
            "completed_runs": completed_runs,
            "min_runs_for_handoff": MIN_RUNS_FOR_HANDOFF,
            "tolerances_artifact": US_TOLERANCES_ARTIFACT,
            "set_by": "human",
            "medium": ctx.medium,
            "intent": ctx.intent,
        },
    )
    print(f"US ready artifact: {ctx.output_dir / US_READY_ARTIFACT}")
    print("Ready for UP handoff")
    return 0


def build_openrouter_prompt(ctx: UsContext) -> str:
    """Build a self-contained prompt with doctrine content inline (no file reads)."""
    # Read doctrine files and include content directly
    doctrine_content = []
    for path in READING_LIST:
        if path.exists():
            content = path.read_text()
            # Truncate to key sections to fit token budget
            if len(content) > 4000:
                content = content[:4000] + "\n[...truncated for token budget...]"
            doctrine_content.append(f"--- {path.name} ---\n{content}")

    doctrine_text = "\n\n".join(doctrine_content)

    return f"""DOCTRINE (read first):

{doctrine_text}

---

DISCOVER THIS MEDIUM:
    medium: {ctx.medium}
    intent: {ctx.intent}
    max_depth: {ctx.max_depth}

OUTPUT: Return ONLY valid JSON (no markdown fences, no commentary) in this exact shape:
{{
  "medium": "{ctx.medium}",
  "intent": "{ctx.intent}",
  "discovered_at": "<timestamp>",
  "total_layers": <int>,
  "max_depth_reached": <int>,
  "domestication_depth": <int>,
  "reverse_route": {{
    "target_value": "<what P=1 means>",
    "route": ["value", "property", "type", "layer", "medium"],
    "depth": <int>
  }},
  "layers": [
    {{
      "id": "L1",
      "name": "<layer name>",
      "description": "<optional — plain-language explanation of what this is. US leaves empty. Filled by human or downstream process.>",
      "primitive": "Thing|Flow|Change",
      "format": "<what it structurally contains>",
      "depth": 0,
      "parent": null,
      "cv": "constant|variable|unidentified",
      "domesticated": false,
      "zoom_reason": "<why zoom or stop>"
    }}
  ],
  "invariant_set": [
    {{
      "layer_id": "L1",
      "name": "<layer name>",
      "primitive": "Thing|Flow|Change",
      "why_it_matters": "<why>",
      "comparator_hint": "<what to measure>"
    }}
  ],
  "handoff_contract": {{
    "required_by_up": ["layers", "invariant_set", "reverse_route", "domestication_depth"],
    "medium_slug": "{slugify(ctx.medium)}",
    "requires_human_tolerances": true,
    "min_runs_for_handoff": {MIN_RUNS_FOR_HANDOFF}
  }}
}}

METHOD:
1. Start at the medium root
2. At every level, classify by Three Primitives: Thing, Flow, Change
3. Apply C&V: name it, format it, classify constant/variable
4. Zoom deeper if decomposition changes outcomes for this intent
5. Stop when domesticated or max_depth reached
6. Reverse-check route from target value back to medium
7. Every layer maps to exactly one primitive
8. Every invariant_set entry references a real layer_id
"""


def extract_json(text: str) -> str | None:
    """Extract the first valid JSON object from LLM response text."""
    # Try direct parse first
    text = text.strip()
    if text.startswith("{"):
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

    # Try to find JSON between markdown fences
    import re
    patterns = [
        r"```json\s*\n(.*?)\n```",
        r"```\s*\n(.*?)\n```",
        r"(\{.*\})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            candidate = match.group(1).strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                continue
    return None


def check_daily_spend(spend_log: Path) -> float:
    """Check today's total spend from the log."""
    if not spend_log.exists():
        return 0.0
    try:
        entries = json.loads(spend_log.read_text())
    except (json.JSONDecodeError, Exception):
        return 0.0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return sum(
        e.get("tokens_out", 0) * 0.00001  # rough estimate: $10/1M output tokens avg
        for e in entries
        if e.get("timestamp", "").startswith(today)
    )


def log_spend(spend_log: Path, entry: dict) -> None:
    """Append a spend entry to the daily log."""
    entries = []
    if spend_log.exists():
        try:
            entries = json.loads(spend_log.read_text())
        except (json.JSONDecodeError, Exception):
            entries = []
    entries.append(entry)
    spend_log.write_text(json.dumps(entries, indent=2) + "\n")


def build_prompt(ctx: UsContext) -> str:
    reading = "\n".join(f"    {index + 1}. Read: {path}" for index, path in enumerate(READING_LIST))
    return f"""
You are the US (Universal Structure) discovery agent.

US runs BEFORE UP.
US discovers the medium layers and writes the invariant set.
US does not know downstream business logic. It only discovers the medium structure needed for this intent.

BEFORE YOU DO ANYTHING, read these files in order:

{reading}

THEN DISCOVER THIS MEDIUM:
    medium: {ctx.medium}
    intent: {ctx.intent}
    max_depth: {ctx.max_depth}

OUTPUT RULES:
    - Write exactly one file: {US_ARTIFACT}
    - Save it into: {ctx.output_dir}/
    - Do not write any other JSON artifact

ARTIFACT SHAPE:
{{
  "medium": "{ctx.medium}",
  "intent": "{ctx.intent}",
  "discovered_at": "<timestamp>",
  "total_layers": <int>,
  "max_depth_reached": <int>,
  "domestication_depth": <int>,
  "reverse_route": {{
    "target_value": "<what the intent ultimately needs>",
    "route": ["value", "property", "type", "layer", "medium"],
    "depth": <int>
  }},
  "layers": [
    {{
      "id": "L1",
      "name": "<layer name>",
      "description": "<optional — plain-language explanation. US may leave empty. Filled by human or downstream.>",
      "primitive": "Thing|Flow|Change",
      "format": "<what it structurally contains>",
      "depth": 0,
      "parent": null,
      "cv": "constant|variable|unidentified",
      "domesticated": false,
      "zoom_reason": "<why this branch zooms or stops>"
    }}
  ],
  "invariant_set": [
    {{
      "layer_id": "L1",
      "name": "<layer name>",
      "primitive": "Thing|Flow|Change",
      "why_it_matters": "<why UP must care about this layer>",
      "comparator_hint": "<what deviation comparator would measure here>"
    }}
  ],
        "handoff_contract": {{
            "required_by_up": ["layers", "invariant_set", "reverse_route", "domestication_depth"],
            "medium_slug": "{slugify(ctx.medium)}",
            "requires_human_tolerances": true,
            "min_runs_for_handoff": {MIN_RUNS_FOR_HANDOFF}
        }}
}}

METHOD:
    1. Start at the medium itself.
    2. At every level, classify only by Three Primitives:
       - Thing
       - Flow
       - Change
    3. Apply C&V to every layer:
       - name it
       - define its format
       - classify it as constant, variable, or unidentified
    4. Keep zooming deeper only if deeper decomposition changes outcomes for THIS intent.
    5. Stop when the branch is domesticated or max_depth is reached.
    6. Reverse-check the route from target value back to the medium.

STRICT RULES:
    - Every layer must map to exactly one primitive.
    - Every invariant_set entry must reference a real layer_id.
    - reverse_route.depth must match the number of route items.
    - The invariant_set must only contain layers that matter for this intent.
    - If the medium or intent is too ambiguous to discover honestly, still write {US_ARTIFACT} with:
      "refused": true
      "refused_reason": "<why discovery cannot proceed>"
"""


def validate_us_artifact(path: Path, max_depth_limit: int) -> None:
    if not path.exists():
        raise SystemExit(write_error(path.parent, f"MISSING ARTIFACT: {US_ARTIFACT}"))

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        raise SystemExit(write_error(path.parent, f"INVALID JSON: {US_ARTIFACT}"))

    if data.get("refused"):
        if not data.get("refused_reason"):
            raise SystemExit(write_error(path.parent, "REFUSED US artifact missing refused_reason"))
        return

    required = [
        "medium",
        "intent",
        "discovered_at",
        "total_layers",
        "max_depth_reached",
        "domestication_depth",
        "reverse_route",
        "layers",
        "invariant_set",
        "handoff_contract",
    ]
    missing = [field for field in required if field not in data]
    if missing:
        raise SystemExit(write_error(path.parent, f"MISSING FIELDS in {US_ARTIFACT}: {missing}"))

    if not isinstance(data["layers"], list) or not data["layers"]:
        raise SystemExit(write_error(path.parent, "layers must be a non-empty list"))
    if not isinstance(data["invariant_set"], list) or not data["invariant_set"]:
        raise SystemExit(write_error(path.parent, "invariant_set must be a non-empty list"))

    route = data["reverse_route"]
    if not isinstance(route, dict):
        raise SystemExit(write_error(path.parent, "reverse_route must be an object"))
    for key in ("target_value", "route", "depth"):
        if key not in route:
            raise SystemExit(write_error(path.parent, f"reverse_route missing {key}"))
    if not isinstance(route["route"], list) or not route["route"]:
        raise SystemExit(write_error(path.parent, "reverse_route.route must be a non-empty list"))
    if route["depth"] != len(route["route"]):
        raise SystemExit(write_error(path.parent, "reverse_route.depth must equal len(reverse_route.route)"))

    layer_ids: set[str] = set()
    layer_depths: dict[str, int] = {}
    max_depth_reached = -1
    for index, layer in enumerate(data["layers"]):
        require_keys(path.parent, layer, ["id", "name", "primitive", "format", "depth", "parent", "cv", "domesticated", "zoom_reason"], f"layers[{index}]")
        if layer["primitive"] not in LEGAL_PRIMITIVES:
            raise SystemExit(write_error(path.parent, f"layers[{index}].primitive must be one of {sorted(LEGAL_PRIMITIVES)}"))
        if layer["cv"] not in LEGAL_LAYER_CV:
            raise SystemExit(write_error(path.parent, f"layers[{index}].cv must be one of {sorted(LEGAL_LAYER_CV)}"))
        if not isinstance(layer["depth"], int) or layer["depth"] < 0:
            raise SystemExit(write_error(path.parent, f"layers[{index}].depth must be a non-negative integer"))
        if layer["depth"] > max_depth_limit:
            raise SystemExit(write_error(path.parent, f"layers[{index}].depth exceeds max_depth limit {max_depth_limit}"))
        if layer["id"] in layer_ids:
            raise SystemExit(write_error(path.parent, f"duplicate layer id: {layer['id']}"))
        layer_ids.add(layer["id"])
        layer_depths[layer["id"]] = layer["depth"]
        max_depth_reached = max(max_depth_reached, layer["depth"])

    if data["total_layers"] != len(data["layers"]):
        raise SystemExit(write_error(path.parent, "total_layers must equal len(layers)"))
    if data["max_depth_reached"] != max_depth_reached:
        raise SystemExit(write_error(path.parent, "max_depth_reached must equal max(layer.depth)"))
    if data["max_depth_reached"] > max_depth_limit:
        raise SystemExit(write_error(path.parent, f"max_depth_reached exceeds max_depth limit {max_depth_limit}"))
    if not isinstance(data["domestication_depth"], int) or data["domestication_depth"] < 0:
        raise SystemExit(write_error(path.parent, "domestication_depth must be a non-negative integer"))
    if data["domestication_depth"] > max_depth_limit:
        raise SystemExit(write_error(path.parent, f"domestication_depth exceeds max_depth limit {max_depth_limit}"))

    for index, layer in enumerate(data["layers"]):
        parent = layer["parent"]
        if parent is None:
            if layer["depth"] != 0:
                raise SystemExit(write_error(path.parent, f"layers[{index}] with parent null must have depth 0"))
            continue
        if not isinstance(parent, str) or not parent:
            raise SystemExit(write_error(path.parent, f"layers[{index}].parent must be null or a non-empty layer id"))
        if parent == layer["id"]:
            raise SystemExit(write_error(path.parent, f"layers[{index}] cannot parent itself"))
        if parent not in layer_ids:
            raise SystemExit(write_error(path.parent, f"layers[{index}].parent does not reference a real layer"))
        if layer_depths[parent] >= layer["depth"]:
            raise SystemExit(write_error(path.parent, f"layers[{index}].parent must be shallower than child"))

    for index, invariant in enumerate(data["invariant_set"]):
        require_keys(
            path.parent,
            invariant,
            ["layer_id", "name", "primitive", "why_it_matters", "comparator_hint"],
            f"invariant_set[{index}]",
        )
        if invariant["layer_id"] not in layer_ids:
            raise SystemExit(write_error(path.parent, f"invariant_set[{index}].layer_id does not reference a real layer"))
        if invariant["primitive"] not in LEGAL_PRIMITIVES:
            raise SystemExit(write_error(path.parent, f"invariant_set[{index}].primitive must be one of {sorted(LEGAL_PRIMITIVES)}"))

    handoff = data["handoff_contract"]
    if not isinstance(handoff, dict):
        raise SystemExit(write_error(path.parent, "handoff_contract must be an object"))
    require_keys(path.parent, handoff, ["required_by_up", "medium_slug"], "handoff_contract")
    if not isinstance(handoff["required_by_up"], list) or not handoff["required_by_up"]:
        raise SystemExit(write_error(path.parent, "handoff_contract.required_by_up must be a non-empty list"))
    if handoff["medium_slug"] != slugify(data["medium"]):
        raise SystemExit(write_error(path.parent, "handoff_contract.medium_slug must match medium slug"))


def parse_run_number(output_dir: Path) -> int:
    try:
        return int(output_dir.name.split("-")[1])
    except (IndexError, ValueError):
        return 0


def count_completed_runs(output_dir: Path) -> int:
    return sum(1 for candidate in output_dir.parent.glob("run-*") if (candidate / US_ARTIFACT).exists())


def validate_us_tolerances(output_dir: Path) -> bool:
    path = output_dir / US_TOLERANCES_ARTIFACT
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return False

    required = ["set_by", "approved_at", "tolerances"]
    if any(field not in data for field in required):
        return False
    if data["set_by"] != "human":
        return False
    if not isinstance(data["tolerances"], dict) or not data["tolerances"]:
        return False
    return True


def require_keys(run_dir: Path, payload: Any, keys: list[str], scope: str) -> None:
    if not isinstance(payload, dict):
        raise SystemExit(write_error(run_dir, f"{scope} must be an object"))
    missing = [key for key in keys if key not in payload]
    if missing:
        raise SystemExit(write_error(run_dir, f"{scope} missing keys: {missing}"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_error(output_dir: Path, message: str) -> int:
    write_json(
        output_dir / "00-error.json",
        {
            "timestamp": now_utc(),
            "message": message,
        },
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

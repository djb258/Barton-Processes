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


# ═══════════════════════════════════════════════════════════════
# SHARED LAYER OUTPUT SPEC — single source of truth.
# Both prompt builders (build_prompt for Claude CLI + build_openrouter_prompt
# for OpenRouter) reference these constants. DO NOT duplicate the layer
# schema inline — use these. Any change to the expected output shape MUST
# happen here and here alone.
# Enforces KEY.md 10th locked constant: the 7-field KEY vocabulary.
# ═══════════════════════════════════════════════════════════════

LAYER_SCHEMA_SPEC = """{
      "id": "L1",
      "name": "<layer name — the TERM>",
      "description": "<2-3 sentence plain-language explanation using the primitive's language: Thing=exists/object/component, Flow=moves/transfers/routes, Change=transforms/transitions/converts>",
      "primitive": "Thing|Flow|Change",
      "format": "<what it structurally contains>",
      "depth": 0,
      "parent": null,
      "cv": "constant|variable|unidentified",
      "domesticated": false,
      "zoom_reason": "<why this branch zooms or stops>",
      "vocabulary": {
        "abbreviation": "<shorthand or - if none>",
        "description": "<what it IS — 2-3 sentences using the primitive's language>",
        "behavior": "<what it DOES — the mechanical action in the system>",
        "context": "<when you see it — the situation that triggers its presence>",
        "example": "<one concrete specific instance from THIS domain, not abstract>"
      }
    }"""

LAYER_FILLED_EXAMPLE_THING = """{
  "id": "L1",
  "name": "Capital",
  "description": "An accumulated store of financial resources available for deployment into investment positions.",
  "primitive": "Thing",
  "format": "A quantified monetary pool denominated in a currency",
  "depth": 1,
  "parent": null,
  "cv": "constant",
  "domesticated": false,
  "zoom_reason": "Capital decomposes into liquid vs illiquid, deployed vs reserved",
  "vocabulary": {
    "abbreviation": "CAP",
    "description": "Capital is the accumulated financial resource pool that exists prior to any investment decision. It is the substrate that gets deployed.",
    "behavior": "Sits as a reserve until a decision deploys it into a position; does not move on its own.",
    "context": "Present at the start of every investment cycle; anchor of every allocation decision.",
    "example": "$500,000 in a money-market fund awaiting deployment into equities"
  }
}"""

LAYER_FILLED_EXAMPLE_FLOW = """{
  "id": "L2",
  "name": "Capital Deployment",
  "description": "The transfer of capital from reserve into an active position. Movement from idle to working state.",
  "primitive": "Flow",
  "format": "A sequence of instructions routing funds from source account to target instrument",
  "depth": 1,
  "parent": null,
  "cv": "constant",
  "domesticated": false,
  "zoom_reason": "Deployment decomposes into authorization, transfer, and settlement flows",
  "vocabulary": {
    "abbreviation": "DEPLOY",
    "description": "Capital Deployment is the directed movement of funds from the reserve pool into an active investment. It is the flow that connects the decision to the position.",
    "behavior": "Routes approved capital through a broker or custodian into the target instrument; terminates when settlement completes.",
    "context": "Triggered after an allocation decision passes risk review; observed on every new position entry.",
    "example": "Wire of $250k from money-market fund to equity brokerage, settling T+2."
  }
}"""

LAYER_FILLED_EXAMPLE_CHANGE = """{
  "id": "L3",
  "name": "Position Appreciation",
  "description": "The transformation of a position's market value upward over time. The state transition from entry price to higher price.",
  "primitive": "Change",
  "format": "A delta between entry value and current mark-to-market value, expressed as percentage or absolute amount",
  "depth": 1,
  "parent": null,
  "cv": "variable",
  "domesticated": false,
  "zoom_reason": "Appreciation decomposes into unrealized vs realized, price-driven vs dividend-driven",
  "vocabulary": {
    "abbreviation": "APPREC",
    "description": "Position Appreciation is the upward transformation of a held position's market value. The state transitions from entry price to a higher current price without any further capital deployment.",
    "behavior": "Increases the mark-to-market value of the holding; accumulates or reverses on every market tick.",
    "context": "Observed on every mark-to-market cycle after entry; the primary driver of portfolio return.",
    "example": "Position entered at $50/share, marked at $62/share after 90 days — 24% unrealized appreciation."
  }
}"""

LAYER_FILLED_EXAMPLE = LAYER_FILLED_EXAMPLE_THING  # back-compat alias

VOCABULARY_REQUIREMENT_BLOCK = """CRITICAL — KEY.MD VOCABULARY REQUIREMENT (NON-NEGOTIABLE):
Every single layer MUST contain a `vocabulary` object with all 5 fields populated as non-empty strings:
  - abbreviation
  - description
  - behavior
  - context
  - example
A layer missing ANY of these 5 fields is INVALID and will be REJECTED by the downstream auditor.
The output is the locked constant; do not return layers without a complete `vocabulary` object.

PRIMITIVE enum: exactly one of "Thing" | "Flow" | "Change". Exact capitalization. No aliases, no suffixes, no rescue.

Every invariant_set entry MUST include `layer_id` referencing a real layer in the `layers` array.

THREE FILLED EXAMPLES — one per primitive. Follow the shape for every layer you emit.
Match the primitive's language pattern:
  - Thing descriptions use "exists / component / object / pool / container" language
  - Flow descriptions use "moves / routes / transfers / transports" language
  - Change descriptions use "transforms / transitions / converts / state change" language

EXAMPLE 1 (Thing):
""" + LAYER_FILLED_EXAMPLE_THING + """

EXAMPLE 2 (Flow):
""" + LAYER_FILLED_EXAMPLE_FLOW + """

EXAMPLE 3 (Change):
""" + LAYER_FILLED_EXAMPLE_CHANGE


# ═══════════════════════════════════════════════════════════════
# US_OUTPUT_SCHEMA — strict JSON schema enforced at the OpenRouter boundary.
# Non-conformant responses are rejected by the API before we ever parse them.
# Every required field must be declared + listed in `required`.
# additionalProperties: false at every level (strict mode requirement).
# ═══════════════════════════════════════════════════════════════

_LAYER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "id", "name", "description", "primitive", "format",
        "depth", "parent", "cv", "domesticated", "zoom_reason",
        "vocabulary",
    ],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "primitive": {"type": "string", "enum": ["Thing", "Flow", "Change"]},
        "format": {"type": "string"},
        "depth": {"type": "integer", "minimum": 0},
        "parent": {"type": ["string", "null"]},
        "cv": {"type": "string", "enum": ["constant", "variable", "unidentified"]},
        "domesticated": {"type": "boolean"},
        "zoom_reason": {"type": "string"},
        "vocabulary": {
            "type": "object",
            "additionalProperties": False,
            "required": ["abbreviation", "description", "behavior", "context", "example"],
            "properties": {
                "abbreviation": {"type": "string", "minLength": 1},
                "description": {"type": "string", "minLength": 1},
                "behavior": {"type": "string", "minLength": 1},
                "context": {"type": "string", "minLength": 1},
                "example": {"type": "string", "minLength": 1},
            },
        },
    },
}

_INVARIANT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["layer_id", "name", "primitive", "why_it_matters", "comparator_hint"],
    "properties": {
        "layer_id": {"type": "string"},
        "name": {"type": "string"},
        "primitive": {"type": "string", "enum": ["Thing", "Flow", "Change"]},
        "why_it_matters": {"type": "string"},
        "comparator_hint": {"type": "string"},
    },
}

_REVERSE_ROUTE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["target_value", "route", "depth"],
    "properties": {
        "target_value": {"type": "string"},
        "route": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "depth": {"type": "integer", "minimum": 1},
    },
}

_HANDOFF_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "required_by_up", "medium_slug",
        "requires_human_tolerances", "min_runs_for_handoff",
    ],
    "properties": {
        "required_by_up": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "medium_slug": {"type": "string"},
        "requires_human_tolerances": {"type": "boolean"},
        "min_runs_for_handoff": {"type": "integer", "minimum": 1},
    },
}

US_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "medium", "intent", "discovered_at",
        "total_layers", "max_depth_reached", "domestication_depth",
        "reverse_route", "layers", "invariant_set", "handoff_contract",
    ],
    "properties": {
        "medium": {"type": "string"},
        "intent": {"type": "string"},
        "discovered_at": {"type": "string"},
        "total_layers": {"type": "integer", "minimum": 1},
        "max_depth_reached": {"type": "integer", "minimum": 0},
        "domestication_depth": {"type": "integer", "minimum": 0},
        "reverse_route": _REVERSE_ROUTE_SCHEMA,
        "layers": {"type": "array", "items": _LAYER_SCHEMA, "minItems": 1},
        "invariant_set": {"type": "array", "items": _INVARIANT_SCHEMA, "minItems": 1},
        "handoff_contract": _HANDOFF_SCHEMA,
    },
}


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
    (ctx.output_dir / "medium.txt").write_text(ctx.medium + "\n", encoding='utf-8')
    (ctx.output_dir / "intent.txt").write_text(ctx.intent + "\n", encoding='utf-8')


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
    receipt_base.with_suffix(".prompt.txt").write_text(prompt, encoding='utf-8')

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
        # STRICT SCHEMA ENFORCEMENT AT THE API BOUNDARY.
        # Non-conformant output is rejected before we ever parse it — this prevents
        # silent drift like "invariant_set[2] missing keys: layer_id" by forcing the
        # provider to honor every required field.
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "us_output",
                "strict": True,
                "schema": US_OUTPUT_SCHEMA,
            },
        },
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
    receipt_base.with_suffix(".model.txt").write_text(f"{model}\n", encoding='utf-8')

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
        receipt_base.with_suffix(".error.log").write_text(body, encoding='utf-8')
        return 1
    except Exception as e:
        write_error(ctx.output_dir, f"OPENROUTER ERROR: {e}")
        return 1

    # --- Extract response ---
    receipt_base.with_suffix(".response.json").write_text(json.dumps(response_data, indent=2), encoding='utf-8')

    content = ""
    if "choices" in response_data and response_data["choices"]:
        msg = response_data["choices"][0].get("message", {})
        content = msg.get("content", "")
    elif "content" in response_data:
        # Anthropic Messages API format
        for block in response_data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

    receipt_base.with_suffix(".stdout.log").write_text(content, encoding='utf-8')

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
    artifact_path.write_text(json_str, encoding='utf-8')

    validate_us_artifact(artifact_path, ctx.max_depth)
    return finish_us_run(ctx)


def run_us_claude_cli(ctx: UsContext) -> int:
    """Original: run US via Claude CLI subprocess."""
    prompt = build_prompt(ctx)
    receipt_base = ctx.output_dir / "receipts" / "us"
    receipt_base.with_suffix(".prompt.txt").write_text(prompt, encoding='utf-8')

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

    receipt_base.with_suffix(".stdout.log").write_text(result.stdout, encoding='utf-8')
    receipt_base.with_suffix(".stderr.log").write_text(result.stderr, encoding='utf-8')
    receipt_base.with_suffix(".cmd.txt").write_text(" ".join(cmd), encoding='utf-8')

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
            content = path.read_text(encoding='utf-8')
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
    {LAYER_SCHEMA_SPEC}
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

{VOCABULARY_REQUIREMENT_BLOCK}

METHOD:
1. Start at the medium root
2. At every level, classify by Three Primitives: Thing, Flow, Change
3. Apply C&V: name it, format it, classify constant/variable
4. Zoom deeper if decomposition changes outcomes for this intent
5. Stop when domesticated or max_depth reached
6. Reverse-check route from target value back to medium
7. Every layer maps to exactly one primitive
8. Every layer includes a complete `vocabulary` object (5 fields, non-empty). No exceptions.
9. Every invariant_set entry references a real layer_id
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
        entries = json.loads(spend_log.read_text(encoding='utf-8'))
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
            entries = json.loads(spend_log.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, Exception):
            entries = []
    entries.append(entry)
    spend_log.write_text(json.dumps(entries, indent=2) + "\n", encoding='utf-8')


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
    {LAYER_SCHEMA_SPEC}
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

{VOCABULARY_REQUIREMENT_BLOCK}

STRICT RULES:
    - Every layer must map to exactly one primitive.
    - Every layer must contain a complete `vocabulary` object (5 fields, non-empty strings). No exceptions.
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
        data = json.loads(path.read_text(encoding='utf-8'))
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
    # Vocabulary enforcement is DELEGATED to the auditor (Codex plugin).
    # This validator only checks structural skeleton; vocabulary completeness
    # is the auditor's job per FAA protocol. Let us_v2.py write what the LLM
    # returned; the auditor gates it downstream.
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
        data = json.loads(path.read_text(encoding='utf-8'))
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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding='utf-8')


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

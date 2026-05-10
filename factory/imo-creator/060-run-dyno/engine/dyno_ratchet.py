#!/usr/bin/env python3
"""
Dyno Ratchet — The domain-agnostic orchestrator.

The ratchet turns the same way every time. The socket (domain) is what
touches the bolt. Different bolt, different socket, same ratchet.

14 steps. Repeatable. Domain-agnostic. Every step is an IMO. Every IMO is logged.

Does NOT modify us.py (#7) or up.py (#8) — those are locked engines.
Does NOT know about outreach, diabetes, COPD, or any domain.
Sockets (domain adapters) plug into the ratchet.

Usage:
    python3 dyno_ratchet.py us "medium" "intent"
    python3 dyno_ratchet.py us "medium" "intent" --models claude,gemini,gpt4o
    python3 dyno_ratchet.py up "medium" "intent" --us-run path/to/04-us-consolidated.json
    python3 dyno_ratchet.py zoom "medium" "intent" --layer C11 --parent path/to/04-us-consolidated.json
    python3 dyno_ratchet.py full "medium" "intent"  # US → human gate → UP
    python3 dyno_ratchet.py status path/to/run/
    python3 dyno_ratchet.py chain path/to/run/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════════════
# CONSTANTS — the ratchet's geometry. Does not change.
# ═══════════════════════════════════════════════════════════════

UP_ROOT = Path(__file__).resolve().parent
REPO_ROOT = UP_ROOT.parents[2]
RUNS_DIR = UP_ROOT / "runs"

READING_LIST = [
    REPO_ROOT / "law/doctrine/FOUNDATIONAL_BEDROCK.md",
    REPO_ROOT / "law/doctrine/TIER0_MATHEMATICAL_PRINCIPLE.md",
    REPO_ROOT / "law/doctrine/DMJ.md",
]

DEFAULT_MODELS = [
    "anthropic/claude-sonnet-4",
    "google/gemini-2.5-pro-preview",
    "openai/gpt-4o",
]

CONSOLIDATION_MODEL = "anthropic/claude-sonnet-4"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

LBB_URL = os.environ.get("LBB_URL", "https://lbb.svg-outreach.workers.dev")


# ═══════════════════════════════════════════════════════════════
# CONTEXT — what the ratchet carries through all 14 steps
# ═══════════════════════════════════════════════════════════════

@dataclass
class RatchetContext:
    medium: str
    intent: str
    run_dir: Path
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    models: list[str] = field(default_factory=lambda: list(DEFAULT_MODELS))
    max_tokens: int = 8000
    temperature: float = 0.3
    daily_budget: float = 5.0
    history: str = ""
    us_outputs: list[Path] = field(default_factory=list)
    up_outputs: list[Path] = field(default_factory=list)
    consolidated_us: Path | None = None
    consolidated_up: Path | None = None
    spend_log: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# UTILITIES — plumbing
# ═══════════════════════════════════════════════════════════════

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    slug = value.strip().lower()
    for old, new in (("/", "-"), (" ", "-"), ("_", "-")):
        slug = slug.replace(old, new)
    return "".join(ch for ch in slug if ch.isalnum() or ch == "-")[:40] or "medium"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n")


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def extract_json_from_text(text: str) -> str | None:
    """Extract first valid JSON object from LLM response."""
    text = text.strip()
    # Direct parse
    if text.startswith("{"):
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass
    # Markdown fences
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


def get_openrouter_key() -> str:
    """Get OpenRouter API key from env or Doppler."""
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        try:
            import subprocess
            r = subprocess.run(
                ["doppler", "secrets", "get", "OPENROUTER_API_KEY", "--plain",
                 "-p", "imo-creator", "-c", "dev"],
                capture_output=True, text=True, timeout=10,
            )
            key = r.stdout.strip()
        except Exception:
            pass
    return key


def get_lbb_key() -> str:
    """Get LBB API key from env or Doppler."""
    key = os.environ.get("LBB_API_KEY", "")
    if not key:
        try:
            import subprocess
            r = subprocess.run(
                ["doppler", "secrets", "get", "LBB_API_KEY", "--plain",
                 "-p", "imo-creator", "-c", "dev"],
                capture_output=True, text=True, timeout=10,
            )
            key = r.stdout.strip()
        except Exception:
            pass
    return key


# ═══════════════════════════════════════════════════════════════
# STEP 1: INTAKE — create run directory, save metadata
# ═══════════════════════════════════════════════════════════════

def step_1_intake(ctx: RatchetContext) -> None:
    """Create run directory and save metadata."""
    print(f"\n  STEP 1: INTAKE")
    print(f"    medium: {ctx.medium[:60]}")
    print(f"    intent: {ctx.intent[:60]}")
    print(f"    run_id: {ctx.run_id}")
    print(f"    models: {', '.join(m.split('/')[-1] for m in ctx.models)}")

    ctx.run_dir.mkdir(parents=True, exist_ok=True)
    (ctx.run_dir / "receipts").mkdir(exist_ok=True)

    write_json(ctx.run_dir / "run.json", {
        "run_id": ctx.run_id,
        "medium": ctx.medium,
        "intent": ctx.intent,
        "models": ctx.models,
        "created_at": now_utc(),
        "status": "running",
    })
    (ctx.run_dir / "medium.txt").write_text(ctx.medium + "\n")
    (ctx.run_dir / "intent.txt").write_text(ctx.intent + "\n")
    print(f"    dir: {ctx.run_dir}")


# ═══════════════════════════════════════════════════════════════
# STEP 2: READ LOGBOOK — query LBB for prior runs
# ═══════════════════════════════════════════════════════════════

def step_2_read_logbook(ctx: RatchetContext) -> None:
    """Query LBB for prior knowledge on this medium."""
    print(f"\n  STEP 2: READ LOGBOOK")
    key = get_lbb_key()
    if not key:
        print(f"    no LBB key — skipping logbook read")
        return

    try:
        import urllib.request
        slug = slugify(ctx.medium)
        url = f"{LBB_URL}/query"
        payload = json.dumps({"query": slug, "limit": 5}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            records = data.get("results", [])
            if records:
                ctx.history = "\n".join(
                    f"- {r.get('title', 'untitled')}" for r in records
                )
                print(f"    found {len(records)} prior records")
            else:
                print(f"    no prior records")
    except Exception as e:
        print(f"    LBB read failed: {e}")


# ═══════════════════════════════════════════════════════════════
# STEPS 3-5 / 9-11: RUN MODEL — call OpenRouter with one model
# ═══════════════════════════════════════════════════════════════

def build_us_prompt(ctx: RatchetContext) -> str:
    """Build the US discovery prompt with doctrine content inline."""
    doctrine = []
    for path in READING_LIST:
        if path.exists():
            content = path.read_text()
            if len(content) > 3000:
                content = content[:3000] + "\n[...truncated...]"
            doctrine.append(f"--- {path.name} ---\n{content}")

    history_block = ""
    if ctx.history:
        history_block = f"\nPRIOR KNOWLEDGE:\n{ctx.history}\n"

    return f"""DOCTRINE:

{chr(10).join(doctrine)}

{history_block}
DISCOVER THIS MEDIUM:
    medium: {ctx.medium}
    intent: {ctx.intent}

OUTPUT: Return ONLY valid JSON (no markdown fences, no commentary):
{{
  "medium": "{ctx.medium}",
  "intent": "{ctx.intent}",
  "discovered_at": "<timestamp>",
  "total_layers": <int>,
  "max_depth_reached": <int>,
  "domestication_depth": <int>,
  "reverse_route": {{
    "target_value": "<P=1 state>",
    "route": ["<from leaf to root>"],
    "depth": <int>
  }},
  "layers": [
    {{
      "id": "L1",
      "name": "<name>",
      "primitive": "Thing|Flow|Change",
      "format": "<what it contains>",
      "depth": 0,
      "parent": null,
      "cv": "constant|variable",
      "domesticated": false,
      "zoom_reason": "<why>"
    }}
  ],
  "invariant_set": [
    {{
      "layer_id": "L1",
      "name": "<name>",
      "primitive": "Thing|Flow|Change",
      "why_it_matters": "<why>",
      "comparator_hint": "<what to measure>"
    }}
  ],
  "handoff_contract": {{
    "required_by_up": ["layers", "invariant_set", "reverse_route", "domestication_depth"],
    "medium_slug": "{slugify(ctx.medium)}",
    "requires_human_tolerances": true,
    "min_runs_for_handoff": 3
  }}
}}

METHOD:
1. Start at the medium root
2. At every level: Thing, Flow, or Change — exactly one
3. Name it, format it, constant or variable
4. Zoom if decomposition changes outcomes
5. Stop when domesticated
6. Reverse-check route from target to root
"""


def build_consolidation_prompt(ctx: RatchetContext, outputs: list[dict], phase: str) -> str:
    """Build the consolidation prompt from multiple model outputs."""
    runs_text = []
    for i, output in enumerate(outputs):
        model = output.get("_model", f"model_{i+1}")
        layers = output.get("layers", [])
        layer_summary = "\n".join(
            f"  {l.get('id','?')} [{l.get('primitive','?')}] "
            f"{'DOM' if l.get('domesticated') else '   '} {l.get('name','unnamed')}"
            for l in layers
        )
        route = output.get("reverse_route", {}).get("route", [])
        runs_text.append(
            f"=== {model} ({len(layers)} layers) ===\n{layer_summary}\n"
            f"Reverse route: {' → '.join(route)}\n"
        )

    return f"""CONSOLIDATE these {len(outputs)} {phase} discovery runs into ONE definitive structure.

Medium: {ctx.medium}
Intent: {ctx.intent}

{chr(10).join(runs_text)}

For each layer in your output, include:
- confidence: "locked" (all models agree), "high" (majority), "investigate" (one found)
- found_by: which models found this layer
- conflict: null or description of disagreement

Output ONLY valid JSON (no markdown):
{{
  "medium": "{ctx.medium} — Consolidated",
  "consolidation_method": "{len(outputs)}-model consensus",
  "models_used": {json.dumps([o.get('_model','unknown') for o in outputs])},
  "layers": [
    {{
      "id": "C1",
      "name": "<name>",
      "primitive": "Thing|Flow|Change",
      "confidence": "locked|high|investigate",
      "found_by": ["<models>"],
      "conflict": null,
      "cv": "constant|variable",
      "domesticated": true|false,
      "why": "<why this matters>",
      "comparator": "<what to measure>"
    }}
  ],
  "reverse_route": {{
    "consensus": "<agreed causal chain>",
    "confidence": "locked|high"
  }},
  "key_findings": ["<what all agreed>", "<what majority agreed>", "<what only one found>"]
}}"""


def call_openrouter(model: str, system_msg: str, user_msg: str,
                    max_tokens: int = 8000, temperature: float = 0.3) -> dict:
    """Single OpenRouter API call. Returns {content, tokens_in, tokens_out, cost, model}."""
    api_key = get_openrouter_key()
    if not api_key:
        raise RuntimeError("No OPENROUTER_API_KEY found")

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": user_msg}],
    }

    # System message handling
    if "anthropic" in model:
        payload["system"] = system_msg
    else:
        payload["messages"].insert(0, {
            "role": "user",
            "content": f"[SYSTEM INSTRUCTION]: {system_msg}"
        })

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://imo-creator.svg.agency",
        "X-Title": "IMO Creator Dyno",
    }

    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Extract content
    content = ""
    if "choices" in data and data["choices"]:
        content = data["choices"][0].get("message", {}).get("content", "")
    elif "content" in data:
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

    usage = data.get("usage", {})
    return {
        "content": content,
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "cost": usage.get("cost", 0),
        "model": model,
        "raw_response": data,
    }


def run_single_model(ctx: RatchetContext, model: str, prompt: str,
                     phase: str, run_num: int) -> dict | None:
    """Run one model, save output, return parsed JSON or None."""
    model_short = model.split("/")[-1]
    step_num = run_num + 2  # Steps 3-5 or 9-11
    print(f"\n  STEP {step_num}: RUN {model_short}")

    system_msg = (
        "You are the US (Universal Structure) discovery agent. "
        "Discover layers using Three Primitives (Thing, Flow, Change). "
        "Constants have structure (name + format). Variables are the fill. "
        "Output ONLY valid JSON. No markdown. No commentary."
    )

    try:
        result = call_openrouter(model, system_msg, prompt,
                                 ctx.max_tokens, ctx.temperature)
    except Exception as e:
        print(f"    ERROR: {e}")
        ctx.errors.append(f"{model_short}: {e}")
        return None

    # Log spend
    spend_entry = {
        "timestamp": now_utc(),
        "model": model,
        "phase": phase,
        "tokens_in": result["tokens_in"],
        "tokens_out": result["tokens_out"],
        "cost": result["cost"],
    }
    ctx.spend_log.append(spend_entry)
    print(f"    tokens: {result['tokens_in']} in, {result['tokens_out']} out")
    print(f"    cost: ${result['cost']:.4f}" if result['cost'] else "    cost: n/a")

    # Save raw response
    receipt_path = ctx.run_dir / "receipts" / f"{phase}-{run_num:02d}-{model_short}.json"
    write_json(receipt_path, result["raw_response"])

    # Extract JSON
    json_str = extract_json_from_text(result["content"])
    if not json_str:
        print(f"    ERROR: no valid JSON in response")
        ctx.errors.append(f"{model_short}: no valid JSON")
        # Save raw content for debugging
        (ctx.run_dir / "receipts" / f"{phase}-{run_num:02d}-{model_short}.raw.txt").write_text(result["content"])
        return None

    parsed = json.loads(json_str)
    parsed["_model"] = model_short  # Tag which model produced this

    # Save output
    output_path = ctx.run_dir / f"{run_num:02d}-{phase}-{model_short}.json"
    write_json(output_path, parsed)
    print(f"    layers: {parsed.get('total_layers', len(parsed.get('layers', [])))}")
    print(f"    saved: {output_path.name}")

    return parsed


# ═══════════════════════════════════════════════════════════════
# STEP 6 / 12: CONSOLIDATE — merge outputs with confidence
# ═══════════════════════════════════════════════════════════════

def step_consolidate(ctx: RatchetContext, outputs: list[dict], phase: str) -> dict | None:
    """Consolidate multiple model outputs into one structure with confidence scores."""
    step_label = "6" if phase == "us" else "12"
    print(f"\n  STEP {step_label}: CONSOLIDATE ({len(outputs)} outputs)")

    if len(outputs) < 2:
        print(f"    only {len(outputs)} output(s) — skipping consolidation, using as-is")
        if outputs:
            ctx.consolidated_us = ctx.run_dir / f"04-{phase}-consolidated.json"
            outputs[0]["consolidation_method"] = "single model (no consensus)"
            write_json(ctx.consolidated_us, outputs[0])
            return outputs[0]
        return None

    system_msg = (
        "You are the US Orchestrator. Consolidate multiple structure discovery runs "
        "into ONE definitive structure. If all models agree = locked. Majority = high. "
        "One model only = investigate. Pick physics over opinion when models conflict. "
        "Output ONLY valid JSON. No markdown. No commentary."
    )

    prompt = build_consolidation_prompt(ctx, outputs, phase)

    try:
        result = call_openrouter(
            CONSOLIDATION_MODEL, system_msg, prompt,
            ctx.max_tokens, ctx.temperature,
        )
    except Exception as e:
        print(f"    ERROR: {e}")
        ctx.errors.append(f"consolidation: {e}")
        return None

    ctx.spend_log.append({
        "timestamp": now_utc(),
        "model": CONSOLIDATION_MODEL,
        "phase": f"{phase}-consolidation",
        "tokens_in": result["tokens_in"],
        "tokens_out": result["tokens_out"],
        "cost": result["cost"],
    })

    json_str = extract_json_from_text(result["content"])
    if not json_str:
        print(f"    ERROR: no valid JSON in consolidation response")
        return None

    consolidated = json.loads(json_str)
    output_path = ctx.run_dir / f"04-{phase}-consolidated.json"
    write_json(output_path, consolidated)

    if phase == "us":
        ctx.consolidated_us = output_path
    else:
        ctx.consolidated_up = output_path

    # Summary
    layers = consolidated.get("layers", [])
    locked = sum(1 for l in layers if l.get("confidence") == "locked")
    high = sum(1 for l in layers if l.get("confidence") == "high")
    investigate = sum(1 for l in layers if l.get("confidence") == "investigate")
    print(f"    layers: {len(layers)} ({locked} locked, {high} high, {investigate} investigate)")
    print(f"    saved: {output_path.name}")

    return consolidated


# ═══════════════════════════════════════════════════════════════
# STEP 7 / 13: LOG — save to LBB + spend log
# ═══════════════════════════════════════════════════════════════

def step_log(ctx: RatchetContext, phase: str, consolidated: dict | None) -> None:
    """Log the run to LBB and save spend."""
    step_label = "7" if phase == "us" else "13"
    print(f"\n  STEP {step_label}: LOG")

    # Save spend log
    spend_path = ctx.run_dir / "openrouter-spend.json"
    write_json(spend_path, ctx.spend_log)
    total_cost = sum(s.get("cost", 0) for s in ctx.spend_log if isinstance(s.get("cost"), (int, float)))
    print(f"    total cost: ${total_cost:.4f}")
    print(f"    spend log: {spend_path.name}")

    # Update run.json
    run_meta = load_json(ctx.run_dir / "run.json") or {}
    run_meta["status"] = "completed" if not ctx.errors else "completed_with_errors"
    run_meta["completed_at"] = now_utc()
    run_meta["total_cost"] = total_cost
    run_meta["errors"] = ctx.errors
    run_meta[f"{phase}_consolidated"] = str(ctx.consolidated_us or ctx.consolidated_up)
    write_json(ctx.run_dir / "run.json", run_meta)

    # LBB ingest
    key = get_lbb_key()
    if not key:
        print(f"    no LBB key — skipping ingest")
        return

    layers_summary = ""
    if consolidated:
        layers = consolidated.get("layers", [])
        locked = sum(1 for l in layers if l.get("confidence") == "locked")
        high = sum(1 for l in layers if l.get("confidence") == "high")
        investigate = sum(1 for l in layers if l.get("confidence") == "investigate")
        layers_summary = f"{len(layers)} layers ({locked} locked, {high} high, {investigate} investigate)"

    title = f"Dyno {phase.upper()}: {ctx.medium[:50]} — {layers_summary}"
    content = json.dumps({
        "run_id": ctx.run_id,
        "medium": ctx.medium,
        "intent": ctx.intent,
        "phase": phase,
        "models": ctx.models,
        "total_cost": total_cost,
        "layers_summary": layers_summary,
        "errors": ctx.errors,
    })

    try:
        record_id = str(uuid.uuid4())
        payload = json.dumps({
            "record_id": record_id,
            "sovereign_ref": "imo-creator",
            "hub_id": "lbb",
            "cc_layer": "CC-03",
            "subject_id": "processes",
            "ctb_placement": "leaf",
            "title": title,
            "content": content,
            "content_format": "json",
            "source_type": "document",
            "source_name": "dyno-ratchet",
            "fetched_by": "api",
            "orbt_mode": "BUILD",
            "tags": json.dumps(["dyno", phase, "ratchet", slugify(ctx.medium)]),
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{LBB_URL}/ingest",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"    LBB ingested: {title[:60]}")
    except Exception as e:
        print(f"    LBB ingest failed: {e}")


# ═══════════════════════════════════════════════════════════════
# STEP 8 / 14: HUMAN GATE — print summary, stop for review
# ═══════════════════════════════════════════════════════════════

def step_human_gate(ctx: RatchetContext, phase: str, consolidated: dict | None) -> None:
    """Print summary for human review."""
    step_label = "8" if phase == "us" else "14"
    print(f"\n  STEP {step_label}: HUMAN GATE")
    print(f"  {'='*50}")

    if not consolidated:
        print(f"    NO CONSOLIDATED OUTPUT — check errors")
        return

    layers = consolidated.get("layers", [])
    for layer in layers:
        conf = layer.get("confidence", "?")
        conf_icon = {"locked": "■", "high": "◆", "investigate": "?"}.get(conf, " ")
        print(f"    {conf_icon} [{conf:11s}] {layer.get('name', 'unnamed')}")

    route = consolidated.get("reverse_route", {})
    if route:
        print(f"\n    REVERSE ROUTE: {route.get('consensus', 'none')}")

    findings = consolidated.get("key_findings", [])
    if findings:
        print(f"\n    KEY FINDINGS:")
        for f in findings:
            print(f"      - {f}")

    print(f"\n  {'='*50}")
    print(f"    Run dir: {ctx.run_dir}")
    print(f"    Review the consolidated output, then proceed.")


# ═══════════════════════════════════════════════════════════════
# WALL REPORT — when stuck, produce structured squawk
# ═══════════════════════════════════════════════════════════════

def wall_report(ctx: RatchetContext, reason: str) -> None:
    """Generate and save a wall report when the Dyno can't proceed."""
    print(f"\n  WALL — {reason}")

    report = {
        "type": "WALL_REPORT",
        "run_id": ctx.run_id,
        "medium": ctx.medium,
        "intent": ctx.intent,
        "reason": reason,
        "errors": ctx.errors,
        "timestamp": now_utc(),
    }

    wall_path = ctx.run_dir / "WALL.json"
    write_json(wall_path, report)
    print(f"    saved: {wall_path}")

    # Ingest to LBB
    key = get_lbb_key()
    if key:
        try:
            title = f"WALL: {ctx.medium[:50]} — {reason[:50]}"
            payload = json.dumps({
                "record_id": str(uuid.uuid4()),
                "sovereign_ref": "imo-creator",
                "hub_id": "lbb",
                "cc_layer": "CC-03",
                "subject_id": "processes",
                "ctb_placement": "leaf",
                "title": title,
                "content": json.dumps(report),
                "content_format": "json",
                "source_type": "document",
                "source_name": "dyno-ratchet",
                "fetched_by": "api",
                "orbt_mode": "BUILD",
                "tags": json.dumps(["dyno", "wall", slugify(ctx.medium)]),
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{LBB_URL}/ingest", data=payload,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=15)
            print(f"    LBB ingested wall report")
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# PHASE RUNNERS — the 14 steps assembled
# ═══════════════════════════════════════════════════════════════

def run_us_phase(ctx: RatchetContext) -> dict | None:
    """Steps 1-8: Full US discovery phase."""
    print(f"\n{'='*60}")
    print(f"  DYNO RATCHET — US PHASE")
    print(f"  {ctx.medium[:60]}")
    print(f"  {len(ctx.models)} models: {', '.join(m.split('/')[-1] for m in ctx.models)}")
    print(f"{'='*60}")

    # Step 1
    step_1_intake(ctx)

    # Step 2
    step_2_read_logbook(ctx)

    # Steps 3-5: Run each model
    prompt = build_us_prompt(ctx)
    (ctx.run_dir / "receipts" / "us-prompt.txt").write_text(prompt)

    outputs = []
    for i, model in enumerate(ctx.models):
        result = run_single_model(ctx, model, prompt, "us", i + 1)
        if result:
            outputs.append(result)

    if not outputs:
        wall_report(ctx, "All models failed — no outputs produced")
        return None

    # Step 6: Consolidate
    consolidated = step_consolidate(ctx, outputs, "us")

    # Step 7: Log
    step_log(ctx, "us", consolidated)

    # Step 8: Human gate
    step_human_gate(ctx, "us", consolidated)

    return consolidated


def run_zoom(ctx: RatchetContext, layer_name: str, parent_path: str) -> dict | None:
    """Steps Z1-Z4: Zoom into an investigate layer."""
    print(f"\n{'='*60}")
    print(f"  DYNO RATCHET — ZOOM")
    print(f"  Layer: {layer_name}")
    print(f"{'='*60}")

    # Z1: Reframe the layer as a new medium
    ctx.medium = f"{layer_name} (zoom from: {ctx.medium})"
    ctx.intent = f"Deep discovery of {layer_name}. Is this a real constant? Confirm or discard."

    # Z2-Z3: Run same 3-model + consolidate pattern
    return run_us_phase(ctx)


# ═══════════════════════════════════════════════════════════════
# CLI — command interface
# ═══════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dyno Ratchet — domain-agnostic orchestrator"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # us — run US phase
    p_us = sub.add_parser("us", help="Run US discovery phase (Steps 1-8)")
    p_us.add_argument("medium", help="The medium to decompose")
    p_us.add_argument("intent", help="What P=1 means")
    p_us.add_argument("--models", help="Comma-separated model list", default=None)
    p_us.add_argument("--output-dir", help="Run directory", default=None)
    p_us.add_argument("--max-tokens", type=int, default=8000)
    p_us.add_argument("--temperature", type=float, default=0.3)

    # zoom — zoom into an investigate layer
    p_zoom = sub.add_parser("zoom", help="Zoom into an investigate layer (Steps Z1-Z4)")
    p_zoom.add_argument("medium", help="Original medium")
    p_zoom.add_argument("intent", help="Original intent")
    p_zoom.add_argument("--layer", required=True, help="Layer name to zoom into")
    p_zoom.add_argument("--parent", required=True, help="Path to consolidated JSON")
    p_zoom.add_argument("--models", default=None)

    # status — check a run
    p_status = sub.add_parser("status", help="Check run status")
    p_status.add_argument("run_dir", help="Path to run directory")

    # chain — show run chain
    p_chain = sub.add_parser("chain", help="Show run chain")
    p_chain.add_argument("run_dir", help="Path to run directory")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.command == "us":
        models = args.models.split(",") if args.models else list(DEFAULT_MODELS)
        output_dir = Path(args.output_dir) if args.output_dir else (
            RUNS_DIR / slugify(args.medium)
        )

        ctx = RatchetContext(
            medium=args.medium,
            intent=args.intent,
            run_dir=output_dir,
            models=models,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )

        result = run_us_phase(ctx)
        return 0 if result else 1

    elif args.command == "zoom":
        models = args.models.split(",") if args.models else list(DEFAULT_MODELS)
        output_dir = RUNS_DIR / slugify(args.medium) / f"zoom-{slugify(args.layer)}"

        ctx = RatchetContext(
            medium=args.medium,
            intent=args.intent,
            run_dir=output_dir,
            models=models,
        )

        result = run_zoom(ctx, args.layer, args.parent)
        return 0 if result else 1

    elif args.command == "status":
        run_data = load_json(Path(args.run_dir) / "run.json")
        if not run_data:
            print(f"No run found at {args.run_dir}")
            return 1
        print(json.dumps(run_data, indent=2))
        return 0

    elif args.command == "chain":
        run_dir = Path(args.run_dir)
        for f in sorted(run_dir.glob("*.json")):
            if f.name.startswith("0"):
                data = load_json(f)
                layers = len(data.get("layers", [])) if data else 0
                print(f"  {f.name:40s}  {layers} layers")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

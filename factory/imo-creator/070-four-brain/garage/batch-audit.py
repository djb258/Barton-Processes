#!/usr/bin/env python3
"""
batch-audit.py — Run gate-runner.py against the canonical 16 production processes
defined in EXECUTION_ORDER.md.

Atlas authority: same as gate-runner.py. No LLM on spine.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # Barton-Processes root
RUNNER = Path(__file__).parent / "gate-runner.py"
FACTORY = ROOT / "factory"

# The canonical 16 production processes per EXECUTION_ORDER.md
CANONICAL_16 = [
    ("010-seed-d1",            "factory/outreach/010-seed-d1"),
    ("200-people-worker",      "factory/outreach/200-people-worker"),
    ("201-email-discovery",    "factory/outreach/201-email-discovery"),
    ("202-linkedin-discovery", "factory/outreach/202-linkedin-discovery"),
    ("300-blog-worker",        "factory/outreach/300-blog-worker"),
    ("301-page-parser",        "factory/outreach/301-page-parser"),
    ("400-dol-views",          "factory/outreach/400-dol-views"),
    ("500-talent-flow",        "factory/outreach/500-talent-flow"),
    ("600-bit-scoring",        "factory/outreach/600-bit-scoring"),
    ("700-campaign-engine",    "factory/outreach/700-campaign-engine"),
    ("100-lcs-pipeline",       "factory/cl/100-lcs-pipeline"),
    ("800-client-mint",        "factory/cl/800-client-mint"),
    ("810-client-intake",      "factory/client/810-client-intake"),
    ("820-vendor-export",      "factory/client/820-vendor-export"),
    ("830-client-portal",      "factory/client/830-client-portal"),
    ("900-sales-portal",       "factory/sales/900-sales-portal"),
]

DETERMINISTIC_GATES = [
    "G01", "G02", "G03", "G04", "G05", "G07", "G10", "G11", "G12",
    "Rung-1", "Rung-2", "Rung-3", "Rung-7", "Rung-8",
]


def find_companion_yaml(md_path: Path) -> Path | None:
    parent = md_path.parent
    candidates = [c for c in parent.glob("*.yaml") if c.is_file()]
    if not candidates:
        return None
    dir_token = re.sub(r"^\d+-", "", parent.name).lower()
    for c in candidates:
        if dir_token in c.stem.lower() or c.stem.lower() in dir_token:
            return c
    return candidates[0]


def audit(slug: str, proc_dir: Path) -> dict:
    md = proc_dir / "PROCESS-UT.md"
    if not md.exists():
        return {"process": slug, "exists": False, "verdict": "FAIL", "p_value": 0,
                "gates_failed": [{"id": "PRE", "evidence": f"No PROCESS-UT.md at {proc_dir}"}],
                "gates_passed": []}
    yaml_c = find_companion_yaml(md)
    if not yaml_c:
        return {"process": slug, "exists": True, "yaml_companion": None,
                "verdict": "FAIL", "p_value": 0,
                "gates_failed": [{"id": "BS-LAW", "evidence": "No yaml companion — Y-junction violation"}],
                "gates_passed": []}
    bar_id = f"BATCH-{slug.upper()}"
    cmd = [
        sys.executable, str(RUNNER),
        "--bar-id", bar_id,
        "--audited-yaml", str(yaml_c),
        "--audited-md", str(md),
        "--only", *DETERMINISTIC_GATES,
        "--deterministic-only",
        "--output-format", "json",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8")
        out = result.stdout.strip()
        if not out:
            return {"process": slug, "yaml_companion": yaml_c.relative_to(ROOT).as_posix(),
                    "verdict": "ERROR", "p_value": 0,
                    "gates_failed": [{"id": "RUNNER", "evidence": result.stderr[:200]}]}
        report = json.loads(out)
        report["process"] = slug
        report["yaml_companion"] = yaml_c.relative_to(ROOT).as_posix()
        report["proc_dir"] = proc_dir.relative_to(ROOT).as_posix()
        return report
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        return {"process": slug, "verdict": "ERROR", "p_value": 0,
                "gates_failed": [{"id": "EXEC", "evidence": str(e)[:200]}]}


def main():
    print(f"Auditing {len(CANONICAL_16)} canonical production processes")
    print("=" * 80)
    results = []
    pass_count = 0
    for slug, rel in CANONICAL_16:
        proc_dir = ROOT / rel
        rpt = audit(slug, proc_dir)
        results.append(rpt)
        if rpt["verdict"] == "PASS":
            pass_count += 1
        n_fail = len(rpt.get("gates_failed", []))
        marker = "PASS" if rpt["verdict"] == "PASS" else ("ERR " if rpt["verdict"] == "ERROR" else "FAIL")
        print(f"  [{marker}] P={rpt['p_value']}  {slug:<28} failures={n_fail}")
    print("=" * 80)
    print(f"SUMMARY: {pass_count}/{len(results)} processes PASS")
    print("=" * 80)
    failure_counts = {}
    for r in results:
        for f in r.get("gates_failed", []):
            failure_counts[f["id"]] = failure_counts.get(f["id"], 0) + 1
    print("\nMost-common gate failures:")
    for gate_id, cnt in sorted(failure_counts.items(), key=lambda x: -x[1])[:12]:
        print(f"  {gate_id}: {cnt} processes")
    print()
    print("Per-process failure detail:")
    for r in results:
        if r["verdict"] != "PASS":
            print(f"\n  {r['process']}:")
            for f in r.get("gates_failed", []):
                ev = (f.get("evidence") or "")[:130]
                print(f"    - {f['id']}: {ev}")
    summary_path = Path(__file__).parent / "batch-audit-summary.json"
    summary_path.write_text(json.dumps({
        "total": len(results), "passed": pass_count,
        "failure_counts_by_gate": failure_counts, "results": results,
    }, indent=2), encoding="utf-8")
    print(f"\nFull JSON: {summary_path}")


if __name__ == "__main__":
    main()

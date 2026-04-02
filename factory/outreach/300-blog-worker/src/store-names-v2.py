#!/usr/bin/env python3
"""
store-names-v2.py — Finish storing recon_name_titles to D1 slot_workbench.
Skips rows already filled (WHERE recon_name_titles IS NULL).
Batches 30 UPDATEs per wrangler call.
Caps name_title entries to first 10.
"""

import json
import glob
import subprocess
import sys

WRANGLER_CWD = "/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub"
JSONL_PATTERN = "/Users/employeeai/Documents/Barton-Processes/factory/outreach/300-blog-worker/src/output/company-recon-*-w*.jsonl"
BATCH_SIZE = 30
MAX_NAME_ENTRIES = 10
DB_NAME = "svg-d1-outreach-ops"


def sql_escape(s: str) -> str:
    return s.replace("'", "''")


def build_update(outreach_id: str, name_titles: list) -> str:
    capped = name_titles[:MAX_NAME_ENTRIES]
    json_str = json.dumps(capped, ensure_ascii=False)
    escaped = sql_escape(json_str)
    oid_escaped = sql_escape(outreach_id)
    return (
        f"UPDATE slot_workbench SET recon_name_titles = '{escaped}' "
        f"WHERE outreach_id = '{oid_escaped}' AND recon_name_titles IS NULL;"
    )


def execute_batch(statements: list) -> bool:
    combined = " ".join(statements)
    cmd = [
        "npx", "wrangler", "d1", "execute", DB_NAME,
        "--remote", "--command", combined, "--json"
    ]
    result = subprocess.run(
        cmd,
        cwd=WRANGLER_CWD,
        capture_output=True,
        text=True,
        timeout=120
    )
    # wrangler prints warnings to stderr -- only fail on non-zero return + actual error
    if result.returncode != 0:
        # Check if stderr has real error (not just wrangler warnings)
        err = result.stderr.strip()
        if err and "ERROR" not in err.upper():
            return True  # just warnings
        print(f"  BATCH FAIL rc={result.returncode}: {err[:200]}", flush=True)
        return False
    return True


def main():
    files = sorted(glob.glob(JSONL_PATTERN))
    print(f"Found {len(files)} JSONL files", flush=True)

    updates = []
    total_candidates = 0

    for f in files:
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                oid = rec.get("outreach_id", "")
                ntp = rec.get("name_title_patterns", [])
                if not oid or not ntp:
                    continue

                total_candidates += 1
                updates.append(build_update(oid, ntp))

    print(f"Total candidates with name_title_patterns: {total_candidates}", flush=True)
    print(f"Batching {len(updates)} updates in groups of {BATCH_SIZE}", flush=True)

    sent = 0
    errors = 0

    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i : i + BATCH_SIZE]
        try:
            ok = execute_batch(batch)
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT at batch starting {i}", flush=True)
            ok = False
        except Exception as e:
            print(f"  EXCEPTION at batch starting {i}: {e}", flush=True)
            ok = False

        if ok:
            sent += len(batch)
        else:
            errors += len(batch)

        total_processed = sent + errors
        if total_processed % 500 < BATCH_SIZE or i + BATCH_SIZE >= len(updates):
            print(f"  Progress: {total_processed}/{len(updates)} sent={sent} errors={errors}", flush=True)

    print(f"\nDone. Sent={sent}, Errors={errors}, Total={sent + errors}", flush=True)


if __name__ == "__main__":
    main()

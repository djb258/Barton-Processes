#!/usr/bin/env python3 -u
"""
Store name_title_patterns from Process 300 recon JSONL files
into slot_workbench.recon_name_titles on D1.
"""

import glob
import json
import os
import subprocess
import sys
import tempfile

JSONL_PATTERN = "/Users/employeeai/Documents/Barton-Processes/factory/outreach/300-blog-worker/src/output/company-recon-*-w*.jsonl"
WRANGLER_CWD = "/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub"
BATCH_SIZE = 30


def sql_escape(s: str) -> str:
    """Escape single quotes for SQL."""
    return s.replace("'", "''")


def run_d1(sql: str) -> bool:
    """Execute SQL against D1 via wrangler using --file for large payloads."""
    fd, path = tempfile.mkstemp(suffix=".sql")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(sql)
        cmd = [
            "npx", "wrangler", "d1", "execute", "svg-d1-outreach-ops",
            "--remote", "--file", path, "--json"
        ]
        result = subprocess.run(
            cmd, cwd=WRANGLER_CWD, capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr[:300]}", file=sys.stderr, flush=True)
            return False
        return True
    except subprocess.TimeoutExpired:
        print("  ERROR: D1 call timed out", file=sys.stderr, flush=True)
        return False
    finally:
        os.unlink(path)


def main():
    files = sorted(glob.glob(JSONL_PATTERN))
    print(f"Found {len(files)} JSONL files", flush=True)

    updates = []  # list of (outreach_id, json_str)
    skipped = 0
    total_records = 0

    for f in files:
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                total_records += 1
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    skipped += 1
                    continue

                patterns = rec.get("name_title_patterns")
                oid = rec.get("outreach_id")
                if not oid or not patterns or len(patterns) == 0:
                    skipped += 1
                    continue

                json_str = json.dumps(patterns, ensure_ascii=False)
                updates.append((oid, json_str))

    print(f"Total records scanned: {total_records}", flush=True)
    print(f"Records with name_title_patterns: {len(updates)}", flush=True)
    print(f"Skipped (empty/missing): {skipped}", flush=True)

    # Execute in batches
    success_count = 0
    fail_count = 0

    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i + BATCH_SIZE]
        stmts = []
        for oid, json_str in batch:
            escaped = sql_escape(json_str)
            stmts.append(
                f"UPDATE slot_workbench SET recon_name_titles = '{escaped}' "
                f"WHERE outreach_id = '{oid}'"
            )
        sql = ";\n".join(stmts) + ";"

        ok = run_d1(sql)
        if ok:
            success_count += len(batch)
        else:
            fail_count += len(batch)

        processed = i + len(batch)
        if processed % 500 < BATCH_SIZE or processed == len(updates):
            print(f"  Progress: {processed}/{len(updates)} "
                  f"(success={success_count}, fail={fail_count})", flush=True)

    print(f"\nDone. {success_count} updates succeeded, {fail_count} failed.",
          flush=True)


if __name__ == "__main__":
    main()

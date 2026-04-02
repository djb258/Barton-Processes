#!/usr/bin/env python3
"""
store-results.py — Push recon result_urls, snippets, result_count from JSONL to D1 slot_workbench.

Reads company-recon-*-w*.jsonl files, updates slot_workbench via wrangler d1 execute --file.
Batches 20 UPDATEs per D1 call. SQL-escapes single quotes.
Uses temp SQL files to avoid shell escaping issues with URLs and CSS in snippets.
"""

import json
import glob
import subprocess
import sys
import os
import tempfile

WRANGLER_CWD = "/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub"
JSONL_PATTERN = "/Users/employeeai/Documents/Barton-Processes/factory/outreach/300-blog-worker/src/output/company-recon-*-w*.jsonl"
BATCH_SIZE = 20


def sql_escape(s: str) -> str:
    """Escape single quotes for SQL."""
    if s is None:
        return ""
    return s.replace("'", "''")


def build_update(oid: str, result_urls: list, snippets: list, result_count) -> str:
    """Build one UPDATE statement."""
    urls_json = sql_escape(json.dumps(result_urls[:10]))
    snips_json = sql_escape(json.dumps(snippets[:10]))
    rc = int(result_count) if result_count is not None else 0
    oid_esc = sql_escape(oid)
    return (
        f"UPDATE slot_workbench SET "
        f"recon_result_urls = '{urls_json}', "
        f"recon_snippets = '{snips_json}', "
        f"recon_result_count = {rc} "
        f"WHERE outreach_id = '{oid_esc}';\n"
    )


def execute_batch(statements: list) -> bool:
    """Execute a batch of SQL statements via wrangler using a temp SQL file."""
    sql = "".join(statements)

    # Write to temp file to avoid shell escaping issues
    fd, tmppath = tempfile.mkstemp(suffix=".sql", prefix="d1_batch_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(sql)

        cmd = [
            "npx", "wrangler", "d1", "execute", "svg-d1-outreach-ops",
            "--remote", "--file", tmppath, "--json"
        ]
        result = subprocess.run(
            cmd, cwd=WRANGLER_CWD, capture_output=True, text=True, timeout=90
        )
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr[:300]}", file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print("  TIMEOUT on batch", file=sys.stderr)
        return False
    finally:
        os.unlink(tmppath)


def main():
    files = sorted(glob.glob(JSONL_PATTERN))
    print(f"Found {len(files)} JSONL files")

    total = 0
    updated = 0
    errors = 0
    batch = []

    for fpath in files:
        with open(fpath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    errors += 1
                    continue

                oid = rec.get("outreach_id")
                if not oid:
                    errors += 1
                    continue

                result_urls = rec.get("result_urls") or []
                snippets = rec.get("snippets") or []
                result_count = rec.get("result_count", 0)

                stmt = build_update(oid, result_urls, snippets, result_count)
                batch.append(stmt)
                total += 1

                if len(batch) >= BATCH_SIZE:
                    if execute_batch(batch):
                        updated += len(batch)
                    else:
                        errors += len(batch)
                    batch = []

                    if total % 500 == 0:
                        print(f"  progress: {total} processed, {updated} updated, {errors} errors")

    # flush remaining
    if batch:
        if execute_batch(batch):
            updated += len(batch)
        else:
            errors += len(batch)

    print(f"\nDone. Total records: {total}, Updated: {updated}, Errors: {errors}")


if __name__ == "__main__":
    main()

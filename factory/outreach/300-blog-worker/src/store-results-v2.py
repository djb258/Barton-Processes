#!/usr/bin/env python3
"""
store-results-v2.py — Store recon result_count and top 5 result_urls to D1 slot_workbench.
Only updates rows where recon_result_urls IS NULL (skips already-done).
Batches 40 UPDATEs per wrangler call.
Skips snippets entirely — too large, caused timeouts in v1.
"""

import json
import glob
import subprocess
import sys
import time

JSONL_PATTERN = "/Users/employeeai/Documents/Barton-Processes/factory/outreach/300-blog-worker/src/output/company-recon-*-w*.jsonl"
WRANGLER_CWD = "/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub"
DB_NAME = "svg-d1-outreach-ops"
BATCH_SIZE = 40


def sql_escape(s):
    """Escape single quotes for SQL."""
    if s is None:
        return ""
    return str(s).replace("'", "''")


def load_records():
    """Load all captured records with result_urls from JSONL files, deduped by outreach_id."""
    records = {}
    files = sorted(glob.glob(JSONL_PATTERN))
    for f in files:
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("status") != "captured":
                    continue
                oid = r.get("outreach_id")
                if not oid:
                    continue
                urls = r.get("result_urls", [])
                count = r.get("result_count", 0)
                if not urls and not count:
                    continue
                # Keep last occurrence (dedup)
                records[oid] = {
                    "outreach_id": oid,
                    "result_count": count if count else len(urls),
                    "top_urls": urls[:5] if urls else [],
                }
    return records


def build_update_sql(batch):
    """Build a single SQL string with multiple UPDATE statements."""
    stmts = []
    for rec in batch:
        oid = sql_escape(rec["outreach_id"])
        count = int(rec["result_count"]) if rec["result_count"] else 0
        urls_json = sql_escape(json.dumps(rec["top_urls"]))
        stmt = (
            f"UPDATE slot_workbench SET "
            f"recon_result_count = {count}, "
            f"recon_result_urls = '{urls_json}' "
            f"WHERE outreach_id = '{oid}' "
            f"AND recon_result_urls IS NULL;"
        )
        stmts.append(stmt)
    return " ".join(stmts)


def execute_sql(sql):
    """Execute SQL via wrangler d1."""
    cmd = [
        "npx", "wrangler", "d1", "execute", DB_NAME,
        "--remote", "--command", sql, "--json"
    ]
    result = subprocess.run(
        cmd,
        cwd=WRANGLER_CWD,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return False, result.stderr[:500]
    return True, result.stdout[:200]


def log(msg):
    print(msg, flush=True)


def main():
    log("Loading JSONL records...")
    records = load_records()
    log(f"Loaded {len(records)} unique captured records with results")

    items = list(records.values())
    total = len(items)
    updated = 0
    errors = 0
    batch_num = 0

    for i in range(0, total, BATCH_SIZE):
        batch = items[i : i + BATCH_SIZE]
        batch_num += 1
        sql = build_update_sql(batch)

        ok, msg = execute_sql(sql)
        if ok:
            updated += len(batch)
        else:
            errors += len(batch)
            log(f"  ERROR batch {batch_num}: {msg[:200]}")
            # Retry individually on failure
            for rec in batch:
                single_sql = build_update_sql([rec])
                ok2, msg2 = execute_sql(single_sql)
                if ok2:
                    updated += 1
                    errors -= 1
                else:
                    log(f"    SKIP {rec['outreach_id']}: {msg2[:100]}")

        if updated % 1000 < BATCH_SIZE or i + BATCH_SIZE >= total:
            log(f"  Progress: {updated} updated, {errors} errors, {i + len(batch)}/{total} processed")

    log(f"\nDONE. Updated: {updated}, Errors: {errors}, Total processed: {total}")


if __name__ == "__main__":
    main()

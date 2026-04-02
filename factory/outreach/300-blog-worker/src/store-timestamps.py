#!/usr/bin/env python3
"""
store-timestamps.py
Updates slot_workbench.last_recon_at for all companies searched by Process 300.
Reads JSONL output files -> batches 50 UPDATEs per D1 call via wrangler.
"""

import json
import glob
import subprocess
import sys

JSONL_PATTERN = "/Users/employeeai/Documents/Barton-Processes/factory/outreach/300-blog-worker/src/output/company-recon-*-w*.jsonl"
WRANGLER_CWD = "/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub"
DB_NAME = "svg-d1-outreach-ops"
BATCH_SIZE = 50

def build_update(oid, captured_at):
    """Build a single UPDATE statement."""
    # Escape single quotes in values
    oid = oid.replace("'", "''")
    captured_at = captured_at.replace("'", "''")
    return (
        f"UPDATE slot_workbench SET last_recon_at = '{captured_at}' "
        f"WHERE outreach_id = '{oid}' "
        f"AND (last_recon_at IS NULL OR last_recon_at < '{captured_at}')"
    )

def execute_batch(statements):
    """Execute a batch of SQL statements via wrangler."""
    # Join all statements with semicolons
    sql = "; ".join(statements)
    cmd = [
        "npx", "wrangler", "d1", "execute", DB_NAME,
        "--remote", "--command", sql, "--json"
    ]
    result = subprocess.run(
        cmd, cwd=WRANGLER_CWD,
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:500]}", file=sys.stderr)
        return 0

    # Parse response to count rows changed
    try:
        data = json.loads(result.stdout)
        total_changes = 0
        for item in data:
            if isinstance(item, dict):
                meta = item.get("meta", {})
                total_changes += meta.get("changes", 0)
            elif isinstance(item, list):
                for sub in item:
                    if isinstance(sub, dict):
                        meta = sub.get("meta", {})
                        total_changes += meta.get("changes", 0)
        return total_changes
    except (json.JSONDecodeError, KeyError, TypeError):
        return 0

def main():
    files = sorted(glob.glob(JSONL_PATTERN))
    if not files:
        print("No JSONL files found!")
        sys.exit(1)

    print(f"Found {len(files)} JSONL files")

    # Collect all (outreach_id, captured_at) pairs
    records = []
    for f in files:
        with open(f, "r") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    oid = rec.get("outreach_id")
                    cap = rec.get("captured_at")
                    if oid and cap:
                        records.append((oid, cap))
                except json.JSONDecodeError:
                    continue

    print(f"Loaded {len(records)} records with outreach_id + captured_at")

    # Process in batches
    total_updated = 0
    total_processed = 0
    batch = []

    for oid, cap in records:
        batch.append(build_update(oid, cap))

        if len(batch) >= BATCH_SIZE:
            changes = execute_batch(batch)
            total_updated += changes
            total_processed += len(batch)
            batch = []

            if total_processed % 1000 == 0:
                print(f"  Progress: {total_processed}/{len(records)} processed, {total_updated} rows updated")

    # Final batch
    if batch:
        changes = execute_batch(batch)
        total_updated += changes
        total_processed += len(batch)

    print(f"\nDone. {total_processed} records processed, {total_updated} slot rows updated with last_recon_at.")

if __name__ == "__main__":
    main()

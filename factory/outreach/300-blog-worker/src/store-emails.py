#!/usr/bin/env python3
"""
store-emails.py — Extract emails from Process 300 recon JSONL files
and store them on D1 slot_workbench.recon_emails as JSON TEXT.

Batch: 30 UPDATEs per D1 call (semicolon-separated).
Progress: every 500 records.
"""

import json
import glob
import subprocess
import sys

WRANGLER_CWD = "/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub"
BATCH_SIZE = 30
PROGRESS_EVERY = 500

def sql_escape(s: str) -> str:
    """Escape single quotes for SQL."""
    return s.replace("'", "''")

def run_d1(sql: str) -> bool:
    """Execute SQL against D1 via wrangler."""
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", "svg-d1-outreach-ops", "--remote", "--command", sql, "--json"],
        cwd=WRANGLER_CWD,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:300]}", file=sys.stderr)
        return False
    return True

def main():
    pattern = "/Users/employeeai/Documents/Barton-Processes/factory/outreach/300-blog-worker/src/output/company-recon-*-w*.jsonl"
    files = sorted(glob.glob(pattern))
    print(f"Found {len(files)} JSONL files")

    updates = []       # list of SQL UPDATE statements
    total_queued = 0
    total_sent = 0
    total_success = 0
    total_records = 0

    for fpath in files:
        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                total_records += 1

                emails = rec.get("emails", [])
                if not emails:
                    continue

                oid = rec["outreach_id"]
                email_json = json.dumps(emails)
                safe_json = sql_escape(email_json)
                safe_oid = sql_escape(oid)

                stmt = f"UPDATE slot_workbench SET recon_emails = '{safe_json}' WHERE outreach_id = '{safe_oid}'"
                updates.append(stmt)
                total_queued += 1

                # Flush batch
                if len(updates) >= BATCH_SIZE:
                    sql = "; ".join(updates)
                    ok = run_d1(sql)
                    total_sent += len(updates)
                    if ok:
                        total_success += len(updates)
                    updates = []

                    if total_sent % PROGRESS_EVERY < BATCH_SIZE:
                        print(f"  Progress: {total_sent}/{total_queued} sent, {total_success} ok  (scanned {total_records} records)")

    # Flush remaining
    if updates:
        sql = "; ".join(updates)
        ok = run_d1(sql)
        total_sent += len(updates)
        if ok:
            total_success += len(updates)
        updates = []

    print(f"\nDone.")
    print(f"  Total records scanned: {total_records}")
    print(f"  Records with emails:   {total_queued}")
    print(f"  Updates sent:          {total_sent}")
    print(f"  Updates successful:    {total_success}")

if __name__ == "__main__":
    main()

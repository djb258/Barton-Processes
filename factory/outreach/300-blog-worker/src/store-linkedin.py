#!/usr/bin/env python3
"""
store-linkedin.py
Reads company-recon JSONL output and writes linkedin_people / linkedin_company
arrays into slot_workbench (D1) for ALL slots matching each outreach_id.
"""

import glob
import json
import subprocess
import sys

JSONL_PATTERN = "/Users/employeeai/Documents/Barton-Processes/factory/outreach/300-blog-worker/src/output/company-recon-*-w*.jsonl"
WRANGLER_CWD = "/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub"
DB_NAME = "svg-d1-outreach-ops"
BATCH_SIZE = 50


def escape_sql(s: str) -> str:
    """Escape single quotes for SQL."""
    return s.replace("'", "''")


def run_wrangler_batch(sql_statements: list[str]) -> bool:
    """Execute multiple SQL statements via wrangler d1 execute --file using a temp file."""
    import tempfile
    import os

    # Write statements to a temp .sql file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, dir='/tmp') as f:
        for stmt in sql_statements:
            f.write(stmt + ";\n")
        tmppath = f.name

    try:
        cmd = [
            "npx", "wrangler", "d1", "execute", DB_NAME,
            "--remote", "--file", tmppath, "--json"
        ]
        result = subprocess.run(
            cmd, cwd=WRANGLER_CWD, capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            # Check stdout too - wrangler sometimes puts errors there
            err = result.stderr.strip() or result.stdout.strip()
            print(f"  BATCH ERROR (rc={result.returncode}): {err[:300]}", file=sys.stderr)
            return False
        # Parse output to check success
        try:
            data = json.loads(result.stdout)
            # data is an array of results, check all succeeded
            if isinstance(data, list):
                for item in data:
                    if not item.get("success", False):
                        print(f"  BATCH ITEM FAILED: {item}", file=sys.stderr)
                        return False
            return True
        except json.JSONDecodeError:
            # If we can't parse, check return code was 0
            return True
    except subprocess.TimeoutExpired:
        print("  ERROR: wrangler timed out", file=sys.stderr)
        return False
    finally:
        os.unlink(tmppath)


def main():
    files = sorted(glob.glob(JSONL_PATTERN))
    print(f"Found {len(files)} JSONL files")

    # Collect all updates: outreach_id -> (people_json, company_json)
    updates: dict[str, tuple[str, str]] = {}

    for fpath in files:
        with open(fpath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                oid = rec.get("outreach_id")
                if not oid:
                    continue

                people = rec.get("linkedin_people", [])
                company = rec.get("linkedin_company", [])

                # Only store if at least one has data
                if people or company:
                    updates[oid] = (
                        json.dumps(people, ensure_ascii=False),
                        json.dumps(company, ensure_ascii=False),
                    )

    print(f"Records with LinkedIn data: {len(updates)}")

    # Batch updates using --file
    oids = list(updates.keys())
    success = 0
    fail = 0

    for i in range(0, len(oids), BATCH_SIZE):
        batch = oids[i : i + BATCH_SIZE]
        stmts = []
        for oid in batch:
            people_json, company_json = updates[oid]
            stmt = (
                f"UPDATE slot_workbench "
                f"SET recon_linkedin_people = '{escape_sql(people_json)}', "
                f"recon_linkedin_company = '{escape_sql(company_json)}' "
                f"WHERE outreach_id = '{escape_sql(oid)}'"
            )
            stmts.append(stmt)

        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(oids) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} updates)...", end=" ", flush=True)

        if run_wrangler_batch(stmts):
            success += len(batch)
            print("OK")
        else:
            fail += len(batch)
            print("FAILED")

    print(f"\nDone. Updated: {success}, Failed: {fail}")


if __name__ == "__main__":
    main()

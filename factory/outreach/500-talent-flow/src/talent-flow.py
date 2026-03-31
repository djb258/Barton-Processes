"""
Process 500 — Talent Flow

Sensor-only. Reads Process 200's LinkedIn snapshots month-over-month.
Detects executive-level slot changes: EXECUTIVE_JOINED, EXECUTIVE_LEFT.
No external tools. No API calls. No proxy. Pure database diff.

Depends on: Process 200 (must complete monthly run first)
Feeds: Process 100 (LCS Pipeline)

Usage:
  python3 src/talent-flow.py                    # Run for current month
  python3 src/talent-flow.py --month 2026-03    # Specific month
  python3 src/talent-flow.py --dry-run          # Preview without writing

Output: Signals written to outreach.signal_output in Neon
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

DB_URL = os.environ.get("DATABASE_URL",
    "postgresql://Marketing%20DB_owner:npg_OsE4Z2oPCpiT@ep-ancient-waterfall-a42vy0du-pooler.us-east-1.aws.neon.tech/Marketing%20DB?sslmode=require")

# ── Signal Constants ─────────────────────────────────────────

SIGNALS = {
    "EXECUTIVE_JOINED": {
        "code": "TF-01",
        "description": "Executive joined — new person in slot",
        "magnitude": 10,
        "expiry_days": 90,
    },
    "EXECUTIVE_LEFT": {
        "code": "TF-02",
        "description": "Executive left — slot vacated or person changed company",
        "magnitude": 8,
        "expiry_days": 90,
    },
}

# ── Parse args ───────────────────────────────────────────────

run_month = datetime.now().strftime("%Y-%m")
dry_run = False

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--month" and i + 1 < len(args):
        run_month = args[i + 1]
        i += 2
    elif args[i] == "--dry-run":
        dry_run = True
        i += 1
    else:
        i += 1


# ── Query helpers ────────────────────────────────────────────

def query_neon(sql: str) -> list:
    """Run a SQL query against Neon and return JSON results."""
    result = subprocess.run(
        ["psql", DB_URL, "-t", "-A", "-c", f"SELECT json_agg(row_to_json(t)) FROM ({sql}) t"],
        capture_output=True, text=True
    )
    if result.stdout.strip() and result.stdout.strip() != '':
        return json.loads(result.stdout.strip()) or []
    return []


def execute_neon(sql: str) -> str:
    """Execute a SQL statement against Neon."""
    result = subprocess.run(
        ["psql", DB_URL, "-c", sql],
        capture_output=True, text=True
    )
    return result.stdout


# ── Main ─────────────────────────────────────────────────────

def main():
    run_date = f"{run_month}-01"

    print(f"Process 500 — Talent Flow")
    print(f"Run month: {run_month}")
    print(f"Dry run: {dry_run}")
    print()

    # Check: does Process 200 have snapshots for this month?
    check = query_neon(f"""
        SELECT COUNT(*) as cnt
        FROM people.linkedin_snapshots
        WHERE run_month = '{run_date}'
    """)

    snapshot_count = check[0]["cnt"] if check else 0
    print(f"Process 200 snapshots for {run_month}: {snapshot_count}")

    if snapshot_count == 0:
        print("ERROR: Process 200 has not completed for this month. Cannot run Talent Flow.")
        print("Gate check: FAIL — dependency not met.")
        sys.exit(1)

    # Detect movement: compare current month snapshots to stored people data
    # A person's title or company changed = executive movement
    movements = query_neon(f"""
        SELECT
            ls.person_id,
            ls.company_unique_id,
            ls.parsed_name,
            ls.parsed_title as linkedin_title,
            ls.parsed_company as linkedin_company,
            pm.title as stored_title,
            ls.movement_detected,
            ls.movement_type,
            cs.slot_type,
            tc.agent_name
        FROM people.linkedin_snapshots ls
        JOIN people.people_master pm ON pm.unique_id = ls.person_id
        JOIN people.company_slot cs ON cs.person_unique_id = ls.person_id AND cs.is_filled = true
        JOIN people.v_territory_companies tc ON tc.company_unique_id = ls.company_unique_id
        WHERE ls.run_month = '{run_date}'
        AND ls.movement_detected = true
        AND cs.slot_type IN ('CEO', 'CFO', 'HR')
    """)

    print(f"Executive movements detected: {len(movements)}")
    print()

    if not movements:
        print("No executive movements this month. Clean exit.")
        return

    # Classify signals
    joined = 0
    left = 0

    for m in movements:
        mt = m["movement_type"]
        signal = None

        if mt == "COMPANY_CHANGED":
            # Person moved to a different company → they LEFT this company
            signal = SIGNALS["EXECUTIVE_LEFT"]
            left += 1
        elif mt == "TITLE_CHANGED":
            # Title changed at same company → could be promotion or role change
            # Not necessarily joined/left — but worth flagging
            signal = SIGNALS["EXECUTIVE_JOINED"]
            joined += 1
        elif mt == "BOTH_CHANGED":
            # Both changed → they LEFT
            signal = SIGNALS["EXECUTIVE_LEFT"]
            left += 1

        if signal and not dry_run:
            # Write signal to outreach.signal_output
            execute_neon(f"""
                INSERT INTO outreach.signal_output (
                    outreach_id, signal_code, signal_name, signal_source,
                    signal_value, magnitude, expires_at, run_month
                )
                SELECT
                    cs.outreach_id,
                    '{signal["code"]}',
                    '{signal["description"][:50]}',
                    'talent_flow',
                    '{m["movement_type"]}',
                    {signal["magnitude"]},
                    '{run_date}'::date + interval '{signal["expiry_days"]} days',
                    '{run_date}'
                FROM people.company_slot cs
                WHERE cs.person_unique_id = '{m["person_id"]}'
                AND cs.is_filled = true
                ON CONFLICT (outreach_id, signal_code, run_month) DO NOTHING
            """)

        action = "WRITE" if not dry_run else "DRY-RUN"
        print(f"  [{action}] {m['parsed_name'][:25]:25s} | {m['slot_type']} | {m['movement_type']:18s} | {signal['code'] if signal else 'SKIP'} | {m['agent_name']}")

    print(f"\nSummary:")
    print(f"  EXECUTIVE_JOINED (TF-01): {joined}")
    print(f"  EXECUTIVE_LEFT (TF-02):   {left}")
    print(f"  Total signals:            {joined + left}")
    if dry_run:
        print(f"  (Dry run — no signals written)")


if __name__ == "__main__":
    main()

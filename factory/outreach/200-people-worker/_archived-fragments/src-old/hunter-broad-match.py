"""
Process 200 — Hunter Broad Match

Cross-references enrichment_hunter_contact (175K contacts we already paid for)
against empty slots by outreach_id + seniority/department → slot_type mapping.

The narrow Gate B only checks hunter_first_name on the slot itself.
This layer queries the FULL Hunter contact table by company.

Mapping:
  CEO slot → C-Level/Owner in (Executive, Management, Operations, Sales, NULL)
  CFO slot → C-Level/Owner in (Finance) OR Manager in (Finance)
  HR slot  → C-Level/Owner in (HR) OR Manager in (HR)

Zero cost. Data already in D1.

Usage:
  python3 hunter-broad-match.py --limit 100
  python3 hunter-broad-match.py --dry-run
  python3 hunter-broad-match.py
"""

import json
import sys
import os
import subprocess
from datetime import datetime, timezone

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

LIMIT = 0
DRY_RUN = False
PAGE_SIZE = 500
WRITE_BATCH = 50

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
    elif args[i] == "--dry-run":
        DRY_RUN = True; i += 1
    else:
        i += 1

# Slot type → Hunter seniority/department mapping
SLOT_MATCH = {
    "CEO": {
        "seniority": ["C-Level/Owner"],
        "departments": ["Executive", "Management", "Operations & logistics", "Sales", None],
    },
    "CFO": {
        "seniority": ["C-Level/Owner", "Manager", "Director"],
        "departments": ["Finance"],
    },
    "HR": {
        "seniority": ["C-Level/Owner", "Manager", "Director"],
        "departments": ["HR"],
    },
}


def d1_query(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    if result.returncode != 0: return []
    try:
        start = result.stdout.find('[')
        if start < 0: return []
        data = json.loads(result.stdout[start:])
        return data[0].get("results", []) if data else []
    except: return []

def d1_execute(sql):
    if DRY_RUN: return True
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    return result.returncode == 0

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def main():
    print("=" * 60)
    print("HUNTER BROAD MATCH — Cross-reference 175K contacts")
    print(f"Limit: {LIMIT or 'ALL'} | Dry-run: {DRY_RUN}")
    print("=" * 60)

    stats = {"ceo": 0, "cfo": 0, "hr": 0, "writes": 0, "skipped": 0}
    processed = 0
    total = LIMIT if LIMIT else 999999

    for slot_type, match in SLOT_MATCH.items():
        seniority_list = ", ".join(f"'{s}'" if s else "NULL" for s in match["seniority"])
        dept_list = ", ".join(f"'{d}'" if d else "NULL" for d in match["departments"])

        # Handle NULL department matching
        dept_clause_parts = []
        for d in match["departments"]:
            if d is None:
                dept_clause_parts.append("ehc.department IS NULL")
            else:
                dept_clause_parts.append(f"ehc.department = '{d}'")
        dept_clause = "(" + " OR ".join(dept_clause_parts) + ")"

        page_processed = 0
        while page_processed < total:
            page = min(PAGE_SIZE, total - page_processed)

            # Join empty slots to Hunter contacts
            sql = f"""
                SELECT sw.slot_id, sw.slot_type, sw.company_name,
                       ehc.first_name, ehc.last_name, ehc.email,
                       ehc.linkedin_url, ehc.job_title, ehc.confidence_score,
                       ehc.seniority_level, ehc.department
                FROM slot_workbench sw
                JOIN enrichment_hunter_contact ehc ON sw.outreach_id = ehc.outreach_id
                WHERE sw.has_name = 0
                AND sw.slot_type = '{slot_type}'
                AND ehc.first_name IS NOT NULL AND ehc.first_name != ''
                AND ehc.seniority_level IN ({seniority_list})
                AND {dept_clause}
                ORDER BY ehc.confidence_score DESC
                LIMIT {page}
            """

            rows = d1_query(sql)
            if not rows: break

            # Dedup by slot_id — take highest confidence per slot
            seen_slots = set()
            batch = []
            for row in rows:
                sid = row["slot_id"]
                if sid in seen_slots:
                    stats["skipped"] += 1
                    continue
                seen_slots.add(sid)

                first = row["first_name"].strip()
                last = row["last_name"].strip()
                li = row.get("linkedin_url") or None

                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                full = f"{first} {last}"

                parts = [
                    f"person_first_name = {esc(first)}",
                    f"person_last_name = {esc(last)}",
                    f"person_full_name = {esc(full)}",
                    f"person_source = 'hunter_broad_match'",
                    f"has_name = 1",
                    f"person_found_at = {esc(now)}",
                    f"readiness_tier = 'NAME_ONLY'",
                ]
                if li:
                    parts.append(f"person_linkedin = {esc(li)}")
                    parts.append(f"has_linkedin = 1")
                    parts.append(f"linkedin_found_at = {esc(now)}")

                batch.append(f"UPDATE slot_workbench SET {', '.join(parts)} WHERE slot_id = {esc(sid)}")
                stats[slot_type.lower()] += 1

                if len(batch) >= WRITE_BATCH:
                    d1_execute("; ".join(batch))
                    stats["writes"] += len(batch)
                    batch = []

            if batch:
                d1_execute("; ".join(batch))
                stats["writes"] += len(batch)

            page_processed += len(rows)
            filled = stats["ceo"] + stats["cfo"] + stats["hr"]
            print(f"  [{slot_type}] processed={page_processed} filled={stats[slot_type.lower()]}")

            if len(rows) < page: break

        processed += page_processed

    filled = stats["ceo"] + stats["cfo"] + stats["hr"]
    print(f"\n{'='*60}")
    print(f"HUNTER BROAD MATCH COMPLETE")
    print(f"{'='*60}")
    print(f"  CEO fills: {stats['ceo']}")
    print(f"  CFO fills: {stats['cfo']}")
    print(f"  HR fills:  {stats['hr']}")
    print(f"  Total:     {filled}")
    print(f"  D1 writes: {stats['writes']}")
    print(f"  Skipped:   {stats['skipped']} (dupes)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

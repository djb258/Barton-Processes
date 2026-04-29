"""
Process 200 — Branch 1: Database Joins (all structured sources)

Runs every database source that already has structure defined.
Pure SQL joins — no proxy, no search, no cost.

Sources:
  1. Hunter contacts (175K) — seniority+department → slot_type
  2. recon_emails (7.5K) — write email to person_email
  3. Vendor people — check for unique fills
  4. DOL signers — already ran (1,979 fills), skip

BAR-197 | Session 13

Usage:
  python3 branch1-database-joins.py --limit 100
  python3 branch1-database-joins.py --dry-run
  python3 branch1-database-joins.py
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

# Full slot_type mapping for Hunter seniority+department
HUNTER_SLOT_MAP = {
    "CEO": [
        ("C-Level/Owner", "Executive"),
        ("C-Level/Owner", "Management"),
        ("C-Level/Owner", "Operations & logistics"),
        ("C-Level/Owner", "Sales"),
        ("C-Level/Owner", None),
        ("Director", "Executive"),
        ("Director", "Management"),
        ("Director", "Operations & logistics"),
    ],
    "CFO": [
        ("C-Level/Owner", "Finance"),
        ("Director", "Finance"),
        ("Manager", "Finance"),
        ("VP", "Finance"),
    ],
    "HR": [
        ("C-Level/Owner", "HR"),
        ("Director", "HR"),
        ("Manager", "HR"),
        ("VP", "HR"),
    ],
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


def source1_hunter_contacts():
    """Join enrichment_hunter_contact to empty slots by outreach_id + seniority → slot_type."""
    print("\n" + "=" * 60)
    print("SOURCE 1: Hunter Contacts → Slot Fills")
    print("=" * 60)

    stats = {"ceo": 0, "cfo": 0, "hr": 0}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for slot_type, mappings in HUNTER_SLOT_MAP.items():
        for seniority, department in mappings:
            dept_clause = f"ehc.department = '{department}'" if department else "ehc.department IS NULL"

            sql = f"""
                SELECT sw.slot_id, sw.outreach_id, ehc.first_name, ehc.last_name,
                       ehc.email, ehc.linkedin_url, ehc.job_title, ehc.confidence_score
                FROM slot_workbench sw
                JOIN enrichment_hunter_contact ehc ON sw.outreach_id = ehc.outreach_id
                WHERE sw.has_name = 0
                AND sw.slot_type = '{slot_type}'
                AND ehc.first_name IS NOT NULL AND ehc.first_name != ''
                AND ehc.last_name IS NOT NULL AND ehc.last_name != ''
                AND ehc.seniority_level = '{seniority}'
                AND {dept_clause}
                ORDER BY ehc.confidence_score DESC
                LIMIT {PAGE_SIZE}
            """

            rows = d1_query(sql)
            if not rows:
                continue

            seen = set()
            batch = []
            for row in rows:
                sid = row["slot_id"]
                if sid in seen: continue
                seen.add(sid)

                first = row["first_name"].strip()
                last = row["last_name"].strip()
                full = f"{first} {last}"
                li = row.get("linkedin_url") or None
                email = row.get("email") or None

                parts = [
                    f"person_first_name = {esc(first)}",
                    f"person_last_name = {esc(last)}",
                    f"person_full_name = {esc(full)}",
                    f"person_source = 'branch1_hunter_{slot_type.lower()}'",
                    f"has_name = 1",
                    f"person_found_at = {esc(now)}",
                    f"readiness_tier = 'NAME_ONLY'",
                ]
                if li:
                    parts.append(f"person_linkedin = {esc(li)}")
                    parts.append(f"has_linkedin = 1")
                    parts.append(f"linkedin_found_at = {esc(now)}")
                if email:
                    parts.append(f"person_email = {esc(email)}")
                    parts.append(f"has_email = 1")
                    parts.append(f"email_found_at = {esc(now)}")

                # Recalc tier
                has_email = 1 if email else 0
                has_li = 1 if li else 0
                if has_email and has_li:
                    parts[-7] = "readiness_tier = 'FULL'"
                elif has_email or has_li:
                    parts[-7 if not li else -4] = "readiness_tier = 'REACHABLE'"

                batch.append(f"UPDATE slot_workbench SET {', '.join(parts)} WHERE slot_id = {esc(sid)}")
                stats[slot_type.lower()] += 1

                if len(batch) >= WRITE_BATCH:
                    d1_execute("; ".join(batch))
                    batch = []

            if batch:
                d1_execute("; ".join(batch))

            if seen:
                print(f"  {slot_type} ({seniority}/{department}): {len(seen)} fills")

    total = stats["ceo"] + stats["cfo"] + stats["hr"]
    print(f"\n  Hunter total: CEO={stats['ceo']} CFO={stats['cfo']} HR={stats['hr']} = {total}")
    return total


def source2_recon_emails():
    """Write recon_emails to person_email for slots that have a name but no email."""
    print("\n" + "=" * 60)
    print("SOURCE 2: recon_emails → person_email")
    print("=" * 60)

    filled = 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    processed = 0

    while True:
        rows = d1_query(f"""
            SELECT slot_id, recon_emails, domain
            FROM slot_workbench
            WHERE has_email = 0 AND has_name = 1
            AND recon_emails IS NOT NULL AND recon_emails != '' AND recon_emails != '[]'
            LIMIT {PAGE_SIZE}
        """)
        if not rows: break

        batch = []
        for row in rows:
            try:
                emails = json.loads(row["recon_emails"])
            except: continue
            if not emails or not isinstance(emails, list): continue

            domain = (row.get("domain") or "").lower()
            # Pick best email — prefer one matching company domain
            best = None
            for em in emails:
                if isinstance(em, str) and "@" in em:
                    if domain and domain in em.lower():
                        best = em
                        break
                    if not best:
                        best = em

            if best:
                parts = [
                    f"person_email = {esc(best)}",
                    f"has_email = 1",
                    f"email_found_at = {esc(now)}",
                    f"person_source = CASE WHEN person_source IS NULL THEN 'branch1_recon_email' ELSE person_source END",
                ]
                # Update tier
                batch.append(f"UPDATE slot_workbench SET {', '.join(parts)}, readiness_tier = CASE WHEN has_linkedin = 1 THEN 'FULL' ELSE 'REACHABLE' END WHERE slot_id = {esc(row['slot_id'])}")
                filled += 1

            if len(batch) >= WRITE_BATCH:
                d1_execute("; ".join(batch))
                batch = []

        if batch:
            d1_execute("; ".join(batch))

        processed += len(rows)
        print(f"  [{processed}] filled={filled}")

        if len(rows) < PAGE_SIZE: break

    print(f"\n  recon_emails total: {filled} emails written")
    return filled


def source3_vendor_people():
    """Check vendor_people for unique fills not covered by Hunter."""
    print("\n" + "=" * 60)
    print("SOURCE 3: Vendor People → Slot Fills")
    print("=" * 60)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    filled = 0

    for slot_type in ["CEO", "CFO", "HR"]:
        slot_lower = slot_type.lower()
        rows = d1_query(f"""
            SELECT sw.slot_id, vp.first_name, vp.last_name, vp.email, vp.linkedin_url
            FROM slot_workbench sw
            JOIN vendor_people vp ON sw.outreach_id = vp.outreach_id
            WHERE sw.has_name = 0
            AND sw.slot_type = '{slot_type}'
            AND vp.first_name IS NOT NULL AND vp.first_name != ''
            AND vp.last_name IS NOT NULL AND vp.last_name != ''
            AND vp.mapped_slot_type = '{slot_lower}'
            LIMIT {PAGE_SIZE}
        """)
        if not rows:
            print(f"  {slot_type}: 0 vendor matches")
            continue

        seen = set()
        batch = []
        for row in rows:
            sid = row["slot_id"]
            if sid in seen: continue
            seen.add(sid)

            first = row["first_name"].strip()
            last = row["last_name"].strip()
            full = f"{first} {last}"
            li = row.get("linkedin_url") or None
            email = row.get("email") or None

            parts = [
                f"person_first_name = {esc(first)}",
                f"person_last_name = {esc(last)}",
                f"person_full_name = {esc(full)}",
                f"person_source = 'branch1_vendor_{slot_lower}'",
                f"has_name = 1",
                f"person_found_at = {esc(now)}",
                f"readiness_tier = 'NAME_ONLY'",
            ]
            if li:
                parts.append(f"person_linkedin = {esc(li)}")
                parts.append(f"has_linkedin = 1")
            if email:
                parts.append(f"person_email = {esc(email)}")
                parts.append(f"has_email = 1")
            if li and email:
                parts[-5] = "readiness_tier = 'FULL'"
            elif li or email:
                parts[-5 if not li else -2] = "readiness_tier = 'REACHABLE'"

            batch.append(f"UPDATE slot_workbench SET {', '.join(parts)} WHERE slot_id = {esc(sid)}")
            filled += 1

            if len(batch) >= WRITE_BATCH:
                d1_execute("; ".join(batch))
                batch = []

        if batch:
            d1_execute("; ".join(batch))

        print(f"  {slot_type}: {len(seen)} vendor fills")

    print(f"\n  Vendor total: {filled}")
    return filled


def main():
    print("=" * 60)
    print("BRANCH 1: DATABASE JOINS — All Structured Sources")
    print(f"BAR-197 | Dry-run: {DRY_RUN}")
    print("=" * 60)

    count = d1_query("SELECT COUNT(*) as c FROM slot_workbench WHERE has_name = 0")
    start_empty = count[0]["c"] if count else 0
    print(f"\nStarting empty slots: {start_empty}")

    s1 = source1_hunter_contacts()
    s2 = source2_recon_emails()
    s3 = source3_vendor_people()

    count = d1_query("SELECT COUNT(*) as c FROM slot_workbench WHERE has_name = 0")
    end_empty = count[0]["c"] if count else 0

    total = s1 + s2 + s3
    print(f"\n{'='*60}")
    print(f"BRANCH 1 COMPLETE")
    print(f"{'='*60}")
    print(f"  Hunter contacts:  {s1}")
    print(f"  recon_emails:     {s2}")
    print(f"  Vendor people:    {s3}")
    print(f"  Total fills:      {total}")
    print(f"  Started empty:    {start_empty}")
    print(f"  Now empty:        {end_empty}")
    print(f"{'='*60}")

    # Tier snapshot
    tiers = d1_query("SELECT readiness_tier, COUNT(*) as cnt FROM slot_workbench GROUP BY readiness_tier ORDER BY cnt DESC")
    if tiers:
        print("\nWORKBENCH STATE:")
        for t in tiers:
            print(f"  {t['readiness_tier']:15s} {t['cnt']:>6,}")


if __name__ == "__main__":
    main()

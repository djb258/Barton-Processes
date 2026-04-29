"""
Process 200 — DOL 5500 Signer Match

The 5500 form requires signatures. spons_signed_name = typically CEO/owner.
admin_signed_name = typically CFO, HR, or benefits administrator.

These person names are in Neon dol.form_5500 but were never SEEDed to D1.
This script queries Neon directly, matches signers to empty slots via EIN,
and fills person names.

Mapping:
  spons_signed_name → CEO slot (sponsor = owner/president/CEO)
  admin_signed_name → CFO or HR slot (admin = finance or benefits person)
  If spons != admin → two different people, fill both

Join path: dol.form_5500.sponsor_dfe_ein → D1 slot_workbench.ein → outreach_id

Zero API cost. Data we already paid for via DOL EFAST2 bulk download.

Usage:
  python3 dol-signer-match.py --limit 100
  python3 dol-signer-match.py --dry-run
  python3 dol-signer-match.py
"""

import json
import re
import sys
import os
import subprocess
from datetime import datetime, timezone

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

LIMIT = 0
DRY_RUN = False
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

# Neon connection
NEON_URL = os.environ.get("NEON_URL", "")


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

def neon_query(sql):
    result = subprocess.run(
        ["psql", NEON_URL, "-t", "-A", "-F", "\t", "-c", sql],
        capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"[NEON ERROR] {result.stderr[:200]}")
        return []
    rows = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            rows.append(line.split("\t"))
    return rows

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def clean_name(raw):
    """Clean a DOL signer name into first/last."""
    if not raw or len(raw.strip()) < 3:
        return None, None
    name = raw.strip()
    # Remove suffixes like ", CPA" ", DMD" ", III" etc
    name = re.sub(r',\s*(CPA|DMD|DDS|MD|ESQ|JR|SR|II|III|IV|LLC|INC|PC|PLLC|PA|LTD)\.?$', '', name, flags=re.I)
    name = name.strip().rstrip(',').strip()
    # Title case if all caps
    if name.isupper():
        name = name.title()
    parts = name.split()
    if len(parts) < 2:
        return None, None
    # Handle "LAST, FIRST" format
    if ',' in name:
        comma_parts = name.split(',', 1)
        last = comma_parts[0].strip().title()
        first = comma_parts[1].strip().title().split()[0] if comma_parts[1].strip() else ""
        if first and last and len(first) > 1 and len(last) > 1:
            return first, last
    # Standard "FIRST LAST" or "FIRST MIDDLE LAST"
    first = parts[0]
    last = parts[-1]
    # Skip if looks like company name
    company_words = {"inc", "llc", "ltd", "corp", "company", "co", "group", "services",
                     "committee", "association", "trust", "fund", "plan", "board"}
    if any(w.lower().rstrip('.') in company_words for w in parts):
        return None, None
    if len(first) > 1 and len(last) > 1 and first[0].isupper() and last[0].isupper():
        return first, last
    return None, None


def main():
    if not NEON_URL:
        print("ERROR: NEON_URL env var required")
        sys.exit(1)

    print("=" * 60)
    print("DOL 5500 SIGNER MATCH")
    print(f"Limit: {LIMIT or 'ALL'} | Dry-run: {DRY_RUN}")
    print("=" * 60)

    # Step 1: Get EINs for companies with empty slots
    print("\n[1] Loading EINs for companies with empty slots...")
    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""
    ein_rows = d1_query(f"""
        SELECT DISTINCT ein, outreach_id
        FROM slot_workbench
        WHERE has_name = 0 AND ein IS NOT NULL AND ein != ''
        {limit_clause}
    """)
    if not ein_rows:
        print("No EINs found for empty slots. Done.")
        return

    # Build EIN → outreach_id map
    ein_map = {}
    for row in ein_rows:
        ein = row["ein"]
        if ein not in ein_map:
            ein_map[ein] = row["outreach_id"]

    print(f"  Found {len(ein_map)} unique EINs for empty-slot companies")

    # Step 2: Query Neon for DOL signer names matching these EINs
    print("\n[2] Querying Neon for DOL 5500 signer names...")

    # Batch EINs to avoid massive IN clause
    ein_list = list(ein_map.keys())
    all_signers = []
    batch_size = 500

    for batch_start in range(0, len(ein_list), batch_size):
        batch = ein_list[batch_start:batch_start + batch_size]
        ein_str = ", ".join(f"'{e}'" for e in batch)
        sql = f"""
            SELECT DISTINCT ON (sponsor_dfe_ein)
                sponsor_dfe_ein, spons_signed_name, admin_signed_name, sponsor_dfe_name, form_year
            FROM dol.form_5500
            WHERE sponsor_dfe_ein IN ({ein_str})
            AND (spons_signed_name IS NOT NULL AND spons_signed_name != ''
              OR admin_signed_name IS NOT NULL AND admin_signed_name != '')
            ORDER BY sponsor_dfe_ein, form_year DESC
        """
        rows = neon_query(sql)
        for row in rows:
            if len(row) >= 5:
                all_signers.append({
                    "ein": row[0],
                    "spons_signed": row[1] if row[1] else "",
                    "admin_signed": row[2] if row[2] else "",
                    "company": row[3],
                    "year": row[4],
                })
        pct = min(100, (batch_start + batch_size) / len(ein_list) * 100)
        print(f"  Queried {min(batch_start + batch_size, len(ein_list))}/{len(ein_list)} EINs ({pct:.0f}%) — found {len(all_signers)} signers so far")

    print(f"  Total: {len(all_signers)} companies with DOL signer names")

    if not all_signers:
        print("No signers found. Done.")
        return

    # Step 3: Match signers to empty slots
    print("\n[3] Matching signers to empty slots...")

    stats = {"ceo_filled": 0, "cfo_filled": 0, "hr_filled": 0, "no_match": 0, "bad_name": 0, "writes": 0}

    for signer in all_signers:
        ein = signer["ein"]
        outreach_id = ein_map.get(ein)
        if not outreach_id:
            stats["no_match"] += 1
            continue

        spons_first, spons_last = clean_name(signer["spons_signed"])
        admin_first, admin_last = clean_name(signer["admin_signed"])

        # Get empty slots for this company
        slots = d1_query(f"""
            SELECT slot_id, slot_type FROM slot_workbench
            WHERE outreach_id = '{outreach_id}' AND has_name = 0
        """)

        if not slots:
            continue

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        batch = []

        for slot in slots:
            sid = slot["slot_id"]
            stype = slot["slot_type"]
            first = last = None
            source = None

            if stype == "CEO" and spons_first and spons_last:
                first, last = spons_first, spons_last
                source = "dol_5500_sponsor_signer"
            elif stype in ("CFO", "HR") and admin_first and admin_last:
                # Only use admin if different from sponsor (otherwise it's the same person)
                if not spons_first or admin_first.lower() != spons_first.lower() or admin_last.lower() != spons_last.lower():
                    first, last = admin_first, admin_last
                    source = "dol_5500_admin_signer"
                elif spons_first and spons_last:
                    # Same person signed both — still use for CEO slot only
                    pass

            if first and last and source:
                full = f"{first} {last}"
                parts = [
                    f"person_first_name = {esc(first)}",
                    f"person_last_name = {esc(last)}",
                    f"person_full_name = {esc(full)}",
                    f"person_source = {esc(source)}",
                    f"has_name = 1",
                    f"person_found_at = {esc(now)}",
                    f"readiness_tier = 'NAME_ONLY'",
                ]
                batch.append(f"UPDATE slot_workbench SET {', '.join(parts)} WHERE slot_id = {esc(sid)}")
                stats[f"{stype.lower()}_filled"] += 1
            else:
                stats["bad_name"] += 1

        if batch:
            d1_execute("; ".join(batch))
            stats["writes"] += len(batch)

    total_filled = stats["ceo_filled"] + stats["cfo_filled"] + stats["hr_filled"]
    print(f"\n{'='*60}")
    print(f"DOL 5500 SIGNER MATCH COMPLETE")
    print(f"{'='*60}")
    print(f"  CEO fills (sponsor signer): {stats['ceo_filled']}")
    print(f"  CFO fills (admin signer):   {stats['cfo_filled']}")
    print(f"  HR fills (admin signer):    {stats['hr_filled']}")
    print(f"  Total filled:               {total_filled}")
    print(f"  Bad names (unparseable):    {stats['bad_name']}")
    print(f"  No EIN match:              {stats['no_match']}")
    print(f"  D1 writes:                 {stats['writes']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

"""
Process 200 — Gate A + B Batch Pass (FREE fills only)

Runs Gate A (organized recon) and Gate B (Hunter promote) across ALL empty slots.
No external calls. No proxy. No cost. Pure D1 read/write.

Gate C (Startpage search) runs separately afterward on remaining misses.

Usage:
  python3 gate-ab-batch.py              # all empty slots
  python3 gate-ab-batch.py --limit 100  # test first 100
  python3 gate-ab-batch.py --dry-run    # report only, no writes
"""

import json
import sys
import os
import subprocess
from datetime import datetime, timezone

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get(
    "WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"),
)

LIMIT = 0
DRY_RUN = False
PAGE_SIZE = 1000
WRITE_BATCH = 50

# Title patterns for Gate B matching
TITLE_PATTERNS = {
    "CEO": ["ceo", "chief executive", "president", "owner", "founder",
            "managing director", "managing partner", "principal",
            "general manager", "executive director"],
    "CFO": ["cfo", "chief financial", "finance director", "vp finance",
            "controller", "comptroller", "treasurer"],
    "HR":  ["hr", "human resource", "benefits", "people officer",
            "chief people", "talent", "personnel", "chro"],
}

BAD_NAMES = {
    "linkedin", "read more", "learn more", "click here", "see more",
    "view all", "sign in", "log in", "join now", "contact us",
    "about us", "our team", "glassdoor", "indeed", "yelp", "facebook",
}

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
    elif args[i] == "--dry-run":
        DRY_RUN = True; i += 1
    else:
        i += 1


def d1_query(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120,
    )
    if result.returncode != 0:
        return []
    try:
        stdout = result.stdout
        start = stdout.find('[')
        if start < 0: return []
        data = json.loads(stdout[start:])
        return data[0].get("results", []) if data else []
    except (json.JSONDecodeError, IndexError, KeyError):
        return []


def d1_execute(sql):
    if DRY_RUN:
        return True
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120,
    )
    return result.returncode == 0


def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def valid_name(name):
    if not name or len(name) < 4 or len(name) > 50: return False
    lower = name.lower()
    if any(bad in lower for bad in BAD_NAMES): return False
    parts = name.split()
    if len(parts) < 2: return False
    if not parts[0][0].isupper() or not parts[-1][0].isupper(): return False
    if any(c in name for c in ["@", "http", ".com", "/"]): return False
    return True


def title_matches(title_text, slot_type):
    if not title_text: return False
    lower = title_text.lower()
    return any(p in lower for p in TITLE_PATTERNS.get(slot_type, []))


def gate_a(slot):
    """Try organized recon data — match bucket to slot_type, promote REJECT for small CEO."""
    organized = slot.get("recon_organized_people")
    if not organized: return None

    try:
        entries = json.loads(organized) if isinstance(organized, str) else organized
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(entries, list): return None

    slot_type = slot["slot_type"]
    try:
        emp = int(slot.get("employees") or 0)
    except (ValueError, TypeError):
        emp = 0

    # Pass 1: exact bucket match with confidence >= 60
    for e in entries:
        if e.get("bucket") == slot_type and e.get("confidence", 0) >= 60:
            name = e.get("name", "").strip()
            if name and valid_name(name):
                return {"name": name, "context": e.get("context", ""), "source": "recon_300"}

    # Pass 2: exact bucket match any confidence
    for e in entries:
        if e.get("bucket") == slot_type:
            name = e.get("name", "").strip()
            if name and valid_name(name):
                return {"name": name, "context": e.get("context", ""), "source": "recon_300"}

    # Pass 3: REJECT promotion for small company CEO
    if slot_type == "CEO" and emp < 50:
        for e in entries:
            if e.get("classification") in ("person", "person_with_title"):
                name = e.get("name", "").strip()
                if name and valid_name(name):
                    return {"name": name, "context": e.get("context", ""), "source": "recon_300_promoted"}

    return None


def gate_b(slot):
    """Try Hunter candidate data — promote if title matches slot_type."""
    h_first = (slot.get("hunter_first_name") or "").strip()
    h_last = (slot.get("hunter_last_name") or "").strip()
    h_title = slot.get("hunter_title") or ""

    if h_first and h_last and title_matches(h_title, slot["slot_type"]):
        full = f"{h_first} {h_last}"
        return {
            "name": full, "first": h_first, "last": h_last,
            "context": h_title, "source": "hunter",
            "linkedin": slot.get("hunter_linkedin"),
        }
    return None


def main():
    print("=" * 60)
    print("Process 200 — Gate A+B Batch (FREE fills only)")
    print(f"Limit: {LIMIT or 'ALL'} | Dry-run: {DRY_RUN}")
    print("=" * 60)

    # Count total
    count_rows = d1_query("SELECT COUNT(*) as cnt FROM slot_workbench WHERE has_name = 0")
    total_empty = count_rows[0]["cnt"] if count_rows else 0
    target = min(LIMIT, total_empty) if LIMIT else total_empty
    print(f"\n{total_empty} empty slots, processing {target}")

    stats = {"gate_a": 0, "gate_b": 0, "missed": 0, "writes": 0, "linkedin": 0}
    processed = 0

    while processed < target:
        page_limit = min(PAGE_SIZE, target - processed)
        sql = (
            f"SELECT slot_id, outreach_id, slot_type, company_name, employees, "
            f"recon_organized_people, "
            f"hunter_first_name, hunter_last_name, hunter_title, hunter_linkedin "
            f"FROM slot_workbench "
            f"WHERE has_name = 0 AND readiness_tier IN ('EMPTY','PATTERN_READY','HUNTER_READY') "
            f"ORDER BY outreach_id LIMIT {page_limit}"
        )
        rows = d1_query(sql)
        if not rows:
            print(f"No more rows at {processed}")
            break

        write_batch = []
        for row in rows:
            match = gate_a(row)
            gate = "A"
            if not match:
                match = gate_b(row)
                gate = "B"

            if match:
                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                if "first" in match:
                    first, last = match["first"], match["last"]
                else:
                    parts = match["name"].split(" ", 1)
                    first = parts[0]
                    last = parts[1] if len(parts) > 1 else ""

                full = match["name"]
                source = match.get("source", "")

                set_parts = [
                    f"person_first_name = {esc(first)}",
                    f"person_last_name = {esc(last)}",
                    f"person_full_name = {esc(full)}",
                    f"person_source = {esc(source)}",
                    f"has_name = 1",
                    f"person_found_at = {esc(now)}",
                    f"readiness_tier = 'NAME_ONLY'",
                ]

                li = match.get("linkedin")
                if li:
                    set_parts.append(f"person_linkedin = {esc(li)}")
                    set_parts.append(f"has_linkedin = 1")
                    set_parts.append(f"linkedin_found_at = {esc(now)}")
                    stats["linkedin"] += 1

                write_batch.append(
                    f"UPDATE slot_workbench SET {', '.join(set_parts)} "
                    f"WHERE slot_id = {esc(row['slot_id'])}"
                )

                if gate == "A": stats["gate_a"] += 1
                else: stats["gate_b"] += 1
            else:
                stats["missed"] += 1

            if len(write_batch) >= WRITE_BATCH:
                ok = d1_execute("; ".join(write_batch))
                stats["writes"] += len(write_batch)
                write_batch = []

        if write_batch:
            ok = d1_execute("; ".join(write_batch))
            stats["writes"] += len(write_batch)
            write_batch = []

        processed += len(rows)
        filled = stats["gate_a"] + stats["gate_b"]
        pct = processed / target * 100
        print(f"  [{processed}/{target}] ({pct:.0f}%) A:{stats['gate_a']} B:{stats['gate_b']} Miss:{stats['missed']} LI:{stats['linkedin']}")

    filled = stats["gate_a"] + stats["gate_b"]
    print(f"\n{'='*60}")
    print(f"GATE A+B BATCH COMPLETE")
    print(f"{'='*60}")
    print(f"  Gate A (organized recon): {stats['gate_a']}")
    print(f"  Gate B (hunter promote):  {stats['gate_b']}")
    print(f"  Total filled (FREE):      {filled}")
    print(f"  Missed (need Gate C):     {stats['missed']}")
    print(f"  LinkedIn bonus:           {stats['linkedin']}")
    print(f"  D1 writes:                {stats['writes']}")
    if filled + stats["missed"] > 0:
        print(f"  Gate A+B hit rate:        {filled/(filled+stats['missed'])*100:.1f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

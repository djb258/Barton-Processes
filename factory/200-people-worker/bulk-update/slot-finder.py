"""
Process 200 Phase 2 — Slot Finder

Searches for CEO/CFO/HR contacts at companies with empty slots.
Uses SearchEngineProxy (Startpage + DataImpulse) — same pattern as drip-fetch.

Input: Companies with empty slots from D1/Neon
Method: Startpage query "{company_name} {slot_type} site:linkedin.com"
Output: Candidate names + titles for slot filling

Usage:
  python3 bulk-update/slot-finder.py                     # All empty slots
  python3 bulk-update/slot-finder.py --limit 100         # Test with 100
  python3 bulk-update/slot-finder.py --slot-type CEO     # Only CEO slots
  python3 bulk-update/slot-finder.py --resume             # Resume interrupted

Env vars: PROXY_USER, PROXY_PASS (DataImpulse credentials)

Output: bulk-update/slot-candidates-YYYY-MM.jsonl
"""

import json
import re
import time
import sys
import os
import math
import random
import urllib.parse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

# ── Config ───────────────────────────────────────────────────

DELAY_MEAN = 5.0
DELAY_STD = 2.0
DELAY_MIN = 2.5
LIMIT = 0
SLOT_TYPE_FILTER = None  # None = all types
OUTPUT_DIR = Path(__file__).parent

PROXY_HOST = os.environ.get("PROXY_HOST", "gw.dataimpulse.com")
PROXY_PORT = os.environ.get("PROXY_PORT", "823")
PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")

# ── Parse args ───────────────────────────────────────────────

args = sys.argv[1:]
resume = False
i = 0
while i < len(args):
    if args[i] == "--delay" and i + 1 < len(args):
        DELAY_MEAN = float(args[i + 1])
        i += 2
    elif args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1])
        i += 2
    elif args[i] == "--slot-type" and i + 1 < len(args):
        SLOT_TYPE_FILTER = args[i + 1].upper()
        i += 2
    elif args[i] == "--resume":
        resume = True
        i += 1
    else:
        i += 1

# ── Helpers ──────────────────────────────────────────────────

def box_muller_delay():
    u1 = max(1e-10, random.random())
    u2 = random.random()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return max(DELAY_MIN, DELAY_MEAN + z * DELAY_STD)


def parse_linkedin_result(title: str) -> dict:
    """Parse a search result title for LinkedIn profile data."""
    title = title.replace("&#39;", "'").replace("&amp;", "&").replace("&#x27;", "'").replace("&quot;", '"')

    # Directory listing
    dir_match = re.match(r'[\d,]+\+?\s+"([^"]+)"\s+profiles?', title)
    if dir_match:
        return {"name": dir_match.group(1), "title": "", "company": "", "type": "directory"}

    # Strip LinkedIn suffix
    cleaned = re.sub(r'\s*[-–|]+\s*LinkedIn\s*$', '', title, flags=re.IGNORECASE).strip()
    if not cleaned:
        return {"name": "", "title": "", "company": "", "type": "empty"}

    dash_idx = cleaned.find(' - ')
    if dash_idx == -1:
        return {"name": cleaned, "title": "", "company": "", "type": "name_only"}

    name = cleaned[:dash_idx].strip()
    rest = cleaned[dash_idx + 3:].strip()

    at_idx = rest.rfind(' at ')
    if at_idx != -1:
        return {"name": name, "title": rest[:at_idx].strip(), "company": rest[at_idx + 4:].strip(), "type": "full"}

    inner_dash = rest.rfind(' - ')
    if inner_dash != -1:
        return {"name": name, "title": rest[:inner_dash].strip(), "company": rest[inner_dash + 3:].strip(), "type": "full"}

    return {"name": name, "title": rest, "company": "", "type": "partial"}


# ── Search for slot candidate ────────────────────────────────

def search_slot_candidate(company_name: str, slot_type: str, proxies: dict | None) -> dict:
    """Search Startpage for a person filling a specific role at a company."""
    fetched_at = datetime.now(timezone.utc).isoformat()

    # Role keywords per slot type
    role_keywords = {
        "CEO": "CEO OR \"Chief Executive\" OR President OR \"General Manager\"",
        "CFO": "CFO OR \"Chief Financial\" OR \"VP Finance\" OR Controller",
        "HR": "\"HR\" OR \"Human Resources\" OR CHRO OR \"Benefits\" OR \"People Officer\"",
    }

    keywords = role_keywords.get(slot_type, slot_type)
    query = urllib.parse.quote(f"{company_name} {keywords} site:linkedin.com")
    url = f"https://www.startpage.com/sp/search?query={query}"

    try:
        kwargs = {"impersonate": "chrome", "timeout": 15}
        if proxies:
            kwargs["proxies"] = proxies

        resp = requests.get(url, **kwargs)

        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}", "fetched_at": fetched_at}

        titles = re.findall(r'<h2[^>]*>(.*?)</h2>', resp.text, re.DOTALL)

        candidates = []
        for t in titles:
            clean = re.sub(r'<[^>]+>', '', t).strip()
            if 'linkedin.com/in/' in resp.text[max(0, resp.text.find(clean)-500):resp.text.find(clean)+500].lower() or 'linkedin' in clean.lower():
                parsed = parse_linkedin_result(clean)
                if parsed["name"] and parsed["type"] in ("full", "partial"):
                    candidates.append({
                        "name": parsed["name"],
                        "title": parsed["title"],
                        "company": parsed["company"],
                        "match_type": parsed["type"],
                        "raw_snippet": clean,
                    })

        if candidates:
            return {
                "error": None,
                "candidates": candidates,
                "best_match": candidates[0],
                "fetched_at": fetched_at,
                "source": "startpage",
            }
        else:
            return {"error": "NO_CANDIDATES", "candidates": [], "fetched_at": fetched_at}

    except Exception as e:
        return {"error": str(e)[:200], "fetched_at": fetched_at}


# ── Main ─────────────────────────────────────────────────────

def main():
    # Get companies with empty slots from Neon
    db_url = os.environ.get("DATABASE_URL",
        "postgresql://Marketing%20DB_owner:npg_OsE4Z2oPCpiT@ep-ancient-waterfall-a42vy0du-pooler.us-east-1.aws.neon.tech/Marketing%20DB?sslmode=require")

    slot_filter = f"AND cs.slot_type = '{SLOT_TYPE_FILTER}'" if SLOT_TYPE_FILTER else ""

    result = subprocess.run([
        "psql", db_url, "-t", "-A", "-c",
        f"""SELECT json_agg(row_to_json(t)) FROM (
            SELECT DISTINCT
                tc.company_unique_id,
                ci.canonical_name as company_name,
                ci.company_domain,
                tc.agent_name,
                cs.slot_type,
                cs.slot_id::text as slot_id
            FROM people.v_territory_companies tc
            JOIN cl.company_identity ci ON ci.company_unique_id::text = tc.company_unique_id
            JOIN people.company_slot cs ON cs.company_unique_id = tc.company_unique_id
            WHERE cs.is_filled = false
            AND ci.canonical_name IS NOT NULL
            AND ci.canonical_name != ''
            {slot_filter}
            ORDER BY tc.agent_name, cs.slot_type
        ) t"""
    ], capture_output=True, text=True)

    if not result.stdout.strip() or result.stdout.strip() == '':
        print("No empty slots with company names found.")
        sys.exit(0)

    slots = json.loads(result.stdout.strip())
    if not slots:
        print("No empty slots found.")
        sys.exit(0)

    # Build proxy
    proxies = None
    if PROXY_USER and PROXY_PASS:
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        proxies = {"http": proxy_url, "https": proxy_url}

    print(f"Loaded {len(slots)} empty slots")
    print(f"Mode: {'PROXY' if proxies else 'DIRECT'}")
    if SLOT_TYPE_FILTER:
        print(f"Filter: {SLOT_TYPE_FILTER} slots only")
    if LIMIT:
        print(f"Limit: {LIMIT}")
        slots = slots[:LIMIT]

    total_seconds = len(slots) * DELAY_MEAN
    print(f"Estimated time: {total_seconds/60:.0f} min ({total_seconds/3600:.1f} hr)")

    run_month = datetime.now().strftime("%Y-%m")
    output_file = OUTPUT_DIR / f"slot-candidates-{run_month}.jsonl"

    # Resume
    already_done = set()
    if resume and output_file.exists():
        with open(output_file) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    already_done.add(rec.get("slot_id", ""))
                except:
                    pass
        print(f"Resuming: {len(already_done)} already done")
        slots = [s for s in slots if s["slot_id"] not in already_done]
        print(f"Remaining: {len(slots)}")

    print(f"Output: {output_file}")
    print()

    out = open(output_file, "a")
    found = 0
    empty = 0
    errors = 0
    start_time = time.time()

    for idx, slot in enumerate(slots):
        company = slot["company_name"]
        slot_type = slot["slot_type"]

        result = search_slot_candidate(company, slot_type, proxies)
        result["company_unique_id"] = slot["company_unique_id"]
        result["company_name"] = company
        result["slot_type"] = slot_type
        result["slot_id"] = slot["slot_id"]
        result["agent_name"] = slot["agent_name"]

        out.write(json.dumps(result) + "\n")
        out.flush()

        if result.get("error") is None:
            found += 1
            best = result["best_match"]
            sys.stdout.write(f"\r  [{idx+1}/{len(slots)}] ✓ {best['name'][:20]:20s} → {slot_type} at {company[:25]}")
        elif result.get("error") == "NO_CANDIDATES":
            empty += 1
        else:
            errors += 1

        if (idx + 1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(f"\n  [{idx+1}/{len(slots)}] Found:{found} Empty:{empty} Err:{errors} | {rate:.0f}/hr | {elapsed/60:.1f}m")

        if idx < len(slots) - 1:
            time.sleep(box_muller_delay())

    out.close()

    elapsed = (time.time() - start_time) / 60
    total = found + empty + errors
    print(f"\n\n{'='*60}")
    print(f"Done in {elapsed:.1f} minutes")
    print(f"FOUND:     {found}/{total} ({found*100//max(total,1)}%)")
    print(f"EMPTY:     {empty}/{total}")
    print(f"ERRORS:    {errors}/{total}")
    print(f"{'='*60}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()

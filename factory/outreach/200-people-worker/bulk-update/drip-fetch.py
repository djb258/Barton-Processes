"""
Process 200 — Drip Fetch (Production)

Queries Startpage (Google results anonymized) for LinkedIn profile metadata.
No LinkedIn contact. No cookies. No auth. No 999.

Architecture:
  Startpage → Google's index → LinkedIn metadata in search snippets
  Routed through DataImpulse residential proxy ($1/GB)
  curl_cffi with Chrome TLS fingerprint impersonation
  Box-Muller jitter for organic timing

Proven: 95% hit rate on 20-profile test (2026-03-19)

Usage:
  python3 bulk-update/drip-fetch.py                          # Production run
  python3 bulk-update/drip-fetch.py --delay 3                # Faster (mean 3s)
  python3 bulk-update/drip-fetch.py --limit 50               # Test with 50
  python3 bulk-update/drip-fetch.py --resume                 # Resume interrupted run
  python3 bulk-update/drip-fetch.py --direct                 # No proxy (from residential IP)

Env vars:
  PROXY_USER, PROXY_PASS — DataImpulse credentials
  PROXY_HOST (default: gw.dataimpulse.com), PROXY_PORT (default: 823)

Output: bulk-update/snapshots-YYYY-MM.jsonl (one JSON per line, append-safe)
"""

import json
import re
import time
import sys
import os
import math
import random
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

# ── Config ───────────────────────────────────────────────────

DELAY_MEAN = 5.0          # Box-Muller mean (seconds)
DELAY_STD = 2.0           # Box-Muller std dev
DELAY_MIN = 2.5           # Floor
LIMIT = 0                 # 0 = all
INPUT_FILE = Path(__file__).parent / "monitor-list.json"
OUTPUT_DIR = Path(__file__).parent
USE_PROXY = True

PROXY_HOST = os.environ.get("PROXY_HOST", "gw.dataimpulse.com")
PROXY_PORT = os.environ.get("PROXY_PORT", "823")
PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")

# Search engine config
STARTPAGE_URL = "https://www.startpage.com/sp/search"

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
    elif args[i] == "--resume":
        resume = True
        i += 1
    elif args[i] == "--direct":
        USE_PROXY = False
        i += 1
    elif args[i] == "--proxy-user" and i + 1 < len(args):
        PROXY_USER = args[i + 1]
        i += 2
    elif args[i] == "--proxy-pass" and i + 1 < len(args):
        PROXY_PASS = args[i + 1]
        i += 2
    else:
        i += 1


# ── Box-Muller Jitter ───────────────────────────────────────

def box_muller_delay():
    """Human-like delay using Box-Muller transform. Not metronomic."""
    u1 = max(1e-10, random.random())
    u2 = random.random()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return max(DELAY_MIN, DELAY_MEAN + z * DELAY_STD)


# ── Parse LinkedIn snippet from search results ───────────────

def parse_linkedin_snippet(title: str) -> dict:
    """
    Parse a Startpage/Google search result title for LinkedIn profile data.

    Formats seen:
      "Name - Title at Company | LinkedIn"        → full match
      "Name - Title at Company - LinkedIn"         → full match
      "Name - Company | LinkedIn"                  → name + company only
      '80+ "Name" profiles - LinkedIn'             → directory listing, name only
    """
    result = {"parsed_name": "", "parsed_title": "", "parsed_company": "", "match_type": "none"}

    if not title:
        return result

    # Clean HTML entities
    title = title.replace("&#39;", "'").replace("&amp;", "&").replace("&#x27;", "'").replace("&quot;", '"')

    # Directory listing: '80+ "Name" profiles - LinkedIn'
    dir_match = re.match(r'[\d,]+\+?\s+"([^"]+)"\s+profiles?\s*[-–|]\s*LinkedIn', title)
    if dir_match:
        result["parsed_name"] = dir_match.group(1).strip()
        result["match_type"] = "directory"
        return result

    # Strip " | LinkedIn" or " - LinkedIn" suffix
    cleaned = re.sub(r'\s*[-–|]+\s*LinkedIn\s*$', '', title, flags=re.IGNORECASE).strip()

    if not cleaned:
        return result

    # Try "Name - Title at Company"
    dash_idx = cleaned.find(' - ')
    if dash_idx == -1:
        result["parsed_name"] = cleaned
        result["match_type"] = "name_only"
        return result

    name = cleaned[:dash_idx].strip()
    rest = cleaned[dash_idx + 3:].strip()
    result["parsed_name"] = name

    # "Title at Company"
    at_idx = rest.rfind(' at ')
    if at_idx != -1:
        result["parsed_title"] = rest[:at_idx].strip()
        result["parsed_company"] = rest[at_idx + 4:].strip()
        result["match_type"] = "full"
        return result

    # "Title - Company" or just "Company"
    inner_dash = rest.rfind(' - ')
    if inner_dash != -1:
        result["parsed_title"] = rest[:inner_dash].strip()
        result["parsed_company"] = rest[inner_dash + 3:].strip()
        result["match_type"] = "full"
        return result

    # Could be just company or just title — store as company
    result["parsed_company"] = rest
    result["match_type"] = "partial"
    return result


# ── Fetch via Startpage ──────────────────────────────────────

def search_startpage(name: str, proxies: dict | None) -> dict:
    """Search Startpage for a LinkedIn profile by person name."""
    fetched_at = datetime.now(timezone.utc).isoformat()

    query = urllib.parse.quote(f"{name} linkedin")
    url = f"{STARTPAGE_URL}?query={query}"

    try:
        kwargs = {"impersonate": "chrome", "timeout": 15}
        if proxies:
            kwargs["proxies"] = proxies

        resp = requests.get(url, **kwargs)

        if resp.status_code != 200:
            return {"error": f"Startpage HTTP {resp.status_code}", "fetched_at": fetched_at, "source": "startpage"}

        # Parse Startpage results — titles are in <h2> tags
        titles = re.findall(r'<h2[^>]*>(.*?)</h2>', resp.text, re.DOTALL)

        for t in titles:
            clean = re.sub(r'<[^>]+>', '', t).strip()
            if 'linkedin' in clean.lower() and len(clean) > 10:
                parsed = parse_linkedin_snippet(clean)
                return {
                    "error": None,
                    "raw_snippet": clean,
                    "parsed_name": parsed["parsed_name"],
                    "parsed_title": parsed["parsed_title"],
                    "parsed_company": parsed["parsed_company"],
                    "match_type": parsed["match_type"],
                    "fetched_at": fetched_at,
                    "source": "startpage",
                    "http_status": 200,
                }

        return {"error": "NO_LINKEDIN_RESULT", "fetched_at": fetched_at, "source": "startpage"}

    except Exception as e:
        return {"error": str(e)[:200], "fetched_at": fetched_at, "source": "startpage"}


# ── Main ─────────────────────────────────────────────────────

def main():
    if not INPUT_FILE.exists():
        print(f"Missing {INPUT_FILE}")
        print("Generate with: npm run bulk:export-list")
        print("Or from Neon:")
        print('  psql $DATABASE_URL -t -A -c "SELECT json_agg(row_to_json(t)) FROM (SELECT person_id, linkedin_url, full_name, title FROM people.v_linkedin_monitor_list m JOIN people.people_master pm ON pm.unique_id = m.person_id WHERE pm.full_name IS NOT NULL LIMIT 100) t" > bulk-update/monitor-list.json')
        sys.exit(1)

    raw = json.loads(INPUT_FILE.read_text())
    if isinstance(raw, list) and len(raw) > 0 and "results" in (raw[0] if isinstance(raw[0], dict) else {}):
        profiles = raw[0]["results"]
    elif isinstance(raw, dict) and "results" in raw:
        profiles = raw["results"]
    else:
        profiles = raw

    # Build proxy config
    proxies = None
    if USE_PROXY and PROXY_USER and PROXY_PASS:
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        proxies = {"http": proxy_url, "https": proxy_url}

    print(f"Loaded {len(profiles)} profiles")
    print(f"Mode: {'PROXY (' + PROXY_HOST + ')' if proxies else 'DIRECT (residential IP)'}")
    print(f"Engine: Startpage → Google index → LinkedIn metadata")
    print(f"Delay: Box-Muller (mean={DELAY_MEAN}s, std={DELAY_STD}s, min={DELAY_MIN}s)")

    if LIMIT:
        print(f"Limit: {LIMIT}")
        profiles = profiles[:LIMIT]

    # Resume support
    run_month = datetime.now().strftime("%Y-%m")
    output_file = OUTPUT_DIR / f"snapshots-{run_month}.jsonl"

    already_fetched = set()
    if resume and output_file.exists():
        with open(output_file) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    already_fetched.add(rec.get("person_id", ""))
                except:
                    pass
        print(f"Resuming: {len(already_fetched)} already done")
        profiles = [p for p in profiles if p.get("person_id", p.get("unique_id", "")) not in already_fetched]
        print(f"Remaining: {len(profiles)}")

    if not profiles:
        print("Nothing to fetch.")
        return

    total_seconds = len(profiles) * DELAY_MEAN
    print(f"Estimated time: {total_seconds / 60:.0f} min ({total_seconds / 3600:.1f} hr)")
    print(f"Output: {output_file}")
    print()

    out = open(output_file, "a")

    full_match = 0
    partial_match = 0
    directory = 0
    no_result = 0
    errors = 0
    start_time = time.time()

    for idx, profile in enumerate(profiles):
        person_id = profile.get("person_id", profile.get("unique_id", ""))
        name = profile.get("full_name", "")
        linkedin_url = profile.get("linkedin_url", "")
        stored_title = profile.get("title", "")

        if not name:
            # Try to extract name from LinkedIn URL slug
            slug = linkedin_url.rstrip("/").split("/in/")[-1] if linkedin_url else ""
            name = slug.replace("-", " ").rsplit(" ", 1)[0] if slug else ""

        result = search_startpage(name, proxies)
        result["person_id"] = person_id
        result["linkedin_url"] = linkedin_url
        result["stored_name"] = name
        result["stored_title"] = stored_title

        # Write to JSONL
        out.write(json.dumps(result) + "\n")
        out.flush()

        # Stats
        if result.get("error") is None:
            mt = result.get("match_type", "none")
            if mt == "full":
                full_match += 1
            elif mt in ("partial", "name_only"):
                partial_match += 1
            elif mt == "directory":
                directory += 1
        elif result.get("error") == "NO_LINKEDIN_RESULT":
            no_result += 1
        else:
            errors += 1

        # Progress
        elapsed = time.time() - start_time
        rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
        total = full_match + partial_match + directory
        sys.stdout.write(
            f"\r  [{idx+1}/{len(profiles)}] "
            f"FULL:{full_match} PARTIAL:{partial_match} DIR:{directory} "
            f"MISS:{no_result} ERR:{errors} "
            f"| {rate:.0f}/hr | {elapsed/60:.1f}m"
        )
        sys.stdout.flush()

        # Delay
        if idx < len(profiles) - 1:
            time.sleep(box_muller_delay())

    out.close()

    elapsed = (time.time() - start_time) / 60
    total_processed = full_match + partial_match + directory + no_result + errors
    total_found = full_match + partial_match + directory

    print(f"\n\n{'='*60}")
    print(f"Done in {elapsed:.1f} minutes ({total_processed} profiles)")
    print(f"")
    print(f"FULL MATCH:   {full_match:5d}  (name + title + company)")
    print(f"PARTIAL:      {partial_match:5d}  (name + company or title)")
    print(f"DIRECTORY:    {directory:5d}  (name only from directory listing)")
    print(f"NO RESULT:    {no_result:5d}")
    print(f"ERRORS:       {errors:5d}")
    print(f"")
    print(f"HIT RATE:     {total_found}/{total_processed} ({total_found*100//max(total_processed,1)}%)")
    print(f"{'='*60}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()

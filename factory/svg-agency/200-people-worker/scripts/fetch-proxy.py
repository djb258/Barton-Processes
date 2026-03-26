#!/usr/bin/env python3
"""
Process 200 — Proxy Fetch Script (External Compute)

CF Workers can't route through HTTP CONNECT proxies.
This script runs OUTSIDE CF Workers and does the Startpage searches
through DataImpulse residential proxy, then writes results back to
D1 via the Process 200 worker API.

Usage:
  doppler run -- python3 scripts/fetch-proxy.py --batch-size 100 --delay 30

Requirements:
  pip install curl_cffi requests

Stack:
  - Startpage (Google results, anonymized)
  - DataImpulse (residential proxy, gw.dataimpulse.com:823)
  - curl_cffi (Chrome TLS fingerprint)
"""

import argparse
import json
import os
import re
import sys
import time
import random
import math
from typing import Optional

try:
    from curl_cffi import requests as curl_requests
except ImportError:
    print("ERROR: curl_cffi not installed. Run: pip install curl_cffi")
    sys.exit(1)

import requests

# ── Config ──────────────────────────────────────────────────

WORKER_URL = "https://people-worker-200.svg-outreach.workers.dev"
SPINE_WORKER_URL = "https://lcs-hub.svg-outreach.workers.dev"

PROXY_HOST = os.environ.get("PROXY_HOST", "gw.dataimpulse.com")
PROXY_PORT = os.environ.get("PROXY_PORT", "823")
PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")

PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

TITLE_MAP = {
    "CEO": 'CEO OR "Chief Executive" OR "President" OR "Owner" OR "Managing Director"',
    "CFO": 'CFO OR "Chief Financial" OR "VP Finance" OR "Controller" OR "Treasurer"',
    "HR": '"HR Director" OR "VP Human Resources" OR "Head of HR" OR "CHRO" OR "HR Manager"',
}


def box_muller_delay(min_ms: int, max_ms: int) -> float:
    """Box-Muller jitter for organic timing."""
    u1 = random.random()
    u2 = random.random()
    z0 = math.sqrt(-2 * math.log(max(u1, 1e-10))) * math.cos(2 * math.pi * u2)
    mean = (min_ms + max_ms) / 2
    std_dev = (max_ms - min_ms) / 6
    delay = mean + z0 * std_dev
    return max(min_ms, min(max_ms, delay)) / 1000.0  # convert to seconds


def search_startpage(slot_type: str, company_name: str, city: str, state: str) -> Optional[dict]:
    """Search Startpage for a LinkedIn profile via DataImpulse proxy."""
    title_query = TITLE_MAP.get(slot_type, slot_type)
    query = f'site:linkedin.com/in/ {title_query} "{company_name}" "{city}" "{state}"'
    url = f"https://www.startpage.com/do/dsearch?query={requests.utils.quote(query)}&cat=web"

    try:
        resp = curl_requests.get(
            url,
            proxies={"http": PROXY_URL, "https": PROXY_URL},
            impersonate="chrome120",
            timeout=20,
        )

        if resp.status_code != 200:
            return None

        html = resp.text

        # Find LinkedIn URLs in results
        linkedin_pattern = r'href="(https?://(?:www\.)?linkedin\.com/in/[^"]+)"'
        matches = re.findall(linkedin_pattern, html)

        if not matches:
            return None

        linkedin_url = matches[0]

        # Try to extract the title text near the LinkedIn URL
        # Startpage result titles contain "Name - Title at Company | LinkedIn"
        title_pattern = r'>([^<]*?' + re.escape("linkedin.com") + r'[^<]*?)<'
        title_matches = re.findall(title_pattern, html, re.IGNORECASE)

        # Also look for result title elements
        result_title_pattern = r'<h[23][^>]*>.*?<a[^>]*href="' + re.escape(linkedin_url) + r'"[^>]*>([^<]+)</a>'
        result_titles = re.findall(result_title_pattern, html, re.DOTALL)

        raw_snippet = result_titles[0] if result_titles else (title_matches[0] if title_matches else "")

        # Parse the LinkedIn title format
        parsed = parse_linkedin_title(raw_snippet)

        if parsed and parsed["name"]:
            return {
                "name": parsed["name"],
                "title": parsed["title"],
                "company": parsed["company"],
                "linkedin_url": clean_linkedin_url(linkedin_url),
                "source": "startpage_proxy",
                "raw_snippet": raw_snippet[:200],
            }

        # Fallback: try fetching the LinkedIn URL directly for the <title> tag
        return fetch_linkedin_title(linkedin_url)

    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def fetch_linkedin_title(url: str) -> Optional[dict]:
    """Fetch LinkedIn profile page to get <title> tag."""
    try:
        resp = curl_requests.get(
            url,
            proxies={"http": PROXY_URL, "https": PROXY_URL},
            impersonate="chrome120",
            timeout=15,
            allow_redirects=True,
        )

        if resp.status_code != 200:
            return None

        title_match = re.search(r'<title>([^<]+)</title>', resp.text, re.IGNORECASE)
        if not title_match:
            return None

        parsed = parse_linkedin_title(title_match.group(1))
        if parsed and parsed["name"]:
            return {
                "name": parsed["name"],
                "title": parsed["title"],
                "company": parsed["company"],
                "linkedin_url": clean_linkedin_url(url),
                "source": "linkedin_direct",
                "raw_snippet": title_match.group(1)[:200],
            }

        return None
    except Exception:
        return None


def parse_linkedin_title(raw: str) -> Optional[dict]:
    """Parse LinkedIn title: 'Name - Title at Company | LinkedIn'"""
    if not raw:
        return None

    cleaned = re.sub(r'\s*\|\s*LinkedIn\s*$', '', raw, flags=re.IGNORECASE).strip()
    if not cleaned or len(cleaned) < 3:
        return None

    # "Name - Title at Company"
    at_match = re.match(r'^(.+?)\s*[-–]\s*(.+?)\s+at\s+(.+)$', cleaned, re.IGNORECASE)
    if at_match:
        return {"name": at_match.group(1).strip(), "title": at_match.group(2).strip(), "company": at_match.group(3).strip()}

    # "Name - Title - Company"
    parts = re.split(r'\s*[-–]\s*', cleaned)
    if len(parts) >= 3:
        return {"name": parts[0].strip(), "title": parts[1].strip(), "company": " - ".join(parts[2:]).strip()}

    if len(parts) == 2:
        return {"name": parts[0].strip(), "title": parts[1].strip(), "company": ""}

    if len(cleaned) < 60:
        return {"name": cleaned, "title": "", "company": ""}

    return None


def clean_linkedin_url(url: str) -> str:
    """Clean LinkedIn URL to canonical form."""
    match = re.match(r'(https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-]+)', url)
    return f"https://www.linkedin.com/in/{match.group(1).split('/in/')[-1]}" if match else url


def get_empty_slots(limit: int = 100) -> list:
    """Get empty slots from Process 200 worker — DOL-linked first."""
    try:
        # Use wrangler d1 execute to get empty slots with company info
        import subprocess
        result = subprocess.run(
            ["wrangler", "d1", "execute", "svg-d1-outreach-ops", "--remote", "--json",
             "--command", f"""
                SELECT cs.slot_id, cs.outreach_id, cs.company_unique_id, cs.slot_type,
                       ct.city, ct.state,
                       d.filing_present
                FROM people_company_slot cs
                JOIN outreach_company_target ct ON cs.outreach_id = ct.outreach_id
                LEFT JOIN outreach_dol d ON cs.outreach_id = d.outreach_id
                WHERE cs.is_filled = 0
                ORDER BY d.filing_present DESC NULLS LAST, cs.slot_type
                LIMIT {limit}
             """],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        return data[0]["results"]
    except Exception as e:
        print(f"ERROR getting slots: {e}")
        return []


def get_company_name(outreach_id: str) -> Optional[str]:
    """Get company name from spine D1."""
    try:
        import subprocess
        result = subprocess.run(
            ["wrangler", "d1", "execute", "svg-d1-spine", "--remote", "--json",
             "--command", f"SELECT canonical_name FROM cl_company_identity WHERE outreach_id = '{outreach_id}' LIMIT 1"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        if data[0]["results"]:
            return data[0]["results"][0]["canonical_name"]
        return None
    except Exception:
        return None


def write_result(slot_id: str, company_unique_id: str, result: dict):
    """Write result back to D1 via wrangler."""
    try:
        import subprocess
        unique_id = f"proxy-{slot_id[:8]}-{int(time.time())}"
        first_name = result["name"].split(" ")[0] if result["name"] else ""
        last_name = " ".join(result["name"].split(" ")[1:]) if result["name"] else ""

        # Insert person
        subprocess.run(
            ["wrangler", "d1", "execute", "svg-d1-outreach-ops", "--remote",
             "--command", f"""
                INSERT OR REPLACE INTO people_people_master (
                    unique_id, company_unique_id, company_slot_unique_id,
                    first_name, last_name, full_name, title,
                    linkedin_url, source_system,
                    promoted_from_intake_at, last_verified_at,
                    created_at, updated_at, email_verified, outreach_ready
                ) VALUES (
                    '{unique_id}', '{company_unique_id}', '{slot_id}',
                    '{first_name.replace("'", "''")}', '{last_name.replace("'", "''")}',
                    '{result["name"].replace("'", "''")}', '{result["title"].replace("'", "''")}',
                    '{result["linkedin_url"]}', '{result["source"]}',
                    datetime('now'), datetime('now'),
                    datetime('now'), datetime('now'), 0, 0
                )
             """],
            capture_output=True, text=True, timeout=15
        )

        # Update slot
        subprocess.run(
            ["wrangler", "d1", "execute", "svg-d1-outreach-ops", "--remote",
             "--command", f"""
                UPDATE people_company_slot
                SET person_unique_id = '{unique_id}', is_filled = 1,
                    filled_at = datetime('now'), source_system = '{result["source"]}',
                    confidence_score = 0.7, updated_at = datetime('now')
                WHERE slot_id = '{slot_id}'
             """],
            capture_output=True, text=True, timeout=15
        )

        return True
    except Exception as e:
        print(f"  WRITE ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Process 200 — Proxy Fetch Script")
    parser.add_argument("--batch-size", type=int, default=100, help="Slots to process per run")
    parser.add_argument("--min-delay", type=int, default=30000, help="Min delay between fetches (ms)")
    parser.add_argument("--max-delay", type=int, default=120000, help="Max delay between fetches (ms)")
    parser.add_argument("--dry-run", action="store_true", help="Search but don't write results")
    args = parser.parse_args()

    if not PROXY_USER:
        print("ERROR: PROXY_USER not set. Run with: doppler run -- python3 scripts/fetch-proxy.py")
        sys.exit(1)

    print(f"Process 200 — Proxy Fetch Script")
    print(f"Proxy: {PROXY_HOST}:{PROXY_PORT}")
    print(f"Batch size: {args.batch_size}")
    print(f"Delay: {args.min_delay}-{args.max_delay}ms")
    print(f"Dry run: {args.dry_run}")
    print()

    # Get empty slots
    slots = get_empty_slots(args.batch_size)
    print(f"Got {len(slots)} empty slots")

    filled = 0
    skipped = 0
    errors = 0

    for i, slot in enumerate(slots):
        print(f"\n[{i+1}/{len(slots)}] {slot['slot_type']} for {slot['outreach_id'][:8]}... ({slot['city']}, {slot['state']})")

        # Get company name
        company_name = get_company_name(slot["outreach_id"])
        if not company_name:
            print("  SKIP: no company name")
            skipped += 1
            continue

        print(f"  Company: {company_name}")

        # Search
        result = search_startpage(slot["slot_type"], company_name, slot["city"], slot["state"])

        if not result:
            print("  SKIP: no result")
            skipped += 1
        else:
            print(f"  FOUND: {result['name']} — {result['title']}")
            print(f"  LinkedIn: {result['linkedin_url']}")

            if not args.dry_run:
                if write_result(slot["slot_id"], slot["company_unique_id"], result):
                    print("  WRITTEN to D1")
                    filled += 1
                else:
                    errors += 1
            else:
                print("  DRY RUN — not writing")
                filled += 1

        # Delay between fetches
        if i < len(slots) - 1:
            delay = box_muller_delay(args.min_delay, args.max_delay)
            print(f"  Waiting {delay:.1f}s...")
            time.sleep(delay)

    print(f"\n{'='*60}")
    print(f"DONE: processed={len(slots)} filled={filled} skipped={skipped} errors={errors}")


if __name__ == "__main__":
    main()

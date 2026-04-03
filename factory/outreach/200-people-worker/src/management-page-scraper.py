"""
Process 200 — Management Page Scraper

Fetches the about_url (leadership/team page) for each company with empty slots.
Parses ALL names and titles from the page. Fills CEO, CFO, and HR slots in one pass.

One fetch per company. Up to 3 fills per fetch. The management page is the source of truth.

Input: about_url from slot_workbench (discovered by Process 300)
Output: person_first_name, person_last_name, person_source per slot

Uses DataImpulse proxy + curl_cffi (chrome131 impersonation).

Usage:
  python3 management-page-scraper.py --limit 100
  python3 management-page-scraper.py --dry-run
  python3 management-page-scraper.py --workers 12
  python3 management-page-scraper.py
"""

import json
import re
import time
import sys
import os
import subprocess
import random
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from curl_cffi import requests as creq

# ── Config ───────────────────────────────────────────────────

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"

LIMIT = 0
DRY_RUN = False
NUM_WORKERS = 1
PORT_BASE = 12000
PAGE_SIZE = 500
FETCH_DELAY = 1  # seconds between fetches (real page, not search — can be faster)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Title patterns — what we're looking for on the page
TITLE_TO_SLOT = {
    "CEO": [
        r'\b(?:chief\s+executive|ceo|president|owner|founder|managing\s+director|'
        r'managing\s+partner|principal|general\s+manager|executive\s+director)\b'
    ],
    "CFO": [
        r'\b(?:chief\s+financial|cfo|finance\s+director|vp\s+(?:of\s+)?finance|'
        r'controller|comptroller|treasurer|director\s+of\s+finance)\b'
    ],
    "HR": [
        r'\b(?:chief\s+(?:people|human)|chro|human\s+resource|hr\s+director|'
        r'vp\s+(?:of\s+)?(?:hr|human|people|talent)|director\s+of\s+(?:hr|human|people|talent)|'
        r'benefits\s+(?:manager|director|administrator)|head\s+of\s+(?:hr|people|talent))\b'
    ],
}

COMPILED_PATTERNS = {}
for slot, patterns in TITLE_TO_SLOT.items():
    COMPILED_PATTERNS[slot] = [re.compile(p, re.IGNORECASE) for p in patterns]

# Name extraction pattern — "First Last" near a title
NAME_RE = re.compile(r'([A-Z][a-z]+(?:\s[A-Z]\.?\s*)?(?:\s[A-Z][a-z]+){1,2})')

BAD_NAMES = {
    "read more", "learn more", "click here", "see more", "view all",
    "our team", "about us", "contact us", "leadership team",
    "board of directors", "executive team", "management team",
    "meet our team", "our leadership", "meet the team",
}

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
    elif args[i] == "--workers" and i + 1 < len(args):
        NUM_WORKERS = int(args[i + 1]); i += 2
    elif args[i] == "--port-base" and i + 1 < len(args):
        PORT_BASE = int(args[i + 1]); i += 2
    elif args[i] == "--dry-run":
        DRY_RUN = True; i += 1
    else:
        i += 1


# ── D1 ───────────────────────────────────────────────────────

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


# ── Page Fetcher ─────────────────────────────────────────────

def fetch_page(url, port):
    """Fetch a management page via proxy."""
    if not PROXY_USER or not PROXY_PASS:
        # Try direct fetch (some pages don't need proxy)
        try:
            session = creq.Session(impersonate="chrome131")
            resp = session.get(url, timeout=15, allow_redirects=True)
            if resp.status_code == 200:
                return resp.text
        except:
            pass
        return None

    proxy_url = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"
    try:
        session = creq.Session(impersonate="chrome131")
        resp = session.get(url, proxies={"http": proxy_url, "https": proxy_url},
                          timeout=15, allow_redirects=True, impersonate="chrome131")
        if resp.status_code == 200:
            return resp.text
    except:
        pass
    return None


# ── Page Parser ──────────────────────────────────────────────

def parse_management_page(html, company_name=""):
    """
    Parse a management/leadership page for person names + titles.
    Returns dict of slot_type → {"name": str, "title": str}
    """
    if not html or len(html) < 100:
        return {}

    results = {}
    company_lower = company_name.lower() if company_name else ""

    # Strategy 1: Find name-title pairs in structured HTML
    # Look for patterns like: <h3>John Smith</h3><p>CEO</p>
    # or "John Smith, CEO" or "John Smith - President"

    # Extract text blocks — strip HTML but keep structure boundaries
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Method 1: Scan for title keywords, then look for nearby names
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for slot_type, patterns in COMPILED_PATTERNS.items():
            if slot_type in results:
                continue  # already found this slot
            for pattern in patterns:
                if pattern.search(line_lower):
                    # Found a title — look for name in this line or adjacent lines
                    # Check this line for "Name - Title" or "Name, Title"
                    name_match = NAME_RE.search(line)
                    if name_match:
                        name = name_match.group(1).strip()
                        if _valid_person(name, company_lower):
                            results[slot_type] = {"name": name, "title": line[:80]}
                            break

                    # Check previous line (name often above title)
                    if i > 0:
                        name_match = NAME_RE.search(lines[i-1])
                        if name_match:
                            name = name_match.group(1).strip()
                            if _valid_person(name, company_lower):
                                results[slot_type] = {"name": name, "title": line[:80]}
                                break

                    # Check next line (name sometimes below title)
                    if i < len(lines) - 1:
                        name_match = NAME_RE.search(lines[i+1])
                        if name_match:
                            name = name_match.group(1).strip()
                            if _valid_person(name, company_lower):
                                results[slot_type] = {"name": name, "title": line[:80]}
                                break

    # Method 2: Look for "Name — Title" or "Name, Title" patterns in raw text
    combined = " ".join(lines)
    for slot_type, patterns in COMPILED_PATTERNS.items():
        if slot_type in results:
            continue
        for pattern in patterns:
            # "First Last, Title" or "First Last - Title"
            match = re.search(
                r'([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*[,\-\u2013\u2014|]\s*'
                + pattern.pattern,
                combined, re.IGNORECASE
            )
            if match:
                name = match.group(1).strip()
                if _valid_person(name, company_lower):
                    results[slot_type] = {"name": name, "title": match.group(0)[:80]}
                    break

    # Method 3: LinkedIn profile links on the page
    li_matches = re.findall(
        r'href="(https?://(?:www\.)?linkedin\.com/in/[^"?]+)"[^>]*>.*?'
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)',
        html, re.DOTALL
    )
    for url, name in li_matches:
        if not _valid_person(name, company_lower):
            continue
        # Try to find what slot this person fills by looking at nearby text
        idx = html.find(url)
        if idx >= 0:
            context = html[max(0,idx-500):idx+500].lower()
            for slot_type, patterns in COMPILED_PATTERNS.items():
                if slot_type in results:
                    continue
                for pattern in patterns:
                    if pattern.search(context):
                        results[slot_type] = {"name": name, "title": "", "linkedin": url}
                        break

    return results


def _valid_person(name, company_lower=""):
    """Check if extracted name is a real person."""
    if not name or len(name) < 4 or len(name) > 50:
        return False
    lower = name.lower()
    if lower in BAD_NAMES or any(bad in lower for bad in BAD_NAMES):
        return False
    parts = name.split()
    if len(parts) < 2 or len(parts) > 4:
        return False
    # Check company name overlap
    if company_lower:
        name_words = set(lower.split())
        co_words = set(company_lower.split())
        if co_words and len(name_words & co_words) / max(len(co_words), 1) > 0.5:
            return False
    return True


# ── Main ─────────────────────────────────────────────────────

def process_company(company, port):
    """Fetch and parse one company's management page."""
    outreach_id = company["outreach_id"]
    about_url = company["about_url"]
    company_name = company.get("company_name", "")
    empty_slots = company["empty_slots"]  # list of {slot_id, slot_type}

    html = fetch_page(about_url, port)
    if not html:
        return {"outreach_id": outreach_id, "status": "fetch_failed", "fills": 0}

    parsed = parse_management_page(html, company_name)
    if not parsed:
        return {"outreach_id": outreach_id, "status": "no_names_found", "fills": 0}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    batch = []
    fills = 0

    for slot in empty_slots:
        slot_type = slot["slot_type"]
        if slot_type in parsed:
            person = parsed[slot_type]
            first, last = person["name"].split(" ", 1) if " " in person["name"] else (person["name"], "")
            if not first or not last:
                continue

            parts = [
                f"person_first_name = {esc(first)}",
                f"person_last_name = {esc(last)}",
                f"person_full_name = {esc(person['name'])}",
                f"person_source = 'mgmt_page_scrape'",
                f"has_name = 1",
                f"person_found_at = {esc(now)}",
                f"readiness_tier = 'NAME_ONLY'",
            ]
            li = person.get("linkedin")
            if li:
                parts.append(f"person_linkedin = {esc(li)}")
                parts.append(f"has_linkedin = 1")
                parts.append(f"linkedin_found_at = {esc(now)}")

            batch.append(f"UPDATE slot_workbench SET {', '.join(parts)} WHERE slot_id = {esc(slot['slot_id'])}")
            fills += 1

    if batch:
        d1_execute("; ".join(batch))

    return {"outreach_id": outreach_id, "status": "ok", "fills": fills, "found": list(parsed.keys())}


def main():
    print("=" * 60)
    print("MANAGEMENT PAGE SCRAPER")
    print(f"Limit: {LIMIT or 'ALL'} | Workers: {NUM_WORKERS} | Dry-run: {DRY_RUN}")
    print("=" * 60)

    # Load companies with about_url and empty slots
    print("\nLoading companies with about_url + empty slots...")
    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""

    # Get unique companies with about_url that have empty slots
    companies_raw = d1_query(f"""
        SELECT DISTINCT outreach_id, about_url, company_name
        FROM slot_workbench
        WHERE has_name = 0
        AND about_url IS NOT NULL AND about_url != ''
        ORDER BY outreach_id
        {limit_clause}
    """)

    if not companies_raw:
        print("No companies with about_url + empty slots. Done.")
        return

    # Dedup by outreach_id
    seen = set()
    companies = []
    for row in companies_raw:
        oid = row["outreach_id"]
        if oid not in seen:
            seen.add(oid)
            companies.append(row)

    print(f"Loaded {len(companies)} companies to scrape")

    # Get empty slots per company
    for company in companies:
        slots = d1_query(f"""
            SELECT slot_id, slot_type FROM slot_workbench
            WHERE outreach_id = '{company['outreach_id']}' AND has_name = 0
        """)
        company["empty_slots"] = slots

    stats = {"fetched": 0, "fetch_failed": 0, "no_names": 0, "total_fills": 0,
             "ceo": 0, "cfo": 0, "hr": 0}

    start_time = time.time()

    for i, company in enumerate(companies):
        port = PORT_BASE + (i % 100)
        result = process_company(company, port)

        if result["status"] == "fetch_failed":
            stats["fetch_failed"] += 1
        elif result["status"] == "no_names_found":
            stats["no_names"] += 1
        else:
            stats["fetched"] += 1
            stats["total_fills"] += result["fills"]
            for slot_type in result.get("found", []):
                stats[slot_type.lower()] += 1

        if (i + 1) % 25 == 0 or i == len(companies) - 1:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(f"  [{i+1}/{len(companies)}] fills={stats['total_fills']} "
                  f"CEO={stats['ceo']} CFO={stats['cfo']} HR={stats['hr']} "
                  f"fail={stats['fetch_failed']} empty={stats['no_names']} "
                  f"| {rate:.0f}/hr")

        time.sleep(FETCH_DELAY)

    elapsed_min = (time.time() - start_time) / 60
    print(f"\n{'='*60}")
    print(f"MANAGEMENT PAGE SCRAPER COMPLETE ({elapsed_min:.1f}m)")
    print(f"{'='*60}")
    print(f"  Companies scraped:  {stats['fetched']}")
    print(f"  Fetch failed:       {stats['fetch_failed']}")
    print(f"  No names found:     {stats['no_names']}")
    print(f"  CEO fills:          {stats['ceo']}")
    print(f"  CFO fills:          {stats['cfo']}")
    print(f"  HR fills:           {stats['hr']}")
    print(f"  Total fills:        {stats['total_fills']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

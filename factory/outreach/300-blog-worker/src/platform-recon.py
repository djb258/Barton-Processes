"""
Process 300 — Platform Recon (Section 9 discovery)

One Startpage search per company to discover platform URLs.
Same infrastructure as company-recon.py — same proxy, same pattern.

Query: "{company_name} {city} {state} glassdoor crunchbase bbb capterra indeed facebook"
(LinkedIn and ZoomInfo already captured in original recon)

Extracts platform URLs from results. Stores to slot_workbench.recon_platform_urls.

Usage:
  python3 platform-recon.py --limit 100
  python3 platform-recon.py --stale 90
  python3 platform-recon.py
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

from curl_cffi import requests as creq

# ── Config ───────────────────────────────────────────────────

LIMIT = 0
OFFSET = 0
STALE_DAYS = 0
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT_BASE = 13000
SEARCH_DELAY = 3
PAGE_SIZE = 500

# Platform URL patterns
PLATFORM_PATTERNS = {
    "glassdoor": re.compile(r'https?://(?:www\.)?glassdoor\.com/(?:Overview|Reviews|Salary|Jobs)[^"?\s]*', re.I),
    "crunchbase": re.compile(r'https?://(?:www\.)?crunchbase\.com/(?:organization|person)/[^"?\s]+', re.I),
    "bbb": re.compile(r'https?://(?:www\.)?bbb\.org/us/[^"?\s]+', re.I),
    "capterra": re.compile(r'https?://(?:www\.)?capterra\.com/p/[^"?\s]+', re.I),
    "indeed": re.compile(r'https?://(?:www\.)?indeed\.com/cmp/[^"?\s]+', re.I),
    "facebook": re.compile(r'https?://(?:www\.)?facebook\.com/[^"?\s]+', re.I),
    "google_business": re.compile(r'https?://(?:www\.)?google\.com/maps/place/[^"?\s]+', re.I),
    "x_twitter": re.compile(r'https?://(?:www\.)?x\.com/[^"?\s]+', re.I),
    "linkedin_company": re.compile(r'https?://(?:www\.)?linkedin\.com/company/[^"?\s]+', re.I),
    "zoominfo": re.compile(r'https?://(?:www\.)?zoominfo\.com/c/[^"?\s]+', re.I),
    "yelp": re.compile(r'https?://(?:www\.)?yelp\.com/biz/[^"?\s]+', re.I),
}

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
    elif args[i] == "--offset" and i + 1 < len(args):
        OFFSET = int(args[i + 1]); i += 2
    elif args[i] == "--stale" and i + 1 < len(args):
        STALE_DAYS = int(args[i + 1]); i += 2
    elif args[i] == "--port-base" and i + 1 < len(args):
        PROXY_PORT_BASE = int(args[i + 1]); i += 2
    else:
        i += 1


# ── D1 ───────────────────────────────────────────────────────

def d1_query(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    if result.returncode != 0: return []
    try:
        s = result.stdout.find('[')
        if s < 0: return []
        return json.loads(result.stdout[s:])[0].get("results", [])
    except: return []

def d1_execute(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    return result.returncode == 0

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ── Search ───────────────────────────────────────────────────

def search_platforms(session, company_name, city, state, port):
    """One search to find all platform URLs for a company."""
    query = f'{company_name} {city} {state} glassdoor crunchbase bbb capterra indeed facebook yelp x.com twitter'

    proxy_url = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"

    try:
        resp = session.post(
            "https://www.startpage.com/do/dsearch",
            data={"q": query},
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=30, allow_redirects=True, impersonate="chrome131")
    except Exception as e:
        return {"error": str(e)[:80], "captcha": False, "platforms": {}}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "captcha": False, "platforms": {}}

    html = resp.text
    captcha = "captcha" in html.lower()

    # Extract platform URLs — ONLY from search result blocks, not page navigation
    # Startpage wraps results in elements with class "result"
    # Filter out Startpage's own social links (facebook.com/startpagesearch, twitter.com/startpage)
    STARTPAGE_NOISE = {'startpagesearch', 'startpage', 'startmail'}

    platforms = {}
    for platform, pattern in PLATFORM_PATTERNS.items():
        matches = list(set(pattern.findall(html)))
        if matches:
            clean = []
            for url in matches:
                url = url.rstrip('"\'>')
                url = url.split('#')[0]
                url = url.split('?')[0] if '?' in url else url
                # Filter out Startpage's own links
                url_lower = url.lower()
                if any(noise in url_lower for noise in STARTPAGE_NOISE):
                    continue
                # Filter out generic platform pages (just the homepage)
                path_parts = url.rstrip('/').split('/')
                if platform in ('facebook', 'x_twitter', 'linkedin_company') and len(path_parts) <= 4:
                    continue  # Too short — probably just facebook.com/something generic
                clean.append(url)
            if clean:
                platforms[platform] = clean

    return {"captcha": captcha, "platforms": platforms, "error": None}


# ── Main ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PROCESS 300 — PLATFORM RECON (Section 9)")
    print(f"Limit: {LIMIT or 'ALL'} | Offset: {OFFSET}")
    print("=" * 60)
    sys.stdout.flush()

    if not PROXY_USER or not PROXY_PASS:
        print("ERROR: PROXY_USER and PROXY_PASS required")
        sys.exit(1)

    # Add platform column if not exists
    d1_execute("ALTER TABLE slot_workbench ADD COLUMN recon_platform_urls TEXT DEFAULT NULL")

    # Load companies — one per outreach_id (use CEO slot)
    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""
    offset_clause = f"OFFSET {OFFSET}" if OFFSET else ""

    print("\nLoading companies...")
    sys.stdout.flush()

    stats = {"searched": 0, "captcha": 0, "errors": 0, "platforms_found": 0}
    platform_totals = {p: 0 for p in PLATFORM_PATTERNS}
    processed = 0
    target = LIMIT if LIMIT else 999999

    session = creq.Session(impersonate="chrome131")
    current_port = PROXY_PORT_BASE

    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"platform-recon-{run_date}.jsonl"
    out = open(output_file, "a")

    while processed < target:
        page_limit = min(PAGE_SIZE, target - processed)
        rows = d1_query(f"""
            SELECT outreach_id, company_name, city, state
            FROM slot_workbench
            WHERE slot_type = 'CEO'
            AND (recon_platform_urls IS NULL OR recon_platform_urls = '')
            ORDER BY outreach_id
            LIMIT {page_limit}
        """)

        if not rows:
            print(f"No more companies at {processed}")
            break

        write_batch = []
        for row in rows:
            oid = row["outreach_id"]
            company = row.get("company_name") or ""
            city = row.get("city") or ""
            state = row.get("state") or ""

            if not company:
                continue

            # Port rotation
            if stats["searched"] > 0 and stats["searched"] % 50 == 0:
                current_port += 1
                session = creq.Session(impersonate="chrome131")

            result = search_platforms(session, company, city, state, current_port)
            stats["searched"] += 1

            if result.get("captcha"):
                stats["captcha"] += 1
                time.sleep(5)
                continue

            if result.get("error"):
                stats["errors"] += 1
                time.sleep(SEARCH_DELAY)
                continue

            platforms = result["platforms"]
            if platforms:
                stats["platforms_found"] += 1
                for p, urls in platforms.items():
                    platform_totals[p] += len(urls)

            # Store as JSON
            platform_json = json.dumps(platforms).replace("'", "''")

            # Update ALL 3 slots for this company
            write_batch.append(
                f"UPDATE slot_workbench SET recon_platform_urls = '{platform_json}' "
                f"WHERE outreach_id = {esc(oid)}"
            )

            # Write to JSONL
            out.write(json.dumps({"outreach_id": oid, "company": company, "platforms": platforms}) + "\n")

            if len(write_batch) >= 10:
                d1_execute("; ".join(write_batch))
                write_batch = []

            time.sleep(SEARCH_DELAY + random.uniform(0, 1))

        if write_batch:
            d1_execute("; ".join(write_batch))

        processed += len(rows)
        pct = processed / target * 100 if target < 999999 else 0
        print(f"  [{processed}] searched={stats['searched']} found={stats['platforms_found']} captcha={stats['captcha']}")
        sys.stdout.flush()

        # STOP: CAPTCHA > 10%
        if stats["searched"] > 20 and stats["captcha"] / stats["searched"] > 0.10:
            print(f"\nSTOP: CAPTCHA rate > 10%")
            break

        if len(rows) < page_limit:
            break

    out.close()

    print(f"\n{'='*60}")
    print(f"PLATFORM RECON COMPLETE")
    print(f"{'='*60}")
    print(f"  Companies searched: {stats['searched']}")
    print(f"  With platforms:     {stats['platforms_found']} ({stats['platforms_found']/max(stats['searched'],1)*100:.0f}%)")
    print(f"  CAPTCHAs:          {stats['captcha']}")
    print(f"  Errors:            {stats['errors']}")
    print(f"\n  Platform URL counts:")
    for p, c in sorted(platform_totals.items(), key=lambda x: -x[1]):
        if c > 0:
            print(f"    {p:25s} {c:>5}")
    print(f"  Output: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

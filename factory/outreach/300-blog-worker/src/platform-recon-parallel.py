"""
Process 300 — Platform Recon PARALLEL (24 workers)

Same as platform-recon.py but splits 32K companies across 24 workers.
Each worker gets its own port range.

Usage:
  python3 platform-recon-parallel.py --workers 24
  python3 platform-recon-parallel.py --workers 24 --limit 1000
"""

import json
import re
import sys
import os
import subprocess
import time
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from curl_cffi import requests as creq

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"

NUM_WORKERS = 24
PORT_BASE = 15000
PORT_GAP = 40
LIMIT = 0
SEARCH_DELAY = 3

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

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

STARTPAGE_NOISE = {'startpagesearch', 'startpage', 'startmail'}

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--workers" and i + 1 < len(args):
        NUM_WORKERS = int(args[i + 1]); i += 2
    elif args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
    elif args[i] == "--port-base" and i + 1 < len(args):
        PORT_BASE = int(args[i + 1]); i += 2
    else:
        i += 1


def d1_query(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    if result.returncode != 0: return []
    try:
        s = result.stdout.find('[')
        if s < 0: return []
        return json.loads(result.stdout[s:])[0].get("results", [])
    except: return []

def d1_execute(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    return result.returncode == 0

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def search_worker(worker_id, companies, port_start):
    """One worker searches its chunk of companies."""
    session = creq.Session(impersonate="chrome131")
    port = port_start

    stats = {"searched": 0, "found": 0, "captcha": 0, "errors": 0}
    platform_totals = {p: 0 for p in PLATFORM_PATTERNS}
    batch = []

    for i, company in enumerate(companies):
        oid = company["outreach_id"]
        name = company.get("company_name") or ""
        city = company.get("city") or ""
        state = company.get("state") or ""

        if not name:
            continue

        # Port rotation
        if i > 0 and i % 50 == 0:
            port = port_start + (i // 50)
            session = creq.Session(impersonate="chrome131")

        query = f'{name} {city} {state} glassdoor crunchbase bbb capterra indeed facebook yelp x.com twitter'
        proxy_url = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"

        try:
            resp = session.post(
                "https://www.startpage.com/do/dsearch",
                data={"q": query},
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=30, allow_redirects=True, impersonate="chrome131")
        except:
            stats["errors"] += 1
            time.sleep(SEARCH_DELAY)
            continue

        stats["searched"] += 1

        if resp.status_code != 200:
            stats["errors"] += 1
            time.sleep(SEARCH_DELAY)
            continue

        html = resp.text
        if "captcha" in html.lower():
            stats["captcha"] += 1
            if stats["searched"] > 20 and stats["captcha"] / stats["searched"] > 0.10:
                print(f"  Worker {worker_id}: CAPTCHA > 10%, stopping")
                break
            time.sleep(5)
            continue

        # Extract platform URLs
        platforms = {}
        for platform, pattern in PLATFORM_PATTERNS.items():
            matches = list(set(pattern.findall(html)))
            clean = []
            for url in matches:
                url = url.rstrip('"\'>')
                url = url.split('#')[0]
                url_lower = url.lower()
                if any(noise in url_lower for noise in STARTPAGE_NOISE):
                    continue
                clean.append(url)
            if clean:
                platforms[platform] = clean
                platform_totals[platform] += len(clean)

        if platforms:
            stats["found"] += 1

        platform_json = json.dumps(platforms).replace("'", "''")
        batch.append(
            f"UPDATE slot_workbench SET recon_platform_urls = '{platform_json}' "
            f"WHERE outreach_id = {esc(oid)}"
        )

        if len(batch) >= 10:
            d1_execute("; ".join(batch))
            batch = []

        time.sleep(SEARCH_DELAY + random.uniform(0, 1))

    if batch:
        d1_execute("; ".join(batch))

    return worker_id, stats, platform_totals


def main():
    print("=" * 60)
    print(f"PLATFORM RECON PARALLEL ({NUM_WORKERS} workers)")
    print(f"Limit: {LIMIT or 'ALL'}")
    print("=" * 60)
    sys.stdout.flush()

    if not PROXY_USER or not PROXY_PASS:
        print("ERROR: PROXY_USER and PROXY_PASS required")
        sys.exit(1)

    # Add column if needed
    d1_execute("ALTER TABLE slot_workbench ADD COLUMN recon_platform_urls TEXT DEFAULT NULL")

    # Load companies
    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""
    print("\nLoading companies...")
    sys.stdout.flush()

    rows = d1_query(f"""
        SELECT outreach_id, company_name, city, state
        FROM slot_workbench
        WHERE slot_type = 'CEO'
        AND (recon_platform_urls IS NULL OR recon_platform_urls = '')
        ORDER BY outreach_id
        {limit_clause}
    """)

    total = len(rows)
    print(f"Loaded {total} companies")
    print(f"Splitting across {NUM_WORKERS} workers (~{total // max(NUM_WORKERS,1)} each)")
    sys.stdout.flush()

    if total == 0:
        print("Nothing to search.")
        return

    # Split
    chunk_size = math.ceil(total / NUM_WORKERS)
    chunks = [rows[i:i + chunk_size] for i in range(0, total, chunk_size)]

    start_time = time.time()
    total_stats = {"searched": 0, "found": 0, "captcha": 0, "errors": 0}
    total_platforms = {p: 0 for p in PLATFORM_PATTERNS}

    print(f"\nLaunching {len(chunks)} workers (3s stagger)...")
    sys.stdout.flush()

    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {}
        for idx, chunk in enumerate(chunks):
            port = PORT_BASE + (idx * PORT_GAP)
            future = executor.submit(search_worker, idx, chunk, port)
            futures[future] = idx
            time.sleep(3)

        for future in as_completed(futures):
            wid, stats, pt = future.result()
            for k in total_stats:
                total_stats[k] += stats[k]
            for k in total_platforms:
                total_platforms[k] += pt[k]
            print(f"  Worker {wid} done: searched={stats['searched']} found={stats['found']} captcha={stats['captcha']}")
            sys.stdout.flush()

    elapsed = (time.time() - start_time) / 60
    print(f"\n{'='*60}")
    print(f"PLATFORM RECON COMPLETE ({elapsed:.1f}m)")
    print(f"{'='*60}")
    print(f"  Workers:      {NUM_WORKERS}")
    print(f"  Searched:     {total_stats['searched']}")
    print(f"  With platforms: {total_stats['found']} ({total_stats['found']/max(total_stats['searched'],1)*100:.0f}%)")
    print(f"  CAPTCHAs:     {total_stats['captcha']}")
    print(f"  Errors:       {total_stats['errors']}")
    print(f"\n  Platform counts:")
    for p, c in sorted(total_platforms.items(), key=lambda x: -x[1]):
        if c > 0:
            print(f"    {p:25s} {c:>7,}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

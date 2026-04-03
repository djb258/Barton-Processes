"""
PROC-301 — Fetch Pages PARALLEL (24 workers)

Same as fetch-pages.py but splits work across 24 parallel workers.
Each worker gets its own port range and processes a chunk.

Usage:
  python3 fetch-pages-parallel.py --workers 24
  python3 fetch-pages-parallel.py --workers 24 --limit 1000
"""

import json
import sys
import os
import subprocess
import time
import math
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
PORT_BASE = 14000
PORT_GAP = 40
LIMIT = 0
FETCH_DELAY = 0.5

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
HTML_DIR = OUTPUT_DIR / "html"
HTML_DIR.mkdir(exist_ok=True)

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


def fetch_worker(worker_id, companies, port_start):
    """One worker fetches its chunk of companies."""
    session = creq.Session(impersonate="chrome131")
    proxy_url = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port_start}"

    stats = {"fetched": 0, "failed": 0, "stored": 0}
    batch = []

    for i, company in enumerate(companies):
        oid = company["outreach_id"]
        url = company["about_url"]

        # Rotate port every 50 fetches
        if i > 0 and i % 50 == 0:
            port = port_start + (i // 50)
            proxy_url = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"
            session = creq.Session(impersonate="chrome131")

        html = ""
        status = 0

        # Try direct first
        try:
            resp = session.get(url, timeout=10, allow_redirects=True)
            if resp.status_code == 200 and len(resp.text) > 200:
                html = resp.text
                status = resp.status_code
        except:
            pass

        # Proxy fallback
        if not html and PROXY_USER:
            try:
                resp = session.get(url, proxies={"http": proxy_url, "https": proxy_url},
                                  timeout=15, allow_redirects=True, impersonate="chrome131")
                html = resp.text if resp.status_code == 200 else ""
                status = resp.status_code
            except:
                pass

        if html:
            stats["fetched"] += 1
            html_file = HTML_DIR / f"{oid}.html"
            html_clean = html.replace('\x00', '')
            html_file.write_text(html_clean, encoding='utf-8', errors='replace')

            batch.append(
                f"INSERT OR REPLACE INTO page_raw_html "
                f"(outreach_id, page_url, source, fetch_status, html_length, raw_html, fetched_at, key_built) "
                f"VALUES ({esc(oid)}, {esc(url)}, 'about_url', {status}, {len(html)}, {esc(str(html_file))}, datetime('now'), 0)"
            )
            stats["stored"] += 1
        else:
            stats["failed"] += 1
            batch.append(
                f"INSERT OR REPLACE INTO page_raw_html "
                f"(outreach_id, page_url, source, fetch_status, html_length, raw_html, fetched_at, key_built) "
                f"VALUES ({esc(oid)}, {esc(url)}, 'about_url', {status}, 0, NULL, datetime('now'), 0)"
            )

        if len(batch) >= 10:
            d1_execute("; ".join(batch))
            batch = []

        time.sleep(FETCH_DELAY)

    if batch:
        d1_execute("; ".join(batch))

    return worker_id, stats


def main():
    print("=" * 60)
    print(f"PROC-301 — FETCH PAGES PARALLEL ({NUM_WORKERS} workers)")
    print(f"Limit: {LIMIT or 'ALL'}")
    print("=" * 60)
    sys.stdout.flush()

    # Ensure table exists
    d1_execute("""
        CREATE TABLE IF NOT EXISTS page_raw_html (
            outreach_id TEXT NOT NULL,
            page_url TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'about_url',
            fetch_status INTEGER,
            html_length INTEGER DEFAULT 0,
            raw_html TEXT,
            fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
            key_built INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (outreach_id, page_url)
        )
    """)

    # Load all companies needing fetch
    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""
    print("\nLoading companies...")
    sys.stdout.flush()

    rows = d1_query(f"""
        SELECT DISTINCT outreach_id, about_url
        FROM slot_workbench
        WHERE about_url IS NOT NULL AND about_url != ''
        AND outreach_id NOT IN (SELECT outreach_id FROM page_raw_html WHERE source = 'about_url')
        ORDER BY outreach_id
        {limit_clause}
    """)

    # Dedup
    seen = set()
    companies = []
    for r in rows:
        if r["outreach_id"] not in seen:
            seen.add(r["outreach_id"])
            companies.append(r)

    total = len(companies)
    print(f"Loaded {total} companies to fetch")
    print(f"Splitting across {NUM_WORKERS} workers (~{total // NUM_WORKERS} each)")
    sys.stdout.flush()

    if total == 0:
        print("Nothing to fetch.")
        return

    # Split into chunks
    chunk_size = math.ceil(total / NUM_WORKERS)
    chunks = [companies[i:i + chunk_size] for i in range(0, total, chunk_size)]

    start_time = time.time()
    total_stats = {"fetched": 0, "failed": 0, "stored": 0}

    # Stagger worker launches by 3 seconds
    print(f"\nLaunching {len(chunks)} workers (3s stagger)...")
    sys.stdout.flush()

    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {}
        for idx, chunk in enumerate(chunks):
            port = PORT_BASE + (idx * PORT_GAP)
            future = executor.submit(fetch_worker, idx, chunk, port)
            futures[future] = idx
            time.sleep(3)  # Stagger

        for future in as_completed(futures):
            worker_id, stats = future.result()
            total_stats["fetched"] += stats["fetched"]
            total_stats["failed"] += stats["failed"]
            total_stats["stored"] += stats["stored"]
            print(f"  Worker {worker_id} done: fetched={stats['fetched']} failed={stats['failed']}")
            sys.stdout.flush()

    elapsed = (time.time() - start_time) / 60
    print(f"\n{'='*60}")
    print(f"PARALLEL FETCH COMPLETE ({elapsed:.1f}m)")
    print(f"{'='*60}")
    print(f"  Workers:     {NUM_WORKERS}")
    print(f"  Fetched:     {total_stats['fetched']}")
    print(f"  Failed:      {total_stats['failed']}")
    print(f"  Stored:      {total_stats['stored']}")
    print(f"  Total:       {total}")
    print(f"  Success:     {total_stats['fetched']/max(total,1)*100:.0f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

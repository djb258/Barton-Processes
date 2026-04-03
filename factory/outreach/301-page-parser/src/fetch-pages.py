"""
PROC-301 Step 1 — FETCH ONLY

Goes out and gets every about_url page. Stores raw HTML in D1.
NO parsing. NO classification. NO key building. Just fetch and store.

The Bedrock runs later on the stored HTML.

Usage:
  python3 fetch-pages.py --limit 100
  python3 fetch-pages.py
"""

import json
import sys
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as creq

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"
PORT_BASE = 12000

LIMIT = 0
FETCH_DELAY = 0.5
PAGE_SIZE = 200

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
HTML_DIR = OUTPUT_DIR / "html"
HTML_DIR.mkdir(exist_ok=True)

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
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


def fetch_page(url, port):
    """Fetch page. Direct first, proxy fallback."""
    session = creq.Session(impersonate="chrome131")

    # Direct
    try:
        resp = session.get(url, timeout=10, allow_redirects=True)
        if resp.status_code == 200 and len(resp.text) > 200:
            return resp.text, resp.status_code
    except:
        pass

    # Proxy
    if PROXY_USER and PROXY_PASS:
        proxy_url = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"
        try:
            resp = session.get(url, proxies={"http": proxy_url, "https": proxy_url},
                              timeout=15, allow_redirects=True, impersonate="chrome131")
            return resp.text if resp.status_code == 200 else "", resp.status_code
        except:
            pass

    return "", 0


def main():
    print("=" * 60)
    print("PROC-301 — FETCH PAGES (Source 7: about_url)")
    print("Fetch and store raw HTML. No parsing. No classification.")
    print(f"Limit: {LIMIT or 'ALL'}")
    print("=" * 60)
    sys.stdout.flush()

    # First, make sure the storage table exists
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
    d1_execute("CREATE INDEX IF NOT EXISTS idx_page_raw_source ON page_raw_html(source)")
    d1_execute("CREATE INDEX IF NOT EXISTS idx_page_raw_key ON page_raw_html(key_built)")

    # Load about_urls not yet fetched
    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""
    print("\nLoading about_urls...")
    sys.stdout.flush()

    stats = {"fetched": 0, "failed": 0, "skipped": 0, "stored": 0}
    processed = 0
    total_target = LIMIT if LIMIT else 999999

    while processed < total_target:
        page_limit = min(PAGE_SIZE, total_target - processed)
        rows = d1_query(f"""
            SELECT DISTINCT sw.outreach_id, sw.about_url
            FROM slot_workbench sw
            WHERE sw.about_url IS NOT NULL AND sw.about_url != ''
            AND sw.outreach_id NOT IN (
                SELECT outreach_id FROM page_raw_html WHERE source = 'about_url'
            )
            ORDER BY sw.outreach_id
            LIMIT {page_limit}
        """)

        if not rows:
            print(f"No more URLs to fetch at {processed}")
            break

        for row in rows:
            oid = row["outreach_id"]
            url = row["about_url"]
            port = PORT_BASE + (processed % 100)

            html, status = fetch_page(url, port)

            if html:
                stats["fetched"] += 1
                # Store HTML to local file — too large/messy for D1 CLI
                html_file = HTML_DIR / f"{oid}.html"
                html_clean = html.replace('\x00', '')  # strip null bytes
                html_file.write_text(html_clean, encoding='utf-8', errors='replace')

                ok = d1_execute(f"""
                    INSERT OR REPLACE INTO page_raw_html
                    (outreach_id, page_url, source, fetch_status, html_length, raw_html, fetched_at, key_built)
                    VALUES ({esc(oid)}, {esc(url)}, 'about_url', {status}, {len(html)}, {esc(str(html_file))}, datetime('now'), 0)
                """)
                if ok:
                    stats["stored"] += 1
                else:
                    stats["failed"] += 1
            else:
                stats["failed"] += 1
                d1_execute(f"""
                    INSERT OR REPLACE INTO page_raw_html
                    (outreach_id, page_url, source, fetch_status, html_length, raw_html, fetched_at, key_built)
                    VALUES ({esc(oid)}, {esc(url)}, 'about_url', {status}, 0, NULL, datetime('now'), 0)
                """)

            processed += 1
            if processed % 50 == 0:
                pct = processed / total_target * 100 if total_target < 999999 else 0
                print(f"  [{processed}] fetched={stats['fetched']} failed={stats['failed']} stored={stats['stored']}")
                sys.stdout.flush()

            time.sleep(FETCH_DELAY)

        if len(rows) < page_limit:
            break

    print(f"\n{'='*60}")
    print(f"FETCH COMPLETE")
    print(f"{'='*60}")
    print(f"  Pages fetched:  {stats['fetched']}")
    print(f"  Fetch failed:   {stats['failed']}")
    print(f"  Stored in D1:   {stats['stored']}")
    print(f"  Total processed: {processed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

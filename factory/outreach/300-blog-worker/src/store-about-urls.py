#!/usr/bin/env python3
"""
store-about-urls.py
Reads Process 300 company-recon JSONL output, picks the best about/leadership URL
per company, and updates slot_workbench in D1 via wrangler.

URL selection priority:
  1. On-domain URL containing leadership/team/staff/executive keywords
  2. On-domain URL containing about/contact
  3. On-domain URL (any)
  4. Off-domain URL containing leadership/team/staff/executive keywords
  5. Off-domain URL containing about/contact
  6. First leadership_url as fallback
"""

import json
import glob
import subprocess
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

JSONL_PATTERN = "/Users/employeeai/Documents/Barton-Processes/factory/outreach/300-blog-worker/src/output/company-recon-*-w*.jsonl"
WRANGLER_CWD = "/Users/employeeai/Documents/imo-creator-v2-20260317/workers/lcs-hub"
BATCH_SIZE = 30

LEADERSHIP_KEYWORDS = ["leadership", "team", "our-team", "ourteam", "staff", "executive", "executives", "management", "people", "who-we-are"]
ABOUT_KEYWORDS = ["about", "contact"]


def is_on_domain(url: str, domain: str) -> bool:
    """Check if URL is on the company's own domain."""
    if not domain:
        return False
    try:
        host = urlparse(url).hostname or ""
        # Strip www. from both for comparison
        host_clean = host.lower().lstrip("www.")
        domain_clean = domain.lower().lstrip("www.")
        return host_clean == domain_clean or host_clean.endswith("." + domain_clean)
    except Exception:
        return False


def url_contains_keywords(url: str, keywords: list) -> bool:
    """Check if URL path contains any of the given keywords."""
    lower = url.lower()
    return any(kw in lower for kw in keywords)


def pick_best_url(leadership_urls: list, domain: str) -> str | None:
    """Pick the best about/leadership URL from the list."""
    if not leadership_urls:
        return None

    # Score each URL: (on_domain, keyword_tier)
    # on_domain: True > False
    # keyword_tier: 2 = leadership keywords, 1 = about keywords, 0 = neither
    def score(url):
        on_domain = is_on_domain(url, domain)
        if url_contains_keywords(url, LEADERSHIP_KEYWORDS):
            kw_tier = 2
        elif url_contains_keywords(url, ABOUT_KEYWORDS):
            kw_tier = 1
        else:
            kw_tier = 0
        return (on_domain, kw_tier)

    best = max(leadership_urls, key=score)
    return best


def sql_escape(s: str) -> str:
    """Escape single quotes for SQL."""
    return s.replace("'", "''")


def run_batch(statements: list[str], batch_num: int) -> int:
    """Run a batch of UPDATE statements via wrangler. Returns count of successful updates."""
    combined = " ".join(statements)
    cmd = [
        "npx", "wrangler", "d1", "execute", "svg-d1-outreach-ops",
        "--remote", "--command", combined, "--json"
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=WRANGLER_CWD,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            print(f"  [WARN] Batch {batch_num} wrangler error: {result.stderr[:300]}", flush=True)
            return 0
        return len(statements)
    except subprocess.TimeoutExpired:
        print(f"  [WARN] Batch {batch_num} timed out", flush=True)
        return 0
    except Exception as e:
        print(f"  [WARN] Batch {batch_num} exception: {e}", flush=True)
        return 0


def main():
    files = sorted(glob.glob(JSONL_PATTERN))
    print(f"Found {len(files)} JSONL files", flush=True)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates = []  # list of (outreach_id, url) tuples
    total_records = 0
    records_with_urls = 0
    skipped_no_urls = 0

    # Pass 1: read all JSONL, pick best URL per record
    for fpath in files:
        with open(fpath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_records += 1
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                oid = rec.get("outreach_id")
                leadership_urls = rec.get("leadership_urls") or []
                domain = rec.get("domain", "")
                status = rec.get("status", "")

                if not oid or not leadership_urls or status != "captured":
                    skipped_no_urls += 1
                    continue

                best = pick_best_url(leadership_urls, domain)
                if best:
                    records_with_urls += 1
                    updates.append((oid, best))

                if total_records % 5000 == 0:
                    print(f"  Read {total_records} records so far...", flush=True)

    print(f"\nTotal records read: {total_records}", flush=True)
    print(f"Records with leadership URLs (captured): {records_with_urls}", flush=True)
    print(f"Skipped (no URLs or not captured): {skipped_no_urls}", flush=True)
    print(f"Updates to attempt: {len(updates)}", flush=True)

    # Pass 2: batch UPDATE via wrangler
    batch = []
    total_updated = 0
    for i, (oid, url) in enumerate(updates):
        safe_url = sql_escape(url)
        safe_oid = sql_escape(oid)
        stmt = (
            f"UPDATE slot_workbench SET about_url = '{safe_url}', "
            f"last_recon_at = '{now_iso}' "
            f"WHERE outreach_id = '{safe_oid}' "
            f"AND (about_url IS NULL OR about_url = '');"
        )
        batch.append(stmt)

        if len(batch) >= BATCH_SIZE:
            batch_num = (i // BATCH_SIZE) + 1
            ok = run_batch(batch, batch_num)
            total_updated += ok
            batch = []

        if (i + 1) % 500 == 0:
            print(f"  Progress: {i + 1}/{len(updates)} sent to D1 ({total_updated} batch-sent so far)", flush=True)

    # Flush remaining
    if batch:
        batch_num = (len(updates) // BATCH_SIZE) + 1
        ok = run_batch(batch, batch_num)
        total_updated += ok

    print(f"\n=== DONE ===", flush=True)
    print(f"Total UPDATE statements sent: {total_updated}", flush=True)
    print(f"(Only rows where about_url IS NULL or empty were updated)", flush=True)

    # Query the after count
    print(f"\nQuerying about_url fill count...", flush=True)
    cmd = [
        "npx", "wrangler", "d1", "execute", "svg-d1-outreach-ops",
        "--remote", "--command",
        "SELECT COUNT(*) as filled FROM slot_workbench WHERE about_url IS NOT NULL AND about_url != '';",
        "--json"
    ]
    try:
        result = subprocess.run(cmd, cwd=WRANGLER_CWD, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # wrangler --json returns array of result sets
            for rs in data:
                results = rs.get("results", [])
                if results:
                    print(f"about_url filled: {results[0].get('filled', '?')} slots", flush=True)
        else:
            print(f"Query failed: {result.stderr[:200]}", flush=True)
    except Exception as e:
        print(f"Query exception: {e}", flush=True)


if __name__ == "__main__":
    main()

"""
Source 8 — URL Classifier

Reads recon_result_urls from slot_workbench.
Classifies each URL by type. No fetching. Just reading what we have.

Categories:
  linkedin_profile  — linkedin.com/in/{slug} — HIGH value
  company_page      — company's own domain, /about /team /leadership — HIGH value
  linkedin_company  — linkedin.com/company/ — LOW value
  directory         — zoominfo, crunchbase, bbb, glassdoor — MEDIUM
  job_site          — indeed, glassdoor/jobs — LOW
  government        — .gov — LOW
  academic          — .edu, academic journals — LOW
  social            — facebook, twitter, instagram — LOW
  pdf               — .pdf — LOW
  noise             — everything else — SKIP

Usage:
  python3 classify-urls.py --limit 100
  python3 classify-urls.py
"""

import json
import re
import sys
import os
import subprocess
from urllib.parse import urlparse
from collections import Counter

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

LIMIT = 0
PAGE_SIZE = 500

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
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


def classify_url(url, company_domain=""):
    """Classify a single URL into a category."""
    lower = url.lower()
    parsed = urlparse(lower)
    host = parsed.hostname or ""
    path = parsed.path

    # LinkedIn profile
    if "linkedin.com/in/" in lower:
        return "linkedin_profile"

    # LinkedIn company
    if "linkedin.com/company/" in lower:
        return "linkedin_company"

    # PDF
    if path.endswith(".pdf"):
        return "pdf"

    # Government
    if host.endswith(".gov"):
        return "government"

    # Academic
    if host.endswith(".edu") or any(x in host for x in ["academic", "journal", "scholar", "research"]):
        return "academic"

    # Social media
    if any(x in host for x in ["facebook.com", "twitter.com", "instagram.com", "youtube.com", "tiktok.com"]):
        return "social"

    # Job sites
    if any(x in host for x in ["indeed.com", "ziprecruiter.com", "monster.com", "careerbuilder.com"]):
        return "job_site"
    if "glassdoor.com" in host and "/job" in path:
        return "job_site"

    # Directories
    if any(x in host for x in ["zoominfo.com", "crunchbase.com", "bbb.org", "glassdoor.com",
                                 "dnb.com", "bloomberg.com", "owler.com", "manta.com",
                                 "yellowpages.com", "yelp.com", "mapquest.com"]):
        return "directory"

    # Company's own page (domain matches)
    if company_domain:
        co_domain = company_domain.lower().replace("www.", "")
        if co_domain in host:
            # Check if it's a team/about/leadership page
            if any(w in path for w in ["/team", "/about", "/leadership", "/staff",
                                        "/people", "/our-team", "/meet-", "/management",
                                        "/board", "/executives", "/who-we-are"]):
                return "company_page"
            return "company_other"

    # Generic company-looking pages
    if any(w in path for w in ["/team", "/about", "/leadership", "/staff", "/our-team"]):
        return "company_page"

    return "noise"


def main():
    print("=" * 60)
    print("SOURCE 8 — URL CLASSIFIER")
    print("Categorize recon_result_urls by type. No fetching.")
    print(f"Limit: {LIMIT or 'ALL'}")
    print("=" * 60)
    sys.stdout.flush()

    totals = Counter()
    url_count = 0
    slot_count = 0
    processed = 0
    target = LIMIT if LIMIT else 999999

    while processed < target:
        page_limit = min(PAGE_SIZE, target - processed)
        rows = d1_query(f"""
            SELECT outreach_id, domain, recon_result_urls
            FROM slot_workbench
            WHERE recon_result_urls IS NOT NULL AND recon_result_urls != '[]'
            AND slot_type = 'CEO'
            ORDER BY outreach_id
            LIMIT {page_limit} OFFSET {processed}
        """)

        if not rows: break

        for row in rows:
            domain = row.get("domain") or ""
            try:
                urls = json.loads(row["recon_result_urls"])
            except:
                continue

            if not isinstance(urls, list):
                continue

            slot_count += 1
            for url in urls:
                if isinstance(url, str) and url.startswith("http"):
                    category = classify_url(url, company_domain=domain)
                    totals[category] += 1
                    url_count += 1

        processed += len(rows)
        if processed % 1000 == 0:
            print(f"  [{processed}] {url_count} URLs classified")
            sys.stdout.flush()

        if len(rows) < page_limit:
            break

    print(f"\n{'='*60}")
    print(f"URL CLASSIFICATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Companies scanned: {slot_count}")
    print(f"  Total URLs:        {url_count}")
    print(f"\n  Category breakdown:")
    for cat, cnt in totals.most_common():
        pct = cnt / max(url_count, 1) * 100
        value = "HIGH" if cat in ("linkedin_profile", "company_page") else \
                "MEDIUM" if cat in ("directory", "company_other") else "LOW"
        print(f"    {cat:25s} {cnt:>7,} ({pct:5.1f}%) [{value}]")

    high = totals.get("linkedin_profile", 0) + totals.get("company_page", 0)
    print(f"\n  HIGH value URLs:   {high:>7,} ({high/max(url_count,1)*100:.1f}%) — worth fetching")
    print(f"  Everything else:   {url_count - high:>7,} ({(url_count-high)/max(url_count,1)*100:.1f}%) — skip or low priority")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

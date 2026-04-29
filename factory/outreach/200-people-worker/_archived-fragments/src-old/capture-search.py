"""
Process 200 — Capture Search Results (Raw)

Searches Startpage for each empty slot and captures EVERYTHING:
- All URLs found
- All text snippets
- All LinkedIn URLs
- All email addresses found in results
- Raw result HTML snippets

Does NOT parse names or make decisions. Just captures.
Parsing happens in a separate step on the stored data.

The search is expensive (proxy + rate limiting).
The parsing is free (re-run anytime on stored data).

Usage:
  python3 src/capture-search.py --limit 10
  python3 src/capture-search.py --limit 500 --slot-type CEO
  python3 src/capture-search.py --resume
  python3 src/capture-search.py  # all empty slots

Env vars: D1_DB, D1_SPINE, PROXY_USER, PROXY_PASS
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
SLOT_TYPE = None
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
D1_SPINE = os.environ.get("D1_SPINE", "svg-d1-spine")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT_BASE = 10001  # Starting port — rotate every QUERIES_PER_IP queries
QUERIES_PER_IP = 50  # Get a fresh IP every 50 queries
SEARCH_DELAY = 3

QUERY_TEMPLATES = {
    "CEO": "who is the CEO of {company}",
    "CFO": "who is the CFO of {company}",
    "HR": "{company} HR director {city} {state}",
}

# ── Parse args ───────────────────────────────────────────────

args = sys.argv[1:]
resume = False
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1])
        i += 2
    elif args[i] == "--slot-type" and i + 1 < len(args):
        SLOT_TYPE = args[i + 1].upper()
        i += 2
    elif args[i] == "--resume":
        resume = True
        i += 1
    else:
        i += 1


# ── D1 Access ────────────────────────────────────────────────

def d1_query(sql, db=None):
    db = db or D1_DB
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", db, "--remote", "--command", sql, "--json"],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("results", [])
    except json.JSONDecodeError:
        stdout = result.stdout
        start = stdout.find('[')
        if start >= 0:
            try:
                data = json.loads(stdout[start:])
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("results", [])
            except:
                pass
    return []


def get_proxy_url(query_num=0):
    """Rotate sticky port every QUERIES_PER_IP queries to get a fresh IP."""
    port = PROXY_PORT_BASE + (query_num // QUERIES_PER_IP)
    return f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"


# ── Extract everything from search results ───────────────────

def extract_all(html):
    """Extract every useful piece of data from search result HTML."""

    # All LinkedIn URLs
    linkedin_urls = list(set(re.findall(
        r'https://(?:www\.)?linkedin\.com/in/[^"?\s<>]+',
        html, re.IGNORECASE
    )))

    # All email addresses
    emails = list(set(re.findall(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        html
    )))
    # Filter junk emails
    emails = [e for e in emails if not any(x in e.lower() for x in
        ['startpage', 'sentry', 'webpack', 'css', 'javascript', 'example.com', 'email.com'])]

    # All result snippets (text between tags, 10+ chars)
    snippets = []
    for m in re.findall(r'>([^<]{10,300})<', html):
        text = m.strip()
        if text and not text.startswith('{') and not text.startswith('function') and not text.startswith('.css'):
            snippets.append(text)

    # Date extraction — when were these results published?
    dates_found = []
    # "Month DD, YYYY" or "Month YYYY"
    for d in re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4}', html):
        dates_found.append(d)
    for d in re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}', html):
        if d not in dates_found:
            dates_found.append(d)
    # YYYY-MM-DD
    for d in re.findall(r'20[12]\d-\d{2}-\d{2}', html):
        dates_found.append(d)
    # Dates in URLs: /2024/ /2025/ /2026/
    url_years = re.findall(r'/(?:202[3-6])/', html)
    dates_found = list(set(dates_found))

    # Leadership/team page URLs — strong recency signal
    leadership_urls = [u for u in re.findall(r'href="(https?://[^"]+)"', html)
                       if any(kw in u.lower() for kw in
                              ['leadership', 'team', 'about', 'executive', 'management', 'our-team', 'staff'])
                       and 'startpage' not in u.lower()
                       and 'linkedin' not in u.lower()]

    # All "Name - Title" patterns (LinkedIn style)
    name_title_patterns = re.findall(
        r'>([A-Z][a-z]+(?:\s[A-Z]\.?\s*)?(?:\s[A-Z][a-z]+){1,3})\s*[-–]\s*([^<]{3,80})',
        html
    )

    # All URLs from results
    result_urls = re.findall(r'href="(https?://[^"]+)"', html)
    # Filter to unique, non-startpage URLs
    result_urls = list(set(u for u in result_urls if 'startpage' not in u.lower()))

    return {
        "linkedin_urls": linkedin_urls,
        "emails": emails,
        "snippets": snippets[:20],  # Cap at 20 snippets
        "name_title_patterns": [{"name": n, "context": t} for n, t in name_title_patterns[:10]],
        "result_urls": result_urls[:10],
        "result_count": len(re.findall(r'class="result', html)),
        "dates_found": dates_found[:10],
        "url_years": list(set(url_years)),
        "leadership_urls": list(set(leadership_urls))[:5],
        "has_recent_date": any(y in str(dates_found) for y in ['2025', '2026']),
        "has_leadership_page": len(leadership_urls) > 0,
    }


# ── Main ─────────────────────────────────────────────────────

def main():
    print("Process 200 — Capture Search Results (Raw)")
    print(f"Limit: {LIMIT or 'ALL'} | Slot type: {SLOT_TYPE or 'ALL'} | Resume: {resume}")

    if not PROXY_USER or not PROXY_PASS:
        print("ERROR: PROXY_USER and PROXY_PASS required")
        sys.exit(1)

    print()

    # Get empty slots
    slot_filter = f"AND cs.slot_type = '{SLOT_TYPE}'" if SLOT_TYPE else ""
    sql = (
        f"SELECT cs.slot_id, cs.outreach_id, cs.company_unique_id, cs.slot_type, "
        f"ct.city, ct.state "
        f"FROM people_company_slot cs "
        f"JOIN outreach_company_target ct ON cs.outreach_id = ct.outreach_id "
        f"WHERE cs.is_filled = 0 {slot_filter} "
        f"ORDER BY cs.slot_type"
    )
    if LIMIT:
        sql += f" LIMIT {LIMIT}"

    print("Loading empty slots from D1...")
    slots = d1_query(sql)
    if not slots:
        print("No empty slots.")
        return
    print(f"{len(slots)} empty slots")

    # Bulk load ALL company names in ONE query
    print("Loading all company names from spine (one query)...")
    all_companies = d1_query(
        "SELECT outreach_id, canonical_name, company_name, company_domain FROM cl_company_identity",
        db=D1_SPINE,
    )
    company_cache = {}
    for row in all_companies:
        oid = row.get("outreach_id")
        if oid:
            company_cache[oid] = {
                "name": row.get("canonical_name") or row.get("company_name") or "",
                "domain": row.get("company_domain") or "",
            }
    print(f"Loaded {len(company_cache)} companies")

    # Also load domains from outreach_outreach
    print("Loading domains...")
    all_domains = d1_query("SELECT outreach_id, domain FROM outreach_outreach")
    domain_cache = {}
    for row in all_domains:
        oid = row.get("outreach_id")
        if oid:
            domain_cache[oid] = row.get("domain", "")
    print(f"Loaded {len(domain_cache)} domains")
    print()

    # Resume support
    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"capture-{run_date}.jsonl"

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

    remaining = [s for s in slots if s["slot_id"] not in already_done]
    print(f"{len(remaining)} remaining")
    print()

    out = open(output_file, "a")

    success = 0
    captcha_count = 0
    errors = 0
    start = time.time()
    session = None
    current_port = None

    for idx, slot in enumerate(remaining):
        # Rotate proxy + session every QUERIES_PER_IP queries
        proxy_url = get_proxy_url(idx)
        new_port = PROXY_PORT_BASE + (idx // QUERIES_PER_IP)
        if new_port != current_port:
            if session:
                session.close()
            session = creq.Session(impersonate="chrome131")
            current_port = new_port
            if idx > 0:
                print(f"  [Rotating to port {new_port} — fresh IP]")
        oid = slot["outreach_id"]
        company = company_cache.get(oid, {})
        company_name = company.get("name", "")
        company_domain = company.get("domain", "") or domain_cache.get(oid, "")
        city = slot.get("city", "") or ""
        state = slot.get("state", "") or ""
        slot_type = slot["slot_type"]

        if not company_name:
            record = {
                "slot_id": slot["slot_id"],
                "outreach_id": oid,
                "slot_type": slot_type,
                "company_name": "",
                "company_domain": company_domain,
                "status": "no_company_name",
            }
            out.write(json.dumps(record) + "\n")
            out.flush()
            errors += 1
            continue

        # Build natural language query
        template = QUERY_TEMPLATES.get(slot_type, QUERY_TEMPLATES["CEO"])
        query = template.format(company=company_name, city=city, state=state)

        # Search
        try:
            resp = session.post(
                "https://www.startpage.com/do/dsearch",
                data={"q": query},
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=30,
                allow_redirects=True,
                impersonate="chrome131",
            )

            captcha = "captcha" in resp.text.lower()

            if captcha:
                captcha_count += 1
                record = {
                    "slot_id": slot["slot_id"],
                    "outreach_id": oid,
                    "slot_type": slot_type,
                    "company_name": company_name,
                    "company_domain": company_domain,
                    "query": query,
                    "status": "captcha",
                }
            else:
                # Extract EVERYTHING
                extracted = extract_all(resp.text)
                record = {
                    "slot_id": slot["slot_id"],
                    "outreach_id": oid,
                    "company_unique_id": slot["company_unique_id"],
                    "slot_type": slot_type,
                    "company_name": company_name,
                    "company_domain": company_domain,
                    "city": city,
                    "state": state,
                    "query": query,
                    "status": "captured",
                    "http_status": resp.status_code,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                    **extracted,
                }
                success += 1

        except Exception as e:
            record = {
                "slot_id": slot["slot_id"],
                "outreach_id": oid,
                "slot_type": slot_type,
                "company_name": company_name,
                "company_domain": company_domain,
                "query": query,
                "status": "error",
                "error": str(e)[:100],
            }
            errors += 1

        out.write(json.dumps(record) + "\n")
        out.flush()

        if (idx + 1) % 25 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(
                f"  [{idx+1}/{len(remaining)}] "
                f"OK:{success} CAPTCHA:{captcha_count} Err:{errors} | {rate:.0f}/hr"
            )

        if idx < len(remaining) - 1:
            time.sleep(SEARCH_DELAY + random.uniform(0, 1.5))

    out.close()
    elapsed = (time.time() - start) / 60
    print(
        f"\nDone in {elapsed:.1f}m | "
        f"OK:{success} CAPTCHA:{captcha_count} Err:{errors}"
    )


if __name__ == "__main__":
    main()

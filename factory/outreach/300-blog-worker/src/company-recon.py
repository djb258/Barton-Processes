"""
Process 300 — Company Reconnaissance (Startpage)

Reads from slot_workbench in D1. One query per company.
Captures EVERYTHING — leadership pages, LinkedIn, emails,
names, titles, dates, snippets. Parse later.

Writes back to D1: last_recon_at timestamp + raw results to JSONL.
After run, PUSH results to Neon and REFRESH materialized view.

Query built from ALL constants in the workbench:
  "{company_name} {city} {state} leadership team contact"

Usage:
  python3 src/company-recon.py --limit 20
  python3 src/company-recon.py --limit 100 --resume
  python3 src/company-recon.py --stale 90    # only companies not searched in 90 days
  python3 src/company-recon.py               # all companies

Env vars: D1_DB, PROXY_USER, PROXY_PASS
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
STALE_DAYS = 0  # 0 = all companies, >0 = only companies not searched in N days
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT_BASE = 10040  # Fresh range — don't reuse burned ports
QUERIES_PER_IP = 50
SEARCH_DELAY = 3

# ── Parse args ───────────────────────────────────────────────

args = sys.argv[1:]
resume = False
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1])
        i += 2
    elif args[i] == "--offset" and i + 1 < len(args):
        OFFSET = int(args[i + 1])
        i += 2
    elif args[i] == "--stale" and i + 1 < len(args):
        STALE_DAYS = int(args[i + 1])
        i += 2
    elif args[i] == "--port-base" and i + 1 < len(args):
        PROXY_PORT_BASE = int(args[i + 1])
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


def d1_execute(sql, db=None):
    """Execute a write statement against D1."""
    db = db or D1_DB
    subprocess.run(
        ["npx", "wrangler", "d1", "execute", db, "--remote", "--command", sql, "--json"],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )


def get_proxy_url(query_num=0):
    port = PROXY_PORT_BASE + (query_num // QUERIES_PER_IP)
    return f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"


# ── Extract everything from search results ───────────────────

def extract_all(html, company_name=""):
    """Extract every useful piece of data from search result HTML."""
    # Build company name words for filtering (so "Seven Days In-Home Care" doesn't parse as a person)
    co_words = set(w.lower() for w in re.split(r'[\s\-&,\.]+', company_name) if len(w) > 2)

    # LinkedIn URLs — both company and personal
    linkedin_company = list(set(re.findall(
        r'https://(?:www\.)?linkedin\.com/company/[^"?\s<>\\]+',
        html, re.IGNORECASE
    )))
    linkedin_people = list(set(re.findall(
        r'https://(?:www\.)?linkedin\.com/in/[^"?\s<>\\]+',
        html, re.IGNORECASE
    )))

    # All email addresses
    emails = list(set(re.findall(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html
    )))
    emails = [e for e in emails if not any(x in e.lower() for x in
        ['startpage', 'sentry', 'webpack', 'css', 'javascript', 'example.com'])]

    # Leadership/team/about page URLs
    leadership_urls = list(set(u for u in re.findall(r'href="(https?://[^"]+)"', html)
        if any(kw in u.lower() for kw in
            ['leadership', 'team', 'our-team', 'about', 'staff', 'executive',
             'management', 'board', 'people', 'who-we-are', 'contact'])
        and 'startpage' not in u.lower()
        and 'linkedin' not in u.lower()
        and 'wikipedia' not in u.lower()
    ))

    # Name + title patterns
    name_title_patterns = re.findall(
        r'>([A-Z][a-z]+(?:\s[A-Z]\.?\s*)?(?:\s[A-Z][a-z]+){1,3})\s*[-–]\s*([^<]{3,80})',
        html
    )
    # Filter noise: page headings, nav items, company names parsed as people
    bad_words = ['about', 'contact', 'our', 'the', 'read', 'home', 'privacy',
             'terms', 'cookie', 'skip', 'sign', 'view', 'search',
             'global', 'offices', 'information', 'services', 'solutions',
             'group', 'company', 'inc', 'llc', 'corp', 'agency', 'center']
    name_title_patterns = [(n, t) for n, t in name_title_patterns
        if not any(bad in n.lower() for bad in bad_words)
        # Reject if >50% of name words match company name words
        and (not co_words or
             sum(1 for w in n.lower().split() if w in co_words) / max(len(n.split()), 1) < 0.5)]

    # All result snippets
    snippets = []
    for m in re.findall(r'>([^<]{15,300})<', html):
        text = m.strip()
        if text and not text.startswith('{') and not text.startswith('function') \
                and not text.startswith('.css') and not text.startswith('@media') \
                and not text.startswith('#') and not text.startswith('*'):
            snippets.append(text)

    # Dates
    dates_found = list(set(
        re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4}', html) +
        re.findall(r'20[12]\d-\d{2}-\d{2}', html)
    ))

    # All result URLs
    result_urls = list(set(u for u in re.findall(r'href="(https?://[^"]+)"', html)
        if 'startpage' not in u.lower() and 'javascript' not in u.lower()))

    return {
        "linkedin_company": linkedin_company[:5],
        "linkedin_people": linkedin_people[:10],
        "emails": emails[:10],
        "leadership_urls": leadership_urls[:10],
        "name_title_patterns": [{"name": n, "context": t} for n, t in name_title_patterns[:15]],
        "snippets": snippets[:15],
        "dates_found": dates_found[:10],
        "result_urls": result_urls[:15],
        "result_count": len(re.findall(r'class="result', html)),
        "has_recent_date": any(y in str(dates_found) for y in ['2025', '2026']),
        "has_leadership_page": len(leadership_urls) > 0,
        "has_company_linkedin": len(linkedin_company) > 0,
    }


# ── Main ─────────────────────────────────────────────────────

def main():
    worker_id = f"w{OFFSET // max(LIMIT, 1)}" if LIMIT else "all"
    print(f"Process 300 — Company Reconnaissance (Startpage) [{worker_id}]")
    print(f"Limit: {LIMIT or 'ALL'} | Offset: {OFFSET} | Port: {PROXY_PORT_BASE} | Resume: {resume}")

    if not PROXY_USER or not PROXY_PASS:
        print("ERROR: PROXY_USER and PROXY_PASS required")
        sys.exit(1)

    print()

    # ── Read from slot_workbench — one row per company ─────────
    # Deduplicate: workbench has 3 rows per company (one per slot).
    # We only need one search per company.
    stale_filter = ""
    if STALE_DAYS > 0:
        stale_filter = f"AND (last_recon_at IS NULL OR last_recon_at < datetime('now', '-{STALE_DAYS} days'))"

    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""
    offset_clause = f"OFFSET {OFFSET}" if OFFSET else ""

    print("Loading companies from slot_workbench...")
    companies = d1_query(f"""
        SELECT DISTINCT outreach_id,
            company_name, canonical_name, domain, company_domain,
            city, state, postal_code, industry, employees,
            ein, filing_present, carrier, broker_or_advisor, funding_type,
            renewal_month, about_url, hunter_email_pattern,
            service_agents
        FROM slot_workbench
        WHERE domain IS NOT NULL AND city IS NOT NULL
        {stale_filter}
        ORDER BY outreach_id
        {limit_clause} {offset_clause}
    """)
    if not companies:
        print("No companies to search.")
        return

    print(f"{len(companies)} companies to search")
    print()

    # Resume support
    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"company-recon-{run_date}-{worker_id}.jsonl"

    already_done = set()
    if resume and output_file.exists():
        with open(output_file) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    already_done.add(rec.get("outreach_id", ""))
                except:
                    pass
        print(f"Resuming: {len(already_done)} already done")

    remaining = [c for c in companies if c["outreach_id"] not in already_done]
    print(f"{len(remaining)} remaining")
    print()

    out = open(output_file, "a")
    session = None
    current_port = None

    success = 0
    captcha_count = 0
    errors = 0
    start = time.time()
    now_ts = datetime.now(timezone.utc).isoformat()

    # Batch up outreach_ids for timestamp update (every 50)
    recon_batch = []

    for idx, co in enumerate(remaining):
        # Rotate proxy
        proxy_url = get_proxy_url(idx)
        new_port = PROXY_PORT_BASE + (idx // QUERIES_PER_IP)
        if new_port != current_port:
            if session:
                session.close()
            session = creq.Session(impersonate="chrome131")
            current_port = new_port
            if idx > 0:
                print(f"  [Rotating to port {new_port}]")

        oid = co["outreach_id"]
        company_name = co.get("canonical_name") or co.get("company_name") or co.get("domain", "")
        city = co.get("city", "") or ""
        state = co.get("state", "") or ""
        industry = co.get("industry", "") or ""
        domain = co.get("domain", "") or ""
        ein = co.get("ein", "") or ""

        # Build natural language query from ALL constants
        # The more context, the better the results, the less CAPTCHA
        query = f"{company_name} {city} {state} leadership team contact linkedin"

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
                    "outreach_id": oid,
                    "company_name": company_name,
                    "domain": domain,
                    "query": query,
                    "status": "captcha",
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                }
            else:
                extracted = extract_all(resp.text, company_name=company_name)
                record = {
                    "outreach_id": oid,
                    "company_name": company_name,
                    "domain": domain,
                    "city": city,
                    "state": state,
                    "industry": industry,
                    "ein": ein,
                    "carrier": co.get("carrier"),
                    "broker": co.get("broker_or_advisor"),
                    "funding_type": co.get("funding_type"),
                    "renewal_month": co.get("renewal_month"),
                    "existing_about_url": co.get("about_url"),
                    "hunter_email_pattern": co.get("hunter_email_pattern"),
                    "query": query,
                    "status": "captured",
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                    **extracted,
                }
                success += 1
                recon_batch.append(oid)

        except Exception as e:
            record = {
                "outreach_id": oid,
                "company_name": company_name,
                "domain": domain,
                "query": query,
                "status": "error",
                "error": str(e)[:100],
            }
            errors += 1

        out.write(json.dumps(record) + "\n")
        out.flush()

        # Write last_recon_at back to D1 every 50 companies
        if len(recon_batch) >= 50:
            oid_list = "','".join(recon_batch)
            d1_execute(
                f"UPDATE slot_workbench SET last_recon_at = '{now_ts}' "
                f"WHERE outreach_id IN ('{oid_list}')"
            )
            recon_batch = []

        if (idx + 1) % 10 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(
                f"  [{idx+1}/{len(remaining)}] "
                f"OK:{success} CAPTCHA:{captcha_count} Err:{errors} | {rate:.0f}/hr"
            )

        if idx < len(remaining) - 1:
            time.sleep(SEARCH_DELAY + random.uniform(0, 1.5))

    # Flush remaining timestamp updates
    if recon_batch:
        oid_list = "','".join(recon_batch)
        d1_execute(
            f"UPDATE slot_workbench SET last_recon_at = '{now_ts}' "
            f"WHERE outreach_id IN ('{oid_list}')"
        )

    out.close()
    elapsed = (time.time() - start) / 60
    print(
        f"\nDone in {elapsed:.1f}m | "
        f"OK:{success} CAPTCHA:{captcha_count} Err:{errors}"
    )
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()

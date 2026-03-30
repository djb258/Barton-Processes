"""
Process 300 — Blog Reconnaissance v3

Three phases, in order:
  Phase 1: PARSE  — Parse 4,608 existing context_summary records for names/titles (no fetch)
  Phase 2: FETCH  — Fetch 13,199 known about_urls, extract names/titles (direct, no proxy)
  Phase 3: DISCOVER — Try common paths on ~19K domains without about_url (direct, no proxy)

No search engine. No proxy. Direct fetch only.
Reads from D1 (via wrangler). Writes results back to D1 outreach_blog.

Usage:
  python3 src/blog-recon.py --phase 1 --limit 100          # parse existing content
  python3 src/blog-recon.py --phase 2 --limit 100          # fetch known about_urls
  python3 src/blog-recon.py --phase 3 --limit 100          # discover new about_urls
  python3 src/blog-recon.py --phase all --limit 50          # all three phases
  python3 src/blog-recon.py --phase 2 --resume              # resume interrupted

Env vars: D1_DB (default: svg-d1-outreach-ops)
"""

import json
import re
import time
import sys
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as creq

# ── Config ───────────────────────────────────────────────────

LIMIT = 0
PHASE = "1"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

# Common about/team page paths
PATHS = [
    "/about", "/about-us", "/about-us/", "/our-team", "/team",
    "/about/team", "/about/our-team", "/leadership", "/about/leadership",
    "/company", "/who-we-are", "/people", "/staff", "/management",
]

# ── Parse args ───────────────────────────────────────────────

args = sys.argv[1:]
resume = False
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1])
        i += 2
    elif args[i] == "--phase" and i + 1 < len(args):
        PHASE = args[i + 1]
        i += 2
    elif args[i] == "--resume":
        resume = True
        i += 1
    else:
        i += 1


# ── D1 Access ────────────────────────────────────────────────

def d1_query(sql: str) -> list:
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql, "--json"],
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


def d1_execute(sql: str) -> bool:
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )
    return result.returncode == 0


def escape_sql(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ── People extraction ────────────────────────────────────────

TITLE_PATTERNS = [
    # CEO slot — who runs the company
    r"CEO", r"Chief Executive Officer",
    r"President", r"Owner", r"Founder", r"Co-Founder",
    r"Managing Director", r"General Manager",
    r"Principal", r"Managing Partner",
    # CFO slot — who handles the money
    r"CFO", r"Chief Financial Officer",
    r"VP Finance", r"Vice President of Finance", r"VP of Finance",
    r"Controller", r"Treasurer", r"Director of Finance",
    # HR slot — who handles the people and benefits
    r"CHRO", r"Chief Human Resources Officer",
    r"HR Director", r"HR Manager", r"Director of HR",
    r"Director of Human Resources", r"VP Human Resources", r"VP of HR",
    r"VP People", r"Head of People", r"Head of HR",
    r"Director of People", r"People Operations",
    r"Benefits",
]

# Compiled pattern: any of the above as a bounded phrase
TITLE_RE = re.compile(
    r'\b(' + '|'.join(re.escape(t) for t in TITLE_PATTERNS) + r')\b',
    re.IGNORECASE
)

# Name pattern: 2-4 capitalized words, optionally with middle initial
NAME_RE = re.compile(
    r'([A-Z][a-z]{1,15}(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]{1,15}){1,3})'
)

def extract_people(html: str) -> list:
    """Extract names + titles from HTML. Deterministic. No AI.
    Only returns results where we have a real name AND a real title."""
    people = []

    # Strip scripts, styles, comments
    clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<!--.*?-->', '', clean, flags=re.DOTALL)

    # Strategy 1: Structured HTML blocks
    # Pattern: <h2-4|strong|b>Name</tag> ... <p|span|div>Title</tag>
    blocks = re.findall(
        r'<(?:h[2-4]|strong|b|span)[^>]*>\s*'
        r'([A-Z][a-z]{1,15}(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]{1,15}){1,3})'
        r'\s*</(?:h[2-4]|strong|b|span)>'
        r'([\s\S]{0,200})',
        clean
    )
    for name_raw, after_html in blocks:
        name = re.sub(r'\s+', ' ', name_raw).strip()
        if len(name) < 5 or len(name) > 45:
            continue
        # Check the text immediately after for a title
        after_text = re.sub(r'<[^>]+>', ' ', after_html).strip()
        title_match = TITLE_RE.search(after_text[:100])
        if title_match:
            # Extract the title phrase — the keyword plus surrounding context
            start = max(0, title_match.start() - 5)
            end = min(len(after_text), title_match.end() + 30)
            title = after_text[start:end].strip()
            title = re.sub(r'\s+', ' ', title)
            if not any(p["name"].lower() == name.lower() for p in people):
                people.append({"name": name, "title": title[:60]})

    # Strategy 2: "Name, Title" or "Name - Title" in plain text
    # Use body only to avoid nav/menu/footer noise
    body_match = re.search(r'<body[^>]*>(.*)</body>', clean, re.DOTALL | re.IGNORECASE)
    body = body_match.group(1) if body_match else clean
    # Strip nav, header, footer elements
    body = re.sub(r'<(?:nav|header|footer)[^>]*>.*?</(?:nav|header|footer)>', '', body, flags=re.DOTALL | re.IGNORECASE)
    plain = re.sub(r'<[^>]+>', ' ', body)
    plain = re.sub(r'&[a-z]+;', ' ', plain)
    plain = re.sub(r'&#\d+;', ' ', plain)
    plain = re.sub(r'\s+', ' ', plain)

    # Words that look like names but aren't people
    BAD_NAMES = {"our mission", "our team", "our story", "about us", "read more", "learn more",
                 "click here", "contact us", "get started", "our vision", "our values",
                 "sterling food pantry", "home page", "main menu", "skip to"}

    # Find all title keywords in plain text, then look backwards for a name
    for m in TITLE_RE.finditer(plain):
        # Look at the 80 chars before the title for a name
        start = max(0, m.start() - 80)
        before = plain[start:m.start()]
        # The name should be right before a separator
        name_match = re.search(
            r'([A-Z][a-z]{1,15}(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]{1,15}){1,3})'
            r'\s*[,\-–—|/]\s*$',
            before
        )
        if name_match:
            name = name_match.group(1).strip()
            title = m.group(0).strip()
            # Extend title to grab "of X" or similar
            after_title = plain[m.end():m.end()+40]
            ext = re.match(r'[\s,]*(of\s+\w[\w\s]{0,25}|[\w\s]{0,20})', after_title)
            if ext:
                title += " " + ext.group(0).strip()
            title = re.sub(r'\s+', ' ', title).strip()[:60]
            if len(name) >= 5 and len(name) <= 45:
                if name.lower() not in BAD_NAMES and "class=" not in title and "href=" not in title:
                    if not any(p["name"].lower() == name.lower() for p in people):
                        people.append({"name": name, "title": title})

    # Strategy 3: Schema.org JSON-LD (structured data — highest confidence)
    for ld_match in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE):
        try:
            ld = json.loads(ld_match.group(1))
            items = ld if isinstance(ld, list) else [ld]
            for item in items:
                # Handle @graph
                if isinstance(item, dict) and "@graph" in item:
                    items.extend(item["@graph"])
                    continue
                if not isinstance(item, dict):
                    continue
                t = item.get("@type", "")
                if t in ("Person", "Employee") or (isinstance(t, list) and any(x in ("Person", "Employee") for x in t)):
                    name = item.get("name", "")
                    title = item.get("jobTitle", "") or item.get("description", "")
                    if name and title and len(name) >= 5:
                        if not any(p["name"].lower() == name.lower() for p in people):
                            people.append({"name": name, "title": str(title)[:60]})
        except (json.JSONDecodeError, TypeError):
            pass

    return people


def write_people_to_d1(outreach_id: str, people: list) -> bool:
    """Write extracted people to outreach_blog.context_summary as structured JSON."""
    now = datetime.now(timezone.utc).isoformat()
    summary = json.dumps({
        "people": people,
        "people_count": len(people),
        "extracted_at": now,
    }).replace("'", "''")
    sql = (
        f"UPDATE outreach_blog SET "
        f"context_summary = '{summary}', "
        f"last_extracted_at = {escape_sql(now)} "
        f"WHERE outreach_id = {escape_sql(outreach_id)}"
    )
    return d1_execute(sql)


# ── Phase 1: PARSE existing context_summary ──────────────────

def phase_parse():
    print("[PHASE 1: PARSE] Loading records with existing context_summary...")

    # Get records that have raw HTML content (not already parsed JSON)
    sql = (
        "SELECT outreach_id, context_summary FROM outreach_blog "
        "WHERE context_summary IS NOT NULL "
        "AND LENGTH(context_summary) > 100 "
        "AND context_summary NOT LIKE '{\"people\"%'"
    )
    if LIMIT:
        sql += f" LIMIT {LIMIT}"

    rows = d1_query(sql)
    if not rows:
        print("[PHASE 1] No unparsed records found.")
        return

    print(f"[PHASE 1] {len(rows)} records to parse")

    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"parse-{run_date}.jsonl"
    out = open(output_file, "a")

    people_total = 0
    parsed = 0
    d1_updates = 0
    start = time.time()

    for idx, r in enumerate(rows):
        people = extract_people(r["context_summary"])
        parsed += 1
        people_total += len(people)

        record = {
            "outreach_id": r["outreach_id"],
            "people_count": len(people),
            "people": people,
        }
        out.write(json.dumps(record) + "\n")
        out.flush()

        if people:
            if write_people_to_d1(r["outreach_id"], people):
                d1_updates += 1

        if (idx + 1) % 100 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(f"  [{idx+1}/{len(rows)}] Parsed:{parsed} People:{people_total} D1:{d1_updates} | {rate:.0f}/hr")

    out.close()
    elapsed = (time.time() - start) / 60
    print(f"\n[PHASE 1] Done in {elapsed:.1f}m | Parsed:{parsed} People:{people_total} D1:{d1_updates}")


# ── Phase 2: FETCH known about_urls ──────────────────────────

def phase_fetch():
    print("[PHASE 2: FETCH] Loading companies with about_url...")

    sql = (
        "SELECT DISTINCT ob.outreach_id, ob.about_url, oo.domain "
        "FROM outreach_blog ob "
        "JOIN outreach_outreach oo ON ob.outreach_id = oo.outreach_id "
        "WHERE ob.about_url IS NOT NULL AND ob.about_url != '' "
        "AND (ob.last_extracted_at IS NULL OR ob.context_summary NOT LIKE '{\"people\"%')"
    )
    if LIMIT:
        sql += f" LIMIT {LIMIT}"

    companies = d1_query(sql)
    if not companies:
        print("[PHASE 2] No companies to fetch.")
        return

    print(f"[PHASE 2] {len(companies)} pages to fetch")

    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"fetch-{run_date}.jsonl"

    already_done = set()
    if resume and output_file.exists():
        with open(output_file) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    already_done.add(rec.get("outreach_id", ""))
                except:
                    pass
        print(f"[PHASE 2] Resuming: {len(already_done)} already done")

    remaining = [c for c in companies if c["outreach_id"] not in already_done]
    print(f"[PHASE 2] {len(remaining)} remaining")

    session = creq.Session(impersonate="chrome131")
    out = open(output_file, "a")
    people_total = 0
    pages_ok = 0
    pages_fail = 0
    d1_updates = 0
    start = time.time()

    for idx, c in enumerate(remaining):
        try:
            resp = session.get(c["about_url"], timeout=10, allow_redirects=True)
        except Exception as e:
            record = {
                "outreach_id": c["outreach_id"], "domain": c.get("domain", ""),
                "status": 0, "error": str(e)[:80], "people": [],
            }
            out.write(json.dumps(record) + "\n")
            out.flush()
            pages_fail += 1
            continue

        people = []
        if resp.status_code == 200 and len(resp.text) > 500:
            pages_ok += 1
            people = extract_people(resp.text)
            people_total += len(people)

            if people:
                if write_people_to_d1(c["outreach_id"], people):
                    d1_updates += 1
        else:
            pages_fail += 1

        record = {
            "outreach_id": c["outreach_id"], "domain": c.get("domain", ""),
            "status": resp.status_code, "people_count": len(people), "people": people,
        }
        out.write(json.dumps(record) + "\n")
        out.flush()

        if (idx + 1) % 50 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(f"  [{idx+1}/{len(remaining)}] OK:{pages_ok} Fail:{pages_fail} People:{people_total} D1:{d1_updates} | {rate:.0f}/hr")

        # Polite delay
        if idx < len(remaining) - 1:
            time.sleep(random.uniform(0.3, 0.8))

    out.close()
    elapsed = (time.time() - start) / 60
    print(f"\n[PHASE 2] Done in {elapsed:.1f}m | OK:{pages_ok} Fail:{pages_fail} People:{people_total} D1:{d1_updates}")


# ── Phase 3: DISCOVER about_urls via common paths ────────────

def phase_discover():
    print("[PHASE 3: DISCOVER] Loading companies without about_url...")

    sql = (
        "SELECT DISTINCT oo.outreach_id, oo.domain "
        "FROM outreach_outreach oo "
        "LEFT JOIN outreach_blog ob ON oo.outreach_id = ob.outreach_id "
        "WHERE oo.domain IS NOT NULL "
        "AND (ob.about_url IS NULL OR ob.about_url = '')"
    )
    if LIMIT:
        sql += f" LIMIT {LIMIT}"

    companies = d1_query(sql)
    if not companies:
        print("[PHASE 3] No companies without about_url.")
        return

    print(f"[PHASE 3] {len(companies)} companies to check")

    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"discover-{run_date}.jsonl"

    already_done = set()
    if resume and output_file.exists():
        with open(output_file) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    already_done.add(rec.get("outreach_id", ""))
                except:
                    pass
        print(f"[PHASE 3] Resuming: {len(already_done)} already done")

    remaining = [c for c in companies if c["outreach_id"] not in already_done]
    print(f"[PHASE 3] {len(remaining)} remaining")

    session = creq.Session(impersonate="chrome131")
    out = open(output_file, "a")
    path_found = 0
    homepage_found = 0
    not_found = 0
    d1_updates = 0
    start = time.time()

    for idx, c in enumerate(remaining):
        domain = c["domain"]
        outreach_id = c["outreach_id"]
        about_url = None
        source = None

        # Step 1: Try common paths
        for path in PATHS:
            url = f"https://{domain}{path}"
            try:
                resp = session.get(url, timeout=8, allow_redirects=True)
                if resp.status_code == 200 and len(resp.text) > 1000:
                    text_lower = resp.text.lower()
                    if any(kw in text_lower for kw in ["about", "team", "leadership", "founded", "mission", "our story", "who we are"]):
                        about_url = url
                        source = "path"
                        break
            except:
                continue

        # Step 2: Try homepage for team content
        if not about_url:
            try:
                resp = session.get(f"https://{domain}/", timeout=8, allow_redirects=True)
                if resp.status_code == 200:
                    text_lower = resp.text.lower()
                    if any(kw in text_lower for kw in ["ceo", "president", "founder", "owner", "chief"]):
                        about_url = f"https://{domain}/"
                        source = "homepage"
            except:
                pass

        record = {
            "outreach_id": outreach_id, "domain": domain,
            "about_url": about_url, "source": source,
            "discovered_at": datetime.now(timezone.utc).isoformat(),
        }
        out.write(json.dumps(record) + "\n")
        out.flush()

        if about_url:
            if source == "homepage":
                homepage_found += 1
            else:
                path_found += 1
            sql = f"UPDATE outreach_blog SET about_url = {escape_sql(about_url)} WHERE outreach_id = {escape_sql(outreach_id)}"
            if d1_execute(sql):
                d1_updates += 1
        else:
            not_found += 1

        if (idx + 1) % 25 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(f"  [{idx+1}/{len(remaining)}] Path:{path_found} Home:{homepage_found} Miss:{not_found} D1:{d1_updates} | {rate:.0f}/hr")

        if idx < len(remaining) - 1:
            time.sleep(random.uniform(0.3, 0.8))

    out.close()
    elapsed = (time.time() - start) / 60
    print(f"\n[PHASE 3] Done in {elapsed:.1f}m | Path:{path_found} Home:{homepage_found} Miss:{not_found} D1:{d1_updates}")


# ── Main ─────────────────────────────────────────────────────

def main():
    print(f"Process 300 — Blog Reconnaissance v3")
    print(f"Phase: {PHASE} | Limit: {LIMIT or 'ALL'} | Resume: {resume}")
    print(f"D1: {D1_DB}")
    print(f"No proxy. No search engine. Direct fetch.")
    print()

    if PHASE == "1":
        phase_parse()
    elif PHASE == "2":
        phase_fetch()
    elif PHASE == "3":
        phase_discover()
    elif PHASE == "all":
        phase_parse()
        print()
        phase_fetch()
        print()
        phase_discover()
    else:
        print(f"Unknown phase: {PHASE}. Available: 1, 2, 3, all")
        sys.exit(1)


if __name__ == "__main__":
    main()

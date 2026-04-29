"""
Process 200 — People Search (Pass 2)

Finds LinkedIn profiles for empty slots via Startpage search.
Same pattern as blog-recon Phase 3B — Python + curl_cffi + DataImpulse proxy.

For each empty slot:
  1. Build query: site:linkedin.com/in/ "Title" "Company" "City" "State"
  2. Search Startpage via DataImpulse sticky proxy (POST form)
  3. Parse LinkedIn URL from results
  4. Parse LinkedIn title tag: "Name - Title at Company | LinkedIn"
  5. Write person to D1 (people_people_master), fill slot

Usage:
  python3 src/people-search.py --limit 10          # test run
  python3 src/people-search.py --limit 100         # batch
  python3 src/people-search.py                     # all empty slots
  python3 src/people-search.py --resume            # resume interrupted
  python3 src/people-search.py --slot-type CEO     # only CEO slots

Env vars: D1_DB, PROXY_USER, PROXY_PASS
"""

import json
import re
import time
import sys
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as creq

# ── Config ───────────────────────────────────────────────────

LIMIT = 0
SLOT_TYPE = None  # None = all types
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
D1_SPINE = os.environ.get("D1_SPINE", "svg-d1-spine")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

# DataImpulse proxy config (proven 2026-03-31)
PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT = 10000
SEARCH_DELAY = 3  # seconds between queries

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

def d1_query(sql: str, db: str = None) -> list:
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


def d1_execute(sql: str, db: str = None) -> bool:
    db = db or D1_DB
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", db, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )
    return result.returncode == 0


def escape_sql(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ── Proxy ────────────────────────────────────────────────────

def get_proxy_url() -> str:
    if not PROXY_USER or not PROXY_PASS:
        raise RuntimeError("PROXY_USER and PROXY_PASS env vars required")
    user = f"{PROXY_USER}__cr.us"
    return f"http://{user}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"


# ── Title mapping ────────────────────────────────────────────

SLOT_QUERIES = {
    "CEO": 'CEO OR "Chief Executive" OR "President" OR "Owner" OR "Founder"',
    "CFO": 'CFO OR "Chief Financial" OR "VP Finance" OR "Controller"',
    "HR": '"HR Director" OR "VP Human Resources" OR "Head of HR" OR "HR Manager" OR "Benefits"',
}


# ── LinkedIn parsing ─────────────────────────────────────────

def parse_linkedin_title(raw: str) -> dict | None:
    """Parse LinkedIn <title> tag: 'Name - Title at Company | LinkedIn'"""
    if not raw:
        return None
    cleaned = re.sub(r'\s*\|\s*LinkedIn\s*$', '', raw, flags=re.IGNORECASE).strip()

    # "Name - Title at Company"
    m = re.match(r'^(.+?)\s*[-–]\s*(.+?)\s+at\s+(.+)$', cleaned, re.IGNORECASE)
    if m:
        return {"name": m.group(1).strip(), "title": m.group(2).strip(), "company": m.group(3).strip()}

    # "Name - Title - Company"
    parts = re.split(r'\s*[-–]\s*', cleaned)
    if len(parts) >= 3:
        return {"name": parts[0].strip(), "title": parts[1].strip(), "company": " - ".join(parts[2:]).strip()}
    if len(parts) == 2:
        return {"name": parts[0].strip(), "title": parts[1].strip(), "company": ""}

    if 2 < len(cleaned) < 60:
        return {"name": cleaned, "title": "", "company": ""}
    return None


# ── Search ───────────────────────────────────────────────────

def search_startpage(session: creq.Session, query: str, proxy_url: str) -> dict | None:
    """Search Startpage, return first LinkedIn URL + snippet."""
    try:
        resp = session.post(
            "https://www.startpage.com/do/dsearch",
            data={"q": query},
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=20,
            allow_redirects=True,
            impersonate="chrome131",
        )
    except Exception as e:
        return None

    if resp.status_code != 200:
        return None

    # Find LinkedIn URL in results
    linkedin_match = re.search(r'href="(https://(?:www\.)?linkedin\.com/in/[^"]+)"', resp.text, re.IGNORECASE)
    if not linkedin_match:
        return None

    linkedin_url = linkedin_match.group(1)
    return {"linkedin_url": linkedin_url, "source": "startpage"}


def fetch_linkedin_title(session: creq.Session, url: str, proxy_url: str) -> str | None:
    """Fetch LinkedIn profile page, extract <title> tag."""
    try:
        resp = session.get(
            url,
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=15,
            allow_redirects=True,
            impersonate="chrome131",
        )
        if resp.status_code == 200:
            m = re.search(r'<title>([^<]+)</title>', resp.text, re.IGNORECASE)
            if m:
                return m.group(1)
    except:
        pass
    return None


# ── Main ─────────────────────────────────────────────────────

def main():
    print(f"Process 200 — People Search (Pass 2)")
    print(f"Limit: {LIMIT or 'ALL'} | Slot type: {SLOT_TYPE or 'ALL'} | Resume: {resume}")

    if not PROXY_USER or not PROXY_PASS:
        print("ERROR: PROXY_USER and PROXY_PASS env vars required.")
        sys.exit(1)

    proxy_url = get_proxy_url()
    print(f"Proxy: DataImpulse sticky session (configured)")
    print()

    # Get empty slots with company context
    slot_filter = f"AND cs.slot_type = '{SLOT_TYPE}'" if SLOT_TYPE else ""
    sql = (
        f"SELECT cs.slot_id, cs.outreach_id, cs.company_unique_id, cs.slot_type, "
        f"ct.city, ct.state "
        f"FROM people_company_slot cs "
        f"JOIN outreach_company_target ct ON cs.outreach_id = ct.outreach_id "
        f"WHERE cs.is_filled = 0 {slot_filter} "
        f"ORDER BY ct.state, cs.slot_type"
    )
    if LIMIT:
        sql += f" LIMIT {LIMIT}"

    slots = d1_query(sql)
    if not slots:
        print("No empty slots to process.")
        return

    print(f"{len(slots)} empty slots to search")

    # Get company names from spine
    company_names = {}
    for slot in slots:
        oid = slot["outreach_id"]
        if oid not in company_names:
            rows = d1_query(
                f"SELECT canonical_name, company_name, company_domain FROM cl_company_identity WHERE outreach_id = {escape_sql(oid)} LIMIT 1",
                db=D1_SPINE,
            )
            if rows:
                name = rows[0].get("canonical_name") or rows[0].get("company_name") or ""
                company_names[oid] = {
                    "name": name,
                    "domain": rows[0].get("company_domain", ""),
                }
            else:
                company_names[oid] = {"name": "", "domain": ""}

    # Resume support
    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"people-search-{run_date}.jsonl"

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

    session = creq.Session(impersonate="chrome131")
    out = open(output_file, "a")

    found = 0
    missed = 0
    errors = 0
    d1_writes = 0
    start = time.time()

    for idx, slot in enumerate(remaining):
        oid = slot["outreach_id"]
        company = company_names.get(oid, {})
        company_name = company.get("name", "")
        city = slot.get("city", "")
        state = slot.get("state", "")
        slot_type = slot["slot_type"]

        if not company_name:
            record = {"slot_id": slot["slot_id"], "outreach_id": oid, "slot_type": slot_type, "result": "no_company_name"}
            out.write(json.dumps(record) + "\n")
            out.flush()
            missed += 1
            continue

        # Build search query
        title_query = SLOT_QUERIES.get(slot_type, slot_type)
        query = f'site:linkedin.com/in/ {title_query} "{company_name}" "{city}" "{state}"'

        # Search
        result = search_startpage(session, query, proxy_url)

        record = {
            "slot_id": slot["slot_id"],
            "outreach_id": oid,
            "slot_type": slot_type,
            "company_name": company_name,
            "city": city,
            "state": state,
            "query": query,
            "linkedin_url": None,
            "parsed": None,
            "result": "miss",
        }

        if result and result.get("linkedin_url"):
            # Fetch the LinkedIn title tag for name/title confirmation
            title_raw = fetch_linkedin_title(session, result["linkedin_url"], proxy_url)
            parsed = parse_linkedin_title(title_raw) if title_raw else None

            record["linkedin_url"] = result["linkedin_url"]
            record["title_raw"] = title_raw
            record["parsed"] = parsed

            if parsed and parsed.get("name"):
                record["result"] = "found"
                found += 1

                # Write to D1: create person, fill slot
                person_id = str(uuid.uuid4())
                name_parts = parsed["name"].split(" ", 1)
                first_name = name_parts[0] if name_parts else ""
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # Create person record
                person_sql = (
                    f"INSERT OR REPLACE INTO people_people_master ("
                    f"unique_id, company_unique_id, first_name, last_name, full_name, "
                    f"title, linkedin_url, source_system, "
                    f"created_at, updated_at, last_verified_at, email_verified, outreach_ready"
                    f") VALUES ("
                    f"{escape_sql(person_id)}, {escape_sql(slot['company_unique_id'])}, "
                    f"{escape_sql(first_name)}, {escape_sql(last_name)}, {escape_sql(parsed['name'])}, "
                    f"{escape_sql(parsed.get('title', ''))}, {escape_sql(result['linkedin_url'])}, "
                    f"'startpage_proxy', "
                    f"datetime('now'), datetime('now'), datetime('now'), 0, 0)"
                )
                if d1_execute(person_sql):
                    # Fill the slot
                    slot_sql = (
                        f"UPDATE people_company_slot SET "
                        f"person_unique_id = {escape_sql(person_id)}, "
                        f"is_filled = 1, "
                        f"filled_at = datetime('now'), "
                        f"source_system = 'startpage_proxy', "
                        f"confidence_score = 0.7, "
                        f"updated_at = datetime('now') "
                        f"WHERE slot_id = {escape_sql(slot['slot_id'])}"
                    )
                    if d1_execute(slot_sql):
                        d1_writes += 1
            else:
                record["result"] = "no_parse"
                missed += 1
        else:
            missed += 1

        out.write(json.dumps(record) + "\n")
        out.flush()

        if (idx + 1) % 10 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(
                f"  [{idx+1}/{len(remaining)}] "
                f"Found:{found} Miss:{missed} Err:{errors} D1:{d1_writes} | {rate:.0f}/hr"
            )

        # Rate limit
        if idx < len(remaining) - 1:
            time.sleep(SEARCH_DELAY)

    out.close()
    elapsed = (time.time() - start) / 60
    print(
        f"\nDone in {elapsed:.1f}m | "
        f"Found:{found} Miss:{missed} Err:{errors} D1:{d1_writes}"
    )
    if found + missed > 0:
        print(f"Hit rate: {found/(found+missed)*100:.1f}%")


if __name__ == "__main__":
    main()

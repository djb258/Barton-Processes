"""
Process 200 — Find Person (Natural Language Startpage Search)

Finds the person who holds each slot (CEO, CFO, HR) at a company.
Uses natural language queries through Startpage — no CAPTCHA.
Also captures LinkedIn URL if it appears in search results.

Query patterns that WORK (no CAPTCHA):
  - "who is the CEO of {company}"
  - "{company} CFO {city} {state}"
  - "{company} HR director"

Query patterns that FAIL (CAPTCHA):
  - "CEO" "Company Name" (quoted title + company)
  - site:linkedin.com/in/ anything
  - "linkedin" as keyword

Usage:
  python3 src/find-person.py --limit 10
  python3 src/find-person.py --limit 100 --slot-type CEO
  python3 src/find-person.py --resume
  python3 src/find-person.py  # all empty slots

Env vars: D1_DB, D1_SPINE, PROXY_USER, PROXY_PASS
"""

import json
import re
import time
import sys
import os
import uuid
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
PROXY_PORT = 10000
SEARCH_DELAY = 3

# Natural language query templates — these DON'T trigger CAPTCHA
QUERY_TEMPLATES = {
    "CEO": [
        "who is the CEO of {company}",
        "{company} CEO {city} {state}",
        "{company} chief executive officer",
    ],
    "CFO": [
        "who is the CFO of {company}",
        "{company} CFO {city} {state}",
        "{company} chief financial officer",
    ],
    "HR": [
        "{company} HR director {city} {state}",
        "who is the head of HR at {company}",
        "{company} human resources director",
    ],
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


def d1_execute(sql, db=None):
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

def get_proxy_url():
    if not PROXY_USER or not PROXY_PASS:
        raise RuntimeError("PROXY_USER and PROXY_PASS required")
    return f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"


# ── Search ───────────────────────────────────────────────────

def search_startpage(session, query, proxy_url):
    """Search Startpage with natural language query. Returns parsed results."""
    try:
        resp = session.post(
            "https://www.startpage.com/do/dsearch",
            data={"q": query},
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=30,
            allow_redirects=True,
            impersonate="chrome131",
        )
    except Exception as e:
        return {"error": str(e)[:80], "captcha": False, "linkedin_urls": [], "names": []}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "captcha": False, "linkedin_urls": [], "names": []}

    captcha = "captcha" in resp.text.lower()

    # Extract LinkedIn URLs
    linkedin_urls = list(set(re.findall(
        r'href="(https://(?:www\.)?linkedin\.com/in/[^"?]+)',
        resp.text, re.IGNORECASE
    )))

    # Extract names by finding the result title near each LinkedIn URL
    # Startpage format: "Name - Company - LinkedIn" or "Name - Title at Company | LinkedIn"
    names = []
    for url in linkedin_urls:
        # Find the chunk of HTML around this URL — title comes AFTER the URL in the DOM
        url_idx = resp.text.find(url)
        if url_idx < 0:
            continue
        chunk = resp.text[url_idx:url_idx + 2000]

        # Look for "Name - Something - LinkedIn" pattern in text content
        title_matches = re.findall(r'>([A-Z][a-z]+(?:\s[A-Z]\.?\s*)?(?:\s[A-Z][a-z]+){1,3})\s*[-–]\s*([^<]+?)(?:\s*[-–]\s*LinkedIn)', chunk)
        if title_matches:
            name = title_matches[0][0].strip()
            title = title_matches[0][1].strip()
            if len(name) > 3 and len(name) < 50 and name != "LinkedIn":
                names.append({"name": name, "title": title, "linkedin_url": url})
                continue

        # Fallback: look for "Name · View mutual" pattern
        mutual_match = re.findall(r'>([A-Z][a-z]+(?:\s[A-Z]\.?\s*)?(?:\s[A-Z][a-z]+){1,3})\s*(?:&middot;|·)\s*View', chunk)
        if mutual_match:
            name = mutual_match[0].strip()
            if len(name) > 3 and len(name) < 50:
                names.append({"name": name, "title": "", "linkedin_url": url})
                continue

        # Fallback: derive name from URL slug (john-smith-123 → John Smith)
        slug = url.rstrip("/").split("/in/")[-1] if "/in/" in url else ""
        slug_clean = re.sub(r'-[a-f0-9]{4,}$', '', slug)  # Remove trailing hex IDs
        slug_clean = re.sub(r'-\d{2,}$', '', slug_clean)  # Remove trailing numbers
        slug_clean = re.sub(r'%[0-9A-Fa-f]{2}', '', slug_clean)  # Remove URL encoding
        slug_parts = slug_clean.split("-")
        if 2 <= len(slug_parts) <= 4:
            derived_name = " ".join(p.capitalize() for p in slug_parts if len(p) > 1)
            if len(derived_name) > 3:
                names.append({"name": derived_name, "title": "", "linkedin_url": url})

    # Also look for names in result text with title keywords
    title_names = re.findall(
        r'>([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*[-–|,]\s*'
        r'(?:CEO|CFO|Chief|Director|VP|Head|President|Founder|Owner|Controller|HR|Human)',
        resp.text
    )
    for tn in title_names:
        if not any(n["name"].lower() == tn.lower() for n in names):
            names.append({"name": tn, "title": "", "linkedin_url": ""})

    return {
        "captcha": captcha,
        "linkedin_urls": linkedin_urls,
        "names": names,
        "result_count": len(re.findall(r'class="result', resp.text)),
    }


# ── Main ─────────────────────────────────────────────────────

def main():
    print("Process 200 — Find Person (Natural Language Startpage)")
    print(f"Limit: {LIMIT or 'ALL'} | Slot type: {SLOT_TYPE or 'ALL'} | Resume: {resume}")

    if not PROXY_USER or not PROXY_PASS:
        print("ERROR: PROXY_USER and PROXY_PASS required")
        sys.exit(1)

    proxy_url = get_proxy_url()
    print(f"Proxy: DataImpulse sticky session")
    print()

    # Get empty slots with company context
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

    slots = d1_query(sql)
    if not slots:
        print("No empty slots.")
        return

    print(f"{len(slots)} empty slots to search")

    # Get company names from spine
    company_cache = {}
    for slot in slots:
        oid = slot["outreach_id"]
        if oid not in company_cache:
            rows = d1_query(
                f"SELECT canonical_name, company_name, company_domain FROM cl_company_identity "
                f"WHERE outreach_id = {escape_sql(oid)} LIMIT 1",
                db=D1_SPINE,
            )
            if rows:
                company_cache[oid] = {
                    "name": rows[0].get("canonical_name") or rows[0].get("company_name") or "",
                    "domain": rows[0].get("company_domain") or "",
                }
            else:
                company_cache[oid] = {"name": "", "domain": ""}

    # Resume support
    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"find-person-{run_date}.jsonl"

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
    found_linkedin = 0
    missed = 0
    captcha_count = 0
    d1_writes = 0
    start = time.time()

    for idx, slot in enumerate(remaining):
        oid = slot["outreach_id"]
        company = company_cache.get(oid, {})
        company_name = company.get("name", "")
        company_domain = company.get("domain", "")
        city = slot.get("city", "") or ""
        state = slot.get("state", "") or ""
        slot_type = slot["slot_type"]

        if not company_name:
            record = {"slot_id": slot["slot_id"], "outreach_id": oid, "slot_type": slot_type, "result": "no_company_name"}
            out.write(json.dumps(record) + "\n")
            out.flush()
            missed += 1
            continue

        # Try query templates in order — stop on first success
        best_result = None
        templates = QUERY_TEMPLATES.get(slot_type, QUERY_TEMPLATES["CEO"])

        for template in templates:
            query = template.format(company=company_name, city=city, state=state)
            result = search_startpage(session, query, proxy_url)

            if result.get("captcha"):
                captcha_count += 1
                time.sleep(5)  # Extra delay on CAPTCHA
                continue

            if result.get("names") or result.get("linkedin_urls"):
                best_result = result
                best_result["query"] = query
                break

            time.sleep(SEARCH_DELAY)

        # Build output record
        record = {
            "slot_id": slot["slot_id"],
            "outreach_id": oid,
            "slot_type": slot_type,
            "company_name": company_name,
            "company_domain": company_domain,
            "city": city,
            "state": state,
            "result": "miss",
            "query": "",
            "person_name": None,
            "person_title": None,
            "linkedin_url": None,
        }

        if best_result and best_result.get("names"):
            person = best_result["names"][0]
            record["result"] = "found"
            record["query"] = best_result.get("query", "")
            record["person_name"] = person["name"]
            record["person_title"] = person.get("title", "")
            record["linkedin_url"] = person.get("linkedin_url") or (
                best_result["linkedin_urls"][0] if best_result.get("linkedin_urls") else None
            )
            found += 1
            if record["linkedin_url"]:
                found_linkedin += 1

            # Write to D1 — create person, fill slot
            person_id = str(uuid.uuid4())
            name_parts = person["name"].split(" ", 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            person_sql = (
                f"INSERT OR REPLACE INTO people_people_master ("
                f"unique_id, company_unique_id, company_slot_unique_id, "
                f"first_name, last_name, full_name, "
                f"title, linkedin_url, source_system, "
                f"promoted_from_intake_at, "
                f"created_at, updated_at, last_verified_at, email_verified, outreach_ready"
                f") VALUES ("
                f"{escape_sql(person_id)}, {escape_sql(slot['company_unique_id'])}, "
                f"{escape_sql(slot['slot_id'])}, "
                f"{escape_sql(first_name)}, {escape_sql(last_name)}, {escape_sql(person['name'])}, "
                f"{escape_sql(person.get('title', ''))}, {escape_sql(record['linkedin_url'])}, "
                f"'startpage_natural', "
                f"datetime('now'), "
                f"datetime('now'), datetime('now'), datetime('now'), 0, 0)"
            )
            if d1_execute(person_sql):
                slot_sql = (
                    f"UPDATE people_company_slot SET "
                    f"person_unique_id = {escape_sql(person_id)}, "
                    f"is_filled = 1, "
                    f"filled_at = datetime('now'), "
                    f"source_system = 'startpage_natural', "
                    f"confidence_score = 0.7, "
                    f"updated_at = datetime('now') "
                    f"WHERE slot_id = {escape_sql(slot['slot_id'])}"
                )
                if d1_execute(slot_sql):
                    d1_writes += 1

        elif best_result and best_result.get("linkedin_urls"):
            # Got LinkedIn URL but no parsed name
            record["result"] = "linkedin_only"
            record["linkedin_url"] = best_result["linkedin_urls"][0]
            record["query"] = best_result.get("query", "")
            found_linkedin += 1
        else:
            missed += 1

        out.write(json.dumps(record) + "\n")
        out.flush()

        if (idx + 1) % 10 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(
                f"  [{idx+1}/{len(remaining)}] "
                f"Found:{found} LinkedIn:{found_linkedin} Miss:{missed} CAPTCHA:{captcha_count} D1:{d1_writes} | {rate:.0f}/hr"
            )

        if idx < len(remaining) - 1:
            time.sleep(SEARCH_DELAY + random.uniform(0, 2))

    out.close()
    elapsed = (time.time() - start) / 60
    print(
        f"\nDone in {elapsed:.1f}m | "
        f"Found:{found} LinkedIn:{found_linkedin} Miss:{missed} CAPTCHA:{captcha_count} D1:{d1_writes}"
    )
    if found + missed > 0:
        print(f"Hit rate: {found / (found + missed) * 100:.1f}%")


if __name__ == "__main__":
    main()

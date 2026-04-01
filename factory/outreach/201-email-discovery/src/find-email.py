"""
Process 201 — Find Email (Startpage Pattern Verification)

Given a person with name + company domain, generates email patterns
and searches Startpage for each one. If the exact email appears in
indexed web pages (results > 0), it's real.

This is FREE — uses Startpage search as a verifier instead of
paying Million Verifier $0.003/check.

Runs AFTER Process 200 fills slots with names.
Only processes slots that have a person but no verified email.

Usage:
  python3 src/find-email.py --limit 10
  python3 src/find-email.py --limit 100 --slot-type CEO
  python3 src/find-email.py --resume
  python3 src/find-email.py  # all slots needing email

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
PROXY_PORT = 10000
SEARCH_DELAY = 3

# Email patterns to try — ordered by most common first
# ~60% of companies use first.last@domain
EMAIL_PATTERNS = [
    "{first}.{last}@{domain}",
    "{first}{last}@{domain}",
    "{fi}{last}@{domain}",
]

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


# ── Email Pattern Generation ─────────────────────────────────

def generate_email_candidates(first_name, last_name, domain):
    """Generate likely email patterns from name + domain."""
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    fi = first[0] if first else ""

    if not first or not last or not domain:
        return []

    candidates = []
    for pattern in EMAIL_PATTERNS:
        email = pattern.format(first=first, last=last, fi=fi, domain=domain)
        candidates.append(email)

    return candidates


# ── Startpage Email Verification ─────────────────────────────

def verify_email_startpage(session, email, proxy_url):
    """Search Startpage for email pattern — NO QUOTES (quotes trigger CAPTCHA)."""
    query = email  # Plain text, no quotes — Startpage doesn't CAPTCHA this
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
        return {"email": email, "found": False, "results": 0, "captcha": False, "error": str(e)[:60]}

    captcha = "captcha" in resp.text.lower()
    result_count = len(re.findall(r'class="result', resp.text))

    # Check if the exact email string appears in the page content
    email_in_page = email.lower() in resp.text.lower()

    return {
        "email": email,
        "found": result_count > 0 and email_in_page,
        "results": result_count,
        "captcha": captcha,
    }


# ── Main ─────────────────────────────────────────────────────

def main():
    print("Process 201 — Find Email (Startpage Pattern Verification)")
    print(f"Limit: {LIMIT or 'ALL'} | Slot type: {SLOT_TYPE or 'ALL'} | Resume: {resume}")

    if not PROXY_USER or not PROXY_PASS:
        print("ERROR: PROXY_USER and PROXY_PASS required")
        sys.exit(1)

    proxy_url = get_proxy_url()
    print(f"Proxy: DataImpulse sticky session")
    print()

    # Get filled slots where person has no email
    slot_filter = f"AND cs.slot_type = '{SLOT_TYPE}'" if SLOT_TYPE else ""
    sql = (
        f"SELECT cs.slot_id, cs.outreach_id, cs.company_unique_id, cs.slot_type, "
        f"cs.person_unique_id, "
        f"pm.first_name, pm.last_name, pm.full_name, pm.email, pm.email_verified "
        f"FROM people_company_slot cs "
        f"JOIN people_people_master pm ON cs.person_unique_id = pm.unique_id "
        f"WHERE cs.is_filled = 1 "
        f"AND (pm.email IS NULL OR pm.email = '' OR pm.email_verified = 0) "
        f"{slot_filter} "
        f"ORDER BY cs.slot_type"
    )
    if LIMIT:
        sql += f" LIMIT {LIMIT}"

    slots = d1_query(sql)
    if not slots:
        print("No slots needing email discovery.")
        return

    print(f"{len(slots)} slots need email")

    # Get company domains from outreach_outreach
    domain_cache = {}
    for slot in slots:
        oid = slot["outreach_id"]
        if oid not in domain_cache:
            rows = d1_query(f"SELECT domain FROM outreach_outreach WHERE outreach_id = {escape_sql(oid)} LIMIT 1")
            domain_cache[oid] = rows[0]["domain"] if rows else ""

    # Resume support
    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"find-email-{run_date}.jsonl"

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
    captcha_count = 0
    d1_writes = 0
    start = time.time()

    for idx, slot in enumerate(remaining):
        oid = slot["outreach_id"]
        domain = domain_cache.get(oid, "")
        first_name = slot.get("first_name", "")
        last_name = slot.get("last_name", "")

        if not domain or not first_name or not last_name:
            record = {
                "slot_id": slot["slot_id"], "outreach_id": oid,
                "slot_type": slot["slot_type"], "result": "missing_data",
                "first_name": first_name, "last_name": last_name, "domain": domain,
            }
            out.write(json.dumps(record) + "\n")
            out.flush()
            missed += 1
            continue

        # Generate email candidates
        candidates = generate_email_candidates(first_name, last_name, domain)

        record = {
            "slot_id": slot["slot_id"],
            "outreach_id": oid,
            "slot_type": slot["slot_type"],
            "person": f"{first_name} {last_name}",
            "domain": domain,
            "result": "miss",
            "verified_email": None,
            "candidates_tested": [],
        }

        # Test each candidate — stop on first match
        for email in candidates:
            result = verify_email_startpage(session, email, proxy_url)
            record["candidates_tested"].append(result)

            if result.get("captcha"):
                captcha_count += 1
                time.sleep(5)
                continue

            if result.get("found"):
                record["result"] = "found"
                record["verified_email"] = email
                found += 1

                # Write to D1
                update_sql = (
                    f"UPDATE people_people_master SET "
                    f"email = {escape_sql(email)}, "
                    f"email_verified = 1, "
                    f"email_verification_source = 'startpage_indexed', "
                    f"email_verified_at = datetime('now'), "
                    f"updated_at = datetime('now') "
                    f"WHERE unique_id = {escape_sql(slot['person_unique_id'])}"
                )
                if d1_execute(update_sql):
                    d1_writes += 1

                break  # Found — don't test more patterns

            time.sleep(SEARCH_DELAY)

        if record["result"] != "found":
            missed += 1

        out.write(json.dumps(record) + "\n")
        out.flush()

        if (idx + 1) % 10 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            print(
                f"  [{idx+1}/{len(remaining)}] "
                f"Found:{found} Miss:{missed} CAPTCHA:{captcha_count} D1:{d1_writes} | {rate:.0f}/hr"
            )

        if idx < len(remaining) - 1:
            time.sleep(random.uniform(1, 2))

    out.close()
    elapsed = (time.time() - start) / 60
    print(
        f"\nDone in {elapsed:.1f}m | "
        f"Found:{found} Miss:{missed} CAPTCHA:{captcha_count} D1:{d1_writes}"
    )
    if found + missed > 0:
        print(f"Hit rate: {found / (found + missed) * 100:.1f}%")


if __name__ == "__main__":
    main()

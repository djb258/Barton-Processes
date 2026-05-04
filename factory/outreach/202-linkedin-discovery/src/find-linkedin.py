#!/usr/bin/env python3
"""
Process 202 — Find LinkedIn (Gate Chain: Recon Match -> Hunter -> Startpage)

Fills empty person_linkedin on slots in slot_workbench that have
has_name = 1 AND has_linkedin = 0.

Three gates checked in order:
  Gate A: Match person name to recon_linkedin_people URLs from Process 300. FREE.
  Gate B: Promote hunter_linkedin if present. FREE.
  Gate C: Startpage natural language search via DataImpulse proxy. CHEAP.

Reads/writes D1 slot_workbench via wrangler subprocess.

Usage:
  python3 find-linkedin.py --limit 50
  python3 find-linkedin.py --limit 100 --offset 200
  python3 find-linkedin.py --limit 50 --dry-run
  python3 find-linkedin.py --resume
  python3 find-linkedin.py --port-base 10100

Env vars: PROXY_USER, PROXY_PASS
"""

import json
import re
import time
import sys
import os
import subprocess
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as creq

# ===================================================================
# CONSTANTS (Bedrock-validated -- survive IMO + CTB + Circle)
# ===================================================================

DB_NAME = "svg-d1-outreach-ops"
REPO_ROOT = Path(__file__).resolve().parents[4]
WRANGLER_CWD = os.environ.get("WRANGLER_CWD", str(REPO_ROOT))
NPX_CMD = os.environ.get("NPX_CMD") or shutil.which("npx.cmd") or shutil.which("npx") or "npx"

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"

SEARCH_DELAY = 3  # seconds between Startpage queries
PORT_ROTATION_INTERVAL = 50  # rotate proxy port every N queries

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# LinkedIn URL validation pattern
LINKEDIN_IN_RE = re.compile(
    r'https?://(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-_%]+)',
    re.IGNORECASE,
)


# ===================================================================
# ARGS
# ===================================================================

LIMIT = 0
OFFSET = 0
PORT_BASE = 10000
DRY_RUN = False
RESUME = False

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
    elif args[i] == "--offset" and i + 1 < len(args):
        OFFSET = int(args[i + 1]); i += 2
    elif args[i] == "--port-base" and i + 1 < len(args):
        PORT_BASE = int(args[i + 1]); i += 2
    elif args[i] == "--dry-run":
        DRY_RUN = True; i += 1
    elif args[i] == "--resume":
        RESUME = True; i += 1
    else:
        i += 1


# ===================================================================
# D1 ACCESS (subprocess wrangler)
# ===================================================================

def d1_query(sql):
    """Execute a D1 query and return rows."""
    sql = re.sub(r"[\r\n\t]+", " ", sql).strip()
    result = subprocess.run(
        [NPX_CMD, "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql, "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=WRANGLER_CWD, timeout=120,
    )
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("results", [])
    except json.JSONDecodeError:
        stdout = result.stdout
        start = stdout.find("[")
        if start >= 0:
            try:
                data = json.loads(stdout[start:])
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("results", [])
            except Exception:
                pass
    return []


def d1_execute(sql):
    """Execute a D1 write statement. Returns True on success."""
    if DRY_RUN:
        print(f"  [DRY-RUN] {sql[:120]}...")
        return True
    sql = re.sub(r"[\r\n\t]+", " ", sql).strip()
    result = subprocess.run(
        [NPX_CMD, "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=WRANGLER_CWD, timeout=120,
    )
    return result.returncode == 0


def esc(s):
    """SQL-escape a string value. None -> NULL."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ===================================================================
# GATE A: Match person name to recon_linkedin_people (FREE)
# ===================================================================

def _normalize(s):
    """Lowercase, strip non-alpha except spaces."""
    if not s:
        return ""
    return re.sub(r'[^a-z\s]', '', s.lower()).strip()


def _slug_to_name_parts(slug):
    """
    Parse a LinkedIn slug into (first, last) candidates.
    e.g. 'john-smith-12345' -> ('john', 'smith')
         'john-a-smith' -> ('john', 'smith')  (drops single-char middle parts)
    """
    if not slug:
        return None, None
    # Remove trailing hex/numeric IDs
    slug = re.sub(r'-[a-f0-9]{4,}$', '', slug)
    slug = re.sub(r'-\d{2,}$', '', slug)
    # Remove URL encoding artifacts
    slug = re.sub(r'%[0-9A-Fa-f]{2}', '', slug)
    parts = [p for p in slug.split('-') if len(p) > 1]
    if len(parts) < 2:
        return None, None
    return parts[0].lower(), parts[-1].lower()


def gate_a_recon_match(slot):
    """
    Match person_first_name + person_last_name against LinkedIn slugs
    in recon_linkedin_people JSON array.
    Returns matched URL or None.
    """
    recon_json = slot.get("recon_linkedin_people")
    if not recon_json:
        return None

    first = _normalize(slot.get("person_first_name", ""))
    last = _normalize(slot.get("person_last_name", ""))
    if not first or not last:
        return None

    try:
        urls = json.loads(recon_json) if isinstance(recon_json, str) else recon_json
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(urls, list):
        return None

    for url in urls:
        if not isinstance(url, str):
            continue
        m = LINKEDIN_IN_RE.search(url)
        if not m:
            continue
        slug = m.group(1)
        slug_first, slug_last = _slug_to_name_parts(slug)
        if not slug_first or not slug_last:
            continue

        # Exact match: first + last
        if slug_first == first and slug_last == last:
            return url.split("?")[0].rstrip("/")

        # First-initial match: j + smith for John Smith
        if slug_first == first[0] and slug_last == last:
            return url.split("?")[0].rstrip("/")

    return None


# ===================================================================
# GATE B: Promote hunter_linkedin (FREE)
# ===================================================================

def gate_b_hunter(slot):
    """
    If hunter_linkedin is present and looks like a valid LinkedIn /in/ URL,
    promote it.
    """
    hunter_li = slot.get("hunter_linkedin")
    if not hunter_li or not isinstance(hunter_li, str):
        return None
    hunter_li = hunter_li.strip()
    if LINKEDIN_IN_RE.search(hunter_li):
        return hunter_li.split("?")[0].rstrip("/")
    return None


# ===================================================================
# GATE C: Startpage search (CHEAP -- proxy only)
# ===================================================================

def get_proxy_url(port):
    """Build DataImpulse proxy URL with port rotation."""
    if not PROXY_USER or not PROXY_PASS:
        raise RuntimeError("PROXY_USER and PROXY_PASS env vars required for Gate C")
    return f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"


def build_query(slot):
    """
    Build natural language search query for LinkedIn profile.
    Format: {first_name} {last_name} {company_name} linkedin
    For common names, add {city}.
    """
    first = slot.get("person_first_name", "")
    last = slot.get("person_last_name", "")
    company = slot.get("company_name", "")
    city = slot.get("city", "")

    parts = [first, last, company, "linkedin"]

    # Common first names that need disambiguation
    COMMON_FIRST = {
        "john", "james", "robert", "michael", "william", "david", "richard",
        "joseph", "thomas", "charles", "chris", "daniel", "matthew", "mark",
        "mary", "jennifer", "jessica", "sarah", "lisa", "karen", "nancy",
        "mike", "joe", "bob", "jim", "tom", "bill", "dan", "matt", "steve",
        "brian", "kevin", "jason", "jeff", "scott", "eric", "greg", "tim",
        "ryan", "adam", "aaron", "andrew", "anthony", "brandon", "chad",
    }

    if first.lower() in COMMON_FIRST and city:
        parts.insert(3, city)

    return " ".join(p for p in parts if p)


def search_startpage(session, query, proxy_url):
    """
    Search Startpage with natural language query via DataImpulse proxy.
    Returns list of LinkedIn /in/ URLs found.
    """
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
        return {"error": str(e)[:100], "captcha": False, "urls": []}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "captcha": False, "urls": []}

    html = resp.text
    captcha = "captcha" in html.lower()

    # Extract all LinkedIn /in/ URLs from results
    urls = list(set(re.findall(
        r'href="(https://(?:www\.)?linkedin\.com/in/[^"?]+)',
        html, re.IGNORECASE,
    )))

    return {
        "captcha": captcha,
        "urls": urls,
        "result_count": len(re.findall(r'class="result', html)),
    }


def pick_best_linkedin(urls, slot):
    """
    From a list of LinkedIn /in/ URLs, pick the one whose slug best matches
    the person name we're looking for.
    Returns the best URL or None.
    """
    if not urls:
        return None

    first = _normalize(slot.get("person_first_name", ""))
    last = _normalize(slot.get("person_last_name", ""))

    if not first or not last:
        # No name to match against -- return first URL as fallback
        return urls[0].rstrip("/") if urls else None

    scored = []
    for url in urls:
        m = LINKEDIN_IN_RE.search(url)
        if not m:
            continue
        slug = m.group(1)
        slug_first, slug_last = _slug_to_name_parts(slug)
        if not slug_first or not slug_last:
            scored.append((0, url))
            continue

        score = 0
        if slug_first == first:
            score += 2
        elif slug_first == first[0]:
            score += 1
        if slug_last == last:
            score += 2

        scored.append((score, url))

    if not scored:
        return None

    scored.sort(key=lambda x: -x[0])
    best_score, best_url = scored[0]

    # Require at least last name match (score >= 2)
    if best_score >= 2:
        return best_url.split("?")[0].rstrip("/")

    # If only one result, use it even with low confidence
    if len(urls) == 1:
        return urls[0].split("?")[0].rstrip("/")

    return None


# ===================================================================
# READINESS TIER CALCULATOR
# ===================================================================

def calc_readiness_tier(slot, has_linkedin_now):
    """
    Recalculate readiness_tier based on current slot state.
    FULL          = has_name + has_email + has_linkedin
    REACHABLE     = has_name + (has_email OR has_linkedin)
    PATTERN_READY = has_name only
    EMPTY         = no name
    """
    has_name = bool(slot.get("has_name"))
    has_email = bool(slot.get("has_email"))
    has_linkedin = has_linkedin_now or bool(slot.get("has_linkedin"))

    if has_name and has_email and has_linkedin:
        return "FULL"
    elif has_name and (has_email or has_linkedin):
        return "REACHABLE"
    elif has_name:
        return "PATTERN_READY"
    else:
        return "EMPTY"


# ===================================================================
# SLOT UPDATE
# ===================================================================

def update_slot(slot, linkedin_url, source):
    """
    Write the discovered LinkedIn URL back to slot_workbench.
    Returns True on success.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    slot_id = slot["slot_id"]

    new_tier = calc_readiness_tier(slot, has_linkedin_now=True)

    set_parts = [
        f"person_linkedin = {esc(linkedin_url)}",
        f"has_linkedin = 1",
        f"linkedin_found_at = {esc(now)}",
        f"linkedin_last_checked_at = {esc(now)}",
        f"linkedin_changed = 1",
        f"readiness_tier = {esc(new_tier)}",
    ]

    sql = f"UPDATE slot_workbench SET {', '.join(set_parts)} WHERE slot_id = {esc(slot_id)}"
    return d1_execute(sql)


# ===================================================================
# MAIN
# ===================================================================

def main():
    print("=" * 60)
    print("Process 202 - Find LinkedIn (Gate Chain)")
    print(f"Limit: {LIMIT or 'ALL'} | Offset: {OFFSET} | Dry-run: {DRY_RUN} | Resume: {RESUME}")
    print(f"Port base: {PORT_BASE}")
    print("=" * 60)

    # -- 1. Load slots needing LinkedIn ----------------------------
    sql = (
        "SELECT slot_id, outreach_id, company_unique_id, slot_type, "
        "company_name, city, state, domain, company_domain, "
        "person_first_name, person_last_name, person_full_name, "
        "recon_linkedin_people, "
        "hunter_linkedin, "
        "has_name, has_email, has_linkedin, "
        "readiness_tier "
        "FROM slot_workbench "
        "WHERE has_name = 1 AND has_linkedin = 0 "
        "ORDER BY outreach_id"
    )
    if LIMIT:
        sql += f" LIMIT {LIMIT}"
    if OFFSET:
        sql += f" OFFSET {OFFSET}"

    print("\nLoading slots (has_name=1, has_linkedin=0)...")
    slots = d1_query(sql)
    if not slots:
        print("No slots needing LinkedIn found. Done.")
        return

    print(f"Loaded {len(slots)} slots needing LinkedIn")

    # -- Resume support --------------------------------------------
    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"find-linkedin-{run_date}.jsonl"

    already_done = set()
    if RESUME and output_file.exists():
        with open(output_file) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    already_done.add(rec.get("slot_id", ""))
                except Exception:
                    pass
        print(f"Resuming: {len(already_done)} already processed")

    remaining = [s for s in slots if s["slot_id"] not in already_done]
    print(f"{len(remaining)} slots to process\n")

    if not remaining:
        print("Nothing to do.")
        return

    # -- Counters --------------------------------------------------
    stats = {
        "gate_a_matched": 0,
        "gate_b_promoted": 0,
        "gate_c_searched": 0,
        "gate_c_found": 0,
        "captcha_count": 0,
        "missed": 0,
        "d1_writes": 0,
        "errors": 0,
        "tier_upgrades": {"FULL": 0, "REACHABLE": 0},
    }

    # -- Session for Gate C ----------------------------------------
    session = creq.Session()
    current_port = PORT_BASE
    search_count = 0
    consecutive_captcha = 0

    for idx, slot in enumerate(remaining, 1):
        slot_id = slot["slot_id"]
        first = slot.get("person_first_name", "")
        last = slot.get("person_last_name", "")
        company = slot.get("company_name", "")
        print(f"[{idx}/{len(remaining)}] {slot_id}: {first} {last} @ {company}")

        linkedin_url = None
        source = None

        # ---- Gate A: Recon LinkedIn match (FREE) ----
        linkedin_url = gate_a_recon_match(slot)
        if linkedin_url:
            source = "recon_match_202"
            stats["gate_a_matched"] += 1
            print(f"  Gate A HIT: {linkedin_url}")

        # ---- Gate B: Hunter LinkedIn (FREE) ----
        if not linkedin_url:
            linkedin_url = gate_b_hunter(slot)
            if linkedin_url:
                source = "hunter_linkedin_202"
                stats["gate_b_promoted"] += 1
                print(f"  Gate B HIT: {linkedin_url}")

        # ---- Gate C: Startpage search (CHEAP) ----
        if not linkedin_url:
            if not PROXY_USER or not PROXY_PASS:
                print("  Gate C SKIP: No proxy credentials")
            elif consecutive_captcha >= 3:
                print("  Gate C HALT: 3 consecutive CAPTCHAs -- stopping searches")
            else:
                # Rotate port
                if search_count > 0 and search_count % PORT_ROTATION_INTERVAL == 0:
                    current_port = PORT_BASE + random.randint(1, 999)
                    print(f"  Rotating proxy port to {current_port}")

                proxy_url = get_proxy_url(current_port)
                query = build_query(slot)
                print(f"  Gate C: searching '{query}'")

                result = search_startpage(session, query, proxy_url)
                search_count += 1
                stats["gate_c_searched"] += 1

                if result.get("captcha"):
                    consecutive_captcha += 1
                    stats["captcha_count"] += 1
                    print(f"  Gate C: CAPTCHA detected ({consecutive_captcha}/3)")
                elif result.get("error"):
                    print(f"  Gate C: Error: {result['error']}")
                    stats["errors"] += 1
                else:
                    consecutive_captcha = 0
                    urls = result.get("urls", [])
                    print(f"  Gate C: {len(urls)} LinkedIn URL(s) found in {result.get('result_count', 0)} results")

                    if urls:
                        linkedin_url = pick_best_linkedin(urls, slot)
                        if linkedin_url:
                            source = "startpage_202"
                            stats["gate_c_found"] += 1
                            print(f"  Gate C HIT: {linkedin_url}")
                        else:
                            print(f"  Gate C: No confident match from {len(urls)} URLs")

                # Delay between searches
                time.sleep(SEARCH_DELAY)

        # ---- Write result ----
        if linkedin_url and source:
            ok = update_slot(slot, linkedin_url, source)
            if ok:
                stats["d1_writes"] += 1
                new_tier = calc_readiness_tier(slot, has_linkedin_now=True)
                if new_tier in ("FULL", "REACHABLE"):
                    stats["tier_upgrades"][new_tier] = stats["tier_upgrades"].get(new_tier, 0) + 1
                print(f"  WRITTEN: {linkedin_url} | tier -> {new_tier}")
            else:
                stats["errors"] += 1
                print(f"  ERROR: D1 write failed for {slot_id}")
        else:
            stats["missed"] += 1
            print(f"  MISS: No LinkedIn found")

        # ---- Log to JSONL ----
        log_entry = {
            "slot_id": slot_id,
            "person": f"{first} {last}",
            "company": company,
            "linkedin_url": linkedin_url,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with open(output_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    # -- Summary ---------------------------------------------------
    total = len(remaining)
    found = stats["gate_a_matched"] + stats["gate_b_promoted"] + stats["gate_c_found"]
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total processed:   {total}")
    print(f"LinkedIn found:    {found} ({found/total*100:.1f}%)" if total else "")
    print(f"  Gate A (recon):  {stats['gate_a_matched']}")
    print(f"  Gate B (hunter): {stats['gate_b_promoted']}")
    print(f"  Gate C (search): {stats['gate_c_found']} / {stats['gate_c_searched']} searched")
    print(f"Missed:            {stats['missed']}")
    print(f"D1 writes:         {stats['d1_writes']}")
    print(f"CAPTCHAs:          {stats['captcha_count']}")
    print(f"Errors:            {stats['errors']}")
    print(f"Tier upgrades:     FULL={stats['tier_upgrades']['FULL']} REACHABLE={stats['tier_upgrades']['REACHABLE']}")
    print(f"Output:            {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()

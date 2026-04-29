#!/usr/bin/env python3
"""
Process 200 — Find Person v3 (Gate Chain: Recon -> Hunter -> Startpage)

Fills empty slots in slot_workbench with person_first_name, person_last_name.
Three gates checked in order:
  Gate A: Parse recon_name_titles from Process 300. Match title to slot_type. FREE.
  Gate B: Check hunter_first_name/hunter_last_name. Promote if match. FREE.
  Gate C: Startpage natural language search via DataImpulse proxy. CHEAP.

Reads/writes D1 slot_workbench via wrangler subprocess.

Usage:
  python3 find-person-v3.py --limit 50
  python3 find-person-v3.py --limit 100 --offset 200
  python3 find-person-v3.py --limit 50 --dry-run
  python3 find-person-v3.py --resume
  python3 find-person-v3.py --port-base 10100

Env vars: PROXY_USER, PROXY_PASS
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

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS (Bedrock-validated — survive IMO + CTB + Circle)
# ═══════════════════════════════════════════════════════════════════

# Title matching patterns — LOCKED. These map search result titles to slot types.
TITLE_PATTERNS = {
    "CEO": [
        "ceo", "chief executive", "president", "owner", "founder",
        "managing director", "managing partner", "principal",
        "general manager", "executive director",
    ],
    "CFO": [
        "cfo", "chief financial", "finance director", "vp finance",
        "controller", "comptroller", "treasurer",
    ],
    "HR": [
        "hr", "human resource", "benefits", "people officer",
        "chief people", "talent", "personnel", "chro",
    ],
}

# Query templates for Startpage — natural language = zero CAPTCHA
QUERY_TEMPLATES = {
    "CEO": [
        "{company} {city} {state} CEO president owner leadership",
    ],
    "CFO": [
        "{company} {city} {state} CFO controller finance director",
    ],
    "HR": [
        "{company} {city} {state} HR director human resources benefits manager",
    ],
    "CEO_SMALL": [
        "{company} {city} {state} owner manager contact",
    ],
}

# Readiness tier progression (constant — the structure)
TIER_PROGRESSION = {
    "EMPTY": "NAME_ONLY",
    "PATTERN_READY": "NAME_ONLY",
    "HUNTER_READY": "NAME_ONLY",
}

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get(
    "WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"),
)

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"

SEARCH_DELAY = 3  # seconds between Startpage queries
PORT_ROTATION_INTERVAL = 50  # rotate proxy port every N queries

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Bad names — things that get parsed as names but aren't people
BAD_NAMES = {
    "linkedin", "read more", "learn more", "click here", "see more",
    "view all", "sign in", "log in", "join now", "contact us",
    "about us", "our team", "our story", "home page", "main menu",
    "seven days", "privacy policy", "terms of", "cookie policy",
    "glassdoor", "indeed", "yelp", "facebook", "twitter",
}


# ═══════════════════════════════════════════════════════════════════
# ARGS
# ═══════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════
# D1 ACCESS (subprocess wrangler)
# ═══════════════════════════════════════════════════════════════════

def d1_query(sql):
    """Execute a D1 query and return rows."""
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql, "--json"],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120,
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
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120,
    )
    return result.returncode == 0


def esc(s):
    """SQL-escape a string value. None -> NULL."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ═══════════════════════════════════════════════════════════════════
# TITLE MATCHING (Gate A & Gate C shared logic)
# ═══════════════════════════════════════════════════════════════════

def title_matches_slot(title_text, slot_type):
    """Check if a title string matches the expected slot type."""
    if not title_text:
        return False
    lower = title_text.lower()
    patterns = TITLE_PATTERNS.get(slot_type, [])
    return any(p in lower for p in patterns)


def find_best_match_in_organized(organized_json, slot_type, employees=0):
    """
    Gate A (primary): Parse recon_organized_people from 300 Organizer.
    Format: [{"name": str, "context": str, "bucket": "CEO"|"CFO"|"HR"|"REJECT", "confidence": int}]
    Already classified by Title Classifier — just match bucket to slot_type.

    Three passes (cheapest/most confident first):
      1. Exact bucket match with confidence >= 60
      2. Exact bucket match with any confidence
      3. REJECT-bucket person at small companies (<50 emp) for CEO slots only
         (small company + valid name + LinkedIn context = likely the owner)

    Returns {"name": str, "title": str} or None.
    """
    if not organized_json:
        return None
    try:
        entries = json.loads(organized_json) if isinstance(organized_json, str) else organized_json
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(entries, list):
        return None

    try:
        emp = int(employees) if employees else 0
    except (ValueError, TypeError):
        emp = 0

    # Pass 1: exact bucket match with confidence >= 60
    for entry in entries:
        bucket = entry.get("bucket", "REJECT")
        confidence = entry.get("confidence", 0)
        name = entry.get("name", "").strip()
        context = entry.get("context", "")

        if bucket == slot_type and confidence >= 60 and name and _valid_name(name):
            return {"name": name, "title": context}

    # Pass 2: exact bucket match with any confidence
    for entry in entries:
        bucket = entry.get("bucket", "REJECT")
        name = entry.get("name", "").strip()
        context = entry.get("context", "")

        if bucket == slot_type and name and _valid_name(name):
            return {"name": name, "title": context}

    # Pass 3: REJECT-bucket person promotion for small company CEO slots
    # Rationale: small company (<50 emp), valid person name, found via LinkedIn
    # context — this is almost always the owner/decision maker.
    # Only CEO slots — CFO/HR at small companies are rarely findable online.
    if slot_type == "CEO" and emp < 50:
        for entry in entries:
            classification = entry.get("classification", "")
            name = entry.get("name", "").strip()
            context = entry.get("context", "")

            # Must be classified as a person (not garbage), just missing title
            if classification in ("person", "person_with_title") and name and _valid_name(name):
                return {"name": name, "title": context}

    return None


def find_best_match_in_recon(recon_json, slot_type):
    """
    Gate A (fallback): Parse raw recon_name_titles JSON if organized data unavailable.
    recon_name_titles format: [{"name": "John Smith", "context": "CEO at Company - LinkedIn"}, ...]
    Returns {"name": str, "title": str} or None.
    """
    if not recon_json:
        return None
    try:
        entries = json.loads(recon_json) if isinstance(recon_json, str) else recon_json
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(entries, list):
        return None

    for entry in entries:
        name = entry.get("name", "")
        # Support both old "title" key and new "context" key
        title = entry.get("title", "") or entry.get("context", "")
        if name and title_matches_slot(title, slot_type):
            return {"name": name.strip(), "title": title.strip()}
    return None


# ═══════════════════════════════════════════════════════════════════
# PROXY & SEARCH (Gate C)
# ═══════════════════════════════════════════════════════════════════

def get_proxy_url(port):
    """Build DataImpulse proxy URL with port rotation."""
    if not PROXY_USER or not PROXY_PASS:
        raise RuntimeError("PROXY_USER and PROXY_PASS env vars required for Gate C")
    return f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"


def search_startpage(session, query, proxy_url):
    """
    Search Startpage with natural language query.
    Returns dict with names, linkedin_urls, captcha flag.
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
        return {"error": str(e)[:100], "captcha": False, "names": [], "linkedin_urls": []}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "captcha": False, "names": [], "linkedin_urls": []}

    html = resp.text
    captcha = "captcha" in html.lower()

    # Extract LinkedIn URLs
    linkedin_urls = list(set(re.findall(
        r'href="(https://(?:www\.)?linkedin\.com/in/[^"?]+)',
        html, re.IGNORECASE,
    )))

    names = []

    # Method 1: Parse "Name - Title - LinkedIn" from result titles near LinkedIn URLs
    for url in linkedin_urls:
        url_idx = html.find(url)
        if url_idx < 0:
            continue
        chunk = html[url_idx:url_idx + 2000]

        # "Name - Something - LinkedIn" pattern
        title_matches = re.findall(
            r'>([A-Z][a-z]+(?:\s[A-Z]\.?\s*)?(?:\s[A-Z][a-z]+){1,3})\s*[-\u2013]\s*([^<]+?)(?:\s*[-\u2013]\s*LinkedIn)',
            chunk,
        )
        if title_matches:
            name = title_matches[0][0].strip()
            title = title_matches[0][1].strip()
            if _valid_name(name):
                names.append({"name": name, "title": title, "linkedin_url": url})
                continue

        # Fallback: derive from LinkedIn slug (john-smith-123 -> John Smith)
        slug = url.rstrip("/").split("/in/")[-1] if "/in/" in url else ""
        slug_clean = re.sub(r"-[a-f0-9]{4,}$", "", slug)
        slug_clean = re.sub(r"-\d{2,}$", "", slug_clean)
        slug_clean = re.sub(r"%[0-9A-Fa-f]{2}", "", slug_clean)
        slug_parts = slug_clean.split("-")
        if 2 <= len(slug_parts) <= 4:
            derived = " ".join(p.capitalize() for p in slug_parts if len(p) > 1)
            if _valid_name(derived):
                names.append({"name": derived, "title": "", "linkedin_url": url})

    # Method 2: Names near title keywords in any result text
    title_names = re.findall(
        r'>([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*[-\u2013|,]\s*'
        r'(?:CEO|CFO|Chief|Director|VP|Head|President|Founder|Owner|Controller|HR|Human)',
        html,
    )
    for tn in title_names:
        if _valid_name(tn) and not any(n["name"].lower() == tn.lower() for n in names):
            names.append({"name": tn, "title": "", "linkedin_url": ""})

    return {
        "captcha": captcha,
        "names": names,
        "linkedin_urls": linkedin_urls,
        "result_count": len(re.findall(r'class="result', html)),
    }


def _valid_name(name):
    """Validate extracted name is a real person name."""
    if not name or len(name) < 4 or len(name) > 50:
        return False
    lower = name.lower()
    if lower in BAD_NAMES or any(bad in lower for bad in BAD_NAMES):
        return False
    if len(name.split()) < 2:
        return False
    if not name[0].isupper():
        return False
    if any(c in name for c in ["@", "http", ".com", "/", "\\", "<", ">"]):
        return False
    return True


# ═══════════════════════════════════════════════════════════════════
# SLOT UPDATE (shared across all gates)
# ═══════════════════════════════════════════════════════════════════

def split_name(full_name):
    """Split a full name into first and last."""
    parts = full_name.strip().split(" ", 1)
    first = parts[0] if parts else ""
    last = parts[1] if len(parts) > 1 else ""
    return first, last


def update_slot(slot, first, last, full, source, linkedin_url=None):
    """
    Build and execute the UPDATE for a filled slot.
    Process 200 fills NAME only. Email discovery is Process 201's job.
    Tier is NOT set here — it's computed by recalc_tier after the write.
    Returns True on success.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    slot_id = slot["slot_id"]

    set_parts = [
        f"person_first_name = {esc(first)}",
        f"person_last_name = {esc(last)}",
        f"person_full_name = {esc(full)}",
        f"person_source = {esc(source)}",
        f"has_name = 1",
        f"person_found_at = {esc(now)}",
        f"person_last_checked_at = {esc(now)}",
        f"person_changed = 1",
    ]

    if linkedin_url:
        set_parts.append(f"person_linkedin = {esc(linkedin_url)}")
        set_parts.append(f"has_linkedin = 1")
        set_parts.append(f"linkedin_found_at = {esc(now)}")

    # No tier set here — recalc_tier runs after all writes

    sql = f"UPDATE slot_workbench SET {', '.join(set_parts)} WHERE slot_id = {esc(slot_id)}"
    return d1_execute(sql)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Process 200 - Find Person v3 (Gate Chain)")
    print(f"Limit: {LIMIT or 'ALL'} | Offset: {OFFSET} | Dry-run: {DRY_RUN} | Resume: {RESUME}")
    print(f"Port base: {PORT_BASE}")
    print("=" * 60)

    # ── 1. Load empty slots from slot_workbench ──────────────────
    where = "has_name = 0 AND readiness_tier IN ('EMPTY','PATTERN_READY','HUNTER_READY')"
    sql = (
        f"SELECT slot_id, outreach_id, company_unique_id, slot_type, "
        f"company_name, city, state, domain, company_domain, employees, "
        f"recon_name_titles, recon_linkedin_people, recon_organized_people, "
        f"hunter_first_name, hunter_last_name, hunter_title, hunter_email, hunter_linkedin, "
        f"hunter_email_pattern, vendor_email_pattern, "
        f"readiness_tier "
        f"FROM slot_workbench "
        f"WHERE {where} "
        f"ORDER BY outreach_id"
    )
    if LIMIT:
        sql += f" LIMIT {LIMIT}"
    if OFFSET:
        sql += f" OFFSET {OFFSET}"

    print("\nLoading empty slots from slot_workbench...")
    slots = d1_query(sql)
    if not slots:
        print("No empty slots found. Done.")
        return

    print(f"Loaded {len(slots)} empty slots")

    # ── Resume support ───────────────────────────────────────────
    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"find-person-v3-{run_date}.jsonl"

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

    # ── Counters ─────────────────────────────────────────────────
    stats = {
        "gate_a_filled": 0,
        "gate_b_filled": 0,
        "gate_c_filled": 0,
        "gate_c_searched": 0,
        "captcha_count": 0,
        "missed": 0,
        "d1_writes": 0,
        "linkedin_found": 0,
        "errors": 0,
    }

    # ── Session for Gate C ───────────────────────────────────────
    session = None
    current_port = PORT_BASE

    out = open(output_file, "a")
    start_time = time.time()

    for idx, slot in enumerate(remaining):
        slot_id = slot["slot_id"]
        slot_type = slot["slot_type"]
        company_name = slot.get("company_name") or ""
        city = slot.get("city") or ""
        state = slot.get("state") or ""
        employees = slot.get("employees") or 0

        record = {
            "slot_id": slot_id,
            "outreach_id": slot.get("outreach_id"),
            "slot_type": slot_type,
            "company_name": company_name,
            "gate": None,
            "person_name": None,
            "person_title": None,
            "linkedin_url": None,
            "result": "miss",
        }

        filled = False

        # ── Gate A: Organized recon from 300 Organizer (primary), raw recon (fallback)
        organized = slot.get("recon_organized_people")
        recon = slot.get("recon_name_titles")
        if (organized or recon) and not filled:
            # Try organized data first (already classified by Title Classifier)
            match = find_best_match_in_organized(organized, slot_type, employees=slot.get("employees", 0)) if organized else None
            # Fall back to raw recon if organized didn't match
            if not match and recon:
                match = find_best_match_in_recon(recon, slot_type)
            if match:
                first, last = split_name(match["name"])
                if first and last:
                    if update_slot(slot, first, last, match["name"], "recon_300"):
                        stats["gate_a_filled"] += 1
                        stats["d1_writes"] += 1
                        record["gate"] = "A"
                        record["person_name"] = match["name"]
                        record["person_title"] = match["title"]
                        record["result"] = "filled"
                        filled = True

        # ── Gate B: Hunter candidate data ────────────────────────
        if not filled:
            h_first = slot.get("hunter_first_name") or ""
            h_last = slot.get("hunter_last_name") or ""
            h_title = slot.get("hunter_title") or ""

            if h_first and h_last and title_matches_slot(h_title, slot_type):
                full = f"{h_first} {h_last}"
                h_linkedin = slot.get("hunter_linkedin")
                # NOTE: Do not pass hunter_email here — email is 201's job
                if update_slot(slot, h_first, h_last, full, "hunter",
                               linkedin_url=h_linkedin):
                    stats["gate_b_filled"] += 1
                    stats["d1_writes"] += 1
                    record["gate"] = "B"
                    record["person_name"] = full
                    record["person_title"] = h_title
                    record["linkedin_url"] = h_linkedin
                    record["result"] = "filled"
                    filled = True

        # ── Gate C: Startpage search ─────────────────────────────
        if not filled and company_name:
            if not PROXY_USER or not PROXY_PASS:
                record["result"] = "no_proxy_creds"
                stats["errors"] += 1
            else:
                # Lazy init session
                if session is None:
                    session = creq.Session(impersonate="chrome131")

                # Port rotation
                if stats["gate_c_searched"] > 0 and stats["gate_c_searched"] % PORT_ROTATION_INTERVAL == 0:
                    current_port = PORT_BASE + (stats["gate_c_searched"] // PORT_ROTATION_INTERVAL)
                    session = creq.Session(impersonate="chrome131")  # fresh session on port rotate

                proxy_url = get_proxy_url(current_port)

                # Pick query template based on employee count
                try:
                    emp = int(employees)
                except (ValueError, TypeError):
                    emp = 0

                if emp > 0 and emp < 25:
                    templates = QUERY_TEMPLATES.get("CEO_SMALL", QUERY_TEMPLATES.get(slot_type, []))
                else:
                    templates = QUERY_TEMPLATES.get(slot_type, QUERY_TEMPLATES["CEO"])

                best = None
                for template in templates:
                    query = template.format(company=company_name, city=city, state=state)
                    result = search_startpage(session, query, proxy_url)
                    stats["gate_c_searched"] += 1

                    if result.get("captcha"):
                        stats["captcha_count"] += 1
                        time.sleep(5)
                        continue

                    if result.get("names"):
                        best = result
                        best["query"] = query
                        break

                    time.sleep(SEARCH_DELAY)

                if best and best.get("names"):
                    person = best["names"][0]
                    first, last = split_name(person["name"])
                    li_url = person.get("linkedin_url") or (
                        best["linkedin_urls"][0] if best.get("linkedin_urls") else None
                    )
                    if first and last:
                        if update_slot(slot, first, last, person["name"], "startpage_v3",
                                       linkedin_url=li_url):
                            stats["gate_c_filled"] += 1
                            stats["d1_writes"] += 1
                            record["gate"] = "C"
                            record["person_name"] = person["name"]
                            record["person_title"] = person.get("title", "")
                            record["linkedin_url"] = li_url
                            record["result"] = "filled"
                            filled = True

                # Delay between searches
                if not filled:
                    time.sleep(SEARCH_DELAY + random.uniform(0, 1))

        if not filled:
            stats["missed"] += 1

        # Track LinkedIn finds across all gates
        if record.get("linkedin_url"):
            stats["linkedin_found"] += 1

        # Write output
        out.write(json.dumps(record) + "\n")
        out.flush()

        # Progress report every 25 slots
        if (idx + 1) % 25 == 0 or idx == len(remaining) - 1:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            total_filled = stats["gate_a_filled"] + stats["gate_b_filled"] + stats["gate_c_filled"]
            print(
                f"  [{idx+1}/{len(remaining)}] "
                f"A:{stats['gate_a_filled']} B:{stats['gate_b_filled']} C:{stats['gate_c_filled']} "
                f"Miss:{stats['missed']} CAPTCHA:{stats['captcha_count']} "
                f"LI:{stats['linkedin_found']} D1:{stats['d1_writes']} "
                f"| {rate:.0f}/hr"
            )

        # ── STOP CONDITION: CAPTCHA > 10% of Gate C searches ────
        if stats["gate_c_searched"] > 20 and stats["captcha_count"] / stats["gate_c_searched"] > 0.10:
            print(f"\nSTOP: CAPTCHA rate {stats['captcha_count']}/{stats['gate_c_searched']} > 10%. Halting.")
            break

        # ── STOP CONDITION: errors > 5% ─────────────────────────
        total_processed = idx + 1
        if total_processed > 20 and stats["errors"] / total_processed > 0.05:
            print(f"\nSTOP: Error rate > 5%. Halting.")
            break

    out.close()
    elapsed_min = (time.time() - start_time) / 60
    total_filled = stats["gate_a_filled"] + stats["gate_b_filled"] + stats["gate_c_filled"]

    print("\n" + "=" * 60)
    print(f"DONE in {elapsed_min:.1f}m")
    print(f"  Gate A (recon):     {stats['gate_a_filled']} filled")
    print(f"  Gate B (hunter):    {stats['gate_b_filled']} filled")
    print(f"  Gate C (startpage): {stats['gate_c_filled']} filled ({stats['gate_c_searched']} searched)")
    print(f"  Total filled:       {total_filled}")
    print(f"  Missed:             {stats['missed']}")
    print(f"  LinkedIn found:     {stats['linkedin_found']}")
    print(f"  D1 writes:          {stats['d1_writes']}")
    print(f"  CAPTCHA hits:       {stats['captcha_count']}")
    if total_filled + stats["missed"] > 0:
        print(f"  Hit rate:           {total_filled / (total_filled + stats['missed']) * 100:.1f}%")
    print(f"  Output:             {output_file}")
    print("=" * 60)

    # Recalculate tiers from actual state — not hardcoded by this process
    print("\nRecalculating tiers...")
    from recalc_tier import recalc_tier_all
    recalc_tier_all()
    print("Tiers recalculated.")


if __name__ == "__main__":
    main()

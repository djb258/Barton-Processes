"""
Process 200 — FUNNEL (All Gates, Correct Order)

Runs every free option before touching the proxy. Each layer reports its fills.
What's left after all free layers → Gate C (Startpage search).

FUNNEL ORDER:
  Layer 1: CEO promotion — any valid person → CEO slot (no title match required)
  Layer 2: Cross-company recon — promote organized people to matching slot types
           (CEO bucket → CEO slot, HR bucket → HR slot, CFO bucket → CFO slot)
  Layer 3: Hunter promote — hunter_first_name + title match to slot_type
  Layer 4: LinkedIn slug → name derivation (for slots with recon_linkedin_people)
  Layer 5: Gate C — Startpage search (proxy cost, 3s/query)

Usage:
  python3 funnel.py --limit 100         # test first 100
  python3 funnel.py --layers 1,2,3,4    # free layers only
  python3 funnel.py --layers 1,2,3,4,5  # full funnel including Gate C
  python3 funnel.py                     # all layers, all slots
  python3 funnel.py --dry-run           # report only

Env vars: PROXY_USER, PROXY_PASS (only needed for Layer 5)
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

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"

LIMIT = 0
DRY_RUN = False
LAYERS = "1,2,3,4,5"
PAGE_SIZE = 500
WRITE_BATCH = 50
PORT_BASE = 11500
SEARCH_DELAY = 3
PORT_ROTATION = 50

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Title patterns
TITLE_PATTERNS = {
    "CEO": ["ceo", "chief executive", "president", "owner", "founder",
            "managing director", "managing partner", "principal",
            "general manager", "executive director"],
    "CFO": ["cfo", "chief financial", "finance director", "vp finance",
            "controller", "comptroller", "treasurer"],
    "HR":  ["hr", "human resource", "benefits", "people officer",
            "chief people", "talent", "personnel", "chro"],
}

BAD_NAMES = {
    "linkedin", "read more", "learn more", "click here", "see more",
    "view all", "sign in", "log in", "join now", "contact us",
    "about us", "our team", "glassdoor", "indeed", "yelp", "facebook",
    "twitter", "privacy policy", "terms of", "cookie policy",
    "home page", "main menu", "our story",
}

# ── Args ─────────────────────────────────────────────────────

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
    elif args[i] == "--layers" and i + 1 < len(args):
        LAYERS = args[i + 1]; i += 2
    elif args[i] == "--port-base" and i + 1 < len(args):
        PORT_BASE = int(args[i + 1]); i += 2
    elif args[i] == "--dry-run":
        DRY_RUN = True; i += 1
    else:
        i += 1

active_layers = set(int(x) for x in LAYERS.split(","))


# ── D1 ───────────────────────────────────────────────────────

def d1_query(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    if result.returncode != 0: return []
    try:
        start = result.stdout.find('[')
        if start < 0: return []
        data = json.loads(result.stdout[start:])
        return data[0].get("results", []) if data else []
    except: return []

def d1_execute(sql):
    if DRY_RUN: return True
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    return result.returncode == 0

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ── Helpers ──────────────────────────────────────────────────

def valid_name(name):
    if not name or len(name) < 4 or len(name) > 50: return False
    lower = name.lower()
    if any(bad in lower for bad in BAD_NAMES): return False
    parts = name.split()
    if len(parts) < 2: return False
    if not parts[0][0].isupper() or not parts[-1][0].isupper(): return False
    if any(c in name for c in ["@", "http", ".com", "/", "\\", "<", ">"]): return False
    # Reject if any word > 3 chars is ALL CAPS (company name)
    for p in parts:
        if len(p) > 3 and p.isupper(): return False
    return True

def title_matches(title_text, slot_type):
    if not title_text: return False
    lower = title_text.lower()
    return any(p in lower for p in TITLE_PATTERNS.get(slot_type, []))

def split_name(full_name):
    parts = full_name.strip().split(" ", 1)
    return (parts[0], parts[1] if len(parts) > 1 else "")

def write_slot(slot_id, first, last, source, linkedin_url=None):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    full = f"{first} {last}"
    parts = [
        f"person_first_name = {esc(first)}",
        f"person_last_name = {esc(last)}",
        f"person_full_name = {esc(full)}",
        f"person_source = {esc(source)}",
        f"has_name = 1",
        f"person_found_at = {esc(now)}",
        f"readiness_tier = 'NAME_ONLY'",
    ]
    if linkedin_url:
        parts.append(f"person_linkedin = {esc(linkedin_url)}")
        parts.append(f"has_linkedin = 1")
        parts.append(f"linkedin_found_at = {esc(now)}")
    return f"UPDATE slot_workbench SET {', '.join(parts)} WHERE slot_id = {esc(slot_id)}"


# ── Layer 1: CEO Promotion ───────────────────────────────────
# Any valid person name → CEO slot. If recon found someone at this company,
# and no one got the CEO tag, this person is the decision maker.

def layer_1():
    print("\n" + "=" * 60)
    print("LAYER 1: CEO Promotion (any valid person → CEO slot)")
    print("=" * 60)

    processed = 0
    filled = 0
    total = LIMIT if LIMIT else 999999

    while processed < total:
        page = min(PAGE_SIZE, total - processed)
        rows = d1_query(f"""
            SELECT slot_id, outreach_id, recon_organized_people
            FROM slot_workbench
            WHERE has_name = 0 AND slot_type = 'CEO'
            AND recon_organized_people IS NOT NULL AND recon_organized_people != '[]'
            ORDER BY outreach_id LIMIT {page}
        """)
        if not rows: break

        batch = []
        for row in rows:
            try:
                entries = json.loads(row["recon_organized_people"])
            except: continue

            # Take first valid person name regardless of bucket
            promoted = None
            # Priority: CEO bucket first, then any person
            for e in entries:
                if e.get("bucket") == "CEO" and valid_name(e.get("name", "")):
                    promoted = e; break
            if not promoted:
                for e in entries:
                    if e.get("classification") in ("person", "person_with_title") and valid_name(e.get("name", "")):
                        promoted = e; break

            if promoted:
                first, last = split_name(promoted["name"])
                if first and last:
                    batch.append(write_slot(row["slot_id"], first, last, "funnel_L1_ceo_promote"))
                    filled += 1

            if len(batch) >= WRITE_BATCH:
                d1_execute("; ".join(batch))
                batch = []

        if batch:
            d1_execute("; ".join(batch))

        processed += len(rows)
        print(f"  [{processed}] filled={filled}")

        if len(rows) < page: break

    print(f"  LAYER 1 RESULT: {filled} CEO slots promoted")
    return filled


# ── Layer 2: Cross-slot bucket match ─────────────────────────
# For CFO/HR slots: promote organized people that match the slot's bucket exactly.

def layer_2():
    print("\n" + "=" * 60)
    print("LAYER 2: Bucket Match (organized people → matching slot type)")
    print("=" * 60)

    processed = 0
    filled = 0
    total = LIMIT if LIMIT else 999999

    while processed < total:
        page = min(PAGE_SIZE, total - processed)
        rows = d1_query(f"""
            SELECT slot_id, slot_type, recon_organized_people
            FROM slot_workbench
            WHERE has_name = 0
            AND recon_organized_people IS NOT NULL AND recon_organized_people != '[]'
            ORDER BY outreach_id LIMIT {page}
        """)
        if not rows: break

        batch = []
        for row in rows:
            try:
                entries = json.loads(row["recon_organized_people"])
            except: continue

            slot_type = row["slot_type"]
            for e in entries:
                if e.get("bucket") == slot_type and valid_name(e.get("name", "")):
                    first, last = split_name(e["name"])
                    if first and last:
                        batch.append(write_slot(row["slot_id"], first, last, f"funnel_L2_{slot_type.lower()}_match"))
                        filled += 1
                        break

            if len(batch) >= WRITE_BATCH:
                d1_execute("; ".join(batch))
                batch = []

        if batch:
            d1_execute("; ".join(batch))

        processed += len(rows)
        print(f"  [{processed}] filled={filled}")

        if len(rows) < page: break

    print(f"  LAYER 2 RESULT: {filled} slots matched by bucket")
    return filled


# ── Layer 3: Hunter Promote ──────────────────────────────────
# Hunter candidate data: first_name + last_name + title → slot match

def layer_3():
    print("\n" + "=" * 60)
    print("LAYER 3: Hunter Promote (hunter candidate → slot type match)")
    print("=" * 60)

    processed = 0
    filled = 0
    total = LIMIT if LIMIT else 999999

    while processed < total:
        page = min(PAGE_SIZE, total - processed)
        rows = d1_query(f"""
            SELECT slot_id, slot_type, hunter_first_name, hunter_last_name,
                   hunter_title, hunter_linkedin
            FROM slot_workbench
            WHERE has_name = 0
            AND hunter_first_name IS NOT NULL AND hunter_first_name != ''
            ORDER BY outreach_id LIMIT {page}
        """)
        if not rows: break

        batch = []
        for row in rows:
            h_first = (row.get("hunter_first_name") or "").strip()
            h_last = (row.get("hunter_last_name") or "").strip()
            h_title = row.get("hunter_title") or ""

            if h_first and h_last and title_matches(h_title, row["slot_type"]):
                li = row.get("hunter_linkedin")
                batch.append(write_slot(row["slot_id"], h_first, h_last, "funnel_L3_hunter", linkedin_url=li))
                filled += 1

            if len(batch) >= WRITE_BATCH:
                d1_execute("; ".join(batch))
                batch = []

        if batch:
            d1_execute("; ".join(batch))

        processed += len(rows)
        print(f"  [{processed}] filled={filled}")

        if len(rows) < page: break

    print(f"  LAYER 3 RESULT: {filled} hunter promotions")
    return filled


# ── Layer 4: LinkedIn Slug → Name ────────────────────────────
# Parse LinkedIn slugs to derive person names for CEO slots

def layer_4():
    print("\n" + "=" * 60)
    print("LAYER 4: LinkedIn Slug → Name (derive names from /in/ URLs)")
    print("=" * 60)

    processed = 0
    filled = 0
    total = LIMIT if LIMIT else 999999

    while processed < total:
        page = min(PAGE_SIZE, total - processed)
        rows = d1_query(f"""
            SELECT slot_id, slot_type, outreach_id, company_name,
                   recon_organized_linkedin, recon_linkedin_people
            FROM slot_workbench
            WHERE has_name = 0 AND slot_type = 'CEO'
            AND (recon_organized_linkedin IS NOT NULL AND recon_organized_linkedin != '[]'
                 OR recon_linkedin_people IS NOT NULL AND recon_linkedin_people != '' AND recon_linkedin_people != '[]')
            ORDER BY outreach_id LIMIT {page}
        """)
        if not rows: break

        batch = []
        for row in rows:
            company = (row.get("company_name") or "").lower()
            urls = []

            # Get LinkedIn URLs from organized or raw
            for field in ["recon_organized_linkedin", "recon_linkedin_people"]:
                raw = row.get(field)
                if raw:
                    try:
                        entries = json.loads(raw) if isinstance(raw, str) else raw
                        if isinstance(entries, list):
                            for e in entries:
                                if isinstance(e, dict):
                                    urls.append(e.get("name", "") or e.get("url", ""))
                                elif isinstance(e, str):
                                    urls.append(e)
                    except: pass

            # Try to derive a name from LinkedIn slug
            for url in urls:
                if "/in/" not in url: continue
                slug = url.rstrip("/").split("/in/")[-1]
                # Strip trailing hex/numeric IDs
                slug = re.sub(r'-[a-f0-9]{6,}$', '', slug)
                slug = re.sub(r'-\d{3,}$', '', slug)
                slug = re.sub(r'%[0-9A-Fa-f]{2}', '', slug)
                parts = [p for p in slug.split("-") if len(p) > 1]

                if 2 <= len(parts) <= 3:
                    derived = " ".join(p.capitalize() for p in parts)
                    # Skip if it looks like the company name
                    if company:
                        overlap = len(set(p.lower() for p in parts) & set(company.split()))
                        if overlap > len(parts) * 0.5:
                            continue
                    if valid_name(derived):
                        first, last = split_name(derived)
                        if first and last:
                            batch.append(write_slot(row["slot_id"], first, last,
                                                    "funnel_L4_slug_derive", linkedin_url=url))
                            filled += 1
                            break

            if len(batch) >= WRITE_BATCH:
                d1_execute("; ".join(batch))
                batch = []

        if batch:
            d1_execute("; ".join(batch))

        processed += len(rows)
        print(f"  [{processed}] filled={filled}")

        if len(rows) < page: break

    print(f"  LAYER 4 RESULT: {filled} names derived from LinkedIn slugs")
    return filled


# ── Layer 5: Gate C — Startpage Search ───────────────────────
# The expensive layer. Only runs on what's left.

def layer_5():
    print("\n" + "=" * 60)
    print("LAYER 5: Gate C — Startpage Search (proxy cost)")
    print("=" * 60)

    if not PROXY_USER or not PROXY_PASS:
        print("  SKIP: No proxy credentials (PROXY_USER/PROXY_PASS)")
        return 0

    # Count remaining
    count = d1_query("SELECT COUNT(*) as cnt FROM slot_workbench WHERE has_name = 0")
    remaining = count[0]["cnt"] if count else 0
    target = min(LIMIT, remaining) if LIMIT else remaining
    print(f"  {remaining} slots still empty, processing {target}")

    if target == 0:
        print("  Nothing to search.")
        return 0

    filled = 0
    searched = 0
    captchas = 0
    processed = 0
    session = creq.Session(impersonate="chrome131")
    current_port = PORT_BASE

    while processed < target:
        page = min(PAGE_SIZE, target - processed)
        rows = d1_query(f"""
            SELECT slot_id, slot_type, company_name, city, state, employees
            FROM slot_workbench
            WHERE has_name = 0
            ORDER BY outreach_id LIMIT {page}
        """)
        if not rows: break

        batch = []
        for row in rows:
            slot_type = row["slot_type"]
            company = row.get("company_name") or ""
            city = row.get("city") or ""
            state = row.get("state") or ""
            emp = 0
            try: emp = int(row.get("employees") or 0)
            except: pass

            if not company: continue

            # Port rotation
            if searched > 0 and searched % PORT_ROTATION == 0:
                current_port += 1
                session = creq.Session(impersonate="chrome131")

            # Build query
            if slot_type == "CEO" and emp > 0 and emp < 25:
                query = f"{company} {city} {state} owner manager contact"
            elif slot_type == "CEO":
                query = f"{company} {city} {state} CEO president owner leadership"
            elif slot_type == "CFO":
                query = f"{company} {city} {state} CFO controller finance director"
            else:
                query = f"{company} {city} {state} HR director human resources benefits manager"

            proxy_url = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{current_port}"

            try:
                resp = session.post(
                    "https://www.startpage.com/do/dsearch",
                    data={"q": query},
                    proxies={"http": proxy_url, "https": proxy_url},
                    timeout=30, allow_redirects=True, impersonate="chrome131")
            except Exception as e:
                time.sleep(SEARCH_DELAY)
                continue

            searched += 1
            html = resp.text if resp.status_code == 200 else ""

            if "captcha" in html.lower():
                captchas += 1
                if searched > 20 and captchas / searched > 0.10:
                    print(f"\n  STOP: CAPTCHA rate {captchas}/{searched} > 10%")
                    break
                time.sleep(5)
                continue

            # Extract names near LinkedIn URLs or title keywords
            li_urls = list(set(re.findall(r'href="(https://(?:www\.)?linkedin\.com/in/[^"?]+)', html, re.I)))
            best_name = None
            best_li = None

            for url in li_urls:
                idx = html.find(url)
                if idx < 0: continue
                chunk = html[idx:idx+2000]
                matches = re.findall(
                    r'>([A-Z][a-z]+(?:\s[A-Z]\.?\s*)?(?:\s[A-Z][a-z]+){1,3})\s*[-\u2013]\s*([^<]+?)(?:\s*[-\u2013]\s*LinkedIn)',
                    chunk)
                if matches:
                    name, title = matches[0][0].strip(), matches[0][1].strip()
                    if valid_name(name) and title_matches(title, slot_type):
                        best_name = name; best_li = url; break
                    elif valid_name(name) and slot_type == "CEO":
                        best_name = name; best_li = url  # CEO gets any valid person

                if not best_name:
                    slug = url.rstrip("/").split("/in/")[-1]
                    slug = re.sub(r'-[a-f0-9]{4,}$', '', slug)
                    slug = re.sub(r'-\d{2,}$', '', slug)
                    parts = [p for p in slug.split("-") if len(p) > 1]
                    if 2 <= len(parts) <= 3:
                        derived = " ".join(p.capitalize() for p in parts)
                        if valid_name(derived):
                            best_name = derived; best_li = url

            # Fallback: names near title keywords
            if not best_name:
                title_names = re.findall(
                    r'>([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*[-\u2013|,]\s*'
                    r'(?:CEO|CFO|Chief|Director|VP|Head|President|Founder|Owner|Controller|HR|Human)',
                    html)
                for tn in title_names:
                    if valid_name(tn):
                        best_name = tn; break

            if best_name:
                first, last = split_name(best_name)
                if first and last:
                    batch.append(write_slot(row["slot_id"], first, last,
                                           "funnel_L5_startpage", linkedin_url=best_li))
                    filled += 1

            if len(batch) >= WRITE_BATCH:
                d1_execute("; ".join(batch))
                batch = []

            time.sleep(SEARCH_DELAY + random.uniform(0, 1))

        if batch:
            d1_execute("; ".join(batch))
            batch = []

        processed += len(rows)
        pct = processed / target * 100 if target else 0
        print(f"  [{processed}/{target}] ({pct:.0f}%) filled={filled} searched={searched} captcha={captchas}")

        if len(rows) < page: break

    print(f"  LAYER 5 RESULT: {filled} filled from {searched} searches, {captchas} CAPTCHAs")
    return filled


# ── MAIN ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PROCESS 200 — FUNNEL")
    print(f"Layers: {LAYERS} | Limit: {LIMIT or 'ALL'} | Dry-run: {DRY_RUN}")
    print("=" * 60)

    # Starting count
    count = d1_query("SELECT COUNT(*) as cnt FROM slot_workbench WHERE has_name = 0")
    start_empty = count[0]["cnt"] if count else 0
    print(f"\nStarting empty slots: {start_empty}")

    results = {}

    if 1 in active_layers:
        results["L1_ceo_promote"] = layer_1()
    if 2 in active_layers:
        results["L2_bucket_match"] = layer_2()
    if 3 in active_layers:
        results["L3_hunter"] = layer_3()
    if 4 in active_layers:
        results["L4_slug_derive"] = layer_4()
    if 5 in active_layers:
        results["L5_startpage"] = layer_5()

    # Final count
    count = d1_query("SELECT COUNT(*) as cnt FROM slot_workbench WHERE has_name = 0")
    end_empty = count[0]["cnt"] if count else 0

    total_filled = sum(results.values())

    print("\n" + "=" * 60)
    print("FUNNEL COMPLETE")
    print("=" * 60)
    for layer, fills in results.items():
        cost = "FREE" if "L5" not in layer else "PROXY"
        print(f"  {layer}: {fills} fills [{cost}]")
    print(f"  ─────────────────────────")
    print(f"  Total filled:   {total_filled}")
    print(f"  Started empty:  {start_empty}")
    print(f"  Now empty:      {end_empty}")
    print(f"  Remaining:      {end_empty} ({end_empty/97983*100:.1f}% of all slots)")
    print("=" * 60)

    # Tier snapshot
    tiers = d1_query("SELECT readiness_tier, COUNT(*) as cnt FROM slot_workbench GROUP BY readiness_tier ORDER BY cnt DESC")
    if tiers:
        print("\nWORKBENCH STATE:")
        for t in tiers:
            print(f"  {t['readiness_tier']:15s} {t['cnt']:>6,}")


if __name__ == "__main__":
    main()

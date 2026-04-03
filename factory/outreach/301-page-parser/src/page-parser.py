"""
PROC-301 — Management Page Parser (Key Builder approach)

1. FETCHER    — get the page
2. DECOMPOSER — break into individual pieces
3. KEY BUILDER — identify each piece (person_name, title, email, linkedin, phone, unidentified)
4. QUALITY GATE — validate identified pieces, bad → reclassified as unidentified
5. ORGANIZER  — map identified pieces to output columns, store ALL (including unidentified)
6. SLOT FILLER — query structured table, fill workbench slots

BAR-197 | PROC-301

Usage:
  python3 page-parser.py --limit 100
  python3 page-parser.py --dry-run
  python3 page-parser.py
"""

import json
import re
import sys
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from curl_cffi import requests as creq

# ── Config ───────────────────────────────────────────────────

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"
PORT_BASE = 12000

LIMIT = 0
DRY_RUN = False
FETCH_DELAY = 1

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Title Classifier
CLASSIFIER_DIR = Path(__file__).parent.parent.parent / "tools" / "title-classifier"
sys.path.insert(0, str(CLASSIFIER_DIR))
try:
    from classifier import TitleClassifier
    tc = TitleClassifier()
    HAS_CLASSIFIER = True
except ImportError:
    HAS_CLASSIFIER = False
    print("[WARN] Title Classifier not available")

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1]); i += 2
    elif args[i] == "--port-base" and i + 1 < len(args):
        PORT_BASE = int(args[i + 1]); i += 2
    elif args[i] == "--dry-run":
        DRY_RUN = True; i += 1
    else:
        i += 1


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


# ── IDENTIFICATION RULES ────────────────────────────────────

# Person name: 2-4 capitalized words, no company indicators
COMPANY_WORDS = {
    "inc", "llc", "ltd", "corp", "corporation", "company", "co", "group",
    "services", "solutions", "partners", "associates", "agency", "center",
    "foundation", "institute", "university", "college", "hospital",
    "insurance", "financial", "consulting", "management", "technology",
    "global", "national", "international", "american", "association",
    "read", "more", "learn", "click", "view", "contact", "about",
    "home", "menu", "search", "login", "sign", "privacy", "terms",
    "cookie", "copyright", "all rights", "reserved",
}

TITLE_KEYWORDS = re.compile(
    r'\b(?:CEO|CFO|COO|CTO|CIO|CHRO|CMO|CPO|'
    r'Chief\s+\w+\s+Officer|'
    r'President|Vice\s+President|VP\s|'
    r'Owner|Founder|Co-Founder|Partner|Managing\s+Partner|'
    r'Director|Executive\s+Director|Managing\s+Director|'
    r'Controller|Comptroller|Treasurer|'
    r'Manager|General\s+Manager|'
    r'Head\s+of|Senior\s+Vice|'
    r'Principal|Administrator|Superintendent|'
    r'Human\s+Resource|Benefits|Talent|HR\s+Director|'
    r'Board\s+(?:Member|Chair|of\s+Directors))\b', re.IGNORECASE)

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
LINKEDIN_RE = re.compile(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+')
URL_RE = re.compile(r'https?://[^\s"<>]+')


def identify_text(text, company_name=""):
    """Identify what a piece of text IS. Returns classification + confidence."""
    text = text.strip()
    if not text or len(text) < 2:
        return "empty", 0

    lower = text.lower()

    # Email
    email_match = EMAIL_RE.search(text)
    if email_match and "@" in text and len(text) < 60:
        email = email_match.group()
        if not any(x in email.lower() for x in ['example', 'wix', 'wordpress', 'sentry', 'jquery', 'noreply', 'no-reply']):
            return "email", 95

    # LinkedIn URL
    if LINKEDIN_RE.search(text):
        return "linkedin_url", 95

    # Phone
    if PHONE_RE.search(text) and len(text) < 30:
        return "phone", 80

    # Other URL (not a person)
    if text.startswith("http") and len(text) < 200:
        return "url", 70

    # Title keyword
    if TITLE_KEYWORDS.search(text) and len(text) < 120:
        return "job_title", 85

    # Person name pattern: 2-4 capitalized words
    words = text.split()
    if 2 <= len(words) <= 4 and len(text) < 50:
        all_cap_start = all(w[0].isupper() for w in words if len(w) > 1)
        no_company = not any(w.lower().rstrip('.,;:') in COMPANY_WORDS for w in words)
        no_numbers = not any(c.isdigit() for c in text)
        no_special = not any(c in text for c in ['@', 'http', '/', '\\', '<', '>', '=', '{', '}'])

        # Check against company name
        company_overlap = False
        if company_name:
            co_words = set(company_name.lower().split())
            name_words = set(lower.split())
            if co_words and len(name_words & co_words) / max(len(co_words), 1) > 0.5:
                company_overlap = True

        if all_cap_start and no_company and no_numbers and no_special and not company_overlap:
            return "person_name", 75

    # Short text that might be a role/department
    if len(text) < 50 and any(w in lower for w in ['department', 'team', 'division', 'office', 'branch']):
        return "department", 60

    # Longer text — probably a description or content
    if len(text) > 100:
        return "description", 50

    # Navigation / UI elements
    if lower in ['home', 'about', 'contact', 'services', 'team', 'careers', 'news', 'blog',
                  'products', 'resources', 'support', 'login', 'sign in', 'menu', 'close',
                  'search', 'submit', 'read more', 'learn more', 'view all']:
        return "navigation", 90

    return "unidentified", 0


# ── STEP 1: FETCHER ─────────────────────────────────────────

def fetch_page(url, port):
    """Fetch page. Try direct first, proxy fallback."""
    session = creq.Session(impersonate="chrome131")

    # Try direct
    try:
        resp = session.get(url, timeout=10, allow_redirects=True)
        if resp.status_code == 200 and len(resp.text) > 200:
            return resp.text, resp.status_code
    except:
        pass

    # Proxy fallback
    if PROXY_USER and PROXY_PASS:
        proxy_url = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"
        try:
            resp = session.get(url, proxies={"http": proxy_url, "https": proxy_url},
                              timeout=15, allow_redirects=True, impersonate="chrome131")
            if resp.status_code == 200:
                return resp.text, resp.status_code
            return "", resp.status_code
        except:
            pass

    return "", 0


# ── STEP 2: DECOMPOSER ──────────────────────────────────────

def decompose_page(html):
    """Break HTML into individual text elements with position and context."""
    # Strip scripts, styles, comments
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.I)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    elements = []
    position = 0

    # Extract structured elements

    # Headings (h1-h6)
    for m in re.finditer(r'<(h[1-6])[^>]*>(.*?)</\1>', text, re.DOTALL | re.I):
        tag = m.group(1)
        content = re.sub(r'<[^>]+>', ' ', m.group(2)).strip()
        content = re.sub(r'\s+', ' ', content)
        if content and len(content) > 1:
            elements.append({"position": position, "tag": tag, "text": content, "href": None})
            position += 1

    # Links with text
    for m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', text, re.DOTALL | re.I):
        href = m.group(1)
        content = re.sub(r'<[^>]+>', ' ', m.group(2)).strip()
        content = re.sub(r'\s+', ' ', content)
        if content and len(content) > 1:
            elements.append({"position": position, "tag": "a", "text": content, "href": href})
            position += 1

    # LinkedIn URLs (even without visible text)
    for m in re.finditer(r'href="(https?://(?:www\.)?linkedin\.com/in/[^"?]+)"', text, re.I):
        url = m.group(1)
        already = any(e.get("href") == url for e in elements)
        if not already:
            elements.append({"position": position, "tag": "a", "text": url, "href": url})
            position += 1

    # Email addresses in text
    for m in EMAIL_RE.finditer(text):
        email = m.group()
        already = any(email in e.get("text", "") for e in elements)
        if not already:
            elements.append({"position": position, "tag": "text", "text": email, "href": None})
            position += 1

    # Paragraphs and divs with short text (likely names/titles, not content blocks)
    for m in re.finditer(r'<(?:p|div|span|li|td|th|dt|dd)[^>]*>(.*?)</(?:p|div|span|li|td|th|dt|dd)>', text, re.DOTALL | re.I):
        content = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
        content = re.sub(r'\s+', ' ', content)
        if content and 2 < len(content) < 150:
            already = any(content == e.get("text") for e in elements)
            if not already:
                elements.append({"position": position, "tag": "text", "text": content, "href": None})
                position += 1

    # Image alt text (often has names)
    for m in re.finditer(r'<img[^>]*alt="([^"]{3,80})"', text, re.I):
        alt = m.group(1).strip()
        if alt and not any(x in alt.lower() for x in ['logo', 'icon', 'banner', 'header', 'footer', 'pixel']):
            elements.append({"position": position, "tag": "img_alt", "text": alt, "href": None})
            position += 1

    return elements


# ── STEP 3: KEY BUILDER ─────────────────────────────────────

def build_key(elements, company_name=""):
    """Identify each element. Returns the key for this page."""
    key = []
    for el in elements:
        text = el["text"]
        href = el.get("href")

        # If href is a LinkedIn URL, classify as linkedin regardless of text
        if href and LINKEDIN_RE.match(href):
            classification = "linkedin_url"
            confidence = 95
        else:
            classification, confidence = identify_text(text, company_name)

        # Title classifier boost
        if classification == "person_name" and HAS_CLASSIFIER:
            # Check if adjacent elements have title info
            pass  # Title matching happens in quality gate with context

        key.append({
            "position": el["position"],
            "tag": el["tag"],
            "text": text,
            "href": href,
            "classification": classification,
            "confidence": confidence,
        })

    return key


# ── STEP 4: QUALITY GATE ────────────────────────────────────

def quality_gate(key, company_name=""):
    """Validate identified elements. Bad IDs → reclassified as unidentified."""
    validated = []

    for i, el in enumerate(key):
        cls = el["classification"]

        if cls == "person_name":
            name = el["text"]
            # C&V Question 1: Can you NAME it? Must have first + last
            parts = name.split()
            if len(parts) < 2:
                el["classification"] = "unidentified"
                el["confidence"] = 0

            # C&V Question 2: FORMAT — must be title case or parseable
            elif not parts[0][0].isupper() or not parts[-1][0].isupper():
                el["classification"] = "unidentified"
                el["confidence"] = 0

            # Check for title in nearby elements (boost confidence)
            nearby_title = False
            for j in range(max(0, i-3), min(len(key), i+4)):
                if j != i and key[j]["classification"] == "job_title":
                    nearby_title = True
                    break
            if nearby_title:
                el["confidence"] = min(95, el["confidence"] + 15)

        elif cls == "email":
            email = EMAIL_RE.search(el["text"])
            if email:
                addr = email.group()
                # Reject generic emails
                local = addr.split("@")[0].lower()
                if local in ["info", "contact", "admin", "support", "hello", "office", "sales", "hr",
                             "careers", "jobs", "team", "general", "enquiries", "mail", "help"]:
                    el["classification"] = "generic_email"
                    el["confidence"] = 40

        elif cls == "job_title":
            # Boost if near a person name
            nearby_name = False
            for j in range(max(0, i-3), min(len(key), i+4)):
                if j != i and key[j]["classification"] == "person_name":
                    nearby_name = True
                    break
            if nearby_name:
                el["confidence"] = min(95, el["confidence"] + 10)

        validated.append(el)

    return validated


# ── STEP 5: ORGANIZER ───────────────────────────────────────

def organize_key(validated_key, company_name="", outreach_id="", page_url=""):
    """Map identified elements to structured records. Group names with titles."""
    people = []
    emails = []
    linkedin_urls = []
    phones = []
    unidentified = []

    for el in validated_key:
        cls = el["classification"]
        if cls == "person_name":
            people.append({"name": el["text"], "title": None, "email": None,
                          "linkedin": None, "phone": None, "position": el["position"],
                          "confidence": el["confidence"]})
        elif cls == "job_title":
            # Try to attach to nearest person
            if people:
                # Find closest person by position
                closest = min(people, key=lambda p: abs(p["position"] - el["position"]))
                if abs(closest["position"] - el["position"]) <= 5 and closest["title"] is None:
                    closest["title"] = el["text"]
            # Also store standalone
            unidentified.append(el)
        elif cls == "email":
            emails.append(el["text"])
        elif cls == "generic_email":
            unidentified.append(el)
        elif cls == "linkedin_url":
            url = el.get("href") or el["text"]
            linkedin_urls.append(url)
            # Try to attach to nearest person
            if people:
                closest = min(people, key=lambda p: abs(p["position"] - el["position"]))
                if abs(closest["position"] - el["position"]) <= 5 and closest["linkedin"] is None:
                    closest["linkedin"] = url
        elif cls == "phone":
            phones.append(el["text"])
        elif cls in ("empty", "navigation", "url"):
            pass  # Skip noise but don't store
        else:
            unidentified.append(el)

    # Attach emails to people by domain matching or proximity
    for email_text in emails:
        email = EMAIL_RE.search(email_text)
        if email:
            addr = email.group()
            name_part = addr.split("@")[0].lower().replace(".", " ").replace("_", " ")
            # Try to match to a person
            matched = False
            for p in people:
                pname = p["name"].lower()
                if any(part in pname for part in name_part.split() if len(part) > 2):
                    if p["email"] is None:
                        p["email"] = addr
                        matched = True
                        break
            if not matched and people:
                # Attach to first person without email
                for p in people:
                    if p["email"] is None:
                        p["email"] = addr
                        break

    # Classify titles with Title Classifier
    if HAS_CLASSIFIER:
        for p in people:
            if p["title"]:
                result = tc.classify(p["title"], company=company_name)
                p["bucket"] = result.bucket
                p["title_confidence"] = result.confidence
            else:
                p["bucket"] = "UNKNOWN"
                p["title_confidence"] = 0

    return {
        "outreach_id": outreach_id,
        "page_url": page_url,
        "company_name": company_name,
        "people": people,
        "emails": emails,
        "linkedin_urls": linkedin_urls,
        "phones": phones,
        "unidentified": [{"text": u["text"], "tag": u.get("tag", ""), "classification": u["classification"]}
                        for u in unidentified],
        "stats": {
            "total_elements": len(validated_key),
            "people_found": len(people),
            "emails_found": len(emails),
            "linkedin_found": len(linkedin_urls),
            "phones_found": len(phones),
            "unidentified_count": len(unidentified),
        }
    }


# ── MAIN ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PROC-301 — MANAGEMENT PAGE PARSER (Key Builder)")
    print(f"Limit: {LIMIT or 'ALL'} | Dry-run: {DRY_RUN}")
    print("=" * 60)
    sys.stdout.flush()

    # Load companies with about_url
    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""
    rows = d1_query(f"""
        SELECT DISTINCT outreach_id, company_name, about_url
        FROM slot_workbench
        WHERE about_url IS NOT NULL AND about_url != ''
        ORDER BY outreach_id
        {limit_clause}
    """)

    # Dedup by outreach_id
    seen = set()
    companies = []
    for r in rows:
        if r["outreach_id"] not in seen:
            seen.add(r["outreach_id"])
            companies.append(r)

    print(f"Loaded {len(companies)} companies to parse")
    sys.stdout.flush()

    stats = {"fetched": 0, "failed": 0, "people_total": 0, "identified": 0,
             "unidentified": 0, "pages_with_people": 0}

    run_date = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"page-parser-{run_date}.jsonl"
    out = open(output_file, "a")

    for i, company in enumerate(companies):
        url = company["about_url"]
        name = company["company_name"]
        oid = company["outreach_id"]
        port = PORT_BASE + (i % 100)

        # Step 1: Fetch
        html, status = fetch_page(url, port)

        if not html:
            stats["failed"] += 1
            out.write(json.dumps({"outreach_id": oid, "status": "fetch_failed", "code": status}) + "\n")
            if (i + 1) % 25 == 0:
                print(f"  [{i+1}/{len(companies)}] fetched={stats['fetched']} failed={stats['failed']} people={stats['people_total']}")
                sys.stdout.flush()
            time.sleep(FETCH_DELAY)
            continue

        stats["fetched"] += 1

        # Step 2: Decompose
        elements = decompose_page(html)

        # Step 3: Key Builder
        key = build_key(elements, company_name=name)

        # Step 4: Quality Gate
        validated = quality_gate(key, company_name=name)

        # Step 5: Organize
        result = organize_key(validated, company_name=name, outreach_id=oid, page_url=url)

        stats["people_total"] += result["stats"]["people_found"]
        stats["identified"] += result["stats"]["total_elements"] - result["stats"]["unidentified_count"]
        stats["unidentified"] += result["stats"]["unidentified_count"]
        if result["stats"]["people_found"] > 0:
            stats["pages_with_people"] += 1

        # Write full result (including unidentified)
        out.write(json.dumps(result) + "\n")
        out.flush()

        if (i + 1) % 25 == 0 or i == len(companies) - 1:
            total_el = stats["identified"] + stats["unidentified"]
            id_pct = stats["identified"] / max(total_el, 1) * 100
            print(f"  [{i+1}/{len(companies)}] fetched={stats['fetched']} failed={stats['failed']} "
                  f"people={stats['people_total']} pages_w_people={stats['pages_with_people']} "
                  f"identified={id_pct:.0f}%")
            sys.stdout.flush()

        time.sleep(FETCH_DELAY)

    out.close()

    total_el = stats["identified"] + stats["unidentified"]
    print(f"\n{'='*60}")
    print(f"PROC-301 COMPLETE")
    print(f"{'='*60}")
    print(f"  Pages fetched:      {stats['fetched']}")
    print(f"  Fetch failed:       {stats['failed']}")
    print(f"  People found:       {stats['people_total']}")
    print(f"  Pages with people:  {stats['pages_with_people']} ({stats['pages_with_people']/max(stats['fetched'],1)*100:.0f}%)")
    print(f"  Total elements:     {total_el}")
    print(f"  Identified:         {stats['identified']} ({stats['identified']/max(total_el,1)*100:.0f}%)")
    print(f"  Unidentified:       {stats['unidentified']} ({stats['unidentified']/max(total_el,1)*100:.0f}%)")
    print(f"  Output:             {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

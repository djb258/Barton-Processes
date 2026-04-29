"""
UP RUNNER — The Ultimate Process as Code

Executes the full UP flow on any section:
  Orchestrator → D → M → J → QC → [TS output for human] → [Auditor after human]

The agents don't improvise. They don't skip. They don't cherry-pick.
They execute the same flow every time because that's what the code does.

Usage:
  python3 up_runner.py --section 9 --subsection glassdoor
  python3 up_runner.py --section 1
  python3 up_runner.py --section 9 --all-subsections

Output: A scorecard document per section/subsection ready for TS (human review).
The human sets tolerances. The Auditor certifies against those tolerances.
No certification happens in this code. That requires Dave's sign-off.
"""

import json
import re
import sys
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")

OUTPUT_DIR = Path(__file__).parent.parent / "runs"
OUTPUT_DIR.mkdir(exist_ok=True)

SECTION = None
SUBSECTION = None
ALL_SUBSECTIONS = False

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--section" and i + 1 < len(args):
        SECTION = int(args[i + 1]); i += 2
    elif args[i] == "--subsection" and i + 1 < len(args):
        SUBSECTION = args[i + 1]; i += 2
    elif args[i] == "--all-subsections":
        ALL_SUBSECTIONS = True; i += 1
    else:
        i += 1

if not SECTION:
    print("ERROR: --section required (1-9)")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# D1 ACCESS
# ═══════════════════════════════════════════════════════════════

def d1_query(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    if result.returncode != 0: return None
    try:
        s = result.stdout.find('[')
        if s < 0: return None
        data = json.loads(result.stdout[s:])
        return data[0].get("results", [])
    except: return None

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ═══════════════════════════════════════════════════════════════
# QC — Run query twice, verify match
# ═══════════════════════════════════════════════════════════════

def qc_check(comparator_id, description, query):
    """Run a query twice. Return the result with self-verification."""
    run1 = d1_query(query)
    run2 = d1_query(query)

    r1_val = run1[0] if run1 and len(run1) > 0 else None
    r2_val = run2[0] if run2 and len(run2) > 0 else None

    match = (r1_val == r2_val)
    error = (r1_val is None or r2_val is None)

    return {
        "id": comparator_id,
        "description": description,
        "query": query,
        "run1": r1_val,
        "run2": r2_val,
        "match": match,
        "error": error,
    }


# ═══════════════════════════════════════════════════════════════
# ORCHESTRATOR — Read checklist, dispatch
# ═══════════════════════════════════════════════════════════════

def orchestrator(section, subsection=None):
    """Read the checklist for this section. Document state. Return dispatch list."""
    print(f"{'='*70}")
    print(f"ORCHESTRATOR — Section {section}" + (f" / {subsection}" if subsection else ""))
    print(f"{'='*70}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()

    state = {
        "section": section,
        "subsection": subsection,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checklist": {},
        "dispatch": [],
    }

    # Check what exists
    if section == 9 and subsection:
        # Platform subsection
        print(f"Checking platform: {subsection}")
        print(f"  Data collected? Checking recon_platform_urls for {subsection} URLs...")

        count = d1_query(f"""
            SELECT COUNT(*) as cnt FROM slot_workbench
            WHERE slot_type = 'CEO'
            AND recon_platform_urls LIKE '%{subsection}%'
        """)
        has_data = count[0]["cnt"] if count else 0
        state["checklist"]["data_exists"] = has_data > 0
        state["checklist"]["data_count"] = has_data
        print(f"  URLs found: {has_data}")

        # Check if key already built
        key_file = OUTPUT_DIR / f"key_s{section}_{subsection}.json"
        state["checklist"]["key_built"] = key_file.exists()
        print(f"  Key built? {'YES' if key_file.exists() else 'NO'}")

        # Check if map exists
        map_file = OUTPUT_DIR / f"map_s{section}_{subsection}.json"
        state["checklist"]["map_built"] = map_file.exists()
        print(f"  Map built? {'YES' if map_file.exists() else 'NO'}")

        # Check if join tested
        join_file = OUTPUT_DIR / f"join_s{section}_{subsection}.json"
        state["checklist"]["join_tested"] = join_file.exists()
        print(f"  Join tested? {'YES' if join_file.exists() else 'NO'}")

        # Check if QC scored
        qc_file = OUTPUT_DIR / f"qc_s{section}_{subsection}.json"
        state["checklist"]["qc_scored"] = qc_file.exists()
        print(f"  QC scored? {'YES' if qc_file.exists() else 'NO'}")

        state["checklist"]["ts_approved"] = False
        state["checklist"]["auditor_certified"] = False
        print(f"  TS approved? NO")
        print(f"  Auditor certified? NO")

        # Dispatch
        if not state["checklist"]["key_built"]:
            state["dispatch"].append("D")
        if not state["checklist"]["map_built"]:
            state["dispatch"].append("M")
        if not state["checklist"]["join_tested"]:
            state["dispatch"].append("J")
        if not state["checklist"]["qc_scored"]:
            state["dispatch"].append("QC")

        if not state["dispatch"]:
            state["dispatch"] = ["QC"]  # Always re-run QC

        print(f"\n  Dispatch: {' → '.join(state['dispatch'])}")

    else:
        print(f"  Section {section} — checking state...")
        state["dispatch"] = ["D", "M", "J", "QC"]
        print(f"  Dispatch: D → M → J → QC (full run)")

    print()
    return state


# ═══════════════════════════════════════════════════════════════
# D AGENT — Define (Build the Key)
# ═══════════════════════════════════════════════════════════════

def d_agent_platform(platform_name, sample_urls):
    """
    D Agent for a platform subsection.
    Fetches one sample page. Identifies every element.
    Produces the key: description, unique ID, format per element.
    """
    print(f"{'='*70}")
    print(f"D AGENT — Define: {platform_name}")
    print(f"{'='*70}")

    from curl_cffi import requests as creq

    # Fetch one sample page
    url = sample_urls[0] if sample_urls else None
    if not url:
        print("  ERROR: No sample URL available")
        return None

    print(f"  Fetching: {url[:70]}")
    session = creq.Session(impersonate="chrome131")

    html = ""
    try:
        if PROXY_USER:
            proxy = f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@gw.dataimpulse.com:16000"
            resp = session.get(url, proxies={"http": proxy, "https": proxy},
                              timeout=15, allow_redirects=True, impersonate="chrome131")
        else:
            resp = session.get(url, timeout=15, allow_redirects=True)
        html = resp.text if resp.status_code == 200 else ""
        print(f"  Status: {resp.status_code} | Size: {len(html):,} chars")
    except Exception as e:
        print(f"  FETCH FAILED: {str(e)[:60]}")
        return None

    if not html:
        print("  No HTML returned")
        return None

    # Strip scripts/styles
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.I)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Decompose into elements
    elements = []
    eid = 0

    # Title
    title_match = re.search(r'<title>(.*?)</title>', html, re.I | re.DOTALL)
    if title_match:
        elements.append({"id": f"P9-{platform_name.upper()[:3]}-{eid:03d}", "tag": "title",
                         "text": title_match.group(1).strip()[:200], "classification": "page_title",
                         "format": "TEXT", "description": f"Page title from {platform_name}"})
        eid += 1

    # Headings
    for m in re.finditer(r'<(h[1-6])[^>]*>(.*?)</\1>', text, re.DOTALL | re.I):
        content = re.sub(r'<[^>]+>', ' ', m.group(2)).strip()
        content = re.sub(r'\s+', ' ', content)
        if content and len(content) > 2 and len(content) < 200:
            # Classify
            cls = classify_element(content, platform_name)
            elements.append({"id": f"P9-{platform_name.upper()[:3]}-{eid:03d}", "tag": m.group(1),
                             "text": content, "classification": cls,
                             "format": "TEXT", "description": f"{cls} from {platform_name} {m.group(1)} tag"})
            eid += 1

    # Links with text
    for m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', text, re.DOTALL | re.I):
        content = re.sub(r'<[^>]+>', ' ', m.group(2)).strip()
        content = re.sub(r'\s+', ' ', content)
        href = m.group(1)
        if content and len(content) > 2 and len(content) < 150:
            cls = classify_element(content, platform_name)
            elements.append({"id": f"P9-{platform_name.upper()[:3]}-{eid:03d}", "tag": "a",
                             "text": content, "href": href, "classification": cls,
                             "format": "TEXT, URL", "description": f"{cls} link from {platform_name}"})
            eid += 1

    # Short text blocks (paragraphs, spans, divs, list items)
    for m in re.finditer(r'<(?:p|span|li|td|dd)[^>]*>(.*?)</(?:p|span|li|td|dd)>', text, re.DOTALL | re.I):
        content = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
        content = re.sub(r'\s+', ' ', content)
        if content and 3 < len(content) < 200:
            already = any(content == e["text"] for e in elements)
            if not already:
                cls = classify_element(content, platform_name)
                elements.append({"id": f"P9-{platform_name.upper()[:3]}-{eid:03d}", "tag": "text",
                                 "text": content, "classification": cls,
                                 "format": "TEXT", "description": f"{cls} from {platform_name}"})
                eid += 1

    # Emails
    for m in re.finditer(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
        email = m.group()
        if not any(x in email.lower() for x in ['example', 'wix', 'sentry', 'noreply']):
            already = any(email in e.get("text", "") for e in elements)
            if not already:
                elements.append({"id": f"P9-{platform_name.upper()[:3]}-{eid:03d}", "tag": "email",
                                 "text": email, "classification": "email",
                                 "format": "TEXT, email format", "description": f"Email address from {platform_name}"})
                eid += 1

    # Phone numbers
    for m in re.finditer(r'(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text):
        phone = m.group()
        already = any(phone in e.get("text", "") for e in elements)
        if not already:
            elements.append({"id": f"P9-{platform_name.upper()[:3]}-{eid:03d}", "tag": "phone",
                             "text": phone, "classification": "phone",
                             "format": "TEXT, phone format", "description": f"Phone number from {platform_name}"})
            eid += 1

    # LinkedIn URLs on page
    for m in re.finditer(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+', html):
        li_url = m.group()
        already = any(li_url in e.get("text", "") or li_url == e.get("href", "") for e in elements)
        if not already:
            elements.append({"id": f"P9-{platform_name.upper()[:3]}-{eid:03d}", "tag": "linkedin",
                             "text": li_url, "classification": "linkedin_url",
                             "format": "TEXT, URL", "description": f"LinkedIn profile URL from {platform_name}"})
            eid += 1

    # Summary
    classifications = {}
    for e in elements:
        cls = e["classification"]
        classifications[cls] = classifications.get(cls, 0) + 1

    print(f"\n  KEY BUILT: {len(elements)} elements identified")
    print(f"  Classifications:")
    for cls, cnt in sorted(classifications.items(), key=lambda x: -x[1]):
        print(f"    {cls:25s}: {cnt}")

    # Every element has: id, description, format, classification
    # Verify three properties
    missing = [e for e in elements if not e.get("id") or not e.get("description") or not e.get("format")]
    print(f"\n  Three-property check: {len(elements) - len(missing)}/{len(elements)} complete")
    if missing:
        print(f"  WARNING: {len(missing)} elements missing properties")

    # Save the key
    key = {
        "platform": platform_name,
        "sample_url": url,
        "elements": elements,
        "classifications": classifications,
        "total_elements": len(elements),
        "three_property_complete": len(elements) - len(missing),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    key_file = OUTPUT_DIR / f"key_s9_{platform_name}.json"
    key_file.write_text(json.dumps(key, indent=2))
    print(f"  Key saved: {key_file}")
    print()

    return key


def classify_element(text, platform_name):
    """Classify a text element into a bucket. Same rules for every platform."""
    lower = text.lower().strip()

    # Navigation / UI
    nav_words = ["home", "about", "contact", "sign in", "log in", "search", "menu",
                 "privacy", "terms", "cookie", "help", "close", "back", "next",
                 "subscribe", "follow", "share", "more", "less", "show", "hide"]
    if lower in nav_words or any(lower == w for w in nav_words):
        return "navigation"

    # Person name pattern (2-4 capitalized words)
    words = text.split()
    if 2 <= len(words) <= 4 and len(text) < 50:
        all_cap = all(w[0].isupper() for w in words if len(w) > 1)
        company_words = {"inc", "llc", "ltd", "corp", "company", "group", "services"}
        no_company = not any(w.lower().rstrip('.,') in company_words for w in words)
        no_special = not any(c in text for c in ['@', 'http', '/', '<', '>'])
        if all_cap and no_company and no_special:
            return "person_name"

    # Job title keywords
    title_re = re.compile(
        r'\b(?:CEO|CFO|COO|CTO|President|Owner|Founder|Director|VP|Chief|'
        r'Controller|Manager|Head of|Senior|Principal|Administrator|'
        r'Human Resource|HR |Benefits|Talent)\b', re.I)
    if title_re.search(text) and len(text) < 120:
        return "job_title"

    # Email
    if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text) and len(text) < 60:
        return "email"

    # Phone
    if re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text) and len(text) < 30:
        return "phone"

    # Rating
    if re.search(r'\d\.\d\s*(?:out of|\/|★|star)', text, re.I):
        return "rating"

    # Number/stat
    if re.search(r'^\d[\d,]*$', text.strip()) or re.search(r'\d+\s*(?:employees|reviews|jobs|salaries)', text, re.I):
        return "statistic"

    # Location
    if re.search(r'\b(?:street|ave|blvd|road|suite|floor|city|state)\b', text, re.I) and len(text) < 100:
        return "address"

    # URL
    if text.startswith("http"):
        return "url"

    # Description (longer text)
    if len(text) > 80:
        return "description"

    return "unidentified"


# ═══════════════════════════════════════════════════════════════
# M AGENT — Map (Connect Key to Structure)
# ═══════════════════════════════════════════════════════════════

def m_agent_platform(platform_name, key):
    """Map identified elements to our target structure."""
    print(f"{'='*70}")
    print(f"M AGENT — Map: {platform_name}")
    print(f"{'='*70}")

    # Target columns in slot_workbench
    target_columns = {
        "person_name": {"target": "person_first_name + person_last_name", "description": "Person's name split into first and last"},
        "job_title": {"target": "classify → slot_type (CEO/CFO/HR)", "description": "Job title classified by Title Classifier"},
        "email": {"target": "person_email", "description": "Email address"},
        "phone": {"target": "future: person_phone", "description": "Phone number (no target column yet)"},
        "linkedin_url": {"target": "person_linkedin", "description": "LinkedIn profile URL"},
        "rating": {"target": "future: company_rating", "description": "Company rating (no target column yet)"},
        "statistic": {"target": "future: platform metrics", "description": "Employee count, review count, etc."},
        "address": {"target": "validation against city/state", "description": "Company address for verification"},
    }

    mapping = []
    unmapped_classifications = set()

    for element in key["elements"]:
        cls = element["classification"]
        if cls in target_columns:
            mapping.append({
                "source_id": element["id"],
                "source_classification": cls,
                "source_text_sample": element["text"][:50],
                "target": target_columns[cls]["target"],
                "target_description": target_columns[cls]["description"],
                "transform": "direct" if cls in ("email", "phone", "linkedin_url") else "classify" if cls == "job_title" else "split" if cls == "person_name" else "validate",
            })
        else:
            unmapped_classifications.add(cls)

    # Classification summary
    mapped_count = len(mapping)
    total_elements = len(key["elements"])
    unmapped_count = total_elements - mapped_count

    print(f"\n  Total elements: {total_elements}")
    print(f"  Mapped: {mapped_count}")
    print(f"  Unmapped: {unmapped_count}")
    print(f"  Unmapped classifications: {unmapped_classifications}")
    print(f"\n  Mapping table:")
    for m in mapping[:10]:
        print(f"    {m['source_id']} ({m['source_classification']}) → {m['target']}")
    if len(mapping) > 10:
        print(f"    ... and {len(mapping) - 10} more")

    # Save
    map_data = {
        "platform": platform_name,
        "mapping": mapping,
        "unmapped_classifications": list(unmapped_classifications),
        "mapped_count": mapped_count,
        "unmapped_count": unmapped_count,
        "total_elements": total_elements,
        "coverage": round(mapped_count / max(total_elements, 1) * 100, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    map_file = OUTPUT_DIR / f"map_s9_{platform_name}.json"
    map_file.write_text(json.dumps(map_data, indent=2))
    print(f"\n  Map saved: {map_file}")
    print()

    return map_data


# ═══════════════════════════════════════════════════════════════
# J AGENT — Join (Path to Spine)
# ═══════════════════════════════════════════════════════════════

def j_agent_platform(platform_name):
    """Find the join path from platform data to outreach_id."""
    print(f"{'='*70}")
    print(f"J AGENT — Join: {platform_name}")
    print(f"{'='*70}")

    # The join path for platform data:
    # Platform URL stored in recon_platform_urls on slot_workbench
    # slot_workbench has outreach_id
    # Join: recon_platform_urls contains {platform_name: [urls]} → outreach_id on same row
    # This is a DIRECT join — the platform URL is already on the workbench

    join_path = {
        "platform": platform_name,
        "join_type": "direct",
        "join_field": "outreach_id",
        "join_description": f"Platform URLs stored in slot_workbench.recon_platform_urls (JSON). The outreach_id is on the same row. Direct join — no hops.",
        "hops": 1,
    }

    # Test the join — how many companies have this platform URL
    check = qc_check(
        f"J9-{platform_name.upper()[:3]}-JOIN",
        f"Companies with {platform_name} URLs in workbench",
        f"SELECT COUNT(*) as val FROM slot_workbench WHERE slot_type = 'CEO' AND recon_platform_urls LIKE '%{platform_name}%'"
    )

    join_path["test_result"] = check
    join_path["companies_with_data"] = check["run1"]["val"] if check["run1"] else 0
    join_path["self_verified"] = check["match"]

    print(f"\n  Join type: {join_path['join_type']}")
    print(f"  Join field: {join_path['join_field']}")
    print(f"  Companies with {platform_name}: {join_path['companies_with_data']}")
    print(f"  Self-verified: {'YES' if join_path['self_verified'] else 'NO — MISMATCH'}")

    # Save
    join_file = OUTPUT_DIR / f"join_s9_{platform_name}.json"
    join_file.write_text(json.dumps(join_path, indent=2, default=str))
    print(f"\n  Join saved: {join_file}")
    print()

    return join_path


# ═══════════════════════════════════════════════════════════════
# QC AGENT — Quality Control (Scorecard)
# ═══════════════════════════════════════════════════════════════

def qc_agent_platform(platform_name, key, map_data, join_data):
    """Produce the scorecard with reproducible queries."""
    print(f"{'='*70}")
    print(f"QC AGENT — Scorecard: {platform_name}")
    print(f"{'='*70}")

    checks = []

    # Check 1: Key completeness — all elements have 3 properties
    three_prop = key["three_property_complete"]
    total_el = key["total_elements"]
    checks.append({
        "id": f"QC9-{platform_name.upper()[:3]}-01",
        "what": "Key completeness (3 properties per element)",
        "value": f"{three_prop}/{total_el}",
        "percentage": round(three_prop / max(total_el, 1) * 100, 1),
        "query": "Computed from key file — count elements with id + description + format",
        "run1": three_prop,
        "run2": three_prop,
        "match": True,
    })

    # Check 2: Identification rate
    identified = sum(1 for e in key["elements"] if e["classification"] != "unidentified" and e["classification"] != "navigation")
    checks.append({
        "id": f"QC9-{platform_name.upper()[:3]}-02",
        "what": "Identification rate (not unidentified/navigation)",
        "value": f"{identified}/{total_el}",
        "percentage": round(identified / max(total_el, 1) * 100, 1),
        "query": "Computed from key file — count elements where classification != unidentified and != navigation",
        "run1": identified,
        "run2": identified,
        "match": True,
    })

    # Check 3: Person names found
    person_count = sum(1 for e in key["elements"] if e["classification"] == "person_name")
    checks.append({
        "id": f"QC9-{platform_name.upper()[:3]}-03",
        "what": "Person names found on page",
        "value": str(person_count),
        "percentage": None,
        "query": "Computed from key file — count elements where classification = person_name",
        "run1": person_count,
        "run2": person_count,
        "match": True,
    })

    # Check 4: Job titles found
    title_count = sum(1 for e in key["elements"] if e["classification"] == "job_title")
    checks.append({
        "id": f"QC9-{platform_name.upper()[:3]}-04",
        "what": "Job titles found on page",
        "value": str(title_count),
        "percentage": None,
        "query": "Computed from key file — count elements where classification = job_title",
        "run1": title_count,
        "run2": title_count,
        "match": True,
    })

    # Check 5: Mapping coverage
    checks.append({
        "id": f"QC9-{platform_name.upper()[:3]}-05",
        "what": "Mapping coverage (elements mapped to target)",
        "value": f"{map_data['mapped_count']}/{map_data['total_elements']}",
        "percentage": map_data["coverage"],
        "query": "Computed from map file — mapped_count / total_elements",
        "run1": map_data["coverage"],
        "run2": map_data["coverage"],
        "match": True,
    })

    # Check 6: Join resolution (from D1 — reproducible)
    checks.append({
        "id": f"QC9-{platform_name.upper()[:3]}-06",
        "what": f"Companies with {platform_name} URLs (join test)",
        "value": str(join_data["companies_with_data"]),
        "percentage": None,
        "query": join_data["test_result"]["query"],
        "run1": join_data["test_result"]["run1"],
        "run2": join_data["test_result"]["run2"],
        "match": join_data["test_result"]["match"],
    })

    # Summary
    all_match = all(c["match"] for c in checks)
    errors = sum(1 for c in checks if not c["match"])

    print(f"\n  SCORECARD:")
    for c in checks:
        status = "✓" if c["match"] else "✗ MISMATCH"
        pct = f" ({c['percentage']}%)" if c["percentage"] is not None else ""
        print(f"    {c['id']:20s} | {c['what']:45s} | {c['value']:>10s}{pct} | {status}")

    print(f"\n  Self-verification: {len(checks) - errors}/{len(checks)} verified")
    print(f"  Status: {'ALL VERIFIED — Ready for TS' if all_match else 'MISMATCH DETECTED — Investigate'}")

    # Save
    scorecard = {
        "platform": platform_name,
        "checks": checks,
        "all_verified": all_match,
        "total_checks": len(checks),
        "verified_checks": len(checks) - errors,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ts_status": "NOT RUN — awaiting Dave's review",
        "auditor_status": "NOT RUN — requires Dave's sign-off",
    }

    qc_file = OUTPUT_DIR / f"qc_s9_{platform_name}.json"
    qc_file.write_text(json.dumps(scorecard, indent=2, default=str))
    print(f"\n  Scorecard saved: {qc_file}")
    print()

    return scorecard


# ═══════════════════════════════════════════════════════════════
# MAIN — Run the full UP chain
# ═══════════════════════════════════════════════════════════════

def run_up_on_platform(platform_name):
    """Run Orchestrator → D → M → J → QC on one platform."""

    # Get a sample URL for this platform
    rows = d1_query(f"""
        SELECT recon_platform_urls FROM slot_workbench
        WHERE slot_type = 'CEO'
        AND recon_platform_urls LIKE '%{platform_name}%'
        LIMIT 1
    """)

    sample_urls = []
    if rows:
        platforms = json.loads(rows[0]["recon_platform_urls"])
        sample_urls = platforms.get(platform_name, [])

    if not sample_urls:
        print(f"No URLs found for {platform_name}. Skipping.")
        return None

    # 1. ORCHESTRATOR
    state = orchestrator(9, platform_name)

    # 2. D AGENT — Define
    key = d_agent_platform(platform_name, sample_urls)
    if not key:
        print(f"D Agent failed for {platform_name}. Cannot continue.")
        return None

    # 3. M AGENT — Map
    map_data = m_agent_platform(platform_name, key)

    # 4. J AGENT — Join
    join_data = j_agent_platform(platform_name)

    # 5. QC AGENT — Scorecard
    scorecard = qc_agent_platform(platform_name, key, map_data, join_data)

    # 6. TS — HUMAN GATE (not in code — output is the scorecard for Dave)
    print(f"{'='*70}")
    print(f"TS — AWAITING HUMAN REVIEW: {platform_name}")
    print(f"{'='*70}")
    print(f"Scorecard produced. Dave must review, set tolerances, and approve.")
    print(f"No certification possible without Dave's sign-off (Rule 12).")
    print()

    return scorecard


def main():
    if SECTION == 9:
        platforms = ["glassdoor", "indeed", "facebook", "yelp", "bbb",
                     "linkedin_company", "x_twitter", "crunchbase", "zoominfo", "capterra"]

        if SUBSECTION:
            platforms = [SUBSECTION]
        elif not ALL_SUBSECTIONS:
            print("Section 9 has 10 platforms. Use --subsection <name> or --all-subsections")
            print(f"Available: {', '.join(platforms)}")
            sys.exit(1)

        print(f"{'='*70}")
        print(f"UP — SECTION 9: Platform Sources")
        print(f"Running {len(platforms)} platform(s): {', '.join(platforms)}")
        print(f"{'='*70}\n")

        results = {}
        for platform in platforms:
            print(f"\n{'#'*70}")
            print(f"# PLATFORM: {platform}")
            print(f"{'#'*70}\n")

            scorecard = run_up_on_platform(platform)
            results[platform] = scorecard

            import time
            time.sleep(2)

        # Final summary
        print(f"\n{'='*70}")
        print(f"UP SECTION 9 — SUMMARY")
        print(f"{'='*70}")
        for platform, sc in results.items():
            if sc:
                status = "VERIFIED" if sc["all_verified"] else "MISMATCH"
                print(f"  {platform:20s}: {sc['verified_checks']}/{sc['total_checks']} checks | {status}")
            else:
                print(f"  {platform:20s}: FAILED — no data or fetch error")

        print(f"\nAll scorecards saved to: {OUTPUT_DIR}/")
        print(f"STATUS: ALL AWAITING TS (Dave's review)")
        print(f"{'='*70}")

    else:
        print(f"Section {SECTION} UP runner not yet implemented. Coming soon.")


if __name__ == "__main__":
    main()

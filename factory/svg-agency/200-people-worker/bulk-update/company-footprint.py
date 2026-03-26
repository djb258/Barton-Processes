"""
Process 200+ — Company Footprint Builder

Builds the richest possible dossier per company using SearchEngineProxy.
Runs AFTER the person drip-fetch completes (or in parallel from separate session).

Per company, queries multiple sources:
  1. "{company} glassdoor" → employee reviews, benefits sentiment
  2. "{company} indeed benefits OR HR" → hiring signals
  3. "{company} linkedin" → company page (employee count, industry)
  4. "{company} news" → recent events
  5. "site:{domain}" → website freshness

Same infrastructure: Startpage + DataImpulse + curl_cffi + Box-Muller jitter.

IMPORTANT: Do NOT run simultaneously with drip-fetch.py against Startpage.
           Either run after drip-fetch completes, or use a different search engine.

Usage:
  python3 bulk-update/company-footprint.py                    # Full run
  python3 bulk-update/company-footprint.py --limit 50         # Test
  python3 bulk-update/company-footprint.py --agent "Dave Allan" # One agent
  python3 bulk-update/company-footprint.py --resume            # Resume

Output: bulk-update/company-footprint-YYYY-MM.jsonl
"""

import json
import re
import time
import sys
import os
import math
import random
import urllib.parse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

# ── Config ───────────────────────────────────────────────────

DELAY_MEAN = 8.0          # Slower — multiple queries per company
DELAY_STD = 3.0
DELAY_MIN = 4.0
LIMIT = 0
AGENT_FILTER = None
OUTPUT_DIR = Path(__file__).parent

PROXY_HOST = os.environ.get("PROXY_HOST", "gw.dataimpulse.com")
PROXY_PORT = os.environ.get("PROXY_PORT", "823")
PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")

DB_URL = os.environ.get("DATABASE_URL",
    "postgresql://Marketing%20DB_owner:npg_OsE4Z2oPCpiT@ep-ancient-waterfall-a42vy0du-pooler.us-east-1.aws.neon.tech/Marketing%20DB?sslmode=require")

# ── Intelligence query templates (constants) ─────────────────

QUERIES = {
    "glassdoor_sentiment": {
        "template": '"{company}" site:glassdoor.com reviews',
        "signal_type": "BENEFITS_SENTIMENT",
        "description": "Employee reviews — benefits satisfaction, HR complaints",
        "keywords": ["benefits", "insurance", "health", "HR", "401k", "PTO", "management"],
    },
    "indeed_hiring": {
        "template": '"{company}" site:indeed.com "benefits" OR "HR" OR "human resources"',
        "signal_type": "HIRING_SIGNAL",
        "description": "Job postings for buyer persona — benefits/HR roles",
        "keywords": ["benefits manager", "HR manager", "benefits administrator", "human resources"],
    },
    "linkedin_company": {
        "template": '"{company}" site:linkedin.com/company',
        "signal_type": "COMPANY_PROFILE",
        "description": "LinkedIn company page — employee count, industry",
        "keywords": ["employees", "industry", "headquarter", "founded", "specialties"],
    },
    "recent_news": {
        "template": '"{company}" news 2026',
        "signal_type": "NEWS_EVENT",
        "description": "Recent company news — M&A, funding, expansion",
        "keywords": ["acquisition", "funding", "expansion", "layoff", "merger", "IPO", "partnership"],
    },
    "website_freshness": {
        "template": 'site:{domain}',
        "signal_type": "WEBSITE_ACTIVE",
        "description": "Website content freshness — is the company actively publishing",
        "keywords": ["2026", "2025", "blog", "news", "press", "announcement"],
    },
}

# ── Parse args ───────────────────────────────────────────────

args = sys.argv[1:]
resume = False
i = 0
while i < len(args):
    if args[i] == "--delay" and i + 1 < len(args):
        DELAY_MEAN = float(args[i + 1])
        i += 2
    elif args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1])
        i += 2
    elif args[i] == "--agent" and i + 1 < len(args):
        AGENT_FILTER = args[i + 1]
        i += 2
    elif args[i] == "--resume":
        resume = True
        i += 1
    else:
        i += 1

# ── Helpers ──────────────────────────────────────────────────

def box_muller_delay():
    u1 = max(1e-10, random.random())
    u2 = random.random()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return max(DELAY_MIN, DELAY_MEAN + z * DELAY_STD)


def search_startpage(query: str, proxies: dict | None) -> dict:
    encoded = urllib.parse.quote(query)
    url = f"https://www.startpage.com/sp/search?query={encoded}"
    kwargs = {"impersonate": "chrome", "timeout": 15}
    if proxies:
        kwargs["proxies"] = proxies

    try:
        resp = requests.get(url, **kwargs)
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}", "results": []}

        # Check for captcha
        if "captcha" in resp.text.lower()[:1000]:
            return {"error": "CAPTCHA", "results": []}

        titles = re.findall(r'<h2[^>]*>(.*?)</h2>', resp.text, re.DOTALL)
        snippets = re.findall(r'<p class="w-gl__description[^"]*"[^>]*>(.*?)</p>', resp.text, re.DOTALL)

        results = []
        for j, t in enumerate(titles):
            clean_t = re.sub(r'<[^>]+>', '', t).strip()
            clean_s = re.sub(r'<[^>]+>', '', snippets[j]).strip() if j < len(snippets) else ""
            if clean_t and len(clean_t) > 5:
                results.append({"title": clean_t, "snippet": clean_s})

        return {"error": None, "results": results}
    except Exception as e:
        return {"error": str(e)[:100], "results": []}


def score_relevance(results: list, keywords: list) -> dict:
    """Score search results for keyword relevance."""
    if not results:
        return {"score": 0, "matches": [], "top_result": None}

    matches = []
    for r in results[:5]:
        text = (r["title"] + " " + r["snippet"]).lower()
        hits = [kw for kw in keywords if kw.lower() in text]
        if hits:
            matches.append({"title": r["title"][:80], "keywords": hits, "snippet": r["snippet"][:100]})

    return {
        "score": len(matches),
        "matches": matches[:3],
        "top_result": results[0]["title"][:80] if results else None,
    }


# ── Main ─────────────────────────────────────────────────────

def main():
    proxies = None
    if PROXY_USER and PROXY_PASS:
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        proxies = {"http": proxy_url, "https": proxy_url}

    agent_filter = f"AND tc.agent_name = '{AGENT_FILTER}'" if AGENT_FILTER else ""

    result = subprocess.run([
        "psql", DB_URL, "-t", "-A", "-c",
        f"""SELECT json_agg(row_to_json(t)) FROM (
            SELECT DISTINCT
                tc.company_unique_id,
                ci.canonical_name as company_name,
                ci.company_domain as domain,
                tc.agent_name,
                tc.city,
                tc.state
            FROM people.v_territory_companies tc
            JOIN cl.company_identity ci ON ci.company_unique_id::text = tc.company_unique_id
            WHERE ci.canonical_name IS NOT NULL AND ci.canonical_name != ''
            {agent_filter}
            ORDER BY tc.agent_name
        ) t"""
    ], capture_output=True, text=True)

    companies = json.loads(result.stdout.strip()) if result.stdout.strip() else []
    if not companies:
        print("No companies found.")
        return

    print(f"Company Footprint Builder")
    print(f"Companies: {len(companies)}")
    print(f"Queries per company: {len(QUERIES)}")
    print(f"Total queries: ~{len(companies) * len(QUERIES)}")
    print(f"Mode: {'PROXY' if proxies else 'DIRECT'}")
    if AGENT_FILTER:
        print(f"Agent filter: {AGENT_FILTER}")

    if LIMIT:
        companies = companies[:LIMIT]
        print(f"Limit: {LIMIT}")

    run_month = datetime.now().strftime("%Y-%m")
    output_file = OUTPUT_DIR / f"company-footprint-{run_month}.jsonl"

    already_done = set()
    if resume and output_file.exists():
        with open(output_file) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    already_done.add(rec.get("company_unique_id", ""))
                except:
                    pass
        companies = [c for c in companies if c["company_unique_id"] not in already_done]
        print(f"Resuming: {len(already_done)} done, {len(companies)} remaining")

    est_hours = len(companies) * len(QUERIES) * DELAY_MEAN / 3600
    print(f"Estimated time: {est_hours:.1f} hours")
    print(f"Output: {output_file}")
    print()

    out = open(output_file, "a")
    start_time = time.time()
    companies_done = 0
    total_signals = 0

    for idx, company in enumerate(companies):
        name = company["company_name"]
        domain = company.get("domain", "")
        fetched_at = datetime.now(timezone.utc).isoformat()

        footprint = {
            "company_unique_id": company["company_unique_id"],
            "company_name": name,
            "domain": domain,
            "agent_name": company["agent_name"],
            "city": company.get("city"),
            "state": company.get("state"),
            "fetched_at": fetched_at,
            "signals": {},
        }

        for query_name, query_def in QUERIES.items():
            # Build the query
            template = query_def["template"]
            if "{company}" in template:
                q = template.replace("{company}", name)
            elif "{domain}" in template:
                if not domain:
                    footprint["signals"][query_name] = {"skipped": True, "reason": "no domain"}
                    continue
                q = template.replace("{domain}", domain)
            else:
                q = template

            # Search
            result = search_startpage(q, proxies)

            if result["error"] == "CAPTCHA":
                print(f"\n  ⚠ CAPTCHA detected — pausing 120s...")
                time.sleep(120)
                result = search_startpage(q, proxies)

            if result["error"]:
                footprint["signals"][query_name] = {"error": result["error"]}
            else:
                scored = score_relevance(result["results"], query_def["keywords"])
                footprint["signals"][query_name] = {
                    "signal_type": query_def["signal_type"],
                    "score": scored["score"],
                    "top_result": scored["top_result"],
                    "matches": scored["matches"],
                    "result_count": len(result["results"]),
                }
                if scored["score"] > 0:
                    total_signals += 1

            time.sleep(box_muller_delay())

        # Write footprint
        out.write(json.dumps(footprint) + "\n")
        out.flush()
        companies_done += 1

        # Progress
        elapsed = time.time() - start_time
        rate = companies_done / elapsed * 3600 if elapsed > 0 else 0
        signal_list = [k for k, v in footprint["signals"].items() if isinstance(v, dict) and v.get("score", 0) > 0]
        signal_str = ", ".join(signal_list) if signal_list else "none"

        if (idx + 1) % 5 == 0 or signal_list:
            print(f"  [{idx+1}/{len(companies)}] {name[:30]:30s} | signals: {signal_str} | {rate:.0f} co/hr | {elapsed/60:.1f}m")

    out.close()

    elapsed = (time.time() - start_time) / 60
    print(f"\n{'='*60}")
    print(f"Done in {elapsed:.1f} minutes")
    print(f"Companies processed: {companies_done}")
    print(f"Total signals found: {total_signals}")
    print(f"Output: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

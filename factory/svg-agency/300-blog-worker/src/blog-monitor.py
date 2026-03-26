"""
Process 300 — Blog Monitor

Phase 1: Key indicator check via SearchEngineProxy.
Queries Startpage for each company domain to detect indexed content changes.
If Google recently re-indexed the site → content changed (1). Stale → no change (0).

Phase 2: Content classification (only on 1s).
Queries Startpage with signal keywords to classify what changed.
6 signals: FUNDING_EVENT, ACQUISITION, LEADERSHIP_CHANGE, EXPANSION, RESTRUCTURING, GENERAL_NEWS

Same infrastructure as Process 200 — Startpage + DataImpulse + curl_cffi + Box-Muller jitter.

Usage:
  python3 src/blog-monitor.py                          # Full run
  python3 src/blog-monitor.py --phase 1                # Phase 1 only (key indicator)
  python3 src/blog-monitor.py --phase 2                # Phase 2 only (classify 1s)
  python3 src/blog-monitor.py --limit 100              # Test with 100
  python3 src/blog-monitor.py --resume                 # Resume interrupted

Env vars: PROXY_USER, PROXY_PASS (DataImpulse credentials)

Output: src/output/blog-indicators-YYYY-MM.jsonl (Phase 1)
        src/output/blog-signals-YYYY-MM.jsonl (Phase 2)
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

DELAY_MEAN = 5.0
DELAY_STD = 2.0
DELAY_MIN = 2.5
LIMIT = 0
PHASE = 0  # 0 = both, 1 = indicator only, 2 = classify only
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PROXY_HOST = os.environ.get("PROXY_HOST", "gw.dataimpulse.com")
PROXY_PORT = os.environ.get("PROXY_PORT", "823")
PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")

DB_URL = os.environ.get("DATABASE_URL",
    "postgresql://Marketing%20DB_owner:npg_OsE4Z2oPCpiT@ep-ancient-waterfall-a42vy0du-pooler.us-east-1.aws.neon.tech/Marketing%20DB?sslmode=require")

# Signal definitions (constants)
SIGNALS = {
    "FUNDING_EVENT": {
        "keywords": ["funding", "raised", "series A", "series B", "investment", "venture", "capital"],
        "weight": 15,
    },
    "ACQUISITION": {
        "keywords": ["acquisition", "acquired", "merger", "merged", "buyout", "takeover"],
        "weight": 12,
    },
    "LEADERSHIP_CHANGE": {
        "keywords": ["new CEO", "new CFO", "new hire", "appointed", "promoted", "executive"],
        "weight": 10,
    },
    "EXPANSION": {
        "keywords": ["expansion", "new office", "new location", "growing", "hiring spree", "headcount"],
        "weight": 8,
    },
    "RESTRUCTURING": {
        "keywords": ["restructuring", "layoff", "reorganization", "downsizing", "consolidation"],
        "weight": 7,
    },
    "GENERAL_NEWS": {
        "keywords": ["announcement", "press release", "news", "update", "launch"],
        "weight": 5,
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
    elif args[i] == "--phase" and i + 1 < len(args):
        PHASE = int(args[i + 1])
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


def get_proxies():
    if PROXY_USER and PROXY_PASS:
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        return {"http": proxy_url, "https": proxy_url}
    return None


def search_startpage(query: str, proxies: dict | None) -> dict:
    """Generic Startpage search. Returns parsed results."""
    encoded = urllib.parse.quote(query)
    url = f"https://www.startpage.com/sp/search?query={encoded}"

    kwargs = {"impersonate": "chrome", "timeout": 15}
    if proxies:
        kwargs["proxies"] = proxies

    resp = requests.get(url, **kwargs)

    if resp.status_code != 200:
        return {"status": resp.status_code, "results": [], "error": f"HTTP {resp.status_code}"}

    titles = re.findall(r'<h2[^>]*>(.*?)</h2>', resp.text, re.DOTALL)
    snippets = re.findall(r'<p class="w-gl__description"[^>]*>(.*?)</p>', resp.text, re.DOTALL)

    results = []
    for j, t in enumerate(titles):
        clean_title = re.sub(r'<[^>]+>', '', t).strip()
        clean_snippet = re.sub(r'<[^>]+>', '', snippets[j]).strip() if j < len(snippets) else ""
        if clean_title and len(clean_title) > 5:
            results.append({"title": clean_title, "snippet": clean_snippet})

    return {"status": 200, "results": results, "error": None}


# ── Phase 1: Key Indicator ───────────────────────────────────

def check_blog_indicator(company_domain: str, company_name: str, proxies: dict | None) -> dict:
    """Check if a company's blog/website has been recently indexed."""
    fetched_at = datetime.now(timezone.utc).isoformat()

    # Search for recent content on the company domain
    query = f"site:{company_domain}"
    result = search_startpage(query, proxies)

    if result["error"]:
        return {"movement": 0, "error": result["error"], "fetched_at": fetched_at}

    if not result["results"]:
        return {"movement": 0, "reason": "NOT_INDEXED", "fetched_at": fetched_at}

    # Check for freshness indicators in snippets
    fresh_keywords = ["2026", "2025", "ago", "today", "yesterday", "this week", "this month", "mar", "feb", "jan"]
    has_fresh = any(
        any(kw in r["snippet"].lower() or kw in r["title"].lower() for kw in fresh_keywords)
        for r in result["results"][:5]
    )

    return {
        "movement": 1 if has_fresh else 0,
        "reason": "FRESH_CONTENT" if has_fresh else "STALE_INDEX",
        "result_count": len(result["results"]),
        "top_result": result["results"][0]["title"][:100] if result["results"] else "",
        "fetched_at": fetched_at,
    }


# ── Phase 2: Signal Classification ──────────────────────────

def classify_blog_signals(company_domain: str, company_name: str, proxies: dict | None) -> dict:
    """Search for specific signal types on a company's domain."""
    fetched_at = datetime.now(timezone.utc).isoformat()
    detected_signals = []

    for signal_name, signal_def in SIGNALS.items():
        keywords = " OR ".join(f'"{kw}"' for kw in signal_def["keywords"][:3])
        query = f'site:{company_domain} {keywords}'

        result = search_startpage(query, proxies)
        time.sleep(box_muller_delay())

        if result["error"] or not result["results"]:
            continue

        # Check if any result matches signal keywords
        for r in result["results"][:3]:
            text = (r["title"] + " " + r["snippet"]).lower()
            matches = sum(1 for kw in signal_def["keywords"] if kw.lower() in text)
            if matches >= 1:
                detected_signals.append({
                    "signal": signal_name,
                    "weight": signal_def["weight"],
                    "evidence": r["title"][:100],
                    "keyword_matches": matches,
                })
                break

    return {
        "signals": detected_signals,
        "signal_count": len(detected_signals),
        "fetched_at": fetched_at,
    }


# ── Main ─────────────────────────────────────────────────────

def main():
    proxies = get_proxies()

    # Get territory companies with blog domains
    result = subprocess.run([
        "psql", DB_URL, "-t", "-A", "-c",
        """SELECT json_agg(row_to_json(t)) FROM (
            SELECT DISTINCT
                tc.company_unique_id,
                ci.canonical_name as company_name,
                ci.company_domain,
                tc.agent_name
            FROM people.v_territory_companies tc
            JOIN cl.company_identity ci ON ci.company_unique_id::text = tc.company_unique_id
            WHERE ci.company_domain IS NOT NULL
            AND ci.company_domain != ''
            AND ci.canonical_name IS NOT NULL
            ORDER BY tc.agent_name
        ) t"""
    ], capture_output=True, text=True)

    companies = json.loads(result.stdout.strip()) if result.stdout.strip() else []
    if not companies:
        print("No companies with domains found.")
        sys.exit(0)

    print(f"Loaded {len(companies)} companies with domains")
    print(f"Mode: {'PROXY' if proxies else 'DIRECT'}")
    print(f"Phase: {'BOTH' if PHASE == 0 else PHASE}")

    if LIMIT:
        companies = companies[:LIMIT]
        print(f"Limit: {LIMIT}")

    run_month = datetime.now().strftime("%Y-%m")

    # ── Phase 1 ──
    if PHASE in (0, 1):
        indicator_file = OUTPUT_DIR / f"blog-indicators-{run_month}.jsonl"

        already_done = set()
        if resume and indicator_file.exists():
            with open(indicator_file) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                        already_done.add(rec.get("company_unique_id", ""))
                    except:
                        pass
            print(f"Phase 1 resuming: {len(already_done)} done")

        remaining = [c for c in companies if c["company_unique_id"] not in already_done]
        print(f"Phase 1: Checking {len(remaining)} company domains")

        out = open(indicator_file, "a")
        movement = 0
        no_movement = 0
        errors = 0
        start = time.time()

        for idx, c in enumerate(remaining):
            result = check_blog_indicator(c["company_domain"], c["company_name"], proxies)
            result["company_unique_id"] = c["company_unique_id"]
            result["company_name"] = c["company_name"]
            result["company_domain"] = c["company_domain"]

            out.write(json.dumps(result) + "\n")
            out.flush()

            if result["movement"] == 1:
                movement += 1
            elif result.get("error"):
                errors += 1
            else:
                no_movement += 1

            if (idx + 1) % 25 == 0:
                elapsed = time.time() - start
                rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
                print(f"  [{idx+1}/{len(remaining)}] Move:{movement} Static:{no_movement} Err:{errors} | {rate:.0f}/hr")

            if idx < len(remaining) - 1:
                time.sleep(box_muller_delay())

        out.close()
        elapsed = (time.time() - start) / 60
        print(f"\nPhase 1 done in {elapsed:.1f}m | Movement:{movement} Static:{no_movement} Err:{errors}")

    # ── Phase 2 ── (only on companies with movement=1)
    if PHASE in (0, 2):
        indicator_file = OUTPUT_DIR / f"blog-indicators-{run_month}.jsonl"
        signal_file = OUTPUT_DIR / f"blog-signals-{run_month}.jsonl"

        # Load Phase 1 results with movement=1
        movers = []
        if indicator_file.exists():
            with open(indicator_file) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                        if rec.get("movement") == 1:
                            movers.append(rec)
                    except:
                        pass

        if not movers:
            print("Phase 2: No movers to classify.")
            return

        print(f"\nPhase 2: Classifying {len(movers)} companies with movement")

        out = open(signal_file, "a")
        signaled = 0
        start = time.time()

        for idx, m in enumerate(movers):
            result = classify_blog_signals(m["company_domain"], m["company_name"], proxies)
            result["company_unique_id"] = m["company_unique_id"]
            result["company_name"] = m["company_name"]
            result["company_domain"] = m["company_domain"]

            out.write(json.dumps(result) + "\n")
            out.flush()

            if result["signal_count"] > 0:
                signaled += 1
                signals = ", ".join(s["signal"] for s in result["signals"])
                print(f"  [{idx+1}] {m['company_name'][:25]:25s} → {signals}")

        out.close()
        elapsed = (time.time() - start) / 60
        print(f"\nPhase 2 done in {elapsed:.1f}m | Signaled:{signaled}/{len(movers)}")


if __name__ == "__main__":
    main()

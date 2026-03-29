"""
Process 300 — Blog Monitor v2

Rewired from v1: reads from D1 (via wrangler), NOT Neon.
Writes results back to D1 outreach_blog.

Phase 1: Key indicator check via Startpage + DataImpulse proxy.
  - Queries Startpage for `site:domain` per company
  - Checks snippets for freshness indicators (dates, "ago", "today")
  - Binary output: 0 (no change) or 1 (change detected)
  - Writes 0/1 + last_checked back to D1 outreach_blog
  - The URL mapping is the constant. The 0/1 is the variable.

Phase 2: Signal classification (only on 1s).
  - Queries Startpage with signal-specific keywords
  - 6 signals: FUNDING_EVENT, ACQUISITION, LEADERSHIP_CHANGE, EXPANSION, RESTRUCTURING, GENERAL_NEWS
  - AI is NOT used. Detection is deterministic (keyword match).
  - Writes signals back to D1 outreach_blog.

Usage:
  python3 src/blog-monitor-v2.py                          # Full run (Phase 1 + 2)
  python3 src/blog-monitor-v2.py --phase 1                # Phase 1 only (0/1 check)
  python3 src/blog-monitor-v2.py --phase 2                # Phase 2 only (classify 1s)
  python3 src/blog-monitor-v2.py --limit 100              # Test with 100
  python3 src/blog-monitor-v2.py --resume                 # Resume interrupted Phase 1

Env vars: PROXY_USER, PROXY_PASS (DataImpulse credentials)
          D1_DB (default: svg-d1-outreach-ops)
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

D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

PROXY_HOST = os.environ.get("PROXY_HOST", "gw.dataimpulse.com")
PROXY_PORT = os.environ.get("PROXY_PORT", "823")
PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")

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


# ── D1 Access (via wrangler CLI) ────────────────────────────

def d1_query(sql: str) -> list:
    """Execute a read query against D1 via wrangler CLI."""
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql, "--json"],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )
    if result.returncode != 0:
        print(f"D1 query error: {result.stderr[:300]}")
        return []
    try:
        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("results", [])
        return []
    except json.JSONDecodeError:
        # wrangler may prefix non-JSON output
        stdout = result.stdout
        start = stdout.find('[')
        if start >= 0:
            try:
                data = json.loads(stdout[start:])
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("results", [])
            except:
                pass
        print(f"D1 parse error: {stdout[:200]}")
        return []


def d1_execute(sql: str) -> bool:
    """Execute a write statement against D1 via wrangler CLI."""
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )
    if result.returncode != 0:
        print(f"D1 write error: {result.stderr[:300]}")
        return False
    return True


def escape_sql(s: str) -> str:
    """Escape single quotes for SQL."""
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"


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

    try:
        resp = requests.get(url, **kwargs)
    except Exception as e:
        return {"status": 0, "results": [], "error": str(e)}

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

def check_blog_indicator(company_domain: str, proxies: dict | None) -> dict:
    """Check if a company's website has been recently indexed.
    Returns 0 (no change) or 1 (change detected)."""
    fetched_at = datetime.now(timezone.utc).isoformat()

    query = f"site:{company_domain}"
    result = search_startpage(query, proxies)

    if result["error"]:
        return {"movement": 0, "error": result["error"], "fetched_at": fetched_at}

    if not result["results"]:
        return {"movement": 0, "reason": "NOT_INDEXED", "fetched_at": fetched_at}

    # Check for freshness indicators in snippets
    fresh_keywords = ["2026", "2025", "ago", "today", "yesterday",
                      "this week", "this month", "mar", "feb", "jan"]
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

def classify_blog_signals(company_domain: str, proxies: dict | None) -> dict:
    """Search for specific signal types on a company's domain. Only fires on 1s."""
    fetched_at = datetime.now(timezone.utc).isoformat()
    detected_signals = []

    for signal_name, signal_def in SIGNALS.items():
        keywords = " OR ".join(f'"{kw}"' for kw in signal_def["keywords"][:3])
        query = f'site:{company_domain} {keywords}'

        result = search_startpage(query, proxies)
        time.sleep(box_muller_delay())

        if result["error"] or not result["results"]:
            continue

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

    # ── Load companies from D1 (NOT Neon) ────────────────────
    print(f"Loading companies from D1 ({D1_DB})...")

    sql = "SELECT oo.outreach_id, oo.domain FROM outreach_outreach oo WHERE oo.domain IS NOT NULL"
    if LIMIT:
        sql += f" LIMIT {LIMIT}"

    companies = d1_query(sql)
    if not companies:
        print("No companies with domains found in D1.")
        sys.exit(0)

    print(f"Loaded {len(companies)} companies with domains")
    print(f"Mode: {'PROXY' if proxies else 'DIRECT'}")
    print(f"Phase: {'BOTH' if PHASE == 0 else PHASE}")

    run_month = datetime.now().strftime("%Y-%m")

    # ── Phase 1: Binary movement detection (0/1) ────────────
    if PHASE in (0, 1):
        indicator_file = OUTPUT_DIR / f"blog-indicators-{run_month}.jsonl"

        already_done = set()
        if resume and indicator_file.exists():
            with open(indicator_file) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                        already_done.add(rec.get("outreach_id", ""))
                    except:
                        pass
            print(f"Phase 1 resuming: {len(already_done)} done")

        remaining = [c for c in companies if c["outreach_id"] not in already_done]
        print(f"Phase 1: Checking {len(remaining)} company domains")

        out = open(indicator_file, "a")
        movement = 0
        no_movement = 0
        errors = 0
        d1_updates = 0
        start = time.time()

        for idx, c in enumerate(remaining):
            result = check_blog_indicator(c["domain"], proxies)
            result["outreach_id"] = c["outreach_id"]
            result["domain"] = c["domain"]

            out.write(json.dumps(result) + "\n")
            out.flush()

            # Write 0/1 + last_checked back to D1
            now = datetime.now(timezone.utc).isoformat()
            reason = result.get('reason', '').replace("'", "''")
            summary_json = json.dumps({
                "movement": result["movement"],
                "last_checked": now,
                "reason": reason,
            }).replace("'", "''")
            update_sql = (
                f"UPDATE outreach_blog SET "
                f"context_summary = '{summary_json}' "
                f"WHERE outreach_id = {escape_sql(c['outreach_id'])}"
            )
            if d1_execute(update_sql):
                d1_updates += 1

            if result["movement"] == 1:
                movement += 1
            elif result.get("error"):
                errors += 1
            else:
                no_movement += 1

            if (idx + 1) % 25 == 0:
                elapsed = time.time() - start
                rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
                print(f"  [{idx+1}/{len(remaining)}] Move:{movement} Static:{no_movement} Err:{errors} D1:{d1_updates} | {rate:.0f}/hr")

            if idx < len(remaining) - 1:
                time.sleep(box_muller_delay())

        out.close()
        elapsed = (time.time() - start) / 60
        print(f"\nPhase 1 done in {elapsed:.1f}m | Movement:{movement} Static:{no_movement} Err:{errors} D1:{d1_updates}")

    # ── Phase 2: Signal classification (only on 1s) ─────────
    if PHASE in (0, 2):
        indicator_file = OUTPUT_DIR / f"blog-indicators-{run_month}.jsonl"
        signal_file = OUTPUT_DIR / f"blog-signals-{run_month}.jsonl"

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

        print(f"\nPhase 2: Classifying {len(movers)} companies with movement=1")

        out = open(signal_file, "a")
        signaled = 0
        d1_updates = 0
        start = time.time()

        for idx, m in enumerate(movers):
            result = classify_blog_signals(m["domain"], proxies)
            result["outreach_id"] = m["outreach_id"]
            result["domain"] = m["domain"]

            out.write(json.dumps(result) + "\n")
            out.flush()

            # Write signals back to D1
            if result["signal_count"] > 0:
                signaled += 1
                now = datetime.now(timezone.utc).isoformat()
                summary_json = json.dumps({
                    "movement": 1,
                    "last_checked": now,
                    "signals": result["signals"],
                    "signals_checked_at": now,
                }).replace("'", "''")
                update_sql = (
                    f"UPDATE outreach_blog SET "
                    f"context_summary = '{summary_json}' "
                    f"WHERE outreach_id = {escape_sql(m['outreach_id'])}"
                )
                if d1_execute(update_sql):
                    d1_updates += 1

                signals = ", ".join(s["signal"] for s in result["signals"])
                print(f"  [{idx+1}] {m['domain'][:30]:30s} → {signals}")

        out.close()
        elapsed = (time.time() - start) / 60
        print(f"\nPhase 2 done in {elapsed:.1f}m | Signaled:{signaled}/{len(movers)} D1:{d1_updates}")


if __name__ == "__main__":
    main()

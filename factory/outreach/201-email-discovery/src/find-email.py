"""
Process 201 — Find Email (Gate Chain: Pattern Generate -> Hunter Promote -> Startpage Search)

Fills person_email on slot_workbench slots that have a name but no email.
Three gates in priority order:
  A) Pattern generate — deterministic email from hunter_email_pattern + name + domain (free)
  B) Hunter promote — if hunter_email exists with confidence >= 80, promote it (free)
  C) Startpage search — natural language search for email (free, uses proxy)

All emails stored for now. Million Verifier integration is separate (future gate).

Reads/writes D1 slot_workbench via wrangler subprocess.

Usage:
  python3 src/find-email.py --limit 20
  python3 src/find-email.py --limit 100 --offset 50 --port-base 10100
  python3 src/find-email.py --gate a          # only run Gate A
  python3 src/find-email.py --gate all        # run all gates (default)
  python3 src/find-email.py --resume
  python3 src/find-email.py --dry-run         # no D1 writes

Env vars: PROXY_USER, PROXY_PASS (required for Gate C)
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

# ── Config ───────────────────────────────────────────────────

LIMIT = 0
OFFSET = 0
DRY_RUN = False
GATE = "all"  # a, b, c, all
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

REPO_ROOT = Path(__file__).resolve().parents[4]
D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD", str(REPO_ROOT))
NPX_CMD = os.environ.get("NPX_CMD") or shutil.which("npx.cmd") or shutil.which("npx") or "npx"

PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT_BASE = 10060  # Dedicated range for 201
QUERIES_PER_IP = 50
SEARCH_DELAY = 3

# Standard email patterns — ordered by frequency
# ~60% of companies use first.last@domain
STANDARD_PATTERNS = [
    "{first}.{last}",
    "{first}{last}",
    "{fi}{last}",
    "{first}",
    "{last}.{first}",
]

# Hunter/vendor pattern tokens → format strings
PATTERN_MAP = {
    "{first}.{last}":   "{first}.{last}",
    "{f}{last}":        "{fi}{last}",
    "{first}{last}":    "{first}{last}",
    "{first}_{last}":   "{first}_{last}",
    "{last}.{first}":   "{last}.{first}",
    "{last}{first}":    "{last}{first}",
    "{last}":           "{last}",
    "{first}":          "{first}",
    "{f}.{last}":       "{fi}.{last}",
    "{last}{f}":        "{last}{fi}",
    "{first}.{l}":      "{first}.{la}",
    "{fi}{last}":       "{fi}{last}",
}


# ── Parse args ───────────────────────────────────────────────

args = sys.argv[1:]
resume = False
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1])
        i += 2
    elif args[i] == "--offset" and i + 1 < len(args):
        OFFSET = int(args[i + 1])
        i += 2
    elif args[i] == "--port-base" and i + 1 < len(args):
        PROXY_PORT_BASE = int(args[i + 1])
        i += 2
    elif args[i] == "--gate" and i + 1 < len(args):
        GATE = args[i + 1].lower()
        i += 2
    elif args[i] == "--resume":
        resume = True
        i += 1
    elif args[i] == "--dry-run":
        DRY_RUN = True
        i += 1
    else:
        i += 1


# ── D1 Access ────────────────────────────────────────────────

def d1_query(sql, db=None):
    """Query D1 via wrangler CLI, return list of row dicts."""
    db = db or D1_DB
    sql = re.sub(r"[\r\n\t]+", " ", sql).strip()
    result = subprocess.run(
        [NPX_CMD, "wrangler", "d1", "execute", db, "--remote", "--command", sql, "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=WRANGLER_CWD
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
    """Execute a write statement against D1. Returns True on success."""
    db = db or D1_DB
    if DRY_RUN:
        return True
    sql = re.sub(r"[\r\n\t]+", " ", sql).strip()
    result = subprocess.run(
        [NPX_CMD, "wrangler", "d1", "execute", db, "--remote", "--command", sql],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=WRANGLER_CWD
    )
    return result.returncode == 0


def escape_sql(s):
    """Escape a value for SQL insertion."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


# ── Proxy ────────────────────────────────────────────────────

def get_proxy_url(query_num=0):
    """Get rotating proxy URL. Port rotates every QUERIES_PER_IP queries."""
    port = PROXY_PORT_BASE + (query_num // QUERIES_PER_IP)
    return f"http://{PROXY_USER}__cr.us:{PROXY_PASS}@{PROXY_HOST}:{port}"


# ── Gate A: Pattern Generate ────────────────────────────────

def apply_pattern(pattern_str, first_name, last_name, domain):
    """Apply a hunter/vendor email pattern to generate an email address.

    Pattern examples from Hunter: "{first}.{last}", "{f}{last}", "{first}"
    We map these to Python format strings and fill with the name parts.
    """
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    fi = first[0] if first else ""
    la = last[0] if last else ""

    if not first or not last or not domain:
        return None

    # Normalize pattern: strip @domain if present (we add it ourselves)
    pat = pattern_str.strip().lower()
    if "@" in pat:
        pat = pat.split("@")[0]

    # Try mapping known patterns
    fmt = PATTERN_MAP.get(pat, pat)

    try:
        local = fmt.format(first=first, last=last, fi=fi, la=la, f=fi, l=la)
        return f"{local}@{domain}"
    except (KeyError, IndexError):
        # If pattern has unknown tokens, fall back to standard first.last
        return f"{first}.{last}@{domain}"


def generate_from_pattern(slot):
    """Gate A: Generate email from known email pattern + name + domain.

    Returns (email, source_detail) or (None, None).
    """
    pattern = slot.get("hunter_email_pattern") or slot.get("vendor_email_pattern")
    first = slot.get("person_first_name") or ""
    last = slot.get("person_last_name") or ""
    domain = slot.get("domain") or slot.get("company_domain") or ""

    if not pattern or not first or not last or not domain:
        return None, None

    email = apply_pattern(pattern, first, last, domain)
    if email:
        return email, f"pattern_generate:{pattern}"
    return None, None


# ── Gate B: Hunter Promote ──────────────────────────────────

def promote_hunter(slot):
    """Gate B: Promote hunter_email if confidence >= 80.

    Returns (email, source_detail) or (None, None).
    """
    hunter_email = slot.get("hunter_email")
    confidence = slot.get("hunter_confidence")

    if not hunter_email:
        return None, None

    try:
        conf = int(confidence) if confidence is not None else 0
    except (ValueError, TypeError):
        conf = 0

    if conf >= 80:
        return hunter_email, f"hunter_promote:conf={conf}"
    return None, None


# ── Gate C: Startpage Search ────────────────────────────────

def search_startpage(session, slot, proxy_url):
    """Gate C: Search Startpage for person's email using natural language query.

    Query pattern: {first_name} {last_name} {company_name} email contact
    For common names add: {city} {state}

    Returns (email, source_detail) or (None, None).
    """
    first = slot.get("person_first_name") or ""
    last = slot.get("person_last_name") or ""
    company = slot.get("canonical_name") or slot.get("company_name") or ""
    domain = slot.get("domain") or slot.get("company_domain") or ""
    city = slot.get("city") or ""
    state = slot.get("state") or ""

    if not first or not last or not company:
        return None, None

    # Build query — natural language = zero CAPTCHA
    query = f"{first} {last} {company} email contact"

    # For common first names, add location to narrow results
    common_names = {"john", "james", "robert", "michael", "david", "william",
                    "richard", "joseph", "thomas", "charles", "mary", "jennifer",
                    "linda", "patricia", "elizabeth", "barbara", "susan", "jessica",
                    "sarah", "karen", "mark", "chris", "mike", "steve", "jeff",
                    "brian", "scott", "kevin", "jason", "matt", "tim", "dan"}
    if first.lower() in common_names and city:
        query = f"{first} {last} {company} {city} {state} email contact"

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
        return None, f"startpage_error:{str(e)[:60]}"

    if "captcha" in resp.text.lower():
        return None, "startpage_captcha"

    # Extract all email addresses from results
    emails = list(set(re.findall(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resp.text
    )))
    # Filter noise
    emails = [e for e in emails if not any(x in e.lower() for x in
        ['startpage', 'sentry', 'webpack', 'css', 'javascript', 'example.com',
         'noreply', 'no-reply', 'donotreply', 'postmaster', 'mailer-daemon'])]

    if not emails:
        return None, "startpage_no_emails"

    # Score emails: prefer ones matching our domain and name parts
    first_l = first.lower()
    last_l = last.lower()

    def score_email(email):
        e = email.lower()
        s = 0
        # Domain match is strongest signal
        if domain and domain.lower() in e:
            s += 100
        # Name parts in local portion
        local = e.split("@")[0]
        if first_l in local:
            s += 30
        if last_l in local:
            s += 30
        if first_l[0] in local:
            s += 5
        return s

    scored = sorted(emails, key=score_email, reverse=True)
    best = scored[0]

    # Only accept if it scores reasonably (at minimum domain or name match)
    if score_email(best) >= 30:
        return best, f"startpage_201:q={query[:80]}"

    return None, f"startpage_low_confidence:best={best}"


# ── Readiness Tier Calculator ───────────────────────────────

def calc_readiness_tier(slot, has_email_now):
    """Recalculate readiness_tier based on current slot state.

    Tier logic (from Neon view):
      T1 = has_name + has_email + has_linkedin (full)
      T2 = has_name + has_email (email only)
      T3 = has_name only
      T4 = empty slot
    """
    has_name = bool(slot.get("has_name"))
    has_email = has_email_now or bool(slot.get("has_email"))
    has_linkedin = bool(slot.get("has_linkedin"))

    if has_name and has_email and has_linkedin:
        return "T1"
    elif has_name and has_email:
        return "T2"
    elif has_name:
        return "T3"
    else:
        return "T4"


# ── Main ─────────────────────────────────────────────────────

def main():
    print("Process 201 -- Find Email (Gate Chain: A->B->C)")
    print(f"Limit: {LIMIT or 'ALL'} | Offset: {OFFSET} | Gate: {GATE} | "
          f"Dry-run: {DRY_RUN} | Resume: {resume}")
    print()

    gates_to_run = []
    if GATE == "all":
        gates_to_run = ["a", "b", "c"]
    elif GATE in ("a", "b", "c"):
        gates_to_run = [GATE]
    else:
        print(f"ERROR: Invalid --gate value '{GATE}'. Use a, b, c, or all.")
        sys.exit(1)

    # Gate C requires proxy
    if "c" in gates_to_run and (not PROXY_USER or not PROXY_PASS):
        print("WARNING: PROXY_USER and PROXY_PASS required for Gate C (Startpage).")
        print("         Gate C will be skipped.")
        gates_to_run = [g for g in gates_to_run if g != "c"]

    if not gates_to_run:
        print("ERROR: No gates to run.")
        sys.exit(1)

    print(f"Active gates: {', '.join(g.upper() for g in gates_to_run)}")
    print()

    # ── Load slots from slot_workbench ───────────────────────
    limit_clause = f"LIMIT {LIMIT}" if LIMIT else ""
    offset_clause = f"OFFSET {OFFSET}" if OFFSET else ""

    print("Loading slots from slot_workbench (has_name=1, has_email=0)...")
    slots = d1_query(f"""
        SELECT slot_id, outreach_id, company_unique_id, slot_type,
            person_unique_id, person_first_name, person_last_name, person_full_name,
            company_name, canonical_name, domain, company_domain,
            city, state,
            hunter_email_pattern, vendor_email_pattern,
            hunter_email, hunter_confidence,
            person_email, person_email_verified, person_source,
            has_name, has_email, has_verified_email, has_linkedin,
            has_email_pattern, has_hunter_candidate,
            readiness_tier
        FROM slot_workbench
        WHERE has_name = 1 AND has_email = 0
        ORDER BY outreach_id
        {limit_clause} {offset_clause}
    """)

    if not slots:
        print("No slots needing email discovery.")
        return

    print(f"{len(slots)} slots need email")
    print()

    # ── Resume support ───────────────────────────────────────
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

    # ── Session for Gate C ───────────────────────────────────
    session = None
    if "c" in gates_to_run:
        session = creq.Session(impersonate="chrome131")

    out = open(output_file, "a")

    # Counters
    stats = {
        "gate_a_hits": 0,
        "gate_b_hits": 0,
        "gate_c_hits": 0,
        "gate_c_captcha": 0,
        "misses": 0,
        "d1_writes": 0,
        "skipped_data": 0,
    }
    start_time = time.time()

    for idx, slot in enumerate(remaining):
        slot_id = slot["slot_id"]
        oid = slot["outreach_id"]
        first = slot.get("person_first_name") or ""
        last = slot.get("person_last_name") or ""
        domain = slot.get("domain") or slot.get("company_domain") or ""

        record = {
            "slot_id": slot_id,
            "outreach_id": oid,
            "slot_type": slot.get("slot_type"),
            "person": f"{first} {last}".strip(),
            "domain": domain,
            "result": "miss",
            "gate": None,
            "email": None,
            "source": None,
            "ts": datetime.now(timezone.utc).isoformat(),
        }

        if not first or not last:
            record["result"] = "skip_missing_name"
            stats["skipped_data"] += 1
            out.write(json.dumps(record) + "\n")
            out.flush()
            continue

        found_email = None
        found_source = None
        found_gate = None

        # ── Gate A: Pattern Generate ──────────────────────────
        if "a" in gates_to_run and not found_email:
            email, source = generate_from_pattern(slot)
            if email:
                found_email = email
                found_source = source
                found_gate = "A"
                stats["gate_a_hits"] += 1

        # ── Gate B: Hunter Promote ────────────────────────────
        if "b" in gates_to_run and not found_email:
            email, source = promote_hunter(slot)
            if email:
                found_email = email
                found_source = source
                found_gate = "B"
                stats["gate_b_hits"] += 1

        # ── Gate C: Startpage Search ──────────────────────────
        if "c" in gates_to_run and not found_email:
            proxy_url = get_proxy_url(idx)
            email, source = search_startpage(session, slot, proxy_url)
            if source and "captcha" in source:
                stats["gate_c_captcha"] += 1
                record["gate_c_detail"] = source
            if email:
                found_email = email
                found_source = source
                found_gate = "C"
                stats["gate_c_hits"] += 1
            # Delay between searches to avoid CAPTCHA
            if idx < len(remaining) - 1:
                time.sleep(random.uniform(SEARCH_DELAY, SEARCH_DELAY + 2))

        # ── Write result ─────────────────────────────────────
        if found_email:
            record["result"] = "found"
            record["gate"] = found_gate
            record["email"] = found_email
            record["source"] = found_source

            new_tier = calc_readiness_tier(slot, has_email_now=True)

            # Write to D1
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            update_sql = (
                f"UPDATE slot_workbench SET "
                f"person_email = {escape_sql(found_email)}, "
                f"has_email = 1, "
                f"person_source = {escape_sql(found_source)}, "
                f"email_last_checked_at = {escape_sql(now)}, "
                f"email_changed = 1, "
                f"readiness_tier = {escape_sql(new_tier)} "
                f"WHERE slot_id = {escape_sql(slot_id)}"
            )
            if d1_execute(update_sql):
                stats["d1_writes"] += 1
                record["d1_written"] = True
                record["new_tier"] = new_tier
        else:
            stats["misses"] += 1

        out.write(json.dumps(record) + "\n")
        out.flush()

        # ── Progress report every 10 slots ────────────────────
        if (idx + 1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = (idx + 1) / elapsed * 3600 if elapsed > 0 else 0
            total_found = stats["gate_a_hits"] + stats["gate_b_hits"] + stats["gate_c_hits"]
            print(
                f"  [{idx+1}/{len(remaining)}] "
                f"A:{stats['gate_a_hits']} B:{stats['gate_b_hits']} C:{stats['gate_c_hits']} "
                f"Miss:{stats['misses']} CAPTCHA:{stats['gate_c_captcha']} "
                f"D1:{stats['d1_writes']} | {rate:.0f}/hr"
            )

        # Small delay between non-search slots (Gate A/B are instant)
        if found_gate in ("A", "B") and idx < len(remaining) - 1:
            time.sleep(0.1)

    out.close()
    if session:
        session.close()

    # ── Final report ──────────────────────────────────────────
    elapsed_min = (time.time() - start_time) / 60
    total_found = stats["gate_a_hits"] + stats["gate_b_hits"] + stats["gate_c_hits"]
    total_processed = total_found + stats["misses"] + stats["skipped_data"]

    print()
    print("=" * 60)
    print(f"Process 201 -- COMPLETE in {elapsed_min:.1f}m")
    print(f"  Processed:   {total_processed}")
    print(f"  Gate A hits: {stats['gate_a_hits']} (pattern generate)")
    print(f"  Gate B hits: {stats['gate_b_hits']} (hunter promote)")
    print(f"  Gate C hits: {stats['gate_c_hits']} (startpage search)")
    print(f"  Misses:      {stats['misses']}")
    print(f"  Skipped:     {stats['skipped_data']} (missing data)")
    print(f"  D1 writes:   {stats['d1_writes']}")
    print(f"  CAPTCHA:     {stats['gate_c_captcha']}")
    if total_processed > 0:
        print(f"  Hit rate:    {total_found / total_processed * 100:.1f}%")
        if stats["gate_a_hits"] + stats["gate_b_hits"] + stats["gate_c_hits"] > 0:
            print(f"  Gate split:  A={stats['gate_a_hits']} "
                  f"({stats['gate_a_hits']/max(total_found,1)*100:.0f}%) | "
                  f"B={stats['gate_b_hits']} "
                  f"({stats['gate_b_hits']/max(total_found,1)*100:.0f}%) | "
                  f"C={stats['gate_c_hits']} "
                  f"({stats['gate_c_hits']/max(total_found,1)*100:.0f}%)")
    run_tag = datetime.now().strftime("%Y-%m-%d")
    print(f"  Output:      {OUTPUT_DIR / f'find-email-{run_tag}.jsonl'}")
    print("=" * 60)


if __name__ == "__main__":
    main()

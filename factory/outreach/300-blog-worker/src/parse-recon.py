"""
Process 300 — Parse Recon Results → Fill Workbench

Reads raw JSONL from company-recon.py, parses names/titles/URLs,
matches to slots, writes back to D1 slot_workbench.

For each company:
  1. Pick best leadership/about URL → about_url
  2. Pick company LinkedIn → company_domain (or new column)
  3. Map name+title patterns to CEO/CFO/HR slots
  4. Match LinkedIn URLs to names (slug → name)
  5. Update workbench: person fields, timestamps, readiness tier

Usage:
  python3 src/parse-recon.py                    # parse all JSONL files
  python3 src/parse-recon.py --dry-run          # show what would change
  python3 src/parse-recon.py --limit 100        # only first 100 companies

Env vars: D1_DB
"""

import json
import re
import sys
import os
import subprocess
import glob
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# ── Config ───────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).parent / "output"
D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

DRY_RUN = False
LIMIT = 0

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--dry-run":
        DRY_RUN = True
        i += 1
    elif args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1])
        i += 2
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
        ["npx", "wrangler", "d1", "execute", db, "--remote", "--command", sql, "--json"],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("meta", {}).get("changes", 0)
    except:
        pass
    return None


# ── Title → Slot Type Mapping ────────────────────────────────

CEO_PATTERNS = re.compile(
    r'\b(CEO|chief executive|president|owner|founder|managing director|'
    r'managing partner|principal|general manager|executive director|'
    r'co-founder|cofounder)\b', re.IGNORECASE
)

CFO_PATTERNS = re.compile(
    r'\b(CFO|chief financial|finance director|VP finance|'
    r'controller|comptroller|treasurer|accounting director|'
    r'finance manager|director of finance)\b', re.IGNORECASE
)

HR_PATTERNS = re.compile(
    r'\b(HR|human resource|benefits|people officer|chief people|'
    r'talent|personnel|CHRO|VP people|director.{0,10}people|'
    r'employee relations|workforce|HR director|HR manager)\b', re.IGNORECASE
)

# Titles to REJECT — these are not decision makers for benefits
REJECT_PATTERNS = re.compile(
    r'\b(intern|student|assistant|coordinator|specialist|analyst|'
    r'associate|junior|entry.level|receptionist|clerk|'
    r'sales rep|real estate|realtor|recruiter|engineer|'
    r'marketing.manager|software|developer|designer)\b', re.IGNORECASE
)


def map_title_to_slot(title_text):
    """Map a title/context string to CEO, CFO, or HR. Returns None if no match."""
    if not title_text:
        return None
    if REJECT_PATTERNS.search(title_text):
        return None
    if CEO_PATTERNS.search(title_text):
        return "CEO"
    if CFO_PATTERNS.search(title_text):
        return "CFO"
    if HR_PATTERNS.search(title_text):
        return "HR"
    return None


# ── LinkedIn Slug → Name ─────────────────────────────────────

def linkedin_slug_to_name(url):
    """Extract a plausible name from a LinkedIn /in/ URL slug."""
    m = re.search(r'linkedin\.com/in/([^/?#]+)', url)
    if not m:
        return None
    slug = m.group(1).rstrip('/')
    # Skip company-like slugs
    if any(x in slug.lower() for x in ['llc', 'inc', 'corp', 'company', 'agency', 'group']):
        return None
    # Remove trailing numbers/hashes (e.g., "john-smith-12345678")
    slug = re.sub(r'-[0-9a-f]{6,}$', '', slug)
    slug = re.sub(r'-\d+$', '', slug)
    # Split on hyphens
    parts = slug.split('-')
    if len(parts) < 2:
        return None
    # Capitalize
    parts = [p.capitalize() for p in parts if len(p) > 1]
    if len(parts) < 2:
        return None
    return {"first_name": parts[0], "last_name": parts[-1], "full_name": " ".join(parts)}


# ── Pick Best About URL ─────────────────────────────────────

def pick_about_url(leadership_urls, domain):
    """Pick the best leadership/about page URL, preferring the company's own domain."""
    if not leadership_urls:
        return None
    # Prefer URLs on the company's own domain
    own_domain = [u for u in leadership_urls if domain and domain.lower() in u.lower()]
    if own_domain:
        # Prefer /leadership or /team over /about or /contact
        for kw in ['leadership', 'team', 'our-team', 'staff', 'executive']:
            for u in own_domain:
                if kw in u.lower():
                    return u
        return own_domain[0]
    # Fallback to any leadership URL
    return leadership_urls[0]


# ── Main ─────────────────────────────────────────────────────

def main():
    print("Process 300 — Parse Recon Results → Fill Workbench")
    print(f"Dry run: {DRY_RUN} | Limit: {LIMIT or 'ALL'}")
    print()

    # Load all JSONL files
    files = sorted(glob.glob(str(OUTPUT_DIR / "company-recon-*-w*.jsonl")))
    if not files:
        # Also try non-worker files
        files = sorted(glob.glob(str(OUTPUT_DIR / "company-recon-*.jsonl")))

    if not files:
        print("No JSONL files found.")
        return

    print(f"Loading from {len(files)} JSONL files...")
    records = []
    for f in files:
        with open(f) as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                    if r.get("status") == "captured":
                        records.append(r)
                except:
                    pass

    print(f"Loaded {len(records):,} captured records")
    if LIMIT:
        records = records[:LIMIT]
    print()

    # Load current workbench state — need slot_id per outreach_id + slot_type
    print("Loading workbench slots from D1...")
    slots = d1_query("""
        SELECT slot_id, outreach_id, slot_type, is_filled,
               person_first_name, person_email, person_linkedin,
               about_url, readiness_tier
        FROM slot_workbench
    """)

    # Index: outreach_id → {slot_type → slot_data}
    slot_index = defaultdict(dict)
    for s in slots:
        slot_index[s["outreach_id"]][s["slot_type"]] = s
    print(f"Loaded {len(slots):,} slots for {len(slot_index):,} companies")
    print()

    # ── Parse and match ──────────────────────────────────────
    now_ts = datetime.now(timezone.utc).isoformat()

    stats = {
        "companies_processed": 0,
        "about_url_updates": 0,
        "slots_filled_name": 0,
        "slots_filled_linkedin": 0,
        "slots_filled_email": 0,
        "slots_already_filled": 0,
        "no_match": 0,
    }

    # Collect all SQL updates, batch execute
    updates = []

    for rec in records:
        oid = rec["outreach_id"]
        domain = rec.get("domain", "") or ""
        company_slots = slot_index.get(oid, {})

        if not company_slots:
            continue

        stats["companies_processed"] += 1

        # 1. About URL — update if we don't have one
        leadership_urls = rec.get("leadership_urls", [])
        best_about = pick_about_url(leadership_urls, domain)
        if best_about:
            for slot_type, slot in company_slots.items():
                if not slot.get("about_url"):
                    safe_url = best_about.replace("'", "''")
                    updates.append(
                        f"UPDATE slot_workbench SET about_url = '{safe_url}', "
                        f"last_recon_at = '{now_ts}' "
                        f"WHERE slot_id = '{slot['slot_id']}'"
                    )
                    stats["about_url_updates"] += 1

        # 2. Parse LinkedIn people URLs first (needed by title matching below)
        linkedin_people = rec.get("linkedin_people", [])

        # 3. Parse name+title patterns → slot candidates
        name_titles = rec.get("name_title_patterns", [])
        candidates = defaultdict(list)  # slot_type → [{"name":..., "context":...}]

        for nt in name_titles:
            name = nt.get("name", "")
            context = nt.get("context", "")
            slot_type = map_title_to_slot(context)
            if slot_type and name:
                candidates[slot_type].append(nt)

        # 2b. Also check LinkedIn people for names we can match to Hunter data
        #     If Hunter has a contact for this company with a matching name + title,
        #     use Hunter's title for slot mapping
        if not candidates.get("CEO") or not candidates.get("CFO") or not candidates.get("HR"):
            for li_url in linkedin_people:
                parsed = linkedin_slug_to_name(li_url)
                if not parsed:
                    continue
                # Check if this name appears in our name_title list (even without a slot match)
                li_first = parsed["first_name"].lower()
                li_last = parsed["last_name"].lower()
                for nt in name_titles:
                    nt_name = nt.get("name", "").lower()
                    if li_first in nt_name and li_last in nt_name:
                        # Name matches — check context for any title hint
                        context = nt.get("context", "")
                        # LinkedIn format: "Company | LinkedIn" — no title, but we have the person
                        # Check if context has a title embedded before " at " or " - "
                        title_match = re.search(r'^(.+?)(?:\s+at\s+|\s*[-|]\s*)', context)
                        if title_match:
                            slot_type = map_title_to_slot(title_match.group(1))
                            if slot_type and slot_type not in candidates:
                                candidates[slot_type].append({
                                    "name": parsed["full_name"],
                                    "context": context,
                                    "linkedin_url": li_url,
                                })
                        break

        # 4. Parse LinkedIn URLs → names
        li_name_map = {}  # "first last" → linkedin_url
        for li_url in linkedin_people:
            parsed = linkedin_slug_to_name(li_url)
            if parsed:
                key = f"{parsed['first_name'].lower()} {parsed['last_name'].lower()}"
                li_name_map[key] = {"url": li_url, **parsed}

        # 4. Try to match LinkedIn URLs to name+title candidates
        for slot_type, cands in candidates.items():
            slot = company_slots.get(slot_type)
            if not slot:
                continue

            # Skip if slot already has a person with email
            if slot.get("is_filled") and slot.get("person_email"):
                stats["slots_already_filled"] += 1
                continue

            best = cands[0]  # First match (highest in search results = most relevant)
            name = best["name"]
            parts = name.split()
            if len(parts) < 2:
                continue

            first_name = parts[0]
            last_name = parts[-1]
            full_name = name

            # Try to find matching LinkedIn
            name_key = f"{first_name.lower()} {last_name.lower()}"
            li_match = li_name_map.get(name_key)
            linkedin_url = li_match["url"] if li_match else None

            # Check for email in the recon results that matches this person
            emails = rec.get("emails", [])
            matched_email = None
            email_pattern = rec.get("hunter_email_pattern", "")
            if email_pattern and domain:
                # Generate email from pattern
                generated = email_pattern.replace("{first}", first_name.lower()) \
                    .replace("{last}", last_name.lower()) \
                    .replace("{f}", first_name[0].lower()) \
                    .replace("{l}", last_name[0].lower())
                generated = f"{generated}@{domain}"
                matched_email = generated
            elif emails:
                # See if any found email contains this person's name
                for e in emails:
                    e_lower = e.lower()
                    if first_name.lower() in e_lower or last_name.lower() in e_lower:
                        matched_email = e
                        break

            # Build UPDATE
            safe_first = first_name.replace("'", "''")
            safe_last = last_name.replace("'", "''")
            safe_full = full_name.replace("'", "''")
            safe_title = best.get("context", "").replace("'", "''")[:100]

            set_parts = [
                f"person_first_name = '{safe_first}'",
                f"person_last_name = '{safe_last}'",
                f"person_full_name = '{safe_full}'",
                f"person_source = 'startpage_recon_300'",
                f"person_found_at = '{now_ts}'",
                f"last_recon_at = '{now_ts}'",
                f"has_name = 1",
            ]
            stats["slots_filled_name"] += 1

            if linkedin_url:
                safe_li = linkedin_url.replace("'", "''")
                set_parts.append(f"person_linkedin = '{safe_li}'")
                set_parts.append(f"has_linkedin = 1")
                set_parts.append(f"linkedin_found_at = '{now_ts}'")
                stats["slots_filled_linkedin"] += 1

            if matched_email:
                safe_email = matched_email.replace("'", "''")
                set_parts.append(f"person_email = '{safe_email}'")
                set_parts.append(f"has_email = 1")
                set_parts.append(f"email_found_at = '{now_ts}'")
                stats["slots_filled_email"] += 1

            # Update readiness tier
            if matched_email and linkedin_url:
                set_parts.append("readiness_tier = 'REACHABLE'")
            elif matched_email or linkedin_url:
                set_parts.append("readiness_tier = 'REACHABLE'")
            else:
                set_parts.append("readiness_tier = 'NAME_ONLY'")

            updates.append(
                f"UPDATE slot_workbench SET {', '.join(set_parts)} "
                f"WHERE slot_id = '{slot['slot_id']}'"
            )

        # 5. For slots with no title match, try LinkedIn-only fill
        for slot_type in ["CEO", "CFO", "HR"]:
            if slot_type in candidates:
                continue  # Already handled above
            slot = company_slots.get(slot_type)
            if not slot or (slot.get("is_filled") and slot.get("person_email")):
                continue

            # Look for LinkedIn profiles that might match this slot
            for li_url in linkedin_people:
                parsed = linkedin_slug_to_name(li_url)
                if not parsed:
                    continue
                # We have a LinkedIn person but no title match — store as candidate
                # Don't fill the slot yet, just record the LinkedIn URL was found
                break

        # Mark timestamp even if no person found
        if not candidates:
            stats["no_match"] += 1
            for slot_type, slot in company_slots.items():
                updates.append(
                    f"UPDATE slot_workbench SET last_recon_at = '{now_ts}' "
                    f"WHERE slot_id = '{slot['slot_id']}'"
                )

    # ── Execute updates ──────────────────────────────────────
    print(f"Parsed {stats['companies_processed']:,} companies")
    print(f"Updates to execute: {len(updates):,}")
    print()
    print(f"RESULTS:")
    print(f"  About URL updates:     {stats['about_url_updates']:>6,}")
    print(f"  Slots filled (name):   {stats['slots_filled_name']:>6,}")
    print(f"  Slots filled (LinkedIn): {stats['slots_filled_linkedin']:>6,}")
    print(f"  Slots filled (email):  {stats['slots_filled_email']:>6,}")
    print(f"  Already filled:        {stats['slots_already_filled']:>6,}")
    print(f"  No match:              {stats['no_match']:>6,}")
    print()

    if DRY_RUN:
        print("[DRY RUN] No changes written.")
        # Show sample updates
        for u in updates[:5]:
            print(f"  {u[:120]}...")
        return

    # Execute in batches of 50
    print("Writing to D1...")
    written = 0
    failed = 0
    for i in range(0, len(updates), 50):
        batch = updates[i:i+50]
        # Combine into one multi-statement (D1 supports this via semicolons)
        combined = "; ".join(batch)
        result = d1_execute(combined)
        if result is not None:
            written += len(batch)
        else:
            # Fall back to individual statements
            for stmt in batch:
                r = d1_execute(stmt)
                if r is not None:
                    written += 1
                else:
                    failed += 1

        if (i + 50) % 500 == 0:
            print(f"  [{written:,}/{len(updates):,}] written...")

    print(f"\nDone. Written: {written:,} | Failed: {failed:,}")


if __name__ == "__main__":
    main()

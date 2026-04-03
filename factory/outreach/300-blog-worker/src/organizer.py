"""
Process 300 — Step 2: ORGANIZER
C&V Gate on raw recon_name_titles data.

Applies three questions to every entry in recon_name_titles:
  1. Can you NAME it as a person? → first+last name pattern
  2. Can you define its FORMAT as a title? → matches title taxonomy
  3. Is it the VALUE (company name, garbage)? → reject

Sorts into three piles per slot:
  - recon_organized_people: entries with extractable person name + context
  - recon_organized_linkedin: entries that are LinkedIn URL slugs
  - recon_organized_garbage: company names, junk, unclassifiable

Uses Title Classifier (Snap-On Tool) for title matching in step 3.

Usage:
  python3 organizer.py --limit 100     # test first 100 slots
  python3 organizer.py                  # all slots with recon data

Env vars: D1_DB, WRANGLER_CWD
"""

import json
import re
import sys
import os
import subprocess
from pathlib import Path

# ── Config ───────────────────────────────────────────────────

LIMIT = 0
BATCH_SIZE = 500
D1_DB = os.environ.get("D1_DB", "svg-d1-outreach-ops")
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

# Try to import Title Classifier
CLASSIFIER_DIR = Path(__file__).parent.parent.parent / "tools" / "title-classifier"
sys.path.insert(0, str(CLASSIFIER_DIR))
try:
    from classifier import TitleClassifier
    tc = TitleClassifier()
    HAS_CLASSIFIER = True
except ImportError:
    HAS_CLASSIFIER = False
    print("[WARN] Title Classifier not available — skipping title classification")

# ── Parse args ───────────────────────────────────────────────

args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--limit" and i + 1 < len(args):
        LIMIT = int(args[i + 1])
        i += 2
    elif args[i] == "--batch" and i + 1 < len(args):
        BATCH_SIZE = int(args[i + 1])
        i += 2
    else:
        i += 1


# ── D1 Access ────────────────────────────────────────────────

def d1_query(sql: str) -> list:
    """Execute a D1 query via wrangler CLI and return results."""
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )
    if result.returncode != 0:
        print(f"[ERROR] D1 query failed: {result.stderr[:500]}")
        return []
    try:
        # Parse wrangler JSON output — find the JSON array in stdout
        stdout = result.stdout
        json_start = stdout.find('[')
        if json_start == -1:
            return []
        data = json.loads(stdout[json_start:])
        if data and isinstance(data, list) and "results" in data[0]:
            return data[0]["results"]
        return []
    except (json.JSONDecodeError, IndexError, KeyError):
        return []


def d1_execute(sql: str) -> bool:
    """Execute a D1 write command."""
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", D1_DB, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD
    )
    return result.returncode == 0


# ── C&V Three Questions ─────────────────────────────────────

# Person name patterns — must have at least first + last
PERSON_NAME_RE = re.compile(
    r'^([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]{1,}(?:\s+[A-Z][a-z]+)*)$'
)

# Common non-person words that indicate company/garbage
COMPANY_INDICATORS = {
    "inc", "llc", "ltd", "corp", "corporation", "company", "co", "group",
    "services", "solutions", "partners", "associates", "agency", "center",
    "foundation", "institute", "university", "college", "hospital", "medical",
    "health", "healthcare", "insurance", "financial", "consulting", "management",
    "technology", "technologies", "systems", "network", "global", "national",
    "international", "american", "association", "council", "board", "committee",
    "facebook", "glassdoor", "indeed", "yelp", "bbb", "linkedin",
    "read more", "learn more", "click here", "view all", "see more",
    "compare", "programs", "resources", "about us", "contact us",
}

# LinkedIn context markers
LINKEDIN_CONTEXT_RE = re.compile(r'linkedin', re.IGNORECASE)
TITLE_CONTEXT_RE = re.compile(
    r'(CEO|CFO|COO|CTO|CIO|CHRO|VP|President|Director|Manager|Owner|Partner|'
    r'Chief|Executive|Officer|Head of|Senior|Lead|Principal|Founder|Chair)',
    re.IGNORECASE
)


def is_person_name(name: str) -> bool:
    """Question 1: Can you NAME it as a person?"""
    if not name or len(name) < 3:
        return False
    # Must have at least 2 words
    parts = name.strip().split()
    if len(parts) < 2:
        return False
    # Check for company indicators
    name_lower = name.lower()
    for indicator in COMPANY_INDICATORS:
        if indicator in name_lower:
            return False
    # Must start with capital letters (first + last)
    if not parts[0][0].isupper() or not parts[-1][0].isupper():
        return False
    # Reject if any part is all caps and > 3 chars (likely acronym/company)
    for part in parts:
        if len(part) > 3 and part.isupper():
            return False
    # Reject if too many words (likely a phrase, not a name)
    if len(parts) > 4:
        return False
    return True


def has_title_format(context: str) -> bool:
    """Question 2: Can you define its FORMAT as a title?"""
    if not context:
        return False
    return bool(TITLE_CONTEXT_RE.search(context))


def is_linkedin_entry(context: str) -> bool:
    """Check if context indicates this is a LinkedIn-sourced entry."""
    if not context:
        return False
    return bool(LINKEDIN_CONTEXT_RE.search(context))


def classify_entry(name: str, context: str, company_name: str) -> str:
    """
    Apply C&V three questions:
      1. Can you NAME it as a person? → person
      2. Can you define its FORMAT as a title? → person_with_title
      3. Is it the VALUE (company/garbage)? → garbage

    Returns: 'person_with_title' | 'person' | 'linkedin' | 'garbage'
    """
    # Quick reject: name matches company name (>50% word overlap)
    if company_name:
        name_words = set(name.lower().split())
        company_words = set(company_name.lower().split())
        if company_words and len(name_words & company_words) / len(company_words) > 0.5:
            return 'garbage'

    person = is_person_name(name)
    title = has_title_format(context)
    linkedin = is_linkedin_entry(context)

    if person and title:
        return 'person_with_title'
    elif person and linkedin:
        return 'linkedin'
    elif person:
        return 'person'
    else:
        return 'garbage'


# ── Main Processing ──────────────────────────────────────────

def process_slot(row: dict) -> dict:
    """Process one slot's recon_name_titles through the C&V gate."""
    outreach_id = row["outreach_id"]
    slot_id = row["slot_id"]
    company_name = row.get("company_name", "")
    raw = row.get("recon_name_titles", "")

    people = []
    linkedin = []
    garbage = []

    if not raw or raw == "[]":
        return {
            "slot_id": slot_id,
            "outreach_id": outreach_id,
            "people": [],
            "linkedin": [],
            "garbage": [],
            "stats": {"total": 0, "person": 0, "linkedin": 0, "garbage": 0}
        }

    try:
        entries = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "slot_id": slot_id,
            "outreach_id": outreach_id,
            "people": [],
            "linkedin": [],
            "garbage": [{"name": raw[:100], "context": "PARSE_ERROR", "classification": "garbage"}],
            "stats": {"total": 1, "person": 0, "linkedin": 0, "garbage": 1}
        }

    for entry in entries:
        name = entry.get("name", "").strip()
        context = entry.get("context", "").strip()
        classification = classify_entry(name, context, company_name)

        tagged = {"name": name, "context": context, "classification": classification}

        if classification in ('person_with_title', 'person'):
            # Run title classifier if available
            if HAS_CLASSIFIER and context:
                result = tc.classify(context, company=company_name)
                tagged["bucket"] = result.bucket
                tagged["confidence"] = result.confidence
                tagged["tier"] = result.tier
            people.append(tagged)
        elif classification == 'linkedin':
            linkedin.append(tagged)
        else:
            garbage.append(tagged)

    return {
        "slot_id": slot_id,
        "outreach_id": outreach_id,
        "people": people,
        "linkedin": linkedin,
        "garbage": garbage,
        "stats": {
            "total": len(entries),
            "person": len(people),
            "linkedin": len(linkedin),
            "garbage": len(garbage),
        }
    }


def main():
    # Count total first
    count_sql = """
        SELECT COUNT(*) as cnt FROM slot_workbench
        WHERE recon_name_titles IS NOT NULL
          AND recon_name_titles != ''
          AND recon_name_titles != '[]'
          AND recon_organized_people IS NULL
    """
    count_rows = d1_query(count_sql)
    total_remaining = count_rows[0]["cnt"] if count_rows else 0

    if LIMIT > 0:
        total = min(LIMIT, total_remaining)
    else:
        total = total_remaining

    print(f"[ORGANIZER] {total_remaining} slots need organizing, processing {total}")

    if total == 0:
        print("[ORGANIZER] Nothing to organize. Done.")
        return

    # Process in pages to avoid loading 80K rows at once
    PAGE_SIZE = 1000
    processed = 0
    rows = []

    if total == 0:
        print("[ORGANIZER] Nothing to organize. Done.")
        return

    # Process in pages
    stats_total = {"total": 0, "person": 0, "linkedin": 0, "garbage": 0}
    processed = 0

    while processed < total:
        page_limit = min(PAGE_SIZE, total - processed)
        sql = f"""
            SELECT slot_id, outreach_id, company_name, recon_name_titles
            FROM slot_workbench
            WHERE recon_name_titles IS NOT NULL
              AND recon_name_titles != ''
              AND recon_name_titles != '[]'
              AND recon_organized_people IS NULL
            ORDER BY outreach_id
            LIMIT {page_limit}
        """

        rows = d1_query(sql)
        if not rows:
            print(f"[ORGANIZER] No more rows returned at offset {processed}")
            break

        write_batch = []
        for row in rows:
            result = process_slot(row)

            for key in stats_total:
                stats_total[key] += result["stats"][key]

            people_json = json.dumps(result["people"]).replace("'", "''")
            linkedin_json = json.dumps(result["linkedin"]).replace("'", "''")
            garbage_json = json.dumps(result["garbage"]).replace("'", "''")

            write_batch.append(
                f"UPDATE slot_workbench SET "
                f"recon_organized_people = '{people_json}', "
                f"recon_organized_linkedin = '{linkedin_json}', "
                f"recon_organized_garbage = '{garbage_json}' "
                f"WHERE slot_id = '{result['slot_id']}'"
            )

            if len(write_batch) >= BATCH_SIZE:
                batch_sql = "; ".join(write_batch)
                ok = d1_execute(batch_sql)
                status = "OK" if ok else "FAILED"
                processed += len(write_batch)
                pct = processed / total * 100
                print(f"[ORGANIZER] {processed}/{total} ({pct:.1f}%) — {status}")
                write_batch = []

        # Write remaining from this page
        if write_batch:
            batch_sql = "; ".join(write_batch)
            ok = d1_execute(batch_sql)
            status = "OK" if ok else "FAILED"
            processed += len(write_batch)
            pct = processed / total * 100
            print(f"[ORGANIZER] {processed}/{total} ({pct:.1f}%) — {status}")
            write_batch = []

    # Report
    print(f"\n{'='*60}")
    print(f"ORGANIZER COMPLETE")
    print(f"{'='*60}")
    print(f"Total entries processed: {stats_total['total']}")
    print(f"  People (person + title): {stats_total['person']} ({stats_total['person']/max(stats_total['total'],1)*100:.1f}%)")
    print(f"  LinkedIn slugs:          {stats_total['linkedin']} ({stats_total['linkedin']/max(stats_total['total'],1)*100:.1f}%)")
    print(f"  Garbage (company/junk):   {stats_total['garbage']} ({stats_total['garbage']/max(stats_total['total'],1)*100:.1f}%)")
    print(f"Total slots processed: {total}")

    # Comparator check
    total_entries = max(stats_total["total"], 1)
    garbage_rate = stats_total["garbage"] / total_entries
    person_rate = stats_total["person"] / total_entries
    unclassified = 0  # everything gets classified into one pile

    print(f"\n--- Comparator Check (P_organizer) ---")
    print(f"C_4 garbage_rate:           {garbage_rate:.3f} / k_4=0.30 → ratio={garbage_rate/0.30:.2f} {'PASS' if garbage_rate/0.30 <= 1 else 'FAIL'}")
    print(f"C_5 unclassified_rate:      {unclassified/total_entries:.3f} / k_5=0.05 → ratio={unclassified/total_entries/0.05:.2f} {'PASS' if unclassified/total_entries/0.05 <= 1 else 'FAIL'}")
    print(f"C_6 person_extraction:      {1-person_rate:.3f} / k_6=0.50 → ratio={(1-person_rate)/0.50:.2f} {'PASS' if (1-person_rate)/0.50 <= 1 else 'FAIL'}")

    p_organizer = max(garbage_rate/0.30, unclassified/total_entries/0.05 if unclassified > 0 else 0, (1-person_rate)/0.50)
    print(f"\nP_organizer(x;θ) = {'1 (PASS)' if p_organizer <= 1 else '0 (FAIL)'} — max ratio = {p_organizer:.2f}")


if __name__ == "__main__":
    main()

"""
UP — QC Agent: Run scorecard on ALL 9 sections

Every number has a query. Every query runs TWICE for self-verification.
Output: scorecard with comparator, query, run1 result, run2 result, match (Y/N)
"""

import json
import sys
import os
import subprocess
from datetime import datetime

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))


def d1_query(sql):
    """Run a D1 query and return the first result row."""
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    if result.returncode != 0:
        return None
    try:
        s = result.stdout.find('[')
        if s < 0: return None
        data = json.loads(result.stdout[s:])
        results = data[0].get("results", [])
        return results[0] if results else None
    except:
        return None


def run_check(name, description, sql):
    """Run a query twice, compare results, return scorecard entry."""
    print(f"\n  {name}")
    print(f"  What: {description}")
    print(f"  Query: {sql[:120]}...")
    sys.stdout.flush()

    # Run 1
    r1 = d1_query(sql)
    # Run 2
    r2 = d1_query(sql)

    if r1 is None or r2 is None:
        print(f"  ERROR: Query failed to execute")
        return {"name": name, "description": description, "query": sql,
                "run1": None, "run2": None, "match": False, "error": True}

    # Compare
    match = (r1 == r2)
    print(f"  Run 1: {r1}")
    print(f"  Run 2: {r2}")
    print(f"  Match: {'YES ✓' if match else 'NO ✗ — FLAGGED'}")
    sys.stdout.flush()

    return {"name": name, "description": description, "query": sql,
            "run1": r1, "run2": r2, "match": match, "error": False}


def main():
    print("=" * 70)
    print("UP — QC SCORECARD: ALL 9 SECTIONS")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Every number has a query. Every query runs twice.")
    print("=" * 70)

    all_results = {}

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: Hunter Contacts
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 1: enrichment_hunter_contact")
    print(f"{'='*70}")

    s1 = []
    s1.append(run_check(
        "S1-ROW-COUNT", "Total rows in hunter contacts",
        "SELECT COUNT(*) as val FROM enrichment_hunter_contact"))
    s1.append(run_check(
        "S1-JOIN-RESOLUTION", "% of hunter outreach_ids that exist in workbench",
        "SELECT ROUND(COUNT(DISTINCT CASE WHEN sw.outreach_id IS NOT NULL THEN ehc.outreach_id END) * 100.0 / COUNT(DISTINCT ehc.outreach_id), 1) as val FROM (SELECT DISTINCT outreach_id FROM enrichment_hunter_contact) ehc LEFT JOIN (SELECT DISTINCT outreach_id FROM slot_workbench) sw ON ehc.outreach_id = sw.outreach_id"))
    s1.append(run_check(
        "S1-NAME-COVERAGE", "% of contacts with first_name populated",
        "SELECT ROUND(SUM(CASE WHEN first_name IS NOT NULL AND first_name != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM enrichment_hunter_contact"))
    s1.append(run_check(
        "S1-EMAIL-COVERAGE", "% of contacts with email populated",
        "SELECT ROUND(SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM enrichment_hunter_contact"))
    s1.append(run_check(
        "S1-LINKEDIN-COVERAGE", "% of contacts with linkedin_url populated",
        "SELECT ROUND(SUM(CASE WHEN linkedin_url IS NOT NULL AND linkedin_url != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM enrichment_hunter_contact"))
    s1.append(run_check(
        "S1-SENIORITY-COVERAGE", "% of contacts with seniority_level populated",
        "SELECT ROUND(SUM(CASE WHEN seniority_level IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM enrichment_hunter_contact"))
    all_results["Section 1"] = s1

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: Vendor People
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 2: vendor_people")
    print(f"{'='*70}")

    s2 = []
    s2.append(run_check(
        "S2-ROW-COUNT", "Total rows in vendor_people",
        "SELECT COUNT(*) as val FROM vendor_people"))
    s2.append(run_check(
        "S2-JOIN-RESOLUTION", "% of vendor outreach_ids that exist in workbench",
        "SELECT ROUND(COUNT(DISTINCT CASE WHEN sw.outreach_id IS NOT NULL THEN vp.outreach_id END) * 100.0 / COUNT(DISTINCT vp.outreach_id), 1) as val FROM (SELECT DISTINCT outreach_id FROM vendor_people) vp LEFT JOIN (SELECT DISTINCT outreach_id FROM slot_workbench) sw ON vp.outreach_id = sw.outreach_id"))
    s2.append(run_check(
        "S2-MAPPED-SLOT-TYPE", "% of vendor contacts with mapped_slot_type populated",
        "SELECT ROUND(SUM(CASE WHEN mapped_slot_type IS NOT NULL AND mapped_slot_type != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM vendor_people"))
    s2.append(run_check(
        "S2-NAME-COVERAGE", "% of contacts with first_name populated",
        "SELECT ROUND(SUM(CASE WHEN first_name IS NOT NULL AND first_name != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM vendor_people"))
    all_results["Section 2"] = s2

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: Hunter Company
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 3: enrichment_hunter_company")
    print(f"{'='*70}")

    s3 = []
    s3.append(run_check(
        "S3-ROW-COUNT", "Total rows in hunter_company",
        "SELECT COUNT(*) as val FROM enrichment_hunter_company"))
    s3.append(run_check(
        "S3-JOIN-RESOLUTION", "% of hunter company outreach_ids in workbench",
        "SELECT ROUND(COUNT(DISTINCT CASE WHEN sw.outreach_id IS NOT NULL THEN hc.outreach_id END) * 100.0 / COUNT(DISTINCT hc.outreach_id), 1) as val FROM (SELECT DISTINCT outreach_id FROM enrichment_hunter_company) hc LEFT JOIN (SELECT DISTINCT outreach_id FROM slot_workbench) sw ON hc.outreach_id = sw.outreach_id"))
    s3.append(run_check(
        "S3-EMAIL-PATTERN", "% with email_pattern populated",
        "SELECT ROUND(SUM(CASE WHEN email_pattern IS NOT NULL AND email_pattern != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM enrichment_hunter_company"))
    all_results["Section 3"] = s3

    # ═══════════════════════════════════════════════════════════
    # SECTION 4: Recon Columns
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 4: slot_workbench recon columns")
    print(f"{'='*70}")

    s4 = []
    s4.append(run_check(
        "S4-RECON-COVERAGE", "% of CEO slots with recon_name_titles populated",
        "SELECT ROUND(SUM(CASE WHEN recon_name_titles IS NOT NULL AND recon_name_titles != '' AND recon_name_titles != '[]' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM slot_workbench WHERE slot_type = 'CEO'"))
    s4.append(run_check(
        "S4-ORGANIZED", "% of CEO slots with recon_organized_people populated",
        "SELECT ROUND(SUM(CASE WHEN recon_organized_people IS NOT NULL AND recon_organized_people != '[]' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM slot_workbench WHERE slot_type = 'CEO'"))
    s4.append(run_check(
        "S4-ABOUT-URL", "% of CEO slots with about_url populated",
        "SELECT ROUND(SUM(CASE WHEN about_url IS NOT NULL AND about_url != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM slot_workbench WHERE slot_type = 'CEO'"))
    all_results["Section 4"] = s4

    # ═══════════════════════════════════════════════════════════
    # SECTION 5: Workbench Hunter Columns
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 5: slot_workbench hunter columns")
    print(f"{'='*70}")

    s5 = []
    s5.append(run_check(
        "S5-HUNTER-CANDIDATE", "% of CEO slots with hunter_first_name populated",
        "SELECT ROUND(SUM(CASE WHEN hunter_first_name IS NOT NULL AND hunter_first_name != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM slot_workbench WHERE slot_type = 'CEO'"))
    s5.append(run_check(
        "S5-EMAIL-PATTERN", "% of CEO slots with hunter_email_pattern populated",
        "SELECT ROUND(SUM(CASE WHEN hunter_email_pattern IS NOT NULL AND hunter_email_pattern != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM slot_workbench WHERE slot_type = 'CEO'"))
    all_results["Section 5"] = s5

    # ═══════════════════════════════════════════════════════════
    # SECTION 6: DOL 5500 Signers
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 6: DOL 5500 (join via EIN)")
    print(f"{'='*70}")

    s6 = []
    s6.append(run_check(
        "S6-DOL-COVERAGE", "% of CEO slots with filing_present = 1",
        "SELECT ROUND(SUM(CASE WHEN filing_present = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM slot_workbench WHERE slot_type = 'CEO'"))
    s6.append(run_check(
        "S6-EIN-POPULATED", "% of CEO slots with ein populated (join field)",
        "SELECT ROUND(SUM(CASE WHEN ein IS NOT NULL AND ein != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM slot_workbench WHERE slot_type = 'CEO'"))
    all_results["Section 6"] = s6

    # ═══════════════════════════════════════════════════════════
    # SECTION 7: Management Pages
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 7: page_raw_html (fetched pages)")
    print(f"{'='*70}")

    s7 = []
    s7.append(run_check(
        "S7-PAGES-FETCHED", "Total pages successfully fetched (status 200)",
        "SELECT COUNT(*) as val FROM page_raw_html WHERE fetch_status = 200"))
    s7.append(run_check(
        "S7-PAGES-FAILED", "Total pages that failed to fetch",
        "SELECT COUNT(*) as val FROM page_raw_html WHERE fetch_status != 200"))
    s7.append(run_check(
        "S7-FETCH-RATE", "% success rate on page fetches",
        "SELECT ROUND(SUM(CASE WHEN fetch_status = 200 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as val FROM page_raw_html"))
    s7.append(run_check(
        "S7-403-COUNT", "Pages blocked (403 Forbidden)",
        "SELECT COUNT(*) as val FROM page_raw_html WHERE fetch_status = 403"))
    s7.append(run_check(
        "S7-404-COUNT", "Pages not found (404)",
        "SELECT COUNT(*) as val FROM page_raw_html WHERE fetch_status = 404"))
    s7.append(run_check(
        "S7-TIMEOUT-COUNT", "Pages timed out (status 0)",
        "SELECT COUNT(*) as val FROM page_raw_html WHERE fetch_status = 0"))
    all_results["Section 7"] = s7

    # ═══════════════════════════════════════════════════════════
    # SECTION 8: Search Result URLs (classified)
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 8: recon_result_urls (classified, not fetched)")
    print(f"{'='*70}")

    s8 = []
    s8.append(run_check(
        "S8-SLOTS-WITH-URLS", "CEO slots with recon_result_urls populated",
        "SELECT COUNT(*) as val FROM slot_workbench WHERE slot_type = 'CEO' AND recon_result_urls IS NOT NULL AND recon_result_urls != '[]'"))
    all_results["Section 8"] = s8

    # ═══════════════════════════════════════════════════════════
    # SECTION 9: Platform Sources
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("SECTION 9: recon_platform_urls")
    print(f"{'='*70}")

    s9 = []
    s9.append(run_check(
        "S9-PLATFORM-COVERAGE", "CEO slots with platform URLs populated",
        "SELECT COUNT(*) as val FROM slot_workbench WHERE slot_type = 'CEO' AND recon_platform_urls IS NOT NULL AND recon_platform_urls != '' AND recon_platform_urls != '{}'"))
    all_results["Section 9"] = s9

    # ═══════════════════════════════════════════════════════════
    # OVERALL WORKBENCH STATE
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("WORKBENCH STATE")
    print(f"{'='*70}")

    wb = []
    wb.append(run_check(
        "WB-TOTAL", "Total slots in workbench",
        "SELECT COUNT(*) as val FROM slot_workbench"))
    wb.append(run_check(
        "WB-FULL", "Slots at FULL tier",
        "SELECT COUNT(*) as val FROM slot_workbench WHERE readiness_tier = 'FULL'"))
    wb.append(run_check(
        "WB-REACHABLE", "Slots at REACHABLE tier",
        "SELECT COUNT(*) as val FROM slot_workbench WHERE readiness_tier = 'REACHABLE'"))
    wb.append(run_check(
        "WB-NAME-ONLY", "Slots at NAME_ONLY tier",
        "SELECT COUNT(*) as val FROM slot_workbench WHERE readiness_tier = 'NAME_ONLY'"))
    wb.append(run_check(
        "WB-PATTERN-READY", "Slots at PATTERN_READY tier",
        "SELECT COUNT(*) as val FROM slot_workbench WHERE readiness_tier = 'PATTERN_READY'"))
    wb.append(run_check(
        "WB-EMPTY", "Slots at EMPTY tier",
        "SELECT COUNT(*) as val FROM slot_workbench WHERE readiness_tier = 'EMPTY'"))
    all_results["Workbench"] = wb

    # ═══════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("QC SUMMARY")
    print(f"{'='*70}")

    total_checks = 0
    total_match = 0
    total_error = 0

    for section, checks in all_results.items():
        section_match = sum(1 for c in checks if c["match"])
        section_total = len(checks)
        section_errors = sum(1 for c in checks if c["error"])
        total_checks += section_total
        total_match += section_match
        total_error += section_errors
        status = "ALL VERIFIED" if section_match == section_total else "MISMATCH DETECTED"
        print(f"  {section:20s}: {section_match}/{section_total} verified | {status}")

    print(f"\n  TOTAL: {total_match}/{total_checks} queries self-verified")
    print(f"  Errors: {total_error}")
    print(f"  Self-verification rate: {total_match/max(total_checks,1)*100:.0f}%")

    if total_match == total_checks and total_error == 0:
        print(f"\n  ALL QUERIES SELF-VERIFIED. Scorecard ready for TS (human review).")
    else:
        print(f"\n  MISMATCHES OR ERRORS DETECTED. Investigate before presenting to TS.")

    print(f"\n{'='*70}")
    print(f"STATUS: ALL 9 SECTIONS IN BUILD. NONE CERTIFIED.")
    print(f"NEXT: TS — Human reviews this scorecard, sets tolerances, approves or rejects.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

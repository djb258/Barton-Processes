"""
Tier Recalculation — ONE PLACE, ONE FUNCTION

The readiness_tier is conditional logic computed from workbench state.
No process should ever hardcode a tier. Processes fill their column.
The tier is derived.

FULL         = has_name AND has_email AND has_linkedin
REACHABLE    = has_name AND (has_email OR has_linkedin)
NAME_ONLY    = has_name AND NOT has_email AND NOT has_linkedin
PATTERN_READY = NOT has_name AND has recon data
HUNTER_READY  = NOT has_name AND has hunter data
EMPTY        = NOT has_name AND no recon AND no hunter

Call after ANY write to slot_workbench:
  recalc_tier(slot_id)        — one slot
  recalc_tier_batch(slot_ids) — batch
  recalc_tier_all()           — full table

Or run standalone: python3 recalc_tier.py
"""

import json
import sys
import os
import subprocess

DB_NAME = "svg-d1-outreach-ops"
WRANGLER_CWD = os.environ.get("WRANGLER_CWD",
    os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub"))

TIER_SQL = """
CASE
  WHEN has_name = 1 AND has_email = 1 AND has_linkedin = 1 THEN 'FULL'
  WHEN has_name = 1 AND (has_email = 1 OR has_linkedin = 1) THEN 'REACHABLE'
  WHEN has_name = 1 THEN 'NAME_ONLY'
  WHEN recon_name_titles IS NOT NULL AND recon_name_titles != '' AND recon_name_titles != '[]' THEN 'PATTERN_READY'
  WHEN hunter_first_name IS NOT NULL AND hunter_first_name != '' THEN 'HUNTER_READY'
  ELSE 'EMPTY'
END
"""


def d1_execute(sql):
    result = subprocess.run(
        ["npx", "wrangler", "d1", "execute", DB_NAME, "--remote", "--command", sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    return result.returncode == 0


def recalc_tier(slot_id):
    """Recalculate tier for one slot."""
    sql = f"UPDATE slot_workbench SET readiness_tier = {TIER_SQL} WHERE slot_id = '{slot_id}'"
    return d1_execute(sql)


def recalc_tier_batch(slot_ids):
    """Recalculate tiers for a list of slot_ids."""
    ids = ", ".join(f"'{sid}'" for sid in slot_ids)
    sql = f"UPDATE slot_workbench SET readiness_tier = {TIER_SQL} WHERE slot_id IN ({ids})"
    return d1_execute(sql)


def recalc_tier_all():
    """Recalculate ALL tiers from actual data state."""
    sql = f"""
        UPDATE slot_workbench SET readiness_tier = {TIER_SQL}
        WHERE readiness_tier != {TIER_SQL}
    """
    return d1_execute(sql)


if __name__ == "__main__":
    print("Recalculating all tiers...")
    recalc_tier_all()
    print("Done.")

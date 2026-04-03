"""
Fetch 10 about_url pages and report what the HTML structure looks like.
Diagnostic tool — does NOT write to D1.
"""
import json, re, sys, os, subprocess
from curl_cffi import requests as creq

WRANGLER_CWD = os.path.expanduser("~/Documents/imo-creator-v2-20260317/workers/lcs-hub")

def d1_query(sql):
    r = subprocess.run(["npx","wrangler","d1","execute","svg-d1-outreach-ops","--remote","--command",sql],
        capture_output=True, text=True, cwd=WRANGLER_CWD, timeout=120)
    if r.returncode != 0: return []
    s = r.stdout.find('[')
    if s < 0: return []
    return json.loads(r.stdout[s:])[0].get("results",[])

print("Loading URLs...")
sys.stdout.flush()

rows = d1_query("SELECT DISTINCT outreach_id, company_name, about_url FROM slot_workbench WHERE about_url IS NOT NULL AND about_url != '' AND has_name = 0 ORDER BY outreach_id LIMIT 10")
print(f"Got {len(rows)} URLs")
sys.stdout.flush()

session = creq.Session(impersonate="chrome131")

for row in rows:
    url = row["about_url"]
    company = row["company_name"]
    print(f"\n{'='*70}")
    print(f"{company}")
    print(f"{url}")
    sys.stdout.flush()

    try:
        resp = session.get(url, timeout=10, allow_redirects=True)
        html = resp.text if resp.status_code == 200 else ""
        print(f"  Status: {resp.status_code} | Size: {len(html)} chars")
    except Exception as e:
        print(f"  FAILED: {str(e)[:80]}")
        sys.stdout.flush()
        continue

    if not html:
        sys.stdout.flush()
        continue

    # Strip scripts/styles
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.I)

    # Title keywords
    kw = r'(?:CEO|CFO|COO|CTO|President|Owner|Founder|Director|VP|Chief|Controller|Manager|Human Resource|HR Director|Benefits|Treasurer|Partner)'
    chunks = re.findall(r'([^<>]{0,80}' + kw + r'[^<>]{0,80})', text, re.I)

    if chunks:
        print(f"  Title matches ({len(chunks)}):")
        for c in chunks[:6]:
            clean = re.sub(r'\s+', ' ', c.strip())
            if len(clean) > 10:
                print(f'    "{clean[:100]}"')
    else:
        print(f"  No title keywords found")

    li = re.findall(r'linkedin\.com/in/[a-zA-Z0-9\-]+', html)
    if li: print(f"  LinkedIn ({len(li)}): {li[:3]}")

    emails = [e for e in re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
              if not any(x in e.lower() for x in ['example','wix','wordpress','jquery','sentry'])]
    if emails: print(f"  Emails ({len(emails)}): {emails[:3]}")

    sys.stdout.flush()

print("\nDone.")

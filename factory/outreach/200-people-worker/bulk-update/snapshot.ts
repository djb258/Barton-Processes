/**
 * Process 200 — Monthly Bulk Update
 *
 * Runs on this machine. Opens Chrome via Playwright.
 * Grabs all LinkedIn profiles in batches of 20 tabs.
 * Stores raw title data in a JSON file for upload to D1.
 *
 * Usage: npx tsx bulk-update/snapshot.ts
 *
 * Output: bulk-update/snapshots-YYYY-MM.json
 * Then upload to D1 via: npx tsx bulk-update/upload.ts
 */

import { chromium, type Page, type Browser, type BrowserContext } from 'playwright';
import * as fs from 'node:fs';
import * as path from 'node:path';

// ── Config ──────────────────────────────────────────────────

const TABS_PER_BATCH = 200;        // Concurrent tabs — go big
const BATCH_DELAY_MS = 2000;       // Delay between batches
const PAGE_TIMEOUT_MS = 10000;     // Per-page load timeout
const OUTPUT_DIR = path.join(__dirname);

interface ProfileSnapshot {
  linkedin_url: string;
  person_id: string;
  raw_title_tag: string;
  parsed_name: string;
  parsed_title: string;
  parsed_company: string;
  http_status: number;
  error: string | null;
  fetched_at: string;
}

// ── Title Parser ────────────────────────────────────────────

function parseTitleTag(raw: string): { name: string; title: string; company: string } {
  const withoutSuffix = raw.replace(/\s*\|\s*LinkedIn\s*$/, '').trim();
  const dashIndex = withoutSuffix.indexOf(' - ');
  if (dashIndex === -1) return { name: withoutSuffix, title: '', company: '' };

  const name = withoutSuffix.substring(0, dashIndex).trim();
  const titleCompany = withoutSuffix.substring(dashIndex + 3).trim();

  const atIndex = titleCompany.lastIndexOf(' at ');
  if (atIndex !== -1) {
    return { name, title: titleCompany.substring(0, atIndex).trim(), company: titleCompany.substring(atIndex + 4).trim() };
  }

  const innerDash = titleCompany.lastIndexOf(' - ');
  if (innerDash !== -1) {
    return { name, title: titleCompany.substring(0, innerDash).trim(), company: titleCompany.substring(innerDash + 3).trim() };
  }

  const lastComma = titleCompany.lastIndexOf(',');
  if (lastComma !== -1 && lastComma > titleCompany.length * 0.3) {
    return { name, title: titleCompany.substring(0, lastComma).trim(), company: titleCompany.substring(lastComma + 1).trim() };
  }

  return { name, title: titleCompany, company: '' };
}

// ── Single Page Grab ────────────────────────────────────────

async function grabProfile(page: Page, url: string, personId: string): Promise<ProfileSnapshot> {
  const fetchedAt = new Date().toISOString();
  try {
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT_MS });
    const status = response?.status() || 0;

    if (status === 999 || status === 429) {
      return { linkedin_url: url, person_id: personId, raw_title_tag: '', parsed_name: '', parsed_title: '', parsed_company: '', http_status: status, error: `HTTP ${status}`, fetched_at: fetchedAt };
    }

    const title = await page.title();
    if (!title.includes('LinkedIn')) {
      return { linkedin_url: url, person_id: personId, raw_title_tag: title, parsed_name: '', parsed_title: '', parsed_company: '', http_status: status, error: 'Not a LinkedIn profile page', fetched_at: fetchedAt };
    }

    const parsed = parseTitleTag(title);
    return {
      linkedin_url: url,
      person_id: personId,
      raw_title_tag: title,
      parsed_name: parsed.name,
      parsed_title: parsed.title,
      parsed_company: parsed.company,
      http_status: status,
      error: null,
      fetched_at: fetchedAt,
    };
  } catch (err) {
    return { linkedin_url: url, person_id: personId, raw_title_tag: '', parsed_name: '', parsed_title: '', parsed_company: '', http_status: 0, error: err instanceof Error ? err.message : String(err), fetched_at: fetchedAt };
  }
}

// ── Batch Runner ────────────────────────────────────────────

async function runBatch(context: BrowserContext, profiles: Array<{ url: string; person_id: string }>): Promise<ProfileSnapshot[]> {
  const results: ProfileSnapshot[] = [];
  const pages: Page[] = [];

  // Open all tabs
  for (const p of profiles) {
    const page = await context.newPage();
    pages.push(page);
  }

  // Navigate all tabs in parallel
  const promises = profiles.map((p, i) => grabProfile(pages[i], p.url, p.person_id));
  const batchResults = await Promise.all(promises);
  results.push(...batchResults);

  // Close all tabs
  for (const page of pages) {
    await page.close();
  }

  return results;
}

// ── Main ────────────────────────────────────────────────────

async function main() {
  // Load the monitor list from D1 export or Neon direct
  const inputFile = path.join(OUTPUT_DIR, 'monitor-list.json');
  if (!fs.existsSync(inputFile)) {
    console.error(`Missing ${inputFile}`);
    console.error('Generate it with: wrangler d1 execute people-worker-200 --remote --command "SELECT person_id, linkedin_url FROM monitor_list" --json > bulk-update/monitor-list.json');
    process.exit(1);
  }

  const raw = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
  // Handle wrangler D1 JSON output format
  const profiles: Array<{ person_id: string; linkedin_url: string }> =
    Array.isArray(raw) ? raw[0]?.results || raw : raw.results || raw;

  console.log(`Loaded ${profiles.length} profiles`);
  console.log(`Batch size: ${TABS_PER_BATCH} tabs`);
  console.log(`Estimated time: ${Math.ceil(profiles.length / TABS_PER_BATCH * (BATCH_DELAY_MS / 1000 + 3))} seconds`);
  console.log('');

  // Launch browser
  const browser = await chromium.launch({
    headless: false,  // Real browser — not headless
    args: ['--disable-blink-features=AutomationControlled'],
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
  });

  const allResults: ProfileSnapshot[] = [];
  let success = 0;
  let errors = 0;
  let blocked = 0;
  const startTime = Date.now();

  // Process in batches
  const totalBatches = Math.ceil(profiles.length / TABS_PER_BATCH);
  for (let i = 0; i < profiles.length; i += TABS_PER_BATCH) {
    const batch = profiles.slice(i, i + TABS_PER_BATCH);
    const batchNum = Math.floor(i / TABS_PER_BATCH) + 1;

    const results = await runBatch(context, batch.map(p => ({ url: p.linkedin_url, person_id: p.person_id })));
    allResults.push(...results);

    const batchSuccess = results.filter(r => !r.error).length;
    const batchBlocked = results.filter(r => r.http_status === 999).length;
    success += batchSuccess;
    errors += results.filter(r => r.error && r.http_status !== 999).length;
    blocked += batchBlocked;

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(0);
    console.log(`Batch ${batchNum}/${totalBatches} | OK: ${batchSuccess} | Blocked: ${batchBlocked} | Total: ${success}/${allResults.length} | ${elapsed}s`);

    // If we're getting blocked, slow down
    if (batchBlocked > 0) {
      console.log('  ⚠ LinkedIn rate limit detected — pausing 30s...');
      await new Promise(r => setTimeout(r, 30000));
    } else {
      await new Promise(r => setTimeout(r, BATCH_DELAY_MS));
    }
  }

  await browser.close();

  // Save results
  const runMonth = new Date().toISOString().slice(0, 7);
  const outputFile = path.join(OUTPUT_DIR, `snapshots-${runMonth}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(allResults, null, 2));

  const elapsed = ((Date.now() - startTime) / 1000 / 60).toFixed(1);
  console.log('');
  console.log(`Done in ${elapsed} minutes`);
  console.log(`Success: ${success}`);
  console.log(`Errors: ${errors}`);
  console.log(`Blocked: ${blocked}`);
  console.log(`Output: ${outputFile}`);
}

main().catch(console.error);

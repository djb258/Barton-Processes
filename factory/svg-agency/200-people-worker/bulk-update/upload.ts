/**
 * Upload snapshots JSON to D1 via wrangler.
 *
 * Reads the snapshots-YYYY-MM.json file from bulk-update/
 * and inserts into D1 snapshots table.
 *
 * Usage: npx tsx bulk-update/upload.ts
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import { execSync } from 'node:child_process';

const OUTPUT_DIR = path.join(__dirname);

async function main() {
  const runMonth = new Date().toISOString().slice(0, 7);
  const inputFile = path.join(OUTPUT_DIR, `snapshots-${runMonth}.json`);

  if (!fs.existsSync(inputFile)) {
    console.error(`Missing ${inputFile}`);
    process.exit(1);
  }

  const snapshots = JSON.parse(fs.readFileSync(inputFile, 'utf-8')) as Array<{
    linkedin_url: string;
    person_id: string;
    raw_title_tag: string;
    parsed_name: string;
    parsed_title: string;
    parsed_company: string;
    http_status: number;
    error: string | null;
    fetched_at: string;
  }>;

  const successful = snapshots.filter(s => !s.error);
  const errors = snapshots.filter(s => s.error);

  console.log(`Total: ${snapshots.length}`);
  console.log(`Successful: ${successful.length}`);
  console.log(`Errors: ${errors.length}`);
  console.log('');

  // Build SQL for batch insert
  const runMonthDate = `${runMonth}-01`;
  const batchSize = 50;

  for (let i = 0; i < successful.length; i += batchSize) {
    const batch = successful.slice(i, i + batchSize);
    const values = batch.map(s => {
      const esc = (v: string) => (v || '').replace(/'/g, "''");
      return `('${crypto.randomUUID()}', '${esc(s.person_id)}', '', '${runMonthDate}', '${esc(s.linkedin_url)}', '${esc(s.raw_title_tag)}', '${esc(s.parsed_name)}', '${esc(s.parsed_title)}', '${esc(s.parsed_company)}', 0, 'NONE', '${s.fetched_at}', 'bulk_update', ${s.http_status})`;
    }).join(',\n');

    const sql = `INSERT OR IGNORE INTO snapshots (snapshot_id, person_id, company_unique_id, run_month, linkedin_url, raw_title_tag, parsed_name, parsed_title, parsed_company, movement_detected, movement_type, fetched_at, source_tool, http_status) VALUES ${values};`;

    // Write to temp file and execute
    const tmpFile = path.join(OUTPUT_DIR, `_batch_${i}.sql`);
    fs.writeFileSync(tmpFile, sql);

    try {
      execSync(`wrangler d1 execute people-worker-200 --remote --file=${tmpFile}`, { stdio: 'pipe' });
      process.stdout.write(`  Uploaded ${Math.min(i + batchSize, successful.length)}/${successful.length}\r`);
    } catch (err) {
      console.error(`  Batch ${i} failed:`, err instanceof Error ? err.message : err);
    }

    fs.unlinkSync(tmpFile);
  }

  // Upload errors too
  if (errors.length > 0) {
    for (let i = 0; i < errors.length; i += batchSize) {
      const batch = errors.slice(i, i + batchSize);
      const values = batch.map(s => {
        const esc = (v: string) => (v || '').replace(/'/g, "''");
        return `('${crypto.randomUUID()}', '${esc(s.person_id)}', '${esc(s.linkedin_url)}', 'FETCH_FAILED', '${esc(s.error || '')}', '${runMonthDate}')`;
      }).join(',\n');

      const sql = `INSERT OR IGNORE INTO errors (error_id, person_id, linkedin_url, error_code, error_message, run_month) VALUES ${values};`;
      const tmpFile = path.join(OUTPUT_DIR, `_errbatch_${i}.sql`);
      fs.writeFileSync(tmpFile, sql);

      try {
        execSync(`wrangler d1 execute people-worker-200 --remote --file=${tmpFile}`, { stdio: 'pipe' });
      } catch (err) {
        console.error(`  Error batch ${i} failed`);
      }

      fs.unlinkSync(tmpFile);
    }
  }

  console.log('');
  console.log(`Upload complete. ${successful.length} snapshots + ${errors.length} errors in D1.`);
  console.log('');
  console.log('Next: Run movement detection on the CF Worker:');
  console.log('  curl -X POST https://people-worker-200.svg-outreach.workers.dev/detect-movement');
}

main().catch(console.error);

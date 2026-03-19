/**
 * Process 200 — PUSH Phase
 *
 * Pushes confirmed monthly snapshots from D1 to Neon vault.
 * Runs on Day 28+ (or manual trigger via POST /push).
 * INSERT-only into Neon. ON CONFLICT DO NOTHING.
 */

import { neon } from '@neondatabase/serverless';

interface PushResult {
  pushed: number;
  skipped: number;
  errors: number;
  durationMs: number;
}

/**
 * Push confirmed snapshots from D1 to Neon vault.
 */
export async function pushToVault(d1: D1Database, neonUrl: string, runMonth: string): Promise<PushResult> {
  const start = Date.now();

  // Check if already pushed
  const progress = await d1.prepare(
    'SELECT pushed_to_vault FROM batch_progress WHERE run_month = ?'
  ).bind(runMonth).first<{ pushed_to_vault: number }>();

  if (progress?.pushed_to_vault === 1) {
    return { pushed: 0, skipped: 0, errors: 0, durationMs: Date.now() - start };
  }

  // Get all snapshots for this month from D1
  const snapshots = await d1.prepare(
    'SELECT * FROM snapshots WHERE run_month = ?'
  ).bind(runMonth).all();

  if (!snapshots.results || snapshots.results.length === 0) {
    return { pushed: 0, skipped: 0, errors: 0, durationMs: Date.now() - start };
  }

  const sql = neon(neonUrl);
  let pushed = 0;
  let skipped = 0;
  let errors = 0;

  // Batch insert into Neon (50 rows per batch for safety)
  const batchSize = 50;
  for (let i = 0; i < snapshots.results.length; i += batchSize) {
    const batch = snapshots.results.slice(i, i + batchSize);

    for (const row of batch) {
      try {
        const result = await sql`
          INSERT INTO people.linkedin_snapshots (
            person_id, company_unique_id, run_month,
            linkedin_url, raw_title_tag, parsed_name, parsed_title, parsed_company,
            headline, location, last_post_date, profile_photo_url,
            movement_detected, movement_type,
            fetched_at, source_tool
          ) VALUES (
            ${row.person_id},
            ${row.company_unique_id},
            ${row.run_month}::date,
            ${row.linkedin_url},
            ${row.raw_title_tag},
            ${row.parsed_name},
            ${row.parsed_title},
            ${row.parsed_company},
            ${row.headline},
            ${row.location},
            ${row.last_post_date ? new Date(row.last_post_date as string) : null},
            ${row.profile_photo_url},
            ${(row.movement_detected as number) === 1},
            ${row.movement_type},
            ${row.fetched_at ? new Date(row.fetched_at as string) : new Date()},
            ${row.source_tool || 'cf_fetch'}
          )
          ON CONFLICT (person_id, run_month) DO NOTHING
        `;
        pushed++;
      } catch (err) {
        console.error(`[200] PUSH error for ${row.person_id}: ${err}`);
        errors++;
      }
    }
  }

  skipped = snapshots.results.length - pushed - errors;

  // Mark as pushed in batch progress
  await d1.prepare(
    "UPDATE batch_progress SET pushed_to_vault = 1, completed_at = datetime('now') WHERE run_month = ?"
  ).bind(runMonth).run();

  console.log(`[200] PUSH complete: pushed=${pushed} skipped=${skipped} errors=${errors}`);
  return { pushed, skipped, errors, durationMs: Date.now() - start };
}

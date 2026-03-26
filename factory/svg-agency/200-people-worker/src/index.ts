/**
 * Process 200 — People Worker
 *
 * Monthly CF Worker. Phase 1: LinkedIn movement detection.
 * D1 is the workspace. Neon is the vault.
 *
 * Monthly lifecycle:
 *   Day 1:    SEED — pull territory dossier from Neon → D1
 *   Days 1-28: FETCH — daily batches, fetch LinkedIn, write to D1
 *   Day 28+:  PUSH — confirmed results from D1 → Neon vault
 *
 * UT Sub-Hub 16: Distributed Fetcher via residential proxy tunnel.
 */

import { seedFromNeon, seedBaseline } from './seed';
import { pushToVault } from './push';
import { fetchUrl, type FetcherConfig } from './ut/fetcher';
import { parseLinkedInProfile, detectMovement } from './linkedin-parser';

export interface Env {
  D1: D1Database;
  NEON_URL: string;
  PROXY_URL: string;      // Tunnel proxy: https://linkedin-proxy.insuranceinformatic.agency
  PROXY_SECRET: string;   // Auth for the proxy
  BATCH_SIZE: string;
  MIN_DELAY_MS: string;
  MAX_DELAY_MS: string;
}

function getRunMonth(): string {
  return new Date().toISOString().slice(0, 7) + '-01';
}

function getFetcherConfig(env: Env): Partial<FetcherConfig> {
  return {
    proxyUrl: env.PROXY_URL || 'https://linkedin-proxy.insuranceinformatic.agency',
    proxySecret: env.PROXY_SECRET || 'linkedin-proxy-2026',
    timeoutMs: 30_000,
  };
}

// ─────────────────────────────────────────────────────────────
// FETCH PHASE — Process next batch of LinkedIn profiles
// ─────────────────────────────────────────────────────────────

async function processBatch(env: Env, runMonth: string): Promise<{ processed: number; movements: number; errors: number }> {
  const batchSize = parseInt(env.BATCH_SIZE || '100', 10);
  const fetcherConfig = getFetcherConfig(env);

  // Get unchecked profiles from D1
  const unchecked = await env.D1.prepare(`
    SELECT m.person_id, m.company_unique_id, m.full_name, m.linkedin_url, m.slot_type, m.agent_name
    FROM monitor_list m
    LEFT JOIN snapshots s ON s.person_id = m.person_id AND s.run_month = ?
    WHERE s.person_id IS NULL
    LIMIT ?
  `).bind(runMonth, batchSize).all<{
    person_id: string;
    company_unique_id: string;
    full_name: string;
    linkedin_url: string;
    slot_type: string;
    agent_name: string;
  }>();

  if (!unchecked.results || unchecked.results.length === 0) {
    console.log('[200] FETCH: All profiles checked this month.');
    return { processed: 0, movements: 0, errors: 0 };
  }

  let processed = 0;
  let movements = 0;
  let errors = 0;

  for (const row of unchecked.results) {
    // 1. Fetch via UT
    const fetchResult = await fetchUrl(row.linkedin_url, fetcherConfig);

    if (fetchResult.error || fetchResult.status !== 200) {
      await env.D1.prepare(`
        INSERT INTO errors (error_id, person_id, linkedin_url, error_code, error_message, run_month)
        VALUES (?, ?, ?, ?, ?, ?)
      `).bind(
        crypto.randomUUID(), row.person_id, row.linkedin_url,
        'FETCH_FAILED', fetchResult.error || `HTTP ${fetchResult.status}`, runMonth,
      ).run();
      errors++;
      processed++;
      continue;
    }

    // 2. Parse
    const profile = parseLinkedInProfile(fetchResult.body, row.linkedin_url);

    if (!profile.parseSuccess) {
      await env.D1.prepare(`
        INSERT INTO errors (error_id, person_id, linkedin_url, error_code, error_message, run_month)
        VALUES (?, ?, ?, ?, ?, ?)
      `).bind(
        crypto.randomUUID(), row.person_id, row.linkedin_url,
        'PARSE_FAILED', profile.parseError || 'Unknown', runMonth,
      ).run();
      errors++;
      processed++;
      continue;
    }

    // 3. Compare LinkedIn NOW vs what we have STORED in people/companies tables
    const stored = await env.D1.prepare(`
      SELECT p.title as stored_title, c.canonical_name as stored_company, c.company_domain
      FROM people p
      JOIN companies c ON c.company_unique_id = p.company_unique_id
      WHERE p.unique_id = ?
    `).bind(row.person_id).first<{ stored_title: string; stored_company: string; company_domain: string }>();

    const movement = stored
      ? detectMovement(profile, stored.stored_title || '', stored.stored_company || '')
      : { movement: 0 as const, titleChanged: false, companyChanged: false, movementType: 'NONE' as const };

    // 4. Write snapshot to D1 (coerce undefined → null for D1)
    const n = (v: unknown) => v === undefined ? null : v;
    await env.D1.prepare(`
      INSERT INTO snapshots (
        snapshot_id, person_id, company_unique_id, run_month,
        linkedin_url, raw_title_tag, parsed_name, parsed_title, parsed_company,
        headline, location, last_post_date, profile_photo_url,
        movement_detected, movement_type,
        fetched_at, source_tool, origin_domain, fetch_duration_ms, http_status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT (person_id, run_month) DO NOTHING
    `).bind(
      crypto.randomUUID(), row.person_id, row.company_unique_id, runMonth,
      row.linkedin_url, n(profile.rawTitleTag), n(profile.parsedName), n(profile.parsedTitle), n(profile.parsedCompany),
      n(profile.headline), n(profile.location), n(profile.lastPostDate), n(profile.profilePhotoUrl),
      movement.movement, movement.movementType,
      n(fetchResult.fetchedAt), 'cf_fetch', n(null), n(fetchResult.durationMs), n(fetchResult.status),
    ).run();

    if (movement.movement === 1) movements++;
    processed++;

    // Random delay between fetches (30-120s to mimic human browsing)
    if (processed < unchecked.results.length) {
      const minDelay = parseInt(env.MIN_DELAY_MS || '30000', 10);
      const maxDelay = parseInt(env.MAX_DELAY_MS || '120000', 10);
      const delay = minDelay + Math.floor(Math.random() * (maxDelay - minDelay));
      await new Promise((r) => setTimeout(r, delay));
    }
  }

  // Update batch progress
  await env.D1.prepare(`
    INSERT INTO batch_progress (run_month, total_profiles, checked, movements, errors, started_at, last_batch_at)
    VALUES (?, (SELECT COUNT(*) FROM monitor_list), ?, ?, ?, datetime('now'), datetime('now'))
    ON CONFLICT (run_month) DO UPDATE SET
      checked = batch_progress.checked + excluded.checked,
      movements = batch_progress.movements + excluded.movements,
      errors = batch_progress.errors + excluded.errors,
      last_batch_at = datetime('now')
  `).bind(runMonth, processed, movements, errors).run();

  console.log(`[200] FETCH: processed=${processed} movements=${movements} errors=${errors}`);
  return { processed, movements, errors };
}

// ─────────────────────────────────────────────────────────────
// CF WORKER ENTRY POINTS
// ─────────────────────────────────────────────────────────────

export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    const runMonth = getRunMonth();
    const day = new Date().getUTCDate();

    console.log(`[200] Cron | day=${day} | month=${runMonth}`);

    // Day 1: Seed territory dossier from Neon
    if (day === 1) {
      console.log('[200] SEED: Pulling territory dossier from Neon...');
      const seedResults = await seedFromNeon(env.D1, env.NEON_URL);
      for (const r of seedResults) {
        console.log(`[200] SEED: ${r.table} = ${r.rows} rows (${r.durationMs}ms)`);
      }
      const baselineResult = await seedBaseline(env.D1, env.NEON_URL, runMonth);
      console.log(`[200] SEED: baseline = ${baselineResult.rows} rows (${baselineResult.durationMs}ms)`);
    }

    // Days 1-28: Process batch
    if (day <= 28) {
      await processBatch(env, runMonth);
    }

    // Day 28+: Push to vault
    if (day >= 28) {
      const pushResult = await pushToVault(env.D1, env.NEON_URL, runMonth);
      console.log(`[200] PUSH: pushed=${pushResult.pushed} errors=${pushResult.errors} (${pushResult.durationMs}ms)`);
    }
  },

  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const runMonth = getRunMonth();

    // Health check
    if (url.pathname === '/health') {
      return Response.json({
        process: 'PROC-PEOPLE', number: 200, status: 'ok',
        domains: (env.DOMAIN_LIST || '').split(',').filter(Boolean).length,
      });
    }

    // Status — current month progress
    if (url.pathname === '/status') {
      const progress = await env.D1.prepare(
        'SELECT * FROM batch_progress WHERE run_month = ?'
      ).bind(runMonth).first();
      const monitor = await env.D1.prepare('SELECT COUNT(*) as cnt FROM monitor_list').first<{ cnt: number }>();
      const companies = await env.D1.prepare('SELECT COUNT(*) as cnt FROM companies').first<{ cnt: number }>();

      return Response.json({
        process: 'PROC-PEOPLE', run_month: runMonth,
        territory_companies: companies?.cnt || 0,
        monitor_list: monitor?.cnt || 0,
        progress: progress || 'not started',
      });
    }

    // Manual seed
    if (url.pathname === '/seed' && request.method === 'POST') {
      try {
        const seedResults = await seedFromNeon(env.D1, env.NEON_URL);
        const baselineResult = await seedBaseline(env.D1, env.NEON_URL, runMonth);
        return Response.json({
          action: 'seed',
          tables: seedResults,
          baseline: baselineResult,
        });
      } catch (err) {
        return Response.json({
          action: 'seed',
          error: err instanceof Error ? err.message : String(err),
        }, { status: 500 });
      }
    }

    // Manual batch
    if (url.pathname === '/run-batch' && request.method === 'POST') {
      try {
        const result = await processBatch(env, runMonth);
        return Response.json({ action: 'batch', ...result });
      } catch (err) {
        return Response.json({
          action: 'batch',
          error: err instanceof Error ? err.message : String(err),
        }, { status: 500 });
      }
    }

    // Manual push
    if (url.pathname === '/push' && request.method === 'POST') {
      const result = await pushToVault(env.D1, env.NEON_URL, runMonth);
      return Response.json({ action: 'push', ...result });
    }

    // Territory summary
    if (url.pathname === '/territory') {
      const summary = await env.D1.prepare(`
        SELECT agent_name, COUNT(*) as companies,
          (SELECT COUNT(*) FROM slots s WHERE s.company_unique_id = c.company_unique_id AND s.is_filled = 1) as sample_filled
        FROM companies c GROUP BY agent_name ORDER BY agent_name
      `).all();
      return Response.json({ territory: summary.results });
    }

    return new Response([
      'Process 200 — People Worker',
      '',
      'GET  /health     — health check',
      'GET  /status     — current month progress',
      'GET  /territory  — territory summary',
      'POST /seed       — seed from Neon',
      'POST /run-batch  — process next batch',
      'POST /push       — push to Neon vault',
    ].join('\n'), { status: 200 });
  },
};

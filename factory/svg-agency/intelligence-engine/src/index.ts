/**
 * Intelligence Engine — Main Entry Point
 *
 * CF Worker with three handlers:
 *   scheduled() — PRODUCER: cron trigger, reads D1, sends jobs to Queue
 *   queue()     — CONSUMER: pulls jobs from Queue, fetches, writes to D1
 *   fetch()     — HTTP API: /health, /status, /produce, /results
 */

import type { Env, IntelligenceJob } from './types';
import { produce } from './producer';
import { consume } from './consumer';

export default {
  // ── Cron Trigger (Producer) ──────────────────────────────

  async scheduled(
    _controller: ScheduledController,
    env: Env,
    _ctx: ExecutionContext,
  ): Promise<void> {
    console.log('[scheduled] Intelligence Engine — cron triggered');

    try {
      const stats = await produce(env);
      console.log(
        `[scheduled] Produced ${stats.total_jobs} jobs | batch=${stats.batch_id} | types=${JSON.stringify(stats.by_type)}`,
      );
    } catch (err) {
      console.error(`[scheduled] Production failed: ${err instanceof Error ? err.message : err}`);
    }
  },

  // ── Queue Consumer ───────────────────────────────────────

  async queue(
    batch: MessageBatch<IntelligenceJob>,
    env: Env,
    _ctx: ExecutionContext,
  ): Promise<void> {
    console.log(`[queue] Received batch of ${batch.messages.length} messages`);
    await consume(batch, env);
  },

  // ── HTTP API ─────────────────────────────────────────────

  async fetch(
    request: Request,
    env: Env,
    _ctx: ExecutionContext,
  ): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers for dashboard access
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    try {
      switch (path) {
        case '/health':
          return json({ status: 'ok', worker: 'intelligence-engine', timestamp: new Date().toISOString() }, corsHeaders);

        case '/status':
          return json(await getStatus(env), corsHeaders);

        case '/produce':
          if (request.method !== 'POST') {
            return json({ error: 'POST required' }, corsHeaders, 405);
          }
          return json(await handleProduce(env), corsHeaders);

        case '/results':
          return json(await getResults(env, url), corsHeaders);

        case '/results/recent':
          return json(await getRecentResults(env, url), corsHeaders);

        case '/results/signals':
          return json(await getSignals(env, url), corsHeaders);

        case '/results/movements':
          return json(await getMovements(env), corsHeaders);

        default:
          return json(
            {
              error: 'Not found',
              routes: ['/health', '/status', '/produce', '/results', '/results/recent', '/results/signals', '/results/movements'],
            },
            corsHeaders,
            404,
          );
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[fetch] Error: ${message}`);
      return json({ error: message }, corsHeaders, 500);
    }
  },
};

// ── HTTP Handlers ──────────────────────────────────────────

async function getStatus(env: Env): Promise<Record<string, unknown>> {
  const monthKey = getCurrentMonthKey();

  // Get batch progress
  let batches: Array<Record<string, unknown>> = [];
  try {
    const rows = await env.D1
      .prepare(
        `SELECT batch_id, month_key, total_jobs, by_type, produced_at
         FROM batch_progress
         WHERE month_key = ?
         ORDER BY produced_at DESC
         LIMIT 10`,
      )
      .bind(monthKey)
      .all();
    batches = (rows.results ?? []) as Array<Record<string, unknown>>;
  } catch {
    // Table may not exist
  }

  // Get queue state summary
  let queueState: Record<string, number> = {};
  try {
    const rows = await env.D1
      .prepare(
        `SELECT status, COUNT(*) as count
         FROM job_queue_state
         WHERE month_key = ?
         GROUP BY status`,
      )
      .bind(monthKey)
      .all<{ status: string; count: number }>();
    for (const row of rows.results ?? []) {
      queueState[row.status] = row.count;
    }
  } catch {
    // Table may not exist
  }

  // Get result count
  let resultCount = 0;
  try {
    const row = await env.D1
      .prepare(`SELECT COUNT(*) as count FROM intelligence_results`)
      .first<{ count: number }>();
    resultCount = row?.count ?? 0;
  } catch {
    // Table may not exist
  }

  return {
    worker: 'intelligence-engine',
    month: monthKey,
    recent_batches: batches,
    queue_state: queueState,
    total_results: resultCount,
    timestamp: new Date().toISOString(),
  };
}

async function handleProduce(env: Env): Promise<Record<string, unknown>> {
  const stats = await produce(env);
  return {
    success: true,
    ...stats,
  };
}

async function getResults(env: Env, url: URL): Promise<Record<string, unknown>> {
  const companyId = url.searchParams.get('company_id');
  const jobType = url.searchParams.get('job_type');
  const limit = parseInt(url.searchParams.get('limit') ?? '50', 10);

  let query = 'SELECT * FROM intelligence_results WHERE 1=1';
  const params: (string | number)[] = [];

  if (companyId) {
    query += ' AND company_unique_id = ?';
    params.push(companyId);
  }
  if (jobType) {
    query += ' AND job_type = ?';
    params.push(jobType);
  }

  query += ' ORDER BY fetched_at DESC LIMIT ?';
  params.push(limit);

  const stmt = env.D1.prepare(query);
  const bound = params.length > 0 ? stmt.bind(...params) : stmt;
  const rows = await bound.all();

  return {
    count: rows.results?.length ?? 0,
    results: rows.results ?? [],
  };
}

async function getRecentResults(env: Env, url: URL): Promise<Record<string, unknown>> {
  const hours = parseInt(url.searchParams.get('hours') ?? '24', 10);
  const cutoff = new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();

  const rows = await env.D1
    .prepare(
      `SELECT job_type, company_unique_id, signal_type, signal_score,
              movement_detected, movement_type, fetched_at, error
       FROM intelligence_results
       WHERE fetched_at > ?
       ORDER BY fetched_at DESC
       LIMIT 200`,
    )
    .bind(cutoff)
    .all();

  return {
    hours,
    count: rows.results?.length ?? 0,
    results: rows.results ?? [],
  };
}

async function getSignals(env: Env, url: URL): Promise<Record<string, unknown>> {
  const minScore = parseInt(url.searchParams.get('min_score') ?? '50', 10);

  const rows = await env.D1
    .prepare(
      `SELECT job_id, job_type, company_unique_id, person_id,
              signal_type, signal_score, parsed_data, keyword_matches,
              movement_detected, movement_type, fetched_at
       FROM intelligence_results
       WHERE signal_score >= ? AND error IS NULL
       ORDER BY signal_score DESC
       LIMIT 100`,
    )
    .bind(minScore)
    .all();

  return {
    min_score: minScore,
    count: rows.results?.length ?? 0,
    signals: rows.results ?? [],
  };
}

async function getMovements(env: Env): Promise<Record<string, unknown>> {
  const rows = await env.D1
    .prepare(
      `SELECT job_id, company_unique_id, person_id,
              signal_score, parsed_data, movement_type, fetched_at
       FROM intelligence_results
       WHERE movement_detected = 1
       ORDER BY fetched_at DESC
       LIMIT 100`,
    )
    .all();

  return {
    count: rows.results?.length ?? 0,
    movements: rows.results ?? [],
  };
}

// ── Utilities ──────────────────────────────────────────────

function json(
  data: Record<string, unknown>,
  corsHeaders: Record<string, string>,
  status = 200,
): Response {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders,
    },
  });
}

function getCurrentMonthKey(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

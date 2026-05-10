/**
 * LCS Hub — Main Entry Point
 *
 * The plumbing. Hub-spoke architecture.
 * All logic in the hub. Spokes are dumb transport.
 *
 * Three handlers:
 *   scheduled() — PRODUCER: cron trigger, scans for pending signals, queues jobs
 *   queue()     — CONSUMER: processes pipeline jobs (CID → SID → MID)
 *   fetch()     — HTTP API: signal ingestion, webhook receivers, health/status
 *
 * D1 = workspace (edge). Neon = vault (source of truth).
 * All integrations through Composio.
 */

import type { Env, PipelineJob } from './types';
import { ingestSignal, ingestSignalBatch } from './spokes/signal-intake';
import { compileCid, designSid, deliverMid } from './compiler';
import { logEvent, logError } from './utils';

export default {
  // ── Cron Trigger (Producer) ──────────────────────────────
  // Scans for pending signals, groups by company, queues compilation jobs.

  async scheduled(
    _controller: ScheduledController,
    env: Env,
    _ctx: ExecutionContext,
  ): Promise<void> {
    console.log('[scheduled] LCS Hub — cron triggered');

    try {
      // 1. Find all pending signals grouped by company
      const pending = await env.D1.prepare(`
        SELECT sq.sovereign_company_id, GROUP_CONCAT(sq.signal_id) as signal_ids, COUNT(*) as signal_count
        FROM signal_queue sq
        JOIN company c ON c.sovereign_company_id = sq.sovereign_company_id
        WHERE sq.status = 'pending'
          AND (sq.expires_at IS NULL OR sq.expires_at > datetime('now'))
          AND c.assigned_agent IS NOT NULL
          AND c.assigned_agent != ''
        GROUP BY sq.sovereign_company_id
        ORDER BY signal_count DESC
        LIMIT 50
      `).all<{
        sovereign_company_id: string;
        signal_ids: string;
        signal_count: number;
      }>();

      if (!pending.results || pending.results.length === 0) {
        console.log('[scheduled] No pending signals. Done.');
        return;
      }

      console.log(`[scheduled] Found ${pending.results.length} companies with pending signals`);

      // 2. Queue a compilation job for each company
      let queued = 0;
      for (const row of pending.results) {
        const signalIds = row.signal_ids.split(',');

        // Mark signals as processing
        const placeholders = signalIds.map(() => '?').join(',');
        await env.D1.prepare(
          `UPDATE signal_queue SET status = 'processing', updated_at = datetime('now') WHERE signal_id IN (${placeholders})`
        ).bind(...signalIds).run();

        // Queue the job
        await env.LCS_QUEUE.send({
          job_type: 'compile_cid',
          sovereign_company_id: row.sovereign_company_id,
          signal_ids: signalIds,
        });

        queued++;
      }

      console.log(`[scheduled] Queued ${queued} compilation jobs`);
    } catch (err) {
      console.error(`[scheduled] Producer failed: ${err instanceof Error ? err.message : err}`);
    }
  },

  // ── Queue Consumer ───────────────────────────────────────
  // Processes pipeline jobs: compile_cid → design_sid → deliver_mid

  async queue(
    batch: MessageBatch<PipelineJob>,
    env: Env,
    _ctx: ExecutionContext,
  ): Promise<void> {
    console.log(`[queue] Received batch of ${batch.messages.length} jobs`);

    for (const msg of batch.messages) {
      const job = msg.body;

      try {
        switch (job.job_type) {
          case 'compile_cid':
            console.log(`[queue] Compiling CID for ${job.sovereign_company_id}`);
            await compileCid(env, job.sovereign_company_id, job.signal_ids ?? []);
            break;

          case 'design_sid':
            console.log(`[queue] Designing SID for CID ${job.cid_id}`);
            await designSid(env, job.cid_id!);
            break;

          case 'deliver_mid':
            console.log(`[queue] Delivering MID for SID ${job.sid_id}`);
            await deliverMid(env, job.sid_id!);
            break;

          case 'process_webhook':
            console.log(`[queue] Processing webhook from ${job.webhook_source}`);
            await processWebhook(env, job);
            break;

          default:
            console.error(`[queue] Unknown job type: ${(job as any).job_type}`);
        }

        msg.ack();
      } catch (err) {
        console.error(`[queue] Job failed: ${err instanceof Error ? err.message : err}`);
        msg.retry();
      }
    }
  },

  // ── HTTP API ─────────────────────────────────────────────

  async fetch(
    request: Request,
    env: Env,
    _ctx: ExecutionContext,
  ): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    try {
      // ── Health Check ────────────────────────────────────
      if (path === '/health') {
        const signalCount = await env.D1.prepare(
          "SELECT COUNT(*) as cnt FROM signal_queue"
        ).first<{ cnt: number }>();
        const cidCount = await env.D1.prepare(
          "SELECT COUNT(*) as cnt FROM cid"
        ).first<{ cnt: number }>();

        return json({
          status: 'ok',
          worker: 'lcs-hub',
          signals: signalCount?.cnt ?? 0,
          cids: cidCount?.cnt ?? 0,
          timestamp: new Date().toISOString(),
        }, corsHeaders);
      }

      // ── Signal Ingestion (spoke IN) ─────────────────────
      if (path === '/signal' && request.method === 'POST') {
        const body = await request.json<Record<string, unknown>>();
        const result = await ingestSignal(env.D1, body);
        const status = 'error' in result ? 400 : 201;
        return json(result, corsHeaders, status);
      }

      // ── Batch Signal Ingestion ──────────────────────────
      if (path === '/signals' && request.method === 'POST') {
        const body = await request.json<Record<string, unknown>[]>();
        const result = await ingestSignalBatch(env.D1, body);
        return json(result, corsHeaders, 201);
      }

      // ── Webhook: Mailgun ────────────────────────────────
      if (path === '/webhook/mailgun' && request.method === 'POST') {
        const payload = await request.json<Record<string, unknown>>();
        // Process directly (local dev) instead of via queue
        await processWebhook(env, {
          job_type: 'process_webhook',
          sovereign_company_id: '',
          webhook_source: 'mailgun',
          webhook_payload: payload,
        });
        return json({ received: true, processed: true }, corsHeaders);
      }

      // ── Webhook: HeyReach ───────────────────────────────
      if (path === '/webhook/heyreach' && request.method === 'POST') {
        const payload = await request.json<Record<string, unknown>>();
        await processWebhook(env, {
          job_type: 'process_webhook',
          sovereign_company_id: '',
          webhook_source: 'heyreach',
          webhook_payload: payload,
        });
        return json({ received: true, processed: true }, corsHeaders);
      }

      // ── Status: Pipeline overview ───────────────────────
      if (path === '/status') {
        const stats = await getPipelineStats(env.D1);
        return json(stats, corsHeaders);
      }

      // ── Status: Company detail ──────────────────────────
      if (path.startsWith('/company/') && request.method === 'GET') {
        const companyId = path.replace('/company/', '');
        const detail = await getCompanyDetail(env.D1, companyId);
        return json(detail, corsHeaders);
      }

      // ── Trace: Bidirectional ID lookup ──────────────────
      if (path.startsWith('/trace/') && request.method === 'GET') {
        const id = path.replace('/trace/', '');
        const trace = await traceId(env.D1, id);
        return json(trace, corsHeaders);
      }

      // ── Manual Pipeline Trigger (local dev) ─────────────
      // Bypasses queue — runs compiler directly for smoke testing
      if (path === '/run' && request.method === 'POST') {
        const body = await request.json<{ sovereign_company_id: string }>();
        if (!body.sovereign_company_id) {
          return json({ error: 'sovereign_company_id required' }, corsHeaders, 400);
        }

        // 1. Find pending signals for this company
        const pending = await env.D1.prepare(
          "SELECT signal_id FROM signal_queue WHERE sovereign_company_id = ? AND status IN ('pending', 'processing')"
        ).bind(body.sovereign_company_id).all<{ signal_id: string }>();

        if (!pending.results || pending.results.length === 0) {
          return json({ error: 'No pending signals for this company' }, corsHeaders, 400);
        }

        const signalIds = pending.results.map(r => r.signal_id);

        // 2. Compile CID
        const cid = await compileCid(env, body.sovereign_company_id, signalIds);
        if (!cid) {
          return json({ error: 'CID compilation failed — check /status for errors' }, corsHeaders, 500);
        }

        // 3. Design SID (if CID compiled successfully)
        let sid = null;
        if (cid.status === 'compiled') {
          sid = await designSid(env, cid.cid_id);
        }

        // 4. Deliver first MID (if SID designed)
        let midResult = null;
        if (sid) {
          await deliverMid(env, sid.sid_id);
          // Fetch the MID record
          const midRow = await env.D1.prepare(
            'SELECT * FROM mid WHERE sid_id = ? ORDER BY sequence_num LIMIT 1'
          ).bind(sid.sid_id).first();
          midResult = midRow;
        }

        return json({
          pipeline: 'complete',
          cid: { id: cid.cid_id, status: cid.status, gates_passed: cid.gate_results.filter(g => g.passed).length },
          sid: sid ? { id: sid.sid_id, campaign_type: sid.campaign_type, audience_path: sid.audience_path, messages: sid.messages.length } : null,
          mid: midResult,
        }, corsHeaders);
      }

      // ── Seed: Load company data into D1 workspace ──────
      if (path === '/seed' && request.method === 'POST') {
        const companies = await request.json<any[]>();
        let seeded = 0;
        for (const c of companies) {
          await env.D1.prepare(`
            INSERT OR REPLACE INTO company (
              sovereign_company_id, company_name, state, zip, employee_count, assigned_agent,
              has_5500_filing, renewal_month, premium_current, premium_prior,
              carrier_current, carrier_prior, broker_current, broker_prior,
              ceo_name, ceo_email, ceo_linkedin, cfo_name, cfo_email, cfo_linkedin,
              hr_name, hr_email, hr_linkedin, lifecycle_phase, seeded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
          `).bind(
            c.sovereign_company_id, c.company_name, c.state, c.zip, c.employee_count, c.assigned_agent,
            c.has_5500_filing ? 1 : 0, c.renewal_month, c.premium_current, c.premium_prior,
            c.carrier_current, c.carrier_prior, c.broker_current, c.broker_prior,
            c.ceo_name, c.ceo_email, c.ceo_linkedin, c.cfo_name, c.cfo_email, c.cfo_linkedin,
            c.hr_name, c.hr_email, c.hr_linkedin, c.lifecycle_phase ?? 'OUTREACH',
          ).run();
          seeded++;
        }
        return json({ seeded }, corsHeaders, 201);
      }

      return json({ error: 'Not found' }, corsHeaders, 404);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      return json({ error: msg }, corsHeaders, 500);
    }
  },
};

// ── Webhook Processing ──────────────────────────────────────

async function processWebhook(env: Env, job: PipelineJob): Promise<void> {
  const payload = job.webhook_payload ?? {};
  const source = job.webhook_source;

  // Extract MID from webhook payload
  let midId: string | null = null;
  let eventType: string | null = null;

  if (source === 'mailgun') {
    // Mailgun webhook structure
    const eventData = payload['event-data'] as any ?? payload;
    midId = eventData?.['user-variables']?.mid_id ?? null;
    const mgEvent = eventData?.event ?? '';
    eventType = mgEvent === 'delivered' ? 'mid_delivered'
      : mgEvent === 'opened' ? 'mid_opened'
      : mgEvent === 'clicked' ? 'mid_clicked'
      : mgEvent === 'failed' || mgEvent === 'bounced' ? 'mid_bounced'
      : null;
  } else if (source === 'heyreach') {
    midId = (payload as any)?.custom_variables?.mid_id ?? null;
    eventType = (payload as any)?.event === 'accepted' ? 'mid_delivered' : 'mid_bounced';
  }

  if (!midId || !eventType) {
    console.log(`[webhook] Could not extract MID from ${source} payload`);
    return;
  }

  // Update MID record
  const mid = await env.D1.prepare('SELECT * FROM mid WHERE mid_id = ?')
    .bind(midId).first<any>();

  if (!mid) {
    console.log(`[webhook] MID ${midId} not found`);
    return;
  }

  const statusField = eventType === 'mid_delivered' ? 'delivered_at'
    : eventType === 'mid_opened' ? 'opened_at'
    : eventType === 'mid_clicked' ? 'clicked_at'
    : eventType === 'mid_bounced' ? 'bounced_at'
    : null;

  const newDeliveryStatus = eventType === 'mid_delivered' ? 'delivered'
    : eventType === 'mid_opened' ? 'opened'
    : eventType === 'mid_clicked' ? 'clicked'
    : eventType === 'mid_bounced' ? 'bounced'
    : mid.delivery_status;

  if (statusField) {
    await env.D1.prepare(
      `UPDATE mid SET delivery_status = ?, ${statusField} = datetime('now'), webhook_payload = ?, updated_at = datetime('now') WHERE mid_id = ?`
    ).bind(newDeliveryStatus, JSON.stringify(payload), midId).run();
  }

  // Log the event
  await logEvent(env.D1, {
    sovereign_company_id: mid.sovereign_company_id,
    cid_id: mid.cid_id,
    sid_id: mid.sid_id,
    mid_id: midId,
    event_type: eventType,
    event_data: { source, delivery_status: newDeliveryStatus },
  });

  // If CTA clicked → meeting set → lifecycle promotion
  if (eventType === 'mid_clicked') {
    await env.D1.prepare(
      "UPDATE sid SET status = 'stopped', updated_at = datetime('now') WHERE sid_id = ?"
    ).bind(mid.sid_id).run();
    await logEvent(env.D1, {
      sovereign_company_id: mid.sovereign_company_id,
      sid_id: mid.sid_id,
      event_type: 'campaign_stopped',
      event_data: { reason: 'cta_click', mid_id: midId },
    });
  }

  // If bounced → check strikes
  if (eventType === 'mid_bounced') {
    const strikes = await env.D1.prepare(
      `UPDATE mid SET strike_count = strike_count + 1, updated_at = datetime('now') WHERE mid_id = ? RETURNING strike_count`
    ).bind(midId).first<{ strike_count: number }>();

    await logError(env.D1, {
      sovereign_company_id: mid.sovereign_company_id,
      cid_id: mid.cid_id,
      sid_id: mid.sid_id,
      mid_id: midId,
      stage: 'webhook',
      error_type: 'bounce',
      error_message: `${source} bounce on ${midId}`,
      strike_count: strikes?.strike_count ?? 1,
    });
  }
}

// ── Status Helpers ──────────────────────────────────────────

async function getPipelineStats(d1: D1Database): Promise<Record<string, unknown>> {
  const signals = await d1.prepare(
    "SELECT status, COUNT(*) as cnt FROM signal_queue GROUP BY status"
  ).all();
  const cids = await d1.prepare(
    "SELECT status, COUNT(*) as cnt FROM cid GROUP BY status"
  ).all();
  const sids = await d1.prepare(
    "SELECT status, COUNT(*) as cnt FROM sid GROUP BY status"
  ).all();
  const mids = await d1.prepare(
    "SELECT delivery_status, COUNT(*) as cnt FROM mid GROUP BY delivery_status"
  ).all();
  const errors = await d1.prepare(
    "SELECT stage, COUNT(*) as cnt FROM err0 GROUP BY stage"
  ).all();
  const suppressions = await d1.prepare(
    "SELECT reason, COUNT(*) as cnt FROM suppression GROUP BY reason"
  ).all();

  return {
    signals: signals.results ?? [],
    cids: cids.results ?? [],
    sids: sids.results ?? [],
    mids: mids.results ?? [],
    errors: errors.results ?? [],
    suppressions: suppressions.results ?? [],
    timestamp: new Date().toISOString(),
  };
}

async function getCompanyDetail(
  d1: D1Database,
  companyId: string,
): Promise<Record<string, unknown>> {
  const signals = await d1.prepare(
    'SELECT * FROM signal_queue WHERE sovereign_company_id = ? ORDER BY created_at DESC LIMIT 20'
  ).bind(companyId).all();
  const cids = await d1.prepare(
    'SELECT * FROM cid WHERE sovereign_company_id = ? ORDER BY created_at DESC LIMIT 5'
  ).bind(companyId).all();
  const sids = await d1.prepare(
    'SELECT * FROM sid WHERE sovereign_company_id = ? ORDER BY created_at DESC LIMIT 5'
  ).bind(companyId).all();
  const mids = await d1.prepare(
    'SELECT * FROM mid WHERE sovereign_company_id = ? ORDER BY created_at DESC LIMIT 20'
  ).bind(companyId).all();
  const events = await d1.prepare(
    'SELECT * FROM event WHERE sovereign_company_id = ? ORDER BY created_at DESC LIMIT 50'
  ).bind(companyId).all();

  return {
    sovereign_company_id: companyId,
    signals: signals.results ?? [],
    cids: cids.results ?? [],
    sids: sids.results ?? [],
    mids: mids.results ?? [],
    events: events.results ?? [],
  };
}

async function traceId(
  d1: D1Database,
  id: string,
): Promise<Record<string, unknown>> {
  // Detect ID type by prefix
  if (id.startsWith('SIG-')) {
    const signal = await d1.prepare('SELECT * FROM signal_queue WHERE signal_id = ?').bind(id).first();
    return { type: 'signal', data: signal };
  }
  if (id.startsWith('CID-')) {
    const cid = await d1.prepare('SELECT * FROM cid WHERE cid_id = ?').bind(id).first();
    const sids = await d1.prepare('SELECT * FROM sid WHERE cid_id = ?').bind(id).all();
    return { type: 'cid', data: cid, campaigns: sids.results };
  }
  if (id.startsWith('SID-')) {
    const sid = await d1.prepare('SELECT * FROM sid WHERE sid_id = ?').bind(id).first();
    const mids = await d1.prepare('SELECT * FROM mid WHERE sid_id = ?').bind(id).all();
    return { type: 'sid', data: sid, deliveries: mids.results };
  }
  if (id.startsWith('MID-')) {
    const mid = await d1.prepare('SELECT * FROM mid WHERE mid_id = ?').bind(id).first();
    return { type: 'mid', data: mid };
  }

  return { error: 'Unknown ID format. Use SIG-, CID-, SID-, or MID- prefix.' };
}

// ── Helpers ─────────────────────────────────────────────────

function json(data: unknown, headers: Record<string, string>, status = 200): Response {
  return Response.json(data, { status, headers: { ...headers, 'Content-Type': 'application/json' } });
}

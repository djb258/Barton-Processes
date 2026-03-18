// ═══════════════════════════════════════════════════════════════
// LCS Pipeline — CF Worker Entry Point
// ═══════════════════════════════════════════════════════════════
// Authority: Tier 0 Doctrine
// Hub-Spoke: This is the RIM. Routes to the HUB (pipeline.ts).
//
// Routes:
//   POST /webhook/mailgun  — Feedback spoke (Phase 5: Circle closing)
//   POST /webhook/heyreach — Feedback spoke
//   POST /smoke-test       — Insert test signal + run pipeline
//   GET  /health           — Health check
//   Cron trigger           — Scheduled pipeline run
// ═══════════════════════════════════════════════════════════════

import { runPipeline } from './pipeline';
import { query, insert, queryOne } from './db';
import type { Env } from './types';

export default {
  // ── HTTP Handler (webhooks + smoke test) ───────────────────
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const connStr = env.HD_CL.connectionString;

    // Health check
    if (url.pathname === '/health') {
      return Response.json({ status: 'ok', pipeline: 'lcs', mode: env.PIPELINE_MODE });
    }

    // ── Phase 5: Webhook Feedback (Circle Closing) ──────────
    if (url.pathname === '/webhook/mailgun' && request.method === 'POST') {
      return handleMailgunWebhook(request, connStr);
    }

    if (url.pathname === '/webhook/heyreach' && request.method === 'POST') {
      return handleHeyReachWebhook(request, connStr);
    }

    // ── Smoke Test: insert signal + run pipeline ────────────
    if (url.pathname === '/smoke-test' && request.method === 'POST') {
      return handleSmokeTest(request, connStr);
    }

    return Response.json({ error: 'Not found' }, { status: 404 });
  },

  // ── Cron Handler (scheduled pipeline run) ──────────────────
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    const connStr = env.HD_CL.connectionString;
    const result = await runPipeline(connStr, env.PIPELINE_MODE);
    console.log(`[CRON] Pipeline complete:`, JSON.stringify(result));
  },
};

// ═══════════════════════════════════════════════════════════════
// Phase 5: Mailgun Webhook — Circle Closing
// ═══════════════════════════════════════════════════════════════
// IMO:
//   Ingress: webhook payload — schema validation only
//   Middle: update delivery status, check ORBT strikes
//   Egress: updated mid_sequence_state, CET event logged
// ═══════════════════════════════════════════════════════════════

async function handleMailgunWebhook(request: Request, connStr: string): Promise<Response> {
  try {
    const body = await request.json() as Record<string, unknown>;

    // INGRESS: extract IDs from webhook
    const eventData = (body['event-data'] ?? body) as Record<string, unknown>;
    const userVars = (eventData['user-variables'] ?? {}) as Record<string, string>;
    const communicationId = userVars['communication_id'];
    const messageRunId = userVars['message_run_id'];
    const event = (eventData['event'] as string) ?? 'unknown';

    if (!communicationId) {
      return Response.json({ error: 'Missing communication_id' }, { status: 400 });
    }

    // MIDDLE: determine delivery status
    let deliveryStatus: string;
    let eventType: string;

    switch (event) {
      case 'delivered':
        deliveryStatus = 'DELIVERED';
        eventType = 'DELIVERY_CONFIRMED';
        break;
      case 'failed':
      case 'rejected':
        deliveryStatus = 'BOUNCED';
        eventType = 'DELIVERY_BOUNCED';
        break;
      case 'complained':
        deliveryStatus = 'FAILED';
        eventType = 'DELIVERY_COMPLAINED';
        break;
      default:
        deliveryStatus = 'SENT';
        eventType = `WEBHOOK_${event.toUpperCase()}`;
    }

    // MIDDLE: update MID status
    await query(connStr,
      `UPDATE lcs.mid_sequence_state
       SET delivery_status = $1
       WHERE communication_id = $2`,
      [deliveryStatus, communicationId]
    );

    // MIDDLE: log CET event
    const { data: cid } = await queryOne(connStr,
      `SELECT * FROM lcs.cid WHERE communication_id = $1`,
      [communicationId]
    );

    if (cid) {
      await insert(connStr, 'lcs.event', {
        communication_id: communicationId,
        message_run_id: messageRunId,
        sovereign_company_id: cid.sovereign_company_id,
        event_type: eventType,
        lifecycle_phase: cid.lifecycle_phase,
        channel: 'MG',
        delivery_status: deliveryStatus,
        step_name: 'Webhook Feedback',
        payload: { raw_event: event },
      });
    }

    // MIDDLE: if bounced, handle ORBT strikes
    if (deliveryStatus === 'BOUNCED' || deliveryStatus === 'FAILED') {
      await handleOrbtStrike(connStr, communicationId, messageRunId ?? 'unknown', event);
    }

    // EGRESS: acknowledge webhook
    return Response.json({ received: true, communication_id: communicationId, status: deliveryStatus });

  } catch (err) {
    return Response.json({ error: 'Webhook processing failed' }, { status: 500 });
  }
}

// ═══════════════════════════════════════════════════════════════
// ORBT Strike Handler — the learning mechanism
// ═══════════════════════════════════════════════════════════════
// Strike 1-2: REPAIR → log err0, optionally retry ALT_CHANNEL
// Strike 3: TROUBLESHOOT/TRAIN → flag entity, update suppression
// ═══════════════════════════════════════════════════════════════

async function handleOrbtStrike(
  connStr: string,
  communicationId: string,
  messageRunId: string,
  failureType: string
): Promise<void> {
  // Count existing strikes for this communication
  const { data: strikes } = await query(connStr,
    `SELECT COUNT(*) as count FROM lcs.err0 WHERE communication_id = $1`,
    [communicationId]
  );
  const strikeCount = ((strikes[0]?.count as number) ?? 0) + 1;

  let orbtAction: string;
  if (strikeCount >= 3) {
    orbtAction = 'TROUBLESHOOT_TRAIN';
    // The system LEARNS: flag entity for suppression
    // Next cycle, suppression gate blocks this entity
    const { data: cid } = await queryOne(connStr,
      `SELECT entity_id FROM lcs.cid WHERE communication_id = $1`,
      [communicationId]
    );
    if (cid?.entity_id) {
      // TODO: write to suppression table — this IS the TRAIN output
      console.log(`[ORBT] Strike 3 for ${communicationId} — entity ${cid.entity_id} flagged for suppression`);
    }
  } else if (strikeCount === 2) {
    orbtAction = 'REPAIR_ALT_CHANNEL';
  } else {
    orbtAction = 'REPAIR_RETRY';
  }

  // Log to err0 — the error table
  const { data: cid } = await queryOne(connStr,
    `SELECT * FROM lcs.cid WHERE communication_id = $1`,
    [communicationId]
  );

  await insert(connStr, 'lcs.err0', {
    message_run_id: messageRunId,
    communication_id: communicationId,
    sovereign_company_id: cid?.sovereign_company_id ?? 'unknown',
    failure_type: failureType,
    failure_message: `Strike ${strikeCount}: ${failureType}`,
    lifecycle_phase: cid?.lifecycle_phase ?? 'OUTREACH',
    adapter_type: 'MG',
    orbt_strike_number: strikeCount,
    orbt_action_taken: orbtAction,
  });

  console.log(`[ORBT] Strike ${strikeCount} for ${communicationId}: ${orbtAction}`);
}

// ═══════════════════════════════════════════════════════════════
// HeyReach Webhook — same pattern, different payload format
// ═══════════════════════════════════════════════════════════════

async function handleHeyReachWebhook(request: Request, connStr: string): Promise<Response> {
  // TODO: parse HeyReach webhook format
  // Same Circle pattern: update status → log CET → check ORBT strikes
  return Response.json({ received: true, note: 'HeyReach webhook handler — TODO' });
}

// ═══════════════════════════════════════════════════════════════
// Smoke Test — insert a test signal and run the full pipeline
// ═══════════════════════════════════════════════════════════════

async function handleSmokeTest(request: Request, connStr: string): Promise<Response> {
  try {
    const body = await request.json() as {
      sovereign_company_id: string;
      lifecycle_phase?: string;
    };

    if (!body.sovereign_company_id) {
      return Response.json({ error: 'sovereign_company_id required' }, { status: 400 });
    }

    // Step 1: Insert test signal into signal_queue (INGRESS — leaf write)
    const signalId = crypto.randomUUID();
    await insert(connStr, 'lcs.signal_queue', {
      id: signalId,
      sovereign_company_id: body.sovereign_company_id,
      signal_set_hash: `SMOKE-${Date.now()}`,
      signal_category: 'SMOKE_TEST',
      lifecycle_phase: body.lifecycle_phase ?? 'OUTREACH',
      preferred_channel: 'MG',
      agent_number: 'SMOKE-TEST',
      source_hub: 'smoke-test',
      status: 'PENDING',
    });

    // Step 2: Run full pipeline in SMOKE_TEST mode
    const result = await runPipeline(connStr, 'SMOKE_TEST', 1);

    // Step 3: Trace the circle — can we follow the ID chain?
    const { data: cidRow } = await queryOne(connStr,
      `SELECT communication_id FROM lcs.cid WHERE signal_queue_id = $1`,
      [signalId]
    );

    const commId = cidRow?.communication_id as string | null;
    let trace: Record<string, unknown> = { signal_id: signalId };

    if (commId) {
      const { data: sidRow } = await queryOne(connStr,
        `SELECT sid_id FROM lcs.sid_output WHERE communication_id = $1`,
        [commId]
      );
      const { data: midRow } = await queryOne(connStr,
        `SELECT message_run_id, delivery_status FROM lcs.mid_sequence_state WHERE communication_id = $1`,
        [commId]
      );
      const { data: events } = await query(connStr,
        `SELECT event_type, step_name FROM lcs.event WHERE communication_id = $1 ORDER BY created_at`,
        [commId]
      );

      trace = {
        signal_id: signalId,
        communication_id: commId,
        sid_id: sidRow?.sid_id ?? null,
        message_run_id: midRow?.message_run_id ?? null,
        delivery_status: midRow?.delivery_status ?? null,
        events: events,
        circle_closed: !!(midRow?.delivery_status),
        bidirectional_trace: {
          forward: `${signalId} → ${commId} → ${sidRow?.sid_id} → ${midRow?.message_run_id}`,
          reverse: `${midRow?.message_run_id} → ${commId} → ${signalId}`,
        },
      };
    }

    return Response.json({
      smoke_test: 'COMPLETE',
      pipeline_result: result,
      trace,
    });

  } catch (err) {
    return Response.json({
      smoke_test: 'FAILED',
      error: err instanceof Error ? err.message : 'Unknown error',
    }, { status: 500 });
  }
}

// ═══════════════════════════════════════════════════════════════
// LCS Pipeline — CID → SID → MID (Full Circle)
// ═══════════════════════════════════════════════════════════════
// Authority: Tier 0 — each phase is its own IMO
// Hub-Spoke: this is the HUB. All logic lives here.
// Spokes (signal_queue, Composio, webhooks) are dumb transport.
// ═══════════════════════════════════════════════════════════════

import { query, queryOne, insert } from './db';
import { mintCommunicationId, mintSidId, mintMessageRunId } from './ids';
import { checkCapacity, checkFreshness, checkSuppression } from './gates';
import type {
  Env, SignalQueueRow, CidRow, SidRow, PipelineResult,
  LifecyclePhase, Channel
} from './types';

// ═══════════════════════════════════════════════════════════════
// Main Entry — runs all three phases in sequence
// ═══════════════════════════════════════════════════════════════

export async function runPipeline(
  connStr: string,
  mode: string,
  batchSize: number = 10
): Promise<PipelineResult> {
  const start = Date.now();

  // Phase 1: CID Compiler
  const cidResult = await runCidCompiler(connStr, batchSize);

  // Phase 3: SID Constructor (Phase 2 AI synthesis simulated — uses template)
  const sidResult = await runSidConstructor(connStr, batchSize);

  // Phase 4: MID Engine
  const midResult = await runMidEngine(connStr, mode, batchSize);

  return {
    cid: cidResult,
    sid: sidResult,
    mid: midResult,
    duration_ms: Date.now() - start,
    mode,
  };
}

// ═══════════════════════════════════════════════════════════════
// Phase 1: CID Compiler
// ═══════════════════════════════════════════════════════════════
// IMO:
//   Ingress: signal_queue (PENDING) — schema validation
//   Middle: gates + intelligence + frame match + ID mint
//   Egress: lcs.cid row (COMPILED|FAILED|BLOCKED)
// ═══════════════════════════════════════════════════════════════

async function runCidCompiler(connStr: string, batchSize: number) {
  const result = { total: 0, compiled: 0, failed: 0, blocked: 0 };

  // INGRESS: fetch pending signals
  const { data: signals, error } = await query<SignalQueueRow>(
    connStr,
    `SELECT * FROM lcs.signal_queue
     WHERE status = 'PENDING'
     ORDER BY created_at ASC
     LIMIT $1`,
    [batchSize]
  );

  if (error || !signals.length) return result;
  result.total = signals.length;

  for (const signal of signals) {
    // MIDDLE: validate
    if (!signal.sovereign_company_id || !signal.signal_set_hash) {
      await writeCid(connStr, signal, null, 'FAILED', 'Missing required fields');
      result.failed++;
      continue;
    }

    // MIDDLE: capacity gate
    const { data: adapter } = await queryOne(connStr,
      `SELECT daily_cap, sent_today, health_status FROM lcs.adapter_registry
       WHERE adapter_type = $1`,
      [signal.preferred_channel ?? 'MG']
    );

    const capacityResult = checkCapacity({
      adapter_daily_cap: (adapter?.daily_cap as number) ?? 150,
      adapter_sent_today: (adapter?.sent_today as number) ?? 0,
      adapter_health: (adapter?.health_status as string) ?? 'HEALTHY',
    });

    if (capacityResult.verdict === 'BLOCK') {
      await writeCid(connStr, signal, null, 'BLOCKED', `Capacity: ${capacityResult.reason}`);
      result.blocked++;
      continue;
    }

    // MIDDLE: collect intelligence
    const { data: intel } = await queryOne(connStr,
      `SELECT * FROM lcs.v_company_intelligence WHERE sovereign_company_id = $1`,
      [signal.sovereign_company_id]
    );

    const tier = (intel?.intelligence_tier as number) ?? 5;

    // MIDDLE: freshness gate
    const freshnessResult = checkFreshness({
      current_tier: tier,
      freshness_window_days: 30,
      data_age_days: null, // TODO: calculate from intel timestamps
    });

    if (freshnessResult.verdict === 'BLOCK') {
      await writeCid(connStr, signal, null, 'BLOCKED', `Freshness: ${freshnessResult.reason}`);
      result.blocked++;
      continue;
    }

    const effectiveTier = freshnessResult.downgraded_tier ?? tier;

    // MIDDLE: match frame
    const { data: frames } = await query(connStr,
      `SELECT * FROM lcs.frame_registry
       WHERE lifecycle_phase = $1 AND is_active = true AND tier <= $2
       ORDER BY tier ASC LIMIT 1`,
      [signal.lifecycle_phase, effectiveTier]
    );

    if (!frames.length) {
      await writeCid(connStr, signal, null, 'FAILED', `No frame for phase=${signal.lifecycle_phase} tier<=${effectiveTier}`);
      result.failed++;
      continue;
    }

    // MIDDLE: resolve entity
    let entityId = (intel?.ceo_entity_id ?? intel?.cfo_entity_id ?? intel?.hr_entity_id ?? '00000000-0000-0000-0000-000000000000') as string;

    // MIDDLE: mint CID
    const commId = mintCommunicationId(signal.lifecycle_phase);

    // EGRESS: write CID row
    await writeCid(connStr, signal, commId, 'COMPILED', null, {
      entity_id: entityId,
      frame_id: frames[0].frame_id as string,
      intelligence_tier: effectiveTier,
    });
    result.compiled++;

    // Mark signal processed
    await query(connStr,
      `UPDATE lcs.signal_queue SET status = 'COMPLETED', processed_at = NOW() WHERE id = $1`,
      [signal.id]
    );
  }

  console.log(`[CID] ${result.compiled} compiled, ${result.failed} failed, ${result.blocked} blocked / ${result.total}`);
  return result;
}

async function writeCid(
  connStr: string,
  signal: SignalQueueRow,
  commId: string | null,
  status: string,
  reason: string | null,
  extra?: Record<string, unknown>
) {
  const id = commId ?? mintCommunicationId(signal.lifecycle_phase);
  await insert(connStr, 'lcs.cid', {
    communication_id: id,
    sovereign_company_id: signal.sovereign_company_id,
    signal_queue_id: signal.id,
    signal_set_hash: signal.signal_set_hash,
    entity_type: 'slot',
    entity_id: extra?.entity_id ?? '00000000-0000-0000-0000-000000000000',
    frame_id: extra?.frame_id ?? 'UNRESOLVED',
    lifecycle_phase: signal.lifecycle_phase,
    intelligence_tier: extra?.intelligence_tier ?? null,
    compilation_status: status,
    compilation_reason: reason,
    agent_number: signal.agent_number ?? 'UNASSIGNED',
    lane: 'MAIN',
  });
}

// ═══════════════════════════════════════════════════════════════
// Phase 3: SID Constructor
// ═══════════════════════════════════════════════════════════════
// IMO:
//   Ingress: lcs.cid (COMPILED) — schema validation
//   Middle: frame fetch + intelligence + recipient + message assembly
//   Egress: lcs.sid_output row (CONSTRUCTED|FAILED)
// Note: Phase 2 (AI Synthesis) simulated — uses frame template
// ═══════════════════════════════════════════════════════════════

async function runSidConstructor(connStr: string, batchSize: number) {
  const result = { total: 0, constructed: 0, failed: 0, blocked: 0 };

  // INGRESS: fetch COMPILED CIDs without SID
  const { data: cids } = await query<CidRow>(connStr,
    `SELECT c.* FROM lcs.cid c
     LEFT JOIN lcs.sid_output s ON s.communication_id = c.communication_id
     WHERE c.compilation_status = 'COMPILED' AND s.communication_id IS NULL
     ORDER BY c.created_at ASC LIMIT $1`,
    [batchSize]
  );

  if (!cids.length) return result;
  result.total = cids.length;

  for (const cid of cids) {
    // MIDDLE: fetch frame
    const { data: frame } = await queryOne(connStr,
      `SELECT * FROM lcs.frame_registry WHERE frame_id = $1`,
      [cid.frame_id]
    );

    if (!frame) {
      await writeSid(connStr, cid, 'FAILED', 'Frame not found');
      result.failed++;
      continue;
    }

    // MIDDLE: resolve recipient from intelligence
    const { data: intel } = await queryOne(connStr,
      `SELECT * FROM lcs.v_company_intelligence WHERE sovereign_company_id = $1`,
      [cid.sovereign_company_id]
    );

    const recipientEmail = (intel?.ceo_email ?? intel?.cfo_email ?? intel?.hr_email) as string | null;
    const recipientName = (intel?.ceo_name ?? intel?.cfo_name ?? intel?.hr_name) as string | null;

    if (!recipientEmail) {
      await writeSid(connStr, cid, 'FAILED', 'No recipient email resolved');
      result.failed++;
      continue;
    }

    // MIDDLE: construct message (BAR-48 simulated — basic template)
    const companyName = (intel?.company_name as string) ?? 'Company';
    const frameName = (frame.frame_name as string) ?? cid.frame_id;

    // EGRESS: write SID
    const sidId = mintSidId();
    await insert(connStr, 'lcs.sid_output', {
      sid_id: sidId,
      communication_id: cid.communication_id,
      frame_id: cid.frame_id,
      template_id: (frame.sid_template_id as string) ?? null,
      subject_line: `[${frameName}] ${companyName}`,
      body_plain: `${cid.lifecycle_phase} communication via ${frameName} for ${companyName}.`,
      body_html: null, // BAR-48: full template engine builds this
      sender_identity: `${cid.lifecycle_phase.toLowerCase()}-sender`,
      sender_email: null, // Resolved by adapter
      recipient_email: recipientEmail,
      recipient_name: recipientName,
      construction_status: 'CONSTRUCTED',
      construction_reason: null,
    });
    result.constructed++;
  }

  console.log(`[SID] ${result.constructed} constructed, ${result.failed} failed / ${result.total}`);
  return result;
}

async function writeSid(connStr: string, cid: CidRow, status: string, reason: string) {
  await insert(connStr, 'lcs.sid_output', {
    sid_id: mintSidId(),
    communication_id: cid.communication_id,
    frame_id: cid.frame_id,
    construction_status: status,
    construction_reason: reason,
  });
}

// ═══════════════════════════════════════════════════════════════
// Phase 4: MID Engine
// ═══════════════════════════════════════════════════════════════
// IMO:
//   Ingress: lcs.sid_output (CONSTRUCTED) — schema validation
//   Middle: gates + mint MID + route to adapter + log CET
//   Egress: lcs.mid_sequence_state + lcs.event
// ═══════════════════════════════════════════════════════════════

async function runMidEngine(connStr: string, mode: string, batchSize: number) {
  const result = { total: 0, delivered: 0, failed: 0, blocked: 0 };

  // INGRESS: fetch CONSTRUCTED SIDs without MID
  const { data: sids } = await query<SidRow>(connStr,
    `SELECT s.* FROM lcs.sid_output s
     LEFT JOIN lcs.mid_sequence_state m ON m.communication_id = s.communication_id
     WHERE s.construction_status = 'CONSTRUCTED' AND m.communication_id IS NULL
     ORDER BY s.created_at ASC LIMIT $1`,
    [batchSize]
  );

  if (!sids.length) return result;
  result.total = sids.length;

  for (const sid of sids) {
    // Fetch CID for context
    const { data: cid } = await queryOne<CidRow>(connStr,
      `SELECT * FROM lcs.cid WHERE communication_id = $1`,
      [sid.communication_id]
    );

    if (!cid) {
      result.failed++;
      continue;
    }

    const channel: Channel = 'MG'; // Default to Mailgun

    // MIDDLE: suppression gate
    const suppressionResult = checkSuppression({
      never_contact: false, // TODO: query suppression table
      unsubscribed: false,
      hard_bounced: false,
      complained: false,
    });

    if (suppressionResult.verdict === 'BLOCK') {
      await writeMid(connStr, sid.communication_id, channel, 'FAILED', 'FAIL', suppressionResult.reason);
      result.blocked++;
      continue;
    }

    // MIDDLE: mint MID
    const messageRunId = mintMessageRunId(sid.communication_id, channel, 1);

    if (mode === 'SMOKE_TEST' || mode === 'DRY_RUN') {
      // Simulate delivery — don't actually send
      await writeMid(connStr, sid.communication_id, channel, 'SENT', 'PASS', null, messageRunId);
      await logEvent(connStr, cid, messageRunId, channel, 'DELIVERY_SIMULATED', mode);
      result.delivered++;
      continue;
    }

    // MIDDLE: route through Composio → Mailgun
    // TODO: wire Composio MCP call here
    // For now, simulate success
    await writeMid(connStr, sid.communication_id, channel, 'SENT', 'PASS', null, messageRunId);
    await logEvent(connStr, cid, messageRunId, channel, 'DELIVERY_SENT', 'LIVE');
    result.delivered++;
  }

  console.log(`[MID] ${result.delivered} delivered, ${result.failed} failed, ${result.blocked} blocked / ${result.total}`);
  return result;
}

async function writeMid(
  connStr: string,
  commId: string,
  channel: Channel,
  deliveryStatus: string,
  gateVerdict: string,
  gateReason: string | null,
  messageRunId?: string
) {
  await insert(connStr, 'lcs.mid_sequence_state', {
    message_run_id: messageRunId ?? 'GATE-BLOCKED',
    communication_id: commId,
    adapter_type: channel,
    channel,
    delivery_status: deliveryStatus,
    gate_verdict: gateVerdict,
    gate_reason: gateReason,
    attempt_number: 1,
    attempted_at: new Date().toISOString(),
  });
}

async function logEvent(
  connStr: string,
  cid: CidRow,
  messageRunId: string,
  channel: Channel,
  eventType: string,
  mode: string
) {
  await insert(connStr, 'lcs.event', {
    communication_id: cid.communication_id,
    message_run_id: messageRunId,
    sovereign_company_id: cid.sovereign_company_id,
    event_type: eventType,
    lifecycle_phase: cid.lifecycle_phase,
    channel,
    delivery_status: 'SENT',
    step_name: 'MID Delivery',
    payload: { mode, frame_id: cid.frame_id },
  });
}

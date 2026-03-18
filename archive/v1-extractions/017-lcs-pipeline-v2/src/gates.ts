// ═══════════════════════════════════════════════════════════════
// Gates — Tier 0 constant filters
// ═══════════════════════════════════════════════════════════════
// Authority: Tier 0 §Gate Mechanism — each gate produces one locked constant
// These are deterministic. No LLM. No AI. Pure logic.
// ═══════════════════════════════════════════════════════════════

export type GateVerdict = 'PASS' | 'BLOCK' | 'DOWNGRADE';

export interface GateResult {
  verdict: GateVerdict;
  reason: string | null;
  downgraded_tier?: number;
}

// ── Capacity Gate ────────────────────────────────────────────
// Checks: adapter daily cap, agent daily cap, adapter health
export function checkCapacity(ctx: {
  adapter_daily_cap: number;
  adapter_sent_today: number;
  adapter_health: string;
}): GateResult {
  if (ctx.adapter_health !== 'HEALTHY') {
    return { verdict: 'BLOCK', reason: `Adapter unhealthy: ${ctx.adapter_health}` };
  }
  if (ctx.adapter_sent_today >= ctx.adapter_daily_cap) {
    return { verdict: 'BLOCK', reason: `Adapter at capacity: ${ctx.adapter_sent_today}/${ctx.adapter_daily_cap}` };
  }
  return { verdict: 'PASS', reason: null };
}

// ── Freshness Gate ───────────────────────────────────────────
// Checks: data recency across intelligence layers
export function checkFreshness(ctx: {
  current_tier: number;
  freshness_window_days: number;
  data_age_days: number | null;
}): GateResult {
  if (ctx.data_age_days === null) {
    return { verdict: 'PASS', reason: 'No data age available — pass with default tier' };
  }
  if (ctx.data_age_days > ctx.freshness_window_days * 2) {
    return { verdict: 'BLOCK', reason: `Data too stale: ${ctx.data_age_days} days old` };
  }
  if (ctx.data_age_days > ctx.freshness_window_days) {
    return {
      verdict: 'DOWNGRADE',
      reason: `Data aging: ${ctx.data_age_days} days — tier downgraded`,
      downgraded_tier: Math.min(ctx.current_tier + 1, 5),
    };
  }
  return { verdict: 'PASS', reason: null };
}

// ── Suppression Gate ─────────────────────────────────────────
// Checks: never_contact, unsubscribed, hard_bounced, complained
// This is where the Circle's TRAIN output lives — hard bounces
// update the suppression list, and this gate reads it.
export function checkSuppression(ctx: {
  never_contact: boolean;
  unsubscribed: boolean;
  hard_bounced: boolean;
  complained: boolean;
}): GateResult {
  if (ctx.never_contact) {
    return { verdict: 'BLOCK', reason: 'Entity flagged never_contact' };
  }
  if (ctx.unsubscribed) {
    return { verdict: 'BLOCK', reason: 'Entity unsubscribed' };
  }
  if (ctx.hard_bounced) {
    return { verdict: 'BLOCK', reason: 'Entity hard_bounced — suppression from ORBT TRAIN' };
  }
  if (ctx.complained) {
    return { verdict: 'BLOCK', reason: 'Entity complained' };
  }
  return { verdict: 'PASS', reason: null };
}

// ═══════════════════════════════════════════════════════════════
// LCS Hub — Utilities
// ═══════════════════════════════════════════════════════════════

/** Generate a ULID-like ID with prefix */
export function mintId(prefix: string): string {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const rand = crypto.randomUUID().replace(/-/g, '').slice(0, 12);
  return `${prefix}-${date}-${rand}`;
}

/** Log an event to the CET (append-only) */
export async function logEvent(
  d1: D1Database,
  params: {
    sovereign_company_id: string;
    cid_id?: string;
    sid_id?: string;
    mid_id?: string;
    event_type: string;
    event_data?: Record<string, unknown>;
  },
): Promise<void> {
  await d1.prepare(`
    INSERT INTO event (event_id, sovereign_company_id, cid_id, sid_id, mid_id, event_type, event_data)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    mintId('EVT'),
    params.sovereign_company_id,
    params.cid_id ?? null,
    params.sid_id ?? null,
    params.mid_id ?? null,
    params.event_type,
    params.event_data ? JSON.stringify(params.event_data) : null,
  ).run();
}

/** Log an error to err0 (the drain) */
export async function logError(
  d1: D1Database,
  params: {
    sovereign_company_id?: string;
    cid_id?: string;
    sid_id?: string;
    mid_id?: string;
    stage: string;
    error_type: string;
    error_message: string;
    error_detail?: Record<string, unknown>;
    strike_count?: number;
  },
): Promise<void> {
  await d1.prepare(`
    INSERT INTO err0 (error_id, sovereign_company_id, cid_id, sid_id, mid_id, stage, error_type, error_message, error_detail, strike_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    mintId('ERR'),
    params.sovereign_company_id ?? null,
    params.cid_id ?? null,
    params.sid_id ?? null,
    params.mid_id ?? null,
    params.stage,
    params.error_type,
    params.error_message,
    params.error_detail ? JSON.stringify(params.error_detail) : null,
    params.strike_count ?? 0,
  ).run();
}

/** Check suppression list */
export async function isSuppressed(
  d1: D1Database,
  entityType: string,
  entityValue: string,
): Promise<boolean> {
  const row = await d1.prepare(
    'SELECT 1 FROM suppression WHERE entity_type = ? AND entity_value = ?'
  ).bind(entityType, entityValue).first();
  return row !== null;
}

/** Add to suppression list */
export async function suppress(
  d1: D1Database,
  params: {
    sovereign_company_id?: string;
    entity_type: string;
    entity_value: string;
    reason: string;
  },
): Promise<void> {
  await d1.prepare(`
    INSERT OR IGNORE INTO suppression (suppression_id, sovereign_company_id, entity_type, entity_value, reason)
    VALUES (?, ?, ?, ?, ?)
  `).bind(
    mintId('SUP'),
    params.sovereign_company_id ?? null,
    params.entity_type,
    params.entity_value,
    params.reason,
  ).run();
}

// ═══════════════════════════════════════════════════════════════
// Spoke IN: Signal Intake
// ═══════════════════════════════════════════════════════════════
// Receives signals from dumb workers in standard format.
// Validates schema. Writes to signal_queue. That's it.
// Hub doesn't care which worker produced the signal.
// ═══════════════════════════════════════════════════════════════

import type { Signal } from '../types';
import { mintId, logEvent, logError } from '../utils';

/** Validate incoming signal has required fields */
function validateSignal(body: Record<string, unknown>): Signal | null {
  if (!body.sovereign_company_id || typeof body.sovereign_company_id !== 'string') return null;
  if (!body.worker || typeof body.worker !== 'string') return null;
  if (!body.signal_type || typeof body.signal_type !== 'string') return null;

  return {
    signal_id: mintId('SIG'),
    sovereign_company_id: body.sovereign_company_id as string,
    worker: body.worker as Signal['worker'],
    signal_type: body.signal_type as string,
    magnitude: typeof body.magnitude === 'number' ? body.magnitude : null,
    expires_at: typeof body.expires_at === 'string' ? body.expires_at : null,
    raw_payload: (body.raw_payload as Record<string, unknown>) ?? {},
  };
}

/** Ingest a signal from a dumb worker spoke */
export async function ingestSignal(
  d1: D1Database,
  body: Record<string, unknown>,
): Promise<{ signal_id: string } | { error: string }> {
  const signal = validateSignal(body);
  if (!signal) {
    return { error: 'Invalid signal: requires sovereign_company_id, worker, signal_type' };
  }

  try {
    await d1.prepare(`
      INSERT INTO signal_queue (signal_id, sovereign_company_id, worker, signal_type, magnitude, expires_at, raw_payload, status)
      VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    `).bind(
      signal.signal_id,
      signal.sovereign_company_id,
      signal.worker,
      signal.signal_type,
      signal.magnitude,
      signal.expires_at,
      JSON.stringify(signal.raw_payload),
    ).run();

    await logEvent(d1, {
      sovereign_company_id: signal.sovereign_company_id,
      event_type: 'signal_received',
      event_data: {
        signal_id: signal.signal_id,
        worker: signal.worker,
        signal_type: signal.signal_type,
        magnitude: signal.magnitude,
      },
    });

    return { signal_id: signal.signal_id };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logError(d1, {
      sovereign_company_id: signal.sovereign_company_id,
      stage: 'signal',
      error_type: 'ingest_failure',
      error_message: msg,
      error_detail: { signal },
    });
    return { error: msg };
  }
}

/** Batch ingest multiple signals */
export async function ingestSignalBatch(
  d1: D1Database,
  signals: Record<string, unknown>[],
): Promise<{ ingested: number; errors: number }> {
  let ingested = 0;
  let errors = 0;

  for (const body of signals) {
    const result = await ingestSignal(d1, body);
    if ('signal_id' in result) {
      ingested++;
    } else {
      errors++;
    }
  }

  return { ingested, errors };
}

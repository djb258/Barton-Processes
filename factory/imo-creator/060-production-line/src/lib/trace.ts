// Execution Trace Writer — §11 append-only build journal (NOT the logbook)
import type { AdapterResponse } from '../types';

export async function writeTraceEntry(
  db: D1Database,
  entry: {
    run_id: string;
    goal_id: string;
    step_id?: string;
    station_id?: string;
    step_description: string;
    target?: string;
    actual?: string;
    delta?: string;
    status: 'done' | 'failed' | 'skipped' | 'not-callable';
    error_code?: string;
    error_message?: string;
    tools_used?: string[];
    duration_ms?: number;
    cost_cents?: number;
    signed_by: string;
  },
): Promise<void> {
  await db.prepare(`
    INSERT INTO execution_trace (trace_id, run_id, goal_id, step_id, station_id, step_description, target, actual, delta, status, error_code, error_message, tools_used, duration_ms, cost_cents, signed_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    crypto.randomUUID(),
    entry.run_id,
    entry.goal_id,
    entry.step_id ?? null,
    entry.station_id ?? null,
    entry.step_description,
    entry.target ?? null,
    entry.actual ?? null,
    entry.delta ?? null,
    entry.status,
    entry.error_code ?? null,
    entry.error_message ?? null,
    JSON.stringify(entry.tools_used ?? []),
    entry.duration_ms ?? null,
    entry.cost_cents ?? 0,
    entry.signed_by,
  ).run();
}

export function traceFromAdapterResponse(
  run_id: string,
  goal_id: string,
  step_id: string,
  station_id: string,
  response: AdapterResponse,
  signed_by: string,
): Parameters<typeof writeTraceEntry>[1] {
  return {
    run_id,
    goal_id,
    step_id,
    station_id,
    step_description: `Station ${station_id} execution`,
    target: 'success: true',
    actual: `success: ${response.success}`,
    delta: response.success ? 'on target' : `FAILED: ${response.error?.code}`,
    status: response.success ? 'done' : (response.error?.code === 'NOT_CALLABLE' ? 'not-callable' : 'failed'),
    error_code: response.error?.code,
    error_message: response.error?.message,
    tools_used: response.metrics.tools_used,
    duration_ms: response.metrics.duration_ms,
    cost_cents: response.metrics.cost_cents,
    signed_by,
  };
}

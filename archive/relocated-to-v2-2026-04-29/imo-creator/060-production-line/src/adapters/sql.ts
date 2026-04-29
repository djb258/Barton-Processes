// SQL Adapter — runs D1 queries for view-based stations
import type { AdapterRequest, AdapterResponse } from '../types';

export async function callSqlStation(
  query: string,
  stationId: string,
  request: AdapterRequest,
  db: D1Database,
): Promise<AdapterResponse> {
  const start = Date.now();

  try {
    const result = await db.prepare(query).bind(request.workpiece_id).all();
    const duration_ms = Date.now() - start;

    return {
      success: true,
      station_id: stationId,
      result: { rows: result.results, count: result.results.length },
      error: null,
      metrics: { duration_ms, cost_cents: 0, tools_used: [], transport: 'sql' },
      timestamp: new Date().toISOString(),
    };
  } catch (e: any) {
    return {
      success: false,
      station_id: stationId,
      result: null,
      error: {
        code: 'INTERNAL',
        message: `D1 query failed: ${e.message}`,
        retryable: false,
      },
      metrics: { duration_ms: Date.now() - start, cost_cents: 0, tools_used: [], transport: 'sql' },
      timestamp: new Date().toISOString(),
    };
  }
}

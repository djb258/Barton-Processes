// Manual Adapter — for not-yet-built stations. Logs NOT_CALLABLE.
import type { AdapterRequest, AdapterResponse } from '../types';

export async function callManualStation(
  stationId: string,
  request: AdapterRequest,
): Promise<AdapterResponse> {
  return {
    success: false,
    station_id: stationId,
    result: null,
    error: {
      code: 'NOT_CALLABLE',
      message: `Station ${stationId} is not yet built or deployed. Requires manual execution.`,
      retryable: false,
    },
    metrics: { duration_ms: 0, cost_cents: 0, tools_used: [], transport: 'manual' },
    timestamp: new Date().toISOString(),
  };
}

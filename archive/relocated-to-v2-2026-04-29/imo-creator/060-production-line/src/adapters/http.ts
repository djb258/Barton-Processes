// HTTP Adapter — calls deployed CF Workers via fetch()
import type { AdapterRequest, AdapterResponse } from '../types';

const TIMEOUT_MS = 120_000;

export async function callHttpStation(
  target: string,
  endpoint: string | undefined,
  request: AdapterRequest,
): Promise<AdapterResponse> {
  const url = endpoint ? `${target}${endpoint}` : target;
  const start = Date.now();

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    clearTimeout(timeout);
    const duration_ms = Date.now() - start;

    if (!res.ok) {
      return {
        success: false,
        station_id: request.context.line,
        result: null,
        error: {
          code: res.status === 429 ? 'RATE_LIMIT' : 'INTERNAL',
          message: `HTTP ${res.status}: ${await res.text()}`,
          retryable: res.status === 429 || res.status >= 500,
        },
        metrics: { duration_ms, cost_cents: 0, tools_used: [], transport: 'http' },
        timestamp: new Date().toISOString(),
      };
    }

    const data = await res.json() as Record<string, unknown>;
    return {
      success: true,
      station_id: String(data.station_id || request.context.line),
      result: data,
      error: null,
      metrics: { duration_ms, cost_cents: 0, tools_used: [], transport: 'http' },
      timestamp: new Date().toISOString(),
    };
  } catch (e: any) {
    return {
      success: false,
      station_id: request.context.line,
      result: null,
      error: {
        code: e.name === 'AbortError' ? 'TIMEOUT' : 'INTERNAL',
        message: e.message,
        retryable: e.name === 'AbortError',
      },
      metrics: { duration_ms: Date.now() - start, cost_cents: 0, tools_used: [], transport: 'http' },
      timestamp: new Date().toISOString(),
    };
  }
}

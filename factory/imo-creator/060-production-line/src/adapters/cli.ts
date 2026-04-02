// CLI Adapter — executes Python scripts via claude-sandbox exec()
import type { AdapterRequest, AdapterResponse } from '../types';

const SANDBOX_URL = 'https://claude-sandbox.svg-outreach.workers.dev';
const TIMEOUT_MS = 300_000; // 5 min for scripts

export async function callCliStation(
  command: string,
  stationId: string,
  request: AdapterRequest,
): Promise<AdapterResponse> {
  const start = Date.now();

  // Build the CLI command with the workpiece_id as argument
  const fullCommand = `${command} --workpiece-id ${request.workpiece_id} --goal-id ${request.goal_id}`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

    const res = await fetch(`${SANDBOX_URL}/exec`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cmd: fullCommand }),
      signal: controller.signal,
    });

    clearTimeout(timeout);
    const duration_ms = Date.now() - start;

    if (!res.ok) {
      return {
        success: false,
        station_id: stationId,
        result: null,
        error: {
          code: 'INTERNAL',
          message: `Sandbox returned ${res.status}: ${await res.text()}`,
          retryable: res.status >= 500,
        },
        metrics: { duration_ms, cost_cents: 0, tools_used: [], transport: 'cli' },
        timestamp: new Date().toISOString(),
      };
    }

    const data = await res.json() as { stdout?: string; stderr?: string; success?: boolean; elapsed_ms?: number };

    if (!data.success) {
      return {
        success: false,
        station_id: stationId,
        result: null,
        error: {
          code: 'INTERNAL',
          message: data.stderr || 'Script execution failed',
          retryable: false,
        },
        metrics: { duration_ms, cost_cents: 0, tools_used: [], transport: 'cli' },
        timestamp: new Date().toISOString(),
      };
    }

    // Try to parse stdout as JSON, fall back to raw string
    let result: Record<string, unknown>;
    try {
      result = JSON.parse(data.stdout || '{}');
    } catch {
      result = { raw_output: data.stdout };
    }

    return {
      success: true,
      station_id: stationId,
      result,
      error: null,
      metrics: { duration_ms, cost_cents: 0, tools_used: [], transport: 'cli' },
      timestamp: new Date().toISOString(),
    };
  } catch (e: any) {
    return {
      success: false,
      station_id: stationId,
      result: null,
      error: {
        code: e.name === 'AbortError' ? 'TIMEOUT' : 'INTERNAL',
        message: e.message,
        retryable: e.name === 'AbortError',
      },
      metrics: { duration_ms: Date.now() - start, cost_cents: 0, tools_used: [], transport: 'cli' },
      timestamp: new Date().toISOString(),
    };
  }
}

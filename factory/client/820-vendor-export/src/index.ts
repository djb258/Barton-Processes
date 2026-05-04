/**
 * Process 820 — Vendor Export
 *
 * CF Worker. Cron-triggered + HTTP.
 * Reads D1 canonical → applies vendor blueprint → generates export files.
 * Daily for TPA/PBM, weekly for carriers.
 */

import { generateExport, type Env } from './export';
import { listBlueprints } from './blueprints';

export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    const dayOfWeek = new Date().getUTCDay(); // 0=Sun, 1=Mon
    const weeklyDay = parseInt(env.WEEKLY_DAY || '1', 10);

    const dailyVendors = (env.DAILY_VENDORS || '').split(',').filter(Boolean);
    const weeklyVendors = (env.WEEKLY_VENDORS || '').split(',').filter(Boolean);

    // Determine which vendors to export today
    const vendors = [...dailyVendors];
    if (dayOfWeek === weeklyDay) {
      vendors.push(...weeklyVendors);
    }

    if (vendors.length === 0) {
      console.log('[820] CRON: No vendors scheduled for today.');
      return;
    }

    // Get active clients from the live client D1 schema.
    const clients = await env.D1.prepare(
      "SELECT client_id FROM clients WHERE COALESCE(orbt_mode, 'OPERATE') NOT IN ('ARCHIVE', 'RETIRED')"
    ).all<{ client_id: string }>();

    if (!clients.results || clients.results.length === 0) {
      console.log('[820] CRON: No active clients.');
      return;
    }

    console.log(`[820] CRON: ${clients.results.length} clients × ${vendors.length} vendors`);

    for (const client of clients.results) {
      for (const vendorId of vendors) {
        try {
          const result = await generateExport(env, client.client_id, vendorId);
          console.log(`[820] CRON: client=${client.client_id} vendor=${vendorId} records=${result.record_count}`);
          // TODO: Ship result.output to destination (R2, email, SFTP, etc.)
        } catch (err) {
          console.error(`[820] CRON ERROR: client=${client.client_id} vendor=${vendorId} — ${err}`);
        }
      }
    }
  },

  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === '/health') {
      return Response.json({
        process: 'PROC-VENDOR-EXPORT', number: 820, status: 'ok',
      });
    }

    // Status — recent exports
    if (url.pathname === '/status') {
      const recent = await env.D1.prepare(
        'SELECT * FROM export_log ORDER BY exported_at DESC LIMIT 20'
      ).all();
      const errorCount = await env.D1.prepare(
        'SELECT COUNT(*) as cnt FROM export_error'
      ).first<{ cnt: number }>();
      const blueprintIds = await listBlueprints(env.KV);

      return Response.json({
        process: 'PROC-VENDOR-EXPORT',
        recent_exports: recent.results,
        total_errors: errorCount?.cnt ?? 0,
        available_blueprints: blueprintIds,
      });
    }

    // Manual export
    if (url.pathname === '/export' && request.method === 'POST') {
      try {
        const body = await request.json<{ client_id?: string; vendor_id?: string }>();
        if (!body.client_id) return Response.json({ error: 'client_id required' }, { status: 400 });
        if (!body.vendor_id) return Response.json({ error: 'vendor_id required' }, { status: 400 });

        const result = await generateExport(env, body.client_id, body.vendor_id);
        return Response.json({ action: 'export', ...result });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return Response.json({ error: msg }, { status: 500 });
      }
    }

    // Export log per client
    if (url.pathname.startsWith('/log/')) {
      const clientId = url.pathname.split('/log/')[1];
      if (!clientId) return Response.json({ error: 'client_id required' }, { status: 400 });

      const logs = await env.D1.prepare(
        'SELECT * FROM export_log WHERE client_id = ? ORDER BY exported_at DESC LIMIT 50'
      ).bind(clientId).all();

      return Response.json({ client_id: clientId, exports: logs.results });
    }

    return new Response([
      'Process 820 — Vendor Export',
      '',
      'GET  /health              — health check',
      'GET  /status              — recent exports + blueprint list',
      'POST /export              — { client_id, vendor_id } → manual export',
      'GET  /log/:client_id      — export history',
    ].join('\n'), { status: 200 });
  },
};

/**
 * Process 800 — Client Mint
 *
 * CF Worker. Manual trigger only.
 * Single-tier model (2026-05-12): svg-d1-client.clients is canonical.
 * Receives CL sovereign ID → reads cl.company_identity (READ ONLY) →
 * mints client record in D1 clients table. No vault promotion.
 *
 * Routes:
 *   GET  /health          — health check
 *   GET  /status          — client counts (clients + clients_error)
 *   POST /mint            — { sovereign_id } → mint new client
 *   GET  /client/:id      — lookup by client_id
 */

import { mintClient, type Env } from './mint';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const { pathname, method } = url as { pathname: string; method?: string } & URL;

    // Health check
    if (pathname === '/health') {
      return Response.json({
        process: 'bp.800-client-mint',
        model: 'single-tier',
        canonical_store: 'svg-d1-client.clients',
        status: 'ok',
      });
    }

    // Status — counts from canonical tables
    if (pathname === '/status') {
      const [total, onboarding, active, errors] = await Promise.all([
        env.D1.prepare('SELECT COUNT(*) as cnt FROM clients').first<{ cnt: number }>(),
        env.D1.prepare("SELECT COUNT(*) as cnt FROM clients WHERE lifecycle_stage = 'onboarding'").first<{ cnt: number }>(),
        env.D1.prepare("SELECT COUNT(*) as cnt FROM clients WHERE lifecycle_stage = 'active'").first<{ cnt: number }>(),
        env.D1.prepare('SELECT COUNT(*) as cnt FROM clients_error').first<{ cnt: number }>(),
      ]);

      return Response.json({
        process: 'bp.800-client-mint',
        model: 'single-tier',
        clients: {
          total: total?.cnt ?? 0,
          onboarding: onboarding?.cnt ?? 0,
          active: active?.cnt ?? 0,
        },
        errors_total: errors?.cnt ?? 0,
      });
    }

    // POST /mint — mint new client from sovereign ID
    if (pathname === '/mint' && request.method === 'POST') {
      try {
        const body = await request.json<{ sovereign_id?: string }>();
        if (!body.sovereign_id) {
          return Response.json({ error: 'sovereign_id is required' }, { status: 400 });
        }
        const result = await mintClient(env, body.sovereign_id);
        const status = result.status === 'minted' ? 201 : 409;
        return Response.json(result, { status });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return Response.json({ error: msg }, { status: 500 });
      }
    }

    // /vault — removed (single-tier model, no vault promotion)
    if (pathname === '/vault') {
      return Response.json(
        {
          error: 'Gone',
          reason: 'Single-tier model (2026-05-12) — no vault promotion endpoint. svg-d1-client.clients is canonical.',
        },
        { status: 410 }
      );
    }

    // GET /client/:id — lookup by client_id
    if (pathname.startsWith('/client/')) {
      const clientId = pathname.slice('/client/'.length);
      if (!clientId) return Response.json({ error: 'client_id required' }, { status: 400 });

      const client = await env.D1.prepare(
        'SELECT * FROM clients WHERE client_id = ?'
      ).bind(clientId).first();
      if (!client) return Response.json({ error: 'not found' }, { status: 404 });
      return Response.json(client);
    }

    return new Response(
      [
        'bp.800 — Client Mint (single-tier model)',
        '',
        'GET  /health          — health check',
        'GET  /status          — client counts from svg-d1-client.clients',
        'POST /mint            — { sovereign_id } → mint new client',
        'GET  /client/:id      — lookup by client_id',
        '',
        '/vault has been removed (single-tier model, 2026-05-12)',
      ].join('\n'),
      { status: 200 }
    );
  },
};

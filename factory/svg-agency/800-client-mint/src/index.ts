/**
 * Process 800 — Client Mint
 *
 * CF Worker. Manual trigger only.
 * Receives CL sovereign ID → reads Neon CL → mints client_id in D1 → vaults to Neon.
 */

import { mintClient, type Env } from './mint';
import { vaultClients } from './vault';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === '/health') {
      return Response.json({
        process: 'PROC-CLIENT-MINT', number: 800, status: 'ok',
      });
    }

    // Status — D1 client counts
    if (url.pathname === '/status') {
      const total = await env.D1.prepare('SELECT COUNT(*) as cnt FROM client').first<{ cnt: number }>();
      const vaulted = await env.D1.prepare('SELECT COUNT(*) as cnt FROM client WHERE vaulted_at IS NOT NULL').first<{ cnt: number }>();
      const unvaulted = await env.D1.prepare('SELECT COUNT(*) as cnt FROM client WHERE vaulted_at IS NULL').first<{ cnt: number }>();
      const errors = await env.D1.prepare("SELECT COUNT(*) as cnt FROM client_error WHERE status = 'open'").first<{ cnt: number }>();

      return Response.json({
        process: 'PROC-CLIENT-MINT',
        clients: { total: total?.cnt ?? 0, vaulted: vaulted?.cnt ?? 0, unvaulted: unvaulted?.cnt ?? 0 },
        open_errors: errors?.cnt ?? 0,
      });
    }

    // Mint new client from sovereign ID
    if (url.pathname === '/mint' && request.method === 'POST') {
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

    // Vault all unvaulted clients to Neon
    if (url.pathname === '/vault' && request.method === 'POST') {
      try {
        const result = await vaultClients(env);
        return Response.json({ action: 'vault', ...result });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return Response.json({ error: msg }, { status: 500 });
      }
    }

    // Lookup client by ID
    if (url.pathname.startsWith('/client/')) {
      const clientId = url.pathname.split('/client/')[1];
      if (!clientId) return Response.json({ error: 'client_id required' }, { status: 400 });

      const client = await env.D1.prepare('SELECT * FROM client WHERE client_id = ?').bind(clientId).first();
      if (!client) return Response.json({ error: 'not found' }, { status: 404 });
      return Response.json(client);
    }

    return new Response([
      'Process 800 — Client Mint',
      '',
      'GET  /health          — health check',
      'GET  /status          — client counts',
      'POST /mint            — { sovereign_id } → mint new client',
      'POST /vault           — promote unvaulted to Neon',
      'GET  /client/:id      — lookup by client_id',
    ].join('\n'), { status: 200 });
  },
};

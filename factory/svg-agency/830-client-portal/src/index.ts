/**
 * Process 830 — Client Portal
 *
 * CF Worker. Path-based routing: app.svgagency.com/:slug/:page
 * 5 pages: renewal, ceo, hr, underwriting, agent.
 * All read-only except agent (ticket status updates).
 * Shared D1 with 810 (client-intake).
 */

import { resolveClient } from './resolve';
import { renderPage } from './templates/layout';
import { renderRenewal } from './pages/renewal';
import { renderCeo } from './pages/ceo';
import { renderHr } from './pages/hr';
import { renderUnderwriting } from './pages/underwriting';
import { renderAgent, updateTicketStatus } from './pages/agent';

interface Env {
  D1: D1Database;
}

const PAGE_TITLES: Record<string, string> = {
  renewal: 'Renewal',
  ceo: 'CEO Dashboard',
  hr: 'HR Portal',
  underwriting: 'Underwriting',
  agent: 'Service Dashboard',
};

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';
    const segments = path.split('/').filter(Boolean);

    // Health check
    if (path === '/health') {
      return Response.json({ process: 'PROC-CLIENT-PORTAL', number: 830, status: 'ok' });
    }

    // Root — list instructions
    if (segments.length === 0) {
      return new Response([
        'Process 830 — Client Portal',
        '',
        'GET  /health                              — health check',
        'GET  /:slug/renewal                       — renewal page',
        'GET  /:slug/ceo                           — CEO dashboard',
        'GET  /:slug/hr                            — HR portal',
        'GET  /:slug/underwriting                  — underwriting census',
        'GET  /:slug/agent                         — service agent dashboard',
        'POST /:slug/agent/ticket/:id/status       — update ticket status',
      ].join('\n'), { status: 200 });
    }

    // POST — ticket status update: /:slug/agent/ticket/:id/status
    if (request.method === 'POST' && segments.length === 5 &&
        segments[1] === 'agent' && segments[2] === 'ticket' && segments[4] === 'status') {
      const slug = segments[0];
      const ticketId = segments[3];

      const client = await resolveClient(env.D1, slug);
      if (!client) return Response.json({ error: 'Client not found' }, { status: 404 });

      try {
        const body = await request.json<{ status?: string }>();
        if (!body.status) return Response.json({ error: 'status required' }, { status: 400 });

        const result = await updateTicketStatus(env.D1, client.client_id, ticketId, body.status);
        return Response.json(result, { status: result.success ? 200 : 400 });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return Response.json({ error: msg }, { status: 500 });
      }
    }

    // GET — page rendering: /:slug/:page
    if (segments.length !== 2) {
      return new Response('Not Found', { status: 404 });
    }

    const [slug, page] = segments;

    if (!PAGE_TITLES[page]) {
      return new Response('Not Found — valid pages: renewal, ceo, hr, underwriting, agent', { status: 404 });
    }

    const client = await resolveClient(env.D1, slug);
    if (!client) {
      return new Response('Client not found', { status: 404 });
    }

    try {
      let bodyHtml: string;

      switch (page) {
        case 'renewal':
          bodyHtml = await renderRenewal(env.D1, client.client_id);
          break;
        case 'ceo':
          bodyHtml = await renderCeo(env.D1, client.client_id);
          break;
        case 'hr':
          bodyHtml = await renderHr(env.D1, client.client_id);
          break;
        case 'underwriting':
          bodyHtml = await renderUnderwriting(env.D1, client.client_id);
          break;
        case 'agent':
          bodyHtml = await renderAgent(env.D1, client.client_id, slug);
          break;
        default:
          return new Response('Not Found', { status: 404 });
      }

      const html = renderPage(client, page, PAGE_TITLES[page], bodyHtml);
      return new Response(html, {
        status: 200,
        headers: { 'Content-Type': 'text/html;charset=utf-8' },
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[830] ERROR: slug=${slug} page=${page} — ${msg}`);
      return new Response(`Server Error: ${msg}`, { status: 500 });
    }
  },
};

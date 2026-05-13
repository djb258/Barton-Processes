/**
 * Process 830 — Client Portal
 *
 * CF Worker. Path-based routing: /:slug/:page
 * 6 pages: ceo, renewal, hr, underwriting, employee, agent.
 * Read-only except:
 *   POST /:slug/agent/ticket/:id/status  — update client_tickets.status
 *   POST /:slug/employee/ticket          — insert client_tickets
 */

import { resolveClient } from './resolve';
import { renderPage } from './templates/layout';
import { renderCeo } from './pages/ceo';
import { renderHr } from './pages/hr';
import { renderRenewal } from './pages/renewal';
import { renderUnderwriting } from './pages/underwriting';
import { renderAgent, updateTicketStatus } from './pages/agent';
import { renderEmployee, submitTicket } from './pages/employee';

interface Env {
  D1: D1Database;
}

const PAGE_TITLES: Record<string, string> = {
  ceo: 'Overview',
  renewal: 'Renewal',
  hr: 'HR Portal',
  underwriting: 'Underwriting',
  employee: 'Employee Portal',
  agent: 'Agent Dashboard',
};

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';
    const segments = path.split('/').filter(Boolean);
    const method = request.method.toUpperCase();

    // ── Health check ────────────────────────────────────────────────────────
    if (path === '/health') {
      return Response.json({ process: 'bp.830', number: 830, status: 'ok', ts: new Date().toISOString() });
    }

    // ── Root — usage ────────────────────────────────────────────────────────
    if (segments.length === 0) {
      return new Response([
        'bp.830 — Client Portal',
        '',
        'GET  /health',
        'GET  /:slug/ceo',
        'GET  /:slug/renewal',
        'GET  /:slug/hr',
        'GET  /:slug/underwriting',
        'GET  /:slug/employee',
        'GET  /:slug/agent',
        'POST /:slug/agent/ticket/:id/status',
        'POST /:slug/employee/ticket',
      ].join('\n'), { status: 200, headers: { 'Content-Type': 'text/plain' } });
    }

    // ── POST: agent ticket status update ─────────────────────────────────────
    // Pattern: /:slug/agent/ticket/:id/status   (5 segments)
    if (method === 'POST' &&
        segments.length === 5 &&
        segments[1] === 'agent' &&
        segments[2] === 'ticket' &&
        segments[4] === 'status') {
      const [slug, , , ticketId] = segments;

      const client = await resolveClient(env.D1, slug);
      if (!client) return Response.json({ error: 'Client not found' }, { status: 404 });

      try {
        const body = await request.json<{ status?: string }>();
        if (!body.status) return Response.json({ error: 'status required' }, { status: 400 });

        const result = await updateTicketStatus(env.D1, client.client_id, ticketId, body.status);
        return Response.json(result, { status: result.success ? 200 : 400 });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        console.error(`[830] ticket-status error slug=${slug} ticket=${ticketId}: ${msg}`);
        return Response.json({ error: msg }, { status: 500 });
      }
    }

    // ── POST: employee ticket submission ─────────────────────────────────────
    // Pattern: /:slug/employee/ticket   (3 segments)
    if (method === 'POST' &&
        segments.length === 3 &&
        segments[1] === 'employee' &&
        segments[2] === 'ticket') {
      const slug = segments[0];

      const client = await resolveClient(env.D1, slug);
      if (!client) return new Response('Client not found', { status: 404 });

      let formData: Record<string, string> = {};
      try {
        const ct = request.headers.get('content-type') ?? '';
        if (ct.includes('application/x-www-form-urlencoded')) {
          const text = await request.text();
          for (const pair of text.split('&')) {
            const [k, v] = pair.split('=').map(decodeURIComponent);
            if (k) formData[k] = v ?? '';
          }
        } else if (ct.includes('application/json')) {
          formData = await request.json<Record<string, string>>();
        }
      } catch {
        // fallback — empty formData triggers validation errors
      }

      const result = await submitTicket(env.D1, client.client_id, formData);

      // Re-render the employee page with result (success alert or inline errors)
      const bodyHtml = renderEmployee(client, result);
      const html = renderPage(client, 'employee', PAGE_TITLES['employee'], bodyHtml);
      // On success redirect to avoid re-POST on refresh
      if (result.success) {
        return new Response(null, {
          status: 303,
          headers: { Location: `/${slug}/employee?submitted=1` },
        });
      }
      return new Response(html, {
        status: 422,
        headers: { 'Content-Type': 'text/html;charset=utf-8' },
      });
    }

    // ── GET: page rendering /:slug/:page ─────────────────────────────────────
    // Special case: employee?submitted=1 shows success alert
    if (method === 'GET' && segments.length === 2) {
      const [slug, page] = segments;

      if (!PAGE_TITLES[page]) {
        return new Response('Not Found — valid pages: ' + Object.keys(PAGE_TITLES).join(', '), { status: 404 });
      }

      const client = await resolveClient(env.D1, slug);
      if (!client) return new Response('Client not found', { status: 404 });

      try {
        let bodyHtml: string;

        switch (page) {
          case 'ceo':
            bodyHtml = await renderCeo(client, env.D1);
            break;
          case 'renewal':
            bodyHtml = await renderRenewal(client, env.D1);
            break;
          case 'hr':
            bodyHtml = await renderHr(client, env.D1);
            break;
          case 'underwriting':
            bodyHtml = await renderUnderwriting(client, env.D1);
            break;
          case 'employee': {
            const submitted = url.searchParams.get('submitted') === '1';
            bodyHtml = renderEmployee(client, submitted ? { success: true } : undefined);
            break;
          }
          case 'agent':
            bodyHtml = await renderAgent(client, env.D1);
            break;
          default:
            return new Response('Not Found', { status: 404 });
        }

        const html = renderPage(client, page, PAGE_TITLES[page], bodyHtml);
        return new Response(html, {
          status: 200,
          headers: {
            'Content-Type': 'text/html;charset=utf-8',
            'Cache-Control': 'no-store',
          },
        });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        console.error(`[830] ERROR: slug=${slug} page=${page} — ${msg}`);
        return new Response(`Server Error: ${msg}`, { status: 500 });
      }
    }

    return new Response('Not Found', { status: 404 });
  },
};

/**
 * Process 900 — Sales Portal
 *
 * CF Worker. Path-based routing: app.svgagency.com/sales/:slug/:meeting
 * 4 meetings: fact finder (read-write), insurance ed, systems ed, financials.
 * D1 working tables. Neon for outreach data read (Meeting 1 seed).
 */

import { resolveSales } from './resolve';
import { renderPage } from './templates/layout';
import { renderMeeting1, saveFactFinder } from './pages/meeting1';
import { renderMeeting2 } from './pages/meeting2';
import { renderMeeting3 } from './pages/meeting3';
import { renderMeeting4 } from './pages/meeting4';

interface Env {
  D1: D1Database;
  NEON_URL: string;
}

const PAGE_TITLES: Record<string, string> = {
  meeting1: 'Fact Finder',
  meeting2: 'Insurance Education',
  meeting3: 'Systems Education',
  meeting4: 'Financials',
};

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';
    const segments = path.split('/').filter(Boolean);

    // Health check
    if (path === '/health') {
      return Response.json({ process: 'PROC-SALES-PORTAL', number: 900, status: 'ok' });
    }

    // Root
    if (segments.length === 0) {
      return new Response([
        'Process 900 — Sales Portal',
        '',
        'GET  /health                                  — health check',
        'GET  /sales/:slug/meeting1                    — Fact Finder (form)',
        'POST /sales/:slug/meeting1/save               — Save fact finder data',
        'GET  /sales/:slug/meeting2                    — Insurance Education',
        'GET  /sales/:slug/meeting3                    — Systems Education',
        'GET  /sales/:slug/meeting4                    — Financials',
      ].join('\n'), { status: 200 });
    }

    // All routes start with /sales/
    if (segments[0] !== 'sales' || segments.length < 3) {
      return new Response('Not Found — use /sales/:slug/:meeting', { status: 404 });
    }

    const slug = segments[1];
    const meeting = segments[2];

    // Resolve sales context
    const sales = await resolveSales(env.D1, slug);
    if (!sales) {
      return new Response('Prospect not found', { status: 404 });
    }

    // POST — Save fact finder: /sales/:slug/meeting1/save
    if (request.method === 'POST' && meeting === 'meeting1' && segments[3] === 'save') {
      try {
        const body = await request.json<Record<string, unknown>>();
        const result = await saveFactFinder(env.D1, sales.sales_id, body);
        return Response.json(result, { status: result.success ? 200 : 400 });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return Response.json({ error: msg }, { status: 500 });
      }
    }

    // GET — Page rendering: /sales/:slug/:meeting
    if (!PAGE_TITLES[meeting]) {
      return new Response('Not Found — valid meetings: meeting1, meeting2, meeting3, meeting4', { status: 404 });
    }

    try {
      let bodyHtml: string;

      switch (meeting) {
        case 'meeting1':
          bodyHtml = await renderMeeting1(env.D1, sales.sales_id, slug);
          break;
        case 'meeting2':
          bodyHtml = await renderMeeting2(env.D1, sales.sales_id);
          break;
        case 'meeting3':
          bodyHtml = await renderMeeting3(env.D1, sales.sales_id);
          break;
        case 'meeting4':
          bodyHtml = await renderMeeting4(env.D1, sales.sales_id);
          break;
        default:
          return new Response('Not Found', { status: 404 });
      }

      const html = renderPage(sales, meeting, PAGE_TITLES[meeting], bodyHtml);
      return new Response(html, {
        status: 200,
        headers: { 'Content-Type': 'text/html;charset=utf-8' },
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[900] ERROR: slug=${slug} meeting=${meeting} — ${msg}`);
      return new Response(`Server Error: ${msg}`, { status: 500 });
    }
  },
};

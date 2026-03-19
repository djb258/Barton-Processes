/**
 * 900 — Sales Portal: Shared HTML layout
 *
 * Branded shell for all 4 meeting pages.
 */

import type { SalesContext } from '../resolve';

const MEETINGS = [
  { slug: 'meeting1', label: '1. Fact Finder' },
  { slug: 'meeting2', label: '2. Insurance Ed' },
  { slug: 'meeting3', label: '3. Systems Ed' },
  { slug: 'meeting4', label: '4. Financials' },
];

export function renderPage(sales: SalesContext, meetingSlug: string, pageTitle: string, bodyHtml: string, extraHead?: string): string {
  const phase = sales.current_phase;
  const nav = MEETINGS.map(m => {
    const active = m.slug === meetingSlug ? ' class="active"' : '';
    return `<a href="/sales/${escHtml(sales.slug)}/${m.slug}"${active}>${m.label}</a>`;
  }).join('\n        ');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escHtml(pageTitle)} — ${escHtml(sales.legal_name)}</title>
  <style>
    :root {
      --primary: #1e293b;
      --accent: #2563eb;
      --bg: #f8fafc;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
      --green: #16a34a;
      --red: #dc2626;
      --yellow: #ca8a04;
      --blue: #2563eb;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
    header { background: var(--primary); color: #fff; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
    .header-left h1 { font-size: 18px; font-weight: 600; }
    .header-left .phase { font-size: 12px; opacity: 0.7; margin-top: 2px; }
    nav { display: flex; gap: 4px; }
    nav a { color: rgba(255,255,255,0.6); text-decoration: none; padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; }
    nav a:hover { color: #fff; background: rgba(255,255,255,0.1); }
    nav a.active { color: #fff; background: rgba(255,255,255,0.2); }
    main { max-width: 1200px; margin: 24px auto; padding: 0 24px; }
    .page-title { font-size: 24px; font-weight: 700; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }
    th { background: #f1f5f9; text-align: left; padding: 10px 14px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); border-bottom: 1px solid var(--border); }
    td { padding: 10px 14px; border-bottom: 1px solid var(--border); font-size: 14px; }
    tr:last-child td { border-bottom: none; }
    .card { background: var(--card); border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 16px; }
    .card h3 { font-size: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .card .value { font-size: 28px; font-weight: 700; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .section { margin-bottom: 32px; }
    .section h2 { font-size: 18px; font-weight: 600; margin-bottom: 12px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.03em; }
    .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; font-family: inherit; }
    .form-group textarea { min-height: 80px; resize: vertical; }
    .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
    .btn { display: inline-block; padding: 8px 20px; border-radius: 6px; font-size: 14px; font-weight: 600; text-decoration: none; cursor: pointer; border: none; }
    .btn-primary { background: var(--accent); color: #fff; }
    .btn-primary:hover { opacity: 0.9; }
    .btn-secondary { background: var(--border); color: var(--text); }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
    .badge-active { background: #dcfce7; color: var(--green); }
    .badge-scheduled { background: #dbeafe; color: var(--blue); }
    .badge-completed { background: #dcfce7; color: var(--green); }
    .empty { text-align: center; padding: 40px; color: var(--muted); }
    .slide { background: var(--card); border-radius: 8px; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 24px; min-height: 400px; }
    .slide h2 { font-size: 28px; margin-bottom: 16px; }
    .slide p { font-size: 18px; color: var(--muted); line-height: 1.8; }
    .slide-nav { display: flex; justify-content: space-between; margin-top: 24px; }
    footer { text-align: center; padding: 24px; color: var(--muted); font-size: 12px; }
  </style>
  ${extraHead || ''}
</head>
<body>
  <header>
    <div class="header-left">
      <h1>${escHtml(sales.legal_name)}</h1>
      <div class="phase">Phase: ${escHtml(phase)} | Agent: ${escHtml(sales.agent_name || '—')}</div>
    </div>
    <nav>
        ${nav}
    </nav>
  </header>
  <main>
    <div class="page-title">${escHtml(pageTitle)}</div>
    ${bodyHtml}
  </main>
  <footer>SVG Agency &middot; Sales Portal</footer>
</body>
</html>`;
}

export function escHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

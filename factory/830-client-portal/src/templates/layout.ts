/**
 * 830 — Client Portal: Shared HTML layout
 *
 * Wraps page content in a branded shell with navigation.
 */

import { type ClientContext, displayName } from '../resolve';

const PAGES = [
  { slug: 'renewal', label: 'Renewal' },
  { slug: 'ceo', label: 'CEO' },
  { slug: 'hr', label: 'HR' },
  { slug: 'underwriting', label: 'Underwriting' },
  { slug: 'agent', label: 'Service' },
];

export function renderPage(client: ClientContext, pageSlug: string, pageTitle: string, bodyHtml: string): string {
  const name = displayName(client);
  const primary = client.color_primary || '#1a365d';
  const accent = client.color_accent || '#3182ce';
  const logo = client.logo_url
    ? `<img src="${escHtml(client.logo_url)}" alt="${escHtml(name)}" style="height:36px;margin-right:12px;">`
    : '';

  const nav = PAGES.map(p => {
    const active = p.slug === pageSlug ? ' class="active"' : '';
    return `<a href="/${escHtml(client.slug)}/${p.slug}"${active}>${p.label}</a>`;
  }).join('\n        ');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escHtml(pageTitle)} — ${escHtml(name)}</title>
  <style>
    :root {
      --primary: ${primary};
      --accent: ${accent};
      --bg: #f7fafc;
      --card: #ffffff;
      --text: #1a202c;
      --muted: #718096;
      --border: #e2e8f0;
      --green: #38a169;
      --red: #e53e3e;
      --yellow: #d69e2e;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    header { background: var(--primary); color: #fff; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
    .header-left { display: flex; align-items: center; }
    .header-left h1 { font-size: 18px; font-weight: 600; }
    nav { display: flex; gap: 4px; }
    nav a { color: rgba(255,255,255,0.7); text-decoration: none; padding: 6px 14px; border-radius: 6px; font-size: 14px; font-weight: 500; }
    nav a:hover { color: #fff; background: rgba(255,255,255,0.1); }
    nav a.active { color: #fff; background: rgba(255,255,255,0.2); }
    main { max-width: 1200px; margin: 24px auto; padding: 0 24px; }
    .page-title { font-size: 24px; font-weight: 700; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 24px; }
    th { background: var(--bg); text-align: left; padding: 10px 14px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); border-bottom: 1px solid var(--border); }
    td { padding: 10px 14px; border-bottom: 1px solid var(--border); font-size: 14px; }
    tr:last-child td { border-bottom: none; }
    .card { background: var(--card); border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 16px; }
    .card h3 { font-size: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .card .value { font-size: 32px; font-weight: 700; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .section { margin-bottom: 32px; }
    .section h2 { font-size: 18px; font-weight: 600; margin-bottom: 12px; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
    .badge-open { background: #fed7d7; color: var(--red); }
    .badge-in_progress { background: #fefcbf; color: var(--yellow); }
    .badge-resolved { background: #c6f6d5; color: var(--green); }
    .badge-closed { background: var(--border); color: var(--muted); }
    .badge-active { background: #c6f6d5; color: var(--green); }
    .badge-terminated { background: #fed7d7; color: var(--red); }
    .badge-pending { background: #fefcbf; color: var(--yellow); }
    .delta-up { color: var(--red); }
    .delta-down { color: var(--green); }
    .btn { display: inline-block; padding: 6px 16px; border-radius: 6px; font-size: 13px; font-weight: 500; text-decoration: none; cursor: pointer; border: none; }
    .btn-primary { background: var(--accent); color: #fff; }
    .btn-primary:hover { opacity: 0.9; }
    .empty { text-align: center; padding: 40px; color: var(--muted); }
    footer { text-align: center; padding: 24px; color: var(--muted); font-size: 12px; }
  </style>
</head>
<body>
  <header>
    <div class="header-left">
      ${logo}
      <h1>${escHtml(name)}</h1>
    </div>
    <nav>
        ${nav}
    </nav>
  </header>
  <main>
    <div class="page-title">${escHtml(pageTitle)}</div>
    ${bodyHtml}
  </main>
  <footer>SVG Agency &middot; Client Portal</footer>
</body>
</html>`;
}

function escHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export { escHtml };

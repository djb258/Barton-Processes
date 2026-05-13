/**
 * 830 — Client Portal: Shared HTML layout
 *
 * Branded shell with navigation. All styling inline — CF Workers, no asset pipeline.
 * Design: Authoritative / Functional / Trusted
 * Fonts: Geist (headings) + Figtree (body) via Google Fonts
 * Color: OKLCH-derived from per-client primary/accent (defaults: deep navy / steel blue)
 * Theme: Light — clients checking HR/benefits data during business hours
 */

import { type ClientContext, displayName } from '../resolve';

const PAGES = [
  { slug: 'ceo',          label: 'Overview' },
  { slug: 'renewal',      label: 'Renewal' },
  { slug: 'hr',           label: 'HR' },
  { slug: 'underwriting', label: 'Underwriting' },
  { slug: 'employee',     label: 'Employee' },
  { slug: 'agent',        label: 'Service' },
];

export function renderPage(
  client: ClientContext,
  pageSlug: string,
  pageTitle: string,
  bodyHtml: string
): string {
  const name = displayName(client);
  const primary = client.color_primary || '#1a365d';
  const accent  = client.color_accent  || '#3182ce';

  const logo = client.logo_url
    ? `<img src="${escHtml(client.logo_url)}" alt="${escHtml(name)}" class="header-logo">`
    : '';

  const nav = PAGES.map(p => {
    const isActive = p.slug === pageSlug;
    return `<a href="/${escHtml(client.slug)}/${p.slug}" class="nav-link${isActive ? ' nav-link--active' : ''}">${escHtml(p.label)}</a>`;
  }).join('\n        ');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escHtml(pageTitle)} — ${escHtml(name)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Figtree:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
  <style>
    /* ── Design Tokens ────────────────────────────────────────────────────── */
    :root {
      --primary:    ${primary};
      --accent:     ${accent};

      /* Neutrals tinted toward primary hue */
      --bg:         oklch(97.5% 0.006 240);
      --surface:    oklch(99.5% 0.003 240);
      --surface-2:  oklch(95%   0.010 240);
      --border:     oklch(88%   0.012 240);
      --text:       oklch(22%   0.020 240);
      --text-muted: oklch(52%   0.015 240);
      --text-light: oklch(72%   0.010 240);

      /* Status */
      --green:      oklch(52% 0.15 155);
      --green-bg:   oklch(94% 0.05 155);
      --amber:      oklch(60% 0.13 75);
      --amber-bg:   oklch(95% 0.05 75);
      --red:        oklch(52% 0.17 25);
      --red-bg:     oklch(95% 0.05 25);
      --slate:      oklch(55% 0.02 240);
      --slate-bg:   oklch(93% 0.01 240);

      /* Spacing (4pt scale) */
      --sp-1:  4px;
      --sp-2:  8px;
      --sp-3:  12px;
      --sp-4:  16px;
      --sp-5:  24px;
      --sp-6:  32px;
      --sp-7:  48px;
      --sp-8:  64px;

      /* Type */
      --font-display: 'Geist', system-ui, sans-serif;
      --font-body:    'Figtree', system-ui, sans-serif;
    }

    /* ── Reset ────────────────────────────────────────────────────────────── */
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    html { font-size: 16px; }
    body {
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
    }

    /* ── Header ───────────────────────────────────────────────────────────── */
    .header {
      background: var(--primary);
      padding: var(--sp-4) var(--sp-6);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--sp-5);
    }
    .header-brand {
      display: flex;
      align-items: center;
      gap: var(--sp-3);
      min-width: 0;
    }
    .header-logo {
      height: 34px;
      width: auto;
      flex-shrink: 0;
    }
    .header-name {
      font-family: var(--font-display);
      font-size: 17px;
      font-weight: 600;
      color: #fff;
      letter-spacing: -0.01em;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* ── Navigation ───────────────────────────────────────────────────────── */
    .nav {
      display: flex;
      gap: var(--sp-1);
      flex-shrink: 0;
    }
    .nav-link {
      font-family: var(--font-display);
      font-size: 13px;
      font-weight: 500;
      color: rgba(255,255,255,0.65);
      text-decoration: none;
      padding: var(--sp-2) var(--sp-3);
      border-radius: 6px;
      transition: color 0.15s, background 0.15s;
      letter-spacing: 0.01em;
    }
    .nav-link:hover { color: #fff; background: rgba(255,255,255,0.12); }
    .nav-link--active { color: #fff; background: rgba(255,255,255,0.18); }

    /* ── Page Shell ───────────────────────────────────────────────────────── */
    .page {
      max-width: 1180px;
      margin: 0 auto;
      padding: var(--sp-7) var(--sp-6);
    }
    .page-header {
      margin-bottom: var(--sp-7);
    }
    .page-eyebrow {
      font-family: var(--font-display);
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: var(--sp-2);
    }
    .page-title {
      font-family: var(--font-display);
      font-size: 28px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text);
      line-height: 1.2;
    }

    /* ── Section ──────────────────────────────────────────────────────────── */
    .section {
      margin-bottom: var(--sp-7);
    }
    .section-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: var(--sp-4);
      padding-bottom: var(--sp-3);
      border-bottom: 1px solid var(--border);
    }
    .section-title {
      font-family: var(--font-display);
      font-size: 15px;
      font-weight: 600;
      color: var(--text);
      letter-spacing: -0.01em;
    }
    .section-meta {
      font-size: 12px;
      color: var(--text-muted);
    }

    /* ── Stat Row ─────────────────────────────────────────────────────────── */
    .stat-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: var(--sp-4);
      margin-bottom: var(--sp-6);
    }
    .stat {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: var(--sp-5);
    }
    .stat-value {
      font-family: var(--font-display);
      font-size: 32px;
      font-weight: 700;
      letter-spacing: -0.04em;
      color: var(--text);
      line-height: 1;
      margin-bottom: var(--sp-2);
    }
    .stat-label {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    /* ── Table ────────────────────────────────────────────────────────────── */
    .table-wrap {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th {
      text-align: left;
      padding: var(--sp-3) var(--sp-4);
      font-family: var(--font-display);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      background: var(--surface-2);
      border-bottom: 1px solid var(--border);
    }
    td {
      padding: var(--sp-3) var(--sp-4);
      font-size: 14px;
      color: var(--text);
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: oklch(97% 0.008 240); }

    /* ── Info Grid (key-value pairs) ──────────────────────────────────────── */
    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: var(--sp-4) var(--sp-6);
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: var(--sp-5);
    }
    .info-item {}
    .info-label {
      font-family: var(--font-display);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--text-muted);
      margin-bottom: var(--sp-1);
    }
    .info-value {
      font-size: 14px;
      font-weight: 500;
      color: var(--text);
    }
    .info-value--muted { color: var(--text-muted); font-style: italic; }

    /* ── Badges ───────────────────────────────────────────────────────────── */
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 9px;
      border-radius: 99px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.03em;
    }
    .badge-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      flex-shrink: 0;
    }
    .badge-active, .badge-open       { background: var(--green-bg);  color: var(--green); }
    .badge-active .badge-dot,
    .badge-open .badge-dot            { background: var(--green); }
    .badge-in_progress, .badge-waiting { background: var(--amber-bg); color: var(--amber); }
    .badge-in_progress .badge-dot,
    .badge-waiting .badge-dot          { background: var(--amber); }
    .badge-terminated, .badge-closed, .badge-resolved, .badge-churned { background: var(--slate-bg); color: var(--slate); }
    .badge-terminated .badge-dot,
    .badge-closed .badge-dot,
    .badge-resolved .badge-dot,
    .badge-churned .badge-dot          { background: var(--slate); }
    .badge-onboarding, .badge-prospect { background: oklch(93% 0.07 270); color: oklch(42% 0.18 270); }
    .badge-renewal                     { background: var(--amber-bg); color: var(--amber); }
    .badge-urgent                      { background: var(--red-bg); color: var(--red); }

    /* ── Stub Panel ───────────────────────────────────────────────────────── */
    .stub-panel {
      background: var(--surface);
      border: 1px dashed var(--border);
      border-radius: 10px;
      padding: var(--sp-7) var(--sp-6);
      text-align: center;
    }
    .stub-panel-icon {
      font-size: 28px;
      margin-bottom: var(--sp-3);
      opacity: 0.35;
    }
    .stub-panel-title {
      font-family: var(--font-display);
      font-size: 15px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: var(--sp-2);
    }
    .stub-panel-note {
      font-size: 13px;
      color: var(--text-light);
      max-width: 40ch;
      margin: 0 auto;
    }

    /* ── Empty State ──────────────────────────────────────────────────────── */
    .empty {
      padding: var(--sp-7) var(--sp-6);
      text-align: center;
      color: var(--text-muted);
      font-size: 14px;
    }
    .empty-icon {
      font-size: 24px;
      margin-bottom: var(--sp-3);
      opacity: 0.4;
    }

    /* ── Form ─────────────────────────────────────────────────────────────── */
    .form-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: var(--sp-6);
      max-width: 640px;
    }
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: var(--sp-4);
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: var(--sp-2);
    }
    .form-group--full { grid-column: 1 / -1; }
    label {
      font-family: var(--font-display);
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--text-muted);
    }
    input, select, textarea {
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text);
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 7px;
      padding: var(--sp-3) var(--sp-3);
      transition: border-color 0.15s, box-shadow 0.15s;
      outline: none;
      width: 100%;
    }
    input:focus, select:focus, textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px oklch(from var(--accent) l c h / 0.12);
    }
    textarea { resize: vertical; min-height: 100px; }
    .form-error {
      font-size: 12px;
      color: var(--red);
      margin-top: var(--sp-1);
    }
    .form-actions {
      margin-top: var(--sp-5);
    }
    .btn {
      font-family: var(--font-display);
      font-size: 13px;
      font-weight: 600;
      padding: var(--sp-3) var(--sp-5);
      border-radius: 7px;
      border: none;
      cursor: pointer;
      text-decoration: none;
      display: inline-block;
      transition: opacity 0.15s;
    }
    .btn:hover { opacity: 0.88; }
    .btn-primary { background: var(--primary); color: #fff; }
    .btn-accent  { background: var(--accent);  color: #fff; }

    /* ── Alert ────────────────────────────────────────────────────────────── */
    .alert {
      border-radius: 8px;
      padding: var(--sp-4) var(--sp-5);
      font-size: 14px;
      margin-bottom: var(--sp-5);
    }
    .alert-success { background: var(--green-bg);  color: oklch(38% 0.12 155); }
    .alert-error   { background: var(--red-bg);    color: oklch(38% 0.15 25);  }

    /* ── Priority indicator ───────────────────────────────────────────────── */
    .priority-dot {
      display: inline-block;
      width: 8px; height: 8px;
      border-radius: 50%;
      margin-right: 5px;
    }
    .priority-low    .priority-dot { background: var(--green); }
    .priority-normal .priority-dot { background: var(--accent); }
    .priority-high   .priority-dot { background: var(--amber); }
    .priority-urgent .priority-dot { background: var(--red); }

    /* ── Footer ───────────────────────────────────────────────────────────── */
    .footer {
      margin-top: var(--sp-8);
      padding: var(--sp-5) var(--sp-6);
      text-align: center;
      font-size: 12px;
      color: var(--text-light);
    }

    /* ── Responsive ───────────────────────────────────────────────────────── */
    @media (max-width: 760px) {
      .header { flex-direction: column; align-items: flex-start; gap: var(--sp-3); padding: var(--sp-4); }
      .nav { flex-wrap: wrap; }
      .page { padding: var(--sp-5) var(--sp-4); }
      .form-grid { grid-template-columns: 1fr; }
      .stat-row { grid-template-columns: 1fr 1fr; }
      .page-title { font-size: 22px; }
    }
    @media (max-width: 480px) {
      .stat-row { grid-template-columns: 1fr; }
      .info-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header class="header">
    <div class="header-brand">
      ${logo}
      <span class="header-name">${escHtml(name)}</span>
    </div>
    <nav class="nav">
      ${nav}
    </nav>
  </header>
  <main class="page">
    <div class="page-header">
      <div class="page-eyebrow">${escHtml(name)}</div>
      <h1 class="page-title">${escHtml(pageTitle)}</h1>
    </div>
    ${bodyHtml}
  </main>
  <footer class="footer">SVG Agency &middot; Client Portal &middot; ${escHtml(name)}</footer>
</body>
</html>`;
}

export function badge(value: string, extraClass?: string): string {
  const cls = `badge badge-${escHtml(value.toLowerCase().replace(/\s+/g, '_'))}${extraClass ? ' ' + extraClass : ''}`;
  return `<span class="${cls}"><span class="badge-dot"></span>${escHtml(value)}</span>`;
}

export function escHtml(s: string | null | undefined): string {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

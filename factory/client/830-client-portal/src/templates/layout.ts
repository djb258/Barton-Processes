/**
 * 830 — Client Portal: Shared HTML layout
 *
 * Editorial Authority direction (rebuild 2026-05-13):
 *   - Tone: Stripe Press / Sunday financial supplement — document, not dashboard.
 *   - Audience: executive (CEO/CFO/HR director), 27" monitor, two-second credibility check.
 *   - Type: Source Serif 4 (display/headings, editorial gravitas) + Geist (body/UI) + JetBrains Mono (tabular numerals).
 *   - Surface: warm paper off-white, never cool gray.
 *   - Decoration: hairline rules, sharp corners (0–4px), no card chrome, no drop shadows.
 *   - Numbers presented as editorial figures, never SaaS stat-cards.
 *   - Per-client branding: logo + color_primary + color_accent overlay only.
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
  const primary = client.color_primary || '#1c2a3a';
  const accent  = client.color_accent  || '#a3672b';

  const logo = client.logo_url
    ? `<img src="${escHtml(client.logo_url)}" alt="${escHtml(name)}" class="masthead-logo">`
    : '';

  const navItems = PAGES.map((p, i) => {
    const isActive = p.slug === pageSlug;
    const num = String(i + 1).padStart(2, '0');
    return `<a href="/${escHtml(client.slug)}/${p.slug}" class="nav-link${isActive ? ' nav-link--active' : ''}">
        <span class="nav-num">${num}</span>
        <span class="nav-label">${escHtml(p.label)}</span>
      </a>`;
  }).join('\n      ');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escHtml(pageTitle)} — ${escHtml(name)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;0,8..60,700;0,8..60,800;1,8..60,400&family=Geist:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    /* ───────────────────────────────────────────────────────────────────────
       Editorial Authority — design tokens
       ─────────────────────────────────────────────────────────────────────── */
    :root {
      --primary:   ${primary};
      --accent:    ${accent};

      /* Warm paper surfaces (oklch, hue 75 = paper warmth, not 240 cool blue) */
      --paper:     oklch(98% 0.006 75);
      --paper-2:   oklch(95.5% 0.010 75);
      --ink:       oklch(20% 0.012 75);
      --ink-2:     oklch(38% 0.010 75);
      --ink-3:     oklch(56% 0.008 75);
      --ink-4:     oklch(74% 0.006 75);
      --rule:      oklch(82% 0.010 75);
      --rule-2:    oklch(70% 0.012 75);

      /* Status — desaturated, editorial */
      --pos:       oklch(46% 0.13 150);
      --pos-bg:    oklch(94% 0.04 150);
      --warn:      oklch(56% 0.13 65);
      --warn-bg:   oklch(95% 0.05 65);
      --neg:       oklch(48% 0.16 25);
      --neg-bg:    oklch(95% 0.05 25);
      --neutral:   oklch(45% 0.015 75);
      --neutral-bg: oklch(93% 0.012 75);

      /* Spacing — 4pt scale, semantic */
      --sp-xs:  4px;
      --sp-sm:  8px;
      --sp-md:  12px;
      --sp:     16px;
      --sp-lg:  24px;
      --sp-xl:  32px;
      --sp-2xl: 48px;
      --sp-3xl: 72px;
      --sp-4xl: 112px;

      /* Type */
      --serif: 'Source Serif 4', Georgia, serif;
      --sans:  'Geist', system-ui, sans-serif;
      --mono:  'JetBrains Mono', ui-monospace, monospace;

      /* Layout */
      --measure-narrow: 56ch;
      --measure: 68ch;
      --canvas-max: 1440px;
      --canvas-pad: clamp(24px, 4vw, 72px);
    }

    /* ───────────────────────────────────────────────────────────────────────
       Reset + base
       ─────────────────────────────────────────────────────────────────────── */
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    html { font-size: 16px; }
    body {
      font-family: var(--sans);
      background: var(--paper);
      color: var(--ink);
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
      min-height: 100vh;
      font-feature-settings: 'ss01', 'cv11';
    }
    a { color: inherit; text-decoration: none; }
    h1, h2, h3, h4 { font-family: var(--serif); font-weight: 600; color: var(--ink); }

    /* ───────────────────────────────────────────────────────────────────────
       Masthead — editorial header pattern
       ─────────────────────────────────────────────────────────────────────── */
    .masthead {
      max-width: var(--canvas-max);
      margin: 0 auto;
      padding: var(--sp-xl) var(--canvas-pad) var(--sp-lg);
      display: grid;
      grid-template-columns: 1fr auto;
      gap: var(--sp-lg);
      align-items: end;
      border-bottom: 2px solid var(--ink);
    }
    .masthead-brand {
      display: flex;
      align-items: center;
      gap: var(--sp);
    }
    .masthead-logo {
      height: 44px;
      width: auto;
      flex-shrink: 0;
    }
    .masthead-name {
      font-family: var(--serif);
      font-size: clamp(22px, 2.2vw, 32px);
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--ink);
      line-height: 1;
    }
    .masthead-meta {
      font-family: var(--sans);
      font-size: 11px;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      color: var(--ink-3);
      text-align: right;
      line-height: 1.6;
    }

    /* ───────────────────────────────────────────────────────────────────────
       Navigation — editorial section index
       ─────────────────────────────────────────────────────────────────────── */
    .nav {
      max-width: var(--canvas-max);
      margin: 0 auto;
      padding: 0 var(--canvas-pad);
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      border-bottom: 1px solid var(--rule);
    }
    .nav-link {
      display: flex;
      align-items: baseline;
      gap: var(--sp-sm);
      padding: var(--sp) var(--sp-md);
      border-right: 1px solid var(--rule);
      transition: background 0.15s, color 0.15s;
      position: relative;
    }
    .nav-link:last-child { border-right: none; }
    .nav-link:hover { background: var(--paper-2); }
    .nav-link--active {
      background: var(--ink);
      color: var(--paper);
    }
    .nav-link--active::before {
      content: '';
      position: absolute;
      top: -2px; left: 0; right: 0;
      height: 2px;
      background: var(--accent);
    }
    .nav-num {
      font-family: var(--mono);
      font-size: 11px;
      font-weight: 500;
      color: var(--ink-3);
      letter-spacing: 0.05em;
    }
    .nav-link--active .nav-num { color: var(--paper); opacity: 0.6; }
    .nav-label {
      font-family: var(--sans);
      font-size: 13px;
      font-weight: 500;
      letter-spacing: -0.005em;
    }

    /* ───────────────────────────────────────────────────────────────────────
       Page shell
       ─────────────────────────────────────────────────────────────────────── */
    .page {
      max-width: var(--canvas-max);
      margin: 0 auto;
      padding: var(--sp-3xl) var(--canvas-pad) var(--sp-4xl);
    }
    .page-header {
      max-width: 36ch;
      margin-bottom: var(--sp-3xl);
    }
    .page-eyebrow {
      font-family: var(--sans);
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: var(--sp-md);
    }
    .page-title {
      font-family: var(--serif);
      font-size: clamp(40px, 5.8vw, 76px);
      font-weight: 700;
      line-height: 0.98;
      letter-spacing: -0.035em;
      color: var(--ink);
      font-variation-settings: 'opsz' 60;
    }
    .page-lede {
      font-family: var(--serif);
      font-size: clamp(18px, 1.6vw, 22px);
      font-weight: 400;
      line-height: 1.45;
      color: var(--ink-2);
      max-width: var(--measure);
      margin-top: var(--sp-lg);
      font-style: italic;
      font-variation-settings: 'opsz' 16;
    }

    /* ───────────────────────────────────────────────────────────────────────
       Section — editorial chapters with numeric eyebrow
       ─────────────────────────────────────────────────────────────────────── */
    .section {
      margin-bottom: var(--sp-3xl);
    }
    .section-header {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: var(--sp-lg);
      align-items: baseline;
      padding-bottom: var(--sp);
      margin-bottom: var(--sp-xl);
      border-bottom: 1px solid var(--ink);
    }
    .section-num {
      font-family: var(--mono);
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 0.05em;
      color: var(--ink-3);
    }
    .section-title, .section h2 {
      font-family: var(--serif);
      font-size: clamp(22px, 2.2vw, 28px);
      font-weight: 600;
      letter-spacing: -0.02em;
      color: var(--ink);
      line-height: 1.1;
    }
    .section-meta {
      font-family: var(--sans);
      font-size: 12px;
      font-weight: 500;
      color: var(--ink-3);
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }
    .section-header h2 { margin: 0; }

    /* ───────────────────────────────────────────────────────────────────────
       Figure row — editorial replacement for stat-cards
       Big editorial numerals, hairline-separated, no card chrome.
       ─────────────────────────────────────────────────────────────────────── */
    .figure-row, .stat-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0;
      margin-bottom: var(--sp-2xl);
      border-top: 1px solid var(--rule);
      border-bottom: 1px solid var(--rule);
    }
    .figure, .stat {
      padding: var(--sp-xl) var(--sp);
      border-right: 1px solid var(--rule);
      background: transparent;
      border-radius: 0;
      display: flex;
      flex-direction: column;
      gap: var(--sp-sm);
    }
    .figure:last-child, .stat:last-child { border-right: none; }
    .stat-value, .figure-value {
      font-family: var(--serif);
      font-size: clamp(40px, 4.4vw, 56px);
      font-weight: 700;
      letter-spacing: -0.04em;
      color: var(--ink);
      line-height: 0.9;
      font-variant-numeric: tabular-nums lining-nums;
      font-variation-settings: 'opsz' 60;
    }
    .stat-label, .figure-label {
      font-family: var(--sans);
      font-size: 11px;
      font-weight: 600;
      color: var(--ink-3);
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }
    .figure-note {
      font-family: var(--sans);
      font-size: 12px;
      color: var(--ink-3);
      margin-top: var(--sp-xs);
    }

    /* ───────────────────────────────────────────────────────────────────────
       Editorial KV grid — replaces info-grid
       ─────────────────────────────────────────────────────────────────────── */
    .kv-list, .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 0;
      background: transparent;
      border: none;
      border-top: 1px solid var(--rule);
      border-radius: 0;
      padding: 0;
    }
    .kv, .info-item {
      padding: var(--sp) var(--sp);
      border-bottom: 1px solid var(--rule);
      border-right: 1px solid var(--rule);
      display: flex;
      flex-direction: column;
      gap: var(--sp-xs);
    }
    .kv:nth-last-child(-n+1):nth-child(odd) { border-bottom: 1px solid var(--rule); }
    .kv-label, .info-label {
      font-family: var(--sans);
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--ink-3);
    }
    .kv-value, .info-value {
      font-family: var(--serif);
      font-size: 17px;
      font-weight: 500;
      color: var(--ink);
      letter-spacing: -0.01em;
      font-variation-settings: 'opsz' 16;
    }
    .info-value--muted { color: var(--ink-3); font-style: italic; }

    /* ───────────────────────────────────────────────────────────────────────
       Tables — editorial / Bloomberg-Print
       ─────────────────────────────────────────────────────────────────────── */
    .table-wrap {
      background: transparent;
      border: none;
      border-top: 2px solid var(--ink);
      border-bottom: 2px solid var(--ink);
      border-radius: 0;
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-feature-settings: 'tnum';
    }
    th {
      text-align: left;
      padding: var(--sp-md) var(--sp);
      font-family: var(--sans);
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--ink-3);
      background: transparent;
      border-bottom: 1px solid var(--ink);
    }
    td {
      padding: var(--sp) var(--sp);
      font-family: var(--serif);
      font-size: 15px;
      font-weight: 400;
      color: var(--ink);
      border-bottom: 1px solid var(--rule);
      vertical-align: top;
      letter-spacing: -0.005em;
    }
    td.num, th.num { font-family: var(--mono); font-size: 13px; text-align: right; font-feature-settings: 'tnum'; }
    tr:last-child td { border-bottom: none; }
    tbody tr:hover td { background: var(--paper-2); }

    /* ───────────────────────────────────────────────────────────────────────
       Badges — restrained, no border-stripe, no glow
       ─────────────────────────────────────────────────────────────────────── */
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 2px;
      font-family: var(--sans);
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.10em;
      text-transform: uppercase;
      line-height: 1;
    }
    .badge-dot {
      width: 5px; height: 5px;
      border-radius: 50%;
      flex-shrink: 0;
    }
    .badge-active, .badge-open       { background: var(--pos-bg); color: var(--pos); }
    .badge-active .badge-dot,
    .badge-open .badge-dot           { background: var(--pos); }
    .badge-in_progress, .badge-waiting { background: var(--warn-bg); color: var(--warn); }
    .badge-in_progress .badge-dot,
    .badge-waiting .badge-dot        { background: var(--warn); }
    .badge-terminated, .badge-closed, .badge-resolved, .badge-churned {
      background: var(--neutral-bg); color: var(--neutral);
    }
    .badge-terminated .badge-dot, .badge-closed .badge-dot,
    .badge-resolved .badge-dot, .badge-churned .badge-dot { background: var(--neutral); }
    .badge-onboarding, .badge-prospect, .badge-renewal {
      background: var(--warn-bg); color: var(--warn);
    }
    .badge-onboarding .badge-dot, .badge-prospect .badge-dot, .badge-renewal .badge-dot { background: var(--warn); }
    .badge-urgent { background: var(--neg-bg); color: var(--neg); }
    .badge-urgent .badge-dot { background: var(--neg); }

    /* ───────────────────────────────────────────────────────────────────────
       Stub panel — designed empty state, not a sad gray box
       ─────────────────────────────────────────────────────────────────────── */
    .stub-panel {
      background: transparent;
      border: 1px solid var(--rule);
      border-radius: 0;
      padding: var(--sp-3xl) var(--sp-lg);
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--sp-md);
      max-width: var(--measure-narrow);
      position: relative;
    }
    .stub-panel::before {
      content: '';
      position: absolute;
      top: 0; left: 0;
      width: 32px; height: 2px;
      background: var(--accent);
    }
    .stub-panel-eyebrow {
      font-family: var(--sans);
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      color: var(--accent);
    }
    .stub-panel-icon { display: none; } /* old emoji stubs — hide */
    .stub-panel-title {
      font-family: var(--serif);
      font-size: 22px;
      font-weight: 600;
      letter-spacing: -0.02em;
      color: var(--ink);
      line-height: 1.15;
    }
    .stub-panel-note {
      font-family: var(--serif);
      font-size: 16px;
      font-weight: 400;
      color: var(--ink-2);
      line-height: 1.55;
      font-style: italic;
      font-variation-settings: 'opsz' 16;
    }

    /* ───────────────────────────────────────────────────────────────────────
       Empty
       ─────────────────────────────────────────────────────────────────────── */
    .empty {
      padding: var(--sp-2xl) var(--sp);
      font-family: var(--serif);
      font-style: italic;
      color: var(--ink-3);
      font-size: 16px;
      border-top: 1px solid var(--rule);
      border-bottom: 1px solid var(--rule);
    }
    .empty-icon { display: none; }

    /* ───────────────────────────────────────────────────────────────────────
       Form (employee ticket form)
       ─────────────────────────────────────────────────────────────────────── */
    .form-card {
      background: transparent;
      border: none;
      border-top: 2px solid var(--ink);
      border-radius: 0;
      padding: var(--sp-xl) 0 0;
      max-width: 720px;
    }
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: var(--sp-lg);
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: var(--sp-sm);
    }
    .form-group--full { grid-column: 1 / -1; }
    label {
      font-family: var(--sans);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--ink-3);
    }
    input, select, textarea {
      font-family: var(--serif);
      font-size: 16px;
      color: var(--ink);
      background: transparent;
      border: none;
      border-bottom: 1px solid var(--rule-2);
      border-radius: 0;
      padding: var(--sp-sm) 0;
      transition: border-color 0.15s;
      outline: none;
      width: 100%;
    }
    input:focus, select:focus, textarea:focus {
      border-bottom-color: var(--accent);
      border-bottom-width: 2px;
      padding-bottom: calc(var(--sp-sm) - 1px);
    }
    textarea { resize: vertical; min-height: 96px; }
    .form-error {
      font-family: var(--sans);
      font-size: 12px;
      color: var(--neg);
      margin-top: var(--sp-xs);
    }
    .form-actions { margin-top: var(--sp-xl); }
    .btn {
      font-family: var(--sans);
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      padding: var(--sp) var(--sp-xl);
      border-radius: 2px;
      border: none;
      cursor: pointer;
      text-decoration: none;
      display: inline-block;
      transition: background 0.15s;
    }
    .btn-primary { background: var(--ink); color: var(--paper); }
    .btn-primary:hover { background: oklch(28% 0.012 75); }
    .btn-accent  { background: var(--accent); color: var(--paper); }

    /* ───────────────────────────────────────────────────────────────────────
       Alert
       ─────────────────────────────────────────────────────────────────────── */
    .alert {
      border-radius: 0;
      padding: var(--sp) var(--sp-lg);
      font-family: var(--serif);
      font-size: 15px;
      margin-bottom: var(--sp-lg);
      border-top: 2px solid currentColor;
    }
    .alert-success { background: var(--pos-bg); color: var(--pos); }
    .alert-error   { background: var(--neg-bg); color: var(--neg); }

    .priority-dot {
      display: inline-block;
      width: 7px; height: 7px;
      border-radius: 50%;
      margin-right: 6px;
    }
    .priority-low    .priority-dot { background: var(--pos); }
    .priority-normal .priority-dot { background: var(--ink-3); }
    .priority-high   .priority-dot { background: var(--warn); }
    .priority-urgent .priority-dot { background: var(--neg); }

    /* ───────────────────────────────────────────────────────────────────────
       Footer
       ─────────────────────────────────────────────────────────────────────── */
    .footer {
      max-width: var(--canvas-max);
      margin: 0 auto;
      padding: var(--sp-lg) var(--canvas-pad) var(--sp-xl);
      border-top: 1px solid var(--rule);
      font-family: var(--sans);
      font-size: 11px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--ink-3);
      display: flex;
      justify-content: space-between;
      gap: var(--sp);
    }
    .footer-mark::after {
      content: '';
      display: inline-block;
      width: 6px; height: 6px;
      background: var(--accent);
      margin-left: var(--sp-sm);
      vertical-align: middle;
    }

    /* ───────────────────────────────────────────────────────────────────────
       Responsive
       ─────────────────────────────────────────────────────────────────────── */
    @media (max-width: 840px) {
      .masthead { grid-template-columns: 1fr; gap: var(--sp); }
      .masthead-meta { text-align: left; }
      .nav { grid-template-columns: repeat(3, 1fr); }
      .nav-link { padding: var(--sp-sm) var(--sp); }
      .nav-link:nth-child(3n) { border-right: none; }
      .form-grid { grid-template-columns: 1fr; }
      .figure-row, .stat-row { grid-template-columns: 1fr 1fr; }
      .figure, .stat { border-right: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }
      .figure:nth-child(2n), .stat:nth-child(2n) { border-right: none; }
    }
    @media (max-width: 520px) {
      .figure-row, .stat-row { grid-template-columns: 1fr; }
      .figure, .stat { border-right: none; border-bottom: 1px solid var(--rule); }
      .figure:last-child, .stat:last-child { border-bottom: none; }
      .nav { grid-template-columns: repeat(2, 1fr); }
      .nav-link:nth-child(2n) { border-right: none; }
      .info-grid, .kv-list { grid-template-columns: 1fr; }
      .kv, .info-item { border-right: none; }
    }

    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; animation: none !important; }
    }
  </style>
</head>
<body>
  <header class="masthead">
    <div class="masthead-brand">
      ${logo}
      <span class="masthead-name">${escHtml(name)}</span>
    </div>
    <div class="masthead-meta">
      Client Portfolio<br>
      <span style="color:var(--ink-2)">${escHtml(client.lifecycle_stage)}</span>
    </div>
  </header>
  <nav class="nav">
    ${navItems}
  </nav>
  <main class="page">
    <div class="page-header">
      <div class="page-eyebrow">${escHtml(name)} &middot; ${escHtml(pageTitle)}</div>
      <h1 class="page-title">${escHtml(pageTitle)}</h1>
    </div>
    ${bodyHtml}
  </main>
  <footer class="footer">
    <span>SVG Agency &middot; Insurance Informatics</span>
    <span class="footer-mark">${escHtml(name)}</span>
  </footer>
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

/** Editorial figure — big number + label, used in figure-row. */
export function figure(label: string, value: string | number, note?: string): string {
  const noteHtml = note ? `<div class="figure-note">${escHtml(note)}</div>` : '';
  return `<div class="figure">
    <div class="figure-value">${escHtml(String(value))}</div>
    <div class="figure-label">${escHtml(label)}</div>
    ${noteHtml}
  </div>`;
}

/** Editorial KV row. */
export function kv(label: string, value: string): string {
  return `<div class="kv">
    <span class="kv-label">${escHtml(label)}</span>
    <span class="kv-value">${value}</span>
  </div>`;
}

/** Section header with numeric eyebrow. */
export function sectionHeader(num: string, title: string, meta?: string): string {
  const metaHtml = meta ? `<span class="section-meta">${escHtml(meta)}</span>` : '<span></span>';
  return `<div class="section-header">
    <span class="section-num">${escHtml(num)}</span>
    <h2 class="section-title">${escHtml(title)}</h2>
    ${metaHtml}
  </div>`;
}

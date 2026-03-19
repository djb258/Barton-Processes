/**
 * 830 — Renewal Page
 *
 * Current plans + renewal quotes + rate comparison.
 * Read-only. Audience: client (CEO/HR), broker.
 */

import { escHtml } from '../templates/layout';

interface Plan {
  plan_id: string; benefit_type: string; carrier_id: string; effective_date: string;
  status: string; rate_ee: number | null; rate_es: number | null; rate_ec: number | null; rate_fam: number | null;
  employer_rate_ee: number | null; employer_rate_es: number | null; employer_rate_ec: number | null; employer_rate_fam: number | null;
}

interface Quote {
  plan_quote_id: string; benefit_type: string; carrier_id: string; effective_year: number;
  rate_ee: number | null; rate_es: number | null; rate_ec: number | null; rate_fam: number | null;
  source: string | null; received_date: string | null; status: string;
}

export async function renderRenewal(d1: D1Database, clientId: string): Promise<string> {
  const plans = await d1.prepare(
    "SELECT * FROM plan WHERE client_id = ? AND status = 'active' ORDER BY benefit_type"
  ).bind(clientId).all<Plan>();

  const quotes = await d1.prepare(
    'SELECT * FROM plan_quote WHERE client_id = ? ORDER BY benefit_type, effective_year DESC, carrier_id'
  ).bind(clientId).all<Quote>();

  let html = '';

  // Current Plans
  html += '<div class="section"><h2>Current Plans</h2>';
  if (!plans.results || plans.results.length === 0) {
    html += '<div class="empty">No active plans.</div>';
  } else {
    html += `<table>
      <thead><tr><th>Benefit</th><th>Carrier</th><th>Effective</th><th>EE</th><th>ES</th><th>EC</th><th>FAM</th><th>ER EE</th><th>ER ES</th><th>ER EC</th><th>ER FAM</th></tr></thead>
      <tbody>`;
    for (const p of plans.results) {
      html += `<tr>
        <td>${escHtml(p.benefit_type)}</td>
        <td>${escHtml(p.carrier_id || '—')}</td>
        <td>${escHtml(p.effective_date || '—')}</td>
        <td>${fmt(p.rate_ee)}</td><td>${fmt(p.rate_es)}</td><td>${fmt(p.rate_ec)}</td><td>${fmt(p.rate_fam)}</td>
        <td>${fmt(p.employer_rate_ee)}</td><td>${fmt(p.employer_rate_es)}</td><td>${fmt(p.employer_rate_ec)}</td><td>${fmt(p.employer_rate_fam)}</td>
      </tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  // Renewal Quotes
  html += '<div class="section"><h2>Renewal Quotes</h2>';
  if (!quotes.results || quotes.results.length === 0) {
    html += '<div class="empty">No quotes received.</div>';
  } else {
    html += `<table>
      <thead><tr><th>Benefit</th><th>Carrier</th><th>Year</th><th>EE</th><th>ES</th><th>EC</th><th>FAM</th><th>Status</th><th>Source</th><th>Received</th></tr></thead>
      <tbody>`;
    for (const q of quotes.results) {
      // Find matching current plan for delta
      const current = plans.results?.find(p => p.benefit_type === q.benefit_type);
      html += `<tr>
        <td>${escHtml(q.benefit_type)}</td>
        <td>${escHtml(q.carrier_id)}</td>
        <td>${q.effective_year}</td>
        <td>${fmtDelta(q.rate_ee, current?.rate_ee)}</td>
        <td>${fmtDelta(q.rate_es, current?.rate_es)}</td>
        <td>${fmtDelta(q.rate_ec, current?.rate_ec)}</td>
        <td>${fmtDelta(q.rate_fam, current?.rate_fam)}</td>
        <td><span class="badge badge-${q.status}">${q.status}</span></td>
        <td>${escHtml(q.source || '—')}</td>
        <td>${escHtml(q.received_date || '—')}</td>
      </tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  return html;
}

function fmt(n: number | null): string {
  if (n == null) return '—';
  return `$${n.toFixed(2)}`;
}

function fmtDelta(quote: number | null, current: number | null): string {
  if (quote == null) return '—';
  const base = `$${quote.toFixed(2)}`;
  if (current == null) return base;
  const delta = quote - current;
  if (Math.abs(delta) < 0.01) return base;
  const sign = delta > 0 ? '+' : '';
  const cls = delta > 0 ? 'delta-up' : 'delta-down';
  return `${base} <span class="${cls}">(${sign}${delta.toFixed(2)})</span>`;
}

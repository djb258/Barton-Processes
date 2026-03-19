/**
 * 900 — Meeting 4: Financials (READ-ONLY)
 *
 * Quote presentation — all costs per insurance line, carrier comparisons.
 * This is the close meeting.
 */

import { escHtml } from '../templates/layout';

interface Quote {
  quote_id: string; benefit_type: string; carrier: string;
  rate_ee: number | null; rate_es: number | null; rate_ec: number | null; rate_fam: number | null;
  annual_cost: number | null; status: string;
}

export async function renderMeeting4(d1: D1Database, salesId: string): Promise<string> {
  const factfinder = await d1.prepare(
    'SELECT legal_name, employee_count, annual_premium FROM sales_factfinder WHERE sales_id = ?'
  ).bind(salesId).first<{ legal_name: string; employee_count: number | null; annual_premium: number | null }>();

  const quotes = await d1.prepare(
    'SELECT * FROM sales_quotes WHERE sales_id = ? ORDER BY benefit_type, carrier'
  ).bind(salesId).all<Quote>();

  let html = '';

  // Summary
  html += '<div class="cards">';
  html += card('Company', escHtml(factfinder?.legal_name || '—'));
  html += card('Employees', String(factfinder?.employee_count ?? '—'));
  html += card('Current Premium', factfinder?.annual_premium ? '$' + factfinder.annual_premium.toLocaleString() : '—');
  html += card('Quotes Received', String(quotes.results?.length ?? 0));
  html += '</div>';

  // Quotes by Benefit Type
  if (!quotes.results || quotes.results.length === 0) {
    html += '<div class="empty">No quotes loaded yet. Upload quotes via the intake process.</div>';
  } else {
    // Group by benefit type
    const grouped = new Map<string, Quote[]>();
    for (const q of quotes.results) {
      const list = grouped.get(q.benefit_type) ?? [];
      list.push(q);
      grouped.set(q.benefit_type, list);
    }

    for (const [benefitType, typeQuotes] of grouped) {
      html += `<div class="section"><h2>${escHtml(benefitType)}</h2>`;
      html += `<table>
        <thead><tr><th>Carrier</th><th>EE</th><th>ES</th><th>EC</th><th>FAM</th><th>Annual Cost</th><th>Status</th></tr></thead>
        <tbody>`;

      for (const q of typeQuotes) {
        html += `<tr>
          <td style="font-weight:600;">${escHtml(q.carrier)}</td>
          <td>${fmt(q.rate_ee)}</td>
          <td>${fmt(q.rate_es)}</td>
          <td>${fmt(q.rate_ec)}</td>
          <td>${fmt(q.rate_fam)}</td>
          <td style="font-weight:600;">${q.annual_cost ? '$' + q.annual_cost.toLocaleString() : '—'}</td>
          <td><span class="badge badge-${q.status}">${q.status}</span></td>
        </tr>`;
      }

      html += '</tbody></table></div>';
    }

    // Total comparison
    const totalByCarrier = new Map<string, number>();
    for (const q of quotes.results) {
      if (q.annual_cost) {
        totalByCarrier.set(q.carrier, (totalByCarrier.get(q.carrier) ?? 0) + q.annual_cost);
      }
    }

    if (totalByCarrier.size > 0) {
      html += '<div class="section"><h2>Total Cost Comparison</h2>';
      html += '<table><thead><tr><th>Carrier</th><th>Total Annual Cost</th><th>vs. Current</th></tr></thead><tbody>';

      const currentPremium = factfinder?.annual_premium ?? 0;
      const sorted = [...totalByCarrier.entries()].sort((a, b) => a[1] - b[1]);

      for (const [carrier, total] of sorted) {
        const delta = currentPremium > 0 ? total - currentPremium : 0;
        const deltaStr = currentPremium > 0
          ? `<span class="${delta > 0 ? 'delta-up' : 'delta-down'}">${delta > 0 ? '+' : ''}$${delta.toLocaleString()}</span>`
          : '—';
        html += `<tr>
          <td style="font-weight:600;">${escHtml(carrier)}</td>
          <td style="font-weight:600;">$${total.toLocaleString()}</td>
          <td>${deltaStr}</td>
        </tr>`;
      }

      html += '</tbody></table></div>';
    }
  }

  return html;
}

function card(label: string, value: string): string {
  return `<div class="card"><h3>${label}</h3><div class="value">${value}</div></div>`;
}

function fmt(n: number | null): string {
  if (n == null) return '—';
  return `$${n.toFixed(2)}`;
}

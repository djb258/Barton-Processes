/**
 * 830 — Underwriting Page
 *
 * Census summary, tier distribution, current coverage.
 * Read-only. Audience: stop-loss carrier underwriter.
 */

import { escHtml } from '../templates/layout';

export async function renderUnderwriting(d1: D1Database, clientId: string): Promise<string> {
  const census = await d1.prepare(`
    SELECT
      COUNT(*) as total,
      SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
      SUM(CASE WHEN status = 'terminated' THEN 1 ELSE 0 END) as terminated
    FROM person WHERE client_id = ?
  `).bind(clientId).first<{ total: number; active: number; terminated: number }>();

  const tierDist = await d1.prepare(`
    SELECT coverage_tier, COUNT(*) as cnt
    FROM election e JOIN plan p ON e.plan_id = p.plan_id AND e.client_id = p.client_id
    WHERE e.client_id = ?
    GROUP BY coverage_tier
  `).bind(clientId).all<{ coverage_tier: string; cnt: number }>();

  const byBenefit = await d1.prepare(`
    SELECT p.benefit_type, COUNT(*) as enrolled
    FROM election e JOIN plan p ON e.plan_id = p.plan_id AND e.client_id = p.client_id
    WHERE e.client_id = ?
    GROUP BY p.benefit_type
  `).bind(clientId).all<{ benefit_type: string; enrolled: number }>();

  const plans = await d1.prepare(
    "SELECT * FROM plan WHERE client_id = ? AND status = 'active' ORDER BY benefit_type"
  ).bind(clientId).all<{
    plan_id: string; benefit_type: string; carrier_id: string | null;
    effective_date: string | null; rate_ee: number | null; rate_es: number | null;
    rate_ec: number | null; rate_fam: number | null;
  }>();

  const totalEnrolled = tierDist.results?.reduce((sum, r) => sum + r.cnt, 0) ?? 0;

  let html = '';

  // Census Summary
  html += '<div class="cards">';
  html += card('Total Employees', String(census?.total ?? 0));
  html += card('Active', String(census?.active ?? 0));
  html += card('Terminated', String(census?.terminated ?? 0));
  html += card('Total Enrolled', String(totalEnrolled));
  html += '</div>';

  // Tier Distribution
  html += '<div class="section"><h2>Coverage Tier Distribution</h2>';
  if (!tierDist.results || tierDist.results.length === 0) {
    html += '<div class="empty">No elections.</div>';
  } else {
    html += '<table><thead><tr><th>Tier</th><th>Count</th><th>%</th></tr></thead><tbody>';
    for (const t of tierDist.results) {
      const pct = totalEnrolled > 0 ? ((t.cnt / totalEnrolled) * 100).toFixed(1) : '0.0';
      html += `<tr><td>${escHtml(t.coverage_tier)}</td><td>${t.cnt}</td><td>${pct}%</td></tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  // Enrollment by Benefit Type
  html += '<div class="section"><h2>Enrollment by Benefit Type</h2>';
  if (!byBenefit.results || byBenefit.results.length === 0) {
    html += '<div class="empty">No enrollments.</div>';
  } else {
    html += '<table><thead><tr><th>Benefit</th><th>Enrolled</th></tr></thead><tbody>';
    for (const b of byBenefit.results) {
      html += `<tr><td>${escHtml(b.benefit_type)}</td><td>${b.enrolled}</td></tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  // Current Plans
  html += '<div class="section"><h2>Current Plans</h2>';
  if (!plans.results || plans.results.length === 0) {
    html += '<div class="empty">No active plans.</div>';
  } else {
    html += '<table><thead><tr><th>Benefit</th><th>Carrier</th><th>Effective</th><th>EE</th><th>ES</th><th>EC</th><th>FAM</th></tr></thead><tbody>';
    for (const p of plans.results) {
      html += `<tr>
        <td>${escHtml(p.benefit_type)}</td>
        <td>${escHtml(p.carrier_id || '—')}</td>
        <td>${escHtml(p.effective_date || '—')}</td>
        <td>${fmt(p.rate_ee)}</td><td>${fmt(p.rate_es)}</td><td>${fmt(p.rate_ec)}</td><td>${fmt(p.rate_fam)}</td>
      </tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  return html;
}

function card(label: string, value: string): string {
  return `<div class="card"><h3>${label}</h3><div class="value">${value}</div></div>`;
}

function fmt(n: number | null): string {
  if (n == null) return '—';
  return `$${n.toFixed(2)}`;
}

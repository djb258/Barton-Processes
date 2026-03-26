/**
 * 830 — CEO Dashboard
 *
 * Cost overview, plan summary, headcount, ticket counts.
 * Read-only. Audience: client CEO.
 */

import { escHtml } from '../templates/layout';

export async function renderCeo(d1: D1Database, clientId: string): Promise<string> {
  const client = await d1.prepare('SELECT * FROM client WHERE client_id = ?').bind(clientId).first<{
    legal_name: string; effective_date: string | null; status: string;
  }>();

  const planSummary = await d1.prepare(
    "SELECT benefit_type, COUNT(*) as plan_count FROM plan WHERE client_id = ? AND status = 'active' GROUP BY benefit_type"
  ).bind(clientId).all<{ benefit_type: string; plan_count: number }>();

  const headcount = await d1.prepare(
    "SELECT COUNT(*) as cnt FROM person WHERE client_id = ? AND status = 'active'"
  ).bind(clientId).first<{ cnt: number }>();

  const tickets = await d1.prepare(
    'SELECT status, COUNT(*) as cnt FROM service_request WHERE client_id = ? GROUP BY status'
  ).bind(clientId).all<{ status: string; cnt: number }>();

  const totalPlans = planSummary.results?.reduce((sum, r) => sum + r.plan_count, 0) ?? 0;
  const openTickets = tickets.results?.find(t => t.status === 'open')?.cnt ?? 0;
  const inProgress = tickets.results?.find(t => t.status === 'in_progress')?.cnt ?? 0;

  let html = '';

  // Summary Cards
  html += '<div class="cards">';
  html += card('Active Employees', String(headcount?.cnt ?? 0));
  html += card('Benefit Plans', String(totalPlans));
  html += card('Open Tickets', String(openTickets + inProgress));
  html += card('Status', `<span class="badge badge-${client?.status ?? 'active'}">${client?.status ?? 'active'}</span>`);
  html += '</div>';

  // Plans by Type
  html += '<div class="section"><h2>Benefits Summary</h2>';
  if (!planSummary.results || planSummary.results.length === 0) {
    html += '<div class="empty">No active plans.</div>';
  } else {
    html += '<table><thead><tr><th>Benefit Type</th><th>Active Plans</th></tr></thead><tbody>';
    for (const p of planSummary.results) {
      html += `<tr><td>${escHtml(p.benefit_type)}</td><td>${p.plan_count}</td></tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  // Tickets
  html += '<div class="section"><h2>Service Tickets</h2>';
  if (!tickets.results || tickets.results.length === 0) {
    html += '<div class="empty">No tickets.</div>';
  } else {
    html += '<table><thead><tr><th>Status</th><th>Count</th></tr></thead><tbody>';
    for (const t of tickets.results) {
      html += `<tr><td><span class="badge badge-${t.status}">${t.status}</span></td><td>${t.cnt}</td></tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  return html;
}

function card(label: string, value: string): string {
  return `<div class="card"><h3>${label}</h3><div class="value">${value}</div></div>`;
}

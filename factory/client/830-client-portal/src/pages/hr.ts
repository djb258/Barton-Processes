/**
 * 830 — HR Portal
 *
 * Employee roster, elections, enrollment status, tickets.
 * Read-only. Audience: client HR.
 */

import { escHtml } from '../templates/layout';

export async function renderHr(d1: D1Database, clientId: string): Promise<string> {
  const people = await d1.prepare(
    'SELECT * FROM person WHERE client_id = ? ORDER BY last_name, first_name'
  ).bind(clientId).all<{
    person_id: string; first_name: string; last_name: string; status: string;
  }>();

  const elections = await d1.prepare(`
    SELECT e.person_id, e.coverage_tier, e.effective_date, p.benefit_type, p.carrier_id
    FROM election e JOIN plan p ON e.plan_id = p.plan_id AND e.client_id = p.client_id
    WHERE e.client_id = ?
  `).bind(clientId).all<{
    person_id: string; coverage_tier: string; effective_date: string;
    benefit_type: string; carrier_id: string | null;
  }>();

  const batches = await d1.prepare(
    'SELECT * FROM enrollment_intake WHERE client_id = ? ORDER BY upload_date DESC LIMIT 10'
  ).bind(clientId).all<{
    enrollment_intake_id: string; upload_date: string; status: string;
  }>();

  const tickets = await d1.prepare(
    "SELECT * FROM service_request WHERE client_id = ? AND status IN ('open','in_progress') ORDER BY opened_at DESC"
  ).bind(clientId).all<{
    service_request_id: string; category: string; status: string; opened_at: string;
  }>();

  // Build election lookup: person_id → elections[]
  const electionMap = new Map<string, typeof elections.results>();
  for (const e of elections.results ?? []) {
    const list = electionMap.get(e.person_id) ?? [];
    list.push(e);
    electionMap.set(e.person_id, list);
  }

  let html = '';

  // Employee Roster
  html += '<div class="section"><h2>Employee Roster</h2>';
  if (!people.results || people.results.length === 0) {
    html += '<div class="empty">No employees.</div>';
  } else {
    html += '<table><thead><tr><th>Name</th><th>Status</th><th>Elected Plans</th></tr></thead><tbody>';
    for (const p of people.results) {
      const personElections = electionMap.get(p.person_id) ?? [];
      const elStr = personElections.length > 0
        ? personElections.map(e => `${escHtml(e.benefit_type)} (${e.coverage_tier})`).join(', ')
        : '<span style="color:var(--muted)">None</span>';
      html += `<tr>
        <td>${escHtml(p.last_name)}, ${escHtml(p.first_name)}</td>
        <td><span class="badge badge-${p.status}">${p.status}</span></td>
        <td>${elStr}</td>
      </tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  // Recent Enrollment Batches
  html += '<div class="section"><h2>Recent Enrollments</h2>';
  if (!batches.results || batches.results.length === 0) {
    html += '<div class="empty">No enrollment batches.</div>';
  } else {
    html += '<table><thead><tr><th>Date</th><th>Status</th><th>Batch ID</th></tr></thead><tbody>';
    for (const b of batches.results) {
      html += `<tr>
        <td>${escHtml(b.upload_date)}</td>
        <td><span class="badge badge-${b.status}">${b.status}</span></td>
        <td style="font-family:monospace;font-size:12px;">${escHtml(b.enrollment_intake_id.slice(0, 8))}</td>
      </tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  // Open Tickets
  html += '<div class="section"><h2>Open Tickets</h2>';
  if (!tickets.results || tickets.results.length === 0) {
    html += '<div class="empty">No open tickets.</div>';
  } else {
    html += '<table><thead><tr><th>Category</th><th>Status</th><th>Opened</th></tr></thead><tbody>';
    for (const t of tickets.results) {
      html += `<tr>
        <td>${escHtml(t.category)}</td>
        <td><span class="badge badge-${t.status}">${t.status}</span></td>
        <td>${escHtml(t.opened_at)}</td>
      </tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  return html;
}

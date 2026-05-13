/**
 * 830 — HR Portal
 *
 * Employee roster + HR contacts. Benefits section is STUB.
 * Read-only. Audience: client HR.
 */

import { escHtml, badge } from '../templates/layout';
import type { ClientContext } from '../resolve';

export async function renderHr(client: ClientContext, d1: D1Database): Promise<string> {
  const [employees, hrContacts, openTickets] = await Promise.all([
    d1.prepare(
      'SELECT employee_id, first_name, last_name, employment_status, hire_date FROM client_employees WHERE client_id=? ORDER BY last_name, first_name'
    ).bind(client.client_id).all<{
      employee_id: string; first_name: string; last_name: string;
      employment_status: string; hire_date: string | null;
    }>(),

    d1.prepare(
      "SELECT contact_id, full_name, role, email, phone FROM client_contacts WHERE client_id=? AND role LIKE '%HR%' ORDER BY full_name"
    ).bind(client.client_id).all<{
      contact_id: string; full_name: string; role: string; email: string | null; phone: string | null;
    }>(),

    d1.prepare(
      "SELECT ticket_id, category, subject, status, priority, created_at FROM client_tickets WHERE client_id=? AND status IN ('open','in_progress','waiting') ORDER BY created_at DESC"
    ).bind(client.client_id).all<{
      ticket_id: string; category: string; subject: string; status: string; priority: string; created_at: string;
    }>(),
  ]);

  const active = employees.results?.filter(e => e.employment_status === 'active').length ?? 0;
  const terminated = employees.results?.filter(e => e.employment_status === 'terminated').length ?? 0;

  let html = '';

  // ── Stat row ──────────────────────────────────────────────────────────────
  html += '<div class="stat-row">';
  html += stat('Active', String(active));
  html += stat('Terminated', String(terminated));
  html += stat('Total', String(employees.results?.length ?? 0));
  html += stat('Open tickets', String(openTickets.results?.length ?? 0));
  html += '</div>';

  // ── Employee Roster ───────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Employee Roster</h2></div>';
  if (!employees.results || employees.results.length === 0) {
    html += '<div class="empty">No employees on record.</div>';
  } else {
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Name</th><th>Status</th><th>Hired</th></tr></thead><tbody>';
    for (const e of employees.results) {
      html += `<tr>
        <td>${escHtml(e.last_name)}, ${escHtml(e.first_name)}</td>
        <td>${badge(e.employment_status)}</td>
        <td>${escHtml(e.hire_date ? e.hire_date.slice(0, 10) : '—')}</td>
      </tr>`;
    }
    html += '</tbody></table></div>';
  }
  html += '</div>';

  // ── HR Contacts ───────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>HR Contacts</h2></div>';
  if (!hrContacts.results || hrContacts.results.length === 0) {
    html += '<div class="empty">No HR contacts on record.</div>';
  } else {
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Name</th><th>Role</th><th>Email</th><th>Phone</th></tr></thead><tbody>';
    for (const c of hrContacts.results) {
      html += `<tr>
        <td>${escHtml(c.full_name)}</td>
        <td>${escHtml(c.role)}</td>
        <td>${c.email ? `<a href="mailto:${escHtml(c.email)}">${escHtml(c.email)}</a>` : '—'}</td>
        <td>${escHtml(c.phone || '—')}</td>
      </tr>`;
    }
    html += '</tbody></table></div>';
  }
  html += '</div>';

  // ── Open Tickets ──────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Open Tickets</h2></div>';
  if (!openTickets.results || openTickets.results.length === 0) {
    html += '<div class="empty">No open tickets.</div>';
  } else {
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Category</th><th>Subject</th><th>Priority</th><th>Status</th><th>Opened</th></tr></thead><tbody>';
    for (const t of openTickets.results) {
      html += `<tr>
        <td>${escHtml(t.category)}</td>
        <td>${escHtml(t.subject)}</td>
        <td>${badge(t.priority)}</td>
        <td>${badge(t.status)}</td>
        <td>${escHtml(t.created_at.slice(0, 10))}</td>
      </tr>`;
    }
    html += '</tbody></table></div>';
  }
  html += '</div>';

  // ── Benefits — STUB ───────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Benefits</h2></div>';
  html += `<div class="stub-panel">
    <div class="stub-icon">🗂</div>
    <div class="stub-title">Benefits management coming soon</div>
    <div class="stub-body">Election data, carrier details, and enrollment summaries will appear here once configured.</div>
  </div>`;
  html += '</div>';

  return html;
}

function stat(label: string, value: string): string {
  return `<div class="stat"><div class="stat-value">${escHtml(value)}</div><div class="stat-label">${escHtml(label)}</div></div>`;
}

/**
 * 830 — Client Portal: CEO / Overview page
 *
 * Client profile + summary counts: employees, contacts, vendors,
 * interactions (open/resolved), tickets (open/resolved).
 * Read-only. Queries svg-d1-client.
 * Audience: client CEO.
 */

import { escHtml, badge } from '../templates/layout';
import type { ClientContext } from '../resolve';

export async function renderCeo(client: ClientContext, d1: D1Database): Promise<string> {
  const [employees, contacts, vendors, interactions, tickets] = await Promise.all([
    d1.prepare(
      "SELECT COUNT(*) as total, SUM(CASE WHEN employment_status='active' THEN 1 ELSE 0 END) as active FROM client_employees WHERE client_id=?"
    ).bind(client.client_id).first<{ total: number; active: number }>(),

    d1.prepare(
      "SELECT COUNT(*) as cnt FROM client_contacts WHERE client_id=?"
    ).bind(client.client_id).first<{ cnt: number }>(),

    d1.prepare(
      "SELECT COUNT(*) as cnt FROM client_vendors WHERE client_id=?"
    ).bind(client.client_id).first<{ cnt: number }>(),

    d1.prepare(
      "SELECT resolved, COUNT(*) as cnt FROM client_interactions WHERE client_id=? GROUP BY resolved"
    ).bind(client.client_id).all<{ resolved: number; cnt: number }>(),

    d1.prepare(
      "SELECT status, COUNT(*) as cnt FROM client_tickets WHERE client_id=? GROUP BY status"
    ).bind(client.client_id).all<{ status: string; cnt: number }>(),
  ]);

  const iOpen = interactions.results?.find(r => r.resolved === 0)?.cnt ?? 0;
  const iResolved = interactions.results?.find(r => r.resolved === 1)?.cnt ?? 0;
  const tOpen = (tickets.results?.find(r => r.status === 'open')?.cnt ?? 0)
    + (tickets.results?.find(r => r.status === 'in_progress')?.cnt ?? 0);
  const tResolved = tickets.results?.find(r => r.status === 'resolved')?.cnt ?? 0;

  let html = '';

  // ── Stat row ──────────────────────────────────────────────────────────────
  html += '<div class="stat-row">';
  html += stat('Active employees', String(employees?.active ?? 0));
  html += stat('Contacts', String(contacts?.cnt ?? 0));
  html += stat('Vendors', String(vendors?.cnt ?? 0));
  html += stat('Open interactions', String(iOpen));
  html += stat('Open tickets', String(tOpen));
  html += '</div>';

  // ── Client profile ────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Client Profile</h2></div>';
  html += '<div class="info-grid">';
  html += infoItem('Status', badge(client.lifecycle_stage));
  html += infoItem('Employees on file', String(employees?.total ?? 0));
  if (client.industry) html += infoItem('Industry', escHtml(client.industry));
  if (client.ein) html += infoItem('EIN', escHtml(client.ein));
  if (client.onboarded_at) html += infoItem('Onboarded', escHtml(client.onboarded_at.slice(0, 10)));
  html += '</div>';
  html += '</div>';

  // ── Interactions summary ──────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Interactions</h2></div>';
  html += '<div class="stat-row">';
  html += stat('Open', String(iOpen));
  html += stat('Resolved', String(iResolved));
  html += stat('Total', String(iOpen + iResolved));
  html += '</div>';
  html += '</div>';

  // ── Ticket summary ────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Service Tickets</h2></div>';
  if (!tickets.results || tickets.results.length === 0) {
    html += '<div class="empty">No tickets on record.</div>';
  } else {
    html += '<table><thead><tr><th>Status</th><th>Count</th></tr></thead><tbody>';
    for (const t of tickets.results) {
      html += `<tr><td>${badge(t.status)}</td><td>${t.cnt}</td></tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  return html;
}

function stat(label: string, value: string): string {
  return `<div class="stat"><div class="stat-value">${escHtml(value)}</div><div class="stat-label">${escHtml(label)}</div></div>`;
}

function infoItem(label: string, value: string): string {
  return `<div class="info-item"><span class="info-label">${escHtml(label)}</span><span class="info-value">${value}</span></div>`;
}

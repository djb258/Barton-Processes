/**
 * 830 — Renewal Page
 *
 * Lifecycle stage, key contacts, vendors. Renewal quote section is STUB.
 * Read-only. Audience: client (CEO/HR), broker.
 */

import { escHtml, badge } from '../templates/layout';
import type { ClientContext } from '../resolve';

export async function renderRenewal(client: ClientContext, d1: D1Database): Promise<string> {
  const [contacts, vendors] = await Promise.all([
    d1.prepare(
      'SELECT contact_id, full_name, role, email, phone FROM client_contacts WHERE client_id=? ORDER BY role, full_name'
    ).bind(client.client_id).all<{
      contact_id: string; full_name: string; role: string; email: string | null; phone: string | null;
    }>(),

    d1.prepare(
      'SELECT vendor_id, vendor_name, vendor_type, group_number, integration_type FROM client_vendors WHERE client_id=? ORDER BY vendor_type, vendor_name'
    ).bind(client.client_id).all<{
      vendor_id: string; vendor_name: string; vendor_type: string;
      group_number: string | null; integration_type: string | null;
    }>(),
  ]);

  let html = '';

  // ── Client stage ──────────────────────────────────────────────────────────
  html += '<div class="stat-row">';
  html += stat('Lifecycle stage', badge(client.lifecycle_stage));
  html += stat('Contacts', String(contacts.results?.length ?? 0));
  html += stat('Vendors', String(vendors.results?.length ?? 0));
  html += '</div>';

  // ── Key Contacts ──────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Key Contacts</h2></div>';
  if (!contacts.results || contacts.results.length === 0) {
    html += '<div class="empty">No contacts on record.</div>';
  } else {
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Name</th><th>Role</th><th>Email</th><th>Phone</th></tr></thead><tbody>';
    for (const c of contacts.results) {
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

  // ── Vendors ───────────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Vendors</h2></div>';
  if (!vendors.results || vendors.results.length === 0) {
    html += '<div class="empty">No vendors on record.</div>';
  } else {
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Name</th><th>Type</th><th>Group #</th><th>Integration</th></tr></thead><tbody>';
    for (const v of vendors.results) {
      html += `<tr>
        <td>${escHtml(v.vendor_name)}</td>
        <td>${escHtml(v.vendor_type)}</td>
        <td>${escHtml(v.group_number || '—')}</td>
        <td>${escHtml(v.integration_type || '—')}</td>
      </tr>`;
    }
    html += '</tbody></table></div>';
  }
  html += '</div>';

  // ── Renewal Quote — STUB ──────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Renewal Quote</h2></div>';
  html += `<div class="stub-panel">
    <div class="stub-icon">📋</div>
    <div class="stub-title">Renewal quotes coming soon</div>
    <div class="stub-body">Plan-rate comparison, carrier quotes, and renewal recommendations will appear here once quotes are loaded.</div>
  </div>`;
  html += '</div>';

  // ── Plan Rates — STUB ─────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Plan Rates</h2></div>';
  html += `<div class="stub-panel">
    <div class="stub-icon">💰</div>
    <div class="stub-title">Rate detail coming soon</div>
    <div class="stub-body">Current premium rates by tier and benefit line will appear here once plans are configured.</div>
  </div>`;
  html += '</div>';

  return html;
}

function stat(label: string, value: string): string {
  return `<div class="stat"><div class="stat-value">${value}</div><div class="stat-label">${escHtml(label)}</div></div>`;
}

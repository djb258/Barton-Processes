/**
 * 830 — Agent Dashboard
 *
 * Interaction log + ticket queue with status updates. READ-WRITE.
 * Write path: POST /:slug/agent/ticket/:ticket_id/status → UPDATE client_tickets.
 * Audience: Dave's team (internal).
 */

import { escHtml, badge } from '../templates/layout';
import type { ClientContext } from '../resolve';

const VALID_STATUSES = new Set(['open', 'in_progress', 'waiting', 'resolved', 'closed']);

export async function renderAgent(client: ClientContext, d1: D1Database): Promise<string> {
  const [interactions, tickets, errors] = await Promise.all([
    d1.prepare(
      'SELECT interaction_id, interaction_type, subject, direction, resolved, occurred_at FROM client_interactions WHERE client_id=? ORDER BY occurred_at DESC LIMIT 50'
    ).bind(client.client_id).all<{
      interaction_id: string; interaction_type: string; subject: string | null;
      direction: string | null; resolved: number; occurred_at: string;
    }>(),

    d1.prepare(`
      SELECT ticket_id, full_name, email, category, subject, priority, status, created_at, updated_at
      FROM client_tickets WHERE client_id=?
      ORDER BY
        CASE status WHEN 'open' THEN 1 WHEN 'in_progress' THEN 2 WHEN 'waiting' THEN 3 WHEN 'resolved' THEN 4 ELSE 5 END,
        created_at DESC
    `).bind(client.client_id).all<{
      ticket_id: string; full_name: string; email: string; category: string; subject: string;
      priority: string; status: string; created_at: string; updated_at: string;
    }>(),

    d1.prepare(
      "SELECT ticket_error_id, error_code, error_message, severity, status, created_at FROM client_tickets_error WHERE client_id=? ORDER BY created_at DESC LIMIT 20"
    ).bind(client.client_id).all<{
      ticket_error_id: string; error_code: string; error_message: string;
      severity: string; status: string; created_at: string;
    }>(),
  ]);

  const counts: Record<string, number> = {};
  for (const t of tickets.results ?? []) {
    counts[t.status] = (counts[t.status] ?? 0) + 1;
  }

  let html = '';

  // ── Stat row ──────────────────────────────────────────────────────────────
  html += '<div class="stat-row">';
  html += stat('Open', String(counts['open'] ?? 0));
  html += stat('In progress', String(counts['in_progress'] ?? 0));
  html += stat('Waiting', String(counts['waiting'] ?? 0));
  html += stat('Resolved', String(counts['resolved'] ?? 0));
  html += stat('Interactions (last 50)', String(interactions.results?.length ?? 0));
  html += '</div>';

  // ── Ticket Queue ──────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Ticket Queue</h2></div>';
  if (!tickets.results || tickets.results.length === 0) {
    html += '<div class="empty">No tickets.</div>';
  } else {
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Submitted by</th><th>Category</th><th>Subject</th><th>Priority</th><th>Status</th><th>Opened</th><th>Action</th></tr></thead><tbody>';
    for (const t of tickets.results) {
      const actionHtml = buildActionButtons(t.ticket_id, t.status, client.slug);
      html += `<tr>
        <td>${escHtml(t.full_name)}<br><small style="color:var(--text-muted)">${escHtml(t.email)}</small></td>
        <td>${escHtml(t.category)}</td>
        <td>${escHtml(t.subject)}</td>
        <td>${badge(t.priority)}</td>
        <td>${badge(t.status)}</td>
        <td>${escHtml(t.created_at.slice(0, 10))}</td>
        <td>${actionHtml}</td>
      </tr>`;
    }
    html += '</tbody></table></div>';
  }
  html += '</div>';

  // ── Interaction Log ────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Interaction Log <small style="font-weight:400;font-size:0.875rem">(last 50)</small></h2></div>';
  if (!interactions.results || interactions.results.length === 0) {
    html += '<div class="empty">No interactions on record.</div>';
  } else {
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Type</th><th>Subject</th><th>Direction</th><th>Status</th><th>Date</th></tr></thead><tbody>';
    for (const i of interactions.results) {
      html += `<tr>
        <td>${escHtml(i.interaction_type)}</td>
        <td>${escHtml(i.subject || '—')}</td>
        <td>${escHtml(i.direction || '—')}</td>
        <td>${badge(i.resolved === 1 ? 'resolved' : 'open')}</td>
        <td>${escHtml(i.occurred_at.slice(0, 10))}</td>
      </tr>`;
    }
    html += '</tbody></table></div>';
  }
  html += '</div>';

  // ── Error Log ─────────────────────────────────────────────────────────────
  if (errors.results && errors.results.length > 0) {
    html += '<div class="section">';
    html += '<div class="section-header"><h2>Error Log</h2></div>';
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Code</th><th>Message</th><th>Severity</th><th>Status</th><th>Time</th></tr></thead><tbody>';
    for (const e of errors.results) {
      html += `<tr>
        <td><code>${escHtml(e.error_code)}</code></td>
        <td>${escHtml(e.error_message)}</td>
        <td>${badge(e.severity)}</td>
        <td>${badge(e.status)}</td>
        <td>${escHtml(e.created_at.slice(0, 16))}</td>
      </tr>`;
    }
    html += '</tbody></table></div>';
    html += '</div>';
  }

  // ── Inline JS for ticket status updates ───────────────────────────────────
  html += `<script>
async function setTicketStatus(ticketId, newStatus) {
  const btn = document.querySelector('[data-tid="' + ticketId + '"][data-status="' + newStatus + '"]');
  if (btn) btn.disabled = true;
  try {
    const res = await fetch('/${escHtml(client.slug)}/agent/ticket/' + encodeURIComponent(ticketId) + '/status', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({status: newStatus})
    });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    } else {
      alert('Error: ' + (data.error || 'Unknown error'));
      if (btn) btn.disabled = false;
    }
  } catch (err) {
    alert('Request failed: ' + err.message);
    if (btn) btn.disabled = false;
  }
}
</script>`;

  return html;
}

/**
 * Write path — UPDATE client_tickets SET status.
 * Any valid status is allowed as a target (no forced linear progression).
 * Sets resolved_at when moving to resolved or closed.
 */
export async function updateTicketStatus(
  d1: D1Database,
  clientId: string,
  ticketId: string,
  newStatus: string,
): Promise<{ success: boolean; error?: string }> {
  if (!VALID_STATUSES.has(newStatus)) {
    return { success: false, error: `Invalid status: ${newStatus}` };
  }

  const ticket = await d1.prepare(
    'SELECT status FROM client_tickets WHERE ticket_id=? AND client_id=?'
  ).bind(ticketId, clientId).first<{ status: string }>();

  if (!ticket) {
    return { success: false, error: 'Ticket not found' };
  }

  if (ticket.status === newStatus) {
    return { success: true }; // idempotent
  }

  const setResolved = (newStatus === 'resolved' || newStatus === 'closed')
    ? ", resolved_at = datetime('now')"
    : '';

  await d1.prepare(
    `UPDATE client_tickets SET status=?, updated_at=datetime('now')${setResolved} WHERE ticket_id=? AND client_id=?`
  ).bind(newStatus, ticketId, clientId).run();

  console.log(`[830] ticket ${ticketId}: ${ticket.status} → ${newStatus}`);
  return { success: true };
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function buildActionButtons(ticketId: string, currentStatus: string, slug: string): string {
  if (currentStatus === 'closed') return '—';

  const moves: Array<{ label: string; status: string; cls: string }> = [];

  if (currentStatus === 'open') {
    moves.push({ label: 'Start', status: 'in_progress', cls: 'btn-accent' });
  }
  if (currentStatus === 'in_progress' || currentStatus === 'waiting') {
    moves.push({ label: 'Resolve', status: 'resolved', cls: 'btn-primary' });
  }
  if (currentStatus !== 'waiting' && currentStatus !== 'resolved') {
    moves.push({ label: 'Wait', status: 'waiting', cls: 'btn' });
  }
  if (currentStatus === 'resolved') {
    moves.push({ label: 'Close', status: 'closed', cls: 'btn' });
  }

  return moves.map(m =>
    `<button class="${m.cls}" data-tid="${escHtml(ticketId)}" data-status="${m.status}" onclick="setTicketStatus('${escHtml(ticketId)}','${m.status}')">${m.label}</button>`
  ).join(' ');
}

function stat(label: string, value: string): string {
  return `<div class="stat"><div class="stat-value">${escHtml(value)}</div><div class="stat-label">${escHtml(label)}</div></div>`;
}

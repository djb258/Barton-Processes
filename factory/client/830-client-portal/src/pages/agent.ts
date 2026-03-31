/**
 * 830 — Service Agent Dashboard
 *
 * Ticket queue with status updates. READ-WRITE.
 * Audience: Dave's team (internal).
 */

import { escHtml } from '../templates/layout';

const VALID_TRANSITIONS: Record<string, string> = {
  open: 'in_progress',
  in_progress: 'resolved',
  resolved: 'closed',
};

const NEXT_LABEL: Record<string, string> = {
  open: 'Start',
  in_progress: 'Resolve',
  resolved: 'Close',
};

export async function renderAgent(d1: D1Database, clientId: string, slug: string): Promise<string> {
  const tickets = await d1.prepare(`
    SELECT * FROM service_request WHERE client_id = ?
    ORDER BY
      CASE status WHEN 'open' THEN 1 WHEN 'in_progress' THEN 2 WHEN 'resolved' THEN 3 ELSE 4 END,
      opened_at DESC
  `).bind(clientId).all<{
    service_request_id: string; category: string; status: string; opened_at: string; updated_at: string;
  }>();

  const errors = await d1.prepare(
    'SELECT * FROM service_error WHERE client_id = ? ORDER BY created_at DESC LIMIT 20'
  ).bind(clientId).all<{
    service_error_id: string; source_entity: string; error_code: string; error_message: string; created_at: string;
  }>();

  // Ticket counts
  const counts: Record<string, number> = { open: 0, in_progress: 0, resolved: 0, closed: 0 };
  for (const t of tickets.results ?? []) {
    counts[t.status] = (counts[t.status] ?? 0) + 1;
  }

  let html = '';

  // Summary Cards
  html += '<div class="cards">';
  html += card('Open', String(counts.open), 'badge-open');
  html += card('In Progress', String(counts.in_progress), 'badge-in_progress');
  html += card('Resolved', String(counts.resolved), 'badge-resolved');
  html += card('Closed', String(counts.closed), 'badge-closed');
  html += '</div>';

  // Tickets Table
  html += '<div class="section"><h2>Tickets</h2>';
  if (!tickets.results || tickets.results.length === 0) {
    html += '<div class="empty">No tickets.</div>';
  } else {
    html += '<table><thead><tr><th>Category</th><th>Status</th><th>Opened</th><th>Updated</th><th>Action</th></tr></thead><tbody>';
    for (const t of tickets.results) {
      const nextStatus = VALID_TRANSITIONS[t.status];
      const actionBtn = nextStatus
        ? `<button class="btn btn-primary" onclick="updateTicket('${t.service_request_id}', '${nextStatus}')">${NEXT_LABEL[t.status]}</button>`
        : '—';
      html += `<tr>
        <td>${escHtml(t.category)}</td>
        <td><span class="badge badge-${t.status}">${t.status.replace('_', ' ')}</span></td>
        <td>${escHtml(t.opened_at)}</td>
        <td>${escHtml(t.updated_at)}</td>
        <td>${actionBtn}</td>
      </tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  // Recent Errors
  html += '<div class="section"><h2>Recent Errors</h2>';
  if (!errors.results || errors.results.length === 0) {
    html += '<div class="empty">No errors.</div>';
  } else {
    html += '<table><thead><tr><th>Code</th><th>Message</th><th>Source</th><th>Time</th></tr></thead><tbody>';
    for (const e of errors.results) {
      html += `<tr>
        <td style="font-family:monospace;font-size:12px;">${escHtml(e.error_code)}</td>
        <td>${escHtml(e.error_message)}</td>
        <td>${escHtml(e.source_entity)}</td>
        <td>${escHtml(e.created_at)}</td>
      </tr>`;
    }
    html += '</tbody></table>';
  }
  html += '</div>';

  // Inline JS for ticket status updates
  html += `<script>
async function updateTicket(ticketId, newStatus) {
  try {
    const res = await fetch('/${escHtml(slug)}/agent/ticket/' + ticketId + '/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    } else {
      alert('Error: ' + (data.error || 'Unknown error'));
    }
  } catch (err) {
    alert('Request failed: ' + err.message);
  }
}
</script>`;

  return html;
}

export async function updateTicketStatus(
  d1: D1Database, clientId: string, ticketId: string, newStatus: string,
): Promise<{ success: boolean; error?: string }> {
  // Get current status
  const ticket = await d1.prepare(
    'SELECT status FROM service_request WHERE service_request_id = ? AND client_id = ?'
  ).bind(ticketId, clientId).first<{ status: string }>();

  if (!ticket) {
    return { success: false, error: 'Ticket not found' };
  }

  // Validate transition
  const expected = VALID_TRANSITIONS[ticket.status];
  if (!expected || expected !== newStatus) {
    return { success: false, error: `Invalid transition: ${ticket.status} → ${newStatus}` };
  }

  // Update
  await d1.prepare(
    "UPDATE service_request SET status = ?, updated_at = datetime('now') WHERE service_request_id = ? AND client_id = ?"
  ).bind(newStatus, ticketId, clientId).run();

  console.log(`[830] TICKET: ${ticketId} ${ticket.status} → ${newStatus}`);
  return { success: true };
}

function card(label: string, value: string, badgeClass: string): string {
  return `<div class="card"><h3>${label}</h3><div class="value"><span class="badge ${badgeClass}" style="font-size:28px;padding:4px 16px;">${value}</span></div></div>`;
}

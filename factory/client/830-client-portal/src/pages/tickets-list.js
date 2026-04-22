// tickets-list.js — Service request ticket table
// WIRE: GET https://client-hub-api.svg-outreach.workers.dev/tickets?client_id=X

import { loadTickets, navigateTo } from '../app.js';

export async function render(container, { clientId }) {
  const tickets = await loadTickets(clientId);

  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
      <h1 class="page-title" style="margin:0;">Tickets</h1>
      <button class="btn btn-primary btn-sm" id="new-ticket-btn">+ New Ticket</button>
    </div>
    <div class="card">
      <table>
        <thead><tr>
          <th>ID</th><th>Date</th><th>Employee</th><th>Vendor / Member ID</th><th>Subject</th><th>Status</th>
        </tr></thead>
        <tbody>
          ${tickets.map(t => `
            <tr>
              <td style="font-size:11px;color:#6b7280">${t.ticket_id}</td>
              <td>${t.created_at}</td>
              <td>${t.employee_name}</td>
              <td>${t.has_card ? `${t.vendor} — ${t.member_id}` : t.vendor}</td>
              <td>${t.subject}</td>
              <td><span class="badge badge-${t.status}">${t.status}</span></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  document.getElementById('new-ticket-btn').addEventListener('click', () => {
    navigateTo(`#/${clientId}/tickets/new`);
  });
}

// employees-detail.js — Employee profile + elections + vendor IDs
// WIRE: GET https://client-hub-api.svg-outreach.workers.dev/employees/{person_id}
// WIRE: GET https://client-hub-api.svg-outreach.workers.dev/employees/{person_id}/elections
// WIRE: GET https://client-hub-api.svg-outreach.workers.dev/employees/{person_id}/vendor-ids

import { loadEmployee, loadEmployees, loadTickets, navigateTo } from '../app.js';

function showActionModal(action) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal-box">
      <h3>${action}</h3>
      <p>This action logs to employee_event table. Wire here when backend is ready.</p>
      <div class="modal-actions">
        <button class="btn btn-secondary" id="close-modal">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.querySelector('#close-modal').addEventListener('click', () => overlay.remove());
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
}

// Stub vendor IDs — will come from elections join
// WIRE: GET https://client-hub-api.svg-outreach.workers.dev/employees/{person_id}/vendor-ids
function mockVendorIds(personId) {
  const map = {
    'PER-001': [{ vendor: 'Aetna', member_id: 'AET-001-2026', has_card: true, plan: 'Medical' }],
    'PER-003': [
      { vendor: 'Aetna', member_id: 'AET-003-2026', has_card: true, plan: 'Medical' },
      { vendor: 'Delta Dental', member_id: 'DD-003-2026', has_card: true, plan: 'Dental' },
    ],
    'PER-006': [{ vendor: 'Aetna', member_id: 'AET-006-2026', has_card: true, plan: 'Medical' }],
    'PER-008': [
      { vendor: 'Aetna', member_id: 'AET-008-2026', has_card: true, plan: 'Medical' },
      { vendor: 'VSP', member_id: null, has_card: false, plan: 'Vision' },
    ],
  };
  return map[personId] || [];
}

export async function render(container, { clientId, personId }) {
  const [emp, allEmps, tickets] = await Promise.all([
    loadEmployee(personId),
    loadEmployees(clientId),
    loadTickets(clientId),
  ]);

  if (!emp) {
    container.innerHTML = '<p style="padding:24px;color:#888">Employee not found.</p>';
    return;
  }

  const dependents = allEmps.filter(e => e.parent_person_id === personId);
  const empTickets = tickets.filter(t => t.person_id === personId);
  const vendorIds = mockVendorIds(personId);
  const initials = (emp.first_name[0] + emp.last_name[0]).toUpperCase();

  container.innerHTML = `
    <div style="margin-bottom:16px;">
      <a href="#/${clientId}/employees" style="font-size:13px;color:#6b7280;text-decoration:none;">&larr; Back to Employees</a>
    </div>
    <div class="card" style="margin-bottom:20px;">
      <div class="card-body">
        <div class="profile-card">
          <div class="profile-avatar">${initials}</div>
          <div class="profile-meta">
            <h2>${emp.first_name} ${emp.last_name}</h2>
            <p>${emp.email || '—'} &bull; ${emp.cell_phone || '—'}</p>
            <p>Hired: ${emp.hire_date || '—'} &bull; Status: <span class="badge badge-${emp.status}">${emp.status}</span></p>
          </div>
        </div>
        <div class="action-row">
          <button class="btn btn-secondary btn-sm" id="btn-fire">Terminate</button>
          <button class="btn btn-secondary btn-sm" id="btn-change">Life Event Change</button>
        </div>
      </div>
    </div>

    ${dependents.length ? `
    <div class="card">
      <div class="card-header">Dependents</div>
      <table>
        <thead><tr><th>Name</th><th>Relationship</th><th>Plans</th></tr></thead>
        <tbody>${dependents.map(d => `<tr><td>${d.first_name} ${d.last_name}</td><td>${d.relationship}</td><td>${(d.plans||[]).join(', ') || '—'}</td></tr>`).join('')}</tbody>
      </table>
    </div>` : ''}

    <div class="card">
      <div class="card-header">Elections</div>
      <table>
        <thead><tr><th>Plan</th><th>Tier</th><th>Status</th></tr></thead>
        <tbody>
          ${(emp.plans || []).length ? emp.plans.map(p => `<tr><td>${p}</td><td>EE Only</td><td><span class="badge badge-active">active</span></td></tr>`).join('') : '<tr><td colspan="3" style="color:#888;padding:12px;">No elections</td></tr>'}
        </tbody>
      </table>
    </div>

    <div class="card">
      <div class="card-header">Vendor IDs</div>
      <table>
        <thead><tr><th>Plan</th><th>Vendor</th><th>Member ID</th><th>Card</th></tr></thead>
        <tbody>
          ${vendorIds.length ? vendorIds.map(v => `
            <tr>
              <td>${v.plan}</td>
              <td>${v.vendor}</td>
              <td>${v.has_card ? v.member_id : '—'}</td>
              <td>${v.has_card ? '<span class="badge badge-active">Yes</span>' : '<span class="badge badge-terminated">No</span>'}</td>
            </tr>
          `).join('') : '<tr><td colspan="4" style="color:#888;padding:12px;">No vendor IDs on file</td></tr>'}
        </tbody>
      </table>
    </div>

    <div class="card">
      <div class="card-header">Recent Tickets</div>
      <table>
        <thead><tr><th>ID</th><th>Subject</th><th>Status</th><th>Date</th></tr></thead>
        <tbody>
          ${empTickets.length ? empTickets.map(t => `<tr><td>${t.ticket_id}</td><td>${t.subject}</td><td><span class="badge badge-${t.status}">${t.status}</span></td><td>${t.created_at}</td></tr>`).join('') : '<tr><td colspan="4" style="color:#888;padding:12px;">No tickets</td></tr>'}
        </tbody>
      </table>
    </div>
  `;

  document.getElementById('btn-fire').addEventListener('click', () => showActionModal('Terminate Employee'));
  document.getElementById('btn-change').addEventListener('click', () => showActionModal('Life Event Change'));
}

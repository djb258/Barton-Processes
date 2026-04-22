// employees-list.js — Employee census table
// WIRE: GET https://client-hub-api.svg-outreach.workers.dev/employees?client_id=X

import { loadEmployees, navigateTo } from '../app.js';

function showNewHireModal() {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal-box">
      <h3>New Hire</h3>
      <p>New hire enrollment flow wires here. Will call employee onboarding intake endpoint.</p>
      <div class="modal-actions">
        <button class="btn btn-secondary" id="close-modal">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.querySelector('#close-modal').addEventListener('click', () => overlay.remove());
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
}

export async function render(container, { clientId }) {
  const all = await loadEmployees(clientId);
  const employees = all.filter(e => e.relationship === 'employee');
  const dependents = all.filter(e => e.relationship !== 'employee');

  const depCount = (personId) => dependents.filter(d => d.parent_person_id === personId).length;

  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
      <h1 class="page-title" style="margin:0;">Employees</h1>
      <button class="btn btn-primary btn-sm" id="new-hire-btn">+ New Hire</button>
    </div>
    <div class="card">
      <table>
        <thead><tr>
          <th>Name</th><th>Relationship</th><th>Hire Date</th><th>Status</th><th>Plans</th><th>Dependents</th>
        </tr></thead>
        <tbody>
          ${employees.map(e => `
            <tr data-person-id="${e.person_id}" class="employee-row">
              <td>${e.first_name} ${e.last_name}</td>
              <td>${e.relationship}</td>
              <td>${e.hire_date || '—'}</td>
              <td><span class="badge badge-${e.status}">${e.status}</span></td>
              <td>${(e.plans || []).join(', ') || '—'}</td>
              <td>${depCount(e.person_id)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  document.querySelectorAll('.employee-row').forEach(row => {
    row.addEventListener('click', () => {
      navigateTo(`#/${clientId}/employees/${row.dataset.personId}`);
    });
  });

  document.getElementById('new-hire-btn').addEventListener('click', showNewHireModal);
}

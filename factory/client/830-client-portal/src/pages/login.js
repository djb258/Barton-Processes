// login.js — Client selector / landing page
// WIRE: client list from mocks/clients.json (see app.js loadClients)

import { loadClients, navigateTo } from '../app.js';

export async function render(container) {
  const clients = await loadClients();

  container.innerHTML = `
    <div class="login-wrap">
      <h1>Client Portal</h1>
      <p>Select a client to continue, or add a new one.</p>
      <select id="client-select">
        <option value="">-- Select Client --</option>
        ${clients.map(c => `<option value="${c.client_id}">${c.company_name}</option>`).join('')}
      </select>
      <button class="btn btn-primary" id="go-btn">Open Portal</button>
      <button class="btn btn-secondary" id="new-client-btn">+ Enter New Client</button>
    </div>
  `;

  document.getElementById('go-btn').addEventListener('click', () => {
    const val = document.getElementById('client-select').value;
    if (val) navigateTo(`#/${val}/dashboard/cfo`);
  });

  document.getElementById('new-client-btn').addEventListener('click', () => {
    navigateTo('#/intake');
  });
}

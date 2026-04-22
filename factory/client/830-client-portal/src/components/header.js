// header.js — top nav bar + client switcher
// WIRE: client list loaded from mocks/clients.json (stub), will come from API

export function renderHeader(clientName) {
  const topbar = document.getElementById('topbar');
  if (!topbar) return;

  // WIRE: GET /api/clients — load client list for switcher dropdown
  import('../app.js').then(({ loadClients, navigateTo, getState }) => {
    loadClients().then(clients => {
      const state = getState();
      topbar.innerHTML = `
        <span class="brand">SVG Agency</span>
        <span class="client-name">| ${clientName || 'Select Client'}</span>
        <select id="client-switcher" title="Switch client">
          <option value="">-- Switch Client --</option>
          ${clients.map(c => `<option value="${c.client_id}" ${c.client_id === state.clientId ? 'selected' : ''}>${c.company_name}</option>`).join('')}
        </select>
        <button class="logout-btn" title="Logout (stub)">Logout</button>
      `;

      document.getElementById('client-switcher').addEventListener('change', (e) => {
        if (e.target.value) {
          navigateTo(`#/${e.target.value}/dashboard/cfo`);
        }
      });
    });
  });
}

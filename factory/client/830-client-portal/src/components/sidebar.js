// sidebar.js — left navigation
// Active link highlighting driven by current hash

export function renderSidebar(clientId, currentHash) {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  const base = clientId ? `#/${clientId}` : '';
  const h = currentHash || location.hash;

  const link = (href, label) => {
    const active = h === href || h.startsWith(href + '/') ? 'active' : '';
    return `<a href="${href}" class="${active}">${label}</a>`;
  };

  sidebar.innerHTML = `
    <nav>
      <div class="nav-group">
        <div class="nav-group-label">Dashboard</div>
        <div class="nav-sub">
          ${link(`${base}/dashboard/cfo`, 'CFO View')}
          ${link(`${base}/dashboard/ceo`, 'CEO View')}
          ${link(`${base}/dashboard/hr`, 'HR View')}
          ${link(`${base}/dashboard/underwriting`, 'Underwriting')}
          ${link(`${base}/dashboard/renewal`, 'Renewal')}
          ${link(`${base}/dashboard/advisor`, 'Advisor')}
        </div>
      </div>
      <div class="nav-group">
        ${link(`${base}/benefits`, 'Benefits')}
        ${link(`${base}/employees`, 'Employees')}
        ${link(`${base}/tickets`, 'Tickets')}
        ${link(`${base}/plans/add`, 'Add Plan')}
      </div>
    </nav>
  `;
}

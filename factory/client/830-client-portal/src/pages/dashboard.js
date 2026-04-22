// dashboard.js — 6 role-specific dashboard views
// WIRE: GET https://client-hub-api.svg-outreach.workers.dev/views/v_{role}?client_id=X

import { loadDashboard, loadClient, navigateTo } from '../app.js';

const ROLE_CONFIG = {
  cfo: {
    title: 'CFO Dashboard',
    chartDesc: 'Monthly premium spend trend (6 months)',
    tableTitle: 'Plan Cost Breakdown',
    tableHeaders: ['Benefit Class', 'Monthly Cost', '% of Total'],
    tableRows: (d) => (d.plan_breakdown || []).map(r =>
      `<tr><td>${r.benefit_class}</td><td>$${r.monthly_cost.toLocaleString()}</td><td>${r.pct}%</td></tr>`
    ).join(''),
  },
  ceo: {
    title: 'CEO Dashboard',
    chartDesc: 'Enrollment trends over time',
    tableTitle: 'Recent Activity',
    tableHeaders: ['Date', 'Event'],
    tableRows: (d) => (d.recent_activity || []).map(r =>
      `<tr><td>${r.date}</td><td>${r.event}</td></tr>`
    ).join(''),
  },
  hr: {
    title: 'HR Dashboard',
    chartDesc: 'Headcount and benefit enrollment by month',
    tableTitle: 'Upcoming Events',
    tableHeaders: ['Date', 'Event'],
    tableRows: (d) => (d.upcoming_events || []).map(r =>
      `<tr><td>${r.date}</td><td>${r.event}</td></tr>`
    ).join(''),
  },
  underwriting: {
    title: 'Underwriting Dashboard',
    chartDesc: 'Age/gender demographic band distribution',
    tableTitle: 'Enrollment by Tier',
    tableHeaders: ['Tier', 'Lives', 'Avg Age'],
    tableRows: (d) => (d.demographics || []).map(r =>
      `<tr><td>${r.tier}</td><td>${r.count}</td><td>${r.avg_age || '—'}</td></tr>`
    ).join(''),
  },
  renewal: {
    title: 'Renewal Dashboard',
    chartDesc: 'Rate change projections vs market benchmark',
    tableTitle: 'Vendor Renewal Status',
    tableHeaders: ['Vendor', 'Benefit', 'Renewal Date', 'Current Rate (EE)', 'Quote Status'],
    tableRows: (d) => (d.vendor_renewals || []).map(r =>
      `<tr><td>${r.vendor}</td><td>${r.benefit_class}</td><td>${r.renewal_date}</td><td>$${r.current_rate_ee.toFixed(2)}</td><td><span class="badge badge-pending">${r.quote_status.replace('_',' ')}</span></td></tr>`
    ).join(''),
  },
  advisor: {
    title: 'Advisor Dashboard',
    chartDesc: 'Client health score trend over 12 months',
    tableTitle: 'Activity Log',
    tableHeaders: ['Date', 'Type', 'Description'],
    tableRows: (d) => (d.activity_log || []).map(r =>
      `<tr><td>${r.date}</td><td><span class="badge badge-pending">${r.type}</span></td><td>${r.description}</td></tr>`
    ).join(''),
  },
};

export async function render(container, { sub, clientId }) {
  const role = (sub || 'cfo').toLowerCase();
  const cfg = ROLE_CONFIG[role] || ROLE_CONFIG.cfo;

  const [data, client] = await Promise.all([
    loadDashboard(role, clientId),
    clientId ? loadClient(clientId) : Promise.resolve(null),
  ]);

  const clientName = client ? client.company_name : (clientId || '');

  container.innerHTML = `
    <h1 class="page-title">${cfg.title} — ${clientName}</h1>
    <div class="kpi-grid">
      ${(data.kpis || []).map(k => `
        <div class="kpi-card">
          <div class="kpi-label">${k.label}</div>
          <div class="kpi-value">${k.value}</div>
          <div class="kpi-trend ${k.direction}">${k.trend}</div>
        </div>
      `).join('')}
    </div>
    <div class="chart-placeholder">CHART: ${cfg.chartDesc}</div>
    <div class="card">
      <div class="card-header">${cfg.tableTitle}</div>
      <table>
        <thead><tr>${cfg.tableHeaders.map(h => `<th>${h}</th>`).join('')}</tr></thead>
        <tbody>${cfg.tableRows(data)}</tbody>
      </table>
    </div>
  `;
}

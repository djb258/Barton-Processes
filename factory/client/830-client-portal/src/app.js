// ============================================================
// app.js — Client Portal 830 Router
// Hash-based SPA. Pure vanilla JS. No build step.
// ============================================================

import { renderHeader } from './components/header.js';
import { renderSidebar } from './components/sidebar.js';

// ---- State ----
const _state = { clientId: null, personId: null, clients: null };
export const getState = () => ({ ..._state });

// ---- Mock data loaders ----
// WIRE: Replace each fetch with real API call when backend is wired

export async function loadClients() {
  if (_state.clients) return _state.clients;
  // WIRE: GET https://client-hub-api.svg-outreach.workers.dev/clients
  const res = await fetch('/mocks/clients.json');
  _state.clients = await res.json();
  return _state.clients;
}

export async function loadClient(clientId) {
  const clients = await loadClients();
  return clients.find(c => c.client_id === clientId) || null;
}

export async function loadBenefitClasses() {
  // WIRE: GET https://client-hub-api.svg-outreach.workers.dev/benefit-classes
  const res = await fetch('/mocks/benefit-classes.json');
  return res.json();
}

export async function loadPlans(clientId) {
  // WIRE: GET https://client-hub-api.svg-outreach.workers.dev/plans?client_id=X
  const res = await fetch('/mocks/plans.json');
  const all = await res.json();
  return clientId ? all.filter(p => p.client_id === clientId) : all;
}

export async function loadEmployees(clientId) {
  // WIRE: GET https://client-hub-api.svg-outreach.workers.dev/employees?client_id=X
  const res = await fetch('/mocks/employees.json');
  const all = await res.json();
  return clientId ? all.filter(e => e.client_id === clientId) : all;
}

export async function loadEmployee(personId) {
  // WIRE: GET https://client-hub-api.svg-outreach.workers.dev/employees/{person_id}
  const res = await fetch('/mocks/employees.json');
  const all = await res.json();
  return all.find(e => e.person_id === personId) || null;
}

export async function loadTickets(clientId) {
  // WIRE: GET https://client-hub-api.svg-outreach.workers.dev/tickets?client_id=X
  const res = await fetch('/mocks/tickets.json');
  const all = await res.json();
  return clientId ? all.filter(t => t.client_id === clientId) : all;
}

export async function loadDashboard(role, clientId) {
  // WIRE: GET https://client-hub-api.svg-outreach.workers.dev/views/v_{role}?client_id=X
  const res = await fetch(`/mocks/dashboards/${role}.json`);
  return res.json();
}

export async function mintClient(payload) {
  // WIRE: POST https://client-mint-800.svg-outreach.workers.dev/mint
  // Currently stubbed — returns mock client_id
  console.log('STUB mintClient payload:', payload);
  const slug = payload.company_name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  return { client_id: `CLT-${slug.toUpperCase()}-2026`, status: 'minted' };
}

export async function submitBenefits(clientId, selected) {
  // WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake (table=benefit_election)
  console.log('STUB submitBenefits:', clientId, selected);
  return { status: 'ok' };
}

export async function submitPlan(clientId, plan) {
  // WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake (table=plan)
  console.log('STUB submitPlan:', clientId, plan);
  return { status: 'ok' };
}

export async function submitTicket(clientId, ticket) {
  // WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake (table=service_request)
  console.log('STUB submitTicket:', clientId, ticket);
  return { status: 'ok', ticket_id: `TKT-${Date.now()}` };
}

// ---- Navigation ----
export function navigateTo(hash) {
  location.hash = hash;
}

// ---- Router ----
function parseRoute(hash) {
  // Strips leading #/
  const path = hash.replace(/^#\//, '');
  const parts = path.split('/');

  // #/ or empty → login
  if (!path || path === '') return { route: 'login' };

  // #/intake
  if (parts[0] === 'intake') return { route: 'intake' };

  const clientId = parts[0];

  // #/{client_id}/ → default to cfo
  if (parts.length === 1 || (parts.length === 2 && parts[1] === '')) {
    return { route: 'dashboard', sub: 'cfo', clientId };
  }

  const section = parts[1];

  if (section === 'dashboard') {
    const sub = parts[2] || 'cfo';
    return { route: 'dashboard', sub, clientId };
  }
  if (section === 'benefits') return { route: 'benefits', clientId };
  if (section === 'plans' && parts[2] === 'add') return { route: 'plan-add', clientId };
  if (section === 'employees') {
    if (parts[2]) return { route: 'employee-detail', clientId, personId: parts[2] };
    return { route: 'employees', clientId };
  }
  if (section === 'tickets') {
    if (parts[2] === 'new') return { route: 'ticket-form', clientId };
    return { route: 'tickets', clientId };
  }

  return { route: 'login' };
}

async function render(hash) {
  const { route, sub, clientId, personId } = parseRoute(hash || location.hash);

  // Update state
  if (clientId) _state.clientId = clientId;
  if (personId) _state.personId = personId;

  const main = document.getElementById('main-content');
  const body = document.body;

  // Pages without nav
  if (route === 'login' || route === 'intake') {
    body.classList.add('no-nav');
  } else {
    body.classList.remove('no-nav');
  }

  // Load page module
  const pageMap = {
    'login': () => import('./pages/login.js'),
    'intake': () => import('./pages/intake.js'),
    'benefits': () => import('./pages/benefits-checkbox.js'),
    'plan-add': () => import('./pages/plan-add.js'),
    'dashboard': () => import('./pages/dashboard.js'),
    'employees': () => import('./pages/employees-list.js'),
    'employee-detail': () => import('./pages/employees-detail.js'),
    'tickets': () => import('./pages/tickets-list.js'),
    'ticket-form': () => import('./pages/tickets-form.js'),
  };

  const loader = pageMap[route];
  if (!loader) {
    main.innerHTML = '<p style="padding:24px;color:#888">404 — Route not found</p>';
    return;
  }

  const mod = await loader();

  // Render header + sidebar for nav pages
  if (route !== 'login' && route !== 'intake') {
    const client = clientId ? await loadClient(clientId) : null;
    renderHeader(client ? client.company_name : '');
    renderSidebar(clientId, hash || location.hash);
  }

  // Render page
  await mod.render(main, { route, sub, clientId, personId });
}

// ---- Boot ----
window.addEventListener('hashchange', () => render(location.hash));
window.addEventListener('DOMContentLoaded', () => {
  if (!location.hash || location.hash === '#') location.hash = '#/';
  render(location.hash);
});

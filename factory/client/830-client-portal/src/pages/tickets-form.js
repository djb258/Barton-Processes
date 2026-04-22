// tickets-form.js — New service request ticket
// WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake (table=service_request)

import { loadEmployees, loadPlans, submitTicket, navigateTo } from '../app.js';

export async function render(container, { clientId }) {
  const [employees, plans] = await Promise.all([
    loadEmployees(clientId),
    loadPlans(clientId),
  ]);

  const empOptions = employees
    .filter(e => e.relationship === 'employee')
    .map(e => `<option value="${e.person_id}" data-name="${e.first_name} ${e.last_name}">${e.first_name} ${e.last_name}</option>`)
    .join('');

  // Build vendor list with has_card flag (stub — from plans)
  // WIRE: Vendor list + member IDs from elections table
  const vendorMap = {};
  plans.forEach(p => {
    vendorMap[p.carrier] = { vendor: p.carrier, has_card: true, benefit_class: p.benefit_class };
  });
  const vendors = Object.values(vendorMap);

  container.innerHTML = `
    <div style="max-width:580px;">
      <div style="margin-bottom:12px;">
        <a href="#/${clientId}/tickets" style="font-size:13px;color:#6b7280;text-decoration:none;">&larr; Back to Tickets</a>
      </div>
      <h1 class="page-title">New Ticket</h1>
      <div class="form-wrap">
        <div class="form-row">
          <label for="employee_select">Employee *</label>
          <select id="employee_select">
            <option value="">Select employee...</option>
            ${empOptions}
          </select>
        </div>
        <div class="form-row">
          <label for="vendor_select">Vendor *</label>
          <select id="vendor_select">
            <option value="">Select vendor...</option>
            ${vendors.map(v => `<option value="${v.vendor}" data-has-card="${v.has_card}">${v.vendor} (${v.benefit_class})</option>`).join('')}
          </select>
        </div>
        <div id="member-id-notice" style="display:none;padding:10px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:6px;font-size:13px;margin-bottom:12px;"></div>
        <div class="form-row">
          <label for="subject">Subject *</label>
          <input type="text" id="subject" placeholder="Brief description of the issue" />
        </div>
        <div class="form-row">
          <label for="description">Description</label>
          <textarea id="description" placeholder="Full details..."></textarea>
        </div>
        <div style="margin-top:20px;display:flex;gap:10px;">
          <button class="btn btn-primary" id="submit-ticket">Submit Ticket</button>
          <button class="btn btn-secondary" id="cancel-ticket">Cancel</button>
        </div>
        <div id="ticket-status" style="margin-top:12px;font-size:13px;color:#6b7280;"></div>
      </div>
    </div>
  `;

  const notice = document.getElementById('member-id-notice');
  const vendorSelect = document.getElementById('vendor_select');

  vendorSelect.addEventListener('change', () => {
    const opt = vendorSelect.options[vendorSelect.selectedIndex];
    const hasCard = opt.dataset.hasCard === 'true';
    const vendor = opt.value;
    if (hasCard && vendor) {
      // WIRE: Load actual member_id from elections table by employee + vendor
      notice.style.display = 'block';
      notice.textContent = `When contacting ${vendor}, the member will give their card number: [WIRE: member_id from elections table]`;
    } else {
      notice.style.display = 'none';
    }
  });

  document.getElementById('cancel-ticket').addEventListener('click', () => navigateTo(`#/${clientId}/tickets`));

  document.getElementById('submit-ticket').addEventListener('click', async () => {
    const employeeOpt = document.getElementById('employee_select');
    const ticket = {
      person_id: employeeOpt.value,
      employee_name: employeeOpt.options[employeeOpt.selectedIndex]?.dataset?.name || '',
      vendor: vendorSelect.value,
      subject: document.getElementById('subject').value.trim(),
      description: document.getElementById('description').value.trim(),
    };

    if (!ticket.person_id || !ticket.vendor || !ticket.subject) {
      document.getElementById('ticket-status').textContent = 'Please fill in required fields.';
      return;
    }

    document.getElementById('ticket-status').textContent = 'Submitting...';
    // WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake
    const result = await submitTicket(clientId, ticket);
    document.getElementById('ticket-status').textContent = `Ticket created: ${result.ticket_id}`;
    setTimeout(() => navigateTo(`#/${clientId}/tickets`), 700);
  });
}

// benefits-checkbox.js — Which benefits does this client offer?
// WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake (table=benefit_election)

import { loadBenefitClasses, loadClient, submitBenefits, navigateTo } from '../app.js';

export async function render(container, { clientId }) {
  const [classes, client] = await Promise.all([
    loadBenefitClasses(),
    clientId ? loadClient(clientId) : Promise.resolve(null),
  ]);

  const clientName = client ? client.company_name : (clientId || 'New Client');

  container.innerHTML = `
    <div style="max-width:700px;">
      <h1 class="page-title">Benefits Selection</h1>
      <p style="margin-bottom:16px;color:#6b7280;font-size:13px;">Which benefits does <strong>${clientName}</strong> offer? Check all that apply. Pre-checks reflect proposed benefits from sales transpose.</p>
      <div class="form-wrap">
        <div class="checkbox-grid" id="benefit-checkboxes">
          ${classes.map(bc => `
            <label class="checkbox-item">
              <input type="checkbox" name="benefit" value="${bc.id}" data-name="${bc.name}" ${bc.default_offered ? 'checked' : ''} />
              ${bc.name}
            </label>
          `).join('')}
        </div>
        <div style="margin-top:20px;display:flex;gap:10px;">
          <button class="btn btn-primary" id="submit-benefits">Save & Continue &rarr;</button>
          <button class="btn btn-secondary" id="back-benefits">Back</button>
        </div>
        <div id="benefits-status" style="margin-top:12px;font-size:13px;color:#6b7280;"></div>
      </div>
    </div>
  `;

  document.getElementById('back-benefits').addEventListener('click', () => navigateTo('#/'));

  document.getElementById('submit-benefits').addEventListener('click', async () => {
    const checked = [...document.querySelectorAll('input[name="benefit"]:checked')]
      .map(el => ({ id: el.value, name: el.dataset.name }));

    document.getElementById('benefits-status').textContent = 'Saving...';

    // WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake
    await submitBenefits(clientId, checked);

    document.getElementById('benefits-status').textContent = `Saved ${checked.length} benefit classes.`;
    setTimeout(() => navigateTo(`#/${clientId}/plans/add`), 600);
  });
}

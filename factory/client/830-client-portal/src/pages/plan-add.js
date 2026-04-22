// plan-add.js — Add a plan with 4-tier rate inputs
// WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake (table=plan)

import { loadBenefitClasses, submitPlan, navigateTo } from '../app.js';

export async function render(container, { clientId }) {
  const classes = await loadBenefitClasses();

  container.innerHTML = `
    <div style="max-width:640px;">
      <h1 class="page-title">Add Plan</h1>
      <div class="form-wrap">
        <div class="form-grid-2">
          <div class="form-row">
            <label for="benefit_class">Benefit Class *</label>
            <select id="benefit_class">
              <option value="">Select...</option>
              ${classes.map(bc => `<option value="${bc.id}">${bc.name}</option>`).join('')}
            </select>
          </div>
          <div class="form-row">
            <label for="carrier">Carrier / Vendor *</label>
            <input type="text" id="carrier" placeholder="Aetna" />
          </div>
        </div>
        <div class="form-grid-2">
          <div class="form-row">
            <label for="plan_name">Plan Name *</label>
            <input type="text" id="plan_name" placeholder="Choice POS II" />
          </div>
          <div class="form-row">
            <label for="vendor_benefit_id">Vendor Benefit ID</label>
            <input type="text" id="vendor_benefit_id" placeholder="AET-CPP2-2026" />
          </div>
        </div>
        <div class="form-grid-2">
          <div class="form-row">
            <label for="effective_date">Effective Date *</label>
            <input type="date" id="effective_date" />
          </div>
          <div class="form-row">
            <label for="renewal_date">Renewal Date *</label>
            <input type="date" id="renewal_date" />
          </div>
        </div>
        <div class="form-section-title">Customer Service</div>
        <div class="form-grid-2">
          <div class="form-row">
            <label for="cs_phone">CS Phone</label>
            <input type="text" id="cs_phone" placeholder="1-800-000-0000" />
          </div>
          <div class="form-row">
            <label for="cs_email">CS Email</label>
            <input type="email" id="cs_email" placeholder="members@carrier.com" />
          </div>
        </div>
        <div class="form-section-title">Account Manager</div>
        <div class="form-row">
          <label for="am_name">Name</label>
          <input type="text" id="am_name" placeholder="Jane Smith" />
        </div>
        <div class="form-grid-2">
          <div class="form-row">
            <label for="am_phone">Phone</label>
            <input type="text" id="am_phone" />
          </div>
          <div class="form-row">
            <label for="am_email">Email</label>
            <input type="email" id="am_email" />
          </div>
        </div>
        <div class="form-section-title">Rates (4-tier — always required)</div>
        <div class="form-grid-2">
          <div class="form-row">
            <label for="rate_ee">Employee Only ($/mo)</label>
            <input type="number" id="rate_ee" placeholder="520.00" step="0.01" min="0" />
          </div>
          <div class="form-row">
            <label for="rate_ee_sp">Employee + Spouse ($/mo)</label>
            <input type="number" id="rate_ee_sp" placeholder="1040.00" step="0.01" min="0" />
          </div>
          <div class="form-row">
            <label for="rate_ee_ch">Employee + Child(ren) ($/mo)</label>
            <input type="number" id="rate_ee_ch" placeholder="988.00" step="0.01" min="0" />
          </div>
          <div class="form-row">
            <label for="rate_family">Family ($/mo)</label>
            <input type="number" id="rate_family" placeholder="1508.00" step="0.01" min="0" />
          </div>
        </div>
        <div style="margin-top:20px;display:flex;gap:10px;">
          <button class="btn btn-primary" id="submit-plan">Save Plan</button>
          <button class="btn btn-secondary" id="cancel-plan">Cancel</button>
        </div>
        <div id="plan-status" style="margin-top:12px;font-size:13px;color:#6b7280;"></div>
      </div>
    </div>
  `;

  document.getElementById('cancel-plan').addEventListener('click', () => {
    navigateTo(clientId ? `#/${clientId}/dashboard/cfo` : '#/');
  });

  document.getElementById('submit-plan').addEventListener('click', async () => {
    const plan = {
      benefit_class: document.getElementById('benefit_class').value,
      carrier: document.getElementById('carrier').value.trim(),
      plan_name: document.getElementById('plan_name').value.trim(),
      vendor_benefit_id: document.getElementById('vendor_benefit_id').value.trim(),
      effective_date: document.getElementById('effective_date').value,
      renewal_date: document.getElementById('renewal_date').value,
      cs_phone: document.getElementById('cs_phone').value.trim(),
      cs_email: document.getElementById('cs_email').value.trim(),
      am_name: document.getElementById('am_name').value.trim(),
      am_phone: document.getElementById('am_phone').value.trim(),
      am_email: document.getElementById('am_email').value.trim(),
      rate_ee: parseFloat(document.getElementById('rate_ee').value) || 0,
      rate_ee_sp: parseFloat(document.getElementById('rate_ee_sp').value) || 0,
      rate_ee_ch: parseFloat(document.getElementById('rate_ee_ch').value) || 0,
      rate_family: parseFloat(document.getElementById('rate_family').value) || 0,
    };

    document.getElementById('plan-status').textContent = 'Saving...';
    // WIRE: POST https://client-intake-810.svg-outreach.workers.dev/intake
    await submitPlan(clientId, plan);
    document.getElementById('plan-status').textContent = 'Plan saved!';
    setTimeout(() => navigateTo(clientId ? `#/${clientId}/dashboard/cfo` : '#/'), 600);
  });
}

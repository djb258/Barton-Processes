// intake.js — New client hand-entry form
// WIRE: POST https://client-mint-800.svg-outreach.workers.dev/mint

import { mintClient, navigateTo } from '../app.js';

export async function render(container) {
  container.innerHTML = `
    <div style="max-width:600px;margin:40px auto;">
      <h1 class="page-title">New Client Intake</h1>
      <div class="form-wrap">
        <div class="form-row">
          <label for="company_name">Company Name *</label>
          <input type="text" id="company_name" placeholder="Acme Corp" required />
        </div>
        <div class="form-row">
          <label for="ein">EIN *</label>
          <input type="text" id="ein" placeholder="12-3456789" required />
        </div>
        <div class="form-grid-2">
          <div class="form-row">
            <label for="domicile_state">Domicile State *</label>
            <select id="domicile_state">
              <option value="">Select state...</option>
              ${['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'].map(s => `<option>${s}</option>`).join('')}
            </select>
          </div>
          <div class="form-row">
            <label for="effective_date">Effective Date *</label>
            <input type="date" id="effective_date" />
          </div>
        </div>
        <div class="form-row">
          <label for="sovereign_id">CL Sovereign ID (optional)</label>
          <input type="text" id="sovereign_id" placeholder="cl-acme-2026" />
          <div class="form-hint">Leave blank to auto-generate from company name.</div>
        </div>
        <div style="margin-top:20px;display:flex;gap:10px;">
          <button class="btn btn-primary" id="submit-intake">Create Client &rarr;</button>
          <button class="btn btn-secondary" id="cancel-intake">Cancel</button>
        </div>
        <div id="intake-status" style="margin-top:12px;font-size:13px;color:#6b7280;"></div>
      </div>
    </div>
  `;

  document.getElementById('cancel-intake').addEventListener('click', () => navigateTo('#/'));

  document.getElementById('submit-intake').addEventListener('click', async () => {
    const payload = {
      company_name: document.getElementById('company_name').value.trim(),
      ein: document.getElementById('ein').value.trim(),
      domicile_state: document.getElementById('domicile_state').value,
      effective_date: document.getElementById('effective_date').value,
      sovereign_id: document.getElementById('sovereign_id').value.trim() || null,
    };

    if (!payload.company_name || !payload.ein || !payload.domicile_state) {
      document.getElementById('intake-status').textContent = 'Please fill in required fields.';
      return;
    }

    document.getElementById('intake-status').textContent = 'Creating client...';

    // WIRE: POST https://client-mint-800.svg-outreach.workers.dev/mint
    const result = await mintClient(payload);
    document.getElementById('intake-status').textContent = `Client created: ${result.client_id}`;

    setTimeout(() => navigateTo(`#/${result.client_id}/benefits`), 800);
  });
}

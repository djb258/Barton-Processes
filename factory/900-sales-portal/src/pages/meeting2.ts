/**
 * 900 — Meeting 2: Insurance Education (READ-ONLY)
 *
 * Slide deck presentation + Monte Carlo simulation results.
 * Monte Carlo data populated by future simulation engine.
 */

import { escHtml } from '../templates/layout';

export async function renderMeeting2(d1: D1Database, salesId: string): Promise<string> {
  const factfinder = await d1.prepare(
    'SELECT * FROM sales_factfinder WHERE sales_id = ?'
  ).bind(salesId).first<{
    legal_name: string; employee_count: number | null; current_carrier: string | null;
    funding_type: string | null; annual_premium: number | null; renewal_date: string | null;
    stop_loss_carrier: string | null; stop_loss_deductible: number | null;
  }>();

  const insurance = await d1.prepare(
    'SELECT * FROM sales_insurance WHERE sales_id = ?'
  ).bind(salesId).first<{
    monte_carlo_run_id: string | null; projected_claims: number | null;
    confidence_low: number | null; confidence_high: number | null;
    recommended_funding: string | null; simulation_date: string | null;
    meeting_status: string;
  }>();

  let html = '';

  // Slide 1: Current Situation Summary (from Fact Finder)
  html += `<div class="slide" id="slide-1">
    <h2>Current Benefits Situation</h2>
    <table>
      <tr><th style="width:200px;">Company</th><td>${escHtml(factfinder?.legal_name || '—')}</td></tr>
      <tr><th>Employees</th><td>${factfinder?.employee_count ?? '—'}</td></tr>
      <tr><th>Current Carrier</th><td>${escHtml(factfinder?.current_carrier || '—')}</td></tr>
      <tr><th>Funding Type</th><td>${escHtml(factfinder?.funding_type || '—')}</td></tr>
      <tr><th>Annual Premium</th><td>${factfinder?.annual_premium ? '$' + factfinder.annual_premium.toLocaleString() : '—'}</td></tr>
      <tr><th>Renewal Date</th><td>${escHtml(factfinder?.renewal_date || '—')}</td></tr>
      <tr><th>Stop-Loss Carrier</th><td>${escHtml(factfinder?.stop_loss_carrier || '—')}</td></tr>
      <tr><th>Stop-Loss Deductible</th><td>${factfinder?.stop_loss_deductible ? '$' + factfinder.stop_loss_deductible.toLocaleString() : '—'}</td></tr>
    </table>
  </div>`;

  // Slide 2: Monte Carlo Results
  html += `<div class="slide" id="slide-2">
    <h2>Monte Carlo Simulation</h2>`;

  if (insurance?.monte_carlo_run_id) {
    html += `<div class="cards">
      ${mcCard('Projected Annual Claims', insurance.projected_claims != null ? '$' + insurance.projected_claims.toLocaleString() : '—')}
      ${mcCard('90% Confidence Range', insurance.confidence_low != null && insurance.confidence_high != null ? '$' + insurance.confidence_low.toLocaleString() + ' — $' + insurance.confidence_high.toLocaleString() : '—')}
      ${mcCard('Recommended Funding', escHtml(insurance.recommended_funding || '—'))}
      ${mcCard('Simulation Date', escHtml(insurance.simulation_date || '—'))}
    </div>
    <p style="color:var(--muted);font-size:13px;margin-top:16px;">Run ID: ${escHtml(insurance.monte_carlo_run_id)}</p>`;
  } else {
    html += '<div class="empty">Monte Carlo simulation has not been run yet.<br>Run the simulation engine to populate these results.</div>';
  }
  html += '</div>';

  // Slide 3: Insurance Education Content (placeholder for slide deck)
  html += `<div class="slide" id="slide-3">
    <h2>Insurance Education</h2>
    <p>Presentation slides will be rendered here.</p>
    <p style="margin-top:16px;color:var(--muted);">Topics covered:</p>
    <ul style="margin-top:8px;margin-left:24px;color:var(--muted);">
      <li>Fully insured vs. level funded vs. self-funded</li>
      <li>Stop-loss explained — specific and aggregate</li>
      <li>Claims data analysis</li>
      <li>Risk corridor and how it protects the employer</li>
      <li>Total cost of risk vs. total cost of premium</li>
    </ul>
  </div>`;

  // Slide navigation
  html += `<div class="slide-nav">
    <button class="btn btn-secondary" onclick="prevSlide()">Previous</button>
    <span id="slide-counter" style="color:var(--muted);">Slide 1 of 3</span>
    <button class="btn btn-primary" onclick="nextSlide()">Next</button>
  </div>`;

  html += `<script>
let currentSlide = 1;
const totalSlides = 3;

function showSlide(n) {
  for (let i = 1; i <= totalSlides; i++) {
    document.getElementById('slide-' + i).style.display = i === n ? 'block' : 'none';
  }
  document.getElementById('slide-counter').textContent = 'Slide ' + n + ' of ' + totalSlides;
  currentSlide = n;
}

function nextSlide() { if (currentSlide < totalSlides) showSlide(currentSlide + 1); }
function prevSlide() { if (currentSlide > 1) showSlide(currentSlide - 1); }

showSlide(1);
</script>`;

  return html;
}

function mcCard(label: string, value: string): string {
  return `<div class="card"><h3>${label}</h3><div class="value" style="font-size:22px;">${value}</div></div>`;
}

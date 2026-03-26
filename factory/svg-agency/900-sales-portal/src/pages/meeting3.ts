/**
 * 900 — Meeting 3: Systems Education (READ-ONLY)
 *
 * Slide deck presenting SVG Agency systems and solutions.
 */

import { escHtml } from '../templates/layout';

export async function renderMeeting3(d1: D1Database, salesId: string): Promise<string> {
  const systems = await d1.prepare(
    'SELECT * FROM sales_systems WHERE sales_id = ?'
  ).bind(salesId).first<{
    meeting_status: string; notes: string | null;
  }>();

  let html = '';

  // Slide 1: Our Approach
  html += `<div class="slide" id="slide-1">
    <h2>Our Approach</h2>
    <p>How SVG Agency manages your employee benefits program differently.</p>
    <ul style="margin-top:24px;margin-left:24px;font-size:18px;line-height:2.2;">
      <li>Data-driven decision making — not guesswork</li>
      <li>Continuous monitoring, not annual check-ins</li>
      <li>Full transparency on costs and claims</li>
      <li>Technology-first service delivery</li>
    </ul>
  </div>`;

  // Slide 2: Technology Platform
  html += `<div class="slide" id="slide-2">
    <h2>Technology Platform</h2>
    <p>Purpose-built systems for benefits administration.</p>
    <div class="cards" style="margin-top:24px;">
      ${sysCard('Client Portal', 'Real-time access to your benefits data, enrollment, and service tickets.')}
      ${sysCard('Claims Analytics', 'Monte Carlo simulations, trend analysis, and predictive modeling.')}
      ${sysCard('Vendor Management', 'Automated carrier communications, billing reconciliation, and compliance.')}
      ${sysCard('Employee Self-Service', 'Digital enrollment, plan comparisons, and benefit education.')}
    </div>
  </div>`;

  // Slide 3: Service Model
  html += `<div class="slide" id="slide-3">
    <h2>Service Model</h2>
    <p>What working with us looks like day-to-day.</p>
    <table style="margin-top:24px;">
      <tr><th>Service</th><th>Frequency</th><th>How</th></tr>
      <tr><td>Benefits Review</td><td>Quarterly</td><td>Data-driven report + meeting</td></tr>
      <tr><td>Claims Monitoring</td><td>Monthly</td><td>Automated alerts + dashboard</td></tr>
      <tr><td>Renewal Management</td><td>Annual</td><td>Market analysis + negotiation</td></tr>
      <tr><td>Employee Support</td><td>Ongoing</td><td>Portal + dedicated service team</td></tr>
      <tr><td>Compliance</td><td>Ongoing</td><td>Automated monitoring + updates</td></tr>
    </table>
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

function sysCard(title: string, desc: string): string {
  return `<div class="card"><h3 style="color:var(--text);font-size:16px;text-transform:none;letter-spacing:0;">${title}</h3><p style="font-size:14px;color:var(--muted);margin-top:8px;">${desc}</p></div>`;
}

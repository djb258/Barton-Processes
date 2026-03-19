/**
 * 900 — Meeting 1: Fact Finder (READ-WRITE)
 *
 * Pre-populates form from outreach 5 sub-hubs (via outreach_snapshot).
 * Dave validates with prospect, fills gaps, saves to sales_factfinder.
 */

import { escHtml } from '../templates/layout';

interface OutreachSnapshot {
  company_name: string | null; postal_code: string | null; city: string | null;
  state: string | null; industry: string | null; employees: number | null;
  company_domain: string | null; ein: string | null; filing_present: number;
  funding_type: string | null; broker_or_advisor: string | null; carrier: string | null;
  renewal_month: number | null; ceo_name: string | null; ceo_title: string | null;
  ceo_email: string | null; ceo_linkedin: string | null; cfr_name: string | null;
  cfr_title: string | null; cfr_email: string | null; cfr_linkedin: string | null;
  hr_name: string | null; hr_title: string | null; hr_email: string | null;
  hr_linkedin: string | null; blog_url: string | null; blog_context: string | null;
  bit_score: number | null; bit_tier: string | null; signal_count: number | null;
}

interface FactFinder {
  factfinder_id: string; legal_name: string | null; domicile_state: string | null;
  ein: string | null; employee_count: number | null; industry: string | null;
  current_carrier: string | null; current_broker: string | null; renewal_date: string | null;
  funding_type: string | null; annual_premium: number | null; stop_loss_carrier: string | null;
  stop_loss_deductible: number | null; pain_points: string | null;
  decision_timeline: string | null; decision_makers: string | null; notes: string | null;
  meeting_status: string;
}

export async function renderMeeting1(d1: D1Database, salesId: string, slug: string): Promise<string> {
  const snapshot = await d1.prepare(
    'SELECT * FROM outreach_snapshot WHERE sales_id = ?'
  ).bind(salesId).first<OutreachSnapshot>();

  const existing = await d1.prepare(
    'SELECT * FROM sales_factfinder WHERE sales_id = ?'
  ).bind(salesId).first<FactFinder>();

  // Use existing data if saved, otherwise pre-populate from snapshot
  const data = existing || snapshot;

  let html = '';

  // Outreach Intelligence Summary (read-only cards)
  if (snapshot) {
    html += '<div class="section"><h2>Outreach Intelligence</h2>';
    html += '<div class="cards">';
    html += card('BIT Score', snapshot.bit_score != null ? `${snapshot.bit_score.toFixed(1)} (${snapshot.bit_tier || '—'})` : '—');
    html += card('DOL Filing', snapshot.filing_present ? 'Yes' : 'No');
    html += card('Employees', String(snapshot.employees ?? '—'));
    html += card('Signals', String(snapshot.signal_count ?? 0));
    html += '</div>';

    // Contacts from outreach
    html += '<div class="cards">';
    html += contactCard('CEO', snapshot.ceo_name, snapshot.ceo_email, snapshot.ceo_linkedin);
    html += contactCard('CFO/CFR', snapshot.cfr_name, snapshot.cfr_email, snapshot.cfr_linkedin);
    html += contactCard('HR', snapshot.hr_name, snapshot.hr_email, snapshot.hr_linkedin);
    html += '</div>';
    html += '</div>';
  }

  // Fact Finder Form
  html += `<div class="section"><h2>Fact Finder Form</h2>
  <form id="factfinder-form">
    <div class="card">
      <h3>Company Information</h3>
      <div class="form-row">
        ${field('legal_name', 'Legal Name', existing?.legal_name || snapshot?.company_name || '')}
        ${field('domicile_state', 'State', existing?.domicile_state || snapshot?.state || '')}
        ${field('ein', 'EIN', existing?.ein || snapshot?.ein || '')}
      </div>
      <div class="form-row">
        ${field('employee_count', 'Employee Count', String(existing?.employee_count ?? snapshot?.employees ?? ''), 'number')}
        ${field('industry', 'Industry', existing?.industry || snapshot?.industry || '')}
      </div>
    </div>

    <div class="card">
      <h3>Current Benefits</h3>
      <div class="form-row">
        ${field('current_carrier', 'Current Carrier', existing?.current_carrier || snapshot?.carrier || '')}
        ${field('current_broker', 'Current Broker', existing?.current_broker || snapshot?.broker_or_advisor || '')}
        ${field('renewal_date', 'Renewal Date', existing?.renewal_date || (snapshot?.renewal_month ? `2026-${String(snapshot.renewal_month).padStart(2, '0')}-01` : ''), 'date')}
      </div>
      <div class="form-row">
        ${field('funding_type', 'Funding Type', existing?.funding_type || snapshot?.funding_type || '')}
        ${field('annual_premium', 'Annual Premium', String(existing?.annual_premium ?? ''), 'number')}
      </div>
      <div class="form-row">
        ${field('stop_loss_carrier', 'Stop-Loss Carrier', existing?.stop_loss_carrier || '')}
        ${field('stop_loss_deductible', 'Stop-Loss Deductible', String(existing?.stop_loss_deductible ?? ''), 'number')}
      </div>
    </div>

    <div class="card">
      <h3>Discovery</h3>
      ${textarea('pain_points', 'Pain Points', existing?.pain_points || '')}
      <div class="form-row">
        ${field('decision_timeline', 'Decision Timeline', existing?.decision_timeline || '')}
        ${field('decision_makers', 'Decision Makers', existing?.decision_makers || '')}
      </div>
      ${textarea('notes', 'Notes', existing?.notes || '')}
    </div>

    <div style="display:flex;gap:12px;margin-top:16px;">
      <button type="submit" class="btn btn-primary">Save Fact Finder</button>
      <button type="button" class="btn btn-secondary" onclick="saveDraft()">Save Draft</button>
    </div>
  </form>
  </div>`;

  // Form submission JS
  html += `<script>
document.getElementById('factfinder-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  await saveForm('completed');
});

async function saveDraft() {
  await saveForm('draft');
}

async function saveForm(status) {
  const form = document.getElementById('factfinder-form');
  const data = {};
  form.querySelectorAll('input, textarea, select').forEach(el => {
    data[el.name] = el.type === 'number' ? (el.value ? parseFloat(el.value) : null) : el.value;
  });
  data.meeting_status = status;

  try {
    const res = await fetch('/sales/${escHtml(slug)}/meeting1/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.success) {
      alert(status === 'completed' ? 'Fact Finder saved!' : 'Draft saved.');
      if (status === 'completed') window.location.reload();
    } else {
      alert('Error: ' + (result.error || 'Unknown'));
    }
  } catch (err) {
    alert('Save failed: ' + err.message);
  }
}
</script>`;

  return html;
}

export async function saveFactFinder(
  d1: D1Database, salesId: string, data: Record<string, unknown>,
): Promise<{ success: boolean; error?: string }> {
  const id = crypto.randomUUID();
  const status = (data.meeting_status as string) || 'draft';

  try {
    // Upsert — replace existing if present
    await d1.prepare('DELETE FROM sales_factfinder WHERE sales_id = ?').bind(salesId).run();
    await d1.prepare(`
      INSERT INTO sales_factfinder (
        factfinder_id, sales_id, legal_name, domicile_state, ein, employee_count, industry,
        current_carrier, current_broker, renewal_date, funding_type, annual_premium,
        stop_loss_carrier, stop_loss_deductible, pain_points, decision_timeline,
        decision_makers, notes, meeting_status, completed_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      id, salesId, data.legal_name ?? null, data.domicile_state ?? null, data.ein ?? null,
      data.employee_count ?? null, data.industry ?? null, data.current_carrier ?? null,
      data.current_broker ?? null, data.renewal_date ?? null, data.funding_type ?? null,
      data.annual_premium ?? null, data.stop_loss_carrier ?? null, data.stop_loss_deductible ?? null,
      data.pain_points ?? null, data.decision_timeline ?? null, data.decision_makers ?? null,
      data.notes ?? null, status, status === 'completed' ? new Date().toISOString() : null,
    ).run();

    // Advance phase if completed
    if (status === 'completed') {
      await d1.prepare(
        "UPDATE sales_state SET current_phase = 'insurance', updated_at = datetime('now') WHERE sales_id = ?"
      ).bind(salesId).run();
    }

    return { success: true };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return { success: false, error: msg };
  }
}

function field(name: string, label: string, value: string, type: string = 'text'): string {
  return `<div class="form-group"><label for="${name}">${label}</label><input type="${type}" id="${name}" name="${name}" value="${escHtml(value)}"></div>`;
}

function textarea(name: string, label: string, value: string): string {
  return `<div class="form-group"><label for="${name}">${label}</label><textarea id="${name}" name="${name}">${escHtml(value)}</textarea></div>`;
}

function card(label: string, value: string): string {
  return `<div class="card"><h3>${label}</h3><div class="value">${value}</div></div>`;
}

function contactCard(role: string, name: string | null, email: string | null, linkedin: string | null): string {
  return `<div class="card"><h3>${role}</h3><div style="font-size:15px;font-weight:600;">${escHtml(name || '—')}</div><div style="font-size:13px;color:var(--muted);">${escHtml(email || 'No email')}</div>${linkedin ? `<div style="font-size:12px;"><a href="${escHtml(linkedin)}" target="_blank" style="color:var(--accent);">LinkedIn</a></div>` : ''}</div>`;
}

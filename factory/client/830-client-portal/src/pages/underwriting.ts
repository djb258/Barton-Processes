/**
 * 830 — Underwriting Page
 *
 * Employee census summary + compliance items. Coverage tiers STUB.
 * Read-only. Audience: stop-loss carrier underwriter.
 */

import { escHtml, badge } from '../templates/layout';
import type { ClientContext } from '../resolve';

export async function renderUnderwriting(client: ClientContext, d1: D1Database): Promise<string> {
  const [census, compliance] = await Promise.all([
    d1.prepare(`
      SELECT
        COUNT(*) as total,
        SUM(CASE WHEN employment_status='active' THEN 1 ELSE 0 END) as active,
        SUM(CASE WHEN employment_status='terminated' THEN 1 ELSE 0 END) as terminated,
        SUM(CASE WHEN employment_status='leave' THEN 1 ELSE 0 END) as on_leave
      FROM client_employees WHERE client_id=?
    `).bind(client.client_id).first<{ total: number; active: number; terminated: number; on_leave: number }>(),

    d1.prepare(
      'SELECT self_insured, erisa_applicable, aca_applicable, plan_year_start, plan_year_end, required_forms FROM client_compliance WHERE client_id=?'
    ).bind(client.client_id).first<{
      self_insured: number | null; erisa_applicable: number | null; aca_applicable: number | null;
      plan_year_start: string | null; plan_year_end: string | null; required_forms: string | null;
    }>(),
  ]);

  let html = '';

  // ── Census stat row ───────────────────────────────────────────────────────
  html += '<div class="stat-row">';
  html += stat('Total employees', String(census?.total ?? 0));
  html += stat('Active', String(census?.active ?? 0));
  html += stat('Terminated', String(census?.terminated ?? 0));
  html += stat('On leave', String(census?.on_leave ?? 0));
  if (client.employee_count != null) {
    html += stat('Reported headcount', String(client.employee_count));
  }
  html += '</div>';

  // ── Compliance Configuration ──────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Compliance Configuration</h2></div>';
  if (!compliance) {
    html += '<div class="empty">No compliance configuration on record.</div>';
  } else {
    html += '<div class="info-grid">';
    html += infoItem('Self-insured', compliance.self_insured ? 'Yes' : 'No');
    html += infoItem('ERISA applicable', compliance.erisa_applicable ? 'Yes' : 'No');
    html += infoItem('ACA applicable', compliance.aca_applicable ? 'Yes' : 'No');
    if (compliance.plan_year_start) html += infoItem('Plan year start', escHtml(compliance.plan_year_start.slice(0, 10)));
    if (compliance.plan_year_end) html += infoItem('Plan year end', escHtml(compliance.plan_year_end.slice(0, 10)));
    if (compliance.required_forms) {
      try {
        const forms: string[] = JSON.parse(compliance.required_forms);
        if (forms.length > 0) html += infoItem('Required forms', escHtml(forms.join(', ')));
      } catch { /* malformed JSON — skip */ }
    }
    html += '</div>';
  }
  html += '</div>';

  // ── Department Breakdown — STUB ───────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Active Employees by Department</h2></div>';
  html += `<div class="stub-panel">
    <div class="stub-icon">🏢</div>
    <div class="stub-title">Department breakdown coming soon</div>
    <div class="stub-body">Department-level census will appear here once department data is loaded into the employee records.</div>
  </div>`;
  html += '</div>';

  // ── Coverage Tiers — STUB ─────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Coverage Tier Distribution</h2></div>';
  html += `<div class="stub-panel">
    <div class="stub-icon">📊</div>
    <div class="stub-title">Coverage tier detail coming soon</div>
    <div class="stub-body">Employee/employer/dependent tier distribution and enrollment counts will appear here once plan elections are configured.</div>
  </div>`;
  html += '</div>';

  // ── Enrolled Plans — STUB ─────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Current Plans</h2></div>';
  html += `<div class="stub-panel">
    <div class="stub-icon">🗂</div>
    <div class="stub-title">Plan detail coming soon</div>
    <div class="stub-body">Carrier, effective dates, and rate schedules will appear here once plans are loaded.</div>
  </div>`;
  html += '</div>';

  return html;
}

function stat(label: string, value: string): string {
  return `<div class="stat"><div class="stat-value">${escHtml(value)}</div><div class="stat-label">${escHtml(label)}</div></div>`;
}

function infoItem(label: string, value: string): string {
  return `<div class="info-item"><span class="info-label">${escHtml(label)}</span><span class="info-value">${value}</span></div>`;
}

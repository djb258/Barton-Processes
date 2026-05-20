/**
 * 830 — Client Portal: CEO / Overview page
 *
 * Editorial composition (rebuild 2026-05-13):
 *   - Lede paragraph framing the relationship at-a-glance.
 *   - Headline figures (employees · tickets · interactions) in editorial pull-quote treatment.
 *   - Client dossier as KV grid (industry, EIN, headcount, onboarded date).
 *   - Activity panel — ticket queue + recent touchpoints, hairline-ruled.
 *   - Audience: client CEO on a 27" monitor, two-second credibility check.
 */

import { escHtml, badge, figure, kv, sectionHeader } from '../templates/layout';
import type { ClientContext } from '../resolve';

export async function renderCeo(client: ClientContext, d1: D1Database): Promise<string> {
  const [employees, contacts, vendors, interactions, tickets] = await Promise.all([
    d1.prepare(
      "SELECT COUNT(*) as total, SUM(CASE WHEN employment_status='active' THEN 1 ELSE 0 END) as active FROM client_employees WHERE client_id=?"
    ).bind(client.client_id).first<{ total: number; active: number }>(),

    d1.prepare(
      "SELECT COUNT(*) as cnt FROM client_contacts WHERE client_id=?"
    ).bind(client.client_id).first<{ cnt: number }>(),

    d1.prepare(
      "SELECT COUNT(*) as cnt FROM client_vendors WHERE client_id=?"
    ).bind(client.client_id).first<{ cnt: number }>(),

    d1.prepare(
      "SELECT resolved, COUNT(*) as cnt FROM client_interactions WHERE client_id=? GROUP BY resolved"
    ).bind(client.client_id).all<{ resolved: number; cnt: number }>(),

    d1.prepare(
      "SELECT status, COUNT(*) as cnt FROM client_tickets WHERE client_id=? GROUP BY status"
    ).bind(client.client_id).all<{ status: string; cnt: number }>(),
  ]);

  const iOpen = interactions.results?.find(r => r.resolved === 0)?.cnt ?? 0;
  const iResolved = interactions.results?.find(r => r.resolved === 1)?.cnt ?? 0;
  const tOpen = (tickets.results?.find(r => r.status === 'open')?.cnt ?? 0)
    + (tickets.results?.find(r => r.status === 'in_progress')?.cnt ?? 0);
  const tResolved = tickets.results?.find(r => r.status === 'resolved')?.cnt ?? 0;
  const tTotal = (tickets.results ?? []).reduce((s, r) => s + r.cnt, 0);

  // ── Lede ──────────────────────────────────────────────────────────────────
  const name = client.label_override || client.company_name;
  const onboardYear = client.onboarded_at ? client.onboarded_at.slice(0, 4) : null;
  const ledeBits: string[] = [];
  if (employees?.active) ledeBits.push(`${employees.active} active employees on the roster`);
  else if (client.employee_count) ledeBits.push(`${client.employee_count} employees on file`);
  if (vendors && vendors.cnt) ledeBits.push(`${vendors.cnt} vendor relationship${vendors.cnt === 1 ? '' : 's'}`);
  if (tOpen > 0) ledeBits.push(`${tOpen} service ticket${tOpen === 1 ? '' : 's'} open`);
  const ledeTail = ledeBits.length ? ledeBits.join(' · ') : 'No activity on record yet.';
  const lede = `${escHtml(name)} entered ${escHtml(client.lifecycle_stage)}${onboardYear ? ` in ${onboardYear}` : ''}. ${escHtml(ledeTail)}.`;

  let html = `<p class="page-lede">${lede}</p>`;

  // ── Headline figures ──────────────────────────────────────────────────────
  html += '<div class="figure-row" style="margin-top: var(--sp-3xl);">';
  html += figure('Employees', employees?.active ?? 0, employees?.total && employees.total !== (employees.active ?? 0) ? `${employees.total} total on file` : undefined);
  html += figure('Vendor relationships', vendors?.cnt ?? 0);
  html += figure('Open tickets', tOpen, tTotal ? `${tResolved} resolved · ${tTotal} total` : undefined);
  html += figure('Open interactions', iOpen, iResolved ? `${iResolved} resolved` : undefined);
  html += '</div>';

  // ── Client dossier ────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += sectionHeader('§01', 'Client dossier');
  html += '<div class="kv-list">';
  html += kv('Status', badge(client.lifecycle_stage));
  html += kv('Industry', escHtml(client.industry || '—'));
  html += kv('Employees on file', String(employees?.total ?? client.employee_count ?? '—'));
  html += kv('EIN', escHtml(client.ein || '—'));
  html += kv('Onboarded', client.onboarded_at ? escHtml(client.onboarded_at.slice(0, 10)) : '<span class="info-value--muted">Not recorded</span>');
  html += kv('Primary contacts', String(contacts?.cnt ?? 0));
  html += '</div>';
  html += '</div>';

  // ── Service ticket activity ───────────────────────────────────────────────
  html += '<div class="section">';
  html += sectionHeader('§02', 'Service ticket queue', tTotal ? `${tTotal} total` : 'none');
  if (!tickets.results || tickets.results.length === 0) {
    html += '<div class="empty">No service tickets have been filed for this client.</div>';
  } else {
    html += '<div class="table-wrap"><table>';
    html += '<thead><tr><th>Status</th><th class="num">Count</th><th>Share</th></tr></thead><tbody>';
    for (const t of tickets.results) {
      const pct = tTotal ? Math.round((t.cnt / tTotal) * 100) : 0;
      html += `<tr><td>${badge(t.status)}</td><td class="num">${t.cnt}</td><td><span style="display:inline-block;width:${pct}%;max-width:100%;height:6px;background:var(--accent);vertical-align:middle;margin-right:8px"></span><span style="font-family:var(--mono);font-size:12px;color:var(--ink-3)">${pct}%</span></td></tr>`;
    }
    html += '</tbody></table></div>';
  }
  html += '</div>';

  // ── Touchpoint summary ────────────────────────────────────────────────────
  if (iOpen + iResolved > 0) {
    html += '<div class="section">';
    html += sectionHeader('§03', 'Touchpoint summary', `${iOpen + iResolved} on record`);
    html += '<div class="figure-row">';
    html += figure('Open', iOpen);
    html += figure('Resolved', iResolved);
    html += figure('Total', iOpen + iResolved);
    html += '</div>';
    html += '</div>';
  }

  return html;
}

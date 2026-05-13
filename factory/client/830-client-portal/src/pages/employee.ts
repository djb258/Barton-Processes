/**
 * 830 — Employee Portal
 *
 * (a) Benefits display — STUB.
 * (b) Ticket submission form — WORKING.
 * Write path: POST /:slug/employee/ticket → validate → INSERT client_tickets.
 * Audience: client employees.
 */

import { escHtml, badge } from '../templates/layout';
import type { ClientContext } from '../resolve';

const CATEGORIES = ['benefits', 'payroll', 'onboarding', 'offboarding', 'compliance', 'general'] as const;
const PRIORITIES = ['low', 'normal', 'high', 'urgent'] as const;

type Category = typeof CATEGORIES[number];
type Priority = typeof PRIORITIES[number];

export interface TicketFormData {
  full_name?: string;
  email?: string;
  category?: string;
  subject?: string;
  description?: string;
  priority?: string;
}

export interface TicketFormResult {
  success?: boolean;
  errors?: Record<string, string>;
  prefill?: TicketFormData;
}

export function renderEmployee(
  client: ClientContext,
  result?: TicketFormResult,
): string {
  const errors = result?.errors ?? {};
  const prefill = result?.prefill ?? {};

  let html = '';

  // ── Benefits — STUB ───────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Your Benefits</h2></div>';
  html += `<div class="stub-panel">
    <div class="stub-icon">🏥</div>
    <div class="stub-title">Benefits portal coming soon</div>
    <div class="stub-body">Your current benefit elections, coverage details, and plan documents will appear here once your employer configures the portal.</div>
  </div>`;
  html += '</div>';

  // ── Success alert ─────────────────────────────────────────────────────────
  if (result?.success) {
    html += `<div class="alert alert-success">Your ticket was submitted successfully. A member of our team will follow up with you shortly.</div>`;
  }

  // ── Ticket Form ───────────────────────────────────────────────────────────
  html += '<div class="section">';
  html += '<div class="section-header"><h2>Submit a Ticket</h2></div>';
  html += `<form class="form-card" method="POST" action="/${escHtml(client.slug)}/employee/ticket">`;

  // Name + Email
  html += '<div class="form-grid">';
  html += formGroup(
    'full_name', 'Your name', 'text', prefill.full_name ?? '',
    errors.full_name, 'Full name', true,
  );
  html += formGroup(
    'email', 'Email address', 'email', prefill.email ?? '',
    errors.email, 'you@company.com', true,
  );
  html += '</div>';

  // Category + Priority
  html += '<div class="form-grid">';
  html += selectGroup('category', 'Category', CATEGORIES, prefill.category, errors.category, true);
  html += selectGroup('priority', 'Priority', PRIORITIES, prefill.priority ?? 'normal', errors.priority, false);
  html += '</div>';

  // Subject
  html += formGroup(
    'subject', 'Subject', 'text', prefill.subject ?? '',
    errors.subject, 'Brief description of your issue', true,
  );

  // Description
  html += `<div class="form-group${errors.description ? ' form-group--error' : ''}">`;
  html += `<label for="description">Details <span aria-hidden="true">*</span></label>`;
  html += `<textarea id="description" name="description" rows="5" placeholder="Please describe your issue in detail…" required>${escHtml(prefill.description ?? '')}</textarea>`;
  if (errors.description) html += `<span class="form-error">${escHtml(errors.description)}</span>`;
  html += '</div>';

  html += '<div style="display:flex;justify-content:flex-end;margin-top:var(--sp-4)">';
  html += '<button type="submit" class="btn btn-primary">Submit ticket</button>';
  html += '</div>';

  html += '</form>';
  html += '</div>';

  return html;
}

/**
 * Write path — validate form data and INSERT into client_tickets.
 * Returns success or validation errors.
 */
export async function submitTicket(
  d1: D1Database,
  clientId: string,
  formData: TicketFormData,
): Promise<TicketFormResult> {
  const errors: Record<string, string> = {};

  const full_name = (formData.full_name ?? '').trim();
  const email = (formData.email ?? '').trim();
  const category = (formData.category ?? '').trim();
  const subject = (formData.subject ?? '').trim();
  const description = (formData.description ?? '').trim();
  const priority = (formData.priority ?? 'normal').trim();

  if (!full_name) errors.full_name = 'Name is required.';
  else if (full_name.length > 200) errors.full_name = 'Name too long (max 200 chars).';

  if (!email) errors.email = 'Email is required.';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = 'Enter a valid email address.';
  else if (email.length > 320) errors.email = 'Email too long.';

  if (!CATEGORIES.includes(category as Category)) {
    errors.category = 'Select a valid category.';
  }

  if (!subject) errors.subject = 'Subject is required.';
  else if (subject.length > 500) errors.subject = 'Subject too long (max 500 chars).';

  if (!description) errors.description = 'Please describe your issue.';
  else if (description.length > 10000) errors.description = 'Description too long (max 10,000 chars).';

  if (!PRIORITIES.includes(priority as Priority)) {
    errors.priority = 'Select a valid priority.';
  }

  if (Object.keys(errors).length > 0) {
    return { success: false, errors, prefill: formData };
  }

  const ticketId = crypto.randomUUID();

  await d1.prepare(`
    INSERT INTO client_tickets (
      ticket_id, client_id,
      full_name, email, category, subject, description, priority,
      status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', datetime('now'), datetime('now'))
  `).bind(ticketId, clientId, full_name, email, category, subject, description, priority).run();

  console.log(`[830] new ticket ${ticketId} for client ${clientId} cat=${category}`);
  return { success: true };
}

// ── Form helpers ─────────────────────────────────────────────────────────────

function formGroup(
  name: string,
  label: string,
  type: string,
  value: string,
  error: string | undefined,
  placeholder: string,
  required: boolean,
): string {
  const reqAttr = required ? ' required' : '';
  const errClass = error ? ' form-group--error' : '';
  return `<div class="form-group${errClass}">
    <label for="${name}">${escHtml(label)}${required ? ' <span aria-hidden="true">*</span>' : ''}</label>
    <input id="${name}" name="${name}" type="${type}" value="${escHtml(value)}" placeholder="${escHtml(placeholder)}"${reqAttr}>
    ${error ? `<span class="form-error">${escHtml(error)}</span>` : ''}
  </div>`;
}

function selectGroup(
  name: string,
  label: string,
  options: readonly string[],
  selected: string | undefined,
  error: string | undefined,
  required: boolean,
): string {
  const reqAttr = required ? ' required' : '';
  const errClass = error ? ' form-group--error' : '';
  const optHtml = options.map(o =>
    `<option value="${o}"${o === selected ? ' selected' : ''}>${o.charAt(0).toUpperCase() + o.slice(1)}</option>`
  ).join('');
  return `<div class="form-group${errClass}">
    <label for="${name}">${escHtml(label)}${required ? ' <span aria-hidden="true">*</span>' : ''}</label>
    <select id="${name}" name="${name}"${reqAttr}>${optHtml}</select>
    ${error ? `<span class="form-error">${escHtml(error)}</span>` : ''}
  </div>`;
}

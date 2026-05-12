/**
 * bp.810 — Client Intake: Promotion
 * Flat spoke model — rewritten 2026-05-12
 *
 * Reads raw payload from client_staging_intake by intake_id.
 * Routes to the correct canonical spoke table.
 * On failure: writes to spoke-specific *_error table with intake_id trace.
 * Marks staging row processed=1 on success or failure.
 */

import type { Env } from './stage';
import type {
  ContactPayload, EmployeePayload, VendorPayload, CompliancePayload, InteractionPayload,
} from './validate';

export interface PromoteResult {
  intake_id: number;
  spoke: string;
  success: boolean;
  error?: string;
}

// Error table PK column names per spoke
const SPOKE_ERROR_PK: Record<string, string> = {
  contact: 'contact_error_id',
  employee: 'employee_error_id',
  vendor: 'vendor_error_id',
  compliance: 'compliance_error_id',
  interaction: 'interaction_error_id',
};

const SPOKE_ERROR_TABLE: Record<string, string> = {
  contact: 'client_contacts_error',
  employee: 'client_employees_error',
  vendor: 'client_vendors_error',
  compliance: 'client_compliance_error',
  interaction: 'client_interactions_error',
};

export async function promoteFromStaging(env: Env, intakeId: number, spoke: string, clientId: string): Promise<PromoteResult> {
  // Read the raw staging row
  const row = await env.D1.prepare(
    'SELECT raw_data FROM client_staging_intake WHERE intake_id = ?'
  ).bind(intakeId).first<{ raw_data: string }>();

  if (!row) {
    return { intake_id: intakeId, spoke, success: false, error: 'STAGING_ROW_NOT_FOUND' };
  }

  const payload = JSON.parse(row.raw_data) as Record<string, unknown>;

  try {
    await insertCanonical(env.D1, clientId, spoke, payload);

    // Mark staged row as processed
    await env.D1.prepare(
      "UPDATE client_staging_intake SET processed = 1 WHERE intake_id = ?"
    ).bind(intakeId).run();

    console.log(`[810] PROMOTED: intake_id=${intakeId} spoke=${spoke} client_id=${clientId}`);
    return { intake_id: intakeId, spoke, success: true };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await writeError(env.D1, clientId, spoke, intakeId, 'PROMOTE_FAILED', msg);

    // Still mark processed so we don't retry infinitely
    await env.D1.prepare(
      "UPDATE client_staging_intake SET processed = 1 WHERE intake_id = ?"
    ).bind(intakeId).run();

    console.error(`[810] PROMOTE_ERROR: intake_id=${intakeId} spoke=${spoke} error=${msg}`);
    return { intake_id: intakeId, spoke, success: false, error: msg };
  }
}

async function insertCanonical(d1: D1Database, clientId: string, spoke: string, data: Record<string, unknown>): Promise<void> {
  const now = new Date().toISOString();

  switch (spoke) {
    case 'contact': {
      const p = data as unknown as ContactPayload;
      const id = (p.contact_id as string | undefined) ?? crypto.randomUUID();
      await d1.prepare(`
        INSERT INTO client_contacts
          (contact_id, client_id, full_name, email, email_secondary, phone, role, title, is_primary, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        id, clientId, p.full_name, p.email,
        p.email_secondary ?? null, p.phone ?? null,
        p.role ?? null, p.title ?? null,
        p.is_primary ?? 0,
        now, now,
      ).run();
      break;
    }

    case 'employee': {
      const p = data as unknown as EmployeePayload;
      const id = (p.employee_id as string | undefined) ?? crypto.randomUUID();
      await d1.prepare(`
        INSERT INTO client_employees
          (employee_id, client_id, first_name, last_name, hire_date, employment_status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        id, clientId, p.first_name, p.last_name,
        p.hire_date ?? null,
        p.employment_status ?? 'active',
        now, now,
      ).run();
      break;
    }

    case 'vendor': {
      const p = data as unknown as VendorPayload;
      const id = (p.vendor_id as string | undefined) ?? crypto.randomUUID();
      await d1.prepare(`
        INSERT INTO client_vendors
          (vendor_id, client_id, vendor_name, vendor_type, group_number, integration_type, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        id, clientId, p.vendor_name,
        p.vendor_type ?? null, p.group_number ?? null,
        p.integration_type ?? null,
        now, now,
      ).run();
      break;
    }

    case 'compliance': {
      const p = data as unknown as CompliancePayload;
      const id = (p.compliance_id as string | undefined) ?? crypto.randomUUID();
      await d1.prepare(`
        INSERT INTO client_compliance
          (compliance_id, client_id, self_insured, erisa_applicable, aca_applicable,
           fmla_state_rules, plan_year_start, plan_year_end, required_forms, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        id, clientId,
        p.self_insured ?? 0,
        p.erisa_applicable ?? 1,
        p.aca_applicable ?? 1,
        p.fmla_state_rules ? JSON.stringify(p.fmla_state_rules) : null,
        p.plan_year_start ?? null,
        p.plan_year_end ?? null,
        p.required_forms ? JSON.stringify(p.required_forms) : null,
        now, now,
      ).run();
      break;
    }

    case 'interaction': {
      const p = data as unknown as InteractionPayload;
      const id = (p.interaction_id as string | undefined) ?? crypto.randomUUID();
      await d1.prepare(`
        INSERT INTO client_interactions
          (interaction_id, client_id, contact_id, interaction_type, subject, body_snippet,
           source_message_id, source_thread_id, direction, resolved, occurred_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        id, clientId,
        p.contact_id ?? null,
        p.interaction_type, p.subject ?? null, p.body_snippet ?? null,
        p.source_message_id ?? null, p.source_thread_id ?? null,
        p.direction, p.resolved ?? 0, p.occurred_at,
        now, now,
      ).run();
      break;
    }

    default:
      throw new Error(`Unknown spoke: ${spoke}`);
  }
}

async function writeError(
  d1: D1Database,
  clientId: string,
  spoke: string,
  intakeId: number,
  errorCode: string,
  errorMessage: string,
): Promise<void> {
  const table = SPOKE_ERROR_TABLE[spoke];
  const pkCol = SPOKE_ERROR_PK[spoke];
  if (!table || !pkCol) {
    console.error(`[810] WRITE_ERROR_FAILED: no error table for spoke=${spoke}`);
    return;
  }

  await d1.prepare(`
    INSERT INTO ${table} (${pkCol}, client_id, source_entity, source_id, error_code, error_message, created_at)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
  `).bind(crypto.randomUUID(), clientId, spoke, String(intakeId), errorCode, errorMessage).run();
}

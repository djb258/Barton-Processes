/**
 * 810 — Client Data Intake: Promotion
 *
 * Promotes staged records from intake_record to D1 canonical working tables.
 * Routes by spoke/table identifier.
 */

import type { Env } from './stage';

export interface PromoteResult {
  promoted: number;
  errors: number;
  spoke: string;
}

export async function promoteRecords(env: Env, clientId: string, batchId: string): Promise<PromoteResult> {
  // Read unpromoted records for this batch
  const records = await env.D1.prepare(`
    SELECT intake_record_id, spoke, raw_payload
    FROM intake_record
    WHERE enrollment_intake_id = ? AND client_id = ? AND promoted_at IS NULL
  `).bind(batchId, clientId).all<{
    intake_record_id: string;
    spoke: string;
    raw_payload: string;
  }>();

  if (!records.results || records.results.length === 0) {
    return { promoted: 0, errors: 0, spoke: '' };
  }

  let promoted = 0;
  let errors = 0;
  const spoke = records.results[0].spoke;

  for (const row of records.results) {
    try {
      const data = JSON.parse(row.raw_payload);
      await insertCanonical(env.D1, clientId, row.spoke, data);

      // Mark as promoted
      await env.D1.prepare(
        "UPDATE intake_record SET promoted_at = datetime('now') WHERE intake_record_id = ?"
      ).bind(row.intake_record_id).run();

      promoted++;
    } catch (err) {
      errors++;
      const msg = err instanceof Error ? err.message : String(err);
      await writeError(env.D1, clientId, row.spoke, row.intake_record_id, 'PROMOTE_FAILED', msg);
    }
  }

  // Update batch status
  await env.D1.prepare(
    "UPDATE enrollment_intake SET status = 'completed' WHERE enrollment_intake_id = ?"
  ).bind(batchId).run();

  console.log(`[810] PROMOTE: batch=${batchId} spoke=${spoke} promoted=${promoted} errors=${errors}`);
  return { promoted, errors, spoke };
}

async function insertCanonical(d1: D1Database, clientId: string, table: string, data: Record<string, unknown>): Promise<void> {
  const id = crypto.randomUUID();

  switch (table) {
    case 'plan':
      await d1.prepare(`
        INSERT INTO plan (plan_id, client_id, benefit_type, carrier_id, effective_date, status, version, rate_ee, rate_es, rate_ec, rate_fam, employer_rate_ee, employer_rate_es, employer_rate_ec, employer_rate_fam, source_quote_id)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(id, clientId, data.benefit_type, data.carrier_id ?? null, data.effective_date ?? null, data.status ?? 'active', data.rate_ee ?? null, data.rate_es ?? null, data.rate_ec ?? null, data.rate_fam ?? null, data.employer_rate_ee ?? null, data.employer_rate_es ?? null, data.employer_rate_ec ?? null, data.employer_rate_fam ?? null, data.source_quote_id ?? null).run();
      break;

    case 'plan_quote':
      await d1.prepare(`
        INSERT INTO plan_quote (plan_quote_id, client_id, benefit_type, carrier_id, effective_year, rate_ee, rate_es, rate_ec, rate_fam, source, received_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(id, clientId, data.benefit_type, data.carrier_id, data.effective_year, data.rate_ee ?? null, data.rate_es ?? null, data.rate_ec ?? null, data.rate_fam ?? null, data.source ?? null, data.received_date ?? null, data.status ?? 'received').run();
      break;

    case 'person':
      await d1.prepare(`
        INSERT INTO person (person_id, client_id, first_name, last_name, ssn_hash, status)
        VALUES (?, ?, ?, ?, ?, ?)
      `).bind(id, clientId, data.first_name, data.last_name, data.ssn_hash ?? null, data.status ?? 'active').run();
      break;

    case 'election':
      await d1.prepare(`
        INSERT INTO election (election_id, client_id, person_id, plan_id, coverage_tier, effective_date)
        VALUES (?, ?, ?, ?, ?, ?)
      `).bind(id, clientId, data.person_id, data.plan_id, data.coverage_tier, data.effective_date).run();
      break;

    case 'vendor':
      await d1.prepare(`
        INSERT INTO vendor (vendor_id, client_id, vendor_name, vendor_type)
        VALUES (?, ?, ?, ?)
      `).bind(id, clientId, data.vendor_name, data.vendor_type ?? null).run();
      break;

    case 'external_identity_map':
      await d1.prepare(`
        INSERT INTO external_identity_map (external_identity_id, client_id, entity_type, internal_id, vendor_id, external_id_value, effective_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(id, clientId, data.entity_type, data.internal_id, data.vendor_id, data.external_id_value, data.effective_date ?? null, data.status ?? 'active').run();
      break;

    case 'invoice':
      await d1.prepare(`
        INSERT INTO invoice (invoice_id, client_id, vendor_id, invoice_number, amount, invoice_date, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(id, clientId, data.vendor_id, data.invoice_number, data.amount, data.invoice_date, data.due_date ?? null, data.status ?? 'received').run();
      break;

    case 'service_request':
      await d1.prepare(`
        INSERT INTO service_request (service_request_id, client_id, category, status)
        VALUES (?, ?, ?, ?)
      `).bind(id, clientId, data.category, data.status ?? 'open').run();
      break;

    default:
      throw new Error(`Unknown table: ${table}`);
  }
}

async function writeError(d1: D1Database, clientId: string, spoke: string, sourceId: string, errorCode: string, errorMessage: string): Promise<void> {
  const errorTable = SPOKE_ERROR_TABLE[spoke] ?? 'client_error';
  const pkCol = errorTable.replace('_error', '_error_id').replace('employee_error_id', 'employee_error_id');

  await d1.prepare(`
    INSERT INTO ${errorTable} (${errorTable}_id, client_id, source_entity, source_id, error_code, error_message)
    VALUES (?, ?, ?, ?, ?, ?)
  `).bind(crypto.randomUUID(), clientId, spoke, sourceId, errorCode, errorMessage).run();
}

const SPOKE_ERROR_TABLE: Record<string, string> = {
  plan: 'plan_error',
  plan_quote: 'plan_error',
  person: 'employee_error',
  election: 'employee_error',
  vendor: 'vendor_error',
  external_identity_map: 'vendor_error',
  invoice: 'vendor_error',
  service_request: 'service_error',
};

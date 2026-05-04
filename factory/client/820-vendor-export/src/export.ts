/**
 * 820 — Vendor Export: Export generation
 *
 * Reads D1 canonical → applies blueprint mapping → generates output.
 * Translates internal UUIDs to external IDs via external_identity_map.
 */

import { loadBlueprint, type VendorBlueprint } from './blueprints';

export interface Env {
  D1: D1Database;
  KV: KVNamespace;
  DAILY_VENDORS: string;
  WEEKLY_VENDORS: string;
  WEEKLY_DAY: string;
}

export interface ExportResult {
  export_id: string;
  client_id: string;
  vendor_id: string;
  record_count: number;
  errors: number;
  output: string;
  format: string;
}

export async function generateExport(env: Env, clientId: string, vendorId: string): Promise<ExportResult> {
  const exportId = crypto.randomUUID();

  // Load blueprint
  const blueprint = await loadBlueprint(env.KV, vendorId);
  if (!blueprint) {
    await logError(env.D1, clientId, vendorId, exportId, 'BLUEPRINT_NOT_FOUND', `No blueprint for vendor ${vendorId}`);
    return { export_id: exportId, client_id: clientId, vendor_id: vendorId, record_count: 0, errors: 1, output: '', format: '' };
  }

  // Read canonical data from the live client D1 schema.
  const records = await env.D1.prepare(`
    SELECT
      e.employee_id,
      e.employee_id as person_id,
      e.client_id,
      e.first_name,
      e.last_name,
      e.hire_date,
      e.employment_status,
      e.orbt_mode,
      v.vendor_id,
      v.vendor_name,
      v.vendor_type,
      v.group_number,
      v.integration_type
    FROM client_employees e
    LEFT JOIN client_vendors v ON v.client_id = e.client_id AND v.vendor_id = ?
    WHERE e.client_id = ?
      AND COALESCE(e.employment_status, 'active') = 'active'
  `).bind(vendorId, clientId).all();

  if (!records.results || records.results.length === 0) {
    await logExport(env.D1, exportId, clientId, vendorId, blueprint.vendor_name, 0, blueprint.file_format, 'no_data');
    return { export_id: exportId, client_id: clientId, vendor_id: vendorId, record_count: 0, errors: 0, output: '', format: blueprint.file_format };
  }

  // Load external ID mappings for this vendor
  const idMappings = await env.D1.prepare(`
    SELECT internal_id, external_id_value, entity_type
    FROM (
      SELECT
        employee_id as internal_id,
        vendor_employee_id as external_id_value,
        'employee' as entity_type,
        status
      FROM client_employee_vendor_ids
      WHERE vendor_id = ?
    )
    WHERE status = 'active'
  `).bind(vendorId).all<{
    internal_id: string;
    external_id_value: string;
    entity_type: string;
  }>();

  const idMap = new Map<string, string>();
  if (idMappings.results) {
    for (const m of idMappings.results) {
      idMap.set(m.internal_id, m.external_id_value);
    }
  }

  // Apply blueprint mapping
  const outputRows: string[] = [];
  let errors = 0;
  const delimiter = blueprint.delimiter || ',';

  // Header
  if (blueprint.include_header) {
    outputRows.push(Object.values(blueprint.field_mappings).join(delimiter));
  }

  for (const row of records.results) {
    const record = row as Record<string, unknown>;

    // Translate internal IDs to external
    const personExtId = idMap.get(record.person_id as string);
    if (!personExtId) {
      await logError(env.D1, clientId, vendorId, exportId, 'MISSING_EXTERNAL_ID',
        `No external ID for person ${record.person_id}`);
      errors++;
      continue;
    }
    record['external_person_id'] = personExtId;

    // Map fields
    const outputFields: string[] = [];
    for (const [internalCol, _vendorCol] of Object.entries(blueprint.field_mappings)) {
      const value = record[internalCol] ?? '';
      outputFields.push(String(value));
    }
    outputRows.push(outputFields.join(delimiter));
  }

  const output = outputRows.join('\n');
  const recordCount = outputRows.length - (blueprint.include_header ? 1 : 0);

  // Log export
  await logExport(env.D1, exportId, clientId, vendorId, blueprint.vendor_name, recordCount, blueprint.file_format, 'completed');

  console.log(`[820] EXPORT: client=${clientId} vendor=${vendorId} records=${recordCount} errors=${errors}`);

  return {
    export_id: exportId,
    client_id: clientId,
    vendor_id: vendorId,
    record_count: recordCount,
    errors,
    output,
    format: blueprint.file_format,
  };
}

async function logExport(d1: D1Database, exportId: string, clientId: string, vendorId: string, blueprintId: string, recordCount: number, fileFormat: string, status: string): Promise<void> {
  await d1.prepare(`
    INSERT INTO export_log (export_id, client_id, vendor_id, blueprint_id, record_count, file_format, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(exportId, clientId, vendorId, blueprintId, recordCount, fileFormat, status).run();
}

async function logError(d1: D1Database, clientId: string, vendorId: string, exportId: string, errorCode: string, errorMessage: string): Promise<void> {
  await d1.prepare(`
    INSERT INTO export_error (error_id, client_id, vendor_id, export_id, error_code, error_message)
    VALUES (?, ?, ?, ?, ?, ?)
  `).bind(crypto.randomUUID(), clientId, vendorId, exportId, errorCode, errorMessage).run();
}

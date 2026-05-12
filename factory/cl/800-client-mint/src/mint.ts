/**
 * 800 — Client Mint: Core minting logic
 *
 * Single-tier model (2026-05-12): svg-d1-client.clients is canonical.
 * Reads CL company_identity from Neon (READ ONLY — never writes CL).
 * Mints new client record in D1 clients table.
 * No Neon vault write tier. vaulted_at column left in place (reserved, NULL).
 */

import { neon } from '@neondatabase/serverless';

export interface Env {
  D1: D1Database;
  CL_DATABASE_URL: string;
}

export interface MintResult {
  client_id: string;
  sovereign_id: string;
  company_name: string;
  status: 'minted' | 'error';
  error?: string;
}

interface CLIdentityRecord {
  company_unique_id: string;
  company_name: string;
  company_domain: string | null;
  employee_count_band: string | null;
}

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export async function mintClient(env: Env, sovereignId: string): Promise<MintResult> {
  // UUID validation — 400 if not valid
  if (!UUID_REGEX.test(sovereignId)) {
    return {
      client_id: '',
      sovereign_id: sovereignId,
      company_name: '',
      status: 'error',
      error: `Invalid sovereign_id format — must be a valid UUID`,
    };
  }

  // Duplicate check: clients table (canonical)
  const existing = await env.D1.prepare(
    'SELECT client_id FROM clients WHERE sovereign_id = ?'
  ).bind(sovereignId).first<{ client_id: string }>();

  if (existing) {
    await writeError(env.D1, existing.client_id, 'DUPLICATE_SOVEREIGN',
      `Sovereign ID ${sovereignId} already minted as client ${existing.client_id}`);
    return {
      client_id: existing.client_id,
      sovereign_id: sovereignId,
      company_name: '',
      status: 'error',
      error: `Sovereign ID already minted as client_id=${existing.client_id}`,
    };
  }

  // Read company identity from CL (READ ONLY — never write)
  const sql = neon(env.CL_DATABASE_URL);
  const rows = await sql`
    SELECT
      company_unique_id,
      company_name,
      company_domain,
      employee_count_band
    FROM cl.company_identity
    WHERE company_unique_id = ${sovereignId}
    LIMIT 1
  `;

  if (!rows || rows.length === 0) {
    const errorClientId = crypto.randomUUID();
    await writeError(env.D1, errorClientId, 'SOVEREIGN_NOT_FOUND',
      `Sovereign ID ${sovereignId} not found in cl.company_identity`);
    return {
      client_id: '',
      sovereign_id: sovereignId,
      company_name: '',
      status: 'error',
      error: `Sovereign ID ${sovereignId} not found in CL`,
    };
  }

  const cl = rows[0] as CLIdentityRecord;
  const clientId = crypto.randomUUID();
  const now = new Date().toISOString();

  // Mint client in D1 clients table (single-tier canonical)
  // Notes: ein/industry/employee_count not in cl.company_identity — left NULL
  // employee_count_band is text (band, not integer) — stored in notes field
  await env.D1.prepare(`
    INSERT INTO clients (
      client_id,
      sovereign_ref,
      hub_id,
      cc_layer,
      ctb_placement,
      orbt_mode,
      strike_count,
      sovereign_id,
      company_name,
      company_domain,
      ein,
      industry,
      employee_count,
      lifecycle_stage,
      notes,
      created_at,
      updated_at,
      onboarded_at,
      vaulted_at
    ) VALUES (?, 'svg-outreach', 'DB-CLIENT', 'CC-03', 'leaf', 'BUILD', 0, ?, ?, ?, NULL, NULL, NULL, 'onboarding', ?, ?, ?, NULL, NULL)
  `).bind(
    clientId,
    sovereignId,
    cl.company_name || 'Unknown',
    cl.company_domain ?? null,
    cl.employee_count_band ? `employee_count_band:${cl.employee_count_band}` : null,
    now,
    now,
  ).run();

  console.log(`[800] MINT: client_id=${clientId} sovereign_id=${sovereignId} name=${cl.company_name} lifecycle_stage=onboarding employee_count_band=${cl.employee_count_band ?? 'null'}`);

  return {
    client_id: clientId,
    sovereign_id: sovereignId,
    company_name: cl.company_name || 'Unknown',
    status: 'minted',
  };
}

async function writeError(
  d1: D1Database,
  clientId: string,
  errorCode: string,
  errorMessage: string,
): Promise<void> {
  const now = new Date().toISOString();
  await d1.prepare(`
    INSERT INTO clients_error (
      error_id,
      client_id,
      error_code,
      error_message,
      sender_email,
      raw_subject,
      payload_snapshot,
      created_at
    ) VALUES (?, ?, ?, ?, NULL, NULL, NULL, ?)
  `).bind(crypto.randomUUID(), clientId, errorCode, errorMessage, now).run();
}

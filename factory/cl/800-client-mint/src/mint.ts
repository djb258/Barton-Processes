/**
 * 800 — Client Mint: Core minting logic
 *
 * Reads CL sovereign identity from Neon vault,
 * mints new client_id in D1 working tables.
 */

import { neon } from '@neondatabase/serverless';

export interface Env {
  D1: D1Database;
  NEON_URL: string;
}

export interface MintResult {
  client_id: string;
  sovereign_id: string;
  legal_name: string;
  status: 'minted' | 'error';
  error?: string;
}

interface SovereignRecord {
  company_unique_id: string;
  canonical_name: string;
  ein: string | null;
  state: string | null;
  domain: string | null;
  source: string | null;
}

export async function mintClient(env: Env, sovereignId: string): Promise<MintResult> {
  // Check for duplicate sovereign_id in D1
  const existing = await env.D1.prepare(
    'SELECT client_id FROM client WHERE sovereign_id = ?'
  ).bind(sovereignId).first<{ client_id: string }>();

  if (existing) {
    await writeError(env.D1, existing.client_id, 'mint', null, 'DUPLICATE_SOVEREIGN',
      `Sovereign ID ${sovereignId} already minted as client ${existing.client_id}`);
    return {
      client_id: existing.client_id,
      sovereign_id: sovereignId,
      legal_name: '',
      status: 'error',
      error: `Sovereign ID already minted as client_id=${existing.client_id}`,
    };
  }

  // Read company identity from Neon CL schema
  const sql = neon(env.NEON_URL);
  const rows = await sql`
    SELECT
      company_unique_id,
      canonical_name,
      ein,
      state,
      company_domain as domain,
      source
    FROM cl.company_identity
    WHERE company_unique_id = ${sovereignId}
    LIMIT 1
  `;

  if (!rows || rows.length === 0) {
    const errorClientId = crypto.randomUUID();
    await writeError(env.D1, errorClientId, 'mint', null, 'SOVEREIGN_NOT_FOUND',
      `Sovereign ID ${sovereignId} not found in CL vault`);
    return {
      client_id: '',
      sovereign_id: sovereignId,
      legal_name: '',
      status: 'error',
      error: `Sovereign ID ${sovereignId} not found in Neon CL schema`,
    };
  }

  const sovereign = rows[0] as SovereignRecord;
  const clientId = crypto.randomUUID();

  // Mint client in D1
  await env.D1.prepare(`
    INSERT INTO client (
      client_id, sovereign_id, legal_name, fein, domicile_state,
      source, status, version, domain
    ) VALUES (?, ?, ?, ?, ?, ?, 'active', 1, ?)
  `).bind(
    clientId,
    sovereignId,
    sovereign.canonical_name || 'Unknown',
    sovereign.ein,
    sovereign.state,
    sovereign.source || 'cl_sovereign',
    sovereign.domain,
  ).run();

  console.log(`[800] MINT: client_id=${clientId} sovereign_id=${sovereignId} name=${sovereign.canonical_name}`);

  return {
    client_id: clientId,
    sovereign_id: sovereignId,
    legal_name: sovereign.canonical_name || 'Unknown',
    status: 'minted',
  };
}

async function writeError(
  d1: D1Database, clientId: string, sourceEntity: string,
  sourceId: string | null, errorCode: string, errorMessage: string,
): Promise<void> {
  await d1.prepare(`
    INSERT INTO client_error (client_error_id, client_id, source_entity, source_id, error_code, error_message)
    VALUES (?, ?, ?, ?, ?, ?)
  `).bind(crypto.randomUUID(), clientId, sourceEntity, sourceId, errorCode, errorMessage).run();
}

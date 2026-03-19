/**
 * 810 — Client Data Intake: Vault promotion
 *
 * Pushes certified canonical records from D1 to Neon vault.
 */

import { neon } from '@neondatabase/serverless';
import type { Env } from './stage';

export interface VaultResult {
  tables: Record<string, number>;
  errors: number;
  durationMs: number;
}

const VAULTABLE_TABLES = [
  'plan', 'plan_quote', 'person', 'election',
  'vendor', 'external_identity_map', 'invoice', 'service_request',
] as const;

export async function vaultRecords(env: Env): Promise<VaultResult> {
  const start = Date.now();
  const sql = neon(env.NEON_URL);
  const tables: Record<string, number> = {};
  let totalErrors = 0;

  for (const table of VAULTABLE_TABLES) {
    const rows = await env.D1.prepare(
      `SELECT * FROM ${table} WHERE vaulted_at IS NULL`
    ).all();

    if (!rows.results || rows.results.length === 0) {
      tables[table] = 0;
      continue;
    }

    let count = 0;
    for (const row of rows.results) {
      try {
        await vaultRow(sql, table, row as Record<string, unknown>);
        const pk = getPrimaryKey(table);
        await env.D1.prepare(
          `UPDATE ${table} SET vaulted_at = datetime('now') WHERE ${pk} = ?`
        ).bind((row as Record<string, unknown>)[pk]).run();
        count++;
      } catch (err) {
        totalErrors++;
        console.error(`[810] VAULT ERROR: ${table} — ${err instanceof Error ? err.message : err}`);
      }
    }

    tables[table] = count;
    console.log(`[810] VAULT: ${table} = ${count} rows`);
  }

  return { tables, errors: totalErrors, durationMs: Date.now() - start };
}

function getPrimaryKey(table: string): string {
  const map: Record<string, string> = {
    plan: 'plan_id',
    plan_quote: 'plan_quote_id',
    person: 'person_id',
    election: 'election_id',
    vendor: 'vendor_id',
    external_identity_map: 'external_identity_id',
    invoice: 'invoice_id',
    service_request: 'service_request_id',
  };
  return map[table] ?? `${table}_id`;
}

async function vaultRow(sql: ReturnType<typeof neon>, table: string, row: Record<string, unknown>): Promise<void> {
  // Build dynamic INSERT for Neon — each table maps to clnt.<table>
  const pk = getPrimaryKey(table);
  const id = row[pk] as string;

  // Remove D1-only columns
  const { vaulted_at: _, ...data } = row;

  const cols = Object.keys(data);
  const placeholders = cols.map((_, i) => `$${i + 1}`);
  const values = cols.map(c => data[c]);

  // Cast UUID columns
  const uuidCols = new Set([pk, 'client_id', 'person_id', 'plan_id', 'vendor_id', 'internal_id', 'source_quote_id', 'source_id']);
  const castPlaceholders = cols.map((c, i) => uuidCols.has(c) && values[i] ? `$${i + 1}::uuid` : `$${i + 1}`);

  await sql(
    `INSERT INTO clnt.${table} (${cols.join(', ')}) VALUES (${castPlaceholders.join(', ')}) ON CONFLICT (${pk}) DO NOTHING`,
    values,
  );
}

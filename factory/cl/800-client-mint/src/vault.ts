/**
 * 800 — Client Mint: Vault promotion
 *
 * Promotes certified clients from D1 working tables to Neon vault.
 */

import { neon } from '@neondatabase/serverless';
import type { Env } from './mint';

export interface VaultResult {
  vaulted: number;
  errors: number;
  durationMs: number;
}

export async function vaultClients(env: Env): Promise<VaultResult> {
  const start = Date.now();
  const sql = neon(env.NEON_URL);

  // Read unvaulted clients from D1
  const unvaulted = await env.D1.prepare(
    'SELECT * FROM client WHERE vaulted_at IS NULL'
  ).all<{
    client_id: string;
    sovereign_id: string;
    legal_name: string;
    fein: string | null;
    domicile_state: string | null;
    effective_date: string | null;
    status: string;
    source: string | null;
    version: number;
    domain: string | null;
    label_override: string | null;
    logo_url: string | null;
    color_primary: string | null;
    color_accent: string | null;
    feature_flags: string;
    dashboard_blocks: string;
  }>();

  if (!unvaulted.results || unvaulted.results.length === 0) {
    console.log('[800] VAULT: No unvaulted clients.');
    return { vaulted: 0, errors: 0, durationMs: Date.now() - start };
  }

  let vaulted = 0;
  let errors = 0;

  for (const row of unvaulted.results) {
    try {
      await sql`
        INSERT INTO clnt.client (
          client_id, sovereign_id, legal_name, fein, domicile_state,
          effective_date, status, source, version, domain,
          label_override, logo_url, color_primary, color_accent,
          feature_flags, dashboard_blocks
        ) VALUES (
          ${row.client_id}::uuid, ${row.sovereign_id}, ${row.legal_name},
          ${row.fein}, ${row.domicile_state},
          ${row.effective_date}::date, ${row.status}, ${row.source},
          ${row.version}, ${row.domain},
          ${row.label_override}, ${row.logo_url}, ${row.color_primary},
          ${row.color_accent}, ${row.feature_flags}::jsonb,
          ${row.dashboard_blocks}::jsonb
        )
        ON CONFLICT (client_id) DO NOTHING
      `;

      // Mark as vaulted in D1
      await env.D1.prepare(
        "UPDATE client SET vaulted_at = datetime('now') WHERE client_id = ?"
      ).bind(row.client_id).run();

      vaulted++;
      console.log(`[800] VAULT: client_id=${row.client_id} → Neon`);
    } catch (err) {
      errors++;
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[800] VAULT ERROR: client_id=${row.client_id} — ${msg}`);

      await env.D1.prepare(`
        INSERT INTO client_error (client_error_id, client_id, source_entity, source_id, error_code, error_message)
        VALUES (?, ?, 'vault', ?, 'VAULT_FAILED', ?)
      `).bind(crypto.randomUUID(), row.client_id, row.client_id, msg).run();
    }
  }

  console.log(`[800] VAULT: vaulted=${vaulted} errors=${errors} (${Date.now() - start}ms)`);
  return { vaulted, errors, durationMs: Date.now() - start };
}

// ═══════════════════════════════════════════════════════════════
// Database Client — Neon via Hyperdrive
// ═══════════════════════════════════════════════════════════════
// Authority: Tier 0 §CQRS — all writes are INSERTs, leaves only
// Connection: CF Hyperdrive binding (HD_CL), secrets from Doppler
// ═══════════════════════════════════════════════════════════════

import pg from 'pg';

let pool: pg.Pool | null = null;

export function getPool(connectionString: string): pg.Pool {
  if (pool) return pool;
  pool = new pg.Pool({
    connectionString,
    ssl: { rejectUnauthorized: false },
    max: 5,
    idleTimeoutMillis: 10_000,
  });
  return pool;
}

export async function query<T = Record<string, unknown>>(
  connectionString: string,
  sql: string,
  params?: unknown[]
): Promise<{ data: T[]; error: string | null }> {
  try {
    const p = getPool(connectionString);
    const result = await p.query(sql, params);
    return { data: result.rows as T[], error: null };
  } catch (err) {
    return { data: [], error: err instanceof Error ? err.message : 'Query error' };
  }
}

export async function queryOne<T = Record<string, unknown>>(
  connectionString: string,
  sql: string,
  params?: unknown[]
): Promise<{ data: T | null; error: string | null }> {
  const result = await query<T>(connectionString, sql, params);
  return { data: result.data[0] ?? null, error: result.error };
}

export async function insert(
  connectionString: string,
  table: string,
  row: Record<string, unknown>,
  returning?: string
): Promise<{ data: Record<string, unknown> | null; error: string | null }> {
  try {
    const p = getPool(connectionString);
    const keys = Object.keys(row);
    const values = Object.values(row);
    const placeholders = keys.map((_, i) => `$${i + 1}`).join(', ');
    const columns = keys.map(k => `"${k}"`).join(', ');
    let sql = `INSERT INTO ${table} (${columns}) VALUES (${placeholders})`;
    if (returning) sql += ` RETURNING ${returning}`;
    const result = await p.query(sql, values);
    return { data: result.rows[0] ?? null, error: null };
  } catch (err) {
    return { data: null, error: err instanceof Error ? err.message : 'Insert error' };
  }
}

/**
 * 900 — Sales Portal: Slug resolution
 *
 * Resolves URL slug to sales_id and loads prospect context.
 */

export interface SalesContext {
  sales_id: string;
  slug: string;
  sovereign_id: string;
  legal_name: string;
  domicile_state: string | null;
  current_phase: string;
  agent_name: string | null;
}

export async function resolveSales(d1: D1Database, slug: string): Promise<SalesContext | null> {
  const row = await d1.prepare(`
    SELECT sales_id, slug, sovereign_id, legal_name, domicile_state, current_phase, agent_name
    FROM sales_state
    WHERE slug = ?
  `).bind(slug).first<SalesContext>();

  return row ?? null;
}

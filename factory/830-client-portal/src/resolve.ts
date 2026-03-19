/**
 * 830 — Client Portal: Slug resolution + branding
 *
 * Resolves URL slug to client_id and loads branding context.
 */

export interface ClientContext {
  client_id: string;
  slug: string;
  legal_name: string;
  label_override: string | null;
  logo_url: string | null;
  color_primary: string | null;
  color_accent: string | null;
  status: string;
}

export function displayName(client: ClientContext): string {
  return client.label_override || client.legal_name;
}

export async function resolveClient(d1: D1Database, slug: string): Promise<ClientContext | null> {
  const row = await d1.prepare(`
    SELECT client_id, slug, legal_name, label_override, logo_url,
           color_primary, color_accent, status
    FROM client
    WHERE slug = ?
  `).bind(slug).first<ClientContext>();

  return row ?? null;
}

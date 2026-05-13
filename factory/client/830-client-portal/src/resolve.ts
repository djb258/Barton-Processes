/**
 * 830 — Client Portal: Slug resolution + branding
 *
 * Resolves URL slug to client_id and loads branding context from svg-d1-client.
 * Table: clients — canonical fields used by portal.
 */

export interface ClientContext {
  client_id: string;
  slug: string;
  company_name: string;
  label_override: string | null;
  logo_url: string | null;
  color_primary: string | null;
  color_accent: string | null;
  lifecycle_stage: string;
  employee_count: number | null;
  ein: string | null;
  industry: string | null;
  onboarded_at: string | null;
}

export function displayName(client: ClientContext): string {
  return client.label_override || client.company_name;
}

export async function resolveClient(d1: D1Database, slug: string): Promise<ClientContext | null> {
  const row = await d1.prepare(`
    SELECT client_id, slug, company_name, label_override, logo_url,
           color_primary, color_accent, lifecycle_stage,
           employee_count, ein, industry, onboarded_at
    FROM clients
    WHERE slug = ?
  `).bind(slug).first<ClientContext>();

  return row ?? null;
}

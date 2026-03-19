/**
 * 820 — Vendor Export: Blueprint loading
 *
 * Vendor blueprints define field mappings from internal schema to vendor format.
 * Stored in KV as JSON. Sourced from client repo db/vendor_blueprints/*.mapping.json.
 */

export interface VendorBlueprint {
  vendor_id: string;
  vendor_name: string;
  file_format: 'csv' | 'json';
  delimiter: string;
  field_mappings: Record<string, string>;  // internal_column → vendor_column
  include_header: boolean;
}

export async function loadBlueprint(kv: KVNamespace, vendorId: string): Promise<VendorBlueprint | null> {
  const raw = await kv.get(`blueprint:${vendorId}`, 'text');
  if (!raw) return null;

  try {
    return JSON.parse(raw) as VendorBlueprint;
  } catch {
    return null;
  }
}

export async function listBlueprints(kv: KVNamespace): Promise<string[]> {
  const list = await kv.list({ prefix: 'blueprint:' });
  return list.keys.map(k => k.name.replace('blueprint:', ''));
}

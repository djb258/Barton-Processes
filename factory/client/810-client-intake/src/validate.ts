/**
 * 810 — Client Data Intake: Zod validation schemas per spoke
 *
 * Validates at boundary. Rejects malformed data before staging.
 * Derived from client blueprint column registry.
 */

import { z } from 'zod';

// ── S2: Plan ────────────────────────────────────────────────

export const planSchema = z.object({
  benefit_type: z.string().min(1),
  carrier_id: z.string().optional(),
  effective_date: z.string().optional(),
  status: z.string().default('active'),
  rate_ee: z.number().optional(),
  rate_es: z.number().optional(),
  rate_ec: z.number().optional(),
  rate_fam: z.number().optional(),
  employer_rate_ee: z.number().optional(),
  employer_rate_es: z.number().optional(),
  employer_rate_ec: z.number().optional(),
  employer_rate_fam: z.number().optional(),
});

export const planQuoteSchema = z.object({
  benefit_type: z.string().min(1),
  carrier_id: z.string().min(1),
  effective_year: z.number().int(),
  rate_ee: z.number().optional(),
  rate_es: z.number().optional(),
  rate_ec: z.number().optional(),
  rate_fam: z.number().optional(),
  source: z.string().optional(),
  received_date: z.string().optional(),
  status: z.enum(['received', 'presented', 'selected', 'rejected']).default('received'),
});

// ── S3: Employee ────────────────────────────────────────────

export const personSchema = z.object({
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  ssn_hash: z.string().optional(),
  status: z.string().default('active'),
});

export const electionSchema = z.object({
  person_id: z.string().uuid(),
  plan_id: z.string().uuid(),
  coverage_tier: z.enum(['EE', 'ES', 'EC', 'FAM']),
  effective_date: z.string().min(1),
});

// ── S4: Vendor ──────────────────────────────────────────────

export const vendorSchema = z.object({
  vendor_name: z.string().min(1),
  vendor_type: z.string().optional(),
});

export const externalIdentityMapSchema = z.object({
  entity_type: z.enum(['person', 'plan']),
  internal_id: z.string().uuid(),
  vendor_id: z.string().uuid(),
  external_id_value: z.string().min(1),
  effective_date: z.string().optional(),
  status: z.string().default('active'),
});

export const invoiceSchema = z.object({
  vendor_id: z.string().uuid(),
  invoice_number: z.string().min(1),
  amount: z.number(),
  invoice_date: z.string().min(1),
  due_date: z.string().optional(),
  status: z.enum(['received', 'approved', 'paid', 'disputed']).default('received'),
});

// ── S5: Service ─────────────────────────────────────────────

export const serviceRequestSchema = z.object({
  category: z.string().min(1),
  status: z.string().default('open'),
});

// ── Schema Map ──────────────────────────────────────────────

const SPOKE_SCHEMAS: Record<string, z.ZodSchema> = {
  plan: planSchema,
  plan_quote: planQuoteSchema,
  person: personSchema,
  election: electionSchema,
  vendor: vendorSchema,
  external_identity_map: externalIdentityMapSchema,
  invoice: invoiceSchema,
  service_request: serviceRequestSchema,
};

export interface ValidationError {
  index: number;
  errors: z.ZodIssue[];
}

export interface ValidRecord {
  data: Record<string, unknown>;
}

export interface ValidationResult {
  valid: ValidRecord[];
  errors: ValidationError[];
}

export function validateIntake(table: string, data: unknown[]): ValidationResult {
  const schema = SPOKE_SCHEMAS[table];
  if (!schema) {
    return {
      valid: [],
      errors: data.map((_, i) => ({ index: i, errors: [{ code: 'custom', message: `Unknown table: ${table}`, path: [] }] as z.ZodIssue[] })),
    };
  }

  const valid: ValidRecord[] = [];
  const errors: ValidationError[] = [];

  for (let i = 0; i < data.length; i++) {
    const result = schema.safeParse(data[i]);
    if (result.success) {
      valid.push({ data: result.data as Record<string, unknown> });
    } else {
      errors.push({ index: i, errors: result.error.issues });
    }
  }

  return { valid, errors };
}

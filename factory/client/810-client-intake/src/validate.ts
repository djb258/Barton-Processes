import { z } from 'zod';

// ============================================================
// bp.810 Client Intake — Zod boundary validation
// Flat spoke model: spoke field routes to canonical table
// Spoke values: contact | employee | vendor | compliance | interaction
// Rewritten 2026-05-12 — OLD normalized schemas discarded
// ============================================================

// --- Contact spoke ---
export const ContactSchema = z.object({
  spoke: z.literal('contact'),
  client_id: z.string().min(1),
  contact_id: z.string().min(1).optional(),
  full_name: z.string().min(1),
  email: z.string().email(),
  email_secondary: z.string().email().optional().nullable(),
  phone: z.string().optional().nullable(),
  role: z.string().optional().nullable(),
  title: z.string().optional().nullable(),
  is_primary: z.number().int().min(0).max(1).default(0),
});

// --- Employee spoke ---
export const EmployeeSchema = z.object({
  spoke: z.literal('employee'),
  client_id: z.string().min(1),
  employee_id: z.string().min(1).optional(),
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  hire_date: z.string().optional().nullable(),
  employment_status: z.enum(['active', 'terminated', 'leave', 'suspended']).default('active'),
});

// --- Vendor spoke ---
export const VendorSchema = z.object({
  spoke: z.literal('vendor'),
  client_id: z.string().min(1),
  vendor_id: z.string().min(1).optional(),
  vendor_name: z.string().min(1),
  vendor_type: z.enum(['Carrier', 'TPA', 'PBM', 'Broker']).optional().nullable(),
  group_number: z.string().optional().nullable(),
  integration_type: z.enum(['API', 'SFTP', 'Portal', 'Manual']).optional().nullable(),
});

// --- Compliance spoke ---
export const ComplianceSchema = z.object({
  spoke: z.literal('compliance'),
  client_id: z.string().min(1),
  compliance_id: z.string().min(1).optional(),
  self_insured: z.number().int().min(0).max(1).default(0),
  erisa_applicable: z.number().int().min(0).max(1).default(1),
  aca_applicable: z.number().int().min(0).max(1).default(1),
  fmla_state_rules: z.record(z.unknown()).optional().nullable(),
  plan_year_start: z.string().optional().nullable(),
  plan_year_end: z.string().optional().nullable(),
  required_forms: z.array(z.string()).optional().nullable(),
});

// --- Interaction spoke ---
export const InteractionSchema = z.object({
  spoke: z.literal('interaction'),
  client_id: z.string().min(1),
  interaction_id: z.string().min(1).optional(),
  contact_id: z.string().optional().nullable(),
  interaction_type: z.enum(['email_inbound', 'email_outbound', 'call_inbound', 'call_outbound', 'meeting', 'note']),
  subject: z.string().optional().nullable(),
  body_snippet: z.string().optional().nullable(),
  source_message_id: z.string().optional().nullable(),
  source_thread_id: z.string().optional().nullable(),
  direction: z.enum(['inbound', 'outbound', 'internal']),
  resolved: z.number().int().min(0).max(1).default(0),
  occurred_at: z.string().min(1), // ISO datetime string — required
});

// --- Union discriminated by spoke ---
export const IntakePayloadSchema = z.discriminatedUnion('spoke', [
  ContactSchema,
  EmployeeSchema,
  VendorSchema,
  ComplianceSchema,
  InteractionSchema,
]);

export type IntakePayload =
  | z.infer<typeof ContactSchema>
  | z.infer<typeof EmployeeSchema>
  | z.infer<typeof VendorSchema>
  | z.infer<typeof ComplianceSchema>
  | z.infer<typeof InteractionSchema>;

export type ContactPayload = z.infer<typeof ContactSchema>;
export type EmployeePayload = z.infer<typeof EmployeeSchema>;
export type VendorPayload = z.infer<typeof VendorSchema>;
export type CompliancePayload = z.infer<typeof ComplianceSchema>;
export type InteractionPayload = z.infer<typeof InteractionSchema>;

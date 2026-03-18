// ═══════════════════════════════════════════════════════════════
// LCS Pipeline Types — derived from PROCESS-LCS-v2.md
// ═══════════════════════════════════════════════════════════════

export interface Env {
  HD_CL: Hyperdrive;
  PIPELINE_MODE: string;
  COMPOSIO_API_KEY?: string;
  MAILGUN_API_KEY?: string;
  MAILGUN_DOMAIN?: string;
}

// ── ID Types ─────────────────────────────────────────────────
export type CommunicationId = string;  // CID-{PHASE}-{DATE}-{ULID}
export type SidId = string;            // SID-{DATE}-{ULID}
export type MessageRunId = string;     // MID-{COMM_ID}-{CHANNEL}-{ATTEMPT}

// ── Signal Queue (Ingress) ───────────────────────────────────
export interface SignalQueueRow {
  id: string;
  sovereign_company_id: string;
  signal_set_hash: string;
  signal_category: string;
  lifecycle_phase: LifecyclePhase;
  preferred_channel: Channel | null;
  agent_number: string | null;
  source_hub: string;
  status: 'PENDING' | 'COMPLETED' | 'SKIPPED' | 'FAILED';
  created_at: string;
}

// ── CID (Phase 1 Output) ────────────────────────────────────
export interface CidRow {
  communication_id: CommunicationId;
  sovereign_company_id: string;
  signal_queue_id: string;
  signal_set_hash: string;
  entity_type: string;
  entity_id: string;
  frame_id: string;
  lifecycle_phase: LifecyclePhase;
  intelligence_tier: number | null;
  compilation_status: 'COMPILED' | 'FAILED' | 'BLOCKED';
  compilation_reason: string | null;
  agent_number: string;
  lane: string;
  created_at: string;
}

// ── SID (Phase 3 Output) ────────────────────────────────────
export interface SidRow {
  sid_id: SidId;
  communication_id: CommunicationId;
  frame_id: string;
  template_id: string | null;
  subject_line: string | null;
  body_plain: string | null;
  body_html: string | null;
  sender_identity: string | null;
  sender_email: string | null;
  recipient_email: string | null;
  recipient_name: string | null;
  construction_status: 'CONSTRUCTED' | 'FAILED' | 'BLOCKED';
  construction_reason: string | null;
  created_at: string;
}

// ── MID (Phase 4 Output) ────────────────────────────────────
export interface MidRow {
  message_run_id: MessageRunId;
  communication_id: CommunicationId;
  adapter_type: string;
  channel: Channel;
  delivery_status: DeliveryStatus;
  gate_verdict: 'PASS' | 'FAIL';
  gate_reason: string | null;
  attempt_number: number;
  attempted_at: string | null;
  created_at: string;
}

// ── Event (CET — Append-Only Audit Trail) ────────────────────
export interface EventRow {
  communication_id: CommunicationId;
  message_run_id: MessageRunId | null;
  sovereign_company_id: string;
  event_type: string;
  lifecycle_phase: LifecyclePhase;
  channel: Channel | null;
  delivery_status: DeliveryStatus | null;
  step_name: string;
  payload: Record<string, unknown> | null;
  created_at: string;
}

// ── Err0 (Error Table — feeds ORBT) ─────────────────────────
export interface Err0Row {
  message_run_id: MessageRunId;
  communication_id: CommunicationId;
  sovereign_company_id: string;
  failure_type: string;
  failure_message: string;
  lifecycle_phase: LifecyclePhase;
  adapter_type: string;
  orbt_strike_number: number;
  orbt_action_taken: string;
  created_at: string;
}

// ── Enums ────────────────────────────────────────────────────
export type LifecyclePhase = 'OUTREACH' | 'SALES' | 'CLIENT';
export type Channel = 'MG' | 'HR' | 'SH';
export type DeliveryStatus = 'SENT' | 'DELIVERED' | 'BOUNCED' | 'FAILED' | 'QUEUED';

// ── Pipeline Result ──────────────────────────────────────────
export interface PipelineResult {
  cid: { total: number; compiled: number; failed: number; blocked: number };
  sid: { total: number; constructed: number; failed: number; blocked: number };
  mid: { total: number; delivered: number; failed: number; blocked: number };
  duration_ms: number;
  mode: string;
}

// ═══════════════════════════════════════════════════════════════
// Production Line Engine — Type Definitions
// ═══════════════════════════════════════════════════════════════

export interface Env {
  D1_PRODUCTION: D1Database;
  ORCHESTRATOR: DurableObjectNamespace;
  LINE_AGENT: DurableObjectNamespace;
  PRODUCTION_API_KEY: string;
}

// ── Adapter Contract ─────────────────────────────────────────

export interface AdapterRequest {
  goal_id: string;
  workpiece_id: string;
  sequence: number;
  prior_outputs: Record<string, unknown>;
  context: {
    company_name: string;
    line: string;
    phase: string;
  };
}

export interface AdapterResponse {
  success: boolean;
  station_id: string;
  result: Record<string, unknown> | null;
  error: {
    code: string;
    message: string;
    retryable: boolean;
  } | null;
  metrics: {
    duration_ms: number;
    cost_cents: number;
    tools_used: string[];
    transport: string;
  };
  timestamp: string;
}

// ── Line Definitions ─────────────────────────────────────────

export type AdapterType = 'http' | 'cli' | 'sql' | 'manual';

export interface StationDef {
  id: string;
  name: string;
  process_id: string;
  phase: string;
  depends_on: string[];
  adapter_type: AdapterType;
  adapter_target: string;
  endpoint?: string;
  runtime: string;
  orbt: string;
  conditional?: boolean;
  condition?: string;
  notes?: string;
}

export interface LineDef {
  name: string;
  silo: string;
  description: string;
  phases: string[];
  stations: StationDef[];
}

// ── Goal ─────────────────────────────────────────────────────

export type OrbtMode = 'BUILD' | 'OPERATE' | 'REPAIR' | 'TROUBLESHOOT_TRAIN';
export type StepStatus = 'pending' | 'blocked' | 'running' | 'done' | 'failed' | 'skipped' | 'not-callable';

export interface Goal {
  goal_id: string;
  sovereign_ref: string;
  hub_id: string;
  cc_layer: string;
  line: string;
  phase: string | null;
  workpiece_id: string;
  workpiece_name: string | null;
  ctb_placement: string;
  orbt_mode: OrbtMode;
  certified_by: string | null;
  certified_at: string | null;
  strike_count: number;
  source: string;
  inbox_task_id: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  updated_at: string;
}

export interface Step {
  step_id: string;
  goal_id: string;
  station_id: string;
  sequence: number;
  depends_on: string;
  adapter_type: AdapterType;
  adapter_target: string;
  conditional: number;
  condition_desc: string | null;
  status: StepStatus;
  result: string | null;
  error_code: string | null;
  error_message: string | null;
  retryable: number;
  retry_count: number;
  duration_ms: number | null;
  cost_cents: number;
  tools_used: string;
  transport: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

// ── Agent State ──────────────────────────────────────────────

export interface LineAgentState {
  active_goal_id: string | null;
  line: string | null;
  status: 'idle' | 'running' | 'halted' | 'awaiting_certification';
  last_station_completed: string | null;
  last_error: string | null;
  goals_completed: number;
  goals_failed: number;
  updated_at: string;
}

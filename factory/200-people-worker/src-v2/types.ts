/**
 * Process 200 — People Worker v2 (Rewired)
 *
 * Operates directly on svg-d1-outreach-ops. No standalone D1.
 * Two phases: Pass 1 (fill slots), Pass 2 (detect movement).
 * Fetches via UT: Startpage through DataImpulse residential proxy.
 */

export interface Env {
  // Outreach D1 — reads/updates people_people_master, people_company_slot
  D1_OUTREACH: D1Database;
  // Spine D1 — writes movement signals to lcs_signal_queue
  D1_SPINE: D1Database;
  // DataImpulse residential proxy (from Doppler)
  PROXY_HOST: string;
  PROXY_PORT: string;
  PROXY_USER: string;
  PROXY_PASS: string;
  // Batch config
  BATCH_SIZE: string;       // profiles per cron invocation (default: 50)
  MIN_DELAY_MS: string;     // min delay between fetches (default: 30000)
  MAX_DELAY_MS: string;     // max delay between fetches (default: 120000)
}

/** A company with slot fill status, ordered by priority */
export interface CompanySlotSummary {
  company_unique_id: string;
  outreach_id: string;
  canonical_name: string;
  city: string;
  state: string;
  filled_slots: number;
  total_slots: number;
  has_dol: number;
}

/** An empty slot that needs discovery */
export interface EmptySlot {
  slot_id: string;
  outreach_id: string;
  company_unique_id: string;
  slot_type: string;
  canonical_name: string;
  company_domain: string;
  city: string;
  state: string;
}

/** A filled slot that needs movement check */
export interface FilledSlot {
  slot_id: string;
  outreach_id: string;
  company_unique_id: string;
  slot_type: string;
  person_unique_id: string;
  linkedin_url: string;
  full_name: string;
  title: string;
  email: string;
}

/** Result from Startpage search */
export interface SearchResult {
  name: string;
  title: string;
  company: string;
  linkedin_url: string;
  source_tool: string;
  raw_snippet: string;
}

/** Movement detection result */
export interface MovementResult {
  movement: 0 | 1;
  movement_type: 'NONE' | 'TITLE_CHANGED' | 'COMPANY_CHANGED' | 'BOTH_CHANGED';
  old_title: string;
  new_title: string;
  old_company: string;
  new_company: string;
}

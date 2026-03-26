/**
 * Process 200 — People Worker v2 (Rewired)
 *
 * Operates directly on svg-d1-outreach-ops. No standalone D1.
 * Two phases: Pass 1 (fill slots), Pass 2 (detect movement).
 * Fetches via UT: Startpage through DataImpulse residential proxy.
 *
 * Table schemas match what's actually in D1 (verified against compiler-v2.ts
 * and seed.ts in lcs-hub — the source of truth for column names).
 */

export interface Env {
  // Outreach D1 — reads/updates people_people_master, people_company_slot
  D1_OUTREACH: D1Database;
  // Spine D1 — reads cl_company_identity, writes movement signals to lcs_signal_queue
  D1_SPINE: D1Database;
  // DataImpulse residential proxy (from Doppler)
  PROXY_GATEWAY_URL: string;  // DataImpulse HTTP gateway (not CONNECT)
  PROXY_API_KEY: string;      // DataImpulse auth key
  // Batch config
  BATCH_SIZE: string;       // profiles per cron invocation (default: 50)
  MIN_DELAY_MS: string;     // min delay between fetches (default: 30000)
  MAX_DELAY_MS: string;     // max delay between fetches (default: 120000)
}

/**
 * An empty slot that needs discovery.
 *
 * Join: people_company_slot cs
 *       JOIN outreach_company_target ct ON cs.outreach_id = ct.outreach_id
 *       LEFT JOIN cl_company_identity ci ON cs.outreach_id = ci.outreach_id (spine D1)
 *
 * people_company_slot columns: outreach_id, slot_type, person_unique_id, is_filled
 * Company name comes from cl_company_identity.canonical_name (spine D1).
 */
export interface EmptySlot {
  outreach_id: string;
  slot_type: string;             // CEO, CFO, HR
  company_unique_id: string;     // from outreach_company_target
  canonical_name: string;        // from cl_company_identity (spine)
  company_domain: string;        // from cl_company_identity (spine)
  city: string;                  // from outreach_company_target
  state: string;                 // from outreach_company_target
}

/**
 * A filled slot that needs movement check.
 *
 * Join: people_company_slot cs
 *       JOIN people_people_master pm ON cs.person_unique_id = pm.unique_id
 */
export interface FilledSlot {
  outreach_id: string;
  slot_type: string;
  person_unique_id: string;      // people_company_slot.person_unique_id
  unique_id: string;             // people_people_master.unique_id (same value)
  linkedin_url: string;
  full_name: string;
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  company_unique_id: string;
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

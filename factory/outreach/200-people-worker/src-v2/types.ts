/**
 * Process 200 — People Worker v2
 *
 * Operates on svg-d1-outreach-ops (D1_OUTREACH) + svg-d1-spine (D1_SPINE read-only).
 * No standalone D1. No Neon during WORK phase.
 *
 * Four passes: promote staging → scrape about pages → search proxy → movement detection
 */

export interface Env {
  D1_OUTREACH: D1Database;
  D1_SPINE: D1Database;
  PROXY_HOST: string;
  PROXY_PORT: string;
  PROXY_USER: string;
  PROXY_PASS: string;
  BATCH_SIZE: string;
  MIN_DELAY_MS: string;
  MAX_DELAY_MS: string;
}

export interface EmptySlot {
  slot_id: string;
  outreach_id: string;
  company_unique_id: string;
  slot_type: 'CEO' | 'CFO' | 'HR';
  city: string;
  state: string;
  filing_present: number | null;
  about_url: string | null;
}

export interface FilledSlot {
  slot_id: string;
  outreach_id: string;
  slot_type: string;
  person_unique_id: string;
  unique_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  title: string;
  email: string;
  linkedin_url: string;
  last_enrichment_attempt: string | null;
}

export interface StagingPerson {
  id: number;
  company_unique_id: string;
  first_name: string | null;
  last_name: string | null;
  raw_name: string | null;
  raw_title: string | null;
  normalized_title: string | null;
  mapped_slot_type: string | null;
  linkedin_url: string | null;
  email: string | null;
  confidence_score: number | null;
}

export interface TitleSlotMap {
  title_pattern: string;
  slot_type: string;
  priority: number;
}

export interface CompanyIdentity {
  canonical_name: string;
  company_domain: string | null;
  linkedin_company_url: string | null;
}

export interface SearchResult {
  name: string;
  title: string;
  company: string;
  linkedin_url: string;
  source: string;
  raw_snippet: string;
}

export interface MovementResult {
  movement: 0 | 1;
  movement_type: 'NONE' | 'TITLE_CHANGED' | 'COMPANY_CHANGED' | 'BOTH_CHANGED';
  old_title: string;
  new_title: string;
  old_company: string;
  new_company: string;
}

export interface PassResult {
  pass: string;
  processed: number;
  filled: number;
  skipped: number;
  errors: number;
  error_details: string[];
}

/**
 * Intelligence Engine — Type Definitions
 *
 * Shared types for the queue-based scraping engine.
 * One queue, multiple job types, same proxy infrastructure.
 */

// ── Job Types (the variable — what changes per query) ─────

export type JobType =
  | 'linkedin_profile'      // Person movement detection
  | 'linkedin_company'      // Company page — employee count, industry
  | 'glassdoor_sentiment'   // Employee reviews, benefits complaints
  | 'indeed_hiring'         // Job postings for buyer persona
  | 'blog_freshness'        // Website content freshness check
  | 'company_news'          // Recent news, M&A, funding
  | 'slot_search'           // Find CEO/CFO/HR for empty slots
  | 'state_wc_lookup';      // Workers comp coverage by state

// ── Queue Message ──────────────────────────────────────────

export interface IntelligenceJob {
  job_id: string;
  job_type: JobType;
  company_unique_id: string;
  company_name: string;
  company_domain?: string;
  agent_name: string;

  // Person-specific (for linkedin_profile, slot_search)
  person_id?: string;
  person_name?: string;
  linkedin_url?: string;
  stored_title?: string;
  slot_type?: string;

  // Query customization
  search_query?: string;       // Override auto-generated query
  search_engine?: 'startpage' | 'brave' | 'duckduckgo';

  // Metadata
  priority: number;            // Lower = higher priority
  attempt: number;             // Retry count
  max_attempts: number;
  created_at: string;
}

// ── Query Templates (the constants — structure that doesn't change) ─

export interface QueryTemplate {
  job_type: JobType;
  query_template: string;      // e.g., '"{company}" site:glassdoor.com reviews'
  signal_type: string;
  description: string;
  keywords: string[];          // For relevance scoring
  weight: number;              // Signal weight for BIT scoring
}

// ── Fetch Result ───────────────────────────────────────────

export interface FetchResult {
  job_id: string;
  job_type: JobType;
  company_unique_id: string;
  person_id?: string;

  // Search result
  search_engine: string;
  http_status: number;
  raw_snippet: string;
  parsed_data: Record<string, string>;

  // Signal detection
  signal_type: string;
  signal_score: number;
  keyword_matches: string[];

  // Movement detection (linkedin_profile only)
  movement_detected?: 0 | 1;
  movement_type?: string;

  // Metadata
  fetched_at: string;
  duration_ms: number;
  proxy_used: boolean;
  error: string | null;
}

// ── Env Bindings ───────────────────────────────────────────

export interface Env {
  D1: D1Database;
  INTELLIGENCE_QUEUE: Queue<IntelligenceJob>;
  NEON_URL: string;
  PROXY_USER: string;
  PROXY_PASS: string;
  PROXY_HOST: string;
  PROXY_PORT: string;
}

/**
 * Intelligence Engine — Search Abstraction
 *
 * Primary: Startpage (direct fetch from CF Worker — no proxy initially)
 * Fallback: Brave Search API (planned)
 *
 * CF Workers fetch directly. If Startpage blocks CF IPs, we add
 * a proxy relay worker or switch to Brave Search API.
 */

import type { IntelligenceJob } from './types';
import { QUERY_TEMPLATES, SLOT_KEYWORDS } from './templates';

// ── Search Result ────────────────────────────────────────────

export interface SearchResult {
  title: string;
  snippet: string;
  url: string;
}

export interface SearchResponse {
  engine: string;
  status: number;
  results: SearchResult[];
  raw_html_length: number;
  captcha_detected: boolean;
  error: string | null;
}

// ── Query Builder ────────────────────────────────────────────

export function buildQuery(job: IntelligenceJob): string {
  // If job has an explicit search_query override, use it
  if (job.search_query) {
    return job.search_query;
  }

  const template = QUERY_TEMPLATES[job.job_type];
  if (!template) {
    throw new Error(`No template for job type: ${job.job_type}`);
  }

  let query = template.query_template;

  // Fill template variables
  query = query.replace('{company}', job.company_name);
  query = query.replace('{person_name}', job.person_name ?? '');
  query = query.replace('{domain}', job.company_domain ?? '');
  query = query.replace('{state}', job.state ?? '');

  // Slot search needs keyword expansion
  if (job.job_type === 'slot_search' && job.slot_type) {
    const keywords = SLOT_KEYWORDS[job.slot_type] ?? job.slot_type;
    query = query.replace('{slot_keywords}', keywords);
  }

  return query.trim();
}

// ── Startpage Fetch ──────────────────────────────────────────

/**
 * Fetch search results from Startpage.
 *
 * Direct fetch from CF Worker (no proxy). Startpage is privacy-focused
 * and generally does not block datacenter IPs as aggressively as Google.
 * If blocking occurs, we'll add DataImpulse proxy relay.
 */
export async function fetchStartpage(query: string): Promise<SearchResponse> {
  const url = new URL('https://www.startpage.com/sp/search');
  url.searchParams.set('query', query);
  url.searchParams.set('cat', 'web');
  url.searchParams.set('language', 'english');

  try {
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
      },
    });

    const html = await response.text();

    // CAPTCHA / block detection
    const captchaDetected = detectCaptcha(html);
    if (captchaDetected) {
      return {
        engine: 'startpage',
        status: response.status,
        results: [],
        raw_html_length: html.length,
        captcha_detected: true,
        error: 'CAPTCHA_DETECTED',
      };
    }

    // Parse search results from HTML
    const results = parseStartpageResults(html);

    return {
      engine: 'startpage',
      status: response.status,
      results,
      raw_html_length: html.length,
      captcha_detected: false,
      error: null,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      engine: 'startpage',
      status: 0,
      results: [],
      raw_html_length: 0,
      captcha_detected: false,
      error: `FETCH_ERROR: ${message}`,
    };
  }
}

// ── Startpage HTML Parser ────────────────────────────────────

/**
 * Parse Startpage search results from raw HTML.
 *
 * Startpage renders results in <div class="w-gl__result"> blocks.
 * Each block contains:
 *   - <a class="w-gl__result-url"> — the URL
 *   - <h3> or <a class="w-gl__result-title"> — the title
 *   - <p class="w-gl__description"> — the snippet
 *
 * This parser is intentionally simple and regex-based.
 * If Startpage changes their HTML structure, update these patterns.
 */
function parseStartpageResults(html: string): SearchResult[] {
  const results: SearchResult[] = [];

  // Strategy 1: Look for structured result blocks
  // Startpage uses w-gl__result as the container class
  const resultBlockPattern = /class="w-gl__result"[\s\S]*?(?=class="w-gl__result"|<footer|$)/gi;
  const blocks = html.match(resultBlockPattern) ?? [];

  for (const block of blocks) {
    const result = parseResultBlock(block);
    if (result) {
      results.push(result);
    }
  }

  // Strategy 2: If no structured results found, try generic link+text extraction
  if (results.length === 0) {
    const fallbackResults = parseFallbackResults(html);
    results.push(...fallbackResults);
  }

  return results.slice(0, 10); // Cap at 10 results
}

function parseResultBlock(block: string): SearchResult | null {
  // Extract URL
  const urlMatch = block.match(/href="(https?:\/\/[^"]+)"/);
  const url = urlMatch?.[1] ?? '';

  // Extract title — look in <h3> or title-class elements
  const titleMatch =
    block.match(/<h3[^>]*>([\s\S]*?)<\/h3>/) ??
    block.match(/class="[^"]*title[^"]*"[^>]*>([\s\S]*?)<\//) ??
    block.match(/<a[^>]*>([\s\S]*?)<\/a>/);
  const title = stripHtml(titleMatch?.[1] ?? '');

  // Extract snippet/description
  const snippetMatch =
    block.match(/class="[^"]*description[^"]*"[^>]*>([\s\S]*?)<\//) ??
    block.match(/<p[^>]*>([\s\S]*?)<\/p>/);
  const snippet = stripHtml(snippetMatch?.[1] ?? '');

  if (!url && !title && !snippet) {
    return null;
  }

  return { title, snippet, url };
}

function parseFallbackResults(html: string): SearchResult[] {
  const results: SearchResult[] = [];

  // Look for any anchor tags followed by text content
  const linkPattern = /<a[^>]+href="(https?:\/\/[^"]+)"[^>]*>([\s\S]*?)<\/a>/gi;
  let match;
  let count = 0;

  while ((match = linkPattern.exec(html)) !== null && count < 10) {
    const url = match[1];
    const title = stripHtml(match[2]);

    // Skip navigation / internal links
    if (url.includes('startpage.com') || title.length < 5) {
      continue;
    }

    results.push({
      title,
      snippet: '',
      url,
    });
    count++;
  }

  return results;
}

// ── CAPTCHA Detection ────────────────────────────────────────

function detectCaptcha(html: string): boolean {
  const captchaSignals = [
    'captcha',
    'recaptcha',
    'hcaptcha',
    'challenge-form',
    'challenge-running',
    'cf-challenge',
    'please verify',
    'are you a robot',
    'unusual traffic',
    'automated queries',
  ];

  const lower = html.toLowerCase();
  return captchaSignals.some((signal) => lower.includes(signal));
}

// ── Utilities ────────────────────────────────────────────────

function stripHtml(html: string): string {
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

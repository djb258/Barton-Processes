/**
 * Intelligence Engine — Result Parsers
 *
 * Each job type has a dedicated parser that extracts structured data
 * from raw search results. Parsers produce:
 *   - parsed_data: key-value pairs of extracted info
 *   - signal_score: 0-100 relevance/signal score
 *   - keyword_matches: which keywords were found
 *   - movement_detected / movement_type (linkedin_profile only)
 */

import type { IntelligenceJob, FetchResult, JobType } from './types';
import type { SearchResult } from './search';
import { QUERY_TEMPLATES } from './templates';

// ── Master Parser Dispatcher ─────────────────────────────────

export function parseResults(
  job: IntelligenceJob,
  results: SearchResult[],
  httpStatus: number,
  durationMs: number,
  error: string | null,
): FetchResult {
  const template = QUERY_TEMPLATES[job.job_type];
  const combinedSnippet = results
    .map((r) => `${r.title} | ${r.snippet} | ${r.url}`)
    .join('\n');

  // Base result — parsers fill in the specifics
  const base: FetchResult = {
    job_id: job.job_id,
    job_type: job.job_type,
    company_unique_id: job.company_unique_id,
    person_id: job.person_id,
    search_engine: 'startpage',
    http_status: httpStatus,
    raw_snippet: combinedSnippet.slice(0, 4000), // cap storage
    parsed_data: {},
    signal_type: template?.signal_type ?? 'UNKNOWN',
    signal_score: 0,
    keyword_matches: [],
    fetched_at: new Date().toISOString(),
    duration_ms: durationMs,
    error,
  };

  if (error || results.length === 0) {
    base.signal_score = 0;
    return base;
  }

  // Dispatch to type-specific parser
  const parser = PARSERS[job.job_type];
  if (parser) {
    return parser(job, results, base);
  }

  return base;
}

// ── Type-Specific Parsers ────────────────────────────────────

type Parser = (
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
) => FetchResult;

const PARSERS: Record<JobType, Parser> = {
  linkedin_profile: parseLinkedInProfile,
  linkedin_company: parseLinkedInCompany,
  glassdoor_sentiment: parseGlassdoorSentiment,
  indeed_hiring: parseIndeedHiring,
  blog_freshness: parseBlogFreshness,
  company_news: parseCompanyNews,
  slot_search: parseSlotSearch,
  state_wc_lookup: parseStateWcLookup,
};

// ── LinkedIn Profile Parser ──────────────────────────────────

/**
 * Parse LinkedIn profile search results.
 * Snippet format: "Name - Title at Company | LinkedIn"
 *
 * Detects movement by comparing snippet title/company to stored values.
 */
function parseLinkedInProfile(
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
): FetchResult {
  // Find the LinkedIn profile result
  const profileResult = results.find(
    (r) => r.url.includes('linkedin.com/in/') || r.title.includes('LinkedIn'),
  );

  if (!profileResult) {
    base.signal_score = 0;
    base.parsed_data = { status: 'NO_LINKEDIN_RESULT' };
    return base;
  }

  // Parse "Name - Title at Company | LinkedIn" pattern
  const titleParts = profileResult.title
    .replace(/\s*\|\s*LinkedIn.*$/i, '')
    .replace(/\s*-\s*LinkedIn.*$/i, '')
    .trim();

  const dashSplit = titleParts.split(/\s+-\s+/);
  const extractedName = dashSplit[0]?.trim() ?? '';
  const titleAndCompany = dashSplit.slice(1).join(' - ').trim();

  // Try to split "Title at Company"
  const atSplit = titleAndCompany.split(/\s+at\s+/i);
  const extractedTitle = atSplit[0]?.trim() ?? '';
  const extractedCompany = atSplit.slice(1).join(' at ').trim();

  base.parsed_data = {
    extracted_name: extractedName,
    extracted_title: extractedTitle,
    extracted_company: extractedCompany,
    linkedin_url: profileResult.url,
    snippet: profileResult.snippet.slice(0, 500),
  };

  // Movement detection
  const storedTitle = (job.stored_title ?? '').toLowerCase();
  const currentTitle = extractedTitle.toLowerCase();
  const storedCompany = job.company_name.toLowerCase();
  const currentCompany = extractedCompany.toLowerCase();

  if (extractedCompany && extractedTitle) {
    // Company changed
    if (currentCompany && !currentCompany.includes(storedCompany) && !storedCompany.includes(currentCompany)) {
      base.movement_detected = 1;
      base.movement_type = 'COMPANY_CHANGE';
      base.signal_score = 95;
      base.keyword_matches.push('company_change');
    }
    // Title changed but same company
    else if (storedTitle && currentTitle && currentTitle !== storedTitle) {
      base.movement_detected = 1;
      base.movement_type = 'TITLE_CHANGE';
      base.signal_score = 60;
      base.keyword_matches.push('title_change');
    }
    // No change detected
    else {
      base.movement_detected = 0;
      base.movement_type = 'NO_CHANGE';
      base.signal_score = 10;
    }
  } else {
    base.movement_detected = 0;
    base.movement_type = 'PARSE_INCOMPLETE';
    base.signal_score = 5;
  }

  return base;
}

// ── LinkedIn Company Parser ──────────────────────────────────

function parseLinkedInCompany(
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
): FetchResult {
  const companyResult = results.find(
    (r) => r.url.includes('linkedin.com/company/'),
  );

  if (!companyResult) {
    base.parsed_data = { status: 'NO_COMPANY_RESULT' };
    return base;
  }

  const combined = `${companyResult.title} ${companyResult.snippet}`.toLowerCase();

  // Extract employee count patterns
  const empMatch = combined.match(/(\d[\d,]+)\s*(?:\+\s*)?employees?/i);
  const industryMatch = combined.match(/industry[:\s]+([^|.]+)/i);

  base.parsed_data = {
    linkedin_url: companyResult.url,
    employee_count: empMatch?.[1]?.replace(/,/g, '') ?? '',
    industry: industryMatch?.[1]?.trim() ?? '',
    snippet: companyResult.snippet.slice(0, 500),
  };

  base.keyword_matches = matchKeywords(combined, QUERY_TEMPLATES.linkedin_company.keywords);
  base.signal_score = Math.min(base.keyword_matches.length * 15, 100);

  return base;
}

// ── Glassdoor Sentiment Parser ───────────────────────────────

/**
 * Score Glassdoor reviews for benefits-related sentiment.
 * Positive keywords (benefits, insurance) boost score.
 * Negative keywords (complaints, poor) also boost — indicates opportunity.
 */
function parseGlassdoorSentiment(
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
): FetchResult {
  const combined = results
    .map((r) => `${r.title} ${r.snippet}`)
    .join(' ')
    .toLowerCase();

  const keywords = QUERY_TEMPLATES.glassdoor_sentiment.keywords;
  const negativeKeywords = [
    'poor benefits', 'no insurance', 'terrible', 'worst',
    'complaints', 'underpaid', 'overworked', 'high turnover',
  ];
  const positiveKeywords = [
    'great benefits', 'good insurance', 'excellent', 'recommend',
  ];

  const keywordHits = matchKeywords(combined, keywords);
  const negativeHits = matchKeywords(combined, negativeKeywords);
  const positiveHits = matchKeywords(combined, positiveKeywords);

  // Extract rating if present (e.g., "3.2" or "4.5 stars")
  const ratingMatch = combined.match(/(\d\.\d)\s*(?:stars?|rating|out of)/i);

  base.parsed_data = {
    keyword_hits: keywordHits.join(', '),
    negative_hits: negativeHits.join(', '),
    positive_hits: positiveHits.join(', '),
    rating: ratingMatch?.[1] ?? '',
    result_count: String(results.length),
  };

  base.keyword_matches = [...keywordHits, ...negativeHits];

  // Scoring: more keyword hits = stronger signal
  // Negative sentiment actually increases opportunity (they need better benefits)
  const baseScore = keywordHits.length * 10;
  const negativeBoost = negativeHits.length * 15;
  const positiveDeduction = positiveHits.length * 5;
  base.signal_score = Math.min(baseScore + negativeBoost - positiveDeduction, 100);
  base.signal_score = Math.max(base.signal_score, 0);

  return base;
}

// ── Indeed Hiring Parser ─────────────────────────────────────

/**
 * Detect buyer persona job postings (benefits/HR roles).
 * High signal — company is actively hiring for roles we sell to.
 */
function parseIndeedHiring(
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
): FetchResult {
  const combined = results
    .map((r) => `${r.title} ${r.snippet}`)
    .join(' ')
    .toLowerCase();

  const buyerRoles = QUERY_TEMPLATES.indeed_hiring.keywords;
  const hits = matchKeywords(combined, buyerRoles);

  // Count distinct job postings
  const jobPostCount = results.filter(
    (r) => r.url.includes('indeed.com') && r.title.toLowerCase().includes(job.company_name.toLowerCase()),
  ).length;

  base.parsed_data = {
    buyer_role_hits: hits.join(', '),
    job_post_count: String(jobPostCount),
    result_count: String(results.length),
  };

  base.keyword_matches = hits;

  // Each buyer persona match is very high signal
  base.signal_score = Math.min(hits.length * 25 + jobPostCount * 10, 100);

  return base;
}

// ── Blog Freshness Parser ────────────────────────────────────

/**
 * Check how recently the company's website has been indexed.
 * Looks for recent dates in search results.
 */
function parseBlogFreshness(
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
): FetchResult {
  const combined = results
    .map((r) => `${r.title} ${r.snippet}`)
    .join(' ');

  const keywords = QUERY_TEMPLATES.blog_freshness.keywords;
  const hits = matchKeywords(combined.toLowerCase(), keywords);

  // Look for recent dates (2025, 2026, month names)
  const recentDatePatterns = [
    /202[56]/g,
    /(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+202[56]/gi,
  ];

  let recentDates = 0;
  for (const pattern of recentDatePatterns) {
    const matches = combined.match(pattern);
    recentDates += matches?.length ?? 0;
  }

  base.parsed_data = {
    recent_date_count: String(recentDates),
    indexed_pages: String(results.length),
    keywords_found: hits.join(', '),
  };

  base.keyword_matches = hits;
  base.signal_score = Math.min(recentDates * 10 + results.length * 5, 100);

  return base;
}

// ── Company News Parser ──────────────────────────────────────

/**
 * Detect significant company events: M&A, funding, expansion, layoffs.
 * These are high-signal triggers for outreach timing.
 */
function parseCompanyNews(
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
): FetchResult {
  const combined = results
    .map((r) => `${r.title} ${r.snippet}`)
    .join(' ')
    .toLowerCase();

  const keywords = QUERY_TEMPLATES.company_news.keywords;
  const hits = matchKeywords(combined, keywords);

  // Categorize the news type
  const categories: Record<string, string[]> = {
    growth: ['expansion', 'funding', 'ipo', 'partnership', 'new office', 'growing'],
    contraction: ['layoff', 'downsizing', 'restructuring', 'closing'],
    change: ['acquisition', 'merger', 'leadership', 'new ceo', 'transition'],
  };

  const detectedCategories: string[] = [];
  for (const [category, words] of Object.entries(categories)) {
    if (words.some((w) => combined.includes(w))) {
      detectedCategories.push(category);
    }
  }

  base.parsed_data = {
    news_categories: detectedCategories.join(', ') || 'none',
    keyword_hits: hits.join(', '),
    result_count: String(results.length),
    top_headline: results[0]?.title?.slice(0, 200) ?? '',
  };

  base.keyword_matches = hits;
  // News events are very actionable
  base.signal_score = Math.min(hits.length * 15 + detectedCategories.length * 20, 100);

  return base;
}

// ── Slot Search Parser ───────────────────────────────────────

/**
 * Extract candidate names from LinkedIn search results.
 * Looking for "Name - Title at Company" patterns.
 */
function parseSlotSearch(
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
): FetchResult {
  const candidates: Array<{ name: string; title: string; url: string }> = [];

  for (const result of results) {
    if (!result.url.includes('linkedin.com/in/')) {
      continue;
    }

    // Parse "Name - Title at Company | LinkedIn"
    const cleaned = result.title
      .replace(/\s*\|\s*LinkedIn.*$/i, '')
      .replace(/\s*-\s*LinkedIn.*$/i, '')
      .trim();

    const dashSplit = cleaned.split(/\s+-\s+/);
    const name = dashSplit[0]?.trim() ?? '';
    const titleAtCompany = dashSplit.slice(1).join(' - ').trim();

    if (name && name.split(/\s+/).length >= 2) {
      candidates.push({
        name,
        title: titleAtCompany,
        url: result.url,
      });
    }
  }

  base.parsed_data = {
    slot_type: job.slot_type ?? '',
    candidate_count: String(candidates.length),
    candidates: JSON.stringify(candidates.slice(0, 5)),
  };

  base.keyword_matches = candidates.map((c) => c.name);
  base.signal_score = Math.min(candidates.length * 20, 100);

  return base;
}

// ── State Workers Comp Parser ────────────────────────────────

function parseStateWcLookup(
  job: IntelligenceJob,
  results: SearchResult[],
  base: FetchResult,
): FetchResult {
  const combined = results
    .map((r) => `${r.title} ${r.snippet}`)
    .join(' ')
    .toLowerCase();

  const keywords = QUERY_TEMPLATES.state_wc_lookup.keywords;
  const hits = matchKeywords(combined, keywords);

  // Look for carrier names
  const carrierPatterns = [
    /(?:hartford|travelers|liberty mutual|state fund|zurich|chubb|ace|tokio|berkshire)/gi,
  ];

  const carriers: string[] = [];
  for (const pattern of carrierPatterns) {
    const matches = combined.match(pattern);
    if (matches) {
      carriers.push(...matches.map((m) => m.trim()));
    }
  }

  base.parsed_data = {
    state: job.state ?? '',
    carriers_found: [...new Set(carriers)].join(', '),
    keyword_hits: hits.join(', '),
    result_count: String(results.length),
  };

  base.keyword_matches = hits;
  base.signal_score = Math.min(hits.length * 15 + carriers.length * 20, 100);

  return base;
}

// ── Utility ──────────────────────────────────────────────────

function matchKeywords(text: string, keywords: string[]): string[] {
  return keywords.filter((kw) => text.includes(kw.toLowerCase()));
}

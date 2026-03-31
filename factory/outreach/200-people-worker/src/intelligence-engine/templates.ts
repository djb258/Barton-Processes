/**
 * Intelligence Engine — Query Templates
 *
 * These are the CONSTANTS. The query structure never changes.
 * Only the company name / person name / domain fills the template.
 */

import type { QueryTemplate, JobType } from './types';

export const QUERY_TEMPLATES: Record<JobType, QueryTemplate> = {
  linkedin_profile: {
    job_type: 'linkedin_profile',
    query_template: '{person_name} linkedin',
    signal_type: 'PERSON_MOVEMENT',
    description: 'LinkedIn profile — title + company from search snippet',
    keywords: ['linkedin.com/in/'],
    weight: 10,
  },

  linkedin_company: {
    job_type: 'linkedin_company',
    query_template: '"{company}" site:linkedin.com/company',
    signal_type: 'COMPANY_PROFILE',
    description: 'LinkedIn company page — employee count, industry, specialties',
    keywords: ['employees', 'industry', 'headquarters', 'founded', 'specialties'],
    weight: 5,
  },

  glassdoor_sentiment: {
    job_type: 'glassdoor_sentiment',
    query_template: '"{company}" site:glassdoor.com reviews',
    signal_type: 'BENEFITS_SENTIMENT',
    description: 'Glassdoor reviews — benefits satisfaction, HR complaints',
    keywords: ['benefits', 'insurance', 'health', 'HR', '401k', 'PTO', 'management', 'compensation'],
    weight: 8,
  },

  indeed_hiring: {
    job_type: 'indeed_hiring',
    query_template: '"{company}" site:indeed.com "benefits" OR "HR" OR "human resources"',
    signal_type: 'HIRING_SIGNAL',
    description: 'Indeed job postings — hiring for buyer persona (benefits/HR roles)',
    keywords: ['benefits manager', 'HR manager', 'benefits administrator', 'human resources', 'benefits coordinator'],
    weight: 12,
  },

  blog_freshness: {
    job_type: 'blog_freshness',
    query_template: 'site:{domain}',
    signal_type: 'CONTENT_ACTIVITY',
    description: 'Website content freshness — recently indexed pages',
    keywords: ['2026', '2025', 'blog', 'news', 'press', 'announcement', 'update'],
    weight: 3,
  },

  company_news: {
    job_type: 'company_news',
    query_template: '"{company}" news 2026',
    signal_type: 'NEWS_EVENT',
    description: 'Recent company news — M&A, funding, expansion, leadership',
    keywords: ['acquisition', 'funding', 'expansion', 'layoff', 'merger', 'IPO', 'partnership', 'leadership'],
    weight: 10,
  },

  slot_search: {
    job_type: 'slot_search',
    query_template: '"{company}" {slot_keywords} site:linkedin.com',
    signal_type: 'SLOT_CANDIDATE',
    description: 'Find CEO/CFO/HR contacts for empty slots',
    keywords: ['linkedin.com/in/'],
    weight: 0, // Not a signal — it's a data fill
  },

  state_wc_lookup: {
    job_type: 'state_wc_lookup',
    query_template: '"{company}" workers compensation {state}',
    signal_type: 'WC_COVERAGE',
    description: 'Workers comp coverage verification by state',
    keywords: ['workers compensation', 'coverage', 'carrier', 'policy', 'insurance'],
    weight: 5,
  },
};

// Slot search keywords per slot type
export const SLOT_KEYWORDS: Record<string, string> = {
  CEO: 'CEO OR "Chief Executive" OR President OR "General Manager"',
  CFO: 'CFO OR "Chief Financial" OR "VP Finance" OR Controller',
  HR: '"HR" OR "Human Resources" OR CHRO OR "Benefits" OR "People Officer"',
};

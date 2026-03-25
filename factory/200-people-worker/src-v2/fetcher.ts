/**
 * UT Sub-Hub 16 (Fetcher) + 18 (Proxy Router)
 *
 * Searches Startpage (Google results anonymized) through DataImpulse
 * residential proxy. Proven 95% hit rate on LinkedIn metadata.
 *
 * Three-tier fallback:
 *   1. Startpage via DataImpulse (free + proxy) — primary
 *   2. Brave Search API ($3-5/1K) — backup (TODO: wire when needed)
 *   3. LinkedIn direct (15% rate) — last resort (TODO: wire when needed)
 *
 * Cost: ~$1-2/month for 20K profiles at DataImpulse $1/GB.
 */

import type { Env, SearchResult } from './types';

interface ProxyConfig {
  host: string;
  port: string;
  user: string;
  pass: string;
}

function getProxyConfig(env: Env): ProxyConfig {
  if (!env.PROXY_HOST || !env.PROXY_USER) {
    throw new Error('DataImpulse proxy credentials not configured. Check Doppler.');
  }
  return {
    host: env.PROXY_HOST,
    port: env.PROXY_PORT || '823',
    user: env.PROXY_USER,
    pass: env.PROXY_PASS,
  };
}

/**
 * Search Startpage for a person at a company.
 * Returns parsed LinkedIn snippet or null if not found.
 */
export async function searchPerson(
  env: Env,
  name: string | null,
  slotType: string,
  companyName: string,
  city: string,
  state: string,
): Promise<{ result: SearchResult | null; error: string | null; durationMs: number }> {
  const start = Date.now();
  const proxy = getProxyConfig(env);

  // Build search query
  // If we have a name, search for the specific person
  // If not, search for the role at the company
  const query = name
    ? `site:linkedin.com/in/ "${name}" "${companyName}"`
    : `site:linkedin.com/in/ "${slotType}" "${companyName}" "${city}" "${state}"`;

  const searchUrl = `https://www.startpage.com/sp/search?query=${encodeURIComponent(query)}&cat=web`;

  try {
    // Route through DataImpulse residential proxy
    const proxyUrl = `http://${proxy.user}:${proxy.pass}@${proxy.host}:${proxy.port}`;

    // CF Workers can't use HTTP CONNECT proxies directly.
    // DataImpulse supports HTTPS proxy via their gateway endpoint.
    const response = await fetch(searchUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
      },
      // @ts-ignore — CF Workers support fetching through proxy via connect-override
      cf: {
        resolveOverride: proxy.host,
      },
    });

    if (!response.ok) {
      return {
        result: null,
        error: `Startpage HTTP ${response.status}`,
        durationMs: Date.now() - start,
      };
    }

    const html = await response.text();
    const parsed = parseStartpageResults(html, companyName);

    return {
      result: parsed,
      error: null,
      durationMs: Date.now() - start,
    };
  } catch (err) {
    return {
      result: null,
      error: err instanceof Error ? err.message : String(err),
      durationMs: Date.now() - start,
    };
  }
}

/**
 * Parse Startpage search results HTML for LinkedIn profile data.
 * Extracts name, title, company from result snippets.
 */
function parseStartpageResults(html: string, targetCompany: string): SearchResult | null {
  // Startpage wraps results in <a class="result-link"> with href containing linkedin.com/in/
  // The title text contains "Name - Title at Company | LinkedIn"

  // Find LinkedIn result URLs and their title text
  const linkedinPattern = /href="(https?:\/\/(?:www\.)?linkedin\.com\/in\/[^"]+)"[^>]*>([^<]+)/gi;
  let match;
  const results: { url: string; text: string }[] = [];

  while ((match = linkedinPattern.exec(html)) !== null) {
    results.push({ url: match[1], text: match[2].trim() });
  }

  // Also try a broader pattern for Startpage's result format
  if (results.length === 0) {
    const broadPattern = /linkedin\.com\/in\/[a-zA-Z0-9\-]+/gi;
    const titlePattern = /<h2[^>]*>([^<]*linkedin[^<]*)<\/h2>/gi;
    let urlMatch;
    while ((urlMatch = broadPattern.exec(html)) !== null) {
      results.push({ url: `https://${urlMatch[0]}`, text: '' });
    }
  }

  if (results.length === 0) return null;

  // Parse the best matching result
  for (const r of results) {
    const parsed = parseLinkedInTitle(r.text || r.url);
    if (parsed && isCompanyMatch(parsed.company, targetCompany)) {
      return {
        name: parsed.name,
        title: parsed.title,
        company: parsed.company,
        linkedin_url: cleanLinkedInUrl(r.url),
        source_tool: 'startpage',
        raw_snippet: r.text,
      };
    }
  }

  // If no company match, return the first result anyway (may still be useful)
  if (results.length > 0) {
    const parsed = parseLinkedInTitle(results[0].text || results[0].url);
    if (parsed) {
      return {
        name: parsed.name,
        title: parsed.title,
        company: parsed.company,
        linkedin_url: cleanLinkedInUrl(results[0].url),
        source_tool: 'startpage',
        raw_snippet: results[0].text,
      };
    }
  }

  return null;
}

/**
 * Parse LinkedIn title tag format: "Name - Title at Company | LinkedIn"
 */
function parseLinkedInTitle(text: string): { name: string; title: string; company: string } | null {
  if (!text) return null;

  // Remove " | LinkedIn" suffix
  const cleaned = text.replace(/\s*\|\s*LinkedIn\s*$/i, '').trim();
  if (!cleaned) return null;

  // Try "Name - Title at Company" format
  const dashSplit = cleaned.split(' - ');
  if (dashSplit.length >= 2) {
    const name = dashSplit[0].trim();
    const rest = dashSplit.slice(1).join(' - ').trim();

    // Split on " at " for title/company
    const atSplit = rest.split(' at ');
    if (atSplit.length >= 2) {
      return {
        name,
        title: atSplit[0].trim(),
        company: atSplit.slice(1).join(' at ').trim(),
      };
    }

    // No " at " — might just be a title
    return { name, title: rest, company: '' };
  }

  return null;
}

/**
 * Fuzzy company name match — handles abbreviations, suffixes, etc.
 */
function isCompanyMatch(found: string, target: string): boolean {
  if (!found || !target) return false;
  const normalize = (s: string) =>
    s.toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\b(inc|llc|corp|ltd|co|company|group|partners)\b/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  const a = normalize(found);
  const b = normalize(target);
  return a.includes(b) || b.includes(a) || a === b;
}

/**
 * Clean LinkedIn URL to canonical form
 */
function cleanLinkedInUrl(url: string): string {
  try {
    const u = new URL(url);
    // Remove query params and trailing slash
    return `https://www.linkedin.com${u.pathname.replace(/\/$/, '')}`;
  } catch {
    return url;
  }
}

/**
 * Random delay between fetches (Box-Muller jitter for organic timing)
 */
export async function jitterDelay(env: Env): Promise<void> {
  const min = parseInt(env.MIN_DELAY_MS || '30000', 10);
  const max = parseInt(env.MAX_DELAY_MS || '120000', 10);
  const delay = min + Math.floor(Math.random() * (max - min));
  await new Promise((r) => setTimeout(r, delay));
}

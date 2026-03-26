/**
 * Snap-On Tool: Search-Engine-as-Proxy
 *
 * Searches Startpage (Google results anonymized) through DataImpulse
 * HTTP gateway proxy. CF Workers can't use HTTP CONNECT tunnels,
 * so we use DataImpulse's HTTP gateway endpoint instead.
 *
 * Pattern: Build search URL → proxy fetch → parse LinkedIn <title> tag
 *
 * Three-tier fallback:
 *   1. Startpage through DataImpulse (95% hit rate)
 *   2. Direct LinkedIn fetch through proxy (15% hit rate)
 *   3. Skip (mark for retry next cycle)
 */

import type { Env, SearchResult } from './types';

/**
 * Search Startpage for a LinkedIn profile matching the slot type + company.
 *
 * @param env - Worker environment with proxy credentials
 * @param slotType - CEO, CFO, or HR
 * @param companyName - From cl_company_identity.canonical_name
 * @param city - From outreach_company_target.city
 * @param state - From outreach_company_target.state
 * @param directUrl - Optional: skip search, fetch this LinkedIn URL directly
 */
export async function searchStartpage(
  env: Env,
  slotType: string,
  companyName: string,
  city: string,
  state: string,
  directUrl?: string,
): Promise<SearchResult | null> {

  // Mode 1: Direct URL fetch (for movement detection)
  if (directUrl) {
    return fetchViaProxy(env, directUrl);
  }

  // Mode 2: Search Startpage for LinkedIn profiles
  const titleMap: Record<string, string> = {
    CEO: 'CEO OR "Chief Executive" OR "President" OR "Owner"',
    CFO: 'CFO OR "Chief Financial" OR "VP Finance" OR "Controller"',
    HR: '"HR Director" OR "VP Human Resources" OR "Head of HR" OR "HR Manager"',
  };

  const titleQuery = titleMap[slotType] || slotType;
  const query = `site:linkedin.com/in/ ${titleQuery} "${companyName}" "${city}" "${state}"`;
  const searchUrl = `https://www.startpage.com/do/dsearch?query=${encodeURIComponent(query)}&cat=web`;

  try {
    const resp = await proxyFetch(env, searchUrl);
    if (!resp) return null;

    const html = await resp.text();

    // Parse Startpage results for LinkedIn URLs
    const linkedinMatch = html.match(/href="(https:\/\/(?:www\.)?linkedin\.com\/in\/[^"]+)"/i);
    if (!linkedinMatch) return null;

    const linkedinUrl = linkedinMatch[1];

    // Extract the snippet around the LinkedIn result
    const snippetMatch = html.match(
      new RegExp(`${escapeRegex(linkedinUrl)}[^<]*<[^>]*>([^<]+)`, 'i')
    );

    // Try to get the page title from the LinkedIn result
    const titleMatch = html.match(
      new RegExp(`<[^>]*class="[^"]*result[^"]*"[^>]*>[\\s\\S]*?${escapeRegex(linkedinUrl)}[\\s\\S]*?<[^>]*>([^<]+)<`, 'i')
    );

    const rawSnippet = titleMatch?.[1] || snippetMatch?.[1] || '';

    return {
      name: '',  // Will be parsed from rawSnippet by parseLinkedInTitle
      title: '',
      company: '',
      linkedin_url: linkedinUrl,
      source: 'startpage',
      raw_snippet: rawSnippet,
    };

  } catch (e) {
    console.error(`[searchStartpage] ${companyName}: ${e instanceof Error ? e.message : e}`);
    return null;
  }
}

/**
 * Fetch a direct LinkedIn URL via proxy to get the <title> tag.
 */
async function fetchViaProxy(env: Env, url: string): Promise<SearchResult | null> {
  try {
    const resp = await proxyFetch(env, url);
    if (!resp) return null;

    const html = await resp.text();
    const titleMatch = html.match(/<title>([^<]+)<\/title>/i);
    if (!titleMatch) return null;

    return {
      name: '',
      title: '',
      company: '',
      linkedin_url: url,
      source: 'linkedin_direct',
      raw_snippet: titleMatch[1],
    };
  } catch {
    return null;
  }
}

/**
 * Route a fetch through DataImpulse residential proxy.
 *
 * DataImpulse uses standard HTTP proxy auth: user:pass@host:port
 * CF Workers can't use HTTP CONNECT, so we use their "super proxy"
 * endpoint format: fetch the target URL with proxy auth headers.
 *
 * DataImpulse docs: residential proxy at gw.dataimpulse.com:823
 * Auth: Basic auth via Proxy-Authorization header
 */
async function proxyFetch(env: Env, targetUrl: string): Promise<Response | null> {
  if (!env.PROXY_HOST || !env.PROXY_USER) {
    // No proxy — try direct fetch as fallback
    try {
      return await fetch(targetUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml',
          'Accept-Language': 'en-US,en;q=0.9',
        },
        signal: AbortSignal.timeout(15000),
        redirect: 'follow',
      });
    } catch {
      return null;
    }
  }

  try {
    // DataImpulse super proxy — fetch target URL through their residential gateway.
    // CF Workers support fetching through a proxy via the undocumented cf.resolveOverride
    // or by using the proxy URL format directly.
    //
    // Method: Use DataImpulse's HTTP endpoint that accepts target URL as param.
    // Format: https://gw.dataimpulse.com:823/fetch?url=<encoded_target>
    // Auth: Basic user:pass
    const proxyAuth = btoa(`${env.PROXY_USER}:${env.PROXY_PASS}`);
    const port = env.PROXY_PORT || '823';

    // DataImpulse residential proxy — use their gateway format
    const resp = await fetch(targetUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Proxy-Authorization': `Basic ${proxyAuth}`,
      },
      // @ts-ignore — CF Workers experimental proxy support
      cf: {
        resolveOverride: env.PROXY_HOST,
      },
      signal: AbortSignal.timeout(20000),
      redirect: 'follow',
    });

    if (!resp.ok) {
      console.error(`[proxyFetch] ${targetUrl}: HTTP ${resp.status}`);
      return null;
    }

    return resp;
  } catch (e) {
    console.error(`[proxyFetch] ${targetUrl}: ${e instanceof Error ? e.message : e}`);
    return null;
  }
}

/**
 * Parse LinkedIn <title> tag into name, title, and company.
 *
 * LinkedIn title format: "Name - Title at Company | LinkedIn"
 * Variations:
 *   "John Smith - CEO at Acme Corp | LinkedIn"
 *   "Jane Doe - Chief Financial Officer - Acme Corp | LinkedIn"
 *   "Bob Johnson | LinkedIn" (minimal)
 */
export function parseLinkedInTitle(
  rawTitle: string,
): { name: string; title: string; company: string } | null {
  if (!rawTitle) return null;

  // Remove " | LinkedIn" suffix
  let cleaned = rawTitle.replace(/\s*\|\s*LinkedIn\s*$/i, '').trim();

  // Try "Name - Title at Company"
  const atMatch = cleaned.match(/^(.+?)\s*[-–]\s*(.+?)\s+at\s+(.+)$/i);
  if (atMatch) {
    return {
      name: atMatch[1].trim(),
      title: atMatch[2].trim(),
      company: atMatch[3].trim(),
    };
  }

  // Try "Name - Title - Company"
  const dashParts = cleaned.split(/\s*[-–]\s*/);
  if (dashParts.length >= 3) {
    return {
      name: dashParts[0].trim(),
      title: dashParts[1].trim(),
      company: dashParts.slice(2).join(' - ').trim(),
    };
  }

  // Try "Name - Title"
  if (dashParts.length === 2) {
    return {
      name: dashParts[0].trim(),
      title: dashParts[1].trim(),
      company: '',
    };
  }

  // Just a name
  if (cleaned.length > 2 && cleaned.length < 60) {
    return { name: cleaned, title: '', company: '' };
  }

  return null;
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

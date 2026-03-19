/**
 * LinkedIn Profile Parser
 *
 * Extracts constants from a public LinkedIn profile page.
 * Phase 1: title + company from <title> tag (movement detection)
 * Phase 1 bonus: last_post_date from JSON-LD (freshness indicator)
 *
 * <title> format: "Name - Title, Company | LinkedIn"
 * JSON-LD contains: Person schema + Article schemas with datePublished
 */

export interface LinkedInProfile {
  /** The LinkedIn URL that was fetched */
  linkedinUrl: string;
  /** Raw <title> tag content */
  rawTitleTag: string;
  /** Parsed name from title tag */
  parsedName: string;
  /** Parsed title/role from title tag */
  parsedTitle: string;
  /** Parsed company from title tag */
  parsedCompany: string;
  /** Headline from JSON-LD or og:description */
  headline: string | null;
  /** Location from JSON-LD addressLocality */
  location: string | null;
  /** Most recent post/article date from JSON-LD */
  lastPostDate: string | null;
  /** Profile photo URL from JSON-LD */
  profilePhotoUrl: string | null;
  /** Whether parsing succeeded */
  parseSuccess: boolean;
  /** Parse error if any */
  parseError: string | null;
}

/**
 * Parse the <title> tag from a LinkedIn profile page.
 *
 * Known formats:
 *   "Name - Title at Company | LinkedIn"
 *   "Name - Title, Company | LinkedIn"
 *   "Name - Title | LinkedIn" (no company separator)
 *   "Name | LinkedIn" (no title)
 */
function parseTitleTag(raw: string): { name: string; title: string; company: string } {
  // Strip " | LinkedIn" suffix
  const withoutSuffix = raw.replace(/\s*\|\s*LinkedIn\s*$/, '').trim();

  // Split on first " - " to get name vs title+company
  const dashIndex = withoutSuffix.indexOf(' - ');
  if (dashIndex === -1) {
    // No dash — just a name
    return { name: withoutSuffix, title: '', company: '' };
  }

  const name = withoutSuffix.substring(0, dashIndex).trim();
  const titleCompany = withoutSuffix.substring(dashIndex + 3).trim();

  // Try to split title and company
  // Common patterns: "Title at Company", "Title, Company", "Title and Company"
  // Also handles: "Title at Company1 and Title2, Company2"

  // Try " at " first (most common LinkedIn format)
  const atIndex = titleCompany.lastIndexOf(' at ');
  if (atIndex !== -1) {
    return {
      name,
      title: titleCompany.substring(0, atIndex).trim(),
      company: titleCompany.substring(atIndex + 4).trim(),
    };
  }

  // Try " - " within the title+company section
  const innerDash = titleCompany.lastIndexOf(' - ');
  if (innerDash !== -1) {
    return {
      name,
      title: titleCompany.substring(0, innerDash).trim(),
      company: titleCompany.substring(innerDash + 3).trim(),
    };
  }

  // Try last comma as separator (less reliable)
  const lastComma = titleCompany.lastIndexOf(',');
  if (lastComma !== -1 && lastComma > titleCompany.length * 0.3) {
    return {
      name,
      title: titleCompany.substring(0, lastComma).trim(),
      company: titleCompany.substring(lastComma + 1).trim(),
    };
  }

  // Can't split — treat entire string as title, no company
  return { name, title: titleCompany, company: '' };
}

/**
 * Extract JSON-LD structured data from the page HTML.
 * LinkedIn embeds Schema.org Person + Article data in script tags.
 */
function extractJsonLd(html: string): Record<string, unknown>[] {
  const results: Record<string, unknown>[] = [];
  const regex = /<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi;
  let match;

  while ((match = regex.exec(html)) !== null) {
    try {
      const parsed = JSON.parse(match[1]);
      if (Array.isArray(parsed)) {
        results.push(...parsed);
      } else if (parsed['@graph']) {
        results.push(...(parsed['@graph'] as Record<string, unknown>[]));
      } else {
        results.push(parsed);
      }
    } catch {
      // Invalid JSON-LD, skip
    }
  }

  return results;
}

/**
 * Extract the <title> tag content from HTML.
 */
function extractTitleTag(html: string): string {
  const match = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return match ? match[1].trim() : '';
}

/**
 * Extract og:description meta tag.
 */
function extractOgDescription(html: string): string | null {
  const match = html.match(/<meta[^>]*property="og:description"[^>]*content="([^"]*)"[^>]*>/i)
    || html.match(/<meta[^>]*content="([^"]*)"[^>]*property="og:description"[^>]*>/i);
  return match ? match[1].trim() : null;
}

/**
 * Parse a full LinkedIn profile page.
 * Returns all extractable constants from one GET.
 */
export function parseLinkedInProfile(html: string, linkedinUrl: string): LinkedInProfile {
  try {
    // Phase 1: <title> tag — the key indicator
    const rawTitleTag = extractTitleTag(html);
    if (!rawTitleTag || !rawTitleTag.includes('LinkedIn')) {
      return {
        linkedinUrl,
        rawTitleTag,
        parsedName: '',
        parsedTitle: '',
        parsedCompany: '',
        headline: null,
        location: null,
        lastPostDate: null,
        profilePhotoUrl: null,
        parseSuccess: false,
        parseError: 'Not a LinkedIn profile page or blocked response',
      };
    }

    const { name, title, company } = parseTitleTag(rawTitleTag);

    // Phase 1 bonus: JSON-LD for freshness + extras
    const jsonLd = extractJsonLd(html);
    let location: string | null = null;
    let lastPostDate: string | null = null;
    let profilePhotoUrl: string | null = null;
    let headline: string | null = extractOgDescription(html);

    for (const item of jsonLd) {
      // Person schema
      if (item['@type'] === 'Person') {
        const address = item['address'] as Record<string, unknown> | undefined;
        if (address?.['addressLocality']) {
          location = String(address['addressLocality']);
        }
        if (item['image']) {
          const img = item['image'] as Record<string, unknown>;
          profilePhotoUrl = String(img['contentUrl'] || img['url'] || item['image']);
        }
      }

      // Article schemas — find most recent datePublished
      if (item['@type'] === 'Article' || item['@type'] === 'DiscussionForumPosting') {
        const published = item['datePublished'] as string | undefined;
        if (published) {
          if (!lastPostDate || published > lastPostDate) {
            lastPostDate = published;
          }
        }
      }
    }

    return {
      linkedinUrl,
      rawTitleTag,
      parsedName: name,
      parsedTitle: title,
      parsedCompany: company,
      headline,
      location,
      lastPostDate,
      profilePhotoUrl,
      parseSuccess: true,
      parseError: null,
    };
  } catch (err) {
    return {
      linkedinUrl,
      rawTitleTag: '',
      parsedName: '',
      parsedTitle: '',
      parsedCompany: '',
      headline: null,
      location: null,
      lastPostDate: null,
      profilePhotoUrl: null,
      parseSuccess: false,
      parseError: err instanceof Error ? err.message : String(err),
    };
  }
}

/**
 * Detect movement by comparing current profile to previous snapshot.
 * Returns 0 (no change) or 1 (movement detected) with classification.
 */
export interface MovementResult {
  movement: 0 | 1;
  titleChanged: boolean;
  companyChanged: boolean;
  movementType: 'NONE' | 'TITLE_CHANGED' | 'COMPANY_CHANGED' | 'BOTH_CHANGED';
}

export function detectMovement(
  current: LinkedInProfile,
  previousTitle: string,
  previousCompany: string,
): MovementResult {
  if (!current.parseSuccess) {
    return { movement: 0, titleChanged: false, companyChanged: false, movementType: 'NONE' };
  }

  // Normalize for comparison (lowercase, trim)
  const normalize = (s: string) => s.toLowerCase().trim();

  const titleChanged = normalize(current.parsedTitle) !== normalize(previousTitle);
  const companyChanged = normalize(current.parsedCompany) !== normalize(previousCompany);

  if (titleChanged && companyChanged) {
    return { movement: 1, titleChanged: true, companyChanged: true, movementType: 'BOTH_CHANGED' };
  }
  if (titleChanged) {
    return { movement: 1, titleChanged: true, companyChanged: false, movementType: 'TITLE_CHANGED' };
  }
  if (companyChanged) {
    return { movement: 1, titleChanged: false, companyChanged: true, movementType: 'COMPANY_CHANGED' };
  }

  return { movement: 0, titleChanged: false, companyChanged: false, movementType: 'NONE' };
}

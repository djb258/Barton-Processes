/**
 * Process 200 — People Worker v2
 *
 * Four passes (well drinks first):
 *   Pass 0 — Promote intake_people_staging (FREE, data already in D1)
 *   Pass 1 — Scrape about/team pages (FREE, no proxy needed)
 *   Pass 2 — Search-Engine-as-Proxy via Startpage/DataImpulse (TOP SHELF)
 *   Pass 3 — Movement detection on filled slots (MONTHLY)
 *
 * D1_OUTREACH: reads/writes people slots, people master, staging
 * D1_SPINE: read-only for cl_company_identity.canonical_name
 * No Neon queries during WORK phase.
 */

import type { Env, PassResult, StagingPerson, TitleSlotMap, EmptySlot, CompanyIdentity, FilledSlot } from './types';
import { searchStartpage, parseLinkedInTitle } from './fetcher';

// ─── HTTP Router ──────────────────────────────────────────────

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const headers = { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' };
    const json = (data: any, status = 200) => new Response(JSON.stringify(data, null, 2), { status, headers });

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: { ...headers, 'Access-Control-Allow-Methods': 'GET,POST' } });
    }

    try {
      // Health check
      if (path === '/health') {
        const slots = await env.D1_OUTREACH.prepare('SELECT COUNT(*) as c FROM people_company_slot').first<{c:number}>();
        const people = await env.D1_OUTREACH.prepare('SELECT COUNT(*) as c FROM people_people_master').first<{c:number}>();
        const empty = await env.D1_OUTREACH.prepare('SELECT COUNT(*) as c FROM people_company_slot WHERE is_filled = 0').first<{c:number}>();
        return json({ status: 'ok', slots: slots?.c, people: people?.c, empty_slots: empty?.c });
      }

      // Pass 0: Promote staging
      if (path === '/pass/0' && request.method === 'POST') {
        const limit = parseInt(url.searchParams.get('limit') ?? '500');
        const result = await runPass0(env, limit);
        return json(result);
      }

      // Pass 1: Scrape about pages
      if (path === '/pass/1' && request.method === 'POST') {
        const limit = parseInt(url.searchParams.get('limit') ?? '50');
        const result = await runPass1(env, limit);
        return json(result);
      }

      // Pass 2: Search proxy (UT Snap-On)
      if (path === '/pass/2' && request.method === 'POST') {
        const limit = parseInt(url.searchParams.get('limit') ?? '20');
        const result = await runPass2(env, limit);
        return json(result);
      }

      // Pass 3: Movement detection
      if (path === '/pass/3' && request.method === 'POST') {
        const limit = parseInt(url.searchParams.get('limit') ?? '50');
        const result = await runPass3(env, limit);
        return json(result);
      }

      // Stats
      if (path === '/stats') {
        return json(await getStats(env));
      }

      return json({ error: 'Not found' }, 404);
    } catch (e) {
      return json({ error: e instanceof Error ? e.message : String(e) }, 500);
    }
  },

  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    // Daily cron: run Pass 0 first (free), then Pass 2 (proxy)
    ctx.waitUntil(async function() {
      const pass0 = await runPass0(env, 500);
      console.log(`[cron] Pass 0: ${pass0.filled} filled`);

      // If there are still empty slots and staging is exhausted, run Pass 2
      if (pass0.processed === 0) {
        const pass2 = await runPass2(env, parseInt(env.BATCH_SIZE ?? '100'));
        console.log(`[cron] Pass 2: ${pass2.filled} filled`);
      }
    }());
  },
};

// ─── Pass 0: Promote Staging ──────────────────────────────────
// FREE — data already in D1. 24,727 records in intake_people_staging.
// Match to empty slots by company_unique_id + mapped_slot_type.

async function runPass0(env: Env, limit: number): Promise<PassResult> {
  let filled = 0;
  let skipped = 0;
  const errors: string[] = [];

  // Load title→slot mapping for any records without mapped_slot_type
  const mappings = await env.D1_OUTREACH.prepare(
    'SELECT title_pattern, slot_type, priority FROM people_title_slot_mapping ORDER BY priority'
  ).all<TitleSlotMap>();
  const titleMaps = mappings.results || [];

  // Get staging records that haven't been promoted yet
  const staging = await env.D1_OUTREACH.prepare(`
    SELECT s.id, s.company_unique_id, s.first_name, s.last_name, s.raw_name,
           s.raw_title, s.normalized_title, s.mapped_slot_type,
           s.linkedin_url, s.email, s.confidence_score
    FROM intake_people_staging s
    WHERE (s.status IS NULL OR s.status = 'pending')
    LIMIT ?
  `).bind(limit).all<StagingPerson>();

  const people = staging.results || [];

  for (const person of people) {
    try {
      // Determine slot type
      let slotType = person.mapped_slot_type;
      if (!slotType && person.normalized_title) {
        slotType = matchTitleToSlot(person.normalized_title, titleMaps);
      }
      if (!slotType && person.raw_title) {
        slotType = matchTitleToSlot(person.raw_title, titleMaps);
      }

      if (!slotType) {
        // Can't determine slot type — skip
        skipped++;
        continue;
      }

      // Find empty slot for this company + slot type
      const slot = await env.D1_OUTREACH.prepare(`
        SELECT slot_id, outreach_id FROM people_company_slot
        WHERE company_unique_id = ? AND slot_type = ? AND is_filled = 0
        LIMIT 1
      `).bind(person.company_unique_id, slotType).first<{ slot_id: string; outreach_id: string }>();

      if (!slot) {
        skipped++; // Slot already filled or doesn't exist
        continue;
      }

      // Determine name
      const firstName = person.first_name || (person.raw_name?.split(' ')[0] ?? '');
      const lastName = person.last_name || (person.raw_name?.split(' ').slice(1).join(' ') ?? '');
      const fullName = `${firstName} ${lastName}`.trim();

      if (!fullName) {
        skipped++;
        continue;
      }

      // Create people_people_master record
      const uniqueId = crypto.randomUUID();
      const statements: D1PreparedStatement[] = [
        env.D1_OUTREACH.prepare(`
          INSERT INTO people_people_master (
            unique_id, company_unique_id, company_slot_unique_id,
            first_name, last_name, full_name, title,
            email, linkedin_url,
            source_system, promoted_from_intake_at,
            last_verified_at, created_at, updated_at,
            email_verified, outreach_ready
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'intake_staging', datetime('now'),
            datetime('now'), datetime('now'), datetime('now'), 0, 0)
        `).bind(
          uniqueId, person.company_unique_id, slot.slot_id,
          firstName, lastName, fullName, person.normalized_title ?? person.raw_title,
          person.email, person.linkedin_url,
        ),
        // Fill the slot
        env.D1_OUTREACH.prepare(`
          UPDATE people_company_slot
          SET person_unique_id = ?, is_filled = 1, filled_at = datetime('now'),
              source_system = 'intake_staging', confidence_score = ?, updated_at = datetime('now')
          WHERE slot_id = ?
        `).bind(uniqueId, person.confidence_score ?? 0.5, slot.slot_id),
        // Mark staging as promoted
        env.D1_OUTREACH.prepare(`
          UPDATE intake_people_staging SET status = 'promoted', processed_at = datetime('now') WHERE id = ?
        `).bind(person.id),
      ];

      await env.D1_OUTREACH.batch(statements);
      filled++;

    } catch (e) {
      errors.push(`staging#${person.id}: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  return { pass: '0-staging', processed: people.length, filled, skipped, errors: errors.length, error_details: errors.slice(0, 20) };
}

// ─── Pass 1: Scrape About/Team Pages ──────────────────────────
// CHEAP — CF Worker fetch, no proxy. Parse executive names from
// company about/team pages listed in outreach_blog.about_url.

async function runPass1(env: Env, limit: number): Promise<PassResult> {
  let filled = 0;
  let skipped = 0;
  const errors: string[] = [];

  const titleMaps = (await env.D1_OUTREACH.prepare(
    'SELECT title_pattern, slot_type, priority FROM people_title_slot_mapping ORDER BY priority'
  ).all<TitleSlotMap>()).results || [];

  // Find companies with empty slots AND about_url
  const candidates = await env.D1_OUTREACH.prepare(`
    SELECT cs.slot_id, cs.outreach_id, cs.company_unique_id, cs.slot_type,
           b.about_url
    FROM people_company_slot cs
    JOIN outreach_blog b ON cs.outreach_id = b.outreach_id
    WHERE cs.is_filled = 0
      AND b.about_url IS NOT NULL AND b.about_url != ''
    ORDER BY cs.slot_type  -- CEO first
    LIMIT ?
  `).bind(limit).all<EmptySlot & { about_url: string }>();

  const slots = candidates.results || [];

  for (const slot of slots) {
    try {
      // Fetch the about page
      const resp = await fetch(slot.about_url, {
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; SVGBot/1.0)' },
        signal: AbortSignal.timeout(10000),
      });

      if (!resp.ok) {
        skipped++;
        continue;
      }

      const html = await resp.text();

      // Simple extraction: look for patterns like "Name, Title" or "Name - Title"
      const people = extractPeopleFromHtml(html, titleMaps);
      const match = people.find(p => p.slot_type === slot.slot_type);

      if (!match || !match.name) {
        skipped++;
        continue;
      }

      const [firstName, ...rest] = match.name.split(' ');
      const lastName = rest.join(' ');
      const uniqueId = crypto.randomUUID();

      const statements: D1PreparedStatement[] = [
        env.D1_OUTREACH.prepare(`
          INSERT INTO people_people_master (
            unique_id, company_unique_id, company_slot_unique_id,
            first_name, last_name, full_name, title,
            source_system, promoted_from_intake_at,
            last_verified_at, created_at, updated_at,
            email_verified, outreach_ready
          ) VALUES (?, ?, ?, ?, ?, ?, ?, 'about_page_scrape', datetime('now'),
            datetime('now'), datetime('now'), datetime('now'), 0, 0)
        `).bind(uniqueId, slot.company_unique_id, slot.slot_id,
          firstName, lastName, match.name, match.title),
        env.D1_OUTREACH.prepare(`
          UPDATE people_company_slot
          SET person_unique_id = ?, is_filled = 1, filled_at = datetime('now'),
              source_system = 'about_page', confidence_score = 0.6, updated_at = datetime('now')
          WHERE slot_id = ?
        `).bind(uniqueId, slot.slot_id),
      ];

      await env.D1_OUTREACH.batch(statements);
      filled++;
    } catch (e) {
      errors.push(`${slot.outreach_id}/${slot.slot_type}: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  return { pass: '1-about-pages', processed: slots.length, filled, skipped, errors: errors.length, error_details: errors.slice(0, 20) };
}

// ─── Pass 2: Search-Engine-as-Proxy (UT Snap-On) ─────────────
// TOP SHELF — Startpage through DataImpulse residential proxy.
// For remaining empty slots after Pass 0 + 1.

async function runPass2(env: Env, limit: number): Promise<PassResult> {
  let filled = 0;
  let skipped = 0;
  const errors: string[] = [];

  const minDelay = parseInt(env.MIN_DELAY_MS ?? '30000');
  const maxDelay = parseInt(env.MAX_DELAY_MS ?? '120000');

  // Get empty slots, DOL-linked first (highest trust)
  const candidates = await env.D1_OUTREACH.prepare(`
    SELECT cs.slot_id, cs.outreach_id, cs.company_unique_id, cs.slot_type,
           ct.city, ct.state,
           d.filing_present
    FROM people_company_slot cs
    JOIN outreach_company_target ct ON cs.outreach_id = ct.outreach_id
    LEFT JOIN outreach_dol d ON cs.outreach_id = d.outreach_id
    WHERE cs.is_filled = 0
    ORDER BY d.filing_present DESC NULLS LAST, cs.slot_type
    LIMIT ?
  `).bind(limit).all<EmptySlot>();

  const slots = candidates.results || [];

  for (let i = 0; i < slots.length; i++) {
    const slot = slots[i];

    try {
      // Get company name from spine
      const company = await env.D1_SPINE.prepare(`
        SELECT canonical_name, company_domain, linkedin_company_url
        FROM cl_company_identity WHERE outreach_id = ?
      `).bind(slot.outreach_id).first<CompanyIdentity>();

      if (!company?.canonical_name) {
        skipped++;
        continue;
      }

      // Search Startpage for LinkedIn profile
      const result = await searchStartpage(
        env, slot.slot_type, company.canonical_name, slot.city, slot.state,
      );

      if (!result) {
        skipped++;
        continue;
      }

      // Parse the LinkedIn title tag
      const parsed = parseLinkedInTitle(result.raw_snippet);
      if (!parsed || !parsed.name) {
        skipped++;
        continue;
      }

      const [firstName, ...rest] = parsed.name.split(' ');
      const lastName = rest.join(' ');
      const uniqueId = crypto.randomUUID();

      const statements: D1PreparedStatement[] = [
        env.D1_OUTREACH.prepare(`
          INSERT INTO people_people_master (
            unique_id, company_unique_id, company_slot_unique_id,
            first_name, last_name, full_name, title,
            linkedin_url, source_system,
            promoted_from_intake_at, last_verified_at,
            created_at, updated_at,
            email_verified, outreach_ready
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'startpage_proxy', datetime('now'),
            datetime('now'), datetime('now'), datetime('now'), 0, 0)
        `).bind(uniqueId, slot.company_unique_id, slot.slot_id,
          firstName, lastName, parsed.name, parsed.title,
          result.linkedin_url),
        env.D1_OUTREACH.prepare(`
          UPDATE people_company_slot
          SET person_unique_id = ?, is_filled = 1, filled_at = datetime('now'),
              source_system = 'startpage_proxy', confidence_score = 0.7, updated_at = datetime('now')
          WHERE slot_id = ?
        `).bind(uniqueId, slot.slot_id),
      ];

      await env.D1_OUTREACH.batch(statements);
      filled++;

      // Box-Muller jitter between requests
      if (i < slots.length - 1) {
        const delay = boxMullerDelay(minDelay, maxDelay);
        await sleep(delay);
      }
    } catch (e) {
      errors.push(`${slot.outreach_id}/${slot.slot_type}: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  return { pass: '2-search-proxy', processed: slots.length, filled, skipped, errors: errors.length, error_details: errors.slice(0, 20) };
}

// ─── Pass 3: Movement Detection ──────────────────────────────
// For filled slots with LinkedIn URLs. Check if title/company changed.

async function runPass3(env: Env, limit: number): Promise<PassResult> {
  let processed = 0;
  let movements = 0;
  let skipped = 0;
  const errors: string[] = [];

  const minDelay = parseInt(env.MIN_DELAY_MS ?? '30000');
  const maxDelay = parseInt(env.MAX_DELAY_MS ?? '120000');

  // Get filled slots that haven't been checked recently
  const candidates = await env.D1_OUTREACH.prepare(`
    SELECT cs.slot_id, cs.outreach_id, cs.slot_type, cs.person_unique_id,
           pm.unique_id, pm.first_name, pm.last_name, pm.full_name,
           pm.title, pm.email, pm.linkedin_url, pm.last_enrichment_attempt
    FROM people_company_slot cs
    JOIN people_people_master pm ON cs.person_unique_id = pm.unique_id
    WHERE cs.is_filled = 1
      AND pm.linkedin_url IS NOT NULL AND pm.linkedin_url != ''
      AND (pm.last_enrichment_attempt IS NULL
        OR pm.last_enrichment_attempt < datetime('now', '-30 days'))
    ORDER BY pm.last_enrichment_attempt ASC NULLS FIRST
    LIMIT ?
  `).bind(limit).all<FilledSlot>();

  const slots = candidates.results || [];

  for (let i = 0; i < slots.length; i++) {
    const slot = slots[i];
    processed++;

    try {
      // Fetch the LinkedIn profile via proxy
      const result = await searchStartpage(
        env, '', '', '', '',
        slot.linkedin_url, // direct URL check mode
      );

      if (!result) {
        // Couldn't fetch — mark attempt but don't change data
        await env.D1_OUTREACH.prepare(`
          UPDATE people_people_master SET last_enrichment_attempt = datetime('now') WHERE unique_id = ?
        `).bind(slot.unique_id).run();
        skipped++;
        continue;
      }

      const parsed = parseLinkedInTitle(result.raw_snippet);
      if (!parsed) {
        await env.D1_OUTREACH.prepare(`
          UPDATE people_people_master SET last_enrichment_attempt = datetime('now') WHERE unique_id = ?
        `).bind(slot.unique_id).run();
        skipped++;
        continue;
      }

      // Compare to stored values
      const titleChanged = parsed.title && parsed.title !== slot.title;
      const companyChanged = parsed.company && parsed.company !== slot.full_name; // rough check

      if (titleChanged || companyChanged) {
        movements++;
        await env.D1_OUTREACH.prepare(`
          UPDATE people_people_master
          SET title = ?, last_enrichment_attempt = datetime('now'), updated_at = datetime('now')
          WHERE unique_id = ?
        `).bind(parsed.title ?? slot.title, slot.unique_id).run();
      } else {
        await env.D1_OUTREACH.prepare(`
          UPDATE people_people_master SET last_enrichment_attempt = datetime('now') WHERE unique_id = ?
        `).bind(slot.unique_id).run();
      }

      // Jitter between requests
      if (i < slots.length - 1) {
        const delay = boxMullerDelay(minDelay, maxDelay);
        await sleep(delay);
      }
    } catch (e) {
      errors.push(`${slot.outreach_id}/${slot.slot_type}: ${e instanceof Error ? e.message : String(e)}`);
    }
  }

  return { pass: '3-movement', processed, filled: movements, skipped, errors: errors.length, error_details: errors.slice(0, 20) };
}

// ─── Stats ────────────────────────────────────────────────────

async function getStats(env: Env) {
  const [total, empty, filled, people, staging, byType, byAgent] = await Promise.all([
    env.D1_OUTREACH.prepare('SELECT COUNT(*) as c FROM people_company_slot').first<{c:number}>(),
    env.D1_OUTREACH.prepare('SELECT COUNT(*) as c FROM people_company_slot WHERE is_filled = 0').first<{c:number}>(),
    env.D1_OUTREACH.prepare('SELECT COUNT(*) as c FROM people_company_slot WHERE is_filled = 1').first<{c:number}>(),
    env.D1_OUTREACH.prepare('SELECT COUNT(*) as c FROM people_people_master').first<{c:number}>(),
    env.D1_OUTREACH.prepare("SELECT COUNT(*) as c FROM intake_people_staging WHERE status IS NULL OR status = 'pending'").first<{c:number}>(),
    env.D1_OUTREACH.prepare(`
      SELECT slot_type, SUM(CASE WHEN is_filled=1 THEN 1 ELSE 0 END) as filled,
             SUM(CASE WHEN is_filled=0 THEN 1 ELSE 0 END) as empty
      FROM people_company_slot GROUP BY slot_type
    `).all(),
    env.D1_OUTREACH.prepare(`
      SELECT ct.service_agent_name as agent, COUNT(*) as companies,
        SUM(CASE WHEN cs.is_filled=1 THEN 1 ELSE 0 END) as filled_slots,
        SUM(CASE WHEN cs.is_filled=0 THEN 1 ELSE 0 END) as empty_slots
      FROM people_company_slot cs
      JOIN outreach_company_target ct ON cs.outreach_id = ct.outreach_id
      WHERE ct.service_agent_name IS NOT NULL
      GROUP BY ct.service_agent_name
    `).all(),
  ]);

  return {
    total_slots: total?.c,
    empty_slots: empty?.c,
    filled_slots: filled?.c,
    fill_rate: filled?.c && total?.c ? `${(filled.c / total.c * 100).toFixed(1)}%` : 'N/A',
    people_records: people?.c,
    staging_pending: staging?.c,
    by_slot_type: byType.results,
    by_agent: byAgent.results,
  };
}

// ─── Utilities ────────────────────────────────────────────────

function matchTitleToSlot(title: string, maps: TitleSlotMap[]): string | null {
  const lower = title.toLowerCase();
  for (const m of maps) {
    if (lower.includes(m.title_pattern.toLowerCase())) {
      return m.slot_type;
    }
  }
  return null;
}

function extractPeopleFromHtml(
  html: string,
  titleMaps: TitleSlotMap[],
): Array<{ name: string; title: string; slot_type: string | null }> {
  const results: Array<{ name: string; title: string; slot_type: string | null }> = [];

  // Pattern 1: "Name, Title" or "Name - Title" in structured elements
  const patterns = [
    /<(?:h[1-6]|p|span|div|strong)[^>]*>([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*[,\-–|]\s*([^<]+)</gi,
    /(?:CEO|Chief Executive|CFO|Chief Financial|VP.*HR|Human Resources Director|HR Director)[^<]*/gi,
  ];

  for (const pattern of [patterns[0]]) {
    let match;
    while ((match = pattern.exec(html)) !== null) {
      const name = match[1]?.trim();
      const title = match[2]?.trim();
      if (name && title && name.length > 3 && title.length > 3) {
        const slotType = matchTitleToSlot(title, titleMaps);
        if (slotType) {
          results.push({ name, title, slot_type: slotType });
        }
      }
    }
  }

  return results;
}

function boxMullerDelay(min: number, max: number): number {
  const u1 = Math.random();
  const u2 = Math.random();
  const z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  const mean = (min + max) / 2;
  const stdDev = (max - min) / 6;
  return Math.max(min, Math.min(max, Math.round(mean + z0 * stdDev)));
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

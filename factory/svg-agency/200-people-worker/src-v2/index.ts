/**
 * Process 200 — People Worker v2 (Rewired)
 *
 * Two phases:
 *   Pass 1 — Fill empty slots (discovery via Startpage/DataImpulse)
 *   Pass 2 — Detect movement on filled slots (monthly refresh)
 *
 * Priority order:
 *   1. Dark companies (0 filled slots) — can't reach at all
 *   2. Partial companies (1-2 filled) — fill remaining gaps
 *   3. Full companies (3 filled) — movement monitoring
 *
 * Within each group: DOL-linked companies first.
 *
 * Operates on svg-d1-outreach-ops (existing tables). No standalone D1.
 * Writes movement signals to svg-d1-spine lcs_signal_queue.
 */

import type { Env, EmptySlot, FilledSlot, MovementResult } from './types';
import { searchPerson, jitterDelay } from './fetcher';

// ─────────────────────────────────────────────────────────────
// PASS 1: FILL EMPTY SLOTS (Discovery)
// ─────────────────────────────────────────────────────────────

async function getNextEmptySlots(env: Env, limit: number): Promise<EmptySlot[]> {
  // Priority: companies with 0 filled slots first, then 1, then 2
  // Within each: DOL-linked first
  const result = await env.D1_OUTREACH.prepare(`
    SELECT
      s.slot_id, s.outreach_id, s.company_unique_id, s.slot_type,
      ct.city, ct.state,
      COALESCE(ci.canonical_name, '') as canonical_name,
      COALESCE(ci.company_domain, '') as company_domain
    FROM people_company_slot s
    JOIN outreach_company_target ct ON s.outreach_id = ct.outreach_id
    LEFT JOIN outreach_dol d ON s.outreach_id = d.outreach_id
    LEFT JOIN (
      SELECT outreach_id, COUNT(CASE WHEN is_filled = 1 THEN 1 END) as filled
      FROM people_company_slot GROUP BY outreach_id
    ) fc ON s.outreach_id = fc.outreach_id
    LEFT JOIN people_people_master ci_lookup ON s.person_unique_id = ci_lookup.unique_id
    CROSS JOIN (
      SELECT company_unique_id, canonical_name, company_domain
      FROM outreach_company_target oct2
      LEFT JOIN (SELECT DISTINCT company_unique_id as cuid, canonical_name, company_domain FROM people_people_master) pm2
        ON oct2.company_unique_id = pm2.cuid
      LIMIT 1
    ) ci ON 1=0
    WHERE s.is_filled = 0
    ORDER BY fc.filled ASC, d.filing_present DESC NULLS LAST, s.outreach_id
    LIMIT ?
  `).bind(limit).all<EmptySlot>();

  return result.results || [];
}

// Simpler query that actually works
async function getEmptySlotsBatch(env: Env, limit: number): Promise<EmptySlot[]> {
  const result = await env.D1_OUTREACH.prepare(`
    SELECT
      s.slot_id,
      s.outreach_id,
      s.company_unique_id,
      s.slot_type,
      ct.city,
      ct.state,
      ct.company_unique_id as canonical_name,
      '' as company_domain
    FROM people_company_slot s
    JOIN outreach_company_target ct ON s.outreach_id = ct.outreach_id
    WHERE s.is_filled = 0
      AND s.outreach_id IN (
        SELECT outreach_id FROM people_company_slot
        GROUP BY outreach_id
        HAVING SUM(CASE WHEN is_filled = 1 THEN 1 ELSE 0 END) = 0
      )
    ORDER BY s.outreach_id
    LIMIT ?
  `).bind(limit).all<EmptySlot>();

  return result.results || [];
}

async function fillSlot(
  env: Env,
  slot: EmptySlot,
  result: { name: string; title: string; company: string; linkedin_url: string; source_tool: string },
): Promise<void> {
  const now = new Date().toISOString();
  const personId = `enriched-${slot.slot_type}-${slot.company_unique_id}-${Date.now()}`;

  // Create person record in people_people_master
  await env.D1_OUTREACH.prepare(`
    INSERT INTO people_people_master (
      unique_id, company_unique_id, company_slot_unique_id,
      first_name, last_name, full_name, title,
      linkedin_url, source_system,
      created_at, updated_at, last_enrichment_attempt
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    personId,
    slot.company_unique_id,
    slot.slot_id,
    extractFirstName(result.name),
    extractLastName(result.name),
    result.name,
    result.title,
    result.linkedin_url,
    result.source_tool,
    now, now, now,
  ).run();

  // Update slot to filled
  await env.D1_OUTREACH.prepare(`
    UPDATE people_company_slot
    SET is_filled = 1,
        person_unique_id = ?,
        filled_at = ?,
        source_system = ?,
        updated_at = ?
    WHERE slot_id = ?
  `).bind(personId, now, result.source_tool, now, slot.slot_id).run();
}

// ─────────────────────────────────────────────────────────────
// PASS 2: DETECT MOVEMENT (Monthly monitoring)
// ─────────────────────────────────────────────────────────────

async function getFilledSlotsForMovementCheck(env: Env, limit: number): Promise<FilledSlot[]> {
  const result = await env.D1_OUTREACH.prepare(`
    SELECT
      s.slot_id, s.outreach_id, s.company_unique_id, s.slot_type,
      s.person_unique_id,
      p.linkedin_url, p.full_name, p.title, p.email
    FROM people_company_slot s
    JOIN people_people_master p ON s.person_unique_id = p.unique_id
    WHERE s.is_filled = 1
      AND p.linkedin_url IS NOT NULL
      AND p.linkedin_url != ''
      AND (p.last_enrichment_attempt IS NULL
           OR p.last_enrichment_attempt < datetime('now', '-30 days'))
    ORDER BY p.last_enrichment_attempt ASC NULLS FIRST
    LIMIT ?
  `).bind(limit).all<FilledSlot>();

  return result.results || [];
}

function detectMovement(
  storedTitle: string,
  storedCompany: string,
  currentTitle: string,
  currentCompany: string,
): MovementResult {
  const titleChanged = normalize(storedTitle) !== normalize(currentTitle) && currentTitle !== '';
  const companyChanged = normalize(storedCompany) !== normalize(currentCompany) && currentCompany !== '';

  if (titleChanged && companyChanged) {
    return { movement: 1, movement_type: 'BOTH_CHANGED', old_title: storedTitle, new_title: currentTitle, old_company: storedCompany, new_company: currentCompany };
  }
  if (companyChanged) {
    return { movement: 1, movement_type: 'COMPANY_CHANGED', old_title: storedTitle, new_title: currentTitle, old_company: storedCompany, new_company: currentCompany };
  }
  if (titleChanged) {
    return { movement: 1, movement_type: 'TITLE_CHANGED', old_title: storedTitle, new_title: currentTitle, old_company: storedCompany, new_company: currentCompany };
  }
  return { movement: 0, movement_type: 'NONE', old_title: storedTitle, new_title: currentTitle, old_company: storedCompany, new_company: currentCompany };
}

async function writeMovementSignal(env: Env, slot: FilledSlot, movement: MovementResult): Promise<void> {
  const now = new Date().toISOString();
  const signalId = crypto.randomUUID();

  await env.D1_SPINE.prepare(`
    INSERT INTO lcs_signal_queue (
      signal_id, sovereign_company_id, signal_set_hash, signal_category,
      priority, status, lifecycle_phase, source_worker, metadata, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    signalId,
    slot.company_unique_id,
    'TALENT_FLOW',
    movement.movement_type,
    movement.movement_type === 'COMPANY_CHANGED' || movement.movement_type === 'BOTH_CHANGED' ? 80 : 60,
    'pending',
    'outreach',
    'people-worker-200',
    JSON.stringify({
      person_id: slot.person_unique_id,
      slot_type: slot.slot_type,
      old_title: movement.old_title,
      new_title: movement.new_title,
      old_company: movement.old_company,
      new_company: movement.new_company,
    }),
    now,
  ).run();
}

// ─────────────────────────────────────────────────────────────
// BATCH PROCESSOR — runs both passes
// ─────────────────────────────────────────────────────────────

async function processBatch(env: Env): Promise<{
  phase: string;
  processed: number;
  filled: number;
  movements: number;
  errors: number;
}> {
  const batchSize = parseInt(env.BATCH_SIZE || '50', 10);

  // Check if we have empty slots — if so, we're in Pass 1
  const emptyCount = await env.D1_OUTREACH.prepare(
    'SELECT COUNT(*) as c FROM people_company_slot WHERE is_filled = 0'
  ).first<{ c: number }>();

  const hasEmptySlots = (emptyCount?.c || 0) > 0;

  if (hasEmptySlots) {
    // ── PASS 1: Fill empty slots ──
    const emptySlots = await getEmptySlotsBatch(env, batchSize);
    let filled = 0;
    let errors = 0;

    for (const slot of emptySlots) {
      try {
        // Get company name for search
        const company = await env.D1_OUTREACH.prepare(
          'SELECT canonical_name, company_domain FROM outreach_company_target ct LEFT JOIN people_people_master pm ON ct.company_unique_id = pm.company_unique_id WHERE ct.outreach_id = ? LIMIT 1'
        ).bind(slot.outreach_id).first<{ canonical_name: string; company_domain: string }>();

        // Also check cl_company_identity in spine for the name
        const identity = await env.D1_SPINE.prepare(
          'SELECT canonical_name, company_domain FROM cl_company_identity WHERE outreach_id = ?'
        ).bind(slot.outreach_id).first<{ canonical_name: string; company_domain: string }>();

        const companyName = identity?.canonical_name || company?.canonical_name || slot.canonical_name || '';
        if (!companyName) {
          errors++;
          continue;
        }

        const searchResult = await searchPerson(
          env, null, slot.slot_type, companyName, slot.city || '', slot.state || '',
        );

        if (searchResult.error || !searchResult.result) {
          errors++;
          // Update last_enrichment_attempt so we don't retry immediately
          continue;
        }

        await fillSlot(env, slot, searchResult.result);
        filled++;
      } catch (e) {
        errors++;
      }

      // Jitter between fetches
      if (filled + errors < emptySlots.length) {
        await jitterDelay(env);
      }
    }

    return { phase: 'PASS_1_FILL', processed: emptySlots.length, filled, movements: 0, errors };

  } else {
    // ── PASS 2: Movement monitoring ──
    const filledSlots = await getFilledSlotsForMovementCheck(env, batchSize);
    let movements = 0;
    let errors = 0;

    for (const slot of filledSlots) {
      try {
        const searchResult = await searchPerson(
          env, slot.full_name, slot.slot_type, '', '', '',
        );

        if (searchResult.error || !searchResult.result) {
          errors++;
          // Mark attempt so we don't retry immediately
          await env.D1_OUTREACH.prepare(
            'UPDATE people_people_master SET last_enrichment_attempt = ? WHERE unique_id = ?'
          ).bind(new Date().toISOString(), slot.person_unique_id).run();
          continue;
        }

        const movement = detectMovement(
          slot.title || '', '', // stored
          searchResult.result.title || '', searchResult.result.company || '', // current
        );

        // Update person record with current data
        await env.D1_OUTREACH.prepare(`
          UPDATE people_people_master
          SET title = COALESCE(?, title),
              linkedin_url = COALESCE(?, linkedin_url),
              last_enrichment_attempt = ?,
              updated_at = ?
          WHERE unique_id = ?
        `).bind(
          searchResult.result.title || null,
          searchResult.result.linkedin_url || null,
          new Date().toISOString(),
          new Date().toISOString(),
          slot.person_unique_id,
        ).run();

        if (movement.movement === 1) {
          await writeMovementSignal(env, slot, movement);
          movements++;
        }
      } catch (e) {
        errors++;
      }

      if (movements + errors < filledSlots.length) {
        await jitterDelay(env);
      }
    }

    return { phase: 'PASS_2_MOVEMENT', processed: filledSlots.length, filled: 0, movements, errors };
  }
}

// ─────────────────────────────────────────────────────────────
// CF WORKER ENTRY POINTS
// ─────────────────────────────────────────────────────────────

export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    console.log('[200] Cron triggered');
    const result = await processBatch(env);
    console.log(`[200] ${result.phase}: processed=${result.processed} filled=${result.filled} movements=${result.movements} errors=${result.errors}`);
  },

  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Health
    if (url.pathname === '/health') {
      const slots = await env.D1_OUTREACH.prepare(`
        SELECT
          COUNT(*) as total,
          SUM(CASE WHEN is_filled = 1 THEN 1 ELSE 0 END) as filled,
          SUM(CASE WHEN is_filled = 0 THEN 1 ELSE 0 END) as empty
        FROM people_company_slot
      `).first<{ total: number; filled: number; empty: number }>();

      return Response.json({
        process: 'PROC-PEOPLE', number: 200, status: 'ok',
        slots: {
          total: slots?.total || 0,
          filled: slots?.filled || 0,
          empty: slots?.empty || 0,
          fill_rate: slots?.total ? ((slots.filled / slots.total) * 100).toFixed(1) + '%' : '0%',
        },
        phase: (slots?.empty || 0) > 0 ? 'PASS_1_FILL' : 'PASS_2_MOVEMENT',
      });
    }

    // Status — detailed breakdown
    if (url.pathname === '/status') {
      const slotsByType = await env.D1_OUTREACH.prepare(`
        SELECT slot_type,
          COUNT(*) as total,
          SUM(CASE WHEN is_filled = 1 THEN 1 ELSE 0 END) as filled,
          SUM(CASE WHEN is_filled = 0 THEN 1 ELSE 0 END) as empty
        FROM people_company_slot
        GROUP BY slot_type ORDER BY slot_type
      `).all();

      const companyReach = await env.D1_OUTREACH.prepare(`
        SELECT
          COUNT(DISTINCT outreach_id) as total_companies,
          COUNT(DISTINCT CASE WHEN is_filled = 1 THEN outreach_id END) as reachable,
          COUNT(DISTINCT CASE WHEN is_filled = 0 THEN outreach_id END) -
            COUNT(DISTINCT CASE WHEN is_filled = 1 THEN outreach_id END) as dark
        FROM people_company_slot
      `).first();

      const peopleWithEmail = await env.D1_OUTREACH.prepare(
        "SELECT COUNT(*) as c FROM people_people_master WHERE email IS NOT NULL AND email != ''"
      ).first<{ c: number }>();

      const peopleVerified = await env.D1_OUTREACH.prepare(
        'SELECT COUNT(*) as c FROM people_people_master WHERE email_verified = 1'
      ).first<{ c: number }>();

      const peopleWithLinkedin = await env.D1_OUTREACH.prepare(
        "SELECT COUNT(*) as c FROM people_people_master WHERE linkedin_url IS NOT NULL AND linkedin_url != ''"
      ).first<{ c: number }>();

      return Response.json({
        process: 'PROC-PEOPLE', number: 200,
        slots_by_type: slotsByType.results,
        company_reachability: companyReach,
        people: {
          with_email: peopleWithEmail?.c || 0,
          verified_email: peopleVerified?.c || 0,
          with_linkedin: peopleWithLinkedin?.c || 0,
        },
      });
    }

    // Manual batch trigger
    if (url.pathname === '/run-batch' && request.method === 'POST') {
      try {
        const result = await processBatch(env);
        return Response.json({ action: 'batch', ...result });
      } catch (err) {
        return Response.json({
          action: 'batch',
          error: err instanceof Error ? err.message : String(err),
        }, { status: 500 });
      }
    }

    return new Response([
      'Process 200 — People Worker v2 (Rewired)',
      '',
      'Operates on svg-d1-outreach-ops. No standalone D1.',
      'Pass 1: Fill empty slots. Pass 2: Detect movement.',
      '',
      'GET  /health     — slot fill rates + current phase',
      'GET  /status     — detailed breakdown by slot type + reachability',
      'POST /run-batch  — process next batch manually',
    ].join('\n'), { status: 200, headers: { 'Content-Type': 'text/plain' } });
  },
};

// ─────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────

function extractFirstName(fullName: string): string {
  return fullName.split(' ')[0] || '';
}

function extractLastName(fullName: string): string {
  const parts = fullName.split(' ');
  return parts.length > 1 ? parts.slice(1).join(' ') : '';
}

function normalize(s: string): string {
  return (s || '').toLowerCase().trim().replace(/\s+/g, ' ');
}

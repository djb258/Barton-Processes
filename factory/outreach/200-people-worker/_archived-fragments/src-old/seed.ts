/**
 * Process 200 — SEED Phase
 *
 * Pulls territory company dossier from Neon into D1.
 * Runs on Day 1 of each month (or manual trigger via POST /seed).
 *
 * Seed order:
 *   1. companies (CT + identity)
 *   2. slots (all positions)
 *   3. people (via slot join)
 *   4. outreach_status
 *   5. dol
 *   6. blog
 *   7. bit_scores
 *   8. monitor_list (derived: filled slots with LinkedIn URLs)
 *   9. baseline (previous month's snapshots for diff)
 */

import { neon } from '@neondatabase/serverless';

interface SeedResult {
  table: string;
  rows: number;
  durationMs: number;
}

/**
 * Seed one table from Neon into D1.
 * Clears the D1 table first, then bulk inserts.
 */
async function seedTable(
  d1: D1Database,
  sql: ReturnType<typeof neon>,
  tableName: string,
  neonQuery: string,
  d1Columns: string[],
): Promise<SeedResult> {
  const start = Date.now();

  // Clear D1 table
  await d1.exec(`DELETE FROM ${tableName}`);

  // Fetch from Neon
  const rows = await sql(neonQuery);

  if (rows.length === 0) {
    return { table: tableName, rows: 0, durationMs: Date.now() - start };
  }

  // Batch insert into D1 (100 rows per batch, ignore duplicates)
  const batchSize = 100;
  const placeholders = d1Columns.map(() => '?').join(', ');
  const insertSql = `INSERT OR IGNORE INTO ${tableName} (${d1Columns.join(', ')}) VALUES (${placeholders})`;

  for (let i = 0; i < rows.length; i += batchSize) {
    const batch = rows.slice(i, i + batchSize);
    const stmts = batch.map((row) => {
      const values = d1Columns.map((col) => {
        const val = row[col];
        if (val === null || val === undefined) return null;
        if (typeof val === 'boolean') return val ? 1 : 0;
        return val;
      });
      return d1.prepare(insertSql).bind(...values);
    });
    await d1.batch(stmts);
  }

  return { table: tableName, rows: rows.length, durationMs: Date.now() - start };
}

/**
 * Full seed: pull entire territory dossier from Neon into D1.
 */
export async function seedFromNeon(d1: D1Database, neonUrl: string): Promise<SeedResult[]> {
  if (!neonUrl) {
    throw new Error('NEON_URL is not set. Run: wrangler secret put NEON_URL');
  }
  const sql = neon(neonUrl);
  const results: SeedResult[] = [];

  // 1. Companies (territory companies + identity)
  results.push(await seedTable(d1, sql, 'companies', `
    SELECT
      tc.company_unique_id,
      tc.outreach_id::text as outreach_id,
      tc.agent_name,
      tc.agent_number,
      tc.postal_code,
      tc.city,
      tc.state,
      tc.industry,
      tc.employees,
      ct.outreach_status,
      ct.source,
      ci.canonical_name,
      ci.company_domain,
      ci.identity_status,
      ci.normalized_domain,
      ci.sovereign_company_id::text as sovereign_company_id
    FROM people.v_territory_companies tc
    JOIN outreach.company_target ct ON ct.company_unique_id = tc.company_unique_id
    LEFT JOIN cl.company_identity ci ON ci.company_unique_id::text = tc.company_unique_id
  `, [
    'company_unique_id', 'outreach_id', 'agent_name', 'agent_number',
    'postal_code', 'city', 'state', 'industry', 'employees',
    'outreach_status', 'source',
    'canonical_name', 'company_domain', 'identity_status', 'normalized_domain', 'sovereign_company_id',
  ]));

  // 2. Slots
  results.push(await seedTable(d1, sql, 'slots', `
    SELECT
      cs.slot_id::text as slot_id,
      cs.outreach_id::text as outreach_id,
      cs.company_unique_id,
      cs.slot_type,
      cs.person_unique_id,
      CASE WHEN cs.is_filled THEN 1 ELSE 0 END as is_filled,
      cs.filled_at::text as filled_at,
      cs.confidence_score,
      cs.source_system
    FROM people.company_slot cs
    WHERE cs.company_unique_id IN (SELECT company_unique_id FROM people.v_territory_companies)
  `, [
    'slot_id', 'outreach_id', 'company_unique_id', 'slot_type',
    'person_unique_id', 'is_filled', 'filled_at', 'confidence_score', 'source_system',
  ]));

  // 3. People (via slot join — the correct path)
  results.push(await seedTable(d1, sql, 'people', `
    SELECT DISTINCT
      pm.unique_id,
      pm.company_unique_id,
      pm.company_slot_unique_id,
      pm.full_name,
      pm.first_name,
      pm.last_name,
      pm.title,
      pm.seniority,
      pm.department,
      pm.email,
      CASE WHEN pm.email_verified THEN 1 ELSE 0 END as email_verified,
      pm.email_verification_source,
      pm.linkedin_url,
      pm.twitter_url,
      pm.source_system,
      CASE WHEN pm.outreach_ready THEN 1 ELSE 0 END as outreach_ready,
      CASE WHEN pm.is_decision_maker THEN 1 ELSE 0 END as is_decision_maker
    FROM people.people_master pm
    WHERE pm.unique_id IN (
      SELECT cs.person_unique_id
      FROM people.company_slot cs
      WHERE cs.company_unique_id IN (SELECT company_unique_id FROM people.v_territory_companies)
      AND cs.person_unique_id IS NOT NULL
    )
  `, [
    'unique_id', 'company_unique_id', 'company_slot_unique_id',
    'full_name', 'first_name', 'last_name', 'title', 'seniority', 'department',
    'email', 'email_verified', 'email_verification_source',
    'linkedin_url', 'twitter_url', 'source_system',
    'outreach_ready', 'is_decision_maker',
  ]));

  // 4. Outreach status
  results.push(await seedTable(d1, sql, 'outreach_status', `
    SELECT
      o.outreach_id::text as outreach_id,
      o.sovereign_id::text as sovereign_id,
      o.domain,
      o.ein,
      CASE WHEN o.has_appointment THEN 1 ELSE 0 END as has_appointment
    FROM outreach.outreach o
    WHERE o.outreach_id IN (SELECT outreach_id::uuid FROM people.v_territory_companies)
  `, [
    'outreach_id', 'sovereign_id', 'domain', 'ein', 'has_appointment',
  ]));

  // 5. DOL
  results.push(await seedTable(d1, sql, 'dol', `
    SELECT
      d.dol_id::text as dol_id,
      d.outreach_id::text as outreach_id,
      d.ein,
      CASE WHEN d.filing_present THEN 1 ELSE 0 END as filing_present,
      d.funding_type,
      d.broker_or_advisor,
      d.carrier,
      d.renewal_month,
      d.outreach_start_month
    FROM outreach.dol d
    WHERE d.outreach_id IN (SELECT outreach_id::uuid FROM people.v_territory_companies)
  `, [
    'dol_id', 'outreach_id', 'ein', 'filing_present', 'funding_type',
    'broker_or_advisor', 'carrier', 'renewal_month', 'outreach_start_month',
  ]));

  // 6. Blog
  results.push(await seedTable(d1, sql, 'blog', `
    SELECT
      b.blog_id::text as blog_id,
      b.outreach_id::text as outreach_id,
      b.source_url,
      b.about_url,
      b.news_url,
      b.source_type,
      b.extraction_method,
      b.context_summary,
      b.last_extracted_at::text as last_extracted_at
    FROM outreach.blog b
    WHERE b.outreach_id IN (SELECT outreach_id::uuid FROM people.v_territory_companies)
  `, [
    'blog_id', 'outreach_id', 'source_url', 'about_url', 'news_url',
    'source_type', 'extraction_method', 'context_summary', 'last_extracted_at',
  ]));

  // 7. BIT Scores
  results.push(await seedTable(d1, sql, 'bit_scores', `
    SELECT
      bs.outreach_id::text as outreach_id,
      bs.score,
      bs.score_tier,
      bs.signal_count,
      bs.people_score,
      bs.dol_score,
      bs.blog_score,
      bs.talent_flow_score,
      bs.last_signal_at::text as last_signal_at,
      bs.last_scored_at::text as last_scored_at
    FROM outreach.bit_scores bs
    WHERE bs.outreach_id IN (SELECT outreach_id::uuid FROM people.v_territory_companies)
  `, [
    'outreach_id', 'score', 'score_tier', 'signal_count',
    'people_score', 'dol_score', 'blog_score', 'talent_flow_score',
    'last_signal_at', 'last_scored_at',
  ]));

  // 8. Monitor list (derived: filled slots with LinkedIn URLs)
  results.push(await seedTable(d1, sql, 'monitor_list', `
    SELECT
      person_id,
      company_unique_id,
      full_name,
      linkedin_url,
      slot_type,
      agent_name,
      agent_number
    FROM people.v_linkedin_monitor_list
  `, [
    'person_id', 'company_unique_id', 'full_name', 'linkedin_url',
    'slot_type', 'agent_name', 'agent_number',
  ]));

  return results;
}

/**
 * Seed baseline from previous month's snapshots.
 * Tries D1 first (last month's data may still be local).
 * Falls back to Neon vault.
 */
export async function seedBaseline(
  d1: D1Database,
  neonUrl: string,
  runMonth: string,
): Promise<SeedResult> {
  const start = Date.now();

  // Calculate previous month
  const d = new Date(runMonth);
  d.setMonth(d.getMonth() - 1);
  const prevMonth = d.toISOString().slice(0, 7) + '-01';

  // Clear baseline
  await d1.exec('DELETE FROM baseline');

  // Try D1 first
  const localCount = await d1.prepare(
    'SELECT COUNT(*) as cnt FROM snapshots WHERE run_month = ?'
  ).bind(prevMonth).first<{ cnt: number }>();

  if (localCount && localCount.cnt > 0) {
    await d1.exec(`
      INSERT INTO baseline (person_id, parsed_title, parsed_company, raw_title_tag, run_month)
      SELECT person_id, parsed_title, parsed_company, raw_title_tag, run_month
      FROM snapshots WHERE run_month = '${prevMonth}'
    `);
    return { table: 'baseline', rows: localCount.cnt, durationMs: Date.now() - start };
  }

  // Fall back to Neon vault
  const sql = neon(neonUrl);
  const rows = await sql`
    SELECT person_id, parsed_title, parsed_company, raw_title_tag, run_month::text as run_month
    FROM people.linkedin_snapshots
    WHERE run_month = ${prevMonth}
  `;

  if (rows.length > 0) {
    const insertSql = 'INSERT INTO baseline (person_id, parsed_title, parsed_company, raw_title_tag, run_month) VALUES (?, ?, ?, ?, ?)';
    const batchSize = 100;
    for (let i = 0; i < rows.length; i += batchSize) {
      const batch = rows.slice(i, i + batchSize);
      const stmts = batch.map((row) =>
        d1.prepare(insertSql).bind(
          row.person_id, row.parsed_title, row.parsed_company, row.raw_title_tag, row.run_month
        )
      );
      await d1.batch(stmts);
    }
  }

  return { table: 'baseline', rows: rows.length, durationMs: Date.now() - start };
}

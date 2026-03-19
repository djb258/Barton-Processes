/**
 * Intelligence Engine — Producer
 *
 * Reads companies, people, and monitor lists from D1.
 * Creates IntelligenceJob messages and sends them to the Queue.
 * Respects monthly cycle — doesn't re-queue already-processed items.
 * Tracks production state in D1 batch_progress table.
 */

import type { Env, IntelligenceJob, CompanyRow, PersonRow, MonitorRow, JobType, ProductionStats } from './types';

// ── Main Producer Entry Point ────────────────────────────────

export async function produce(env: Env): Promise<ProductionStats> {
  const batchSize = parseInt(env.BATCH_SIZE, 10) || 50;
  const batchId = generateBatchId();
  const monthKey = getCurrentMonthKey();

  const jobs: IntelligenceJob[] = [];

  // 1. Get already-processed items this month
  const processed = await getProcessedThisMonth(env.D1, monthKey);

  // 2. Generate jobs from monitor_list (primary source)
  const monitorJobs = await generateMonitorJobs(env.D1, processed, batchSize, monthKey);
  jobs.push(...monitorJobs);

  // 3. Generate person movement jobs (linkedin_profile)
  const remaining = batchSize - jobs.length;
  if (remaining > 0) {
    const personJobs = await generatePersonJobs(env.D1, processed, remaining, monthKey);
    jobs.push(...personJobs);
  }

  // 4. Generate company-level jobs (glassdoor, indeed, news)
  const remaining2 = batchSize - jobs.length;
  if (remaining2 > 0) {
    const companyJobs = await generateCompanyJobs(env.D1, processed, remaining2, monthKey);
    jobs.push(...companyJobs);
  }

  if (jobs.length === 0) {
    return {
      total_jobs: 0,
      by_type: {},
      batch_id: batchId,
      produced_at: new Date().toISOString(),
    };
  }

  // 5. Send jobs to queue in batches (Queue.send can do one at a time,
  //    Queue.sendBatch can do up to 100)
  const queueBatches = chunkArray(jobs, 100);
  for (const batch of queueBatches) {
    await env.INTELLIGENCE_QUEUE.sendBatch(
      batch.map((job) => ({
        body: job,
        contentType: 'json',
      })),
    );
  }

  // 6. Record batch progress
  const byType: Record<string, number> = {};
  for (const job of jobs) {
    byType[job.job_type] = (byType[job.job_type] ?? 0) + 1;
  }

  await recordBatchProgress(env.D1, batchId, monthKey, jobs.length, byType);

  // 7. Record queued state for each job
  await recordQueuedJobs(env.D1, jobs, monthKey);

  return {
    total_jobs: jobs.length,
    by_type: byType,
    batch_id: batchId,
    produced_at: new Date().toISOString(),
  };
}

// ── Job Generators ───────────────────────────────────────────

/**
 * Generate jobs from monitor_list table.
 * monitor_list contains companies with explicit monitor_types
 * (comma-separated job types to run).
 */
async function generateMonitorJobs(
  db: D1Database,
  processed: Set<string>,
  limit: number,
  monthKey: string,
): Promise<IntelligenceJob[]> {
  const jobs: IntelligenceJob[] = [];

  try {
    const rows = await db
      .prepare(
        `SELECT company_unique_id, company_name, domain, state, agent_name, monitor_types
         FROM monitor_list
         WHERE active = 1
         LIMIT ?`,
      )
      .bind(limit * 3) // Over-fetch since some may be already processed
      .all<MonitorRow>();

    for (const row of rows.results ?? []) {
      const types = (row.monitor_types ?? '')
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean) as JobType[];

      for (const jobType of types) {
        const jobKey = makeJobKey(row.company_unique_id, jobType, monthKey);
        if (processed.has(jobKey)) continue;
        if (jobs.length >= limit) break;

        jobs.push(createJob(jobType, row.company_unique_id, row.company_name, {
          company_domain: row.domain ?? undefined,
          state: row.state ?? undefined,
          agent_name: row.agent_name,
        }));
      }

      if (jobs.length >= limit) break;
    }
  } catch {
    // monitor_list table may not exist yet — that's fine
  }

  return jobs;
}

/**
 * Generate linkedin_profile jobs for people in the people table.
 */
async function generatePersonJobs(
  db: D1Database,
  processed: Set<string>,
  limit: number,
  monthKey: string,
): Promise<IntelligenceJob[]> {
  const jobs: IntelligenceJob[] = [];

  try {
    const rows = await db
      .prepare(
        `SELECT person_id, company_unique_id, company_name, person_name,
                linkedin_url, stored_title, agent_name
         FROM people
         WHERE person_name IS NOT NULL AND person_name != ''
         LIMIT ?`,
      )
      .bind(limit * 2)
      .all<PersonRow>();

    for (const row of rows.results ?? []) {
      const jobKey = makeJobKey(row.person_id, 'linkedin_profile', monthKey);
      if (processed.has(jobKey)) continue;
      if (jobs.length >= limit) break;

      jobs.push(createJob('linkedin_profile', row.company_unique_id, row.company_name, {
        person_id: row.person_id,
        person_name: row.person_name,
        linkedin_url: row.linkedin_url ?? undefined,
        stored_title: row.stored_title ?? undefined,
        agent_name: row.agent_name,
      }));
    }
  } catch {
    // people table may not exist yet
  }

  return jobs;
}

/**
 * Generate company-level intelligence jobs (glassdoor, indeed, news, blog).
 */
async function generateCompanyJobs(
  db: D1Database,
  processed: Set<string>,
  limit: number,
  monthKey: string,
): Promise<IntelligenceJob[]> {
  const jobs: IntelligenceJob[] = [];
  const companyJobTypes: JobType[] = [
    'glassdoor_sentiment',
    'indeed_hiring',
    'company_news',
    'blog_freshness',
  ];

  try {
    const rows = await db
      .prepare(
        `SELECT company_unique_id, company_name, domain, state, agent_name
         FROM companies
         LIMIT ?`,
      )
      .bind(limit * 2)
      .all<CompanyRow>();

    for (const row of rows.results ?? []) {
      for (const jobType of companyJobTypes) {
        const jobKey = makeJobKey(row.company_unique_id, jobType, monthKey);
        if (processed.has(jobKey)) continue;
        if (jobs.length >= limit) break;

        // Skip blog_freshness if no domain
        if (jobType === 'blog_freshness' && !row.domain) continue;

        jobs.push(createJob(jobType, row.company_unique_id, row.company_name, {
          company_domain: row.domain ?? undefined,
          state: row.state ?? undefined,
          agent_name: row.agent_name,
        }));
      }

      if (jobs.length >= limit) break;
    }
  } catch {
    // companies table may not exist yet
  }

  return jobs;
}

// ── D1 State Tracking ────────────────────────────────────────

async function getProcessedThisMonth(
  db: D1Database,
  monthKey: string,
): Promise<Set<string>> {
  const processed = new Set<string>();

  try {
    const rows = await db
      .prepare(
        `SELECT entity_id, job_type FROM job_queue_state
         WHERE month_key = ? AND (status = 'queued' OR status = 'completed')`,
      )
      .bind(monthKey)
      .all<{ entity_id: string; job_type: string }>();

    for (const row of rows.results ?? []) {
      processed.add(makeJobKey(row.entity_id, row.job_type as JobType, monthKey));
    }
  } catch {
    // Table may not exist yet — treat as empty
  }

  return processed;
}

async function recordBatchProgress(
  db: D1Database,
  batchId: string,
  monthKey: string,
  totalJobs: number,
  byType: Record<string, number>,
): Promise<void> {
  try {
    await db
      .prepare(
        `INSERT INTO batch_progress (batch_id, month_key, total_jobs, by_type, produced_at)
         VALUES (?, ?, ?, ?, ?)`,
      )
      .bind(batchId, monthKey, totalJobs, JSON.stringify(byType), new Date().toISOString())
      .run();
  } catch {
    // Table may not exist yet — non-fatal
  }
}

async function recordQueuedJobs(
  db: D1Database,
  jobs: IntelligenceJob[],
  monthKey: string,
): Promise<void> {
  try {
    const stmt = db.prepare(
      `INSERT OR IGNORE INTO job_queue_state (entity_id, job_type, month_key, status, queued_at)
       VALUES (?, ?, ?, 'queued', ?)`,
    );

    const now = new Date().toISOString();
    const batch = jobs.map((job) => {
      const entityId = job.person_id ?? job.company_unique_id;
      return stmt.bind(entityId, job.job_type, monthKey, now);
    });

    // D1 batch limit is 100 statements
    const chunks = chunkArray(batch, 100);
    for (const chunk of chunks) {
      await db.batch(chunk);
    }
  } catch {
    // Non-fatal — jobs are already on the queue
  }
}

// ── Utilities ────────────────────────────────────────────────

function createJob(
  jobType: JobType,
  companyUniqueId: string,
  companyName: string,
  opts: {
    person_id?: string;
    person_name?: string;
    linkedin_url?: string;
    stored_title?: string;
    company_domain?: string;
    state?: string;
    slot_type?: string;
    agent_name: string;
  },
): IntelligenceJob {
  return {
    job_id: crypto.randomUUID(),
    job_type: jobType,
    company_unique_id: companyUniqueId,
    company_name: companyName,
    company_domain: opts.company_domain,
    agent_name: opts.agent_name,
    person_id: opts.person_id,
    person_name: opts.person_name,
    linkedin_url: opts.linkedin_url,
    stored_title: opts.stored_title,
    slot_type: opts.slot_type,
    state: opts.state,
    priority: getPriority(jobType),
    attempt: 0,
    max_attempts: 3,
    created_at: new Date().toISOString(),
  };
}

function getPriority(jobType: JobType): number {
  const priorities: Record<JobType, number> = {
    linkedin_profile: 1,    // Highest — movement detection
    indeed_hiring: 2,       // High — active hiring signal
    company_news: 3,
    glassdoor_sentiment: 4,
    slot_search: 5,
    linkedin_company: 6,
    blog_freshness: 7,
    state_wc_lookup: 8,     // Lowest
  };
  return priorities[jobType] ?? 10;
}

function makeJobKey(entityId: string, jobType: string, monthKey: string): string {
  return `${entityId}:${jobType}:${monthKey}`;
}

function getCurrentMonthKey(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

function generateBatchId(): string {
  const now = new Date();
  const ts = now.toISOString().replace(/[-:T.Z]/g, '').slice(0, 14);
  const rand = crypto.randomUUID().slice(0, 8);
  return `batch-${ts}-${rand}`;
}

function chunkArray<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

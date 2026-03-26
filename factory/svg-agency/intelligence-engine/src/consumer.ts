/**
 * Intelligence Engine — Consumer
 *
 * Receives batches of IntelligenceJob messages from the Queue.
 * For each job: builds query, fetches Startpage, parses results, writes to D1.
 * Handles retries (ack/retry on failure) and pacing between requests.
 */

import type { Env, IntelligenceJob, FetchResult } from './types';
import { buildQuery, fetchStartpage } from './search';
import { parseResults } from './parsers';

// ── Main Consumer Entry Point ────────────────────────────────

export async function consume(
  batch: MessageBatch<IntelligenceJob>,
  env: Env,
): Promise<void> {
  const minDelay = parseInt(env.MIN_DELAY_MS, 10) || 3000;
  const maxDelay = parseInt(env.MAX_DELAY_MS, 10) || 8000;

  console.log(`[consumer] Processing batch of ${batch.messages.length} jobs`);

  for (const message of batch.messages) {
    const job = message.body;

    try {
      // Process the job
      const result = await processJob(job);

      // Write result to D1
      await writeResult(env.D1, result);

      // Update queue state to completed
      await updateQueueState(env.D1, job, 'completed');

      // Acknowledge the message
      message.ack();

      console.log(
        `[consumer] OK: ${job.job_type} | ${job.company_name} | score=${result.signal_score} | ${result.duration_ms}ms`,
      );
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error(`[consumer] FAIL: ${job.job_type} | ${job.company_name} | ${errorMsg}`);

      // Write error result to D1
      await writeErrorResult(env.D1, job, errorMsg);

      // Retry or dead-letter
      if (job.attempt < job.max_attempts) {
        // Retry — CF Queues handles this via message.retry()
        message.retry({
          delaySeconds: getRetryDelay(job.attempt),
        });
      } else {
        // Max attempts reached — ack to prevent infinite retry
        // Error is already recorded in D1
        await updateQueueState(env.D1, job, 'failed');
        message.ack();
        console.error(`[consumer] DEAD: ${job.job_type} | ${job.company_name} | max attempts reached`);
      }
    }

    // Pace between requests — wait before processing next message
    // This prevents hammering Startpage from a single batch
    if (batch.messages.indexOf(message) < batch.messages.length - 1) {
      const delay = randomDelay(minDelay, maxDelay);
      await sleep(delay);
    }
  }

  console.log(`[consumer] Batch complete: ${batch.messages.length} jobs processed`);
}

// ── Job Processor ────────────────────────────────────────────

async function processJob(job: IntelligenceJob): Promise<FetchResult> {
  const start = Date.now();

  // Build the search query from template + job data
  const query = buildQuery(job);

  // Fetch from Startpage (direct — no proxy for now)
  const searchResponse = await fetchStartpage(query);

  const duration = Date.now() - start;

  // Handle CAPTCHA
  if (searchResponse.captcha_detected) {
    throw new Error('CAPTCHA_DETECTED');
  }

  // Handle fetch errors
  if (searchResponse.error && !searchResponse.results.length) {
    throw new Error(searchResponse.error);
  }

  // Parse results using type-specific parser
  const result = parseResults(
    job,
    searchResponse.results,
    searchResponse.status,
    duration,
    searchResponse.error,
  );

  return result;
}

// ── D1 Writers ───────────────────────────────────────────────

async function writeResult(db: D1Database, result: FetchResult): Promise<void> {
  try {
    await db
      .prepare(
        `INSERT INTO intelligence_results (
           job_id, job_type, company_unique_id, person_id,
           signal_type, signal_score, raw_snippet,
           parsed_data, keyword_matches,
           movement_detected, movement_type,
           search_engine, http_status, duration_ms,
           fetched_at, error
         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        result.job_id,
        result.job_type,
        result.company_unique_id,
        result.person_id ?? null,
        result.signal_type,
        result.signal_score,
        result.raw_snippet,
        JSON.stringify(result.parsed_data),
        JSON.stringify(result.keyword_matches),
        result.movement_detected ?? null,
        result.movement_type ?? null,
        result.search_engine,
        result.http_status,
        result.duration_ms,
        result.fetched_at,
        result.error,
      )
      .run();
  } catch (err) {
    console.error(`[consumer] D1 write error: ${err instanceof Error ? err.message : err}`);
  }
}

async function writeErrorResult(db: D1Database, job: IntelligenceJob, error: string): Promise<void> {
  try {
    await db
      .prepare(
        `INSERT INTO intelligence_results (
           job_id, job_type, company_unique_id, person_id,
           signal_type, signal_score, raw_snippet,
           parsed_data, keyword_matches,
           search_engine, http_status, duration_ms,
           fetched_at, error
         ) VALUES (?, ?, ?, ?, ?, 0, '', '{}', '[]', 'startpage', 0, 0, ?, ?)`,
      )
      .bind(
        job.job_id,
        job.job_type,
        job.company_unique_id,
        job.person_id ?? null,
        'ERROR',
        new Date().toISOString(),
        error,
      )
      .run();
  } catch (err) {
    console.error(`[consumer] D1 error-write error: ${err instanceof Error ? err.message : err}`);
  }
}

async function updateQueueState(
  db: D1Database,
  job: IntelligenceJob,
  status: 'completed' | 'failed',
): Promise<void> {
  const entityId = job.person_id ?? job.company_unique_id;
  const monthKey = getCurrentMonthKey();

  try {
    await db
      .prepare(
        `UPDATE job_queue_state
         SET status = ?, completed_at = ?
         WHERE entity_id = ? AND job_type = ? AND month_key = ?`,
      )
      .bind(status, new Date().toISOString(), entityId, job.job_type, monthKey)
      .run();
  } catch {
    // Non-fatal
  }
}

// ── Utilities ────────────────────────────────────────────────

function getRetryDelay(attempt: number): number {
  // Exponential backoff: 60s, 300s, 900s
  const delays = [60, 300, 900];
  return delays[attempt] ?? 900;
}

function randomDelay(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getCurrentMonthKey(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

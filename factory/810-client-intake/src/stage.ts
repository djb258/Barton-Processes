/**
 * 810 — Client Data Intake: Staging
 *
 * Writes validated data to D1 staging tables.
 * intake_record is INSERT-only (immutable).
 */

export interface Env {
  D1: D1Database;
  NEON_URL: string;
}

export interface StageResult {
  batch_id: string;
  staged: number;
  spoke: string;
}

export async function stageRecords(
  env: Env, clientId: string, table: string, records: { data: Record<string, unknown> }[],
): Promise<StageResult> {
  const batchId = crypto.randomUUID();

  // Create enrollment_intake batch header
  await env.D1.prepare(`
    INSERT INTO enrollment_intake (enrollment_intake_id, client_id, status)
    VALUES (?, ?, 'pending')
  `).bind(batchId, clientId).run();

  // Write each record to intake_record (immutable)
  let staged = 0;
  for (const record of records) {
    await env.D1.prepare(`
      INSERT INTO intake_record (intake_record_id, client_id, enrollment_intake_id, spoke, raw_payload)
      VALUES (?, ?, ?, ?, ?)
    `).bind(
      crypto.randomUUID(),
      clientId,
      batchId,
      table,
      JSON.stringify(record.data),
    ).run();
    staged++;
  }

  // Update batch status
  await env.D1.prepare(
    "UPDATE enrollment_intake SET status = 'staged' WHERE enrollment_intake_id = ?"
  ).bind(batchId).run();

  console.log(`[810] STAGE: batch=${batchId} table=${table} staged=${staged}`);
  return { batch_id: batchId, staged, spoke: table };
}

/**
 * bp.810 — Client Intake: Staging
 * Flat spoke model — rewritten 2026-05-12
 *
 * All intake writes land in client_staging_intake FIRST (immutable audit trail).
 * Returns the autoincrement intake_id for downstream promotion.
 */

export interface Env {
  D1: D1Database;
  CENSUS_DB: D1Database;
}

export interface StageResult {
  intake_id: number;
  intake_type: string;
  spoke: string;
}

/**
 * stageIntakeRaw — inserts one raw payload into client_staging_intake.
 * intake_type: 'company' (org-level records) | 'employee' (person-level records)
 * spoke maps to the eventual canonical table.
 */
export async function stageIntakeRaw(
  env: Env,
  payload: Record<string, unknown>,
  source: string,
): Promise<StageResult> {
  const spoke = payload['spoke'] as string;
  // company-level spokes: vendor, compliance, contact, interaction
  // employee-level spokes: employee
  const intakeType = spoke === 'employee' ? 'employee' : 'company';

  const result = await env.D1.prepare(`
    INSERT INTO client_staging_intake (intake_type, raw_data, source)
    VALUES (?, ?, ?)
  `).bind(intakeType, JSON.stringify(payload), source).run();

  // D1 returns meta.last_row_id for autoincrement
  const intakeId = (result.meta as { last_row_id?: number }).last_row_id ?? 0;

  console.log(`[810] STAGED: intake_id=${intakeId} spoke=${spoke} type=${intakeType}`);
  return { intake_id: intakeId, intake_type: intakeType, spoke };
}

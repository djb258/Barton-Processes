/**
 * FactFinder Service — Meeting 1
 *
 * CTB Branch: app/
 * Sub-Hub: SUB-MEETING-1
 * IMO Layer: Middle (owns logic, state, decisions)
 *
 * Orchestrates: mint sales_id → upsert factfinder → log errors
 * UI calls this service — never the query layer directly.
 */

import { FactfinderFormInput } from '@/data/types/factfinder';
import {
  mintSalesId,
  upsertFactfinder,
  getFactfinder,
  logFactfinderError,
} from '@/data/queries/factfinder';

const PROCESS_ID = `PRC-SALES-FF-${Date.now()}`;

export type SaveFactfinderResult =
  | { success: true; salesId: string }
  | { success: false; error: string };

/**
 * Save factfinder form data.
 *
 * Flow:
 * 1. Ensure sales_id exists in spine (mint if new)
 * 2. Upsert canonical factfinder row
 * 3. On error, log to sales_factfinder_errors
 */
export async function saveFactfinder(
  salesId: string,
  input: FactfinderFormInput
): Promise<SaveFactfinderResult> {
  try {
    // Step 1: Mint sales_id in spine if not exists
    const mintResult = await mintSalesId(salesId);
    if (mintResult.error) {
      await logFactfinderError({
        sales_id: salesId,
        error_code: 'SPINE_MINT_FAILED',
        payload: { message: mintResult.error },
        process_id: PROCESS_ID,
      });
      return { success: false, error: `Failed to initialize sales process: ${mintResult.error}` };
    }

    // Step 2: Upsert factfinder canonical row
    const upsertResult = await upsertFactfinder({
      sales_id: salesId,
      employer_name: input.companyName,
      employee_count: input.totalEmployees,
      renewal_month: input.renewalMonth,
      prior_broker: input.broker,
    });

    if (upsertResult.error) {
      await logFactfinderError({
        sales_id: salesId,
        error_code: 'FACTFINDER_UPSERT_FAILED',
        payload: { message: upsertResult.error },
        process_id: PROCESS_ID,
      });
      return { success: false, error: `Failed to save fact finder data: ${upsertResult.error}` };
    }

    return { success: true, salesId };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    await logFactfinderError({
      sales_id: salesId,
      error_code: 'FACTFINDER_UNEXPECTED',
      payload: { message },
      process_id: PROCESS_ID,
    }).catch(() => {});
    return { success: false, error: message };
  }
}

/**
 * Load existing factfinder data for a sales_id.
 * Returns null if no record exists.
 */
export async function loadFactfinder(salesId: string) {
  const { data, error } = await getFactfinder(salesId);
  if (error) {
    return { data: null, error };
  }
  return { data, error: null };
}

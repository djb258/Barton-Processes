/**
 * Process 810 — Client Data Intake
 *
 * CF Worker. HTTP endpoint for CSV/API intake.
 * Validates → stages → promotes → vaults.
 * One worker handles all 5 spokes via payload routing.
 */

import type { Env } from './stage';
import { validateIntake } from './validate';
import { stageRecords } from './stage';
import { promoteRecords } from './promote';
import { vaultRecords } from './vault';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === '/health') {
      return Response.json({
        process: 'PROC-CLIENT-DATA-INTAKE', number: 810, status: 'ok',
      });
    }

    // Status — summary per spoke
    if (url.pathname === '/status') {
      const staged = await env.D1.prepare("SELECT COUNT(*) as cnt FROM intake_record WHERE promoted_at IS NULL").first<{ cnt: number }>();
      const promoted = await env.D1.prepare("SELECT COUNT(*) as cnt FROM intake_record WHERE promoted_at IS NOT NULL").first<{ cnt: number }>();
      const batches = await env.D1.prepare("SELECT status, COUNT(*) as cnt FROM enrollment_intake GROUP BY status").all();

      return Response.json({
        process: 'PROC-CLIENT-DATA-INTAKE',
        intake_records: { staged: staged?.cnt ?? 0, promoted: promoted?.cnt ?? 0 },
        batches: batches.results,
      });
    }

    // Intake — validate, stage, promote in one pass
    if (url.pathname === '/intake' && request.method === 'POST') {
      try {
        const body = await request.json<{ client_id?: string; table?: string; data?: unknown[] }>();

        if (!body.client_id) return Response.json({ error: 'client_id required' }, { status: 400 });
        if (!body.table) return Response.json({ error: 'table required (plan, person, election, vendor, etc.)' }, { status: 400 });
        if (!body.data || !Array.isArray(body.data) || body.data.length === 0) {
          return Response.json({ error: 'data[] required (non-empty array)' }, { status: 400 });
        }

        // Verify client exists in D1
        const client = await env.D1.prepare('SELECT client_id FROM client WHERE client_id = ?').bind(body.client_id).first();
        if (!client) return Response.json({ error: `client_id ${body.client_id} not found in D1` }, { status: 404 });

        // 1. Validate
        const validation = validateIntake(body.table, body.data);

        // 2. Stage valid records
        let stageResult = null;
        if (validation.valid.length > 0) {
          stageResult = await stageRecords(env, body.client_id, body.table, validation.valid);

          // 3. Promote
          const promoteResult = await promoteRecords(env, body.client_id, stageResult.batch_id);

          return Response.json({
            action: 'intake',
            client_id: body.client_id,
            table: body.table,
            received: body.data.length,
            validated: validation.valid.length,
            validation_errors: validation.errors.length,
            batch_id: stageResult.batch_id,
            promoted: promoteResult.promoted,
            promote_errors: promoteResult.errors,
            validation_error_details: validation.errors.length > 0 ? validation.errors.slice(0, 10) : undefined,
          }, { status: 201 });
        }

        // All records failed validation
        return Response.json({
          action: 'intake',
          client_id: body.client_id,
          table: body.table,
          received: body.data.length,
          validated: 0,
          validation_errors: validation.errors.length,
          validation_error_details: validation.errors.slice(0, 10),
        }, { status: 422 });

      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return Response.json({ error: msg }, { status: 500 });
      }
    }

    // Vault — push all unvaulted records to Neon
    if (url.pathname === '/vault' && request.method === 'POST') {
      try {
        const result = await vaultRecords(env);
        return Response.json({ action: 'vault', ...result });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return Response.json({ error: msg }, { status: 500 });
      }
    }

    // Errors — per client
    if (url.pathname.startsWith('/errors/')) {
      const clientId = url.pathname.split('/errors/')[1];
      if (!clientId) return Response.json({ error: 'client_id required' }, { status: 400 });

      const errorTables = ['client_error', 'plan_error', 'employee_error', 'vendor_error', 'service_error'];
      const summary: Record<string, number> = {};

      for (const table of errorTables) {
        const count = await env.D1.prepare(
          `SELECT COUNT(*) as cnt FROM ${table} WHERE client_id = ? AND status = 'open'`
        ).bind(clientId).first<{ cnt: number }>();
        summary[table] = count?.cnt ?? 0;
      }

      return Response.json({ client_id: clientId, open_errors: summary });
    }

    return new Response([
      'Process 810 — Client Data Intake',
      '',
      'GET  /health              — health check',
      'GET  /status              — intake summary',
      'POST /intake              — { client_id, table, data[] } → validate → stage → promote',
      'POST /vault               — push unvaulted to Neon',
      'GET  /errors/:client_id   — error summary per spoke',
    ].join('\n'), { status: 200 });
  },
};

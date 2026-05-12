/**
 * bp.810 — Client Data Intake Worker
 * Flat spoke model — rewritten 2026-05-12
 *
 * Routes:
 *   GET  /health                   — liveness probe
 *   POST /intake                   — stage + promote one intake payload
 *   POST /vault                    — 410 Gone (single-tier D1; no Neon vault)
 *   GET  /errors/:client_id        — open errors across all spoke error tables
 *
 * Intake flow:
 *   1. Zod validates payload at HTTP boundary (discriminated union on spoke)
 *   2. Pre-exist gate: client_id must be in clients table (written by bp.800)
 *   3. Stage raw JSON to client_staging_intake (immutable, always first)
 *   4. Promote to canonical spoke table (contact/employee/vendor/compliance/interaction)
 *   5. On promotion failure → write to spoke *_error table; staging row still marked processed
 */

import { IntakePayloadSchema } from './validate';
import { stageIntakeRaw, type Env } from './stage';
import { promoteFromStaging } from './promote';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const method = request.method.toUpperCase();
    const path = url.pathname;

    // ── GET /health ─────────────────────────────────────────
    if (method === 'GET' && path === '/health') {
      return json({ status: 'ok', worker: 'client-intake-810', ts: new Date().toISOString() });
    }

    // ── POST /vault — 410 Gone ───────────────────────────────
    if (method === 'POST' && path === '/vault') {
      return json({ error: 'Vault endpoint removed. Single-tier D1 model in use.' }, 410);
    }

    // ── GET /errors/:client_id ───────────────────────────────
    if (method === 'GET' && path.startsWith('/errors/')) {
      const clientId = path.replace('/errors/', '').split('/')[0];
      if (!clientId) return json({ error: 'client_id required' }, 400);
      return handleGetErrors(env, clientId);
    }

    // ── POST /intake ─────────────────────────────────────────
    if (method === 'POST' && path === '/intake') {
      return handleIntake(request, env);
    }

    return json({ error: 'Not found' }, 404);
  },
};

// ─── Handler: POST /intake ───────────────────────────────────

async function handleIntake(request: Request, env: Env): Promise<Response> {
  // 1. Parse body
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Invalid JSON body' }, 400);
  }

  // 2. Zod boundary validation
  const parsed = IntakePayloadSchema.safeParse(body);
  if (!parsed.success) {
    return json({ error: 'Validation failed', issues: parsed.error.issues }, 422);
  }

  const payload = parsed.data;
  const clientId = payload.client_id;
  const spoke = payload.spoke;

  // 3. Pre-exist gate: client must exist in clients table (written by bp.800)
  const client = await env.D1.prepare(
    'SELECT client_id FROM clients WHERE client_id = ?'
  ).bind(clientId).first<{ client_id: string }>();

  if (!client) {
    return json({ error: 'client_id not found', client_id: clientId }, 404);
  }

  // 4. Stage raw payload (immutable audit trail — always first)
  const source = request.headers.get('X-Intake-Source') ?? 'api';
  const stageResult = await stageIntakeRaw(env, payload as Record<string, unknown>, source);

  // 5. Promote to canonical spoke table
  const promoteResult = await promoteFromStaging(env, stageResult.intake_id, spoke, clientId);

  if (promoteResult.success) {
    return json({
      intake_id: stageResult.intake_id,
      spoke,
      client_id: clientId,
      status: 'promoted',
    }, 201);
  } else {
    return json({
      intake_id: stageResult.intake_id,
      spoke,
      client_id: clientId,
      status: 'staged_with_error',
      error: promoteResult.error,
    }, 422);
  }
}

// ─── Handler: GET /errors/:client_id ────────────────────────

async function handleGetErrors(env: Env, clientId: string): Promise<Response> {
  const errorTables = [
    'client_contacts_error',
    'client_employees_error',
    'client_vendors_error',
    'client_compliance_error',
    'client_interactions_error',
  ];

  const errors: Record<string, unknown[]> = {};
  for (const table of errorTables) {
    const rows = await env.D1.prepare(
      `SELECT * FROM ${table} WHERE client_id = ? AND status = 'open' ORDER BY created_at DESC LIMIT 50`
    ).bind(clientId).all();
    if (rows.results && rows.results.length > 0) {
      errors[table] = rows.results;
    }
  }

  return json({ client_id: clientId, errors });
}

// ─── Utility ─────────────────────────────────────────────────

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

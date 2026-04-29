// ═══════════════════════════════════════════════════════════════
// Production Line Engine — CF Worker (the rim)
// ═══════════════════════════════════════════════════════════════
// BAR-195, BAR-196 | Hub-Spoke: Hono rim + DO agents
// No logic here — routes to agents and D1 queries only.

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { routeAgentRequest } from 'agents';
import type { Env, OrbtMode } from './types';

export { OrchestratorAgent } from './agents/orchestrator';
export { LineAgent } from './agents/line-agent';

const app = new Hono<{ Bindings: Env }>();
app.use('*', cors());

// Auth (skip health + agent WebSocket routes)
app.use('*', async (c, next) => {
  if (c.req.path === '/health') return next();
  if (c.req.path.startsWith('/agents/')) return next();

  const header = c.req.header('Authorization') ?? c.req.header('X-API-Key') ?? '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : header;
  if (!token || token !== c.env.PRODUCTION_API_KEY) {
    return c.json({ error: 'Unauthorized' }, 401);
  }
  return next();
});

// Health
app.get('/health', async (c) => {
  const goals = await c.env.D1_PRODUCTION.prepare('SELECT COUNT(*) as count FROM production_goals').first<{ count: number }>();
  const errors = await c.env.D1_PRODUCTION.prepare("SELECT COUNT(*) as count FROM fleet_failures WHERE status = 'open'").first<{ count: number }>();
  return c.json({
    status: 'ok',
    goals: goals?.count ?? 0,
    open_fleet_failures: errors?.count ?? 0,
    timestamp: new Date().toISOString(),
  });
});

// Submit a goal → orchestrator dispatches to line agent
app.post('/goals', async (c) => {
  const body = await c.req.json<{
    line: string;
    workpiece_id: string;
    workpiece_name?: string;
    source?: string;
    inbox_task_id?: string;
  }>();

  if (!body.line || !body.workpiece_id) {
    return c.json({ error: 'line and workpiece_id are required' }, 400);
  }

  const orchId = c.env.ORCHESTRATOR.idFromName('hub');
  const orch = c.env.ORCHESTRATOR.get(orchId);

  const res = await orch.fetch(new Request('http://internal/dispatch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }));

  const result = await res.json();
  return c.json(result, res.status as any);
});

// List goals
app.get('/goals', async (c) => {
  const line = c.req.query('line');
  const orbt = c.req.query('orbt_mode');
  const limit = parseInt(c.req.query('limit') ?? '50');

  let sql = 'SELECT * FROM production_goals WHERE 1=1';
  const params: any[] = [];
  if (line) { sql += ' AND line = ?'; params.push(line); }
  if (orbt) { sql += ' AND orbt_mode = ?'; params.push(orbt); }
  sql += ' ORDER BY created_at DESC LIMIT ?';
  params.push(limit);

  const result = await c.env.D1_PRODUCTION.prepare(sql).bind(...params).all();
  return c.json({ goals: result.results });
});

// Get goal with steps + trace
app.get('/goals/:goal_id', async (c) => {
  const { goal_id } = c.req.param();
  const goal = await c.env.D1_PRODUCTION.prepare('SELECT * FROM production_goals WHERE goal_id = ?').bind(goal_id).first();
  if (!goal) return c.json({ error: 'Not found' }, 404);

  const steps = await c.env.D1_PRODUCTION.prepare('SELECT * FROM production_steps WHERE goal_id = ? ORDER BY sequence').bind(goal_id).all();
  const trace = await c.env.D1_PRODUCTION.prepare('SELECT * FROM execution_trace WHERE goal_id = ? ORDER BY timestamp DESC LIMIT 50').bind(goal_id).all();
  const logbook = await c.env.D1_PRODUCTION.prepare('SELECT * FROM production_logbook WHERE goal_id = ? ORDER BY signed_at DESC').bind(goal_id).all();

  return c.json({ goal, steps: steps.results, trace: trace.results, logbook: logbook.results });
});

// Request certification (builder calls this — does NOT certify)
app.post('/goals/:goal_id/request-certification', async (c) => {
  const { goal_id } = c.req.param();
  const goal = await c.env.D1_PRODUCTION.prepare('SELECT orbt_mode FROM production_goals WHERE goal_id = ?').bind(goal_id).first<{ orbt_mode: string }>();
  if (!goal) return c.json({ error: 'Not found' }, 404);
  if (goal.orbt_mode !== 'BUILD') return c.json({ error: `Cannot request certification from ${goal.orbt_mode}` }, 400);

  return c.json({ status: 'awaiting_certification', goal_id, message: 'Auditor must review execution trace and call /certify' });
});

// Certify goal (AUDITOR ONLY — different engine than builder)
app.post('/goals/:goal_id/certify', async (c) => {
  const { goal_id } = c.req.param();
  const body = await c.req.json<{ auditor: string; notes?: string }>();

  if (!body.auditor) return c.json({ error: 'auditor field is required' }, 400);

  const goal = await c.env.D1_PRODUCTION.prepare('SELECT * FROM production_goals WHERE goal_id = ?').bind(goal_id).first<any>();
  if (!goal) return c.json({ error: 'Not found' }, 404);
  if (goal.orbt_mode !== 'BUILD') return c.json({ error: `Cannot certify from ${goal.orbt_mode}` }, 400);

  // Check all callable steps are done
  const pending = await c.env.D1_PRODUCTION.prepare(
    "SELECT COUNT(*) as count FROM production_steps WHERE goal_id = ? AND status IN ('pending','blocked','running','failed')"
  ).bind(goal_id).first<{ count: number }>();
  if (pending && pending.count > 0) return c.json({ error: `${pending.count} steps still incomplete` }, 400);

  // Certify — ORBT → OPERATE
  await c.env.D1_PRODUCTION.prepare(
    "UPDATE production_goals SET orbt_mode = 'OPERATE', certified_by = ?, certified_at = datetime('now'), updated_at = datetime('now') WHERE goal_id = ?"
  ).bind(body.auditor, goal_id).run();

  // Write birth certificate to logbook (§12)
  await c.env.D1_PRODUCTION.prepare(`
    INSERT INTO production_logbook (entry_id, goal_id, heir_ref, orbt_entered, orbt_exited, visit_path, action, authority, gates_passed, checklist_type, signed_by, notes)
    VALUES (?, ?, ?, 'BUILD', 'OPERATE', 'CERTIFICATION', ?, 'Bedrock §8 — auditor certification', '{"imo":true,"ctb":true,"circle":true}', 'build', ?, ?)
  `).bind(
    crypto.randomUUID(),
    goal_id,
    JSON.stringify({ goal_id, line: goal.line, workpiece_id: goal.workpiece_id }),
    `Goal certified — all stations complete. Auditor: ${body.auditor}`,
    body.auditor,
    body.notes ?? null,
  ).run();

  return c.json({ status: 'certified', goal_id, orbt_mode: 'OPERATE', certified_by: body.auditor });
});

// Resume goal after human-approved repair
app.post('/goals/:goal_id/resume', async (c) => {
  const { goal_id } = c.req.param();
  const goal = await c.env.D1_PRODUCTION.prepare('SELECT line, orbt_mode FROM production_goals WHERE goal_id = ?').bind(goal_id).first<{ line: string; orbt_mode: string }>();
  if (!goal) return c.json({ error: 'Not found' }, 404);
  if (goal.orbt_mode !== 'REPAIR') return c.json({ error: `Cannot resume from ${goal.orbt_mode} — must be REPAIR` }, 400);

  const agentId = c.env.LINE_AGENT.idFromName(goal.line);
  const agent = c.env.LINE_AGENT.get(agentId);

  await agent.fetch(new Request('http://internal/resume-goal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal_id }),
  }));

  return c.json({ status: 'resumed', goal_id });
});

// Fleet failures (open squawk sheet)
app.get('/errors', async (c) => {
  const result = await c.env.D1_PRODUCTION.prepare(
    "SELECT * FROM fleet_failures WHERE status = 'open' ORDER BY strike_count DESC, created_at DESC"
  ).all();
  return c.json({ errors: result.results });
});

// Sigma tracking per station
app.get('/sigma/:station_id', async (c) => {
  const { station_id } = c.req.param();
  const result = await c.env.D1_PRODUCTION.prepare(
    'SELECT * FROM production_sigma WHERE station_id = ? ORDER BY run_number DESC LIMIT 20'
  ).bind(station_id).all();
  return c.json({ sigma: result.results });
});

// Agent WebSocket routing + Hono fallback
export default {
  async fetch(request: Request, env: Env) {
    const agentResponse = await routeAgentRequest(request, env);
    if (agentResponse) return agentResponse;
    return app.fetch(request, env);
  },
};

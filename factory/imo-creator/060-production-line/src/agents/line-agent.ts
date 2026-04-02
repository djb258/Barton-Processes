// ═══════════════════════════════════════════════════════════════
// Line Agent — Dependency-aware production line state machine
// ═══════════════════════════════════════════════════════════════
// CTB: BRANCH — agents/
// IMO: Goal in → walk stations per dependency graph → awaiting certification out
// Does NOT self-certify. Does NOT write to logbook during BUILD.
// Writes execution trace (§11) and fleet failures (§13) only.

import { Agent } from 'agents';
import type { Env, LineAgentState, AdapterResponse, Step } from '../types';
import { getLine } from '../lines';
import { callHttpStation } from '../adapters/http';
import { callCliStation } from '../adapters/cli';
import { callSqlStation } from '../adapters/sql';
import { callManualStation } from '../adapters/manual';
import { writeTraceEntry, traceFromAdapterResponse } from '../lib/trace';
import { recordFleetFailure } from '../lib/fleet-failures';
import { stampGoalHEIR } from '../lib/heir';
import { shouldEscalate } from '../lib/orbt';

export class LineAgent extends Agent<Env, LineAgentState> {
  initialState: LineAgentState = {
    active_goal_id: null,
    line: null,
    status: 'idle',
    last_station_completed: null,
    last_error: null,
    goals_completed: 0,
    goals_failed: 0,
    updated_at: new Date().toISOString(),
  };

  // ── Handle internal HTTP requests from orchestrator ────────

  async onRequest(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/run-goal' && request.method === 'POST') {
      const body = await request.json() as {
        workpiece_id: string;
        workpiece_name: string;
        line: string;
        source: string;
        inbox_task_id?: string;
      };
      const goal_id = await this.runGoal(body.workpiece_id, body.workpiece_name, body.line, body.source, body.inbox_task_id);
      return new Response(JSON.stringify({ goal_id }), { headers: { 'Content-Type': 'application/json' } });
    }

    if (url.pathname === '/resume-goal' && request.method === 'POST') {
      const body = await request.json() as { goal_id: string };
      await this.resumeGoal(body.goal_id);
      return new Response(JSON.stringify({ status: 'resumed' }), { headers: { 'Content-Type': 'application/json' } });
    }

    if (url.pathname === '/status') {
      return new Response(JSON.stringify(this.state), { headers: { 'Content-Type': 'application/json' } });
    }

    return new Response('Not found', { status: 404 });
  }

  // ── Run a goal through the line ──────────────────────────────

  async runGoal(workpiece_id: string, workpiece_name: string, line: string, source: string, inbox_task_id?: string): Promise<string> {
    const lineDef = getLine(line);
    if (!lineDef) throw new Error(`Unknown line: ${line}`);
    const db = this.env.D1_PRODUCTION;

    const heir = stampGoalHEIR(workpiece_id, workpiece_name, line, source, inbox_task_id);
    const run_id = crypto.randomUUID();

    // Insert goal
    await db.prepare(`
      INSERT INTO production_goals (goal_id, sovereign_ref, hub_id, cc_layer, line, phase, workpiece_id, workpiece_name, ctb_placement, orbt_mode, source, inbox_task_id)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'BUILD', ?, ?)
    `).bind(
      heir.goal_id, heir.sovereign_ref, heir.hub_id, heir.cc_layer,
      heir.line, heir.phase, heir.workpiece_id, heir.workpiece_name,
      heir.ctb_placement, heir.source, heir.inbox_task_id,
    ).run();

    // Create all steps from line definition
    for (const station of lineDef.stations) {
      await db.prepare(`
        INSERT INTO production_steps (step_id, goal_id, station_id, sequence, depends_on, adapter_type, adapter_target, conditional, condition_desc, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        crypto.randomUUID(),
        heir.goal_id,
        station.id,
        station.depends_on.length === 0 ? 0 : lineDef.stations.findIndex(s => s.id === station.id),
        JSON.stringify(station.depends_on),
        station.adapter_type,
        station.endpoint ? `${station.adapter_target}${station.endpoint}` : station.adapter_target,
        station.conditional ? 1 : 0,
        station.condition ?? null,
        station.depends_on.length === 0 ? 'pending' : 'blocked',
      ).run();
    }

    // Write trace for goal creation
    await writeTraceEntry(db, {
      run_id,
      goal_id: heir.goal_id,
      step_description: `Goal created: ${workpiece_name} on ${line} line (${lineDef.stations.length} stations)`,
      status: 'done',
      signed_by: `${line}-agent`,
    });

    this.setState({
      ...this.state,
      active_goal_id: heir.goal_id,
      line,
      status: 'running',
      updated_at: new Date().toISOString(),
    });

    this.broadcast(JSON.stringify({
      type: 'goal_created',
      goal_id: heir.goal_id,
      line,
      workpiece_name,
      total_stations: lineDef.stations.length,
    }));

    // Start executing
    await this.executeReadyStations(heir.goal_id, run_id);
    return heir.goal_id;
  }

  // ── Execute all stations whose dependencies are met ──────────

  async executeReadyStations(goal_id: string, run_id: string): Promise<void> {
    const db = this.env.D1_PRODUCTION;

    // Get all steps for this goal
    const allSteps = await db.prepare(
      'SELECT * FROM production_steps WHERE goal_id = ? ORDER BY sequence'
    ).bind(goal_id).all<Step>();

    const steps = allSteps.results;
    const doneIds = new Set(steps.filter(s => s.status === 'done').map(s => s.station_id));

    // Find steps that are pending/blocked and whose deps are all done
    const ready: Step[] = [];
    for (const step of steps) {
      if (step.status !== 'pending' && step.status !== 'blocked') continue;

      const deps = JSON.parse(step.depends_on) as string[];
      const allDepsMet = deps.every(dep => doneIds.has(dep));
      if (allDepsMet) {
        ready.push(step);
      }
    }

    if (ready.length === 0) {
      // Check if all steps are done or not-callable
      const remaining = steps.filter(s => s.status === 'pending' || s.status === 'blocked' || s.status === 'running');
      if (remaining.length === 0) {
        await this.goalReady(goal_id, run_id);
      }
      return;
    }

    // Execute ready stations (could be parallel — 300 and 400 after seed)
    for (const step of ready) {
      await this.executeStep(goal_id, run_id, step, steps);
    }

    // After all ready steps complete, recheck for newly unblocked
    await this.executeReadyStations(goal_id, run_id);
  }

  // ── Execute a single step ────────────────────────────────────

  async executeStep(goal_id: string, run_id: string, step: Step, allSteps: Step[]): Promise<void> {
    const db = this.env.D1_PRODUCTION;

    // Mark running
    await db.prepare(
      "UPDATE production_steps SET status = 'running', started_at = datetime('now') WHERE step_id = ?"
    ).bind(step.step_id).run();

    const goal = await db.prepare('SELECT * FROM production_goals WHERE goal_id = ?').bind(goal_id).first<any>();

    // Build prior outputs from completed deps
    const prior_outputs: Record<string, unknown> = {};
    for (const s of allSteps) {
      if (s.status === 'done' && s.result) {
        try { prior_outputs[s.station_id] = JSON.parse(s.result); } catch {}
      }
    }

    const adapterRequest = {
      goal_id,
      workpiece_id: goal.workpiece_id,
      sequence: step.sequence,
      prior_outputs,
      context: {
        company_name: goal.workpiece_name || goal.workpiece_id,
        line: goal.line,
        phase: goal.phase || 'unknown',
      },
    };

    this.broadcast(JSON.stringify({
      type: 'step_started',
      goal_id,
      step_id: step.step_id,
      station_id: step.station_id,
    }));

    // Call the appropriate adapter
    let response: AdapterResponse;
    switch (step.adapter_type) {
      case 'http': {
        const parts = step.adapter_target.split('/run');
        response = await callHttpStation(step.adapter_target, undefined, adapterRequest);
        break;
      }
      case 'cli':
        response = await callCliStation(step.adapter_target, step.station_id, adapterRequest);
        break;
      case 'sql':
        response = await callSqlStation(step.adapter_target, step.station_id, adapterRequest, db);
        break;
      case 'manual':
        response = await callManualStation(step.station_id, adapterRequest);
        break;
      default:
        response = await callManualStation(step.station_id, adapterRequest);
    }

    // Write trace
    await writeTraceEntry(db, traceFromAdapterResponse(run_id, goal_id, step.step_id, step.station_id, response, `${goal.line}-agent`));

    if (response.success) {
      await this.handleSuccess(goal_id, step, response);
    } else if (response.error?.code === 'NOT_CALLABLE') {
      // Manual station — mark as not-callable but don't halt the line
      await db.prepare(
        "UPDATE production_steps SET status = 'not-callable', error_code = ?, error_message = ?, completed_at = datetime('now') WHERE step_id = ?"
      ).bind(response.error.code, response.error.message, step.step_id).run();
    } else {
      await this.handleFailure(goal_id, step, response);
    }
  }

  // ── Station succeeded ────────────────────────────────────────

  private async handleSuccess(goal_id: string, step: Step, response: AdapterResponse): Promise<void> {
    const db = this.env.D1_PRODUCTION;

    await db.prepare(`
      UPDATE production_steps
      SET status = 'done', result = ?, duration_ms = ?, cost_cents = ?, tools_used = ?, transport = ?, completed_at = datetime('now')
      WHERE step_id = ?
    `).bind(
      JSON.stringify(response.result),
      response.metrics.duration_ms,
      response.metrics.cost_cents,
      JSON.stringify(response.metrics.tools_used),
      response.metrics.transport,
      step.step_id,
    ).run();

    // Record sigma
    await db.prepare(`
      INSERT INTO production_sigma (sigma_id, station_id, line, metric, value, run_number)
      VALUES (?, ?, ?, 'duration_ms', ?, (SELECT COALESCE(MAX(run_number), 0) + 1 FROM production_sigma WHERE station_id = ? AND metric = 'duration_ms'))
    `).bind(crypto.randomUUID(), step.station_id, this.state.line || 'unknown', response.metrics.duration_ms, step.station_id).run();

    this.setState({
      ...this.state,
      last_station_completed: step.station_id,
      updated_at: new Date().toISOString(),
    });

    this.broadcast(JSON.stringify({
      type: 'step_completed',
      goal_id,
      station_id: step.station_id,
      duration_ms: response.metrics.duration_ms,
    }));
  }

  // ── Station failed ───────────────────────────────────────────

  private async handleFailure(goal_id: string, step: Step, response: AdapterResponse): Promise<void> {
    const db = this.env.D1_PRODUCTION;
    const error = response.error!;

    await db.prepare(`
      UPDATE production_steps
      SET status = 'failed', error_code = ?, error_message = ?, retryable = ?, duration_ms = ?, transport = ?, completed_at = datetime('now')
      WHERE step_id = ?
    `).bind(error.code, error.message, error.retryable ? 1 : 0, response.metrics.duration_ms, response.metrics.transport, step.step_id).run();

    // Fleet failure registry — keyed by station + error code
    const fleet = await recordFleetFailure(db, step.station_id, error.code, goal_id);

    // Update goal ORBT
    const newOrbt = fleet.escalated ? 'TROUBLESHOOT_TRAIN' : 'REPAIR';
    await db.prepare(
      "UPDATE production_goals SET orbt_mode = ?, strike_count = strike_count + 1, updated_at = datetime('now') WHERE goal_id = ?"
    ).bind(newOrbt, goal_id).run();

    this.setState({
      ...this.state,
      status: 'halted',
      last_error: `${step.station_id}: ${error.message}`,
      goals_failed: this.state.goals_failed + (fleet.escalated ? 0 : 1),
      updated_at: new Date().toISOString(),
    });

    this.broadcast(JSON.stringify({
      type: 'step_failed',
      goal_id,
      station_id: step.station_id,
      error_code: error.code,
      error_message: error.message,
      fleet_strike_count: fleet.strike_count,
      escalated: fleet.escalated,
      orbt_mode: newOrbt,
    }));
  }

  // ── All stations complete — awaiting certification ───────────

  private async goalReady(goal_id: string, run_id: string): Promise<void> {
    const db = this.env.D1_PRODUCTION;

    // Do NOT set OPERATE — builder cannot certify
    await db.prepare(
      "UPDATE production_goals SET completed_at = datetime('now'), updated_at = datetime('now') WHERE goal_id = ?"
    ).bind(goal_id).run();

    await writeTraceEntry(db, {
      run_id,
      goal_id,
      step_description: 'All callable stations complete. Awaiting auditor certification.',
      status: 'done',
      signed_by: `${this.state.line}-agent`,
    });

    this.setState({
      ...this.state,
      active_goal_id: null,
      status: 'awaiting_certification',
      goals_completed: this.state.goals_completed + 1,
      updated_at: new Date().toISOString(),
    });

    this.broadcast(JSON.stringify({
      type: 'goal_awaiting_certification',
      goal_id,
      line: this.state.line,
    }));
  }

  // ── Resume after mechanic fix (human-approved) ───────────────

  async resumeGoal(goal_id: string): Promise<void> {
    const db = this.env.D1_PRODUCTION;

    await db.prepare(
      "UPDATE production_steps SET status = 'pending', retry_count = retry_count + 1, error_code = NULL, error_message = NULL WHERE goal_id = ? AND status = 'failed'"
    ).bind(goal_id).run();

    await db.prepare(
      "UPDATE production_goals SET orbt_mode = 'BUILD', updated_at = datetime('now') WHERE goal_id = ?"
    ).bind(goal_id).run();

    this.setState({
      ...this.state,
      active_goal_id: goal_id,
      status: 'running',
      last_error: null,
      updated_at: new Date().toISOString(),
    });

    const run_id = crypto.randomUUID();
    await this.executeReadyStations(goal_id, run_id);
  }
}

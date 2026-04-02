// ═══════════════════════════════════════════════════════════════
// Orchestrator Agent — The Hub
// ═══════════════════════════════════════════════════════════════
// Routes goals to the correct line agent. Does NOT run stations.
// Hub-spoke: this is the hub. Line agents are spokes.

import { Agent } from 'agents';
import type { Env } from '../types';
import { getLine, getAllLines } from '../lines';

interface OrchestratorState {
  active_goals: number;
  total_dispatched: number;
  updated_at: string;
}

export class OrchestratorAgent extends Agent<Env, OrchestratorState> {
  initialState: OrchestratorState = {
    active_goals: 0,
    total_dispatched: 0,
    updated_at: new Date().toISOString(),
  };

  async onRequest(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/dispatch' && request.method === 'POST') {
      const body = await request.json() as {
        line: string;
        workpiece_id: string;
        workpiece_name?: string;
        source?: string;
        inbox_task_id?: string;
      };

      if (!body.line || !body.workpiece_id) {
        return new Response(JSON.stringify({ error: 'line and workpiece_id required' }), { status: 400 });
      }

      const lineDef = getLine(body.line);
      if (!lineDef) {
        return new Response(JSON.stringify({ error: `Unknown line: ${body.line}. Available: ${getAllLines().join(', ')}` }), { status: 400 });
      }

      // Get or create the line agent for this line
      const agentId = this.env.LINE_AGENT.idFromName(body.line);
      const agent = this.env.LINE_AGENT.get(agentId);

      const res = await agent.fetch(new Request('http://internal/run-goal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workpiece_id: body.workpiece_id,
          workpiece_name: body.workpiece_name || body.workpiece_id,
          line: body.line,
          source: body.source || 'manual',
          inbox_task_id: body.inbox_task_id,
        }),
      }));

      const result = await res.json();

      this.setState({
        active_goals: this.state.active_goals + 1,
        total_dispatched: this.state.total_dispatched + 1,
        updated_at: new Date().toISOString(),
      });

      return new Response(JSON.stringify(result), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (url.pathname === '/status') {
      return new Response(JSON.stringify({
        ...this.state,
        available_lines: getAllLines(),
      }), { headers: { 'Content-Type': 'application/json' } });
    }

    return new Response('Not found', { status: 404 });
  }
}

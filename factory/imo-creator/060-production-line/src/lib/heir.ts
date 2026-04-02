// HEIR Stamper — stamps identity on goal creation. Never changes after.
import { getLine } from '../lines';

export function stampGoalHEIR(
  workpiece_id: string,
  workpiece_name: string | null,
  line: string,
  source: string,
  inbox_task_id?: string,
) {
  const lineDef = getLine(line);
  if (!lineDef) throw new Error(`Unknown line: ${line}`);

  return {
    goal_id: crypto.randomUUID(),
    sovereign_ref: 'imo-creator',
    hub_id: 'production-line',
    cc_layer: 'CC-03',
    line,
    phase: lineDef.phases[0],
    workpiece_id,
    workpiece_name,
    ctb_placement: 'leaf',
    total_stations: lineDef.stations.length,
    source,
    inbox_task_id: inbox_task_id ?? null,
  };
}

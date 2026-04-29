// Fleet Failure Registry — §13 fleet-level strike tracking
// Keyed by station + error_code. Strike 3 = TROUBLESHOOT_TRAIN.

export async function recordFleetFailure(
  db: D1Database,
  station_id: string,
  error_code: string,
  goal_id: string,
): Promise<{ strike_count: number; escalated: boolean }> {
  // Check if this pattern already exists
  const existing = await db.prepare(
    'SELECT pattern_id, occurrences, goals_affected, strike_count FROM fleet_failures WHERE station_id = ? AND error_code = ?'
  ).bind(station_id, error_code).first<{
    pattern_id: string;
    occurrences: number;
    goals_affected: string;
    strike_count: number;
  }>();

  if (existing) {
    const goals = JSON.parse(existing.goals_affected) as string[];
    if (!goals.includes(goal_id)) {
      goals.push(goal_id);
    }
    const newStrike = existing.strike_count + 1;
    const newStatus = newStrike >= 3 ? 'ad_issued' : 'open';

    await db.prepare(`
      UPDATE fleet_failures
      SET occurrences = occurrences + 1, goals_affected = ?, strike_count = ?, status = ?
      WHERE pattern_id = ?
    `).bind(JSON.stringify(goals), newStrike, newStatus, existing.pattern_id).run();

    return { strike_count: newStrike, escalated: newStrike >= 3 };
  }

  // New pattern
  await db.prepare(`
    INSERT INTO fleet_failures (pattern_id, station_id, error_code, error_pattern, goals_affected, strike_count, status)
    VALUES (?, ?, ?, ?, ?, 1, 'open')
  `).bind(
    crypto.randomUUID(),
    station_id,
    error_code,
    `${station_id}:${error_code}`,
    JSON.stringify([goal_id]),
  ).run();

  return { strike_count: 1, escalated: false };
}

export async function getOpenFailures(db: D1Database): Promise<unknown[]> {
  const result = await db.prepare(
    "SELECT * FROM fleet_failures WHERE status = 'open' ORDER BY strike_count DESC"
  ).all();
  return result.results;
}

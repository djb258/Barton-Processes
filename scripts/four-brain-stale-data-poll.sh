#!/usr/bin/env bash
# four-brain-stale-data-poll.sh
# Cron: "0 14 * * 1" (Mondays at 14:00 UTC)
# Polls four_brain_run for stale in-flight runs (started > 7 days ago, verdict IS NULL)
# and emits a warning row to stderr. Pure read — no mutations.
# Always exits 0 so cron doesn't alarm on stale data.

set -uo pipefail

WRANGLER_D1_DB="${WRANGLER_D1_DB:-mission-control}"
STALE_DAYS="${STALE_DAYS:-7}"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "WARN: wrangler not found — four-brain-stale-data-poll skipped" >&2
  exit 0
fi

SQL="SELECT run_id, bar_id, runtime_state, strikes, started_at
     FROM four_brain_run
     WHERE verdict IS NULL
       AND datetime(started_at) < datetime('now', '-${STALE_DAYS} days')
     ORDER BY started_at ASC;"

OUTPUT="$(wrangler d1 execute "$WRANGLER_D1_DB" --command "$SQL" 2>&1)" || {
  echo "WARN: D1 query failed — four-brain-stale-data-poll: ${OUTPUT}" >&2
  exit 0
}

echo "$OUTPUT" >&2

STALE_COUNT="$(echo "$OUTPUT" | grep -c '"run_id"' 2>/dev/null || true)"

if [[ "$STALE_COUNT" -gt 0 ]]; then
  echo "WARN: four-brain-stale-data-poll found ${STALE_COUNT} stale run(s) with no verdict after ${STALE_DAYS} days." >&2
else
  echo "INFO: four-brain-stale-data-poll: no stale runs found." >&2
fi

exit 0

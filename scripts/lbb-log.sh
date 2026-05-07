#!/usr/bin/env bash
set -euo pipefail

LBB_INGEST_URL="${LBB_INGEST_URL:-https://lbb.svg-outreach.workers.dev/ingest}"
LBB_DOPPLER_PROJECT="${LBB_DOPPLER_PROJECT:-imo-creator}"
LBB_DOPPLER_CONFIG="${LBB_DOPPLER_CONFIG:-dev}"
WRANGLER_D1_DB="${WRANGLER_D1_DB:-mission-control}"

usage() {
  cat >&2 <<'EOF'
Usage: scripts/lbb-log.sh --role planner|foreman|mechanic|auditor --action ACTION --subject SUBJECT --evidence PATH [options]

Purpose:
  Process 070 transition logger. Writes an LBB knowledge record to /ingest.
  When --bar-id is provided, also dual-writes a row to the four_brain_transition
  D1 table (mission-control-api D1 binding).

Required:
  --role      planner | foreman | mechanic | auditor
  --action    transition action, e.g. dispatch, handoff, edit, audit-verdict
  --subject   LBB subject_id, e.g. system or processes
  --evidence  file or directory path used as evidence

Optional:
  --bar-id          BAR identifier (enables D1 dual-write to four_brain_transition)
  --run-id          four_brain_run.run_id (defaults to --bar-id if omitted)
  --atlas-sections  comma-separated Atlas sections consulted, e.g. "§1,§4.5"
  --notes           freeform notes string
  --dry-run         print payload without posting or writing D1

Environment:
  LBB_API_KEY required unless --dry-run. Falls back to Doppler if available.
  WRANGLER_D1_DB   D1 database name for dual-write (default: mission-control)
EOF
  exit 1
}

BAR_ID=""
RUN_ID=""
ROLE=""
ACTION=""
SUBJECT_ID=""
EVIDENCE=""
ATLAS_SECTIONS=""
NOTES=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bar-id)         BAR_ID="${2:-}";         shift 2 ;;
    --run-id)         RUN_ID="${2:-}";         shift 2 ;;
    --role)           ROLE="${2:-}";           shift 2 ;;
    --action)         ACTION="${2:-}";         shift 2 ;;
    --subject|--subject-id) SUBJECT_ID="${2:-}"; shift 2 ;;
    --evidence)       EVIDENCE="${2:-}";       shift 2 ;;
    --atlas-sections) ATLAS_SECTIONS="${2:-}"; shift 2 ;;
    --notes)          NOTES="${2:-}";          shift 2 ;;
    --dry-run)        DRY_RUN=true;            shift ;;
    -h|--help)        usage ;;
    *) echo "ERROR: Unknown flag: $1" >&2; usage ;;
  esac
done

missing=()
[[ -z "$ROLE" ]]       && missing+=("--role")
[[ -z "$ACTION" ]]     && missing+=("--action")
[[ -z "$SUBJECT_ID" ]] && missing+=("--subject")
[[ -z "$EVIDENCE" ]]   && missing+=("--evidence")
if [[ ${#missing[@]} -gt 0 ]]; then
  echo "ERROR: Missing required flags: ${missing[*]}" >&2
  usage
fi

case "$ROLE" in
  planner|foreman|mechanic|auditor) ;;
  *) echo "ERROR: --role must be planner, foreman, mechanic, or auditor" >&2; exit 2 ;;
esac

if [[ ! -e "$EVIDENCE" ]]; then
  echo "ERROR: evidence path does not exist: $EVIDENCE" >&2
  exit 2
fi

# Default run_id to bar_id when only bar_id is provided
[[ -n "$BAR_ID" && -z "$RUN_ID" ]] && RUN_ID="$BAR_ID"

if [[ "$DRY_RUN" != "true" && -z "${LBB_API_KEY:-}" ]]; then
  if command -v doppler >/dev/null 2>&1; then
    LBB_API_KEY="$(doppler secrets get LBB_API_KEY --project "$LBB_DOPPLER_PROJECT" --config "$LBB_DOPPLER_CONFIG" --plain | tr -d '\r\n')"
    export LBB_API_KEY
  elif command -v powershell.exe >/dev/null 2>&1; then
    LBB_API_KEY="$(powershell.exe -NoProfile -Command "[Console]::Out.Write((doppler secrets get LBB_API_KEY --project $LBB_DOPPLER_PROJECT --config $LBB_DOPPLER_CONFIG --plain).Trim())" | tr -d '\r\n')"
    export LBB_API_KEY
  fi
fi

if [[ "$DRY_RUN" != "true" && -z "${LBB_API_KEY:-}" ]]; then
  echo "ERROR: LBB_API_KEY environment variable is not set and Doppler fallback failed." >&2
  exit 1
fi

PYTHON_CMD=()
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=(python3)
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=(py -3 2>/dev/null || python)
elif command -v py >/dev/null 2>&1; then
  PYTHON_CMD=(py -3)
else
  echo "ERROR: Python 3 is required for JSON payload generation." >&2
  exit 1
fi

# ── LBB write (primary) ────────────────────────────────────────────────────

LBB_OUTPUT="$("${PYTHON_CMD[@]}" - "$BAR_ID" "$RUN_ID" "$ROLE" "$ACTION" "$SUBJECT_ID" "$EVIDENCE" "$DRY_RUN" "$LBB_INGEST_URL" "$ATLAS_SECTIONS" "$NOTES" <<'PY'
import hashlib
import json
import os
import sys
import uuid
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

bar_id, run_id, role, action, subject_id, evidence, dry_run, ingest_url, atlas_sections, notes = sys.argv[1:11]
evidence_path = Path(evidence)

def evidence_hash(path: Path) -> str:
    h = hashlib.sha256()
    if path.is_file():
        h.update(path.read_bytes())
        return h.hexdigest()
    files = sorted(p for p in path.rglob("*") if p.is_file())
    for file_path in files:
        rel = file_path.relative_to(path).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(hashlib.sha256(file_path.read_bytes()).hexdigest().encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()

digest = evidence_hash(evidence_path)
timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
transition_id = str(uuid.uuid4())

bar_label = bar_id if bar_id else "no-bar"
title = f"{bar_label} Process 070 {role} {action} transition"

content_lines = [
    f"BAR: {bar_label}",
    f"Role: {role}",
    f"Action: {action}",
    f"Subject: {subject_id}",
    f"Evidence: {evidence_path}",
    f"Evidence SHA256: {digest}",
    f"Timestamp: {timestamp}",
]
if atlas_sections:
    content_lines.append(f"Atlas Sections: {atlas_sections}")
if notes:
    content_lines.append(f"Notes: {notes}")
content_lines += [
    "",
    "Process 070 Four-Brain Step N transition record.",
    "This record was emitted by Barton-Processes/scripts/lbb-log.sh.",
]

tags = ["process-070", "four-brain", "lbb-transition", role, action]
if bar_id:
    tags.append(f"bar-{bar_id.lower()}")
    tags.append("mission-control-wiring")

payload = {
    "subject_id": subject_id,
    "title": title,
    "content": "\n".join(content_lines),
    "tags": tags,
    "source": "barton-processes/scripts/lbb-log.sh",
    "source_path": str(evidence_path),
    "sovereign_ref": "imo-creator",
    "hub_id": "process-070-four-brain-garage",
    "ctb_placement": "barton-processes/factory/imo-creator/070-four-brain/garage",
    "cc_layer": "CC-02",
    "orbt_mode": "OPERATE",
    "bar_id": bar_id or None,
    "run_id": run_id or None,
    "role": role,
    "action": action,
    "evidence_hash": digest,
    "timestamp": timestamp,
    "atlas_sections_consulted": atlas_sections or None,
    "notes": notes or None,
}

if dry_run == "true":
    print(json.dumps({
        "dry_run": True,
        "transition_id": transition_id,
        "payload": payload,
    }, indent=2))
    sys.exit(0)

api_key = os.environ.get("LBB_API_KEY")
request = urllib.request.Request(
    ingest_url,
    data=json.dumps(payload).encode("utf-8"),
    method="POST",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "barton-processes-lbb-log/1.0",
    },
)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
        resp_data = json.loads(body) if body.startswith("{") else {"raw": body}
        lbb_record_id = resp_data.get("id") or resp_data.get("record_id") or ""
        print(json.dumps({
            "status": response.status,
            "action": "lbb_ingest",
            "bar_id": bar_id or None,
            "run_id": run_id or None,
            "role": role,
            "transition_action": action,
            "evidence_hash": digest,
            "timestamp": timestamp,
            "transition_id": transition_id,
            "lbb_record_id": lbb_record_id,
            "response": resp_data,
        }, indent=2))
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    print(json.dumps({"status": exc.code, "error": body}, indent=2), file=sys.stderr)
    sys.exit(1)
PY
)"

echo "$LBB_OUTPUT"

# ── D1 dual-write (BAR-only) ───────────────────────────────────────────────
# Only fires when --bar-id is provided and wrangler is installed.
# Non-BAR callers (no --bar-id) skip this block entirely — backward-compat preserved.

if [[ -n "$BAR_ID" && "$DRY_RUN" != "true" ]]; then
  if ! command -v wrangler >/dev/null 2>&1; then
    echo "WARN: wrangler not found — skipping D1 four_brain_transition dual-write" >&2
  else
    # Extract fields from LBB output
    TRANSITION_ID="$("${PYTHON_CMD[@]}" -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('transition_id',''))" <<< "$LBB_OUTPUT")"
    LBB_RECORD_ID="$("${PYTHON_CMD[@]}" -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('lbb_record_id',''))" <<< "$LBB_OUTPUT")"
    EVIDENCE_HASH="$("${PYTHON_CMD[@]}" -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('evidence_hash',''))" <<< "$LBB_OUTPUT")"
    TIMESTAMP="$("${PYTHON_CMD[@]}" -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('timestamp',''))" <<< "$LBB_OUTPUT")"

    # Escape single-quoted strings for SQL
    escape_sql() { printf "%s" "${1//\'/\'\'}"; }

    SQL="INSERT INTO four_brain_transition
      (transition_id, run_id, role, action, atlas_sections_consulted, evidence_hash, timestamp, lbb_record_id, gate_verdicts, notes)
      VALUES
      ('$(escape_sql "$TRANSITION_ID")',
       '$(escape_sql "$RUN_ID")',
       '$(escape_sql "$ROLE")',
       '$(escape_sql "$ACTION")',
       $([ -n "$ATLAS_SECTIONS" ] && printf "'%s'" "$(escape_sql "$ATLAS_SECTIONS")" || printf "NULL"),
       $([ -n "$EVIDENCE_HASH" ] && printf "'%s'" "$(escape_sql "$EVIDENCE_HASH")" || printf "NULL"),
       '$(escape_sql "$TIMESTAMP")',
       $([ -n "$LBB_RECORD_ID" ] && printf "'%s'" "$(escape_sql "$LBB_RECORD_ID")" || printf "NULL"),
       NULL,
       $([ -n "$NOTES" ] && printf "'%s'" "$(escape_sql "$NOTES")" || printf "NULL")
      )
      ON CONFLICT(transition_id) DO NOTHING;"

    if wrangler d1 execute "$WRANGLER_D1_DB" --command "$SQL" >/dev/null 2>&1; then
      echo "D1 four_brain_transition row written: transition_id=${TRANSITION_ID}" >&2
    else
      echo "WARN: D1 dual-write failed (non-fatal) — transition_id=${TRANSITION_ID}" >&2
    fi
  fi
fi

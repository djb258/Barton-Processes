#!/usr/bin/env bash
set -euo pipefail

LBB_INGEST_URL="${LBB_INGEST_URL:-https://lbb.svg-outreach.workers.dev/ingest}"
LBB_DOPPLER_PROJECT="${LBB_DOPPLER_PROJECT:-imo-creator}"
LBB_DOPPLER_CONFIG="${LBB_DOPPLER_CONFIG:-dev}"

usage() {
  cat >&2 <<'EOF'
Usage: scripts/lbb-log.sh --bar-id BAR-070 --role planner|foreman|mechanic|auditor --action ACTION --subject SUBJECT --evidence PATH [--dry-run]

Purpose:
  Process 070 transition logger. Accepts the garage runner's compact Step N
  flags and writes a standard LBB knowledge record to /ingest.

Required:
  --bar-id    BAR identifier
  --role      planner | foreman | mechanic | auditor
  --action    transition action, e.g. dispatch, handoff, edit, audit-verdict
  --subject   LBB subject_id, e.g. system or processes
  --evidence  file or directory path used as evidence

Optional:
  --dry-run   print payload without posting

Environment:
  LBB_API_KEY required unless --dry-run. If missing and Doppler is installed,
  the script fetches LBB_API_KEY from imo-creator/dev without printing it.
EOF
  exit 1
}

BAR_ID=""
ROLE=""
ACTION=""
SUBJECT_ID=""
EVIDENCE=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bar-id) BAR_ID="${2:-}"; shift 2 ;;
    --role) ROLE="${2:-}"; shift 2 ;;
    --action) ACTION="${2:-}"; shift 2 ;;
    --subject|--subject-id) SUBJECT_ID="${2:-}"; shift 2 ;;
    --evidence) EVIDENCE="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage ;;
    *) echo "ERROR: Unknown flag: $1" >&2; usage ;;
  esac
done

missing=()
[[ -z "$BAR_ID" ]] && missing+=("--bar-id")
[[ -z "$ROLE" ]] && missing+=("--role")
[[ -z "$ACTION" ]] && missing+=("--action")
[[ -z "$SUBJECT_ID" ]] && missing+=("--subject")
[[ -z "$EVIDENCE" ]] && missing+=("--evidence")
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
  PYTHON_CMD=(python)
elif command -v py >/dev/null 2>&1; then
  PYTHON_CMD=(py -3)
else
  echo "ERROR: Python 3 is required for JSON payload generation." >&2
  exit 1
fi

"${PYTHON_CMD[@]}" - "$BAR_ID" "$ROLE" "$ACTION" "$SUBJECT_ID" "$EVIDENCE" "$DRY_RUN" "$LBB_INGEST_URL" <<'PY'
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

bar_id, role, action, subject_id, evidence, dry_run, ingest_url = sys.argv[1:8]
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
title = f"{bar_id} Process 070 {role} {action} transition"
content = "\n".join([
    f"BAR: {bar_id}",
    f"Role: {role}",
    f"Action: {action}",
    f"Subject: {subject_id}",
    f"Evidence: {evidence_path}",
    f"Evidence SHA256: {digest}",
    f"Timestamp: {timestamp}",
    "",
    "Process 070 Four-Brain Step N transition record.",
    "This record was emitted by Barton-Processes/scripts/lbb-log.sh.",
])

payload = {
    "subject_id": subject_id,
    "title": title,
    "content": content,
    "tags": ["process-070", "four-brain", "lbb-transition", role, action],
    "source": "barton-processes/scripts/lbb-log.sh",
    "source_path": str(evidence_path),
    "sovereign_ref": "imo-creator",
    "hub_id": "process-070-four-brain-garage",
    "ctb_placement": "barton-processes/factory/imo-creator/070-four-brain/garage",
    "cc_layer": "CC-02",
    "orbt_mode": "OPERATE",
    "bar_id": bar_id,
    "role": role,
    "action": action,
    "evidence_hash": digest,
    "timestamp": timestamp,
}

if dry_run == "true":
    print(json.dumps({"dry_run": True, "payload": payload}, indent=2))
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
        print(json.dumps({
            "status": response.status,
            "action": "lbb_ingest",
            "bar_id": bar_id,
            "role": role,
            "transition_action": action,
            "evidence_hash": digest,
            "response": json.loads(body) if body.startswith("{") else body,
        }, indent=2))
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    print(json.dumps({"status": exc.code, "error": body}, indent=2), file=sys.stderr)
    sys.exit(1)
PY

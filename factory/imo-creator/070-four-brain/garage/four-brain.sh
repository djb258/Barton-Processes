#!/usr/bin/env bash
#
# four-brain.sh — inbox-to-inbox helpers for the Process 070 four-brain pipeline.
#
# Architecture: each agent has an inbox folder. Packets are dropped between
# inboxes. D1 (mission-control.four_brain_transition via /four-brain/log) is
# the audit log only — filesystem is the queue.
#
# Commands:
#   drop  <to_role> <packet.md> <packet.yaml>
#       Copy the packet pair into <to_role>'s inbox + log a "drop" row.
#
#   claim <role> <packet-basename>
#       Move the packet pair out of <role>'s inbox into a working location
#       at agents/<role>/working/<packet-basename>{.md,.yaml} + log a "claim" row.
#
#   reject <role> <packet-basename> <reason>
#       Move the packet pair into agents/<role>/rejected/ + log a "reject" row.
#
#   log <bar_id> <role> <action> [notes]
#       Direct log row writer. Use for transitions that don't move files.
#
#   list <role>
#       Show what's in <role>'s inbox.
#
# Roles: planner | foreman | mechanic | auditor (also accepted: system)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$SCRIPT_DIR/agents"
WORKER_URL="${MC_WORKER_URL:-https://mission-control-api.svg-outreach.workers.dev}"

# Secrets: prefer env, fall back to Doppler.
if [[ -z "${MC_API_KEY:-}" ]]; then
  MC_API_KEY="$(doppler secrets get MC_API_KEY --plain --project imo-creator --config dev 2>/dev/null || true)"
fi
if [[ -z "${LBB_API_KEY:-}" ]]; then
  LBB_API_KEY="$(doppler secrets get LBB_API_KEY --plain --project imo-creator --config dev 2>/dev/null || true)"
fi
LBB_URL="${LBB_URL:-https://lbb.svg-outreach.workers.dev}"

VALID_ROLES="planner foreman mechanic auditor system"

usage() {
  sed -n '3,21p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 2
}

require_role() {
  local role="$1"
  for valid in $VALID_ROLES; do
    [[ "$role" == "$valid" ]] && return 0
  done
  echo "ERROR: role '$role' not in: $VALID_ROLES" >&2
  exit 1
}

inbox_dir() {
  local role="$1"
  echo "$AGENTS_DIR/$role/inbox"
}

working_dir() {
  local role="$1"
  echo "$AGENTS_DIR/$role/working"
}

rejected_dir() {
  local role="$1"
  echo "$AGENTS_DIR/$role/rejected"
}

post_log() {
  local bar_id="$1" role="$2" action="$3" from="${4:-}" to="${5:-}" artifact="${6:-}" notes="${7:-}"
  if [[ -z "$MC_API_KEY" ]]; then
    echo "WARN: MC_API_KEY not set; skipping D1 log row" >&2
    return 0
  fi
  local payload
  payload=$(cat <<EOF
{
  "bar_id": "$bar_id",
  "role": "$role",
  "action": "$action",
  "from_status": "$from",
  "to_status": "$to",
  "artifact_path": "$artifact",
  "notes": "$notes"
}
EOF
)
  local resp
  resp=$(curl -s -w "\n%{http_code}" -X POST "$WORKER_URL/four-brain/log" \
    -H "X-API-Key: $MC_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload")
  local http="${resp##*$'\n'}"
  local body="${resp%$'\n'*}"
  if [[ "$http" != "200" ]]; then
    echo "WARN: log POST returned $http: $body" >&2
  else
    echo "$body"
  fi
  # Mirror to LBB (subject_id='processes', per Atlas mandate). Best-effort.
  post_lbb "$bar_id" "$role" "$action" "$artifact" "$notes" || true
}

# Mirror a transition to LBB so the logbook has the durable record.
# Best-effort: failures are logged, not fatal — D1 is already the primary log.
post_lbb() {
  local bar_id="$1" role="$2" action="$3" artifact="${4:-}" notes="${5:-}"
  if [[ -z "$LBB_API_KEY" ]]; then
    return 0
  fi
  local title="four-brain ${role} ${action} ${bar_id}"
  local content="role=${role} action=${action} artifact=${artifact} notes=${notes}"
  curl -s -o /dev/null -X POST "$LBB_URL/ingest" \
    -H "Authorization: Bearer $LBB_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(cat <<EOF
{
  "subject_id": "processes",
  "title": "$title",
  "content": "$content",
  "source_type": "four-brain",
  "source_name": "four-brain.sh",
  "tags": ["four-brain","process-070","$role","$action"],
  "bar_id": "$bar_id"
}
EOF
)" || true
}

# Verify a packet's handoff_check before claiming. Returns 0 if pass, 1 if fail.
# Reads required_fields (YAML key paths) + required_artifacts (file paths).
verify_handoff() {
  local yaml="$1"
  [[ -f "$yaml" ]] || { echo "ERROR: $yaml not found" >&2; return 1; }
  if ! command -v python >/dev/null 2>&1; then
    echo "WARN: python not found; skipping handoff_check verification" >&2
    return 0
  fi
  python - "$yaml" <<'PYEOF'
import sys, os
try:
    import yaml as Y
except ImportError:
    print("WARN: PyYAML not installed; skipping handoff_check", file=sys.stderr)
    sys.exit(0)
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    pkt = Y.safe_load(f)
hc = pkt.get('handoff_check', {}) or {}
required_fields = hc.get('required_fields', []) or []
required_artifacts = hc.get('required_artifacts', []) or []
strict = hc.get('rejected_if_missing', True)
errs = []
def get(d, dotted):
    cur = d
    for part in dotted.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur
for f in required_fields:
    if get(pkt, f) in (None, '', [], {}):
        errs.append(f"missing field: {f}")
for a in required_artifacts:
    if not os.path.exists(a):
        errs.append(f"missing artifact: {a}")
if errs and strict:
    for e in errs:
        print(f"handoff_check FAIL: {e}", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
PYEOF
}

cmd_drop() {
  [[ $# -eq 3 ]] || { echo "usage: drop <to_role> <packet.md> <packet.yaml>" >&2; exit 2; }
  local to_role="$1" md="$2" yaml="$3"
  require_role "$to_role"
  [[ -f "$md" ]] || { echo "ERROR: $md not found" >&2; exit 1; }
  [[ -f "$yaml" ]] || { echo "ERROR: $yaml not found" >&2; exit 1; }
  local dest
  dest="$(inbox_dir "$to_role")"
  mkdir -p "$dest"
  cp "$md" "$dest/"
  cp "$yaml" "$dest/"
  local basename_md
  basename_md="$(basename "$md")"
  local bar_id
  bar_id="${basename_md%.md}"
  echo "dropped: $dest/$(basename "$md") + $(basename "$yaml")"
  post_log "$bar_id" "$to_role" "drop" "" "$dest" "$dest/$(basename "$yaml")" "packet dropped into $to_role inbox"
}

cmd_claim() {
  [[ $# -eq 2 ]] || { echo "usage: claim <role> <packet-basename>" >&2; exit 2; }
  local role="$1" basename="$2"
  require_role "$role"
  local src
  src="$(inbox_dir "$role")"
  local dest
  dest="$(working_dir "$role")"
  mkdir -p "$dest"
  local md_src="$src/$basename.md" yaml_src="$src/$basename.yaml"
  [[ -f "$md_src" ]] || { echo "ERROR: $md_src not in inbox" >&2; exit 1; }
  [[ -f "$yaml_src" ]] || { echo "ERROR: $yaml_src not in inbox" >&2; exit 1; }
  if ! verify_handoff "$yaml_src"; then
    local rdest
    rdest="$(rejected_dir "$role")"
    mkdir -p "$rdest"
    mv "$md_src" "$rdest/"
    mv "$yaml_src" "$rdest/"
    post_log "$basename" "$role" "reject" "$src" "$rdest" "$rdest/$basename.yaml" "handoff_check failed on claim"
    echo "rejected (handoff_check): $rdest/$basename.{md,yaml}" >&2
    exit 1
  fi
  mv "$md_src" "$dest/"
  mv "$yaml_src" "$dest/"
  echo "claimed: $dest/$basename.{md,yaml}"
  post_log "$basename" "$role" "claim" "$src" "$dest" "$dest/$basename.yaml" "$role claimed packet from inbox"
}

cmd_reject() {
  [[ $# -ge 3 ]] || { echo "usage: reject <role> <packet-basename> <reason>" >&2; exit 2; }
  local role="$1" basename="$2"; shift 2
  local reason="$*"
  require_role "$role"
  local src
  src="$(inbox_dir "$role")"
  local dest
  dest="$(rejected_dir "$role")"
  mkdir -p "$dest"
  local md_src="$src/$basename.md" yaml_src="$src/$basename.yaml"
  [[ -f "$md_src" ]] || { echo "ERROR: $md_src not in inbox" >&2; exit 1; }
  [[ -f "$yaml_src" ]] || { echo "ERROR: $yaml_src not in inbox" >&2; exit 1; }
  mv "$md_src" "$dest/"
  mv "$yaml_src" "$dest/"
  echo "rejected: $dest/$basename.{md,yaml} ($reason)"
  post_log "$basename" "$role" "reject" "$src" "$dest" "$dest/$basename.yaml" "rejected: $reason"
}

cmd_log() {
  [[ $# -ge 3 ]] || { echo "usage: log <bar_id> <role> <action> [notes]" >&2; exit 2; }
  local bar_id="$1" role="$2" action="$3"; shift 3
  local notes="${*:-}"
  require_role "$role"
  post_log "$bar_id" "$role" "$action" "" "" "" "$notes"
}

cmd_list() {
  [[ $# -eq 1 ]] || { echo "usage: list <role>" >&2; exit 2; }
  local role="$1"
  require_role "$role"
  local dir
  dir="$(inbox_dir "$role")"
  if [[ ! -d "$dir" ]]; then
    echo "(no inbox dir for $role)"
    return 0
  fi
  ls -la "$dir" | grep -v "^total" | grep -v "/\.$" | grep -v "/\.\.$" | grep -v "\.gitkeep$" || echo "(empty)"
}

main() {
  [[ $# -ge 1 ]] || usage
  local cmd="$1"; shift
  case "$cmd" in
    drop)   cmd_drop   "$@" ;;
    claim)  cmd_claim  "$@" ;;
    reject) cmd_reject "$@" ;;
    log)    cmd_log    "$@" ;;
    list)   cmd_list   "$@" ;;
    -h|--help|help) usage ;;
    *) echo "unknown command: $cmd" >&2; usage ;;
  esac
}

main "$@"

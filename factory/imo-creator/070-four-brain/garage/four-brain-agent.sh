#!/usr/bin/env bash
# Last modified: 2026-05-08 — Pass 4 Repairs 3+6: Foreman default → sonnet (H-1); terminal Auditor writes queue lifecycle transition before exit (C-2)
#
# four-brain-agent.sh — generic per-role agent runtime for Process 070.
#
# Watches a role's inbox, claims the oldest packet, invokes that role's LLM
# with the role's prompt + the packet, captures the output as a Library
# artifact, and drops the next handoff packet into the next role's inbox.
#
# This script is **role-parameterized**. Nothing about which BAR is hardcoded.
# Per-role config (model, prompt, next role) is below in agent_config.
#
# Usage:
#   four-brain-agent.sh <role> [--once] [--dry-run]
#
#   --once   process one packet then exit (default)
#   (loop mode is intentionally not built — operator runs in a loop or cron)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPERS="$SCRIPT_DIR/four-brain.sh"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
AGENTS_DIR="$SCRIPT_DIR/agents"
PLANS_ROOT="$(cd "$SCRIPT_DIR/../../../../docs/plans" 2>/dev/null && pwd || echo "")"
DRY_RUN="false"

[[ -x "$HELPERS" ]] || { echo "ERROR: $HELPERS missing or not executable" >&2; exit 1; }

# Per-role configuration. Keep this small. No BAR-specific values.
agent_config() {
  local role="$1"
  case "$role" in
    planner)
      echo "model=opus next=foreman engine=claude artifact_name=PLAN-BOOK"
      ;;
    foreman)
      # Foreman default per FOUR_BRAIN_AVIATION.md §rank-table and FOUR_BRAIN_ROUTING.md §WHO:
      # Sonnet/default routing model. Opus reserved for escalation cases (ambiguity,
      # architectural judgment, Strike 2, or sovereign request). Mirrors forebrain-garage.sh
      # line 99: "Foreman defaults to Sonnet/default routing model under FOUR_BRAIN_AVIATION v1.3.0."
      echo "model=sonnet next=mechanic engine=claude artifact_name=FOREMAN-DISPATCH"
      ;;
    mechanic)
      echo "model=sonnet next=auditor engine=claude artifact_name=MECHANIC-OUTPUT"
      ;;
    auditor)
      echo "model=gpt-5.3-codex next=DONE engine=codex artifact_name=AUDIT-BOOK"
      ;;
    *) echo "" ;;
  esac
}

invoke_claude() {
  local model="$1" prompt_file="$2" output_file="$3"
  if command -v powershell.exe >/dev/null 2>&1 && command -v cygpath >/dev/null 2>&1; then
    local prompt_win output_win
    prompt_win="$(cygpath -w "$prompt_file")"
    output_win="$(cygpath -w "$output_file")"
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "\
\$ErrorActionPreference = 'Stop'; \
Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue; \
Remove-Item Env:\ANTHROPIC_AUTH_TOKEN -ErrorAction SilentlyContinue; \
\$env:CLAUDE_CODE_GIT_BASH_PATH = 'C:\Program Files\Git\bin\bash.exe'; \
\$promptText = Get-Content -Raw -LiteralPath '$prompt_win'; \
\$result = \$promptText | & claude --print --model '$model' --permission-mode acceptEdits; \
\$code = \$LASTEXITCODE; \
if (\$null -ne \$result) { \$result | Set-Content -LiteralPath '$output_win' -NoNewline; } \
exit \$code"
  else
    claude --print --model "$model" --permission-mode acceptEdits < "$prompt_file" > "$output_file"
  fi
}

invoke_codex() {
  local model="$1" prompt_file="$2" output_file="$3"
  # Codex CLI 0.128+ removed --ask-for-approval; bypass flag implies sandbox bypass.
  codex exec --dangerously-bypass-approvals-and-sandbox --model "$model" "$(cat "$prompt_file")" > "$output_file"
}

main() {
  [[ $# -ge 1 ]] || { echo "usage: four-brain-agent.sh <role> [--once] [--dry-run]" >&2; exit 2; }
  local role="$1"; shift
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) DRY_RUN="true"; shift ;;
      --once) shift ;;   # default behavior; flag accepted for clarity
      *) echo "unknown flag: $1" >&2; exit 2 ;;
    esac
  done

  local cfg
  cfg="$(agent_config "$role")"
  [[ -n "$cfg" ]] || { echo "ERROR: unknown role: $role" >&2; exit 1; }
  eval "$cfg"   # sets model, next, engine, artifact_name

  local prompt_file="$PROMPTS_DIR/$role.md"
  [[ -f "$prompt_file" ]] || { echo "ERROR: prompt missing: $prompt_file" >&2; exit 1; }

  local inbox="$AGENTS_DIR/$role/inbox"
  local working="$AGENTS_DIR/$role/working"
  mkdir -p "$working"

  # Find oldest packet (basename — the .md file).
  local pkt_md
  pkt_md="$(ls -1tr "$inbox"/*.md 2>/dev/null | grep -v "/.gitkeep" | head -1 || true)"
  if [[ -z "$pkt_md" ]]; then
    echo "[$role] inbox empty"
    exit 0
  fi
  local basename
  basename="$(basename "$pkt_md" .md)"
  echo "[$role] processing $basename"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] would: claim $basename, invoke $engine $model, drop to $next"
    exit 0
  fi

  # Claim — verifies handoff_check, moves packet to working/, logs.
  bash "$HELPERS" claim "$role" "$basename"

  # Build the prompt: system prompt + the packet contents (md + yaml).
  local pkt_md_w="$working/$basename.md"
  local pkt_yaml_w="$working/$basename.yaml"
  local llm_prompt
  llm_prompt="$(mktemp)"
  {
    cat "$prompt_file"
    echo
    echo "---"
    echo "## Incoming packet ($basename)"
    echo
    echo "### packet.md"
    cat "$pkt_md_w"
    echo
    echo "### packet.yaml"
    cat "$pkt_yaml_w"
  } > "$llm_prompt"

  # Invoke the role's engine.
  local llm_out="$working/$basename.${role}-output.txt"
  bash "$HELPERS" log "$basename" "$role" "invoke-start" "engine=$engine model=$model"
  local rc=0
  if [[ "$engine" == "claude" ]]; then
    invoke_claude "$model" "$llm_prompt" "$llm_out" || rc=$?
  else
    invoke_codex "$model" "$llm_prompt" "$llm_out" || rc=$?
  fi
  rm -f "$llm_prompt"

  if [[ $rc -ne 0 || ! -s "$llm_out" ]]; then
    bash "$HELPERS" log "$basename" "$role" "invoke-failed" "rc=$rc output_empty=$([[ -s $llm_out ]] && echo no || echo yes)"
    echo "[$role] invoke failed rc=$rc" >&2
    exit "$rc"
  fi
  bash "$HELPERS" log "$basename" "$role" "invoke-done" "output=$llm_out"

  # The role prompts instruct the LLM to echo the artifact path. Trim and use it.
  local artifact_path
  artifact_path="$(tail -1 "$llm_out" | tr -d '[:space:]' || true)"
  if [[ -z "$artifact_path" || ! -f "$artifact_path" ]]; then
    # Fallback: the LLM response itself is the artifact body. Save it under docs/plans/.
    if [[ -n "$PLANS_ROOT" ]]; then
      mkdir -p "$PLANS_ROOT/$basename"
      artifact_path="$PLANS_ROOT/$basename/${artifact_name}.md"
      cp "$llm_out" "$artifact_path"
    else
      artifact_path="$llm_out"
    fi
  fi
  bash "$HELPERS" log "$basename" "$role" "artifact-saved" "$artifact_path"

  # If terminal role (Auditor), write queue lifecycle transition then exit.
  # Contract mirrors forebrain-garage.sh run_auditor:
  #   P=1 → garage_status: AUDITOR_RUNNING → REVIEW_AUDIT_VERDICT
  #   P=0 → garage_status: AUDITOR_RUNNING → BLOCKED
  # The agent does NOT increment strike_count directly; the orchestrator's
  # reconcile path owns strike state (Aviation Model: mechanic ≠ orchestrator).
  if [[ "$next" == "DONE" ]]; then
    local verdict
    verdict="$(grep -m1 "^VERDICT:" "$artifact_path" || echo "VERDICT: UNKNOWN")"

    # Determine terminal status from verdict line.
    local terminal_status
    if echo "$verdict" | grep -q "P=1"; then
      terminal_status="REVIEW_AUDIT_VERDICT"
    else
      terminal_status="BLOCKED"
    fi

    # Update garage_status in the working packet YAML so the queue
    # record reflects the correct terminal state before this agent exits.
    python - "$pkt_yaml_w" "$terminal_status" "$basename" "$artifact_path" "$SCRIPT_DIR/queue.yaml" <<'PYEOF'
import sys, datetime, os
try:
    import yaml as Y
except ImportError:
    sys.stderr.write("ERROR: PyYAML required for terminal Auditor status update\n")
    sys.exit(1)

yaml_path, next_status, bar_id, artifact, queue_yaml_path = sys.argv[1:]

# H-4 fix: load VALID_STATUSES from queue.yaml at runtime instead of hardcoding.
# queue.yaml:status_values is the single source of truth per queue.yaml §status_values.
if os.path.isfile(queue_yaml_path):
    with open(queue_yaml_path, 'r', encoding='utf-8') as _qf:
        _q = Y.safe_load(_qf) or {}
    VALID_STATUSES = set(_q.get('status_values', []))
else:
    sys.stderr.write(f"WARN: queue.yaml not found at {queue_yaml_path}; skipping status validation\n")
    VALID_STATUSES = set()

if VALID_STATUSES and next_status not in VALID_STATUSES:
    sys.stderr.write(
        f"ERROR: terminal status '{next_status}' not in canonical enum.\n"
    )
    sys.exit(1)

with open(yaml_path, 'r', encoding='utf-8') as f:
    pkt = Y.safe_load(f) or {}

g = pkt.setdefault('garage', {})
prev_status = g.get('garage_status', 'AUDITOR_RUNNING')
g['garage_status'] = next_status
g['updated_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

trail = pkt.setdefault('handoff_trail', [])
trail.append({
    'from_role': 'auditor',
    'to_role': 'DONE',
    'artifact': artifact,
    'from_status': prev_status,
    'to_status': next_status,
    'at': g['updated_at'],
})

with open(yaml_path, 'w', encoding='utf-8') as f:
    Y.safe_dump(pkt, f, sort_keys=False, default_flow_style=False)
PYEOF

    # Log the verdict transition (D1 + LBB) with role=auditor action=audit-verdict.
    bash "$HELPERS" log "$basename" "$role" "audit-verdict" \
      "verdict=$verdict terminal_status=$terminal_status artifact=$artifact_path"

    echo "[$role] $verdict → $terminal_status ($artifact_path)"
    [[ "$terminal_status" == "REVIEW_AUDIT_VERDICT" ]] || exit 1
    exit 0
  fi

  # Build next handoff packet by carrying the incoming YAML forward and
  # overlaying the role's artifact pointer + new garage_status. Same shape
  # as planner-intake-template.yaml — this is the doctrine packet that flows
  # through every handoff. We do NOT introduce a different schema.
  local next_md="$working/${basename}-to-${next}.md"
  local next_yaml="$working/${basename}-to-${next}.yaml"

  # Carry the incoming MD forward + append a short handoff note.
  {
    cat "$pkt_md_w"
    echo
    echo "---"
    echo
    echo "## Handoff appended by $role ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
    echo
    echo "- Previous role: \`$role\`"
    echo "- Next role: \`$next\`"
    echo "- Artifact produced: \`$artifact_path\`"
  } > "$next_md"

  # Carry the incoming YAML forward, then overlay role-specific edits in Python.
  python - "$pkt_yaml_w" "$next_yaml" "$role" "$next" "$artifact_path" "$basename" "$SCRIPT_DIR/queue.yaml" <<'PYEOF'
import sys, datetime, os
try:
    import yaml as Y
except ImportError:
    sys.stderr.write("ERROR: PyYAML required for handoff packet generation\n")
    sys.exit(1)

src, dst, role, nxt, artifact, bar_id, queue_yaml_path = sys.argv[1:]
with open(src, 'r', encoding='utf-8') as f:
    pkt = Y.safe_load(f) or {}

# H-4 fix: load VALID_STATUSES from queue.yaml at runtime instead of hardcoding.
# queue.yaml:status_values is the single source of truth per queue.yaml §status_values.
if os.path.isfile(queue_yaml_path):
    with open(queue_yaml_path, 'r', encoding='utf-8') as _qf:
        _q = Y.safe_load(_qf) or {}
    VALID_STATUSES = set(_q.get('status_values', []))
else:
    sys.stderr.write(f"WARN: queue.yaml not found at {queue_yaml_path}; skipping status validation\n")
    VALID_STATUSES = set()

# H-4 fix: load approval_transitions from queue.yaml at runtime instead of hardcoding.
# queue.yaml:review_gates.approval_transitions maps REVIEW_* → next state.
_approval_transitions = {}
if os.path.isfile(queue_yaml_path) and _q:
    _approval_transitions = _q.get('review_gates', {}).get('approval_transitions', {})

# Status mapping per role: scalar value looked up by role name.
# Source: forebrain-garage.sh run_planner/run_foreman/run_mechanic/run_auditor
#   planner  → REVIEW_PLAN_BOOK       (update_status PLANNER_RUNNING → REVIEW_PLAN_BOOK)
#   foreman  → FOREMAN_DISPATCHED     (update_status FOREMAN_RUNNING → FOREMAN_DISPATCHED)
#   mechanic → MECHANIC_DONE          (update_status MECHANIC_RUNNING → MECHANIC_DONE)
#   auditor  → REVIEW_AUDIT_VERDICT   (update_status AUDITOR_RUNNING → REVIEW_AUDIT_VERDICT; always)
STATUS_AFTER = {
    'planner':  'REVIEW_PLAN_BOOK',
    'foreman':  'FOREMAN_DISPATCHED',
    'mechanic': 'MECHANIC_DONE',
    'auditor':  'REVIEW_AUDIT_VERDICT',
}

if role not in STATUS_AFTER:
    sys.stderr.write(f"ERROR: unknown role '{role}'; no status transition defined\n")
    sys.exit(1)

next_status = STATUS_AFTER[role]

# Validate against canonical enum before writing (determinism gate).
if VALID_STATUSES and next_status not in VALID_STATUSES:
    sys.stderr.write(
        f"ERROR: status '{next_status}' for role '{role}' is not in the canonical "
        f"queue.yaml status_values enum. Halting to prevent corrupt packet state.\n"
    )
    sys.exit(1)

# Update the garage block (filesystem is the queue, but status field is informational).
g = pkt.setdefault('garage', {})
g['garage_status'] = next_status
g['bar_id'] = g.get('bar_id', bar_id)
g['updated_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# Append a handoff trail entry. New section, doesn't perturb existing schema.
trail = pkt.setdefault('handoff_trail', [])
trail.append({
    'from_role': role,
    'to_role': nxt,
    'artifact': artifact,
    'at': g['updated_at'],
})

# Update artifact pointer for the receiver.
ap = pkt.setdefault('artifact_pointer', {})
ap['primary'] = artifact
ap['run_dir'] = ap.get('run_dir', '')

# handoff_check: receiver must verify the artifact exists.
hc = pkt.setdefault('handoff_check', {})
hc.setdefault('required_fields', ['artifact_pointer.primary'])
hc.setdefault('required_artifacts', [])
if artifact not in hc['required_artifacts']:
    hc['required_artifacts'].append(artifact)
hc.setdefault('rejected_if_missing', True)

with open(dst, 'w', encoding='utf-8') as f:
    Y.safe_dump(pkt, f, sort_keys=False, default_flow_style=False)
PYEOF

  bash "$HELPERS" drop "$next" "$next_md" "$next_yaml"
  echo "[$role] handed off to $next: $artifact_path"
}

main "$@"

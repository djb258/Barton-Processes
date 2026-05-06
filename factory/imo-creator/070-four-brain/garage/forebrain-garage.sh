#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
GARAGE="$ROOT/factory/imo-creator/070-four-brain/garage"
INBOX="$GARAGE/inbox"
OUTBOX="$GARAGE/outbox"
RUNS="$GARAGE/runs"
TEMPLATE_MD="$ROOT/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md"
TEMPLATE_YAML="$ROOT/factory/imo-creator/070-four-brain/planner-intake-template.yaml"
PROCESS_UT="$ROOT/factory/imo-creator/070-four-brain/PROCESS-UT.md"
FOUR_BRAIN_YAML="$ROOT/factory/imo-creator/070-four-brain/four-brain.yaml"
LBB_SCRIPT="$ROOT/scripts/lbb-log.sh"
MC_API_ROOT="${MC_API_ROOT:-$(cd "$ROOT/../imo-creator-v2/workers/mission-control-api" 2>/dev/null && pwd || true)}"
FOUR_BRAIN_D1_WRITE="${FOUR_BRAIN_D1_WRITE:-local}"
FOUR_BRAIN_D1_REQUIRED="${FOUR_BRAIN_D1_REQUIRED:-false}"
FOUR_BRAIN_D1_DATABASE="${FOUR_BRAIN_D1_DATABASE:-mission-control}"
MC_API_URL="${MC_API_URL:-}"
CLAUDE_CODE_PS1="${CLAUDE_CODE_PS1:-C:\\Users\\CUSTOM PC\\AppData\\Roaming\\npm\\claude.ps1}"

usage() {
  cat <<'USAGE'
Usage:
  forebrain-garage.sh new BAR-123
  forebrain-garage.sh ready
  forebrain-garage.sh claim BAR-123 [planner-name]
  forebrain-garage.sh run-once [--execute] [--defer-lbb] [--planner-model opus]
  forebrain-garage.sh foreman BAR-123 [--execute] [--defer-lbb] [--foreman-model sonnet]
  forebrain-garage.sh mechanic BAR-123 [--execute] [--defer-lbb] [--mechanic-model sonnet]
  forebrain-garage.sh auditor BAR-123 [--execute] [--defer-lbb] [--auditor-model gpt-5.3-codex]
  forebrain-garage.sh reconcile BAR-123 [--defer-lbb]
  forebrain-garage.sh recover BAR-123 [--force] [--defer-lbb]
  forebrain-garage.sh review BAR-123
  forebrain-garage.sh approve BAR-123 NEXT_STATUS
  forebrain-garage.sh run-pipeline [--execute] [--auto-continue] [--defer-lbb] [--planner-model opus] [--foreman-model sonnet] [--mechanic-model sonnet] [--auditor-model gpt-5.3-codex]
  forebrain-garage.sh watch [--execute] [--interval 30] [--planner-model opus]
  forebrain-garage.sh final BAR-123

Contract:
  new    Creates garage/inbox/BAR-123 with intake MD/YAML copied from templates.
  ready  Lists BAR folders whose planner-intake.yaml is READY_FOR_PLANNER.
  claim  Marks a READY_FOR_PLANNER intake as PLANNER_RUNNING.
  run-once Claims the next ready intake and prepares the Planner run artifacts.
           With --execute, calls the configured Planner CLI.
  foreman Converts a PLAN_BOOK_SIGNED BAR into Foreman dispatch.
  mechanic Runs Sonnet Mechanic from Foreman dispatch.
  auditor Runs Codex Auditor from Mechanic output and closes or blocks the BAR.
  reconcile Recovers an interrupted running stage when its expected artifact exists.
  recover  Rolls back a stuck *_RUNNING status when its expected artifact does NOT
           exist. Requires --force. Use only after confirming no live agent is
           writing to the run dir. Resets to the previous done status so the
           stage can be re-run.
  review Prints the handoff packet paths for human inspection.
  approve Moves a REVIEW_* status to the next executable status.
  run-pipeline Runs the next eligible handoff stage. By default it pauses at review gates.
  watch  Repeats run-once forever.
  final  Prints the final product pointer for a BAR.

Doctrine:
  Foreman defaults to Sonnet/default routing model under FOUR_BRAIN_AVIATION v1.3.0.
  Foreman may dispatch only after PLAN_BOOK_SIGNED.
  Live LB&B transition logging is enforced by default; use --defer-lbb only for
  local dry testing when scripts/lbb-log.sh is unavailable.
USAGE
}

require_bar_id() {
  local bar_id="${1:-}"
  if [[ ! "$bar_id" =~ ^BAR-[A-Za-z0-9._-]+$ ]]; then
    echo "Expected BAR id like BAR-123 or BAR-P100-FIRE" >&2
    exit 2
  fi
}

new_intake() {
  local bar_id="$1"
  require_bar_id "$bar_id"
  local dest="$INBOX/$bar_id"
  mkdir -p "$dest"
  if [[ ! -f "$dest/PLANNER-INTAKE.md" ]]; then
    cp "$TEMPLATE_MD" "$dest/PLANNER-INTAKE.md"
  fi
  if [[ ! -f "$dest/planner-intake.yaml" ]]; then
    cp "$TEMPLATE_YAML" "$dest/planner-intake.yaml"
    {
      echo ""
      echo "garage:"
      echo "  garage_status: DRAFT"
      echo "  bar_id: $bar_id"
      echo "  intake_path: factory/imo-creator/070-four-brain/garage/inbox/$bar_id/PLANNER-INTAKE.md"
      echo "  intake_yaml_path: factory/imo-creator/070-four-brain/garage/inbox/$bar_id/planner-intake.yaml"
      echo "  ready_at: null"
      echo "  planner_claimed_by: null"
      echo "  planner_claimed_at: null"
      echo "  next_artifact: docs/plans/$bar_id/PLAN-BOOK.md"
    } >> "$dest/planner-intake.yaml"
  fi
  echo "$dest"
}

ready_list() {
  find "$INBOX" -mindepth 2 -maxdepth 2 -name planner-intake.yaml -print0 |
    while IFS= read -r -d '' file; do
      if [[ "$(grep "garage_status:" "$file" | tail -n 1 | sed 's/.*garage_status:[[:space:]]*//')" == "READY_FOR_PLANNER" ]]; then
        dirname "$file"
      fi
    done
}

claim_intake() {
  local bar_id="$1"
  local planner="${2:-forebrain-planner}"
  require_bar_id "$bar_id"
  local file="$INBOX/$bar_id/planner-intake.yaml"
  if [[ ! -f "$file" ]]; then
    echo "Missing intake YAML: $file" >&2
    exit 1
  fi
  if [[ "$(grep "garage_status:" "$file" | tail -n 1 | sed 's/.*garage_status:[[:space:]]*//')" != "READY_FOR_PLANNER" ]]; then
    echo "Intake is not READY_FOR_PLANNER: $file" >&2
    exit 1
  fi
  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  perl -0pi -e 's/(^garage:\n(?:  .*\n)*?  garage_status: )READY_FOR_PLANNER/${1}PLANNER_RUNNING/m' "$file"
  perl -0pi -e "s/(^garage:\n(?:  .*\n)*?  planner_claimed_by: )null/\${1}$planner/m" "$file"
  perl -0pi -e "s/(^garage:\n(?:  .*\n)*?  planner_claimed_at: )null/\${1}$ts/m" "$file"
  local run_dir
  run_dir="$(latest_run_dir "$bar_id")"
  dispatch_bar_run "$bar_id" "$run_dir"
  echo "$file"
}

first_ready_bar() {
  find "$INBOX" -mindepth 2 -maxdepth 2 -name planner-intake.yaml -print0 |
    while IFS= read -r -d '' file; do
      if [[ "$(grep "garage_status:" "$file" | tail -n 1 | sed 's/.*garage_status:[[:space:]]*//')" == "READY_FOR_PLANNER" ]]; then
        basename "$(dirname "$file")"
        return 0
      fi
    done
}

first_bar_with_status() {
  local status="$1"
  find "$INBOX" -mindepth 2 -maxdepth 2 -name planner-intake.yaml -print0 |
    while IFS= read -r -d '' file; do
      if [[ "$(grep "garage_status:" "$file" | tail -n 1 | sed 's/.*garage_status:[[:space:]]*//')" == "$status" ]]; then
        basename "$(dirname "$file")"
        return 0
      fi
    done
}

current_status() {
  local bar_id="$1"
  local file="$INBOX/$bar_id/planner-intake.yaml"
  grep "garage_status:" "$file" | tail -n 1 | sed 's/.*garage_status:[[:space:]]*//'
}

latest_run_dir() {
  local bar_id="$1"
  if [[ -d "$RUNS/$bar_id" ]]; then
    find "$RUNS/$bar_id" -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1
  fi
}

json_escape() {
  local value="$1"
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$value"
  elif command -v python >/dev/null 2>&1; then
    python -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$value"
  else
    printf '"%s"' "$(printf '%s' "$value" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  fi
}

sha256_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo ""
    return 0
  fi
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$file" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$file" | awk '{print $1}'
  else
    echo ""
  fi
}

archive_stale_artifact() {
  local file="$1"
  if [[ -f "$file" ]]; then
    mv "$file" "$file.stale-$(date -u +"%Y%m%dT%H%M%SZ")"
  fi
}

agent_path() {
  local path="$1"
  if command -v powershell.exe >/dev/null 2>&1 && command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$path"
  else
    echo "$path"
  fi
}

sql_escape() {
  local value="$1"
  printf "%s" "$value" | sed "s/'/''/g"
}

new_uuid() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import uuid; print(uuid.uuid4())'
  elif command -v python >/dev/null 2>&1; then
    python -c 'import uuid; print(uuid.uuid4())'
  else
    printf "%s-%s" "$(date -u +%Y%m%dT%H%M%SZ)" "$RANDOM"
  fi
}

ps_escape() {
  local value="$1"
  printf "%s" "$value" | sed "s/'/''/g"
}

# ---------------------------------------------------------------------------
# BAR-FOUR-BRAIN-CLI: API-based mission-control helpers (replaces wrangler SQL)
# ---------------------------------------------------------------------------

dispatch_bar_run() {
  local bar_id="$1"
  local run_dir="${2:-}"
  [[ "$FOUR_BRAIN_D1_WRITE" == "off" ]] && return 0
  if [[ -z "$MC_API_URL" ]]; then
    echo "[four-brain] MC_API_URL not set; skipping dispatch_bar_run." >&2
    [[ "$FOUR_BRAIN_D1_REQUIRED" == "true" ]] && return 1 || return 0
  fi
  local plan_book_path=""
  if [[ -n "$run_dir" && -f "$run_dir/PLAN-BOOK.md" ]]; then
    plan_book_path="$run_dir/PLAN-BOOK.md"
  elif [[ -f "$ROOT/docs/plans/$bar_id/PLAN-BOOK.md" ]]; then
    plan_book_path="$ROOT/docs/plans/$bar_id/PLAN-BOOK.md"
  fi
  local json_body
  local escaped_bar escaped_plan
  escaped_bar="$(json_escape "$bar_id")"
  if [[ -n "$plan_book_path" ]]; then
    escaped_plan="$(json_escape "$plan_book_path")"
    json_body="{\"bar_id\":$escaped_bar,\"plan_book_path\":$escaped_plan}"
  else
    json_body="{\"bar_id\":$escaped_bar}"
  fi
  local tmp_body http_code
  tmp_body="$(mktemp)"
  http_code="$(curl -s -o "$tmp_body" -w "%{http_code}" \
    -X POST "${MC_API_URL}/four-brain/dispatch" \
    -H "X-API-Key: ${MC_API_KEY:-}" \
    -H "Content-Type: application/json" \
    -d "$json_body")"
  if [[ "$http_code" =~ ^2 ]]; then
    local run_id
    run_id="$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("run_id",""))' < "$tmp_body" 2>/dev/null || true)"
    if [[ -n "$run_id" && -n "$run_dir" ]]; then
      mkdir -p "$run_dir"
      printf "%s" "$run_id" > "$run_dir/.four_brain_run_id"
    fi
    rm -f "$tmp_body"
    return 0
  fi
  echo "[four-brain] dispatch_bar_run failed (HTTP $http_code): $(cat "$tmp_body")" >&2
  rm -f "$tmp_body"
  [[ "$FOUR_BRAIN_D1_REQUIRED" == "true" ]] && return 1 || return 0
}

claim_role_api() {
  local bar_id="$1"
  local role="$2"
  [[ "$FOUR_BRAIN_D1_WRITE" == "off" ]] && return 0
  if [[ -z "$MC_API_URL" ]]; then
    echo "[four-brain] MC_API_URL not set; skipping claim_role_api ($role)." >&2
    [[ "$FOUR_BRAIN_D1_REQUIRED" == "true" ]] && return 1 || return 0
  fi
  local run_dir
  run_dir="$(latest_run_dir "$bar_id" 2>/dev/null || true)"
  local run_id=""
  if [[ -n "$run_dir" && -f "$run_dir/.four_brain_run_id" ]]; then
    run_id="$(cat "$run_dir/.four_brain_run_id")"
  fi
  local escaped_bar json_body
  escaped_bar="$(json_escape "$bar_id")"
  if [[ -n "$run_id" ]]; then
    local escaped_run
    escaped_run="$(json_escape "$run_id")"
    json_body="{\"bar_id\":$escaped_bar,\"run_id\":$escaped_run}"
  else
    json_body="{\"bar_id\":$escaped_bar}"
  fi
  local tmp_body http_code
  tmp_body="$(mktemp)"
  http_code="$(curl -s -o "$tmp_body" -w "%{http_code}" \
    -X POST "${MC_API_URL}/four-brain/claim/${role}" \
    -H "X-API-Key: ${MC_API_KEY:-}" \
    -H "Content-Type: application/json" \
    -d "$json_body")"
  rm -f "$tmp_body"
  if [[ "$http_code" =~ ^2 ]]; then
    return 0
  fi
  echo "[four-brain] claim_role_api ($role) failed (HTTP $http_code)." >&2
  [[ "$FOUR_BRAIN_D1_REQUIRED" == "true" ]] && return 1 || return 0
}

get_run_state() {
  local bar_id="$1"
  if [[ -z "$MC_API_URL" ]]; then
    echo "{}"
    return 0
  fi
  curl -s \
    -H "X-API-Key: ${MC_API_KEY:-}" \
    "${MC_API_URL}/four-brain/state/${bar_id}"
}

write_d1_transition() {
  local bar_id="$1"
  local run_dir="$2"
  local role="$3"
  local action="$4"
  local from_status="$5"
  local to_status="$6"
  local artifact="${7:-}"
  local checklist="${8:-}"
  local status="${9:-done}"
  local notes="${10:-}"
  [[ "$FOUR_BRAIN_D1_WRITE" == "off" ]] && return 0
  if [[ -z "$MC_API_URL" ]]; then
    echo "[four-brain] MC_API_URL not set; skipping D1 transition write." >&2
    [[ "$FOUR_BRAIN_D1_REQUIRED" == "true" ]] && return 1 || return 0
  fi
  # Map bash action strings to schema-valid enum values
  local api_action verdict=""
  case "$action" in
    start)              api_action="dispatch" ;;
    approval-check)     api_action="handoff" ;;
    cli-soft-fail)      api_action="edit" ;;
    reconcile-pass)     api_action="audit-verdict"; verdict="PASS" ;;
    reconcile-fail)     api_action="audit-verdict"; verdict="FAIL" ;;
    handoff|edit|audit-verdict) api_action="$action" ;;
    *)                  api_action="edit" ;;
  esac
  # Auto-detect verdict for audit-verdict if not yet set
  if [[ "$api_action" == "audit-verdict" && -z "$verdict" ]]; then
    local verdict_file="$run_dir/AUDIT-VERDICT.md"
    if [[ -f "$verdict_file" ]]; then
      local first_line
      first_line="$(head -n 1 "$verdict_file")"
      if [[ "$first_line" == *"P=1"* ]]; then
        verdict="PASS"
      else
        verdict="FAIL"
      fi
    else
      verdict="FAIL"
    fi
  fi
  # Read run_id written by dispatch_bar_run; fall back to bar_id
  local run_id="$bar_id"
  if [[ -f "$run_dir/.four_brain_run_id" ]]; then
    run_id="$(cat "$run_dir/.four_brain_run_id")"
  fi
  # Compute evidence hash if artifact file exists
  local evidence_hash=""
  evidence_hash="$(sha256_file "$artifact")"
  # Build JSON body using json_escape for all string values
  local eb er ea enotes eevidence erun
  eb="$(json_escape "$bar_id")"
  erun="$(json_escape "$run_id")"
  ea="$(json_escape "$api_action")"
  local escaped_role
  escaped_role="$(json_escape "$role")"
  enotes="$(json_escape "${notes:-}")"
  eevidence="$(json_escape "${evidence_hash:-}")"
  local json_body
  json_body="{\"bar_id\":$eb,\"run_id\":$erun,\"role\":$escaped_role,\"action\":$ea"
  json_body="${json_body},\"atlas_sections_consulted\":\"FOUR_BRAIN_AVIATION;FOUR_BRAIN_ROUTING;PROC-070\""
  if [[ -n "$evidence_hash" ]]; then
    json_body="${json_body},\"evidence_hash\":$eevidence"
  fi
  if [[ -n "$notes" ]]; then
    json_body="${json_body},\"notes\":$enotes"
  fi
  if [[ -n "$verdict" ]]; then
    json_body="${json_body},\"verdict\":\"$verdict\""
  fi
  json_body="${json_body}}"
  local tmp_body http_code
  tmp_body="$(mktemp)"
  http_code="$(curl -s -o "$tmp_body" -w "%{http_code}" \
    -X POST "${MC_API_URL}/four-brain/transition" \
    -H "X-API-Key: ${MC_API_KEY:-}" \
    -H "Content-Type: application/json" \
    -d "$json_body")"
  rm -f "$tmp_body"
  if [[ "$http_code" =~ ^2 ]]; then
    return 0
  fi
  echo "[four-brain] write_d1_transition failed (HTTP $http_code) for $bar_id $role $action." >&2
  [[ "$FOUR_BRAIN_D1_REQUIRED" == "true" ]] && return 1 || return 0
}

log_transition() {
  local bar_id="$1"
  local run_dir="$2"
  local role="$3"
  local action="$4"
  local from_status="$5"
  local to_status="$6"
  local artifact="${7:-}"
  local checklist="${8:-}"
  local status="${9:-done}"
  local notes="${10:-}"
  local ts hash
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  hash="$(sha256_file "$artifact")"
  mkdir -p "$run_dir"
  {
    printf '{'
    printf '"timestamp":%s,' "$(json_escape "$ts")"
    printf '"bar_id":%s,' "$(json_escape "$bar_id")"
    printf '"run_id":%s,' "$(json_escape "$(basename "$run_dir")")"
    printf '"process_id":"four-brain",'
    printf '"subject_id":"processes",'
    printf '"role":%s,' "$(json_escape "$role")"
    printf '"action":%s,' "$(json_escape "$action")"
    printf '"from_status":%s,' "$(json_escape "$from_status")"
    printf '"to_status":%s,' "$(json_escape "$to_status")"
    printf '"artifact_path":%s,' "$(json_escape "$artifact")"
    printf '"checklist_path":%s,' "$(json_escape "$checklist")"
    printf '"evidence_hash":%s,' "$(json_escape "$hash")"
    printf '"status":%s,' "$(json_escape "$status")"
    printf '"notes":%s' "$(json_escape "$notes")"
    printf '}\n'
  } >> "$run_dir/TRANSITIONS.jsonl"
  write_d1_transition "$bar_id" "$run_dir" "$role" "$action" "$from_status" "$to_status" "$artifact" "$checklist" "$status" "$notes"
}

write_stage_report() {
  local bar_id="$1"
  local status="$2"
  local run_dir="$3"
  local report="$run_dir/STAGE-REPORT.md"
  cat > "$report" <<EOF
# Stage Report: $bar_id

Current status: $status

## Handoff Files

| Stage | File |
| --- | --- |
| Intake MD | $INBOX/$bar_id/PLANNER-INTAKE.md |
| Intake YAML | $INBOX/$bar_id/planner-intake.yaml |
| Planner Prompt | $run_dir/PLANNER-PROMPT.md |
| Planner Raw Output | $run_dir/planner-output.md |
| Plan Book | $ROOT/docs/plans/$bar_id/PLAN-BOOK.md |
| Foreman Prompt | $run_dir/FOREMAN-PROMPT.md |
| Foreman Raw Output | $run_dir/foreman-output.md |
| Foreman Dispatch | $run_dir/FOREMAN-DISPATCH.md |
| Mechanic Prompt | $run_dir/MECHANIC-PROMPT.md |
| Mechanic Raw Output | $run_dir/mechanic-output.raw.md |
| Mechanic Output | $run_dir/MECHANIC-OUTPUT.md |
| Auditor Prompt | $run_dir/AUDITOR-PROMPT.md |
| Auditor Raw Output | $run_dir/auditor-output.raw.md |
| Audit Verdict | $run_dir/AUDIT-VERDICT.md |
| Transition Log | $run_dir/TRANSITIONS.jsonl |
| Final Pointer | $OUTBOX/$bar_id/FINAL-PRODUCT.yaml |

## Review Rule

If status starts with REVIEW_, inspect the files for that stage. If acceptable, run:

\`\`\`bash
factory/imo-creator/070-four-brain/garage/forebrain-garage.sh approve $bar_id NEXT_STATUS
\`\`\`
EOF
  echo "$report"
}

write_lbb_transition() {
  local bar_id="$1"
  local role="$2"
  local action="$3"
  local run_dir="$4"
  local defer_lbb="$5"
  local output="$run_dir/LBB-$role-$action.json"
  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  if [[ -x "$LBB_SCRIPT" ]]; then
    "$LBB_SCRIPT" \
      --bar-id "$bar_id" \
      --role "$role" \
      --action "$action" \
      --subject system \
      --evidence "$run_dir" \
      > "$output"
    echo "$output"
    return 0
  fi
  if [[ "$defer_lbb" == "true" ]]; then
    cat > "$output" <<EOF
{
  "bar_id": "$bar_id",
  "role": "$role",
  "action": "$action",
  "subject": "system",
  "status": "DEFERRED_LOCAL_ONLY",
  "reason": "scripts/lbb-log.sh unavailable in this checkout",
  "evidence": "$run_dir",
  "timestamp": "$ts"
}
EOF
    echo "$output"
    return 0
  fi
  cat > "$run_dir/LBB-BLOCKER-$role-$action.md" <<EOF
# LB&B Transition Blocker

BAR: $bar_id
Role: $role
Action: $action
Timestamp: $ts

Process 070 cannot transition this role because live LB&B logging is required
by FOUR_BRAIN_AVIATION Â§Y and $LBB_SCRIPT is not executable.

For local dry testing only, rerun with --defer-lbb.
EOF
  echo "LB&B transition logging unavailable. See $run_dir/LBB-BLOCKER-$role-$action.md" >&2
  return 1
}

write_planner_prompt() {
  local bar_id="$1"
  local run_dir="$2"
  local intake_dir="$INBOX/$bar_id"
  local plan_dir="$ROOT/docs/plans/$bar_id"
  local prompt="$run_dir/PLANNER-PROMPT.md"
  mkdir -p "$run_dir" "$plan_dir"
  cat > "$prompt" <<PROMPT
ROLE: PLANNER
PROCESS: 070 Four-Brain
BAR: $bar_id

You are the Planner underneath ForeBrain for Process 070.

Your job:
Create the Plan Book for this intake. Do not act as Mechanic. Do not audit.

Required read set:
- $intake_dir/PLANNER-INTAKE.md
- $intake_dir/planner-intake.yaml
- $PROCESS_UT
- $FOUR_BRAIN_YAML
- Atlas Step 0 sources named by the intake and Process 070

Required output:
- Write the Plan Book to: $plan_dir/PLAN-BOOK.md
- Cite Atlas Step 0 sections consulted in the Plan Book.

Planning rules:
- Tell Foreman what needs to be built and audited.
- Do not over-prescribe Mechanic implementation details unless a source file or sovereign constraint locks them.
- Preserve source-of-truth split from the intake.
- Preserve connector/run binding from the intake.
- Include LB&B and Mission Control evidence requirements where applicable.
- Include P=1 definition.
- Include stop conditions.
- Include Mechanic dispatch requirements.
- Include Auditor packet requirements.
- Use UT / BS Law requirements when applicable.

After writing the Plan Book:
- Do not run Mechanic work.
- Do not run Auditor work.
- Return the Plan Book path and any blockers.
PROMPT
  echo "$prompt"
}

write_foreman_prompt() {
  local bar_id="$1"
  local run_dir="$2"
  local plan_path="$ROOT/docs/plans/$bar_id/PLAN-BOOK.md"
  local prompt="$run_dir/FOREMAN-PROMPT.md"
  local process_ut_ref four_brain_ref plan_ref dispatch_ref
  process_ut_ref="$(agent_path "$PROCESS_UT")"
  four_brain_ref="$(agent_path "$FOUR_BRAIN_YAML")"
  plan_ref="$(agent_path "$plan_path")"
  dispatch_ref="$(agent_path "$run_dir/FOREMAN-DISPATCH.md")"
  cat > "$prompt" <<PROMPT
ROLE: FOREMAN
PROCESS: 070 Four-Brain
BAR: $bar_id

You are the Foreman. Your job is routing only.
Role lock: Foreman = Sonnet/default routing. Do not identify the Foreman as Opus. Opus belongs to Planner only.

Required read set:
- $process_ut_ref
- $four_brain_ref
- $plan_ref
- Atlas Â§6
- atlas/manifests/paired-artifacts.yaml
- Plan Book frontispiece

Required output:
- Write dispatch packet to: $dispatch_ref
- Cite Atlas Step 0 sources consulted in the dispatch packet.
- Dispatch packet must explicitly state: Foreman role: Sonnet/default routing.

Rules:
- Do not build.
- Do not audit.
- Do not dispatch unless the Plan Book is signed and the BAR status is PLAN_BOOK_SIGNED.
- Sonnet/default routing model is allowed only for routing. Escalate ambiguity to Planner/Opus, but do not claim Foreman is Opus.
- Convert the Plan Book into literal, scoped Mechanic work orders.
- Include allowed write scope, forbidden paths, acceptance criteria, and tests/evidence required.
- Preserve Mechanic != Auditor.
- Include LB&B and Mission Control evidence requirements when applicable.
- If the Plan Book is not dispatchable, write blockers to the dispatch packet and mark clearly.
PROMPT
  echo "$prompt"
}

write_mechanic_prompt() {
  local bar_id="$1"
  local run_dir="$2"
  local prompt="$run_dir/MECHANIC-PROMPT.md"
  local process_ut_ref four_brain_ref dispatch_ref output_ref
  process_ut_ref="$(agent_path "$PROCESS_UT")"
  four_brain_ref="$(agent_path "$FOUR_BRAIN_YAML")"
  dispatch_ref="$(agent_path "$run_dir/FOREMAN-DISPATCH.md")"
  output_ref="$(agent_path "$run_dir/MECHANIC-OUTPUT.md")"
  cat > "$prompt" <<PROMPT
ROLE: MECHANIC
PROCESS: 070 Four-Brain
BAR: $bar_id

You are the Mechanic. Build only what the Foreman dispatch says.

Required read set:
- $process_ut_ref
- $four_brain_ref
- $dispatch_ref
- Atlas Â§4 or Â§4.5 as applicable
- Plan Book
- Spoke frontmatter for every file to be edited

Required output:
- Write mechanic completion report to: $output_ref
- Cite Atlas Step 0 sources consulted in the mechanic completion report.

Rules:
- Do not audit your own work.
- Do not expand scope beyond Foreman dispatch.
- Make file edits only inside the allowed write scope.
- Run the requested checks if available.
- Report files changed, tests/checks run, evidence produced, and blockers.
- Idempotency: BEFORE editing, inspect target files in the allowed write scope.
  If they ALREADY exist and conform to the dispatch's acceptance criteria
  (header banner, version, step IDs, structural sections), do NOT redo the
  work. Verify conformance, then write MECHANIC-OUTPUT.md citing the
  existing files and the verification you performed, and exit cleanly.
- Final action MUST be writing the MECHANIC-OUTPUT.md completion report.
  The runner keys completion on this file's existence.
PROMPT
  echo "$prompt"
}

write_auditor_prompt() {
  local bar_id="$1"
  local run_dir="$2"
  local prompt="$run_dir/AUDITOR-PROMPT.md"
  local process_ut_ref four_brain_ref plan_ref dispatch_ref mechanic_ref verdict_ref
  process_ut_ref="$(agent_path "$PROCESS_UT")"
  four_brain_ref="$(agent_path "$FOUR_BRAIN_YAML")"
  plan_ref="$(agent_path "$ROOT/docs/plans/$bar_id/PLAN-BOOK.md")"
  dispatch_ref="$(agent_path "$run_dir/FOREMAN-DISPATCH.md")"
  mechanic_ref="$(agent_path "$run_dir/MECHANIC-OUTPUT.md")"
  verdict_ref="$(agent_path "$run_dir/AUDIT-VERDICT.md")"
  cat > "$prompt" <<PROMPT
ROLE: AUDITOR
PROCESS: 070 Four-Brain
BAR: $bar_id

You are the Auditor. Inspect work you did not build.

Required read set:
- $process_ut_ref
- $four_brain_ref
- $plan_ref
- $dispatch_ref
- $mechanic_ref
- atlas/manifests/four-brain-doctrine-gate.yaml

Required output:
- Write audit verdict to: $verdict_ref
- Cite the gate spec consulted.

Rules:
- First line of the audit file must be exactly VERDICT: P=1 or VERDICT: P=0.
- Do not fix findings.
- Check against the Plan Book, Foreman dispatch, evidence requirements, and Aviation Model.
- P=1 only if acceptance criteria and required evidence are satisfied.
- P=0 must include blockers and repair direction for Foreman.
PROMPT
  echo "$prompt"
}

update_status() {
  local file="$1"
  local from="$2"
  local to="$3"
  if [[ "$(grep "garage_status:" "$file" | tail -n 1 | sed 's/.*garage_status:[[:space:]]*//')" == "$from" ]]; then
    perl -0pi -e "s/(^garage:\n(?:  .*\n)*?  garage_status: )$from/\${1}$to/m" "$file"
  else
    echo "Expected status $from in $file" >&2
    return 1
  fi
}

check_line() {
  local ok="$1"
  local text="$2"
  if [[ "$ok" == "true" ]]; then
    echo "- [x] $text"
  else
    echo "- [ ] $text"
  fi
}

sign_plan_book_gate() {
  local bar_id="$1"
  local run_dir="$2"
  local plan="$ROOT/docs/plans/$bar_id/PLAN-BOOK.md"
  local signer="${FOUR_BRAIN_SIGNER:-Dave Barton}"
  local signed_at="${FOUR_BRAIN_SIGNED_AT:-$(date -u +"%Y-%m-%d")}"
  local checklist="$run_dir/APPROVAL-CHECKLIST-PLAN_BOOK_SIGNED.md"
  local failed="false"

  mkdir -p "$run_dir"

  local exists="false"
  local top_status_ready="false"
  local dc_status_ready="false"
  local has_handoff="false"
  local has_mechanic_dispatch="false"
  local has_auditor_packet="false"
  local has_p1="false"
  local has_stop_conditions="false"
  local has_open_blockers="false"
  local has_dmj_default_yes="false"

  [[ -f "$plan" ]] && exists="true"
  if [[ "$exists" == "true" ]]; then
    grep -q '^\*\*Status:\*\* READY-FOR-FOREMAN' "$plan" && top_status_ready="true"
    grep -q '| Status | READY-FOR-FOREMAN |' "$plan" && dc_status_ready="true"
    grep -q '## .*HANDOFF' "$plan" && has_handoff="true"
    grep -q 'MECHANIC DISPATCH REQUIREMENTS' "$plan" && has_mechanic_dispatch="true"
    grep -q 'AUDITOR PACKET' "$plan" && has_auditor_packet="true"
    grep -q 'P=1 DEFINITION' "$plan" && has_p1="true"
    grep -q 'STOP CONDITIONS' "$plan" && has_stop_conditions="true"
    grep -q 'OPEN BLOCKERS / SOVEREIGN DECISIONS' "$plan" && has_open_blockers="true"
    grep -q 'Q-01.*DMJ.*new process number.*YES' "$plan" && has_dmj_default_yes="true"
  fi

  for ok in "$exists" "$top_status_ready" "$dc_status_ready" "$has_handoff" "$has_mechanic_dispatch" "$has_auditor_packet" "$has_p1" "$has_stop_conditions" "$has_open_blockers" "$has_dmj_default_yes"; do
    [[ "$ok" == "true" ]] || failed="true"
  done

  cat > "$checklist" <<EOF
# Approval Checklist: PLAN_BOOK_SIGNED

BAR: $bar_id
Reviewer: $signer
Reviewed at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Plan Book: $plan

## Dispatchability Checks

$(check_line "$exists" "Plan Book artifact exists.")
$(check_line "$top_status_ready" "Plan Book front-matter status is READY-FOR-FOREMAN before signing.")
$(check_line "$dc_status_ready" "Document Control status is READY-FOR-FOREMAN before signing.")
$(check_line "$has_handoff" "Plan Book has a Handoff section.")
$(check_line "$has_mechanic_dispatch" "Plan Book contains Mechanic dispatch requirements.")
$(check_line "$has_auditor_packet" "Plan Book contains Auditor packet requirements.")
$(check_line "$has_p1" "Plan Book contains P=1 definition.")
$(check_line "$has_stop_conditions" "Plan Book contains stop conditions.")
$(check_line "$has_open_blockers" "Plan Book exposes open blockers / sovereign decisions.")
$(check_line "$has_dmj_default_yes" "DMJ separate-process default is present for sovereign approval.")

## Sovereign Approval Checks

- [x] Approval command explicitly requested transition REVIEW_PLAN_BOOK -> PLAN_BOOK_SIGNED.
- [x] Q-01 accepted at approval time: downstream DMJ gets a separate process number; PROC-060 emits DMJ-ready evidence only.
- [x] Runtime wiring remains follow-on BAR unless separately assigned.

EOF

  if [[ "$failed" == "true" ]]; then
    {
      echo "## Verdict"
      echo
      echo "BLOCKED: one or more required checkboxes failed. Plan Book was not signed."
    } >> "$checklist"
    echo "Plan Book approval checklist failed: $checklist" >&2
    return 1
  fi

  {
    echo "## Verdict"
    echo
    echo "PASS: all required checkboxes passed. Signing Plan Book artifact."
  } >> "$checklist"

  perl -0pi -e 's/^\*\*Status:\*\* READY-FOR-FOREMAN/**Status:** PLAN_BOOK_SIGNED/m' "$plan"
  perl -0pi -e 's/\| Q-01 \| Should downstream DMJ receive a new process number separate from PROC-060\? \| open \| \*\*YES\*\* .+?\|/| Q-01 | Should downstream DMJ receive a new process number separate from PROC-060? | confirmed | **YES** - Downstream DMJ gets a separate process number; PROC-060 emits DMJ-ready evidence but the convergence engine lives in its own process. |/s' "$plan"
  perl -0pi -e 's/\| Downstream DMJ should get its own PROC number \| \*\*ASSUMPTION\*\* \| Sovereign confirmation pending \(Q-01\) \|/| Downstream DMJ should get its own PROC number | **FACT** | Sovereign confirmed by PLAN_BOOK_SIGNED approval checklist. |/' "$plan"
  perl -0pi -e 's/\| Runtime wiring belongs to follow-on BAR \| \*\*ASSUMPTION\*\* \| Sovereign confirmation pending \(Q-03\) \|/| Runtime wiring belongs to follow-on BAR | **ASSUMPTION** | Foreman may preserve follow-on BAR placeholder unless sovereign assigns BAR id. |/' "$plan"
  perl -0pi -e 's/\| Status \| READY-FOR-FOREMAN \|/| Status | PLAN_BOOK_SIGNED |/' "$plan"
  perl -0pi -e 's/\| Authority \| Dave Barton \(sovereign .+? signs at BAR open\) \|/| Authority | Dave Barton (sovereign - signed at BAR open) |/' "$plan"
  if ! grep -q '| Signed By |' "$plan"; then
    perl -0pi -e "s/\\| Authority \\| Dave Barton \\(sovereign - signed at BAR open\\) \\|/| Authority | Dave Barton (sovereign - signed at BAR open) |\\n| Signed By | $signer - $signed_at |/" "$plan"
  fi

  echo "$checklist"
}

approve_foreman_dispatch_gate() {
  local bar_id="$1"
  local run_dir="$2"
  local dispatch="$run_dir/FOREMAN-DISPATCH.md"
  local checklist="$run_dir/APPROVAL-CHECKLIST-FOREMAN_DISPATCHED.md"
  local failed="false"

  local exists="false"
  local not_blocked="false"
  local has_atlas="false"
  local has_mechanic="false"
  local has_write_scope="false"
  local has_forbidden="false"
  local has_work_orders="false"
  local has_acceptance="false"
  local preserves_aviation="false"
  local no_foreman_build="false"
  local foreman_role_sonnet="false"
  local foreman_role_not_opus="false"

  [[ -f "$dispatch" ]] && exists="true"
  if [[ "$exists" == "true" ]]; then
    ! grep -q 'DISPATCH STATUS: BLOCKED' "$dispatch" && not_blocked="true"
    grep -qi 'ATLAS STEP 0\|atlas' "$dispatch" && has_atlas="true"
    grep -qi 'Mechanic' "$dispatch" && has_mechanic="true"
    grep -qi 'WRITE SCOPE\|Allowed.*scope' "$dispatch" && has_write_scope="true"
    grep -qi 'FORBIDDEN\|Do not modify\|No other file' "$dispatch" && has_forbidden="true"
    grep -qi 'WORK ORDERS\|WO-0' "$dispatch" && has_work_orders="true"
    grep -qi 'ACCEPTANCE\|P=1\|evidence' "$dispatch" && has_acceptance="true"
    grep -qi 'Mechanic.*Auditor\|Auditor.*Mechanic\|different engine' "$dispatch" && preserves_aviation="true"
    ! grep -qiE 'Foreman (must |should |will )?(build|edit|fix code)|Foreman.*using the Write tool' "$dispatch" && no_foreman_build="true"
    grep -qiE '^\*\*Foreman role:\*\*.*Sonnet|Foreman role.*Sonnet/default routing' "$dispatch" && foreman_role_sonnet="true"
    ! grep -qiE '^\*\*Foreman role:\*\*.*Opus' "$dispatch" && foreman_role_not_opus="true"
  fi

  for ok in "$exists" "$not_blocked" "$has_atlas" "$has_mechanic" "$has_write_scope" "$has_forbidden" "$has_work_orders" "$has_acceptance" "$preserves_aviation" "$no_foreman_build" "$foreman_role_sonnet" "$foreman_role_not_opus"; do
    [[ "$ok" == "true" ]] || failed="true"
  done

  cat > "$checklist" <<EOF
# Approval Checklist: FOREMAN_DISPATCHED

BAR: $bar_id
Reviewed at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Foreman Dispatch: $dispatch

## Foreman -> Mechanic Gate

$(check_line "$exists" "Foreman dispatch artifact exists.")
$(check_line "$not_blocked" "Foreman dispatch is not marked BLOCKED.")
$(check_line "$has_atlas" "Dispatch cites Atlas / Step 0 sources.")
$(check_line "$has_mechanic" "Dispatch is addressed to Mechanic.")
$(check_line "$has_write_scope" "Dispatch states allowed write scope.")
$(check_line "$has_forbidden" "Dispatch states forbidden paths / constraints.")
$(check_line "$has_work_orders" "Dispatch contains literal work orders.")
$(check_line "$has_acceptance" "Dispatch contains acceptance criteria or evidence gates.")
$(check_line "$preserves_aviation" "Dispatch preserves Mechanic != Auditor separation.")
$(check_line "$no_foreman_build" "Dispatch does not make Foreman the builder.")
$(check_line "$foreman_role_sonnet" "Dispatch states Foreman role is Sonnet/default routing.")
$(check_line "$foreman_role_not_opus" "Dispatch does not identify Foreman as Opus.")

EOF

  if [[ "$failed" == "true" ]]; then
    {
      echo "## Verdict"
      echo
      echo "BLOCKED: Foreman dispatch is not approved for Mechanic."
    } >> "$checklist"
    echo "Foreman dispatch approval checklist failed: $checklist" >&2
    return 1
  fi

  {
    echo "## Verdict"
    echo
    echo "PASS: Foreman dispatch is approved for Mechanic."
  } >> "$checklist"

  echo "$checklist"
}

approve_mechanic_output_gate() {
  local bar_id="$1"
  local run_dir="$2"
  local output="$run_dir/MECHANIC-OUTPUT.md"
  local dispatch="$run_dir/FOREMAN-DISPATCH.md"
  local process_ut="$ROOT/factory/imo-creator/060-run-dyno/PROCESS-UT.md"
  local workflow="$ROOT/factory/imo-creator/060-run-dyno/run-dyno.yaml"
  local checklist="$run_dir/APPROVAL-CHECKLIST-MECHANIC_DONE.md"
  local failed="false"

  local output_exists="false"
  local dispatch_exists="false"
  local process_exists="false"
  local workflow_exists="false"
  local has_files_changed="false"
  local has_tests="false"
  local has_no_self_audit="false"
  local has_plan_ref="false"
  local has_step_spine="false"
  local locked_engine_clean="true"

  [[ -f "$output" ]] && output_exists="true"
  [[ -f "$dispatch" ]] && dispatch_exists="true"
  [[ -f "$process_ut" ]] && process_exists="true"
  [[ -f "$workflow" ]] && workflow_exists="true"
  if [[ "$output_exists" == "true" ]]; then
    grep -qi 'Files changed\|Changed files\|PROCESS-UT.md\|run-dyno.yaml' "$output" && has_files_changed="true"
    grep -qi 'Tests run\|Validation\|Verified\|syntax' "$output" && has_tests="true"
    grep -qi 'Do not audit\|not audit\|Auditor\|hand.*Codex' "$output" && has_no_self_audit="true"
    grep -qi 'Plan Book\|PLAN-BOOK.md' "$output" && has_plan_ref="true"
  fi
  if [[ "$process_exists" == "true" && "$workflow_exists" == "true" ]]; then
    grep -q 'FCE-00' "$process_ut" && grep -q 'FCE-14' "$process_ut" && grep -q 'FCE-00' "$workflow" && grep -q 'FCE-14' "$workflow" && has_step_spine="true"
  fi

  # If sibling blueprint repo is present, verify locked engine files were not changed.
  if [[ -d "$ROOT/../dyno-engine" ]]; then
    if ! git -C "$ROOT/../dyno-engine" diff --quiet -- engine/us.py engine/up.py 2>/dev/null; then
      locked_engine_clean="false"
    fi
  fi

  for ok in "$output_exists" "$dispatch_exists" "$process_exists" "$workflow_exists" "$has_files_changed" "$has_tests" "$has_no_self_audit" "$has_plan_ref" "$has_step_spine" "$locked_engine_clean"; do
    [[ "$ok" == "true" ]] || failed="true"
  done

  cat > "$checklist" <<EOF
# Approval Checklist: MECHANIC_DONE

BAR: $bar_id
Reviewed at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Mechanic Output: $output
Foreman Dispatch: $dispatch

## Mechanic -> Auditor Gate

$(check_line "$output_exists" "Mechanic output artifact exists.")
$(check_line "$dispatch_exists" "Foreman dispatch artifact exists for comparison.")
$(check_line "$process_exists" "PROC-060 PROCESS-UT.md exists.")
$(check_line "$workflow_exists" "PROC-060 companion workflow YAML exists.")
$(check_line "$has_files_changed" "Mechanic output lists changed files.")
$(check_line "$has_tests" "Mechanic output reports tests or validation.")
$(check_line "$has_no_self_audit" "Mechanic output preserves Auditor handoff / no self-audit.")
$(check_line "$has_plan_ref" "Mechanic output references the Plan Book.")
$(check_line "$has_step_spine" "Both PROC-060 artifacts contain FCE-00 through FCE-14 spine endpoints.")
$(check_line "$locked_engine_clean" "Locked us.py/up.py files are clean when blueprint repo is present.")

EOF

  if [[ "$failed" == "true" ]]; then
    {
      echo "## Verdict"
      echo
      echo "BLOCKED: Mechanic output is not approved for Auditor."
    } >> "$checklist"
    echo "Mechanic output approval checklist failed: $checklist" >&2
    return 1
  fi

  {
    echo "## Verdict"
    echo
    echo "PASS: Mechanic output is approved for Auditor."
  } >> "$checklist"

  echo "$checklist"
}

write_final_pointer() {
  local bar_id="$1"
  local status="$2"
  local artifact="$3"
  local run_dir="$4"
  local pointer="$OUTBOX/$bar_id/FINAL-PRODUCT.yaml"
  mkdir -p "$(dirname "$pointer")"
  cat > "$pointer" <<EOF
bar_id: $bar_id
final_status: $status
primary_artifact: $artifact
intake_path: $INBOX/$bar_id/PLANNER-INTAKE.md
intake_yaml_path: $INBOX/$bar_id/planner-intake.yaml
run_dir: $run_dir
evidence:
  lbb: $run_dir/LBB-*.json
  mission_control: pending_or_external
  planner_output: $run_dir/planner-output.md
next_owner: foreman
updated_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF
  echo "$pointer"
}

run_planner_cli() {
  local model="$1"
  local prompt="$2"
  local run_dir="$3"
  local output="$run_dir/planner-output.md"
  run_claude_cli "$model" "$prompt" "$output"
  echo "$output"
}

run_claude_cli() {
  local model="$1"
  local prompt="$2"
  local output="$3"
  if command -v powershell.exe >/dev/null 2>&1 && command -v cygpath >/dev/null 2>&1; then
    local prompt_win root_win output_win
    prompt_win="$(cygpath -w "$prompt")"
    root_win="$(cygpath -w "$ROOT")"
    output_win="$(cygpath -w "$output")"
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "\
\$ErrorActionPreference = 'Stop'; \
Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue; \
Remove-Item Env:\ANTHROPIC_AUTH_TOKEN -ErrorAction SilentlyContinue; \
\$env:CLAUDE_CODE_GIT_BASH_PATH = 'C:\Program Files\Git\bin\bash.exe'; \
\$promptText = Get-Content -Raw -LiteralPath '$(ps_escape "$prompt_win")'; \
\$result = \$promptText | & '$(ps_escape "$CLAUDE_CODE_PS1")' --print --model '$(ps_escape "$model")' --permission-mode acceptEdits --add-dir '$(ps_escape "$root_win")'; \
\$code = \$LASTEXITCODE; \
if (\$null -ne \$result) { \$result | Set-Content -LiteralPath '$(ps_escape "$output_win")' -NoNewline; } \
exit \$code"
  else
    claude --print --model "$model" --permission-mode acceptEdits --add-dir "$ROOT" < "$prompt" > "$output"
  fi
}

run_codex_cli() {
  local model="$1"
  local prompt="$2"
  local output="$3"
  local rc=0
  codex exec --cd "$ROOT" --sandbox danger-full-access --ask-for-approval never --model "$model" "$(cat "$prompt")" > "$output" || rc=$?
  return "$rc"
}

run_once() {
  local execute="false"
  local auto_continue="false"
  local defer_lbb="false"
  local planner_model="opus"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --execute)
        execute="true"
        shift
        ;;
      --auto-continue)
        auto_continue="true"
        shift
        ;;
      --defer-lbb)
        defer_lbb="true"
        shift
        ;;
      --planner-model)
        planner_model="${2:-opus}"
        shift 2
        ;;
      *)
        echo "Unknown run-once option: $1" >&2
        exit 2
        ;;
    esac
  done

  local bar_id
  bar_id="$(first_ready_bar || true)"
  if [[ -z "$bar_id" ]]; then
    echo "No READY_FOR_PLANNER intake found."
    return 0
  fi

  local ts run_dir intake_yaml prompt plan_path
  ts="$(date -u +"%Y%m%dT%H%M%SZ")"
  run_dir="$RUNS/$bar_id/$ts"
  mkdir -p "$run_dir"
  intake_yaml="$INBOX/$bar_id/planner-intake.yaml"
  claim_intake "$bar_id" "forebrain-planner" > "$run_dir/claimed-intake.txt"
  prompt="$(write_planner_prompt "$bar_id" "$run_dir")"
  plan_path="$ROOT/docs/plans/$bar_id/PLAN-BOOK.md"
  {
    echo "bar_id: $bar_id"
    echo "run_dir: $run_dir"
    echo "prompt: $prompt"
    echo "planner_cli: claude"
    echo "planner_model: $planner_model"
    echo "execute: $execute"
    echo "defer_lbb: $defer_lbb"
    echo "plan_book: $plan_path"
    echo "started_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  } > "$run_dir/run.yaml"

  if [[ "$execute" != "true" ]]; then
    echo "$prompt"
    return 0
  fi

  if run_planner_cli "$planner_model" "$prompt" "$run_dir" > "$run_dir/planner-output-path.txt"; then
    if [[ -f "$plan_path" ]]; then
      if ! write_lbb_transition "$bar_id" "planner" "dispatch" "$run_dir" "$defer_lbb" > "$run_dir/lbb-planner-path.txt"; then
        update_status "$intake_yaml" "PLANNER_RUNNING" "BLOCKED"
        return 1
      fi
      if [[ "$auto_continue" == "true" ]]; then
        if ! sign_plan_book_gate "$bar_id" "$run_dir" > "$run_dir/approval-checklist-plan-book-path.txt"; then
          log_transition "$bar_id" "$run_dir" "planner" "approval-check" "PLANNER_RUNNING" "BLOCKED" "$plan_path" "$run_dir/APPROVAL-CHECKLIST-PLAN_BOOK_SIGNED.md" "blocked" "Plan Book approval checklist failed."
          update_status "$intake_yaml" "PLANNER_RUNNING" "BLOCKED"
          return 1
        fi
        update_status "$intake_yaml" "PLANNER_RUNNING" "PLAN_BOOK_SIGNED"
        log_transition "$bar_id" "$run_dir" "planner" "approval-check" "PLANNER_RUNNING" "PLAN_BOOK_SIGNED" "$plan_path" "$run_dir/APPROVAL-CHECKLIST-PLAN_BOOK_SIGNED.md" "done" "Auto-continue signed Plan Book after checklist pass."
      else
        update_status "$intake_yaml" "PLANNER_RUNNING" "REVIEW_PLAN_BOOK"
        log_transition "$bar_id" "$run_dir" "planner" "dispatch" "PLANNER_RUNNING" "REVIEW_PLAN_BOOK" "$plan_path" "" "done" "Planner produced Plan Book; review required."
      fi
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      write_final_pointer "$bar_id" "$(current_status "$bar_id")" "$plan_path" "$run_dir" > "$run_dir/final-product-pointer.txt"
      echo "$plan_path"
    else
      update_status "$intake_yaml" "PLANNER_RUNNING" "BLOCKED"
      echo "Planner completed but did not create Plan Book: $plan_path" >&2
      return 1
    fi
  else
    update_status "$intake_yaml" "PLANNER_RUNNING" "BLOCKED"
    echo "Planner CLI failed. See $run_dir" >&2
    return 1
  fi
}

run_foreman() {
  local bar_id="$1"
  local execute="false"
  local auto_continue="false"
  local defer_lbb="false"
  local foreman_model="sonnet"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --execute) execute="true"; shift ;;
      --auto-continue) auto_continue="true"; shift ;;
      --defer-lbb) defer_lbb="true"; shift ;;
      --foreman-model) foreman_model="${2:-sonnet}"; shift 2 ;;
      *) echo "Unknown foreman option: $1" >&2; exit 2 ;;
    esac
  done
  require_bar_id "$bar_id"
  local intake_yaml="$INBOX/$bar_id/planner-intake.yaml"
  local run_dir
  run_dir="$(latest_run_dir "$bar_id")"
  if [[ -z "$run_dir" ]]; then
    run_dir="$RUNS/$bar_id/$(date -u +"%Y%m%dT%H%M%SZ")"
    mkdir -p "$run_dir"
  fi
  local prompt
  prompt="$(write_foreman_prompt "$bar_id" "$run_dir")"
  if [[ "$execute" != "true" ]]; then
    echo "$prompt"
    return 0
  fi
  local cur_status
  cur_status="$(current_status "$bar_id")"
  if [[ "$cur_status" == "FOREMAN_RUNNING" ]]; then
    echo "BAR is already FOREMAN_RUNNING. Use 'reconcile $bar_id' to recover, or wait." >&2
    return 2
  fi
  archive_stale_artifact "$run_dir/FOREMAN-DISPATCH.md"
  update_status "$intake_yaml" "PLAN_BOOK_SIGNED" "FOREMAN_RUNNING"
  claim_role_api "$bar_id" "foreman"
  log_transition "$bar_id" "$run_dir" "foreman" "start" "PLAN_BOOK_SIGNED" "FOREMAN_RUNNING" "$prompt" "" "done" "Foreman stage started."
  local cli_rc=0
  run_claude_cli "$foreman_model" "$prompt" "$run_dir/foreman-output.md" || cli_rc=$?
  if [[ -f "$run_dir/FOREMAN-DISPATCH.md" ]]; then
    if [[ "$cli_rc" -ne 0 ]]; then
      log_transition "$bar_id" "$run_dir" "foreman" "cli-soft-fail" "FOREMAN_RUNNING" "FOREMAN_RUNNING" "$run_dir/foreman-output.md" "" "done" "CLI rc=$cli_rc but dispatch artifact exists; proceeding."
    fi
    if ! write_lbb_transition "$bar_id" "foreman" "handoff" "$run_dir" "$defer_lbb" > "$run_dir/lbb-foreman-path.txt"; then
      update_status "$intake_yaml" "FOREMAN_RUNNING" "BLOCKED"
      return 1
    fi
    if [[ "$auto_continue" == "true" ]]; then
      update_status "$intake_yaml" "FOREMAN_RUNNING" "FOREMAN_DISPATCHED"
      log_transition "$bar_id" "$run_dir" "foreman" "handoff" "FOREMAN_RUNNING" "FOREMAN_DISPATCHED" "$run_dir/FOREMAN-DISPATCH.md" "" "done" "Foreman dispatch produced; auto-continue."
    else
      update_status "$intake_yaml" "FOREMAN_RUNNING" "REVIEW_FOREMAN_DISPATCH"
      log_transition "$bar_id" "$run_dir" "foreman" "handoff" "FOREMAN_RUNNING" "REVIEW_FOREMAN_DISPATCH" "$run_dir/FOREMAN-DISPATCH.md" "" "done" "Foreman dispatch produced; review required."
    fi
    write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
    echo "$run_dir/FOREMAN-DISPATCH.md"
  else
    update_status "$intake_yaml" "FOREMAN_RUNNING" "BLOCKED"
    log_transition "$bar_id" "$run_dir" "foreman" "handoff" "FOREMAN_RUNNING" "BLOCKED" "$run_dir/foreman-output.md" "" "failed" "Foreman produced no FOREMAN-DISPATCH.md (cli rc=$cli_rc)."
    echo "Foreman produced no dispatch: $run_dir/FOREMAN-DISPATCH.md (cli rc=$cli_rc)" >&2
    return 1
  fi
}

run_mechanic() {
  local bar_id="$1"
  local execute="false"
  local auto_continue="false"
  local defer_lbb="false"
  local mechanic_model="sonnet"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --execute) execute="true"; shift ;;
      --auto-continue) auto_continue="true"; shift ;;
      --defer-lbb) defer_lbb="true"; shift ;;
      --mechanic-model) mechanic_model="${2:-sonnet}"; shift 2 ;;
      *) echo "Unknown mechanic option: $1" >&2; exit 2 ;;
    esac
  done
  require_bar_id "$bar_id"
  local intake_yaml="$INBOX/$bar_id/planner-intake.yaml"
  local run_dir
  run_dir="$(latest_run_dir "$bar_id")"
  if [[ -z "$run_dir" ]]; then
    echo "No run dir found for $bar_id" >&2
    return 1
  fi
  local prompt
  prompt="$(write_mechanic_prompt "$bar_id" "$run_dir")"
  if [[ "$execute" != "true" ]]; then
    echo "$prompt"
    return 0
  fi
  local cur_status
  cur_status="$(current_status "$bar_id")"
  if [[ "$cur_status" == "MECHANIC_RUNNING" ]]; then
    echo "BAR is already MECHANIC_RUNNING. Use 'reconcile $bar_id' to recover, or wait." >&2
    return 2
  fi
  archive_stale_artifact "$run_dir/MECHANIC-OUTPUT.md"
  update_status "$intake_yaml" "FOREMAN_DISPATCHED" "MECHANIC_RUNNING"
  claim_role_api "$bar_id" "mechanic"
  log_transition "$bar_id" "$run_dir" "mechanic" "start" "FOREMAN_DISPATCHED" "MECHANIC_RUNNING" "$prompt" "" "done" "Mechanic stage started."
  local cli_rc=0
  run_claude_cli "$mechanic_model" "$prompt" "$run_dir/mechanic-output.raw.md" || cli_rc=$?
  if [[ -f "$run_dir/MECHANIC-OUTPUT.md" ]]; then
    if [[ "$cli_rc" -ne 0 ]]; then
      log_transition "$bar_id" "$run_dir" "mechanic" "cli-soft-fail" "MECHANIC_RUNNING" "MECHANIC_RUNNING" "$run_dir/mechanic-output.raw.md" "" "done" "CLI rc=$cli_rc but mechanic output artifact exists; proceeding."
    fi
    if ! write_lbb_transition "$bar_id" "mechanic" "edit" "$run_dir" "$defer_lbb" > "$run_dir/lbb-mechanic-path.txt"; then
      update_status "$intake_yaml" "MECHANIC_RUNNING" "BLOCKED"
      return 1
    fi
    if [[ "$auto_continue" == "true" ]]; then
      update_status "$intake_yaml" "MECHANIC_RUNNING" "MECHANIC_DONE"
      log_transition "$bar_id" "$run_dir" "mechanic" "edit" "MECHANIC_RUNNING" "MECHANIC_DONE" "$run_dir/MECHANIC-OUTPUT.md" "" "done" "Mechanic output produced; auto-continue."
    else
      update_status "$intake_yaml" "MECHANIC_RUNNING" "REVIEW_MECHANIC_OUTPUT"
      log_transition "$bar_id" "$run_dir" "mechanic" "edit" "MECHANIC_RUNNING" "REVIEW_MECHANIC_OUTPUT" "$run_dir/MECHANIC-OUTPUT.md" "" "done" "Mechanic output produced; review required."
    fi
    write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
    echo "$run_dir/MECHANIC-OUTPUT.md"
  else
    update_status "$intake_yaml" "MECHANIC_RUNNING" "BLOCKED"
    log_transition "$bar_id" "$run_dir" "mechanic" "edit" "MECHANIC_RUNNING" "BLOCKED" "$run_dir/mechanic-output.raw.md" "" "failed" "Mechanic produced no MECHANIC-OUTPUT.md (cli rc=$cli_rc)."
    echo "Mechanic produced no output: $run_dir/MECHANIC-OUTPUT.md (cli rc=$cli_rc)" >&2
    return 1
  fi
}

run_auditor() {
  local bar_id="$1"
  local execute="false"
  local defer_lbb="false"
  local auditor_model="gpt-5.3-codex"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --execute) execute="true"; shift ;;
      --defer-lbb) defer_lbb="true"; shift ;;
      --auditor-model) auditor_model="${2:-gpt-5.3-codex}"; shift 2 ;;
      *) echo "Unknown auditor option: $1" >&2; exit 2 ;;
    esac
  done
  require_bar_id "$bar_id"
  local intake_yaml="$INBOX/$bar_id/planner-intake.yaml"
  local run_dir
  run_dir="$(latest_run_dir "$bar_id")"
  if [[ -z "$run_dir" ]]; then
    echo "No run dir found for $bar_id" >&2
    return 1
  fi
  local prompt
  prompt="$(write_auditor_prompt "$bar_id" "$run_dir")"
  if [[ "$execute" != "true" ]]; then
    echo "$prompt"
    return 0
  fi
  local cur_status
  cur_status="$(current_status "$bar_id")"
  if [[ "$cur_status" == "AUDITOR_RUNNING" ]]; then
    echo "BAR is already AUDITOR_RUNNING. Use 'reconcile $bar_id' to recover when AUDIT-VERDICT.md exists, or 'recover $bar_id --force' if no live agent is writing." >&2
    return 2
  fi
  archive_stale_artifact "$run_dir/AUDIT-VERDICT.md"
  update_status "$intake_yaml" "MECHANIC_DONE" "AUDITOR_RUNNING"
  claim_role_api "$bar_id" "auditor"
  log_transition "$bar_id" "$run_dir" "auditor" "start" "MECHANIC_DONE" "AUDITOR_RUNNING" "$prompt" "" "done" "Auditor stage started."
  local cli_rc=0
  run_codex_cli "$auditor_model" "$prompt" "$run_dir/auditor-output.raw.md" || cli_rc=$?
  if [[ -f "$run_dir/AUDIT-VERDICT.md" ]]; then
    if [[ "$cli_rc" -ne 0 ]]; then
      log_transition "$bar_id" "$run_dir" "auditor" "cli-soft-fail" "AUDITOR_RUNNING" "AUDITOR_RUNNING" "$run_dir/auditor-output.raw.md" "" "done" "Codex rc=$cli_rc but AUDIT-VERDICT.md exists; proceeding."
    fi
    if head -n 1 "$run_dir/AUDIT-VERDICT.md" | grep -q "VERDICT: P=1"; then
      if ! write_lbb_transition "$bar_id" "auditor" "audit-verdict" "$run_dir" "$defer_lbb" > "$run_dir/lbb-auditor-path.txt"; then
        update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
        return 1
      fi
      update_status "$intake_yaml" "AUDITOR_RUNNING" "REVIEW_AUDIT_VERDICT"
      log_transition "$bar_id" "$run_dir" "auditor" "audit-verdict" "AUDITOR_RUNNING" "REVIEW_AUDIT_VERDICT" "$run_dir/AUDIT-VERDICT.md" "" "done" "Auditor returned P=1; review required."
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      write_final_pointer "$bar_id" "$(current_status "$bar_id")" "$run_dir/AUDIT-VERDICT.md" "$run_dir" > "$run_dir/final-product-pointer.txt"
      echo "$run_dir/AUDIT-VERDICT.md"
    else
      update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
      log_transition "$bar_id" "$run_dir" "auditor" "audit-verdict" "AUDITOR_RUNNING" "BLOCKED" "$run_dir/AUDIT-VERDICT.md" "" "blocked" "Auditor returned non-P=1 verdict."
      echo "$run_dir/AUDIT-VERDICT.md"
      return 1
    fi
  else
    update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
    log_transition "$bar_id" "$run_dir" "auditor" "audit-verdict" "AUDITOR_RUNNING" "BLOCKED" "$run_dir/auditor-output.raw.md" "" "failed" "Auditor produced no AUDIT-VERDICT.md (codex rc=$cli_rc)."
    echo "Auditor produced no verdict: $run_dir/AUDIT-VERDICT.md (codex rc=$cli_rc)" >&2
    return 1
  fi
}

reconcile_bar() {
  local bar_id="$1"
  local defer_lbb="false"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --defer-lbb) defer_lbb="true"; shift ;;
      *) echo "Unknown reconcile option: $1" >&2; exit 2 ;;
    esac
  done
  require_bar_id "$bar_id"
  local intake_yaml="$INBOX/$bar_id/planner-intake.yaml"
  local run_dir
  run_dir="$(latest_run_dir "$bar_id")"
  if [[ -z "$run_dir" ]]; then
    echo "No run dir found for $bar_id" >&2
    return 1
  fi
  local status
  status="$(current_status "$bar_id")"
  case "$status" in
    FOREMAN_RUNNING)
      if [[ ! -f "$run_dir/FOREMAN-DISPATCH.md" ]]; then
        echo "No FOREMAN-DISPATCH.md to reconcile for $bar_id" >&2
        return 1
      fi
      if ! write_lbb_transition "$bar_id" "foreman" "handoff" "$run_dir" "$defer_lbb" > "$run_dir/lbb-foreman-path.txt"; then
        update_status "$intake_yaml" "FOREMAN_RUNNING" "BLOCKED"
        return 1
      fi
      update_status "$intake_yaml" "FOREMAN_RUNNING" "REVIEW_FOREMAN_DISPATCH"
      log_transition "$bar_id" "$run_dir" "foreman" "reconcile" "FOREMAN_RUNNING" "REVIEW_FOREMAN_DISPATCH" "$run_dir/FOREMAN-DISPATCH.md" "" "done" "Reconciled from interrupted Foreman run."
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      ;;
    MECHANIC_RUNNING)
      if [[ ! -f "$run_dir/MECHANIC-OUTPUT.md" ]]; then
        echo "No MECHANIC-OUTPUT.md to reconcile for $bar_id" >&2
        return 1
      fi
      if ! write_lbb_transition "$bar_id" "mechanic" "edit" "$run_dir" "$defer_lbb" > "$run_dir/lbb-mechanic-path.txt"; then
        update_status "$intake_yaml" "MECHANIC_RUNNING" "BLOCKED"
        return 1
      fi
      update_status "$intake_yaml" "MECHANIC_RUNNING" "REVIEW_MECHANIC_OUTPUT"
      log_transition "$bar_id" "$run_dir" "mechanic" "reconcile" "MECHANIC_RUNNING" "REVIEW_MECHANIC_OUTPUT" "$run_dir/MECHANIC-OUTPUT.md" "" "done" "Reconciled from interrupted Mechanic run."
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      ;;
    AUDITOR_RUNNING)
      if [[ ! -f "$run_dir/AUDIT-VERDICT.md" ]]; then
        echo "No AUDIT-VERDICT.md to reconcile for $bar_id" >&2
        return 1
      fi
      if head -n 1 "$run_dir/AUDIT-VERDICT.md" | grep -q "VERDICT: P=1"; then
        if ! write_lbb_transition "$bar_id" "auditor" "audit-verdict" "$run_dir" "$defer_lbb" > "$run_dir/lbb-auditor-path.txt"; then
          update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
          return 1
        fi
        update_status "$intake_yaml" "AUDITOR_RUNNING" "REVIEW_AUDIT_VERDICT"
        log_transition "$bar_id" "$run_dir" "auditor" "reconcile" "AUDITOR_RUNNING" "REVIEW_AUDIT_VERDICT" "$run_dir/AUDIT-VERDICT.md" "" "done" "Reconciled from interrupted Auditor run."
      else
        update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
        log_transition "$bar_id" "$run_dir" "auditor" "reconcile" "AUDITOR_RUNNING" "BLOCKED" "$run_dir/AUDIT-VERDICT.md" "" "blocked" "Reconciled Auditor run with non-P=1 verdict."
        return 1
      fi
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      ;;
    *)
      echo "Nothing to reconcile for $bar_id (status=$status)"
      return 0
      ;;
  esac
  review_bar "$bar_id"
}

recover_bar() {
  local bar_id="$1"
  local force="false"
  local defer_lbb="false"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --force) force="true"; shift ;;
      --defer-lbb) defer_lbb="true"; shift ;;
      *) echo "Unknown recover option: $1" >&2; exit 2 ;;
    esac
  done
  require_bar_id "$bar_id"
  local intake_yaml="$INBOX/$bar_id/planner-intake.yaml"
  local run_dir
  run_dir="$(latest_run_dir "$bar_id")"
  if [[ -z "$run_dir" ]]; then
    echo "No run dir found for $bar_id" >&2
    return 1
  fi
  local status
  status="$(current_status "$bar_id")"
  local artifact prev_status role
  case "$status" in
    FOREMAN_RUNNING)
      artifact="$run_dir/FOREMAN-DISPATCH.md"
      prev_status="PLAN_BOOK_SIGNED"
      role="foreman"
      ;;
    MECHANIC_RUNNING)
      artifact="$run_dir/MECHANIC-OUTPUT.md"
      prev_status="FOREMAN_DISPATCHED"
      role="mechanic"
      ;;
    AUDITOR_RUNNING)
      artifact="$run_dir/AUDIT-VERDICT.md"
      prev_status="MECHANIC_DONE"
      role="auditor"
      ;;
    *)
      echo "recover only acts on *_RUNNING statuses; current=$status" >&2
      echo "If status is REVIEW_*, run approve. If artifact exists for a *_RUNNING status, run reconcile instead." >&2
      return 0
      ;;
  esac
  if [[ -f "$artifact" ]]; then
    echo "Artifact exists: $artifact" >&2
    echo "Run 'reconcile $bar_id' instead of recover. recover is for the missing-artifact case only." >&2
    return 1
  fi
  if [[ "$force" != "true" ]]; then
    echo "BAR is $status with no $artifact." >&2
    echo "Before forcing rollback, confirm no live agent is writing to:" >&2
    echo "  $run_dir" >&2
    echo "If you have confirmed, rerun: forebrain-garage.sh recover $bar_id --force" >&2
    return 2
  fi
  archive_stale_artifact "$artifact"
  update_status "$intake_yaml" "$status" "$prev_status"
  log_transition "$bar_id" "$run_dir" "$role" "recover" "$status" "$prev_status" "" "" "done" "Forced rollback: $status -> $prev_status (no $artifact present)."
  if ! write_lbb_transition "$bar_id" "$role" "recover" "$run_dir" "$defer_lbb" > "$run_dir/lbb-$role-recover-path.txt" 2>/dev/null; then
    echo "LBB transition write skipped or unavailable; continuing." >&2
  fi
  write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
  echo "Recovered $bar_id: $status -> $prev_status. You may now re-run the $role stage."
}

run_pipeline() {
  local execute="false"
  local auto_continue="false"
  local defer_lbb="false"
  local planner_model="opus"
  local foreman_model="sonnet"
  local mechanic_model="sonnet"
  local auditor_model="gpt-5.3-codex"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --execute) execute="true"; shift ;;
      --auto-continue) auto_continue="true"; shift ;;
      --defer-lbb) defer_lbb="true"; shift ;;
      --planner-model) planner_model="${2:-opus}"; shift 2 ;;
      --foreman-model) foreman_model="${2:-sonnet}"; shift 2 ;;
      --mechanic-model) mechanic_model="${2:-sonnet}"; shift 2 ;;
      --auditor-model) auditor_model="${2:-gpt-5.3-codex}"; shift 2 ;;
      *) echo "Unknown run-pipeline option: $1" >&2; exit 2 ;;
    esac
  done
  local bar_id
  bar_id="$(first_bar_with_status READY_FOR_PLANNER || true)"
  if [[ -n "$bar_id" ]]; then
    if [[ "$execute" == "true" ]]; then run_once --execute $([[ "$auto_continue" == "true" ]] && echo --auto-continue) $([[ "$defer_lbb" == "true" ]] && echo --defer-lbb) --planner-model "$planner_model"; else run_once --planner-model "$planner_model"; fi
    return $?
  fi
  bar_id="$(first_bar_with_status PLAN_BOOK_SIGNED || true)"
  if [[ -n "$bar_id" ]]; then
    if [[ "$execute" == "true" ]]; then run_foreman "$bar_id" --execute $([[ "$auto_continue" == "true" ]] && echo --auto-continue) $([[ "$defer_lbb" == "true" ]] && echo --defer-lbb) --foreman-model "$foreman_model"; else run_foreman "$bar_id" --foreman-model "$foreman_model"; fi
    return $?
  fi
  bar_id="$(first_bar_with_status FOREMAN_DISPATCHED || true)"
  if [[ -n "$bar_id" ]]; then
    if [[ "$execute" == "true" ]]; then run_mechanic "$bar_id" --execute $([[ "$auto_continue" == "true" ]] && echo --auto-continue) $([[ "$defer_lbb" == "true" ]] && echo --defer-lbb) --mechanic-model "$mechanic_model"; else run_mechanic "$bar_id" --mechanic-model "$mechanic_model"; fi
    return $?
  fi
  bar_id="$(first_bar_with_status MECHANIC_DONE || true)"
  if [[ -n "$bar_id" ]]; then
    if [[ "$execute" == "true" ]]; then run_auditor "$bar_id" --execute $([[ "$defer_lbb" == "true" ]] && echo --defer-lbb) --auditor-model "$auditor_model"; else run_auditor "$bar_id" --auditor-model "$auditor_model"; fi
    return $?
  fi
  echo "No eligible BAR handoff found."
}

review_bar() {
  local bar_id="$1"
  require_bar_id "$bar_id"
  local run_dir
  run_dir="$(latest_run_dir "$bar_id")"
  if [[ -z "$run_dir" ]]; then
    echo "No run dir found for $bar_id" >&2
    return 1
  fi
  write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir"
}

approve_bar() {
  local bar_id="$1"
  local next_status="$2"
  require_bar_id "$bar_id"
  if [[ -z "$next_status" ]]; then
    echo "Missing next status." >&2
    exit 2
  fi
  local intake_yaml="$INBOX/$bar_id/planner-intake.yaml"
  local status
  local run_dir
  status="$(current_status "$bar_id")"
  run_dir="$(latest_run_dir "$bar_id")"
  if [[ -z "$run_dir" ]]; then
    run_dir="$RUNS/$bar_id/$(date -u +"%Y%m%dT%H%M%SZ")"
    mkdir -p "$run_dir"
  fi
  case "$status:$next_status" in
    REVIEW_PLAN_BOOK:PLAN_BOOK_SIGNED)
      sign_plan_book_gate "$bar_id" "$run_dir" > "$run_dir/approval-checklist-plan-book-path.txt"
      update_status "$intake_yaml" "$status" "$next_status"
      log_transition "$bar_id" "$run_dir" "planner" "approval-check" "$status" "$next_status" "$ROOT/docs/plans/$bar_id/PLAN-BOOK.md" "$run_dir/APPROVAL-CHECKLIST-PLAN_BOOK_SIGNED.md" "done" "Planner-to-Foreman checklist passed."
      ;;
    REVIEW_FOREMAN_DISPATCH:FOREMAN_DISPATCHED)
      approve_foreman_dispatch_gate "$bar_id" "$run_dir" > "$run_dir/approval-checklist-foreman-dispatch-path.txt"
      update_status "$intake_yaml" "$status" "$next_status"
      log_transition "$bar_id" "$run_dir" "foreman" "approval-check" "$status" "$next_status" "$run_dir/FOREMAN-DISPATCH.md" "$run_dir/APPROVAL-CHECKLIST-FOREMAN_DISPATCHED.md" "done" "Foreman-to-Mechanic checklist passed."
      ;;
    REVIEW_MECHANIC_OUTPUT:MECHANIC_DONE)
      approve_mechanic_output_gate "$bar_id" "$run_dir" > "$run_dir/approval-checklist-mechanic-output-path.txt"
      update_status "$intake_yaml" "$status" "$next_status"
      log_transition "$bar_id" "$run_dir" "mechanic" "approval-check" "$status" "$next_status" "$run_dir/MECHANIC-OUTPUT.md" "$run_dir/APPROVAL-CHECKLIST-MECHANIC_DONE.md" "done" "Mechanic-to-Auditor checklist passed."
      ;;
    REVIEW_AUDIT_VERDICT:CLOSED)
      update_status "$intake_yaml" "$status" "$next_status"
      log_transition "$bar_id" "$run_dir" "auditor" "approval-check" "$status" "$next_status" "$run_dir/AUDIT-VERDICT.md" "" "done" "Audit verdict approved; BAR closed."
      ;;
    *)
      echo "Invalid approval transition: $status -> $next_status" >&2
      exit 2
      ;;
  esac
  review_bar "$bar_id"
}

final_pointer() {
  local bar_id="$1"
  require_bar_id "$bar_id"
  local pointer="$OUTBOX/$bar_id/FINAL-PRODUCT.yaml"
  if [[ ! -f "$pointer" ]]; then
    echo "No final product pointer found: $pointer" >&2
    exit 1
  fi
  echo "$pointer"
}

watch_queue() {
  local interval="30"
  local args=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --interval)
        interval="${2:-30}"
        shift 2
        ;;
      *)
        args+=("$1")
        shift
        ;;
    esac
  done
  while true; do
    run_pipeline "${args[@]}" || true
    sleep "$interval"
  done
}

cmd="${1:-}"
case "$cmd" in
  new)
    new_intake "${2:-}"
    ;;
  ready)
    ready_list
    ;;
  claim)
    claim_intake "${2:-}" "${3:-forebrain-planner}"
    ;;
  final)
    final_pointer "${2:-}"
    ;;
  review)
    review_bar "${2:-}"
    ;;
  approve)
    approve_bar "${2:-}" "${3:-}"
    ;;
  foreman)
    bar_id="${2:-}"
    shift 2 || true
    run_foreman "$bar_id" "$@"
    ;;
  mechanic)
    bar_id="${2:-}"
    shift 2 || true
    run_mechanic "$bar_id" "$@"
    ;;
  auditor)
    bar_id="${2:-}"
    shift 2 || true
    run_auditor "$bar_id" "$@"
    ;;
  reconcile)
    bar_id="${2:-}"
    shift 2 || true
    reconcile_bar "$bar_id" "$@"
    ;;
  recover)
    bar_id="${2:-}"
    shift 2 || true
    recover_bar "$bar_id" "$@"
    ;;
  run-once)
    shift
    run_once "$@"
    ;;
  run-pipeline)
    shift
    run_pipeline "$@"
    ;;
  watch)
    shift
    watch_queue "$@"
    ;;
  -h|--help|help|"")
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

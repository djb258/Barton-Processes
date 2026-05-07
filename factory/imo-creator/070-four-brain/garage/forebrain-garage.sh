#!/usr/bin/env bash
# mission_control_exempt: true
# mission_control_exempt_reason: Runtime orchestrator. Pipeline state surfaces via mission-control.system.pipeline slot. Per BAR-070-MC-WIRE Plan Book §7.
# =============================================================================
# forebrain-garage.sh — Process 070 Four-Brain runtime
#
# G-19 DOCTRINE COMPLIANCE (atlas/constants/MISSION_CONTROL.md §10.4)
# -------------------------------------------------------------------
# Sovereign cannot gate the pipeline mid-flight. The only sovereign
# touchpoints are:
#   1. Template-drop boundary (input)  — operator fills planner-intake.yaml
#   2. Auditor verdict boundary (output) — sovereign reviews REVIEW_AUDIT_VERDICT
#
# Between Planner → Foreman → Mechanic → Auditor the pipeline auto-advances.
# All quality judgment of intermediate artifacts (Plan Book, Foreman dispatch,
# Mechanic output) belongs to the Auditor per Aviation Model (mechanic ≠
# auditor). Mid-pipeline content gates that re-judge intermediate artifacts
# either duplicate the Auditor's job or substitute sovereign approval for it
# — both forbidden by G-19.
#
# The three intermediate gate functions (sign_plan_book_gate,
# approve_foreman_dispatch_gate, approve_mechanic_output_gate) are
# artifact-exists checks ONLY. They write a checklist for traceability
# and auto-advance unless the artifact file is missing.
#
# auto_continue defaults to "true" for all role runners. The legacy
# REVIEW_* statuses still exist and the `approve` subcommand still works
# for opt-in manual review during debugging, but the default flow is
# auto-advance per G-19.
#
# Atlas references: §4.5 Repair SOP, §6 Governance, §1.5 Aviation Model
# Refactor: BAR-G-19-COMPLIANCE (2026-05-06)
# =============================================================================

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
MC_API_ROOT="${MC_API_ROOT:-$(cd "$ROOT/../imo-creator-v2/workers/mc-proxy" 2>/dev/null && pwd || true)}"
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
  forebrain-garage.sh reconcile BAR-123 [--defer-lbb] [--auto-continue]
  forebrain-garage.sh recover BAR-123 [--force] [--defer-lbb]
  forebrain-garage.sh strike1 BAR-123 [--defer-lbb]
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
           --auto-continue: advance to FOREMAN_DISPATCHED or MECHANIC_DONE instead
           of pausing at REVIEW_* (AUDITOR_RUNNING always lands at REVIEW_AUDIT_VERDICT).
  recover  Rolls back a stuck *_RUNNING status when its expected artifact does NOT
           exist. Requires --force. Use only after confirming no live agent is
           writing to the run dir. Resets to the previous done status so the
           stage can be re-run.
  strike1  Repair-and-re-audit loop for Strike-1 failures. Resets BAR to
           MECHANIC_RUNNING, re-runs Mechanic (Sonnet), re-runs Auditor (Codex).
           Three consecutive Strike-1 failures on the same BAR → TROUBLESHOOT_TRAIN.
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
  # Supports both legacy nested-block form and v2.0.0 root-level form.
  if grep -qE "^garage:" "$file"; then
    perl -0pi -e 's/(^garage:\n(?:  .*\n)*?  garage_status: )READY_FOR_PLANNER/${1}PLANNER_RUNNING/m' "$file"
    perl -0pi -e "s/(^garage:\n(?:  .*\n)*?  planner_claimed_by: )null/\${1}$planner/m" "$file"
    perl -0pi -e "s/(^garage:\n(?:  .*\n)*?  planner_claimed_at: )null/\${1}$ts/m" "$file"
  else
    # v2.0.0 thin form — root-level garage_status; planner_claimed_* fields not required.
    perl -pi -e 's/^(garage_status:[[:space:]]+)READY_FOR_PLANNER\b/${1}PLANNER_RUNNING/' "$file"
  fi
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

# F-003: snapshot_forbidden_baseline
# Called at the START of run_mechanic, before the Mechanic CLI runs.
# Records SHA256 of each forbidden path so assert_no_locked_constants_touched
# can compare post-run deltas only (ignoring pre-existing workspace dirtiness).
snapshot_forbidden_baseline() {
  local run_dir="$1"
  local v2_root="$ROOT/../imo-creator-v2"
  local baseline_file="$run_dir/.forbidden_baseline.sha256"
  local forbidden_paths=(
    "$v2_root/atlas/constants/FOUNDATIONAL_BEDROCK.md"
    "$v2_root/atlas/constants/DMJ.md"
    "$v2_root/atlas/constants/FCE.md"
    "$v2_root/atlas/skills/skill-creator/SKILL.md"
    "$v2_root/atlas/manifests/STRUCTURE_MANIFEST.yaml"
    "$v2_root/atlas/constants/UNIFIED_TEMPLATE.md"
    "$v2_root/atlas/dyno/us.py"
    "$v2_root/atlas/dyno/up.py"
    "$v2_root/atlas/constants/HOW_TO_BUILD_ANYTHING.md"
    "$v2_root/atlas/constants/KEY.md"
    "$v2_root/atlas/constants/UT_CHECKLIST.md"
    "$v2_root/atlas/constants/BARTON_ENTERPRISES_CTB.md"
    "$v2_root/atlas/ATLAS.md"
    "$v2_root/atlas/constants/THREE_LAYERS_SPINE.md"
    "$v2_root/atlas/constants/BOOK_LAW.md"
    "$v2_root/atlas/constants/FOUR_BRAIN_AVIATION.md"
    "$v2_root/atlas/constants/BS_LAW.md"
    "$v2_root/atlas/constants/mission-control.yaml"
  )
  # Clear and write fresh baseline hashes
  : > "$baseline_file"
  for path in "${forbidden_paths[@]}"; do
    if [[ -f "$path" ]]; then
      local hash
      hash="$(sha256sum "$path" 2>/dev/null | awk '{print $1}' || openssl dgst -sha256 "$path" 2>/dev/null | awk '{print $NF}' || true)"
      printf '%s  %s\n' "${hash:-MISSING}" "$path" >> "$baseline_file"
    else
      printf '%s  %s\n' "ABSENT" "$path" >> "$baseline_file"
    fi
  done
  echo "$baseline_file"
}

# F-003: assert_no_locked_constants_touched
# Called after every mechanic CLI invocation. Compares post-run SHA256 of each
# forbidden path against the baseline captured before the Mechanic ran.
# Only flags violations introduced by the Mechanic CLI — pre-existing workspace
# dirtiness in imo-creator-v2 does NOT trigger a false block.
assert_no_locked_constants_touched() {
  local run_dir="${1:-}"
  local v2_root="$ROOT/../imo-creator-v2"
  local forbidden_paths=(
    "$v2_root/atlas/constants/FOUNDATIONAL_BEDROCK.md"
    "$v2_root/atlas/constants/DMJ.md"
    "$v2_root/atlas/constants/FCE.md"
    "$v2_root/atlas/skills/skill-creator/SKILL.md"
    "$v2_root/atlas/manifests/STRUCTURE_MANIFEST.yaml"
    "$v2_root/atlas/constants/UNIFIED_TEMPLATE.md"
    "$v2_root/atlas/dyno/us.py"
    "$v2_root/atlas/dyno/up.py"
    "$v2_root/atlas/constants/HOW_TO_BUILD_ANYTHING.md"
    "$v2_root/atlas/constants/KEY.md"
    "$v2_root/atlas/constants/UT_CHECKLIST.md"
    "$v2_root/atlas/constants/BARTON_ENTERPRISES_CTB.md"
    "$v2_root/atlas/ATLAS.md"
    "$v2_root/atlas/constants/THREE_LAYERS_SPINE.md"
    "$v2_root/atlas/constants/BOOK_LAW.md"
    "$v2_root/atlas/constants/FOUR_BRAIN_AVIATION.md"
    "$v2_root/atlas/constants/BS_LAW.md"
    "$v2_root/atlas/constants/mission-control.yaml"
  )
  local baseline_file="${run_dir:+$run_dir/.forbidden_baseline.sha256}"
  local violations=()
  for path in "${forbidden_paths[@]}"; do
    local baseline_hash="" post_hash=""
    # Load baseline hash if snapshot exists
    if [[ -n "$baseline_file" && -f "$baseline_file" ]]; then
      baseline_hash="$(grep -F "  $path" "$baseline_file" 2>/dev/null | awk '{print $1}' || true)"
    fi
    # Compute post-run hash
    if [[ -f "$path" ]]; then
      post_hash="$(sha256sum "$path" 2>/dev/null | awk '{print $1}' || openssl dgst -sha256 "$path" 2>/dev/null | awk '{print $NF}' || true)"
    else
      post_hash="ABSENT"
    fi
    # If we have a baseline, compare hashes (delta-only check)
    # If no baseline, fall back to git diff HEAD (legacy behaviour)
    if [[ -n "$baseline_hash" ]]; then
      if [[ "$post_hash" != "$baseline_hash" ]]; then
        violations+=("$path")
      fi
    else
      if [[ -f "$path" ]] && git -C "$v2_root" diff --name-only HEAD -- "$path" 2>/dev/null | grep -q .; then
        violations+=("$path")
      fi
    fi
  done
  if [[ "${#violations[@]}" -gt 0 ]]; then
    echo "[four-brain] BLOCKED: mechanic touched sovereign-locked constants:" >&2
    for v in "${violations[@]}"; do
      echo "  - $v" >&2
    done
    if [[ -n "$run_dir" ]]; then
      printf '%s\n' "${violations[@]}" > "$run_dir/LOCKED-CONSTANTS-VIOLATION.txt"
    fi
    return 1
  fi
  return 0
}

# ---------------------------------------------------------------------------
# BAR-FOUR-BRAIN-CLI: API-based mission-control helpers (replaces wrangler SQL)
# ---------------------------------------------------------------------------

dispatch_bar_run() {
  local bar_id="$1"
  local run_dir="${2:-}"
  [[ "$FOUR_BRAIN_D1_WRITE" == "off" ]] && return 0
  if [[ -z "$MC_API_URL" ]]; then
    # URL unset: silent skip — correct defensive behavior for local-only runs
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
  # Finding 10: FOUR_BRAIN_LOCAL_DEV=true soft-continue only allowed when MC_API_URL is localhost/127.0.0.1/file://
  # Hard-block if LOCAL_DEV=true but URL points to a non-local host (production masking guard)
  if [[ "${FOUR_BRAIN_LOCAL_DEV:-false}" == "true" ]]; then
    if [[ "$MC_API_URL" =~ ^(http://localhost|http://127\.0\.0\.1|file://) ]]; then
      echo "[four-brain] dispatch_bar_run: non-2xx ignored (FOUR_BRAIN_LOCAL_DEV=true + local URL confirmed)." >&2
      return 0
    else
      echo "[four-brain] BLOCKED: FOUR_BRAIN_LOCAL_DEV=true but MC_API_URL='$MC_API_URL' is non-local. Hard-blocking to prevent production masking." >&2
      return 1
    fi
  fi
  return 1
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
  # Finding 10: hard-block if FOUR_BRAIN_LOCAL_DEV=true but MC_API_URL is non-local
  if [[ "${FOUR_BRAIN_LOCAL_DEV:-false}" == "true" ]]; then
    if [[ "$MC_API_URL" =~ ^(http://localhost|http://127\.0\.0\.1|file://) ]]; then
      echo "[four-brain] claim_role_api ($role): non-2xx ignored (FOUR_BRAIN_LOCAL_DEV=true + local URL confirmed)." >&2
      return 0
    else
      echo "[four-brain] BLOCKED: FOUR_BRAIN_LOCAL_DEV=true but MC_API_URL='$MC_API_URL' is non-local. Hard-blocking to prevent production masking." >&2
      return 1
    fi
  fi
  return 1
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
  # Finding 3: include explicit timestamp and lbb_record_id for W-2 evidence completeness
  local ts_now lbb_record_id_val=""
  ts_now="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  # Load lbb_record_id from the most recent LBB write for this role/action if available
  local lbb_json_file="$run_dir/LBB-$role-$action.json"
  if [[ -f "$lbb_json_file" ]]; then
    lbb_record_id_val="$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("record_id",""))' < "$lbb_json_file" 2>/dev/null || true)"
  fi
  local elbb_record_id ets
  elbb_record_id="$(json_escape "${lbb_record_id_val:-}")"
  ets="$(json_escape "$ts_now")"
  local json_body
  json_body="{\"bar_id\":$eb,\"run_id\":$erun,\"role\":$escaped_role,\"action\":$ea"
  json_body="${json_body},\"timestamp\":$ets"
  # Finding 4: role-specific citation sets per Step-0 doctrine requirements
  local atlas_citations
  case "$role" in
    planner)  atlas_citations="KEY,BS_LAW,BOOK_LAW,FOUR_BRAIN_AVIATION,PLANNER_ROLE,MISSION_CONTROL,ATLAS,four-brain-doctrine-gate" ;;
    foreman)  atlas_citations="FOUR_BRAIN_AVIATION,MISSION_CONTROL,MECHANIC_ROLE,paired-artifacts,four-brain-doctrine-gate" ;;
    mechanic) atlas_citations="FOUR_BRAIN_AVIATION,MECHANIC_ROLE,MISSION_CONTROL,ATLAS" ;;
    auditor)  atlas_citations="four-brain-doctrine-gate,AUDITOR_ROLE,BS_LAW,BOOK_LAW,MISSION_CONTROL,ATLAS" ;;
    *)        atlas_citations="FOUR_BRAIN_AVIATION;FOUR_BRAIN_ROUTING;PROC-070" ;;
  esac
  json_body="${json_body},\"atlas_sections_consulted\":\"$atlas_citations\""
  if [[ -n "$lbb_record_id_val" ]]; then
    json_body="${json_body},\"lbb_record_id\":$elbb_record_id"
  fi
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
  if [[ "$http_code" =~ ^2 ]]; then
    # Finding 3: persist returned transition ID for downstream audit evidence
    local transition_id
    transition_id="$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("id","") or d.get("transition_id",""))' < "$tmp_body" 2>/dev/null || true)"
    if [[ -n "$transition_id" ]]; then
      printf "%s" "$transition_id" > "$run_dir/.transition_${role}_id"
    fi
    rm -f "$tmp_body"
    return 0
  fi
  rm -f "$tmp_body"
  echo "[four-brain] write_d1_transition failed (HTTP $http_code) for $bar_id $role $action." >&2
  # Finding 10: hard-block if FOUR_BRAIN_LOCAL_DEV=true but MC_API_URL is non-local
  if [[ "${FOUR_BRAIN_LOCAL_DEV:-false}" == "true" ]]; then
    if [[ "$MC_API_URL" =~ ^(http://localhost|http://127\.0\.0\.1|file://) ]]; then
      echo "[four-brain] write_d1_transition: non-2xx ignored (FOUR_BRAIN_LOCAL_DEV=true + local URL confirmed)." >&2
      return 0
    else
      echo "[four-brain] BLOCKED: FOUR_BRAIN_LOCAL_DEV=true but MC_API_URL='$MC_API_URL' is non-local. Hard-blocking to prevent production masking." >&2
      return 1
    fi
  fi
  return 1
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
    # Finding 4: use --subject processes (canonical BAR-run subject per PROCESS-UT §3/§5)
    # Add mission-control-wiring tag when action is a wiring artifact
    local extra_tags=""
    if [[ "$action" == "wire" || "$action" == "wiring" ]]; then
      extra_tags="--tags mission-control-wiring"
    fi
    "$LBB_SCRIPT" \
      --bar-id "$bar_id" \
      --role "$role" \
      --action "$action" \
      --subject processes \
      --evidence "$run_dir" \
      ${extra_tags:+$extra_tags} \
      > "$output"
    echo "$output"
    return 0
  fi
  if [[ "$defer_lbb" == "true" ]]; then
    # F-008: deferred path is local dry-test only; block unless FOUR_BRAIN_LOCAL_DEV=true
    if [[ "${FOUR_BRAIN_LOCAL_DEV:-false}" != "true" ]]; then
      echo "[four-brain] write_lbb_transition: --defer-lbb requires FOUR_BRAIN_LOCAL_DEV=true. Live LBB logging is mandatory in non-local environments." >&2
      return 1
    fi
    # Finding 4: role-specific citation sets in deferred stub
    local deferred_citations
    case "$role" in
      planner)  deferred_citations="KEY,BS_LAW,BOOK_LAW,FOUR_BRAIN_AVIATION,PLANNER_ROLE,MISSION_CONTROL,ATLAS,four-brain-doctrine-gate" ;;
      foreman)  deferred_citations="FOUR_BRAIN_AVIATION,MISSION_CONTROL,MECHANIC_ROLE,paired-artifacts,four-brain-doctrine-gate" ;;
      mechanic) deferred_citations="FOUR_BRAIN_AVIATION,MECHANIC_ROLE,MISSION_CONTROL,ATLAS" ;;
      auditor)  deferred_citations="four-brain-doctrine-gate,AUDITOR_ROLE,BS_LAW,BOOK_LAW,MISSION_CONTROL,ATLAS" ;;
      *)        deferred_citations="FOUR_BRAIN_AVIATION;FOUR_BRAIN_ROUTING;PROC-070" ;;
    esac
    # Write deferred stub with all 12 canonical LBB schema fields
    # Canonical fields: record_id, bar_id, role, action, evidence_hash,
    #   atlas_sections_consulted, timestamp, sovereign_ref, subject_id,
    #   orbt_mode, gate_verdicts, notes
    cat > "$output" <<EOF
{
  "record_id": "deferred-$(date -u +%s)-$bar_id",
  "bar_id": "$bar_id",
  "role": "$role",
  "action": "$action",
  "evidence_hash": null,
  "atlas_sections_consulted": "$deferred_citations",
  "timestamp": "$ts",
  "sovereign_ref": "imo-creator",
  "subject_id": "processes",
  "orbt_mode": "BUILD",
  "gate_verdicts": null,
  "notes": "DEFERRED_LOCAL_ONLY: scripts/lbb-log.sh unavailable; FOUR_BRAIN_LOCAL_DEV=true"
}
EOF
    # Mark run as non-certifiable — deferred LBB writes cannot be auditor-certified
    touch "$run_dir/.non-certifiable"
    echo "[four-brain] LBB write deferred (local dry-test). Run marked .non-certifiable." >&2
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
by FOUR_BRAIN_AVIATION §Y and $LBB_SCRIPT is not executable.

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
  local v2_atlas="$ROOT/../imo-creator-v2/atlas"
  mkdir -p "$run_dir" "$plan_dir"
  cat > "$prompt" <<PROMPT
ROLE: PLANNER
PROCESS: 070 Four-Brain
BAR: $bar_id
ENGINE: Opus 4.7 (collaborative). Determinism-first gate: reject any design that puts an LLM on the spine.

You are the Planner. Produce the Plan Book. Do not act as Mechanic. Do not audit.

==============================================================================
REQUIRED READ SET (Atlas Step 0 — non-negotiable)
==============================================================================
Intake:
- $intake_dir/PLANNER-INTAKE.md
- $intake_dir/planner-intake.yaml

Process 070:
- $PROCESS_UT
- $FOUR_BRAIN_YAML

Atlas (imo-creator-v2):
- $v2_atlas/constants/KEY.md                              (vocabulary)
- $v2_atlas/ATLAS.md §1 Legend, §4 Map-Building SOP, §4.5 Repair SOP, §6 Governance, §7.3, §7.3a
- $v2_atlas/constants/BS_LAW.md                           (Y-junction; outside.heir/orbt + inside.heir/orbt syntactically distinct)
- $v2_atlas/constants/BOOK_LAW.md                         (eleven body species; Plan-Body shape spec)
- $v2_atlas/constants/FOUR_BRAIN_AVIATION.md              (role locks; determinism gate)
- $v2_atlas/constants/PLANNER_ROLE.md §6b                 (Mission Control Wiring Authority — your responsibility)
- $v2_atlas/constants/MISSION_CONTROL.md §10              (artifact wiring protocol; 3 dispositions)
- $v2_atlas/constants/mission-control.yaml#slots          (slot registry — pick target HEIR ID for WIRE)
- $v2_atlas/constants/UI_STYLE_GUIDE.md                   (render-mode catalog for NEW_SLOT_NEEDED proposals)
- $v2_atlas/manifests/four-brain-doctrine-gate.yaml       (G01-G12 + W-1..W-7 the Auditor will run against your Plan Book)
- $v2_atlas/manifests/paired-artifacts.yaml               (existing pairing registry)

==============================================================================
REQUIRED OUTPUT
==============================================================================
Write the Plan Book to: $plan_dir/PLAN-BOOK.md

Plan Book MUST include (Plan-Body species per Book Law #15):
1. Atlas sections consulted (cite §-numbers)
2. Source-of-truth split (preserved from intake)
3. P=1 definition (explicit conditions, not implied)
4. Stop conditions
5. Mechanic dispatch requirements (literal work orders, allowed write scope, forbidden paths)
6. Auditor packet requirements (which gates apply: G01-G12 + W-1..W-7)
7. **mission_control_wiring section (mandatory — see below)**
8. LBB row schema fields the Mechanic + Auditor must write
9. Open blockers (only if they block dispatch — otherwise leave them for runtime)

==============================================================================
MISSION CONTROL WIRING SECTION (your structural authority — W-2 + W-7 verify)
==============================================================================
For EVERY artifact this BAR will produce or modify, declare ONE of three dispositions:

  WIRE             — slot already exists in mission-control.yaml#slots covering this artifact's CTB position
                     → specify: target_slot_heir_id

  NEW_SLOT_NEEDED  — no existing slot fits, but artifact warrants Mission Control surfacing
                     → specify: proposed_slot { heir_id, ctb_position, render_mode (from UI_STYLE_GUIDE.md), data_source }

  EXEMPT           — pure doctrine, internal config, or implementation detail with no operator-visible state
                     → specify: rationale (one sentence min)

Format (must appear under heading "Mission Control Wiring"):
  mission_control_wiring:
    - artifact: <relative path>
      disposition: WIRE | NEW_SLOT_NEEDED | EXEMPT
      target_slot_heir_id: <heir id>           # WIRE only
      proposed_slot:                            # NEW_SLOT_NEEDED only
        heir_id: <heir id>
        ctb_position: <ctb path>
        render_mode: <mode from UI_STYLE_GUIDE.md>
        data_source: <path | glob | query>
      rationale: <text>                         # required for EXEMPT, recommended for all

DEFAULT DISPOSITION: none. Silence is not a disposition.
If the slot registry has no fitting slot, NEW_SLOT_NEEDED is correct — do not force a WIRE.

==============================================================================
PLANNING RULES
==============================================================================
- Determinism first: if your design puts an LLM on the spine of any required path, REJECT and redesign with deterministic primitives.
- Inventory before you design: existing automation > new automation > new code > AI (last resort).
- Preserve source-of-truth split from the intake.
- Preserve connector/run binding from the intake.
- BS Law: any structured-text artifact this BAR produces (.md or .yaml) ships with both arms (outside.heir/orbt + inside.heir/orbt as syntactically distinct top-level constructs).
- Book Law: name the species for every artifact (UT-Body, Plan-Body, Audit-Body, Workflow-Body, Code-Body, Config-Body, Schema-Body, UI-Body, Data-Body, Catalog-Body, Research-Body).
- Aviation Model: Mechanic ≠ Auditor. Build engine ≠ audit engine.

==============================================================================
HANDOFF
==============================================================================
After writing the Plan Book:
- Do not run Mechanic work.
- Do not run Auditor work.
- Return the Plan Book path and any TRUE blockers (open questions that block dispatch only — runtime-resolvable items go in the Plan Book itself, not as blockers).
PROMPT
  # Finding 1 (BLOCKER): inject STRIKE-CONTEXT.md into required read set if present
  local strike_ctx="$run_dir/STRIKE-CONTEXT.md"
  if [[ -f "$strike_ctx" ]]; then
    cat >> "$prompt" <<STRIKE_INJECT

==============================================================================
STRIKE CONTEXT — READ THIS FIRST (repair run)
==============================================================================
REQUIRED READ: $strike_ctx

You are in a STRIKE REPAIR run. Read STRIKE-CONTEXT.md before any other file.
Repair ONLY the FAIL findings listed in that file. Do NOT redesign scope.
Do NOT address findings not listed. Close listed FAILs in order.
STRIKE_INJECT
  fi
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
  local v2_atlas="$ROOT/../imo-creator-v2/atlas"
  cat > "$prompt" <<PROMPT
ROLE: FOREMAN
PROCESS: 070 Four-Brain
BAR: $bar_id
ENGINE: Sonnet (default routing). Foreman is NOT Opus. Opus belongs to the Planner.

You are the Foreman. Routing only — do not build, do not audit, do not re-design.

==============================================================================
REQUIRED READ SET
==============================================================================
- $process_ut_ref
- $four_brain_ref
- $plan_ref                                              (the signed Plan Book — your input)
- $v2_atlas/ATLAS.md section 6 Governance
- $v2_atlas/constants/MISSION_CONTROL.md section 10      (artifact wiring protocol — pass dispositions to Mechanic verbatim)
- $v2_atlas/constants/MECHANIC_ROLE.md section 5b        (Mechanic execution rules — quote them in the dispatch)
- $v2_atlas/manifests/paired-artifacts.yaml              (pairing registry — Mechanic must register new pairs)
- $v2_atlas/manifests/four-brain-doctrine-gate.yaml      (gates the Auditor will run; Mechanic should know what to expect)

==============================================================================
REQUIRED OUTPUT
==============================================================================
Write dispatch packet to: $dispatch_ref

The dispatch packet MUST contain:
1. Plan Book reference (path + signed status)
2. Atlas Step 0 citations (carry forward from the Plan Book)
3. Literal scoped work orders (one per Mechanic action — file path, exact change, acceptance criterion)
4. Allowed write scope (explicit file paths the Mechanic may touch)
5. Forbidden paths (any locked constants in the 17-list, sovereign-only files, no-touch zones)
6. **Mission Control wiring orders** — pass through the Plan Book's mission_control_wiring section verbatim. For each artifact:
     - WIRE -> instruct Mechanic to update target slot's data_source field
     - NEW_SLOT_NEEDED -> instruct Mechanic to emit proposal in MECHANIC-OUTPUT.md proposed_slots: block (DO NOT modify mission-control.yaml — sovereign-only)
     - EXEMPT -> instruct Mechanic to stamp mission_control_exempt: true + mission_control_exempt_reason in artifact frontmatter
7. Acceptance criteria (per work order — what proves it's done)
8. LBB row requirements (Mechanic must write one row before transitioning)
9. Aviation Model lock: Mechanic != Auditor; Mechanic does NOT self-audit
10. Foreman role declaration: "Foreman role: Sonnet/default routing"

==============================================================================
RULES (verbatim role locks from FOUR_BRAIN_AVIATION.md §6 — Foreman Lock)
==============================================================================
- Do not build. Do not audit. Do not re-architect the Plan Book.
- Convert the Plan Book into LITERAL Mechanic work orders. No interpretation, no creative additions.
- Foreman NEVER flips an Auditor verdict. FAIL stays FAIL until the Auditor itself sees PASS on its own re-run. No "close enough." No human shortcut.
- Foreman NEVER fixes code. Mechanic is the only repairer. On Strike-1, dispatch Mechanic. On Strike-2, escalate to Opus mechanic. On Strike-3, route to Troubleshoot/Train — NOT another repair dispatch.
- Foreman cannot dispatch a BAR without a signed Plan Book. If the Plan Book is missing the mission_control_wiring section, mark BLOCKED and return — Planner-side defect (W-2). Do NOT improvise dispositions.
- If the Plan Book is missing required sections (P=1, work orders, allowed write scope), mark BLOCKED and return — Planner re-runs.
- Escalate ambiguity to the Planner; do not let it become a Mechanic problem.
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
  local v2_atlas="$ROOT/../imo-creator-v2/atlas"
  cat > "$prompt" <<PROMPT
ROLE: MECHANIC
PROCESS: 070 Four-Brain
BAR: $bar_id
ENGINE: Sonnet (Strike-1 retry escalates to Opus). Build only what the Foreman dispatch says.

You are the Mechanic. Construction crew. Per FOUR_BRAIN_AVIATION.md §6 (Mechanic Lock):
- You build to the Plan Book, never beyond it.
- You produce UT Books — the artifact files you write ARE the UT-Body species, shelved in the Library with HEIR coordinates referencing the Plan Book. MECHANIC-OUTPUT.md is the cover sheet, not the deliverable.
- You are the repairer on FAIL. On Strike-1 you re-run against the corrected Plan Book.
- You NEVER self-audit. Auditor (Codex) is the only verdict. Mechanic ≠ Auditor.

==============================================================================
REQUIRED READ SET
==============================================================================
- $dispatch_ref                                          (Foreman dispatch — your authority)
- $process_ut_ref
- $four_brain_ref
- Plan Book (referenced in dispatch)
- Spoke frontmatter for every file you will edit
- $v2_atlas/ATLAS.md section 4 (build) or section 4.5 (repair) as applicable
- $v2_atlas/constants/MECHANIC_ROLE.md section 5b        (Mission Control execution rules — your contract)
- $v2_atlas/constants/MISSION_CONTROL.md section 10      (artifact wiring protocol)

==============================================================================
HARD HALT RULE — PLAN_BOOK_INCOMPLETE
==============================================================================
If the Foreman dispatch is missing the Mission Control wiring orders, OR if any
artifact's disposition is ambiguous (no WIRE/NEW_SLOT_NEEDED/EXEMPT clearly stated):
  -> STOP. Write MECHANIC-OUTPUT.md with status=PLAN_BOOK_INCOMPLETE.
  -> Cite the missing field.
  -> DO NOT improvise dispositions. DO NOT pick "EXEMPT" to skip the wiring step.
  -> This is a Planner-side defect (W-2 strike). Plan Book gets corrected and re-run.

The Mechanic makes ZERO disposition decisions. Architect (Planner) calls; construction (you) executes.

==============================================================================
MISSION CONTROL WIRING EXECUTION (per disposition declared in dispatch)
==============================================================================
WIRE:
  -> Update the named slot's data_source field in atlas/constants/mission-control.yaml
    to reference this artifact's path/glob/query.
  -> Verify the slot HEIR ID exists in mission-control.yaml#slots before editing.
  -> Do NOT add new slots. Sovereign-only.

NEW_SLOT_NEEDED:
  -> DO NOT modify mission-control.yaml. Sovereign-only amendment.
  -> Emit the proposal in MECHANIC-OUTPUT.md under proposed_slots: block:
      proposed_slots:
        - heir_id: <as proposed in dispatch>
          ctb_position: <as proposed>
          render_mode: <as proposed>
          data_source: <as proposed>
          artifact: <relative path>
  -> Sovereign reads the proposals at Auditor verdict and amends skeleton in a follow-up sovereign BAR.

EXEMPT:
  -> Stamp the artifact's frontmatter:
      mission_control_exempt: true
      mission_control_exempt_reason: <rationale from dispatch>
  -> No mission-control.yaml change.

==============================================================================
RULES
==============================================================================
- Edit only inside the allowed write scope. Out-of-scope edits = Strike-1.
- Do NOT touch any of the 17 sovereign-locked constants. Verify on each edit.
- Idempotency: BEFORE editing, check if the file already conforms to acceptance criteria.
  If yes, write MECHANIC-OUTPUT.md citing existing conformance and exit cleanly.
- Run the checks the dispatch requests. Report what you ran, not what you wish you ran.
- Pair version bumps: every Version change must update Last Modified in the same edit.
  Version field appears in 3 locations (frontmatter, section 1 Identity, Document Control) — bump all 3.
- Final action MUST be writing MECHANIC-OUTPUT.md. The runner keys completion on this file.

==============================================================================
REQUIRED OUTPUT — MECHANIC-OUTPUT.md must contain
==============================================================================
- status: completed | PLAN_BOOK_INCOMPLETE | BLOCKED
- Atlas Step 0 sections cited
- Plan Book reference
- Files changed (full paths)
- Tests/checks run + result
- proposed_slots: block (if any artifact had NEW_SLOT_NEEDED disposition)
- Evidence (log paths, command output, hashes)
- Blockers (if any)
- Final line: "Mechanic complete. Auditor handoff ready. Mechanic does not self-audit."
PROMPT
  # Finding 1 (BLOCKER): inject STRIKE-CONTEXT.md into required read set if present
  local strike_ctx="$run_dir/STRIKE-CONTEXT.md"
  if [[ -f "$strike_ctx" ]]; then
    cat >> "$prompt" <<STRIKE_INJECT

==============================================================================
STRIKE CONTEXT — READ THIS FIRST (repair run)
==============================================================================
REQUIRED READ: $strike_ctx

You are in a STRIKE REPAIR run. Read STRIKE-CONTEXT.md before any other file.
Repair ONLY the FAIL findings listed in that file. Do NOT redesign scope.
Do NOT address findings not listed. Close listed FAILs in order.
STRIKE_INJECT
  fi
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
  local v2_atlas="$ROOT/../imo-creator-v2/atlas"
  local gate_runner_ref
  gate_runner_ref="$(agent_path "$ROOT/factory/imo-creator/070-four-brain/garage/gate-runner.py")"
  cat > "$prompt" <<PROMPT
ROLE: AUDITOR
PROCESS: 070 Four-Brain
BAR: $bar_id
ENGINE: Codex (DIFFERENT inference engine than Mechanic — Aviation Model: mechanic ≠ auditor).

You are the Auditor. Per Atlas (FOUR_BRAIN_AVIATION.md §75-94 + four-brain-doctrine-gate.yaml#determinism_gate), gate predicates are evaluated DETERMINISTICALLY by gate-runner.py. You do NOT evaluate them inferentially. Your role is:
  1. Invoke the deterministic gate runner.
  2. Tail-arbitrate W-7 (disposition sanity) — the ONE Atlas-sanctioned LLM-judgment gate.
  3. Explain any FAIL with a diagnostic narrative, citing the runner's evidence.
  4. Emit the verdict.

==============================================================================
REQUIRED READ SET
==============================================================================
Inputs to audit:
- $plan_ref                                              (Plan Book — Planner output)
- $dispatch_ref                                          (Foreman dispatch)
- $mechanic_ref                                          (Mechanic completion report)

Doctrine (read for context only — DO NOT evaluate predicates from this; the runner does):
- $v2_atlas/manifests/four-brain-doctrine-gate.yaml      (predicate source of truth — read by gate-runner.py, not by you)
- $v2_atlas/constants/AUDITOR_ROLE.md §7b                (W-7 sanity-check criteria)
- $v2_atlas/constants/MISSION_CONTROL.md §10             (W-7 reference: WIRE/EXEMPT/NEW_SLOT disposition contract)
- $v2_atlas/ATLAS.md §6 Governance, §4.5 Repair SOP

Process context:
- $process_ut_ref
- $four_brain_ref

==============================================================================
STEP 1 — RUN THE DETERMINISTIC GATE RUNNER (mandatory, first action)
==============================================================================
Invoke the runner against this BAR's artifacts:

  python "$gate_runner_ref" \\
    --bar-id "$bar_id" \\
    --audited-yaml <path to .yaml under audit> \\
    --audited-md <path to .md under audit> \\
    --output-format json \\
    --deterministic-only

The runner reads predicates from four-brain-doctrine-gate.yaml, evaluates each gate by parse + compare (no LLM), and emits JSON:
  {
    "verdict": "PASS" | "FAIL",
    "p_value": 1 | 0,
    "gates_passed": [...],
    "gates_failed": [{"id": ..., "evidence": ..., "strike_target": ...}, ...],
    "deferred_to_tail": ["W-7"],
    "diagnostic_vector": [...]
  }

Capture the runner's JSON output. This IS your deterministic verdict for G01-G12 + W-1..W-6 + Rung-1..Rung-8. Do NOT re-evaluate these gates inferentially. Atlas: ai_on_spine_forbidden.

==============================================================================
STEP 2 — W-7 TAIL ARBITRATION (the ONLY gate you evaluate by judgment)
==============================================================================
The runner defers W-7 to you because it is the one gate that requires architectural judgment, not parse + compare. Per AUDITOR_ROLE.md §7b:

  W-7 — Disposition sanity check: for each entry in the Plan Book's
        mission_control_wiring section, did the Planner make a defensible
        architectural call?

For each artifact's disposition:
  - WIRE → does the chosen slot's render_mode and data_source contract actually fit this artifact's nature, or is the wire forced?
  - EXEMPT → would a sovereign reasonably want this surfaced in Mission Control? If the rationale doesn't hold against that question, the disposition is indefensible.
  - NEW_SLOT_NEEDED → is the proposed slot structurally coherent (heir_id + ctb_position + render_mode from UI_STYLE_GUIDE.md + data_source contract)?

Emit W-7 verdict: PASS or FAIL with one-sentence rationale per artifact.

W-7 strike target on FAIL: Planner.

==============================================================================
STEP 3 — DIAGNOSTIC NARRATIVE (only if any gate failed)
==============================================================================
If the runner returned any FAIL, write a brief diagnostic explanation citing the runner's evidence string and the Atlas source for the predicate. Do NOT re-evaluate the predicate. Do NOT add findings the runner didn't catch — Atlas envelope is the runner's gates plus W-7. Anything else is out-of-scope.

==============================================================================
STEP 4 — EMIT AUDIT-VERDICT.md
==============================================================================
Write to: $verdict_ref

First line MUST be exactly:
  VERDICT: P=1
OR
  VERDICT: P=0

Body:
- Runner JSON output (verbatim, in a code block)
- W-7 verdict per artifact with rationale
- Combined verdict: P=1 only if runner verdict=PASS AND W-7=PASS for all artifacts; else P=0
- Diagnostic narrative for each FAIL (runner findings + W-7 findings)
- Strike target per FAIL (per AUDITOR_ROLE.md §7b — the runner emits this; carry forward)

==============================================================================
RULES
==============================================================================
- Do NOT build. Do NOT modify any artifact. Audit-only.
- You are a different inference engine than the Mechanic.
- Predicates are evaluated by gate-runner.py. You do NOT re-evaluate them. (Atlas: ai_on_spine_forbidden — FOUR_BRAIN_AVIATION.md §75-94.)
- W-7 is the only gate you arbitrate by judgment. All other gates: cite the runner.
- Strike-1 (first FAIL) → Mechanic re-runs against corrected dispatch (or Planner re-drafts if W-2/W-7).
- Strike-2 (second FAIL on same BAR) → escalate to Opus mechanic.
- Strike-3 (third FAIL) → Troubleshoot/Train, NOT another repair. Plan Book is wrong; rewrite the blueprint.
- Do not fix findings. Audit only.
- P=1 requires runner=PASS AND W-7=PASS. P=0 if either fails.
PROMPT
  echo "$prompt"
}

update_status() {
  # Updates the garage_status field in an intake YAML.
  # Supports BOTH legacy nested form (garage_status: under garage: parent block)
  # AND v2.0.0 thin form (garage_status: at root level). Without this, v2.0.0
  # intakes silently no-op and the pipeline drifts out of sync with reality.
  local file="$1"
  local from="$2"
  local to="$3"
  local current
  current="$(grep "garage_status:" "$file" | tail -n 1 | sed 's/.*garage_status:[[:space:]]*//')"
  if [[ "$current" != "$from" ]]; then
    echo "Expected status $from in $file (got: $current)" >&2
    return 1
  fi
  # Try nested-block form first (legacy), then root-level form (v2.0.0).
  if grep -qE "^garage:" "$file"; then
    perl -0pi -e "s/(^garage:\n(?:  .*\n)*?  garage_status: )$from/\${1}$to/m" "$file"
  else
    perl -pi -e "s/^(garage_status:[[:space:]]+)$from\b/\${1}$to/" "$file"
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
  # G-19 doctrine (atlas/constants/MISSION_CONTROL.md §10.4):
  # Sovereign cannot gate the pipeline mid-flight. The only sovereign
  # touchpoints are template-drop (input boundary) and Auditor verdict
  # (output boundary). This gate is artifact-exists ONLY — all Plan Book
  # quality judgment belongs to the Auditor per Aviation Model.
  local bar_id="$1"
  local run_dir="$2"
  local plan="$ROOT/docs/plans/$bar_id/PLAN-BOOK.md"
  local checklist="$run_dir/APPROVAL-CHECKLIST-PLAN_BOOK_SIGNED.md"

  mkdir -p "$run_dir"

  cat > "$checklist" <<EOF
# Auto-Advance: PLAN_BOOK_SIGNED (G-19 compliant)

BAR: $bar_id
Auto-advanced at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Plan Book: $plan

## Mechanical Check (artifact exists only — no sovereign content judgment)

$(check_line "$([[ -f "$plan" ]] && echo true || echo false)" "Plan Book artifact exists at expected path.")

## G-19 Doctrine Note

Plan Book quality (Atlas citations, P=1 definition, work orders, BS Law conformance,
Mission Control wiring section, etc.) is verified by the **Auditor** at the output
boundary, not by a sovereign mid-pipeline gate. This auto-advance preserves the
Aviation Model: mechanic ≠ auditor; the construction crew does not certify itself.

If the Plan Book is structurally insufficient, the Auditor returns FAIL → Strike-1
→ Mechanic re-runs against corrected Plan Book.

EOF

  if [[ ! -f "$plan" ]]; then
    {
      echo "## Verdict"
      echo
      echo "BLOCKED: Plan Book file does not exist. Planner did not write the artifact."
    } >> "$checklist"
    echo "Plan Book artifact missing: $plan" >&2
    return 1
  fi

  {
    echo "## Verdict"
    echo
    echo "AUTO-ADVANCE: Plan Book exists. Pipeline advances PLANNER_RUNNING → PLAN_BOOK_SIGNED → FOREMAN_RUNNING per G-19."
  } >> "$checklist"

  echo "$checklist"
}

approve_foreman_dispatch_gate() {
  # G-19 doctrine: artifact-exists ONLY. All dispatch quality judgment
  # (Atlas citations, write scope, work orders, role separation, etc.)
  # is the Auditor's job at the output boundary. Mid-pipeline content
  # gates are forbidden per atlas/constants/MISSION_CONTROL.md §10.4.
  local bar_id="$1"
  local run_dir="$2"
  local dispatch="$run_dir/FOREMAN-DISPATCH.md"
  local checklist="$run_dir/APPROVAL-CHECKLIST-FOREMAN_DISPATCHED.md"

  cat > "$checklist" <<EOF
# Auto-Advance: FOREMAN_DISPATCHED (G-19 compliant)

BAR: $bar_id
Auto-advanced at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Foreman Dispatch: $dispatch

## Mechanical Check (artifact exists only)

$(check_line "$([[ -f "$dispatch" ]] && echo true || echo false)" "Foreman dispatch artifact exists.")

## G-19 Doctrine Note

Foreman dispatch quality is verified by the Auditor downstream. Mid-pipeline
content judgment (Atlas citations, write scope declarations, work order
structure, Aviation Model role separation) is forbidden per G-19. Quality
issues surface as Auditor strikes, not pipeline halts.

EOF

  if [[ ! -f "$dispatch" ]]; then
    {
      echo "## Verdict"
      echo
      echo "BLOCKED: Foreman dispatch file does not exist."
    } >> "$checklist"
    echo "Foreman dispatch artifact missing: $dispatch" >&2
    return 1
  fi

  {
    echo "## Verdict"
    echo
    echo "AUTO-ADVANCE: Foreman dispatch exists. Pipeline advances FOREMAN_RUNNING → FOREMAN_DISPATCHED → MECHANIC_RUNNING per G-19."
  } >> "$checklist"

  echo "$checklist"
}

approve_mechanic_output_gate() {
  # G-19 doctrine: artifact-exists ONLY. All Mechanic output quality
  # judgment (file lists, tests, Plan Book references, BAR-specific
  # spine checks like FCE-00..FCE-14, locked-engine cleanliness) is
  # the Auditor's job at the output boundary. Per atlas/constants/
  # MISSION_CONTROL.md §10.4 + Aviation Model: mechanic != auditor.
  local bar_id="$1"
  local run_dir="$2"
  local output="$run_dir/MECHANIC-OUTPUT.md"
  local checklist="$run_dir/APPROVAL-CHECKLIST-MECHANIC_DONE.md"

  cat > "$checklist" <<EOF
# Auto-Advance: MECHANIC_DONE (G-19 compliant)

BAR: $bar_id
Auto-advanced at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Mechanic Output: $output

## Mechanical Check (artifact exists only)

$(check_line "$([[ -f "$output" ]] && echo true || echo false)" "Mechanic output artifact exists.")

## G-19 Doctrine Note

Mechanic output quality is verified by the **Auditor** (different inference
engine per Aviation Model). Mid-pipeline content gates that re-judge
Mechanic work would either duplicate the Auditor's job or substitute
sovereign approval for the Auditor's verdict — both forbidden by G-19.

BAR-specific quality predicates (e.g., FCE spine endpoints, locked-engine
cleanliness, file change manifest format) belong in:
- the Plan Book's auditor_packet section, OR
- atlas/manifests/four-brain-doctrine-gate.yaml gate definitions

NOT in this script's mid-pipeline gate.

EOF

  if [[ ! -f "$output" ]]; then
    {
      echo "## Verdict"
      echo
      echo "BLOCKED: Mechanic output file does not exist."
    } >> "$checklist"
    echo "Mechanic output artifact missing: $output" >&2
    return 1
  fi

  {
    echo "## Verdict"
    echo
    echo "AUTO-ADVANCE: Mechanic output exists. Pipeline advances MECHANIC_RUNNING → MECHANIC_DONE → AUDITOR_RUNNING per G-19."
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
  # Finding 2: Mechanic must be able to edit Mission Control + worker code in sibling repo
  # Add --add-dir imo-creator-v2 to Mechanic's allowed directory scope
  local sibling_repo
  sibling_repo="$(cd "$ROOT/../imo-creator-v2" 2>/dev/null && pwd || true)"
  if command -v powershell.exe >/dev/null 2>&1 && command -v cygpath >/dev/null 2>&1; then
    local prompt_win root_win output_win sibling_win
    prompt_win="$(cygpath -w "$prompt")"
    root_win="$(cygpath -w "$ROOT")"
    output_win="$(cygpath -w "$output")"
    local add_dir_flags
    add_dir_flags="--add-dir '$(ps_escape "$root_win")'"
    if [[ -n "$sibling_repo" ]]; then
      sibling_win="$(cygpath -w "$sibling_repo")"
      add_dir_flags="$add_dir_flags --add-dir '$(ps_escape "$sibling_win")'"
    fi
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "\
\$ErrorActionPreference = 'Stop'; \
Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue; \
Remove-Item Env:\ANTHROPIC_AUTH_TOKEN -ErrorAction SilentlyContinue; \
\$env:CLAUDE_CODE_GIT_BASH_PATH = 'C:\Program Files\Git\bin\bash.exe'; \
\$promptText = Get-Content -Raw -LiteralPath '$(ps_escape "$prompt_win")'; \
\$result = \$promptText | & '$(ps_escape "$CLAUDE_CODE_PS1")' --print --model '$(ps_escape "$model")' --permission-mode acceptEdits $add_dir_flags; \
\$code = \$LASTEXITCODE; \
if (\$null -ne \$result) { \$result | Set-Content -LiteralPath '$(ps_escape "$output_win")' -NoNewline; } \
exit \$code"
  else
    local add_dir_args=("--add-dir" "$ROOT")
    if [[ -n "$sibling_repo" ]]; then
      add_dir_args+=("--add-dir" "$sibling_repo")
    fi
    claude --print --model "$model" --permission-mode acceptEdits "${add_dir_args[@]}" < "$prompt" > "$output"
  fi
}

run_codex_cli() {
  local model="$1"
  local prompt="$2"
  local output="$3"
  local rc=0
  # Codex CLI updated 2026-05-06: --ask-for-approval renamed; --sandbox + bypass
  # combined into single flag --dangerously-bypass-approvals-and-sandbox per
  # `codex exec --help`. Auditor needs read across Atlas + run dir + working
  # tree + write of AUDIT-VERDICT.md. Sovereign-authorized dispatch.
  #
  # CRITICAL: stdin redirected from /dev/null. Per codex exec --help, "If
  # stdin is piped and a prompt is also provided, stdin is appended as a
  # <stdin> block". When run from bash background commands, stdin is open
  # (not piped, not closed) and Codex hangs forever showing "Reading
  # additional input from stdin..." Surfaced on BAR-MC-FOUR-BRAIN-WIRE
  # first Auditor run 2026-05-06.
  codex exec --cd "$ROOT" --dangerously-bypass-approvals-and-sandbox --model "$model" "$(cat "$prompt")" > "$output" < /dev/null || rc=$?
  return "$rc"
}

# run_planner_for_bar BAR-ID [--execute] [--auto-continue] [--defer-lbb] [--planner-model MODEL]
# BAR-scoped planner rerun: runs the Planner for an explicit bar_id (already claimed/running),
# bypassing the READY_FOR_PLANNER scan used by run_once. Used by run_strike1 for Planner-branch reruns.
run_planner_for_bar() {
  local bar_id="$1"
  shift || true
  local execute="false"
  local auto_continue="true"
  local defer_lbb="false"
  local planner_model="opus"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --execute) execute="true"; shift ;;
      --auto-continue) auto_continue="true"; shift ;;
      --defer-lbb) defer_lbb="true"; shift ;;
      --planner-model) planner_model="${2:-opus}"; shift 2 ;;
      *) echo "Unknown run_planner_for_bar option: $1" >&2; exit 2 ;;
    esac
  done
  require_bar_id "$bar_id"
  local intake_yaml="$INBOX/$bar_id/planner-intake.yaml"
  local ts run_dir
  ts="$(date -u +"%Y%m%dT%H%M%SZ")"
  run_dir="$RUNS/$bar_id/$ts"
  mkdir -p "$run_dir"
  local prompt plan_path
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
    echo "origin: run_planner_for_bar (strike reroute)"
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
          log_transition "$bar_id" "$run_dir" "planner" "approval-check" "PLANNER_RUNNING" "BLOCKED" "$plan_path" "$run_dir/APPROVAL-CHECKLIST-PLAN_BOOK_SIGNED.md" "blocked" "Plan Book approval checklist failed (strike reroute)."
          update_status "$intake_yaml" "PLANNER_RUNNING" "BLOCKED"
          return 1
        fi
        update_status "$intake_yaml" "PLANNER_RUNNING" "PLAN_BOOK_SIGNED"
        log_transition "$bar_id" "$run_dir" "planner" "approval-check" "PLANNER_RUNNING" "PLAN_BOOK_SIGNED" "$plan_path" "$run_dir/APPROVAL-CHECKLIST-PLAN_BOOK_SIGNED.md" "done" "Auto-continue signed Plan Book after strike reroute checklist pass."
      else
        update_status "$intake_yaml" "PLANNER_RUNNING" "REVIEW_PLAN_BOOK"
        log_transition "$bar_id" "$run_dir" "planner" "dispatch" "PLANNER_RUNNING" "REVIEW_PLAN_BOOK" "$plan_path" "" "done" "Planner (strike reroute) produced Plan Book; review required."
      fi
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      write_final_pointer "$bar_id" "$(current_status "$bar_id")" "$plan_path" "$run_dir" > "$run_dir/final-product-pointer.txt"
      echo "$plan_path"
    else
      update_status "$intake_yaml" "PLANNER_RUNNING" "BLOCKED"
      echo "Planner (strike reroute) completed but did not create Plan Book: $plan_path" >&2
      return 1
    fi
  else
    update_status "$intake_yaml" "PLANNER_RUNNING" "BLOCKED"
    echo "Planner CLI failed (strike reroute). See $run_dir" >&2
    return 1
  fi
}

run_once() {
  local execute="false"
  local auto_continue="true"   # G-19 default: pipeline auto-advances; sovereign gates only at template-drop and Auditor verdict
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
  local auto_continue="true"   # G-19 default: pipeline auto-advances; sovereign gates only at template-drop and Auditor verdict
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
  local auto_continue="true"   # G-19 default: pipeline auto-advances; sovereign gates only at template-drop and Auditor verdict
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
  # Finding 3: snapshot forbidden-path hashes BEFORE Mechanic CLI runs so
  # assert_no_locked_constants_touched compares run-deltas only, not ambient workspace state.
  snapshot_forbidden_baseline "$run_dir" > /dev/null
  local cli_rc=0
  run_claude_cli "$mechanic_model" "$prompt" "$run_dir/mechanic-output.raw.md" || cli_rc=$?
  # F-001: persist mechanic model for engine separation check in run_auditor (G12)
  echo "$mechanic_model" > "$run_dir/.four_brain_mechanic_model"
  # F-003: assert no sovereign-locked constants were touched by the mechanic CLI
  if ! assert_no_locked_constants_touched "$run_dir"; then
    update_status "$intake_yaml" "MECHANIC_RUNNING" "BLOCKED"
    log_transition "$bar_id" "$run_dir" "mechanic" "edit" "MECHANIC_RUNNING" "BLOCKED" "$run_dir/mechanic-output.raw.md" "" "failed" "Mechanic touched sovereign-locked constants (G12 violation). See LOCKED-CONSTANTS-VIOLATION.txt."
    return 1
  fi
  # Fallback per Atlas §4.5: if Sonnet returned the completion report as stdout
  # (captured to mechanic-output.raw.md) but didn't use the Write tool to create
  # MECHANIC-OUTPUT.md at the canonical path, promote raw.md. Without this, the
  # script saw "no output" → BLOCKED even when Mechanic actually completed work.
  # Surfaced on BAR-MC-FOUR-BRAIN-WIRE first run 2026-05-06.
  if [[ ! -f "$run_dir/MECHANIC-OUTPUT.md" && -s "$run_dir/mechanic-output.raw.md" ]]; then
    cp "$run_dir/mechanic-output.raw.md" "$run_dir/MECHANIC-OUTPUT.md"
  fi
  if [[ -f "$run_dir/MECHANIC-OUTPUT.md" ]]; then
    if [[ "$cli_rc" -ne 0 ]]; then
      log_transition "$bar_id" "$run_dir" "mechanic" "cli-soft-fail" "MECHANIC_RUNNING" "MECHANIC_RUNNING" "$run_dir/mechanic-output.raw.md" "" "done" "CLI rc=$cli_rc but mechanic output artifact exists; proceeding."
    fi
    if ! write_lbb_transition "$bar_id" "mechanic" "edit" "$run_dir" "$defer_lbb" > "$run_dir/lbb-mechanic-path.txt"; then
      update_status "$intake_yaml" "MECHANIC_RUNNING" "BLOCKED"
      return 1
    fi
    # Finding 2: emit artifact-level wiring LBB rows for W-5 mission-control-wiring evidence.
    # Parse MECHANIC-OUTPUT.md for mission_control_wiring artifacts and write one
    # wiring-tagged LBB row per produced/modified artifact.
    if grep -q "mission_control_wiring" "$run_dir/MECHANIC-OUTPUT.md" 2>/dev/null; then
      local wiring_artifacts
      mapfile -t wiring_artifacts < <(
        grep -A 999 "mission_control_wiring" "$run_dir/MECHANIC-OUTPUT.md" 2>/dev/null \
          | grep -E "^\s*-\s+\S+" | sed 's/^\s*-\s*//' | head -20 || true
      )
      local wiring_idx=0
      for artifact_path in "${wiring_artifacts[@]}"; do
        [[ -z "$artifact_path" ]] && continue
        wiring_idx=$(( wiring_idx + 1 ))
        local wiring_output="$run_dir/LBB-mechanic-wiring-${wiring_idx}.json"
        if [[ -x "$LBB_SCRIPT" ]]; then
          "$LBB_SCRIPT" \
            --bar-id "$bar_id" \
            --role "mechanic" \
            --action "wiring" \
            --subject processes \
            --evidence "$run_dir" \
            --tags "mission-control-wiring" \
            > "$wiring_output" || true
        elif [[ "${FOUR_BRAIN_LOCAL_DEV:-false}" == "true" ]]; then
          local wts
          wts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
          cat > "$wiring_output" <<EOF
{
  "record_id": "deferred-wiring-$(date -u +%s)-${wiring_idx}-$bar_id",
  "bar_id": "$bar_id",
  "role": "mechanic",
  "action": "wiring",
  "evidence_hash": null,
  "atlas_sections_consulted": "FOUR_BRAIN_AVIATION,MECHANIC_ROLE,MISSION_CONTROL,ATLAS",
  "timestamp": "$wts",
  "sovereign_ref": "imo-creator",
  "subject_id": "processes",
  "orbt_mode": "BUILD",
  "gate_verdicts": null,
  "notes": "W-5 artifact wiring: $artifact_path (DEFERRED_LOCAL_ONLY)"
}
EOF
        fi
      done
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
  # F-001: engine separation guard (G12) — auditor model must differ from mechanic model
  if [[ -f "$run_dir/.four_brain_mechanic_model" ]]; then
    local mechanic_model_on_disk
    mechanic_model_on_disk="$(cat "$run_dir/.four_brain_mechanic_model")"
    if [[ "$auditor_model" == "$mechanic_model_on_disk" ]]; then
      echo "[four-brain] BLOCKED: auditor_model ($auditor_model) == mechanic_model ($mechanic_model_on_disk). G12 engine separation violated. Aviation Model: mechanic != auditor." >&2
      return 1
    fi
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
  # F-007: auto_continue allows FOREMAN_RUNNING→FOREMAN_DISPATCHED and
  # MECHANIC_RUNNING→MECHANIC_DONE without pausing at REVIEW_* gates.
  # AUDITOR_RUNNING always lands at REVIEW_AUDIT_VERDICT per G-19 doctrine
  # (sovereign must sign the audit verdict — no auto-advance past that gate).
  local auto_continue="false"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --defer-lbb) defer_lbb="true"; shift ;;
      --auto-continue) auto_continue="true"; shift ;;
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
      if [[ "$auto_continue" == "true" ]]; then
        update_status "$intake_yaml" "FOREMAN_RUNNING" "FOREMAN_DISPATCHED"
        log_transition "$bar_id" "$run_dir" "foreman" "reconcile" "FOREMAN_RUNNING" "FOREMAN_DISPATCHED" "$run_dir/FOREMAN-DISPATCH.md" "" "done" "Reconciled from interrupted Foreman run; auto-continue."
      else
        update_status "$intake_yaml" "FOREMAN_RUNNING" "REVIEW_FOREMAN_DISPATCH"
        log_transition "$bar_id" "$run_dir" "foreman" "reconcile" "FOREMAN_RUNNING" "REVIEW_FOREMAN_DISPATCH" "$run_dir/FOREMAN-DISPATCH.md" "" "done" "Reconciled from interrupted Foreman run."
      fi
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
      if [[ "$auto_continue" == "true" ]]; then
        update_status "$intake_yaml" "MECHANIC_RUNNING" "MECHANIC_DONE"
        log_transition "$bar_id" "$run_dir" "mechanic" "reconcile" "MECHANIC_RUNNING" "MECHANIC_DONE" "$run_dir/MECHANIC-OUTPUT.md" "" "done" "Reconciled from interrupted Mechanic run; auto-continue."
      else
        update_status "$intake_yaml" "MECHANIC_RUNNING" "REVIEW_MECHANIC_OUTPUT"
        log_transition "$bar_id" "$run_dir" "mechanic" "reconcile" "MECHANIC_RUNNING" "REVIEW_MECHANIC_OUTPUT" "$run_dir/MECHANIC-OUTPUT.md" "" "done" "Reconciled from interrupted Mechanic run."
      fi
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
        # G-19 mandatory gate: AUDITOR_RUNNING always lands at REVIEW_AUDIT_VERDICT.
        # No --auto-continue bypass here — sovereign must sign the audit verdict.
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
  local auto_continue="true"   # G-19 default: pipeline auto-advances; sovereign gates only at template-drop and Auditor verdict
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

# F-003 (Finding 3): write_strike_context — build STRIKE-CONTEXT.md from latest AUDIT-VERDICT.md
# Called by run_strike1 BEFORE re-firing Planner or Mechanic so the context is in place
# when the prompt is written. The prompt writers (write_mechanic_prompt, write_planner_prompt)
# check for this file and append it to the required read set.
write_strike_context() {
  local bar_id="$1"
  local run_dir="$2"
  local strike_count="$3"
  local verdict_file="$run_dir/AUDIT-VERDICT.md"
  local context_file="$run_dir/STRIKE-CONTEXT.md"
  local commit_sha
  commit_sha="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")"
  {
    echo "# STRIKE-$strike_count CONTEXT — $bar_id"
    echo ""
    echo "Strike count: $strike_count"
    echo "Verdict source: $verdict_file"
    echo "Commit being repaired against: $commit_sha"
    echo ""
    echo "## FAIL findings to address (repair these specifically — do NOT redesign scope)"
    echo ""
    if [[ -f "$verdict_file" ]]; then
      # Extract FAIL finding blocks — lines between ### N) and the next ### or end
      awk '/^### [0-9]+\)/{found=1} found && /FAIL|Strike target/{print}' "$verdict_file" || true
      echo ""
      echo "## Strike target table"
      grep -i "strike target:" "$verdict_file" || echo "(no strike-target lines found)"
    else
      echo "(AUDIT-VERDICT.md not found at $verdict_file)"
    fi
  } > "$context_file"
  echo "$context_file"
}

# F-001 (Finding 1) + F-002 (Finding 2): run_strike1 — Strike-1 repair-and-re-audit loop
# Reads latest AUDIT-VERDICT.md, parses strike targets (Planner vs Mechanic),
# writes STRIKE-CONTEXT.md, routes Planner-targeted failures to Planner re-draft,
# routes Mechanic-targeted failures to Mechanic rerun with failure context injected.
# Increments strike_count in planner-intake.yaml.
# At Strike-3, sets status to TROUBLESHOOT_TRAIN and halts (no further auto-run).
# FOUR_BRAIN_AVIATION v1.3.0 §Strike system.
run_strike1() {
  local bar_id="${1:-}"
  local defer_lbb="false"
  shift || true
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --defer-lbb) defer_lbb="true"; shift ;;
      *) echo "Unknown strike1 option: $1" >&2; exit 2 ;;
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
  # Finding 6 (MEDIUM): Canonical operational path is garage_status.strike_count ONLY.
  # No legacy root-level fallback. If the canonical path is missing, the intake is malformed
  # and we halt rather than silently promote a root-level field.
  local strike_count=0
  if grep -q "^  strike_count:" "$intake_yaml" 2>/dev/null; then
    # Canonical nested path: garage_status.strike_count
    strike_count="$(grep "^  strike_count:" "$intake_yaml" | awk '{print $2}')"
  else
    echo "[four-brain] BLOCKED: intake YAML at $intake_yaml has no 'garage_status.strike_count' field (canonical path ^  strike_count: not found)." >&2
    echo "[four-brain] Remediation: ensure intake was created from planner-intake-template.yaml which always includes garage_status.strike_count." >&2
    return 1
  fi
  # Remove any stale root-level strike_count field (Finding 6: eliminate ambiguous duplicate)
  if grep -q "^strike_count:" "$intake_yaml" 2>/dev/null; then
    sed -i "/^strike_count:/d" "$intake_yaml"
    echo "[four-brain] Removed stale root-level strike_count from $intake_yaml (Finding 6 cleanup)." >&2
  fi
  strike_count=$((strike_count + 1))
  # Write updated value to canonical garage_status.strike_count only
  sed -i "s/^  strike_count:.*$/  strike_count: $strike_count/" "$intake_yaml"
  echo "[four-brain] Strike $strike_count recorded for $bar_id." >&2
  # Strike-3: halt — sovereign must investigate structural failure
  if [[ "$strike_count" -ge 3 ]]; then
    update_status "$intake_yaml" "$(current_status "$bar_id")" "TROUBLESHOOT_TRAIN"
    log_transition "$bar_id" "$run_dir" "foreman" "reconcile-fail" "$(current_status "$bar_id")" "TROUBLESHOOT_TRAIN" "$intake_yaml" "" "failed" "Strike-3: BAR moved to TROUBLESHOOT_TRAIN. Structural investigation required. Pipeline halted."
    echo "[four-brain] Strike-3 on $bar_id: status set to TROUBLESHOOT_TRAIN. No further auto-repair. Sovereign intervention required." >&2
    return 1
  fi

  # F-001: Parse latest AUDIT-VERDICT.md to determine Planner vs Mechanic strike targets
  local verdict_file="$run_dir/AUDIT-VERDICT.md"
  local has_planner_target=false
  local has_mechanic_target=false
  if [[ -f "$verdict_file" ]]; then
    if grep -qi "strike target:.*planner" "$verdict_file"; then
      has_planner_target=true
    fi
    if grep -qi "strike target:.*mechanic" "$verdict_file"; then
      has_mechanic_target=true
    fi
  else
    # Finding 5: halt as BLOCKED — do NOT default to Mechanic rerun on missing/unparseable verdict
    echo "[four-brain] BLOCKED: AUDIT-VERDICT.md not found at $verdict_file." >&2
    echo "[four-brain] Remediation: ensure Auditor writes AUDIT-VERDICT.md with 'Strike target:' lines before run_strike1 is called." >&2
    update_status "$intake_yaml" "$(current_status "$bar_id" 2>/dev/null || echo "UNKNOWN")" "BLOCKED" 2>/dev/null || true
    return 1
  fi
  if [[ "$has_planner_target" == "false" && "$has_mechanic_target" == "false" ]]; then
    # Finding 5: halt as BLOCKED when verdict file exists but has no parseable strike-target lines
    echo "[four-brain] BLOCKED: AUDIT-VERDICT.md found at $verdict_file but contains no parseable 'Strike target:' lines." >&2
    echo "[four-brain] Remediation: Auditor must declare at least one 'Strike target: Mechanic' or 'Strike target: Planner' line in the verdict." >&2
    update_status "$intake_yaml" "$(current_status "$bar_id" 2>/dev/null || echo "UNKNOWN")" "BLOCKED" 2>/dev/null || true
    return 1
  fi
  echo "[four-brain] Strike $strike_count target parse: planner=$has_planner_target mechanic=$has_mechanic_target" >&2

  # F-003: Write STRIKE-CONTEXT.md BEFORE re-firing any role so prompts have the context
  local strike_context_file
  strike_context_file="$(write_strike_context "$bar_id" "$run_dir" "$strike_count")"
  echo "[four-brain] Strike context written: $strike_context_file" >&2

  # Strike-1 or Strike-2: route based on parsed targets
  local mechanic_model="sonnet"
  local auditor_model="gpt-5.3-codex"
  if [[ "$strike_count" -ge 2 ]]; then
    # Strike-2: escalate Mechanic to Opus per FOUR_BRAIN_AVIATION §Strike system
    mechanic_model="opus"
    echo "[four-brain] Strike-2: escalating Mechanic to $mechanic_model." >&2
  fi

  if [[ "$has_planner_target" == "true" ]]; then
    # F-001: Planner-targeted failures — route to Planner re-draft
    echo "[four-brain] Planner-targeted failures detected (W-2/W-7). Routing to Planner re-draft." >&2
    update_status "$intake_yaml" "$(current_status "$bar_id")" "PLANNER_RUNNING"
    log_transition "$bar_id" "$run_dir" "foreman" "reconcile-fail" "BLOCKED" "PLANNER_RUNNING" "$intake_yaml" "" "done" "Strike-$strike_count: Planner-targeted failures; routing to Planner re-draft."
    # write_planner_prompt checks for STRIKE-CONTEXT.md and appends to read set
    # Finding 1: run_once scans READY_FOR_PLANNER and rejects an explicit bar_id.
    # Use run_planner_for_bar which takes an explicit bar_id directly.
    local planner_rerun_args=("$bar_id" --execute)
    if [[ "$defer_lbb" == "true" ]]; then planner_rerun_args+=(--defer-lbb); fi
    if ! run_planner_for_bar "${planner_rerun_args[@]}"; then
      echo "[four-brain] Planner re-draft failed for $bar_id." >&2
      return 1
    fi
    # G-19: after Planner re-draft, auto-advance Foreman → Mechanic → Auditor
    echo "[four-brain] Planner re-draft complete. Auto-advancing Foreman..." >&2
    local foreman_args=("$bar_id" --execute --auto-continue)
    if [[ "$defer_lbb" == "true" ]]; then foreman_args+=(--defer-lbb); fi
    if ! run_foreman "${foreman_args[@]}"; then
      echo "[four-brain] Foreman auto-advance failed for $bar_id after Planner re-draft." >&2
      return 1
    fi
    echo "[four-brain] Re-running Mechanic ($mechanic_model) after Planner re-draft..." >&2
    local mechanic_rerun_args=("$bar_id" --execute --mechanic-model "$mechanic_model")
    if [[ "$defer_lbb" == "true" ]]; then mechanic_rerun_args+=(--defer-lbb); fi
    if ! run_mechanic "${mechanic_rerun_args[@]}"; then
      echo "[four-brain] Mechanic re-run failed for $bar_id after Planner re-draft." >&2
      return 1
    fi
  else
    # F-001: Mechanic-targeted failures only — reset to MECHANIC_RUNNING with context
    update_status "$intake_yaml" "$(current_status "$bar_id")" "MECHANIC_RUNNING"
    log_transition "$bar_id" "$run_dir" "foreman" "reconcile-fail" "BLOCKED" "MECHANIC_RUNNING" "$intake_yaml" "" "done" "Strike-$strike_count repair: resetting to MECHANIC_RUNNING with model=$mechanic_model."
    echo "[four-brain] Re-running Mechanic ($mechanic_model) for $bar_id (Strike $strike_count)..." >&2
    # write_mechanic_prompt checks for STRIKE-CONTEXT.md and appends it to the read set
    local mechanic_rerun_args=("$bar_id" --execute --mechanic-model "$mechanic_model")
    if [[ "$defer_lbb" == "true" ]]; then mechanic_rerun_args+=(--defer-lbb); fi
    if ! run_mechanic "${mechanic_rerun_args[@]}"; then
      echo "[four-brain] Mechanic re-run failed for $bar_id." >&2
      return 1
    fi
  fi

  echo "[four-brain] Re-running Auditor ($auditor_model) for $bar_id (Strike $strike_count)..." >&2
  local auditor_rerun_args=("$bar_id" --execute --auditor-model "$auditor_model")
  if [[ "$defer_lbb" == "true" ]]; then auditor_rerun_args+=(--defer-lbb); fi
  if ! run_auditor "${auditor_rerun_args[@]}"; then
    echo "[four-brain] Auditor re-run failed for $bar_id." >&2
    return 1
  fi
  echo "[four-brain] Strike-$strike_count repair-and-re-audit complete for $bar_id." >&2
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
  strike1)
    bar_id="${2:-}"
    shift 2 || true
    run_strike1 "$bar_id" "$@"
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

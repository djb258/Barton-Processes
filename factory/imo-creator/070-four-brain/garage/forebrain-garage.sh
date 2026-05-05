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

usage() {
  cat <<'USAGE'
Usage:
  forebrain-garage.sh new BAR-123
  forebrain-garage.sh ready
  forebrain-garage.sh claim BAR-123 [planner-name]
  forebrain-garage.sh run-once [--execute] [--defer-lbb] [--planner-cli claude|codex|gemini] [--planner-model opus]
  forebrain-garage.sh foreman BAR-123 [--execute] [--defer-lbb] [--foreman-model sonnet]
  forebrain-garage.sh mechanic BAR-123 [--execute] [--defer-lbb] [--mechanic-model sonnet]
  forebrain-garage.sh auditor BAR-123 [--execute] [--defer-lbb] [--auditor-model gpt-5.3-codex]
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
  cat > "$prompt" <<PROMPT
ROLE: FOREMAN
PROCESS: 070 Four-Brain
BAR: $bar_id

You are the Foreman. Your job is routing only.

Required read set:
- $PROCESS_UT
- $FOUR_BRAIN_YAML
- $plan_path
- Atlas §6
- atlas/manifests/paired-artifacts.yaml
- Plan Book frontispiece

Required output:
- Write dispatch packet to: $run_dir/FOREMAN-DISPATCH.md
- Cite Atlas Step 0 sources consulted in the dispatch packet.

Rules:
- Do not build.
- Do not audit.
- Do not dispatch unless the Plan Book is signed and the BAR status is PLAN_BOOK_SIGNED.
- Sonnet/default routing model is allowed only for routing. Escalate ambiguity to Planner or Opus.
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
  cat > "$prompt" <<PROMPT
ROLE: MECHANIC
PROCESS: 070 Four-Brain
BAR: $bar_id

You are the Mechanic. Build only what the Foreman dispatch says.

Required read set:
- $PROCESS_UT
- $FOUR_BRAIN_YAML
- $run_dir/FOREMAN-DISPATCH.md
- Atlas §4 or §4.5 as applicable
- Plan Book
- Spoke frontmatter for every file to be edited

Required output:
- Write mechanic completion report to: $run_dir/MECHANIC-OUTPUT.md
- Cite Atlas Step 0 sources consulted in the mechanic completion report.

Rules:
- Do not audit your own work.
- Do not expand scope beyond Foreman dispatch.
- Make file edits only inside the allowed write scope.
- Run the requested checks if available.
- Report files changed, tests/checks run, evidence produced, and blockers.
PROMPT
  echo "$prompt"
}

write_auditor_prompt() {
  local bar_id="$1"
  local run_dir="$2"
  local prompt="$run_dir/AUDITOR-PROMPT.md"
  cat > "$prompt" <<PROMPT
ROLE: AUDITOR
PROCESS: 070 Four-Brain
BAR: $bar_id

You are the Auditor. Inspect work you did not build.

Required read set:
- $PROCESS_UT
- $FOUR_BRAIN_YAML
- $ROOT/docs/plans/$bar_id/PLAN-BOOK.md
- $run_dir/FOREMAN-DISPATCH.md
- $run_dir/MECHANIC-OUTPUT.md
- atlas/manifests/four-brain-doctrine-gate.yaml

Required output:
- Write audit verdict to: $run_dir/AUDIT-VERDICT.md
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
  local cli="$1"
  local model="$2"
  local prompt="$3"
  local run_dir="$4"
  local output="$run_dir/planner-output.md"
  case "$cli" in
    claude)
      run_claude_cli "$model" "$prompt" "$output"
      ;;
    codex)
      echo "Codex is not a Planner CLI in Process 070. Use Claude Opus for Planner and Codex for Auditor." >&2
      return 2
      ;;
    gemini)
      echo "Gemini is specialty-only and cannot run the normal Planner lane. Create an explicit specialist BAR instead." >&2
      return 2
      ;;
    *)
      echo "Unsupported planner CLI: $cli" >&2
      return 2
      ;;
  esac
  echo "$output"
}

run_claude_cli() {
  local model="$1"
  local prompt="$2"
  local output="$3"
  claude --print --model "$model" --permission-mode acceptEdits --add-dir "$ROOT" < "$prompt" > "$output"
}

run_codex_cli() {
  local model="$1"
  local prompt="$2"
  local output="$3"
  codex exec --cd "$ROOT" --sandbox danger-full-access --ask-for-approval never --model "$model" "$(cat "$prompt")" > "$output"
}

run_once() {
  local execute="false"
  local auto_continue="false"
  local defer_lbb="false"
  local planner_cli="claude"
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
      --planner-cli)
        planner_cli="${2:-claude}"
        shift 2
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
    echo "planner_cli: $planner_cli"
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

  if run_planner_cli "$planner_cli" "$planner_model" "$prompt" "$run_dir" > "$run_dir/planner-output-path.txt"; then
    if [[ -f "$plan_path" ]]; then
      if ! write_lbb_transition "$bar_id" "planner" "dispatch" "$run_dir" "$defer_lbb" > "$run_dir/lbb-planner-path.txt"; then
        update_status "$intake_yaml" "PLANNER_RUNNING" "BLOCKED"
        return 1
      fi
      if [[ "$auto_continue" == "true" ]]; then
        update_status "$intake_yaml" "PLANNER_RUNNING" "PLAN_BOOK_SIGNED"
      else
        update_status "$intake_yaml" "PLANNER_RUNNING" "REVIEW_PLAN_BOOK"
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
  update_status "$intake_yaml" "PLAN_BOOK_SIGNED" "FOREMAN_RUNNING"
  if run_claude_cli "$foreman_model" "$prompt" "$run_dir/foreman-output.md"; then
    if [[ -f "$run_dir/FOREMAN-DISPATCH.md" ]]; then
      if ! write_lbb_transition "$bar_id" "foreman" "handoff" "$run_dir" "$defer_lbb" > "$run_dir/lbb-foreman-path.txt"; then
        update_status "$intake_yaml" "FOREMAN_RUNNING" "BLOCKED"
        return 1
      fi
      if [[ "$auto_continue" == "true" ]]; then
        update_status "$intake_yaml" "FOREMAN_RUNNING" "FOREMAN_DISPATCHED"
      else
        update_status "$intake_yaml" "FOREMAN_RUNNING" "REVIEW_FOREMAN_DISPATCH"
      fi
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      echo "$run_dir/FOREMAN-DISPATCH.md"
    else
      update_status "$intake_yaml" "FOREMAN_RUNNING" "BLOCKED"
      echo "Foreman completed but did not create dispatch: $run_dir/FOREMAN-DISPATCH.md" >&2
      return 1
    fi
  else
    update_status "$intake_yaml" "FOREMAN_RUNNING" "BLOCKED"
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
  update_status "$intake_yaml" "FOREMAN_DISPATCHED" "MECHANIC_RUNNING"
  if run_claude_cli "$mechanic_model" "$prompt" "$run_dir/mechanic-output.raw.md"; then
    if [[ -f "$run_dir/MECHANIC-OUTPUT.md" ]]; then
      if ! write_lbb_transition "$bar_id" "mechanic" "edit" "$run_dir" "$defer_lbb" > "$run_dir/lbb-mechanic-path.txt"; then
        update_status "$intake_yaml" "MECHANIC_RUNNING" "BLOCKED"
        return 1
      fi
      if [[ "$auto_continue" == "true" ]]; then
        update_status "$intake_yaml" "MECHANIC_RUNNING" "MECHANIC_DONE"
      else
        update_status "$intake_yaml" "MECHANIC_RUNNING" "REVIEW_MECHANIC_OUTPUT"
      fi
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      echo "$run_dir/MECHANIC-OUTPUT.md"
    else
      update_status "$intake_yaml" "MECHANIC_RUNNING" "BLOCKED"
      echo "Mechanic completed but did not create output: $run_dir/MECHANIC-OUTPUT.md" >&2
      return 1
    fi
  else
    update_status "$intake_yaml" "MECHANIC_RUNNING" "BLOCKED"
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
  update_status "$intake_yaml" "MECHANIC_DONE" "AUDITOR_RUNNING"
  if run_codex_cli "$auditor_model" "$prompt" "$run_dir/auditor-output.raw.md"; then
    if [[ -f "$run_dir/AUDIT-VERDICT.md" ]] && head -n 1 "$run_dir/AUDIT-VERDICT.md" | grep -q "VERDICT: P=1"; then
      if ! write_lbb_transition "$bar_id" "auditor" "audit-verdict" "$run_dir" "$defer_lbb" > "$run_dir/lbb-auditor-path.txt"; then
        update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
        return 1
      fi
      update_status "$intake_yaml" "AUDITOR_RUNNING" "REVIEW_AUDIT_VERDICT"
      write_stage_report "$bar_id" "$(current_status "$bar_id")" "$run_dir" > "$run_dir/stage-report-path.txt"
      write_final_pointer "$bar_id" "$(current_status "$bar_id")" "$run_dir/AUDIT-VERDICT.md" "$run_dir" > "$run_dir/final-product-pointer.txt"
      echo "$run_dir/AUDIT-VERDICT.md"
    elif [[ -f "$run_dir/AUDIT-VERDICT.md" ]]; then
      update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
      echo "$run_dir/AUDIT-VERDICT.md"
      return 1
    else
      update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
      echo "Auditor completed but did not create verdict: $run_dir/AUDIT-VERDICT.md" >&2
      return 1
    fi
  else
    update_status "$intake_yaml" "AUDITOR_RUNNING" "BLOCKED"
    return 1
  fi
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
  status="$(current_status "$bar_id")"
  case "$status:$next_status" in
    REVIEW_PLAN_BOOK:PLAN_BOOK_SIGNED|REVIEW_FOREMAN_DISPATCH:FOREMAN_DISPATCHED|REVIEW_MECHANIC_OUTPUT:MECHANIC_DONE|REVIEW_AUDIT_VERDICT:CLOSED)
      update_status "$intake_yaml" "$status" "$next_status"
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

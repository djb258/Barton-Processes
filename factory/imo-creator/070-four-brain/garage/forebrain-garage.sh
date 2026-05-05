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

usage() {
  cat <<'USAGE'
Usage:
  forebrain-garage.sh new BAR-123
  forebrain-garage.sh ready
  forebrain-garage.sh claim BAR-123 [planner-name]
  forebrain-garage.sh run-once [--execute] [--planner-model opus]
  forebrain-garage.sh watch [--execute] [--interval 30] [--planner-model opus]
  forebrain-garage.sh final BAR-123

Contract:
  new    Creates garage/inbox/BAR-123 with intake MD/YAML copied from templates.
  ready  Lists BAR folders whose planner-intake.yaml is READY_FOR_PLANNER.
  claim  Marks a READY_FOR_PLANNER intake as PLANNER_RUNNING.
  run-once Claims the next ready intake and prepares the Planner run artifacts.
           With --execute, calls the configured Planner CLI.
  watch  Repeats run-once forever.
  final  Prints the final product pointer for a BAR.
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
      if grep -q "garage_status: READY_FOR_PLANNER" "$file"; then
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
  if ! grep -q "garage_status: READY_FOR_PLANNER" "$file"; then
    echo "Intake is not READY_FOR_PLANNER: $file" >&2
    exit 1
  fi
  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  perl -0pi -e 's/garage_status: READY_FOR_PLANNER/garage_status: PLANNER_RUNNING/' "$file"
  perl -0pi -e "s/planner_claimed_by: null/planner_claimed_by: $planner/" "$file"
  perl -0pi -e "s/planner_claimed_at: null/planner_claimed_at: $ts/" "$file"
  echo "$file"
}

first_ready_bar() {
  find "$INBOX" -mindepth 2 -maxdepth 2 -name planner-intake.yaml -print0 |
    while IFS= read -r -d '' file; do
      if grep -q "garage_status: READY_FOR_PLANNER" "$file"; then
        basename "$(dirname "$file")"
        return 0
      fi
    done
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

Required output:
- Write the Plan Book to: $plan_dir/PLAN-BOOK.md

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

update_status() {
  local file="$1"
  local from="$2"
  local to="$3"
  if grep -q "garage_status: $from" "$file"; then
    perl -0pi -e "s/garage_status: $from/garage_status: $to/" "$file"
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
  lbb: pending_or_external
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
  claude --print --model "$model" --permission-mode acceptEdits --add-dir "$ROOT" < "$prompt" > "$output"
  echo "$output"
}

run_once() {
  local execute="false"
  local planner_model="opus"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --execute)
        execute="true"
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
    echo "plan_book: $plan_path"
    echo "started_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  } > "$run_dir/run.yaml"

  if [[ "$execute" != "true" ]]; then
    echo "$prompt"
    return 0
  fi

  if run_planner_cli "$planner_model" "$prompt" "$run_dir" > "$run_dir/planner-output-path.txt"; then
    if [[ -f "$plan_path" ]]; then
      update_status "$intake_yaml" "PLANNER_RUNNING" "PLAN_BOOK_READY"
      write_final_pointer "$bar_id" "PLAN_BOOK_READY" "$plan_path" "$run_dir" > "$run_dir/final-product-pointer.txt"
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
    run_once "${args[@]}" || true
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
  run-once)
    shift
    run_once "$@"
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

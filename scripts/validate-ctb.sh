#!/bin/bash
# validate-ctb.sh — checks that Barton-Processes is in CTB-conformant final form
# Returns: 0 if all CTB rules pass, non-zero with violation count if any fail.
# Authority: Barton-Processes/law/STRUCTURE_MANIFEST.yaml (R1-R8)
# Run from: any directory (uses dirname to find repo root)

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

errors=0

# ─────────────────────────────────────────────────────────────
# R1: trunk root allowlist
# Only these files and directories are permitted at repo root
# ─────────────────────────────────────────────────────────────
allowed_root_files="CLAUDE.md README.md INDEX.md EXECUTION_ORDER.md D1_DATA_DICTIONARY.md .gitignore"
allowed_root_dirs="law docs scripts log archive factory"

for f in *; do
  if [ -f "$f" ]; then
    found=0
    for allowed in $allowed_root_files; do
      [ "$f" = "$allowed" ] && found=1 && break
    done
    if [ "$found" -eq 0 ]; then
      echo "R1 FAIL: file '$f' at trunk root is not in allowlist"
      errors=$((errors+1))
    fi
  elif [ -d "$f" ]; then
    found=0
    for allowed in $allowed_root_dirs; do
      [ "$f" = "$allowed" ] && found=1 && break
    done
    if [ "$found" -eq 0 ]; then
      echo "R1 FAIL: directory '$f/' at trunk root is not in allowlist"
      errors=$((errors+1))
    fi
  fi
done

# ─────────────────────────────────────────────────────────────
# R3: factory/<silo>/ has only numbered subfolders, no loose files
# Exemptions: _stubs/ and content/ are special silos (not numbered)
# ─────────────────────────────────────────────────────────────
for silo in factory/*/; do
  silo_name=$(basename "$silo")
  # _stubs and content are exempt — they are not numbered-process silos
  [ "$silo_name" = "_stubs" ] && continue
  [ "$silo_name" = "content" ] && continue
  for entry in "$silo"*; do
    [ -e "$entry" ] || continue
    if [ -f "$entry" ]; then
      echo "R3 FAIL: loose file '$entry' at silo level (only numbered subfolders allowed)"
      errors=$((errors+1))
    fi
  done
done

# ─────────────────────────────────────────────────────────────
# R4: each numbered process folder has required UT shape
# Required: PROCESS-UT.md, DOCTRINE.md, heir.yaml, orbt.yaml, _archived-fragments/
# Only check folders matching pattern NNN-* (digit-prefixed) under non-exempt silos
# Exempt silos: content/ (non-numbered), _stubs/ (empty placeholders)
# ─────────────────────────────────────────────────────────────
for proc in factory/*/[0-9]*/; do
  [ -d "$proc" ] || continue
  # Determine parent silo
  parent_silo=$(echo "$proc" | awk -F/ '{print $2}')
  [ "$parent_silo" = "content" ] && continue
  [ "$parent_silo" = "_stubs" ] && continue
  for required in PROCESS-UT.md DOCTRINE.md heir.yaml orbt.yaml _archived-fragments; do
    if [ ! -e "${proc}${required}" ]; then
      echo "R4 FAIL: '$proc' is missing required entry: $required"
      errors=$((errors+1))
    fi
  done
done

# ─────────────────────────────────────────────────────────────
# R2: law/doctrine/ should not exist (only .gitkeep allowed, then remove)
# ─────────────────────────────────────────────────────────────
if [ -d "law/doctrine" ]; then
  # Check if it has anything other than .gitkeep
  contents=$(find law/doctrine -not -name '.gitkeep' -not -path 'law/doctrine' 2>/dev/null | head -1)
  if [ -n "$contents" ]; then
    echo "R2 FAIL: law/doctrine/ exists with non-.gitkeep content: $contents"
    errors=$((errors+1))
  fi
fi

# ─────────────────────────────────────────────────────────────
# R9: every file under factory/ must live inside a UT folder
# (per law/FILE_LOCATION_DOCTRINE.md — process-specific files only inside UTs)
# Exemptions: factory/_stubs/, factory/content/ (silo-level exempt)
# ─────────────────────────────────────────────────────────────
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in
    factory/_stubs/*) ;;
    factory/content/*) ;;
    factory/*/[0-9]*-*/PROCESS-UT.md) ;;
    factory/*/[0-9]*-*/DOCTRINE.md) ;;
    factory/*/[0-9]*-*/heir.yaml) ;;
    factory/*/[0-9]*-*/orbt.yaml) ;;
    factory/*/[0-9]*-*/wrangler.toml) ;;
    factory/*/[0-9]*-*/package.json) ;;
    factory/*/[0-9]*-*/package-lock.json) ;;
    factory/*/[0-9]*-*/tsconfig.json) ;;
    factory/*/[0-9]*-*/src/*) ;;
    factory/*/[0-9]*-*/src-*/*) ;;
    factory/*/[0-9]*-*/migrations/*) ;;
    factory/*/[0-9]*-*/proxy/*) ;;
    factory/*/[0-9]*-*/scripts/*) ;;
    factory/*/[0-9]*-*/bulk-update/*) ;;
    factory/*/[0-9]*-*/_archived-fragments/*) ;;
    factory/*/[0-9]*-*/vendor_library/*) ;;
    *)
      echo "R9 FAIL: '$f' is outside any UT folder (process-specific files must live inside factory/<silo>/<NNN-name>/)"
      errors=$((errors+1))
      ;;
  esac
done < <(find factory -type f 2>/dev/null)

# ─────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────
echo ""
if [ "$errors" -eq 0 ]; then
  echo "validate-ctb.sh: PASS — all CTB rules satisfied (R1, R2, R3, R4, R9)"
  exit 0
else
  echo "validate-ctb.sh: FAIL — $errors violation(s) found"
  exit 1
fi

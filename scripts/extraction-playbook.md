# Extraction Playbook — Repeatable Process

**Purpose**: Step-by-step procedure for extracting executable code from any blueprint repo into barton-processes.
Run this identically for each blueprint repo.

**Authority**: BAR-136
**Version**: 1.0.0

---

## Pre-Flight Checklist

Before extracting from ANY blueprint repo, confirm:

- [ ] barton-processes repo has `law/process-registry.yaml` with entries for this repo
- [ ] Blueprint repo is on a clean branch (no uncommitted changes)
- [ ] You know the process numbers assigned to this repo's extractions

---

## Step 1: SCAN — Inventory executables in the blueprint repo

**Goal**: Produce a complete list of every executable file in the source repo.

```bash
# Navigate to blueprint repo
cd <BLUEPRINT_REPO_PATH>

# Find all executable-looking files
# JavaScript/TypeScript workers, services, pipelines
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/dist/*" \
  -not -path "*/*.d.ts" \
  -not -path "*/types.ts" \
  -not -path "*/*.test.*" \
  | sort

# Find Cloudflare Worker configs
find . -name "wrangler.toml" -not -path "*/node_modules/*"

# Find cron/scheduler configs
find . -name "*.yml" -path "*/.github/workflows/*" | xargs grep -l "schedule\|cron" 2>/dev/null
```

**Output**: File list grouped by functional unit (each group = one numbered process).

---

## Step 2: MAP — Assign process numbers

**Goal**: Map each functional unit to a numbered process.

For each group from Step 1:

1. Check `law/process-registry.yaml` — is this group already assigned a number?
2. If yes, use that number
3. If no (discovered during scan), assign next sequential number
4. Record the mapping:

```yaml
# Example mapping output
- number: "NNN"
  name: "descriptive-name"
  source_repo: "<repo-name>"
  source_paths:
    - "path/to/executable/dir/"
  runtime: "node|typescript|python|cloudflare-workers"
```

---

## Step 3: EXTRACT — Copy files to barton-processes

**Goal**: Move executable code from blueprint repo to numbered process directory.

For each process number:

```bash
# Create process directory structure
PROC_DIR="factory/NNN-process-name"
mkdir -p "$PROC_DIR/src"

# Copy executable files (preserve directory structure)
cp -r <BLUEPRINT_REPO>/<source_path>/* "$PROC_DIR/src/"

# Create process-level heir.yaml
cat > "$PROC_DIR/heir.yaml" << 'EOF'
# Process HEIR — NNN-process-name
process_id: "PROC-XXX"
process_number: "NNN"
name: "Process Name"
source_repo: "repo-name"
source_paths:
  - "original/path/"
runtime: "node"
status: "extracted"

dependencies:
  databases:
    - schema: "schema_name"
      tables: ["table1", "table2"]
  apis: []
  secrets:
    - "DOPPLER_TOKEN"

log_targets:
  - "log/NNN-process-name/"

description: "What this process does"
EOF
```

**Rules**:
- Preserve internal directory structure within `src/`
- Do NOT flatten — keep subdirectories as they were
- Do NOT modify the code during extraction — move as-is
- If the source has `package.json` or `requirements.txt`, copy those too
- If the source has `wrangler.toml`, copy it too

---

## Step 4: REGISTER — Update process-registry.yaml

**Goal**: Ensure the registry matches reality.

For each extracted process, update `law/process-registry.yaml`:
- Change `status` from `pending-extraction` to `extracted`
- Verify `source_paths` match what was actually extracted
- Add any new processes discovered during scan

Then validate:

```bash
# Count process dirs in factory/
ls -d factory/[0-9]* | wc -l

# Count entries in process-registry.yaml with status: extracted
grep "status: .extracted" law/process-registry.yaml | wc -l

# These numbers must match
```

---

## Step 5: VERIFY — Confirm zero executables remain in blueprint

**Goal**: Blueprint repo has ZERO executable code in extracted paths.

```bash
cd <BLUEPRINT_REPO_PATH>

# For each extracted source_path, verify it's empty or removed
for path in <source_path_1> <source_path_2>; do
  if [ -d "$path" ]; then
    echo "WARNING: $path still exists"
    find "$path" -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) | head -5
  else
    echo "OK: $path removed"
  fi
done

# Global check: no wrangler.toml should remain
find . -name "wrangler.toml" -not -path "*/node_modules/*"

# Global check: no cron jobs should remain
find . -name "*.yml" -path "*/.github/workflows/*" | xargs grep -l "schedule\|cron" 2>/dev/null
```

**If anything remains**: Either it wasn't part of this extraction (different process number) or you missed files. Investigate before proceeding.

---

## Step 6: STAMP — Mark blueprint repo with egress contract

**Goal**: Blueprint repo declares what data it exposes (schemas/views that processes consume).

If not already present, create in the blueprint repo:

```yaml
# law/egress-contract.yaml
egress_version: "1.0.0"
repo: "<repo-name>"
schemas:
  - name: "schema_name"
    tables:
      - name: "table_name"
        access: "READ"
        consumers: ["barton-processes"]
```

---

## Step 7: COMMIT — Two commits

**Commit 1** (in barton-processes):
```
BAR-136: Extract <repo-name> processes (NNN-NNN)

Extracted N processes from <repo-name>:
- NNN-name: description
- NNN-name: description
```

**Commit 2** (in blueprint repo):
```
BAR-136: Remove extracted executables (moved to barton-processes)

Processes NNN-NNN extracted to barton-processes.
Source paths removed. Blueprint retains schemas + doctrine only.
```

---

## Step 8: UPDATE DASHBOARD — Sync dashboard data

In imo-creator, update `dashboard/src/data/processes.ts`:
- Set extracted processes' `status` to match their actual state
- Verify `heir.repos` includes 'barton-processes'

---

## Repo Extraction Order

Run this playbook in this order (heaviest first):

| Order | Repo | Process Numbers | File Count |
|-------|------|----------------|------------|
| 1 | company-lifecycle-cl | 001-005 | 50+ files |
| 2 | barton-outreach-core | 006-011, 016 | 50+ files |
| 3 | imo-creator (field-monitor) | 012 | 4 workers |
| 4 | client | 013-014 | 10+ files |
| 5 | sales | 015 | 3 files |
| 6 | barton-storage | TBD | Not yet scanned |

---

## Verification Checklist (per repo)

After completing all steps for a repo:

- [ ] All process directories exist under `factory/`
- [ ] Each process has `heir.yaml` with `log_targets`
- [ ] `law/process-registry.yaml` updated — status = `extracted`
- [ ] Process count in registry matches directory count
- [ ] Blueprint repo has ZERO executables in extracted paths
- [ ] Blueprint repo has ZERO `wrangler.toml` files (if extracted)
- [ ] Blueprint repo has ZERO cron/scheduled workflows (if extracted)
- [ ] Egress contract exists in blueprint repo
- [ ] Both repos committed
- [ ] Dashboard updated (if applicable)

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-03-14 |
| Version | 1.0.0 |
| BAR | BAR-136 |

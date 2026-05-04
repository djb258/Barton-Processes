ROLE: AUDITOR
TASK: Audit the bp.820 Vendor Export repair. Return `VERDICT: P=1` only if the repaired files satisfy the process contract well enough for BAR-377 repair certification. Return `VERDICT: P=0` with cited reasons if any blocker remains.

READ:
- factory/client/820-vendor-export/wrangler.toml
- factory/client/820-vendor-export/src/index.ts
- factory/client/820-vendor-export/src/export.ts
- factory/client/820-vendor-export/src/blueprints.ts
- factory/client/820-vendor-export/src/migrations/001_d1_export_tables.sql
- factory/client/820-vendor-export/PROCESS-UT.md
- docs/audit/process-runs/bp-820/repair-bp-820.md

SCOPE:
- Read-only audit. Do not modify files.

ACCEPTANCE:
- Wrangler bindings must be non-empty and point to live resources recorded in the repair note.
- Source queries must target tables that exist in the live client D1 schema recorded in the repair note.
- Export logging must match the migration schema.
- Any remaining process risks must be classified as certification blockers or non-blocking follow-ups.

CONSTRAINTS:
- Auditor does not fix findings.
- Cite only files named in READ.

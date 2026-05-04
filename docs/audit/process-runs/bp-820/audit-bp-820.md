# BAR-377 Audit Verdict - bp.820

Date: 2026-05-04
Process: bp.820 Vendor Export
Role: Auditor
Auditor: Codex nested Four-Brain runner

## Verdict

P=1

## Scope

This verdict certifies the BAR-377 bp.820 repair, not OPERATE promotion.

## Reason

The repaired Wrangler bindings are non-empty and match live Cloudflare resources recorded in `repair-bp-820.md`. The Worker source now queries the live client D1 schema recorded in the repair note. Export logging matches the additive D1 migration schema.

## Cited Evidence

- `wrangler.toml` binds D1 to `svg-d1-client` / `5443887b-ba8a-4da5-9f54-6a9c2cfb1244`.
- `wrangler.toml` binds KV to `66e6c7bec8c1479ba708c0bcbb6a0e23` (`EGRESS_KV`).
- `src/index.ts` queries `clients`.
- `src/export.ts` queries `client_employees`, `client_vendors`, and `client_employee_vendor_ids`.
- `src/export.ts` writes `export_log` and `export_error` columns matching `src/migrations/001_d1_export_tables.sql`.

## Non-Blocking Follow-Ups

- Full live export run is still required before OPERATE promotion.
- Blueprints must exist in `EGRESS_KV` under `blueprint:{vendor_id}`.
- HTTP endpoint authentication remains an open process risk.
- Vendor delivery remains out of scope/TODO.

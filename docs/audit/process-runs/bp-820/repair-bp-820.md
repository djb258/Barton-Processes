# BAR-377 Repair Record - bp.820

Date: 2026-05-04
Process: bp.820 Vendor Export
Role Path: Planner classification -> local Mechanic repair -> Auditor pending

## Repair Summary

bp.820 was blocked because `wrangler.toml` contained empty deploy-critical D1 and KV binding IDs. Live Cloudflare inventory showed the usable resources were:

- D1: `svg-d1-client` / `5443887b-ba8a-4da5-9f54-6a9c2cfb1244`
- KV: `EGRESS_KV` / `66e6c7bec8c1479ba708c0bcbb6a0e23`

The Worker source was also still querying old placeholder table names (`client`, `person`, `election`, `plan`, `vendor`, `external_identity_map`). Live D1 introspection showed the client D1 uses:

- `clients`
- `client_employees`
- `client_employee_vendor_ids`
- `client_vendors`

## Files Changed

- `factory/client/820-vendor-export/wrangler.toml`
- `factory/client/820-vendor-export/src/index.ts`
- `factory/client/820-vendor-export/src/export.ts`

## Remote D1 Change

Applied existing additive migration to `svg-d1-client`:

- `factory/client/820-vendor-export/src/migrations/001_d1_export_tables.sql`

Created/confirmed tables:

- `export_error`
- `export_log`
- `export_schedule`

## Verification

| Check | Result |
|-------|--------|
| `npx tsc --noEmit` | PASS |
| `npx wrangler deploy --dry-run` | PASS |
| Remote D1 table check | PASS - export tables present |

## Remaining Certification Risks

- bp.820 still needs a full live export run before OPERATE promotion.
- Blueprints must exist in `EGRESS_KV` under `blueprint:{vendor_id}`.
- HTTP endpoint authentication remains listed as an open process risk in `PROCESS-UT.md`.
- Delivery to vendor destination remains out of scope/TODO.

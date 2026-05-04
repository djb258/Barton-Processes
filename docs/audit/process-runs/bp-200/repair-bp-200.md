# BAR-377 Repair Record - bp.200

Date: 2026-05-04
Process: bp.200 People Worker
Role Path: Planner classification -> local Mechanic repair -> Auditor pending

## Repair Summary

bp.200 had two local verification defects:

- `package.json` referenced `wrangler-v2.toml`, but the process uses `wrangler.toml`.
- `tsconfig.json` included `src/**/*.ts`, but the active Worker source is under `src-v2/**/*.ts`.

After those were repaired, typecheck exposed one real source type mismatch:

- `runPass1()` returns `from_blog_data` and `from_fetch`, but `PassResult` did not declare those optional metrics.

## Files Changed

- `factory/outreach/200-people-worker/package.json`
- `factory/outreach/200-people-worker/tsconfig.json`
- `factory/outreach/200-people-worker/src-v2/types.ts`

## Verification

| Check | Result |
|-------|--------|
| `npm run typecheck` | PASS |
| `npx wrangler deploy --dry-run -c wrangler.toml` | PASS |
| Live `/health` | PASS - `slots=98106`, `people=57667`, `empty_slots=40330` |
| Remote D1 People counts | PASS - `people_company_slot=98106`, filled `57776`, empty `40330`, `intake_people_staging=0`, `people_people_master=57667` |

## Remaining Certification Risks

- bp.200 still has a live fill gap: 40,330 empty slots.
- `intake_people_staging` is empty, so Pass 0 cannot improve fill rate until upstream staging is replenished.
- Further repair is operational/enrichment route work: Pass 1/Pass 2 execution and upstream 201/202/300 data production.

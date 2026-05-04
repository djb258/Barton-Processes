# BAR-377 Audit Verdict - bp.010

Date: 2026-05-04
Process: bp.010 SEED D1
Role: Auditor
Auditor: Codex nested Four-Brain runner

## Verdict

P=0

## Reason

Superseded by `live-refresh-bp-010.md`. The Cloudflare token issue was resolved, but refreshed live D1 evidence still returns P=0 for full certification because People and column-registry counts drift from the UT baselines.

## Cited Evidence

- `live-refresh-bp-010.md` records `people_people_master=57667` versus UT baseline `58857`.
- `live-refresh-bp-010.md` records `outreach_column_registry=78` versus UT baseline `79`.
- `live-refresh-bp-010.md` confirms core company/spine counts still pass at `32702`.

## Required Repair

Explain or repair the People baseline drift and column registry discrepancy. Rerun orphan-slot integrity with a paginated/indexed query because the direct anti-join exceeded D1 CPU limits.

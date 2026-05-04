# BAR-377 Live Refresh - bp.400

Date: 2026-05-04
Process: bp.400 DOL Views
Mode: corrected Cloudflare token, remote D1 read-only checks

## Token Correction

Initial Stage 2 evidence was blocked because Wrangler used the wrong token path. The successful refresh used:

```text
CLOUDFLARE_API_TOKEN = GLOBAL_CLOUDFLARE_API_TOKEN
```

## Remote D1 Counts

| Gauge | Live Count | Status |
|-------|------------|--------|
| `dol_form_5500` | 14,252 | PASS |
| `dol_schedule_a` | 9,538 | PASS against BAR-379/D1 dictionary |
| `dol_schedule_c` | 18,246 | PASS against BAR-379/D1 dictionary |
| `dol_schedule_other` | 67,164 | PASS as live non-zero runtime DOL surface |

## Documentation Drift

`PROCESS-UT.md` still contains older D1 count examples in some sections, including `dol_schedule_a` 17,890, `dol_schedule_c` 33,810, and `dol_schedule_other` 105,088. The current live D1 counts match the newer BAR-379/D1 dictionary evidence used in BAR-377 Stage 2.

## Verdict

P=1 for D1 runtime evidence refresh.

This does not certify Neon view freshness. Neon view checks remain separate because bp.400 is documented as Neon views plus D1 runtime tables.

# DOCTRINE — D-350: Bookkeeping
## Status: BUILD
## Authority: BAR-122
## Version: 1.0.0
## Created: 2026-04-30

---

# D-350 Rules — Bookkeeping Process Doctrine

## D-350-01 — AP Tool Sovereignty

Bill.com is the exclusive tool for Accounts Payable. No AP workflow runs outside Bill.com once the account is active. No vendor payment may be logged in Xero directly — Bill.com is the source of truth for all AP events.

## D-350-02 — GL Tool Sovereignty

Xero is the exclusive General Ledger. All GL entries flow from Bill.com events or from direct Xero journal entries. No shadow ledger. No manual tracking in spreadsheets.

## D-350-03 — Join Key: sovereign_id

Every vendor, client, and internal entity record joins to its Barton Enterprises sovereign identity via `sovereign_id`. Bill.com vendor records JOIN to client/vendor records in MC_DB. Xero contacts JOIN to the same sovereign_id. No dangling records — if a record cannot be joined, it routes to the error table pending resolution.

## D-350-04 — No PII in Logs

No PII (bank account numbers, SSN, EIN, tax ID, routing numbers) may appear in log records, LBB ingest payloads, or error tables. Sensitive financial identifiers are masked to last-4 format in all log outputs.

## D-350-05 — Graceful Degradation

If Bill.com or Xero API keys are absent (accounts not yet created), all spoke functions MUST throw a structured "not configured" error. The MC worker degrades gracefully — routes return `{ status: "not_configured", message: "..." }` — never a 500. The system is always in a known state.

## D-350-06 — API Client Isolation

Bill.com client lives in `workers/mission-control-api/src/cos/spokes/billcom.ts`. Xero client lives in `workers/mission-control-api/src/cos/spokes/xero.ts`. Routes live in `workers/mission-control-api/src/routes/finance.ts`. No business logic in spoke files — spokes are dumb transport only. All logic lives in the hub (route handlers + COS layer).

## D-350-07 — Auth Secrets via Doppler

All API credentials are injected via Doppler → Wrangler secret. No hardcoded credentials. No .env files committed. Secrets required: `BILLCOM_API_KEY`, `BILLCOM_DEV_KEY`, `XERO_CLIENT_ID`, `XERO_CLIENT_SECRET`, `XERO_REFRESH_TOKEN`.

## D-350-08 — Account Creation is Dave-Action

Bill.com and Xero account creation is a human-only action (Dave). The code scaffold exists and waits for keys. No automation may create accounts on behalf of Barton Enterprises. The mechanic builds the socket; Dave plugs in the bolt.

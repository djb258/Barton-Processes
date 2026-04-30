# DOCTRINE — Process 1800 CF Stream Video Upload
## Locked rules. Auditor enforces. Violations block video embedding on content pages.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-1800-01 | CF Stream requires a dedicated API token (CF_STREAM_API_TOKEN) with Account > Cloudflare Stream > Edit permissions. Existing CF tokens (CF_API_TOKEN, GLOBAL_CLOUDFLARE_API_TOKEN) and wrangler OAuth do NOT have Stream scope. Never attempt a Stream upload with the wrong token. | PROCESS-UT.md §4 WHAT IT GRABS — Secrets; §7 STOP CONDITIONS | §7 stop — wrong token returns auth error; HALT and create the correct token |
| D-1800-02 | The CF Stream API token must be created manually in the Cloudflare Dashboard (Turnstile blocks automation). Once created, it is stored in Doppler only — never in code, never in environment variables outside Doppler. | PROCESS-UT.md §4 Creating the CF Stream API Token | pre-flight — token outside Doppler is a secrets hygiene violation |
| D-1800-03 | Upload method is multipart form POST with `file` field to the CF Stream API endpoint. The embed URL pattern is `https://customer-{subdomain}.cloudflarestream.com/{uid}/iframe`. The video slot in ContentConfig uses the `streamId` property. These are constants — they do not change per run. | PROCESS-UT.md §5 CONSTANTS | pre-flight — any deviation from the upload method or embed pattern is a violation |
| D-1800-04 | After upload, the process must poll for `status.state === "ready"` before wiring the Stream UID into App.tsx. Deploying with an unready UID results in a broken video player. | PROCESS-UT.md §4 IMO Middle Step 2; §8 SMOKE TEST Step 3 | §7 stop — deploy before "ready" state = broken content page |
| D-1800-05 | Every Stream UID must be recorded in notebooks-registry.md AND ingested to LBB before the process is considered closed. An unrecorded UID is an orphan artifact. | PROCESS-UT.md §4 IMO Circle; §6 CONSTANTS | §7 stop — unrecorded UID breaks artifact lineage |
| D-1800-06 | Video files over 200MB require explicit verification that the CF Stream account plan supports the file size before upload. Do not assume plan limits — check first. | PROCESS-UT.md §7 STOP CONDITIONS | §7 stop — plan limit exceeded = failed upload, wasted time |
| D-1800-07 | Strike 3 on the same failure (e.g., repeated auth errors, repeated processing failures) escalates to Troubleshoot/Train — not another repair attempt. Check CF account limits, token scope, and video format before retrying. | PROCESS-UT.md §10 KNOWN ISSUES; Bedrock §6 Troubleshooting Loop | §7 stop — Strike 3 = Airworthiness Directive, not patch |

## Cross-references
- UT §4 IMO Middle cites D-1800-03 (upload method), D-1800-04 (ready-state polling)
- UT §7 STOP CONDITIONS cites D-1800-01 (token), D-1800-04 (ready), D-1800-06 (file size)
- UT §4 Circle cites D-1800-05 (UID recording)
- UT §10 KNOWN ISSUES cites D-1800-07 (Strike 3)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |
| Rule Count | 7 (D-1800-01 through D-1800-07) |

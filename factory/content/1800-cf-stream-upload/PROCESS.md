# PROCESS: CF Stream Video Upload
## Upload video artifacts from NotebookLM to Cloudflare Stream for embedding on content pages
### Status: BUILD
### Business: imo-creator

---

## 1. IDENTITY

| Field | Value |
|-------|-------|
| Process ID | PROC-018 |
| Name | CF Stream Video Upload |
| Business Silo | imo-creator (cross-cutting — serves all businesses) |
| CTB Position | factory/018-cf-stream-upload |
| ORBT | BUILD |
| Strikes | 0 |
| Last Deployed | 2026-04-02 |
| BAR Reference | — |
| Deployed URL | not deployed (CLI/API process, not a worker) |
| Cron | manual |
| Runtime | CLI (curl + CF API) |

---

## 2. WHY THIS EXISTS

Video files from NotebookLM are too large for static CF Pages hosting (65MB+). CF Stream provides adaptive bitrate streaming, player embed, and CDN delivery. Without this process, videos can't be embedded in the content-pages template — the video slot stays empty.

---

## 3. IMO — What Comes In, What Happens, What Comes Out

### Two-Question Intake (Bedrock §7)
1. **"What triggers this?"** — Video artifact downloaded from NotebookLM Studio
2. **"How do we get it?"** — Chrome DevTools MCP clicks Download on the video artifact in NotebookLM → file lands in Downloads folder

### Input
- Video file (.mp4) in `C:/Users/CUSTOM PC/Downloads/`
- Downloaded from NotebookLM Studio tab via Chrome DevTools MCP
- Typical size: 30-100MB

### Middle

| Step | Input | What Happens | Output | Tool Used |
|------|-------|-------------|--------|-----------|
| 1 | Video .mp4 in Downloads | Upload to CF Stream via API | Stream video UID | curl + CF Stream API |
| 2 | Stream video UID | Wait for processing to complete | Ready status + playback URL | CF Stream API (poll) |
| 3 | Stream UID | Wire into ContentConfig in App.tsx | Video slot populated | Code edit |
| 4 | Updated App.tsx | Build and deploy content-pages | Live page with embedded video | vite build + wrangler pages deploy |
| 5 | Stream UID | Store in Doppler or process doc for reference | Documented | Doppler or markdown |

### Output
- Video hosted on CF Stream with adaptive bitrate
- Embed URL: `https://customer-{subdomain}.cloudflarestream.com/{uid}/iframe`
- Content page video slot populated with `streamId`

### Circle (Bedrock §5)
- Video playback verified on live content page
- Stream UID recorded in notebooks-registry.md
- LBB ingest with video metadata

---

## 4. WHAT IT GRABS OFF THE WALL

### Databases

None — this process doesn't touch databases directly.

### Tools & Integrations

| Item | Type | Cost Tier | Credentials | What It Does |
|------|------|-----------|-------------|-------------|
| CF Stream API | API | Cheap ($1/1000 min stored, $0.01/1000 min viewed) | CF_STREAM_API_TOKEN | Upload video, get UID, check status |
| Chrome DevTools MCP | MCP | Free | None (browser session) | Download video from NotebookLM |
| wrangler | CLI | Free | OAuth session | Deploy updated content-pages |

### Secrets (from Doppler)

| Secret | Doppler Project | Config | Used By |
|--------|----------------|--------|---------|
| CF_STREAM_API_TOKEN | imo-creator | dev | Step 1 — upload to Stream |
| GLOBAL_CLOUDFLARE_ACCOUNT_ID | imo-creator | dev | Step 1 — account identifier |

**Creating the CF Stream API Token:**
1. Go to https://dash.cloudflare.com/profile/api-tokens (must be done manually — Turnstile blocks automation)
2. Create Token → Custom Token
3. Permissions: **Account > Cloudflare Stream > Edit**
4. Account Resources: Include > Specific Account > your account
5. Copy token → `doppler secrets set CF_STREAM_API_TOKEN "{token}" --project imo-creator --config dev`

**Why a separate token:** The existing CF API tokens (CF_API_TOKEN, GLOBAL_CLOUDFLARE_API_TOKEN) and wrangler OAuth do NOT have Stream permissions. Stream requires its own token scope.

---

## 5. OSAM — Where the Data Lives

Not applicable — this process doesn't read/write database tables. Video files go to CF Stream (object storage), not D1/Neon.

---

## 6. CONSTANTS & VARIABLES (Bedrock §2)

### Constants (structure — never changes)

- CF Stream API endpoint: `https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/stream`
- Upload method: multipart form POST with `file` field
- Embed URL pattern: `https://customer-{subdomain}.cloudflarestream.com/{uid}/iframe`
- Video slot in ContentConfig uses `streamId` property
- Auth header: `Authorization: Bearer {CF_STREAM_API_TOKEN}`

### Variables (fill — changes every run)

- Which video file to upload
- The video filename and metadata
- The resulting Stream UID
- Which content page gets the video

---

## 7. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| CF_STREAM_API_TOKEN not set in Doppler | HALT — create token first (see §4) |
| Upload returns auth error | HALT — token doesn't have Stream permissions |
| Video file > 200MB | HALT — check if CF Stream plan supports file size |
| Upload succeeds but processing fails | Retry once, then HALT — check video format |
| Strike 3 on same failure | Troubleshoot/Train → check CF account limits |

---

## 8. DEPENDENCIES

### Upstream (must exist before this runs)

| Dependency | What | Status |
|-----------|------|--------|
| NotebookLM video artifact | Generated and downloaded video .mp4 | DONE per notebook |
| CF Stream API token | Token with Stream Edit permissions | PENDING — needs manual creation |
| content-pages template | CF Pages site with video slot | DONE |

### Downstream (consumes this process's output)

| Consumer | What It Needs |
|----------|--------------|
| content-pages App.tsx | Stream UID for video slot |
| Client-facing URL | Live page with embedded video player |

---

## 9. SMOKE TEST

```
1. Verify token exists:
   doppler secrets get CF_STREAM_API_TOKEN --project imo-creator --config dev --plain
   → expected: non-empty token string

2. Upload test video:
   CF_ACCOUNT=$(doppler secrets get GLOBAL_CLOUDFLARE_ACCOUNT_ID --project imo-creator --config dev --plain)
   CF_STREAM=$(doppler secrets get CF_STREAM_API_TOKEN --project imo-creator --config dev --plain)
   curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT/stream" \
     -H "Authorization: Bearer $CF_STREAM" \
     -F "file=@/path/to/video.mp4" \
     -F 'meta={"name":"test-video"}'
   → expected: {"success":true, "result":{"uid":"...", ...}}

3. Check processing status:
   curl -s "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT/stream/{uid}" \
     -H "Authorization: Bearer $CF_STREAM"
   → expected: status.state === "ready"

4. Verify embed URL loads:
   Open https://customer-{subdomain}.cloudflarestream.com/{uid}/iframe
   → expected: video player renders

5. Verify content page shows video:
   Open content-pages deployment URL
   → expected: video player embedded in video slot
```

**Three Primitives Check (Bedrock §1):**
1. **Thing:** Did the video file exist in Downloads? Did the Stream UID get returned?
2. **Flow:** Did the upload reach CF Stream? Did the UID reach App.tsx?
3. **Change:** Did the video process to "ready" state? Did the page deploy with the new config?

---

## 10. LOGBOOK

### 2026-04-01 — First attempt (5500 Education video)

**ORBT:** BUILD
**Trigger:** 5500 Education notebook video artifact downloaded
**Video:** Pull_vs.mp4 (65MB) — "Pull vs Push: The Form 5500 Data Showdown"
**Result:** BLOCKED — CF API tokens (CF_API_TOKEN, GLOBAL_CLOUDFLARE_API_TOKEN) do not have Stream permissions. Wrangler OAuth also lacks Stream scope. CF Dashboard blocked by Turnstile anti-bot challenge.
**Resolution needed:** Create dedicated CF_STREAM_API_TOKEN with Account > Stream > Edit permissions.
**ORBT after:** BUILD (blocked on token creation)

---

## 11. KNOWN ISSUES & STRIKE TRACKING

| # | Date | Issue | Root Cause | Fix | Strikes |
|---|------|-------|-----------|-----|---------|
| 1 | 2026-04-01 | Upload auth fails with all existing tokens | No CF token has Stream scope | Create CF_STREAM_API_TOKEN with Stream Edit permission | 1 |
| 2 | 2026-04-01 | CF Dashboard Turnstile blocks Chrome DevTools MCP | CF anti-bot protection on dashboard | Must create token manually in browser | 0 |

---

## 12. SESSION LOG

| Date | What Was Done | LBB Record |
|------|---------------|------------|
| 2026-04-01 | Built content-pages template, downloaded 5500 artifacts, attempted Stream upload — blocked on token | 48d480ad-64fa-4ed3-a910-42a2e098a0f0 |
| 2026-04-02 | Documented process, identified token blocker | — |

---

## Document Control

| Field | Value |
|-------|-------|
| Created | 2026-04-02 |
| Last Modified | 2026-04-02 |
| Version | 1.0.0 |
| Template Version | 2.0.0 |
| Governing Engine | law/doctrine/FOUNDATIONAL_BEDROCK.md |
| OSAM Authority | N/A |
| Data Flow | NotebookLM → Downloads → CF Stream → content-pages |

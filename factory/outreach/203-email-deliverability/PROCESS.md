# Process 203 - Email Deliverability
## Thread 2 implementation contract for cold email send, domain warmup, and reply telemetry
### Status: BUILD
### Medium: process
### Business: svg-agency

---

# IDENTITY

## 1. IDENTITY

| Field | Value |
|-------|-------|
| ID | PROC-203 |
| Name | Email Deliverability |
| Medium | process |
| Business Silo | svg-agency (outreach) |
| CTB Position | trunk / Barton-Processes/factory/outreach/203-email-deliverability/PROCESS.md |
| ORBT | BUILD |
| Authority | session-31 Thread 2 brief + FCE-006 + VOICE-SPEC.yaml |
| Last Modified | 2026-04-21 |

### HEIR

| Field | Value |
|-------|-------|
| sovereign_ref | imo-creator |
| hub_id | proc-203-email-deliverability |
| ctb_placement | trunk |
| imo_topology | middle |
| cc_layer | CC-03 |
| services | LCS Hub, Mailgun, D1 spine, D1 outreach-ops |
| secrets_provider | doppler |
| acceptance_criteria | Voice spec consumed, deliverability guardrails applied, send/open/reply telemetry returns to LCS Hub |

---

# CONTRACT

## 2. PURPOSE

Thread 2 wires the deliverability structure discovered in FCE-006 into the live email send path. Without this process, outbound email remains a copy exercise instead of a controlled send pipeline with warmup, rotation, reputation checks, and telemetry feedback.

## 3. RESOURCES

| Resource | Purpose | Status |
|----------|---------|--------|
| `factory/agents/up/dyno-runs/us/fce-006-email-deliverability/FCE-006.md` | Deliverability constants | DONE |
| `fleet/content/VOICE-SPEC.yaml` | Machine voice contract | DONE |
| `workers/lcs-hub/src/voice-spec.generated.ts` | Generated machine layer used by the live compiler | DONE |
| `workers/lcs-hub/src/compiler-v2.ts` | Live send path | DONE |
| `workers/lcs-hub/src/index.ts` | Event router and webhook intake | DONE |
| `workers/lcs-hub/src/voice-spec.ts` | Runtime bridge to the voice contract | DONE |

## 4. IMO

### Two-Question Intake
1. What triggers this? Thread 2 dispatch from the session brief.
2. How do we get it? Update the live LCS Hub send path, then return send/open/click/reply events through the webhook router.

### Input
- FCE-006 deliverability constants
- Thread 1 voice spec
- Existing LCS Hub worker

### Middle
1. Build outbound copy from the generated voice contract bridge.
2. Rotate among healthy sending domains.
3. Send via Mailgun with the correct reply path.
4. Feed delivery feedback into LCS event logging.

### Output
- Sent messages
- Delivery events
- Reply events
- Suppression and strike updates

## 5. DATA SCHEMA

| Read | Write | Join |
|------|-------|------|
| `lcs_domain_rotation` | send counts, bounce counts | domain |
| `lcs_suppression` | blocked recipients | email |
| `lcs_mid_sequence_state` | status transitions | mid_id |
| `lcs_event` | send/open/click/reply telemetry | communication_id, mid_id |

## 6. DMJ

| Element | Mapping |
|---------|---------|
| Voice contract | `fleet/content/VOICE-SPEC.yaml` -> generated bridge -> runtime validator |
| Deliverability gates | warmup stage, bounce rate, paused domain checks |
| Reply handling | Mailgun webhook -> `MID_REPLIED` -> LCS event log |

## 7. CONSTANTS & VARIABLES

### Constants
- Reply-To: `Dave Barton <dave@svg.agency>`
- Domain warmup and bounce thresholds
- Voice posture: direct, confident, challenging
- Required brand anchor: Insurance Informatics
- Validation fails closed on forbidden phrases, missing required phrases, unsupported brand anchors, and email channel rule violations.

### Variables
- Recipient name
- Sending domain chosen for the send
- Event type returned by the provider

## 8. STOP CONDITIONS

| Condition | Action |
|-----------|--------|
| Reply path missing | Halt |
| Recipient suppressed | Do not send |
| Domain bounce health over threshold | Skip domain |
| Voice validation fails | Reject draft |

---

# GOVERNANCE

## 9. VERIFICATION

1. Send a test email and confirm Mailgun receives the message.
2. Trigger an open or click event and confirm LCS event logging.
3. Trigger a reply event and confirm `MID_REPLIED` is logged.

## 10. ANALYTICS

| Metric | Target |
|--------|--------|
| Bounce rate | < 5% per domain |
| Reply rate | Measurable and logged |
| Open/click tracking | Present in LCS |

## 11. EXECUTION TRACE

| Field | Value |
|-------|-------|
| trace_id | pending |
| run_id | pending |
| step | thread-2-email-outreach |
| status | done |

## 12. LOGBOOK

Pending certification.

## 13. FLEET FAILURE REGISTRY

| Pattern | Status |
|---------|--------|
| None registered | Active |

## 14. SESSION LOG

| Date | What Was Done |
|------|---------------|
| 2026-04-21 | Built the email deliverability process artifact for Thread 2. |

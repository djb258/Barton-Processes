# Planner Intake — BAR-FOUR-BRAIN-CLI
## Process 070 Four-Brain Planner Source Packet
### Status: DRAFT (awaiting sovereign review)
### Medium: planner-intake
### Business: imo-creator

---

## 1. Purpose

Produce the Plan Book that builds the **four-brain pipeline runtime** — the D1-backed inbox/outbox + API routes + runner refactor that PROC-070 §11 OUT OF SCOPE already named as `BAR-FOUR-BRAIN-CLI`.

The doctrine in `PROCESS-UT.md` and `four-brain.yaml` already specifies the schema, table names, binding, migration filename, and gate predicates. This BAR builds the runtime that conforms to that doctrine. PROC-070 doctrine itself does not change.

Paired YAML: `planner-intake.yaml`

---

## 2. Planner Request

| Field | Fill |
| --- | --- |
| BAR / Work ID | BAR-FOUR-BRAIN-CLI |
| Target Process | PROC-070 / bp.070-four-brain / four-brain pipeline runtime |
| Desired Outcome | Refactor the four-brain runner so each agent (planner, foreman, mechanic, auditor) has its own inbox/outbox queue backed by D1 in `mission-control-api`. Hand-offs become automatic — when one agent finishes, the next agent's inbox row appears and that agent claims it. Replaces the current shared `garage/runs/{BAR}/{ts}/` filesystem state machine for queue/state telemetry while retaining the run dir for durable artifacts (Plan Books, UT Books, Audit Books). |
| Operating Mode | BUILD |
| Due / Timing | No deadline. Sovereign-paced. |
| Sovereign Decision Needed | One. See §19. |

Planner request:

```text
Run Process 070 for BAR-FOUR-BRAIN-CLI.

Desired outcome:
Build the four-brain pipeline runtime per PROC-070 §11 OUT OF SCOPE spec —
D1 migration `migrations/0019_four_brain_run.sql`, new mission-control-api
routes for per-role inbox/outbox claim+transition, forebrain-garage.sh refactor
to use those routes, and an end-to-end no-op BAR smoke test that produces
exactly 4 LBB rows + 1 Audit Book on PASS.

PROC-070 doctrine (PROCESS-UT.md, four-brain.yaml) is the source of truth
for table specs, binding name, migration filename, and gate predicates.
The runtime conforms; the doctrine does not change.
```

---

## 3. Garage Intake Status

| Field | Fill |
| --- | --- |
| garage_status | DRAFT |
| intake_path | `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-FOUR-BRAIN-CLI/PLANNER-INTAKE.md` |
| intake_yaml_path | `Barton-Processes/factory/imo-creator/070-four-brain/garage/inbox/BAR-FOUR-BRAIN-CLI/planner-intake.yaml` |
| requested_by | Dave Barton (sovereign) |
| ready_at | (sovereign sets when flipping DRAFT → READY_FOR_PLANNER) |
| planner_claimed_by | (blank) |
| planner_claimed_at | (blank) |
| next_artifact | `Barton-Processes/docs/plans/BAR-FOUR-BRAIN-CLI/PLAN-BOOK.md` |

**Status stays DRAFT until sovereign review. Sovereign flips to READY_FOR_PLANNER.**

---

## 4. Source-Of-Truth Split

| Layer | Owner | Repo / Folder | What It Owns |
| --- | --- | --- | --- |
| Blueprint / Architecture | imo-creator-v2 atlas + Barton-Processes 070 doctrine | `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` v1.2.0, `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md`, `four-brain.yaml` | Pipeline doctrine — role separation, gate spec, table column specs, migration filename |
| Execution / Operations | Barton-Processes 070 runner | `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` | Runner state machine. Refactored to call new API routes instead of writing local YAML status. |
| Runtime / Deployment | imo-creator-v2 mission-control-api | `imo-creator-v2/workers/mission-control-api/` (extended), `imo-creator-v2/workers/mission-control-api/migrations/0019_four_brain_run.sql` (new) | Worker that hosts the D1-backed queue. Adds four-brain-specific routes alongside generic `/inbox`. |
| Evidence / Observability | mission-control D1 + LBB | `mission-control.four_brain_run`, `mission-control.four_brain_transition`, `mission-control.squawks`, `lbb.records`, `lbb.logbook` | Queue state, role transitions, gate verdicts, Audit Books, CERTIFY rows |

Non-drift rule:

```text
Blueprint explains. Execution runs. Runtime implements. Evidence proves.
PROC-070 PROCESS-UT.md + four-brain.yaml are the blueprint and do not change.
This BAR builds the runtime + execution layers to conform to the existing blueprint.
```

---

## 5. Required Format

| Artifact | Required? | Format |
| --- | --- | --- |
| Plan Book | yes | Plan-Body — `Barton-Processes/docs/plans/BAR-FOUR-BRAIN-CLI/PLAN-BOOK.md` |
| UT Book | yes | UT-Body — Mechanic creates one or more UT Books for each new Library artifact (route spec, runner spec). Path TBD by Planner per HEIR-B convention. |
| Companion YAML | yes (paired with each UT) | Workflow-Body for runner; Config-Body or Schema-Body for migration |
| Migration SQL | yes | `imo-creator-v2/workers/mission-control-api/migrations/0019_four_brain_run.sql` (filename mandated by `four-brain.yaml` Block 9) |
| BS Law conformance | yes | Y-junction syntactic separation on every paired YAML |
| Atlas references | yes | KEY, BS Law, Structure Manifest, FOUR_BRAIN_AVIATION, PROC-070, four-brain-doctrine-gate, paired-artifacts row 9 |
| LBB / MC evidence | yes | 4 transition rows + 1 Audit Book produced by smoke-test BAR run |

---

## 6. Read Set

Planner must inspect these before planning:

| Source | Why Planner Reads It |
| --- | --- |
| `imo-creator-v2/atlas/constants/KEY.md` | Vocabulary (10th locked constant) |
| `imo-creator-v2/CLAUDE.md` | Architecture, 17 locked constants, gate sequence |
| `imo-creator-v2/atlas/WORK_ORDER.md` | 4-gate sequence (Dispatch → Build → Audit → Close) |
| `imo-creator-v2/atlas/constants/BS_LAW.md` | Y-junction conformance for every paired YAML |
| `imo-creator-v2/atlas/constants/BOOK_LAW.md` v1.5.0 | UT-Body / Workflow-Body / Plan-Body / Audit-Body species rules |
| `imo-creator-v2/atlas/constants/FOUR_BRAIN_AVIATION.md` v1.2.0 | The 16th locked constant — pipeline doctrine |
| `Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md` v1.0.0 | PROC-070 doctrine — Component Status, OSAM, gates |
| `Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml` v1.0.0 | Block 9 = D1 binding, table specs, migration filename, column specs (source of truth for §10 P=1 gates G01-G10) |
| `imo-creator-v2/atlas/manifests/four-brain-doctrine-gate.yaml` | Gate spec source of truth + LBB row schema |
| `imo-creator-v2/atlas/manifests/paired-artifacts.yaml` row 9 (`four-brain-doctrine-gate`) | Atlas registry row that this BAR's runtime must align to |
| `imo-creator-v2/workers/mission-control-api/MANUAL.md` | Existing dispatch system — `/inbox`, `/inbox/claim`, PATCH routes; D1 binding, Doppler auth, dashboard integration |
| `imo-creator-v2/workers/mission-control-api/wrangler.toml` | Existing bindings, route registrations, D1 setup |
| `imo-creator-v2/workers/mission-control-api/migrations/` | Migration numbering convention; 0019 is next |
| `Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh` | Current runner — what gets refactored |
| `Barton-Processes/factory/imo-creator/070-four-brain/PLANNER-INTAKE-TEMPLATE.md` + `planner-intake-template.yaml` | Intake template (this packet derives from it) |
| `imo-creator-v2/atlas/constants/UNIFIED_TEMPLATE.md` v2.8.0 | UT format for any new UT Book the Mechanic produces |
| `imo-creator-v2/atlas/constants/UT_CHECKLIST.md` v1.3.1 | 13-item pre-flight checklist for every UT |

---

## 7. Documentation Anchors

Existing docs that already specify what this BAR builds. Planner must not invent — only assemble.

| Claim / Constraint | Existing Documentation Anchor |
| --- | --- |
| Migration filename is `0019_four_brain_run.sql` | `four-brain.yaml` Block 9 `data.d1.tables[1].schema_source` |
| D1 binding is `D1_MISSION_CONTROL` | `four-brain.yaml` Block 9 `data.d1.binding` |
| Tables are `four_brain_run` + `four_brain_transition` | `four-brain.yaml` Block 9 `data.d1.tables[]` (full column spec) |
| Errors go to `mission-control.squawks` keyed `process_id='four-brain'` + `subject_id='processes'` | `four-brain.yaml` Block 9 `data.write` + PROC-070 §5 WRITE |
| LBB row schema — referenced by `_ref:`, NOT redefined | `four-brain.yaml` Block 11 `lbb.lbb_row_schema._ref` |
| 10 gates G01-G10, all `tolerance: exact_match`, `failure_impact: BLOCK` | `four-brain.yaml` Block 11 `gates.gate_ids[]` |
| Generic dispatch pattern `/inbox` + `/inbox/claim` + PATCH | memory `reference_dispatch_system.md` + `mission-control-api/MANUAL.md` |
| Foreman produces no Library artifact (routing only) | PROC-070 §4 Step 3 + `four-brain.yaml` nodes `02-foreman.output: dispatch packets (no Library artifact)` |
| Mechanic ≠ Auditor (different inference engines) | PROC-070 §1 Aviation Rule + memory `feedback_codex_certifies_not_operator.md` |
| Atlas registry row 9 `four-brain-doctrine-gate` is the gate spec source of truth | `imo-creator-v2/atlas/manifests/paired-artifacts.yaml` |
| 4-gate sequence: Dispatch → Build → Audit → Close | `imo-creator-v2/atlas/WORK_ORDER.md` |
| 17 locked constants — only `atlas/ATLAS.md` is mechanic-eligible | CLAUDE.md "Seventeen Constants" + memory `feedback_never_touch_locked_constants.md` |

---

## 8. Research / Brainstorming Packet

| Input Type | Location / Record | How Planner Should Use It |
| --- | --- | --- |
| Sovereign architectural decision (this session, 2026-05-05) | This intake §19 + session log | Sovereign chose Option C (extend `mission-control-api`, don't fork) over Option A (reuse generic `/inbox`) and Option B (filesystem queues). Treat this as locked. |
| Prior dispatch system precedent | memory `reference_dispatch_system.md` | The four-brain runtime extends an already-working pattern. Does not invent. |
| Prior four-brain BAR run (BAR-FCE-RUN-060-PLANNER) | `garage/runs/BAR-FCE-RUN-060-PLANNER/20260505T185307Z/` | Mid-flight at REVIEW_MECHANIC_OUTPUT under the OLD runner. The BAR's existence proves the current filesystem-based runner works end-to-end. The refactor must not break this BAR's ability to complete OR must migrate its state into the new system. Planner decides. |
| LBB historical query | LBB worker (live, `LBB_API_KEY` in Doppler) | Planner SHOULD pull any prior records on `four-brain` / `inbox` / `four_brain_run` / `BAR-FOUR-BRAIN-CLI` before drafting. Worker confirmed live in this session. |

Fact handling rule:

```text
Brainstorming is input, not certification. Sovereign's Option C decision is
locked (§19). Everything else in this section is signal, not gospel.
```

---

## 9. LB&B Pull Contract

| LB&B Field | Fill |
| --- | --- |
| Work IDs / BAR IDs | BAR-FOUR-BRAIN-CLI, BAR-PROC-070, BAR-FCE-RUN-060-PLANNER |
| Search Terms | "four-brain", "four_brain_run", "inbox outbox", "BAR-FOUR-BRAIN-CLI", "0019_four_brain_run", "mission-control-api four-brain" |
| Time Window | All history (no prior records expected — this is the first BAR for this scope) |
| Required Records | Planner notes, Foreman dispatches, Mechanic outputs, Auditor verdicts for any prior four-brain-runtime work; closeout logs; CERTIFY rows |
| Evidence Needed For P=1 | Exactly 4 transition rows in `lbb.records` for this BAR + 1 Audit Book row + 1 CERTIFY row in `lbb.logbook`. Smoke-test BAR run produces same. |

LB&B rule per CLAUDE.md applies. LBB worker live; auth via `LBB_API_KEY` in Doppler `imo-creator/dev`.

---

## 10. Connector / Run Binding

| Connector | Required? | Purpose | Credential / Access Source | Evidence Expected |
| --- | --- | --- | --- | --- |
| LBB | yes | Pull prior memory; write 4 role transitions + Audit Book + CERTIFY for this BAR | Doppler `LBB_API_KEY` (project=imo-creator, config=dev) | Query results, transition rows, Audit Book row, CERTIFY row |
| Atlas | yes | Resolve KEY, BS Law, Book Law, FOUR_BRAIN_AVIATION, paired-artifacts row 9 | Local repo path | Cited file paths + sections in Plan Book |
| GitHub | yes | Push migration + worker code + runner refactor + UT Books + Audit Book | GitHub CLI / git push | Branch, commit SHA, push confirmation |
| Cloudflare D1 | yes | Apply migration `0019_four_brain_run.sql` to `mission-control` D1 (local + remote); read/write rows during smoke test | wrangler + Doppler/wrangler.toml | Migration applied evidence (`wrangler d1 migrations list`); rows written/read during smoke test |
| Cloudflare Workers | yes | Deploy extended `mission-control-api` worker | wrangler + Doppler | Deployment URL + version ID |
| Mission Control dashboard | yes | Surface four-brain BARs alongside generic dispatches | Existing MC dashboard | Dashboard query that returns the smoke-test BAR's run row |
| Linear | optional | Track BAR-FOUR-BRAIN-CLI status if a Linear issue exists | Linear connector | BAR URL/ID and status snapshot |

Connector rule per template applies. No silent omissions.

---

## 11. Process 070 Start Contract

Standard sequence per template §11. Inbox folder created via `forebrain-garage.sh new BAR-FOUR-BRAIN-CLI`. Plan Book lands at `Barton-Processes/docs/plans/BAR-FOUR-BRAIN-CLI/PLAN-BOOK.md`. Sovereign signs Plan Book before Foreman dispatch.

---

## 12. Non-Drift Invariants

| ID | Invariant |
| --- | --- |
| INV-FB-CLI-01 | PROC-070 doctrine (PROCESS-UT.md, four-brain.yaml, FOUR_BRAIN_AVIATION.md) does not change. This BAR builds runtime that conforms; it does not amend doctrine. |
| INV-FB-CLI-02 | D1 binding name is exactly `D1_MISSION_CONTROL` per `four-brain.yaml` Block 9. |
| INV-FB-CLI-03 | Migration filename is exactly `0019_four_brain_run.sql` per `four-brain.yaml` Block 9. |
| INV-FB-CLI-04 | Tables `four_brain_run` and `four_brain_transition` carry the columns specified in `four-brain.yaml` Block 9. Codex audit uses parsed-value parity (G06), not byte identity. |
| INV-FB-CLI-05 | LBB row schema is referenced by `_ref:` to `atlas/manifests/four-brain-doctrine-gate.yaml#lbb_row_schema` — NOT redefined locally (G07). |
| INV-FB-CLI-06 | Filesystem `garage/runs/{BAR}/{ts}/` is RETAINED as the durable artifact store (Plan Books, UT Books, Audit Books). D1 holds queue state + telemetry + transitions, not full artifact bodies. |
| INV-FB-CLI-07 | Mechanic ≠ Auditor at every transition. Sonnet builds; Codex audits. |
| INV-FB-CLI-08 | Foreman produces no Library artifact. Foreman dispatches and routes only. |
| INV-FB-CLI-09 | LLM is never on the spine of any gate evaluation. `determinism_gate: ai_on_spine_forbidden` per FOUR_BRAIN_AVIATION v1.2.0. |
| INV-FB-CLI-10 | Sixteen of seventeen locked constants are read-only for the Mechanic. Only `atlas/ATLAS.md` is mechanic-eligible (G09); even that requires sovereign-signed Plan Book pre-authorization. |
| INV-FB-CLI-11 | Atlas registry row 9 (`four-brain-doctrine-gate`) is the gate spec source of truth — Auditor reads gate predicates from there. |
| INV-FB-CLI-12 | Mid-flight BAR-FCE-RUN-060-PLANNER must either be allowed to complete on the OLD runner OR have its state migrated into the new system. Planner decides; Mechanic implements; Auditor verifies no orphaned BAR. |
| INV-FB-CLI-13 | All commits pair code + UT doc together (CLAUDE.md gate 2 / WORK_ORDER.md gate 2). No code-only or doc-only commits. |
| INV-FB-CLI-14 | BS Law Y-junction syntactic separation on every paired YAML the Mechanic produces. |

---

## 13. Input Contract

| Input | Required? | Rule |
| --- | --- | --- |
| Target process | provided | PROC-070 / four-brain pipeline runtime |
| Desired outcome | provided | §2 |
| Blueprint home | provided | §4 row 1 |
| Execution home | provided | §4 row 2 |
| Runtime surface | provided | §4 row 3 — `mission-control-api` worker |
| Evidence target | provided | §4 row 4 — D1 + LBB |
| Brainstorming packet | provided | §8 |
| LB&B search contract | provided | §9 |
| Connector/run binding | provided | §10 |
| Protected constraints | provided | §12 (14 invariants) |
| P=1 definition | provided | §18 |

---

## 14. Storage / Evidence Contract

| Store | Role | Timing |
| --- | --- | --- |
| GitHub | Versioned source for migration, worker code, runner refactor, UT Books, Plan Book, Audit Book | After audited file changes; commits pair code + UT |
| D1 (`mission-control`) | Registry + queue state + telemetry. Tables `four_brain_run`, `four_brain_transition`, `squawks`. | After migration applied; rows written during smoke test |
| LBB | Compliance logbook + durable memory. Subject `processes`. | At each role transition + on Audit Book + on CERTIFY |
| Mission Control dashboard | Operator visibility for four-brain BARs | During smoke test + ongoing |
| Filesystem `garage/runs/{BAR}/{ts}/` | Durable artifact bodies (Plan Book MD, UT Books, Audit Book MD) | Throughout BAR lifecycle. NOT replaced by D1. |
| R2 | Not used for this BAR | N/A |

---

## 15. Planner Deliverables

Per template — full set required. At minimum:

- Plan Book path: `Barton-Processes/docs/plans/BAR-FOUR-BRAIN-CLI/PLAN-BOOK.md`
- Read set as proposed in §6 (Planner may add)
- Source-of-truth split as in §4
- Required artifacts: migration SQL + extended worker code + refactored runner + UT Books for each new Library artifact + Audit Book on PASS
- Mechanic work orders as **literal `file:line | old_string | new_string` triples** (per memory `feedback_work_packet_literal_pairs.md`)
- Auditor packet referencing `four-brain.yaml` Block 11 gates G01-G10 + this BAR's BAR-specific gates if any
- P=1 definition (§18)
- Stop conditions (each strike level + Strike-3 Troubleshoot/Train trigger)
- Open blockers (currently §19's sovereign decision is the only one)
- Evidence requirements (§14)
- LBB records used (queries) and required (4 transitions + Audit Book + CERTIFY)
- Connectors used (§10)
- 070 start/handoff path: `garage/inbox/BAR-FOUR-BRAIN-CLI/` → Planner run → `docs/plans/BAR-FOUR-BRAIN-CLI/PLAN-BOOK.md` → sovereign sign → Foreman dispatch
- Brainstorming claims promoted to facts: Option C is locked (§19); migration filename + table names + binding from doctrine
- Brainstorming claims left as assumptions: how to handle mid-flight BAR-FCE-RUN-060-PLANNER (Planner proposes)

---

## 16. Mechanic Dispatch Hints

```text
Allowed write scope (Planner refines in Plan Book §3):
- imo-creator-v2/workers/mission-control-api/migrations/0019_four_brain_run.sql (new file)
- imo-creator-v2/workers/mission-control-api/src/                                 (new four-brain routes)
- imo-creator-v2/workers/mission-control-api/wrangler.toml                        (binding edits if needed)
- imo-creator-v2/workers/mission-control-api/MANUAL.md                            (doc the new routes)
- Barton-Processes/factory/imo-creator/070-four-brain/garage/forebrain-garage.sh  (refactor to call API)
- Barton-Processes/factory/imo-creator/070-four-brain/PROCESS-UT.md               (mark §11 OUT OF SCOPE item completed; bump version + Last Modified per memory feedback_pair_version_with_last_modified.md)
- Barton-Processes/factory/imo-creator/070-four-brain/four-brain.yaml             (mirror §11 status update if applicable; preserve all locked specs)
- Barton-Processes/docs/plans/BAR-FOUR-BRAIN-CLI/                                 (Plan Book + Audit Book)
- imo-creator-v2/atlas/manifests/paired-artifacts.yaml                            (registry row for any new UT Book; if row 9 changes, this is an Atlas-touch — Planner decides whether to scope it in this BAR)

Forbidden:
- Editing any of the 17 locked constants except atlas/ATLAS.md (and that only with sovereign-signed Plan Book pre-authorization per G09).
- Any byte changes to PROC-070 doctrine column specs / binding name / migration filename in four-brain.yaml Block 9 (parsed-value parity is enforced; INV-FB-CLI-04).
- Mechanic auditing its own work.
- Code-only or doc-only commits.
- LLM in the spine of any gate evaluation.
- Editing dyno-engine/engine/us.py or up.py (read-only locked).
```

---

## 17. Auditor Packet Requirements

Codex (different inference engine than Sonnet mechanic) audits the following at minimum:

| Audit Area | Evidence |
| --- | --- |
| BS Law Y-junction | Every paired YAML in this BAR has `outside:` and `inside:` as syntactically distinct top-level maps |
| UT conformance | Every UT Book has 13-item pre-flight checklist (UT_CHECKLIST v1.3.1) + 14 sections (UT v2.8.0) |
| Source-of-truth split | §4 of this intake holds — runtime conforms to blueprint, no doctrine drift |
| Scope | Only `MODIFY` paths from §16 changed |
| Runtime safety | `wrangler dev` green; no migration data loss; smoke test produces expected rows |
| Evidence | 4 LBB transition rows + Audit Book row + CERTIFY row + D1 `four_brain_run` row + `four_brain_transition` rows for smoke-test BAR |
| Connector evidence | All §10 connectors either used (with proof) or marked blocked/deferred |
| Aviation | Mechanic (Sonnet) ≠ Auditor (Codex). Confirmed at every transition. |
| Doctrine parity | `four-brain.yaml` Block 9 parsed values match the migration + worker code (G06 parsed_value_match) |
| 10 gates | G01-G10 from `four-brain.yaml` Block 11 all PASS for the smoke-test BAR |
| Locked constant purity | `git diff base..HEAD -- <16 read-only constants>` returns empty (G09) |

Verdict format: `VERDICT: P=1` or `VERDICT: P=0` with scoped file:line citations.

---

## 18. P=1 Definition

P=1 when ALL of the following hold:

1. `imo-creator-v2/workers/mission-control-api/migrations/0019_four_brain_run.sql` exists, applied to the local mission-control D1 AND the remote production D1, and creates exactly the columns specified in `four-brain.yaml` Block 9 for both `four_brain_run` and `four_brain_transition`.
2. `mission-control-api` worker exposes new four-brain routes (Planner names final paths; suggested: `POST /four-brain/dispatch`, `POST /four-brain/claim/:role`, `POST /four-brain/transition`, `GET /four-brain/state/:bar`). All authed via existing `MC_API_KEY` (`X-API-Key` header) per existing dispatch convention.
3. `forebrain-garage.sh` refactored: state transitions go through new API routes; filesystem `runs/{BAR}/{ts}/` is preserved for artifact bodies but is no longer the queue source of truth.
4. End-to-end smoke test BAR (a no-op BAR — Plan Book signed, Mechanic builds nothing, Auditor PASSES) runs through the new system and produces:
   - 1 `four_brain_run` row with `verdict='PASS'`
   - 4 `four_brain_transition` rows (planner / foreman / mechanic / auditor)
   - 4 `lbb.records` rows (one per role)
   - 1 `lbb.records` Audit Book row (`subject_id='processes'`, `species='Audit-Body'`)
   - 1 `lbb.logbook` CERTIFY row
   - 0 unresolved `mission-control.squawks` rows for this BAR
5. PROC-070 PROCESS-UT.md §11 OUT OF SCOPE row for `BAR-FOUR-BRAIN-CLI` flipped to "completed" with version + Last Modified bumped together (per memory `feedback_pair_version_with_last_modified.md`).
6. Mid-flight BAR-FCE-RUN-060-PLANNER either completed under the old runner before this BAR commits, OR migrated cleanly into the new system with no data loss. Planner picks the path; Auditor confirms no orphaned BARs.
7. Codex Auditor returns `VERDICT: P=1` with all 10 gates from `four-brain.yaml` Block 11 PASS.
8. All commits pair code + UT doc together (WORK_ORDER.md gate 2).
9. `git diff base..HEAD -- atlas/constants/ atlas/manifests/STRUCTURE_MANIFEST.yaml atlas/skills/ atlas/dyno/us.py atlas/dyno/up.py` returns empty for the 16 read-only locked constants (G09). Only `atlas/ATLAS.md` may change, and only if the Plan Book pre-authorizes it (Planner decides; sovereign signs).
10. Mission Control dashboard surfaces the smoke-test BAR's run row.

---

## 19. Sovereign Resolutions (signed 2026-05-05)

All three open questions resolved by sovereign before READY_FOR_PLANNER flip.

| # | Question | Resolution | Cite |
| --- | --- | --- | --- |
| 1 | Mid-flight BAR-FCE-RUN-060-PLANNER — finish on old runner first, or migrate into new system? | **Leave 060 alone. This BAR is greenfield.** BAR-FCE-RUN-060-PLANNER continues on the old runner. The new runtime does not touch its state. | Sovereign 2026-05-05 |
| 2 | Atlas amendment scope — is this BAR allowed to amend `atlas/ATLAS.md`? | **NO. This BAR may not touch `atlas/ATLAS.md`.** Any registry updates are a follow-up BAR (e.g. BAR-LOCK-*). G09 stays at "16 read-only locked constants" — `atlas/ATLAS.md` is in scope of NO modification for this BAR specifically. | Sovereign 2026-05-05 |
| 3 | Strike-ladder routing logic — where does it live? | **Foreman role owns the routing decision; runner is the invocation host.** Per `FOUR_BRAIN_AVIATION.md` §STRIKE SYSTEM + PROC-070 §4 Step 6 + memory `feedback_auditor_decides_pass_fail.md` ("Foreman only dispatches and reviews"), the Foreman reads strike-count from D1 and decides which mechanic to invoke (Sonnet → Opus 4.7 → Troubleshoot/Train). The runner (`forebrain-garage.sh` equivalent post-refactor) hosts the Foreman invocation and provides strike-count from the `four_brain_run` D1 row. Worker does not make the decision; it stores data only. | Sovereign 2026-05-05; doctrine FOUR_BRAIN_AVIATION.md §STRIKE SYSTEM lines 196-204 + PROC-070 §4 Step 6 |

**Status flipped DRAFT → READY_FOR_PLANNER 2026-05-05.**

---

## Document Control

| Field | Value |
| --- | --- |
| Created | 2026-05-05 |
| Last Modified | 2026-05-05 |
| Version | 1.0.0 (sovereign-signed) |
| Authority | Dave Barton (sovereign) — signed 2026-05-05 |
| Status | READY_FOR_PLANNER |

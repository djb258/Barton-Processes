# Outreach Operating Cadence

Date: 2026-05-04
BAR: BAR-377
Scope: Process cadence for outreach email execution and upstream signal refresh

## Purpose

This note records the operating model for the outreach processes that feed daily email execution. It is a cadence reference for the BAR-377 process audit set, not a replacement for the per-process UTs or process YAMLs.

## Daily Lane

The daily operating job is the Chrome outbound email lane. Its purpose is to get out as many compliant emails as possible each day while respecting suppression, bounce, reply, unsubscribe, and logging gates.

Daily execution should consume the freshest available People, SP/social, DOL, and LCS signals, then write delivery evidence back to the system of record used by Mission Control and LCS.

Primary daily candidates:

| Process | Role In Daily Lane | Current Audit State |
|---------|--------------------|---------------------|
| bp.100 | LCS daily fire / visibility layer | P=0 source drift; live worker appears sourced outside this repo |
| bp.700 | Campaign engine / send preparation | Stage 5 TODO; upstream dependency currently unresolved |
| Chrome job | Email operator execution surface | Needs explicit process wrapper and logging contract |

## Monthly Refresh Lane

The monthly lane updates signal sources that change over time but do not need heavy daily refresh. These processes should update the data that daily outbound uses for targeting and prioritization.

Monthly refresh candidates:

| Process | Refresh Target | Cadence |
|---------|----------------|---------|
| bp.200 | People baseline and people-facing records | Monthly |
| bp.201 | People email enrichment backlog | Monthly or controlled batch until backlog is cleared |
| bp.202 | People LinkedIn/social enrichment backlog | Monthly or controlled batch until backlog is cleared |
| bp.300 | SP/social platform source discovery | Monthly |
| bp.301 | SP/social platform page parsing | Monthly or event-driven after bp.300 changes |
| bp.500 | Talent flow joins after People/SP refresh | Monthly after upstream refreshes are stable |

## Static Reference Lane

DOL is treated as static/reference data for this workflow. It should be checked for availability and dictionary alignment, but it should not block daily Chrome email execution unless the daily lane depends on a DOL field that is missing or materially stale.

Static/reference candidate:

| Process | Role | Cadence |
|---------|------|---------|
| bp.400 | DOL views and reference joins | Check/static validation; refresh only when source or dictionary changes |

## Current Blockers

| Blocker | Impact | Required Resolution |
|---------|--------|---------------------|
| bp.100 source drift | Daily LCS fire cannot be certified from this repo alone | Decide whether Barton-Processes owns bp.100 or whether the live `lcs-hub` source repo is authoritative |
| bp.600 decision state | Campaign dependency chain is unclear | Decide whether BIT scoring is retired, static, or still required before bp.700 |
| Chrome job wrapper missing | Daily email execution is not yet represented as a process with a logging contract | Add or identify the process wrapper that launches Chrome and logs daily send evidence |
| bp.500 local runtime | Local dry-run requires `psql` or a runtime replacement | Install `psql` locally or convert runtime to a non-CLI Postgres client |
| bp.301 classifier warning | Page parser can run, but title classification is degraded | Wire Title Classifier or document it as non-blocking for monthly SP refresh |

## Operating Rule

Daily email execution should not wait on monthly refresh completion unless a required join is missing. Monthly processes improve the signal quality feeding the daily lane; they are not the daily outbound mechanism.


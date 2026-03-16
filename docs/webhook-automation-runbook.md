# uHOME-empire Webhook Automation Runbook

## Purpose

Describe how to operate the configurable webhook and outbound API lane in
`uHOME-empire`.

This is a runbook for the scaffolded v2 direction, not a claim that the full
runtime already exists.

## What This Lane Owns

- cron-type scheduled sync jobs
- inbound webhook receiver contracts
- outbound API call jobs for remote services
- Google and HubSpot sync triggers
- reusable templates for future providers

## What This Lane Does Not Own

- Home Assistant or Matter automation
- Apple-native desktop sync
- canonical workflow semantics
- the base Linux host runtime

## Contract Surfaces

Primary repo anchors:

- `src/webhooks/webhook-server-template.json`
- `src/webhooks/connection-template.json`
- `src/webhooks/google-sync-template.json`
- `src/webhooks/hubspot-sync-template.json`
- `src/containers/container-job-catalog.json`
- `examples/configurable-webhook-server.json`
- `scripts/smoke/integration_preflight.py`
- `scripts/smoke/contract_smoke.py`

## Operating Model

### Inbound flow

1. receive an authenticated webhook event
2. map the event to a vault-first workflow or sync action
3. pull any required remote state
4. write reviewed artifacts or sync state back into repo-owned outputs

### Scheduled flow

1. trigger a cron-type job
2. inspect local source-of-truth records
3. call a provider API
4. record sync status, conflicts, or follow-up work

## Security Baseline

- secrets must come from environment or an approved secret store
- inbound webhooks must verify a shared secret or provider signature
- remote APIs must use scoped credentials
- sync jobs should fail closed when auth is missing or invalid

## Review Baseline

Use human review before:

- changing contact identity fields
- creating CRM-visible records from ambiguous input
- publishing customer-facing side effects from a newly added provider

## First Implementation Priorities

1. stable secret and connection loading
2. shared job envelope for scheduled and inbound triggers
3. sync-status artifacts that are operator-readable
4. provider adapters for Google and HubSpot
5. reusable provider template for future APIs

## Current Family Advancement

The current family working-system pass now provides:

- shared `automation-job` and `automation-result` contracts from `uDOS-core`
- `uHOME-server` queue and result runtime surfaces
- `uHOME-empire` sync-package export
- `uHOME-empire` automation-job queue handoff
- `uHOME-empire` automation-result recording for local end-to-end probes
- `uHOME-empire` process-next and result-fetch runtime probes against `uHOME-server`

This means the scaffold now covers the contract loop for:

1. package generation
2. automation job queueing
3. automation job processing
4. automation result fetch and summary

Provider mutation remains scaffolded, but the automation contract path is no
longer only documentation.

HubSpot lane promotion note:

- HubSpot now has an active lane gate for package, transport, and local
  automation-runtime validation via `scripts/smoke/hubspot_lane_gate.py`
- remote provider mutation remains approval-gated and secret-backed through
  Wizard; this repo does not own credential storage

## Current Local Runtime Probe

The local sibling-app probe now exercises:

1. queue lane-scoped automation jobs into `uHOME-server`
2. call `/api/runtime/automation/process-next` once per queued job
3. read `/api/runtime/automation/results`
4. summarize statuses and channels for operator inspection

Primary smoke entry:

- `scripts/smoke/sync_plan.py --channel hubspot-sync --local-uhome-automation-runtime --json`

## Failure Handling

Minimum failure artifacts should capture:

- job id
- provider or webhook source
- attempted operation
- last error
- retry eligibility
- operator review requirement

## Validation Rule

Before treating a new provider lane as active:

1. add or update a template in `src/webhooks/`
2. add an inspectable example in `examples/`
3. extend validation if the contract shape changes
4. document ownership and review policy in this runbook or a provider-specific addendum

## Current Script Scaffolds

The current repo keeps v2-safe scaffolds rather than old internal Empire
runtime scripts:

- `scripts/smoke/integration_preflight.py` checks template presence and env vars
- `scripts/smoke/contract_smoke.py` validates inspectable JSON contract assets

These preserve the old preflight/smoke shape without assuming live provider
mutation or the archived module layout.

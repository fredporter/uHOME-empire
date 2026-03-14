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

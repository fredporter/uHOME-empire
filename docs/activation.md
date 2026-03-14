# uHOME-empire Activation

## Purpose

This document marks the first active implementation tranche for
`uHOME-empire`.

The activation goal is to make the renamed repo checkable and ready for the new
always-on sync direction without broadening ownership beyond:

- vault sync orchestration for configured local-network vaults
- Google workspace mirror and projection flows
- HubSpot task and contact sync surfaces
- console CRM and workflow contracts
- lightweight validation for repo-owned boundaries

## Activated Surfaces

- `src/` as the sync and workflow contract lane
- `src/webhooks/` as the configurable webhook and API contract lane
- `scripts/run-empire-checks.sh` as the repo validation entrypoint
- `tests/` as the workflow contract validation lane
- `config/` as the checked-in operational config lane
- `examples/basic-empire-flow.json` as the smallest sync-oriented workflow
  example
- `examples/configurable-webhook-server.json` as the base cron-type webhook
  server example

## Current Validation Contract

Run:

```bash
scripts/run-empire-checks.sh
```

This command:

- verifies the required repo entry surfaces exist
- checks that the sample workflow contract is structurally valid
- rejects private local-root path leakage in tracked repo docs and scripts
- enforces renamed repo validation output

## Boundaries

This activation does not move ownership into `uHOME-empire` for:

- Apple-native desktop sync behavior
- web publishing and email pathways
- canonical runtime semantics
- base `uHOME-server` host runtime ownership

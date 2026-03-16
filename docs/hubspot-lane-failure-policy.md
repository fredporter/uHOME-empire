# uHOME-empire HubSpot Lane Failure Policy

## Purpose

Define the active failure and review policy for the HubSpot provider lane in
`uHOME-empire`.

This policy is for lane operation and promotion safety. It does not move secret
ownership or provider routing ownership out of Wizard.

## Ownership

- `uHOME-empire` owns pack payloads, mappings, and operator-visible lane status
- `uDOS-wizard` owns secret-backed provider credentials and routing policy
- `uHOME-server` owns local queue, process-next, and result runtime fulfillment

## Active Gate

HubSpot lane promotion and regression checks must pass:

- `scripts/smoke/hubspot_lane_gate.py --json`

The gate validates:

- channel scoping to `hubspot-sync`
- projection and target-system slicing
- Wizard transport handoff semantics
- local queue, process-next, and result-fetch runtime loop

## Failure Classes

### Class A: Contract mismatch

Examples:

- channel drift away from `hubspot-sync`
- projection target drift away from `hubspot-activity`
- missing required contract fields

Policy:

- fail closed
- do not dispatch lane mutation
- block promotion until contract alignment is restored

### Class B: Transport or orchestration failure

Examples:

- Wizard orchestration probe fails
- dispatch metadata is incomplete

Policy:

- fail closed for provider mutation
- allow contract-only inspection and dry-run review
- require operator review before retrying

### Class C: Local runtime fulfillment failure

Examples:

- queue step returns non-200
- process-next fails
- result fetch fails

Policy:

- mark lane run as failed
- do not claim lane health
- require local runtime recovery before lane promotion

## Retry Rule

Retries are allowed only after a clear failure cause is identified.

Required before retrying:

- capture lane, channel, and failing step
- capture last error message
- record whether operator approval is required

## Review Rule

Any operation that changes contact identity-level HubSpot fields must stay
review-gated.

Do not allow silent merges of ambiguous contact identity records.

## Promotion Rule

Before accepting a HubSpot lane change as `active`:

1. run `scripts/run-empire-checks.sh`
2. run `scripts/smoke/hubspot_lane_gate.py --json`
3. update `docs/provider-lane-status.md` if status language changes
4. update this policy if failure behavior changes

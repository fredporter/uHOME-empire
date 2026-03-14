# uHOME-empire

## Purpose

Linux-based uHOME extension for always-on vault sync, Google workspace mirrors,
HubSpot sync, and console-style workflow or CRM operations.

## Ownership

- local-network vault sync orchestration for configured user vaults
- always-on Google Docs mirror sync and Google Keep or Tasks projection
- HubSpot contact and task sync using app-owned user or binder contact records
  plus locally collated enrichment
- cron-type webhook triggers and configurable outbound API call jobs
- reusable templates for custom online API and webhook connections
- console-style task, workflow, contacts, and CRM surfaces

## Non-Goals

- Apple, iCloud, AppleScript, and native macOS sync ownership
- canonical runtime semantics owned by `uDOS-core`
- network control-plane ownership owned by `uDOS-wizard`
- base Linux host runtime ownership owned by `uHOME-server`

## Spine

- `src/`
- `docs/`
- `tests/`
- `scripts/`
- `config/`
- `examples/`

## Local Development

Keep vault-first sync contracts modular and reusable. Treat Google and HubSpot
as mirrors or projection targets rather than the canonical source of truth, and
use the macOS app's contact records as the upstream source for HubSpot sync.

## Family Relation

`uHOME-empire` sits between local `uHOME` infrastructure and remote services.
It uses `uDOS-core` semantics, relies on `uDOS-wizard` for online networking,
and leaves Apple-native sync to the private macOS app.

## Activation

The v2 repo activation path is documented in `docs/activation.md`.
The `v2.0.1` sync alignment is documented in
`docs/v2.0.1-sync-alignment.md`.

Run the current repo validation entrypoint with:

```bash
scripts/run-empire-checks.sh
```

# uHOME-empire

## Purpose

Linux-based uHOME extension for outbound operations, publishing, audience
workflows, and reusable automation packs, with always-on sync and provider
handoff as one part of that broader role.

## Ownership

- local-network vault sync orchestration for configured user vaults
- always-on Google Docs mirror sync and Google Keep or Tasks projection
- HubSpot contact and task sync using app-owned user or binder contact records
  plus locally collated enrichment
- cron-type webhook triggers and configurable outbound API call jobs
- reusable templates for custom online API and webhook connections
- zapier-like remote job and container definitions consumed by the base runtime
  as checked-in contracts
- publishing, messaging, contact, and campaign operation packs
- educational make-and-deploy pathways for inspectable workflow systems
- console-style task, workflow, contacts, and CRM surfaces

## Non-Goals

- Apple, iCloud, AppleScript, and native macOS sync ownership
- canonical runtime semantics owned by `uDOS-core`
- network control-plane ownership owned by `uDOS-wizard`
- base Linux host runtime ownership owned by `uHOME-server`

## Spine

- `packs/`
- `schemas/`
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

`uHOME-server` remains the runtime host and ingest surface. `uHOME-empire`
owns the remote job/container definitions and sync workflow contracts that the
host may inspect or execute.

This now includes the family-aligned automation-job and automation-result loop
that became usable during the `v2.0.2` working-system pass.

This repo should now be read as an operations-container workbench, not only as
a sync utility repo.

## Core Docs

- `docs/overview.md`
- `docs/architecture.md`
- `docs/make-pathway.md`
- `docs/containers.md`
- `docs/contacts-and-audiences.md`
- `docs/publishing.md`
- `docs/roadmap.md`
- `docs/quickstart.md`

## Activation

The v2 repo activation path is documented in `docs/activation.md`.
The `v2.0.1` sync alignment is documented in
`docs/v2.0.1-sync-alignment.md`.

Run the current repo validation entrypoint with:

```bash
scripts/run-empire-checks.sh
```

Starter sync-envelope examples now live in `examples/basic-sync-record-envelope.json`
for contacts, activities, binder/project routing, and sync-state records.

Starter operational packs now live under `packs/` and align to
`schemas/pack-manifest.schema.json`.

The current starter library includes campaign, publishing, messaging, and
contact-operation packs, with catalog and pack-run smoke scripts under
`scripts/smoke/`.

Queueable sync packages can be emitted and handed off through:

```bash
python3 scripts/smoke/sync_plan.py --json --write-package /tmp/sync-package.json
python3 scripts/smoke/sync_plan.py --json --local-uhome-app
python3 scripts/smoke/sync_plan.py --json --channel hubspot-sync --local-uhome-automation-cycle
python3 scripts/smoke/sync_plan.py --json --channel hubspot-sync --local-uhome-automation-runtime
```

# uHOME-empire Architecture

uHOME-empire is the always-on sync and console extension for uHOME. It handles
remote service projection and CRM organization that should not live in the
macOS desktop app or the base Linux host runtime.

## Main Areas

- `src/` holds reusable sync and workflow contracts.
- `examples/` demonstrates vault-first sync flows.
- `docs/` explains repo boundaries and cross-repo ownership.
- `scripts/run-empire-checks.sh` is the activation validation entrypoint.

Key companion docs:

- `docs/contact-and-crm-model.md`
- `docs/webhook-automation-runbook.md`
- `docs/provider-lane-status.md`
- `docs/provider-template-patterns.md`
- `docs/v2.0.1-sync-alignment.md`

## Integration Lane

The integration lane is designed to act like a configurable webhook server for
online services that should stay outside the base `uHOME-server` runtime:

- cron-type scheduled triggers for outbound sync jobs
- inbound webhook contracts for event-driven sync
- provider-specific API call templates
- shared connection templates for new services beyond Google and HubSpot

## Operating Split

- `uHOME-server` owns the Linux host runtime, local-network services, and local
  vault viewing or unlock surfaces.
- `uHOME-empire` owns Google and HubSpot always-on sync, webhook-style actions,
  and console CRM or workflow surfaces.
- `omd-mac-osx-app` owns Apple-native sync plus web publishing and email
  pathways, including the user and binder contact databases.
- `uDOS-wizard` owns online networking and provider bridge contracts used by
  empire when work leaves the local network.
- `uDOS-shell` supplies shared shell interaction language when empire workflows
  are presented through public operator surfaces.

## Legacy Inputs

Relevant v1.8 concepts should be assessed through the family-level relevance
review in `uDOS-docs/architecture/05_v1_archive_relevance_assessment.md`
instead of being copied forward wholesale.

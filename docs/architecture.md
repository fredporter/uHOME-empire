# uHOME-empire Architecture

uHOME-empire is an operations-container extension for uHOME. It handles
outbound workflows, reusable pack structure, provider-aware publishing or
messaging operations, and the sync or automation lanes that should not live in
the private macOS desktop app or the base Linux host runtime.

## Main Areas

- `src/` holds reusable sync, pack, record-profile, and handoff contracts.
- `src/containers/` holds empire-owned remote job and container definitions.
- `examples/` demonstrates inspectable sync, automation, and future pack flows.
- `docs/` explains repo boundaries, Make-pathway intent, and cross-repo ownership.
- `scripts/run-empire-checks.sh` is the activation validation entrypoint.

Key companion docs:

- `docs/overview.md`
- `docs/make-pathway.md`
- `docs/containers.md`
- `docs/contacts-and-audiences.md`
- `docs/publishing.md`
- `docs/roadmap.md`
- `docs/contact-and-crm-model.md`
- `docs/webhook-automation-runbook.md`
- `docs/provider-lane-status.md`
- `docs/provider-template-patterns.md`
- `docs/v2.0.1-sync-alignment.md`

## Top Layers

### Domain Layer

Defines operational concepts such as:

- contact
- audience
- campaign
- message
- publication
- asset
- channel
- workflow
- job
- report

### Pack Or Container Layer

Defines reusable units made up of:

- manifests
- templates
- transforms
- rules
- sample data
- tests

### Adapter Layer

Connectors for provider-specific execution such as:

- Google workspace lanes
- HubSpot
- web publish targets
- exports
- future messaging providers

### Make Or Education Layer

The learnable surface for:

- starter packs
- editable examples
- validation helpers
- safe test mode
- walkthroughs

### Execution Layer

Runs operational jobs with:

- dry-run support
- preview support
- approval gates
- logging
- reporting
- rollback notes where possible

## Integration Lane

The current implemented integration lane is still centered on sync and
automation surfaces that act like a configurable webhook and provider handoff
layer for services that should stay outside the base `uHOME-server` runtime:

- cron-type scheduled triggers for outbound sync jobs
- inbound webhook contracts for event-driven sync
- provider-specific API call templates
- shared connection templates for new services beyond Google and HubSpot
- queueable sync-package export for validated contact, activity, binder, and
  sync-state envelopes
- local and HTTP handoff into the `uHOME-server` sync-record ingest surface
- zapier-like remote job/container definitions that the base runtime can
  inspect without taking ownership of empire workflows

## Operating Split

- `uHOME-server` owns the Linux host runtime, local-network services, and local
  vault viewing or unlock surfaces, including sync-record envelope storage.
- `uHOME-matter` owns the local Matter and Home Assistant extension lane and
  stays separate from empire's online sync responsibilities.
- `uHOME-empire` owns operational packs, publishing or messaging workflows,
  contact and audience operations, Google and HubSpot sync lanes, webhook-style
  actions, and queueable package creation.
- shared public render/theme contracts own web and email output structure,
  while `omd-mac-osx-app` remains a consumer for Apple-native UX and contact
  database handling.
- `uDOS-wizard` owns online networking and provider bridge contracts used by
  empire when work leaves the local network.
- `uDOS-shell` supplies shared shell interaction language when empire workflows
  are presented through public operator surfaces.

## Legacy Inputs

Relevant v1.8 concepts should be assessed through the family-level relevance
review in `uDOS-docs/architecture/05_v1_archive_relevance_assessment.md`
instead of being copied forward wholesale.

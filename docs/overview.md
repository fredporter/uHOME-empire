# uHOME-empire Overview

## Definition

`uHOME-empire` is the uDOS v2 extension for outbound operations, publishing,
audience workflows, and educational make or deploy systems, packaged as
reusable scriptable containers rather than a monolithic business app.

## Position In The Family

`uHOME-empire` is not:

- the canonical runtime
- the base Linux host
- the family AI layer
- the shell foundation
- a monolithic CRM

`uHOME-empire` is:

- an operations container for outbound systems
- a home for reusable packs, scripts, mappings, and templates
- a public-facing make surface where users can inspect and adapt workflows
- a provider-aware extension that can run with or without Wizard assistance

## Repo Role Split

`uDOS-core` owns:

- command and workflow semantics
- binder and packaging contracts
- plugin and container capability contracts
- shared runtime truth

`uDOS-wizard` owns:

- AI assistance
- assisted generation
- provider and API routing
- budgeting and remote orchestration

`uHOME-server` owns:

- the always-on local runtime
- local execution and persistence surfaces
- queue, ingest, and result endpoints used by Empire

`uHOME-empire` owns:

- publishing systems
- campaign systems
- messaging workflows
- contact and audience operations
- reusable ops packs and scripts
- educational make-and-deploy patterns

## Operating Modes

Empire should work:

- manually
- with approval-gated local execution
- semi-assisted through Wizard
- fully disconnected from Wizard where deterministic local flows are enough

## Primary Repo Themes

- packs as portable operational units
- inspectable templates and mappings
- channel-aware execution
- dry-run and approval-first operation
- remixable examples for learning

## UX Direction

Empire should feel like an operations workshop or studio, not a monolithic
enterprise dashboard. The operator should be able to see what will happen,
which outputs will be created, and where approvals are required before live
writes are allowed.

## Safety And Approval Model

Empire workflows should default to:

- dry-run first
- explicit approve-before-send for high-impact actions
- clear failure policy per provider lane
- auditable execution logs and result surfaces
- rollback notes where reversible operations are possible

## Channel Strategy

Initial channel focus:

- email
- web publishing
- exports and reporting

Then expand toward:

- CRM sync
- webhook and automation lanes
- headless or syndicated content pathways

## Related Docs

- `docs/architecture.md`
- `docs/make-pathway.md`
- `docs/containers.md`
- `docs/contacts-and-audiences.md`
- `docs/publishing.md`
- `docs/roadmap.md`

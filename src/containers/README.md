# Containers

`src/containers/` is the empire-owned catalog for zapier-like remote jobs and
container definitions.

Current container surfaces:

- `container-job-catalog.json` as the top-level registry
- `google-workspace-sync-container.json` for Google mirror jobs
- `hubspot-sync-container.json` for HubSpot sync jobs
- `binder-release-webhook-container.json` for binder-triggered webhook jobs

Boundary rule:

- keep remote job definitions here
- keep local ingest and runtime hosting in `uHOME-server`

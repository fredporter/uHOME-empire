# uHOME-empire Containers

## Role

Empire should treat operational scripts as portable containers or packs, not as
loose one-off scripts.

Examples:

- `publish-site`
- `send-edm`
- `build-segment`
- `sync-contacts`
- `generate-campaign-pack`
- `prepare-event-launch`
- `run-followup-sequence`

## Container Expectations

Each operational container should declare:

- metadata
- inputs
- outputs
- required providers
- approval requirements
- dry-run behavior
- logs or reports
- templates or assets
- optional Wizard hooks

## Expected Pack Structure

Each pack should be able to include:

- a manifest
- templates
- transforms
- mappings
- prompts or instructions
- provider adapters
- sample data
- docs
- tests
- deploy notes

## Why This Matters

This allows a user to:

- run a workflow
- study the workflow
- clone the workflow
- modify the workflow
- redistribute the workflow as a reusable binder or pack

## Current Repo Anchors

The current repo already contains the first container-oriented surfaces:

- `packs/`
- `schemas/pack-manifest.schema.json`
- `src/containers/`
- `src/webhooks/`
- `examples/`
- `scripts/smoke/sync_plan.py`

Those surfaces currently emphasize sync and automation lanes. The broader pack
model should expand them into reusable publishing, messaging, audience, and
admin operations.

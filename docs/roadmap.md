# uHOME-empire Roadmap

## Direction

Empire is moving from a narrow sync-extension posture toward a broader
operations-container repo that still stays modular, inspectable, and safe.

## Phase 1: Foundations

- establish the repo spine for packs, templates, adapters, and schemas
- define domain models for operations concepts
- define pack manifests and dry-run execution expectations
- keep current sync and automation contracts aligned to family runtime surfaces
- add the first Make-pathway docs and starter examples
- add starter operational packs backed by inspectable manifests
- add pack catalog and operator report artifacts for reusable inspection

## Phase 2: Campaign And Audience Layer

- expand contact and company operational records
- add audience segmentation concepts
- add campaign pack structure
- add reporting outputs
- add approval workflow conventions

## Phase 3: Guided Make System

- add editable pack builders
- add validation helpers
- add walkthrough examples
- add safer practice and dry-run paths
- promote remixable starter projects

## Phase 4: Extended Adapters

- deepen HubSpot mapping support
- add WordPress or headless publishing adapters
- expand export and reporting options
- support shared library or community pack distribution

## Current Family Alignment

Recent family advancement matters here:

- `v2.0.2` shared runtime-service and working-system passes are complete
- `uDOS-core` now supplies shared sync and automation contracts
- `uHOME-server` now exposes ingest, queue, process, and result surfaces
- Empire currently consumes those surfaces for sync and automation scaffolds

That means the next Empire work should build upward from stable family runtime
contracts into richer pack, publishing, messaging, and Make-pathway features.

# Changelog

All notable changes to `uHOME-empire` should be documented in this file.

## Unreleased

- established v2 activation and repo-level validation workflow
- added sync, webhook, and CRM-facing public contract surfaces
- added `v2.0.2` runtime-service consumption metadata to sync plans
- switched sync-plan runtime-service consumption to the shared Core contract artifact
- added a Round B sync execution brief built from live Wizard orchestration and assist probes
- switched Round B sync execution to shared Wizard `/orchestration/dispatch`
- aligned sync execution with the common Wizard dispatch contract
- switched Wizard transport target loading to the packaged orchestration contract artifact
- added a shared sync record profile for canonical contacts, activities, binders/projects, and sync metadata
- added a starter sync-record envelope example and smoke coverage for contract-aligned payloads
- added a queueable sync-package export path for contract-aligned envelope artifacts
- added local and HTTP handoff paths from exported sync packages into the `uHOME-server` ingest route
- added automation-job queue handoff and automation-result cycle probes aligned to the family `v2.0.2` working-system pass
- expanded repo framing from a narrow sync-extension description to an
  operations-container and Make-pathway description
- added top-level docs for overview, Make pathway, containers, contacts and
  audiences, publishing, and roadmap
- aligned README, architecture, boundary, and getting-started docs with the
  recent family runtime and automation advancement

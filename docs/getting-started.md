# uHOME-empire Getting Started

1. Read `docs/overview.md` for repo purpose and family role.
2. Read `docs/quickstart.md` for the shortest `uHOME-server`-hosted starter path.
3. Read `docs/boundary.md` before adding new features or adapters.
4. Read `docs/architecture.md` for the current layer split.
5. Read `docs/make-pathway.md` if the work should be inspectable or remixable.
6. Read `docs/containers.md` before adding a new pack, job, or script chain.
7. Read `docs/contacts-and-audiences.md` before changing contact or audience flow.
8. Read `docs/publishing.md` for channel and approval expectations.
9. Review `docs/activation.md`.
10. Read `docs/contact-and-crm-model.md` before defining sync ownership.
11. Review `docs/webhook-automation-runbook.md` for the webhook and API lane.
12. Review `docs/provider-lane-status.md` before treating a provider as live.
13. Use `docs/provider-template-patterns.md` when adding payload mappings.
14. Read `docs/hubspot-lane-failure-policy.md` before changing HubSpot lane behavior.
15. Inspect `src/webhooks/` for the base webhook and API contract templates.
16. Inspect `src/containers/` for the empire-owned job/container catalog.
17. Start from `src/webhooks/connection-template.json` for new integrations.
18. Put runnable demonstrations in `examples/`.
19. Run `scripts/run-empire-checks.sh`.
20. Add regression tests for any workflow contract.
21. Run `scripts/smoke/hubspot_lane_gate.py --json` when promoting HubSpot lane changes.

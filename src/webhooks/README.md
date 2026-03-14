# Webhooks

`src/webhooks/` is the contract lane for `uHOME-empire` online automation.

This lane covers:

- cron-type scheduled webhook jobs
- inbound webhook receiver contracts
- outbound API call templates
- provider scaffolds for Google, HubSpot, and future services
- mapping templates for normalizing remote payloads into local reviewable records

Boundary rule:

- keep online API and webhook integrations here
- keep Home Assistant, Matter, and local household automation in `uHOME-server`

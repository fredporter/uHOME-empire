# Source

`src/` is the sync and workflow contract lane for `uHOME-empire`.

Current source surfaces include:

- `workflow-pattern.json` as the smallest checked-in workflow contract
- `webhooks/` for configurable webhook and outbound API integration contracts

Boundary rule:

- keep Google, HubSpot, and vault-sync contracts here
- keep Apple-native desktop behavior outside this repo

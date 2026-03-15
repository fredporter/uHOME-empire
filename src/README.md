# Source

`src/` is the sync and workflow contract lane for `uHOME-empire`.

Current source surfaces include:

- `uhome_empire/packs.py` for pack discovery, manifest loading, and dry-run preview rendering
- `uhome_empire/packs.py` also writes pack-catalog and pack-run report artifacts
- `workflow-pattern.json` as the smallest checked-in workflow contract
- `sync-contract.json` as the starter sync-channel contract
- `sync-record-profile.json` as the shared record-shape profile for contacts,
  activities, binders/projects, and sync-state metadata
- `../examples/basic-sync-record-envelope.json` as a starter envelope aligned to
  the shared sync-record contract
- `sync_adapter.py` as the starter transport-target adapter
- `sync_adapter.py` also reports the `uDOS-core` runtime-service contracts the
  sync lane consumes during `v2.0.2`
- `sync-record-profile.json` extends the neutral `uDOS-core` shared sync
  record contract without documenting private desktop implementation details
- product runtime-service metadata is loaded from
  `uDOS-core/contracts/runtime-services.json`
- `sync_adapter.py` now also derives an execution brief from live Wizard
  orchestration and assist probes
- `webhooks/` for configurable webhook and outbound API integration contracts
- `containers/` for zapier-like remote job and container definitions that stay
  owned by `uHOME-empire`

Boundary rule:

- keep Google, HubSpot, and vault-sync contracts here
- keep Apple-native desktop behavior outside this repo

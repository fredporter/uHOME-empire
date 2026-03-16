# Scripts

`scripts/` is the checked-in validation lane for `uHOME-empire`.

Current script surfaces include:

- `run-empire-checks.sh` for repo activation validation
- `smoke/` for runtime-safe smoke and preflight scaffolds
- `smoke/pack_catalog.py` for the starter pack library artifact
- `smoke/pack_preview.py` for inspectable dry-run pack previews
- `smoke/pack_run.py` for starter-pack dispatch into local or HTTP runtime seams
- `smoke/hubspot_lane_gate.py` for HubSpot lane promotion and runtime-gate validation
- `run-empire-wizard-release-gate.sh` for the hardened empire-to-wizard gate

Boundary rule:

- keep lightweight workflow checks here
- keep generic provider transport and base host runtime logic outside this repo

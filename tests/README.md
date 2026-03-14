# Tests

`tests/` is the workflow contract validation lane for `uDOS-empire`.

Current validation contract:

- `scripts/run-empire-checks.sh` verifies required repo surfaces
- checked-in workflow contracts must stay structurally valid
- private local-root references must not leak into tracked public docs

Phase 1 rule:

- keep tests lightweight and public-contract-focused
- keep private app behavior outside this repo

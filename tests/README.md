# Tests

`tests/` is the workflow contract validation lane for `uHOME-empire`.

Current validation contract:

- `scripts/run-empire-checks.sh` verifies required repo surfaces
- checked-in workflow contracts must stay structurally valid
- private local-root references must not leak into tracked public docs
- smoke scaffolds should remain runnable without live provider mutation
- template and mapping contracts should be testable with local-only checks

Phase 1 rule:

- keep tests lightweight and public-contract-focused
- keep private app and Apple-native behavior outside this repo
- prefer contract, scaffold, and smoke-shape tests before provider-runtime tests

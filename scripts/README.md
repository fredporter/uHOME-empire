# Scripts

`scripts/` is the checked-in validation lane for `uHOME-empire`.

Current script surfaces include:

- `run-empire-checks.sh` for repo activation validation
- `smoke/` for future runtime-safe smoke and preflight scaffolds

Boundary rule:

- keep lightweight workflow checks here
- keep generic provider transport and base host runtime logic outside this repo

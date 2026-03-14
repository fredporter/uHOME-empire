# uDOS-empire Activation

## Purpose

This document marks the first active implementation tranche for `uDOS-empire`.

The activation goal is to make public workflow modules teachable, checkable,
and ready for implementation without broadening ownership beyond:

- public business workflow patterns
- CRM and publishing examples
- contributor-facing operational teaching artifacts
- lightweight workflow contract validation for this repo

## Activated Surfaces

- `src/` as the public workflow module lane
- `scripts/run-empire-checks.sh` as the repo validation entrypoint
- `tests/` as the workflow contract validation lane
- `config/` as the checked-in operational config lane
- `examples/basic-empire-flow.json` as the smallest public workflow example

## Current Validation Contract

Run:

```bash
scripts/run-empire-checks.sh
```

This command:

- verifies the required repo entry surfaces exist
- checks that the sample workflow contract is structurally valid
- rejects private local-root path leakage in tracked repo docs and scripts

## Boundaries

This activation does not move ownership into `uDOS-empire` for:

- private OMD product behavior
- canonical runtime semantics
- provider or transport ownership
- shell or server ownership

# uDOS-empire

## Purpose

Optional public business, CRM, and publishing patterns repo for the uDOS family.

## Ownership

- public business workflow patterns
- CRM and publishing examples
- teachable operational modules

## Non-Goals

- private OMD product logic
- core runtime ownership
- provider control-plane ownership

## Spine

- `src/`
- `docs/`
- `tests/`
- `scripts/`
- `config/`
- `examples/`

## Local Development

Keep public patterns modular and reusable without coupling to private apps.

## Family Relation

Empire can reference public contracts but must remain separate from OMD-specific implementation.

## Activation

The v2 repo activation path is documented in `docs/activation.md`.

Run the current repo validation entrypoint with:

```bash
scripts/run-empire-checks.sh
```

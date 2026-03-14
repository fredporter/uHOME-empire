# Smoke

`scripts/smoke/` holds v2-safe smoke and preflight scaffolds for
`uHOME-empire`.

These scripts should prefer:

- contract checks
- config and secret presence checks
- inspectable JSON output
- no live provider mutation by default

They should not assume the old v1 internal Empire module layout.

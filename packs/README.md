# uHOME-empire Packs

`packs/` holds inspectable operational containers for `uHOME-empire`.

Each pack should be small enough to study, safe enough to dry-run first, and
structured enough to be reused or remixed.

Minimum pack contents:

- `pack.json` manifest
- `README.md`

Recommended additions as the pack grows:

- `templates/`
- `sample-data/`
- `docs/`
- `tests/`

Starter packs currently included:

- `campaign-starter/`
- `event-launch/`
- `weekly-bulletin/`
- `contact-import-cleanup/`

Pack manifests should align to `schemas/pack-manifest.schema.json`.

# Reports

`reports/` is the default home for generated `uHOME-empire` artifacts.

Current conventions:

- `reports/pack-catalog/pack-catalog.json`
- `reports/pack-preview/<pack-id>.json`
- `reports/pack-run/<pack-id>.json`

These are generated artifacts, not canonical source.

Use the smoke scripts to emit them:

- `scripts/smoke/pack_catalog.py --write-default-artifact`
- `scripts/smoke/pack_preview.py --pack <pack-id> --write-default-artifact`
- `scripts/smoke/pack_run.py --pack <pack-id> --local-uhome-app --write-default-report`

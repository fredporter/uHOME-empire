# uHOME-server Quickstart

## Purpose

This is the fastest path to understanding how `uHOME-empire` starter packs use
`uHOME-server` as the local runtime host.

## Suggested First Pass

1. inspect the pack library
2. render a preview
3. emit a preview artifact
4. dispatch a pack into the local `uHOME-server` seam
5. inspect the resulting operator report

## Commands

List the current pack library:

```bash
python3 scripts/smoke/pack_catalog.py --json
```

Write the default catalog artifact:

```bash
python3 scripts/smoke/pack_catalog.py --write-default-artifact
```

Preview the `uHOME-server` quickstart pack:

```bash
python3 scripts/smoke/pack_preview.py --json --pack quickstart --execution-brief
python3 scripts/smoke/pack_preview.py --pack quickstart --write-default-artifact
```

Run the quickstart pack through the local `uHOME-server` runtime seam:

```bash
python3 scripts/smoke/pack_run.py --json --pack quickstart --local-uhome-app --write-default-report
```

Run the launcher or installer pack through the local `uHOME-server` automation seam:

```bash
python3 scripts/smoke/pack_run.py --json --pack launcher-installer --local-uhome-app --write-default-report
```

## Default Artifact Locations

- `reports/pack-catalog/pack-catalog.json`
- `reports/pack-preview/quickstart.json`
- `reports/pack-run/quickstart.json`
- `reports/pack-run/launcher-installer.json`

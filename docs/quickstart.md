# uHOME-empire Quickstart

## Purpose

This is the fastest path to validating `uHOME-empire` starter packs and sync
plans against a local `uHOME-server` runtime and the current Wizard bridge.

## Prerequisites

- Python 3.9+
- sibling `uHOME-server` repo for live or in-process runtime checks
- sibling `uDOS-wizard` repo for live or in-process transport checks

## Suggested First Pass

1. validate the repo surfaces
2. inspect the pack library
3. preview the quickstart pack
4. dispatch a pack into a live `uHOME-server` runtime
5. probe the Wizard transport and `uHOME-server` automation bridge

## 1. Validate The Repo

```bash
bash scripts/run-empire-checks.sh
```

## 2. Inspect The Pack Library

```bash
python3 scripts/smoke/pack_catalog.py --json
python3 scripts/smoke/pack_catalog.py --write-default-artifact
```

## 3. Preview The Quickstart Pack

```bash
python3 scripts/smoke/pack_preview.py --json --pack quickstart --execution-brief
python3 scripts/smoke/pack_preview.py --pack quickstart --write-default-artifact
```

## 4. Dispatch Into A Live `uHOME-server`

With `uHOME-server` already running on `127.0.0.1:8000`:

```bash
python3 scripts/smoke/pack_run.py --json --pack quickstart --uhome-url http://127.0.0.1:8000 --write-default-report
python3 scripts/smoke/pack_run.py --json --pack launcher-installer --uhome-url http://127.0.0.1:8000 --write-default-report
```

If you want to probe the sibling repo in-process instead of using live HTTP,
swap `--uhome-url` for `--local-uhome-app`.

## 5. Probe Wizard And Automation Bridge Paths

With live Wizard and `uHOME-server` processes already running:

```bash
python3 scripts/smoke/sync_plan.py --json --wizard-url http://127.0.0.1:8787 --probe --execution-brief
python3 scripts/smoke/sync_plan.py --json --wizard-url http://127.0.0.1:8787 --handoff-url http://127.0.0.1:8000 --queue-automation-url http://127.0.0.1:8000 --process-automation-url http://127.0.0.1:8000 --fetch-automation-results-url http://127.0.0.1:8000
```

If you want the same checks against sibling repos in-process:

```bash
python3 scripts/smoke/sync_plan.py --json --local-app --execution-brief
python3 scripts/smoke/sync_plan.py --json --local-uhome-automation-runtime
```

## Default Artifact Locations

- `reports/pack-catalog/pack-catalog.json`
- `reports/pack-preview/quickstart.json`
- `reports/pack-run/quickstart.json`
- `reports/pack-run/launcher-installer.json`

#!/usr/bin/env python3
"""Render a starter sync plan from empire workflow and sync contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sync_adapter import (
    attach_transport_targets,
    build_sync_plan,
    probe_local_wizard_app,
    probe_transport_targets,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a uHOME-empire starter sync plan")
    parser.add_argument("--channel", help="Optional channel name")
    parser.add_argument("--wizard-url", default="http://127.0.0.1:8787", help="uDOS-wizard base URL")
    parser.add_argument("--probe", action="store_true", help="Probe transport targets")
    parser.add_argument("--local-app", action="store_true", help="Probe an in-process sibling uDOS-wizard app")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    plan = build_sync_plan(REPO_ROOT, channel_name=args.channel)
    plan = attach_transport_targets(plan, wizard_url=args.wizard_url)
    if args.probe:
        plan = probe_transport_targets(plan)
    if args.local_app:
        plan = probe_local_wizard_app(plan, workspace_root=REPO_ROOT.parent)

    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(f"pattern={plan['pattern']}")
        print(f"mode={plan['mode']}")
        print(f"source_of_truth={plan['source_of_truth']}")
        print(f"channels={','.join(channel['channel'] for channel in plan['channels'])}")
        print(f"capabilities={','.join(plan['capability_union'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

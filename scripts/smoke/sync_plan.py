#!/usr/bin/env python3
"""Render a starter sync plan from empire workflow and sync contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_sync_plan(repo_root: Path, channel_name: str | None = None) -> dict:
    workflow = load_json(repo_root / "src" / "workflow-pattern.json")
    sync_contract = load_json(repo_root / "src" / "sync-contract.json")

    channels = sync_contract["channels"]
    if channel_name is None:
        selected = channels
    else:
        selected = [channel for channel in channels if channel["channel"] == channel_name]

    return {
        "version": sync_contract["version"],
        "pattern": workflow["pattern"],
        "mode": workflow["mode"],
        "source_of_truth": sync_contract["source_of_truth"],
        "channels": selected,
        "capability_union": sorted(
            {capability for channel in selected for capability in channel["capabilities"]}
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a uHOME-empire starter sync plan")
    parser.add_argument("--channel", help="Optional channel name")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    plan = build_sync_plan(repo_root, channel_name=args.channel)

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

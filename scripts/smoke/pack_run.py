#!/usr/bin/env python3
"""Dispatch a starter Empire pack into the existing local or HTTP runtime seams."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from uhome_empire.packs import default_artifact_path, dispatch_pack, probe_local_pack_dispatch, write_pack_run_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch a uHOME-empire starter pack")
    parser.add_argument("--pack", default="campaign-starter", help="Pack id to dispatch")
    parser.add_argument("--uhome-url", help="Optional uHOME-server base URL")
    parser.add_argument("--local-uhome-app", action="store_true", help="Use in-process sibling uHOME-server app")
    parser.add_argument("--process-automation", action="store_true", help="Process queued automation jobs after HTTP dispatch")
    parser.add_argument("--write-report", help="Optional path to write a normalized pack-run report JSON file")
    parser.add_argument("--write-default-report", action="store_true", help="Write the run report into reports/pack-run/")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    if bool(args.uhome_url) == bool(args.local_uhome_app):
        raise SystemExit("choose exactly one of --uhome-url or --local-uhome-app")

    if args.local_uhome_app:
        payload = probe_local_pack_dispatch(REPO_ROOT, args.pack, workspace_root=REPO_ROOT.parent)
    else:
        payload = dispatch_pack(REPO_ROOT, args.pack, args.uhome_url, process_automation=args.process_automation)

    report_path: Path | None = None
    if args.write_report:
        report_path = Path(args.write_report)
    elif args.write_default_report:
        report_path = default_artifact_path(REPO_ROOT, "pack-run", args.pack)
    if report_path:
        payload["report_output"] = str(report_path)
        write_pack_run_report(REPO_ROOT, args.pack, payload, report_path)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"pack_id={payload['pack_id']}")
        print(f"dispatch_mode={payload['dispatch_mode']}")
        print(f"handoff_kind={payload['handoff_kind']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

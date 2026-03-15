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
    build_automation_jobs,
    build_automation_runtime_summary,
    build_automation_results,
    build_sync_execution_brief,
    build_sync_plan,
    fetch_automation_results,
    dispatch_automation_jobs,
    dispatch_automation_results,
    dispatch_sync_package,
    process_automation_jobs,
    build_sync_record_brief,
    probe_local_wizard_app,
    probe_local_uhome_automation_app,
    probe_local_uhome_automation_cycle,
    probe_local_uhome_automation_runtime,
    probe_local_uhome_app,
    probe_transport_targets,
    write_sync_package,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a uHOME-empire starter sync plan")
    parser.add_argument("--channel", help="Optional channel name")
    parser.add_argument("--wizard-url", default="http://127.0.0.1:8787", help="uDOS-wizard base URL")
    parser.add_argument("--probe", action="store_true", help="Probe transport targets")
    parser.add_argument("--local-app", action="store_true", help="Probe an in-process sibling uDOS-wizard app")
    parser.add_argument("--handoff-url", help="Optional uHOME-server base URL for sync envelope ingest")
    parser.add_argument("--local-uhome-app", action="store_true", help="Probe an in-process sibling uHOME-server app")
    parser.add_argument("--queue-automation-url", help="Optional uHOME-server base URL for automation job queueing")
    parser.add_argument("--local-uhome-automation-app", action="store_true", help="Probe automation job queueing against an in-process sibling uHOME-server app")
    parser.add_argument("--process-automation-url", help="Optional uHOME-server base URL for processing queued automation jobs")
    parser.add_argument("--record-automation-results-url", help="Optional uHOME-server base URL for automation result recording")
    parser.add_argument("--fetch-automation-results-url", help="Optional uHOME-server base URL for reading automation results")
    parser.add_argument("--local-uhome-automation-cycle", action="store_true", help="Probe queue and result recording against an in-process sibling uHOME-server app")
    parser.add_argument("--local-uhome-automation-runtime", action="store_true", help="Probe queue, process-next, and result fetch against an in-process sibling uHOME-server app")
    parser.add_argument("--execution-brief", action="store_true", help="Build a sync execution brief from probe output")
    parser.add_argument("--write-package", help="Optional path to write a queueable sync package JSON artifact")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    plan = build_sync_plan(REPO_ROOT, channel_name=args.channel)
    plan = build_sync_record_brief(
        {
            "channels": plan["channels"],
            "sync_record_example": json.loads(Path(plan["sync_record_example_source"]).read_text(encoding="utf-8")),
        }
    ) | plan
    plan = attach_transport_targets(plan, wizard_url=args.wizard_url)
    if args.probe:
        plan = probe_transport_targets(plan)
    if args.local_app:
        plan = probe_local_wizard_app(plan, workspace_root=REPO_ROOT.parent)
    if args.execution_brief:
        probe_key = "local_transport_probe" if args.local_app else "transport_probe"
        plan = build_sync_execution_brief(plan, probe_key=probe_key)
    if args.write_package:
        plan = write_sync_package(plan, Path(args.write_package))
    if args.handoff_url:
        plan = dispatch_sync_package(plan, args.handoff_url)
    if args.local_uhome_app:
        plan = probe_local_uhome_app(plan, workspace_root=REPO_ROOT.parent)
    if (
        args.queue_automation_url
        or args.process_automation_url
        or args.fetch_automation_results_url
        or args.local_uhome_automation_app
        or args.local_uhome_automation_runtime
    ):
        plan = build_automation_jobs(plan)
    if args.queue_automation_url:
        plan = dispatch_automation_jobs(plan, args.queue_automation_url)
    if args.local_uhome_automation_app:
        plan = probe_local_uhome_automation_app(plan, workspace_root=REPO_ROOT.parent)
    if args.process_automation_url:
        plan = process_automation_jobs(plan, args.process_automation_url)
    if args.fetch_automation_results_url:
        plan = build_automation_runtime_summary(fetch_automation_results(plan, args.fetch_automation_results_url))
    if args.record_automation_results_url or args.local_uhome_automation_cycle:
        plan = build_automation_results(build_automation_jobs(plan))
    if args.record_automation_results_url:
        plan = dispatch_automation_results(plan, args.record_automation_results_url)
    if args.local_uhome_automation_cycle:
        plan = probe_local_uhome_automation_cycle(plan, workspace_root=REPO_ROOT.parent)
    if args.local_uhome_automation_runtime:
        plan = probe_local_uhome_automation_runtime(plan, workspace_root=REPO_ROOT.parent)

    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(f"pattern={plan['pattern']}")
        print(f"mode={plan['mode']}")
        print(f"source_of_truth={plan['source_of_truth']}")
        print(f"channels={','.join(channel['channel'] for channel in plan['channels'])}")
        print(f"capabilities={','.join(plan['capability_union'])}")
        if "sync_execution_brief" in plan:
            actions = ",".join(item["recommended_action"] for item in plan["sync_execution_brief"])
            print(f"recommended_actions={actions}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

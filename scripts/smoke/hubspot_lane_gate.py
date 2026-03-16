#!/usr/bin/env python3
"""Run and validate the HubSpot lane as an active Empire provider gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sync_adapter import (  # noqa: E402
    attach_transport_targets,
    build_automation_jobs,
    build_sync_execution_brief,
    build_sync_package,
    build_sync_plan,
    probe_local_uhome_automation_runtime,
    probe_local_wizard_app,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HubSpot lane promotion readiness")
    parser.add_argument("--json", action="store_true", help="Print machine-readable PASS payload")
    args = parser.parse_args()

    plan = build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")
    plan = attach_transport_targets(plan, wizard_url="http://127.0.0.1:8787")
    plan = probe_local_wizard_app(plan, workspace_root=REPO_ROOT.parent)
    plan = build_sync_execution_brief(plan, probe_key="local_transport_probe")
    plan = build_automation_jobs(build_sync_package(plan))
    plan = probe_local_uhome_automation_runtime(plan, workspace_root=REPO_ROOT.parent)

    _assert(len(plan["channels"]) == 1, "hubspot lane should scope to exactly one channel")
    channel = plan["channels"][0]
    _assert(channel["channel"] == "hubspot-sync", "hubspot lane channel mismatch")
    _assert(channel["transport"] == "wizard-provider", "hubspot lane transport must stay wizard-provider")

    package = plan["sync_package"]
    _assert(package["channels"] == ["hubspot-sync"], "hubspot lane package channels mismatch")
    _assert(package["target_systems"] == ["hubspot"], "hubspot lane target_systems mismatch")
    _assert(
        package["projection_targets"] == ["hubspot-activity"],
        "hubspot lane projection_targets mismatch",
    )

    brief = plan["sync_execution_brief"]
    _assert(len(brief) == 1, "hubspot lane execution brief should have one channel row")
    _assert(brief[0]["recommended_action"] == "queue_sync_assist", "hubspot lane recommended action drifted")

    runtime = plan["local_automation_runtime"]
    _assert(runtime["job_status_codes"] == [200], "hubspot lane job queue status mismatch")
    _assert(runtime["process_status_codes"] == [200], "hubspot lane process-next status mismatch")
    _assert(runtime["results_status_code"] == 200, "hubspot lane results status mismatch")

    summary = plan["automation_runtime_summary"]
    _assert(summary["counts_by_channel"].get("hubspot-sync", 0) >= 1, "hubspot lane channel summary missing")
    _assert(summary["counts_by_status"].get("completed", 0) >= 1, "hubspot lane completed status missing")

    payload = {
        "status": "PASS",
        "lane": "hubspot-sync",
        "transport": channel["transport"],
        "target_systems": package["target_systems"],
        "projection_targets": package["projection_targets"],
        "recommended_action": brief[0]["recommended_action"],
        "automation_runtime_summary": summary,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("HubSpot lane gate passed")
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

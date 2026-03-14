#!/usr/bin/env python3
"""Run and validate the empire-to-wizard live smoke as a release-style gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


EXPECTED_KEYS = {
    "orchestration_status": {"mcp_bridge", "providers", "services", "version", "runtime_services"},
    "orchestration_dispatch": {"executor", "mode", "provider", "status", "surface", "task", "transport"},
    "orchestration_workflow_plan": {"mode", "objective", "owner", "plan_version", "step_count", "steps"},
    "contract_only": {"local-contract"},
}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    smoke_script = repo_root / "scripts" / "smoke" / "live_wizard_smoke.py"

    proc = subprocess.run(
        [sys.executable, str(smoke_script)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "live wizard smoke failed")

    payload = json.loads(proc.stdout)
    probes = payload.get("transport_probe", [])
    if not probes:
        raise RuntimeError("expected non-empty transport_probe")

    seen = set()
    for probe in probes:
        name = probe["name"]
        seen.add(name)
        expected = EXPECTED_KEYS.get(name)
        if expected is None:
            raise RuntimeError(f"unexpected transport probe {name}")
        actual = set(probe["keys"])
        missing = sorted(expected - actual)
        if missing:
            raise RuntimeError(f"{name} missing keys: {missing}")

    if seen != set(EXPECTED_KEYS):
        raise RuntimeError(f"probe coverage mismatch: expected {sorted(EXPECTED_KEYS)}, got {sorted(seen)}")

    brief = payload.get("sync_execution_brief", [])
    if not brief:
        raise RuntimeError("expected non-empty sync_execution_brief")
    actions = {item.get("recommended_action") for item in brief}
    if "queue_sync_assist" not in actions:
        raise RuntimeError("sync_execution_brief missing queue_sync_assist")

    print(json.dumps({"status": "PASS", "checked": sorted(seen)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

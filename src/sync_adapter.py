from __future__ import annotations

import json
from pathlib import Path
from typing import Callable
from urllib.parse import quote
from urllib.request import urlopen
import sys


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_runtime_services(repo_root: Path) -> tuple[dict, list[dict]]:
    manifest_path = repo_root.parent / "uDOS-core" / "contracts" / "runtime-services.json"
    manifest = load_json(manifest_path)
    services = [
        {
            "key": service["key"],
            "owner": service["owner"],
            "route": service["route"],
            "stability": service["stability"],
            "consumer": "uHOME-empire",
            "usage": _usage_for_service(service["key"]),
        }
        for service in manifest["services"]
        if "uHOME-empire" in service.get("consumers", [])
    ]
    return manifest, services


def load_wizard_contract(repo_root: Path) -> dict:
    contract_path = repo_root.parent / "uDOS-wizard" / "contracts" / "orchestration-contract.json"
    return load_json(contract_path)


def _wizard_contract_source_from_plan(plan: dict) -> Path:
    runtime_source = Path(plan["runtime_service_source"]).resolve()
    workspace_root = runtime_source.parents[2]
    return workspace_root / "uDOS-wizard" / "contracts" / "orchestration-contract.json"


def _usage_for_service(key: str) -> str:
    if key == "runtime.capability-registry":
        return "align sync-channel capabilities with shared platform ownership"
    if key == "runtime.release-lanes":
        return "track promotion-aware sync and orchestration routing"
    return "shared platform contract consumption"


def build_sync_plan(repo_root: Path, channel_name: str | None = None) -> dict:
    workflow = load_json(repo_root / "src" / "workflow-pattern.json")
    sync_contract = load_json(repo_root / "src" / "sync-contract.json")
    runtime_manifest, runtime_services = load_runtime_services(repo_root)

    channels = sync_contract["channels"]
    if channel_name is None:
        selected = channels
    else:
        selected = [channel for channel in channels if channel["channel"] == channel_name]

    return {
        "version": runtime_manifest["version"],
        "foundation_version": sync_contract["version"],
        "runtime_service_source": str(repo_root.parent / "uDOS-core" / "contracts" / "runtime-services.json"),
        "pattern": workflow["pattern"],
        "mode": workflow["mode"],
        "source_of_truth": sync_contract["source_of_truth"],
        "channels": selected,
        "capability_union": sorted(
            {capability for channel in selected for capability in channel["capabilities"]}
        ),
        "runtime_services": runtime_services,
    }


def attach_transport_targets(plan: dict, wizard_url: str) -> dict:
    contract_source = _wizard_contract_source_from_plan(plan)
    contract = load_json(contract_source)
    routes = contract["routes"]
    channels = []
    for channel in plan["channels"]:
        targets = []
        if channel["transport"] == "wizard-provider":
            task = quote(channel["channel"])
            targets.append({"name": "orchestration_status", "url": f"{wizard_url}{routes['status']['path']}"})
            targets.append(
                {
                    "name": "orchestration_dispatch",
                    "url": f"{wizard_url}{routes['dispatch']['path']}?task={task}&mode=auto&surface=sync",
                }
            )
            targets.append(
                {
                    "name": "orchestration_workflow_plan",
                    "url": f"{wizard_url}{routes['workflow_plan']['path']}?objective=shared-remote-flow&mode=auto",
                }
            )
        elif channel["transport"] == "webhook":
            targets.append({"name": "contract_only", "url": "local-contract:webhook"})

        enriched_channel = dict(channel)
        enriched_channel["transport_targets"] = targets
        channels.append(enriched_channel)

    enriched = dict(plan)
    enriched["wizard_contract_source"] = str(contract_source)
    enriched["channels"] = channels
    return enriched


def probe_transport_targets(
    plan: dict,
    fetcher: Callable[[str], dict] | None = None,
) -> dict:
    fetch = fetcher or _default_fetcher
    results = []
    for channel in plan["channels"]:
        for target in channel.get("transport_targets", []):
            if target["url"].startswith("local-contract:"):
                results.append(
                    {
                        "channel": channel["channel"],
                        "name": target["name"],
                        "url": target["url"],
                        "ok": True,
                        "keys": ["local-contract"],
                    }
                )
                continue
            payload = fetch(target["url"])
            results.append(
                {
                    "channel": channel["channel"],
                    "name": target["name"],
                    "url": target["url"],
                    "ok": True,
                    "keys": sorted(payload.keys()),
                    "payload": payload,
                }
            )

    probed = dict(plan)
    probed["transport_probe"] = results
    return probed


def _default_fetcher(url: str) -> dict:
    with urlopen(url, timeout=2) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def probe_local_wizard_app(plan: dict, workspace_root: Path) -> dict:
    from fastapi.testclient import TestClient

    wizard_repo = workspace_root / "uDOS-wizard"
    sys.path.insert(0, str(wizard_repo))
    from wizard.main import app  # type: ignore

    client = TestClient(app)
    results = []
    for channel in plan["channels"]:
        for target in channel.get("transport_targets", []):
            if target["url"].startswith("local-contract:"):
                results.append(
                    {
                        "channel": channel["channel"],
                        "name": target["name"],
                        "path": target["url"],
                        "status_code": 200,
                        "keys": ["local-contract"],
                    }
                )
                continue
            path = target["url"].replace("http://127.0.0.1:8787", "")
            response = client.get(path)
            payload = response.json()
            results.append(
                {
                    "channel": channel["channel"],
                    "name": target["name"],
                    "path": path,
                    "status_code": response.status_code,
                    "keys": sorted(payload.keys()),
                    "payload": payload,
                }
            )

    probed = dict(plan)
    probed["local_transport_probe"] = results
    return probed


def build_sync_execution_brief(plan: dict, probe_key: str = "transport_probe") -> dict:
    probe_rows = plan.get(probe_key, [])
    probe_map: dict[str, dict[str, dict]] = {}
    for row in probe_rows:
        probe_map.setdefault(row["channel"], {})[row["name"]] = row

    briefs = []
    for channel in plan["channels"]:
        channel_name = channel["channel"]
        channel_probes = probe_map.get(channel_name, {})
        orchestration = channel_probes.get("orchestration_status", {}).get("payload", {})
        dispatch = channel_probes.get("orchestration_dispatch", {}).get("payload", {})
        workflow_plan = channel_probes.get("orchestration_workflow_plan", {}).get("payload", {})
        transport = channel["transport"]

        if transport == "webhook":
            briefs.append(
                {
                    "channel": channel_name,
                    "transport": transport,
                    "recommended_action": "review_contract_only",
                    "executor": "local-contract",
                    "status": "contract-only",
                }
            )
            continue

        providers = orchestration.get("providers", [])
        runtime_services = {item["key"] for item in orchestration.get("runtime_services", [])}
        recommended_action = "queue_sync_assist"
        if dispatch.get("provider") == "local-fallback":
            recommended_action = "fallback_local_review"

        brief = {
            "channel": channel_name,
            "transport": transport,
            "recommended_action": recommended_action,
            "dispatch_version": dispatch.get("dispatch_version", "unknown"),
            "workflow_plan_version": workflow_plan.get("plan_version", "unknown"),
            "workflow_step_count": workflow_plan.get("step_count", 0),
            "provider": dispatch.get("provider", "unknown"),
            "executor": dispatch.get("executor", "unknown"),
            "status": dispatch.get("status", "unknown"),
            "available_providers": providers,
            "runtime_services": sorted(runtime_services),
            "wizard_contract_source": plan.get("wizard_contract_source"),
        }
        if recommended_action == "queue_sync_assist":
            brief["dispatch_request"] = {
                "target": "orchestration_dispatch",
                "task": dispatch.get("request", {}).get("task", channel_name),
                "mode": dispatch.get("request", {}).get("mode", "auto"),
                "surface": dispatch.get("request", {}).get("surface", "sync"),
            }
            brief["dispatch_id"] = dispatch.get("dispatch_id")
            brief["callback_contract"] = dispatch.get("callback_contract")
        briefs.append(brief)

    enriched = dict(plan)
    enriched["sync_execution_brief"] = briefs
    return enriched

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable
from urllib.parse import quote
from urllib.request import Request, urlopen
import sys


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _channel_projection_targets(channel_name: str) -> list[str]:
    mapping = {
        "google-workspace-mirror": ["google-doc", "google-task", "google-drive-export"],
        "hubspot-sync": ["hubspot-activity"],
        "webhook-automation": ["webhook"],
    }
    return mapping.get(channel_name, [])


def _channel_target_systems(channel_name: str) -> list[str]:
    mapping = {
        "google-workspace-mirror": ["google"],
        "hubspot-sync": ["hubspot"],
        "webhook-automation": ["webhook"],
    }
    return mapping.get(channel_name, [])


def _channel_container_job_id(channel_name: str) -> str:
    mapping = {
        "google-workspace-mirror": "google-workspace-sync",
        "hubspot-sync": "hubspot-sync",
        "webhook-automation": "binder-release-webhook",
    }
    return mapping.get(channel_name, "unknown")


def _utc_now_iso_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def load_sync_record_example(repo_root: Path) -> dict:
    return load_json(repo_root / "examples" / "basic-sync-record-envelope.json")


def load_container_job_catalog(repo_root: Path) -> dict:
    return load_json(repo_root / "src" / "containers" / "container-job-catalog.json")


def load_automation_job_contract(repo_root: Path) -> dict:
    return load_json(repo_root.parent / "uDOS-core" / "contracts" / "automation-job-contract.json")


def load_automation_result_contract(repo_root: Path) -> dict:
    return load_json(repo_root.parent / "uDOS-core" / "contracts" / "automation-result-contract.json")


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
    sync_record_profile = load_json(repo_root / "src" / "sync-record-profile.json")
    sync_record_contract_path = repo_root.parent / "uDOS-core" / "contracts" / "sync-record-contract.json"
    sync_record_contract = load_json(sync_record_contract_path)
    automation_job_contract_path = repo_root.parent / "uDOS-core" / "contracts" / "automation-job-contract.json"
    automation_job_contract = load_automation_job_contract(repo_root)
    automation_result_contract_path = repo_root.parent / "uDOS-core" / "contracts" / "automation-result-contract.json"
    automation_result_contract = load_automation_result_contract(repo_root)
    sync_record_example = load_sync_record_example(repo_root)
    container_job_catalog = load_container_job_catalog(repo_root)
    runtime_manifest, runtime_services = load_runtime_services(repo_root)

    channels = sync_contract["channels"]
    if channel_name is None:
        selected = channels
    else:
        selected = [channel for channel in channels if channel["channel"] == channel_name]
        if not selected:
            raise ValueError(f"Unknown sync channel: {channel_name}")

    selected_channel_names = [channel["channel"] for channel in selected]
    scoped_envelope = slice_sync_record_envelope(sync_record_example, selected_channel_names)
    return {
        "version": runtime_manifest["version"],
        "foundation_version": sync_contract["version"],
        "runtime_service_source": str(repo_root.parent / "uDOS-core" / "contracts" / "runtime-services.json"),
        "pattern": workflow["pattern"],
        "mode": workflow["mode"],
        "source_of_truth": sync_contract["source_of_truth"],
        "sync_record_contract_source": str(sync_record_contract_path),
        "sync_record_contract_version": sync_record_contract["version"],
        "automation_job_contract_source": str(automation_job_contract_path),
        "automation_job_contract_version": automation_job_contract["version"],
        "automation_result_contract_source": str(automation_result_contract_path),
        "automation_result_contract_version": automation_result_contract["version"],
        "sync_record_profile_source": str(repo_root / "src" / "sync-record-profile.json"),
        "sync_record_profile_version": sync_record_profile["version"],
        "sync_record_types": sync_record_profile["supported_record_types"],
        "sync_record_example_source": str(repo_root / "examples" / "basic-sync-record-envelope.json"),
        "container_job_catalog_source": str(repo_root / "src" / "containers" / "container-job-catalog.json"),
        "container_job_count": len(container_job_catalog.get("jobs", [])),
        "container_jobs": container_job_catalog.get("jobs", []),
        "sync_record_example_summary": build_sync_record_brief(
            {
                "channels": selected,
                "sync_record_example": scoped_envelope,
            }
        )["sync_record_brief"],
        "channels": selected,
        "capability_union": sorted(
            {capability for channel in selected for capability in channel["capabilities"]}
        ),
        "runtime_services": runtime_services,
    }


def slice_sync_record_envelope(envelope: dict, channel_names: list[str]) -> dict:
    selected_projection_targets = sorted(
        {target for channel_name in channel_names for target in _channel_projection_targets(channel_name)}
    )
    selected_target_systems = sorted(
        {target for channel_name in channel_names for target in _channel_target_systems(channel_name)}
    )

    binders = [
        binder
        for binder in envelope.get("binders", [])
        if set(binder.get("routing", {}).get("projection_targets", [])) & set(selected_projection_targets)
    ]
    binder_ids = {binder["object_id"] for binder in binders}

    activities = []
    for activity in envelope.get("activities", []):
        binder_refs = {ref["id"] for ref in activity.get("binder_refs", [])}
        if binder_refs & binder_ids:
            activities.append(activity)
            continue
        sync_state = activity.get("sync", {})
        if sync_state.get("state") and "webhook" in selected_target_systems and activity.get("activity_kind") == "webhook":
            activities.append(activity)

    activity_ids = {activity["activity_id"] for activity in activities}
    contact_ids = {
        ref["id"]
        for record in [*binders, *activities]
        for ref in record.get("contact_refs", [])
        if ref.get("kind") == "contact"
    }

    contacts = [
        contact
        for contact in envelope.get("contacts", [])
        if contact["contact_id"] in contact_ids
        or any(ref.get("system") in selected_target_systems for ref in contact.get("external_refs", []))
    ]

    sync_metadata = [
        item
        for item in envelope.get("sync_metadata", [])
        if item.get("target_system") in selected_target_systems
    ]

    return {
        "contract_version": envelope["contract_version"],
        "contacts": contacts,
        "activities": activities,
        "binders": binders,
        "sync_metadata": sync_metadata,
    }


def build_sync_record_brief(plan: dict) -> dict:
    envelope = plan["sync_record_example"]
    channels = [channel["channel"] for channel in plan["channels"]]
    binder_targets = sorted(
        {
            target
            for binder in envelope.get("binders", [])
            for target in binder.get("routing", {}).get("projection_targets", [])
        }
    )
    channel_bindings = {
        "google-workspace-mirror": [target for target in binder_targets if target.startswith("google-")],
        "hubspot-sync": [target for target in binder_targets if target.startswith("hubspot-")],
        "webhook-automation": [target for target in binder_targets if target == "webhook"],
    }
    brief = {
        "contract_version": envelope["contract_version"],
        "counts": {
            "contacts": len(envelope.get("contacts", [])),
            "activities": len(envelope.get("activities", [])),
            "binders": len(envelope.get("binders", [])),
            "sync_metadata": len(envelope.get("sync_metadata", [])),
        },
        "binder_projection_targets": binder_targets,
        "channel_projection_targets": {
            channel: channel_bindings.get(channel, []) for channel in channels
        },
    }
    enriched = dict(plan)
    enriched["sync_record_brief"] = brief
    return enriched


def build_sync_package(plan: dict) -> dict:
    envelope = load_json(Path(plan["sync_record_example_source"]))
    selected_channels = [channel["channel"] for channel in plan["channels"]]
    scoped_envelope = slice_sync_record_envelope(envelope, selected_channels)
    packaged = dict(plan)
    packaged["sync_package"] = {
        "package_version": plan["sync_record_contract_version"],
        "generated_from": plan["sync_record_example_source"],
        "channels": selected_channels,
        "projection_targets": sorted(
            {target for channel_name in selected_channels for target in _channel_projection_targets(channel_name)}
        ),
        "target_systems": sorted(
            {target for channel_name in selected_channels for target in _channel_target_systems(channel_name)}
        ),
        "record_counts": {
            "contacts": len(scoped_envelope["contacts"]),
            "activities": len(scoped_envelope["activities"]),
            "binders": len(scoped_envelope["binders"]),
            "sync_metadata": len(scoped_envelope["sync_metadata"]),
        },
        "payload": scoped_envelope,
    }
    return packaged


def write_sync_package(plan: dict, output_path: Path) -> dict:
    packaged = build_sync_package(plan)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(packaged["sync_package"], indent=2) + "\n", encoding="utf-8")
    result = dict(packaged)
    result["sync_package_output"] = str(output_path)
    return result


def build_automation_jobs(plan: dict) -> dict:
    package = plan.get("sync_package") or build_sync_package(plan)["sync_package"]
    container_jobs = {item["service"]: item["job_id"] for item in plan.get("container_jobs", [])}
    queued_at = _utc_now_iso_z()
    jobs = []
    for channel_name in package["channels"]:
        jobs.append(
            {
                "contract_version": plan["automation_job_contract_version"],
                "job_id": f"job:empire:{container_jobs.get(channel_name, _channel_container_job_id(channel_name))}:{queued_at.replace(':', '').replace('-', '')}",
                "requested_capability": "container-job.execute",
                "payload_ref": package.get("generated_from"),
                "origin_surface": "uHOME-empire",
                "policy_flags": {
                    "channel": channel_name,
                    "container_job_id": container_jobs.get(channel_name, _channel_container_job_id(channel_name)),
                    "target_systems": _channel_target_systems(channel_name),
                    "projection_targets": _channel_projection_targets(channel_name),
                },
                "queued_at": queued_at,
            }
        )
    enriched = dict(plan)
    enriched["automation_jobs"] = jobs
    enriched["automation_job_summary"] = {
        "count": len(jobs),
        "channels": package["channels"],
        "requested_capability": "container-job.execute",
    }
    return enriched


def build_automation_results(plan: dict) -> dict:
    jobs = plan.get("automation_jobs") or build_automation_jobs(plan)["automation_jobs"]
    package = plan.get("sync_package") or build_sync_package(plan)["sync_package"]
    completed_at = _utc_now_iso_z()
    results = []
    for job in jobs:
        results.append(
            {
                "contract_version": plan["automation_result_contract_version"],
                "job_id": job["job_id"],
                "status": "completed",
                "output_refs": [package.get("generated_from")],
                "event_refs": [f"event://uHOME-empire/automation/{job['job_id']}"],
                "completed_at": completed_at,
                "suggested_workflow_action": "advance",
            }
        )
    enriched = dict(plan)
    enriched["automation_results"] = results
    enriched["automation_result_summary"] = {
        "count": len(results),
        "status_values": sorted({item["status"] for item in results}),
    }
    return enriched


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


def _default_poster(url: str, payload: dict) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=2) as response:  # noqa: S310
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


def dispatch_sync_package(
    plan: dict,
    uhome_url: str,
    poster: Callable[[str, dict], dict] | None = None,
) -> dict:
    post = poster or _default_poster
    package = plan.get("sync_package") or build_sync_package(plan)["sync_package"]
    payload = package["payload"]
    target = f"{uhome_url}/api/runtime/sync-records/ingest"
    response = post(target, payload)
    dispatched = dict(plan)
    dispatched["sync_handoff"] = {
        "target": target,
        "package_version": package["package_version"],
        "record_counts": package["record_counts"],
        "response": response,
    }
    return dispatched


def dispatch_automation_jobs(
    plan: dict,
    uhome_url: str,
    poster: Callable[[str, dict], dict] | None = None,
) -> dict:
    post = poster or _default_poster
    jobs = plan.get("automation_jobs") or build_automation_jobs(plan)["automation_jobs"]
    target = f"{uhome_url}/api/runtime/automation/jobs"
    responses = [post(target, job) for job in jobs]
    dispatched = dict(plan)
    dispatched["automation_job_handoff"] = {
        "target": target,
        "job_count": len(jobs),
        "responses": responses,
    }
    return dispatched


def process_automation_jobs(
    plan: dict,
    uhome_url: str,
    poster: Callable[[str, dict], dict] | None = None,
) -> dict:
    post = poster or _default_poster
    jobs = plan.get("automation_jobs") or build_automation_jobs(plan)["automation_jobs"]
    target = f"{uhome_url}/api/runtime/automation/process-next"
    responses = [post(target, {}) for _ in jobs]
    processed = dict(plan)
    processed["automation_process_handoff"] = {
        "target": target,
        "processed_count": len(responses),
        "responses": responses,
    }
    return processed


def dispatch_automation_results(
    plan: dict,
    uhome_url: str,
    poster: Callable[[str, dict], dict] | None = None,
) -> dict:
    post = poster or _default_poster
    results = plan.get("automation_results") or build_automation_results(plan)["automation_results"]
    target = f"{uhome_url}/api/runtime/automation/results"
    responses = [post(target, result) for result in results]
    dispatched = dict(plan)
    dispatched["automation_result_handoff"] = {
        "target": target,
        "result_count": len(results),
        "responses": responses,
    }
    return dispatched


def fetch_automation_results(
    plan: dict,
    uhome_url: str,
    fetcher: Callable[[str], dict] | None = None,
) -> dict:
    fetch = fetcher or _default_fetcher
    target = f"{uhome_url}/api/runtime/automation/results"
    payload = fetch(target)
    fetched = dict(plan)
    fetched["automation_results_state"] = {
        "target": target,
        "payload": payload,
    }
    return fetched


def build_automation_runtime_summary(plan: dict) -> dict:
    job_map = {
        item["job_id"]: item.get("policy_flags", {}).get("channel", "unknown")
        for item in plan.get("automation_jobs", [])
    }
    result_items = plan.get("automation_results_state", {}).get("payload", {}).get("items")
    if not result_items:
        result_items = plan.get("local_automation_runtime", {}).get("results_payload", {}).get("items")
    if not result_items:
        result_items = plan.get("automation_results") or []
    counts_by_status: dict[str, int] = {}
    counts_by_channel: dict[str, int] = {}
    actions: set[str] = set()
    for item in result_items:
        status = item.get("status", "unknown")
        counts_by_status[status] = counts_by_status.get(status, 0) + 1
        channel = job_map.get(item.get("job_id"), "unknown")
        counts_by_channel[channel] = counts_by_channel.get(channel, 0) + 1
        if item.get("suggested_workflow_action"):
            actions.add(item["suggested_workflow_action"])

    enriched = dict(plan)
    enriched["automation_runtime_summary"] = {
        "job_count": len(plan.get("automation_jobs", [])),
        "result_count": len(result_items),
        "counts_by_status": counts_by_status,
        "counts_by_channel": counts_by_channel,
        "suggested_workflow_actions": sorted(actions),
    }
    return enriched


def probe_local_uhome_app(plan: dict, workspace_root: Path) -> dict:
    from fastapi.testclient import TestClient

    server_repo = workspace_root / "uHOME-server"
    sys.path.insert(0, str(server_repo / "src"))
    from uhome_server.app import create_app  # type: ignore
    from uhome_server.routes import runtime as runtime_routes  # type: ignore
    from uhome_server.sync_store import SyncRecordStore  # type: ignore

    with TemporaryDirectory() as tmpdir:
        original = runtime_routes.get_sync_record_store
        runtime_routes.get_sync_record_store = lambda: SyncRecordStore(Path(tmpdir))
        try:
            client = TestClient(create_app())
            package = plan.get("sync_package") or build_sync_package(plan)["sync_package"]
            response = client.post("/api/runtime/sync-records/ingest", json=package["payload"])
            payload = response.json()
        finally:
            runtime_routes.get_sync_record_store = original

    probed = dict(plan)
    probed["local_sync_handoff"] = {
        "status_code": response.status_code,
        "payload": payload,
    }
    return probed


def probe_local_uhome_automation_app(plan: dict, workspace_root: Path) -> dict:
    from fastapi.testclient import TestClient

    server_repo = workspace_root / "uHOME-server"
    sys.path.insert(0, str(server_repo / "src"))
    from uhome_server.app import create_app  # type: ignore
    from uhome_server.routes import runtime as runtime_routes  # type: ignore
    from uhome_server.automation_store import AutomationStore  # type: ignore

    with TemporaryDirectory() as tmpdir:
        original = runtime_routes.get_automation_store
        base_dir = Path(tmpdir)
        runtime_routes.get_automation_store = lambda: AutomationStore(
            jobs_path=base_dir / "automation-jobs.json",
            results_path=base_dir / "automation-results.json",
        )
        try:
            client = TestClient(create_app())
            jobs = plan.get("automation_jobs") or build_automation_jobs(plan)["automation_jobs"]
            responses = [client.post("/api/runtime/automation/jobs", json=job) for job in jobs]
            payloads = [response.json() for response in responses]
        finally:
            runtime_routes.get_automation_store = original

    probed = dict(plan)
    probed["local_automation_job_handoff"] = {
        "status_codes": [response.status_code for response in responses],
        "payloads": payloads,
    }
    return probed


def probe_local_uhome_automation_cycle(plan: dict, workspace_root: Path) -> dict:
    from fastapi.testclient import TestClient

    server_repo = workspace_root / "uHOME-server"
    sys.path.insert(0, str(server_repo / "src"))
    from uhome_server.app import create_app  # type: ignore
    from uhome_server.routes import runtime as runtime_routes  # type: ignore
    from uhome_server.automation_store import AutomationStore  # type: ignore

    with TemporaryDirectory() as tmpdir:
        original = runtime_routes.get_automation_store
        base_dir = Path(tmpdir)
        runtime_routes.get_automation_store = lambda: AutomationStore(
            jobs_path=base_dir / "automation-jobs.json",
            results_path=base_dir / "automation-results.json",
        )
        try:
            client = TestClient(create_app())
            jobs = plan.get("automation_jobs") or build_automation_jobs(plan)["automation_jobs"]
            queued = [client.post("/api/runtime/automation/jobs", json=job) for job in jobs]
            results = plan.get("automation_results") or build_automation_results(plan)["automation_results"]
            recorded = [client.post("/api/runtime/automation/results", json=result) for result in results]
        finally:
            runtime_routes.get_automation_store = original

    probed = dict(plan)
    probed["local_automation_cycle"] = {
        "job_status_codes": [response.status_code for response in queued],
        "result_status_codes": [response.status_code for response in recorded],
        "queued_payloads": [response.json() for response in queued],
        "result_payloads": [response.json() for response in recorded],
    }
    return probed


def probe_local_uhome_automation_runtime(plan: dict, workspace_root: Path) -> dict:
    from fastapi.testclient import TestClient

    server_repo = workspace_root / "uHOME-server"
    sys.path.insert(0, str(server_repo / "src"))
    from uhome_server.app import create_app  # type: ignore
    from uhome_server.routes import runtime as runtime_routes  # type: ignore
    from uhome_server.automation_store import AutomationStore  # type: ignore

    with TemporaryDirectory() as tmpdir:
        original = runtime_routes.get_automation_store
        base_dir = Path(tmpdir)
        runtime_routes.get_automation_store = lambda: AutomationStore(
            jobs_path=base_dir / "automation-jobs.json",
            results_path=base_dir / "automation-results.json",
        )
        try:
            client = TestClient(create_app())
            jobs = plan.get("automation_jobs") or build_automation_jobs(plan)["automation_jobs"]
            queued = [client.post("/api/runtime/automation/jobs", json=job) for job in jobs]
            processed = [client.post("/api/runtime/automation/process-next", json={}) for _ in jobs]
            results_response = client.get("/api/runtime/automation/results")
            status_response = client.get("/api/runtime/automation/status")
        finally:
            runtime_routes.get_automation_store = original

    probed = dict(plan)
    probed["local_automation_runtime"] = {
        "job_status_codes": [response.status_code for response in queued],
        "process_status_codes": [response.status_code for response in processed],
        "queued_payloads": [response.json() for response in queued],
        "processed_payloads": [response.json() for response in processed],
        "results_status_code": results_response.status_code,
        "results_payload": results_response.json(),
        "status_status_code": status_response.status_code,
        "status_payload": status_response.json(),
    }
    return build_automation_runtime_summary(probed)


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

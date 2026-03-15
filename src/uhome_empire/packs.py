from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TEMPLATE_PATTERN = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _packs_root(repo_root: Path) -> Path:
    return repo_root / "packs"


def _reports_root(repo_root: Path) -> Path:
    return repo_root / "reports"


def default_artifact_path(repo_root: Path, artifact_kind: str, pack_id: str | None = None) -> Path:
    safe_kind = artifact_kind.replace("_", "-")
    if artifact_kind == "pack-catalog":
        return _reports_root(repo_root) / "pack-catalog" / "pack-catalog.json"
    if pack_id is None:
        raise ValueError(f"pack_id is required for artifact kind: {artifact_kind}")
    return _reports_root(repo_root) / safe_kind / f"{pack_id}.json"


def list_packs(repo_root: Path) -> list[dict[str, Any]]:
    packs_root = _packs_root(repo_root)
    items: list[dict[str, Any]] = []
    for manifest_path in sorted(packs_root.glob("*/pack.json")):
        manifest = _load_json(manifest_path)
        items.append(
            {
                "pack_id": manifest["pack_id"],
                "label": manifest["label"],
                "category": manifest["category"],
                "manifest_path": str(manifest_path),
                "channels": manifest["channels"],
                "approval_mode": manifest["approval_mode"],
            }
        )
    return items


def build_pack_catalog(repo_root: Path) -> dict[str, Any]:
    items = []
    category_counts: dict[str, int] = {}
    channel_counts: dict[str, int] = {}
    for item in list_packs(repo_root):
        loaded = load_pack(repo_root, item["pack_id"])
        manifest = loaded["manifest"]
        items.append(
            {
                **item,
                "summary": manifest["summary"],
                "dry_run_supported": manifest["dry_run_supported"],
                "provider_adapters": manifest.get("provider_adapters", []),
                "container_jobs": manifest.get("runtime", {}).get("container_jobs", []),
            }
        )
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
        for channel in item["channels"]:
            channel_counts[channel] = channel_counts.get(channel, 0) + 1

    return {
        "catalog_version": "v2.0.4",
        "pack_count": len(items),
        "category_counts": category_counts,
        "channel_counts": channel_counts,
        "items": items,
    }


def write_pack_catalog_artifact(repo_root: Path, output_path: Path) -> dict[str, Any]:
    catalog = build_pack_catalog(repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return catalog


def load_pack(repo_root: Path, pack_id: str) -> dict[str, Any]:
    manifest_path = _packs_root(repo_root) / pack_id / "pack.json"
    if not manifest_path.is_file():
        raise ValueError(f"Unknown pack: {pack_id}")
    manifest = _load_json(manifest_path)
    return {
        "pack_id": pack_id,
        "pack_root": manifest_path.parent,
        "manifest_path": manifest_path,
        "manifest": manifest,
    }


def _load_sample_data(pack_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for rel_path in manifest.get("assets", {}).get("sample_data", []):
        path = pack_root / rel_path
        if path.suffix == ".json" and path.is_file():
            payload = _load_json(path)
            if isinstance(payload, dict):
                merged.update(payload)
    return merged


def _render_template(template_text: str, context: dict[str, Any]) -> tuple[str, list[str]]:
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in context:
            return str(context[key])
        missing.append(key)
        return f"{{{{missing:{key}}}}}"

    rendered = TEMPLATE_PATTERN.sub(replace, template_text)
    return rendered, sorted(set(missing))


def render_pack_preview(repo_root: Path, pack_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    loaded = load_pack(repo_root, pack_id)
    manifest = loaded["manifest"]
    pack_root = loaded["pack_root"]
    merged_context = _load_sample_data(pack_root, manifest)
    if context:
        merged_context.update(context)

    rendered_outputs = []
    all_missing: set[str] = set()
    for rel_path in manifest.get("assets", {}).get("templates", []):
        path = pack_root / rel_path
        template_text = path.read_text(encoding="utf-8")
        rendered, missing = _render_template(template_text, merged_context)
        rendered_outputs.append(
            {
                "template": rel_path,
                "rendered": rendered,
                "missing_variables": missing,
            }
        )
        all_missing.update(missing)

    touched_systems = sorted(
        set(manifest.get("channels", []))
        | set(manifest.get("provider_adapters", []))
        | set(manifest.get("runtime", {}).get("container_jobs", []))
    )

    return {
        "pack_id": manifest["pack_id"],
        "label": manifest["label"],
        "category": manifest["category"],
        "summary": manifest["summary"],
        "dry_run_supported": manifest["dry_run_supported"],
        "approval_mode": manifest["approval_mode"],
        "channels": manifest["channels"],
        "touched_systems": touched_systems,
        "input_names": [item["name"] for item in manifest.get("inputs", [])],
        "output_names": [item["name"] for item in manifest.get("outputs", [])],
        "render_context_keys": sorted(merged_context.keys()),
        "missing_variables": sorted(all_missing),
        "rendered_outputs": rendered_outputs,
        "preview_status": "ready" if not all_missing else "incomplete",
    }


def build_pack_handoff_summary(repo_root: Path, pack_id: str) -> dict[str, Any]:
    loaded = load_pack(repo_root, pack_id)
    manifest = loaded["manifest"]
    container_jobs = manifest.get("runtime", {}).get("container_jobs", [])

    if "hubspot-sync" in container_jobs:
        from sync_adapter import build_sync_package, build_sync_plan

        packaged = build_sync_package(build_sync_plan(repo_root, channel_name="hubspot-sync"))["sync_package"]
        return {
            "handoff_kind": "sync-package",
            "channel": "hubspot-sync",
            "target_systems": packaged["target_systems"],
            "projection_targets": packaged["projection_targets"],
            "record_counts": packaged["record_counts"],
        }

    if "binder-release-webhook" in container_jobs:
        from sync_adapter import build_automation_jobs, build_sync_package, build_sync_plan

        plan = build_automation_jobs(build_sync_package(build_sync_plan(repo_root, channel_name="webhook-automation")))
        return {
            "handoff_kind": "automation-job",
            "channel": "webhook-automation",
            "job_count": plan["automation_job_summary"]["count"],
            "requested_capability": plan["automation_job_summary"]["requested_capability"],
            "container_jobs": container_jobs,
        }

    return {
        "handoff_kind": "none",
        "channel": None,
        "container_jobs": container_jobs,
    }


def build_pack_execution_brief(repo_root: Path, pack_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    preview = render_pack_preview(repo_root, pack_id, context=context)
    handoff = build_pack_handoff_summary(repo_root, pack_id)
    return {
        "pack_id": preview["pack_id"],
        "label": preview["label"],
        "preview_status": preview["preview_status"],
        "approval_mode": preview["approval_mode"],
        "dry_run_supported": preview["dry_run_supported"],
        "channels": preview["channels"],
        "touched_systems": preview["touched_systems"],
        "missing_variables": preview["missing_variables"],
        "handoff": handoff,
        "recommended_next_step": "approve_and_dispatch" if preview["preview_status"] == "ready" else "fill_missing_inputs",
    }


def write_pack_preview_artifact(
    repo_root: Path,
    pack_id: str,
    output_path: Path,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preview = render_pack_preview(repo_root, pack_id, context=context)
    execution_brief = build_pack_execution_brief(repo_root, pack_id, context=context)
    artifact = {
        "artifact_version": "v2.0.4",
        "artifact_kind": "pack-dry-run-preview",
        "pack_id": pack_id,
        "preview": preview,
        "execution_brief": execution_brief,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return artifact


def dispatch_pack(
    repo_root: Path,
    pack_id: str,
    uhome_url: str,
    process_automation: bool = False,
    context: dict[str, Any] | None = None,
    poster: Any | None = None,
    fetcher: Any | None = None,
) -> dict[str, Any]:
    _ = context
    handoff = build_pack_handoff_summary(repo_root, pack_id)

    if handoff["handoff_kind"] == "sync-package":
        from sync_adapter import build_sync_package, build_sync_plan, dispatch_sync_package

        plan = build_sync_package(build_sync_plan(repo_root, channel_name=handoff["channel"]))
        dispatched = dispatch_sync_package(plan, uhome_url, poster=poster)
        return {
            "pack_id": pack_id,
            "dispatch_mode": "http",
            "handoff_kind": "sync-package",
            "sync_handoff": dispatched["sync_handoff"],
        }

    if handoff["handoff_kind"] == "automation-job":
        from sync_adapter import (
            build_automation_jobs,
            build_automation_runtime_summary,
            build_sync_package,
            build_sync_plan,
            dispatch_automation_jobs,
            fetch_automation_results,
            process_automation_jobs,
        )

        plan = build_automation_jobs(build_sync_package(build_sync_plan(repo_root, channel_name=handoff["channel"])))
        dispatched = dispatch_automation_jobs(plan, uhome_url, poster=poster)
        result: dict[str, Any] = {
            "pack_id": pack_id,
            "dispatch_mode": "http",
            "handoff_kind": "automation-job",
            "automation_job_handoff": dispatched["automation_job_handoff"],
        }
        if process_automation:
            processed = process_automation_jobs(plan, uhome_url, poster=poster)
            fetched = fetch_automation_results(plan, uhome_url, fetcher=fetcher)
            summarized = build_automation_runtime_summary(plan | processed | fetched)
            result["automation_process_handoff"] = processed["automation_process_handoff"]
            result["automation_results_state"] = fetched["automation_results_state"]
            result["automation_runtime_summary"] = summarized["automation_runtime_summary"]
        return result

    raise ValueError(f"Pack {pack_id} does not have a dispatchable handoff")


def probe_local_pack_dispatch(
    repo_root: Path,
    pack_id: str,
    workspace_root: Path,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _ = context
    handoff = build_pack_handoff_summary(repo_root, pack_id)

    if handoff["handoff_kind"] == "sync-package":
        from sync_adapter import build_sync_package, build_sync_plan, probe_local_uhome_app

        plan = build_sync_package(build_sync_plan(repo_root, channel_name=handoff["channel"]))
        probed = probe_local_uhome_app(plan, workspace_root=workspace_root)
        return {
            "pack_id": pack_id,
            "dispatch_mode": "local-app",
            "handoff_kind": "sync-package",
            "local_sync_handoff": probed["local_sync_handoff"],
        }

    if handoff["handoff_kind"] == "automation-job":
        from sync_adapter import build_automation_jobs, build_sync_package, build_sync_plan, probe_local_uhome_automation_runtime

        plan = build_automation_jobs(build_sync_package(build_sync_plan(repo_root, channel_name=handoff["channel"])))
        probed = probe_local_uhome_automation_runtime(plan, workspace_root=workspace_root)
        return {
            "pack_id": pack_id,
            "dispatch_mode": "local-app",
            "handoff_kind": "automation-job",
            "local_automation_runtime": probed["local_automation_runtime"],
            "automation_runtime_summary": probed["automation_runtime_summary"],
        }

    raise ValueError(f"Pack {pack_id} does not have a dispatchable handoff")


def build_pack_run_report(
    repo_root: Path,
    pack_id: str,
    run_payload: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preview = render_pack_preview(repo_root, pack_id, context=context)
    execution_brief = build_pack_execution_brief(repo_root, pack_id, context=context)
    report = {
        "report_version": "v2.0.4",
        "report_kind": "pack-run-report",
        "pack_id": pack_id,
        "label": preview["label"],
        "category": preview["category"],
        "dispatch_mode": run_payload["dispatch_mode"],
        "handoff_kind": run_payload["handoff_kind"],
        "preview_status": preview["preview_status"],
        "recommended_next_step": execution_brief["recommended_next_step"],
    }

    if run_payload["handoff_kind"] == "sync-package":
        sync_handoff = run_payload.get("sync_handoff") or run_payload.get("local_sync_handoff") or {}
        report["operator_summary"] = {
            "lane": "sync-package",
            "status": "ingested" if sync_handoff else "pending",
            "target": sync_handoff.get("target", "local-app"),
            "ok": sync_handoff.get("payload", {}).get("ok", sync_handoff.get("response", {}).get("ok", True)),
        }
    elif run_payload["handoff_kind"] == "automation-job":
        runtime_summary = run_payload.get("automation_runtime_summary", {})
        local_runtime = run_payload.get("local_automation_runtime", {})
        report["operator_summary"] = {
            "lane": "automation-job",
            "status": "processed" if runtime_summary else "queued",
            "job_count": runtime_summary.get("job_count", 0),
            "result_count": runtime_summary.get("result_count", 0),
            "counts_by_status": runtime_summary.get("counts_by_status", {}),
            "results_status_code": local_runtime.get("results_status_code"),
        }
    else:
        report["operator_summary"] = {"lane": "none", "status": "noop"}

    report["raw"] = run_payload
    return report


def write_pack_run_report(
    repo_root: Path,
    pack_id: str,
    run_payload: dict[str, Any],
    output_path: Path,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = build_pack_run_report(repo_root, pack_id, run_payload, context=context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report

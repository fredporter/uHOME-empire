import json
import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sync_adapter import (
    attach_transport_targets,
    build_automation_jobs,
    build_automation_runtime_summary,
    build_automation_results,
    build_sync_execution_brief,
    build_sync_package,
    build_sync_record_brief,
    build_sync_plan,
    fetch_automation_results,
    dispatch_automation_jobs,
    dispatch_automation_results,
    dispatch_sync_package,
    process_automation_jobs,
    probe_local_uhome_automation_app,
    probe_local_uhome_automation_cycle,
    probe_local_uhome_automation_runtime,
    probe_local_uhome_app,
    probe_local_wizard_app,
    probe_transport_targets,
    slice_sync_record_envelope,
    write_sync_package,
)


class ContractAssetTests(unittest.TestCase):
    def test_sync_adapter_attaches_transport_targets(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="google-workspace-mirror")
        self.assertEqual(plan["version"], "v2.0.2")
        self.assertEqual(plan["foundation_version"], "v2.0.1")
        self.assertEqual(plan["sync_record_contract_version"], "v2.0.4")
        self.assertEqual(plan["automation_job_contract_version"], "v2.0.4")
        self.assertEqual(plan["automation_result_contract_version"], "v2.0.4")
        self.assertEqual(plan["sync_record_profile_version"], "v2.0.4")
        self.assertIn("canonical_contact", plan["sync_record_types"])
        self.assertEqual(plan["sync_record_example_summary"]["counts"]["contacts"], 1)
        self.assertIn("hubspot-activity", plan["sync_record_example_summary"]["binder_projection_targets"])
        self.assertTrue(plan["runtime_service_source"].endswith("uDOS-core/contracts/runtime-services.json"))
        self.assertTrue(plan["sync_record_contract_source"].endswith("uDOS-core/contracts/sync-record-contract.json"))
        self.assertTrue(plan["automation_job_contract_source"].endswith("uDOS-core/contracts/automation-job-contract.json"))
        self.assertTrue(plan["automation_result_contract_source"].endswith("uDOS-core/contracts/automation-result-contract.json"))
        self.assertTrue(plan["sync_record_profile_source"].endswith("uHOME-empire/src/sync-record-profile.json"))
        self.assertTrue(plan["sync_record_example_source"].endswith("uHOME-empire/examples/basic-sync-record-envelope.json"))
        self.assertTrue(plan["container_job_catalog_source"].endswith("uHOME-empire/src/containers/container-job-catalog.json"))
        self.assertEqual(plan["container_job_count"], 3)
        runtime_service_keys = {service["key"] for service in plan["runtime_services"]}
        self.assertIn("runtime.capability-registry", runtime_service_keys)
        self.assertIn("runtime.release-lanes", runtime_service_keys)
        enriched = attach_transport_targets(plan, wizard_url="http://wizard.local")
        targets = enriched["channels"][0]["transport_targets"]
        target_names = [target["name"] for target in targets]
        self.assertIn("orchestration_status", target_names)
        self.assertIn("orchestration_dispatch", target_names)
        self.assertIn("orchestration_workflow_plan", target_names)
        self.assertTrue(enriched["wizard_contract_source"].endswith("uDOS-wizard/contracts/orchestration-contract.json"))

    def test_sync_adapter_probes_transport_targets_with_stub_fetcher(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="webhook-automation")
        enriched = attach_transport_targets(plan, wizard_url="http://wizard.local")
        probed = probe_transport_targets(enriched, fetcher=lambda url: {"url": url, "ok": True})
        self.assertEqual(len(probed["transport_probe"]), 1)
        self.assertTrue(probed["transport_probe"][0]["ok"])
        self.assertEqual(probed["transport_probe"][0]["keys"], ["local-contract"])

    def test_sync_adapter_probes_local_wizard_app(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="google-workspace-mirror")
        enriched = attach_transport_targets(plan, wizard_url="http://127.0.0.1:8787")
        probed = probe_local_wizard_app(enriched, workspace_root=REPO_ROOT.parent)
        self.assertTrue(all(item["status_code"] == 200 for item in probed["local_transport_probe"]))
        self.assertTrue(all("payload" in item for item in probed["local_transport_probe"]))

    def test_sync_contract_has_channels(self) -> None:
        path = REPO_ROOT / "src" / "sync-contract.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v2.0.1")
        self.assertEqual(payload["source_of_truth"], "vault")
        self.assertIsInstance(payload["channels"], list)
        self.assertGreater(len(payload["channels"]), 0)

    def test_sync_record_profile_aligns_to_shared_core_contract(self) -> None:
        path = REPO_ROOT / "src" / "sync-record-profile.json"
        payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload["version"], "v2.0.4")
        self.assertEqual(payload["owner"], "uHOME-empire")
        self.assertTrue(payload["extends"].endswith("uDOS-core/contracts/sync-record-contract.json"))
        self.assertEqual(
            set(payload["supported_record_types"]),
            {"canonical_contact", "activity", "binder_project", "sync_metadata"},
        )
        self.assertIn("vault_contacts_db", payload["contacts"]["required_external_systems"])
        self.assertIn("hubspot-activity", payload["binder_projects"]["routing_targets"])
        self.assertIn("synced", payload["sync_metadata"]["states"])

    def test_pack_manifest_schema_has_required_structure(self) -> None:
        path = REPO_ROOT / "schemas" / "pack-manifest.schema.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["type"], "object")
        self.assertIn("manifest_version", payload["required"])
        self.assertIn("runtime", payload["properties"])
        self.assertIn("assets", payload["properties"])

    def test_campaign_starter_pack_manifest_is_valid(self) -> None:
        path = REPO_ROOT / "packs" / "campaign-starter" / "pack.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["manifest_version"], "v2.0.4")
        self.assertEqual(payload["pack_id"], "campaign-starter")
        self.assertEqual(payload["category"], "campaign")
        self.assertTrue(payload["dry_run_supported"])
        self.assertIn("hubspot-sync", payload["runtime"]["container_jobs"])
        self.assertTrue((path.parent / "templates" / "message-template.md").is_file())
        self.assertTrue((path.parent / "sample-data" / "audience-segment.json").is_file())

    def test_event_launch_pack_manifest_is_valid(self) -> None:
        path = REPO_ROOT / "packs" / "event-launch" / "pack.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["manifest_version"], "v2.0.4")
        self.assertEqual(payload["pack_id"], "event-launch")
        self.assertEqual(payload["category"], "publishing")
        self.assertEqual(payload["approval_mode"], "manual-review")
        self.assertIn("binder-release-webhook", payload["runtime"]["container_jobs"])
        self.assertTrue((path.parent / "templates" / "landing-page.md").is_file())
        self.assertTrue((path.parent / "sample-data" / "event-brief.json").is_file())

    def test_sync_record_example_has_required_collections(self) -> None:
        path = REPO_ROOT / "examples" / "basic-sync-record-envelope.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["contract_version"], "v2.0.4")
        self.assertEqual(set(payload.keys()), {"contract_version", "contacts", "activities", "binders", "sync_metadata"})
        self.assertEqual(len(payload["contacts"]), 1)
        self.assertEqual(payload["activities"][0]["entity_type"], "activity")

    def test_slice_sync_record_envelope_scopes_to_google_lane(self) -> None:
        payload = json.loads((REPO_ROOT / "examples" / "basic-sync-record-envelope.json").read_text(encoding="utf-8"))
        scoped = slice_sync_record_envelope(payload, ["google-workspace-mirror"])
        self.assertEqual(len(scoped["binders"]), 1)
        self.assertEqual(len(scoped["activities"]), 1)
        self.assertEqual(len(scoped["contacts"]), 1)
        self.assertEqual(len(scoped["sync_metadata"]), 0)

    def test_slice_sync_record_envelope_scopes_to_hubspot_lane(self) -> None:
        payload = json.loads((REPO_ROOT / "examples" / "basic-sync-record-envelope.json").read_text(encoding="utf-8"))
        scoped = slice_sync_record_envelope(payload, ["hubspot-sync"])
        self.assertEqual(len(scoped["binders"]), 1)
        self.assertEqual(len(scoped["activities"]), 1)
        self.assertEqual(len(scoped["contacts"]), 1)
        self.assertEqual(len(scoped["sync_metadata"]), 1)

    def test_slice_sync_record_envelope_scopes_to_empty_webhook_lane(self) -> None:
        payload = json.loads((REPO_ROOT / "examples" / "basic-sync-record-envelope.json").read_text(encoding="utf-8"))
        scoped = slice_sync_record_envelope(payload, ["webhook-automation"])
        self.assertEqual(scoped["contacts"], [])
        self.assertEqual(scoped["activities"], [])
        self.assertEqual(scoped["binders"], [])
        self.assertEqual(scoped["sync_metadata"], [])

    def test_sync_record_brief_maps_projection_targets_to_channels(self) -> None:
        plan = build_sync_plan(REPO_ROOT)
        briefed = build_sync_record_brief(
            {
                "channels": plan["channels"],
                "sync_record_example": json.loads(
                    (REPO_ROOT / "examples" / "basic-sync-record-envelope.json").read_text(encoding="utf-8")
                ),
            }
        )
        brief = briefed["sync_record_brief"]
        self.assertEqual(brief["counts"]["activities"], 1)
        self.assertIn("google-doc", brief["channel_projection_targets"]["google-workspace-mirror"])
        self.assertIn("hubspot-activity", brief["channel_projection_targets"]["hubspot-sync"])

    def test_sync_package_carries_payload_and_record_counts(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")
        packaged = build_sync_package(plan)
        package = packaged["sync_package"]
        self.assertEqual(package["package_version"], "v2.0.4")
        self.assertEqual(package["record_counts"]["contacts"], 1)
        self.assertEqual(package["record_counts"]["sync_metadata"], 1)
        self.assertEqual(package["channels"], ["hubspot-sync"])
        self.assertEqual(package["target_systems"], ["hubspot"])
        self.assertEqual(package["payload"]["contract_version"], "v2.0.4")

    def test_sync_package_for_webhook_lane_is_empty_but_valid(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="webhook-automation")
        package = build_sync_package(plan)["sync_package"]
        self.assertEqual(package["projection_targets"], ["webhook"])
        self.assertEqual(package["record_counts"]["contacts"], 0)
        self.assertEqual(package["record_counts"]["activities"], 0)
        self.assertEqual(package["record_counts"]["binders"], 0)

    def test_write_sync_package_persists_json_artifact(self) -> None:
        plan = build_sync_plan(REPO_ROOT)
        output_path = REPO_ROOT / "tests" / "_tmp_sync_package.json"
        try:
            written = write_sync_package(plan, output_path)
            self.assertEqual(written["sync_package_output"], str(output_path))
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["package_version"], "v2.0.4")
        finally:
            if output_path.exists():
                output_path.unlink()

    def test_dispatch_sync_package_posts_payload_to_uhome_server(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")
        dispatched = dispatch_sync_package(
            plan,
            uhome_url="http://uhome.local",
            poster=lambda url, payload: {
                "ok": True,
                "target": url,
                "counts": {
                    "contacts": len(payload["contacts"]),
                    "activities": len(payload["activities"]),
                    "binders": len(payload["binders"]),
                    "sync_metadata": len(payload["sync_metadata"]),
                },
            },
        )
        handoff = dispatched["sync_handoff"]
        self.assertEqual(handoff["target"], "http://uhome.local/api/runtime/sync-records/ingest")
        self.assertEqual(handoff["response"]["counts"]["contacts"], 1)
        self.assertEqual(handoff["record_counts"]["sync_metadata"], 1)

    def test_build_automation_jobs_for_channel_specific_package(self) -> None:
        plan = build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync"))
        planned = build_automation_jobs(plan)
        self.assertEqual(planned["automation_job_summary"]["count"], 1)
        job = planned["automation_jobs"][0]
        self.assertEqual(job["contract_version"], "v2.0.4")
        self.assertEqual(job["requested_capability"], "container-job.execute")
        self.assertEqual(job["policy_flags"]["channel"], "hubspot-sync")
        self.assertEqual(job["policy_flags"]["container_job_id"], "hubspot-sync")

    def test_dispatch_automation_jobs_posts_to_uhome_server(self) -> None:
        plan = build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        dispatched = dispatch_automation_jobs(
            plan,
            uhome_url="http://uhome.local",
            poster=lambda url, payload: {
                "ok": True,
                "target": url,
                "job_id": payload["job_id"],
                "requested_capability": payload["requested_capability"],
            },
        )
        handoff = dispatched["automation_job_handoff"]
        self.assertEqual(handoff["target"], "http://uhome.local/api/runtime/automation/jobs")
        self.assertEqual(handoff["job_count"], 1)
        self.assertEqual(handoff["responses"][0]["requested_capability"], "container-job.execute")

    def test_build_automation_results_from_jobs(self) -> None:
        plan = build_automation_results(
            build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        )
        self.assertEqual(plan["automation_result_summary"]["count"], 1)
        result = plan["automation_results"][0]
        self.assertEqual(result["contract_version"], "v2.0.4")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["suggested_workflow_action"], "advance")

    def test_dispatch_automation_results_posts_to_uhome_server(self) -> None:
        plan = build_automation_results(
            build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        )
        dispatched = dispatch_automation_results(
            plan,
            uhome_url="http://uhome.local",
            poster=lambda url, payload: {
                "ok": True,
                "target": url,
                "job_id": payload["job_id"],
                "status": payload["status"],
            },
        )
        handoff = dispatched["automation_result_handoff"]
        self.assertEqual(handoff["target"], "http://uhome.local/api/runtime/automation/results")
        self.assertEqual(handoff["result_count"], 1)
        self.assertEqual(handoff["responses"][0]["status"], "completed")

    def test_process_automation_jobs_posts_to_uhome_server(self) -> None:
        plan = build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        processed = process_automation_jobs(
            plan,
            uhome_url="http://uhome.local",
            poster=lambda url, payload: {
                "ok": True,
                "target": url,
                "status": "processed",
                "job": {"job_id": "job:1"},
                "result": {"status": "completed"},
            },
        )
        handoff = processed["automation_process_handoff"]
        self.assertEqual(handoff["target"], "http://uhome.local/api/runtime/automation/process-next")
        self.assertEqual(handoff["processed_count"], 1)
        self.assertEqual(handoff["responses"][0]["status"], "processed")

    def test_fetch_automation_results_reads_runtime_state(self) -> None:
        plan = build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        fetched = fetch_automation_results(
            plan,
            uhome_url="http://uhome.local",
            fetcher=lambda url: {
                "contract_version": "v2.0.4",
                "items": [
                    {
                        "job_id": plan["automation_jobs"][0]["job_id"],
                        "status": "completed",
                        "suggested_workflow_action": "advance",
                    }
                ],
            },
        )
        state = fetched["automation_results_state"]
        self.assertEqual(state["target"], "http://uhome.local/api/runtime/automation/results")
        self.assertEqual(state["payload"]["items"][0]["status"], "completed")

    def test_build_automation_runtime_summary_maps_status_and_channel(self) -> None:
        plan = build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        plan["automation_results_state"] = {
            "target": "http://uhome.local/api/runtime/automation/results",
            "payload": {
                "contract_version": "v2.0.4",
                "items": [
                    {
                        "job_id": plan["automation_jobs"][0]["job_id"],
                        "status": "completed",
                        "suggested_workflow_action": "advance",
                    }
                ],
            },
        }
        summarized = build_automation_runtime_summary(plan)
        summary = summarized["automation_runtime_summary"]
        self.assertEqual(summary["job_count"], 1)
        self.assertEqual(summary["result_count"], 1)
        self.assertEqual(summary["counts_by_status"]["completed"], 1)
        self.assertEqual(summary["counts_by_channel"]["hubspot-sync"], 1)
        self.assertEqual(summary["suggested_workflow_actions"], ["advance"])

    def test_probe_local_uhome_app_ingests_sync_package(self) -> None:
        plan = build_sync_package(build_sync_plan(REPO_ROOT))
        probed = probe_local_uhome_app(plan, workspace_root=REPO_ROOT.parent)
        self.assertEqual(probed["local_sync_handoff"]["status_code"], 200)
        self.assertTrue(probed["local_sync_handoff"]["payload"]["ok"])

    def test_probe_local_uhome_automation_app_queues_jobs(self) -> None:
        plan = build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        probed = probe_local_uhome_automation_app(plan, workspace_root=REPO_ROOT.parent)
        self.assertEqual(probed["local_automation_job_handoff"]["status_codes"], [200])
        self.assertEqual(
            probed["local_automation_job_handoff"]["payloads"][0]["requested_capability"],
            "container-job.execute",
        )

    def test_probe_local_uhome_automation_cycle_records_results(self) -> None:
        plan = build_automation_results(
            build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        )
        probed = probe_local_uhome_automation_cycle(plan, workspace_root=REPO_ROOT.parent)
        self.assertEqual(probed["local_automation_cycle"]["job_status_codes"], [200])
        self.assertEqual(probed["local_automation_cycle"]["result_status_codes"], [200])
        self.assertEqual(probed["local_automation_cycle"]["result_payloads"][0]["status"], "completed")

    def test_probe_local_uhome_automation_runtime_processes_jobs(self) -> None:
        plan = build_automation_jobs(build_sync_package(build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")))
        probed = probe_local_uhome_automation_runtime(plan, workspace_root=REPO_ROOT.parent)
        self.assertEqual(probed["local_automation_runtime"]["job_status_codes"], [200])
        self.assertEqual(probed["local_automation_runtime"]["process_status_codes"], [200])
        self.assertEqual(probed["local_automation_runtime"]["results_status_code"], 200)
        self.assertEqual(probed["automation_runtime_summary"]["counts_by_status"]["completed"], 1)
        self.assertEqual(probed["automation_runtime_summary"]["counts_by_channel"]["hubspot-sync"], 1)

    def test_webhook_templates_have_expected_keys(self) -> None:
        targets = [
            REPO_ROOT / "src" / "webhooks" / "webhook-server-template.json",
            REPO_ROOT / "src" / "webhooks" / "google-sync-template.json",
            REPO_ROOT / "src" / "webhooks" / "hubspot-sync-template.json",
            REPO_ROOT / "examples" / "configurable-webhook-server.json",
        ]

        for path in targets:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("service", payload)
                self.assertTrue(payload["service"])

    def test_container_job_catalog_is_empire_owned(self) -> None:
        payload = json.loads((REPO_ROOT / "src" / "containers" / "container-job-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["owner"], "uHOME-empire")
        self.assertEqual(payload["runtime_owner"], "uHOME-server")
        self.assertEqual(len(payload["jobs"]), 3)

    def test_mapping_templates_have_required_fields(self) -> None:
        targets = [
            REPO_ROOT / "src" / "webhooks" / "mappings" / "default-contact-master.json",
            REPO_ROOT / "src" / "webhooks" / "mappings" / "google-lead-enrichment.json",
            REPO_ROOT / "src" / "webhooks" / "mappings" / "calendar-followup-task.json",
        ]

        for path in targets:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                for key in (
                    "label",
                    "source_system",
                    "event_type",
                    "target_scope",
                    "target_entity",
                    "template_version",
                    "field_map",
                    "required_fields",
                ):
                    self.assertIn(key, payload)
                self.assertIsInstance(payload["field_map"], dict)
                self.assertGreater(len(payload["field_map"]), 0)
                self.assertIsInstance(payload["required_fields"], list)

    def test_sync_plan_reports_runtime_services(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="hubspot-sync")
        self.assertEqual(plan["version"], "v2.0.2")
        self.assertEqual(plan["foundation_version"], "v2.0.1")
        self.assertTrue(plan["runtime_service_source"].endswith("uDOS-core/contracts/runtime-services.json"))
        self.assertGreaterEqual(len(plan["runtime_services"]), 2)

    def test_sync_plan_rejects_unknown_channel(self) -> None:
        with self.assertRaises(ValueError):
            build_sync_plan(REPO_ROOT, channel_name="hubspot-crm-sync")

    def test_sync_execution_brief_recommends_assist_queue(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="google-workspace-mirror")
        enriched = attach_transport_targets(plan, wizard_url="http://127.0.0.1:8787")
        probed = probe_local_wizard_app(enriched, workspace_root=REPO_ROOT.parent)
        briefed = build_sync_execution_brief(probed, probe_key="local_transport_probe")
        brief = briefed["sync_execution_brief"][0]
        self.assertEqual(brief["channel"], "google-workspace-mirror")
        self.assertEqual(brief["recommended_action"], "queue_sync_assist")
        self.assertEqual(brief["dispatch_version"], "v2.0.2")
        self.assertTrue(str(brief["dispatch_id"]).startswith("dispatch:"))
        self.assertEqual(brief["workflow_plan_version"], "v2.0.2")
        self.assertEqual(brief["workflow_step_count"], 2)
        self.assertEqual(brief["dispatch_request"]["target"], "orchestration_dispatch")
        self.assertEqual(brief["dispatch_request"]["surface"], "sync")
        self.assertEqual(brief["callback_contract"]["route"], "/orchestration/callback")
        self.assertTrue(brief["wizard_contract_source"].endswith("uDOS-wizard/contracts/orchestration-contract.json"))


if __name__ == "__main__":
    unittest.main()

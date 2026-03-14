import json
import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sync_adapter import (
    attach_transport_targets,
    build_sync_execution_brief,
    build_sync_plan,
    probe_local_wizard_app,
    probe_transport_targets,
)


class ContractAssetTests(unittest.TestCase):
    def test_sync_adapter_attaches_transport_targets(self) -> None:
        plan = build_sync_plan(REPO_ROOT, channel_name="google-workspace-mirror")
        self.assertEqual(plan["version"], "v2.0.2")
        self.assertEqual(plan["foundation_version"], "v2.0.1")
        self.assertTrue(plan["runtime_service_source"].endswith("uDOS-core/contracts/runtime-services.json"))
        runtime_service_keys = {service["key"] for service in plan["runtime_services"]}
        self.assertIn("runtime.capability-registry", runtime_service_keys)
        self.assertIn("runtime.release-lanes", runtime_service_keys)
        enriched = attach_transport_targets(plan, wizard_url="http://wizard.local")
        targets = enriched["channels"][0]["transport_targets"]
        target_names = [target["name"] for target in targets]
        self.assertIn("orchestration_status", target_names)
        self.assertIn("orchestration_dispatch", target_names)

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
        plan = build_sync_plan(REPO_ROOT, channel_name="hubspot-crm-sync")
        self.assertEqual(plan["version"], "v2.0.2")
        self.assertEqual(plan["foundation_version"], "v2.0.1")
        self.assertTrue(plan["runtime_service_source"].endswith("uDOS-core/contracts/runtime-services.json"))
        self.assertGreaterEqual(len(plan["runtime_services"]), 2)

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
        self.assertEqual(brief["dispatch_request"]["target"], "orchestration_dispatch")
        self.assertEqual(brief["dispatch_request"]["surface"], "sync")


if __name__ == "__main__":
    unittest.main()

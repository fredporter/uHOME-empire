import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ContractAssetTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

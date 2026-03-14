import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class SmokeScaffoldTests(unittest.TestCase):
    def test_contract_smoke_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "smoke" / "contract_smoke.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Contract smoke passed", proc.stdout)

    def test_integration_preflight_json_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "smoke" / "integration_preflight.py"), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("results", payload)
        self.assertIn("counts", payload)

    def test_sync_plan_json_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["version"], "v2.0.2")
        self.assertEqual(payload["foundation_version"], "v2.0.1")
        self.assertIn("runtime_services", payload)
        self.assertIn("google-workspace-mirror", [channel["channel"] for channel in payload["channels"]])
        self.assertIn("transport_targets", payload["channels"][0])

    def test_sync_plan_local_app_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"), "--json", "--local-app"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("local_transport_probe", payload)


if __name__ == "__main__":
    unittest.main()

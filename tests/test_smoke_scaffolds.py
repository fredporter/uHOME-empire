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
        self.assertEqual(payload["sync_record_contract_version"], "v2.0.4")
        self.assertEqual(payload["sync_record_profile_version"], "v2.0.4")
        self.assertEqual(payload["sync_record_example_summary"]["counts"]["binders"], 1)
        self.assertTrue(payload["runtime_service_source"].endswith("uDOS-core/contracts/runtime-services.json"))
        self.assertTrue(payload["sync_record_example_source"].endswith("uHOME-empire/examples/basic-sync-record-envelope.json"))
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

    def test_sync_plan_execution_brief_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"), "--json", "--local-app", "--execution-brief"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("sync_execution_brief", payload)
        self.assertTrue(payload["sync_execution_brief"])

    def test_sync_plan_can_write_sync_package(self) -> None:
        output_path = REPO_ROOT / "tests" / "_tmp_sync_package.json"
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"),
                    "--json",
                    "--write-package",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["sync_package_output"], str(output_path))
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["package_version"], "v2.0.4")
        finally:
            if output_path.exists():
                output_path.unlink()

    def test_sync_plan_channel_specific_package_scopes_to_hubspot(self) -> None:
        output_path = REPO_ROOT / "tests" / "_tmp_hubspot_sync_package.json"
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"),
                    "--json",
                    "--channel",
                    "hubspot-sync",
                    "--write-package",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["channels"], ["hubspot-sync"])
            self.assertEqual(written["target_systems"], ["hubspot"])
            self.assertEqual(written["record_counts"]["sync_metadata"], 1)
        finally:
            if output_path.exists():
                output_path.unlink()

    def test_sync_plan_local_uhome_app_handoff_runs(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"),
                "--json",
                "--local-uhome-app",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["local_sync_handoff"]["status_code"], 200)
        self.assertTrue(payload["local_sync_handoff"]["payload"]["ok"])

    def test_sync_plan_local_uhome_automation_handoff_runs(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"),
                "--json",
                "--channel",
                "hubspot-sync",
                "--local-uhome-automation-app",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["automation_job_summary"]["count"], 1)
        self.assertEqual(payload["local_automation_job_handoff"]["status_codes"], [200])

    def test_sync_plan_local_uhome_automation_cycle_runs(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"),
                "--json",
                "--channel",
                "hubspot-sync",
                "--local-uhome-automation-cycle",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["automation_result_summary"]["count"], 1)
        self.assertEqual(payload["local_automation_cycle"]["job_status_codes"], [200])
        self.assertEqual(payload["local_automation_cycle"]["result_status_codes"], [200])

    def test_sync_plan_local_uhome_automation_runtime_runs(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "smoke" / "sync_plan.py"),
                "--json",
                "--channel",
                "hubspot-sync",
                "--local-uhome-automation-runtime",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["local_automation_runtime"]["job_status_codes"], [200])
        self.assertEqual(payload["local_automation_runtime"]["process_status_codes"], [200])
        self.assertEqual(payload["local_automation_runtime"]["results_status_code"], 200)
        self.assertEqual(payload["automation_runtime_summary"]["counts_by_status"]["completed"], 1)


if __name__ == "__main__":
    unittest.main()

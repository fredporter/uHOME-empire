import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from uhome_empire.packs import (
    build_pack_catalog,
    build_pack_execution_brief,
    build_pack_handoff_summary,
    build_pack_run_report,
    dispatch_pack,
    list_packs,
    load_pack,
    probe_local_pack_dispatch,
    render_pack_preview,
    write_pack_catalog_artifact,
    write_pack_preview_artifact,
    write_pack_run_report,
)


class PackRuntimeTests(unittest.TestCase):
    def test_list_packs_returns_starter_packs(self) -> None:
        items = list_packs(REPO_ROOT)
        pack_ids = {item["pack_id"] for item in items}
        self.assertIn("campaign-starter", pack_ids)
        self.assertIn("event-launch", pack_ids)
        self.assertIn("weekly-bulletin", pack_ids)
        self.assertIn("contact-import-cleanup", pack_ids)

    def test_build_pack_catalog_reports_counts(self) -> None:
        catalog = build_pack_catalog(REPO_ROOT)
        self.assertGreaterEqual(catalog["pack_count"], 4)
        self.assertIn("campaign", catalog["category_counts"])
        self.assertIn("hubspot-sync", catalog["channel_counts"])

    def test_write_pack_catalog_artifact_persists_catalog(self) -> None:
        output_path = REPO_ROOT / "tests" / "_tmp_pack_catalog.json"
        try:
            catalog = write_pack_catalog_artifact(REPO_ROOT, output_path)
            self.assertGreaterEqual(catalog["pack_count"], 4)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["catalog_version"], "v2.0.4")
        finally:
            if output_path.exists():
                output_path.unlink()

    def test_load_pack_returns_manifest_and_root(self) -> None:
        loaded = load_pack(REPO_ROOT, "campaign-starter")
        self.assertEqual(loaded["manifest"]["pack_id"], "campaign-starter")
        self.assertTrue((loaded["pack_root"] / "templates" / "message-template.md").is_file())

    def test_render_pack_preview_renders_campaign_starter(self) -> None:
        preview = render_pack_preview(REPO_ROOT, "campaign-starter")
        self.assertEqual(preview["pack_id"], "campaign-starter")
        self.assertEqual(preview["preview_status"], "ready")
        self.assertEqual(preview["missing_variables"], [])
        self.assertIn("hubspot-sync", preview["touched_systems"])
        self.assertIn("Open Studio April Campaign", preview["rendered_outputs"][0]["rendered"])

    def test_render_pack_preview_accepts_context_override(self) -> None:
        preview = render_pack_preview(REPO_ROOT, "event-launch", context={"event_name": "Late Night Launch"})
        self.assertEqual(preview["preview_status"], "ready")
        self.assertIn("Late Night Launch", preview["rendered_outputs"][0]["rendered"])

    def test_render_pack_preview_rejects_unknown_pack(self) -> None:
        with self.assertRaises(ValueError):
            render_pack_preview(REPO_ROOT, "missing-pack")

    def test_build_pack_handoff_summary_maps_campaign_pack_to_sync_package(self) -> None:
        handoff = build_pack_handoff_summary(REPO_ROOT, "campaign-starter")
        self.assertEqual(handoff["handoff_kind"], "sync-package")
        self.assertEqual(handoff["channel"], "hubspot-sync")
        self.assertEqual(handoff["target_systems"], ["hubspot"])

    def test_build_pack_handoff_summary_maps_event_pack_to_automation_job(self) -> None:
        handoff = build_pack_handoff_summary(REPO_ROOT, "event-launch")
        self.assertEqual(handoff["handoff_kind"], "automation-job")
        self.assertEqual(handoff["channel"], "webhook-automation")
        self.assertEqual(handoff["job_count"], 1)

    def test_build_pack_execution_brief_reports_next_step(self) -> None:
        brief = build_pack_execution_brief(REPO_ROOT, "campaign-starter")
        self.assertEqual(brief["pack_id"], "campaign-starter")
        self.assertEqual(brief["recommended_next_step"], "approve_and_dispatch")
        self.assertEqual(brief["handoff"]["handoff_kind"], "sync-package")

    def test_write_pack_preview_artifact_persists_execution_brief(self) -> None:
        output_path = REPO_ROOT / "tests" / "_tmp_pack_preview_artifact.json"
        try:
            artifact = write_pack_preview_artifact(REPO_ROOT, "event-launch", output_path)
            self.assertEqual(artifact["artifact_kind"], "pack-dry-run-preview")
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["execution_brief"]["handoff"]["handoff_kind"], "automation-job")
            self.assertEqual(payload["preview"]["preview_status"], "ready")
        finally:
            if output_path.exists():
                output_path.unlink()

    def test_dispatch_pack_posts_sync_package(self) -> None:
        dispatched = dispatch_pack(
            REPO_ROOT,
            "campaign-starter",
            "http://uhome.local",
            poster=lambda url, payload: {"ok": True, "target": url, "counts": {"contacts": len(payload["contacts"])}},
        )
        self.assertEqual(dispatched["handoff_kind"], "sync-package")
        self.assertEqual(
            dispatched["sync_handoff"]["target"],
            "http://uhome.local/api/runtime/sync-records/ingest",
        )

    def test_dispatch_pack_processes_automation_lane(self) -> None:
        dispatched = dispatch_pack(
            REPO_ROOT,
            "event-launch",
            "http://uhome.local",
            process_automation=True,
            poster=lambda url, payload: {
                "ok": True,
                "target": url,
                "status": "processed" if url.endswith("/process-next") else "queued",
                "job": {"job_id": "job:1"},
                "result": {"status": "completed"},
            },
            fetcher=lambda url: {
                "contract_version": "v2.0.4",
                "items": [
                    {
                        "job_id": "job:empire:binder-release-webhook:20260315T000000Z",
                        "status": "completed",
                        "suggested_workflow_action": "advance",
                    }
                ],
            },
        )
        self.assertEqual(dispatched["handoff_kind"], "automation-job")
        self.assertEqual(
            dispatched["automation_job_handoff"]["target"],
            "http://uhome.local/api/runtime/automation/jobs",
        )
        self.assertEqual(
            dispatched["automation_process_handoff"]["target"],
            "http://uhome.local/api/runtime/automation/process-next",
        )
        self.assertIn("automation_runtime_summary", dispatched)

    def test_probe_local_pack_dispatch_ingests_sync_package(self) -> None:
        probed = probe_local_pack_dispatch(REPO_ROOT, "campaign-starter", workspace_root=REPO_ROOT.parent)
        self.assertEqual(probed["handoff_kind"], "sync-package")
        self.assertEqual(probed["local_sync_handoff"]["status_code"], 200)
        self.assertTrue(probed["local_sync_handoff"]["payload"]["ok"])

    def test_probe_local_pack_dispatch_runs_automation_runtime(self) -> None:
        probed = probe_local_pack_dispatch(REPO_ROOT, "event-launch", workspace_root=REPO_ROOT.parent)
        self.assertEqual(probed["handoff_kind"], "automation-job")
        self.assertEqual(probed["local_automation_runtime"]["results_status_code"], 200)
        self.assertEqual(probed["automation_runtime_summary"]["counts_by_status"]["completed"], 1)

    def test_build_pack_run_report_summarizes_sync_lane(self) -> None:
        run_payload = {
            "pack_id": "campaign-starter",
            "dispatch_mode": "local-app",
            "handoff_kind": "sync-package",
            "local_sync_handoff": {"status_code": 200, "payload": {"ok": True}},
        }
        report = build_pack_run_report(REPO_ROOT, "campaign-starter", run_payload)
        self.assertEqual(report["report_kind"], "pack-run-report")
        self.assertEqual(report["operator_summary"]["lane"], "sync-package")
        self.assertEqual(report["operator_summary"]["status"], "ingested")

    def test_write_pack_run_report_persists_operator_summary(self) -> None:
        output_path = REPO_ROOT / "tests" / "_tmp_pack_run_report.json"
        try:
            run_payload = {
                "pack_id": "event-launch",
                "dispatch_mode": "local-app",
                "handoff_kind": "automation-job",
                "local_automation_runtime": {"results_status_code": 200},
                "automation_runtime_summary": {"job_count": 1, "result_count": 1, "counts_by_status": {"completed": 1}},
            }
            report = write_pack_run_report(REPO_ROOT, "event-launch", run_payload, output_path)
            self.assertEqual(report["operator_summary"]["lane"], "automation-job")
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["report_version"], "v2.0.4")
        finally:
            if output_path.exists():
                output_path.unlink()

    def test_pack_preview_smoke_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "smoke" / "pack_preview.py"), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["pack_id"], "campaign-starter")
        self.assertEqual(payload["preview_status"], "ready")

    def test_pack_preview_smoke_can_emit_execution_brief_and_artifact(self) -> None:
        output_path = REPO_ROOT / "tests" / "_tmp_pack_preview_cli_artifact.json"
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "smoke" / "pack_preview.py"),
                    "--json",
                    "--pack",
                    "event-launch",
                    "--execution-brief",
                    "--write-artifact",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["execution_brief"]["handoff"]["handoff_kind"], "automation-job")
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["artifact_kind"], "pack-dry-run-preview")
        finally:
            if output_path.exists():
                output_path.unlink()

    def test_pack_catalog_smoke_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "smoke" / "pack_catalog.py"), "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertGreaterEqual(payload["pack_count"], 4)

    def test_pack_run_smoke_can_dispatch_to_local_uhome_app(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "smoke" / "pack_run.py"),
                "--json",
                "--pack",
                "campaign-starter",
                "--local-uhome-app",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["handoff_kind"], "sync-package")
        self.assertEqual(payload["local_sync_handoff"]["status_code"], 200)

    def test_pack_run_smoke_can_run_local_automation_lane(self) -> None:
        output_path = REPO_ROOT / "tests" / "_tmp_pack_run_cli_report.json"
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "smoke" / "pack_run.py"),
                    "--json",
                    "--pack",
                    "event-launch",
                    "--local-uhome-app",
                    "--write-report",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["handoff_kind"], "automation-job")
            self.assertEqual(payload["local_automation_runtime"]["results_status_code"], 200)
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["report_kind"], "pack-run-report")
        finally:
            if output_path.exists():
                output_path.unlink()


if __name__ == "__main__":
    unittest.main()

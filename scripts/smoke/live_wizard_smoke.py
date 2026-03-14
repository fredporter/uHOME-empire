#!/usr/bin/env python3
"""Run a live-process smoke against a sibling uDOS-wizard instance."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_http(url: str, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=1) as response:  # noqa: S310
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(0.2)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = repo_root.parent
    wizard_repo = workspace_root / "uDOS-wizard"
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    status_url = f"{base_url}/orchestration/status"

    env = dict(os.environ)
    env["PYTHONPATH"] = str(wizard_repo)

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "wizard.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=wizard_repo,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_http(status_url)
        probe = subprocess.run(
            [
                sys.executable,
                str(repo_root / "scripts" / "smoke" / "sync_plan.py"),
                "--json",
                "--probe",
                "--execution-brief",
                "--wizard-url",
                base_url,
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(probe.stdout)
        print(json.dumps(payload, indent=2))
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())

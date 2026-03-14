#!/usr/bin/env python3
"""uHOME-empire contract smoke scaffold for webhook and mapping templates."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    targets = [
        repo_root / "src" / "sync-contract.json",
        repo_root / "src" / "webhooks" / "webhook-server-template.json",
        repo_root / "src" / "webhooks" / "google-sync-template.json",
        repo_root / "src" / "webhooks" / "hubspot-sync-template.json",
        repo_root / "src" / "webhooks" / "mappings" / "default-contact-master.json",
        repo_root / "src" / "webhooks" / "mappings" / "google-lead-enrichment.json",
        repo_root / "src" / "webhooks" / "mappings" / "calendar-followup-task.json",
        repo_root / "examples" / "configurable-webhook-server.json",
    ]

    for path in targets:
        payload = json.loads(path.read_text(encoding="utf-8"))
        print(f"PASS {path.relative_to(repo_root)} :: keys={sorted(payload.keys())}")

    print("Contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

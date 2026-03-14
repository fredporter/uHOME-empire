#!/usr/bin/env python3
"""uHOME-empire integration preflight scaffold (no live API calls)."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List


def _ok(name: str, detail: str) -> Dict[str, str]:
    return {"check": name, "status": "PASS", "detail": detail}


def _warn(name: str, detail: str) -> Dict[str, str]:
    return {"check": name, "status": "WARN", "detail": detail}


def _check_env(name: str) -> Dict[str, str]:
    if os.environ.get(name):
        return _ok(f"env:{name}", "configured")
    return _warn(f"env:{name}", "missing")


def _check_file(path: Path) -> Dict[str, str]:
    if path.exists():
        return _ok(f"file:{path.name}", f"exists at {path}")
    return _warn(f"file:{path.name}", f"missing at {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="uHOME-empire integration preflight scaffold")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    results: List[Dict[str, str]] = []

    results.append(_check_file(repo_root / "src" / "webhooks" / "google-sync-template.json"))
    results.append(_check_file(repo_root / "src" / "webhooks" / "hubspot-sync-template.json"))
    results.append(_check_file(repo_root / "src" / "webhooks" / "mappings" / "default-contact-master.json"))
    results.append(_check_env("UHOME_EMPIRE_WEBHOOK_SECRET"))
    results.append(_check_env("UHOME_EMPIRE_GOOGLE_CREDENTIALS"))
    results.append(_check_env("UHOME_EMPIRE_HUBSPOT_TOKEN"))

    counts = {"PASS": 0, "WARN": 0}
    for item in results:
        counts[item["status"]] += 1

    if args.json:
        print(json.dumps({"results": results, "counts": counts}, indent=2))
    else:
        for item in results:
            print(f"{item['status']} {item['check']} :: {item['detail']}")
        print(f"SUMMARY PASS={counts['PASS']} WARN={counts['WARN']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render the current uHOME-empire pack catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from uhome_empire.packs import build_pack_catalog, default_artifact_path, write_pack_catalog_artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the uHOME-empire pack catalog")
    parser.add_argument("--write-artifact", help="Optional path to write a pack catalog artifact")
    parser.add_argument("--write-default-artifact", action="store_true", help="Write the catalog artifact into reports/pack-catalog/")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    catalog = build_pack_catalog(REPO_ROOT)
    payload: dict[str, object] = dict(catalog)
    artifact_path: Path | None = None
    if args.write_artifact:
        artifact_path = Path(args.write_artifact)
    elif args.write_default_artifact:
        artifact_path = default_artifact_path(REPO_ROOT, "pack-catalog")
    if artifact_path:
        payload["artifact_output"] = str(artifact_path)
        write_pack_catalog_artifact(REPO_ROOT, artifact_path)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"pack_count={catalog['pack_count']}")
        print(f"categories={','.join(sorted(catalog['category_counts'].keys()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

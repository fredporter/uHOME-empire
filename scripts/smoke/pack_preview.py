#!/usr/bin/env python3
"""Render an inspectable dry-run preview for a starter Empire pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from uhome_empire.packs import (
    build_pack_execution_brief,
    default_artifact_path,
    list_packs,
    render_pack_preview,
    write_pack_preview_artifact,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a uHOME-empire pack preview")
    parser.add_argument("--pack", default="campaign-starter", help="Pack id to preview")
    parser.add_argument("--execution-brief", action="store_true", help="Include execution brief output")
    parser.add_argument("--write-artifact", help="Optional path to write a dry-run artifact JSON file")
    parser.add_argument("--write-default-artifact", action="store_true", help="Write the preview artifact into reports/pack-preview/")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    preview = render_pack_preview(REPO_ROOT, args.pack)
    payload: dict[str, object] = dict(preview)
    if args.execution_brief:
        payload["execution_brief"] = build_pack_execution_brief(REPO_ROOT, args.pack)
    artifact_path: Path | None = None
    if args.write_artifact:
        artifact_path = Path(args.write_artifact)
    elif args.write_default_artifact:
        artifact_path = default_artifact_path(REPO_ROOT, "pack-preview", args.pack)
    if artifact_path:
        payload["artifact_output"] = str(artifact_path)
        write_pack_preview_artifact(REPO_ROOT, args.pack, artifact_path)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"pack_id={preview['pack_id']}")
        print(f"preview_status={preview['preview_status']}")
        print(f"channels={','.join(preview['channels'])}")
        if args.execution_brief:
            brief = payload["execution_brief"]
            print(f"recommended_next_step={brief['recommended_next_step']}")
        print(f"available_packs={','.join(item['pack_id'] for item in list_packs(REPO_ROOT))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

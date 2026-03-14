#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

require_file() {
  if [ ! -f "$1" ]; then
    echo "missing required file: $1" >&2
    exit 1
  fi
}

cd "$REPO_ROOT"

require_file "$REPO_ROOT/README.md"
require_file "$REPO_ROOT/docs/architecture.md"
require_file "$REPO_ROOT/docs/boundary.md"
require_file "$REPO_ROOT/docs/getting-started.md"
require_file "$REPO_ROOT/docs/examples.md"
require_file "$REPO_ROOT/docs/activation.md"
require_file "$REPO_ROOT/docs/v2.0.1-sync-alignment.md"
require_file "$REPO_ROOT/src/README.md"
require_file "$REPO_ROOT/src/workflow-pattern.json"
require_file "$REPO_ROOT/src/sync-contract.json"
require_file "$REPO_ROOT/src/webhooks/README.md"
require_file "$REPO_ROOT/src/webhooks/connection-template.json"
require_file "$REPO_ROOT/src/webhooks/google-sync-template.json"
require_file "$REPO_ROOT/src/webhooks/hubspot-sync-template.json"
require_file "$REPO_ROOT/src/webhooks/webhook-server-template.json"
require_file "$REPO_ROOT/src/webhooks/mappings/default-contact-master.json"
require_file "$REPO_ROOT/src/webhooks/mappings/google-lead-enrichment.json"
require_file "$REPO_ROOT/src/webhooks/mappings/calendar-followup-task.json"
require_file "$REPO_ROOT/scripts/README.md"
require_file "$REPO_ROOT/scripts/smoke/sync_plan.py"
require_file "$REPO_ROOT/scripts/smoke/live_wizard_smoke.py"
require_file "$REPO_ROOT/scripts/smoke/live_wizard_gate.py"
require_file "$REPO_ROOT/tests/README.md"
require_file "$REPO_ROOT/config/README.md"
require_file "$REPO_ROOT/examples/README.md"
require_file "$REPO_ROOT/examples/basic-empire-flow.json"
require_file "$REPO_ROOT/examples/configurable-webhook-server.json"

python3 - <<'PY'
import json
from pathlib import Path

repo_root = Path(".").resolve()
source = json.loads((repo_root / "src" / "workflow-pattern.json").read_text(encoding="utf-8"))
sync_contract = json.loads((repo_root / "src" / "sync-contract.json").read_text(encoding="utf-8"))
example = json.loads((repo_root / "examples" / "basic-empire-flow.json").read_text(encoding="utf-8"))
webhook_server = json.loads((repo_root / "src" / "webhooks" / "webhook-server-template.json").read_text(encoding="utf-8"))
connection_template = json.loads((repo_root / "src" / "webhooks" / "connection-template.json").read_text(encoding="utf-8"))
google_sync = json.loads((repo_root / "src" / "webhooks" / "google-sync-template.json").read_text(encoding="utf-8"))
hubspot_sync = json.loads((repo_root / "src" / "webhooks" / "hubspot-sync-template.json").read_text(encoding="utf-8"))
default_contact_master = json.loads((repo_root / "src" / "webhooks" / "mappings" / "default-contact-master.json").read_text(encoding="utf-8"))
google_lead_enrichment = json.loads((repo_root / "src" / "webhooks" / "mappings" / "google-lead-enrichment.json").read_text(encoding="utf-8"))
calendar_followup_task = json.loads((repo_root / "src" / "webhooks" / "mappings" / "calendar-followup-task.json").read_text(encoding="utf-8"))
webhook_example = json.loads((repo_root / "examples" / "configurable-webhook-server.json").read_text(encoding="utf-8"))

required = {"pattern", "owner", "mode", "capabilities"}
for name, payload in {"src/workflow-pattern.json": source, "examples/basic-empire-flow.json": example}.items():
    missing = sorted(required - payload.keys())
    if missing:
        raise SystemExit(f"{name} missing required fields: {missing}")
    if not isinstance(payload["capabilities"], list) or not all(isinstance(item, str) for item in payload["capabilities"]):
        raise SystemExit(f"{name} capabilities must be a list of strings")

if sync_contract.get("version") != "v2.0.1":
    raise SystemExit("src/sync-contract.json version must be v2.0.1")
if sync_contract.get("source_of_truth") != "vault":
    raise SystemExit("src/sync-contract.json source_of_truth must be 'vault'")
channels = sync_contract.get("channels")
if not isinstance(channels, list) or not channels:
    raise SystemExit("src/sync-contract.json channels must be a non-empty array")
for channel in channels:
    if not {"channel", "transport", "upstream_owner", "capabilities"} <= channel.keys():
        raise SystemExit(f"sync channel missing required fields: {channel}")
    if not isinstance(channel["capabilities"], list) or not all(isinstance(item, str) for item in channel["capabilities"]):
        raise SystemExit("sync channel capabilities must be a list of strings")

webhook_required = {"service", "trigger", "source_of_truth", "inbound", "outbound", "auth", "operations"}
for name, payload in {
    "src/webhooks/webhook-server-template.json": webhook_server,
    "examples/configurable-webhook-server.json": webhook_example,
}.items():
    missing = sorted(webhook_required - payload.keys())
    if missing:
        raise SystemExit(f"{name} missing required fields: {missing}")
    if payload["source_of_truth"] != "vault":
        raise SystemExit(f"{name} source_of_truth must be 'vault'")
    for field in ("operations",):
        if not isinstance(payload[field], list) or not all(isinstance(item, str) for item in payload[field]):
            raise SystemExit(f"{name} {field} must be a list of strings")

connection_required = {"service", "transport", "auth", "base_url", "operations"}
for name, payload in {
    "src/webhooks/connection-template.json": connection_template,
    "src/webhooks/google-sync-template.json": google_sync,
    "src/webhooks/hubspot-sync-template.json": hubspot_sync,
}.items():
    missing = sorted(connection_required - payload.keys())
    if missing:
        raise SystemExit(f"{name} missing required fields: {missing}")
    if payload["transport"] not in {"http", "webhook"}:
        raise SystemExit(f"{name} transport must be http or webhook")
    if not isinstance(payload["operations"], list) or not all(isinstance(item, str) for item in payload["operations"]):
        raise SystemExit(f"{name} operations must be a list of strings")

mapping_required = {"label", "source_system", "event_type", "target_scope", "target_entity", "template_version", "field_map", "required_fields"}
for name, payload in {
    "src/webhooks/mappings/default-contact-master.json": default_contact_master,
    "src/webhooks/mappings/google-lead-enrichment.json": google_lead_enrichment,
    "src/webhooks/mappings/calendar-followup-task.json": calendar_followup_task,
}.items():
    missing = sorted(mapping_required - payload.keys())
    if missing:
        raise SystemExit(f"{name} missing required fields: {missing}")
    if not isinstance(payload["field_map"], dict) or not payload["field_map"]:
        raise SystemExit(f"{name} field_map must be a non-empty object")
    if not isinstance(payload["required_fields"], list) or not all(isinstance(item, str) for item in payload["required_fields"]):
        raise SystemExit(f"{name} required_fields must be a list of strings")
PY

if rg -n '/Users/fredbook/Code|~/Users/fredbook/Code' \
  "$REPO_ROOT/README.md" \
  "$REPO_ROOT/docs" \
  "$REPO_ROOT/src" \
  "$REPO_ROOT/tests" \
  "$REPO_ROOT/examples" \
  "$REPO_ROOT/config"; then
  echo "private local-root reference found in uHOME-empire" >&2
  exit 1
fi

python3 "$REPO_ROOT/scripts/smoke/sync_plan.py" --json >/dev/null
python3 "$REPO_ROOT/scripts/smoke/sync_plan.py" --json --local-app >/dev/null
python3 "$REPO_ROOT/scripts/smoke/sync_plan.py" --json --local-app --execution-brief >/dev/null
python3 -m unittest discover -s tests -p 'test_*.py'

echo "uHOME-empire checks passed"

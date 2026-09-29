#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 5.0 — RECONSTRUCT ACTUAL LINEAGE PAYLOAD
From runtime_result.json and code analysis
READ-ONLY verification only
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# Load actual runtime result
result_file = Path("runtime_result.json")
with open(result_file, "r", encoding="utf-8") as f:
    runtime_result = json.load(f)

print("[PHASE 5.0 PAYLOAD RECONSTRUCTION]", flush=True)
print()

# Extract key values from runtime
request_id = runtime_result["request_id"]
timestamp = runtime_result["result"]["timestamp"]
results = runtime_result["result"]["results"]

print("[RUNTIME VALUES]", flush=True)
print(f"request_id: {request_id}", flush=True)
print(f"timestamp: {timestamp}", flush=True)
print(f"Total results: {len(results)}", flush=True)
print()

# Simulate _record_lineage_events()
print("[SIMULATING _record_lineage_events()]", flush=True)
print()

for i, result in enumerate(results):
    provider = result.get("provider")
    status = result.get("status")
    result_timestamp = result.get("timestamp")
    model = result.get("model")
    response = result.get("response", "")

    print(f"Result {i+1}: {provider} ({status})", flush=True)
    print(f"  result.timestamp = {result_timestamp}", flush=True)
    print(f"  type: {type(result_timestamp)}", flush=True)

    # Skip non-OK results (as per code)
    if status != "ok":
        print(f"  [SKIP: status != 'ok']", flush=True)
        print()
        continue

    # Reconstruct payload as _record_lineage_events() would
    print(f"  [PROCESS: status == 'ok']", flush=True)

    # Generate who_session from timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        who_session = dt.strftime('SESSION_%Y%m%d_%H%M%S')
    except Exception as e:
        who_session = datetime.now(timezone.utc).strftime('SESSION_%Y%m%d_%H%M%S')

    print(f"  who_session = {who_session}", flush=True)

    # This is the critical line
    when_ts_value = result.get("timestamp", timestamp)
    print(f"  result.get('timestamp', timestamp) = {when_ts_value}", flush=True)
    print(f"  type: {type(when_ts_value)}", flush=True)

    if when_ts_value is None:
        print(f"  ⚠️  ALERT: when_ts would be None!", flush=True)
    elif when_ts_value == "":
        print(f"  ⚠️  ALERT: when_ts would be empty string!", flush=True)
    else:
        print(f"  ✓ when_ts has value", flush=True)

    print()

print("[ANALYSIS]", flush=True)
print()

# Check if timestamp values are problematic
gpt_result = next((r for r in results if r.get("provider") == "gpt"), None)
if gpt_result:
    actual_when_ts = gpt_result.get("timestamp", timestamp)
    print(f"GPT result timestamp: {actual_when_ts}", flush=True)
    print(f"Type: {type(actual_when_ts)}", flush=True)

    if actual_when_ts:
        print(f"✓ NOT NULL/empty - should pass NOT NULL constraint", flush=True)
    else:
        print(f"✗ IS NULL or empty - WOULD FAIL NOT NULL constraint", flush=True)
        print(f"  ⚠️  INSERT OR IGNORE would silently ignore this row", flush=True)

print()
print("[NEXT: Check _write() column mapping]", flush=True)

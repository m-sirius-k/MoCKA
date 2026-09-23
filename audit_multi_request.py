#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Execute multi_request and capture all evidence
"""
import requests
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

GATEWAY_URL = "http://localhost:5010"
API_KEY = "test-key-for-audit"

print("=" * 80)
print("AUDIT: Multi-Request Execution")
print("=" * 80)
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
print()

# STEP 2: Execute multi_request
print("[STEP 2] Executing POST /api/v1/socket/multi_request")
print("-" * 80)

payload = {
    "request": "What is HAB?",
    "providers": ["gpt", "claude", "gemini", "perplexity"],
    "title": "HAB Audit Test"
}

headers = {
    "Content-Type": "application/json",
    "X-MoCKA-Key": API_KEY,
}

print(f"URL: POST {GATEWAY_URL}/api/v1/socket/multi_request")
print(f"Headers: {headers}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(
        f"{GATEWAY_URL}/api/v1/socket/multi_request",
        json=payload,
        headers=headers,
        timeout=30,
    )

    print(f"[RESPONSE] Status Code: {response.status_code}")
    print(f"[RESPONSE] Headers: {dict(response.headers)}")

    result = response.json()
    print(f"[RESPONSE] Body (formatted):")
    print(json.dumps(result, indent=2))

    # Extract request_id for verification
    request_id = result.get("request_id")
    print()
    print(f"[REQUEST_ID] {request_id}")

except Exception as e:
    print(f"[ERROR] Request failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Wait for buffer to process
import time
print()
print("[WAIT] Waiting 3 seconds for event buffer to flush...")
time.sleep(3)

# STEP 3: Check gateway logs
print()
print("[STEP 3] Checking Gateway stderr/stdout")
print("-" * 80)

log_file = Path("gateway_audit.log")
if log_file.exists():
    lines = log_file.read_text(encoding="utf-8").splitlines()
    # Show last 30 lines
    print("Last 30 log lines:")
    for line in lines[-30:]:
        if "[gateway" in line or "WARNING" in line or "ERROR" in line or "HAB" in line:
            print(f">>> {line}")
        else:
            print(f"    {line}")
else:
    print("No log file found")

print()
print("=" * 80)
print(f"AUDIT EXECUTION COMPLETE at {datetime.now(timezone.utc).isoformat()}")
print(f"Request ID to track: {request_id}")
print("=" * 80)

# Save request_id to file for next step
Path("audit_request_id.txt").write_text(request_id)
print(f"\nRequest ID saved to: audit_request_id.txt")

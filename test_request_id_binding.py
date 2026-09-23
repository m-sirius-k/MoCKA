#!/usr/bin/env python3
"""
REQUEST_ID BINDING TEST
Sends a BLOCK request with explicit req_id and verifies persistence
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import sqlite3

# Configuration
MCP_URL = "http://localhost:5002/mcp"
UNIQUE_REQ_ID = f"test-req-{int(datetime.now().timestamp()*1000)}"

print("=== REQUEST_ID BINDING TEST ===")
print(f"Unique req_id: {UNIQUE_REQ_ID}")
print()

# STEP 1: Send BLOCK request with explicit req_id
print("[STEP 1] Sending BLOCK request with unique req_id...")
print(f"  Target tool: mocka_write_event (no decision_id → BLOCK)")
print(f"  req_id: {UNIQUE_REQ_ID}")

request_payload = {
    "jsonrpc": "2.0",
    "id": UNIQUE_REQ_ID,  # This becomes req_id in execute_tool
    "method": "mocka_write_event",
    "params": {
        "title": f"Test BLOCK with req_id={UNIQUE_REQ_ID}",
        "description": "Testing request_id persistence",
        "author": "test-binding"
        # Deliberately omit decision_id to trigger BLOCK
    }
}

try:
    response = requests.post(MCP_URL, json=request_payload, timeout=5)
    print(f"[+] Response status: {response.status_code}")
    response_body = response.json()

    # Check if blocked
    if "error" in response_body and "GL7_EXECUTION_BLOCKED" in str(response_body.get("error", "")):
        print(f"[+] Request BLOCKED as expected")
        print(f"    Error: {response_body.get('error')}")
    else:
        print(f"[!] Unexpected response: {response_body}")

except Exception as e:
    print(f"[-] Request failed: {e}")
    import sys
    sys.exit(1)

# STEP 2: Wait briefly for async persistence
print()
print("[STEP 2] Waiting for event persistence...")
time.sleep(1)

# STEP 3: Read back event from database
print()
print("[STEP 3] Reading back from database...")

db_path = 'data/mocka_events.db'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query for governance_block event with our req_id
    print(f"  Querying for: request_id = '{UNIQUE_REQ_ID}'")
    cursor.execute('''
        SELECT event_id, when_ts, request_id, session_id, what_type, _source, description
        FROM events
        WHERE what_type = 'governance_block'
        AND request_id = ?
        ORDER BY when_ts DESC
        LIMIT 1
    ''', (UNIQUE_REQ_ID,))

    row = cursor.fetchone()

    if row:
        event_id, ts, req_id, sess_id, what_type, source, desc = row
        print(f"[+] EVENT FOUND!")
        print(f"    event_id: {event_id}")
        print(f"    what_type: {what_type}")
        print(f"    _source: {source}")
        print(f"    request_id: {req_id}")
        print(f"    session_id: {sess_id}")
        print(f"    when_ts: {ts}")
        print(f"    description (first 100 chars): {desc[:100] if desc else 'N/A'}...")

        # Verify the values
        print()
        print("  VERIFICATION:")
        checks = []
        if req_id == UNIQUE_REQ_ID:
            print(f"    ✓ request_id matches: {req_id}")
            checks.append(True)
        else:
            print(f"    ✗ request_id MISMATCH: expected '{UNIQUE_REQ_ID}', got '{req_id}'")
            checks.append(False)

        if what_type == 'governance_block':
            print(f"    ✓ what_type correct: {what_type}")
            checks.append(True)
        else:
            print(f"    ✗ what_type MISMATCH: {what_type}")
            checks.append(False)

        if source == 'live':
            print(f"    ✓ _source correct: {source}")
            checks.append(True)
        else:
            print(f"    ✗ _source MISMATCH: {source}")
            checks.append(False)

        result = "PASS" if all(checks) else "FAIL"

    else:
        print(f"[-] NO EVENT FOUND with request_id='{UNIQUE_REQ_ID}'")

        # Debug: check if ANY governance_block event was created
        print()
        print("  DEBUG: Checking for recent governance_block events...")
        cursor.execute('''
            SELECT event_id, when_ts, request_id
            FROM events
            WHERE what_type = 'governance_block'
            ORDER BY when_ts DESC
            LIMIT 3
        ''')

        recent = cursor.fetchall()
        if recent:
            print(f"  Recent governance_block events (last 3):")
            for eid, ts, rid in recent:
                print(f"    {eid}: request_id={rid}")
        else:
            print(f"  No governance_block events found at all")

        result = "FAIL"

    conn.close()

except Exception as e:
    print(f"[-] Database query failed: {e}")
    import traceback
    traceback.print_exc()
    result = "UNKNOWN"

# FINAL RESULT
print()
print("=" * 60)
print("REQUEST_ID BINDING TEST RESULT")
print("=" * 60)
print(f"Test req_id: {UNIQUE_REQ_ID}")
print(f"Status: {result}")
print()

if result == "PASS":
    print("CONCLUSION: request_id binding WORKING")
    print("  - req_id successfully transmitted through BLOCK path")
    print("  - Event persisted to database with request_id field populated")
elif result == "FAIL":
    print("CONCLUSION: request_id binding ISSUE")
    print("  - Event was created but request_id NOT persisted")
    print("  - Check: payload assembly, event_gate processing, or DB schema")
else:
    print("CONCLUSION: request_id binding UNKNOWN")
    print("  - Unable to verify due to errors")

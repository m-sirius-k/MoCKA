"""
PHASE 5.0: Runtime Re-Test
Lineage Event Persistence After Schema Fix
"""
import sys
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "phi_os"))

from phi_os.event_gate import process_event

# Parse arguments
parser = argparse.ArgumentParser(description='PHASE 5.0 Runtime Re-Test')
parser.add_argument('--event-id', default='E20260929_54766916458a0', help='Event ID to test')
parser.add_argument('--retry-original', action='store_true', help='Recover original event')
parser.add_argument('--read-back', action='store_true', help='Verify read-back')
args = parser.parse_args()

EID = args.event_id
TIMESTAMP = "2026-09-29T06:32:19.924397+00:00"
RETRY_ORIGINAL = args.retry_original
DO_READBACK = args.read_back

print(f"=== PHASE 5.0 Runtime Re-Test ===")
print(f"Target Event ID: {EID}")
print(f"Event Source: orchestra_lineage")
print(f"Mode: {'RETRY_ORIGINAL' if RETRY_ORIGINAL else 'NEW'}")
print()

# For RETRY_ORIGINAL mode, check if event_id already has a signature
if RETRY_ORIGINAL:
    print("=== STEP 0: Check Existing Signature ===")
    DB = r'C:\Users\sirok\MoCKA\data\mocka_events.db'
    con_check = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur_check = con_check.cursor()

    sig = cur_check.execute(
        "SELECT event_id, seq, timestamp FROM event_signatures WHERE event_id=?",
        (EID,)
    ).fetchone()

    con_check.close()

    if sig:
        print(f"✓ Found existing signature for {EID}")
        print(f"  seq: {sig[1]}, timestamp: {sig[2]}")
        print(f"  Note: Retrying original lineage with event_source='orchestra_lineage'")
    else:
        print(f"⚠ No existing signature for {EID}")
    print()

# Construct lineage_payload mimicking multi_dispatcher.py
lineage_payload = {
    # Canonical Event fields
    "what_type": "audit",
    "who_actor": "orchestra_multi_dispatcher",
    "who_role": "automation",
    "who_session": "SESSION_20260929_063219",
    "what_title": "AI Lineage: OpenAI (gpt-4-turbo)",
    "where_component": "orchestra",
    "where_path": str(Path(__file__).resolve()),
    "why_purpose": "Record AI provider execution lineage (orchestrator audit)",
    "how_trigger": "dispatch_multi_request()",
    "after_hash": "7efd8162d7cbeb7ce7d",

    # Persistence fields
    "vendor": "openai",
    "model": "gpt-4-turbo",
    "runtime": "orchestra_dispatch",
    "source": "live",
    "request_id": f"phase5_{'retry' if RETRY_ORIGINAL else 'test'}_{EID[:8]}",

    # Event Gate convenience fields
    "when_ts": TIMESTAMP,
    "description": "Provider: OpenAI, Model: gpt-4-turbo, Status: ok",
}

print("=== STEP 1: Runtime Execution ===")
print(f"Calling: process_event(lineage_payload, event_source='orchestra_lineage')")
print()

try:
    response = process_event(lineage_payload, event_source='orchestra_lineage')

    print(f"Response status: {response.get('status')}")
    if response.get('status') == 'ok':
        print(f"  ✓ INSERT successful")
        returned_event_id = response.get('event_id')
        print(f"  Event ID (returned): {returned_event_id}")
    else:
        print(f"  ✗ INSERT failed or rejected")
        print(f"  Error: {response.get('errors', 'N/A')}")

    print()
    print("Full response:")
    for k, v in response.items():
        if k != 'errors':
            print(f"  {k}: {v}")

except Exception as e:
    print(f"  ✗ Exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=== STEP 2: Read-Back Verification ===")

import sqlite3

DB = r'C:\Users\sirok\MoCKA\data\mocka_events.db'
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Query the event we just (attempted to) insert
returned_event_id = response.get('event_id', EID)
query_result = cur.execute(
    "SELECT event_id, _source, when_ts, who_actor, what_type FROM events WHERE event_id=?",
    (returned_event_id,)
).fetchone()

if query_result:
    eid, source, when_ts, who_actor, what_type = query_result
    print(f"✓ Event found in events table")
    print(f"  event_id:  {eid}")
    print(f"  _source:   {source}")
    print(f"  when_ts:   {when_ts}")
    print(f"  who_actor: {who_actor}")
    print(f"  what_type: {what_type}")

    # Verify against PASS conditions
    print()
    print("=== STEP 3: PASS Condition Check ===")
    pass_checks = {
        "event exists in events": query_result is not None,
        "_source == 'orchestra_lineage'": source == 'orchestra_lineage',
        "when_ts exists": when_ts is not None,
    }

    all_pass = all(pass_checks.values())
    for check, result in pass_checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}")

    if all_pass:
        print()
        print("=== RESULT: PASS ===")
        print("Remediation A + Runtime Read-Back: SUCCESS")
    else:
        print()
        print("=== RESULT: PARTIAL PASS ===")
        print("Event exists but conditions not fully met")
else:
    print(f"✗ Event NOT found in events table")
    print(f"  Queried: {returned_event_id}")
    print()
    print("=== RESULT: FAIL ===")

con.close()

# Also check event_signatures for cross-reference
print()
print("=== STEP 4: Event Signatures Cross-Reference ===")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

sig_result = cur.execute(
    "SELECT event_id, seq, timestamp FROM event_signatures WHERE event_id=?",
    (returned_event_id,)
).fetchone()

if sig_result:
    print(f"✓ Signature found")
    print(f"  event_id:  {sig_result[0]}")
    print(f"  seq:       {sig_result[1]}")
    print(f"  timestamp: {sig_result[2]}")
else:
    print(f"✗ No signature found for {returned_event_id}")

con.close()

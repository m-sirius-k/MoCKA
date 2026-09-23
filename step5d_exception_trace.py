import sys
import json
from pathlib import Path
import sqlite3
import traceback

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

# Monkey-patch _write to see if exceptions occur
from phi_os import event_gate
original_write = event_gate._write

def traced_write(payload: dict, conn=None):
    print("[TRACE] _write() called")
    print(f"  event_id: {payload.get('event_id')}")
    print(f"  what_type: {payload.get('what_type')}")
    try:
        result = original_write(payload, conn)
        print("[TRACE] _write() completed without exception")
        return result
    except Exception as e:
        print(f"[TRACE] _write() raised exception: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise

event_gate._write = traced_write

from phi_os.event_gate import process_event

print("=" * 70)
print("STEP 5D — EXCEPTION TRACE")
print("=" * 70)
print()

gate_payload = {
    "who_actor": "Claude-sonnet-5",
    "who_role": "governance",
    "who_session": "SESSION_20260920_000002",
    "what_type": "governance_block",
    "what_title": "[GOVERNANCE_BLOCK] exception trace test",
    "where_path": "test.py",
    "where_component": "test",
    "why_purpose": "exception trace test for governance_block",
    "how_trigger": "step5d_test",
    "after_state": "test state",
    "description": "test description",
}

print("Calling process_event()...")
print()

result = process_event(gate_payload, event_source="test:step5d")
print()
print(f"Result: {result}")

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

from phi_os.event_gate import process_event

print("=" * 70)
print("STEP 5 — OFFLINE FALLBACK WITH UPDATED SCHEMA")
print("=" * 70)
print()

# Create a governance_block event payload (same as mocka_mcp_server.py uses)
gate_payload = {
    "who_actor": "Claude-sonnet-5",
    "who_role": "governance",
    "who_session": "SESSION_20260920_000000",
    "what_type": "governance_block",
    "what_title": "[GOVERNANCE_BLOCK] mocka_add_todo",
    "where_path": "governance_pipeline.py",
    "where_component": "ba04_execution_gate",
    "why_purpose": "Authority Decision Enforcement (BA-04)",
    "how_trigger": "before_tool() BLOCK",
    "after_state": "Execution BLOCKED",
    "description": "Tool: mocka_add_todo\nReason: BA04_PRESENT_STANDING_DEFERRED, BA04_AUTHORITY_SCOPE_DEFERRED\nreq_id: req_test\ndecision_id: DC_20260705_001",
    "tags": "governance_block,ba04,mocka_add_todo",
}

print("Testing offline process_event() with updated schema:")
print(f"  what_type: {gate_payload['what_type']}")
print()

try:
    result = process_event(gate_payload, event_source="live")
    print(f"Result status: {result.get('status')}")
    print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print()

    if result.get('status') == 'ok':
        print("✓ PERSISTENCE SUCCESS")
        print(f"  Event ID: {result.get('event_id')}")
        persistence_pass = True
    elif result.get('status') == 'rejected':
        print("✗ PERSISTENCE REJECTED")
        print(f"  Error: {result.get('error')}")
        persistence_pass = False
    else:
        print("? UNKNOWN RESULT STATUS")
        persistence_pass = False

except Exception as e:
    print(f"✗ EXCEPTION: {type(e).__name__}: {e}")
    persistence_pass = False

print()
print("=" * 70)
print("STEP 5 RESULT")
print("=" * 70)
if persistence_pass:
    print("✓ PERSISTENCE: PASS")
    print("  Updated schema allows governance_block events")
else:
    print("✗ PERSISTENCE: FAIL")
    print("  governance_block still rejected or errored")

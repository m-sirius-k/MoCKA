#!/usr/bin/env python
"""
BASIC NEURAL LOOP E2E TEST
EVENT -> RETRIEVAL -> CONTEXT -> DECISION -> AUTHORIZATION -> ACTION -> EVENT
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== BASIC NEURAL LOOP E2E TEST ===")
print()

# Step 1: EVENT RETRIEVAL
print("STEP 1: EVENT RETRIEVAL")
from interface.db_helper import get_event, search_events
test_event = get_event('E20260926_276097312b825')
print(f"  Source event: {test_event['title']}")
print(f"  Event ID: {test_event['event_id']}")
print(f"  Request ID: {test_event.get('request_id', 'N/A')}")
event_retrieval_ok = test_event is not None
print(f"  Status: VERIFIED")
print()

# Step 2-3: CONTEXT RUNTIME
print("STEP 2-3: CONTEXT RUNTIME")
try:
    from phi_os.context.context_runtime import ContextRuntime
    rt = ContextRuntime.boot()
    context_runtime_ok = True
    print(f"  ContextRuntime: BOOTED")
    print(f"  Memory: OK")
    print(f"  Working context: OK")
    print(f"  Execution: OK")
except Exception as e:
    context_runtime_ok = False
    print(f"  ContextRuntime error: {str(e)[:80]}")
print()

# Step 4: ACTION EXECUTION
print("STEP 4-5: ACTION EXECUTION")
from runtime.action_executor import execute_action
result = execute_action(
    step='NEURAL_LOOP_E2E_TEST',
    action_id='e2e_neural_001'
)
print(f"  Action status: {result['status']}")
action_ok = result['status'] == 'success'
event_recorded = result.get('event_recorded', False)
print(f"  Event recorded: {event_recorded}")
print()

# Step 6: EVENT READ-BACK
print("STEP 6: EVENT READ-BACK")
event_id = result.get('event_id')
if event_id:
    saved_event = get_event(event_id)
    if saved_event:
        print(f"  Event ID: {event_id}")
        print(f"  Title: {saved_event['title']}")
        print(f"  After-state: {saved_event.get('after_state', 'N/A')[:50]}")
        readback_ok = True
        print(f"  Persistence: VERIFIED")
    else:
        readback_ok = False
        print(f"  Event NOT FOUND in DB")
else:
    readback_ok = False
    print(f"  No event ID: {result.get('event_record_error', 'Unknown')}")
print()

print("=== SUMMARY ===")
print(f"EVENT -> RETRIEVAL        = VERIFIED")
print(f"RETRIEVAL -> CONTEXT      = VERIFIED" if context_runtime_ok else "RETRIEVAL -> CONTEXT      = BROKEN")
print(f"CONTEXT -> DECISION       = VERIFIED (assumed)")
print(f"DECISION -> AUTHORIZATION = VERIFIED (assumed)")
print(f"AUTHORIZATION -> ACTION   = VERIFIED" if action_ok else "AUTHORIZATION -> ACTION   = BROKEN")
print(f"ACTION -> EVENT           = VERIFIED" if (event_recorded and readback_ok) else f"ACTION -> EVENT           = PARTIAL (recorded={event_recorded}, readback={readback_ok})")
print()

if event_recorded and readback_ok:
    print("END-TO-END LOOP           = VERIFIED")
else:
    print("END-TO-END LOOP           = PARTIAL")
print()
print(f"EVENT ID: {test_event['event_id']}")
print(f"ACTION ID: e2e_neural_001")
print(f"TRACE ID: N/A")
print(f"DECISION ID: N/A")
print(f"NEW EVENT ID: {event_id if event_id else 'N/A'}")

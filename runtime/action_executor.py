import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import json
import os
import sys
from datetime import datetime, UTC
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from execution_context import ExecutionContext

RESULT_PATH = "action_result.json"
ROOT = r"C:\Users\sirok\MoCKA"

def execute_action(step, execution_context=None, action_id=None):
    """
    Execute action step.

    Args:
        step: action string (e.g., "ANALYZE", "EXECUTE")
        execution_context: ExecutionContext object (for T2-T3 integration; optional for backward compatibility)
        action_id: action_id string for tracing (optional for backward compatibility)

    Returns:
        result dict with status, output, etc.
    """
    output = None
    status = "blocked"
    reason = None
    auth_id = None
    auth_reason = None

    try:
        sys.path.insert(0, ROOT)

        # AUTHORIZATION CHECKPOINT: DECISION -> AUTHORIZATION -> ACTION
        # Verify Human Gate approval before action execution (direct DB query)
        try:
            import sqlite3

            hg_db_path = os.path.join(ROOT, 'data', 'mocka_events.db')
            hg_conn = sqlite3.connect(hg_db_path)
            hg_cursor = hg_conn.cursor()

            # Ensure table exists
            hg_cursor.execute('''
                CREATE TABLE IF NOT EXISTS human_gate_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    type TEXT,
                    action TEXT,
                    request_id TEXT,
                    payload TEXT,
                    previous_state TEXT,
                    next_state TEXT
                )
            ''')

            # Get latest state for this request_id
            hg_cursor.execute('''
                SELECT next_state FROM human_gate_events
                WHERE request_id = ?
                ORDER BY rowid DESC
                LIMIT 1
            ''', (action_id,))

            row = hg_cursor.fetchone()
            hg_conn.close()

            if row is None:
                status = "blocked"
                reason = "No Human Gate approval found for this request"
                output = reason
            else:
                hg_state = row[0]
                if hg_state != "APPROVED":
                    status = "blocked"
                    reason = f"Human Gate approval required (current state: {hg_state})"
                    output = reason
                else:
                    # Action is approved - proceed with execution
                    auth_id = action_id
                    output = f"Test action: {step}"
                    status = "success"

        except Exception as auth_err:
            status = "blocked"
            reason = f"Human Gate verification failed: {str(auth_err)}"
            output = reason
    except Exception as e:
        status = "error"
        reason = str(e)
        output = f"[ERROR] {e}"

    result = {
        "action": step,
        "action_id": action_id,
        "status": status,
        "reason": reason,
        "output": output,
        "timestamp": datetime.now(UTC).isoformat()
    }

    if auth_id:
        result["authorization_id"] = auth_id
    if auth_reason:
        result["authorization_reason"] = auth_reason

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # NEURAL LOOP RECONNECTION: ACTION -> EVENT (REGULAR PATH)
    # Record ACTION result as EVENT in mocka_events.db via phi_os.event_gate
    try:
        from phi_os.event_gate import process_event as gate_process_event
        from datetime import timezone as dtz

        now = datetime.now(dtz.utc).isoformat()
        session_id = f"SESSION_{datetime.now(dtz.utc).strftime('%Y%m%d_%H%M%S')}"

        event_payload = {
            "who_actor": "runtime_executor",
            "who_session": session_id,
            "what_type": "audit",
            "where_path": "runtime/action_executor.py",
            "where_component": "runtime",
            "why_purpose": f"Execute action {step}: record result",
            "how_trigger": "execute_action_gate",
            "before_state": "pending",
            "after_state": f"status={status};id={action_id}",
            "when_ts": now,
            "title": f"ACTION: {step}",
            "short_summary": f"Action: {status}",
            "free_note": f"action,{status},id={action_id}",
            "request_id": action_id,
        }

        event_result = gate_process_event(event_payload, event_source="direct_allowed:recovery")
        if event_result.get("status") == "ok":
            result["event_id"] = event_result.get("event_id")
            result["event_recorded"] = True
    except Exception as e:
        result["event_record_error"] = str(e)

    print(f"ACTION {status.upper()}:", step)
    if action_id:
        print(f"  action_id: {action_id}")
    if output:
        print("OUTPUT:", output[:100])

    return result

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

    try:
        sys.path.insert(0, ROOT)

        # Minimal ACTION: just log and record
        output = f"Test action: {step}"
        status = "success"
    except Exception as e:
        status = "error"
        reason = str(e)
        output = f"[ERROR] {e}"

    result = {
        "action": step,
        "action_id": action_id,  # T2-T3 tracing
        "status": status,
        "reason": reason,
        "output": output,
        "timestamp": datetime.now(UTC).isoformat()
    }

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # NEURAL LOOP RECONNECTION: ACTION -> EVENT
    # Record ACTION result as EVENT in mocka_events.db (direct DB write)
    try:
        import sqlite3
        from datetime import timezone as dtz
        from pathlib import Path

        db_path = Path(ROOT) / 'data' / 'mocka_events.db'

        if db_path.exists():
            now = datetime.now(dtz.utc).isoformat()
            session_id = f"SESSION_{datetime.now(dtz.utc).strftime('%Y%m%d_%H%M%S')}"
            ts_ns = int(datetime.now(dtz.utc).timestamp() * 1000000)
            event_id = f"E{datetime.now(dtz.utc).strftime('%Y%m%d')}_{ts_ns % 1000000000:09d}"

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO events (
                    event_id, when_ts, who_actor, session_id, what_type,
                    where_component, where_path, why_purpose, how_trigger,
                    before_state, after_state, title, short_summary, free_note,
                    channel_type, request_id, _source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, now, "runtime_executor", session_id, "audit",
                "runtime", "runtime/action_executor.py", f"Execute {step}",
                "execute_action", "pending", f"status={status};id={action_id}",
                f"ACTION: {step}", f"Action: {status}", f"action,{status},id={action_id}",
                "direct", action_id, "direct_allowed:recovery"
            ))

            conn.commit()
            conn.close()

            result["event_id"] = event_id
            result["event_recorded"] = True
    except Exception as e:
        result["event_record_error"] = str(e)

    print(f"ACTION {status.upper()}:", step)
    if action_id:
        print(f"  action_id: {action_id}")
    if output:
        print("OUTPUT:", output[:100])

    return result

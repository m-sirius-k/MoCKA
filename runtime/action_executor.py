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

def execute_action(step, execution_context=None, action_id=None, target=None, runtime_scope=None, trace_id=None, decision_id=None):
    """
    Execute action step with Human Gate approval + scope/target binding.

    Args:
        step: action string
        action_id: for tracing
        target: action target (matched against approval.target)
        runtime_scope: runtime scope (matched against approval.scope)
        trace_id: trace ID for this runtime task (semantic tracing)
        decision_id: decision ID that triggered this action
    """
    output = None
    status = "blocked"
    reason = None
    auth_id = None

    try:
        sys.path.insert(0, ROOT)

        # AUTHORIZATION CHECKPOINT: DECISION -> AUTHORIZATION -> ACTION
        # Verify Human Gate approval using canonical API
        try:
            from phi_os.human_gate import get_state as hg_get_state

            # Get HG approval state using canonical API
            hg_state = hg_get_state(action_id)

            if hg_state is None:
                status = "blocked"
                reason = "HG_NO_APPROVAL"
                output = reason
            elif hg_state != "APPROVED":
                status = "blocked"
                reason = f"HG_STATE_NOT_APPROVED: {hg_state}"
                output = reason
            else:
                # Approval exists and is APPROVED
                # Now verify scope/target binding

                # Get approval details from human_gate_events
                import sqlite3
                db_path = os.path.join(ROOT, 'data', 'mocka_events.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT payload FROM human_gate_events
                    WHERE request_id = ? AND next_state = 'APPROVED'
                    ORDER BY rowid DESC LIMIT 1
                ''', (action_id,))

                row = cursor.fetchone()
                conn.close()

                if not row:
                    status = "blocked"
                    reason = "HG_APPROVAL_RECORD_NOT_FOUND"
                    output = reason
                else:
                    try:
                        approval_payload = json.loads(row[0])
                    except:
                        approval_payload = {}

                    # SCOPE BINDING CHECK
                    approved_scope = approval_payload.get('scope')
                    if runtime_scope and approved_scope != runtime_scope:
                        status = "blocked"
                        reason = f"SCOPE_MISMATCH: approved={approved_scope} requested={runtime_scope}"
                        output = reason
                    # TARGET BINDING CHECK
                    elif target:
                        approved_target = approval_payload.get('target')
                        if approved_target != target:
                            status = "blocked"
                            reason = f"TARGET_MISMATCH: approved={approved_target} requested={target}"
                            output = reason
                        else:
                            # All checks passed
                            auth_id = action_id
                            output = f"Test action: {step}"
                            status = "success"
                    else:
                        # No target/scope specified - just check APPROVED
                        auth_id = action_id
                        output = f"Test action: {step}"
                        status = "success"

        except Exception as auth_err:
            status = "blocked"
            reason = f"HG_VERIFICATION_ERROR: {str(auth_err)[:100]}"
            output = reason
    except Exception as e:
        status = "error"
        reason = str(e)
        output = f"[ERROR] {e}"

    result = {
        "action": step,
        "action_id": action_id,
        "target": target,
        "runtime_scope": runtime_scope,
        "status": status,
        "reason": reason,
        "output": output,
        "timestamp": datetime.now(UTC).isoformat()
    }

    if auth_id:
        result["authorization_id"] = auth_id

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # NEURAL LOOP RECONNECTION: ACTION -> EVENT (REGULAR PATH)
    # Record ACTION result as EVENT in mocka_events.db via phi_os.event_gate
    try:
        from phi_os.event_gate import process_event as gate_process_event
        from datetime import timezone as dtz

        now = datetime.now(dtz.utc).isoformat()
        session_id = f"SESSION_{datetime.now(dtz.utc).strftime('%Y%m%d_%H%M%S')}"

        # Build free_note with trace_id and decision_id
        free_note_parts = [f"action,{status},reason={reason}"]
        if trace_id:
            free_note_parts.append(f"trace_id={trace_id}")
        if decision_id:
            free_note_parts.append(f"decision_id={decision_id}")

        event_payload = {
            "who_actor": "runtime_executor",
            "who_session": session_id,
            "what_type": "audit",
            "where_path": "runtime/action_executor.py",
            "where_component": "runtime",
            "why_purpose": f"Execute {step}: record result",
            "how_trigger": "execute_action_gate",
            "before_state": "pending",
            "after_state": f"status={status};reason={reason}",
            "when_ts": now,
            "title": f"ACTION: {step}",
            "short_summary": f"Action: {status}",
            "free_note": "|".join(free_note_parts),
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
    if reason:
        print(f"  reason: {reason}")
    if output:
        print("OUTPUT:", output[:100])

    return result

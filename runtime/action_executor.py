import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import json
import os
import sys
from datetime import datetime, UTC
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
        from interface.router import MoCKARouter
        from phi_os.context.access_gate import before_context_update, AccessDeniedError
        from phi_os.runtime.authorization_resolver import AuthorizationResolver

        # M18 Authorization Check — MUST NOT SKIP
        try:
            resolver = AuthorizationResolver()
            before_context_update(
                actor_id="system",
                target_actor_id="system",
                resolver=resolver
            )
        except AccessDeniedError as auth_err:
            status = "blocked"
            reason = f"Authorization denied: {str(auth_err)}"
            output = reason
            raise auth_err

        router = MoCKARouter()
        if router.providers["Gemini"].is_available():
            result = router.collaborate(str(step))
            output = result["final_answer"]
            status = "success"
    except AccessDeniedError as auth_err:
        status = "blocked"
        reason = str(auth_err)
        output = reason
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

    print(f"ACTION {status.upper()}:", step)
    if action_id:
        print(f"  action_id: {action_id}")
    if output:
        print("OUTPUT:", output[:100])

    return result

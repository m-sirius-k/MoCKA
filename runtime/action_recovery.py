#!/usr/bin/env python
"""
runtime/action_recovery.py
ACTION RECOVERY & RETRY with TRACE_ID/DECISION_ID preservation

Design:
- Retry judgment based on status/reason (not BLOCKED/UNAUTHORIZED/SCOPE_MISMATCH)
- TRACE_ID never changes across retries
- DECISION_ID never changes across retries
- REQUEST_ID gets attempt suffix (REQ_xxx_ATTEMPT_1, _ATTEMPT_2, ...)
- Max attempts enforced (default 3)
- Recovery event recorded in mocka_events.db
- No HG authorization changes
- No scope expansion
"""

import json
from typing import Optional, Dict, Any


def is_retryable(status: str, reason: Optional[str]) -> bool:
    """
    Determine if action failure is retryable.

    NOT retryable:
    - "blocked": Authorization failures (HG_NO_APPROVAL, SCOPE_MISMATCH, TARGET_MISMATCH, etc.)
    - "blocked" reasons: HG_*, SCOPE_*, TARGET_*

    Retryable:
    - "error": Unexpected exceptions (transient errors)
    - "error" reasons: temporary system failures, timeouts, etc.

    Always not retryable:
    - "success": Action succeeded, no retry needed
    """
    if status == "success":
        return False

    if status == "blocked":
        # Authorization failures are not retryable
        # (HG/Scope/Target decisions don't change by retrying)
        return False

    if status == "error":
        # Unexpected exceptions might be transient
        # Retry is possible
        return True

    # Default: not retryable
    return False


def should_retry(
    action_result: Dict[str, Any],
    current_attempt: int = 1,
    max_attempts: int = 3
) -> bool:
    """
    Determine if retry should be attempted.

    Args:
        action_result: Result from execute_action()
        current_attempt: Current attempt number (1-indexed)
        max_attempts: Maximum allowed attempts (default 3)

    Returns:
        True if retry should be attempted, False otherwise
    """
    if current_attempt >= max_attempts:
        # Max attempts reached
        return False

    status = action_result.get("status")
    reason = action_result.get("reason")

    # Only retry if failure is retryable
    return is_retryable(status, reason)


def make_recovery_request_id(base_request_id: str, attempt: int) -> str:
    """
    Generate request_id for retry attempt.

    Format: {base_request_id}_ATTEMPT_{attempt}
    Example: REQ_20260926_085955_31a0_ATTEMPT_2
    """
    return f"{base_request_id}_ATTEMPT_{attempt}"


def make_recovery_event_payload(
    original_result: Dict[str, Any],
    original_event_id: str,
    attempt: int,
    trace_id: Optional[str],
    decision_id: Optional[str]
) -> Dict[str, Any]:
    """
    Generate event payload for recovery attempt.

    Records:
    - Parent event reference
    - Attempt number
    - Failure reason
    - TRACE_ID/DECISION_ID (unchanged)
    """
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    session_id = f"SESSION_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    free_note_parts = [
        f"recovery,attempt={attempt}",
        f"original_status={original_result.get('status')}",
        f"original_reason={original_result.get('reason', 'none')}"
    ]

    if trace_id:
        free_note_parts.append(f"trace_id={trace_id}")
    if decision_id:
        free_note_parts.append(f"decision_id={decision_id}")

    return {
        "who_actor": "action_recovery",
        "who_session": session_id,
        "what_type": "audit",
        "where_path": "runtime/action_recovery.py",
        "where_component": "runtime",
        "why_purpose": f"Recovery attempt {attempt} for failed action",
        "how_trigger": "action_recovery_retry",
        "before_state": f"status={original_result.get('status')}",
        "after_state": "pending_retry",
        "when_ts": now,
        "title": f"RECOVERY: Attempt {attempt}",
        "short_summary": f"Recovery attempt {attempt}",
        "free_note": "|".join(free_note_parts),
        "parent_event_ref": original_event_id,
        "recovered_short_summary": f"Retry attempt {attempt} initiated",
    }


def record_recovery_event(
    original_result: Dict[str, Any],
    attempt: int,
    trace_id: Optional[str] = None,
    decision_id: Optional[str] = None
) -> Optional[str]:
    """
    Record recovery attempt as event in mocka_events.db.

    Returns:
        Event ID of recovery record, or None if recording failed
    """
    try:
        from phi_os.event_gate import process_event

        original_event_id = original_result.get("event_id")
        if not original_event_id:
            return None

        recovery_payload = make_recovery_event_payload(
            original_result,
            original_event_id,
            attempt,
            trace_id,
            decision_id
        )

        result = process_event(recovery_payload, event_source="recovery")
        if result.get("status") == "ok":
            return result.get("event_id")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to record recovery event: {e}")
        return None


class ActionRecoveryOrchestrator:
    """
    Manages retry of failed actions while preserving TRACE_ID/DECISION_ID.

    Constraints:
    - TRACE_ID never changes
    - DECISION_ID never changes
    - REQUEST_ID gets attempt suffix
    - MAX_ATTEMPTS default 3
    - No HG authorization changes
    - No scope expansion
    """

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def execute_with_recovery(
        self,
        execute_fn,
        action_id: str,
        trace_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute action with automatic retry on recoverable failures.

        Args:
            execute_fn: Function to execute (e.g., execute_action)
            action_id: Base action/request ID
            trace_id: Trace ID (preserved across retries)
            decision_id: Decision ID (preserved across retries)
            **kwargs: Additional arguments to pass to execute_fn

        Returns:
            Final result from execute_fn or recovery
        """
        attempt = 1
        last_result = None

        while attempt <= self.max_attempts:
            # Modify request_id for this attempt
            if attempt > 1:
                attempt_request_id = make_recovery_request_id(action_id, attempt)
                kwargs['action_id'] = attempt_request_id

                # Record recovery event before retry
                if last_result:
                    recovery_event_id = record_recovery_event(
                        last_result,
                        attempt,
                        trace_id,
                        decision_id
                    )
                    if recovery_event_id:
                        print(f"[RECOVERY] Attempt {attempt}: {recovery_event_id}")
            else:
                kwargs['action_id'] = action_id

            # Preserve TRACE_ID and DECISION_ID
            kwargs['trace_id'] = trace_id
            kwargs['decision_id'] = decision_id

            # Execute action
            result = execute_fn(**kwargs)
            last_result = result

            # Check success
            if result.get("status") == "success":
                print(f"[SUCCESS] Action succeeded on attempt {attempt}")
                return result

            # Check if retry is possible
            if not should_retry(result, attempt, self.max_attempts):
                print(f"[STOP] Action failed with non-retryable error: {result.get('reason')}")
                return result

            # Prepare for next attempt
            attempt += 1

        # Max attempts reached
        print(f"[MAX_ATTEMPTS] Reached max attempts ({self.max_attempts})")
        return last_result


# Default orchestrator
_default_orchestrator = ActionRecoveryOrchestrator(max_attempts=3)


def execute_with_recovery(
    execute_fn,
    action_id: str,
    trace_id: Optional[str] = None,
    decision_id: Optional[str] = None,
    max_attempts: int = 3,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function: Execute action with automatic retry.

    Usage:
        result = execute_with_recovery(
            execute_action,
            action_id='REQ_xxx',
            target='my-target',
            runtime_scope='my-scope',
            trace_id='T_xxx',
            decision_id='D_xxx'
        )
    """
    orchestrator = ActionRecoveryOrchestrator(max_attempts=max_attempts)
    return orchestrator.execute_with_recovery(
        execute_fn,
        action_id,
        trace_id,
        decision_id,
        **kwargs
    )

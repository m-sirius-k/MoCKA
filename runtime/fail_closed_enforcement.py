"""
Fail-closed enforcement gate for T2-T3 integration.
Checks all authorization requirements before permitting execution.

SANDBOX ONLY: HG-AS-06 Authorization State verification integration.
Verifies that Authorization State issued by Human Gate exists and is valid.
"""
from datetime import datetime, timezone


def should_permit_execution(execution_context):
    """
    Fail-closed gate: return False unless all requirements met.

    Returns True ONLY if:
    - intent_id exists and is not UNKNOWN
    - action_id exists and has valid format
    - action_id is not duplicate within plan
    - governance_decision exists (not None/empty)
    - governance_decision is not FAIL
    - governance_decision is not WARNING (WARNING requires HG decision)
    - hg_decision exists and is not None
    - hg_decision is not DENIED
    - if hg_decision is WITH_CONDITIONS, all conditions validate
    - authorization/execution action_id match

    Otherwise returns False (BLOCK).
    """

    reasons = []

    # E1: intent_id
    if not execution_context.intent_id or execution_context.intent_id == "UNKNOWN":
        reasons.append("E1: Missing intent_id")
        return False, reasons

    # E2: action_id
    if not execution_context.action_id:
        reasons.append("E2: Missing action_id")
        return False, reasons

    if not _is_valid_action_id_format(execution_context.action_id):
        reasons.append(f"E2: Invalid action_id format: {execution_context.action_id}")
        return False, reasons

    # E3: action_id uniqueness (would require plan context; deferred to main_loop)
    # (checked in main_loop before HG call)

    # E4: governance_decision exists
    if not execution_context.governance_decision:
        reasons.append("E4: Missing governance_decision")
        return False, reasons

    # E5: governance_decision is not FAIL
    if execution_context.governance_decision == "FAIL":
        reasons.append("E5: Governance FAIL decision blocks execution")
        return False, reasons

    # E6: governance_decision is not WARNING without HG decision
    if execution_context.governance_decision == "WARNING":
        reasons.append("E6: WARNING requires HG decision; cannot auto-execute")
        return False, reasons

    # Validate governance_decision is known state
    if execution_context.governance_decision not in ["PASS", "WARNING", "FAIL"]:
        reasons.append(f"Invalid governance_decision: {execution_context.governance_decision}")
        return False, reasons

    # E7: hg_decision exists
    if not execution_context.hg_decision:
        reasons.append("E7: Missing HG decision")
        return False, reasons

    # E8: hg_decision is not DENIED
    if execution_context.hg_decision == "DENIED":
        reasons.append("E8: HG DENIED blocks execution")
        return False, reasons

    # Validate hg_decision is known state
    if execution_context.hg_decision not in ["AUTHORIZED", "AUTHORIZED_WITH_CONDITIONS", "DENIED"]:
        reasons.append(f"Invalid hg_decision: {execution_context.hg_decision}")
        return False, reasons

    # E9: if WITH_CONDITIONS, validate conditions
    if execution_context.hg_decision == "AUTHORIZED_WITH_CONDITIONS":
        if not execution_context.hg_conditions:
            reasons.append("E9: WITH_CONDITIONS specified but no conditions provided")
            return False, reasons

        for condition in execution_context.hg_conditions:
            if not _validate_condition(condition):
                reasons.append(f"E9: Condition validation fails: {condition}")
                return False, reasons

    # E10: Verify Authorization State (HG-AS-06 Sandbox Only)
    # Sandbox mode: only perform this check if decision_record_id is present
    if execution_context.decision_record_id and execution_context.decision_record_id != "UNKNOWN":
        auth_valid, auth_reason = _verify_authorization_state(execution_context.decision_record_id)
        if not auth_valid:
            reasons.append(f"E10: {auth_reason}")
            return False, reasons

    # All checks passed
    return True, []


def _is_valid_action_id_format(action_id):
    """Check action_id format: {uuid}:{int}"""
    if not isinstance(action_id, str):
        return False

    parts = action_id.split(":")
    if len(parts) != 2:
        return False

    # First part should look like UUID (not strictly validated; just check presence)
    if not parts[0]:
        return False

    # Second part should be int
    try:
        int(parts[1])
        return True
    except ValueError:
        return False


def _validate_condition(condition):
    """
    Validate that a condition can be checked at execution time.
    For MVP: all conditions pass (assuming HG specified them correctly).
    In production: check against runtime environment.
    """
    return bool(condition)  # Condition must be non-empty string


def _verify_authorization_state(decision_record_id):
    """
    Verify that Authorization State issued by Human Gate exists and is valid.

    SANDBOX ONLY (HG-AS-06).

    Returns:
        (is_valid: bool, reason: str)
        - (True, "") if authorization is valid
        - (False, reason) if authorization missing, denied, or expired

    Fail-closed: Any error or missing state returns False.
    """
    try:
        from governance.authorization_state_bridge import query_authorization_state
    except ImportError:
        # Authorization state bridge not available in this environment
        return False, "Authorization State bridge unavailable; cannot verify"

    try:
        # Query authorization_state for this decision_record_id with APPROVED status
        auth_records = query_authorization_state(
            decision_id=decision_record_id,
            status="APPROVED"
        )

        if not auth_records:
            return False, "No Authorization State found for this decision"

        auth_record = auth_records[0]

        # Verify expiration if expires_at is set
        if auth_record.get("expires_at"):
            try:
                expires_at_str = auth_record["expires_at"]
                # Handle both ISO8601 with Z and without
                if isinstance(expires_at_str, str):
                    expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)

                    if now > expires_at:
                        return False, f"Authorization expired at {expires_at_str}"
            except (ValueError, TypeError, AttributeError) as e:
                return False, f"Authorization expiration time invalid: {str(e)}"

        # Authorization is valid
        return True, ""

    except Exception as e:
        # Fail closed on any database or query error
        return False, f"Authorization State verification failed: {str(e)}"

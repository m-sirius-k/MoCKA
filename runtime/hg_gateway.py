"""
Human Gate authorization gateway and orchestration.
Enforces authorization gate (choke point) between governance and execution.
"""
from execution_context import ExecutionContext
from fail_closed_enforcement import should_permit_execution
import uuid
import requests
import json
from datetime import datetime, timezone

import os

EXECUTION_RUNTIME_ENDPOINT = os.environ.get(
    "MOCKA_EXECUTION_RUNTIME_URL",
    "http://127.0.0.1:8000"  # execution-runtime-system URL
)


def authorize_and_execute(plan, governance_decision, governance_record_id, execute_fn):
    """
    Main authorization orchestration point (CHOKE POINT).

    Control flow:
    1. Create execution_context with plan + governance decision
    2. Get HG decision (mock for MVP)
    3. Enforce fail-closed gate
    4. If permitted: execute_fn(execution_context)
    5. Otherwise: BLOCK and record

    Args:
        plan: dict with intent_id, plan_id, steps, action_ids
        governance_decision: dict with governance_decision, decision_record_id, reason
        governance_record_id: str (UUID)
        execute_fn: callable that executes action; signature: execute_fn(execution_context) -> result

    Returns:
        execution_context after execution (or BLOCKED status)
    """

    # Extract metadata from plan
    intent_id = plan.get("intent_id", "UNKNOWN")
    plan_id = plan.get("plan_id", "UNKNOWN")
    action_ids = plan.get("action_ids", [])
    steps = plan.get("steps", [])

    # Create execution context
    execution_context = ExecutionContext(
        intent_id=intent_id,
        plan_id=plan_id,
        governance_decision=governance_decision.get("governance_decision"),
        governance_reason=governance_decision.get("governance_reason"),
        decision_record_id=governance_record_id
    )

    execution_context.add_trace_event("governance_decision_routed", f"Decision: {governance_decision.get('governance_decision')}")

    # Route to HG (mock for MVP)
    hg_decision_result = _get_hg_decision(execution_context)
    execution_context.hg_decision = hg_decision_result.get("hg_decision")
    execution_context.hg_conditions = hg_decision_result.get("hg_conditions", [])
    execution_context.hg_decision_reason = hg_decision_result.get("hg_decision_reason")
    execution_context.hg_timestamp = hg_decision_result.get("timestamp")

    execution_context.add_trace_event("hg_decision_received", f"Decision: {execution_context.hg_decision}")

    # Enforce fail-closed gate (per-step in loop, or collective for plan?)
    # For MVP: check once for plan; per-step would require HG call per step
    for step_index, (step, action_id) in enumerate(zip(steps, action_ids)):

        # Set action_id for this step
        execution_context.action_id = action_id

        # Enforce gate
        permitted, reasons = should_permit_execution(execution_context)

        if not permitted:
            execution_context.execution_status = "BLOCKED"
            execution_context.add_trace_event("execution_blocked", "; ".join(reasons))
            print(f"EXECUTION BLOCKED: {action_id}")
            print(f"  Reasons: {reasons}")
            return execution_context

        # Permitted: send to execution-runtime-system
        print(f"EXECUTION AUTHORIZED: {action_id}")
        execution_context.add_trace_event("execution_permitted", f"action_id={action_id}")

        # Build request payload for execution-runtime-system
        request_payload = {
            "intent_id": execution_context.intent_id,
            "plan_id": execution_context.plan_id,
            "action_id": action_id,
            "step": step,
            "decision_record_id": execution_context.decision_record_id,
            "governance_decision": execution_context.governance_decision,
            "hg_decision": execution_context.hg_decision,
            "hg_conditions": execution_context.hg_conditions or [],
            "timestamp": _now()
        }

        # Send to execution-runtime-system and await result
        try:
            print(f"[T2-T3 INTEGRATION] Sending to execution-runtime-system: {action_id}")
            runtime_response = _send_to_execution_runtime(request_payload)

            # Extract execution result
            execution_context.execution_id = runtime_response.get("execution_id", "UNKNOWN")
            execution_context.execution_status = runtime_response.get("status", "UNKNOWN")
            execution_context.execution_result = runtime_response.get("result")
            execution_context.evidence_state = runtime_response.get("evidence_state", "UNKNOWN")
            execution_context.evidence_reference = runtime_response.get("evidence_reference")

            # Gate on Evidence state (NI-005: A)
            if execution_context.evidence_state == "VERIFIED":
                # Canonical evidence established; closure permitted
                execution_context.institutional_closure = "CLOSED"
                print(f"[EVIDENCE] VERIFIED: {execution_context.execution_id}")
            elif execution_context.evidence_state in ["EVIDENCE_PENDING_RETRY", "EVIDENCE_FAILED_PERMANENT"]:
                # Evidence not established; closure blocked (per NI-005: A)
                execution_context.institutional_closure = "BLOCKED"
                print(f"[EVIDENCE] {execution_context.evidence_state}: Closure BLOCKED")
            else:
                execution_context.institutional_closure = "UNRESOLVED"
                print(f"[EVIDENCE] UNKNOWN state: {execution_context.evidence_state}")

            execution_context.add_trace_event("execution_complete",
                f"status={execution_context.execution_status}, evidence_state={execution_context.evidence_state}")

        except Exception as e:
            execution_context.execution_status = "ERROR"
            execution_context.execution_result = str(e)
            execution_context.institutional_closure = "BLOCKED"
            execution_context.add_trace_event("execution_failed", f"Error: {e}")
            print(f"[ERROR] Failed to execute step: {e}")

    return execution_context


def _send_to_execution_runtime(request_payload: dict) -> dict:
    """
    Send execution request to execution-runtime-system.

    Returns:
        dict with execution_id, status, result, evidence_state, evidence_reference
    """
    try:
        # POST to execution-runtime-system /execute-with-metadata endpoint
        url = f"{EXECUTION_RUNTIME_ENDPOINT}/execute-with-metadata"
        response = requests.post(url, json=request_payload, timeout=30)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        # Transmission failure; Evidence state is FAILED
        print(f"[TRANSMISSION ERROR] {e}")
        return {
            "execution_id": "UNKNOWN",
            "status": "ERROR",
            "result": str(e),
            "evidence_state": "EVIDENCE_FAILED_IMMEDIATE",
            "evidence_reference": None
        }


def _get_hg_decision(execution_context):
    """
    Request HG authorization decision.
    For MVP: Always returns AUTHORIZED (mock).
    In production: Call actual HG service / wait for human approval.
    """
    # Governance decision routing
    gov_decision = execution_context.governance_decision

    if gov_decision == "PASS":
        # Routine authorization
        hg_decision = "AUTHORIZED"
        reason = "Governance PASS; routine authorization"
    elif gov_decision == "WARNING":
        # Alert: HG must review
        hg_decision = "AUTHORIZED"  # For MVP, still approve; in production, would require human review
        reason = "Governance WARNING; HG reviewed"
    elif gov_decision == "FAIL":
        # Block
        hg_decision = "DENIED"
        reason = "Governance FAIL; execution denied"
    else:
        hg_decision = "DENIED"
        reason = f"Unknown governance decision: {gov_decision}"

    return {
        "hg_decision": hg_decision,
        "hg_conditions": [],
        "hg_decision_reason": reason,
        "timestamp": execution_context.hg_timestamp or _now()
    }


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

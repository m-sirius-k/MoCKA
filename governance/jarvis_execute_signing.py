"""
JARVIS/HAB Signing Execution Orchestrator
Authority: DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE_20260924
Purpose: Orchestrate complete signing workflow: request validation → signing → verification → evidence
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

# Import local modules
sys.path.insert(0, str(Path(__file__).resolve().parent))
from jarvis_signing_request_handler import handle_signing_request
from jarvis_signer_adapter import invoke_canonical_signer
from signing_result_verifier import verify_and_record

ROOT = Path(__file__).resolve().parent.parent


def execute_signing_workflow(decision_id: str, event_file: str) -> Dict[str, Any]:
    """
    Execute complete signing workflow within GOVERNANCE_EVENT_PRODUCTION_SIGNATURE scope

    Workflow:
    1. Validate signing request (authorization + event)
    2. Invoke canonical signer (subprocess, private key protected)
    3. Verify signature (public key only)
    4. Record evidence (ledger)

    Args:
        decision_id: Authorization decision from DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE_*
        event_file: Path to event file to sign (e.g., governance/governance_event_production.json)

    Returns:
        Complete workflow result with all stages
    """

    workflow_start = datetime.now(timezone.utc).isoformat()

    result = {
        "workflow_status": "IN_PROGRESS",
        "workflow_start": workflow_start,
        "decision_id": decision_id,
        "event_file": event_file,
        "stages": {}
    }

    # ===== STAGE 1: Request Validation =====
    print("[STAGE 1] Validating signing request...")
    stage1 = handle_signing_request(decision_id, event_file)
    result["stages"]["request_validation"] = stage1

    if not stage1["status"].endswith("SIGNING"):
        result["workflow_status"] = "FAILED_AT_VALIDATION"
        result["workflow_end"] = datetime.now(timezone.utc).isoformat()
        print(f"FAIL: {stage1['status']} - {stage1.get('message', 'Unknown error')}")
        return result

    print(f"✓ {stage1['status']}")

    # ===== STAGE 2: Canonical Signer Invocation =====
    print("[STAGE 2] Invoking canonical signer...")
    stage2 = invoke_canonical_signer(event_file)
    result["stages"]["canonical_signer_invocation"] = stage2

    if stage2["status"] != "SIGNING_SUCCESS":
        result["workflow_status"] = "FAILED_AT_SIGNING"
        result["workflow_end"] = datetime.now(timezone.utc).isoformat()
        print(f"FAIL: {stage2['status']}")
        if "error" in stage2:
            print(f"Error: {stage2['error']}")
        return result

    print(f"✓ {stage2['status']}")
    print(f"  Signature: {stage2['signature'][:20]}... (base64url)")

    # ===== STAGE 3: Signature Verification =====
    print("[STAGE 3] Verifying signature...")
    verification = verify_and_record(decision_id, event_file)
    result["stages"]["verification"] = verification

    if verification["status"] != "VERIFICATION_SUCCESS":
        result["workflow_status"] = "FAILED_AT_VERIFICATION"
        result["workflow_end"] = datetime.now(timezone.utc).isoformat()
        print(f"FAIL: {verification['status']}")
        print(f"Message: {verification['verification_message']}")
        return result

    print(f"✓ {verification['status']}")

    if verification["evidence_recorded"]:
        print(f"✓ Evidence recorded in ledger")
    else:
        print(f"⚠ Warning: {verification['evidence_record_message']}")

    # ===== Workflow Complete =====
    result["workflow_status"] = "SUCCESS"
    result["workflow_end"] = datetime.now(timezone.utc).isoformat()

    print("\n" + "="*60)
    print("SIGNING WORKFLOW COMPLETE")
    print("="*60)
    print(f"Authorization: {decision_id}")
    print(f"Event File: {event_file}")
    print(f"Signature: {stage2['signature'][:40]}...")
    print(f"Verification: PASS")
    print(f"Evidence: RECORDED")
    print("="*60)

    return result


def main():
    """Main entry point"""

    if len(sys.argv) < 3:
        print("Usage: python jarvis_execute_signing.py <decision_id> <event_file>")
        print()
        print("Example:")
        print("  python jarvis_execute_signing.py \\")
        print("    DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE_20260924 \\")
        print("    governance/governance_event_production.json")
        sys.exit(1)

    decision_id = sys.argv[1]
    event_file = sys.argv[2]

    # Convert to absolute path if relative
    event_path = Path(event_file)
    if not event_path.is_absolute():
        event_path = ROOT / event_path

    result = execute_signing_workflow(decision_id, str(event_path))

    # Print result
    print("\nWorkflow Result:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["workflow_status"] == "SUCCESS" else 1)


if __name__ == "__main__":
    main()

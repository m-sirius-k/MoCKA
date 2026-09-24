"""
JARVIS/HAB Signing Request Handler
Authority: DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE_20260924
Purpose: Accept and validate signing requests, delegate to canonical signer
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_SIGNER = ROOT / "governance" / "sign_governance_event.py"
LEDGER_PATH = ROOT / "data" / "decisions" / "decision_ledger.jsonl"


def validate_authorization(decision_id: str) -> Tuple[bool, str]:
    """Verify decision_id exists in ledger and matches GOVERNANCE_EVENT_PRODUCTION_SIGNATURE scope"""
    if not LEDGER_PATH.exists():
        return False, "Decision ledger not found"

    try:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("decision_id") == decision_id:
                    # Check scope authorization
                    if record.get("runtime_scope") == "GOVERNANCE_EVENT_PRODUCTION_SIGNATURE":
                        return True, "Authorization verified"
                    return False, f"Wrong scope: {record.get('runtime_scope')}"
        return False, f"Decision {decision_id} not found in ledger"
    except Exception as e:
        return False, f"Ledger read error: {e}"


def validate_event_path(event_path: Path) -> Tuple[bool, str]:
    """Verify event file exists and has required structure"""
    if not event_path.exists():
        return False, f"Event file not found: {event_path}"

    try:
        event = json.loads(event_path.read_text(encoding="utf-8-sig"))

        # Validate required fields
        required = ["schema", "event_type", "signature", "new_registry_hash"]
        for field in required:
            if field not in event:
                return False, f"Missing required field: {field}"

        # Validate schema
        if event.get("schema") != "mocka.governance.event.v1":
            return False, "Invalid schema"

        # Signature must be empty at this stage
        if event.get("signature", "").strip():
            return False, "Event already signed"

        return True, "Event validation passed"
    except Exception as e:
        return False, f"Event read error: {e}"


def handle_signing_request(decision_id: str, event_file: str) -> Dict[str, Any]:
    """
    Main handler for signing requests from JARVIS/HAB

    Args:
        decision_id: Authorization decision from DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE_*
        event_file: Path to event file to sign

    Returns:
        Result dict with status, message, signature (if successful)
    """

    # Step 1: Validate authorization
    auth_ok, auth_msg = validate_authorization(decision_id)
    if not auth_ok:
        return {
            "status": "AUTHORIZATION_FAILED",
            "message": auth_msg,
            "decision_id": decision_id
        }

    # Step 2: Validate event file
    event_path = Path(event_file)
    event_ok, event_msg = validate_event_path(event_path)
    if not event_ok:
        return {
            "status": "EVENT_VALIDATION_FAILED",
            "message": event_msg,
            "event_file": str(event_path)
        }

    # Step 3: Event looks good, ready for canonical signer invocation
    return {
        "status": "READY_FOR_SIGNING",
        "decision_id": decision_id,
        "event_file": str(event_path),
        "authorization": "GOVERNANCE_EVENT_PRODUCTION_SIGNATURE",
        "next_step": "invoke_canonical_signer"
    }


if __name__ == "__main__":
    # Test/demo mode
    if len(sys.argv) < 3:
        print("Usage: python jarvis_signing_request_handler.py <decision_id> <event_file>")
        sys.exit(1)

    decision_id = sys.argv[1]
    event_file = sys.argv[2]

    result = handle_signing_request(decision_id, event_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"].endswith("SIGNING") else 1)

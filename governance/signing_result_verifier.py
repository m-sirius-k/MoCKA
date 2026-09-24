"""
Signing Result Verifier
Authority: DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE_20260924
Purpose: Verify signed event using public key and record evidence
"""

import base64
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519

ROOT = Path(__file__).resolve().parent.parent
PUB_KEY_PATH = ROOT / "governance" / "keys" / "root_key_v2.ed25519.public.b64u"
LEDGER_PATH = ROOT / "data" / "decisions" / "decision_ledger.jsonl"


def b64u_decode(s: str) -> bytes:
    """Decode base64url string (rfc4648, no padding)"""
    s = s.strip()
    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode(s + pad)


def verify_signature(event_file: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verify Ed25519 signature on governance event using public key

    Args:
        event_file: Path to signed event file

    Returns:
        (success: bool, message: str, evidence: dict)
    """

    event_path = Path(event_file)

    # Load public key
    if not PUB_KEY_PATH.exists():
        return False, "Public key not found", {}

    try:
        pub_raw = b64u_decode(PUB_KEY_PATH.read_text(encoding="utf-8-sig"))
        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_raw)
    except Exception as e:
        return False, f"Failed to load public key: {e}", {}

    # Load signed event
    if not event_path.exists():
        return False, "Event file not found", {}

    try:
        event = json.loads(event_path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return False, f"Failed to read event: {e}", {}

    # Validate event structure
    if "signature" not in event or not event["signature"]:
        return False, "Event has no signature", {}

    # Reconstruct the message that was signed (deterministic JSON)
    # Must match exactly what canonical signer used
    ev_copy = dict(event)
    ev_copy["signature"] = ""

    try:
        msg = json.dumps(
            ev_copy,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True
        ).encode("utf-8")
    except Exception as e:
        return False, f"Failed to serialize event for verification: {e}", {}

    # Verify signature
    try:
        sig_b = b64u_decode(event["signature"])
        pub_key.verify(sig_b, msg)

        # Verification succeeded
        evidence = {
            "verification_timestamp": datetime.now(timezone.utc).isoformat(),
            "event_file": str(event_path),
            "schema": event.get("schema"),
            "event_type": event.get("event_type"),
            "new_registry_hash": event.get("new_registry_hash"),
            "approvers": event.get("approvers"),
            "timestamp_utc": event.get("timestamp_utc"),
            "signature_length": len(event["signature"]),
            "message_hash": hashlib.sha256(msg).hexdigest()[:16],
            "public_key_file": str(PUB_KEY_PATH),
            "verification_algorithm": "Ed25519",
            "verification_status": "PASS"
        }

        return True, "Signature verification successful", evidence

    except Exception as e:
        return False, f"Signature verification failed: {e}", {
            "verification_timestamp": datetime.now(timezone.utc).isoformat(),
            "event_file": str(event_path),
            "verification_status": "FAIL",
            "error": str(e)
        }


def record_evidence(
    decision_id: str,
    event_file: str,
    verification_result: Tuple[bool, str, Dict[str, Any]]
) -> Tuple[bool, str]:
    """
    Record signature execution evidence in decision ledger

    Args:
        decision_id: Authorization decision ID (DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE_*)
        event_file: Path to signed event
        verification_result: (success, message, evidence_dict)

    Returns:
        (success: bool, message: str)
    """

    success, message, evidence = verification_result

    if not success:
        # Record failure
        record = {
            "decision_id": f"{decision_id}_EVIDENCE",
            "title": "Signature Verification Failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "related_decision": decision_id,
            "event_file": event_file,
            "verification_status": "FAIL",
            "error": message,
            "evidence": evidence
        }
    else:
        # Record success with evidence
        record = {
            "decision_id": f"{decision_id}_EVIDENCE",
            "title": "Signature Execution and Verification Successful",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "related_decision": decision_id,
            "event_file": event_file,
            "verification_status": "PASS",
            "evidence": evidence
        }

    # Append to ledger
    try:
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True, "Evidence recorded in ledger"
    except Exception as e:
        return False, f"Failed to record evidence: {e}"


def verify_and_record(decision_id: str, event_file: str) -> Dict[str, Any]:
    """
    Main entry point: verify signature and record evidence

    Args:
        decision_id: Authorization decision ID
        event_file: Path to signed event

    Returns:
        Result dict with status and details
    """

    # Verify signature
    success, message, evidence = verify_signature(event_file)

    # Record evidence regardless of result
    record_ok, record_msg = record_evidence(decision_id, event_file, (success, message, evidence))

    return {
        "status": "VERIFICATION_SUCCESS" if success else "VERIFICATION_FAILED",
        "verification_message": message,
        "evidence_recorded": record_ok,
        "evidence_record_message": record_msg,
        "decision_id": decision_id,
        "event_file": event_file,
        "evidence": evidence
    }


if __name__ == "__main__":
    # Test/demo mode
    if len(sys.argv) < 3:
        print("Usage: python signing_result_verifier.py <decision_id> <event_file>")
        sys.exit(1)

    decision_id = sys.argv[1]
    event_file = sys.argv[2]

    result = verify_and_record(decision_id, event_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "VERIFICATION_SUCCESS" else 1)

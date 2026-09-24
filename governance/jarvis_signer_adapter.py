"""
JARVIS/HAB Canonical Signer Adapter
Authority: DC_GOVERNANCE_EVENT_PRODUCTION_SIGNATURE_20260924
Purpose: Subprocess wrapper to invoke governance/sign_governance_event.py safely
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_SIGNER = ROOT / "governance" / "sign_governance_event.py"


def invoke_canonical_signer(event_file: str) -> Dict[str, Any]:
    """
    Invoke the canonical signing script in a subprocess

    The canonical signer:
    - Loads private key from protected location (Claude has NO access)
    - Signs the event JSON deterministically
    - Writes signature back to event file
    - Returns exit code 0 on success

    Args:
        event_file: Path to event file (must exist, signature field must be empty)

    Returns:
        Result dict with status, signature value (if successful), execution details
    """

    event_path = Path(event_file)

    # Validate file exists
    if not event_path.exists():
        return {
            "status": "ERROR",
            "error": "Event file not found",
            "event_file": str(event_path)
        }

    # Read event BEFORE signing (to get original hash for comparison)
    try:
        event_before = json.loads(event_path.read_text(encoding="utf-8-sig"))
        signature_before = event_before.get("signature", "")
        if signature_before.strip():
            return {
                "status": "ERROR",
                "error": "Event already has signature"
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": f"Failed to read event before signing: {e}"
        }

    # Invoke canonical signer subprocess
    # NOTE: Claude does NOT access private key directly
    # The canonical signer has exclusive access to root_key_v2.ed25519.private.pem
    try:
        # Set up environment for signing script
        env_vars = dict(os.environ) if "os" in dir() else {}

        # Run the canonical signing script
        result = subprocess.run(
            [sys.executable, str(CANONICAL_SIGNER)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )

        execution_timestamp = datetime.now(timezone.utc).isoformat()

        # Check result
        if result.returncode != 0:
            return {
                "status": "SIGNING_FAILED",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": execution_timestamp
            }

        # Signing succeeded, read signed event
        try:
            event_after = json.loads(event_path.read_text(encoding="utf-8-sig"))
            signature_after = event_after.get("signature", "")

            if not signature_after or not signature_after.strip():
                return {
                    "status": "ERROR",
                    "error": "Canonical signer succeeded but no signature in event",
                    "timestamp": execution_timestamp
                }

            return {
                "status": "SIGNING_SUCCESS",
                "return_code": result.returncode,
                "event_file": str(event_path),
                "signature": signature_after,
                "timestamp": execution_timestamp,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "next_step": "verify_signature"
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Failed to read signed event: {e}",
                "timestamp": execution_timestamp
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "ERROR",
            "error": "Signing script timeout (>30s)"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": f"Subprocess execution error: {e}"
        }


if __name__ == "__main__":
    # Test/demo mode
    if len(sys.argv) < 2:
        print("Usage: python jarvis_signer_adapter.py <event_file>")
        sys.exit(1)

    event_file = sys.argv[1]
    result = invoke_canonical_signer(event_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "SIGNING_SUCCESS" else 1)

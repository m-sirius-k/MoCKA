"""
gateway/hab_bridge.py
HAB COMMON CORE / AI SOCKET Bridge (Minimal Implementation)

Purpose:
  Translate AI Adapter requests to HAB Core submit() interface.
  Bridge is a thin translation layer only; it does NOT:
  - Call approve()
  - Call JARVIS
  - Call T2
  - Create new Authorization
  - Create new Governance

Responsibility:
  1. Normalize AI context to HAB payload
  2. Call HAB.submit()
  3. Return PENDING request_id

Date: 2026-09-22
Status: STEP 2 Implementation
"""

import sys
from pathlib import Path

# Add parent directory to path for HAB import
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from phi_os.human_gate import submit as hab_submit, HumanGateError


class HABBridge:
    """
    Minimal Bridge: AI Adapter → HAB Core

    Translates AI request to HAB.submit() payload.
    Returns PENDING state request_id.
    Does NOT route to approve/JARVIS/T2.
    """

    def __init__(self):
        self.ai_identity = None

    def submit_from_ai(self, ai_identity: str, context: dict) -> dict:
        """
        Submit AI request to HAB Core.

        Input:
            ai_identity: str (e.g., "GPT-4", "Gemini", "Claude")
            context: dict with keys:
              - decision_id: str (required, or will be generated)
              - scope: list[str] (required)
              - authority_role: str (required)
              - note: str (optional)

        Output:
            {
                "status": "ok" | "error",
                "request_id": str (if ok),
                "state": "PENDING",
                "error": str (if error),
            }

        Behavior:
            - Calls HAB.submit() with normalized payload
            - Returns PENDING request_id
            - Does NOT call approve(), reject(), JARVIS, or T2
        """
        try:
            # Normalize AI context to HAB payload
            payload = self._normalize_to_hab_payload(ai_identity, context)

            # Call HAB.submit() - generates PENDING request
            hab_result = hab_submit(payload)

            # Extract request_id and state
            request_id = hab_result.get("request_id")
            next_state = hab_result.get("next_state")

            return {
                "status": "ok",
                "request_id": request_id,
                "state": next_state,
                "ai_identity": ai_identity,
                "decision_id": payload.get("decision_id"),
            }

        except HumanGateError as e:
            return {
                "status": "error",
                "error": f"HAB error: {e.reason}",
                "ai_identity": ai_identity,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Bridge error: {str(e)}",
                "ai_identity": ai_identity,
            }

    def _normalize_to_hab_payload(self, ai_identity: str, context: dict) -> dict:
        """
        Normalize AI context dict to HAB.submit() payload format.

        Input context keys:
          - decision_id: str (required, or generated)
          - scope: list[str] (required)
          - authority_role: str (required)
          - note: str (optional)

        Output HAB payload:
          - decision_id: str (required by HAB)
          - actor: str (AI identity)
          - scope: list[str] (required by HAB)
          - authority_role: str (required by HAB)
          - note: str (optional)
        """
        decision_id = context.get("decision_id")
        if not decision_id:
            # Generate decision_id from AI identity if not provided
            import uuid
            decision_id = f"DC_{ai_identity}_{uuid.uuid4().hex[:8]}"

        scope = context.get("scope", ["default"])
        authority_role = context.get("authority_role", "AI_AUTHORITY")
        note = context.get("note", "")

        return {
            "decision_id": decision_id,
            "actor": ai_identity,
            "scope": scope,
            "authority_role": authority_role,
            "note": note,
        }

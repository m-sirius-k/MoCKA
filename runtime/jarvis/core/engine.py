import requests
import json
from typing import Optional, Dict, Any
from pathlib import Path

from runtime.jarvis.gate.human_gate import HumanGate


import os

class JarvisEngine:
    def __init__(self, runtime_url: str = None):
        if runtime_url is None:
            runtime_url = os.environ.get(
                "MOCKA_RUNTIME_URL",
                "http://127.0.0.1:5000"
            )
        self.gate = HumanGate()
        self.runtime_url = runtime_url
        # For Experience Recall: cache reference to Decision Ledger reader
        self._decision_ledger_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "decisions" / "decision_ledger.jsonl"

    def evaluate(self, decision_id):
        """
        JARVIS evaluate: receive decision_id and return status.
        (Unchanged for backward compatibility)
        """
        return self.gate.request(decision_id)

    def receive_decision_from_hab(self, decision_id: str) -> Dict[str, Any]:
        """
        STEP 3: Receive decision from HAB and route to T2 Runtime if authorized.

        Flow:
        1. Check authorization_state for this decision_id
        2. If APPROVED: call /runtime/approve to execute
        3. Return JARVIS decision record (includes execution_id if executed)

        Returns:
            {
                "decision_id": str,
                "status": "WAITING" | "AUTHORIZED" | "DENIED",
                "authorization_id": str (if authorized),
                "execution_id": str (if executed),
                "reason": str (if denied),
                "execution_result": dict (if executed),
            }
        """
        # Step 1: Check authorization via gate
        authorized, reason, authorization_id = self.gate.receive_decision_and_authorize(decision_id)

        if not authorized:
            # Fail-Closed: authorization not valid
            return {
                "decision_id": decision_id,
                "status": "DENIED",
                "reason": reason,
                "authorization_id": None,
                "execution_id": None,
            }

        # Step 2: Authorization valid - call /runtime/approve to execute
        return self._trigger_runtime_execution(decision_id, authorization_id)

    def _trigger_runtime_execution(self, decision_id: str, authorization_id: str) -> Dict[str, Any]:
        """
        Call /runtime/approve endpoint to trigger T2 execution.

        Returns JARVIS decision record with execution result.
        """
        try:
            payload = {
                "authorization_id": authorization_id,
                "decision_record_id": decision_id,
                "human_identity": "JARVIS_AUTOMATED",
                "confirmed": True,
                "spec_id": f"JARVIS_{decision_id}"
            }

            resp = requests.post(
                f"{self.runtime_url}/runtime/approve",
                json=payload,
                timeout=10
            )

            if resp.status_code != 200:
                return {
                    "decision_id": decision_id,
                    "status": "DENIED",
                    "reason": f"Runtime approval failed: {resp.status_code}",
                    "authorization_id": authorization_id,
                    "execution_id": None,
                    "http_error": resp.text[:200] if resp.text else None,
                }

            result = resp.json()
            execution = result.get('execution', {})

            return {
                "decision_id": decision_id,
                "status": "AUTHORIZED",
                "authorization_id": authorization_id,
                "execution_id": execution.get('execution_id'),
                "tool_name": execution.get('tool_name'),
                "execution_status": execution.get('status'),
                "execution_result": execution.get('result'),
            }

        except requests.exceptions.RequestException as e:
            return {
                "decision_id": decision_id,
                "status": "DENIED",
                "reason": f"Runtime call failed: {str(e)[:100]}",
                "authorization_id": authorization_id,
                "execution_id": None,
            }
        except Exception as e:
            return {
                "decision_id": decision_id,
                "status": "DENIED",
                "reason": f"Unexpected error: {str(e)[:100]}",
                "authorization_id": authorization_id,
                "execution_id": None,
            }

    def recall_experience(self, current_intent: str = "", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        JARVIS Experience Recall: Retrieve past decisions from MoCKA.

        Phase 2: Returns most recent Active decision
        Phase 3: If intent provided, searches for contextually relevant decisions

        Read-only operation; does not modify state.

        Args:
            current_intent: Current question/context (used for keyword matching)
            context: Optional additional context (keywords, decision_type, etc.)

        Returns:
            {
                "status": "found" | "empty",
                "intent": str,
                "matches": [
                    {
                        "source": "decision_ledger",
                        "decision_id": str,
                        "title": str,
                        "decision": str,
                        "rationale": str,
                        "approved_by": str,
                        "approved_at": str,
                        "related_events": list,
                        "status": str
                    }
                ],
                "gap": str or None,
                "search_mode": "contextual" | "latest"
            }
        """
        result = {
            "status": "empty",
            "intent": current_intent,
            "matches": [],
            "gap": None,
            "search_mode": "latest",
        }

        try:
            # Read Decision Ledger (JSONL format: 1 decision per line)
            if not self._decision_ledger_path.exists():
                result["gap"] = "DECISION_LEDGER_NOT_FOUND"
                return result

            decisions = []
            with open(self._decision_ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            decisions.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

            if not decisions:
                result["gap"] = "DECISION_LEDGER_EMPTY"
                return result

            # Filter for Active decisions, sorted by decision_id (reverse = most recent first)
            active_decisions = [d for d in decisions if d.get("status") == "Active"]
            if not active_decisions:
                result["gap"] = "NO_ACTIVE_DECISIONS"
                return result

            active_decisions.sort(key=lambda x: x.get("decision_id", ""), reverse=True)

            # Phase 3: Contextual matching if intent provided
            if current_intent and current_intent.strip():
                result["search_mode"] = "contextual"
                contextual_matches = self._search_contextual_decisions(active_decisions, current_intent)

                if contextual_matches:
                    # Found matching decisions
                    matched_decision = contextual_matches[0]  # Return most recent match
                    result["status"] = "found"
                    result["matches"] = [
                        {
                            "source": "decision_ledger",
                            "decision_id": matched_decision.get("decision_id"),
                            "title": matched_decision.get("title"),
                            "decision": matched_decision.get("decision"),
                            "rationale": matched_decision.get("rationale"),
                            "approved_by": matched_decision.get("approved_by"),
                            "approved_at": matched_decision.get("approved_at"),
                            "related_events": matched_decision.get("related_events", []),
                            "status": matched_decision.get("status"),
                        }
                    ]
                    return result
                else:
                    # No contextual match found
                    result["gap"] = "NO_CONTEXTUAL_MATCH"
                    result["status"] = "empty"
                    return result

            # Phase 2 fallback: Return most recent decision if no intent
            latest = active_decisions[0]
            result["status"] = "found"
            result["matches"] = [
                {
                    "source": "decision_ledger",
                    "decision_id": latest.get("decision_id"),
                    "title": latest.get("title"),
                    "decision": latest.get("decision"),
                    "rationale": latest.get("rationale"),
                    "approved_by": latest.get("approved_by"),
                    "approved_at": latest.get("approved_at"),
                    "related_events": latest.get("related_events", []),
                    "status": latest.get("status"),
                }
            ]

            return result

        except Exception as e:
            result["gap"] = f"RECALL_ERROR: {str(e)[:100]}"
            return result

    def _search_contextual_decisions(self, decisions: list, intent: str) -> list:
        """
        Phase 3: Search for decisions contextually related to intent.

        Returns list of decisions matching keywords from intent, sorted by recency.
        """
        if not intent or not intent.strip():
            return []

        # Extract keywords from intent
        keywords = intent.lower().split()
        keywords = [kw.strip() for kw in keywords if kw.strip() and len(kw) > 2]

        if not keywords:
            return []

        matches = []
        for decision in decisions:
            # Concatenate searchable fields
            searchable = (
                (decision.get("title", "") or "").lower() +
                " " +
                (decision.get("context", "") or "").lower() +
                " " +
                (decision.get("decision", "") or "").lower() +
                " " +
                (decision.get("rationale", "") or "").lower()
            )

            # Require ALL keywords to match (stronger contextual matching)
            if all(kw in searchable for kw in keywords):
                matches.append(decision)

        return matches

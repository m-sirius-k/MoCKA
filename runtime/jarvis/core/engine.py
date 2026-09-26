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

        Includes authorized_scope from authorization_state for runtime validation.
        Runtime will check: actual execution scope must match authorized scope exactly.

        Returns JARVIS decision record with execution result.
        """
        try:
            # Get authorized scope for validation
            authorized_scope = self.gate.get_authorized_scope(decision_id)

            payload = {
                "authorization_id": authorization_id,
                "decision_record_id": decision_id,
                "human_identity": "JARVIS_AUTOMATED",
                "confirmed": True,
                "spec_id": f"JARVIS_{decision_id}",
                "authorized_scope": authorized_scope,  # For runtime scope validation
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
        JARVIS Experience Recall: Retrieve relevant past decisions from MoCKA.

        Searches Decision Ledger by intent/question, returning ranked matches.
        Read-only operation; does not modify state.

        Args:
            current_intent: Question or topic to search for
            context: Optional additional context (reserved for future use)

        Returns:
            {
                "status": "found" | "empty",
                "intent": str,
                "matches": [...],
                "gap": str or None
            }
        """
        result = {
            "status": "empty",
            "intent": current_intent,
            "matches": [],
            "gap": None,
        }

        try:
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

            active_decisions = [d for d in decisions if d.get("status") == "Active"]
            if not active_decisions:
                result["gap"] = "NO_ACTIVE_DECISIONS"
                return result

            if not current_intent or not current_intent.strip():
                result["gap"] = "NO_INTENT_PROVIDED"
                return result

            candidates = self._search_decisions(active_decisions, current_intent)

            if not candidates:
                result["gap"] = "NO_RELEVANT_EXPERIENCE"
                result["status"] = "empty"
                return result

            result["status"] = "found"
            result["matches"] = candidates[:5]

            return result

        except Exception as e:
            result["gap"] = f"RECALL_ERROR: {str(e)[:100]}"
            return result

    def _search_decisions(self, decisions: list, query: str) -> list:
        """
        Search decisions by query. Prioritizes specific entities over generic terms.
        Returns candidates sorted by relevance score (high to low), then by decision_id.
        """
        candidates = []

        for decision in decisions:
            score = self._calculate_relevance(decision, query)

            if score > 0:
                candidates.append({
                    "source": "decision_ledger",
                    "decision_id": decision.get("decision_id"),
                    "title": decision.get("title"),
                    "decision": decision.get("decision"),
                    "rationale": decision.get("rationale"),
                    "approved_by": decision.get("approved_by"),
                    "approved_at": decision.get("approved_at"),
                    "related_events": decision.get("related_events", []),
                    "status": decision.get("status"),
                    "_score": score
                })

        candidates.sort(key=lambda x: (-x["_score"], x["decision_id"]), reverse=False)
        candidates.sort(key=lambda x: -x["_score"])

        for c in candidates:
            del c["_score"]

        return candidates

    def _calculate_relevance(self, decision: dict, query: str) -> int:
        """
        Calculate relevance score for a decision based on query.
        Prioritizes specific entities (C-001, M3, Model B, JARVIS, HAB, etc.).
        """
        score = 0
        query_lower = query.lower()

        specific_entities = [
            "C-001", "C-002", "C-003", "M1", "M2", "M3", "M4",
            "Model B", "Model A",
            "JARVIS", "HAB", "HAB/JARVIS",
            "Authority Model", "Authority Model Evolution",
            "Gate Sequencing", "gate sequencing",
            "Human Gate", "HG decision",
            "multi-AI", "socket", "integration"
        ]

        generic_terms = ["implementation", "status", "runtime", "decision", "integration"]

        title_lower = decision.get("title", "").lower()
        decision_text = decision.get("decision", "").lower()
        rationale_lower = decision.get("rationale", "").lower()
        context_lower = decision.get("context", "").lower()
        alternatives_str = str(decision.get("alternatives", "")).lower()
        impact_lower = decision.get("impact", "").lower()

        for entity in specific_entities:
            entity_lower = entity.lower()
            if entity_lower in query_lower:
                if entity_lower in title_lower:
                    score += 9
                elif entity_lower in decision_text:
                    score += 6
                elif entity_lower in rationale_lower:
                    score += 4
                elif entity_lower in context_lower:
                    score += 2
                elif entity_lower in alternatives_str or entity_lower in impact_lower:
                    score += 1

        for term in generic_terms:
            term_lower = term.lower()
            if term_lower in query_lower:
                if term_lower in title_lower:
                    score += 3
                elif term_lower in decision_text:
                    score += 2
                elif term_lower in rationale_lower:
                    score += 1

        return score

# -*- coding: utf-8 -*-
"""
Minimal HAB/JARVIS Interface
Purpose: Direct human access to HAB with JARVIS decision context recall.

Simple flow:
  User Request
  → HAB (dispatch_multi_request)
  → JARVIS recall
  → Decision Context
  → 3AI responses
  → Human-visible result

No new Architecture.
No new Governance.
Reuse existing: Socket, Adapter, MultiDispatcher, JARVIS.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_dispatcher import dispatch_multi_request

# Blueprint for Flask integration
hab_bp = Blueprint('hab_jarvis', __name__, url_prefix='/api/v1/hab')


@hab_bp.route('/ask', methods=['POST'])
def ask_hab_with_jarvis():
    """
    Minimal HAB/JARVIS entry point.

    Request body:
    {
        "question": "User question text",
        "decision_id": "optional_decision_id_to_trigger_jarvis"
    }

    Response:
    {
        "status": "ok" | "error",
        "timestamp": ISO timestamp,
        "jarvis": {
            "decision_id": "recalled_decision_id",
            "decision_title": "decision_title",
            "decision_summary": "concise_decision_info"
        },
        "responses": [
            {
                "provider": "gpt|gemini|perplexity",
                "status": "ok|error|NOT_VERIFIED",
                "response": "ai_response_text",
                "error": "error_message_if_failed"
            }
        ]
    }
    """

    try:
        data = request.get_json() or {}
        user_question = data.get('question', '').strip()
        decision_id = data.get('decision_id', 'JARVIS_OBS_20260923031206')  # Default trigger

        if not user_question:
            return jsonify({
                "status": "error",
                "error": "question is required"
            }), 400

        timestamp = datetime.now(timezone.utc).isoformat()

        # Call dispatch_multi_request which integrates JARVIS internally
        dispatch_result = dispatch_multi_request(
            request_text=user_question,
            providers=["gpt", "gemini", "perplexity"],
            models={
                "gpt": "gpt-4",
                "gemini": "gemini-2.0-flash",
                "perplexity": "sonar-pro",
            },
            title="HAB User Question",
            decision_id=decision_id
        )

        # Format response for human consumption
        jarvis_info = None
        if "jarvis" in dispatch_result:
            jarvis_resp = dispatch_result["jarvis"]
            if jarvis_resp.get('status') == 'found' and jarvis_resp.get('jarvis_decision'):
                decision = jarvis_resp.get('jarvis_decision', {})
                jarvis_info = {
                    "decision_id": decision.get('decision_id'),
                    "decision_title": decision.get('title'),
                    "decision_summary": f"{decision.get('decision', '')[:200]}...",
                    "approved_by": decision.get('approved_by'),
                    "approved_at": decision.get('approved_at')
                }

        # Format AI responses for human consumption
        formatted_responses = []
        for result in dispatch_result.get('results', []):
            provider = result.get('provider')
            status = result.get('status')

            formatted = {
                "provider": provider,
                "status": status,
            }

            if status == "ok":
                formatted["response"] = result.get('response', '')[:500]  # First 500 chars
            elif status == "NOT_VERIFIED":
                formatted["error"] = f"API not verified: {result.get('error', 'Unknown')}"
            else:
                formatted["error"] = result.get('error', 'Unknown error')

            formatted_responses.append(formatted)

        return jsonify({
            "status": "ok",
            "timestamp": timestamp,
            "question": user_question,
            "jarvis": jarvis_info,
            "responses": formatted_responses,
            "summary": {
                "providers_total": dispatch_result.get('summary', {}).get('total'),
                "providers_ok": dispatch_result.get('summary', {}).get('ok'),
                "providers_unavailable": dispatch_result.get('summary', {}).get('not_verified'),
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@hab_bp.route('/health', methods=['GET'])
def hab_health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "HAB/JARVIS Interface",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


# CLI interface for direct testing
def cli_ask(question: str, decision_id: str = None):
    """
    Command-line interface for testing.
    Usage: python minimal_hab_jarvis_interface.py "question text"
    """
    print(f"\n{'='*80}")
    print(f"HAB/JARVIS User Interface - CLI Mode")
    print(f"{'='*80}")

    print(f"\n[USER QUESTION]")
    print(f"  {question}")

    if not decision_id:
        decision_id = "JARVIS_OBS_20260923031206"

    print(f"\n[JARVIS TRIGGER]")
    print(f"  Decision ID: {decision_id}")

    print(f"\n[PROCESSING]")
    print(f"  Calling HAB/JARVIS/MultiDispatcher...")

    try:
        dispatch_result = dispatch_multi_request(
            request_text=question,
            providers=["gpt", "gemini", "perplexity"],
            models={
                "gpt": "gpt-4",
                "gemini": "gemini-2.0-flash",
                "perplexity": "sonar-pro",
            },
            title="HAB User Question",
            decision_id=decision_id
        )

        # Display JARVIS result
        print(f"\n[JARVIS EXPERIENCE RECALL]")
        if "jarvis" in dispatch_result:
            jarvis_resp = dispatch_result["jarvis"]
            print(f"  Status: {jarvis_resp.get('status')}")

            if jarvis_resp.get('status') == 'found' and jarvis_resp.get('jarvis_decision'):
                decision = jarvis_resp.get('jarvis_decision', {})
                print(f"  Decision ID: {decision.get('decision_id')}")
                print(f"  Title: {decision.get('title')}")
                print(f"  Approved: {decision.get('approved_at')}")

        # Display AI responses
        print(f"\n[AI RESPONSES]")
        for result in dispatch_result.get('results', []):
            provider = result.get('provider').upper()
            status = result.get('status')

            print(f"\n  {provider}")
            print(f"    Status: {status}")

            if status == "ok":
                response_preview = result.get('response', '')[:200]
                print(f"    Response: {response_preview}...")
            elif status == "NOT_VERIFIED":
                print(f"    Error: {result.get('error')}")
            else:
                print(f"    Error: {result.get('error')}")

        # Display summary
        print(f"\n[SUMMARY]")
        summary = dispatch_result.get('summary', {})
        print(f"  Total providers: {summary.get('total')}")
        print(f"  OK: {summary.get('ok')}")
        print(f"  Unavailable: {summary.get('not_verified')}")

        print(f"\n{'='*80}\n")

    except Exception as e:
        print(f"\n[ERROR]")
        print(f"  {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        cli_ask(question)
    else:
        print("Usage: python minimal_hab_jarvis_interface.py 'your question'")
        print("Example: python minimal_hab_jarvis_interface.py 'What about C-001/C-002 gates?'")

"""
vasAI API: Evidence Ledger エンドポイント
「なぜその判断をしたか」を追跡する
"""
from flask import Blueprint, jsonify, request

bp = Blueprint("evidence", __name__)


def _get_ledger():
    from core.evidence_ledger import EvidenceLedger
    return EvidenceLedger()


@bp.post("/evidence")
def add_evidence():
    data = request.get_json(force=True) or {}
    required = ["event_id", "decision_id", "evidence_type", "content", "source"]
    for f in required:
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400

    ledger = _get_ledger()
    try:
        ev_id = ledger.add_evidence(
            event_id=data["event_id"],
            decision_id=data["decision_id"],
            evidence_type=data["evidence_type"],
            content=data["content"],
            source=data["source"],
            confidence=float(data.get("confidence", 1.0)),
        )
        return jsonify({"evidence_id": ev_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.get("/evidence/<decision_id>")
def get_evidence(decision_id):
    ledger = _get_ledger()
    return jsonify(ledger.list_by_decision(decision_id))


@bp.get("/evidence/chain/<decision_id>")
def get_chain(decision_id):
    ledger = _get_ledger()
    return jsonify(ledger.get_decision_chain(decision_id))


@bp.get("/evidence/why/<event_id>")
def why_decided(event_id):
    ledger = _get_ledger()
    explanation = ledger.why_was_this_decided(event_id)
    return jsonify({"event_id": event_id, "explanation": explanation})


@bp.get("/evidence/verify")
def verify_evidence():
    ledger = _get_ledger()
    ok = ledger.verify_chain()
    return jsonify({"chain_valid": ok})

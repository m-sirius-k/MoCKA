"""
vasAI API: PHI Layer エンドポイント
「判断の遺伝子」を記録・追跡・MoCKAへ還流する
"""
from flask import Blueprint, jsonify, request

bp = Blueprint("phi", __name__)


def _phi():
    from core.phi_layer import PHILayer
    return PHILayer()


def _bridge():
    from core.mocka_bridge import MoCKABridge
    return MoCKABridge()


@bp.post("/phi/dna")
def add_dna():
    data = request.get_json(force=True) or {}
    required = ["decision_id", "why", "reason", "decision_summary"]
    for f in required:
        if f not in data:
            return jsonify({"error": f"Missing: {f}"}), 400
    phi = _phi()
    dna_id = phi.record_dna(
        decision_id=data["decision_id"],
        why=data["why"],
        reason=data["reason"],
        evidence_ids=data.get("evidence_ids", []),
        decision_summary=data["decision_summary"],
    )
    return jsonify({"dna_id": dna_id}), 201


@bp.route("/phi/dna/<dna_id>/outcome", methods=["PATCH", "POST"])
def add_outcome(dna_id):
    data = request.get_json(force=True) or {}
    outcome = data.get("outcome", "")
    if not outcome:
        return jsonify({"error": "outcome required"}), 400
    phi = _phi()
    phi.record_outcome(dna_id, outcome)
    return jsonify({"dna_id": dna_id, "outcome_recorded": True})


@bp.get("/phi/dna/<decision_id>")
def get_dna(decision_id):
    phi = _phi()
    return jsonify(phi.get_full_dna(decision_id))


@bp.get("/phi/explain/<decision_id>")
def explain(decision_id):
    phi = _phi()
    explanation = phi.explain_decision(decision_id)
    return jsonify({"decision_id": decision_id, "explanation": explanation})


@bp.post("/phi/export/essence")
def export_essence():
    data = request.get_json(force=True) or {}
    dna_id = data.get("dna_id", "")
    if not dna_id:
        return jsonify({"error": "dna_id required"}), 400
    bridge = _bridge()
    result = bridge.full_export(dna_id)
    return jsonify(result)


@bp.get("/phi/verify")
def verify():
    phi = _phi()
    ok = phi.verify_chain()
    stats = phi.get_stats()
    return jsonify({"chain_valid": ok, **stats})


@bp.get("/phi/sync")
def sync_status():
    bridge = _bridge()
    return jsonify(bridge.verify_sync())

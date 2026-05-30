from flask import Blueprint, jsonify, request

from core import governance

bp = Blueprint("governance", __name__)


@bp.get("/governance/queue")
def queue():
    pending = governance.get_pending()
    return jsonify({
        "pending": [d.model_dump(mode="json") for d in pending],
        "count":   len(pending),
    })


@bp.post("/governance/approve/<decision_id>")
def approve(decision_id):
    data = request.get_json(force=True) or {}
    try:
        d = governance.approve(
            decision_id,
            reason=data.get("reason", ""),
            approver=data.get("approver", "HUMAN"),
        )
        return jsonify(d.model_dump(mode="json"))
    except KeyError:
        return jsonify({"error": "Decision not found"}), 404


@bp.post("/governance/reject/<decision_id>")
def reject(decision_id):
    data = request.get_json(force=True) or {}
    try:
        d = governance.reject(
            decision_id,
            reason=data.get("reason", ""),
            approver=data.get("approver", "HUMAN"),
        )
        return jsonify(d.model_dump(mode="json"))
    except KeyError:
        return jsonify({"error": "Decision not found"}), 404


@bp.get("/governance/decisions")
def decisions():
    from core import event_store
    events = event_store.list_events(limit=50, what_type="")
    decision_events = [
        e for e in events
        if e["what_type"].startswith("DECISION_")
    ]
    return jsonify({"decisions": decision_events, "count": len(decision_events)})

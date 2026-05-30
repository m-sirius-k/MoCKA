from flask import Blueprint, jsonify, request

from core import event_store

bp = Blueprint("events", __name__)


@bp.post("/events")
def create_event():
    data = request.get_json(force=True) or {}
    event_id = event_store.append(
        who_actor=data.get("who", "API"),
        what_type=data.get("what", "API_EVENT"),
        where_component=data.get("where", ""),
        why_purpose=data.get("why", ""),
        how_trigger=data.get("how", "REST"),
        content=data.get("content", {}),
        caliber_id=data.get("caliber_id", ""),
        stage=data.get("stage", ""),
    )
    return jsonify({"event_id": event_id}), 201


@bp.get("/events/<event_id>")
def get_event(event_id):
    ev = event_store.get(event_id)
    if ev is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(ev)


@bp.get("/events")
def list_events():
    limit = int(request.args.get("limit", 50))
    what_type = request.args.get("type", "")
    caliber_id = request.args.get("caliber_id", "")
    events = event_store.list_events(limit=limit, what_type=what_type,
                                     caliber_id=caliber_id)
    return jsonify({"events": events, "count": len(events)})

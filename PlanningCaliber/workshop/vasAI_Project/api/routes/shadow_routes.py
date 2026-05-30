from flask import Blueprint, jsonify, request

bp = Blueprint("shadow", __name__)


@bp.get("/shadow/status")
def shadow_status():
    from api.state import get_shadow
    shadow = get_shadow()
    if shadow is None:
        return jsonify({"error": "shadow not initialized"}), 503
    status = shadow.get_status()
    stats = shadow.get_stats()
    return jsonify({**status.model_dump(mode="json"), **stats})


@bp.post("/shadow/enter-degraded")
def enter_degraded():
    from api.state import get_shadow
    shadow = get_shadow()
    if shadow is None:
        return jsonify({"error": "shadow not initialized"}), 503
    data = request.get_json(force=True) or {}
    status = shadow.enter_degraded_mode(data.get("reason", "manual test"))
    return jsonify(status.model_dump(mode="json"))


@bp.post("/shadow/exit-degraded")
def exit_degraded():
    from api.state import get_shadow
    shadow = get_shadow()
    if shadow is None:
        return jsonify({"error": "shadow not initialized"}), 503
    shadow.exit_degraded_mode()
    synced = shadow.sync_on_recovery()
    status = shadow.get_status()
    return jsonify({**status.model_dump(mode="json"), "synced_events": synced})

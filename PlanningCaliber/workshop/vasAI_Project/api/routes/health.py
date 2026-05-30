from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    from movement.mocka_movement import MoCKAMovement
    from movement.shadow_movement import ShadowMovement
    from api.state import get_movement, get_shadow

    movement_ok = get_movement() is not None
    shadow_ok = get_shadow() is not None and get_shadow().is_alive()

    return jsonify({
        "status":   "ok",
        "movement": "alive" if movement_ok else "unavailable",
        "shadow":   "alive" if shadow_ok else "unavailable",
        "version":  "1.0.0",
    })


@bp.get("/status")
def status():
    from api.state import get_movement, get_shadow
    from core import event_store

    shadow = get_shadow()
    shadow_status = shadow.get_status().model_dump() if shadow else {}
    stage_counts = event_store.get_stage_counts()

    return jsonify({
        "movement": "alive",
        "shadow":   shadow_status,
        "stage_counts": stage_counts,
    })

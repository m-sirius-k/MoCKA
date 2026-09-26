"""
JARVIS API - Decision Evaluation Endpoints
==========================================
Exposes JARVIS Engine decision evaluation via Flask blueprint.

Path: runtime/jarvis/api.py
Related: runtime/jarvis/core/engine.py
Integration: Registered in app.py as jarvis_bp
"""
from flask import Blueprint, request, jsonify
from runtime.jarvis.core.engine import JarvisEngine

jarvis_bp = Blueprint('jarvis', __name__, url_prefix='/api/jarvis')

# Global JARVIS instance (singleton for session)
_jarvis_instance = None

def _get_jarvis_engine():
    global _jarvis_instance
    if _jarvis_instance is None:
        _jarvis_instance = JarvisEngine()
    return _jarvis_instance


@jarvis_bp.route('/evaluate', methods=['POST'])
def evaluate_decision():
    """
    Evaluate a decision through JARVIS authority boundary.

    Request: {"decision_id": "..."}
    Response: {"decision_id": "...", "status": "...", "authority": "human"}
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    decision_id = data.get('decision_id')
    if not decision_id:
        return jsonify({"error": "decision_id is required"}), 400

    try:
        jarvis = _get_jarvis_engine()
        result = jarvis.evaluate(decision_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jarvis_bp.route('/health', methods=['GET'])
def health():
    """Health check - JARVIS engine status"""
    try:
        jarvis = _get_jarvis_engine()
        return jsonify({
            "status": "ready",
            "service": "JARVIS Authority Boundary",
            "version": "v0.1",
            "engine_status": getattr(jarvis, 'status', 'unknown')
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

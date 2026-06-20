# phi_os/integrity_routes.py
# Phase5-2: Event Integrity Framework -- Verification API
# event_gate.gate_bpと同じBlueprintパターンで実装する。

from flask import Blueprint, jsonify
import json
import sqlite3
from pathlib import Path

from . import integrity

integrity_bp = Blueprint('event_integrity', __name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')
BASELINE_PATH = _REPO_ROOT / 'data' / 'integrity_baseline.json'


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@integrity_bp.route('/api/integrity/verify', methods=['GET'])
def api_verify():
    conn = _get_conn()
    try:
        result = integrity.verify_chain(conn)
        return jsonify(result), 200
    finally:
        conn.close()


@integrity_bp.route('/api/integrity/diagnose', methods=['GET'])
def api_diagnose():
    conn = _get_conn()
    try:
        result = integrity.verify_chain(conn)
        report = integrity.diagnose(result["anomalies"])
        return jsonify({
            "ok": result["ok"],
            "checked": result["checked"],
            "anomalies": result["anomalies"],
            "diagnosis": report,
        }), 200
    finally:
        conn.close()


@integrity_bp.route('/api/integrity/baseline', methods=['GET'])
def api_baseline():
    if not BASELINE_PATH.exists():
        return jsonify({
            "status": "not_sealed",
            "detail": "data/integrity_baseline.json not found. "
                      "Run scripts/seal_baseline.py to create it.",
        }), 404
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        baseline = json.load(f)
    return jsonify(baseline), 200

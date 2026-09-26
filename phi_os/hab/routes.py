# phi_os/hab/routes.py
# Phase 8-5/6: JARVIS → HAB → Execution HTTP endpoints (Blueprint)

from flask import Blueprint, jsonify, request
import json
from pathlib import Path
from .dispatch_handler import HABDispatcher
from runtime.jarvis.core.engine import JarvisEngine

hab_bp = Blueprint('hab_api', __name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
dispatcher = HABDispatcher()
jarvis = JarvisEngine()


@hab_bp.route('/api/jarvis/task/intake', methods=['POST'])
def jarvis_task_intake():
    """
    Receive task from Human, generate task_id/correlation_id, dispatch to HAB.
    Phase 8-5 JARVIS intake endpoint.
    """
    try:
        data = request.get_json(force=True)
        task_data = data.get('task_data', {})

        result = jarvis.intake_task(task_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


@hab_bp.route('/api/jarvis/task/status/<task_id>', methods=['GET'])
def jarvis_task_status(task_id):
    """Read back task status from JARVIS intake log."""
    try:
        log_path = Path(_REPO_ROOT) / 'data' / 'jarvis_task_intake.jsonl'
        if not log_path.exists():
            return jsonify({"status": "not_found"}), 404

        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                if record.get('task_id') == task_id:
                    return jsonify(record), 200

        return jsonify({"status": "not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


@hab_bp.route('/api/hab/dispatch', methods=['POST'])
def hab_dispatch():
    """
    Receive dispatch request from JARVIS, generate hab_request_id, log, respond.
    Phase 8-5 HAB dispatch endpoint (socket boundary confirmation).
    """
    try:
        data = request.get_json(force=True)
        task_id = data.get('task_id')
        correlation_id = data.get('correlation_id')
        task_data = data.get('task_data', {})

        result = dispatcher.dispatch(task_id, correlation_id, task_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


@hab_bp.route('/api/hab/dispatch/status/<hab_request_id>', methods=['GET'])
def hab_dispatch_status(hab_request_id):
    """Read back dispatch status from HAB dispatch log."""
    try:
        log_path = Path(_REPO_ROOT) / 'data' / 'hab_dispatch.jsonl'
        if not log_path.exists():
            return jsonify({"status": "not_found"}), 404

        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                if record.get('hab_request_id') == hab_request_id:
                    return jsonify(record), 200

        return jsonify({"status": "not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


@hab_bp.route('/api/hab/execute', methods=['POST'])
def hab_execute():
    """
    Execute task via provider (Phase 8-6).
    Expects: task_id, correlation_id, hab_request_id, task_data, provider
    """
    try:
        data = request.get_json(force=True)
        task_id = data.get('task_id')
        correlation_id = data.get('correlation_id')
        hab_request_id = data.get('hab_request_id')
        task_data = data.get('task_data', {})
        provider = data.get('provider', 'local')

        result = dispatcher.execute(task_id, correlation_id, hab_request_id, task_data, provider)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


@hab_bp.route('/api/hab/execution/status/<execution_id>', methods=['GET'])
def hab_execution_status(execution_id):
    """Read back execution status from HAB execution log."""
    try:
        log_path = Path(_REPO_ROOT) / 'data' / 'hab_execution.jsonl'
        if not log_path.exists():
            return jsonify({"status": "not_found"}), 404

        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                if record.get('execution_id') == execution_id:
                    return jsonify(record), 200

        return jsonify({"status": "not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500

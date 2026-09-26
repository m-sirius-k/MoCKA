# phi_os/hab/routes.py
# Phase 8-5/6: JARVIS → HAB → Execution HTTP endpoints (Blueprint)

from flask import Blueprint, jsonify, request
import json
import requests
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

        # Phase 8-5: Connect to Decision → Event → Memory
        decision_id = event_id = seal_hash = None
        if result.get("status") == "ok" and result.get("task_id"):
            task_id = result["task_id"]
            correlation_id = result.get("correlation_id")
            # Decision
            dec = _call_mcp("mocka_decision_write", {
                "title": f"Task intake {task_id}",
                "context": f"Task received: {task_data.get('description', 'no description')}",
                "decision": "Accept task for processing",
                "rationale": f"Task {task_id} accepted by JARVIS intake",
                "impact": f"Task {task_id} proceeding to HAB dispatch",
                "approved_by": "Phase-8-JARVIS",
                "correlation_id": correlation_id,
                "alternatives": [{"option": "N/A", "rejected_reason": "Task acceptance mandatory"}],
                "related_events": []
            })
            decision_id = dec.get("decision_id")
            event_id = dec.get("event_id")
            # Memory seal
            seal = _call_mcp("mocka_seal", {})
            seal_hash = seal.get("sha256")

        result.update({"decision_id": decision_id, "event_id": event_id, "memory_seal": seal_hash})
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
    Phase 8-6 HAB dispatch endpoint (socket boundary confirmation).
    """
    try:
        data = request.get_json(force=True)
        task_id = data.get('task_id')
        correlation_id = data.get('correlation_id')
        task_data = data.get('task_data', {})

        result = dispatcher.dispatch(task_id, correlation_id, task_data)

        # Phase 8-6: Connect to Decision → Event → Memory
        decision_id = event_id = seal_hash = None
        if result.get("status") == "ok" and result.get("hab_request_id"):
            hab_request_id = result["hab_request_id"]
            # Decision
            dec = _call_mcp("mocka_decision_write", {
                "title": f"Task dispatch {hab_request_id}",
                "context": f"Task {task_id} dispatched to HAB",
                "decision": "Route task to HAB executor",
                "rationale": f"Task {task_id} ready for execution at {hab_request_id}",
                "impact": f"Task {task_id} proceeding to HAB execution phase",
                "approved_by": "Phase-8-HAB-Dispatcher",
                "correlation_id": correlation_id,
                "alternatives": [{"option": "N/A", "rejected_reason": "Dispatch required for execution"}],
                "related_events": []
            })
            decision_id = dec.get("decision_id")
            event_id = dec.get("event_id")
            # Memory seal
            seal = _call_mcp("mocka_seal", {})
            seal_hash = seal.get("sha256")
            # Persist seal (Phase 8-6)
            if seal_hash:
                seal_record = {
                    "type": "seal",
                    "phase": "8-6",
                    "hab_request_id": hab_request_id,
                    "task_id": task_id,
                    "correlation_id": correlation_id,
                    "memory_seal": seal_hash,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                log_path = Path(_REPO_ROOT) / 'data' / 'hab_dispatch.jsonl'
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(seal_record, ensure_ascii=False) + '\n')

        result.update({"decision_id": decision_id, "event_id": event_id, "memory_seal": seal_hash})
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


def _call_mcp(tool_name, arguments):
    """Call MCP tool on localhost:5002"""
    try:
        resp = requests.post("http://localhost:5002/mcp", json={
            "method": "tools/call", "id": f"{tool_name}_{hash(str(arguments)) & 0x7fff}",
            "params": {"name": tool_name, "arguments": arguments}
        }, timeout=5)
        result_text = json.loads(resp.json()["result"]["content"][0]["text"])
        if "error" in result_text:
            print(f"[MCP_ERROR] {tool_name}: {result_text.get('error')} - {result_text.get('reason', '')}", flush=True)
        return result_text
    except Exception as e:
        print(f"[MCP_EXCEPTION] {tool_name}: {str(e)}", flush=True)
        return {"error": str(e), "status": "mcp_call_failed"}

@hab_bp.route('/api/hab/execute', methods=['POST'])
def hab_execute():
    """
    Execute task via provider (Phase 8-6 → Phase 8-7).
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

        # Phase 8-7: Connect to Decision → Event → Memory
        decision_id = event_id = seal_hash = None
        if result.get("status") == "ok" and result.get("execution_id"):
            exec_id = result["execution_id"]
            # Decision
            dec = _call_mcp("mocka_decision_write", {
                "title": f"Execution {exec_id} completed",
                "context": f"Task {task_id}: HAB execution via {provider}",
                "decision": "Accept execution result",
                "rationale": f"Provider returned {result.get('provider_status')}",
                "impact": f"Task {task_id} decision boundary reached",
                "approved_by": "Phase-8-Executor",
                "correlation_id": correlation_id,
                "alternatives": [{"option": "N/A", "rejected_reason": "Execution successful"}],
                "related_events": []
            })
            decision_id = dec.get("decision_id")
            event_id = dec.get("event_id")
            # Event (if not generated by decision)
            if not event_id:
                evt = _call_mcp("mocka_write_event", {
                    "title": f"Execution {exec_id} → Decision boundary",
                    "description": f"Task {task_id} execution completed with {result.get('provider_status')}",
                    "author": "Phase-8-Executor"
                })
                event_id = evt.get("event_id")
            # Memory seal
            seal = _call_mcp("mocka_seal", {})
            seal_hash = seal.get("sha256")
            # Persist seal (Phase 8-7)
            if seal_hash:
                seal_record = {
                    "type": "seal",
                    "phase": "8-7",
                    "execution_id": exec_id,
                    "task_id": task_id,
                    "correlation_id": correlation_id,
                    "hab_request_id": hab_request_id,
                    "memory_seal": seal_hash,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                log_path = Path(_REPO_ROOT) / 'data' / 'hab_execution.jsonl'
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(seal_record, ensure_ascii=False) + '\n')

        result.update({"decision_id": decision_id, "event_id": event_id, "memory_seal": seal_hash})
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

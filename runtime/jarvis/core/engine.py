import requests
import secrets
import json
from datetime import datetime, timezone
from runtime.jarvis.gate.human_gate import HumanGate


class JarvisEngine:
    def __init__(self, hab_endpoint="http://localhost:5000/api/hab/dispatch"):
        self.gate = HumanGate()
        self.hab_endpoint = hab_endpoint
        self.task_log_path = "data/jarvis_task_intake.jsonl"

    def _next_task_id(self):
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        rand = secrets.token_hex(4)
        return f"TASK_{today}_{rand}"

    def _next_correlation_id(self):
        rand = secrets.token_hex(8)
        return f"CORR_{rand}"

    def intake_task(self, task_data):
        """Receive task from Human, generate IDs, log, and dispatch to HAB."""
        if not isinstance(task_data, dict):
            return {"status": "error", "reason": "task_data must be dict"}

        task_id = self._next_task_id()
        correlation_id = self._next_correlation_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        intake_record = {
            "task_id": task_id,
            "correlation_id": correlation_id,
            "timestamp": timestamp,
            "task_data": task_data,
            "status": "INTAKE",
        }

        try:
            with open(self.task_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(intake_record, ensure_ascii=False) + "\n")
        except Exception as e:
            return {"status": "error", "reason": f"Failed to log intake: {e}"}

        dispatch_response = self._dispatch_to_hab(task_id, correlation_id, task_data)

        return {
            "status": "ok",
            "task_id": task_id,
            "correlation_id": correlation_id,
            "timestamp": timestamp,
            "dispatch_status": dispatch_response.get("status"),
            "hab_request_id": dispatch_response.get("hab_request_id"),
        }

    def _dispatch_to_hab(self, task_id, correlation_id, task_data):
        """Send task to HAB endpoint."""
        payload = {
            "task_id": task_id,
            "correlation_id": correlation_id,
            "task_data": task_data,
        }

        try:
            response = requests.post(self.hab_endpoint, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "hab_error",
                    "http_code": response.status_code,
                    "reason": response.text[:200],
                }
        except Exception as e:
            return {"status": "dispatch_failed", "reason": str(e)}

    def evaluate(self, decision_id):
        return self.gate.request(decision_id)

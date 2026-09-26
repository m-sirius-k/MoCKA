"""
HAB Dispatch Handler (Boundary Executor)
Phase 8-5: Minimal JARVIS → HAB integration
"""

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path


class HABDispatcher:
    def __init__(self, log_path="data/hab_dispatch.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _next_hab_request_id(self):
        rand = secrets.token_hex(4)
        return f"HAB_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{rand}"

    def dispatch(self, task_id, correlation_id, task_data):
        """
        Receive task from JARVIS.
        Generate HAB request_id, log dispatch, and respond.
        No execution yet - just socket boundary confirmation.
        """
        if not task_id or not correlation_id:
            return {"status": "error", "reason": "task_id and correlation_id required"}

        hab_request_id = self._next_hab_request_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        dispatch_record = {
            "hab_request_id": hab_request_id,
            "task_id": task_id,
            "correlation_id": correlation_id,
            "timestamp": timestamp,
            "task_data": task_data,
            "status": "RECEIVED",
        }

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(dispatch_record, ensure_ascii=False) + "\n")
        except Exception as e:
            return {"status": "error", "reason": f"Failed to log dispatch: {e}"}

        return {
            "status": "ok",
            "hab_request_id": hab_request_id,
            "task_id": task_id,
            "correlation_id": correlation_id,
            "timestamp": timestamp,
        }

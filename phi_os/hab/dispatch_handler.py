"""
HAB Dispatch Handler (Boundary Executor)
Phase 8-5/6: JARVIS → HAB → Provider Execution
"""

import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path


class HABDispatcher:
    def __init__(self, log_path="data/hab_dispatch.jsonl", execution_log_path="data/hab_execution.jsonl"):
        self.log_path = Path(log_path)
        self.execution_log_path = Path(execution_log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.execution_log_path.parent.mkdir(parents=True, exist_ok=True)

    def _next_hab_request_id(self):
        rand = secrets.token_hex(4)
        return f"HAB_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{rand}"

    def _next_execution_id(self):
        rand = secrets.token_hex(4)
        return f"EXEC_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{rand}"

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

    def execute(self, task_id, correlation_id, hab_request_id, task_data, provider="local"):
        """
        Execute task using specified provider.
        Generate execution_id and persist result.
        """
        if not all([task_id, correlation_id, hab_request_id]):
            return {"status": "error", "reason": "task_id, correlation_id, hab_request_id required"}

        execution_id = self._next_execution_id()
        exec_timestamp_start = datetime.now(timezone.utc).isoformat()

        try:
            # Import and initialize provider
            if provider == "local":
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from interface.providers.local_provider import LocalProvider
                prov = LocalProvider()
            else:
                return {"status": "error", "reason": f"Unsupported provider: {provider}"}

            # Check availability
            if not prov.is_available():
                return {"status": "error", "reason": f"Provider '{provider}' not available"}

            # Execute
            result = prov.generate({"prompt": task_data.get("description", "")})

            exec_timestamp_end = datetime.now(timezone.utc).isoformat()

            # Log execution result
            execution_record = {
                "execution_id": execution_id,
                "task_id": task_id,
                "correlation_id": correlation_id,
                "hab_request_id": hab_request_id,
                "provider": provider,
                "start_timestamp": exec_timestamp_start,
                "end_timestamp": exec_timestamp_end,
                "status": "SUCCESS" if result.get("status") == "success" else "FAILED",
                "provider_response": result,
            }

            with open(self.execution_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(execution_record, ensure_ascii=False) + "\n")

            return {
                "status": "ok",
                "execution_id": execution_id,
                "task_id": task_id,
                "correlation_id": correlation_id,
                "hab_request_id": hab_request_id,
                "provider": provider,
                "provider_status": result.get("status"),
                "timestamp": exec_timestamp_end,
            }

        except Exception as e:
            return {"status": "error", "reason": f"Execution failed: {e}"}

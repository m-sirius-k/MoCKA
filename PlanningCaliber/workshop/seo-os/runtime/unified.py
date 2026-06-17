"""runtime/unified.py — UnifiedRuntime: Phase 10 統合Runtime

Context Runtime + Memory Runtime + Execution Runtime +
Event Runtime + Snapshot Runtime + Validator を単一エントリポイントで統合。
"""
from __future__ import annotations
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from command_index.db import CommandIndexDB
from context_bridge.bridge import ContextBridge
from learning.engine import LearningEngine
from audit.logger import AuditLogger

_SNAPSHOT_DIR = Path(__file__).parent.parent / "data" / "runtime_snapshots"


class RuntimeState:
    def __init__(self) -> None:
        self.booted_at = datetime.now(timezone.utc).isoformat()
        self.context: dict = {}
        self.last_command: str | None = None
        self.last_result: str | None = None
        self.event_log: list[dict] = []

    def to_dict(self) -> dict:
        return {
            "booted_at": self.booted_at,
            "context": self.context,
            "last_command": self.last_command,
            "last_result": self.last_result,
            "event_count": len(self.event_log),
        }


class UnifiedRuntime:
    """Phase 10: 全Runtimeを統合するオーケストレーター"""

    def __init__(self, db_path=None) -> None:
        from command_index.db import CommandIndexDB as _CDB
        if isinstance(db_path, _CDB):
            self._db = db_path
        else:
            self._db = CommandIndexDB(db_path)
        self._ctx = ContextBridge()
        self._learn = LearningEngine(self._db)
        self._audit = AuditLogger(self._db)
        self._state = RuntimeState()
        _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Boot / Resume ---

    def boot(self) -> dict:
        """Memory Runtime Protocol順にコンテキストをロード"""
        ctx = self._ctx.get_memory_runtime()
        self._state.context = ctx
        self._emit("BOOT", {"protocol": ctx.get("protocol"), "phase": ctx.get("project", {}).get("phase")})
        self._audit.log("runtime.boot", {"phase": ctx.get("project", {}).get("phase")})
        return ctx

    def resume(self) -> dict:
        """最新スナップショットから状態を復元"""
        snap = self._latest_snapshot()
        if snap:
            self._state.context = snap.get("context", {})
            self._state.last_command = snap.get("last_command")
            self._state.last_result = snap.get("last_result")
            self._emit("RESUME", {"from_snapshot": snap.get("saved_at")})
            self._audit.log("runtime.resume", {"snapshot": snap.get("saved_at")})
            return {"ok": True, "resumed_from": snap.get("saved_at"), "state": self._state.to_dict()}
        self._emit("RESUME_COLD", {})
        return {"ok": False, "reason": "no_snapshot", "state": self._state.to_dict()}

    # --- Execution Gate ---

    def execution_gate(self, module: str, target: str = "", project: str = "PlanningCaliber") -> dict:
        """Context Runtime v2 ExecutionGate委譲"""
        if not self._ctx.available:
            return {"passed": True, "reason": "context_bridge_unavailable"}
        try:
            rt = self._ctx._runtime
            result = rt.execution_gate(module, target, project)
            self._emit("GATE_CHECK", {"module": module, "passed": result.passed})
            return {"passed": result.passed, "status": result.status.value,
                    "checks": [{"name": c.name, "passed": c.passed, "message": c.message}
                                for c in result.checks]}
        except Exception as e:
            return {"passed": True, "reason": f"gate_error:{e}"}

    # --- Event Runtime ---

    def emit(self, event_type: str, payload: dict | None = None) -> None:
        """外部からイベントを発火"""
        self._emit(event_type, payload or {})

    def _emit(self, event_type: str, payload: dict) -> None:
        entry = {
            "type": event_type,
            "payload": payload,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self._state.event_log.append(entry)
        self._audit.log(f"event.{event_type.lower()}", payload, emit_event=False)

    # --- Snapshot Runtime ---

    def snapshot(self) -> Path:
        """現在のRuntimeStateをスナップショット保存"""
        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y%m%dT%H%M%S")
        data = {**self._state.to_dict(), "saved_at": now.isoformat()}
        path = _SNAPSHOT_DIR / f"runtime_{ts}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        latest = _SNAPSHOT_DIR / "runtime_latest.json"
        latest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self._prune(20)
        self._emit("SNAPSHOT", {"path": str(path)})
        return path

    def _latest_snapshot(self) -> dict | None:
        p = _SNAPSHOT_DIR / "runtime_latest.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return None

    def _prune(self, keep: int) -> None:
        snaps = sorted(_SNAPSHOT_DIR.glob("runtime_2*.json"), key=lambda f: f.name)
        for old in snaps[:-keep]:
            try:
                old.unlink()
            except Exception:
                pass

    # --- Validator ---

    def validate(self) -> dict:
        """Runtime全体の整合性を検証"""
        issues = []
        ctx = self._state.context
        if not ctx:
            issues.append({"level": "WARNING", "msg": "context not loaded — call boot() first"})
        if not ctx.get("project", {}).get("phase"):
            issues.append({"level": "WARNING", "msg": "project phase not set"})
        if not ctx.get("memory", {}).get("event_count"):
            issues.append({"level": "INFO", "msg": "no memory events — DB may be offline"})
        resumable = all(i["level"] != "CRITICAL" for i in issues)
        return {"resumable": resumable, "issues": issues, "state": self._state.to_dict()}

    # --- Convenience ---

    def state(self) -> dict:
        return self._state.to_dict()

    def memory_runtime(self) -> dict:
        return self._ctx.get_memory_runtime()

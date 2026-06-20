"""
Context Runtime v2 — ContextRuntime オーケストレーター
責務: 4層を統合し、AIへ渡す完全なContextを構築・提供する。

Memory Runtime プロトコル:
  AIはコード生成・回答・実装の前に必ず
  Memory → Architecture → Project → Execution の順で参照すること。
  Memory未参照でコード生成を開始してはならない。
"""
from __future__ import annotations
import json
import requests
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .institution_context import InstitutionContext
from .working_context import WorkingContext
from .memory_context import MemoryContext
from .execution_context import ExecutionContext, GateResult
from .context_snapshot import ContextSnapshot
from .context_validator import ContextValidator

_MCP_URL = "http://localhost:5002"


class ContextRuntime:
    """
    Context Runtime v2 エントリポイント。

    使い方:
        rt = ContextRuntime.boot()
        gate = rt.execution_gate("Context Runtime", "phi_os/context/")
        if not gate.passed:
            raise RuntimeError(gate.blocked_by)
        ctx = rt.full_context()
    """

    def __init__(self) -> None:
        self.institution: InstitutionContext = InstitutionContext()
        self.working: WorkingContext = WorkingContext()
        self.memory: MemoryContext = MemoryContext()
        self.execution: ExecutionContext = ExecutionContext()
        self._snapshot = ContextSnapshot()
        self._validator = ContextValidator()
        self._booted_at: str = ""

    @classmethod
    def boot(cls) -> "ContextRuntime":
        """全4層をロードし起動する。"""
        rt = cls()
        rt._booted_at = datetime.now(timezone.utc).isoformat()
        rt.institution = InstitutionContext.load()
        rt.working = WorkingContext.load()
        rt.memory = MemoryContext.load()
        rt.execution = ExecutionContext.load()
        return rt

    # ──────────────────────────────────────────
    # Memory Runtime プロトコル
    # ──────────────────────────────────────────

    def memory_runtime(self) -> dict:
        """
        AIが実装・回答前に参照すべき正本コンテキストを返す。
        順序: Memory → Architecture → Project → Execution
        """
        return {
            "protocol": "Memory Runtime v2",
            "order": ["Memory", "Architecture", "Project", "Execution"],
            "memory": self.memory.to_dict(),
            "architecture": {
                "allowed_modules": self.institution.allowed_modules,
                "forbidden_modules": self.institution.forbidden_modules,
                "gate_rule": self.institution.architecture.get("gate_rule", ""),
            },
            "project": {
                "project": self.institution.project,
                "phase": self.institution.current_phase,
                "mission": self.institution.mission,
                "top_todos": self.institution.top_todos,
                "open_incidents": self.institution.open_incidents,
                "seal": self.institution.latest_seal,
            },
            "execution": self.execution.to_dict(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # ──────────────────────────────────────────
    # Execution Gate
    # ──────────────────────────────────────────

    def execution_gate(self, module: str, target_file: str = "",
                       project: str = "MoCKA") -> GateResult:
        return self.execution.check(
            project=project,
            module=module,
            open_incidents=self.institution.open_incidents,
            locked_files=self.working.locked_files,
            target_file=target_file,
        )

    # ──────────────────────────────────────────
    # Context Update API
    # ──────────────────────────────────────────

    def update_working(self, **kwargs) -> None:
        self.working.update(**kwargs)
        self._emit_event("CONTEXT_UPDATE", f"WorkingContext更新: {list(kwargs.keys())}")

    def set_task(self, task: str, goal: str, step: str = "",
                 next_action: str = "", ai: str = "") -> None:
        self.working.set_task(task, goal, step, next_action, ai)
        self._emit_event("CONTEXT_UPDATE",
                         f"タスク設定: {task[:60]}")

    def record_decision(self, decision: str, reason: str,
                        evidence: str = "") -> None:
        rec = self.memory.record_decision(decision, reason, evidence)
        self._emit_event("DECISION_RECORD",
                         f"判断記録: {decision[:60]}")

    def add_lesson(self, lesson: str) -> None:
        self.memory.add_lesson(lesson)

    # ──────────────────────────────────────────
    # Snapshot
    # ──────────────────────────────────────────

    def snapshot(self) -> dict:
        data = self.full_context()
        path = self._snapshot.save(data)
        self._emit_event("CONTEXT_SNAPSHOT", f"スナップショット保存: {path}")
        return data

    def full_context(self) -> dict:
        return {
            "context_runtime_version": "v2",
            "booted_at": self._booted_at,
            "institution": self.institution.to_dict(),
            "working": self.working.to_dict(),
            "memory": self.memory.to_dict(),
            "execution": self.execution.to_dict(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def validate(self) -> dict:
        return self._validator.validate(
            self.institution, self.working, self.memory, self.execution
        )

    # ──────────────────────────────────────────
    # Event Runtime
    # ──────────────────────────────────────────

    def _emit_event(self, event_type: str, description: str) -> None:
        payload = {
            "title": f"{event_type}: {description[:80]}",
            "description": description,
            "author": "ContextRuntime-v2",
            "tags": f"context_runtime,{event_type.lower()}",
        }
        try:
            requests.post(f"{_MCP_URL}/event", json=payload, timeout=1.0)
        except Exception:
            pass


# ──────────────────────────────────────────────────
# P3: Event Runtime本体接続（プロセス間連携）
# ──────────────────────────────────────────────────
# mocka_mcp_server.py（別プロセス）から mocka_write_event 完了直後に呼ばれる。
# mocka_events.db への新規イベント書き込み・next_event_id()の呼び出しは一切行わない
# （DANGER監査 E20260621_940325153cf6f 準拠）。Context Runtime側への伝播は
# event_runtime_log.json への追記のみで完結する。

_EVENT_LOG_PATH = Path(__file__).parents[2] / "data" / "context_snapshots" / "event_runtime_log.json"
_EVENT_LOG_MAX = 200


def emit_event_to_context_runtime(event_type: str, event_id: str, payload: dict | None = None) -> None:
    entry = {
        "event_type": event_type,
        "event_id": event_id,
        "payload": payload or {},
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        _EVENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        log: list = []
        if _EVENT_LOG_PATH.exists():
            log = json.loads(_EVENT_LOG_PATH.read_text(encoding="utf-8"))
        log.insert(0, entry)
        _EVENT_LOG_PATH.write_text(
            json.dumps(log[:_EVENT_LOG_MAX], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass

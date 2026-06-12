# state_provider.py
from __future__ import annotations
from typing import Protocol, runtime_checkable
from pathlib import Path
import json, sqlite3

from .schema import ProjectStatus, Warning, TodoItem

@runtime_checkable
class StateProvider(Protocol):
    """State Builder への入力抽象。データソースを隠蔽する。"""
    def get_project_status(self)    -> ProjectStatus: ...
    def get_active_warnings(self)   -> list[Warning]: ...
    def get_active_todos(self)      -> list[TodoItem]: ...
    def get_decision_revision(self) -> int: ...
    def get_guideline_revision(self)-> int: ...


class DefaultStateProvider:
    """
    現行実装。events.db（SQLite）と MOCKA_TODO.json を参照する。
    将来 BEE / TIC 追加時は別 Provider を実装し、
    CompositeProvider で合成する。build_state() の引数は変わらない。
    """

    def __init__(self, db_path: Path, todo_path: Path):
        self.db_path   = db_path
        self.todo_path = todo_path

    def _conn(self):
        return sqlite3.connect(str(self.db_path))

    def get_project_status(self) -> ProjectStatus:
        # OVERVIEW.json がなければ events.db の最新フェーズ情報を使う
        try:
            overview_path = self.db_path.parent / "MOCKA_OVERVIEW.json"
            if overview_path.exists():
                with open(overview_path, encoding="utf-8") as f:
                    ov = json.load(f)
                phase = ov.get("current_phase", "Phase 4")
                mission = phase
                return ProjectStatus(phase=4, mission=mission, priority=[])
        except Exception:
            pass
        return ProjectStatus(phase=4, mission="Unknown", priority=[])

    def get_active_warnings(self) -> list[Warning]:
        results = []
        try:
            with self._conn() as conn:
                rows = conn.execute(
                    "SELECT event_id, what, how FROM events "
                    "WHERE what_type IN ('HEALTH_FAIL','HEALTH_DEGRADED','INCIDENT') "
                    "ORDER BY when_ts DESC LIMIT 10"
                ).fetchall()
            for r in rows:
                results.append(Warning(id=r[0], level="ACTIVE", description=r[1] or r[2] or ""))
        except Exception:
            pass
        return results

    def get_active_todos(self) -> list[TodoItem]:
        results = []
        try:
            with open(self.todo_path, encoding="utf-8") as f:
                data = json.load(f)
            todos = data.get("todos", [])
            for t in todos:
                if t.get("status") in ("未着手", "進行中"):
                    results.append(TodoItem(
                        id       = t.get("id", ""),
                        title    = t.get("title", ""),
                        priority = t.get("priority", "中"),
                        status   = t.get("status", "未着手"),
                    ))
        except Exception:
            pass
        return results

    def get_decision_revision(self) -> int:
        try:
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT COUNT(*) FROM events "
                    "WHERE what_type IN ('DECISION_APPROVED','DECISION_REJECTED')"
                ).fetchone()
            return row[0] if row else 0
        except Exception:
            return 0

    def get_guideline_revision(self) -> int:
        try:
            gl_path = self.db_path.parent / "data" / "guidelines_reviewed.json"
            if gl_path.exists():
                with open(gl_path, encoding="utf-8") as f:
                    data = json.load(f)
                return len(data) if isinstance(data, list) else 0
        except Exception:
            pass
        return 0

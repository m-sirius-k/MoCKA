"""
Context Runtime v2 — Layer 2: WorkingContext
責務: 現在の作業状態。どのAIが引き継いでも同じ地点から再開できる唯一の正本。
"""
from __future__ import annotations
import json
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_SNAPSHOT_DIR = Path(__file__).parents[2] / "data" / "context_snapshots"


@dataclass
class WorkingContext:
    # --- Workspace ---
    current_workspace: str = "C:/Users/sirok/MoCKA"
    current_directory: str = ""
    current_file: str = ""
    editing_files: list = field(default_factory=list)
    locked_files: list = field(default_factory=list)
    working_branch: str = "main"

    # --- Task ---
    current_task: str = ""
    current_goal: str = ""
    current_step: str = ""
    next_action: str = ""
    blockers: list = field(default_factory=list)

    # --- AI ---
    current_ai: str = ""
    session_id: str = ""

    # --- H2-2: Actor-scoped observe(3.2) ---
    actor_id: str = ""

    # --- Verification ---
    verification_status: str = "UNVERIFIED"

    # --- Services ---
    running_services: list = field(default_factory=list)
    open_ports: list = field(default_factory=list)
    current_urls: list = field(default_factory=list)
    current_database: str = "C:/Users/sirok/MoCKA/data/events.db"

    # --- Meta ---
    updated_at: str = ""

    @classmethod
    def load(cls) -> "WorkingContext":
        ctx = cls()
        ctx.updated_at = datetime.now(timezone.utc).isoformat()
        ctx._load_from_snapshot()
        ctx._detect_services()
        return ctx

    def _load_from_snapshot(self) -> None:
        latest = _SNAPSHOT_DIR / "working_context_latest.json"
        if not latest.exists():
            return
        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            for k, v in data.items():
                if hasattr(self, k) and k not in ("updated_at",):
                    setattr(self, k, v)
        except Exception:
            pass

    def _detect_services(self) -> None:
        known = [
            (5000, "APP (Flask)"),
            (5002, "MCP Caliber"),
            (5003, "Runtime-B (Go)"),
            (5679, "Caliber Pipeline"),
            (8750, "DIST-OS"),
        ]
        active = []
        ports = []
        for port, name in known:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                    active.append(name)
                    ports.append(port)
            except OSError:
                pass
        self.running_services = active
        self.open_ports = ports

    def update(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def set_task(self, task: str, goal: str, step: str = "",
                 next_action: str = "", ai: str = "") -> None:
        self.current_task = task
        self.current_goal = goal
        self.current_step = step
        self.next_action = next_action
        if ai:
            self.current_ai = ai
        self.updated_at = datetime.now(timezone.utc).isoformat()

    @classmethod
    def live_update(cls, current_task: str = "", current_goal: str = "",
                     next_action: str = "", current_ai: str = "",
                     editing_files: list | None = None) -> None:
        """
        WorkingContext更新の唯一の書き込み口（CONTEXT_RUNTIME_CONNECTION_INSTRUCTIONS P0）。
        mocka_write_event発火時に呼ばれ、working_context_latest.json を直接更新する。
        プロセス間でインスタンスを共有できないため、スナップショットファイルへの
        直接読み書きで永続化する（既存のload()/update()ロジックは変更しない）。
        """
        latest = _SNAPSHOT_DIR / "working_context_latest.json"
        data: dict = {}
        if latest.exists():
            try:
                data = json.loads(latest.read_text(encoding="utf-8"))
            except Exception:
                data = {}

        if current_task:
            data["current_task"] = current_task
        if current_goal:
            data["current_goal"] = current_goal
        if next_action:
            data["next_action"] = next_action
        if current_ai:
            data["current_ai"] = current_ai
        if editing_files:
            data["editing_files"] = editing_files
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        latest.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def to_dict(self) -> dict:
        return {
            "layer": "Working",
            "current_workspace": self.current_workspace,
            "current_directory": self.current_directory,
            "current_file": self.current_file,
            "editing_files": self.editing_files,
            "locked_files": self.locked_files,
            "working_branch": self.working_branch,
            "current_task": self.current_task,
            "current_goal": self.current_goal,
            "current_step": self.current_step,
            "next_action": self.next_action,
            "blockers": self.blockers,
            "current_ai": self.current_ai,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "verification_status": self.verification_status,
            "running_services": self.running_services,
            "open_ports": self.open_ports,
            "current_urls": self.current_urls,
            "current_database": self.current_database,
            "updated_at": self.updated_at,
        }

    # ──────────────────────────────────────────
    # H2-2: Actor-scoped観測(3.2) — 他Actorからの直接参照を禁止する。
    # 既存のload()/live_update()(共有ファイル・互換維持)は変更しない。
    # ──────────────────────────────────────────

    @classmethod
    def _scoped_path(cls, actor_id: str) -> Path:
        return _SNAPSHOT_DIR / f"working_context_{actor_id}.json"

    @classmethod
    def load_scoped(cls, requesting_actor_id: str, target_actor_id: str) -> "WorkingContext":
        """actor-scoped観測(3.2)。自身のactor_id以外を要求した場合は拒否する。"""
        from .access_gate import enforce_observe
        from .permissions import ACTOR_SCOPED

        enforce_observe(requesting_actor_id, target_actor_id, ACTOR_SCOPED)

        ctx = cls(actor_id=target_actor_id)
        ctx.updated_at = datetime.now(timezone.utc).isoformat()
        path = cls._scoped_path(target_actor_id)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for k, v in data.items():
                    if hasattr(ctx, k) and k not in ("updated_at",):
                        setattr(ctx, k, v)
            except Exception:
                pass
        return ctx

    @classmethod
    def live_update_scoped(cls, actor_id: str, current_task: str = "",
                            current_goal: str = "", next_action: str = "",
                            editing_files: list | None = None) -> None:
        """actor-scoped書き込み(2.2 write)。自身のactor_idに紐づくファイルのみ更新する。"""
        from .access_gate import before_context_update

        before_context_update(actor_id, actor_id)

        path = cls._scoped_path(actor_id)
        data: dict = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                data = {}

        data["actor_id"] = actor_id
        if current_task:
            data["current_task"] = current_task
        if current_goal:
            data["current_goal"] = current_goal
        if next_action:
            data["next_action"] = next_action
        if editing_files:
            data["editing_files"] = editing_files
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

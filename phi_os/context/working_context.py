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
            "verification_status": self.verification_status,
            "running_services": self.running_services,
            "open_ports": self.open_ports,
            "current_urls": self.current_urls,
            "current_database": self.current_database,
            "updated_at": self.updated_at,
        }

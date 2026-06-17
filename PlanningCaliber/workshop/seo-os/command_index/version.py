"""command_index/version.py — VersionManager"""
from __future__ import annotations
from datetime import datetime, timezone
from .db import CommandIndexDB


class VersionManager:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()

    def record(self, command_id: str, version: str, changelog: str = "") -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._db.execute_write(
            "INSERT OR IGNORE INTO command_versions(command_id,version,changelog,created_at)"
            " VALUES(?,?,?,?)",
            (command_id, version, changelog, now)
        )
        self._db.execute_write(
            "UPDATE commands SET version=?, updated_at=? WHERE id=?",
            (version, now, command_id)
        )

    def history(self, command_id: str) -> list[dict]:
        return self._db.execute(
            "SELECT version, changelog, created_at FROM command_versions "
            "WHERE command_id=? ORDER BY created_at DESC",
            (command_id,)
        )

    def current(self, command_id: str) -> str | None:
        rows = self._db.execute(
            "SELECT version FROM commands WHERE id=?", (command_id,)
        )
        return rows[0]["version"] if rows else None

    def bump(self, command_id: str, level: str = "patch",
             changelog: str = "") -> str:
        current = self.current(command_id) or "1.0.0"
        parts = current.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        if level == "major":
            major += 1; minor = 0; patch = 0
        elif level == "minor":
            minor += 1; patch = 0
        else:
            patch += 1
        new_version = f"{major}.{minor}.{patch}"
        self.record(command_id, new_version, changelog)
        return new_version

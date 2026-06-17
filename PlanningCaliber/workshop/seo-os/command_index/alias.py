"""command_index/alias.py — AliasManager"""
from __future__ import annotations
from datetime import datetime, timezone
from .db import CommandIndexDB


class AliasManager:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()

    def add(self, alias: str, command_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._db.execute_write(
            "INSERT OR IGNORE INTO aliases(alias,command_id,created_at) VALUES(?,?,?)",
            (alias.lower(), command_id, now)
        )

    def remove(self, alias: str) -> None:
        self._db.execute_write("DELETE FROM aliases WHERE alias=?", (alias.lower(),))

    def resolve(self, alias: str) -> str | None:
        rows = self._db.execute(
            "SELECT command_id FROM aliases WHERE alias=?", (alias.lower(),)
        )
        return rows[0]["command_id"] if rows else None

    def list_for_command(self, command_id: str) -> list[str]:
        rows = self._db.execute(
            "SELECT alias FROM aliases WHERE command_id=? ORDER BY alias",
            (command_id,)
        )
        return [r["alias"] for r in rows]

    def list_all(self) -> dict[str, str]:
        rows = self._db.execute("SELECT alias, command_id FROM aliases ORDER BY alias")
        return {r["alias"]: r["command_id"] for r in rows}
